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

from ..shape_modifier import __ShapeModifier__
from numpy import transpose, row_stack, ones, array, arange, diff, size, outer
from ipcore.properties.predefined import IntProperty, RESTRICT_POSITIVE

__all__ = ["ShapeBezier"]

class ShapeBezier(__ShapeModifier__):
    """ polynomial bezier curve based on a shape with control points """
    steps = IntProperty(restriction = RESTRICT_POSITIVE, default = 100)
    def __init__(self, original_shape, steps = 100, **kwargs):
        super(ShapeBezier, self).__init__(
            original_shape = original_shape,
            steps = steps,
            **kwargs)

    def define_points(self, pts):
        # perform decasteljau iteration
        step = 1.0 / self.steps
        t = arange(0.0, 1.0 + 0.5 * step, step)
        P = array(self.original_shape.points)
        Px = outer(P[:, 0], ones(size(t)))
        Py = outer(P[:, 1], ones(size(t)))
        for j in range(len(self.original_shape) - 1,  0, -1):
            Px = Px[0:j, :] + diff(Px, 1, 0) * t
            Py = Py[0:j, :] + diff(Py, 1, 0) * t

        pts = transpose(row_stack((Px, Py)))
        return pts
