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

from ipkiss.plugins.photonics.wg.basic import *
from ..basic import FiberCoupler2dGratingAuto
from ..basic.layout import __AutoSocket__
from ..socket_2d import BroadWgSocket2d, BroadWgSocket2dAsymmetric, BroadWgSocket3Port
from ..grating import GratingUniform
from ..grating.layout import __UnitCell__, __AutoUnitCell__, GratingUnitCell
from ipkiss.plugins.photonics.port.port import OpticalPort
from math import sqrt, cos, sin
from ipkiss.plugins.photonics.wg.definition import WaveguideDefProperty, WaveguideDefListProperty
from ipkiss.process import PPLayer
from ipkiss.all import *

__all__ = ["Uniform2dGrating",
           "BiaxialUniform2dGrating",
           "SymmetricUniform2dGrating",
           "SymmetricUniformBiaxialLongOctagon2dGrating",
           "SymmetricUniformBiaxialRect2dGrating",
           "SymmetricUniformRect2dGrating",
           "AsymmetricUniform2dGrating",
           "AsymmetricUniformRect2dGrating",
           "ThreeportUniform2dGrating",
           "ThreeportUniformRect2dGrating",
           "UniformDodec2dGrating",
           "UniformLongOctagon2dGrating",
           "UniformRect2dGrating",
           "UniformSquare2dGrating"]

###############################################################################
## uniform 2D grating
###############################################################################

class Uniform2dGrating(__UnitCell__, FiberCoupler2dGratingAuto):
    """abstract base class for uniform 2D gratings"""
    process = ProcessProperty(default = TECH.PROCESS.FC)
    period = PositiveNumberProperty(required = True)
    n_o_periods = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    
       
    def __get_grating__(self):
        origin = (-0.5*(self.n_o_periods-1) * self.period, -0.5*(self.n_o_periods-1) * self.period)
        return (GratingUniform(unit_cell = self.unit_cell, origin = origin, period = (self.period, self.period), n_o_periods = (self.n_o_periods, self.n_o_periods)), 
                Rotation(rotation_center = (0.0, 0.0), rotation = 45.0)
                )

class BiaxialUniform2dGrating(__UnitCell__, FiberCoupler2dGratingAuto):
    """abstract base class for 2D gratings with a different pitch and fill factor in two axes"""
    periods = Size2Property(required = True)
    n_o_periods = RestrictedProperty(restriction = RESTRICT_INT_TUPLE2, required= True)
    process = ProcessProperty(default = TECH.PROCESS.FC)
    
    def __get_grating__(self):
        origin = (-0.5*(self.n_o_periods[0]-1) * self.periods[0], -0.5*(self.n_o_periods[1]-1) * self.periods[1])
        return (GratingUniform(unit_cell = self.unit_cell, origin = origin, 
                               period = self.periods, n_o_periods = self.n_o_periods), 
                Rotation((0.0, 0.0), 45))
    
class UniformSquare2dGrating(__AutoUnitCell__, Uniform2dGrating):
    """uniform 2D grating with square unit cell """
    hole_diameter = PositiveNumberProperty(required = True)
    
    def define_unit_cell(self):
        s = ShapeRectangle((0.0,0.0),(self.hole_diameter,self.hole_diameter))
        return Structure(self.name + "_hp", Boundary(PPLayer(self.process, TECH.PURPOSE.DF.SQUARE),s))
        
    def define_elements(self, elems):
        # FCW
        sqrt2_2 = 0.5*sqrt(2)
        side=self.period*self.n_o_periods
        my_shape = Shape([(0.0, side*sqrt2_2),(side*sqrt2_2, 0.0),(0.0, -side*sqrt2_2),(-side*sqrt2_2,0.0)])
        elems += Boundary(PPLayer(self.process, TECH.PURPOSE.DF.TRENCH),coordinates = my_shape) 
        return elems

class UniformRect2dGrating(__AutoUnitCell__, BiaxialUniform2dGrating):
    """uniformt 2D grating with rectangular unit cell """
    hole_diameters = Size2Property(required = True)

    def define_unit_cell(self):
        s = ShapeRectangle(center = (0.0,0.0), box_size = (self.hole_diameters[0],self.hole_diameters[1]))       
        s.transform(Rotation(rotation=45.0))
        return Structure(self.name+"_hpr",Boundary(PPLayer(self.process, TECH.PURPOSE.DF.SQUARE),s))

class UniformLongOctagon2dGrating(__AutoUnitCell__,BiaxialUniform2dGrating):
    """uniformt 2D grating with irregular octagonal unit cell """
    hole_diameters = Size2Property(required = True)

    def define_unit_cell(self):
        stub = 0.08
        s = Shape()
        d0 = 0.5*self.hole_diameters[0]
        d1 = 0.5*self.hole_diameters[1]
        s += (-d0+stub,d1)
        s += (d0-stub,d1)
        s += (d0,d1-stub)
        s += (d0,-d1+stub)
        s += (d0-stub,-d1)
        s += (-d0+stub,-d1)
        s += (-d0,-d1+stub)
        s += (-d0,d1-stub)      
        s.transform(Rotation(rotation=-45.0))
        return Structure(self.name+"_hpr",Boundary(PPLayer(self.process, TECH.PURPOSE.DF.SQUARE),s))
    

class UniformDodec2dGrating(__AutoUnitCell__, Uniform2dGrating):
    """uniform 2D grating with dodecagonal unit cell """
    hole_diameter = PositiveNumberProperty(required = True)

    def define_unit_cell(self):
        from picazzo.phc.holes import DodecHole
        return DodecHole(radius = 0.5*self.hole_diameter, process = self.process)
    
   
class __SymmetricSocket2dGrating__(__AutoSocket__):
    """abstract base class for uniform 2D grating with input and output waveguides, 2 symmetry planes"""    
    wg_definition = WaveguideDefProperty(required = True)
    wg_length = PositiveNumberProperty(required = True)
    dev_angle = AngleProperty(required = True)

    def __get_socket_and_pos__(self):
        ap = BroadWgSocket2d(wg_definition = self.wg_definition, wg_length = self.wg_length, dev_angle = self.dev_angle)
        ap_pos = (0.0, 0.0) # check this
        return (ap, ap_pos)
        
        
class SymmetricUniform2dGrating(__SymmetricSocket2dGrating__, Uniform2dGrating):
    """base class for uniform 2D grating with input and output waveguides, 2 symmetry planes"""    


    
class __AsymmetricSocket2dGrating__(__AutoSocket__):
    """abstract base class for uniform 2D grating with input and output waveguides, 1 symmetry plane
    
       initialize with value pairs in wg_widths, wg_lengths, dev_angles and trench_widths
    """    
    wg_definitions = WaveguideDefListProperty(required=True)
    wg_lengths = RestrictedProperty(restriction = RestrictLen(2) & RestrictList(RESTRICT_POSITIVE), required = True)
    dev_angles = RestrictedProperty(restriction = RestrictLen(2) & RestrictList(RESTRICT_NUMBER), required= True)
    
    def __get_socket_and_pos__(self):
        ap = BroadWgSocket2dAsymmetric(wg_definitions = self.wg_definitions, 
                                         wg_lengths = self.wg_lengths,
                                         dev_angles = self.dev_angles)
        ap_pos = (0.0, 0.0) # check this
        return (ap, ap_pos)
    
        
class AsymmetricUniform2dGrating(__AsymmetricSocket2dGrating__, Uniform2dGrating):
    """abstract base class for uniform 2D grating with input and output waveguides, 1 symmetry plane
    
       initialize with value pairs in wg_widths, wg_lengths, dev_angles and trench_widths
    """    

class ThreeportUniform2dGrating(__AutoSocket__, Uniform2dGrating):
    """abstract base class for uniform 2D grating with input and output waveguides, 3 ports"""    
    port3_offset = NumberProperty(required = True)
    wg_definitions = WaveguideDefListProperty(required=True)
    wg_lengths = RestrictedProperty(restriction = RestrictLen(2) & RestrictList(RESTRICT_POSITIVE), required = True)
    dev_angle = AngleProperty(required = True)
    truncate_periods_3port = IntProperty(default = 0, restriction = RESTRICT_NONNEGATIVE)
    
        
    def __get_socket_and_pos__(self):
        ap = BroadWgSocket3Port(wg_definitions = self.wg_definitions, 
                                wg_lengths = self.wg_lengths, 
                                dev_angle = self.dev_angle, 
                                port3_offset = self.port3_offset)
        ap_pos = (0.0, 0.0) # check this
        return (ap, ap_pos)


    def __get_grating__(self):
        sqrt2_2 = 0.5*sqrt(2)
        pitch = snap_value(self.period*sqrt2_2 * 2,self.unit/self.grid)
        positions = [Coord2(-0.5 * (self.n_o_periods-1 ) * pitch + t * pitch , 0.0) for t in range((self.truncate_periods_3port+1)/2, self.n_o_periods)]
        for i in range(1,self.n_o_periods):
            N = self.n_o_periods - i + max(0, i/2 - self.truncate_periods_3port)
            positions += [Coord2(-0.5 * (self.n_o_periods-1-i%2) * pitch + t * pitch, 0.5 * i * pitch) for t in range((self.truncate_periods_3port+1-i%2)/2, self.n_o_periods - (i+1)/2)]
            positions += [Coord2(-0.5 * (self.n_o_periods-1-i%2) * pitch + t * pitch, -0.5 * i * pitch) for t in range((self.truncate_periods_3port+1-i%2)/2, self.n_o_periods - (i+1)/2)]
        return (GratingUnitCell(unit_cell = self.unit_cell,positions = positions), None)
        
class SymmetricUniformRect2dGrating(__SymmetricSocket2dGrating__,UniformDodec2dGrating):
    """ uniform 2D grating with rectangular unit cell and 2 symmetry planes """

class SymmetricUniformBiaxialRect2dGrating(__SymmetricSocket2dGrating__,UniformRect2dGrating):
    """ biaxial uniform 2D grating with rectangula unit cell and 2 symmetry planes """

    def __get_grating__(self):
        return UniformRect2dGrating.__get_grating__(self)

class SymmetricUniformBiaxialLongOctagon2dGrating(__SymmetricSocket2dGrating__,UniformLongOctagon2dGrating):
    """ biaxial uniform 2D grating with rectangula unit cell and 2 symmetry planes """

    def __get_grating__(self):
        return UniformLongOctagon2dGrating.__get_grating__(self)
    
class AsymmetricUniformRect2dGrating(AsymmetricUniform2dGrating,UniformDodec2dGrating):
    """ uniform 2D grating with rectangular unit cell and 1 symmetry plane """


class ThreeportUniformRect2dGrating(ThreeportUniform2dGrating,UniformDodec2dGrating):
    """ uniform 2D grating with rectangular unit cell and 3 ports """

     
