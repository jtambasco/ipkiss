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


from ipkiss.all import *
from ring import RingResonator

class TwoRings(Structure):
    """ structure with two rings defined by the user, which are stacked 
        vertically, with the bottom one flipped. The rings are cascaded in series
        with a route."""
    __name_prefix__ = "TWORING"
    ring1 = DefinitionProperty(restriction = RestrictType(RingResonator))
    ring2 = DefinitionProperty(restriction = RestrictType(RingResonator))
    
    def validate_properties(self):
        if self.ring1.bus_wg_def != self.ring2.bus_wg_def:
            return False # to connect the waveguides, the waveguide should be the same.
        return True
    
    @cache() # not calculated twice, unless needed
    def get_transformations(self):
        # calculate the transformations of the rings based on their properties
        t1 = Translation((0.0, self.ring1.ring_radius + 15.0))
        t2 = VMirror() + Translation((0.0, -self.ring2.ring_radius - 15.0))
        return (t1, t2)

    def get_routes(self):
        # connect the output of the first ring with the input of the second
        # using an automatic routing function
        t1, t2 = self.get_transformations()
        from ipkiss.plugins.photonics.routing.manhattan import RouteManhattan
        route_between = RouteManhattan(input_port = self.ring1.ports[1].transform_copy(t1), 
                                       output_port = self.ring2.ports[0].transform_copy(t2))
        
        return [route_between]
        
    def define_elements(self, elems):
        t1, t2 = self.get_transformations()
        
        # Single References (SREF) place a copy of the layout at a given position with 
        # transformation. This is a reference copy, so the layout data is not duplicated.
        elems += SRef(reference = self.ring1, transformation = t1)
        elems += SRef(reference = self.ring2, transformation = t2)
        
        # add the routes
        from ipkiss.plugins.photonics.routing.connect import RouteConnectorRounded
        for r in self.get_routes():
            elems += RouteConnectorRounded(route  = r)
        return elems
    
    def define_ports(self, prts):
        t1, t2 = self.get_transformations()
        prts += self.ring1.ports[0].transform_copy(t1)
        prts += self.ring2.ports[1].transform_copy(t2)
        return prts
    
        