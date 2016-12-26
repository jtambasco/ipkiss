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
import inspect
from pysimul.exc import *
import hashlib

__all__ = ['SimulationParameterContainer']


class SimulationParameterContainer(StrongPropertyInitializer):
	
	def __set_properties__(self, obj, kwargs):
		props = obj.__unlocked_properties__()
		kwargs_to_assign = dict()
		for name,val in kwargs.items():
			if name in props:
				kwargs_to_assign[name] = val
		obj.__assign_properties__(kwargs_to_assign)
			

        def __init__(self, **kwargs):
                #if a keyword argument 'simul_params' is provided, then expand it into a list of keyword arguments and join it with the current keyword arguments    
                if 'simul_params' in kwargs:		    
                        p = kwargs['simul_params']
			if "component" in p:
				p["structure"] = p["component"]
				del p["component"]
				from pysimul.log import PYSIMUL_LOG as LOG
				LOG.deprecation_warning("Please switch the name of simulation parameter 'component' to 'structure'.",3)	 			
			if (not isinstance(p, dict)):
				raise PythonSimulateException("Keyword argument 'simul_params' must be of type 'dict'. Current type is : '%'" %type(p))
			props = self.__unlocked_properties__()
                        for name, val in p.items():				
				if isinstance(val, SimulationParameterContainer):
					self.__set_properties__(val, p)
				elif isinstance(val, list):
					for v in val:
						if isinstance(v, SimulationParameterContainer):
							self.__set_properties__(v, p)
				if name in props:
					kwargs[name] = val
                        del kwargs['simul_params']						
                super(SimulationParameterContainer, self).__init__(**kwargs)


