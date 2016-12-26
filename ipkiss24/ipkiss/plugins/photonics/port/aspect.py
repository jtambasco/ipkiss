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
from .port import *
from .port_list import *
from ipkiss.aspects.port.port_list import PortListProperty, PortList
from ipkiss.aspects.aspect import __Aspect__
from ipkiss.aspects.port.aspect import PortAspect, TransformablePortAspect
from ipkiss.primitives.elements.basic import __Element__
from ipkiss.primitives.elements import SRef, ARef
from pysics.optics import OpticalDomain

__all__ = []

        
class OpticalPortAspect(PortAspect):
    
    def define_optical_ports(self, ports):
        pl = OpticalPortList()
        for p in self.ports.get_ports_on_domain(OpticalDomain):
            if not isinstance(p, VerticalOpticalPort):
                pl.append(p)
        return pl
    optical_ports = OpticalPortListProperty(locked = True)
    
    def define_vertical_optical_ports(self, ports):
        pl = VerticalOpticalPortList()
        for p in self.ports.get_ports_on_domain(OpticalDomain):
            if isinstance(p, VerticalOpticalPort):
                pl.append(p)
        return pl
    vertical_optical_ports = OpticalPortListProperty(locked = True)
      
    def define_optical_in_ports(self):
        return self.optical_ports.in_ports
    optical_in_ports = OpticalPortListProperty(locked = True)

    def define_optical_out_ports(self):
        return self.optical_ports.out_ports
    optical_out_ports = OpticalPortListProperty(locked = True)
    
    def get_optical_ports_within_angles(self, start_angle, end_angle):
        p = self.optical_ports
        return p.get_ports_within_angles(start_angle,end_angle)

    def define_optical_west_ports(self):
        return self.get_optical_ports_within_angles(180.0 - 0.5 * self.port_angle_decision, 180.0 + 0.5 * self.port_angle_decision)
    optical_west_ports = OpticalPortListProperty(locked = True)

    def define_optical_east_ports(self,ports):
        return self.get_optical_ports_within_angles(-0.5 * self.port_angle_decision, +0.5 * self.port_angle_decision)
    optical_east_ports = OpticalPortListProperty(locked = True)

    def define_optical_north_ports(self):
        return self.get_optical_ports_within_angles(90.0 - 0.5*self.port_angle_decision, 90.0 + 0.5 * self.port_angle_decision)
    optical_north_ports = OpticalPortListProperty(locked = True)

    def define_optical_south_ports(self):
        return self.get_optical_ports_within_angles(270.0 - 0.5*self.port_angle_decision, 270.0 + 0.5 * self.port_angle_decision)
    optical_south_ports = OpticalPortListProperty(locked = True)
    
    def get_optical_ports_on_process(self, process):
        return self.optical_ports.get_ports_on_process(process)

    def get_optical_ports_from_labels(self, labels):
        return self.optical_ports.get_ports_from_labels(labels)

    def get_optical_ports_not_from_labels(self, labels):
        return self.optical_ports.get_ports_not_from_labels(labels)

class OpticalPortListAspect(__Aspect__):    
    def define_optical_ports(self):
        pl = OpticalPortList()
        for p in self.get_ports_on_domain(OpticalDomain):
            if not isinstance(p,VerticalOpticalPort):
                pl.append(p)
        return pl
    optical_ports = property(define_optical_ports)
    
class TransformableOpticalPortAspect(OpticalPortAspect, StoredTransformable):
    def define_optical_ports(self, ports):
        return OpticalPortAspect.define_optical_ports(ports).transform_copy(self.transformation)
 
class SRefOpticalPortAspect(TransformableOpticalPortAspect):
    def define_optical_ports(self, ports):
        ports = self.reference.optical_ports.transform_copy(self.transformation).move(self.position).transform(-self.transformation)
        return ports

class ARefOpticalPortAspect(TransformablePortAspect):
    def define_optical_ports(self, ports):
        for p in self.positions:
            port_list = self.reference.optical_ports.transform_copy(self.transformation).move(p).transform(-self.transformation)
            ports.extend(port_list)
        return ports
            
PortList.mixin_first(OpticalPortListAspect)    
Structure.mixin_first(OpticalPortAspect)
__Element__.mixin_first(TransformableOpticalPortAspect)
SRef.mixin_first(SRefOpticalPortAspect)
ARef.mixin_first(ARefOpticalPortAspect)


        
    