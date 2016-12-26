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

from .curved_basic import CurveDimension, CurvedGrating
from ..basic import FiberCouplerGrating
from math import tan, floor, ceil, asin, cos, sin, atan,sqrt
from ipkiss.all import *

__all__ = ["ConcentricCurvedGrating",
           "ConcentricCurvedGratingBox",
           "ConfocalCurvedGratingBox",
           "ConfocalCurvedGratingBoxApodized",
           "ConfocalCurvedGratingBoxGeneric",
           "AngleConfocalCurvedGratingBox",
           "AngleConfocalCurvedGratingBoxApodized",
           "MinXConfocalCurvedGratingBox",               
           "FiberCouplerConcentricCurvedGrating",
           "FiberCouplerConcentricCurvedGratingBox",
           "FiberCouplerConfocalCurvedGratingBox",
           "FiberCouplerConfocalCurvedGratingBoxApodized",
           "FiberCouplerConfocalCurvedGratingBoxGeneric",
           "FiberCouplerAutoConfocalCurvedGratingBox",
           "FiberCouplerMinXConfocalCurvedGratingBox",
           "FiberCouplerAutoConfocalCurvedGratingBoxApodized",
           ]
           
##############################################################
## Curved gratings with generic aperture
##############################################################

def ConcentricCurvedGrating(min_r_h, min_r_v, h_period, v_period, n_o_trenches, trench_width, angle, process = TECH.PROCESS.FC):
    """ Concentric elliptical curved grating Alle ellipses describe the same angle"""
    focus_position = min_r_h + 0.5*n_o_trenches * h_period
    cd=[]
    for i in range(n_o_trenches):
        cd.append(CurveDimension(center = (focus_position, 0.0), 
                                 ellipse_r_h = min_r_h + i * h_period, 
                                 ellipse_r_v = min_r_v + i * v_period, 
                                 angle = angle, 
                                 line_width = trench_width, 
                                 purpose = TECH.PURPOSE.DF.TRENCH, 
                                 process = process))
    return CurvedGrating(cd)

def FiberCouplerConcentricCurvedGrating(min_r_h, min_r_v, h_period, v_period, n_o_trenches, trench_width, angle, socket, process = TECH.PROCESS.FC, socket_position=(0.0, 0.0)):
    """ Concentric elliptical curved grating Alle ellipses describe the same angle"""
    grating = ConcentricCurvedGrating(min_r_h, min_r_v, h_period, v_period, n_o_trenches, trench_width, angle, process = TECH.PROCESS.FC)
    return FiberCouplerGrating(socket=socket, socket_position=socket_position, grating=grating)

##############################################################

def ConcentricCurvedGratingBox(min_r_h, min_r_v, h_period, v_period, n_o_trenches, trench_width, box_width, process = TECH.PROCESS.FC):
    """ Concentric elliptical curved grating fit inside a rectangular box """
    cd = []
    focus_position = min_r_h + 0.5*n_o_trenches * h_period
    for i in range(n_o_trenches):
        r_h = min_r_h + i * h_period
        r_v = min_r_v + i * v_period
        if r_v < 0.5 * box_width:
            angle = 180.0
        else:
            angle = 2* RAD2DEG * asin(0.5 * box_width/r_v)            
        cd.append(CurveDimension(center = (focus_position, 0.0), 
                                 ellipse_r_h = r_h, 
                                 ellipse_r_v = r_v, 
                                 angle = angle, 
                                 line_width = trench_width, 
                                 purpose = TECH.PURPOSE.DF.TRENCH, 
                                 process = process))
    return CurvedGrating(cd, process)

def FiberCouplerConcentricCurvedGratingBox(min_r_h, min_r_v, h_period, v_period, n_o_trenches, trench_width, box_width, socket , process = TECH.PROCESS.FC, socket_position=(0.0, 0.0)):
    """ Concentric elliptical curved grating fit inside a rectangular box """
    grating = ConcentricCurvedGratingBox(min_r_h, min_r_v, h_period, v_period, n_o_trenches, trench_width, box_width, process )
    return FiberCouplerGrating(socket=socket,socket_position=socket_position, grating=grating)

##############################################################

def ConfocalCurvedGratingBoxGeneric(line_widths_positions, focus_position, box_width, v_h_ratio = 1.0, process = TECH.PROCESS.FC):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle.
        This can be a set of arbitraty lines and x-positions. The ellipses are made confocal, and the h_v_ratio gives the ratio of the vertical versus the 
        horizontal size of the ellipses. (Should be between zero and one) """
    if v_h_ratio <= 0.0 or v_h_ratio > 1.0:
        raise ValueError("v_h_ratio should be between 0 and 1 in ConfocalCurvedGratingBoxGeneric")
    cd = []

    for (w, x)  in line_widths_positions:
        r_h = 2*(focus_position[0] - x) / (1-v_h_ratio)
        r_v = r_h * v_h_ratio
        x_c = x + r_h
        if r_v < 0.5 * box_width:
            angle = 180.0
        else:
            angle = 2* RAD2DEG * asin(0.5 * box_width/r_v)
            
        cd.append(CurveDimension(center = (x_c, 0.0), 
                                 ellipse_r_h = r_h, 
                                 ellipse_r_v = r_v, 
                                 angle = angle, 
                                 line_width = w, 
                                 purpose = TECH.PURPOSE.DF.TRENCH, 
                                 process = process))
    return CurvedGrating(cd, process)

def FiberCouplerConfocalCurvedGratingBoxGeneric(line_widths_positions, focus_position, box_width,socket, v_h_ratio = 1.0, process = TECH.PROCESS.FC,socket_position=(0.0, 0.0)):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle
        This can be a set of arbitraty lines and x-positions. The ellipses are made confocal, and the h_v_ratio gives the ratio of the vertical versus the 
        horizontal size of the ellipses. (Should be between zero and one) """
    grating = ConfocalCurvedGratingBoxGeneric(line_widths_positions, focus_position, box_width, v_h_ratio , process = process)
    return FiberCouplerGrating(socket=socket,socket_position=socket_position, grating=grating)

##############################################################

def ConfocalCurvedGratingBox(min_index,  h_period, v_period, n_o_trenches, box_width, fill_factor = 0.5, process = TECH.PROCESS.FC):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle"""
    cd = []
    r_h_step = (h_period**2 + v_period**2)*0.5/h_period
    focus_position = (min_index + 0.5 * n_o_trenches) * h_period
    trench_width = snap_value(fill_factor * h_period) ### FIXME: snap value

    
    for i in range(int(min_index), int(n_o_trenches + min_index)):
        r_h = i * r_h_step
        r_v = i * v_period
        x_c = - i * (h_period - r_h_step)
        if r_v < 0.5 * box_width:
            angle = 180.0
        else:
            angle = 2* RAD2DEG * asin(0.5 * box_width/r_v)            
        cd.append(CurveDimension(center = (focus_position + x_c, 0.0),
                                 ellipse_r_h = r_h, 
                                 ellipse_r_v = r_v, 
                                 angle = angle, 
                                 line_width = trench_width, 
                                 purpose = TECH.PURPOSE.DF.TRENCH, 
                                 process = process))
    return CurvedGrating(cd, process)

def FiberCouplerConfocalCurvedGratingBox(min_index,  h_period, v_period, n_o_trenches, box_width, socket, fill_factor = 0.5, process = TECH.PROCESS.FC, socket_position=(0.0, 0.0)):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle"""
    grating = ConfocalCurvedGratingBox(min_index,  h_period, v_period, n_o_trenches, box_width, fill_factor , process = process)
    return FiberCouplerGrating(socket=socket, socket_position = socket_position,grating= grating)
##############################################################

def ConfocalCurvedGratingBoxApodized(min_index,  h_period, v_period, n_o_trenches, box_width, fill_factor = 0.5, apo_func = lambda t:t, chirp_func  = lambda p:p, process = TECH.PROCESS.FC):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle
        with apodization and chirping functions
    """
    cd = []
    focus_position = (min_index + 0.5 * n_o_trenches) * h_period
    ff = numpy.ones((n_o_trenches,))*fill_factor
    h_periods = chirp_func(numpy.ones((n_o_trenches,))*h_period)
    v_periods = chirp_func(numpy.ones((n_o_trenches,))*v_period)
    trench_widths = apo_func(ff*h_periods)
    
    for i in range(n_o_trenches):
        ndx = min_index + i
        r_h_step = (h_periods[i]**2 + v_periods[i]**2)*0.5/h_periods[i]
        
        r_h = ndx * r_h_step
        r_v = ndx * v_period
        x_c = - ndx * (h_period - r_h_step)
        if r_v < 0.5 * box_width:
            angle = 180.0
        else:
            angle = 2* RAD2DEG * asin(0.5 * box_width/r_v)            
        cd.append(CurveDimension(center = (focus_position + x_c, 0.0),
                                 ellipse_r_h = r_h, 
                                 ellipse_r_v = r_v, 
                                 angle = angle, 
                                 line_width = snap_value(trench_widths[i]), 
                                 purpose = TECH.PURPOSE.DF.TRENCH, 
                                 process = process))
    return CurvedGrating(cd, process)

def FiberCouplerConfocalCurvedGratingBoxApodized(min_index,  h_period, v_period, n_o_trenches, box_width, socket, fill_factor = 0.5, apo_func = lambda t:t, chirp_func = lambda p:p, process = TECH.PROCESS.FC, socket_position=(0.0, 0.0)):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle"""
    grating = ConfocalCurvedGratingBox(min_index,  h_period, v_period, n_o_trenches, box_width, fill_factor , apo_func, chirp_func, process = process)
    return FiberCouplerGrating(socket=socket, socket_position = socket_position,grating= grating)

##############################################################

def MinXConfocalCurvedGratingBox(min_x, h_period, v_period, box_length, box_width, fill_factor = 0.5, process = TECH.PROCESS.FC):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle, starting from a given distance from the focus point"""
    min_index = int(floor(min_x / h_period))
    max_index = int(ceil((min_x + box_length) / h_period))
    n_o_trenches = max_index - min_index + 1
    return ConfocalCurvedGratingBox(min_index, h_period, v_period, n_o_trenches, box_width, fill_factor, process)

def FiberCouplerMinXConfocalCurvedGratingBox(min_x, h_period, v_period, box_length, box_width,  socket, fill_factor = 0.5, process = TECH.PROCESS.FC, socket_position=(0.0, 0.0)):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle, starting from a given distance from the focus point"""
    grating = MinXConfocalCurvedGratingBox(min_x, h_period, v_period, box_length, box_width, fill_factor , process )
    return FiberCouplerGrating(socket=socket,socket_position=socket_position ,grating= grating)

##############################################################

def AngleConfocalCurvedGratingBox(h_period, v_period, box_length, box_width, angle, fill_factor = 0.5, extra_width = 0.0, process = TECH.PROCESS.FC,**kwargs):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle, with focus distance calculated from the aperture spread angle"""
    min_x = 0.5 * box_width / tan(0.5*angle*DEG2RAD) - 0.5 * box_length
    return MinXConfocalCurvedGratingBox(min_x, h_period, v_period, box_length, box_width + extra_width, fill_factor, process,**kwargs)

def FiberCouplerAutoConfocalCurvedGratingBox(h_period, v_period, box_length, box_width,  socket, fill_factor = 0.5, extra_width = 0.0, process = TECH.PROCESS.FC,socket_position = (0.0,0.0),**kwargs):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle, with focus distance calculated from the aperture spread angle"""
    grating = AngleConfocalCurvedGratingBox(h_period, v_period, box_length, box_width, socket.angle_deg(), fill_factor , extra_width , process )    
    return FiberCouplerGrating(socket=socket,socket_position=socket_position, grating=grating,**kwargs)

##############################################################
def MinXConfocalCurvedGratingBoxApodized(min_x, h_period, v_period, box_length, box_width, fill_factor = 0.5, apo_func = lambda t:t, chirp_func = lambda p:p, process = TECH.PROCESS.FC):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle, starting from a given distance from the focus point"""
    min_index = int(floor(min_x / h_period))
    max_index = int(ceil((min_x + box_length) / h_period))
    n_o_trenches = max_index - min_index + 1
    return ConfocalCurvedGratingBoxApodized(min_index, h_period, v_period, n_o_trenches, box_width, fill_factor, apo_func, chirp_func, process)

def AngleConfocalCurvedGratingBoxApodized(h_period, v_period, box_length, box_width, angle, fill_factor = 0.5, apo_func = lambda t:t, chirp_func = lambda p:p, extra_width = 0.0, process = TECH.PROCESS.FC,**kwargs):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle, with focus distance calculated from the aperture spread angle"""
    min_x = 0.5 * box_width / tan(0.5*angle*DEG2RAD) - 0.5 * box_length
    return MinXConfocalCurvedGratingBoxApodized(min_x, h_period, v_period, box_length, box_width + extra_width, fill_factor, apo_func, chirp_func, process,**kwargs)

def FiberCouplerAutoConfocalCurvedGratingBoxApodized(h_period, v_period, box_length, box_width,  socket, fill_factor = 0.5, apo_func = lambda t:t, chirp_func =  lambda p:p, extra_width = 0.0, process = TECH.PROCESS.FC,socket_position = (0.0,0.0),**kwargs):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside a rectangle, with focus distance calculated from the aperture spread angle"""
    grating = AngleConfocalCurvedGratingBoxApodized(h_period, v_period, box_length, box_width, socket.angle_deg(), fill_factor , apo_func, chirp_func, extra_width , process )    
    return FiberCouplerGrating(socket=socket,socket_position=socket_position, grating=grating,**kwargs)
##############################################################

# FIXME - not working, to be looked at by Wim or Pieter 
#def ConfocalCurvedGratingEllipse(min_index, h_period, v_period, n_o_trenches, box_width, fill_factor = 0.5, process = TECH.PROCESS.FC):
    #""" Confocal elliptical curved grating (all ellipses share the east focus point) fit inside an elliptical area"""
    #cd = []

    #min_x = (min_index-0.5) * h_period
    #box_length = h_period * n_o_trenches
    #max_x = min_x + box_length
    
    #n_o_trenches = (max_x - min_x) / h_period #correct? WAS: max_index - min_index + 1 
    #focus_position = (min_index + 0.5 * n_o_trenches) * h_period
    #trench_width = snap_value(fill_factor * h_period) 
    #h_period = h_period - sqrt(abs(h_period**2-v_period*2))

    #R_v = 0.5 * box_width 
    #R_h = 0.5 * box_length

    #for i in range(min_index, n_o_trenches + min_index):
        #r_h = i * h_period
        #r_v = i * v_period
        #x_c = - sqrt(abs(r_h**2-r_v*2))
        ## solve the equations for the angle: difficult
        #X_C = R_h + min_x + x_c

        #A = R_v**2 * r_h**2
        #B = 2 * R_v**2 * r_h * X_C
        #C = R_v**2 * X_C**2 - R_v**2 * R_h**2
        #D = R_h**2 * r_v**2
        
        #c = A - B + C
        #b = 2 * (2*D - A + C)
        #a = A + B + C
        #Disc = b**2 - 4 * a * c
        ##tg2_t_2 = - (b - sqrt(Disc))/ (2*a)      #origineel
        ##tg2_t_2 = (-b - sqrt(Disc))/ (2*a)       # 1ste oplossing   
        ##tg2_t_2 = (-b + sqrt(Disc))/ (2*a)      # 2de oplossing
        #t = 2*atan(sqrt(tg2_t_2))
        #y = r_v * sin(t)
        #x = r_h * cos(t)
        
        #angle = 2 * RAD2DEG * atan2(y, x)
        #cd.append(CurveDimension((focus_position + x_c, 0.0), r_h, r_v, angle, trench_width, purpose = TECH.PURPOSE.DF.TRENCH, process = process))
    #return CurvedGrating(cd, process)


#FIXME - not working, to be looked at by Wim or Pieter 
#def FiberCouplerConfocalCurvedGratingEllipse(min_index,  h_period, v_period, n_o_trenches, box_width,socket, fill_factor = 0.5, process = TECH.PROCESS.FC):
    #grating = ConfocalCurvedGratingEllipse(min_index,  h_period, v_period, n_o_trenches, box_width, fill_factor , process )
    #return FiberCouplerGrating(socket=socket,socket_position=(0.0,0.0), grating=grating)


##############################################################

#FIXME - not working, to be looked at by Wim or Pieter 
#def MinXConfocalCurvedGratingEllipse(min_x, h_period, v_period, box_length, box_width,  fill_factor = 0.5, process = TECH.PROCESS.FC):
    #""" Confocal elliptical curved grating (all ellipses share the east focus point) fit inside an elliptical area, starting from a given distance from the focus point"""
    #min_index = int(floor(min_x / h_period))
    #max_index = int(ceil((min_x + box_length)/ h_period))

    #n_o_trenches = max_index - min_index + 1
    
    #return ConfocalCurvedGratingEllipse(min_index, h_period, v_period, n_o_trenches, box_width, fill_factor, process)

#FIXME - not working, to be looked at by Wim or Pieter     
#def FiberCouplerMinXConfocalCurvedGratingEllipse(min_x, h_period, v_period, box_length, box_width,  socket, fill_factor = 0.5, process = TECH.PROCESS.FC):
    #grating = MinXConfocalCurvedGratingEllipse(min_x, h_period, v_period, box_length, box_width,  fill_factor , process )
    #return FiberCouplerGrating(socket=socket,socket_position=(0.0,0.0), grating=grating)


##############################################################


def AngleConfocalCurvedGratingBox(h_period, v_period, box_length, box_width,  angle, fill_factor = 0.5, extra_width = 0.0, process = TECH.PROCESS.FC):
    """ Confocal elliptical curved grating (all ellipses share the east focus point) fit inside an elliptcial area, with focus distance calculated from the aperture spread angle"""
    min_x = 0.5 * box_width / tan(0.5*angle*DEG2RAD) - 0.5 * box_length
    return MinXConfocalCurvedGratingBox(min_x, h_period, v_period, box_length, box_width + extra_width, fill_factor,  process )


##############################################################
