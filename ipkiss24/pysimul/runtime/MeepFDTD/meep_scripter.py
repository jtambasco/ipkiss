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

from pysimul.runtime.engine import *
from pysimul.runtime.procedure import *
from pysimul.runtime.processor import *
from pysimul.runtime.basic import *
from pysimul.runtime.basic import __SimulationVolume__, __EMSource__, __GaussianSource__, __ContinuousSource__, __AmplitudeShapedSource__, __EMPointSource__, __EMVolumeSource__
from pysimul.runtime.procedure import *
from ipcore import *
import os


class MeepScripter(FDTDEngine):
    use_averaging = BoolProperty(default=True, doc="Use subpixel averaging in Meep.")
    is_nonlinear = BoolProperty(default=False, doc="When True, use nonlinear chi3. Default False.")

    # FIXME: Make more general. Problem is you cannot pass a symmetry-instance because it needs the volume, which is generated inside initialize_engine
    symmY = BoolProperty(default=False, doc="Use symmetry in Y-direction? Default = False (no symmetry). See python-meep doc.")        

    def init_script(self, landscape, scripter_function, name_template = None):
        '''Initializes the Meep simulation engine. Parameter is a reference to the simulation landscape (object of type runtime.basic.SimulationLandscape) .'''	
        if not isinstance(landscape, SimulationLandscape):
            raise InvalidArgumentException("Invalid argument for function setLandscape:: not of type runtime.basic.SimulationLandscape.")
        if name_template is None:
            name_template = landscape.simulation_volume.name
        self.__script__ = scripter_function
        self.landscape = landscape
        self.__script__(""" 
from cPickle import dump, load

try:
    import meep as meep
except ImportError, e:
    try :
	import meep_mpi as meep
    except ImportError, e:
	raise Exception("Modules 'meep' or 'meep_mpi' not found.")    
	""")
        self.__script__("meep.use_averaging(%s)" %self.use_averaging) 
        self.__script__("meep.quiet(False)")		
        self.dim = self.__createMeepComputationalVolume__(landscape.simulation_volume)
        self.__script__("#callback for epsilon-values")
        if self.dim == 2:
            materials_2d_filename = name_template+".materials2D.pysimul"
            self.__script__("from pysimul.runtime.MeepFDTD.meep_scripter_runtime import MeepMaterial2DPolygonsFromFile")
            self.__script__("material = MeepMaterial2DPolygonsFromFile(config_file = \"%s\", meep_volume = meep_vol)" %(materials_2d_filename)) 
            self.__script__("meep.set_EPS_Callback(material.__disown__())")
            material_stacks_shapely_polygons = landscape.simulation_volume.geometry.material_stacks_shapely_polygons
            south_west = landscape.simulation_volume.size_info.south_west	    
            bitmap_polygons = []
            eps_values = []
            for material_stack_id, bitmap_polygon in material_stacks_shapely_polygons: 
                bitmap_polygons.append(bitmap_polygon)
                eps_values.append(landscape.simulation_volume.geometry.material_stack_factory[material_stack_id].effective_index_epsilon)	
            from cPickle import dump
            file_handle = open(materials_2d_filename, "w")
            dump((bitmap_polygons, eps_values, south_west),file_handle)
            file_handle.close()
        else: #dim == 3
            materials_3d_filename = name_template+".materials3D.pysimul"
            self.__script__("from pysimul.runtime.MeepFDTD.meep_scripter_runtime import MeepMaterial3DPolygonsFromFile")
            self.__script__("material = MeepMaterial3DPolygonsFromFile(config_file = \"%s\", meep_volume = meep_vol)" %(materials_3d_filename)) 
            self.__script__("meep.set_EPS_Callback(material.__disown__())")	    
            material_stacks_shapely_polygons = landscape.simulation_volume.geometry.material_stacks_shapely_polygons
            bitmap_polygons = []
            material_stack_ids = []
            for material_stack_id, bitmap_polygon in material_stacks_shapely_polygons: 
                bitmap_polygons.append(bitmap_polygon)
                material_stack_ids.append(material_stack_id)	
            south_west = landscape.simulation_volume.size_info.south_west	
            material_stacks_npy = landscape.simulation_volume.geometry.get_numpy_matrix_representation_of_all_material_stacks()
            n_o_material_stacks = landscape.simulation_volume.geometry.get_number_of_material_stacks_in_store()
            from cPickle import dump
            file_handle = open(materials_3d_filename, "w")
            dump((bitmap_polygons, material_stack_ids, south_west, material_stacks_npy, n_o_material_stacks),file_handle)
            file_handle.close()	    	    
        if( self.symmY ):
            self.__script__("symmetry_object = meep.mirror(meep.Y,meep_vol)")
            self.__script__("symmetry_object = symmetry_object * complex(1.0,0.0)")
        else:
            self.__script__("symmetry_object = meep.identity()")	

        # When there is a certain PML direction, use that one.
        if landscape.pml_thickness > 0.0:
            self.__script__("#PML")
            if isinstance( landscape.pml_direction, str ):
                dirint = 'XYZ'.rfind(str.upper(landscape.pml_direction))
                assert dirint<=0, 'PML direction should be either X, Y or Z'
                if dirint == 0: self.__script__("direction = meep.X")
                if dirint == 1: self.__script__("direction = meep.Y")
                if dirint == 2: self.__script__("direction = meep.Z")
                self.__script__("pml = meep.pml(%f, direction)" %landscape.pml_thickness)
            else:
                self.__script__("pml = meep.pml(%f)" %landscape.pml_thickness)
        else:
            self.__script__("pml = meep.pml(0.0)")

        self.__script__("#structure and fields")
        self.__script__("structure = meep.structure(meep_vol , meep.EPS, pml, symmetry=symmetry_object )")
        if self.is_nonlinear:
            self.__script__("chi3 = MeepChi3_2D(simulation_volume, meep_vol)")
            self.__script__("meep.set_CHI3_Callback(chi3.__disown__())")
            self.__script__("structure.set_chi3(CHI3)")

        self.__script__("meep_fields = meep.fields(structure)")	

        self.__exportDielectricH5__(name_template+".eps.h5")

        seq_nr_src = 0
        self.ampl_shaping_counter = 0
        for src in landscape.sources:
            self.__addMeepSource__(src, landscape, seq_nr_src, name_template)
            seq_nr_src = seq_nr_src + 1
        seq_nr_fp = 0
        for c in landscape.datacollectors:
            if isinstance(c, Fluxplane):
                self.__addMeepFluxplane__(c, seq_nr_fp)
                seq_nr_fp = seq_nr_fp + 1

    def fini_script(self, landscape, scripter_function, name_template):
        seq_nr_fp = 0
        for c in landscape.datacollectors:
            if isinstance(c, Fluxplane):
                self.__collectAndSaveFluxplane__(name_template, c, seq_nr_fp)
                seq_nr_fp = seq_nr_fp + 1
        if len(landscape.sources)>0:
            self.__script__("del(h5_field_file_handle)")

    def __createMeepComputationalVolume__(self, volume):
        '''Convert the simulation volume (runtime.basic.__SimulationVolume__) into a Meep computational volume'''
        if not isinstance(volume, __SimulationVolume__):
            raise InvalidArgumentException("Invalid argument:: not of type runtime.basic.__SimulationVolume__")	   
        self.__script__("#computational volume")
        if isinstance(volume, SimulationVolume3D):
            self.__script__("meep_vol = meep.vol3d(%f,%f,%f,%i)" %(volume.window_width, volume.window_height, volume.size_z, self.resolution))
            return 3
        if isinstance(volume, SimulationVolume2D):
            self.__script__("meep_vol = meep.vol2d(%f,%f,%i)" %(volume.window_width, volume.window_height, self.resolution))
            return 2
        if isinstance(volume, SimulationVolume1D):
            self.__script__("meep_vol = meep.vol1d(%f,%i)" %(volume.window_width, self.resolution))
            return 1

    def __calc_meep_coord__(self, coord):
        '''Convert a Coord3 object into Meep coordinates'''
        import math
        vol = self.landscape.simulation_volume
        sw = Coord3(vol.size_info.south_west)
        accuracy = int(math.ceil(math.log10(1.0 / (1.0 / self.resolution / 100) )))
        c = coord - sw
        x = round(c.x, accuracy) #because of floating point accuracy erros with Python, whereby sometimes a wrong value is then sent to Meep 
        if (self.dim == 3):
            y = round(c.y, accuracy)
            #FIXME -- TO BE EXTENDED -- z = round(c.z, accuracy)	    
            #FIXME return (x, y, z) 
            return (x, y, 0) 
        elif (self.dim == 2):
            y = round(c.y, accuracy)
            return (x, y)
        elif (self.dim == 1):
            return (x)

    def __make_meep_vec__(self, coord):
        '''Convert a Coord3 object into a Meep vec object'''
        if (self.dim == 3):
            (x,y,z) = self.__calc_meep_coord__(coord)
            return "meep.vec(%f,%f,[FIXME])" %(x, y)
        elif (self.dim == 2):
            (x,y) = self.__calc_meep_coord__(coord)
            return "meep.vec(%f,%f)" %(x, y)
        elif (self.dim == 1):
            (x) = self.__calc_meep_coord__(coord)
            return "meep.vec(%f)" %(x)
        else:
            raise PythonSimulateException("Invalid value for self.dim : expected 1, 2 or 3. The value is : %s" %str(self.dim))

    def __makeMeepComponent__(self, comp):
        if comp == compEx:
            return "meep.Ex"
        elif comp == compEy:
            return "meep.Ey"
        elif comp == compEz:
            return "meep.Ez"
        elif comp == compHx:
            return "meep.Hx"
        elif comp == compHy:
            return "meep.Hy"
        elif comp == compHz:
            return "meep.Hz"
        raise PythonSimulateException("Unknown component. Must be Ex, Ey, Ez, Hx, Hy or Hz.")

    def __addMeepSource__(self, src, landscape, seq_nr, name_template):	
        '''Convert a source (runtime.basic.__EMSource__) into a Meep source and add it to the Meep fields object'''
        if not isinstance(src, __EMSource__):
            raise InvalidArgumentException("Invalid argument:: not of type runtime.basic.__EMSource__")	   	
        self.__script__("#source %i" %seq_nr)
        #create Meep source object
        meepSource = None
        self.__script__("src%i_center_wavelength = %f" %(seq_nr, src.center_wavelength))
        self.__script__("src%i_center_freq = 1.0 / (float(src%i_center_wavelength) / 1000.0)" %(seq_nr, seq_nr))
        if isinstance(src, __GaussianSource__):
            self.__script__("src%i_pulse_width_wl = %f" %(seq_nr, src.pulse_width))
            self.__script__("src%i_pulse_width_freq = ( (float(src%i_pulse_width_wl)/1000.0) / (float(src%i_center_wavelength)/1000.0) ) * src%i_center_freq" %(seq_nr,seq_nr,seq_nr,seq_nr))
            self.__script__("meepSource%i = meep.gaussian_src_time(src%i_center_freq, src%i_pulse_width_freq)" %(seq_nr, seq_nr, seq_nr))
        if isinstance(src, __ContinuousSource__):
            self.__script__("meepSource%i = meep.continuous_src_time(src%i_center_freq, %f, %f, %f, %f)" %(seq_nr, seq_nr, src.smoothing_width, src.start_time, src.stop_time, src.cutoff))
        #create Meep component
        meepComp = self.__makeMeepComponent__(src.field_component)
        #add source to the Meep field
        if isinstance(src, __EMPointSource__):
            vec = self.__make_meep_vec__(src.point)	    
            self.__script__("meep_fields.add_point_source(%s, meepSource%i, %s)" %(meepComp, seq_nr, vec))
        elif isinstance(src, __EMVolumeSource__):
            vec1 = self.__make_meep_vec__(src.south)
            vec2 = self.__make_meep_vec__(src.north)	       
            self.__script__("meepSrcVol%i = meep.volume(%s,%s)" %(seq_nr, vec1, vec2))
            if isinstance(src, __AmplitudeShapedSource__):
                self.ampl_shaping_counter = self.ampl_shaping_counter + 1
                if self.ampl_shaping_counter>1:
                    raise Exception("Amplitude shaping is supported for maiximum 1 source...")
                file_name = name_template+".ampl_src%i.pysimul"%seq_nr
                self.__script__("from pysimul.runtime.MeepFDTD.meep_scripter_runtime import AmplitudeFactorFromFile") 
                self.__script__("ampl = AmplitudeFactorFromFile(config_file = \"%s\")" %file_name)
                self.__script__("meep.set_AMPL_Callback(ampl.__disown__())")
                self.__script__("meep_fields.add_volume_source(%s, meepSource%i, meepSrcVol%i, meep.AMPL)" %(meepComp, seq_nr, seq_nr))
                from cPickle import dump
                file_handle = open(file_name, 'w')
                dump(src.mode_profile, file_handle)
                file_handle.close()
            else:
                self.__script__("meep_fields.add_volume_source(%s, meepSource%i, meepSrcVol%i, %f)" %(meepComp, seq_nr, seq_nr, src.amplitude))
        else:
            raise NotImplementedException("Unexpected case in MeepSimulationEngine::__addMeepSource__")

    def __addMeepFluxplane__(self, flx, seq_nr = 1):
        '''Convert a fluxplane (runtime.basic.Fluxplane) into a Meep fluxplane and add it to the Meep fields object'''	
        if not isinstance(flx, Fluxplane):
            raise InvalidArgumentException("Invalid argument:: not of type runtime.basic.Fluxplane")	  
        vec1 = self.__make_meep_vec__(flx.north)
        vec2 = self.__make_meep_vec__(flx.south)
        self.__script__("#flux plane %i" %seq_nr)
        self.__script__("flx%i_vol = meep.volume(%s,%s)" %(seq_nr, vec1,vec2))
        self.__script__("flx%i_center_wavelength = %f" %(seq_nr,flx.center_wavelength))
        self.__script__("flx%i_center_freq = 1.0 / (float(flx%i_center_wavelength) / 1000.0)" %(seq_nr, seq_nr))
        self.__script__("flx%i_pulse_width_wl = %f" %(seq_nr,flx.pulse_width))
        self.__script__("flx%i_pulse_width_freq = ( (float(flx%i_pulse_width_wl)/1000.0) / (float(flx%i_center_wavelength)/1000.0) ) * flx%i_center_freq" %(seq_nr,seq_nr,seq_nr,seq_nr))
        self.__script__("flx%i_max_freq = flx%i_center_freq + flx%i_pulse_width_freq / 2.0" %(seq_nr,seq_nr,seq_nr))
        self.__script__("flx%i_min_freq =  flx%i_center_freq - flx%i_pulse_width_freq / 2.0" %(seq_nr,seq_nr,seq_nr))
        self.__script__("flx%i_plane = meep_fields.add_dft_flux_plane(flx%i_vol, flx%i_min_freq, flx%i_max_freq, %i )" %(seq_nr, seq_nr, seq_nr, seq_nr, flx.number_of_sampling_freq))
        if not (flx.init_hdf5 is None):
            self.__script__("flx%i_plane.load_hdf5(meep_fields, \"%s\")" %(seq_nr,flx.init_hdf5.replace(".h5","")))


    def __collectAndSaveFluxplane__(self, filename_prefix, flx, seq_nr = 1):
        self.__script__("#collect flux data and save it to file, so it can be retrieved later for analysis")	
        self.__script__("flux%i_data = meep.getFluxData(flx%i_plane)" %(seq_nr, seq_nr))
        self.__script__("flux%i_file_handle = open(\"%s\",'w')" %(seq_nr,filename_prefix+".fluxplane_"+flx.name.replace(" ","_")))
        self.__script__("dump(flux%i_data, flux%i_file_handle)" %(seq_nr, seq_nr))
        self.__script__("flux%i_file_handle.close()" %seq_nr) 	

    def __addMeepProbingPoint__(self, c, seq_nr):
        self.__script__("#probing point %i" %seq_nr)	
        self.__script__("pp%i_coord = %s" %(seq_nr, self.__make_meep_vec__(c.point)))

    def __exportDielectricH5__(self, filename = None):
        '''Export the dielectric to a HDF5 output file'''
        self.__script__("#export dielectricum to HFD5 file")
        self.__script__("if meep.am_master():")
        self.__script__("\tdielectric_file_handle = meep.prepareHDF5File(\"%s\")" %(filename))   
        self.__script__("\tmeep_fields.output_hdf5(meep.Dielectric, meep_vol.surroundings(), dielectric_file_handle)")
        self.__script__("\tdel(dielectric_file_handle)")
        if self.dim == 2:
            self.__script__("\timport os")
            self.__script__("\tos.system(\"h5topng -a yarg %s \")" %filename)	    

    def get_procedure_class(self):
        return MeepScripterProcedure


from pysimul.runtime.procedure import FDTDFieldCalculationProcedure	
from ipcore.runtime.processor import __StopCriterium__

class MeepScripterProcedure(FDTDFieldCalculationProcedure):
    stopcriterium = RestrictedProperty(default=__StopCriterium__(), restriction = RestrictType(__StopCriterium__), doc = "Stopcriterium for the simulation procedure.")     

    def __init_script_file_handle__(self, filename):
        self.__script_file_handle__ = open(filename,"w")	

    def __close_script_file_handle__(self):
        if not (self.__script_file_handle__ is None):
            self.__script_file_handle__.close()

    def __script__(self, cmd):
        self.__script_file_handle__.write(cmd+os.linesep)       

    def run(self, interactive_mode = False, append_script = "", name_template = None):
        self.interactive_mode = interactive_mode
        try:
            self.visualize_landscape()
        except Exception, e:
            print 'Cannot visualize in FDTDFieldCalculationProcedure. Maybe DISPLAY is not set and you''re working remote? Error:', e
        if name_template is None:
            name_template = self.landscape.simulation_volume.name
        script_filename = "meep_"+name_template+".py"
        self.__init_script_file_handle__(filename = script_filename)		    
        self.engine.init_script(self.landscape, self.__script__, name_template = name_template)	
        if isinstance(self.stopcriterium, RunUntilFieldsDecayedAtProbingPoint):
            self.__script__("#stop criterium")
            self.__script__("stopcriterium_field_component = %s" %self.engine.__makeMeepComponent__(self.stopcriterium.field_component))
            self.__script__("stopcriterium_probing_point = %s" %self.engine.__make_meep_vec__(self.stopcriterium.probingpoint.point))
            self.__script__("h5_field_file_handle = meep.prepareHDF5File(\"%s\")" %(name_template+"."+str(self.stopcriterium.field_component)+".h5"))
            stopcriterium_txt = "meep.runUntilFieldsDecayed(meep_fields, meep_vol, stopcriterium_field_component, stopcriterium_probing_point, pDecayFactor = %f, pHDF5OutputFile = h5_field_file_handle" %(self.stopcriterium.decay_factor)
            if isinstance(self.step_processor, SaveFieldsHDF5Processor):
                if self.step_processor.field_component != self.stopcriterium.field_component:
                    raise Exception("MeepScripterProcedure can only handle a combination of RunUntilFieldsDecayedAtProbingPoint and SaveFieldsHDF5Processor with both the same field component parameter.")
                self.__script__(stopcriterium_txt+", pH5OutputIntervalSteps = %i)" %(self.step_processor.H5OutputIntervalSteps))
            else:
                self.__script__(stopcriterium_txt+")")
        elif isinstance(self.stopcriterium, StopAfterSteps):
            self.__script__("#stop after %i steps" %self.stopcriterium.maximumSteps)
            if isinstance(self.step_processor, SaveFieldsHDF5Processor):
                self.__script__("h5_field_file_handle = meep.prepareHDF5File(\"%s\")" %(name_template+"."+str(self.step_processor.field_component)+".h5"))				    
            self.__script__("step_count = 0")
            self.__script__("max_steps = %i" %self.stopcriterium.maximumSteps)
            self.__script__("print_step = int(max_steps / 10.0)")
            self.__script__("while step_count <= max_steps:")
            self.__script__("    meep_fields.step()")
            self.__script__("    if step_count % print_step == 0:")
            self.__script__("	print \"Simulation is at step : %i \"%step_count")
            if isinstance(self.step_processor, SaveFieldsHDF5Processor):
                self.__script__("    if step_count %"+" %i == 0:" %self.step_processor.H5OutputIntervalSteps)
                self.__script__("		meep_fields.output_hdf5(%s, meep_vol.surroundings(), h5_field_file_handle, 1)" %self.engine.__makeMeepComponent__(self.step_processor.field_component))
            self.__script__("    step_count = step_count + 1")
        else:
            if not isinstance(self.stopcriterium, __StopCriterium__):
                self.__script__("#STOPCRITERIUM : type %s was not yet implemented : manually add the code for your stopcriterium" %type(self.stopcriterium))
        self.engine.fini_script(self.landscape, self.__script__, name_template)
        self.__script__(append_script.replace("%name",name_template))
        self.__close_script_file_handle__()
        print "Meep script generated : %s" %script_filename


