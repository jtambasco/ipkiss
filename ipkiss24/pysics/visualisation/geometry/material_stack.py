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

from ipcore.all import *
from ...basics.geometry.material_stack import MaterialStackGeometry1D, MaterialStackGeometry2D, MaterialStackGeometry3D

__all__ = []

#####################################################
# Matplotlib visualization routines for geometries
#####################################################

class __MaterialStackGeometry1DVisualizationMixin__(StrongPropertyInitializer):
    def figure_2d(self, width = 1.0):
        """ generate a matplotlib Figure of a MaterialStackGeometry1D object """
        
        from dependencies.matplotlib_wrapper import Figure, Rectangle
        fig = Figure()
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8], projection = 'rectilinear') 
        
        self.__plot_material_stack_on_axes__(axes, x_start = 0.0, x_end = width)
    
        axes.set_xlim(0, width)
        axes.set_ylim(self.origin_z, self.origin_z + self.thickness)
        axes.set_aspect('equal')
        
        return fig

    
    def __plot_material_stack_on_axes__(self, axes, x_start = 0.0, x_end = 1.0, references_for_legend={}):
        from dependencies.matplotlib_wrapper import Rectangle
        width = x_end - x_start 
        height = 0.0
        for m, h  in self.materials_thicknesses: 
            color = m.display_style.color.html_string()
            hatch = m.display_style.stipple.matplotlib_hatch
            patch = Rectangle((x_start, height), width, h, fc=color, hatch=hatch)
            patch.set_linewidth(0)
            axes.add_patch(patch)
            if m not in references_for_legend:
                references_for_legend[m] = (patch, m.name) 
            height += h
        
        return axes    

MaterialStackGeometry1D.mixin(__MaterialStackGeometry1DVisualizationMixin__)

    
class __MaterialStackGeometry2DVisualizationMixin__(StrongPropertyInitializer):
    def figure_2d(self):
        """ generate a matplotlib Figure of a MaterialStackGeometry1D object """
    
        from dependencies.matplotlib_wrapper import Figure, Rectangle, font_manager
        fig = Figure()
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8], projection = 'rectilinear') 
        legend_refs = {}
        x = self.origin_x
        for ms, w in self.stacks_widths:
            ms.__plot_material_stack_on_axes__(axes, x_start = x, x_end = x+w, references_for_legend = legend_refs)
            x += w
            
        SI = self.size_info()
        axes.set_xlim(SI.west, SI.east)
        axes.set_ylim(SI.south, SI.north)
        axes.set_aspect('equal')

        # legend
        prop = font_manager.FontProperties(size=10) 
        patches_for_legend = [ref[0] for ref in legend_refs.values()]
        labels_for_legend = [ref[1] for ref in legend_refs.values()]
        axes.legend(patches_for_legend, labels_for_legend, loc=(0.5,0.9), prop=prop)
            
        return fig

MaterialStackGeometry2D.mixin(__MaterialStackGeometry2DVisualizationMixin__)

class __MaterialStackGeometry3DVisualizationMixin__(StrongPropertyInitializer):
    
    def tvtk_polydata_3d(self):
        from dependencies.tvtk_wrapper import tvtk
        import numpy

        wedge_cell_indices = []
        wedge_points = []       
        wedge_cell_values = []
        wedge_type = tvtk.Wedge().cell_type 
        materials = []

        N = 0 # running point index: increases when new points are added
        
        for shape, stack in self.shapes_stacks: # check whether it needs reverse iteration
            points2d = numpy.flipud(shape.points) # numpy array
            n_points = len(points2d) # number of points in this shape
            points = numpy.hstack([points2d, numpy.zeros([n_points, 1])]) # 2D to 3D array

            # polygon cell with one shape
            polys = tvtk.CellArray()
            cells = numpy.array([n_points] + range(n_points)) # number of points in the cell, and cell indices
            polys.set_cells(1, cells) # number of cells, list of cell points
            pd = tvtk.PolyData()
            pd.points = points
            pd.polys = polys
            
            # triangulate shape: returns another PolyData set
            tri = tvtk.TriangleFilter()
            tri.input = pd
            tri.update()
            triangle_pd = tri.output
            
            ## step 3: generate a second set of top and bottom triangles
            
            point_array = triangle_pd.points.to_array()
            #n = len(point_array)
            #point_array_bottom = point_array + array([0,0,0])
            #point_array_top = point_array + array([0,0,0.5])
            #new_point_array = numpy.vstack([point_array_bottom, point_array_top])
            #index_array = triangle_pd.polys.data.to_array()
            #n_triangles = len(index_array)/4
            #index_array_bottom = index_array
            #index_array_top = numpy.ravel(index_array.reshape(n_triangles, 4) + array([0, n, n, n]))
            #new_index_array = numpy.hstack([index_array_bottom, index_array_top])
            
            #new_polys = tvtk.CellArray()
            #new_polys.set_cells(2*n_triangles, new_index_array)
            #new_pd = tvtk.PolyData()
            #new_pd.points = new_point_array
            #new_pd.polys = new_polys
            
            ##view([new_pd], mapper_type = tvtk.PolyDataMapper)
            
            index_array = triangle_pd.polys.data.to_array()
            n_triangles = len(index_array)/4
            iar = index_array.reshape(n_triangles, 4) 
            
            
            
            # create wedges for every material layer
            z = stack.origin_z
            for material, thickness in stack.materials_thicknesses:
                # create the Wedge cell points and indices
                # reuse the top points of the last cell as the bottom points of the new cell
                wedge_points.append(point_array + numpy.array([0,0,z]))
                wedge_points.append(point_array + numpy.array([0,0,z + 0.999*thickness]))
                wedge_cell_indices.append(numpy.hstack([iar + numpy.array([3, N, N, N]) , # 3 adds to the existing 3: makes 6
                                                        iar[:,1:] + numpy.array([N+ n_points, N + n_points, N + n_points])]
                                                       ).ravel()
                                          ) 
                N += 2 * n_points
                z += thickness
        
                if not material in materials:
                    materials.append(material)
                wedge_cell_values.extend([materials.index(material)] * n_triangles)
                #ds = material.display_style
                #wedge_cell_values.extend([[ds.color.red, ds.color.green, ds.color.blue, ds.alpha]]*n_triangles)

        # create material color lookup table
        colors = []
        color_lut = tvtk.LookupTable()
        n_mat = len(materials)
        color_lut.table_range = (0, n_mat-1)
        color_lut.number_of_colors = n_mat
        for i in range(n_mat):
            ds = materials[i].display_style
            color_lut.set_table_value(i, ds.color.red, ds.color.green, ds.color.blue, ds.alpha) #RGBA
        color_lut.build
        
        ## create mapper
        mapper = tvtk.DataSetMapper()
        mapper.lookup_table = color_lut
        mapper.scalar_range = (0, n_mat-1)
        #mapper.map_scalars(1)
        
        # build cells
        n_cells = len(wedge_cell_indices) * n_triangles
        cell_array = tvtk.CellArray()
        cell_array.set_cells(n_cells, numpy.hstack(wedge_cell_indices))
        cell_types = numpy.array([wedge_type for i in range(n_cells)])
        cell_offset = numpy.array(range(0,7 * n_cells, 7)) # each cell has one counter and 6 points

        # Now create the UnstructuredGrid which will contain the material data.
        ug = tvtk.UnstructuredGrid(points=numpy.vstack(wedge_points))
        # Now just set the cell types and reuse the ug locations and cells.
        ug.set_cells(cell_types, cell_offset, cell_array)
        #scalars = numpy.random.random([n_cells, 1]) # use random data to visualize the triangulation
        scalars = numpy.array(wedge_cell_values)
        ug.cell_data.scalars = scalars
        ug.cell_data.scalars.name = 'material_color'
        ug.cell_data.set_active_scalars("material_color")

        return (ug, mapper)


    
MaterialStackGeometry3D.mixin(__MaterialStackGeometry3DVisualizationMixin__)
