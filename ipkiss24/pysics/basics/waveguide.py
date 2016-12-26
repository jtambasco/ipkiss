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

from ipcore.all import StrongPropertyInitializer, TypedList, TypedListProperty, RestrictedProperty, StringProperty, RestrictType

class __Waveguide__(StrongPropertyInitializer):
    """ Abstract base class for waveguide """
    name = StringProperty()

def WaveguideProperty(internal_member_name= None, restriction = None,**kwargs):
    R = RestrictType(__Waveguide__) & restriction
    return RestrictedProperty(internal_member_name, restriction = R,**kwargs)

class __Mode__(StrongPropertyInitializer):
    """ Abstract base class for waveguide mode """
    waveguide = WaveguideProperty()

    
class ModeList(TypedList):
    __item_type__ = __Mode__
    
    def __init__(self, modes = [], **kwargs):
        super(TypedList,self).__init__(**kwargs)
        self.namedict = dict()
        if isinstance(modes, dict):
            for m in modes:
                self.append(modes[m],m)
        else:
            for m in modes:
                self += m
    
    def append(self, item, name=None):
        super(ModeList,self).append(item)
        self.namedict[name] = item
    
    def get_mode_by_name(self, name):
        try:
            return self.namedict[name]
        except KeyError:
            return None
        
    def set_mode_name(self, item, name):
        if name in self.namedict.keys():
            return
        if not item in self:
            raise ValueError("Mode %s is not in list"%str(item))
        for (key,it) in self.namedict.iteritems():
            if it == item:
                it = self.namedict.pop(key)
                self.namedict[name] = it
                break

class ModeListProperty(TypedListProperty):
    __list_type__ = ModeList        

    
class Waveguide(__Waveguide__):
    """ Abstract base class for waveguide keeping a list of modes """
    modes = ModeListProperty(fdef_name='define_modes')
    
    def define_modes(self,modes):
        return modes
    
    
    
    