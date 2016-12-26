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
from ipkiss.plugins.photonics.port import *
from ipkiss.plugins.photonics.wg import *
from ipkiss.process import ProcessProperty, PPLayer


class ThreePort(Structure):
    __name_prefix__ = "3PORT"
    width =        PositiveNumberProperty(required = True)
    height =       PositiveNumberProperty(required = True)
    wg_width =     PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH)
    trench_width=  PositiveNumberProperty(default = TECH.WG.TRENCH_WIDTH)
    process =      ProcessProperty(default = TECH.PROCESS.WG)
    
    # this init function is optional
    def __init__(self, **kwargs):
        # init functions should have **kwargs as last argument (to pass on arguments from subclasses)
        # and it should pass all arguments to its parent class

        # add initialization code here that should be executed BEFORE all properties are assigned
        # .....
        
        super(ThreePort, self).__init__(**kwargs)

        # add initialization code here that should be executed AFTER all properties are assigned
        # .....        
        
    # method for determining the name (it is an autoname structure)    
    def define_name(self):
        return "%s_W%d_H%d_W%d_T%d" % (self.__name_prefix__, 
                                       self.width*1000, 
                                       self.height*1000,
                                       self.wg_width*1000, 
                                       self.trench_width*1000)

    def define_elements(self, elems):
        # add shape elements and stuff that should only be on the waveguide layer
        elems += Rectangle(PPLayer(self.process, TECH.PURPOSE.LF.LINE), (0.0, 0.0), (self.width, self.height))
        elems += Rectangle(PPLayer(self.process, TECH.PURPOSE.LF_AREA), (0.0, 0.0), (self.width + 2*self.trench_width, self.height + 2*self.trench_width))
        return elems
        
    def define_ports(self, ports):
        wg_def = WgElDefinition(wg_width = self.wg_width, trench_width = self.trench_width)
        ports += InOpticalPort(position = (-0.5*self.width, 0.0), wg_definition = wg_def, angle = 180.0)
        ports += OutOpticalPort(position = (0.0, 0.5*self.height), wg_definition = wg_def, angle = 90.0 ) 
        ports += OutOpticalPort(position = (0.5*self.width, 0.0), wg_definition = wg_def, angle = 0.0) 
        return ports
        
        
#################################################################
# example 3b
#################################################################              
        
from ipkiss.plugins.photonics.routing.to_line import *
from ipkiss.plugins.photonics.routing.connect import *
        
class ThreePortToEast(ThreePort):
    __name_prefix__ = "3PORT_R" # other name prefix to make names unique   
    three_port = DefinitionProperty(fdef_name = "define_three_port")
    east_route = DefinitionProperty(fdef_name = "define_east_route")

    def define_three_port(self):
        # calculate info and substructures which you might need
        return ThreePort(width = self.width, 
                                    height = self.height, 
                                    wg_width = self.wg_width, 
                                    trench_width = self.trench_width)
    
    def define_east_route(self):
        return RouteToEast(input_port = self.three_port.north_ports[0])
    
    def define_elements(self, elems):
        # add other items
        elems += SRef(self.three_port) 
        elems += RouteConnectorManhattan(self.east_route)
        return elems
    
    def define_ports(self, ports):
        ports += self.three_port.west_ports
        ports += self.three_port.east_ports
        ports += self.east_route.out_ports
        return ports
        
    