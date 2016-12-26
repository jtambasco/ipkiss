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

from .coord import Coord2, Coord2Property, Coord3Property
from . import transformable
from .transforms.translation import Translation
from .transforms.rotation import Rotation
from . import shape_info
from .. import constants

from ipcore.properties.descriptor import RestrictedProperty, FunctionProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.initializer import StrongPropertyInitializer

__all__ = ["Vector", "Vector3", "transformation_from_vector", "vector_from_two_points", "VectorProperty", 
         "vector_match_transform", "vector_match_transform_identical"]


class Vector(StrongPropertyInitializer, transformable.Transformable):
    """ positioned vector, consisting of a point and an angle """
    position = Coord2Property(default = (0.0, 0.0), doc="Position of the port (coordinate).")

    def get_x(self):
        return self.position.x
    x = property(get_x)
    
    def get_y(self):
        return self.position.y
    y = property(get_y)

    def get_angle_rad(self):
        try:
            return constants.DEG2RAD * self.__angle__
        except AttributeError, e:
            return 0.0
        
    def set_angle_rad(self, value):
        self.__angle__ = (constants.RAD2DEG * value) % 360.0
        
    angle_rad = FunctionProperty(get_angle_rad, set_angle_rad, doc="The outward facing angle of the port in radians (stored in degrees by default, converted to radians if needed)")
    
    def get_angle_deg(self):
        try:
            return self.__angle__
        except AttributeError, e:
            return 0.0
        
    def set_angle_deg(self, value):
        self.__angle__ = value % 360.0
        
    angle_deg = FunctionProperty(get_angle_deg, set_angle_deg, doc = "The outward facing angle of the port.")
    angle = angle_deg
    
    def cos(self):
        return cos(constants.DEG2RAD * self.__angle__)
    
    def sin(self):
        return sin(constants.DEG2RAD * self.__angle__)

    def tan(self):
        return tan(constants.DEG2RAD * self.__angle__)
    
    def flip(self):
        #gives port in other direction
        return Vector(position=self.position, angle=(self.__angle__ + 180.0) % 360.0)

    def __getitem__(self, key):
        # behave like a coordinate for e.g. size_info
        if key == 0:
            return self.position[0]
        if key == 1:
            return self.position[1]
        else:
            raise IndexError("Vector supports only subscription[0] and [1], not " + str(key))

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.position == other.position and (self.angle_deg == other.angle_deg)
    
    def __ne__(self, other):
        return self.position != other.position or (self.angle_deg != other.angle_deg)

    def __repr__(self):
        return "<Vector (%f, %f), a=%f>" % (self.x, self.y, self.angle_deg)
    
    def transform(self, transformation):
        self.position = transformation.apply_to_coord(self.position)
        self.angle_deg = transformation.apply_to_angle_deg(self.angle_deg)
        return self    


def transformation_from_vector(vector):
    """ make a transformation (rotation + translation) from a vector """
    return Rotation((0.0, 0.0), vector.angle_deg) + Translation(vector.position)

def vector_from_two_points(point1, point2):
    """ make a vector out of two points """
    return Vector(position=point1, angle=shape_info.angle_deg(point2, point1))

def VectorProperty(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    """ property restricted to a vector """
    R = RestrictType(Vector) & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def vector_match_transform(vector1, vector2):
    """ returns transformation to realign vectort 1 to match position and opposite angle of vector 2 """
    return Translation(vector2.position - vector1.position) + Rotation(vector2.position, vector2.angle_deg - vector1.angle_deg + 180.0)  

def vector_match_transform_identical(vector1, vector2):
    """ returns transformation to realign vectort 1 to match position and angle with vector 2 """
    T = Translation(vector2.position - vector1.position) 
    R = Rotation(vector2.position, vector2.angle_deg - vector1.angle_deg)  
    return T + R

### 3D vector

class Vector3(Vector):
    """ 3D extension of Vector, adding an inclination angle. (Vector.angle is the azimuth angle) """

    def get_inclination_rad(self):
        try:
            return constants.DEG2RAD * self.__inclination__
        except AttributeError, e:
            return 0.0
        
    def set_inclination_rad(self, value):
        self.__inclination__ = (constants.RAD2DEG * value) % 360.0
        
    inclination_rad = FunctionProperty(get_inclination_rad, set_inclination_rad, doc="The outward facing angle of the port relative to the zenit, in radians (stored in degrees by default, converted to radians if needed)")
    
    def get_inclination_deg(self):
        try:
            return self.__inclination__
        except AttributeError, e:
            return 0.0
        
    def set_inclination_deg(self, value):
        self.__inclination__ = value % 360.0
        
    inclination_deg = FunctionProperty(get_inclination_deg, set_inclination_deg, doc = "The outward facing angle of the port relative to the zenit.")
    inclination = inclination_deg


    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.position == other.position and (self.angle_deg == other.angle_deg) and (self.inclination_deg == other.inclination_deg)
    
    def __ne__(self, other):
        return self.position != other.position or (self.angle_deg != other.angle_deg) or (self.inclination_deg != other.inclination_deg)

    def __repr__(self):
        return "<Vector3 (%f, %f), i=%f, a=%f>" % (self.x, self.y, self.inclination_deg, self.angle_deg)
    
    def transform(self, transformation):
        super(Vector3, self).transform(transformation)
        return self    
