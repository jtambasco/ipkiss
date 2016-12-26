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

from .input import InputBasic
from time import mktime
from binascii import b2a_hex
from struct import unpack

from ipcore.properties.predefined import LongIntProperty
from . import gds_records
from .. import constants
from ..primitives import fonts
from ..geometry.transforms.no_distort import NoDistortTransform
from ..geometry.shape import Shape
from ..primitives.structure import Structure
from ..primitives.elements.shape import Boundary, Path
from ..primitives.elements.text import Label
from ..primitives.elements.box import Box
from ..primitives.elements.reference import SRef, ARef
from .gds_layer import GdsiiLayer
import sys
#from ipkiss.log import IPKISS_LOG as LOG
from ipkiss.exceptions.exc import IpkissException

import numpy

import logging

class MyHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        fs = "%s" if getattr(record, "continued", False) else "%s\n"
        self.stream.write(fs % msg)
        self.flush()

IPKISS_INPUT_GDSII_LOGGING_HANDLER = MyHandler(sys.stderr)

LOG = logging.getLogger("%s.INPUT_GDSII" % 'IPKISS')
LOG.propagate = False
LOG.addHandler(IPKISS_INPUT_GDSII_LOGGING_HANDLER)
IPKISS_INPUT_GDSII_LOG = LOG

__all__ = ["InputGdsii", "FileInputGdsii","LOG","InputGdsiiTree"]


class GdsiiRecord(object):
    def __init__(self,rtype, length):
        self.rtype = rtype
        self.length = length

class InputGdsiiHeader(InputBasic):
    """ Parses the header of a GDSII file """
    def __init__(self, i_stream = sys.stdin, **kwargs):
        super(InputGdsiiHeader, self).__init__(
            i_stream = i_stream,
            **kwargs)
        self.__current_structure__ = None
        #self.__stop_on_unknown_gds_layer__ = stop_on_unknown_gds_layer

    def __parse_library__ (self):
        self.__istream__ = self.i_stream
        self.__scaling__ = self.scaling
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            if t == gds_records.BgnStr:
                break
            elif t == gds_records.Header:
                self.__istream__.read(l)
            elif t == gds_records.BgnLib:
                self.library.modified = self.__parse_time__()
                self.library.accessed = self.__parse_time__()
            elif t == gds_records.Units:
                U = self.__parse_real8__()
                self.library.grid = self.__parse_real8__()
                self.library.unit = self.library.grid/U
            elif t == gds_records.LibName:
                self.library.name = self.__parse_string__(l)
            elif t == gds_records.EndLib:
                break
            elif t == gds_records.RefLibs:
                LOG.warning("REFLIBS is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.Fonts:
                LOG.warning("FONTS is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.AttrTable:
                LOG.warning("ATTRTABLE is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.Generations:
                LOG.warning("GENERATIONS is not supported. This will be ignored.")
                self.__istream__.read(l)
            else:
                LOG.error("Unsupported record type in File: %s" % hex(t))
                #FIXME -- to be investigated further -- raise SystemExit
        return self.library
    
    def __parse_record__(self):
        try:
            b1 = self.__istream__.read(2)
            datalen = int (b2a_hex(b1), 16) - 4
            b2 = self.__istream__.read(2)
            rtype = int (b2a_hex(b2), 16)
        except Exception, e:
            msg = "Could not read record : %s" %str(e)
            from ipkiss.exceptions.exc import IpkissException
            raise IpkissException(msg)
        return GdsiiRecord(rtype, datalen)

    def __parse_real8__(self):
        #value = (mantissa/(2^56)) * (16^(exponent-64))
        try:
            data = unpack(">BBHL",self.__istream__.read(8))
        except:
            LOG.error("Could not read REAL8")
            raise SystemError
        if (data[0]==0 and data[1]==0 and data[2]== 0 and data[3]==0):
            return 0.0
        if data[0] > 128:
            sign = -1
        else:
            sign = 1
        exponent = (data[0]%128 - 78)
        m1 = float(data[1] * 65536 + data[2])
        m2 = float(data[3])
        return sign * (m1*(16**8) + m2) * (16**exponent)

    def __parse_string__(self, length):
        s = ""
        t = ""
        try:
            if length > 0:
                s = self.__istream__.read(length-1)
            t = self.__istream__.read(1)
        except:
            LOG.error("Could not read STRING")
            raise SystemError
        if not b2a_hex(t) == "00":
            s += t 
        return s

    def __parse_time__(self):
        year = self.__parse_int2__()
        month= self.__parse_int2__()
        day= self.__parse_int2__()
        hour= self.__parse_int2__()
        minute= self.__parse_int2__()
        second= self.__parse_int2__()
        if year >= 100 and year < 1900:
            year += 1900
        if year < 100: 
            year = 2000
        return mktime((year, month, day, hour, minute, second, 0, 0, -1))

    def __parse_int2__(self):
        try:
            return unpack(">h",self.__istream__.read(2))[0]
        except Exception, e:
            LOG.error("Could not read INT2 : %s" %e)
            raise SystemError
    
class InputGdsiiTree(InputGdsiiHeader):
    """ Parses a GDSII file but extracts only the hierarchy """
    log_bufsize = LongIntProperty(default=0L)
    def __init__(self, i_stream = sys.stdin, stop_on_unknown_gds_layer = True, **kwargs):
        super(InputGdsiiTree, self).__init__(
            i_stream = i_stream,
            **kwargs)
        self.__current_structure__ = None
        self.__stop_on_unknown_gds_layer__ = stop_on_unknown_gds_layer

    def __parse_library__ (self):
        self.__istream__ = self.i_stream
        self.__scaling__ = self.scaling
        if self.log_bufsize>0:
            cur_percentile = 0
            percentile = self.log_bufsize/10
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            if t == gds_records.BgnStr:
                created = self.__parse_time__()
                modified = self.__parse_time__()
                self.__parse_structure__(created, modified)
            elif t == gds_records.Header:
                self.__istream__.read(l) #header is not parsed in an import
            elif t == gds_records.BgnLib:
                self.library.modified = self.__parse_time__()
                self.library.accessed = self.__parse_time__()
            elif t == gds_records.Units:
                U = self.__parse_real8__()
                self.library.grid = self.__parse_real8__()
                self.library.unit = self.library.grid/U
            elif t == gds_records.LibName:
                self.library.name = self.__parse_string__(l)
            elif t == gds_records.EndLib:
                break
            elif t == gds_records.RefLibs:
                LOG.warning("REFLIBS is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.Fonts:
                LOG.warning("FONTS is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.AttrTable:
                LOG.warning("ATTRTABLE is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.Generations:
                LOG.warning("GENERATIONS is not supported. This will be ignored.")
                self.__istream__.read(l)
            else:
                LOG.error("Unsupported record type in File: %s" % hex(t))
                #FIXME -- to be investigated further -- raise SystemExit
            if self.log_bufsize>0:
                pos = self.__istream__.tell()        
                if pos>(percentile*cur_percentile):
                    cur_percentile+=1
                    if cur_percentile<10:
                        continued = dict(continued=True)
                    else:
                        continued = dict(continued=False)
                    LOG.info('%d%% '%(cur_percentile*10),extra=continued)

        return self.library

    def __parse_structure__(self, created, modified):
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            if t == gds_records.Boundary:
                el = self.__parse_boundary_element__()
                if not (el is None):
                    S.add_el(el)
            elif t == gds_records.Path:
                el = self.__parse_path_element__()
                if not (el is None):
                    S.add_el(el)
            elif t == gds_records.SRef:
                el = self.__parse_sref_element__()
                if not (el is None):
                    S.add_el(el)              
            elif t == gds_records.ARef:
                el = self.__parse_aref_element__()
                if not (el is None):
                    S.add_el(el)              
            elif t == gds_records.Box:
                el = self.__parse_box_element__()
                if not (el is None):
                    S.add_el(el)              
            elif t == gds_records.Text:
                el = self.__parse_label_element__()
                if not (el is None):
                    S.add_el(el)              
            elif t == gds_records.StrName:
                name = self.make_structure_name(self.__parse_string__(l))
                S = Structure(name, [], self.library)
                S.__make_static__()
                S.created = created
                S.modified = modified
                S.grid = self.library.grid
                S.unit = self.library.unit
                self.__current_structure__= S
            elif t == gds_records.EndStr:
                self.__istream__.read(l)
                break
            elif t == gds_records.StrClass:
                LOG.warning("STRCLASS is not supported. This will be ignored")
                self.__istream__.read(l)
            else:
                LOG.error("Unsupported element type in Structure: %s" % hex(t))
                #FIXME -- to be investigated further -- raise IpkissException?
        return S


    def __parse_length__(self):
        ### Solve unit problem!!!        
        return self.__parse_int4__() * self.__scaling__ / self.library.grids_per_unit


    def __parse_coordinate__(self):
        s = self.__scaling__ / self.library.grids_per_unit
        return (self.__parse_int4__() * s, self.__parse_int4__() * s)

    def __parse_shape__(self,n_o_points):
        #return Shape( [ self.__parse_coordinate__() for i in range(n_o_points)])
        s = self.__scaling__ / self.library.grids_per_unit
        #p = self.__parse_int4__
        #c_list = numpy.array([(p(), p()) for i in range(n_o_points)]) * s
        coords = self.__parse_int4pairlist__(n_o_points)
        c_list =  coords * s
        return Shape(c_list)

    def __parse_int4pairlist__(self, length):
        return numpy.fromfile(file = self.__istream__, dtype = numpy.dtype('2>i4'), count = length)

    def __parse_boundary_element__(self):
        # Skip: no tree info
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            self.__istream__.read(l)
            if t == gds_records.EndEl:
                break
        return None


    def __parse_path_element__ (self):
        # Skip: no tree info
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            self.__istream__.read(l)
            if t == gds_records.EndEl:
                break
        return None

    def __parse_sref_element__(self):
        name = ""
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            if t == gds_records.SName:
                name = self.__parse_string__(l)
            elif t == gds_records.EndEl:
                break
            else:
                self.__istream__.read(l)

        if name =="":
            LOG.error("SREF: name of structure is empty")
            raise SystemExit
        else:
            name = self.make_structure_name(name)

        if self.library.structure_exists(name):
            S = self.library[name]
        else:
            # add dummy structure (which will be overwritten later)
            S = Structure(name, [], self.library)
            #S.__make_static__()
        if not S in self.__current_structure__.child_structures:
            V = SRef(S, (0,0))
            self.__current_structure__.child_structures += [S]
        else:
            V = None
        return V

    def __parse_aref_element__(self):
        return self.__parse_sref_element__()

    def __parse_box_element__(self):
        # Skip: no tree info
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            self.__istream__.read(l)
            if t == gds_records.EndEl:
                break
        return None

    def __parse_label_element__(self):
        # Skip: no tree info
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            self.__istream__.read(l)
            if t == gds_records.EndEl:
                break
        return None


    def __parse_magnification__(self, T):
        m = self.__parse_real8__()
        T.magnification = m

    def __parse_rotation__ (self, T):
        T.rotation = self.__parse_real8__()

    def __parse_transformation__(self, T):
        bits = self.__parse_int2__()
        T.v_mirror = (bits < 0)
        bits = bits % 8
        T.absolute_magnification = (bits >= 4)
        bits = bits % 4
        T.absolute_rotation = (bits >= 2)
        return 

    def __parse_int4__(self):
        try:
            return unpack(">l",self.__istream__.read(4))[0]
        except Exception, e:
            LOG.error("Could not read INT4 : %s" %e)
            raise SystemError



class InputGdsii(InputGdsiiTree):
    """ Parses a full GDSII file"""

    def __parse_boundary_element__(self):
        # read parameters
        layer_number = 0
        datatype = 0
        coords = []
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            if t == gds_records.Layer:
                layer_number = self.__parse_int2__()
            elif t == gds_records.DataType:
                datatype = self.__parse_int2__()
            elif t == gds_records.XY:
                nxy = l/8
                coords = self.__parse_shape__(nxy)
                coords.close()
            elif t == gds_records.EndEl:
                break
            elif t == gds_records.ElFlags:
                LOG.warning("ELFLAGS in BOUNDARY is not supported (structure %s). This will be ignored." % self.__current_structure__.name)
                self.__istream__.read(l)
            elif t == gds_records.Plex:
                LOG.warning("PLEX in BOUNDARY is not supported (structure %s). This will be ignored." % self.__current_structure__.name)
                self.__istream__.read(l)
            else:
                LOG.error("Unsupported type in BOUNDARY: %s" % hex(t))
                raise SystemExit
        layer = GdsiiLayer(number = layer_number, datatype = datatype)
        L = self.map_layer(layer)
        if L is None:
            err_msg = "Could not map GDS layer %d:%d in InputGdsii." %(layer.number,layer.datatype)
            if self.__stop_on_unknown_gds_layer__:
                raise IpkissException(err_msg)
            else:
                return LOG.warning(err_msg)
        else:
            return Boundary(L, coords)


    def __parse_path_element__ (self):
        # read parameters
        layer_number = 0
        datatype = 0
        pathtype = constants.PATH_TYPE_NORMAL
        width = 0
        coords = []
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            if t == gds_records.Layer:
                layer_number = self.__parse_int2__()
            elif t == gds_records.DataType:
                datatype = self.__parse_int2__()
            elif t == gds_records.PathType:
                pathtype = self.__parse_int2__()
            elif t == gds_records.Width:
                width = self.__parse_length__()
            elif t == gds_records.XY:
                nxy = l/8
                coords = self.__parse_shape__(nxy)
            elif t == gds_records.EndEl:
                self.__istream__.read(l)
                break
            elif t == gds_records.ElFlags:
                LOG.warning("ELFLAGS in PATH is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.Plex:
                LOG.warning("PLEX in PATH is not supported. This will be ignored.")
                self.__istream__.read(l)
            else:
                LOG.error("Unsupported type in PATH: %s" % hex(t))
                raise SystemExit
        layer = GdsiiLayer(number = layer_number, datatype = datatype)
        L = self.map_layer(layer)
        if L is None:
            err_msg = "Could not map GDS layer %s in InputGdsii." %str(layer)
            if self.__stop_on_unknown_gds_layer__:
                raise IpkissException(err_msg)
            else:
                return LOG.error(err_msg)
        else:
            return Path(L, coords, width, pathtype)

    def __parse_sref_element__(self):
        name = ""
        coord = (0.0, 0.0)
        transform = NoDistortTransform()
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            if t == gds_records.SName:
                name = self.__parse_string__(l)
            elif t == gds_records.XY:
                nxy = l/8
                if not nxy == 1:
                    LOG.error("SREF only supports a single coordinate.")
                    raise SystemExit
                coord = self.__parse_coordinate__()
            elif t == gds_records.EndEl:
                break
            elif t == gds_records.ElFlags:
                LOG.warning("ELFLAGS in SREF is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.Plex:
                LOG.warning("PLEX in SREF is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.STrans:
                self.__parse_transformation__(transform)
            elif t == gds_records.Mag:
                self.__parse_magnification__(transform)
            elif t == gds_records.Angle:
                self.__parse_rotation__(transform)
            else:
                LOG.error("Unsupported type in SREF: %s" % hex(t))
                raise SystemExit

        if name =="":
            LOG.error("SREF: name of structure is empty")
            raise SystemExit
        else:
            name = self.make_structure_name(name)

        if self.library.structure_exists(name):
            S = self.library[name]
        else:
            # add dummy structure (which will be overwritten later)
            S = Structure(name, [], self.library)
            S.__make_static__()
        self.library.set_referenced(S)
        V = SRef(S, coord, transform)
        return V

    def __parse_aref_element__(self):
        name = ""
        coord_zero = (0.0, 0.0)
        coord_x = (0.0, 0.0)
        coord_y = (0.0, 0.0)
        col = 1
        row = 1
        transform = NoDistortTransform()
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength
            if t == gds_records.ColRow:
                col = self.__parse_int2__()
                row = self.__parse_int2__()
                if col <= 0 or row <=0:
                    LOG.error("Invalid COLROW in AREF")
                    raise SystemExit
            elif t == gds_records.SName:
                name = self.__parse_string__(l)
            elif t == gds_records.XY:
                nxy = l/8
                if not nxy == 3:
                    LOG.error("gdsii_error: AREF supports exactly three coordinates.")
                    raise SystemExit
                coord_zero = self.__parse_coordinate__()
                coord_x = self.__parse_coordinate__()
                coord_y = self.__parse_coordinate__()
            elif t == gds_records.EndEl:
                break
            elif t == gds_records.ElFlags:
                LOG.warning("ELFLAGS in AREF is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.Plex:
                LOG.warning("PLEX in AREF is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.STrans:
                self.__parse_transformation__(transform)
            elif t == gds_records.Mag:
                self.__parse_magnification__(transform)
            elif t == gds_records.Angle:
                self.__parse_rotation__(transform)
            else:
                LOG.error("Unsupported type in AREF: %s" % hex(t))
                raise SystemExit

        coordinates = Shape([coord_zero, coord_x, coord_y])
        cc= self.library.snap_shape(transform.reverse(coordinates.move_copy((-coord_zero[0], -coord_zero[1]))))
        if (not cc[1][1] == 0.0) or (not cc[2][0] == 0.0):
            LOG.error("Coordinates in AREF do not match Transformation STRANS, MAG, ANGLE in structure %s " % self.__current_structure__.name)

        if name =="":
            LOG.error("AREF: name of structure is empty")
            raise SystemExit
        else:
            name = self.make_structure_name(name)

        if self.library.structure_exists(name):
            S = self.library[name]
        else:
            # add dummy structure (which will be overwritten later)
            S = Structure(name, [], self.library)
            S.__make_static__()
        self.library.set_referenced(S)        
        # try to fix arefs with negative period
        czx = coord_zero[0]
        px = cc[1][0]
        py = cc[2][1]
        czy = coord_zero[1]
        coord_zero = (czx, czy)
        period = (px/col, py/row)

        origin = (czx, czy)
        V = ARef(S, origin, period, (col, row), transform)
        return V

    def __parse_box_element__(self):
        # read parameters
        layer_number = 0
        boxtype = 0
        coords = []
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datalength

            if t == gds_records.Layer:
                layer_number = self.__parse_int2__()
            elif t == gds_records.BoxType:
                boxtype = self.__parse_int2__()
            elif t == gds_records.XY:
                nxy = l/8
                coords = self.__parse_shape__(nxy)
            elif t == gds_records.EndEl:
                break
            elif t == gds_records.ElFlags:
                LOG.warning("ELFLAGS in BOX is not supported. This will be ignored")
                self.__istream__.read(l)
            elif t == gds_records.Plex:
                LOG.warning("PLEX in BOX is not supported. This will be ignored")
                self.__istream__.read(l)
            else:
                LOG.error("Unsupported type in BOX: %s" % hex(t))
                raise SystemExit
        c = coords[0]
        xmin = c[0]
        ymin = c[1]
        xmax = c[0]
        ymax = c[1]
        for c in coords:
            xmin = min(xmin, c[0])
            ymin = min(ymin, c[1])
            xmax = max(xmax, c[0])
            ymax = max(ymax, c[1])
        layer = GdsiiLayer(number = layer_number, datatype = 0)
        L = self.map_layer(layer)
        if L is None:
            err_msg = "Could not map GDS layer %s in InputGdsii." %str(layer)
            if self.__stop_on_unknown_gds_layer__:
                raise IpkissException(err_msg)
            else:
                return LOG.error(err_msg)
        else:
            return Box(L, (0.5*(xmin+xmax), 0.5*(ymin+ymax)), (xmax-xmin, ymax-ymin))

    def __parse_label_element__(self):
        # read parameters
        transform = NoDistortTransform()
        layer_number = 0
        texttype = 0
        font = fonts.TEXT_FONT_DEFAULT
        ver_alignment = constants.TEXT_ALIGN_TOP
        hor_alignment = constants.TEXT_ALIGN_LEFT
        text = ""
        width = 1.0
        coords = []
        height = 1.0
        while 1:
            r = self.__parse_record__()
            t = r.rtype #type
            l = r.length #datatype
            if t == gds_records.Layer:
                layer_number = self.__parse_int2__()
            elif t == gds_records.TextType:
                datatype = self.__parse_int2__()
            elif t == gds_records.PathType:
                pathtype = self.__parse_int2__()
            elif t == gds_records.Presentation:
                presentation = self.__parse_int2__()
                hor_alignment = presentation % 4
                ver_alignment = (presentation - hor_alignment) % 16 / 4
                font = (presentation - hor_alignment - 4 * ver_alignment) % 64 / 16
            elif t == gds_records.Width:
                width = self.__parse_length__()
            elif t == gds_records.XY:
                nxy = l/8
                if not nxy == 1:
                    LOG.error("TEXT (Label) only supports a single coordinate. ")
                    raise SystemExit
                coord = self.__parse_coordinate__()
            elif t == gds_records.String:
                text = self.__parse_string__(l)
            elif t == gds_records.EndEl:
                break
            elif t == gds_records.ElFlags:
                LOG.warning("ELFLAGS in TEXT (Label) is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.Plex:
                LOG.warning("PLEX in TEXT (Label) is not supported. This will be ignored.")
                self.__istream__.read(l)
            elif t == gds_records.STrans:
                self.__parse_transformation__(transform)
            elif t == gds_records.Mag:
                self.__parse_magnification__(transform)
            elif t == gds_records.Angle:
                self.__parse_rotation__(transform)
            else:
                LOG.error("Unsupported type in TEXT (label): %s" % hex(t))
                raise SystemExit
        if layer_number != None:    
            layer = GdsiiLayer(number = layer_number, datatype = 0)
            L = self.map_layer(layer)
            if L is None:
                err_msg = "Could not map GDS layer %s in InputGdsii." %str(layer)
                if self.__stop_on_unknown_gds_layer__:
                    raise IpkissException(err_msg)
                else:
                    return LOG.error(err_msg)
            else:
                return Label (L, text, coord, (hor_alignment, ver_alignment) , font, 1.0, transform)
        else:
            return None




class FileInputGdsii(InputGdsii):
    def __init__(self, FileName, **kwargs):
        self.FileName = FileName
        self.Kwargs = kwargs

    def read(self):
        fStr = open (self.FileName, "rb")
        super(FileInputGdsii, self).__init__(i_stream = fStr, **self.Kwargs)
        lib = super(FileInputGdsii, self).read()
        fStr.close()
        return lib


class GzipInputGdsii(InputGdsii):
    def __init__(self, FileName, **kwargs):
        self.FileName = FileName
        self.Kwargs = kwargs

    def read(self):
        from gzip import GzipFile
        fStr = GzipFile(self.FileName, mode = 'rb')   
        super(GzipInputGdsii, self).__init__(__istream = fStr, **self.Kwargs)       
        lib = super(GzipInputGdsii, self).read()
        fStr.close()
        return lib    



