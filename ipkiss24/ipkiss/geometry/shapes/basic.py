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

from ...constants import RAD2DEG, DEG2RAD
from ... import settings
import math
import numpy
from ..shape import Shape
from ..shape_info import distance, angle_rad
from ..size_info import SizeInfo

from ipcore.properties.predefined import NumberProperty, BoolProperty, IntProperty, AngleProperty, NormalizedAngleProperty, RESTRICT_NONNEGATIVE, AngleProperty, PositiveNumberProperty, NonNegativeNumberProperty
from ipcore.properties.descriptor import DefinitionProperty
from ipcore.properties.restrictions import RestrictRange
from ...technology.settings import TECH

from ..coord import Coord2, Coord2Property, Size2Property

__all__ = ["ShapeArc",
           "ShapeBend",
           "ShapeBendRelative",
           "ShapeCircle",
           "ShapeCross",
           "ShapeDodecagon",
           "ShapeEllipse",
           "ShapeEllipseArc",
           "ShapeHexagon",
           "ShapeParabolic",
           "ShapeRadialWedge",
           "ShapeRectangle",
           "ShapeRegularPolygon",
           "ShapeRingSegment",
           "ShapeRoundedRectangle",
           "ShapeRoundedRectangleArc",
           "ShapeWedge"]

def wrap_kwargs(kwargs_dict, **kwargs):
    for kwa_k, kwa_v in kwargs.items():
        kwargs_dict[kwa_k] = kwa_v
    return kwargs_dict

#----------------------------------------------------------------------------
# ellipses, circles and arcs
#----------------------------------------------------------------------------

class ShapeEllipseArc(Shape):
    """ ellipse arc around a given center """
    center = Coord2Property(default = (0.0, 0.0))
    box_size = Size2Property(default = (1.0, 1.0))
    start_angle = AngleProperty(default = 0.0)
    end_angle = AngleProperty(default = 90.0)
    angle_step = AngleProperty(default = TECH.METRICS.ANGLE_STEP)
    clockwise = BoolProperty(default = False)
    
    def __init__(self, **kwargs):
        super(ShapeEllipseArc, self).__init__(**kwargs)

    def define_points(self, pts):
        sa = self.start_angle * DEG2RAD
        ea = self.end_angle * DEG2RAD 
        h_radius = self.box_size[0] / 2.0
        v_radius = self.box_size[1] / 2.0
        n_s = float(self.end_angle - self.start_angle) / self.angle_step
        n_steps = int(math.ceil(abs(n_s))) * numpy.sign(n_s)
        if n_steps == 0: 
            if sa == ea:
                pts = numpy.array([[math.cos(sa) * h_radius + self.center[0], math.sin(sa) * v_radius + self.center[1]]
                                               ])
            else:		
                pts = numpy.array([[math.cos(sa) * h_radius + self.center[0], math.sin(sa) * v_radius + self.center[1]],
                                               [math.cos(ea) * h_radius + self.center[0], math.sin(ea) * v_radius + self.center[1]]
                                               ])
            return pts

        angle_step = float(ea - sa) / n_steps
        if self.clockwise:
            angle_step = -angle_step
            sign = -1
        else:
            sign = +1
        while sign * sa > sign * ea:
            ea += sign * 2 * math.pi

        angles = numpy.arange(sa, ea + 0.5 * angle_step, angle_step)
        pts = numpy.column_stack((numpy.cos(angles), numpy.sin(angles))) * numpy.array([(h_radius, v_radius)]) + numpy.array([(self.center[0], self.center[1])])
        return pts

    def move(self, position):
        self.center = (self.center.x + position[0], self.center.y + position[1])
        return self

    def is_empty(self):
        return self.start_angle == self.end_angle or self.box_size[0] == 0.0 or self.box_size[1] == 0.0


class ShapeArc(ShapeEllipseArc):
    """ circular arc """
    radius = PositiveNumberProperty(default = 1.0)
    box_size = DefinitionProperty(fdef_name = "define_box_size")

    def __init__(self, **kwargs):
        ShapeEllipseArc.__init__(self, **kwargs)  # super gives error -- why? FIXME

    def define_box_size(self):
        bs = Coord2(2 * self.radius, 2 * self.radius)
        return bs


class ShapeBend(ShapeArc):
    """ bend: circular arc but specified by its starting point insetad of center """
    start_point = Coord2Property(default = (0.0, 0.0))
    center = DefinitionProperty(fdef_name = "define_center")
    start_angle = DefinitionProperty(fdef_name = "define_start_angle")
    end_angle = DefinitionProperty(fdef_name = "define_end_angle")
    input_angle = AngleProperty(default = 0.0)
    output_angle = AngleProperty(default = 90.0)

    def __init__(self, **kwargs):
        super(ShapeBend, self).__init__(**kwargs)
        
    def __get_sign(self):
        if self.clockwise:
            sign = -1
        else:
            sign = 1
        return sign
        
    def define_center(self):
        sign = self.__get_sign()
        c = (self.start_point[0] - sign * self.radius * math.sin(self.input_angle * DEG2RAD), self.start_point[1] + sign * self.radius * math.cos(self.input_angle * DEG2RAD))        
        return c
        
    def define_start_angle(self):
        sign = self.__get_sign()        
        a = self.input_angle - sign * 90.0
        return a
        
    def define_end_angle(self):
        sign = self.__get_sign()        
        a = self.output_angle - sign * 90.0
        return a
    
    def move(self, position):
        self.start_point = Coord2(self.start_point[0] + position[0], self.start_point[1] + position[1])
        return self
    
    
def ShapeBendRelative(start_point = (0.0, 0.0), 
                      radius = 1.0, 
                      input_angle=0.0, 
                      angle_amount = 90.0,
                      angle_step = TECH.METRICS.ANGLE_STEP):
    """ relative bend: bend with relative turning angle instead of absolute end angle """
    clockwise = bool(angle_amount < 0)
    return ShapeBend(start_point = start_point, radius = radius, input_angle = input_angle, output_angle = input_angle + angle_amount, clockwise = clockwise, angle_step = angle_step)

class ShapeEllipse(ShapeEllipseArc):
    """ ellipse """
    start_angle = DefinitionProperty(fdef_name = "define_start_angle")
    end_angle = DefinitionProperty(fdef_name = "define_end_angle")
    
    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeEllipse, self).__init__(**kwargs)

    def define_start_angle(self):
        sa = 0.0
        return sa

    def define_end_angle(self):   
        ea = self.start_angle + 360.0
        return ea
        
    def define_points(self, pts):
        pts = super(ShapeEllipse, self).define_points(pts)
        return pts


class ShapeCircle(ShapeArc, ShapeEllipse):
    """ circle """

    def __init__(self,  **kwargs):
        kwargs["closed"] = True
        super(ShapeCircle, self).__init__(**kwargs)

    def define_points(self, pts):
        pts = super(ShapeCircle, self).define_points(pts)
        return pts


#----------------------------------------------------------------------------
# (rounded) rectangles and squares
#----------------------------------------------------------------------------

class ShapeRoundedRectangle(Shape):
    """ rectangle with rounded corners """
    center = Coord2Property(default = (0.0, 0.0))
    box_size = Size2Property(default = (1.0, 1.0))
    radius = NonNegativeNumberProperty(default = 1.0)
    angle_step = AngleProperty(default = TECH.METRICS.ANGLE_STEP)
    
    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeRoundedRectangle, self).__init__(**kwargs)

    def define_points(self, pts):
        cx = self.center[0]
        cy = self.center[1]
        dx = 0.5 * self.box_size[0]
        dy = 0.5 * self.box_size[1]

        if self.radius <= 0:
            pts += [(cx + dx, cy + dy),
                    (cx - dx, cy + dy),
                    (cx - dx, cy - dy),
                    (cx + dx, cy - dy),
                    (cx + dx, cy + dy)]
        else:
            if self.radius > min(self.box_size) / 2.0:
                self.radius = min(self.box_size) / 2.0

            if (self.radius == self.box_size[0] / 2.0) and (self.radius == self.box_size[1] / 2.0):
                pts += ShapeCircle(center = self.center, radius = self.radius, angle_step = self.angle_step)
            elif self.radius == self.box_size[0] / 2.0:
                pts += ShapeArc(center = (cx, cy + dy - self.radius), radius = self.radius, start_angle = 0.0, end_angle = 180.0, angle_step = self.angle_step)
                pts += ShapeArc(center = (cx, cy - dy + self.radius), radius = self.radius, start_angle = 180.0, end_angle = 360.0, angle_step = self.angle_step)
            elif self.radius == self.box_size[1] / 2.0:
                pts += ShapeArc(center = (cx + dx - self.radius, cy), radius = self.radius, start_angle =270, end_angle =450.0, angle_step = self.angle_step)
                pts += ShapeArc(center = (cx - dx + self.radius, cy), radius = self.radius, start_angle =90.0, end_angle =270.0, angle_step = self.angle_step)
            else: 
                pts += ShapeArc(center = (cx + dx - self.radius, cy + dy - self.radius), radius = self.radius, start_angle =0.0, end_angle =90.0, angle_step = self.angle_step)
                pts += ShapeArc(center = (cx - dx + self.radius, cy + dy - self.radius), radius = self.radius, start_angle =90.0, end_angle =180.0, angle_step = self.angle_step)
                pts += ShapeArc(center = (cx - dx + self.radius, cy - dy + self.radius), radius = self.radius, start_angle =180.0, end_angle =270.0, angle_step = self.angle_step)
                pts += ShapeArc(center = (cx + dx - self.radius, cy - dy + self.radius), radius = self.radius, start_angle =270.0, end_angle =360.0, angle_step = self.angle_step)
        return pts


    def move(self, position):
        self.center = Coord2(self.center[0] + position[0], self.center[1] + position[1])
        return self

    def is_empty(self):
        return self.box_size[0] == 0.0 or self.box_size[1] == 0.0


class ShapeRectangle(ShapeRoundedRectangle):
    """ rectangle """
    radius = DefinitionProperty(fdef_name = "define_radius")
    
    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeRectangle, self).__init__(**kwargs)

    def define_radius(self):
        return 0.0
        
    def define_points(self, pts):
        # overloaded for speed
        cx = self.center[0]
        cy = self.center[1]
        dx = 0.5 * self.box_size[0]
        dy = 0.5 * self.box_size[1]
        pts = [(cx + dx, cy + dy),
                       (cx - dx, cy + dy),
                       (cx - dx, cy - dy),
                       (cx + dx, cy - dy)]
        return pts
    

class ShapeRoundedRectangleArc(Shape):
    center = Coord2Property(default = (0.0, 0.0))
    box_size = Size2Property(default = (1.0, 1.0))
    radius = PositiveNumberProperty(default = 0.1)
    start_angle = AngleProperty(default = 0.0)
    end_angle = AngleProperty(default = 90.0)
    angle_step = AngleProperty(default = TECH.METRICS.ANGLE_STEP)
    clockwise = BoolProperty(default = False)
    
    def __init__(self, **kwargs):
        super(ShapeRoundedRectangleArc, self).__init__(**kwargs)
        # restrict radius
        if self.radius > min(self.box_size) / 2.0:
            self.radius = min(self.box_size) / 2.0            
        
    def define_points(self, pts):
        cx = self.center[0]
        cy = self.center[1]
        dx = 0.5 * self.box_size[0]
        dy = 0.5 * self.box_size[1]
        if self.clockwise:
            as_sign = -1
        else:
            as_sign = 1
        # radius = box: circle arc
        if (self.radius == self.box_size[0] / 2.0) and (self.radius == self.box_size[1] / 2.0):
            pts += ShapeArc(self.center, self.radius, self.start_angle, self.end_angle, angle_step = self.angle_step, clockwise = self.clockwise)
        # radius = zero: part of rectangle
        elif self.radius <= 0:
            for a in arange(self.start_angle, self.end_angle + 45.0, as_sign * 90.0):
                pts += [(cx + sign(math.cos(DEG2RAD * a)) * dx, cy + sign(math.sin(DEG2RAD * a)) * dy)]
        # arbitrary
        else:
            for a in numpy.arange(self.start_angle, self.end_angle + 45.0, as_sign * 90.0):
                start = max(self.start_angle, a - a % 90.0 + 45.0 - as_sign * 45.0)
                end = min(self.end_angle, a - a % 90.0 + 45.0 + as_sign * 45.0)
                pts += ShapeArc(center = (cx + numpy.sign(math.cos(DEG2RAD * a)) * (dx - self.radius), cy + numpy.sign(math.sin(DEG2RAD * a)) * (dy - self.radius)), radius = self.radius, start_angle = start, end_angle = end, angle_step = self.angle_step, clockwise =self.clockwise)
        return pts

           

class ShapeRegularPolygon(Shape):
    """ regular N-sided polygon """
    center = Coord2Property(default = (0.0, 0.0))
    radius = PositiveNumberProperty(default = 1.0)
    n_o_sides = IntProperty(default = 8, restriction = RestrictRange(lower = 3))
    
    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeRegularPolygon, self).__init__(**kwargs)

    def define_points(self, pts):
        if self.radius == 0.0: 
            pts.append(self.center)
            return pts
        angle_step = 2 * math.pi / self.n_o_sides
        for i in xrange(0, self.n_o_sides):
            pts.append((self.center[0] + self.radius * math.cos((i + 0.5) * angle_step + math.pi / 2),
                        self.center[1] + self.radius * math.sin((i + 0.5) * angle_step + math.pi / 2)))
        return pts

    def move(self, position):
        self.center = Coord2(self.center[0] + position[0], self.center[1] + position[1])
        return self

    def is_empty(self):
        return (self.radius == 0.0)
    


class ShapeWedge(Shape):
    """ wedge, or symmetric trapezium. specified by the center of baselines and the length of the baselines """
    begin_coord = Coord2Property(default = (0.0, 0.0))
    end_coord = Coord2Property(default = (10.0, 0.0))
    begin_width = NonNegativeNumberProperty(default = 3.0)
    end_width = NonNegativeNumberProperty(default = 1.0)
    
    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeWedge, self).__init__(**kwargs)

    def define_points(self, pts):
        dist = distance(self.end_coord, self.begin_coord)
        cosangle = (self.end_coord[0] - self.begin_coord[0]) / dist
        sinangle = (self.end_coord[1] - self.begin_coord[1]) / dist
        pts = [(self.begin_coord[0] + sinangle * self.begin_width / 2.0, self.begin_coord[1] - cosangle * self.begin_width / 2.0),
               (self.begin_coord[0] - sinangle * self.begin_width / 2.0, self.begin_coord[1] + cosangle * self.begin_width / 2.0),
               (self.end_coord[0] - sinangle * self.end_width / 2.0, self.end_coord[1] + cosangle * self.end_width / 2.0),
               (self.end_coord[0] + sinangle * self.end_width / 2.0, self.end_coord[1] - cosangle * self.end_width / 2.0)]
        return pts

    def move(self, position):
        self.begin_coord = (self.begin_coord[0] + position[0], self.begin_coord[1] + position[1])
        self.end_coord = (self.end_coord[0] + position[0], self.end_coord[1] + position[1])
        return self

    def is_empty(self):
        return self.begin_coord == self.end_coord
    

class ShapeRadialWedge(Shape):
    """ radial wedge: the coordinates of the start and end point are specified in polar coordinates
        from a given center """
    center = Coord2Property(default = (0.0, 0.0))
    inner_radius = PositiveNumberProperty(required = True)
    outer_radius = PositiveNumberProperty(required = True)
    inner_width = PositiveNumberProperty(required = True)
    outer_width = PositiveNumberProperty(required = True)
    angle = NormalizedAngleProperty(required = True)
    
    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeRadialWedge, self).__init__(**kwargs)

    def define_points(self, pts):
        cosangle = math.cos(self.angle * DEG2RAD)
        sinangle = math.sin(self.angle * DEG2RAD)
        bc = (self.center[0] + self.inner_radius * math.cos(self.angle * DEG2RAD), self.center[1] + self.inner_radius * math.sin(self.angle * DEG2RAD))
        ec = (self.center[0] + self.outer_radius * math.cos(self.angle * DEG2RAD), self.center[1] + self.outer_radius * math.sin(self.angle * DEG2RAD))
        pts += [(bc[0] + sinangle * self.inner_width / 2.0, bc[1] - cosangle * self.inner_width / 2.0),
                (bc[0] - sinangle * self.inner_width / 2.0, bc[1] + cosangle * self.inner_width / 2.0),
                (ec[0] - sinangle * self.outer_width / 2.0, ec[1] + cosangle * self.outer_width / 2.0),
                (ec[0] + sinangle * self.outer_width / 2.0, ec[1] - cosangle * self.outer_width / 2.0)]
        return pts

    def move(self, position):
        self.center = (self.center[0] + position[0], self.center[1] + position[1])
        return self

    def is_empty(self):
        return self.inner_radius == self.outer_radius


class ShapeParabolic(Shape):
    """ parabolic wedge (taper) """
    begin_coord = Coord2Property(default=(0.0, 0.0))
    end_coord = Coord2Property(default=(0.0, 0.0))
    begin_width = NonNegativeNumberProperty(default=3.0)
    end_width = NonNegativeNumberProperty(default=1.0)
    
    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeParabolic, self).__init__(**kwargs)

    def define_points(self, pts):
        if (self.begin_width > self.end_width):
            ew = self.begin_width
            ec = self.begin_coord
            bw = self.end_width
            bc = self.end_coord
        else:
            bw = self.begin_width
            bc = self.begin_coord
            ew = self.end_width
            ec = self.end_coord

        length = distance(ec, bc)
        angle = angle_rad(ec, bc)
        sinangle = math.sin(angle)
        cosangle = math.cos(angle)

        dx = 0.01

        if abs(ew - bw) < dx:
            pts.extend([(bc[0] + sinangle * bw / 2.0, bc[1] - cosangle * bw / 2.0),
                        (bc[0] - sinangle * bw / 2.0, bc[1] + cosangle * bw / 2.0),
                        (ec[0] - sinangle * bw / 2.0, ec[1] + cosangle * ew / 2.0),
                        (ec[0] + sinangle * bw / 2.0, ec[1] - cosangle * ew / 2.0),
                        (bc[0] + sinangle * bw / 2.0, bc[1] - cosangle * bw / 2.0)])
            return pts

        if length < 0.0025:
            return pts

        a = 4.0 * length / (ew ** 2 - bw ** 2)
        y0 = a * bw ** 2 / 4.0
        y = y0
        width = bw

        east_shape = [(bc[0] + sinangle * bw / 2.0, bc[1] - cosangle * bw / 2.0)]
        west_shape = [(bc[0] - sinangle * bw / 2.0, bc[1] + cosangle * bw / 2.0)]

        READY = False
        while (not READY):
            width = width + 4 * dx + 4 * math.sqrt(dx * (width + dx))
            y = a * width ** 2 / 4.0

            if (y - y0 > length):
                READY = True
                coord = ec
                width = ew
            else:
                coord = (bc[0] + (y - y0) * cosangle, bc[1] + (y - y0) * sinangle)

            east_shape.append((coord[0] + sinangle * width / 2.0, coord[1] - cosangle * width / 2.0))
            west_shape.append((coord[0] - sinangle * width / 2.0, coord[1] + cosangle * width / 2.0))

        east_shape.reverse()
        pts += west_shape
        pts += east_shape
        return pts

    def move(self, position):
        self.begin_coord = (self.begin_coord[0] + position[0], self.begin_coord[1] + position[1])
        self.end_coord = (self.end_coord[0] + position[0], self.end_coord[1] + position[1])
        return self

    def is_empty(self):
        return self.begin_coord == self.end_coord
    
    
class ShapeRingSegment(Shape):
    """ ring segment """
    center = Coord2Property(default = (0.0, 0.0))
    angle_start = AngleProperty(default = 0.0)
    angle_end = AngleProperty(default = 90.0)
    inner_radius = PositiveNumberProperty(required = True)
    outer_radius = PositiveNumberProperty(required = True)
    angle_step = AngleProperty(default  = TECH.METRICS.ANGLE_STEP)

    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeRingSegment, self).__init__(**kwargs)

    def define_points(self, pts):
        arc1 = ShapeArc(center = self.center, radius = self.inner_radius, start_angle = self.angle_start, end_angle = self.angle_end, angle_step = self.angle_step)
        Shape.reverse(arc1) # do not destroy dynamism
        arc2 = ShapeArc(center = self.center, radius = self.outer_radius, start_angle = self.angle_start, end_angle = self.angle_end, angle_step = self.angle_step)
        pts += arc1
        pts += arc2
        return pts

    def move(self, position):
        self.center = (self.center[0] + position[0], self.center[1] + position[1])
        return self

    def is_empty(self):
        return self.inner_radius == self.outer_radius or self.angle_start == self.angle_end    
    
    
class ShapeHexagon(ShapeRegularPolygon):
    """ hexagon """
    n_o_sides = IntProperty(default = 6, restriction = RestrictRange(lower = 3))
    

class ShapeDodecagon(ShapeRegularPolygon):
    """ dodecagon """
    n_o_sides = IntProperty(default = 12, restriction = RestrictRange(lower = 3))
        

class ShapeCross(Shape):
    """ cross. thickness sets the width of the arms """
    center = Coord2Property(default = (0.0, 0.0))
    box_size = PositiveNumberProperty(default = 20.0)
    thickness = PositiveNumberProperty(default = 5.0)
    def __init__(self, **kwargs):
        kwargs["closed"] = True
        super(ShapeCross, self).__init__(**kwargs)

    def define_points(self, pts):  
        pts += [(self.center[0]  - self.box_size / 2.0, self.center[1] - self.thickness / 2.0),
                (self.center[0] - self.box_size / 2.0, self.center[1] + self.thickness / 2.0),
                (self.center[0] - self.thickness / 2.0, self.center[1] + self.thickness / 2.0),
                (self.center[0] - self.thickness / 2.0, self.center[1] + self.box_size / 2.0),
                (self.center[0] + self.thickness / 2.0, self.center[1] + self.box_size / 2.0),
                (self.center[0] + self.thickness / 2.0, self.center[1] + self.thickness / 2.0),
                (self.center[0] + self.box_size / 2.0, self.center[1] + self.thickness / 2.0),
                (self.center[0] + self.box_size / 2.0, self.center[1] - self.thickness / 2.0),
                (self.center[0] + self.thickness / 2.0, self.center[1] - self.thickness / 2.0),
                (self.center[0] + self.thickness / 2.0, self.center[1] - self.box_size / 2.0),
                (self.center[0] - self.thickness / 2.0, self.center[1] - self.box_size / 2.0),
                (self.center[0] - self.thickness / 2.0, self.center[1] - self.thickness / 2.0),
                (self.center[0] - self.box_size / 2.0, self.center[1] - self.thickness / 2.0)]
        return pts

    def move(self, position):
        self.center = Coord2(self.center[0] + position[0], self.center[1] + position[1])
        return self

    def is_empty(self):
        return self.box_size == 0.0 or self.thickness == 0.0
    

    
