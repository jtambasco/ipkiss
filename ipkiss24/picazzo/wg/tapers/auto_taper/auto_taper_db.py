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
from ..linear import WgElPortTaperLinear


# Class that stores tapering classes between different waveguide definition
class AutoTaperDataBase(StrongPropertyInitializer):
    lookup_table = DefinitionProperty(default = dict())
    indirection_table = DefinitionProperty(default = dict())
    default = DefinitionProperty(default = None)
    default_if_identical = DefinitionProperty(default = WgElPortTaperLinear)
    
    def get_taper_class(self, start_def, end_def):
        t_s = type(start_def)
        t_e = type(end_def)
        
        # add fallback:
        t_s = self.indirection_table.get(t_s, t_s)
        t_e = self.indirection_table.get(t_e, t_e)
        
        if t_s is t_e:
            tc = self.lookup_table.get((t_s, t_e), self.default_if_identical)
        else:
            tc = self.lookup_table.get((t_s, t_e), self.default)

        return tc
        
    def add(self, start_def, end_def, taper_class):
        t_s = start_def
        t_e = end_def
        self.lookup_table[(t_s, t_e)] = taper_class
        

    def treat_wgdef_as(self, my_wg_def, other_wg_def):
        self.indirection_table[my_wg_def] = other_wg_def

        
        





    