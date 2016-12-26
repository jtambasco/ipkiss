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

import copy
from ipcore.mixin.mixin import MixinBowl
import inspect

###################################################
# restrictions
###################################################

__all__ = ["RestrictNothing",
           "RestrictLen",
           "RestrictLenRange",
           "RestrictRange",
           "RestrictType",
           "RestrictFunction",
           "RestrictIterable",
           "RestrictClass",
           "RestrictList",
           "RestrictTypeList",
           "RestrictValueList",
           "RestrictContains"]


class RestrictionError(ValueError):
    def __init__(self, arg0):
        ValueError.__init__(self, arg0)


class __PropertyRestriction__(MixinBowl):
    """ abstract base class for restrictions on property values """
    def __init__(self):
        pass

    def __and__(self, other):
        if isinstance(other, __PropertyRestriction__):
            return __PropertyRestrictionAnd__(self, other)
        elif other is None:
            return self
        else:
            raise TypeError("Cannot AND __PropertyRestriction__ with %s" % type(other))

    def __iand__(self, other):
        C = self.__and__(other)
        self = C
        return self

    def __or__(self, other):
        if isinstance(other, __PropertyRestriction__):
            return __PropertyRestrictionOr__(self, other)
        elif other is None:
            return self
        else:
            raise TypeError("Cannot OR __PropertyRestriction__ with %s" % type(other))

    def __ior__(self, other):
        C = self.__and__(other)
        self = C
        return self

    def __invert__(self):
        return __PropertyRestrictionNot__(self)

    def __call__(self, value, obj=None):
        return self.validate(value, obj)

    def validate(self, value, obj=None):
        """ returns True if the value passes the restriction """
        return True

    def __repr__(self):
        return "Generic Restriction"


class __PropertyRestrictionAnd__(__PropertyRestriction__):
    def __init__(self, restriction1, restriction2):
        self.restriction1 = restriction1
        self.restriction2 = restriction2

    def validate(self, value, obj=None):
        return self.restriction1(value, obj) and self.restriction2(value, obj)

    def __repr__(self):

        return "(%s and %s)" % (self.restriction1, self.restriction2)


class __PropertyRestrictionOr__(__PropertyRestriction__):
    def __init__(self, restriction1, restriction2):
        self.restriction1 = restriction1
        self.restriction2 = restriction2

    def validate(self, value, obj=None):
        return self.restriction1(value, obj) or self.restriction2(value, obj)

    def __repr__(self):
        return "(%s or %s)" % (self.restriction1, self.restriction2)


class __PropertyRestrictionNot__(__PropertyRestriction__):
    def __init__(self, restriction):
        self.restriction = restriction

    def validate(self, value, obj=None):
        return not self.restriction(value, obj)

    def __repr__(self):
        return "(not %s)" % (self.restriction)


class RestrictNothing(__PropertyRestriction__):
    """ no restriction on the property value """
    def __add__(self, other):
        if isinstance(other, __PropertyRestriction__):
            return copy.copy(other)
        else:
            raise TypeError("Cannot add %s to __PropertyRestriction__" % type(other))

    def __iadd__(self, other):
        self = copy.copy(other)
        return self

    def __repr__(self):
        return "No Restriction"


class RestrictType(__PropertyRestriction__):
    """ restrict the type or types the argument can have. Pass a type or tuple of types """
    def __init__(self, allowed_types):
        self.allowed_types = ()
        self .__types_set = False
        self.__add_type__(allowed_types)
        if not self.__types_set:
            raise ValueError("allowed_typed of Type Restriction should be set on initialization")

    def __add_type__(self, type_type):
        if isinstance(type_type, type):
            self.allowed_types += (type_type,)
            self .__types_set = True
        elif isinstance(type_type, (tuple, list)):
            for T in type_type:
                self.__add_type__(T)
        else:
            raise TypeError("Restrict type should have a 'type' or 'tuple' of types as argument")

    def validate(self, value, obj=None):
        return isinstance(value, self.allowed_types)

    def __repr__(self):
        return "Type Restriction:" + ",".join([T.__name__ for T in self.allowed_types])


class RestrictFunction(__PropertyRestriction__):
    """ restricts the value to those that return 'True' when passed to a given function """
    def __init__(self, validator_function):
        self.validator_function = validator_function

    def validate(self, value, obj=None):
        return self.validator_function(value) == True

    def __repr__(self):
        return "Function Restriction: %s" + str(self.validator_function)


class RestrictClass(RestrictType):
    """ restrict the base class of an argument which is a class. Pass a class or tuple of classes """

    def validate(self, value, obj=None):
        return issubclass(value, self.allowed_types)

    def __repr__(self):
        return "Class Restriction:" + ",".join([T.__name__ for T in self.allowed_types])


class RestrictList(__PropertyRestriction__):
    """ subject all individual elements of an iterable to a certain restriction """
    def __init__(self, restriction):
        self.restriction = restriction

    def validate(self, value, obj=None):
        try:
            for i in value:
                if not self.restriction.validate(i):
                    return False
            return True
        except:
            return False

    def __repr__(self):
        return "List Restriction: %s" % self.restriction


class RestrictTypeList(RestrictList):
    """ restrict the argument to a list which contains a given type or types. Pass a type or tuple of types """
    def __init__(self, allowed_types):

        RestrictList.__init__(self, restriction=RestrictType(allowed_types))

    def __repr__(self):
        return "Type List Restriction:" + ",".join([T.__name__ for T in self.restriction.allowed_types])


class RestrictValueList(__PropertyRestriction__):
    """ restrict the argument to a list of allowed values """
    def __init__(self, allowed_values):
        self.allowed_values = allowed_values

    def validate(self, value, obj=None):
        return value in self.allowed_values

    def __repr__(self):
        return "Value List Restriction: [" + ",".join([str(T) for T in self.allowed_values]) + "]"


class RestrictIterable(__PropertyRestriction__):

    def validate(self, value, obj=None):
        return isinstance(value, basestring) or getattr(value, '__iter__', False)

    def __repr__(self):
        return "Iterable Restriction"


class RestrictRange(__PropertyRestriction__):
    """ restrict the argument to a given range """
    def __init__(self, lower=None, upper=None, lower_inc=True, upper_inc=False):
        self.lower = lower
        self.upper = upper
        self.lower_inc = lower_inc
        self.upper_inc = upper_inc
        if lower is None and upper is None:
            raise ValueError("Range Restriction should have an upper or lower limit")
        if not upper is None and not lower is None:
            if lower > upper:
                raise ValueError("lower limit should be smaller than upper limit in Range Restriction")

    def validate(self, value, obj=None):
        if self.lower is None:
            if self.upper_inc:
                return value < self.upper
            else:
                return value <= self.upper
        elif self.upper is None:
            if self.lower_inc:
                return value >= self.lower
            else:
                return value > self.lower
        else:
            if self.lower_inc:
                T1 = value >= self.lower
            else:
                T1 = value > self.lower
            if self.upper_inc:
                T2 = value <= self.upper
            else:
                T2 = value < self.upper
            return T1 and T2

    def __repr__(self):
        if self.lower_inc:
            west_b = "["
        else:
            west_b = "]"

        if self.upper_inc:
            right_b = "]"
        else:
            right_b = "["
        S = "Range Restriction: %s%s,%s%s" % (west_b, str(self.lower), str(self.upper), right_b)
        return S


class RestrictLenRange(__PropertyRestriction__):
    """ restrict the length of a list, tuple, shape, ... . Value must support __len__ method """

    def __init__(self, min_length=None, max_length=None):
        self.min_length = min_length
        self.max_length = max_length
        if min_length == None and max_length == None:
            raise ValueError("Len Range Restriction should have a minimum and/or maximum value")
        if not min_length is None and not max_length is None:
            if max_length < min_length:
                raise ValueError("Min_length should be smaller than Max_length Len Range Restriction")

    def validate(self, value, obj=None):
        L = len(value)
        if self.min_length is None:
            return L <= self.max_length
        elif self.max_length is None:
            return L >= self.min_length
        else:
            T1 = L >= self.min_length
            T2 = L <= self.max_length
            return T1 and T2

    def __repr__(self):
        return  "Len Range Restriction: %s-%s" % (str(self.min_length), str(self.max_length))


class RestrictLen(__PropertyRestriction__):
    """ restrict the length of a list, tuple, shape, ... . Value must support __len__ method """
    def __init__(self, length):
        self.length = length

    def validate(self, value, obj=None):
        return len(value) == self.length

    def __repr__(self):
        return  "Len Restriction: %s" % (str(self.length))


class RestrictContains(__PropertyRestriction__):
    """ restrict the argument to an object with contains at least one of a set of allowed values """
    def __init__(self, allowed_values):
        self.allowed_values = allowed_values

    def validate(self, value, obj=None):
        for v in self.allowed_values:
            if v in value:
                return True
        return False

    def __repr__(self):
        return  "Contains Restriction: %s" % (str(self.allowed_values))
