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
from ipkiss.all import *
from .geometry import *
from pysics.basics.environment import *
from ipkiss.visualisation.display_style import *
from ipkiss.visualisation.color import *
from pysics.optics import *
from pysics.basics.material.material import Material
from pysics.materials.electromagnetics import *
from ipkiss.technology import get_technology
from ipkiss.primitives.elements.shape import __ShapeElement__
from ipkiss.primitives.elements.basic import __LayerElement__
from ipkiss.exceptions.exc import IpkissException
from ipkiss.primitives.filters.path_to_boundary_filter import PathToBoundaryFilter
from ipkiss.primitives.filters.path_cut_filter import PathCutFilter
from ipkiss.primitives.structure import StructureProperty
from ipkiss.primitives.layer import __GeneratedLayerAnd__, __GeneratedLayerNot__, __GeneratedLayerOr__, __GeneratedLayerXor__, __GeneratedLayer_2Layer__, __GeneratedLayer__
from ipkiss import constants
import logging
import copy
from dependencies.matplotlib_wrapper import *
from dependencies.shapely_wrapper import TopologicalError

all = ["virtual_fabrication"]

TECH = get_technology()

class __VirtualFabrication__(StrongPropertyInitializer):
    pass

class VirtualFabrication(__VirtualFabrication__):  
    geometry = DefinitionProperty(fdef_name = "define_geometry")
    structure = StructureProperty(required = True)
    include_growth = FloatProperty(default = 0.0)
    environment = EnvironmentProperty(default = DEFAULT_ENVIRONMENT)
    grid = FloatProperty(default = 0.05)

    def __collect_metrics__(self):
        #component_size_info = the size of the original component, without the growth
        component_size_info = self.structure.size_info()
        #size_info = the size of the total canvas, including growth
        size_info = copy.deepcopy(component_size_info)
        size_info.grow_absolute(self.include_growth)
        #canvas_size = the number of points in the complete grid (=the grid of the bounding box, including the growth)
        canvas_size = (int(numpy.ceil(size_info.width / self.grid)),
                       int(numpy.ceil(size_info.height / self.grid)))        
        #component_canvas_size = the number of points in the grid covering the component (without the growth)
        component_canvas_size = (int(numpy.ceil(component_size_info.width / self.grid)),
                                 int(numpy.ceil(component_size_info.height / self.grid)))    
        LOG.debug("Component width: %s and height: %s" %(str(component_size_info.width),str(component_size_info.height)))
        LOG.debug("Total canvas size : %s" %str(canvas_size))
        LOG.debug("Total canvas size info : %s" %str(size_info))
        LOG.debug("Component canvas size : %s" %str(component_canvas_size))
        LOG.debug("Component size info: %s" %str(component_size_info))
        return (canvas_size, size_info, component_canvas_size, component_size_info)

    def extend_component_at_ports(self):
        if (self.include_growth > 0.0):
            component_size_info = self.structure.size_info()    
            l = component_size_info.width + component_size_info.height + 2*self.include_growth
            new_elements = ElementList(self.structure.elements)
            for p in self.structure.ports:
                wg_shape = Shape(points = [p.position, p.position.move_polar_copy(l, p.angle_deg)])
                wg_elem = p.wg_definition(shape = wg_shape)
                new_elements.append(wg_elem)
            self.structure = Structure(name = self.structure.name+"_EXT"+str(self.include_growth),
                                       elements = new_elements,
                                       ports = self.structure.ports)        

    def define_geometry(self):
        raise NotImplementedException("define_geometry not implemented in abstract class VirtualFabrication")

# ----------------------------------------------------------------------------------------- 


def __common_function_apply_polygon_to_array_memory_sparing__(array, polygon_points, do_bitwise_or = True, value = None):
    if (do_bitwise_or) and (value is not None):
        raise Exception("Invalid parameters : if do_bitwise_or==True, then value should be None")
    if (not do_bitwise_or) and (value is None):
        raise Exception("Invalid parameters : if do_bitwise_or==False, then value should not be None")
    #calculate for which range in the array we have to calculate the overlap with this polygon
    min_x = max(0,numpy.min([p[0] for p in polygon_points])-1)
    max_x = min(array.shape[0],numpy.max([p[0] for p in polygon_points])+1)
    min_y = max(0,numpy.min([p[1] for p in polygon_points])-1)
    max_y = min(array.shape[1],numpy.max([p[1] for p in polygon_points])+1)
    #the range that requires overlap will be plit up in slices (so as to limit memory consumption) - only needed for large polygons spanning over huge canvas
    SLICE_X_SIZE = 10000.0
    SLICE_Y_SIZE = 10000.0
    slices_x = numpy.arange(0, numpy.ceil((max_x - min_x) / SLICE_X_SIZE)) 
    slices_y = numpy.arange(0, numpy.ceil((max_y - min_y) / SLICE_Y_SIZE)) 
    #now iterate over all the slices 
    for slice_x in slices_x:
        for slice_y in slices_y:
            from_x = numpy.floor(slice_x * SLICE_X_SIZE + min_x)
            to_x = numpy.ceil(min((slice_x + 1) * SLICE_X_SIZE + min_x, max_x))
            from_y = numpy.floor(slice_y * SLICE_Y_SIZE + min_y)
            to_y = numpy.ceil(min((slice_y + 1) * SLICE_Y_SIZE + min_y, max_y))
            x_range = numpy.arange(from_x, to_x, dtype = numpy.int16) 
            y_range = numpy.arange(from_y, to_y, dtype = numpy.int16) 
            #calculate which canvas points correspond to this slice
            x_range_corrected = x_range + 0.5
            y_range_corrected = y_range + 0.5
            canvas_points = __common_function_cartesian__((x_range_corrected, y_range_corrected))
            #calculate the overlap between canvas points and polygon : which canvas point are inside the polygon?
            points_inside_polygon_flag = nxutils.points_inside_poly(canvas_points, polygon_points)
            #reshape the array with the flags
            target_shape = (to_x - from_x, to_y - from_y)
            points_inside_polygon_flag = points_inside_polygon_flag.reshape(target_shape)
            if (do_bitwise_or):
                #apply the true/false flag to the array
                array[from_x:to_x, from_y:to_y] = numpy.bitwise_or(array[from_x:to_x, from_y:to_y], points_inside_polygon_flag)	
            else:
                array[from_x:to_x, from_y:to_y] = numpy.where(points_inside_polygon_flag == True, value, array[from_x:to_x, from_y:to_y])
            percent_done = int(float(slice_x * len(slices_y) + slice_y) * 100.0 / (len(slices_x) * len(slices_y)))
            if percent_done < 100:
                LOG.debug("%i percent done..." % percent_done)


def __common_function_cartesian__(arrays, out=None):
    """cartesian product of Numpy arrays."""
    dtype = arrays[0].dtype    
    n = numpy.prod([x.size for x in arrays])
    if out is None:
        out = numpy.zeros([n, len(arrays)], dtype=dtype)    
    m = n / arrays[0].size
    out[:,0] = numpy.repeat(arrays[0], m)
    if arrays[1:]:
        __common_function_cartesian__(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out	    


from dependencies.shapely_wrapper import ShapelyPolygonCollection
from dependencies.shapely_wrapper import Polygon as ShapelyPolygon


class LayerShapelyPolygons(ShapelyPolygonCollection):
    """Associate a collection of shapely polygons with a layer"""
    layer = LayerProperty(required = True, doc="The layer associated with these Shapely polygons")
    size_info = SizeInfoProperty(required = True, doc="The sizeinfo including the growth")
    shape = FunctionNameProperty(fget_name = "get_shape")
    canvas_polygon = DefinitionProperty(fdef_name="define_canvas_polygon")

    def get_shape(self):
        return (self.size_info.width, self.size_info.height)

    def add_element(self, e):
        if not isinstance(e, __ShapeElement__):	    
            raise IpkissException("Wrong parameter. Expected object of type __ShapeElement__")        
        if (isinstance(e, Path)):        
            grid = TECH.METRICS.GRID 
            filter = PathCutFilter(max_path_length = int(constants.GDSII_MAX_COORDINATES/2) , grids_per_unit = int(1.0 / grid), overlap = 1)            
            filter += PathToBoundaryFilter()
            elems = filter(e)
            for e2 in elems:
                if not isinstance(e2, __LayerElement__):
                    continue
                self.add_element(e2)
        else:         
            shape = Shape(e.shape).transform(e.transformation) 
            self.add_shape(shape)


    def fabricate_offspring(self, georep): 
        return LayerShapelyPolygons(layer = self.layer,
                                    size_info = self.size_info, 
                                    georep = georep)		

    def add_shape(self, shape):
        pts = [(p[0],p[1]) for p in shape.points]
        self.add_polygon_points(pts)

    def define_canvas_polygon(self):
        nw = self.size_info.north_west
        ne = self.size_info.north_east
        se = self.size_info.south_east
        sw = self.size_info.south_west	
        shape = Shape(points = [nw,ne,se,sw,nw])
        shape.closed = True
        pts = [(p[0],p[1]) for p in shape.points]	
        p = ShapelyPolygon(pts)
        return p	

    def to_numpy_array(self, grid = TECH.METRICS.GRID):
        resolution = int(1.0 / TECH.METRICS.GRID)
        bitmap = numpy.zeros([self.shape[0] * resolution,
                              self.shape[1] * resolution], dtype = bool)		
        if (not self.is_empty()):
            mp = self.georep
            for g in mp.geoms:
                polygon_points = list(g.boundary.coords)		    
                self.__common_function_apply_polygon_to_array_memory_sparing__(bitmap, polygon_points)	  
        return bitmap

    def __cartesian__(self, arrays, out=None):
        return __common_function_cartesian__(arrays, out)	


# -------------------------------------------------------------------------------------------	  

from .process_flow import VFabricationProcessFlowProperty
from pysics.basics.material.material_stack import MaterialStackFactory

class VirtualFabricationProcessSuperposition2DMaterialStackPolygonsOnly(VirtualFabrication):
    save_debug_images = BoolProperty(default = False)
    process_flow = VFabricationProcessFlowProperty(required = True, doc="Process flow to use during the virtual fabrication.")
    material_stack_factory = RestrictedProperty(required = True, restriction = RestrictType(MaterialStackFactory))


    def __collect_metrics__(self):
        #component_size_info = the size of the original component, without the growth
        component_size_info = self.structure.size_info()
        #size_info = the size of the total canvas, including growth
        size_info = copy.deepcopy(component_size_info)
        size_info.grow_absolute(self.include_growth)
        LOG.debug("Component width: %s and height: %s" %(str(component_size_info.width),str(component_size_info.height)))
        LOG.debug("Total canvas size info : %s" %str(size_info))
        LOG.debug("Component size info: %s" %str(component_size_info))
        return (size_info, component_size_info)    

    def __make_process_polygons__(self):     
        from ipkiss.boolean_ops.boolean_ops_elements import __get_composite_shapely_polygon_for_elements_on_generated_layer__

        process_polygons = dict()
        (size_info, component_size_info) = self.__collect_metrics__()    
        self.extend_component_at_ports() 

        for process in self.process_flow.active_processes:	    
            if hasattr(TECH.PPLAYER,process.extension) and hasattr(TECH.PPLAYER.__getattribute__(process.extension),"ALL"):
                shapely_geom = __get_composite_shapely_polygon_for_elements_on_generated_layer__(elements = self.structure.elements, 
                                                                                                 generated_layer = TECH.PPLAYER.__getattribute__(process.extension).ALL)
                bm = LayerShapelyPolygons(layer = Layer(number = 0, name = "VFABRICATION_%s" %process.extension), size_info = size_info)	 	    
                bm.georep = shapely_geom
                process_polygons[process] = bm	    

        for process in self.process_flow.active_processes:
            if process not in process_polygons:
                process_polygons[process] = LayerShapelyPolygons(layer = Layer(number = 0, name = "VFABRICATION_%s" %process.extension),
                                                                 size_info = size_info)

        for process, is_lf_fabrication in self.process_flow.is_lf_fabrication.items(): 
            bm = process_polygons[process]
            if is_lf_fabrication:
                process_polygons[process] = bm.bitwise_not()

        if self.save_debug_images:
            for process, bm in process_polygons.items():
                bm.save_to_image("vfabrication_%s_process_polygon_%s.png" %(self.structure.name,process.extension))

        return (process_polygons, size_info)

    def validate_properties(self):
        if set(self.process_flow.is_lf_fabrication.keys()) != set(self.process_flow.active_processes):
            raise Exception("Invalid value for property is_lf_fabrication : every process in property 'all_processes' should have a corresponding entry in property 'is_lf_fabrication' and vice versa.")
        return True

    def define_geometry(self):   
        #STEP 1 : per process in 'self.process_flow.active_processes', generate a Shapely polygon indicating the area where this process will be physically applied
        (process_polygons, size_info) = self.__make_process_polygons__()
        #STEP 2 : resolve the superposition of processes and generate a geometrical description based on material stacks
        g = ProcessSuperpositionVirtualFabrication2DGeometryPolygons(material_stack_factory = self.material_stack_factory,
                                                                     processes = self.process_flow.active_processes,
                                                                     mapping_definition = self.process_flow.process_to_material_stack_map, 
                                                                     process_polygons = process_polygons, 
                                                                     size_info = size_info, 
                                                                     grid = self.grid,
                                                                     save_debug_images = self.save_debug_images)
        LOG.debug("Virtualfabrication: done...")  
        return g

class VirtualFabricationProcessSuperposition3DMaterialStackPolygonsOnly(VirtualFabricationProcessSuperposition2DMaterialStackPolygonsOnly):

    def define_geometry(self):   
        #STEP 1 : per process in 'self.process_flow.active_processes', generate a Shapely polygon indicating the area where this process will be physically applied
        (process_polygons, size_info) = self.__make_process_polygons__()
        #STEP 2 : resolve the superposition of processes and generate a geometrical description based on material stacks
        g = ProcessSuperpositionVirtualFabrication3DGeometryPolygons(material_stack_factory = self.material_stack_factory,
                                                                     processes = self.process_flow.active_processes,
                                                                     mapping_definition = self.process_flow.process_to_material_stack_map, 
                                                                     process_polygons = process_polygons, 
                                                                     size_info = size_info, 
                                                                     grid = self.grid,
                                                                     save_debug_images = self.save_debug_images)
        LOG.debug("Virtualfabrication: done...")  
        return g    


#shortcut function   
def virtual_fabrication_2d(structure, 
                           process_flow,
                           material_stack_factory,                           
                           include_growth = 0.0, 
                           environment = DEFAULT_ENVIRONMENT, 
                           grid = 0.05):    
    return VirtualFabricationProcessSuperposition2DMaterialStackPolygonsOnly(structure = structure, 
                                                                             include_growth = include_growth, 
                                                                             environment = environment,
                                                                             grid = grid,
                                                                             process_flow = process_flow,
                                                                             material_stack_factory = material_stack_factory,
                                                                             save_debug_images = False)


#shortcut function   
def virtual_fabrication_3d(structure, 
                           process_flow,
                           material_stack_factory,
                           include_growth = 0.0, 
                           environment = DEFAULT_ENVIRONMENT, 
                           grid = 0.05):    
    return VirtualFabricationProcessSuperposition3DMaterialStackPolygonsOnly(structure = structure, 
                                                                             include_growth = include_growth, 
                                                                             environment = environment,
                                                                             grid = grid,
                                                                             process_flow = process_flow,
                                                                             material_stack_factory = material_stack_factory,
                                                                             save_debug_images = False)