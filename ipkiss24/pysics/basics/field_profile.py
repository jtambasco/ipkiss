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

from ipcore.all import *
from ipkiss.all import *
from ipkiss.geometry.coord import Coord, Coord3
from ..basics.field import RESTRICT_FIELD
import numpy

# Fieldprofile
# a field value for a list of coordinates
class __FieldProfile__(Transformable, StrongPropertyInitializer):
    positions = RestrictedProperty(required = True, restriction = RestrictList(RestrictType(Coord)))
    fields = RestrictedProperty(required = True, restriction = RestrictList(RESTRICT_FIELD))

    def transform(self, transformation):
        self.transform_positions(transformation)
        self.transform_fields(transformation)
        
    def transform_positions(self, transformation):
        self.positions = [p.transform(transformation) for p in self.positions]

    def transform_fields(self, transformation):
        self.fields = [f.transform(transformation) for f in self.fields]
        
    def positions_to_array(self):
        raise NotImplementedException("__FieldProfile__ subclass must implement positions_to_array method")

    def fields_to_array(self):
        raise NotImplementedException("__FieldProfile__ subclass must implement fields_to_array method")
    
    
class FieldProfile2D(__FieldProfile__):
    positions = RestrictedProperty(required = True, restriction = RestrictList(RestrictType(Coord2)))
    
    def positions_to_array(self):
        return numpy.array([[c[0], c[1]] for c in self.positions])
        
    def to_array(self):
        return numpy.array([self.positions_to_array(), self.fields_to_array()])
        

class FieldProfile3D(__FieldProfile__):
    positions = RestrictedProperty(required = True, restriction = RestrictList(RestrictType(Coord3)))
    
    def positions_to_array(self):
        return numpy.array([[c[0], c[1], c[3]] for c in self.positions])
    
    
class FieldProfile1D(__FieldProfile__):
    def get_positions(self):
        return [Coord2(x, 0.0) for x in self.__positions__] 

    def set_positions(self, value):
        # store in numpy array for efficiency of processing
        L = []
        for c in value:
            if isinstance(c, (Coord2, Coord3, tuple)):
                L.append(c[0])
        self.__positions__ = numpy.array(L)

    positions = FunctionProperty(get_positions, set_positions)

    def positions_to_array(self):
        return self.__positions__    

    def transform_positions(self, transformation):
        self.__positions__ *= tranformation.magnification

    def normalized_overlap(self, other):
        """ the normalized overlap with another field profile """
        p = self.positions_to_array 
        if (p == other.positions_to_array).all():
            d = numpy.diff(p)
            dx = vstack(d[0:1], 
                        0.5*d[:-1] + 0.5*d[1:],
                        d[-1])
        S = []
        S1 = []
        S2 = []
        
        # FIXME: find a good, generic way to calculate the overlaps
        for (f1, f2) in zip(self.fields, other.fields):
            S += [f1.overlap(f2)*numpy.sqrt(abs(f1) * abs(f2))]
            S1 += [f1.overlap(f1)*abs(f1)]
            S2 += [f2.overlap(f2)*abs(f2)]
        S = numpy.array[S]
        S1 = numpy.array[S1]
        S2 = numpy.array[S2]
        
        return numpy.sum(S*dx) / (numpy.sqrt(numpy.sum(S1*dx)) * numpy.sqrt(numpy.sum(S2*dx)))
    
    def overlap_with(self, other):
        """ the overlap with another reference field profile (not normalized) """
        p = self.positions_to_array() 
        if (p == other.positions_to_array()).all():
            d = numpy.diff(p)
            dx = numpy.hstack([d[0:1], 
                        0.5*d[:-1] + 0.5*d[1:],
                        d[-1:]])
            
        S = []
        S1 = []
        S2 = []
        for (f1, f2) in zip(self.fields, other.fields):
            S += [f1.overlap(f2)*numpy.sqrt(abs(f1) * abs(f2))]
            S1 += [f1.overlap(f1)*abs(f1)]
            S2 += [f2.overlap(f2)*abs(f2)]
        S = numpy.array(S)
        S1 = numpy.array(S1)
        S2 = numpy.array(S2)
        
        return numpy.sqrt(numpy.sum(S1*dx)) * numpy.sum(S*dx) / numpy.sqrt(numpy.sum(S2*dx))
            
    def integral(self):
        """ compute the integral (overlap with itself) """
        p = self.positions_to_array 
        if (p == other.positions_to_array).all():
            d = numpy.diff(p)
            dx = vstack(d[0:1], 
                        0.5*d[:-1] + 0.5*d[1:],
                        d[-1])
        S = []
        for (f1, f2) in zip(self.fields, other.fields):
            S += [f1.overlap(f1)]
        S = numpy.array[S]
        
        return sum(S*dx) 
        