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
from .. import transformable
from ..coord import Coord2, Coord2Property
from ipcore.properties.descriptor import SetFunctionProperty
from ipcore.properties.initializer import SUPPRESSED
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.predefined import RESTRICT_NUMBER

from ipcore.mixin import mixin
from numpy import array

__all__ = ["VMirror",
           "HMirror",
           "CMirror"]

class VMirror(__SpecialNoDistortTransform__):
    """ mirror transformation around y-plane """
    def __init__(self, mirror_plane_y = 0.0, **kwargs):
        kwargs['translation'] = SUPPRESSED
        kwargs['v_mirror'] = True
        
        super(VMirror, self).__init__(
            mirror_plane_y = mirror_plane_y,
            **kwargs)
        
    def set_mirror_plane_y(self, value):
        self.__mirror_plane_y__ = value
        self.translation = Coord2(0.0, 2.0 * value)
    mirror_plane_y = SetFunctionProperty("__mirror_plane_y__", set_mirror_plane_y, restriction = RESTRICT_NUMBER, default = 0.0)

    # overloading for efficiency
    def apply_to_coord(self, coord):      
        """ apply transformation to coordinate """
        coord = self.__v_flip__(coord)
        coord = self.__translate__(coord)
        return coord

    def reverse_on_coord(self, coord):      
        """ apply reverse transformation to coordinate """
        coord = self.__inv_translate__(coord)
        coord = self.__inv_v_flip__(coord)
        return coord

    def apply_to_array(self, coords):      
        """ apply transformation to numpy array"""
        coords = self.__v_flip_array__(coords)
        coords = self.__translate_array__(coords)
        return coords

    def reverse_on_array(self, coords):      
        """ internal use: applies reverse transformation to a numpy array """
        coords = self.__inv_translate_array__(coords)
        coords = self.__inv_v_flip_array__(coords)
        return coords

    def __neg__(self):
        """ returns reverse transformation """
        return VMirror(self.mirror_plane_y)

    def is_identity(self):
        """ returns True if the transformation does nothing """
        return False

    def apply_to_angle_deg(self, angle):
        """ apply transformation to absolute angle (degrees) """
        return (-angle) % 360.0
    
    def reverse_on_angle_deg(self, angle):
        """ apply reverse transformation to absolute angle (degrees) """
        return (-angle) % 360.0

    def apply_to_angle_rad(self, angle):
        """ apply transformation to absolute angle (radians) """
        return (-angle) % (2 * pi)
    
    def reverse_on_angle_rad(self, angle):
        """ apply reverse transformation to absolute angle (radians) """
        return (-angle) % (2 * pi)



class HMirror(__SpecialNoDistortTransform__):
    """ mirror transformation around x plane """
    def __init__(self, mirror_plane_x = 0.0, **kwargs):
        kwargs['translation'] = SUPPRESSED
        kwargs['v_mirror'] = True
        kwargs['rotation'] = 180.0
                    
        super(HMirror, self).__init__(
            mirror_plane_x = mirror_plane_x,
            **kwargs)

    def set_mirror_plane_x(self, value):
        self.__mirror_plane_x__ = value
        self.translation = Coord2(2.0 * value, 0.0)
    mirror_plane_x = SetFunctionProperty("__mirror_plane_x__", set_mirror_plane_x, restriction = RESTRICT_NUMBER, default = 0.0)

    def __h_flip__(self, coord):
        """ internal use: mirror coordinate around y-axis """
        return (-coord[0], coord[1])

    def __h_flip_array__(self, coords):
        """ internal use: mirror array around y axis """
        coords *= array([-1, 1])
        return coords

    # overloading for efficiency
    def apply_to_coord(self, coord):      
        """ apply transformation to coordinate """
        # faster than rotation!
        coord = self.__h_flip__(coord)
        coord = self.__translate__(coord)
        return coord

    def reverse_on_coord(self, coord):      
        """ apply reverse transformation to coordinate """
        # faster than rotation!
        coord = self.__inv_translate__(coord)
        coord = self.__h_flip__(coord)
        return coord

    def apply_to_array(self, coords):      
        """ apply transformation to numpy array"""
        # faster than rotation!
        coords = self.__h_flip_array__(coords)
        coords = self.__translate_array__(coords)
        return coords

    def reverse_on_array(self, coords):      
        """ internal use: applies reverse transformation to a numpy array """
        # faster than rotation!
        coords = self.__inv_translate_array__(coords)
        coords = self.__h_flip_array__(coords)
        return coords

    def apply_to_angle_deg(self, angle):
        """ apply transformation to absolute angle (degrees) """
        return (180.0 - angle) % 360.0
    
    def reverse_on_angle_deg(self, angle):
        """ apply reverse transformation to absolute angle (degrees) """
        return (180.0 - angle) % 360.0

    def apply_to_angle_rad(self, angle):
        """ apply transformation to absolute angle (radians) """
        return (pi - angle) % (2 * pi)
    
    def reverse_on_angle_rad(self, angle):
        """ apply reverse transformation to absolute angle (radians) """
        return (pi - angle) % (2 * pi)
 
    def __neg__(self):
        """ returns reverse transformation """        
        return HMirror(self.mirror_plane_x)

    def is_identity(self):
        """ returns True if the transformation does nothing """
        return False


class CMirror(__SpecialNoDistortTransform__):
    """ mirror around point (= 180 degree turn)"""
    def __init__(self, mirror_center = (0.0, 0.0), **kwargs):
        kwargs['translation'] = SUPPRESSED
        kwargs['rotation'] = 180.0
        super(CMirror, self).__init__(
            mirror_center = mirror_center,
            **kwargs)

    def set_mirror_center(self, center):
        self.__mirror_center__ = Coord2(center[0], center[1])
        self.translation = 2 * self.__mirror_center__
    """ mirror center """
    mirror_center = SetFunctionProperty("__mirror_center__", set_mirror_center, restriction = RestrictType(Coord2), preprocess = ProcessorTypeCast(Coord2), default = (0.0, 0.0))

    def __c_flip__(self, coord):
        """ internal use: point mirror coordinate """
        return (-coord[0], -coord[1])
    

    def __c_flip_array__(self, coords):
        """ internal use: point mirror numpy array """
        coords *= array([-1, -1])
        return coords

    # overloading for efficiency
    def apply_to_coord(self, coord):      
        """ apply transformation to coordinate """
        # faster than rotation!
        coord = self.__c_flip__(coord)
        coord = self.__translate__(coord)
        return coord

    def reverse_on_coord(self, coord):      
        """ apply reverse transformation to coordinate """
        # faster than rotation!
        coord = self.__inv_translate__(coord)
        coord = self.__c_flip__(coord)
        return coord

    def apply_to_array(self, coords):      
        """ apply transformation to numpy array"""
        # faster than rotation!
        coords = self.__c_flip_array__(coords)
        coords = self.__translate_array__(coords)
        return coords

    def reverse_on_array(self, coords):      
        """ internal use: applies reverse transformation to a numpy array """
        # faster than rotation!
        coords = self.__inv_translate_array__(coords)
        coords = self.__c_flip_array__(coords)
        return coords

    def apply_to_angle_deg(self, angle):
        """ apply transformation to absolute angle (degrees) """
        return (180.0 + angle) % 360.0
    
    def reverse_on_angle_deg(self, angle):
        """ apply reverse transformation to absolute angle (degrees) """
        return (180.0 + angle) % 360.0

    def __neg__(self):
        """ returns reverse transformation """
        return CMirror(self.mirror_center)
    
    def is_identity(self):
        """ returns True if the transformation does nothing """
        return False


def shape_hflip(shape, flip_plane_x = 0.0):
    """ legacy: apply a h_mirror to a shape """
    return HMirror(flip_plane_x)(shape)

def shape_vflip(shape, flip_plane_y = 0.0):
    """ legacy: apply a v_mirror to a shape """
    return VMirror(flip_plane_y)(shape)



class __MirrorMixin__(object):
    def h_mirror(self, mirror_plane_x = 0.0):
        """mirrors this object horizontally """
        return self.transform(HMirror(mirror_plane_x))
    def v_mirror(self, mirror_plane_y = 0.0):
        """mirrors this this object vertically"""
        return self.transform(VMirror(mirror_plane_y))
    def c_mirror(self, mirror_center = (0.0, 0.0)):
        """point-mirrors this object """
        return self.transform(CMirror(mirror_center))
        
    def h_mirror_copy(self, mirror_plane_x = 0.0):
        """mirrors a copy of this object horizontally """
        return self.transform_copy(HMirror(mirror_plane_x))
    def v_mirror_copy(self, mirror_plane_y = 0.0):
        """mirrors a copy of this object vertically """
        return self.transform_copy(VMirror(mirror_plane_y))
    def c_mirror_copy(self, mirror_center = (0.0, 0.0)):
        """point_mirrors copy of this object """
        return self.transform_copy(CMirror(mirror_center))


transformable.Transformable_basic.mixin(__MirrorMixin__)
