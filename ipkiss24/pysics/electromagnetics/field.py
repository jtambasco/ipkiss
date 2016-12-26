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

from ipcore.all import *

from ..basics.field import __Vectorial3Field__, __CompoundField__
    
class ElectricField(__Vectorial3Field__):
    pass

class MagneticField(__Vectorial3Field__):
    pass

class PoyntingField(__Vectorial3Field__):
    pass


class ElectroMagneticField(__CompoundField__):
    E = FunctionProperty(fget = lambda self: self.value[0], fset = None)
    H = FunctionProperty(fget = lambda self: self.value[1], fset = None)
    S = FunctionProperty(fget = lambda self: PoyntingField(value = self.E.value.cross(self.H.value)), fset = None)
    
    def overlap(self, other):
        # FIXME: Check this computation
        norm = self.S.value.dot(other.S.value)
        if (norm):           
            return self.E.value.cross(other.H.value).dot(other.E.value.cross(self.H.value)) / norm
        else:
            return 0
        
    def __abs__(self):
        return abs(self.S)