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

#! python

# IPKISS Library
# shapes.py
# Illustrates the use of IPKISS and
# shape operations
#
# Wim Bogaerts - 2008
# further modified by: Emmanuel Lambert

from ipkiss.all import *
import sys


class AdvancedShapesExample(Structure):
    
    def define_elements(self, elems):        
        #empty list of elements
        ala = Structure("arc_line_arc")        
        start_coord = (0.0, 0.0)
        end_coord = (40.0, 40.0)
        radius = 10.0
        for i in range(12):
            start_angle = i * 10 #degrees
            end_angle = - i * 10 #degrees
            ala += Path(Layer(0), ShapeArcLineArc(start_coord, start_angle, radius, end_coord, end_angle, radius), 0.2)
        for i in range(12):
            start_angle = 0.0
            end_angle = 0.0
            end_coord = (40.0, i * 5 - 20.0)
            ala += Path(Layer(0), ShapeArcLineArc(start_coord, start_angle, radius, end_coord, end_angle, radius), 0.2)        
        #define a shape: a list of coordinates        
        elems += [ SRef(ala,(0.0, 0.0)) ]
        return elems
        

if __name__ == "__main__":
        layout = AdvancedShapesExample(name = "advanced_layout")
        my_lib = Library(name = "ADVANCED_ELEMENTS", unit = 1E-6, grid = 5E-9)
        # Add main layout to library
        my_lib += layout
        fileName = "example_advshapes.gds"
        OP = FileOutputGdsii(fileName)
        # Write library
        OP.write(my_lib)
        print "Done : GDS2 file written to %s" %fileName    
        #remark : instead of manually creating a Library and exporting it to GDS2, it is also possible to use 
        #the convenient shortcut function "write_gdsii" directly on the Structure, i.e.:
        #layout.write_gdsii("example_advshapes.gds")        
        
    


