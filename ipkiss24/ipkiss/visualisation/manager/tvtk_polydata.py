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
from dependencies.tvtk_wrapper import tvtk
from .basic import __VisualisationManager__

__all__ = ["TvtkPolydataVisualisationManager"]


class TvtkRenderVisualisationManager(__VisualisationManager__):
    item = RestrictedProperty(required = True, restriction = RestrictType(tvtk.Renderer), doc = "Renderer to be visualized")

    renderer = DefinitionProperty(fdef_name = "define_renderer", locked = True)
    
    def define_renderer(self):
        return self.item

    @cache()
    def get_render_window(self):
        ren = self.renderer
        ren_win = tvtk.RenderWindow()
        ren_win.off_screen_rendering=1
        ren_win.add_renderer(ren)
        ren_win.size = (600, 480)
        ren.background = (1.0, 1.0, 1.0)
        return ren_win
    
    def show(self, title = "Visualisation", hold_for_user = True):
        ren = self.renderer
        iren = tvtk.RenderWindowInteractor()
        ren_win = self.get_render_window()
        ren_win.off_screen_rendering=0
        iren.render_window = ren_win
        
        # Render the scene and start interaction.
        iren.initialize()
        ren_win.render()
        iren.start()
        
    def save_image(self, filename):
        # Save the window to a png file
        ren_win = self.get_render_window()
        w2if = tvtk.WindowToImageFilter()
        w2if.magnification = 2
        w2if.input = ren_win
        w2if.update()
        
        wr = tvtk.PNGWriter()
        wr.input = w2if.output
        wr.file_name = filename
        wr.write()
        
    
class TvtkPolydataVisualisationManager(TvtkRenderVisualisationManager):
    """ Object that manages visualization of TVTK Polydata: on screen, saving to image ...
    """
    item = RestrictedProperty(required = True, restriction = RestrictType(tvtk.DataSet), doc = "PolyData to be visualized")
    mapper_type = RestrictedProperty(default = tvtk.DataSetMapper)
    mapper = DefinitionProperty(fdef_name = "define_mapper")
    
    def define_mapper(self):
        return self.mapper_type()
    
    def define_renderer(self):
        ren = tvtk.Renderer()

        mapper = self.mapper
        mapper.input =  self.item
        mapper.scalar_mode = 'default' #'use_cell_data'
        actor = tvtk.Actor()
        actor.mapper = mapper
        actor.add_position(0, 0, 0)
        
        
        ren.add_actor(actor)
        
        ren.reset_camera()
        # NEED TO FIX CAMERA SETTINGS
        ren.active_camera.azimuth(30)
        ren.active_camera.elevation(20)
        ren.active_camera.dolly(2.8)
        ren.reset_camera_clipping_range()

        return ren
        
   