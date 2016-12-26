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

from .input_gdsii import InputGdsii
from .output_gdsii import OutputGdsii

## Easy-to-use Read/write functions ###
__all__ = ["read_library_from_file",
           "write_library_to_file"]

## Read
def read_library_from_file(filename, input_type):
    """ reads a library from a file using the input processor """
    f = open(filename,"rb")
    i = InputGdsii(f)
    L = i.read()
    f.close()
    return L


## Write
def write_library_to_file(library, filename, output_type):
    """ writes a library to a file using the given output processor """
    f = open(filename,"wb")
    o = OutputGdsii(f)
    o.write(library)
    f.close()

