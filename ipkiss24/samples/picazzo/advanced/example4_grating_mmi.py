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

from picazzo.builder import *
from ipkiss.plugins.photonics.wg import *
from ipkiss.plugins.photonics.port import *

class GratingMmi(Structure):
    __name_prefix__ = "GMMI"
    mmi_length = PositiveNumberProperty(required = True)
    mmi_width = PositiveNumberProperty(required = True)
    grating_pitch = PositiveNumberProperty(required=True)
    grating_trench_width = PositiveNumberProperty(required = True)
    wg_width = PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH)
    trench_width = PositiveNumberProperty(default = TECH.WG.TRENCH_WIDTH)
    
    def define_name(self):
        return "%s_L%d_W%d_P%d_T%d_W%d_T%d" % (
            self.__name_prefix__, 
            self.mmi_length*1000, 
            self.mmi_width*1000, 
            self.grating_pitch*1000, 
            self.grating_trench_width*1000,
            self.wg_width*1000, 
            self.trench_width*1000
        )
    
    def define_elements(self, elems):
        wg_def = WgElDefinition(wg_width = self.mmi_width, trench_width = self.trench_width)
        elems += wg_def([(0.0, 0.0), (self.mmi_length, 0.0)])
        n_o_periods = int(self.mmi_length/self.grating_pitch)
        period1 = Structure(name = self.name + "_1", 
                                elements = Line(layer = PPLayer(TECH.PROCESS.FC, TECH.PURPOSE.DF.TRENCH),
                                                   begin_coord = (0.0, 0.0), 
                                                   end_coord = (self.grating_trench_width, 0.0), 
                                                   line_width = self.mmi_width
                                               )
                                           )
        elems += ARef(reference = period1, 
                        origin = (0.0, 0.0), 
                        period = (self.grating_pitch, 1.0), 
                        n_o_periods = (n_o_periods, 1)
                    )
        return elems
        
        
    def define_ports(self, ports):
        wg_def = WgElDefinition(wg_width = self.wg_width, trench_width = self.trench_width)
        ports += InOpticalPort(position = (0.0, 0.0), wg_definition = wg_def, angle = 180.0)
        ports += InOpticalPort(position = (self.mmi_length, 0.0), wg_definition = wg_def, angle = 0.0)
        return ports
    
    
        
        
        