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
from picazzo.phc.w1 import *      # photonic crystals
from picazzo.filters.ring import * # ring resonators
from picazzo.io.column import *  # Standard io columns
from ipkiss.plugins.vfabrication import *
from ipkiss.io.output_gdsii import FileOutputGdsii

#######################################
# add structures to layout
#######################################

class PicazzoExample2(Structure):
    
    def define_elements(self, elems):
        layout = IoColumnGroup(y_spacing=25.0, south_east=(6000.0,0.0))
        
        # alignment waveguide
        wg_def = WgElDefinition()
        align_wg = wg_def(shape = [(0.0, 0.0), (50.0, 0.0)])
        align = Structure(name = "align", elements = [align_wg], ports = align_wg.ports)
        layout += align
        
        # photonic crystal waveguides
        lengths = [20, 40, 60, 80]
        pitch, diameter = 0.430, 0.260
        cladding_layers = 7
        for L in lengths:
            n_o_periods = int(L / pitch)
            layout += W1Waveguide(pitch = pitch, 
                                   diameter = diameter, 
                                   n_o_cladding_layers = cladding_layers, 
                                   n_o_periods = n_o_periods)
        
        # ring resonators
        radii = [3, 4, 5]
        for R in radii:
            layout += RingRectNotchFilter(bend_radius = R, straights = (0.0, 0.0))
            
        elems += layout
        return elems
    
        
if __name__ == "__main__":
    layout = PicazzoExample2(name = "layout")
    # -------- export to GDS -------------    
    my_lib = Library(name = "PICAZZO_EXAMPLE_2", unit = 1E-6, grid = 5E-9)
    # Add main layout to library
    my_lib += layout
    op = FileOutputGdsii("example2.gds")
    # Write library
    op.write(my_lib)
    # visualize_2d too time consuming because of the photonic crystal
    
        

    