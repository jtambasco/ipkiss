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
from ipkiss.plugins.simulation import *
from ipkiss.plugins.photonics.port.port import OpticalPort
from os import *
try:
    import meep_mpi as meep
except ImportError, e:
    try :
        import meep as meep
    except ImportError, e:
        raise Exception("Modules 'meep' or 'meep_mpi' not found.")   

class ProcedureClass(LowLevelPythonMeepProcedure,StrongPropertyInitializer):

    property_object = DefinitionProperty(default = 0)
    #wavelength = NumberProperty(default = 1.55)

    def run(self):

        ## TEMPORARY SETTINGS

        wg_bottom = 0.7
        wg_top = 0.7+0.22
        wg_center = (wg_bottom + wg_top)/2.

        #top = 0.7 + 0.38


        ## preparing

        po = self.property_object
        self.engine.initialise_engine(self.landscape)
        fields = meep.fields(self.engine.structure)
        self.save_engine_dielectricum_to_file(po.eps_filename)

        ## Sources

        print 'Center wavelength:',po.wavelength
        print 'Bandwidth:',po.pulse_width
        center_freq = 1.0 / (float(po.wavelength))
        pulse_width_freq =  (float(po.pulse_width)) / (float(po.wavelength)) * center_freq 	
        print 'Center frequency:',center_freq
        print 'Bandwidth:',pulse_width_freq

        if (po.pulsed_source):	    
            src = meep.gaussian_src_time(center_freq, pulse_width_freq)
        else:
            src = meep.continuous_src_time(center_freq)

        source_port_position = po.input_port.transform_copy(Translation(translation=(po.source_input_port_offset,0))).position
        print 'wg_center_old:',wg_center
        wg_center = (po.input_port.wg_definition.process.wg_upper_z_coord+
                     po.input_port.wg_definition.process.wg_lower_z_coord)/2.
        print 'wg_center_new:',wg_center
        c = Coord3(source_port_position[0],
                   source_port_position[1],
                   wg_center)
        print 'coord:',c
        source_position_vec = self.make_meep_vec(c)

        fields.add_point_source(meep.Ey, src, source_position_vec)


        ## 2D Cross section volumes

        for oc in po.output_cuts:
            fn = '%s_eps.h5'%oc.filename
            vol = oc.get_output_volume(self.engine.meepVol)
            f_eps = meep.prepareHDF5File(fn)
            fields.output_hdf5(meep.Dielectric, vol, f_eps)
            del f_eps
            system('h5topng %s'%fn)


        ### Fluxplanes

        self.fluxes = []
        for p in po.output_ports:	    
            pp = p.position
            port_width = p.wg_definition.wg_width
            wg_bottom = p.wg_definition.process.wg_lower_z_coord
            wg_top = p.wg_definition.process.wg_upper_z_coord



            ## Be aware: this is only for ports along y-axis!!
            vec_near = self.make_meep_vec(Coord3(pp[0],pp[1]-port_width/2.0,wg_bottom))
            vec_far = self.make_meep_vec(Coord3(pp[0],pp[1]+port_width/2.0,wg_top))

            fluxplane = meep.volume(vec_near,vec_far)
            fx = fields.add_dft_flux_plane(fluxplane,
                                           center_freq-(pulse_width_freq/4.0),
                                           center_freq+(pulse_width_freq/4.0),
                                           po.dft_terms)
            self.fluxes.append(fx)

        ## Reverse one of the fluxes if necessary

        if po.load_reversed_flux_from_file_ID > -1:
            self.fluxes[po.load_reversed_flux_from_file_ID].load_hdf5(fields, po.load_reversed_flux_from_file_filename)

        if (po.pulsed_source):
            stop = po.stop_time_multiplier * fields.last_source_time()
        else:
            stop = po.stop_time

        print 'Simulation will run for',stop,'time units'

        output_files = []
        for oc in po.output_cuts:
            fn = '%s.h5'%oc.filename
            oc_file = meep.prepareHDF5File(fn)
            output_files.append(oc_file)

        i = 0
        n_o_output = 0
        while (fields.time() < stop):
            if (i > po.output_steps):
                j = 0
                for oc in po.output_cuts:
                    vol = oc.get_output_volume(self.engine.meepVol)
                    fields.output_hdf5(meep.Ey,vol, output_files[j], 1)
                    j+= 1
                n_o_output += 1
                i = 0
            fields.step()
            i += 1

        print n_o_output,'images outputted'
        print 'Outputting field images..'
        del output_files[:]
        for oc in po.output_cuts:
            fn = '%s.h5'%oc.filename
            fn_eps = '%s_eps.h5'%oc.filename
            st = 'h5topng -t 0:%d -R -Zc dkbluered -a yarg -A %s %s'%(n_o_output-1,fn_eps,fn)
            print st
            system(st)
        print 'Outputting done!'

        #print 'obtaining fluxes:'
        self.flux_data = []
        for i in range(len(po.output_ports)):
            fd = meep.getFluxData(self.fluxes[i])
            self.flux_data.append(fd)
            #print fd

        ## Save flux data if necesarry

        if po.save_reversed_flux_to_file_ID > -1:
            fx = self.fluxes[po.save_reversed_flux_to_file_ID]
            fx.scale_dfts(-1);
            fx.save_hdf5(fields, po.save_reversed_flux_to_file_filename)

        return 

    def set_property_object(self,property_object):
        self.property_object = property_object
        return
    def get_flux_data(self,port_ID):
        fd = self.flux_data[port_ID]
        return fd



class OutputCut(StrongPropertyInitializer):
    normal_vector = StringProperty(required = True)
    cut_value = NumberProperty(default = -1)
    filename = StringProperty(required = True)

    def get_output_volume(self,meepVolume):
        sur_max_vec = meepVolume.surroundings().get_max_corner()

        if (self.normal_vector == 'x'):
            if (self.cut_value <0.):
                self.cut_value = sur_max_vec.x()/2.0
            front_vec = meep.vec(self.cut_value,0.0,0.0)
            rear_vec = meep.vec(self.cut_value,sur_max_vec.y(),sur_max_vec.z())
        elif (self.normal_vector == 'y'):
            if (self.cut_value <0.):
                self.cut_value = sur_max_vec.y()/2.0
            front_vec = meep.vec(0.0,self.cut_value,0.0)
            rear_vec = meep.vec(sur_max_vec.x(),self.cut_value,sur_max_vec.z())
        else :
            if (self.cut_value <0.):
                self.cut_value = sur_max_vec.z()/2.0
            front_vec = meep.vec(0.0,0.0,self.cut_value)
            rear_vec = meep.vec(sur_max_vec.x(),sur_max_vec.y(),self.cut_value)

        perp_vol = meep.volume(front_vec,rear_vec)
        return perp_vol

class StructureMeep3DSimulator(StrongPropertyInitializer):


    component = DefinitionProperty(required = True)
    input_port = DefinitionProperty(required = True)
    output_ports = DefinitionProperty(required = True)
    resolution = NumberProperty(default = 30)
    growth = NumberProperty(default = 1.0)
    wavelength = NumberProperty(default = 1.55)
    pulse_width = NumberProperty(default = 0.4)
    source_input_port_offset = NumberProperty(default = -0.25)
    dft_terms = NumberProperty(default = 200)
    output_steps = NumberProperty(default = 500)
    stop_time_multiplier = NumberProperty(default = 5.0)
    stop_time = NumberProperty(default = 160.)
    pulsed_source = BoolProperty(default = True)
    output_cuts = ListProperty(default = [])
    eps_filename = StringProperty(default = 'eps.h5')

    save_reversed_flux_to_file_ID = NumberProperty(default = -1)
    save_reversed_flux_to_file_filename = StringProperty(default = '')

    load_reversed_flux_from_file_ID = NumberProperty(default = -1)
    load_reversed_flux_from_file_filename = StringProperty(default = '')



    def add_output_cut(self,output_cut):
        self.output_cuts.append(output_cut)


    def clear_output_cut_list(self):
        self.output_cuts = []

    def simulate(self):	


        print 'begining to simulate'
        simul_params = dict()
        simul_params["resolution"] = self.resolution
        simul_params["engine"] = MeepSimulationEngine(resolution = simul_params["resolution"], use_averaging = False)
        simul_params["pml_thickness"] = 0.25
        simul_params["include_growth"] = self.growth 
        simul_params["center_wavelength"] = self.wavelength
        simul_params["dimensions"] = 3
        self.simul_def = self.component.create_simulation(simul_params)
        #overwrite the default procedure with your own custom one
        self.simul_def.procedure_class = ProcedureClass
        #start the simulation
        self.simul_def.procedure.set_property_object(self)
        self.simul_def.procedure.run()


    def get_flux(self,port_ID):
        return self.simul_def.procedure.get_flux_data(port_ID)