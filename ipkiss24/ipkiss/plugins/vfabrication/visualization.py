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
from ipkiss.all import get_technology
from ipkiss.log import IPKISS_LOG as LOG
from ipkiss.primitives.structure import Structure


TECH = get_technology()

resolution_default = 10

class StructureVisualizationAspect(object):

    def __initialize(self, resolution = resolution_default, **kwargs):
        params = dict()
        params["structure"] = self
        params["resolution"] = resolution   
        params["resolution_factor"] = 1
        if "vfabrication_process_flow" in kwargs:
            params["vfabrication_process_flow"] = kwargs["vfabrication_process_flow"]	
        if "material_stack_factory" in kwargs:
            params["material_stack_factory"] = kwargs["material_stack_factory"]		    
        from pysimul.integration.component_integration import StructureSimulationDefinition
        self.simul_def = StructureSimulationDefinition(simul_params = params)                      

    def visualize_2d(self, show = True, save_to_image = False, save_to_image_path = "./", save_to_image_filename_without_ext = None, fig_size_factor = 0.1, enter_tk_mainloop = True, aspect_ratio_equal = True, size = None, **kwargs): 
        self.__initialize(**kwargs)
        from pysimul.visualization.visualization import SimulationVolumeVisualization2D
        vis = SimulationVolumeVisualization2D(simulation_volume = self.simul_def.landscape.simulation_volume)              
        fig = vis.visualize(aspect_ratio_equal)   
        if show:
            from ipkiss.visualisation.show import show
            show(fig, title = self.simul_def.landscape.simulation_volume.name, enter_tk_mainloop = enter_tk_mainloop)
        if save_to_image:
            name = self.simul_def.landscape.simulation_volume.name
            si = self.simul_def.landscape.simulation_volume.size_info
            fig_size_factor = fig_size_factor #default = 0.1
            from dependencies.matplotlib_wrapper import Tk, FigureCanvasTkAgg            
            fig_canvas = FigureCanvasTkAgg(fig)
            if not size is None:
                fig.set_size_inches(size)
            else:
                fig.set_size_inches((si.width * fig_size_factor, si.height * fig_size_factor))
            if save_to_image_filename_without_ext is None:
                fname = name
            else:
                fname = save_to_image_filename_without_ext
            filename_svg = save_to_image_path+"%s.svg" %fname
            fig.savefig(filename_svg)
            filename_png = save_to_image_path+"%s.png" %fname
            fig.savefig(filename_png)
            LOG.debug("Virtual fabrication imaged saved as %s.\n>>> Use INKSCAPE to visualize and zoom in on the file (free download at inkscape.org)" %filename_svg)        
            return filename_png


    def visualize_3d_povray(self, camera_pos, look_at=(0,0,1), z_extrusion_factor = 1.0):
        self.__initialize()
        from pysimul.visualization.visualization import SimulationVolumeVisualization3D
        vis = SimulationVolumeVisualization3D(simulation_volume = self.simul_def.landscape.simulation_volume)    	
        vis.make_povray_file(camera_pos = camera_pos, look_at = look_at, z_extrusion_factor = z_extrusion_factor)	


    def __run_os_cmd__(self, cmd):
        if self.__get_meep_engine_type__() == 0:	
            import subprocess
            import os
            fnull = open(os.devnull, 'w')
            LOG.debug(cmd)
            result_value = subprocess.call([cmd], shell = True, stdout = fnull, stderr = fnull)
            fnull.close()
            return result_value
        else:
            print "Additionally, run the following command : ", cmd
            return 0

    def __get_meep_engine_type__(self):
        try:
            from ipkiss.plugins.simulation import MeepSimulationEngine, LowLevelPythonMeepProcedure
            return 0 #direct interface
        except:
            from ipkiss.plugins.simulation import MeepScripter, MeepScripterProcedure
            return 1 #scripter

    def __generate_3d_hdf5__(self, filename_without_ext, resolution = resolution_default):	    
        meep_engine_type = self.__get_meep_engine_type__()
        if meep_engine_type == 0:
            from ipkiss.plugins.simulation import MeepSimulationEngine, LowLevelPythonMeepProcedure
            __meep_engine_class__ = MeepSimulationEngine
            class SaveDielectricumProcedure(LowLevelPythonMeepProcedure): 

                def run(self, filename, interactive_mode = False):
                    self.engine.initialise_engine(self.landscape) 
                    self.save_engine_dielectricum_to_file(filename = filename)				    
            __procedure_class__ = SaveDielectricumProcedure			    
        else:	
            from ipkiss.plugins.simulation import MeepScripter, MeepScripterProcedure
            __meep_engine_class__ = MeepScripter
            __procedure_class__ = MeepScripterProcedure

        if not hasattr(self, "__eps_hdf5_generated__") or not self.__eps_hdf5_generated__:
            simul_params = dict()		
            simul_params["structure"] = self
            simul_params["resolution"] = resolution 
            meep_engine = __meep_engine_class__(resolution = simul_params["resolution"], use_averaging = False)
            simul_params["engine"] = meep_engine
            simul_params["pml_thickness"] = 0.0
            simul_params["include_growth"] = 0.0
            simul_params["dimensions"] = 3
            simul_def = self.create_simulation(simul_params)
            simul_def.procedure_class = __procedure_class__
            if meep_engine_type == 0:
                simul_def.procedure.run(filename = filename_without_ext+".eps.h5")	
            else:
                simul_def.procedure.run(name_template=filename_without_ext)			
            self.__eps_hdf5_generated__ = True	    
            return meep_engine


    def visualize_3d_x_crosssection(self, x_co, resolution = resolution_default):	 
        """Generate a 3D crosssection along the X axis using Meep."""
        filename_without_ext = self.name
        meep_engine = self.__generate_3d_hdf5__(filename_without_ext, resolution)
        from ipkiss.all import Coord3
        meep_coord = meep_engine.__calc_meep_coord__(Coord3(x_co,0,0))
        x_co_meep = int(meep_coord[0] * float(resolution))
        target_filename = filename_without_ext+"_section_x_"+str(x_co)+".png"
        cmd_make_section_png = "h5topng -x "+str(x_co_meep)+" "+filename_without_ext+".eps.h5 -o "+target_filename
        import os
        if (os.name != "posix"):
            raise Exception("The HDF5 file was created, but could not automatically trigger the h5topng command to generate a cross-section : linux installation needed for that.\n%s"%str(cmd_make_section_png))	
        result = self.__run_os_cmd__(cmd = cmd_make_section_png)	    
        if result != 0:
            raise Exception("The following OS command returned an error : %s"%cmd_make_section_png)
        result = self.__run_os_cmd__(cmd = "eog "+target_filename)
        if result != 0:
            raise Exception("The following OS command return and error : %s"%("eog "+target_filename))	

    def visualize_3d_y_crosssection(self, y_co, resolution = resolution_default):	 
        """Generate a 3D crosssection along the Y axis using Meep."""
        filename_without_ext = self.name 
        meep_engine = self.__generate_3d_hdf5__(filename_without_ext, resolution)
        from ipkiss.all import Coord3
        meep_coord = meep_engine.__calc_meep_coord__(Coord3(0,y_co,0))
        y_co_meep = int(meep_coord[1] * float(resolution))
        target_filename = filename_without_ext+"_section_y_"+str(y_co)+".png"
        cmd_make_section_png = "h5topng -y "+str(y_co_meep)+" "+filename_without_ext+".eps.h5 -o "+target_filename
        import os
        if (os.name != "posix"):
            raise Exception("The HDF5 file was created, but could not automatically trigger the h5topng command to generate a cross-section : linux installation needed for that.\n%s"%str(cmd_make_section_png))	
        result = self.__run_os_cmd__(cmd = cmd_make_section_png)	    
        if result != 0:
            raise Exception("The following OS command returned an error : %s"%cmd_make_section_png)
        result = self.__run_os_cmd__(cmd = "eog "+target_filename)
        if result != 0:
            raise Exception("The following OS command returned an error : %s"%("eog "+target_filename))

    def visualize_3d_vtk(self, resolution = resolution_default):	 
        """Generate a 3D HDF5 and VTK file."""
        filename_without_ext = self.name
        self.__generate_3d_hdf5__(filename_without_ext, resolution)
        cmd_make_vtk = "h5tovtk "+filename_without_ext+".eps.h5"
        import os
        if (os.name != "posix"):
            raise Exception("The HDF5 file was created, but could not automatically trigger the h5tovtk command to generate a VTK file : linux installation needed for that.\n%s"%str(cmd_make_vtk))	
        result = self.__run_os_cmd__(cmd = cmd_make_vtk)	    
        if result != 0:
            raise Exception("The following OS command returned an error : %s"%cmd_make_vtk)
        vtk_file = filename_without_ext+".vtk"
        return vtk_file


Structure.mixin_first(StructureVisualizationAspect)

#--------------------------------------------------------------------------

from ipkiss.primitives import Library

import tkSimpleDialog
from Tkinter import *


class __StructuresVFabricationDialog__(tkSimpleDialog.Dialog):

    def __init__(self, master, library, aspect_ratio_equal = True):
        self.library = library     
        self.cb_initial_value = aspect_ratio_equal
        tkSimpleDialog.Dialog.__init__(self, parent = master)

    def body(self, master):
        #label
        self.label = Label(master, text = "Select a structure and click OK to trigger the virtual fabrication.")
        self.label.pack() 
        #checkbox              
        self.aspect_ratio_equal_int = IntVar()
        self.checkbox = Checkbutton(master, text = "Aspect ration equal", variable = self.aspect_ratio_equal_int)
        if self.cb_initial_value:
            self.checkbox.select()
        else:
            self.checkbox.deselect()
        self.checkbox.pack()
        #scrollbar and listbox
        max_len = 0
        structs = self.library.structures
        structs.sort()
        for s in structs:
            max_len = max(max_len, len(s.name))
        self.listbox = Listbox(master, height=min(20,len(self.library.structures)), width=max_len)
        yscroll = Scrollbar(master, command=self.listbox.yview, orient=VERTICAL)
        yscroll.config(command=self.listbox.yview)
        yscroll.pack(side=RIGHT, fill=Y)
        self.listbox.configure(yscrollcommand=yscroll.set)          
        self.listbox.pack() 
        for s in self.library.structures:
            self.listbox.insert(END, s.name)          
        return self.listbox 

    def apply(self):
        self.result = self.listbox.selection_get()
        self.aspect_ratio_equal = (self.aspect_ratio_equal_int.get() > 0)





class LibraryVisualizationAspect(object):

    def select_structures(self, func = lambda x : x):
        aspect_ratio_equal = True
        while 1:
            root = Tk() 
            root.geometry("0x0") # make root "tiny"
            root.overrideredirect(1) # get rid of the frame, border, etc. 
            d = __StructuresVFabricationDialog__(root, self, aspect_ratio_equal)
            if d.result:
                struct = self.__fast_get_structure__(d.result) 
                aspect_ratio_equal = d.aspect_ratio_equal
                print "Preparing the virtual fabrication of %s..." %d.result
                func(self, struct, aspect_ratio_equal = aspect_ratio_equal)                
            else:
                break

    def __do_visualize_2d_for_struct__(self, struct, **kwargs):
        struct.visualize_2d(save_to_image = False, enter_tk_mainloop=False, **kwargs)

    def visualize_structures_2d(self):
        self.select_structures(LibraryVisualizationAspect.__do_visualize_2d_for_struct__)

    def __do_visualize_3d_for_struct__(self, struct):
        struct.visualize_3d(resolution = self.resolution_3d)

    def visualize_structures_3d(self, resolution = 60):
        self.resolution_3d = resolution
        self.select_structures(LibraryVisualizationAspect.__do_visualize_3d_for_struct__)        

Library.mixin_first(LibraryVisualizationAspect)


