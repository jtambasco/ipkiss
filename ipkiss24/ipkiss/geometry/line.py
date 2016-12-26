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

from .coord import Coord2
from math import tan, sqrt, atan2
from . import transformable

from ..constants import DEG2RAD, RAD2DEG
import numpy

from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.predefined import NumberProperty
from ipcore.properties.initializer import StrongPropertyInitializer

__all__ = ["StraightLine", "straight_line_from_point_angle", "straight_line_from_slope_intercept", "straight_line_from_two_points", "straight_line_from_vector", "LineProperty"]
class StraightLine(transformable.Transformable, StrongPropertyInitializer):
    """ creates a line ax + by + c = 0 """
    a = NumberProperty(required = True)
    b = NumberProperty(required = True)
    c = NumberProperty(required = True)
    
    def __init__(self, a, b, c, **kwargs):
        super(StraightLine, self).__init__(a=a, b=b, c=c, **kwargs)
        
    
    def get_slope(self):
        if self.b == 0:
            return None
        return -self.a / self.b
    slope = property(get_slope, doc = "gives slope (tangent) of the line""")
    
    def is_on_line(self, coordinate):
        """ returns True if point is on line """
        return abs(self.a * coordinate[0] + self.b * coordinate[1] + self.c) < 1E-10
    
    def get_angle_rad(self):
        return atan2(-self.a, self.b)
    angle_rad = property(get_angle_rad, doc = "gives angle of line (in radians)")
    def get_angle_deg(self):
        return RAD2DEG * self.angle_rad
    angle_deg = property(get_angle_deg, doc = "gives angle of line (in radians)")
    
    def get_y_intercept(self):
        if self.b == 0.0:
            return None
        return -self.c / -self.b
    y_intercept = property(get_y_intercept, doc = "gives y-intercept of line (None if parallel to Y)")
    
    def get_x_intercept(self):
        if self.a == 0.0:
            return None
        return -self.c / -self.a
    x_intercept = property(get_x_intercept, doc = "gives x-intercept of line (None if parallel to X)")
    
    def distance(self, coordinate):
        """ gives distance of point to line """
        return abs(self.a * coordinate[0] + self.b * coordinate[1] + self.c) / sqrt(self.a ** 2 + self.b ** 2)

    def intersection(self, line):
        """ gives intersection of line with other line """
        if (self.b * line.a - self.a * line.b) == 0.0:
            return None
        return Coord2(-(self.b * line.c - line.b * self.c) / (self.b * line.a - self.a * line.b),
                      (self.a * line.c - line.a * self.c) / (self.b * line.a - self.a * line.b))

    def closest_point(self, point):
        """ gives closest point on line """
        line2 = straight_line_from_point_angle(point, self.angle_deg + 90.0)
        return self.intersection(line2)
    
    def is_on_same_side(self, point1, point2):
        """ returns True is both points are on the same side of the line """
        return numpy.sign(self.a * point1[0] + self.b * point1[1] + self.c) == numpy.sign(self.a * point2[0] + self.b * point2[1] + self.c)


    def is_parallel(self, other):
        """ returns True is lines are parallel """
        return abs(self.a * other.b - self.b * other.a) < 1E-10

    def __eq__(self, other):
        return abs(self.a * other.b - self.b * other.a) < 1E-10 and abs(self.c * other.b - self.b * other.c) < 1E-10 and abs(self.a * other.c - self.c * other.a) < 1E-10    
        
    def __ne__(self, other):
        return (not self.__eq__(other))    
    
    def __get_2_points__(self):
        """ returns 2 points on the line. If a horizontal or vertical, it returns one point on the axis, and another 1.0 further.
            If the line is oblique, it returns the intersects with the axes """
        from .shape import Shape
        if b == 0:
            return Shape([Coord2(-self.c / self.a, 0.0), Coord2(-self.c / self.a, 1.0)])
        elif a == 0: 
            return Shape([Coord2(0.0, -self.c / self.b), Coord2(1.0, -self.c / self.b)])
        else:
            return Shape([Coord2(-self.c / self.a, 0.0), Coord2(0.0, -self.c / self.b)])
    
    def transform(self, transformation):
        """ transforms the straight line with a given transformation """
        p = self.__get_2_points__().transform(transformation)
        self.a = y2 - y1
        self.b = x1 - x2
        self.c = (x2 - x1) * y1 - (y2 - y1) * x1
        
    def transform_copy(self, transformation):
        """ transforms a copy of the straight line with a given transformation """
        p = self.__get_2_points__().transform(transformation)
        return straight_line_from_two_points(p[0], p[1])


    

def straight_line_from_slope_intercept(slope, y_intercept):
    """ creates StraightLine object from slope and y_intercept """
    return StraightLine(slope, -1.0, intercept)

def straight_line_from_two_points(point1, point2):
    """ creates StraightLine object from two points """
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    return StraightLine(y2 - y1, x1 - x2, (x2 - x1) * y1 - (y2 - y1) * x1)

def straight_line_from_point_angle(point, angle):
    """ creates StraightLine object from point and angle """
    if abs(angle % 180.0 - 90.0) <= 1E-8:
        return straight_line_from_two_points(point, Coord2(0.0, 1) + point)
    slope = tan(DEG2RAD * angle)
    return StraightLine(slope, -1, point[1] - slope * point[0])

def straight_line_from_vector(vector):
    """ creates StraightLine object from a vector """
    return straight_line_from_point_angle(vector.position, vector.angle_deg)
    
def LineProperty(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    R = RestrictType(StraightLine) & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)
