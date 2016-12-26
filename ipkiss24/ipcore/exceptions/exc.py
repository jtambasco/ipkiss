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


__all__ = ["IpcoreException", "IpcoreAttributeException", "IpcorePropertyDescriptorException",
           "IpcoreRestrictionException", "OpenAccessIntegrationException"]

from ipcore.log import IPCORE_LOG as LOG


class IpcoreException(Exception):
    def __init__(self, Msg):
        super(IpcoreException, self).__init__(Msg)


class IpcoreAttributeException(IpcoreException):
    """Exception with attributes """
    def __init__(self, Msg):
        super(IpcoreAttributeException, self).__init__(Msg)


class IpcorePropertyDescriptorException(IpcoreAttributeException):
    """General Exception with property descriptors"""
    def __init__(self, Msg):
        super(IpcorePropertyDescriptorException, self).__init__(Msg)


class IpcoreRestrictionException(IpcorePropertyDescriptorException):
    """Property restriction """
    def __init__(self, Msg):
        super(IpcoreRestrictionException, self).__init__(Msg)


class NotImplementedException(IpcoreException):
    """Exception for functionality that the user must implement through subclassing """
    def __init__(self, Msg="Method not implemented."):
        super(NotImplementedException, self).__init__(Msg)


class InvalidArgumentException(IpcoreException):
    """Exception indicating the use of an invalid argument """
    def __init__(self, Msg):
        super(InvalidArgumentException, self).__init__(Msg)


# FIXME - move to IPKISS once OA integration stuff is there
class OpenAccessIntegrationException(IpcoreException):
    """Exception used in the OpenAccess integration code"""
    def __init__(self, Msg):
        super(IpcoreException, self).__init__(Msg)
