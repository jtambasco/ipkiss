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
from picazzo.fibcoup.uniform import UniformLineGrating as _ULG
from ipkiss.plugins.photonics.wg.basic import WgElDefinition

###############################################################################
## standard gratings 1550nm
###############################################################################
std1550_grating_trench = 0.315
std1550_grating_period = 0.630
std1550_grating_n_o_periods = 25
std_lin_grating_wg_width = 10.0

def STANDARD_GRATING_1550_TE(process = TECH.PROCESS.FC):
    wg_def = WgElDefinition(wg_width = std_lin_grating_wg_width)
    G = _ULG(name = "std_grating_1550",
                           origin = (0.0,0.0),
                           period = std1550_grating_period, 
                           line_width = std1550_grating_trench, 
                           n_o_periods = std1550_grating_n_o_periods, 
                           wg_definition = wg_def,
                           process = process )
    return G


###############################################################################
## standard gratings 1300nm
###############################################################################
std1300_grating_trench = 0.260
std1300_grating_period = 0.520
std1300_grating_n_o_periods = 30
std_lin_grating_wg_width = 10.0

def STANDARD_GRATING_1300_TE(process = TECH.PROCESS.FC):
    wg_def = WgElDefinition(wg_width = std_lin_grating_wg_width)
    return _ULG(name = "std_grating_1300",
                origin = (0.0,0.0),
                period = std1300_grating_period, 
                line_width = std1300_grating_trench, 
                n_o_periods = std1300_grating_n_o_periods, 
                wg_definition = wg_def,
                process = process  )


###############################################################################
## standard gratings 1300nm
###############################################################################
std1550tm_grating_trench = 0.540
std1550tm_grating_period = 1.080
std1550tm_grating_n_o_periods = 18
std_lin_grating_wg_width = 10.0

def STANDARD_GRATING_1550_TM(process = TECH.PROCESS.FC):
    wg_def = WgElDefinition(wg_width = std_lin_grating_wg_width) 
    return _ULG(name = "std_grating_TM_1550",
                origin = (0.0,0.0),
                period = std1550tm_grating_period, 
                line_width = std1550tm_grating_trench, 
                n_o_periods = std1550tm_grating_n_o_periods, 
                wg_definition = wg_def ,
                process = process )

