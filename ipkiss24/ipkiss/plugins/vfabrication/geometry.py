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

from pysics.basics.geometry.geometry import CartesianGeometry2D, __UniformEnvironmentGeometry__
from pysics.basics.material.material import MaterialProperty, Material
from pysics.basics.material.material_stack import MaterialStack, MaterialStackFactory
from ipcore.properties .predefined import *
from ipkiss.all import *
from ipkiss.geometry.coord import Coord3


class __VFabricationGeometry2D__(CartesianGeometry2D):
    grid = FloatProperty(required = True)    


class __ProcessSuperpositionMaterialStackGeometry2DPolygons__(CartesianGeometry2D):
    """2D Geometry where a superposition of processes determines the material stack. 
    The process_polygons dictionnary contains a LayerShapelyPolygons object for every process"""   
    grid = FloatProperty(required = True)   
    material_stack_factory = RestrictedProperty(required = True, restriction = RestrictType(MaterialStackFactory))
    processes = ListProperty(required = True, doc="list of all the processes (in the same order as the columns are listed in the mapping table)") 
    mapping_definition = ListProperty(required = True, doc = "list with tuples (processes_present, processes_not_present, material_stack) / material_stack")
    process_polygons = DictProperty(required = True, doc="dictionary : key : process / value: object of type LayerShapelyPolygons")
    material_stacks_shapely_polygons = DefinitionProperty(doc = "contains the resulting geometry represented as tuple (material_stack_id, shapely_polygon)")
    material_stacks_shapes = DefinitionProperty(doc = "contains the resulting geometry represented as tuple (material_stack_id, shape)")        
    canvas_size = DefinitionProperty()
    canvas_width = FunctionNameProperty(fget_name = "get_canvas_width")
    canvas_height = FunctionNameProperty(fget_name = "get_canvas_height")
    scaler = DefinitionProperty(fdef_name = "define_scaler")       
    __material_array__ = None
    save_debug_images = BoolProperty(default = False)    

    def __get_mapping_internal_format__(self):        
        """convert the mapping definition into a dataformat of tuples (processes_present, processes_not_present, material_stack)"""
        process_to_material_stack_map = []	  			
        for pflags, mstack in self.mapping_definition:
            true_list = []
            false_list = []
            for flag, process in zip(pflags, self.processes):
                if flag: 
                    true_list.append(process)
                else:
                    false_list.append(process)
            process_to_material_stack_map.append((tuple(true_list), tuple(false_list), mstack,))	
        return process_to_material_stack_map	

    def define_canvas_size(self):
        canvas_size = (int(numpy.ceil(self.size_info.width / self.grid)),
                       int(numpy.ceil(self.size_info.height / self.grid)))     
        return canvas_size	

    def get_canvas_width(self):
        return self.canvas_size[0]

    def get_canvas_height(self):
        return self.canvas_size[1]

    def define_material_stacks_shapely_polygons(self):
        """generate Shapely polygons that outline which areas are covered by material stacks. 
        Result is a list of tuples (material_stack_id, shapely_polygon)
        The first polygon indicates the canvas ('background' material stack)
        """
        from .vfabrication import LayerShapelyPolygons	
        mp = list()
        debug_counter_line = 0
        for (process_set, exclude_process_set, material_stack) in self.__get_mapping_internal_format__():
            current_len = len(process_set)
            if (current_len==0):
                empty_polygon = LayerShapelyPolygons(layer = Layer(number = 0, name = "VFABRICATION"), # FIXME: will result in problem if this layer is in use
                                                     size_info = self.size_info)
                canvas_polygon = empty_polygon.bitwise_not()
                id = self.material_stack_factory.get_material_stack_id(material_stack)
                mp.append((id,canvas_polygon))
            else:
                process_polygon = None
                debug_counter = 0
                for p in process_set:		    
                    if (process_polygon is None):
                        process_polygon = self.process_polygons[p]
                    else:
                        process_polygon = process_polygon.bitwise_and(self.process_polygons[p])
                    if (self.save_debug_images):
                        process_polygon.save_to_image("DEBUG_PROCESS_POLYGONS__%i__%i__AND_%s.png" %(debug_counter_line,debug_counter,p.extension))
                    debug_counter = debug_counter + 1
                for e_p in exclude_process_set:
                    process_polygon = process_polygon.difference(self.process_polygons[e_p])
                    if (self.save_debug_images):
                        process_polygon.save_to_image("DEBUG_PROCESS_POLYGONS__%i__%i__DIFFERENCE_%s.png" %(debug_counter_line,debug_counter,e_p.extension))
                    debug_counter = debug_counter + 1
                process_polygon.unionize()
                if (self.save_debug_images):
                    process_polygon.save_to_image("DEBUG_PROCESS_POLYGONS__%i__%i__UNION.png" %(debug_counter_line,debug_counter))
                id = self.material_stack_factory.get_material_stack_id(material_stack)
                mp.append((id,process_polygon))
            debug_counter_line = debug_counter_line + 1
        return mp

    def define_material_stacks_shapes(self):
        """generate ipkiss shapes that outline which areas are covered by material stacks. 
        Result is a list of tuples (material_stack_id, shapely_polygon)
        The first shape indicates the canvas ('background' material stack)"""
        shapes = []
        for (material_stack_id, mp) in self.material_stacks_shapely_polygons: 	
            for geom in flatten_shapely_geom(mp.georep):    
                shape = shapely_geom_to_shape(geom)	
                if len(shape.points)>0:
                    shapes.append((material_stack_id, shape))
        return shapes		    

    def define_scaler(self):
        box = self.size_info.box
        b = [box[0][0], box[1][0], box[0][1], box[1][1]] #FIXME - Scaler klasse hanteert een andere semantiek voor box... :(            
        from ipkiss.visualisation.scaler import Scaler
        scale = Scaler(b, self.canvas_size)          
        return scale	    

    def __scale_polygon_points(self, coords):
        shape = Shape(points = coords)
        scaled_shape = self.scaler.map_shape(shape)  
        points = scaled_shape.points    
        return points

    def __debug_savefig_material_array__(self, material_array, count, count_progress, material_stack_id):
        if self.save_debug_images:
            #-debug code-
            from matplotlib import pyplot
            pyplot.ion()
            pyplot.clf()
            pyplot.contourf(material_array)
            pyplot.savefig(str(count)+"_"+self.material_stack_factory[material_stack_id].name.replace(" ","_")+"_"+str(count_progress)+"_MATERIAL_ARRAY.png")
            #-end of debug code-        

    def __debug_savefig_polygon__(self, polygon_points, count, count_progress, material_stack_id):      
        if self.save_debug_images:      
            #-debug code-
            from .vfabrication import LayerShapelyPolygons
            debug_shape = Shape(polygon_points)
            debug_lbm = LayerShapelyPolygons(layer = Layer(number = 0, name = "VFABRICATION_EMPTY"),
                                             size_info = SizeInfo(west = 0, east = self.canvas_size[0], south =0, north = self.canvas_size[1]))
            debug_lbm.add_shape(debug_shape)
            debug_lbm.save_to_image(str(count)+"_"+self.material_stack_factory[material_stack_id].name.replace(" ","_")+"_"+str(count_progress)+".png")
            #-end of debug code-        

    def get_material_array(self):
        """Convert the geometrical model with polygons into a discrete matrix"""
        if (self.__material_array__ is None):
            from vfabrication import __common_function_apply_polygon_to_array_memory_sparing__
            mat_bm = self.material_stacks_shapely_polygons
            mat_bm[0] = (mat_bm[0][0], None) #replace the canvas polygon (1st element) by "None" : this is more efficient and will be interpreted identically later on
            material_array = numpy.zeros([self.canvas_width, self.canvas_height], dtype = numpy.int16) #store the material id as 16-bit integer			
            count = 0
            for (material_stack_id, mb) in mat_bm: 
                LOG.debug("Geometry : calculating material array for material_stack_id %s..." %self.material_stack_factory[material_stack_id])
                if (mb is None):
                    if (count != 0):
                        raise Exception("Unexpected error : the first element of the 'material_stacks_shapely_polygons' list is supposed to contain the background material.")
                    pass
                    material_array = material_array + material_stack_id #set whole matrix to background material stack 
                else:
                    if not mb.georep.is_empty:
                        #-debug code-
                        if self.save_debug_images:
                            mb.save_to_image(str(count)+"_"+self.material_stack_factory[material_stack_id].name.replace(" ","_")+".png")
                        #-end of debug code-
                        total_geoms = float(len(mb.georep_list))
                        count_progress = 0.0
                        for polygon in mb.georep_list:
                            if polygon.is_ring:
                                polygon_points = polygon.boundary.coords
                                self.__debug_savefig_polygon__(polygon_points,count, count_progress, material_stack_id)
                                polygon_points = self.__scale_polygon_points(polygon_points)
                                __common_function_apply_polygon_to_array_memory_sparing__(material_array, polygon_points, do_bitwise_or = False, value = material_stack_id)
                                self.__debug_savefig_material_array__(material_array, count, count_progress, material_stack_id)
                                progress_percent = count_progress / total_geoms * 100.0
                                LOG.debug("%i percent done..." %progress_percent)
                            else:
                                #outer polygon
                                outer_polygon_points = polygon.exterior.coords
                                outer_polygon_points = self.__scale_polygon_points(outer_polygon_points)
                                #FIXME - array can be made smaller to save memory (just covering the polygon)
                                mat_array = material_array_outer_polygon = numpy.zeros([self.canvas_width, self.canvas_height], dtype = numpy.int16)
                                __common_function_apply_polygon_to_array_memory_sparing__(material_array_outer_polygon, outer_polygon_points, do_bitwise_or = False, value = material_stack_id)
                                #inner polygons
                                for ip in polygon.interiors:
                                    inner_polygon_points = ip.coords
                                    inner_polygon_points = self.__scale_polygon_points(inner_polygon_points)
                                    material_array_inner_polygon = numpy.zeros([self.canvas_width, self.canvas_height], dtype = numpy.int16)
                                    __common_function_apply_polygon_to_array_memory_sparing__(material_array_inner_polygon, inner_polygon_points, do_bitwise_or = False, value = material_stack_id)
                                    #now substract and apply the two material arrays
                                    mat_array = mat_array - material_array_inner_polygon
                                material_array = numpy.where(mat_array>0, mat_array, material_array)
                                self.__debug_savefig_material_array__(material_array, count, count_progress, material_stack_id)
                            count_progress = count_progress + 1
                count = count + 1
            #the outer 2 items have sometimes not been set 
            material_array[0,:] = material_array[2,:]
            material_array[1,:] = material_array[2,:]
            material_array[-1,:] = material_array[-3,:]
            material_array[-2,:] = material_array[-3,:]

            material_array[:,0] = material_array[:,2]
            material_array[:,1] = material_array[:,2]
            material_array[:,-1] = material_array[:,-3]
            material_array[:,-2] = material_array[:,-3]
            self.__material_array__ = material_array	    
        return self.__material_array__



class ProcessSuperpositionVirtualFabrication2DGeometryPolygons(__ProcessSuperpositionMaterialStackGeometry2DPolygons__, __UniformEnvironmentGeometry__):
    pass


class ProcessSuperpositionVirtualFabrication3DGeometryPolygons(ProcessSuperpositionVirtualFabrication2DGeometryPolygons):
    size_z = FunctionNameProperty(fget_name = "get_size_z")

    def get_size_z(self):
        mat_bm = self.material_stacks_shapely_polygons
        material_stack_id = mat_bm[1][0] #take the second element of mat_bm, not the first as that is the canvas polygon
        material_stack = self.material_stack_factory[material_stack_id]
        return material_stack.size_z

    def get_material_array(self):
        raise NotImplementedException()




