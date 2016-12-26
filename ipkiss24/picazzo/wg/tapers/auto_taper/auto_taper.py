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

from ipkiss.all import *
from ..basic.layout import __WgElPortTaper__

__all__ = ["WgElPortTaperAuto"]

class WgElPortTaperAuto(__WgElPortTaper__) :
    """ Automatically generates a taper based on a port and a waveguide definition, using a lookup table"""
    
    length = NonNegativeNumberProperty(allow_none = True, doc="Length of the taper. Not setting it will use the default values.")
    taper_data_base = DefinitionProperty(default = TECH.WGDEF.AUTO_TAPER_DATA_BASE)
    taper = DefinitionProperty(fdef_name = "define_taper")
    taper_class = DefinitionProperty(fdef_name = "define_taper_class")
    swapped = BoolProperty(fdef_name = "define_swapped")
    
    def define_length(self) :        
        return self.taper.length

    @cache()
    def __get_taper_class_swapped__(self):
        swapped = False
        start_wg_def = self.start_port.wg_definition.get_wg_definition_cross_section()
        end_wg_def = self.end_wg_def.get_wg_definition_cross_section()

        taper_class = self.taper_data_base.get_taper_class(start_wg_def, end_wg_def)
        
        # try and swap:
        if taper_class is None:
            taper_class = self.taper_data_base.get_taper_class(end_wg_def, start_wg_def)
            swapped = True
        return (taper_class, swapped)
    
    def define_taper_class(self):
        return self.__get_taper_class_swapped__()[0]
    
    def define_swapped(self):
        return self.__get_taper_class_swapped__()[1]
    
    def define_taper(self) :
        tc = self.taper_class
        if tc is None:
            raise Exception("No taper could be generated between between waveguide types %s and %s." %(self.start_port.wg_definition,self.end_wg_def))
        swapped = self.swapped
        
        if swapped:
            #we manually create a new port in the opposite direction and flip the straight_extensions, so that we can use the same class 'RaisedFCToWgElPortTaper'
            start_port = OpticalPort(position=self.start_port.position, # move the taper later down the road over the correct length
                                   wg_definition=self.end_wg_def.get_wg_definition_cross_section(), 
                                   angle=self.start_port.angle+180.0)
            end_wg_def = self.start_port.wg_definition.get_wg_definition_cross_section()
            straight_extension = (self.straight_extension[1], self.straight_extension[0])
        else:
            start_port = self.start_port
            end_wg_def = self.end_wg_def.get_wg_definition_cross_section()
            straight_extension = self.straight_extension
        
        kwargs = {"start_port": start_port,
                  "end_wg_def": end_wg_def,
                  "straight_extension" : straight_extension
                  }
                  
        # add length if it is set manually    
        if (self.__property_was_externally_set__("length")):
            kwargs["length"] = self.length

        taper = tc(**kwargs)

        # move the taper if necessary
        if swapped:
            taper.move_polar(taper.length, self.start_port.angle_deg)
        return taper                
    
    def define_elements(self, elems) :
        elems += self.taper
        return elems
    
    def validate_properties(self):
        return True #override the restriction that type(self.start_wg_def) should be equal to type(self.end_wg_def)

