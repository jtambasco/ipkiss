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

from picazzo.container import TaperDeepPorts
from ipkiss.plugins.photonics.wg import WgElDefinition
my_ring_tapered = TaperDeepPorts(structure = my_ring,
                                    port_labels = ["W0", "E0", "E1"],
                                    end_wg_def = WgElDefinition(wg_width = 0.7))
my_ring_tapered.write_gdsii("taper_ports_1.gds")



from picazzo.wg.wgdefs.wg_fc import ShallowWgElDefinition
my_shallow_wg = ShallowWgElDefinition(wg_width = 0.6) # a shallow etched waveguide
my_shallow_ring = RingRect180DropFilter(name = "My_Shallow_Ring",
                                ring_wg_definition = my_shallow_wg,
                                coupler_wg_definitions = [my_shallow_wg, my_shallow_wg],
                                coupler_spacings = [0.8, 0.8])

from picazzo.container import TaperShallowPorts
my_shallow_ring_tapered = TaperShallowPorts(structure = my_shallow_ring,
                                    port_labels = ["W0", "E0", "E1"],
                                    )
my_shallow_ring_tapered.write_gdsii("taper_ports_2.gds")
