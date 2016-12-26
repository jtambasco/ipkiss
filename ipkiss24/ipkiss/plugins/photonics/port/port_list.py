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

from ipkiss.geometry.transformable import *
from ipkiss.all import *
from .port import OpticalPort, VerticalOpticalPort
from ipkiss.aspects.port.port_list import PortList, PortListProperty

__all__ = ["OpticalPortList",
           "VerticalOpticalPortList",
           "OpticalPortListProperty",
           "VerticalOpticalPortListProperty"
           ] 
    
class OpticalPortList(PortList):
    __item_type__ = OpticalPort
    port_angle_decision = FloatProperty(default = 90.0)
    
    def get_in_ports(self):
        from .port import InOpticalPort
        pl = self.__class__()
        for p in self:
            if isinstance(p, InOpticalPort):
                pl.append(p)
        return pl
    in_ports = property(get_in_ports)

    def get_out_ports(self):
        from .port import OutOpticalPort
        pl = self.__class__()
        for p in self:
            if isinstance(p, OutOpticalPort):
                pl.append(p)
        return pl
    out_ports = property(get_out_ports)
            

class VerticalOpticalPortList(OpticalPortList):
    __item_type__ = VerticalOpticalPort

class OpticalPortListProperty(PortListProperty):
    __list_type__ = OpticalPortList    

class VerticalOpticalPortListProperty(PortListProperty):
    __list_type__ = VerticalOpticalPortList    
    