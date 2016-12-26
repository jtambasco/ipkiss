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
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from .container import __StructureContainerWithPortLabels__

__all__ = ["ExtendPorts",
           ]

class ExtendPorts(__StructureContainerWithPortLabels__):
    """ Wraps a structure in a container and adds extension waveguides to all specified ports """
    
    __name_prefix__ = "EXTPORTS"
    
    extension_length = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    
    def define_elements(self, elems):
        super(ExtendPorts, self).define_elements(elems)
        
        pl = self.__get_labeled_ports__()
        
        for p in pl:
            s = Shape( [p.position, p.position.move_polar_copy(self.extension_length, p.angle_deg)])
            elems += p.wg_definition(shape = s)
        return elems
                
    def define_ports(self, prts):
        L = self.__get_labeled_ports__()
        for p in L:
            prts += p.move_polar_copy(self.extension_length, p.angle)
        prts += self.__get_unlabeled_ports__()
        return prts
    


    
