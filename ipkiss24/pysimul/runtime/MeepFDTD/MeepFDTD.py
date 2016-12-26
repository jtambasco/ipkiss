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

try:
    import meep as Meep
except ImportError, e:
    try :
        import meep_mpi as Meep
    except ImportError, e:
        raise ImportError("Modules 'meep' or 'meep_mpi' not found.")    

import h5py
import math
from pysics.basics.material.material import Material
from ipkiss.log import IPKISS_LOG as LOG


class MeepChi3_2D(Meep.CallbackMatrix2D):  
    def __init__(self,  simul_volume, meep_volume):
        try:
            Meep.CallbackMatrix2D.__init__(self)
            #ipcore properties cannot be used here in combination with swig wrapper around Meep.Callback class - FIXME - to be investigated furher
            if not isinstance(simul_volume, __SimulationVolume__):
                raise AttributeException("Parameter simul_volume of class MeepMaterial2D must be of type __SimulationVolume__")
            resolution_factor = simul_volume.resolution_factor
            LOG.debug("Meep : using a resolution factor of %i (Numpy matrix has %i times higher resolution than the Meep grid)." %(resolution_factor,resolution_factor))
            meep_resolution = meep_volume.a
            material_matrix =  simul_volume.get_material_dataset_window(meep_resolution * resolution_factor)
            #convert the material matrix to a matrix with epsilon values (doubles)
            from pysics.materials.electromagnetics import transform_material_stack_matrix_in_chi3_matrix
            self.material_chi3_matrix = transform_material_stack_matrix_in_chi3_matrix(material_matrix)
            self.set_matrix_2D(self.material_chi3_matrix, meep_volume, resolution_factor)
            LOG.debug("Meep node %i -MeepMaterial2D (chi3) object initialized." %int(Meep.my_rank()))
        except Exception, e:
            print "Exception in MeepMaterial2D::__init__ : %s" %e	    
            raise e

    def __getstate__(self): #for pickle : do not serialize
        return None


class MeepMaterial2DMatrix(Meep.CallbackMatrix2D):  
    def __init__(self,  simul_volume, meep_volume):
        Meep.CallbackMatrix2D.__init__(self)
        #ipcore properties cannot be used here in combination with swig wrapper around Meep.Callback class - FIXME - to be investigated furher
        if not isinstance(simul_volume, __SimulationVolume__):
            raise AttributeException("Parameter simul_volume of class MeepMaterial2D must be of type __SimulationVolume__")
        resolution_factor = simul_volume.resolution_factor
        LOG.debug("Meep : using a resolution factor of %i (Numpy matrix has %i times higher resolution than the Meep grid)." %(resolution_factor,resolution_factor))
        meep_resolution = meep_volume.a
        material_matrix =  simul_volume.get_material_dataset_window(meep_resolution * resolution_factor)
        #convert the material matrix to a matrix with epsilon values (doubles)
        from pysics.materials.electromagnetics import transform_material_stack_matrix_in_effective_index_epsilon_matrix
        self.material_eps_matrix = transform_material_stack_matrix_in_effective_index_epsilon_matrix(material_matrix, simul_volume.geometry.material_stack_factory)
        self.set_matrix_2D(self.material_eps_matrix, meep_volume, resolution_factor)
        LOG.debug("Meep node %i -MeepMaterial2D (epsilon) object initialized." %int(Meep.my_rank()))

    def __getstate__(self): #for pickle : do not serialize
        return None


class __MeepMaterialPolygons__(object):  
    def __init__(self):
        self.south_west_coord = 0.0

    def __getstate__(self): #for pickle : do not serialize
        return None    

    def __transform_coords_to_numpy_array(self, coords):
        transformed_coords = []
        for c in coords :
            x = c[0] - self.south_west_coord[0]
            y = c[1] - self.south_west_coord[1]
            transformed_coords.append([x,y])
        arr = numpy.array(transformed_coords)
        arr = arr[:-1]
        return arr

    def __add_bitmap_polygon__(self, bitmap_polygon, value):
        #value : will be an eps for 2D and a material stack ID for 3D...
        if not (bitmap_polygon is None):
            georep = bitmap_polygon.georep_list
            for g in georep:
                if not g.is_empty:
                    if g.is_ring:
                        coords = g.boundary.coords			
                        coords_array = self.__transform_coords_to_numpy_array(coords)								
                        self.add_polygon(coords_array, value)		    
                    else:
                        outer_polygon_coords_array = self.__transform_coords_to_numpy_array(g.exterior.coords)
                        outer_polygon = self.add_polygon(outer_polygon_coords_array, value)
                        for ip in g.interiors:
                            #inner polygons
                            inner_polygon_coords_array = self.__transform_coords_to_numpy_array(ip.coords)
                            outer_polygon.add_inner_polygon(inner_polygon_coords_array)		


class MeepMaterial2DPolygons(__MeepMaterialPolygons__, Meep.PolygonCallback2D):  
    def __init__(self,  simul_volume, meep_volume):
        Meep.PolygonCallback2D.__init__(self)
        if not isinstance(simul_volume, __SimulationVolume__):
            raise AttributeException("Parameter simul_volume of class MeepMaterial2DPolygons must be of type __SimulationVolume__")
        bitmap_polygons = simul_volume.geometry.material_stacks_shapely_polygons
        self.south_west_coord = simul_volume.size_info.south_west
        for material_stack_id, bitmap_polygon in bitmap_polygons[1:]: #ignore canvas polygon
            eps = simul_volume.geometry.material_stack_factory[material_stack_id].effective_index_epsilon
            self.__add_bitmap_polygon__(bitmap_polygon, eps)



class MeepMaterial3DPolygons(__MeepMaterialPolygons__, Meep.PolygonCallback3D):  
    def __init__(self,  simul_volume, meep_volume):
        Meep.PolygonCallback3D.__init__(self)
        if not isinstance(simul_volume, __SimulationVolume__):
            raise AttributeException("Parameter simul_volume of class MeepMaterial2DPolygons must be of type __SimulationVolume__")
        bitmap_polygons = simul_volume.geometry.material_stacks_shapely_polygons
        self.south_west_coord = simul_volume.size_info.south_west
        self.add_material_stacks_from_numpy_matrix(simul_volume.geometry.material_stack_factory.get_numpy_matrix_representation_of_all_material_stacks(),
                                                   simul_volume.geometry.material_stack_factory.get_number_of_material_stacks_in_store())
        for material_stack_id, bitmap_polygon in bitmap_polygons[1:]: #ignore canvas polygon
            self.__add_bitmap_polygon__(bitmap_polygon, material_stack_id)



class AmplitudeFactor(Meep.Callback):
    def __init__(self,  source):
        Meep.Callback.__init__(self)
        self.source = source

    def complex_vec(self,vec):
        #BEWARE, these are coordinates RELATIVE to the source center !!!!
        try:
            x = vec.x()
            y = vec.y()
            factor = self.source.get_amplitude_factor(Coord2(x,y))	
            LOG.debug("Meep node %i -Amplitude factor for x=%f - y=%f is: %f \n" %(int(Meep.my_rank()),x,y, factor) )
            if (isinstance(factor, complex)):
                return factor
            else:
                return complex(factor)
        except Exception, e:
            print "Exception in AmplitudeFactor::complex_vec (%f,%f): %s" %(x,y,e)
            raise e

    def __getstate__(self): #for pickle : do not serialize
        return None	

# ------------------------------------------------------------

class MeepSimulationEngine(FDTDEngine):
    use_averaging = BoolProperty(default=True, doc="Use subpixel averaging in Meep.")
    is_nonlinear = BoolProperty(default=False, doc="When True, use nonlinear chi3. Default False.")

    # FIXME: Make more general. Problem is you cannot pass a symmetry-instance because it needs the volume, which is generated inside initialize_engine
    symmY = BoolProperty(default=False, doc="Use symmetry in Y-direction? Default = False (no symmetry). See python-meep doc.")    

    def initialise_engine(self, landscape):
        '''Initializes the Meep simulation engine. Parameter is a reference to the simulation landscape (object of type runtime.basic.SimulationLandscape) .'''	
        self.node_nr = int(Meep.my_rank())
        LOG.debug("Meep node %i -Defining the landscape in Meep..." %(self.node_nr))
        if not isinstance(landscape, SimulationLandscape):
            raise InvalidArgumentException("Invalid argument for function setLandscape:: not of type runtime.basic.SimulationLandscape.")
        self.landscape = landscape
        Meep.use_averaging(self.use_averaging) 
        Meep.quiet(False)

        LOG.debug("Meep node %i -Defining material..." %(self.node_nr))	
        [self.meepVol, self.dim] = self.__createMeepComputationalVolume(landscape.simulation_volume)
        if self.dim == 2:
            try:
                self.material = MeepMaterial2DPolygons(landscape.simulation_volume, self.meepVol)
            except Exception, err:
                LOG.error("MeepMaterial2DPolygons gives errors -> using MeepMaterial2DMatrix instead...") 
                self.material = MeepMaterial2DMatrix(landscape.simulation_volume, self.meepVol)
        else: #dim == 3
            self.material = MeepMaterial3DPolygons(landscape.simulation_volume, self.meepVol)

        Meep.set_EPS_Callback(self.material.__disown__())
        LOG.debug("Meep node %i -Defining structure..." %(self.node_nr))

        symmetry_object = Meep.identity()
        if( self.symmY ):
            LOG.debug("Meep node %i -Using y symmetry!" %(self.node_nr))
            symmetry_object = Meep.mirror(Meep.Y,self.meepVol)
            symmetry_object = symmetry_object * complex(1.0,0.0)

        # When there is a certain PML direction, use that one.
        if isinstance( landscape.pml_direction, str ):
            dirint = 'XYZ'.rfind(str.upper(landscape.pml_direction))
            assert dirint<=0, 'PML direction should be either X, Y or Z'
            if dirint == 0: direction = Meep.X
            if dirint == 1: direction = Meep.Y
            if dirint == 2: direction = Meep.Z
            pml = Meep.pml(landscape.pml_thickness, direction)
        else:
            pml = Meep.pml(landscape.pml_thickness)

        self.structure = Meep.structure(self.meepVol , Meep.EPS, pml, symmetry=symmetry_object )
        if self.is_nonlinear:
            LOG.debug("Meep node %i, setting chi3"%(self.node_nr))
            self.chi3 = MeepChi3_2D(landscape.simulation_volume, self.meepVol)
            Meep.set_CHI3_Callback(self.chi3.__disown__())
            self.structure.set_chi3(CHI3)

        LOG.debug("Meep node %i -Defining fields..." %(self.node_nr))
        self.meep_fields = Meep.fields(self.structure)	
        for src in landscape.sources:
            self.__addMeepSource(src, self.meep_fields)
        for c in landscape.datacollectors:
            if isinstance(c, Fluxplane):
                self.__addMeepFluxplane(c, self.meep_fields)
            elif isinstance(c, Probingpoint):
                c.fieldValueCallback = lambda pComp : self.getFieldAmplitudeAtMonitorPoint(c.point, pComp)	
        LOG.debug("Meep node %i -Meep engine initialised!" %(self.node_nr))

    def __createMeepComputationalVolume(self, volume):
        '''Convert the simulation volume (runtime.basic.__SimulationVolume__) into a Meep computational volume'''
        if not isinstance(volume, __SimulationVolume__):
            raise InvalidArgumentException("Invalid argument:: not of type runtime.basic.__SimulationVolume__")	   
        if isinstance(volume, SimulationVolume3D):
            return [ Meep.vol3d(volume.window_width, volume.window_height, volume.size_z, self.resolution), 3 ]
        if isinstance(volume, SimulationVolume2D):
            return [ Meep.vol2d(volume.window_width, volume.window_height, self.resolution), 2 ]
        if isinstance(volume, SimulationVolume1D):
            return [ Meep.vol1d(volume.window_width, self.resolution), 1 ]

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
            z = round(c.z, accuracy)	    
            return (x, y, z) 
        elif (self.dim == 2):
            y = round(c.y, accuracy)
            return (x, y)
        elif (self.dim == 1):
            return (x)	

    def __make_meep_vec__(self, coord):
        '''Convert a Coord3 object into a Meep vec object'''
        if (self.dim == 3):
            (x,y,z) = self.__calc_meep_coord__(coord)
            return Meep.vec(x, y, z)
        elif (self.dim == 2):
            (x,y) = self.__calc_meep_coord__(coord)
            return Meep.vec(x, y)
        elif (self.dim == 1):
            (x) = self.__calc_meep_coord__(coord)
            return Meep.vec(x) 
        else:
            raise PythonSimulateException("Invalid value for self.dim : expected 1, 2 or 3. The value is : %s" %str(self.dim))

    def __makeMeepComponent(self, comp):
        if comp == compEx:
            return Meep.Ex
        elif comp == compEy:
            return Meep.Ey
        elif comp == compEz:
            return Meep.Ez
        elif comp == compHx:
            return Meep.Hx
        elif comp == compHy:
            return Meep.Hy
        elif comp == compHz:
            return Meep.Hz
        raise PythonSimulateException("Unknown component. Must be Ex, Ey, Ez, Hx, Hy or Hz.")

    def __addMeepSource(self, src, meep_fields):	
        '''Convert a source (runtime.basic.__EMSource__) into a Meep source and add it to the Meep fields object'''
        if not isinstance(src, __EMSource__):
            raise InvalidArgumentException("Invalid argument:: not of type runtime.basic.__EMSource__")	   	
        LOG.debug("Meep node %i -Adding source...." %(self.node_nr))
        #create Meep source object
        meepSource = None
        center_freq = 1.0 / (float(src.center_wavelength) / 1000.0)
        if isinstance(src, __GaussianSource__):
            pw = ( (float(src.pulse_width)/1000.0) / (float(src.center_wavelength)/1000.0) ) * center_freq 
            meepSource = Meep.gaussian_src_time(center_freq, pw)
        if isinstance(src, __ContinuousSource__):
            meepSource = Meep.continuous_src_time(center_freq, src.smoothing_width, src.start_time, src.stop_time, src.cutoff)
        #create Meep component
        meepComp = self.__makeMeepComponent(src.field_component)
        #add source to the Meep field
        if isinstance(src, __EMPointSource__):
            vec = self.__make_meep_vec__(src.point)	    
            meep_fields.add_point_source(meepComp, meepSource, vec)
            print "Point source at point (%f , %f)" %(vec.x(), vec.y())	
        elif isinstance(src, __EMVolumeSource__):
            vec1 = self.__make_meep_vec__(src.south)
            vec2 = self.__make_meep_vec__(src.north)	    
            LOG.debug("Meep node %i -Creating volume for source plane..." %(self.node_nr))	    
            meepSrcVol = Meep.volume(vec1, vec2)
            print "Meep node %i - source plane between points (%f , %f) and (%f , %f)." %(self.node_nr, vec1.x(), vec1.y(), vec2.x(), vec2.y())	
            LOG.debug("Meep node %i -Now adding the volume source to Meep..." %(self.node_nr))
            if isinstance(src, __AmplitudeShapedSource__):
                ampl = AmplitudeFactor(source = src)
                Meep.set_AMPL_Callback(ampl.__disown__())
                meep_fields.add_volume_source(meepComp, meepSource, meepSrcVol, Meep.AMPL)
            else:
                meep_fields.add_volume_source(meepComp, meepSource, meepSrcVol, src.amplitude)
        else:
            raise NotImplementedException("Unexpected case in MeepSimulationEngine::__addMeepSource")

    def __addMeepFluxplane(self, flx, meep_fields):
        '''Convert a fluxplane (runtime.basic.Fluxplane) into a Meep fluxplane and add it to the Meep fields object'''	
        if not isinstance(flx, Fluxplane):
            raise InvalidArgumentException("Invalid argument:: not of type runtime.basic.Fluxplane")	  
        LOG.debug("Meep node %i -Creating Meep volume object for the flux plane..." %(self.node_nr))
        vec1 = self.__make_meep_vec__(flx.north)
        vec2 = self.__make_meep_vec__(flx.south)
        print "Meep node %i : flux plane between points (%f , %f) and (%f , %f) " %(self.node_nr, vec1.x(), vec1.y(), vec2.x(), vec2.y())	
        meepFlxVol = Meep.volume(vec1,vec2)
        center_freq = 1.0 / (float(flx.center_wavelength) / 1000.0)
        pw = ( (float(flx.pulse_width)/1000.0) / (float(flx.center_wavelength)/1000.0) ) * center_freq 	
        max_freq = center_freq + pw / 2.0
        min_freq =  center_freq - pw / 2.0
        LOG.debug("Meep node %i -Now adding the fluxplane to the Meep field..." %(self.node_nr))	
        meepFluxplane = meep_fields.add_dft_flux_plane(meepFlxVol, min_freq, max_freq, flx.number_of_sampling_freq )
        flx.flux_per_freq_callback = lambda : Meep.getFluxData(meepFluxplane)
        setattr(flx, "save_hdf5", lambda fn: self.__saveFluxToHDF5(meepFluxplane, fn) )
        setattr(flx, "scale", lambda factor: self.__scaleFluxplane(meepFluxplane, factor) )
        setattr(flx, "load_hdf5", lambda fn: self.__loadFluxFromHDF5(meepFluxplane, fn) )
        LOG.debug("Meep node %i -initializeing the fluxplane ..." %(self.node_nr))	
        flx.initialize()
        LOG.debug("Meep node %i - done with fluxplane ..." %(self.node_nr))

    def __saveFluxToHDF5(self, pFluxplane, filename):
        LOG.debug("Meep node %i -Saving flux to HDF5 in file %s ..." %(self.node_nr,filename))
        pFluxplane.save_hdf5(self.meep_fields, filename)
        return None

    def __loadFluxFromHDF5(self, pFluxplane, filename):
        LOG.debug("Meep node %i -Loading initial values for fluxplane from HDF5 file %s..." %(self.node_nr,filename))
        pFluxplane.load_hdf5(self.meep_fields, filename)
        return None    

    def __scaleFluxplane(self, pFluxplane, pScalefactor):
        LOG.info("Scaling fluxplane with factor %f ...." %pScalefactor)
        pFluxplane.scale_dfts(pScalefactor)
        return None

    def exportDielectricH5(self, fileName = None):
        '''Export the dielectric to a HDF5 output file'''
        if (fileName == None):
            fileName = "meep_eps.h5"
        LOG.debug("Meep node %i -Exporting dielectric to H5-file : %s" %(self.node_nr,fileName))   
        dielectric_file_handle =  Meep.prepareHDF5File(fileName)
        self.meep_fields.output_hdf5(Meep.Dielectric, self.meepVol.surroundings(), dielectric_file_handle)   
        self.closeHDF5File(dielectric_file_handle)
        LOG.debug("Meep node %i -Export to HDF5 done." %(self.node_nr))

    def save_dielectricum_image(self, filename = None):
        #prepare the filename for the export to HDF5
        if (filename is None):
            filename = self.landscape.simulation_id+"_Eps.h5"
        #let Meep export the dielectricum to HDF5
        self.exportDielectricH5(filename)	
        if (Meep.am_master()):	
            LOG.debug("Meep node %i -Dielectricum saved to file %s..." %(self.node_nr,filename))
            if self.dim == 2:
                cmd = "h5topng -a /home/emmanuel/workspace/Meep_tutorial/colormaps/yarg "+filename
                os.system(cmd)	
        return filename

    def get_material_dataset(self):	
        '''Get a dataset with the EPS values of the dielectric, as it was processed by the Meep engine  (i.e. reverse loaded from a HDF5 file) '''
        #check that the dimension of the dataset that we receive match what we expect
        #what values are we expecting for the dimensions of the HDF5 dataset...
        d = numpy.array([self.landscape.simulation_volume.window_width, self.landscape.simulation_volume.window_height])
        epsDim = numpy.floor(d * self.resolution)
        #let Meep export the dielectricum to HDF5, then read this file and visualize (this is a crosscheck over direct plotting of the epsilon values from the SimulationVolume object)
        h5FileName = self.generate_material_hdf5()
        f = h5py.File(h5FileName, 'r')
        #check that the dimension of the dataset that we receive match what we expect
        ds = f.items()[0][1]
        if (abs(ds.shape[0] - epsDim[0]) > 1) or (abs(ds.shape[1] - epsDim[1]) > 1) :
            raise PythonSimulateException("MeepSimulationEngine::visualizeDielectric - invalid dimension of HDF5 data. Expected %s and got %s" %(str(tuple(epsDim)), str(ds.shape) ))
        #create a matrix with Material objects that will hold the epsilon
        x_range = ds.shape[0]
        y_range = ds.shape[1]
        mat = numpy.zeros((x_range, y_range), Material)
        for x in range(0,x_range):
            for y in range(0,y_range):
                mat[x,y] = Material(name = "dielectricum_material", epsilon = ds[x, y])
        return mat

    def getFieldAmplitudeAtMonitorPoint(self, pCoord, pComp):
        '''Get the value of the field at a certain coordinate and for a certain electromagnetic component'''
        if (self.meep_fields == None):
            raise PythonSimulateException("MeepSimulationEngine::getFieldAtMonitorPoint - call initialise_engine first.")
        m = Meep.monitor_point()
        p = self.__make_meep_vec__(pCoord)
        c = self.__makeMeepComponent(pComp)
        self.meep_fields.get_point(m, p)
        f = m.get_component(c)
        return math.sqrt( (f.real * f.real) + (f.imag * f.imag) )

    def prepareHDF5File(self, filename):
        '''Prepare a HDF5 file for output'''
        LOG.debug("Meep node %i -Preparing HDF5 file '%s'..." %(self.node_nr, filename))
        f = open(filename, 'w')
        f.close()
        h5f = Meep.h5file(filename, Meep.h5file.READWRITE)	
        return h5f

    def writeFieldsToHDF5File(self, pFileRef, pComp, surroundings = None):
        '''Write the given component of the fields to HDF5 file'''
        #LOG.debug("Meep node %i -Writing fields to HDF5 ..." %(self.node_nr)) #comment because it interferes with stdout
        if pFileRef == None:
            raise PythonSimulateException("MeepSimulationEngine::getFieldAtMonitorPoint - call prepareHDF5File first.")	
        c = self.__makeMeepComponent(pComp)
        if surroundings == None:
            surroundings = self.meepVol.surroundings()
        self.meep_fields.output_hdf5(c, surroundings, pFileRef, 1)	

    def closeHDF5File(self, pFileRef):
        '''Close the HDF5 file'''
        if (Meep.am_master()):	
            LOG.debug("Meep node %i - Closing HDF5 file..." %(self.node_nr))	
            if pFileRef == None:
                raise PythonSimulateException("MeepSimulationEngine::getFieldAtMonitorPoint - call prepareHDF5File first : cannot close a file that is not open.")	
            del(pFileRef)

    def step(self):
        self.meep_fields.step()

    def __getstate__(self): #for pickle : do not serialize
        d = dict()
        d["resolution"] = self.resolution
        d["use_averaging"] = self.use_averaging
        d["is_nonlinear"] = self.is_nonlinear
        d["symmY"] = self.symmY
        return d

    def __setstate__(self, d):
        self.__store__ = dict()
        self.flag_busy_initializing = True
        self.resolution = d["resolution"]
        self.use_averaging = d["use_averaging"]
        self.is_nonlinear = d["is_nonlinear"]
        self.symmY = d["symmY"]
        self.flag_busy_initializing = False



class LowLevelPythonMeepProcedure(FDTDFieldCalculationProcedure): 
    stopcriterium = LockedProperty()

    def make_meep_vec(self, coord):
        return self.engine.__make_meep_vec__(coord)

    def run(self):
        self.engine.initialise_engine(self.landscape)
        self.save_engine_dielectricum_to_file()	
        #use should inherit from this class and complement the run-method with low-level python-meep commands...



