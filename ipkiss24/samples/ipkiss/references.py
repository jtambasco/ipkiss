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
# references.py
# Illustrates the use of IPKISS and
# SREF/AREF references (with transformations)
#
# Wim Bogaerts - 2006
# modified by Emmanuel Lambert - 2009

from ipkiss.all import *
import sys

class ReferencesExample(Structure):
    
    def define_elements(self, elems):
        #define a shape: a list of coordinates
        s = Shape([(10.0, 0.0), (15.0, 10.0), (0.0, 10.0), (0.0,5.0), (-15.0, 5.0), (-5.0, 0.0),
             (-10.0, -10.0), (-5.0, -15.0), (10.0, -15.0), (5.0, -10.0), (5.0, -5.0), (10.0, 0.0)])        
        
        #create an element and then a structure from the shape
        base_str = Structure("shape", Boundary(Layer(0), s))
        
        #Transformations: flip over X-axis
        t_flip = NoDistortTransform(v_mirror = True)
        
        #Transformations: relative rotation and scaling
        t_rel = NoDistortTransform(rotation=10.0,
                                absolute_rotation = False,
                                magnification = 1.5,
                                absolute_magnification=False)
        
        #Transformation: absolute rotation and scaling
        t_abs = NoDistortTransform(absolute_rotation = True,
                                   absolute_magnification=True)
        
        # absolute magnification and rotation makes sure that the referred elements
        # keep their original properties (this is not supported in most editors)
        
        #make a structure with a three copies of shape
        shapes_3_ref = Structure("3_shapes",
                                      SRef(base_str, (0.0, 0.0)) +
                                      SRef(base_str, (50.0, 0.0), t_flip) +
                                      SRef(base_str, (100.0, 0.0), t_rel) +
                                      SRef(base_str, (150.0, 0.0), t_abs))
        
        
        # Make a fererence to shapes_"_ref, with another transformation
        shapes_3_ref2 = Structure("3_shapes_bis",
                                      SRef(shapes_3_ref, (0.0, 0.0)) +
                                      SRef(shapes_3_ref, (0.0, 100.0), t_flip) +
                                      SRef(shapes_3_ref, (0.0, 200.0), t_rel) +
                                      SRef(shapes_3_ref, (0.0, 300.0), t_abs))
        
        
        #create a reference axis
        axis = Structure("axis", Path(Layer(2), [(0.0, 300.0), (0.0,0.0), (300.0, 0.0)], 1))
        
        elems += SRef(shapes_3_ref2,(0.0, 0.0))
        elems += SRef(axis, (0.0, 0.0))
        return elems
    
if __name__ == "__main__":
    from ipkiss.primitives.filters.orthogonal_reference_filter import OrthogonalReferenceFilter
    layout = ReferencesExample(name = "layout")
    my_lib = Library(name = "REFS", unit = 1E-6, grid = 5E-9)
    # Add main layout to library
    my_lib += layout
    fileName = "example_refs.gds"
    OP = FileOutputGdsii(fileName, filter = OrthogonalReferenceFilter())
    # Write library
    OP.write(my_lib)
    print "Done : GDS2 file written to %s" %fileName       
    
    

