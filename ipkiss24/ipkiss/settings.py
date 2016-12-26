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

from math import floor

LIB_NAME = "IPKISS"
LIB_DESCRIPTION = "IPKISS: The Mask maker"
VERSION = "version 2.4-alpha"
COPYRIGHT_INFO = "copyright Ghent University, INTEC Photonics Research Group, 2002-2011 (i-depot BBIE 7396, 7556, 7748)"
AUTHOR = "Wim Bogaerts, Pieter Dumon, Antonio Ribeiro, Emmanuel Lambert"
AUTHOR_EMAIL = "ipkiss@intec.ugent.be"

START_MESSAGE = "%s %s - %s" % (LIB_NAME, VERSION, COPYRIGHT_INFO)

global Default_Library 
Default_Library = None
__Ipkiss_Current_Library = None
__Ipkiss_Layer_List = None

#----------------------------------------------------------------------------
#Set library and output
#----------------------------------------------------------------------------
def initialize():
    from .primitives.library import Library
    from .io.output_gdsii import OutputGdsii
    from .primitives.layer import LayerList
    from .technology.settings import TECH
    global Default_Library 
    Default_Library = Library("GK_Default", unit = TECH.METRICS.UNIT, grid = TECH.METRICS.GRID)
    set_current_library(Default_Library)
    __set_current_layerlist__(LayerList())

def get_current_library():
    """Return the current library to which new structures are added by default."""
    k = __Ipkiss_Current_Library
    if k == None: 
        initialize()
    return __Ipkiss_Current_Library

def set_current_library(library):
    """Sets the current library to which new structures are added by default."""    
    global __Ipkiss_Current_Library
    __Ipkiss_Current_Library = library   
        
def clear_current_library():
    """Make the current library completely empty."""    
    clib = get_current_library()
    if clib != None:
        clib.clear()

def get_current_layerlist():
    """Retrieve the list of all layers that were created in Ipkiss."""
    k = __Ipkiss_Layer_List
    from .primitives.layer import LAYER_LIST
    if k is None: 
        return LAYER_LIST
    return __Ipkiss_Layer_List

def __set_current_layerlist__(layerlist):
    """Set the list global list of all layers."""    
    global __Ipkiss_Layer_List
    __Ipkiss_Layer_List = layerlist



#----------------------------------------------------------------------------
# Getting and Setting library variables
#----------------------------------------------------------------------------

def get_grids_per_unit(library=None):
        if library is None:
            library = get_current_library()
        return library.grids_per_unit

def snap_value(value, grids_per_unit=None):
    """round a distance to a grid value"""
    if grids_per_unit is None:
        grids_per_unit = get_grids_per_unit()
    return floor(value * grids_per_unit + 0.5) / (grids_per_unit)    

def snap_coordinate(coordinate, grids_per_unit=None):
    """round a coordinate to a grid value"""    
    from .geometry.coord import Coord2
    if grids_per_unit is None:
        grids_per_unit = get_grids_per_unit()
    return Coord2(floor(coordinate[0] * grids_per_unit + 0.5) / (grids_per_unit),
                               floor(coordinate[1] * grids_per_unit + 0.5) / (grids_per_unit))

def snap_shape(coordinates, grids_per_unit=None):
    """round the coordinates of a shape to a grid value"""
    if grids_per_unit is None:
        grids_per_unit == get_grids_per_unit()
    from .geometry.shape import Shape
    sh = Shape(coordinates).snap_to_grid(grids_per_unit)
    return sh

def snap_points(points, grids_per_unit=None):
    """round a list of points to a grid value"""
    if grids_per_unit is None: grids_per_unit == get_grids_per_unit()
    from .geometry.shape import Shape
    pts = (floor(points * grids_per_unit + 0.5)) / grids_per_unit        
    return pts

#----------------------------------------------------------------------------
#Setting global variables
#----------------------------------------------------------------------------

def get_angle_step(library=None):
    """return the angle step which is applicable in the current default library"""
    if library is None:
        library = get_current_library()
    return library.technology.METRICS.ANGLE_STEP


