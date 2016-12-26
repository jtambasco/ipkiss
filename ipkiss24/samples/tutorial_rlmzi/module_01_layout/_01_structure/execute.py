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


from ring import RingResonator

# documentation for your class
print RingResonator.__doc__

# create a new ringResonator object
my_ring = RingResonator(ring_radius = 5.0)

print my_ring.name # unique name with prefix

# change property
my_ring.ring_wg_width = 0.6

# my_ring.bus_wg_width = 2.0 
# The command above will throw an error because the spacing between the 
# waveguides is too narrow

  
      