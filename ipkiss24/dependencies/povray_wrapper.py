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

import sys, os

class PovrayFile:
  def __init__(self,fnam="out.pov",*items):
    self.file = open(fnam,"w")
    self.__indent = 0
    self.write(*items)
  def include(self,name):
    self.writeln( '#include "%s"'%name )
    self.writeln()
  def indent(self):
    self.__indent += 1
  def dedent(self):
    self.__indent -= 1
    assert self.__indent >= 0
  def block_begin(self):
    self.writeln( "{" )
    self.indent()
  def block_end(self):
    self.dedent()
    self.writeln( "}" )
    if self.__indent == 0:
      # blank line if this is a top level end
      self.writeln( )
  def write(self,*items):
    for item in items:
      if type(item) == str:
        self.include(item)
      elif isinstance(item, list):
        for e in item:
          self.write(e)
      else:
        item.write(self)
  def writeln(self,s=""):
    #print "  "*self.__indent+s
    self.file.write("  "*self.__indent+s+os.linesep)

class Vector:
  def __init__(self,*args):
    if len(args) == 1:
      self.v = args[0]
    else:
      self.v = args
  def __str__(self):
    return "<%s>"%(", ".join([str(x)for x in self.v]))
  def __repr__(self):
    return "Vector(%s)"%self.v
  def __mul__(self,other):
    return Vector( [r*other for r in self.v] )
  def __rmul__(self,other):
    return Vector( [r*other for r in self.v] )

class Vector_List:
  def __init__(self, points_list):
    self.points = points_list
  def __str__(self):
    return "%s"%(", ".join([str(Vector(x))for x in self.points]))

class Item:
  def __init__(self,name,args=[],opts=[],**kwargs):
    self.name = name
    args=list(args)
    for i in range(len(args)):
      if type(args[i]) == tuple or type(args[i]) == list:
        args[i] = Vector(args[i])
    self.args = args
    self.opts = opts
    self.kwargs=kwargs
  def append(self, item):
    self.opts.append( item )
  def write(self, file):
    if self.name != "":
      file.writeln( self.name )
      file.block_begin()
    if self.args:
      file.writeln( ", ".join([str(arg) for arg in self.args]) )
    for opt in self.opts:
      if hasattr(opt,"write"):
        opt.write(file)
      else:
        file.writeln( str(opt) )
    for key,val in self.kwargs.items():
      if type(val)==tuple or type(val)==list:
        val = Vector(*val)
        file.writeln( "%s %s"%(key,val) )
      else:
        file.writeln( "%s %s"%(key,val) )
    if self.name != "":
      file.block_end()
  def __setattr__(self,name,val):
    self.__dict__[name]=val
    if name not in ["kwargs","args","opts","name"]:
      self.__dict__["kwargs"][name]=val
  def __setitem__(self,i,val):
    if i < len(self.args):
      self.args[i] = val
    else:
      i += len(args)
      if i < len(self.opts):
        self.opts[i] = val
  def __getitem__(self,i,val):
    if i < len(self.args):
      return self.args[i]
    else:
      i += len(args)
      if i < len(self.opts):
        return self.opts[i]


class Interior(Item):
  def __init__(self,*opts,**kwargs):
    Item.__init__(self,"interior",(),opts,**kwargs)

class Texture(Item):
  def __init__(self,*opts,**kwargs):
    Item.__init__(self,"texture",(),opts,**kwargs)


class Pigment(Item):
  def __init__(self,*opts,**kwargs):
    Item.__init__(self,"pigment",(),opts,**kwargs)

class Finish(Item):
  def __init__(self,*opts,**kwargs):
    Item.__init__(self,"finish",(),opts,**kwargs)

class Normal(Item):
  def __init__(self,*opts,**kwargs):
    Item.__init__(self,"normal",(),opts,**kwargs)

class Camera(Item):
  def __init__(self,*opts,**kwargs):
    Item.__init__(self,"camera",(),opts,**kwargs)

class LightSource(Item):
  def __init__(self,v,*opts,**kwargs):
    Item.__init__(self,"light_source",(Vector(v),),opts,**kwargs)

class Background(Item):
  def __init__(self,*opts,**kwargs):
    Item.__init__(self,"background",(),opts,**kwargs)

class Box(Item):
  def __init__(self,v1,v2,*opts,**kwargs):
    #self.v1 = Vector(v1)
    #self.v2 = Vector(v2)
    Item.__init__(self,"box",(v1,v2),opts,**kwargs)

class Cylinder(Item):
  def __init__(self,v1,v2,r,*opts,**kwargs):
    " opts: open "
    Item.__init__(self,"cylinder",(v1,v2,r),opts,**kwargs)

class Plane(Item):
  def __init__(self,v,r,*opts,**kwargs):
    Item.__init__(self,"plane",(v,r),opts,**kwargs)

class Torus(Item):
  def __init__(self,r1,r2,*opts,**kwargs):
    Item.__init__(self,"torus",(r1,r2),opts,**kwargs)

class Cone(Item):
  def __init__(self,v1,r1,v2,r2,*opts,**kwargs):
    " opts: open "
    Item.__init__(self,"cone", (v1,r1,v2,r2),*opts,**kwargs)

class Sphere(Item):
  def __init__(self,v,r,*opts,**kwargs):
    Item.__init__(self,"sphere",(v,r),*opts,**kwargs)


class Prism(Item):
  def __init__(self,point_list , heights = (0, 1), prism_item = "linear_spline linear_sweep", opts = [],**kwargs):
    options = [heights[0], heights[1], len(point_list), Vector_List(point_list)]
    options.extend(opts)
    Item.__init__(self,"prism", [prism_item], options,**kwargs)

