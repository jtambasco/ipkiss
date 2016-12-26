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

from ipkiss.logos.basic import Logo
from ipkiss.primitives.elements.shape import Line, ArcPath, Boundary, Wedge, Path, Rectangle
from ipkiss.primitives.elements.text import PolygonText
from ipkiss.geometry.shapes.basic import ShapeEllipseArc
from ipkiss.geometry.transforms.magnification import Magnification
from ipkiss.geometry.transforms.rotation import Rotation
from ipkiss.constants import TEXT_ALIGN_LEFT, TEXT_ALIGN_RIGHT, TEXT_ALIGN_CENTER, TEXT_ALIGN_TOP, TEXT_ALIGN_BOTTOM, TEXT_ALIGN_MIDDLE, PATH_TYPE_ROUNDED

__all__ = ["ImecLogo", "IntecLogo", "UGentLogo"]


class IntecLogo(Logo):
    __name_prefix__ = "logo_intec_"
          
    def define_elements(self, elems):        
        logo_size = (1.0, 1.1)
        scale = min([self.size[0]/logo_size[0],self.size[1]/logo_size[1]])
        line_width = scale * 0.05
        elems += PolygonText(self.layer,'INTEC', (scale/2, 0.0), (TEXT_ALIGN_CENTER, TEXT_ALIGN_BOTTOM), 1, scale * 0.19)
        elems += Line(self.layer, (0.0,0.3*scale), (scale, 0.3 * scale), line_width, PATH_TYPE_ROUNDED)
        elems += Line(self.layer, (0.0,0.4*scale), (scale, 0.4 * scale), line_width, PATH_TYPE_ROUNDED)
        elems += Line(self.layer, (0.0,0.5*scale), (0.4 * scale, 0.5 * scale), line_width, PATH_TYPE_ROUNDED)
        elems += Line(self.layer, (0.6 * scale ,0.5*scale), (scale, 0.5 * scale), line_width, PATH_TYPE_ROUNDED)
        elems += ArcPath(self.layer, (0.5 * scale ,0.6 * scale), 0.1 * scale, line_width, 0.0, 180.0, 10.0, PATH_TYPE_ROUNDED)
        elems += ArcPath(self.layer, (0.5 * scale ,0.6 * scale), 0.2 * scale, line_width, 0.0, 180.0, 10.0, PATH_TYPE_ROUNDED)
        elems += ArcPath(self.layer, (0.5 * scale ,0.6 * scale), 0.3 * scale, line_width, 0.0, 180.0, 10.0, PATH_TYPE_ROUNDED)
        elems += ArcPath(self.layer, (0.5 * scale ,0.6 * scale), 0.4 * scale, line_width, 0.0, 180.0, 10.0, PATH_TYPE_ROUNDED)
        elems += ArcPath(self.layer, (0.5 * scale ,0.6 * scale), 0.5 * scale, line_width, 0.0, 180.0, 10.0, PATH_TYPE_ROUNDED)
        return elems
    

class UGentLogo(Logo):
    __name_prefix__ = "logo_ugent_"

    def define_elements(self, elems):       
        logo_size = (1.0, 1.05)
        scale = min([self.size[0]/logo_size[0],self.size[1]/logo_size[1]])
        line_width = scale * 0.025
        elems += PolygonText(self.layer,'UNIVERSITEIT', (scale/2, scale* 0.25), (TEXT_ALIGN_CENTER, TEXT_ALIGN_BOTTOM), 1,  scale * 0.12)
        elems += PolygonText(self.layer,'GENT', (scale/2, scale*  0.05), (TEXT_ALIGN_CENTER, TEXT_ALIGN_BOTTOM), 1,  scale * 0.12)
        elems += Line(self.layer, (0.0,0.0), (scale, 0.0), line_width)
        elems += Line(self.layer, (0.15*scale,0.45*scale), (0.85*scale, 0.45 * scale), line_width)
        elems += Line(self.layer, (0.18*scale,0.5*scale), (0.82*scale, 0.5 * scale), line_width)
        elems += Line(self.layer, (0.15*scale,0.85*scale), (0.85*scale, 0.85 * scale), line_width)
        elems += Line(self.layer, (0.18*scale,0.8*scale), (0.82*scale, 0.8 * scale), line_width)
        elems += Path(self.layer, [(0.14*scale,0.9*scale),(scale/2.0,1.05*scale),(0.86*scale, 0.9 * scale)], line_width)
        elems += Boundary(self.layer, [(0.20 * scale, 0.88*scale), (0.8*scale, 0.88 * scale), (0.8*scale, 0.89*scale), (scale/2.0, 1.0* scale), (0.2 * scale, 0.89 * scale), (0.20 * scale, 0.88 * scale)])
        elems += Wedge(self.layer, (scale * 0.25,scale * 0.53), (scale * 0.25, scale * 0.77), scale * 0.06, scale * 0.04)
        elems += Wedge(self.layer, (scale * 0.35,scale * 0.53), (scale * 0.35, scale * 0.77), scale * 0.06, scale * 0.04)
        elems += Wedge(self.layer, (scale * 0.45,scale * 0.53), (scale * 0.45, scale * 0.77), scale * 0.06, scale * 0.04)
        elems += Wedge(self.layer, (scale * 0.55,scale * 0.53), (scale * 0.55, scale * 0.77), scale * 0.06, scale * 0.04)
        elems += Wedge(self.layer, (scale * 0.65,scale * 0.53), (scale * 0.65, scale * 0.77), scale * 0.06, scale * 0.04)
        elems += Wedge(self.layer, (scale * 0.75,scale * 0.53), (scale * 0.75, scale * 0.77), scale * 0.06, scale * 0.04)
        return elems

class ImecLogo(Logo):
    __name_prefix__ = "logo_imec_"
        
    def define_elements(self, elems):       
        logo_size = (112.0, 100.0)
        scale = min([self.size[0]/logo_size[0],self.size[1]/logo_size[1]])
        line_width = scale * 0.1
        # first ellipse
        sh1 = ShapeEllipseArc(center=(0.0, 0.0), box_size=(88.8, 57.2), start_angle=98.3, end_angle=377)
        sh1 = Rotation((0.0, 0.0), 312)(sh1)
        sh1.move((12.5, 60))
        sh2 = ShapeEllipseArc(center=(0.0, 0.0), box_size=(93.83, 61.840), start_angle=95.4, end_angle=378.2)
        sh2=Rotation((0.0, 0.0), 312)(sh2)
        sh2.move((11, 60))
        sh1.reverse()
        sh1 += (30.3, 83.0)
        sh1 += sh2
        sh1 += sh1[0]
        elems += Boundary(self.layer, Magnification((0.0, 0.0), scale)(sh1))
        
        # second ellipse
        sh1 = ShapeEllipseArc(center=(0.0, 0.0), box_size=(73.2, 34.7), start_angle=138.5, end_angle=354.0)
        sh1.move((11.45, 35.8))
        sh2 = ShapeEllipseArc(center=(0.0, 0.0), box_size=(78.2, 36.7), start_angle=133, end_angle=352.8)
        sh2.move((9.6, 35.23))
        sh2.reverse()
        sh1 += sh2
        sh1 += sh1[0]
        elems += Boundary(self.layer, Magnification((0.0, 0.0), scale)(sh1))
        

        # third ellipse
        sh1 = ShapeEllipseArc(center=(0.0, 0.0), box_size=(42.8, 32.2), start_angle=96.0, end_angle=367.6)
        sh1= Rotation((0.0, 0.0), 47)(sh1)
        sh1.move((29.44, 22.71))
        sh2 = ShapeEllipseArc(center=(0.0, 0.0), box_size=(46.7, 35.1), start_angle=94, end_angle=370.5)
        sh2=Rotation((0.0, 0.0), 47.5)(sh2)
        sh2.move((29.5, 21.75))
        sh2.reverse()
        sh2 += (15.84, 32.35)
        sh1 += (42.30, 40.4)
        sh1 += sh2
        sh1 += sh1[0]
        elems += Boundary(self.layer, Magnification((0.0, 0.0), scale)(sh1))

        elems += PolygonText(self.layer,'IMEC', (5 * scale, scale* 64.0), (TEXT_ALIGN_LEFT, TEXT_ALIGN_MIDDLE), 1,  scale * 20.0)
        
        return elems
    
    

