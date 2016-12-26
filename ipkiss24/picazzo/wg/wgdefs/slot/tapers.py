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
from picazzo.wg.tapers.basic import __WgElTaper__, __WgElPortTaper__

__all__ = ["WgElPortTaperSlotted",
           "WgElTaperSlotted"]

class WgElTaperSlotted(__WgElTaper__):
    """ Taper from ASlotted Waveguide to Wire waveguide"""

    slot_extension_length = PositiveNumberProperty(default = 4.0)
    
    def define_elements(self, elems):
        start_width = self.start_wg_def.wg_width # slot
        start_slot_width = self.start_wg_def.slot_width
        start_slot_rib_width = 0.5*(start_width-start_slot_width)
        end_width = self.end_wg_def.wg_width # wire
       
        start_position = self.start_position
        end_position = self.end_position
        dist = distance(start_position, end_position)
        cosangle = (start_position[0] - end_position[0])/dist
        sinangle = (start_position[1] - end_position[1])/dist

        # define taper from (0,0) eastward. Transform later
        angled_slot_length = dist - self.slot_extension_length 
        slot_length = dist 
        tan_s = 0.5*(start_slot_width + end_width) / angled_slot_length
        L1a = 0.5*(start_slot_rib_width + start_slot_width)/tan_s
        
        L1c = angled_slot_length / 5.0
        L1b = L1a-0.5*L1c
        w_min = 0.5*start_width - L1b * tan_s
        
        e = ElementList()
        
        # outline of ridge
        o_shape = Shape([(0.0, 0.5* start_slot_width),
                         (0.0, 0.5* start_width),
                         (L1b, w_min),
                         (L1b+L1c, w_min),
                         (angled_slot_length, 0.5*end_width),
                         (slot_length, 0.5 * end_width),
                         (slot_length, -0.5 * end_width),
                         (slot_length, -0.5*start_width - start_slot_rib_width - start_slot_width + TECH.TECH.MINIMUM_LINE),
                         (slot_length, -0.5*start_width - start_slot_rib_width - start_slot_width),
                         (angled_slot_length, -0.5*start_width - start_slot_rib_width - start_slot_width),
                         (0.0, -0.5* start_width),
                         (0.0, -0.5* start_slot_width)],
                        closed = True)
        e += Boundary(layer = PPLayer(self.start_wg_def.process, TECH.PURPOSE.LF.LINE),
                      shape = o_shape)
        # slot shape
        s_shape = Shape([(0.0, 0.5*start_slot_width),
                         (L1a, -0.5*start_slot_rib_width), # if needed, replace by 2 points with smoother transition
                         (angled_slot_length, -0.5*end_width),
                         (slot_length, -0.5 * end_width),
                         (slot_length, -0.5*start_width - start_slot_rib_width - start_slot_width + TECH.TECH.MINIMUM_LINE), # add curvature if needed
                         (angled_slot_length, -0.5 * end_width - start_slot_width),
                         (0.0, -0.5*start_slot_width)],
                        closed = True)
        e += Boundary(layer = PPLayer(self.start_wg_def.slot_process, TECH.PURPOSE.DF.TRENCH),
                      shape = s_shape)
        
        # trench shape
        t_shape = Shape([(0.0, 0.5* start_slot_width),
                         (0.0, 0.5*start_width),
                         (0.0, 0.5*start_width + self.start_wg_def.trench_width),
                         (0.25 * slot_length, 0.5*start_width + self.start_wg_def.trench_width),
                         (0.75 * slot_length, 0.5*end_width + self.end_wg_def.trench_width),
                         (slot_length, 0.5*end_width + self.end_wg_def.trench_width),
                         (slot_length, 0.5*end_width),
                         (slot_length, -0.5*end_width),
                         (slot_length, -0.5*start_width - start_slot_rib_width - start_slot_width + TECH.TECH.MINIMUM_LINE), # add curvature if needed
                         (slot_length, -0.5*start_width - start_slot_rib_width - start_slot_width),
                         (slot_length, -0.5*end_width - self.end_wg_def.trench_width),
                         (0.75 * slot_length, -0.5*end_width - self.end_wg_def.trench_width),
                         (0.25 * slot_length, -0.5*start_width - self.start_wg_def.trench_width),
                         (0.0, -0.5*start_width - self.start_wg_def.trench_width),
                         (0.0, -0.5*start_width ),
                         (0.0, -0.5* start_slot_width)],
                        closed = True)
        e += Boundary(layer = PPLayer(self.start_wg_def.process, TECH.PURPOSE.LF_AREA),
                      shape = t_shape)
                         
        # transformation
        T = Rotation((0.0, 0.0), angle_deg(end_position, start_position)) + Translation(start_position)
        e.transform(T)
        elems += e
        return elems

    def validate_properties(self):
        return True     
        
class WgElPortTaperSlotted(WgElTaperSlotted, __WgElPortTaper__):
    #Note: The end of the taper is the slotted part, while the start is a normal wire/waveguide.
    #This class defines a taper to be placed on a port, the start_port. As for most applications this port is slotted,
    #this implicates that the end of the taper will be placed on the start_port
            
    length = NonNegativeNumberProperty(default = 12.0)
    
    def define_ports(self,ports):
        return __WgElPortTaper__.define_ports(self,ports)

    
##################################
from .wgdef import SlottedWaveguideElementDefinition
from ipkiss.plugins.photonics.wg.basic import WgElDefinition

TECH.WGDEF.AUTO_TAPER_DATA_BASE.add(SlottedWaveguideElementDefinition, WgElDefinition, WgElPortTaperSlotted)
