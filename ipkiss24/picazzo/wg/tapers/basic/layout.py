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

## Authors : Wim Bogaerts, Emmanuel Lambert

from ipkiss.all import *
from ipkiss.plugins.photonics.port.port import OpticalPort, InOpticalPort, OutOpticalPort, OpticalPortProperty
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.geometry.transforms.rotation import shape_rotate

__all__ = ["__WgElTaper__", "__WgElPortTaper__"]

class __WgElTaper__(Group):
    """ Basic taper between 2 waveguide definitions """
    start_position = Coord2Property(required = True, doc = "start position of the taper")
    end_position = Coord2Property(required = True, doc = "end position of the taper")
    start_wg_def = WaveguideDefProperty(required = True, doc = "waveguide definition at the start")
    end_wg_def = WaveguideDefProperty(required = True, doc = "waveguide definition at the end")
    straight_extension = Size2Property(default = (0.0, 0.0), doc = "tuple: straight extension at start and end of taper")
    process = ProcessProperty(allow_none = True, doc="If case the tpaering process must be overruled")
    
    def define_elements(self, elems):
        start_windows_list = self.start_wg_def.windows
        end_windows_list = self.end_wg_def.windows
        # Then we iterate over all the windows and get the corresponding taper shape
        for start_window, end_window in zip(start_windows_list, end_windows_list) :
            taper_window = self.__get_taper_shape__(self.start_position,
                                                    self.end_position,
                                                    start_window,
                                                    end_window,
                                                    self.straight_extension)
            if self.process is None:
                elems += Boundary(start_window.layer, taper_window) #normal case
            else:
                purpose = start_window.layer.purpose
                taper_ppl = PPLayer(self.process, purpose)
                elems += Boundary(taper_ppl, taper_window)                 
        return elems

    def define_ports(self, ports):
        angle = angle_deg(self.end_position, self.start_position)
        ports += [InOpticalPort(wg_definition = self.start_wg_def, position = self.start_position, angle=(angle + 180.0)%360.0), 
                 OutOpticalPort(wg_definition = self.end_wg_def, position = self.end_position, angle = angle)]
        return ports    
    
    def validate_properties(self):
        if type(self.start_wg_def) != type(self.end_wg_def):
            raise AttributeError("The start and end waveguide definition should be of the same type.")
        return True    
    
    def __get_taper_shape__(self, start_position, end_position, start_window, end_window, straight_extension) :
        raise NotImplementedError()

    
class __WgElPortTaper__(__WgElTaper__):
    """ taper starting from ipkiss.plugins.photonics.port. The corresponding start_position and end_position are calculated internally """
    start_position  = DefinitionProperty(fdef_name = "define_start_position")
    end_position = DefinitionProperty(fdef_name = "define_end_position")
    start_wg_def = DefinitionProperty(fdef_name = "define_start_wg_def")        
    start_port = OpticalPortProperty(required = True, doc = "Port the taper starts from")
    length = PositiveNumberProperty(default = TECH.WG.SHORT_TAPER_LENGTH, doc = "taper length")
            
    def define_start_position(self):
        return self.start_port.position
    
    def define_end_position(self):
        return self.start_position.move_polar_copy(self.length, self.start_port.angle_deg)
    
    def define_start_wg_def(self):
        return self.start_port.wg_definition
    
    def define_ports(self, ports):
        angle = angle_deg(self.end_position, self.start_position)
        if isinstance(self.start_port, InOpticalPort):
            ports += [OutOpticalPort(position = self.start_position, wg_definition = self.start_wg_def, angle = (angle + 180.0)%360.0), 
                     InOpticalPort(position = self.end_position, wg_definition = self.end_wg_def, angle = angle)]
        else:
            ports += [InOpticalPort(position = self.start_position, wg_definition = self.start_wg_def, angle = (angle + 180.0)%360.0), 
                     OutOpticalPort(position = self.end_position, wg_definition = self.end_wg_def, angle = angle)]
        return ports
