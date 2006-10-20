include "../ext/cdefs.pxi"
include "../ext/interrupt.pxi"


cimport matrix_integer

cdef class Matrix_integer_dense(matrix_integer.Matrix_integer):
    cdef mpz_t *_entries
    cdef mpz_t **_matrix
    cdef mpz_t tmp
    cdef size_t _nrows, _ncols
    cdef object _pivots
    cdef int mpz_height(self, mpz_t height) except -1

    cdef void _zero_out_matrix(self)
