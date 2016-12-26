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

from Technology import *
from ComponentSimulator3D import *
from Filters_OL_new import *
from numpy import *
from layout import *
import os


#Author : Yannick De Koninck, 05-2011
#Contact Yannick for any questions regarding 3D-simulations of an IPKISS component with Meep.

#Run this script on wpshotonics with 8 processors (mpirun -n 8) : total runtime approximately 2 hours

# For 3D simulations, a slightly other approach is used than for 2D simulations 
# Not the high-level simulation framework is used, but a custom class 'StructureMeep3DSimulator' is used, which wraps low-level python-meep



################################################

## Description: 3D simulation of shallow etched grating
## single mode waveguide - longer section - period is now 330 nm - 30 periods

################################################

output_directory = 'sim_2011_001'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

################################################

## Copy simulation files to folder for future reference

################################################

files_to_copy = ['simulation.py',
                 'ComponentSimulator3D.py',
                 'Filters_OL_new.py',
                 'layout.py',
                 'Technology.py']

source_output_directory = '%s/source' % output_directory

if not os.path.exists(source_output_directory):
    os.makedirs(source_output_directory)
    
for f in files_to_copy :
    new_file = '%s/%s'%(source_output_directory,f)
    copy_command = 'cp %s %s'%(f,new_file)
    print 'Executing:'
    print copy_command
    os.system(copy_command)



wg_def_cavity = WgElDefinition(wg_width = 0.45,trench_width = 1.0)
wg_def_access = WgElDefinition(wg_width = 0.45,trench_width = 1.0)


np_r = 15
np_l = 15
period = 0.330
taper_len = 5.0
section_len = 5.0



print 'Reference Simulation'

grating_unit_cell = WgGratingPeriodShallow(length = period,
                                                       wg_definition = wg_def_cavity,
                                                       shallow_process = TECH.PROCESS.FCW)  
reference_component  = GratingCavityWithModeFilter(wg_definition = wg_def_cavity,
                                                   period = period,
                                                   cavity_length = period/2.0,
                                                   number_of_periods_left = np_l,
                                                   number_of_periods_right = np_r,
                                                   period_component = grating_unit_cell,
                                                   end_wg_def = wg_def_access,
                                                   taper_length = taper_len,
                                                   taper2_length = section_len / 2.0,
                                                   section_length = section_len / 2.0,
                                                   end_wg_def2 = wg_def_access,
                                                   add_overlay = False)


#create new ports that will act as input/output ports for the simulation
act_port_offset = 2.5
p_e = reference_component.east_ports[0].transform_copy(Translation(translation=(-section_len,0)))
p_w = reference_component.west_ports[0].transform_copy(Translation(translation=(+section_len,0)))

reference_component.write_gdsii('comp_for_3d_simulation.gds')

from ipkiss.plugins.vfabrication import *
reference_component.visualize_2d()


print 'Creating reference component simulator'
reference_component_simulator = StructureMeep3DSimulator(component = reference_component,
                                                                input_port = p_w,
                                                                output_ports = [p_w,p_e],
                                                                resolution = 30,
                                                                growth = 0.0,
                                                                wavelength = 1.55,
                                                                source_input_port_offset = -section_len/2.0) #offset for source in reference to the input port

filename = '%s/reversed_flux'%output_directory


print 'Done creating reference component simulator'



reference_component_simulator.pulse_width = 0.4
reference_component_simulator.add_output_cut(OutputCut(normal_vector = 'y',filename = '%s/Ey_y_ref'%output_directory)) #slice orthogonal to the Y-axis at y=0
reference_component_simulator.add_output_cut(OutputCut(normal_vector = 'z',cut_value = 0.810,filename = '%s/Ey_z1_ref'%output_directory)) #slice orthogonal to the Z-axis at z=0.81 (700nm SiOx + half of 220nm Si = 700+110 = 810 => 0.81)
reference_component_simulator.save_reversed_flux_to_file_ID = 0
reference_component_simulator.save_reversed_flux_to_file_filename = filename
reference_component_simulator.stop_time_multiplier = 2.0 #stop after 2 times the pulse length (pulse length calculated by Meep)
reference_component_simulator.dft_terms = 500 #number of sampling points for DFT flux plane
reference_component_simulator.simulate()


print 'Done simulating reference component'

output_filename = '%s/output.txt'%output_directory
output_data = []

## West Port
fd = reference_component_simulator.get_flux(0)
WL_ref = 1./fd[0]
data_ref_w = fd[1]
output_data.append(WL_ref)
output_data.append(data_ref_w)

## East Port
fd = reference_component_simulator.get_flux(1)
WL_ref = 1./fd[0]
data_ref_e = fd[1]
output_data.append(data_ref_e)


## with reversed flux
## ------------------

print 'Simulating with reversed flux'


grating_unit_cell = WgGratingPeriodShallow(length = period,
                                           wg_definition = wg_def_cavity,
                                           shallow_process = TECH.PROCESS.FC)  
component  = GratingCavityWithModeFilter(wg_definition = wg_def_cavity,
                                                   period = period,
                                                   cavity_length = period / 2.0,
                                                   number_of_periods_left = np_l,
                                                   number_of_periods_right = np_r,
                                                   period_component = grating_unit_cell,
                                                   end_wg_def = wg_def_access,
                                                   taper_length = taper_len,
                                                   taper2_length = section_len / 2.0,
                                                   section_length = section_len / 2.0,
                                                   end_wg_def2 = wg_def_access,
                                                   add_overlay = False)

#p_e and p_w are identical to those of the reference component and should therefore not be redefined


reference_component_simulator.component = component
reference_component_simulator.input_port = p_w
reference_component_simulator.output_ports = [p_w,p_e]

reference_component_simulator.clear_output_cut_list()
reference_component_simulator.add_output_cut(OutputCut(normal_vector = 'y',filename = '%s/Ey_y'%output_directory))
reference_component_simulator.add_output_cut(OutputCut(normal_vector = 'z',cut_value = 0.81,filename = '%s/Ey_z1'%output_directory))


reference_component_simulator.save_reversed_flux_to_file_ID = -1 #don't save a flux, but initiliaze the flux from file_ID = 0 (see below)
reference_component_simulator.save_reversed_flux_to_file_filename = filename
reference_component_simulator.load_reversed_flux_from_file_filename = filename
reference_component_simulator.load_reversed_flux_from_file_ID = 0 #initiliaze the flux from file_ID = 0
reference_component_simulator.stop_time_multiplier = 7.0
reference_component_simulator.simulate()



## West Port
fd = reference_component_simulator.get_flux(0)
WL_ref = 1./fd[0]
data_w = fd[1]



output_data.append(WL_ref)
output_data.append(data_w)

## East Port
fd = reference_component_simulator.get_flux(1)
WL_ref = 1./fd[0]
data_e = fd[1]
output_data.append(data_e)


reflection = absolute(array(data_w)) / array(data_ref_w)
transmission = array(data_e) / array(data_ref_w)
output_data.append(WL_ref)
output_data.append(reflection)
output_data.append(transmission)
savetxt(output_filename,matrix(output_data).transpose(),delimiter = '\t')
