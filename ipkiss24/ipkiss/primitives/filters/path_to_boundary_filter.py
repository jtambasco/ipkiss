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
from ..elements.shape import Boundary
from ...geometry.shapes.modifiers import ShapePath
from ipkiss.log import IPKISS_LOG as LOG


class PathToBoundaryFilter(Filter):
    
    def __filter_Path__(self, item):
        if item.line_width != 0:
            LOG.debug("Converting path %s into boundary." %item)
            resultBoundary = Boundary(item.layer, ShapePath(original_shape = item.shape, 
                                                            path_width = abs(item.line_width) , 
                                                            path_type = item.path_type), transformation = item.transformation)            
            resultBoundaryList = [resultBoundary]
            LOG.debug("Result has %i points" %len(resultBoundary.shape.points))
            return resultBoundaryList
        else:
            LOG.debug("Path linewidth is zero: PathToBoundaryFilter not applied.")
            return [item]

    def __repr__(self):
        return "<PathToBoundaryFilter>"                