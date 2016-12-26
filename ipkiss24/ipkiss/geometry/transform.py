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

from copy import deepcopy

from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.processors import ProcessorTypeCast
from types import NoneType
from ipcore.properties.initializer import StrongPropertyInitializer

__all__ = ["generic_TransformationProperty",
           "TransformationProperty"]

#----------------------------------------------------------------------------
# Transformation class
#----------------------------------------------------------------------------

class Transform(StrongPropertyInitializer):
    """ abstract base class for generic transform """

    def apply(self, item):
        """ applies the transform to the transformable item (no copy) """
        if isinstance(item, list):
            from .shape import Shape
            L = Shape(item)
            L.transform(self)
            return L
        else: 
            return item.transform(self)


    def apply_to_copy(self, item):
        """ applies the transform to a copy of the transformable item """
        if isinstance(item, list):
            from .shape import Shape
            L = Shape(item).transform_copy(self)
            return L
        else:
            return item.transform_copy(self)

    def __call__(self, item):
        """ if item is Transformable: applies the transform to a copy of the transformable item
            if item is a transform: returns a new transform that is a concatenation of this one and item """
        if isinstance(item, NoneType):
            return self
        if isinstance(item, Transform):
            return item + self
        else: #shape, coordinatelist or transformable
            return self.apply_to_copy(item)

    # define addition
    def __add__(self, other):
        """ creates a new transformation that is a concatenation of this one and other """
        if other is None: return CompoundTransform([self])
        return CompoundTransform([self, other])

    # define subtraction
    def __sub__(self, other):
        """ creates a new transformation that is a concatenation of this one and the reverse of other """
        if other is None: return CompoundTransform([self])
        if isinstance(other, __ReversibleTransform__):
            return CompoundTransform([self, -other])
        else:
            raise TypeError("Cannot subtract an irreversible transform")

    def is_identity(self):
        """ returns True is the transformation does nothing """
        return True
    
    def is_isometric(self):
        """ returns True if the transformation conserves angles and distances """
        return True
    
    def is_homothetic(self):
        """ returns True if the transformation conserves angles """
        return True

#----------------------------------------------------------------------------
# Reversible Transformationclass
#----------------------------------------------------------------------------

class __ReversibleTransform__(Transform):
    """ base class for a transformation that can be reversed """

    def reverse(self, item):
        """ applies the reverse transformation on item """
        if isinstance(item, list):
            from .shape import Shape
            L = Shape(item)
            L.reverse_transform(self)
            return L
        else:
            return item.reverse_transform(self)

    # define addition
    def __add__(self, other):
        """ creates a new transformation that is a concatenation of this one and other """
        if other is None: return ReversibleCompoundTransform([self])
        if isinstance(other, __ReversibleTransform__):
            return ReversibleCompoundTransform([self, other])
        else:
            return CompoundTransform([self, other])
        # if the other is irreversible, the compound transform will be automatically adjusted

    # define subtraction
    def __sub__(self, other):
        """ creates a new transformation that is a concatenation of this one and the reverse of other """
        if other is None: return ReversibleCompoundTransform([self])
        if isinstance(other, __ReversibleTransform__):
            return ReversibleCompoundTransform([self, -other])
        else:
            raise TypeError("Cannot subtract an irreversible transform")

    # should return the reversed object
    def __neg__(self):
        """ returns the reverse transformation """
        pass


#----------------------------------------------------------------------------
# Transformations that do not distort an object
# these transformation cal all be reduced to a concatenation of
#  - a vertical flip
#  - a rotation
#  - a magnification
#  - a translation
# these are encorporated in a single class, which allows for easy concatenation of
# transformations (using the + of () operator
# Special cases are subclassed (simple translation, rotation, mirroring, ...)
# for efficiency and readability
#
# These transformations can be used on shapes, but also on elements
# in fact, on any NoDistortTransformable object
#
#----------------------------------------------------------------------------

class GenericNoDistortTransform(__ReversibleTransform__):
    pass


#----------------------------------------------------------------------------
# Compound Transformations
# these can be used only on shapes.
# for concatenations, a compound transformation is created
#----------------------------------------------------------------------------

class CompoundTransform(Transform):
    """ a store for the concatenation of (non-homothetic) transforms """
    # a concatenation of transforms
    def __init__(self, transforms = [], **kwargs):
        if isinstance(transforms, list):
            self.__subtransforms__ = transforms
        elif isinstance(transforms, CompoundTransform):
            self.__subtransforms__ = []
            self.__subtransforms__.extend(transforms)
        else:            
            self.__subtransforms__ = [transforms]
        super(CompoundTransform, self).__init__(**kwargs)

    def apply(self, item):
        """ apply the transform to the transformable item """
        if isinstance(item, list):
            from .shape import Shape
            L = Shape(item)
            for c in self.__subtransforms__:
                L = c.apply(L)
            return L
        else:
            for c in self.__subtransforms__:
                item = c.apply(item)

    def apply_to_coord(self, coord):
        """ apply transformation to coordinate """
        for c in self.__subtransforms__:
            coord = c.apply_to_coord(coord)
        return coord

    def apply_to_array(self, coords):
        """ apply transformation to numpy array"""
        for c in self.__subtransforms__:
            coords = c.apply_to_array(coords)
        return coords

    def __add__(self, other):
        """ returns the concatenation of this transform and other """
        T = CompoundTransform(self)
        T.add(other)
        return T

    def __iadd__(self, other):
        """ concatenates other to this transform """
        self.add(other)
        return self

    def add(self, other):
        """ concatenate another transform to the compound transform """
        if other is None: return 
        if isinstance(other, CompoundTransform):
            for c in other.__subtransforms__:
                self.add(other)
        elif isinstance(other, Transform):
            self.elements.append(other)
        else:
            raise TypeError("Cannot add object of type " + str(type(other)) + " to transform")
        
    def is_identity(self):
        """ returns True if the transformation does nothing """
        for c in self.__subtransforms__:
            if not c.is_identity(): return False
        return True

    def is_isometric(self):
        """ returns True if the transformation conserves angles and distances """
        for c in self.__subtransforms__:
            if not c.is_isometric(): return False
        return True
    
    def is_homothetic(self):
        """ returns True if the transformation conserves angles """
        """ returns True if the transformation does nothing """
        for c in self.__subtransforms__:
            if not c.is_homothetic(): return False
        return True

        
class ReversibleCompoundTransform(CompoundTransform, __ReversibleTransform__):
    """ a store for the concatenation of (non-homthetic) reversible transformas """

    def __make_irreversible__(self):
        self.__class__ = CompoundTransform

    def reverse(self, item):
        """ applies the reverse transform on the transformable item"""
        if isinstance(item, list):
            from .shape import Shape
            L = Shape(item)
            for c in reversed(self.__subtransforms__):
                L = c.reverse(L)
            return L
        else:
            for c in reversed(self.__subtransforms__):
                item = c.reverse(item)


    def reverse_on_coord(self, coord):
        """ apply reverse transformation to coordinate """
        for c in reversed(self.__subtransforms__):
            coord = c.reverse_on_coord(coord)
        return coord

    def reverse_on_array(self, coords):
        """ internal use: applies reverse transformation to a numpy array """
        for c in reversed(self.__subtransforms__):
            coords = c.reverse_on_array(coords)
        return coords

    def __add__(self, other):
        """ returns the concatenation of this transform and other """
        T = ReversibleCompoundTransform(self)
        if other != None: T.add(other)
        return T

    def __iadd__(self, other):
        """ concatenates other to this transform """
        self.add(other)
        return self

    def __sub__(self, other):
        """ returns the concatenation of this transform and the reverse of other """
        T = ReversibleCompoundTransform(self)
        T.add(-other)
        return T

    def __isub__(self, other):
        """ concatenates the reverse of other to this transform """
        self.add(- other)
        return self


    def add(self, other):
        """ concatenates the other transform to this """
        if isinstance(other, CompoundTransform):
            for c in other.__subtransforms__:
                self.add(other)
        if isinstance(other, __ReversibleTransform__):
            self.elements.append(other)
        elif isinstance(other, Transform):
            self.__make_irreversible__()
            self.elements.append(other)
        else:
            raise TypeError("Cannot add object of type " + str(type(other)) + " to transform")

    def __neg__(self):
        """ returns the reverse transform """
        T = ReversibleCompoundTransform()
        for c in reversed(self):
            T.add(-c)
        return T

#----------------------------------------------------------------------------
# Transformations that do distort the shape
# these can be used only on shapes.
# for concatenations, a compound transformation is created
#----------------------------------------------------------------------------

    
#----------------------------------------------------------------------------
# Shape rotations and translation functions
#----------------------------------------------------------------------------


class ProcessorTransformation(ProcessorTypeCast):
    def __init__(self):
        ProcessorTypeCast.__init__(self, Transform)
    
    def process(self, value, obj= None):
        from .transforms.identity import IdentityTransform
        if value is None:
            return IdentityTransform()
        else:
            return ProcessorTypeCast.process(self, value, obj)
        
class ProcessorNoDistortTransformation(ProcessorTypeCast):
    def __init__(self):
        ProcessorTypeCast.__init__(self, GenericNoDistortTransform)
   
    def process(self, value, obj=None):
        from .transforms.identity import IdentityTransform
        if value is None:
            return IdentityTransform()
        else:
            return ProcessorTypeCast.process(self, value, obj)
                
        

def generic_TransformationProperty(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    R = RestrictType(Transform) & restriction
    P = ProcessorTransformation() + preprocess
    if "default" in kwargs:
        default = kwargs["default"]
    else:
        default = None
    return RestrictedProperty(internal_member_name, default = default, restriction = R, preprocess = P)

def TransformationProperty(internal_member_name=None, restriction=None, preprocess=None, **kwargs):
    R = RestrictType(GenericNoDistortTransform) & restriction
    P = ProcessorNoDistortTransformation() + preprocess
    if "default" in kwargs:
        default = kwargs["default"]
    else:
        default = None
    return RestrictedProperty(internal_member_name, default = default, restriction = R, preprocess = P)



