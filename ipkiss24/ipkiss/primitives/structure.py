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

from .. import settings
from ..geometry import transformable 

from ipcore.properties.descriptor import RestrictedProperty, FunctionNameProperty, DefinitionProperty
from ipcore.properties.predefined import StringProperty, TimeProperty, IdStringProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.initializer import StrongPropertyInitializer, MetaPropertyInitializer
from ..technology.settings import TECH
from .unit_grid import UnitGridContainer
from .elements.basic import ElementList
from .group import __Group__
from .elements.group import Group
import time
import copy
from ipcore.mixin.mixin import MixinBowl
from ipcore.types_list import TypedList


__all__ = ["Structure",
           "StructureList",
           "StructureProperty",
           "StructureListProperty"]
      

class MetaStructureCreator(MetaPropertyInitializer):
    
    """ Meta-class, called when a new structure is created """
    def __call__(cls, *params, **keyword_params):

        # construct a dictionary of only keyword arguments (removes all non-keyword arguments)
        import inspect
        p, a, k, d = inspect.getargspec(cls.__init__)
        if d is None:
            d = []
        kwargs = {}
        for k, v in zip(p[-len(d):], d):
            kwargs[k] = v
        kwargs.update(keyword_params)
        for k, v in zip(p[1:len(params)+1], params):
            kwargs[k] = v
        
        # optional here: perform check if there are no missing arguments
        
        # extract library for the structure
        from . import library 
        from .. import settings
        lib = None
        if 'library' in kwargs:
            lib = kwargs['library']
            del(kwargs['library'])
        if lib is None:
            lib = settings.get_current_library()
            
        # extract the name of the new structure based on the arguments of
        # the constructor. For default structures, the name is passed as the first argument
        S = super(MetaStructureCreator, cls).__call__(**kwargs)
        name = S.name
        
        libstr = lib.__fast_get_structure__(name)
        if libstr is None:
            lib.__fast_add__(S)
            return S
        else:
            #libstr.set_bulk(**kwargs) # TODO: enable set_bulk in (Strong)PropertyInitializer
            del S
            return libstr
            # return the existing object
                     
                  

class ChildStructuresProperty(DefinitionProperty):
    
    def __init__(self, internal_member_name = None, **kwargs):
        kwargs["restriction"] = RestrictType(allowed_types=[list])
        super(ChildStructuresProperty,self).__init__(internal_member_name = internal_member_name, **kwargs)
        
    def __check_restriction__(self, obj, value):
        super(ChildStructuresProperty, self).__check_restriction__(obj, value)
        for v in value:
            if not isinstance(v, Structure):
                raise AttributeError("The list of child structures should contain items of type 'Structure' only.... found an item of type : %s" %type(v))
        
    def __call_getter_function__(self, obj):
        f = self.__get_getter_function__(obj)        
        value = f(StructureList())
        if (value is None):
            value = {}
        self.__cache_property_value_on_object__(obj, value)
        value = self.__get_property_value_of_object__(obj)        
        return value
    
    
class __StructureHierarchy__(StrongPropertyInitializer):
    child_structures = ChildStructuresProperty(doc="The hierarchical child structures of this structure as a dictionary with key = name, value = structure") 
    
    def define_child_structures(self, children):
        return children

    def __eq__(self,other):
    # FIXME: Is not correct.
        if other == None:
            return False
        if not isinstance(other, Structure):
            return False
        myChStrLen = len(self.child_structures)
        otherChStrLen = len(other.child_structures)
        if (myChStrLen != otherChStrLen):
            return False
        else:
            return True
            
    def __ne__(self, other):
        return not self.__eq__(other)    
    
    
class Structure(UnitGridContainer, __StructureHierarchy__, MixinBowl):
    """Base class for a parametric cell"""
    
    __metaclass__ = MetaStructureCreator    
    __name_generator__ = TECH.ADMIN.NAME_GENERATOR    
    created = TimeProperty(doc = "Timestamp when the structure was created (a floating point number expressed in seconds since the epoch, in UTC).")
    modified = TimeProperty(doc = "Timestamp when the structure was modified (a floating point number expressed in seconds since the epoch, in UTC).")
    comment = StringProperty(doc = "User comment string.", default = "")
    
    name = StringProperty(doc = "The unique name of the structure")        
    
    def __init__(self, name = None, elements = None, library = None,  **kwargs):        
        super(Structure, self).__init__(**kwargs)
        if (library is None): 
            library = settings.get_current_library()
        if (not(name is None)):
            self.__dict__["__name__"] = name
            Structure.name.__set__(self, name)
        kwargs['unit'] = library.unit
        kwargs['grid'] = library.grid
        if (not(elements is None)):
            self.elements = ElementList(elements)
        super(Structure, self).__init__(**kwargs)        


    def define_name(self):
        if (not hasattr(self,'__name__')) or (self.__name__ is None):
            self.__name__ = self.__name_generator__(self)          
        return self.__name__
   
    def __cmp__(self, other):
        myname = self.name
        othername = other.name
        if (myname<othername):
            return -1
        elif (myname>othername):
            return 1
        else:
            return 0  
        
    def id_string(self):
        return self.name
    
    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)
    
    

    
def StructureProperty(internal_member_name = None, restriction = None,  **kwargs):
    """Property for assigning a Structure"""
    R = RestrictType(Structure) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)


#############################################################################
## Structure list
#############################################################################

class StructureList(TypedList):
    """A list of Structure objects"""
    
    __item_type__ = Structure
    
    def is_empty(self):
        if (len(self) == 0): return True
        for e in self:
            if not e.is_empty(): return False
        return True

    # overload acces routines to get dictionary behaviour but without using the name as primary key
    def __getitem__(self, key):
        if isinstance(key, str):
            for i in self:
                if i.name == key: return i
            raise IndexError("Structure " + key + " cannot be found in StructureList.")
        else:
            return list.__getitem__(self,key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            for i in range(0, len(self)):
                if self[i].name == key: return list.__setitem__(self, i, value)
            list.append(self, value)
        else:
            return list.__setitem__(self,key, value)

    def __delitem__(self, key):
        if isinstance(key, str):
            for i in range(0, len(self)):
                if self[i].name == key: return list.__delitem__(self,i)
                return
            return list.__delitem__(self,key)
        else:
            return list.__delitem__(self,key)

    def __contains__(self, item):
        if isinstance(item, Structure):
            name = item.name
        else:
            name = item
        if isinstance(name, str):
            for i in self:
                if i.name == name: return True
            return False
        else:
            return list.__contains__(self,item)
        
    def __fast_contains__(self, name):
        for i in self:
            if i.name == name: return True
        return False
        

    def index(self, item):
        if isinstance(item, str):
            for i in range(0, len(self)):
                if list.__getitem__(self, i).name == item:
                    return i
            raise ValueError("Structure " + item + " is not in StructureList")
        else:
            list.index(self, item)

    def __fast_add__(self, new_str):
        """adds a structure wthout checking if it already exists for library and object creation only"""
        list.append(self, new_str)
            
    def add(self, item, overwrite = False):
        if item == None:
            return
        if isinstance(item, Structure):
            if overwrite:
                self[item.name] = item
                return
            elif not self.__fast_contains__(item.name):
                list.append(self, item)
        elif isinstance(item, StructureList) or isinstance(item, list) or isinstance(item, set):
            for s in item:
                self.add(s, overwrite)
        else:
            self.__raise_invalid_type_exception__(item)


    def append(self, other, overwrite = False):
        return self.add(other, overwrite)

    def extend(self, other, overwrite = False):
        return self.add(other, overwrite)


def StructureListProperty(internal_member_name = None, restriction = None,  **kwargs):
    """Property for assigning a StructureList"""
    R = RestrictType(StructureList) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)
 

