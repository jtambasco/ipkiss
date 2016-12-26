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
from pysimul.runtime.basic import SimulationVolume2D
from pysimul.log import PYSIMUL_LOG as LOG

from ipkiss.technology import get_technology

TECH=get_technology()


class __SimulationVolumeVisualization__(StrongPropertyInitializer):
    pass



class SimulationVolumeVisualization2D(__SimulationVolumeVisualization__):
    simulation_volume = RestrictedProperty(required = True, restriction = RestrictType(SimulationVolume2D), doc = "The simulation volume that we want to visualize")   

    def visualize(self, aspect_ratio_equal = True):
        LOG.debug("Preparing the 2D visualization...")
        from dependencies.matplotlib_wrapper import Figure
        from dependencies.shapely_wrapper import PolygonPatch
        geom = self.simulation_volume.geometry	
        si = geom.size_info
        fig = Figure()
        ax = fig.add_axes([0.05, 0.05, 0.85, 0.85], projection = 'rectilinear')		
        LOG.debug("Painting the polygons per material stack type...")	   
        total = len(geom.material_stacks_shapely_polygons)
        count = 0.0
        from dependencies.shapely_wrapper import Polygon, PolygonPatch
        references_for_legend = dict()
        for (material_stack_id, mb) in geom.material_stacks_shapely_polygons: 	
            color = geom.material_stack_factory[material_stack_id].display_style.color.html_string()
            if (not (mb is None)) and (not mb.georep.is_empty):
                for polygon in mb.georep_list:
                    if isinstance(polygon, Polygon):
                        patch = PolygonPatch(polygon, fc=color)
                        patch.set_linewidth(1)
                        ax.add_patch(patch)	
                        references_for_legend[material_stack_id] = (patch, geom.material_stack_factory[material_stack_id].name) 
                    else:
                        LOG.error("An element of type %s will not be plotted." %type(polygon))
            count = count + 1.0
            percent_complete = int(count / total * 100.0)
        if aspect_ratio_equal:
            ax.set_aspect('equal')

        ##legend
        from dependencies.matplotlib_wrapper import font_manager
        prop = font_manager.FontProperties(size=10) 
        patches_for_legend = [ref[0] for ref in references_for_legend.values()]
        labels_for_legend = [ref[1] for ref in references_for_legend.values()]

        ax.legend(patches_for_legend, labels_for_legend, loc=(0.5,0.9), prop=prop)

        ax.autoscale_view()	

        return fig



class SimulationVolumeVisualization3D(SimulationVolumeVisualization2D):

    def make_povray_file(self, camera_pos, look_at=(0,0,1), z_extrusion_factor = 1.0):
        #initialize povray	
        file_name = "%s.pov"%(self.simulation_volume.name)
        from dependencies.povray_wrapper import PovrayFile, Background, Camera, LightSource, Prism, Texture, Pigment
        povray_file=PovrayFile(file_name,"colors.inc","stones.inc")
        bg = Background(color = "White")
        pov_camera_pos = (camera_pos[0], camera_pos[2], camera_pos[1])
        pov_look_at = (look_at[0],look_at[2],look_at[1])
        cam = Camera(location=pov_camera_pos,look_at=pov_look_at)
        light = LightSource(pov_camera_pos, color="White")
        povray_file.write( bg, cam, light)
        #convert virtual fabrication polygons to povray prisms
        geom = self.simulation_volume.geometry	
        si = geom.size_info
        for (material_stack_id, shape) in geom.material_stacks_shapes[1:]: 	
            color = geom.material_stack_factory[material_stack_id].display_style.color.name
            solid_height = geom.material_stack_factory[material_stack_id].solid_height
            if len(shape.points)>0 and solid_height>0:
                povray_prism = Prism(shape.points, heights= (0, solid_height * z_extrusion_factor), opts = [Texture(Pigment(color=color.capitalize()))])
                print "Writing prism with %i points for %s (solid height : %f) in %s" %(len(shape.points), geom.material_stack_factory[material_stack_id].name, geom.material_stack_factory[material_stack_id].solid_height, color)
                povray_file.write(povray_prism)
        print "Povray file generated : ",file_name












