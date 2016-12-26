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
#########################3
#TaperPorts component
from .taper_ports import TaperPorts
from ..wg.tapers.auto_taper.auto_taper import WgElPortTaperAuto
__all__ = ["AutoTaperPorts"]

class AutoTaperPorts(TaperPorts):
    """ Structure containing another structure which will apply the WgElPortTaperAuto"""
    __name_prefix__ = "AUTOTP"
    taper_length = PositiveNumberProperty(allow_none = True)
    straight_extension = RestrictedProperty(allow_none = True, restriction = RESTRICT_TUPLE2)
    def define_tapers(self):
        kwargs = {
                  "end_wg_def": self.end_wg_def
                  }
        if not self.taper_length is None:
            kwargs["length"] = self.taper_length
        if not self.straight_extension is None:
            kwargs["straight_extension"] = self.straight_extension
            
        
        return [WgElPortTaperAuto(start_port = P, **kwargs) 
                for P in self.__get_labeled_ports__()]        
    

