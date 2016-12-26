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

from intec.technology.imec import *
from ipkiss.io.input_gdsii import InputGdsii
from ipkiss.plugins.vfabrication import *
import sys

def vfabrication_for_gds(gds_file):
    print "Reading %s..."%(gds_file)
    I = InputGdsii(file(gds_file, "rb"))
    L = I.read()
    print "Done reading the gds. Now starting the virtual fabrication..."
    L.visualize_structures_2d()

    

if __name__ == '__main__':
    if len(sys.argv)>1:
        #To use of this script from command line: view_2d.py gds_file.gds
        vfabrication_for_gds(sys.argv[1])
    else:
        vfabrication_for_gds("my_file.gds")