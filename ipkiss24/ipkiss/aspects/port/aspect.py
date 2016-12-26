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

from ipcore.all import FloatProperty
from ipkiss.geometry.transformable import StoredTransformable
from .port_list import PortListProperty
from ipkiss.aspects.aspect import __Aspect__
#from pysics.basics.domain import *
        
__all__ = ["PortAspect", "StructurePortAspect", "ElementPortAspect", "SRefPortAspect", "ARefPortAspect"]

class PortAspect(__Aspect__):
    
    ports = PortListProperty(fdef_name = "__define_ports__") 
    port_angle_decision = FloatProperty(default = 90.0) #spreading angle to deterlmine west, east, north and south ports       

    def __define_ports__(self, ports):
        return self.define_ports(ports)
    
    def define_ports(self, ports):
        return ports

    
    def define_in_ports(self, ports):
        return self.ports.in_ports
    in_ports = PortListProperty(locked = True)

    def define_out_ports(self, ports):
        return self.ports.out_ports
    out_ports = PortListProperty(locked = True)
    
    def get_ports_within_angles(self, start_angle, end_angle):
        p = self.ports
        return p.get_ports_within_angles(start_angle, end_angle)

    def define_west_ports(self, ports):
        return self.get_ports_within_angles(180.0 - 0.5 * self.port_angle_decision, 180.0 + 0.5 * self.port_angle_decision)
    west_ports = PortListProperty(locked = True)

    def define_east_ports(self, ports):
        return self.get_ports_within_angles(- 0.5 * self.port_angle_decision, + 0.5 * self.port_angle_decision)
    east_ports = PortListProperty(locked=True)

    def define_north_ports(self, ports):
        return self.get_ports_within_angles(90.0 - 0.5 * self.port_angle_decision, 90.0 + 0.5 * self.port_angle_decision)
    north_ports = PortListProperty(locked=True)

    def define_south_ports(self, ports):
        return self.get_ports_within_angles(270.0 - 0.5 * self.port_angle_decision, 270.0 + 0.5 * self.port_angle_decision)
    south_ports = PortListProperty(locked=True)
    
    def get_ports_on_domain(self, domain):
        return self.ports.get_ports_on_domain(domain)
    
    def get_ports_on_process(self, process):
        return self.ports.get_ports_on_process(process)

    def get_ports_from_labels(self, labels):
        return self.ports.get_ports_from_labels(labels)

    def get_ports_not_from_labels(self, labels):
        return self.ports.get_ports_not_from_labels(labels)

    def invert_ports(self):
        self.ports = self.ports.invert()
        return self



class TransformablePortAspect(PortAspect, StoredTransformable):
    def __define_ports__(self, ports):
        return self.define_ports(ports).transform_copy(self.transformation)
 
#Structure.mixin_first(OpticalPortAspect)
#__Element__.mixin_first(TransformableOpticalPortAspect)

class SRefPortAspect(TransformablePortAspect):
    
    def define_ports(self, ports):
        ports = self.reference.ports.transform_copy(self.transformation).move(self.position).transform(-self.transformation)
        return ports
    
#SRef.mixin(__SRefOpticalPortMixin__)


class ARefPortAspect(TransformablePortAspect):
    
    def define_ports(self, ports):
        for p in self.positions:
            port_list = self.reference.ports.transform_copy(self.transformation).move(p).transform(-self.transformation)
            ports.extend(port_list)
        return ports
    
#ARef.mixin(__ARefOpticalPortMixin__)

StructurePortAspect = PortAspect
ElementPortAspect = TransformablePortAspect


        
    
