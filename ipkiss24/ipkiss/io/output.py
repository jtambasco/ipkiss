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

from ..geometry import shape_cut 
from ..geometry.shapes import advanced, modifiers 
from ..geometry import shape_info
from ..geometry.shape import Shape
from ipcore.properties.initializer import StrongPropertyInitializer
from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.predefined import BoolProperty, RESTRICT_POSITIVE, IntProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.processors import ProcessorTypeCast
from ..primitives.layer import LayerList
from ..primitives.filter import Filter
from .collector import ListCollector
from .. import constants
from ipkiss.log import IPKISS_LOG as LOG
from ipkiss.settings import *
from ipkiss.primitives import Library
from ipkiss.primitives.elements.basic import ElementList
import sys
import logging

all = []

#######################################################################
## Basic output module
#######################################################################
class BasicOutput(StrongPropertyInitializer):
    o_stream = RestrictedProperty(default = sys.stdout)
    filter = RestrictedProperty(default = Filter(), restriction = RestrictType(Filter), doc = "filter class which is applied to all output items")
    name_filter = RestrictedProperty(default = Filter(), restriction = RestrictType(Filter), doc = "filter class which is applied to all names")
    
    def __init__(self, o_stream = sys.stdout, **kwargs):
        super(BasicOutput, self).__init__(o_stream = o_stream,**kwargs)
        self.__init_collector__()

    def __init_collector__(self):
        self.collector = ListCollector()
    
    def write(self, item):
        self.o_stream.write(self.str(item))
        self.o_stream.flush()

    def str(self, item):
        self.collect(item)
        return self.collector.out_str()

    def list(self, item):
        self.collector += [item]

#######################################################################
## Base class for output modules with collect_<class> methods
#######################################################################

class __OutputBasic__(BasicOutput):         

    def __init__(self, o_stream = sys.stdout, **kwargs):
        super(__OutputBasic__, self).__init__(o_stream = o_stream, **kwargs)
        self.__collect_method_dict__ = {}
                
    def collect(self, item,  **kwargs):       
        self.do_collect(item, **kwargs)
        return 
    
    def do_collect(self, item,  **kwargs):
        import inspect        
            
        items = self.filter(item)
        if len(items) == 1:
            item = items[0]
        else:
            item = items            

        T = type(item)
        if inspect.isclass(T): 
            collect_method = self.__collect_method_dict__.get(T, None)
            if collect_method is None:
                for M in inspect.getmro(T):
                    collect_method_name = "collect_%s" % M.__name__
                    if hasattr(self, collect_method_name):
                        collect_method = getattr(self, collect_method_name)
                        self.__collect_method_dict__[T] = collect_method
                        break
            if collect_method is None:
                LOG.warn("No collect method found for object of type %s" %T)                       
            else:
                collect_method(item, **kwargs)      
                
        return     

        
from ..technology.settings import TECH
from .gds_layer import GdsiiLayer

#######################################################################
## Basic GDS output stream
#######################################################################

class OutputBasic(__OutputBasic__):         
    layer_map = RestrictedProperty(default = TECH.GDSII.EXPORT_LAYER_MAP)
    echo = BoolProperty(default = False)

    def __init__(self, o_stream = sys.stdout, **kwargs):
        super(OutputBasic, self).__init__(o_stream = o_stream, **kwargs)
        self.library = None
        self.__current_structure__ = None
        self.__collect_method_dict__ = {}

    def __init_collector__(self):
        self.collector = ListCollector()
        
    def set_current_structure(self, S):
        self.__current_structure__ = S
        self.__structure_scale__ = S.unit / self.unit        
        
    def define_filter(self):
        return TECH.GDSII.FILTER                

    def do_collect(self, item,  **kwargs):
        from ..primitives import library
        
        if isinstance(item, Library):
            self.library = item
            #for performance, to avoid repeated calls to DefinitionProperty in hot code
            self.grids_per_unit = self.library.grids_per_unit 
            self.unit = self.library.unit 
            
        if (self.library == None):
                self.library = get_current_library()
    
        super(OutputBasic,self).do_collect(item,**kwargs)
        
        return     
    
    def collect_list(self, item, **kwargs):
        for i in item:
            self.collect(i,  **kwargs)   
        return

    def collect_Structure(self, item,  **kwargs):
        if self.echo: 
            LOG.info("Defining Structure %s with %d elements." % (item.name, len(item.elements)))
        self.set_current_structure(item)

        self.__collect_structure_header__(item)
        self.collect(item.elements, **kwargs)
        self.__collect_structure_footer__(item)
        return 
    
    def collect_Library(self, library,  usecache = False, **kwargs):
        self.__collect_library_header__(library)
        unreferenced_structures = self.library.unreferenced_structures(usecache = usecache)
        referenced_structures = self.library.referenced_structures(usecache = usecache)
        self.collect(unreferenced_structures,  **kwargs)
        self.collect(referenced_structures,  **kwargs)
        self.__collect_library_footer__()
        return
    
    def __collect_library_header__(self, library):    
        pass
    
    def __collect_library_footer__(self):
        pass

    def collect_ElementList(self, item,  additional_transform = None, **kwargs):
        for s in item:
            self.collect(s,  additional_transform = additional_transform, **kwargs)
        return

    def collect_StructureList(self, item,  **kwargs):
        for s in item:
            self.collect(s,  **kwargs)
        return 

    def collect_Group(self, item,  additional_transform = None, **kwargs):
        self.collect(item.elements,  additional_transform = item.transformation + additional_transform, **kwargs)
        return


    def collect_Boundary(self, item,  additional_transform = None, **kwargs):       
        shape = item.shape.transform_copy(item.transformation + additional_transform)
        shape.snap_to_grid(self.grids_per_unit)
        shape.remove_identicals()
        coordinates = shape
        # BOUNDARIES
        if len(shape) < 3:
            LOG.warning("BOUNDARY with fewer than 3 coordinates not allowed in structure %s" % self.__current_structure__.name)
            return
        if len(shape) > TECH.GDSII.MAX_VERTEX_COUNT:
            LOG.warning("BOUNDARY with more than " + str(TECH.GDSII.MAX_VERTEX_COUNT) + " coordinates not supported in structure " +  self.__current_structure__.name)
        # shape must be closed!
        if not (coordinates[0] == coordinates[-1]):
            coordinates.append(coordinates[0])
        self.collect_boundary_element(layer = item.layer, coordinates = coordinates)
        return


    def collect_Path(self, item,  additional_transform = None, **kwargs):
        shape = item.shape.transform_copy(item.transformation + additional_transform)
        shape.snap_to_grid(self.grids_per_unit)
        shape.remove_identicals()
        coordinates = Shape(shape)

        if len(coordinates) < 2:
            if self.write_empty:
                LOG.warning("PATH with fewer than 2 coordinates not allowed")
            return

        if shape.closed:
            if not (shape[-1] == shape[0]): coordinates.append(shape[0])
        
        self.collect_path_element(layer = item.layer, 
                               coordinates = coordinates, 
                               line_width = item.line_width , 
                               path_type = item.path_type)
        return


    def __scale_value__(self, value):
        return value * self.__structure_scale__

    def map_layer(self, layer):
        L = self.layer_map.get(layer, None)
        if isinstance(L, GdsiiLayer):
            return L
        elif L is None:
            return L
        else:
            return GdsiiLayer(number = L)

