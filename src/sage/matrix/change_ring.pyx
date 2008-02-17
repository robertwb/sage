"""
Functions for changing the base ring of matrices quickly.
"""

from matrix_space import MatrixSpace
from matrix_real_double_dense cimport Matrix_real_double_dense
from matrix_integer_dense cimport Matrix_integer_dense

from sage.rings.real_double import RDF

include "../ext/cdefs.pxi"
include "../ext/interrupt.pxi"
include "../gsl/gsl.pxi"

def integer_to_real_double_dense(Matrix_integer_dense A):
    """
    Fast conversion of a matrix over the integers to a matrix with
    real double entries.

    INPUT:
        A -- a dense matrix over the integers

    OUTPUT:
        -- a dense real double matrix

    EXAMPLES:
        sage: a = matrix(ZZ,2,3,[-2,-5,3,4,8,1030339830489349908])
        sage: a.change_ring(RDF)
        [             -2.0              -5.0               3.0]
        [              4.0               8.0 1.03033983049e+18]
        sage: import sage.matrix.change_ring
        sage: sage.matrix.change_ring.integer_to_real_double_dense(a)
        [             -2.0              -5.0               3.0]
        [              4.0               8.0 1.03033983049e+18]
    """
    cdef Py_ssize_t i, j
    cdef Matrix_real_double_dense M
    S = MatrixSpace(RDF, A._nrows, A._ncols, sparse=False)
    M = Matrix_real_double_dense.__new__(Matrix_real_double_dense,
                                         S, None, None, None)
    for i from 0 <= i < A._nrows:
        for j from 0 <= j < A._ncols:
            gsl_matrix_set(M._matrix, i, j, mpz_get_d(A._matrix[i][j]))
    return M
