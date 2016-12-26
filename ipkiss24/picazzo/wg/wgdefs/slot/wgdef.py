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

from ipkiss.plugins.photonics.wg.basic import Wg2ElDefinition
from ipkiss.plugins.photonics.wg.window import WindowWaveguideDefinition, PathWindow
from ipkiss.plugins.photonics.wg.definition import BaseWaveguideDefinition, SingleShapeWaveguideElement, TwoShapeWaveguideElement
from ipkiss.all import *

# Overrules slotted waveguides in ipkiss -> should replace them.
__all__ = ["WgElSlottedDefinition", 
           "Wg2ElSlottedDefinition",
           ]  

class __SlotWgDefinition__(StrongPropertyInitializer):
    wg_width = PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH) 
    slot_width = PositiveNumberProperty(default = TECH.WG.SLOT_WIDTH)
    trench_width = NonNegativeNumberProperty(default=TECH.WG.TRENCH_WIDTH)
    process = ProcessProperty(default = TECH.PROCESS.WG) 
    slot_process = ProcessProperty(default = TECH.PROCESS.WG) 
    
    def transform(self, transformation):
        self.slot_width = transformation.apply_to_length(self.slot_width)
        return super(__SlotWgDefinition__, self).transform(transformation)

class __SlotWgElement__(object):
    wg_width = ReadOnlyIndirectProperty("wg_definition")
    slot_width = ReadOnlyIndirectProperty("wg_definition")
    trench_width = ReadOnlyIndirectProperty("wg_definition")    
    process = ReadOnlyIndirectProperty("wg_definition")    
    slot_process = ReadOnlyIndirectProperty("wg_definition")    
    
    


class WgElSlottedDefinition(__SlotWgDefinition__, WindowWaveguideDefinition):
    """wire-like waveguide definition with a slot in the middle with a trench"""
    # properties are here just to override defaults
    __name_prefix__ = "SLOTWG"
    
    
    def define_windows(self):
        windows = []

        windows.append(PathWindow(layer = PPLayer(self.process, TECH.PURPOSE.LF.LINE),
                           start_offset = -0.5 * self.wg_width,
                           end_offset = 0.5 * self.wg_width))
        windows.append(PathWindow(layer = PPLayer(self.slot_process, TECH.PURPOSE.DF.TRENCH),
                           start_offset = -0.5 * self.slot_width,
                           end_offset = +0.5 * self.slot_width))
        if (self.trench_width > 0.0) :
            windows.append(PathWindow(layer = PPLayer(self.process, TECH.PURPOSE.LF_AREA),
                               start_offset = -0.5 * self.wg_width - self.trench_width,
                               end_offset = +0.5 * self.wg_width + self.trench_width))
        return windows
    
    def __repr__(self):
        return "%s w=%f, s=%f, t=%f, %s" % (self.__name_prefix__,
                                              self.wg_width,
                                              self.slot_width,
                                              self.trench_width,
                                              self.process.extension)    
    
#__WgElSlottedDefinitionPathDefinition__ = WgElSlottedDefinition.__WgElSlottedDefinitionPathDefinition__  #to allow picke/unpickle

class Wg2ElSlottedDefinition(WgElSlottedDefinition):
    """slotted wire with a trench, defined with 2 shapes"""
    __name_prefix__ = "SLOT2WG"
    
    class __Wg2ElSlottedDefinitionPathDefinition__(TwoShapeWaveguideElement, WindowWaveguideDefinition.__WindowWaveguideDefinitionPathDefinition__):
        pass
        
    def define_windows(self):
        windows = []
        windows.append(PathWindow(layer = PPLayer(self.process, TECH.PURPOSE.LF.LINE),
                           start_offset = -0.5 * self.wg_width,
                           end_offset = -0.5 * self.slot_width))
        windows.append(PathWindow(layer = PPLayer(self.process, TECH.PURPOSE.LF.LINE),
                           start_offset = +0.5 * self.slot_width,
                           end_offset = +0.5 * self.wg_width))
        if (self.trench_width > 0.0) :
            windows.append(PathWindow(layer = PPLayer(self.process, TECH.PURPOSE.LF_AREA),
                               start_offset = -0.5 * self.wg_width - self.trench_width,
                               end_offset = +0.5 * self.wg_width + self.trench_width,
                               shape_property_name = "trench_shape"))
        return windows
    

            
    def transform(self, transformation):
        self.trench_width = transformation.apply_to_length(self.trench_width)
        return super(__TrenchDefinition__, self).transform(transformation)        


__Wg2ElSlottedDefinitionPathDefinition__ = Wg2ElSlottedDefinition.__Wg2ElSlottedDefinitionPathDefinition__ #to allow pickle/unpickle

SlottedWaveguideElementDefinition = WgElSlottedDefinition
Slotted2WaveguideElementDefinition = Wg2ElSlottedDefinition 

