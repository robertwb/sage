include "../ext/cdefs.pxi"
include "../ext/interrupt.pxi"

cimport matrix_pid_dense

cdef class Matrix_integer_dense(matrix_pid_dense.Matrix_pid_dense):
    cdef char _initialized
    cdef mpz_t *_entries
    cdef mpz_t **_matrix
    cdef object _pivots
    cdef int mpz_height(self, mpz_t height) except -1

    cdef void _zero_out_matrix(self)
    cdef _new_unitialized_matrix(self, size_t nrows, size_t ncols)
