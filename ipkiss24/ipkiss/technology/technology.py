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
from ipcore.properties.restrictions import RestrictType
from ipcore.exceptions.exc import *
from ipcore.config.tree import ConfigTree, DelayedInitConfigTree, FallbackConfigTree

class TechnologyTree(ConfigTree):
    """A hierarchical tree for storing technology settings."""
    pass
    
class DelayedInitTechnologyTree(DelayedInitConfigTree):
    """A hierarchical tree for storing technology settings, but with delayed initialisation : the initialize-function is called only at the moment a value is actually retrieved."""
    pass

class TechnologyLibrary(FallbackConfigTree):
    """A specific type of FallbackTechnologyTree: it's representation is: <TECH...>"""
    def __init__(self, name, description = None, fallback= None, **kwargs):
        super(TechnologyLibrary, self).__init__(fallback = fallback)
        self.name = name
        self.description = description
        
    def __repr__(self):
        return "<TECH %s>" % self.name
    
def TechnologyProperty(internal_member_name = None, restriction = None,  **kwargs):
    """A property for assigning a TechnologyLibrary"""
    R = RestrictType(TechnologyLibrary) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)

class TechAdminTree(DelayedInitTechnologyTree):
    def initialize(self):
        from ipkiss.primitives import name_generator
        self.NAME_GENERATOR = name_generator.CounterNameGenerator(prefix_attribute = "__name_prefix__",
                                             counter_zero = 0,
                                             default_prefix = "STRUCTURE"
                                             )
        

class ProcessTechnologyTree(DelayedInitTechnologyTree):
    
    def initialize(self):
        pass
    
    def get_process_layers(self):
        from ipkiss.process.layer import ProcessLayerList, ProcessLayer
        pl = ProcessLayerList()
        for k,v in self.__dict__.items():
            if isinstance(v, ProcessLayer):
                pl.append(v)
        return pl
    
    def get_key_from_process_layer(self, layer):
        from ipkiss.process.layer import ProcessLayer
        for k,v in self.__dict__.items():
            if isinstance(v,ProcessLayer) and v==layer:
                return k
        return None
                