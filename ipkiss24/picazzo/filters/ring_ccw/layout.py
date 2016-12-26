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
# Coupled Cavity Waveguides
########################################################################

from ..ring import RingRectSymmNotchFilter, RingRect
from ..ring.layout import __Ring__
from ..multi_ring.layout import *
from ..multi_ring.multi_ring_base import MultiRingIdenticalWithChangedInAndOutWithSpacings
from ipkiss.all import *
from ipkiss.plugins.photonics.wg.basic import WgDefProperty

__all__ = ["CoupledRingRectSymm","CoupledRingGeneric"]

class CoupledRingGeneric(Structure):
    """ CCW of horizontally stacked rings (composed of vertically stacked rings, but rotated -90 degrees """
    __name_prefix__ = "CCW"
    
    first_ring = RestrictedProperty(restriction = RestrictType(__Ring__), required = True)
    middle_ring = RestrictedProperty(restriction = RestrictType(__Ring__), required = True)
    last_ring = RestrictedProperty(restriction = RestrictType(__Ring__), required = True)
    spacings = RestrictedProperty(restriction = RestrictList(RESTRICT_NONNEGATIVE), required = True)
    
    
    @cache()
    def __get_MR__(self):
        if len(self.spacings) < 1:
            raise AttributeError("At least 2 resonators needed for a CCW")
        return MultiRingIdenticalWithChangedInAndOutWithSpacings(self.middle_ring, self.first_ring, self.last_ring, self.spacings, True)

    def define_elements(self, elems):
        elems += SRef(self.__get_MR__(), (0.0, 0.0), Rotation((0.0, 0.0), -90.0))
        return elems 
    
    def define_ports(self, P):
        P = self.__get_MR__().ports.rotate_copy((0.0, 0.0), -90.0)
        return P

class CoupledRingRectSymm(CoupledRingGeneric):
    wg_definition = WgDefProperty(default = TECH.WGDEF.WIRE)
    ring_wg_definition = WgDefProperty(default = TECH.WGDEF.WIRE)
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    straights = Size2Property(default = (TECH.WG.SHORT_STRAIGHT, TECH.WG.SHORT_STRAIGHT))
    
    first_ring = DefinitionProperty()
    last_ring = DefinitionProperty()
    middle_ring = DefinitionProperty()
    
    def __init__(self, spacings = [TECH.WG.SPACING], **kwargs):
        super(CoupledRingRectSymm,self).__init__(spacings = spacings[1:-1],**kwargs)     
        self._first_spacing = spacings[0]
        self._last_spacing = spacings[-1]

    def define_first_ring(self):
        return RingRectSymmNotchFilter(coupler_wg_definitions = [self.wg_definition], 
                                       coupler_spacings = [self._first_spacing], 
                                       bend_radius = self.bend_radius, 
                                       straights = self.straights, 
                                       ring_wg_definition = self.ring_wg_definition,
                                       )
    def define_last_ring(self):
        return RingRectSymmNotchFilter(coupler_wg_definitions = [self.wg_definition], 
                                       coupler_spacings = [self._last_spacing], 
                                       bend_radius = self.bend_radius, 
                                       straights = self.straights, 
                                       ring_wg_definition = self.ring_wg_definition,
                                       )
    def define_middle_ring(self):
        return RingRect(bend_radius = self.bend_radius, 
                        straights = self.straights, 
                        ring_wg_definition = self.ring_wg_definition,
                        )
    
#def CoupledRingRectSymm(spacings, 
                        #wg_definition = TECH.WGDEF.WIRE, 
                        #bend_radius= TECH.WG.BEND_RADIUS, 
                        #straights = (TECH.WG.SHORT_STRAIGHT, TECH.WG.SHORT_STRAIGHT), 
                        #ring_wg_definition = TECH.WGDEF.WIRE,
                        #**kwargs):
    #""" CCW of horizontally stacked identical rings, with adjustable spacings (composed of vertically stacked rings, but rotated -90 degrees) """
    #first = RingRectSymmNotchFilter(coupler_wg_definitions = [wg_definition], 
                                       #coupler_spacings = [spacings[0]], 
                                       #bend_radius = bend_radius, 
                                       #straights = straights, 
                                       #ring_wg_definition = ring_wg_definition,
                                       #**kwargs
                                       #)
    #last = RingRectSymmNotchFilter(coupler_wg_definitions = [wg_definition], 
                                      #coupler_spacings = [spacings[-1]], 
                                      #bend_radius = bend_radius, 
                                      #straights = straights, 
                                      #ring_wg_definition = ring_wg_definition,
                                      #**kwargs
                                       #)
    #middle = RingRect(   bend_radius = bend_radius, 
                         #straights = straights, 
                         #ring_wg_definition = ring_wg_definition,
                         #**kwargs
                         #)
    #return CoupledRingGeneric(first_ring = first, 
                              #middle_ring = middle, 
                              #last_ring = last, 
                              #spacings = spacings[1:-1],
                              #)

