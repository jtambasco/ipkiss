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
from ipcore.properties.descriptor import DefinitionProperty
from ipcore.properties.restrictions import RestrictType


class TypedList(StrongPropertyInitializer, list):
    __item_type__ = object

    def __init__(self, items=[]):
        if isinstance(items, list) or isinstance(items, set):
            self.extend(items)
        else:
            self.append(items)
        super(TypedList, self).__init__()

    def __add__(self, other):
        L = self.__class__(self)
        if isinstance(other, list):
            L.extend(other)
        else:
            L.append(other)
        return L

    def __radd__(self, other):
        if isinstance(other, self.__item_type__):
            L = self.__class__([other])
            L.extend(self)
        elif isinstance(other, list):
            L = self.__class__(other)
            L.extend(self)
        return L

    def __iadd__(self, other):
        if isinstance(other, list):
            self.extend(other)
        else:
            self.append(other)
        return self

    def clear(self):
        del self[:]

    def __raise_invalid_type_exception__(self, item):
        raise Exception("You are trying to add an element of type %s to %s. This is not allowed. You can only add elements of type %s." % (str(type(item)), str(self.__class__), str(self.__item_type__)))

    def append(self, item):
        if isinstance(item, self.__item_type__):
            list.append(self, item)
        else:
            self.__raise_invalid_type_exception__(item)

    def extend(self, items):
        if type(self) == type(items):
            # we are certain that all items are of a valid type. No need to check each item individually
            list.extend(self, items)
        elif isinstance(items, list) or isinstance(items, set):
            for i in items:
                list.append(self, i)  # type will be checked in the 'append' function
        else:
            raise Exception("TypedList::extend should be used with a list as argument. Current argument if of type %s, which is not a list." % str(type(item)))

    def __deepcopy__(self, memo):
        from copy import deepcopy
        L = self.__class__()
        for item in self:
            L.append(deepcopy(item))
        return L


class TypedListProperty(DefinitionProperty):
    __list_type__ = TypedList
    """Property type for storing a typed list."""

    def __init__(self, internal_member_name=None, **kwargs):
        kwargs["restriction"] = RestrictType(allowed_types=[self.__list_type__])
        super(TypedListProperty, self).__init__(internal_member_name=internal_member_name, **kwargs)

    def __call_getter_function__(self, obj):
        f = self.__get_getter_function__(obj)
        value = f(self.__list_type__())
        if (value is None):
            value = self.__list_type__()
        self.__cache_property_value_on_object__(obj, value)
        value = self.__get_property_value_of_object__(obj)
        return value

    def __cache_property_value_on_object__(self, obj, objects):
        if isinstance(objects, self.__list_type__):
            super(TypedListProperty, self).__cache_property_value_on_object__(obj, objects)
        elif isinstance(objects, list):
            super(TypedListProperty, self).__cache_property_value_on_object__(obj, self.__list_type__(objects))
        else:
            raise TypeError("Invalid type in setting value of %s (expected %s), but generated : %s" % (self.__class__, self.__list_type__, str(type(objects))))

    def __set__(self, obj, objects):
        if isinstance(objects, self.__list_type__):
            self.__externally_set_property_value_on_object__(obj, objects)
        elif isinstance(objects, list):
            self.__externally_set_property_value_on_object__(obj, self.__list_type__(objects))
        else:
                raise TypeError("Invalid type in setting value of %s (expected %s): %s" % (self.__class_, self.__list_type__, str(type(objects))))
        return
