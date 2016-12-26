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

from ..adapter import IoBlockAdapter
from ipkiss.plugins.photonics.wg.connect import WaveguidePointRoundedConnectElementDefinition
from ipkiss.plugins.photonics.wg.bundle import WgElBundleConnectRoundedGeneric
from ipkiss.plugins.photonics.port.port import  OpticalPort, InOpticalPort, OutOpticalPort, VerticalOpticalPort
from ipkiss.plugins.photonics.port.port_list import OpticalPortList, VerticalOpticalPortList
from ipkiss.plugins.photonics.routing.to_line import RouteToWestAtY, RouteToEastAtY
from picazzo.log import PICAZZO_LOG as LOG
from ipkiss.all import *
import sys
from picazzo.wg.tapers.linear import WgElTaperLinear
from ipkiss.plugins.photonics.wg.basic import WgElDefinition

__all__ = ["IoFibcoupGeneric",
           "IoFibcoupAsymmetric",
           "IoFibcoup"]


#############################################################
# Fiber coupler adapter
#############################################################
class IoFibcoupGeneric(IoBlockAdapter):
    """ generic adapter for grating fiber coupler """
    west_taper_lengths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [300.0])
    west_wg_widths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [3.0])
    west_trench_widths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [TECH.WG.TRENCH_WIDTH])
    west_connect_lengths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [40.0])
    west_bend_radiuses = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [TECH.WG.BEND_RADIUS])
    west_minimum_straights = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [TECH.WG.SHORT_STRAIGHT])
    west_fibcoups = RestrictedProperty(restriction = RestrictTypeList(Structure), default = [TECH.IO.FIBCOUP.DEFAULT_GRATING])
    west_fibcoup_offsets = RestrictedProperty(restriction = RestrictList(RESTRICT_NUMBER), default = [25.6])
    west_fibcoup_taper_lengths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [350.0])
    west_fibcoups_transforms_and_positions = DefinitionProperty()
    west_merged_waveguides = BoolProperty(default = True)

    east_taper_lengths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [300.0])
    east_wg_widths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [3.0])
    east_trench_widths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [TECH.WG.TRENCH_WIDTH])
    east_connect_lengths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [40.0])
    east_bend_radiuses = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [TECH.WG.BEND_RADIUS])
    east_minimum_straights = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [TECH.WG.SHORT_STRAIGHT])
    east_fibcoups = RestrictedProperty(restriction = RestrictTypeList(Structure), default = [TECH.IO.FIBCOUP.DEFAULT_GRATING])
    east_fibcoup_offsets = RestrictedProperty(restriction = RestrictList(RESTRICT_NUMBER), default = [25.6])
    east_fibcoup_taper_lengths = RestrictedProperty(restriction = RestrictList(RESTRICT_POSITIVE), default = [350.0])
    east_fibcoups_transforms_and_positions = DefinitionProperty()
    
    east_merged_waveguides = BoolProperty(default = True)

    # override
    block_trench_position = PositiveNumberProperty(default = 420.0)
    block_trench_width = PositiveNumberProperty(default = 5.0)


    def define_name(self):
        return "%s_FC%d_S%s_H%d_%d_%d" % (self.__name_prefix__,
                                          do_hash("".join([S.name for S in self.west_fibcoups+self.east_fibcoups])),
                                          self.struct.name,
                                          do_hash(str(self.offset) + str(self.y_spacing) + str(self.south_west) + str(self.south_east)),
                                          do_hash(self.west_merged_waveguides) + do_hash(self.east_merged_waveguides),
                                          do_hash(sum(self.west_fibcoup_offsets) + sum(self.east_fibcoup_offsets) + sum(self.west_bend_radiuses) + sum(self.east_bend_radiuses)+
                                                  sum(self.west_connect_lengths) + sum(self.east_connect_lengths) + sum(self.west_minimum_straights) + sum(self.east_minimum_straights) +
                                                  sum(self.west_fibcoup_taper_lengths) + sum(self.east_fibcoup_taper_lengths) +
                                                  sum(self.west_taper_lengths) + sum(self.east_taper_lengths) + sum(self.west_trench_widths) + sum(self.east_trench_widths) +
                                                  sum(self.west_wg_widths) + sum(self.east_wg_widths))
                                          )
    def define_west_fibcoups_transforms_and_positions(self):
        i = 0
        west_fibcoup_and_position = []
        for ypos in self.y_west:
            fc = self.west_fibcoups[i%len(self.west_fibcoups)]
            west_fibcoup_position = (self.west_fibcoup_offsets[i%len(self.west_fibcoup_offsets)], ypos - fc.east_ports[0].y)
            west_fibcoup_and_position.append((fc,west_fibcoup_position,IdentityTransform()))
            i += 1
        return west_fibcoup_and_position
    
    def define_east_fibcoups_transforms_and_positions(self):
        i = 0
        east_fibcoup_and_position = []
        for ypos in self.y_east:
            fc = self.east_fibcoups[i%len(self.east_fibcoups)]
            east_fibcoup_position = (self.width - self.east_fibcoup_offsets[i%len(self.east_fibcoup_offsets)], ypos - fc.east_ports[0].y)
            east_fibcoup_and_position.append((fc,east_fibcoup_position,HMirror()))
            i += 1
        return east_fibcoup_and_position
                
    def define_elements(self, elems):
        super(IoFibcoupGeneric, self).define_elements(elems)    
        T = HMirror() # for east couplers
        for fc,pos,tf in self.west_fibcoups_transforms_and_positions:
            elems += SRef(fc,pos,tf)
        for fc,pos,tf in self.east_fibcoups_transforms_and_positions:
            elems += SRef(fc,pos,tf)
            
        #i = 0
        
        #for ypos in self.y_west:
            #fc = self.west_fibcoups[i%len(self.west_fibcoups)]
            #west_fibcoup_position = (self.west_fibcoup_offsets[i%len(self.west_fibcoup_offsets)], ypos - fc.east_ports[0].y)
            #elems += SRef(fc, west_fibcoup_position)
            #i+= 1

        #i = 0            
        #for ypos in self.y_east:
            #fc = self.east_fibcoups[i%len(self.east_fibcoups)]
            #east_fibcoup_position = (self.width - self.east_fibcoup_offsets[i%len(self.east_fibcoup_offsets)], ypos - fc.east_ports[0].y)
            #elems += SRef(fc, east_fibcoup_position, T)
            #i+= 1

        i = 0
        west_process_match = True
        shapes = []
        wg_widths = []
        trench_widths = []
        radiuses = []
        processes = []
        # get westmost position for ports
        west = 100000000.0
        for ip in self.struct_west_ports:
            west = min(west, ip.position.x)

        for i in range(len(self.struct_west_ports)):
            west_fibcoup = self.west_fibcoups[i%len(self.west_fibcoups)]
            west_fibcoup_port = west_fibcoup.east_ports[0]
            west_fibcoup_length = west_fibcoup_port.position[0] + self.west_fibcoup_offsets[i%len(self.west_fibcoup_offsets)] 
            west_fibcoup_width = west_fibcoup_port.wg_definition.wg_width
            west_fibcoup_trench = west_fibcoup_port.wg_definition.trench_width
            west_connect_length = self.west_connect_lengths[i%len(self.west_connect_lengths)]
            west_taper_length = self.west_taper_lengths[i%len(self.west_taper_lengths)]
            west_trench_width = self.west_trench_widths[i%len(self.west_trench_widths)]
            west_fibcoup_taper_length = self.west_fibcoup_taper_lengths[i%len(self.west_fibcoup_taper_lengths)]           
            west_wg_width = self.west_wg_widths[i%len(self.west_wg_widths)]
            west_bend_radius = self.west_bend_radiuses[i%len(self.west_bend_radiuses)]
            west_minimum_straight = self.west_minimum_straights[i%len(self.west_minimum_straights)]
            west_process = west_fibcoup_port.wg_definition.process

            ip = self.struct_west_ports[i]

            if not ip.wg_definition.process == west_process:
                west_process_match = False
            # position center taper
            t_pos = (west - west_connect_length-TECH.WG.SHORT_STRAIGHT, self.y_west[i])
            #small piece of waveguide at the end
            wg_def = WgElDefinition(wg_width = ip.wg_definition.wg_width, trench_width = ip.wg_definition.trench_width, process = west_process)            
            W = wg_def([t_pos, (t_pos[0] +TECH.WG.SHORT_STRAIGHT , t_pos[1])])
            elems += W
            # taper to the cleave waveguide            
            start_wg_def1 = WgElDefinition(wg_width = ip.wg_definition.wg_width, trench_width = ip.wg_definition.trench_width, process = west_process)            
            end_wg_def1 = WgElDefinition(wg_width = west_wg_width, trench_width = west_trench_width, process = west_process)            
            T = WgElTaperLinear(start_position = t_pos, 
                                end_position = (t_pos[0] - west_taper_length, t_pos[1]), 
                                start_wg_def = start_wg_def1, 
                                end_wg_def = end_wg_def1)
            elems += T
            # draw cleave waveguide (the wider waveguide, connected to the grating coupler)
            wg_def = WgElDefinition(wg_width = west_wg_width, trench_width = west_trench_width, process = west_process)
            elems += wg_def([T.west_ports[0].position, (west_fibcoup_length + west_fibcoup_taper_length, t_pos[1])])
            # draw fibcoup taper (between grating coupler and the cleave waveguide)
            start_wg_def2 = WgElDefinition(wg_width = west_wg_width, trench_width = west_trench_width, process = west_process) 
            end_wg_def2 = WgElDefinition(wg_width = west_fibcoup_width, trench_width = west_fibcoup_trench, process = west_process)  
            elems += WgElTaperLinear(start_position = (west_fibcoup_length+ west_fibcoup_taper_length, t_pos[1]), 
                                     end_position = (west_fibcoup_length, t_pos[1]), 
                                     start_wg_def = start_wg_def2,
                                     end_wg_def = end_wg_def2)
            # generic connector between structure port and taper port
            tp = W.east_ports[0]

            S= Shape(RouteToWestAtY(input_port = ip, 
                                    y_position = tp.position.y, 
                                    bend_radius = west_bend_radius, 
                                    min_straight = west_minimum_straight))
            if len(S) > 2:
                S[-2] = S[-2].translate(tp.position - S[-1])
            S[-1] = tp.position
            shapes += [S]

            wg_widths += [ip.wg_definition.wg_width]
            trench_widths += [ip.wg_definition.trench_width]
            radiuses += [west_bend_radius]
            processes += [west_process]

            #blocking trenches
            elems += Line(PPLayer(west_process, TECH.PURPOSE.LF_AREA), (self.block_trench_position, t_pos[1] + 0.5*west_wg_width + west_trench_width), (self.block_trench_position, t_pos[1]+ 0.5 * self.y_spacing), self.block_trench_width)
            elems += Line(PPLayer(west_process, TECH.PURPOSE.LF_AREA), (self.block_trench_position, t_pos[1] -0.5*west_wg_width - west_trench_width), (self.block_trench_position, t_pos[1]-0.5 * self.y_spacing), self.block_trench_width)
        if len(self.struct_west_ports):
            if self.west_merged_waveguides:
                # TO DO: Sort this out for different processes
                elems += WgElBundleConnectRoundedGeneric(shapes = shapes, 
                                                         wg_widths = wg_widths, 
                                                         trench_widths = trench_widths, 
                                                         bend_radii = radiuses, 
                                                         process = west_process)
            else:
                for (s, w, t, r, p) in zip(shapes, wg_widths, trench_widths, radiuses, processes):
                    wg_def = WgElDefinition(wg_width = w, trench_width = t, process = p)
                    connector_wg_def = WaveguidePointRoundedConnectElementDefinition(wg_definition = wg_def,
                                                                                     bend_radius = r,
                                                                                     manhattan = False)		    
                    elems += connector_wg_def(shape = s)


        shapes = []
        wg_widths = []
        trench_widths = []
        radiuses = []
        processes = []

        east_process_match = True

        # get rigthmost position for ports
        east = -100000000.0
        for op in self.struct_east_ports:
            east = max(east, op.position.x)

        for i in range(len(self.struct_east_ports)):
            east_fibcoup = self.east_fibcoups[i%len(self.east_fibcoups)]
            east_fibcoup_port = east_fibcoup.east_ports[0]
            east_fibcoup_length = east_fibcoup_port.position[0] + self.east_fibcoup_offsets[i%len(self.east_fibcoup_offsets)] 
            east_fibcoup_width = east_fibcoup_port.wg_definition.wg_width
            east_fibcoup_trench = east_fibcoup_port.wg_definition.trench_width
            east_connect_length = self.east_connect_lengths[i%len(self.east_connect_lengths)]
            east_taper_length = self.east_taper_lengths[i%len(self.east_taper_lengths)]
            east_trench_width = self.east_trench_widths[i%len(self.east_trench_widths)]
            east_fibcoup_taper_length = self.east_fibcoup_taper_lengths[i%len(self.east_fibcoup_taper_lengths)]           
            east_wg_width = self.east_wg_widths[i%len(self.east_wg_widths)]
            east_bend_radius = self.east_bend_radiuses[i%len(self.east_bend_radiuses)]
            east_minimum_straight = self.east_minimum_straights[i%len(self.east_minimum_straights)]
            east_process = east_fibcoup_port.wg_definition.process


            op = self.struct_east_ports[i]
            if not op.wg_definition.process == east_process:
                east_process_match = False
            # position taper
            t_pos = (east + east_connect_length+TECH.WG.SHORT_STRAIGHT, self.y_east[i])
            wg_def = WgElDefinition(wg_width = op.wg_definition.wg_width, trench_width = op.wg_definition.trench_width, process = east_process)
            W = wg_def([t_pos, (t_pos[0] -TECH.WG.SHORT_STRAIGHT , t_pos[1])])
            elems += W
            start_wg_def3 = WgElDefinition(wg_width = op.wg_definition.wg_width, trench_width = op.wg_definition.trench_width, process = east_process) 
            end_wg_def3 = WgElDefinition(wg_width = east_wg_width, trench_width = east_trench_width, process = east_process) 
            T = WgElTaperLinear(start_position = t_pos, 
                                end_position = (t_pos[0] + east_taper_length, t_pos[1]), 
                                start_wg_def = start_wg_def3,
                                end_wg_def = end_wg_def3)
            elems += T
            # draw cleave waveguides            
            wg_def = WgElDefinition(wg_width = east_wg_width, trench_width = east_trench_width, process = east_process)
            elems += wg_def([T.east_ports[0].position, (self.width-east_fibcoup_length - east_fibcoup_taper_length, t_pos[1])])
            # draw fibcoup taper	 
            start_wg_def4 = WgElDefinition(wg_width = east_wg_width, trench_width = east_trench_width, process = east_process) 
            end_wg_def4 = WgElDefinition(wg_width = east_fibcoup_width, trench_width = east_fibcoup_trench, process = east_process) 
            elems += WgElTaperLinear(start_position = (self.width-east_fibcoup_length - east_fibcoup_taper_length, t_pos[1]),
                                     end_position = (self.width-east_fibcoup_length, t_pos[1]), 
                                     start_wg_def = start_wg_def4,
                                     end_wg_def = end_wg_def4)
            # generic connector between structure port and taper port
            tp = W.west_ports[0]

            S= Shape(RouteToEastAtY(input_port = op, 
                                    y_position = tp.position.y, 
                                    bend_radius = east_bend_radius, 
                                    min_straight = east_minimum_straight))
            if len(S) > 2:
                S[-2] = S[-2].translate(tp.position - S[-1])
            S[-1] = tp.position
            shapes += [S]

            wg_widths += [op.wg_definition.wg_width]
            trench_widths += [op.wg_definition.trench_width]
            radiuses += [east_bend_radius]
            processes += [east_process]
        if len(self.struct_east_ports):
            if self.east_merged_waveguides:
                # TODO: Correct the bundling to support multiple process layers
                elems += WgElBundleConnectRoundedGeneric(shapes= shapes, 
                                                         wg_widths = wg_widths, 
                                                         trench_widths = trench_widths, 
                                                         bend_radii = radiuses, 
                                                         process = processes[0])
            else:
                for (s, w, t, r, p) in zip(shapes, wg_widths, trench_widths, radiuses, processes):
                    wg_def = WgElDefinition(wg_width = w, trench_width = t, process = p)
                    connector_wg_def = WaveguidePointRoundedConnectElementDefinition(wg_definition = wg_def,
                                                                                     bend_radius = r,
                                                                                     manhattan = False)		    
                    elems += connector_wg_def(shape = s)

        if not (west_process_match and east_process_match):
            if not (west_process_match or east_process_match):
                lr = "west and east"
            elif not west_process_match:
                lr = "west"
            else:
                lr = "east"
            LOG.warning("Some of the %s ports of structure %s are not on the same process layer as the %s fiber couplers" % (lr, self.struct.name, lr))

        return elems

    def define_ports(self, ports):
        # Correct this: fiber couppler ports
        pl = VerticalOpticalPortList()
        cntwest = 0
        cnteast = 0
        for i in range(len(self.y_west)):
            fc,pos,tf = self.west_fibcoups_transforms_and_positions[i]
            for p in fc.ports:
                if isinstance(p,VerticalOpticalPort):
                    vop = p.transform_copy(tf).move_copy(pos)
                    vop.name = "%s_W%d"%(self.name,cntwest)
                    pl += vop
                    cntwest += 1
        for i in range(len(self.y_east)):
            fc,pos,tf = self.east_fibcoups_transforms_and_positions[i]
            for p in fc.ports:
                if isinstance(p,VerticalOpticalPort):
                    vop = p.transform_copy(tf).move_copy(pos)
                    vop.name = "%s_E%d"%(self.name,cnteast)
                    pl += vop
                    cnteast += 1
        (struct_position, struct_west_ports, struct_east_ports) = self.position_west_east_ports
        cnt_c = 0
        for p in self.struct.ports:
            if isinstance(p,VerticalOpticalPort):
                vop = p.transform_copy(self.struct_transformation).move_copy(struct_position)
                vop.name = "%s_C%d"%(self.name,cnt_c)
                pl += vop
                cnt_c += 1
        return pl



class IoFibcoupAsymmetric(IoFibcoupGeneric):
    """ adapter for grating fiber couplers """
    __name_prefix__ = "io_fibcoup_asym_"

    west_taper_length = PositiveNumberProperty(default = 300.0)
    west_wg_width = PositiveNumberProperty(default = 3.0)
    west_trench_width = PositiveNumberProperty(default = TECH.WG.TRENCH_WIDTH)
    west_connect_length = PositiveNumberProperty(default = 40.0)
    west_bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    west_minimum_straight = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    west_fibcoup = StructureProperty(default = TECH.IO.FIBCOUP.DEFAULT_GRATING)
    west_fibcoup_offset = NumberProperty(default = 25.6)
    west_fibcoup_taper_length = PositiveNumberProperty(default = 350.0)

    east_taper_length = PositiveNumberProperty(default = 300.0)
    east_wg_width = PositiveNumberProperty(default = 3.0)
    east_trench_width = PositiveNumberProperty(default = TECH.WG.TRENCH_WIDTH)
    east_connect_length = PositiveNumberProperty(default = 40.0)
    east_bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    east_minimum_straight = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    east_fibcoup = StructureProperty(default = TECH.IO.FIBCOUP.DEFAULT_GRATING)
    east_fibcoup_offset = NumberProperty(default = 25.6)
    east_fibcoup_taper_length = PositiveNumberProperty(default = 350.0)

    west_taper_lengths = DefinitionProperty(fdef_name = "define_west_taper_lengths")
    west_wg_widths = DefinitionProperty(fdef_name = "define_west_wg_widths")
    west_trench_widths = DefinitionProperty(fdef_name = "define_west_trench_widths")
    west_connect_lengths = DefinitionProperty(fdef_name = "define_west_connect_lengths")
    west_bend_radiuses = DefinitionProperty(fdef_name = "define_west_bend_radiuses")
    west_minimum_straights = DefinitionProperty(fdef_name = "define_west_minimum_straights")
    west_fibcoups = DefinitionProperty(fdef_name = "define_west_fibcoups")
    west_fibcoup_offsets = DefinitionProperty(fdef_name = "define_west_fibcoup_offsets")
    west_fibcoup_taper_lengths = DefinitionProperty(fdef_name = "define_west_fibcoup_taper_lengths")


    east_taper_lengths = DefinitionProperty(fdef_name = "define_east_taper_lengths")
    east_wg_widths = DefinitionProperty(fdef_name = "define_east_wg_widths")
    east_trench_widths = DefinitionProperty(fdef_name = "define_east_trench_widths")
    east_connect_lengths = DefinitionProperty(fdef_name = "define_east_connect_lengths")
    east_bend_radiuses = DefinitionProperty(fdef_name = "define_east_bend_radiuses")
    east_minimum_straights = DefinitionProperty(fdef_name = "define_east_minimum_straights")
    east_fibcoups = DefinitionProperty(fdef_name = "define_east_fibcoups")
    east_fibcoup_offsets = DefinitionProperty(fdef_name = "define_east_fibcoup_offsets")
    east_fibcoup_taper_lengths = DefinitionProperty(fdef_name = "define_east_fibcoup_taper_lengths")


    def define_name(self):
        return "%s_%d_%d_%s_%d_H%d" % (self.__name_prefix__,
                                       do_hash(self.west_fibcoup), do_hash(self.east_fibcoup),
                                       self.struct.name,
                                       do_hash(str((str(self.offset) + str(self.y_spacing) + str(self.south_west) + str(self.south_east)))),
                                       self.west_bend_radius + self.east_bend_radius + self.west_connect_length + self.east_connect_length +
                                       self.west_fibcoup_offset + self.east_fibcoup_offset + self.west_fibcoup_taper_length + self.east_fibcoup_taper_length+
                                       self.west_minimum_straight + self.east_minimum_straight + self.west_taper_length + self.east_taper_length +
                                       self.west_trench_width + self.east_trench_width + self.west_wg_width + self.east_wg_width
                                       )

    def define_west_taper_lengths(self):
        return [self.west_taper_length]

    def define_west_wg_widths(self):
        return [self.west_wg_width]

    def define_west_trench_widths(self):
        return [self.west_trench_width]

    def define_west_connect_lengths(self):
        return [self.west_connect_length]

    def define_west_bend_radiuses(self):
        return [self.west_bend_radius]

    def define_west_minimum_straights(self):
        return [self.west_minimum_straight]

    def define_west_fibcoups(self):
        return [self.west_fibcoup]

    def define_west_fibcoup_offsets(self):
        return [self.west_fibcoup_offset]


    def define_west_fibcoup_taper_lengths(self):
        return [self.west_fibcoup_taper_length]

    def define_east_taper_lengths(self):
        return [self.east_taper_length]

    def define_east_wg_widths(self):
        return [self.east_wg_width]

    def define_east_trench_widths(self):
        return [self.east_trench_width]

    def define_east_connect_lengths(self):
        return [self.east_connect_length]

    def define_east_bend_radiuses(self):
        return [self.east_bend_radius]

    def define_east_minimum_straights(self):
        return [self.east_minimum_straight]

    def define_east_fibcoups(self):
        return [self.east_fibcoup]

    def define_east_fibcoup_offsets(self):
        return [self.east_fibcoup_offset]

    def define_east_fibcoup_taper_lengths(self):
        return [self.east_fibcoup_taper_length]




class IoFibcoup(IoFibcoupAsymmetric):
    """ adapter for grating fiber couplers """
    __name_prefix__ = "IoFibcoup"
    taper_length = PositiveNumberProperty(default = 300.0)
    wg_width = PositiveNumberProperty(default = 3.0)
    trench_width = PositiveNumberProperty(default = TECH.WG.TRENCH_WIDTH)
    connect_length = PositiveNumberProperty(default = 40.0)
    bend_radius = PositiveNumberProperty(default = TECH.WG.BEND_RADIUS)
    minimum_straight = PositiveNumberProperty(default = TECH.WG.SHORT_STRAIGHT)
    fibcoup = StructureProperty(default = TECH.IO.FIBCOUP.DEFAULT_GRATING)
    fibcoup_offset = NumberProperty(default = 25.6)
    fibcoup_taper_length = PositiveNumberProperty(default = 350.0)
    merged_waveguides = BoolProperty(default = True)

    west_taper_length = DefinitionProperty(fdef_name = "define_west_taper_length")
    west_wg_width = DefinitionProperty(fdef_name = "define_west_wg_width")
    west_trench_width = DefinitionProperty(fdef_name = "define_west_trench_width")
    west_connect_length = DefinitionProperty(fdef_name = "define_west_connect_length")
    west_bend_radius = DefinitionProperty(fdef_name = "define_west_bend_radius")
    west_minimum_straight = DefinitionProperty(fdef_name = "define_west_minimum_straight")
    west_fibcoup = DefinitionProperty(fdef_name = "define_west_fibcoup")
    west_fibcoup_offset = DefinitionProperty(fdef_name = "define_west_fibcoup_offset")
    west_fibcoup_taper_length = DefinitionProperty(fdef_name = "define_west_fibcoup_taper_length")
    west_merged_waveguides = DefinitionProperty(fdef_name = "define_west_merged_waveguides")

    east_taper_length = DefinitionProperty(fdef_name = "define_east_taper_length")
    east_wg_width = DefinitionProperty(fdef_name = "define_east_wg_width")
    east_trench_width = DefinitionProperty(fdef_name = "define_east_trench_width")
    east_connect_length = DefinitionProperty(fdef_name = "define_east_connect_length")
    east_bend_radius = DefinitionProperty(fdef_name = "define_east_bend_radius")
    east_minimum_straight = DefinitionProperty(fdef_name = "define_east_minimum_straight")
    east_fibcoup = DefinitionProperty(fdef_name = "define_east_fibcoup")
    east_fibcoup_offset = DefinitionProperty(fdef_name = "define_east_fibcoup_offset")
    east_fibcoup_taper_length = DefinitionProperty(fdef_name = "define_east_fibcoup_taper_length")
    east_merged_waveguides = DefinitionProperty(fdef_name = "define_east_merged_waveguides")


    def define_name(self):
        return "%s_%s_%s_%d_H%d" %(self.__name_prefix__,
                                   self.fibcoup.name,
                                   self.struct.name,
                                   do_hash(str((str(self.offset) + str(self.y_spacing) + str(self.south_west) + str(self.south_east)))),
                                   self.bend_radius + self.connect_length + 
                                   self.fibcoup_offset + self.fibcoup_taper_length +
                                   self.minimum_straight + self.taper_length +
                                   self.trench_width + self.wg_width 
                                   )

    def define_west_taper_length(self):
        return self.taper_length

    def define_west_wg_width(self):
        return self.wg_width

    def define_west_trench_width(self):
        return self.trench_width

    def define_west_connect_length(self):
        return self.connect_length

    def define_west_bend_radius(self):
        return self.bend_radius

    def define_west_minimum_straight(self):
        return self.minimum_straight

    def define_west_fibcoup(self):
        return self.fibcoup

    def define_west_fibcoup_offset(self):
        return self.fibcoup_offset

    def define_west_fibcoup_taper_length(self):
        return self.fibcoup_taper_length

    def define_west_merged_waveguides(self):
        return self.merged_waveguides

    def define_east_taper_length(self):
        return self.taper_length

    def define_east_wg_width(self):
        return self.wg_width

    def define_east_trench_width(self):
        return self.trench_width

    def define_east_connect_length(self):
        return self.connect_length

    def define_east_bend_radius(self):
        return self.bend_radius

    def define_east_minimum_straight(self):
        return self.minimum_straight

    def define_east_fibcoup(self):
        return self.fibcoup

    def define_east_fibcoup_offset(self):
        return self.fibcoup_offset

    def define_east_fibcoup_taper_length(self):
        return self.fibcoup_taper_length

    def define_east_merged_waveguides(self):
        return self.merged_waveguides

