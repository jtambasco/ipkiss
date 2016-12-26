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

from ipcore.properties.descriptor import DefinitionProperty
from ipcore.properties.predefined import PositiveNumberProperty
from ipcore.properties.initializer import StrongPropertyInitializer
from ..technology.settings import TECH
from .. import settings


__all__ = []

class UnitGridContainer(StrongPropertyInitializer):
    grids_per_unit = DefinitionProperty(fdef_name = "define_grids_per_unit")
    units_per_grid = DefinitionProperty(fdef_name = "define_units_per_grid")
    unit = PositiveNumberProperty(default = TECH.METRICS.UNIT)
    grid = PositiveNumberProperty(default = TECH.METRICS.GRID)          

    def define_grids_per_unit(self):
        return self.unit/ self.grid

    def define_units_per_grid(self):
        return self.grid/ self.unit

    def validate_properties(self):
        if self.grid > self.unit:
            raise Exception("The grid should be smaller than the unit.")
        return True
