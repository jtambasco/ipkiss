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


from ipkiss.plugins.photonics.port import OpticalPort
from ipkiss.plugins.photonics.wg.basic import WgElDefinition

from ...tapers.basic import __WgElPortTaper__
from ...tapers.linear import WgElTaperLinear, WgElPortTaperLinear
from ...tapers.deep_shallow import WgElPortTaperFromShallow

from .wgdef import ThinWgElDefinition

__all__ = ["ThinWgElToWgElPortTaper"]

class ThinWgElToWgElPortTaper(__WgElPortTaper__) :
    """ Linear taper between waveguide of type FCWgElDefinition and WgElDefinition
    It should be passed a start_port (with correct wg_def) and the end_wg_def. """
    length = PositiveNumberProperty(default = 10.0)
    taper = DefinitionProperty(fdef_name="define_taper")
    
    
    def define_taper(self) :
        start_wg_def = self.start_port.wg_definition.get_wg_definition_cross_section()
        end_wg_def = self.end_wg_def.get_wg_definition_cross_section()
        new_end_wg_def = WGFCWgElDefinition(trench_width = end_wg_def.trench_width,
                                            shallow_wg_width = end_wg_def.wg_width,
                                            shallow_trench_width =0.5 * (start_wg_def.thin_width - end_wg_def.wg_width),
                                            wg_width = end_wg_def.wg_width,
                                            shallow_process = start_wg_def.thin_process
                                            )
        new_start_wg_def = WGFCWgElDefinition(trench_width = start_wg_def.trench_width,
                                        shallow_wg_width = TECH.TECH.MINIMUM_LINE,
                                        shallow_trench_width =0.5 * (start_wg_def.thin_width - TECH.TECH.MINIMUM_LINE),
                                        wg_width = start_wg_def.wg_width,
                                        shallow_process = start_wg_def.thin_process
                                        )
        new_start_port = OpticalPort(position=self.start_port.position, 
                               wg_definition=new_start_wg_def, 
                               angle=self.start_port.angle)
        taper = WgElPortTaperLinear(start_port=new_start_port, 
                                    end_wg_def=new_end_wg_def, 
                                    length = self.length,
                                    straight_extension=self.straight_extension)
        return taper
    
    
    def define_elements(self, elems):
        elems += self.taper
        return elems
    
    def validate_properties(self):
        return True     

from ipkiss.all import *
TECH.WGDEF.AUTO_TAPER_DATA_BASE.add(ThinWgElDefinition, WgElDefinition, ThinWgElToWgElPortTaper)
    
