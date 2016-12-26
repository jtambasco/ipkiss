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

from ..filter import Filter
from ipkiss.log import IPKISS_LOG as LOG
from ...technology import get_technology
from ipcore.all import BoolProperty, PositiveIntProperty
import copy

TECH = get_technology()

class NameScrambleFilter(Filter):
    """ Filter for scrambling a Structure's name.
    """
    scramble_all = BoolProperty(default=False)
    max_name_length = PositiveIntProperty(allow_none=True, default=TECH.GDSII.MAX_NAME_LENGTH)
    
    def __filter_str__(self, item):    
        if item is None:
            return None
        name = copy.copy(item)
        name = name.replace("-","_")
        name = name.replace(" ","_")
        name = name.replace(".","_")
        name = name.replace("/","_")
        if self.scramble_all:
            hashval = hash(name)
            if hashval < 0:
                prefix = "S_"
            else:
                prefix = "S"
            name = prefix + str(abs(hashval))
            name = name.upper()
        elif self.max_name_length != None:
            if  self.max_name_length > 0 and len(name) > self.max_name_length:
                hashval = str(abs(hash(name)))
                L = len(hashval)
                if L > self.max_name_length + 1:
                    raise ValueError("max_name_length %d in NameScrambleFilter is too short for hash algorithm"%(self.max_name_length))
                name = name[0:self.max_name_length - L - 1] + "_" + hashval
                LOG.warning("Too long name encountered. Current length = %d" % len(name))
        return [name]
        
    def __repr__(self):
        return "<NameScrambleFilter>"      