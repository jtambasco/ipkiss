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

"""
Directional couplers

"""

from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.all import *
from ipkiss.plugins.photonics.wg.connect import WaveguidePointRoundedConnectElementDefinition, __RoundedWaveguideManhattan__, __RoundedWaveguide__
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty

__all__ = ["StraightDirectionalCoupler",
           "Bend90SDirectionalCoupler",
           "Bend90DirectionalCoupler"]

# TODO: Include rounding algorithm in here. (From connect.__RoundedWaveguide__)
# FIXME: Add symmetry in the coupling section (wrt assymmetric spline rounding algorithms)

class __DirectionalCoupler__(Structure):
    __name_prefix__ = "GDircoup_"
    wg_definition1 = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    wg_definition2 = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    spacing = PositiveNumberProperty(default = TECH.WG.DC_SPACING)
    length = NonNegativeNumberProperty(default = 30.0)
    waveguides = DefinitionProperty(fdef_name = "define_waveguides")

    
    def define_waveguides(self):
        raise NotImplementedException("__GenericDirectionalCouplerEl__::define_waveguides to be implemented by subclass.")
    
    def define_elements(self, elems):
        elems += self.waveguides
        return elems

    def define_ports(self, ports):
        P = OpticalPortList()
        for w in self.waveguides:
            P += w.ports
        return P
        

class StraightDirectionalCoupler(__DirectionalCoupler__):
    __name_prefix__ = "GDircoup_S_"

    def define_waveguides(self):
        waveguides = [
            self.wg_definition1([(0.0, -0.5*self.spacing ),(self.length, -0.5*self.spacing )]),
            self.wg_definition2([(0.0, +0.5*self.spacing ),(self.length, 0.5*self.spacing )])
            ]
        return waveguides 
        
        

class Bend90DirectionalCoupler(__RoundedWaveguideManhattan__, __DirectionalCoupler__):
    __name_prefix__ = "GDircoup_90_"
        
        
    def define_waveguides(self):
        wgdef1 = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition1,
                                                                   bend_radius = self.bend_radius,
                                                                   manhattan = self.manhattan,
                                                                   rounding_algorithm = self.rounding_algorithm)
        wgdef2 = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition2,
                                                                   bend_radius = self.bend_radius,
                                                                   manhattan = self.manhattan,
                                                                   rounding_algorithm = self.rounding_algorithm)
        bs1, bs2 = self.get_bend90_size()
        
        waveguides = [wgdef1([(-bs2, -0.5*self.spacing - bs1),
                                  (-bs2, -0.5*self.spacing ),
                                  (self.length+bs1, -0.5*self.spacing ),
                                  (self.length+bs1, -0.5*self.spacing - bs2)
                                  ]),
                           wgdef2([(-bs2, 0.5*self.spacing + bs1),
                                  (-bs2, +0.5*self.spacing ),
                                  (self.length+bs1, +0.5*self.spacing ),
                                  (self.length+bs1, +0.5*self.spacing + bs2)
                                 ])
                            ]
        return waveguides

    

class Bend90SDirectionalCoupler(Bend90DirectionalCoupler):
    __name_prefix__ = "GDircoup_90S_"
    min_straight = NonNegativeNumberProperty(default=TECH.WG.SHORT_STRAIGHT)


    def define_waveguides(self):
        wgdef1 = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition1,
                                                                   bend_radius = self.bend_radius,
                                                                   manhattan = self.manhattan,
                                                                   rounding_algorithm = self.rounding_algorithm)
        
        wgdef2 = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition2,
                                                                   bend_radius = self.bend_radius,
                                                                   manhattan = self.manhattan,
                                                                   rounding_algorithm = self.rounding_algorithm)
        bs1, bs2 = self.get_bend90_size()
        waveguides = [wgdef1(shape = [(-bs1 - bs2, -0.5*self.spacing -bs1-bs2-self.min_straight),
                                   (-bs2, -0.5*self.spacing - bs1 - bs2 -self.min_straight),
                                   (-bs2, -0.5*self.spacing ),
                                   (self.length+bs1, -0.5*self.spacing),
                                   (self.length+bs1, -0.5*self.spacing - bs1 - bs2-self.min_straight),
                                   (self.length+bs1+bs2, -0.5*self.spacing - bs1 - bs2 -self.min_straight)
                                   ]),
                           wgdef2(shape = [(-bs1-bs2, 0.5*self.spacing+ bs1 + bs2 +self.min_straight),
                                   (-bs2, 0.5*self.spacing +bs1 + bs2+self.min_straight),
                                   (-bs2, +0.5*self.spacing ),
                                   (self.length+bs1, +0.5*self.spacing ),
                                   (self.length+bs1, +0.5*self.spacing + bs1 + bs2+self.min_straight),
                                   (self.length+bs1+bs2, +0.5*self.spacing + bs1 + bs2 +self.min_straight)
                               ])
                            ]
        return waveguides
    

