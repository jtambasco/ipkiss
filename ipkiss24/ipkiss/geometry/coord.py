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

from . import transformable
from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.restrictions import RestrictType, RestrictList
from ipcore.properties.predefined import RESTRICT_NONNEGATIVE
from ipcore.properties.processors import ProcessorTypeCast
import math
import numpy

__all__ = ["Coord2", "Coord2Property", "Size2Property", "coord2_match_position", "RESTRICT_COORD2", "RESTRICT_SIZE2",
           "Coord3", "Coord3Property", "Size3Property", "coord3_match_position", "RESTRICT_COORD3", "RESTRICT_SIZE3"]

# base class (can also be used for 3-D coords, etc.
class Coord(transformable.Transformable):
    pass

class Coord2(Coord):
    """ 2-D coordinate
        
        .. class:: Coord2(x, y)
                   Coord2(C)
        
           :param x, y: x and y are numbers
           :param C: C is a 2-tuple of numbers or another coordinate           
    """
    def __init__(self, *args):
        if len(args) == 2:
            self.x, self.y = args
        elif len(args) == 1:
            self.x, self.y = args[0][0], args[0][1]
    
    def __getitem__(self, index):
        if index == 0: return self.x
        if index == 1: return self.y
        raise IndexError("Coord2 type only supports index 0 and 1")
    
    def __setitem__(self, index, value):
        if index == 0: 
            self.x = value
        elif index == 1: 
            self.y = value
        else:
            raise IndexError("Coord2 type only supports index 0 and 1")
        return

    def __iter__(self):
        for index in range(2):
            yield self[index]

    def transform(self, transformation):
        """ apply a transformation to the coordinate 
        """
        C = transformation.apply_to_coord(self)
        self.x = C.x
        self.y = C.y
        return self
    
    def transform_copy(self, transformation):
        """ return a transformed copy of the coordinate """
        return transformation.apply_to_coord(Coord2(self.x, self.y))
    
    def move(self, position):
        """ move the coordinate by a displacement vector 

               :param position: displacement
               :type position: Coord2 or tuple
        """
        self.x += position[0] # compatibility with tuples used for quick notation
        self.y += position[1] # compatibility with tuples used for quick notation
        return self
    
    def move_copy(self, position):
        """ return a moved copy of the coordinate """
        return Coord2(self.x + position[0], self.y + position[1])

    def snap_to_grid(self, grids_per_unit = None):
        """ snap the coordinate to the given or current grid

                :param grids_per_unit: number of grid points per unit
                :type grids_per_unit: float
        """
        from .. import settings
        if grids_per_unit is None:
            grids_per_unit = settings.get_grids_per_unit()
        self.x = round(self.x * grids_per_unit) / grids_per_unit
        self.y = round(self.y * grids_per_unit) / grids_per_unit
        return self
        
    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __eq__(self, other):
        return (other != None) and (abs(self[0] - other[0]) < 10e-10) and (abs(self[1] - other[1]) < 10e-10)
    
    def __ne__(self, other):
        return (other == None) or (abs(self[0] - other[0]) > 10e-10) or (abs(self[1] - other[1]) > 10e-10)

    def distance(self, other):    
        """  the distance to another coordinate """
        return math.sqrt((other[0] - self.x) ** 2 + (other[1] - self.y) ** 2)

    def angle_deg(self, other=(0.0, 0.0)):
        """ the angle with respect to another coordinate, in degrees """
        return 180.0 / math.pi * self.angle_rad(other)

    def angle_rad(self, other=(0.0, 0.0)):
        """ the angle with respect to another coordinate, in radians """
        return math.atan2(self.y - other[1], self.x - other[0])
    
    def __iadd__(self, other):
        self.x += other[0]
        self.y += other[1]
        return self
        
    def __add__(self, other):
        return Coord2(self.x + other[0], self.y + other[1])
    
    def __isub__(self, other):
        self.x -= other[0]
        self.y -= other[1]
        return self
        
    def __sub__(self, other):
        return Coord2(self.x - other[0], self.y - other[1])
    
    def __neg__(self):
        return Coord2(-self.x, -self.y)    
    
    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self
    
    def __mul__(self, other):
        return Coord2(self.x * other, self.y * other)
    
    def __rmul__(self, other):
        return Coord2(self.x * other, self.y * other)
    
    def __repr__(self):
        return "C2(%f, %f)" % (self.x, self.y)
    
    def dot(self, other):
        return numpy.conj(self.x) * other[0] + numpy.conj(self.y) * other[1]        
    
    def __abs__(self):
        return math.sqrt(abs(self.x) ** 2 + abs(self.y) ** 2)
        
    def id_string(self):
        return "%d_%d" % (self.x * 1000, self.y * 1000)
    
    def convert_to_array(self):
        return [self.x, self.y]
    

RESTRICT_COORD2 = RestrictType(Coord2)
RESTRICT_SIZE2 = RESTRICT_COORD2 & RestrictList(RESTRICT_NONNEGATIVE) 
            
def Coord2Property(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    """ Coord2 property descriptor for a class """ 
    R = RESTRICT_COORD2 & restriction
    P = ProcessorTypeCast(Coord2) + preprocess
    return RestrictedProperty(internal_member_name=internal_member_name, restriction=R, preprocess=P, **kwargs)

def Size2Property(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    """ Coord2 based size descriptor for a class (non-negative values in both dimensions) """ 
    R = RESTRICT_SIZE2 & restriction
    P = ProcessorTypeCast(Coord2) + preprocess
    return RestrictedProperty(internal_member_name=internal_member_name, restriction=R, preprocess=P, **kwargs)


def coord2_match_position(P1, P2):
    """ returns position (or vector) to translate port 1 in order to coindice with port 2 """
    return Coord2(P2[0], P2[1]) - Coord2(P1[0], P1[1]) 


class Coord3(Coord):
    """ 3-D coordinate
        
        .. class:: Coord3(x, y, z)
                   Coord2(C)
        
           :param x, y, z: x, yand z are numbers
           :param C: C is a 3-tuple of numbers or another coordinate           
    """
    def __init__(self, *args):
        if len(args) == 3:
            self.x, self.y, self.z = args
        if len(args) == 2:
            self.x, self.y = args
            self.z = 0
        elif len(args) == 1:
            try:
                self.x, self.y, self.z = args[0][0], args[0][1], args[0][2]
            except:
                try:
                    self.x, self.y, self.z = args[0][0], args[0][1], 0.0
                except:
                    try:
                        self.x, self.y, self.z = args[0][0], 0.0, 0.0
                    except:                    
                        self.x = args
                        self.y = 0
                        self.z = 0
    
    def __getitem__(self, index):
        if index == 0: return self.x
        if index == 1: return self.y
        if index == 2: return self.z
        raise IndexError("Coord3 type only supports index 0, 1 and 2")
    
    def __setitem__(self, index, value):
        if index == 0: 
            self.x = value
        elif index == 1: 
            self.y = value
        elif index == 2: 
            self.z = value
        else:
            raise IndexError("Coord3 type only supports index 0 and 1")
        return

    def __iter__(self):
        for index in range(3):
            yield self[index]

    def transform(self, transformation):
        """ apply a transformation to the coordinate 
        """
        C = transformation.apply_to_coord3(self)
        self.x = C.x
        self.y = C.y
        self.z = C.z
        return self
    
    def transform_copy(self, transformation):
        """ return a transformed copy of the coordinate """
        return transformation.apply_to_coord3(Coord3(self.x, self.y, self.z))
    
    def move(self, position):
        """ move the coordinate by a displacement vector 

               :param position: displacement
               :type position: Coord2 or tuple
        """
        self.x += position[0] # compatibility with tuples used for quick notation
        self.y += position[1] # compatibility with tuples used for quick notation
        self.z += position[2] # compatibility with tuples used for quick notation
        return self
    
    def move_copy(self, position):
        """ return a moved copy of the coordinate """
        return Coord3(self.x + position[0], self.y + position[1], self.z + position[2])

    def snap_to_grid(self, grids_per_unit = None):
        """ snap the coordinate to the given or current grid

                :param grids_per_unit: number of grid points per unit
                :type grids_per_unit: float
        """
        from .. import settings
        if grids_per_unit is None:
            grids_per_unit = settings.get_grids_per_unit()
        self.x = round(self.x * grids_per_unit) / grids_per_unit
        self.y = round(self.y * grids_per_unit) / grids_per_unit
        self.z = round(self.z * grids_per_unit) / grids_per_unit
        return self
        
    def __str__(self):
        return "(%f, %f, %f)" % (self.x, self.y, self.z)

    def __eq__(self, other):
        return not (other is None) and ((self[0] == other[0]) and (self[1] == other[1]) and (self[2] == other[2]))
    
    def __ne__(self, other):
        return (other is None) or ((self[0] != other[0]) or (self[1] != other[1]) or (self[2] != other[2]))

    def distance(self, other):
        """ the distance to another coordinate """
        return math.sqrt((other[0] - self.x) ** 2 + (other[1] - self.y) ** 2 + (other[2] - self.z) ** 2)
    
    def __iadd__(self, other):
        self.x += other[0]
        self.y += other[1]
        self.z += other[2]
        return self
        
    def __add__(self, other):
        return Coord3(self.x + other[0], self.y + other[1], self.z + other[2])
    
    def __isub__(self, other):
        self.x -= other[0]
        self.y -= other[1]
        self.z -= other[2]
        return self
        
    def __sub__(self, other):
        return Coord3(self.x - other[0], self.y - other[1], self.z - other[2])
    
    def __neg__(self):
        return Coord3(-self.x, -self.y, -self.z)
    
    
    def __imul__(self, other):
        self.x *= other
        self.y *= other
        self.z *= other
        return self
    
    def __mul__(self, other):
        return Coord3(self.x * other, self.y * other, self.z * other)
    def __rmul__(self, other):
        return Coord3(self.x * other, self.y * other, self.z * other)
    
    def dot(self, other):
        """ dot product of two coordinates """
        return numpy.conj(self.x) * other[0] + numpy.conj(self.y) * other[1] + numpy.conj(self.z) * other[2]

    def __abs__(self):
        return math.sqrt(abs(self.x) ** 2 + abs(self.y) ** 2 + abs(self.z) ** 2)
    
    def cross(self, other):
        """ cross product of two coordinates """
        return Coord3(self.y * other[2] - self.z * other[1],
                      self.z * other[0] - self.x * other[2],
                      self.x * other[1] - self.y * other[0])
    
    def __repr__(self):
        return "C3(%f, %f, %f)" % (self.x, self.y, self.z)
        
    def id_string(self):
        return "%d_%d_%d" % (self.x * 1000, self.y * 1000, self.z * 1000)
    
    def convert_to_array(self):
        return [self.x, self.y, self.z]  
    

RESTRICT_COORD3 = RestrictType(Coord3)
RESTRICT_SIZE3 = RESTRICT_COORD3 & RestrictList(RESTRICT_NONNEGATIVE) 
            
def Coord3Property(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    """ Coord3 property descriptor for a class """ 
    R = RESTRICT_COORD3 & restriction
    P = ProcessorTypeCast(Coord3) + preprocess
    return RestrictedProperty(internal_member_name=internal_member_name, restriction=R, preprocess=P, **kwargs)

def Size3Property(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    """ Coord2 based size descriptor for a class (non-negative values in both dimensions) """ 
    R = RESTRICT_SIZE3 & restriction
    P = ProcessorTypeCast(Coord3) + preprocess
    return RestrictedProperty(internal_member_name=internal_member_name, restriction=R, preprocess=P, **kwargs)


def coord3_match_position(P1, P2):
    """ returns position (or vector) to translate port 1 in order to coindice with port 2 """
    return Coord3(P2[0], P2[1], P2[2]) - Coord3(P1[0], P1[1], P2[2]) 
