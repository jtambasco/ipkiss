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
from ipkiss.plugins.photonics.port.port import InOpticalPort, OutOpticalPort, OpticalPortProperty
from ipkiss.aspects.port import PortAspect
#from ipkiss.plugins.photonics.port.aspect import OpticalPortAspect
from ipkiss.plugins.photonics.wg.connect import __RoundedShape__

__all__ = ["Route"]

class Route(__RoundedShape__, PortAspect, Shape):
    
    min_straight = NonNegativeNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    input_port = OpticalPortProperty(required = True)

    def define_ports(self, ports):  
        a = self.angles_deg()
        ports += [InOpticalPort(position = self[0], angle = a[0] + 180.0, wg_definition = self.input_port.wg_definition), 
                      OutOpticalPort(position = self[-1], angle = a[-2], wg_definition = self.input_port.wg_definition)]
        return ports
    
    def route_length(self):
        RA = self.rounding_algorithm
        return RA(original_shape = self, radius = self.bend_radius).length()

    def __add__(self, pointlist):
        points = Shape.__add__(self, pointlist)
        return self.modified_copy(points = points)

    
    
class __RouteBasic__(Route):
    """ base class for routing: creates a shape with control points based on ports etc. which can be used in 
        wg_el_connect_point connectors """
    end_straight = NonNegativeNumberProperty(allow_none = True)
    start_straight = NonNegativeNumberProperty(allow_none = True)
    
    def __init__(self, input_port, bend_radius = TECH.WG.BEND_RADIUS, min_straight = TECH.WG.SHORT_STRAIGHT, **kwargs):
        if not 'start_straight' in kwargs: 
            kwargs['start_straight'] = min_straight
        if not 'end_straight' in kwargs: 
            kwargs['end_straight'] = min_straight
        super(__RouteBasic__, self).__init__(input_port = input_port,
                                          bend_radius = bend_radius,
                                          min_straight = min_straight,
                                          **kwargs)
        


