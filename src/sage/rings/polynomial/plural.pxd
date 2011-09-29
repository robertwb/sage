include "../../libs/singular/singular-cdefs.pxi"

from sage.rings.ring cimport Ring
from sage.structure.element cimport RingElement, Element
from sage.structure.parent cimport Parent
from sage.libs.singular.function cimport RingWrap
from sage.rings.polynomial.multi_polynomial_libsingular cimport MPolynomialRing_libsingular


cdef class NCPolynomialRing_plural(Ring):
    cdef object __ngens
    cdef object _c
    cdef object _d
    cdef object __term_order
    cdef public object _has_singular
    cdef public object _magma_gens, _magma_cache
#    cdef _richcmp_c_impl(left, Parent right, int op)
    cdef int _cmp_c_impl(left, Parent right) except -2

    cdef ring *_ring
#    cdef NCPolynomial_plural _one_element
#    cdef NCPolynomial_plural _zero_element

    cdef public object _relations,_relations_commutative
    pass

cdef class ExteriorAlgebra_plural(NCPolynomialRing_plural):
    pass

cdef class NCPolynomial_plural(RingElement):
    cdef poly *_poly
    cpdef _repr_short_(self)
    cdef long _hash_c(self)
    cpdef is_constant(self)
#    cpdef _homogenize(self, int var)

cdef NCPolynomial_plural new_NCP(NCPolynomialRing_plural parent, poly *juice)

cpdef MPolynomialRing_libsingular new_CRing(RingWrap rw, base_ring)
cpdef NCPolynomialRing_plural new_NRing(RingWrap rw, base_ring)
