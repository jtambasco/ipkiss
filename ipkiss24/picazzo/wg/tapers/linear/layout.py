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
from ..basic.layout import __WgElTaper__, __WgElPortTaper__

__all__ = ["WgElTaperLinear", "WgElPortTaperLinear"]

class WgElTaperLinear(__WgElTaper__):
    """ This class generates a linear taper between waveguide definitions to make tapers for more complex waveguide structures.
    The waveguide definitions should be of the same type """
    
    def __get_taper_shape__(self, start_position, end_position, start_window, end_window, straight_extension) :
        angle = angle_deg(end_position, start_position)
        dist = distance(start_position, end_position)
        
        var_poly = Shape([(start_position[0],start_window.start_offset+start_position[1]), 
                    (start_position[0]-straight_extension[0],start_window.start_offset+start_position[1]),
                    (start_position[0]-straight_extension[0],start_window.end_offset+start_position[1]), 
                    (start_position[0],start_window.end_offset+start_position[1]), 
                    (start_position[0]+dist,end_window.end_offset+start_position[1]), 
                    (start_position[0]+dist+straight_extension[1],end_window.end_offset+start_position[1]), 
                    (start_position[0]+dist+straight_extension[1],end_window.start_offset+start_position[1]),
                    (start_position[0]+dist,end_window.start_offset+start_position[1])])
        var_poly_trans = var_poly.rotate(start_position, angle)
        return var_poly_trans
    
     

    

class WgElPortTaperLinear(WgElTaperLinear, __WgElPortTaper__):
    """ Linear taper starting from ipkiss.plugins.photonics.port between two waveguide definitions of the same class """
    
    start_process = ProcessProperty(allow_none = True, doc = "To overrule the start process, if the processes of the windows of the waveguide definition at the start port should not be used")    

    def define_elements(self, elems):
        start_windows_list = self.start_wg_def.windows
        end_windows_list = self.end_wg_def.windows
        if len(start_windows_list) != len(end_windows_list):
            raise Exception("Start and end waveguide definitions have a different number of windows (%i vs %i)." %(len(start_windows_list), len(end_windows_list)))
        # Then we iterate over all the windows and get the corresponding taper shape        
        for start_window, end_window in zip(start_windows_list, end_windows_list) :
            taper_window = self.__get_taper_shape__(self.start_position,
                                                    self.end_position,
                                                    start_window,
                                                    end_window,
                                                    self.straight_extension)
            if self.start_process is None:
                elems += Boundary(start_window.layer, taper_window)
            else:
                elems += Boundary(PPLayer(process = self.start_process, purpose = start_window.layer.purpose), taper_window)                
        return elems    
    
    def validate_properties(self):
        if not (self.start_process is None):
            for start_window in self.start_wg_def.windows:
                if not isinstance(start_window.layer, PPLayer):
                    raise AttributeError("'start_process' of 'WgElPortTaperLinear' can only be set if the starting waveguide definition has windows with layer of type 'PPLayer'")
        return True


