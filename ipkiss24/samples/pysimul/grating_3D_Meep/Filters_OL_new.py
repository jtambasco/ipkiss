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

if __name__ == '__main__':
    from Technology import * #when ran from the test suite, the default technology is used
 

from ipkiss.all import *
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.plugins.photonics.port.port import OpticalPort
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.plugins.photonics.routing import *
from layout import *
from picazzo.wg.tapers.linear import *
from OL_wg_def import *


class GratingCavity(Structure):
    period = PositiveNumberProperty(required = True)
    cavity_length = NumberProperty(required = True)
    number_of_periods_left = NumberProperty(default = 10)
    number_of_periods_right = NumberProperty(default = 10)
    left_wg_length = NumberProperty(default = 1.0)
    right_wg_length = NumberProperty(default = 1.0)
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    add_overlay = BoolProperty(default = True)
    ol_wg1_width = NumberProperty(default = 1.6)
    ol_wg1_ext = NumberProperty(default = 1.0)
    ol_wg1_ext_2 = NumberProperty(default = 2.0)
    ol_wg2_width = NumberProperty(default = 0.5)
    ol_wg2_length = NumberProperty(default = 5.0)
    ol_taper_length = NumberProperty(default = 6.0)
    grating_cavity = StructureProperty(fdef_name = "define_cavity")
    left_grating = DefinitionProperty(fdef_name = "define_left_grating")
    right_grating = DefinitionProperty(fdef_name = "define_right_grating")
    period_component = DefinitionProperty(fdef_name = "define_period_component")
    overlay_wg1 = DefinitionProperty(fdef_name = "define_overlay_wg1")
    overlay_wg2 = DefinitionProperty(fdef_name = "define_overlay_wg2")
    overlay_taper = DefinitionProperty(fdef_name = "define_overlay_taper")

    def define_period_component(self):
        return WgGratingPeriodShallow(length = self.period,
                                      wg_definition = self.wg_definition)
    def define_left_grating(self):
        wg_def1 = self.wg_definition
        
        grating_left = WgGrating(period = self.period_component,
                                 n_o_periods = self.number_of_periods_left)
        a = SRef(grating_left)
        return a

    def define_right_grating(self):
        wg_def1 = self.wg_definition
        grating_right = WgGrating(period =self.period_component,
                                  n_o_periods = self.number_of_periods_right)
        shift = self.left_grating.size_info().get_width()
        c = SRef(grating_right,position = (shift + self.cavity_length,0.))
        return c
    
    def define_cavity(self):
        wg_def1 = self.wg_definition
        a = self.left_grating
        c = self.right_grating
        x1 = self.left_grating.west_ports[0].position[0]
        x2 = self.right_grating.east_ports[0].position[0]
        s = Shape([(x1,0.),(x2,0.)])
        b = wg_def1(shape = s)
        return Structure(elements = [a,b,c])


    def get_active_port(self):
        return self.overlay_wg2.west_ports[0]
    
    def define_ports(self, prts):
        prts = [self.left_grating.west_ports[0],
                self.right_grating.east_ports[0]]
        return prts
    

    def define_overlay_wg1(self):
        x1 = self.left_grating.west_ports[0].position[0]-self.ol_wg1_ext
        x2 = self.right_grating.east_ports[0].position[0]+self.ol_wg1_ext_2
        y = 0.0
        s = Shape([(x1,y),(x2,y)])
        ol_wg_def = OverlayWgDefinition(wg_width = self.ol_wg1_width)
        return ol_wg_def(shape = s)
    
    def define_overlay_wg2(self):
        x1 = self.overlay_taper.west_ports[0].position[0]
        x2 = x1-self.ol_wg2_length
        y = 0.0
        s = Shape([(x1,y),(x2,y)])
        ol_wg_def = OverlayWgDefinition(wg_width = self.ol_wg2_width)
        return ol_wg_def(shape = s)
    
    def define_overlay_taper(self):
        ol_wg_def = OverlayWgDefinition(wg_width = self.ol_wg2_width)
        st_port = self.overlay_wg1.west_ports[0]
        taper = WgElPortTaperLinear(start_port = st_port,
                                    end_wg_def = ol_wg_def,
                                    length = self.ol_taper_length)
        return taper
    
    def define_elements(self, elems):

        #ol_wg_def = OverlayWgDefinition(wg_width = 1.6)
        #ol_wg_def_2 = OverlayWgDefinition(wg_width = 0.45)
        #s = Shape([(0.0,0.0),(self.grating_cavity.size_info().get_width(),0.0)])
        #wg = ol_wg_def(shape = s)
        #st_port = wg.west_ports[0]
        #length = 3.0
        #taper = WgElPortTaperLinear(start_port = st_port,
                                    #end_wg_def = ol_wg_def_2,
                                    #length = length)
        
        
        
        #elems += wg
        #elems += taper
        
        elems += SRef(self.grating_cavity)
        if (self.add_overlay):
            elems += self.overlay_wg1
            elems += self.overlay_taper
            elems += self.overlay_wg2
        return elems
    


class GratingCavityWithRightTaper(GratingCavity):
    end_wg_def = DefinitionProperty(default = TECH.WGDEF.WIRE)
    taper_length = NumberProperty(default = 10.0)
    section_length = NumberProperty(default = 5.0)
    void_length = NumberProperty(default = 10.0)
    
    right_taper = DefinitionProperty(fdef_name = 'define_right_taper')
    right_section = DefinitionProperty(fdef_name = 'define_right_section')
    
    def define_right_taper(self):
        p1 = self.right_grating.east_ports[0]
        length = self.taper_length
        taper = WgElPortTaperLinear(start_port = p1,
                                    end_wg_def = self.end_wg_def,
                                    length = length)
        return taper
    def define_right_section(self):
        p1 = self.right_taper.east_ports[0]
        length = self.section_length
        taper = WgElPortTaperLinear(start_port = p1,
                                    end_wg_def = self.end_wg_def,
                                    length = length)
        return taper
    
    def define_elements(self,elems):
        elems += GratingCavity.define_elements(self,elems)
        elems += self.right_section
        elems += self.right_taper
        port_pos = self.left_grating.west_ports[0].position
        elems += Line(layer = PPLayer(TECH.PROCESS.WG, TECH.PURPOSE.DF.TRENCH),
                      begin_coord = port_pos, 
                      end_coord = (port_pos[0]-self.void_length, port_pos[1]), 
                      line_width = 2.0 * TECH.WG.TRENCH_WIDTH
                      )
        return elems
    
    def define_ports(self,ports):
        ports = [self.left_grating.west_ports[0],self.right_section.east_ports[0]]
        return ports
    
class GratingCavityWithTapers(GratingCavity):
    end_wg_def = DefinitionProperty(default = TECH.WGDEF.WIRE)
    taper_length = NumberProperty(default = 10.0)
    
    left_taper = DefinitionProperty(fdef_name = 'define_left_taper')
    right_taper = DefinitionProperty(fdef_name = 'define_right_taper')
    
    
    def define_left_taper(self):
        st_port = GratingCavity.define_ports(self,0)[0]
        length = self.taper_length
        taper = WgElPortTaperLinear(start_port = st_port,
                                    end_wg_def = self.end_wg_def,
                                    length = length)
        return taper
    def define_right_taper(self):
        st_port = GratingCavity.define_ports(self,0)[1]
        length = self.taper_length
        taper = WgElPortTaperLinear(start_port = st_port,
                                    end_wg_def = self.end_wg_def,
                                    length = length)
        return taper
    def define_elements(self,elems):
        elems += GratingCavity.define_elements(self,elems)
        elems += self.left_taper
        elems += self.right_taper
        return elems
    
    def define_ports(self,ports):
        ports = [self.left_taper.west_ports[0],self.right_taper.east_ports[0]]
        return ports
    
class GratingCavityWithModeFilter(GratingCavityWithTapers):
    section_length = NumberProperty(default = 10.0)
    taper2_length = NumberProperty(default = 30.0)
    end_wg_def2 = DefinitionProperty(required = True)
    
    left_mode_filter = DefinitionProperty(fdef_name = 'define_left_mode_filter')
    right_mode_filter = DefinitionProperty(fdef_name  = 'define_right_mode_filter')
    
    def define_right_mode_filter(self):
        st_port = GratingCavityWithTapers.define_ports(self,0)[1]
        wg_def = st_port.wg_definition
        s = Shape([st_port.position,(st_port.position[0]+self.section_length,
                                     st_port.position[1])])
        
        wg = wg_def(shape = s)
        
        st_port = wg.east_ports[0]
        taper = WgElPortTaperLinear(start_port = st_port,
                                    end_wg_def = self.end_wg_def2,
                                    length = self.taper2_length)
        
        return [wg,taper]
    
    def define_left_mode_filter(self):
        st_port = GratingCavityWithTapers.define_ports(self,0)[0]
        wg_def = st_port.wg_definition
        s = Shape([st_port.position,(st_port.position[0]-self.section_length,
                                     st_port.position[1])])
        
        wg = wg_def(shape = s)
        
        st_port = wg.west_ports[0]
        taper = WgElPortTaperLinear(start_port = st_port,
                                    end_wg_def = self.end_wg_def2,
                                    length = self.taper2_length)
        
        return [wg,taper]
    
    def define_elements(self,elems):
        elems += GratingCavityWithTapers.define_elements(self,elems)
        lmf = self.left_mode_filter
        rmf = self.right_mode_filter
        elems += lmf[0]
        elems += lmf[1]
        elems += rmf[0]
        elems += rmf[1]
        return elems
    
    def define_ports(self,ports):
        ports = [self.left_mode_filter[1].west_ports[0],self.right_mode_filter[1].east_ports[0]]
        return ports
class GratingCavityWithAccessWaveguides(GratingCavity):
    offset = NumberProperty(default = 1.0)
    bend_1 = DefinitionProperty(fdef_name = "define_bend_1")
    bend_2 = DefinitionProperty(fdef_name = "define_bend_2")
    def define_bend_1(self):      
        route = RouteToWestAtY(GratingCavity.define_ports(self,0)[0],y_position= -self.offset,min_straight=0.1)
        connecting_wg_el_left = RouteConnectorRounded(route)
        return connecting_wg_el_left
    def define_bend_2(self):
        route = RouteToEastAtY(GratingCavity.define_ports(self,0)[1],y_position= -self.offset,min_straight=0.1)
        connecting_wg_el_right = RouteConnectorRounded(route)
        return connecting_wg_el_right
    def define_elements(self,elems):
        elems += GratingCavity.define_elements(self,elems)
        elems += self.bend_1
        elems += self.bend_2
        return elems
    def define_ports(self,ports):
        ports = [self.bend_1.west_ports[0],self.bend_2.east_ports[0]]
        return ports
    
class GratingCavityFilter(GratingCavity):
    gap_space = PositiveNumberProperty(required = True)
    wg_definition_access = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    def define_elements(self, elems):
        
        length = self.get_length()
        height = self.wg_definition.wg_width / 2.0 + self.gap_space + self.wg_definition_access.wg_width / 2.
        s = Shape([(0,height),(length,height)])
        wg = self.wg_definition_access(shape = s)
        elems += GratingCavity.define_elements(self,elems)
        elems += wg
        return elems

    def define_ports(self, ports):
        height = self.wg_definition.wg_width / 2.0 + self.gap_space + self.wg_definition_access.wg_width / 2.
        pts = GratingCavity.define_ports(self,0)
        x1 = pts[0].position[0]
        x2 = pts[1].position[0]
        ports = [pts[0],pts[1],OpticalPort(position = (x1, height), angle = -180.0, wg_definition = self.wg_definition_access),
                 OpticalPort(position = (x2,height),
                             angle = 0.0, wg_definition = self.wg_definition_access)]
    
        return ports
    
    
class GratingCavityFilterWithAccessWaveguides(GratingCavityFilter):    
        
    offset = NumberProperty(default = 0.5)
    
    bend_up_l = DefinitionProperty(fdef_name = "define_bend_up_l")
    bend_up_r = DefinitionProperty(fdef_name = "define_bend_up_r")
    bend_down_l = DefinitionProperty(fdef_name = "define_bend_down_l")
    bend_down_r = DefinitionProperty(fdef_name = "define_bend_down_r")
    

    def define_bend_up_l(self):
        pts = GratingCavityFilter.define_ports(self,0)
        route = RouteToWestAtY(pts[2], y_position=pts[2].position[1]+self.offset, min_straight=0.1)
        connecting_wg_el = RouteConnectorRounded(route)
        return connecting_wg_el
    def define_bend_up_r(self):
        pts = GratingCavityFilter.define_ports(self,0)
        route = RouteToEastAtY(pts[3],y_position= pts[3].position[1]+self.offset, min_straight=0.1)
        connecting_wg_el = RouteConnectorRounded(route)
        return connecting_wg_el
    def define_bend_down_l(self):
        pts = GratingCavityFilter.define_ports(self,0)
        route = RouteToWestAtY(pts[0], y_position=pts[0].position[1]-self.offset, min_straight=0.1)
        connecting_wg_el = RouteConnectorRounded(route)
        return connecting_wg_el
    def define_bend_down_r(self):
        pts = GratingCavityFilter.define_ports(self,0)
        route = RouteToEastAtY(pts[1],y_position= pts[1].position[1]-self.offset, min_straight=0.1)
        connecting_wg_el = RouteConnectorRounded(route)
        return connecting_wg_el
    
    def define_elements(self,elems):
        elems = GratingCavityFilter.define_elements(self,elems)
        elems += self.bend_down_l
        elems += self.bend_down_r
        elems += self.bend_up_l
        elems += self.bend_up_r
        return elems
    
    def define_ports(self,ports):
        p1 = self.bend_down_l.west_ports[0]
        p2 = self.bend_up_l.west_ports[0]
        p3 = self.bend_down_r.east_ports[0]
        p4 = self.bend_up_r.east_ports[0]
        ports = [p1,p2,p3,p4]
        return ports
    
 
if __name__ == '__main__':
    
    grating_unit_cell = WgGratingPeriodShallow(length = 0.29,
                                               wg_definition = WgElDefinition(wg_width = 0.45),
                                               shallow_process = TECH.PROCESS.FC)    
    cavity1 = GratingCavity(wg_definition = WgElDefinition(wg_width = 0.45),
                            period = 0.29,
                            cavity_length = 0.0,
                            number_of_periods_left = 10,
                            number_of_periods_right = 10,
                            period_component = grating_unit_cell)
    from picazzo.aspects.visualization import *
    cavity1.visualize_2d()
