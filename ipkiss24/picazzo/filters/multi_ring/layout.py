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

########################################################################
# filters with multiple rings
########################################################################
from ipkiss.all import *

__all__ = ["MultiRingRectNotchFilter",
           "MultiRingRect180DropFilter"
           ]

############################################################
# Most common notch filters
############################################################

def MultiRingRectNotchFilter(coupler_spacings, 
                               ring_wg_definition = TECH.WGDEF.WIRE,
                               coupler_wg_definition = TECH.WGDEF.WIRE,
                               bend_radius= TECH.WG.BEND_RADIUS, 
                               straights = (TECH.WG.SHORT_STRAIGHT, TECH.WG.SHORT_STRAIGHT), 
                               **kwargs):
    """ Notch filter with stacked identical rect rings, with adjustable spacings """
    first = _r.RingRectNotchFilter(coupler_spacings = [coupler_spacings[0]], 
                                   bend_radius = bend_radius, 
                                   straights = straights, 
                                   ring_wg_definition = ring_wg_definition,
                                   coupler_wg_definitions = coupler_wg_definitions,
                                   **kwargs)
    middle = _r.RingRect(bend_radius = bend_radius, 
                         straights = straights, 
                         ring_wg_definition = ring_wg_definition,
                         **kwargs)
    return _mrb.MultiRingIdenticalWithChangedInAndOutWithGaps(ring_middle = middle, 
                                                              ring_in = first, 
                                                              ring_out = middle, 
                                                              spacings = self.spacings[1:])

############################################################
# Most common drop filters
############################################################

def MultiRingRect180DropFilter(coupler_spacings, 
                               ring_wg_definition = TECH.WGDEF.WIRE,
                               coupler_wg_definitions = [TECH.WGDEF.WIRE,TECH.WGDEF.WIRE],
                               bend_radius= TECH.WG.BEND_RADIUS, 
                               straights = (TECH.WG.SHORT_STRAIGHT, TECH.WG.SHORT_STRAIGHT), 
                               **kwargs):
    """ Notch filter with stacked identical rect rings, with adjustable spacings """
    first = _r.RingRectNotchFilter(coupler_spacings = [coupler_spacings[0]], 
                                   bend_radius = bend_radius, 
                                   straights = straights, 
                                   ring_wg_definition = ring_wg_definition,
                                   coupler_wg_definitions = [coupler_wg_definitions[0]],
                                   **kwargs)
    middle = _r.RingRect(bend_radius = bend_radius, 
                         straights = straights, 
                         ring_wg_definition = ring_wg_definition,
                         **kwargs)
    last = _r.RingRectNotchFilter(coupler_spacings = [coupler_spacings[-1]], 
                                  bend_radius = bend_radius, 
                                  straights = straights, 
                                  ring_wg_definition = ring_wg_definition,
                                  coupler_wg_definitions = [coupler_wg_definitions[-1]],
                                  **kwargs)
    return _mrb.MultiRingIdenticalWithChangedInAndOutWithSpacings(ring_middle = middle, 
                                                              ring_in = first, 
                                                              ring_out = last, 
                                                              spacings = coupler_spacings[1:-1], 
                                                              flip_last = True)


