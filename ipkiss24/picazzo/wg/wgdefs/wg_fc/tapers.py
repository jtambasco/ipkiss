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
from ...tapers.basic import __WgElPortTaper__
from ...tapers.linear import WgElTaperLinear, WgElPortTaperLinear

from ipkiss.plugins.photonics.port import OpticalPort

__all__ = ["WgElPortTaperFromShallow", 
           "WgElPortTaperToShallow",
           "WgElTaperDeepShallow",
           "WgElTaperShallowDeep",
           "WGFCWgElToWgElPortTaper"
           ]

class WgElTaperDeepShallow(WgElTaperLinear):
    """ Taper from deep to shallow etched waveguides """
    deep_only_length = PositiveNumberProperty(allow_none = True, doc = "length of taper on deep etch only")
    deep_only_wg_def = DefinitionProperty(fdef_name = "define_deep_only_wg_def")
    deep_process = ProcessProperty(default = TECH.PROCESS.WG, doc = "deep etch process layer")
    shallow_process = ProcessProperty(default = TECH.PROCESS.FC, doc = "shallow etch process layer")
    deep_only_length_val = DefinitionProperty(fdef_name = "define_deep_only_length_val")
        
    def define_deep_only_length_val(self):
        if self.deep_only_length is None:
            return 0.5*self.length
        else:
            return self.deep_only_length

    def define_deep_only_wg_def(self) :
        return WgElDefinition(wg_width=self.start_wg_def.wg_width+self.start_wg_def.trench_width*2, trench_width=self.end_wg_def.trench_width)
        
    def define_elements(self, elems):
        se = (self.straight_extension[0], max(TECH.TECH.MINIMUM_LINE, self.straight_extension[1]))
        ## WG        
        deep_only_end_position = Coord2(self.start_position[0], self.start_position[1]).move_polar(self.deep_only_length_val, angle_deg(self.end_position, self.start_position))
        taper_wg = WgElTaperLinear(start_wg_def=self.start_wg_def, 
                                   end_wg_def=self.deep_only_wg_def, 
                                   start_position=self.start_position, 
                                   end_position=deep_only_end_position, 
                                   straight_extension= se)
        elems += taper_wg
        
        ## FC
        from ipkiss.plugins.photonics.wg.basic import PathWindow
        # We first create the shape for the wire ...
        start_window = PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE),
                                  start_offset = -0.5 * self.start_wg_def.wg_width,
                                  end_offset = +0.5 * self.start_wg_def.wg_width)
        end_window = PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE),
                                  start_offset = -0.5 * self.end_wg_def.wg_width,
                                  end_offset = +0.5 * self.end_wg_def.wg_width)
        s1 = self.__get_taper_shape__(self.start_position, 
                                      self.end_position, 
                                      start_window,
                                      end_window,
                                      self.straight_extension)
        # Then we create the shape for the inversion layer around it ...
        start_window = PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA),
                                  start_offset = -0.5 * self.start_wg_def.wg_width - self.start_wg_def.trench_width,
                                  end_offset = +0.5 * self.start_wg_def.wg_width + self.start_wg_def.trench_width)
        end_window = PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA),
                                  start_offset = -0.5 * self.end_wg_def.wg_width - self.end_wg_def.trench_width,
                                  end_offset = +0.5 * self.end_wg_def.wg_width + self.end_wg_def.trench_width)
        s2 = self.__get_taper_shape__(self.start_position, 
                                      self.end_position, 
                                      start_window,
                                      end_window,
                                      self.straight_extension)
        elems += Boundary(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), s1)
        elems += Boundary(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), s2)
        return elems

    def define_ports(self, ports):
        angle = angle_deg(self.end_position, self.start_position)
        ports += [InOpticalPort(position = self.start_position, wg_definition = self.start_wg_def, angle = (angle + 180.0)%360.0), 
                 OutOpticalPort(position = self.end_position, wg_definition = self.end_wg_def, angle = angle)]
        return ports    
    
class WgElTaperShallowDeep(WgElTaperDeepShallow) :
    """ taper which converts a shallow etched waveguide into a deep-etched waveguide """  
    
    def define_elements(self, elems) :
        se = (max(self.straight_extension[0], TECH.TECH.MINIMUM_LINE), self.straight_extension[1])

        ## WG
        sp = Coord2(self.end_position[0], self.end_position[1]).move_polar(self.deep_only_length_val, angle_deg(self.start_position, self.end_position))
        taper_wg = WgElTaperLinear(start_wg_def=self.deep_only_wg_def, 
                                   end_wg_def=self.end_wg_def, 
                                   start_position=sp, 
                                   end_position=self.end_position, 
                                   straight_extension=se)
        elems += taper_wg
        ## FC
        from ipkiss.plugins.photonics.wg.basic import PathWindow
        start_window = PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE),
                                  start_offset = -0.5 * self.start_wg_def.wg_width,
                                  end_offset = +0.5 * self.start_wg_def.wg_width)
        end_window = PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE),
                                  start_offset = -0.5 * self.end_wg_def.wg_width,
                                  end_offset = +0.5 * self.end_wg_def.wg_width)
        s1 = self.__get_taper_shape__(self.start_position, 
                                      self.end_position, 
                                      start_window,
                                      end_window,
                                      self.straight_extension)
        start_window = PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA),
                                  start_offset = -0.5 * self.start_wg_def.wg_width - self.start_wg_def.trench_width,
                                  end_offset = +0.5 * self.start_wg_def.wg_width + self.start_wg_def.trench_width)
        end_window = PathWindow(layer = PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA),
                                  start_offset = -0.5 * self.end_wg_def.wg_width - self.end_wg_def.trench_width,
                                  end_offset = +0.5 * self.end_wg_def.wg_width + self.end_wg_def.trench_width)
        s2 = self.__get_taper_shape__(self.start_position, 
                                      self.end_position, 
                                      start_window,
                                      end_window,
                                      self.straight_extension)
        elems += Boundary(PPLayer(self.shallow_process, TECH.PURPOSE.LF.LINE), s1)
        elems += Boundary(PPLayer(self.shallow_process, TECH.PURPOSE.LF_AREA), s2)
        return elems
    
    def define_ports(self, ports):
        angle = angle_deg(self.end_position, self.start_position)
        ports += [InOpticalPort(position = self.start_position, wg_definition = self.start_wg_def, angle = (angle + 180.0)%360.0), 
                 OutOpticalPort(position = self.end_position.move_polar_copy(0.2,angle_deg(self.end_position, self.start_position)), wg_definition = self.end_wg_def, angle = angle)]
        return ports

    
class WgElPortTaperFromShallow(WgElTaperShallowDeep, WgElPortTaperLinear):
    """ Linear taper starting from a shallow port converting it to a deep waveguide """
        
    def define_ports(self,ports):
        return WgElPortTaperLinear.define_ports(self,ports)
    
class WgElPortTaperToShallow(WgElTaperDeepShallow, WgElPortTaperLinear):
    """ Linear taper starting from a deep port converting it to a shallow waveguide """
    def define_ports(self,ports):
        return WgElPortTaperLinear.define_ports(self,ports)


class WGFCWgElToWgElPortTaper(__WgElPortTaper__) :
    """ Linear taper between waveguide of type WGFCWgElDefinition and WgElDefinition
    It should be passed a start_port (with correct wg_def) and the end_wg_def. """
    length = PositiveNumberProperty(default = 10.0)
    taper = DefinitionProperty(fdef_name="define_taper")
    
    
    def define_taper(self) :
        start_wg_def = self.start_port.wg_definition.get_wg_definition_cross_section()
        end_wg_def = self.end_wg_def.get_wg_definition_cross_section()
        if start_wg_def.trench_width == 0.0:
            new_start_wg_def = WgElDefinition(wg_width = start_wg_def.shallow_wg_width,
                                            trench_width = start_wg_def.shallow_trench_width,
                                            process = start_wg_def.shallow_process
                                            )
            new_start_port = OpticalPort(position=self.start_port.position, 
                                   wg_definition=new_start_wg_def, 
                                   angle=self.start_port.angle)
            taper = WgElPortTaperFromShallow(start_port = new_start_port,
                                             end_wg_def = end_wg_def,
                                             length = self.length,
                                             straight_extension = self.straight_extension,
                                             shallow_process = start_wg_def.shallow_process)
        else:
            new_end_wg_def = WGFCWgElDefinition(trench_width = end_wg_def.trench_width,
                                                shallow_wg_width = end_wg_def.wg_width,
                                                shallow_trench_width =start_wg_def.shallow_trench_width,
                                                wg_width = end_wg_def.wg_width,
                                                shallow_process = start_wg_def.shallow_process
                                                )

            taper = WgElPortTaperLinear(start_port=self.start_port, 
                                             end_wg_def=new_end_wg_def, 
                                             length = self.length,
                                             straight_extension=self.straight_extension)

        return taper
    
    
    def define_elements(self, elems) :
        elems += self.taper
        return elems
    
    def validate_properties(self):
        return True     

## DEPRECATE: Replace this waveguide with ThinWg    
#class FCWgElToWgElPortTaper(__WgElPortTaper__) :
    #""" Linear taper between waveguide of type FCWgElDefinition and WgElDefinition
    #It should be passed a start_port (with correct wg_def) and the end_wg_def. """
    #length = PositiveNumberProperty(default = 10.0)
    #taper = DefinitionProperty(fdef_name="define_taper")
    
    
    #def define_taper(self) :
        #start_wg_def = self.start_port.wg_definition.get_wg_definition_cross_section()
        #end_wg_def = self.end_wg_def.get_wg_definition_cross_section()
        #new_end_wg_def = WGFCWgElDefinition(trench_width = end_wg_def.trench_width,
                                            #shallow_wg_width = end_wg_def.wg_width,
                                            #shallow_trench_width =0.5 * (start_wg_def.wg_width + 2.0 - end_wg_def.wg_width),
                                            #wg_width = end_wg_def.wg_width,
                                            #shallow_process = start_wg_def.shallow_process
                                            #)
        #new_start_wg_def = WGFCWgElDefinition(trench_width = start_wg_def.trench_width,
                                        #shallow_wg_width = TECH.TECH.MINIMUM_LINE,
                                        #shallow_trench_width =0.5 * (start_wg_def.wg_width + 2.0 - TECH.TECH.MINIMUM_LINE),
                                        #wg_width = start_wg_def.wg_width,
                                        #shallow_process = start_wg_def.shallow_process
                                        #)
        #new_start_port = OpticalPort(position=self.start_port.position, 
                               #wg_definition=new_start_wg_def, 
                               #angle=self.start_port.angle)
        #taper = WgElPortTaperLinear(start_port=new_start_port, 
                                    #end_wg_def=new_end_wg_def, 
                                    #length = self.length,
                                    #straight_extension=self.straight_extension)
        #return taper
    
    
    #def define_elements(self, elems):
        #elems += self.taper
        #return elems
    
    #def validate_properties(self):
        #return True     

    
##################################
from .wgdef import WGFCWgElDefinition
from ipkiss.plugins.photonics.wg.basic import WgElDefinition

TECH.WGDEF.AUTO_TAPER_DATA_BASE.add(WGFCWgElDefinition, WgElDefinition, WGFCWgElToWgElPortTaper)

##################################

from .wgdef import ShallowWgElDefinition

class __WgElPortTaperFromShallowAuto__(WgElPortTaperFromShallow):
    shallow_process = DefinitionProperty(doc = "shallow etch process layer")
    length = PositiveNumberProperty(default = 20.0, doc = "taper length")
    
    def define_shallow_process(self):
        return self.start_wg_def.process
    
    def define_deep_only_wg_def(self) :
        return WgElDefinition(wg_width=1.5)


TECH.WGDEF.AUTO_TAPER_DATA_BASE.add(ShallowWgElDefinition, WgElDefinition, __WgElPortTaperFromShallowAuto__)
