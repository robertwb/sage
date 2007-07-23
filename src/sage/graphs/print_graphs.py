##
## print-graphs.sage
##
## Craig Citro
## 07_06_12
##
## Copying old scheme print-graph methods over to SAGE
##

#*****************************************************************************
#                        Copyright (C) 2007 Craig Citro
#
# Distributed  under  the  terms  of  the  GNU  General  Public  License (GPL)
#                         http://www.gnu.org/licenses/
#*****************************************************************************


import time
from math import floor
from copy import copy

def print_header_ps(s):
    s += "%% --- Auto-generated PostScript ---\n\n\n"
    s += "%% Generated on: \n"
    s += "%%" + time.asctime() + "\n"
    return s

def print_header_eps(s, xmin, ymin, xmax, ymax):

    s += "%!PS-Adobe-3.0 EPSF-3.0\n"
    s += "%" + "%" + "BoundingBox: %s %s %s %s \n"%(xmin, ymin, xmax, ymax)

    return s

def print_functions(s):
    s +=  "/point %% input: x y\n"
    s += "{ moveto\n"
    s +=  "  gsave\n"
    s +=  "  currentpoint translate\n"
    s += "  0 0 2 0 360 arc\n"
    s += "  fill\n"
    s += "  grestore\n"
    s += "  } def\n\n\n"
    s += "/edge %% input: x1 y1 x2 y2\n"
    s += "{ moveto\n"
    s += "  lineto\n"
    s += "  stroke\n"
    s += "  } def\n\n"

    return s

def print_graph_ps(vert_ls, edge_iter, pos_dict):

    pos_dict = copy(pos_dict) # assumption: all pos's are -1 <= ... <= 1

    s = ""

    s = print_header_ps(s)
    s = print_functions(s)

    for v in vert_ls:
        x,y = pos_dict[v]
        pos_dict[v] = int(floor(50*x))+50, int(floor(50*y))+50
        x,y = pos_dict[v]
        s += "%s %s point\n"%(x,y)

    for (u, v, l) in edge_iter:
        ux, uy = pos_dict[u]
        vx, vy = pos_dict[v]
        s += "%s %s %s %s edge\n"%(ux, uy, vx, vy)

    return s


def print_graph_eps(vert_ls, edge_iter, pos_dict):

    pos_dict = copy(pos_dict) # assumption: all pos's are -1 <= ... <= 1

    t = ""
    s = ""

    xmin = 0
    ymin = 0

    xmax = -1
    ymax = -1

#    n = len(vert_ls)

    for v in vert_ls:
        x,y = pos_dict[v]
        pos_dict[v] = int(floor(50*x))+50, int(floor(50*y))+50
        x,y = pos_dict[v]
        s += "%s %s point\n"%(x,y)

    for (u, v, l) in edge_iter:
        ux, uy = pos_dict[u]
        vx, vy = pos_dict[v]
        s += "%s %s %s %s edge\n"%(ux, uy, vx, vy)

    t = print_header_eps(t, 0, 0, 100, 100)
    t = print_functions(t)

    return t + s
