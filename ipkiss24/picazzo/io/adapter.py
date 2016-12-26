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



from .block import IoBlock
from ipkiss.all import *
from ..log import PICAZZO_LOG as LOG
import sys
__all__ = ["AdapterProperty"]

#######################################################
# I/O Adapter for horizontal waveguides
#######################################################

class IoBlockAdapter(Structure, IoBlock):
    __name_prefix__ = "io"
    offset = Coord2Property(required = True)
    struct = StructureProperty(required = True)
    struct_transformation = TransformationProperty()
    y_west = DefinitionProperty(fdef_name = "define_y_west")
    y_east = DefinitionProperty(fdef_name = "define_y_east")    
    struct_east_ports = DefinitionProperty(fdef_name = "define_struct_east_ports")    
    struct_west_ports = DefinitionProperty(fdef_name = "define_struct_west_ports")    
    position_west_east_ports = DefinitionProperty(fdef_name = "define_position_west_east_ports")
    

    def define_name(self):
        return "%s_%s_T%s_%d" % (self.__name_prefix__ ,
                                          self.struct.name ,
                                          self.struct_transformation.id_string(),
                                          do_hash(str((str(self.offset) + str(self.y_spacing) + str(self.south_west) + str(self.south_east))))
                                      )
    
    def define_position_west_east_ports(self):
        west_ports = self.struct.optical_ports.transform_copy(self.struct_transformation).west_ports.y_sorted()
        if len(west_ports) == 0:
            LOG.warning("Structure " + self.struct.name + " has no west ports, so no adapters will be added.")
        S_in = west_ports.size_info()
        L = S_in.west
        
        east_ports = self.struct.optical_ports.transform_copy(self.struct_transformation).east_ports.y_sorted()
        if len(east_ports) == 0:
            LOG.warning("Structure " + self.struct.name + " has no east ports, so no adapters will be added.")
        S_out = east_ports.size_info()
        R = S_out.east

        # determine the position
        if R is None and L is None:
            R = 0.0
            L = 0.0
        elif R is None:
            R = L
        elif L is None: 
            L = R
            
        w = R - L
        x = self.south_west[0] + 0.5 * (self.width - w) - L + self.offset[0]
        if len(west_ports) > 0:
            y = self.south_west[1] - west_ports[0][1] + self.offset[1]
        else:
            y = self.south_west[1] + self.offset[1]
        struct_position = Coord2(x, y).snap_to_grid()
        struct_west_ports = west_ports.move_copy(struct_position)
        struct_east_ports = east_ports.move_copy(struct_position)
        return (struct_position, struct_west_ports, struct_east_ports)

        
    def define_elements(self, elems):
        (struct_position, struct_west_ports, struct_east_ports) = self.position_west_east_ports
        elems.append(SRef(self.struct, struct_position, self.struct_transformation))
        return elems
    
    def define_y_west(self):
        (struct_position, struct_west_ports, struct_east_ports) = self.position_west_east_ports
        y_west =  [self.south_west[1] + i * self.y_spacing for i in range(len(struct_west_ports))]
        return y_west
    
    def define_y_east(self):   
        (struct_position, struct_west_ports, struct_east_ports) = self.position_west_east_ports
        y_east = [self.south_east[1] + i * self.y_spacing for i in range(len(struct_east_ports))]        
        return y_east

    def get_count_east(self):
        return len(self.struct.optical_ports.transform_copy(self.struct_transformation).east_ports)

    def get_count_west(self):
        return len(self.struct.optical_ports.transform_copy(self.struct_transformation).west_ports)
    
    def define_struct_west_ports(self):   
        (struct_position, struct_west_ports, struct_east_ports) = self.position_west_east_ports
        return struct_west_ports    
    
    def define_struct_east_ports(self):   
        (struct_position, struct_west_ports, struct_east_ports) = self.position_west_east_ports
        return struct_east_ports   
            

def AdapterProperty(internal_member_name = None, **kwargs):
    return RestrictedProperty(internal_member_name=None, **kwargs)

