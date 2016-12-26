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

from technologies.si_photonics.picazzo.default import *
from picazzo.io.column import IoColumn
from ipkiss.all import *
from numpy import arange

class MmiSweep(Structure):
    
    def get_mmi(self, width, length, wg_offset, taper_width):
        from picazzo.filters.mmi import Mmi2x2Tapered
        return Mmi2x2Tapered(width = width,length = length,wg_offset = wg_offset,taper_width = taper_width)

    def define_elements(self, elems):   
        #create a layout with a sweep of MMI's
        from picazzo.io.fibcoup import IoFibcoup
        col = IoColumn(name = "MMI SWEEP",
                          y_spacing = 35.0,
                          south_west = (0.0, 0.0),
                          south_east = (3500.0, 0.0),
                          adapter = IoFibcoup
                          )
        for l in arange(6.0,7.0,0.1):
            col += self.get_mmi(width = 4.0, length = l, wg_offset = 0.67, taper_width = 0.8)
        elems += SRef(reference = col)
        return elems
    
    
class RingSweep(Structure):
    
    def get_ring(self, radius):
        from picazzo.filters.ring import RingRect180DropFilter
        return RingRect180DropFilter(bend_radius = radius, straights = (0.0, 0.0), coupler_spacings=[0.67,0.67])    
            
    def define_elements(self, elems):       
        #create a layout with a sweep of RINGS
        from picazzo.io.fibcoup import IoFibcoup
        col = IoColumn(name = "RING SWEEP",
                          y_spacing = 55.0,
                          south_west = (0.0, 0.0),
                          south_east = (2500.0, 0.0),
                          adapter = IoFibcoup
                          )
        for r in arange(5.0,18.0,0.5):
            col  += self.get_ring(radius = r) 
        elems += SRef(reference = col)
        return elems
        
                   

class HugeRingWithFibcoup(Structure):
    
    def define_elements(self, elems):
        from picazzo.filters.ring import RingRect180DropFilter
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition
        huge_ring = RingRect180DropFilter(ring_wg_definition = WgElDefinition(wg_width = 0.5),
                                   coupler_wg_definitions = [WgElDefinition(wg_width = 0.4), WgElDefinition(wg_width = 0.6)], 
                                   coupler_spacings = [5.0, 5.0], 
                                   straights=(60.0,120.0),
                                   bend_radius = 110.0
                                   )
        from picazzo.io.fibcoup import IoFibcoup
        from picazzo.fibcoup.uniform import UniformLineGrating
        grating = UniformLineGrating(origin = (0.0,0.0),
                                     period = 0.689, 
                                     line_width = 0.423, 
                                     n_o_periods = 20, 
                                     wg_definition = WgElDefinition(wg_width = 9.0),
                                     process = TECH.PROCESS.FC)
        ring_with_fibcoup = IoFibcoup(struct = huge_ring, 
                                      offset = (0.0,0.0), 
                                      y_spacing = huge_ring.size_info().height,
                                      south_west = (0.0,0.0), 
                                      south_east = (1500.0,0.0),
                                      fibcoup = grating)
        elems += SRef(reference = ring_with_fibcoup)
        return elems
    
    
class ExampleDesign(Structure):
    
    def define_elements(self, elems):  
        #create 3 structures for each of the designs
        ring_sweep = RingSweep()
        mmi_sweep = MmiSweep()
        ring_with_fibcoup = HugeRingWithFibcoup()        
        #position eacht of the layouts
        elems += SRef(reference = mmi_sweep, position = (0.0,0.0))    
        elems += SRef(reference = ring_sweep, position = (4000,0.0))
        elems += SRef(reference = ring_with_fibcoup, position = (2000.0,1000.0))
        return elems
    

if __name__ == "__main__":
        TECH.GDSII.EXPORT_LAYER_MAP.process_layer_map[TECH.PROCESS.WG] = 5
        TECH.GDSII.EXPORT_LAYER_MAP.purpose_datatype_map[TECH.PURPOSE.LF_AREA] = 1
        layout = ExampleDesign(name = "layout")
        layout.write_gdsii("example_sweep.gds")
  

        