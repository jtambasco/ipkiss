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
from ipkiss.all import Structure, get_technology
from ipkiss.process import PPLayer
from ipkiss.primitives.elements.basic import ElementList, ElementListProperty
from ipkiss.boolean_ops.boolean_ops_elements import get_elements_for_generated_layers


TECH=get_technology()


class __ElementsForVFabricationAspect__(__Aspect__):
    elements_per_active_process = ElementListProperty()

    def define_elements_per_active_process(self, elems):      
        """
        Convert the structure's elements into a new set of elements for every active process, as defined by TECH.VFABRICATION.PROCESS_FLOW.
        """
        elems = self.__get_elements_per_process__(processes = TECH.VFABRICATION.PROCESS_FLOW.active_processes)
        return elems

    def __get_elements_per_process__(self, processes):  
        """
        For a given TECH.PPLAYER.XX, calculate the composite elements according to the GeneratedLayer in TECH.PPLAYER.XX.ALL
        and generate a Boundary on layer TECH.PPLAYER.XX.TEXT
        """
        mapping = dict()
        elems = ElementList()
        for process in processes:	    
            if hasattr(TECH.PPLAYER,process.extension) and hasattr(TECH.PPLAYER.__getattribute__(process.extension),"ALL"):
                pplayer = TECH.PPLAYER.__getattribute__(process.extension).__getattribute__("TEXT")
                mapping[TECH.PPLAYER.__getattribute__(process.extension).ALL] = pplayer
        elems += get_elements_for_generated_layers(self.elements, mapping = mapping)
        return elems

    def write_gdsii_vfabrication(self, filename_or_stream, **kwargs):
        struct_vfab = Structure(name = self.name+"_VFAB", elements = self.elements_per_active_process)
        struct_vfab.write_gdsii(filename_or_stream, **kwargs)   




Structure.mixin_first(__ElementsForVFabricationAspect__)





