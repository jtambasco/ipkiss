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
from ipcore.runtime.procedure import __Procedure__
from ipcore.runtime.processor import __StopCriterium__
from ipkiss.all import *
from ipkiss.plugins.photonics.port.port import OpticalPort
from pysimul.runtime.engine import __SimulationEngine__
from pysimul.runtime.basic import *
from pysimul.runtime.params import *
from pysimul import *
import matplotlib.lines as LINES
import matplotlib.patches as PATCHES
import matplotlib.text as mtext
from ipkiss.plugins.vfabrication import *
from pysics.basics import *
from pysics.materials.all import *
from pysics.electromagnetics.field import *
from pysics.basics.environment import *
from pysics.basics.field_profile import *
import logging
import numpy as np


class SimulationProcedure(__Procedure__, SimulationParameterContainer): 
    engine = RestrictedProperty(required=True, restriction = RestrictType(__SimulationEngine__), doc = "Engine used for the simulation.") 
    landscape = RestrictedProperty(required=True, restriction = RestrictType(SimulationLandscape), doc = "The landscape of the simulation.") 


class SMatrixProcedure(SimulationProcedure):
    pass


class __FieldCalculationProcedure__(SimulationProcedure):
    pass

def __criterium_always_ok__(ref_filename, field_profile):
    return True

class ModeSolverFieldCalculationProcedure(__FieldCalculationProcedure__):

    def run(self, field_extraction_geometry_x_positions, validation_criterium = __criterium_always_ok__, ref_filename = None, inc_field = None):
        LOG.debug("Starting run of FieldCalculationProcedure...")	
        f = self.engine.field_for_geometry(self.landscape.simulation_volume, field_extraction_geometry_x_positions, geometry_name = self.landscape.simulation_id, validation_criterium = validation_criterium, ref_filename = ref_filename, inc_field = inc_field)
        return f

class FDTDFieldCalculationProcedure(__FieldCalculationProcedure__):
    stopcriterium = RestrictedProperty(required=True, restriction = RestrictType(__StopCriterium__), doc = "Stopcriterium for the simulation procedure.") 
    interactive_mode = BoolProperty(default = False)
    save_images = BoolProperty(default = True)	

    def run(self, interactive_mode = False):
        self.interactive_mode = interactive_mode
        LOG.debug("Starting run of FDTDFieldCalculationProcedure...")
        try:
            self.visualize_landscape()
        except Exception, e:
            print 'Cannot visualize in FDTDFieldCalculationProcedure. Maybe DISPLAY is not set and you''re working remote? Error:', e

        LOG.debug("Initializing the engine...")		
        self.engine.initialise_engine(self.landscape)
        self.save_engine_dielectricum_to_file()
        LOG.debug("Initiliazing the processor...")
        self.step_processor.initialize(engine = self.engine)
        LOG.debug("FieldCalculationProcedure - starting the simulation...")
        stop = False		
        stepCount = 1
        if self.interactive_mode:
            i = raw_input("Press <return> to start the simulation...")
        while (not stop):
            self.engine.step()
            self.step_processor.process()
            stop = self.stopcriterium()
            stepCount = stepCount + 1
            if( (stepCount % 10000) == 0 ):
                flxcntr = 0
                for flx in self.landscape.datacollectors:
                    if isinstance(flx, Fluxplane):
                        flx.collect()
                        wavelengths = 1000.0 / flx.flux_per_freq[0] 
                        fluxes = flx.flux_per_freq[1]
                        for wl, flux in zip(wavelengths, fluxes):
                            print 'flux',flxcntr, ': (step', stepCount,  '), ', wl, flux
                        #double enter so gnuplot can interpret this correctly as new data.
                        print 'flux',flxcntr, ': '
                        print 'flux',flxcntr, ': '
                        flxcntr += 1


        LOG.debug("Finalizing the processor...")		
        self.step_processor.finalize()	
        #collect the values of the fluxes
        for flx in self.landscape.datacollectors:
            if isinstance(flx, Fluxplane):
                flx.collect()
        self.post_processor.process()
        LOG.debug("FieldCalculationProcedure finished !")

    def visualize_landscape_through_engine(self):
        '''Visualize the dielectricum as it was processed by the engine (by requesting a dataset of the dielectricum-values from the engine)'''
        if self.interactive_mode:		
            LOG.debug("Visualization of the dielectric through the engine...")
            from dependencies.matplotlib_wrapper import pyplot as PYPLOT
            PYPLOT.ion()						
            ds = self.engine.get_material_dataset()
            self.create_visualization(ds, indicate_window = False)	
            PYPLOT.draw()
            i = raw_input("Press <return> to continue...")
            LOG.debug("End of visualization...")

    def visualize_landscape(self):
        '''Visualize the dielectricum as it was defined with the __SimulationVolume__ class '''
        if self.interactive_mode or self.save_images:
            LOG.debug("Visualization of the dielectric...")
            from dependencies.matplotlib_wrapper import pyplot as PYPLOT
            PYPLOT.ion()			
            ds = self.landscape.get_material_dataset(self.engine.resolution)
            self.create_visualization(ds, indicate_window = True)
            if self.save_images:
                PYPLOT.savefig(self.landscape.simulation_id+"_landscape.png", dpi = 500)
            if self.interactive_mode:		
                PYPLOT.draw()
                i = raw_input("Press <return> to continue or '0' to abort...")
                if (i.find("0")>=0):
                    import sys
                    print "Exiting..."
                    sys.exit(0)
                PYPLOT.clf()
                PYPLOT.cla()			

    def save_engine_dielectricum_to_file(self, filename = None):
        '''Save the dielectricum to file (as it was defined with the __SimulationVolume__ class) '''
        if self.save_images:
            LOG.debug("Saving visualization of the dielectric to file...")
            filename = self.engine.save_dielectricum_image(filename)
            if ((not (filename is None)) and (self.interactive_mode)):
                try:
                    from dependencies.pil_wrapper import Image
                    png_file = filename.replace(".h5",".png")
                    im = Image.open(png_file)
                    im.show()				
                except Exception, e:
                    LOG.error("Unexpected error with python-PIL : %s" %str(e))

    def __contourf_material_matrix_effective_index__(self, pyplot, simulation_volume, material_array):
        from pysics.materials.electromagnetics import transform_material_stack_matrix_in_effective_index_epsilon_matrix
        eps = transform_material_stack_matrix_in_effective_index_epsilon_matrix(material_array, simulation_volume.geometry.material_stack_factory)				
        resolution = int(eps.shape[1] / simulation_volume.size_info.height)
        grid = 1.0 / simulation_volume.get_total_resolution()
        len_x = eps.shape[0]
        len_y = eps.shape[1]
        x = numpy.linspace(simulation_volume.size_info.west, simulation_volume.size_info.east, num = len_x)
        y = numpy.linspace(simulation_volume.size_info.south, simulation_volume.size_info.north, num = len_y)
        msf = simulation_volume.geometry.material_stack_factory
        pyplot.contourf(x, y, numpy.transpose(eps)) # FIXME: use appropriate colors
        #pyplot.contourf(x, y, numpy.transpose(eps), color = (msf.MSTACK_SOI_AIR.display_style.color.html_string, 
        #                                                     msf.MSTACK_SOI_SI_150nm.display_style.color.html_string, 
        #                                                     msf.MSTACK_SOI_SI_220nm.display_style.color.html_string) ) #transpose: for some reason, contourf uses flipped x en y axes.... the other matplotlib functions work on regular x/y axes...					



    def create_visualization(self, material_dataset, indicate_window = False):		
        '''Do the visualisation with Matplotlib'''		
        LOG.debug("Initiating the visualization in Python....")
        from dependencies.matplotlib_wrapper import pyplot as PYPLOT
        PYPLOT.ion()					
        #we now have a dataset that contains the eps-values of the dielectricum. Let's draw it.
        dim = len(material_dataset.shape)
        if (dim == 1):
            raise NotImplementedException("MeepSimulationEngine::visualizeDielectric -   not yet implemented for 1D")	    
        elif (dim== 2):    
            vol = self.landscape.simulation_volume
            box = vol.size_info.box
            PYPLOT.clf()
            #convert the material matrix into epsilon values for visualisation
            from pysimul.visualization.visualization import SimulationVolumeVisualization2D
            self.__contourf_material_matrix_effective_index__(PYPLOT, simulation_volume = vol, material_array = material_dataset)			
            ax = PYPLOT.axes() 
            ax.set_aspect('equal')
            #indicate the simulation window with a yellow rectangle
            if (indicate_window):
                if (vol.has_window_defined()):
                    width = vol.window_width 
                    height = vol.window_height
                    from matplotlib.patches import Rectangle
                    corner = vol.get_window_south_west()
                    rect = Rectangle(corner, width, height, color = 'y', alpha = 0.5)
                    ax.add_patch(rect)
            #indicate the sources with a  yellow line
            for src in self.landscape.sources:	
                if isinstance(src, GaussianPointSource):
                    c = PATCHES.Circle((src.point.x, src.point.y), delta*4.0, color = 'y', label = "SRC")
                    ax.add_patch(c)
                else:
                    l = MyLine([src.north.x, src.south.x], [src.north.y, src.south.y], linewidth=1, color = 'y', label = "S") 
                    ax.add_line(l)
            #draw the flux planes with a thick green line
            for dc in self.landscape.datacollectors:				
                if isinstance(dc, Fluxplane):
                    l = MyLine([dc.north.x, dc.south.x], [dc.north.y, dc.south.y], linewidth=1, color = 'g', label = "F") 
                    ax.add_line(l)
                elif  isinstance(dc, Probingpoint):
                    delta = 1.0 / vol.get_total_resolution()
                    c = PATCHES.Circle((dc.point.x, dc.point.y), delta*4.0, color = 'c', label = "P")
                    ax.add_patch(c)
                else:
                    pass
                    #raise NotImplementedException("MeepSimulationEngine::visualize -   visualisation for this type of datacollector has not been implemented yet.")
        elif (dim == 3):
            raise NotImplementedException("MeepSimulationEngine::visualize -   not yet implemented for 3D")	





class MyLine(LINES.Line2D):

    def __init__(self, *args, **kwargs):
        # we'll update the position when the line data is set
        self.text = mtext.Text(0, 0, '')
        LINES.Line2D.__init__(self, *args, **kwargs)
        self.text.set_text(kwargs["label"])

    def set_figure(self, figure):
        self.text.set_figure(figure)
        LINES.Line2D.set_figure(self, figure)

    def set_axes(self, axes):
        self.text.set_axes(axes)
        LINES.Line2D.set_axes(self, axes)

    def set_data(self, x, y):
        if len(x):
            self.text.set_position((x[1], y[1]))	
        LINES.Line2D.set_data(self, x, y)

    def draw(self, renderer):
        # draw my label at the end of the line with 2 pixel offset
        LINES.Line2D.draw(self, renderer)
        self.text.draw(renderer)				



class SlabCalculationProcedure(__FieldCalculationProcedure__):
    interactive_mode = BoolProperty(default = False)
    save_images = BoolProperty(default = True)	

    def run(self):
        LOG.debug("Starting run of SlabCalculationProcedure...")
        self.visualize_landscape()
        fields = self.engine.slab_field_calculation()
        return fields

    def visualize_landscape(self):
        if self.interactive_mode or self.save_images:
            self.create_visualization()
            #if self.save_images:
                #PYPLOT.savefig(self.landscape.simulation_id+"_landscape.png", dpi = 500)

    #def create_visualization(self, material_dataset, indicate_window = False):		
    def create_visualization(self, indicate_window = False):		
        '''Do the visualisation with Matplotlib'''		
        LOG.debug("Initiating the visualization in Python....")				
        vol = self.landscape.simulation_volume
        box = vol.size_info.box
        input_vector = self.landscape.simulation_volume.component.input_vector
        output_vector = self.landscape.simulation_volume.component.output_vector
        #convert the material matrix into epsilon values for visualisation
        from pysimul.visualization.visualization import SimulationVolumeVisualization2D
        vis = SimulationVolumeVisualization2D(simulation_volume = vol)
        #vis.contourf_material_matrix_effective_index(PYPLOT, material_dataset)	
        fig = vis.visualize()
        #add code for visualizing the vectors

        x11 = input_vector.position.x
        y11 = input_vector.position.y
        x21 = 10.0 * np.cos(input_vector.angle_rad)
        y21 = 10.0 * np.sin(input_vector.angle_rad)
        fig.axes[0].arrow(x11,y11,x21, y21, width=1.0)

        x12 = output_vector.position.x
        y12 = output_vector.position.y
        x22 = 10.0 * np.cos(output_vector.angle_rad)
        y22 = 10.0 * np.sin(output_vector.angle_rad)
        fig.axes[0].arrow(x12,y12,x22, y22, width=1.0)
        fig.axes[0].set_aspect('equal')	
        #from ipkiss.visualisation.show import  
        from dependencies.matplotlib_wrapper import Tk, FigureCanvasTkAgg
        name = self.landscape.simulation_volume.name
        root = Tk.Tk()
        root.wm_title("Virtual fabrication of %s" %name)   
        fig_canvas = FigureCanvasTkAgg(fig, master=root)
        filename_png = "%s.png" %name
        fig.savefig(filename_png)
        root.destroy()

        #show(fig, title="Hello from Shibnath")
        return