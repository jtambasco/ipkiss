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
from ipkiss.plugins.photonics import *
from .basic import Wg2ElDefinition
from .definition import BaseWaveguideDefinition, WaveguideDefProperty, SingleShapeWaveguideElement
from math import acos, tan, pi
from ipkiss.process.layer import ProcessProperty, PPLayer
from ipkiss.plugins.photonics.port.port import OpticalPortProperty, OpticalPort, InOpticalPort, OutOpticalPort
from numpy import sign, roll
import math
import sys

__all__ = ["WaveguidePointRoundedConnectElementDefinition",
           "WaveguidePointRoundedExpandedConnectElementDefinition"        
           ]

class __RoundedShape__(StrongPropertyInitializer):
    """Rounded Waveguide base class"""
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    rounding_algorithm = RestrictedProperty(default = ShapeRound)

    @cache()
    def get_bend90_size(self):
        s = Shape([(-100*self.bend_radius,0), (0,0), (0.0, 100*self.bend_radius)])
        RA = self.rounding_algorithm
        s = RA(original_shape = s, radius = self.bend_radius)
        if len(s)>1:
            return abs(s[1].x), abs(s[-2].y)
        else:
            return 0,0
    
    def get_bend_size(self, angle):
        if angle == 0.0: return 0,0
        s = Shape([(-100*self.bend_radius,0), (0,0), (100*self.bend_radius*math.cos(angle * DEG2RAD), 100*self.bend_radius*math.sin(angle * DEG2RAD))])
        RA = self.rounding_algorithm

        s = RA(original_shape = s, radius = self.bend_radius)
        if len(s)>1:
            return distance(s[1]), distance(s[-2]) #L1,L2
        else:
            return 0,0

class __RoundedWaveguide__(__RoundedShape__):
    manhattan = BoolProperty(default = False)
    
class __RoundedWaveguideManhattan__(__RoundedWaveguide__):
    manhattan = BoolProperty(default = True)

        
class __WaveguideConnectElement__(Group):
    input = OpticalPortProperty(required = True)
    output = OpticalPortProperty(required = True)
    
    def define_ports(self, ports):
        ports += [InOpticalPort(position = self.input.position, angle = (self.input.angle + 180)%360.0, wg_definition = self.input.wg_definition), 
                      OutOpticalPort(position = self.output.position, angle = (self.output.angle + 180)%360.0, wg_definition = self.output.wg_definition),]
        return ports


class __WaveguidePointConnectElementDefinition__(BaseWaveguideDefinition):
    """connector based on waypoints and another waveguide definition"""
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.DEFAULT)
    process = ReadOnlyIndirectProperty("wg_definition")
    wg_width = ReadOnlyIndirectProperty("wg_definition")
    trench_width = ReadOnlyIndirectProperty("wg_definition")
    remove_straight_angles = BoolProperty(default = True)
           
    class __WaveguidePointConnectElementDefinitionPathDefinition__(__WaveguideConnectElement__, SingleShapeWaveguideElement):
        shape = ShapeProperty(required = True)
        input = DefinitionProperty(fdef_name = "define_input")
        output = DefinitionProperty(fdef_name = "define_output")
        remove_straight_angles = ReadOnlyIndirectProperty("wg_definition")
    
        def define_input(self):
            c = Shape(self.shape)
            a1 = angle_deg(c[1], c[0])
            a2 = angle_deg(c[-2], c[-1])
            i = OpticalPort(position = c[0], angle =a1, wg_definition = self.wg_definition)
            return i
    
        def define_output(self):
            c = self.get_control_shape()
            a1 = angle_deg(c[1], c[0])
            a2 = angle_deg(c[-2], c[-1])  
            o = OpticalPort(position = c[-1], angle = a2, wg_definition = self.wg_definition)
            return o    
           
        @cache()
        def length(self):
            return self.center_line().length()
        
        @cache()
        def center_line(self):
            # build centerline out of 3-point bends
            CS = self.get_control_shape()
            S = Shape()
            for i in range(len(CS)):
                S += self.get_single_bend(i)
            S.end_face_angle = angle_deg(CS[-1], CS[-2])
            S.start_face_angle = angle_deg(CS[1], CS[0])
    
            return S
    
        @cache()
        def get_control_shape(self):
            S = Shape(self.shape)
            if self.remove_straight_angles:
                S.remove_straight_angles()
            return S
    
        @cache()
        def get_single_bend(self, index):
            return Shape(self.get_control_shape()[index])
    
        @cache()
        def trench_center_line(self):
            return self.center_line()
    
    def get_wg_definition_cross_section(self):
        return self.wg_definition.get_wg_definition_cross_section()        
    
__WaveguidePointConnectElementDefinitionPathDefinition__ = __WaveguidePointConnectElementDefinition__.__WaveguidePointConnectElementDefinitionPathDefinition__    
    
        
class WaveguidePointRoundedConnectElementDefinition(__RoundedWaveguide__, __WaveguidePointConnectElementDefinition__):
    """connector based on waypoints and another waveguide definition with rounded corners"""
    
    reverse_bends = BoolProperty(default = False)

    class __WaveguidePointRoundedConnectElementDefinitionPathDefinition__(__RoundedWaveguide__, __WaveguidePointConnectElementDefinition__.__WaveguidePointConnectElementDefinitionPathDefinition__):
        bend_radius = ReadOnlyIndirectProperty("wg_definition")
        manhattan = ReadOnlyIndirectProperty("wg_definition")
        rounding_algorithm = ReadOnlyIndirectProperty("wg_definition")
        reverse_bends = ReadOnlyIndirectProperty("wg_definition")
        process = ReadOnlyIndirectProperty("wg_definition")    
    
        def define_elements(self, elems):
            
            s = self.center_line()
            s.remove_identicals()
            if issubclass(self.wg_definition.wg_definition.path_definition_class, Wg2ElDefinition.__Wg2ElDefinitionPathDefinition__): 
                s2 = self.trench_center_line()
                elems += self.wg_definition.wg_definition(shape = s, trench_shape = s2)
            else:
                elems += self.wg_definition.wg_definition(shape = s)
    
            if self.manhattan:
                if hasattr(self.wg_definition.wg_definition, "trench_width") and not (self.wg_definition.trench_width is None):
                    S = Shape(self.shape).remove_straight_angles()
                    L = len(S)
                    if self.shape.closed:
                        start, stop  = 0, L
                    else:
                        start, stop  = 1, L-1
                    L2 = 0.5*self.wg_definition.wg_width + self.wg_definition.trench_width
                    TW = self.wg_definition.trench_width + 0.5* self.wg_definition.wg_width
                    for i in range(start, stop):
                        SI1 = self.get_single_bend(i).size_info
                        SI2 = ShapeOffset(original_shape = [S[i-1], S[i], S[(i+1)%L]], 
                                          offset = L2)[1:-1].size_info
                        SI3 = ShapeOffset([S[i-1], S[i], S[(i+1)%L]],
                                          offset = -L2)[1:-1].size_info
                        SI = SI1 + SI2 + SI3
                        if SI.width > TW or SI.height > TW:
                            elems += Rectangle(layer = PPLayer(self.process, TECH.PURPOSE.LF_AREA), 
                                          center = SI.center, 
                                          box_size = SI.size)

                    
            return elems
      
                        
        def get_single_bend(self, i):
            S = self.get_control_shape()
            L = len(S)
            RA = self.rounding_algorithm
            if self.shape.closed or ((i!=0) and (i%L != L-1)):
                if self.reverse_bends:
                    p_start = S[(i+1)%L]
                    p_end = S[(i-1)%L]
                else:
                    p_start = S[(i-1)%L]
                    p_end = S[(i+1)%L]
                p_turn = S[i%L]
                bend = RA(original_shape = Shape([p_start, p_turn, p_end]), 
                          radius = self.bend_radius,
                          angle_step = TECH.WG.ANGLE_STEP,
                          )
                if self.reverse_bends: bend.reverse()
                return bend[1:-1]
            else:
                return Shape([S[i]])
                            
        def center_line(self):
            S = self.get_control_shape()
            RA = self.rounding_algorithm
            cl =  RA(original_shape = S, 
                      radius = self.bend_radius, 
                      angle_step = TECH.WG.ANGLE_STEP)
            cl.end_face_angle = angle_deg(S[-1], S[-2])
            cl.start_face_angle = angle_deg(S[1], S[0])
            return cl
            #return ShapeRound(original_shape = self.shape, radius = self.bend_radius, angle_step = TECH.WG.ANGLE_STEP)
    
        def trench_center_line(self):
            r = self.wg_definition.bend_radius
            S = self.get_control_shape()
            if self.manhattan:
                a_step_t = 180.0
                cl = Shape(S)
            else:
                RA = self.rounding_algorithm
                w = self.wg_definition.wg_width
                t = self.wg_definition.trench_width
                a_step_t = 2 * RAD2DEG*acos((r + 0.5*w+ 0.8* t) / (r + 0.5*w + t))
                
                
                if self.reverse_bends: 
                    S = Shape(S)
                    S.reverse()
                rs =  RA(original_shape = S, 
                         radius = r, 
                         angle_step = a_step_t)
                if self.reverse_bends: rs.reverse()
                cl = rs

            cl.end_face_angle = angle_deg(S[-1], S[-2])
            cl.start_face_angle = angle_deg(S[1], S[0])
            return cl

    def __str__(self):
        return "WGPRCEDEF:br=%f-mh=%s-wd=%s"%(self.bend_radius, str(self.manhattan), str(self.wg_definition))
    
    def define_name(self):
        return "WGPRCEDEF_R%d_M%s_W%s"%(self.bend_radius*1000,str(self.manhattan),self.wg_definition.name)
    
__WaveguidePointRoundedConnectElementDefinitionPathDefinition__ = WaveguidePointRoundedConnectElementDefinition.__WaveguidePointRoundedConnectElementDefinitionPathDefinition__

#######################################################################################
# expanded generic classes
#######################################################################################

class __WaveguideExpandedConnectGenericDefinition__(object):
    taper_length = PositiveNumberProperty(default = TECH.WG.EXPANDED_TAPER_LENGTH)
    min_wire_length = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    remove_straight_angles = BoolProperty(default = False)
    

class __WaveguideExpandedConnectGeneric__(WaveguidePointRoundedConnectElementDefinition.__WaveguidePointConnectElementDefinitionPathDefinition__):
    min_expanded_length = ReadOnlyIndirectProperty("wg_definition")
    taper_length = ReadOnlyIndirectProperty("wg_definition")
    min_wire_length = ReadOnlyIndirectProperty("wg_definition")
 
    expanded_widths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), required = True)
    expanded_lengths = RestrictedProperty(restriction = RestrictList(RESTRICT_NONNEGATIVE), required = True)
    expanded_positions = RestrictedProperty(restriction = RestrictList(RESTRICT_FRACTION), required = True)

        
    def expanded_length(self):
        return sum(self.expanded_lengths)
    
    def define_elements(self, elems):
        super(__WaveguideExpandedConnectGeneric__, self).define_elements(elems)
        thresh = 0.5/get_grids_per_unit()
        c = self.get_control_shape()
        
        L = len(c)
        if self.shape.closed:
            end = L
        else:
            end = L-1
        if L > 1:
            this_bend = self.get_single_bend(0)

        
            
        for k in range(end):
            next_bend = self.get_single_bend((k+1)%L)
            L_exp = self.expanded_lengths[k]
    
            p0 = this_bend[-1]
            p1 = next_bend[0]
            L_available = distance(p0, p1) - self.min_wire_length - 2 * self.taper_length
            if L_exp == None:
                L_exp = L_available
            if L_exp <= 0.0:
                this_bend = next_bend
                continue
            
            
            if L_available - L_exp < -thresh:
                raise ValueError("Available length %f is too small for specified expansion length %f in section %d of wg_el_connect_points_rounded_expanded_generic" % (L_available, L_exp, k))
            else:
                L1 = self.expanded_positions[k]*(L_available-L_exp) + 0.5*self.min_wire_length
                L2 = (1.0-self.expanded_positions[k])*(L_available - L_exp) + 0.5*self.min_wire_length
                ang = angle_deg(p1, p0)
                if self.expanded_widths[k] > self.wg_definition.wg_width:
                    t1 = ShapeRadialWedge(center = p0, 
                                          inner_radius = L1, 
                                          outer_radius = L1 + self.taper_length, 
                                          inner_width = self.wg_definition.wg_width-0.01, 
                                          outer_width = self.expanded_widths[k], 
                                          angle = ang)
                    t2 = ShapeRadialWedge(center = p1, 
                                          inner_radius = L2,  
                                          outer_radius = L2 + self.taper_length, 
                                          inner_width = self.wg_definition.wg_width-0.01, 
                                          outer_width = self.expanded_widths[k], 
                                          angle = ang+180.0)
                    t = Shape([t1[0], t1[1], t1[2], t2[3], t2[0], t2[1], t2[2], t1[3], t1[0]])
                    elems += Boundary(PPLayer(self.process, TECH.PURPOSE.LF.LINE), t)
                if self.expanded_widths[k] < self.wg_definition.wg_width:
                    raise AttributeError("Expanded Waveguide cannot be narrower than Waveguide width")
    
            this_bend = next_bend
        return elems
        
          

class WaveguidePointRoundedExpandedGenericConnectElementDefinition(__WaveguideExpandedConnectGenericDefinition__, WaveguidePointRoundedConnectElementDefinition):

    class __WaveguidePointRoundedExpandedGenericConnectElementDefinitionPathDefinition__(__WaveguideExpandedConnectGeneric__,  WaveguidePointRoundedConnectElementDefinition.__WaveguidePointRoundedConnectElementDefinitionPathDefinition__):
        pass
     
__WaveguidePointRoundedExpandedGenericConnectElementDefinitionPathDefinition__ = WaveguidePointRoundedExpandedGenericConnectElementDefinition.__WaveguidePointRoundedExpandedGenericConnectElementDefinitionPathDefinition__

class __WaveguideExpandedConnectDefinition__(__WaveguideExpandedConnectGenericDefinition__):
    expanded_width = PositiveNumberProperty(default = TECH.WG.EXPANDED_WIDTH)
    min_expanded_length = PositiveNumberProperty(default = TECH.WG.EXPANDED_STRAIGHT)
    remove_straight_angles = BoolProperty(default = True)
    
class __WaveguideExpandedConnect__(__WaveguideExpandedConnectGeneric__):
    expanded_width = ReadOnlyIndirectProperty("wg_definition")
    min_expanded_length = ReadOnlyIndirectProperty("wg_definition")
 
    expanded_widths = DefinitionProperty(fdef_name = "define_expanded_widths")
    expanded_lengths = DefinitionProperty(fdef_name = "define_expanded_lengths")
    expanded_positions = DefinitionProperty(fdef_name = "define_expanded_positions")

    def define_expanded_lengths(self):
        (l,w,p) = self.__get_expanded_lengths_widths_positions__()
        return l
    
    def define_expanded_widths(self):
        (l,w,p) = self.__get_expanded_lengths_widths_positions__()
        return w
               
    def define_expanded_positions(self):
        (l,w,p) = self.__get_expanded_lengths_widths_positions__()
        return p
    
    @cache()
    def __get_expanded_lengths_widths_positions__(self):
        c = self.get_control_shape()
        L = len(c)

        el = [None for i in range(L)]
        ew = [self.expanded_width for i in range(L)]
        ep = [0.5 for i in range(L)]        
        
        return (el, ew, ep)   


                
class WaveguidePointRoundedExpandedConnectElementDefinition(__WaveguideExpandedConnectDefinition__, WaveguidePointRoundedConnectElementDefinition):

    class __WaveguidePointRoundedExpandedConnectElementDefinitionPathDefinition__(__WaveguideExpandedConnect__, WaveguidePointRoundedConnectElementDefinition.__WaveguidePointRoundedConnectElementDefinitionPathDefinition__):
        pass 
    
            
__WaveguidePointRoundedExpandedConnectElementDefinitionPathDefinition__ = WaveguidePointRoundedExpandedConnectElementDefinition.__WaveguidePointRoundedExpandedConnectElementDefinitionPathDefinition__

