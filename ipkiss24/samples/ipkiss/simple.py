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


__all__ = ["SimpleExample"]

from ipkiss.all import *

class SimpleExample(Structure):

    def define_elements(self, elems):
        boundaries = Structure(name = "boundaries")
        boundaries += Rectangle  (layer=Layer(0), center=(0,150),box_size=(200, 200.0)) #rectangle 

        boundaries += Circle(layer=Layer(1), center=(0,-150), radius=100) #circle        
   
        paths = Structure(name = "paths")
        paths += RectanglePath(layer=Layer(2), center=(0,150),box_size=(200, 200), line_width=4.0) #rectangle
        paths += CirclePath(layer=Layer(3), center=(0,-150),radius=100, line_width=4.0) #circle 
 
        elems +=  SRef(boundaries, (0,0))
        elems += SRef(paths, (300,0))   #simple references

        return elems
    
    
if (__name__ == "__main__"):
        layout = SimpleExample(name = "layout")
        my_lib = Library(name = "ELEMENTS", unit = 1E-6, grid = 5E-9)
        # Add main layout to library
        my_lib += layout
        fileName = "example_simple.gds"
        OP = FileOutputGdsii(fileName)
        # Write library
        OP.write(my_lib)
        print "Done : GDS2 file written to %s" %fileName       
        #remark : instead of manually creating a Library and exporting it to GDS2, it is also possible to use 
        #the convenient shortcut function "write_gdsii" directly on the Structure, i.e.:
        #layout.write_gdsii("example_simple.gds")        
        