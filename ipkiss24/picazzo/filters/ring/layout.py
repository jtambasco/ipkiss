# IPKISS - Parametric Design Framework
# Copyright (C) 2002-2012  Ghent University - imec
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# 
# i-depot BBIE 7396, 7556, 7748
# 
# Contact: ipkiss@intec.ugent.be

from ipkiss.plugins.photonics.routing.to_line import RouteToEastAtY, RouteToEastAtMinY
from ipkiss.plugins.photonics.routing.connect import RouteConnectorManhattan
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.wg.connect import WaveguidePointRoundedConnectElementDefinition, __RoundedWaveguide__
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty, WaveguideDefListProperty
import math
from ipkiss.all import *

__all__ = ["RingShape",
           "RingRoundedShape",
           "RingRect",
           "RingRectNotchFilter",
           "RingRect180DropFilter",
           "RingRect90DropFilter",
           "RingRectBentNotchFilter",
           "RingRectBent180DropFilter",
           "RingRectSymmNotchFilter",
           "RingRectSymm180DropFilter",
           "RingRectSymm90DropFilter",
           "RingRectSBendNotchFilter",
           "RingRectSBend180DropFilter"
           ]


#######################################################################################
# New Ring classes
#######################################################################################

class __Ring__(Structure):
    area_layer_on = BoolProperty(default = True)

    couplers = DefinitionProperty(fdef_name = "define_couplers", doc = "list of coupler structures")
    coupler_transformations = DefinitionProperty(fdef_name = "define_coupler_transformations", doc = "list of coupler transformations")
    
    
    def get_ring(self):
        return []

    def define_couplers(self):
        return []
    
    def define_coupler_transformations(self):
        return []
    
    
    def define_elements(self, elems):
        elems += [SRef(reference = c, transformation = t) for (c,t) in zip(self.couplers, self.coupler_transformations)]
        elems += self.get_ring()
        
        if self.area_layer_on:
            SI = elems.size_info()
            elems += Rectangle(layer = PPLayer(self.ring_wg_definition.process, TECH.PURPOSE.LF_AREA), 
                               center = SI.center, 
                               box_size = SI.size)
        return elems

    def define_ports(self, prts):
        for (c, t) in zip(self.couplers, self.coupler_transformations):
            prts += c.ports.transform_copy(t)
        return prts
    
class RingShapes(__Ring__):
    """ Ring made of an arbitrary a set of shapes"""
    __name_prefix__ = "RINGSHAPE"
    shapes = DefinitionProperty(fdef_name = "define_shapes", doc = "Shapes of the ring")
    ring_wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    
    def define_shapes(self):
        return []
    
    @cache()
    def get_ring(self):
        return [self.ring_wg_definition(shape = s) for s in self.shapes]

class RingShape(RingShapes):
    """ Ring made of an arbitrary shape"""
    __name_prefix__ = "RINGSHAPE"
    shape = ShapeProperty(required = True, doc = "Shape of the ring")
    shape_position = Coord2Property(allow_none = True, doc = "Translation of the shape. None means auto_centering")
    ring_wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)

    def define_shapes(self):
        return [self.get_shape()]
    
    @cache()
    def get_shape(self):
        S = self.shape
        if self.shape_position is None:
            SI = S.size_info
            t =-SI.center
        else:
            t = self.shape_position
        return S.move_copy(t)

    @cache()
    def get_ring(self):
        return self.ring_wg_definition(shape = self.get_shape())
    
class RingRoundedShape(__RoundedWaveguide__, RingShape):
    """ Base Class: rounded shape ring"""
    __name_prefix__ = "RINGRSHAPE"
    
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    rounding_algorithm = RestrictedProperty(default = ShapeRound)
    

    @cache()
    def get_ring(self):
        wgdef = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.ring_wg_definition,
                                                              bend_radius = self.bend_radius,
                                                              rounding_algorithm = self.rounding_algorithm,
                                                              manhattan = self.manhattan
                                                              )
        return wgdef(shape = self.get_shape())
    

    
class RingRect(RingRoundedShape):
    """ Base Class: Rectangular ring (rounded rectangle) """
    __name_prefix__ = "RINGRECT"
    process = ProcessProperty(default = TECH.PROCESS.WG)
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    straights = Size2Property(default = (TECH.WG.SHORT_STRAIGHT, TECH.WG.SHORT_STRAIGHT))
    shape = DefinitionProperty(fdef_name = "define_shape")

    @cache()
    def define_shape(self):
        bs1, bs2 = self.get_bend90_size()
        (S1x, S1y) = Coord2(bs1 + bs2 + self.straights[0], bs1 + bs2 + self.straights[1])
        return ShapeRectangle(center = (0.0, 0.0), 
                                     box_size = (S1x, S1y))



#####################################################################################
# Ring Couplers
#####################################################################################
class __RingCoupler__(Structure):
    """ Base class for a coupling section of a ring."""
    pass

    
class RingWaveguideCoupler(__RingCoupler__):
    """ Coupler for a ring resonator based on a simple waveguide """
    # This is a base class for more sophisticated coupler. In principle you could just as well use
    # a simple waveguide instead of this class, but it is not possible to easily subclass it.
    
    shape = DefinitionProperty(fdef_name = "define_shape")
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    
    def define_shape(self):
        return Shape()
    
    @cache()
    def get_waveguide(self):
        return self.wg_definition(shape = self.shape)
    
    def define_elements(self, elems):
        elems += self.get_waveguide()
        return elems
    
    def define_ports(self, prts):
        prts += self.get_waveguide().ports
        return prts

class RingRoundedWaveguideCoupler(__RoundedWaveguide__, RingWaveguideCoupler):
    """ Coupler for a ring resonator based on a rounded waveguide """
    # This is a base class for more sophisticated coupler. In principle you could just as well use
    # a simple waveguide instead of this class, but it is not possible to easily subclass it.
    
    
    @cache()
    def get_waveguide(self):
        wgdef = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition,
                                                              bend_radius = self.bend_radius,
                                                              rounding_algorithm = self.rounding_algorithm,
                                                              manhattan = self.manhattan
                                                              )
        return wgdef(shape = self.shape)
            
        
class RingStraightWaveguideCoupler(RingWaveguideCoupler):
    """ straight coupling section """
    length = PositiveNumberProperty(required = True)
    
    def define_shape(self):
        return Shape([(-0.5*self.length, 0.0), (0.5*self.length, 0.0)])
    
class RingSymmWaveguideCoupler(RingRoundedWaveguideCoupler):
    """ coupler that bends away from the ring """    
    length = NonNegativeNumberProperty(required = True)
    coupler_angles = RestrictedProperty(default = (90.0, 90.0), restriction = RESTRICT_TUPLE2, doc = "Coupler angles of the symmetric coupler section")
    
    def define_shape(self):
        bs1a, bs2a = self.get_bend_size(self.coupler_angles[0])
        bs1b, bs2b = self.get_bend_size(self.coupler_angles[1])
        s1 = Shape([(-0.5*self.length-bs2a, 0.0)])
        s1.add_polar(bs1a, 180.0 + self.coupler_angles[0])
        
        s2 = Shape([(0.5*self.length+bs1b, 0.0)])
        s2.add_polar(bs2b, - self.coupler_angles[1])
        s1.reverse()
        
        cs = s1 + s2
        return cs
    
class RingSBendWaveguideCoupler(RingSymmWaveguideCoupler):
    """ coupler that couples with an SBend along or away from the ring """    
    sbend_straight = NonNegativeNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    
    def define_shape(self):
        bs1a, bs2a = self.get_bend_size(self.coupler_angles[0])
        bs1b, bs2b = self.get_bend_size(self.coupler_angles[1])
        
        s1 = Shape([(-0.5*self.length-bs2a, 0.0)])
        s1.add_polar(bs1a + bs2a + self.sbend_straight, 180.0 + self.coupler_angles[0])
        s1.add_polar(bs1a, 180.0)
        
        s2 = Shape([(0.5*self.length+bs1b, 0.0)])
        s2.add_polar(bs1b + bs2b + self.sbend_straight, - self.coupler_angles[1])
        s2.add_polar(bs2b, 0.0)
        s1.reverse()
        
        cs = s1 + s2
        
        return cs



################################################################################
# Defining the couplers in the class
################################################################################

class __RingWaveguideCouplers__(StrongPropertyInitializer):
    """abstract partial base class for rings which have waveguide directional couplers """
    coupler_wg_definitions = WaveguideDefListProperty(required = True, doc = "list of waveguide definitions for the ring couplers")

class __RingWaveguideCouplers1__(__RingWaveguideCouplers__):
    """abstract partial base class for rings which have a single waveguide directional coupler """
    coupler_wg_definitions = WaveguideDefListProperty(default = [TECH.WGDEF.WIRE], doc = "list of waveguide definitions for the ring couplers")
    
class __RingWaveguideCouplers2__(__RingWaveguideCouplers__):
    """abstract partial base class for rings which have 2 waveguide directional couplers """
    coupler_wg_definitions = WaveguideDefListProperty(default = [TECH.WGDEF.WIRE, TECH.WGDEF.WIRE], doc = "list of waveguide definitions for the ring couplers")
    
class __RingStraightCouplers__(__RingWaveguideCouplers__):
    coupler_lengths = RestrictedProperty(allow_none = True, restriction = RestrictList(RESTRICT_NONNEGATIVE), doc = "straight lengths of the couplers. if None, same lengths as the ring will be used")

    def define_coupler_lengths(self):
        L = self.get_ring().size_info().width
        return [L for i in self.coupler_wg_definitions]

    def define_couplers(self):
        couplers = []
        i = 1
        for wgdef in self.coupler_wg_definitions:
            couplers += [RingStraightWaveguideCoupler(name = self.name + "_coupler_%d" % i,
                                               wg_definition = wgdef,
                                               length = self.get_ring().size_info().width
                                               )
                        ]
            i += 1
        return couplers

class __RingRoundedWaveguideCouplers__(__RingWaveguideCouplers__, RingRoundedShape):
    coupler_lengths = RestrictedProperty(allow_none = True, restriction = RestrictList(RESTRICT_NONNEGATIVE), doc = "straight lengths of the couplers. if None, same lengths as the ring will be used")
    coupler_radii = RestrictedProperty(allow_none = True, restriction = RestrictList(RESTRICT_NONNEGATIVE), doc = "radii of the couplers. if None, same radius as the ring will be used")
    coupler_rounding_algorithms = RestrictedProperty(allow_none = True, restriction = RestrictList(RESTRICT_NONNEGATIVE), doc = "rounding algorithm of the couplers. if None, same radius as the ring will be used")
    
    def define_coupler_lengths(self):
        return [self.straights[0] for i in self.coupler_wg_definitions]
        
    def define_coupler_radii(self):
        return [self.bend_radius for i in self.coupler_wg_definitions]
        
    def define_coupler_rounding_algorithms(self):
        return [self.rounding_algorithm for i in self.coupler_wg_definitions]
        
    #def validate_properties(self):
        ### FIXME: COmplete validation code
        # len(self.coupler_radii) == len(self.coupler_wg_definitions)
        # len(self.coupler_lengths) == len(self.coupler_wg_definitions)
        # len(self.coupler_rounding_algorithms) == len(self.coupler_wg_definitions)
        #return super(__RingRoundedWaveguideCouplers__, self).validate_properties()
            
class __RingSymmCouplers__(__RingRoundedWaveguideCouplers__):
    coupler_angles = RestrictedProperty(allow_none = True, restriction = RestrictList(RESTRICT_POSITIVE))
     
    def define_coupler_angles(self):
        return [90.0 for i in self.coupler_wg_definitions]
  
    def define_couplers(self):
        couplers = []
        wg_defs = self.coupler_wg_definitions
        ls = self.coupler_lengths 
        rs = self.coupler_radii
        ras = self.coupler_rounding_algorithms 
        cas = self.coupler_angles 
        i = 1
        for (wgdef, l, r, ra, ca) in zip(wg_defs, ls, rs, ras, cas):
            couplers += [RingSymmWaveguideCoupler(name = self.name + "_coupler_%d" % i,
                                               wg_definition = wgdef,
                                               length = l,
                                               bend_radius = r,
                                               rounding_algorithm = ra,
                                               coupler_angles = (ca,ca),
                                               manhattan = self.manhattan
                                               )
                        ]
            i += 1
        return couplers

    
    
class __RingSBendCouplers__(__RingSymmCouplers__):
    coupler_sbend_straights = RestrictedProperty(allow_none = True, restriction = RestrictList(RESTRICT_NONNEGATIVE))    
    
    def define_coupler_angles(self):
        return [30.0 for i in self.coupler_wg_definitions]
        
    def define_coupler_sbend_straights(self):
        return [TECH.WG.SHORT_STRAIGHT for i in self.coupler_wg_definitions]
     
    def define_couplers(self):
        couplers = []
        wg_defs = self.coupler_wg_definitions
        ls = self.coupler_lengths
        rs = self.coupler_radii
        ras = self.coupler_rounding_algorithms 
        cas = self.coupler_angles 
        css = self.coupler_sbend_straights 
        i = 1
        for (wgdef, l, r, ra, ca, cs) in zip(wg_defs, ls, rs, ras, cas, css):
            couplers += [RingSBendWaveguideCoupler(name = self.name + "_coupler_%d" % i,
                                               wg_definition = wgdef,
                                               length = l,
                                               bend_radius = r,
                                               rounding_algorithm = ra,
                                               coupler_angles = (ca,ca),
                                               sbend_straight = cs,
                                               manhattan = self.manhattan
                                               )
                        ]
            i += 1
        return couplers
    
class __RingBentCouplers__(__RingSBendCouplers__):
    coupler_angles = RestrictedProperty(allow_none = True, restriction = RestrictList(RESTRICT_NUMBER))
    
    def define_coupler_angles(self):
        return [-30.0 for i in self.coupler_wg_definitions]
    
    def define_coupler_lengths(self):
        return [self.straights[0] for i in self.coupler_wg_definitions]
    
    def define_coupler_radii(self):
        return [self.bend_radius + s for s in self.coupler_spacings] #negative radius!

    def define_coupler_rounding_algorithms(self):
        return [self.rounding_algorithm for i in self.coupler_wg_definitions]

    
    
################################################################################
# Defining the coupler transformations in the class
################################################################################

class __RingCouplerTransformations__(StrongPropertyInitializer):
    coupler_spacings = RestrictedProperty(required = True, restriction = RestrictList(RESTRICT_NUMBER), doc = "list of centerline-to-centerline spacings of teh ring couplers")
    coupler_offsets = RestrictedProperty(required = True, restriction = RestrictList(RESTRICT_NUMBER), doc = "list of offsets of the ring couplers along the centerline")
    #def validate_properties(self):
        ### FIXME: COmplete validation code
        # len(self.coupler_spacings) == len(self.coupler_wg_definitions)
        #return super(__RingCouplerTransformations__, self).validate_properties()
    
class __RingCouplerTransformation1__(__RingCouplerTransformations__):
    coupler_spacings = RestrictedProperty(default = [TECH.WG.DC_SPACING], restriction = RestrictList(RESTRICT_NUMBER), doc = "list of centerlin-to-centerline spacings of teh ring couplers")
    coupler_offsets = RestrictedProperty(default = [0.0], restriction = RestrictList(RESTRICT_NUMBER), doc = "list of offsets of the ring couplers along the centerline")
    def define_coupler_transformations(self):
        bs1, bs2 = self.get_bend90_size()
        transformation = Translation((self.coupler_offsets[0], -0.5 * self.straights[1] - bs2 - self.coupler_spacings[0]))
        #transformation = Translation((self.coupler_offsets[0], -0.5 * (self.straights[1] + bs1 + bs2) - self.coupler_spacings[0]))
        return [transformation]

class __Ring180CouplerTransformation2__(__RingCouplerTransformations__):
    coupler_spacings = RestrictedProperty(default = [TECH.WG.DC_SPACING, TECH.WG.DC_SPACING], restriction = RestrictList(RESTRICT_NUMBER), doc = "list of centerlin-to-centerline spacings of teh ring couplers")
    coupler_offsets = RestrictedProperty(default = [0.0, 0.0], restriction = RestrictList(RESTRICT_NUMBER), doc = "list of offsets of the ring couplers along the centerline")
    def define_coupler_transformations(self):
        bs1, bs2 = self.get_bend90_size()
        transformation_south = Translation((self.coupler_offsets[0], -0.5 * self.straights[1] - bs2 - self.coupler_spacings[0]))
        transformation_north = Translation((self.coupler_offsets[1], -0.5 * self.straights[1] - bs2 - self.coupler_spacings[1])) + Rotation(rotation = 180.0)
        #transformation_south = Translation((self.coupler_offsets[0], -0.5 * (self.straights[1] + bs1 + bs2) - self.coupler_spacings[0]))
        #transformation_north = Translation((self.coupler_offsets[1], -0.5 * (self.straights[1] + bs1 + bs2) - self.coupler_spacings[1])) + Rotation(rotation = 180.0)
        return [transformation_south, transformation_north]

class __Ring90CouplerTransformation2__(__Ring180CouplerTransformation2__):
    def define_coupler_transformations(self):
        bs1, bs2 = self.get_bend90_size()
        transformation_south = Translation((self.coupler_offsets[0], -0.5 * self.straights[1] - bs2 - self.coupler_spacings[0]))
        transformation_east = Rotation(rotation = 90.0) + Translation((0.5 * self.straights[0] + bs1 + self.coupler_spacings[1], self.coupler_offsets[1])) 
        return [transformation_south, transformation_east]

################################################################################
# Commonly used Predefined Rings
################################################################################
    
    
class RingRectNotchFilter(__RingStraightCouplers__, __RingCouplerTransformation1__, __RingWaveguideCouplers1__,  RingRect):
    """ rectangular ring filter with one access waveguide (notch filter) """
    __name_prefix__ = "RINGRECT_NOTCH"
        
    
class RingRect180DropFilter(__RingStraightCouplers__, __Ring180CouplerTransformation2__, __RingWaveguideCouplers2__, RingRect):
    """ rectangular ring filter with one straight access waveguide (notch filter) """
    __name_prefix__ = "RINGRECT_180DROP"

class RingRect90DropFilter(__RingStraightCouplers__, __Ring90CouplerTransformation2__,__RingWaveguideCouplers2__,  RingRect):
    """ rectangular ring filter with two straight access waveguides (drop filter) """
    __name_prefix__ = "RINGRECT_90DROP"
    
class RingRectSymmNotchFilter(__RingSymmCouplers__, __RingCouplerTransformation1__, __RingWaveguideCouplers1__, RingRect):
    """ rectangular ring filter with one access waveguide (notch filter) """
    __name_prefix__ = "RINGRECTSYMM_NOTCH"
        
    
class RingRectSymm180DropFilter(__RingSymmCouplers__, __Ring180CouplerTransformation2__,__RingWaveguideCouplers2__,  RingRect):
    """ rectangular ring filter with two access waveguides (drop filter) """
    __name_prefix__ = "RINGRECTSYMM_180DROP"

class RingRectSymm90DropFilter(__RingSymmCouplers__, __Ring90CouplerTransformation2__,__RingWaveguideCouplers2__,  RingRect):
    """ rectangular ring filter with two access waveguides (drop filter) """
    __name_prefix__ = "RINGRECTSYMM_90DROP"
    
class RingRectBentNotchFilter(__RingBentCouplers__, __RingCouplerTransformation1__, __RingWaveguideCouplers1__, RingRect):
    """ rectangular ring filter with one one conformally curved access waveguide (notch filter) """
    __name_prefix__ = "RINGRECTBENT_NOTCH"
        
    
class RingRectBent180DropFilter(__RingBentCouplers__, __Ring180CouplerTransformation2__,__RingWaveguideCouplers2__,  RingRect):
    """ rectangular ring filter with two conformally curved access waveguides (drop filter) """
    __name_prefix__ = "RINGRECTBENT_180DROP"
      

class RingRectSBendNotchFilter(__RingSBendCouplers__, __RingCouplerTransformation1__, __RingWaveguideCouplers1__, RingRect):
    """ rectangular ring filter with one S-curved access waveguide (notch filter) """
    __name_prefix__ = "RINGRECTSBEND_NOTCH"
        
    
class RingRectSBend180DropFilter(__RingSBendCouplers__, __Ring180CouplerTransformation2__,__RingWaveguideCouplers2__,  RingRect):
    """ rectangular ring filter with two S-curved access waveguides (drop filter) """
    __name_prefix__ = "RINGRECTSBEND_180DROP"

