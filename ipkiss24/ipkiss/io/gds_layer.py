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
from ipcore.properties.predefined import IntProperty, RESTRICT_NONNEGATIVE, DictProperty
from ipcore.properties.descriptor import RestrictedProperty
from ipkiss.primitives.layer import LayerProperty
from ..primitives.layer import Layer
from ipcore.exceptions.exc import *
from ipkiss.exceptions.exc import IpkissException

GDSII_LAYER_CONVERSION_RADIX = 256

__all__ = ["GdsiiLayer","GdsiiLayerInputMap","GdsiiLayerOutputMap","AutoGdsiiLayerOutputMap","AutoGdsiiLayerInputMap"]

class GdsiiLayer(StrongPropertyInitializer):
    number = IntProperty(required = True, restriction = RESTRICT_NONNEGATIVE)
    datatype = IntProperty(default = 0, restriction = RESTRICT_NONNEGATIVE)
    
    def __init__(self, number, datatype = 0, **kwargs):
        super(GdsiiLayer, self).__init__(number = number,
                                         datatype = datatype,
                                         **kwargs)
    
    def __eq__(self, other):
        return self.number == other.number and self.datatype == other.datatype    
        
    def __ne__(self, other):
        return (not self.__eq__(other))   
    
    def __repr__(self):
        return "GdsiiLayer %i/%i" %(self.number, self.datatype)
    

class GdsiiLayerOutputMap(StrongPropertyInitializer):
    
    layer_map = RestrictedProperty(required = True)     # map with keys of type "Layer" and values of type "GdsiiLayer"

    def __init__(self, layer_map, **kwargs):
        super(GdsiiLayerOutputMap, self).__init__(layer_map = layer_map, **kwargs)
        # check if the input map doesn't contain any duplicates on the "source side" (duplicates may exist on the target size)
        ln = []
        for L in self.layer_map.keys():
            ln.append(str(L))
        if len(ln) != len(list(set(ln))):
            raise InvalidArgumentException("layer_map may not contain duplicate layers on the source-side.")             
    
    def __getitem__(self, layer):
        for key, value in self.layer_map.items():
            if (layer == key):
                return value
        raise IpkissException("GdsiiLayerOutputMap::No valid mapping found for layer %s" %layer)
    
    def get(self, key, default):
        return self[key]

    
class AutoGdsiiLayerOutputMap(StrongPropertyInitializer):   

    def __getitem__(self, key):
        return GdsiiLayer(number = key.number%GDSII_LAYER_CONVERSION_RADIX,
                           datatype = key.number/GDSII_LAYER_CONVERSION_RADIX)
    
    def get(self, key, default):
        return self[key]

__AutoGdsiiLayerOutputMap__ = AutoGdsiiLayerOutputMap #DEPRECATED - for backwards compatibility    
    
class AutoGdsiiLayerInputMap(StrongPropertyInitializer):
    
    def __make_layer_name__(self, L):
        name = "L%d_%d" % (L.number, L.datatype)
        return name
    
    def __getitem__(self,key):
        return Layer(name = self.__make_layer_name__(key),
                         number = key.number + GDSII_LAYER_CONVERSION_RADIX * key.datatype)
    
    def get(self, key, default):
        try:
            return self[key]
        except:
            return default
    
__AutoGdsiiLayerInputMap__ = AutoGdsiiLayerInputMap  # DEPRECATED - for backwards compatibility           
#---------------------------------------------------------------------------------


class GdsiiLayerInputMap(StrongPropertyInitializer):
    layer_map = RestrictedProperty(required = True)
    default = LayerProperty(allow_none = True)
    
    def __init__(self, layer_map, **kwargs):
        super(GdsiiLayerInputMap, self).__init__(layer_map = layer_map, **kwargs)
        # check if the input map doesn't contain any duplicates on the "source side" (duplicates may exist on the target size)
        ln = []
        for L in self.layer_map.keys():
            ln.append((L.number,L.datatype))
        if len(ln) != len(list(set(ln))):
            raise IpkissException("layer_map may not contain duplicate layer number on the source-side.")                                    

    def __getitem__(self,key):
        for L in self.layer_map.keys():
            if L.number == key.number and L.datatype == key.datatype:
                return self.layer_map[L]
        return self.default
    
    def get(self,key,default):
        return self[key]

def make_layer_input_map(layermap, default = None):
    lm = {}
    for k in layermap.keys():
        if isinstance(k,int):
            datatype = 0
            number = k
        elif isinstance(k,tuple):
            datatype = k[1]
            number = k[0]
        else:
            raise TypeError("Wrong input in make_GdsiiLayerInputMap")
        lm[GdsiiLayer(number=number,datatype=datatype)]=layermap[k]
    L = GdsiiLayerInputMap(layer_map = lm, default = default)
    return L
