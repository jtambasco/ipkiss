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

from output import OutputBasic
from inspect import ismethod
from ipkiss.log import IPKISS_LOG as LOG
DO = set(dir(list()))

__all__ = ["OutputObject"]

class OutputObject(OutputBasic):

    def __str_object__(self, item):
        s = []
        s.append("TYPE: " + str(type(item)))
        if hasattr(item, "name"):
            s.append("NAME: " + str(item.name))
        d = set(dir(item)) - DO
        for i in d:
            I = getattr(item,i)
            if ismethod(I): continue
            try:
                s.append("---" + str(i) + " = " + str(I))
            except:
                s.append("---" + str(i) + " : " + str(type(I)))
        s.append("-----------------------------------------------------\n")
        return "\n".join(s)

    def __str_library_header__(self, library):
        self.init_library_header(library)
        return self.__str_object__(library)

    def __str_library_footer__(self):
        return "END OF LIBRARY\n\n"

    def __str_structure_header__(self, item):
        LOG.info("STRUCTURE: " + item.name)
        return self.__str_object__(item)

    #generate the footer for any structure
    def __str_structure_footer__(self, item):
        return "END OF STRUCTURE : " + item.name + "\n\n"

    def str_shape_element(self, item):
        return "\n".join([self.__str_object__(item),
                          self.__str_object__(item.shape),
                          OutputBasic.str_shape_element(self, item),
                          ]
                          )

    def str_path_element (self, layer, coordinates, line_width, path_type):
        return "\n".join(["   PATHSHAPE = " + str(type(shape)),
                           self.__str_object__(coordinates)])

    def str_boundary_element (self, layer,coordinates):
        return "\n".join(["   BOUNDARYSHAPE = " + self.__str_object__(coordinates)])

    def str_label_element (self, item):
        return self.__str_object__(item)

    def str_box_element (self, item):
        return self.__str_object__(item)

    def str_sref_element (self, item):
        return self.__str_object__(item)

    def str_aref_element (self, item):
        return self.__str_object__(item)

