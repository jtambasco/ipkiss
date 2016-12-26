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

# our basic component that we will use...
from picazzo.filters.ring import RingRect180DropFilter
my_ring = RingRect180DropFilter(name = "My_Ring")

from picazzo.container import FanoutPorts

# fanout using default parameters
my_ring_fanout = FanoutPorts(structure = my_ring,
                              port_labels = ["E0", "E1"],
                              output_direction = EAST)
my_ring_fanout.write_gdsii("fanout_ports_1.gds")

# customizing
my_ring_fanout_2 = FanoutPorts(structure = my_ring,
                               structure_transformation = Rotation(rotation = 10.0),
                               port_labels = ["E0", "E1"],
                               output_direction = EAST,       
                               spacing = 20.0,                # spacing between outputs
                               reference_coordinate = -12.5,  # y-coordinate (or x for NORTH and SOUTH) of first waveguide
                               target_coordinate = 20.0,      # x-coordinate (or y for NORTH and SOUTH) of output port
                               max_s_bend_angle = 45.0,       # maximum angle of S-bend
                               bend_radius = 4.5,             # bend radius of waveguides
                               bundled = True)                # if True, adds a trench between the waveguides
my_ring_fanout_2.write_gdsii("fanout_ports_2.gds")

# cascading containers to have two fanouts
my_ring_fanout_3 = FanoutPorts(structure = my_ring_fanout,
                              port_labels = ["W0", "W1"],
                              output_direction = WEST,
                              )
my_ring_fanout_3.write_gdsii("fanout_ports_3.gds")

# routing in another direction
my_ring_fanout_4 = FanoutPorts(structure = my_ring,
                              port_labels = ["W0", "W1", "E1", "E0"], 
                              reference_coordinate = -37.5,
                              output_direction = NORTH) 
my_ring_fanout_4.write_gdsii("fanout_ports_4.gds")

# limitation: overlapping waveguides
my_ring_fanout_5 = FanoutPorts(structure = my_ring,
                              port_labels = ["E0", "E1", "W0", "W1"], 
                              output_direction = EAST)
my_ring_fanout_5.write_gdsii("fanout_ports_5.gds")
# limited workaround: reordering the ports
my_ring_fanout_5 = FanoutPorts(structure = my_ring,
                              port_labels = ["W0", "E0", "E1", "W1"], # it can be fixed by picking the right order
                              reference_coordinate = -37.5,           # and manually fixing the reference y
                              output_direction = EAST)
my_ring_fanout_5.write_gdsii("fanout_ports_5b.gds")

