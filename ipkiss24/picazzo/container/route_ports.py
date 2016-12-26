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

from ipkiss.plugins.photonics.routing.to_line import *
from ipkiss.plugins.photonics.routing.basic import Route
from .fanout import FanoutPorts
from .container import __StructureContainerWithRoutes__
from ipkiss.all import *


__all__ = ["RoutePortsAroundCorner",
           "RoutePortsEastWest"]


class RoutePortsAroundCorner(FanoutPorts):
    __name_prefix__ = "ROUTECORNER"
    first_step_direction = RestrictedProperty(required = True, restriction = RestrictValueList([NORTH, SOUTH, EAST, WEST]))
    reference_coordinate_first_step = NumberProperty(allow_none = True)
    first_step_spacing = PositiveNumberProperty(default = TECH.WG.SPACING)
    
    def define_routes(self):
        routes = []
        SI = self.structure.size_info().transform(self.structure_transformation)
            
        first_step_sign = -1.0 if self.output_direction in [NORTH, EAST] else 1.0
        second_step_sign = 1.0 if self.first_step_direction in [NORTH, EAST] else -1.0
        
        first_step_relation = '<' if self.output_direction in [NORTH, EAST] else '>'
        second_step_relation = '>' if self.first_step_direction in [NORTH, EAST] else '<'
        
        first_step = first_step_sign * self.first_step_spacing

        if self.reference_coordinate_first_step is None:
            first_base = SI.get_border_on_one_side(-self.output_direction) + first_step
        else:
            first_base = self.reference_coordinate_first_step

        second_step = self.spacing * second_step_sign
        if self.reference_coordinate is None:
            second_base = SI.get_border_on_one_side(self.first_step_direction) + second_step
        else:
            second_base = self.reference_coordinate
            
        if self.target_coordinate is None:
            target = SI.get_border_on_one_side(self.output_direction)
        else:
            target = self.target_coordinate
            
        routes = []
        PL = self.__get_labeled_ports__()

        for p in PL.sorted_in_direction(-self.first_step_direction):
            R = RouteToManhattanRelativeToPosition(input_port = p,
                                                   direction = self.first_step_direction,
                                                   position = first_base,
                                                   relation = first_step_relation,
                                                   end_straight = 0.0,
                                                   bend_radius = self.bend_radius,
                                                   rounding_algorithm = self.rounding_algorithm
                                                   )
            first_base = -first_step_sign * R.out_ports[0].position.dot(self.output_direction) + first_step
                                                   
            R2 = RouteToManhattanRelativeToPosition(input_port = R.out_ports[0], 
                                                    direction = self.output_direction,
                                                    position = second_base,
                                                    relation = second_step_relation,
                                                    rounding_algorithm = self.rounding_algorithm,
                                                    bend_radius = self.bend_radius,
                                                    end_straight = 0.0)
            R2.end_straight += max(0.0, -first_step_sign * (target + first_step_sign * R2.out_ports[0].position.dot(self.output_direction)) )
            second_base = second_step_sign * R2.out_ports[0].position.dot(self.first_step_direction) + second_step
            
            routes += [Route(input_port = R.input_port, points = R + R2, bend_radius = self.bend_radius, rounding_algorithm = self.rounding_algorithm)]
        return routes
    
    
    def define_ports(self, prts):
        from copy import deepcopy
        for (P, R) in zip(self.__get_labeled_ports__(), self.routes):
            new_port = deepcopy(P)
            new_port.position = R.points[-1]
            new_port.angle_deg = angle_deg(self.output_direction)
            prts += new_port
        prts.extend(self.__get_unlabeled_ports__())
        return prts


class RoutePortsEastWest(__StructureContainerWithRoutes__):
    """ routes the specified ports of a structure to the west, and the rest to the east.
        A lot of the stuff is automatic, so it might not be exactly what you want.
    """
    __name_prefix__ = "RPLR"
    spacing = PositiveNumberProperty(default = 25.0)
    ports_to_west = RestrictedProperty(required = True, restriction = RestrictTypeList(str))
    ports_to_east = RestrictedProperty(required= True, restriction = RestrictTypeList(str))
    reference_east = StringProperty(allow_none = True, doc = "Port Label of port that serves as y reference")
    reference_west = StringProperty(allow_none = True, doc = "Port Label of port that serves as y reference")

    def __get_west_routes__(self):
        SPL= self.get_structure_port_list()
        west_routes = []
        if len(self.ports_to_west)> 0:
            if self.reference_west is None:
                ref_west = self.ports_to_west[0]
            else:
                ref_west = self.reference_west
            R = RouteToWest(input_port = SPL[ref_west],
                            bend_radius = self.bend_radius,
                            rounding_algorithm = self.rounding_algorithm)
            y = R.out_ports[0].position.y - self.spacing * self.ports_to_west.index(ref_west)
            for p in self.ports_to_west:
                port = SPL[p]
                west_routes += [RouteToWestAtY(input_port = port, 
                                               y_position = y,
                                               bend_radius = self.bend_radius,
                                               rounding_algorithm = self.rounding_algorithm)]
                y += self.spacing
                
            # find westmost point
            LM = 10000000000
            for r in west_routes:
                LM = min(r.out_ports[0].position.x, LM)
            for r in west_routes:
                r.end_straight = r.end_straight + r.out_ports[0].position.x - LM
        return west_routes
    
    def __get_east_routes__(self):   
        SPL= self.get_structure_port_list()
        east_routes = []
        if len(self.ports_to_east) > 0:
            if self.reference_east is None:
                ref_east = self.ports_to_east[0]
            else:
                ref_east = self.reference_east
            R = RouteToEast(input_port = SPL[ref_east],
                            bend_radius = self.bend_radius,
                            rounding_algorithm = self.rounding_algorithm)
            y = R.out_ports[0].position.y - self.spacing * self.ports_to_east.index(ref_east)
            for p in self.ports_to_east:
                port = SPL[p]
    
                if y is None: y = port.position.y
                east_routes += [RouteToEastAtY(input_port = port, 
                                               y_position = y,
                                               bend_radius = self.bend_radius,
                                               rounding_algorithm = self.rounding_algorithm)]
                y += self.spacing
            

                # find eastmost point
                LM = -10000000000
                for r in east_routes:
                    LM = max(r.out_ports[0].position.x, LM)
                for r in east_routes:
                    r.end_straight = r.end_straight + LM - r.out_ports[0].position.x 
        return east_routes
   
    #def define_waveguides(self):
        #return super(RoutePortsEastWest,self).define_waveguides()
    
    def define_routes(self):
        west_routes = self.__get_west_routes__()
        east_routes = self.__get_east_routes__()
        return west_routes + east_routes
    
    def define_elements(self, elems):
        return super(RoutePortsEastWest,self).define_elements(elems)
    
    def define_ports(self, port_list):
        from copy import deepcopy
        SPL= self.get_structure_port_list()
        west_routes = self.__get_west_routes__()
        for port_ref,R in zip(self.ports_to_west, west_routes):
            new_port = deepcopy(SPL[port_ref])
            new_port.position = R.points[-1]
            new_port.angle = R.angles_deg()[-2]
            port_list += new_port
        east_routes = self.__get_east_routes__()  
        for port_ref,R in zip(self.ports_to_east, east_routes):
            new_port = deepcopy(SPL[port_ref])
            new_port.position = R.points[-1]
            new_port.angle = R.angles_deg()[-2]
            port_list += new_port     
        return port_list
    


