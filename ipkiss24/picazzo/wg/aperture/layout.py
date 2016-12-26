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
Apertures of one structure into another

"""

from ipkiss.plugins.photonics.port.port import OpticalPort
from ..taper import WgElTaperLinear, WgElTaperParabolic
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.all import *
from math import atan2

__all__ = ["WgApertureWrapper",
           "DeepWgAperture",
           "OpenAperture",
           "ApertureProperty",
           "ShallowWgAperture"]
           
##############################################################
## Waveguide aperture: empty base class
##############################################################
class __WgAperture__(Structure):
    """ abstract aperture base class """
    
    def angle_deg(self):
        return RAD2DEG * self.angle_rad()
    
    def aperture_shape(self, process):
        return Shape()

def ApertureProperty(internal_member_name= None, restriction = None,  **kwargs):
    R = RestrictType(__WgAperture__) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)   
    

class _WgApertureSingleProcess(__WgAperture__):
    """ abstract aperture base class on a single_process layer"""
    process = ProcessProperty(default = TECH.PROCESS.WG)
    
class WgApertureWrapper(__WgAperture__):
    structure = StructureProperty(required = True)
    center = Coord2Property(default = (0.0, 0.0))

    def define_name(self):
        return "AP_%s_C%d_%d" % (self.structure.name, self.center.x*1000, self.center.y*1000)
    
    def define_elements(self, elems):
        elems += SRef(self.structure)
        return elems
    
    def define_ports(self, ports):
        ports = self.structure.ports
        return ports
    
        
##############################################################
## Apertures into slab WG
##############################################################

class OpenAperture(__WgAperture__):
    """ Aperture into a slab area """
    __name_prefix__ = "APO"
    aperture_wg_definition = WaveguideDefProperty(required=True, doc="definition of the aperture cross-section")
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc="definition of the start waveguide")
    center = Coord2Property( default = (0.0, 0.0), doc = "center coordinate")
    taper_length = PositiveNumberProperty(default = 30.0, doc = "taper length")
    aperture_angle = AngleProperty(default = 10.0, doc = "diffraction angle of the aperture")

    def angle_deg(self):
        return self.aperture_angle
    def angle_rad(self):
        return DEG2RAD * self.aperture_angle

    def aperture_shape(self, process):
        ap_def = self.aperture_wg_definition
        return Shape([(0, -ap_def.trench_width - 0.5*ap_def.wg_width),
                          (0, -0.5*ap_def.wg_width),
                          (0, 0.5*ap_def.wg_width),
                          (0, 0.5*ap_def.wg_width + ap_def.trench_width)]
                          ).move(self.center)
    
    def define_ports(self, ports):
        ports += [OpticalPort(position = (self.center[0] + self.taper_length, self.center[1]), wg_definition = self.wg_definition, angle = 0.0)]
        return ports

class DeepWgAperture(OpenAperture):
    """Deep waveguide aperture into a slab area"""
    __name_prefix__ = "APD"
        
    def define_elements(self, elems):
        apw = self.aperture_wg_definition.wg_width
        apt = self.aperture_wg_definition.trench_width
        ww = self.wg_definition.wg_width
        wt = self.wg_definition.trench_width
        elems += Wedge(PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.LF.LINE), 
                       (self.center[0] ,  self.center[1]),
                       (self.center[0] + self.taper_length , self.center[1]), 
                       apw, 
                       ww)
        S = Shape([(0.0, + 0.5*apw),
                       (-0.1, + 0.5*apw+ 0.5*apt),
                       (0.0, + 0.5*apw+ apt),
                       (0.5*self.taper_length ,0.25*(ww +apw) + max(wt, apt)),
                       (self.taper_length ,+ 0.5*ww + wt),
                       (self.taper_length +0.1,+ 0.5*ww+ 0.5*wt),
                       (self.taper_length ,+ 0.5*ww),
                       (self.taper_length ,- 0.5*ww),
                       (self.taper_length +0.1,- 0.5*ww -0.5* wt),
                       (self.taper_length ,- 0.5*ww - wt),
                       (0.5*self.taper_length ,- 0.25*(ww +apw) - max(wt, apt)),
                       (0.0,- 0.5*apw- apt),
                       (-0.1,- 0.5*apw- 0.5*apt),
                       (0.0,- 0.5*apw)],
                      closed = True)
        S.translate(self.center)
        elems += Boundary(PPLayer(TECH.PROCESS.WG,TECH.PURPOSE.LF_AREA), S)
        return elems

    def aperture_shape(self, process):
        if process == TECH.PROCESS.WG: return OpenAperture.aperture_shape(self, process)
                          
    def define_ports(self, ports):
        ports += [OpticalPort(position = (self.center[0] + self.taper_length, self.center[1]), wg_definition = self.wg_definition, angle = 0.0)]
        return ports
    
                    
class ShallowWgAperture(OpenAperture):
    """Shallow waveguide aperture into a slab area, starting from a deep etched waveguide"""
    __name_prefix__ = "APS"
    deep_taper_length = PositiveNumberProperty(default = 15.0)
    deep_taper_width = PositiveNumberProperty(default = 3.0)
    shallow_wg_width = PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH + 0.1)
    deep_process = ProcessProperty(default = TECH.PROCESS.WG)
    shallow_process = ProcessProperty(default = TECH.PROCESS.FC)

    def define_elements(self, elems):
        apw = self.aperture_wg_definition.wg_width
        apt = self.aperture_wg_definition.trench_width
        ww = self.wg_definition.wg_width
        wt = self.wg_definition.trench_width

        # shallow part
        W = Wedge(PPLayer(self.shallow_process,TECH.PURPOSE.LF.LINE), 
                               (self.center[0] , self.center[1]), 
                               (self.center[0] + self.taper_length , self.center[1]), 
                               apw, 
                               self.shallow_wg_width)
        elems += W
        S = Shape([(0.0, + 0.5*apw),
                       (- 0.1 , 0.5*apw + 0.5* apt),                       
                       (0.0, + 0.5*apw+ apt),
                       (0.5*self.taper_length ,0.25*(self.shallow_wg_width +apw) + max(wt, apt)),
                       (self.taper_length ,+ 0.5*self.shallow_wg_width + wt),
                       (self.taper_length +0.1 ,+ 0.5*self.shallow_wg_width+ 0.5 *wt),
                       (self.taper_length ,+ 0.5*self.shallow_wg_width),
                       (self.taper_length ,- 0.5*self.shallow_wg_width),
                       (self.taper_length +0.1 ,- 0.5*self.shallow_wg_width- 0.5 * wt),
                       (self.taper_length ,- 0.5*self.shallow_wg_width - wt),
                       (0.5*self.taper_length ,- 0.25*(self.shallow_wg_width +apw) - max(wt, apt)),
                       (0.0,- 0.5*apw- apt),
                       (- 0.1, -0.5*apw - 0.5* apt),                       
                       (0.0,- 0.5*apw)],
                      closed = True)
        S.translate(self.center)
        elems += Boundary(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), S)

        # deep part
        W = Wedge(PPLayer(self.deep_process,TECH.PURPOSE.LF.LINE), 
                        (self.center[0] +  (self.taper_length - self.deep_taper_length),self.center[1]), 
                        (self.center[0] + self.taper_length, self.center[1]), 
                        self.deep_taper_width, 
                        ww)
        elems += W
        S = Shape([(self.taper_length - self.deep_taper_length, + 0.5*self.deep_taper_width),
                       (self.taper_length - self.deep_taper_length-0.1, + 0.5*self.deep_taper_width + 0.5*apt),
                       (self.taper_length - self.deep_taper_length, + 0.5*self.deep_taper_width + apt),
                       (self.taper_length - 0.5*self.deep_taper_length  ,0.25*(ww +self.deep_taper_width) + wt),
                       (self.taper_length ,+ 0.5*ww + wt),
                       (self.taper_length +0.1,+ 0.5*ww + 0.5*wt),
                       (self.taper_length ,+ 0.5*ww),
                       (self.taper_length ,- 0.5*ww),
                       (self.taper_length +0.1,- 0.5*ww-0.5* wt),
                       (self.taper_length ,- 0.5*ww - wt),
                       (self.taper_length - 0.5*self.deep_taper_length  ,- 0.25*(ww +self.deep_taper_width) - wt),
                       (self.taper_length - self.deep_taper_length,- 0.5*self.deep_taper_width- apt),
                       (self.taper_length - self.deep_taper_length-0.1, - 0.5*self.deep_taper_width - 0.5*apt),
                       (self.taper_length - self.deep_taper_length,- 0.5*self.deep_taper_width)],
                      closed = True)
        S.translate(self.center)
        elems += Boundary(PPLayer(self.deep_process, TECH.PURPOSE.LF_AREA), S)
        return elems

    def aperture_shape(self, process):
        if process == self.shallow_process: 
            return OpenAperture.aperture_shape(self, process)
        else:
            ap_def = self.aperture_wg_definition
            return Shape([(0, -self.apdef.trench_width - 0.5*self.deep_taper_width),
                              (0, -0.5*self.deep_taper_width),
                              (0, 0.5*self.deep_taper_width),
                              (0, 0.5*self.deep_taper_width+ self.ap_def.trench_width)]
                              ).rotate((0.0,0.0),self.aperture_angle).move(self.center)
                
        
    def define_ports(self, ports):
        ports += [OpticalPort(position = (self.center[0] + self.taper_length, self.center[1]), wg_definition = self.wg_definition, angle = 0.0)]
        return ports



