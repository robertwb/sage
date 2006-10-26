include "../ext/cdefs.pxi"

cimport matrix_generic

cdef class Matrix_dense(matrix_generic.Matrix):
    cdef object __entries
    cdef int* _row_indices

cdef class MatrixWindow:
    cdef Matrix_dense _matrix
    cdef int _row
    cdef int _col
    cdef int _nrows
    cdef int _ncols
