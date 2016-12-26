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

from .special import __SpecialNoDistortTransform__
from .no_distort import NoDistortTransform
from .translation import Translation
from .rotation import Rotation
from .magnification import Magnification
from ..coord import Coord2
from types import NoneType

__all__ = ["IdentityTransform"]


class IdentityTransform(Translation, Rotation, Magnification, __SpecialNoDistortTransform__):
    """ transform that leaves an object unchanged """
    def __init__(self, **kwargs):
        kwargs["rotation_center"] = (0.0, 0.0)
        kwargs["magnification_center"] = (0.0, 0.0)
        super(IdentityTransform, self).__init__(**kwargs)
    
    def apply(self, item):
        
        if isinstance(item, list):
            return shape.Shape(item)
        else:
            return item
            
    def reverse(self, shape):
        if isinstance(item, list):
            return shape.Shape(item)
        else:
            return item

    def apply_to_coord(self, coord):
        """ apply transformation to coordinate """
        return coord

    def reverse_on_coord(self, coord):
        """ apply reverse transformation to coordinate """
        return coord

    def apply_to_coord3(self, coord):
        """ apply transformation to coordinate """
        return coord

    def reverse_on_coord3(self, coord):
        """ apply reverse transformation to coordinate """
        return coord
    
    
    def apply_to_array(self, coords):
        """ apply transformation to numpy array"""
        return coords

    def reverse_on_array(self, coords):
        """ internal use: applies reverse transformation to a numpy array """
        return coords

    def apply_to_array3(self, coords):
        """ apply transformation to numpy array"""
        return coords

    def reverse_on_array3(self, coords):
        """ internal use: applies reverse transformation to a numpy array """
        return coords

    def __neg__(self):
        return IdentityTransform()

    def __add__(self, other):
        """ returns the concatenation of this transform and other """
        if isinstance(other, (NoneType, IdentityTransform)):
            return IdentityTransform()
        elif isinstance(other, Translation):
            return Translation(other.translation)
        elif isinstance(other, Rotation):
            return Rotation(other.rotation_center, other.rotation, other.absolute_rotation)
        elif isinstance(other, Magnification):
            return Magnification(other.magnification_center, other.magnification, other.absolute_magnfication)
        else:
            return __SpecialNoDistortTransform__.__add__(self, other)
    
    def __iadd__(self, other):
        """ concatenates other to this transform """
        if isinstance(other, (NoneType, IdentityTransform)):
            return self
        else:
            return __SpecialNoDistortTransform__.__iadd__(self, other)

    def is_identity(self):
        """ returns True if the transformation does nothing """
        return True
