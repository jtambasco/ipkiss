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
from example3_three_port import * # our structure
from ipkiss.plugins.vfabrication import *

#Illustrates how to create a 2D- and 3D-visualization of a certain component.
#Only use for specific components, not for complete masks (requires quite a lot of RAM)

my_component = ThreePortToEast(width = 5.0, height = 2.0)

#make a 2d-visualisation (requires Matplotlib)
my_component.visualize_2d()

#render a 3d-visualisation with POVRAY : create a POVRAY-file
my_component.visualize_3d_povray(camera_pos = (10,0,10)) 
# This generates a file '3PORT_R_W5000_H2000_W450_T2000_2D_R10_GR0.000000.pov' which should then be rendered
# with the software Povray : http://www.povray.org/download/

#render a 3d-visualisation as a VTK-file (requires Meep)
#my_component.visualize_3d_vtk(resolution = 40) 



