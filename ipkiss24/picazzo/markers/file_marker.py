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
from ipkiss.io.gds_layer import GdsiiLayerInputMap, AutoGdsiiLayerInputMap
from ipkiss.process.layer_map import GdsiiPurposeInputMap, GdsiiPPLayerInputMap, GenericGdsiiPPLayerInputMap
import os

class FileMarker(Structure):
    __name_prefix__ = "FILEMARK"
    filename = FilenameProperty(required = True)
    layer_map = RestrictedProperty(restriction = RestrictType(allowed_types = [GdsiiLayerInputMap, 
                                                                               AutoGdsiiLayerInputMap,
                                                                               GdsiiPPLayerInputMap,
                                                                               GenericGdsiiPPLayerInputMap]),
                                   required = True)
    toplevel = StringProperty(default="")
    prefix = StringProperty(default="")

    def define_name(self):
        return "%s_%s%s" % (self.__name_prefix__,self.prefix, 
                             os.path.splitext(os.path.split(self.filename)[1])[0])

    @cache()
    def get_file_library(self):
        LOG.info("Importing %s " %  self.filename )
        filesize = os.path.getsize(self.filename)
        LOG.info("size: %d KB"%(filesize/1024))
        if os.path.exists(self.filename):
            F = open(self.filename,"rb")
            input = InputGdsii(F, stop_on_unknown_gds_layer=False, log_bufsize = filesize)
            input.layer_map = self.layer_map
            L = input.read()
            F.close()
        else:
            raise IpkissException("ImportStructure:: Could not find " + self.filename + " for import.") #FIXME - should be PicazzoException
        return L
    
    @cache()
    def get_library_top_level(self):
        L = self.get_file_library()
        if self.toplevel!="":
            S = L["%s"%(self.toplevel)]
        else:
            S = L.top_layout()      
        return S
    
    def define_elements(self, elems):
        S = self.get_library_top_level()
        elems += S.elements
        return elems

from ipkiss.io.gds_layer import GdsiiLayerInputMap

class SingleProcessFileMarker(FileMarker):
    __name_prefix__ = "FILEMARKS"
    process = ProcessProperty(required = True)

    def define_name(self):
        return "%s_%s" % (super(SingleProcessFileMarker, self).define_name(), self.process.extension)

    def define_elements(self, elems):
        f = open(self.filename,"rb")
        I = InputGdsii(f, stop_on_unknown_gds_layer = False)
        I.prefix = "%s_"%(self.process.extension)
        if self.layer_map != None:
            I.layer_map = self.layer_map
        S = I.read().top_layout()
        elems += S.elements
        return elems
    
