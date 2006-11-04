"""
Dense matrices over the rational field.
"""

##############################################################################
#       Copyright (C) 2004,2005,2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
##############################################################################

include "../ext/interrupt.pxi"
include "../ext/stdsage.pxi"
include "../ext/cdefs.pxi"

from sage.rings.rational cimport Rational
from matrix cimport Matrix
import sage.structure.coerce
from sage.rings.integer cimport Integer

cdef class Matrix_rational_dense(matrix_dense.Matrix_dense):

    ########################################################################
    # LEVEL 1 functionality
    # x * __new__
    # x * __dealloc__
    # x * __init__
    # x * set_unsafe
    # x * get_unsafe
    # x * cdef _pickle
    # x * cdef _unpickle
    ########################################################################
    def __new__(self, parent, entries, copy, coerce):
        """
        Create and allocate memory for the matrix.

        Unlike over matrix_integer_dense, mpq_init() is called (as there is no mpq_init_set function).

        INPUT:
            parent, entries, coerce, copy -- as for __init__.

        EXAMPLES:
            sage: from sage.matrix.matrix_rational_dense import Matrix_rational_dense
            sage: a = Matrix_rational_dense.__new__(Matrix_rational_dense, Mat(ZZ,3), 0,0,0)
            sage: type(a)
            <type 'sage.matrix.matrix_rational_dense.Matrix_rational_dense'>

        WARNING: This is for internal use only, or if you really know what you're doing.
        """
        matrix_dense.Matrix_dense.__init__(self, parent)

        cdef Py_ssize_t i, k

        self._entries = <mpq_t *> sage_malloc(sizeof(mpq_t)*(self._nrows * self._ncols))
        if self._entries == <mpq_t *> 0:
            raise MemoryError, "out of memory allocating a matrix"

        self._matrix =  <mpq_t **> sage_malloc(sizeof(mpq_t*) * self._ncols)
        if self._matrix == <mpq_t**> 0:
            raise MemoryError, "out of memory allocating a matrix"

        # store pointers to the starts of the rows
        k = 0
        for i from 0 <= i < self._nrows:
            self._matrix[i] = self._entries + k
            k = k + self._ncols

        for i from 0 <= i < self._nrows * self._ncols:
            mpq_init(self._entries[i])

    def  __dealloc__(self):
        cdef Py_ssize_t i
        for i from 0 <= i < self._nrows * self._ncols:
            mpq_clear(self._entries[i])
        sage_free(self._entries)
        sage_free(self._matrix)

    def __init__(self, parent, entries=0, coerce=True, copy=True):

        cdef Py_ssize_t i
        cdef Rational z

        if not isinstance(entries, list):
            try:
                entries = list(entries)
                is_list = 1
            except TypeError:
                try:
                    # Try to coerce entries to a scalar (an integer)
                    z = Rational(entries)
                    is_list = 0
                except TypeError:
                    raise TypeError, "entries must be coercible to a list or integer"
        else:
            is_list = 1

        if is_list:
            if len(entries) != self._nrows * self._ncols:
                raise TypeError, "entries has the wrong length"

            _sig_on
            if coerce:
                for i from 0 <= i < self._nrows * self._ncols:
                    # TODO: Should use an unsafe un-bounds-checked array access here.
                    z = Rational(entries[i])
                    mpq_set(self._entries[i], z.value)
            else:
                for i from 0 <= i < self._nrows * self._ncols:
                    # TODO: Should use an unsafe un-bounds-checked array access here.
                    z = entries[i]
                    mpq_set(self._entries[i], z.value)
            _sig_off

        else:
            # is it a scalar
            _sig_on
            for i from 0 <= i < self._nrows * self._ncols:
                mpq_init(self._entries[i])
            _sig_off

            if not z.is_zero():
                if self._nrows != self._ncols:
                    raise TypeError, "nonzero scalar matrix must be square"
                for i from 0 <= i < self._nrows:
                    mpq_set(self._entries[i*i+i], z.value)


    cdef set_unsafe(self, Py_ssize_t i, Py_ssize_t j, value):
        cdef Rational y
        y = value
        mpq_set(self._matrix[i][j], y.value)


    cdef get_unsafe(self, Py_ssize_t i, Py_ssize_t j):
        cdef Rational x
        x = Rational.__new__(Rational)
        mpq_set(x.value, self._matrix[i][j])
        return x

    cdef _pickle(self):
        return self._pickle_version0(), 0

    cdef _unpickle(self, data, int version):
        if version == 0:
            self._unpickle_version0(data)
        else:
            raise RuntimeError, "unknown matrix version (=%s)"%version

    cdef _pickle_version0(self):
        cdef Py_ssize_t i, j, len_so_far, m, n
        cdef char *a
        cdef char *s, *t, *tmp

        if self._nrows == 0 or self._ncols == 0:
            data = ''
        else:
            n = self._nrows*self._ncols*10
            s = <char*> sage_malloc(n * sizeof(char))
            t = s
            len_so_far = 0

            _sig_on
            for i from 0 <= i < self._nrows:
                for j from 0 <= j < self._ncols:
                    m = mpz_sizeinbase (mpq_numref(self._matrix[i][j]), 32) + \
                        mpz_sizeinbase (mpq_denref(self._matrix[i][j]), 32) + 3
                    if len_so_far + m + 1 >= n:
                        # copy to new string with double the size
                        n = 2*n + m + 1
                        tmp = <char*> sage_malloc(n * sizeof(char))
                        strcpy(tmp, s)
                        sage_free(s)
                        s = tmp
                        t = s + len_so_far
                    #endif
                    mpq_get_str(t, 32, self._matrix[i][j])
                    m = strlen(t)
                    len_so_far = len_so_far + m + 1
                    t = t + m
                    t[0] = <char>32
                    t[1] = <char>0
                    t = t + 1
            _sig_off
            data = str(s)[:-1]
            free(s)
        return data

    cdef _unpickle_version0(self, data):
        cdef Py_ssize_t i, n
        data = data.split()
        n = self._nrows * self._ncols
        if len(data) != n:
            raise RuntimeError, "invalid pickle data."
        for i from 0 <= i < n:
            s = data[i]
            if mpq_set_str(self._entries[i], s, 32):
                raise RuntimeError, "invalid pickle data"

    def __richcmp__(Matrix self, right, int op):
        return self._richcmp(right, op)

    ########################################################################
    # LEVEL 2 functionality
    #   * cdef _add_c_impl
    #   * cdef _mul_c_impl
    #   * cdef _cmp_c_impl
    #   * __neg__
    #   * __invert__
    #   * __copy__
    #   * _multiply_classical
    #   * _list -- list of underlying elements (need not be a copy)
    #   * _dict -- sparse dictionary of underlying elements (need not be a copy)
    ########################################################################
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
    #    * _multiply_classical
    #    * Matrix windows -- only if you need strassen for that base
    #    * Other functions (list them here):
    ########################################################################
    def denom(self):
        """
        Return the denominator of this matrix.

        OUTPUT:
            -- SAGE Integer

        EXAMPLES:
            sage: b = matrix(QQ,2,range(6)); b[0,0]=-5007/293; b
            [-5007/293         1         2]
            [        3         4         5]
            sage: b.denom()
            293
        """
        cdef Integer z
        z = Integer.__new__(Integer)
        self.mpz_denom(z.value)
        return z

    cdef int mpz_denom(self, mpz_t d) except -1:
        cdef mpz_t y
        mpz_set_si(d,1)
        mpz_init(y)
        cdef int i, j
        _sig_on
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                mpq_get_den(y,self._matrix[i][j])
                mpz_lcm(d, d, y)
        _sig_off
        mpz_clear(y)
        return 0

    cdef int mpz_height(self, mpz_t height) except -1:
        cdef mpz_t x, h
        mpz_init(x)
        mpz_init_set_si(h, 0)
        cdef int i, j
        _sig_on
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                mpq_get_num(x,self._matrix[i][j])
                mpz_abs(x, x)
                if mpz_cmp(h,x) < 0:
                    mpz_set(h,x)
                mpq_get_den(x,self._matrix[i][j])
                mpz_abs(x, x)
                if mpz_cmp(h,x) < 0:
                    mpz_set(h,x)
        _sig_off
        mpz_set(height, h)
        mpz_clear(h)
        mpz_clear(x)
        return 0

    def height(self):
        """
        Return the height of this matrix, which is the least common
        multiple of all numerators and denominators of elements of
        this matrix.

        OUTPUT:
            -- SAGE Integer

        EXAMPLES:
            sage: b = matrix(QQ,2,range(6)); b[0,0]=-5007/293; b
            [-5007/293         1         2]
            [        3         4         5]
            sage: b.height()
            5007
        """
        cdef Integer z
        z = Integer.__new__(Integer)
        self.mpz_height(z.value)
        return z

    cdef int _rescale(self, mpq_t a) except -1:
        cdef int i, j
        _sig_on
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                mpq_mul(self._matrix[i][j], self._matrix[i][j], a)
        _sig_off


###########################
