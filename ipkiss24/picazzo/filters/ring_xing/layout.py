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



from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from picazzo.filters.ring import RingRect


from ipkiss.all import *

__all__ = ["RingCrossingGeneric",
           "RingCrossingMiniGeneric",
           "RingCrossingBendGeneric"]
           

#################################################################
### crossing classes
#################################################################

class RingCrossingGeneric(Structure):
    """crossing with a ring resonator"""
    __name_prefix__ = "ringX_"    
    process = ProcessProperty(default = TECH.PROCESS.WG)
    ring = RestrictedProperty(restriction = RestrictType(RingRect), required = True)
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    spacing = PositiveNumberProperty(default = TECH.WG.DC_SPACING)


    @cache()
    def get_wg_length(self):
        bs = mean(self.ring.get_bend90_size()) 
        return max(2 * R, 2 * R) + self.spacing
    
    @cache()
    def get_waveguides(self):
        wgdef = self.wg_definition
        wg_length = self.get_wg_length()
        L = []
        L += [wgdef(shape = [(-wg_length, 0.0), (wg_length, 0.0)])]
        L += [wgdef(shape = [(0.0, wg_length), (0.0, -wg_length)])]
        return L
    
        
    def define_elements(self, elems):
        R = mean(self.ring.get_bend90_size())
        ring_pos_south = (-R- self.spacing, -R- self.spacing)
        ring_pos_north =    (+R+  self.spacing, +R+ self.spacing)       
        elems += SRef(self.ring, ring_pos_south)
        elems += SRef(self.ring, ring_pos_north, CMirror())
        elems += self.get_waveguides()
        return elems
        
    def define_ports(self, P):
        for w in self.get_waveguides():
            P += w.ports
        return P


class RingCrossingMiniGeneric(RingCrossingGeneric):
    """crossing with a ring resonator"""
    __name_prefix__ = "mringX_"    

    def get_wg_length(self):
        return R + self.spacing
    
    def define_wg_h(self):
        wg_def = WgElDefinition(wg_width = self.wg_width, trench_width = self.trench_width, process = self.process)
        return wg_def([(-wg_length, 0.0), (wg_length, 0.0)])
    
    def define_wg_v(self):
        wg_def = WgElDefinition(wg_width = self.wg_width, trench_width = self.trench_width, process = self.process)
        return wg_def([(0.0, wg_length), (0.0, -wg_length)])
        

    
class RingCrossingBendGeneric(RingCrossingGeneric):
    """crossing with a ring resonator with bent coupling sections"""
    __name_prefix__ = "ringX_B"    

    couple_angle = AngleProperty(required = True)
    
    wg_h_wg_v = DefinitionProperty(fdef_name = "define_wg_h_wg_v")
    
    def define_wg_h_wg_v(self):
        # override waveguides
        R = mesn(self.ring.get_bend90_size()) + self.spacing
        s = ShapeBendRelative((R, 0.0), R, 0.0, self.couple_angle)
        s += ShapeBendRelative(s[-1].move_polar_copy(R, self.couple_angle), R, self.couple_angle, -self.couple_angle)
        s += s[-1].move_polar_copy(R, 0)
        s2 = s.c_mirror_copy()
        s2.reverse()
        s2 += s
        s3 = Shape([s2[0], (0.0, s2[0][1]), (0.0, s2[-1][1]), s2[-1]])
        wg_h = Wg2El(s2, s3, self.wg_width, self.trench_width)
        wg_v = Wg2El(s2.rotate_copy((0.0, 0.0), 90).v_mirror(), s3.rotate_copy((0.0, 0.0), 90).v_mirror(), self.wg_width, self.trench_width)
        return (wg_h, wg_v)
    
    def define_wg_h(self):
        return self.get_wg_h_wg_v()[0]
    
    def define_wg_v(self):    
        return self.get_wg_h_wg_v()[1]
    
    def define_elements(self, elems):
        elems = super(RingCrossingBendGeneric, self).define_elements(self, elems)
        elems += Boundary(PPLayer(self.process,TECH.PURPOSE.LF_AREA), self.wg_h.size_info().bounding_box)
        elems += Boundary(PPLayer(self.process, TECH.PURPOSE.LF_AREA), self.wg_v.size_info().bounding_box)
        return elems
        
