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


STD_IOCOLUMN_Y_SPACING = 25.0
STD_IOCOLUMN_MARGIN = 50.0

STD_IOCOLUMN_Left_Margin = 150
STD_IOCOLUMN_Right_Margin = 250
STD_IOCOLUMN_Top_Margin = 300
STD_IOCOLUMN_Bottom_Margin = 300


########################################################
# Columns
########################################################

# STD12mm
STD12MM_Column_Width = 12100
STD12MM_Column_Spacing = 100
STD12MM_Column_N_Lines = 320
STD12MM_Column_Bottom_Left = lambda c: (STD_IOCOLUMN_Left_Margin + c*STD12MM_Column_Width + c*STD12MM_Column_Spacing,0.0)
STD12MM_Column_Bottom_Right = lambda c: (STD_IOCOLUMN_Left_Margin + (c+1)*STD12MM_Column_Width + c*STD12MM_Column_Spacing,0.0)

# STD6MM
STD6MM_Column_Width = 6000.0
STD6MM_Column_Spacing = 100
STD6MM_Column_N_Lines = 320
STD6MM_Column_Bottom_Left = lambda c: (STD_IOCOLUMN_Left_Margin + c*STD6MM_Column_Width + c*STD6MM_Column_Spacing,0.0)
STD6MM_Column_Bottom_Right = lambda c: (STD_IOCOLUMN_Left_Margin + (c+1)*STD6MM_Column_Width + c*STD6MM_Column_Spacing,0.0)

# STD4MM
STD4MM_Column_Width = 4000
STD4MM_Column_Spacing = 50
STD4MM_Column_N_Lines = 320
STD4MM_Column_Bottom_Left = lambda c: (STD_IOCOLUMN_Left_Margin + c*STD4MM_Column_Width + c*STD4MM_Column_Spacing,0.0)
STD4MM_Column_Bottom_Right = lambda c: (STD_IOCOLUMN_Left_Margin + (c+1)*STD4MM_Column_Width + c*STD4MM_Column_Spacing,0.0)

# STD3MM
STD3MM_Column_Width = 2950
STD3MM_Column_Spacing = 100
STD3MM_Column_N_Lines = 320
STD3MM_Column_Bottom_Left = lambda c: (STD_IOCOLUMN_Left_Margin + c*STD3MM_Column_Width + c*STD3MM_Column_Spacing,0.0)
STD3MM_Column_Bottom_Right = lambda c: (STD_IOCOLUMN_Left_Margin + (c+1)*STD3MM_Column_Width + c*STD3MM_Column_Spacing,0.0)


# STD1MM
STD1MM_Column_Width = 950
STD1MM_Column_Spacing = 100
STD1MM_Column_N_Lines = 320
#STD3MM_Column_Bottom_Left = [(STD_IOCOLUMN_Left_Margin, STD_IOCOLUMN_Bottom_Margin),
                           #(STD_IOCOLUMN_Left_Margin + STD3MM_Column_Widths[0] + STD3MM_Column_Spacings[0] , 0.0 ),
                           #(STD_IOCOLUMN_Left_Margin + STD3MM_Column_Widths[0] + STD3MM_Column_Spacings[0] + STD3MM_Column_Widths[1] + STD3MM_Column_Spacings[1] , 0.0 ),
                           #(STD_IOCOLUMN_Left_Margin + STD3MM_Column_Widths[0] + STD3MM_Column_Spacings[0] + STD3MM_Column_Widths[1] + STD3MM_Column_Spacings[1] + STD3MM_Column_Widths[2] + STD3MM_Column_Spacings[2] , 0.0)
                           #]
#STD3MM_Column_Bottom_Right = [(STD_IOCOLUMN_Left_Margin + STD3MM_Column_Widths[0], STD_IOCOLUMN_Bottom_Margin ),
                            #(STD_IOCOLUMN_Left_Margin + STD3MM_Column_Widths[0] + STD3MM_Column_Widths[1] + STD3MM_Column_Spacings[0] , 0.0),
                            #(STD_IOCOLUMN_Left_Margin + STD3MM_Column_Widths[0] + STD3MM_Column_Widths[1] + STD3MM_Column_Spacings[0] + STD3MM_Column_Widths[2] + STD3MM_Column_Spacings[1] , 0.0 ),
                            #(STD_IOCOLUMN_Left_Margin + STD3MM_Column_Widths[0] + STD3MM_Column_Widths[1] + STD3MM_Column_Spacings[0] + STD3MM_Column_Widths[2] + STD3MM_Column_Spacings[1] + STD3MM_Column_Widths[3] + STD3MM_Column_Spacings[2], 0.0)
                            #]

STD1MM_Column_Bottom_Left = lambda c: (STD_IOCOLUMN_Left_Margin + c*STD1MM_Column_Width + c*STD1MM_Column_Spacing,0.0)
STD1MM_Column_Bottom_Right = lambda c: (STD_IOCOLUMN_Left_Margin + (c+1)*STD1MM_Column_Width + c*STD1MM_Column_Spacing,0.0)



