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
from pysimul.runtime.basic import *
from pysimul.runtime.procedure import *
import cPickle
import glob


__all__ = ['SimulationDefinition']


class SimulationDefinition(StrongPropertyInitializer):	
	simul_params = RestrictedProperty(default = dict(), restriction = RestrictType(dict), doc = "A set of parameters for the simulation")    
	landscape = DefinitionProperty(fdef_name="define_landscape") 
	procedure = DefinitionProperty(fdef_name="define_procedure") 
	saveDatacollectorsImageToFileFunction = DefinitionProperty(fdef_name="define_SaveDatacollectorsImageToFileFunction") 
		
	def save_default_landscape_to_file(self, filename = None):
		'''create an image of the landscape in accord with the default parameter values and save it to file'''
		if filename == None:
			filename =  "./%s_default_landscape.pysimul.png" %self.landscape.simulation_id
		self.procedure.visualizeLandscapeToFile(filename)
		return filename

	def __str__(self):
		s = self.landscape.simulation_id 
		return s
	
	def __get_default_filename_without_extension(self):
		return self.__str__() 
	
	def define_landscape(self):
		raise NotImplementedException("Implement this function by returning an object of type SimulationLandscape")

	def define_procedure(self):
		raise NotImplementedException("Implement this function by returning an object of type SimulationProcedure")
	
	def __cleanUpFiles(self):
		'''clean up older files that could possibly exist for an earlier run of this simulation'''
		for f in glob.glob('./%s*' %self.__get_default_filename_without_extension()):
			os.remove(f)
	
	def persist_to_file(self, filename = None):
		'''serialize a SimulationDefinition to file'''
		self.__cleanUpFiles()
		self.landscape.set_default_filename_without_extension(self.__get_default_filename_without_extension())		
		if filename == None:
			filename = self.__get_default_filename_without_extension()+ '.def.pysimul'	
		f = open(filename, 'wb')
		LOG.debug("Persisting simulation definition to file : %s" %filename)
		cPickle.dump(self,f)
		f.close()
		return filename
		
	def save_datacollectors_to_file(self, filename = None):
		'''save the datacollectors to file and also trigger the function that creates a graph and save this to file'''
		if filename == None:
			filename = self.__get_default_filename_without_extension()		
			filename = filename + '.datacollectors.pysimul'
		f = open(filename, 'wb')
		cPickle.dump(self.landscape.datacollectors,f)
		f.close()		
		self.save_datacollectors_to_file_function(filename+".png")
		
	@classmethod
	def load_from_file(cls,filename):
		'''deserialize a SimulationDefinition from file'''
		LOG.debug("Loading simulation definition from file : %s" %filename)		
		f = open(filename,'rb')
		simul_def = cPickle.load(f)
		f.close()
		return simul_def
	
	