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

from ... import constants
from ...geometry.shape import Shape, ShapeProperty
from ...geometry.shapes import basic as shapes
from .basic import __Element__, __LayerElement__
from .group import Group

from ipcore.properties.descriptor import SetFunctionProperty, RestrictedProperty
from ipcore.properties.restrictions import RestrictValueList

from ...geometry import shape_info
from ...geometry import shape_modifier
from ...technology.settings import TECH
import copy
from ipkiss.log import IPKISS_LOG as LOG

from ipcore.properties.predefined import NumberProperty, BoolProperty

__all__ = ["Boundary",
           "Path",
           "ArcPath",
           "BendPath",
           "RelativeBendPath",
           "Circle",
           "CirclePath",
           "Cross",
           "CrossPath",
           "Ellipse",
           "EllipseArcPath",
           "EllipsePath",
           "Hexagon",
           "HexagonPath",
           "Line",
           "ParabolicWedge",
           "RadialLine",
           "RadialWedge",
           "Rectangle",
           "RectanglePath",
           "RegularPolygon",
           "RegularPolygonPath",
           "RingSegment",
           "RoundedRectangle",
           "RoundedRectanglePath",
           "Wedge"]


##########################################
# Basic Class
##########################################
class __ShapeElement__(__LayerElement__):
        shape = ShapeProperty(required = True)      

        def size_info(self):
                return self.shape.size_info.transform_copy(self.transformation)

        def convex_hull(self):
                return self.shape.convex_hull().transform(self.transformation)

        def is_empty(self):
                S = self.shape
                return S.is_empty() or S.len_without_identicals() < self.__min_length__
        
        def expand_transform(self):
                if not self.transformation.is_identity():
                        self.shape = self.shape.transform_copy(self.transformation)
                        from ...geometry.transforms.identity import IdentityTransform
                        self.transformation = IdentityTransform()
                return self
        



class Boundary(__ShapeElement__):
        line_width = 0.0  # for some backward compatibility functions
        __min_length__ = 3
        
        def __init__(self, 
                     layer, 
                     shape, 
                     transformation = None, 
                     **kwargs):
                super(Boundary, self).__init__(layer = layer,
                                                   shape = shape, 
                                                   transformation = transformation, 
                                                   **kwargs)
                


        def flat_copy(self, level = -1):
                S = Boundary(layer = self.layer, 
                             shape = self.shape, 
                             transformation = self.transformation)
                S.expand_transform()
                return S
                     
                
class Path (__ShapeElement__):
        path_type = RestrictedProperty(restriction = RestrictValueList(constants.PATH_TYPES), default = constants.PATH_TYPE_NORMAL)
        absolute_line_width = BoolProperty(default = False)
        __min_length__ = 2
        
        def __init__(self, 
                     layer, 
                     shape, 
                     line_width = 1.0, 
                     path_type = constants.PATH_TYPE_NORMAL, 
                     transformation = None, 
                     **kwargs):
                super(Path, self).__init__(layer = layer,
                                                   shape = shape, 
                                                         line_width = line_width, 
                                                         path_type = path_type, 
                                                         transformation = transformation, 
                                                         **kwargs)


        def set_line_width(self, new_line_width):
                self.absolute_line_width = bool(new_line_width < 0)
                self.__line_width__ = abs(new_line_width)
                #line widths of zero must be allowed for e-beam 
        line_width = SetFunctionProperty("__line_width__", set_line_width, required = True)

        def size_info(self):
                if self.line_width == 0.0:
                        return self.shape.size_info.transform_copy(self.transformation)
                else:
                        # this is slower, but accurate
                        from ...geometry.shapes.modifiers import ShapePath
                        return ShapePath(original_shape = self.shape, 
                                         path_width = self.line_width, 
                                         path_type = self.path_type).size_info.transform_copy(self.transformation)
                        # this is fast, but inaccurate
                        #return self.shape.size_info().transform_copy(self.transformation)

        def convex_hull(self):
                if self.line_width == 0.0:
                        return self.shape.convex_hull().transform(self.transformation)
                else:
                        # this is slower, but accurate
                        from ipkiss.geometry.shapes.modifiers import ShapePath
                        return ShapePath(original_shape = self.shape, 
                                         path_width = self.line_width, 
                                         path_type = self.path_type).convex_hull().transform(self.transformation)
                        # this is fast, but inaccurate
                        #return self.shape.size_info().transform_copy(self.transformation)



        def flat_copy(self, level = -1):
                S = Path(layer = self.layer, 
                                 shape = self.shape, 
                                 line_width = self.line_width, 
                                 path_type = self.path_type, 
                                 transformation = self.transformation,
                                 absolute_line_width = self.absolute_line_width)
                S.expand_transform()
                return S

        def expand_transform(self):
                if not self.transformation.is_identity():
                        self.shape = self.shape.transform_copy(self.transformation)
                        if not self.absolute_line_width:
                                self.line_width = self.transformation.apply_to_length(self.line_width)
                        from ...geometry.transforms.identity import IdentityTransform
                        self.transformation = IdentityTransform()
                return self
          


###########################################
# Circles and ellipses (and arcs)
###########################################


def Circle(layer, center = (0.0, 0.0),radius = 1.0, line_width = 0.0, angle_step = TECH.METRICS.ANGLE_STEP):
        coordinates = shapes.ShapeCircle(center = center, radius = radius, angle_step =angle_step)
        return Boundary(layer = layer, shape = coordinates)

def Ellipse (layer, center = (0.0, 0.0),box_size = (1.0,1.0), line_width = 0.0, angle_step = TECH.METRICS.ANGLE_STEP):
        coordinates = shapes.ShapeEllipse(center = center, box_size = box_size, angle_step =angle_step)
        return Boundary(layer = layer, shape = coordinates)

def RingSegment(layer, center, angle_start, angle_end, inner_radius, outer_radius, angle_step = TECH.METRICS.ANGLE_STEP):
        coordinates = shapes.ShapeRingSegment(center = center, angle_start = angle_start, angle_end = angle_end, inner_radius = inner_radius, outer_radius = outer_radius, angle_step =angle_step)
        return Boundary(layer = layer, shape = coordinates)

def Rectangle (layer, center = (0.0, 0.0),box_size = (1.0, 1.0), line_width=0):
        coordinates = shapes.ShapeRectangle(center = center, box_size = box_size)
        return Boundary(layer = layer, shape = coordinates)

def RoundedRectangle (layer, center = (0.0, 0.0), box_size = (1.0, 1.0), radius = 0, line_width = 0.0, angle_step = TECH.METRICS.ANGLE_STEP):
        coordinates = shapes.ShapeRoundedRectangle(center = center, 
                                       box_size = box_size, 
                                       radius = radius,
                                       angle_step = angle_step)
        return Boundary(layer = layer, shape = coordinates)

def Hexagon (layer, center = (0.0, 0.0),radius = 1.0, line_width = 0.0):
        coordinates = shapes.ShapeHexagon(center = center, radius = radius)
        return Boundary(layer = layer, shape = coordinates)

def RegularPolygon (layer, center = (0.0,0.0), radius = 1.0, n_o_sides = 8, line_width=0.0):
        coordinates = shapes.ShapeRegularPolygon(center = center, radius = radius, n_o_sides = n_o_sides)
        return Boundary(layer = layer, shape = coordinates)

def Cross (layer, center = (0.0,0.0), box_size = 20.0, thickness = 5.0, line_width = 0.0):
        coordinates = shapes.ShapeCross(center = center, box_size = box_size, thickness = thickness)
        return Boundary(layer = layer, shape = coordinates)

def Wedge (layer, begin_coord=(0.0,0.0), end_coord = (10.0, 0.0), begin_width = 3.0, end_width = 1.0, line_width = 0.0):
        coordinates = shapes.ShapeWedge(begin_coord = begin_coord, end_coord = end_coord, begin_width = begin_width, end_width = end_width)
        return Boundary(layer = layer, shape = coordinates)

def RadialWedge(layer, center, inner_radius, outer_radius, inner_width, outer_width, angle):
        coordinates = shapes.ShapeRadialWedge(center = center, inner_radius = inner_radius, outer_radius = outer_radius, inner_width = inner_width, outer_width = outer_width, angle = angle)
        return Boundary(layer = layer, shape = coordinates)

def ParabolicWedge (layer, begin_coord=(0.0,0.0), end_coord = (10.0, 0.0), begin_width = 3.0, end_width = 1.0, line_width = 0.0):
        coordinates = shapes.ShapeParabolic(begin_coord = begin_coord, end_coord = end_coord, begin_width = begin_width, end_width = end_width)
        return Boundary(layer = layer, shape = coordinates)

def Line (layer, begin_coord=(0.0,0.0), end_coord=(10.0, 0.0), line_width=1.0, path_type = constants.PATH_TYPE_NORMAL):
        coordinates = Shape([begin_coord, end_coord], False)
        return Path(layer, coordinates, line_width, path_type)

def RadialLine(layer, center, inner_radius, outer_radius, width, angle):
        length = abs(outer_radius - inner_radius)
        return Line(layer,
                       (center[0] + inner_radius * cos(angle*DEG2RAD), center[1] + inner_radius * sin(angle*DEG2RAD)),
                       (center[0] + outer_radius * cos(angle*DEG2RAD), center[1] + outer_radius * sin(angle*DEG2RAD)),
                       width)


def BendPath(layer, start_point = (0.0,0.0), radius = 1.0, line_width = 0.5, input_angle=0.0, output_angle = 90.0, angle_step = TECH.METRICS.ANGLE_STEP, path_type = constants.PATH_TYPE_NORMAL, clockwise = False):
        coordinates = shapes.ShapeBend(start_point = start_point, radius = radius, input_angle = input_angle, output_angle = output_angle , angle_step = angle_step, clockwise = clockwise)
        return Path (layer, coordinates, line_width, path_type)

def RelativeBendPath(layer, start_point = (0.0,0.0), radius = 1.0, line_width = 0.5, input_angle=0.0, angle_amount = 90.0, angle_step = TECH.METRICS.ANGLE_STEP, path_type = constants.PATH_TYPE_NORMAL):
        coordinates = shapes.ShapeBendRelative(start_point = start_point, radius = radius, input_angle = input_angle, angle_amount = angle_amount , angle_step = angle_step)
        return Path (layer, coordinates, line_width, path_type)

def ArcPath (layer, center = (0.0,0.0), radius = 1.0, line_width = 0.5, start_angle=0.0, end_angle = 90.0, angle_step = TECH.METRICS.ANGLE_STEP, path_type = constants.PATH_TYPE_NORMAL, clockwise = False):
        coordinates = shapes.ShapeArc(center = center, radius = radius, start_angle = start_angle, end_angle = end_angle, angle_step =angle_step, clockwise = clockwise)
        return Path (layer, coordinates, line_width, path_type)

def EllipseArcPath (layer, center = (0.0,0.0),box_size = (1.0,1.0), line_width = 0.5, start_angle=0.0, end_angle = 90.0, angle_step = TECH.METRICS.ANGLE_STEP, path_type = constants.PATH_TYPE_NORMAL, clockwise = False):
        coordinates = shapes.ShapeEllipseArc(center = center, box_size = box_size, start_angle = start_angle, end_angle = end_angle , angle_step = angle_step, clockwise = clockwise)
        return Path (layer, coordinates, line_width, path_type)

def EllipsePath (layer, center = (0.0,0.0), box_size = (1.0,1.0), line_width = 0.5, angle_step = TECH.METRICS.ANGLE_STEP):
        coordinates = shapes.ShapeEllipse(center = center, box_size = box_size, angle_step =angle_step)
        return Path(layer, coordinates, line_width)

def CirclePath (layer, center = (0.0,0.0), radius = 1.0, line_width = 0.5, angle_step = TECH.METRICS.ANGLE_STEP):
        coordinates = shapes.ShapeCircle(center = center, radius = radius, angle_step =angle_step)
        return Path(layer, coordinates, line_width)

def RectanglePath (layer, center = (0.0, 0.0), box_size = (1.0, 1.0), line_width=1.0):
        coordinates = shapes.ShapeRectangle(center = center, box_size = box_size)
        return Path(layer, coordinates, line_width)

def RoundedRectanglePath (layer, center = (0.0, 0.0), box_size = (1.0, 1.0), radius = 0,  line_width = 0.5, angle_step = TECH.METRICS.ANGLE_STEP):
        coordinates = shapes.ShapeRoundedRectangle(center = center, box_size = box_size, radius = radius, angle_step =angle_step)
        return Path(layer, coordinates, line_width)

def HexagonPath (layer, center = (0.0,0.0), radius = 1.0, line_width=0.5):
        coordinates = shapes.ShapeHexagon(center = center, radius = radius)
        return Path (layer,coordinates, line_width)

def RegularPolygonPath (layer, center = (0.0,0.0), radius = 1.0, n_o_sides = 8, line_width=0.5):
        coordinates = shapes.ShapeRegularPolygon(center = center, radius = radius, n_o_sides = n_o_sides)
        return Path (layer,coordinates, line_width)

def CrossPath (layer, center = (0.0,0.0), box_size = 20.0, thickness = 5.0, line_width = 0.5):
        coordinates = shapes.ShapeCross(center = center, box_size = box_size, thickness = thickness)
        return Path (layer,coordinates, line_width)

