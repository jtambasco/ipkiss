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



from .w1 import generic_W1_waveguide, generic_W1_waveguide_section
from ipkiss.all import *

__all__ = ["W1HeteroCavity", "W1HeteroCavityMulti"]

class W1HeteroCavity1Mirror(Structure):
    __name_prefix__ = "W1HC"
    mirror_unit_cell = StructureProperty(required = True)
    cavity_unit_cell = cavity_unit_cell(required = True)
    n_o_cladding_layers = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    n_o_mirror_periods = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    n_o_cavity_periods = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    mirror_pitch = PositiveNumberProperty(required= True)
    cavity_pitch = PositiveNumberProperty(required= True)
    process_wg = ProcessProperty(default = TECH.PROCESS.WG)
    process_hfw = ProcessProperty(default = TECH.PROCESS.WG)
    mirror = DefinitionProperty(fdef_name = "define_mirror")
    cavity = DefinitionProperty(fdef_name = "define_cavity")
    mirror_pos = DefinitionProperty(fdef_name = "define_mirror_pos")
    cavity_pos = DefinitionProperty(fdef_name = "define_cavity_pos")
    

    def define_name(self):
        return "%s_MA%d_CA%d_MU%d_CU%d_C%d_ML%d_CL%d_%s_%s" % (
                self.__name_prefix__,
                self.mirror_pitch*1000,
                self.cavity_pitch*1000,
                do_hash(self.mirror_unit_cell.name),
                do_hash(self.cavity_unit_cell.name),
                self.n_o_cladding_layers,
                self.n_o_mirror_periods,
                self.n_o_cavity_periods,
                self.process_wg.extension,
                self.process_hfw.extension
                )
       
    def define_mirror(self):
        return generic_W1_waveguide_section((self.mirror_pitch, self.mirror_pitch), self.mirror_unit_cell, self.n_o_cladding_layers, self.n_o_mirror_periods, process_wg = self.process_wg, process_hfw = self.process_hfw)
    
    def define_cavity(self):
        return generic_W1_waveguide((self.cavity_pitch, self.mirror_pitch), self.cavity_unit_cell, self.n_o_cladding_layers, self.n_o_cavity_periods, process_wg = self.process_wg, process_hfw = self.process_hfw)
    
    def define_mirror_pos(self):
        return Coord2(0.0, 0.0)
    
    def define_cavity_pos(self):
        return Coord2(self.mirror_pitch * (self.n_o_mirror_periods) - 0.5*(self.mirror_pitch - self.cavity_pitch) , 0.0)
            
    def define_elements(self, elems):
        elems += SRef(self.mirror, self.mirror_pos)
        elems += SRef(self.cavity, self.cavity_pos)
        return elems
    
    def define_ports(self, ports):
        return self.mirror.west_ports.move_copy(self.mirror_pos) +  self.cavity.east_ports.move_copy(self.mirror_pos) 


class W1HeteroCavity(W1HeteroCavity1Mirror):
    __name_prefix__ = "W1HC"
    mirror_pos2 = DefinitionProperty(fdef_name = "define_mirror_pos2")
    termination = DefinitionProperty(fdef_name = "define_termination")
    termination_pos = DefinitionProperty(fdef_name = "define_termination_pos")    

    def define_mirror_pos2(self):
        return Coord2(self.mirror_pitch * (2*self.n_o_mirror_periods-1) + self.cavity_pitch * self.n_o_cavity_periods, 0.0)
    
    def define_termination(self):
        return generic_W1_waveguide_termination((self.mirror_pitch, self.mirror_pitch), self.mirror_unit_cell, self.n_o_cladding_layers, process_wg = self.process_wg, process_hfw = self.process_hfw)

    def define_termination_pos(self):        
        return [coord2_match_position(self.termination.east_ports[0], self.mirror.west_ports[0].move_copy(self.mirror_pos) ),
                     coord2_match_position(self.termination.east_ports[0], self.mirror.west_ports[0].h_mirror_copy().move(self.mirror_pos2)) ]
    
    def define_elements__(self, elems):
        elems += SRef(self.mirror, self.mirror_pos2, HMirror()) 
        elems += SRef(self.termination, self.termination_pos[0]) 
        elems += SRef(self.termination, self.termination_pos[1]) 
        return elems
            
    def define_ports(self, ports):
        W = self.mirror_unit_cell.size_info().width        
        ports += (self.termination.west_ports.move_copy(self.termination_pos[0] - (self.mirror_pitch - 0.5*W, 0.0)) + 
                      self.termination.east_ports.move_copy(self.termination_pos[1] + (self.mirror_pitch - 0.5*W, 0.0)))
        return ports


class W1HeteroCavityMulti(W1HeteroCavity):
    __name_prefix__ = "W1HC1"
    n_o_cavities = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    define_cavity_period = DefinitionProperty(fdef_name = "define_cavity_period")

    
    def define_name(self):
        return "%s_MA%d_CA%d_MU%d_CU%d_C%d_ML%d_CL%d_N%d_%s_%s" % (
                self.__name_prefix__,
                self.mirror_pitch*1000,
                self.cavity_pitch*1000,
                do_hash(self.mirror_unit_cell.name),
                do_hash(self.cavity_unit_cell.name),
                self.n_o_cladding_layers,
                self.n_o_mirror_periods,
                self.n_o_cavity_periods,
                self.n_o_cavities,
                self.process_wg.extension,
                self.process_hfw.extension
                )    
    
    def define_cavity_period(self):
        return self.mirror_pitch * (self.n_o_mirror_periods-0.5) + self.cavity_pitch * (self.n_o_cavity_periods-0.5)

    def define_elements(self, elems):
        M = generic_W1_waveguide_section((self.mirror_pitch, self.mirror_pitch), self.mirror_unit_cell, self.n_o_cladding_layers, self.n_o_mirror_periods, process_wg = self.process_wg, process_hfw = self.process_hfw)
        C = generic_W1_waveguide((self.cavity_pitch, self.mirror_pitch), self.cavity_unit_cell, self.n_o_cladding_layers, self.n_o_cavity_periods, process_wg = self.process_wg, process_hfw = self.process_hfw)
        p = -self.cavity_period
        elems += SRef(self.termination, self.termination_pos[0]) 
        for i in range(self.n_o_cavities):
            p += self.cavity_period 
            elems += SRef(self.mirror, self.mirror_pos + (p, 0.0))
            elems += SRef(self.cavity, self.cavity_pos + (p, 0.0))
        elems += SRef(self.mirror, self.mirror_pos2 + (p, 0.0), HMirror()) 
        elems += SRef(self.termination, self.termination_pos[1] + (p, 0.0)) 
        return elems
    
    
    def define_ports(self, ports):
        W = self.mirror_unit_cell.size_info().width
        ports = (self.termination.west_ports.move_copy(self.termination_pos[0] - (self.mirror_pitch - 0.5*W, 0.0)) + 
                      self.termination.east_ports.move_copy(self.termination_pos[1] + (self.cavity_period * (self.n_o_cavities-1), 0.0) +(self.mirror_pitch - 0.5*W, 0.0))
                    )
        return ports


