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

from ipkiss.aspects.port.port_list import PortList
from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.all import *
from ipkiss.plugins.photonics.routing.connect import RouteConnector
from ipkiss.plugins.photonics.wg.bundle import WgElBundleWaveguides
from ipkiss.plugins.photonics.wg.connect import __RoundedWaveguide__

__all__ = []

class __StructureContainer__(Structure):
    """ Base Container class which contains one structure.
        Subclasses can then add additional elements 
    """
    __name_prefix__ = "CONTAINER"
    structure = StructureProperty(required = True)
    structure_transformation = TransformationProperty()

    def define_elements(self, elems):
        elems += SRef(reference = self.structure, 
                      transformation = self.structure_transformation)
        return elems

    @cache()
    def get_structure_port_list(self):
        return self.structure.ports.transform_copy(self.structure_transformation)

    def define_ports(self, ports):
        ports += self.structure.ports.transform_copy(self.structure_transformation)
        return ports
    
    
class __StructureContainerWithPortLabels__(__StructureContainer__):
    """ Base Container class which contains one structure.
        Also has a property for the port labels which need to be addressed
        Subclasses can then add additional elements based on those port labels
    """
    
    port_labels = RestrictedProperty(allow_none = True, 
                                     restriction = RestrictTypeList(str), 
                                     doc = "labels of ports to be processes. \
                                            Set to None to process all ports")
    
    # FIXME - Cache me
    def __get_labeled_ports__(self):
        PL = self.get_structure_port_list()
        if self.port_labels is None:
            return PL
        else:
            return PL.get_ports_from_labels(self.port_labels)
        
    # FIXME - Cache me
    def __get_unlabeled_ports__(self):
        if self.port_labels is None:
            return PortList()
        else:
            PL = self.get_structure_port_list()
            return PL.get_ports_not_from_labels(self.port_labels)
        
    
class __StructureContainerWithWaveguides__(__StructureContainer__):
    """ Base Container class which contains one structure.
        Also adds additional waveguides in the define_waveguides method
    """
    waveguides = DefinitionProperty(fdef_name = "define_waveguides")
    bundled = BoolProperty(default = False)
    
    
    def define_elements(self, elems):
        super(__StructureContainerWithWaveguides__, self).define_elements(elems)
            
        wgs = self.waveguides
        if self.bundled:
            elems += WgElBundleWaveguides(waveguides = wgs)
        else:
            elems += wgs
        return elems

    
class __StructureContainerWithRoutes__(__RoundedWaveguide__, __StructureContainerWithWaveguides__):
    """ Base Container class which contains one structure.
        Also adds additional waveguides by specifying routes in the define_routes method
    """
    routes = DefinitionProperty(fdef_name = "define_routes")
    
    
    def define_waveguides(self):
        return [RouteConnector(route = R, manhattan = self.manhattan) for R in self.routes]

    