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

from ipkiss.all import *

class ExampleColumnParameters1(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        my_column = IoColumnGroup(south_east = (2000.0,0.0),  # column width = 2000um
                                  y_spacing = 25.0)           # vertical spacing between waveguides
        
        
        # define a component
        from picazzo.filters.ring import RingRect180DropFilter
        my_ring = RingRect180DropFilter(name = "My_Ring")

        # add the component to the column
        from picazzo.io.fibcoup import IoFibcoup
        my_column.add(my_ring,
                      offset = (50,50),          # offset the structure from the center
                      adapter = IoFibcoup,          # this is the default adapter.
                      transformation = Rotation(rotation=10.0)) # transform the structure
        
        elems += my_column
        return elems


my_layout = ExampleColumnParameters1(name = "MyLayout")
my_layout.write_gdsii("column_parameters_1.gds")    
    
class ExampleColumnParameters2(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        my_column = IoColumnGroup(south_east = (2000.0,0.0),  # column width = 2000um
                                  y_spacing = 25.0)           # vertical spacing between waveguides
        
        
        # define a component
        from picazzo.filters.ring import RingRect180DropFilter
        my_ring = RingRect180DropFilter(name = "My_Ring")

        # add the component to the column
        my_column.add(my_ring,
                      # the following are parameters of the IOFibcoup adapter, which are passed on
                      taper_length = 50.0,                     # taper from component to intermediate waveguide. Default = 300.
                      wg_width = 2.0,                          # width of intermediate waveguide. Default = 3.0
                      trench_width = 2.0,                      # trench width of intermediate waveguide. Default from TECH
                      connect_length = 100.0,                  # horizontal length of Fanout. Default = 40.0
                      bend_radius = 30.0,                      # bend radius of Fanout. Default from TECH 
                      minimum_straight = 8.0,                  # minimum straight sections
                      fibcoup = TECH.IO.FIBCOUP.DEFAULT_GRATING ,# default fiber coupler
                      fibcoup_offset = 30.0,                   # offset of grating coupler from the edge. Default = 25.6
                      fibcoup_taper_length = 200.0,            # Taper length from intermedeate waveguide to fiber coupler
                      merged_waveguides = False                # bundle waveguide in Fanout
                      )    
        elems += my_column
        return elems
    
    
my_layout = ExampleColumnParameters2(name = "MyLayout2")
my_layout.write_gdsii("column_parameters_2.gds")