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

__all__ = ['Environment', 
           'EnvironmentProperty',
           'DEFAULT_ENVIRONMENT']

class __Environment__(StrongPropertyInitializer):
    """ Base class to subclass with new environment properties """

class Environment(__Environment__):
    """ Class that holds all physical quantities which describe the environment 
        (Temperature, fields, ...)
        The environment can change from point to point in a Geometry.
        New physical quantities are mixed in when loading the library for some (multi)physics.
        Default values should ben those of vacuum at room temperature. 
    """
    pass

DEFAULT_ENVIRONMENT = Environment()

RESTRICT_ENVIRONMENT = RestrictType(Environment)
            
def EnvironmentProperty(internal_member_name= None, restriction = None, preprocess = None, **kwargs):
    """ Environment property descriptor for a class """ 
    R = RESTRICT_ENVIRONMENT & restriction
    return RestrictedProperty(internal_member_name = internal_member_name, restriction = R, preprocess = preprocess, **kwargs )
