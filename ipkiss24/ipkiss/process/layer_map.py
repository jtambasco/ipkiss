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

from ipkiss.io.gds_layer import GdsiiLayerInputMap
from ipkiss.process.layer import ProcessProperty
from ipkiss.io.gds_layer import GdsiiLayer
from .layer import ProcessPurposeLayer, PPLayer
from ipcore.properties.initializer import StrongPropertyInitializer
from ipcore.properties.predefined import DictProperty, ListProperty, BoolProperty
from ipcore.caching.cache import cache
from ipkiss.technology import get_technology
from ipkiss.technology.technology import TechnologyTree
from ipkiss.log import IPKISS_LOG as LOG
        
TECH = get_technology()

###########################################################################
##  OUTPUT MAPS                                                          ##
###########################################################################
  
class UnconstrainedGdsiiPPLayerOutputMap(StrongPropertyInitializer):
    process_layer_map = DictProperty(required = True)
    purpose_datatype_map = DictProperty(required = True) 
    layer_map = DictProperty(default = {}, doc = "Additional layer map, to be used complementarily to the 'process_layer_map' and 'purpose_datatype_map'.")
    
    def __getitem__(self, key, default = None):
        if isinstance(key, ProcessPurposeLayer):
            ln = self.process_layer_map.get(key.process, None)
            dt = self.purpose_datatype_map.get(key.purpose, None)
            if ln is None or dt is None: 
                for pplayer, gdsiilayer in self.layer_map.items():
                    if (key.process == pplayer.process) and (key.purpose == pplayer.purpose):
                        return gdsiilayer
                self.__warn__(key)
                return default
            else:
                return GdsiiLayer(ln, dt)
        else:
            raise Exception("Key should be of type ProcessPurposeLayer, but is of type %s." %type(key))
        
    def get(self, key, default):
        return self.__getitem__(key, default)
    
    def __warn__(self, key):
        LOG.error("Warning during export : no corresponding GDSII layer found for process %s and purpose %s" %(key.process, key.purpose))




class GdsiiPPLayerOutputMap(StrongPropertyInitializer):
    process_layer_map = DictProperty(required=True, doc="Mapping from process to GDS2 layer number")
    purpose_datatype_map = DictProperty(required=True, doc="Mapping from purpose to GDS2 datatype number")
    purpose_layer_map = DictProperty(default={}, doc="PPLayers with these purposes will be mapped to the give GDS2 layer number and TECH.GDSII.DEFAULT_DATATYPE ('purpose_datatype_map' will be ignored)")  
    layer_map = DictProperty(doc="The mapping from a PPLayer to a GdsiiLayer")
    ignore_pplayer = ListProperty(default=[], doc="These PPLayer's will not mapped to a Gdsii layer")
    process_ignore_purpose = ListProperty(default=[], doc="For these processes, the TECH.GDSII.DEFAULT_DATATYPE will always be used as datatype")
    purpose_noignore = ListProperty(default=[], doc="Purposes that cannot be ignored by process_ignore_purpose")
    
    def define_layer_map(self):
        lm = dict()
        #iterate over all pplayers in TECH.PPLAYER
        for pplayer_node_str in TECH.PPLAYER.keys():
            pplayer_node = getattr(TECH.PPLAYER, pplayer_node_str)
            if isinstance(pplayer_node, TechnologyTree):
                for pplayer_str in pplayer_node.keys():
                    pplayer = getattr(pplayer_node, pplayer_str)
                    if isinstance(pplayer, ProcessPurposeLayer):
                        if pplayer.purpose in self.purpose_layer_map:
                            lm[pplayer] = GdsiiLayer(number=self.purpose_layer_map[pplayer.purpose], 
                                                                       datatype=TECH.GDSII.DEFAULT_DATATYPE)
                        else:
                            if pplayer.process in self.process_ignore_purpose and (not pplayer.purpose in self.purpose_noignore):
                                dt = TECH.GDSII.DEFAULT_DATATYPE
                            else:
                                dt = self.purpose_datatype_map[pplayer.purpose]
                            lm[pplayer] = GdsiiLayer(number=self.process_layer_map[pplayer.process], 
                                                                       datatype=dt)
        return lm
    
    
    def __getitem__(self, key, default = None):
        if isinstance(key, ProcessPurposeLayer):
            if not key in self.ignore_pplayer:
                for pplayer, gdsiilayer in self.layer_map.items():
                    if (pplayer == key):
                        return gdsiilayer                
                self.__warn__(key)
                return default
            else:
                return default
        else:
            raise Exception("They key for GdsiiPPLayerOutputMap should be of type PPLayer (ProcessPurposeLayer), but received something of type %s." %type(key)) 
    
    def get(self, key, default):
        return self.__getitem__(key, default)
    
    def __warn__(self, key):
        LOG.error("Warning during export : no corresponding GDSII layer found for process %s and purpose %s" %(key.process, key.purpose))


class GenericGdsiiPPLayerOutputMap(StrongPropertyInitializer):
    pplayer_map = DictProperty(doc="map of (process, purpose) to (layer,datatype)")
    ignore_undefined_mappings = BoolProperty(default = False)
    
    def __getitem__(self, key, default = None):
        if (key.process,key.purpose) in self.pplayer_map:
            (lay,dat) = self.pplayer_map[(key.process,key.purpose)]
            return GdsiiLayer(number=lay, datatype=dat)
        else:
            error_message = "Warning during GDSII export : no corresponding GDSII layer/datatype found for process = %s and purpose = %s" %(key.process, key.purpose)
            if self.ignore_undefined_mappings:
                LOG.warning(error_message)
                return default
            else:
                raise Exception(error_message)
            
    def get(self, key, default):
        return self.__getitem__(key, default)       
                   
###########################################################################
##  INPUT MAPS                                                           ##
###########################################################################
    
class GenericGdsiiPPLayerInputMap(GenericGdsiiPPLayerOutputMap):
    gdsiilayer_map = DictProperty(doc="map of (layer,datatype) to PPLayer")
    
    def define_gdsiilayer_map(self):
        lm = {}
        for k, v in self.pplayer_map.items():
            if v in lm:
                LOG.warning("PPLayer to GDSII layer mapping for GDSII %i:%i => %s:%s overwritten with %s:%s"
                            %(v[0],v[1],lm[v][0],lm[v][1],k[0],k[1]))
            lm[v] = k
        return lm

    def __getitem__(self, key, default = None):
        if (key.number,key.datatype) in self.gdsiilayer_map:
            (pl,pp) = self.gdsiilayer_map[(key.number,key.datatype)]
            return PPLayer(process=pl, purpose = pp)
        else:
            error_message = "Warning during GDSII import : no corresponding process/purpose layer found for number = %i and datatype = %s" %(key.number, key.datatype)
            if self.ignore_undefined_mappings:
                LOG.warning(error_message)
                return default
            else:
                raise Exception(error_message)
            
            

       
class UnconstrainedGdsiiPPLayerInputMap(StrongPropertyInitializer):
    process_layer_map = DictProperty(required = True)
    purpose_datatype_map = DictProperty(required = True)     
    layer_process_map = DictProperty()
    datatype_purpose_map = DictProperty()        
    layer_map = DictProperty(default = {}, doc = "Additional layer map, to be used complementarily to the 'process_layer_map' and 'purpose_datatype_map'.")
    
    def define_layer_process_map(self):
        lpm = {}
        for k, v in self.process_layer_map.items():
            lpm[v] = k
        return lpm
    
    def define_datatype_purpose_map(self):
        dpm = {}
        for k, v in self.purpose_datatype_map.items():
            dpm[v] = k        
        return dpm
        
    def __getitem__(self, key, default = None):
        if isinstance(key, GdsiiLayer):
            pr = self.layer_process_map.get(key.number, None)
            pu = self.datatype_purpose_map.get(key.datatype, None)
            if pr is None or pu is None: 
                for gdsiilayer,pplayer  in self.layer_map.items():
                    if (key.number == gdsiilayer.number) and (key.datatype == gdsiilayer.datatype):
                        return pplayer                
                self.__warn__(key)                
                return default
            else:
                return ProcessPurposeLayer(process = pr, purpose = pu)
        else:
            raise Exception("Key should be of type ProcessPurposeLayer, but is of type %s." %type(key))
        
    def get(self, key, default):
        return self.__getitem__(key, default)        

    def __warn__(self, key):
        from ipkiss.log import IPKISS_LOG as LOG
        LOG.error("Warning during GDSII import : no corresponding process/purpose layer found for number = %i and datatype = %s" %(key.number, key.datatype))
        
        

GdsiiPurposeInputMap = UnconstrainedGdsiiPPLayerInputMap #DEPRECATED - for backwards compatibility


class QuietUnconstrainedGdsiiPPLayerInputMap(UnconstrainedGdsiiPPLayerInputMap): 

    def __warn__(self, key):
        #show no warning when no match for mapping is found 
        pass
    
QuietGdsiiPurposeInputMap = QuietUnconstrainedGdsiiPPLayerInputMap #DEPRECATED - for backwards compatibility   
    
    
class GdsiiPPLayerInputMap(GdsiiPPLayerOutputMap):
    ignore_undefined_mappings = BoolProperty(default = False)
    
    def define_layer_map(self):
        layer_map = super(GdsiiPPLayerInputMap, self).define_layer_map()
        reverse_layer_map = dict()
        for pplayer, gdsiilayer in layer_map.items():
            reverse_layer_map[(gdsiilayer.number,gdsiilayer.datatype)] = pplayer
        return reverse_layer_map
                
    def __getitem__(self, gdsiilayer, default = None):
        if (gdsiilayer.number,gdsiilayer.datatype) in self.layer_map:
            return self.layer_map[(gdsiilayer.number,gdsiilayer.datatype)]
        else:
            error_message = "Warning during GDSII import : no corresponding process/purpose layer found for number = %i and datatype = %s" %(gdsiilayer.number, gdsiilayer.datatype)
            if self.ignore_undefined_mappings:
                LOG.warning(error_message)
                return default
            else:
                raise Exception(error_message)
            
            

        
    
    
    



    

