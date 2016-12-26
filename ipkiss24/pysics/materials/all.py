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

from pysics.basics.material.material import *
from pysics.basics.material.material_stack import *
from ipkiss.visualisation.display_style import *
from ipkiss.visualisation.color import *
from ipkiss.technology import get_technology

TECH = get_technology()


# -- define the notion of "solid height" for a materialstack: this is the height of all the solid material

def calculate_solid_height(stack):
    solid_height = 0.0
    check_that_no_solid_materials_follow = False
    for material, height in stack.materials_heights:
        if (material == TECH.MATERIALS.AIR):
            break 
        else:
            solid_height = solid_height + height
    return solid_height

MaterialStack.define_solid_height = calculate_solid_height

MaterialStack.solid_height = DefinitionProperty(fdef_name = "define_solid_height")

material_stack_id_to_solid_height_map = dict()

def get_solid_height_for_material_stack_id(id):
    return material_stack_id_to_solid_height_map[id]

def transform_material_stack_matrix_in_solid_height_matrix(material_stack_matrix):
    from numpy import vectorize
    f = vectorize(get_solid_height_for_material_stack_id, otypes=[float])
    #re-initialize the mapping : for every material stack, store the epsilon value that corresponds to the z_coord
    material_stack_id_to_solid_height_map.clear()
    for id, material_stack in TECH.MATERIAL_STACKS:    
        material_stack_id_to_solid_height_map[id] = material_stack.solid_height
    sh_matrix = f(material_stack_matrix)    
    return sh_matrix

