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
from ipcore.exceptions.exc import NotImplementedException
from math import ceil, floor
from ipcore.types_list import TypedList

__all__ = []

#######################################################
# Block of spaced waveguides
#######################################################
class IoBlock (StrongPropertyInitializer):
    y_spacing = PositiveNumberProperty(required = True)
    south_west = Coord2Property(default = (0.0, 0.0))
    south_east = Coord2Property(default = (0.0, 0.0))
    count_east = FunctionNameProperty(fget_name = "get_count_east")
    count_west = FunctionNameProperty(fget_name = "get_count_west")
    count_offset = FunctionNameProperty(fget_name = "get_count_offset")    
    

    def define_south_offset(self):
        return int(round((self.south_east[1] - self.south_west[1]) / self.y_spacing))
    south_offset = NumberProperty(locked=True)

    def define_width(self):
        return self.south_east[0] - self.south_west[0]
    width = NonNegativeNumberProperty(locked=True)
      
    def define_count(self):
        return (self.count_west, self.count_east)
    count = NonNegativeNumberProperty(locked=True)
    
    def get_count_offset(self):
        return self.count_east - self.count_west + self.south_offset

    def get_count_west(self):
        raise NotImplementedException("To be implemented by subclass :: get_count_west")

    def get_count_east(self):
        raise NotImplementedException("To be implemented by subclass :: get_count_east")
    
    def size_info(self):
        return SizeInfo(self.south_west[0], 
                             self.south_east[0], 
                             max(self.south_west[1] + self.count_west * self.y_spacing, self.south_east[1], self.south_east[1] + self.count_east * self.y_spacing),
                             min(self.south_west[1] , self.south_east[1])
                             )
    

class IoSpacerBlock(IoBlock):
    n_o_lines = FunctionNameProperty(fget_name = "get_n_o_lines", fset_name="set_n_o_lines")

    def set_n_o_lines(self, value):
        if isinstance(value, int):
            self.__count_west__ = value
            self.__count_east__ = value
        elif isinstance(value, tuple):
            self.__count_west__ = value[0]
            self.__count_east__ = value[1]
        else:
            raise TypeError("Wrong type " + str(type(value)) + " for n_o_lines in IoSpacerBlock.__init__().")
        
    def get_n_o_lines(self):
        return (self.count_west, self.count_east)        
    
    def get_count_west(self):
        return self.__count_west__

    def get_count_east(self):
        return self.__count_east__
    
    
        


##########################################################
# List of blocks
##########################################################
class BlockList(TypedList):
    __item_type__ = IoBlock
    
    def flat_copy(self, level = -1):
        el = BlockList()
        for e in self:
            el += e.flat_copy(level)
        return el

    def is_empty(self):
        if (len(self) == 0): return True
        for e in self:
            if not e.is_empty(): return False
        return True
    
##########################################################
# BlocksDefinitionProperty
##########################################################

class BlocksDefinitionProperty(DefinitionProperty):
    __allowed_keyword_arguments__ = ["required","restriction","default","fdef_name"]
    
    def __init__(self, **kwargs):        
        super(BlocksDefinitionProperty, self).__init__(**kwargs)    
        if ("restriction" in kwargs):
            R = kwargs["restriction"]
            self.restriction = RestrictType(BlockList) & R 
        else:
            self.restriction = RestrictType(BlockList)             
                       
    def __call_getter_function__(self, obj):
        f = self.__get_getter_function__(obj)
        try:
            stored_value = self.__get_property_value_of_object__(obj)
        except KeyError:
            stored_value = BlockList()
        value = f(stored_value)
        DefinitionProperty.__set__(self,obj, value)
        return value        
                


class IoCompoundBlock(IoBlock):
    blocks = BlocksDefinitionProperty(fdef_name = "define_blocks")
    blocks_pos = FunctionNameProperty(fget_name = "get_blocks_pos")   
    

    def get_count_west(self):
        (count_west, count_east, blocks_pos) = self.get_count_east_west_block_pos()
        return count_west

    def get_count_east(self):
        (count_west, count_east, blocks_pos) = self.get_count_east_west_block_pos()
        return count_east
    
    def get_blocks_pos(self):
        (count_west, count_east, blocks_pos) = self.get_count_east_west_block_pos()
        return blocks_pos
    
    def add_block(self, block):
        if not isinstance(block, IoBlock):
            raise TypeError("You can only add an IoBlock to an io_composite_block, not a " + str(type(block)))
        b = self.blocks
        b.append(block)
        self.blocks = b # workaround to set 'dirty' flags
      
    def __iadd__(self, block):
        self.add_block(block)
    
    def get_count_east_west_block_pos(self):
        count_west = 0
        count_east = 0
        blocks_pos = []
        BO = self.south_offset
        for b in self.blocks:
            BO2 = b.south_offset
            CO = count_east - count_west + BO 
            count_west += max(0, CO - BO2)
            count_east += max(0, BO2 - CO) + b.count_east
            blocks_pos.append((self.south_west[0] - b.south_west[0], self.south_west[1] + self.y_spacing * count_west - b.south_west[1]))
            count_west +=  b.count_west 
        return (count_west, count_east, blocks_pos)
                        
    
    # It should be possible to make these more dynamic. If a block below changes, this should be reflected in the
    # the empty blocks. but then it should almost be like the class accesses the compound_block properties
    def add_emptyline(self, N_lines=1):
        self.add_block(IoSpacerBlock(y_spacing = self.y_spacing, 
                                      south_west = (0.0, 0.0),
                                      south_east = (self.width, self.count_offset * self.y_spacing),
                                      n_o_lines = (N_lines, N_lines)))
                                      

    def add_emptyline_west(self, N_lines=1):
        self.add_block(IoSpacerBlock(y_spacing = self.y_spacing, 
                                      south_west = (0.0, 0.0),
                                      south_east = (self.width, self.count_offset * self.y_spacing),
                                      n_o_lines = (N_lines, 0)))

    def add_emptyline_east(self, N_lines=1):
        self.add_block(IoSpacerBlock(y_spacing = self.y_spacing, 
                                      south_west = (0.0, 0.0),
                                      south_east = (self.width, self.count_offset * self.y_spacing),
                                      n_o_lines = (0, N_lines)))

    def straighten(self):
        CO = self.count_offset
        n_o_lines = (max(0, CO), max(0, -CO))
        if not n_o_lines == (0, 0):
            self.add_block(IoSpacerBlock(y_spacing = self.y_spacing, 
                                          south_west = (0.0, 0.0),
                                          south_east = (self.width, CO * self.y_spacing),
                                          n_o_lines = n_o_lines))

    def straighten_to_north(self):
        CO = self.count_offset
        if len(self.blocks) > 0:
            SI = self.blocks[-1].size_info() 
            if SI.height == 0:
                self.straighten()
            else:
                t =  self.blocks_pos[-1][1] + SI.north
                L = max([int(ceil((t - self.south_west[1] + 0.0*self.y_spacing) / self.y_spacing)) - self.count_west, 0, CO])
                R = max([int(ceil((t - self.south_east[1] + 0.0*self.y_spacing ) / self.y_spacing)) - self.count_east, 0, -CO])
                if  L > 0 or R > 0:
                    self.add_block(IoSpacerBlock(y_spacing = self.y_spacing, 
                                                  south_west = (0.0, 0.0),
                                                  south_east = (self.width, CO * self.y_spacing),
                                                  n_o_lines = (L, R)))
        else:
            self.straighten()
            

    def define_blocks(self, blocks):
        return blocks