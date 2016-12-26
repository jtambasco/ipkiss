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
from ipkiss.plugins.simulation import *
from pysimul import LOG 
import logging

#create an instance of the Picazzo component that we want to simulate
from picazzo.filters.mmi_shallow import ShallowMmi1x2Tapered
W_mmi = 2.90 
L_mmi = 9.90 
D_wg = 1.0
W_wg = 0.45 #no tapers
offset = 0.5*D_wg + 0.5*W_wg
L_taper = 8.0
mmi = ShallowMmi1x2Tapered(width=W_mmi, length=L_mmi, wg_offset=offset, 
                                taper_width=W_wg, taper_length=L_taper, straight_extension=[0.12,0.2])

#export the component to GDS, just for our own reference
mmi.write_gdsii("simul_mmi.gds")

#create a dictionary with all the simulation parameters
simul_params = dict()

#specify the simulation engine that we want to use : Meep FDTD with a resolution of 20
simul_params["resolution"] = 30 #low resolution just for the example 
simul_params["engine"] = MeepSimulationEngine(resolution = simul_params["resolution"])
#add PML of 2 micrometer and grow the component 3 micrometer larger
simul_params["pml_thickness"] = 2.0

#grow the component for 3 micron around it's bounding box, so that the ports don't stick to the PML (we want to apply the source 1 micron let of the west port)
simul_params["include_growth"] = 3.0

#define a continuous source matching the mode profile at 1 micrometer left of the west port
#CAMFR will be used to calculate this mode profile and the source will be shaped accordingly
#the source will run for 100 time steps
center_wavelength = 1550.0
fluxplane_width = 30.0
simul_params["sources"] = [ModeProfileContinuousSourceAtPort(center_wavelength = center_wavelength, 
                                                       smoothing_width = 60.0, 
                                                       port = mmi.west_ports[0].transform_copy(transformation = Translation(translation=(-1.0,0.0))), 
                                                       polarization = TE,
                                                       stop_time = 120.0)]

#add a fluxplane at the input port and 2 fluxplanes at each of the output ports
#add a probing point 0.25 micrometer to the right of one of the output ports
simul_params["datacollectors"] = [FluxplaneAtPort(center_wavelength = center_wavelength, 
                                                                        pulse_width = fluxplane_width,
                                                                        number_of_sampling_freq = 100,
                                                                        port = mmi.west_ports[0],
                                                                        overlap_trench = False,
                                                                        name = "flux input"),  
                            FluxplaneAtPort(center_wavelength = center_wavelength, 
                                                                        pulse_width = fluxplane_width,
                                                                        number_of_sampling_freq = 100,
                                                                        port = mmi.east_ports[0],
                                                                        overlap_trench = False,
                                                                        name = "flux upper output"),
                            FluxplaneAtPort(center_wavelength = center_wavelength, 
                                                                        pulse_width = fluxplane_width,
                                                                        number_of_sampling_freq = 100,
                                                                        port = mmi.east_ports[1],
                                                                        overlap_trench = False,
                                                                        name = "flux lower output"),                            
                            ProbingpointAtPort(port = mmi.east_ports[0].transform_copy(transformation = Translation(translation=(0.25,0.0))))]

#specify a step_processor : this processor will be called at every step of the FDTD simulatioN.
#In our case, save the Hz component to file every 100 steps
simul_params["step_processor"] = SaveFieldsHDF5Processor(H5OutputIntervalSteps = 100, field_component = compHz)

#specify a stop criterium : stop when the Hz field component at the probing point has decayed to 0.01 of it's peak value
simul_params["stopcriterium"] = RunUntilFieldsDecayedAtProbingPoint(field_component = compHz, probingpoint = simul_params["datacollectors"][3], decay_factor = 0.01)

#specify a post_processor : this processor will be called when the simulation finishes : save the fluxes to file. 
#These files can later be loaded with cPickle, see below
simul_params["post_processor"] = PersistFluxplanes()

#with these parameters, instantiate a SimulationDefinition object
simul_def = mmi.create_simulation(simul_params)

#OPTIONAL : save thisSimulationDefinition to file : useful if you want to run the simulation on the supercomputer for example !!
#this creates a file with extension ".def.pysimul", which can be transfered to the supercomputer for execution there
filename = simul_def.persist_to_file()


#start the simulation : when 'interactive_mode' is set to 'False', all intermediate graphical output is saved in file
LOG.info("Now starting the simulation...")
simul_def.procedure.run(interactive_mode = False)

#display the fluxes
LOG.info("Now displaying the fluxes...")
from dependencies.matplotlib_wrapper import *
#this could be done without reading the fluxes from file (since we can retrieve them from memory), 
#but we do it here as an illustration of the technique, in case you want to process the fluxes after the simulation in a seperate script
file_flux_output_north = open("fluxplane_fluxupperoutput", 'r')
file_flux_output_south = open("fluxplane_fluxloweroutput",'r')
file_flux_input = open("fluxplane_fluxinput",'r')
#load the files with flux data, which were saved by the post_processor 'PersistFluxplanes' (see above)
import cPickle
flux_input = cPickle.load(file_flux_input)
flux_output_south = cPickle.load(file_flux_output_south)
flux_output_north = cPickle.load(file_flux_output_north)
file_flux_input.close()
file_flux_output_south.close()
file_flux_output_north.close()

#prepare the data
frequencies = 1000.0 / flux_input.flux_per_freq[0] 

F_in = flux_input.flux_per_freq[1]
F_out_south = flux_output_south.flux_per_freq[1]
F_out_north = flux_output_north.flux_per_freq[1] 

ref_max = max(F_in)

Fi = [f / ref_max for f in F_in]

Fo1 = [fo / fi  for fo,fi in zip(F_out_south, F_in)]
Fo2 = [fo / fi  for fo, fi in zip(F_out_north, F_in)]
Fo = [f1+f2 for f1,f2 in zip(Fo1,Fo2)]

known_efficiency = [0.95] #we know from earlier simualtions that the efficiency of the MMI is 95%

#initiate the plotting
pyplot.clf()
p1, = pyplot.plot(frequencies, Fi, 'yo')
p2, = pyplot.plot([1550],known_efficiency, 'co')
p3, = pyplot.plot(frequencies, Fo, 'bo')
p4, = pyplot.plot(frequencies, Fo1, 'ro', )
p5, = pyplot.plot(frequencies, Fo2, 'go' )

pyplot.savefig("mmi_flux.png")

pyplot.show()

#create an animated GIF of the fields
LOG.info("Now creating animated gif...")
name = simul_def.landscape.simulation_id
create_animated_gif_from_hdf5(name + "_Hz.h5", name + "_Eps.h5")

LOG.info("Done.")


