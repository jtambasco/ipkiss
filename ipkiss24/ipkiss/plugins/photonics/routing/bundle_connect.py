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
from ipkiss.plugins.photonics.wg.bundle import WgElBundleConnectRoundedGeneric


__all__ = ["RouteBundleConnectRounded"]

class RouteBundleConnectRounded(WgElBundleConnectRoundedGeneric):
    """ bundle of rounded waveguide routes, with a common inversion layer. the shapes should be in the east order for the inversion layer to work """
    wg_widths = DefinitionProperty(fdef_name = "define_wg_widths")
    trench_widths = DefinitionProperty(fdef_name = "define_trench_widths")
    bend_radii = DefinitionProperty(fdef_name = "define_bend_radii")
    shapes = RestrictedProperty(restriction = RestrictTypeList(Shape), required = True)
            
    def define_wg_widths(self):
        wg_widths = []
        for route in self.shapes:
            if hasattr(route, "input_port"):
                wg_widths.append(route.input_port.wg_width)
            else:
                wg_widths.append(TECH.WG.WIRE_WIDTH)
        return wg_widths
                
    def define_trench_widths(self):
        trench_widths = []
        for route in self.shapes:
            if hasattr(route, "input_port"):
                trench_widths.append(route.input_port.trench_width)
            else:
                trench_widths.append(TECH.WG.TRENCH_WIDTH)
        return trench_widths
                
    def define_bend_radii(self):
        bend_radii = []
        for route in self.shapes:
            if hasattr(route, "bend_radius"):
                bend_radii.append(route.bend_radius)
            else:
                bend_radii.append(TECH.WG.BEND_RADIUS)
        return bend_radii
 
