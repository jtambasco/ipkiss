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

from ipcore.all import *
from ipkiss.all import *
from pysimul.runtime.basic import *
from pysics.basics.environment import *
from pysics.optics import *
from ipkiss.plugins.vfabrication import *
from ipkiss.plugins.vfabrication.vfabrication import *
from ipkiss.geometry.coord import Coord2
from pysics.basics.material.material import Material
from ipkiss.plugins.photonics.port.port import OpticalPortProperty
from pysimul.runtime.basic import *
from pysimul.runtime.definition import *
from pysimul.runtime.procedure import *
from pysimul.runtime.engine import *
from ipcore.runtime.processor import  __Processor__
from pysics.basics.environment import DEFAULT_ENVIRONMENT
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.technology.technology import *
import cPickle
from math import cos, sin, pi
from pysimul.log import PYSIMUL_LOG as LOG
import logging
import sys

__all__ = ["StructureSimulationVolume2D", 
           "GaussianVolumeSourceAtPort",
           "ModeProfileContinuousSourceAtPort",
           "get_mode_profile_at_port",
           "FluxplaneAtPort",
           "ProbingpointAtPort", 
           "ModeProfileContinuousSourceAtPosition",
           "FluxplaneAtPosition",
           "ProbingpointAtPosition", 
           "StructureSimulationDefinition"] #DEPRECATED - for backwards compatibility only - to be removed !


class __StructureSimulationVolume__(SimulationVolume1D):
    structure = RestrictedProperty(required = True, restriction = RestrictType(Structure), doc = "The ipkiss structure")
    geometry = DefinitionProperty(fdef_name = "define_geometry")
    environment = Environment(wavelength = 1.55)
    size_info = FunctionNameProperty(fget_name = "get_size_info")
    resolution = IntProperty(default = 5, doc="Resolution for discretisation of the geometry (if relevant)")
    resolution_factor = IntProperty(default = 1, doc="Additional factor to be applied to the resolution")
    include_growth = FloatProperty(default = 0.0, doc="absolute additional growth of the simulation volume")
    name = DefinitionProperty(fdef_name = "define_name")
    vfabrication_process_flow = DefinitionProperty(required = True)
    material_stack_factory = DefinitionProperty(required = True)

    def __init__(self, **kwargs):
        super(__StructureSimulationVolume__, self).__init__(**kwargs)
        self.material_dataset_dict = dict()

    def get_size_info(self):
        if not self.has_window_defined():
            si = self.geometry.size_info
        else:
            si = self.window_size_info
        return si

    def define_name(self):
        return str(self)

    def get_total_resolution(self):
        return float(self.resolution) * float(self.resolution_factor)

    def define_geometry(self):    
        raise NotImplementedException()	

    def get_material_array(self):
        raise NotImplementedException()

    def get_material_dataset(self, resolution = None):        
        raise NotImplementedException()

    def get_material_dataset_window(self, resolution = None):
        raise NotImplementedException()

    def get_material(self, coordinate):	
        raise NotImplementedException()

    def get_material_in_window(self, coordinate):	
        raise NotImplementedException()


class StructureSimulationVolume2D(__StructureSimulationVolume__, SimulationVolume2D):

    def __init__(self, **kwargs):  
        super(StructureSimulationVolume2D, self).__init__(**kwargs)
        LOG.debug("Size of simulation volume : %f x %f" %(self.width, self.height))	

    def define_geometry(self):
        LOG.debug("Running virtual fabrication on structure %s...")
        from ipkiss.plugins.vfabrication.vfabrication import virtual_fabrication_2d     	
        vf = virtual_fabrication_2d(structure = self.structure, 
                                    include_growth = self.include_growth, 
                                    environment= self.environment, 
                                    grid = 1.0 / (float(self.resolution_factor) * float(self.resolution)),
                                    process_flow = self.vfabrication_process_flow,
                                    material_stack_factory = self.material_stack_factory)
        geometry = vf.geometry
        LOG.debug("Virtual fabrication ready.")
        return geometry

    def get_window_south_west(self):
        if (not self.has_window_defined()):
            return self.size_info().south_west
        else:
            LOG.debug("Simulation window size : %f x %f" %(self.window_width, self.window_height))
            sw = self.window_size_info.south_west
            return sw

    def get_window_width(self):
        width = self.width
        if (not self.has_window_defined()):
            return width
        else:
            window_width = self.window_size_info.width
            if ((window_width > width) or (window_width < 0)):
                raise PythonSimulateException("Invalid value for simulation window (%f): the width should be larger than 0 and smaller than the structure width (=%f)."%(window_width, width))
            return window_width

    def get_window_height(self):
        height = self.height
        if (not self.has_window_defined()):
            return height
        else:
            window_height = self.window_size_info.height
            if ((window_height > height) or (window_height < 0)):
                raise PythonSimulateException("Invalid vlaue for simulation window (%f): the height should be larger than 0 and smaller than the structure height (=%f)."%(window_height, height))
            return window_height


    def get_material_dataset_for_subset(self, corner, width, height, angle = 0):
        angle = angle % 360.0
        H = do_hash("%s-%f-%f-%f"%(str(corner),width,height,angle))
        #cache already requested datasets in a dictionary attribute
        total_resolution = self.get_total_resolution()
        if not (H in self.material_dataset_dict):
            corner = Coord2(corner[0], corner[1])
            w_range = numpy.arange(0, numpy.ceil(width*total_resolution))
            h_range = numpy.arange(0, numpy.ceil(height*total_resolution))
            LOG.debug("Creating the material matrix with resolution of %i : %i x %i elements." %(total_resolution, len(w_range), len(h_range)))
            mat = numpy.zeros([len(w_range), len(h_range)], Material)
            if (angle != 0):
                for w in w_range:
                    delta_w = float(w) / total_resolution
                    current_corner = corner.move_polar_copy(delta_w, angle)
                    for h in h_range:
                        delta_h = float(h) / total_resolution
                        point = current_corner.move_polar_copy(delta_h, angle+90)
                        mat[w,h] = self.geometry.get_material(point)
                self.material_dataset_dict[H] = mat
            else:
                #faster implementation for the special case where angle == 0
                ref_point = corner - self.geometry.size_info.south_west
                delta_x = int(ref_point[0] * float(total_resolution))
                delta_y = int(ref_point[1] * float(total_resolution))
                x_min = max(0,min(w_range) + delta_x)
                y_min = max(0,min(h_range) + delta_y)
                x_max = max(w_range) + delta_x
                y_max = max(h_range) + delta_y
                full_material_array = self.geometry.get_material_array()
                mat = full_material_array[x_min:x_max+1,y_min:y_max+1]
                self.material_dataset_dict[H] = mat
        return self.material_dataset_dict[H]

    def get_material_array(self):
        return self.get_material_dataset_window()

    def get_material_dataset(self, resolution = None):
        corner = self.size_info.south_west
        return self.geometry.get_material_array()

    def get_material_dataset_window(self, resolution = None):
        if not self.has_window_defined():
            return self.get_material_dataset(resolution)
        else:
            return self.get_material_dataset_for_subset(self.get_window_south_west(), self.get_window_width(), self.get_window_height(), angle = 0)

    def get_material(self, coordinate):
        mat = self.geometry.get_material(coordinate)
        return mat

    def get_material_in_window(self, coordinate):
        mat = self.geometry.get_material(coordinate)
        return mat

    def __str__(self):
        name = "%s_2D_R%i_GR%f" %(self.structure.name, self.resolution, self.include_growth)
        return name


class StructureSimulationVolume3D(__StructureSimulationVolume__, SimulationVolume3D):  
    size_z = FunctionNameProperty(fget_name = "get_size_z")

    def get_size_info(self):
        si = self.geometry.size_info
        si.size_z = self.size_z
        return si

    def get_size_z(self):
        return self.geometry.size_z

    def __str__(self):
        name = "%s_3D_R%i_GR%f" %(self.structure.name, self.resolution, self.include_growth)
        return name   

    def define_geometry(self):
        LOG.debug("Running virtual fabrication 3d on structure %s...")
        from ipkiss.plugins.vfabrication.vfabrication import virtual_fabrication_3d     	
        vf = virtual_fabrication_3d(structure = self.structure, 
                                    include_growth = self.include_growth, 
                                    environment= self.environment, 
                                    grid = 1.0 / (float(self.resolution_factor) * float(self.resolution)),
                                    process_flow = self.vfabrication_process_flow,
                                    material_stack_factory = self.material_stack_factory)
        geometry = vf.geometry                	
        LOG.debug("Virtual fabrication ready.")
        return geometry  	    


class GaussianVolumeSourceAtPort(GaussianVolumeSource):
    port = OpticalPortProperty(required = True)
    north = DefinitionProperty(fdef_name = "define_north")
    south = DefinitionProperty(fdef_name = "define_south")

    def define_north(self):
        return self.port.corner1 

    def define_south(self):
        return self.port.corner2 



class ModeProfileContinuousSourceAtPort(AmplitudeShapedContinuousVolumeSource, CartesianGeometry2D):
    port = OpticalPortProperty(required = True)   
    mode = IntProperty(default = 0)
    north = DefinitionProperty(fdef_name = "define_north")
    south = DefinitionProperty(fdef_name = "define_south")    
    size_info = FunctionNameProperty(fget_name = "get_size_info")
    mode_profile = DefinitionProperty(fdef_name = "define_mode_profile")
    save_images = BoolProperty(default = True, doc="Export images (and csv files) during calculation of the mode profile")
    field_component = FunctionNameProperty(fget_name = "get_field_component")
    polarization = IntProperty(default = TE, doc="TM or TE polarization")
    material_stack_factory = RestrictedProperty(restriction = RestrictType(MaterialStackFactory))

    def set_structure_simulation_volume(self, structure_simulation_volume):
        self.structure_simulation_volume = structure_simulation_volume	
        self.resolution = (self.structure_simulation_volume.resolution * self.structure_simulation_volume.resolution_factor)
        self.grid = 1.0 / self.resolution

    def get_material(self, coordinate):
        if (not hasattr(self, "material_dataset")):
            self.material_dataset = self.get_material_array()
        x = coordinate[0]
        y = coordinate[1]
        return self.material_dataset[x,y]    

    def get_size_info(self):	
        L = self.south.distance(self.north)
        return SizeInfo(west = 0.0, east = 0.1, north = L, south = 0.0)

    def get_material_array(self):
        if (not hasattr(self, 'structure_simulation_volume')):
            raise PythonSimulateException("Attrbute not set : structure_simulation_volume. Call function 'set_structure_simulation_volume' with a reference to the object of type StructureSimulationVolume2D.")
        si = self.size_info
        v = self.structure_simulation_volume
        material_dataset = v.get_material_dataset_for_subset(self.south, si.width, si.height, self.port.angle+180.0)
        return material_dataset

    def define_material_stack_factory(self):
        v = self.structure_simulation_volume
        return v.geometry.material_stack_factory

    def define_north(self):
        P = self.port.position.move_polar_copy(self.port.wg_definition.wg_width / 2.0 + self.port.wg_definition.trench_width - (self.grid / 2.0), self.port.angle - 90)
        return P

    def define_south(self): #'south' for west-facing port (angle = 180), just a convention
        P = self.port.position.move_polar_copy(self.port.wg_definition.wg_width / 2.0 + self.port.wg_definition.trench_width - (self.grid / 2.0), self.port.angle + 90)
        return P

    def define_mode_profile(self):
        if (not hasattr(self, 'structure_simulation_volume')):
            raise PythonSimulateException("Attribute not set : structure_simulation_volume. Call function 'set_structure_simulation_volume' with a reference to the object of type StructureSimulationVolume2D.")
        import camfr 
        camfr_technology = TechnologyTree()
        if self.polarization == TE:	    
            camfr_technology.POLARIZATION = camfr.TM # use for top-down simulations : #TE-mode in 3D -> TM-mode for 2D upper surface view -> extract Hz component
        elif self.polarization == TM:
            camfr_technology.POLARIZATION = camfr.TE # use for top-down simulations : #TM-mode in 3D -> TE-mode for 2D upper surface view -> extract Ez component	    
        else:
            raise Exception("Unknown value for polarization.")
        camfr_technology.NMODES = 50
        camfr_technology.PML = -0.05
        camfr_technology.WAVELENGTH = self.center_wavelength / 1000.0
        from pysimul.runtime.camfr_engine.camfr_engine import CamfrEngine
        engine = CamfrEngine(camfr_technology = camfr_technology, save_images = self.save_images)
        engine.set_camfr_settings(camfr_technology)
        (profiles, beta, transmission) = engine.field_for_geometry(self, 
                                                                   field_extraction_geometry_x_positions = [0.0], 
                                                                   max_slabs = 1, 
                                                                   geometry_name = self.structure_simulation_volume.structure.name)
        profile = profiles[0]
        positions = [c[1] for c in profile.positions] 
        relative_positions = positions - (positions[-1] / 2.0)
        if self.polarization == TE:
            Hz = [f.H.value.z.real for f in  profile.fields]
            return (relative_positions, Hz)
        elif self.polarization == TM:
            Ez = [f.E.value.z.real for f in  profile.fields]
            return (relative_positions, Ez)
        else:
            raise Exception("Unknown value for polarization.")	

    def get_field_component(self):
        if self.polarization == TE:
            return compHz 
        elif self.polarization == TM:
            return compEz
        else:
            raise Exception("Unknown value for polarization.")

    def get_amplitude_factor(self, coordinate_relative_to_port_position):	
        positions = self.mode_profile[0]
        fields = self.mode_profile[1]
        from scipy.interpolate import interp1d as interp
        i = interp(x = positions, y = fields, kind = 'linear', copy = True, bounds_error = False, fill_value = 0.0)	
        f = float(i(coordinate_relative_to_port_position[1]))
        return f


def get_mode_profile_at_port(structure, resolution, port, wavelength, save_images = True):
    """This function can be used for users who want to combine Pysimul with low-level python-meep scripting. Given a port, calculate the ground mode profile with Camfr."""
    simul_params = dict()
    simul_params["structure"] = structure
    simul_params["resolution"] = resolution    
    simulation_volume = StructureSimulationVolume2D(simul_params = simul_params)		
    s = ModeProfileContinuousSourceAtPort(center_wavelength = wavelength, 
                                          port = port, 
                                          smoothing_width = 0.0,  #dummy value: we will not actually trigger the source	                                               
                                          stop_time = 1.0, #dummy value: we will not actually trigger the source
                                          save_images = save_images) 
    s.set_structure_simulation_volume(simulation_volume)	
    return s.mode_profile


class ModeProfileContinuousSourceAtPosition(ModeProfileContinuousSourceAtPort):
    port = DefinitionProperty(fdef_name="define_port")
    position = Coord2Property(required = True)
    angle = FloatProperty(required = True) # for the mode profile calculation
    width = FloatProperty(default = TECH.WG.WIRE_WIDTH)

    def define_port(self):
        return OpticalPort(position = self.position, angle = self.angle, wg_definition = WgElDefinition(wg_width = self.width / 2.0, trench_width = 0.0))	    


class FluxplaneAtPort(Fluxplane):
    port = OpticalPortProperty(required = True)    
    north = DefinitionProperty(fdef_name = "define_north")
    south = DefinitionProperty(fdef_name = "define_south")
    overlap_trench = BoolProperty(default = True)

    def define_north(self):
        if (self.overlap_trench):
            tw = self.port.wg_definition.trench_width
            if (tw == 0.0):
                tw = self.port.wg_definition.wg_width / 2.0
        else:
            tw=0
        P = self.port.position.move_polar_copy(self.port.wg_definition.wg_width / 2.0 + tw, self.port.angle - 90)
        return P

    def define_south(self): #'south' for west-facing port (angle = 180), just a convention
        if (self.overlap_trench):
            tw = self.port.wg_definition.trench_width
            if (tw == 0.0):
                tw = self.port.wg_definition.wg_width / 2.0
        else:
            tw=0
        P = self.port.position.move_polar_copy(self.port.wg_definition.wg_width / 2.0 + tw, self.port.angle + 90)
        return P    


class FluxplaneAtPosition(FluxplaneAtPort):
    port = DefinitionProperty(fdef_name="define_port")
    position = Coord2Property(required = True)
    angle = FloatProperty(default = 0.0)
    width = FloatProperty(default = TECH.WG.WIRE_WIDTH)


    def define_port(self):	
        return OpticalPort(position = self.position, 
                           angle = self.angle, 
                           wg_definition = WgElDefinition(wg_width = self.width / 2.0, trench_width = 0.0))    

class ProbingpointAtPort(Probingpoint):
    port = OpticalPortProperty(required = True)    
    point = DefinitionProperty(fdef_name = "define_point")    

    def define_point(self):
        return self.port.position


class ProbingpointAtPosition(ProbingpointAtPort):
    port = DefinitionProperty(fdef_name="define_port")   
    point = Coord2Property(required = True)   

    def define_point(self):
        return self.point  



def PicazzoComponentSaveResult(filename):
    pass



class StructureSimulationDefinition(SimulationDefinition):
    procedure_class = DefinitionProperty(fdef_name = "define_procedure_class")       

    def __init__(self, simul_params):
        if "component" in simul_params:
            #FIXME -- THIS MAY BE REMOVED IN A LATER PHASE...
            simul_params["structure"] = simul_params["component"]
            del simul_params["component"]
            LOG.deprecation_warning("Please switch the name of simulation parameter 'component' to 'structure'.",-1)
        struct = simul_params["structure"]
        simul_params["simulation_id"] = struct.name.replace("<","").replace(">","")
        if "vfabrication_process_flow" not in simul_params:
            simul_params["vfabrication_process_flow"] = TECH.VFABRICATION.PROCESS_FLOW
        if "material_stack_factory" not in simul_params:
            simul_params["material_stack_factory"] = TECH.MATERIAL_STACKS 	
        dim = self.__get_simulation_dimension__(simul_params)

        if dim == 2:
            if ("engine" in simul_params):
                # FIXME: ENgine should check its parameters itself. 
                # Possible solution: add parameter check to StrongPropertyInitializer 
                # to check parameter requirements without need for instantiation.
                try:
                    from pysimul.runtime.camfr_engine.camfr_engine import CamfrEngine		
                except ImportError:
                    pass
                try:
                    from pysimul.runtime.MeepFDTD.MeepFDTD import MeepSimulationEngine
                except ImportError:
                    pass

                if 'CamfrEngine' in sys.modules and isinstance(simul_params["engine"], CamfrEngine):
                    if ("resolution_factor" not in simul_params) or (simul_params["resolution_factor"] != 1):
                        simul_params["resolution_factor"] = 1
                        LOG.warning("Parameter 'resolution_factor' forced to 1 for CAMFR engine.")
                
                elif 'MeepSimulationEngine' in sys.modules and isinstance(simul_params["engine"], MeepSimulationEngine):
                    if ("resolution_factor" not in simul_params):
                        simul_params["resolution_factor"] = 2
                        LOG.warning("Parameter 'resolution_factor' was missing and thus set to 2 for MEEP engine.")
                 

        SimulationDefinition.__init__(self, simul_params = simul_params)

    def __get_simulation_dimension__(self, simul_params):
        if ("dimensions" in simul_params):
            dim = int(simul_params["dimensions"])
            if (dim in [2,3]):
                return dim
            else:
                raise Exception("Invalid value for simulation parameter 'dimensions': should be 2 or 3.")
        else:
            return 2


    def define_landscape(self):
        dim = self.__get_simulation_dimension__(self.simul_params)  	
        if(dim == 2):
            simulation_volume = StructureSimulationVolume2D(simul_params = self.simul_params)	
            #do some initialisations specific for certain types of sources
            if "sources" in self.simul_params:
                for src in self.simul_params["sources"]:
                    if (isinstance(src, ModeProfileContinuousSourceAtPort)):
                        src.set_structure_simulation_volume(simulation_volume)
            else:
                self.simul_params["sources"] = []
        else: #dim==3
            simulation_volume = StructureSimulationVolume3D(simul_params = self.simul_params)		   
            #self.simul_params["sources"] = []	    //fix requested by Thach Nguyen 2012-12-19
        #create the Landscape	
        if not ("datacollectors" in self.simul_params):
            self.simul_params["datacollectors"] = []
        ls = SimulationLandscape(simulation_volume = simulation_volume , simul_params = self.simul_params)  
        #do initialisation for certain types of processors
        if "step_processor" in self.simul_params:
            p = self.simul_params["step_processor"]
            from pysimul.runtime.processor import SaveFieldsHDF5Processor
            if (isinstance(p, SaveFieldsHDF5Processor)):
                p.fileName = ls.simulation_id+"_"+str(p.field_component)+".h5"
        #do initialisation for certain types of post-processors
        if "post_processor" in self.simul_params:
            pp = self.simul_params["post_processor"]
            from pysimul.runtime.processor import FluxSimulationProcessor
            if (isinstance(pp, FluxSimulationProcessor)):
                pp.initialize(ls)
        return ls

    def define_procedure_class(self):
        engine = self.simul_params["engine"]
        procedure_class = engine.get_procedure_class()
        return procedure_class

    def define_procedure(self):
        cls = self.procedure_class
        pr = cls(engine = self.simul_params["engine"], landscape = self.landscape,simul_params = self.simul_params)
        return pr


PicazzoStructureSimulationDefinition = StructureSimulationDefinition #DEPRECATED - for backwards compatibility only - to be removed



