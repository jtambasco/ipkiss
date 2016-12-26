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

# combining multiple containers
from technologies.si_photonics.picazzo.default import *
from ipkiss.all import *

# our basic component that we will use...
from picazzo.filters.ring import RingRect180DropFilter
from picazzo.wg.wgdefs.wg_fc import ShallowWgElDefinition
from picazzo.wg.aperture import DeepWgAperture
from ipkiss.plugins.photonics.wg import WgElDefinition

my_shallow_wg = ShallowWgElDefinition(wg_width = 0.6) # a shallow etched waveguide
my_shallow_ring = RingRect180DropFilter(name = "My_Shallow_Ring",
                                ring_wg_definition = my_shallow_wg,
                                coupler_wg_definitions = [my_shallow_wg, my_shallow_wg],
                                coupler_spacings = [0.8, 0.8])


from picazzo.container import *
from ipkiss.plugins.photonics.wg import WgElDefinition
# add tapers
my_ring_tapered = AutoTaperPorts(structure = my_shallow_ring,
                                 structure_transformation = Rotation(rotation = 20)) # Easy: taper all ports
my_ring_tapered.write_gdsii('matrioszka_1.gds')

# suppress north-east 'ADD' port
# define a stub
my_stub = DeepWgAperture(name = "my_stub",
                         aperture_wg_definition = WgElDefinition(wg_width = 2.0),
                         taper_length = 4.0)

my_ring_suppressed = SuppressPorts(structure = my_ring_tapered,
                                  port_labels = ["W1"],
                                  stub = my_stub) 
my_ring_suppressed.write_gdsii('matrioszka_2.gds')

# route west ports to the x-axis
my_ring_routed = FanoutPorts(structure = my_ring_suppressed,
                             port_labels = ["W0"],
                             output_direction = WEST
                             )
my_ring_routed.write_gdsii('matrioszka_3.gds')

# route east ports to the West
my_ring_routed_2 = RoutePortsAroundCorner(structure = my_ring_routed,
                                          port_labels = ["E1", "E0"],
                                          first_step_direction = NORTH,  
                                          output_direction = WEST,       
                                          spacing = TECH.WG.SPACING, 
                                          manhattan = True,              
                                          bundled = True)                
my_ring_routed_2.write_gdsii('matrioszka_4.gds')
# do a small fanout (bundled) to arrange waveguides to equal spacing
my_ring_routed_3 = FanoutPorts(structure = my_ring_routed_2,
                               port_labels = ["W0","W1", "W2"],
                               output_direction = WEST,
                               reference_coordinate = 10.0,
                               spacing = 10.0,
                               bundled = True
                             )
my_ring_routed_3.write_gdsii('matrioszka_5.gds')

# do a larger fanout not bundled to obtain fiber-array compatible spacing
my_ring_routed_4 = FanoutPorts(structure = my_ring_routed_3,
                               output_direction = WEST,
                               spacing = 127.5,
                               max_s_bend_angle = 75.0,
                               reference_coordinate = -100.0
                               )
my_ring_routed_4.write_gdsii('matrioszka_6.gds')

# write this one to gdsii without hierarchy
# There is no shortcut for that
L = Library("MYLIB")
L.add(my_ring_routed_4)
O = FileOutputGdsii("matrioszka_7.gds")
O.layer_map = TECH.GDSII.EXPORT_LAYER_MAP
O.flatten_structure_container = True
O.write(L)

