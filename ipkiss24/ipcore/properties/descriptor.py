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

from .restrictions import RestrictNothing, RestrictFunction, RestrictionError
from .restrictions import RestrictTypeList
from .processors import PropertyProcessor, ProcessorException

from types import NoneType

from ipcore.log import IPCORE_LOG as LOG
from ipcore.exceptions.exc import *
from ipcore.helperfunc import *

from ipcore.mixin.mixin import MixinBowl

from numpy import ndarray

__all__ = ["DefinitionProperty",
           "ListDefinitionProperty",
           "RestrictedProperty",  # DEPRECATED -- just a placeholder for DefinitionProperty : to be removed in later phase
           "RestrictedListProperty",  # DEPRECATED -- just a placeholder for DefinitionProperty : to be removed in later phase
           "PropertyDescriptor",  # DEPRECATED -- just a placeholder for DefinitionProperty : to be removed in later phase
           "ListPropertyDescriptor",  # DEPRECATED -- just a placeholder for ListDefinitionProperty : to be removed in later phase
           "FunctionProperty",
           "FunctionNameProperty",
           "SetFunctionProperty",
           "IndirectProperty",
           "ReadOnlyIndirectProperty",
           "ConvertProperty",
           "LockedProperty"]


#---------------------------------- BASE CLASS ---------------------------------------
class __BasePropertyDescriptor__(object):
    """ base class for property descriptors """
    __allowed_keyword_arguments__ = ["required"]

    def __init__(self, **kwargs):
        self.required = False
        self.__allowed_keyword_arguments__.append("doc")
        if "doc" in kwargs:
            self.__doc__ = kwargs["doc"]
            kwargs.pop("doc")
        else:
            self.__doc__ = ""

        for (k, v) in kwargs.items():
            if k in self.__allowed_keyword_arguments__:
                object.__setattr__(self, k, v)
            else:
                raise IpcorePropertyDescriptorException("Argument '%s' is not valid for %s" % (k, self))

    def bind_to_class(self, cls, name):
        pass

    def validate_on_binding(self, host_cls, name):
        return True


#------------------------------------------ CATEGORY 1 : RESTRICTED PROPERTIES --------------------

SET_EXTERNALLY = 0
CACHED = 1


class DefinitionProperty(__BasePropertyDescriptor__):
    __allowed_keyword_arguments__ = ["required", "default", "locked", "preprocess", "allow_none", "fdef_name", "restriction"]

    def __init__(self, internal_member_name=None, **kwargs):
        self.__name__ = internal_member_name
        self.name = internal_member_name
        # initialize with default values
        self.locked = False
        self.allow_none = False
        self.preprocess = PropertyProcessor()
        self.restriction = RestrictNothing()
        __BasePropertyDescriptor__.__init__(self, **kwargs) #FIXME: why set the arguments before valiate it?
        if ("fdef_name" not in kwargs):
            if ("default" not in kwargs):
                if ((("allow_none" not in kwargs) or (not kwargs["allow_none"]))
                      and (("required" in kwargs) and (not kwargs["required"]))):
                        raise IpcorePropertyDescriptorException("Property is specified as required='False', but should then have either a 'default' OR an 'fdef_name' OR be set to 'allow_none'")
            else:
                if (("required" in kwargs) and (kwargs["required"])):
                    raise IpcorePropertyDescriptorException("Property is specified as both required='True' and having a default : this is not allowed !")
            self.fdef_name = None
        else:
            if ("default" in kwargs):
                raise IpcorePropertyDescriptorException("Property has both a 'default' specified and an 'fdef_name' : this is not allowed !")
            if ("required" in kwargs) and (kwargs["required"]):
                raise IpcorePropertyDescriptorException("Property is both specified as 'required' and having an 'fdef_name' : this is not allowed !")

    def __get_default__(self):
        import inspect
        if inspect.isroutine(self.default):
            return self.default()
        else:
            return self.default

    def __externally_set_property_value_on_object__(self, obj, value):  # FIXME : add subscribe new value / unsubscribe old value
        clear_cached_values_in_store = True
        if self.__value_was_stored__(obj):
            old_value = obj.__store__[self.__name__][0]
            try:
                clear_cached_values_in_store = (type(old_value) != type(value)) or (old_value != value)
                if type(clear_cached_values_in_store) == ndarray:
                    clear_cached_values_in_store = clear_cached_values_in_store.all()
            except ValueError, e:  # precaution... if exceptionally this would occur because the comparison between old_value and value cannot be done, then clear caches anyway...
                clear_cached_values_in_store = True
        obj.__store__[self.__name__] = (value, SET_EXTERNALLY)
        if not(obj.flag_busy_initializing):
            obj.__do_validation__()
            if (clear_cached_values_in_store):
                obj.__clear_cached_values_in_store__()

    def __get_property_value_origin__(self, obj):
        (value, origin) = obj.__store__[self.__name__]
        return origin

    def __get_property_value_of_object__(self, obj):
        return obj.__store__[self.__name__][0]

    def __value_was_stored__(self, obj):
        return (self.__name__ in obj.__store__)

    def __get__(self, obj, type=None):
        '''Check if a value was set by the user : in that case, return the value, otherwise invoke the getter function to retrieve the value'''
        if obj is None:
            return self
        #check if a value was set by the user
        if not self.__value_was_stored__(obj):
            #no value was set in the store by the user, return the value calculated by the getter-function
            #if there a getter-method ?
            f = self.__get_getter_function__(obj)
            if f is None:
                #is there a default ?
                if hasattr(self, "default"):
                    value = self.preprocess(self.__get_default__(), obj)
                else:
                    #no default and no getter method
                    value = None
            else:
                #there is a getter method and no locally stored value
                value = self.__call_getter_function__(obj)  #FIXME: use f
            #check if the value is compatible with the property's restriction
            if not self.restriction(value, obj):
                if value is None:
                    if not self.allow_none:
                        raise IpcorePropertyDescriptorException("Cannot set property '%s' of '%s' to None." % (self.name, obj.__class__.__name__))
                else:
                    raise IpcorePropertyDescriptorException("Cannot set value '%s' to property '%s' of '%s' because it is incompatible with the restriction %s of the property." % (str(value), self.name, obj.__class__.__name__, str(self.restriction)))
            return value
        else:
            stored_value = self.__get_property_value_of_object__(obj)
            return stored_value

    def __get_getter_function__(self, obj):
        if self.fdef_name is None:
            if hasattr(self, "autogenerated_fdef_name") and hasattr(obj, self.autogenerated_fdef_name):
                result = getattr(obj, self.autogenerated_fdef_name)
                return result
            else:
                return None
        else:
            return getattr(obj, self.fdef_name)

    def __check_restriction__(self, obj, value):
            """ check if the value is compatible with the restriction """
            if self.restriction(value, obj) or (self.allow_none and value is None):
                return True
            else:
                raise IpcorePropertyDescriptorException("Invalid assignment for Property '%s' of '%s' with value %s: not compatible with restriction %s." % (self.name, obj.__class__.__name__, str(value), str(self.restriction)))

    def __cache_property_value_on_object__(self, obj, value):
        if type(obj) != NoneType: #FIXME: ???
            new_value = self.preprocess(value, obj)
            self.__check_restriction__(obj, new_value)
            obj.__store__[self.__name__] = (new_value, CACHED)
            return new_value
        else:
            return value

    def __call_getter_function__(self, obj):
        f = self.__get_getter_function__(obj)
        value = f()
        new_value = self.__cache_property_value_on_object__(obj, value)
        return new_value

    def __set__(self, obj, value):
        if self.locked:
            raise IpcorePropertyDescriptorException("Cannot assign to locked property '%s' of '%s'" % (self.name, type(obj).__name__))
        if self.preprocess is not None:
            try:
                new_value = self.preprocess(value, obj)
            except ProcessorException, e:
                LOG.info("RestrictedProperty::__set__ : an error was raised on self.preprocess : %s" % str(e))
                if (value is None) and not self.allow_none:
                    raise IpcorePropertyDescriptorException("Invalid assignment for property '%s' of '%s' with value %s" % (self.name, type(obj).__name__, str(value)))
                new_value = value
        else:
            new_value = value
        self.__check_restriction__(obj, new_value)
        self.__externally_set_property_value_on_object__(obj, new_value)

    def bind_to_class(self, cls, name):
        self.name = name
        if (not hasattr(self, "__name__")) or (self.__name__ is None):
            self.__name__ = "__prop_%s__" % name

    def validate_on_binding(self, host_cls, name):
        # autogenerate the name of the fdef-function if it was not set
        if self.fdef_name is None:
            self.autogenerated_fdef_name = "define_" + name
        #derive "required" automatically
        if (not hasattr(self, "default")) and ((self.fdef_name is None) and (not hasattr(host_cls, self.autogenerated_fdef_name))):
            if (not hasattr(self, "allow_none")) or (not self.allow_none):
                if (not self.locked):
                    self.required = True
        if hasattr(self, "default") and (self.default is None) and (not hasattr(self, "allow_none") or not self.allow_none):
            self.allow_none = True


class ListDefinitionProperty(DefinitionProperty):

    def __init__(self, internal_member_name=None, allowed_types=(object,), **kwargs):
        self.restriction = RestrictTypeList(allowed_types=allowed_types)
        if not ("required" in kwargs) and not ("fdef_name" in kwargs) and not ("default" in kwargs):
            kwargs["default"] = []
        if internal_member_name is not None:
            kwargs["internal_member_name"] = internal_member_name
        super(ListDefinitionProperty, self).__init__(**kwargs)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        if (self.__value_was_stored__(obj)):
            value = self.__get_property_value_of_object__(obj)
        else:
            value = self.__call_getter_function__(obj)
        return value


class PropertyDescriptor(DefinitionProperty):
    pass
    # now just a placeholder for backwards compatibility


class RestrictedProperty(PropertyDescriptor):
    pass
    #now just a placeholder for backwards compatibility


class RestrictedListProperty(ListDefinitionProperty):
    pass
    #now just a placeholder for backwards compatibility


class ListPropertyDescriptor(ListDefinitionProperty):
    pass
    #now just a placeholder for backwards compatibility


#---------------------------------- CATEGORY 2 : FUNCTION-PROPERTIES ---------------------------------------


class FunctionProperty(__BasePropertyDescriptor__):
    """ property which calls a get and set method to set the variables
        Very similar to python's built-in property
        If set method is not specified, then the property is considered locked and cannot be set. """

    __allowed_keyword_arguments__ = ["required"]

    def __init__(self, fget, fset=None, **kwargs):
        self.fget = fget
        if fset is None:
            self.locked = True
        else:
            self.fset = fset
            self.locked = False
        __BasePropertyDescriptor__.__init__(self, **kwargs)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return self.fget(obj)

    def __set__(self, obj, value):
        if not self.locked:
            return self.fset(obj, value)
        else:
            raise IpcorePropertyDescriptorException("Cannot assign to readonly FunctionProperty %s of '%s'" % (self.__name__, type(obj).__name__))


class FunctionNameProperty(__BasePropertyDescriptor__):
    """ property which calls a get and set method to set the variables.
        the get and set method are specified by name, so it supports
        override, but is slower than FunctionProperty.
        If set method is not specified, then the property is considered locked and cannot be set. """

    __allowed_keyword_arguments__ = ["required", "default"]

    def __init__(self, fget_name, fset_name=None, **kwargs):
        self.fget_name = fget_name
        if fset_name is None:
            self.locked = True
        else:
            self.fset_name = fset_name
            self.locked = False
        __BasePropertyDescriptor__.__init__(self, **kwargs)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return getattr(obj, self.fget_name)()

    def __set__(self, obj, value):
        if not self.locked:
            return getattr(obj, self.fset_name)(value)
        else:
            raise IpcorePropertyDescriptorException("Cannot assign to readonly FunctionProperty %s of '%s'" % (self.__name__, type(obj).__name__))


class SetFunctionProperty(__BasePropertyDescriptor__):
    """property which calls a set method to set the variables,
    but it is stored in a known attribute, so a get method
    need not be specified. A restriction can be specified."""

    __allowed_keyword_arguments__ = ["required", "default", "preprocess", "restriction"]

    def __init__(self, internal_member_name, fset, **kwargs):
        self.fset = fset
        self.__name__ = internal_member_name
        self.name = internal_member_name
        self.locked = False
        self.allow_none = False
        self.preprocess = PropertyProcessor()
        if "restriction" in kwargs:
            self.restriction = kwargs["restriction"]
        else:
            self.restriction = RestrictNothing()
        super(SetFunctionProperty, self).__init__(**kwargs)

    def __get_default__(self):
        import inspect
        if inspect.isroutine(self.default):
            return self.default()
        else:
            return self.default

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        if (self.__name__ in obj.__dict__):
            return obj.__dict__[self.__name__]
        else:
            if hasattr(self, "default"):
                d = self.__get_default__()
                if self.preprocess is None:
                    return d
                else:
                    return self.preprocess(d, obj)
            elif self.allow_none:
                return None
            else:
                raise IpcorePropertyDescriptorException("Attribute '%s' of '%s' is not set, and no default value is specified" (self.name, obj))

    def __set__(self, obj, value):
        new_value = self.preprocess(value, obj)
        if self.restriction(new_value, obj):
            return self.fset(obj, self.preprocess(value, obj))
        else:
            raise IpcoreRestrictionException("%s does not match restriction %s in property %s" % (value, self.restriction, self.__name__))

    def bind_to_class(self, cls, name):
        self.name = name
        if self.__name__ is None:
            self.__name__ = "__prop_%s__" % name


#---------------------------------- CATEGORY 3 : INDIRECT PROPERTIES ---------------------------------------

class IndirectProperty(__BasePropertyDescriptor__):
    """ property that gives access to properties of an attribute of the object.
    if property_name is omitted, it looks for a property with the same name """
    def __init__(self, attribute_name, property_name=None, **kwargs):
        self.attribute_name = attribute_name
        self.property_name = property_name
        self.locked = False
        __BasePropertyDescriptor__.__init__(self, **kwargs)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return eval("obj.%s.%s" % (self.attribute_name, self.property_name))

    def __set__(self, obj, value):
        return getattr(obj, self.attribute_name).__setattr__(self.property_name, value)

    def bind_to_class(self, cls, name):
        self.name = name
        self.property_name = name


class ReadOnlyIndirectProperty(IndirectProperty):
    """ property that gives access to properties of an attribute of the object """
    __allowed_keyword_arguments__ = ["preprocess"]

    def __init__(self, attribute_name, property_name=None, **kwargs):
        IndirectProperty.__init__(self,
                                   attribute_name=attribute_name,
                                   property_name=property_name,
                                    **kwargs)
        self.locked = True

    def __set__(self, obj, value):
        raise IpcorePropertyDescriptorException("Cannot assign to a read_only IndirectProperty of '%s'" % (type(obj).__name__))


#----------------------------------- CATEGORY 4 : CONVERT PROPERTY-----------------------------------

class ConvertProperty(__BasePropertyDescriptor__):
    __allowed_keyword_arguments__ = ["preprocess"]

    def __init__(self, parent_class, parent_property_name, convert_method):
        self.convert_method = convert_method
        self.parent_class = parent_class
        self.parent_property_name = parent_property_name
        self.locked = True
        __BasePropertyDescriptor__.__init__(self)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return self.parent_property.__get__(obj, type)

    def __set__(self, obj, value):
        if not is_call_internal(obj):
            self.convert_method(obj)
        value = self.parent_property.__set__(obj, value)
        return value

    def bind_to_class(self, cls, name):
        import inspect
        self.name = name
        if None == self.parent_property_name:
            self.parent_property_name = name
        if None == self.parent_class:
            mro = inspect.getmro(cls)
            found = False
            for C in mro[1:]:
                if name in C.__store__:
                    if isinstance(C.__store__[name][0], DefinitionProperty):
                        continue
                    self.parent_class = C
                    found = True
                    break
            if not found:
                raise IpcorePropertyDescriptorException("DefinitionProperty '%s' of '%s' should have a matching property in a parent class." % (name, cls))
        self.parent_property = object.__getattribute__(self.parent_class, self.parent_property_name)

#---------------------------------------- CATEGORY 5 : LOCKED PROPERTY --------------------------------------


class LockedProperty(DefinitionProperty):
    """ the use of this class disables a property in a parent class"""

    __allowed_keyword_arguments__ = ["locked"]

    def __init__(self, **kwargs):
        kwargs["locked"] = True
        super(LockedProperty, self).__init__(**kwargs)

    def __set__(self, obj, value):
        raise IpcorePropertyDescriptorException("Cannot assign to locked property '%s' of '%s'" % (self.name, type(obj).__name__))
