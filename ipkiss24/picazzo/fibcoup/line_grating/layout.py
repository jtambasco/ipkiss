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

from ..basic import FiberCouplerGratingAuto
from ..grating import GratingUniform
from ipkiss.all import *

__all__ = ["GratingLine",
           "FiberCouplerGratingLine"]

class __GratingLine__(StrongPropertyInitializer):
    line_widths_positions = RestrictedProperty(restriction = RestrictList(RESTRICT_NUMBER_TUPLE2), required = True)
    line_length = PositiveNumberProperty(required = True)
    purpose = PurposeProperty(default = TECH.PURPOSE.DF.TRENCH)

class GratingLine(__GratingLine__,Structure):
    """ grating with lines, with given widths and positions, and given length.
        line_widths_positions should be a list of tuples:
        [ (w1, x1), (w2, x2), (w3, x3), ...] with w the line width and x the x position
        """
    __name_prefix__ = "gratingl_"
    process = ProcessProperty(default = TECH.PROCESS.FC)

    def define_elements(self, elems):
        for (w,x) in self.line_widths_positions:
            elems += Line(PPLayer(self.process, self.purpose), (x, 0.0), (x + w, 0.0), self.line_length)
        return elems

class FiberCouplerGratingLine(FiberCouplerGratingAuto,GratingLine):
    """ grating line on a socket """
    __name_prefix__ = "fc_gratingl_"
        
    def __get_grating__(self):
        return (GratingLine(line_widths_positions=self.line_widths_positions, 
                            line_length=self.line_length, 
                            purpose=self.purpose, 
                            process=self.process), 
                None)


