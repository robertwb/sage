include "../ext/cdefs.pxi"
include "../libs/flint/fmpz.pxi"
include "../libs/flint/fmpz_poly.pxi"

import sage.structure.element
cimport sage.structure.element
from sage.structure.element cimport AlgebraElement, RingElement, ModuleElement, Element
from sage.categories.morphism cimport Morphism

cdef class QuaternionAlgebraElement_abstract(AlgebraElement):
    cdef _do_print(self, x,y,z,w)
    cpdef conjugate(self)
    cpdef reduced_norm(self)
    cpdef reduced_trace(self)

cdef class QuaternionAlgebraElement_generic(QuaternionAlgebraElement_abstract):
    cdef object x, y, z, w, d, a, b
        # we will assume that our element has the representation
        # x + yi + zj + wk, where i^2 = a, j^2 = b

cdef class QuaternionAlgebraElement_number_field(QuaternionAlgebraElement_abstract):
    cdef fmpz_poly_t x, y, z, w, a, b, modulus
    cdef mpz_t d
    cdef inline canonicalize(self)

cdef class QuaternionAlgebraElement_rational_field(QuaternionAlgebraElement_abstract):
    cdef mpz_t x, y, z, w, a, b, d
    cdef inline canonicalize(self)
