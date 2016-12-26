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

class ExampleAsymmetricFibcoup(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        from picazzo.io.fibcoup import IoFibcoupAsymmetric
        my_column = IoColumnGroup(south_east = (2000.0,0.0),     # column width = 2000um
                                  y_spacing = 25.0,              # vertical spacing between waveguides
                                  adapter = IoFibcoupAsymmetric) # new default adapter          
                
        # define a component
        from picazzo.filters.ring import RingRect180DropFilter
        my_ring = RingRect180DropFilter(name = "My_Ring")

        # add the component to the column
        my_column.add(my_ring,
                      west_fibcoup = TECH.IO.FIBCOUP.DEFAULT_GRATING_TE,
                      east_fibcoup = TECH.IO.FIBCOUP.DEFAULT_GRATING_TM,
                      east_merged_waveguides = False,
                      ) # all adapter parameters can be set for east and west separately
                        # all the regular parameters if IoFibcoup can be used, now with prefix
                        # 'east_' or "west_' (see previous example).
        
        elems += my_column
        return elems


my_layout = ExampleAsymmetricFibcoup(name = "MyLayout")
my_layout.write_gdsii("advanced_adapters_1.gds")    
    
class ExampleGenericFibcoup(Structure):
    
    def define_elements(self, elems):
        # define a column
        from picazzo.io.column import IoColumnGroup
        from picazzo.io.fibcoup import IoFibcoupGeneric
        my_column = IoColumnGroup(south_east = (2000.0,0.0),     # column width = 2000um
                                  y_spacing = 25.0,              # vertical spacing between waveguides
                                  adapter = IoFibcoupGeneric) # new default adapter          
        
        
        # define a component
        from picazzo.filters.ring import RingRect180DropFilter
        my_ring = RingRect180DropFilter(name = "My_Ring")

        # add the component to the column
        my_column.add(my_ring,
                      west_fibcoups= [TECH.IO.FIBCOUP.DEFAULT_GRATING_TE,
                                      TECH.IO.FIBCOUP.DEFAULT_GRATING_TM], # list
                      east_fibcoup_taper_lengths = [50.0, 300.0, 500.0], # list
                      ) # each individual fiber coupler interface can now be set separately
                        # if there are more parts than elements in a list, the adapter will cycle through
                        # the elements in the list. in this case, the west fiber couplers will 
                        # alternate between TE and TM. The east taper lengths will cycle between the 
                        # three values.
                        # The cycling restarts with each new invokation of the adapter.
                        # all parameters of IoFibcoup can be used, but with prefix 'east_' or 'west_',
                        # and converted to plural
        elems += my_column
        return elems
    
    
my_layout = ExampleGenericFibcoup(name = "MyLayout2")
my_layout.write_gdsii("advanced_adapters_2.gds")