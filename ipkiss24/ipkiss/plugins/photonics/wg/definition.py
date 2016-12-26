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

__all__ = []

#############################################################
# base class for waveguide definition
#############################################################
class BaseWaveguideDefinition(StrongPropertyInitializer, Transformable):
    """base class for waveguide definitions"""
    path_definition_class = FunctionNameProperty(fget_name = "get_path_definition_class")
    name = StringProperty()
    
    def get_path_definition_class(self):
        class_name = self.__class__.__name__
        path_definition_class_name = "__" + class_name + "PathDefinition__"
        try:
            return getattr(self.__class__, path_definition_class_name)
        except AttributeError:
            import inspect
            for C in inspect.getmro(type(self)):
                path_definition_class_name = "__" + C.__name__ + "PathDefinition__"
                if hasattr(self.__class__, path_definition_class_name):            
                    return getattr(self.__class__, path_definition_class_name)
            raise Exception("Type "+self.__class__+" has no inner class "+"__" + class_name + "PathDefinition__ for the path definition")

    def __call__(self, *args, **kwargs):
        kwargs['wg_definition'] = self
        return self.path_definition_class(*args, **kwargs)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def get_bend90_size(self):
        return 0,0
    
    def get_bend_size(self, angle):
        return 0,0
    
    def get_wg_definition_cross_section(self):
        return self
    
    def define_name(self):
        return ""

class WaveguideDefCrossSectionProperty(DefinitionProperty):
    
    def __init__(self, internal_member_name = None, **kwargs):
        kwargs["restriction"] = RestrictType(allowed_types=[BaseWaveguideDefinition])
        super(WaveguideDefCrossSectionProperty,self).__init__(internal_member_name = internal_member_name, **kwargs)                           
    
    def __set__(self, obj, value):
        wg_def_cross_section = value.get_wg_definition_cross_section()
        self.__externally_set_property_value_on_object__(obj, wg_def_cross_section)
        return        
    

def WaveguideDefProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RestrictType(BaseWaveguideDefinition) & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)

def WaveguideDefListProperty(internal_member_name=None, restriction=None, **kwargs):
    R = RestrictTypeList(BaseWaveguideDefinition) & restriction
    return RestrictedProperty(internal_member_name, restriction=R, **kwargs)
    

#############################################################
# base class for waveguide elements
#############################################################

class __BaseWaveguideElement__(Group):
    """ base class for a definition which produces waveguide elements """
    wg_definition = WaveguideDefProperty(required = True)

class SingleShapeWaveguideElement(__BaseWaveguideElement__):
    """ generic waveguide element based on a single shape """
    
    shape = ShapeProperty(required = True)
    
    def __init__(self,  shape, wg_definition, **kwargs):
        super(SingleShapeWaveguideElement, self).__init__(shape=shape, wg_definition=wg_definition, **kwargs)
        
    def definition(self):
        return self.wg_definition
    
    def length(self):
        return self.shape.length()
    
    def center_line(self):
        return self.shape
    
    @cache()
    def __get_shape_list__(self):
        if self.shape.closed:
            return cut_open_shape_in_n_sections_with_overlap(shape = self.shape,
                                                             n_o_sections = 2,
                                                             overlap = 0)
        else:
            return [self.shape]
    
    
    def define_ports(self, ports):
        from ipkiss.plugins.photonics.port.port import InOpticalPort, OutOpticalPort
        if len(self.shape) == 0:
            self.ports = []
            return
        ports += [InOpticalPort (position = self.shape[0], angle = angle_deg(self.shape[0],  self.shape[1]), wg_definition = self.definition()), 
                      OutOpticalPort(position = self.shape[-1], angle = angle_deg(self.shape[-1], self.shape[-2]), wg_definition = self.definition())]
        return ports
        
        

class TwoShapeWaveguideElement(SingleShapeWaveguideElement):
    """ generic waveguide element based on two shapes """

    # shape is the only parameter that is waveguide dependent
    trench_shape = ShapeProperty(fdef_name='define_trench_shape')
    
    def __init__(self, shape, trench_shape = None, **kwargs):
        super(TwoShapeWaveguideElement, self).__init__(shape = shape, trench_shape = trench_shape, **kwargs)
        
    def define_trench_shape(self):
        return self.shape

    @cache()
    def __get_trench_shape_list__(self):
        if self.trench_shape.is_empty(): 
            T_shape = self.shape
        else: 
            T_shape = self.trench_shape

        if T_shape.closed:
            return cut_open_shape_in_n_sections_with_overlap(shape = T_shape,
                                                             n_o_sections = 2,
                                                             overlap = 0)
        else:
            return [T_shape]        

    