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
from ipcore.properties.restrictions import RestrictType


class __Processor__(StrongPropertyInitializer):
    """ generic processor """

    def process(self, data=None, **kwargs):
        # do nothing
        return None

    def __call__(self, data, **kwargs):
        return self.process(data, **kwargs)

    def initialize(self, **kwargs):
        pass

    def finalize(self, **kwargs):
        pass

    def stopProcessing(self):
        '''A flag indicating if the last processing step triggered the end of the procedure.'''
        return False


def EMPTY_PROCESSOR(self, **kwargs):
    return __Processor__()

# ------------------- STOP CRITERIA -------------------------


class __StopCriterium__(StrongPropertyInitializer):
    """generic stop criterium class"""

    def __init__(self, **kwargs):
        super(__StopCriterium__, self).__init__(**kwargs)

    def __call__(self):
        return self.evaluateStopCriterium()

    def evaluateStopCriterium(self):
        return False


class ProcessorStopCriterium(__StopCriterium__):
    """Stop criterium that does a callback to the processor to make the decision."""
    processor = RestrictedProperty(required=False, default=__Processor__(), restriction=RestrictType(__Processor__), doc="Reference back to the processor: this can be used to retrieve information about the processed steps, in order to make a decision for the stop criterium.")

    def __init__(self, **kwargs):
        super(ProcessorStopCriterium, self).__init__(**kwargs)

    def __call__(self):
        return self.evaluateStopCriterium()

    def evaluateStopCriterium(self):
        return self.processor.stopProcessing()
