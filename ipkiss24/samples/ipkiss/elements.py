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
from math import *

class ElementsExample(Structure):
    
    def define_elements(self, elems):
        #--------------
        #Straight lines
        lines = Structure("lines")
        #start with an empty list of elements and append
        for i in range (5, 50, 5):
            #horizontal line
            L = Line(layer = Layer(0), begin_coord = (0, i), end_coord = (2 * i,i), line_width = 1.0)
            lines += L
            #diagonal line
            lines += Line(Layer(0), (10+i, 0), (10+2*i, i), 1.0)
            #vertical line
            lines += Line(Layer(0), (60+i, 0), (60+i, i), 1.0)
        
        
        # make a structure with a given name, fill it with elements
        # and direct it to the output
        
        #--------------
        #Wedges/tapers
        tapers = Structure("tapers")
        for i in range (10, 60, 10):
            #horizontal taper
            tapers += Wedge(layer = Layer(0), begin_coord = (0, i), end_coord = (100,i), begin_width = 1.0, end_width = i/10.0)
            #diagonal taper
            tapers += ParabolicWedge(Layer(0), (150+i, 0), (210+i, 60), 1.0, i/10.0)
            
        
        ##-----------------
        ##Circles and rings
        circles = Structure("circles")
        xpos = 0
        for i in range (5, 30, 5):
            #circle
            circles += Circle(layer = Layer(0), center = (xpos,0), radius = i)
            #concentric ring
            circles += CirclePath(Layer(0), (xpos,0), i+10, 2.0)
            xpos += 80
        
        
        ##----------------
        ##Ellipses
        ellipses = Structure("ellipses")
        xpos = 0
        for i in range (5, 30, 5):
            #filled ellipse
            ellipses += Ellipse(layer = Layer(0), center = (xpos,0), box_size = (2 * i, 60))
            #elliptic ring
            ellipses += EllipsePath( Layer(0), (xpos,0), (60, 2*i), 2.0)
            xpos += 80
        
        ##------------------------
        ##Arcs and elliptical arcs
        arcs = Structure("arcs")
        for i in range (5, 50, 5):
            #circular arc
            arcs += ArcPath(layer = Layer(0), center = (0,0), radius  = i, start_angle = 0, end_angle = 120, line_width = 1.0)
            #elliptical_arc
            arcs += EllipseArcPath(layer = Layer(0), center = (120,0), box_size = (2 * i, i) , start_angle = 45, end_angle = 270, line_width = 1.0)
            
        ##------------------------
        ##Bend and relativebend
        bends = Structure("bends")
        for i in range (5, 50, 5):
            bends += BendPath(layer = Layer(0), start_point = (0,0), radius = i, line_width = 1.5, input_angle=60.0, output_angle = 90.0+i*2.0)
            bends += RelativeBendPath(layer = Layer(0), start_point = (100,0), radius = i, line_width = 1.5, input_angle=60.0, angle_amount = 30.0+i*2.0)        
        
        ##---------------------------------
        ##rectangles and rounded rectangles
        rectangles = Structure("rectangles")
        xpos = 0
        for i in range (5, 30, 5):
            #filled rectangle using Rectangle
            rectangles += Rectangle(layer = Layer(0), center = (xpos,0), box_size = (2 * i, 50))
            #rectangular line 
            rectangles += RectanglePath( Layer(0), (xpos,0), (2*i + 10, 60), line_width = 2.0)
            #filled slightly round rectangle using RoundedRectangle
            rectangles += RoundedRectangle( layer = Layer(0), center = (xpos,-100), box_size = (2 * i, 50), radius = 1)
            #slightly rounded rectangular line 
            rectangles += RoundedRectanglePath(Layer(0), (xpos,-100), (2*i+10, 60), 1, 2.0)
            #very slightly round rectangle using RoundedRectangle
            rectangles += RoundedRectangle( Layer(0), (xpos,-200), (2 * i, 50), i)
            #very rounded rectangular line 
            rectangles += RoundedRectanglePath(Layer(0), (xpos,-200), (2*i+10, 60), i, 2.0)
            xpos += 80
        
        #------------------------------------------------------------------
        #boxes
        #A box is similar as a rectangle, but is another data type in GDSII
        boxes = Structure("boxes")
        xpos = 0
        for i in range (5, 30, 5):
            #filled rectangle using Box
            boxes += Box(layer = Layer(0), center = (xpos + i,25), box_size = (2 * i, 50))
            xpos += 80
        
        
        ##------------------------------------------------------------------
        ##Regular Polygons
        polygons = Structure("polygons")
        xpos = 0
        for i in range (5, 10):
            #filled regular_polygon
            polygons += RegularPolygon(layer = Layer(0), center = (xpos,0), radius = 20, n_o_sides = i )
            #regular_polygon line
            polygons += RegularPolygonPath(layer = Layer(0), center = (xpos,0), radius = 30, n_o_sides = i, line_width = 2.0 )
            xpos += 80
        
        ##-------------------------------------------------------------------
        ## cross markers
        markers = Structure("markers")
        xpos = 0
        for i in range (5, 25, 5):
            markers += Cross (layer = Layer(0), center = (xpos,0), box_size = 40, thickness = i)
            xpos += 60
        
        #------------------------------------------------------------------
        #create a hexagon and make a triangular lattice out of it
        hexagon_radius = 2.0
        lattice_constant = 5.0
        
        # 1 hexagon structure
        hexagon = Structure("hexagon", Hexagon (layer = Layer(0), center = (0.0,0.0), radius = hexagon_radius))
        
        # Now make a unit cell of a triangular lattice, consisting of 2 hexagons
        # because we already have a hexagon, we use a reference to the existing hexagon
        unit_cell = Structure("lattice_unit_cell")
        
        translation_vector = (lattice_constant/2.0, sqrt(3) * lattice_constant / 2.0)
        unit_cell += SRef (hexagon, position = (0.0,0.0))
        unit_cell += SRef (hexagon, position = translation_vector)
        
        # Now we will take this unit cell, and make an array reference (aref) of it
        lattice = Structure("lattice")
        n_o_periods = (40, 10) #in X and Y-direction
        lattice_vector = (lattice_constant, sqrt(3) * lattice_constant) #translation in X and Y
        lattice += ARef (unit_cell, origin = (0.0,0.0), period = lattice_vector, n_o_periods = n_o_periods)
        
        #-------------------------------------------------------------------
        #Noughts and crosses
        
        # a nought
        nought = Structure("nought", CirclePath (Layer(0), (0,0), 15, 6))
        # a cross
        cross = Structure("cross", [Line(Layer(0), (-15,-15), (15,15),6) , Line(Layer(0), (-15,15), (15,-15),6)])
        # noughts and crosses
        tic_tac_toe = Structure("tic_tac_toe")
        tic_tac_toe += Line (Layer(0),(50,0),(50,-150),3) + Line (Layer(0),(100,0),(100,-150),3) #vertical lines
        tic_tac_toe += Line (Layer(0),(0,-50),(150,-50),3) + Line (Layer(0),(0,-100),(150,-100),3) #vertical lines
        
        tic_tac_toe += (SRef(nought, (25,-25))
                   + SRef(nought, (75,-25))
                   + SRef(nought, (125,-75))
                   + SRef(nought, (25,-125))
                   + SRef(nought, (75,-125)))
                   #references to noughts
        tic_tac_toe += (SRef(cross, (125,-25))
                   + SRef(cross, (25,-75))
                   + SRef(cross, (75,-75))
                   + SRef(cross, (125,-125)))
                   #references to crosses
        
        #-------------------------------------------------------------------
        # text labels
        text = Structure("text")
        text += Label(layer = Layer(0), text = "TIC-TAC-TOE", alignment = (TEXT_ALIGN_LEFT, TEXT_ALIGN_TOP), font = 0, height = 30)
        
        #-------------------------------------------------------------------
        # polygon text
        polygon_text = Structure("polygon_text")
        polygon_text += PolygonText (layer = Layer(0), text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890(){}[];:.,/\\?!#$%*-+_=<>", alignment = (TEXT_ALIGN_LEFT, TEXT_ALIGN_TOP), font=0, height = 15)
        polygon_text_rotated = Structure("polygon_text_rotated")
        polygon_text_rotated += PolygonText (layer = Layer(0), text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890(){}[];:.,/\\?!#$%*-+_=<>", coordinate=(0.0, -30.0), alignment = (TEXT_ALIGN_LEFT, TEXT_ALIGN_TOP), font=1, height = 15, transformation = Rotation((0.0, 0.0), -3.0))
        
        #-------------------------------------------------------------------
        #construct a polygon from scratch
        enterprise = Structure("enterprise")
        coordinates = Shape([(-179,54), (101,54), (101,149), (59,149), (-11,172), (-39,209), (-11,246),
                                 (59,268), (696,268), (768,246), (795,209), (768,172), (696,149), (147,149),
                                 (147,54), (186,54), (238,31), (258,-5), (238,-42), (186,-65), (147,-65),
                                 (147,-139), (696,-139), (768,-161), (795,-198), (768,-235), (696,-258), (59,-258),
                                 (-11,-235), (-39,-198), (-11,-161), (59,-139), (101,-139), (101,-65), (-179,-65),
                                 (-179,-100), (-297,-262), (-487,-323), (-678,-262), (-795,-100), (-795,100),
                                 (-678,262), (-487,323), (-297,262), (-179,100)],
                                 closed = True
                                 )
        coordinates.magnify((0.0, 0.0), 0.1)
        coordinates.rotate((0.0, 0.0), -45.0)
        coordinates.move((100, 0))
        enterprise += Boundary(layer=Layer(0), shape = coordinates)
        
        ##-------------------------------------------------------------------
        ## Create the top structure, containing references to 
        ## all other structures       
        xpos = 0
        ypos = 1000

        elems += SRef(lines, (xpos, ypos))
        elems += SRef(arcs, (xpos+200, ypos))
        elems += SRef(bends, (xpos+265, ypos))
        ypos -= 100
        elems += SRef(circles, (xpos, ypos))
        ypos -= 100
        elems += SRef(ellipses, (xpos, ypos))
        ypos -= 100
        elems += SRef(rectangles, (xpos, ypos))
        ypos -= 300
        elems += SRef(polygons, (xpos, ypos))
        ypos -= 100
        elems += SRef(boxes, (xpos, ypos))
        ypos -= 100        
        elems += SRef(polygon_text, (xpos, ypos))
        ypos -= 100        
        elems += SRef(polygon_text_rotated, (xpos, ypos))
        xpos = 500
        ypos = 1000
        elems += SRef(lattice, (xpos, ypos))
        ypos -= 150
        elems += SRef(tapers, (xpos, ypos))
        ypos -= 50
        elems += SRef(tic_tac_toe, (xpos, ypos))
        ypos -= 200
        elems += SRef(text, (xpos, ypos))
        ypos -=100        
        elems += SRef(markers, (xpos, ypos))        
        ypos -=150
        elems += SRef(enterprise, (xpos, ypos))
        
        return elems
        
    
if __name__ == "__main__":
        layout = ElementsExample(name = "layout")
        my_lib = Library(name = "ELEMENTS", unit = 1E-6, grid = 5E-9)
        # Add main layout to library
        my_lib += layout
        fileName = "example_elements.gds"
        OP = FileOutputGdsii(fileName)
        # Write library
        OP.write(my_lib)
        LOG.debug("Done : GDS2 file written to %s" %fileName)       
        #remark : instead of manually creating a Library and exporting it to GDS2, it is also possible to use 
        #the convenient shortcut function "write_gdsii" directly on the Structure, i.e.:
        #layout.write_gdsii("example_elements.gds")            
    

