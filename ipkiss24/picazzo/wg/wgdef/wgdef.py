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
from ipkiss.process import PPLayer, ProcessProperty
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.plugins.photonics.wg.window import PathWindow 

from ipkiss.technology import get_technology
TECH = get_technology()

if hasattr(TECH.PROCESS,'RFC'):  # FIXME: dirty - need modular imports
    from ..wgdefs.raised import RaisedWgElDefinition, RaisedFCWgElDefinition, RaisedWGFCWgElDefinition

#Naming convention:
#From center to edge the name of the silicon height is given
#Options are Raised (380nm), Wg (220nm), Fc (150nm) and Box (0nm)


## deprecated. replaced by ThinWgElDefinition
#class FCWgElDefinition(WgElDefinition) :
    #""" Shallow waveguide. The core is 150nm high and the trenches are etched until the buried oxide     
                     #___________________   
                    #|      150nm        |
          #___________________________________________________
        
    #"""
    #shallow_process = ProcessProperty(default = TECH.PROCESS.FC) 
    #def define_windows(self) :
        #windows = super(FCWgElDefinition, self).define_windows()
        
        #windows += [PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA),
                           #start_offset = -0.5 * self.wg_width-1.0,
                           #end_offset = +0.5 * self.wg_width+1.0)]
        #return windows
    #def __repr__(self):
        #return "%s w=%f, t=%f" % ("FC WIRE",
                                  #self.wg_width,
                                  #self.trench_width)
    

    
