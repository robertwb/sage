include "../../ext/cdefs.pxi"
include "../../libs/ntl/decl.pxi"

from sage.rings.integer cimport Integer
from sage.rings.rational cimport Rational
from sage.structure.element cimport Element, FieldElement, RingElement, ModuleElement


from number_field_element cimport NumberFieldElement, NumberFieldElement_absolute

cdef class NumberFieldElement_quadratic(NumberFieldElement_absolute):
    # (a + b sqrt(disc)) / denom
    cdef mpz_t a, b, denom
    cdef Integer disc
    cdef NumberFieldElement conjugate_c(self)
    cdef bint is_sqrt_disc(self)
