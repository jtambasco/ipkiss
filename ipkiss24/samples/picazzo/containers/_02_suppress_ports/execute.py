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


from picazzo.container import SuppressPorts
my_ring_suppressed = SuppressPorts(structure = my_ring,
                                   port_labels = ["W1"])
my_ring_suppressed.write_gdsii("suppress_ports_1.gds")
# layout will not look any different 

from picazzo.wg.aperture import DeepWgAperture
from ipkiss.plugins.photonics.wg import WgElDefinition
# a stub to paste on the suppressed ports
my_stub = DeepWgAperture(name = "my_stub",
                         aperture_wg_definition = WgElDefinition(wg_width = 2.0),
                         taper_length = 4.0)
my_ring_stubbed = SuppressPorts(structure = my_ring,
                                port_labels = ["W1"],
                                stub = my_stub)
my_ring_stubbed.write_gdsii("suppress_ports_2.gds")
