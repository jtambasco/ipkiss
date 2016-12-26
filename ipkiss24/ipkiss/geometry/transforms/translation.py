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
from ... import constants

import math
import copy 

__all__ = ["Translation"]

class Translation(__SpecialNoDistortTransform__):
    """ translation transform """
    def __init__(self, translation = (0.0, 0.0), **kwargs):
        super(Translation, self).__init__(
            translation = translation,
            **kwargs)

    translation = getattr(NoDistortTransform, 'translation')

    # overloading for efficiency
    def apply_to_coord(self, coord):  
        """ apply transformation to coordinate """
        return self.__translate__(coord)

    def reverse_on_coord(self, coord):      
        """ apply reverse transformation on coodinate """
        return self.__inv_translate__(coord)

    def apply_to_array(self, coords):      
        """ applies transformation to numpy array """
        return self.__translate_array__(coords)

    def reverse_on_array(self, coords):      
        """ apply reverse transformation to numpy array """
        return self.__inv_translate_array__(coords)

    def __add__(self, other):
        """ returns the concatenation of this transform and other """
        if other is None: return copy.deepcopy(self)
        if isinstance(other, Translation):
            return Translation(Coord2(self.translation.x + other.translation.x, self.translation[1] + other.translation[1]))
        else:
            return __SpecialNoDistortTransform__.__add__(self, other)
    
    def __iadd__(self, other):
        """ concatenates other to this transform """        
        if other is None: return self
        if isinstance(other, Translation):
            self.translation = Coord2(self.translation.x + other.translation.x, self.translation.y + other.translation.y)
            return self
        else:
            return NoDistortTransform.__iadd__(self, other)

    def __neg__(self):
        """ helper methods which returns the reverse transformation """
        return Translation(Coord2(-self.translation.x, -self.translation.y))
    

    def is_identity(self):
        """ returns True if the transformation does nothing """
        return ((self.translation.x == 0.0) and
                (self.translation.y == 0.0) 
            )


def shape_translate(shape, translation_vector = (1.0, 0.0)):
    """ legacy: apply a translation to a shape """
    return Translation(translation_vector)(shape)

class __TranslationMixin__(object):
    def move(self, position):
        """moves this object """
        return self.transform(Translation(position))

    def move_copy(self, position):
        """moves copy of this object """
        return self.transform_copy(Translation(position))
    
    def move_polar(self, distance, angle):
        return self.move((distance * math.cos(constants.DEG2RAD * angle), distance * math.sin(constants.DEG2RAD * angle))) 
    
    def move_polar_copy(self, distance, angle):
        """moves copy of this object """
        return self.move_copy((distance * math.cos(constants.DEG2RAD * angle), distance * math.sin(constants.DEG2RAD * angle))) 

    def translate(self, translation = (0.0, 0.0)):
        """translates this object """
        return self.transform(Translation(translation))
    
    def translate_copy(self, position):
        """moves copy of this object """
        return self.transform_copy(Translation(position))


transformable.Transformable_basic.mixin(__TranslationMixin__)
