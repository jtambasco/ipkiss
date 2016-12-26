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

#####################################################
## Shape Cutting
#####################################################

import math
from .shape import Shape

__all__ = ["cut_open_shape_with_overlap",
           "cut_open_shape_in_sections_with_overlap",
           "cut_open_shape_in_n_sections_with_overlap"]

###################################################
## Cut open shapes (paths)
####################################################

def cut_open_shape_with_overlap(shape, cut_indices, overlap=1):
    ci = list(cut_indices)
    if len(cut_indices) == 0:
        return [shape]
    shape = Shape(shape)
    if shape.closed and shape[0] != shape[-1]:
        shape += shape[0]
    shapes = []
    cmax = len(shape) 
    ccur = 0
    pre_overlap = int(overlap / 2)
    post_overlap = int(overlap - pre_overlap)
    if cmax - pre_overlap <= cut_indices[-1] + post_overlap + 2:
        cut_indices[-1] = cmax
    else:
        cut_indices.append(cmax)

    a = shape.angles_deg()
    for cp in cut_indices:
        sp = max(0, ccur - pre_overlap)
        ep = min(cp + 1 + post_overlap, cmax)
        s = Shape(shape[sp:ep], False)
        if len(s) > 0:

            if sp == 0:
                if not shape.start_face_angle is None:
                    s.start_face_angle = shape.start_face_angle
                
            else:
                s.start_face_angle = 0.5 * (a[sp - 1] + a[sp])


            if ep == cmax:
                if not shape.end_face_angle is None:
                    s.end_face_angle = shape.end_face_angle
            else:
                s.end_face_angle = 0.5 * (a[ep - 1] + a[ep - 2])
            shapes.append(s)

        ccur = cp

    return shapes


def cut_open_shape_in_n_sections_with_overlap(shape, n_o_sections, overlap=1):
    l = len(shape)
    section_length = int(math.ceil(l / n_o_sections))
    return cut_open_shape_with_overlap(shape, range(section_length - 1, l - overlap - 1, section_length), overlap)

def cut_open_shape_in_sections_with_overlap(shape, max_section_length, overlap=1, min_n_o_sections=1):
    l = len(shape)
    if l > max_section_length or min_n_o_sections > 1:
        no_paths = int(max(min_n_o_sections, math.ceil((l - overlap + 0.0) / (max_section_length - overlap))))
        return cut_open_shape_in_n_sections_with_overlap(shape, no_paths, overlap)
    else:
        return [shape]

### closed shapes

def __triangle_area(P1, P2, P3):
    return (P3[1] - P1[1]) * (P2[0] - P1[0]) - (P3[0] - P1[0]) * (P2[1] - P1[1])

def ___triangle_counter_clockwise(P1, P2, P3):
    return __triangle_area(P1, P2, P3) > 0

def find_diagonal(shape):
    """ returns a tuple with two indices giving a valid diagonal of a shape"""
    q = 0
    n = len(shape)
    P = shape.tolist()
    Pq = P[q]
    for i in range(1, n):
        if P[i].x < Pq.x:
            q = i
    p = (q - 1) % n
    r = (q + 1) % n
    
    Pp = P[p]
    Pr = P[r]
    
    ear = True
    s = p
    for i in range(n):
        Ps = P[s]
        Pi = P[i]
        if i <= p and i != q and i != r and point_in_triangle(Pi, Pp, Pq, Pr):
            ear = False
            if __triangle_area(Pi, Pr, Pp) > __triangle_area(Ps, Pr, Pp):
                s = i
    if ear:
        return (p, r)
    else:
        return (q, s)

    
    
def __edges_cross_line(P1, P2, points):
    # check if line ends between points cross
    # rechte = Ax + By - C = 0
    A1 = P2[1] - P1[1]
    B1 = -P2[0] + P1[0]
    C1 = - (P1[1] * B1 + P1[0] * A1)

    begin2 = points
    end2 = roll(points, 1, 0)
    A2 = end2[:, 1] - begin2[:, 1]
    B2 = -end2[:, 0] + begin2[:, 0]
    C2 = - (begin2[:, 1] * B2 + begin2[:, 0] * A2)

    return (((A1 * begin2[:, 0] + B1 * begin2[:, 1] + C1) * (A1 * end2[:, 0] + B1 * end2[:, 1] + C1) < 0) *
                    ((A2 * P1[0] + B2 * P1[1] + C2) * (A2 * P2[0] + B2 * P2[1] + C2) < 0)).any()



def find_opposite_diagonal(shape):
    """ returns a tuple with two indices giving a the most opposite valid diagonal of a shape"""
    L = len(shape)
    P = shape.points
    for roll_index in range(L / 2):
        Pp = P[0]
        for offset in range(0, L / 2 - 2):
            q = (L / 2 + offset) % L
            Pq = P[q] # hopeful target point
            if not __edges_cross_line(Pp, Pq, P) and shape.encloses((0.5 * (Pp[0] + Pq[0]), 0.5 * (Pp[1] + Pq[1]))):
                return (roll_index, (q + roll_index) % L)
            if not offset == 0:
                q = (L / 2 + offset) % L
                Pq = P[q] # hopeful target point
                if not __edges_cross_line(Pp, Pq, P) and P.encloses((0.5 * (Pp[0] + Pq[0]), 0.5 * (Pp[1] + Pq[1]))):
                    return (roll_index, (q + roll_index) % L)
            P = roll(P, -1, 0)
   
    
def cut_closed_shape_in_sections(shape, max_n_o_points):
    """ cuts a closed shape in shapes which do not contain more than a given number of points 
        returns a list of shapes """
    S = Shape(shape).remove_identicals()
    if len(S) < max_n_o_points: 
        return [S]
    # find a valid diagonal
    diagonal = find_opposite_diagonal(shape)
    shapes = S.cut_in_two(diagonal[0], diagonal[1])
    return (cut_closed_shape_in_sections(shapes[0], max_n_o_points) + 
            cut_closed_shape_in_sections(shapes[0], max_n_o_points))
    
            