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

from ..primitives.structure import Structure
from ..primitives.layer import LayerProperty
from ..geometry.coord import Size2Property

__all__ = []

class Logo(Structure):
    layer = LayerProperty(required = True)
    size = Size2Property(default = (50.0, 50.0))
    
    def __init__(self, layer, size= (50.0,50.0), **kwargs):
        super(Logo, self).__init__(
            layer = layer,
            size = size,
            **kwargs)

    __name_prefix__ = "logo_"

    def define_name(self):
        logo_size = (1.0, 1.1)
        scale = min([self.size[0]/logo_size[0],self.size[1]/logo_size[1]])
        return "%s_L%d_S%d" % (self.__name_prefix__ ,
                               self.layer.id(),
                               int(scale*1000)
                           )
