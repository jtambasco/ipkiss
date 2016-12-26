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


from picazzo.container.container import __StructureContainer__
# base class of containers. Does nothing except put a structure in a container.
# For other predefined container classes, we can use 
# from picazzo.container import *

my_ring_in_container_1 = __StructureContainer__(structure = my_ring)
my_ring_in_container_1.write_gdsii("container_1.gds")

# put that one in a container with a transformation
my_ring_in_container_2 = __StructureContainer__(structure = my_ring_in_container_1,
                                                structure_transformation = Rotation(rotation=30.0))
my_ring_in_container_2.write_gdsii("container_2.gds")

# write this one to gdsii without hierarchy
# There is no shortcut for that
L = Library("MYLIB")
L.add(my_ring_in_container_2)
O = FileOutputGdsii("container_3.gds")
O.flatten_structure_container = True
O.write(L)
