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

from ..ipkiss.common import *
from ipkiss.technology.technology import ProcessTechnologyTree, TechnologyTree, DelayedInitTechnologyTree
from ipkiss.technology import get_technology
from ipkiss.geometry.coord import Coord2
from ipkiss.process.layer import ProcessLayer, PatternPurpose

TECH = get_technology()

###############################################################################################
# Process Layers
###############################################################################################        

# silicon structuring
TECH.PROCESS.RFC = ProcessLayer("Raised Fiber Couplers", "RFC")
TECH.PROCESS.FCW = ProcessLayer("Fiber Coupler Windows", "FCW")
TECH.PROCESS.FC = ProcessLayer("Fiber Couplers", "FC")
TECH.PROCESS.WG = ProcessLayer("Waveguides", "WG")
TECH.PROCESS.SLOT = ProcessLayer("Slot waveguides", "SLOT")
TECH.PROCESS.SK = ProcessLayer("Socket waveguides", "SK")

# implants, silicide, contacts
TECH.PROCESS.NBODY = ProcessLayer("Body N doping","NBODY")
TECH.PROCESS.PBODY = ProcessLayer("Body P doping" ,"PBODY")
TECH.PROCESS.N1 = ProcessLayer("N-type doping 1","N1")
TECH.PROCESS.NPLUS = ProcessLayer("N++ doping" ,"N2")
TECH.PROCESS.P1 = ProcessLayer("P-type doping 1","P1")
TECH.PROCESS.PPLUS = ProcessLayer("P++ doping","PPLUS")
TECH.PROCESS.PP1 = ProcessLayer("Poly P-type doping 1","PP1")
TECH.PROCESS.PP2 = ProcessLayer("Poly P-type doping 2","PP2")

TECH.PROCESS.SAL = ProcessLayer("Self-aligned silicide","SAL")
TECH.PROCESS.PCON = ProcessLayer("Photonic Contact holes","PCON")

# backend
TECH.PROCESS.POL = ProcessLayer("Polymer backend", "POL")
TECH.PROCESS.NIT = ProcessLayer("Nitride liner", "NIT")
TECH.PROCESS.UCUT = ProcessLayer("Undercut", "UCUT")
TECH.PROCESS.EXPO = ProcessLayer("Exposure windows", "EXPO")
# metal
TECH.PROCESS.MH = ProcessLayer("Metal Heaters" ,"MH")
TECH.PROCESS.M1 = ProcessLayer("Metallization 1" ,"M1")
TECH.PROCESS.V12 = ProcessLayer("Matel Via 1-2" ,"V12")
TECH.PROCESS.M2 = ProcessLayer("Metallization 2" ,"M2")
TECH.PROCESS.PASS = ProcessLayer("Passivation", "PASS")
TECH.PROCESS.METPASS = ProcessLayer("Passivation", "METPASS")

# Germanium
TECH.PROCESS.GEW = ProcessLayer("Oxide windows for Ge", "GEW")
TECH.PROCESS.GN1 = ProcessLayer("N1 implant in Ge", "GN1")
TECH.PROCESS.GP1 = ProcessLayer("P1 implant in Ge", "GP1")
TECH.PROCESS.GCONT = ProcessLayer("Contact holes to Ge", "GCONT")
TECH.PROCESS.GER = ProcessLayer("Local germanidation", "GER")

# TSV
TECH.PROCESS.TSV = ProcessLayer("Through Silicon Via","TSV")
TECH.PROCESS.UBUMP = ProcessLayer("Microbumps on Top Wafer for 3D integration", "UBUMP")
TECH.PROCESS.BBUMP = ProcessLayer("Microbumps on Bottom Wafer for 3D integration", "BBUMP")
TECH.PROCESS.M2B = ProcessLayer("Metallization 2 Bottom wafer" ,"M2B")

# Clearout
TECH.PROCESS.IPCO = ProcessLayer("IP Clearout windows", "IPCO")

# various test modules 
TECH.PROCESS.NT = ProcessLayer("Nitride Tapers", "NT")
TECH.PROCESS.EBW = ProcessLayer("E-Beam Windows", "EBW")
TECH.PROCESS.HFW = ProcessLayer("HF Substrate removal windows", "HFW")
TECH.PROCESS.VGW = ProcessLayer("V-groove windows", "VGW")
TECH.PROCESS.CO = ProcessLayer("Clear out windows", "CO")
TECH.PROCESS.MC1 = ProcessLayer("Lift-off contact holes 1","MC1")
TECH.PROCESS.MC2 = ProcessLayer("Lift-off contact holes 2","MC2")
TECH.PROCESS.MP1 = ProcessLayer("Metal Plating 1" ,"MP1")
TECH.PROCESS.MP2= ProcessLayer("Metal Plating 2" ,"MP2")
TECH.PROCESS.FC2 = ProcessLayer("Fiber Couplers 2", "FC2")
TECH.PROCESS.WG2 = ProcessLayer("Waveguides 2", "WG2")
TECH.PROCESS.VO1 = ProcessLayer("Optical via 1", "VO1")
TECH.PROCESS.GW1 = ProcessLayer("Generic Windows 1", "GW1")
TECH.PROCESS.GW2 = ProcessLayer("Generic Windows 2", "GW2")
TECH.PROCESS.GW3 = ProcessLayer("Generic Windows 3", "GW3")
TECH.PROCESS.XW = ProcessLayer("Various windows, grouping of GW1, FCW, HFW,...","XW")

# contact masks
TECH.PROCESS.CONT1 = ProcessLayer("Contact mask 1", "CONT1")
TECH.PROCESS.CONT2 = ProcessLayer("Contact mask 2", "CONT2")
TECH.PROCESS.CONT3 = ProcessLayer("Contact mask 3", "CONT3")
TECH.PROCESS.CONT4 = ProcessLayer("Contact mask 4", "CONT4")
TECH.PROCESS.CONT5 = ProcessLayer("Contact mask 5", "CONT5")
TECH.PROCESS.MP1 = ProcessLayer("Metal Plating 1", "MP1")
TECH.PROCESS.MP2 = ProcessLayer("Metal Plating 2", "MP2")

# other
TECH.PROCESS.NONE = ProcessLayer("No Specific Process Layer", "NONE")
TECH.PROCESS.CA = ProcessLayer("Contact Litho Alignment", "CA")

# purposes
TECH.PURPOSE.VERBBOX = PatternPurpose("VERBBOX","VB")
TECH.PURPOSE.VERPORT = PatternPurpose("VERPORT","VP")

####################################################################
# MASK LAYER RULES
####################################################################

# This should become process layer dependent!
TECH.TECH.MINIMUM_LINE = 0.120
TECH.TECH.MINIMUM_SPACE = 0.120

####################################################################
# DISPLAY STYLES
####################################################################
class TechDisplayTree(DelayedInitTechnologyTree):
    def initialize(self):
        from ipkiss.process import PPLayer
        from ipkiss.visualisation.display_style import DisplayStyle, DisplayStyleSet
        from ipkiss.visualisation import color
    
        self.PREDEFINED_STYLE_SETS = TechnologyTree()        
    
        # colorful purpose map
        DISPLAY_BLACK = DisplayStyle(color = color.COLOR_BLACK, edgewidth = 0.0)
        DISPLAY_WHITE = DisplayStyle(color = color.COLOR_WHITE, edgewidth = 0.0)
        DISPLAY_INVERSION = DisplayStyle(color = color.COLOR_BLUE, alpha = 0.5, edgewidth = 1.0)
        DISPLAY_DF = DisplayStyle(color = color.COLOR_GREEN, alpha = 0.5, edgewidth = 1.0)
        DISPLAY_LF = DisplayStyle(color = color.COLOR_YELLOW, alpha = 0.5, edgewidth = 1.0)
        DISPLAY_TEXT = DisplayStyle(color = color.COLOR_MAGENTA, alpha = 0.5, edgewidth = 1.0)
        DISPLAY_HOLE = DisplayStyle(color = color.COLOR_RED, alpha = 0.5, edgewidth = 1.0)
        DISPLAY_ALIGNMENT = DisplayStyle(color = color.COLOR_CYAN, alpha = 0.5, edgewidth = 1.0) 
        style_set = DisplayStyleSet()
        style_set.background = DISPLAY_WHITE
        process_display_order = [ 
                      TECH.PROCESS.RFC,
                      TECH.PROCESS.FCW,
                      TECH.PROCESS.FC,
                      TECH.PROCESS.WG,
                      TECH.PROCESS.NT,
                      TECH.PROCESS.EBW,
                      TECH.PROCESS.HFW,
                      TECH.PROCESS.VGW,
                      TECH.PROCESS.CO,
                      TECH.PROCESS.NBODY,
                      TECH.PROCESS.PBODY,
                      TECH.PROCESS.P1,
                      TECH.PROCESS.PPLUS,
                      TECH.PROCESS.N1,
                      TECH.PROCESS.NPLUS,
                      TECH.PROCESS.PP1,
                      TECH.PROCESS.PP2,
                      TECH.PROCESS.SAL,
                      TECH.PROCESS.MC1,
                      TECH.PROCESS.MC2,
                      TECH.PROCESS.MH,
                      TECH.PROCESS.M1,
                      TECH.PROCESS.V12,
                      TECH.PROCESS.M2,
                      TECH.PROCESS.MP1,
                      TECH.PROCESS.MP2,
                      TECH.PROCESS.FC2,
                      TECH.PROCESS.WG2,
                      TECH.PROCESS.VO1,
                      TECH.PROCESS.GW1,
                      TECH.PROCESS.GW2,
                      TECH.PROCESS.GW3
                  ]
    
        for process in process_display_order:
            style_set += [(PPLayer(process, TECH.PURPOSE.LF_AREA),DISPLAY_INVERSION),
                          (PPLayer(process, TECH.PURPOSE.DF_AREA) , DISPLAY_INVERSION),
                          (PPLayer(process, TECH.PURPOSE.DF.MARKER) , DISPLAY_ALIGNMENT),
                          (PPLayer(process, TECH.PURPOSE.LF.MARKER) , DISPLAY_ALIGNMENT),
                          (PPLayer(process, TECH.PURPOSE.LF.LINE) , DISPLAY_DF),
                          (PPLayer(process, TECH.PURPOSE.LF.ISLAND) , DISPLAY_DF),
                          (PPLayer(process, TECH.PURPOSE.DF.TEXT) , DISPLAY_TEXT),
                          (PPLayer(process, TECH.PURPOSE.DF.HOLE) , DISPLAY_HOLE),
                          (PPLayer(process, TECH.PURPOSE.DF.TRENCH), DISPLAY_LF),
                          (PPLayer(process, TECH.PURPOSE.DF.SQUARE) , DISPLAY_HOLE),
                          ]
        
        self.PREDEFINED_STYLE_SETS.PURPOSE_HIGHLIGHT  = style_set
    
TECH.DISPLAY = TechDisplayTree()


