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

from picazzo.wg.aperture import *
from ipkiss.process.layer import PurposeProperty, ProcessProperty
from ..basic import FiberCouplerGratingAuto
from ipkiss.all import *

#################################################################
## Segmented gratings: basic classes
#################################################################

class SegmentTrench(StrongPropertyInitializer):
    y_offset = NumberProperty(required = True)
    x_offset = NumberProperty(required = True)
    length = PositiveNumberProperty(required = True)
    line_width = PositiveNumberProperty(required = True)
    

class Segmentation(Group):
    center_position = Coord2Property(default = (0.0, 0.0))
    trench_list = RestrictedProperty(restriction = RestrictTypeList(SegmentTrench), required = True)
    process = ProcessProperty(default = TECH.PROCESS.FC)
    purpose = PurposeProperty(default = TECH.PURPOSE.DF.TRENCH)
       
    def define_elements(self, elems):
        for t in self.trench_list:
            elems += Rectangle(PPLayer(self.process, self.purpose), 
                            (self.center[0]+t.x_offset, self.center[1] + t.y_offset), 
                            (t.line_width, t.length)
                        )
        return elems

class SegmentedFiberCoupler(FiberCouplerGratingAuto):            
    
    def __get_grating__(self):
        return (Structure(name = self.name, elements = self.segmentations), None)

##################################################################################
## Predefined types
##################################################################################

# equal segmentation
def equal_segmented_trench(total_length, n_o_segments, fill_factor, trench_width):
    tl = []
    if fill_factor == 0.0:
        return tl
    elif fill_factor == 1.0:
        return [SegmentTrench(0.0, 0.0, total_length, trench_width)]
    else:
        segment_length = total_length / n_o_segments
        for i in range(n_o_segments):
            tl.append(SegmentTrench(0.0, -0.5*total_length + (i + 0.5) * segment_length, segment_length * fill_factor, trench_width))
    return tl

def equal_segmentation(center, total_length, n_o_segments, fill_factor, trench_width):
    tl = equal_segmented_trench(total_length, n_o_segments, fill_factor, trench_width)
    return segmentation(center, tl)


def equal_segmented_trench_grating(name, period, fill_factors, n_o_segments, grating_width, line_width):
    n_o_periods = len(fill_factors)
    c_x = 0.5 * n_o_periods * period
    segmentations = []
    for i in range(n_o_periods):
        segmentations.append(equal_segmentation((0.0 - c_x + i * period, 0.0),grating_width, n_o_segments, fill_factors[i], line_width))
    return segmented_trench_grating(name, segmentations)
