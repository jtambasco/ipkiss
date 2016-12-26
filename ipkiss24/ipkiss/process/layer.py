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
from ipcore.properties.predefined import StringProperty, IdStringProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.initializer import StrongPropertyInitializer, MetaPropertyInitializer
from ipcore.all import do_hash

DEFINED_PROCESS_LAYERS = {}
DEFINED_PATTERN_PURPOSES = {}
__all__ = ["ProcessLayer", 
           "ProcessProperty", 
           "ProcessLayerList",
           "PatternPurpose",
           "PurposeProperty",
           "PPLayer",
           "ProcessPurposeLayer"]

###############################################################################################################
# Process Layer
###############################################################################################################

class MetaProcessLayerCreator(MetaPropertyInitializer):
    """ Metaclass which creates unique process layers """
    # Called when a new object is created
    def __call__(cls, *params, **keyword_params):
        # extract layer number
        if 'extension' in keyword_params:
            extension = keyword_params['extension']
        elif len(params) >= 1:
            extension = params[1]
        else:
            extension = "XX"
            raise AttributeError("Extension for a process layer should not be empty. Reset to XX")
        
        # extract the name of the new structure based on the arguments of
        # the constructor. For default structures, the name is passed as the first argument
        
        L = type.__call__(cls, *params, **keyword_params)
        exist = DEFINED_PROCESS_LAYERS.get(extension, None)
        if exist:
            return exist
        else:
            DEFINED_PROCESS_LAYERS[extension] = L
            return L

class ProcessLayer(StrongPropertyInitializer):
    """ Process layer represents a specific process step which requires a defined mask pattern. 
        Typically this is a lithography step in.
        """
    __metaclass__ = MetaProcessLayerCreator
    name = StringProperty(required = True)
    extension = IdStringProperty(required = True)
    def __init__(self, name, extension, **kwargs):
        super(ProcessLayer, self).__init__(name = name, extension = extension, **kwargs)
        
    def __eq__(self, other):
        if not isinstance(other, ProcessLayer): return False
        return self.extension == other.extension
            
    def __ne__(self, other):
        return (not self.__eq__(other))    

    def __repr__(self):
        return "<Process %s>"% self.extension
    
    
def ProcessProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RestrictType(ProcessLayer) & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)

###############################################################################################################
# PatternPurpose
###############################################################################################################

class MetaPatternPurposeCreator(MetaPropertyInitializer):
    """ Metaclass which creates unique pattern purposes """
    # Called when a new object is created
    def __call__(cls, *params, **keyword_params):
        # extract layer number
        if 'extension' in keyword_params:
            extension = keyword_params['extension']
        elif len(params) >= 1:
            extension = params[1]
        else:
            extension = "XX"
            raise AttributeError("Extension for a pattern purpose should not be empty. Reset to XX")
        
        # extract the name of the new structure based on the arguments of
        # the constructor. For default structures, the name is passed as the first argument
        
        L = type.__call__(cls, *params, **keyword_params)
        exist = DEFINED_PATTERN_PURPOSES.get(extension, None)
        if exist:
            return exist
        else:
            DEFINED_PATTERN_PURPOSES[extension] = L
            return L


class PatternPurpose(StrongPropertyInitializer):
    """ Pattern Purpose represents what should be done with the geometric patterns which is defined.
        e.g. etch, inversion, comment, ...
        """
    __metaclass__ = MetaPatternPurposeCreator
    name = StringProperty(required = True)
    extension = IdStringProperty(required = True)
    doc = StringProperty(default="")
    
    def __init__(self, name, extension, **kwargs):
        super(PatternPurpose, self).__init__(name = name, extension = extension, **kwargs)
        
    def __eq__(self, other):
        if not isinstance(other, PatternPurpose): return False
        return self.extension == other.extension
            
    def __ne__(self, other):
        return (not self.__eq__(other))    

    def __repr__(self):
        return "<Purpose %s>"% self.extension
    
    
def PurposeProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RestrictType(PatternPurpose) & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


###############################################################################################################
# ProcessPurposeLayer, or PPLayer
###############################################################################################################

from ipkiss.primitives.layer import Layer

class ProcessPurposeLayer(Layer):
    """ An Ipkiss layer which consists of a processlayer and a patternpurpose
    """
    process = ProcessProperty(required = True)
    purpose = PurposeProperty(required = True)
    def __init__(self, process, purpose, **kwargs):
        super(ProcessPurposeLayer, self).__init__(process = process, 
                                                  purpose = purpose, **kwargs)
    # add visualisation information for later use in SVG output or display

    def __str__(self):
        return "PPLAYER %s-%s" % (self.process.extension, self.purpose.extension)
    
    def __repr__(self):
        return "<PPLayer %s-%s>" % (self.process.extension, self.purpose.extension)
    
    def __eq__(self, other):
        if isinstance(other, ProcessPurposeLayer):
            return other.id() == self.id()
        elif isinstance(other, int):
            # this should be changed when new layer properties come in...
            return self.id() == other
        else:
            return False
    
    def __ne__(self, other):
        if isinstance(other, ProcessPurposeLayer):
            return other.id() != self.id()
        elif isinstance(other, int):
            return self.id() != other
        else:
            return True
    
    def id(self):
        # can become more complex when datatype etc. is included
        return do_hash("%s-%s" % (self.process.extension, self.purpose.extension))

PPLayer = ProcessPurposeLayer

###############################################################################################################
# ProcessLayerList
###############################################################################################################

class ProcessLayerList(list):
    __item_type__ = ProcessLayer
    

    def __getitem__(self, key):
        """ get ProcessLayerList item based on process layer extension """
        if isinstance(key, str):
            for i in self:
                if i.extension == key: return i
            raise IndexError("layer " + str(key) + " cannot be found in ProcessLayerList.")
        else:
            raise TypeError("Index is wrong type " + str(type(key)) + " in ProcessLayerList")
    
    def __setitem__(self, key, value):
        """ set ProcessLayerList item based on process layer extension """
        if isinstance(key, str):
            for i in range(0, len(self)):
                if self[i].extension == key: return list.__setitem__(self, i, value)
            list.append(self, value)
        else:
            raise TypeError("Index is wrong type " + str(type(key)) + " in ProcessLayerList")

    def __delitem__(self, key):
        if isinstance(key, str):
            for i in range(0, len(self)):
                if list.__getitem__(self,i).extension == key: return list.__delitem__(self,i)
                return
            return list.__delitem__(self,key)
        else:
            raise TypeError("Index is wrong type " + str(type(key)) + " in ProcessLayerList")

    def __contains__(self, item):
        if isinstance(item, ProcessLayer):
            id = item.extension
        elif isinstance(item, str):
            id = item
        
        for i in self:
            if i.extension == id: return True
        return False


    def __fast_get_layer__(self, extension):
        for L in self:
            if L.extension == extension: return L
        return None

    def index(self, item):
        if isinstance(item, str):
            for i in range(0, len(self)):
                if list.__getitem__(self, i).extension == item:
                    return i
            raise ValueError("layer " + item + " is not in ProcessLayerList")
        else:
            raise ValueError("layer " + item + " is not in ProcessLayerList")

    def add(self, item, overwrite = False):
        if isinstance(item, ProcessLayer):
            if not item in self:
                list.append(self,item)
            elif overwrite:
                self[item.extension] = item
                return
        elif isinstance(item, ProcessLayerList):
            for s in item:
                self.add(s, overwrite)
        else:
            self.__raise_invalid_type_exception__(item)

    def append(self, other, overwrite = False):
        return self.add(other, overwrite)

    def extend(self, other, overwrite = False):
        return self.add(other, overwrite)

 