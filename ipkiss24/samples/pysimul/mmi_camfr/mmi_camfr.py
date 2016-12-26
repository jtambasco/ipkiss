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
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.plugins.simulation import *
from dependencies.matplotlib_wrapper import *
from pysimul import LOG as LOG
import logging
import numpy

LOG.setLevel(logging.DEBUG)

#create an instance of the Picazzo component that we want to simulate with CAMFR
from picazzo.filters.mmi_shallow import ShallowMmi1x2Tapered
W_mmi = 2.90 
L_mmi = 9.90 
D_wg = 1.0
W_wg = 0.45 #CAREFUL : IN CASE OF TAPERS, CAMFR APPEARS NOT TO BE STABLE (FOR W_Wg = 0.45 THERE ARE NO TAPERS)
offset = 0.5*D_wg + 0.5*W_wg
L_taper = 8.0

mmi = ShallowMmi1x2Tapered(width=W_mmi, length=L_mmi, wg_offset=offset, 
                                taper_width=W_wg, taper_length=L_taper, straight_extension=[0.12,0.2])
                  
mmi.write_gdsii("simul_ShallowMmiSplit3Db_camfr.gds") 

from ipkiss.plugins.vfabrication import *
mmi.visualize_2d()

import camfr
camfr.set_lambda(1.55)
camfr.set_N(30) #we can see convergence when increasing the number of modes to 20, 30, ... : the result doesn't change
camfr.set_polarisation(camfr.TM) #TE in 3D is equivalent to TM in 2D
camfr.set_lower_PML(-0.05)
camfr.set_upper_PML(-0.05)    
	
#INSTEAD OF MANUALLY CREATING SLABS AND A STACK, GENERATE IT FROM THE PICAZZO COMPONENT
from ipkiss.plugins.simulation import *
co_west = -8.21
co_east = 18.10
window_si = SizeInfo(west = co_west, east = co_east, south = -2.15, north = 2.15)
stack_expr = camfr_stack_expr_for_structure(structure = mmi,
                                 discretisation_resolution = 10, #DO NOT SET IT TOO HIGH : it will increase the number of slabs considerably, leading to numerical instability
                                 window_size_info = window_si) 

#NOW PROCEED WITH REGULAR CAMFR SCRIPTING
camfr_stack = camfr.Stack(stack_expr)
inc = numpy.zeros(camfr.N())
inc[0] = 1
camfr_stack.set_inc_field(inc) 
LOG.debug("Now extracting the fields...")
camfr_stack.calc()
beta = camfr_stack.inc().mode(0).kz()

#extract the field at the input and output position
x_positions = numpy.arange(0,window_si.height,0.01)
IHz= numpy.zeros(len(x_positions), dtype=numpy.complex)
IH1= numpy.zeros(len(x_positions), dtype=numpy.complex)
IH2= numpy.zeros(len(x_positions), dtype=numpy.complex)
OHz= numpy.zeros(len(x_positions), dtype=numpy.complex)
OH1= numpy.zeros(len(x_positions), dtype=numpy.complex)
OH2= numpy.zeros(len(x_positions), dtype=numpy.complex)

LOG.debug("Now extracting the fields...")
for x_pos, i in zip(x_positions, range(len(x_positions))):
    coord_input = camfr.Coord(x_pos, 0.0, 0.0)
    coord_output = camfr.Coord(x_pos, 0.0, co_east - co_west)
    field_input = camfr_stack.field(coord_input) 
    field_output = camfr_stack.field(coord_output) 
    IHz[i] = field_input.Hz()
    IH1[i] = field_input.H1()
    IH2[i] = field_input.H2()
    OHz[i] = field_output.Hz()
    OH1[i] = field_output.H1()
    OH2[i] = field_output.H2()

#we need the absolute value, not the complex number    
IHz = numpy.absolute(IHz)
IH1 = numpy.absolute(IH1)
IH2 = numpy.absolute(IH2)

OHz = numpy.absolute(OHz)
OH1 = numpy.absolute(OH1)
OH2 = numpy.absolute(OH2)

#normalize
IHz_max = numpy.max(IHz)
IH1_max = numpy.max(IH1)
IH2_max = numpy.max(IH2)

IHz = IHz / IHz_max
OHz = OHz / IHz_max

IH1 = IH1 / IH1_max
OH1 = OH1 / IH1_max

IH2 = IH2 / IH2_max
OH2 = OH2 / IH2_max

#plot
LOG.debug("Now plotting...")    
from matplotlib import pyplot
pyplot.clf()
pyplot.plot(x_positions, IHz, 'b')
pyplot.plot(x_positions, IH1, 'g')
pyplot.plot(x_positions, IH2, 'k')
pyplot.plot(x_positions, OHz, 'r')
pyplot.plot(x_positions, OH1, 'c')
pyplot.plot(x_positions, OH2, 'y')

from scipy.integrate import trapz
PI = trapz(numpy.square(IH2))
PO= trapz(numpy.square(OH2))

print "Integral over H2 square at input : ", PI
print "Integral over H2 square at output : ", PO
print PO / PI * 100.0,"%"
 
pyplot.show()

