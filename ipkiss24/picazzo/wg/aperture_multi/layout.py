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



from ..aperture import DeepWgAperture, ApertureProperty
from ..aperture.layout import __WgAperture__
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.all import *
from numpy import sign
from math import acos, cos, sin

__all__ = ["WgApertureMultiFrom1d",
           "WgApertureMultiFrom1dGeneric",
           "DeepWgApertureMerged",
           "DeepWgApertureMulti"]

class __WgApertureMulti__(__WgAperture__):
    """ generic multiple aperture class """
    __name_prefix__ = "APMabstract"
    vectors = RestrictedProperty(restriction = RestrictList(RestrictType(Vector)), required = True)
    dummy_list = RestrictedProperty(restriction = RestrictList(RESTRICT_INT), default = [])
    actual_dummy_list = DefinitionProperty(fdef_name = "define_actual_dummy_list")
    trans = DefinitionProperty(fdef_name = "define_trans")

    def define_name(self):
        p  = "".join(["%f,%f,%f" %(v.x, v.y,v.angle_deg) for v in self.vectors])
        dl = "".join([str(i) for i in self.dummy_list])
        
        return "%s_V%d_%d" % (self.__name_prefix__, 
                              do_hash(p), 
                              do_hash(dl))

    def define_trans(self):
        trans = [transformation_from_vector(v) for v in self.vectors]
        return trans

        
    def define_actual_dummy_list(self):
        L = len(self.vectors)
        return [i%L for i in self.dummy_list]



class WgApertureMultiFrom1dGeneric(__WgApertureMulti__):
    """ creates a Multiple aperture from a list of 1D apertures by positioning several them rotated at a given angle."""
    __name_prefix__ = "APMS"
    apertures_1d = RestrictedListProperty(allowed_types = [__WgAperture__], required = True)
    
    def define_name(self):
        p  = "".join(["%f,%f,%f" %(v.x, v.y,v.angle_deg) for v in self.vectors])
        n = "".join([A.name for A in self.apertures_1d])
        dl = "".join([str(i) for i in self.dummy_list])        
        return "%s_%d_V%d_%d" % (self.__name_prefix__,do_hash(n), do_hash(p) , do_hash(dl))

    def define_elements(self, elems):
        for i in range(len(self.trans)):
            elems += SRef(self.apertures_1d[i], (0.0, 0.0), self.trans[i]).flat_copy()
        return elems

    def define_ports(self, ports):
        if len(self.apertures_1d) != len(self.vectors): #FIXME -- maybe we should make a method "assess_correctness" in Structure, which is called after construction?
            raise AttributeError("Length of vectors and apertures_1d list is not equal in in WgApertureMultiFrom1dGeneric")        
        for i in range(len(self.trans)):
            if not i in self.actual_dummy_list:
                ports += self.apertures_1d[i].ports.transform_copy(self.trans[i])
        return ports

    

class WgApertureMultiFrom1d(WgApertureMultiFrom1dGeneric):
    """ creates a Multiple aperture from a 1D aperture by positioning several copies rotated at a given angle."""
    __name_prefix__ = "APM"
    apertures_1d = DefinitionProperty(fdef_name = "define_apertures_1d")
    aperture_1d = ApertureProperty(required = True)
    
    
    def define_name(self):
        p  = "".join(["%f,%f,%f" %(v.x, v.y,v.angle_deg) for v in self.vectors])
        dl = "".join([str(i) for i in self.dummy_list])
        return "%s_%s_V%d_%d" % (self.__name_prefix__, self.aperture_1d.name, do_hash(p), do_hash(dl))
    
    def define_apertures_1d(self):
        return [self.aperture_1d for i in range(len(self.vectors))]

    

class __DeepWgApertureMulti__(__WgApertureMulti__):
    """ abstract base class for a multiple deep waveguide aperture """
    aperture_wg_definition = WaveguideDefProperty(required=True)
    wg_definition = WaveguideDefProperty(required=True)
    taper_length = PositiveNumberProperty(default = 30.0)
    aperture_1d = DefinitionProperty(fdef_name = "define_aperture_1d")    
    
    def define_aperture_1d(self):
        return DeepWgAperture(aperture_wg_definition = self.aperture_wg_definition, wg_definition = self.wg_definition, center = (0.0, 0.0), taper_length = self.taper_length)

    def define_ports(self, ports):
        for i in range(len(self.trans)):
            if not i in self.actual_dummy_list:
                T = self.trans[i]
                ports += self.aperture_1d.ports.transform_copy(T)
        return ports
    

class DeepWgApertureMulti(__DeepWgApertureMulti__, WgApertureMultiFrom1d):
    """ multiple deep waveguide aperture based on repetrition of a single deep wg aperture """
    __name_prefix__ = "APDM"
    
        
class DeepWgApertureMerged(__DeepWgApertureMulti__):
    """ multiple deep waveguide aperture with a single merged trench"""
    __name_prefix__ = "APDB"
    
    def define_elements(self, elems):
        # get orientation sign
        if len(self.vectors) <=1:
            sign = 1
        else:
            c1 = Coord2(0.0, 0.0)
            c2 = Coord2(self.taper_length, 0.0)
            S1 = Shape([c1.transform_copy(T) for T in self.trans])
            S2 = Shape([c2.transform_copy(T) for T in self.trans])
            S2.reverse()
            sign = (S1 + S2).orientation()

        # ordinary taper
        S = Shape(ShapeWedge(begin_coord=(0.0, 0.0), end_coord=(self.taper_length, 0.0), begin_width=self.aperture_wg_definition.wg_width, end_width=self.wg_definition.wg_width))
        # dummy taper
        SD1 = Shape(ShapeWedge(begin_coord=(0.0, 0.0), end_coord=(0.5*self.taper_length, 0.0), begin_width=self.aperture_wg_definition.wg_width, end_width=0.5*self.wg_definition.wg_width + 0.5*self.aperture_wg_definition.wg_width))
        SD2 = Shape(ShapeWedge(begin_coord=(0.5*self.taper_length,  0.0), end_coord=(self.taper_length, 0.0), begin_width=0.5*self.wg_definition.wg_width + 0.5*self.aperture_wg_definition.wg_width, end_width=self.aperture_wg_definition.wg_width))
        S_dummy = Shape([SD1[0], SD1[1], SD1[2], SD2[2], SD2[3], SD1[3]], closed = True)
        if sign < 0:
            S.v_mirror()
            S_dummy.v_mirror()
        start = True
        T1 = Shape()
        T2 = Shape()
        shapelist = []
        for i  in range(len(self.trans)):
            T = self.trans[i]
            if i in self.actual_dummy_list:
                S1 = S_dummy.transform_copy(T)
            else:
                S1 = S.transform_copy(T)
            shapelist.append(S1)
        
        elems += hull_inversion(shapelist, self.aperture_wg_definition.trench_width, self.wg_definition.trench_width, sign, (True, False))
        for S1 in shapelist:
            elems += Boundary(PPLayer(self.aperture_wg_definition.process, TECH.PURPOSE.LF.LINE), S1)
        return elems
    
                  

def hull_inversion_segment(shape0, shape1, trench_width, stub_sharp_angles = True, process = TECH.PROCESS.WG):
    S0 = shape0
    sh0 = shape0[1:2]
    A0 = S0.angles_deg()

    S1 = shape1
    sh1 = shape1[1:2]
    A1 = S1.angles_deg()

    T1 = Shape()

    elements = ElementList()

    #D = distance(S0[1], S1[1])
    L1 = straight_line_from_two_points(S1[0], S1[1])
    L0 = straight_line_from_two_points(S0[0], S0[1])
    P0 = L0.closest_point(S1[1])
    P1 = L1.closest_point(S0[1])
    P0b = 2*P0-S1[1]
    P1b = 2*P1-S0[1]
    # determine closest point: either distance to line, or distance to vertex
    D_points = distance(S0[1], S1[1])
    D_lines1 = L1.distance(S0[1])
    if lines_cross(S1[0], S1[1], S0[1], P1b):
        D1 = D_lines1
    else:
        D1 = D_points
    
    D_lines0 = L0.distance(S1[1])
    if lines_cross(S0[0], S0[1], S1[1], P0b):
        D0 = D_lines0
    else:
        D0 = D_points
    D = min(D0, D1)
    D_lines = min(D_lines0, D_lines1)
    if lines_cross(S0[0], S0[1], S1[0], S1[1]):
        # overlapping
        I = intersection(S1[1], S1[0], S0[1], S0[0])
        if lines_cross(S0[2], S0[1], S1[2], S1[1]):
            # end faces cross
            es = ShapeStub(original_shape = [S1[0], I, S0[0]], stub_width = TECH.TECH.MINIMUM_SPACE+2*0.015)
            astub = angle_deg(es[1], es[2])
            I2 = intersection(S0[2], S0[1], S1[2], S1[1])
            T1 += I2
            
            sh0 = Shape([I2, es[1].move_polar_copy(0.015, astub+180.0), es[2].move_polar_copy(0.015, astub), es[2].move_polar_copy(TECH.TECH.MINIMUM_SPACE, A0[0]+180.0) ])
            sh1 = Shape([I2, es[2].move_polar_copy(0.015, astub), es[1].move_polar_copy(0.015, astub+180.0), es[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, A1[0]+180.0) ])
            return (T1, elements, sh0, sh1)

        elif S0.encloses(S1[1]):
            es = ShapeStub(original_shape = [S1[0], I, S0[0]], stub_width = TECH.TECH.MINIMUM_SPACE+2*0.015)
            astub = angle_deg(es[1], es[2])
            sh0 = Shape([S0[1], es[1].move_polar_copy(0.015, astub+180.0), es[2].move_polar_copy(0.015, astub), es[2].move_polar_copy(TECH.TECH.MINIMUM_SPACE, A0[0]+180.0) ])
            sh1 = Shape([S0[1], S1[1], es[2].move_polar_copy(0.015, astub), es[1].move_polar_copy(0.015, astub+180.0), es[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, A1[0]+180.0) ])

            
            T1 += [S0[1]]
            return (T1, elements, sh0, sh1)
        elif S1.encloses(S0[1]):
            es = ShapeStub(original_shape = [S1[0], I, S0[0]], stub_width = TECH.TECH.MINIMUM_SPACE+2*0.015)
            astub = angle_deg(es[1], es[2])
            sh0 = Shape([S1[1], S0[1], es[1].move_polar_copy(0.015, astub+180.0), es[2].move_polar_copy(0.015, astub), es[2].move_polar_copy(TECH.TECH.MINIMUM_SPACE, A0[0]+180.0) ])
            sh1 = Shape([S1[1], es[2].move_polar_copy(0.015, astub), es[1].move_polar_copy(0.015, astub+180.0), es[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, A1[0]+180.0) ])

            T1 += [S1[1]]
            return (T1, elements, sh0, sh1)

            
    if D < 1.5*TECH.TECH.MINIMUM_SPACE:
        # too close for technology: add correction
        es = ShapeStub(original_shape = [S1[0], intersection(S1[0], S1[1], S0[0], S0[1]), S0[0]], stub_width = max(D,TECH.TECH.MINIMUM_SPACE)+2*0.015)
        astub = angle_deg(es[1], es[2])
        sh0 = Shape([S0[1], S1[1], es[1].move_polar_copy(0.015, astub+180.0), es[2].move_polar_copy(0.015, astub), es[2].move_polar_copy(TECH.TECH.MINIMUM_SPACE, A0[0]+180.0) ])
        sh1 = Shape([S1[1], S0[1], es[2].move_polar_copy(0.015, astub), es[1].move_polar_copy(0.015, astub+180.0), es[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, A1[0]+180.0) ])
        T1 += [S0[1], S1[1]]
    elif D_points < 2*TECH.TECH.MINIMUM_SPACE:
        t0 = turn_deg(S0[0], S0[1], S1[1])
        t1 = turn_deg(S1[0], S1[1], S0[1])
        if abs(t0) < 88.0 and abs(t1) < 88.0:
            T1 += [S0[1], S1[1]]
        else:
            if abs(t0) > abs(t1):
                a = sign(t0) * RAD2DEG*acos(TECH.TECH.MINIMUM_SPACE/D_points) + A0[0]
                T1 += [S0[1], S0[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, a), S1[1]]
            else:
                a = sign(t1) * RAD2DEG*acos(TECH.TECH.MINIMUM_SPACE/D_points) + A1[0]
                T1 += [S0[1], S1[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, a), S1[1]]
    elif D_lines < 2*TECH.TECH.MINIMUM_SPACE:
        t0 = turn_deg(S0[0], S0[1], S1[1])
        t1 = turn_deg(S1[0], S1[1], S0[1])
        if abs(t0) < 88.0 and abs(t1) < 88.0:
            T1 += [S0[1], S1[1]]
        else:
            if abs(t0) > abs(t1):
                if abs(t0) >=93.0: 
                    a = A0[1]+180.0 + sign(t0)*3.0
                else: 
                    a = A0[0] - sign(t0) * 85.0
                T1 += [S0[1], S0[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, a), S1[1]]
            else:
                if abs(t1) >=93.0: 
                    a = A1[1]+180.0+ sign(t1)*3.0
                else: 
                    a = A1[0] - sign(t1) * 85.0
                T1 += [S0[1], S1[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, a), S1[1]]

    elif D_points < 2*trench_width:

        t0 = shape0.turns_deg()[1]
        if abs(t0) >=93.0: 
            a0 = A0[1]+180.0 + sign(t0)*3.0
            d0 = trench_width
        else: 
            a0 = A0[0] - sign(t0) * 85.0
            d0 = trench_width / sin(DEG2RAD*(abs(t0) - 5.0))

        t1 = shape1.turns_deg()[1]
        if abs(t1) >=93.0: 
            a1 = A1[1]+180.0+ sign(t1)*3.0
            d1 = trench_width
        else: 
            a1 = A1[0] - sign(t1) * 85.0
            d1 = trench_width / sin(DEG2RAD*(abs(t1) - 5.0))

        p0 = S0[1].move_polar_copy(d0, a0)
        p1 = S1[1].move_polar_copy(d1, a1)
        if lines_cross(S0[1], p0, S1[1], p1):
            T1 += [S0[1], 0.5*(p0 + p1), S1[1]]
        else:
            q0 = S0[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, a0)
            q1 = S1[1].move_polar_copy(TECH.TECH.MINIMUM_SPACE, a1)
            T1 += [S0[1], q0, q1, S1[1]]
    else:
        Tx = Shape()
        Tx += S0[1]
        t0 = shape0.turns_deg()[1]
        if abs(t0) <93.0: 
            Tx += S0[1].move_polar_copy(0.5*trench_width, A0[0] - sign(t0) * 85.0)
        Tx += S0[1].move_polar_copy(trench_width, A0[1]+180.0)

        t1 = shape1.turns_deg()[1]
        a1 = A1[1]+180.0
        Tx += S1[1].move_polar_copy(trench_width, A1[1]+180.0)
        if abs(t1) <93.0: 
            Tx += S1[1].move_polar_copy(0.5*trench_width, A1[0] - sign(t1) * 85.0)
        Tx += S1[1]
            
        if stub_sharp_angles:
            T1 += ShapeStub(original_shape = Tx, stub_width = TECH.TECH.MINIMUM_SPACE, only_sharp_angles = True)
        else:
            T1 += Tx
    
    return (T1, elements, sh0, sh1)

def hull_inversion(taper_shapes, in_trench_width, out_trench_width, orientation, stub_sharp_angles = (True, True), process = TECH.PROCESS.WG):
    
        if len(taper_shapes) == 0 :
            return []
        
        # get orientation sign
        sign = orientation
        elements = ElementList()

        new_taper_shapes = []

        start = True
        T1 = Shape()
        T2 = Shape()
        
        S1 = taper_shapes[0]
        A1 = S1.angles_deg()
        L1 = len(S1)/2
        
        
        D = distance(S1[0], S1[L1+1])
        p1 = S1[0].move_polar_copy(in_trench_width, 180.0 + A1[0])
        p0 = p1.move_polar_copy(D/3.0, 180.0 + A1[0] + sign * 85.0)
        p2 = p1.move_polar_copy(in_trench_width, 180.0 + A1[0] )
        shape0 = Shape([S1[-1], S1[0], S1[1]])
        shape1 = Shape([p0, p1, p2])
        (T1sh, el, sh0, sh1) = hull_inversion_segment(shape0, shape1, in_trench_width, stub_sharp_angles[0], process = process)
        T1 += [p0]
        T1 += T1sh.reversed()
                            
        p1 = S1[(L1+1)].move_polar_copy(out_trench_width,  A1[L1])
        p0 = p1.move_polar_copy(D/3.0, A1[L1] - sign * 85.0)
        p2 = p1.move_polar_copy(out_trench_width, A1[L1] )
        shape0 = Shape([S1[(L1+2)%(2*L1)], S1[L1+1], S1[L1]])
        shape1 = Shape([p0, p1, p2])
        (T2sh, el, sh2, sh3) = hull_inversion_segment(shape0, shape1, out_trench_width, stub_sharp_angles[1])
        T2 += [p0]
        T2 += T2sh.reversed()

        S0 = S1
        L0 = L1
        old_sh1 = Shape(S0[0])
        old_sh3 = Shape(S0[L0+1])
        for S1 in taper_shapes[1:]:
            L1 = len(S1)/2
            ##### T1 #####
            shape0 = Shape([S0[2], S0[1], S0[0]])
            shape1 = Shape([S1[-1], S1[0], S1[1]])
            (T1sh, el, sh0, sh1) = hull_inversion_segment(shape0, shape1, in_trench_width,stub_sharp_angles[0])
            T1 += T1sh
            elements += el

            ##### T2 #####
            shape0 = Shape([S0[L0-1], S0[L0], S0[L0+1]])
            shape1 = Shape([S1[(L1+2)%(2*L1)], S1[L1+1], S1[L1]])
            (T2sh, el, sh2, sh3) = hull_inversion_segment(shape0, shape1, out_trench_width,stub_sharp_angles[1])
            T2 += T2sh
            elements += el

            # add local inversion layer (not one monolithic shape to avoid cutting
            elements += Boundary(PPLayer(process,TECH.PURPOSE.LF_AREA), T1 + T2.reversed())
            T1 = T1sh
            T2 = T2sh

            # complete S0
            new_S0 = Shape(old_sh1)
            new_S0 += sh0
            new_S0 += S0[2:L0]
            new_S0 += sh2
            new_S0 += old_sh3
            new_S0 += S0[L0+1:]
            new_taper_shapes += [new_S0]

            S0 = S1
            L0 = L1
            old_sh1 = sh1
            old_sh1.reverse()
            old_sh3 = sh3
            old_sh3.reverse()

        # complete last 
        new_S1 = Shape(old_sh1, closed = True)
        new_S1 += S1[1:L1+1]
        new_S1 += old_sh3
        new_S1 += S0[L1+2:]
        new_taper_shapes += [new_S1]


        A1 = S1.angles_deg()
        
        D = distance(S1[1], S1[L1])
        p1 = S1[1].move_polar_copy(in_trench_width, A1[0])
        p0 = p1.move_polar_copy(D/3.0, A1[0] - sign * 85.0)
        p2 = p1.move_polar_copy(in_trench_width, A1[0] )
        shape0 = Shape([S1[2], S1[1], S1[0]])
        shape1 = Shape([p0, p1, p2])
        (T1sh, el, sh0, sh1) = hull_inversion_segment(shape0, shape1, in_trench_width,stub_sharp_angles[0])
        T1 += T1sh
        T1 += [p0]
                            
        p1 = S1[(L1)].move_polar_copy(out_trench_width,  180.0 + A1[L1])
        p0 = p1.move_polar_copy(D/3.0, 180.0 + A1[L1] + sign * 85.0)
        p2 = p1.move_polar_copy(out_trench_width, 180.0 + A1[L1] )
        shape0 = Shape([S1[L0-1], S1[L0], S1[L0+1]])
        shape1 = Shape([p0, p1, p2])
        (T2sh, el, sh2, sh3) = hull_inversion_segment(shape0, shape1, out_trench_width, stub_sharp_angles[1])
        T2 += T2sh
        T2 += [p0]

        T2.reverse()
        T1 += T2
        T1.close()
        elements += Boundary(PPLayer(process, TECH.PURPOSE.LF_AREA), T1)

        del taper_shapes[:]
        taper_shapes += new_taper_shapes
        return elements
