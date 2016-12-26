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

from ..geometry import size_info
import copy
from ipcore.properties.initializer import StrongPropertyInitializer, MetaPropertyInitializer
from ipcore.properties.descriptor import FunctionProperty
from .elements.basic import __Element__, ElementList, ElementListProperty
from ipcore.caching.cache import cache
__all__ = []

##########################################################
# group of elements
##########################################################
class __Group__(StrongPropertyInitializer):  
    
    elements = ElementListProperty(fdef_name = "define_elements")           
    
    def define_elements(self, elems):
        result = ElementList()
        return result

    @cache()
    def dependencies(self):
        return self.elements.dependencies()    

    def append(self, element):
        '''append 1 item to the list of elements'''
        myElems = self.elements
        myElems.append(element)
        self.elements = myElems
        
    def extend(self, elems):
        '''extend the list of elements with a list of elements'''
        from ..primitives.elements.group import Group
        myElems = self.elements        
        if isinstance(elems, Group):
            myElems.extend(elems.elements)
        else:
            myElems.extend(elems)
        self.elements = myElems  
        
    def __iadd__(self, element):
        ''' for external additions: add element and reduce the class to a simple compound element'''
        if isinstance(element, list):
            self.extend(element)
        elif isinstance(element, __Element__): 
            self.append(element)
        elif element is None:
            return self
        else:
            raise TypeError("Invalid type " + str(type(element)) + " in __Group__.__iadd__().")
        return self
    
    def add_el(self, elems):
        """ add an element """
        self.elements +=  elems           

    def size_info(self):
        return self.elements.size_info()

    def convex_hull(self):
        return self.elements.convex_hull()

    def flatten(self, level = -1):     
        self.elements = self.elements.flat_copy(level = level)
        return self
    
    def __iter__(self):
        return self.elements.__iter__()

    def is_empty(self):   
        return self.elements.is_empty()
    
    def __eq__(self,other):
        if other == None:
            return False
        if not isinstance(other, Structure):
            return False
        myElements = self.elements        
        otherElements = other.elements        
        myLen = len(myElements)
        otherLen = len(otherElements)
        if (myLen != otherLen):
            return False
        for myElem, otherElem in zip(myElements,otherElements):         
            if (myElem != otherElem):
                return False
        return True
            
    def __ne__(self, other):
        return not self.__eq__(other)    
    

        