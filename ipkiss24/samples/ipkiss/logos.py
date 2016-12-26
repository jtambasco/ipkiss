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

if __name__ == "__main__":
    from technologies.si_photonics.ipkiss.default import *
from ipkiss.all import *
from genericpdk.library.logos import *
import sys

# makes the logos og Ghent University, IMEC and INTEC available

class LogosExample(Structure):
    
    def define_elements(self, elems):
        #-------------------------------------------------------------------
        # INTEC Logo
        logo_size = (150.0, 150.0)
        intec = IntecLogo (PPLayer(process = TECH.PROCESS.WG, purpose = TECH.PURPOSE.DF.TRENCH), logo_size)        
        #-------------------------------------------------------------------
        # UGent Logo
        ugent = UGentLogo(PPLayer(process = TECH.PROCESS.WG, purpose = TECH.PURPOSE.DF.TRENCH), size = logo_size)        
        #-------------------------------------------------------------------
        # IMEC Logo
        imec = ImecLogo(PPLayer(process = TECH.PROCESS.WG, purpose = TECH.PURPOSE.DF.TRENCH), size = logo_size)        
        #-------------------------------------------------------------------
        # Layout with references to all other structures
        ypos = 200
        xpos = 0
        elems += SRef(intec, (xpos,ypos))
        xpos += 250
        elems += SRef(ugent, (xpos,ypos))
        xpos += 250
        elems += SRef(imec, (xpos,ypos))               
        return elems

if __name__ == "__main__":
        layout = LogosExample(name = "layout")
        my_lib = Library(name = "LOGOS", unit = 1E-6, grid = 5E-9)
        # Add main layout to library
        my_lib += layout
        fileName = "example_logos.gds"
        OP = FileOutputGdsii(fileName)
        # Write library
        OP.write(my_lib)
        print "Done : GDS2 file written to %s" %fileName    
        #remark : instead of manually creating a Library and exporting it to GDS2, it is also possible to use 
        #the convenient shortcut function "write_gdsii" directly on the Structure, i.e.:
        #layout.write_gdsii("example_logos.gds")        
        


