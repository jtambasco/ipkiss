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

#from ..geometry.shape import 
from ..geometry.transforms.no_distort import NoDistortTransform
from .elements.shape import Boundary, Path
from .elements.basic import ElementList
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.initializer import StrongPropertyInitializer
from ipcore.properties.predefined import PositiveNumberProperty, NonNegativeNumberProperty
from ..geometry.coord import Size2Property
from ipkiss.log import IPKISS_LOG as LOG

__all__ = ["BoundaryFont", "PathFont"]

class Font(StrongPropertyInitializer):
    coords = RestrictedProperty(restriction = RestrictType(dict), default = {})
    line_width = PositiveNumberProperty(default = 0.1)
    default_char = RestrictedProperty(restriction = RestrictType(list), default = [[]])
    cell_size = Size2Property(default = (0.6, 1.0))
    spacing = NonNegativeNumberProperty(default = 0.2)
    def __init__(self, **kwargs):
        super(Font, self).__init__(
            **kwargs)

    def shapes_character (self, character, letter_height = 1.0, south_west_coord = (0.0,0.0), angle = 0.0):
        #returns a list of shapes!!!
        if character in self.coords:
            shapes = self.coords[character]
        else:
            shapes = [self.default_char]
        ret_shapes = []
        #T = Rotation((0.0,0.0), angle) + Magnification((0.0,0,0), letter_height) + Translation(south_west_coord)
        T = NoDistortTransform(south_west_coord, angle, letter_height/self.letter_height())
        for s in shapes:
            if len(s) < 2:
                LOG.warning("Shape with too few coordinates in letter " % character)
            #ret_shapes.append(shape_translate(shape_scale(shape_rotate(s, (0.0,0.0), angle), (letter_height, letter_height)), south_west_coord))		
            ret_shapes.append(T.apply_to_copy(s))
        return ret_shapes

    def letter_width(self):
        return self.cell_size[0]
    
    def letter_height(self):
        return self.cell_size[1]
       
class BoundaryFont(Font):
    def elements_character(self, layer, character, letter_height = 1.0, south_west_coord = (0.0,0.0), angle = 0.0):
        EL = ElementList()
        for s in self.shapes_character(character, letter_height , south_west_coord , angle):
            EL += Boundary(layer, s)
        return EL
    
    def shapes_character (self, character, letter_height = 1.0, south_west_coord = (0.0,0.0), angle = 0.0):
        S = Font.shapes_character(self, character, letter_height , south_west_coord , angle)
        for s in S:
            s.close()
        return S
    
class PathFont(Font):

    def letter_width(self):
        return self.cell_size[0] + self.line_width

    def letter_height(self):
        return self.cell_size[1] + self.line_width

    def elements_character(self, layer, character, letter_height = 1.0, south_west_coord = (0.0,0.0), angle = 0.0):
        EL = ElementList()
        lw = self.line_width * letter_height * self.letter_height()
        for s in self.shapes_character(character, letter_height , south_west_coord , angle):
            EL += Path(layer, s, lw)
        return EL
    
class ProcessorFont(ProcessorTypeCast):
    """ restrict the type or types the argument can have, and tries a typecast where possible """
    def __init__(self):
        pass
    
    def process(self, value, obj = None):
        if isinstance(value, Font):
            return value
        try:
            import fonts
            new_val = fonts.TEXT_FONTS[value]
            return new_val
        except:
            raise ValueError("Invalid font: %s" % value)            
        
    def __repr__(self):
        S = "<Font Processor>" 

def FontProperty(internal_member_name= None, restriction = None,  preprocess = None, **kwargs):
    R = RestrictType(Font) & restriction
    P = ProcessorFont() + preprocess
    return RestrictedProperty(internal_member_name, restriction = R, preprocess = P, **kwargs)
