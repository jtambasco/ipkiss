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

# Example: Using the ring in a hierarchy
# Nothing has changed here compared to the previous examples.
# The ring is now used as a standard building block

from ipkiss.all import *
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.plugins.photonics.port import OpticalPort

class RingResonator(Structure):
    """ A generic ring resonator class, defined by a circular waveguide
        evanescently coupled to a straight bus waveguide """
    
    __name_prefix__ = "RINGRES" # a prefix added to the unique identifier 
        
    ring_radius     = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    ring_wg_def     = WaveguideDefProperty (default = TECH.WGDEF.WIRE)
    bus_wg_def      = WaveguideDefProperty (default = TECH.WGDEF.WIRE)
    coupler_spacing = PositiveNumberProperty(default = TECH.WG.DC_SPACING, 
                                             doc = "spacing between centerline of bus waveguide and ring waveguide")
                                             
    def validate_properties(self):
        """ check whether the combination of properties is valid """
        if self.coupler_spacing <= 0.5*(self.ring_wg_def.wg_width + self.bus_wg_def.wg_width):
            return False # waveguides would touch: Not OK 
        if self.ring_radius < self.ring_wg_def.wg_width:
            return False # ring would become a disc
        return True # no errors


    def define_elements(self, elems):
        shape_ring = ShapeCircle(center = (0,0), radius = self.ring_radius)
        shape_bus =  [(-self.ring_radius, -self.ring_radius - self.coupler_spacing), 
                      (self.ring_radius, -self.ring_radius - self.coupler_spacing)]
        
        elems += self.ring_wg_def(shape = shape_ring)
        elems += self.bus_wg_def(shape = shape_bus)
        return elems
    
    def define_ports(self, prts):
        prts += [OpticalPort(position = (-self.ring_radius, -self.ring_radius - self.coupler_spacing),
                             angle = 180.0,
                             wg_definition = self.bus_wg_def),
                 OpticalPort(position = (self.ring_radius, -self.ring_radius - self.coupler_spacing),
                             angle = 0.0,
                             wg_definition = self.bus_wg_def)
                 ]
        return prts
    
    
if __name__ == "__main__":
    print "This is not the main file. Run 'execute.py' in the same folder"