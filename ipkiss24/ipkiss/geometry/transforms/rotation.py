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

from .no_distort import NoDistortTransform
from .special import __SpecialNoDistortTransform__
from ipcore.properties.descriptor import SetFunctionProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.initializer import SUPPRESSED

from .. import transformable
from ..coord import Coord2, Coord2Property, Coord2
from ipcore.mixin import mixin
from ... import constants
from math import cos, sin
__all__ = ["Rotation"]

class Rotation(__SpecialNoDistortTransform__):
    """ rotation around point over a given angle (degrees) """
    def __init__(self, rotation_center = (0.0, 0.0), rotation = 0.0, absolute_rotation = False, **kwargs):
        if not 'translation' in kwargs:
            kwargs['translation'] = SUPPRESSED
        super(Rotation, self).__init__(
            rotation_center = rotation_center,
            rotation = rotation,
            absolute_rotation = absolute_rotation,
            **kwargs)
        

    absolute_rotation = getattr(NoDistortTransform, 'absolute_rotation')
    
    def set_rotation(self, value):
        self.__rotation__ = value % 360.0
        if value % 90.0 == 0.0:
            # make sure sine and cosine are really zero when needed!
            if self.__rotation__ == 0.0:
                self.__ca__ = 1.0
                self.__sa__ = 0.0
            elif self.__rotation__ == 90.0:
                self.__ca__ = 0.0
                self.__sa__ = 1.0
            elif self.__rotation__ == 180.0:
                self.__ca__ = -1.0
                self.__sa__ = 0.0
            elif self.__rotation__ == 270.0:
                self.__ca__ = 0.0
                self.__sa__ = -1.0
        else:
            self.__ca__ = cos(value * constants.DEG2RAD)
            self.__sa__ = sin(value * constants.DEG2RAD)
        if hasattr(self, "__rotation_center__"):
            center = self.__rotation_center__
            self.translation = Coord2(center.x * (1 - self.__ca__) + center.y * self.__sa__,
                                      center.y * (1 - self.__ca__) - center.x * self.__sa__)
            
    rotation = SetFunctionProperty("__rotation__", set_rotation, default = 0.0)
    
    def set_rotation_center(self, center):
        if not isinstance(center, Coord2):
            center = Coord2(center[0], center[1])
        self.__rotation_center__ = center
        if hasattr(self, "__ca__"):
            self.translation = Coord2(center.x * (1 - self.__ca__) + center.y * self.__sa__,
                                      center.y * (1 - self.__ca__) - center.x * self.__sa__)
    rotation_center = SetFunctionProperty("__rotation_center__", set_rotation_center, restriction = RestrictType(Coord2), preprocess = ProcessorTypeCast(Coord2), default = (0.0, 0.0))

    # overloading for efficiency
    def apply_to_coord(self, coord):     
        """ apply transformation to coordinate """
        coord = self.__rotate__(coord)
        coord = self.__translate__(coord)
        return coord

    def reverse_on_coord(self, coord):      
        """ apply reverse transformation to coordinate """
        coord = self.__inv_translate__(coord)
        coord = self.__inv_rotate__(coord)
        return coord

    def apply_to_array(self, coords):      
        """ apply transformation to numpy array"""
        coords = self.__rotate_array__(coords)
        coords = self.__translate_array__(coords)
        return coords

    def reverse_on_array(self, coords):      
        """ internal use: applies reverse transformation to a numpy array """
        coords = self.__inv_translate_array__(coords)
        coords = self.__inv_rotate_array__(coords)
        return coords


    def apply_to_angle_deg(self, angle):
        """ apply transformation to absolute angle (degrees) """
        a = angle
        a += self.rotation
        return a % 360.0
    
    def reverse_on_angle_deg(self, angle):
        """ apply transformation to absolute angle (degrees) """
        a = angle - self.rotation
        return a % 360.0

    def apply_to_angle_rad(self, angle):
        a = angle
        a += self.rotation * constants.DEG2RAD
        return a % (2 * pi)
    
    def reverse_on_angle_rad(self, angle):
        a = angle - self.rotation * constants.DEG2RAD
        return a % (2 * pi)

    def __neg__(self):
        """  returns the reverse transformation """
        return Rotation(self.rotation_center, -self.rotation)
    
    def is_identity(self):
        """ returns True if the transformation does nothing """
        return (self.rotation == 0.0)

    
def shape_rotate(shape, origin = (0.0, 0.0), angle = 90.0):
    """ legacy: apply a rotation to a shape """
    return Rotation(origin, angle)(shape)

class __RotationMixin__(object):
    def rotate(self, rotation_center = (0.0, 0.0), rotation = 0.0, absolute_rotation = False):
        """rotates this object """
        return self.transform(Rotation(rotation_center, rotation, absolute_rotation))
    def rotate_copy(self, rotation_center = (0.0, 0.0), rotation = 0.0, absolute_rotation = False):
        """rotates a copy of this object """
        return self.transform_copy(Rotation(rotation_center, rotation, absolute_rotation))


transformable.Transformable_basic.mixin(__RotationMixin__)
