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

from .geometry import CartesianGeometry1D, CartesianGeometry2D, CartesianGeometry3D
from ipcore.all import *
from ipkiss.all import SizeInfo
from ipkiss.all import Coord3

__all__ = ["MaterialStackGeometry1D",
           "MaterialStackGeometry2D",
           "material_stack_to_geometry",
           ]

class MaterialStackGeometry1D(CartesianGeometry1D):  
    """ A 1-D geometry class describing a material distribution in 1D as a stack of materials """
    
    materials_thicknesses = ListProperty(required = True, doc="A list with (material, thickness) tuples")
    origin_z = NumberProperty(default = 0.0, doc = "Bottom of the first layer")
    size_info = LockedProperty()
    thickness = LockedProperty()
    
    def get_material(self, coordinate):
        # slow
        if isinstance(coordinate, (Coord3, tuple)):
            c = coordinate[2] # z-component
        else: 
            c = coordinate # scalar
        if c < self.origin_z or c > self.origin_z + self.thickness:
            raise AttributeError("coordinate %f is outside the Geometry: cannot retreive material" % c)
        
        z = self.origin_z
        for m, t in self.materials_thicknesses:
            z += t
            if c < z: 
                break
        return m
        
    def define_size_info(self):
        return SizeInfo(east = 0.0, west = 0.0, 
                        north = self.origin_z + self.thickness, 
                        south = self.origin_z)
    
    def define_thickness(self):
        z = 0.0
        for m,h in self.materials_thicknesses:
            z = z + h
        return z
    
    def get_number_of_layers(self):
        return len(self.materials_thicknesses)

    def get_solid_thickness(self):
        """ returns the length of the stack from bottom to top until the forst non-solid material is encountered 
        """
        th = 0
        for m, h in self.materials_thicknesses:
            if m.solid:
                th += h
            else:
                break
        return  th
    
    def __add__(self, other):
        if not isinstance(other, MaterialStackGeometry1D):
            raise Exception("Cannot add %s to an object of type MaterialStackGeometry1D.")        
        result_materials_thicknesses = []           
        result_materials_thicknesses.extend(self.materials_thicknesses)
        if (not result_materials_thicknesses[-1][0].solid) and len(other.materials_thicknesses)>0:
            result_materials_thicknesses[-1] = (other.materials_thicknesses[0][0], result_materials_thicknesses[-1][1] + other.materials_thicknesses[0][1])
            result_materials_thicknesses.extend(other.materials_thicknesses[1:])      
        else:
            result_materials_thicknesses.extend(other.materials_thicknesses)      
        result_display_style = self.display_style.blend(other.display_style)
        result_ms = MaterialStack(materials_thicknesses = result_materials_thicknesses,
                                  display_style = result_display_style,
                                  name = self.name + " + " + other.name)
        return result_ms
    
    def __repr__(self):
        return "<MaterialStackGeometry1D %s>" % self.name
    
    def __hash__(self):
        return hash("".join(["%s_%d" % (m.name, round(d*100000)) for m,d in self.materials_thicknesses]))
            

    def consolidate(self):
        """ join all adjacent layers of identical materials together """
        
        last_material = self.materials_thicknesses[0][0]
        last_thickness = self.materials_thicknesses[0][1]
        mh = []
        for m, h in self.materials_thicknesses[1:]:
            if m == last_material:
                last_thickness += h
            else:
                mh += [(last_material, last_thickness)]
                last_material = m
                last_thickness = h
        mh += [(last_material, last_thickness)]
        
        
        self.materials_thicknesses = mh
        return self
    
    
    def consolidate_copy(self):
        """ generates a copy where all adjacent layers of identical materials are joined """
        
        ms = self.__class__(name = self.name,
                            materials_thicknesses = self.materials_thicknesses,
                            #display_style = self.display_style
                            )
        ms.consolidate()
        return ms

class MaterialStackGeometry2D(CartesianGeometry2D):  
    """ A 2-D geometry class describing a material distribution in 2D as a stack of MaterialStackGeometry1D objects"""
    
    stacks_widths= ListProperty(required = True, doc="A list with (material_stack, width) tuples")
    origin_x = NumberProperty(default = 0.0, doc = "Left side of the leftmost stack")
    size_info = LockedProperty()
    
    def get_material_stack(self, coordinate):
        # slow
        if not isinstance(coordinate, (Coord3, tuple)):
            raise AttributeError("coordinate should be a Coord3 object or tuple to retreive material from geometry")
        cx, cz = coordinate[0], coordinate[2]
        if cx < self.origin_x or cx > self.origin_x + self.width:
            raise AttributeError("coordinate %f is outside the Geometry: cannot retreive material" % c)
        
        x = self.origin_x
        for s, w in self.stacks_widths:
            x += w
            if cx < x: 
                break
        return s

    def get_material(self, coordinate):
        # slow
        m = self.get_material_stack(coordinate)
        return m

    def size_info(self):
        return SizeInfo(west = self.origin_x, 
                        east = self.origin_x + self.width,
                        south = min([m.origin_z for m,h in self.stacks_widths]),
                        north = max([m.origin_z + m.thickness for m,h in self.stacks_widths])
                        )
                        
                        
    
    def define_width(self):
        x = 0.0
        for m,t in self.stacks_widths:
            x = x + t
        return x

    def define_thickness(self):
        z = 0.0
        return max([m.thickness for m,h in self.stacks_widths])
    
    
    def get_number_of_stacks(self):
        return len(self.stacks_widths)

    def __repr__(self):
        return "<MaterialStackGeometry2D %s>" % self.name
    
    def __hash__(self):
        return hash("".join(["%s_%d" % (m.name, round(d*100000)) for m,d in self.stacks_widths]))
            

    def consolidate(self):
        """ join all adjacent layers of identical material_stacks together """
        
        last_stack = self.stack_widths[0][0]
        last_width = self.stack_widths[0][1]
        mh = []
        for m, h in self.staqck_widths[1:]:
            if m == last_stack:
                last_width += h
            else:
                mh += [(last_stack, last_width)]
                last_stack = m
                last_width = h
        mh += [(last_stack, last_width)]
        
        
        self.stack_widths = mh
        return self
    
    
    def consolidate_copy(self):
        """ generates a copy where all adjacent layers of identical materials are joined """
        
        ms = self.__class__(name = self.name,
                            stack_widths = self.stacks_widths,
                            #display_style = self.display_style
                            )
        ms.consolidate()
        return ms

from ..material.material import Material    
    
class MaterialStackGeometry3D(CartesianGeometry3D):  
    """ A 3-D geometry class describing a material distribution as a set of 2-D shapes with a MaterialStackGeometry1D in the third direction"""
    background_material = RestrictedProperty(required = True, restriction = RestrictType(Material))
    background_stack = RestrictedProperty(required = True, restriction = RestrictType(MaterialStackGeometry1D))
    shapes_stacks= ListProperty(required = True, doc="A list with (shape, material_stack) tuples")
    size_info = LockedProperty()
    
    def get_material_stack(self, coordinate):
        """ retrieves the material stack at a given coordinate """
        # reverse iteration
        c = (coordinate[0], coordinate[1])
        for s, m in self.shapes_stacks:
            if s.encloses(c, True):
                return m
        return self.background_stack
    
    def get_material(self, coordinate):
        """ retrieves the material at a given coordinate """
        # slow
        if not isinstance(coordinate, (Coord3, tuple)):
            raise AttributeError("coordinate should be a Coord3 object or tuple to retreive material from geometry")
        #cx, cz = coordinate[0], coordinate[2]
        #if cx < self.origin_x or cx > self.origin_x + self.width:
            #raise AttributeError("coordinate %f is outside the Geometry: cannot retreive material" % c)
        
        # reverse iteration
        m = self.get_material_stack(coordinate)
        if cz >= m.origin_z and cz <= m.origin_z + m.thickness:
            return m.get_material(cz)
        else:
            return self.background_material

    def size_info(self):
        return SizeInfo(west = self.origin_x, 
                        east = self.origin_x + self.width,
                        south = min([m.origin_z for m,h in self.stacks_widths]),
                        north = max([m.origin_z + m.thickness for m,h in self.stacks_widths])
                        )
                        
                        
    
    def define_width(self):
        x = 0.0
        for m,t in self.stacks_widths:
            x = x + t
        return x

    def define_thickness(self):
        z = 0.0
        return max([m.thickness for m,h in self.shapes_stacks])
    
    
    def get_number_of_stacks(self):
        return len(self.shapes_stacks)

    def __repr__(self):
        return "<MaterialStackGeometry3D %s>" % self.name
    
    def __hash__(self):
        return hash("".join(["%s_%d" % (m.name, s.id_string()) for s, m in self.shapes_stacks]))
            

    #def consolidate(self):
        #""" join all adjacent layers of identical material_stacks together """
        
        #last_stack = self.stack_widths[0][0]
        #last_width = self.stack_widths[0][1]
        #mh = []
        #for m, h in self.staqck_widths[1:]:
            #if m == last_stack:
                #last_width += h
            #else:
                #mh += [(last_stack, last_width)]
                #last_stack = m
                #last_width = h
        #mh += [(last_stack, last_width)]
        
        
        #self.stack_widths = mh
        #return self
    
    
    #def consolidate_copy(self):
        #""" generates a copy where all adjacent layers of identical materials are joined """
        
        #ms = self.__class__(name = self.name,
                            #stack_widths = self.stacks_widths,
                            ##display_style = self.display_style
                            #)
        #ms.consolidate()
        #return ms

    
    
########################################################################
# convert old MaterialStack objects to new Geometries and vice versa
########################################################################

def material_stack_to_geometry(ms):
    return MaterialStackGeometry1D(name = ms.name,
                                   materials_thicknesses = ms.materials_heights
                                   )

def geometry_to_material_stack(ms):
    from ..material.material_stack import MaterialStack
    return MaterialStack(name = ms.name,
                         materials_heights = ms.materials_thicknesses
                        )

