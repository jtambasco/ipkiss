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

if __name__ == "__main__":
    from technologies.si_photonics.picazzo.default import *
    
from ipkiss.all import *
from ipkiss.io.output_gdsii import FileOutputGdsii
from ipkiss.plugins.photonics.wg import *
from ipkiss.plugins.photonics.wg.window import WindowWaveguideDefinition, WindowsOnWaveguideDefinition, PathWindow
    
#################################################################################################"
# example: waveguide definition for shallow waveguide with p-n junction, contacts and silicides
#################################################################################################"

class JunctionWaveguideDefinition(WgElDefinition):
    process = ProcessProperty(default = TECH.PROCESS.FC) #shallow etched
    
    p_process = ProcessProperty(default = TECH.PROCESS.P1)
    n_process = ProcessProperty(default = TECH.PROCESS.N1)
    pp_process = ProcessProperty(default = TECH.PROCESS.PPLUS)
    nn_process = ProcessProperty(default = TECH.PROCESS.N1)
    sal_process = ProcessProperty(default = TECH.PROCESS.SAL)
    
    junction_offset = NumberProperty(default = 0.0, doc = "center of junction") 
    junction_overlap = NumberProperty(default = 0.0, doc = "overlap of p and n region")
    
    p_width = NonNegativeNumberProperty(default = 5.0)
    n_width = NonNegativeNumberProperty(default = 5.0)

    pp_offset = NumberProperty(default = 3.0)
    pp_width  = NumberProperty(default = 2.0)
    nn_offset = NumberProperty(default = 3.0)
    nn_width  = NumberProperty(default = 2.0)
    
    salp_offset = NumberProperty(default = 3.2)
    salp_width  = NumberProperty(default = 1.6)
    saln_offset = NumberProperty(default = 3.2)
    saln_width  = NumberProperty(default = 1.6)
    
    flipped = BoolProperty(default = False, doc = "flips all the offsets")
    
    def define_windows(self):
        windows = super(JunctionWaveguideDefinition, self).define_windows()
        
        sign = -1.0 if self.flipped else +1.0
        
        windows += [PathWindow(layer = PPLayer(self.p_process, TECH.PURPOSE.DF.TRENCH),
                               start_offset = -sign * 0.5 * self.junction_overlap + sign* self.junction_offset,
                               end_offset = sign * self.p_width),
                    PathWindow(layer = PPLayer(self.n_process, TECH.PURPOSE.DF.TRENCH),
                               start_offset = sign * 0.5 * self.junction_overlap - sign * self.junction_offset,
                               end_offset = -sign * self.n_width),
                    PathWindow(layer = PPLayer(self.pp_process, TECH.PURPOSE.DF.TRENCH),
                               start_offset = sign * self.pp_offset,
                               end_offset = sign * (self.pp_offset + self.pp_width)),
                    PathWindow(layer = PPLayer(self.nn_process, TECH.PURPOSE.DF.TRENCH),
                               start_offset = -sign * self.nn_offset,
                               end_offset = -sign * (self.nn_offset + self.nn_width)),
                    PathWindow(layer = PPLayer(self.sal_process, TECH.PURPOSE.DF.TRENCH),
                               start_offset = sign * self.salp_offset,
                               end_offset = sign * (self.salp_offset + self.salp_width)),
                    PathWindow(layer = PPLayer(self.sal_process, TECH.PURPOSE.DF.TRENCH),
                               start_offset = -sign * self.saln_offset,
                               end_offset = -sign * (self.saln_offset + self.saln_width)),
                    ]
        return windows
                                                      
                                  
########################################################################################
# example: waveguide definition for single doping window on existing waveguide
########################################################################################

class DopedWaveguideDefinition(WindowsOnWaveguideDefinition):
    doping_process = ProcessProperty(default = TECH.PROCESS.P1)
    doping_width = NonNegativeNumberProperty(default = 1.0)
    
    def define_windows(self):
        return [PathWindow (layer = PPLayer(self.doping_process, TECH.PURPOSE.DF.TRENCH),
                            start_offset = -0.5 * self.doping_width,
                            end_offset = 0.5 * self.doping_width)
                ]
    
    


class PicazzoExampleWindowWaveguide(Structure):
    
    def define_elements(self, elems):
        from picazzo.io.fibcoup import IoFibcoup
        from picazzo.io.column import IoColumn
        layout = IoColumn(name = "EXAMPLE_WINDOW_WAVEGUIDE",
                          y_spacing = 35.0,
                          south_west = (0.0, 0.0),
                          south_east = (3500.0, 0.0),
                          adapter = IoFibcoup
                          )

        # define a shape
        my_path_shape = Shape([(0.0, 0.0), (50.0, 0.0), (100.0, 30.0), (150.0, 5.0)])
        
        # Example 1:
        # Make a standard wire waveguide by using the well-know regular class 'WgElDefinition'        
        wire_wg_def = WgElDefinition(wg_width = 0.6, trench_width = 0.9)        
        wire_wg = wire_wg_def(shape = my_path_shape)
        layout += Structure(name ="wire", elements = [wire_wg], ports = wire_wg.ports)        
        layout.add_blocktitle("REGULAR_WIRE", center_clearout = (500.0,0.0))
        layout.add_emptyline(2)
        
        # Example 2:
        # Make wire waveguide by directly using the raw base class 'WindowWaveguideDefinition'
        from ipkiss.plugins.photonics.wg.window import WindowWaveguideDefinition, PathWindow
        raw_wg_def = WindowWaveguideDefinition(
                            wg_width = 0.45, #no function except for ports
                            trench_width = 2.0, #no function except for ports
                            process = TECH.PROCESS.WG, #no function except for ports
                            windows = 
                            [PathWindow(layer = PPLayer(TECH.PROCESS.WG, TECH.PURPOSE.LF.LINE), start_offset = -0.225, end_offset = 0.225), # waveguide
                             PathWindow(layer = PPLayer(TECH.PROCESS.WG, TECH.PURPOSE.LF_AREA), start_offset = -0.225-2.0, end_offset = 0.225+2.0)
                             # add additional layers if needed
                             ]
                            )
        raw_wg = raw_wg_def(shape = my_path_shape)
        layout += Structure(name ="raw", elements = [raw_wg], ports = raw_wg.ports)
        layout.add_blocktitle("RAW", center_clearout = (500.0,0.0))
        layout.add_emptyline(2)
               
       
        # Example 3:
        # implanted waveguide: doping window on top of other waveguide definition
        doped_wg_def = DopedWaveguideDefinition(wg_definition = wire_wg_def, 
                                                doping_width = 1.5,
                                                doping_process = TECH.PROCESS.P1
                                                )         

        doped_wg = doped_wg_def(shape = my_path_shape)
        layout += Structure(name="doped", elements=[doped_wg], ports = doped_wg.ports)
        layout.add_blocktitle("DOP", center_clearout = (500.0,0.0))
        layout.add_emptyline(2)

        # Example 4:
        # Add new windows to another waveguide definition
        from ipkiss.plugins.photonics.wg.window import WindowsOnWaveguideDefinition
        win_wg_def = WindowsOnWaveguideDefinition(wg_definition = wire_wg_def,
                                                  windows = [PathWindow(layer = PPLayer(TECH.PROCESS.FC, TECH.PURPOSE.DF.TRENCH),
                                                                        start_offset = 0.0,
                                                                        end_offset = 1.0)
                                                             ] # etch an FC window in one side of the waveguide
                                                  )
        win_wg = win_wg_def(shape = my_path_shape)
        layout += Structure(name="window", elements=[win_wg], ports = win_wg.ports)
        
        layout.add_blocktitle("WIN", center_clearout = (500.0,0.0))
        layout.add_emptyline(2)
        
        # Example 5:
        # Modulator : use of JunctionWaveguideDefinition
        mod_wg_def = JunctionWaveguideDefinition()
        mod_wg = mod_wg_def(shape = my_path_shape)
        layout += Structure(name="modulator", elements=[mod_wg], ports = mod_wg.ports)
        layout.add_blocktitle("MOD", center_clearout = (500.0,0.0))
        layout.add_emptyline(2)
        
        # Example 6:
        # Use new waveguide in a rounded connector
        from ipkiss.plugins.photonics.wg.connect import WaveguidePointRoundedConnectElementDefinition
        rounded_wg_def = WaveguidePointRoundedConnectElementDefinition(
                            wg_definition = mod_wg_def , # previous definition, with the junction
                            bend_radius = 20.0, # needs to be sufficiently large with the broad windows
                            )        
        rounded_wg = rounded_wg_def (shape = my_path_shape)
        layout += Structure(name="rounded", elements=[rounded_wg], ports = rounded_wg.ports)
        layout.add_blocktitle("ROUND", center_clearout = (500.0,0.0))
        layout.add_emptyline(2)
        

        # Example 7:
        # Use new waveguide in a spiral
        from picazzo.wg.spiral import WaveguideDoubleSpiralWithIncoupling
        from picazzo.container.taper_ports import TaperShallowPorts        
        spiral = WaveguideDoubleSpiralWithIncoupling(wg_definition = rounded_wg_def,
                                                     spacing = 12.0,
                                                     n_o_loops = 2,
                                                     inner_size = (100.0, 100.0)
                                                     )
        layout += TaperShallowPorts(structure =spiral)                                    
        layout.add_blocktitle("SPIRAL", center_clearout = (500.0,0.0))
                
        elems += SRef(reference = layout)
        return elems
    
        
if __name__ == "__main__":
    layout = PicazzoExampleWindowWaveguide(name = "layout")
    layout.write_gdsii("example_window_waveguides.gds")

        

    