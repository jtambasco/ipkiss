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



from picazzo.wg.tapers.linear import WgElTaperLinear 
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.process import ProcessProperty, PPLayer
from ..basic import FiberCoupler
from ipkiss.plugins.photonics.port.port import OpticalPort
from ipkiss.all import *

__all__ = ["InvertedTaper",
           "InvertedTaperShallow",
           "NitrideInvertedTaper",
           "NitrideInvertedTaperShallow"]

###############################################################################
## simple inverted taper (with possible assist features)
###############################################################################
class InvertedTaper(FiberCoupler):
    
    process = ProcessProperty(default = TECH.PROCESS.WG)
    wg_def_start = WaveguideDefProperty(default = WgElDefinition(wg_width = TECH.WG.WIRE_WIDTH,trench_width = TECH.WG.TRENCH_WIDTH))
    wg_def_end = WaveguideDefProperty(default = WgElDefinition(wg_width = 0.080 ,trench_width = 11.46))
    tip_length = PositiveNumberProperty(default = 250.0)
    tip_offset = NonNegativeNumberProperty(default = 300.0)
    nitride_clearance = NonNegativeNumberProperty(default = 50.0)
    nitride_width = PositiveNumberProperty(default = 3.0)
    y_spacing = PositiveNumberProperty(default = 25.0)
    assist_lines = IntProperty(restriction = RESTRICT_NONNEGATIVE, default = 0)
    assist_spacing = PositiveNumberProperty(default = 0.160)
    assist_width = PositiveNumberProperty(default = 0.080)
    extension = NonNegativeNumberProperty(default = 1.0)
    

    def define_elements(self, elems):
        # draw tip

        ## Warning: end-waveguide definition is calculated using y_spacing and tip_width, only wg-width is extracted from wg_def
        
        wg_def_stop = WgElDefinition(wg_width = self.wg_def_end.wg_width, trench_width = 0.5*(self.y_spacing-self.wg_def_end.wg_width)-1.0)
        
        elems += WgElTaperLinear(start_position = (self.tip_length + self.tip_offset, 0.0), 
                           end_position = (self.tip_offset, 0.0), 
                            start_wg_def = self.wg_def_start, 
                            end_wg_def = wg_def_stop)
        if self.extension > 0:
            wg_def = WgElDefinition(wg_width = self.wg_def_end.wg_width, trench_width = 0.5*(self.y_spacing-self.wg_def_end.wg_width)-1.0, process = self.process)
            elems += wg_def([(self.tip_offset - self.extension , 0.0), (self.tip_offset, 0.0)])
        
        #assist lines for tip
        for i in range(self.assist_lines):
            elems += Path(PPLayer(self.process, TECH.PURPOSE.LF.LINE), 
                            [(self.tip_length + self.tip_offset, 0.0 + (0.5*self.tip_start_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)), 
                             (self.tip_offset, 0.0 + (0.5*self.tip_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)),
                             (self.tip_offset - self.extension, 0.0 + (0.5*self.tip_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)),
                             ], self.assist_width)
            elems += Path(PPLayer(self.process, TECH.PURPOSE.LF.LINE), 
                            [(self.tip_length +  self.tip_offset, 0.0 - (0.5*self.tip_start_width+ (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)), 
                            (self.tip_offset, 0.0 - (0.5*self.tip_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)),
                            (self.tip_offset- self.extension, 0.0 - (0.5*self.tip_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)),
                            ], self.assist_width)
        return elems

    def define_ports(self, prts):
        wg_def = WgElDefinition(wg_width = self.wg_def_start.wg_width, trench_width = self.wg_def_start.trench_width, process = self.process)
        prts +=  [OpticalPort(position = (self.tip_length + self.tip_offset, 0.0), angle = 0.0, wg_definition = wg_def)]
        return prts
    

class NitrideInvertedTaper(InvertedTaper):
    nitride_only_length = PositiveNumberProperty(default = 300.0)
    nitride_clearance = PositiveNumberProperty(default = 50.0)
    nitride_width = PositiveNumberProperty(default = 3.0)
    nt_process = ProcessProperty(default = TECH.PROCESS.NT)
    tip_offset = DefinitionProperty(fdef_name = "define_tip_offset")

    def define_tip_offset(self):
        return self.nitride_only_length
        
    def define_elements(self, elems):
        elems += super(NitrideInvertedTaper,self).define_elements(elems)
        # WG
        elems += Line(PPLayer(self.process,TECH.PURPOSE.LF_AREA), 
                        (0.0, 0.0), (self.nitride_only_length - self.extension , 0.0), 
                        self.y_spacing)
        # NT
        elems += Line(PPLayer(self.nt_process, TECH.PURPOSE.LF.LINE), 
                        (0.0, 0.0), (self.nitride_only_length + self.tip_length + 100.0 , 0.0), 
                        self.nitride_width )
        return elems
    


###############################################################################
## inverted taper with extra shallow tip defintion (with possible assist features)
###############################################################################
class InvertedTaperShallow(InvertedTaper):
    process = DefinitionProperty(fdef_name = "define_process")
    
    wg_def_sh_start = WaveguideDefProperty(default = WgElDefinition(wg_width = 1.0 ,trench_width = TECH.WG.TRENCH_WIDTH))
    wg_def_sh_end = WaveguideDefProperty(default = WgElDefinition(wg_width = 0.080 ,trench_width = TECH.WG.TRENCH_WIDTH))

    deep_process = ProcessProperty(default = TECH.PROCESS.WG)
    shallow_process = ProcessProperty(default = TECH.PROCESS.FC)
    shallow_tip_width = PositiveNumberProperty(default = 0.080)
    shallow_tip_start_width = PositiveNumberProperty(default = 1.0)
    shallow_tip_length = PositiveNumberProperty(default = 150.0)


    def define_process(self):
        return self.deep_process
        
    def define_elements(self, elems):
        # WG
        wg_def_stop = WgElDefinition(wg_width = self.wg_def_end.wg_width,trench_width =  self.wg_def_start.trench_width)

        shallow_tip_width = self.wg_def_sh_end.wg_width
        shallow_tip_start_width = self.wg_def_sh_start.wg_width
        elems += WgElTaperLinear(start_position = (self.shallow_tip_length + self.tip_offset + self.tip_length, 0.0), 
                            end_position = (self.tip_offset + self.tip_length, 0.0), 
                            start_wg_def = self.wg_def_start, 
                            end_wg_def = self.wg_def_end)

        # FC
        s_o_length = self.tip_offset + self.tip_length
        # draw taper to tip
        wg_def_sh_start = WgElDefinition(wg_width = self.wg_def_sh_start.wg_width+1.0, trench_width = self.wg_def_start.trench_width)
        wg_def_sh_end = WgElDefinition(wg_width = self.wg_def_sh_end.wg_width, trench_width = 0.5*(self.y_spacing-self.wg_def_sh_end.wg_width)-1.0)
        elems += WgElTaperLinear( start_position = (self.shallow_tip_length + s_o_length, 0.0),
                            end_position =  (s_o_length, 0.0), 
                            start_wg_def = wg_def_sh_start, 
                            end_wg_def = wg_def_sh_end, 
                            process = self.shallow_process)
        if self.extension > 0:
            wg_def = WgElDefinition(wg_width = self.shallow_tip_width, trench_width = 0.5*(self.y_spacing-shallow_tip_width)-1.0, process = self.shallow_process)
            elems += wg_def([(s_o_length - self.extension , 0.0), (s_o_length, 0.0)])
        #assist lines for tip
        for i in range(self.assist_lines):
            elems += Path(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), 
                            [(self.shallow_tip_length + s_o_length, (0.5*shallow_tip_start_width +0.5 + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)), 
                             (s_o_length, + (0.5*shallow_tip_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)),
                             (s_o_length- self.extension , + (0.5*shallow_tip_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width))
                            ], self.assist_width)
            elems += Path(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), 
                            [(self.shallow_tip_length + s_o_length, - (0.5*shallow_tip_start_width+0.5+ (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)), 
                             (s_o_length,  - (0.5*shallow_tip_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width)),
                             (s_o_length- self.extension ,  - (0.5*shallow_tip_width + (i+1)*(self.assist_width+ self.assist_spacing) - 0.5*self.assist_width))
                            ], self.assist_width)
        return elems
            

    def define_ports(self, ports):
        wg_def = WgElDefinition(wg_width = self.shallow_tip_start_width, trench_width = self.wg_def_start.trench_width, process = self.deep_process)
        ports +=  [OpticalPort(position = (self.tip_length + self.tip_offset+ self.shallow_tip_length , 0.0), angle = 0.0, wg_definition = wg_def)]
        return ports
    

class NitrideInvertedTaperShallow(InvertedTaperShallow):
    nitride_only_length = PositiveNumberProperty(default = 300.0)
    nitride_clearance = PositiveNumberProperty(default = 50.0)
    nitride_width = PositiveNumberProperty(default = 3.0)
    nt_process = ProcessProperty(default = TECH.PROCESS.NT)


    def define_elements(self, elems):
        # WG
        elems += Line(PPLayer(self.deep_process,TECH.PURPOSE.LF_AREA), 
                        (0.0, 0.0), (self.nitride_only_length - self.extension , 0.0), 
                        self.y_spacing)
        # FC
        s_o_length = self.tip_offset + self.tip_length
        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), 
                        (0.0, 0.0), (s_o_length- self.extension , 0.0), 
                        self.y_spacing)

        # NT
        elems += Line(PPLayer(self.nt_process, TECH.PURPOSE.LF.LINE), 
                        (0.0, 0.0), (self.nitride_only_length + self.tip_length + self.shallow_tip_length + 50.0 , 0.0), 
                        self.nitride_width )
        return elems


