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

from ipcore.all import *
from .field import ElectricField, MagneticField

from ..basics.environment import __Environment__, Environment, DEFAULT_ENVIRONMENT

__all__ = ['DEFAULT_ENVIRONMENT']

class __ElectroMagneticEnvironment__(__Environment__):
    electric_field = RestrictedProperty(default = ElectricField(value = (0.0, 0.0, 0.0)), restriction = RestrictType(ElectricField))
    magnetic_field = RestrictedProperty(default = MagneticField(value = (0.0, 0.0, 0.0)), restriction = RestrictType(MagneticField))
    
Environment.mixin(__ElectroMagneticEnvironment__)
