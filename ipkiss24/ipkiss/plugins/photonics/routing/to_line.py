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
from ipcore.helperfunc import extract_kwarg
from .basic import __RouteBasic__
from math import cos, sin, tan, atan, atan2, sqrt
from ipkiss.plugins.photonics.port.port import OpticalPort
from numpy import sign, arange
import math

__all__ = ["RouteToAngle",
           "RouteToSouth",
           "RouteToSouthAtMaxX",
           "RouteToSouthAtMinX",
           "RouteToSouthAtX",
           "RouteToHorizontal",
           "RouteToHorizontalAtY",
           "RouteToWest",
           "RouteToWestAtMaxY",
           "RouteToWestAtMinY",
           "RouteToWestAtY",
           "RouteToLine",
           "RouteToManhattan",
           "RouteToParallelLine",
           "RouteToEast",
           "RouteToEastAtMaxY",
           "RouteToEastAtMinY",
           "RouteToEastAtY",
           "RouteToNorth",
           "RouteToNorthAtMaxX",
           "RouteToNorthAtMinX",
           "RouteToNorthAtX",
           "RouteToVertical",
           "RouteToVerticalAtX",
           "RouteToManhattanRelativeToPosition"]
           

class RouteToAngle(__RouteBasic__):
    """ gives a route to bend a port to a given angle """
    angle_out = AngleProperty(default = 0.0)
    
        
    def define_points(self, pts):
        # start point
        pts.append(self.input_port.position)

        angle = round(self.angle_out - self.input_port.angle_deg, 5)%360.0
        if angle == 0.0:
            pts = points_add_polar(pts,max(self.start_straight, self.end_straight) , self.angle_out)
        elif angle == 180.0:
            bs1_90, bs2_90 = self.get_bend90_size()
            pts = points_add_polar(pts,self.start_straight + bs1_90, self.input_port.angle_deg)
            pts = points_add_polar(pts,self.min_straight + bs1_90 + bs2_90, self.input_port.angle_deg + 90.0)
            pts = points_add_polar(pts,self.end_straight + bs2_90, self.input_port.angle_deg + 180.0)
        else:
            bs1, bs2 = self.get_bend_size(angle)
            pts = points_add_polar(pts,self.start_straight + bs1, self.input_port.angle_deg)
            pts = points_add_polar(pts,self.end_straight + bs2 , self.angle_out)
        return pts

class RouteToEast(RouteToAngle):
    """ route a port to a horizontal pointing east """
    
    def define_angle_out(self):
        return 0.0
                        
class RouteToWest(RouteToAngle):
    """ route a port to a horizontal pointing west """
    
    def define_angle_out(self):
        return 180.0                      

                        
class RouteToNorth(RouteToAngle):
    """ route a port to a horizontal pointing north """
    
    def define_angle_out(self):
        return 90.0                           

                        
class RouteToSouth(RouteToAngle):
    """ route a port to a horizontal pointing south """
    
    def define_angle_out(self):
        return -90.0    
    
class RouteToHorizontal(RouteToAngle):
    """ route a port to the horizontal (west or east, whichever is closest) """
    
    def define_angle_out(self):
        a = self.input_port.angle_deg%360.0
        if a<=90 or a>270.0:
            return 0.0 #route to east
        else:
            return 180.0 #route to west    

                        
class RouteToVertical(RouteToAngle):
    """ route a port to the horizontal (west or east, whichever is closest) """
    
    def define_angle_out(self):
        a = self.input_port.angle_deg%360.0
        if a<180 and a>=0.0:
            return 90.0 #route to north
        else:
            return -90.0 #route to south                          
    
    
class RouteToManhattan(RouteToAngle):
    """ route a port to the nearest manhattan direction """
    
    def define_angle_out(self):
        a = self.input_port.angle_deg%360.0    
        if a<135.0 and a>45.0:
            return 90.0
        elif a<=225.0 and a>=135.0:
            return 180.0
        elif a<315.0 and a>225.0:
            return -90.0
        else:
            return 0.0   
     

class __RouteToLine__(RouteToAngle):  
    line_point = Coord2Property(required = True)
    max_s_bend_angle = AngleProperty(default = 90.0)
    
class RouteToParallelLine(__RouteToLine__):
    """ gives a route that bends a port to a parallel line through a given point """
    line_point = Coord2Property(required = True)
    max_s_bend_angle = AngleProperty(default = 90.0)
    angle_out = DefinitionProperty(fdef_name = "define_angle_out")
    s_bend_angle_resolution = AngleProperty(default= -0.1)
    
    def define_angle_out(self):
        return self.input_port.angle_deg

    def find_angle(self,D,max_a, min_a, res_a):
        if int(abs(max_a-min_a)/abs(res_a))<=2.0:
            return min_a
        h_a = 0.5*(max_a+min_a)
        h_bs1, h_bs2 = self.get_bend_size(h_a)
        Lh = (h_bs1 + h_bs2 + self.min_straight)
        if  D < Lh * sin(h_a * DEG2RAD):
            return self.find_angle(D,h_a,min_a, res_a)
        else:
            return self.find_angle(D,max_a,h_a, res_a)
        
        
    def define_points(self, pts):
        pts.append(self.input_port.position)
        line = straight_line_from_point_angle(self.line_point, self.angle_out)
        line2 = straight_line_from_point_angle(self.input_port.position, self.input_port.angle_deg)

        # parallel or coinciding
        if line == line2:
            # coinciding
            pts = points_add_polar(pts,max(self.start_straight, self.end_straight), self.angle_out)
        else:
            D = line.distance(self.input_port.position)
            max_bs1, max_bs2 = self.get_bend_size(self.max_s_bend_angle)
            Lmax = (max_bs1 + max_bs2 + self.min_straight)
            if  D >= Lmax * sin(self.max_s_bend_angle * DEG2RAD):
                angle = self.max_s_bend_angle
            angle = self.find_angle(D,self.max_s_bend_angle,0.0,self.s_bend_angle_resolution)
            #for angle in arange(self.max_s_bend_angle, 0.0, self.s_bend_angle_resolution):
                #bs1, bs2 = self.get_bend_size(angle)
                #L = (bs1 + bs2 + self.min_straight)
                #if  D >= L * sin(angle * DEG2RAD):
                    #break

                # Sufficiently far apart: max_s_bend_angle bends
            if angle%90.0 == 0.0:
                Dx = 0.0
            else:
                Dx = D  / tan(angle * DEG2RAD)
            
            bs1, bs2 = self.get_bend_size(angle)
            pts = points_add_polar(pts, self.start_straight + bs1, self.input_port.angle_deg)

            P = self.input_port.position.move_polar_copy(self.start_straight + bs1 + Dx, self.input_port.angle_deg)
            P = line.closest_point(P)
            pts.append((P.x, P.y))
            pts = points_add_polar(pts, self.end_straight + bs2, self.angle_out)
        return pts
    

class RouteToLine(__RouteToLine__):
    """ gives a route that bends a port to get fit on a line defined by a point and an angle """
        
    def define_points(self, pts):
        # there are quite some cases to take into account here
        angle = (self.angle_out - self.input_port.angle_deg + 180.0)%360.0-180.0 #the difference between the angles 'angle_out' and 'angle_deg' (normalized between -180 and +180), to know if the bend is to be made in negative or positive sense
        bs1, bs2 = self.get_bend_size(angle)
        min_dist = bs1 + self.start_straight #compute from min_straight (equals min-straight if not explicitely overruled)
        P1 = self.input_port.position.move_polar_copy(bs1, self.input_port.angle_deg) #start point of connecting line (not necessarily used later on) 
        #above move_polar_copy statement to be checked : should L become min_dist ?
        line = straight_line_from_point_angle(self.line_point, self.angle_out) #reference line going through 'line_point' with angle 'angle_out'
        line2 = straight_line_from_point_angle(self.input_port.position, self.input_port.angle_deg) #line going through 'input_port' with angle 'angle_deg'
        
        if line.is_parallel(line2):
            # parallel or coinciding
            bs1, bs2 = self.get_bend90_size()
            if line == line2:
                pts.append(self.input_port.position)
                if (self.input_port.angle_deg - self.angle_out)%360.0 < 0.1:
                    # same direction: min_straight
                    pts = points_add_polar(pts,max(self.start_straight , self.end_straight), self.angle_out)
                else:
                    # opposite_direction: U-turn
                    pts = points_add_polar(pts,self.start_straight + bs1, self.input_port.angle_deg)
                    pts = points_add_polar(pts,bs1+bs2 + self.min_straight, self.input_port.angle_deg + 90.0)
                    pts = points_add_polar(pts,bs1+bs2 + max(self.min_straight, self.start_straight), self.input_port.angle_deg + 180.0)
                    pts = points_add_polar(pts,bs1+bs2 + self.min_straight, self.input_port.angle_deg + 270.0)
                    pts = points_add_polar(pts,bs2+ self.end_straight, self.angle_out)
            else:
                D = line.distance(self.input_port.position)
                if (self.input_port.angle_deg - self.angle_out)%360.0 < 0.1:
                    # same direction
                    P = RouteToParallelLine(input_port = self.input_port, 
                                            line_point = self.line_point, 
                                            max_s_bend_angle = self.max_s_bend_angle, 
                                            bend_radius = self.bend_radius, 
                                            rounding_algorithm = self.rounding_algorithm,
                                            min_straight = self.min_straight
                                            )
                    P.start_straight = self.start_straight
                    P.end_straight = self.end_straight
                    pts += P
                elif D - (bs1 + bs2+ self.min_straight) >= -0.1/get_grids_per_unit():
                        # sufficient distance
                        pts.append(self.input_port.position)
                        pts = points_add_polar(pts,self.start_straight + bs1, self.input_port.angle_deg)
                        pts.append(line.closest_point(pts[-1]))
                        pts = points_add_polar(pts,self.end_straight+bs2, self.angle_out)
                else:
                        # insufficient distance
                        pts.append(self.input_port.position)
                        pts = points_add_polar(pts,self.start_straight + bs1, self.input_port.angle_deg)
                        A = angle_deg(line.closest_point(self.input_port.position), self.input_port.position)
                        pts = points_add_polar(pts,bs1+bs2+ self.min_straight, A)
                        P2 = Coord2(pts[-1][0], pts[-1][1]).move_polar(bs2+ self.min_straight, self.angle_out)
                        P = RouteToParallelLine(input_port = OpticalPort(position = P2, 
                                                             wg_definition = self.input_port.wg_definition, 
                                                             angle = self.angle_out), 
                                                line_point = self.line_point, 
                                                max_s_bend_angle = self.max_s_bend_angle, 
                                                bend_radius = self.bend_radius, 
                                                min_straight = self.min_straight,
                                                rounding_algorithm = self.rounding_algorithm)
                        P.start_straight = 0.0
                        P.end_straight = self.end_straight
                        pts += P
        else:
            # not parallel
            bs1, bs2 = self.get_bend_size(angle)
            i = line.intersection(line2)
            Di = distance(i, self.input_port.position)
            D = line.distance(self.input_port.position)
            angle_diff = abs((angle_deg(i, self.input_port.position) - self.input_port.angle_deg + 180.0)%360.0 - 180.0)
            if (Di - min_dist)>= 0 and angle_diff < 0.1:
                if self.min_straight >= (Di - min_dist) or self.max_s_bend_angle < abs(angle) <= 90.0:
                    # simple case: just a single bend
                    pts.append(self.input_port.position)
                    pts.append(i)
                    pts = points_add_polar(pts,bs2 + self.end_straight, self.angle_out)

                else:
                    pts.append(self.input_port.position)
                    # extra S-bend to shorten path: difficult
                    # check maximum angle:
                    s = self.min_straight
                    st = self.start_straight
                    R = self.bend_radius
                    a_2 = sign(angle) *self.max_s_bend_angle
                    a_1 = angle-a_2
                    L1_1, L1_2 = self.get_bend_size(a_1)
                    L2_1, L2_2 = self.get_bend_size(a_2)
                    P1 = self.input_port.position.move_polar_copy(st+ L1_1, self.input_port.angle_deg)
                    line3 = straight_line_from_point_angle(P1, self.input_port.angle_deg+a_1)
                    P2 = line.intersection(line3)
                    if distance(P2, P1) < L1_2+L2_1+s:
                        ##a_2 = sign(a_2) * min(abs(a_2), self.max_s_bend_angle)
                        if abs(angle)>= self.max_s_bend_angle:
                            angle_range = [abs(angle)]
                        else:
                            angle_range = arange(self.max_s_bend_angle, abs(angle), -(self.max_s_bend_angle- abs(angle))/30.0)
                                
                            
                        for A in angle_range:
                            a_2 = sign(angle) * A
                            a_1 = angle-a_2
                            L1_1, L1_2 = self.get_bend_size(a_1)
                            L2_1, L2_2 = self.get_bend_size(a_2)
                            P = self.input_port.position.move_polar_copy(st+ L1_1, self.input_port.angle_deg)
                            line3 = straight_line_from_point_angle(P1, self.input_port.angle_deg+a_1)
                            P2 = line.intersection(line3)
                            if distance(P2, P1) >= L1_2+L2_1+s:
                                break
                    pts.extend([P1, P2])
                    pts = points_add_polar(pts,L2_2+self.end_straight, self.angle_out)                                       
            else:
                pts.append(self.input_port.position)
                pts = points_add_polar(pts, self.start_straight + bs1, self.input_port.angle_deg)
                P2 = Coord2(pts[-1][0], pts[-1][1]).move_polar(bs2, self.angle_out)
                P = RouteToParallelLine(input_port = OpticalPort(position = P2, 
                                                          wg_definition = self.input_port.wg_definition,
                                                          angle= self.angle_out), 
                                        line_point = self.line_point, 
                                        max_s_bend_angle = self.max_s_bend_angle, 
                                        bend_radius = self.bend_radius, 
                                        min_straight = self.min_straight,
                                        rounding_algorithm = self.rounding_algorithm,
                                        start_straight = self.min_straight,
                                        end_straight = self.end_straight)
                pts.extend(P)
        return pts
                
        
def RouteToManhattanRelativeToPosition(**kwargs):
    """ route a port to a horizontal pointing east at a coordinate value larger/smaller than or equal to the given position (coordinate is x for EAST/WEST direction, and y for NORTH/SOUTH)
        relation is either '>' or '<' """
    direction = extract_kwarg(kwargs, "direction")
    relation = extract_kwarg(kwargs, "relation")
    position = extract_kwarg(kwargs, "position")
    if not direction in [EAST, WEST, NORTH, SOUTH]:
        raise AttributeError("direction of RouteToManhattanBeyondPosition must be EAST, WEST, NORTH or SOUTH")
    if not relation in ['<', '>']:
        raise AttributeError("relation in RouteToManhattanBeyondPosition must be '<' (smaller than) or '>' (larger than)")
    R = RouteToAngle(angle_out = angle_deg(direction), allow_unmatched_kwargs = True, **kwargs)
    
    if direction in [NORTH, SOUTH]:
        pos_coord = Coord2(position, 0.0)
        out_coord = R.out_ports[0].x
    else:
        pos_coord = Coord2(0, position)
        out_coord = R.out_ports[0].y

    if relation == '<':
        if out_coord <= position: 
            return R
    else:
        if out_coord >= position: 
            return R
    return RouteToLine(line_point = pos_coord, angle_out = angle_deg(direction), **kwargs)
        
class RouteToEastAtY(RouteToLine):
    """ route a port to a horizontal pointing east """
    
    y_position = FloatProperty(required = True)
    line_point = Coord2Property()
    angle_out = 0.0   
    
    def define_line_point(self):
        return (0.0, self.y_position)
    

class RouteToWestAtY(RouteToLine):
    """ route a port to a horizontal pointing west """
    
    y_position = FloatProperty(required = True)
    line_point = Coord2Property()
    angle_out = 180.0   
    
    def define_line_point(self):
        return (0.0, self.y_position)
    

class RouteToNorthAtX(RouteToLine):
    """ route a port to a vertical pointing upward """
    
    x_position = FloatProperty(required = True)
    line_point = Coord2Property()
    angle_out = 90.0   
    
    def define_line_point(self):
        return (self.x_position, 0.0)
    
class RouteToSouthAtX(RouteToLine):
    """ route a port to a vertical pointing downward """
    
    x_position = FloatProperty(required = True)
    line_point = Coord2Property()
    angle_out = -90.0   
    
    def define_line_point(self):
        return (self.x_position, 0.0)    
    

class RouteToHorizontalAtY(RouteToLine):
    """ route a port to the horizontal (west or east, whichever is closest) """
    
    y_position = FloatProperty(required = True)
    line_point = Coord2Property()
    
    def define_line_point(self):
        return (0.0, self.y_position)
    
    def define_angle_out(self):
        a = self.input_port.angle_deg%360.0
        if a<=90 or a>270.0:
            return 0.0
        else:
            return 180.0
        
    

class RouteToVerticalAtX(RouteToLine):
    """ route a port to the vertical (up or down, whichever is closest) """
    
    x_position = FloatProperty(required = True)
    line_point = Coord2Property()
    
    def define_line_point(self):
        return (self.x_position, 0.0)
    
    def define_angle_out(self):
        a = self.input_port.angle_deg%360.0
        if a<180 and a>=0.0:
            return 90.0
        else:
            return -90.0
    
    
   
    
def RouteToEastAtMaxY(**kwargs):
    """ route a port to a horizontal pointing east at a y-value smaller than or equal to y_position """
    y_position = extract_kwarg(kwargs, "y_position")
    R = RouteToEast(allow_unmatched_kwargs = True, **kwargs)
    if R.out_ports[0].y <= y_position:
        return R
    else:
        return RouteToLine(line_point = (0.0, y_position), 
                           angle_out= 0.0, 
                           **kwargs)
    
    
def RouteToWestAtMaxY(**kwargs):
    """ route a port to a horizontal pointing west at a y-value smaller than or equal to y_position """
    y_position = extract_kwarg(kwargs, "y_position")
    R = RouteToWest(allow_unmatched_kwargs = True, **kwargs)
    if R.out_ports[0].y <= y_position:
        return R
    else:
        return RouteToLine(line_point = (0.0, y_position), 
                           angle_out= 180.0, 
                           **kwargs)   
    
    
def RouteToNorthAtMaxX(**kwargs):
    """ route a port to a vertical pointing up at a x-value smaller than or equal to y_position """
    x_position = extract_kwarg(kwargs, "x_position")    
    R = RouteToNorth(allow_unmatched_kwargs = True, **kwargs)
    if R.out_ports[0].x <= x_position:
        return R
    else:
        return RouteToLine(line_point = (x_position, 0.0), 
                           angle_out= 90.0, 
                           **kwargs)    

def RouteToSouthAtMaxX(**kwargs):
    """ route a port to a vertical pointing down at a x-value smaller than or equal to y_position """
    x_position = extract_kwarg(kwargs, "x_position")  
    R = RouteToSouth(allow_unmatched_kwargs = True, **kwargs)
    if R.out_ports[0].x <= x_position:
        return R
    else:
        return RouteToLine(line_point = (x_position, 0.0), 
                           angle_out= -90.0, 
                           **kwargs)    

def RouteToEastAtMinY(**kwargs):
    """ route a port to a horizontal pointing east at a y-value larger than or equal to y_position """
    y_position = extract_kwarg(kwargs, "y_position")
    R = RouteToEast(allow_unmatched_kwargs = True, **kwargs)
    if R.out_ports[0].y >= y_position:
        return R
    else:
        return RouteToLine(line_point = (0.0, y_position), 
                           **kwargs)
    
def RouteToWestAtMinY(**kwargs):
    """ route a port to a horizontal pointing west at a y-value larger than or equal to y_position """
    y_position = extract_kwarg(kwargs, "y_position")  
    R = RouteToWest(allow_unmatched_kwargs = True, **kwargs)
    if R.out_ports[0].y >= y_position:
        return R
    else:
        return RouteToLine(line_point = (0.0, y_position), 
                           angle_out= 180.0, 
                           **kwargs)
    
def RouteToNorthAtMinX(**kwargs):
    """ route a port to a vertical pointing up at a x-value larger than or equal to y_position """
    x_position = extract_kwarg(kwargs, "x_position")  
    R = RouteToNorth(allow_unmatched_kwargs = True, **kwargs)
    if R.out_ports[0].x >= x_position:
        return R
    else:
        return RouteToLine(line_point = (x_position, 0.0), 
                           angle_out=  90.0, 
                           **kwargs)    

def RouteToSouthAtMinX(**kwargs):
    """ route a port to a vertical pointing down at a x-value larger than or equal to y_position """
    x_position = extract_kwarg(kwargs, "x_position")  
    R = RouteToSouth(allow_unmatched_kwargs = True, **kwargs)
    if R.out_ports[0].x >= x_position:
        return R
    else:
        return RouteToLine(line_point = (x_position, 0.0), 
                           angle_out= -90.0, 
                           **kwargs)    
