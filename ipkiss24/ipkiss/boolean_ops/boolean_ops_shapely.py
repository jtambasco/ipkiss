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

from .boolean_ops import __ShapeBooleanOpsAspect__
from dependencies.shapely_wrapper import *
from ipkiss.all import Coord2
import sys

########## boolean operations on Shape ##########

class __ShapeBooleanOpsWithShapelyAspect__(__ShapeBooleanOpsAspect__):  

    def __sub__(self, shape):
        my_poly = Polygon(self.points)
        other_poly = Polygon(shape.points)
        result_poly = my_poly.difference(other_poly)
        result_shapes = self.__poly_to_shape_list__(result_poly)
        return result_shapes
    
    def __and__(self, shape):
        my_poly = Polygon(self.points)
        other_poly = Polygon(shape.points)
        result_poly = my_poly.intersection(other_poly)
        result_shapes = self.__poly_to_shape_list__(result_poly)
        return result_shapes
    
    def __or__(self, shape):
        my_poly = Polygon(self.points)
        other_poly = Polygon(shape.points)
        result_poly = my_poly.union(other_poly)
        result_shapes = self.__poly_to_shape_list__(result_poly)
        return result_shapes
    
    def __xor__(self, shape):
        my_poly = Polygon(self.points)
        other_poly = Polygon(shape.points)
        result_poly = my_poly.symmetric_difference(other_poly)
        result_shapes = self.__poly_to_shape_list__(result_poly)
        return result_shapes    
    
    def __poly_to_shape_list__(self, poly):
        """Convert a Shapely polygon to a list of IPKISS shapes"""
        from dependencies.shapely_wrapper import shapely_geom_to_shape
        result_shapes = []
        if poly.is_empty:
            result_shapes.append(Shape())
        else:
            if isinstance(poly, MultiPolygon):
                for g in poly.geoms:
                    s = shapely_geom_to_shape(g)
                    result_shapes.append(s)
            else:
                s = shapely_geom_to_shape(poly)
                result_shapes.append(s)
        return result_shapes    
    
    
from ipkiss.geometry.shape import Shape

Shape.mixin_first(__ShapeBooleanOpsWithShapelyAspect__)


########## boolean operations on __ShapeElement__ ##########


from ipkiss.primitives.elements.shape import Boundary
from ipkiss.primitives.elements.basic import ElementList
from .boolean_ops import __BoundaryBooleanOpsAspect__


class __BoundaryBooleanOpsWithShapelyAspect__(__BoundaryBooleanOpsAspect__):


    def __sub__(self, elem):
        if (self.layer != elem.layer):
            return ElementList([self])
        else:
            result_shapes = self.shape.__sub__(elem.shape)
            result_elems = [Boundary(layer = self.layer, shape = rsh) for rsh in result_shapes]
            return result_elems            
    
    def __and__(self, elem):
        if (self.layer != elem.layer):
            return ElementList([])
        else:
            result_shapes = self.shape.__and__(elem.shape)
            result_elems = [Boundary(layer = self.layer, shape = rsh) for rsh in result_shapes]
            return result_elems  
    
    def __or__(self, elem):
        if (self.layer != elem.layer):
            return ElementList([self, elem])
        else:
            result_shapes = self.shape.__or__(elem.shape)
            result_elems = [Boundary(layer = self.layer, shape = rsh) for rsh in result_shapes]
            return result_elems  
    
    def __xor__(self, elem):
        if (self.layer != elem.layer):
            return ElementList([])
        else:
            result_shapes = self.shape.__xor__(elem.shape)
            result_elems = [Boundary(layer = self.layer, shape = rsh) for rsh in result_shapes]
            return result_elems      
    
Boundary.mixin_first(__BoundaryBooleanOpsWithShapelyAspect__)



