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

from .. import constants
from ..primitives.shapes_to_elements import str_shapes_boundaries, str_shapes_paths
from ..geometry.shapes.modifiers import ShapeStub
from ..geometry.shape_modify import shapes_fit
from ..geometry.shape import Shape
from ..primitives.layer import Layer
__all__ = ["hpgl_to_structure", "hpgl_to_shapes"]


def hpgl_get_shapes(f):
    ret_shapes = []
    shape = Shape()
    s = " "
    pu = False
    while not s == "":
        s = f.readline()
        if s.startswith("PU"):
            if pu and len(shape) > 1:
                ret_shapes.append(shape)
            t = s.replace('PU','').replace(';','')
            t = t.split()
            shape = [(float(t[0]), float(t[1]))]
            pu = True                
        elif s.startswith('PD') and pu:
            t = s.replace('PD','').replace(';','')
            t = t.split()
            shape.append((float(t[0]),float(t[1])))
        else:
            if pu and len(shape) > 1:
                ret_shapes.append(shape)
            pu = False
    return ret_shapes
    
def hpgl_get_next_shape(f):
    ret_shape = Shape()
    s = ' '
    while not s.startswith('PU') and not s=='':
        s = f.readline()
    if s == '':
        return ret_shape
    
    t = s.replace('PU','').replace(';','')
    t = t.split()
    ret_shape.append((float(t[0]),float(t[1])))
    
    s = f.readline()
    while s.startswith('PD'):
        t = s.replace('PD','').replace(';','')
        t = t.split()
        ret_shape.append((float(t[0]),float(t[1])))
        s = f.readline()
    return ret_shape        
    


def hpgl_to_shapes (filename):
    ret_shapes = []
    f = open(filename,'r')
    ret_shapes = hpgl_get_shapes(f)
##    s = hpgl_get_next_shape(f)
##    while s != []:
##        ret_shapes.append(s)
##        s = hpgl_get_next_shape(f)
    f.close()
    return ret_shapes


def hpgl_to_structure (name, filename, layer = Layer(0), size = (50.0, 50.0), alignment= (constants.TEXT_ALIGN_CENTER, constants.TEXT_ALIGN_TOP), line_width = 0.0, stub = 0.0):
    if alignment[0] == constants.TEXT_ALIGN_RIGHT:
        xpos = - size[0]
    elif alignment[0] == constants.TEXT_ALIGN_CENTER:
        xpos = - size[0]/2.0
    else:
        xpos = 0.0

    if alignment[1] == constants.TEXT_ALIGN_BOTTOM:
        ypos = 0.0
    elif alignment[1] == constants.TEXT_ALIGN_MIDDLE:
        ypos = - size[1]/2.0
    else:
        ypos = -size[1]

    south_west = (xpos, ypos)
    north_east = (xpos + size[0], ypos + size[1])
    
    shapes = hpgl_to_shapes(filename)
    if len(shapes) > 0:
        shapes = shapes_fit(shapes, south_west, north_east)

    if stub > 0.0:
        final_shapes = []
        for s in shapes:
            final_shapes.append(ShapeStub(original_shape = s, stub_width = stub, only_sharp_angles = True))
    else:
        final_shapes = shapes

    if line_width == 0.0 :
        return str_shapes_boundaries(name, layer, final_shapes)
    else:
        return str_shapes_paths(name, layer, final_shapes, line_width)

def hpgl_to_python_coords (name, filename, file_out, size = (50.0,50.0), alignment= (constants.TEXT_ALIGN_CENTER, constants.TEXT_ALIGN_TOP), stub = 0.0):
    ret_str = ''
    if alignment[0] == constants.TEXT_ALIGN_RIGHT:
        xpos = - size[0]
    elif alignment[0] == constants.TEXT_ALIGN_CENTER:
        xpos = - size[0]/2.0
    else:
        xpos = 0.0

    if alignment[0] == constants.TEXT_ALIGN_BOTTOM:
        ypos = 0.0
    elif alignment[1] == constants.TEXT_ALIGN_MIDDLE:
        ypos = - size[1]/2.0
    else:
        ypos = -size[1]

    south_west = (xpos, ypos)
    north_east = (xpos + size[0], ypos + size[1])
    
    shapes = hpgl_to_shapes(filename, stub)
    if len(shapes) > 0:
        shapes = shapes_fit(shapes, south_west, north_east)

    ret_str = str(shapes)
    
