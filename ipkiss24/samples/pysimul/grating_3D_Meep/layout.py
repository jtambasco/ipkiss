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


from copy import *
from numpy import *
from ipkiss.all import *

from ipkiss.plugins.photonics.port.port import OpticalPort
from ipkiss.plugins.photonics.port.port_list import OpticalPortList



##############################################################################
## Grating periods
##############################################################################

from picazzo.wg.grating.layout import __WgGratingPeriod__, WgGrating

class WgGratingPeriodShallow(__WgGratingPeriod__):
    __name_prefix__ = "MY_WG_GPS_"
    fill_factor = RestrictedProperty(restriction = RESTRICT_FRACTION, default = 0.5)
    deep_process = ProcessProperty(default = TECH.PROCESS.WG)
    shallow_process = ProcessProperty(default = TECH.PROCESS.FC)
    grating_trench = NumberProperty(default = 0.5)
        
    def define_elements(self, elems):
        elems += Line(layer = PPLayer(self.shallow_process, TECH.PURPOSE.DF.TRENCH),
                      begin_coord = ((0.5 - self.fill_factor/2.0) * self.length, 0.), 
                      end_coord = ((0.5+self.fill_factor/2.0)*self.length, 0.), 
                      line_width = self.wg_definition.wg_width+2.*self.grating_trench
                      )
        
        return elems

    def define_ports(self, prts):
        prts += [OpticalPort(position = (0.0, 0.0), angle = -180.0, wg_definition = self.wg_definition),
                OpticalPort(position = (self.length, 0.0), angle = 0.0, wg_definition = self.wg_definition)]
        return prts
