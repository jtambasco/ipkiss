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

# Example: Using routes to build a component
# A directional coupler is constructed by defining two routes
# with different waveguide definitions.

from ipkiss.all import *
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.plugins.photonics.port import InOpticalPort

# First, we define a simple directional coupler which consists of 
# two straight parallel waveguides
class DirectionalCoupler(Structure):
    """ A directional coupler class, made by two parallel waveguides 
        """
    
    __name_prefix__ = "DIRCOUP"  
        
    wg_def_1 = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc = "waveguide definition for upper arm")
    wg_def_2 = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc = "waveguide definition for lower arm")
    coupler_spacing = PositiveNumberProperty(default = TECH.WG.DC_SPACING, 
                                             doc = "spacing between the two waveguide centerlines")
    coupler_length = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT, 
                                             doc = "length of the directional coupler")
    
    def validate_properties(self):
        """ check whether the combination of properties is valid """
        if self.coupler_spacing <= 0.5*(self.wg_def_1.wg_width + self.wg_def_2.wg_width):
            return False # waveguides would touch: Not OK 
        return True # no errors


    @cache()
    def get_waveguide_routes(self):
        """ routes are shapes which have also some information about the waveguide
            they need to draw"""
        from ipkiss.plugins.photonics.routing.basic import Route
        
        # simple, static, user-defined route (only a straight line)
        r1 = Route(points = [(0, 0.5*self.coupler_spacing), (self.coupler_length, 0.5*self.coupler_spacing)],
                    input_port = InOpticalPort(position = (0, 0.5*self.coupler_spacing), 
                                               angle = 180.0,
                                               wg_definition = self.wg_def_1)
                    )
        r2 = Route(points = [(0, -0.5*self.coupler_spacing), (self.coupler_length, -0.5*self.coupler_spacing)],
                    input_port = InOpticalPort(position = (0, -0.5*self.coupler_spacing), 
                                               angle = 180.0,
                                               wg_definition = self.wg_def_2)
                    )

        return r1, r2
    
    def define_elements(self, elems):
        from ipkiss.plugins.photonics.routing.connect import RouteConnectorRounded
        r1, r2= self.get_waveguide_routes()
        
        elems += RouteConnectorRounded(route = r1)
        elems += RouteConnectorRounded(route = r2)
        return elems
    
    def define_ports(self, prts):
        # calculate ports from the shape, instead of hard-coded
        r1, r2 = self.get_waveguide_routes()
        prts += r1.ports
        prts += r2.ports
        return prts

# In this child class, we add bends on each end of the directional coupler
class BentDirectionalCoupler(DirectionalCoupler):
    """ a directional coupler with bends on each side """
    
    bend_radius =         PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    bend_angle =          AngleProperty(default = 45.0, restriction = RestrictRange(0,90, True, True)) # angle between 0 and 90 degrees, including 0 and 90
    straight_after_bend = PositiveNumberProperty (default = TECH.WG.SHORT_STRAIGHT)
    
    # we need only to override the waveguide_routes. the rest of the parent class is reused!    
    @cache()
    def get_waveguide_routes(self):
        """ routes are shapes which have also some information about the waveguide
            they need to draw"""
        from ipkiss.plugins.photonics.routing.to_line import RouteToAngle
        from ipkiss.plugins.photonics.routing.basic import Route
        
        # retrieve the routes for the straight section from the parent class
        r1s, r2s = super(BentDirectionalCoupler, self).get_waveguide_routes()
        
        # define a section on each end to bend towards the correct angle
        r1_start = RouteToAngle(input_port = r1s.ports[0], angle_out = 180.0 - self.bend_angle, 
                                bend_radius = self.bend_radius, 
                                start_straight = 0.0, end_straight = self.straight_after_bend)
        r1_end = RouteToAngle(input_port = r1s.ports[-1], angle_out = self.bend_angle, 
                              bend_radius = self.bend_radius, 
                                start_straight = 0.0, end_straight = self.straight_after_bend)
        r1 = r1_start.reversed() + r1s + r1_end

        
        r2_start = RouteToAngle(input_port = r2s.ports[0], angle_out = 180.0 + self.bend_angle, 
                                bend_radius = self.bend_radius, start_straight = 0.0)
        r2_end = RouteToAngle(input_port = r2s.ports[-1], angle_out = -self.bend_angle, 
                              bend_radius = self.bend_radius, start_straight = 0.0)
        r2 = r2_start.reversed() + r2s + r2_end # add the pieces together

        return r1, r2
    

if __name__ == "__main__":
    print "This is not the main file. Run 'execute.py' in the same folder"