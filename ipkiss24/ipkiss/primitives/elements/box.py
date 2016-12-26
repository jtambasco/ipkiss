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

from .basic import __LayerElement__
from ...geometry import size_info
from ...geometry.coord import Coord2Property, Size2Property
from ...geometry.shapes.basic import ShapeRectangle

__all__ = ["Box", "Box"]

class Box(__LayerElement__):
    center = Coord2Property(default = (0.0, 0.0))
    box_size = Size2Property(default = (1.0, 1.0))
    def __init__ (self, layer, center = (0.0,0.0), box_size = (1.0, 1.0), transformation = None, **kwargs):
        super(Box, self).__init__(layer = layer, transformation = transformation, center = center, box_size = box_size, **kwargs)

    def size_info(self):
        return size_info.SizeInfo ([(self.center[0] - 0.5* self.box_size[0], self.center[1] - 0.5* self.box_size[1]) ,
                      (self.center[0] + 0.5* self.box_size[0], self.center[1] + 0.5* self.box_size[1])])

    def convex_hull(self):
        return ShapeRectangle(center = self.center, box_size = self.box_size)

    def flat_copy(self, level = -1):
        return ElementList(Box(self.layer, self.center, self.box_size))
    
    def is_empty(self):
        return (self.box_size[0] == 0.0 and self.box_size[1]==0.0)

        