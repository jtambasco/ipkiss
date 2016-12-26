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
from .geometry import __Geometry2D__, __UniformEnvironmentGeometry__
from ..material.material import MaterialProperty, DEFAULT_MATERIAL

try:
    from dependencies.pil_wrapper.PIL import Image
except:
    raise AssertionError("PIL must be installed to use geometry.image")

class __ImageGeometry2D__(__Geometry2D__):
    center = Coord2Property(required = True)
    size = Size2Property(required = True)
    
    def size_info(self):
        return SizeInfo(west = self.center[0] - 0.5* self.size[0],
                        east = self.center[0] + 0.5* self.size[0],
                        south = self.center[1] - 0.5* self.size[1],
                        north = self.center[1] + 0.5* self.size[1])
    

class __ImageMaterialGeometry2D__(__ImageGeometry2D__):
    """ abstract 2DGeometry based on an image_map for the material """
    material_image = RestrictedProperty(required = True)
    material_grid = DefinitionProperty("define_material_grid")
    
    def define_material_grid(self):
        """ equivalent size of one image pixel """
        i = self.material_image
        return coord2(self.size[0]/i.size[0],self.size[1]/i.size[1])
    
    def get_material(self, coordinate):
        pixel_coord = (int(self.coordinate[0]/self.grid.x + 0.5), int(self.coordinate[1]/self.grid.y + 0.5))
        return color_to_material(self.image[pixel_coord[0]][pixel_coord[1]])    
    

class __ColormapImageMaterialGeometry2D__(__ImageMaterialGeometry2D__):
    """ 2DGeometry based on an image and a dict which matches a color to a given material"""
    color_map = RestrictedProperty(required = True)
    
    def color_to_material(self, color):
        return self.color_map(color)
    
class __GrayscaleImageMaterialGeometry2D__(__ImageMaterialGeometry2D__):
    material_white = MaterialProperty(default = DEFAULT_MATERIAL)
    material_black = MaterialProperty(default = DEFAULT_MATERIAL)

    def color_to_material(self, color):
        fraction = (color[1]/255.0)
        return BlendedMaterial(material_1 = self.material_white, material_2 = self.material_black, fraction = fraction)
    
    
class __LayerSuperpositionMaterialGeometry2D__(__ImageGeometry2D__):
    """2D Geometry where a superposition of layers determines the material. A map defines the material for each superposition of layers"""   
    layer_to_material_map = DictProperty(required = True) #key: set with layers / value : material
    layer_superposition_array = NumpyArrayProperty(required = True) #numpy array with in every point of the grid the list of layers at that point
    grid = FloatProperty(required = True)
    
    def __init__(self, **kwargs):        
        super(__LayerSuperpositionMaterialGeometry2D__, self).__init__(**kwargs)
        self.len_0 = self.layer_superposition_array.shape[0]
        self.len_1 = self.layer_superposition_array.shape[1]
        
    def __layers_to_material(self, layers):
        """ For a given combination of layers (list or tuple), return the corresponding material"""
        layers = LayerList(layers)
        try:
            mat = self.layer_to_material_map[layers]
        except KeyError:
            from ipkiss.exceptions.exc import IpkissException
            raise IpkissException("The following superposition of layers does not have a corresponding material : %s"%layers)
        return mat
        
    def get_material(self, coordinate):
        """ at a given coordinate, return the material """
        pixel_coord = (int(coordinate[0]/self.grid), int(coordinate[1]/self.grid))  
        try:
            layers_at_coordinate = self.layer_superposition_array[pixel_coord[0], pixel_coord[1]]
        except IndexError, e: #some engines will request the material 1 step over the border of the simulation volume
            if (pixel_coord[0] >= self.len_0):
                X = self.len_0 - 1
            else:
                X = pixel_coord[0]
            if (pixel_coord[1] >= self.len_1):
                Y = self.len_1 - 1
            else:
                Y = pixel_coord[1]                
            layers_at_coordinate = self.layer_superposition_array[X,Y]
        mat = self.__layers_to_material(layers_at_coordinate)
        return mat
    
    
    
    
class __ProcessSuperpositionMaterialGeometry2D__(__ImageGeometry2D__):
    """2D Geometry where a superposition of processes determines the material. 
    The process flag dictionnary contains an array for every process, which indicates if the process is used at the particular point or not"""   
    process_to_material_map = DictProperty(required = True) #key: set with processes / value : material
    process_flags = DictProperty(required = True) #key : process / value : numpy array with True/False flag at every point
    grid = FloatProperty(required = True)
    
    def __init__(self, **kwargs):        
        super(__ProcessSuperpositionMaterialGeometry2D__, self).__init__(**kwargs)
        self.processes = self.process_flags.keys()
        self.processes.sort()
        self.len_0 = self.process_flags[self.processes[0]].shape[0]
        self.len_1 = self.process_flags[self.processes[0]].shape[1]
        
    def __processes_to_material(self, processes):
        """ For a given combination of processes (list or tuple), return the corresponding material"""
        p = tuple(processes)
        try:
            mat = self.process_to_material_map[p]
        except KeyError:
            from ipkiss.exceptions.exc import IpkissException
            raise IpkissException("The following superposition of prcoesses does not have a corresponding material : %s"%p)
        return mat
    
    def __processes_at_coordinate(self, coord):
        processes_at_coordinate = []
        for process in self.processes:
            process_active_at_coord = self.process_flags[process][coord[0], coord[1]]
            if process_active_at_coord:
                processes_at_coordinate.append(process)        
        return processes_at_coordinate
        
    def get_material(self, coordinate):
        """ at a given coordinate, return the material """
        pixel_coord = (int(coordinate[0]/self.grid), int(coordinate[1]/self.grid))  
        try:
            processes_at_coordinate = self.__processes_at_coordinate(pixel_coord)                    
        except IndexError, e: #some engines will request the material 1 step over the border of the simulation volume
            if (pixel_coord[0] >= self.len_0):
                X = self.len_0 - 1
            else:
                X = pixel_coord[0]
            if (pixel_coord[1] >= self.len_1):
                Y = self.len_1 - 1
            else:
                Y = pixel_coord[1]                
            processes_at_coordinate = self.__processes_at_coordinate(Coord2(X,Y))                    
        mat = self.__processes_to_material(processes_at_coordinate)
        return mat
        
    
                
            
        
    
    
 