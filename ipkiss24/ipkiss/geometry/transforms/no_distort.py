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

from ..transform import GenericNoDistortTransform, __ReversibleTransform__
from ..coord import Coord2, Coord2Property, Coord3
from ipcore.properties.descriptor import SetFunctionProperty
from ipcore.properties.predefined import NumberProperty, BoolProperty, RESTRICT_NONZERO

import numpy
from math import cos, sin, tan
from ... constants import DEG2RAD, RAD2DEG
import copy

__all__ = ["NoDistortTransform"]

class NoDistortTransform(GenericNoDistortTransform):
    """ A homothetic transformation that does not distort the item it is applied to (angle conservation) 
        The transform is defined by 
        - a mirror around the x-axis
        - a scaling with respect to the origin
        - a rotation around the origin
        - a translation
        
        it is also possible to set absolute magnification and rotation, which means that subsequent transformations
        will not affect the angle and size any further
        """
    # FIXME : Use transformation matrix which is computed once (and cached)
    
    def __init__(self, translation = (0.0, 0.0), rotation = 0.0, magnification = 1.0, v_mirror = False, absolute_magnification = False, absolute_rotation = False, **kwargs):
        # note: translation is no part of gdsII transform. It should be taken into account while writing the file
        super(NoDistortTransform, self).__init__(
            translation = translation,
            rotation = rotation,
            magnification = magnification,
            v_mirror = v_mirror,
            absolute_magnification = absolute_magnification,
            absolute_rotation =absolute_rotation,
            **kwargs)

    translation = Coord2Property("__translation__", default = (0.0, 0.0))
    """ the translation coordinate """
    
   
    #def get_rotation (self): return self.rotation
    def set_rotation(self, value):
        self.__rotation__ = value % 360.0
        if value % 90.0 == 0.0:
            # make sure sine and cosine are really zero when needed!
            if self.__rotation__ == 0.0:
                self.__ca__ = 1.0
                self.__sa__ = 0.0
            elif self.__rotation__ == 90.0:
                self.__ca__ = 0.0
                self.__sa__ = 1.0
            elif self.__rotation__ == 180.0:
                self.__ca__ = -1.0
                self.__sa__ = 0.0
            elif self.__rotation__ == 270.0:
                self.__ca__ = 0.0
                self.__sa__ = -1.0
        else:
            self.__ca__ = cos(value * DEG2RAD)
            self.__sa__ = sin(value * DEG2RAD)
    rotation = SetFunctionProperty("__rotation__", set_rotation, default=0.0)
    """ the rotation around the origin """

    magnification = NumberProperty("__magnification__", restriction = RESTRICT_NONZERO, default = 1.0)
    """ the magnification factor """

    v_mirror = BoolProperty("__v_mirror__", default = False)
    """ the vertical mirror """
    flip = v_mirror
    

    #""" set absolute magnification on or off"""
    absolute_magnification = BoolProperty("__absolute_magnification__", default = False)
    
    #""" set absolute rotation on or off"""
    absolute_rotation = BoolProperty("__absolute_rotation__", default = False)
    
    def __make_simple__(self):
        """ internal use: reduces special subclasses to this generic type """
        # if you change special types, they should revert to generic type
        self.__class__ = NoDistortTransform

    def __translate__(self, coord):
        """ internal use: applies translation to a coordinate """
        return Coord2(coord[0] + self.translation.x, coord[1] + self.translation.y)
    
    def __rotate__(self, coord):
        """ internal use: applies rotation to a coordinate """
        return Coord2(coord[0] * self.__ca__ - coord[1] * self.__sa__, coord[0] * self.__sa__ + coord[1] * self.__ca__)

    def __magnify__(self, coord):
        """ internal use: applies magnification to a coordinate """
        return Coord2(coord[0] * self.magnification, coord[1] * self.magnification)

    def __v_flip__(self, coord):
        """ internal use: applies v_mirror to a coordinate """
        if self.v_mirror:
            return Coord2(coord[0], -coord[1])
        else:
            return Coord2(coord[0], coord[1])

    def __inv_translate__(self, coord):
        """ internal use: applies reverse translation to a coordinate """
        return Coord2(coord[0] - self.translation.x, coord[1] - self.translation.y)
    
    def __inv_rotate__(self, coord):
        """ internal use: applies reverse rotation to a coordinate """
        return Coord2(coord[0] * self.__ca__ + coord[1] * self.__sa__, - coord[0] * self.__sa__ + coord[1] * self.__ca__)

    def __inv_magnify__(self, coord):
        """ internal use: applies reverse magnification to a coordinate """
        return Coord2(coord[0] / self.magnification, coord[1] / self.magnification)

    def __inv_v_flip__(self, coord):
        """ internal use: applies reverse v_mirror to a coordinate """
        if self.v_mirror:
            return Coord2(coord[0], - coord[1])
        else:
            return Coord2(coord[0], coord[1])

    def __translate3__(self, coord):
        """ internal use: applies translation to a 3d coordinate """
        return Coord3(coord[0] + self.translation.x, coord[1] + self.translation.y, coord[2])
    
    def __rotate3__(self, coord):
        """ internal use: applies rotation to a 3d coordinate """
        return Coord3(coord[0] * self.__ca__ - coord[1] * self.__sa__, coord[0] * self.__sa__ + coord[1] * self.__ca__, coord[2])

    def __magnify3__(self, coord):
        """ internal use: applies magnification to a 3d coordinate """
        return Coord3(coord[0] * self.magnification, coord[1] * self.magnification, coord[2])

    def __v_flip3__(self, coord):
        """ internal use: applies v_mirror to a 3d coordinate """
        if self.v_mirror:
            return Coord3(coord[0], -coord[1], coord[2])
        else:
            return Coord3(coord[0], coord[1], coord[2])

    def __inv_translate3__(self, coord):
        """ internal use: applies reverse translation to a 3d coordinate """
        return Coord3(coord[0] - self.translation.x, coord[1] - self.translation.y, coord[2])
    
    def __inv_rotate3__(self, coord):
        """ internal use: applies reverse rotation to a 3d coordinate """
        return Coord3(coord[0] * self.__ca__ + coord[1] * self.__sa__, - coord[0] * self.__sa__ + coord[1] * self.__ca__, coord[2])

    def __inv_magnify3__(self, coord):
        """ internal use: applies reverse magnification to a 3d coordinate """
        return Coord3(coord[0] / self.magnification, coord[1] / self.magnification, coord[2])

    def __inv_v_flip3__(self, coord):
        """ internal use: applies reverse v_mirror to a 3d coordinate """
        if self.v_mirror:
            return Coord3(coord[0], - coord[1], coord[2])
        else:
            return Coord3(coord[0], coord[1], coord[2])
        
    def __translate_array__(self, coords):
        """ internal use: applies translation to a numpy array """
        coords += numpy.array([self.translation.x, self.translation.y])
        return coords
    
    def __rotate_array__(self, coords):
        """ internal use: applies rotation to a numpy array """
        x_a = numpy.array([self.__ca__, -self.__sa__])
        y_a = numpy.array([self.__sa__, self.__ca__])
        coords = numpy.transpose(numpy.vstack((numpy.sum(coords * x_a, 1), numpy.sum(coords * y_a, 1))))
        return coords

    def __magnify_array__(self, coords):
        """ internal use: applies magnification to a numpy array """
        coords *= numpy.array([self.magnification, self.magnification])
        return coords

    def __v_flip_array__(self, coords):
        """ internal use: applies v_mirror to a numpy array """
        coords *= (numpy.array([False, self.v_mirror]) * -2.0 + 1.0)
        return coords

    def __inv_translate_array__(self, coords):
        """ internal use: applies reverse translation to a numpy array """
        coords -= numpy.array([self.translation.x, self.translation.y])
        return coords
    
    def __inv_rotate_array__(self, coords):
        """ internal use: applies reverse rotation to a numpy array """
        x_a = array([self.__ca__, self.__sa__])
        y_a = array([-self.__sa__, self.__ca__])
        coords = numpy.transpose(numpy.vstack((numpy.sum(coords * x_a, 1), numpy.sum(coords * y_a, 1))))
        return coords

    def __inv_magnify_array__(self, coords):
        """ internal use: applies reverse magnification to a numpy array """
        coords *= numpy.array([1.0 / self.magnification, 1.0 / self.magnification])
        return coords

    def __inv_v_flip_array__(self, coords):
        """ internal use: applies reverse v_mirror to a numpy array """
        coords *= numpy.array([False, self.v_mirror]) * (-2.0) + 1.0
        return coords

    def __translate_array3__(self, coords):
        """ internal use: applies translation to a numpy array """
        coords += numpy.array([self.translation.x, self.translation.y, 0.0])
        return coords
    
    def __rotate_array3__(self, coords):
        """ internal use: applies rotation to a numpy array """
        x_a = numpy.array([self.__ca__, -self.__sa__, 0])
        y_a = numpy.array([self.__sa__, self.__ca__, 0])
        z_a = numpy.array([0, 0, 1.0])
        
        coords = numpy.transpose(numpy.vstack((numpy.sum(coords * x_a, 1), numpy.sum(coords * y_a, 1), numpy.sum(coords * z_a, 1))))
        return coords

    def __magnify_array3__(self, coords):
        """ internal use: applies magnification to a numpy array """
        coords *= numpy.array([self.magnification, self.magnification, 1.0])
        return coords

    def __v_flip_array3__(self, coords):
        """ internal use: applies v_mirror to a numpy array """
        coords *= (numpy.array([False, self.v_mirror, False]) * -2.0 + 1.0)
        return coords

    def __inv_translate_array3__(self, coords):
        """ internal use: applies reverse translation to a numpy array """
        coords -= numpy.array([self.translation.x, self.translation.y, 0.0])
        return coords
    
    def __inv_rotate_array3__(self, coords):
        """ internal use: applies reverse rotation to a numpy array """
        x_a = array([self.__ca__, self.__sa__, 0.0])
        y_a = array([-self.__sa__, self.__ca__, 0.0])
        z_a = numpy.array([0, 0, 1.0])
        
        coords = numpy.transpose(numpy.vstack((numpy.sum(coords * x_a, 1), numpy.sum(coords * y_a, 1), numpy.sum(coords * z_a, 1))))
        return coords

    def __inv_magnify_array3__(self, coords):
        """ internal use: applies reverse magnification to a numpy array """
        coords *= numpy.array([1.0 / self.magnification, 1.0 / self.magnification, 1.0])
        return coords

    def __inv_v_flip_array3__(self, coords):
        """ internal use: applies reverse v_mirror to a numpy array """
        coords *= numpy.array([False, self.v_mirror, False]) * (-2.0) + 1.0
        return coords

    def apply_to_coord(self, coord):
        """ applies transformation to a coordinate """
        # this could be speeded up
        # Check the east order
        coord = self.__v_flip__(coord)# first flip 
        coord = self.__rotate__(coord)# then magnify
        coord = self.__magnify__(coord)# then rotate
        coord = self.__translate__(coord) # finally translate
        return coord
    
    def reverse_on_coord(self, coord):
        """ applies reverse transformation to a coordinate """
        # this could be speeded up
        # Check the right order
        coord = self.__inv_translate__(coord) # finally translate
        coord = self.__inv_magnify__(coord)# then rotate
        coord = self.__inv_rotate__(coord)# then magtnify
        coord = self.__inv_v_flip__(coord)# first flip 
        return coord

    def apply_to_array(self, coords):
        """ internal use: applies transformation to a numpy array"""
        # this could be speeded up
        # Check the right order
        coords = self.__v_flip_array__(coords)# first flip 
        coords = self.__rotate_array__(coords)# then rotate
        coords = self.__magnify_array__(coords)# then magnify
        coords = self.__translate_array__(coords) # finally translate
        return coords
    
    def reverse_on_array(self, coord):
        """ internal use: applies reverse transformation to a numpy array """
        # this could be speeded up
        # Check the right order
        coords = self.__inv_translate_array__(coords) # finally translate
        coords = self.__inv_magnify_array__(coords)# then magnify
        coords = self.__inv_rotate_array__(coords)# then rotate
        coords = self.__inv_v_flip_array__(coords)# first flip 
        return coords    

    def apply_to_coord3(self, coord):
        """ applies transformation to a coordinate """
        # this could be speeded up
        # Check the east order
        coord = self.__v_flip3__(coord)# first flip 
        coord = self.__rotate3__(coord)# then magnify
        coord = self.__magnify3__(coord)# then rotate
        coord = self.__translate3__(coord) # finally translate
        return coord
    
    def reverse_on_coord3(self, coord):
        """ applies reverse transformation to a coordinate """
        # this could be speeded up
        # Check the right order
        coord = self.__inv_translate3__(coord) # finally translate
        coord = self.__inv_magnify3__(coord)# then rotate
        coord = self.__inv_rotate3__(coord)# then magtnify
        coord = self.__inv_v_flip3__(coord)# first flip 
        return coord

    def apply_to_array3(self, coords):
        """ internal use: applies transformation to a numpy array"""
        # this could be speeded up
        # Check the right order
        coords = self.__v_flip_array3__(coords)# first flip 
        coords = self.__rotate_array3__(coords)# then rotate
        coords = self.__magnify_array3__(coords)# then magnify
        coords = self.__translate_array3__(coords) # finally translate
        return coords
    
    def reverse_on_array3(self, coord):
        """ internal use: applies reverse transformation to a numpy array """
        # this could be speeded up
        # Check the right order
        coords = self.__inv_translate_array3__(coords) # finally translate
        coords = self.__inv_magnify_array3__(coords)# then magnify
        coords = self.__inv_rotate_array3__(coords)# then rotate
        coords = self.__inv_v_flip_array3__(coords)# first flip 
        return coords    
    
    
    def apply_to_angle_deg(self, angle):
        """ applies transformation to an absolute angle (degrees) """
        a = angle
        if self.v_mirror:
            a = -a
        a += self.rotation
        return a % 360.0
    
    def reverse_on_angle_deg(self, angle):
        """ applies reverse transformation to an absolute angle (degrees)"""
        a = angle - self.rotation
        if self.v_mirror:
            a = -a
        return a % 360.0

    def apply_to_angle_rad(self, angle):
        """ applies transformation to an absolute angle (radians) """
        a = angle
        if self.v_mirror:
            a = -a
        a += self.rotation * DEG2RAD
        return a % (2 * pi)
    
    def reverse_on_angle_rad(self, angle):
        """ applies reverse transformation to an absolute angle (radians) """
        a = angle - self.rotation * DE2RAD
        if self.v_mirror:
            a = -a
        return a % (2 * pi)

    def apply_to_length(self, length):
        """ applies transformation to a distance """
        return length * self.magnification

    def reverse_on_length(self, length):
        """ applies reverse transformation to a distance """
        return length / self.magnification

    def __neg__(self):
        """ returns the reverse transformation """
        from .translation import Translation
        from .rotation import Rotation
        from .magnification import Magnification
        from .mirror import VMirror
        
        T = Translation(- self.translation) + Magnification((0.0, 0.0), 1 / self.magnification) + Rotation((0.0, 0.0), -self.rotation)
        if self.v_mirror:
            T += VMirror(0.0)
        return T

    def __sub__(self, other):
        """ returns the concatenation of this transform and the reverse of other """
        if other is None: return copy.deepcopy(self)
        if not isinstance(other, __ReversibleTransform__):
            raise TypeError("Cannot subtract an irreversible transform")
        return self.__add__(-other)

    def __isub__(self, other):
        """ concatenates the reverse of other to this transform """
        if other is None: return self
        if not isinstance(other, __ReversibleTransform__):
            raise TypeError("Cannot subtract an irreversible transform")
        return self.__iadd__(self, -other)

    def __add__(self, other):
        """ returns the concatenation of this transform and other """
        # performs transformation "other" after "self" and returns resulting transform
        if other is None: return copy.deepcopy(self)

        if isinstance(other, NoDistortTransform):
            T = NoDistortTransform()

            if self.absolute_magnification:
                M1 = 1.0
            else:
                M1 = other.magnification
            T.magnification = self.magnification * M1

            #flip signs
            if other.v_mirror: s_1 = -1
            else:              s_1 = 1

            if not self.absolute_rotation:
                T.rotation = s_1 * self.rotation + other.rotation
                ca = other.__ca__
                sa = other.__sa__
            else:
                T.rotation = s_1 * self.rotation
                ca = 1.0
                sa = 0.0


            # tricky part: translation
            T.translation = Coord2(other.translation.x + ca * self.translation.x * M1 - s_1 * sa * self.translation.y * M1,
                                   other.translation.y + sa * self.translation.x * M1 + s_1 * ca * self.translation.y * M1)

            T.absolute_rotation = self.absolute_rotation or other.absolute_rotation
            T.absolute_magnification = self.absolute_magnification or other.absolute_magnification
            T.v_mirror = (not self.v_mirror == other.v_mirror)
        else:
            T = Transform.__add__(self, other)
        return T

    def __iadd__(self, other):
        """ concatenates other to this transform """
        if other is None: return self
        # performs transformation other after self and returns self
        if isinstance(other, NoDistortTransform):
            # tricky part: translation
            if self.absolute_magnification:
                self.magnification = self.magnification * other.magnification
                M1 = 1
            else:
                M1 = other.magnification

            #flip signs
            if other.v_mirror: s_1 = -1
            else:              s_1 = 1


            if not self.absolute_rotation:
                self.rotation = s_1 * self.rotation + other.rotation
                ca = other.__ca__
                sa = other.__sa__
            else:
                self.rotation = s_1 * self.rotation                
                ca = 1
                sa = 0

            # tricky part: translation
            self.translation = (other.translation.x + ca * self.translation.x * M1 - s_1 * sa * self.translation.y * M1,
                                other.translation.y + sa * self.translation.x * M1 + s_1 * ca * self.translation.y * M1)

            self.absolute_rotation = self.absolute_rotation or other.absolute_rotation
            self.absolute_magnification = self.absolute_magnification or other.absolute_magnification
            self.v_mirror = (not self.v_mirror == other.v_mirror)
        else:
            raise TypeError("Error: Cannot perform += operation for NoDistortTransform and other transform of type " + str(type(other)))
        return self
    
    def __eq__(self, other):
        """ check if the transforms do the same thing """
        if other is None: return self.is_identity()
        if not isinstance(other, NoDistortTransform): return False
        return ((self.rotation == other.rotation) and
                (self.translation == other.translation) and
                (self.v_mirror == other.v_mirror) and
                (self.magnification == other.magnification) and
                (self.absolute_rotation == other.absolute_rotation) and
                (self.absolute_magnification == other.absolute_magnification)
                )

    def __ne__(self, other):
        """ checks if the transforms do different things """

        if other is None: return not self.is_identity()
        if not isinstance(other, NoDistortTransform): return False
        return ((self.rotation != other.rotation) or
                (self.translation != other.translation) or
                (self.v_mirror != other.v_mirror) or
                (self.magnification != other.magnification) or
                (self.absolute_rotation != other.absolute_rotation) or 
                (self.absolute_magnification != other.absolute_magnification)
                )
        
    def is_identity(self):
        """ returns True if the transformation does nothing """
        return ((self.rotation == 0.0) and
                (self.translation.x == 0.0) and
                (self.translation.y == 0.0) and
                not (self.v_mirror) and 
                (self.magnification == 1.0)
            )

    def is_isometric(self):
        """ returns True if the transformation conserves angles and distances """
        return self.magnification == 1.0

    def is_homothetic(self):
        """ returns True if the transformation conserves angles """
        return True

    def is_orthogonal(self):
        """ returns True if the transformation does only rotate on 90degree angles """
        return (self.rotation % 90.0) == 0.0

    def is_octogonal(self):
        """ returns True if the transformation does only rotate on 45degree angles """
        return (self.rotation % 45.0) == 0.0
    
    def id_string(self):
        """ gives a hash of the transform (for naming purposes) """
        return str(hash("R" + str(int(self.rotation * 10000)) + 
                        "T" + str(int(self.translation[0] * 1000)) + "_" + str(int(self.translation[1] * 1000)) +
                        "M" + str(int(self.magnification * 1000)) +
                        "V" + str(self.v_mirror) +
                        "AM" + str(self.absolute_magnification) +
                        "AR" + str(self.absolute_rotation) 
                        ))
    
    def __str__(self):
        """ gives a string representing the transform """
        return "R=%s-T=%s-M=%s-V=%s-AM=%s-AR=%s" % (str(int(self.rotation * 10000)), 
                                        str(int(self.translation[0] * 1000)) + "_" + str(int(self.translation[1] * 1000)),
                                        str(int(self.magnification * 1000)),
                                        str(self.v_mirror),
                                        str(self.absolute_magnification),
                                        str(self.absolute_rotation))    


