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

from ipcore.all import PositiveNumberProperty
from ..basics.waveguide import __Mode__, Waveguide

class OpticalMode(__Mode__):
    def n_eff(self, wavelength):
        raise NotImplementedError("n_eff not implemented" )
    
    def n_group(self, wavelength):    
        raise NotImplementedError("n_group implemented" )
    
    def loss_dBcm(self, wavelength):
        raise NotImplementedError("lossdBcm not implemented" )

    def angle_rad(self, wavelength):
        raise NotImplementedError("angle (diffraction angle in slab) not implemented" )
    
    def angle_deg(self, wavelength):
        self.angle_rad(wavelength)*RAD2DEG
        
class SlabWaveguide(Waveguide):
    thickness = PositiveNumberProperty(default=1.0)

class StripWaveguide(SlabWaveguide):
    width = PositiveNumberProperty(default=1.0)

class RibWaveguide(StripWaveguide):
    depth = PositiveNumberProperty(default=1.0)