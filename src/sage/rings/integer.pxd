include "../ext/cdefs.pxi"

import sage.structure.element
cimport sage.structure.element
from sage.structure.element cimport EuclideanDomainElement, RingElement

cdef class Integer(EuclideanDomainElement):
    cdef mpz_t value

    cdef int cmp(self, Integer x)
    cdef void set_from_mpz(self, mpz_t value)
    cdef mpz_t* get_value(self)
    cdef object _pari
    cdef RingElement _add_sibling_cdef(self, RingElement right)
