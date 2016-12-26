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


class __ElectroMagneticMaterial__(__Material__):
    """ Material with electromagnetic properties """
    epsilon = NumberProperty(default = 1.0)
    mu = NumberProperty(default = 1.0)

    
class __BlendedElectroMagneticMaterial__(__ElectroMagneticMaterial__):
    """ Material with electromagnetic properties """
    fraction = FloatProperty(default = 1.0)
    epsilon = FunctionNameProperty("get_epsilon")
    mu = FunctionNameProperty("get_n")
    
    def get_epsilon(self, environment = DEFAULT_ENVIRONMENT):
        return self.fraction * self.material_1.get_epsilon(environment) + (1-self.fraction) * self.material_2.get_epsilon(environment)
    def get_mu(self):
        return self.fraction * self.material_1.get_mu(environment) + (1-self.fraction) * self.material_2.get_mu(environment)
    
#before doing the mixin, assess that we are not overwriting any epsilon values that were already set in the technology settings.
from ipkiss.technology import get_technology
TECH=get_technology()
if hasattr(TECH,"MATERIALS"):
    for (material_id,material) in TECH.MATERIALS:    
        if hasattr(material, "epsilon"):
            raise Exception("Epsilon value of material '%s' is about to be overwritten by mixin of class __ElectroMagneticMaterial__.\nMake sure you do \"from pysics.electromagnetics import *\" in your technology settings before setting epsilon values." %material.name)
    
Material.mixin(__ElectroMagneticMaterial__)

