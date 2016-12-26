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

from ipcore.properties.initializer import StrongPropertyInitializer
from ipkiss.geometry.vector import Vector, Vector3
from ipkiss.geometry.coord import Coord2, Coord2Property, Size2Property
from pysics.basics.domain import DomainProperty
from ipcore.properties.predefined import StringProperty

class __Port__(StrongPropertyInitializer):
    """ Base class for interfaces in and out of a structure """
    domain = DomainProperty(required=True)
    name = StringProperty(default="")
    
    def __str__(self):
        return self.name
    
__Port__.__invert_class__ = __Port__

class __DirectionalPort__(__Port__):
    """ Directional port """
    
    def invert(self):
        self.__class__ = self.__invert_class__
        return self


class __InPort__(__DirectionalPort__):
    """ Unidirectional input port """
    pass

class __OutPort__(__DirectionalPort__):
    """ Unidirectional output port """
    __invert_class__ = __InPort__

__InPort__.__invert_class__ = __OutPort__

class __InPlanePort__(__Port__):
    """ Port with a position in the (x,y) plane 
    """
    position = Coord2Property(default=(0.0, 0.0))
    
    def move(self, coordinate):
        self.position.move(coordinate)
    
    def move_copy(self, coordinate):
        return self.__class__(position = self.position + coordinate)
 
    def transform(self, transformation):
        self.position = transformation.apply_to_coord(self.position)
        return self

    def transform_copy(self, transformation):
        return self.__class__(position = transformation.apply_to_coord(self.position))

    def is_match(self, other):
        return (self.position == other.position)
    

    def __eq__(self, other):
        if not isinstance(other, __InPlanePort__): return False
        return (self.position == other.position)

    def __ne__(self, other):
        return (self.position != other.position)
    
class __AreaPort__(__InPlanePort__):
    """ Port with a given area size in the plane 
    """
    area = Size2Property(default=(0.0, 0.0))

    def __eq__(self, other):
        if not isinstance(other, __AreaPort__): return False
        return (self.area == other.area) and super(__AreaPort__, self).__eq__(other)
    
    def __ne__(self, other):
        return (self.area != other.area) or super(__AreaPort__, self).__ne__(other)
    
        
class __OrientedPort__(Vector, __Port__):
    """ In-plane port with orientation
        Has a position and an (in-plane) angle (azimuth) 
    """
    def move_copy(self, coordinate):
        return self.__class__(position = self.position + coordinate, angle = self.angle_deg)

    def transform(self, transformation):
        self.position = transformation.apply_to_coord(self.position)
        self.angle_deg = transformation.apply_to_angle_deg(self.angle_deg)
        return self

    def transform_copy(self, transformation):
        return self.__class__(position = transformation.apply_to_coord(self.position), 
                              angle = transformation.apply_to_angle_deg(self.angle_deg))

    def flip(self):
        #gives port in other direction
        return self.__class__(position = self.position, angle = (self.angle_deg + 180.0) % 360.0)

    def invert_copy(self):
        #changes the Port from InPort to OutPort. This is just added here for ease of coding
        return self.__invert_class__(position = self.position, angle = self.angle_deg)


    def is_match(self, other):
        return ((self.position == other.position) and
                ((self.angle - other.angle) % 360.0 == 180.0))

    def is_manhattan(self):
        return (abs(abs((self.angle_deg + 45) % 90) - 45) < 0.001) 

    def __eq__(self, other):
        if not isinstance(other, OpticalPort): return False
        return (self.position == other.position and 
                (self.angle_deg == other.angle_deg))


    def __ne__(self, other):
        return (self.position != other.position or 
                (self.angle_deg != other.angle_deg))


class __OutOfPlanePort__(Vector3, __Port__):
    """ Out-of-plan port with orientation
        Has a position, an in-plan angle (azimuth) and an out-of-plan angle (inclination).
    """
    pass
