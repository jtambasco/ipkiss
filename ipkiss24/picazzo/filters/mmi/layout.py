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

from picazzo.container.taper_ports import TaperDeepPorts, TaperShallowPorts
from ipkiss.plugins.photonics.port.port import InOpticalPort, OutOpticalPort
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.all import *
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty, WaveguideDefListProperty

__all__ = ["MmiUniformWgWidth",
           "Mmi",
           "MmiTapered",
           "Mmi1x2",
           "Mmi1x2Tapered",
           "Mmi2x1Tapered",
           "Mmi2x2",
           "Mmi2x2Tapered",
           "MmiTaperPorts",
           "__MmiTaperPorts__",
           "__MmiSymmetric__"]  


class MmiBasic(Structure):
    """ rectangular multimode interferometer, generated from a waveguide definition"""
    __name_prefix__ = "mmib"
    mmi_wg_definition = WaveguideDefProperty(required = True, doc = "waveguide definition used to define the MMI core")
    input_wg_definitions = WaveguideDefListProperty(default = [], doc= "waveguide definitions of the inputs")
    output_wg_definitions = WaveguideDefListProperty(default = [], doc= "waveguide definitions of the outputs")
    input_y_positions = RestrictedProperty(restriction = RestrictList(RESTRICT_NUMBER), default = [])
    output_y_positions = RestrictedProperty(restriction = RestrictList(RESTRICT_NUMBER), default = [])
    length = PositiveNumberProperty(required = True)
    
    def define_elements(self, elems):
        elems += self.mmi_wg_definition(shape = [(0.0, 0.0), (self.length, 0.0)])
        return elems
    
    def define_ports(self, ports):
        for wd, y in zip(self.input_wg_definitions, self.input_y_positions):
            ports += InOpticalPort(wg_definition = wd, position = (0.0, y), angle = 180.0)
        for wd, y in zip(self.output_wg_definitions, self.output_y_positions):
            ports += OutOpticalPort(wg_definition = wd, position = (self.length, y), angle = 0.0)
        return ports
    
class MmiUniformWgWidth(MmiBasic):
    __name_prefix__ = "mmibuwgp"
    """ rectangular multimode interferometer, generated from a waveguide definition with uniform input and output waveguide definitions"""
    input_wg_definitions = DefinitionProperty(fdef_name = "define_input_wg_definitions")
    output_wg_definitions = DefinitionProperty(fdef_name = "define_output_wg_definitions")
    wg_definition = WaveguideDefProperty(default=TECH.WGDEF.WIRE, doc = "waveguide definition for input and output waveguides")
                        
    def define_input_wg_definitions(self):
        return [self.wg_definition for y in self.input_y_positions]
    
    def define_output_wg_definitions(self):
        return [self.wg_definition for y in self.output_y_positions]
        
def MmiTaperedBasic(width, 
                    length, 
                    input_y_positions, 
                    output_y_positions, 
                    input_taper_widths, 
                    output_taper_widths, 
                    taper_length, 
                    wg_definition = TECH.WGDEF.WIRE,
                    **kwargs):
    """ a deep-etch rectangular MMI with tapers  """
    mmi_wg_definition = WgElDefinition(wg_width = width, process = wg_definition.process, trench_width = wg_definition.trench_width)
    input_taper_definitions = []
    for i in range(len(input_taper_widths)):
        input_taper_definitions += [WgElDefinition(wg_width = input_taper_widths[i], process = wg_definition.process, trench_width = wg_definition.trench_width)]
    output_taper_definitions = []
    for i in range(len(output_taper_widths)):
        output_taper_definitions += [WgElDefinition(wg_width = output_taper_widths[i], process = wg_definition.process, trench_width = wg_definition.trench_width)]
    M = MmiBasic(mmi_wg_definition = mmi_wg_definition, 
                 length = length, 
                 input_y_positions = input_y_positions, 
                 output_y_positions = output_y_positions, 
                 input_wg_definitions = input_taper_definitions, 
                 output_wg_definitions = output_taper_definitions, **kwargs)
    return TaperDeepPorts(structure = M, taper_length = taper_length, end_wg_def = wg_definition)

class Mmi(MmiUniformWgWidth):
    """ MmiUniformWgWidth with standard input and output wg definitions"""
    width = NonNegativeNumberProperty(required=True)
    mmi_wg_definition = WaveguideDefProperty(doc = "waveguide definition used to define the MMI core")
    
    def define_mmi_wg_definition(self):
        return WgElDefinition(wg_width = self.width, process = self.wg_definition.process, trench_width = self.wg_definition.trench_width)

class __MmiTaperPorts__(object):
    width = NonNegativeNumberProperty(required=True)
    length = NonNegativeNumberProperty(required=True)
    structure = StructureProperty(required = False, fdef_name = 'define_structure')
    input_y_positions = RestrictedProperty(restriction = RestrictList(RESTRICT_NUMBER), default = [])
    output_y_positions = RestrictedProperty(restriction = RestrictList(RESTRICT_NUMBER), default = [])
    taper_width = NonNegativeNumberProperty(required=True)
    straight_extension = Size2Property(default = (0.0,TECH.TECH.MINIMUM_LINE))
    
class MmiTaperPorts(TaperDeepPorts):
    """ a deep-etch generic MMI with tapers  """
    pass


class MmiTapered(__MmiTaperPorts__,MmiTaperPorts):    
    
    def define_structure(self):        
        twg = WgElDefinition(wg_width = self.taper_width, process = self.end_wg_def.process, 
                             trench_width = self.end_wg_def.trench_width)
        
        return Mmi(width = self.width,
                   length = self.length, 
                   input_y_positions = self.input_y_positions, 
                   output_y_positions = self.output_y_positions, 
                   wg_definition = twg)

class __MmiSymmetric__(object):
    wg_offset = NonNegativeNumberProperty(required=True)
    
class Mmi1x2(__MmiSymmetric__,Mmi):
    def define_input_y_positions(self):
        return [0.0]
    def define_output_y_positions(self):
        return [-self.wg_offset, self.wg_offset]

class Mmi2x1(__MmiSymmetric__,Mmi):
    def define_input_y_positions(self):
        return [-self.wg_offset, self.wg_offset]
    def define_output_y_positions(self):
        return [0.0]

class Mmi2x2(__MmiSymmetric__,Mmi):
    def define_input_y_positions(self):
        return [-self.wg_offset, self.wg_offset]
    def define_output_y_positions(self):
        return [-self.wg_offset, self.wg_offset]

class Mmi1x2Tapered(__MmiSymmetric__,MmiTapered):    
    def define_input_y_positions(self):
        return [0.0]
    def define_output_y_positions(self):
        return [-self.wg_offset, self.wg_offset]
    
class Mmi2x1Tapered(__MmiSymmetric__,MmiTapered):    
    def define_input_y_positions(self):
        return [-self.wg_offset, self.wg_offset]
    def define_output_y_positions(self):
        return [0.0]
    
class Mmi2x2Tapered(__MmiSymmetric__,MmiTapered):
    def define_input_y_positions(self):
        return [-self.wg_offset, self.wg_offset]
    def define_output_y_positions(self):
        return [-self.wg_offset, self.wg_offset]  
