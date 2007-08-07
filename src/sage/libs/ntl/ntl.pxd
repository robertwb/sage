# here's all the C/C++ definitions need to make NTL go from pyrex
include "decl.pxi"

cdef class ntl_ZZ:
    cdef ZZ_c* x
    cdef set(self, void *y)
    cdef public int get_as_int(ntl_ZZ self)
    cdef public void set_from_int(ntl_ZZ self, int value)

cdef class ntl_ZZX:
    cdef ZZX_c* x
    cdef set(self, void *y)
    cdef void setitem_from_int(ntl_ZZX self, long i, int value)
    cdef int getitem_as_int(ntl_ZZX self, long i)

cdef extern from "ntl_wrap.h":
    cdef int ZZ_p_to_int(ZZ_p_c* x)
    cdef ZZ_p_c* int_to_ZZ_p(int value)
    cdef void ZZ_p_set_from_int(ZZ_p_c* x, int value)

cdef class ntl_ZZ_p:
    cdef ZZ_p_c* x
    cdef set(self, void *y)
    cdef public int get_as_int(ntl_ZZ_p self)
    cdef public void set_from_int(ntl_ZZ_p self, int value)

cdef extern from "ntl_wrap.h":
    cdef void ZZ_pX_setitem_from_int(ZZ_pX_c* x, long i, int value)
    cdef int ZZ_pX_getitem_as_int(ZZ_pX_c* x, long i)

cdef class ntl_ZZ_pX:
    cdef ZZ_pX_c* x
    cdef set(self, void *y)
    cdef void setitem_from_int(ntl_ZZ_pX self, long i, int value)
    cdef int getitem_as_int(ntl_ZZ_pX self, long i)

cdef class ntl_mat_ZZ:
    cdef mat_ZZ_c* x
    cdef long __nrows, __ncols

cdef class ntl_GF2X:
    cdef GF2X_c* gf2x_x
    cdef set(self,void *y)

cdef class ntl_GF2E(ntl_GF2X):
    cdef GF2E_c* gf2e_x
    cdef set(self,void *y)

cdef class ntl_mat_GF2E:
    cdef mat_GF2E_c* x
    cdef long __nrows, __ncols

cdef class ntl_GF2EX:
    cdef GF2EX_c* x
    cdef set(self,void *y)
