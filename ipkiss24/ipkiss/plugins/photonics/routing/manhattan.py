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
from ipkiss.plugins.photonics.port.port import OpticalPortProperty
from .to_line import RouteToManhattan
from .basic import __RouteBasic__
from numpy import sign

__all__ = ["RouteManhattan"]

class RouteManhattanBasic(__RouteBasic__):
    """ routes according to a manhattan pattern when input_port and output_port are manhattan """
    output_port = OpticalPortProperty(required = True)

        
    def define_points(self, pts):        
        threshold = 0.5/get_grids_per_unit()
        bs1, bs2 = self.get_bend90_size()

        # for ease of reasoning: output in (0.0, 0.0) and pointing east.
        T = Rotation((0.0, 0.0), self.output_port.angle_deg + 180.0) + Translation(self.output_port.position) 
        I = self.input_port.reverse_transform_copy(T)
        O = self.output_port.reverse_transform_copy(T)
        S = Shape(closed = False)
        S += I.position
        
        p = I.position
        a = I.angle_deg
        s= self.start_straight
        count = 0
        while 1:
            count += 1
            if count > 40:
                LOG.error("Exceeds allowed steps in RouteManhattanBasic: \nInput:%s\nOutput:%s\nShape:%s" %
                          (str(self.input_port), str(self.output_port), str(S.points))
                          )
                raise AttributeError()
            # not ready for final bend: go over possibilities
            sigp = sign(p[1])
            if not sigp: sigp=1
            if a%360.0 == 0.0:
                #same directions
                if abs(p[1]) < threshold and p[0]<= threshold:
                    # we made it!
                    S += O.position
                    break
                elif p[0] + (bs1 + bs2 + self.end_straight+s) < threshold and abs(p[1])  - (bs1 + bs2 + self.min_straight) > -threshold:
                    # sufficient space for S-bend
                    p = (-self.end_straight - bs2, p[1])
                    a = -sigp * 90.0
                elif p[0] + (2 * bs1 + 2 * bs2 + self.end_straight + s + self.min_straight) < threshold:
                    # sufficient distance to move aside
                    p = (p[0] + s + bs1, p[1]) 
                    a = -sigp * 90.0
                elif abs(p[1]) - (2 * bs1 + 2 * bs2 + 2 * self.min_straight) > - threshold:
                    p = (p[0] + s + bs1, p[1])
                    a = -sigp * 90.0
                else: 
                    p = (p[0] + s + bs1, p[1]) 
                    a = sigp * 90.0
                #else:
                    #S.add_polar(s + bs2, 0.0)
                    #S.add_polar(bs1 + bs2 + self.min_straight, sigp * 90.0)
                    #S.add_polar(bs1 + bs2 + self.min_straight, 0.0)
                    #p = (p[0]+s+self.min_straight + 2 * bs1 + bs2, sigp * min(max(0.5 * abs(p[1]), abs(p[1])-self.min_straight), bs1 + bs2 + self.min_straight))
                    #a = 180.0
                    

            elif a == 180.0:
                # opposite directions
                if abs(p[1]) - (bs1 + bs2 + self.min_straight) > - threshold:
                    # far enough: U-turn
                    p = (min(p[0] - s, -self.end_straight) - bs2, p[1])
                    a = -sigp * 90.0
                else:
                    # more complex turn
                    p = (min(p[0] - s - bs1, -self.end_straight - self.min_straight - 2 * bs1 - bs2) , p[1])
                    a = -sigp * 90.0
            elif a % 180.0 == 90.0:
                siga = -sign((a % 360.0) - 180.0)
                if not siga: siga = 1
                
                if ((-p[1] * siga) - (s+bs2) > -threshold) and (-p[0] - (self.end_straight+bs2)) > -threshold:
                    # simple case: one right angle to the end
                    p = (p[0], 0.0)
                    a = 0.0
                elif (p[1] * siga) <= threshold and p[0] +(self.end_straight+bs1) > - threshold:
                    # go to the west, and then turn upward
                    # this will sometimes result in too sharp bends, but there is no avoiding this!
                    p = (p[0], sigp * min(max(min(self.min_straight, 0.5*abs(p[1])), abs(p[1])-s- bs1), bs1 + bs2 + self.min_straight))
                    a = 180.0
                elif -p[0] - (self.end_straight+2*bs1 + bs2+ self.min_straight) > -threshold:
                    # go sufficiently up, and then east
                    p = (p[0], siga * max(p[1] * siga + s + bs1, bs1 + bs2+ self.min_straight))
                    a = 0.0
                elif -p[0] - ( self.end_straight + bs2) > - threshold:
                    # make vertical S-bend to get sufficient room for movement
                    S += (p[0], p[1] + siga * (bs2 + s))
                    p = (min(p[0] - bs1 + bs2 + self.min_straight, - 2 * bs1 -bs2 - self.end_straight - self.min_straight),p[1] + siga * (bs2 + s))
                    # a remains the same
                else:
                    # tricky case, because there is no valable solution for this
                    # doing the best we can, but this could sometimes result in crossed waveguides
                    p = (p[0], p[1] + sigp * (s + bs1))
                    a = 180.0
            S += p
            s = self.min_straight + bs1
        pts += S.transform(T)
        return pts

class RouteManhattan(RouteManhattanBasic):
    """ generates a shape to route between an input port and output port according to a manhattan pattern"""
    
    def define_points(self, pts):     
        S1 = RouteToManhattan(input_port = self.input_port, 
                              bend_radius = self.bend_radius, 
                              min_straight = self.min_straight, 
                              rounding_algorithm = self.rounding_algorithm)
        S1.start_straight = self.start_straight
        S3 = RouteToManhattan(input_port= self.output_port, 
                              bend_radius = self.bend_radius, 
                              min_straight = self.min_straight, 
                              rounding_algorithm = self.rounding_algorithm)
        S3.start_straight = self.end_straight
        S2 = RouteManhattanBasic(input_port = S1.out_ports[0], 
                                 output_port = S3.out_ports[0], 
                                 bend_radius = self.bend_radius, 
                                 min_straight = self.min_straight, 
                                 rounding_algorithm = self.rounding_algorithm)
        S2.start_straight = 0.0
        S2.end_straight = 0.0
        S3.reverse()
        pts += (S1[0:-1] + S2 + S3[0:])
        return pts
    
