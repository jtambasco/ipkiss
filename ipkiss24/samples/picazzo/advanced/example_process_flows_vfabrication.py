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

from technologies.si_photonics.picazzo.default import *
from ipkiss.all import *

################# STEP 1 : DEFINE THE NEW PROCESSES ###############################
from ipkiss.technology.technology import TechnologyLibrary, TechnologyTree, DelayedInitTechnologyTree

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
TECH.MATERIALS.BCB = Material(name = "BCB",display_style = DisplayStyle(color = COLOR_GREEN))

nInP = 3.1
nBCB = 1.544 
TECH.MATERIALS.InP.epsilon = nInP**2 #9.61
TECH.MATERIALS.BCB.epsilon = nBCB**2 #2.38

TECH.MATERIAL_STACKS.MSTACK_BCB = MaterialStack(name = "BCB", 
                                                        materials_heights = [(TECH.MATERIALS.BCB,0.480), 
                                                                             (TECH.MATERIALS.AIR,1.3)], 
                                                        display_style = DisplayStyle(color = COLOR_WHITE))


TECH.MATERIAL_STACKS.MSTACK_ACLAD = MaterialStack(name = "ACTIVE CLADDING", 
                                                           materials_heights = [(TECH.MATERIALS.BCB,0.480),
                                                                                (TECH.MATERIALS.InP,0.2),
                                                                                (TECH.MATERIALS.AIR,1.1)], 
                                                           display_style = DisplayStyle(color = COLOR_BLACK))

TECH.MATERIAL_STACKS.MSTACK_ACORE = MaterialStack(name = "ACTIVE CORE", 
                                                  materials_heights = [(TECH.MATERIALS.BCB,0.480),
                                                                       (TECH.MATERIALS.InP,0.8),
                                                                       (TECH.MATERIALS.AIR,0.5)],
                                                  display_style = DisplayStyle(color = COLOR_ORANGE))

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


from ipkiss.plugins.photonics.wg.basic import *
from ipkiss.all import *

class MyRing(Structure):
        radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
        spacing = PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH * 4.0)
        wg_definition = WgDefProperty(default = TECH.WGDEF.WIRE)

        def define_elements(self, elems):
                #the ring
                c = ShapeCircle(center = (0.0, 0.0),
                                radius = self.radius,
                                start_face_angle = 90.0,
                                end_face_angle = 90.0)

                # the access waveguide
                w_y_co = -self.radius - self.spacing
                w_half_length = self.radius + self.wg_definition.wg_width / 2.0 + self.wg_definition.trench_width
                w = Shape([(-w_half_length, w_y_co), (w_half_length, w_y_co)])

                # add the active cladding and active core to the elements
                elems += self.wg_definition(shape = c)
                elems += self.wg_definition(shape = w)
                elems += Rectangle(center = (0.0, 0.0),
                                   box_size=(9.0,9.0),
                                   layer=TECH.PPLAYER.ACL.DEFAULT)
                elems += Rectangle(center = (5.0, 0.0),
                                   box_size=(1.0,2.0),
                                   layer=TECH.PPLAYER.ACO.DEFAULT)                
                
                return elems

wg_def = WgElDefinition(wg_width = 0.60, trench_width = 0.8)
r = MyRing(radius = 5.0, wg_definition = wg_def)
r.write_gdsii("my_ring.gds")

from ipkiss.plugins.vfabrication import *
r.visualize_2d()

r.visualize_3d_y_crosssection(y_co = 0.0, resolution = 30)

vtk_filename = r.visualize_3d_vtk(resolution = 30)
print "Generated VTK file : ",vtk_filename 
