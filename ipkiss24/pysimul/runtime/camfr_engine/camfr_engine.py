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

from pysimul.runtime.engine import *
from pysimul.runtime.procedure import *
from pysimul.runtime.processor import *
from pysimul.runtime.basic import *
from pysimul.exc import PythonSimulateException
from pysimul.runtime.basic import __SimulationVolume__, __EMSource__, __GaussianSource__, __ContinuousSource__, __EMPointSource__, __EMVolumeSource__, compEx, compEy, compEz, compHx, compHy, compHz
from pysimul.runtime.procedure import *
from ipcore import *
from ipkiss.technology.technology import *
from ipkiss.geometry.vector import *
try:
    import camfr 
except ImportError,e:
    raise PythonSimulateException("Cannot load CAMFR engine:%s"%e.message)
from ipkiss.plugins.photonics.port.port import OpticalPort
from pysics.basics import *
from pysics.electromagnetics.field import *
from pysics.basics.environment import *
from pysics.basics.field_profile import *
from pysics.electromagnetics.field_profile import *
from ipkiss.plugins.vfabrication import *
import numpy
from pysimul.log import PYSIMUL_LOG as LOG

TECH.CAMFR = TechnologyTree()
TECH.CAMFR.POLARIZATION = camfr.TM # use for top-down simulations of 
TECH.CAMFR.NMODES = 50
TECH.CAMFR.NMODES_PER_MICRON = 3
TECH.CAMFR.PML = -0.05
TECH.CAMFR.WAVELENGTH = 1550

PLOTCOLOR = ['g','r','b','y','c','m','k','ro']
global PLOTCOLORCOUNTER
PLOTCOLORCOUNTER = 0

class IncFieldParameters(object):
    params = dict()

    def set_parameter(self,name,value):
        self.params[name] = value

    def get_parameter(self, name):
        return self.params[name]

inc_field_parameters = IncFieldParameters()
def inc_field_func(x): 
    inc_field_x_coord_new = inc_field_parameters.get_parameter("inc_field_x_coord")


    inc_field_field_value_real_array = inc_field_parameters.get_parameter("inc_field_field_value_real")
    inc_field_field_value_imag_array = inc_field_parameters.get_parameter("inc_field_field_value_imag")

    inc_field_x_coord_array = inc_field_x_coord_new
    inc_field_x_coord = list(inc_field_x_coord_array)
    inc_field_x_coord_max = max(inc_field_x_coord)
    inc_field_x_coord_min = min(inc_field_x_coord)

    inc_field_field_value_real = list(inc_field_field_value_real_array)
    inc_field_field_value_imag = list(inc_field_field_value_imag_array)
    si_south = inc_field_parameters.get_parameter("si_south")
    x_modi = x.real + si_south
    if x_modi > -1.03 or x_modi < -1.47: # co ordinate of the waveguide
        f1 = 0.0
        f2 = 0.0
        f = f1 + f2*(1.0j)
    else:
        f1 = numpy.interp(x_modi, inc_field_x_coord, inc_field_field_value_real)
        f2 = numpy.interp(x_modi, inc_field_x_coord, inc_field_field_value_imag)
        f = f1 + f2*(1.0j)
    return f


class __CamfrGeometryCoordinateConverter__(StrongPropertyInitializer):
    geometry_box = RestrictedProperty(required = True)
    camfr_box_size_x = DefinitionProperty(fdef_name = "define_camfr_box_size_x")    
    camfr_box_size_z = DefinitionProperty(fdef_name = "define_camfr_box_size_z")

    def __call__(self, geometry_coordinate):
        cx, cz = self.camfr_x(geometry_coordinate), self.camfr_z(geometry_coordinate)
        if (cx<0) or (cx>self.camfr_box_size_x) or (cz<0) or (cz>self.camfr_box_size_z) :
            raise PythonSimulateException("Coordinate out of bounds of geometry box")
        return camfr.Coord(cx, 0.0, cz)

    def camfr_x(self, geometry_coordinate):
        return geometry_coordinate[1] - self.geometry_box[2]

    def camfr_z(self, geometry_coordinate):
        return geometry_coordinate[0]-self.geometry_box[0]

    def define_camfr_box_size_z(self):
        return self.geometry_box[1] - self.geometry_box[0]

    def define_camfr_box_size_x(self):
        return self.geometry_box[3] - self.geometry_box[2]

def __criterium_always_ok__(ref_filename, field_profile):
    return True

class CamfrEngine(ModeSolverEngine):  	   
    camfr_technology = RestrictedProperty(default = TECH.CAMFR,  restriction = RestrictType(TechnologyTree))
    save_images = BoolProperty(default = True, doc="Export images (and csv files) of the mode profile and the geometry during the simulation.")

    def initialise_engine_for_landscape(self, landscape):    
        self.landscape = landscape
        n_o_sources = len(landscape.sources)
        if (n_o_sources!=1):
            raise PythonSimulateException("Expected exactly 1 source and got %i...." %n_o_sources)
        elif type(landscape.sources[0]) != ContinuousPointSource:
            raise PythonSimulateException("Expected a datasource of type ContinuousPointSource, but got type %s..." %str(type(landscape.sources[0])))
        self.camfr_technology = copy.deepcopy(TECH.CAMFR)
        self.camfr_technology.WAVELENGTH = landscape.sources[0].center_wavelength
        self.set_camfr_settings()

    def set_camfr_settings(self, camfr_technology):
        camfr_technology.overwrite_allowed = ["WAVELENGTH"] 
        self.camfr_technology = camfr_technology	
        if (type(self.camfr_technology.WAVELENGTH) == int):
            raise Exception("Invalid type for camfr_technology.WAVELENGTH : expected float, not int. ")	
        if (self.camfr_technology.WAVELENGTH > 1.7) or (self.camfr_technology.WAVELENGTH<1.0):
            raise Exception("Invalid range for camfr_technology.WAVELENGTH : expected a float value between 1.0 (1000 nm) and 1.7 (1.7000nm). ")		    
        camfr.set_lambda(self.camfr_technology.WAVELENGTH)
        LOG.debug("Camfr wavelength : %f micron" %self.camfr_technology.WAVELENGTH)
        camfr.set_N(self.camfr_technology.NMODES)
        LOG.debug("Camfr number of modes : %i" %self.camfr_technology.NMODES)
        camfr.set_polarisation(self.camfr_technology.POLARIZATION)
        LOG.debug("Camfr polarization : %s" %str(self.camfr_technology.POLARIZATION))
        camfr.set_lower_PML(self.camfr_technology.PML)
        camfr.set_upper_PML(self.camfr_technology.PML)    		
        LOG.debug("Camfr PML : %f" %self.camfr_technology.PML)

    def set_inc_field(self, camfr_stack):
        camfr_stack = camfr_stack
        inc = numpy.zeros(self.camfr_technology.NMODES)
        inc[0] = 1
        return camfr_stack.set_inc_field(inc) 

    def set_mode_profile_field(self, camfr_stack,inc_field, si_south):
        inc_field_parameters= IncFieldParameters()

        inc_field_parameters.set_parameter("inc_field_x_coord", inc_field[0])
        inc_field_parameters.set_parameter("inc_field_field_value_real", inc_field[1])
        inc_field_parameters.set_parameter("inc_field_field_value_imag", inc_field[2])
        inc_field_parameters.set_parameter("si_south", si_south)

        inc_field_eps = 1
        return camfr_stack.set_inc_field_function(inc_field_func, inc_field_eps)

    def get_camfr_stack_expr_for_geometry(self, geometry, max_slabs = None, geometry_figure_filename = "geometry_for_camfr_field_calculation_%s.png", geometry_name = None):	
        LOG.debug("Now starting camfr_engine::field_for_geometry...")
        geometry_figure_filename = geometry_figure_filename %geometry_name
        from pysics.materials.electromagnetics import get_epsilon_for_material_id
        #retrieve the material matrix for the geometry
        mat = geometry.get_material_array()
        #convert into matrix with epsilon valie
        from pysics.materials.electromagnetics import transform_material_stack_matrix_in_effective_index_epsilon_matrix
        eps = transform_material_stack_matrix_in_effective_index_epsilon_matrix(mat, geometry.material_stack_factory)	
        #create auxiliary arrays for plotting
        grid_step =  1.0/float(geometry.resolution)
        si = geometry.size_info
        len_x = eps.shape[0]
        len_y = eps.shape[1]
        X = numpy.linspace(si.west, si.east, num = len_x)
        Y = numpy.linspace(si.south, si.north, num = len_y)
        if self.save_images:
            #plot
            from pysics.materials.all import *
            #from dependencies.matplotlib_wrapper import pyplot
            #pyplot.clf()
            #pyplot.contourf(X, Y, eps.transpose(), antialiased = True) #transpose: for some reason, contourf uses flipped x en y axes.... the other matplotlib functions work on regular x/y axes...					
            #pyplot.colorbar(orientation='vertical', format = '%i', shrink = 0.5)
            #pyplot.axis('equal')
            #pyplot.savefig(geometry_figure_filename, dpi=300)
        #create a working array 'deltas' with the same dimensions as eps : the first column should contain ones, 
        #the other columns will indicate if there is a difference between that columns in "eps" and the next column
        deltas = numpy.ones_like(eps)
        d = numpy.diff(eps, axis=0)
        for d_counter in xrange(d.shape[0]):
            deltas[d_counter+1] = d[d_counter]
        #now identify the slabs and their width
        slabs_specifications = []
        current_slab_eps = []	
        current_slab_pixel_width = 0
        LOG.debug("Calculating the camfr slabs...")
        for eps_column, delta_column in zip(eps, deltas):
            if (any(delta_column)):
                #if the current eps-column is different from the previous ones, finish the previous slab and add it to the list "slabs_specifications"
                slabs_specifications.append((current_slab_eps, current_slab_pixel_width))
                #start a new slab
                current_slab_eps = eps_column
                current_slab_pixel_width = 1
            else:
                current_slab_pixel_width = current_slab_pixel_width + 1	
        slabs_specifications.append((current_slab_eps, current_slab_pixel_width))

        camfr_stack_expr = camfr.Expression()	
        #must hold materials and slabs in an attribute list, otherwise camfr segmentation faults when cleanup by the garbage collector
        self.materials = dict()	
        self.slabs = []
        #create camfr slabs
        if (max_slabs == None):
            max_slabs = len(slabs_specifications)
        stack_width = 0.0
        for slab_spec in slabs_specifications[1:max_slabs+1]:
            eps_column = slab_spec[0]
            slab_width = slab_spec[1]	    
            if (slab_width ==0) and (len(slabs_specifications[1:])==1):
                raise PythonSimulateException("No slabs could be determined. Fatal error in camfr_engine::mode_profile_for_geometry (is your resolution high enough??)")
            #do the same trick again, but now for the heights
            material_specifications = []
            current_material_eps = 0
            current_material_height = 0
            deltas = [1]
            for d in numpy.diff(eps_column):
                deltas.append(d)
            for eps, delta in zip(eps_column, deltas):
                if (delta != 0):
                    material_specifications.append((current_material_eps, current_material_height))
                    current_material_eps = eps
                    current_material_height = 1
                else:
                    current_material_height = current_material_height +1
            material_specifications.append((current_material_eps, current_material_height))
            LOG.debug("Camfr slab %i : z-width = %f - materials: " %(len(self.slabs)+1, slab_width * grid_step))
            for ms in material_specifications[1:]:
                LOG.debug("                n=%s, height=%s"  %(numpy.sqrt(ms[0]), ms[1]* grid_step))
            #now we know for the current slab which materials are needed with what height
            camfr_slab_expr = camfr.Expression()	    
            for mat_eps, mat_height in material_specifications[1:]:
                if mat_eps in self.materials:
                    mat = self.materials[mat_eps]
                else:
                    mat = camfr.Material(numpy.sqrt(mat_eps))
                    self.materials[mat_eps] = mat			    
                camfr_slab_expr.add(mat(mat_height * grid_step))
            camfr_slab = camfr.Slab(camfr_slab_expr)
            self.slabs.append(camfr_slab)
            #now add this slab to the camfr stack expression
            camfr_stack_expr.add(camfr_slab(slab_width * grid_step))
            stack_width = stack_width + slab_width
            LOG.debug("Camfr: cumulative width of slabs : %f" %(stack_width * grid_step))
        LOG.debug("Camfr stack total width = %f" %(stack_width * grid_step))
        LOG.debug("Camfr stack expression created.")	
        return camfr_stack_expr

    def field_for_geometry(self, geometry, field_extraction_geometry_x_positions = [], field_extraction_grid = 0.01, max_slabs = None, geometry_figure_filename = "geometry_for_camfr_field_calculation_%s.png", mode_profile_figure_filename = "mode_profile_%s.png", geometry_name = None, validation_criterium = __criterium_always_ok__, ref_filename = None, delta_wavelength_faulty_result = 0.000001, inc_field=None):	
        LOG.debug("Now starting camfr_engine::field_for_geometry...")
        mode_profile_figure_filename = mode_profile_figure_filename %geometry_name
        if len(field_extraction_geometry_x_positions) == 0:
            raise PythonSimulateException("Please specify the x positions at which to extract the field profiles. Parameter 'field_extraction_geometry_x_positions' is empty list.")

        maximum_faulty_iterations = 5
        validation = False
        iterations_counter = 0

        while (not validation) and (iterations_counter < maximum_faulty_iterations):	
            camfr_stack_expr = self.get_camfr_stack_expr_for_geometry(geometry = geometry, max_slabs = max_slabs, geometry_figure_filename = geometry_figure_filename, geometry_name = geometry_name)
            camfr_stack = camfr.Stack(camfr_stack_expr)
            LOG.debug("Camfr stack dimensions : (%f,%f)" %(camfr_stack.length(), camfr_stack.width()))	
            #set the incident field and calculate
            if inc_field is None:
                self.set_inc_field(camfr_stack)
            else:
                self.set_mode_profile_field(camfr_stack, inc_field, si.south)

            LOG.debug("Initiating the camfr calculation...")
            camfr_stack.calc()

            #LOG.debug("Initiating the camfr plot...")	    
            #camfr_stack.plot() - doesn't work with Python 2.6 yet
            beta = camfr_stack.inc().mode(0).kz()	
            si = geometry.size_info
            camfr_z_positions = [p - si.west for p in field_extraction_geometry_x_positions]

            field_profiles = []
            for z_position in camfr_z_positions:
                LOG.debug("Now getting the field profile for Camfr z-position %f (geometry position %f)..." %(z_position, z_position + si.west))	
                # get the field profile 
                f = []
                invalid_probing = True
                geometry_y_positions = numpy.arange(si.south, si.north, field_extraction_grid)
                camfr_x_positions = geometry_y_positions - si.south	    
                for camfr_x in camfr_x_positions:
                    coord = camfr.Coord(camfr_x, 0.0, z_position)
                    cf = camfr_stack.field(coord) 
                    f += [ElectroMagneticField(value = [ElectricField(value = (cf.Ez(), cf.E1(), cf.E2())), MagneticField(value = (cf.Hz(), cf.H1(), cf.H2()))])]
                geometry_x_position = z_position + si.west		    
                fp = ElectroMagneticFieldProfile2D(positions = [Coord2(geometry_x_position, camfr_x + si.south) for camfr_x in camfr_x_positions], fields = f)
                field_profiles.append(fp)
                transmission = camfr_stack.T21(0,0)

                if self.save_images:
                    #ensure that output directories exist
                    csv_output_dir = "pysimul_camfr_output/csv/"
                    if not os.path.exists(csv_output_dir):
                        os.makedirs(csv_output_dir)	    
                    img_output_dir = "pysimul_camfr_output/images/"
                    if not os.path.exists(img_output_dir):
                        os.makedirs(img_output_dir)

                    #from dependencies.matplotlib_wrapper import pyplot			

                    #save field to file (image and csv)
                    #Hz
                    #save to image
                    #pyplot.clf()
                    #field_for_plot_real = [f.H.value.z.real for f in fp.fields]  #Hz | Ey -> f.E.value.y
                    #field_for_plot_imag = [f.H.value.z.imag for f in fp.fields] 
                    #field_for_plot_abs = list(abs(numpy.array(field_for_plot_real) + (1j)*numpy.array(field_for_plot_imag)))
                    #pyplot.plot(geometry_y_positions,field_for_plot_abs ,'g')
                    #pyplot.plot(geometry_y_positions,field_for_plot_real,'b')
                    #pyplot.plot(geometry_y_positions,field_for_plot_imag,'r')	
                    image_file = "%sHz_%f_W%f_%s"%(img_output_dir,geometry_x_position,self.camfr_technology.WAVELENGTH,mode_profile_figure_filename)
                    #pyplot.savefig(image_file)
                    #save values to csv   
                    csv_file = image_file.replace('images','csv')
                    csv_file = csv_file.replace('png','csv')
                    csv_file_handle = open(csv_file,'w')
                    data_for_csv = [[p, f.H.value.z.real] for p, f in zip(geometry_y_positions, fp.fields)] 	    
                    numpy.savetxt(csv_file_handle, numpy.array(data_for_csv), delimiter=', ')
                    csv_file_handle.close()	 

                    #Hy
                    #save to image
                    #pyplot.clf()
                    #field_for_plot_real = [f.H.value.y.real for f in fp.fields]  #Hz | Ey -> f.E.value.y
                    #field_for_plot_imag = [f.H.value.y.imag for f in fp.fields]
                    #field_for_plot_abs = list(abs(numpy.array(field_for_plot_real) + (1j)*numpy.array(field_for_plot_imag)))
                    #pyplot.plot(geometry_y_positions,field_for_plot_abs ,'g')
                    #pyplot.plot(geometry_y_positions,field_for_plot_real,'b')
                    #pyplot.plot(geometry_y_positions,field_for_plot_imag,'r')
                    image_file = "%sHy_%f_W%f_%s"%(img_output_dir,geometry_x_position,self.camfr_technology.WAVELENGTH,mode_profile_figure_filename)
                    #pyplot.savefig(image_file)
                    #save values to csv
                    csv_file = image_file.replace('images','csv')	    
                    csv_file = csv_file.replace('png','csv')
                    csv_file_handle = open(csv_file,'w')
                    data_for_csv = [[p, f.H.value.y.real] for p, f in zip(geometry_y_positions, fp.fields)] 	    
                    numpy.savetxt(csv_file_handle, numpy.array(data_for_csv), delimiter=', ')
                    csv_file_handle.close()		    

                    #Hx
                    #save to image
                    #pyplot.clf()
                    #field_for_plot_real = [f.H.value.x.real for f in fp.fields]  #Hz | Ey -> f.E.value.y
                    #field_for_plot_imag = [f.H.value.x.imag for f in fp.fields] 
                    #field_for_plot_abs = list(abs(numpy.array(field_for_plot_real) + (1j)*numpy.array(field_for_plot_imag)))
                    #pyplot.plot(geometry_y_positions,field_for_plot_abs ,'g')                
                    #pyplot.plot(geometry_y_positions,field_for_plot_real,'b')
                    #pyplot.plot(geometry_y_positions,field_for_plot_imag,'r')
                    image_file = "%sHx_%f_W%f_%s"%(img_output_dir,geometry_x_position,self.camfr_technology.WAVELENGTH,mode_profile_figure_filename)
                    #pyplot.savefig(image_file)
                    #save values to csv
                    csv_file = image_file.replace('images','csv')	    
                    csv_file = csv_file.replace('png','csv')
                    csv_file_handle = open(csv_file,'w')
                    data_for_csv = [[p, f.H.value.x.real] for p, f in zip(geometry_y_positions, fp.fields)] 	    
                    numpy.savetxt(csv_file_handle, numpy.array(data_for_csv), delimiter=', ')
                    csv_file_handle.close()

                    #Ez
                    #save to image
                    #pyplot.clf()
                    #field_for_plot_real = [f.E.value.z.real for f in fp.fields]
                    #field_for_plot_imag = [f.E.value.z.imag for f in fp.fields]
                    #field_for_plot_abs = list(abs(numpy.array(field_for_plot_real) + (1j)*numpy.array(field_for_plot_imag)))
                    #pyplot.plot(geometry_y_positions,field_for_plot_abs ,'g')                
                    #pyplot.plot(geometry_y_positions,field_for_plot_real,'b')
                    #pyplot.plot(geometry_y_positions,field_for_plot_imag,'r')	    
                    image_file = "%sEz_%f_W%f_%s"%(img_output_dir,geometry_x_position,self.camfr_technology.WAVELENGTH,mode_profile_figure_filename)
                    #pyplot.savefig(image_file)
                    ##save values to csv
                    csv_file = image_file.replace('images','csv')	    
                    csv_file = csv_file.replace('png','csv')
                    csv_file_handle = open(csv_file,'w')
                    data_for_csv = [[p, f.E.value.z.real] for p, f in zip(geometry_y_positions, fp.fields)] 	    
                    numpy.savetxt(csv_file_handle, numpy.array(data_for_csv), delimiter=', ')
                    csv_file_handle.close()

                    #Ey
                    #save to image
                    #pyplot.clf()
                    #field_for_plot_real = [f.E.value.y.real for f in fp.fields] 
                    #field_for_plot_imag = [f.E.value.y.imag for f in fp.fields] 
                    #field_for_plot_abs = list(abs(numpy.array(field_for_plot_real) + (1j)*numpy.array(field_for_plot_imag)))
                    #pyplot.plot(geometry_y_positions,field_for_plot_abs ,'g')                
                    #pyplot.plot(geometry_y_positions,field_for_plot_real,'b')
                    #pyplot.plot(geometry_y_positions,field_for_plot_imag,'r')
                    image_file = "%sEy_%f_W%f_%s"%(img_output_dir,geometry_x_position, self.camfr_technology.WAVELENGTH,mode_profile_figure_filename)
                    #pyplot.savefig(image_file)
                    ##save values to csv
                    csv_file = image_file.replace('images','csv')	    
                    csv_file = csv_file.replace('png','csv')
                    csv_file_handle = open(csv_file,'w')
                    data_for_csv = [[p, f.E.value.y.real] for p, f in zip(geometry_y_positions, fp.fields)] 	    
                    numpy.savetxt(csv_file_handle, numpy.array(data_for_csv), delimiter=', ')
                    csv_file_handle.close()	    

                    #Ex
                    #save to image
                    #pyplot.clf()
                    #field_for_plot_real = [f.E.value.x.real for f in fp.fields] 
                    #field_for_plot_imag = [f.E.value.x.imag for f in fp.fields] 
                    #field_for_plot_abs = list(abs(numpy.array(field_for_plot_real) + (1j)*numpy.array(field_for_plot_imag)))
                    #pyplot.plot(geometry_y_positions,field_for_plot_abs ,'g')                
                    #pyplot.plot(geometry_y_positions,field_for_plot_real,'b')
                    #pyplot.plot(geometry_y_positions,field_for_plot_imag,'r')	    
                    image_file = "%sEx_%f_W%f_%s"%(img_output_dir,geometry_x_position,self.camfr_technology.WAVELENGTH,mode_profile_figure_filename)
                    #pyplot.savefig(image_file)
                    ##save values to csv
                    csv_file = image_file.replace('images','csv')	    
                    csv_file = csv_file.replace('png','csv')
                    csv_file_handle = open(csv_file,'w')
                    data_for_csv = [[p, f.E.value.x.real] for p, f in zip(geometry_y_positions, fp.fields)] 	    
                    numpy.savetxt(csv_file_handle, numpy.array(data_for_csv), delimiter=', ')
                    csv_file_handle.close()	    

            iterations_counter = iterations_counter + 1		
            validation = validation_criterium(ref_filename, field_profiles)
            if (not validation):
                self.camfr_technology.WAVELENGTH = self.camfr_technology.WAVELENGTH + delta_wavelength_faulty_result
                LOG.warning("WARNING FROM CAMFR_ENGINE : little bit shift of wavelength due to wrong result. New wavelength = %f" %self.camfr_technology.WAVELENGTH) 
                self.set_camfr_settings(self.camfr_technology)

            camfr.free_tmps()

        if (iterations_counter >= maximum_faulty_iterations):
            LOG.warning("ERROR FROM CAMFR_ENGINE : no result could be obtained that is accepted by the validation criterium ! Is your criterium correct ??") 

        return (field_profiles, beta, transmission)       