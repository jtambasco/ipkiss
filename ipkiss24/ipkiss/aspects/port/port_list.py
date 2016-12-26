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

from ipcore.all import *
from ipkiss.constants import *
from ipkiss.geometry.size_info import size_info_from_point_list
from ipkiss.geometry.transformable import *
from .port import __Port__, __OutOfPlanePort__

__all__ = ["PortList", "PortListProperty"]

class PortList(TypedList, Transformable):
    __item_type__ = __Port__
    port_angle_decision = FloatProperty(default = 90.0)
    def move(self, position):
        for c in self:
            c.move(position)
        return self

    def move_copy(self, position):
        T = self.__class__()
        for c in self:
            T.append(c.move_copy(position))
        return T

    def transform_copy(self, transformation):
        T = self.__class__()
        for c in self:
            T.append(c.transform_copy(transformation))
        return T

    def transform(self, transformation):
        for c in self:
            c.transform(transformation)
        return self

    def invert(self):
        for c in self:
            c.invert()
        return self

    def invert_copy(self):
        L = self.__class__()
        for c in self:
            L += c.invert_copy()
        return L

    def size_info(self):
        return size_info_from_point_list(self)
    
    
    def y_sorted(self):
        """return a copy of the list sorted on the y position"""
        return self.__class__(sorted(self, key=lambda f: f.position[1]))
    
    def y_sorted_backward(self):
        """return a copy of the list reverse sorted on the y position"""
        return self.__class__(sorted(self, key=lambda f: (-f.position[1])))
    
    def x_sorted(self):
        """return a copy of the list sorted on the x position"""
        return self.__class__(sorted(self, key=lambda f: f.position[0]))
    
    def x_sorted_backward(self):
        """return a copy of the list reverse sorted on the x position"""
        return self.__class__(sorted(self, key=lambda f: (-f.position[0])))
    
    def sorted_in_direction(self, direction):
        if direction == NORTH:
            return self.y_sorted()
        elif direction == SOUTH:
            return self.y_sorted_backward()
        elif direction == EAST:
            return self.x_sorted()
        elif direction == WEST:
            return self.x_sorted_backward()
        else:
            raise AttributeError("direction in OpticalPortList.sorted_in_direction() should be NORTH, EAST, SOUTH or WEST")
    
    def angle_sorted(self, reference_angle=0.0):
        """ sorts ports by angle, using angles between the reference_angle and reference_angle+360 """
        return self.__class__(sorted(self, key=lambda f: ((f.angle_deg - reference_angle) % 360.0)))
        
    def angle_sorted_backward(self, reference_angle=0.0):
        """ sorts ports by angle, using angles between the reference_angle and reference_angle+360 """
        return self.__class__(sorted(self, key=lambda f: (-(f.angle_deg - reference_angle) % 360.0)))
    
    def get_in_ports(self):
        from .port import __InPort__
        pl = self.__class__()
        for p in self:
            if isinstance(p, __InPort__):
                pl.append(p)
        return pl
    in_ports = property(get_in_ports)

    def get_out_ports(self):
        from .port import __OutPort__
        pl = self.__class__()
        for p in self:
            if isinstance(p, __OutPort__):
                pl.append(p)
        return pl
    out_ports = property(get_out_ports)
    
    def get_ports_within_angles(self, start_angle, end_angle):
        pl = self.__class__()
        aspread = (end_angle - start_angle) % 360.0
        sa = start_angle % 360.0
        ea = sa + aspread
        for p in self:
            if isinstance(p, __OutOfPlanePort__):
                continue
            a = (p.angle_deg - sa) % 360.0
            if a <= aspread: pl.append(p)
        return pl    

    def get_ports_on_domain(self, domain):
        pl = self.__class__()
        for p in self:
            if p.domain == domain: pl.append(p)
        return pl
    
    def get_ports_on_process(self, process):
        pl = self.__class__()
        for p in self:
            if p.process == process: pl.append(p)
        return pl    

    def get_ports_from_labels(self, labels):
        P = self.__class__()
        for i in labels:
            P += self.get_from_label(i)
        return P

    def get_ports_not_from_labels(self, labels):
        P = self.__class__()
        LP = self.get_ports_from_labels(labels)
        for p in self:
            if not p in LP:
                P += p
        return P

    def get_from_label(self, label):
        D = label[0]
        if D == "I":
            portl = self.in_ports
        elif D == "O":
            portl = self.out_ports
        elif D == "N":
            portl = self.north_ports.x_sorted()
        elif D == "S":
            portl = self.south_ports.x_sorted()
        elif D == "W":
            portl = self.west_ports.y_sorted()
        elif D == "E":
            portl = self.east_ports.y_sorted()
        else:
            raise AttributeError("Invalid Port label: %s" % label)
        if label[1:] == "*":
            port = portl
        else:
            N = int(label[1:])
            port = portl[N] 
        return port
    
    def get_port_index_from_label(self, label):
        p = self.get_from_label(label)
        index = 0
        while self[index] != p:
            index = index + 1
        return index        
    
    def get_west_ports(self):
        return self.get_ports_within_angles(180.0 - 0.5 * self.port_angle_decision, 180.0 + 0.5 * self.port_angle_decision)
    west_ports = property(get_west_ports)

    def get_east_ports(self):
        return self.get_ports_within_angles(-0.5 * self.port_angle_decision, +0.5 * self.port_angle_decision)
    east_ports = property(get_east_ports)

    def get_north_ports(self):
        return self.get_ports_within_angles(90.0 - 0.5 * self.port_angle_decision, 90.0 + 0.5 * self.port_angle_decision)
    north_ports = property(get_north_ports)

    def get_south_ports(self):
        return self.get_ports_within_angles(270.0 - 0.5 * self.port_angle_decision, 270.0 + 0.5 * self.port_angle_decision)
    south_ports = property(get_south_ports)
    
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return list.__getitem__(self, key)
        else:
            return self.get_from_label(key)
        
class PortListProperty(DefinitionProperty):
    __list_type__ = PortList
    """Property type for storing a list of Ports."""
    
    def __init__(self, internal_member_name=None, **kwargs):
        kwargs["restriction"] = RestrictType(allowed_types=[self.__list_type__])
        super(PortListProperty, self).__init__(internal_member_name=internal_member_name, **kwargs)
                           
    def __call_getter_function__(self, obj):
        f = self.__get_getter_function__(obj)        
        value = f(self.__list_type__())
        if (value is None):
            value = self.__list_type__()
        self.__cache_property_value_on_object__(obj, value)
        value = self.__get_property_value_of_object__(obj)        
        return value
    
    def __cache_property_value_on_object__(self, obj, ports):
        if isinstance(ports, self.__list_type__):
            super(PortListProperty, self).__cache_property_value_on_object__(obj, ports)
        elif isinstance(ports, list):
            super(PortListProperty, self).__cache_property_value_on_object__(obj, self.__list_type__(ports))           
        else:
            raise TypeError("Invalid type in setting value of PortListProperty (expected PortList), but generated : " + str(type(ports)))
        
    def __set__(self, obj, ports):
        if isinstance(ports, self.__list_type__):
            self.__externally_set_property_value_on_object__(obj, ports)
        elif isinstance(ports, list):
            self.__externally_set_property_value_on_object__(obj, self.__list_type__(ports))            
        else:
                raise TypeError("Invalid type in setting value of PortListProperty (expected PortList): " + str(type(ports)))
        return

