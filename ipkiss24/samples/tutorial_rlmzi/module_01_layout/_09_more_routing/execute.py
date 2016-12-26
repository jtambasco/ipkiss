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
from dircoup import DirectionalCoupler, BentDirectionalCoupler


my_dircoup_1 = DirectionalCoupler(coupler_length = 10.0) 
my_dircoup_2 = BentDirectionalCoupler(coupler_length = 8.0, 
                                   bend_angle = 30.0,
                                   bend_radius = 10.0)



# create a dumb structure to collect our different directional couplers
my_group = Structure(name = "Group")
my_group += SRef(reference = my_dircoup_1, position = (0,0))
my_group += SRef(reference = my_dircoup_2, position = (0,15))


my_group.write_gdsii("dircoups.gds")









