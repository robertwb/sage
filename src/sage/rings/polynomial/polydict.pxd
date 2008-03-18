include '../../ext/cdefs.pxi'

cdef class ETuple:
    cdef size_t _length
    cdef size_t _nonzero
    cdef int *_data

    cpdef ETuple eadd(ETuple self, ETuple self)
    cdef ETuple _new(ETuple self)
