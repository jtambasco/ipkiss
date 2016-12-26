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
from math import cos, sin, pi
from ipkiss.log import IPKISS_LOG as LOG
from ipkiss.aspects.port.port import __InPort__, __OutPort__, __OrientedPort__,__OutOfPlanePort__
from ipkiss.plugins.photonics.wg.definition import WaveguideDefCrossSectionProperty 
from pysics.basics.domain import DomainProperty
from pysics.optics import OpticalDomain

__all__ = ["OpticalPort",
           "InOpticalPort",
           "OutOpticalPort",
           "OpticalPortProperty",
           "VerticalOpticalPort"
           ]

class __OpticalPort__:
    domain = DomainProperty(default=OpticalDomain, locked=True)
    

class OpticalPort(__OpticalPort__,__OrientedPort__):
    wg_definition = WaveguideDefCrossSectionProperty(default = TECH.WGDEF.DEFAULT, doc = "Waveguide definition for the waveguide connecting to this port")
    corner1 = FunctionNameProperty(fget_name = "get_corner1")
    corner2 = FunctionNameProperty(fget_name = "get_corner2")

    def move_copy(self, coordinate):
        return self.__class__(position = self.position + coordinate, angle = self.angle_deg, wg_definition = self.wg_definition)

    def transform(self, transformation):
        if transformation.is_isometric():
            self.position = transformation.apply_to_coord(self.position)
            self.angle_deg = transformation.apply_to_angle_deg(self.angle_deg)
        else:
            self.position = transformation.apply_to_coord(self.position)
            self.angle_deg = transformation.apply_to_angle_deg(self.angle_deg)
            self.wg_definition = self.wg_definition.transform_copy(transformation)
        return self

    def transform_copy(self, transformation):
        if transformation.is_isometric():
            D = self.wg_definition
        else:
            D = self.wg_definition.transform_copy(transformation)
        return self.__class__(position = transformation.apply_to_coord(self.position), 
                              angle = transformation.apply_to_angle_deg(self.angle_deg), 
                              wg_definition = D)

    def flip(self):
        #gives OpticalPort in other direction
        return self.__class__(position = self.position, angle = (self.angle_deg+180.0)%360.0, wg_definition = self.wg_definition)


    def invert_copy(self):
        #changes the OpticalPort from InOpticalPort to OutOpticalPort. This is just added here for ease of coding
        return self.__invert_class__(position = self.position, angle = self.angle_deg, wg_definition = self.wg_definition)


    def is_match(self, other):
        return ((self.position == other.position) and
                (self.angle - other.angle) % 360.0 == 180.0 and
                (self.wg_definition == other.wg_definition) 
                )

    def __eq__(self, other):
        if not isinstance(other, OpticalPort): return False
        return (self.position==other.position and 
                (self.angle_deg == other.angle_deg) and
                (self.wg_definition == other.wg_definition)
                )


    def __ne__(self, other):
        return (self.position!=other.position or 
                (self.angle_deg != other.angle_deg) or
                (self.wg_definition != other.wg_definition)
                )

    def __repr__(self):
        return "<OpticalPort: (%f, %f), a=%f, D=%s>" %(self.position[0], self.position[1], self.angle_deg, self.wg_definition)

    def get_corner1(self):
        port_position = self.position
        port_angle = self.angle * DEG2RAD
        wg_width = self.wg_definition.wg_width
        port_corner1_x = port_position[0] + (wg_width / 2.0) * cos(port_angle-pi/2.0)
        port_corner1_y = port_position[1] + (wg_width / 2.0) * sin(port_angle-pi/2.0)
        corner1 = Coord3(port_corner1_x, port_corner1_y, 0) 
        return corner1

    def get_corner2(self):
        port_position = self.position
        port_angle = self.angle * DEG2RAD
        wg_width = self.wg_definition.wg_width
        port_corner2_x = port_position[0] + (wg_width / 2.0) * cos(port_angle+pi/2.0)
        port_corner2_y = port_position[1] + (wg_width / 2.0) * sin(port_angle+pi/2.0)
        corner2 = Coord3(port_corner2_x, port_corner2_y, 0) 
        return corner2       

OpticalPort.__invert_class__ = OpticalPort


class InOpticalPort(OpticalPort, __InPort__):
    pass

class OutOpticalPort(OpticalPort, __OutPort__):
    __invert_class__ = InOpticalPort

InOpticalPort.__invert_class__ = OutOpticalPort



def OpticalPortProperty(internal_member_name= None, restriction = None,  **kwargs):
    """Property type for storing an OpticalPort"""
    R = RestrictType(OpticalPort) & restriction
    return RestrictedProperty(internal_member_name, restriction = R, **kwargs)


class VerticalOpticalPort(__OpticalPort__,__OutOfPlanePort__):
    """ Optical port in 3D, for optical I/O 
        Specific optical features to be added in the future? 
           - wavelength-dependent angle
           - physical spot size information (like wg definition does for OpticalPort)
    """
    def __repr__(self):
        return "<VerticalOpticalPort: (%f, %f), a=%f, i=%f>" %(self.position[0], self.position[1], self.angle_deg, self.inclination_deg)

