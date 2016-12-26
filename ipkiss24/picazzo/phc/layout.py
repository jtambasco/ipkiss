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

from ipkiss.all import *
from .holes import HexHole, DodecHole
from ..log import PICAZZO_LOG as LOG
from math import sqrt

__all__ = ["PhCLayout",
           "HexPhcLayout",
           "DodecPhCLayout",
           "TriangularPhCLayout"]

def PhCCellsProperty(internal_member_name = None, restriction = None,  **kwargs): # should be refined
    R = RestrictType(dict) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)

def PhcMapProperty(internal_member_name = None, restriction = None,  **kwargs): # should be refined
    R = restriction
    return StringProperty(internal_member_name, restriction = R, **kwargs)

def PhCHolesProperty(internal_member_name = None, restriction = None,  **kwargs): # should be refined
    R = RestrictType(dict) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)

class PhCLayout(Structure):
    pitches = Size2Property(required = True)
    cells = PhCCellsProperty(required = True)
    map = PhcMapProperty(required = True)
    process_hfw = ProcessProperty(default = TECH.PROCESS.HFW)
    zero_line_y = NumberProperty(default = 0, doc = "Which line is located at zero")
    ports_coordinates = RestrictedProperty(default = [], doc="list of tuple with (coordinate (in pitches), angle, waveguide_definition)")
    
    def define_elements(self, elems):
        lines = self.map.splitlines()
        nothing_added = True
        lines.reverse()
        ypos = -(len(lines) - self.zero_line_y) * self.pitches[1]
        maxlen = 0
        for line in lines:
            # find repetitions
            patterns = line.split("/")
            xpos = 0.0
            t = 0
            for p in patterns:
                # check if there is a repetition
                q = p.split(",")
                if len(q) == 1:
                    for char in q[0]:
                        if char in self.cells:
                            nothing_added = False
                            elems += SRef(self.cells[char], (xpos, ypos))
                        xpos += self.pitches[0]
                        t += 1
                elif len(q) == 2:
                    n_o_periods = int(q[0])
                    content = q[1]
                    period = len(content) * self.pitches[0]
                    if n_o_periods < 0:
                        LOG.error("Wrong syntax in repetions (invalid number of periods)")
                        raise AttributeError
                    if period <= 0.0:
                        LOG.error("Wrong syntax in repetions (content of period is empty)")
                        raise SystemExit
                    for char in content:
                        if char in self.cells:
                            nothing_added = False
                            elems+= ARefX(self.cells[char], (xpos, ypos), period, n_o_periods)
                        xpos += self.pitches[0]
                        t += n_o_periods
                    xpos += period * (n_o_periods -1)

                elif len(q) > 2 or len(q) < 0:
                    LOG.error("Wrong syntax in repetions (do not use , or / in patterns)")
                    raise AttributeError
            maxlen = max([t, maxlen])
            ypos += self.pitches[1]
            
        if nothing_added:
            LOG.error("map is empty")
            raise SystemExit

        # HFW
        elems += Rectangle(PPLayer(self.process_hfw, TECH.PURPOSE.DF.TRENCH), 
                        center=((maxlen/2.0-0.5)* self.pitches[0], self.pitches[1]*( self.zero_line_y -len(lines)/2.0 -0.5)), 
                        box_size = ((maxlen+2) * self.pitches[0], ((len(lines) + 2)*self.pitches[1]))
                        )
        
        return elems

    def define_ports(self,prts):
        from ipkiss.plugins.photonics.port.port import OpticalPort
        for coord, angle, wg_def in self.ports_coordinates:
            p = OpticalPort(position = (self.pitches[0] * coord[0], self.pitches[1] * coord[1]),
                            angle_deg = angle,
                            wg_definition = wg_def
                            )
            prts += p
        return prts
    
class TriangularPhCLayout(PhCLayout):        
    pitches = DefinitionProperty(fdef_name = "define_pitches")
    lattice_pitches = Size2Property(required = True)
       
    def define_pitches(self):
        pitches = (0.5 * self.lattice_pitches[0], sqrt(0.75)*self.lattice_pitches[1])
        return pitches

    def define_ports(self,prts):
        from ipkiss.plugins.photonics.port.port import OpticalPort
        for coord, angle, wg_def in self.ports_coordinates:
            p = OpticalPort(position = (self.lattice_pitches[0] * coord[0], self.lattice_pitches[1]*sqrt(3.0) * coord[1]),
                            angle_deg = angle,
                            wg_definition = wg_def
                            )
            prts += p
        return prts
    
    
class RectangularPhCLayout(PhCLayout):        
    pitches = DefinitionProperty(fdef_name = "define_pitches")
    lattice_pitches = Size2Property(required = True)
       
    def define_pitches(self):
        pitches = (0.5 * self.lattice_pitches[0], 0.5*self.lattice_pitches[1])
        return pitches

class __HolePhCLayout__(TriangularPhCLayout):
    cells = DefinitionProperty(fdef_name = "define_cells")
    lattice_pitches = DefinitionProperty(fdef_name = "define_lattice_pitches")
    process_wg = ProcessProperty(default  = TECH.PROCESS.WG)
    hole_sizes = PhCHolesProperty(required = True)
    pitch = NonNegativeNumberProperty(required = True)                                               

    def define_lattice_pitches(self):
        lattice_pitches = (self.pitch, self.pitch)
        return lattice_pitches
        
    def define_cells(self):
        cells = {}
        for c in self.hole_sizes:
            s = self.hole_sizes[c]
            if s == 0:
                continue
            cells[c] = self.hole(radius = s/2.0, process = self.process_wg)
        return cells

    
class HexPhcLayout(__HolePhCLayout__):
    hole = HexHole

    
class DodecPhCLayout(__HolePhCLayout__):
    hole = DodecHole

class __PhCAutoMap__(object):
    map = DefinitionProperty(fdef_name = "define_map")
    
    def define_map(self):
        raise NotImplementedException("Function 'define_maps' to be implemented by subclass of __PhCAutoMap__")
    
    
        
        
        
