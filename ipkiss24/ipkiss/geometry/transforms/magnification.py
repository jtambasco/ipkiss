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
from ipcore.mixin import mixin
from ipcore.properties.descriptor import SetFunctionProperty
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.initializer import SUPPRESSED


__all__ = ["Magnification"]


class Magnification(__SpecialNoDistortTransform__):
    """ scaling transformation with respect to a given point """
    def __init__(self, magnification_center = (0.0, 0.0), magnification = 1.0, absolute_magnification = False, **kwargs):
        if not "translation" in kwargs:
            kwargs['translation'] = SUPPRESSED
        super(Magnification, self).__init__(
            magnification_center = magnification_center,
            magnification = magnification,
            absolute_magnification = absolute_magnification,
            **kwargs)        

    absolute_magnification = getattr(NoDistortTransform, 'absolute_magnification')
    
    def set_magnification(self, value):
        self.__magnification__ = value
        if hasattr(self, "__magnification_center__"):
            center = self.__magnification_center__
            self.translation = Coord2((1 - self.__magnification__) * center.x,
                                          (1 - self.__magnification__) * center.y)
            
            
    magnification = SetFunctionProperty("__magnification__", set_magnification, default = 1.0)
    
    
    def set_magnification_center(self, center):
        if not isinstance(center, Coord2):
            center = Coord2(center[0], center[1])
        self.__magnification_center__ = center
        if hasattr(self, "__magnification__"):
            self.translation = Coord2((1 - self.__magnification__) * center.x,
                                          (1 - self.__magnification__) * center.y)
    magnification_center = SetFunctionProperty("__magnification_center__", set_magnification_center, restriction = RestrictType(Coord2), preprocess = ProcessorTypeCast(Coord2), default = (0.0, 0.0))
    
    # overloading for efficiency
    def apply_to_coord(self, coord):      
        """ apply transformation to coordinate """
        coord = self.__magnify__(coord)
        coord = self.__translate__(coord)
        return coord

    def reverse_on_coord(self, coord):      
        """ apply reverse transformation to coordinate """
        coord = self.__inv_translate__(coord)
        coord = self.__inv_magnify__(coord)
        return coord

    
    def apply_to_array(self, coords):      
        """ apply transformation to numpy array"""
        coords = self.__magnify_array__(coords)
        coords = self.__translate_array__(coords)
        return coords

    def reverse_on_array(self, coords):      
        """ internal use: applies reverse transformation to a numpy array """
        coords = self.__inv_translate_array__(coords)
        coords = self.__inv_magnify__array__(coords)
        return coords

    def apply_to_length(self, length):
        """ applies transformation to a distance """
        return length * self.magnification
    
    def reverse_on_length(self, length):
        """ applies reverse transformation to a distance """
        return length / self.magnification
    
    def __neg__(self):
        """ returns reverse transformation """
        return Magnification(self.magnification_center, 1.0 / self.magnification)    

    def is_identity(self):
        """ returns True if the transformation does nothing """
        return (self.magnification == 1.0)

    def is_isometric(self):
        """ returns True if the transformation does nothing """
        return (self.magnification == 1.0)



class __MagnificationMixin__(object):
    def magnify(self, magnification_center = (0.0, 0.0), magnification = 1.0, absolute_magnification = False):
        """magnifies this object """
        return self.transform(Magnification(magnification_center, magnification, absolute_magnification))

    def magnify_copy(self, magnification_center = (0.0, 0.0), magnification = 1.0, absolute_magnification = False):
        """magnifies a copy of this object """
        return self.transform_copy(Magnification(magnification_center, magnification, absolute_magnification))


transformable.Transformable_basic.mixin( __MagnificationMixin__)