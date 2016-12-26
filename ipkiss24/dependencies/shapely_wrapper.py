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

from sys import stderr
try:
    from shapely.geometry import Polygon
    from shapely.geometry import LineString
    from shapely.ops import cascaded_union
    from shapely.geometry import MultiPolygon 
    from shapely.geometry import MultiLineString
    from shapely.geometry.polygon import LinearRing
    from shapely.geometry import Point
    from shapely.coords import CoordinateSequence
    from shapely.geometry.collection import GeometryCollection
    from shapely.geos import TopologicalError

except ImportError, e:
    print >> stderr, "*************************** DEPENDENCY NOT FOUND **************************************************************************************** "
    print >> stderr, "**** MODULE SHAPELY COULD NOT BE FOUND, PLEASE INSTALL IT                                                                             *** "
    print >> stderr, "**** On Windows, download from :                                                                                                      *** "
    print >> stderr, "****         http://gispython.org/dist/Shapely-1.2.1.win32.exe                                                                        *** "
    print >> stderr, "**** On Linux :                                                                                                                       *** "
    print >> stderr, "****         install from source (version 1.2.1 needed) :                                                                             *** "
    print >> stderr, "****         http://pypi.python.org/packages/source/S/Shapely/Shapely-1.2.1.tar.gz#md5=da54c772443bd0398aa588e0f3e9c190               *** "
    print >> stderr, "***************************************************************************************************************************************** "



try:
    from descartes import PolygonPatch

except ImportError, e:
    print >> stderr, "*************************** DEPENDENCY NOT FOUND **************************************************************************************** "
    print >> stderr, "**** MODULE DESCARTES COULD NOT BE FOUND, PLEASE INSTALL IT                                                                           *** "
    print >> stderr, "**** On both Windows and Linux, install from source as follows:                                                                       *** "  
    print >> stderr, "****         * download from : http://pypi.python.org/packages/source/d/descartes/descartes-1.0.tar.gz                                *** "                                   
    print >> stderr, "****         * extract it. On Windows, you can use 7-zip (available at www.7-zip.org)                                                 *** "
    print >> stderr, "****         * run the following command in the directory where you extracted the file :                                              *** "                                                                             
    print >> stderr, "****                    python setup.py install                                                                                       *** "
    print >> stderr, "***************************************************************************************************************************************** "



def shapely_polygon_to_image(polygon, filename, show=False):
    from dependencies.matplotlib_wrapper import pyplot
    fig = pyplot.gcf()
    fig.clear()
    ax = fig.add_subplot(1,1,1)
    if (not polygon.is_empty):
        if isinstance(polygon, Polygon):
            patch = PolygonPatch(polygon, fc='b')
            ax.add_patch(patch)
        else:
            for p in polygon.geoms:
                try:
                    patch = PolygonPatch(p, fc='b')
                    ax.add_patch(patch)
                except AssertionError:
                    LOG.error("An element of type %s will not be plotted on the image." %type(polygon))			
    ax.autoscale_view() 
    pyplot.axis('equal')
    if show:
        pyplot.show()
    pyplot.savefig(filename, dpi=500)	

def shapely_geom_to_shape(g):
    """Convert a Shapely geometry to an IPKISS shape"""
    from ipkiss.all import Shape, Coord2
    import sys
    if g.is_empty:	
        return Shape()
    elif g.is_ring:
        result_points = g.boundary.coords
        result_shape = Shape(points = result_points)    
    elif isinstance(g, LineString):
        return Shape(g.coords)
    else:
        result_points = []
        if not g.exterior.is_ring:
            raise Exception("Unexpected case : exterior geometry expected to be a Shapely linear ring.")
        if len(g.interiors) == 0:
            result_points = g.exterior.coords
            result_shape = Shape(points = result_points)    
        else:
            g_exterior_coords_list = [c for c in g.exterior.coords]
            for interior in g.interiors:
                result_points = []
                if interior.is_ring:
                    interior_start_point = interior.coords[0]
                    result_points.append(interior_start_point)
                    interior_start_point_coord2 = Coord2(interior_start_point)
                    dist = sys.maxint
                    exterior_point_index = -1
                    for exterior_point in g_exterior_coords_list:
                        exterior_point_index = exterior_point_index + 1
                        curr_dist = interior_start_point_coord2.distance(Coord2(exterior_point))
                        if curr_dist < dist:
                            closest_exterior_point_index = exterior_point_index
                            dist = curr_dist                    
                    result_points.extend(g_exterior_coords_list[closest_exterior_point_index:])
                    result_points.extend(g_exterior_coords_list[0:closest_exterior_point_index])
                    result_points.append(g_exterior_coords_list[closest_exterior_point_index])
                    result_points.append(interior_start_point)
                    result_points.extend(interior.coords)                                            
                else:
                    raise Exception("Unexpected case : interior geometry expected to be a Shapely linear ring.")
                g_exterior_coords_list = result_points
        result_shape = Shape(points = result_points, closed=True)
    return result_shape    


def flatten_shapely_geom(g):
    result_list = []
    if (isinstance(g, MultiPolygon) or isinstance(g, GeometryCollection)) and (not g.is_empty):
        for g2 in g.geoms:
            result_list.extend(flatten_shapely_geom(g2))
    else:
        result_list = [g]
    return result_list

from ipcore.all import *
from ipkiss.all import SizeInfoProperty
from ipkiss.all import LOG

class ShapelyPolygonCollection(StrongPropertyInitializer):
    size_info = SizeInfoProperty(required = True)  
    canvas_polygon = DefinitionProperty(fdef_name = "define_canvas_polygon")
    georep_list = FunctionNameProperty(fget_name = "get_georep_list")
    georep = FunctionNameProperty(fget_name="__get_georep__", fset_name="__set_georep__")

    def __get_georep__(self):
        if not hasattr(self, "__georep__"):
            return MultiPolygon()
        else:
            return self.__georep__

    def __set_georep__(self, value):
        self.__georep__ = value.buffer(0)    

    def fabricate_offspring(self, georep):
        return PolygonCollection(size_info = self.size_info,
                                 georep = georep)		    

    def add_polygon_points(self, pts):
        if len(pts)>2:
            polygon = Polygon(pts)
            if not polygon.is_valid:
                LOG.warning("Tried to add an invalid polygon to the PolygonCollection: %s\nThe polygon is ignored." %str(pts))           
            else:
                self.georep = self.georep.union(polygon)
        else:
            LOG.warning("Tried to add a polygon with %i points to the PolygonCollection: %s\nThe polygon is ignored." %(len(pts),str(pts)))    

    def get_georep_list(self):
        """Return a list with all elements in the geometrical representation """	
        if isinstance(self.georep, MultiPolygon):
            if not self.georep.is_empty:
                return self.georep.geoms
            else:
                return []
        elif isinstance(self.georep, Polygon):
            return [self.georep]
        else:
            if not self.georep.is_empty:
                return self.georep.geoms
            else:
                return []

    def define_canvas_polygon(self):
        nw = list(self.size_info.north_west)
        ne = list(self.size_info.north_east)
        se = list(self.size_info.south_east)
        sw = list(self.size_info.south_west)	    
        p = Polygon([nw,ne,se,sw,nw])
        return p

    def is_empty(self):
        return self.georep.is_empty

    def __do_cascaded_union__(self, p):
        if isinstance(p, Polygon):
            mp = MultiPolygon([p])
            up = cascaded_union(mp)
        else:
            try:
                up = cascaded_union(p)      
            except ValueError:
                raise Exception("__do_cascaded_union__ failed...")
        return up

    def bitwise_or(self, other_polygon_collection):
        if (other_polygon_collection.is_empty()):
            return self
        elif (self.is_empty()):
            return other_polygon_collection
        else:
            other_georep = other_polygon_collection.georep
            my_georep = self.georep
            p1 = self.__do_cascaded_union__(other_georep)
            p2 = self.__do_cascaded_union__(my_georep)          
            mp = p1.union(p2)
            pc = self.fabricate_offspring(mp)
            return pc

    def bitwise_and(self, other_polygon_collection):
        if (other_polygon_collection.is_empty()):
            return self.fabricate_offspring(MultiPolygon())
        elif (self.is_empty()):
            return self.fabricate_offspring(MultiPolygon())
        else:       
            other_georep = other_polygon_collection.georep
            my_georep = self.georep
            p1 = self.__do_cascaded_union__(other_georep)
            p2 = self.__do_cascaded_union__(my_georep)      
            mp = p1.intersection(p2)
            pc = self.fabricate_offspring(mp)
            return pc

    def bitwise_xor(self, other_polygon_collection):
        if (other_polygon_collection.is_empty()):
            return self
        elif (self.is_empty()):
            return other_polygon_collection
        else:
            other_georep = other_polygon_collection.georep
            my_georep = self.georep
            p1 = self.__do_cascaded_union__(other_georep)
            p2 = self.__do_cascaded_union__(my_georep)
            mp = p2.symmetric_difference(p1)
            pc = self.fabricate_offspring(mp)
            return pc

    def bitwise_not(self):
        if (not self.is_empty()):
            my_georep = self.georep
            my_p = self.__do_cascaded_union__(my_georep)
        else:
            my_p = MultiPolygon()       
        mp = self.canvas_polygon.difference(my_p)
        pc = self.fabricate_offspring(mp)
        return pc       

    def difference(self, other_polygon_collection):
        if (other_polygon_collection is None or other_polygon_collection.is_empty()):
            return self	
        elif (self.is_empty()):
            return self
        else:
            other_georep = other_polygon_collection.georep
            my_georep = self.georep
            p1 = self.__do_cascaded_union__(other_georep)
            p2 = self.__do_cascaded_union__(my_georep)	    
            try:
                diff_p = p2.difference(p1)    
            except TopologicalError, err:
                if isinstance(p1, MultiPolygon):
                    diffs = []
                    for p1pol in p1.geoms:
                        d = p2.difference(p1pol)
                        diffs.append(d)
                    diff_p = diffs[0]
                    for d in diffs[1:]:
                        diff_p = diff_p.intersection(d)
                elif isinstance(p2, MultiPolygon):
                    diffs = []
                    for p2pol in p2.geoms:
                        d = p2pol.difference(p1)
                        diffs.append(d)
                    diff_p = MultiPolygon(diffs)
                else:
                    raise err
            pc = self.fabricate_offspring(diff_p)
            return pc   

    def unionize(self):
        if (self.is_empty()):
            return self.georep
        else:
            my_georep = self.georep   
            if isinstance(my_georep, MultiPolygon):
                mp = self.__do_cascaded_union__(my_georep)
                return self.fabricate_offspring(mp)
            else:
                return self.fabricate_offspring(my_georep)

    def save_to_image(self, filename, show=False):
        from dependencies.shapely_wrapper import shapely_polygon_to_image
        shapely_polygon_to_image(self.georep, filename, show)  

