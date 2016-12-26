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

from ipcore.properties.predefined import PositiveNumberProperty, AngleProperty, PositiveNumberProperty, NonNegativeNumberProperty, RESTRICT_NONNEGATIVE
from ipcore.properties.restrictions import RestrictList
from ipcore.properties.descriptor import LockedProperty, RestrictedProperty 
from ipkiss.geometry.shape import Shape
from ipkiss.geometry.shapes.basic import ShapeBendRelative
from ipkiss.geometry.shape_modifier import __ShapeModifier__
from ipkiss.geometry.coord import Coord2Property, Coord2
from ipkiss.geometry.shape_info import turn_deg, angle_deg
from ipkiss.geometry.line import straight_line_from_point_angle
import ipkiss.geometry.transforms.mirror 
from ipkiss.settings import get_grids_per_unit
from ipkiss.constants import DEG2RAD
from .curves import ShapeBezier

import numpy
import math

from ipkiss.technology import get_technology
from ipkiss.log import IPKISS_LOG as LOG


__all__ = ["OneEndedNaturalSpline",
           "AdiabaticSplineCircleSplineShape",
           "ShapeRoundAdiabaticSplineGeneric",
           "ShapeRoundAdiabaticSpline",
           "SplineRoundingAlgorithm"
           ]

TECH = get_technology()

class OneEndedNaturalSpline(Shape):
    radius = PositiveNumberProperty(required = True)
    angle = AngleProperty(required = True)
    angle_step = AngleProperty(default  = TECH.METRICS.ANGLE_STEP)
    def define_points(self,pts):
        alpha = self.angle * DEG2RAD
        c = math.sin(alpha)
        if self.angle == 45.0:
            t = 0.5
        else:
            c2 = c**2
            t = math.sin(math.atan(((1.0-c2)/c2)**0.125))**2
            
        a2 = (1-t)**2 * (t**4 + (1-t)**4)
    
        L = self.radius * 2 * t * (1-t) / (3* (t**4 + (1-t)**4)**1.5) # characteristic length of the full natural spline of a right angle
        
        # control points of full natural spline (right angle)
        q0_0 = Coord2(-L, 0)
        q0_1 = Coord2(0,0)
        q0_2 = Coord2(0,0)
        q0_3 = Coord2(0, L)
        
        # control points of first section of the spline
        q1_0 = t * q0_0 + (1-t) * q0_1
        q2_0 = t**2 * q0_0 + 2*t*(1-t) * q0_1 + (1-t)**2 * q0_2
        q3_0 = t**3 * q0_0 + 3*t**2*(1-t) * q0_1 + 3 * t * (1-t)**2 * q0_2 + (1-t)**3 * q0_3
    
        
        S_control = Shape(points = [q0_0, q1_0, q2_0, q3_0])    

        steps = int(math.ceil(2.0* self.angle / self.angle_step))
        return ShapeBezier(original_shape = S_control, steps = steps).points # add angle step as a parameter

class AdiabaticSplineCircleSplineShape(Shape):
    start_point = Coord2Property(required = True)
    turn_point = Coord2Property(required = True)
    end_point = Coord2Property(required = True)
    
    radius = PositiveNumberProperty(required = True)
    adiabatic_angles = RestrictedProperty(allow_none = True, doc = "tuple of adiabatic transistion angles for input and output")
    angle_step = AngleProperty(default = TECH.METRICS.ANGLE_STEP)
    
    def define_points(self,pts):
        alpha_in = self.adiabatic_angles[0]
        alpha_out = self.adiabatic_angles[1]
        turn_angle = turn_deg(self.start_point, self.turn_point, self.end_point)
        
        if (alpha_in + alpha_out) > abs(turn_angle):
            alpha_in = alpha_out = 0.5 * abs(turn_angle)
    
        bend_angle = abs(turn_angle) - alpha_in-alpha_out
        
        # first section
        if alpha_in > 0.0:
            S5 = OneEndedNaturalSpline(radius = self.radius, angle = alpha_in, angle_step = self.angle_step)
        else:
            S5 = Shape((- self.radius, 0))
    
        # middle section
        if bend_angle > 0.0:
            S5 += ShapeBendRelative(start_point = S5[-1],
                                    input_angle = alpha_in,
                                    angle_amount = bend_angle,
                                    radius = self.radius,
                                    angle_step = self.angle_step,
                                    )
            
        # last section
        if alpha_out > 0.0:
            S6 = Shape(OneEndedNaturalSpline(radius = self.radius, angle = alpha_out, angle_step = self.angle_step))
        else:
            S6 = Shape((-self.radius, 0))
        S6.h_mirror()
        S6.rotate((0, 0), abs(turn_angle))
        S6.reverse()
        S6.move(S5[-1] - S6[0])
        
        # transform to match the right position
        
        S = S5 + S6
        
        if turn_angle < 0:
            S.v_mirror()
    
        L = straight_line_from_point_angle((0.0,0.0), turn_angle)
        d = L.distance(S[-1])
    
        ep = S[-1]
        if abs(turn_angle) == 90.0:
            d = ep.x
        else:
            d = ep.x - ep.y*math.cos(turn_angle * DEG2RAD)/ math.sin(turn_angle*DEG2RAD)
        
        S.move((-d, 0.0))
        S.rotate((0.0,0.0), angle_deg(self.turn_point, self.start_point))
        S.move(self.turn_point)
        S.remove_identicals()
        
        return S.points
        

class ShapeRoundAdiabaticSplineGeneric(__ShapeModifier__):
    """ returns a shape with adiabatic spline corners """
    radii = RestrictedProperty(restriction = RestrictList(restriction = RESTRICT_NONNEGATIVE), required = True)
    adiabatic_angles_list = RestrictedProperty(required = True)
    angle_step = AngleProperty(default = TECH.METRICS.ANGLE_STEP)
    
    def __original_shape_without_straight_angles__(self):
        S1 = Shape(self.original_shape)
        S = Shape(S1).remove_straight_angles()
        straight = (numpy.abs(numpy.abs((S1.turns_rad()+(0.5*numpy.pi))%numpy.pi)-0.5*numpy.pi) < 0.00001)
        if not S1.closed:
            straight[0] = False
            straight[-1]= False
        R = numpy.delete(self.radii, straight.nonzero()[0], 0)
        A = numpy.delete(self.adiabatic_angles_list, straight.nonzero()[0], 0)
        return (S,R,A)
    
    def define_points(self,pts):
        
        (s, R, A) = self.__original_shape_without_straight_angles__()        

        if len(R) != len(s): 
            raise AttributeError("ShapeRoundAdiabaticSplineGeneric: length of radius vector should be identical to that of points in shape")
        if len(A) != len(s): 
            raise AttributeError("ShapeRoundAdiabaticSplineGeneric: length of adiabatic_angles vector should be identical to that of points in shape")

        if len(s) < 3: 
            self.__points__ = s.points
            return
        margin = 0.5/get_grids_per_unit()
        
        S = []
        
        if not self.original_shape.closed:
            S.append(numpy.array([s.points[0]]))
        L1 = 0.0

        for i in range(1, len(s)-1):
            sh = AdiabaticSplineCircleSplineShape(start_point = s[i-1], turn_point = s[i], end_point = s[i+1],
                                                  radius = R[i], adiabatic_angles = A[i],
                                                  angle_step = self.angle_step)
            L0 = sh[0].distance(s[i])
            if L0 + L1-margin > s[i-1].distance(s[i]):
                LOG.warning("Insufficient space for spline rounding in (%f, %f)" % (s[i].x, s[i].y))
            L1 = sh[-1].distance(s[i])
            S.append(sh.points)

        if self.original_shape.closed:
            sh = AdiabaticSplineCircleSplineShape(start_point = s[-2], turn_point = s[-1], end_point = s[0],
                                                  radius = R[-1], 
                                                  adiabatic_angles = A[-1],
                                                  angle_step = self.angle_step)
            L0 = sh[0].distance(s[-1])
            if L0 + L1 -margin> s[-2].distance(s[-1]):
                LOG.warning("Insufficient space for spline rounding in (%f, %f)" % (s[-1].x, s[-1].y))
            L1 = sh[-1].distance(s[-1])
            S.append(sh.points)
            sh = AdiabaticSplineCircleSplineShape(start_point = s[-1], turn_point = s[0], end_point = s[1],
                                                  radius = R[0], 
                                                  adiabatic_angles = A[0],
                                                  angle_step = self.angle_step)
            L0 = sh[0].distance(s[0])
            if L0 + L1 -margin> s[-1].distance(s[0]):
                LOG.warning("Insufficient space for spline rounding in (%f, %f)" % (s[0].x, s[0].y))
            L1 = sh[-1].distance(s[0])
            S.append(sh.points)
            self.__closed__ = True
        else:
            # open curve
            S.append(numpy.array([s.points[-1]]))
            L0 = 0.0
            if L0 + L1-margin > s[-2].distance(s[-1]):
                LOG.warning("Insufficient space for spline rounding in (%f, %f)" % (s[-1].x, s[-1].y))
            L1 = sh[-1].distance(s[0])
            self.__closed__ = False
        return numpy.vstack(S)
        
class ShapeRoundAdiabaticSpline(ShapeRoundAdiabaticSplineGeneric):
    """ returns a shape with adiabatic spline corners """
    adiabatic_angles_list = LockedProperty()
    adiabatic_angles = RestrictedProperty(default=(0.0,0.0))
    radii = LockedProperty()
    radius = NonNegativeNumberProperty(required = True)
        
    def define_radii(self):
        return numpy.ones(len(self.original_shape)) * self.radius
    
    def define_adiabatic_angles_list(self):
        return [self.adiabatic_angles for i in range(len(self.original_shape))]


from functools import partial

def SplineRoundingAlgorithm(adiabatic_angles = (0.0, 0.0)):
    return partial(ShapeRoundAdiabaticSpline,adiabatic_angles =adiabatic_angles)        



