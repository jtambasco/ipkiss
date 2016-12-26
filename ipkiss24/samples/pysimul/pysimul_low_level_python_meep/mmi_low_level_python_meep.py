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

try:
    import meep as meep
except ImportError, e:
    try :
        import meep_mpi as meep
    except ImportError, e:
        raise Exception("Modules 'meep' or 'meep_mpi' not found.")    


#This example illustrates how you can combine automatic interface of a Picazzo geometry with low-level Python-Meep scripting.
#It is intended for advanced users only

#Create the Picazzo component for which we want to interface the geometry to Meep
from picazzo.filters.mmi_shallow import ShallowMmi1x2Tapered
W_mmi = 2.90 
L_mmi = 9.90 
D_wg = 1.0
W_wg = 0.45 #no tapers
offset = 0.5*D_wg + 0.5*W_wg
L_taper = 8.0
mmi = ShallowMmi1x2Tapered(width=W_mmi, length=L_mmi, wg_offset=offset, 
                           taper_width=W_wg, taper_length=L_taper, straight_extension=[0.12,0.2])
mmi.write_gdsii("simul_mmi.gds")

#Set simulation parameters
simul_params = dict()
simul_params["resolution"] = 10
simul_params["engine"] = MeepSimulationEngine(resolution = simul_params["resolution"])
simul_params["pml_thickness"] = 2.0
simul_params["include_growth"] = 10.0 #we want to put a point source far left of the west port, therefore, we extend the component at the ports with a waveguide of 10 micron
simul_params["center_wavelength"] = 1550.0


#Create a class that wraps the low-level Python-Meep commands
class MyProcedure(LowLevelPythonMeepProcedure): 

    def run(self, interactive_mode = False):
        self.engine.initialise_engine(self.landscape) #mandatory !
        self.save_engine_dielectricum_to_file()	#export to file the dielectricum as it was received by Meep	
        #create a reference to the meep fields object
        fields = meep.fields(self.engine.structure)
        #If you want to use the mode profile at a certain port in your python-meep scripting,then you can retrieve it as follows (THIS IS NOT ACTUALLY USED FURTHER IN THE SCRIPT, IT'S JUST AN ILLUSTRATION OF WHAT YOU COULD DO...)
        mp = get_mode_profile_at_port(structure = mmi,
                                      resolution = simul_params["resolution"],
                                      port = mmi.west_ports[0], 
                                      wavelength = simul_params["center_wavelength"])
        print mp		
        #create a Gaussian source 
        center_wavelength = simul_params["center_wavelength"]
        pulse_width = 30
        center_freq = 1.0 / (float(center_wavelength) / 1000.0)
        pulse_width_freq = ( (float(pulse_width)/1000.0) / (float(center_wavelength)/1000.0) ) * center_freq 			
        src_gaussian = meep.gaussian_src_time(center_freq, pulse_width_freq)
        #add a point source (linked to the Gaussian source) at the position of the west port
        source_position_vec = self.make_meep_vec(mmi.west_ports[0].transform_copy(Translation(translation=(-9.0,0))).position)
        fields.add_point_source(meep.Hz, src_gaussian, source_position_vec)		
        #add a probing point to the upper output arm
        probing_point_vec = self.make_meep_vec(mmi.east_ports[1].position)
        #run the simulation
        h5_file = meep.prepareHDF5File("./mmi_low_level.h5")
        meep.runUntilFieldsDecayed(fields, self.engine.meepVol, meep.Hz, probing_point_vec, pHDF5OutputFile = h5_file, pH5OutputIntervalSteps = 100)

#create the simulation		
simul_def = mmi.create_simulation(simul_params)
#overwrite the default procedure with your own custom one
simul_def.procedure_class = MyProcedure
#start the simulation
simul_def.procedure.run()