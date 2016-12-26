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

from technologies.si_photonics.picazzo.default import *
from picazzo.awg_pcg import *
from intec.library.awg.design_tools import star_coupler_design as lbawg
from intec.library.awg.design_tools import focus_from_pitch
from intec.library.materials import SOI as materials
from picazzo.wg.aperture import * 
from picazzo.wg.aperture_multi_shallow import ShallowWgApertureMerged
from ipkiss.plugins.photonics.wg.basic import *
from intec.library.awg.awg_design import __AWGRegularDeMuxDesign__
import numpy 
   
        
class MyMMIAWG( __AWGRegularDeMuxDesign__):
    transformation_in = DefinitionProperty(fdef_name = "define_transformation_in")
    transformation_out = DefinitionProperty(fdef_name = "define_transformation_out")

    arm_aperture_width = PositiveNumberProperty(default = 2.0)
    arm_aperture_spacing = PositiveNumberProperty(default = 0.1)
    arm_aperture_medium = RestrictedProperty(restriction = RestrictClass(materials.WaveguideMedium), default = materials.ShallowIosoi220)
    arm_taper_length = PositiveNumberProperty(default = 45.0)
    
    port_aperture_width = PositiveNumberProperty(default = 2.0)
    port_aperture_spacing = PositiveNumberProperty(default = 0.1)
    port_aperture_medium = RestrictedProperty(restriction = RestrictClass(materials.WaveguideMedium), default = materials.ShallowIosoi220)
    port_taper_length = PositiveNumberProperty(default = 25.0)
    
    
    in_port_mmi_width = PositiveNumberProperty(default =5.0)
    in_port_taper_width = PositiveNumberProperty(default =4.0)
    in_port_mmi_length = PositiveNumberProperty(default =19.401)
   
    angle = DefinitionProperty(fdef_name = "define_angle")
    star_couplers = DefinitionProperty(fdef_name = "define_star_couplers")
    star_coupler_offset = NumberProperty(required = True)
    
    # required because of init of parent class
    def __init__(self, name, **kwargs): 
        super(MyMMIAWG, self).__init__(name = name, 
                 star_coupler_in = SUPPRESSED, 
                 star_coupler_out = SUPPRESSED, 
                 delay_line_lengths = SUPPRESSED, 
                 **kwargs)
        pass
    
    
    def get_delay_line_waveguide(self):
        return self.waveguide_medium(self.wg_definition.wg_width)
    
    def define_delay_line_lengths(self):    
        dll =  [i * self.delay for i in range(self.N_arms)]
        return dll
    
    def get_arm_aperture_pitch(self):
        return self.arm_aperture_width + self.arm_aperture_spacing
    
    def get_focus(self):
        cwl = self.get_reference_wavelength()
        arm_aperture_pitch = self.get_arm_aperture_pitch()
        aperture_waveguide = self.arm_aperture_medium(self.arm_aperture_width)
        return focus_from_pitch(arm_aperture_pitch, self.N_arms, aperture_waveguide.angle_deg(cwl)*1.4)
    
    def get_aperture_angles(self):
        cwl = self.get_reference_wavelength()
        arm_aperture_pitch = self.get_arm_aperture_pitch()
        focus = self.get_focus()
        angles = aperture_angles(focus, 0.0, arm_aperture_pitch, self.N_arms+2)
        return angles
        
        
 
    def define_star_couplers(self):
        cwl = self.get_reference_wavelength()
        # arms
        arm_aperture_pitch = self.get_arm_aperture_pitch()
        aperture_waveguide = self.arm_aperture_medium(self.arm_aperture_width)
        focus = focus_from_pitch(arm_aperture_pitch, self.N_arms, aperture_waveguide.angle_deg(cwl)*1.4)
        angles = self.get_aperture_angles()
        arm_aperture_vectors = aperture_mounting_circular((0.0, 0.0), focus, angles)#0.0, arm_aperture_pitch, self.N_arms+2)
        # output ports
        out_port_pole_vector = Vector(position = (focus, 0.0), angle = 180.0)
        out_port_angles = [lbawg.port_angle_from_wavelength(wl, 
                                                      round(self.order), 
                                                      self.delay, 
                                                      self.waveguide.n_eff(wl), 
                                                      self.slab_medium.n_eff(wl), 
                                                      arm_aperture_pitch) for wl in self.out_wavelengths]

        # out_port_angles should reflect the orientation of the delay lines
        #out_port_aperture_vectors = aperture_mounting_circular((focus, 0.0), focus, angles = out_port_angles)
        out_port_aperture_vectors = aperture_mounting_rowland(Vector(position = (focus, 0.0), angle = 180.0), 0.5* focus, angles = out_port_angles)
        sc_out_arms = ShallowWgApertureMerged(vectors = arm_aperture_vectors, 
                                                 aperture_wg_definition=WgElDefinition(wg_width=self.arm_aperture_width), 
                                                 wg_definition = self.wg_definition, 
                                                 dummy_list = [0, -1], 
                                                 taper_length = self.arm_taper_length,
                                                 deep_taper_length = 0.5 * self.arm_taper_length)
        sc_out_ports = ShallowWgApertureMerged(vectors = out_port_aperture_vectors, 
                                                  aperture_wg_definition=WgElDefinition(wg_width=self.port_aperture_width), 
                                                  wg_definition = self.wg_definition,
                                                  dummy_list = self.dummy_out_channels, 
                                                  taper_length = self.port_taper_length)
        star_coupler_out = StarCoupler(aperture_in = sc_out_ports, 
                                            aperture_out = sc_out_arms,
                                            transformation_in = HMirror(), 
                                            transformation_out = HMirror())
        star_coupler_out.angles = out_port_angles
        if self.in_wavelengths is None:
            in_wavelengths = [self.get_reference_wavelength()]
        else:
            in_wavelengths  = self.in_wavelengths
            
        in_port_angles = [lbawg.port_angle_from_wavelength(wl, 
                                                      round(self.order), 
                                                      self.delay, 
                                                      self.waveguide.n_eff(wl), 
                                                      self.slab_medium.n_eff(wl), 
                                                      arm_aperture_pitch) for wl in in_wavelengths]
        in_port_aperture_vectors = aperture_mounting_circular((focus, 0.0), focus, angles = in_port_angles)
        sc_in_arms = sc_out_arms
        in_port_mmi_width = self.in_port_mmi_width
        in_port_taper_width = self.in_port_taper_width
        in_port_mmi_length = self.in_port_mmi_length
        sc_in_ports_mmi = ShallowWgApertureMerged(vectors = in_port_aperture_vectors, 
                                                  aperture_wg_definition = WgElDefinition(wg_width= in_port_mmi_width),
                                                  dummy_list = [], 
                                                  taper_length = in_port_mmi_length,
                                                  deep_taper_length = 10.0,
                                                  wg_definition = WgElDefinition(wg_width = in_port_taper_width),
                                                  shallow_wg_width = in_port_mmi_width,
                                                  deep_taper_width = in_port_mmi_width + 2.0,
                                                  deep_process = TECH.PROCESS.NONE 
                                                  )
        V = [p.move_polar_copy(0.03, p.angle_deg + 180.0) for p in sc_in_ports_mmi.ports]
    
        sc_in_ports_tapers = ShallowWgApertureMerged(vectors = V, 
                                                  dummy_list = [], 
                                                  taper_length = 43.0,
                                                  deep_taper_width = in_port_mmi_width,
                                                  deep_taper_length = 20.0,
                                                  aperture_wg_definition = WgElDefinition(wg_width = in_port_taper_width, trench_width = 3.0),
                                                  wg_definition = WgElDefinition(trench_width = 3.0)                                                  
                                                  )
        
        sc_in_ports = WgApertureWrapper(structure = Structure(
                                        "%s_SC_in_MW_%f_ML_%f" % (self.name, in_port_mmi_width, in_port_mmi_length ),
                                        [SRef(sc_in_ports_mmi), SRef(sc_in_ports_tapers)],
                                        ports = sc_in_ports_tapers.ports)
                                    )

        star_coupler_in = StarCoupler(aperture_in = sc_in_ports, 
                                           aperture_out = sc_in_arms,
                                           transformation_in = HMirror(), 
                                           transformation_out = HMirror())
        star_coupler_in.angles = in_port_angles
        star_coupler_out.angles = out_port_angles
        return (star_coupler_in, star_coupler_out)
    
    
    def define_star_coupler_in(self):
        return self.star_couplers[0]
    
    def define_star_coupler_out(self):    
        return self.star_couplers[1]

    def define_transformation_in(self):
        return IdentityTransform()
        
    def define_transformation_out(self):
        return VMirror(0.5*self.star_coupler_offset)
    
    def define_transformation_grating(self):
        return IdentityTransform()    
    
    def define_angle(self):
        angle = 180.0
        return angle        
    
    def get_in_star_couplers_angles(self):        
        return self.star_coupler_in.angles
    
    def get_out_star_couplers_angles(self):        
        return self.star_coupler_out.angles
        
   
if __name__ == "__main__":
        awg = MyMMIAWG(name = "My_AWG",  N_arms = 29, star_coupler_offset = 150, in_wavelengths = [1.54735])    
        awg.write_gdsii("example_awg_mmi.gds")
        from ipkiss.plugins.vfabrication import *
        awg.visualize_2d()
        print "Done!"
        