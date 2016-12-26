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

# example: A generic Mach-Zehnder component
# We define it quite generic, and then make a special subclass which makes a simple 
# MZI with two waveguides.



from ipkiss.all import *
from ipkiss.plugins.photonics.port import OpticalPort
from dircoup import DirectionalCoupler


# We define the arms of an MZI in seperate classes.
# This way, they can be hierarchically inserted into the MZI
# and we can use subclassing to make more special types of arms

class __MziArm__(Structure):
    """ abstract base class for an arm in a Mach-Zehnder interferometer """
    __name_prefix__ = "MZI_ARM"
    splitter_port = DefinitionProperty(restriction = RestrictType(OpticalPort))
    combiner_port = DefinitionProperty(restriction = RestrictType(OpticalPort))
    
class MziArmWaveguide(__MziArm__):
    """ A Mach-Zehnder arm with a given length: routing upward at right-angle """
    __name_prefix__ = "MZI_WG_ARM"
    extra_length = NonNegativeNumberProperty(default = 0.0)
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    length = DefinitionProperty()
    route_south = BoolProperty(default = False, doc = "route downward instead of upward")
    
    @cache()
    def get_route(self):
        from ipkiss.plugins.photonics.routing.to_line import RouteToNorth, RouteToEastAtY, RouteToWestAtY, RouteToEast, RouteToWest

        # if we route south, we just flip the ports, and do all the calculation 
        # for north. Then at the end we flip again.
        if self.route_south:
            sp = self.splitter_port.transform_copy(VMirror())
            cp = self.combiner_port.transform_copy(VMirror())
        else:
            sp = self.splitter_port
            cp = self.combiner_port
        
        r1a = RouteToNorth(input_port = sp, end_straight = 0.0)
        r2a = RouteToNorth(input_port = cp, end_straight = 0.0)
        # check which one ends up northmost, and bend both of them
        # toward each other at the same height.
        if r1a[-1].y > r2a[-1].y:
            r1b = RouteToEast(input_port = r1a.ports[-1])
            r2b = RouteToWestAtY(input_port = r2a.ports[-1], y_position = r1b.ports[-1].position.y)
        else:
            r2b = RouteToWest(input_port = r2a.ports[-1])
            r1b = RouteToEastAtY(input_port = r1a.ports[-1], y_position = r2b.ports[-1].position.y)
        r = r1a + r1b + r2b.reversed() + r2a.reversed()
        
        if not self.extra_length==0.0:
            # adjust the length to the user-set length
            y = r2b.ports[-1].position.y + 0.5 * (self.extra_length)
            r2b = RouteToWestAtY(input_port = r2a.ports[-1], y_position = y)
            r1b = RouteToEastAtY(input_port = r1a.ports[-1], y_position = y)

            r = r1a + r1b + r2b.reversed() + r2a.reversed()
        
        # don't forget to flip if we calculated everything upside down
        if self.route_south:
            r.v_mirror()
        return r

    # this define method is automatically associated with the property 'length',
    # so it will be calculated automatically unless the user manually overrides it
    def define_length(self):
        return self.get_route().route_length()
        
    def define_elements(self, elems):
        from ipkiss.plugins.photonics.routing.connect import RouteConnectorRounded
        elems += RouteConnectorRounded(route  = self.get_route())
        return elems

    def define_ports(self, prts):
        prts += self.get_route().ports
        return prts
        

#
# Mach-Zehnder classes
#        
class MZI (Structure):
    """ generic MZI, taking a splitter, combiner and two __MziArm__ objects """
    __name_prefix__ = "MZI"
    arm1 = DefinitionProperty(restriction = RestrictType(__MziArm__))
    arm2 = DefinitionProperty(restriction = RestrictType(__MziArm__))
    splitter = DefinitionProperty(restriction = RestrictType(DirectionalCoupler))
    combiner = DefinitionProperty(restriction = RestrictType(DirectionalCoupler))

    arm1_transformation = TransformationProperty()
    arm2_transformation = TransformationProperty()
    splitter_transformation = TransformationProperty()
    combiner_transformation = TransformationProperty()
    
    def define_elements(self, elems):
        # Single References (SREF) place a copy of the layout at a given position with 
        # transformation. This is a reference copy, so the layout data is not duplicated.
        elems += SRef(reference = self.splitter, transformation = self.splitter_transformation)
        elems += SRef(reference = self.combiner, transformation = self.combiner_transformation)
        elems += SRef(reference = self.arm1, transformation = self.arm1_transformation)
        elems += SRef(reference = self.arm2, transformation = self.arm2_transformation)
        return elems
        
    def define_ports(self, prts):
        prts += self.splitter.ports.transform_copy(self.splitter_transformation).west_ports()
        prts += self.combiner.ports.transform_copy(self.combiner_transformation).east_ports()
        return prts

class MZIWaveguides(MZI):
    """ A MZI with two simple waveguide arms """
    __name_prefix__ = "MZI_WG"
    delay_length = NumberProperty(required = True, doc = "if positive, the upper arms is longer, if negative, the lower arm")
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)

    
    # Locked_properties make it impossible for the user to manually set the property
    # it will only be calculated automatically through a define method or default value
    arm1 = LockedProperty()
    arm2 = LockedProperty()
    arm1_transformation = LockedProperty()
    arm2_transformation = LockedProperty()
    splitter_transformation = LockedProperty()
    combiner_transformation = LockedProperty()
    
    @cache()
    def get_transformations(self):
        # size_info objects: information about the footprint of the object
        si_splitter = self.splitter.size_info() # object with contours of the component
        si_combiner = self.combiner.size_info() # object with contours of the component
        
        # spacing between components to allow easy routing (can be optimized)
        spacing = 4 * self.bend_radius + TECH.WG.SHORT_STRAIGHT 
                
        t_splitter = IdentityTransform() # place the splitter in (0,0)
        t_arm1 = IdentityTransform()
        t_arm2 = IdentityTransform() 
        t_combiner = Translation((spacing + si_splitter.east - si_combiner.west, 0.0))
        
        return (t_arm1, t_arm2, t_splitter, t_combiner)        
    
    # these define functions are automatically linked to the properties with the respective name
    # this way, properties are calculated automatically, but they can be overriden by the user if 
    # this is needed.
    def define_arm1_transformation(self):
        return self.get_transformations()[0]
    def define_arm2_transformation(self):
        return self.get_transformations()[1]
    def define_splitter_transformation(self):
        return self.get_transformations()[2]
    def define_combiner_transformation(self):
        return self.get_transformations()[3]

    def get_arms(self):
        arm1 = MziArmWaveguide(splitter_port = self.splitter.ports.transform_copy(self.splitter_transformation)["E1"],
                               combiner_port = self.combiner.ports.transform_copy(self.combiner_transformation)["W1"],
                               bend_radius = self.bend_radius
                               )
        # arm 2 is calculated upside down
        arm2 = MziArmWaveguide(splitter_port = self.splitter.ports.transform_copy(self.splitter_transformation)["E0"],
                               combiner_port = self.combiner.ports.transform_copy(self.combiner_transformation)["W0"],
                               route_south = True,
                               bend_radius = self.bend_radius
                               )
        l1 = arm1.length
        l2 = arm2.length
        extra_length = self.delay_length - l1 + l2
        arm1.extra_length = max(extra_length, 0.0)
        arm2.extra_length = max(-extra_length, 0.0)
        
        return (arm1, arm2)
    
    def define_arm1(self):
        return self.get_arms()[0]
    def define_arm2(self):
        return self.get_arms()[1]
    
