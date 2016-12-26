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
Bend structures and elements
Not yet based on waveguide definitions
"""


from ipkiss.all import *
from ipkiss.plugins.photonics.port.port import InOpticalPort, OutOpticalPort
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.plugins.photonics.wg.connect import WaveguidePointRoundedConnectElementDefinition, __RoundedWaveguide__
from math import cos, sin, tan

__all__ = ["WgElBend",
           "Wg90Bend"
           ]
           

#############################
# generic bend
##############################

class __WgElBend__(__RoundedWaveguide__, Group):
    """ Base class for bend elements """
    start_point = Coord2Property(default = (0.0, 0.0), doc = "start coordinate of the bend")
    start_angle = AngleProperty(default = 0.0, doc = "start angle of the bend")
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc = "waveguide definition of the bend")
    angle = AngleProperty(default = 90.0, restriction = RestrictRange(lower = -180.0, upper = +180.0, lower_inc = False, upper_inc = False), doc="angle of arc span by bend")
    center_shape = DefinitionProperty(fdef_name="define_center_shape") # should be read_only   
    center =  DefinitionProperty(fdef_name="define_center") # should be read_only   
    end_angle =  DefinitionProperty(fdef_name="define_end_angle") # should be read_only   
    end_point =  DefinitionProperty(fdef_name="define_end_point") # should be read_only   
    manhattan = BoolProperty(default = False)
    
    def define_center_shape(self):
        RA = self.rounding_algorithm
        return RA(original_shape = self.get_control_shape(),
                  radius = self.bend_radius)
    
    def define_center(self):
        return self.center_shape.center
    
    def define_end_angle(self):
        return  self.start_angle + self.angle
    
    def define_end_point(self):
        return self.center_shape[-1]    
    
    def define_ports(self, ports):
        ports += [InOpticalPort(position = self.start_point, wg_definition = self.wg_definition, angle = self.start_angle + 180.0),
                OutOpticalPort(position = self.end_point, wg_definition = self.wg_definition, angle = self.end_angle)]
        return ports
    
    @cache()
    def get_connect_wg_definition(self):
        return WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition, 
                                                             bend_radius = self.bend_radius ,
                                                             rounding_algorithm = self.rounding_algorithm,
                                                             manhattan = self.manhattan) 

    def define_elements(self, elems):
        rwd = self.get_connect_wg_definition()
        elems += rwd(shape = self.get_control_shape())
        return elems
    
class WgElBend(__WgElBend__):
    
    @cache()
    def get_control_shape(self):
        bs1, bs2 = self.get_bend_size(self.angle)
        cs = Shape([(-bs1, 0.0),
                    (0.0, 0.0), 
                    (bs2*cos(self.angle*DEG2RAD), bs2 * sin(self.angle * DEG2RAD))])
    
        cs.move(-cs[0])
        cs.rotate(rotation = self.start_angle)
        cs.move(self.start_point)
        return cs
        
    

##############################
# 90 degree abstract base class
##############################

# 90 degree bend in structure (abstract)
class Wg90Bend(__RoundedWaveguide__, Structure):
    """ 90 degree bend structure """
    __name_prefix__ = "bend_w90i"
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc = "waveguide definition of the bend")
    quadrant = IntProperty(restriction = (RestrictRange(-4, -1, True, True) | RestrictRange(1, 4, True, True)), required = True, doc = "quadrant of the bend (-4=>4)")
    manhattan = BoolProperty(default = False)
            
    @cache()
    def get_bend(self):
        if self.quadrant>0 and self.quadrant <=4:
            start_angle = (self.quadrant) * 90
            angle = 90.0
        if self.quadrant<0 and self.quadrant >=-4:
            start_angle = (self.quadrant) * 90
            angle = -90.0

        if self.quadrant < 0.0:
            start_angle = (self.quadrant) * 90
        else:            
            start_angle = (self.quadrant) * 90

        return WgElBend(start_angle = start_angle,
                        bend_radius = self.bend_radius ,
                        angle = angle,
                        wg_definition = self.wg_definition,
                        rounding_algorithm = self.rounding_algorithm,
                        manhattan = self.manhattan)
                        
    def define_elements(self, elems):
        elems += self.get_bend()
        return elems

    def define_ports(self, ports):
        ports += self.get_bend().ports
        return ports



