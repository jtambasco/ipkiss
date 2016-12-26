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

from ..socket import SocketProperty
from ipkiss.plugins.photonics.port import VerticalOpticalPort
from ipkiss.all import *

__all__ = ["FiberCoupler",
           "FiberCouplerGrating", 
           "FiberCoupler2dGrating",
           "FiberCouplerGratingAuto",
           "FiberCoupler2dGratingAuto"]
           

##############################################################
## General grating
##############################################################

class FiberCoupler(Structure):
    __name_prefix__ = "FIBCOUP"
    """ generic fiber coupler structure """
        
class __Socket__(StrongPropertyInitializer):        
    socket = SocketProperty(required = True)
    socket_position = Coord2Property(default = (0.0, 0.0))
        
class __AutoSocket__(__Socket__):
    socket = DefinitionProperty(fdef_name = "define_socket")
    socket_position = DefinitionProperty(fdef_name = "define_socket_position")
    
    def define_socket(self):
        (socket, socket_position) = self.__get_socket_and_pos__()
        return socket

    def define_socket_position(self):
        (socket, socket_position) = self.__get_socket_and_pos__()
        return socket_position
        
class __Grating__(StrongPropertyInitializer): 
    grating_transform = TransformationProperty()
    grating = StructureProperty(required = True)
        
class __AutoGrating__(__Grating__):
    grating = DefinitionProperty(fdef_name = "define_grating")
    grating_transform = DefinitionProperty(fdef_name = "define_grating_transform")

    def define_grating_transform(self):
        (grating, grating_transform) = self.__get_grating__()
        return  grating_transform
        
    def define_grating(self):
        (grating, grating_transform) = self.__get_grating__()
        return  grating

class FiberCouplerGrating(__Socket__ , __Grating__, FiberCoupler):
    """ fiber coupler grating base class, which combines a grating on top of a socket """
    __name_prefix__ = "FIBCOUPG"
        
    def define_elements(self, elems):
        elems += SRef(self.socket, self.socket_position)
        E = SRef(self.grating, position = (0.0, 0.0) , transformation = self.grating_transform)
        if self.grating_transform is None or self.grating_transform.is_orthogonal():
            elems  += E
        else:
            elems  += E.flat_copy()
        return elems

    def define_ports(self, ports):
        ports = self.socket.ports.move_copy(self.socket_position)
        fibcoup_pos = Coord2(0.0,0.0)
        if self.grating_transform:
            fibcoup_pos.transform(self.grating_transform)
        ports.append(VerticalOpticalPort(position=(fibcoup_pos.x,fibcoup_pos.y,0.0),inclination=0.0, angle=0.0)) # FIXME: use port given by the grating
        return ports

    

class FiberCouplerGratingAuto(__AutoGrating__, FiberCouplerGrating):
    """ fiber coupler which can determine its grating object itself """
    
    def __init__(self, **kwargs):
        super(FiberCouplerGratingAuto, self).__init__(**kwargs)
    
    def __get_grating__(self):
        """ this function should be overloaded """
        raise NotImplementedError("Function __get_grating__ should be overloaded.")

class FiberCoupler2dGrating(FiberCouplerGrating):
    """abstract base class for 2D gratings"""

class FiberCoupler2dGratingAuto(__AutoGrating__, FiberCoupler2dGrating):
    """abstract base class for 2D gratings"""
    

    def __get_grating__(self):
        raise NotImplementedError("Function __get_grating__ should be overloaded.")
