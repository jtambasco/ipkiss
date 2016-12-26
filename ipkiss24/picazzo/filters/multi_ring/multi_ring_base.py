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
# generic classes for multiple rings
########################################################################

from ipkiss.plugins.photonics.port.port_list import OpticalPortList
from ipkiss.all import *
from ipkiss.geometry.transform import GenericNoDistortTransform
from picazzo.filters.ring.layout import __Ring__
import numpy

__all__ = ["MultiRing",
           "MultiRingIdentical",
           "MultiRingIdenticalWithChangedInAndOut",
           "MultiRingIdenticalWithChangedInAndOutWithSpacing",
           "MultiRingIdenticalWithChangedInAndOutWithSpacings",
           "MultiRingIdenticalWithSpacing",
           "MultiRingIdenticalWithSpacings",
           "MultiRingPeriodic",
           "MultiRingWithGaps"]

####################################################################
# stacked rings (in series)
####################################################################

class MultiRing(Structure):
    """ geneneric multiple rings placed with multiple ring_transformations """
    __name_prefix__ = "MULTIRING"
    rings = RestrictedProperty(restriction = RestrictTypeList(__Ring__), required = True)
    ring_transformations = RestrictedProperty(restriction = RestrictTypeList(NoDistortTransform), required = True)

   
    def define_elements(self, elems):
        if len(self.rings) != len(self.ring_transformations):
            raise IpcoreAttributeException("length of ring list is different from length of ring_transformations list")
        for (R, T) in zip(self.rings, self.ring_transformations):
            elems += SRef(R, (0.0, 0.0), T)
        return elems
    
    def define_ports(self, ports):
        for (R, T) in zip(self.rings, self.ring_transformations):
            ports += R.ports.transform_copy(T)
        return ports

    
class MultiRingIdentical(MultiRing):
    """ geneneric multiple identical rings placed with multiple ring_transformations """
    rings = DefinitionProperty(fdef_name="define_rings")
    ring = RestrictedProperty(restriction = RestrictType(__Ring__), required = True)
        
    
    def define_rings(self):
        return [self.ring for T in self.ring_transformations]

        
class MultiRingPeriodic(MultiRingIdentical):
    """ ring periodically placed """
    ring_transformations = DefinitionProperty(fdef_name="define_ring_transformations")
    origin = Coord2Property(default = (0.0, 0.0))
    period = Coord2Property(required = True)
    n_o_rings = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    
    
    def define_ring_transformations(self):
        return [Translation((self.origin[0]+i * self.period[0], self.origin[1] + i * self.period[1]))for i in range(self.n_o_rings)]


        
def MultiRingIdenticalWithChangedInAndOut(ring_middle, ring_in, ring_out, ring_transformations, **kwargs):
    """ identical ring placed with multiple ring_transformations, but with different in and out ring """
    # TODO: Replace with subclass once definitionproperties are implicit
    rings = [ring_in] + [ring_middle for i in range(len(ring_transformations)-2)] + [ring_out]
    return MultiRing(rings = rings,
                     ring_transformations = ring_transformations,
                     **kwargs
                     )

def MultiRingWithSpacings(rings, spacings, flip_last = False, **kwargs):
    """ multiple rings with different spacings between the rings """
    # TODO: Replace with subclass once definitionproperties are implicit
    ring_transformations = [IdentityTransform()]
    bs=[numpy.mean(r.get_bend90_size()) for r in rings]
    ss=[r.straights for r in rings]
    for i in range(len(spacings)-1):
        ring_transformations += [ring_transformations[-1] + Translation((0.0, 0.5*ss[i][1] + 0.5*ss[i+1][1] + bs[1] + bs[i+1] + spacings[i]))
                       ]
    if len(rings)> 1:
        if flip_last:
            ring_transformations.append(CMirror() + 
                                   ring_transformations[-1] + 
                                   Translation((0.0, 0.5*ss[-1][1] + 0.5*ss[-2][1] + bs[-1] + bs[-2] + spacings[-1])))
        else:
            ring_transformations.append(ring_transformations[-1] + Translation((0.0, 0.5*ss[-1][1] + 0.5*ss[-2][1] + bs[-1] + bs[-2] + spacings[-1])))
    return MultiRing(rings = rings, 
                     ring_transformations = ring_transformations,
                     **kwargs
                     )


#def MultiRingIdenticalWithSpacings(ring, 
                               #spacings):
    #""" multiple identical rings with different spacings between the rings """
    ##ring.*alc_info() - REMOVED IN REFACTORING
    #ring_transformations = [IdentityTransform()]
    #for s in spacings:
        #ring_transformations.append(ring_transformations[-1] + Translation((0.0, ring.straights[1] + 2* numpy.mean(ring.get_bend90_size()) + s)))
    #return MultiRingIdentical(ring = ring, 
                              #ring_transformations = ring_transformations
                              #)
class MultiRingIdenticalWithSpacings(MultiRingIdentical):
    spacings = ListDefinitionProperty(allowed_types = [int,float], restriction = RESTRICT_POSITIVE)
    ring_transformations = DefinitionProperty(fdef_name="define_ring_transformations")
    def define_ring_transformations(self):
        ring_transformations = [IdentityTransform()]
        for s in self.spacings:
            ring_transformations.append(ring_transformations[-1] + Translation((0.0, self.ring.straights[1] + 2* numpy.mean(self.ring.get_bend90_size()) + s)))
        return ring_transformations
        
class MultiRingIdenticalWithSpacing(MultiRingIdenticalWithSpacings):
    spacing = PositiveNumberProperty()
    n_o_rings = PositiveIntProperty()
    def define_spacings(self):
        return [spacing for i in range(self.n_o_rings)]
                                       
#def MultiRingIdenticalWithSpacing(ring, 
                              #spacing, 
                              #n_o_rings):
    #""" multiple identical rings with different spacings between the rings """
    #spacings = [spacing for i in range(n_o_rings-1)]
    #return MultiRingIdenticalWithSpacings(ring = ring, 
                                      #spacings = spacings
                                      #)

def MultiRingIdenticalWithChangedInAndOutWithSpacings(ring_middle, 
                                                  ring_in, 
                                                  ring_out, 
                                                  spacings, 
                                                  flip_last = False):
    rings = [ring_in] + [ring_middle for i in range(len(spacings)-1)] + [ring_out]    
    return MultiRingWithSpacings(rings = rings, 
                             spacings = spacings, 
                             flip_last = flip_last
                             )

def MultiRingIdenticalWithChangedInAndOutWithSpacing(ring_middle, 
                                                 ring_in, 
                                                 ring_out, 
                                                 spacing, 
                                                 n_o_rings, 
                                                 flip_last = False):
    spacings = [spacing for i in range(n_o_rings-1)]
    return MultiRingIdenticalWithChangedInAndOutWithSpacings(ring_middle = ring_middle, 
                                                         ring_in = ring_in, 
                                                         ring_outp = ring_out, 
                                                         spacings = spacings, 
                                                         flip_last = flip_last
                                                         )


