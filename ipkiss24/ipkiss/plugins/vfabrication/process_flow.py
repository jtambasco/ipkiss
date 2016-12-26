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
from ipkiss.process import ProcessLayer
from pysics.basics.material.material_stack import MaterialStack, MaterialStackFactory

class VFabricationProcessFlow(StrongPropertyInitializer):
    active_processes = RestrictedListProperty(required = True, allowed_types=[ProcessLayer], doc="Full list of all the processes relevant for virtual fabrication")    
    process_to_material_stack_map = RestrictedListProperty(required = True, allowed_types=[tuple], doc="Mapping from physical process to material stack")
    is_lf_fabrication = DictProperty(required = True, doc="Dict indicating for every process with True/False if it is fabricated in LF")
    
    def __add__(self, other):
        from ipkiss.all import get_technology
        TECH = get_technology()
        return self.add(other, material_stack_factory = TECH.MATERIAL_STACKS)
    
    def add(self, other, material_stack_factory):
        if not isinstance(other, VFabricationProcessFlow):
            raise Exception("Cannot add %s to an object of type VFabricationProcessFlow.")
        #active processes
        result_active_processes = []
        result_active_processes.extend(self.active_processes)
        result_active_processes.extend(other.active_processes)
        #process_to_material_stack_map
        from ipkiss.technology import get_technology
        TECH = get_technology()
        result_process_to_material_stack_map = []
        for (my_process_indicators, my_material_stack) in self.process_to_material_stack_map:
            for (other_process_indicators, other_material_stack) in other.process_to_material_stack_map:
                result_process_indicators = list(my_process_indicators) + list(other_process_indicators)
                result_material_stack = my_material_stack + other_material_stack
                setattr(material_stack_factory, 
                        "MSTACK_%s_%s" %(str(do_hash(my_material_stack)),str(do_hash(other_material_stack))),
                        result_material_stack)                        
                result_process_to_material_stack_map.append((result_process_indicators, result_material_stack))
        #is_lf_fabrication
        result_is_lf_fabrication = dict()
        result_is_lf_fabrication.update(self.is_lf_fabrication)
        result_is_lf_fabrication.update(other.is_lf_fabrication)
        #final result
        result_process = VFabricationProcessFlow(active_processes = result_active_processes,
                                                 process_to_material_stack_map = result_process_to_material_stack_map,
                                                 is_lf_fabrication = result_is_lf_fabrication)
        return result_process
            
        
        
        
    
def VFabricationProcessFlowProperty(internal_member_name = None, restriction = None,  **kwargs):
    """Property for VFabricationProcessFlow"""
    R = RestrictType(VFabricationProcessFlow) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)    