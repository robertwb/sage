# choose: dense or sparse

cimport matrix_dense

from sage.libs.m4ri cimport *

cdef class Matrix_mod2_dense(matrix_dense.Matrix_dense):
    cdef mzd_t *_entries
    cdef object _one
    cdef object _zero

    cdef set_unsafe_int(self, Py_ssize_t i, Py_ssize_t j, int value)

    cpdef Matrix_mod2_dense _multiply_m4rm(Matrix_mod2_dense self, Matrix_mod2_dense right, int k)
    cpdef Matrix_mod2_dense _multiply_strassen(Matrix_mod2_dense self, Matrix_mod2_dense right, int cutoff)

    # For conversion to other systems
    cpdef _export_as_string(self)
