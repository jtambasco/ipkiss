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

if __name__ == "__main__":   
    from technologies.si_photonics.picazzo.default import *
from picazzo.wg.wgdefs.raised import RaisedWGFCWgElDefinition, RaisedFCWgElDefinition
from picazzo.wg.wgdefs.wg_fc import WGFCWgElDefinition
from picazzo.wg.taper_extended import *
from ipkiss.plugins.photonics.port import *
from ipkiss.all import *

# TODO: remove this example. Replace with AutoTaperPorts
class ExampleTapersExtended(Structure):
    
    def define_elements(self, elems):

        #tapering from RaisedWGFCWgElDefinition to WGFCWgElDefinition
        wg_def_start = RaisedWGFCWgElDefinition(top_width=2.0)        
        wg_def_end = WGFCWgElDefinition(wg_width = 0.8, trench_width = 2.0, shallow_wg_width = 0.40, shallow_trench_width=2.0)
        taper1 = WgElPortTaperExtended(start_port=OpticalPort(position=(90.0,80.0), wg_definition=wg_def_start, angle=60.0), 
                                       end_wg_def=wg_def_end, 
                                       straight_extension=(70.0,40.0),
                                       length = 20.0)   #default taper length is 10.0         
        elems += taper1
        
        #tapering from RaisedFCWgElDefinition to WgElDefinition
        wg_def_start = RaisedFCWgElDefinition(shallow_wg_width=2.0)
        wg_def_end = WgElDefinition(wg_width=1.0)
        taper2 = WgElPortTaperExtended(start_port=OpticalPort(position=(-10.0,10.0), wg_definition=wg_def_start, angle=90.0), 
                                       end_wg_def=wg_def_end, 
                                       straight_extension=(25.0,10.0))
        elems += taper2

        return elems
    
if __name__ == "__main__":    
    d = ExampleTapersExtended()
    d.write_gdsii("sample_tapers_extended.gds")
    
    from ipkiss.plugins.vfabrication import *
    d.visualize_2d()
