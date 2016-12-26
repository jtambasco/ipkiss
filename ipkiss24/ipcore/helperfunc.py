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

import zlib
import sys

__all__ = ["is_call_internal", "do_hash"]


def is_call_internal(obj, level=1):
    """ checks if a call to a function is done from within the object
        or from outside """
    f = sys._getframe(1 + level).f_locals
    if not "self" in f:
        return False
    return (f["self"] is obj)


def do_hash(obj):
    if (isinstance(obj, list)):
        return abs(sum(do_hash(e) for e in obj))
    else:
        return abs(zlib.adler32(str(obj)))


def extract_kwarg(kwargs, arg_name):
    try:
        arg = kwargs[arg_name]
    except KeyError, ke:
        raise Exception("Keyword argument '%s' is required but was not found." % arg_name)
    del kwargs[arg_name]
    return arg
