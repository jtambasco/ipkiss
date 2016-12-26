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



from picazzo.wg.splitters import WgY90Splitter, WgY90Combiner
from ipkiss.plugins.photonics.routing.to_line import RouteToWestAtY, RouteToEastAtY, RouteToEast
from ipkiss.plugins.photonics.routing.manhattan import RouteManhattan
from ipkiss.plugins.photonics.routing.connect import RouteConnector
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.plugins.photonics.wg.connect import WaveguidePointRoundedConnectElementDefinition, WaveguidePointRoundedExpandedConnectElementDefinition
from ipkiss.plugins.photonics.port import OpticalPort, InOpticalPort, OutOpticalPort
from picazzo.wg.tapers.linear import WgElPortTaperLinear
from ipkiss.plugins.photonics.wg.connect import __RoundedWaveguide__, __RoundedWaveguideManhattan__
from picazzo.wg.spiral import WgSpiralFixedLength
from ipkiss.all import *

__all__ = ["WgMzi",
           "WgMziY90",
           "WgMzi1x1Y90",
           "WgMzi1x1Y90Asymmetric",
           "WgMzi1x1Y90Symmetric",
           "WgMziAsymmetric", 
           "WgMziSymmetric",
           "WgMziGeneric"]
           
# generic mzi that takes a splitter object and a combiner object
class WgMzi(Structure):
    splitter = StructureProperty(required = True)
    combiner = StructureProperty(required = True)
    splitter_transform = TransformationProperty()
    combiner_transform = TransformationProperty()
    
    splitter_ref = DefinitionProperty()
    combiner_ref = DefinitionProperty()
    
    def define_splitter_ref(self):
        return SRef(reference = self.splitter, position = (0.0, 0.0), transformation = self.splitter_transform)
    def define_combiner_ref(self):
        return SRef(reference = self.combiner, position = (0.0, 0.0), transformation = self.combiner_transform)
    def define_elements(self, elems):
        elems += self.splitter_ref
        elems += self.combiner_ref
        return elems

    def define_ports(self, ports):
        return self.splitter_ref.in_ports + self.combiner_ref.out_ports
    

class WgMziY90(__RoundedWaveguide__, WgMzi):
    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    straight1 = PositiveNumberProperty(default = 9.2)
    straight2 = PositiveNumberProperty(default = 34.2)
    
    splitter = DefinitionProperty()
    combiner = DefinitionProperty()
    splitter_transform = DefinitionProperty()
    combiner_transform = DefinitionProperty()

    def define_splitter(self):
        return WgY90Splitter(bend_radius = self.bend_radius, wg_definition = self.wg_definition)
    
    def define_combiner(self):
        return WgY90Combiner(bend_radius = self.bend_radius,wg_definition = self.wg_definition)
    
    def define_splitter_transform(self):
        return IdentityTransform()
    
    def define_combiner_transform(self):
        return Translation(translation = (4 * self.bend_radius, 0.0))

    def define_elements(self, elems):
        elems = WgMzi.define_elements(self,elems)
        R = RouteManhattan(input_port = self.splitter_ref.north_ports[0],
                           output_port = self.combiner_ref.north_ports[0],
                           bend_radius = self.bend_radius,
                           rounding_algorithm = self.rounding_algorithm,
                           min_straight = 0.0,
                           start_straight = self.straight1,
                           end_straight = self.straight1)
        elems += RouteConnector(route = R,manhattan = self.manhattan)        
        R = RouteManhattan(input_port = self.splitter_ref.south_ports[0], 
                           output_port = self.combiner_ref.south_ports[0],
                           bend_radius = self.bend_radius,
                           rounding_algorithm = self.rounding_algorithm,
                           min_straight = 0.0,
                           start_straight = self.straight2,
                           end_straight = self.straight2)
        elems += RouteConnector(route = R,manhattan = self.manhattan)
        return elems
        

#####################
## New MZI classes
#####################
class __MziDelaySimple__(__RoundedWaveguide__, Structure):
    """ a simple 4-bend delay line """
    __name_prefix__ = "MZIS_D"

    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    straight = PositiveNumberProperty(required = True)
    extension = PositiveNumberProperty(default = TECH.WG.OVERLAP_EXTENSION)
    connectors = DefinitionProperty()    
    
    def define_elements(self, elems):
        for c in self.connectors:
            elems += c
        return elems
        
    def define_connectors(self):
        bs1, bs2 = self.get_bend90_size()
        s = Shape()
        s += (-self.extension,0.0)
        s += (0.0,0.0)
        s += (bs1,0.0)
        s += (bs1,bs1+bs2+self.straight)
        s += (2*bs1+bs2,bs1+bs2+self.straight)
        s += (2*bs1+bs2,0.0)
        s += (2*bs1+2*bs2,0.0)
        s += (2*bs1+2*bs2+self.extension,0.0)

        wgdef = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition,
                                                              bend_radius = self.bend_radius,
                                                              rounding_algorithm = self.rounding_algorithm,
                                                              manhattan = self.manhattan)
        return [wgdef(shape = s)]
        
    def define_ports(self, ports):
        ports += self.connectors[0].in_ports.move_copy((0.0,0.0)) + self.connectors[-1].out_ports.move_copy((0.0,0.0))
        return ports

class __MziDelaySpiral__(__RoundedWaveguide__, Structure):
    """ a spiral delay line """
    __name_prefix__ = "MZISP_D"

    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    total_length = PositiveNumberProperty(required = True)
    no_loops = IntProperty(required=True)
    spacing = PositiveNumberProperty(default=TECH.WG.SPACING)
    
    connectors = DefinitionProperty()
    
    def define_connectors(self):
        wg_def = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition,
                                                               bend_radius = self.bend_radius,
                                                               rounding_algorithm = self.rounding_algorithm,
                                                               manhattan = self.manhattan
                                                               )
        connectors = [WgSpiralFixedLength(wg_definition = wg_def,
                                          total_length = self.total_length, 
                                          n_o_loops = self.no_loops, 
                                          spacing = self.spacing)]
        return connectors
        
    def define_elements(self, elems):
        for c in self.connectors:
            elems += SRef(c,(0.0,0.0))
        return elems
        
    def define_ports(self, ports):
        ports = self.connectors[0].in_ports.move_copy((0.0,0.0)) + self.connectors[-1].out_ports.move_copy((0.0,0.0))
        return ports
        

class __MziDelaySimpleFlipped__(__MziDelaySimple__):
    __name_prefix__ = "MZIS_DF"
    
    def define_connectors(self):
        c = __MziDelaySimple__.define_connectors(self)
        return [ci.v_mirror() for ci in c]


    
class __MziDelaySpiralFlipped__(__MziDelaySpiral__):
    __name_prefix__ = "MZISP_DF"
    
    def define_connectors(self):
        wg_def = WaveguidePointRoundedConnectElementDefinition(wg_definition = self.wg_definition,
                                                               bend_radius = self.bend_radius,
                                                               rounding_algorithm = self.rounding_algorithm,
                                                               manhattan = self.manhattan
                                                               )
        spiral = WgSpiralFixedLength(wg_definition = wg_def, 
                                     total_length = self.total_length, 
                                     n_o_loops = self.no_loops, 
                                     spacing = self.spacing)
        spiral_ref = SRef(reference = spiral, transformation = VMirror())
        struct = Structure(name = spiral.name + "_flipped", elements = [spiral_ref],
                           ports = spiral_ref.ports)
        connectors = [struct]
        return connectors
    
        
class __MziDelayExpanded__(__MziDelaySimple__):
    """ a simple 4-bend delay line """
    __name_prefix__ = "MZIE_D"
    expanded_wg_width = PositiveNumberProperty(default = TECH.WG.EXPANDED_WIDTH)
    min_expanded_length = PositiveNumberProperty(default = TECH.WG.EXPANDED_STRAIGHT)
    expanded_taper_length = PositiveNumberProperty(default = TECH.WG.EXPANDED_TAPER_LENGTH)
    delay = NumberProperty(required = True)
    straight = DefinitionProperty(fdef_name="define_straight")
    
    def define_connectors(self):
        bs1, bs2 = self.get_bend90_size()
        S = self.min_straight +  self.min_expanded_length + 2* self.expanded_taper_length
        s = self.min_straight
        D = self.delay/2.0
        shape = Shape([(0.0, 0.0), (s + bs1, 0.0), (s + bs1, S+bs1+bs2+D), (2*s+2*bs1+bs2, S+bs1+bs2+D), (2*s+2*bs1+bs2, 0.0), (3*s+2*bs1+2*bs2, 0.0)]) 
        wgdef = WaveguidePointRoundedExpandedConnectElementDefinition(wg_definition = self.wg_definition,
                                                                      bend_radius = self.bend_radius,
                                                                      rounding_algorithm = self.rounding_algorithm,
                                                                      expanded_width = self.expanded_wg_width,
                                                                      expanded_taper_length = self.expanded_taper_length,
                                                                      min_straight = self.min_straight,
                                                                      min_expanded_length = self.min_expanded_length,
                                                                      manhattan = True)
        connectors = [wgdef(shape = shape)]
        return connectors 
        
        
class __MziDelayExpandedFlipped__(__MziDelayExpanded__):
    __name_prefix__ = "MZIE_DF"
    
    def define_connectors(self):
        c = __MziDelayExpanded__.define_connectors(self)
        for c in self.connectors: 
            c.v_mirror()
        return c

class __MziDelayFlatExpanded__(__MziDelayExpanded__):
    __name_prefix__ = "MZIE_DFL"
    
    min_wire_length = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    
    def define_connectors(self):
        from numpy import sign
        bs1, bs2 = self.get_bend90_size()
        S = self.min_wire_length +  self.min_expanded_length + 2* self.expanded_taper_length
        s = self.min_wire_length
        sD = sign(self.delay)
        D = abs(self.delay/2.0)

        if sD <= 0:
            shape = Shape([(0.0, 0.0), (s + bs1, 0.0), (s + bs1, 4*bs2+2*s), 
                           (3*s+5*bs1+S+D, 4*bs2+2*s), (3*s+5*bs1+S+D, 2*bs2+s), (2*s+2*bs1, 2*bs2+s), (2*s+2*bs1, 0.0), (3*s + 3*bs1, 0.0)])
        else:
            shape = Shape([(0.0, 0.0), (s + bs1, 0.0), (s + bs1, 2*bs2+s), 
                           (s - S - D-bs1, 2*bs2+s), (s-S-D-bs1, 4*bs2+2*s), (2*s+2*bs1, 4*bs2+2*s), (2*s+2*bs1, 0.0), (3*s + 3*bs1, 0.0)])
        
        wgdef = WaveguidePointRoundedExpandedConnectElementDefinition(wg_definition = self.wg_definition,
                                                                      bend_radius = self.bend_radius,
                                                                      rounding_algorithm = self.rounding_algorithm,
                                                                      expanded_width = self.expanded_wg_width,
                                                                      taper_length = self.expanded_taper_length,
                                                                      min_wire_length = self.min_wire_length,
                                                                      min_expanded_length = self.min_expanded_length,
                                                                      manhattan = True)
        connectors = [wgdef(shape = shape)]
        return connectors
                
class __MziDelayFlatExpandedFlipped__(__MziDelayFlatExpanded__):
    __name_prefix__ = "MZIE_DFLF"
    
    def define_connectors(self):
        c = __MziDelayFlatExpanded__.define_connectors(self)
        for c in self.connectors: 
            c.v_mirror()
        return c

      
class __MziBase__(Structure):
    """ Generic MZI that consists of an input coupler, output coupler and arm elements """
    in_coupler_transform = TransformationProperty()
    out_coupler_transform = TransformationProperty()
    arm1 = StructureProperty(allow_none = True)
    arm2 = StructureProperty(allow_none = True)
    separation = NonNegativeNumberProperty(default = 0.0, allow_none = True)
    in_coupler = DefinitionProperty(default = None)
    out_coupler = DefinitionProperty(default = None)
    in_coupler_transform = DefinitionProperty()
    out_coupler_transform = DefinitionProperty()
    
    in_coupler_ref = DefinitionProperty()
    out_coupler_ref = DefinitionProperty()
    
    def define_in_coupler_transform(self):                
        return IdentityTransform()
    
    def define_out_coupler_transform(self):
        return IdentityTransform()
    
    def define_in_coupler_ref(self):
        return SRef(self.in_coupler, (0.0, 0.0), self.in_coupler_transform)
    
    def define_out_coupler_ref(self):
        return SRef(self.out_coupler, (0.0, 0.0), self.out_coupler_transform)
    
    def define_elements(self, elems):
        elems += self.in_coupler_ref
        elems += self.out_coupler_ref
        return elems
    
    def define_ports(self, ports):
        ports += self.in_coupler_ref.in_ports + self.out_coupler_ref.out_ports
        return ports

class __WgMzi__(__RoundedWaveguideManhattan__, __MziBase__,Structure):
    """ Generic MZI that connects its couplers and arm elements with simple waveguides"""
    __name_prefix__ = "MZIWG"

    wg_definition = WaveguideDefProperty(default = TECH.WGDEF.WIRE)
    
    CPin = DefinitionProperty()
    CPout = DefinitionProperty()    
    A1C = DefinitionProperty(fdef_name="define_a1c")    
    A2C = DefinitionProperty(fdef_name="define_a2c")    
    in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos = DefinitionProperty()
    in_coupler_pos = DefinitionProperty()
    out_coupler_pos = DefinitionProperty()
    R1 = DefinitionProperty()
    R2 = DefinitionProperty()
    R3 = DefinitionProperty()
    R4 = DefinitionProperty()
    arm1_pos = DefinitionProperty()
    arm2_pos =  DefinitionProperty()  
    
    automatic_taper_west_length = FloatProperty(allow_none = True)
    automatic_taper_east_length = FloatProperty(allow_none = True)
                                                              
    def define_CPin(self):
        return self.in_coupler_ref.out_ports.y_sorted()
    
    def define_CPout(self):
        return self.out_coupler_ref.in_ports.y_sorted()

    def __get_arm_content__(self, A):        
        # if no content in arm, create dummy
        if A is None:
            A = Structure(name = "%s_BLANK"%(self.name),
                           elements = [],
                           ports = [OpticalPort(position = (0.0,0.0),wg_definition = self.wg_definition, angle_deg = 180.0),
                                    OpticalPort(position = (0.0,0.0),wg_definition = self.wg_definition, angle_deg = 0.0)])
            
        # if widths not identical,add tapers
        if A.west_ports[0].wg_definition.wg_width == self.CPin[1].wg_definition.wg_width and A.east_ports[0].wg_definition.wg_width == self.CPout[1].wg_definition.wg_width:
            AC = A
        else:
            from picazzo.wg.taper_extended import WgElPortTaperExtended
            if self.automatic_taper_west_length is None:
                T1 = WgElPortTaperExtended(start_port = A.west_ports[0], end_wg_def = self.CPin[1].wg_definition)  
            else:
                T1 = WgElPortTaperExtended(start_port = A.west_ports[0], end_wg_def = self.CPin[1].wg_definition, length = self.automatic_taper_west_length)  
                
            if self.automatic_taper_east_length is None:
                T2 = WgElPortTaperExtended(start_port = A.east_ports[0], end_wg_def = self.CPout[1].wg_definition)
            else:
                T2 = WgElPortTaperExtended(start_port = A.east_ports[0], end_wg_def = self.CPout[1].wg_definition, length = self.automatic_taper_east_length)
                
            AC = Structure(elements = [ SRef(A, (0.0, 0.0)), T1,T2], 
                           ports = [T1.west_ports[0], 
                                    T2.east_ports[0]]                          
                       )
        return AC
            
        
    def define_a1c(self):
        return self.__get_arm_content__(self.arm1)

    def define_a2c(self):
        return self.__get_arm_content__(self.arm2)
    
    def define_in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos (self):
        in_coupler_pos = Coord2(0.0, 0.0)
        
        y_1 = self.R1.out_ports[0].position.y
        y_2 = self.R2.out_ports[0].position.y
        
        R3 = RouteToWestAtY(input_port = self.CPout[1], 
                            y_position = y_1, 
                            bend_radius=self.bend_radius,
                            rounding_algorithm = self.rounding_algorithm)
        R4 = RouteToWestAtY(input_port = self.CPout[0], 
                            y_position = y_2, 
                            bend_radius=self.bend_radius,
                            rounding_algorithm = self.rounding_algorithm)
            
        #S1in = self.R1.size_info
        #S2in = self.R2.size_info
        #S1out = R3.size_info
        #S2out = R4.size_info
        R1w = abs(self.R1.ports[0].x-self.R1.ports[1].x)   
        R2w = abs(self.R2.ports[0].x-self.R2.ports[1].x)
        R3w = abs(R3.ports[0].x-R3.ports[1].x)
        R4w = abs(R4.ports[0].x-R4.ports[1].x)
        
        L1 = self.A1C.east_ports[0].x - self.A1C.west_ports[0].x 
        L2 = self.A2C.east_ports[0].x - self.A2C.west_ports[0].x 
        #L = max(L1 + S1in.width + S1out.width , L2 + S2in.width + S2out.width) + 0.5
        L = max(L1 + R1w + R3w , L2 + R2w + R4w) + 0.5

        OPin_max = max(self.R1.out_ports[0].x, self.R2.out_ports[0].x)
        OPout_max = min(R3.out_ports[0].x, R4.out_ports[0].x)
        arm1_pos = Coord2(OPin_max , y_1) - self.A1C.west_ports[0].position
        arm2_pos = Coord2(OPin_max  , y_2) - self.A2C.west_ports[0].position

        out_coupler_pos = Coord2(max(L1, L2) + OPin_max - OPout_max, 0.0)
        R3.move(out_coupler_pos)
        R4.move(out_coupler_pos)
        
        return (in_coupler_pos,self.R1,self.R2,R3,R4,arm1_pos,arm2_pos,out_coupler_pos)
        
    def define_in_coupler_pos(self):
        return Coord2(0.0,0.0)
    
    def define_R1(self):
        if self.separation is None:
            return RouteToEast(input_port = self.CPin[1],#.move_copy(in_coupler_pos), 
                             bend_radius=self.bend_radius,
                             rounding_algorithm = self.rounding_algorithm)
        else:
            return RouteToEastAtY(input_port = self.CPin[1],#.move_copy(in_coupler_pos), 
                                y_position = 0.5*self.separation,
                                bend_radius=self.bend_radius,
                                rounding_algorithm = self.rounding_algorithm)
        
    def define_R2(self):
        if self.separation is None:
            return RouteToEast(input_port = self.CPin[0],#.move_copy(in_coupler_pos), 
                             bend_radius=self.bend_radius,
                             rounding_algorithm = self.rounding_algorithm)
        else:
            return RouteToEastAtY(input_port = self.CPin[0],#.move_copy(in_coupler_pos), 
                                y_position = -0.5*self.separation,
                                bend_radius=self.bend_radius,
                                rounding_algorithm = self.rounding_algorithm)
        
    def define_R3(self):
        return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[3] 
    
    def define_R4(self):
        return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[4]     
    
    def define_arm1_pos(self):
        return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[5]     
    
    def define_arm2_pos(self):
        return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[6]         
    
    def define_out_coupler_pos(self):
        return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[7]     
    
    #def define_in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos (self):
        #in_coupler_pos = Coord2(0.0, 0.0)
        
        #if self.separation is None:
            #R1 = RouteToEast(input_port = self.CPin[1],#.move_copy(in_coupler_pos), 
                             #bend_radius=self.bend_radius,
                             #rounding_algorithm = self.rounding_algorithm)
            #R2 = RouteToEast(input_port = self.CPin[0],#.move_copy(in_coupler_pos), 
                             #bend_radius=self.bend_radius,
                             #rounding_algorithm = self.rounding_algorithm)
        #else:
            #R1 = RouteToEastAtY(input_port = self.CPin[1],#.move_copy(in_coupler_pos), 
                                #y_position = 0.5*self.separation,
                                #bend_radius=self.bend_radius,
                                #rounding_algorithm = self.rounding_algorithm)
            #R2 = RouteToEastAtY(input_port = self.CPin[0],#.move_copy(in_coupler_pos), 
                                #y_position = -0.5*self.separation,
                                #bend_radius=self.bend_radius,
                                #rounding_algorithm = self.rounding_algorithm)
        #y_1 = R1.out_ports[0].position.y
        #y_2 = R2.out_ports[0].position.y
        
        #R3 = RouteToWestAtY(input_port = self.CPout[1], 
                            #y_position = y_1, 
                            #bend_radius=self.bend_radius,
                            #rounding_algorithm = self.rounding_algorithm)
        #R4 = RouteToWestAtY(input_port = self.CPout[0], 
                            #y_position = y_2, 
                            #bend_radius=self.bend_radius,
                            #rounding_algorithm = self.rounding_algorithm)
            
        #S1in = R1.size_info
        #S2in = R2.size_info
        #S1out = R3.size_info
        #S2out = R4.size_info
        ##R1w = abs(R1.ports[0].x-R1.ports[1].x)   
        ##R2w = abs(R2.ports[0].x-R2.ports[1].x)
        ##R3w = abs(R3.ports[0].x-R3.ports[1].x)
        ##R4w = abs(R4.ports[0].x-R4.ports[1].x)
        
        #L1 = self.A1C.east_ports[0].x - self.A1C.west_ports[0].x 
        #L2 = self.A2C.east_ports[0].x - self.A2C.west_ports[0].x 
        #L = max(L1 + S1in.width + S1out.width , L2 + S2in.width + S2out.width) + 0.5
        ##L = max(L1 + R1w + R3w , L2 + R2w + R4w) + 0.5

        #OPin_max = max(R1.out_ports[0].x, R2.out_ports[0].x)
        #OPout_max = min(R3.out_ports[0].x, R4.out_ports[0].x)
        #arm1_pos = Coord2(OPin_max , y_1) - self.A1C.west_ports[0].position
        #arm2_pos = Coord2(OPin_max  , y_2) - self.A2C.west_ports[0].position

        #out_coupler_pos = Coord2(max(L1, L2) + OPin_max - OPout_max, 0.0)
        #R3.move(out_coupler_pos)
        #R4.move(out_coupler_pos)
        
        #return (in_coupler_pos,R1,R2,R3,R4,arm1_pos,arm2_pos,out_coupler_pos)
        
    #def define_in_coupler_pos(self):
        #return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[0]
    
    #def define_R1(self):
        #return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[1] 

    #def define_R2(self):
        #return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[2] 
    
    #def define_R3(self):
        #return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[3] 
    
    #def define_R4(self):
        #return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[4]     
    
    #def define_arm1_pos(self):
        #return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[5]     
    
    #def define_arm2_pos(self):
        #return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[6]         
    
    #def define_out_coupler_pos(self):
        #return self.in_coupler_pos_R1_R2_R3_R4_arm1_pos_arm2_pos_out_coupler_pos[7]     
            
    def define_elements(self, elems):
        elems += SRef(self.in_coupler, self.in_coupler_pos)
        elems += SRef(self.out_coupler, self.out_coupler_pos)
        elems += SRef(self.A1C, self.arm1_pos)
        elems += SRef(self.A2C, self.arm2_pos)
        
        R1,R2,R3,R4 = self.R1, self.R2, self.R3, self.R4
        
        R1 += self.A1C.west_ports[0].position.move_copy(self.arm1_pos)
        elems +=RouteConnector(R1,manhattan = self.manhattan)
        
        R2 += self.A2C.west_ports[0].position.move_copy(self.arm2_pos)
        elems +=RouteConnector(R2,manhattan = self.manhattan)
        
        R3 += self.A1C.east_ports[0].position.move_copy(self.arm1_pos)
        elems +=RouteConnector(R3,manhattan = self.manhattan)
        
        R4 += self.A2C.east_ports[0].position.move_copy(self.arm2_pos)
        elems +=RouteConnector(R4,manhattan = self.manhattan)
        return elems        
    
    def define_ports(self, ports):
        ports += self.in_coupler.in_ports.transform_copy(self.in_coupler_transform).translate(self.in_coupler_pos) 
        ports += self.out_coupler.out_ports.transform_copy(self.out_coupler_transform).translate(self.out_coupler_pos)
        return ports
    
class WgMziGeneric(__WgMzi__):
    __name_prefix__ = "MZIWGG"
    in_coupler = StructureProperty(required = True)
    out_coupler = StructureProperty(required = True)
    in_coupler_transform = TransformationProperty()
    out_coupler_transform = TransformationProperty()

class __Mzi11Y90__(__MziBase__):
    """ abstract 1x1 MZI that has 2 Y splitters as its couplers """
    
    def define_in_coupler(self):        
        return WgY90Splitter(bend_radius = self.bend_radius,
                             wg_definition= self.wg_definition)
        
    def define_out_coupler(self):        
        return WgY90Combiner(bend_radius = self.bend_radius,
                             wg_definition= self.wg_definition)

    def define_in_coupler_transform(self):                
        return IdentityTransform()
        
    def define_out_coupler_transform(self):
        return IdentityTransform()
    
class __WgMziAutoArms__(__WgMzi__):        
    arm1 = DefinitionProperty(fdef_name = "define_arm1")
    arm2 = DefinitionProperty(fdef_name = "define_arm2")
    
    def __init__(self, **kwargs):
        kwargs["arm1"] = SUPPRESSED
        kwargs["arm2"] = SUPPRESSED
        super(__WgMziAutoArms__, self).__init__(**kwargs)
        
class __WgMziSymmetric__(__WgMziAutoArms__):
    """ abstract base for symmetric MZI with simple waveguides """
    __name_prefix__ = "MZIWG_symm"
    arm_length = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)

    def define_arm1(self):      
        arm_name = self.name+"_arm1"
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition
        wg_def = WgElDefinition()
        wg = wg_def(shape = [(0.0,0.0),(self.arm_length,0.0)])
        wg_struct = Structure(name = arm_name, elements = [wg], ports = wg.ports)
        return wg_struct
    
    def define_arm2(self):
        return self.arm1
    
class __WgMziAsymmetric__(__WgMziAutoArms__):
    """ abstract base for asymmetric MZI with simple delay waveguides """
    __name_prefix__ = "MZIWG_asymm"
    straight1 = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    straight2 = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    
    def define_arm1(self):   
        return __MziDelaySimple__(straight = self.straight1,
                                  bend_radius = self.bend_radius,
                                  rounding_algorithm = self.rounding_algorithm,
                                  wg_definition = self.wg_definition,
                                  manhattan = self.manhattan)
    
    def define_arm2(self):       
        return __MziDelaySimpleFlipped__(straight = self.straight2,
                                         bend_radius = self.bend_radius,
                                         rounding_algorithm = self.rounding_algorithm,
                                         wg_definition = self.wg_definition,
                                         manhattan = self.manhattan)
    
class __WgMziSpiralAsymmetric__(__WgMziAutoArms__):
    """ abstract base for asymmetric MZI with spiral delay waveguides """
    __name_prefix__ = "MZISPIRAL_asymm"
    total_length1 = NumberProperty(required = True)
    total_length2 = NumberProperty(required = True)
    no_loops = IntProperty(required = True)

    def define_arm1(self):        
        return __MziDelaySpiral__(total_length = self.total_length1,
                                  no_loops = self.no_loops,
                                  bend_radius = self.bend_radius,
                                  spacing = TECH.WG.SPACING,
                                  wg_definition = self.wg_definition,
                                  manhattan = self.manhattan
                                  )
    
    def define_arm2(self):         
        return __MziDelaySpiralFlipped__(total_length = self.total_length2,
                                         no_loops = self.no_loops,
                                         bend_radius  = self.bend_radius,
                                         spacing = TECH.WG.SPACING,
                                         wg_definition = self.wg_definition,
                                         manhattan = self.manhattan
                                         )
    
class WgMzi1x1Y90(__Mzi11Y90__, __WgMzi__):
    """ 1x1 MZI with simple waveguides and Y splitters. Container for given arms. """
    __name_prefix__ = "MZI11WG_Y90"

class WgMzi1x1Y90Symmetric(__Mzi11Y90__,__WgMziSymmetric__):
    """ symmetric 1x1 MZI with Y splitters and simple waveguides """
    __name_prefix__ = "MZI11WG_Y90_symm"

class WgMzi1x1Y90Asymmetric(__Mzi11Y90__, __WgMziAsymmetric__):
    """ asymmetric 1x1 MZI with Y splitters and simple delay waveguides """
    __name_prefix__ = "MZI11WG_Y90_asymm"    
  
class WgMziSymmetric(__WgMziSymmetric__, WgMziGeneric):
    """ symmetric MZI with arbitrary couplers """
    __name_prefix__ = "MZIWG_sym"

class WgMziAsymmetric(__WgMziAsymmetric__, WgMziGeneric):
    """ asymmetric MZI with arbitrary couplers """
    __name_prefix__ = "MZIWG_asym"

