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

from technologies.si_photonics.picazzo.default import *
from ipkiss.all import *
from numpy import*
from ipkiss.plugins.simulation import *
from dependencies.matplotlib_wrapper import *
from ipkiss.technology.technology import TechnologyTree
from mmi_awg import * #see folder trunk/samples/pysimul/awg_aperture_camfr

#create an instance of the MMIAWG for which we want to simulate the aperture
awg = MyMMIAWG(name = "MMI_AWG", N_arms = 9,
                        star_coupler_offset = 160,
                        in_wavelengths = [1.54735],   
                        arm_aperture_width = 2.0,
                        arm_aperture_spacing= 0.2,
                        port_aperture_width = 2.0,
                        port_aperture_spacing = 0.2,
                        N_output_channels = 3,
                        output_channel_spacing = 400,
                        in_port_mmi_width = 5.0,
                        in_port_taper_width = 4.0,
                        in_port_mmi_length = 19.501)			
		
#pick out the aperture
aperture  = awg.star_coupler_in.aperture_in
#export to GDS, just for our reference
aperture.write_gdsii("simul_aperture.gds") 
	
#------------- Simulation with CAMFR----------------------
#create a dictionary with all the simulation parameters
params = dict()
#resolution for matrix discretization, used when interfacing the component's virtually fabricated geometry to CAMFR
params["resolution"] = 50 #this generates quite a large number of slabs, but apparently CAMFR behaves stable...

#define a window spanning the section for which we want to create a CAMFR stack
params["window_size_info"] = SizeInfo(west = -62.301, east = -0.01, south = -2.8, north = 2.8) 
#prepare the CAMFR engine
import camfr 
from pysimul.runtime.camfr_engine.camfr_engine import CamfrEngine		
engine = CamfrEngine()
camfr_technology = TechnologyTree()
camfr_technology.POLARIZATION = camfr.TM # use for top-down simulations 
camfr_technology.NMODES = 10 #we can see convergence when increasing the number of modes to 20, 30, ... : the result doesn't change
camfr_technology.PML =  -0.05
camfr_technology.WAVELENGTH = 1.54735 #wavelength in micrometer
engine.set_camfr_settings(camfr_technology)        
params["engine"] = engine
#set up the simulation
simul_camfr = aperture.create_simulation(simul_params = params)
#run the simulation and extract the fields at x = -0.01 (in the coordinate system of the original component, see the GDS)
f = simul_camfr.procedure.run(field_extraction_geometry_x_positions= [-0.01])
#look in trunk/pysimul_camfr_output for plots of the fields
print "Done with CAMFR simulation"



#------------- Simulation with Meep----------------------
from pysimul.runtime.MeepFDTD import *

#new parameter set
params = dict()
params["resolution"] = 20 #low resolution just for the example 
params["engine"] = MeepSimulationEngine(resolution = params["resolution"])

#add PML of 2 micrometer and grow the component 1 micrometer larger
params["pml_thickness"] = 2.0
params["include_growth"] = 1.0


center_wavelength = 1550.0

params["sources"] = [ModeProfileContinuousSourceAtPort(center_wavelength = center_wavelength, 
                                                       smoothing_width = 60.0,
                                                       port = aperture.west_ports[0],
                                                       mode = 0,
                                                       stop_time = 120.0)]
 
flux_pulse_width = 30.0
params["datacollectors"] = [FluxplaneAtPort(center_wavelength = center_wavelength, 
                                                        pulse_width = flux_pulse_width,
                                                        number_of_sampling_freq = 100,
                                                        port = aperture.west_ports[0],
                                                        name = "Flux at input port"),
                           
                            FluxplaneAtPosition(center_wavelength = center_wavelength, 
                                                        pulse_width = flux_pulse_width,
                                                        number_of_sampling_freq = 100,
                                                        position =(-0.01, 0.0),
                                                        width = 5.0,
                                                        name = "Flux at upper output arm"),
                            ProbingpointAtPosition(point =( -0.01, 0.0))]

#every 100 steps, save the Hz component to file
params["step_processor"] = SaveFieldsHDF5Processor(H5OutputIntervalSteps = 100, field_component = compHz)

#stop when the Hz field component at the probing has decayed to 0.01 of it's peak value
params["stopcriterium"] = RunUntilFieldsDecayedAtProbingPoint(field_component = compHz, probingpoint = params["datacollectors"][2], decay_factor = 0.01)

#when the simulation finishes, save the fluxes to file
params["post_processor"] = PersistFluxplanes()

#now create a simulation definition
simul_meep = aperture.create_simulation(simul_params = params)
#save this object to file (useful if you want to run the simulation on the supercomputer for example). 
#this creates a file with extension ".def.pysimul", which can be transfered to the supercomputer for execution there
filename = simul_meep.persist_to_file()

#start the simulation
simul_meep.procedure.run(interactive_mode = False)

#create an animated GIF
name = simul_meep.landscape.simulation_id
create_animated_gif_from_hdf5(name + "_Hz.h5", name + "_Eps.h5")

print "Done with Meep simulation."
