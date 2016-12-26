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

from ipkiss.technology import get_technology
from ipkiss.primitives.layer import Layer, LayerProperty, LayerList,__GeneratedLayer__
from ipcore.all import StrongPropertyInitializer, StringProperty, PositiveNumberProperty,MixinBowl, RestrictedProperty, RestrictType, ListProperty
from ipcore.properties.predefined import RESTRICT_NUMBER, RESTRICT_POSITIVE

TECH = get_technology()

class __DesignRule__(StrongPropertyInitializer,MixinBowl):
    """ Design rule base class """
    doc = StringProperty(default="", doc="Documentation of design rule")
    name = StringProperty(default="")
    def __str__(self):
        return ""

def DesignRuleProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RestrictType(__DesignRule__) & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)

class __LayerDesignRule__(__DesignRule__):
    """ Layer rule applying to one layer """
    layer = LayerProperty(required=True, doc="Layer the rule applies to")
    def __str__(self):
        return "Layer rule %s"%(self.layer)

    def get_layers(self):
        l = LayerList()
        if isinstance(self.layer,__GeneratedLayer__):
            l += self.layer.layers()
        else:
            l += self.layer
        return l
    
        
class __TwoLayerDesignRule__(__DesignRule__):
    """ Layer rule applying to two layers """
    layer1 = LayerProperty(required=True, doc="First layer the rule applies to")
    layer2 = LayerProperty(required=True, doc="Second layer the rule applies to")
    def get_layers(self):
        l = LayerList()
        if isinstance(self.layer1,__GeneratedLayer__):
            l += self.layer1.layers()
        else:
            l += self.layer1
        if isinstance(self.layer2,__GeneratedLayer__):
            l += self.layer2.layers()
        else:
            l += self.layer2
        return l
    
    def __str__(self):
        return "Two layer rule %s %s"%(self.layer1,self.layer2)

class MinimumSpaceDesignRule(__LayerDesignRule__):
    """ Minimum allowed space between two edges or vertices in a single layer """
    minimum_space = PositiveNumberProperty(required=True)
    def __str__(self):
        return "Minimum space %.3f on layer %s"%(self.minimum_space,self.layer)

class MaximumSpaceDesignRule(__LayerDesignRule__):
    """ Maximum allowed space between two edges or vertices in a single layer """
    maximum_space = PositiveNumberProperty(required=True)
    
    def __str__(self):
        return "Maximum space %.3f on layer %s"%(self.maximum_space,self.layer)

class MinimumWidthDesignRule(__LayerDesignRule__):
    """ Minimum allowed width between two edges or vertices in a single layer """
    minimum_width = PositiveNumberProperty(required=True)
    
    def __str__(self):
        return "Minimum width %.3f on layer %s"%(self.minimum_width,self.layer)

class MinimumDiameterDesignRule(__LayerDesignRule__):
    """ Minimum allowed width between two edges or vertices in a single layer """
    minimum_diameter = PositiveNumberProperty(required=True)
    
    def __str__(self):
        return "Minimum diameter %.3f on layer %s"%(self.minimum_diameter,self.layer)

class MaximumWidthDesignRule(__LayerDesignRule__):
    """ Maximum allowed width between two edges or vertices in a single layer """
    maximum_width = PositiveNumberProperty(required=True)
    
    def __str__(self):
        return "Maximum width %.3f on layer %s"%(self.maximum_width,self.layer)

class AllowedWidthsDesignRule(__LayerDesignRule__):
    """ Allowed width between two edges or vertices in a single layer """
    allowed_widths = ListProperty(restriction = RESTRICT_NUMBER & RESTRICT_POSITIVE)
    
    def __str__(self):
        a = ["Width must be one of "]
        a.extend(["%.3f "%w for w in self.allowed_widths])
        a.append("on layer %s"%(self.layer))
        return "".join(a)

class AllowedDiameterDesignRule(__LayerDesignRule__):
    """ Allowed width between two edges or vertices in a single layer """
    allowed_diameters = ListProperty(restriction = RESTRICT_NUMBER & RESTRICT_POSITIVE)
    
    def __str__(self):
        a = ["Diameters must be one of "]
        a.extend(["%.3f "%w for w in self.allowed_diameters])
        a.append("on layer %s"%(self.layer))
        return "".join(a)
    
class NoOverlapDesignRule(__TwoLayerDesignRule__):
    def __str__(self):
        return "Layer %s not on layer %s"%(self.layer1,self.layer2)

class OverlapDesignRule(__TwoLayerDesignRule__):
    def __str__(self):
        return "Layer %s must be on layer %s"%(self.layer1,self.layer2)

class InsideDesignRule(__TwoLayerDesignRule__):
    def __str__(self):
        return "Layer %s must be fully covered by layer %s"%(self.layer1,self.layer2)
    
class MinimumEnclosureDesignRule(__TwoLayerDesignRule__):
    minimum_enclosure = PositiveNumberProperty(required=True)
    
    def __str__(self):
        return "Layer %s must be enclosed by layer %s by at least %.3f micron"%(self.layer1,self.layer2,self.minimum_enclosure)

class Rule(StrongPropertyInitializer):
    design_rule = DesignRuleProperty(required=True)
    error_layer = LayerProperty(required=True)
    
    
