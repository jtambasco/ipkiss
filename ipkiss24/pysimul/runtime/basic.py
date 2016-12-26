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
from ipkiss.geometry.coord import *
from ipkiss.geometry.size_info import SizeInfoProperty, EMPTY_SIZE_INFO
import numpy
import copy
import os
from pysimul.exc import *
from pysimul.runtime.params import *
from pysics.basics.geometry.geometry import *
from pysics.basics.material.material import Material
from pysimul import LOG
   

# -------------------------------- -------------------------------- --------------------------------


class Axis(StrongPropertyInitializer):
    name = StringProperty(required = True, doc="Plotting name of the axis")
    
    def __init__(self, **kwargs):
	super(Axis, self).__init__(**kwargs)
	
    def __str__(self):
	return self.name

axisX = Axis(name ="X")
axisY = Axis(name ="Y")
axisZ = Axis(name ="Z")

class ElectromagneticFieldType(StrongPropertyInitializer):
    name = StringProperty(required = True, doc="Vectorial component name")
    
    def __init__(self, **kwargs):
	super(ElectromagneticFieldType, self).__init__(**kwargs)    
	
    def __str__(self):
	return self.name	
	
fieldE = 	ElectromagneticFieldType(name = "E")
fieldH = 	ElectromagneticFieldType(name = "H")

class FieldComponent(StrongPropertyInitializer):
    axis = RestrictedProperty(required = True, restriction = RestrictType(Axis), doc = "The axis of the component (X, Y or Z).")
    emType = RestrictedProperty(required = True, restriction = RestrictType(ElectromagneticFieldType), doc = "The type of electromagnetic component (E or H).")    
    
    def __init__(self, **kwargs):
	super(FieldComponent, self).__init__(**kwargs)
	
    def __str__(self):
	s = str(self.emType) + str(self.axis).lower()
	return s
	
    def __eq__(self, other):
	return str(self) == str(other)

compEx = FieldComponent(axis = axisX, emType = fieldE)	
compEy = FieldComponent(axis = axisY, emType = fieldE)
compEz = FieldComponent(axis = axisZ, emType = fieldE)

compHx = FieldComponent(axis = axisX, emType = fieldH)	
compHy = FieldComponent(axis = axisY, emType = fieldH)
compHz = FieldComponent(axis = axisZ, emType = fieldH)


# ------------------------ POLARIZATIONS ------------------------------------------------------------
TM = 0
TE = 1
	
# ------------------------ SOURCES ------------------------------------------------------------------

class __EMSource__(SimulationParameterContainer):
    """Electromagnetic source"""
    
    field_component = RestrictedProperty(required = True, restriction = RestrictType(FieldComponent), doc = "The electromagnetic component of the source")
    name = RestrictedProperty(default="SOURCE", restriction = RESTRICT_STRING, doc = "A user-friendly name assigned to the source")        
    amplitude = RestrictedProperty(default = 1.0, restriction = RESTRICT_NUMBER & RESTRICT_POSITIVE, doc = "Amplitude of the Gaussian source")    
    
    pass
    
class __EMVolumeSource__(SimulationParameterContainer):
    """Electromagnetic volume source"""
    north = RestrictedProperty(required = True, restriction = RESTRICT_COORD3, doc = "Upper left corner of the source plane")
    south = RestrictedProperty(required = True, restriction = RESTRICT_COORD3, doc = "Lower right corner of the source plane")

    pass
		
	
class __EMPointSource__(SimulationParameterContainer):
    """Electromagnetic point source"""
    point= RestrictedProperty(required = True, restriction = RESTRICT_COORD3, doc = "Coordinates of the point source")

    pass
			    
	
class __GaussianSource__(__EMSource__):
    center_wavelength = RestrictedProperty(required = True, restriction = RESTRICT_FLOAT & RESTRICT_POSITIVE, doc = "Center wavelength (in nm) of the gaussian source")
    pulse_width = RestrictedProperty(required = True, restriction = RESTRICT_FLOAT & RESTRICT_POSITIVE, doc = "Width (in nm) of the Gaussian source")    
    
    def __init__(self, **kwargs):
	super(__GaussianSource__, self).__init__(**kwargs)
	
class __ContinuousSource__(__EMSource__):
    center_wavelength = RestrictedProperty(required = True, restriction = RESTRICT_FLOAT & RESTRICT_POSITIVE, doc = "Center wavelength (in nm) of the continuous source")
    smoothing_width = RestrictedProperty(default = 0.0, restriction = RESTRICT_FLOAT & RESTRICT_NONNEGATIVE, doc = "Temporal smoothing width of continuous source (default: 0)")
    cutoff = RestrictedProperty(default = 3.0, restriction = RESTRICT_FLOAT & RESTRICT_NONNEGATIVE, doc = "How many widths the current decays for before we cut it off and set it to zero; the default is 3.0. A larger value of cutoff will reduce the amount of high-frequency components that are introduced by the start/stop of the source, but will of course lead to longer simulation times.")
    start_time = RestrictedProperty(default = 0.0, restriction = RESTRICT_FLOAT & RESTRICT_NONNEGATIVE, doc = "Start time of the continuous source (default: 0)")
    stop_time = RestrictedProperty(default = float('inf'), restriction = RESTRICT_FLOAT & RESTRICT_POSITIVE, doc = "Stop time of the continuous source (default: infinity)")    
    
	
class __AmplitudeShapedSource__(__EMSource__):
    def get_amplitude_factor(self, coordinate):
	raise PythonSimulateException("__AmplitudeShapedSource__ class should implement : get_amplitude_factor")
    	
	
class GaussianPointSource(__EMPointSource__, __GaussianSource__):
    pass
	
class GaussianVolumeSource(__EMVolumeSource__, __GaussianSource__):
    pass
	
class ContinuousPointSource(__EMPointSource__, __ContinuousSource__):
    pass


class ContinuousVolumeSource(__EMVolumeSource__, __ContinuousSource__):
    pass


class AmplitudeShapedContinuousVolumeSource(ContinuousVolumeSource, __AmplitudeShapedSource__):
    pass

    	
# ------------------------------------------------------------------------------------------	    

class __DataCollector__(SimulationParameterContainer):
    name = RestrictedProperty(default="Datacollector", restriction = RESTRICT_STRING, doc = "A user-friendly name assigned to the datacollector")    
    
    def __init__(self, **kwargs):
	super(__DataCollector__, self).__init__(**kwargs)    
	
    def getValue(self):
	return self.callbackForValue()
    

class Fluxplane(__DataCollector__):
    """Plane for incremental capturing of the flux """
    north = RestrictedProperty(required = True, restriction = RESTRICT_COORD3, doc = "Upper left corner of the fluxplane")
    south = RestrictedProperty(required = True, restriction = RESTRICT_COORD3, doc = "Lower right corner of the fluxplane")
    center_wavelength = RestrictedProperty(required = True, restriction = RESTRICT_FLOAT & RESTRICT_NONNEGATIVE, doc = "Center wavelength (in nm) for collecting the flux")
    pulse_width = RestrictedProperty(required = True, restriction = RESTRICT_FLOAT & RESTRICT_NONNEGATIVE, doc = "Wavelength width (in nm) for collecting the flux")    
    number_of_sampling_freq = RestrictedProperty(required = True, restriction = RESTRICT_INT & RESTRICT_NONNEGATIVE, doc = "Number of discrete sampling frequencies to monitor the flux")   
    flux_per_freq_callback = lambda : 0  #callback function (probably to the engine), to get the flux values. To be set upon initialisation
    flux_per_freq = RestrictedProperty(default = [[],[]], restriction = RestrictType(list), doc = "the flux per frequency that was collected during the simulation")   
    init_hdf5 = StringProperty(default=None, doc = "The name of a HDF5 file from which to load initial values of the flux")        
	
    def initialize(self):
	if not (self.init_hdf5 is None):
	    self.load_hdf5(self.init_hdf5)
	
    def collect(self):
	self.flux_per_freq = self.flux_per_freq_callback()	
	return self.flux_per_freq
    
    def persist_to_file(self, filename = None):
	if (filename == None):
	    filename = "fluxplane_%s_%s.pickle" %(self.north, self.south)
	f = open(filename, 'wb')
	LOG.debug("Persisting Fluxplane to file : %s" %filename)
	import cPickle
	cPickle.dump(self,f)
	f.close()	  	
    
    def save_hdf5(self, filename):
	raise NotImplementedException("No default implementation. Can be set with an engine-specific implementation upon initialisation.")

    def load_hdf5(self, filename):
	raise NotImplementedException("No default implementation. Can be set with an engine-specific implementation upon initialisation.")
    
    def scale(self, pScalefactor):
	raise NotImplementedException("No default implementation. Can be set with an engine-specific implementation upon initialisation.")    

    def __getstate__(self):
	#pickle cannot serialize lambda functions
	self.flux_per_freq_callback = None
	self.save_hdf5 = None
	self.load_hdf5 = None
	self.scale = None
	return self.__dict__
    
	
class Probingpoint(__DataCollector__):
    """Probing point where the field is monitored """
    point =  RestrictedProperty(required = True, restriction = RESTRICT_COORD3, doc = "The coordinates of the probing point")
    fieldValueCallback = lambda : 0   #callback function (probably to the engine), to get the field value at this probing point. To be set by the engine upon initialisation
    
    def collect(self, pComp):
	'''Collect the value of the field at the probing point for the specified component'''
	cf = self.fieldValueCallback
	f = cf(pComp)
	return f	
    
    def __getstate__(self):
	#pickle cannot serialize lambda functions
	self.fieldValueCallback = None
	return self.__dict__   
    
# ------------------------------------------------------------------------------------------	    	
	
class __SimulationVolume__(SimulationParameterContainer):
    material_dataset = DefinitionProperty(fdef_name = "get_material_dataset")           
    geometry = DefinitionProperty(fdef_name = "define_geometry")       
   
    def get_material_dataset(self, resolution = 1.0):	
	'''Get a dataset with the material at every coordinate in the simulation volume'''
	raise NotImplementedException("Abstract class :: please implement 'get_material_dataset' in your subclass.")

    def get_dimensions(self):
	'''Return a numpy array with the size dimensions of the dielectric'''
	raise NotImplementedException("Abstract class :: please implement 'get_dimensions' in your subclass.")    
    
    
class SimulationVolume1D(CartesianGeometry1D, __SimulationVolume__):
    window_size_info = SizeInfoProperty(default = EMPTY_SIZE_INFO)
    window_width = FunctionNameProperty(fget_name="get_window_width")
    
    def get_dimensions(self):
	'''Return a numpy array with the size dimensions of the dielectric'''
	return numpy.array([self.width])
    
    def get_material_dataset(self, resolution = 1.0):	
	'''Get a dataset with the material on each coordinate'''
	raise  NotImplementedException("To be implemented by subclass.")   
    
    def get_window_width(self):
	if (self.has_window_defined()):
	    return self.window_size_info.width
	else:
	    return self.width
    
    def has_window_defined(self):
	if (not (self.window_size_info is None)) and (self.window_size_info != EMPTY_SIZE_INFO):
	    return True
	else:
	    return False    
	
    def get_material_dataset_window(self, resolution = 1.0):	
	if not self.has_window_defined() :
	    return self.get_material_dataset(resolution)   
	else:
	    raise  NotImplementedException("To be implemented by subclass.")   	
    
    
	
class SimulationVolume2D(CartesianGeometry2D, SimulationVolume1D):
    window_height = FunctionNameProperty(fget_name = "get_window_height")
    
    def get_dimensions(self):
	'''Return a numpy array with the size dimensions of the dielectric'''	
	return numpy.array([self.width, self.height])
    	
    def get_window_height(self):    
	if (self.has_window_defined()):
	    return self.window_size_info.height
	else:
	    return self.height
            
    def get_material_dataset(self, resolution):
	x_range = numpy.arange(0, numpy.ceil(self.width*resolution))
	y_range = numpy.arange(0, numpy.ceil(self.height*resolution))	
	mat = numpy.zeros([len(x_range), len(y_range)], Material)
	for x in x_range:
	    for y in y_range:
		x_co = float(x) / float(resolution)
		y_co = float(y) / float(resolution)
		mat[x,y] = self.get_material(Coord3(x_co,y_co,0))
	return mat
 

    
class SimulationVolume3D(CartesianGeometry3D, SimulationVolume2D):  
    window_thickness = FunctionNameProperty(fget_name = "get_window_thickness")    
    
    def get_dimensions(self):
	'''Return a numpy array with the size dimensions of the dielectric'''	
	return numpy.array([self.width, self.height, self.thickness])
    
    def get_material_dataset(self, resolution = 1.0):	
	'''Get a dataset with the material on each coordinate'''
	raise  NotImplementedException("To be implemented by subclass.")  
    
    def get_window_thickness(self):    
	raise  NotImplementedException("To be implemented by subclass.")	
    
    	
# ------------------------------------------------------------------------------------------	

def NOVISUALISATION_FUNCTION():
    pass
    
class SimulationLandscape(SimulationParameterContainer):
    """ The landscape describing the simulation (sources, material, flux planes, etc..)"""
    simulation_volume = RestrictedProperty(required=True, restriction = RestrictType(__SimulationVolume__), doc = "The simulation volume.") 
    sources = RestrictedProperty(required=True, restriction = RestrictTypeList(__EMSource__), doc = "A list of electromagnetic sources.") 
    datacollectors = RestrictedProperty(required=True, restriction = RestrictTypeList(__DataCollector__), doc = "A list of datacollectors (e.g. fluxplanes, monitoring points,...).") 
    pml_thickness = RestrictedProperty(default = 0.0, restriction =  RESTRICT_FLOAT, doc = "Specification of the perfectly matching layer (PML) on the boundaries, if any. Set to 0 if no PML.") 
    pml_direction = RestrictedProperty(default = None, restriction = RESTRICT_CHAR, doc = "When specified, only one pml-direction is used" )
    simulation_id = RestrictedProperty(required=True, restriction =  RESTRICT_STRING, doc = "A unique ID identifying the simulation.") 
    visualize_datacollectors_to_file_function = CallableProperty(default = NOVISUALISATION_FUNCTION, doc="function which creates a plot of the data in the datacollectors and saves this to file (parameter : filename)")    
	
    def __str__(self):
	return self.simulation_id

    def __repr__(self):
	return self.simulation_id
    
    def get_dimensions(self):
	'''Return a numpy array with the size dimensions of the dielectric'''	
	return self.simulation_volume.get_dimensions()
    
    def get_material_dataset(self, resolution = None):	
	'''Get a dataset with the EPS values of the dielectric'''
	return self.simulation_volume.get_material_dataset(resolution = resolution)
    
    def visualize_datacollectors_to_file(self, filename = None):
	'''Calls the user defined function, which creates a plot of the data in the datacollectors and saves this to file'''
	if filename == None:
	    try:
		filename = self.default_filename_without_extension + ".datacollectors.pysimul.png"
	    except Exception,e :
		raise PythonSimulateException("Could not find a default filename for the 'visualizeDatacollectorsToFile' function. Fatal error.")	    
	if not os.path.isfile(filename):
	    self.visualize_datacollectors_to_file_function(filename)	
	    
    def set_default_filename_without_extension(self, filename):
	self.default_filename_without_extension = filename
	


