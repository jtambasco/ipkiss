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

from time import localtime
import sys
import math
from binascii import b2a_hex, a2b_hex
from struct import pack
from ipkiss.io.output import OutputBasic
from ipkiss import constants
from ipkiss.geometry.shape import Shape
from ipkiss.geometry.shapes.basic import  ShapeRectangle
from ipkiss.geometry.transforms.translation import Translation
from io import BytesIO
import copy
from ipkiss.log import IPKISS_LOG as LOG
from ipcore.exceptions.exc import *
from ipkiss.primitives.fonts import *
from ipkiss.primitives import Library
import xml.etree.ElementTree as etree
import logging
from ..technology.settings import TECH

__all__ = ["OutputXml","FileOutputXml","MemoryOutputXml"]

class IpcoreOutputXmlException(IpcoreAttributeException):
    pass

class OutputXml(OutputBasic):	
    def __init__(self,  **kwargs):
        super(OutputXml, self).__init__(**kwargs)
        self.layer_map = TECH.GDSII.EXPORT_LAYER_MAP
        self.topElem = None		



    def collect(self, item,  **kwargs):   	
        self.do_collect(item, **kwargs)           
        return 	

    #FIXME - to be further implemented	
    def __collect_library_header__(self, library):
        return

    #FIXME - to be further implemented	
    def __collect_library_footer__(self):
        return

    def collect_Library(self, library,  **kwargs):
        self.__collect_library_header__(library)
        attribs = {"name": library.name}
        precision = abs(math.floor(math.log10(library.units_per_grid)))
        self.coord_format_str = "(%%.%df, %%.%df)"%(precision,precision) 
        self.topElem = self.__makeXMLElement__("IPKISSLIBRARY", attribs)
        self.referedItemsInLibrary = []
        self.collect(library.structures,  **kwargs)
        #all the items that were refered to (by SRef or ARef) should be defined in the top level, i.e. at the level of the library
        #while collecting these, the list can grow. Continue to collect, while removing duplicates and collected items
        while len(self.referedItemsInLibrary)>0:
            #remove duplicates
            self.referedItemsInLibrary = list(set(self.referedItemsInLibrary))
            self.referedItemsInLibrary.sort()
            #make a working copy
            items = list(self.referedItemsInLibrary)
            for referedItem in items:
                self.collect(referedItem)
                self.referedItemsInLibrary.remove(referedItem)
        return

    #FIXME - to be further implemented
    def __collect_structure_header__(self, item):
        return

    #FIXME - to be further implemented
    def __collect_structure_footer__(self, item):
        return

    def __makeXMLElement__(self, p_tag, p_attribs, p_parentXMLElement = None):
        '''Create an XML element as top element (without parent) or as subelement (with the given parent)'''

        #force all attribute values to string
        for k in p_attribs.keys():
            p_attribs[k] = str(p_attribs[k])

        if (p_parentXMLElement == None):
            el = etree.Element(p_tag, p_attribs) 
        else:
            el = etree.SubElement(p_parentXMLElement, p_tag, p_attribs)	
        return el


    def __makePointXMLElement(self, p_coordinate, p_parentXMLElement = None):
        '''Create an XML element representing a point on the grid (if p_parent is provided, the XML element is created as a subelement)'''
        gridsperunit = self.library.grids_per_unit
        xCo = int(p_coordinate[0]*gridsperunit)
        yCo = int(p_coordinate[1]*gridsperunit)
        attrib = {"x": xCo, "y":yCo}
        el = self.__makeXMLElement__("POINT",attrib,p_parentXMLElement)
        return el


    def __makePointlistXMLElement(self, p_tag, p_name, p_coordinates, p_layer, p_purpose, p_parentXMLElement = None, p_extraAttrib = {}):
        '''Create an XML element that groups a number of points (on given layer and purpose)'''
        n = p_coordinates.shape[0]
        attribs = {"countPoints": n, "layer": p_layer, "purpose" : p_purpose}
        attribs.update(p_extraAttrib)
        if (p_name != None):
            attribs["name"] = p_name
        pointlistXMLElement = self.__makeXMLElement__(p_tag, attribs, p_parentXMLElement)
        for pnt in p_coordinates:
            self.__makePointXMLElement(pnt, pointlistXMLElement)
        return pointlistXMLElement	


    def __makeBoundaryXMLElement(self, p_name, p_coordinates, p_layer, p_purpose, p_parentXMLElement = None):
        '''Create and XML element representing a boundary'''
        return self.__makePointlistXMLElement("BOUNDARY", p_name, p_coordinates, p_layer, p_purpose, p_parentXMLElement)	


    def __makePathXMLElement(self, p_name,  p_coordinates, p_layer, p_purpose, p_LineWidth, p_parentXMLElement = None):
        '''Create and XML element representing a shape'''
        return self.__makePointlistXMLElement("PATH", p_name, p_coordinates, p_layer, p_purpose, p_parentXMLElement, {"linewidth": p_LineWidth})	


    def __getLayerPurposeNmbr(self, p_Item):
        '''Derive the layer number and purpose number using the appropriate layer map (i.e. GDS)'''
        try:
            gdsLayer = self.layer_map.get(p_Item,None)   
            lyr = gdsLayer.number
            pur = gdsLayer.datatype
        except Exception, e:
            LOG.error("Warning: layer %s not found: %s - forcing layer number to 1." %(p_Item,e))
            lyr = 1
            pur = 100
        return (lyr,pur)	

    def collect_Label (self, item,  additional_transform = None):
        #resolve the attributes 
        T = item.transformation + additional_transform # make a copy because there is also the height
        lyrPurp = self.__getLayerPurposeNmbr(item.layer)
        lyr = lyrPurp[0]
        purp = lyrPurp[1]
        coordinates =  [T.__translate__(item.coordinate)]
        T.magnification *= item.height
        textOrigin = self.__makePointXMLElement(coordinates[0])
        textAlign = str(item.alignment)
        textFont = str(item.font)
        textHeight = int(item.height)
        #create the XML element representing the text
        attribs = {"alignment": textAlign,  "font": textFont,  "height": textHeight, "layer": lyr, "purpose" : purp, "x" : coordinates[0][0], "y" : coordinates[0][1]}
        labelElem = self.__makeXMLElement__("TEXT", attribs, self.topElem) 
        labelElem.text = item.text
        return

    def collect_Structure(self, item,  **kwargs):
        self.set_current_structure(item)		
        self.prevTopElem = self.topElem
        self.topElem = self.__makeXMLElement__("STRUCTURE", {"name" : self.name_filter(item.name)[0]}, self.prevTopElem) 	
        self.__collect_structure_header__(item)
        self.collect(item.elements, **kwargs)
        self.__collect_structure_footer__(item)
        self.topElem = self.prevTopElem
        return 


    def collect_SRef (self, item,  additional_transform = None):
        T = item.transformation + Translation(item.position) + additional_transform
        sname = self.name_filter(item.reference.name)[0]
        #sname = sname.replace("-","_").replace(" ","_").replace(".","_")
        self.__makeXMLElement__("SREF", {"referee" : sname, "transformation" : str(T)}, self.topElem) 
        self.referedItemsInLibrary.append(item.reference) #collect them add the end and add as top-level XML-elements
        return 

    def collect_ARef (self, item,  additional_transform = None):
        T = item.transformation + Translation(item.origin) + additional_transform
        aname = self.name_filter(item.reference.name)[0]
        #aname = aname.replace("-","_").replace(" ","_").replace(".","_")		
        #self.__makeXMLElement__("AREF", {"referee" : aname, "n_o_periods" : str(item.n_o_periods), "period" : str(item.period), "transformation": str(T)}, self.topElem) 		
        self.__makeXMLElement__("AREF", {"referee" : aname, "n_o_periods" : str(item.n_o_periods), "period" : self.coord_format_str%(item.period[0],item.period[1]), "transformation": str(T)}, self.topElem) 		
        self.referedItemsInLibrary.append(item.reference) #collect them add the end and add as top-level XML-elements
        return 

    def collect_BoxElement (self, item,  additional_transform = None):
        try:
            T = item.transformation + additional_transform
            coordinates = T(ShapeRectangle(item.center, item.box_size)).tolist()
            self.collect_boundary_element(item.layer, coordinates)
        except Exception, err:
            msg = "OutputXml::Fatal exception in collect_BoxElement : %s" %err
            LOG.error(msg)
            raise err
        return 



    def collect_path_element (self, layer, coordinates, line_width, path_type): 
        try:
            lyrPurp = self.__getLayerPurposeNmbr(layer)
            self.__makePathXMLElement(None, coordinates.points, lyrPurp[0], lyrPurp[1], line_width, self.topElem)   
        except Exception, err:
            msg = "OutputXml::Fatal exception in collect_path_element : %s" %err
            LOG.error(msg)	
            raise err
        return 


    def collect_boundary_element (self, layer, coordinates): 
        try:
            lyrPurp = self.__getLayerPurposeNmbr(layer)
            self.__makeBoundaryXMLElement(None, coordinates.points, lyrPurp[0], lyrPurp[1], self.topElem)
        except Exception, err:
            msg = "OutputXml::Fatal exception in collect_boundary_element : %s" %err
            LOG.error(msg)	
            raise err
        return 	

    def write(self, item):		
        self.collect(item)
        self.o_stream.write(etree.tostring(self.topElem).replace('><','>\n<'))
        self.o_stream.flush()	


class FileOutputXml(OutputXml):
    """Writes XML output to a file. The constructor takes the filename. The write() method streams the XML data to the file"""       
    def __init__(self, FileName, **kwargs):
        super(FileOutputXml, self).__init__(**kwargs)
        self.FileName = FileName
        self.Kwargs = kwargs	


    def write(self, item):
        fStr = open (self.FileName, "w")
        super(FileOutputXml, self).__init__(o_stream = fStr, **self.Kwargs)	
        super(FileOutputXml, self).write(item)
        fStr.close()


class MemoryOutputXml(OutputXml):
    """ Writes XML output to a memory buffer. The write() method returns a reference to a BytesIO object. """
    def __init__(self, **kwargs):
        bf = BytesIO()
        super(MemoryOutputXml, self).__init__(o_stream = bf, **kwargs)

    def write(self, item):
        super(MemoryOutputXml, self).write(item)
        self.o_stream.seek(0) #reset to beginning of the buffer
        return self.o_stream

