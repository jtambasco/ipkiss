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

import hashlib
import pickle
from itertools import chain


def cache():
    """caching decorator: caches the result of a function called on an object"""
    def _cache(function):
        def __cache(*args, **kw):
            key = hashlib.sha1(function.func_name).hexdigest()
            obj = args[0]
            if not hasattr(obj, "__IPCORE_CACHE__"):
                obj.__IPCORE_CACHE__ = dict()

            if key in obj.__IPCORE_CACHE__:
                return obj.__IPCORE_CACHE__[key]

            #not in cache... call the underlying function, then case the result
            result = function(*args, **kw)
            obj.__IPCORE_CACHE__[key] = result
            return result
        return __cache
    return _cache
