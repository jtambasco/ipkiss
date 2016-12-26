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

from ..basic import FiberCouplerGratingAuto
from ipkiss.all import *

##############################################################
## Curved gratings: basic classes
##############################################################
__all__ = []

class __CurveDimensionBase__(Group):
    process = ProcessProperty(default = TECH.PROCESS.FC)
    purpose = PurposeProperty(default = TECH.PURPOSE.DF.TRENCH)
    

class CurveDimension(__CurveDimensionBase__):
    center = Coord2Property(required = True)
    ellipse_r_h = PositiveNumberProperty(required = True)
    ellipse_r_v = PositiveNumberProperty(required= True)
    angle = AngleProperty(required = True)
    line_width = PositiveNumberProperty(required= True)

    def __init__(self, center, ellipse_r_h, ellipse_r_v, angle, line_width, purpose = TECH.PURPOSE.DF.TRENCH, **kwargs):
        super(CurveDimension, self).__init__(center = center,
                                              ellipse_r_h = ellipse_r_h,
                                              ellipse_r_v = ellipse_r_v,
                                              angle = angle,
                                              line_width = line_width,
                                              purpose = purpose,
                                              **kwargs)

    def define_elements(self, elems):
        S = ShapeEllipseArc(center = (self.center[0], self.center[1]), 
                            box_size = (2*self.ellipse_r_h, 2*self.ellipse_r_v), 
                              start_angle = 180.0 - 0.5*self.angle, end_angle = 180.0 + 0.5*self.angle)

        elems += Boundary(PPLayer(self.process, self.purpose), 
                            #ShapePath(original_shape = S, path_width = self.line_width))
                            ShapePathSpike(original_shape = S, path_width = self.line_width, spike_angle = 120.0))
        return elems
    
            
            
class CurvedGrating(Structure):
    __name_prefix__  = "CG"
    curve_dimensions = RestrictedProperty(restriction = RestrictTypeList(__CurveDimensionBase__), required = True)
    process = ProcessProperty(default = TECH.PROCESS.FC)
    
    def __init__(self, curve_dimensions = [], process = TECH.PROCESS.FC, **kwargs): #FIXME - why can't we remove this? parameter curve_dimensions seems to give a problem
        super(CurvedGrating, self).__init__(curve_dimensions = curve_dimensions,
                                            process = process,
                                             **kwargs)
        
    def define_elements(self, elems):
        for cd in self.curve_dimensions:
            elems += cd
        return elems





