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
from . import transform
import math
from ipcore.mixin.mixin import MixinBowl

__all__ = ["Transformable",
           "NoDistortTransformable",
           "StoredTransformable",
           "StoredNoDistortTransformable"]

class __Transformable(MixinBowl):
    pass

class Transformable_basic(__Transformable):
    def transform(self, transformation):
        """applies transform to this object """
        return self

    def transform_copy(self, transformation):
        """ applies a transformation on a copy of this object """
        T = deepcopy(self)
        T.transform(transformation) # make a copy
        return T
    
    def reverse_transform(self, transformation):
        """applies reversed transform this object """
        return self.transform(-transformation)
    
    def reverse_transform_copy(self, transformation):
        """applies transform to copy of this object """
        T = deepcopy(self)
        T.reverse_transform(transformation) # make a copy
        return T

class NoDistortTransformable(Transformable_basic):
    """ object that cannot be distorted """
    pass

class Transformable(Transformable_basic):
    """ object that can be transformed """
    pass

from . import transforms

class StoredTransformable(Transformable):
    """ transformable that stores its transforms """
    __transformation_type__ = transform.Transform
    transformation = transform.generic_TransformationProperty()
    
    def __init__(self, transformation = None, **kwargs):
        if ((not "transformation" in kwargs) or (transformation != None)):
            kwargs['transformation'] = transformation
        super(StoredTransformable, self).__init__(**kwargs)
    
    def transform(self, transformation):
        """ applies a transformation on this object """
        if isinstance(transformation, self.__transformation_type__):
            self.transformation = self.transformation + transformation # make a copy
        elif transformation is None:
            return
        else:
            raise TypeError("Wrong type " + str(type(transformation)) + " for transformation in StoredTransformable")
        return self

    
    def expand_transform(self):
        """ tries to propagate the transformation as deep as possible in the hierarchy """

        return self

class StoredNoDistortTransformable(StoredTransformable, NoDistortTransformable):
    """ transformable that stores its homothetic transforms """
    __transformation_type__ = transform.GenericNoDistortTransform
    transformation = transform.TransformationProperty()
    
    def __init__(self, transformation=None, **kwargs):
        if ((not "transformation" in kwargs) or (transformation != None)):
            kwargs['transformation'] = transformation
        super(StoredNoDistortTransformable, self).__init__(**kwargs)
        
        