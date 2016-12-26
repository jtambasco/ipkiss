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

from ipkiss.technology import get_technology
from pysics.materials.all import *
from pysics.electromagnetics import *

TECH = get_technology()
# ------------------------------MATERIALS --------------------------------------------------

material_id_to_epsilon = dict()

def fill_material_id_to_epsilon_map():
    for id, material in MATERIAL_FACTORY.store_id.items():
        material_id_to_epsilon[id] = material.epsilon

def get_epsilon_for_material_id(id):
    try:
        return material_id_to_epsilon[id]
    except KeyError, e:
        fill_material_id_to_epsilon_map()
        return material_id_to_epsilon[id]
    
def transform_material_matrix_in_epsilon_matrix(material_matrix):
    #convert the material matrix to a matrix with epsilon values (doubles)        
    from numpy import vectorize
    f = vectorize(get_epsilon_for_material_id, otypes=[float])
    eps_matrix = f(material_matrix)    
    return eps_matrix

# ------------------------------------------ MATERIAL STACK --------------------------------

material_stack_id_to_effective_index_epsilon = dict()

def fill_material_stack_id_to_effective_index_epsilon_map(material_stack_factory):
    reference_height = None
    material_stack_id_to_effective_index_epsilon.clear()
    for id, material_stack in material_stack_factory:
        material_stack_id_to_effective_index_epsilon[id] = material_stack.effective_index_epsilon

def fill_material_stack_id_to_chi3_map(material_stack_factory):
    reference_height = None
    material_stack_id_to_effective_index_epsilon.clear()
    for id, material_stack in material_stack_factory:
        material_stack_id_to_chi3[id] = material_stack.chi3

def get_effective_index_epsilon_for_material_stack_id(id):
    return material_stack_id_to_effective_index_epsilon[id]
    
def get_chi3_for_material_stack_id(id):
    return material_stack_id_to_chi3[id]
       
def transform_material_stack_matrix_in_effective_index_epsilon_matrix(material_stack_matrix, material_stack_factory):
    #convert the material_stack matrix to a matrix with effective_index_epsilon values (doubles)      
    fill_material_stack_id_to_effective_index_epsilon_map(material_stack_factory)
    from numpy import vectorize
    f = vectorize(get_effective_index_epsilon_for_material_stack_id, otypes=[float])
    effective_index_epsilon_matrix = f(material_stack_matrix)    
    return effective_index_epsilon_matrix

def transform_material_stack_matrix_in_chi3_matrix(material_stack_matrix, material_stack_factory):
    #convert the material_stack matrix to a matrix with effective_index_epsilon values (doubles)       
    fill_material_stack_id_to_chi3_map(material_stack_factory)
    from numpy import vectorize
    f = vectorize(get_chi3_for_material_stack_id, otypes=[float])
    chi3_matrix = f(material_stack_matrix)    
    return chi3_matrix

# ---------------------------------------

material_stack_id_to_epsilon_map = dict() #must be available in global scope
material_stack_id_to_chi3_map = dict() #must be available in global scope

def get_epsilon_for_material_stack_id(id):
    return material_stack_id_to_epsilon_map[id]
    
def transform_material_stack_matrix_in_epsilon_matrix(material_stack_matrix, z_coord, material_stack_factory):
    #make a slice with epsilon-values for a certain z-coordinate
    from numpy import vectorize
    f = vectorize(get_epsilon_for_material_stack_id, otypes=[float])
    #re-initialize the mapping : for every material stack, store the epsilon value that corresponds to the z_coord
    material_stack_id_to_epsilon_map.clear()
    for id, material_stack in material_stack_factory:    
        epsilon = material_stack.get_epsilon_at_z(z_coord)
        material_stack_id_to_epsilon_map[id] = epsilon
    epsilon_matrix = f(material_stack_matrix)    
    return epsilon_matrix

