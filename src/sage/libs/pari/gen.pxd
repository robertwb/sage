from .types cimport *
cimport cython


cdef class gen_auto:
    cdef GEN g
    cdef pari_sp b
    cdef dict refers_to

@cython.final
cdef class gen(gen_auto):
    pass

cpdef gen objtogen(s)
