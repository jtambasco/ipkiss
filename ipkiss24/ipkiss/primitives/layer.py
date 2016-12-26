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
from ipcore.properties.processors import ProcessorTypeCast
from ipcore.properties.predefined import NumberProperty, IntProperty, StringProperty
from ipcore.properties.initializer import StrongPropertyInitializer, MetaPropertyInitializer
from ipcore.helperfunc import do_hash
from ipcore.types_list import TypedList

__all__=["Layer", "LayerList", "LayerProperty"]

class MetaLayerCreator(MetaPropertyInitializer):
    # Called when a new object is created
    def __call__(cls, *params, **keyword_params):
        
        # check is there is a layerlist passed.
        # otherwise, use current layerlist

        import inspect
        from .. import settings
        p, a, k, d = inspect.getargspec(cls.__init__)
        if d is None:
            d = []
        kwargs = {}
        for k, v in zip(p[-len(d):], d):
            kwargs[k] = v
        kwargs.update(keyword_params)
        for k, v in zip(p[1:len(params)+1], params):
            kwargs[k] = v
        

        if 'layerlist' in kwargs:
            layerlist = kwargs['layerlist']
            del(kwargs['layerlist'])
        else:
            layerlist = None
            
        if layerlist is None:
            layerlist = settings.get_current_layerlist()

        L = type.__call__(cls, **kwargs)
        id = L.id()
        layer = layerlist.__fast_get_layer__(id)
        if layer is None:
            list.append(layerlist, L)
            return L
        else:
            return layer

class __Layer__(StrongPropertyInitializer):
    __metaclass__ = MetaLayerCreator

    def __and__(self, other):
        if isinstance(other, __Layer__):
            return __GeneratedLayerAnd__(self, other)
        elif other is None:
            return self
        else:
            raise TypeError("Cannot AND %s with %s" % (type(self),type(other)))

    def __iand__(self, other):
        C = self.__and__(other)
        self = C
        return self

    def __or__(self, other):
        if isinstance(other, __Layer__):
            return __GeneratedLayerOr__(self, other)
        elif other is None:
            return self
        else:
            raise TypeError("Cannot OR %s with %s" % (type(self),type(other)))

    def __ior__(self, other):
        C = self.__and__(other)
        self = C
        return self

    def __xor__(self, other):
        if isinstance(other, __Layer__):
            return __GeneratedLayerXor__(self, other)
        elif other is None:
            return self
        else:
            raise TypeError("Cannot XOR %s with %s" % (type(self),type(other)))

    def __ixor__(self, other):
        C = self.__xor__(other)
        self = C
        return self

    def __invert__(self):
        return __GeneratedLayerNot__(self)

class __GeneratedLayer__(__Layer__):
    name = StringProperty(allow_none = True)
    
    def get_layers(self, lobject):
        if isinstance(lobject, __GeneratedLayer__):
            return lobject.layers()
        else:
            return lobject
        
    def __str__(self):
        if self.name!=None:
            return self.name
        else:
            return self.__repr__()

class __GeneratedLayer_2Layer__(__GeneratedLayer__):
    def __init__(self, layer1, layer2):
        super(__GeneratedLayer_2Layer__,self).__init__()
        self.layer1 = layer1
        self.layer2 = layer2      
  
    def layers(self):
        l = LayerList()
        l += self.get_layers(self.layer1)
        l += self.get_layers(self.layer2)
        return l 

class __GeneratedLayerAnd__(__GeneratedLayer_2Layer__):    
    def __repr__(self):
        return "(%s AND %s)" % (self.layer1, self.layer2)
    
    def id(self):
        return "%s AND %s"%(self.layer1, self.layer2)
        
class __GeneratedLayerOr__(__GeneratedLayer_2Layer__):        
    def __repr__(self):
        return "(%s OR %s)" % (self.layer1, self.layer2)
    
    def id(self):
        return "%s OR %s"%(self.layer1, self.layer2)

class __GeneratedLayerXor__(__GeneratedLayer_2Layer__):        
    def __repr__(self):
        return "(%s XOR %s)" % (self.layer1, self.layer2)
    
    def id(self):
        return "%s XOR %s"%(self.layer1, self.layer2)
        
class __GeneratedLayerNot__(__GeneratedLayer__):
    def __init__(self, layer1):
        super(__GeneratedLayerNot__,self).__init__()
        self.layer1 = layer1
        
    def __repr__(self):
        return "(NOT %s)" % (self.layer1)
    
    def id(self):
        return "NOT %s"%(self.layer1)
    
    def layers(self):
        l = LayerList()
        l += self.get_layers(self.layer1)
        return l 

class Layer(__Layer__):
    number = IntProperty(required = True)
    name = StringProperty(required = True)
    
    def __init__(self, number = 0, name=None, layerlist = None, **kwargs):
        if name is None:
            name = "layer" + str(number)
        super(Layer, self).__init__(number = number, name = name, **kwargs)

    def __str__(self):
        return "LAYER" + str(self.number)
    
    def __repr__(self):
        return "<Layer %d>" %self.number
    
    def __eq__(self, other):
        if isinstance(other, Layer):
            return other.id() == self.id()
        elif isinstance(other, int):
            # this should be changed when new layer properties come in...
            return self.id() == other
        else:
            return False
    
    def __ne__(self, other):
        if isinstance(other, Layer):
            return other.id() != self.id()
        elif isinstance(other, int):
            return self.id() != other
        else:
            return True
    
    def id(self):
        # can become more complex when datatype etc. is included
        return self.number

def LayerProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RestrictType(__Layer__) & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)

class LayerList(TypedList):
    __item_type__ = __Layer__
    
    # overload acces routines to get dictionary behaviour but without
    # using the name as primary key
    def __getitem__(self, key):
        if isinstance(key, int):
            for i in self:
                if i.id() == key: return i
            raise IndexError("layer " + str(key) + " cannot be found in LayerList.")
        elif isinstance(key, str):
            for i in self:
                if i.name == key: return i
            raise IndexError("layer " + str(key) + " cannot be found in LayerList.")
        else:
            raise TypeError("Index is wrong type " + str(type(key)) + " in LayerList")
    
    def __setitem__(self, key, value):
        if isinstance(key, int):
            for i in range(0, len(self)):
                if self[i].id() == key: return list.__setitem__(self, i, value)
            list.append(self, value)
        elif isinstance(key, str):
            for i in range(0, len(self)):
                if self[i].name == key: return list.__setitem__(self, i, value)
            list.append(self, value)
        else:
            raise TypeError("Index is wrong type " + str(type(key)) + " in LayerList")

    def __delitem__(self, key):
        if isinstance(key, int):
            for i in range(0, len(self)):
                if list.__getitem__(self,i).id() == key: return list.__delitem__(self,i)
                return
            return list.__delitem__(self,key)
        if isinstance(key, str):
            for i in range(0, len(self)):
                if list.__getitem__(self,i).name == key: return list.__delitem__(self,i)
                return
            return list.__delitem__(self,key)
        else:
            raise TypeError("Index is wrong type " + str(type(key)) + " in LayerList")

    def __contains__(self, item):
        if isinstance(item, Layer):
            id = item.id()
        elif isinstance(item, int):
            id = item
        elif isinstance(item, str):
            for i in self:
                if i.name == name: return True
            return False

        if isinstance(id, int):
            for i in self:
                if i.id() == id: return True
            return False

    def __fast_get_layer__(self, id):
        for L in self:
            if L.id() == id: return L
        return None

    def index(self, item):
        if isinstance(item, Layer):
            id = item.id()
        elif isinstance(item, int):
            id = item

        if isinstance(id, int):
            for i in range(0, len(self)):
                if list.__getitem__(self, i).id() == id:
                    return i
            raise ValueError("layer " + id + " is not in LayerList")
        if isinstance(item, str):
            for i in range(0, len(self)):
                if list.__getitem__(self, i).name == item:
                    return i
            raise ValueError("layer " + item + " is not in LayerList")
        else:
            raise ValueError("layer " + item + " is not in LayerList")

    def add(self, item, overwrite = False):
        if isinstance(item, Layer):
            if not item in self:
                list.append(self,item)
            elif overwrite:
                self[item.id()] = item
                return
        elif isinstance(item, LayerList) or isinstance(item, list):
            for s in item:
                self.add(s, overwrite)
        elif isinstance(item, int):
            if overwrite or (not item in self):
                self.add(Layer(item), overwrite)
        else:
            self.__raise_invalid_type_exception__(item)

    def append(self, other, overwrite = False):
        return self.add(other, overwrite)

    def extend(self, other, overwrite = False):
        return self.add(other, overwrite)

    def clear(self):
        del self[:]
        
    def __eq__(self, other):
        return set(self) == set(other)

    def __hash__(self):
        return do_hash(self)
        
LAYER_LIST = LayerList()