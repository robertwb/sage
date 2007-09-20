include "decl.pxi"
include "../../ext/cdefs.pxi"

from sage.libs.ntl.ntl_ZZ_pContext cimport ntl_ZZ_pContext_class

cdef class ntl_ZZ_pX:
    cdef ZZ_pX_c x
    cdef ntl_ZZ_pContext_class c
    cdef void setitem_from_int(ntl_ZZ_pX self, long i, int value)
    cdef int getitem_as_int(ntl_ZZ_pX self, long i)
    cdef ntl_ZZ_pX _new(self)
