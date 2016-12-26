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
from ipkiss.visualisation.display_style import DisplayStyleProperty

__all__ = ["BlendedMaterial", 
           "MaterialProperty",
           "RESTRICT_MATERIAL",
           "Material"
           ]

### Material classes
### this should be the basis for multiphysics
class __Material__(StrongPropertyInitializer):
    """ abstract material class base class which should be the basis for Other material 
        Material classes should support multiple inheritance to 
        make materials with complex beehaviour and multiphysics(e.g. thermo-optic).
        Default behaviour of all properties should be vacuum
        """       

class Material(__Material__):
    """ Base material. all other materials should subclass from this """
    name = StringProperty(required = True, doc = "The name of the material")        
    display_style = DisplayStyleProperty(required = False, doc = "A display style for visualisation of the material in plots")
    solid = BoolProperty(default = True, doc="Indicates if a material is solid, e.g. air is not solid and silicon is solid")
    
    def __repr__(self):
        return "<Material %s>" % self.name
    
    def __eq__(self, other):
        # simple comparison based on name. Subclasses can make it more complex
        return isinstance(other,Material) and self.name == other.name
    
    def __neq__(self, other):
        return (not isinstance(other,Material)) or self.name != other.name
    
class MaterialFactory(object):
    id_counter = 1
    store_id = dict() #key = the binary id of the material
    
    def get_number_of_materials_in_store(self):
        return len(self.store_id.keys())
    
    def __getitem__(self,key):
        if isinstance(key,int):
            return self.store_id[key]
        else:
            raise Exception("Invalid type of key for accessing an item in MaterialFactory::__get_item__ expects an integer key and got: %s" %str(key))         
        
    def __setattr__(self, key, mat):
        if (key in self.__dict__):
            current_value = self.__dict__[key]
            if (current_value != mat):
                    raise IpcoreAttributeException("Material '%s' was already defined." %(mat))
        self.__dict__[key] = mat
        self.store_id[self.id_counter] = mat 
        self.__dict__["id_counter"] = self.id_counter + 1 
        
    def __iter__(self):
        return self.store_id.iteritems()        
        
    def find_item_key(self, item):
        for k,v in self.__dict__.items():
            if isinstance(v,Material) and v == item:
                return k
                
RESTRICT_MATERIAL = RestrictType(Material)


def MaterialProperty(internal_member_name= None, restriction = None, preprocess = None, **kwargs):
    """ Material property descriptor for a class """ 
    R = RESTRICT_MATERIAL & restriction
    return RestrictedProperty(internal_member_name = internal_member_name, restriction = R, preprocess = preprocess, **kwargs )


class BlendedMaterial(Material):
    """ Material consisting of a linear combination of 2 other materials.
        Any property will consist of a linear combination of both materials. """
    
    material_1 = MaterialProperty(required = True)
    material_2 = MaterialProperty(required = True)
    fraction = FractionProperty(default = 0.5)
    
    def __init__(self, **kwargs):
        name_1 = self.material_1.name
        name_2 = self.material_2.name
        kwargs["name"] = "Blend of material %s and %s" %(name_1, name_2)
        super(BlendedMaterial, self).__init__(**kwargs)        

    # TODO: Think about a way to mix all material properties automatically. 
    # Now every sublibrary needs to mixin here by itself.
    
