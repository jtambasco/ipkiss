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
from ..material.material import MaterialProperty, Material
from ..environment import EnvironmentProperty, DEFAULT_ENVIRONMENT
from ipkiss.geometry.size_info import SizeInfoProperty

__all__ = ["GeometryProperty","CartesianGeometry1D","CartesianGeometry2D","CartesianGeometry3D"]

# Geometry Classes
# This should come in a generic framework
# These geometries returns a material at a given point


class __Geometry__(StrongPropertyInitializer):
    name = StringProperty(allow_none = True)
    
    """ abstract Geometry base class """
    def get_material(self, coordinate):
        raise AssertionError, "__Geometry__ instance or subclass should have material(self, coordinate) method"

    def get_environment(self, coordinate):
        raise AssertionError, "__Geometry__ instance or subclass should have environment(self, coordinate) method"

    def size_info(self):
        raise AssertionError, "__Geometry__ instance or subclass should have size_info() method"
    
    def get_material_array(self, **kwargs):
        raise AssertionError, "__Geometry__ instance or subclass should have get_material_array(self) method"    
    
    def __repr__(self):
        return "<Geometry %s>" % self.name

class Geometry(__Geometry__):
    """ Base class for new geometries """
    
#FIXME - SUBKLASSEN CARTESIAN + POLAR
class __Geometry1D__(__Geometry__):
    """ abstract 1D Geometry base class """
class __Geometry2D__(__Geometry__):
    """ abstract 2D Geometry base class """
class __Geometry3D__(__Geometry__):
    """ abstract 3D Geometry base class """
    
class CartesianGeometry1D(__Geometry1D__):
    size_info = SizeInfoProperty(required = True)

    def define_width(self):
        return self.size_info.width    
    width = NonNegativeNumberProperty(locked = True)
    

class CartesianGeometry2D(__Geometry2D__, CartesianGeometry1D):
    size_info = SizeInfoProperty(required = True)    

    def define_height(self):
        return self.size_info.height
    height = NonNegativeNumberProperty(locked = True)
           
    
    
class CartesianGeometry3D(__Geometry3D__, CartesianGeometry2D):
    size_info = SizeInfoProperty(required = True)    

    def define_thickness(self):
        return self.size_info.thickness
    thickness = NonNegativeNumberProperty(locked = True)
        
    pass


class __UniformMaterialGeometry__(__Geometry__):
    material = MaterialProperty(required = True)

    def get_material(self, coordinate):
        return self.material

class __UniformEnvironmentGeometry__(__Geometry__):
    environment = EnvironmentProperty(default = DEFAULT_ENVIRONMENT)
    
    def get_environment(self, coordinate):
        return self.environment
    
RESTRICT_GEOMETRY = RestrictType(Geometry)
            
def GeometryProperty(internal_member_name= None, restriction = None, preprocess = None, **kwargs):
    """ Geometry property descriptor for a class """ 
    R = RESTRICT_GEOMETRY & restriction
    return RestrictedProperty(internal_member_name = internal_member_name, restriction = R, preprocess = preprocess, **kwargs )
