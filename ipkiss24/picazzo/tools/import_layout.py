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
from ipkiss.exceptions.exc import IpkissException
import os.path 
from ..log import PICAZZO_LOG as LOG
import sys
from ipkiss.process import PPLayer
from ipkiss.technology import get_technology
from ipkiss.io.input import InputBasic

__all__ = ["ImportLayout", "ImportStructure"]

TECH = get_technology()

class __ImportBase__(StrongPropertyInitializer):
    filename = FilenameProperty(default = "")
    layer_map = RestrictedProperty(default = TECH.GDSII.IMPORT_LAYER_MAP)
    input_handler = RestrictedProperty(default = InputGdsii, restriction = RestrictClass(InputBasic))


class ImportLayout( StoredNoDistortTransformable, __ImportBase__):
    name = StringProperty(required = True)
    position = Coord2Property(default = (0.0, 0.0))

    def read(self):
        if os.path.exists(self.filename):
            F = open(self.filename,"rb")
            input = InputGdsii(F)
            input.layer_map = self.layermap
            input.prefix = self.name + "_"
            L = input.read()
            F.close()
        else:
            raise IpkissException("ImportLayout::read : Could not find " + self.filename + " for import.")
        return L
        

class ImportStructure(__ImportBase__, Structure):
    toplevel = StringProperty(default="")
    prefix = DefinitionProperty()
    gzipped = BoolProperty(default=False)
    
    def define_prefix(self):
        return (self.name + "_")

    def get_header_only(self):
        from ipkiss.io.input_gdsii import InputGdsiiHeader
        if os.path.exists(self.filename):
            if self.gzipped:
                from gzip import GzipFile
                F = GzipFile(self.filename, mode = "rb")
            else:
                F = open(self.filename,"rb")
            input = InputGdsiiHeader(F)
            input.layer_map = self.layer_map
            input.prefix = self.prefix
            L = input.read()
            F.close()
        else:
            raise IpkissException("ImportStructure:: Could not find " + self.filename + " for import.") #FIXME - should be PicazzoException
        return L
        
    @cache()
    def get_file_library(self):
        LOG.info("Importing %s " %  self.filename )
        filesize = os.path.getsize(self.filename)
        LOG.info("size: %d KB"%(filesize/1024))
        if os.path.exists(self.filename):
            if self.gzipped:
                from gzip import GzipFile
                F = GzipFile(self.filename, mode = "rb")
            else:
                F = open(self.filename,"rb")
            input = self.input_handler(F, stop_on_unknown_gds_layer=False, log_bufsize = filesize)
            input.layer_map = self.layer_map
            input.prefix = self.prefix
            L = input.read()
            F.close()
        else:
            raise IpkissException("ImportStructure:: Could not find " + self.filename + " for import.") #FIXME - should be PicazzoException
        return L
        
    @cache()
    def get_library_top_level(self):
        L = self.get_file_library()
        if self.toplevel!="":
            S = L["%s%s"%(input.prefix,self.toplevel)]
        else:
            S = L.top_layout()      
        return S
    
    def define_elements(self, elems):
        S = self.get_library_top_level()
        elems += S.elements
        return elems


