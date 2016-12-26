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

# example: A ring-loaded Mach-Zehnder interferometer.
# A directiopnal coupler is used for splitter and combiner
# and each MZI arm has a ring in it.


from ipkiss.all import *
from ring import RingResonator
from dircoup import DirectionalCoupler

class RingLoadedMZI(Structure):
    """ A Mach-Zehnder with a ring resonator in each arm 
    """
    
    __name_prefix__ = "TWORING"
    ring1 = DefinitionProperty(restriction = RestrictType(RingResonator))
    ring2 = DefinitionProperty(restriction = RestrictType(RingResonator))
    splitter = DefinitionProperty(restriction = RestrictType(DirectionalCoupler))
    combiner = DefinitionProperty(restriction = RestrictType(DirectionalCoupler))
    connect_bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    
    @cache() # not calculated twice, unless needed
    def get_transformations(self):
        # calculate the transformations of the components based on their properties
        # simplified here: placement should be done based on their 

        # size_info objects: information about the footprint of the object
        si_splitter = self.splitter.size_info() # object with contours of the component
        si_combiner = self.combiner.size_info() # object with contours of the component
        si_ring1    = self.ring1.size_info() # object with contours of the component
        si_ring2    = self.ring2.size_info() # object with contours of the component

        si_dircoups = si_splitter + si_combiner # union of contours
        
        # spacing between components to allow easy routing (can be optimized)
        spacing = 2 * self.connect_bend_radius + 3* TECH.WG.SHORT_STRAIGHT 
                
        # splitter1
        t_splitter = IdentityTransform() # place the splitter in (0,0)
        
        # ring1
        t_ring1 = Translation((si_splitter.east - si_ring1.west + spacing, 
                               si_dircoups.north - si_ring1.south + spacing ))
        
        # ring2
        t_ring2 = VMirror() + Translation((si_splitter.east - si_ring2.west + spacing, 
                                           si_dircoups.south + si_ring2.south - spacing))
        
        si_rings = si_ring1.transform(t_ring1) + si_ring2.transform(t_ring2)
        
        # combiner
        t_combiner = Translation((si_rings.east - si_combiner.west + spacing,0.0))
        
        return (t_ring1, t_ring2, t_splitter, t_combiner)

    def get_routes(self):
        # connect the outputs of the splitter and the inputs of the combiner with both rings
        # using automatic routing functions
        t_ring1, t_ring2, t_splitter, t_combiner = self.get_transformations()
        from ipkiss.plugins.photonics.routing.manhattan import RouteManhattan
        r1 = RouteManhattan(input_port = self.splitter.ports.transform_copy(t_splitter)["E1"],
                            output_port = self.ring1.ports.transform_copy(t_ring1)["W0"])
        r2 = RouteManhattan(input_port = self.splitter.ports.transform_copy(t_splitter)["E0"],
                            output_port = self.ring2.ports.transform_copy(t_ring2)["W0"])
        r3 = RouteManhattan(input_port = self.ring1.ports.transform_copy(t_ring1)["E0"],
                            output_port = self.combiner.ports.transform_copy(t_combiner)["W1"])
        r4 = RouteManhattan(input_port = self.ring2.ports.transform_copy(t_ring2)["E0"],
                            output_port = self.combiner.ports.transform_copy(t_combiner)["W0"])
        
        return [r1, r2, r3, r4]
        
    def define_elements(self, elems):
        t_ring1, t_ring2, t_splitter, t_combiner = self.get_transformations()
        
        # Single References (SREF) place a copy of the layout at a given position with 
        # transformation. This is a reference copy, so the layout data is not duplicated.
        elems += SRef(reference = self.splitter, transformation = t_splitter)
        elems += SRef(reference = self.combiner, transformation = t_combiner)
        elems += SRef(reference = self.ring1, transformation = t_ring1)
        elems += SRef(reference = self.ring2, transformation = t_ring2)
        
        # add the routes
        from ipkiss.plugins.photonics.routing.connect import RouteConnectorRounded
        for r in self.get_routes():
            elems += RouteConnectorRounded(route  = r)
        return elems
    
    def define_ports(self, prts):
        t_ring1, t_ring2, t_splitter, t_combiner = self.get_transformations()
        prts += self.splitter.ports.transform_copy(t_splitter).west_ports()
        prts += self.combiner.ports.transform_copy(t_combiner).east_ports()
        return prts
    
        