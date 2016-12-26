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
from .layout import TriangularPhCLayout, DodecPhCLayout, PhCHolesProperty, __PhCAutoMap__
from ipkiss.plugins.photonics.port.port import OpticalPort, InOpticalPort, OutOpticalPort
from ipkiss.plugins.photonics.wg import *
from math import sqrt, ceil, cos, sin, pi

__all__ = ["GenericW1Waveguide",
           "W1Waveguide",
           "W1WaveguideWithInlineCavity",
           "W1WaveguideWithAllpass"]


class __GenericW1Slice__(__PhCAutoMap__, TriangularPhCLayout):
    unit_cells = RestrictedProperty(required = True, doc = "List of unit cells: center to outside")
    port_row = IntProperty(allow_none = True, restriction= RESTRICT_NONNEGATIVE)
    port_width = PositiveNumberProperty(allow_none = True)
    port_offset = NumberProperty(default = 0.0)
    start_even = BoolProperty(default = True)

    def define_cells(self):
        cells = {}
        cell_letters = "ABCDEFGHIJKLMNOPQRSTUVWXY"
        L = len(self.unit_cells)
        for i in range(0,L):
            H1 = cell_letters[2*i]
            C = self.unit_cells[i]
            if not C is None:
                cells[H1] = self.unit_cells[i]
        return cells
    
    
class __GenericW1Waveguide__(__GenericW1Slice__):
    n_o_periods = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    cells_map = DefinitionProperty(fdef_name = "define_cells_map")
    
    def define_map(self):
        (cells, mymap) = self.cells_map
        return mymap

    def define_cells(self):
        (cells, mymap) = self.cells_map
        return cells
    
    
class GenericW1WaveguideSection( __GenericW1Waveguide__):
    """ unterminated W1 wavegudie section """
    __name_prefix__ = "SW1_A"

    def define_name(self):
        port_row = -1 if self.port_row is None else self.port_row
        port_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width
        name = ("%s_P%d_%d_U%d_L%d_P%d_%d_%d_E%d_%s_%s" %
                (self.__name_prefix__,
                 self.lattice_pitches[0]*1000,
                 self.lattice_pitches[1]*1000,
                 do_hash("".join([u.name for u in self.unit_cells])),
                 self.n_o_periods,
                 port_row,
                 port_width *1000,
                 self.port_offset * 1000,
                 int(self.start_even),
                 self.process_wg.extension,
                 self.process_hfw.extension) 
                )
        return name
           

    def define_cells_map(self):
        maplist = []
        if self.start_even:
            k = 1
        else:
            k = 0
        L = len(self.unit_cells)
        cell_letters = "ABCDEFGHIJKLMNOPQRSTUVWXY"
        cells = {}
        for i in range(L):
            k+= 1
            H = cell_letters[i]
            C = self.unit_cells[i]
            if not C is None:
                cells[H] = self.unit_cells[i]

            if k%2:
                maplist.append("/%d,%s /" % (self.n_o_periods, H))
            else:
                maplist.append(" /%d,%s /" % (self.n_o_periods, H))
        
        mymap = "\n".join(maplist)
        return (cells, mymap)

    def define_ports_coordinates(self):
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition
        wg_def = WgElDefinition(wg_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width,
                                trench_width = TECH.WG.TRENCH_WIDTH,
                                process = TECH.PROCESS.WG
                                )
        port_row = (len(self.unit_cells)-1)/2 if self.port_row is None else self.port_row
        port_col = self.port_offset / self.pitches[0]
        
        return [((-port_col, -port_row), -180, wg_def),
                ((port_col + self.n_o_periods, -port_row), 0.0, wg_def)
                 ]
    #def define_ports(self, prts):
        #if self.port_row is None: 
            #port_row = (len(self.unit_cells)-1)/2
        #else:
            #port_row = self.port_row
        #port_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width

        #ports += [OldPort((-self.port_offset, port_row * sqrt(0.75)*self.lattice_pitches[1]), TECH.WG.TRENCH_WIDTH, 180.0, self.process_wg), 
                  #OldPort((self.port_offset+ self.lattice_pitches[0] * (self.n_o_periods), port_row * sqrt(0.75)*self.lattice_pitches[1]), port_width, TECH.WG.TRENCH_WIDTH, 0.0, self.process_wg)]
        #return ports
    

class GenericW1WaveguideTermination(__GenericW1Slice__):
    """ unterminated W1 waveguide section """
    
    __name_prefix__ = "TW1_A"
    cells_map = DefinitionProperty(fdef_name = "define_cells_map")  
    
    def define_name(self):
        port_row = -1 if self.port_row is None else self.port_row
        port_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width
        name = ("%s_P%d_%d_U%d_P%d_%d_%d_E%d_%s_%s" %
                (self.__name_prefix__,
                 self.lattice_pitches[0]*1000,
                 self.lattice_pitches[1]*1000,
                 do_hash("".join([u.name for u in self.unit_cells])),
                 port_row,
                 port_width *1000,
                 self.port_offset * 1000,
                 int(self.start_even),
                 self.process_wg.extension,
                 self.process_hfw.extension) 
                )
        return name
    
    def define_map(self):
        (cells, mymap) = self.cells_map
        return mymap

    def define_cells(self):
        (cells, mymap) = self.cells_map
        return cells
               
    def define_cells_map(self):
        maplist = []
        
        if self.start_even:
            k = 1
        else:
            k = 0
        L = len(self.unit_cells)
        cell_letters = "ABCDEFGHIJKLMNOPQRSTUVWXY"
        cells = {}
        for i in range(L):
            k+= 1
            H = cell_letters[i]
            C = self.unit_cells[i]
            if not C is None:
                cells[H] = self.unit_cells[i]

            if k%2:
                maplist.append("/%s /" % (H))
            else:
                maplist.append(" /%s /" % (H))        
        mymap = "\n".join(maplist)        
        return (cells,mymap)
    

    def define_ports_coordinates(self):
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition
        wg_def = WgElDefinition(wg_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width,
                                trench_width = TECH.WG.TRENCH_WIDTH,
                                process = TECH.PROCESS.WG
                                )
        port_row = (len(self.unit_cells)-1)/2 if self.port_row is None else self.port_row
        port_col = self.port_offset / self.pitches[0]
        
        return [((-port_col, -port_row), -180, wg_def),
                ((port_col , -port_row), 0.0, wg_def)
                 ]
    #def define_ports(self, prts):
        #if self.port_row is None: 
            #port_row = (len(self.unit_cells)-1)/2
        #else:
            #port_row = self.port_row
        #port_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width

        #ports += [OldPort((-self.port_offset, port_row * sqrt(0.75)*self.lattice_pitches[1]),  port_width, TECH.WG.TRENCH_WIDTH, 180.0, self.process_wg), 
                      #OldPort((self.port_offset, port_row * sqrt(0.75)*self.lattice_pitches[1]), sqrt(3.0)*self.lattice_pitches[1], port_width, TECH.WG.TRENCH_WIDTH, 0.0, self.process_wg)]
        #return ports
    

class GenericW1Waveguide(__GenericW1Waveguide__):
    """ terminated W1 waveguide """
    
    __name_prefix__ = "GW1_A"
    
    def __init__(self, lattice_pitches, unit_cells, n_o_periods,process_wg = TECH.PROCESS.WG, process_hfw = TECH.PROCESS.HFW, **kwargs):
        super(generic_W1_waveguide, self).__init__(
            lattice_pitches = lattice_pitches,
            unit_cells = unit_cells,
            n_o_periods = n_o_periods,
            process_wg = process_wg,
            process_hfw = process_hfw,
            **kwargs)

    def define_name(self):
        port_row = -1 if self.port_row is None else self.port_row
        port_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width
        name = ("%s_P%d_%d_U%d_L%d_P%d_%d_%d_E%d_%s_%s" %
                (self.__name_prefix__,
                 self.lattice_pitches[0]*1000,
                 self.lattice_pitches[1]*1000,
                 do_hash("".join([u.name for u in self.unit_cells])),
                 self.n_o_periods,
                 port_row,
                 port_width * 1000, 
                 self.port_offset * 1000,
                 int(self.start_even),
                 self.process_wg.extension,
                 self.process_hfw.extension) 
                )
        return name

    def define_cells_map(self):
        maplist = []
        if self.start_even:
            k = 1
        else:
            k = 0
        L = len(self.unit_cells)
        cell_letters = "ABCDEFGHIJKLMNOPQRSTUVWXY"
        cells = {}
        for i in range(L):
            k+= 1
            H = cell_letters[i]
            C = self.unit_cells[i]
            if not C is None:
                cells[H] = self.unit_cells[i]

            if k%2:
                maplist.append("/%d,%s /" % (self.n_o_periods, H))
            else:
                maplist.append(" /%d,%s /" % (self.n_o_periods-1, H))
        
        mymap = "\n".join(maplist)
        return (cells,mymap)

    def define_ports_coordinates(self):
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition
        wg_def = WgElDefinition(wg_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width,
                                trench_width = TECH.WG.TRENCH_WIDTH,
                                process = TECH.PROCESS.WG
                                )
        port_row = (len(self.unit_cells)-1)/2 if self.port_row is None else self.port_row
        port_col = self.port_offset / self.pitches[0]
        
        return [((-port_col, -port_row), -180, wg_def),
                ((port_col + self.n_o_periods - 1, -port_row), 0.0, wg_def)
                 ]
    #def define_ports(self, prts):
        #if self.port_row is None: 
            #port_row = (len(self.unit_cells)-1)/2
        #else:
            #port_row = self.port_row
        #port_width = sqrt(3.0)*self.lattice_pitches[1] if self.port_width is None else self.port_width
        #ports += [OldPort((-self.port_offset, port_row * sqrt(0.75)*self.lattice_pitches[1]),  port_width, TECH.WG.TRENCH_WIDTH, 180.0, self.process_wg), 
                      #OldPort((self.port_offset + self.lattice_pitches[0] * (self.n_o_periods-1), port_row * sqrt(0.75)*self.lattice_pitches[1]), port_width, TECH.WG.TRENCH_WIDTH, 0.0, self.process_wg)]
        #return ports
    

class __W1__(DodecPhCLayout):
    pitch = PositiveNumberProperty(required = True)
    diameter = PositiveNumberProperty(required = True)
    defect_diameter = NonNegativeNumberProperty(default = 0.0)
    n_o_cladding_layers = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    n_o_periods = IntProperty(restriction = RESTRICT_POSITIVE, required = True)
    hole_sizes = DefinitionProperty(fdef_name = "define_hole_sizes")
    map = DefinitionProperty(fdef_name = "define_map")

    def define_zero_line_y(self):
        return self.n_o_cladding_layers + 1
    
    def define_ports_coordinates(self):
        from ipkiss.plugins.photonics.wg.basic import WgElDefinition
        wg_def = WgElDefinition(wg_width = sqrt(3.0)*self.pitch ,
                                trench_width = TECH.WG.TRENCH_WIDTH,
                                process = TECH.PROCESS.WG
                                )
        port_row = 0.0
        port_col = (0.5*cos(pi/12.0)* self.diameter + TECH.TECH.MINIMUM_LINE) / self.pitch
        
        return [((-port_col, port_row), -180, wg_def),
                ((port_col + self.n_o_periods-1, port_row), 0.0, wg_def)
                 ]
    
    
class W1Waveguide(__W1__):
    
    __name_prefix__ = "W1"            

    def define_name(self):
        return "%s_A%d_D%d_C%d_L%d_DC%d_%s_%s" % (self.__name_prefix__,
                                             self.pitch*1000,
                                             self.diameter * 1000,
                                             self.n_o_cladding_layers,
                                             self.n_o_periods,
                                             self.defect_diameter * 1000,
                                             self.process_wg.extension,
                                             self.process_hfw.extension)
    
    def define_hole_sizes(self):        
        hole_sizes = {}
        hole_sizes['A'] = self.diameter
        if not self.defect_diameter == 0.0:
            hole_sizes['Z'] = self.defect_diameter
        return hole_sizes
        
    def define_map(self):
        maplist = []
        for i in range(self.n_o_cladding_layers, 0, -1):
            if i%2:
                maplist.append("/" + str(self.n_o_periods) + ",A /")
            else:
                maplist.append(" /" + str(self.n_o_periods-1) + ",A /")
    
        maplist.append(" /" + str(self.n_o_periods-1) + ",Z /")
        
        for i in range(1, self.n_o_cladding_layers+1):
            if i%2:
                maplist.append("/" + str(self.n_o_periods) + ",A /")
            else:
                maplist.append(" /" + str(self.n_o_periods-1) + ",A /")
        
        mymap = "\n".join(maplist)
        return mymap

    
    
    #def define_ports(self, ports):
        #yCo = self.n_o_cladding_layers * sqrt(0.75)*self.pitch
        #trench_width = 2.0
        #deltaX = 0.5*cos(pi/12.0)* self.diameter + 0.12
        #wg_width = sqrt(3.0)*self.pitch
        #xLength = self.pitch * (self.n_o_periods-1)
        #wg_def = WgElDefinition(wg_width = wg_width, trench_width = trench_width, process = self.process_wg)
        #ports += [OpticalPort(position = (- deltaX, yCo), angle = 180.0, wg_definition = wg_def), 
                      #OpticalPort(position = (xLength + deltaX, yCo), wg_definition = wg_def, angle = 0.0)]
        #return ports

                      
class W1WaveguideWithInlineCavity(__W1__):
    
    __name_prefix__ = "W1IL_A"
    cavity_holes = PhCHolesProperty(required = True)
    hole_sizes_map = DefinitionProperty(fdef_name = "define_hole_sizes_map")

    def define_name(self):
        cavity_holes_name = ""
        for c in self.cavity_holes:
            cavity_holes_name += "%d"%(int(c*1000))
        cavity_holes_name = str(do_hash(cavity_holes_name))
        return "%s_A%d_D%d_C%d_L%d_DC%d_CH%s_%s_%s" % (self.__name_prefix__,
                                              self.pitch*1000,
                                              self.diameter * 1000,
                                              self.n_o_cladding_layers,
                                              self.n_o_periods,
                                              self.defect_diameter*1000,
                                              cavity_holes_name,
                                              self.process_wg.extension,
                                              self.process_hfw.extension)

    def define_hole_sizes(self):
        (hole_sizes, mymap) = self.hole_sizes_map
        return hole_sizes

    def define_map(self):
        (hole_sizes, mymap) = self.hole_sizes_map
        return mymap
        
    def define_hole_sizes_map(self):
        hole_sizes = {}
        hole_sizes['A'] = self.diameter
        if not self.defect_diameter == 0.0:
            hole_sizes['Z'] = self.defect_diameter
        cav_str = ""
        for i in range(len(self.cavity_holes)):
            hole_sizes[chr(66+i)] = self.cavity_holes.values()[i]
            cav_str += chr(66+i) + " "
        cav_str += "  "
        for i in range(len(self.cavity_holes), 0, -1):
            cav_str += chr(65+i) + " "
            
        maplist = []
        for i in range(self.n_o_cladding_layers, 0, -1):
            if i%2:
                maplist.append("/" + str(self.n_o_periods) + ",A /")
            else:
                maplist.append(" /" + str(self.n_o_periods-1) + ",A /")
        n_core = int(floor((self.n_o_periods - 2* len(self.cavity_holes) - 1) /2.0))
        maplist.append("/" + str(n_core) +  ", Z/ " + cav_str + "/" + str(n_core) + ",Z /")
       
        for i in range(1, self.n_o_cladding_layers+1):
            if i%2:
                maplist.append("/" + str(self.n_o_periods) + ",A /")
            else:
                maplist.append(" /" + str(self.n_o_periods-1) + ",A /")

        mymap = "\n".join(maplist)
        return (hole_sizes, mymap)
    
        
    #def define_ports(self, prts):
        #wg_def = WgElDefinition(wg_width = sqrt(3.0)*self.pitch, trench_width = 2.0, process = self.process_wg)
        #ports += [OpticalPort(position = (- 0.5*cos(pi/12.0) * self.diameter - 0.12, self.n_o_cladding_layers * sqrt(0.75)*self.pitch), angle = 180.0, wg_definition = wg_def),
                      #OpticalPort(position = (self.pitch * (self.n_o_periods-1) + 0.5*cos(pi/12.0)* self.diameter + 0.12, self.n_o_cladding_layers * sqrt(0.75)*self.pitch), 
                                  #angle = 0.0, wg_definition = wg_def)]
        #return ports
    

class W1WaveguideWithAllpass(__W1__):
    __name_prefix__ = "W1AP"
    hole_sizes_map = DefinitionProperty(fdef_name = "define_hole_sizes_map")    


    def define_name(self):
        return "%s_A%d_D%d_C%d_L%d_DC%d_%s_%s" % (self.__name_prefix__,
                                       self.pitch*1000,
                                       self.diameter * 1000,
                                       self.n_o_cladding_layers,
                                       self.n_o_periods,
                                       self.defect_diameter * 1000,
                                       self.process_wg.extension,
                                       self.process_hfw.extension)


    def define_hole_sizes_map(self):
        hole_sizes = {}
        hole_sizes['A'] = self.diameter
        if not self.defect_diameter == 0.0:
            hole_sizes['Z'] = self.defect_diameter
        maplist = []
        for i in range(self.n_o_cladding_layers, 1, -1):
            if i%2:
                maplist.append("/" + str(self.n_o_periods) + ",A /")
            else:
                maplist.append(" /" + str(self.n_o_periods-1) + ",A /")
    
        maplist.append("/" + str(int(ceil(self.n_o_periods/2-1))) + ",A /Z /" + str(self.n_o_periods-int(ceil(self.n_o_periods/2))) + ",A /")
        maplist.append(" /" + str(self.n_o_periods-1) + ",A /")
        maplist.append("/" + str(self.n_o_periods) + ",A /")
        maplist.append("/" + str(self.n_o_periods) + ",Z /")
        
        for i in range(1, self.n_o_cladding_layers+1):
            if i%2:
                maplist.append("/" + str(self.n_o_periods) + ",A /")
            else:
                maplist.append(" /" + str(self.n_o_periods-1) + ",A /")
    
        mymap = "\n".join(maplist)
        return (hole_sizes, mymap)
    
    
    
    #def define_ports(self, prts):
        #ports += [OldPort((- 0.5*cos(pi/12.0) * self.diameter - 0.12, self.n_o_cladding_layers * sqrt(0.75)*self.pitch), sqrt(3.0)*self.pitch, 2.0, 180.0, self.process_wg),
                      #OldPort((self.pitch * (self.n_o_periods-1) + 0.5*cos(pi/12.0)* self.diameter + 0.12, self.n_o_cladding_layers * sqrt(0.75)*self.pitch), sqrt(3.0)*self.pitch, 2.0, 0.0, self.process_wg)]
        #return ports
    
