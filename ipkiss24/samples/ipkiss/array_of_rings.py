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

from ipkiss.all import *

#First, we define the basic component, i.e. the ring.
class Ring(Structure):
        radius = FloatProperty(required = True, restriction = RestrictRange(lower = 10.0, upper = 15.0, lower_inc = True, upper_inc = True))

        def define_elements(self, elems):
                elems += CirclePath(Layer(0), radius = self.radius, line_width = 0.5)
                return elems

#We now take this ring as base element for an array (ARef, see 1.1 above)
class ArrayOfRings(Structure):
        ring_radius = FloatProperty(required = True)
        n_of_rings_width = PositiveNumberProperty(required = True)
        n_of_rings_height = PositiveNumberProperty(required = True, restriction = RestrictRange(lower = 5, upper = 7, lower_inc = True, upper_inc = True) )
        origin = Coord2Property(required = True)

        def define_elements(self, elems):
                r = Ring(radius = self.ring_radius)
                delta = 2.0*r.radius + 5.0
                elems += ARef(reference = r, origin = self.origin, period = (delta,delta), n_o_periods = (self.n_of_rings_width, self.n_of_rings_height))
                return elems

#we now create an instance of such an array and export to GDS
s = ArrayOfRings(ring_radius = 11.563, n_of_rings_width = 41, n_of_rings_height = 6, origin = (0.0, 0.0))
s.write_gdsii("array_of_rings.gds")


