#
#*****************************************************************************
#      Copyright (C) 2006 - 2007 Robert L. Miller <rlmillster@gmail.com>
#
# Distributed  under  the  terms  of  the  GNU  General  Public  License (GPL)
#                         http://www.gnu.org/licenses/
#*****************************************************************************

include '../ext/cdefs.pxi'

# The class OrbitPartition is a quasi-sorted union-find tree with path
# compression. This type is used for Theta, which keeps track of the orbit
# partition of that part of the automorphism group thus far encountered. The
# only operations required for this are taking unions, and finding which cell
# a vertex lives in. Unions place the minimal of the two roots as the new
# root, so that the cell representatives are minimal. Finds compress the paths
# they traverse, so that all the vertices visited point directly to the
# parent. Since the tree is unbalanced, the worst case find time is linear.
#
# (TODO)
# Important note: the following are probably suboptimal:
#  1. The use of the variable OP at all- the involved functions should just be
#     functions of _gamma. (see graph_isom.pyx:1176:32)
#  2. If instead, roots are chosen to be those of the larger tree during union
#     by keeping track of rank, this together with path compression yield a
#     running time of O(alpha(n)) for union and find operations, where alpha
#     is the inverse Ackerman function [2].
#       We can have this complexity, which is practically constant, without
#     making any sacrifices. Along with keeping track of rank, we could do the
#     same for minimal representative and size, whose operations would be
#     essentially identical.
# These have not yet been implemented since this structure is not the
# bottleneck of the loop.
#
# The class itself is simply an integer array, where each entry is the parent
# of that cell. A value of -1 indicates a null pointer, i.e. a root.

cdef class OrbitPartition:
    cdef int *elements
    cdef int *sizes

    cdef int _find(self, int x)
    cdef void _union_find(self, int a, int b)
    cdef void _union_roots(self, int a, int b)
    cdef int _is_finer_than(self, OrbitPartition other, int n)
    cdef void _vee_with(self, OrbitPartition other, int n)
    cdef int _is_min_cell_rep(self, int i)
    cdef int _is_fixed(self, int i)

# The class PartitionStack is our main way of investigating the search tree
# T(G, Pi). At any given time, a PartitionStack contains data for each k from
# 0 <= k < n. This is the bound for the depth of the tree, and thus of the
# stack. The structure keeps track of neither k nor n itself, however the last
# entry of self.levels is -1. Otherwise, self.levels[i] indicates at which k
# the separation between i and i+1 is made.

cdef class PartitionStack:
    cdef int *entries
    cdef int *levels

    cdef int _is_discrete(self, int k)
    cdef int _num_cells(self, int k)
    cdef int _is_min_cell_rep(self, int i, int k)
    cdef int _is_fixed(self, int i, int k)
    cdef int _sat_225(self, int k, int n)
    cdef int _split_vertex(self, int v, int k)
    cdef void _percolate(self, int start, int end)
    cdef int _sort_by_function(self, int start, int *degrees, int k, int n)
    cdef void _clear(self, int k)
    cdef int _refine_by_square_matrix(self, int k, int *alpha, int n, int **G, int dig)
    cdef int _degree_square_matrix(self, int **G, int v, int W, int k)
    cdef int _degree_inv_square_matrix(self, int **G, int v, int W, int k)
    cdef int _first_smallest_nontrivial(self, int *W, int k, int n)
    cdef void _get_permutation_from(self, PartitionStack zeta, int *gamma)
    cdef _enumerate_graph_from_discrete(self, int **G, int n)
