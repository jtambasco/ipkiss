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

from ipcore.properties.initializer import StrongPropertyInitializer
from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.predefined import RESTRICT_FRACTION, BoolProperty, NonNegativeNumberProperty
from .color import ColorProperty, Color, COLOR_BLACK
from .stipple import StippleProperty, STIPPLE_NONE

__all__ = ["ColorProperty",
           "DisplayStyle",
           "DisplayStyleSet", 
           "DisplayStyleProperty"]

class DisplayStyle(StrongPropertyInitializer):
    color = ColorProperty(default = COLOR_BLACK)
    edgecolor = ColorProperty(default = COLOR_BLACK)
    stipple = StippleProperty(default = STIPPLE_NONE)    
    alpha = RestrictedProperty(restriction = RESTRICT_FRACTION, default = 1.0)
    
    edgewidth = NonNegativeNumberProperty(default = 1.0)
    visible = BoolProperty(default = True)
    
    def __str__(self):
        return "DisplayStyle : color: %s - edgecolor: %s - stipple: %s - alpha: %f - edgewidth: %f - visible: %s" %(str(self.color),str(self.edgecolor),str(self.stipple), self.alpha,self.edgewidth,self.visible)

    def blend(self, other, fraction_first_color = 0.33):
        result_color_red = fraction_first_color * self.color.red + (1.0-fraction_first_color) * other.color.red 
        result_color_green = fraction_first_color * self.color.green + (1.0-fraction_first_color) * other.color.green 
        result_color_blue = fraction_first_color * self.color.blue + (1.0-fraction_first_color) * other.color.blue 
        result_color = Color(name="#%02X%02X%02X" %(result_color_red, result_color_green, result_color_blue),
                             red = result_color_red,
                             green = result_color_green,
                             blue = result_color_blue)
        result_ds = DisplayStyle(color = result_color,
                                 edgecolor = self.edgecolor,
                                 stipple = self.stipple,
                                 alpha = self.alpha)
        return result_ds
    
class DisplayStyleSet(list):
    pass

class ProcessorDisplayStyle(ProcessorTypeCast):
    def __init__(self):
        ProcessorTypeCast.__init__(self, DisplayStyle)
    
    def process(self, value, obj= None):
        if value is None:
            return DisplayStyle()
        else:
            return ProcessorTypeCast.process(self, value, obj)
       

def DisplayStyleProperty(internal_member_name = None, restriction = None, preprocess = None,**kwargs):
    if not "default" in kwargs:
        kwargs["default"] = None
    R = RestrictType(DisplayStyle) & restriction
    P = ProcessorDisplayStyle() + preprocess
    return RestrictedProperty(internal_member_name, restriction = R, preprocess = P, **kwargs)


