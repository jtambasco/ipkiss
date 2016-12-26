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

import h5py
import os

def create_animated_gif_from_hdf5(field_filename, eps_filename, remove_png = True, uniform_colormap_range = True):
	f = h5py.File(field_filename, 'r')
	ds = f.items()[0][1]
	max_time = ds.shape[2]-1
	print "Creating animated gif from files %s and %s (time steps : %i)." %(field_filename, eps_filename, max_time)
	png_filename_template = field_filename.replace(".h5",".t*.png")
	print "Removing old png files : %s" %png_filename_template
	os.system("rm %s" %png_filename_template)
	print "Creating png files ...."	
	if (uniform_colormap_range):
		params = "-R"
	else:
		params = ""
	cmd = "h5topng %s -t 0:%i -Zc dkbluered %s -a gray -A %s" %(params, max_time, field_filename, eps_filename)
	os.system(cmd)
	print "Converting png files to animated gif...."
	gif_filename = field_filename.replace(".h5",".gif")
	os.system("convert %s %s" %(png_filename_template, gif_filename))
	if (remove_png):
		print "Removing png files..." 
		os.system("rm %s" %png_filename_template)
	print "Done with creating the animated gif : %s" %gif_filename
	return gif_filename


	
	
	

    
    
