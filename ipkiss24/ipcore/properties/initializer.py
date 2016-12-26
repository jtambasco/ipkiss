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

from .descriptor import __BasePropertyDescriptor__, CACHED, SET_EXTERNALLY
from ..mixin.mixin import MetaMixinBowl
from time import *
from ipcore.mixin.mixin import MixinBowl
from ipcore.properties.descriptor import *
from ipcore.helperfunc import *
from ipcore.exceptions.exc import IpcoreAttributeException
import inspect

SUPPRESSED = (None,)

_REGISTERED_CLASSES = set()


class MetaPropertyInitializer(MetaMixinBowl):
    def __init__(cls, name, bases, dict):
        cls.bind_properties()
        super(MetaPropertyInitializer, cls).__init__(name, bases, dict)
        _REGISTERED_CLASSES.add(cls)

    def bind_properties(cls):
        cls.__all_props__ = []
        req_props = []
        locked_props = []
        unlocked_props = []
        opt_props = []

        for p, a in cls.__get_properties__():
            if not p in cls.__all_props__:

                if hasattr(a, "bind_to_class"):
                    a.bind_to_class(cls, p)
                a.validate_on_binding(cls, p)

                if a.required:
                    req_props.append(p)
                else:
                    opt_props.append(p)

                if a.locked:
                    locked_props.append(p)
                else:
                    unlocked_props.append(p)

                cls.__all_props__.append(p)

        cls.__optional_props__ = opt_props
        cls.__required_props__ = req_props
        cls.__locked_props__ = locked_props
        cls.__unlocked_props__ = unlocked_props
        cls.compile_doc()

    def mixin_first(cls, mixin_class):
        super(MetaPropertyInitializer, cls).mixin_first(mixin_class)
        cls.bind_properties()
        for C in _REGISTERED_CLASSES:
            if issubclass(C, cls):
                C.bind_properties()

    def mixin_last(cls, mixin_class):
        super(MetaPropertyInitializer, cls).mixin_last(mixin_class)
        cls.bind_properties()
        for C in _REGISTERED_CLASSES:
            if issubclass(C, cls):
                C.bind_properties()

    def compile_doc(cls, ignore_properties=[]):
        ''' create a string in the RestructedText format with documentation about the class and it's properties '''
        cdescr = "- Class description : "
        if (cls.__doc__) and (cls.__doc__.find(cdescr) < 0):
            #first time __doc__ is generated
            cls.__doc_source_code__ = cls.__doc__.strip()
            doc = cdescr + "*" + cls.__doc_source_code__ + "*\n"
        else:
            if not hasattr(cls, "__doc_source_code__"):
                doc = cdescr + "*not available*\n"
            else:
                doc = cdescr + "*" + cls.__doc_source_code__ + "*\n"

        rp = cls.__required_properties__()
        ignore_properties.extend(cls.__locked_properties__())
        op = cls.__optional_properties__()

        if len(rp) > 0:
            doc += "\n- Required parameters :\n"
            for p in rp:
                if p not in ignore_properties:
                    doc += "\t* **" + p + "** "
                    prop_attr = getattr(cls, p)
                    if hasattr(prop_attr, "__doc__"):
                        doc += " : " + prop_attr.__doc__
                    if hasattr(prop_attr, "restriction"):
                        doc += "\n\t\t - restriction = *" + str(prop_attr.restriction) + "*\n"

        if len(op) > 0:
            doc += "\n- Optional parameters :\n"
            for p in op:
                if p not in ignore_properties:
                    doc += "\t* **" + p + "** "
                    prop_attr = getattr(cls, p)
                    if hasattr(prop_attr, "__doc__"):
                        doc += " : " + prop_attr.__doc__
                    if hasattr(prop_attr, "restriction"):
                        doc += "\n\t\t - restriction = *" + str(prop_attr.restriction) + "*"
                    if hasattr(prop_attr, "default"):
                        doc += "\n\t\t - default = *" + str(prop_attr.default) + "*"
                    if hasattr(prop_attr, "allow_none") and (prop_attr.allow_none):
                        doc += "\n\t\t - *None* allowed"
                    doc += "\n"

        doc += "\n- Methods :\n"
        cls_dir = dir(cls)
        for a in dir(MetaPropertyInitializer):
            if a in cls_dir:
                cls_dir.remove(a)
        for attr_name in cls_dir:
            if (attr_name.find("__") < 0):
                attr = getattr(cls, attr_name)
                if inspect.ismethod(attr):
                    (args, varargs, varkw, defaults) = inspect.getargspec(attr)
                    len_args = len(args) if args is not None else 0
                    len_defaults = len(defaults) if defaults is not None else 0
                    default_completed = list((None,) * (len_args - len_defaults))
                    default_completed.extend(defaults if defaults is not None else [])
                    if len_args > 0:
                        param_doc = "("
                        for arg, default in zip(args, default_completed):
                            param_doc = param_doc + arg
                            if not (default is None):
                                param_doc = param_doc + " = " + str(default)
                            param_doc = param_doc + ","
                        param_doc = param_doc[:-1] + ")"
                    else:
                        param_doc = "()"
                    doc += "\n\t\t - " + attr_name + param_doc
        cls.__doc__ = doc


def is_suppressed(propvalue):
    if isinstance(propvalue, tuple):
        return SUPPRESSED == propvalue
    else:
        return False


class PropertyInitializer(MixinBowl):
    __metaclass__ = MetaPropertyInitializer

    def __init__(self, **kwargs):
        self.flag_busy_initializing = True

        if not hasattr(self, "__store__"):
            self.__store__ = dict()
        props = self.__properties__()

        # assign properties
        for (key, value) in kwargs.items():
            if not is_suppressed(value):
                setattr(self, key, value)

        self.flag_busy_initializing = False

    @classmethod
    def __get_properties__(cls):
        prop = []
        for attrName in dir(cls):
            attr = getattr(cls, attrName)
            if isinstance(attr, __BasePropertyDescriptor__):
                prop.append([attrName, attr])
        return prop

    @classmethod
    def __properties__(cls):
        return cls.__all_props__

    @classmethod
    def __required_properties__(cls):
        return cls.__required_props__

    @classmethod
    def __optional_properties__(cls):
        return cls.__optional_props__

    @classmethod
    def __unlocked_properties__(cls):
        return cls.__unlocked_props__

    @classmethod
    def __locked_properties__(cls):
        return cls.__locked_props__

    @classmethod
    def __is_required__(cls, item):
        return getattr(cls, item).required

    @classmethod
    def __is_optional__(cls, item):
        I = getattr(cls, item)
        return not (I.required or I.locked)

    @classmethod
    def __is_locked__(cls, item):
        return not getattr(cls, item).locked

    @classmethod
    def __is_unlocked__(cls, item):
        return not getattr(cls, item).locked

    def __clear_cached_values_in_store__(self):  # FIXME: improve performance?
        if (not self.flag_busy_initializing):
            store_content_flattened = self.__store__.items()
            for (key, item) in store_content_flattened:
                origin = item[1]
                if origin == CACHED:
                    del self.__store__[key]
            if hasattr(self, "__IPCORE_CACHE__"):
                self.__IPCORE_CACHE__.clear()

    def __externally_set_properties__(self):  # FIXME: improve performance?
        es_props = []
        for p in self.__unlocked_properties__():
            prop = getattr(self.__class__, p)
            if isinstance(prop, DefinitionProperty):
                if (prop.__value_was_stored__(self)) and (prop.__get_property_value_origin__(self) == SET_EXTERNALLY):
                    es_props.append(p)
            else:
                es_props.append(p)
        return es_props

    def __init_property_default__(self, item):
        P = getattr(type(self), item)
        if hasattr(P, 'default'):
            setattr(self, item, P.__get_default__())

    def __copy__(self):
        req_props = self.__externally_set_properties__()
        kwargs = {}
        for p in req_props:
            kwargs[p] = getattr(self, p)
        return self.__class__(**kwargs)

    def __deepcopy__(self, memo):
        from copy import deepcopy
        req_props = self.__externally_set_properties__()
        kwargs = {}
        for p in req_props:
            kwargs[p] = deepcopy(getattr(self, p), memo)
        return self.__class__(**kwargs)

    def modified_copy(self, **override_kwargs):
        """ returns a copy of the object, but where the user can
            override properties using **override_kwargs
            """
        req_props = self.__externally_set_properties__()
        kwargs = {}
        for p in req_props:
            kwargs[p] = getattr(self, p)
        kwargs.update(override_kwargs)
        return self.__class__(**kwargs)

    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, type(self)):
            return False
        myprops = self.__get_properties__()
        otherprops = other.__get_properties__()
        if (len(myprops) != len(otherprops)):
            return False
        for myp, otherp in zip(myprops, otherprops):
            name = myp[0]
            if (name != otherp[0]):
                return False
            myVal = getattr(self, name)
            otherVal = getattr(other, name)
            try:
                if (myVal != otherVal):
                    return False
            except ValueError, e:
                import numpy
                if isinstance(myVal, numpy.ndarray):
                    if (myVal != otherVal).any():
                        return False
                else:
                    raise e
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class StrongPropertyInitializer(PropertyInitializer):

    def __init__(self, **kwargs):
        self.is_static = False
        self.flag_busy_initializing = True

        if not hasattr(self, "__store__"):
            self.__store__ = dict()
        req_props = self.__required_properties__()

        self.__assign_properties__(kwargs)

        for p in req_props:
            if not p in kwargs:
                raise IpcoreAttributeException("Required property '%s' is not found in keyword arguments of '%s' initialization." % (p, str(type(self))))

        self.flag_busy_initializing = False

        self.__do_validation__()

    def __assign_properties__(self, kwargs):
        """Assign properties from keyword arguments that are passed.
        
        This function assigns values to the properties based on keyword arguments that were passed. 
        It will look at self.__properties__ for all possible properties. 
        One can use the keyword argument "allow_unmatched_kwargs" to allow keyword arguments which do not have a corresponding property.
        These will be ignored, but not error will be raised.

        Example with allow_unmatched_kwargs:
            params = {"wg_width" : 0.45, "radius" : 5.0 }
            ring = Ring(**params, allow_unmatched_kwargs = True)    # Ring recognizes both arguments. True of False does not make a difference
            wg = Waveguide(**params, allow_unmatched_kwargs = True) # waveguide has no property 'radius', but no error is thrown.

            This is useful for PySimul, where all component and simulation parameters can be given in one dictionary, and
            each object extracts the parameters which are relevant for it.
        
        Raises:
            IpcoreAttributeException when a keyword argument cannot be matched 
                (unless "allow_unmatched_kwargs" is given as a keyword argument)
        """
        if "allow_unmatched_kwargs" in kwargs:
            allow_unmatched_kwargs = kwargs["allow_unmatched_kwargs"]
            del kwargs["allow_unmatched_kwargs"]
        else:
            allow_unmatched_kwargs = False
        props = self.__properties__()
        for (key, value) in kwargs.items():
            if (not key in props) and (not allow_unmatched_kwargs):
                raise IpcoreAttributeException("Keyword argument '%s' does not match a property of %s." % (key, str(type(self))))
            if not is_suppressed(value):
                setattr(self, key, value)

    def __do_validation__(self):
        if not self.validate_properties():
            from ipcore.exceptions.exc import IpcorePropertyDescriptorException
            raise IpcorePropertyDescriptorException("Validation failed for object %s of type %s." % (str(self), str(self.__class__)))

    def __make_static__(self):
        """Disables the automatic clearing of cached values when a property is externally set.
        A static object may thus be in an inconsistent state, because it's cached values are not automatically recalculated."""
        self.is_static = True

    def __make_dynamic__(self):
        """Enables the automatic clearing of cached values when a property is externally set."""
        self.is_static = False
        self.__clear_cached_values_in_store__()

    def __clear_cached_values_in_store__(self):
        if (not self.is_static):
            super(StrongPropertyInitializer, self).__clear_cached_values_in_store__()

    def validate_properties(self):
        """Check whether a combination of properties is valid.
        
        This function checks whether a combination of properties is valid. 
        It does not check the individual properties for valid use, this is done through the 
        use of DefinitionProperty with restrictions (for example: length = FloatProperty(default=5.0)).
        
        Returns:
            True: When the properties for this StrongPropertyInitializer are valid.
            False: When the properties are not valid. In this case, an IpcorePropertyDescriptorException will be raised
                   in StrongPropertyInitializer.__do_validation__
        """         
        return True

    def __property_was_externally_set__(self, property_name):
        property_name = "__prop_%s__" % property_name
        return (property_name in self.__store__) and (self.__store__[property_name][1] == 0)  # 0=SET_EXTERNALLY
