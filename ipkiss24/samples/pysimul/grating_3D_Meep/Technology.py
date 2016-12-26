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

from intec.technology.imec import *
from ipkiss.visualisation.color import *
from ipkiss.technology.technology import TechnologyLibrary, TechnologyTree
## Copied from imec tech

####################################################################
# MATERIALS
####################################################################

from pysics.electromagnetics import *
from pysics.basics.material.material import Material, MaterialFactory
from ipkiss.visualisation.display_style import DisplayStyle

TECH.overwrite_allowed=["MATERIALS","MATERIAL_STACKS","VFABRICATION","PPLAYER","PROCESS_LAYER_MAP"]
TECH.MATERIALS = MaterialFactory()

TECH.MATERIALS.AIR = Material(name = "air",display_style = DisplayStyle(color = COLOR_GREEN))
TECH.MATERIALS.SILICON = Material(name = "silicon",display_style = DisplayStyle(color = COLOR_CYAN))
TECH.MATERIALS.SILICON_OXIDE = Material(name = "silicon oxide", display_style = DisplayStyle(color = COLOR_BLUE))
TECH.MATERIALS.GERMANIUM = Material(name = "germanium", display_style = DisplayStyle(color = COLOR_DARK_GREEN))



from pysics.basics.material.material_stack import MaterialStack, MaterialStackFactory

TECH.MATERIAL_STACKS = MaterialStackFactory()

MSTACK_SOI_SILICON_OXIDE_HEIGHT = 0.700

TECH.MATERIAL_STACKS.MSTACK_SOI_AIR = MaterialStack(name = "Air", 
                                                    materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                        (TECH.MATERIALS.AIR,0.220)], 
                                                    display_style = DisplayStyle(color = COLOR_BLUE))

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_80nm = MaterialStack(name = "80nm Si", 
                                                        materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                            (TECH.MATERIALS.SILICON,0.080),
                                                                            (TECH.MATERIALS.AIR,0.300-0.160)], 
                                                        display_style = DisplayStyle(color = COLOR_GREEN))

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_150nm = MaterialStack(name = "150nm Si", 
                                                        materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                            (TECH.MATERIALS.SILICON,0.150),
                                                                            (TECH.MATERIALS.AIR,0.07)], 
                                                        display_style = DisplayStyle(color = COLOR_YELLOW))

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_220nm = MaterialStack(name = "220nm Si", 
                                                        materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                            (TECH.MATERIALS.SILICON,0.220)], 
                                                        display_style = DisplayStyle(color = COLOR_RED))

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm = MaterialStack(name = "380nm Si", 
                                                        materials_heights = [(TECH.MATERIALS.SILICON_OXIDE,MSTACK_SOI_SILICON_OXIDE_HEIGHT),
                                                                            (TECH.MATERIALS.SILICON,0.220)], 
                                                        display_style = DisplayStyle(color = COLOR_WHITE))   

TECH.MATERIALS.SILICON.epsilon = 12.08

TECH.MATERIALS.SILICON_OXIDE.epsilon = 1.45**2#2.3104

TECH.MATERIALS.AIR.epsilon = 1.544**2

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_80nm.effective_index_epsilon = 1.936**2 

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_150nm.effective_index_epsilon = 2.539**2

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_220nm.effective_index_epsilon =  2.844**2

TECH.MATERIAL_STACKS.MSTACK_SOI_SI_380nm.effective_index_epsilon = 3.158**2 

TECH.MATERIAL_STACKS.MSTACK_SOI_AIR.effective_index_epsilon = 1.0

####################################################################
# VIRTUAL FABRICATION
####################################################################
from ipkiss.plugins.vfabrication.process_flow import VFabricationProcessFlow

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

TECH.PROCESS.WG.wg_lower_z_coord = MSTACK_SOI_SILICON_OXIDE_HEIGHT
TECH.PROCESS.WG.wg_upper_z_coord = MSTACK_SOI_SILICON_OXIDE_HEIGHT + 0.220

## Overlay Tech

################# STEP 1 : DEFINE THE NEW PROCESSES ###############################
from ipkiss.technology.technology import TechnologyLibrary, TechnologyTree, DelayedInitTechnologyTree
from ipkiss.all import *

TECH.PROCESS.ACL = ProcessLayer("Active Cladding", "ACL")
TECH.PROCESS.ACO = ProcessLayer("Active Core", "ACO")

TECH.PURPOSE.ACTIVE = PatternPurpose("Active material","ACT")

TECH.PPLAYER.ACL = TechnologyTree()
TECH.PPLAYER.ACO = TechnologyTree()

TECH.PPLAYER.ACL.DEFAULT = ProcessPurposeLayer(TECH.PROCESS.ACL,TECH.PURPOSE.ACTIVE,name = "ACL")
TECH.PPLAYER.ACL.ALL = TECH.PPLAYER.ACL.DEFAULT
TECH.PPLAYER.ACL.ALL.NAME = "ACL_ALL"

TECH.PPLAYER.ACO.DEFAULT = ProcessPurposeLayer(TECH.PROCESS.ACO,TECH.PURPOSE.ACTIVE,name = "ACO")
TECH.PPLAYER.ACO.ALL = TECH.PPLAYER.ACO.DEFAULT
TECH.PPLAYER.ACO.ALL.NAME = "ACO_ALL"

TECH.GDSII.EXPORT_LAYER_MAP.process_layer_map[TECH.PROCESS.ACL] = 37
TECH.GDSII.EXPORT_LAYER_MAP.process_layer_map[TECH.PROCESS.ACO] = 43
TECH.GDSII.EXPORT_LAYER_MAP.purpose_datatype_map[TECH.PURPOSE.ACTIVE] = 0
TECH.GDSII.EXPORT_LAYER_MAP.purpose_datatype_map[TECH.PURPOSE.ACTIVE] = 0

################# STEP 2 : DEFINE THE MATERIALS AND MATERIAL STACKS ###############################
from pysics.materials.all import *

#define the materials InP
TECH.MATERIALS.InP = Material(name = "InP", display_style = DisplayStyle(color = COLOR_ORANGE))
TECH.MATERIALS.InGaAsP1p55 = Material(name = "InGaAsP - Q=1.55", display_style = DisplayStyle(color = COLOR_BLUE))
TECH.MATERIALS.InGaAsP1p2 = Material(name = "InGaAsP - Q=1.2", display_style = DisplayStyle(color = COLOR_BLACK))
TECH.MATERIALS.BCB = Material(name = "BCB",display_style = DisplayStyle(color = COLOR_GREEN))

nInP = 3.1649
nBCB = 1.544
nInGaAsP1p55 = 3.515
nInGaAsP1p2 = 3.322

TECH.MATERIALS.InP.epsilon = nInP**2 #9.61

TECH.MATERIALS.InGaAsP1p55.epsilon = nInGaAsP1p55**2
TECH.MATERIALS.InGaAsP1p2.epsilon = nInGaAsP1p2**2


TECH.MATERIALS.BCB.epsilon = nBCB**2 #2.38

LowerCladdingHeight = 0.02
ActiveLayerHeight = 0.08
UpperCladdingHeight = 0.08
CompensationLayer1Height = 0.01
CompensationLayer2Height = 0.01

Number_of_compensation_stacks = 4



MESA_CORE_HEIGHT = LowerCladdingHeight + ActiveLayerHeight + UpperCladdingHeight + Number_of_compensation_stacks * (CompensationLayer1Height + CompensationLayer2Height)

MESA_CORE_HEIGHT = 0.0

BONDING_HEIGHT = 0.30
AIR_CLADDING_HEIGHT = 0.5
MESA_CLADDING_HEIGHT = 0.1
TECH.PROCESS.ACO.wg_lower_z_coord = MSTACK_SOI_SILICON_OXIDE_HEIGHT + 0.22 + BONDING_HEIGHT
TECH.PROCESS.ACO.wg_upper_z_coord = MSTACK_SOI_SILICON_OXIDE_HEIGHT + 0.22 + BONDING_HEIGHT + MESA_CORE_HEIGHT
HEIGHT_ABOVE_SILICON = MESA_CORE_HEIGHT+BONDING_HEIGHT+AIR_CLADDING_HEIGHT

#MSTACK_SOI_SILICON_OXIDE_HEIGHT = 0.500

TECH.MATERIAL_STACKS.MSTACK_BCB = MaterialStack(name = "BCB",
                                                        materials_heights = [(TECH.MATERIALS.BCB,BONDING_HEIGHT),
                                                                             (TECH.MATERIALS.AIR,AIR_CLADDING_HEIGHT+MESA_CORE_HEIGHT)],
                                                        display_style = DisplayStyle(color = COLOR_WHITE))


TECH.MATERIAL_STACKS.MSTACK_ACLAD = MaterialStack(name = "ACTIVE CLADDING",
                                                           materials_heights = [(TECH.MATERIALS.BCB,BONDING_HEIGHT),
                                                                                (TECH.MATERIALS.InP,MESA_CLADDING_HEIGHT),
                                                                                (TECH.MATERIALS.AIR,AIR_CLADDING_HEIGHT+MESA_CORE_HEIGHT-MESA_CLADDING_HEIGHT)],
                                                           display_style = DisplayStyle(color = COLOR_BLACK))

heights = [(TECH.MATERIALS.BCB,BONDING_HEIGHT),
           (TECH.MATERIALS.InP,LowerCladdingHeight),
           (TECH.MATERIALS.InGaAsP1p55,ActiveLayerHeight),
           (TECH.MATERIALS.InP,UpperCladdingHeight)]

for i in range(Number_of_compensation_stacks):
    heights.append((TECH.MATERIALS.InGaAsP1p2,CompensationLayer1Height))
    heights.append((TECH.MATERIALS.InP,CompensationLayer2Height))
heights.append((TECH.MATERIALS.AIR,AIR_CLADDING_HEIGHT+MESA_CORE_HEIGHT))
TECH.MATERIAL_STACKS.MSTACK_ACORE = MaterialStack(name = "ACTIVE CORE",
                                                  materials_heights = heights,
                                                  display_style = DisplayStyle(color = COLOR_ORANGE))



TECH.PROCESS.ACO.wg_lower_z_coord = MSTACK_SOI_SILICON_OXIDE_HEIGHT + 0.220 + BONDING_HEIGHT
TECH.PROCESS.ACO.wg_upper_z_coord = MSTACK_SOI_SILICON_OXIDE_HEIGHT + 0.220 + BONDING_HEIGHT + MESA_CORE_HEIGHT


################# STEP 3 : DEFINE THE FABRICATION PROCESS FLOW ###############################
from ipkiss.plugins.vfabrication.process_flow import VFabricationProcessFlow

my_process_flow = VFabricationProcessFlow(active_processes = [TECH.PROCESS.ACL,
                                                              TECH.PROCESS.ACO], # DO NOT CHANGE THE SEQUENCE OF THE ELEMENTS ! IT MUST MATCH THE SEQUENCE OF THE COLUMNS IN VFABRICATION PROPERTY process_to_material_stack_map
        process_to_material_stack_map = [
                    #ACL, ACO
                    ((0, 0), TECH.MATERIAL_STACKS.MSTACK_BCB),
                    ((1, 0), TECH.MATERIAL_STACKS.MSTACK_ACLAD),
                    ((0, 1), TECH.MATERIAL_STACKS.MSTACK_ACORE),
                    ((1, 1), TECH.MATERIAL_STACKS.MSTACK_ACORE)],

        is_lf_fabrication = {TECH.PROCESS.ACL  : False,
                             TECH.PROCESS.ACO  : False})

################# STEP 4 : SUPERPOSE THE FABRICATION PROCESS FLOWS ###############################
TECH.VFABRICATION.overwrite_allowed=["PROCESS_FLOW"] #explicitely declare that you want to overwrite this setting
TECH.VFABRICATION.PROCESS_FLOW = TECH.VFABRICATION.PROCESS_FLOW + my_process_flow