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



class __NameGenerator__(object):
    """Abstract base class for name generators"""
    def reset(self):
        pass


class CounterNameGenerator(__NameGenerator__):
    """Generate a unique name based on a counter for every prefix"""
    def __init__(self, prefix_attribute = "__name_prefix__", default_prefix = "OBJ", counter_zero = 0):
        self.prefix_attribute = prefix_attribute
        self.counter_zero = counter_zero
        self.default_prefix = default_prefix
        self.names_counters = {}            
    
    def __call__(self, obj):
        if hasattr(obj, self.prefix_attribute):
            prefix = getattr(obj, self.prefix_attribute)
        else:
            prefix = self.default_prefix
        c = self.names_counters.get(prefix, self.counter_zero)
        c += 1
        c = self.names_counters[prefix] = c       
        return "%s_%d" % (prefix, c)
    
    def reset(self):
        self.prefix_attribute = "__name_prefix__"
        self.counter_zero = 0
        self.names_counters = {}                

# ---- DISABLED FOR NOW - niet sluitend - FIXME ----
#class PropertyNameGenerator(__NameGenerator__):
    #def __init__(self, prefix_attribute = "__name_prefix__", default_prefix = "OBJ"):
        #self.prefix_attribute = prefix_attribute
        #self.default_prefix = default_prefix
        #self.names_counters = {}

    #def __call__(self, obj):
        #if hasattr(obj, self.prefix_attribute):
            #prefix = getattr(obj, self.prefix_attribute)
        #else:
            #prefix = self.default_prefix

        #if hasattr(obj, '__name_properties__'):
            #props = obj.__name_properties__
        #else:
            #props = obj.__unlocked_properties__()
            #props.sort()

        #name_list = [prefix]
        #for n in props: 
            #p = getattr(obj, n)
            #if hasattr(p, 'id_string'):
                #name_list += ["%s%s_" % (string.upper(n[0]), p.id_string())]
            #else:
                #try:
                    #name_list += ["%s%d_" % (string.upper(n[0]), hash(p))]
                #except:
                    #name_list += ["%s%d_" % (string.upper(n[0]), hash(str(p)))]
                
        #return "".join(name_list)