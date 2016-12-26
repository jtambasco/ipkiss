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
Waveguide element bundles

"""

from ipkiss.plugins.photonics.wg.connect import WaveguidePointRoundedConnectElementDefinition, __RoundedWaveguide__
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.plugins.photonics.port import *
from ipkiss.all import *

__all__ = ["WgElBundleWaveguides",
           "WgElBundle",
           "WgElBundleConnectRounded"]

class WgElBundleWaveguides(Group):
    """ bundle of waveguides, with a common inversion layer. the shapes should be in the east order for the inversion layer to work """
    process = ProcessProperty(default = TECH.PROCESS.WG)
    waveguides = RestrictedProperty(restriction = RestrictTypeList(Group), required = True) # maybe waveguide later on


    def define_waveguides(self):
        raise NotImplementedException("Subclass of WgElBundleWaveguides should implement method define_waveguides.")


    def define_elements(self, elems):
        for w in self.waveguides:
            elems += w

        if len(self.waveguides) <= 1:
            return elems
        S_T_first = self.waveguides[0].center_line() 
        S_T_last = self.waveguides[-1].center_line().reversed() 
        S_T_tmp = S_T_first + S_T_last
        orientation = -S_T_tmp.orientation()        

        ST_1 = Shape()
        ST_2 = Shape()
        for (wg1, Wg2) in zip(self.waveguides[:-1], self.waveguides[1:]):
            S1 = wg1.center_line()
            A1 = S1.angles_deg()
            S2 = Wg2.center_line()
            A2 = S2.angles_deg()
            D0 = distance(S1[0], S2[0])
            D1 = distance(S1[-1], S2[-1])
            w1 = wg1.in_ports[0].wg_definition.wg_width
            if hasattr(wg1.in_ports[0].wg_definition,'trench_width'):
                t1 = wg1.in_ports[0].wg_definition.trench_width
            else: t1 = 0.0
            w2 = Wg2.in_ports[0].wg_definition.wg_width
            if hasattr(Wg2.in_ports[0].wg_definition,'trench_width'):
                t2 = Wg2.in_ports[0].wg_definition.trench_width
            else: t2 = 0.0
            D_ref = t1 + t2 + 0.5*(w1 + w2)

            ST_1 += S1[0].move_polar_copy(0.5*w1, A1[0]+orientation * 90.0)
            if D0 > D_ref:
                ST_1 += S1[0].move_polar_copy(0.5*w1 + t1, A1[0]+orientation * 90.0)
                ST_1 += S2[0].move_polar_copy(0.5*w2 + t2, A2[0]-orientation * 90.0)
            ST_1 += S2[0].move_polar_copy(0.5*w2, A2[0]-orientation * 90.0)

            ST_2 += S1[-1].move_polar_copy(0.5*w1, A1[-2]+orientation * 90.0)
            if D1 > D_ref:
                ST_2 += S1[-1].move_polar_copy(0.5*w1+ t1, A1[-2]+orientation * 90.0)
                ST_2 += S2[-1].move_polar_copy(0.5*w2+ t2, A2[-2]-orientation * 90.0)
            ST_2 += S2[-1].move_polar_copy(0.5*w2, A2[-2]-orientation * 90.0)

        S_T = S_T_first + ST_2 + S_T_last + ST_1.reversed()
        S_T.close()
        elems += Boundary(PPLayer(self.process, TECH.PURPOSE.LF_AREA), S_T)
        return elems


    def define_ports(self, ports):
        P = OpticalPortList()
        for wg in self.waveguides:
            P += wg.in_ports
            P += wg.out_ports
        return P

    def lengths(self):
        return [wg.length() for wg in self.waveguides]

    def center_lines(self):
        return [wg.center_line() for wg in self.waveguides]


class __IdenticalWaveguides__(object):
    wg_widths = DefinitionProperty(fdef_name = "define_wg_widths")
    trench_width = DefinitionProperty(fdef_name = "define_trench_width")
    wg_width = PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH)
    trench_width = PositiveNumberProperty(default = TECH.WG.TRENCH_WIDTH)

    def define_wg_widths(self):
        wg_widths = [self.wg_width for i in range(len(self.shapes))]
        return wg_widths 

    def define_trench_widths(self):
        trench_widths = [self.trench_width for i in range(len(self.shapes))]
        return trench_widths


class WgElBundleGeneric(WgElBundleWaveguides):
    """ bundle of waveguides, with a common inversion layer. the shapes should be in the east order for the inversion layer to work """
    waveguides = DefinitionProperty(fdef_name = "define_waveguides")
    shapes = RestrictedProperty(restriction = RestrictTypeList(Shape), required = True)
    wg_widths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), required = True)
    trench_widths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), required = True)
    
    def __make_wg_element__(shape, wg_width, trench_width, process):
        wg_def = WgElDefinition(wg_width = wg_width , trench_width = trench_width, process = process)    
        return wg_def(shape = shape)

    def define_waveguides(self):
        if (len(self.shapes) != len(self.wg_widths) or
            len(self.wg_widths) != len(self.trench_widths)):
            raise AttributeError("Length of shapes, wg_widths and trench_widths should be identical in WgElBundleGeneric")
        waveguides = [self.__make_wg_element__(S, w, t, self.process) for (S,w,t) in zip(self.shapes, self.wg_widths, self.trench_widths)]
        return waveguides


class WgElBundle(__IdenticalWaveguides__, WgElBundleGeneric):
    """ bundle of waveguides, with a common inversion layer. the shapes should be in the right order for the inversion layer to work """
    pass


class WgElBundleConnectRoundedGeneric(__RoundedWaveguide__, WgElBundleGeneric):
    """ bundle of rounded waveguides, with a common inversion layer. the shapes should be in the right order for the inversion layer to work """

    bend_radii = RestrictedProperty(required = True, restriction = RestrictList(RESTRICT_POSITIVE))
    
    def define_waveguides(self):
        waveguides = []
        for (S,w,t, r) in zip(self.shapes, self.wg_widths, self.trench_widths, self.bend_radii):
            wg_def = WgElDefinition(wg_width = w, trench_width = t, process = self.process)
            connector_wg_def = WaveguidePointRoundedConnectElementDefinition(wg_definition = wg_def,
                                                                             bend_radius = r,
                                                                             manhattan = self.manhattan,
                                                                             rounding_algorithm = self.rounding_algorithm)		    
            waveguides.append(connector_wg_def(shape = S))
        return waveguides 


class WgElBundleConnectRounded(__IdenticalWaveguides__, WgElBundleConnectRoundedGeneric):
    """ bundle of rounded waveguides, with a common inversion layer. the shapes should be in the east order for the inversion layer to work """
    bend_radii = DefinitionProperty(fdef_name = "define_bend_radii")    


    def define_bend_radii(self):
        bend_radii = [self.bend_radius for i in range(len(self.shapes))]
        return bend_radii




