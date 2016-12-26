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
import sys
from ipkiss.io.gds_layer import AutoGdsiiLayerOutputMap, AutoGdsiiLayerInputMap

from os import path
my_path = path.dirname(sys.modules[__name__].__file__)

class ImportLibraryExample(Structure):
         
         def define_elements(self, elems):
                  #--------------------------------------------------
                  # Make a simple structure containing two rectangles
                  rectangles = Structure("rectangles")
                  rectangles += [ Rectangle(layer = Layer(0), center = (0.0, -150),box_size = (200, 200.0)),
                                            RectanglePath(layer = Layer(0), center = (0.0, 150),box_size = (200, 200.0), line_width= 4.0) ]                                    
                  #import another GDS-II file, put it in the
                  #structure "imported" and prefix all structure names with "imp_"
                  fnGds = path.join(my_path, "import/hex.gds")
                  I1 = InputGdsii(file(fnGds, "rb"))
                  I1.prefix = "imp1_"
                  #the following line is not required if you make a stand-alone ipkiss script (FIXME -- line was added to be able to combine ipkiss and picazzo in one unit test suite)
                  I1.layer_map = AutoGdsiiLayerInputMap()      
                  L1 = I1.read()
                  S1 = L1.top_layout()
                  # Import the same GDS-II file again, but scale the imported file to 70% of its original size
                  # and map the layers of the imported file to other layers in this layout
                  fn2Gds  = path.join(my_path, "import/hex.gds")
                  I2 = InputGdsii(file(fn2Gds, "rb"))
                  I2.prefix = "imp2_"
                  I2.scaling = 0.7
                  I2.layer_map = GdsiiLayerInputMap(layer_map = ({GdsiiLayer(0):Layer(6), 
                                                                  GdsiiLayer(1):Layer(0),
                                                                  GdsiiLayer(2):Layer(1),
                                                                  GdsiiLayer(3):Layer(2)}))
                  L2 = I2.read()
                  S2 = L2.top_layout()
                  
                  #-------------------------------------------------------------------
                  # Add references to all structures
                  xpos = 0.0
                  ypos = 0.0
                  elems += SRef(rectangles, (xpos, ypos))
                  
                  xpos = 350.0
                  ypos = 0
                  elems += SRef(S1, (xpos, ypos))
                  
                  xpos = 750.0
                  ypos = 0
                  elems += SRef(S2, (xpos, ypos))
                                             
                  return elems

if __name__ == "__main__":
         layout = ImportLibraryExample(name = "layout")
         my_lib = Library(name = "IMPORTS", unit = 1E-6, grid = 5E-9)
         # Add main layout to library
         my_lib += layout
         fileName = "example_importLib.gds"
         OP = FileOutputGdsii(fileName)
         # Write library
         OP.write(my_lib)
         LOG.debug("Done : GDS2 file written to %s" %fileName)
        
        


