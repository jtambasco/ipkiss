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

from ..block import IoBlock, IoCompoundBlock
from ipkiss.all import *
from ipkiss.primitives.group import __Group__
from ipkiss.primitives.elements.basic import __Element__

__all__ = ["IoCompoundBlockStructure",
           "IoTitleBlock",
           "IoCompoundBlockGroup"]


class IoBlockStructure(IoBlock, Structure):
    pass

class __IoCompoundBlockGroup__(IoCompoundBlock, __Group__):
    __additional_elements__ = ElementList() # this is not a property, rather a store

        
    def define_elements(self, elems):
        for i in range(len(self.blocks)):
            B = self.blocks[i]
            p = self.blocks_pos[i]
            if isinstance(B, Structure):
                elems += SRef(B, p)
        elems += self.__additional_elements__
        return elems

    def add_abs(self, struct, position, transformation = None):
        if not isinstance(struct, Structure):
            raise TypeError("Invalid type " + str(type(struct)) + " for structure in add_abs()")
        self.__additional_elements__.append(SRef(struct, position, transformation))

    def __iadd__(self, something):
        if isinstance(something, IoBlock):
            return IoCompoundBlock.__iadd__(self, something)
        elif isinstance(something, __Element__):
            self.__additional_elements__.append(something)
            return self
        elif isinstance(something, ElementList):
            self.__additional_elements__.extend(something)
            return self
        else:
            raise TypeError("Cannot add " + str(type(something)) + " to IoCompoundBlockStructure.")
        
class IoCompoundBlockGroup(Group, __IoCompoundBlockGroup__):
    pass
        
class IoCompoundBlockStructure(IoBlockStructure, __IoCompoundBlockGroup__):
    pass
        

class IoTitleBlock(IoBlockStructure):
    process = ProcessProperty(default = TECH.PROCESS.WG)
    text = StringProperty(required = True)
    center_clearout = RestrictedProperty(restriction = RESTRICT_NUMBER_TUPLE2, default = (0.0, 0.0))
    edge_clearout = RestrictedProperty(restriction = RESTRICT_NUMBER_TUPLE2, default = (0.0, 0.0))

    __name_prefix__ = "IOTITLEBLOCK"

    def get_count_west(self):
        return 1

    def get_count_east(self):
        return 1

    def define_elements(self, elems):
        title = Structure(self.name + "_1", PolygonText(PPLayer(self.process, TECH.PURPOSE.DF.TEXT), 
                                                        self.text, 
                                                        (0.0, 0.0), 
                                                        alignment = (TEXT_ALIGN_CENTER, TEXT_ALIGN_MIDDLE) , 
                                                        font = TEXT_FONT_COMPACT, 
                                                        height = 0.7 * self.y_spacing))
        w = title.size_info().width
        N_periods = int(0.5* (0.5* self.width - self.center_clearout[0] - self.edge_clearout[0]) / w)
        if N_periods > 0:
            period = (0.5*self.width - self.center_clearout[0]-self.edge_clearout[0]) / N_periods
            pos = (0.5*period + self.edge_clearout[0], self.south_west[1] * self.y_spacing)
            elems += ARefX(title, pos, period, N_periods)

        N_periods = int( 0.5*(0.5* self.width - self.center_clearout[1] - self.edge_clearout[1]) / w)
        if N_periods > 0:
            period = (0.5*self.width - self.center_clearout[1]-self.edge_clearout[1]) / N_periods
            pos = (0.5 * self.width + 0.5 * period + self.center_clearout[1], self.south_east[1])
            elems += ARefX(title, pos, period, N_periods)
            
        return elems
    
    

