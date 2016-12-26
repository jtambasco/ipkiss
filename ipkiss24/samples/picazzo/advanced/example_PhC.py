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
from picazzo.phc.layout import * # generic PhC layouts

# define a layout by just drawing a 'map'
my_phc_map = ["A A A A A A A A A A",
               " A A A A A A A A A ",
               "A A A A A A A A A A",
               " A A A A A A A A A ",
               "",
               " A A A A A A A A A ",
               "A A A A A A A A A A",
               " A A A A A A A A A ",
               "A A A A A A A A A A",
               ] # W1 waveguide
 
# equivalent, using repeat shorthand
my_phc_map = ["A/9, A/", #A, then repeat 9 times the sequence between the comma and the next /
              " /9,A /",
              "A/9, A/",
              " /9,A /",
              "",
              " /9,A /",
              "A/9, A/",
              " /9,A /",
              "A/9, A/",
              ] # W1 waveguide, 9.5 periods


my_component = DodecPhCLayout(pitch = 0.45,
                              hole_sizes = {"A" : 0.290},
                              map = "\n".join(my_phc_map),
                              zero_line_y = 5, #count lines from the top
                              )

my_component.write_gdsii("example_phc.gds")
 # -------- verify the fabrication materials with a 2D visualization
from ipkiss.plugins.vfabrication import *
my_component.visualize_2d()     

# A cavity
my_phc_map = ["A A A A A A A A A A A",
              " A A A A A A A A A A",
              "A A A A A A A A A A A",
              " A A A A A A A A A A",
              "    B A B   B A B  ",
              " A A A A A A A A A A",
              "A A A A A A A A A A A",
              " A A A A A A A A A A",
              "A A A A A A A A A A A",
              ] # W1 waveguide with cavity

my_component = DodecPhCLayout(pitch = 0.45,
                              hole_sizes = {"A" : 0.290,
                                            "B" : 0.190}, # two sizes
                              map = "\n".join(my_phc_map),
                              zero_line_y = 5, #count lines from the top
                              ports_coordinates = [((-0.5, 0), 180, TECH.WGDEF.WIRE),
                                                   ((10.5, 0), 0, TECH.WGDEF.WIRE)
                                                   ] # coordinates expressed in lattice pitches
                              )


my_component.write_gdsii("example_phc2.gds")
 # -------- verify the fabrication materials with a 2D visualization
from ipkiss.plugins.vfabrication import *
my_component.visualize_2d()     



from picazzo.container.extend_ports import ExtendPorts
my_component_with_wg = ExtendPorts(structure = my_component)

my_component_with_wg.write_gdsii("example_phc3.gds")
my_component_with_wg .visualize_2d()     


       


