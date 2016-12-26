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

from picazzo.container import RoutePortsEastWest

## Routing using default parameters
#my_ring_ew = RoutePortsEastWest(structure = my_ring,
                                #ports_to_east = ["E0", "E1", "W1" ],   # ports to be routed eastwards
                                #ports_to_west = ["W0"]                 # ports to be routed westwards
                                #)       
#my_ring_ew.write_gdsii("route_east_west_1.gds")

# customize all parameters
from ipkiss.geometry.shapes.spline import SplineRoundingAlgorithm

my_ring_ew_2 = RoutePortsEastWest(structure = my_ring,
                                  structure_transformation = Rotation(rotation = -20.0),
                                  ports_to_east = ["E0", "E1", "W1" ],   
                                  ports_to_west = ["W0"],
                                  reference_east = "E0",    # Port that serves as y-reference 
                                  reference_west = "W0",    # Port that serves as y-reference
                                  spacing = 17.0,           # vertical spacing between outputs
                                  manhattan = True,         # add suares on corners
                                  bend_radius = 3.0,        # bend radius of the waveguides
                                  rounding_algorithm = SplineRoundingAlgorithm(adiabatic_angles = (10.0, 10.0))
                                  )       
my_ring_ew_2.write_gdsii("route_east_west_2.gds")
