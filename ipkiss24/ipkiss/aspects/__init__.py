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

from ipkiss.primitives.structure import Structure
from ipkiss.aspects.layout.layout import StructureLayoutAspect
from ipkiss.aspects.output.output import StructureOutputAspect
from ipkiss.aspects.port.aspect import *
from ipkiss.primitives.elements.basic import __Element__
from ipkiss.primitives.elements import SRef, ARef

#this is called when ipkiss.all is loaded
def load_aspects():
    Structure.mixin_first(StructureLayoutAspect)
    Structure.mixin_first(StructureOutputAspect) 
    Structure.mixin_first(StructurePortAspect)
    __Element__.mixin(ElementPortAspect)
    SRef.mixin(SRefPortAspect)
    ARef.mixin(ARefPortAspect)
    
load_aspects()
