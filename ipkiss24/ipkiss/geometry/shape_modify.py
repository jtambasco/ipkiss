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

from .shape import Shape
from .shape_info import shape_south_west, shape_size, shape_orientation
from .size_info import SizeInfo
from .coord import Coord2
from .shape_info import angle_rad, lines_cross
from .transforms.magnification import Magnification
from .transforms.stretch import shape_scale
from .transforms.translation import Translation, shape_translate
from ipkiss.log import IPKISS_LOG as LOG
from numpy import pi, cos, sin

import numpy

__all__ = ["shapes_fit"]

def shape_fit(coordinates, south_west, north_east):
        ret_coords = Shape()
        #rescale
        size = shape_size(coordinates)
        box_size = shape_size([south_west, north_east])
        scale_factor = min([box_size[0] / size[0], box_size[1] / size[1]])
        ret_coords = shape_scale(coordinates, (scale_factor, scale_factor))
        #translate
        bl = shape_south_west(coordinates)
        translation = (south_west[0] - bl[0], south_west[1] - bl[1])
        ret_coords = shape_translate(ret_coords, translation)
        return ret_coords

# fit multiple shapes
def shapes_fit(shapes, south_west, north_east):
        ret_shapes = []
        #get the extent of all shapes
        new_shapes = [Shape(s) for s in shapes]

        SI = SizeInfo()
        for s in new_shapes:
                SI += s.size_info
        bl = Coord2(SI.west, SI.south)
        tr = Coord2(SI.east, SI.north)
        new_size = SizeInfo(west=south_west[0], east=north_east[0], south=south_west[1], north=north_east[1])
        scale_factor = min([new_size.width / SI.width, new_size.height / SI.height])
        translation = (south_west[0] - scale_factor * new_size.west, south_west[1] - scale_factor * new_size.south)
        T = Magnification((0.0, 0.0), scale_factor) + Translation(translation)
        for s in new_shapes:
                ret_shapes.append(s.transform_copy(T))
        return ret_shapes


def shape_remove_identicals(shape):
        #removes two subsequent identical points
        S = Shape(shape)
        return S.remove_identicals()

def shape_delete_loops(coordinates):
        if len(coordinates) <= 3:
                return coordinates

        nc = Shape(coordinates).remove_identicals().points
        # eliminate backloop

        dels = set()
        i = -1
        L = len(nc)
        while i < L - 2:
                i += 1
                if i in dels:
                        continue
                c1 = nc[i]
                c2 = nc[i + 1]
                k = i + 2
                while k < L - 1:

                        c3 = nc[k]
                        c4 = nc[k + 1]
                        if lines_cross(c1, c2, c3, c4):
                                nc[i + 1] = intersection(c1, c2, c3, c4)
                                dels.update(range(i + 2, k + 1))
                                c2 = nc[i + 1]
                        k += 1 
        return numpy.delete(nc, dels, 0)

