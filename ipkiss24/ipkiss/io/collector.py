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
from binascii import b2a_hex, a2b_hex

class __Collector__(StrongPropertyInitializer):
    def __init__(self, **kwargs):
        self.reset()
        super(__Collector__, self).__init__(**kwargs)

    def reset(self):
        pass
    
class ListCollector(__Collector__):

    def __iadd__(self, item_list):
        self.__list__ += item_list
        return self
        
    def reset(self):
        self.__list__ = []
        return
    
    def out_str(self):
        return self.__list__
    
class ListStringCollector(ListCollector):
    def out_str(self):
        return "".join(self.__list__)

class NewlineStringCollector(ListStringCollector):
    def __iadd__(self, item_list):
        self.__list__ += item_list
        self.__list__ += ["\n"]
        return self
        
class __StreamCollector__(__Collector__):
    o_stream = RestrictedProperty(required = True)

    def out_str(self):
        return ""

class StreamStringCollector(__StreamCollector__):
    def __iadd__(self, item_list):
        self.o_stream.write("".join(item_list))
        return self

class StreamA2BHexCollector(__StreamCollector__):
    def __iadd__(self, item_list):
        self.o_stream.write(a2b_hex("".join(item_list)))
        return self
