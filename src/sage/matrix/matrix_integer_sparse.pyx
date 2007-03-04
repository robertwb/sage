"""
Sparse integer matrices.

AUTHORS:
    -- William Stein (2007-02-21)
    -- Soroosh Yazdani (2007-02-21)
"""

##############################################################################
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
##############################################################################

include '../modules/vector_integer_sparse_h.pxi'
include '../modules/vector_integer_sparse_c.pxi'
include '../ext/stdsage.pxi'

from sage.rings.integer  cimport Integer
from matrix cimport Matrix

import sage.matrix.matrix_space

from sage.rings.integer_ring import ZZ
from sage.rings.integer_mod_ring import IntegerModRing


cdef class Matrix_integer_sparse(matrix_sparse.Matrix_sparse):

    ########################################################################
    # LEVEL 1 functionality
    #   * __new__
    #   * __dealloc__
    #   * __init__
    #   * set_unsafe
    #   * get_unsafe
    #   * __richcmp__    -- always the same
    #   * __hash__       -- alway simple
    ########################################################################
    def __new__(self, parent, entries, copy, coerce):
        self._initialized = False
        # set the parent, nrows, ncols, etc.
        matrix_sparse.Matrix_sparse.__init__(self, parent)

        self._matrix = <mpz_vector*> sage_malloc(parent.nrows()*sizeof(mpz_vector))
        if self._matrix == NULL:
            raise MemoryError, "error allocating sparse matrix"
        # initialize the rows
        for i from 0 <= i < parent.nrows():
            init_mpz_vector(&self._matrix[i], self._ncols, 0)
        # record that rows have been initialized
        self._initialized = True


    def __dealloc__(self):
        cdef Py_ssize_t i
        if self._initialized:
            for i from 0 <= i < self._nrows:
                clear_mpz_vector(&self._matrix[i])
        sage_free(self._matrix)

    def __init__(self, parent, entries, copy, coerce):
        """
        Create a sparse matrix over the integers.

        INPUT:
            parent -- a matrix space
            entries -- * a Python list of triples (i,j,x), where 0 <= i < nrows,
                         0 <= j < ncols, and x is coercible to an int.  The i,j
                         entry of self is set to x.  The x's can be 0.
                       * Alternatively, entries can be a list of *all* the entries
                         of the sparse matrix (so they would be mostly 0).
            copy -- ignored
            coerce -- ignored
        """
        cdef Py_ssize_t i, j, k
        cdef Integer z
        cdef void** X

        # set the parent, nrows, ncols, etc.
        matrix_sparse.Matrix_sparse.__init__(self, parent)

        # fill in entries in the dict case
        if isinstance(entries, dict):
            R = self.base_ring()
            for ij, x in entries.iteritems():
                z = R(x)
                if z != 0:
                    i, j = ij  # nothing better to do since this is user input, which may be bogus.
                    if i < 0 or j < 0 or i >= self._nrows or j >= self._ncols:
                        raise IndexError, "invalid entries list"
                    mpz_vector_set_entry(&self._matrix[i], j, z.value)

        elif isinstance(entries, list):

            # Dense input format -- fill in entries
            if len(entries) != self._nrows * self._ncols:
                raise TypeError, "list of entries must be a dictionary of (i,j):x or a dense list of n * m elements"
            seq = PySequence_Fast(entries,"expected a list")
            X = PySequence_Fast_ITEMS(seq)
            k = 0
            R = self.base_ring()
            # Get fast access to the entries list.
            for i from 0 <= i < self._nrows:
                for  j from 0 <= j < self._ncols:
                    z = R(<object>X[k])
                    if z != 0:
                        mpz_vector_set_entry(&self._matrix[i], j, z.value)
                    k = k + 1

        else:

            # fill in entries in the scalar case
            z = Integer(entries)
            if z == 0:
                return
            if self._nrows != self._ncols:
                raise TypeError, "matrix must be square to initialize with a scalar."
            for i from 0 <= i < self._nrows:
                mpz_vector_set_entry(&self._matrix[i], i, z.value)


    cdef set_unsafe(self, Py_ssize_t i, Py_ssize_t j, x):
        mpz_vector_set_entry(&self._matrix[i], j, (<Integer> x).value)

    cdef get_unsafe(self, Py_ssize_t i, Py_ssize_t j):
        cdef Integer x
        x = Integer()
        mpz_vector_get_entry(&x.value, &self._matrix[i], j)
        return x

    def __richcmp__(Matrix self, right, int op):  # always need for mysterious reasons.
        return self._richcmp(right, op)

    def __hash__(self):
        return self._hash()


    ########################################################################
    # LEVEL 2 functionality
    #   * def _pickle
    #   * def _unpickle
    #   * cdef _add_c_impl
    #   * cdef _sub_c_impl
    #   * cdef _mul_c_impl
    #   * cdef _cmp_c_impl
    #   * __neg__
    #   * __invert__
    #   * __copy__
    #   * _multiply_classical
    #   * _matrix_times_matrix_c_impl
    #   * _list -- list of underlying elements (need not be a copy)
    #   * _dict -- sparse dictionary of underlying elements (need not be a copy)
    ########################################################################
    # def _pickle(self):
    # def _unpickle(self, data, int version):   # use version >= 0
    # cdef ModuleElement _add_c_impl(self, ModuleElement right):
    # cdef _mul_c_impl(self, Matrix right):
    # cdef int _cmp_c_impl(self, Matrix right) except -2:
    # def __neg__(self):
    # def __invert__(self):
    # def __copy__(self):
    # def _multiply_classical(left, matrix.Matrix _right):
    # def _list(self):
    # def _dict(self):


    ########################################################################
    # LEVEL 3 functionality (Optional)
    #    * cdef _sub_c_impl
    #    * __deepcopy__
    #    * __invert__
    #    * Matrix windows -- only if you need strassen for that base
    #    * Other functions (list them here):
    ########################################################################

    def _mod_int(self, modulus):
        return self._mod_int_c(modulus)

    cdef _mod_int_c(self, mod_int p):
        raise NotImplementedError

    def rational_reconstruction(self, N):
        """
        Use rational reconstruction to lift self to a matrix over the
        rational numbers (if possible), where we view self as a matrix
        modulo N.
        """
        import misc
        return misc.matrix_integer_sparse_rational_reconstruction(self, N)
