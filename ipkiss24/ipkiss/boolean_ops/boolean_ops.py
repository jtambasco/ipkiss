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

class __ShapeBooleanOpsAspect__(__Aspect__):
    
    def __sub__(self, shape):
        raise Exception("Method __sub__ not implemented in abstract class __ShapeBooleanOpsAspect__")
    
    def __and__(self, shape):
        raise Exception("Method __and__ not implemented in abstract class __ShapeBooleanOpsAspect__")
    
    def __or__(self, shape):
        raise Exception("Method __or__ not implemented in abstract class __ShapeBooleanOpsAspect__")
    
    def sub(self, shape):
        return self.__sub__(shape)
        
    def xor(self, shape):        
        return self.__xor__(shape)    
    
    

class __BoundaryBooleanOpsAspect__(__Aspect__):
    
    def __sub__(self, elem):
        raise Exception("Method __sub__ not implemented in abstract class __ShapeElementBooleanOpsAspect__")
    
    def __and__(self, elem):
        raise Exception("Method __and__ not implemented in abstract class __ShapeElementBooleanOpsAspect__")
    
    def __or__(self, elem):
        raise Exception("Method __or__ not implemented in abstract class __ShapeElementBooleanOpsAspect__")
    
    def sub(self, elem):
        return self.__sub__(elem)
        
    def xor(self, elem):        
        return self.__xor__(elem)    
    
    
    
    
    