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



from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.all import *

__all__ = ["IoArray",
           "IoPeriodicArray",
           "IoRegularArray"]

class IoArray(Structure):
    __name_prefix__ = "io_array" 
    fibcoups = RestrictedProperty(restriction = RestrictTypeList(Structure), required = True)
    positions = ShapeProperty(required = True)

    def define_name(self):
        return "%s_%d_%d" % (
            self.__name_prefix__,
            do_hash("".join([f.name for f in self.fibcoups])),
            do_hash("".join([p for p in self.positions]))
            )
    
    def define_elements(self, elems):       
        for i in range(len(self.fibcoups)):
            elems += SRef(self.fibcoups[i],self.positions[i])
        return elems
            
    def define_ports(self, ports):
        for i in range(0,len(self.fibcoups)):
            ports += self.io_fibcoups[i].ports.move_copy(self.positions[i])
        return ports


class IoRegularArray(IoArray):
    __name_prefix__ = "io_reg_array" 
    positions = DefinitionProperty(fdef_name = "define_positions")
    spacing = PositiveNumberProperty(default = 250.0)

    def define_name(self):
        return "%s_%d_%d" % (
            self.__name_prefix__,
            do_hash("".join([f.name for f in self.fibcoups])),
            self.spacing)
    
    def define_positions(self):
        return [(0.0,i * self.spacing) for i in range(len(self.fibcoups))]
    
    def define_elements(self, elems):       
        for i in range(len(self.fibcoups)):
            elems += SRef(self.fibcoups[i],self.positions[i])
        return elems
            
    def define_ports(self, ports):
        for i in range(0,len(self.fibcoups)):
            ports += self.fibcoups[i].ports.move_copy(self.positions[i])
        return ports


class IoPeriodicArray(IoRegularArray):
    __name_prefix__ = "io_per_array" 
    
    fibcoups = DefinitionProperty(fdef_name = "define_fibcoups")
    fibcoup = StructureProperty(required = True)
    n_o_fibcoup = IntProperty(restriction = RESTRICT_POSITIVE, default = 4)
 
    def define_name(self):
        return "%s_%s_%d_%d" % (
            self.__name_prefix__,
            self.fibcoup.name,
            self.n_o_fibcoup,
            self.spacing * 1000)

    def define_fibcoups(self):
        return [self.fibcoup for i in range(self.n_o_fibcoup)]
    
    def define_elements(self, elems):       
        elems += ARefY(self.fibcoup,(0.0,0.0),self.spacing,self.n_o_fibcoup)
        return elems
            
    def define_ports(self, ports):
        for i in range(0,self.n_o_fibcoup):
            ports += self.fibcoup.ports.move_copy(self.positions[i])
        return ports
