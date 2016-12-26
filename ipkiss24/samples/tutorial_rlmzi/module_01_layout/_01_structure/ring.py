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

# Example: Definition of a PCell Structure with Properties
#

from ipkiss.all import *

#
# We will define a Ring Resonator Structure which consists of
# a ring waveguide with evalescent coupling to a bus waveguide
# 

class RingResonator(Structure):
    """ A generic ring resonator class, defined by a circular waveguide
        evanescently coupled to a straight bus waveguide """
    
    __name_prefix__ = "RINGRES" # a prefix added to the unique identifier 
        
    ring_radius     = PositiveNumberProperty(required = True)
    ring_wg_width   = PositiveNumberProperty(default = 0.5)
    bus_wg_width    = PositiveNumberProperty(default = 0.5)
    coupler_spacing = PositiveNumberProperty(default = 1.0, 
                                             doc = "spacing between centerline of bus waveguide and ring waveguide")
                                             
    def validate_properties(self):
        """ check whether the combination of properties is valid """
        if self.coupler_spacing <= 0.5*(self.ring_wg_width + self.bus_wg_width):
            return False # waveguides would touch: Not OK 
        if self.ring_radius < self.ring_wg_width:
            return False # ring would become a disc
        return True # no errors


# The code below is only executed if this python file is run directly.
# As this is only contains a library component, we should call it from
# another file. In this case, it is 'execute.py'
if __name__ == "__main__":
    print "This is not the main file. Run 'execute.py' in the same folder"