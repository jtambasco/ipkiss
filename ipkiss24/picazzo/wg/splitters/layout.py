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
from ..bend import Wg90Bend
from ipkiss.plugins.photonics.port.port import  InOpticalPort, OutOpticalPort
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.all import *
from math import *

__all__ = ["WgY180Combiner",
           "WgY180Splitter",
           "WgY90Combiner",
           "WgY90Splitter"]
           


    
# structures
class __WgYSplitter__(Structure):
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc = "waveguide definition of the Y splitter")
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)

class WgY90Splitter(__WgYSplitter__):
    """ Y-splitter structure with branches perpendicular to input waveguide """

    __name_prefix__ = "Y90_splitter_"
    
    def define_elements(self, elems):
        wg_width = self.wg_definition.wg_width
        trench_width = self.wg_definition.trench_width
        process = self.wg_definition.process
        
        shape = Shape()
        shape.append((-2.0, 0.5*wg_width))
        shape.append((-0.1, 0.5*wg_width))
        shape += ShapeArc(center = (0.0, 0.5 * wg_width + self.bend_radius), 
                           radius = self.bend_radius - 0.5 * wg_width, 
                           start_angle = -90.0, 
                           end_angle = 0.0)

       
        a1 = RAD2DEG * acos((self.bend_radius-0.07+ 0.5*wg_width)/(self.bend_radius+0.5 * wg_width))
        shape += ShapeArc(center = (0.0, 0.5 * wg_width + self.bend_radius), 
                           radius = self.bend_radius + 0.5 * wg_width, 
                           start_angle = 0, 
                           end_angle = -90.0 + a1, 
                           clockwise = True)

        shape2 = shape.v_mirror_copy()
        shape2.reverse()
        shape += shape2
        shape.close()
        elems += Boundary(PPLayer(process, TECH.PURPOSE.LF.LINE), shape)

        # inversion layer
        a1 = RAD2DEG * acos((self.bend_radius-0.07+ 0.5*wg_width)/(self.bend_radius+0.5 * wg_width + trench_width))
        shape_inv = ShapeArc(center = (0.0, 0.5 * wg_width + self.bend_radius), 
                               radius = self.bend_radius + 0.5 * wg_width + trench_width, 
                               start_angle = -90.0+a1 , 
                               end_angle = 0, 
                               clockwise = False)

        shape_inv += ShapeArc(center = (0.0, 0.5 * wg_width + self.bend_radius), radius = self.bend_radius - 0.5 * wg_width - trench_width, start_angle = 0.0, end_angle = -90.0, clockwise = True)
        shape_inv += (-2.0, trench_width + wg_width)
        shape_inv += (-2.0, 0.5*wg_width)

        shape_inv2 = shape_inv.v_mirror_copy()
        shape_inv2.reverse()
        shape_inv += shape_inv2
        shape_inv.close()
        elems += Boundary(PPLayer(process, TECH.PURPOSE.LF_AREA), shape_inv)
        return elems                                              

    def define_ports(self, prts):
        prts += [InOpticalPort(position=(-2.0, 0.0), wg_definition=self.wg_definition, angle=180.0), 
                 OutOpticalPort(position=(self.bend_radius, self.bend_radius + 0.5 * self.wg_definition.wg_width), wg_definition=self.wg_definition, angle=90.0),
                 OutOpticalPort(position=(self.bend_radius, -self.bend_radius - 0.5 * self.wg_definition.wg_width), wg_definition=self.wg_definition, angle=-90.0)]
        return prts
            

                          
class WgY90Combiner(WgY90Splitter):
    """ Y-combiner structure with input branches perpendicular to output waveguide """

    __name_prefix__ = "Y90_combiner_"
    
    def define_elements(self, elems):
        super(WgY90Combiner, self).define_elements(elems)
        elems.h_mirror()
        return elems

    def define_ports(self, ports):
        super(WgY90Combiner, self).define_ports(ports)
        ports.h_mirror()
        ports.invert()
        return ports
    
class WgY180Splitter(__WgYSplitter__):
    """ Y-splitter structure with branches in the same direction as input waveguide """

    __name_prefix__ = "Y180_splitter_"

    
    @cache()
    def get_90_splitter(self):
        return WgY90Splitter(name = self.name+ "_90",
                             wg_definition = self.wg_definition,
                             bend_radius = self.bend_radius
                             )
                             
    @cache()
    def get_bend_north(self):
        p = self.get_90_splitter().north_ports
        bend = Wg90Bend(name = self.name+"_bend_north",
                          wg_definition=self.wg_definition, 
                          bend_radius=self.bend_radius, 
                          quadrant=-3)
        return SRef(reference = bend,
                    position=p[0].position)
    
    @cache()
    def get_bend_south(self):
        p = self.get_90_splitter().south_ports
        bend = Wg90Bend(name = self.name+"_bend_south",
                          wg_definition=self.wg_definition, 
                          bend_radius=self.bend_radius, 
                          quadrant=3)
        return SRef(reference = bend,
                    position=p[0].position)
    
    def define_elements(self, elems):
        elems += SRef(reference = self.get_90_splitter())
        elems += self.get_bend_south()
        elems += self.get_bend_north()
        return elems

    def define_ports(self, prts):
        prts += self.get_90_splitter().in_ports
        prts += self.get_bend_south().out_ports
        prts += self.get_bend_north().out_ports
        return prts
    
    
class WgY180Combiner(WgY180Splitter):
    """ Y-combiner structure with branches in the same direction as input waveguide """

    __name_prefix__ = "Y180_combiner_"

    
    @cache()
    def get_90_splitter(self):
        return WgY90Combiner(name = self.name+ "_90",
                             wg_definition = self.wg_definition,
                             bend_radius = self.bend_radius
                             )
                             
    @cache()
    def get_bend_north(self):
        p = self.get_90_splitter().north_ports
        bend = Wg90Bend(name = self.name+"_bend_north",
                          wg_definition=self.wg_definition, 
                          bend_radius=self.bend_radius, 
                          quadrant=1)
        return SRef(reference = bend,
                    position=p[0].position)
    
    @cache()
    def get_bend_south(self):
        p = self.get_90_splitter().south_ports
        bend = Wg90Bend(name = self.name+"_bend_south",
                          wg_definition=self.wg_definition, 
                          bend_radius=self.bend_radius, 
                          quadrant=-1)
        return SRef(reference = bend,
                    position=p[0].position)
    
    def define_ports(self, prts):
        prts += self.get_90_splitter().out_ports
        prts += self.get_bend_south().out_ports.invert_copy()
        prts += self.get_bend_north().out_ports.invert_copy()
        return prts
    

