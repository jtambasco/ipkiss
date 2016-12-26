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

from ipcore.exceptions.exc import *


class ProcessorError(ValueError):
    def __init__(self, arg0):
        ValueError.__init__(self, arg0)


class ProcessorException(IpcoreException):
    pass


class PropertyProcessor(object):
    """ processes a value before it is passed as a property """
    def __init__(self):
        pass

    def __add__(self, other):
        if isinstance(other, PropertyProcessor):
            return __CompoundPropertyProcessor__([self, other])
        elif other is None:
            return self
        else:
            raise ProcessorException("Cannot add %s to PropertyProcessor " % type(other))

    def __iadd__(self, other):
        C = self.__add__(other)
        self = C
        return self

    def __call__(self, value, obj=None):
        return self.process(value, obj)

    def process(self, value, obj=None):
        return value

    def __repr__(self):
        return "<Property Processor >"


class __CompoundPropertyProcessor__(PropertyProcessor):
    """ compound property processor class """
    def __init__(self, processors=[]):
        self.__sub_processors = processors

    def __add__(self, other):
        if isinstance(other, __CompoundPropertyProcessor__):
            return __CompoundPropertyProcessor__(self.__sub_processors + other.__sub_processors)
        elif isinstance(other, PropertyProcessor):
            return __CompoundPropertyProcessor__(self.__sub_processors + [other])
        else:
            raise ProcessorException("Cannot add %s to PropertyProcessor" % type(other))

    def __iadd__(self, other):
        if isinstance(other, __CompoundPropertyProcessor__):
            self.__sub_processors += other.__sub_processors
            return self
        elif isinstance(other, PropertyProcessor):
            self.__sub_processors += [other]
            return self
        else:
            raise ProcessorException("Cannot add %s to PropertyProcessor" % type(other))

    def process(self, value, obj=None):
        """ processes the value """
        v = value
        for R in self.__sub_processors:
            v = R.process(self, value, obj)
        return v

    def __repr__(self):
        S = "< Compound Property Processor:"
        for i in self.__sub_processors:
            S += "   %s" % i.__repr__()
        S += ">"
        return S


class ProcessorTypeCast(PropertyProcessor):
    """ restrict the type or types the argument can have, and tries a typecast where possible """
    def __init__(self, cast_type):
        if not isinstance(cast_type, type):
            raise ProcessorException("cast_type argument %s in TypeCast Processor should be of type 'type'" % cast_type)
        self.cast_type = cast_type

    def process(self, value, obj=None):
        if isinstance(value, self.cast_type):
            return value
        else:
            return self.cast_type(value)

    def __repr__(self):
        S = "<Type Cast Processor: %s >" % self.cast_type.__name__


def ProcessorInt():
    return ProcessorTypeCast(int)


def ProcessorFloat():
    return ProcessorTypeCast(float)


def ProcessorString():
    return ProcessorTypeCast(str)


class ProcessorIntRound(PropertyProcessor):
    """ rounds a number to the nearest integer"""

    def process(self, value, obj=None):
        return int(round(value))

    def __repr__(self):
        S = "<Int Round Processor >"


class ProcessorRange(PropertyProcessor):
    """ brings a number to within a certain range """
    
    def __init__(self, lower=None, upper=None):
    
        if lower is None and upper is None:
            raise ProcessorException("Range Processor should have an upper or lower limit")

        if not upper is None and not lower is None:
            if lower > upper: #FIXME: what about >= ??
                raise ProcessorException("lower limit should be smaller than upper limit in Range Processor")
    
        self.lower = lower
        self.upper = upper

    def process(self, value, obj=None):
        if not self.lower is None:
            if value < self.lower:
                return self.lower
        if not self.upper is None:
            if value > self.upper:
                return self.upper
        return value

    def __repr__(self):
        S = "<Range Processor: [%s, %s] >" % (str(self.lower), str(upper))
