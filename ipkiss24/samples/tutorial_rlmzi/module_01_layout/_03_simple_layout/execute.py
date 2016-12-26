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

my_ring.write_gdsii("myring.gds") # fast writing to GDSII

# The proper way is to create a library, add your structure to the library, 
# and export that to GDSII

my_lib = Library(name = "MYLIB")
my_lib += my_ring

FileOutputGdsii("myring2.gds").write(my_lib)

# The second GDSII file will be slightly different from the first, because the
# in the first a default library name is used, while in the second a user-defined
# name is used.


