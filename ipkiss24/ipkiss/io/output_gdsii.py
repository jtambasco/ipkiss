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


from .output import OutputBasic
from time import localtime
import sys
import math
from binascii import b2a_hex, a2b_hex
from struct import pack
from .. import constants
from ..geometry.shape import Shape
from ..geometry.shapes.basic import  ShapeRectangle
from ..geometry.transforms.translation import Translation
from ..geometry.coord import *
from ipkiss.primitives import Library
from . import gds_records
from .collector import StreamA2BHexCollector
from ipkiss.log import IPKISS_LOG as LOG
import logging
from io import BytesIO
from output_xml import FileOutputXml
import numpy as np
from ipcore.properties.predefined import BoolProperty, RestrictedProperty
from ipcore.properties.restrictions import RestrictType
from ipkiss.primitives.elements import ElementList
from ipkiss.primitives.elements.reference import SRef
from ipkiss.primitives.filter import Filter
from ipkiss.technology import get_technology
import copy

TECH = get_technology()

__all__ = ["OutputGdsii","FileOutputGdsii", "MemoryOutputGdsii", "FileOutputXmlWithGDSFilters"]

class OutputGdsii(OutputBasic):
        """ Writes GDS output to a stream """
        userefcache = BoolProperty(default=False)
        name_filter = RestrictedProperty(default = TECH.GDSII.NAME_FILTER, restriction = RestrictType(Filter), doc = "filter class which is applied to all names")
        
        def __init__(self, o_stream = sys.stdout, **kwargs):
                kwargs["allow_unmatched_kwargs"] = True
                super(OutputGdsii, self).__init__(o_stream = o_stream,**kwargs)
                if 'flatten_structure_container' in kwargs:
                        self.flatten_structure_container = kwargs.get('flatten_structure_container')
                elif hasattr(TECH.GDSII, 'FLATTEN_STRUCTURE_CONTAINER'):
                        self.flatten_structure_container = TECH.GDSII.FLATTEN_STRUCTURE_CONTAINER
                else:
                        self.flatten_structure_container = False                        
                self.__ref_referenced_structures__ = set()
                if sys.platform == "win32":
                        import os
                        import msvcrt
                        msvcrt.setmode(self.o_stream.fileno(), os.O_BINARY)
                        
        def __init_collector__(self):
                self.collector = StreamA2BHexCollector(o_stream = self.o_stream)
                
        def collect(self, item,  **kwargs):    
                self.do_collect(item, **kwargs)           
                return                 

        #----------------------------------------------------------------------------
        #Layout-level output functions
        #----------------------------------------------------------------------------
        
        def collect_Library(self, library, **kwargs):
                self.__collect_library_header__(library)
                unreferenced_structures = self.library.unreferenced_structures(usecache = self.userefcache)
                referenced_structures = self.library.referenced_structures(usecache = self.userefcache)
                self.collect(unreferenced_structures,  **kwargs)  
                collected_referenced_structures = []
                while len(self.__ref_referenced_structures__)>0:
                        for rs in referenced_structures:
                                if rs in self.__ref_referenced_structures__:
                                        self.collect(rs, **kwargs)     
                                        collected_referenced_structures.append(rs)
                        for crs in collected_referenced_structures:
                                referenced_structures.remove(crs)    
                        self.__ref_referenced_structures__.clear()
                self.__collect_library_footer__()
                return        
              

        def __collect_library_header__(self, library):
                self.collector+= [__str_record__(gds_records.Header, __hex_int2__(5)),
                         __str_record__(gds_records.BgnLib, __hex_date__(library.modified) + __hex_date__(library.accessed)),
                         __str_record__(gds_records.LibName, __hex_text__(library.name)),
                         __str_record__(gds_records.Units, __hex_float__(self.library.grid/self.library.unit) + __hex_float__(self.library.grid))
                 ]
                return

        def __collect_library_footer__(self):
                self.library = None
                self.collector += [__str_record__(gds_records.EndLib)]
                return

        def __collect_structure_header__(self, item):
                sname = self.name_filter(item.name)[0]
                self.collector += [__str_record__(gds_records.BgnStr, __hex_date__(item.created) + __hex_date__(item.modified)),
                             __str_record__(gds_records.StrName, __hex_text__(sname))
                                    ]

        #generate the footer for any structure
        def __collect_structure_footer__(self, item):
                self.collector += [__str_record__(gds_records.EndStr)]
                return

        #----------------------------------------------------------------------------
        #__Element__ level output functions
        #----------------------------------------------------------------------------

        #text
        def collect_Label (self, item,  additional_transform = None):
                T = item.transformation + additional_transform # make a copy because there is also the height
                layer = self.map_layer(item.layer)
                if layer is None:
                        return
                coordinates =  [T.__translate__(item.coordinate)]
                T.magnification *= item.height
                self.collector += [__str_record__(gds_records.Text),
                                   self.__str_layer__(layer.number),
                                   __str_record__(gds_records.TextType, __hex_int2__(0)),
                                   __str_record__(gds_records.Presentation, __hex_int2__((item.h_alignment + 4 * item.v_alignment + 8 * item.font%4))),
                                   __str_record__(gds_records.PathType, __hex_int2__(1))]
                self.collector += __list_transformation__(T)
                self.collector += [self.__str_coordinatelist__(coordinates),
                                   __str_record__(gds_records.String, __hex_text__(item.text)),
                                   __str_record__(gds_records.EndEl)]
                return

        #references
        def collect_SRef (self, item, additional_transform = None):
                T = item.transformation + Translation(item.position.snap_to_grid()) + additional_transform
                coordinates = Shape((0.0, 0.0)).transform(T)
                sname = self.name_filter(item.reference.name)[0]
                self.collector += [__str_record__(gds_records.SRef),
                                   __str_record__(gds_records.SName, __hex_text__(sname))]
                self.collector += __list_transformation__(T)
                self.collector += [self.__str_coordinatelist__(coordinates), 
                                   __str_record__(gds_records.EndEl)
                      ]
                self.__ref_referenced_structures__.add(item.reference)
                
        def collect_ARef (self, item,  additional_transform = None):
                T = item.transformation + Translation(item.origin) + additional_transform
                p = Coord2(item.period).snap_to_grid()
                corner1 = Coord2(item.n_o_periods[0] * p[0], 0.0)
                corner2 = Coord2(0.0, item.n_o_periods[1] * p[1])
                coordinates = Shape([(0.0, 0.0), corner1,corner2]).transform(T)
                sname = self.name_filter(item.reference.name)[0]
                self.collector += [__str_record__(gds_records.ARef),
                                   __str_record__(gds_records.SName, __hex_text__(sname))]
                self.collector += __list_transformation__(T)
                self.collector += [__str_record__(gds_records.ColRow, __hex_int2__(item.n_o_periods[0]) + __hex_int2__(item.n_o_periods[1])),
                                   self.__str_coordinatelist__(coordinates), 
                              __str_record__(gds_records.EndEl)]
                self.__ref_referenced_structures__.add(item.reference)
                return 

        def collect_BoxElement (self, item,  additional_transform = None):
                T = item.transformation + additional_transform
                layer = self.map_layer(item.layer)
                if layer is None:
                        return
                coordinates = T(ShapeRectangle(item.center, item.box_size)).tolist()
                self.collector += [__str_record__(gds_records.Box),
                             self.__str_layer__(layer.number),
                             __str_record__ (gds_records.BoxType, __hex_int2__(0)), 
                             self.__str_coordinatelist__(coordinates), 
                             __str_record__(gds_records.EndEl)]
                return 

        def collect_path_element (self, layer, coordinates, line_width, path_type):
                L = self.map_layer(layer)
                if L is None:
                        return
                self.collector += [__str_record__ (gds_records.Path),
                            self.__str_layer__(L.number),
                            self.__str_datatype__(L.datatype),
                            __str_record__ (gds_records.PathType, __hex_int2__(path_type)),
                            __str_record__ (gds_records.Width, __hex_int4__(self.__db_value__(line_width))),
                            self.__str_shape__(coordinates),
                            __str_record__(gds_records.EndEl)]
                return 

        def collect_boundary_element (self, layer, coordinates):
                L = self.map_layer(layer)
                if L is None:
                        return

                self.collector += [__str_record__ (gds_records.Boundary),
                            self.__str_layer__(L.number),
                            self.__str_datatype__(L.datatype),
                            self.__str_shape__(coordinates),
                            __str_record__(gds_records.EndEl)
                    ]
                return 
        
        def __collect_container_elements__(self, item, sref_level_counter):
                # FIXME. Containers are PICAZZO classes. This method should be converted to a Filter or a mixin
                from picazzo.container.container import __StructureContainer__
                from ipkiss.primitives.elements.reference import __RefElement__
                if isinstance(item, __StructureContainer__) and isinstance(item.elements[0],__RefElement__):                        
                        sref = item.elements[0]  
                        sref_elements = sref.reference.elements
                        sref_transformation = sref.transformation + Translation(translation = sref.position)
                        sref_elements_transformed = sref_elements.transform_copy(transformation = sref_transformation)                        
                        new_elements = ElementList()
                        if (isinstance(sref.reference, __StructureContainer__)):
                                (inner_container_elements, sref_level_counter) = self.__collect_container_elements__(sref.reference, sref_level_counter + 1)                        
                                new_elements.extend(inner_container_elements)
                                if len(item.elements)>1:
                                        new_elements.extend(item.elements[1:])
                        else:
                                new_elements.extend(sref_elements_transformed)
                                if len(item.elements)>1:
                                        new_elements.extend(item.elements[1:])
                        return (new_elements, sref_level_counter)
                else:
                        return (item.elements, sref_level_counter)                              
                       
        def collect___StructureContainer__(self, item):
                # FIXME. Containers are PICAZZO classes. This method should be converted to a Filter or a mixin
                from ipkiss.primitives.elements.reference import __RefElement__
                if self.flatten_structure_container and isinstance(item.elements[0],__RefElement__):
                        sref = item.elements[0]
                        (new_elements, sref_levels) = self.__collect_container_elements__(item = item, sref_level_counter = 1)   
                        sref_transformation = sref.transformation + Translation(translation = sref.position)
                        new_elements_transformed = new_elements.transform_copy(transformation = sref_transformation)
                        if sref_levels >= 1:
                                if len(item.elements)>1:
                                        new_elements_transformed.extend(item.elements[1:]) 
                                item.__make_static__()
                                item.elements = new_elements_transformed
                                item.__make_dynamic__()
                self.collect_Structure(item)

        #----------------------------------------------------------------------------
        # unit conversion
        #----------------------------------------------------------------------------

        def __db_value__(self, value):
                #convents absolute coordinates to database units
                return round(value * self.__structure_scale__ * self.grids_per_unit)
        
        def __db_value_array__(self, value_array): #faster, direct operation on numpy array
                result = np.round(value_array * self.__structure_scale__ * self.grids_per_unit)
                return result

        #generate coordinate strings from a shape or list of coordinates
        def __str_coordinatelist__ (self, coords):                
                if isinstance(coords, Shape):
                        db_value_coordinates = self.__db_value_array__(coords.points)                        
                        ret_data = ["%s%s" % (__hex_int4__(c0) , __hex_int4__(c1)) for c0,c1 in db_value_coordinates]
                else: 
                        ret_data = ["%s%s" % (__hex_int4__(self.__db_value__(c[0])) , __hex_int4__(self.__db_value__(c[1]))) for c in coords]
                return __str_record__(gds_records.XY, "".join(ret_data))
                        
                
        def __str_shape__ (self, coordinates):
                db_value_points = self.__db_value_array__(coordinates.points.ravel())
                ret_data = [__hex_int4__(p) for p in db_value_points]
                return __str_record__(gds_records.XY, "".join(ret_data))

        def __collect_shape__ (self, coordinates):
                db_value_points = self.__db_value_array__(coordinates.points.ravel())
                ret_data = [__hex_int4__(p) for p in db_value_points]
                self.collector +=  [__str_record__(gds_records.XY, "".join(ret_data))]
        
        def __str_layer__(self, layer_number):
                return __str_record__(gds_records.Layer, __hex_int2__(layer_number))		

        def __str_datatype__(self, datatype):
                return __str_record__(gds_records.DataType, __hex_int2__(datatype))


class FileOutputGdsii(OutputGdsii):
        """Writes GDS2 output to a file. The constructor takes the filename. The write() method streams the GDS2 data to the file"""       
        def __init__(self, FileName, **kwargs):
                self.FileName = FileName
                super(FileOutputGdsii, self).__init__(**kwargs)
            
        def write(self, item):
                fStr = open(self.FileName, "wb")
                self.o_stream = fStr
                self.collector.o_stream = fStr
                self.o_stream.write(self.str(item))
                self.o_stream.flush()
                fStr.close()
                
    
class GzipOutputGdsii(OutputGdsii):
        """Writes GDS2 output to a GZIP file. The constructor takes the filename. The write() method streams the GDS2 data to the file"""       
        def __init__(self, FileName, **kwargs):
                self.FileName = FileName
                super(GzipOutputGdsii, self).__init__(**kwargs)
            
        def write(self, item):    
                from gzip import GzipFile
                fStr =  GzipFile(self.FileName, mode = 'wb')
                self.o_stream = fStr
                self.collector.o_stream = fStr
                self.o_stream.write(self.str(item))
                self.o_stream.flush()
                fStr.close()  
                
                
class FileOutputXmlWithGDSFilters(FileOutputXml):
        """Writes XML output to a file, but with the data filtered according to GDS standards"""        
        name_filter = RestrictedProperty(default = TECH.GDSII.NAME_FILTER, restriction = RestrictType(Filter), doc = "filter class which is applied to all names")
        def __init__(self, FileName, **kwargs):
                super(FileOutputXmlWithGDSFilters, self).__init__(FileName, **kwargs)		
        
class MemoryOutputGdsii(OutputGdsii):
        """ Writes GDS2 output to a memory buffer. The write() method returns a reference to a BytesIO object. """
        def __init__(self, **kwargs):
                buffer = BytesIO()
                super(MemoryOutputGdsii, self).__init__(o_stream = buffer, **kwargs)
        
        def write(self, item):
                self.o_stream.write(self.str(item))
                self.o_stream.flush()
                self.o_stream.seek(0) #reset to beginning of the buffer
                return self.o_stream
        
        
#----------------------------------------------------------------------------
# Low-level output
#----------------------------------------------------------------------------

#Generate record
def __str_record__(record_type, hex_data=""):
        length = len(hex_data)/2 + 4
        return ''.join([__hex_int2__(length), __hex_int2__(record_type), hex_data]) #fastest string concatenation

def __hex_int2__ (number):
        return __hex_text__(pack(">H",number))

def __hex_int4__ (number):
        return b2a_hex(pack(">l",number))

def __hex_float__(number):
        B1 = 0
        B2 = 0
        S3 = 0
        L4 = 0
        if not number == 0:
                if number < 0:
                        B1 = 128
                        number = abs(number)
                E = int(math.ceil(math.log(number)/math.log(16)))
                inumber = long(number * 16L**(-E+14))
                B1 += E+64
                B2 = (inumber/281474976710656)%256
                if B2 == 0:
                        B2 = 16
                        B1 += 1
                S3 = (inumber%281474976710656)/4294967296L
                L4 = inumber%4294967296L
        return __hex_text__(pack(">BBHL",B1, B2, S3, L4))

def __hex_text__ (text):
        t = b2a_hex(text)
        if not len(t)%4 == 0:
                t += "00"
        return t

#Create the date strings
def __hex_date__(T = None):
        if T is None: T = time()
        t = localtime(T)
        ret_data = [__hex_int2__(t[0]%100),
                    __hex_int2__(t[1]),
                    __hex_int2__(t[2]),
                    __hex_int2__(t[3]),
                    __hex_int2__(t[4]),
                    __hex_int2__(t[5])
            ]
        return "".join(ret_data)

#Generate comment in the Key file
def __list_comment__(text):
        #not available n GDSII. Supported for compatibility with Key
        return ""

def __list_transformation__(transform):
        strans = 0
        flip = transform.flip
        rotation = transform.rotation

        if flip:
                strans += 32768
        if transform.absolute_rotation:
                strans += 2
        if transform.absolute_magnification:
                strans += 4

        if isinstance(transform.magnification, tuple):
                T = transform.magnification[0]
        else:
                T = transform.magnification

        return [__str_record__(gds_records.STrans, __hex_int2__(strans)),
                __str_record__(gds_records.Mag, __hex_float__(T)),
                __str_record__(gds_records.Angle, __hex_float__(rotation))
        ]
