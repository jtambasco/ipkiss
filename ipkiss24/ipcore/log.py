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


__all__ = ["IPCORE_LOG"]

import logging
import sys

IPCORE_LOGGING_HANDLER = logging.StreamHandler(sys.stderr)
IPCORE_LOG = logging.getLogger('IPCORE')
IPCORE_LOG.setLevel(logging.ERROR)
IPCORE_LOG.addHandler(IPCORE_LOGGING_HANDLER)

displayed_deprecation_warnings = []


def display_warning(self, message, frame_depth=2, warning_str="WARNING"):
    if frame_depth > 0:
        from sys import _getframe
        f = _getframe(frame_depth)
        fname = f.f_code.co_filename
        lno = f.f_lineno
    else:
        fname = ""
        lno = 0
    if (fname, lno) not in displayed_deprecation_warnings:
        sys.stderr.writelines("\n**%s** %s\nPLEASE MODIFY YOUR SCRIPT !\n%s %s %s %d\n" % (warning_str,
                                                                                           message,
                                                                                           " -> in ",
                                                                                           fname,
                                                                                           "line",
                                                                                           lno)
                    )
        displayed_deprecation_warnings.append((fname, lno))


# add deprecation_warning function to the Logger class
def deprecation_warning(self, message, frame_depth=2):
    self.display_warning(message=message, frame_depth=frame_depth, warning_str="DEPRECATION_WARNING")

logging.Logger.display_warning = display_warning
logging.Logger.deprecation_warning = deprecation_warning
