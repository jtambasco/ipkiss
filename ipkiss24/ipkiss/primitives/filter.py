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
from ipcore.properties.predefined import StringProperty
from ipkiss.log import IPKISS_LOG as LOG


class Filter(StrongPropertyInitializer):
    """ base class that processes any IPKISS primitive (does type checking where needed).
        The call should ALWAYS return a list object with IPKISS primitives """
    name = StringProperty(allow_none=True)
    
    def __call__(self, item):
        if isinstance(item, list):
            L = []
            for v in item: 
                L += self.__call__(v)
            return L
        else:
            return self.filter(item)

    def filter(self, item):
        import inspect
        T = type(item)
        if inspect.isclass(T):
            for M in inspect.getmro(T):
                N = "__filter_%s__" % M.__name__
                if hasattr(self, N):
                    LOG.debug("Applying method %s of %s to %s" %(N,self,item))
                    return getattr(self, N)(item)
            return self.__filter_default__(item)
        else:
            N = "__filter_%s" % T.__name__
            if hasattr(self, N):
                expr = "self.%s(item)" % N
                LOG.debug("Executing %s" %expr)
                return eval(expr)
            else:
                return self.__filter_default__(item)
        
    def __filter_default__(self, item):
        return [item]
        
    def __add__(self, other):
        if isinstance(other, Filter):
            return __CompoundFilter__(filters = [self, other])
        elif other is None:
            return self
        else:
            raise TypeError("Cannot add %s to filter " % type(other))
    
    def __iadd__(self, other):
        C = self.__add__(other)
        self = C
        return self

    def __repr__(self):
        return "<GDS Primitive Filter>"
    
class __CompoundFilter__(Filter):
    """ compound property processor class """
    def __init__(self, filters = [], **kwargs):
        super(__CompoundFilter__,self).__init__(**kwargs)
        self._sub_filters = filters

    def __add__(self, other):
        if isinstance(other, __CompoundFilter__):
            return __CompoundFilter__(name = self.name, filters = self._sub_filters + other.__sub_filters)
        elif isinstance(other, Filter):
            return __CompoundFilter__(name = self.name, filters = self._sub_filters + [other])
        else:
            raise TypeError("Cannot add %s to Filter" % type(other))
    
    def __iadd__(self, other):
        self.add(other)
        return self
    
    def add(self, other):
        if isinstance(other, __CompoundFilter__):
            self._sub_filters += other._sub_filter
        elif isinstance(other, Filter):
            self._sub_filters += [other]
        else:
            raise TypeError("Cannot add %s to Filter" % type(other))
        
    def __call__(self, item):
        """ processes the item """ 
        LOG.debug("Applying all subfilters. Item = %s" % item)
        v = item
        for R in self._sub_filters:
            LOG.debug("** Applying subfilter %s to %s" % (R, v))
            v = R(v)
            LOG.debug("** Result after filtering = %s\n" % v)
        LOG.debug("Finished applying all subfilters. Item = %s" % item)        
        return v

    def __repr__(self):
        S = "< Compound Filter:"
        for i in self._sub_filters:
            S += "   %s" % i.__repr__() 
        S += ">"
        return S

class ToggledCompoundFilter(__CompoundFilter__):
    """ Compound filter in which filters can be turned on or off
        by doing filter['filter_name'] = True|False
        Only for named filters!
    """
    def __init__(self, filters = [], **kwargs):
        super(ToggledCompoundFilter,self).__init__(filters = filters,**kwargs)
        self.__filter_status = dict()
        
    def __setitem__(self, key, item):
        """ dict behaviour: enable or disable a filter based on it's name """
        if not isinstance(key,str):
            raise KeyError("__ToggledCompoundFilter__: key must be of type str, is type %s"%(type(key)))
        if not isinstance(item, bool):
            raise KeyError("__ToggledCompoundFilter__: item must be of type bool, is type %s"%(type(item)))
        self.__filter_status[key]=item
    
    def __getitem__(self,key):
        if not isinstance(key,str):
            raise KeyError("__ToggledCompoundFilter__: key must be of type str, is type %s"%(type(key)))
        if not key in self.__filter_status.keys():
            return True
        return self.__filter_status[key]
    
    def __call__(self, item):
        """ processes the item """ 
        LOG.debug("Applying all subfilters. Item = %s" % item)
        v = item
        k = self.__filter_status.keys()
        for R in self._sub_filters:
            if R.name not in k or self.__filter_status[R.name]:
                LOG.debug("** Applying subfilter %s to %s"  % (R, v))
                v = R(v)
                LOG.debug("** Result after filtering = %s\n" % v)
        LOG.debug("Finished applying all subfilters. Item = %s" % item)        
        return v
    
    def __repr__(self):
        S = "< Toggled Compound Filter:"
        for i in self._sub_filters:
            S += "   %s" % i.__repr__() 
            if i.name not in self.__filter_status.keys() or self.__filter_status[i.name]:
                S += "(enabled)"
            else:
                S += "(disabled)"
        S += ">"
        return S
