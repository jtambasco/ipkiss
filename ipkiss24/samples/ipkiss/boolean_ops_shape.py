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


# First create 2 ShapeCircle's and corresponding boundaries to start from...

sc1 = ShapeCircle(center = (0.0,0.0), radius = 10.0)
sc2 = ShapeCircle(center = (12.0,0.0), radius = 7.0)

cp1 = Boundary(layer = Layer(1), shape = sc1)
cp2 = Boundary(layer = Layer(1), shape = sc2)

# Boolean operations on the shapes

elements = [cp1, cp2]
for rsh in sc1 & sc2:
    elements.append(Boundary(layer = Layer(2), shape = rsh))    
for rsh in sc1 - sc2:
    elements.append(Boundary(layer = Layer(3), shape = rsh))    
for rsh in sc1 | sc2:
    elements.append(Boundary(layer = Layer(4), shape = rsh))    
for rsh in sc1.xor(sc2):
    elements.append(Boundary(layer = Layer(5), shape = rsh))

s = Structure(elements = elements)

s.write_gdsii("sample_boolean_ops.gds")

# Boolean operations on the boundaries

b_and = cp1 & cp2
for b in b_and:
    b.layer = Layer(6)
    
b_sub = cp1 - cp2
for b in b_sub:
    b.layer = Layer(7)
    
b_or = cp1 | cp2
for b in b_or:
    b.layer = Layer(8)
    
b_xor = cp1.xor(cp2)
for b in b_xor:
    b.layer = Layer(9)       

s2 = Structure(elements = b_and + b_sub + b_or + b_xor)
s2.write_gdsii("sample_boolean_ops_2.gds")





