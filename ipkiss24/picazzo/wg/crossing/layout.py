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
Waveguide crossings
* WgDirectCrossing: direct crossing
* WgParabolicCrossing: parabolic crossing
"""

from ipkiss.plugins.photonics.port.port import OpticalPort
from ipkiss.all import *
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty

__all__ = ["WgDirectCrossing",
           "WgParabolicCrossing"]

class __WgCrossing__(Structure):
    """ abstract base class for crossing """
    length = PositiveNumberProperty(required = True)
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc = "waveguide definition used to define the crossing")
    straight_stub = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
                                   
    def define_ports(self, ports):
        # assumes orthogonality """
        ports += [OpticalPort(wg_definition = self.wg_definition, position = (-0.5*self.length- self.straight_stub, 0.0), angle = 180),
                 OpticalPort(wg_definition = self.wg_definition, position = (0.5*self.length + self.straight_stub, 0.0), angle = 0),
                 OpticalPort(wg_definition = self.wg_definition, position = (0.0, 0.5*self.length + self.straight_stub), angle = 90),
                 OpticalPort(wg_definition = self.wg_definition, position = (0.0, -0.5*self.length - self.straight_stub), angle = -90)]
        return ports
    
    
class WgDirectCrossing(__WgCrossing__):
    """ direct waveguide crossing """
    __name_prefix__ = "DXING"
    length = DefinitionProperty(fdef_name = "define_length")

    def define_length(self):
        length = self.wg_definition.wg_width
        return length
    
    def define_elements(self, elems):
        elems += self.wg_definition(shape = [(-0.5*self.length -self.straight_stub, 0.0), (+0.5*self.length +self.straight_stub, 0.0)])
        elems += self.wg_definition(shape = [(0.0, -0.5*self.length -self.straight_stub), (0.0, +0.5*self.length +self.straight_stub)])
        return elems


class WgParabolicCrossing(__WgCrossing__):
    """ Parabolic, double-etch crossing """
    __name_prefix__ = "PXING"
    length = PositiveNumberProperty(default = 5.7)
    deep_width = PositiveNumberProperty(default = 2.6)
    shallow_width = PositiveNumberProperty(default = 0.8)
    shallow_trench_width = PositiveNumberProperty(default = 0.5)
    deep_process = ProcessProperty(default = TECH.PROCESS.WG)
    shallow_process = ProcessProperty(default = TECH.PROCESS.FC)
    
    def define_elements(self, elems):
        # WG
        length = self.length
        wg_width = self.wg_definition.wg_width
        trench_width = self.wg_definition.trench_width
        elems += ParabolicWedge(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), 
                                begin_coord = (-0.5*length, 0.0), 
                                end_coord = (0.0, 0.0), 
                                begin_width = wg_width, 
                                end_width = self.deep_width)
        elems += ParabolicWedge(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), 
                                begin_coord = (0.0, 0.0), 
                                end_coord = (0.5*length , 0.0), 
                                begin_width = self.deep_width, 
                                end_width = wg_width)
        elems += ParabolicWedge(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), 
                                begin_coord = (0.0, 0.5*length), 
                                end_coord = (0.0, 0.0), 
                                begin_width = wg_width, 
                                end_width = self.deep_width)
        elems += ParabolicWedge(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), 
                                begin_coord = (0.0, 0.0), 
                                end_coord = (0.0, -0.5*length), 
                                begin_width = self.deep_width, 
                                end_width = wg_width)
        if self.straight_stub > 0.0:
            elems += Line(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), 
                          begin_coord = ( - self.straight_stub -0.5*length, 0.0), 
                          end_coord = (0.5*self.length,0.0), 
                          line_width = wg_width)
            elems += Line(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), 
                          begin_coord = (0.0, -0.5 * length - self.straight_stub ), 
                          end_coord = (0.0, -0.5 * length), 
                          line_width = wg_width)
            elems += Line(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), 
                          begin_coord = ( 0.5*length, 0.0), 
                          end_coord = (0.5*length + self.straight_stub,0.0), 
                          line_width = wg_width)
            elems += Line(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF.LINE), 
                          begin_coord = (0.0, 0.5 * length + self.straight_stub), 
                          end_coord = (0.0*length, 0.5 * length), 
                          line_width = wg_width
                          )
        if self.length > (wg_width+2*trench_width):
            elems += Rectangle(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF_AREA), 
                               center = (0.0, 0.0), 
                               box_size = (length, length))
        elems += Line(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF_AREA), 
                      begin_coord = (-0.5*length - self.straight_stub, 0.0), 
                      end_coord = (0.5*length+self.straight_stub, 0.0), 
                      line_width = 2*trench_width+wg_width)
        elems += Line(layer = PPLayer(self.deep_process, TECH.PURPOSE.LF_AREA), 
                      begin_coord = (0.0, -0.5*length - self.straight_stub), 
                      end_coord = (0.0, 0.5*length+self.straight_stub), 
                      line_width = 2*trench_width+wg_width)
        
        # FC
        elems += ParabolicWedge(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), (-0.5*length, 0.0), (0.0, 0.0), wg_width, self.shallow_width)
        elems += ParabolicWedge(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), (0.0, 0.0), (0.5*length , 0.0), self.shallow_width, wg_width)
        elems += ParabolicWedge(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), (0.0, 0.5*length), (0.0, 0.0), wg_width, self.shallow_width)
        elems += ParabolicWedge(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), (0.0, 0.0), (0.0 , -0.5*length), self.shallow_width, wg_width)
        W1 = min(wg_width + 2*self.shallow_trench_width, self.length)
        W2 = min(self.deep_width+ 2*self.shallow_trench_width, self.length)
        elems += ParabolicWedge(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), (-0.5*length, 0.0), (0.0, 0.0), W1, W2)
        elems += ParabolicWedge(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), (0.0, 0.0), (0.5*length , 0.0), W2, W1)
        elems += ParabolicWedge(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), (0.0, 0.5*length), (0.0, 0.0), W1, W2)
        elems += ParabolicWedge(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), (0.0, 0.0), (0.0 , -0.5*length), W2, W1)
        
        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), ( - self.straight_stub -0.5*length, 0.0), (-0.5*self.length,0.0), wg_width)
        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), (0.0, -0.5 * length - self.straight_stub ), (0.0, -0.5 * length), wg_width)
        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), ( 0.5*length, 0.0), (0.5*length + self.straight_stub,0.0), wg_width)
        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), (0.0, 0.5 * length + self.straight_stub), (0.0*length, 0.5 * length), wg_width)

        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), ( - self.straight_stub -0.5*length, 0.0), (-0.5*self.length,0.0), W1)
        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), (0.0, -0.5 * length - self.straight_stub ), (0.0, -0.5 * length), W1)
        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), ( 0.5*length, 0.0), (0.5*length + self.straight_stub,0.0), W1)
        elems += Line(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), (0.0, 0.5 * length + self.straight_stub), (0.0*length, 0.5 * length), W1)
        return elems
        
