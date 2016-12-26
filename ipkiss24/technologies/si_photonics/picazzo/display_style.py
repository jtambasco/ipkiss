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

from ipkiss.process import ProcessPurposeLayer
from ipkiss.visualisation.display_style import DisplayStyle

class __AutoDisplayStyleSet__(object):

    def get(self, key, default):
        try:
            return self.__get_item__(key)
        except:
            return default

class PurposeDisplayStyleSet(__AutoDisplayStyleSet__):
    def __init__(self, purpose_map):
        self.purpose_map = purpose_map
    def get_item(self, key):
        if isinstance(key, ProcessPurposeLayer):
            return self.purpose_map[key.purpose]

class ProcessPurposeDisplayStyleSet(__AutoDisplayStyleSet__):
    def __init__(self, process_map, purpose_map, process_kw = ["color"], purpose_kw = ["edge_color"]):
        self.process_map = process_map
        self.purpose_map = purpose_map
        self.process_kw = process_kw
        self.purpose_kw = purpose_kw
        
    def get_item(self, key):
        if isinstance(key, ProcessPurposeLayer):
            kwargs = {}
            for i in range(len(self.process_kw)):
                kwargs[self.process_kw[i]] = self.process_map[key.process]
            for i in range(len(self.purpose_kw)):
                kwargs[self.purpose_kw[i]] = self.purpose_map[key.purpose]
            return DisplayStyle(**kwargs)

    