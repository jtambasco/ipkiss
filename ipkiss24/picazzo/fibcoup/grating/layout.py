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
from ipkiss.process import PPLayer

""" gratings: structures for the repeated and periodic use of unit cells """

__all__ = ["GratingGeneric",
           "GratingUnitCell",
           "GratingUniform",
           "GratingUniformLine"]
           
class __UnitCell__(object):
    unit_cell = StructureProperty(required = True)
    
class __AutoUnitCell__(__UnitCell__):
    unit_cell = DefinitionProperty(fdef_name = "define_unit_cell")

    
    def define_unit_cell(self):
        raise NotImplementedException("To be implemented by subclass of __AutoUnitCell__ :: define_unit_cell")
    
class GratingGeneric(Structure):
    """ generic grating which places a dictionary of unit cells in certain positions 
        cells_positions should look like:
        { cell1: [pos1, pos2, pos3],
          cell2: [pos1, pos2, pos3], ...}
          """
    __name_prefix__ = "grating_"
    cells_positions = RestrictedProperty(restriction = RestrictType(dict), required = True) # should be elaborated?

    def define_elements(self, elems):
        k = self.cells_positions.keys() 
        k.sort() #to ensure a deterministic build-up of the elements. -- FIXME : this should not be required, but the best solution right now to get the unit testing framework in order
        for cell in k:
            positions = self.cells_positions[cell]
            for p in positions:
                elems += SRef(cell, p)
        return elems


class GratingUnitCell(__UnitCell__, GratingGeneric):
    """ generic grating which places one unit cells in certain positions """
    __name_prefix__ = "grating1_"
    cells_positions = LockedProperty()
    positions = RestrictedProperty(restriction = RestrictTypeList(Coord2), required = True)
    
    def define_elements(self, elems):
        for p in self.positions:
            elems += SRef(self.unit_cell, p)
        return elems
    
class GratingUniform(GratingUnitCell):
    """ generic grating which places one unit cells in a 2D periodic array
          """
    __name_prefix__ = "grating1uni_"
    positions = LockedProperty()
    origin = Coord2Property(required = True)
    period = Coord2Property(required = True)
    n_o_periods = RestrictedProperty(restriction = RESTRICT_INT_TUPLE2, required = True)
    

    def define_name(self):
        L = []
        L.extend([str(int(self.origin[0]*1000)) , str(int(self.origin[0]*1000))])
        L.extend([str(int(self.period[0]*1000)) , str(int(self.period[0]*1000))])
        L.extend([str(self.n_o_periods[0]) , str(self.n_o_periods[0])])
        return "%s_%s_%d" % (self.__name_prefix__,
                             self.unit_cell.name,
                             do_hash("_".join(L))
                         )

    def define_elements(self, elems):
        elems += SoftRotationARef(self.unit_cell, self.origin, self.period, self.n_o_periods)
        return elems
    
def GratingUniformLine(line_width, line_length, period, n_o_periods, purpose = TECH.PURPOSE.DF.TRENCH, process = TECH.PROCESS.FC):
    """ 1-D grating (X-direction) with uniform lines"""
    unit_cell = Structure("line"+ str(int(line_width * 1000)) + "_" + str(int(line_length * 1000)) + "_" + str(PPLayer(process,purpose)).replace(" ","_").replace("-","_"), 
                             Rectangle(PPLayer(process, purpose), (-0.5*line_width, 0.0), (line_width, line_length)))
    origin = (- 0.5 * (n_o_periods-1)*period, 0.0)
    return GratingUniform(unit_cell = unit_cell, 
                          origin = origin, 
                          period = (period, 1.0), 
                          n_o_periods = (n_o_periods, 1))



