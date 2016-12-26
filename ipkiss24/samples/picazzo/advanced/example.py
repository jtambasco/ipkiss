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
from ipkiss.all import *
from ipkiss.plugins.photonics.wg.basic import *    # basic waveguides
from picazzo.io.column import IoColumnGroup
from picazzo.log import PICAZZO_LOG as LOG

#######################################
# add structures to layout
#######################################

class PicazzoExample1(Structure):
    
    def define_elements(self, elems):
        # alignment waveguide      
        layout = IoColumnGroup(y_spacing=25.0, south_east=(6000.0,0.0))
        
        wg_def2 = WgElDefinition(wg_width=0.5,trench_width=7.0)
        align2_wg = wg_def2(shape = [(0.0,0.0), (100.0,0.0)])
        align2 = Structure(name="align2", elements=[align2_wg], ports=align2_wg.ports)
        layout += align2
        
        wg_def3 = WgElDefinition(wg_width=2.0,trench_width=7.0)
        align3_wg = wg_def3(shape = [(0.0,0.0), (200.0,0.0)])
        align3 = Structure(name="align3", elements=[align3_wg], ports=align3_wg.ports)
        layout += align3
        
        elems += layout
        return elems

    
if __name__ == "__main__":
    layout = PicazzoExample1(name = "layout")
    # -------- export to GDS2 : instead of manually making a library, we can use this convenient shortcut-function to export a structure 
    layout.write_gdsii("example1.gds")
    # -------- verify the fabrication materials with a 2D visualization
    from ipkiss.plugins.vfabrication import *
    layout.visualize_2d()  
    # -------- export a GDS file with the virtual fabrication 
    layout.write_gdsii_vfabrication("example1_vfab.gds")    
  