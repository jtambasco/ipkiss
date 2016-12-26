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
from ipkiss.plugins.photonics.wg.basic import *    # basic waveguides
from picazzo.io.column import *  # Standard io columns

from example4_grating_mmi import * #our structure (in seperate file example4_grating_mmi.py)
from picazzo.fibcoup.inverted_taper import *
from picazzo.io.fibcoup import *


######################################
# add structures to layout
#######################################

class PicazzoExample4(Structure):
    
    def define_elements(self, elems):            
        layout = IoColumnGroup(y_spacing=25.0, south_east=(6000.0,0.0))
        layout.y_spacing=250.0
        
        # alignment waveguide
        wg_def = WgElDefinition()
        align_wg = wg_def(shape = [(0.0, 0.0), (50.0, 0.0)])
        align = Structure(name = "align", elements=[align_wg], ports=align_wg.ports)        
        
        layout.add(align, fibcoup = NitrideInvertedTaper('it'))
        
        layout += GratingMmi(mmi_length = 5,
                              mmi_width = 2, 
                              grating_pitch = 0.6, 
                              grating_trench_width = 0.3)
        
        elems += layout
        return elems
    

if __name__ == "__main__":
        layout = PicazzoExample4(name = "layout")
        # -------- export to GDS2 : instead of manually making a library, we can use this convenient shortcut-function to export a structure 
        layout.write_gdsii("example4.gds")
        # -------- verify the fabrication materials with a 2D visualization
        from ipkiss.plugins.vfabrication import *
        layout.visualize_2d()         

        
          
    
    