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


import ipkiss.aspects

from constants import *
from settings import *

from ipcore.all import *
from ipkiss.log import IPKISS_LOG as LOG

from geometry.transform import *
from geometry.transformable import *
from geometry.transforms.no_distort import *
from geometry.transforms.translation import *
from geometry.transforms.rotation import *
from geometry.transforms.identity import *
from geometry.transforms.magnification import *
from geometry.transforms.mirror import *
from geometry.transforms.stretch import *
from geometry.coord import *
from geometry.vector import *
from geometry.shape import *
from geometry.line import *
from geometry.shapes.basic import *
from geometry.shapes.advanced import *
from geometry.shape_cut import *
from geometry.shape_info import *
from geometry.size_info import *
from geometry.shape_modify import *
from geometry.shape_modifier import *
from geometry.shapes.modifiers import *
from geometry.shapes.curves import *

from primitives.layer import *
from primitives.elements import *
from primitives.fonts import *
from primitives.library import *
from primitives.structure import *

from io.import_hpgl import *
from io.input_gdsii import *
from io.output import OutputBasic
from io.output_gdsii import *
from io.output_object import *
from io.output_xml import *
from io.file_io import *
from io.gds_layer import *

from process import ProcessProperty, PurposeProperty, PPLayer, ProcessPurposeLayer, ProcessLayer, PatternPurpose

from technology.settings import get_technology

TECH = get_technology()

from exceptions import *

#from settings import *

from boolean_ops import *







