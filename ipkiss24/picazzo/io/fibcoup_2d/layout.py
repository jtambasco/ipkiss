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



from ..io_array import IoPeriodicArray
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.port.port import OpticalPort, OutOpticalPort
from picazzo.wg.tapers.parabolic import WgElTaperParabolic
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.all import *
from math import cos, sin, tan
from ipcore.properties.predefined import FloatProperty

#################################
# 2D fibre coupler with tapers
#################################

__all__ = ["IoSingleSided2dFibcoup",
           "IoDoubleSided2dFibcoupArray",
           "IoSingleSided2dFibcoup",
           "IoSingleSided2dFibcoupArray",
           "FibcoupDuplex3Port",
           "FibcoupDuplex4Port"]

#base class !
class Io2dFibcoup(Structure):
    """base class for 2D fibre couplers with inputs and outputs"""
    __name_prefix__ = "Io2dFibcoup"

    fibcoup = StructureProperty(required = True)
    taper_length = PositiveNumberProperty(default = 250.0)
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    waveguide_overlap = PositiveNumberProperty(default = 0.0)
    min_straight_wire = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    
    start_coords = DefinitionProperty(fdef_name = "define_start_coords")
    end_coords = DefinitionProperty(fdef_name = "define_end_coords")
    start_coords_end_coords = DefinitionProperty(fdef_name = "define_start_coords_end_coords")        
    
    
    def define_elements(self, elems):
        elems += SRef(self.fibcoup,(0.0,0.0))
        return elems
    
    @cache()
    def define_start_coords_end_coords(self):
        start_coords = OpticalPortList()
        end_coords = OpticalPortList()
        
        for p in self.fibcoup.optical_ports:
            start_coords += p
            end_coords += OpticalPort(position = p.position.move_polar_copy(self.taper_length, p.angle_deg), wg_definition = self.wg_definition, angle = p.angle_deg)
        return (start_coords, end_coords)
    
    def define_start_coords(self):
        return self.start_coords_end_coords[0]

    def define_end_coords(self):
        return self.start_coords_end_coords[1]    
                       
    def add_taper(self,elems, angle_start,angle_end):
        sp = self.start_coords.get_ports_within_angles(angle_start,angle_end)
        ep = self.end_coords.get_ports_within_angles(angle_start,angle_end)
        
        wg_ext = 0.1
        for i in range(0,len(sp)):
            elems += WgElTaperParabolic(start_position = sp[i].position, end_position = ep[i].position, 
                                        start_wg_def = sp[i].wg_definition, end_wg_def = ep[i].wg_definition)
        return elems
            

            
class IoSingleSided2dFibcoupBase(Io2dFibcoup):
    __name_prefix__ = "Io2dFibcoup_ss"
    
    def define_elements(self, elems):
        elems += SRef(self.fibcoup,(0.0,0.0))
        elems = self.add_taper(elems, 0.0,90.0)
        elems = self.add_taper(elems, 270.0,360.0)
        return elems
                    
    def define_ports(self, ports):
        for port in self.end_coords.get_ports_within_angles(270.0,90.0):
            port = OutOpticalPort(wg_definition = port.wg_definition, position = port.position, angle = port.angle)
            ports += port
        return ports
        
            
def IoSingleSided2dFibcoup(wg_definition = TECH.WGDEF.WIRE, taper_length=250.0):
    return IoSingleSided2dFibcoupBase(fibcoup = TECH.IO.FIBCOUP.DEFAULT_2D_GRATING,wg_definition = wg_definition,taper_length = taper_length)

class IoDoubleSided2dFibcoupBase(Io2dFibcoup):
    __name_prefix__ = "Io2dFibcoup_ds"
        
    def define_elements(self, elems):
        elems += SRef(self.fibcoup,(0.0,0.0))
        elems = self.add_taper(elems,0.0,90.0)
        elems = self.add_taper(elems,90.0,180.0)
        elems = self.add_taper(elems,180.0,270.0)
        elems = self.add_taper(elems,270.0,360.0)
        return elems
                    
    def define_ports(self, ports):
        ports = self.end_coords
        return ports

def IoDoubleSided2dFibcoup(wg_definition = TECH.WGDEF.WIRE, taper_length=250.0):
    return IoDoubleSided2dFibcoupBase(fibcoup = TECH.IO.FIBCOUP.DEFAULT_2D_GRATING,wg_definition = wg_definition, taper_length = taper_length)


class FibcoupDuplex4Port(Io2dFibcoup):
    __name_prefix__ = "FibcoupDuplex4Port"
    port_angle_decision = FloatProperty(default = 120.0)
    
        
    def define_elements(self, elems):
        elems += SRef(self.fibcoup,(0.0,0.0))
        elems = self.add_taper(elems,0.0,90.0)
        elems = self.add_taper(elems,90.0,180.0)
        elems = self.add_taper(elems,180.0,270.0)
        elems = self.add_taper(elems,270.0,360.0)
        return elems
        
    def define_ports(self, ports):
        ports = self.end_coords
        return ports
    
        
class FibcoupDuplex3Port(Io2dFibcoup):
    __name_prefix__ = "FibcoupDuplex3Port"
               
    def define_elements(self, elems):
        elems += SRef(self.fibcoup,(0.0,0.0))
        elems = self.add_taper(elems,0.0,90.0)
        elems = self.add_taper(elems,270.0,360.0)
        elems = self.add_taper(elems,135.0,225.0)
        return elems
        
    def define_ports(self, ports):
        ports = self.end_coords
        return ports
        
        
############################################
# 1D array of 2D fibre couplers 
#   for connecting to an array connector
############################################
           
def IoSingleSided2dFibcoupArray(num_fibcoup=4, wg_definition = TECH.WGDEF.WIRE, spacing=250.0):
    FC = IoSingleSided2dFibcoup(wg_definition,140.0) 
    return IoPeriodicArray(FC, num_fibcoup, spacing)

           
def IoDoubleSided2dFibcoupArray(num_fibcoup=4, wg_definition =TECH.WGDEF.WIRE, spacing=250.0):
    FC = IoDoubleSided2dFibcoup(wg_definition,140.0) 
    return IoPeriodicArray(FC, num_fibcoup, spacing, library)

        
    
