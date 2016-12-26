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
from ipkiss.technology.technology import TechnologyTree
import copy
from ipkiss.process import PPLayer
from ipkiss.process.layer import ProcessLayer
from ipkiss.process.layer import PatternPurpose
from ipkiss.plugins.photonics.wg.basic import *    # basic waveguides
from picazzo.io.column import *  # StdIO


DT_LINE = 0
DT_SQUARE = 1
DT_HEX = 2
DT_INV = 3

MY_TECH = TechnologyTree()

MY_TECH.PROCESS = TechnologyTree()
MY_TECH.PROCESS.OL35_1 = ProcessLayer("Overlay With III-V etch 1", "OL35_1")
MY_TECH.PROCESS.OL35_2 = ProcessLayer("Overlay With III-V etch 2", "OL35_2")
MY_TECH.PROCESS.BCB_1 = ProcessLayer("Bcb etch1", "BCB_1")
MY_TECH.PROCESS.BCB_2 = ProcessLayer("Bcb etch2", "BCB_2")
MY_TECH.PROCESS.MET_1 = ProcessLayer("Metalization etch1", "MET_1")
MY_TECH.PROCESS.MET_2 = ProcessLayer("Metalization etch2", "MET_2")
MY_TECH.PROCESS.MET_3 = ProcessLayer("Metalization etch3", "MET_3")
MY_TECH.PROCESS.MET_4 = ProcessLayer("Metalization etch4", "MET_4")

MY_TECH.PURPOSE = TechnologyTree()
MY_TECH.PURPOSE.DEFAULT = PatternPurpose(name = "Default", extension = "00")

MY_OUTPUT_MAP = copy.deepcopy(TECH.GDSII.EXPORT_LAYER_MAP)
MY_OUTPUT_MAP.layer_map[PPLayer(process = MY_TECH.PROCESS.OL35_1, purpose = MY_TECH.PURPOSE.DEFAULT)] = GdsiiLayer(number = 101, datatype = DT_LINE) # disk
MY_OUTPUT_MAP.layer_map[PPLayer(process = MY_TECH.PROCESS.OL35_2, purpose = MY_TECH.PURPOSE.DEFAULT)] = GdsiiLayer(number = 102, datatype = DT_LINE) # island
MY_OUTPUT_MAP.layer_map[PPLayer(process = MY_TECH.PROCESS.BCB_1, purpose = MY_TECH.PURPOSE.DEFAULT)] = GdsiiLayer(number = 104, datatype = DT_LINE)  # botvia
MY_OUTPUT_MAP.layer_map[PPLayer(process = MY_TECH.PROCESS.BCB_2, purpose = MY_TECH.PURPOSE.DEFAULT)] = GdsiiLayer(number = 105, datatype = DT_LINE)  # topvia
MY_OUTPUT_MAP.layer_map[PPLayer(process = MY_TECH.PROCESS.MET_1, purpose = MY_TECH.PURPOSE.DEFAULT)] = GdsiiLayer(number = 103, datatype = DT_LINE)  # botcont
MY_OUTPUT_MAP.layer_map[PPLayer(process = MY_TECH.PROCESS.MET_2, purpose = MY_TECH.PURPOSE.DEFAULT)] = GdsiiLayer(number = 106, datatype = DT_LINE)  # topcont
MY_OUTPUT_MAP.layer_map[PPLayer(process = MY_TECH.PROCESS.MET_3, purpose = MY_TECH.PURPOSE.DEFAULT)] = GdsiiLayer(number = 107, datatype = DT_LINE)  # pads
MY_OUTPUT_MAP.layer_map[PPLayer(process = MY_TECH.PROCESS.MET_4, purpose = MY_TECH.PURPOSE.DEFAULT)] = GdsiiLayer(number = 108, datatype = DT_LINE)  # plating



class Layout(Structure):
    
    def define_elements(self, elems):        
        layout = IoColumnGroup(y_spacing=25.0, south_east=(6000.0,0.0))

        #we first create a regular waveguide element 
        wg_def = WgElDefinition(wg_width = TECH.WG.WIRE_WIDTH, trench_width = TECH.WG.TRENCH_WIDTH, process = TECH.PROCESS.WG)
        wg = wg_def(shape = [(0.0,0.0), (500.0,0.0)])
        #on top of it, we add a rectangle element with III-V
        rectangle_III_V = Rectangle(PPLayer(MY_TECH.PROCESS.OL35_1, MY_TECH.PURPOSE.DEFAULT), center = (250.0, 0.0),box_size = (500.0, 20.0))
        
        #assemble both elemeents in a structure
        layout += Structure(name= "wg_with_III_V", elements = [wg, rectangle_III_V], ports = wg.ports)
        
        elems += layout
        return elems


#when exporting the layout to GDS, specify MY_OUTPUT_MAP for the mapping of process/purpose-layer to GDS layer numbers
g = Layout()
g.write_gdsii("example_contact_mask.gds", layer_map=MY_OUTPUT_MAP)

