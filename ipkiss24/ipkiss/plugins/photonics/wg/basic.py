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



"""
Basic strip/rib waveguide definitions, elements and structures

"""

from ipkiss.all import *
from .window import WindowWaveguideDefinition, PathWindow
from .definition import TwoShapeWaveguideElement
import functools

__all__ = ["WgElDefinition",
           "WgLFElDefinition",
           "Wg2ElDefinition",
           "WgDefProperty"
           ]


########################################################################################

class WgElDefinition(WindowWaveguideDefinition):
    """wire-like waveguide definition with a single shape and with a trench"""
    # properties are here just to override defaults
    wg_width = PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH) 
    process = ProcessProperty(default = TECH.PROCESS.WG) 
    trench_width = NonNegativeNumberProperty(default = TECH.WG.TRENCH_WIDTH)     

    def define_windows(self):
        windows = []
        windows.append(PathWindow(layer = PPLayer(self.process, TECH.PURPOSE.LF.LINE),
                           start_offset = -0.5 * self.wg_width,
                           end_offset = +0.5 * self.wg_width))
        if (self.trench_width > 0.0) :
            windows.append(PathWindow(layer = PPLayer(self.process, TECH.PURPOSE.LF_AREA),
                               start_offset = -0.5 * self.wg_width - self.trench_width,
                               end_offset = +0.5 * self.wg_width + self.trench_width))
        return windows
    
    def __repr__(self):
        return "%s w=%f, t=%f, %s" % ("WIRE",
                                              self.wg_width,
                                              self.trench_width,
                                              self.process.extension)    
    def define_name(self):
        return "%s_WIRE_W%d_T%d"%(self.process.extension,self.wg_width*1000,self.trench_width*1000)

class WgLFElDefinition(WgElDefinition):
    """wire-like waveguide definition with a single shape but without trench"""
    trench_width = 0.0 
                            
    def __repr__(self):
        return "%s w=%f, %s" % ("WIRE_NO_TRENCH",
                                              self.wg_width,
                                              self.process.extension)
         
########################################################################################
            
class Wg2ElDefinition(WgElDefinition):
    """wire with a trench, defined with 2 shapes"""
    
    windows = LockedProperty()
    
    class __Wg2ElDefinitionPathDefinition__(TwoShapeWaveguideElement, WindowWaveguideDefinition.__WindowWaveguideDefinitionPathDefinition__):
        
        def __init__(self, shape, **kwargs):                
            super(Wg2ElDefinition.__Wg2ElDefinitionPathDefinition__, self).__init__(shape = shape, **kwargs)
            
        
    def define_windows(self):
        windows = []
        windows.append(PathWindow(layer = PPLayer(self.process, TECH.PURPOSE.LF.LINE),
                           start_offset = -0.5 * self.wg_width,
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


__Wg2ElDefinitionPathDefinition__ = Wg2ElDefinition.__Wg2ElDefinitionPathDefinition__ #to allow pickle/unpickle


from .definition import WaveguideDefProperty
WgDefProperty = WaveguideDefProperty #alias for convenience


####################################################################################################################################






