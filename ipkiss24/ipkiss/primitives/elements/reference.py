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



from ...geometry.transforms.translation import Translation
from ...geometry.coord import Coord2, Coord2Property
from ...geometry import shape
from ...geometry import shape_info
from .basic import __Element__, ElementList
from .group import Group
from .. import structure as structure_module
from ... import constants
from ... import settings
from ipcore.properties.descriptor import RestrictedProperty, DefinitionProperty, FunctionNameProperty
from ipcore.properties.predefined import RESTRICT_INT_TUPLE2, RESTRICT_POSITIVE, RESTRICT_NONZERO, IntProperty, NumberProperty
from ipcore.properties.initializer import SUPPRESSED
from types import NoneType
from copy import copy, deepcopy
from numpy import transpose, reshape, meshgrid, array
from ipkiss.log import IPKISS_LOG as LOG
from ipcore.mixin.mixin import MixinBowl


__all__ = ["ARef",
           "CompoundArefElement",
           "__RefElement__",
           "MRef",
           "SoftRotationARef",
           "SoftARef",
           "SRef",
           "StackARef"]

##########################################################
# Basic Reference __Element__
##########################################################

class __RefElement__(__Element__):
    reference = structure_module.StructureProperty(required = True)
    def __init__(self,
                 reference,
                 transformation = None,
                 **kwargs):
        super(__RefElement__, self).__init__(reference = reference, transformation = transformation, **kwargs)


    def dependencies(self):
        d = structure_module.StructureList()
        d.add(self.reference)
        d.add(self.reference.dependencies())
        return d

    def expand_transform(self):
        if not self.transformation.is_identity():
            S = structure_module.Structure(self.reference.name + self.transformation.id_string(),
                              deepcopy(self.reference.elements)
                              )
            self.reference = S
            S.transform(self.transformation)
            self.transformation = None

    def is_empty(self):
        if self.reference is None:
            return True
        else:
            return self.reference.is_empty()
        
    def __repr__(self):
        return "<Ref of %s>" % self.reference.name
    

class MRef(__RefElement__):
    positions = RestrictedProperty(default = [(0.0, 0.0)])
    
    def __init__(self,
                 reference,
                 positions, 
                 transformation= None,
                 **kwargs):
        super(MRef, self).__init__(reference = reference, transformation = transformation, positions = positions, **kwargs)


    def move(self, position):
        self.positions = [Coord2(p[0] + position[0], p[1] + position[1]) for p in self.positions]

    def size_info(self):
        S = self.reference.size_info().transform(self.transformation)
        S2 = SizeInfo()
        for p in self.positions: S2 += S.move_copy(p)
        return S2

    def convex_hull(self):
        S = self.reference.convex_hull().transform(self.transformation)
        S2 = Shape()
        for p in self.positions: S2 += S.move_copy(p)
        return S2.convex_hull()
    
    
    def __untransformed_positions__(self):
        p = shape.Shape(self.positions)
        return p

    def __positions__(self):
        return self.__untransformed_positions__()

    def __deepcopy__(self, memo):#cannot be removed ! self.reference should not be deepcopied !
        return MRef(self.reference, deepcopy(self.positions), deepcopy(self.transformation))
    
    def flat_copy(self, level = -1):
        if level == 0: return ElementList(self.__copy__())
        el = self.reference.elements.flat_copy(level-1) 
        el_tot = ElementList()
        T = self.transformation 
        for p in self.__positions__():
            T2 = T + Translation(p)  
            el_tot += el.transform_copy(T2)
        return el_tot


    def is_empty(self):
        return __RefElement__.is_empty(self) or (len(self.positions) == 0)

    def __repr__(self):
        return "<MRef of %s>" % self.reference.name


class __AutoRefPositions__(object):
    positions = FunctionNameProperty("__positions__")
    def __init__(self, **kwargs):
        super(__AutoRefPositions__, self).__init__(positions = SUPPRESSED, **kwargs)
    
class SRef(__AutoRefPositions__, MRef, MixinBowl):
    position = Coord2Property(default = (0.0, 0.0))
    
    def __init__(self, reference,position = (0.0, 0.0), transformation = None, **kwargs):
        if isinstance(reference, SRef):
            from ipkiss.primitives.structure import Structure
            reference = Structure(elements=[reference], ports = reference.ports)            
        super(SRef, self).__init__(reference = reference, position = position, transformation = transformation, **kwargs)
        
    def size_info(self):
        ref_size_info = self.reference.size_info()
        return ref_size_info.transform(self.transformation + Translation(self.position))

    def convex_hull(self):
        return self.reference.convex_hull().transform(self.transformation + Translation(self.position))

    def __untransformed_positions__(self):
        return [self.position]

    def move(self, position):
        self.position = Coord2(self.position[0] + position[0], self.position[1] + position[1])

        
    def __deepcopy__(self, memo):#cannot be removed ! self.reference should not be deepcopied !
        return SRef(self.reference, deepcopy(self.position), deepcopy(self.transformation))
        
    def flat_copy(self, level = -1):
        if level == 0: return ElementList(self.__copy__())
        el = self.reference.elements.flat_copy(level-1)
        el.transform(self.transformation + Translation(self.position))
        return el
    
    def __repr__(self):
        return "<SRef of %s>" % self.reference.name
    
    def __eq__(self, other):
        if not isinstance(other, SRef):
            return False
        return (self.reference == other.reference) and (self.position == other.position) and (self.transformation == other.transformation)
    
    def __ne__(self,other):
        return not self.__eq__(other)    
    
   
    
class ARef(__AutoRefPositions__, MRef, MixinBowl):
    origin = Coord2Property(default = (0.0, 0.0))
    period = Coord2Property(required = True)
    n_o_periods = RestrictedProperty(restriction = RESTRICT_INT_TUPLE2, required = True)
    
    def __init__(self,
                 reference,
                 origin,
                 period ,
                 n_o_periods,
                 transformation= None,
                 **kwargs):
        super(ARef, self).__init__(reference = reference, transformation = transformation, origin = origin, period = period, n_o_periods = n_o_periods, **kwargs)
              
        
    def move(self, position):
        self.origin = (self.origin[0] + position[0], self.origin[1] + position[1])

    def size_info(self):
        S = self.reference.size_info()
        S2 = (S
              + S.move_copy(((self.n_o_periods[0] - 1) * self.period[0], (self.n_o_periods[1] - 1) * self.period[1]))
              )
        return S2.transform(self.transformation + Translation(self.origin))

    def convex_hull(self):
        S = self.reference.convex_hull()
        S2 = (S
              + S.move_copy(((self.n_o_periods[0] - 1) * self.period[0], (self.n_o_periods[1] - 1) * self.period[1]))
              )
        return S2.convex_hull().transform(self.transformation + Translation(self.origin))

    def __untransformed_positions__(self):
        p = shape.Shape(transpose(reshape(meshgrid(range(self.n_o_periods[0]), range(self.n_o_periods[1])),(2, self.n_o_periods[0]* self.n_o_periods[1]))) * array([self.period[0], self.period[1]]))
        return p

    def __positions__(self):
        p = self.__untransformed_positions__()
        return p.transform(self.transformation + Translation(self.origin))

    
    def __deepcopy__(self, memo):#cannot be removed ! self.reference should not be deepcopied !
        return ARef(self.reference, deepcopy(self.origin), deepcopy(self.period), deepcopy(self.n_o_periods), deepcopy(self.transformation))
        
        
    def flat_copy(self, level = -1):
        if level == 0: return ElementList(self.__copy__())
        el = self.reference.elements.flat_copy(level-1) 
        el_tot = ElementList()
        T = self.transformation - Translation(self.transformation.translation)
        for p in self.__positions__():
            T2 = T + Translation(p)  
            el_tot += el.transform_copy(T2)
        return el_tot
    

    def is_empty(self):
        return __RefElement__.is_empty(self) or (self.n_o_periods[0] == 0) or (self.n_o_periods[1] ==0)
    
    def __repr__(self):
        return "<ARef of %s>" % self.reference.name
    
    def __eq__(self, other):
        if not isinstance(other, ARef):
            return False
        return (self.reference == other.reference) and (self.transformation == other.transformation) and (self.origin == other.origin) and (self.period  == other.period) and (self.n_o_periods == other.n_o_periods)
    
    def __ne__(self,other):
        return not self.__eq__(other)    
    



class __ARef1dElement__(ARef):
    period = DefinitionProperty(fdef_name= "define_period")
    n_o_periods = DefinitionProperty(fdef_name= "define_n_o_periods")

    period_1d = NumberProperty(default = 1.0, restriction = RESTRICT_NONZERO)
    n_o_periods_1d = IntProperty(default = 1, restriction = RESTRICT_POSITIVE)


    def __init__(self,
                 reference,
                 origin,
                 period_1d,
                 n_o_periods_1d,
                 transformation= None,
                 **kwargs):
        kwargs["period"] = SUPPRESSED
        kwargs["n_o_periods"] = SUPPRESSED        
        super(__ARef1dElement__, self).__init__(reference = reference,
                                                        origin = origin,
                                                        period_1d = period_1d,
                                                        n_o_periods_1d = n_o_periods_1d,
                                                        transformation = transformation,
                                                        **kwargs)

    def is_empty(self):
        return __RefElement__.is_empty(self) or (self.n_o_periods_1d ==0) 
        
        

class ARefX(__ARef1dElement__):

    def define_period(self):
        p = (self.period_1d, 1.0)
        return p

    def define_n_o_periods(self):
        nop = (self.n_o_periods_1d, 1)
        return nop    
    
    def __deepcopy__(self, memo): #cannot be removed ! self.reference should not be deepcopied !
        return ARefX(self.reference, deepcopy(self.origin), deepcopy(self.period_1d), deepcopy(self.n_o_periods_1d), deepcopy(self.transformation))        
        
class ARefY(__ARef1dElement__):
    
    def define_period(self):
        p = (1.0, self.period_1d)
        return p

    def define_n_o_periods(self):
        nop = (1, self.n_o_periods_1d)
        return nop    
        
    
    def __deepcopy__(self, memo):#cannot be removed ! self.reference should not be deepcopied !
        return ARefY(self.reference, deepcopy(self.origin), deepcopy(self.period_1d), deepcopy(self.n_o_periods_1d), deepcopy(self.transformation))
        
        
class CompoundArefElement(Group, ARef):
    def __init__(self,
                 reference,
                 origin,
                 period ,
                 n_o_periods,
                 transformation= None,
                 **kwargs):
        super(CompoundArefElement, self).__init__(reference = reference,
                                                        origin = origin,
                                                        period = period,
                                                        n_o_periods = n_o_periods,
                                                        transformation = transformation,
                                                        **kwargs)

    def flat_copy(self, level = -1):
        return ARef.flat_copy(self, level)

    def is_empty(self):
        return ARef.is_empty(self)

    def __deepcopy__(self, memo):#cannot be removed ! self.reference should not be deepcopied !
        return CompoundARef(self.reference, deepcopy(self.origin), deepcopy(self.period), deepcopy(self.n_o_periods), deepcopy(self.transformation))

    
class SoftARef(CompoundArefElement):

    def define_elements(self, elems):
        if not self.reference.is_empty():
            P = self.__untransformed_positions__().translate(self.origin)
            
            T = self.transformation + Translation(self.origin) - self.transformation - Translation(self.origin) 
            for pos in P:
                elems.append(SRef(self.reference, pos, T))
        return elems

    def size_info(self):
        return ARef.size_info(self)

    def convex_hull(self):
        return ARef.convex_hull(self)

    def __deepcopy__(self, memo):#cannot be removed ! self.reference should not be deepcopied !
        return SoftARef(self.reference, deepcopy(self.origin), deepcopy(self.period), deepcopy(self.n_o_periods), deepcopy(self.transformation))
    

class SoftRotationARef(CompoundArefElement):

    def define_elements(self, elems):
        if not self.reference.is_empty():
            if self.transformation.rotation == 0.0:
                period = self.transformation.apply_to_coord(self.period)
                elems.append(ARef(self.reference, self.origin, period, self.n_o_periods, self.transformation))
            elif (self.transformation.rotation % 360.0) == 90.0:
                transform = deepcopy(self.transformation)
                transform.rotation = 0.0
                period = transform.apply_to_coord(self.period)
                period = (period[1], period[0])
                n_o_periods = (self.n_o_periods[1], self.n_o_periods[0])
                zero = (self.origin[0] - (n_o_periods[0] - 1) * period[0], self.origin[1])
                elems.append(ARef(self.reference, zero, period, n_o_periods, transform))
            elif (self.transformation.rotation%360.0) == 270.0:
                transform = deepcopy(self.transformation)
                transform.rotation = 0.0
                period = transform.apply_to_coord(self.period)
                period = (period[1], period[0])
                n_o_periods = (self.n_o_periods[1], self.n_o_periods[0])
                zero = (self.origin[0] , self.origin[1] - (n_o_periods[1] - 1) * period[1])
                elems.append(ARef(self.reference, zero, period, n_o_periods, transform))
            else:
                elems.append(SoftARef(self.reference, self.origin, period, self.n_o_periods, self.transformation))
        return elems

    def __deepcopy__(self, memo):#cannot be removed ! self.reference should not be deepcopied !
        return SoftRotationARef(self.reference, deepcopy(self.origin), deepcopy(self.period), deepcopy(self.n_o_periods), deepcopy(self.transformation))
    
    
    def size_info(self):
        return ARef.size_info(self)

    def convex_hull(self):
        return ARef.convex_hull(self)



class StackARef(CompoundArefElement):
    stack_size = IntProperty(restriction = RESTRICT_POSITIVE, default = 20)
    
    def __init__(self,
                 reference,
                 origin = (0.0,0.0),
                 period = (1.0, 1.0) ,
                 n_o_periods = (1,1),
                 transformation= None,
                 stack_size = 20,
                 **kwargs):
        super(StackARef, self).__init__(reference = reference, 
                                                     origin = origin, 
                                                     period = period, 
                                                     n_o_periods = n_o_periods, 
                                                     transformation = transformation, 
                                                     stack_size = stack_size, 
                                                     **kwargs)

    def define_elements(self, elems):
        # X_periodicity: 1
        if self.n_o_periods[0] == 1:
            # do not create X-cell, but use self.reference for Y-periodicity
            x_cell = self.reference
            x_cell_content = SRef(self.reference, (0.0, 0.0))
        # X-periodicity: smaller than 2 * stack size:
        elif self.n_o_periods[0] < 2 * self.stack_size:
            # use soft_aref
            x_cell_content = SoftARef(self.reference, (0.0, 0.0), self.period, (self.n_o_periods, 1))
        # X-periodicity: larger than 2 * stack size
        else:
            # should become autoname structure
            x_cell_stack = structure_module.Structure("R_" + self.reference.name + "_SX" + str(int(self.stack_size)),
                                   SoftARef(self.reference, (0.0, 0.0), self.period, (self.stack_size, 1)))
            x_cell_content  = SoftARef(x_cell_stack, (0.0, 0.0), (self.period[0] * self.stack_size, self.period[1]), (self.n_o_periods[0] / self.stack_size, 1))
            x_cell_content += SoftARef(self.reference, (self.period[0] * self.stack_size * (self.n_o_periods[0] / self.stack_size), 0.0), self.period, (self.n_o_periods[0] % self.stack_size, 1))
            
        # do not yet create the X-cell

        # Y-periodicity: 1
        if self.n_o_periods[1] == 1:
            x_cell_content.move(self.origin)
            # transformation is passed automatically through the compound_element transformation
            elems += x_cell_content
            # do not create X-cell, but add the previously defined content to self, return
            return

        # create x_cell
        # this should become an autoname_structure
        x_cell = structure_module.Structure("R_" + self.reference + "_X" + str(int(n_o_periods[0])),
                               x_cell_content)
        
        if self.n_o_periods[1] < 2 * self.stack_size:
            # soft_aref of X_cell
            elems += SoftARef(x_cell, self.origin, self.period,(1, self.n_o_periods[1]))
        else: # Y_periodicity < 2* stack_size:
            y_cell_stack = structure_module.Structure("R_" + x_cell.name + "_SY" + str(int(self.stack_size)),
                                         SoftARef(x_cell, (0.0, 0.0), (self.period[0], self.stack_size * self.period[1]), (1, self.n_o_periods[1] / self.stack_size)))
            elems += SoftARef(y_cell_stack, self.origin, (self.period[0], self.stack_size * self.period[1]), (1, self.n_o_periods[1] / self.stack_size))
            elems += SoftARef(x_cell, (self.origin[0], self.origin[1] + self.period[1] * self.stack_size * (self.n_o_periods[1] / self.stack_size)), self.period, (1, self.n_o_periods[1] % self.stack_size))
        return elems
            
    def size_info(self):
        return ARef.size_info(self)

    
    def convex_hull(self):
        return ARef.convex_hull(self)

    def __deepcopy__(self, memo):#cannot be removed ! self.reference should not be deepcopied !
        return StackARef(self.reference, deepcopy(self.origin), deepcopy(self.period), deepcopy(self.n_o_periods), deepcopy(self.transformation))

       


