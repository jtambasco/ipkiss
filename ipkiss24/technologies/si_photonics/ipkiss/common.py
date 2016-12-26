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


from ipkiss.technology.technology import ProcessTechnologyTree, TechnologyTree, DelayedInitTechnologyTree
from ipkiss.technology import get_technology
from ipkiss.geometry.coord import Coord2
from ipkiss.process.layer import ProcessLayer, PatternPurpose

TECH = get_technology()

###############################################################################################
# Process Layers
###############################################################################################
        
TECH.PROCESS = ProcessTechnologyTree()

# silicon structuring
TECH.PROCESS.FC = ProcessLayer("Fiber Couplers", "FC")
TECH.PROCESS.WG = ProcessLayer("Waveguides", "WG")

# other
TECH.PROCESS.NONE = ProcessLayer("No Specific Process Layer", "NONE")

####################################################################
# MASK
####################################################################
    
TECH.MASK = TechnologyTree()
TECH.MASK.POLARITY_DF = "DF"
TECH.MASK.POLARITY_LF = "LF"

####################################################################
# MASK LAYER RULES
####################################################################

# This should become process layer dependent!
TECH.TECH = TechnologyTree()
TECH.TECH.MINIMUM_LINE = 0.120
TECH.TECH.MINIMUM_SPACE = 0.120

###############################################################################################
# Pattern Purposes
###############################################################################################

TECH.PURPOSE = TechnologyTree()
# system defined
TECH.PURPOSE.DRAWING = PatternPurpose(name = "Drawing", extension = "DRW", doc="Layout drawing")
#TECH.PURPOSE.ANNOTATE = PatternPurpose(name = "Annotation", extension = "AN", doc="Annotation")
#TECH.PURPOSE.BOUNDARY = PatternPurpose(name = "Boundary", extension = "BND", doc="Boundary for place-and-route")
#TECH.PURPOSE.NET = PatternPurpose(name="Net", extension = "NET", doc="Interconnects")
#TECH.PURPOSE.PIN = PatternPurpose(name="Pin", extension = "PIN", doc="Pins")
#TECH.PURPOSE.WARNING = PatternPurpose(name="Warning", extension = "WRN", doc="Warning for DRC")

TECH.PURPOSE.LF = TechnologyTree()
TECH.PURPOSE.DF = TechnologyTree()
TECH.PURPOSE.LF.MARKER = PatternPurpose(name = "Light-Field Markers", extension = "LFMARK")
TECH.PURPOSE.LF.LINE = PatternPurpose(name = "Light-field Lines", extension = "LIN")
TECH.PURPOSE.LF.ISLAND = PatternPurpose(name = "Light-field Islands", extension = "ISL")
TECH.PURPOSE.LF.TEXT = PatternPurpose(name = "Light-field Text", extension = "LFTXT")
TECH.PURPOSE.LF.DUMMY = PatternPurpose(name = "Light-Field Dummies", extension = "LFDUM")
TECH.PURPOSE.DF_AREA = PatternPurpose(name = "Dark-Field area in Light-Field mask", extension = "DFAREA")
TECH.PURPOSE.LF_AREA = PatternPurpose(name = "Light-Field area in Dark-Field mask", extension = "LFAREA")
TECH.PURPOSE.DF.MARKER = PatternPurpose(name = "Dark-Field Marker", extension = "DFMARK")
TECH.PURPOSE.DF.HOLE = PatternPurpose(name = "Dark-field Holes", extension = "HOL")
TECH.PURPOSE.DF.TRENCH = PatternPurpose(name = "Dark-field Lines=Trenches", extension = "TRE")
TECH.PURPOSE.DF.SQUARE = PatternPurpose(name = "Dark-field Square Holes", extension = "SQU")
TECH.PURPOSE.DF.TEXT = PatternPurpose(name = "Dark-field Text", extension = "DFTXT")
TECH.PURPOSE.DF.DUMMY = PatternPurpose(name = "Dark-Field Dummies", extension = "DFDUM")
TECH.PURPOSE.CORE = TECH.PURPOSE.LF.LINE
TECH.PURPOSE.TRENCH = TECH.PURPOSE.DF.TRENCH
TECH.PURPOSE.TEXT = TECH.PURPOSE.DF.TEXT
TECH.PURPOSE.CLADDING = TECH.PURPOSE.LF_AREA
TECH.PURPOSE.HOLE = TECH.PURPOSE.DF.HOLE

# general purposes (layer NONE)
TECH.PURPOSE.FINAL = PatternPurpose(name = "Final mask layer", extension = "FINAL")
TECH.PURPOSE.NO_FILL = PatternPurpose(name = "No tiling", extension = "NOFILL")
TECH.PURPOSE.NO_GEN = PatternPurpose(name = "No generated data", extension = "NOGEN")
TECH.PURPOSE.NO_PERF = PatternPurpose(name = "No metal perforation", extension = "NOPERF")
TECH.PURPOSE.DOC = PatternPurpose(name = "Documentation", extension = "DOC")
TECH.PURPOSE.BBOX = PatternPurpose(name = "Bounding Box", extension = "BBOX")
TECH.PURPOSE.INVISIBLE = PatternPurpose(name = "Invisible", extension = "INVIS")

# error purposes
TECH.PURPOSE.ERROR = TechnologyTree()
TECH.PURPOSE.ERROR.SPACE = PatternPurpose(name="Too small space", extension = "ERRS")
TECH.PURPOSE.ERROR.WIDTH = PatternPurpose(name="Too small width", extension = "ERRW")
TECH.PURPOSE.ERROR.ANGLE = PatternPurpose(name="Acute angle", extension = "ERRA") 
TECH.PURPOSE.ERROR.MINEXT = PatternPurpose(name="Too small extension", extension = "ERRMEXT")
TECH.PURPOSE.ERROR.MAXEXT = PatternPurpose(name="Too long extension", extension = "ERREXT")
TECH.PURPOSE.ERROR.MINENC = PatternPurpose(name="Too small enclosure", extension = "ERRENC")
TECH.PURPOSE.ERROR.OVERLAP = PatternPurpose(name="Wrong overlap between layers or datatypes", extension = "ERROVL")
TECH.PURPOSE.ERROR.INSIDE = PatternPurpose(name="Layer not inside another layer", extension = "ERRINS")


################################################################################
# GENERIC LAYERS
################################################################################

from ipkiss.primitives.layer import Layer 
TECH.LAYER = TechnologyTree()
#TECH.LAYER.DUMMY = Layer(100, "dummy")
#TECH.LAYER.DOC   = Layer(101, "doc")
#TECH.LAYER.LABEL = Layer(102, "label")
#TECH.LAYER.ERROR = Layer(103, "error")
#TECH.LAYER.NO_SIZE = Layer(104, "no_size")
#TECH.LAYER.NO_GEN = Layer(105, "no_gen")
#TECH.LAYER.RED_FILL = Layer(106, "red_fill")
#TECH.LAYER.NO_FILL = Layer(107, "no_fill")
#TECH.LAYER.NO_DHOL = Layer(108, "no_dhol")
#TECH.LAYER.COVER = Layer(109, "cover")
#TECH.LAYER.CHIPEDGE = Layer(110, "chipedge")
TECH.LAYER.SIZE_BOX = Layer(36, "size_box")

####################################################################
# DEFINITION OF TECHNOLOGY TREES (the layer maps are attached in the technology-specific packages)
####################################################################

TECH.OPENACCESS = TechnologyTree()

####################################################################
# METAL DEFINITION
####################################################################
TECH.METAL = TechnologyTree()

####################################################################
# WAVEGUIDE DEFINITION
####################################################################
TECH.WG = TechnologyTree()
TECH.FC = TechnologyTree()

class TechWgTree(DelayedInitTechnologyTree):
    def initialize(self):
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition, Wg2ElDefinition
        self.WIRE = WgElDefinition(wg_width =  TECH.WG.WIRE_WIDTH, 
                                trench_width = TECH.WG.TRENCH_WIDTH,
                                process = TECH.PROCESS.WG)
        
        self.WIRE2 = Wg2ElDefinition(wg_width =  TECH.WG.WIRE_WIDTH, 
                                trench_width = TECH.WG.TRENCH_WIDTH,
                                process = TECH.PROCESS.WG)
        
        self.DEFAULT = self.WIRE
        
        
        # FIXME -- old stuff to be removed !!! DEPRECATED-----
        self.WG_WIRE = self.WIRE
        self.WG_WIRE2 = self.WIRE2

        self.FC_WIRE = WgElDefinition(wg_width =  TECH.FC.WIRE_WIDTH, 
                                   trench_width = TECH.FC.TRENCH_WIDTH,
                                   process = TECH.PROCESS.FC)
        
        self.FC_WIRE2 = Wg2ElDefinition(wg_width =  TECH.FC.WIRE_WIDTH, 
                                     trench_width = TECH.FC.TRENCH_WIDTH,
                                     process = TECH.PROCESS.FC)
        # -----------------------------------------------------


    
TECH.WGDEF = TechWgTree()


class TechFcWireTree(DelayedInitTechnologyTree):
    def initialize(self):
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition, Wg2ElDefinition
        self.WIRE = WgElDefinition(wg_width =  TECH.FC.WIRE_WIDTH, 
                                   trench_width = TECH.FC.TRENCH_WIDTH,
                                   process = TECH.PROCESS.FC)
        
        self.FC_WIRE2 = Wg2ElDefinition(wg_width =  TECH.FC.WIRE_WIDTH, 
                                     trench_width = TECH.FC.TRENCH_WIDTH,
                                     process = TECH.PROCESS.FC)

        self.DEFAULT = self.WIRE
        
TECH.FCDEF = TechFcWireTree()     



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
                      TECH.PROCESS.FC,
                      TECH.PROCESS.WG,
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
TECH.overwrite_allowed.append('DISPLAY')


