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


from math import pi as _pi, sqrt as _sqrt
from ipkiss.geometry.coord import Coord2

DEG2RAD = _pi / 180.0
RAD2DEG = 180.0 / _pi

#----------------------------------------------------------------------------
#Some global constants
#----------------------------------------------------------------------------
TEXT_ALIGN_LEFT = 0
TEXT_ALIGN_CENTER = 1
TEXT_ALIGN_RIGHT = 2
TEXT_ALIGNS_HORIZONTAL = [TEXT_ALIGN_LEFT, TEXT_ALIGN_CENTER, TEXT_ALIGN_RIGHT]


TEXT_ALIGN_TOP = 0
TEXT_ALIGN_MIDDLE = 1
TEXT_ALIGN_BOTTOM = 2
TEXT_ALIGNS_VERTICAL = [TEXT_ALIGN_TOP, TEXT_ALIGN_MIDDLE, TEXT_ALIGN_BOTTOM]

TEXT_STYLE_POLYGONS = 1
TEXT_STYLE_LABELS = 2

PATH_TYPE_NORMAL = 0
PATH_TYPE_ROUNDED = 1
PATH_TYPE_EXTENDED = 2
PATH_TYPES = [PATH_TYPE_NORMAL, PATH_TYPE_ROUNDED, PATH_TYPE_EXTENDED]

GDSII_MAX_COORDINATES = 200

NORTH = Coord2(0.0, 1.0)
SOUTH = Coord2(0.0, -1.0)
EAST = Coord2(1.0, 0.0)
WEST = Coord2(-1.0, 0.0)

_sqrt2_2 = _sqrt(0.5)
NORTHEAST = Coord2(_sqrt2_2, _sqrt2_2,)
NORTHWEST = Coord2(- _sqrt2_2, _sqrt2_2,)
SOUTHEAST = Coord2(_sqrt2_2, -_sqrt2_2,)
SOUTHWEST = Coord2(- _sqrt2_2, -_sqrt2_2,)


