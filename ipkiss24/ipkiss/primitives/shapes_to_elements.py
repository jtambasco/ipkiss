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

from .elements.shape import Path, Boundary
from .elements.basic import ElementList
from .structure import Structure
from .. import constants

#Multiple shapes to polygons

__all__ = ["str_shapes_boundaries",
           "str_shapes_paths",
           "el_shapes_boundaries",
           "el_shapes_paths"]

def str_shapes_boundaries(name, layer, shapes):
    """Convert a list of shapes into a structure with Boundary elements on the specified layer"""
    return Structure(name, elements = el_shapes_boundaries(layer, shapes))

def str_shapes_paths(name, layer, shapes, line_width = 1.0, path_type = constants.PATH_TYPE_NORMAL):
    """Convert a list of shapes into a structure with Path elements on the specified layer"""
    return Structure(name, elements = el_shapes_paths(layer, shapes, line_width, path_type))
        
def el_shapes_boundaries(layer, shapes):
    """Converts a list of shapes into a list of Boundary elements on the specified layer"""
    ret_el = ElementList()
    for s in shapes:
            ret_el.append(Boundary(layer = layer, shape = s))
    return ret_el

def el_shapes_paths(layer, shapes, line_width = 0.0, path_type = constants.PATH_TYPE_NORMAL):
    """Converts a list of shapes into a list of Path elements on the specified layer"""    
    ret_el = ElementList()
    for s in shapes:
            ret_el.append(Path(layer=layer, shape = s, line_width = line_width, path_type = path_type))
    return ret_el
        