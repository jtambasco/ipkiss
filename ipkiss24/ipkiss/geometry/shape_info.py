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

from .. import constants
from . import coord
from . import shape
from transforms.rotation import Rotation
import numpy
from math import atan2, pi, sqrt
from ipkiss.log import IPKISS_LOG as LOG


__all__ = ["shape_point_east",
           "shape_point_at_angle",
           "shape_point_between_angles",
           "shape_south",
           "shape_south_west",
           "shape_south_east",
           "shape_bounding_box",
           "shape_box",
           "shape_box_center",
           "shape_west",
           "shape_length",
           "shape_orientation",
           "shape_east",
           "shape_size",
           "shape_north",
           "shape_north_west",
           "shape_north_east",
           "shape_xcoords",
           "shape_ycoords",
           "angle_deg",
           "angle_rad",
           "distance",
           "lines_cross",
           "lines_parallel",
           "lines_coincide",
           "intersection",
           "turn_deg",
           "turn_rad",
           "is_west",
           "midpoint",
           "sort_points_on_line",
           "point_in_triangle"]
           

#----------------------------------------------------------------------------
#shape information
#----------------------------------------------------------------------------

def shape_xcoords(shape):
        """ returns the x coordinates of a shape """
        return shape.points[:, 0].tolist()
                
def shape_ycoords(shape):
        """ returns the y coordinates of a shape """
        return shape.points[:, 1].tolist()

def shape_north(shape):
        """ returns the north Y of the shape """
        return numpy.max(shape.points[:, 1])

def shape_south(shape):
        """ returns the south Y of the shape """
        return numpy.min(shape.points[:, 1])

def shape_west(shape):
        """ returns the west X of the shape """
        return numpy.min(shape.points[:, 0])

def shape_east(shape):
        """ returns the east X of the shape """
        return numpy.max(shape.points[:, 0])

def shape_size(shape):
        """ returns the size of the shape """
        LB = numpy.min(shape.points, 0)
        TR = numpy.max(shape.points, 0)
        return (TR[0] - LB[0], TR[1] - LB[1])

def shape_south_west(shape):
        """ returns the south west coordinate of the shape """
        LB = numpy.min(shape.points, 0)
        TR = numpy.max(shape.points, 0)
        return coord.Coord2(LB[0], LB[1])

def shape_north_east(shape):
        """ returns the north east coordinate of the shape """
        TR = numpy.max(shape.points, 0)
        return coord.Coord2(TR[0], TR[1])

def shape_south_east(shape):
        """ returns the south east coordinate of the shape """
        LB = numpy.min(shape.points, 0)
        TR = numpy.max(shape.points, 0)
        return coord.Coord2(TR[0], LB[1])

def shape_north_west(shape):
        """ returns the north west coordinate of the shape """
        LB = numpy.min(shape.points, 0)
        TR = numpy.max(shape.points, 0)
        return coord.Coord2(LB[0], TR[1])

def shape_point_east(shape):
        points = shape.points
        max_x_point = None
        for point in points:
                if max_x_point is not None:
                        if point[0] > max_x_point[0]:
                                max_x_point = point
                else: 
                        max_x_point = point
        return coord.Coord2(max_x_point)

def shape_point_at_angle(shape, angle):
        s = shape.rotate_copy((0.0, 0.0), -angle)
        max_point = shape_point_east(s)
        return max_point.transform_copy(transformation = Rotation(rotation=angle))

def shape_point_between_angles(shape, angle_begin, angle_end, angle_res=0.01):
        max_point = shape_point_at_angle(shape, angle_begin)
        for angle in numpy.arange(angle_begin, angle_end, angle_res):
                point = shape_point_at_angle(shape, angle)
                if point.__abs__ > max_point.__abs__:
                        max_point = point
        return max_point

def shape_box_center(shape):
        """ returns the center coordinate of the shape """
        LB = numpy.min(shape.points, 0)
        TR = numpy.max(shape.points, 0)
        return coord.Coord2(0.5 * (LB[0] + TR[0]), 0.5 * (LB[0] + TR[1]))

def shape_box(shape):
        """ returns the (south_west , north_east) coordinates of the shape """
        if len(shape) == 0:
                return shape.Shape([(0.0, 0.0), (0.0, 0.0)])
        else:
                LB = numpy.min(shape.points, 0)
                TR = numpy.max(shape.points, 0)
                return shape.Shape([(LB[0], LB[1]), (TR[0], TR[1])], True)

def shape_bounding_box(coordinates):
        """ returns a rectangle shape enclosing the shape"""
        if len(shape) == 0:
                return shape.Shape([(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)], True)
        else:
                LB = numpy.min(shape.points, 0)
                TR = numpy.max(shape.points, 0)
                return shape.Shape([(LB[0], LB[1]), (LB[0], TR[1]), (TR[0], TR[1]), (TR[0], LB[1])], True)

def shape_orientation(coordinates):
        """ returns true for clockwise orientation """
        #returns True if the coordinates are clockwise or False if not
        turn = 0.0
        L = len(coordinates)
        if coordinates[0] == coordinates[-1]:
                L -= 1
        for i in range(L):
                angle1 = atan2(coordinates[i][1] - coordinates[(i - 1) % L][1], coordinates[i][0] - coordinates[(i - 1) % L][0])
                angle2 = atan2(coordinates[(i + 1) % L][1] - coordinates[i][1], coordinates[(i + 1) % L][0] - coordinates[i][0])
                turn += ((angle2 - angle1 + pi) % (2 * pi)) - pi
        return turn < 0
        

def distance(coord, origin = (0.0, 0.0)):
        """ distance of coordinate to origin """
        return sqrt((coord[0] - origin[0]) ** 2 + (coord[1] - origin[1]) ** 2)

def angle_rad(coord, origin = (0.0, 0.0)):
        """ absolute angle (radians) of coordinate with respect to origin"""
        return atan2(coord[1] - origin[1], coord[0] - origin[0])

def angle_deg(coord, origin = (0.0, 0.0)):
        """ absolute angle (radians) of coordinate with respect to origin"""
        return angle_rad(coord, origin) * constants.RAD2DEG

def turn_rad(coord1, Coord2, coord3):
        """ turn angle in coord 2 """
        angle1 = angle_rad(Coord2, coord1)
        angle2 = angle_rad(coord3, Coord2)
        return (angle2 - angle1 + pi) % (2 * pi) - pi

def turn_deg(coord1, Coord2, coord3):
        """ turn angle in coord 2 """
        return turn_rad(coord1, Coord2, coord3) * constants.RAD2DEG


def is_west(point, line_point1, line_point2):
        """ checks if point lies to the west (>0), the east (<0) or on (=0) of the line defined by line_point1 and 2 
        point can be a single point or a numpy array"""
        S = shape.Shape(point)
        P1 = numpy.array([line_point1[0], line_point1[1]])
        P2 = numpy.array([line_point2[0], line_point2[1]])
        R = numpy.sign(numpy.diff((S.points - P1) * numpy.flipud(P2 - P1), 1, 1))
        if len(R) == 1: 
                return R[0]
        else:
                return R
        
                #return ( (line_point2[0] - line_point1[0]) * (point[1]- line_point1[1])
                         #- (point[0] - line_point1[0]) * (line_point2[1] - line_point1[1]) )


def lines_cross(begin1, end1, begin2, end2, inclusive = False):
        """ returns true if the line segments intersect """
        # check if line ends between points cross
        # rechte = Ax + By - C = 0
        A1 = end1[1] - begin1[1]
        B1 = -end1[0] + begin1[0]
        C1 = - (begin1[1] * B1 + begin1[0] * A1)

        A2 = end2[1] - begin2[1]
        B2 = -end2[0] + begin2[0]
        C2 = - (begin2[1] * B2 + begin2[0] * A2)

        if A1 * B2 == A2 * B1:  #parallel
                return False

        if inclusive:
                return ((A1 * begin2[0] + B1 * begin2[1] + C1) * (A1 * end2[0] + B1 * end2[1] + C1) <= 0 and
                        (A2 * begin1[0] + B2 * begin1[1] + C2) * (A2 * end1[0] + B2 * end1[1] + C2) <= 0)
        else:
                return ((A1 * begin2[0] + B1 * begin2[1] + C1) * (A1 * end2[0] + B1 * end2[1] + C1) < 0 and
                        (A2 * begin1[0] + B2 * begin1[1] + C2) * (A2 * end1[0] + B2 * end1[1] + C2) < 0)

def lines_parallel(begin1, end1, begin2, end2):
        """ returns true if the line segments intersect """
        # check if line ends between points cross
        # rechte = Ax + By - C = 0
        A1 = end1[1] - begin1[1]
        B1 = -end1[0] + begin1[0]
        C1 = - (begin1[1] * B1 + begin1[0] * A1)

        A2 = end2[1] - begin2[1]
        B2 = -end2[0] + begin2[0]
        C2 = - (begin2[1] * B2 + begin2[0] * A2)

        return A1 * B2 == A2 * B1

def lines_coincide(begin1, end1, begin2, end2):
        """ returns true if the line segments intersect """
        # check if line ends between points cross
        # rechte = Ax + By - C = 0
        A1 = end1[1] - begin1[1]
        B1 = -end1[0] + begin1[0]
        C1 = - (begin1[1] * B1 + begin1[0] * A1)

        A2 = end2[1] - begin2[1]
        B2 = -end2[0] + begin2[0]
        C2 = - (begin2[1] * B2 + begin2[0] * A2)

        if (not(A1 or B1)) or (not(A2 or B2)):
                return False # one segment consists of 2 identical points
        
        return abs(A1 * B2 - A2 * B1) < 1E-10 and abs(C1 * A2 - C2 * A1) < 1E-10 and abs(C1 * B2 - C2 * B1) < 1E-10
        
def intersection(begin1, end1, begin2, end2):
        """ gives the intersection between two lines (not sections) """
        # compute the intersection of 2 lines through points
        # rechte = Ax + By  = C
        A1 = end1[1] - begin1[1]
        B1 = -end1[0] + begin1[0]
        C1 = begin1[1] * B1 + begin1[0] * A1

        A2 = end2[1] - begin2[1]
        B2 = -end2[0] + begin2[0]
        C2 = begin2[1] * B2 + begin2[0] * A2

        # check if lines aren't parallel
        if A1 * B2 == A2 * B1:
                LOG.error("Can't intersect parallel lines")
                raise SystemExit

        x = (C1 * B2 - C2 * B1) / (A1 * B2 - A2 * B1)
        y = (C1 * A2 - C2 * A1) / (B1 * A2 - B2 * A1)
        return coord.Coord2(x, y)

def midpoint(P1, P2, ratio=0.5):
        return ratio * coord.Coord2(P1[0], P1[1]) + (1 - ratio) * coord.Coord2(P2[0], P2[1])

def sort_points_on_line(point_list):
        """ sorts points on a line, taking the two first points as the reference direction """
        point_list = [coord.Coord2(p[0], p[1]) for p in point_list]
        p0 = point_list[0]
        
        dx, dy = point_list[1][0] - p0[0], point_list[1][1] - p0[1]
        if dx == 0.0:
                point_list.sort(key = lambda p: p[1])
        else:
                point_list.sort(key = lambda p: p[0])
                
        return point_list
        

def point_in_triangle(P, P1, P2, P3):
        """ returns true if point P is in the triangle (P1,P2,P3) """
        # for speed
        x, y = P[0], P[1]
        x1, y1 = P1[0], P1[1] 
        x2, y2 = P2[0], P3[1] 
        x3, y3 = P3[0], P3[1] 
        f12 = (y - y1) * (x2 - x1) - (x - x1) * (y2 - y1)
        f31 = (y - y3) * (x1 - x3) - (x - x3) * (y1 - y3)
        f23 = (y - y2) * (x3 - x2) - (x - x2) * (y3 - y2)
        return (f12 * f23) > 0 and (f23 * f31) > 0


def shape_length(coordinates):
        """ length of a shape """
        #returns the length of a shape
        L = 0
        last_c = coordinates[0]
        for c in coordinates[1:]:
                L += distance(c, last_c)
                last_c = c
        return L

def points_unique(coordinates):
        unique_coordinates = []
        for c in coordinates:
                already_in_list = False
                for uc in unique_coordinates:
                        if c == uc:
                                already_in_list = True
                if not already_in_list:
                        unique_coordinates.append(c)
        return unique_coordinates

                                


