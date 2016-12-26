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

from ipkiss.aspects.aspect import __Aspect__
from ipkiss.primitives.elements.basic import ElementList, ElementListProperty
from ipkiss.all import Layer, Boundary, Path, Structure, get_technology
from ipkiss.primitives.layer import __GeneratedLayerAnd__, __GeneratedLayerNot__, __GeneratedLayerOr__, __GeneratedLayerXor__, __GeneratedLayer_2Layer__, __GeneratedLayer__
from ipkiss.boolean_ops.boolean_ops_elements import *
from dependencies.shapely_wrapper import shapely_geom_to_shape, flatten_shapely_geom, Polygon, cascaded_union, MultiPolygon
from ipkiss.process import PPLayer
from ipkiss.primitives.filters.path_cut_filter import PathCutFilter
from ipkiss.primitives.filters.path_to_boundary_filter import PathToBoundaryFilter
from ipkiss.primitives.filters.boundary_cut_filter import BoundaryCutFilter
#from ipkiss.constants import GDSII_MAX_COORDINATES 
from ipkiss.primitives.elements.basic import __LayerElement__



TECH = get_technology()


def __get_composite_shapely_polygon_for_elements_on_generated_layer__(elements, generated_layer):
    """
    Recursive algorithm : 
    -give a Generated Layer, apply the corresponding Shapely boolean operations, then recursively call the function.
    -lowest level : given a Layer, create a Shapely Multipolygon spanning all the elements.
    """    
    if isinstance(generated_layer, Layer):
        #lowest level of the recursion
        boundaries = []
        elements_flattened = elements.flat_copy()	    
        fp = PathCutFilter(max_path_length = TECH.GDSII.MAX_PATH_LENGTH, grids_per_unit=int(1.0 / TECH.METRICS.GRID), overlap=1)            
        fp += PathToBoundaryFilter()	    
        fb = BoundaryCutFilter()
        for elem in elements_flattened:
            if (isinstance(elem, Path)) and (elem.layer == generated_layer):        
                for e in fp(elem):
                    if isinstance(e, __LayerElement__):
                        boundaries.append(e)
            elif (isinstance(elem, Boundary)) and (elem.layer == generated_layer):		
                boundaries.extend(fb(elem.flat_copy()))
        shapely_polygons = []
        for b in boundaries:
            if b.transformation is not None:
                tr_sh = b.shape.transform_copy(b.transformation)
                tr_sh.snap_to_grid() #otherwise Shapely numerical errors occur 
                p = Polygon(tr_sh.points)
            else:
                sh = Shape(b.shape.points)
                sh.snap_to_grid()
                p = Polygon(sh.points)
            if p.is_valid:
                shapely_polygons.append(p)
            else:
                raise Exception("Boundary could not be converted to a valid Shapely polygon.")	
        if len(shapely_polygons) > 0:
            shapely_polygon = cascaded_union(MultiPolygon(shapely_polygons))
        else:
            shapely_polygon = Polygon()			
        return shapely_polygon   
    elif isinstance(generated_layer, __GeneratedLayer_2Layer__):
        p1 = __get_composite_shapely_polygon_for_elements_on_generated_layer__(elements, generated_layer.layer1)
        p2 = __get_composite_shapely_polygon_for_elements_on_generated_layer__(elements, generated_layer.layer2)
        if isinstance(generated_layer, __GeneratedLayerAnd__):
            result_p = p1.intersection(p2)
        elif isinstance(generated_layer, __GeneratedLayerOr__):
            result_p = p1.union(p2)
        elif isinstance(generated_layer, __GeneratedLayerXor__):
            result_p = p1.symmetric_difference(p2)
        return result_p
    else:
        raise Exception("Unexpected type for parameter 'generated_layer' : %s" % str(type(generated_layer)))


def get_elements_for_generated_layers(elements, mapping):
    """
    Given a list of elements and a list of tuples (GeneratedLayer, PPLayer), create new elements according to the boolean
    operations of the GeneratedLayer and place these elements on the specified PPLayer.
    """
    generated_layers = mapping.keys()
    export_layers = mapping.values()
    elems = ElementList()
    process_processelems_dict = dict()
    for generated_layer, export_layer in zip(generated_layers, export_layers):
        shapely_geom = __get_composite_shapely_polygon_for_elements_on_generated_layer__(elements = elements, generated_layer = generated_layer)		    		
        for geom in flatten_shapely_geom(shapely_geom):    
            shape = shapely_geom_to_shape(geom)			    
            elems += Boundary(layer = export_layer, shape = shape)
    return elems





