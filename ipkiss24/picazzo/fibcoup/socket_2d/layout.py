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



from ..socket import SocketProperty
from ..socket.layout import __WgSocket__
from ipkiss.plugins.photonics.port.port import OpticalPort
from ipkiss.plugins.photonics.wg.definition import WaveguideDefListProperty
from math import cos, sin, tan, sqrt
from ipkiss.all import *

__all__ = ["WgSocket2dFrom1d", 
           "BroadWgSocket2d",
           "BroadWgSocket2dAsymmetric",
           "BroadWgSocket3Port"]

class WgSocket2d(__WgSocket__):
    """ generic 2D socket class """
    pass


class WgSocket2dFrom1d(WgSocket2d):
    """ creates a 2D socket from a 1D socket by positioning 2 copies rotated at a given angle.
        If angle is 90.0, the sockets are positioned at position_1d and then rotated over half the angle """
    __name_prefix__ = "SOC2D"
    socket_1d = SocketProperty(required = True)
    position_1d = Coord2Property(required = True)
    dev_angle = AngleProperty(default = 0.0)
    process = ProcessProperty(default = TECH.PROCESS.WG)
    trans1 = DefinitionProperty(fdef_name = "define_trans1")
    trans2 = DefinitionProperty(fdef_name = "define_trans2")    

    def define_trans1(self):
        return Translation(self.position_1d) + Rotation((0.0, 0.0), 45.0 - self.dev_angle)

    def define_trans2(self):    
        return Translation(self.position_1d) + Rotation((0.0, 0.0), -45.0 + self.dev_angle)

    def define_elements(self, elems):
        E1 = SRef(self.socket_1d, (0.0, 0.0), self.trans1).flat_copy()
        E2 = SRef(self.socket_1d, (0.0, 0.0), self.trans2).flat_copy()
        elems += E1
        elems += E2
        return elems

    def define_ports(self, ports):
        return self.socket_1d.ports.transform_copy(self.trans1) + self.socket_1d.ports.transform_copy(self.trans2)


class BroadWgSocket2dAsymmetric(WgSocket2d):
    """ broad wavegudie socket for 2-D fiber coupler with west-east asymmetry for outcoupling """
    __name_prefix__ = "APBWG2D"
    wg_definitions = WaveguideDefListProperty(required=True)
    wg_lengths = RestrictedProperty(restriction = RestrictLen(2) & RestrictList(RESTRICT_POSITIVE), required = True)
    dev_angles = RestrictedProperty(restriction = RestrictLen(2) & RestrictList(RESTRICT_NUMBER), required = True)   
    waveguide_overlap  = NonNegativeNumberProperty(default = 0.05)
    trench_overlap = NonNegativeNumberProperty(default = 4.0)
    p_tr = DefinitionProperty(fdef_name = "define_p_tr")
    p_br = DefinitionProperty(fdef_name = "define_p_br")
    p_tl = DefinitionProperty(fdef_name = "define_p_tl")
    p_bl = DefinitionProperty(fdef_name = "define_p_bl")

    def define_p_tr(self):
        ww = max(self.wg_definitions[0].wg_width, self.wg_definitions[1].wg_width)
        return Coord2(0.0, 0.0).move_polar(0.5*ww + self.wg_lengths[0], 45-self.dev_angles[0])

    def define_p_br(self):
        ww = max(self.wg_definitions[0].wg_width, self.wg_definitions[1].wg_width)
        return Coord2(0.0, 0.0).move_polar(0.5*ww + self.wg_lengths[0], -45+self.dev_angles[0])

    def define_p_tl(self):
        ww = max(self.wg_definitions[0].wg_width, self.wg_definitions[1].wg_width)
        return Coord2(0.0, 0.0).move_polar(0.5*ww + self.wg_lengths[1], 135+self.dev_angles[1])

    def define_p_bl(self):
        ww = max(self.wg_definitions[0].wg_width, self.wg_definitions[1].wg_width)
        return Coord2(0.0, 0.0).move_polar(0.5*ww + self.wg_lengths[1], -135-self.dev_angles[1])

    def define_elements(self, elems):  
        ww0 = self.wg_definitions[0].wg_width
        ww1 = self.wg_definitions[1].wg_width
        tw0 = self.wg_definitions[0].trench_width
        tw1 = self.wg_definitions[1].trench_width
        
        # OpticalPort corners
        p_tr1 = self.p_tr.move_polar_copy(0.5*ww0, 135-self.dev_angles[0])
        p_tr2 = self.p_tr.move_polar_copy(0.5*ww0, -45-self.dev_angles[0]),

        p_br1 = self.p_br.move_polar_copy(0.5*ww0, 45+self.dev_angles[0])
        p_br2 = self.p_br.move_polar_copy(0.5*ww0, -135+self.dev_angles[0]),

        p_tl1 = self.p_tl.move_polar_copy(0.5*ww1, -135+self.dev_angles[1])
        p_tl2 = self.p_tl.move_polar_copy(0.5*ww1, 45+self.dev_angles[1]),

        p_bl1 = self.p_bl.move_polar_copy(0.5*ww1, -45-self.dev_angles[1])
        p_bl2 = self.p_bl.move_polar_copy(0.5*ww1, 135-self.dev_angles[1]),

        # path shape from center to OpticalPort
        L_tr = ShapePath(original_shape = [(0.0, 0.0), self.p_tr], path_width = ww0)
        L_br = ShapePath(original_shape = [(0.0, 0.0), self.p_br], path_width = ww0)
        L_tl = ShapePath(original_shape = [(0.0, 0.0), self.p_tl], path_width = ww1)
        L_bl = ShapePath(original_shape = [(0.0, 0.0), self.p_bl], path_width = ww1)

        # indices for positions in the path (start_east, end_east, ...)
        i_sl = 0
        i_el = 1
        i_sr = 3
        i_er = 2

        sh_wg = (ShapeStub(original_shape = [L_tr[i_er], intersection(L_tr[i_sr], L_tr[i_er], L_br[i_sl], L_br[i_el]), L_br[i_el]], stub_width = TECH.TECH.MINIMUM_LINE) + 
                 ShapeStub(original_shape = [L_br[i_er], intersection(L_br[i_sr], L_br[i_er], L_bl[i_sl], L_bl[i_el]), L_bl[i_el]], stub_width = TECH.TECH.MINIMUM_LINE) +
                 ShapeStub(original_shape = [L_bl[i_er], intersection(L_bl[i_sr], L_bl[i_er], L_tl[i_sl], L_tl[i_el]), L_tl[i_el]], stub_width = TECH.TECH.MINIMUM_LINE) +
                 ShapeStub(original_shape = [L_tl[i_er], intersection(L_tl[i_sr], L_tl[i_er], L_tr[i_sl], L_tr[i_el]), L_tr[i_el]], stub_width = TECH.TECH.MINIMUM_LINE)
                 )
        sh_wg.close()

        # path shape from center to OpticalPort
        T_tr = ShapePath(original_shape = [(0.0, 0.0), self.p_tr], path_width = ww0 + 2* tw0)
        T_br = ShapePath(original_shape = [(0.0, 0.0), self.p_br], path_width = ww0 + 2* tw0)
        T_tl = ShapePath(original_shape = [(0.0, 0.0), self.p_tl], path_width = ww1 + 2* tw1)
        T_bl = ShapePath(original_shape = [(0.0, 0.0), self.p_bl], path_width = ww1 + 2* tw1)

        sh_tr = Shape([L_tr[i_er], T_tr[i_er], T_br[i_el], L_br[i_el]] + 
                      [L_br[i_er], T_br[i_er], T_bl[i_el], L_bl[i_el]] +
                      [L_bl[i_er], T_bl[i_er], T_tl[i_el], L_tl[i_el]]+
                      [L_tl[i_er], T_tl[i_er], T_tr[i_el], L_tr[i_el]]
                      )
        sh_tr.close()
        from ipkiss.process import PPLayer
        elems += Boundary(PPLayer(self.wg_definitions[0].process, TECH.PURPOSE.LF.LINE), sh_wg)
        elems += Boundary(PPLayer(self.wg_definitions[0].process, TECH.PURPOSE.LF_AREA), sh_tr)
        return elems


    def define_ports(self, ports):
        ports += [OpticalPort(position = self.p_tr, wg_definition = self.wg_definitions[0], angle = 45.0-self.dev_angles[0]),
                  OpticalPort(position = self.p_tl, wg_definition = self.wg_definitions[1], angle = 135.0+self.dev_angles[1]),
                  OpticalPort(position = self.p_bl, wg_definition = self.wg_definitions[1], angle = 225.0-self.dev_angles[1]),
                  OpticalPort(position = self.p_br, wg_definition = self.wg_definitions[0], angle = 315.0+self.dev_angles[0])]
        return ports



def BroadWgSocket2d(wg_definition, wg_length, dev_angle, **kwargs):
    """ broad waveguide socket for 2-D fiber coupler with west-east symmetry for outcoupling """
    return BroadWgSocket2dAsymmetric(wg_definitions = (wg_definition,wg_definition), wg_lengths = (wg_length,wg_length), dev_angles = (dev_angle, dev_angle), **kwargs)


class BroadWgSocket3Port(WgSocket2d):
    """abstract base class for waveguide socketith input and output waveguides, 3 ports"""    
    __name_prefix__ = "APBWG3P_W"
    wg_definitions = WaveguideDefListProperty(required=True)
    wg_lengths = RestrictedProperty(restriction = RestrictLen(2) & RestrictList(RESTRICT_POSITIVE), required = True)
    dev_angle = AngleProperty(default = 0.0)
    port3_offset = NumberProperty(required = True)
    waveguide_overlap  = NonNegativeNumberProperty(default = 0.05)
    trench_overlap = NonNegativeNumberProperty(default = 4.0)
    p_tr = DefinitionProperty(fdef_name = "define_p_tr")
    p_br = DefinitionProperty(fdef_name = "define_p_br")
    p_l = DefinitionProperty(fdef_name = "define_p_l")

    def define_p_tr(self):
        ww = self.wg_definitions[0].wg_width
        return Coord2(0.0, 0.0).move_polar(0.5*ww + self.wg_lengths[0], 45-self.dev_angle)

    def define_p_br(self):
        ww = self.wg_definitions[0].wg_width
        return Coord2(0.0, 0.0).move_polar(0.5*ww + self.wg_lengths[0], -45+self.dev_angle)

    def define_p_l(self):
        ww = self.wg_definitions[0].wg_width
        return Coord2(0.0, 0.0).move_polar(0.5*sqrt(0.5)*ww + self.wg_lengths[1]+self.port3_offset, 180.0)    

    def define_elements(self, elems):    
        ww0 = self.wg_definitions[0].wg_width
        ww1 = self.wg_definitions[1].wg_width
        
        # path shape from center to OpticalPort
        L_tr = ShapePath(original_shape = [(0.0, 0.0), self.p_tr], path_width = ww0)
        L_br = ShapePath(original_shape = [(0.0, 0.0), self.p_br], path_width = ww0)
        L_l = ShapePath(original_shape = [(0.0, 0.0), self.p_l], path_width = ww1)

        # indices for positions in the path (start_east, end_east, ...)
        i_sl = 0
        i_el = 1
        i_sr = 3
        i_er = 2

        sh_wg = (ShapeStub(original_shape = [L_tr[i_er], intersection(L_tr[i_sr], L_tr[i_er], L_br[i_sl], L_br[i_el]), L_br[i_el]], stub_width = TECH.TECH.MINIMUM_LINE) + 
                 ShapeStub(original_shape = [L_br[i_er], intersection(L_br[i_sr], L_br[i_er], L_tr[i_sr], L_tr[i_er]), L_l[i_el].move_copy((self.wg_lengths[1], 0.0)), L_l[i_el]], stub_width = TECH.TECH.MINIMUM_LINE, only_sharp_angles = True) +
                 ShapeStub(original_shape = [L_l[i_er], L_l[i_er].move_copy((self.wg_lengths[1], 0.0)), intersection(L_tr[i_el], L_tr[i_sl], L_br[i_el], L_br[i_sl]), L_tr[i_el]], stub_width = TECH.TECH.MINIMUM_LINE)
                 )
        sh_wg.close()

        # path shape from center to OpticalPort
        T_tr = ShapePath(original_shape = [(0.0, 0.0), self.p_tr], path_width = ww0 + 2* self.wg_definitions[0].trench_width)
        T_br = ShapePath(original_shape = [(0.0, 0.0), self.p_br], path_width = ww0+ 2* self.wg_definitions[0].trench_width)
        T_l = ShapePath(original_shape = [(0.0, 0.0), self.p_l], path_width = ww1+ 2* self.wg_definitions[0].trench_width)

        sh_tr = Shape([L_tr[i_er], T_tr[i_er], T_br[i_el], L_br[i_el], 
                       L_br[i_er], T_br[i_er],
                       (0.0, T_br[i_er].y),
                       T_l[i_el], L_l[i_el], L_l[i_er], T_l[i_er],
                       (0.0, T_tr[i_el].y),
                       T_tr[i_el], L_tr[i_el]
                       ]
                      )
        sh_tr.close()

        elems += Boundary(PPLayer(self.wg_definitions[0].process, TECH.PURPOSE.LF.LINE), sh_wg)
        elems += Boundary(PPLayer(self.wg_definitions[0].process, TECH.PURPOSE.LF_AREA), sh_tr)
        return elems

    def define_ports(self, ports):
        ports += [OpticalPort(position = self.p_tr, wg_definition = self.wg_definitions[0], angle = 45.0-self.dev_angle),
                 OpticalPort(position = self.p_br, wg_definition = self.wg_definitions[0], angle = 315.0+self.dev_angle),
                 OpticalPort(position = self.p_l, wg_definition = self.wg_definitions[1], angle = 180.0)]
        return ports

