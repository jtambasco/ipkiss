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
from .block_structure import IoCompoundBlockStructure, IoCompoundBlockGroup, IoTitleBlock
from .block_structure.layout import __IoCompoundBlockGroup__
from .adapter import AdapterProperty
from ipkiss.plugins.photonics.port.port import OpticalPort
from ipkiss.all import *

__all__ = ["IoColumn", "IoColumnGroup"]

#######################################################
# Column of Waveguide Structures
#######################################################

class __IoColumn__(__IoCompoundBlockGroup__):
    adapter = AdapterProperty(default = TECH.IO.ADAPTER.DEFAULT_ADAPTER)

    def get_n_o_lines(self):
        return (self.__n_o_lines_west__, self.__n_o_lines_east__)
    
    def set_n_o_lines(self, value):
        if isinstance(value, int):
            self.__n_o_lines_west__ = value
            self.__n_o_lines_east__ = value
        elif isinstance(value, tuple):
            self.__n_o_lines_west__ = value[0]
            self.__n_o_lines_east__ = value[1]
        else:
            raise TypeError("Wrong type " + str(type(value)) + " for IoColumn.n_o_lines.")
    n_o_lines = FunctionProperty(get_n_o_lines, set_n_o_lines)
        

    def add(self, struct, offset = (0.0, 0.0), adapter = None, transformation = None, **adapter_kwargs):
        # Calculate structure position
        if adapter is None:
            adapter = self.adapter
        if transformation is None:
            transformation = IdentityTransform()

        c = self.count_offset
        br = (self.width, self.y_spacing * self.count_offset)
        block = adapter(struct = struct,
                        offset = offset,
                        y_spacing = self.y_spacing,
                        south_west = (0.0, 0.0),
                        south_east = br,
                        struct_transformation = transformation,
                        **adapter_kwargs
                        )
        # add it to the list
        self.add_block(block)
        return block

    def __iadd__(self, something):
        if isinstance(something, Structure):
            if isinstance(something, IoBlock):
                self.add_block(something)
            else:
                self.add(something)
            return self
        else:
            return __IoCompoundBlockGroup__.__iadd__(self, something)
    

    def add_blocktitle (self, text, center_clearout = (0.0, 0.0), edge_clearout = (0.0, 0.0)):
        self.add_block(IoTitleBlock(text = text, 
                                      y_spacing = self.y_spacing, 
                                      south_west = (0.0, 0.0),
                                      south_east = (self.width, self.count_offset * self.y_spacing), 
                                      center_clearout = center_clearout, 
                                      edge_clearout = edge_clearout))
   
    def add_align(self, west_east_offset = 0.0, wg_definition = TECH.WGDEF.WIRE, adapter = None):
        struct = Structure(name = "Empty_align_WG", 
                           elements = [], 
                           ports = [OpticalPort(position = (0.0, 0.0), angle = 0.0, wg_definition = wg_definition), 
                                    OpticalPort(position = (0.0, 0.0), angle = 180.0, wg_definition = wg_definition)]
                                )
        self.add(struct, offset = (west_east_offset, 0.0), adapter = adapter)
  

    def is_full(self):
        return (self.count_west >= self.n_o_lines[0]) or (self.count_east>= self.n_o_lines[1])

    def get_block_and_pos_by_name(self,name):
        for i in range(len(self.blocks)):
            B = self.blocks[i]
            p = self.blocks_pos[i]
            if hasattr(B,'name') and B.name == name:
                return [B,p]
        return None
    

class IoColumn (IoCompoundBlockStructure, __IoColumn__):
    
    def define_ports(self, ports):
        for i in range(len(self.blocks)):
            B = self.blocks[i]
            pos = self.blocks_pos[i]
            if hasattr(B,'vertical_optical_ports'):
                for p in B.vertical_optical_ports:
                    ports += p.move_copy(pos)
        return ports
    
class IoColumnGroup (IoCompoundBlockGroup, __IoColumn__):
    pass

