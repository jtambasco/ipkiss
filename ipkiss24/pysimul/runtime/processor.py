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
from ipcore.runtime.processor import __Processor__, __StopCriterium__
from pysimul.runtime.basic import *
from pysimul import *

class SimulationProcessor(__Processor__):
    """Generic processor for one step in a simulation"""

    def initialize(self, engine):
        self.engine = engine	


class FluxSimulationProcessor(__Processor__):
    """Simulation processor that processes fluxes"""

    def initialize(self, landscape):
        self.landscape = landscape    


class FieldPropagationSimulationProcessor(__Processor__):
    """Simulation processor for treating the propagation of the fields """

    def initialize(self, engine):
        self.engine = engine


class SaveFieldsHDF5Processor(FieldPropagationSimulationProcessor):
    """In every step, append the fields to a HDF5 file"""

    fileName = RestrictedProperty(default="fields.h5", restriction = RESTRICT_STRING, doc = "HDF5 filename where to save the fields to")
    H5OutputIntervalSteps = RestrictedProperty(default = 25, restriction = RESTRICT_INT, doc = "Interval for output to HDF5 (default : every 25 steps)")
    field_component = RestrictedProperty(required = True, restriction = RestrictType(FieldComponent), doc = "The field component which must be exported")
    stepsCount = RestrictedProperty(default = 0, restriction = RESTRICT_INT, doc = "Counter for the steps (not to be set by the user ; for use by other objects such as the stopcriterium)")    
    surroundings = RestrictedProperty(default = None, doc = "Surroundings of the box. (meep.vol2d(...).surroundings()")

    def __init__(self, **kwargs):
        super(SaveFieldsHDF5Processor, self).__init__(**kwargs)	
        self.stepsCount = 0

    def initialize(self, engine):
        self.engine = engine
        self.h5file = self.engine.prepareHDF5File(self.fileName)

    def finalize(self):
        self.engine.closeHDF5File(self.h5file)
        del(self.h5file)

    def process(self, data = None, **kwargs):
        if (self.stepsCount % self.H5OutputIntervalSteps == 0):
            self.engine.writeFieldsToHDF5File(self.h5file, self.field_component, self.surroundings)
        self.stepsCount  = self.stepsCount  + 1                 


    def __getstate__(self):
        try:
            import meep as Meep
        except:
            try:
                import meep_mpi as Meep
            except:
                print 'Cannot import meep'

        if isinstance(self.surroundings, Meep.volume):
            print 'WARNING: Cannot yet pickle surroundings-instance. (meep.vol2d(...).surroundings'
            print 'This is of type meep.volume; proxy of <Swig Object of type \'meep::volume *\' at 0x31...c0> '
            #self.surroundings = 'surrounding can not yet be pickled correctly'
            ndict = self.__dict__.copy()
            del ndict['__prop_surroundings__']
            return ndict
        else:
            return self.__dict__

    def __setstate__(self, d):
        self.__store__ = dict()
        self.flag_busy_initializing = True	
        self.surroundings = None
        self.__dict__.update(d)
        self.flag_busy_initializing = False	

class RunUntilFieldsDecayedAtProbingPoint(__StopCriterium__):
    """Monitor the field at the specified probing point. Stop when the field has decayed to 0.001 of the peak amplitude"""

    probingpoint = RestrictedProperty(required=True, restriction = RestrictType(Probingpoint), doc= "Reference to the probing point that will be monitored for decay of the field")    
    field_component = RestrictedProperty(required = True, restriction = RestrictType(FieldComponent), doc = "The field component which will be probed")    
    decayedStopAfterStepsInitialValue = RestrictedProperty(default = 50, restriction = RESTRICT_INT, doc = "When the source has decayed, continue for another x timesteps (default: 50)")
    decay_factor = RestrictedProperty(default = 0.001, restriction = RESTRICT_FLOAT, doc = "When the field has decayed with this factor at the probing point, stop the simulation")

    def __init__(self, **kwargs):
        super(RunUntilFieldsDecayedAtProbingPoint, self).__init__(**kwargs)
        self.currAmpl = 0
        self.peakAmpl = 0
        self.avoidEndlessLoopCount = 0

    def evaluateStopCriterium(self):
        #check the current amplitude of the source component
        self.currAmpl = self.probingpoint.collect(self.field_component)
        if self.currAmpl > self.peakAmpl:
            self.peakAmpl = self.currAmpl
        #run for another 50 time steps when the amplitude has decayed to 'decay_factor' of the peak amplitude
        if (self.peakAmpl!=0) and (self.currAmpl / self.peakAmpl)<self.decay_factor:
            if (self.decayedStopAfterSteps % 10 ==0):
                LOG.debug("Source has decayed... counting down... %i\n" %self.decayedStopAfterSteps )
            self.decayedStopAfterSteps  = self.decayedStopAfterSteps  - 1
        else:
            self.decayedStopAfterSteps  = self.decayedStopAfterStepsInitialValue
        #now make a final decision about stopping the simulation or not
        if (self.peakAmpl==0) or (self.currAmpl / self.peakAmpl) > self.decay_factor  or (self.decayedStopAfterSteps > 0):
            return False #continue with the simulation
        else:
            return True #stop the simulation


class StopAfterSteps(__StopCriterium__):

    def __init__(self, maximum_steps = 100):
        self.StepsCount = 0
        self.maximumSteps = maximum_steps

    def __call__(self):
        self.StepsCount = self.StepsCount + 1
        if (self.StepsCount % int (self.maximumSteps / 10.0) == 0):
            print "The simulation is now at step %i" %self.StepsCount
        return self.StepsCount >= self.maximumSteps   



class PersistFluxplanes(FluxSimulationProcessor):
    def initialize(self, landscape):
        self.landscape = landscape

    def process(self, data = None, **kwargs):
        for dc in self.landscape.datacollectors:
            if (isinstance(dc, Fluxplane)):
                charset = "abcdefghijklmnopqrstuvwxyz"
                fn = "fluxplane_" + ''.join([c for c in dc.name.lower() if c in charset])
                dc.collect()
                dc.persist_to_file(filename = fn)



