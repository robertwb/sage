include "cdefs.pxi"
cimport _element
import _element

cdef class Integer(_element.EuclideanDomainElement):
    cdef mpz_t value
    cdef int cmp(self, Integer x)
    cdef void set_from_mpz(Integer self, mpz_t value)
    cdef mpz_t* get_value(self)
    cdef object _pari
