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

from ..filter import Filter
from ...geometry.coord import Coord2
from ...geometry.shape import Shape
from ...geometry.transforms.rotation import Rotation
from ...primitives.elements.shape import Boundary
from ipcore.all import IntProperty, BoolProperty
import numpy


class BoundaryCutFilter(Filter):
    max_vertex_count = IntProperty(default = 4000)
    save_debug_gds = BoolProperty(default = False)
    
    def __filter_Boundary__(self, item, DEBUG_ID = None): 
        if DEBUG_ID is None:
            import random
            DEBUG_ID = str(random.randint(0,999999))          
        
        if len(item.shape)<=self.max_vertex_count:
            result_boundaries = [item]                           
        else:
            if self.save_debug_gds: #DEBUG     
                from ipkiss.all import Structure
                from ipkiss.primitives import Library
                from ipkiss.io.output_gdsii import FileOutputGdsii, OutputGdsii
                lib_debug = Library(name = "DEBUG")
                lib_debug += Structure(elements = [item])
                OP2 = FileOutputGdsii(FileName = "debug_struct_boundary_cut_%s_ORIGINAL.gds"%(DEBUG_ID), cut_boundaries = False)
                OP2.write(lib_debug)                     
                print DEBUG_ID, " -- DECISION CRITERIUM len(item.shape) = ", len(item.shape)
                print "max_vertex_count = ", self.max_vertex_count
                print "-------------"            
            result_boundaries = []
            #define the horizontal cutting line
            si = item.size_info()
            cutting_y = si.south + (si.north - si.south) / 3.0 #do not take 2, to avoid particular problems with Y-symmetric structures !
            #make a new list of all the points as Coord2 and indicate for every point : its position in reference to the cutting line and its index in the list of points
            points = []
            index = 0
            for p in item.shape.points:
                c = Coord2(p)
                c.side = (p[1] - cutting_y)>=0
                c.index = index
                index = index + 1
                points.append(c)
                
            #mark transition points 
            transition_points_unsorted = []
            current_side = (points[0].y - cutting_y)>=0
            for c in points + [points[0]]:
                if c.side != current_side:
                    transition_points_unsorted.append(c)
                    current_side = c.side            
        
            transition_points = sorted(transition_points_unsorted, cmp = lambda p1,p2: int(numpy.sign(p1.x - p2.x)))  
            
            #if the 2 first transition points are consecutive points in the list of points, then ignore these
            while (len(transition_points)>0) and ((abs(transition_points[0].index - transition_points[1].index) == 1) or (transition_points[0].index == 0 and transition_points[1].index == len(points)-1) or (transition_points[1].index == 0 and transition_points[0].index == len(points)-1)):
                transition_points = transition_points[2:]
                
            if len(transition_points)==0:
                result_boundaries = self.__rotate_and_filter__(item, DEBUG_ID = DEBUG_ID)
            else:
                if self.save_debug_gds: #DEBUG    
                    from ipkiss.all import Path, TECH
                    DEBUG_trans_point_path = Path(layer = TECH.PPLAYER.FC.TEXT, shape = Shape(transition_points), line_width = 0)                
                
                #build the two composing Boundaries and pull them recursively through the filter again
                tp1 = transition_points[0]
                tp2 = transition_points[1]
                if tp1.index > tp2.index:
                    tp1 = transition_points[1]
                    tp2 = transition_points[0]
                if len(item.shape.intersections(other_shape = Shape(points = [tp1, tp2])))>2:
                    result_boundaries = self.__rotate_and_filter__(item, DEBUG_ID = DEBUG_ID)
                else:
                    points_piece1 = points[tp1.index:tp2.index+1]
                    points_piece2 = points[tp2.index:]+points[:tp1.index+1]
                    boundary1 = Boundary(layer = item.layer, shape = Shape(points_piece1, closed = True))
                    boundary2 = Boundary(layer = item.layer, shape = Shape(points_piece2, closed = True))
                    #make a recursive call to filter the two pieces in turn
                    filtered_boundaries1 = self.__filter_Boundary__(boundary1, DEBUG_ID = DEBUG_ID + "_1")
                    filtered_boundaries2 = self.__filter_Boundary__(boundary2, DEBUG_ID = DEBUG_ID + "_2")
                    result_boundaries.extend(filtered_boundaries1)
                    result_boundaries.extend(filtered_boundaries2)
            
                if self.save_debug_gds: #DEBUG 
                    from ipkiss.all import Structure
                    from ipkiss.primitives import Library
                    from ipkiss.io.output_gdsii import FileOutputGdsii, OutputGdsii
                    debug_struct = Structure(elements = result_boundaries + DEBUG_trans_point_path)            
                    my_lib = Library(name = "DEBUG")
                    my_lib += debug_struct
                    OP = FileOutputGdsii(FileName = "debug_struct_boundary_cut_%s.gds"%(DEBUG_ID), cut_boundaries = False)
                    OP.write(my_lib)   
                    
        return result_boundaries  
    
    def __rotate_and_filter__(self, item, DEBUG_ID):
        #emergency strategy : rotate the item over 50 degrees and try again... 
        rot_angle = 50.0 #360 is niet deelbaar door 50
        rot_item = item.transform_copy(transformation = Rotation(rotation = rot_angle)).flat_copy()
        rot_boundaries = self.__filter_Boundary__(rot_item, DEBUG_ID = DEBUG_ID + "_ROT")
        result = [b.transform_copy(transformation = Rotation(rotation = -rot_angle)).flat_copy() for b in rot_boundaries]        
        return result
    

    
 