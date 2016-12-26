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

from .component_integration import StructureSimulationVolume2D
from pysimul.runtime.camfr_engine.camfr_engine import CamfrEngine
from ipkiss.all import TECH

CAMFR_ENGINE = CamfrEngine() #reference to engine must remain in memory, otherwise camfr segmentation fault (reference to slabs and materials get garbage collected)

def camfr_stack_expr_for_structure(structure, discretisation_resolution, window_size_info = None):
    params = dict()
    params["structure"] = structure
    params["resolution"] = discretisation_resolution #resolution for matrix discretization, used when calculating CAMFR slabs
    if window_size_info is not None:
        params["window_size_info"] = window_size_info
    params["vfabrication_process_flow"] = TECH.VFABRICATION.PROCESS_FLOW
    params["material_stack_factory"] = TECH.MATERIAL_STACKS         
    simulation_volume = StructureSimulationVolume2D(simul_params = params)
    stack_expr = CAMFR_ENGINE.get_camfr_stack_expr_for_geometry(geometry = simulation_volume)
    return stack_expr
