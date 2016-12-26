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

## Authors : 
## -written by Martijn Tassert 
## -refactored and integrated by Emmanuel Lambert

from ipkiss.all import *
from ipkiss.plugins.photonics.port.port import OpticalPort, InOpticalPort, OutOpticalPort, OpticalPortProperty
from picazzo.wg.taper.layout import __WgElPortTaper__, WgElTaperLinear, WgElPortTaperLinear
from picazzo.wg.wgdef import *
from picazzo.wg.wgdefs.wg_fc.wgdef import WGFCWgElDefinition
from ipkiss.technology import get_technology

# TODO: m=remove this class. Deprecated. Replaced with AutoTaperPorts.
class WgElPortTaperExtended(__WgElPortTaper__) :
    """ Linear taper between two waveguide definitions that may be of a different type (starting from a port).
    If the taper that converts the start_wg_def to the end_wg_def is defined in the database, it will be returned by use of this class.
    Otherwise a warning will be generated and 'None' will be returned ... """
    
    # FIXME - Should somehow still be expanded such that for equal waveguide definitions also the taper length can be automatically generated if the waveguide definitions are of a known class ...
    taper = DefinitionProperty(fdef_name="define_taper")
    length = FloatProperty(allow_none = True, doc="Length of the taper. Not setting it will use the default values.")
    
    def define_length(self) :        
        return self.taper.length
    
    def define_taper(self) :
        tech = get_technology()
        if hasattr(tech.PROCESS,'RFC'): # FIXME: dirty modular import
            hasraised = True
        else:
            hasraised = False
        # Case: same waveguide definitions ...
        if type(self.end_wg_def)==type(self.start_port.wg_definition) :
            taper = WgElPortTaperLinear(start_port=self.start_port, end_wg_def=self.end_wg_def, straight_extension=self.straight_extension)
        # Case: special tapering structures ...
        elif (hasraised and type(self.start_port.wg_definition) == RaisedWGFCWgElDefinition) and (type(self.end_wg_def) == WGFCWgElDefinition) :
                taper = RaisedWGFCToWGFCPortTaper(start_port=self.start_port, 
                                                 end_wg_def=self.end_wg_def, 
                                                 straight_extension=self.straight_extension)
        elif (hasraised and type(self.start_port.wg_definition) == WGFCWgElDefinition) and (type(self.end_wg_def) == RaisedWGFCWgElDefinition) :
                #we manually create a new port in the opposite direction and flip the straight_extensions, so that we can use the same class 'RaisedWGFCToWGFCPortTaper'
                new_port = OpticalPort(position=(0.0,0.0), wg_definition=self.end_wg_def, angle=self.start_port.angle+180.0)
                taper = RaisedWGFCToWGFCPortTaper(start_port=new_port, 
                                                  end_wg_def=self.start_port.wg_definition, 
                                                  straight_extension=(self.straight_extension[1], self.straight_extension[0]))
                taper = Translation(translation=self.start_position.move_polar_copy(self.length, self.start_port.angle_deg))(taper)
        elif (hasraised and type(self.start_port.wg_definition) == RaisedFCWgElDefinition) and (type(self.end_wg_def) == WgElDefinition) :
                return RaisedFCToWgElPortTaper(start_port=self.start_port, end_wg_def=self.end_wg_def, straight_extension=self.straight_extension)
        elif (hasraised and type(self.start_port.wg_definition) == RaisedWgElDefinition) and (type(self.end_wg_def) == WgElDefinition) :
                taper = RaisedWgElToWgElPortTaper(start_port=self.start_port, 
                                                 end_wg_def=self.end_wg_def, 
                                                 straight_extension=self.straight_extension)
        elif hasraised and (type(self.start_port.wg_definition) == WgElDefinition) :
            if type(self.end_wg_def) == RaisedFCWgElDefinition :
                #we manually create a new port in the opposite direction and flip the straight_extensions, so that we can use the same class 'RaisedFCToWgElPortTaper'
                new_port = OpticalPort(position=(0.0,0.0), wg_definition=self.end_wg_def, angle=self.start_port.angle+180.0)
                taper = RaisedFCToWgElPortTaper(start_port=new_port, 
                                                end_wg_def=self.start_port.wg_definition, 
                                                straight_extension=(self.straight_extension[1], self.straight_extension[0]))
                return Translation(translation=self.start_position.move_polar_copy(self.length, self.start_port.angle_deg))(taper)
            elif type(self.end_wg_def) == RaisedWgElDefinition :
                #we manually create a new port in the opposite direction and flip the straight_extensions, so that we can use the same class 'RaisedWgElToWgElPortTaper'
                new_port = OpticalPort(position=(0.0,0.0), wg_definition=self.end_wg_def, angle=self.start_port.angle+180.0)
                taper = RaisedWgElToWgElPortTaper(start_port=new_port, 
                                                  end_wg_def=self.start_port.wg_definition, 
                                                  straight_extension=(self.straight_extension[1], self.straight_extension[0]))
                taper = Translation(translation=self.start_position.move_polar_copy(self.length, self.start_port.angle_deg))(taper)
            else :
                raise Exception("No taper could be generated between between waveguide types %s and %s." %(self.start_port.wg_definition,self.end_wg_def))
        else :
            raise Exception("No taper could be generated between between waveguide types %s and %s." %(self.start_port.wg_definition,self.end_wg_def))
        if (self.__property_was_externally_set__("length")):
            taper.length = self.length
        return taper                
    
    def define_elements(self, elems) :
        elems += self.taper
        return elems
    
    def validate_properties(self):
        return True #override the restriction that type(self.start_wg_def) should be equal to type(self.end_wg_def)

    
# FIXME: Backward compatibility. This module originally contained these classes    
TECH = get_technology()
if hasattr(TECH.PROCESS,'RFC'):
    from ..wgdefs.raised.tapers import RaisedFCToWgElPortTaper, RaisedWgElToWgElPortTaper, RaisedWGFCToWGFCPortTaper
