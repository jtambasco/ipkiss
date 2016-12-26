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

from ..basics.material.material import __Material__, Material, BlendedMaterial
from ..basics.environment import DEFAULT_ENVIRONMENT
from ipcore.all import *

__all__ = []

# Optical materials. Should be separate module which loads only when optical simulations are needed.
# this mixes new properties into existing material classes
class __OpticalMaterial__(__Material__):
    """ Material with optical properties """
    n = NumberProperty(default = 1.0)
    
    def get_n(self, environment = DEFAULT_ENVIRONMENT):
        return self.n
    
class __BlendedOpticalMaterial__(__Material__):
    """ Material with optical properties """
    n = FunctionNameProperty("get_n")
    
    def get_n(self, environment = DEFAULT_ENVIRONMENT):
        return self.fraction * self.material_1.get_n(DEFAULT_ENVIRONMENT) + (1-self.fraction) * self.material_2.get_n(DEFAULT_ENVIRONMENT)

Material.mixin(__OpticalMaterial__)
BlendedMaterial.mixin(__BlendedOpticalMaterial__)

