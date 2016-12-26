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

#This sample shows to how apply boolean operations to the elements of a structure

#STEP1 : create the original structure
from picazzo.filters.mzi import WgMzi1x1Y90Asymmetric
original_structure =  WgMzi1x1Y90Asymmetric(separation = 20.0,straight1=10.0,straight2=20.0)
original_structure.write_gdsii("original.gds")


#STEP 2 : apply boolean operations to the structure's elements; create a new structure based on these elements.
from ipkiss.boolean_ops.boolean_ops_elements import get_elements_for_generated_layers
gl = TECH.PPLAYER.WG.TRENCH | (TECH.PPLAYER.WG.LINE ^ TECH.PPLAYER.WG.LF_AREA) & TECH.PPLAYER.WG.LF_AREA
elements_on_generated_layer = get_elements_for_generated_layers(elements = original_structure.elements,
                                                                mapping = {gl : TECH.PPLAYER.WG.TEXT})
                                          

new_structure = Structure(elements = elements_on_generated_layer)
new_structure.write_gdsii("generated.gds")





