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

# example: Mach-Zehnders with Structures in the Arms
# We extend the generic MZI classes from the previous examples
# to include a structure in each arm. This can be a ring, to make 
# a ring-loaded MZI, but it can also be spirals, modulators, ...
# For this, we add one class for an MZI arm with a structure, and another 
# class for a complete MZI with a structure in each arm.

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

        # if we route sourh, we just flip the ports, and do allt he calculation 
        # for north. Then at the end we flip again.
        if self.route_south:
            sp = self.splitter_port.transform_copy(VMirror())
            cp = self.combiner_port.transform_copy(VMirror())
        else:
            sp = self.splitter_port
            cp = self.combiner_port
        
        r1a = RouteToNorth(input_port = sp)
        r2a = RouteToNorth(input_port = cp)
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

class MziArmWithStructure(__MziArm__):
    """ A Mach-Zehnder arm with a structure in it: routing upward at right-angle """
    __name_prefix__ = "MZI_STR_ARM"
    structure = StructureProperty(required = True)
    structure_transformation = TransformationProperty()
    port_labels = RestrictedProperty(default = ["W0", "E0"], restriction = RestrictTypeList(str), doc = "Which ports to use to attach the structure to the MZI arm")

    extra_length = NonNegativeNumberProperty(default = 0.0)
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    length = DefinitionProperty()
    route_south = BoolProperty(default = False, doc = "route downward instead of upward")
    
    @cache()
    def get_routes(self):
        from ipkiss.plugins.photonics.routing.to_line import RouteToNorth, RouteToEastAtY, RouteToWestAtY, RouteToEast, RouteToWest

        # if we route south, we just flip the ports, and do allt he calculation 
        # for north. Then at the end we flip again.
        if self.route_south:
            sp = self.splitter_port.transform_copy(VMirror())
            cp = self.combiner_port.transform_copy(VMirror())
        else:
            sp = self.splitter_port
            cp = self.combiner_port
        str_p = self.structure.ports.transform_copy(self.structure_transformation)

        # going up
        r1a = RouteToNorth(input_port = sp, end_straight = 0.0)
        r1b = RouteToEast(input_port = r1a.ports[-1])
        # going towards the center
        r2a = RouteToNorth(input_port = cp, end_straight = 0.0)
        r2b = RouteToWest(input_port = r2a.ports[-1])
        # going outward from the component
        r1c = RouteToWest(input_port = str_p[self.port_labels[0]], end_straight = 0.0)
        r2c = RouteToEast(input_port = str_p[self.port_labels[1]], end_straight = 0.0)
    
        # deterimine which should go more north
        if r1b[-1].y - r1c[-1].y > r2b[-1].y - r2c[-1].y:
            r2b = RouteToWestAtY(input_port = r2a.ports[-1], y_position = r1b.ports[-1].position.y)
        else:
            r1b = RouteToEastAtY(input_port = r1a.ports[-1], y_position = r2b.ports[-1].position.y)

        
        if not self.extra_length==0.0:
            # adjust the length to the user-set length
            y = r2b.ports[-1].position.y + 0.5 * (self.extra_length)
            r2b = RouteToWestAtY(input_port = r2a.ports[-1], y_position = r2b.ports[-1].position.y + 0.5*self.extra_length)
            r1b = RouteToEastAtY(input_port = r1a.ports[-1], y_position = r1b.ports[-1].position.y + 0.5*self.extra_length)

        # moving the structure in place
        extra_translation = (0.5*(r1b[-1].x + r2b[-1].x - (r1c[-1].x + r2c[-1].x)), r1b[-1].y - r1c[-1].y)
        
            
        r1 = r1a + r1b + r1c.reversed().move_copy( extra_translation)
        r2 = r2a + r2b + r2c.reversed().move_copy( extra_translation) 
        
        # don't forget to flip if we calculated everything upside down
        if self.route_south:
            r1.v_mirror()
            r2.v_mirror()
        return [r1, r2]

    
    # this define method is automatically associated with the property 'length',
    # so it will be calculated automatically unless the user manually overrides it
    def define_length(self):
        r1, r2 = self.get_routes()
        return r1.route_length() + r2.route_length() + distance(r1[-1], r2[-1])
        
    def define_elements(self, elems):
        from ipkiss.plugins.photonics.routing.connect import RouteConnectorRounded
        for r in self.get_routes():
            elems += RouteConnectorRounded(route  = r)

        #calculate additional transformation to put the structure in place.
        structure_transform = vector_match_transform(self.structure.ports[self.port_labels[0]].transform_copy(self.structure_transformation),
                                                     self.get_routes()[0].ports[-1]
                                                     )
            
        elems += SRef(reference = self.structure, 
                      transformation = self.structure_transformation + structure_transform
                      )
        return elems

    def define_ports(self, prts):
        r1, r2 = self.get_routes()
        prts += r1.ports[0]
        prts += r2.ports[0]
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
        # size_info objects: information about the footptinr of the object
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
    # this way, properties are calculated automatically, but they can be overriden by the user is 
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

class MZIWithStructures(MZIWaveguides):
    structure1 = StructureProperty(allow_none = True, doc = "None means an ordinary waveguide")
    structure2 = StructureProperty(allow_none = True, doc = "None means an ordinary waveguide")

    structure1_transformation = TransformationProperty()
    structure2_transformation = TransformationProperty()
    
    structure1_port_labels = RestrictedProperty(default = ["W0", "E0"], restriction = RestrictTypeList(str), doc = "Which ports to use to attach the structure to the MZI arm")
    structure2_port_labels = RestrictedProperty(default = ["W0", "E0"], restriction = RestrictTypeList(str), doc = "Which ports to use to attach the structure to the MZI arm")

    @cache()
    def get_transformations(self):
        # size_info objects: information about the footptinr of the object
        si_splitter = self.splitter.size_info() # object with contours of the component
        si_combiner = self.combiner.size_info() # object with contours of the component

        if self.structure1 is None:
            si_structure1 = size_info_from_coord((0.0, 0.0))
        else:
            si_structure1 = self.structure1.size_info()

        if self.structure2 is None:
            si_structure2 = size_info_from_coord((0.0, 0.0))
        else:
            si_structure2 = self.structure2.size_info()
            
        # spacing between components to allow easy routing (can be optimized)
        spacing = 4 * self.bend_radius + TECH.WG.SHORT_STRAIGHT 
                
        t_splitter = IdentityTransform() # place the splitter in (0,0)
        t_arm1 = IdentityTransform()
        t_arm2 = IdentityTransform() 
        t_combiner = Translation((spacing + si_splitter.east - si_combiner.west + max(si_structure1.width, si_structure2.width), 0.0))
        
        return (t_arm1, t_arm2, t_splitter, t_combiner)        

    def get_arms(self):
        if self.structure1 is None:
            arm1 = MziArmWaveguide(splitter_port = self.splitter.ports.transform_copy(self.splitter_transformation)["E1"],
                                   combiner_port = self.combiner.ports.transform_copy(self.combiner_transformation)["W1"],
                                   bend_radius = self.bend_radius
                                   )
        else:
            arm1 = MziArmWithStructure(structure = self.structure1,
                                       structure_transformation = self.structure1_transformation,
                                       port_labels = self.structure1_port_labels,
                                       splitter_port = self.splitter.ports.transform_copy(self.splitter_transformation)["E1"],
                                       combiner_port = self.combiner.ports.transform_copy(self.combiner_transformation)["W1"],
                                       bend_radius = self.bend_radius
                                       )
            
        
        if self.structure2 is None:
            arm2 = MziArmWaveguide(splitter_port = self.splitter.ports.transform_copy(self.splitter_transformation)["E0"],
                                   combiner_port = self.combiner.ports.transform_copy(self.combiner_transformation)["W0"],
                                   route_south = True,
                                   bend_radius = self.bend_radius
                                   )
        else:
            arm2 = MziArmWithStructure(structure = self.structure2,
                                       structure_transformation = self.structure2_transformation,
                                       port_labels = self.structure2_port_labels,
                                       splitter_port = self.splitter.ports.transform_copy(self.splitter_transformation)["E0"],
                                       combiner_port = self.combiner.ports.transform_copy(self.combiner_transformation)["W0"],
                                       bend_radius = self.bend_radius,
                                       route_south = True,
                                       )
        l1 = arm1.length
        l2 = arm2.length
        extra_length = self.delay_length - l1 + l2
        arm1.extra_length = max(extra_length, 0.0)
        arm2.extra_length = max(-extra_length, 0.0)
        
        return (arm1, arm2)
