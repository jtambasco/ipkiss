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

from ipkiss.all import Vector, RAD2DEG, DEG2RAD
from math import atan2, cos, sin

__all__ = ["aperture_mounting_circular",
           "aperture_mounting_circular_spacing",
           "aperture_mounting_rowland",
           "aperture_angles"]

def aperture_mounting_circular(center, radius, angles):
    """ Generates a tuple of (positions, angles), with positions and angles lists, for 
    apertures on a same circle, pointing to the center of the circle, with given angles from the center"""
    vectors = [Vector(position = (center[0] + radius * cos(DEG2RAD * a), center[1] + radius * sin(DEG2RAD*a)), angle = a) for a in angles]
    return vectors

def aperture_angles(radius, center_angle, pitch, n_o_apertures):
    angle_step = RAD2DEG * atan2(pitch, radius)
    angles = [center_angle + (i-0.5*(n_o_apertures-1)) * angle_step for i in range(n_o_apertures)]
    return angles
    
def aperture_mounting_circular_spacing(center, radius, center_angle, pitch, n_o_apertures):
    """ Generates a tuple of (positions, angles), with positions and angles lists, for 
    apertures on a circle, pointing to the center of the circle, with a given spacing """    
    angles = aperture_angles(radius, center_angle, pitch, n_o_apertures)
    return aperture_mounting_circular(center, radius, angles)

def aperture_mounting_rowland(pole_vector, radius, angles):
    """ Generates a tuple of (positions, angles), with positions and angles lists, for 
    apertures ojn a Rowland circle wit a given pole and direction of the pole (a vector), 
    and the apertures pointing to the pole and for given angles with respect to the pole """
    vectors = [Vector(position = (pole_vector[0] + 2*radius * cos(DEG2RAD* (a-pole_vector.angle_deg)) * cos(DEG2RAD * a) , 
                           pole_vector[1] + 2*radius * cos(DEG2RAD* (a-pole_vector.angle_deg)) * sin(DEG2RAD*a)),
                       angle = a) 
                        for a in angles]
    return vectors
    

