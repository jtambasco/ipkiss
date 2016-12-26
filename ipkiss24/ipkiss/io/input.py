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

from ..primitives.library import Library
from ..primitives.layer import Layer, __Layer__
from ipcore.properties.initializer import StrongPropertyInitializer
from ipcore.properties.descriptor import DefinitionProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.predefined import PositiveNumberProperty, StringProperty
from ipkiss.technology import get_technology
import sys

TECH = get_technology()

__all__ = []

#######################################################################
## Basic input module
#######################################################################
class BasicInput(StrongPropertyInitializer):
    i_stream = DefinitionProperty(default = sys.stdin) # add limitation
    def __init__(self, i_stream = sys.stdin, **kwargs):
        super(BasicInput, self).__init__(
            i_stream = i_stream,
            **kwargs)

    def read(self, size = None):
        if size is None:
            return self.parse(self.i_stream.read())
        else:
            return self.parse(self.i_stream.read(size))

    def parse(self, item):
        return item

#######################################################################
## Basic GDS input stream
#######################################################################
class InputBasic(BasicInput):
    scaling = PositiveNumberProperty(default = 1.0)
    layer_map = DefinitionProperty()
    prefix = StringProperty(default = "")
    
    def __init__(self, i_stream = sys.stdin, **kwargs):
        super(InputBasic, self).__init__(
            i_stream = i_stream,
            **kwargs)
        self.library = None

    def read(self):
        return self.parse()        

    def parse(self):
        return self.parse_library()

    def parse_library(self):
        self.library = Library("IMPORT")
        self.__parse_library__()
        return self.library

    def map_layer(self, layer):
        L = self.layer_map.get(layer, None)
        if isinstance(L, __Layer__):
            return L
        elif L is None:
            return L
        else:
            return Layer(L)

    def make_structure_name(self, name):
        return self.prefix + name
    
    def define_layer_map(self):
        return TECH.GDSII.IMPORT_LAYER_MAP #FIXME : using 'default' for the property would be better, but that gives an exception ...

#################################################
## __Element__ Types
#################################################
Type_Boundary = 1
Type_Path = 2
Type_SRef = 3
Type_ARef = 4
Type_Label = 5
Type_Box = 6