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
from ring import RingResonator

class TwoRings(Structure):
    """ structure with two rings defined by the user, which are stacked 
        vertically, with the bottom one flipped. """
    __name_prefix__ = "TWORING"
    ring1 = DefinitionProperty(restriction = RestrictType(RingResonator))
    ring2 = DefinitionProperty(restriction = RestrictType(RingResonator))
    
    def get_transformations(self):
        # calculate the transformations of the rings based on their properties
        t1 = Translation((0.0, self.ring1.ring_radius + 5.0))
        t2 = VMirror() + Translation((0.0, -self.ring2.ring_radius - 5.0))
        return (t1, t2)
    
    def define_elements(self, elems):
        t1, t2 = self.get_transformations()
        
        # Single References (SREF) place a copy of the layout at a given position with 
        # transformation. This is a reference copy, so the layout data is not duplicated.
        elems += SRef(reference = self.ring1, transformation = t1)
        elems += SRef(reference = self.ring2, transformation = t2)
        return elems
    
    def define_ports(self, prts):
        t1, t2 = self.get_transformations()
        prts += self.ring1.ports.transform_copy(t1)
        prts += self.ring2.ports.transform_copy(t2)
        return prts
    
        