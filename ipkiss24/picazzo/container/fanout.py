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

from .container import __StructureContainerWithPortLabels__, __StructureContainerWithRoutes__
from ipkiss.plugins.photonics.routing.to_line import RouteToLine, RouteToAngle
from ipkiss.plugins.photonics.routing.connect import RouteConnector
from ipkiss.plugins.photonics.wg.connect import __RoundedWaveguide__
from ipkiss.plugins.photonics.wg.bundle import WgElBundleWaveguides

from ipkiss.all import *

__all__ = ["FanoutPorts"]

class FanoutPorts( __StructureContainerWithPortLabels__, __StructureContainerWithRoutes__):
    """ Fanout Container"""
    __name_prefix__ = "FANOUT"
    spacing = PositiveNumberProperty(default = 25.0)
    output_direction = RestrictedProperty(required = True, restriction = RestrictValueList([NORTH, SOUTH, EAST, WEST]))
    reference_coordinate = NumberProperty(allow_none = True)
    max_s_bend_angle = AngleProperty(default = 60.0, restriction = RestrictRange(lower = 0.0, upper = 90.0, lower_inc = False, upper_inc = True))
    suppress_other_ports = BoolProperty(default = False)
    bundled = BoolProperty(default = False)
    target_coordinate = NumberProperty(allow_none = True)
    
    def define_elements(self, elems):
        super(FanoutPorts, self).define_elements(elems)
            
        r = [RouteConnector(R) for R in self.routes]
        if self.bundled:
            elems += WgElBundleWaveguides(waveguides = r)
        else:
            elems += r
        return elems

    def define_routes(self):
        routes =[]           
        # reference coordinate
        pl = self.__get_labeled_ports__()
        if len(pl)>0:
            if self.reference_coordinate is None:
                p = pl[0]
                if self.output_direction == NORTH or self.output_direction==SOUTH:
                    refcoord = p.position.x
                else:
                    refcoord = p.position.y
            else:
                refcoord = self.reference_coordinate
    
            
            if self.output_direction == NORTH:
                c = Coord2(refcoord, 0.0)
                a = 90.0
                mf = max
                i = 1
                s = 1
            elif self.output_direction == SOUTH:
                c = Coord2(refcoord, 0.0)
                a = -90.0
                mf = min
                i = 1
                s = -1
            elif self.output_direction == EAST:
                c = Coord2(0.0, refcoord)
                a = 0.0
                mf = max
                i = 0
                s = 1
            elif self.output_direction == WEST:
                c = Coord2(0.0, refcoord)
                a = 180.0
                mf = min
                i = 0
                s = -1
             
            for p in pl:
                r = RouteToLine(input_port = p,
                                line_point = c,
                                angle_out = a,
                                max_s_bend_angle = self.max_s_bend_angle,
                                bend_radius = self.bend_radius,
                                rounding_algorithm = self.rounding_algorithm,
                                )
                c = Coord2(c.x, c.y)
                c[(i+1)%2] += self.spacing
                routes += [r]
                
            mp = routes[0].out_ports[0].position[i]
            for r in routes[1:]:
                mp = mf(mp, r.out_ports[0].position[i])
            if not self.target_coordinate is None:
                mp = mf(mp, self.target_coordinate)
                
            
            for r in routes:
                r.end_straight +=  s * (mp - r.out_ports[0].position[i]) 
        
        return routes
    
    def define_ports(self, prts):
        from copy import deepcopy
        for (P, R) in zip(self.__get_labeled_ports__(), self.routes):
            new_port = deepcopy(P)
            new_port.position = R.points[-1]
            if (self.output_direction == NORTH):
                new_port.angle = 90.0
            elif (self.output_direction == SOUTH):
                new_port.angle = 270.0
            elif (self.output_direction == EAST):
                new_port.angle = 0.0
            elif (self.output_direction == WEST):
                new_port.angle = 180.0
            prts += new_port
        if not self.suppress_other_ports:
            prts.extend(self.__get_unlabeled_ports__())
        return prts
    
