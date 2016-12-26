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

from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.predefined import StringProperty, NumberProperty, RESTRICT_FRACTION
from ipcore.properties.initializer import StrongPropertyInitializer

__all__ = ["Color",
           "ColorProperty",
           "COLOR_BLACK",
           "COLOR_BLUE",
           "COLOR_CYAN",
           "COLOR_GREEN",
           "COLOR_MAGENTA",
           "COLOR_RED",
           "COLOR_WHITE",
           "COLOR_YELLOW",
           "COLOR_DARK_GREEN",
           "COLOR_ORANGE",
           "COLOR_PURPLE",
           "COLOR_DEEP_GREEN",
           "COLOR_GHOSTWHITE",
           "COLOR_CHERRY",
           "COLOR_CHAMPAGNE",
           "COLOR_BLUE_VIOLET",
           "COLOR_BLUE_CRAYOLA",
           "COLOR_SCARLET",
           "COLOR_SANGRIA",
           "COLOR_SILVER",
           "COLOR_TITANIUM_YELLOW",
           "COLOR_GRAY",
           "COLOR_COPPER",
           "COLOR_DARKSEA_GREEN"]

# color names: http://en.wikipedia.org/wiki/List_of_colors

class Color(StrongPropertyInitializer):
    """Defines a color in terms of a name and RGB values"""
    name = StringProperty()
    red = NumberProperty(default = 0.0, restriction = RESTRICT_FRACTION)
    green = NumberProperty(default = 0.0, restriction = RESTRICT_FRACTION)
    blue = NumberProperty(default = 0.0, restriction = RESTRICT_FRACTION)
    
    def __init__(self, red=0.0, green=0.0, blue= 0.0, **kwargs):
        super(Color, self).__init__(red= red,
                                    green = green,
                                    blue = blue,
                                    **kwargs)
    
    def rgb_tuple(self):
        return (self.red, self.green, self.blue)
    
    def numpy_array(self):
        import numpy
        return numpy.array([self.red, self.green, self.blue])
    
    def set(self, red, green, blue):
        self.red = red
        self. green = green
        self.blue = blue
        
    def html_string(self):
        return "#%02X%02X%02X" % (self.red*255, self.green * 255, self.blue * 255)

    def __eq__(self, other):
        return other.red == self.red and other.green == self.green and other.blue == self.blue

    def __neq__(self, other):
        return other.red != self.red or other.green != self.green or other.blue != self.blue
    
    def __str__(self):
        return self.name
    
    

class ProcessorColor(ProcessorTypeCast):
    def __init__(self):
        ProcessorTypeCast.__init__(self, Color)
    
    def process(self, value, obj= None):
        # TODO: add more conversions
        return ProcessorTypeCast.process(self, value, obj)
    
    
def ColorProperty(internal_member_name = None, restriction = None, preprocess = None,**kwargs):
    R = RestrictType(Color) & restriction
    P = ProcessorColor() + preprocess
    return RestrictedProperty(internal_member_name,  restriction = R, preprocess = P, **kwargs)


COLOR_BLACK = Color(name = "black", red = 0, green = 0, blue = 0)
COLOR_WHITE = Color(name = "white", red = 1, green = 1, blue = 1)
COLOR_GHOSTWHITE = Color(name = "ghost white", red = 0.97, green = 0.97, blue = 1)
COLOR_RED = Color(name = "red", red = 1, green = 0, blue = 0)
COLOR_GREEN = Color(name = "green", red = 0, green = 1, blue = 0)
COLOR_BLUE = Color(name = "blue", red = 0, green = 0, blue = 1)
COLOR_CYAN = Color(name = "cyan", red = 0, green = 1, blue = 1)
COLOR_YELLOW = Color(name = "yellow", red = 1, green = 1, blue = 0)
COLOR_MAGENTA = Color(name = "magenta", red = 1, green = 0, blue = 1)
COLOR_DARK_GREEN = Color(name = "dark green", red = 0.5, green = 0.31, blue = 0)
COLOR_DEEP_GREEN = Color(name = "deep green", red = 0, green = 0.5, blue = 0.5)
COLOR_ORANGE = Color(name = "ORANGE", red = 1, green = 0.62, blue = 0.62)
COLOR_PURPLE = Color(name = "PURPLE", red = 0.75, green = 0.5, blue = 1)
COLOR_CHERRY = Color(name = "CHERRY", red = 0.87, green = 0.19, blue = 0.39)
COLOR_CHAMPAGNE = Color(name = "CHAMPAGNE", red = 0.98, green = 0.84, blue = 0.65)
COLOR_BLUE_VIOLET = Color(name = "BLUE-VIOLET", red = 0.44, green = 0.0, blue = 1.0)
COLOR_BLUE_CRAYOLA = Color(name = "BLUE (CRAYOLA)", red = 0.12, green = 0.46, blue = 1.0)
COLOR_SCARLET = Color(name = "SCARLET", red = 1.0, green = 0.14, blue = 0.0)
COLOR_SANGRIA = Color(name = "SANGRIA", red=0.57, green = 0.0, blue = 0.04)
COLOR_SILVER = Color(name = "SILVER", red=0.75, green = 0.75, blue = 0.75)
COLOR_TITANIUM_YELLOW = Color(name = "TITANIUM_YELLOW", red=0.93, green = 0.90, blue = 0.0)
COLOR_GRAY = Color(name="GRAY", red=0.55, green=0.52, blue = 0.55)
COLOR_COPPER = Color(name="COPPER", red=0.72, green = 0.45, blue = 0.20)
COLOR_DARKSEA_GREEN = Color(name="DARKSEA_GREEN", red=0.56, green=0.74, blue=0.56)