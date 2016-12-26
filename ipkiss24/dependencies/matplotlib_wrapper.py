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

import Tkinter as Tk
from sys import stderr
try:
    import matplotlib as matplotlib
    matplotlib.use('TkAgg')
    
    from matplotlib import nxutils as nxutils
    
    from matplotlib import pyplot as pyplot
    from matplotlib import pylab as pylab
    from matplotlib.collections import *
    from matplotlib.colors import colorConverter
    
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
    
    from matplotlib.figure import Figure
    
    from matplotlib.ticker import ScalarFormatter
    
    from matplotlib import font_manager
    
    from matplotlib.patches import Rectangle
    
    pyplot.ion()

except ImportError, e:
    print >> stderr, "*************************** DEPENDENCY NOT FOUND **************************************************************************************** "
    print >> stderr, "**** MODULE MATPLOTLIB COULD NOT BE FOUND, PLEASE INSTALL IT                                                                          *** "
    print >> stderr, "**** On Windows, download from :                                                                                                      *** "
    print >> stderr, "****         http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-0.99.3/matplotlib-0.99.3.win32-py2.6.exe/download *** "
    print >> stderr, "**** On Linux : sudo apt-get install python-matplotlib                                                                                *** "
    print >> stderr, "***************************************************************************************************************************************** "
    
    