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

from .display_style import DisplayStyleProperty, DisplayStyle
from ipcore.mixin.mixin import MixinIngredient
from ..primitives.layer import Layer
from .color import COLOR_BLACK, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_RED, COLOR_WHITE, COLOR_YELLOW


class DisplayLayer(MixinIngredient):
    display_style = DisplayStyleProperty(default = None)
    

Layer.mixin(DisplayLayer)
cycle_colors = [COLOR_BLACK, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_MAGENTA, COLOR_YELLOW, COLOR_CYAN]
DEFAULT_DISPLAY_LAYER_SET = [(D, DisplayStyle(color = cycle_colors[D%len(cycle_colors)], alpha = 0.5)) for D in xrange(256)]
