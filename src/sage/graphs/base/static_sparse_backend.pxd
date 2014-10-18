from c_graph cimport CGraph
from static_sparse_graph cimport short_digraph, ushort
from c_graph import CGraphBackend

include 'sage/ext/stdsage.pxi'

cdef class StaticSparseCGraph(CGraph):
    cdef short_digraph g
    cdef short_digraph g_rev
    cdef bint _directed

    cpdef list verts(self)
    cpdef int out_degree(self, int u)
    cpdef int in_degree(self, int u)
