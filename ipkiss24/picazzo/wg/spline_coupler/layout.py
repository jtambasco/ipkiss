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

from ipcore.properties.predefined import NonNegativeNumberProperty, RestrictedProperty, restrictions
from ipkiss.all import Shape, VMirror, PPLayer, Boundary, Rectangle
from ipkiss.plugins.photonics.wg.connect import WaveguidePointRoundedConnectElementDefinition, __RoundedWaveguide__
from ipkiss.geometry.shapes.spline import ShapeRoundAdiabaticSpline, SplineRoundingAlgorithm, ShapeRoundAdiabaticSplineGeneric
from picazzo.wg.coupler.layout import __DirectionalCoupler__
from ipkiss.technology import get_technology
import functools

TECH = get_technology()

def PartialProperty(internal_member_name= None, restriction = None,**kwargs):    
    R = restrictions.RestrictType(functools.partial) & restriction
    P = RestrictedProperty(internal_member_name, restriction = R,**kwargs)   
    P.__get_default__ = lambda : P.default
    return P

class SplineDirectionalCoupler(__RoundedWaveguide__, __DirectionalCoupler__):
    __name_prefix__ = "SplineDircoup_"
    rounding_algorithm = PartialProperty() # FIXME: Rounding algorithms should be callables that are instances of rounding algorithm classes
    adiabatic_angle_in_coupler = NonNegativeNumberProperty(default=10.0)
    adiabatic_angle_in_access = NonNegativeNumberProperty(default=10.0)
    
    def define_rounding_algorithm(self):
        return SplineRoundingAlgorithm(adiabatic_angles = (self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_access))
    
    def get_bend90_size(self):
        B = self.rounding_algorithm(original_shape = [(-100* self.bend_radius, 0.0), (0.0, 0.0), (0.0, 100*self.bend_radius)], 
                                    radius = self.bend_radius)
        bend_size = B[1:-1].size_info.size
        return (bend_size[0]+0.01, bend_size[1]+0.01)

    def define_elements(self, elems):
        super(SplineDirectionalCoupler,self).define_elements(elems)
        SI = elems.size_info()
        elems += Rectangle(layer = PPLayer(self.wg_definition1.process,TECH.PURPOSE.LF_AREA),
                           center = SI.center, box_size = (SI.width, SI.height))
        return elems
    
    def define_waveguides(self):
        (bs1,bs2) = self.get_bend90_size()
        rect_size = (bs1+self.length, bs2)
        S = Shape([(-bs1-0.5*self.length,-bs2),(-bs1-0.5*self.length,0.0),(-0.5*self.length,0.0),
                   (0.5*self.length,0.0),(bs1+0.5*self.length,0.0),(bs1+0.5*self.length,-bs2)])
        S = ShapeRoundAdiabaticSplineGeneric(original_shape = S,
                                             radii = [self.bend_radius for i in range(len(S))],
                                             adiabatic_angles_list = [(self.adiabatic_angle_in_access, self.adiabatic_angle_in_access),
                                                                      (self.adiabatic_angle_in_access, self.adiabatic_angle_in_coupler),
                                                                      (self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_coupler),
                                                                      (self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_coupler),
                                                                      (self.adiabatic_angle_in_coupler, self.adiabatic_angle_in_access),
                                                                      (self.adiabatic_angle_in_access, self.adiabatic_angle_in_access)]
                                             )
        S.move((0.0,-0.5*self.spacing))
        S2 = S.transform_copy(VMirror())
        waveguides = [self.wg_definition1(shape = S),
                      self.wg_definition2(shape = S2)
                      ]
        return waveguides