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

from ..socket import BroadWgSocket
from ..basic import FiberCouplerGratingAuto
from ..basic.layout import __AutoSocket__
from ..grating.layout import __UnitCell__, __AutoUnitCell__
from ..grating import GratingUniformLine
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.all import *

__all__ = ["UniformLineGrating"]

class FiberCouplerGratingUniform(__UnitCell__, FiberCouplerGratingAuto):
    period = PositiveNumberProperty(required = True)
    origin = Coord2Property(required= True)
    n_o_periods = IntProperty(restriction = RESTRICT_POSITIVE, required = True)

    def __get_grating__(self):
        return (GratingUniform(self.unit_cell, self.origin, (self.period, 1.0), (self.n_o_periods, 1)), None)


###############################################################################
## uniform grating
###############################################################################
class UniformLineGrating(__AutoUnitCell__, __AutoSocket__, FiberCouplerGratingUniform):
  
    line_width = PositiveNumberProperty(required = True)
    wg_definition = WaveguideDefProperty(required = True)
    wg_length = PositiveNumberProperty(default = 50.0)
    process = ProcessProperty(default = TECH.PROCESS.FC)
     
    def __get_grating__(self):
        return (GratingUniformLine(self.line_width, 
                                   self.wg_definition.wg_width+self.wg_definition.trench_width, 
                                   self.period, 
                                   self.n_o_periods, 
                                   TECH.PURPOSE.DF.TRENCH, 
                                   self.process
                                   ), 
                None)
    
    def __get_socket_and_pos__(self):
        socket = BroadWgSocket(wg_definition = self.wg_definition, wg_length = self.wg_length)
        socket_position = Coord2(-self.wg_length*0.5, 0.0)
        return (socket, socket_position)

