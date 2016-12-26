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


from ..column import IoColumn
from ipkiss.all import *

__all__ = ["ColumnSet"]

class ColumnSet(Structure):
    columns = RestrictedProperty(restriction = RestrictTypeList(IoColumn), required = True)

    def define_elements(self, elems):
        for c in self.columns:
            elems += SRef(c, (0.0, 0.0))
        return elems

    def n_wests(self):
        return [c.count_west for c in self.columns]
    
    def n_easts(self):
        return [c.count_east for c in self.columns]

    def south_wests(self):
        return [c.south_west for c in self.columns]

    def south_easts(self):
        return [c.south_east for c in self.columns]

