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

import numpy
from ipkiss.geometry.shape import Shape

class Scaler(object):
    def __init__(self, box, canvas_size):
        self.box = box
        self.canvas_size = canvas_size        
        self.scale = float(self.canvas_size[0]) / float(self.box[1] - self.box[0])
        self.box_center = (0.5 * box[0] + 0.5 * box[1], 0.5 * box[2]  + 0.5 * box[3])
        self.box_south_west = (self.box[0],self.box[2]) 
        self.origin_offset = self.__calculate_origin_offset()
        
    def __get_scaled_points(self, shape):
        sp = (shape.points - [self.origin_offset[0], self.origin_offset[1]] - [self.box_south_west[0], self.box_south_west[1]]) * self.scale
        return sp
    
    def __calculate_origin_offset(self):
        scaled_origin = (numpy.array([0.0, 0.0]) - [self.box_south_west[0], self.box_south_west[1]]) * self.scale
        origin_offset = (scaled_origin - [int(scaled_origin[0]), int(scaled_origin[1])]) / self.scale
        return origin_offset    
    
    def map_shape(self, shape):
        return Shape(numpy.asarray(self.__get_scaled_points(shape) , dtype = numpy.integer))
    
    def map_shape_to_list(self, shape):
        return list(numpy.asarray(numpy.reshape(self.__get_scaled_points(shape) , numpy.size(shape.points)), dtype=numpy.integer))

    def map_coordinate(self, coordinate):  
        s = Shape(points = [coordinate])
        return self.__get_scaled_points(s)
        
    def map_length(self, length):
        return length * self.scale
