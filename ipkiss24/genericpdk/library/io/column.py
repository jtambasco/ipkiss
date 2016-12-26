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
from picazzo.io.column import IoColumn, IoColumnGroup
import constants

class StdIoColumnGroup(IoColumnGroup):
    y_spacing = PositiveNumberProperty(default = constants.STD_IOCOLUMN_Y_SPACING)    
    column_number = IntProperty(default = 0)

class StdIoColumn(IoColumn):
    y_spacing = PositiveNumberProperty(default = constants.STD_IOCOLUMN_Y_SPACING)    

class Std1mmColumn(StdIoColumnGroup):
    def define_south_east(self):
        return Coord2(1000.0-constants.STD_IOCOLUMN_MARGIN,0.0)

class Std3mmColumn(StdIoColumnGroup):
    def define_south_east(self):
        return (constants.STD3MM_Column_Bottom_Right(self.column_number)[0] - constants.STD3MM_Column_Bottom_Left(self.column_number)[0],
                constants.STD3MM_Column_Bottom_Right(self.column_number)[1] - constants.STD3MM_Column_Bottom_Left(self.column_number)[1])
    
    def define_n_o_lines(self):
        return (constants.STD3MM_Column_N_Lines, constants.STD3MM_Column_N_Lines)

    
class Std4mmColumn(StdIoColumnGroup):
        
    def define_south_east(self):
        return (constants.STD4MM_Column_Bottom_Right(self.column_number)[0] - constants.STD4MM_Column_Bottom_Left(self.column_number)[0],
                constants.STD4MM_Column_Bottom_Right(self.column_number)[1] - constants.STD4MM_Column_Bottom_Left(self.column_number)[1])
   
    def define_n_o_lines(self):
        return (constants.STD4MM_Column_N_Lines, constants.STD4MM_Column_N_Lines)
        

class Std6mmColumn(StdIoColumnGroup):
    def define_south_east(self):
        return (constants.STD6MM_Column_Bottom_Right(self.column_number)[0] - constants.STD6MM_Column_Bottom_Left(self.column_number)[0],
                constants.STD6MM_Column_Bottom_Right(self.column_number)[1] - constants.STD6MM_Column_Bottom_Left(self.column_number)[1])
    
    def define_n_o_lines(self):    
        return (constants.STD6MM_Column_N_Lines, constants.STD6MM_Column_N_Lines)            

class Std12mmColumn(StdIoColumnGroup):
    def define_south_east(self):
        return (constants.STD12MM_Column_Bottom_Right(self.column_number)[0] - constants.STD12MM_Column_Bottom_Left(self.column_number)[0],
                 constants.STD12MM_Column_Bottom_Right(self.column_number)[1] - constants.STD12MM_Column_Bottom_Left(self.column_number)[1])
        
    def define_n_o_lines(self):
        return (constants.STD12MM_Column_N_Lines, constants.STD12MM_Column_N_Lines)
                      
                
        

    

    
            