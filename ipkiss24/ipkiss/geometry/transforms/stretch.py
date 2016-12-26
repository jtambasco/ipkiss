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

from ..transform import __ReversibleTransform__
from ..coord import Coord2, Coord2Property
from ipcore.properties.descriptor import SetFunctionProperty
from numpy import array
__all__ = ["Stretch"]

class Stretch(__ReversibleTransform__):
    """ non-homothetic scaling """

    stretch_center = Coord2Property(default = (0.0, 0.0))
    
    def set_stretch_factor(self, value):
        if isinstance(value, Coord2):
            self.__stretch_factor__ = value
        else:
            self.__stretch_factor__ = Coord2(value[0], value[1])
        if self.__stretch_factor__[0] == 0.0 or self.__stretch_factor__[1] == 0.0:
            raise IpcoreAttributeException("Error: Stretch factor cannot be zero in Stretch transform")
    stretch_factor = SetFunctionProperty("__stretch_factor__", set_stretch_factor, required = True)
    """ stretch factor (x, y) """

    def apply_to_coord(self, coord):
        """ apply transformation to coordinate """
        return Coord2(self.__stretch_factor__[0] * coord[0] + (1 - self.__stretch_factor__[0]) * self.stretch_center[0],
                      self.__stretch_factor__[1] * coord[1] + (1 - self.__stretch_factor__[1]) * self.stretch_center[1])

    def reverse_on_coord(self, coord):
        """ apply reverse transformation to coordinate """
        return Coord2(1.0 / self.__stretch_factor__[0] * coord[0] + (1 - 1.0 / self.__stretch_factor__[0]) * self.stretch_center[0],
                      1.0 / self.__stretch_factor__[1] * coord[1] + (1 - 1.0 / self.__stretch_factor__[1]) * self.stretch_center[1])
    
    def apply_to_array(self, coords):
        """ apply transformation to numpy array"""
        coords  *= array([self.stretch_factor.x, self.stretch_factor.y])
        coords += array([(1 - self.__stretch_factor__.x) * self.stretch_center.x, (1 - self.__stretch_factor__.y) * self.stretch_center.y])
        return coords


    def reverse_on_array(self, coords):
        """ internal use: applies reverse transformation to a numpy array """
        coords  *= array([1.0 / self.stretch_factor.x, 1.0 / self.stretch_factor.y])
        coords += array([(1 - 1.0 / self.__stretch_factor__.x) * self.stretch_center.x, (1 - 1.0 / self.__stretch_factor__.y) * self.stretch_center.y])
        return coords
    
    def is_identity(self):
        """ returns True if the transformation does nothing """
        return ((self.stretch_factor.x == 1.0) and
                (self.stretch_factor.y == 1.0))

    def is_isometric(self):
        """ returns True if the transformation conserves angles and distances"""
        return ((self.stretch_factor.x == 1.0) and
                (self.stretch_factor.y == 1.0))

    def is_homothetic(self):
        """ returns True if the transformation conserves angles """
        return self.stretch_factor.x == self.stretch_factor.y


def shape_scale(shape, scaling=(1.0, 1.0), scale_center=(0.0, 0.0)):
    """ legacy: apply a magnification to a shape """
    from .magnification import Magnification
    if scaling[0] == scaling[1]:
        return Magnification(scale_center, scaling[0])(shape)
    else:
        return Stretch(scale_center, scaling)(shape)
