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

from pysics.basics.field_profile import FieldProfile2D
import numpy

class ElectroMagneticFieldProfile2D(FieldProfile2D):
       
    def fields_to_array(self):
        return numpy.array([[f.E.value.x.real, f.E.value.x.imag, 
                                            f.E.value.y.real, f.E.value.y.imag, 
                                            f.E.value.z.real, f.E.value.z.imag, 
                                            f.H.value.x.real, f.H.value.x.imag, 
                                            f.H.value.y.real, f.H.value.y.imag, 
                                            f.H.value.z.real, f.H.value.z.imag] for f in self.fields])     
    
    def to_array(self):
        return numpy.array([[p[0], p[1], 
                                            f.E.value.x.real, f.E.value.x.imag, 
                                            f.E.value.y.real, f.E.value.y.imag, 
                                            f.E.value.z.real, f.E.value.z.imag, 
                                            f.H.value.x.real, f.H.value.x.imag, 
                                            f.H.value.y.real, f.H.value.y.imag, 
                                            f.H.value.z.real, f.H.value.z.imag] for p,f in zip(self.positions,self.fields)])         