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
from ipkiss.plugins.photonics.wg.definition import BaseWaveguideDefinition, SingleShapeWaveguideElement
from ipkiss.all import *

__all__ = ["WgElSlottedDefinition", 
           "Wg2ElSlottedDefinition"]  


class __SlotWgDefinition__(StrongPropertyInitializer):
    wg_width = PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH) 
    slot_width = PositiveNumberProperty(default = TECH.WG.SLOT_WIDTH)
    trench_width = NonNegativeNumberProperty(default=TECH.WG.TRENCH_WIDTH)
    process = ProcessProperty(default = TECH.PROCESS.WG) 
    
    def transform(self, transformation):
        self.slot_width = transformation.apply_to_length(self.slot_width)
        return super(__SlotWgDefinition__, self).transform(transformation)

class __SlotWgElement__(object):
    wg_width = ReadOnlyIndirectProperty("wg_definition")
    slot_width = ReadOnlyIndirectProperty("wg_definition")
    trench_width = ReadOnlyIndirectProperty("wg_definition")    
    process = ReadOnlyIndirectProperty("wg_definition")    
    
    
    
class WgLFElSlottedDefinition(__SlotWgDefinition__, BaseWaveguideDefinition):
    
    class __WgLFElSlottedDefinitionPathDefinition__(__SlotWgElement__, SingleShapeWaveguideElement):
        """single_shape slot waveguides without trench"""
    
        def define_elements(self, elems):
            for s in self.__get_shape_list__():
                C1a = ShapeOffset(s, 0.5*self.slot_width)
                C1b = ShapeOffset(s, 0.5*self.wg_width)
                C2a = ShapeOffset(s, -0.5*self.slot_width)
                C2b = ShapeOffset(s, -0.5*self.wg_width)
                elems += Boundary(PPLayer(self.process, TECH.PURPOSE.LF.LINE), C1a + C1b.reversed())
                elems += Boundary(PPLayer(self.process, TECH.PURPOSE.LF.LINE), C2a + C2b.reversed())
            return elems

    
    def __init__(self, wg_width = TECH.WG.SLOTTED_WIRE_WIDTH, slot_width = TECH.WG.SLOT_WIDTH, process = TECH.PROCESS.WG):
        super(WgElDefinition, self).__init__(wg_width = wg_width, slot_width = slot_width, process = process)
                
    def __eq__(self, other):
        if isinstance(other, __SlottedNoTrenchWaveguideElementDefinition__):
            return (self.slot_width == other.slot_width and
                    self.process == other.process and
                    self.trench_width == other.trench_width)
        else:
            return False        
        
    def __ne__(self, other):
        return (not self.__eq__(other))        

    def transform(self, transformation):
        __SlotWgDefinition__.transform(self, transformation)
        return BaseWaveguideDefinition.transform(self, transformation)

    def __repr__(self):
        return "%s w=%f, s=%f, %s" % (self.__id_name__,
                                              self.wg_width,
                                              self.slot_width,
                                              self.process.extension)
         
    
__WgLFElSlottedDefinitionPathDefinition__ = WgLFElSlottedDefinition.__WgLFElSlottedDefinitionPathDefinition__   # to allow picke/unpickle 

        
class WgElSlottedDefinition(__SlotWgDefinition__, BaseWaveguideDefinition):
    
    class __WgElSlottedDefinitionPathDefinition__(__SlotWgElement__, SingleShapeWaveguideElement):
        """ single_shape slotted waveguides with trench """
        
        def define_elements(self, elems):
            for s in self.__get_shape_list__():
                C1a = ShapeOffset(s, 0.5*self.slot_width)
                C1b = ShapeOffset(s, 0.5*self.wg_width)
                C2a = ShapeOffset(s, -0.5*self.slot_width)
                C2b = ShapeOffset(s, -0.5*self.wg_width)
                elems += Boundary(PPLayer(self.process, TECH.PURPOSE.LF.LINE), C1a + C1b.reversed())
                elems += Boundary(PPLayer(self.process, TECH.PURPOSE.LF.LINE), C2a + C2b.reversed())
                T1 = ShapeOffset(s, 0.5*self.wg_width + self.trench_width)
                T2 = ShapeOffset(s, -0.5*self.wg_width - self.trench_width)
                end_face = Shape([C1b[-1],C1a[-1],C2a[-1],C2b[-1]])
                start_face = Shape([C2b[0],C2a[0],C1a[0],C1b[0]])
                elems += Boundary(PPLayer(self.process, TECH.PURPOSE.LF_AREA), T1 + end_face + T2.reversed() + start_face)
            return elems    
        
    def __init__(self, wg_width = TECH.WG.SLOTTED_WIRE_WIDTH, slot_width = TECH.WG.SLOT_WIDTH, trench_width = TECH.WG.TRENCH_WIDTH, process = TECH.PROCESS.WG):
        super(WgElSlottedDefinition, self).__init__(wg_width = wg_width, slot_width = slot_width, trench_width = trench_width, process = process)
        
    def __eq__(self, other):
        if isinstance(other, WgElSlottedDefinition):
            return (self.slot_width == other.slot_width and
                    self.wg_width == other.wg_width and
                    self.process == other.process and
                    self.trench_width == other.trench_width)
        else:
            return False
        
        
    def __ne__(self, other):
        return (not self.__eq__(other))        

    def __repr__(self):
        return "SlottedWgElDef w=%f, s=%f, t=%f, %s" % (self.wg_width,
                                              self.slot_width,
                                              self.trench_width,
                                              self.process.extension)
    

__WgElSlottedDefinitionPathDefinition__ = WgElSlottedDefinition.__WgElSlottedDefinitionPathDefinition__  # to allow picke/unpickle


class Wg2ElSlottedDefinition(WgElSlottedDefinition):
    """two_shape slotted waveguide definition"""
    
    class __Wg2ElSlottedDefinitionPathDefinition__(Wg2ElDefinition.__Wg2ElDefinitionPathDefinition__, WgElSlottedDefinition.__WgElSlottedDefinitionPathDefinition__):
        def define_elements(self, elems):
            for (s, ts) in zip(self.__get_shape_list__(), self.__get_trench_shape_list__()):
                C1a = ShapeOffset(s, 0.5*self.slot_width)
                C1b = ShapeOffset(s, 0.5*self.wg_width)
                C2a = ShapeOffset(s, -0.5*self.slot_width)
                C2b = ShapeOffset(s, -0.5*self.wg_width)
                elems += Boundary(self.layer, C1a + C1b.reversed())
                elems += Boundary(self.layer, C2a + C2b.reversed())
                T1 = ShapeOffset(ts, 0.5*self.wg_width + self.trench_width)
                T2 = ShapeOffset(ts, -0.5*self.wg_width - self.trench_width)
                end_face = Shape([C1b[-1],C1a[-1],C2a[-1],C2b[-1]])
                start_face = Shape([C2b[0],C2a[0],C1a[0],C1b[0]])
                elems += Boundary(self.inv_layer, T1 + end_face + T2.reversed() + start_face)
            return elems
        
    
__Wg2ElSlottedDefinitionPathDefinition__ = Wg2ElSlottedDefinition.__Wg2ElSlottedDefinitionPathDefinition__

