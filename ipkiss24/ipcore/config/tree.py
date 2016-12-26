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

from ..properties.descriptor import RestrictedProperty
from ..properties.predefined import StringProperty
from ..properties.restrictions import RestrictType
from ..exceptions.exc import IpcoreAttributeException


class ConfigTree(object):
    """A hierarchical tree for storing configuration settings."""

    def __init__(self, overwrite_allowed=[], **kwargs):
        self.__dict__["__config_tree_keys__"] = []
        self.overwrite_allowed = overwrite_allowed

    def __setattr__(self, key, value):
        if (key in self.__dict__) and (key not in ["name", "description", "__initialized__", "overwrite_allowed"]):
            current_value = self.__dict__[key]
            if (current_value != value):
                if   (not (key in self.overwrite_allowed)):
                    raise IpcoreAttributeException("Overwriting attributes in a configuration tree is not allowed (the attribute %s already has a value %s)" % (key, str(current_value)))
                else:
                    self.__dict__[key] = value
        else:
            self.__dict__[key] = value
            self.__getattribute__("__config_tree_keys__").append(key)

    def __generate_doc__(self, header):
        doc = ""
        keys = self.__dict__.keys()
        for k in keys:
            value = self.__dict__[k]
            if isinstance(value, ConfigTree):
                child_doc = value.__generate_doc__(header.upper() + "." + k.upper())
                doc = doc + child_doc + "\n"
            else:
                if not (k.startswith("__")):
                    doc = doc + header.upper() + "." + k.upper() + " = " + str(value) + "\n"
        return doc

    def keys(self):
        keys = []
        for k in self.__config_tree_keys__:
            if k in self.__dict__:
                keys.append(k)
        self.__config_tree_keys__ = keys
        return self.__config_tree_keys__

    def items(self):
        items = []
        for k in self.__config_tree_keys__:
            if k in self.__dict__:
                items.append((k,self.__dict__[k]))
        return items
    
    def find_item_key(self, item):
        for k in self.__config_tree_keys__:
            if k in self.__dict__:
                if self.__dict__[k] == item:
                    return k

    def __getitem__(self, key):
        return self.__dict__[key]

class DelayedInitConfigTree(ConfigTree):
    """A hierarchical tree for storing configuration settings, but with delayed initialisation : the initialize-function is called only at the moment a value is actually retrieved."""
    def __init__(self, **kwargs):
        super(DelayedInitConfigTree, self).__init__(**kwargs)
        self.__initialized__ = False

    def __getattr__(self, key):
        if self.__initialized__:
            raise IpcoreAttributeException("No attribute %s of ConfigTree" % key)
        self.initialize()
        self.__initialized__ = True
        return getattr(self, key)

    def initialize(self):
        raise NotImplementedError()


class FallbackConfigTree(ConfigTree):
    """A hierarchical tree for storing configuration settings, but with fallback. If a key cannot be found in this tree, the fallback tree is queried."""
    def __init__(self, fallback=None, **kwargs):
        super(FallbackConfigTree, self).__init__(**kwargs)
        self.fallback = fallback

    def __getattr__(self, key):
        if (not hasattr(self, "fallback")) or (self.fallback is None):
            raise IpcoreAttributeException("Attribute %s of the configuration tree could not be found: have you imported a configuration file?" % key)
        return getattr(self.fallback, key)
