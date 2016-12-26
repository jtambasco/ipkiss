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
from ipkiss.technology.settings import get_technology
import sys

TECH = get_technology()

class StructureOutputAspect(object):

    #mixin for convenient export of a Structure to GDS2
    def write_gdsii(self, filename_or_stream, unit = TECH.METRICS.UNIT, grid = TECH.METRICS.GRID, layer_map = None):
        from ipkiss.primitives import Library
        from ipkiss.io.output_gdsii import FileOutputGdsii, OutputGdsii
        from ipkiss.log import IPKISS_LOG as LOG
        my_lib = Library(name = self.name, unit = unit, grid = grid)
        my_lib += self
        if layer_map is None:
            layer_map = TECH.GDSII.EXPORT_LAYER_MAP #bind only at this moment, because TECH.GDSII.EXPORT_LAYER_MAP could have been assigned a different value since original loading of this module
        if isinstance(filename_or_stream, str):
            OP = FileOutputGdsii(filename_or_stream, layer_map = layer_map)
        elif (filename_or_stream == sys.stdout):
            OP = OutputGdsii(sys.stdout, layer_map = layer_map)
        OP.write(my_lib)
        LOG.debug("Finished writing structure to GDS2.")
        
        
    