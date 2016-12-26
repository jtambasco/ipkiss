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

from ipcore.all import StrongPropertyInitializer,StringProperty,RestrictedProperty, RestrictType

class FileType(StrongPropertyInitializer):
    name = StringProperty(required=True)
    doc = StringProperty(default="")
    
    def __str__(self):
        return self.name
def FileTypeProperty(internal_member_name= None, restriction = None,**kwargs): 
    return RestrictedProperty(restriction = RestrictType(FileType),**kwargs) 

GDSII = FileType(name="GDSII", doc="GDSII stream file")
OASIS = FileType(name="OASIS", doc="OASIS file")
OA = FileType(name="OA", doc="OpenAccess database")
SPICE = FileType(name="SPICE", doc="SPICE or HSPICE netlist")
LEFDEF = FileType(name="LEFDEF", doc="LEF and DEF fileset")
CNET = FileType(name="CNET", doc="LVS CNET database")
ASCII = FileType(name="ASCII", doc = "ASCII polygon fileset")
BINARY = FileType(name="BINARY", doc = "Binary polygon fileset")
                       