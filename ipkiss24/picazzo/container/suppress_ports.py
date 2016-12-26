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

__all__ = ["SuppressPorts",
           ]

class SuppressPorts(__StructureContainerWithPortLabels__):
    """Wraps a structure in a container and suppresses the ports specified by the user.
       If None is given, all ports will be suppressed. You can also provide a structure which
       will be attached to each suppressed port (a stub, to remove reflections)
       """
    __name_prefix__ = "SUPTRG"
    
    stub = StructureProperty(allow_none = True)

    def define_elements(self, elems):
        super(SuppressPorts, self).define_elements(elems)
        
        pl = self.__get_labeled_ports__()
        
        S = self.stub
        if not (S is None):
            for p in pl:
                elems += SRef(reference = S, 
                             transformation = vector_match_transform(S.ports[0], p))
        return elems
                
    def define_ports(self, ports):
        spl = self.__get_labeled_ports__()
        for p in self.structure.ports.transform_copy(self.structure_transformation):
            if not (p in spl):
                ports += p

        return ports
    
