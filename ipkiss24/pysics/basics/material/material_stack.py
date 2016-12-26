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
from .material import *
from ipkiss.visualisation.display_style import DisplayStyleProperty

class __MaterialStack__(StrongPropertyInitializer):
    pass


class MaterialStack(__MaterialStack__):
    name = StringProperty(required = True, doc = "The name of the material stack")      
    materials_heights = ListProperty(required = True, doc="A list with (material, height) tuples")
    display_style = DisplayStyleProperty(required = False, doc = "A display style for visualisation of the material stack")    
    size_z  = FloatProperty()
    
    def __eq__(self, other):
        if not isinstance(other,MaterialStack):
            return False
        for (smh,omh) in zip(self.materials_heights,other.materials_heights):
            if smh[0]!=omh[0] or abs(smh[1]-omh[1])>1e-6:
                return False
        return True
    
    def get_epsilon_at_z(self, z_coord):
        current_height = 0.0
        for material, height in self.materials_heights:
            current_height = current_height + height
            if current_height > z_coord:
                break
        return material.epsilon            
    
    
    def define_size_z(self):
        z = 0.0
        for m,h in self.materials_heights:
            z = z + h
        return z
    
    def get_number_of_layers(self):
        return len(self.materials_heights)

    def get_numpy_matrix_representation(self):       
        """Make a numpy matrix with for each layer a row that contains:
        StackID | Layer Height | Layer epsilon | number of layers in stack"""
        from ipkiss.technology import get_technology
        TECH = get_technology()
        number_of_heights = self.get_number_of_layers()
        
        nm = numpy.zeros((number_of_heights,4))
        
        for i in range(number_of_heights):
            nm[i,3] = number_of_heights
            nm[i,2] = self.materials_heights[i][0].epsilon
            nm[i,1] = self.materials_heights[i][1]
            nm[i,0] = self.get_unique_id()
            
        return nm
    
    def get_unique_id(self):
        return self.unique_id #FIXME : now set by the material stack factory, but should be done with a uniquely calculated hash
    
    def get_solid_size_z(self):
        """ returns the height of the stack from bottom to top until the forst non-solid material is encountered 
        """
        th = 0
        for m, h in self.materials_heights:
            if m.solid:
                th += h
            else:
                break
        return  th
    
    def __str__(self):
        return self.name
    
    def __add__(self, other):
        if not isinstance(other, MaterialStack):
            raise Exception("Cannot add %s to an object of type MaterialStack.")        
        result_materials_heights = []           
        result_materials_heights.extend(self.materials_heights)
        if (not result_materials_heights[-1][0].solid) and len(other.materials_heights)>0:
            #result_materials_heights[-1] = (other.materials_heights[0][0], result_materials_heights[-1][1] + other.materials_heights[0][1])
            result_materials_heights[-1] = other.materials_heights[0]
            result_materials_heights.extend(other.materials_heights[1:])      
        else:
            result_materials_heights.extend(other.materials_heights)      
        result_display_style = self.display_style.blend(other.display_style)
        result_ms = MaterialStack(materials_heights = result_materials_heights,
                                  display_style = result_display_style,
                                  name = self.name + " + " + other.name)
        return result_ms
    
    def __repr__(self):
        return "<MaterialStack %s>" % self.name
    
    def __hash__(self):
        return hash("".join(["%s_%d" % (m.name, round(d*100000)) for m,d in self.materials_heights]))
            

    def consolidate(self):
        """ generates a copy where all adjacent layers of identical materials are joined """
        
        last_material = self.materials_heights[0][0]
        last_thickness = self.materials_heights[0][1]
        mh = []
        for m, h in self.materials_heights[1:]:
            if m == last_material:
                last_thickness += h
            else:
                mh += [(last_material, last_thickness)]
                last_material = m
                last_thickness = h
        mh += [(last_material, last_thickness)]
        
        
        self.materials_heights = mh
        return self
    
    
    def consolidate_copy(self):
        """ generates a copy where all adjacent layers of identical materials are joined """
        
        last_material = self.materials_heights[0][0]
        last_thickness = self.materials_heights[0][1]
        mh = []
        for m, h in self.materials_heights[1:]:
            if m == last_material:
                last_thickness += h
            else:
                mh += [(last_material, last_thickness)]
                last_material = m
                last_thickness = h
        mh += [(last_material, last_thickness)]
        
        
        ms = MaterialStack(name = self.name,
                           materials_heights = mh,
                           display_style = self.display_style
                           )
        return ms
        
    
class MaterialStackFactory(object):
    id_counter = 1
    store_id = dict()

    def __getitem__(self,key):
        if isinstance(key,int):
            return self.store_id[key]
        else:
            raise Exception("Invalid type of key for accessing an item in MaterialFactory::__get_item__ expects an integer key and got: %s" %str(key))         
        
    def __setattr__(self, key, matstack):
        if (key in self.__dict__):
            current_value = self.__dict__[key]
            if (current_value != matstack):
                    raise IpcoreAttributeException("MaterialStack '%s' was already defined." %(matstack.name))
        self.__dict__[key] = matstack
        self.store_id[self.id_counter] = matstack 
        matstack.unique_id = self.id_counter #FIXME: should be done with a uniquely calculated hash 
        self.__dict__["id_counter"] = self.id_counter + 1       
    
    def get_key_from_material_stack(self, matstack):
        for (k,v) in self.__dict__.items():
            if isinstance(v,MaterialStack) and v == matstack:
                return k
        return None
    
    def get_number_of_material_stacks_in_store(self):
        return len(self.store_id.keys())    
    
    def get_numpy_matrix_representation_of_all_material_stacks(self):
        """Make a numpy matrix with for each layer in each material stack a row that contains:
        StackID | Layer Height | Layer epsilon | number of layers in stack"""
        
        number_of_items = self.get_number_of_material_stacks_in_store()
        
        #first iteration: find out how many rows should be included
        total_number_of_layers = 0
        for key in self.store_id.keys():
            total_number_of_layers += self.store_id[key].get_number_of_layers()
        
        #create numpy matrix
        nm = numpy.zeros((total_number_of_layers,4))
        
        #second iteration: add contributions to final matrix
        current_row_index = 0        
        for key in self.store_id.keys():
            mat_stack = self.store_id[key]
            number_of_layers = mat_stack.get_number_of_layers()
            nm[current_row_index:(current_row_index+number_of_layers),:] = mat_stack.get_numpy_matrix_representation()
            current_row_index += number_of_layers
            
        return nm
            
    def clear(self):
        self.store_id.clear()
        self.id_counter = 1
        
    def get_material_stack_id(self, material_stack):
        for (i,mstack) in self.store_id.items():
            if mstack == material_stack:
                return i
        raise Exception("Material stack with id = %i not found." %material_stack)
    
    def __iter__(self):
        return self.store_id.iteritems()
    


