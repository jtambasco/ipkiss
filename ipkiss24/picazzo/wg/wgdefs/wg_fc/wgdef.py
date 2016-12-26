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

from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.plugins.photonics.wg.window import PathWindow
from ipkiss.all import *

__all__ = ["ShallowWgElDefinition",
           "WGFCWgElDefinition"
           ]

class ShallowWgElDefinition(WgElDefinition):    
    """ This waveguide is a shallow etched Silicon waveguide. 
    
                         ___________
               _________|   22nm    |______________   
               150nm        
          ___________________________________________________
    
    """
    process = ProcessProperty(default = TECH.PROCESS.FC)

    
class WGFCWgElDefinition(WgElDefinition) :
    """ This waveguide is a shallow etched Silicon waveguide. 
    It can be ended with an etch to the BOX if the trench parameter is set to a value >0 
    
                         ___________
                        |   220nm   |
                     ___|___________|___   
                    |      150nm        |
          ___________________________________________________
            
    
    """
    ## FIXME. Ambiguity between trench width and shallow trench width. 
    ## Reduce this to a single class of waveguide (two etch). The other class in is wgdefs.fc
    
    trench_width = NonNegativeNumberProperty(default=0.0)
    shallow_wg_width = PositiveNumberProperty(default=TECH.WG.WIRE_WIDTH)
    shallow_trench_width = NonNegativeNumberProperty(default=TECH.WG.TRENCH_WIDTH)
    wg_width = DefinitionProperty(fdef_name="define_wg_width")
    shallow_process = ProcessProperty(default = TECH.PROCESS.FC) 
    
    def define_wg_width(self) :
        # The WG LINE window is put over the shallow etched waveguide (core+trench). 
        # If the WG LF_AREA is bigger than this window, a trench to the BOX will be etched around the waveguide.
        return (self.shallow_trench_width*2+self.shallow_wg_width)
    
    def define_windows(self) :
        windows = super(WGFCWgElDefinition, self).define_windows()
        
        windows += [PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA),
                           start_offset = -0.5 * self.shallow_wg_width-self.shallow_trench_width,
                           end_offset = +0.5 * self.shallow_wg_width+self.shallow_trench_width),
                    PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE),
                           start_offset = -0.5 * self.shallow_wg_width,
                           end_offset = +0.5 * self.shallow_wg_width)]
        return windows
    
    def __repr__(self):
        return "%s w=%f, t=%f" % ("WGFC WIRE",
                                  self.shallow_wg_width,
                                  self.shallow_trench_width) 
    