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
from .definition import BaseWaveguideDefinition, SingleShapeWaveguideElement, WaveguideDefProperty


__all__ = ["PathWindow",
           "WindowWaveguideDefinition",
           "WindowsOnWaveguideDefinition"
           ]

class __ShapeWindow__(StrongPropertyInitializer):
    """ Abstract: Defines a window to be extruded along a shape """

    shape_property_name = StringProperty(default = "shape", doc = "Name of the property of the __WindowDefinition__ object that is used to generate the window elements")
    
    @cache()
    def get_offsets(self):
        """ returns the list of offsets from the central shape, which can be used to control the termination. """
        return []
    
    def get_elements_from_shape(self, shape, **kwargs):
        """ Returns the elements based on a shape. Keyword arguments can be passed.
            Preferably use get_elements_from_window_definition"""
        return 
        
    def get_elements_from_path_definition(self, path_definition):
        shape = getattr(path_definition, self.shape_property_name)
        return self.get_elements_from_shape(shape = shape)

    
class __OffsetPathWindow__(__ShapeWindow__):
    start_offset = NumberProperty(required = True)
    end_offset = NumberProperty(required = True)

    def get_path_shape_with_termination_offsets(self, shape, termination_offsets):
        offsets = termination_offsets
        o1 = min(self.start_offset, self.end_offset)
        o2 = max(self.start_offset, self.end_offset)
                       
        C_start = Shape()
        C_end = Shape()
        
        red_shape = Shape(shape).remove_identicals() # FIXME: can we make this more efficient? We only need the first and last segment.
        s1 = Shape([red_shape[0], red_shape[1]], start_face_angle = shape.start_face_angle)
        s2 = Shape([red_shape[-2], red_shape[-1]], end_face_angle = shape.end_face_angle)
        for o in offsets:
            if o>o1 and o<o2:
                s = ShapeOffset(original_shape = s1, offset = o)
                C_start += s[0]
                s = ShapeOffset(original_shape = s2, offset = o)
                C_end += s[-1]

        C1 = ShapeOffset(original_shape = red_shape, offset = o1)
        C2 = ShapeOffset(original_shape = red_shape, offset = o2)                    
        b_shape = C1 + C_end + C2.reversed() + C_start.reversed()                                                                          
        return b_shape
    
    def transform(self, transformation):
        self.start_offset = transformation.apply_to_length(self.start_offset)
        self.end_offset = transformation.apply_to_length(self.end_offset)
    
class PathWindow(__OffsetPathWindow__):
    """ Defines a window to be extruded along a shape in the form of a path"""
    layer = LayerProperty(required = True)
    
    @cache()
    def get_offsets(self):
        """ returns the list of offsets from the central shape, which can be used to control the termination """
        return [self.start_offset, self.end_offset]
    

    def get_elements_from_shape(self, shape, termination_offsets = [], **kwargs):
        from ipkiss.primitives.elements import ElementList
        elems = ElementList()
        offsets = termination_offsets
        o1 = min(self.start_offset, self.end_offset)
        o2 = max(self.start_offset, self.end_offset)
                       
        C_start = Shape()
        C_end = Shape()
        
        # this avoids wrong overlaps at non-manhattan interfaces
        shapes = []
        if not shape.closed:
            shapes = [self.get_path_shape_with_termination_offsets(shape = shape, termination_offsets = termination_offsets)]
        else:
            #we do not want closed Boundaries as resulting elements, as this gives troubles in other parts of the framework, i.e. with Shapely
            #FIXME : better alternative? 
            #Wim: This should not be handled here! This should be processed at the interface with Shapely.
            from ipkiss.primitives.filters.path_cut_filter import ShapeCutFilter
            import sys
            f = ShapeCutFilter(max_path_length = sys.maxint)
            shapes_to_offset = f(shape)
            shapes = [self.get_path_shape_with_termination_offsets(shape = sh, termination_offsets = []) for sh in shapes_to_offset]
        
        for sh in shapes:
            elems += Boundary(self.layer, sh)
        return elems
        
    def get_elements_from_path_definition(self, path_definition):
        shape = getattr(path_definition, self.shape_property_name)
        return self.get_elements_from_shape(shape = shape, 
                                            termination_offsets = path_definition.definition().get_offset_list())


    
class __WindowDefinition__(StrongPropertyInitializer):
    windows = RestrictedProperty(default = [], restriction = RestrictTypeList(__ShapeWindow__))
    
    @cache()
    def get_offset_list(self):
        offsets = set()
        for w in self.windows:
            for o in w.get_offsets():
                offsets.add(o)
            
        offsets = list(offsets)
        offsets.sort()
        return offsets
    
    def transform(self, transformation):
        # FIXME: should only be done in manually set windows?
        self.windows = [w.transform_copy(transformation) for w in self.windows]
        super(__WindowDefinition__, self).transform(transformable)
        
class __CompatibilityWithAdapters__(StrongPropertyInitializer):    
    # These properties serve only as a compatibility layer with adapters, so the ports
    # can return a value for wg_width and process
    
    wg_width = PositiveNumberProperty(required = True)  # have no function except for the ports
    process = ProcessProperty(required = True)  # have no function except for the ports
    trench_width = NonNegativeNumberProperty(required = True)  # have no function except for the ports 


class WindowWaveguideDefinition(__WindowDefinition__, __CompatibilityWithAdapters__, BaseWaveguideDefinition):

    class __WindowWaveguideDefinitionPathDefinition__(SingleShapeWaveguideElement):
        
        def __get_wg_elements_from_windows_and_shape__(self, windows, shape):
            #### Deprecated, does not work with some new Window types
            return [w.get_elements_from_shape(shape) for w in windows]

        @cache()
        def __get_wg_elements_from_windows__(self):
            windows = self.definition().windows
            return [w.get_elements_from_path_definition(path_definition = self) for w in windows]
        
        
        def define_elements(self, elems):
            elems += self.__get_wg_elements_from_windows__()
            return elems
        

__WindowWaveguideDefinitionPathDefinition__ = WindowWaveguideDefinition.__WindowWaveguideDefinitionPathDefinition__
   
# adds windows to an exsiting waveguide definition
class WindowsOnWaveguideDefinition(__WindowDefinition__, BaseWaveguideDefinition):
    wg_definition = WaveguideDefProperty(required = True)   
    wg_width = ReadOnlyIndirectProperty("wg_definition")
    process = ReadOnlyIndirectProperty("wg_definition")
    trench_width = ReadOnlyIndirectProperty("wg_definition")
    
    class __WindowsOnWaveguideDefinitionPathDefinition__(WindowWaveguideDefinition.__WindowWaveguideDefinitionPathDefinition__):
        def define_elements(self, elems):
            elems += self.wg_definition.wg_definition(shape = self.shape)
            return super(__WindowsOnWaveguideDefinitionPathDefinition__, self).define_elements(elems)    
    
    def definition(self):
        return self.wg_definiton.definition()
    
__WindowsOnWaveguideDefinitionPathDefinition__ = WindowsOnWaveguideDefinition.__WindowsOnWaveguideDefinitionPathDefinition__


