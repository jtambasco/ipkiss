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

from .marker import OverlayMarker
from ipkiss.all import *
from ipkiss.process import PPLayer

__all__ = ["VernierMarkerH", "VernierMarkerV"]

class __VernierMarker__(StrongPropertyInitializer):
    inner_marks_width = PositiveNumberProperty(default=5.0)
    outer_marks_width = PositiveNumberProperty(default=8.0)
    marks_length = PositiveNumberProperty(default=30.0)
    outer_pitch = PositiveNumberProperty(default=20.25)
    inner_pitch = DefinitionProperty(fdef_name = 'define_inner_pitch')
    n_o_lines = PositiveNumberProperty(default=9)
    no_fill_clearing = NonNegativeNumberProperty(default = 10.0)
    def define_inner_pitch(self):
        return self.outer_pitch - (self.outer_marks_width - self.inner_marks_width)/(self.n_o_lines-1)
    
class VernierMarkerH(OverlayMarker,__VernierMarker__):
    __name_prefix__ = "VERNIER_H"
    
    def define_elements(self, elems):
        if self.overlay_process != TECH.PROCESS.NONE:
            HI1 = VernierMarkHI(layer=PPLayer(self.overlay_process, self.overlay_purpose),marks_width=self.inner_marks_width,marks_length=self.marks_length)
            elems += ARefX(HI1, (self.outer_pitch + self.outer_marks_width - self.inner_marks_width, 0.0), self.inner_pitch, self.n_o_lines)

        if self.master_process != TECH.PROCESS.NONE:
            HO1 = VernierMarkHO(layer=PPLayer(self.master_process, self.master_purpose),marks_width=self.outer_marks_width,marks_length=self.marks_length)
            elems += ARefX(HO1, (self.outer_pitch, 0.0), self.outer_pitch, self.n_o_lines)
        si = elems.size_info()
        elems += Rectangle(layer = PPLayer(TECH.PROCESS.NONE, TECH.PURPOSE.NO_FILL),
                      center = si.center,
                      box_size = (si.width + 2*self.no_fill_clearing, si.height + 2*self.no_fill_clearing)
                      )
        elems += Rectangle(layer = PPLayer(TECH.PROCESS.NONE, TECH.PURPOSE.NO_FILL),
                      center = si.center,
                      box_size = (si.width + 2*self.no_fill_clearing, si.height + 2*self.no_fill_clearing)
                      )

        return elems

class VernierMarkerV(OverlayMarker,__VernierMarker__):
    __name_prefix__ = "VERNIER_V"

    def define_elements(self, elems):
        elems = ElementList()
        if self.overlay_process != TECH.PROCESS.NONE:
            VI1 = VernierMarkVI(layer=PPLayer(self.overlay_process, self.overlay_purpose),marks_width=self.inner_marks_width,marks_length=self.marks_length)
            elems += ARefY(VI1, (0.0, self.outer_pitch + self.outer_marks_width - self.inner_marks_width ),  self.inner_pitch, self.n_o_lines)

        if self.master_process != TECH.PROCESS.NONE:
            VO1 = VernierMarkVO(layer=PPLayer(self.master_process, self.master_purpose),marks_width=self.outer_marks_width,marks_length=self.marks_length)
            elems += ARefY(VO1, (0.0, self.outer_pitch ), self.outer_pitch, self.n_o_lines)
        si = elems.size_info()
        elems += Rectangle(layer = PPLayer(TECH.PROCESS.NONE, TECH.PURPOSE.NO_FILL),
                      center = si.center,
                      box_size = (si.width + 2*self.no_fill_clearing, si.height + 2*self.no_fill_clearing)
                      )
        elems += Rectangle(layer = PPLayer(TECH.PROCESS.NONE, TECH.PURPOSE.NO_FILL),
                      center = si.center,
                      box_size = (si.width + 2*self.no_fill_clearing, si.height + 2*self.no_fill_clearing)
                      )
        return elems


class __SingleVernierMark__(Structure):
    layer = LayerProperty(required = True)
    marks_width = FloatProperty(default=5.0)
    marks_length = FloatProperty(default=30.0)
    
       
class VernierMarkHI(__SingleVernierMark__):
    __name_prefix__ = "VERNIER_HI"
    
    def define_elements(self, elems):
        elems += Rectangle(self.layer, (0.5*self.marks_width, 0.5*self.marks_length-1), (self.marks_width, self.marks_length))
        return elems

class VernierMarkHO(__SingleVernierMark__):
    __name_prefix__ = "VERNIER_HO"
    
    def define_elements(self, elems):
        elems += Rectangle(self.layer, (0.5*self.marks_width, -0.5*self.marks_length+1), (self.marks_width, self.marks_length))
        return elems

class VernierMarkVI(__SingleVernierMark__):
    __name_prefix__ = "VERNIER_VI"
    
    def define_elements(self, elems):
        elems += Rectangle(self.layer, (0.5*self.marks_length-1, 0.5*self.marks_width), (self.marks_length, self.marks_width ))
        return elems
        
class VernierMarkVO(__SingleVernierMark__):
    __name_prefix__ = "VERNIER_VO"
    
    def define_elements(self, elems):
        elems += Rectangle(self.layer, (-0.5*self.marks_length+1, 0.5*self.marks_width), (self.marks_length, self.marks_width ))
        return elems
