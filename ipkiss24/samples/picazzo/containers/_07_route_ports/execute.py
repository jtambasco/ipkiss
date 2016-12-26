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

from picazzo.container import RoutePortsAroundCorner

# Routing using default parameters
my_ring_routed = RoutePortsAroundCorner(structure = my_ring,
                                        port_labels = ["W1", "W0"],    # ports to be routed
                                        first_step_direction = SOUTH,  # when rounding corner, go this direction first
                                        output_direction = EAST)       # final output direction
my_ring_routed.write_gdsii("route_ports_1.gds")

# customizing: similar as fanout
my_ring_routed_2 = RoutePortsAroundCorner(structure = my_ring,
                                          port_labels = ["W1", "W0"],
                                          first_step_direction = SOUTH,  
                                          first_step_spacing = 4.0,      # spacing of wavegudies in the first step
                                          reference_coordinate_first_step = - 15.0,  # x-location of the first vertical waveguide
                                          output_direction = EAST,       
                                          spacing = 20.0,                # spacing between outputs
                                          reference_coordinate = -12.5,  # y-coordinate (or x for NORTH and SOUTH) of first waveguide
                                          target_coordinate = 20.0,      # x-coordinate (or y for NORTH and SOUTH) of output port
                                          manhattan = True,              # Adds rectangles to corners, to reduce sharp angle errors
                                          bundled = True)                # if True, adds a trench between the waveguides
my_ring_routed_2.write_gdsii("route_ports_2.gds")
