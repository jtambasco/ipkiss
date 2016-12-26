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
from ipkiss.plugins.photonics.wg.connect import *
from .basic import Route


__all__ = ["RouteConnectorRounded",
           "RouteConnectorManhattan",
           "RouteConnector",
           "RouteConnectorExpanded",
           "RouteConnectorRoundedExpanded",
           "RouteConnectorManhattanExpanded"]

def RouteConnector(route, process=TECH.PROCESS.WG, manhattan = False):
    # make sure it is not an oridinary shape. if so, use default values    
    if hasattr(route, "input_port"):
        wg_def = route.input_port.wg_definition
    else:
        wg_def = TECH.WGDEF.DEFAULT
    if hasattr(route, "bend_radius"):
        bend_radius = route.bend_radius
    else:
        bend_radius = TECH.WG.BEND_RADIUS
    if hasattr(route, "rounding_algorithm"):
        ra = route.rounding_algorithm
    else:
        ra = ShapeRound
    connector_wg_def = WaveguidePointRoundedConnectElementDefinition(wg_definition = wg_def,
                                                           bend_radius = bend_radius,
                                                           manhattan = manhattan,
                                                           rounding_algorithm = ra)     
    return connector_wg_def(shape = route)


def RouteConnectorRounded(route, process=TECH.PROCESS.WG):
    return RouteConnector(route, process, manhattan = False)

def RouteConnectorManhattan(route, process=TECH.PROCESS.WG):
    return RouteConnector(route, process, manhattan = True)


def RouteConnectorExpanded(route, 
                           expanded_width = TECH.WG.EXPANDED_WIDTH, 
                           taper_length = TECH.WG.EXPANDED_TAPER_LENGTH, 
                           min_wire_length = TECH.WG.SHORT_STRAIGHT, 
                           process=TECH.PROCESS.WG, 
                           manhattan = False):
    # make sure it is not an oridinary shape. if so, use default values
    if hasattr(route, "input_port"):
        wg_def = route.input_port.wg_definition
    else:
        wg_def = TECH.WGDEF.DEFAULT
    if hasattr(route, "bend_radius"):
        bend_radius = route.bend_radius
    else:
        bend_radius = TECH.WG.BEND_RADIUS
    if hasattr(route, "rounding_algorithm"):
        ra = route.rounding_algorithm
    else:
        ra = ShapeRound
    
    connector_wg_def = WaveguidePointRoundedExpandedConnectElementDefinition(wg_definition = wg_def,
                                                           expanded_width = expanded_width,
                                                           bend_radius = bend_radius,
                                                           manhattan = manhattan,
                                                           taper_length = taper_length,
                                                           min_wire_length = min_wire_length,
                                                           rounding_algorithm = ra)
    return connector_wg_def(shape = route)
    


def RouteConnectorRoundedExpanded(route, 
                                  expanded_width = TECH.WG.EXPANDED_WIDTH, 
                                  taper_length = TECH.WG.EXPANDED_TAPER_LENGTH, 
                                  min_wire_length = TECH.WG.SHORT_STRAIGHT, 
                                  process=TECH.PROCESS.WG):
    return RouteConnectorExpanded(route, 
                                  expanded_width,
                                  taper_length, 
                                  min_wire_length,
                                  process,
                                  manhattan = False)

def RouteConnectorManhattanExpanded(route, 
                                    expanded_width = TECH.WG.EXPANDED_WIDTH, 
                                    taper_length = TECH.WG.EXPANDED_TAPER_LENGTH, 
                                    min_wire_length = TECH.WG.SHORT_STRAIGHT, 
                                    process=TECH.PROCESS.WG):
    return RouteConnectorExpanded(route, 
                                  expanded_width,
                                  taper_length, 
                                  min_wire_length,
                                  process,
                                  manhattan = True)
 