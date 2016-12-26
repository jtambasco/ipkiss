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

from ipkiss.technology.technology import TechnologyLibrary, TechnologyTree, DelayedInitTechnologyTree
from ipkiss.technology import get_technology
from ipkiss.io.gds_layer import GdsiiLayerInputMap,GdsiiLayerOutputMap
from ipkiss.process.layer import PPLayer as PPLayer

TECH = get_technology()

####################################################################
# DEFINED PPLayers
####################################################################

TECH.overwrite_allowed.append('PPLAYER')        
TECH.PPLAYER = TechnologyTree()

TECH.PPLAYER.WG = TechnologyTree()
TECH.PPLAYER.FC = TechnologyTree()
TECH.PPLAYER.FCW = TechnologyTree()
TECH.PPLAYER.RFC = TechnologyTree()

### WG ###
TECH.PPLAYER.WG.TRENCH = PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.DF.TRENCH,name="WG_TRE")
TECH.PPLAYER.WG.SQUARE = PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.DF.TRENCH,name="WG_SQ")
TECH.PPLAYER.WG.HOLE = PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.DF.HOLE,name="WG_HEX")
TECH.PPLAYER.WG.MARKER = PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.DF.MARKER,name="WG_MRK")
TECH.PPLAYER.WG.TEXT = PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.DF.TEXT,name="WG_TXT")
TECH.PPLAYER.WG.LINE = PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.LF.LINE,name="WG_LIN")
TECH.PPLAYER.WG.LF_AREA = PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.LF_AREA,name="WG_LFAREA")

# generated layers, not to be used to draw on
TECH.PPLAYER.WG.CRITICAL = TECH.PPLAYER.WG.TRENCH | TECH.PPLAYER.WG.SQUARE | TECH.PPLAYER.WG.HOLE | TECH.PPLAYER.WG.MARKER | (TECH.PPLAYER.WG.LINE ^ TECH.PPLAYER.WG.LF_AREA) & TECH.PPLAYER.WG.LF_AREA
TECH.PPLAYER.WG.NONCRITICAL = TECH.PPLAYER.WG.TEXT | TECH.PPLAYER.WG.MARKER
TECH.PPLAYER.WG.SPACE = TECH.PPLAYER.WG.TRENCH | (TECH.PPLAYER.WG.LINE ^ TECH.PPLAYER.WG.LF_AREA) & TECH.PPLAYER.WG.LF_AREA
TECH.PPLAYER.WG.CRITICAL.name = 'WG_CRIT'
TECH.PPLAYER.WG.NONCRITICAL.name = 'WG_NONCRIT'
TECH.PPLAYER.WG.SPACE.name = 'WG_SPACE'
TECH.PPLAYER.WG.ALL = TECH.PPLAYER.WG.CRITICAL | TECH.PPLAYER.WG.NONCRITICAL

### FC ###
TECH.PPLAYER.FC.TRENCH = PPLayer(TECH.PROCESS.FC,TECH.PURPOSE.DF.TRENCH,name="FC_TRE")
TECH.PPLAYER.FC.SQUARE = PPLayer(TECH.PROCESS.FC,TECH.PURPOSE.DF.TRENCH,name="FC_SQ")
TECH.PPLAYER.FC.HOLE = PPLayer(TECH.PROCESS.FC,TECH.PURPOSE.DF.HOLE,name="FC_HEX")
TECH.PPLAYER.FC.MARKER = PPLayer(TECH.PROCESS.FC,TECH.PURPOSE.DF.MARKER,name="FC_MRK")
TECH.PPLAYER.FC.TEXT = PPLayer(TECH.PROCESS.FC,TECH.PURPOSE.DF.TEXT,name="FC_TXT")
TECH.PPLAYER.FC.LINE = PPLayer(TECH.PROCESS.FC,TECH.PURPOSE.LF.LINE,name="FC_LIN")
TECH.PPLAYER.FC.LF_AREA = PPLayer(TECH.PROCESS.FC,TECH.PURPOSE.LF_AREA,name="FC_LFAREA")

# generated layers, not to be used to draw on
TECH.PPLAYER.FC.CRITICAL = TECH.PPLAYER.FC.TRENCH | TECH.PPLAYER.FC.SQUARE | TECH.PPLAYER.FC.HOLE | (TECH.PPLAYER.FC.LINE ^ TECH.PPLAYER.FC.LF_AREA) & TECH.PPLAYER.FC.LF_AREA
TECH.PPLAYER.FC.NONCRITICAL = TECH.PPLAYER.FC.TEXT | TECH.PPLAYER.FC.MARKER
TECH.PPLAYER.FC.SPACE = TECH.PPLAYER.FC.TRENCH | (TECH.PPLAYER.FC.LINE ^ TECH.PPLAYER.FC.LF_AREA) & TECH.PPLAYER.FC.LF_AREA
TECH.PPLAYER.FC.CRITICAL.name = 'FC_CRIT'
TECH.PPLAYER.FC.NONCRITICAL.name = 'FC_NONCRIT'
TECH.PPLAYER.FC.SPACE.name = 'FC_SPACE'
TECH.PPLAYER.FC.ALL = TECH.PPLAYER.FC.CRITICAL | TECH.PPLAYER.FC.NONCRITICAL

### RFC ###
TECH.PPLAYER.RFC.TRENCH = PPLayer(TECH.PROCESS.RFC,TECH.PURPOSE.DF.TRENCH,name="RFC_TRE")
TECH.PPLAYER.RFC.SQUARE = PPLayer(TECH.PROCESS.RFC,TECH.PURPOSE.DF.SQUARE,name="RFC_SQ")
TECH.PPLAYER.RFC.HOLE = PPLayer(TECH.PROCESS.RFC,TECH.PURPOSE.DF.HOLE,name="RFC_HEX")
TECH.PPLAYER.RFC.MARKER = PPLayer(TECH.PROCESS.RFC,TECH.PURPOSE.DF.MARKER,name="RFC_MRK")
TECH.PPLAYER.RFC.TEXT = PPLayer(TECH.PROCESS.RFC,TECH.PURPOSE.DF.TEXT,name="RFC_TXT")
TECH.PPLAYER.RFC.LINE = PPLayer(TECH.PROCESS.RFC,TECH.PURPOSE.LF.LINE,name="RFC_LIN")
TECH.PPLAYER.RFC.LF_AREA = PPLayer(TECH.PROCESS.RFC,TECH.PURPOSE.LF_AREA,name="RFC_LFAREA")

# generated layers, not to be used to draw on
TECH.PPLAYER.RFC.CRITICAL = TECH.PPLAYER.RFC.TRENCH | TECH.PPLAYER.RFC.SQUARE | TECH.PPLAYER.RFC.HOLE | (TECH.PPLAYER.RFC.LINE ^ TECH.PPLAYER.RFC.LF_AREA) & TECH.PPLAYER.RFC.LF_AREA
TECH.PPLAYER.RFC.NONCRITICAL = TECH.PPLAYER.RFC.TEXT | TECH.PPLAYER.RFC.MARKER
TECH.PPLAYER.RFC.SPACE = TECH.PPLAYER.RFC.TRENCH | (TECH.PPLAYER.RFC.LINE ^ TECH.PPLAYER.RFC.LF_AREA) & TECH.PPLAYER.RFC.LF_AREA
TECH.PPLAYER.RFC.CRITICAL.name = 'RFC_CRIT'
TECH.PPLAYER.RFC.NONCRITICAL.name = 'RFC_NONCRIT'
TECH.PPLAYER.RFC.SPACE.name = 'RFC_SPACE'
TECH.PPLAYER.RFC.ALL = TECH.PPLAYER.RFC.CRITICAL | TECH.PPLAYER.RFC.NONCRITICAL        \

 ### FCW ###
TECH.PPLAYER.FCW.TRENCH = PPLayer(TECH.PROCESS.FCW,TECH.PURPOSE.DF.TRENCH,name="FCW_TRE")
TECH.PPLAYER.FCW.MARKER = PPLayer(TECH.PROCESS.FCW,TECH.PURPOSE.LF.MARKER,name="FCW_MRK")
TECH.PPLAYER.FCW.TEXT = PPLayer(TECH.PROCESS.FCW,TECH.PURPOSE.LF.TEXT,name="FCW_TXT")
TECH.PPLAYER.FCW.LINE = PPLayer(TECH.PROCESS.FCW,TECH.PURPOSE.LF.LINE,name="FCW_LIN")
TECH.PPLAYER.FCW.DF_AREA = PPLayer(TECH.PROCESS.FCW,TECH.PURPOSE.DF_AREA,name="FCW_DFAREA")

# generated layers, not to be used to draw on
TECH.PPLAYER.FCW.CRITICAL = TECH.PPLAYER.FCW.LINE | (TECH.PPLAYER.FCW.TRENCH ^ TECH.PPLAYER.FCW.DF_AREA) & TECH.PPLAYER.FCW.DF_AREA
TECH.PPLAYER.FCW.NONCRITICAL = TECH.PPLAYER.FCW.TEXT | TECH.PPLAYER.FCW.MARKER
TECH.PPLAYER.FCW.CRITICAL.name = 'FCW_CRIT'
TECH.PPLAYER.FCW.NONCRITICAL.name = 'FCW_NONCRIT'
TECH.PPLAYER.FCW.ALL = TECH.PPLAYER.FCW.CRITICAL | TECH.PPLAYER.FCW.NONCRITICAL   


####################################################################
# EXPORT MAPS
####################################################################
TECH.GDSII.overwrite_allowed.append('PROCESS_LAYER_MAP')
TECH.GDSII.PROCESS_LAYER_MAP =   {
        TECH.PROCESS.RFC: 1,
        TECH.PROCESS.FCW: 2,
        TECH.PROCESS.FC: 3,
        TECH.PROCESS.WG: 4,
        TECH.PROCESS.NT : 5,
        TECH.PROCESS.EBW : 6,
        TECH.PROCESS.HFW : 7,
        TECH.PROCESS.VGW : 8,
        TECH.PROCESS.CO : 9,
        TECH.PROCESS.P1 : 20,
        TECH.PROCESS.PPLUS : 21,
        TECH.PROCESS.N1 : 23,
        TECH.PROCESS.NPLUS : 24,
        TECH.PROCESS.SAL : 29,
        TECH.PROCESS.MC1 : 31,
        TECH.PROCESS.MC2 : 32,
        TECH.PROCESS.MH : 35,
        TECH.PROCESS.M1 : 41,
        TECH.PROCESS.V12 : 42,
        TECH.PROCESS.M2 : 43,
        TECH.PROCESS.MP1 : 33,
        TECH.PROCESS.MP2: 34,
        TECH.PROCESS.FC2 : 13,
        TECH.PROCESS.WG2 : 14,
        TECH.PROCESS.VO1 : 15,
        TECH.PROCESS.CA : 60,
        TECH.PROCESS.GW1 : 61,
        TECH.PROCESS.GW2 : 62,
        TECH.PROCESS.GW3 : 63,
        TECH.PROCESS.XW : 10,
        TECH.PROCESS.IPCO : 18,
        TECH.PROCESS.PCON: 64,
        TECH.PROCESS.SLOT: 65,
        TECH.PROCESS.GEW: 66,
        TECH.PROCESS.GN1: 67,
        TECH.PROCESS.GP1: 68,
        TECH.PROCESS.GCONT: 69,
        TECH.PROCESS.GER: 70,
        TECH.PROCESS.NIT: 71,
        TECH.PROCESS.NONE: 100,
    }

TECH.GDSII.overwrite_allowed.append('PROCESS_DATATYPE_MAP')
TECH.GDSII.PURPOSE_DATATYPE_MAP = { 
      TECH.PURPOSE.LF.MARKER: 1,
      TECH.PURPOSE.LF.LINE: 2,
      TECH.PURPOSE.LF.ISLAND: 3,
      TECH.PURPOSE.LF.TEXT: 4,
      TECH.PURPOSE.LF.DUMMY: 5,
      TECH.PURPOSE.LF_AREA: 9, 
      TECH.PURPOSE.DF_AREA: 10, 
      TECH.PURPOSE.DF.MARKER : 11,
      TECH.PURPOSE.DF.HOLE: 12, 
      TECH.PURPOSE.DF.TRENCH: 13,
      TECH.PURPOSE.DF.SQUARE: 14,
      TECH.PURPOSE.DF.TEXT : 15,
      TECH.PURPOSE.DF.DUMMY: 16,
      TECH.PURPOSE.NO_GEN: 20,
      TECH.PURPOSE.NO_FILL: 21,
      TECH.PURPOSE.DOC: 22,
      TECH.PURPOSE.BBOX: 25,
      TECH.PURPOSE.ERROR.SPACE: 40,
      TECH.PURPOSE.ERROR.WIDTH: 41,
      TECH.PURPOSE.ERROR.ANGLE: 42,
      TECH.PURPOSE.ERROR.MINEXT: 43,
      TECH.PURPOSE.ERROR.MAXEXT: 44,
      TECH.PURPOSE.ERROR.MINENC: 45,
      TECH.PURPOSE.ERROR.OVERLAP: 46,
      }

      
####################################################################
# LAYER MAPS
####################################################################

from ipkiss.process.layer_map import UnconstrainedGdsiiPPLayerInputMap, UnconstrainedGdsiiPPLayerOutputMap

TECH.GDSII.overwrite_allowed.append('EXPORT_LAYER_MAP')        
TECH.GDSII.overwrite_allowed.append('IMPORT_LAYER_MAP')        
TECH.GDSII.EXPORT_LAYER_MAP = UnconstrainedGdsiiPPLayerOutputMap(process_layer_map = TECH.GDSII.PROCESS_LAYER_MAP, purpose_datatype_map = TECH.GDSII.PURPOSE_DATATYPE_MAP)
TECH.GDSII.IMPORT_LAYER_MAP = UnconstrainedGdsiiPPLayerInputMap(process_layer_map = TECH.GDSII.PROCESS_LAYER_MAP, purpose_datatype_map = TECH.GDSII.PURPOSE_DATATYPE_MAP)

TECH.OPENACCESS.EXPORT_LAYER_MAP = UnconstrainedGdsiiPPLayerOutputMap(process_layer_map = TECH.GDSII.PROCESS_LAYER_MAP, purpose_datatype_map = TECH.GDSII.PURPOSE_DATATYPE_MAP)
TECH.OPENACCESS.IMPORT_LAYER_MAP = UnconstrainedGdsiiPPLayerInputMap(process_layer_map = TECH.GDSII.PROCESS_LAYER_MAP, purpose_datatype_map = TECH.GDSII.PURPOSE_DATATYPE_MAP)

####################################################################
# GDSII EXPORT FLAGS
####################################################################

TECH.GDSII.FILTER["cut_path"] = True
TECH.GDSII.FILTER["path_to_boundary"] = True
TECH.GDSII.FILTER["cut_boundary"] = True
TECH.GDSII.FILTER["write_empty"] = True

#TECH.GDSII.PATHS_TO_BOUNDARIES_FILTER = True
#TECH.GDSII.CUT_PATHS_FILTER = True
#TECH.GDSII.CUT_BOUNDARIES_FILTER = True
#TECH.GDSII.WRITE_EMPTY = False
TECH.GDSII.FLATTEN_STRUCTURE_CONTAINER = False

####################################################################
# METAL
####################################################################
from ipkiss.geometry.coord import Coord2

TECH.METAL.LINE_WIDTH = 10.0
TECH.METAL.PAD_SIZE = Coord2(100.0, 100.0)

####################################################################
# WAVEGUIDES
####################################################################
TECH.WG.WIRE_WIDTH = 0.45
TECH.WG.TRENCH_WIDTH = 2.0
TECH.WG.BEND_RADIUS = 5.0
TECH.WG.SPACING = 2.0
TECH.WG.DC_SPACING = TECH.WG.WIRE_WIDTH + 0.18
TECH.WG.SHORT_STRAIGHT = 2.0
TECH.WG.SHORT_TAPER_LENGTH = 5.0
TECH.WG.OVERLAP_EXTENSION = 0.020
TECH.WG.OVERLAP_TRENCH = 0.010
TECH.WG.EXPANDED_WIDTH = 0.8
TECH.WG.EXPANDED_TAPER_LENGTH = 3.0
TECH.WG.EXPANDED_STRAIGHT = 5.0
TECH.WG.ANGLE_STEP = 1.0
TECH.WG.SLOT_WIDTH = 0.15
TECH.WG.SLOTTED_WIRE_WIDTH = 0.7

TECH.FC.WIRE_WIDTH = 0.45
TECH.FC.TRENCH_WIDTH = 4.0


####################################################################
# MATERIALS
####################################################################

from pysics.materials.electromagnetics import *
from pysics.basics.material.material import Material, MaterialFactory
from ipkiss.visualisation.display_style import DisplayStyle
from ipkiss.visualisation.color import *

TECH.overwrite_allowed.append('MATERIALS')
TECH.MATERIALS = MaterialFactory()

TECH.MATERIALS.AIR = Material(name = "air",display_style = DisplayStyle(color = COLOR_GREEN), solid = False)
TECH.MATERIALS.SILICON = Material(name = "silicon",display_style = DisplayStyle(color = COLOR_CYAN))
TECH.MATERIALS.SILICON_OXIDE = Material(name = "silicon oxide", display_style = DisplayStyle(color = COLOR_BLUE))
TECH.MATERIALS.GERMANIUM = Material(name = "germanium", display_style = DisplayStyle(color = COLOR_DARK_GREEN))

from pysics.basics.material.material_stack import MaterialStack, MaterialStackFactory

TECH.overwrite_allowed.append('MATERIAL_STACKS')
TECH.MATERIAL_STACKS = MaterialStackFactory()

MSTACK_SOI_SILICON_OXIDE_HEIGHT = 0.500

TECH.MATERIAL_STACKS.MSTACK_SOI_AIR = MaterialStack(name = "Air", 
                                                    materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                        (TECH.MATERIALS.AIR,0.380)], 
                                                    display_style = DisplayStyle(color = COLOR_BLUE))

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_80nm = MaterialStack(name = "80nm Si", 
                                                        materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                            (TECH.MATERIALS.SILICON,0.080),
                                                                            (TECH.MATERIALS.AIR,0.300)], 
                                                        display_style = DisplayStyle(color = COLOR_GREEN))

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_150nm = MaterialStack(name = "150nm Si", 
                                                        materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                            (TECH.MATERIALS.SILICON,0.150),
                                                                            (TECH.MATERIALS.AIR,0.230)], 
                                                        display_style = DisplayStyle(color = COLOR_YELLOW))

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_220nm = MaterialStack(name = "220nm Si", 
                                                        materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                            (TECH.MATERIALS.SILICON,0.220),
                                                                            (TECH.MATERIALS.AIR,0.160)], 
                                                        display_style = DisplayStyle(color = COLOR_RED))

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm = MaterialStack(name = "380nm Si", 
                                                        materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                            (TECH.MATERIALS.SILICON,0.380)], 
                                                        display_style = DisplayStyle(color = COLOR_WHITE))   

TECH.MATERIALS.SILICON.epsilon = 12

TECH.MATERIALS.SILICON_OXIDE.epsilon = 2.3104

TECH.MATERIALS.AIR.epsilon = 1

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_80nm.effective_index_epsilon = 1.936**2 

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_150nm.effective_index_epsilon = 2.539**2

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_220nm.effective_index_epsilon =  2.844**2

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm.effective_index_epsilon = 3.158**2 

TECH.MATERIAL_STACKS.MSTACK_SOI_AIR.effective_index_epsilon = 1.0

####################################################################
# VIRTUAL FABRICATION
####################################################################
from ipkiss.plugins.vfabrication.process_flow import VFabricationProcessFlow

TECH.overwrite_allowed.append('VFABRICATION')
TECH.VFABRICATION = TechnologyTree()

TECH.VFABRICATION.PROCESS_FLOW = VFabricationProcessFlow(active_processes = [ TECH.PROCESS.RFC, TECH.PROCESS.FCW,
                                                                 TECH.PROCESS.FC, TECH.PROCESS.WG,
                                                                 TECH.PROCESS.SLOT], # DO NOT CHANGE THE SEQUENCE OF THE ELEMENTS ! IT MUST MATCH THE SEQUENCE OF THE COLUMNS IN VFABRICATION PROPERTY process_to_material_stack_map
        process_to_material_stack_map = #RFC, FCW, FC, WG, SLOT (SLOT process is equivalent to WG.... )
                        #SLOT=0
                        [((0, 0, 0, 0, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm ),
                        ((0, 0, 0, 1, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm ), 
                        ((0, 0, 1, 0, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm ), # Only a problem if the hardmask gets etched through
                        ((0, 0, 1, 1, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm ), # Only a problem if the hardmask gets etched through
                        ((0, 1, 0, 0, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_220nm ),
                        ((0, 1, 0, 1, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR ),
                        ((0, 1, 1, 0, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_150nm ),
                        ((0, 1, 1, 1, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR ),
                        ((1, 0, 0, 0, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_150nm ), 
                        ((1, 0, 0, 1, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 0, 1, 0, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_80nm ),
                        ((1, 0, 1, 1, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 1, 0, 0, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 1, 0, 1, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 1, 1, 0, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 1, 1, 1, 0), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        #SLOT=1
                        ((0, 0, 0, 0, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm ),
                        ((0, 0, 0, 1, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm ), 
                        ((0, 0, 1, 0, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm ), # Only a problem if the hardmask gets etched through
                        ((0, 0, 1, 1, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm ), # Only a problem if the hardmask gets etched through
                        ((0, 1, 0, 0, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR ),
                        ((0, 1, 0, 1, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR ),
                        ((0, 1, 1, 0, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR ),
                        ((0, 1, 1, 1, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR ),
                        ((1, 0, 0, 0, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR ), 
                        ((1, 0, 0, 1, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 0, 1, 0, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR ),
                        ((1, 0, 1, 1, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 1, 0, 0, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 1, 0, 1, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 1, 1, 0, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),
                        ((1, 1, 1, 1, 1), TECH.MATERIAL_STACKS.MSTACK_SOI_AIR),          
                      ],   
            is_lf_fabrication = {TECH.PROCESS.WG   : False, 
                                 TECH.PROCESS.FC   : False,
                                 TECH.PROCESS.SLOT : False,
                                 TECH.PROCESS.RFC  : False,
                                 TECH.PROCESS.FCW  : True} #etch to 220nm is implicitely present over the whole canvas
            )


TECH.PURPOSE.LF.TEXT.ignore_vfabrication = True   
TECH.PURPOSE.LF.DUMMY.ignore_vfabrication = True   
TECH.PURPOSE.DF.DUMMY.ignore_vfabrication = True   
TECH.PURPOSE.NO_FILL.ignore_vfabrication = True   
TECH.PURPOSE.NO_GEN.ignore_vfabrication = True   
TECH.PURPOSE.NO_PERF.ignore_vfabrication = True   
TECH.PURPOSE.DOC.ignore_vfabrication = True    
TECH.PURPOSE.BBOX.ignore_vfabrication = True   
TECH.PURPOSE.INVISIBLE.ignore_vfabrication = True   
TECH.PURPOSE.ERROR.SPACE.ignore_vfabrication = True   
TECH.PURPOSE.ERROR.WIDTH.ignore_vfabrication = True   
TECH.PURPOSE.ERROR.ANGLE.ignore_vfabrication = True   
TECH.PURPOSE.ERROR.MINEXT.ignore_vfabrication = True   
TECH.PURPOSE.ERROR.MAXEXT.ignore_vfabrication = True   
TECH.PURPOSE.ERROR.MINENC.ignore_vfabrication = True   
TECH.PURPOSE.ERROR.OVERLAP.ignore_vfabrication = True   
    
