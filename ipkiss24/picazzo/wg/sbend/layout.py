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
from ..bend.layout import __WgElBend__
import math

__all__ = ["WgElSBend"]

class WgElSBend(__WgElBend__):
    __name_prefix__ = "wgelsbend"
    straight = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
        
    @cache()
    def get_control_shape(self):
        bs1, bs2 = self.get_bend_size(self.angle)
        cs = Shape([(-bs1, 0.0),
                    (0.0, 0.0), 
                    ((bs1+bs2+self.straight) * math.cos(self.angle*DEG2RAD), (bs1+bs2+self.straight) * math.sin(self.angle * DEG2RAD))
                    ])

        cs.add_polar(bs2, 0.0)
        cs.move(-cs[0])
        cs.rotate(rotation = self.start_angle)
        cs.move(self.start_point)
        return cs

  
        
