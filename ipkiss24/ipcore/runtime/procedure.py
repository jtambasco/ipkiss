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

from ipcore.properties.initializer import StrongPropertyInitializer
from ipcore.properties.descriptor import RestrictedProperty
from ipcore.properties.predefined import CallableProperty
from ipcore.properties.restrictions import RestrictType
from ipcore.runtime.processor import __Processor__, EMPTY_PROCESSOR


class __Procedure__(StrongPropertyInitializer):
    """ generic procedure """

    # procedure before, during and after
    init_procedure = CallableProperty(default=None, 
                                      doc="initialization procedure before the procedure starts")
    step_procedure = CallableProperty(default=None, 
                                      doc="procedure for each step")
    fini_procedure = CallableProperty(default=None, 
                                      doc="finalization procedure after the procedure")

    # processing of data during and after
    step_processor = RestrictedProperty(default=__Processor__(), 
                                        restriction=RestrictType(__Processor__), 
                                        doc="Processor called in every step of the procedure.")
    post_processor = RestrictedProperty(default=__Processor__(), 
                                        restriction=RestrictType(__Processor__), 
                                        doc="Data processor after the procedure (e.g. visualize)")

    def __call__(self):
        return self.run()

    def run(self):
        pass


def EMPTY_PROCEDURE(self, **kwargs):
    return __Procedure__()
