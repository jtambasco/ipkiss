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

from math import *
import sys

from ipkiss.all import *
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from picazzo.log import PICAZZO_LOG as LOG


class __SpiralLoopElement__(Group):
    center = Coord2Property(default = (0.0, 0.0))
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    loop_size = Size2Property(required = True)
    spacing = NonNegativeNumberProperty(default = TECH.WG.SPACING)
    waveguides = DefinitionProperty(fdef_name="define_waveguides")
    reverse = BoolProperty(default = False)
    change_end_straight = Coord2Property(default = (0.0, 0.0), doc = "change the length of the end sections")

    def define_elements(self, elems):
        for w in self.waveguides: 
            elems += w
        return elems
        
    def spiral_length(self):
        return sum([w.center_line().length() for w in self.waveguides])
        
    def define_ports(self, P):
        for w in self.waveguides:
            P += w.ports
        return P
    

class WaveguideSpiralHeartElement(__SpiralLoopElement__):
    stub_direction = RestrictedProperty(default = "H", restriction = RestrictValueList(["H", "V"]))

    def define_waveguides(self):
        S = self.spacing

        waveguides = []
        Sx, Sy = 0.5*self.loop_size.x, 0.5*self.loop_size.y
        S = self.spacing

        b1, b2 = self.wg_definition.get_bend90_size()
        if self.reverse:
            bs2, bs1 = b1, b2
        else:
            bs1, bs2 = b1, b2
            
        Si = -Sy + bs1 - 2*S - self.change_end_straight[0]
        So = -Sy + bs2 - S + self.change_end_straight[1]


        if self.stub_direction == "H":
            sh = Shape([(Sx, Si),
                        (Sx, Sy),
                        (-Sx, Sy),
                        (-Sx, -Sy),
                        (Sx-2*S, -Sy),
                        (Sx-2*S, -0.5*S),
                        (-Sx+S, -0.5*S),
                        (-Sx + S, Sy-S),
                        (Sx - S, Sy-S),
                        (Sx - S, So)])
        else:
            sh = Shape([(Sx, Si),
                (Sx, Sy),
                (-Sx, Sy),
                (-Sx, -Sy),
                (-0.5*S, -Sy),
                (-0.5*S, Sy-S),
                (Sx-S, Sy-S),
                (Sx-S, So)])
    
        if self.reverse:
            sh.reverse()

        
        sh.move(self.center)
        waveguides.append(self.wg_definition(shape = sh))
        return waveguides
        
    def spiral_n_o_bends(self):
        return 8

        
class WaveguideSpiralLoopElement(__SpiralLoopElement__):

    def define_waveguides(self):
        S = self.spacing
        waveguides = []
        Sx, Sy = 0.5*self.loop_size.x, 0.5*self.loop_size.y
        S = self.spacing
        
        b1, b2 = self.wg_definition.get_bend90_size()
        if self.reverse:
            bs2, bs1 = b1, b2
        else:
            bs1, bs2 = b1, b2
            
        Si = -Sy + bs1 - S - self.change_end_straight[0]
        So = -Sy + bs2 + self.change_end_straight[1]
        sh = Shape([(Sx, Si),
                        (Sx, Sy),
                        (-Sx, Sy),
                        (-Sx, -Sy),
                        (Sx-S, -Sy),
                        (Sx-S, So)
                    ])
        if self.reverse:
            sh = sh.reverse()
        sh.move(self.center)
        waveguides.append(self.wg_definition(shape = sh))
        return waveguides

    def spiral_n_o_bends(self):
        return 4

class __WaveguideSpiral__(Structure):
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    n_o_loops = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    inner_size = Size2Property(required = True)
    spacing = NonNegativeNumberProperty(default = TECH.WG.SPACING)
    spiral_center = Coord2Property(default = (0.0, 0.0))

    def spiral_length(self):
        return sum([W.spiral_length() for W in self.loops])

    def spiral_n_o_bends(self):
        return sum([W.spiral_n_o_bends() for W in self.loops])

    def define_elements(self, elems):
        elems += self.loops
        return elems


class WaveguideSingleSpiral(__WaveguideSpiral__):
    __name_prefix__ = "SPIRAL1"
    loops = DefinitionProperty(fdef_name = "define_loops")
    

    def define_loops(self):
        loops = []
        LS = self.inner_size  - (self.spacing, self.spacing)
        for i in range(self.n_o_loops):
            loops += [WaveguideSpiralLoopElement(wg_definition = self.wg_definition,
                                                     center = self.spiral_center,
                                                     loop_size = LS,
                                                     spacing = self.spacing)]
            LS = LS + (2*self.spacing, 2*self.spacing)
        return loops

    def define_ports(self, ports):
        ports = self.loops[-1].in_ports + self.loops[0].out_ports
        return ports


class WaveguideDoubleSpiral(__WaveguideSpiral__):
    __name_prefix__ = "SPIRAL2"
    loops = DefinitionProperty(fdef_name = "define_loops")
    stub_direction = RestrictedProperty(default = "H", restriction = RestrictValueList(["H", "V"]))

    def define_loops(self):
        if (self.n_o_loops == 1):
            change_end_straight = (-self.spacing, 0.0)
        else:
            change_end_straight = (0.0, 0.0)
        loops = [WaveguideSpiralHeartElement(wg_definition = self.wg_definition,
                                                     center = self.spiral_center,
                                                     loop_size = self.inner_size,
                                                     spacing = self.spacing,
                                                     stub_direction = self.stub_direction,
                                                     change_end_straight = change_end_straight,
                                                     reverse = True) #reverse : required for asymmetric waveguide definitions
                  ]
        LS = self.inner_size  
        for i in range(self.n_o_loops-1):
            LS = LS + (2*self.spacing, 2*self.spacing)
            if (i==self.n_o_loops-2):
                change_end_straight = (-self.spacing, 0.0)
            else:
                change_end_straight = (0.0, 0.0)
            loops += [WaveguideSpiralLoopElement(wg_definition = self.wg_definition,
                                                     center = self.spiral_center,
                                                     loop_size = LS,
                                                     spacing = 2*self.spacing,
                                                     change_end_straight = (0.0, 0.0),
                                                     )
                                                     ]
            LS = LS + (2*self.spacing, 2*self.spacing)
            loops += [WaveguideSpiralLoopElement(wg_definition = self.wg_definition,
                                                     center = self.spiral_center,
                                                     loop_size = LS,
                                                     spacing = 2*self.spacing,
                                                     change_end_straight = change_end_straight,
                                                     reverse = True) #reverse : required for asymmetric waveguide definitions
                                                 ]
        return loops


    def define_ports(self, ports):
        if self.n_o_loops == 1:
            ports = self.loops[0].ports 
        else:
            ports = self.loops[-2].in_ports + self.loops[-1].in_ports.invert_copy()
        return ports
    

class WaveguideDoubleSpiralWithIncoupling(WaveguideDoubleSpiral):
    __name_prefix__ = "SPIRAL2I"
    inc_length = NonNegativeNumberProperty(default = 5.0)
    spiral_center = DefinitionProperty(fdef_name = "define_spiral_center")
    waveguides = DefinitionProperty(fdef_name = "define_waveguides")

    def define_spiral_center(self):
        S = self.spacing

        OS = 4 * (self.n_o_loops-1) * S + self.inner_size.x 
        
        spiral_center = Coord2(self.inc_length +  0.5*OS, (2 * self.n_o_loops - 1) * S + 0.5*self.inner_size.y)
        return spiral_center
    
    def define_waveguides(self):
        waveguides = []
        S = self.spacing
        
        OLS = self.loops[-1].loop_size
        
        
        OS = 4 * (self.n_o_loops-1) * S + self.inner_size.x 
        bs1, bs2 = self.wg_definition.get_bend90_size()

        if self.stub_direction == "H":
            L_out = 0.5 * self.inner_size.y - self.spacing # backward compatibility
            #L_out = self.spacing + bs2
        else:
            L_out = self.spacing + bs2
        sh = Shape([(0.0,0.0), 
                        (self.inc_length + OS - S, 0.0),
                        (self.inc_length + OS - S, self.spiral_center.y  - 0.5 * OLS[1] - S + bs1)
                    ])
        waveguides += [self.wg_definition(shape = sh)]

        sh = Shape([(self.inc_length + OS +L_out + self.inc_length, 0.0),
                        (self.inc_length + OS, 0.0),
                        (self.inc_length + OS, self.spiral_center.y  - 0.5 * OLS[1] - S + bs2)
                    ]).reverse() #reverse : required for asymmetric waveguide definitions       
        from ipkiss.plugins.photonics.port import InOpticalPort, OutOpticalPort, OpticalPortList
        #because the second waveguide's shape was reversed, we also need to switch the ports
        wg_el = self.wg_definition(shape = sh)
        waveguides += [wg_el]
        return waveguides
    

    def define_elements(self, elems):
        T = self.wg_definition.trench_width
        W = self.wg_definition.wg_width
        X1 = min(self.inc_length - T - 0.5* W, 0 )

        elems += self.loops
        elems += self.waveguides
        return elems

        
    def spiral_length(self):
        return super(WaveguideDoubleSpiralWithIncoupling, self).spiral_length() + sum([W.center_line().length() for W in self.waveguides])

    def n_o_bends(self):
        return super(WaveguideDoubleSpiralWithIncoupling, self).n_o_bends() + 2

    def define_ports(self,prts):
        prts += self.waveguides[-2].in_ports 
        #prts += self.waveguides[-1].in_ports.invert_copy()
        prts += self.waveguides[-1].out_ports
        return prts
    
    
class __AutoSizeSpiral__(StrongPropertyInitializer):
    inner_size = DefinitionProperty(fdef_name = "define_inner_size")
    stub_length = NonNegativeNumberProperty(default  = TECH.WG.SHORT_STRAIGHT)
    
    def define_inner_size(self):
        (bs1, bs2) = self.wg_definition.get_bend90_size()
        if self.stub_direction == "H":
            return Coord2(self.stub_length + bs1 + bs2 + 3*self.spacing, 
                      2 * bs1 + 2 * bs2 + self.spacing)
        else:
            return Coord2(2*bs1 + 2*bs2 + self.spacing, 
                       self.stub_length + bs1 + bs2 + self.spacing)
            

class WgSpiral(__AutoSizeSpiral__, WaveguideDoubleSpiralWithIncoupling):
    pass
    



#def WgSpiralFixedLength(wg_definition, 
                        #total_length, 
                        #n_o_loops, 
                        #spacing = TECH.WG.SPACING, 
                        #stub_direction = "H",
                        #**kwargs):
    #S = WgSpiral(wg_definition = wg_definition,
                  #stub_length = 0, 
                  #n_o_loops = n_o_loops, 
                  #spacing = spacing, 
                  #stub_direction = stub_direction,
                  #**kwargs)
    #l = S.spiral_length()    
    #if total_length < l:
        #LOG.warning("Total length is too short for the given bend radius and n_o_loops")
    #else:
        #sis = S.inner_size
        #S.inner_size = Coord2(sis[0] + (total_length - l) / (4 * n_o_loops +1), sis[1])
    #l = S.spiral_length()    
    #if abs(l-total_length) > 0.01:
        #LOG.info("Desired length: " + str(total_length)+  ", actual length: " + str(l))
   
    #return S
        

class __AutoSizeFixedLengthSpiral__(__AutoSizeSpiral__):
    total_length = NonNegativeNumberProperty(required = True)
    growth_direction =  RestrictedProperty(default = "H", restriction = RestrictValueList(["H", "V"]))
    stub_length = LockedProperty()
    
    def define_inner_size(self):
        S = WgSpiral(wg_definition = self.wg_definition,
                      stub_length = 0, 
                      n_o_loops = self.n_o_loops, 
                      spacing = self.spacing, 
                      stub_direction = self.stub_direction,
                      inc_length = self.inc_length,

                      )
        l = S.spiral_length()    

        if self.total_length < l:
            LOG.warning("Total length is too short for the given bend radius and n_o_loops")
            raise ValueError("Total length is too short for the given bend radius and n_o_loops")
        else:
            sis = S.inner_size
            if self.growth_direction == "H":
                if self.stub_direction == "H":
                    new_sis = Coord2(sis[0] + (self.total_length - l) / (4 * self.n_o_loops +1), sis[1])
                else: 
                    new_sis = Coord2(sis[0] + (self.total_length - l) / (4 * self.n_o_loops -1), sis[1])
            else:
                if self.stub_direction == "H":
                    new_sis= Coord2(sis[0], sis[1] + (self.total_length - l) / (4 * self.n_o_loops))
                else:
                    new_sis = Coord2(sis[0], sis[1] + (self.total_length - l) / (4 * self.n_o_loops +2))
        
        # S.inner_size = new_sis
        # l = S.spiral_length()    
        # if abs(l - self.total_length) > 0.01:
        #     LOG.error("Hoho: Desired length: " + str(self.total_length)+  ", actual length: " + str(l))
        
        del S
        return new_sis

    def define_stub_length(self):
        if self.stub_direction == "H":
            return Coord2(self.stub_length + bs1 + bs2 + 3*self.spacing, 
                      2 * bs1 + 2 * bs2 + self.spacing)
        else:
            return Coord2(2*bs1 + 2*bs2 + 3*self.spacing, 
                       self.stub_length + bs1 + bs2 + 3*self.spacing)

        (bs1, bs2) = self.wg_definition.get_bend90_size()
        if self.stub_direction == "H":
            return self.inner_size[0]-bs1-bs2-3*self.spacing
        else:
            return self.inner_size[1] - bs1-bs2 - 3*spacing

        
class WgSpiralFixedLength(__AutoSizeFixedLengthSpiral__, WaveguideDoubleSpiralWithIncoupling):
    pass
    
