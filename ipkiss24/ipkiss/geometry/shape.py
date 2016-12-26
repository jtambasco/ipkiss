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
from . import transformable 
from coord import Coord2, Coord3, Coord

from . import size_info
from copy import copy, deepcopy
from numpy import *

from ipcore.properties.descriptor import DefinitionProperty, FunctionProperty, RestrictedProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.predefined import BoolProperty, AngleProperty
from ipcore.properties.initializer import StrongPropertyInitializer, MetaPropertyInitializer

from ipkiss.log import IPKISS_LOG as LOG
from ipcore.mixin.mixin import MixinBowl
from ipkiss.geometry.size_info import SizeInfoProperty

from ipkiss.exceptions.exc import *
import numpy

__all__ = ["PointsDefinitionProperty", "Shape", "ShapeProperty", "points_add_relative", "points_add_polar"]



def convert_coord_to_array(c): #this can be Coord2, a tuple or a list
    return asarray([c[0], c[1]], dtype=numpy.float64)
    
convert_coord_list_to_numpy_array_vectorized = numpy.vectorize(convert_coord_to_array, otypes=[tuple])  


class PointsDefinitionProperty(DefinitionProperty):
    __allowed_keyword_arguments__ = ["required", "restriction", "default", "fdef_name"]
    
                       
    def __call_getter_function__(self, obj):
        f = self.__get_getter_function__(obj)
        value = f([])
        if (value is None):
            value = self.__process__([])
        else:
            value = self.__process__([c.convert_to_array() if isinstance(c, Coord) else c for c in value])
        self.__cache_property_value_on_object__(obj, value)
        return value 
    
    def __process__(self, points):
        if isinstance(points, Shape):
            return array(points.points)
        elif isinstance(points, (list, ndarray)):
            if len(points):
                element = points[0]
                if isinstance(element, (ndarray, list)):
                    points_as_array = array(points, copy=False)
                else:
                    points_as_array = array([(c[0], c[1]) for c in points])
                return points_as_array
            else:
                return ndarray((0, 2))
        elif isinstance(points, Coord2):
                return array([[points.x, points.y]])
        elif isinstance(points, tuple):
                return array([[points[0], points[1]]])
        else:
                raise TypeError("Invalid type of points in setting value of PointsDefinitionProperty: " + str(type(points)))
    
    def __set__(self, obj, points):
        points = self.__process__(points)
        self.__externally_set_property_value_on_object__(obj, points)
            
    
#########################################################
#  Some helper functions to add points to a list
#########################################################
def points_add_relative(pts, coordinate):
    """ add a point with a relative position of the last point """
    if shape(pts) == (2,) and (isinstance(pts[0], int) or isinstance(pts[0], float)):
        pts = [pts]
    pts. append([pts[-1][0] + coordinate[0], pts[-1][1] + coordinate[1]])
    return pts

def points_add_polar(pts, distance, angle=0.0):
    """ add a point with a relative distance and angle from the last point """
    pts = points_add_relative(pts, (distance * cos(constants.DEG2RAD * angle), distance * sin(constants.DEG2RAD * angle)))
    return pts

               

#----------------------------------------------------------------------------
# Basic shape
#----------------------------------------------------------------------------

class Shape(transformable.Transformable, StrongPropertyInitializer, MixinBowl):
    '''Basic shape'''
    points = PointsDefinitionProperty(fdef_name="define_points")     
    start_face_angle = AngleProperty(allow_none=True, doc="Use this to overrule the 'dangling' angle at the start of an open shape")
    end_face_angle = AngleProperty(allow_none=True, doc="Use this to overrule the 'dangling' angle at the end of an open shape")
    

    def __init__(self, points=[], closed=None, **kwargs):
        if not (isinstance(points, Shape) and (closed is None)):
                kwargs["closed"] = closed
        else:
            if (points.closed):
                kwargs["closed"] = True  
                
        if isinstance(points, Shape):
            if not "start_face_angle" in kwargs:
                kwargs["start_face_angle"] = points.start_face_angle
            if not "end_face_angle" in kwargs:
                kwargs["end_face_angle"] = points.end_face_angle

        if (points != None):
            if (isinstance(points, list) or isinstance(points, ndarray) or isinstance(points, Shape) or isinstance(points, tuple)):
                if (len(points) > 0):
                    kwargs["points"] = points
            elif (isinstance(points, Coord2)):
                kwargs["points"] = [points]
            else:
                try:
                    from dependencies.shapely_wrapper import CoordinateSequence
                    if (isinstance(points, CoordinateSequence)):
                        pl = [pt for pt in points]
                        kwargs["points"] = pl
                    else:
                        raise Exception()
                except Exception, e:
                    raise IpkissException("Unexpected type %s for parameter 'points' in Shape::__init__" % str(type(points)))
        super(Shape, self).__init__(**kwargs)
                
    def define_points(self, pts): 
        return pts #to be overridden by subclasses

    def clear(self):
        """ clears all points """
        self.points = ndarray((0, 2))

       
    #########################################################
    #  Is a shape open or closed
    #########################################################
    def close(self):
        """ closes the shape """
        self.set_closed(True)
        
    def open(self):
        """ opens the shape""" 
        self.set_closed(False)
        
    def set_closed(self, value):
        if isinstance(value, bool):
            self.__closed__ = value
        elif value is None:
            self.__closed__ = None
        else:
            raise TypeError("closed attribute of Shape must be True, False or None")
        
    def is_closed(self):
        if len(self.points) == 0:
            return False
        if (not hasattr(self, "__closed__")) or self.__closed__ is None:
            return bool(prod(self.points[-1] == self.points[0]))
        else:
            return self.__closed__
        
    closed = FunctionProperty(is_closed, set_closed)
    """ is the chape closed or not """

    #########################################################
    #  Some speed-functions to add points
    #########################################################
    def add_relative(self, coordinate):
        """ add a point with a relative position of the last point """
        self += Coord2(self.points[-1][0] + coordinate[0], self.points[-1][1] + coordinate[1])
   
    def add_polar(self, distance, angle = 0.0):
        """ add a point with a relative distance and angle from the last point """
        self.add_relative((distance * cos(constants.DEG2RAD * angle), distance * sin(constants.DEG2RAD * angle)))

    #########################################################
    #  Transforms
    #########################################################
    def transform(self, transformation):
        """ applies transformation to the shape points """
        # applies a selected transformation
        self.__make_static__()
        self.points = transformation.apply_to_array(self.points)
        if not self.start_face_angle is None:
            self.start_face_angle = transformation.apply_to_angle_deg(self.start_face_angle)
        if not self.end_face_angle is None:
            self.end_face_angle = transformation.apply_to_angle_deg(self.end_face_angle)        
        return self

    def move(self, position):
        """ moves the shape """
        p = array([position[0], position[1]])
        self.points += p
        return self

    #########################################################
    #  Computations
    #########################################################

    def define_size_info(self):
        si = size_info.size_info_from_numpyarray(self.points)
        return si
    
    size_info = SizeInfoProperty(locked = True)

    def snap_to_grid(self, grids_per_unit = None):
        """ snaps all points to grid """
        from .. import settings
        if grids_per_unit is None:
            grids_per_unit = settings.get_grids_per_unit()
        self.points = (floor(self.points * grids_per_unit + 0.5)) / grids_per_unit 
        return self

    def len_without_identicals(self):
        """ returns the length without identicals """
        pts = self.points
        if (len(pts) > 1):
            identicals = sum(pts != roll(pts, -1, 0), 1)
            if not self.closed:
                identicals[0] = True
            return len(identicals.nonzero()[0])                               
        return len(pts)

    def remove_identicals(self):
        """ removes consecutive identical points """
        # FIXME: in some cases a series of many points close together is removed, even if they form
        # together a valid shape...
        from .. import settings
        pts = self.points
        if len(pts) > 1:
            identicals = prod(abs(pts - roll(self.points, -1, 0)) < 0.5 / settings.get_grids_per_unit(), 1)
            if not self.closed:
                identicals[-1] = False
            self.points = delete(pts, identicals.nonzero()[0], 0)
        return self
    
    def remove_straight_angles(self):
        """ removes points with turn zero or 180 degrees """
        Shape.remove_identicals(self)
        # also removes identicals and 180deg bends
        pts = self.points
        if len(pts) > 1:
            straight = (abs(abs((self.turns_rad() + (0.5 * pi)) % pi) - 0.5 * pi) < 0.00001)  # (self.turns_rad()%pi == 0.0)
            if not self.closed:
                straight[0] = False
                straight[-1] = False
            self.points = delete(pts, straight.nonzero()[0], 0)
        return self

    def remove_loops(self):
        """ removes local loops"""
        from . import shape_info
        pts = self.points
        if len(pts) <= 3:
            return self

        Shape.remove_identicals(self) # avoids recomputation
        # eliminate backloop
        nc = pts
        dels = []
        i = -1
        L = len(nc)
        if self.closed:
            L2 = L + 1
        else:
            L2 = L
        while i < L - 2:
            i += 1
            if i in dels:
                continue
            c1 = nc[i]
            c2 = nc[i + 1]
            k = i + 2
            while k < L2 - 1:

                c3 = nc[k % L]
                c4 = nc[(k + 1) % L]
                if shape_info.lines_cross(c1, c2, c3, c4):
                    nc[i + 1] = shape_info.intersection(c1, c2, c3, c4)
                    dels.append(slice(i + 2, k + 1))
                    c2 = nc[i + 1]
                k += 1 
        for s in reversed(dels):
            self.points = delete(nc, s, 0)
        return self

    def tolist(self):
        """ converts a shpa to a list of Coord2 objects """
        L = [Coord2(c[0], c[1]) for c in self.points]
        if self.closed and L[0] != L[-1]:
            L.append(L[0])
        return L

    #######################################################
    #  Information
    #########################################################
    def distances(self):
        """ returns the distance from each point to each next point """
        pts = self.points
        return sqrt(sum((roll(pts, -1, 0) - pts) ** 2, 1))

    def relative(self):
        """ returns an array with the relative displacement to each point to the next point """
        pts = self.points
        return roll(pts, -1, 0) - pts

    def cos_sin(self):
        """ returns an 2-D array containing the cos and sin of the angle between each point and the next point """
        D = self.distances()
        return self.relative() / column_stack((D, D))

    def length(self):
        """ returns the total length of the shape """
        S = self.distances()
        if self.closed:
            return sum(S)
        else:
            return sum(S) - S[-1]

    def angles_rad(self):
        """ returns the angles (radians) of the connection between each point and the next """
        pts = self.points
        R = roll(pts, -1, 0)
        radians = arctan2(R[:, 1] - pts[:, 1], R[:, 0] - pts[:, 0])
        return radians

    def angles_deg(self):
        """ returns the angles (degrees) of the connection between each point and the next """
        return self.angles_rad() * constants.RAD2DEG


    def turns_rad(self):
        """ returns the angles (radians) of the turn in each point """
        a = self.angles_rad()
        return (a - roll(a, 1, 0) + pi) % (2 * pi) - pi

    def turns_deg(self):
        """ returns the angles (degrees) of the turn in each point """
        return self.turns_rad() * constants.RAD2DEG

    def area(self):
        """ returns the area of the shape """
        pts = self.points
        T = roll(roll(pts, 1, 1), 1, 0)
        return sum(abs(diff(pts * T, 1, 1))) * 0.5

    def orientation(self):
        """ returns the orientation of the shape: +1(counterclock) or -1(clock) """
        pts = self.points
        T = roll(roll(pts, 1, 1), 1, 0)
        return -sign(sum(diff(pts * T, 1, 1)))

    def winding_number_test(self, point, inclusive = False):
        """ Returns the number of times a polygon winds around a point.
                    point can be a single point, an array or list of points or a shape. 
                    For a single point, a number is returned. For a shape or a list of points,
                    an array of values is returned.
                    inclusive=True denotes inclusion of points on the shape"""
        ## uses the winding number algorithm
        ## http://www.geometryalgorithms.com/Archive/algorithm_0103/algorithm_0103.htm#wn_PinPolygon()
        from . import shape_info
        wn = 0    # the winding number counter
        ## loop through all edges of the polygon
        S = Shape(point) # convert input to uniform data format shape
        P = S.points
        N = len(self.points)
        pts = self.points
        V0 = pts # starting points of edges
        V1 = roll(V0, -1, 0) # end points of edges

        wn = zeros(size(P, 0))
        for i in range(N): 
            v_sign0 = ((V0[i, 1] <= P[:, 1]) * 2 - 1) # positive if V0 is below P
            v_sign1 = ((V1[i, 1] > P[:, 1]) * 2 - 1)  # positive if V1 is above P
            if inclusive:
                wn += (v_sign0 == v_sign1) * numpy.sign(shape_info.is_west(P, V0[i], V1[i]) - 0.1)
            else:
                wn += (v_sign0 == v_sign1) * shape_info.is_west(P, V0[i], V1[i])
        if len(wn) == 1:
            return wn[0] / 2
        return wn / 2


    def convex_hull(self):
        link = lambda a, b: concatenate((a, b[1:]))
        def dome(sample, base): 
            edge = lambda a, b: concatenate(([a], [b]))

            h, t = base


            dists = dot(sample - h, dot(((0, -1), (1, 0)), (t - h)))
            outer = repeat(sample, dists > 0, axis=0)

            if len(outer):
                pivot = sample[argmax(dists)]
                return link(dome(outer, edge(h, pivot)),
                            dome(outer, edge(pivot, t)))
            else:
                return base


        if len(self.points) > 2:
            axis = self.points[:, 0]
            base = take(self.points, [argmin(axis), argmax(axis)], axis = 0)
            return Shape(link(dome(self.points, base),
                              dome(self.points, base[::-1])), closed = True)
        else:
            return Shape(self.points)

    def encloses(self, point, inclusive = False):
        """ tests whether a point lies in the shape (closed) """
        if not self.size_info.encloses(point, inclusive): return False
        return (self.winding_number_test(point, inclusive) != 0)

    def x_coords(self):
        """ returns the x coordinates """
        return self.points[:, 0]
    def y_coords(self):
        """ returns the y coordinates """
        return self.points[:, 1]

    def cut_in_two(self, index1, index2):
        """ cuts the shape in two using the diagonal through points at index 1 and index 2
                    there is NO test wether this is a valid cut resulting in valid shapes.
                    It resturns a list with 2 CLOSED shapes """
        mini = min([index1, index2])
        maxi = max([index1, index2])
        pts = self.points
        l = len(pts)

        if mini == maxi or maxi - mini == 1:
            return [Shape(pts)]
        S1 = Shape(pts[mini: maxi + 1], True)
        S2 = Shape(roll(pts, -maxi, 0)[0:(l - maxi + mini + 1)])
        return [S1, S2]

    def is_empty(self):
        return self.len_without_identicals() <= 1

    def center_of_mass(self):
        COM = mean(self.points, 0)
        return Coord2(COM[0], COM[1]) 

    def segments(self):
        """ returns a list of point pairs with the segments of the shape """
        p = self.points # computes the shape
        if len(p) < 2:
            return []
        if self.is_closed():
            segments = zip(p, roll(p, 1, 0))
        else:
            segments = zip(p[:-1], p[1:])
        return segments

    def intersections(self, other_shape):
        """ the intersections with this shape and the other shape """
        from shape_info import intersection, lines_cross, lines_coincide, sort_points_on_line, points_unique
        s = Shape(self)
        s.remove_straight_angles()
        segments1 = s.segments() 
        if len(segments1) < 1:
            return []

        s = Shape(other_shape)
        s.remove_straight_angles()
        segments2 = s.segments() 
        if len(segments2) < 1:
            return []

        intersections = []
        for s1 in segments1:
            for s2 in segments2:
                if lines_cross(s1[0], s1[1], s2[0], s2[1], inclusive = True):
                    intersections += [intersection(s1[0], s1[1], s2[0], s2[1])]
                elif lines_coincide(s1[0], s1[1], s2[0], s2[1]):
                    pl = sort_points_on_line([s1[0], s1[1], s2[0], s2[1]])
                    intersections += [pl[1], pl[2]]  # the two middlemost points 
        intersections = points_unique(intersections)
        return Shape(intersections)

    def define_size_info(self):
            si = size_info.size_info_from_numpyarray(self.points)    
            return si
        
    size_info = SizeInfoProperty(locked = True)

    #########################################################
    #  List-type behaviour
    #########################################################
    def __add__(self, pointlist):
        """ creates copy of shape with points added """
        if len(self.points) == 0:
            points = pointlist        
        else:
            if isinstance(pointlist, Shape):
                points = append(self.points, pointlist.points, 0)
            elif isinstance(pointlist, list):
                points = append(self.points, pointlist, 0)                
            elif isinstance(pointlist, ndarray):
                if len(pointlist.shape) == 2 and (pointlist.shape[1] == 2):
                    points = append(self.points, pointlist, 0)
                elif len(pointlist.shape) == 1 and (pointlist.shape[0] == 2):  #individual point
                    points = append(self.points, [(pointlist[0], pointlist[1])], 0)
            elif isinstance(pointlist, (Coord2, tuple)): # indiviual points
                points = append(self.points, [(pointlist[0], pointlist[1])], 0)
            else:
                raise TypeError("Wrong type " + str(type(pointlist)) + " to add to Shape")
        return Shape(points, self.closed)

    def __iadd__(self, pointlist):
        """ adds points to this shape """
        if len(self.points) == 0:
            self.points = pointlist
        elif (not isinstance(pointlist, (Coord2, tuple)) and (len(pointlist) == 0)):
            return self
        else:
            if isinstance(pointlist, Shape):
                self.points = append(self.points, pointlist.points, 0)
                self.end_face_angle = pointlist.end_face_angle
            elif isinstance(pointlist, (list)):
                for p in pointlist: 
                    self += p
            elif isinstance(pointlist, (ndarray)):
                self.points = append(self.points, pointlist, 0)
            elif isinstance(pointlist, (Coord2, tuple)): # indiviual points
                self.points = append(self.points, array([(pointlist[0], pointlist[1])]), 0)
            else:
                raise TypeError("Wrong type " + str(type(pointlist)) + " to add to Shape")
        return self

    def __len__(self):
        """ number of points in the shape """
        return size(self.points, 0)

    def __getitem__(self, index):
        """ access a point """
        p = self.points[index]
        return Coord2(p[0], p[1])

    def __setitem__(self, index, value):
        """ sets a point """
        self.points[index] = [value[0], value[1]]

    def __delitem__(self, point):
        """ removes a point """
        i = self.index(point)
        self.points = delete(self.points, i, 0)
        return self

    def __getslice__(self, i, j):
        """ gets a slice of points """
        return Shape(self.points.__getslice__(i, j))

    def __setslice__(self, i, j, pointlist):
        """ set a slice of points """
        if isinstance(pointlist, Shape):
            points = pointlist.points
        else:
            points = pointlist
        self.points = row_stack((self.points[:i], points, self.points[j:]))

    def __delslice__(self, i, j):
        """ remove a slice of points """
        self.points = delete(self.points, range(i, j), 0)
        return self

    def __mul__(self, times):
        """ makes a shape with the pointlist repeated """
        points = repeat(self.points, times, 0)
        return Shape(points, self.closed)

    def __imul__(self, times):
        """ concatenates the shape e few times to itself """
        self.points = repeat(self.points, times, 0)
        return self
    
    def __iter__(self):
        """ returns an iterator over the coordinates """
        for c in self.points:
            yield Coord2(c[0], c[1])

    def append(self, point):
        """ appends points """
        if isinstance(point, (Coord2, tuple)): # indiviual points
            point_arr = [(point[0], point[1])]
            if len(self.points) > 0:
                self.points = vstack((self.points, point_arr))
            else:
                self.points = array(point_arr)
        else:
            raise TypeError("Wrong type " + str(type(point)) + " to append to Shape")
        return self

    def extend(self, pointlist):
        """ adds a list of points """
        if (len(self.points) == 0):
            self.points = pointlist
        else:
            if isinstance(pointlist, Shape):            
                self.points = vstack((self.points, pointlist.points))
            elif isinstance(pointlist, (list, ndarray)):
                self.points = vstack((self.points, pointlist))
            else:
                raise TypeError("Wrong type " + str(type(pointlist)) + " to extend Shape with")
        return self

    def insert(self, i, item):
        """ inserts a list of points """
        if isinstance(item, Shape):
            self.points = insert(self.points, i, item.points, 0)
        elif isinstance(item, (list, ndarray)):
            self.points = insert(self.points, i, item, 0)
        elif isinstance(item, (Coord2, tuple)): # indiviual points
            self.points = insert(self.points, i, [(item[0], item[1])], 0)
        else:
            raise TypeError("Wrong type " + str(type(item)) + " to extend Shape with")
        return self

    def __contains__(self, point):
        """ checks if point is on the shape """
        return prod(sum(self.points == array(point[0], point[1]), 0))

    def __rmul__(self, number):
        """ repeats the pointlist of the shape a number of times """
        return __mul__(self, number)

    def count(self):
        """ number of points in the shape """
        return self.__len__()

    def index(self, item):
        """ get the index of a specific point """
        i = prod(self.points == array([item[0], item[1]]), 1).nonzero()[0]
        if len(i) == 0:
            raise IndexError("Coordinate (", + str(item[0]) + "," + str(item[1]) + ") cannot be found in shape")
        return i[0]

    def reverse(self):
        """ reverses the order of the shape """
        self.points = flipud(self.points)
        sfa, efa = self.start_face_angle, self.end_face_angle
        if not sfa is None: self.end_face_angle = sfa
        if not efa is None: self.start_face_angle = efa
        return self

    def reversed(self):
        """ returns shape with reversed order """
        return self.modified_copy(points = flipud(self.points), 
                     start_face_angle = self.end_face_angle, 
                     end_face_angle = self.start_face_angle
                     )
        #return Shape(flipud(self.points), 
                     #start_face_angle = self.end_face_angle, 
                     #end_face_angle = self.start_face_angle, 
                     #closed = self.closed)

    def __str__(self):
        """ string representation """
        L = ["Shape ["]
        L += [("(%d,%d)" % (c[0] * 1000, c[1] * 1000)) for c in self.points]
        L += ["]"]
        return "".join(L)

    def id_string(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Shape):
            return False
        myPoints = self.remove_identicals().points
        otherPoints = other.remove_identicals().points
        if not array([myP == otherP for myP, otherP in zip(myPoints, otherPoints)]).all():
            return False
        else:
            return True
    
    def __ne__(self, other):
        return not self.__eq__(other)   
 
    def __deepcopy__(self, memo): #FIXME: this should be removed (fallback on __deepcopy__ from initializer.py, but for some reason this gives wrong results in test_ipkiss.test_ipkiss_examples (logo's)... so we leave it for now   
        return Shape(points = deepcopy(self.points), 
                     closed = self.closed,
                     start_face_angle = self.start_face_angle,
                     end_face_angle = self.end_face_angle)
    
    
# empty shape for quick reference
EMPTY_SHAPE = Shape()


def ShapeProperty(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    R = RestrictType(Shape) & restriction
    P = ProcessorTypeCast(Shape) + preprocess
    return RestrictedProperty(internal_member_name, restriction=R, preprocess=P, **kwargs)


