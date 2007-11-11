include "../../libs/ntl/decl.pxi"

from sage.rings.padics.padic_ext_element cimport pAdicExtElement
from sage.rings.padics.pow_computer_ext cimport PowComputer_ZZ_pX
from sage.libs.ntl.ntl_ZZ_pContext cimport ntl_ZZ_pContext_class

cdef class pAdicZZpXElement(pAdicExtElement):
    cdef PowComputer_ZZ_pX prime_pow
    cdef int _set_from_ZZ_pX_c(self, ZZ_pX_c poly, ntl_ZZ_pContext_class ctx) except -1
