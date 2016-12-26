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

from technologies.si_photonics.picazzo.default import * 

from ipkiss.plugins.vfabrication import *
from picazzo.filters.ring import RingRectSBend180DropFilter

ring = RingRectSBend180DropFilter(straights=(TECH.WG.SHORT_STRAIGHT,TECH.WG.SHORT_STRAIGHT+3.0),
                                      coupler_angles = [30.0, 10.0],
                                      coupler_spacings = [1.0, 0.8],
                                      coupler_lengths = [6.0, 2.0],
                                      coupler_radii = [3.0, 7.0]
                                      )

ring.visualize_2d()
ring.write_gdsii("ring.gds")


from picazzo.fibcoup.line_grating import FiberCouplerGratingLine
from ipkiss.plugins.photonics.wg.basic import WgElDefinition
from picazzo.fibcoup.socket import BroadWgSocket

wg_def = WgElDefinition(wg_width=5.0)
socket = BroadWgSocket(wg_definition = wg_def, wg_length = 15.0)
C = FiberCouplerGratingLine(line_widths_positions=[(1.0,1.0),(3.0,3.0),(4.0,7.0)],
                            line_length = 7.0,
                            socket=socket)
C.visualize_2d()
