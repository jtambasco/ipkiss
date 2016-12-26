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



from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.routing.to_line import RouteToEastAtY
from ipkiss.plugins.photonics.routing.connect import RouteConnectorRounded
from ipkiss.all import *

__all__ = ["SplitterTreeLeftToRight",
           "SplitterWithYSpacing"]

class SplitterTreeBasic(Structure):
    """ base class for splitter trees """
    __name_prefix__ = "SPLITTREE_"
    splitter = StructureProperty(required = True)
    branch_level = IntProperty(default = 1, restriction = RESTRICT_NONNEGATIVE)
    patches = DefinitionProperty(fdef_name = "define_patches")
    connectors = DefinitionProperty(fdef_name = "define_connectors")    
    splitter_transforms = DefinitionProperty(fdef_name = "define_splitter_transforms")
    
    def define_elements(self, elems):
        for t in self.splitter_transforms:
            elems += SRef(self.splitter, (0.0, 0.0), t)
        for C_list in self.connectors:
            elems += C_list
        return elems        
            
    def define_connectors(self):
        raise NotImplementedException("SplitterTreeBasic::define_connectors to be implemented by subclasses")
    
    def define_patches(self):        
        raise NotImplementedException("SplitterTreeBasic::define_patches to be implemented by subclasses")
    
    def define_splitter_transforms(self):        
        raise NotImplementedException("SplitterTreeBasic::define_splitter_transforms to be implemented by subclasses")
    
    def define_ports(self, P):
        P += self.splitter.in_ports.transform_copy(self.splitter_transforms[0])
        for C in self.connectors[-1]:
            # iterate over last level of connectors
            P += C.out_ports
        return P
        

class SplitterWithYSpacing(SplitterTreeBasic):
    """ creates a west-to-east splitter with arms spaced at a given Y spacing with the input at Y=0.0"""
    __name_prefix__ = "SPLIT_AT_Y"
    y_spacing = PositiveNumberProperty(required = True)
    branch_level = 1,
    connectors_splitter_transforms = DefinitionProperty(fdef_name = "define_connectors_splitter_transforms")    

    def define_connectors_splitter_transforms(self):
        T = -Translation(self.splitter.in_ports[0].position)
        #T = -Translation((0.0,0.0))
        splitter_transforms = [T]
        P = self.splitter.out_ports.y_sorted().transform_copy(T)
        connectors = [[RouteConnectorRounded(RouteToEastAtY(input_port = P[0], y_position = -0.5*self.y_spacing)),
                       RouteConnectorRounded(RouteToEastAtY(input_port = P[1], y_position = 0.5*self.y_spacing))]]
        return (connectors, splitter_transforms)
   
    def define_connectors(self):        
        return self.connectors_splitter_transforms[0]
    
    def define_splitter_transforms(self):        
        return self.connectors_splitter_transforms[1]    
    
        
class SplitterTreeLeftToRight(SplitterTreeBasic):
    """ a Left-to-east splitter tree """
    __name_prefix__ = "SPLITTREE_LR_"
    y_spacing = PositiveNumberProperty(required = True)
    patches_connectors_splitter_transforms = DefinitionProperty(fdef_name = "define_patches_connectors_splitter_transforms")    
    
    def define_patches_connectors_splitter_transforms(self):
        N = 2 ** self.branch_level
        L = self.splitter.out_ports.size_info().east - self.splitter.in_ports.size_info().west
        T = [Translation(-self.splitter.in_ports[0].position)]
        splitter_transforms = []
        splitter_transforms += T
        connectors = []
        patches = []
        for i in range(self.branch_level):
            C = []
            P = []
            T2 = []
            Y = 0.5 * self.y_spacing * 2**(self.branch_level-i)
            for t in T:
                P_out = self.splitter.out_ports.y_sorted().transform_copy(t)
                P_in = self.splitter.in_ports.transform_copy(t)
                c1 = RouteConnectorRounded(RouteToEastAtY(input_port = P_out[0], y_position = P_in[0].y - 0.5*Y))
                c2 = RouteConnectorRounded(RouteToEastAtY(input_port = P_out[1], y_position = P_in[0].y + 0.5*Y))
                C += [c1, c2]
                # patch sharp angle between connectors
                c1i = c1.in_ports[0]
                c2i = c2.in_ports[0]
                c1o = c1.out_ports[0]
                c2o = c2.out_ports[0]
                xl = min(c1i.position.x,c2i.position.x)+0.5*c1.shape.start_straight
                yl = 0.5*(c1i.position.y+c2i.position.y)
                xr = max(c1o.position.x,c2o.position.x)-0.5*c1.shape.end_straight
                wp = abs(c2o.position.y-c1o.position.y)+0.5*(c1o.wg_definition.wg_width+c2o.wg_definition.wg_width)+c1o.wg_definition.trench_width+c2o.wg_definition.trench_width
                ## patches necessary??? probably depends on the splitter you take
                #P += [Line(layer=PPLayer(self.splitter.wg_definition.process, TECH.PURPOSE.LF_AREA),begin_coord=(xl,yl),end_coord=(xr,yl),line_width=wp)]
                if i < self.branch_level-1:
                    T2 += [Translation(coord2_match_position(self.splitter.in_ports[0], c1.out_ports[0])),
                           Translation(coord2_match_position(self.splitter.in_ports[0], c2.out_ports[0]))]
        
            connectors += [C]
            patches += [P]
            splitter_transforms += T2
            T = T2
        return (patches,connectors,splitter_transforms)
        
    def define_patches(self):        
        return self.patches_connectors_splitter_transforms[0]
    
    def define_connectors(self):        
        return self.patches_connectors_splitter_transforms[1]
    
    def define_splitter_transforms(self):        
        return self.patches_connectors_splitter_transforms[2]    
    
    def define_elements(self, elems):
        for t in self.splitter_transforms:
            elems += SRef(self.splitter, (0.0, 0.0), t)
        for C_list in self.connectors:
            elems += C_list
        for P_list in self.patches:
            elems += P_list
        return elems