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



from ..basic import FiberCoupler
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.all import *

class FiberCouplerCleave(FiberCoupler):
    """ fiber coupler grating base class, which combines a grating on top of an aperture """
    wg_definition = WaveguideDefProperty(required=True)
    wg_length = PositiveNumberProperty(default = 1000.0)
    wg = DefinitionProperty(fdef_name = "define_wg")

    def define_wg(self):
        return self.wg_definition(shape = [(0.0, 0.0), (self.wg_length, 0.0)])
        
    def define_elements(self, elems):
        elems += self.wg
        return elems

    def define_ports(self, ports):
        return self.wg.ports
    
    
