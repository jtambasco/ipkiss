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

from ipkiss.primitives.structure import *
from ipkiss.primitives.unit_grid import UnitGridContainer
from time import time
from ipcore.properties.predefined import StringProperty, BoolProperty, TimeProperty
from ipcore.mixin.mixin import MixinBowl


from .. import settings
from ipkiss.log import IPKISS_LOG as LOG
import sys

__all__ = ["Library"]


class Library(UnitGridContainer, MixinBowl):
    name = StringProperty(required = True, doc="Unique name for the library")
    accessed = TimeProperty(doc = "Timestamp at which the library was accessed.")
    modified = TimeProperty(doc = "Timestamp at which the library was modified.")
    layout = BoolProperty(default = True, doc="Indicates whether the library contains a layout : in that case, there should be only 1 top-level structure.")
    allow_empty_structures = BoolProperty(default = True, doc="Indicates whether empty structures are allowed.")
    
    def __init__(self, name, **kwargs):
        super(Library, self).__init__(name=name, **kwargs)
        self.structures = StructureList()
        self.__referenced_structures = set()
        
    def snap_value(self,value):
        return settings.snap_value(value, self.grids_per_unit)

    def snap_coordinate(self,coordinate):
        return settings.snap_coordinate(coordinate, self.grids_per_unit)

    def snap_shape(self,coordinates):
        return settings.snap_shape(coordinates, self.grids_per_unit)

    def add(self,structure):
        if isinstance(structure, Structure) or isinstance(structure, StructureList):
            self.structures.add(structure)
        else:
            raise TypeError("Wrong type " + str(type(structure)) + "of argument in Library.structure_exists.")

    def __iadd__(self, other):
        if isinstance(other, Structure) or isinstance(other, StructureList):
            self.structures.add(other)
        elif isinstance(other, Library):
            for i in other.structures:
                self.structures.add(i)
        return self

    def structure_exists(self,structure):
        return structure in self.structures

    def clean_up(self):
        if self.allow_empty_structures: return

        # remove references to empty structures
        for s in self.structures:
            empty_e = []
            e_list = s.elements
            for i in range(len(e_list)):
                if e_list[i].is_empty: empty_e.append(i)
            del s.elements[empty_e]

        # remove empty structures
        empty_s = []
        for s in range(0,len(self.structures)):
            if self.structures[s].is_empty(): empty_s.append(s)
        del self.structures[empty_s]

    def is_empty(self):
        return len(self.structures) == 0

    def size_info(self):
        return self.top_layout().size_info()

    def flat_copy(self, level = -1):
        newlib = Library(self.name, self.unit, self.grid)
        for s in self.unreferenced_structures():
            newlib.add(s.flat_copy(level))
        newlib.collect_references()
        return newlib

    def flatten(self, level = -1):
        sl = StructureList()
        for s in self.unreferenced_structures():
            sl.add(s.flatten(level))
        self.structures = sl
        self.collect_references()
        return self


    def top_layout(self):
        L = self.unreferenced_structures()
        if len(L) == 1:
            return L[0]
        elif len(L) == 0:
            if len(self.structures) == 0:
                return Structure("__empty__")
            else:
                LOG.warning("There is no top_level structure in library %s. This could be caused by a circular reference" % self.name)
                return None
        elif self.layout:
            warning_string = """There is more than one top-level structure in library %s. 
                                This is ambiguous if the library is to be used as a layout.
                                Please make sure that all but the top-level structures are referred to.
                                #The following structures are 'floating': 
                                #%s """ % (self.name, "#\n".join([s.name for s in L]))
            LOG.warning(warning_string)

    def set_referenced(self, struct):
        self.__referenced_structures.add(struct)
        
    def unreferenced_structures(self, usecache = False):
        """returns a list of unreferenced structures"""
        referred_to_list = self.referenced_structures(usecache = usecache)
        not_referred_to_list = StructureList()
        for s in self.structures:
            if not s in referred_to_list:
                not_referred_to_list.add(s)
        return not_referred_to_list

    def referenced_structures(self, usecache = False):
        """Build list of referred structures"""
        if usecache:
            return StructureList(self.__referenced_structures)
        referred_to_list = StructureList()
        for s in self.structures:
            referred_to_list.add(s.dependencies())
        return referred_to_list

    def collect_references(self, structure = None):
        if structure is None:
            s_list = self.structures
        else:
            s_list = StructureList(structure)
        new_s = StructureList()
        for s1 in s_list:
            d = s1.dependencies()
            for s2 in d:
                new_s.add(s2)
        self.add(new_s)

    def check_references(self):
        """check if all references belong to the library"""
        
        Referred_to_list = self.referenced_structures()
                
        for s in Referred_to_list:
            if not s in self.structures:
                LOG.error("The structure %s you refer to is not part of library %s " % (s.name, self.name))
                raise SystemExit

        Not_Referred_to_list = StructureList()
        for s in self.structures:
            if not Referred_to_list.__fast_contains__(s.name):
                Not_Referred_to_list.__fast_add__(s)
        if len(Not_Referred_to_list) == 0:
            return -2
        return 0

    def __fast_get_structure__(self, str_name):
        """ returns the structure if it exists or returns None"""
        for s in self.structures:
            if s.name == str_name: return s
        return None
    
    def __fast_add__(self, new_str):
        """add a structure without checking if the structure exists"""
        self.structures.__fast_add__(new_str)
        

    def __contains__(self, item):
        return self.structures.__contains__(item)

    def __iter__(self):
        return self.structures.__iter__()

    def __getitem__(self, index):
        return self.structures[index]
    
    def clear(self):
        self.structures.clear()
        
    def __eq__(self, other):
        if not isinstance(other, Library):
            return False
        if len(self.structures) != len(other.structures):
            return False
        for struct1, struct2 in zip(self.structures,other.structures):            
            if (struct1.name != struct2.name):  # check that all structure elements have identical names (this is not required by the __eq__ operator in Structure
                return False
            if (struct1 != struct2):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
    

        
    