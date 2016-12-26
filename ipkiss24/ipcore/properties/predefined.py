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

from .descriptor import RestrictedProperty, DefinitionProperty
from . import restrictions
from .processors import ProcessorTypeCast
import numpy
import inspect

#######################################################
# Predefined Restrictions
#######################################################
RESTRICT_INT = restrictions.RestrictType(int)
RESTRICT_LONG = restrictions.RestrictType(long)
RESTRICT_FLOAT = restrictions.RestrictType(float)
RESTRICT_NUMBER = restrictions.RestrictType((int, float))
RESTRICT_COMPLEX = restrictions.RestrictType((int, float, complex))

RESTRICT_NONZERO = ~restrictions.RestrictValueList([0])
RESTRICT_POSITIVE = restrictions.RestrictRange(lower=0, lower_inc=False)
RESTRICT_NEGATIVE = restrictions.RestrictRange(upper=0, upper_inc=False)
RESTRICT_NONNEGATIVE = restrictions.RestrictRange(lower=0, lower_inc=True)
RESTRICT_NONPOSITIVE = restrictions.RestrictRange(upper=0, upper_inc=True)
RESTRICT_BOOL = restrictions.RestrictType(bool)
RESTRICT_FRACTION = restrictions.RestrictRange(lower=0, upper=1, lower_inc=True, upper_inc=True)
RESTRICT_STRING = restrictions.RestrictType(str)
RESTRICT_CHAR = restrictions.RestrictType(str) & restrictions.RestrictLen(1)
RESTRICT_ID_STRING = RESTRICT_STRING & ~restrictions.RestrictContains(" \/+")
RESTRICT_DICT = restrictions.RestrictType(dict)
RESTRICT_TUPLE = restrictions.RestrictType(tuple)
RESTRICT_LIST = restrictions.RestrictType(list)
RESTRICT_TUPLE2 = RESTRICT_TUPLE & restrictions.RestrictLen(2)
RESTRICT_INT_TUPLE2 = RESTRICT_TUPLE & restrictions.RestrictLen(2) & restrictions.RestrictTypeList(int)
RESTRICT_NUMBER_TUPLE2 = RESTRICT_TUPLE & restrictions.RestrictLen(2) & restrictions.RestrictTypeList((int, float))
RESTRICT_NUMPY_ARRAY = restrictions.RestrictType(numpy.ndarray)

class RestrictArrayDim(restrictions.__PropertyRestriction__):
    """ restrict the number of dimensions of a ndarray """
    def __init__(self, dim):
        self.dim = dim
    def validate(self, value, obj = None):
        return value.ndim == self.dim
    def __repr__(self):
        return  "Array Dimension Restriction: %s" % (str(self.dim))

RESTRICT_NUMPY_MASKED2DARRAY = restrictions.RestrictType(numpy.ma.MaskedArray) & RestrictArrayDim(2)
RESTRICT_NUMPY_MASKED3DARRAY = restrictions.RestrictType(numpy.ma.MaskedArray) & RestrictArrayDim(3)

######################################################
# predefined properties
######################################################


def CallableProperty(internal_member_name=None, restriction=None, **kwargs):
    R = (restrictions.RestrictFunction(inspect.isroutine) | restrictions.RestrictFunction(inspect.isclass)) & restriction
    P = RestrictedProperty(internal_member_name, restriction=R, **kwargs)
    P.__get_default__ = lambda: P.default
    return P


def IntProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_INT & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def LongIntProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_LONG & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def FloatProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_FLOAT & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def NumberProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_NUMBER & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)

def ComplexNumberProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_COMPLEX & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)

def StringProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_STRING & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def IdStringProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_ID_STRING & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def FilenameProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_STRING & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def BoolProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_BOOL & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def PositiveNumberProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_NUMBER & RESTRICT_POSITIVE & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def PositiveIntProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_INT & RESTRICT_POSITIVE & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def NonNegativeNumberProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_NUMBER & RESTRICT_NONNEGATIVE & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def NonNegativeIntProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_INT & RESTRICT_NONNEGATIVE & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def FractionProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_NUMBER & RESTRICT_FRACTION & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)

AngleProperty = NumberProperty  # to be specified later
NormalizedAngleProperty = NumberProperty  # to be specified later


def TimeProperty(internal_member_name=None, restriction=None, **kwargs):
    import time
    R = RESTRICT_NUMBER & restriction
    if not 'default' in kwargs:
        kwargs['default'] = time.time()
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def DictProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_DICT & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def ListProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_LIST & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def NumpyArrayProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_NUMPY_ARRAY & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)


def Tuple2Property(internal_member_name=None, restriction=None, **kwargs):
    R = RESTRICT_TUPLE2 & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)

def NumpyMasked2DArrayProperty(internal_member_name = None, restriction = None, **kwargs):
    R = RESTRICT_NUMPY_MASKED2DARRAY & restriction
    return RestrictedProperty(internal_member_name, restriction = R,**kwargs)

def NumpyMasked3DArrayProperty(internal_member_name = None, restriction = None, **kwargs):
    R = RESTRICT_NUMPY_MASKED3DARRAY & restriction
    return RestrictedProperty(internal_member_name, restriction = R,**kwargs)
