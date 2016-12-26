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
from ipkiss.plugins.photonics.wg.window import WindowsOnWaveguideDefinition
from ipkiss.plugins.photonics.wg.window import PathWindow
from ipkiss.plugins.photonics.wg.window import WindowWaveguideDefinition
from picazzo.wg.taper.layout import __WgElPortTaper__
from numpy import *


#waveguide definition

class LshapeWgDefinition(WindowWaveguideDefinition):
    """L shape waveguide: one side shallow etched, another side deep etched"""  
    # properties are here just to override defaults
    wg_width = PositiveNumberProperty(default = TECH.WG.WIRE_WIDTH)  
    trench_width = NonNegativeNumberProperty(default = TECH.WG.TRENCH_WIDTH)
    process = LockedProperty()    
    polarity=  StringProperty(required = True, restriction=RestrictValueList(allowed_values = ["left","right"]))                                            

    def define_windows(self):
        windows = []
        windows.append(PathWindow(layer = PPLayer(TECH.PROCESS.FC, TECH.PURPOSE.LF.LINE),
                           start_offset = -0.5 * self.wg_width,
                           end_offset = +0.5 * self.wg_width))
        windows.append(PathWindow(layer = PPLayer(TECH.PROCESS.WG, TECH.PURPOSE.LF.LINE),
                           start_offset = -0.5 * self.wg_width,
                           end_offset = +0.5 * self.wg_width))        
        if self.polarity=="left":
            sign=-1 
        else:
            sign=+1.0

        if (self.trench_width > 0.0) :
            windows.append(PathWindow(layer = PPLayer(TECH.PROCESS.FC, TECH.PURPOSE.LF_AREA),
                               start_offset = sign*(-0.5 * self.wg_width),
                               end_offset = sign*(0.5 * self.wg_width + self.trench_width))),
            windows.append(PathWindow(layer = PPLayer(TECH.PROCESS.WG, TECH.PURPOSE.LF_AREA),
                               start_offset = -sign*(-0.5 * self.wg_width),
                               end_offset = -sign*(0.5 * self.wg_width + self.trench_width)))
        return windows
    
    
#taper from LshapeWgDefinition to WgElDefinition 
    
class LshapeWgToWgElDefinitionTaper(__WgElPortTaper__):
    end_wg_def = LockedProperty()
    
    def define_elements(self, elems):
        wg_line_window = self.start_wg_def.windows[0]
        fc_line_window = self.start_wg_def.windows[1]
        fc_lfarea_window = self.start_wg_def.windows[2]
        wg_lfarea_window = self.start_wg_def.windows[3]
        
        taper_elements = Group()
        taper_elem1 = Boundary(layer = wg_lfarea_window.layer,
                               shape = Shape([(wg_lfarea_window.start_offset, 0),
                                              (sign(wg_lfarea_window.end_offset)*(abs(wg_lfarea_window.end_offset)),0),
                                              (wg_lfarea_window.end_offset, self.length),
                                              (wg_lfarea_window.start_offset, self.length)]))
        taper_elements+= taper_elem1
        taper_elem2 = Boundary(layer = wg_line_window.layer,
                       shape = Shape([(wg_line_window.start_offset, 0),
                                      (wg_line_window.end_offset,0),
                                      (wg_line_window.end_offset, self.length),
                                      (wg_line_window.start_offset, self.length)])
                       )
        
        taper_elements+= taper_elem2
        taper_elem3 = Boundary(layer = fc_line_window.layer,
                       shape = Shape([(fc_line_window.start_offset, 0),
                                      (fc_line_window.end_offset,0),
                                      (fc_line_window.end_offset, self.length),
                                      (fc_line_window.start_offset, self.length)]))
        taper_elements+= taper_elem3        

        taper_elem4 = Boundary(layer = fc_lfarea_window.layer,
                       shape = Shape([(fc_lfarea_window.start_offset, 0),
                                      (fc_lfarea_window.end_offset,0),
                                      (fc_lfarea_window.end_offset, self.length),
                                      (fc_lfarea_window.start_offset, self.length)]))
        taper_elements+= taper_elem4    
        
        taper_elem5 = Boundary(layer = wg_lfarea_window.layer,
                       shape = Shape([(wg_lfarea_window.start_offset, self.length),            
                                      (fc_lfarea_window.end_offset, self.length),
                                      (sign(fc_lfarea_window.end_offset)*(abs(fc_lfarea_window.end_offset)), 0),
                                      (fc_lfarea_window.end_offset, 0),
                                      (wg_lfarea_window.start_offset, self.length-1)])
                       )                                                                                                         
        taper_elements+= taper_elem5            
    
        if self.start_port.angle_deg >= 90 and self.start_port.angle_deg <= 270:
            pass
        else: 
            taper_elements.transform(transformation = HMirror())          
        taper_elements_transformed = taper_elements.transform_copy(transformation = Translation(translation = self.start_port.position)  + Rotation(rotation = (self.start_port.angle - 90.0), rotation_center = self.start_port.position) )
        return taper_elements_transformed
    
    def define_ports(self, ports): 
        from ipkiss.plugins.photonics.port import *
        ports += OutOpticalPort(position = (self.start_port.position.x +self.length*cos(self.start_port.angle_rad), 
                                            self.start_port.position.y +self.length*sin(self.start_port.angle_rad)),
                                angle = self.start_port.angle,
                                wg_definition = TECH.WGDEF.WIRE)
        return ports
           
         
    def validate_properties(self):
        if not isinstance(self.start_port.wg_definition,LshapeWgDefinition):
            raise Exception("Start port should have a waveguide definition of type 'LshapeWgDefinition'")
        return True
            
    
    
      
if __name__ == "__main__":
    
    class Example(Structure):
        
        def define_elements(self, elems):
            my_path_shape = Shape([(0.0, 0.0), (50.0, 25.0), (100.0, 30.0), (150.0, 10.0)])
            
            from picazzo.container.taper_ports import TaperDeepPorts
            from ipkiss.plugins.photonics.wg import WgElDefinition                      
            
            #use of LshapeWgDefinition
            l_wg_def = LshapeWgDefinition(polarity="right")
            wg_el = l_wg_def(shape = my_path_shape)
            taper =  LshapeWgToWgElDefinitionTaper(start_port = wg_el.ports[1], length = 20.0)
            taper1 = LshapeWgToWgElDefinitionTaper(start_port = wg_el.ports[0], length = 20.0)

            struct = TaperDeepPorts(structure = Structure(elements=[wg_el,taper,taper1],ports = taper.ports +taper1.ports))                           
            elems += SRef(reference=struct)
            return elems
                      
    
    
    layout = Example(name = "EXAMPLE")
    layout.write_gdsii("l_shape_window_waveguide.gds")
  

