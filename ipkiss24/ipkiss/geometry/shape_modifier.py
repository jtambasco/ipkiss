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

from .shape import Shape, ShapeProperty
from ipkiss.log import IPKISS_LOG as LOG

__all__ = ["__ShapeModifier__"]

class __ShapeModifier__(Shape):
    original_shape = ShapeProperty(required = True)
    
    def __init__(self, original_shape, **kwargs):
        super(__ShapeModifier__, self).__init__(
            original_shape = original_shape, 
            **kwargs)

    def move(self, position):
        self.original_shape = self.original_shape.move_copy(position)
        return self

