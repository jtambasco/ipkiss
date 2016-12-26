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
Sockets for fiber couplers

"""

from ipkiss.plugins.photonics.port.port import OpticalPort
from picazzo.wg.tapers.linear import WgElTaperLinear
from picazzo.wg.tapers.parabolic import WgElTaperParabolic
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.all import *
from math import atan2

__all__ = ["BroadWgSocket",
           "TaperSocket",
           "OpenApertureSocket",
           "SocketProperty",
           "LinearTaperSocket"]

class __WgSocket__(Structure):
    """ abstract aperture base class """
    def angle_deg(self):
        return RAD2DEG * self.angle_rad()
    
    def aperture_shape(self, process):
        return Shape()
    
def SocketProperty(internal_member_name= None, restriction = None,  **kwargs):
    R = RestrictType(__WgSocket__) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)

class BroadWgSocket(__WgSocket__):
    __name_prefix__ = "SWGAP"
    """ Broad waveguide socket """
    wg_definition = WaveguideDefProperty(required=True)
    wg_length = PositiveNumberProperty(default = 50.0)

    def define_name(self):
        return "%s_%d_%d_%d_%s"%(self.__name_prefix__,self.wg_definition.wg_width*1000,
                                 self.wg_definition.trench_width*1000, self.wg_length*1000,
                                 self.wg_definition.process.extension)
    
    def define_elements(self, elems):
        elems += self.wg_definition(shape = [(0.0,0.0), (self.wg_length, 0.0)])
        return elems
    
    def define_ports(self, ports):
        ports += [OpticalPort(position = (0.0, 0.0), wg_definition = self.wg_definition, angle = 180.0),
                 OpticalPort(position = (self.wg_length, 0.0), wg_definition = self.wg_definition, angle = 0.0)]
        return ports
    
class TaperSocket(__WgSocket__):
    "Base class for an aperture consisting of a taper"
    __name_prefix__ = "TAPS"
    start_wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc = "waveguide definition at the start")
    end_wg_definition = WaveguideDefProperty(required=True, doc = "waveguide definition at the end")
    length = PositiveNumberProperty(default = 20.0)
    center = Coord2Property(default = (0.0, 0.0))
    extension = NonNegativeNumberProperty(default = 0.0)
    straight_extension = NonNegativeNumberProperty(default = 0.5)
    straight_entrance = NonNegativeNumberProperty(default=0.0)                    

    def define_ports(self, ports):
        ports += [OpticalPort(position = self.center.move_copy((self.length + self.straight_entrance, 0.0)), wg_definition = self.start_wg_definition, angle = 0.0)]
        return ports

    def angle_rad(self):
        #return 2* atan2(0.5* (self.start_width), self.length) 
        return 2* atan2(0.5* (self.end_wg_definition.wg_width), self.length)
        # end width is not included, because the approximation goes for a gaussian beam
        
class LinearTaperSocket(TaperSocket):
    __name_prefix__ = "LTAPS"
    
    def define_elements(self, elems):
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition
        if self.extension != 0.0:
            extended_start_width = self.start_wg_definition.wg_width + (self.end_wg_definition.wg_width-self.start_wg_definition.wg_width)  * (self.extension + self.length- self.straight_extension)/self.length
        else:
            extended_start_width = self.end_wg_definition.wg_width
        end_wg_def = WgElDefinition(wg_width = extended_start_width, trench_width = self.end_wg_definition.trench_width, process = self.end_wg_definition.process)
        end_wg_def_ext = WgElDefinition(wg_width = extended_start_width+0.05, trench_width = self.end_wg_definition.trench_width-0.05, process = self.end_wg_definition.process)

        elems += WgElTaperLinear(start_position = (self.center[0] - self.extension ,self.center[1]),
                                 end_position = (self.center[0] + self.length, self.center[1]), 
                                 start_wg_def = end_wg_def,
                                 end_wg_def = self.start_wg_definition,
                                 straight_extension = (0.0, 0.0))
        if self.straight_extension > 0:
            elems += WgElTaperLinear(start_position = (self.center[0] - self.extension, self.center[1]),
                                     end_position = (self.center[0] - self.extension - self.straight_extension, self.center[1]), 
                                     start_wg_def = end_wg_def,
                                     end_wg_def = end_wg_def_ext,
                                     straight_extension = (0.0, 0.0))
   
        if self.straight_entrance > 0.0:
            elems += self.start_wg_definition(shape = [(self.center[0] + self.length ,self.center[1]), (self.center[0] + self.length + self.straight_entrance, self.center[1])])

        return elems
    

class OpenApertureSocket(__WgSocket__):
    __name_prefix__ = "OPENSOCKET"
    aperture = StructureProperty(required = True)
    aperture_center = Coord2Property(default = (0.0, 0.0))
    
    def define_elements(self, elems):
        elems += SRef(reference = self.aperture, position= self.aperture_center)
        return elems
    
    def define_ports(self, prts):
        prts += self.aperture.ports.move_copy(self.aperture_center)
        return prts