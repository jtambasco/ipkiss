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

from ..filter import Filter
from ipcore.properties.predefined import IntProperty, RESTRICT_POSITIVE, RESTRICT_NONNEGATIVE
from ..elements.shape import Path
from ...geometry.shape import Shape
from ...geometry import shape_info
from ...geometry import shape_cut
from ipkiss.log import IPKISS_LOG as LOG


class ShapeCutFilter(Filter):
    grids_per_unit = IntProperty(default = 200, restriction = RESTRICT_POSITIVE)
    overlap = IntProperty(default = 1, restriction = RESTRICT_NONNEGATIVE)
    max_path_length = IntProperty(required = True, restriction = RESTRICT_POSITIVE)
    
    def __filter_Shape__(self, shape):
        coordinates = Shape(shape)
        coordinates.closed = False # this one is open, but the original one can be closed
        coordinates.remove_identicals()        
        if shape.closed:
            min_sections = 2
            if (coordinates[-1] == coordinates[0]):
                coordinates.append(coordinates[1]) # create overlap
            elif ((coordinates[-2] != coordinates[0]) or (coordinates[-1] != coordinates[1])):
                coordinates.append(coordinates[0]) # close
                coordinates.append(coordinates[1]) # create overlap
            coordinates.end_face_angle = 0.5 *(shape_info.angle_deg(coordinates[2], coordinates[1]) + shape_info.angle_deg(coordinates[1], coordinates[0]))
            coordinates.start_face_angle = 0.5 *(shape_info.angle_deg(coordinates[-2], coordinates[-3]) + shape_info.angle_deg(coordinates[-1], coordinates[-2]))
        elif coordinates[-1] == coordinates[0]:
            # not closed, but ends will overlap:
            min_sections = 2
        else:
            min_sections = 1
        
        shapes = shape_cut.cut_open_shape_in_sections_with_overlap (coordinates, self.max_path_length, self.overlap, min_sections)
        return shapes
        
    def __repr__(self):
        return "<ShapeCutFilter>"      
    
    
class PathCutFilter(ShapeCutFilter):
           
    def __filter_Path__(self, item):        
        if item.line_width != 0:
            shapes = ShapeCutFilter.__filter_Shape__(self, item.shape)
               
            if item.absolute_line_width:
                line_width = - item.line_width
            else:
                line_width = item.line_width * item.transformation.magnification
            
            return [Path(item.layer, sh, line_width, item.path_type, transformation = item.transformation) for sh in shapes]
        else:
            LOG.debug("Path linewidth is zero: PathCutFilter not applied.")
            return [item]
        
    def __repr__(self):
        return "<PathCutFilter>"        
