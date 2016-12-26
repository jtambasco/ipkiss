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

__all__ = ["HexHole", "DodecHole"]

class __RoundHole__(Structure):
    process = ProcessProperty(default = TECH.PROCESS.WG)
    radius = PositiveNumberProperty(required = True)
    angle = AngleProperty(default = 90.0)
    center = Coord2Property(default = (0.0, 0.0))
    purpose = PurposeProperty(default = TECH.PURPOSE.DF.HOLE)
    
    def define_name(self):
        return "%s_%d_C%d_%d_A%d_P%s_PP%s" % (self.__name_prefix__ , 
                                     self.radius * 1000, 
                                     self.center.x * 1000, self.center.y * 1000,
                                     self.angle*1000,self.process.extension,self.purpose.extension)

class HexHole(__RoundHole__):
    __name_prefix__ = "HEX"

    def define_elements(self, elems):
        sh = ShapeHexagon(center = self.center, radius = self.radius).rotate( (0.0, 0.0), self.angle)
        elems += Boundary(PPLayer(self.process, self.purpose), sh)
        return elems

class DodecHole(__RoundHole__):
    __name_prefix__ = "DODEC"

    def define_elements(self, elems):
        sh = ShapeRegularPolygon(center = self.center, radius = self.radius, n_o_sides = 12).rotate((0.0, 0.0), self.angle)
        elems += Boundary(PPLayer(self.process, self.purpose), sh)
        return elems

