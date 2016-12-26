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

from ...geometry import size_info
import copy
from ipcore.properties.initializer import StrongPropertyInitializer
from ipcore.properties.descriptor import FunctionProperty

from .basic import __Element__
from ..group import __Group__
from ipcore.mixin.mixin import MixinBowl

__all__ = ["Group"]

class Group(__Group__,__Element__, MixinBowl):
    
    def __init__(self, transformation = None, **kwargs):
        super(Group, self).__init__(transformation = transformation, **kwargs)
    
    def size_info(self):
        return self.elements.size_info().transform(self.transformation)
    
    def convex_hull(self):
        return self.elements.convex_hull().transform(self.transformation)

    def flat_copy(self, level = -1):
        if not level == 0:
            return self.elements.flat_copy(level).transform(self.transformation)
        else:
            return ElementList(self.elements)

    def expand_transform(self):
        if not self.transformation.is_identity():
            self.elements.transform(self.transformation)
            self.transformation = None  
            
    def __eq__(self, other):
            return (self.elements == other.elements) and (self.transformation == other.transformation)
         

            