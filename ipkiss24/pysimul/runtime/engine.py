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
from ipcore.runtime.processor import __Processor__
from ipcore.runtime.procedure import __Procedure__
from pysimul.runtime.basic import *
from ipcore.exceptions.exc import *

class __SimulationEngine__(StrongPropertyInitializer):
    """Generic engine for a simulation"""    

	
    def initialise_engine(self, pLandscape):
	'''Initializes the  simulation engine. Parameter is a reference to the simulation landscape. To be implemented by subclasses.'''
	if not isinstance(pLandscape, SimulationLandscape):
	    raise InvalidArgumentException("Invalid argument for function setLandscape:: not of type runtime.basic.Landscape.")
	          
    def get_procedure_class(self):
	raise NotImplementedException("get_procedure_class not implemented in class __SimulationEngine__")
    

class FDTDEngine(__SimulationEngine__):
    resolution = RestrictedProperty(required=True, restriction = RESTRICT_INT & RESTRICT_POSITIVE, doc= "Resolution of the FDTD simulation")
    

    def exportDielectricH5(self, fileName = None):
	'''Export the EPS values of the dielectric to a HDF5 output file'''
	raise NotImplementedException("exportDielectricH5 not implemented in class FDTDEngine")
    
    def get_material_dataset(self):	
	'''Get a dataset with the EPS values of the dielectric, as it was processed by the engine '''
	raise NotImplementedException("get_material_dataset not implemented in class FDTDEngine")
    
    def getFieldAmplitudeAtMonitorPoint(self, pCoord, pComp):  
	'''Get the amplitude of the given component of the field at the given monitoring point'''
	raise NotImplementedException("getFieldAmplitudeAtMonitorPoint not implemented in class FDTDEngine")

    def step(self):	
	'''Perform a step in the simulation'''
	raise NotImplementedException("step not implemented in class FDTDEngine")
        
    def prepareHDF5File(self, filename):
	raise NotImplementedException("prepareHDF5File not implemented in class FDTDEngine")
    
    def writeFieldsToHDF5File(self, pFileRef, pComp):
	raise NotImplementedException("writeFieldsToHDF5File not implemented in class FDTDEngine")
    
    def closeHDF5File(self, pFileRef):
	raise NotImplementedException("closeHDF5File not implemented in class FDTDEngine")
    
    def get_procedure_class(self):
	from pysimul.runtime.procedure import FDTDFieldCalculationProcedure
	return FDTDFieldCalculationProcedure
    

    
class ModeSolverEngine(__SimulationEngine__):

    def mode_profile_of_port(self, port):	
	raise NotImplementedException("mode_profile_of_port not implemented in abstract superclass ModeSolverEngine")	

    def get_procedure_class(self):
	from pysimul.runtime.procedure import ModeSolverFieldCalculationProcedure
	return ModeSolverFieldCalculationProcedure
