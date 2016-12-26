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

from ipkiss.aspects.aspect import __Aspect__
from ipkiss.primitives.group import __Group__
from ipkiss.primitives.structure import Structure, __StructureHierarchy__, StructureList
from ipkiss.primitives.elements.reference import __RefElement__

class StructureLayoutAspect(__StructureHierarchy__, __Group__, __Aspect__):
    """Mixin-class for adding the layout aspect to Structure"""
    
    def flat_copy(self, level = -1):
        new_name = self.name + "_flat"    
        S = Structure(new_name, self.elements.flat_copy(level = level))
        return S      
    
