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

from ipcore.all import *
from dependencies.matplotlib_wrapper import Figure, Tk, NavigationToolbar2TkAgg, FigureCanvasTkAgg
from .basic import __VisualisationManager__

__all__ = ["FigureVisualisationManager"]


class FigureVisualisationManager(__VisualisationManager__):
    """ Object that manages visualization of a matplotlib figure: on screen, saving to image ...
    """
    item = RestrictedProperty(required = True, restriction = RestrictType(Figure), doc = "matplotlib Figure to be visualized")
    
    
    def show(self, title = "Visualisation", hold_for_user = True):
        fig = self.item        
        root = Tk.Tk()
        root.wm_title(title)
        
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2TkAgg(canvas, root)
        toolbar.update()
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        canvas.show()
        
        if hold_for_user:
            Tk.mainloop()        
        
    def save_image(self, filename):
        fig = self.item
        fig.savefig(filename)
