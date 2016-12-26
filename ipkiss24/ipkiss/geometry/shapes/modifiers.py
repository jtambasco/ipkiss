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

from ..shape import Shape, ShapeProperty
from ..shape_modifier import __ShapeModifier__
from ..coord import Coord2, Coord2Property
from .basic import ShapeBendRelative, ShapeArc
from ...constants import RAD2DEG, DEG2RAD
from ... import constants
from ..shape_info import distance, angle_rad, angle_deg
from ..size_info import SizeInfo
from ... import settings
from numpy import array, arange, roll, size, amax, amin, column_stack, sin, cos, vstack
from numpy import tan, abs, ones, flipud, sign, delete, hstack, cumsum
from math import pi, atan2
from ipcore.properties.predefined import AngleProperty, RESTRICT_NONNEGATIVE, RESTRICT_NUMBER, RESTRICT_POSITIVE 
from ipcore.properties.predefined import PositiveNumberProperty, NonNegativeNumberProperty, BoolProperty, AngleProperty, NumberProperty
from ipcore.properties.initializer import SUPPRESSED
from ipcore.properties.descriptor import RestrictedProperty, DefinitionProperty, LockedProperty, FunctionProperty
from ipcore.properties.restrictions import RestrictList, RestrictRange
from ipkiss.geometry.coord import Size2Property
from ipkiss.log import IPKISS_LOG as LOG
from ...technology.settings import TECH
import sys
from ipcore.exceptions.exc import *
from ipcore.caching.cache import cache

__all__ = ["ShapeExtendEnds",
           "ShapeGrow",
           "ShapeOffset",
           "ShapePath",
           "__ShapePathBase__",
           "ShapePathExtended",
           "ShapePathRounded",
           "ShapePathSimple",
           "ShapePathSpike",
           "ShapePathStub",
           "ShapeRound",
           "ShapeRoundGeneric",
           "ShapeSerif",
           "ShapeStub",
           "ShapeVariableOffset",
           "ShapeFit",
           "ShapeShorten",
           "ShapeSample",
           "ShapeSamplePeriodic",
           ]

class ShapeRoundGeneric(__ShapeModifier__):
    """ returns a shape with rounded corners based on a given shape """

    radii = DefinitionProperty(fdef_name = "define_radii")    
    original_shape = ShapeProperty(required = True)    
    angle_step = AngleProperty(default = TECH.METRICS.ANGLE_STEP)
            
    def define_radii(self):
        raise NotImplementedException("ShapeRoundGeneric is an abstract class : must implement 'define_radii' in subclass")
     
    def __original_shape_without_straight_angles__(self, shape, radii):
        S1 = Shape(shape)
        S = Shape(S1).remove_straight_angles()
        R = array(radii)
        straight = (abs(abs((S1.turns_rad() + (0.5 * pi)) % pi) - 0.5 * pi) < 0.00001)
        R = delete(radii, straight.nonzero()[0], 0)
        return (S, R)
        
    def define_points(self, pts):
        (Swsa, R) = self.__original_shape_without_straight_angles__(self.original_shape, self.radii)
        closed = Swsa.closed
        if len(self.radii) != len(Swsa): 
            raise IpcoreAttributeException("ShapeRoundGeneric: length of radius vector should be identical to that of points in shape")
        
        c = Swsa.points
        if len(c) == 0:
            return
        (r, tt, t, a1, a2, L, D) = self.__radii_and_turns__(Swsa)
        
        # create the bends
        Swsa = c - column_stack((L * cos(a1), L * sin(a1))) # bend start points (whereby we can ignore the 1st and last point for an open shape)

        S = []
        if not closed: 
            S.append(array([c[0]]))
        for i in range(1, len(c) - 1):  #ignore first and last point in matrix
            sh = ShapeBendRelative(Swsa[i], r[i], a1[i] * RAD2DEG, t[i] * RAD2DEG, self.angle_step)
            S.append(sh.points)

        if closed: #construct first and last bend in case the shape is closed
            sh = ShapeBendRelative(Swsa[-1], r[-1], a1[-1] * RAD2DEG, t[-1] * RAD2DEG, self.angle_step)
            S.append(sh.points)
            sh = ShapeBendRelative(Swsa[0], r[0], a1[0] * RAD2DEG, t[0] * RAD2DEG, self.angle_step)
            S.append(sh.points)
            self.closed = True
        else:
            # open curve
            S.append(array([c[-1]]))
            self.closed = False
        pts = vstack(S)
        return pts

    def __radii_and_turns__(self, s):
        R = self.radii
        r = array(R)
        D = s.distances()
        a2 = s.angles_rad() # angle to next vertex
        a1 = roll(a2, 1)   # angle from previous vertex
        t = (a2 - a1 + pi) % (2 * pi) - pi # turns, save an extra angle computation
        tt = abs(tan(0.5 * t))
        L = R * tt # length of the straight section consumed by the bend
        (Swsa, dummy) = self.__original_shape_without_straight_angles__(self.original_shape, self.radii)        
        if not Swsa.closed:
            L[0] = 0
            L[-1] = 0
        # check where the bend consumes more length than possible!
        m_L = ((L + roll(L, -1)) - D) # missing length in the next segment
        missing_L = amax(column_stack((m_L, roll(m_L, 1))), 1) # missing length over previous and next segment
        overf = (missing_L > 0.5 / settings.get_grids_per_unit())
        r[overf] = 0.5 * (amin(column_stack((D[overf], roll(D, 1)[overf])), 1)) / tt[overf]
        # FIXME: Find a more robust algorithm to reduce the radius if there is insufficient space
        r_difference = R - r 
        if (r_difference > settings.get_current_library().units_per_grid).any() : 
            LOG.warning("Bend radius is reduced by maximum %f to round shape." % max(r_difference))
        if not Swsa.closed:
            r[0] = 0
            r[-1] = 0
        L = r * tt # recompute the length of the straight section consumed by the bend
        return (r, tt, t, a1, a2, L, D)
        
    def length(self):
        import sys
        (Swsa, R) = self.__original_shape_without_straight_angles__(self.original_shape, self.radii)  
        (r, tt, t, a1, a2, L, D) = self.__radii_and_turns__(Swsa)
        L2 = sum(D) + sum(abs(t) * r - 2 * L)
        if not self.original_shape.closed:
            L2 -= D[-1]
        return L2
    
class ShapeRound(ShapeRoundGeneric):
    """ returns a shape with rounded corners based on a given shape """
    radius = NonNegativeNumberProperty(required = True)
    
      
    def define_radii(self):
        S1 = Shape(self.original_shape)
        S = Shape(S1).remove_straight_angles()        
        r = ones(len(S)) * self.radius
        return r
        
    def length(self):
        #self.radii = ones((len(self.original_shape))) * self.radius
        return super(ShapeRound, self).length()
        

class ShapeStub(__ShapeModifier__):
    """ stubs the corners of a given shape """
    stub_width = NonNegativeNumberProperty(required = True)
    only_sharp_angles = BoolProperty(default = False)
    

    def define_points(self, pts):
        c = Shape(self.original_shape)
        
        if len(c) == 0:
            return pts

        if self.original_shape.is_closed():
            if not c[0] == c[-1]:
                c.append(c[0])
            #closed curve
            c.append(c[1])
        else:
            # open curve
            pts.append(c[0])

        min_sw = self.stub_width
        for i in range(1, len(c) - 1):
            angle1 = angle_rad(c[i], c[i - 1])
            angle2 = angle_rad(c[i + 1], c[i])
            turn = (angle2 - angle1 + pi) % (2 * pi) - pi
            if turn == 0 or (abs(turn) <= (pi / 2.0) and self.only_sharp_angles):
                pts.append(c[i])
            elif abs(turn == pi):
                LOG.error("ShapeStub::define_points : ERROR : Cannot stub shape with a 180 degree turn")
            else:
                d1 = distance(c[i], c[i - 1])
                d2 = distance(c[i + 1], c[i])
                L = self.stub_width * sin(turn / 2.0) / sin(turn)
                max_L = max([d1 / 2.0, d2 / 2.0])
                if L > max_L:
                    L = max_L
                    sw = L * sin(turn) / sin(turn / 2.0)
                else:
                    sw = self.stub_width
                if sw < min_sw:
                    min_sw = sw

                s1 = (c[i][0] - L * cos(angle1), c[i][1] - L * sin(angle1))
                s2 = (c[i][0] + L * cos(angle2), c[i][1] + L * sin(angle2))
                pts.append(s1)
                pts.append(s2)
        ''' REFACTORED --> moved to constructor
        if self.original_shape.closed:
            #closed curve
            self.close()
        else:
        '''
        if not self.original_shape.closed:  # open curve
            pts.append(c[-1])

        if min_sw < self.stub_width:
            LOG.warning("Warning: ShapeStub::define_points : Stub width is reduced from " + str(self.stub_width) + " to " + str(min_sw) + "to stub shape.")

        return pts
    

class ShapeSerif(__ShapeModifier__):
    """ puts a bump on the corners of a given shape """
    stub_width = PositiveNumberProperty(required=True)
    stub_height = PositiveNumberProperty(required=True)
    tip_width = NonNegativeNumberProperty(required=True)
    only_sharp_angles = BoolProperty(default=False)
    
    def __init__(self, **kwargs):
        super(ShapeSerif, self).__init__(**kwargs)
        if self.original_shape.closed:
            self.close()        
        else:
            self.open()            
            
    def define_points(self, pts):
        c = Shape(self.original_shape)
        if len(c) == 0:
            return

        if self.original_shape.is_closed():
            if not c[0] == c[-1]:
                c.append(c[0])
            #closed curve
            c.append(c[1])
        else:
            # open curve
            pts.append(c[0])

        c.remove_identicals()

        min_sw = self.stub_width
        for i in range(1, len(c) - 1):
            angle1 = angle_rad(c[i], c[i - 1])
            angle2 = angle_rad(c[i + 1], c[i])
            turn = (angle2 - angle1 + pi) % (2 * pi) - pi
            if turn == 0 or (abs(turn) <= (pi / 2.0) and self.only_sharp_angles):
                pts.append(c[i])
            elif abs(turn == pi):
                LOG.error("Cannot stub shape with a 180 degree turn")
            else:
                d1 = distance(c[i], c[i - 1])
                d2 = distance(c[i + 1], c[i])
                L = self.stub_width * sin(turn / 2.0) / sin(turn)
                max_L = max([d1 / 2.0, d2 / 2.0])
                if L > max_L:
                    L = max_L
                    sw = L * sin(turn) / sin(turn / 2.0)
                else:
                    sw = self.stub_width
                if sw < min_sw:
                    min_sw = sw

                theta_div2 = (pi - angle1 + angle2) % (2 * pi) / 2.0

                s1 = Coord2(c[i][0] - L * cos(angle1), c[i][1] - L * sin(angle1))
                s2 = (c[i][0] + L * cos(angle2), c[i][1] + L * sin(angle2))

                B = -self.stub_height * sign(turn)
                delta = 0.5 * (self.stub_width - self.tip_width)
                s2 = (s1[0] + B * cos(angle1 + theta_div2) + delta * cos(angle1 + theta_div2 - pi / 2.0),
                      s1[1] + B * sin(angle1 + theta_div2) + delta * sin(angle1 + theta_div2 - pi / 2.0))
                s4 = Coord2(c[i][0] + L * cos(angle2), c[i][1] + L * sin(angle2))
                s3 = (s4[0] + B * cos(angle2 + pi - theta_div2) + delta * cos(angle2 + pi - theta_div2 + pi / 2.0),
                      s4[1] + B * sin(angle2 + pi - theta_div2) + delta * sin(angle2 + pi - theta_div2 + pi / 2.0))
                pts.append(s1)
                pts.append(s2)
                pts.append(s3)
                pts.append(s4)
                
        if not self.original_shape.closed:        
            # open curve
            pts.append(c[-1])

        if min_sw < self.stub_width:
            LOG.warning("Stub width is reduced from " + str(self.stub_width) + " to " + str(min_sw) + "to stub shape.")

        return pts
    
class __ShapeStartEndAngle__(__ShapeModifier__):
    start_face_angle = DefinitionProperty(restriction = RESTRICT_NUMBER, fdef_name = "define_start_face_angle")
    end_face_angle = DefinitionProperty(restriction = RESTRICT_NUMBER, fdef_name = "define_end_face_angle")

    @cache()
    def __get_original_shape_without_straight_angles__(self):
        s = Shape(self.original_shape).remove_straight_angles()
        if self.original_shape.closed:
            if s[-1] != s[0]:
                s.append(s[0])
        return s
        
    def define_start_face_angle(self):
        s = self.__get_original_shape_without_straight_angles__()
        if not self.original_shape.start_face_angle is None:
            return self.original_shape.start_face_angle
        if len(s) > 1:
            return angle_deg(s[1], s[0])
        else:
            return 0.0

    def define_end_face_angle(self):
        s = self.__get_original_shape_without_straight_angles__()
        if not self.original_shape.end_face_angle is None:
            return self.original_shape.end_face_angle
        if len(s) > 1:
            return angle_deg(s[-1], s[-2])
        else:
            return 0.0

    @cache()
    def get_original_shape_angles_rad(self):
        s = self.__get_original_shape_without_straight_angles__()
        a = s.angles_rad()        
        if len(s) < 2:
            return a
        if not s.closed:
            a[0] = self.start_face_angle * DEG2RAD
            a[-1] = self.end_face_angle * DEG2RAD
        return a
    
    
            
class __ShapePathBase__(__ShapeStartEndAngle__):
    """ base class for path shapes"""
    path_width = PositiveNumberProperty(required = True)
    


class ShapePathSimple(__ShapePathBase__):
    """ simple path based on a centerline shape """

    def define_points(self, pts):
        original = self.__get_original_shape_without_straight_angles__()
        if len(original) <= 1: return

        a2 = original.angles_rad() * 0.5
        a1 = roll(a2, 1)

        if original.closed:
            a2[-1] = a2[0]
            a1[0] = a1[-1]
        else:
            a2[-1] = self.end_face_angle * DEG2RAD - a2[-2]
            a1[0] = self.start_face_angle * DEG2RAD - a1[1]
            

        a_plus = a2 + a1
        cos_a_min = cos(a2 - a1)
        offsets = column_stack((-sin(a_plus) / cos_a_min, cos(a_plus) / cos_a_min)) * (0.5 * self.path_width)

        # compute offsets from each point
        pts = vstack((original.points + offsets, flipud(original.points - offsets)))
        return pts


class ShapePathSpike(__ShapePathBase__):
    """ simple path based on a centerline shape,but with a sharp endpoint with a given angle """
    spike_angle = AngleProperty(restriction = RestrictRange(0.0, 180.0, False, True), default = 90.0)
    

    def define_points(self, pts):
        original = self.__get_original_shape_without_straight_angles__()
        if len(original) <= 1: return
        a = original.angles_rad() 
        a2 = a * 0.5
        a1 = roll(a2, 1)

        if original.closed:
            a2[-1] = a2[0]
            a1[0] = a1[-1]
        else:
            a2[-1] = self.end_face_angle * DEG2RAD - a2[-2]
            a1[0] = self.start_face_angle * DEG2RAD - a1[1]

        a_plus = a2 + a1
        cos_a_min = cos(a2 - a1)
        offsets = column_stack((-sin(a_plus) / cos_a_min, cos(a_plus) / cos_a_min)) * (0.5 * self.path_width)

        # spikes
        if not original.closed and self.spike_angle > 0 and self.spike_angle < 180.0:
            L = 0.5 * self.path_width / tan(self.spike_angle * constants.DEG2RAD * 0.5)
            start_spike = array([[original[0][0] - cos(a[0]) * L,  original[0][1] - sin(a[0]) * L]])
            end_spike = array([[original[-1][0] + cos(a[-2]) * L,  original[-1][1] + sin(a[-2]) * L]])
        else:
            start_spike = ndarray((0, 2))
            end_spike = ndarray((0, 2))

        pts = vstack((start_spike, original.points + offsets, end_spike, flipud(original.points - offsets)))
        return pts


class ShapePathRounded(__ShapePathBase__):
    """ path with rounded corners based on a centerline """
    

    def define_points(self, pts):
        # TODO: include start_face_angle and end_face_angle in the calculations
        west_coords = Shape()
        east_coords = Shape()

        coords = self.__get_original_shape_without_straight_angles__().points
        if len(coords) == 0:
            return
                 
        # begin
        x = coords[0][0]
        y = coords[0][1]
        angle = atan2(coords[1][1] - y, coords[1][0] - x)
        sa = sin(angle)
        ca = cos(angle)
        west_coords.extend(ShapeArc(center = (x, y), radius = self.path_width / 2.0,
                                    start_angle = (angle * RAD2DEG) + 270.0,
                                    end_angle = (angle * RAD2DEG) + 90.0,
                                    clockwise=True))

        #middle
        for i in range(1, len(coords) - 1):
            x = coords[i][0]
            y = coords[i][1]
            angle1 = atan2(y - coords[i - 1][1], x - coords[i - 1][0])
            angle2 = atan2(coords[i + 1][1] - y, coords[i + 1][0] - x)
            angle = angle1 + 0.5 * (angle2 - angle1 + pi) % (pi) - 0.5 * pi
            ca = cos(angle)
            sa = sin(angle)
            turn = (angle2 - angle1) % (2 * pi)
            if turn == pi:
                LOG.error("Path to Boundary conversion is not possible with paths that turn 180 degree at a node")
                raise SystemExit
            w = 0.5 * self.path_width / abs(cos(0.5 * turn))

            c_west = (x - w * sa, y + w * ca)
            c_east = (x + w * sa, y - w * ca)
            if turn < pi:
                # turn west
                west_coords.append(c_west)
                east_coords.extend(ShapeArc(center = c_west, radius = self.path_width,
                                            start_angle = (angle1 * RAD2DEG) - 90.0,
                                            end_angle = (angle2 * RAD2DEG) - 90.0,
                                            clockwise= False))
            else:
                # turn east
                west_coords.extend(ShapeArc(center = c_east, radius = self.path_width,
                                            start_angle = (angle1 * RAD2DEG) + 90.0,
                                            end_angle = (angle2 * RAD2DEG) + 90.0,
                                            clockwise= True))
                east_coords.append(c_east)

        #end
        x = coords[-1][0]
        y = coords[-1][1]
        angle = atan2(y - coords[-2][1], x - coords[-2][0])
        sa = sin(angle)
        ca = cos(angle)
        east_coords.extend(ShapeArc(center=(x, y), radius=self.path_width / 2.0,
                                    start_angle = (angle * RAD2DEG) - 90.0,
                                    end_angle = (angle * RAD2DEG) + 90.0))
        east_coords.reverse()
        pts.extend(west_coords) 
        pts.extend(east_coords)
        pts.append(west_coords[0])
        return pts
    

class ShapePathExtended(__ShapePathBase__):
    """ path with extended ends based on a centerline shape """
    def __init__(self, original_shape, path_width, **kwargs):
        super(ShapePathExtended, self).__init__(
            original_shape = original_shape,
            path_width = path_width,
            **kwargs)

    def define_points(self, pts):
        # TODO: include start_face_angle and end_face_angle in the calculations
        west_coords = Shape()
        east_coords = Shape()

        coords = self.__get_original_shape_without_straight_angles__().points
        if len(coords) == 0:
            return

        # begin
        x = coords[0][0]
        y = coords[0][1]
        angle = atan2(coords[1][1] - y, coords[1][0] - x)
        sa = sin(angle)
        ca = cos(angle)
        west_coords.append((x - 0.5 * self.path_width * (sa + ca), y + 0.5 * self.path_width * (ca - sa)))
        east_coords.append((x + 0.5 * self.path_width * (sa - ca), y - 0.5 * self.path_width * (ca + sa)))


        #middle
        for i in range(1, len(coords) - 1):
            x = coords[i][0]
            y = coords[i][1]
            angle1 = atan2(y - coords[i - 1][1], x - coords[i - 1][0])
            angle2 = atan2(coords[i + 1][1] - y, coords[i + 1][0] - x)
            angle = angle1 + 0.5 * (angle2 - angle1 + pi) % (pi) - 0.5 * pi
            ca = cos(angle)
            sa = sin(angle)
            turn = (angle2 - angle1) % (2 * pi)
            if turn == pi:
                LOG.error("Path to Boundary conversion is not possible with paths that turn 180 degree at a node")
                raise SystemExit
            w = 0.5 * self.path_width / abs(cos(0.5 * turn))

            c_west = (x - w * sa, y + w * ca)
            c_east = (x + w * sa, y - w * ca)
            west_coords.append(c_west)
            east_coords.append(c_east)

        #end
        x = coords[-1][0]
        y = coords[-1][1]
        angle = atan2(y - coords[-2][1], x - coords[-2][0])
        sa = sin(angle)
        ca = cos(angle)
        west_coords.append((x - 0.5 * self.path_width * (sa - ca), y + 0.5 * self.path_width * (ca + sa)))
        east_coords.append((x + 0.5 * self.path_width * (sa + ca), y - 0.5 * self.path_width * (ca - sa)))
        east_coords.reverse()
        pts.extend(west_coords)
        pts.extend(east_coords)
        pts.append(west_coords[0])
        return pts


class ShapePathStub(__ShapePathBase__):
    """ path with stubbed corners based on a centerline shape """
    
    stub_width = NonNegativeNumberProperty(default = 0.0)
    

    def define_points(self, pts):
        # TODO: include start_face_angle and end_face_angle in the calculations
        west_coords = Shape()
        east_coords = Shape()

        coords = self.__get_original_shape_without_straight_angles__().points
        if len(coords) == 0:
            return

        # begin
        x = coords[0][0]
        y = coords[0][1]
        angle = atan2(coords[1][1] - y, coords[1][0] - x)
        sa = sin(angle)
        ca = cos(angle)
        if self.start_face_angle is None:
            new_angle = angle
            turn = 0.0
        else:
            new_angle = self.start_face_angle * constants.DEG2RAD
            turn = 2 * (angle - new_angle) % (pi)
        w = 0.5 * self.path_width / abs(cos(turn / 2.0))
        west_coords.append((x - w * sin(new_angle), y + w * cos(new_angle)))
        east_coords.append((x + w * sin(new_angle), y - w * cos(new_angle)))

        #middle
        for i in range(1, len(coords) - 1):
            x = coords[i][0]
            y = coords[i][1]
            angle1 = atan2(y - coords[i - 1][1], x - coords[i - 1][0])
            angle2 = atan2(coords[i + 1][1] - y, coords[i + 1][0] - x)
            angle = angle1 + 0.5 * (angle2 - angle1 + pi) % (pi) - 0.5 * pi
            ca = cos(angle)
            sa = sin(angle)
            turn = (angle2 - angle1) % (2 * pi)
            if turn == pi:
                LOG.error("Path to Boundary conversion is not possible with paths that turn 180 degree at a node")
                raise SystemExit
            w = 0.5 * self.path_width / abs(cos(0.5 * turn))

            c_west = (x - w * sa, y + w * ca)
            c_east = (x + w * sa, y - w * ca)
            west_coords.append(c_west)
            east_coords.append(c_east)

        #end
        x = coords[-1][0]
        y = coords[-1][1]
        angle = atan2(y - coords[-2][1], x - coords[-2][0])
        sa = sin(angle)
        ca = cos(angle)
        if self.end_face_angle is None:
            new_angle = angle
            turn = 0.0
        else:
            new_angle = self.end_face_angle * constants.DEG2RAD
            turn = 2 * (new_angle - angle) % (pi)
        w = 0.5 * self.path_width / abs(cos(0.5 * turn))
        west_coords.append((x - w * sin(angle), y + w * cos(angle)))
        east_coords.append((x + w * sin(angle), y - w * cos(angle)))

        if (self.stub_width > 0):
            east_coords = ShapeStub(original_shape = east_coords, stub_width = self.stub_width)
            west_coords = ShapeStub(original_shape = west_coords, stub_width = self.stub_width)
        east_coords.reverse()
        pts.extend(west_coords)
        pts.extend(east_coords)
        pts.append(west_coords[0])
        return pts


def ShapePath(original_shape, path_width, path_type= constants.PATH_TYPE_NORMAL, stub_width = 0.0, **kwargs):
    """ path shape based on centerline """
    if stub_width != 0.0:
        return ShapePathStub(original_shape = original_shape, 
                             path_width = path_width, 
                             stub_width = 0.0,
                             **kwargs)
    elif path_type == constants.PATH_TYPE_NORMAL:
        return ShapePathSimple(original_shape = original_shape, 
                             path_width = path_width, 
                             **kwargs)
    elif path_type == constants.PATH_TYPE_EXTENDED:
        return ShapePathExtended(original_shape = original_shape, 
                             path_width = path_width, 
                             **kwargs)
    elif path_type == constants.PATH_TYPE_ROUNDED:
        return ShapePathRounded(original_shape = original_shape, 
                             path_width = path_width, 
                             **kwargs)
    raise IpcoreException("Invalid path type in ShapePath factory method")


    
class ShapeOffset(__ShapeStartEndAngle__):
    """ generates a shape with a given offset from its original shape"""
    offset = NumberProperty(required = True)    
    
    
    def __init__(self, original_shape, offset, **kwargs):
        super(ShapeOffset, self).__init__(
            original_shape = original_shape,
            offset = offset,
            **kwargs)

    def define_points(self, pts):
        original = self.__get_original_shape_without_straight_angles__()
        if len(original) <= 1: return

        a2 = original.angles_rad() * 0.5
        a1 = roll(a2, 1)

        if original.closed:
            a2[-1] = a2[0]
            a1[0] = a1[-1]
        else:
            a2[-1] = self.end_face_angle * DEG2RAD - a2[-2]
            a1[0] = self.start_face_angle * DEG2RAD - a1[1]

        a_plus = a2 + a1
        cos_a_min = cos(a2 - a1)
        offsets = column_stack((-sin(a_plus) / cos_a_min, cos(a_plus) / cos_a_min)) * (self.offset)

        # compute offsets from each point
        pts = (original.points + offsets)
        return pts

class ShapeGrow(__ShapeModifier__):
    """ generates a shape with uniformly grows """
    offset = DefinitionProperty(fdef_name = "define_offset")
    amount = NumberProperty(required = True)
    
    def __init__(self, original_shape, amount, **kwargs):
        super(ShapeGrow, self).__init__(
            original_shape = original_shape,
            amount = amount,
            **kwargs)

    def is_closed(self):
        return self.original_shape.is_closed()
    closed = FunctionProperty(is_closed,Shape.set_closed)

    def define_offset(self):
        o = self.original_shape.orientation() * self.amount
        return o
    
    def define_points(self, pts):
        original = Shape(self.original_shape).remove_straight_angles()
        if len(original) <= 1: return

        a2 = original.angles_rad() * 0.5
        a1 = roll(a2, 1)

        a_plus = a2 + a1

        cos_a_min = cos(a2 - a1)
        offsets = column_stack((-sin(a_plus) / cos_a_min, cos(a_plus) / cos_a_min)) * (self.offset)

        # compute offsets from each point
        pts = (original.points + offsets)
        return pts 


class ShapeVariableOffset(__ShapeModifier__):
    """ generates a shape with a variable offset from its original shape"""
    offsets = RestrictedProperty(restriction = RestrictList(RESTRICT_NUMBER), required = True)
    
    def __init__(self, original_shape, offsets, **kwargs):
        super(ShapeVariableOffset, self).__init__(
            original_shape = original_shape,
            offsets = offsets,
            **kwargs)
        
    def define_points(self, pts):
        if len(self.offset) != len(self.original_shape):
            raise AssertionError("Length of shape and offsets should be the same in ShapeVariableOffset")
        original = self.original_shape
        if len(original) <= 1: return

        a2 = original.angles_rad() * 0.5
        a1 = roll(a2, 1)

        if original.closed:
            a2[-1] = a2[0]
            a1[0] = a1[-1]
        else:
            a2[-1] = self.end_face_angle * DEG2RAD - a2[-2]
            a1[0] = self.start_face_angle * DEG2RAD - a1[1]

        a_plus = a2 + a1
        cos_a_min = cos(a2 - a1)
        offsets = column_stack((-sin(a_plus) / cos_a_min * self.offset, cos(a_plus) / cos_a_min * self.offset))

        # compute offsets from each point
        pts = (original.points + offsets)
        return pts

class ShapeExtendEnds(__ShapeModifier__):
    """ stubs the corners of a given shape """
    start_extension = NonNegativeNumberProperty(required = True)
    end_extension = NonNegativeNumberProperty(required = True)
    
    def __init__(self, original_shape, start_extension, end_extension, **kwargs):
        super(ShapeExtendEnds, self).__init__(
            original_shape = original_shape,
            start_extension = start_extension,
            end_extension = end_extension,
            **kwargs)
        
    def define_points(self, pts):
        c = Shape(self.original_shape)
        if c.closed:
            self += c
            return

        a1 = angle_rad(c[0], c[1])
        pts += Coord2(c[0].x + cos(a1) * self.start_extension, c[0].y + sin(a1) * self.start_extension)
        pts += c[1:-1]
        a1 = angle_rad(c[-1], c[-2])
        pts += Coord2(c[-1].x + cos(a1) * self.end_extension, c[-1].y + sin(a1) * self.end_extension)
        return pts


class ShapeFit(__ShapeModifier__):
    """ fits a shape in a given box """
    south_west = Coord2Property(required = True)
    north_east = Coord2Property(required = True)
    
    def __init__(self, original_shape, south_west, north_east, **kwargs):
        super(ShapeFit, self).__init__(
            original_shape = original_shape,
            south_west =south_west,
            north_east = north_east,
            **kwargs)        

    def define_points(self, pts):
        c = Shape(self.original_shape)
        #rescale
        SI = c.size_info
        size = SI.size
        SI2 = SizeInfo(west = self.south_west[0], east = self.north_east[0], north = self.north_east[1], south = self.south_west[1])
        box_size = SI2.size
        scale_factor = min([box_size[0] / size[0], box_size[1] / size[1]])
        c.magnify((0.0, 0.0), scale_factor)
        #translate
        bl = Coord2(SI.west, SI.south)
        translation = (self.south_west[0] - bl[0], self.south_west[1] - bl[1])
        c.move(translation)
        pts += c
        return pts

class ShapeShorten(__ShapeModifier__):
    """ Shortens a shape on both ends by given trim lengths """
    trim_lengths = Size2Property(default = (0.0, 0.0))
    
    def define_points(self, pts):
        if self.original_shape.closed:
            pts = self.original_shape.points
            return pts
        
        S = Shape(self.original_shape)
        distances = array(self.original_shape.distances())
        cumul = hstack([array([0]), cumsum(distances)[:-1]])

        start_point_distance = self.trim_lengths[0]
        end_point_distance = cumul[-1] - self.trim_lengths[1]
        
        if start_point_distance > end_point_distance:
            raise AttributeError('trim_lengths should be small enough to leave part of the shape')

        L = len(S)
        start_point_added = False
        end_point_added = False
        points = []
        
        # could be made much more efficient using numpy operations
        
        for i in range(L):
            d1 = cumul[i]
            if d1 >= start_point_distance:
                if not start_point_added:
                    d2 = cumul[i-1]
                    fraction = (start_point_distance-d2) / (d1-d2)
                    if fraction > 0 and fraction < 1:
                        points += [S[i]*fraction + S[max(i-1, 0)] * (1-fraction)]
                    start_point_added = True
            if d1 >= start_point_distance and d1 <= end_point_distance:
                points += [S[i]]
            else:
                if start_point_added and not end_point_added:
                    d2 = cumul[i-1]
                    fraction = (end_point_distance-d2) / (d1-d2)
                    if fraction > 0 and fraction < 1:
                        points += [S[i]*fraction + S[i-1] * (1-fraction)]
                    end_point_added = True
                
        pts = array(points)
        return pts

class ShapeSample(__ShapeModifier__):
    """ creates a shape sampling points on another shape along specified distances between the sampling point"""
    sampling_distances = RestrictedProperty(required = True, restriction = RestrictList(RESTRICT_POSITIVE))
    
    def define_points(self, pts):
        S = Shape(self.original_shape)
        distances = array(self.original_shape.distances())
        cumul = cumsum(distances)
        sampling_points = []
        i = 0
        j = 1
        d1 = 0
        d2 = cumul[0]
        L = len(self.original_shape)
        for D in self.sampling_distances:
            while d2 < D:
                d1 = d2
                d2 = cumul[j]
                j+= 1
                
            fraction = (D-d1)/(d2-d1)
            last_point = S[max(j-1, 0)]
            next_point = S[j%L]
            sampling_points += [fraction * next_point + (1-fraction) * last_point]
        
        pts = array(sampling_points)
        return pts

    
class ShapeSamplePeriodic(ShapeSample):
    """ creates a shape sampling points on another shape along specified periodic distances from the start point of the shape """
    sampling_period = PositiveNumberProperty(required = True)
    exclude_ends = Size2Property(default = (0.0, 0.0), doc = "Lengths not taken into account on both ends")
    sampling_distances = LockedProperty()
    
    def define_sampling_distances(self):
        L = self.original_shape.length()
        return arange(self.exclude_ends[0], L-self.exclude_ends[1]+0.001 * self.sampling_period, self.sampling_period)

