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
from ring import RingResonator, RingResonatorWithDisc
from double_ring import TwoRings


my_ring1 = RingResonator(ring_radius = 5.0)
my_ring2 = RingResonatorWithDisc(ring_radius = 6.0, disc_radius = 2.0)

my_two_rings = TwoRings(ring1 = my_ring1, ring2 = my_ring2)

my_two_rings.write_gdsii("tworings.gds")

print my_two_rings.ports








