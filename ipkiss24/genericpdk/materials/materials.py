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

from pysics.basics.material.material_stack import Material
from pyfab.materials.resist import PatterningResistMaterial
from ipkiss.visualisation.display_style import DisplayStyle
from ipkiss.visualisation.color import *
from ipkiss.visualisation.stipple import *

__all__ = []


###########################################################
# Raw materials involved
###########################################################

AIR = Material(name = "air",
               display_style = DisplayStyle(color = COLOR_BLUE, alpha = 0.2), 
               solid = False)
SILICON = Material(name = "silicon",
                   display_style = DisplayStyle(color = COLOR_ORANGE))
SILICON_OXIDE = Material(name = "silicon oxide", 
                         display_style = DisplayStyle(color = COLOR_YELLOW, alpha = 0.7))
SILICON_NITRIDE = Material(name = "silicon nitride", 
                         display_style = DisplayStyle(color = COLOR_CYAN))
SILICON_CARBON_NITRIDE = Material(name = "silicon carbon nitride", 
                         display_style = DisplayStyle(color = COLOR_BLUE))

PHOTORESIST = PatterningResistMaterial(name = "photoresist",
                                       display_style = DisplayStyle(color = COLOR_GREEN))
EXPOSED_PHOTORESIST = Material(name = "exposed_photoresist",
                                       display_style = DisplayStyle(color = COLOR_DARK_GREEN))

BARC = Material(name = "BARC",
                display_style = DisplayStyle(color = COLOR_DEEP_GREEN))

P_SILICON = Material(name = "P implanted silicon",
                     display_style = DisplayStyle(color = COLOR_BLUE_VIOLET))
PP_SILICON = Material(name = "P+ implanted silicon",
                     display_style = DisplayStyle(color = COLOR_BLUE_CRAYOLA))
N_SILICON = Material(name = "N implanted silicon",
                     display_style = DisplayStyle(color = COLOR_CHERRY))
NP_SILICON = Material(name = "N+ implanted silicon",
                     display_style = DisplayStyle(color = COLOR_CHAMPAGNE))
IMPUNDEF_SILICON = Material(name="silicon with undefined implant",
                            display_style = DisplayStyle(color = COLOR_RED, stipple=STIPPLE_LINES_DIAGONAL_L))
NICKEL = Material(name="Nickel",
                    display_style = DisplayStyle(color = COLOR_SCARLET))
NISI = Material(name="NiSi", display_style = DisplayStyle(color = COLOR_SANGRIA))

TITANIUM = Material(name="Titanium",
                    display_style = DisplayStyle(color = COLOR_SILVER))
TITANIUM_NITRIDE = Material(name="Titanium nitride",
                    display_style = DisplayStyle(color = COLOR_TITANIUM_YELLOW))
TUNGSTEN = Material(name="Tungsten",
                    display_style = DisplayStyle(color = COLOR_GRAY))
COPPER = Material(name="Copper",
                  display_style = DisplayStyle(color=COLOR_COPPER))
TANTALUM = Material(name="Tantalum",display_style = DisplayStyle(color = COLOR_SCARLET))
TANTALUM_NITRIDE = Material(name="Tantalum_Nitride",display_style = DisplayStyle(color = COLOR_SANGRIA))

ALUMINIUM_COPPER = Material(name="AlCu", display_style = DisplayStyle(color=COLOR_DARKSEA_GREEN))