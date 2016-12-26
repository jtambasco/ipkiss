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


from dircoup import BentDirectionalCoupler
from mzi import MZI, MziArmWaveguide, MziArmWithStructure, MZIWithStructures
from ring import RingResonator

my_splitter = BentDirectionalCoupler(coupler_length = 10.0, bend_angle = 30.0) 
my_combiner =  BentDirectionalCoupler(coupler_length = 8.0, bend_angle = 30.0)

my_ring1 = RingResonator(ring_radius = 5.0)
my_ring2 = RingResonator(ring_radius = 6.0)

# Example 1: 
# construct an MZI manually, by defining 2 arms
#
my_combiner_transform = Translation((50, 0))
my_arm1 = MziArmWithStructure(structure = my_ring1,
                              splitter_port = my_splitter.ports["E1"],
                              combiner_port = my_combiner.ports.transform_copy(my_combiner_transform)["W1"])
my_arm2 = MziArmWaveguide(splitter_port = my_splitter.ports["E0"],
                          combiner_port = my_combiner.ports.transform_copy(my_combiner_transform)["W0"],
                          route_south = True,
                          extra_length = 40.0)
my_mzi = MZI(arm1 = my_arm1,
             arm2 = my_arm2,
             splitter = my_splitter,
             combiner = my_combiner,
             combiner_transformation = my_combiner_transform)

my_mzi.write_gdsii("rlmzi1.gds")

# Example 2: 
# use our MZIWithStructure class
#

my_mzi2 = MZIWithStructures(structure2 = my_ring2,
                            splitter = my_splitter,
                            combiner = my_combiner,
                            delay_length = -40.0)

my_mzi2.write_gdsii("rlmzi2.gds")


# Example 3: 
# two rings, one in each arm
#

my_mzi3 = MZIWithStructures(structure1 = my_ring1,
                            structure2 = my_ring2,
                            structure2_transformation = VMirror(),
                            splitter = my_splitter,
                            combiner = my_combiner,
                            delay_length = 20.0)

my_mzi3.write_gdsii("rlmzi3.gds")








