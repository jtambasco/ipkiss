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
from ipkiss.geometry.shapes.spline import ShapeRoundAdiabaticSpline, ShapeRoundAdiabaticSplineGeneric, SplineRoundingAlgorithm
from picazzo.filters.ring import RingRoundedShape
from picazzo.filters.ring.layout import __RingStraightCouplers__, __RingCouplerTransformation1__, __Ring180CouplerTransformation2__, __RingWaveguideCouplers1__, __RingWaveguideCouplers2__, __Ring90CouplerTransformation2__


import functools

__all__ = ["RingAdiabaticSpline","RingSplineNotchFilter","RingSpline180DropFilter","RingSpline90DropFilter"]

def PartialProperty(internal_member_name= None, restriction = None,**kwargs):    
    R = restrictions.RestrictType(functools.partial) & restriction
    P = RestrictedProperty(internal_member_name, restriction = R,**kwargs)   
    P.__get_default__ = lambda : P.default
    return P

class RingAdiabaticSpline(RingRoundedShape):
    """ base Class: Ring with adiabatic spline bends """
    __name_prefix__ = "RINGSPLINE"
    length = PositiveNumberProperty(required = True)
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    straight = NonNegativeNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    adiabatic_angle_in_coupler = NonNegativeNumberProperty(default=10.0)
    adiabatic_angle_in_ring = NonNegativeNumberProperty(default=10.0)
    process = ProcessProperty(default = TECH.PROCESS.WG)
    
    shape = DefinitionProperty(fdef_name = "define_shape")
    straights = DefinitionProperty(fdef_name = "define_straights")

    rounding_algorithm = PartialProperty()
    
    def define_straights(self):
        return (self.straight,)
    
    def define_rounding_algorithm(self):
        return SplineRoundingAlgorithm(adiabatic_angles = (self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_ring))
    
    def get_ring(self):
        return self.ring_wg_definition(shape = self.get_shape())
    
    def get_bend90_size(self):
        B = self.rounding_algorithm(original_shape = [(-100* self.bend_radius, 0.0), (0.0, 0.0), (0.0, 100*self.bend_radius)], 
                                    radius = self.bend_radius)
        bend_size = B[1:-1].size_info.size
        return (bend_size[0]+0.01, bend_size[1]+0.01)
    
    def define_straights(self):
        (bs1,bs2) = self.get_bend90_size()
        rect_size = (2 * bs1, 2 * bs2)
        S = ShapeRectangle(center = (0.0, 0.0), box_size = rect_size)
        S = ShapeRoundAdiabaticSplineGeneric(original_shape = S,
                                             radii = [self.bend_radius, self.bend_radius, self.bend_radius, self.bend_radius],
                                             adiabatic_angles_list = [(self.adiabatic_angle_in_ring, self.adiabatic_angle_in_coupler),(self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_ring),
                                                                      (self.adiabatic_angle_in_ring, self.adiabatic_angle_in_coupler), (self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_ring)]
                                             )
        L = S.length()
        straight1 = 0.5*(self.length-L) - self.straight
        return (self.straight,straight1)
        
    def define_shape(self):
        (bs1,bs2) = self.get_bend90_size()
        rect_size = (2*bs1+self.straights[0], 2*bs2+self.straights[1])
        S = ShapeRectangle(center = (0.0, 0.0), box_size = rect_size)
        S = ShapeRoundAdiabaticSplineGeneric(original_shape = S,
                                             radii = [self.bend_radius, self.bend_radius, self.bend_radius, self.bend_radius],
                                             adiabatic_angles_list = [(self.adiabatic_angle_in_ring, self.adiabatic_angle_in_coupler),(self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_ring),
                                                                      (self.adiabatic_angle_in_ring, self.adiabatic_angle_in_coupler), (self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_ring)]
                                             )

        return S
    

class RingSplineNotchFilter(__RingStraightCouplers__, __RingCouplerTransformation1__, __RingWaveguideCouplers1__, RingAdiabaticSpline):
    """ spline ring filter with one straight access waveguide (notch filter) """
    __name_prefix__ = "RINGSPLINE_NOTCH"
     
class RingSpline180DropFilter(__RingStraightCouplers__, __Ring180CouplerTransformation2__, __RingWaveguideCouplers2__, RingAdiabaticSpline):
    """ spline ring filter with two straight access waveguide (drop filter) """
    __name_prefix__ = "RINGSPLINE_180DROP"

class RingSpline90DropFilter(__RingStraightCouplers__, __Ring90CouplerTransformation2__, __RingWaveguideCouplers2__, RingAdiabaticSpline):
    """ spline ring filter with two straight access waveguides under 90 degrees (drop filter) """
    __name_prefix__ = "RINGSPLINE_90DROP"
        
#FIXME: Make couplers with adiabatic splines as well
#class RingSplineSymmNotchFilter(__RingSymmCouplers__, __RingCouplerTransformation1__, __RingWaveguideCouplers1__, RingAdiabaticSpline):
    #""" spline ring filter with one access waveguide (notch filter) """
    #__name_prefix__ = "RINGSPLINESYMM_NOTCH"
            
#class RingSplineSymm180DropFilter(__RingSymmCouplers__, __Ring180CouplerTransformation2__,__RingWaveguideCouplers2__,  RingAdiabaticSpline):
    #""" spline ring filter with two access waveguides (drop filter) """
    #__name_prefix__ = "RINGSPLINESYMM_180DROP"

#class RingSplineSymm90DropFilter(__RingSymmCouplers__, __Ring90CouplerTransformation2__,__RingWaveguideCouplers2__,  RingAdiabaticSpline):
    #""" spline ring filter with two access waveguides (drop filter) """
    #__name_prefix__ = "RINGSPLINESYMM_90DROP"
    