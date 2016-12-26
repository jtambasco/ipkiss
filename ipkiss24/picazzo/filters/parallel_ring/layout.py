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



#####################################################
# parallel ring filters and ring filter arrays
#####################################################
from ..multi_ring.multi_ring_base import MultiRing, MultiRingIdentical, MultiRingPeriodic
from ..ring import layout as ring
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.routing.manhattan import RouteManhattan
from ipkiss.plugins.photonics.routing.connect import RouteConnectorManhattanExpanded
from ipkiss.all import *
from ipkiss.plugins.photonics.wg.basic import WgElDefinition

__all__ = ["ParallelRing",
           "ParallelRingIdentical",
           "ParallelRingPeriodic",
           "ParallelRingRect180DropFilter",
           "ParallelRingRectNotchFilter",
           "ParallelRingReturnBend",
       ]

####################################################################
# parallel rings (= ring arrays)
####################################################################
class ParallelRing(MultiRing):
    """ parallel rings: rings linked west-ro-east """
    __name_prefix__ = "PARRING"
    process = ProcessProperty(default = TECH.PROCESS.WG)
    suppress_intermediary_ports = BoolProperty(default = True)
    
    routes_intermediary_ports = DefinitionProperty(fdef_name = "define_routes_intermediary_ports")
    routes = DefinitionProperty(fdef_name = "define_routes")
    intermediary_ports = DefinitionProperty(fdef_name = "define_intermediary_ports")
    

    def define_routes_intermediary_ports(self):      
        routes = []
        intermediary_ports = []
        for (R1, T1, R2, T2) in zip (self.rings[0:-1], self.ring_transformations[0:-1], self.rings[1:], self.ring_transformations[1:]):
            P1 = R1.ports.transform_copy(T1).east_ports.y_sorted()
            P2 = R2.ports.transform_copy(T2).west_ports.y_sorted()
            L = min(len(P1), len(P2))
            for (p1, p2) in zip(P1[:L], P2[:L]):
                routes += [RouteManhattan(input_port = p1, output_port = p2)]                
            intermediary_ports += P1[L:]
            intermediary_ports += P2[L:]
        return (routes, intermediary_ports)
    
    def define_routes(self):      
        return self.routes_intermediary_ports[0]

    def define_intermediary_ports(self):      
        return self.routes_intermediary_ports[1]    
    
    def define_elements(self, elems):
        super(ParallelRing, self).define_elements(elems)
        for R in self.routes:
            elems += RouteConnectorManhattanExpanded(route = R, process = self.process)
        return elems

    def define_ports(self, ports):
        # only take west_ports from first and east_ports from last
        P1 = self.rings[0].ports.transform_copy(self.ring_transformations[0]).west_ports
        P2 = self.rings[-1].ports.transform_copy(self.ring_transformations[-1]).east_ports
        ports = P1 + P2
        if not self.suppress_intermediary_ports: P += self.intermediary_ports
        return ports
        

class ParallelRingIdentical(MultiRingIdentical, ParallelRing):
    pass

class ParallelRingPeriodic(MultiRingPeriodic, ParallelRing):
    """ ring periodically placed """
    pass
    

class ParallelRingReturnBend(ParallelRing):
    simple_rings = RestrictedProperty(restriction = RestrictTypeList(ring.__Ring__), required = True)
    rbend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    rbend_min_y = NumberProperty(allow_none = True)
    stub = StructureProperty(allow_none = True)
    rbend_spacing = PositiveNumberProperty(default = TECH.WG.SPACING)
    suppress_intermediary_ports = BoolProperty(default = False)
    rings = DefinitionProperty(fdef_name = "define_rings")

    
    def define_rings(self):
        y_min = self.simple_rings[-1].west_ports.y_sorted()[-1].transform_copy(self.transformations[-1]).position.y
        y_min += 2 * self.rbend_radius + TECH.WG.SHORT_STRAIGHT
        if self.rbend_min_y is None:
            y = y_min
        else:
            y = max(y_min, self.rbend_min_y)

        rings = []
        
        x = self.simple_rings[-1].east_ports.y_sorted()[-1].transform_copy(self.transformations[-1]).position.x
        
        for (r, t) in reversed(zip(self.simple_rings, self.transformations)):
            y_r = r.west_ports.y_sorted()[-1].transform_copy(t).position.y
            s = y - y_r - 2 * self.rbend_radius 
            
            end_x = x - t(Coord2(0.0, 0.0)).x
            
            new_r = ring.RingFilterReturnBend(ring = r, 
                                              rbend_radius = self.rbend_radius, 
                                              rbend_straight = s, 
                                              rbend_end_x = end_x, 
                                              stub = self.stub) # specify end point
            rings += [new_r]
            
            y = new_r.east_ports.y_sorted()[-1].transform_copy(t).position.y + self.rbend_spacing

        rings.reverse()
        return rings

        
def ParallelRingRect180DropFilter(positions, 
                                  coupler_wg_definitions = (TECH.WGDEF.WIRE, TECH.WGDEF.WIRE),
                                  coupler_spacings = (TECH.WG.DC_SPACING, TECH.WG.DC_SPACING), 
                                  bend_radius= TECH.WG.BEND_RADIUS, 
                                  straights = (TECH.WG.SHORT_STRAIGHT, TECH.WG.SHORT_STRAIGHT), 
                                  ring_wg_definition = TECH.WGDEF.WIRE
                                  ):
    R = ring.RingRect180DropFilter(ring_wg_definition = ring_wg_definition,
                                   coupler_wg_definitions = coupler_wg_definitions,
                                   coupler_spacings = coupler_spacings, 
                                   bend_radius = bend_radius, 
                                   straights = straights,
                                   )
    T = [Translation(p) for p in positions]
    return ParallelRingIdentical(ring = R, 
                                 ring_transformations = T, 
                                 )
        

def ParallelRingRectNotchFilter(positions, 
                                coupler_wg_definition = TECH.WGDEF.WIRE,
                                coupler_spacing = TECH.WG.DC_SPACING, 
                                bend_radius= TECH.WG.BEND_RADIUS, 
                                straights = (TECH.WG.SHORT_STRAIGHT, TECH.WG.SHORT_STRAIGHT ),
                                ring_wg_definition = TECH.WGDEF.WIRE
                                  ):
    R = ring.RingRectNotchFilter(ring_wg_definition = ring_wg_definition,
                                   coupler_wg_definitions = (coupler_wg_definition,),
                                   coupler_spacings = (coupler_spacing, ), 
                                   bend_radius = bend_radius, 
                                   straights = straights,
                                   )
    T = [Translation(p) for p in positions]
    return ParallelRingIdentical(rings = R, 
                                 transformations = T, 
                                 process = process
                                 )
        

