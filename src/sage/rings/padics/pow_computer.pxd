include "../../ext/cdefs.pxi"

from sage.structure.sage_object cimport SageObject
from sage.rings.integer cimport Integer

cdef class PowComputer_class(SageObject):
    cdef Integer prime
    cdef bint in_field
    cdef int _initialized

    cdef unsigned long cache_limit
    cdef unsigned long prec_cap

    cdef mpz_t temp_m

    cdef Integer pow_Integer(self, unsigned long n)
    cdef mpz_t* pow_mpz_t_top(self)
    cdef mpz_t* pow_mpz_t_tmp(self, unsigned long n)

cdef class PowComputer_base(PowComputer_class):
    cdef mpz_t* small_powers
    cdef mpz_t top_power
    cdef object __weakref__