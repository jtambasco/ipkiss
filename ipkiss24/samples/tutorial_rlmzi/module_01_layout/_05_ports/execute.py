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

from technologies.si_photonics.ipkiss.default import *
from ipkiss.all import *

# load the file with our RingResonator component
from ring import RingResonator

# create a new ringResonator object
my_ring = RingResonator(ring_radius = 5.0)

print my_ring.ports
print my_ring.ports.east_ports # ports pointing east
print my_ring.ports.east_ports.y_sorted() # ports pointing east, sorted south to north
print my_ring.ports.north_ports # ports pointing north (none)
print my_ring.ports["E0"] #first port in the list east_ports.y_sorted()









