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
from ipcore.properties.restrictions import RestrictType
from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.processors import ProcessorTypeCast
from ...log import IPKISS_LOG as LOG
from ..layer import LayerList


class __LayerFilter__(Filter):
    layers = RestrictedProperty(default = LayerList(), restriction = RestrictType(LayerList), preprocess = ProcessorTypeCast(LayerList))
    

class LayerFilterAllow(__LayerFilter__):
    def __filter___LayerElement____(self, item):
        if item.layer in self.layers:
            return [item]
        else:
            LOG.debug("LayerFilterAllow is filtering out item %s" %item)
            return []
        
    def __repr__(self):
        return "<LayerFilterDelete>"   
    

class LayerFilterDelete(__LayerFilter__):
    def __filter___LayerElement____(self, item):
        if item.layer in self.layers:
            LOG.debug("LayerFilterDelete is filtering out item %s" %item)
            return []
        else:
            return [item]
        
    def __repr__(self):
        return "<LayerFilterDelete>"            
