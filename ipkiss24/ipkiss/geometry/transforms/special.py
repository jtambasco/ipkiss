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

from . import no_distort
from ..coord import Coord2
from ipcore.properties.descriptor import ConvertProperty


__all__ = []

BASE = no_distort.NoDistortTransform

class __SpecialNoDistortTransform__(BASE):
    """ abstract base class for special transforms that are subclassed from NoDistortTransforms"""

    def __make_simple__(self):
        self.__class__ = no_distort.NoDistortTransform
        
    translation = ConvertProperty(BASE, "translation", __make_simple__)
    rotation = ConvertProperty(BASE, "rotation", __make_simple__)
    magnification = ConvertProperty(BASE, "magnification", __make_simple__)
    v_mirror = ConvertProperty(BASE, "v_mirror", __make_simple__)
    absolute_magnification = ConvertProperty(BASE, "absolute_magnification", __make_simple__)
    absolute_rotation = ConvertProperty(BASE, "absolute_rotation", __make_simple__)
    
    def __isub__(self, other):
        """ concatenates reverse of other to this transformation """
        self.__make_simple__()
        return BASE.__isub__(self, other)

    def __iadd__(self, other):
        """ concatenates other to this transformation """
        self.__make_simple__()
        return BASE.__iadd__(self, other)

    def apply_to_angle_deg(self, angle):
        """ applies transformation to absolute angle (degrees) """
        return angle
    
    def reverse_on_angle_deg(self, angle):
        """ applies reverse transformation to absolute angle (degrees) """
        return angle

    def apply_to_angle_rad(self, angle):
        """ applies transformation to absolute angle (radians) """
        return angle
    
    def reverse_on_angle_rad(self, angle):
        """ applies reverse transformation to absolute angle (radians) """
        return angle

    def apply_to_length(self, length):
        """ applies transformation to distance """
        return length

    def reverse_on_length(self, length):
        """ applies reverse transformation to distance """
        return length

    def is_isometric(self):
        """ returns True if the transformation does nothing """
        return True
