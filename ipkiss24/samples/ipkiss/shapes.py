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

class ShapesExample(Structure):
    
    def define_elements(self, elems):
        #define a shape: a list of coordinates
        s = Shape([(10.0, 0.0), (15.0, 10.0), (0.0, 10.0), (0.0,5.0), (-15.0, 5.0), (-5.0, 0.0),
                       (-10.0, -10.0), (-5.0, -15.0), (10.0, -15.0), (5.0, -10.0), (5.0, -5.0)],
                       closed = True)
        
        
        #create an element and then a structure from the shape
        S1 = Structure("shape", Boundary(Layer(0), s))
        
        #translate a copy of the shape
        t = s.move_copy((0.0, 20.0))
        S2 = Structure("shape_trans", Boundary(Layer(0), t))
        
        #rotate the shape (angle in degree)
        t = s.rotate_copy((0.0, 0.0), 50)
        S3 = Structure("shape_rot", Boundary(Layer(0), t))
        
        #scale the shape
        t = s.magnify_copy((0.0, 0.0), 1.2)
        S4 = Structure("shape_scale", Boundary(Layer(0), t))
        
        #stretch the shape horizontally and squeeze vertically 
        t = Stretch(stretch_center = (0.0, 0.0), stretch_factor = (1.5, 0.5))(s)
        S5 = Structure("shape_stretch", Boundary(Layer(0), t))
        
        #fit the shape in a box
        south_west = (-7.0, -7.0)
        north_east = (7.0, 7.0)
        t = ShapeFit(s, south_west, north_east)
        S6 = Structure("shape_fit", Boundary(Layer(0), t))
        
        #create a shape which traces the contour with a certain line width
        t = ShapePath(original_shape = s, path_width = 0.5)
        S7 = Structure("ShapePath1", Boundary(Layer(0), t))
        
        t = ShapePathRounded(original_shape = s, path_width = 0.5)
        S8 = Structure("ShapePath2", Boundary(Layer(0), t))
        
        #expand the shape with a certain distance
        t = ShapeGrow(s, 1.0)
        S9 = Structure("shape_grow", Boundary(Layer(1), t) + Boundary(Layer(0), s))
        
        #round the shape with a given radius
        t = ShapeRound(original_shape = s, radius = 2.0)
        S10 = Structure("shape_round", Boundary(Layer(1), t) + Boundary(Layer(0), s))
        
        elems +=  [ SRef(S1,       (0.0, 200.0)),
                     SRef(S2, (50.0, 200.0)),
                     SRef(S3,   (100.0, 200.0)),
                     SRef(S4, (0.0, 150.0)),
                     SRef(S5, (50.0, 150.0)),
                     SRef(S6, (100.0, 150.0)),
                     SRef(S7, (0.0, 100.0)),
                     SRef(S8, (50.0, 100.0)),
                     SRef(S9, (100.0, 100.0)),
                     SRef(S10, (150.0, 100.0))
                     ]
        
        return elems

if (__name__ == "__main__"):
        layout = ShapesExample(name = "layout")
        my_lib = Library(name = "ELEMENTS", unit = 1E-6, grid = 5E-9)
        # Add main layout to library
        my_lib += layout
        fileName = "example_shapes.gds"
        OP = FileOutputGdsii(fileName)
        # Write library
        OP.write(my_lib)
        print "Done : GDS2 file written to %s" %fileName    
        #remark : instead of manually creating a Library and exporting it to GDS2, it is also possible to use 
        #the convenient shortcut function "write_gdsii" directly on the Structure, i.e.:
        #layout.write_gdsii("example_shapes.gds")
        


