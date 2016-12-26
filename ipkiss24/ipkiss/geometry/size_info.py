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

from ipcore.all import *
from .. import constants
from . import transformable
from . import coord
import numpy 

#----------------------------------------------------------------------------
# SizeInfo class
#----------------------------------------------------------------------------

__all__ = ["SizeInfo", "SizeInfoProperty", 
           "EMPTY_SIZE_INFO",
           "size_info",
           "size_info_from_coord",
           "size_info_from_numpyarray",
           "size_info_from_point_list"]


class SizeInfo(transformable.Transformable):

    """ object which describes the bounding box of a shape, element or structure """
    def __init__(self, west=None, east=None, north=None, south=None):
        self.__west = west
        self.__east = east
        self.__north = north
        self.__south = south

    def __is_initialized__(self):
        """ checks whether the internal data makes sense """
        return not ((self.__west is None) or
                    (self.__east is None) or
                    (self.__north is None)or
                    (self.__south is None))

    # internal properties
    def get_west(self): return self.__west
    def set_west(self, value):
        self.__west = value
        if not self.__east is None:
            self.__east = max(self.__west, self.__east)
    west = property(get_west, set_west)
    """ westmost x-coordinate """

    def get_east(self): return self.__east
    def set_east(self, value):
        self.__east = value
        if not self.__west is None:
            self.__west = min(self.__west, self.__east)
    east = property(get_east, set_east)
    """ eastmost x coordinate """

    def get_north(self): return self.__north
    def set_north(self, value):
        self.__north = value
        if not self.__south is None:
            self.__south = min(self.__north, self.__south)
    north = property(get_north, set_north)
    """ highest y coordinate """

    def get_south(self): return self.__south
    def set_south(self, value):
        self.__south = value
        if not self.__north is None:
            self.__north = max(self.__north, self.__south)
    south = property(get_south, set_south)
    """ lowest y coordinate """

    # virtual properties
    def get_center(self):
        if not self.__is_initialized__(): return None
        return coord.Coord2(0.5 * (self.__west + self.__east), 0.5 * (self.__south + self.__north))
    def set_center(self, value):
        # change center but keep height and width
        if self.__is_initialized__():
            wo2 = 0.5 * (self.__east - self.__west)
            self.__west = value[0] - wo2
            self.__east = value[0] + wo2
            ho2 = 0.5 * (self.__north - self.__south)
            self.__north = value[1] + ho2
            self.__south = value[1] - ho2
        else:
            self.__west = value[0]
            self.__east = value[0]
            self.__north = value[1]
            self.__south = value[1]
    center = property(get_center, set_center)
    """ center coordinate """

    # virtual properties
    def get_size(self):
        if not self.__is_initialized__(): return (0.0, 0.0)
        return coord.Coord2(self.__east - self.__west, self.__north - self.__south)
    def set_size(self, value):
        # change width and height but keep the center
        if self.__is_initialized__():
            cw = 0.5 * (value[0] - self.__east + self.__west)
            self.__west -= cw
            self.__east += cw
            ch = 0.5 * (value[1] - self.__north + self.__south)
            self.__south -= ch
            self.__north += ch
    size = property(get_size, set_size)
    """ size: (width, height)"""

    def get_width(self):
        if not self.__is_initialized__(): return 0.0
        return self.__east - self.__west
    def set_width(self, value):
        # change width but keep center
        if self.__is_initialized__():
            cw = 0.5 * (value - self.__east + self.__west)
            self.__west -= cw
            self.__east += cw
    width = property(get_width, set_width)
    """ width """

    def get_height(self):
        if not self.__is_initialized__(): return 0.0
        return self.__north - self.__south
    def set_height(self, value):
        # change height but keep center
        if self.__is_initialized__():
            ch = 0.5 * (value - self.__north + self.__south)
            self.__south -= ch
            self.__north += ch
    height = property(get_height, set_height)
    """ height """

    # read-only properties
    def get_north_west(self): return (self.__west, self.__north)
    north_west = property(get_north_west)
    """ north_west coordinate """
    def get_north_east(self): return (self.__east, self.__north)
    north_east = property(get_north_east)
    """ north east coordinate """
    def get_south_west(self): return (self.__west, self.__south)
    south_west = property(get_south_west)
    """ south west coordinate """

    def get_south_east(self): return (self.__east, self.__south)
    south_east = property(get_south_east)
    """ south east coordinate """

    def get_border_on_one_side(self, side):
        from ..constants import NORTH, SOUTH, EAST, WEST
        if side == NORTH: 
            return self.north
        elif side == SOUTH:
            return self.south
        elif side == EAST:
            return self.east
        elif side == WEST:
            return self.west
        else:
            raise AttributeError("side in size_info.get_border_on_one_side() should be EAST, WEST NORTH or SOUTH")


    def get_box(self):
        if not self.__is_initialized__(): return None
        from . import shape
        return shape.Shape([(self.__west, self.__south), (self.__east, self.__north)])
    box = property(get_box)
    """ box: Shape(south_west, north_east) """

    def __bounding_box_array__(self):
        """ numpy array with the corner point of the enclosing rectangle """
        if not self.__is_initialized__(): return None
        return  numpy.array([(self.__west, self.__south),
                             (self.__east, self.__south),
                             (self.__east, self.__north),
                             (self.__west, self.__north)])

    def get_bounding_box(self):
        if not self.__is_initialized__(): return None
        from . import shape
        return  shape.Shape([(self.__west, self.__south),
                             (self.__east, self.__south),
                             (self.__east, self.__north),
                             (self.__west, self.__north)], True)
    bounding_box = property(get_bounding_box)
    """ shape with enclosing rectangle """

    def get_area(self):
        return self.width * self.height
    area = property(get_area)

    # check interaction with other objects
    def __contains__(self, other):
        """ checks whether point(s) is in bounding box """
        return self.encloses(other, inclusive = True)

    def encloses(self, other, inclusive = False):
        """ checks whether point is in bounding box """
        from . import shape
        if not self.__is_initialized__(): return False
        if inclusive:
            if isinstance(other, (tuple, coord.Coord2)):
                return (other[0] <= self.__east) and (other[0] >= self.__west) and (other[1] <= self.__north) and (other[1] >= self.__south)
            elif isinstance(other, shape.Shape):
                for c in other:
                    if not self.encloses(c, inclusive): return False
                return True
            elif isinstance(other, SizeInfo):
                return (other.__east <= self.__east) and (other.__west >= self.__west) and (other.__north <= self.__north) and (other.__south >= self.__south)
            else:
                raise TypeError("Unsupported type " + str(type(other)) + " in SizeInfo.encloses()")
        else:
            if isinstance(other, (tuple, coord.Coord2)):
                return (other[0] < self.__east) and (other[0] > self.__west) and (other[1] < self.__north) and (other[1] > self.__south)
            elif isinstance(other, shape.Shape):
                for c in other:
                    if not self.encloses(c, inclusive): return False
                return True
            elif isinstance(other, SizeInfo):
                return (other.__east < self.__east) and (other.__west > self.__west) and (other.__north < self.__north) and (other.__south > self.__south)
            else:
                raise TypeError("Unsupported type " + str(type(other)) + " in SizeInfo.encloses()")


    def snap_to_grid(self, grids_per_unit = None):
        """ snaps the size_info object to the grid """
        if not self.__is_initialized__(): return self
        if grids_per_unit is None: grids_per_unit = constants.get_grids_per_unit()
        self.__west = constants.snap_value(self.__west, grids_per_unit)
        self.__east = constants.snap_value(self.__east, grids_per_unit)
        self.__north = constants.snap_value(self.__north, grids_per_unit)
        self.__south = constants.snap_value(self.__south, grids_per_unit)
        return self

    def expand_to_grid(self, grids_per_unit = None):
        """ expands the size_info object to the grid """
        if not self.__is_initialized__(): return self
        if grids_per_unit is None: grids_per_unit = constants.get_grids_per_unit()
        self.__west = floor(self.__west * grids_per_unit) / grids_per_unit
        self.__east = ceil(self.__east * grids_per_unit) / grids_per_unit
        self.__north = ceil(self.__north * grids_per_unit) / grids_per_unit
        self.__south = floor(self.__south * grids_per_unit) / grids_per_unit
        return self

    # combine with another size_info object
    def __add__(self, other):
        """ gives the sizeinfo of the box enclosing the union of both boxes """
        if self.__is_initialized__() and other.__is_initialized__():
            west = min(self.__west, other.__west)
            east = max(self.__east, other.__east)
            south = min(self.__south, other.__south)
            north = max(self.__north, other.__north)
        elif other.__is_initialized__():
            west = other.__west
            east = other.__east
            south = other.__south
            north = other.__north
        elif self.__is_initialized__():
            west = self.__west
            east = self.__east
            south = self.__south
            north = self.__north
        else:        
            west, east, north, south = None, None, None, None

        return SizeInfo(west, east, north, south)

    def __iadd__(self, other):
        """ expands the sizeinfo to include the other box """
        if self.__is_initialized__() and other.__is_initialized__():
            self.__west = min(self.__west, other.__west)
            self.__east = max(self.__east, other.__east)
            self.__south = min(self.__south, other.__south)
            self.__north = max(self.__north, other.__north)
        elif other.__is_initialized__():
            self.__west = other.__west
            self.__east = other.__east
            self.__south = other.__south
            self.__north = other.__north
        return self

    def move(self, coordinate):
        """ translates the center """
        if self.__is_initialized__():
            self.west += coordinate[0]
            self.east += coordinate[0]
            self.north += coordinate[1]
            self.south += coordinate[1]
        else:
            self.west, self.east, self.north, self.south = None, None, None, None
        return self

    def move_copy(self, coordinate):
        """ creates a copy of this sizeinfo and moves it """
        if self.__is_initialized__():
            west = self.__west + coordinate[0]
            east = self.__east + coordinate[0]
            north = self.__north + coordinate[1]
            south = self.__south + coordinate[1]
        else:
            west, east, north, south = None, None, None, None
        return SizeInfo(west, east, north, south)

    # apply a transformation        
    def transform(self, transformation):
        """ transforms the size_info box and makes a new cartesian box over it """
        if self.__is_initialized__():
            BB = transformation.apply_to_array(self.__bounding_box_array__())
            LB = numpy.min(BB, 0)
            TR = numpy.max(BB, 0)
            self.__init__(LB[0], TR[0], TR[1], LB[1])
        return self

    def transform_copy(self, transformation):
        """ transforms a copy of the size_info box and makes a new cartesian box over it """
        if self.__is_initialized__():
            return size_info_from_numpyarray(transformation.apply_to_array(self.__bounding_box_array__()))
        else:
            return SizeInfo()

    def __eq__(self, other):
        return self.west == other.west and self.east == other.east and self.north == other.north and self.south == other.south and self.center == other.center and self.size == other.size and self.width == other.width and self.height == other.height 

    def __ne__(self, other):
        return not self.__eq__(other)

    def grow_absolute(self, growth):
        self.__west = self.__west - growth
        self.__east = self.__east + growth
        self.__north = self.__north + growth
        self.__south = self.__south - growth

    def __str__(self):
        return "west: %f - east: %f - south: %f - north: %f" % (self.west, self.east, self.south, self.north)


def size_info_from_point_list(point_list):
    """ generate a size info from a point list """
    if len(point_list) == 0: return SizeInfo()
    x = [c[0] for c in point_list]
    y = [c[1] for c in point_list]
    return SizeInfo(min(x), max(x), max(y), min(y))

def size_info_from_numpyarray(points):
    """ generate a size_info from a numpy array """
    if len(points) == 0: return SizeInfo()
    LB = numpy.min(points, 0)
    TR = numpy.max(points, 0)
    return SizeInfo(LB[0], TR[0], TR[1], LB[1])

def size_info_from_coord(coord):
    """ generate a size info from a single coordinate """
    return SizeInfo(coord[0], coord[0], coord[1], coord[1])

def size_info(shape):
    """ generate a size_info from a shape-like object """
    from . import shape
    if isinstance(shape, shape.Shape):
        return shape.size_info()
    elif isinstance(shape, numpy.ndarray):
        return size_info_from_numpyarray(shape)
    elif isinstance(shape, list):
        return size_info_from_pointlist(shape)
    elif isinstance(shape, coord.Coord2):
        return size_info_from_coord(shape)
    else:
        raise TypeError("Invalid type for size_info(): " + str(type(shape)))


def SizeInfoProperty(internal_member_name=None, restriction=RestrictNothing(), **kwargs):
    """ SizeInfo property descriptor for a class """ 
    R = RestrictType(SizeInfo) & restriction
    return RestrictedProperty(internal_member_name=internal_member_name, restriction=R, **kwargs)


EMPTY_SIZE_INFO = SizeInfo(west=0.0, east=0.0, south=0.0, north=0.0)

