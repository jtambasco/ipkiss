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

from ipkiss.all import *
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from picazzo.container.taper_ports import TaperDeepPorts, TaperShallowPorts

__all__ = ["ShallowMmi",
           "ShallowMmi1x2Tapered",
           "ShallowMmi2x1Tapered",
           "ShallowMmi2x2Tapered",
           "ShallowMmiTapered",
           "ShallowMmiTaperPorts",
           "ShallowMmiTaperedBasic"]


def ShallowMmiTaperedBasic(width, 
                           length, 
                           input_y_positions, 
                           output_y_positions, 
                           input_taper_widths , 
                           output_taper_widths, 
                           taper_length, 
                           wg_definition = TECH.WGDEF.FC_WIRE,
                           **kwargs):
    """ a shallow-etch rectangular MMI with tapers  """
    mmi_wg_definition = WgElDefinition(wg_width = width, process = wg_definition.process, trench_width = wg_definition.trench_width)
    input_taper_definitions = []
    for i in range(len(input_taper_widths)):
        input_taper_definitions += [WgElDefinition(wg_width = input_taper_widths[i], process = wg_definition.process, trench_width = wg_definition.trench_width)]
    output_taper_definitions = []
    for i in range(len(output_taper_widths)):
        output_taper_definitions += [WgElDefinition(wg_width = output_taper_widths[i], process = wg_definition.process, trench_width = wg_definition.trench_width)]
    from picazzo.filters.mmi.layout import MmiBasic
    M = MmiBasic(mmi_wg_definition = mmi_wg_definition, 
                 length = length, 
                 input_y_positions = input_y_positions, 
                 output_y_positions = output_y_positions, 
                 input_wg_definitions = input_taper_definitions, 
                 output_wg_definitions = output_taper_definitions, **kwargs)
    return ShallowMmiTaperPorts(structure = M, taper_length = taper_length, end_wg_def = wg_definition)   

from picazzo.filters.mmi import MmiUniformWgWidth
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty 

class ShallowMmi(MmiUniformWgWidth):
    width = NonNegativeNumberProperty(required=True)
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.FC_WIRE)
    mmi_wg_definition = WaveguideDefProperty(doc = "waveguide definition used to define the MMI core")
    
    def define_mmi_wg_definition(self):
        return WgElDefinition(wg_width = self.width, process = self.wg_definition.process, trench_width = self.wg_definition.trench_width)
        

class ShallowMmiTaperPorts(TaperShallowPorts):
    """ a shallow-etch generic MMI with tapers  """

    def define_elements(self, elems):
        super(ShallowMmiTaperPorts, self).define_elements(elems)
        # WG: corrections for sharp angles...
        E = max(self.straight_extension[0], TECH.TECH.MINIMUM_LINE)  # deep taper extension
        TL = 0.5*self.taper_length  # deep taper length

        i_y = [p.position.y for p in self.structure.in_ports.y_sorted()]
        x_i = -TL + E
        for (y1, y2) in zip(i_y[:-1], i_y[1:]):
            y_excess = self.deep_only_width + TECH.TECH.MINIMUM_SPACE - (y2 - y1) 
            if y_excess > 0:
                average = 0.5*(y1 + y2)
                L = y_excess * TL  / (self.deep_only_width - self.end_wg_def.wg_width) + E
                elems += Line(PPLayer(self.deep_process,TECH.PURPOSE.LF.LINE), (x_i, average), (x_i-L, average), TECH.TECH.MINIMUM_SPACE + 0.14)

        x_o = self.structure.length + TL - E
        o_y = [p.position.y  for p in self.structure.out_ports.y_sorted()]
        for (y1,y2) in zip(o_y[:-1], o_y[1:]):
            y_excess = self.deep_only_width + TECH.TECH.MINIMUM_SPACE - (y2 - y1) 
            if y_excess > 0:
                average = 0.5*(y1 + y2)
                L = y_excess * TL / (self.deep_only_width - self.end_wg_def.wg_width) + E
                elems += Line(PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), (x_o, average), (x_o+L, average), TECH.TECH.MINIMUM_SPACE + 0.14)

        # Light field inversion layer
        elems += Line(PPLayer(self.deep_process, TECH.PURPOSE.DF_AREA), (x_i, 0), (x_o, 0), self.structure.mmi_wg_definition.wg_width + self.structure.mmi_wg_definition.trench_width)
        return elems 

from ..mmi import __MmiTaperPorts__

class ShallowMmiTapered(__MmiTaperPorts__,ShallowMmiTaperPorts):
    shallow_wg_definition = WaveguideDefProperty(default = TECH.WGDEF.FC_WIRE)
    
    def define_structure(self):        
        twg = WgElDefinition(wg_width = self.taper_width, process = self.shallow_wg_definition.process, 
                             trench_width = self.shallow_wg_definition.trench_width)
        
        return ShallowMmi(width = self.width,
                          length = self.length, 
                          input_y_positions = self.input_y_positions, 
                          output_y_positions = self.output_y_positions, 
                          wg_definition = twg)

from ..mmi import __MmiSymmetric__    

class ShallowMmi1x2Tapered(__MmiSymmetric__,ShallowMmiTapered):    
    def define_input_y_positions(self):
        return [0.0]
    def define_output_y_positions(self):
        return [-self.wg_offset, self.wg_offset]
    
class ShallowMmi2x1Tapered(__MmiSymmetric__,ShallowMmiTapered):
    def define_input_y_positions(self):
        return [-self.wg_offset, self.wg_offset]
    def define_output_y_positions(self):
        return [0.0]
    
    
class ShallowMmi2x2Tapered(__MmiSymmetric__,ShallowMmiTapered):
    def define_input_y_positions(self):
        return [-self.wg_offset, self.wg_offset]
    def define_output_y_positions(self):
        return [-self.wg_offset, self.wg_offset]  
