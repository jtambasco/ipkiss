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

# illustrate how to stack many Structures on top of one another
class ExampleStacking(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        my_column = IoColumnGroup(south_east = (2000.0,0.0),
                                  y_spacing = 25.0) 
        
        
        from picazzo.filters.ring import RingRect180DropFilter
        for r in [5.0, 6.0, 7.0]:
            my_ring = RingRect180DropFilter(bend_radius = r)
            my_column.add(my_ring)
        my_column.add_blocktitle("RING")
        
        elems += my_column
        return elems

my_layout = ExampleStacking(name = "MyLayout1")
my_layout.write_gdsii("column_stacking_1.gds")

# illustrates how stacking structures with unequal number
# of ports may lead to an excessive asymmetry and errors
class ExampleStacking2(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        my_column = IoColumnGroup(south_east = (2000.0,0.0),
                                  y_spacing = 25.0) 
        
        
        from picazzo.filters.ring import RingRect180DropFilter
        from picazzo.container import RoutePortsAroundCorner
        for r in [5.0, 6.0, 7.0]:
            my_ring = RingRect180DropFilter(bend_radius = r)
            my_ring_routed = RoutePortsAroundCorner(structure = my_ring,
                                                    port_labels = ["W1"],
                                                    first_step_direction = NORTH,
                                                    output_direction = EAST,
                                                    spacing = 5.0,
                                                    ) # routes add port to the east
            my_column.add(my_ring_routed)
        my_column.add_blocktitle("RING")
        
        elems += my_column
        return elems

my_layout = ExampleStacking2(name = "MyLayout2")
my_layout.write_gdsii("column_stacking_2.gds")


# illustrates how the 'straighten' command may help to 
# level both sides of the column
class ExampleStackAndStraighten(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        my_column = IoColumnGroup(south_east = (2000.0,0.0),
                                  y_spacing = 25.0) 
        
        
        from picazzo.filters.ring import RingRect180DropFilter
        from picazzo.container import RoutePortsAroundCorner
        for r in [5.0, 6.0, 7.0]:
            my_ring = RingRect180DropFilter(bend_radius = r)
            my_ring_routed = RoutePortsAroundCorner(structure = my_ring,
                                                    port_labels = ["W1"],
                                                    first_step_direction = NORTH,
                                                    output_direction = EAST,
                                                    spacing = 5.0,
                                                    ) # routes add port to the east
            my_column.add(my_ring_routed)
            my_column.add_emptyline_west(2)

        my_column.add_blocktitle("RING")
        elems += my_column
        return elems

my_layout = ExampleStackAndStraighten(name = "MyLayout3")
my_layout.write_gdsii("column_stacking_3.gds")

# illustrates how the 'straighten' command may help to 
# level both sides of the column
class ExampleStackAndStraighten2(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        my_column = IoColumnGroup(south_east = (2000.0,0.0),
                                  y_spacing = 25.0) 
        
        
        from picazzo.filters.ring import RingRect180DropFilter
        from picazzo.container import RoutePortsAroundCorner
        for r in [5.0, 6.0, 7.0]:
            my_ring = RingRect180DropFilter(bend_radius = r)
            my_ring_routed = RoutePortsAroundCorner(structure = my_ring,
                                                    port_labels = ["W1"],
                                                    first_step_direction = NORTH,
                                                    output_direction = EAST,
                                                    spacing = 5.0,
                                                    ) # routes add port to the east
            my_column.add(my_ring_routed)
            my_column.straighten()

        my_column.add_blocktitle("RING")
        elems += my_column
        return elems

my_layout = ExampleStackAndStraighten2(name = "MyLayout4")
my_layout.write_gdsii("column_stacking_4.gds")

class ExampleStackAndStraighten3(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        my_column = IoColumnGroup(south_east = (2000.0,0.0),
                                  y_spacing = 25.0) 
        
        
        from picazzo.filters.ring import RingRect180DropFilter
        from picazzo.container import RoutePortsAroundCorner
        for r in [25.0, 30.0, 35.0]: # we make the rings 5 times larger
            my_ring = RingRect180DropFilter(bend_radius = r)
            my_ring_routed = RoutePortsAroundCorner(structure = my_ring,
                                                    port_labels = ["W1"],
                                                    first_step_direction = NORTH,
                                                    output_direction = EAST,
                                                    spacing = 5.0,
                                                    ) # routes add port to the east
            my_column.add(my_ring_routed)
            my_column.straighten_to_north() # levels out both sides, taking into account the 
                                          # size of the last structure in the middle

        my_column.add_blocktitle("RING")
        elems += my_column
        return elems

my_layout = ExampleStackAndStraighten3(name = "MyLayout5")
my_layout.write_gdsii("column_stacking_5.gds")
