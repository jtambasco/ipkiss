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

import string

from ipcore.properties.restrictions import __PropertyRestriction__
from ipcore.properties.predefined import StringProperty, PositiveNumberProperty, IntProperty, RESTRICT_NONNEGATIVE
from ipcore.properties.descriptor import RestrictedProperty

from .basic import __LayerElement__
from .group import Group
from ..fonts import TEXT_FONT_DEFAULT, TEXT_FONTS
from ... import constants
from ... import settings
from ..font import Font, FontProperty
from ...geometry.shape import Shape
from ...geometry import size_info
from ...geometry.coord import Coord2Property

from ipkiss.log import IPKISS_LOG as LOG

__all__ = ["PolygonText",
           "Label",
           "AlignmentProperty",
           "RESTRICT_ALIGNMENT"]


class RestrictAlignment(__PropertyRestriction__):
    """ restrict to a 2-tuple for text alignment """
    def validate(self, value, obj = None):
        if len(value) == 2:
            if not value[0] in constants.TEXT_ALIGNS_HORIZONTAL: return False
            if not value[1] in constants.TEXT_ALIGNS_VERTICAL: return False
            return True
        return False

    def __repr__(self):
        return  "Alignment restriction" 

RESTRICT_ALIGNMENT = RestrictAlignment()

def AlignmentProperty(internal_member_name= None, restriction = None,  **kwargs):
    R = RESTRICT_ALIGNMENT & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)

#----------------------------------------------------------------------------
# Text
#----------------------------------------------------------------------------
class __TextElement__(__LayerElement__):
    text = StringProperty(required = True)
    coordinate = Coord2Property(default = (0.0, 0.0))
    alignment = AlignmentProperty(default = (constants.TEXT_ALIGN_CENTER, constants.TEXT_ALIGN_TOP))
    height = PositiveNumberProperty(default = 20.0)
    font = FontProperty(default = TEXT_FONT_DEFAULT)
    
    def __init__(self, 
                 layer,  
                 text, 
                 coordinate = (0.0,0.0), 
                 alignment = (constants.TEXT_ALIGN_CENTER, constants.TEXT_ALIGN_TOP) , 
                 font = TEXT_FONT_DEFAULT, 
                 height = 20.0, 
                 transformation = None, 
                 **kwargs):
        super(__TextElement__, self).__init__(layer = layer, 
                                               text = text, 
                                               coordinate = coordinate, 
                                               alignment = alignment, 
                                               font = font, 
                                               height = height, 
                                               transformation = transformation, 
                                               **kwargs)
    def get_h_alignment(self):
        return self.alignment[0]
    h_alignment = property(get_h_alignment)

    def get_v_alignment(self):
        return self.alignment[1]
    v_alignment = property(get_v_alignment)

    def is_empty(self):
        return (len(string.strip(self.text)) == 0) or (self.height == 0)


#----------------------------------------------------------------------------
# Polygon Text
#----------------------------------------------------------------------------

class PolygonText(Group, __TextElement__):
    def __init__(self, 
                 layer,  
                 text, 
                 coordinate = (0.0,0.0), 
                 alignment = (constants.TEXT_ALIGN_CENTER, constants.TEXT_ALIGN_TOP) , 
                 font = TEXT_FONT_DEFAULT, 
                 height = 20.0, 
                 transformation = None, 
                 **kwargs):
            super(PolygonText,self).__init__(layer = layer,  
                                                    text = text, 
                                                    coordinate = coordinate, 
                                                    alignment = alignment, 
                                                    font = font, 
                                                    height = height, 
                                                    transformation = transformation,
                                                **kwargs)

    def define_elements(self, elems):
        F = self.font
        text = self.text.upper()

        #determine start position
        letter_height = self.height
        letter_spacing = letter_height * F.spacing
        line_width =  letter_height * F.line_width
        letter_width = letter_height * (F.letter_width() + F.spacing)
        text_width = letter_width * len(text) - letter_spacing

        if self.h_alignment == constants.TEXT_ALIGN_RIGHT:
            x0 = - text_width
        elif self.h_alignment == constants.TEXT_ALIGN_CENTER:
            x0 = - text_width/2.0
        else:
            x0 = 0.0

        if self.v_alignment == constants.TEXT_ALIGN_BOTTOM:
            y0 = 0.0
        elif self.v_alignment == constants.TEXT_ALIGN_MIDDLE:
            y0 = - letter_height/2.0
        else:
            y0 = -letter_height

        xpos = x0
        ypos = y0

        xpos += self.coordinate[0]
        ypos += self.coordinate[1]
        for c in text:
            elems += F.elements_character(self.layer, c, letter_height, (xpos, ypos), angle = 0.0)
            xpos += letter_width #* ca
        
        return elems

#----------------------------------------------------------------------------
# Label text
#----------------------------------------------------------------------------
class Label(__TextElement__):
    font = IntProperty(restriction = RESTRICT_NONNEGATIVE, required= True)
    def __init__(self,
                 layer ,  
                 text , 
                 coordinate = (0.0,0.0), 
                 alignment = (constants.TEXT_ALIGN_CENTER, constants.TEXT_ALIGN_TOP) , 
                 font = TEXT_FONT_DEFAULT, 
                 height = 20.0, 
                 transformation = None,
                 **kwargs):
            super(Label,self).__init__(
                                         layer = layer, 
                                         text = text, 
                                         coordinate = coordinate, 
                                         alignment = alignment, 
                                         font = font, 
                                         height = height, 
                                         transformation = transformation,
                                     **kwargs)

            
    def size_info(self):
        text_width = len(self.text) * self.height
        if self.h_alignment == constants.TEXT_ALIGN_RIGHT:
            L = self.coordinate[0] - text_width
        elif self.h_alignment == constants.TEXT_ALIGN_CENTER:
            L = self.coordinate[0] - text_width/2.0
        else:
            L = self.coordinate[0]
        R = L + text_width

        if self.v_alignment == constants.TEXT_ALIGN_BOTTOM:
            B = self.coordinate[1]
        elif self.v_alignment == constants.TEXT_ALIGN_MIDDLE:
            B = self.coordinate[1]- self.height/2.0
        else:
            B = self.coordinate[1] - self.height
        T = B + self.height
        return size_info.size_info_from_numpyarray((Shape([(L,B), (L,T), (R, B), (R,T)], True).transform(self.transformation)).points)

    def flat_copy(self, level = -1):
        return self.__copy__()

