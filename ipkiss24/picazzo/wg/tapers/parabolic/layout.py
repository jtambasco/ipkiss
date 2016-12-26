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

# TODO: introduce parametric shape tapers, and subclass this one.
from ipkiss.all import *
from ..basic import __WgElTaper__    

__all__ = ["WgElTaperParabolic"]

class WgElTaperParabolic(__WgElTaper__):
    """ This class generates a parabolic taper between wavguide definitions to make tapers for more complex waveguide structures.
    The waveguide definitions should be of the same type. Only gives meaningful result for symmetric windows """
    
    def __get_taper_shape__(self, start_position, end_position, start_window, end_window, se):
        sp = start_position
        ep = end_position        
        dist = distance(ep, sp)
        cosangle = (ep[0] - sp[0])/dist
        sinangle = (ep[1] - sp[1])/dist

        sw = abs(start_window.start_offset-start_window.end_offset)
        ew = abs(end_window.start_offset-end_window.end_offset)
        avg_offset_start = 0.5*(start_window.start_offset+start_window.end_offset)
        avg_offset_end = 0.5*(end_window.start_offset+end_window.end_offset)
        
        sp = (start_position[0]+(sinangle*(avg_offset_start)), start_position[1]+(cosangle*(avg_offset_start)))
        ep = (end_position[0]+(sinangle*(avg_offset_end)), end_position[1]+(cosangle*(avg_offset_end)))
        
        sp1 = ShapeParabolic(begin_coord = sp, end_coord = ep, begin_width = sw, end_width = ew)

        if sw >= ew:
            sp1b = sp1[:len(sp1)/2]
            sp1a = sp1[len(sp1)/2:]
        else:
            sp1a = sp1[:len(sp1)/2]
            sp1b = sp1[len(sp1)/2:]
            
        s1 =Shape([], True)
        if se[0]:
            s1 += [(sp[0] + sinangle * sw/2.0 - cosangle * (se[0] + TECH.WG.OVERLAP_TRENCH),
                    sp[1] - cosangle * sw/2.0 - sinangle * (se[0] + TECH.WG.OVERLAP_TRENCH)),
                   (sp[0] - sinangle * sw/2.0 - cosangle * (se[0] + TECH.WG.OVERLAP_TRENCH),
                    sp[1] + cosangle * sw/2.0 - sinangle * (se[0] + TECH.WG.OVERLAP_TRENCH))]
            
        s1 += sp1a
        if se[1]:
            s1 += [(ep[0] - sinangle * ew/2.0 + cosangle * (se[1] + TECH.WG.OVERLAP_TRENCH),
                    ep[1] + cosangle * ew/2.0 + sinangle * (se[1] + TECH.WG.OVERLAP_TRENCH)),
                   (ep[0] + sinangle * ew/2.0 + cosangle * (se[1] + TECH.WG.OVERLAP_TRENCH),
                    ep[1] - cosangle * ew/2.0 + sinangle * (se[1] + TECH.WG.OVERLAP_TRENCH))]
            
        s1 += sp1b
        return s1
