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


from .container import __StructureContainerWithPortLabels__
from picazzo.wg.wgdefs.wg_fc.tapers import WgElPortTaperLinear, WgElPortTaperFromShallow
from ipkiss.plugins.photonics.port.port import InOpticalPort,OutOpticalPort
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from ipkiss.all import *

__all__ = ["TaperDeepPorts",
           "TaperShallowPorts",
           "ExtendedTaperPorts"]

class __TaperPorts__(__StructureContainerWithPortLabels__):
    """ Base class for a structure containing an other structure with tapered ports """
    __name_prefix__ = "TP"

    tapers = DefinitionProperty(fdef_name = "define_tapers")    
    
    def define_elements(self, elems):
        super(__TaperPorts__,self).define_elements(elems)
        elems += self.tapers
        return elems
        

    def define_ports(self, prts):
        L = self.__get_labeled_ports__().optical_ports
        for i in range(len(L)):
            if isinstance(L[i], InOpticalPort):
                prts += self.tapers[i].in_ports
            else:
                prts += self.tapers[i].out_ports
        prts += self.__get_unlabeled_ports__().optical_ports
        return prts

    def define_tapers(self):
        raise NotImplementedException("__TaperPorts__::define_tapers to be implemented by subclass!")
    

class TaperPorts(__TaperPorts__):
    """ Base class for tapered port structures"""
    __name_prefix__ = "TP"
    taper_length = PositiveNumberProperty(default = TECH.WG.SHORT_TAPER_LENGTH, doc = "length of the taper")
    end_wg_def = WaveguideDefProperty(default = TECH.WGDEF.WIRE, doc = "waveguide definition of the outputs")
    straight_extension = Size2Property(default = (0.0, 0.0), doc = "tuple: straight extensions of the tapers")
       

class TaperDeepPorts(TaperPorts):
    """ Structure containing another structure with its deep etched ports tapered """
    process = ProcessProperty(allow_none = True, doc = "To overrule the process, if the process of the start port should not be used")
    straight_extension = Size2Property(default = (0.15, 0.15), doc = "tuple: straight extensions of the tapers (0.15 as default to avoid DRC violations)")    
    __name_prefix__ = "TDP"
            
    def define_tapers(self):
        if self.process is None:
            return [WgElPortTaperLinear(start_port = P, end_wg_def = self.end_wg_def, length = self.taper_length, straight_extension = self.straight_extension) for P in self.__get_labeled_ports__().optical_ports]        
        else:
            return [WgElPortTaperLinear(start_port = P, end_wg_def = self.end_wg_def, length = self.taper_length, straight_extension = self.straight_extension, start_process = self.process) for P in self.__get_labeled_ports__().optical_ports]        
            
    
class TaperShallowPorts(TaperPorts):
    __name_prefix__ = "TSP"
    deep_process = ProcessProperty(default = TECH.PROCESS.WG)
    shallow_process = ProcessProperty(default = TECH.PROCESS.FC)
    deep_only_width = DefinitionProperty()
    straight_extension = Size2Property(default = (0.15, 0.15), doc = "tuple: straight extensions of the tapers")
                                         
    def define_deep_only_width(self):
        wg_widths = [P.wg_definition.wg_width for P in self.__get_labeled_ports__()]
        
        return  max(TECH.WG.SPACING, self.end_wg_def.wg_width, max(wg_widths))
       
    
    def define_tapers(self):     
        tapers = []
        for P in self.__get_labeled_ports__():
            if self.deep_only_width is None:
                deep_only_width = max(TECH.WG.SPACING, self.end_wg_def.wg_width, P.wg_definition.wg_width)
            else:
                deep_only_width = self.deep_only_width
            deep_only_wg = WgElDefinition(wg_width =  deep_only_width, 
                                          trench_width = P.wg_definition.trench_width,
                                          process = self.deep_process)
            tapers.append(WgElPortTaperFromShallow(start_port = P, end_wg_def = self.end_wg_def, length = self.taper_length, deep_process = self.deep_process, shallow_process = self.shallow_process,
                                         straight_extension = self.straight_extension, deep_only_wg_def =  deep_only_wg))
        return tapers


        
        
class ExtendedTaperPorts(TaperPorts):
    # FIXME: deprecated. Use AutoTaperPorts instead
    """ Structure containing another structure which will apply the WgElPortTaperExtended"""
    __name_prefix__ = "EXTTP"
            
    def define_tapers(self):
        from picazzo.wg.taper_extended import WgElPortTaperExtended
        return [WgElPortTaperExtended(start_port = P, end_wg_def = self.end_wg_def, length = self.taper_length, straight_extension = self.straight_extension) for P in self.__get_labeled_ports__()]        
    


