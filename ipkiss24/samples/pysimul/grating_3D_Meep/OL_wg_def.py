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

##from technologies.si_photonics.picazzo.default import *
from ipkiss.plugins.photonics.wg import *
from ipkiss.plugins.photonics.wg.window import WindowWaveguideDefinition, WindowsOnWaveguideDefinition, PathWindow
import numpy
from ipkiss.all import *

        
class OverlayWgDefinition(WindowWaveguideDefinition):
    process = ProcessProperty(default = TECH.PROCESS.ACO)
    wg_width = FloatProperty(default = 1.5) 
    trench_width = FloatProperty(default = 0.0)
    def define_windows(self):
        return [PathWindow (layer = TECH.PPLAYER.ACO.DEFAULT,
                            start_offset = -0.5 * self.wg_width,
                            end_offset = 0.5 * self.wg_width)]
    
    
