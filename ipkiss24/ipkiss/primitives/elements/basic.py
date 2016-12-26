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
from ...geometry import transformable 
import copy
from ..layer import LayerProperty, Layer
from ipcore.properties.initializer import StrongPropertyInitializer, MetaPropertyInitializer
from ipcore.properties.descriptor import FunctionProperty, DefinitionProperty, RestrictedProperty
from ipcore.properties.restrictions import RestrictType, RestrictList
from ipcore.mixin.mixin import MixinBowl
from ipcore.types_list import TypedList
from ipkiss.exceptions.exc import IpkissException
from ipkiss.log import IPKISS_LOG as LOG


__all__ = ["ElementList",
           "ElementListProperty",
           "ElementProperty"]


##########################################################
# Basic __Element__
##########################################################

class __Element__(transformable.StoredNoDistortTransformable, StrongPropertyInitializer):
    
    def __init__(self, transformation = None, **kwargs):
        super(__Element__, self).__init__(transformation = transformation, **kwargs)
    
    def dependencies(self):
        return None
        #from .. import structure
        #return structure.StructureList()

    def __add__(self, other):
        if isinstance(other, list):
            l = ElementList([self])
            l.extend(other)
            return l
        elif isinstance(other, __Element__):
            return ElementList([self, other])
        else:
            raise TypeError("Wrong type of argument for addition in __Element__: " + str(type(other)))

    def __radd__(self, other):
        if isinstance(other, list) :
            l = ElementList(other)
            l.append(self)
            return l
        elif isinstance(other, __Element__):
            return ElementList([other, self])
        else:
            raise TypeError("Wrong type of argument for addition in __Element__: " + str(type(other)))


##########################################################
# __Element__ with a layer
##########################################################
class __LayerElement__(__Element__, MixinBowl):

    layer = LayerProperty(required = True)
    
    def __init__(self, layer = 0, transformation = None, **kwargs):
        super(__LayerElement__, self).__init__(transformation = transformation, layer = layer, **kwargs)
        
    def __eq__(self, other):
            if other == None:
                    return False
            if (not isinstance(other, __LayerElement__)):
                return False
            if (other.layer.id() != self.layer.id()):
                    return False                
            if (self.shape.transform_copy(self.transformation) != other.shape.transform_copy(other.transformation)):
                    return False
            return True
    
    def __ne__(self,other):
            return not self.__eq__(other)                 
                

##########################################################
# List of elements
##########################################################
class ElementList(TypedList, transformable.NoDistortTransformable):
    __item_type__ = __Element__    

    def dependencies(self):
        from .. import structure
        d = structure.StructureList()
        for e in self:
            d.add(e.dependencies())
        return d

    def size_info(self):
        if len(self) == 0:
            return size_info.SizeInfo()
        else:
            SI = self[0].size_info()
            for e in self[1::]:
                SI += e.size_info()
            return SI

    def convex_hull(self):
        from ...geometry.shape import Shape
        if len(self) == 0:
            return Shape()
        else:
            S = Shape()
            for e in self:
                S += e.convex_hull()
            return S.convex_hull()
        
    def move(self, position):
        for c in self:
            c.move(position)
        return self

    def transform(self, transform):
        for c in self:
            c.transform(transform)
        return self

    def flat_copy(self, level = -1):
        el = ElementList()
        for e in self:
            el += e.flat_copy(level)
        return el

    def is_empty(self):
        if (len(self) == 0): return True
        for e in self:
            if not e.is_empty(): return False
        return True
    
    def append(self, item): #FIXME - TEMPORARY FUNCTION, TO BE REMOVED ONCE THE EXCEPTION ABOUT 'Structure' IS NO LONGER REQUIRED -- DEPRECATED
        from ipkiss.primitives.structure import Structure        
        if isinstance(item, Structure):
            LOG.display_warning("You are trying to add a structure to an ElementList. This is not allowed : only elements can be added to an ElementList", 3)            
            import sys
            sys.exit(-1)
        elif isinstance(item, self.__item_type__):
            list.append(self, item)
        elif isinstance(item, list):
            self.extend(item)            
        else:
            self.__raise_invalid_type_exception__(item)    
     
    
##########################################################
# ElementListProperty
##########################################################

class ElementListProperty(DefinitionProperty):
    __allowed_keyword_arguments__ = ["required","restriction","default","fdef_name"]
    
    def __init__(self, **kwargs):        
        super(ElementListProperty, self).__init__(**kwargs)    
        if ("restriction" in kwargs):
            R = kwargs["restriction"]
            self.restriction = ((RestrictType(ElementList) | RestrictList(restriction = RestrictType(__Element__))) & R) 
        else:
            self.restriction = RestrictType(ElementList) | RestrictList(restriction = RestrictType(__Element__))             
                       
    def __call_getter_function__(self, obj):
        f = self.__get_getter_function__(obj)
        value = f(ElementList())
        if value is None:
            raise IpkissException("Function '%s' returned None : this is invalid." %(f.__name__))
        new_value = self.__cache_property_value_on_object__(obj, value)
        return new_value        
                
ElementsDefinitionProperty = ElementListProperty #DEPRECATED - for backwards compatibility only    


def ElementProperty(internal_member_name = None, restriction = None,  **kwargs):
    """Property for assigning 1 element"""
    R = RestrictType(__Element__) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)


    
    