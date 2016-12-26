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


# Fields classes
# Question: should the value of a field be stored in a property, or
# should a vectorial fiel subclass from e.g. a coordinate?

# TODO: add transformations

__all__ = ["FieldProperty"]

from ipkiss.all import *
from ipcore.all import *
import math



class __Field__(Transformable, StrongPropertyInitializer):
    """ abstract base class for a field """
    def transform(self,transformation):
        """ transforms a field in a coordinate system: this basically just reverses the rotation """
        R = Rotation(rotation = -transformation.rotation)
        self.value.transform(R) 
        return self


class __ScalarField__(__Field__):
    """ a scalar value field """
    value = NumberProperty(required = True)
    
    def overlap(self, other):
        # FIXME: Check this computation
        if hasattr(self.value, "conj"):
            return self.value.conj() * other.value / sqrt(abs(self.value) * abs(other.value))
        else:
            return self.value * other.value / math.sqrt(abs(self.value) * abs(other.value))

    def __abs__(self):
        return abs(self.value)
        
class __Vectorial2Field__(__Field__):
    value = Coord2Property(required = True)
    def overlap(self, other):
        # FIXME: Check this calculation
        return self.value.dot(other.value) / math.sqrt(abs(self) * abs(other))
    def __abs__(self):
        return abs(self.value)
    
    
class __Vectorial3Field__(__Field__):
    value = Coord3Property(required = True)
    def overlap(self, other):
        # FIXME: Check this computation
        return self.value.dot(other.value) / math.sqrt(abs(self) * abs(other))
    def __abs__(self):
        return abs(self.value)

class __CompoundField__(__Field__):
    value = RestrictedProperty(required = True, restriction = RestrictList(RestrictType(__Field__)))
    def transform(self,transformation):
        """ transforms a field in a coordinate system: this basically just reverses the rotation """
        for v in self.value:
            v.transform(transformation)
        return self
        

    
RESTRICT_FIELD = RestrictType(__Field__)
            
def FieldProperty(internal_member_name= None, restriction = None, preprocess = None, **kwargs):
    """ Geometry property descriptor for a class """ 
    R = RESTRICT_FIELD & restriction
    return RestrictedProperty(internal_member_name = internal_member_name, restriction = R, preprocess = preprocess, **kwargs )
