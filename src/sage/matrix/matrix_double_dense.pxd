cimport matrix_dense
cimport sage.ext.numpy as cnumpy

cdef class Matrix_double_dense(matrix_dense.Matrix_dense):
    cdef object _numpy_dtype
    cdef cnumpy.NPY_TYPES _numpy_dtypeint
    cdef object _python_dtype
    cdef object _sage_dtype
    cdef object _sage_vector_dtype
    cdef cnumpy.ndarray _L, _U, _P
    cdef int _LU_valid
    cdef Matrix_double_dense _new(self, int nrows=*, int ncols=*)
    cdef _c_compute_LU(self)
    cdef cnumpy.ndarray _matrix_numpy
