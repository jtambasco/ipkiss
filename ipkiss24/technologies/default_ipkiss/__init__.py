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

from ipkiss.technology.technology import TechnologyTree, DelayedInitTechnologyTree
from ipkiss.technology import get_technology, TECHNOLOGY as TECH

TECH.name = "IPKISS_DEFAULT"


####################################################################
# NAME GENERATOR
####################################################################
class TechAdminTree(DelayedInitTechnologyTree):
    """A technology tree with a name generator"""
    def initialize(self):
        from ipkiss.primitives import name_generator
        self.NAME_GENERATOR = name_generator.CounterNameGenerator(prefix_attribute = "__name_prefix__",
                                             counter_zero = 0,
                                             default_prefix = "STRUCTURE"
                                             )
        
TECH.ADMIN = TechAdminTree()


####################################################################
# Basic Metrics 
####################################################################

TECH.METRICS = TechnologyTree()
TECH.METRICS.GRID = 5E-9
TECH.METRICS.UNIT = 1E-6
TECH.METRICS.ANGLE_STEP = 1.0
TECH.METRICS.overwrite_allowed = ["UNIT","GRID","ANGLE_STEP"]

####################################################################
# LAYER MAP
####################################################################

class TechGdsiiTree(DelayedInitTechnologyTree):
    """A technology tree with a GDS2 import and export layer map"""
        
    def initialize(self):
        from ipkiss.io.gds_layer import AutoGdsiiLayerOutputMap, AutoGdsiiLayerInputMap
        from ipkiss.io.gds_layer import AutoGdsiiLayerOutputMap
                
        #if not hasattr(self, "EXPORT_LAYER_MAP"):
        if not "EXPORT_LAYER_MAP"  in self.keys():
            self.EXPORT_LAYER_MAP = AutoGdsiiLayerOutputMap()
            self.overwrite_allowed.append('EXPORT_LAYER_MAP')
        if not "IMPORT_LAYER_MAP"  in self.keys():
            self.IMPORT_LAYER_MAP = AutoGdsiiLayerInputMap()
            self.overwrite_allowed.append('IMPORT_LAYER_MAP')

        if not "FILTER" in self.keys():
            from ipkiss.primitives.filters.path_cut_filter import PathCutFilter
            from ipkiss.primitives.filters.empty_filter import EmptyFilter
            from ipkiss.primitives.filters.path_to_boundary_filter import PathToBoundaryFilter
            from ipkiss.primitives.filters.boundary_cut_filter import BoundaryCutFilter
            from ipkiss.primitives.filters.name_scramble_filter import NameScrambleFilter
            from ipkiss.primitives.filters.layer_filter import LayerFilterDelete
            from ipkiss.primitives.filter import ToggledCompoundFilter
            
            f = ToggledCompoundFilter()
            f += PathCutFilter(name = "cut_path", max_path_length = TECH.GDSII.MAX_COORDINATES, grids_per_unit = int(TECH.METRICS.UNIT/TECH.METRICS.GRID), overlap = 1)
            f += PathToBoundaryFilter(name = "path_to_boundary")
            f += BoundaryCutFilter(name = "cut_boundary", max_vertex_count = TECH.GDSII.MAX_VERTEX_COUNT)
            f += EmptyFilter(name = "write_empty")
            f["write_empty"]=False
            self.FILTER = f

            self.overwrite_allowed.append('FILTER')            

            self.NAME_FILTER = NameScrambleFilter(max_name_length = TECH.GDSII.MAX_NAME_LENGTH, scramble_all = False)
            self.overwrite_allowed.append('NAME_FILTER')
            
TECH.GDSII = TechGdsiiTree()
#TECH.GDSII.FILTERS = TechGdsiiFilterTree()
TECH.GDSII.MAX_COORDINATES = 200
TECH.GDSII.MAX_PATH_LENGTH = 100
TECH.GDSII.MAX_VERTEX_COUNT = 4000
TECH.GDSII.MAX_NAME_LENGTH = 255

####################################################################
# GDSII EXPORT FLAGS
####################################################################


#TECH.GDSII.PATHS_TO_BOUNDARIES_FILTER = True
#TECH.GDSII.CUT_PATHS_FILTER = True
#TECH.GDSII.CUT_BOUNDARIES_FILTER = True
#TECH.GDSII.WRITE_EMPTY = False

