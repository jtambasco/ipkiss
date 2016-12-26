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

import math

#########################################################
# commonly used roots
#########################################################

SQRT2 = math.sqrt(2.0)
SQRT2_2 = SQRT2 / 2.0
SQRT3 = math.sqrt(3.0)
SQRT3_2 = SQRT3 / 2.0

INV_SQRT_2 = 1.0/1.4142135623730950488016887242097 # inverse square root of 2


#########################################################
# Conversion of radians to degrees
#########################################################
DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0/math.pi
