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
from picazzo.filters.ring import *
from pysimul.runtime.basic import *
from pysimul.runtime.animation import *
from pysimul.runtime.MeepFDTD.MeepFDTD import MeepSimulationEngine
from ipkiss.plugins.simulation import *
from pysimul.runtime.processor import *
from ipkiss.all import LOG

ring = RingRect180DropFilter(bend_radius = 5.00, straights = (0.0, 0.0), coupler_spacings=[0.67,0.67])

from ipkiss.plugins.vfabrication import *
ring.write_gdsii_vfabrication("ring_vfab.gds")

#export to GDS
my_lib = Library("RING") 
my_lib += ring
fileName = "ring.gds"
out = FileOutputGdsii(fileName)
out.write(my_lib)
LOG.debug("Export to GDS file done. Now starting the simulation.")

wavelength  = 1540.0 
pulse_width = 50.0 

from ipkiss.plugins.vfabrication import *

ring.visualize_2d()

params = dict()
params["structure"] = ring

params["resolution"] = 20 # low resolution, just for the example...
params["engine"] = MeepSimulationEngine(resolution = params["resolution"], use_averaging = False)
params["pml_thickness"] = 1.0
params["include_growth"] = 0.0


params["sources"] = [GaussianVolumeSourceAtPort(field_component = compHz, 
                                                        center_wavelength = wavelength, 
                                                        pulse_width = pulse_width, 
                                                        port = ring.west_ports[0].transform_copy(transformation = Translation(translation=(2.0,0.0))))]

params["datacollectors"] = [FluxplaneAtPort(center_wavelength = wavelength, 
                                            pulse_width = pulse_width,
                                            number_of_sampling_freq = 2000,
                                            port = ring.east_ports[0].transform_copy(transformation = Translation(translation=(-2.0,0.0))),
                                            overlap_trench = False)
                                            ]

params["step_processor"] = SaveFieldsHDF5Processor(fileName = "RING_Hz.h5", H5OutputIntervalSteps = 1000, field_component = compHz)
print
print
print "*************************************** WARNING **********************************************************************"
print "***** WARNING : INCREASE THE maximum_steps PARAMETER TO 750000 IN ORDER TO SEE RESONANCE PEAK !!!!!!!! ***************" 
print "*************************************** WARNING **********************************************************************"
print
print
print
params["stopcriterium"] = StopAfterSteps(maximum_steps = 10000) #INCREASE TO 750000 IN ORDER TO SEE RESONANCE PEAK !!!!!!!!

params["post_processor"] = PersistFluxplanes()

simul = ring.create_simulation(simul_params = params)
simul.procedure.run(interactive_mode = False)        

print "Done with the simulation. Now plotting the flux..."

import cPickle
from dependencies.matplotlib_wrapper import *
file_flux_output = open("fluxplane_datacollector", 'r')


flux_output = cPickle.load(file_flux_output)
file_flux_output.close()

frequencies = 1000.0 / flux_output.flux_per_freq[0] 
F = flux_output.flux_per_freq[1]

pyplot.clf()
p1, = pyplot.plot(frequencies, F, 'yo')

pyplot.savefig("ring_output_flux.png")

pyplot.show()

create_animated_gif_from_hdf5("%s_Hz.h5" %ring.name, "%s_Eps.h5" %ring.name)

