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

from ...constants import DEG2RAD, RAD2DEG
from math import *
from ..shape import  Shape
from .basic import ShapeBendRelative
from ..shape_info import angle_rad, distance
from ... import settings
from ..coord import Coord2Property
from ipcore.properties.predefined import AngleProperty, PositiveNumberProperty
from ipkiss.log import IPKISS_LOG as LOG
from ...technology.settings import TECH

__all__ = ["ShapeArcLineArc"]

class ShapeArcLineArc (Shape):
    coord_start = Coord2Property(required = True)
    angle_start = AngleProperty(required = True)
    radius_start = PositiveNumberProperty(required = True)

    coord_end = Coord2Property(required = True)
    angle_end = AngleProperty(required = True)
    radius_end = PositiveNumberProperty(required = True)

    angle_step = AngleProperty(default = TECH.METRICS.ANGLE_STEP)
    
    def __init__(self, 
                 coord_start, 
                 angle_start, 
                 radius_start, 
                 coord_end, 
                 angle_end, 
                 radius_end, 
                 **kwargs):
        super(ShapeArcLineArc, self).__init__(
            coord_start = coord_start,
            coord_end = coord_end,
            angle_start = angle_start,
            angle_end = angle_end,
            radius_start = radius_start,
            radius_end = radius_end,
            **kwargs)

    def define_points(self, pts):
        sa = self.angle_start * DEG2RAD
        ea = self.angle_end * DEG2RAD
        bae = (ea + pi) % ( 2 * pi)

        # normalize angles between 0 and 2pi
        sa = (sa) % (2 * pi)
        ea = (ea) % (2 * pi)

        #angle bvetween two points
        connect_angle = angle_rad(self.coord_end, self.coord_start)
        ca_start = (connect_angle - sa) % (2 * pi)
        ca_end = (connect_angle - ea) % (2 * pi)
        #LOG.debug("ca: %f %f %f" %(, connect_angle , ca_start, ca_end))

        #check both positive and negative radii
        valid = False
        signs = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for s in signs:
            radius_start = abs(self.radius_start) * s[0]
            radius_end = abs(self.radius_end) * s[1]
            
            # Centers of circles through the points.
            c_start = (self.coord_start[0] + radius_start * sin(sa),  self.coord_start[1] - radius_start * cos(sa))
            c_end = (self.coord_end[0] + radius_end * sin(ea), self.coord_end[1] - radius_end * cos(ea))

            #distance between centers
            dm = distance(c_start, c_end)
            if abs(radius_start - radius_end) > dm:
                # no valid solution possible 
                continue

            # unit vector between circle centers
            mm = ((c_end[0] - c_start[0]) / dm, (c_end[1] - c_start[1]) / dm)
            # angle between normal to connector line and circle centers
            alpha = -acos((radius_start - radius_end) / dm)

            # unit vector from m to p.
            mp = (mm[0] * cos(alpha) + mm[1] * sin(alpha), -mm[0] * sin(alpha) + mm[1] * cos(alpha))

            # Point at first circle. 
            p0 = (c_start[0] + radius_start * mp[0], c_start[1] + radius_start * mp[1])
            # Point at second circle.
            p1 = (c_end[0] + radius_end * mp[0], c_end[1] + radius_end * mp[1])

            #LOG.debug("p0, p1:" %( p0, p1))

            forward_angle = angle_rad(p1, p0) % (2 * pi)
            backward_angle = angle_rad(p0, p1) % (2 * pi)

            forward_turn = (forward_angle - sa + pi) % (2 * pi) - pi
            backward_turn = (backward_angle - bae + pi) % (2 * pi) - pi

            # LOG.debug("F: %f B:%f %f %f" % (s[0],  s[1], forward_turn, backward_turn))
            
            if (forward_turn * s[0] <= 0) and (backward_turn * s[1] >= 0):
                valid = True
                break

        if not valid:
            LOG.error("Can't connect two points with arc_line_arc")
            raise SystemExit

        #LOG.debug("angles: %f %f %f %f" %( angle_start, straight_angle*180/pi, angle_end, backward_angle*180/pi))
        if forward_turn == 0.0:
            pts += [self.coord_start]
        else:
            pts += ShapeBendRelative(self.coord_start, abs(radius_start), sa * RAD2DEG, forward_turn * RAD2DEG, angle_step = self.angle_step)

        if backward_turn == 0.0:
            pts += [self.coord_end]
        else:
            bend2 = ShapeBendRelative(self.coord_end, abs(radius_end), bae * RAD2DEG, backward_turn * RAD2DEG, angle_step = self.angle_step)
            bend2.reverse()
            pts += bend2
            
        return pts

    def move(self, position):
        self.coord_start = (self.coord_start[0] + position[0], self.coord_start[1] + position[1])
        self.coord_end = (self.coord_end[0] + position[0], self.coord_end[1] + position[1])
        return self
    
    