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



from picazzo.wg.aperture.layout import __WgAperture__
from ipkiss.plugins.photonics.port.port import  InOpticalPort, OutOpticalPort
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.wg import WgElDefinition
from picazzo.wg.aperture import ApertureProperty
from ipkiss.all import *


__all__ = ["StarCoupler"] 
           

class StarCouplerBase(Structure):
    """ Abstract base class for star couplers """
    __name_prefix__ = "STAR"
    transformation_in = TransformationProperty(default = None)
    transformation_out = TransformationProperty(default = None)

    def define_elements(self, elems):
        if not self.aperture_in is None:
            E= SRef(self.aperture_in, (0.0, 0.0), self.transformation_in)
            if self.transformation_in is None or self.transformation_in.is_orthogonal():
                elems += E
            else:
                elems += E.flat_copy()            
        if not self.aperture_out is None:
            E= SRef(self.aperture_out, (0.0, 0.0), self.transformation_out)        
            if self.transformation_out is None or self.transformation_out.is_orthogonal():
                elems += E
            else:
                elems += E.flat_copy()                
        return elems

    def define_ports(self, P):
        if not self.aperture_in is None:
            for p in self.aperture_in.ports.transform_copy(self.transformation_in):
                P += InOpticalPort(position = p.position, angle = p.angle_deg, wg_definition = p.wg_definition)
        if not self.aperture_out is None:
            for p in self.aperture_out.ports.transform_copy(self.transformation_out):
                P += OutOpticalPort(position = p.position, angle = p.angle_deg, wg_definition = p.wg_definition)
        return P


class __StarCouplerHull__(object):
    process = ProcessProperty(default = TECH.PROCESS.WG)
    hull_extension = NonNegativeNumberProperty(default = 0.0)
    hull_growth = NonNegativeNumberProperty(default = TECH.WG.SPACING)
    
    # Cache this!
    def get_hull_shape(self):
        if self.aperture_in is None or self.aperture_out is None: return
        
        hull_shape1 = self.aperture_in.convex_hull().transform(self.transformation_in)
        hull_shape2 = self.aperture_out.convex_hull().transform(self.transformation_out)

        hull_center1 = hull_shape1.size_info.center
        hull_center2 = hull_shape2.size_info.center

        line_through_centers = straight_line_from_two_points(hull_center1, hull_center2)
        d1_1 = 0.0
        # find closest point on one side of hull 1
        for p in hull_shape1:
            d =line_through_centers.distance(p)
            if d > d1_1:
                d1_1 = d
                p1_1 = p
 
        # find closest point on other side of hull 1
        d1_2 = 0.0
        for p in hull_shape1:
            d =line_through_centers.distance(p)
            if d > d1_2 and not line_through_centers.is_on_same_side(p, p1_1):
                d1_2 = d
                p1_2 = p
                
        d2_1 = 0.0
        # find closest point on one side of hull 2
        for p in hull_shape2:
            d =line_through_centers.distance(p)
            if d > d2_1:
                d2_1 = d
                p2_1 = p
 
        # find closest point on other side of hull 2
        d2_2 = 0.0
        for p in hull_shape2:
            d =line_through_centers.distance(p)
            if d > d2_2 and not line_through_centers.is_on_same_side(p, p2_1):
                d2_2 = d
                p2_2 = p

        d_max = max(d1_1, d1_2, d2_1, d2_2)
        
        a = line_through_centers.angle_deg
        extra_points = Shape([p1_1.move_polar_copy(d_max-d1_1+self.hull_extension, a+90.0),
                                  p1_1.move_polar_copy(d_max-d1_1+self.hull_extension, a-90.0),
                                  p1_2.move_polar_copy(d_max-d1_2+self.hull_extension, a+90.0),
                                  p1_2.move_polar_copy(d_max-d1_2+self.hull_extension, a-90.0),
                                  p2_1.move_polar_copy(d_max-d2_1+self.hull_extension, a+90.0),
                                  p2_1.move_polar_copy(d_max-d2_1+self.hull_extension, a-90.0),
                                  p2_2.move_polar_copy(d_max-d2_2+self.hull_extension, a+90.0),
                                  p2_2.move_polar_copy(d_max-d2_2+self.hull_extension, a-90.0)
                                  ])
            
        hull = (hull_shape1+hull_shape2+extra_points).convex_hull()
        hull = ShapeStub(original_shape = ShapeGrow(original_shape = hull, amount = self.hull_growth), 
                              stub_width = TECH.TECH.MINIMUM_LINE)
        return hull
    
    def define_elements(self, elems):
        hull = self.get_hull_shape()
        elems += Boundary(PPLayer(self.process, TECH.PURPOSE.DF_AREA), hull)
        elems += Boundary(PPLayer(TECH.PROCESS.NONE, TECH.PURPOSE.NO_FILL), hull)
        super(__StarCouplerHull__, self).define_elements(elems)
        return elems
    
    
        
class StarCoupler(__StarCouplerHull__, StarCouplerBase):
    """ Most generic star coupler component. It takes 2 apertures (can be multi_apertures) """
    __name_prefix__ = "STAR"
    aperture_in = ApertureProperty(allow_none= True)
    aperture_out = ApertureProperty(allow_none= True)
    
    #def __init__(self, aperture_in, aperture_out, transformation_in = None, transformation_out = None, library=None, **kwargs):
        #super(StarCoupler, self).__init__(
            #aperture_in = aperture_in,
            #aperture_out = aperture_out,
            #transformation_in = transformation_in,
            #transformation_out = transformation_out,
            #**kwargs)
        
        
