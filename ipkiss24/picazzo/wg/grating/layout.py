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
Waveguide gratings (various forms)

"""

from ipkiss.all import *
from ipkiss.plugins.photonics.port.port import OpticalPort
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty

from ipkiss.plugins.photonics.wg import WgElDefinition

__all__ = ["WgGrating",
           "WgGratingGeneric",
           "WgGratingRect",
           "WgGratingSideblock",
           "WgGratingShallow",
           "WgGratingPeriodBlocks",
           "WgGratingPeriodShallow",
           "WgGratingPeriodSideblock"]

##############################################################################
## Grating periods
##############################################################################

class __WgGratingPeriod__(Structure):
    """ abstract class for waveguide grating period """
    __name_prefix__ = "WG_GP_"
    length = PositiveNumberProperty(required = True)
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    
    def define_ports(self, prts):
        prts += [OpticalPort(position = (0.0, 0.0), angle = -180.0, wg_definition = self.wg_definition),
                OpticalPort(position = (self.length,0.0), angle = 0.0, wg_definition = self.wg_definition)]
        return prts
        
    
    
    
class WgGratingPeriodBlocks(__WgGratingPeriod__):
    """ waveguide grating period consisting of rectangular blocks
        blocks is a list of (wg_definition, length) tuples """
    __name_prefix__ = "TECH_WG_GPB_"

    length = DefinitionProperty(fdef_name = "define_length")
    blocks = RestrictedProperty(restriction = RestrictList(RESTRICT_TUPLE2), required = True)
    
   
    def define_length(self):
        length = sum([d[1] for d in self.blocks])
        return length
        
    def define_elements(self, elems):
        x = 0.0
        for b in self.blocks:
            elems += b[0](shape = [(x, 0), (x+b[1], 0)])
            x += b[1]
        return elems

    def define_ports(self, prts):
        prts += [OpticalPort(position = (0.0, 0.0), angle = -180.0, wg_definition = self.wg_definition),
                OpticalPort(position = (self.length, 0.0), angle = 0.0, wg_definition = self.wg_definition)]
        return prts
        
        
def wg_grating_period_rect(length, wg_width, wide_width, narrow_width, fill_factor = 0.5, trench_width=2.0, process = TECH.PROCESS.WG):
    """ a waveguide grating period with a rectagular tooth """
    return WgGratingPeriodBlocks(wg_width, [Coord2(narrow_width, 0.5*length * (1-fill_factor)), Coord2(wide_width, length * fill_factor), Coord2(narrow_width, 0.5*length * (1-fill_factor))], trench_width, process , library)


class WgGratingPeriodShallow(__WgGratingPeriod__):
    __name_prefix__ = "TECH_WG_GPS_"
    fill_factor = RestrictedProperty(restriction = RESTRICT_FRACTION, default = 0.5)
    deep_process = ProcessProperty(default = TECH.PROCESS.WG)
    shallow_process = ProcessProperty(default = TECH.PROCESS.FC)
    
        
    def define_elements(self, elems):
        elems += self.wg_definition(shape = [(0.0, 0.0), (self.length, 0.0) ])
        elems += Rectangle(PPLayer(self.shallow_process, TECH.PURPOSE.DF.TRENCH),(0.5*self.length, 0.0), (self.fill_factor * self.length, 2* self.wg_definition.wg_width))
        return elems

    def define_ports(self, prts):
        prts += [OpticalPort(position = (0.0, 0.0), angle = -180.0, wg_definition = self.wg_definition),
                OpticalPort(position = (self.length, 0.0), angle = 0.0, wg_definition = self.wg_definition)]
        return prts

class WgGratingPeriodSideblock(__WgGratingPeriod__):
    __name_prefix__ = "TECH_WG_GPSB_"
    process = ProcessProperty(default = TECH.PROCESS.WG)
    block_size = Size2Property(required = True)
    block_spacing = NonNegativeNumberProperty(required = True)
        
    def define_elements(self, elems):
        elems += self.wg_definition(shape = [(0.0, 0.0), (self.length, 0.0) ])
        elems += Rectangle(PPLayer(self.process, TECH.PURPOSE.LF.LINE),(0.5*self.length, 0.5* self.wg_definition.wg_width + self.block_spacing + 0.5 * self.block_size[1]), self.block_size)
        elems += Rectangle(PPLayer(self.process, TECH.PURPOSE.LF.LINE),(0.5*self.length, -0.5* self.wg_definition.wg_width - self.block_spacing - 0.5 * self.block_size[1]), self.block_size)
        return elems

    def define_ports(self, prts):
        prts += [OpticalPort(position = (0.0, 0.0), angle = -180.0, wg_definition = self.wg_definition),
                OpticalPort(position = (self.length, 0.0), angle = 0.0, wg_definition = self.wg_definition)]
        return prts

        
class WgGratingGeneric(Structure):
    """ waveguide with a grating """
    __name_prefix__ = "TECH_WG_GG_"
    periods = RestrictedProperty(restriction = RestrictTypeList(__WgGratingPeriod__), required = True) 
    positions = DefinitionProperty(fdef_name = "define_positions")
                                         
    
    def define_positions(self):
        p = [Coord2(0.0, 0.0)]
        for i in range(len(self.periods)-1):
            p += [p[-1] - self.periods[i+1].west_ports[0].position + self.periods[i].east_ports[0].position]
        return p
    
    def define_elements(self, elems):
        for period, position in zip(self.periods, self.positions):
            elems += SRef(period, position)
        return elems
    
    def define_ports(self, prts):
        P = OpticalPortList()
        P += self.periods[0].west_ports.move_copy(self.positions[0])
        P += self.periods[-1].east_ports.move_copy(self.positions[-1])
        return P


class WgGrating(Structure):
    """ waveguide with a grating """
    __name_prefix__ = "TECH_WG_G_"
    period = RestrictedProperty(restriction = RestrictType(__WgGratingPeriod__), required = True)
    n_o_periods = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    pitch = DefinitionProperty(fdef_name = "define_pitch")
    

    def define_pitch(self):
        return self.period.east_ports[0].x - self.period.west_ports[0].x
        
    def define_elements(self, elems):
        elems += ARefX(self.period, (0.0, 0.0), self.pitch, self.n_o_periods)
        return elems
    
    def define_ports(self, prts):
        P = OpticalPortList()
        P += self.period.west_ports
        P += self.period.east_ports.move_copy((self.pitch * (self.n_o_periods-1), 0))
        return P
    
        
def wg_grating_period_rect(length, wg_definition, wide_wg_definition, narrow_wg_definition, fill_factor = 0.5):
    """ a waveguide grating period with a rectagular tooth """
    return WgGratingPeriodBlocks(wg_definition = wg_definition, 
                                  blocks = [(narrow_wg_definition, 0.5*length * (1-fill_factor)), 
                                            (wide_wg_definition, length * fill_factor), 
                                            (narrow_wg_definition, 0.5*length * (1-fill_factor))])    

def WgGratingRect(pitch, n_o_periods, wg_definition, wide_wg_definition, narrow_wg_definition, fill_factor = 0.5, 
                  trench_width=TECH.WG.TRENCH_WIDTH, 
                  process = TECH.PROCESS.WG ):
    period = wg_grating_period_rect(pitch, wg_definition, wide_wg_definition, narrow_wg_definition, fill_factor)
    return WgGrating(period = period, n_o_periods = n_o_periods)


def WgGratingShallow(pitch, n_o_periods, wg_definition = TECH.WGDEF.WIRE, fill_factor = 0.5, deep_process = TECH.PROCESS.WG, shallow_process = TECH.PROCESS.FC ):    
    period = WgGratingPeriodShallow(length = pitch, 
                                    wg_definition = wg_definition, 
                                    fill_factor = fill_factor, 
                                    deep_process = deep_process, 
                                    shallow_process = shallow_process)
    return WgGrating(period = period, n_o_periods = n_o_periods)

def WgGratingSideblock(pitch, n_o_periods, wg_definition, block_size, block_spacing):
    period = WgGratingPeriodSideblock(length = pitch, wg_definition = wg_definition, block_size = block_size, block_spacing = block_spacing)
    return WgGrating(period = period, n_o_periods = n_o_periods)

