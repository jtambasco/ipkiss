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

from ipkiss.technology import get_technology
from ipkiss.technology.technology import TechnologyTree, DelayedInitTechnologyTree
from ipkiss.log import IPKISS_LOG as LOG
TECH = get_technology()

####################################################################
# DEFAULT FIBER COUPLER
####################################################################

TECH.IO = TechnologyTree()

class TechFibcoupTree(DelayedInitTechnologyTree):
    
    def initialize(self):
        
        ## standard gratings 1550nm
        def STANDARD_GRATING_1550_TE():
            from picazzo.fibcoup.uniform import UniformLineGrating as _ULG
            from ipkiss.plugins.photonics.wg.basic import WgElDefinition
            std1550_grating_trench = 0.315
            std1550_grating_period = 0.630
            std1550_grating_n_o_periods = 25
            std_lin_grating_wg_def = WgElDefinition(wg_width = 10.0)
            G = _ULG(name = "std_grating_1550",
                     origin = (0.0,0.0),
                     period = std1550_grating_period, 
                     line_width = std1550_grating_trench, 
                     n_o_periods = std1550_grating_n_o_periods, 
                     wg_definition = std_lin_grating_wg_def,
                     process = TECH.PROCESS.FC )    
            return G

        ## standard gratings 1550nm TM polarization
        def STANDARD_GRATING_1550_TM():
            from picazzo.fibcoup.uniform import UniformLineGrating as _ULG
            from ipkiss.plugins.photonics.wg.basic import WgElDefinition
            std1550_grating_trench = 0.540
            std1550_grating_period = 1.080
            std1550_grating_n_o_periods = 16
            std_lin_grating_wg_def = WgElDefinition(wg_width = 10.0)
            G = _ULG(name = "std_grating_1550_tm",
                     origin = (0.0,0.0),
                     period = std1550_grating_period, 
                     line_width = std1550_grating_trench, 
                     n_o_periods = std1550_grating_n_o_periods, 
                     wg_definition = std_lin_grating_wg_def,
                     process = TECH.PROCESS.FC )    
            return G

        def STANDARD_2DGRATING_1550_TE():
            from picazzo.fibcoup.uniform_2d import SymmetricUniformRect2dGrating as _UG2D
            from ipkiss.plugins.photonics.wg.basic import WgElDefinition
            std1550_2dgrating_period = 0.605   
            std1550_2dgrating_hole_diameter = 0.390    # desired after litho: 370
            std1550_2dgrating_n_o_periods = 19      
            std1550_2dgrating_wg_def = WgElDefinition(wg_width = 12.0)
            std1550_2dgrating_wg_length = 11 # length of trench before the taper starts
            std1550_2dgrating_trench_overlap = 4 # length of overlap between taper and fiber coupler trench
            std1550_2dgrating_dev_angle = 3.1           # angle deviation w/respect to 90 degrees.
            G = _UG2D(name = "std_2dgrating_1550",
                      period = std1550_2dgrating_period, 
                      hole_diameter = std1550_2dgrating_hole_diameter, 
                      n_o_periods = std1550_2dgrating_n_o_periods,
                      wg_definition = std1550_2dgrating_wg_def,
                      wg_length = std1550_2dgrating_wg_length,
                      dev_angle = std1550_2dgrating_dev_angle,
                      process = TECH.PROCESS.WG)
            return G
        
        self.DEFAULT_GRATING_TE = STANDARD_GRATING_1550_TE()
        self.DEFAULT_GRATING_TM = STANDARD_GRATING_1550_TM()
        self.DEFAULT_GRATING = self.DEFAULT_GRATING_TE
        
        try:
            self.DEFAULT_2D_GRATING = STANDARD_2DGRATING_1550_TE()
        except Exception, exc:
            LOG.warn("TECH.IO.FIBCOUP.DEFAULT_2D_GRATING will not be set : "+str(exc))
        
TECH.IO.FIBCOUP = TechFibcoupTree()

class TechAdapterTree(DelayedInitTechnologyTree):
    def initialize(self):
        from picazzo.io.fibcoup import IoFibcoup
        self.DEFAULT_ADAPTER = IoFibcoup

TECH.IO.ADAPTER = TechAdapterTree()
