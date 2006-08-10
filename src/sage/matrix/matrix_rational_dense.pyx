"""
Dense matrices over the rational field.

This is a compiled implementation of dense matrix algebra over small
prime finite fields and the rational numbers, which is used mainly
internally by other classes.

TODO:
    -- do one big allocation instead of lots of small ones.
"""

#*****************************************************************************
#       Copyright (C) 2004,2005,2006 William Stein <wstein@ucsd.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.misc import verbose, get_verbose

include "../ext/gmp.pxi"
include "../ext/interrupt.pxi"

cimport matrix_field
import matrix_field

cimport sage.ext.rational
import  sage.ext.rational


cdef class Matrix_rational_dense(matrix_field.Matrix_field):
    """
    Matrix over the rational numbers.
    """
    def __new__(self, parent, object entries=None, construct=False):
        cdef int i, nrows, ncols
        self.initialized = 0
        if isinstance(entries, str) and entries == LEAVE_UNINITIALIZED:
            self.matrix = <mpq_t **>0
            return
        nrows = parent.nrows()
        ncols = parent.ncols()
        self.matrix = <mpq_t **> PyMem_Malloc(sizeof(mpq_t*)*nrows)
        if self.matrix == <mpq_t**> 0:
            raise MemoryError, "Error allocating matrix."
        for i from 0 <= i < nrows:
            self.matrix[i] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*ncols)
            if self.matrix[i] == <mpq_t *> 0:
                raise MemoryError, "Error allocating matrix."

    def __init__(self, parent, object entries=None, construct=False):
        cdef int n, i, j, k, r, base, nrows, ncols
        cdef mpq_t *v

        matrix_field.Matrix_field.__init__(self, parent)

        nrows = parent.nrows()
        ncols = parent.ncols()
        self._nrows = nrows
        self._ncols = ncols
        self.__pivots = None
        base = 10
        if isinstance(entries, str):
            if entries == LEAVE_UNINITIALIZED:
                return
            elif construct:
                base = 32
                entries = entries.split(' ')

        if isinstance(entries, sage.ext.rational.Rational):
            if entries != 0 and nrows != ncols:
                raise TypeError, "scalar matrix must be square"
            s = str(entries)
            mpq_init(self.tmp)
            r = mpq_set_str(self.tmp, s, 0)
            if r == -1:
                raise TypeError, "Invalid rational number %s"%entries[k]
            mpq_canonicalize(self.tmp)
            _sig_on
            for i from 0 <= i < nrows:
                v = self.matrix[i]
                for j from 0 <= j < ncols:
                    mpq_init(v[j])
                    if i == j:
                        mpq_set(v[j], self.tmp)
                        k = k + 1
                    else:
                        mpq_set_si(v[j], 0, 1)
            _sig_off
            self.initialized = 1
            return

        if nrows*ncols != 0:
            if entries != None and len(entries) != nrows*ncols:
                raise IndexError, "The vector of entries has length %s but should have length %s"%(len(entries), nrows*ncols)

        _sig_on
        k = 0
        for i from 0 <= i < nrows:
            v = self.matrix[i]
            for j from 0 <= j < ncols:
                mpq_init(v[j])
                if entries != None:
                    # TODO: If entries[k] is a rational,
                    # this should be WAY faster.  (Also see above)
                    s = str(entries[k])
                    r = mpq_set_str(v[j], s, base)
                    if r == -1:
                        _sig_off
                        raise TypeError, "Invalid rational number %s"%entries[k]
                    mpq_canonicalize(v[j])
                    k = k + 1
                else:
                    mpq_set_si(v[j],0, 1)
        _sig_off
        self.initialized = 1

    def nrows(self):
        return self._nrows

    def ncols(self):
        return self._ncols

    def __reduce__(self):
        import sage.matrix.reduce

        cdef int i, j, len_so_far, m, n
        cdef char *a
        cdef char *s, *t, *tmp

        if self._nrows == 0 or self._ncols == 0:
            entries = ''
        else:
            n = self._nrows*self._ncols*10
            s = <char*> PyMem_Malloc(n * sizeof(char))
            t = s
            len_so_far = 0

            _sig_on
            for i from 0 <= i < self._nrows:
                for j from 0 <= j < self._ncols:
                    m = mpz_sizeinbase (mpq_numref(self.matrix[i][j]), 32) + \
                        mpz_sizeinbase (mpq_denref(self.matrix[i][j]), 32) + 3
                    if len_so_far + m + 1 >= n:
                        # copy to new string with double the size
                        n = 2*n + m + 1
                        tmp = <char*> PyMem_Malloc(n * sizeof(char))
                        strcpy(tmp, s)
                        PyMem_Free(s)
                        s = tmp
                        t = s + len_so_far
                    #endif
                    mpq_get_str(t, 32, self.matrix[i][j])
                    m = strlen(t)
                    len_so_far = len_so_far + m + 1
                    t = t + m
                    t[0] = <char>32
                    t[1] = <char>0
                    t = t + 1
            _sig_off
            entries = str(s)[:-1]
            free(s)

        return sage.matrix.reduce.make_Matrix_rational_dense, \
               (self.parent(), entries)


    def __cmp__(self, other):
        if not isinstance(other, Matrix_rational_dense):
            return -1
        raise NotImplementedError

    def __setitem__(self, ij, x):
        i, j = ij
        if self.matrix == <mpq_t **>0:
            raise RuntimeError, "Matrix has not yet been initialized!"
        if i < 0 or i >= self._nrows or j < 0 or j >= self._ncols:
            raise IndexError, "Invalid index."
        s = str(x)
        mpq_set_str(self.matrix[i][j], s, 0)

    def __getitem__(self, ij):
        i, j = ij
        if i < 0 or i >= self._nrows or j < 0 or j >= self._ncols:
            raise IndexError, "Invalid index."
        cdef sage.ext.rational.Rational x
        x = sage.ext.rational.Rational()
        x.set_from_mpq(self.matrix[i][j])
        return x

    cdef set_matrix(Matrix_rational_dense self, mpq_t **m):
        if self.matrix != <mpq_t **> 0:
            raise RuntimeError, "Only set matrix of uninitialized matrix."
        self.matrix = m
        self.initialized = 1

    def  __dealloc__(self):
        cdef int i, j
        if self.matrix == <mpq_t **> 0:
            return
        for i from 0 <= i < self._nrows:
            if self.matrix[i] != <mpq_t *> 0:
                for j from 0 <= j < self._ncols:
                    if self.initialized:
                        mpq_clear(self.matrix[i][j])
                PyMem_Free(self.matrix[i])
        PyMem_Free(self.matrix)

    def _mul_(Matrix_rational_dense self, Matrix_rational_dense other):
        if self._ncols != other._nrows:
            raise IndexError, "Number of columns of self must equal number of rows of other."

        cdef int i, j, k, nr, nc, snc
        cdef mpq_t *v
        cdef mpq_t s, z
        nr = self._nrows
        nc = other._ncols
        snc = self._ncols

        cdef Matrix_rational_dense M
        M = Matrix_rational_dense(self.parent(), LEAVE_UNINITIALIZED)

        cdef mpq_t **m
        m = <mpq_t **> PyMem_Malloc(sizeof(mpq_t*)*nr)
        if m == <mpq_t**> 0:
            raise MemoryError, "Error allocating matrix"

        mpq_init(s); mpq_init(z)

        _sig_on
        for i from 0 <= i < nr:
            m[i] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*nc)
            if m[i] == <mpq_t*> 0:
                mpq_clear(s); mpq_clear(z)
                _sig_off
                raise MemoryError, "Error allocating matrix"
            for j from 0 <= j < nc:
                mpq_set_si(s,0,1)   # set s = 0
                v = self.matrix[i]
                for k from 0 <= k < snc:
                    mpq_mul(z, v[k], other.matrix[k][j])
                    mpq_add(s, s, z)
                mpq_init(m[i][j])
                mpq_set(m[i][j], s)
        _sig_off
        M.set_matrix(m)
        mpq_clear(s); mpq_clear(z)
        return M

    def _add_(Matrix_rational_dense self, Matrix_rational_dense other):
        if self._ncols != other._ncols:
            raise IndexError, "Number of columns of self must equal number of rows of other."
        if self._nrows != other._nrows:
            raise IndexError, "Number of columns of self must equal number of rows of other."

        cdef int i, j, nr, nc
        nr = self._nrows
        nc = other._ncols

        cdef Matrix_rational_dense M
        M = Matrix_rational_dense(nr, nc, LEAVE_UNINITIALIZED)

        cdef mpq_t **m
        m = <mpq_t **> PyMem_Malloc(sizeof(mpq_t*)*nr)
        if m == <mpq_t**> 0:
            raise MemoryError, "Error allocating matrix"

        _sig_on
        for i from 0 <= i < nr:
            m[i] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*nc)
            if m[i] == <mpq_t*> 0:
                _sig_off
                raise MemoryError, "Error allocating matrix"
            for j from 0 <= j < nc:
                mpq_init(m[i][j])
                mpq_add(m[i][j], self.matrix[i][j], other.matrix[i][j])
        _sig_off
        M.set_matrix(m)
        return M

    def transpose(self):
        """
        Returns the transpose of self.
        """
        cdef int i, j
        cdef Matrix_rational_dense M

        M = Matrix_rational_dense(self._ncols, self._nrows, entries=LEAVE_UNINITIALIZED)
        cdef mpq_t **m
        m = <mpq_t **> PyMem_Malloc(sizeof(mpq_t*)*self._ncols)
        if m == <mpq_t**> 0:
            raise MemoryError, "Error allocating matrix"

        _sig_on
        for i from 0 <= i < self._ncols:
            m[i] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*self._nrows)
            if m[i] == <mpq_t*> 0:
                raise MemoryError, "Error allocating matrix"
            for j from 0 <= j < self._nrows:
                mpq_init(m[i][j])
                mpq_set(m[i][j], self.matrix[j][i])
        _sig_off
        M.set_matrix(m)
        return M

    def matrix_from_rows(self, rows):
        """
        Return the submatrix formed from the given rows.

        INPUT:
            rows -- list of int's

        OUTPUT:
            matrix created from the rows with given indexes
        """
        cdef int i, j, k, nc, nr
        cdef Matrix_rational_dense M

        if not isinstance(rows, list):
            raise TypeError, "rows (=%s) must be a list"%rows
        nr = len(rows)
        if nr == 0:
            return Matrix_rational_dense(0, self._ncols)
        nc = self._ncols
        v = []
        for i in rows:
            v.append(int(i))
        rows = v
        if min(rows) < 0 or max(rows) >= self._nrows:
            raise IndexError, "invalid row indexes; rows don't exist"

        M = Matrix_rational_dense(self.parent(), entries=LEAVE_UNINITIALIZED)
        cdef mpq_t **m
        m = <mpq_t **> PyMem_Malloc(sizeof(mpq_t*)*nr)
        if m == <mpq_t**> 0:
            raise MemoryError, "Error allocating matrix"

        for i from 0 <= i < nr:
            m[i] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*nc)
            if m[i] == <mpq_t*> 0:
                raise MemoryError, "Error allocating matrix"
            k = rows[i]
            for j from 0 <= j < nc:
                mpq_init(m[i][j])
                mpq_set(m[i][j], self.matrix[k][j])

        M.set_matrix(m)
        return M



    def iterates(self, v, int n):
        """
        Let A be this matrix.   Return a matrix with rows
        $$
           v, Av, A^2v, ..., A^(n-1)v.
        $$
        """
        cdef int i, j, k, nr, nc
        cdef mpq_t s, z
        nr = n
        nc = self._ncols

        if self._nrows != self._ncols:
            raise ArithmeticError, "matrix must be square"
        if not isinstance(v, list):
            raise TypeError, "v must be a list"
        if len(v) != self._nrows:
            raise ArithmeticError, "incompatible matrix vector multiple"

        cdef Matrix_rational_dense M
        M = Matrix_rational_dense(self.parent(), LEAVE_UNINITIALIZED)

        cdef mpq_t **m
        m = <mpq_t **> PyMem_Malloc(sizeof(mpq_t*)*nr)
        if m == <mpq_t**> 0:
            raise MemoryError, "Error allocating matrix"
        m[0] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*nc)
        if m[0] == <mpq_t*> 0:
            mpq_clear(s); mpq_clear(z)
            raise MemoryError, "Error allocating matrix"
        mpq_init(self.tmp)
        for j from 0 <= j < nc:
            string = str(v[j])
            r = mpq_set_str(self.tmp, string, 0)
            if r == -1:
                raise TypeError, "Invalid rational number %s"%v[i]
            mpq_init(m[0][j])
            mpq_set(m[0][j], self.tmp)

        mpq_init(s)
        mpq_init(z)
        for i from 1 <= i < nr:
            m[i] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*nc)
            if m[i] == <mpq_t*> 0:
                raise MemoryError, "Error allocating matrix"
            for j from 0 <= j < nc:
                mpq_set_si(s,0,1)  # set s = 0
                for k from 0 <= k < self._nrows:
                    mpq_mul(z, m[i-1][k], self.matrix[k][j])
                    mpq_add(s, s, z)
                mpq_init(m[i][j])
                mpq_set(m[i][j], s)
        M.set_matrix(m)
        mpq_clear(s); mpq_clear(z)
        return M


    def scalar_multiple(self, d):
        """
        Return the product self*d, as a new matrix.
        """
        cdef int i, j, nr, nc
        nr = self._nrows
        nc = self._ncols

        cdef mpq_t x
        mpq_init(x)
        s = str(d)
        r = mpq_set_str(x, s, 0)
        if r == -1:
            raise TypeError, "Invalid rational number %s"%entries[k]
        cdef Matrix_rational_dense M
        M = Matrix_rational_dense(self.parent(), LEAVE_UNINITIALIZED)

        cdef mpq_t **m
        m = <mpq_t **> PyMem_Malloc(sizeof(mpq_t*)*nr)
        if m == <mpq_t**> 0:
            raise MemoryError, "Error allocating matrix"

        _sig_on
        for i from 0 <= i < nr:
            m[i] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*nc)
            if m[i] == <mpq_t*> 0:
                mpq_clear(x)
                _sig_off
                raise MemoryError, "Error allocating matrix"
            for j from 0 <= j < nc:
                mpq_init(m[i][j])
                mpq_mul(m[i][j], self.matrix[i][j], x)
        _sig_off
        M.set_matrix(m)
        mpq_clear(x)
        return M

    def copy(self):
        cdef int i, j, nr, nc
        nr = self._nrows; nc = self._ncols

        cdef Matrix_rational_dense M
        M = Matrix_rational_dense(self.parent(), LEAVE_UNINITIALIZED)
        cdef mpq_t **m
        m = <mpq_t **> PyMem_Malloc(sizeof(mpq_t*)*nr)
        if m == <mpq_t**> 0:
            raise MemoryError, "Error allocating matrix"

        for i from 0 <= i < nr:
            m[i] = <mpq_t *> PyMem_Malloc(sizeof(mpq_t)*nc)
            if m[i] == <mpq_t*> 0:
                raise MemoryError, "Error allocating matrix"
            for j from 0 <= j < nc:
                mpq_init(m[i][j])
                mpq_set(m[i][j], self.matrix[i][j])

        M.set_matrix(m)
        return M

    def number_nonzero(self):
        cdef int i, j, n
        cdef mpq_t *v
        n = 0
        _sig_on
        for i from 0 <= i < self._nrows:
            v = self.matrix[i]
            for j from 0 <= j < self._ncols:
                if mpq_sgn(v[j]):   # if nonzero
                    n = n + 1
        _sig_off
        return n

    def list(self, int base=0):
        cdef int i, j
        cdef mpq_t *r
        cdef object v
        cdef sage.ext.rational.Rational x

        v = []
        _sig_on
        for i from 0 <= i < self._nrows:
            r = self.matrix[i]
            for j from 0 <= j < self._ncols:
                x = sage.ext.rational.Rational()
                x.set_from_mpq(r[j])
                v.append(x)
        _sig_off
        return v

    def echelon_gauss_in_place(self):
        """
        Changes self into echelon form.
        """
        cdef int start_row, c, r, nr, nc, i
        cdef mpq_t **m
        cdef mpq_t a_inverse, minus_b

        mpq_init(a_inverse)
        mpq_init(minus_b)
        start_row = 0
        m = self.matrix
        nr = self._nrows
        nc = self._ncols
        self.__pivots = []

        for c from 0 <= c < nc:
            if PyErr_CheckSignals(): raise KeyboardInterrupt
            for r from start_row <= r < nr:
                if mpq_sgn(m[r][c]):
                    self.__pivots.append(c)
                    mpq_inv(a_inverse,m[r][c])
                    self.scale_row(r, a_inverse, c)
                    self.swap_rows(r, start_row)
                    for i from 0 <= i < nr:
                        if i != start_row:
                            if mpq_sgn(m[i][c]):
                                mpq_neg(minus_b, m[i][c])
                                self.add_multiple_of_row(start_row, minus_b, i, c)
                    start_row = start_row + 1
                    break
        mpq_clear(a_inverse)
        mpq_clear(minus_b)

    def rank(self):
        """
        Return the rank found during the last echelon operation on self.
        Of course if self is changed, and the echelon form of self is not
        recomputed, then the rank could be incorrect.
        """
        if self.__pivots == None:
            raise ArithmeticError, "Echelon form has not yet been computed."
        return len(self.__pivots)

    def pivots(self):
        """
        Return the pivots found during the last echelon operation on self.
        Of course if self is changed, and the echelon form of self is not
        recomputed, then the pivots could be incorrect.
        """
        if self.__pivots == None:
            raise ArithmeticError, "Echelon form has not yet been computed."
        return self.__pivots

    def _set_pivots(self, v):
        self.__pivots = v

    def hessenberg_form(self):
        if not self.is_immutable():
            raise ValueError, "matrix must be mutable, since hessenberg form changes it"
        if self._nrows != self._ncols:
            raise ArithmeticError, "Matrix must be square to compute Hessenberg form."

        cdef int n
        n = self._nrows

        cdef mpq_t **h
        h = self.matrix

        cdef int i, j, m, p, r
        cdef mpq_t t, t_inv, u, neg_u
        mpq_init(t)
        mpq_init(t_inv)
        mpq_init(u)
        mpq_init(neg_u)

        for m from 1 <= m < n-1:
            if PyErr_CheckSignals(): raise KeyboardInterrupt
            # Search for a nonzero entry in column m-1
            i = -1
            for r from m+1 <= r < n:
                if mpq_sgn(h[r][m-1]):
                     i = r
                     break

            if i != -1:
                 # Found a nonzero entry in column m-1 that is strictly
                 # below row m.  Now set i to be the first nonzero position >=
                 # m in column m-1.
                 if mpq_sgn(h[m][m-1]): i = m
                 mpq_set(t,h[i][m-1])
                 mpq_inv(t_inv, t)
                 if i > m:
                     self.swap_rows(i,m)
                     self.swap_columns(i,m)

                 # Now the nonzero entry in position (m,m-1) is t.
                 # Use t to clear the entries in column m-1 below m.
                 for j from m+1 <= j < n:
                     if mpq_sgn(h[j][m-1]):
                         mpq_mul(u,h[j][m-1], t_inv)
                         mpq_neg(neg_u, u)
                         self.add_multiple_of_row(m, neg_u, j, 0)  # h[j] -= u*h[m]
                         # To maintain charpoly, do the corresponding
                         # column operation, which doesn't mess up the
                         # matrix, since it only changes column m, and
                         # we're only worried about column m-1 right
                         # now.  Add u*column_j to column_m.
                         self.add_multiple_of_column(j, u, m, 0)
                 # end for
            # end if
        # end for
        mpq_clear(t)
        mpq_clear(t_inv)
        mpq_clear(u)
        mpq_clear(neg_u)

    cdef scale_row(self, int row, mpq_t multiple, int start_col):
        cdef int r
        cdef mpq_t* v

        r = row*self._ncols
        v = self.matrix[row]
        for i from start_col <= i < self._ncols:
            mpq_mul(v[i], v[i], multiple)

    cdef add_multiple_of_row(self, int row_from, mpq_t multiple,
                            int row_to, int start_col):
        cdef int i
        cdef mpq_t *v_from, *v_to
        cdef mpq_t prod, x

        mpq_init(prod); mpq_init(x)
        v_from = self.matrix[row_from]
        v_to = self.matrix[row_to]
        for i from start_col <= i < self._ncols:
            mpq_mul(prod, multiple, v_from[i])
            mpq_add(x, prod, v_to[i])
            mpq_set(v_to[i], x)   # v_to[i] <-- multipe*v_from[i] + v_to[i]

        mpq_clear(prod); mpq_clear(x)

    def set_row_to_multiple_of_row(self, int row_to, int row_from, sage.ext.rational.Rational multiple):
        """
        Set row row_to equal to multiple times row row_from.
        """
        cdef int i
        cdef mpq_t *v_from, *v_to

        if row_from < 0 or row_from >= self._nrows:
            raise IndexError, "row_from is %s but must be >= 0 and < %s"%(row_from, self._nrows)
        if row_to < 0 or row_to >= self._nrows:
            raise IndexError, "row_to is %s but must be >= 0 and < %s"%(row_to, self._nrows)

        v_from = self.matrix[row_from]
        v_to = self.matrix[row_to]
        for i from 0 <= i < self._ncols:
            mpq_mul(v_to[i], multiple.value, v_from[i])


    cdef add_multiple_of_column(self, int col_from, mpq_t multiple,
                               int col_to, int start_row):
        cdef int i, p, nr
        cdef mpq_t **m
        cdef mpq_t prod, x

        mpq_init(prod); mpq_init(x)
        m = self.matrix
        nr = self._nrows
        for i from start_row <= i < self._nrows:
            mpq_mul(prod, multiple, m[i][col_from])
            mpq_add(x, m[i][col_to], prod)
            mpq_set(m[i][col_to], x)
        mpq_clear(prod); mpq_clear(x)

    cdef swap_rows(self, int row1, int row2):
        cdef mpq_t* temp
        temp = self.matrix[row1]
        self.matrix[row1] = self.matrix[row2]
        self.matrix[row2] = temp

    cdef swap_columns(self, int col1, int col2):
        cdef int i, nr
        cdef mpq_t **m
        cdef mpq_t t

        mpq_init(t)
        m = self.matrix
        nr = self._nrows
        for i from 0 <= i < self._nrows:
            mpq_set(t, m[i][col1])
            mpq_set(m[i][col1], m[i][col2])
            mpq_set(m[i][col2], t)
        mpq_clear(t)

    cdef int mpz_denom(self, mpz_t d) except -1:
        cdef mpz_t y
        mpz_set_si(d,1)
        mpz_init(y)
        cdef int i, j
        _sig_on
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                mpq_get_den(y,self.matrix[i][j])
                mpz_lcm(d, d, y)
        _sig_off
        mpz_clear(y)
        return 0

    def denom(self):
        cdef mpz_t d
        mpz_init(d)
        self.mpz_denom(d)
        dl = mpz_to_long(d)
        mpz_clear(d)
        return dl

    cdef int mpz_height(self, mpz_t height) except -1:
        cdef mpz_t x, h
        mpz_init(x)
        mpz_init_set_si(h, 0)
        cdef int i, j
        _sig_on
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                mpq_get_num(x,self.matrix[i][j])
                mpz_abs(x, x)
                if mpz_cmp(h,x) < 0:
                    mpz_set(h,x)
                mpq_get_den(x,self.matrix[i][j])
                mpz_abs(x, x)
                if mpz_cmp(h,x) < 0:
                    mpz_set(h,x)
        _sig_off
        mpz_set(height, h)
        mpz_clear(h)
        mpz_clear(x)
        return 0

    def height(self):
        cdef mpz_t h
        mpz_init(h)
        self.mpz_height(h)
        a = mpz_to_long(h)
        mpz_clear(h)
        return a

    def prod_of_row_sums(self, cols):
        r"""
        Calculate the product of all row sums of a submatrix of $A$ for a
        list of selected columns \code{cols}.

        This is used for the computation of matrix permanents.
        """
        cdef int row, c, n, t

        n = len(cols)
        cdef int* v
        v = <int*> PyMem_Malloc(n * sizeof(int))
        for c from 0 <= c < n:
            t = cols[c]
            if t < 0 or t >= self._ncols:
                PyMem_Free(v)
                raise IndexError, "invalid column index (= %s)"%t
            v[c] = t

        cdef mpq_t pr, z
        mpq_init(pr)
        mpq_init(z)

        mpq_set_si(pr, 1, 1)
        for row from 0 <= row < self._nrows:
            mpq_set_si(z, 0, 1)
            for c from 0 <= c < n:
                mpq_add(z, z, self.matrix[row][v[c]])
            mpq_mul(pr, pr, z)

        cdef sage.ext.rational.Rational x
        x = sage.ext.rational.Rational()
        x.set_from_mpq(pr)
        mpq_clear(pr)
        mpq_clear(z)
        PyMem_Free(v)
        return x

    def _clear_denom(self):
        """
        INPUT:
            self -- a matrix
        OUTPU:
            self, D, if D=denominator is 1
            D*self, D if D > 1.

        Thus returns a copy of self only if D > 1.
        """
        cdef mpz_t d
        mpz_init(d)
        self.mpz_denom(d)
        if mpz_cmp_si(d,1) == 0:
            mpz_clear(d)
            return self, sage.ext.rational.Rational(1)
        cdef Matrix_rational_dense A
        A = self.copy()
        cdef mpq_t denom
        mpq_init(denom)
        mpq_set_z(denom, d)
        A._rescale(denom)
        mpz_clear(d)
        mpq_clear(denom)

        cdef sage.ext.rational.Rational x
        x = sage.ext.rational.Rational()
        x.set_from_mpq(denom)
        return A, x

    cdef int _rescale(self, mpq_t a) except -1:
        cdef int i, j
        _sig_on
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                mpq_mul(self.matrix[i][j], self.matrix[i][j], a)
        _sig_off


    def echelon(self, alg="modular", height_guess=None):
        """
        echelon(self, alg="modular", height_guess=None):

        Returns echelon form of self, without modifying self.
        """
        if alg=="modular":
            return self.echelon_modular(height_guess=height_guess)
        elif alg=="gauss":
            A = self.copy()
            A.echelon_gauss()
            return A
        else:
            raise ValueError, "%s is not one of the allowed algorithms (modular, gauss)"%alg

    def echelon_modular(self, height_guess=None):
        """
        echelon_modular(self, height_guess=None):

        Returns echelon form of self, without modifying self.  Uses a
        multi-modular method.

        ALGORITHM:
        The following is a modular algorithm for computing the echelon
        form.  Define the height of a matrix to be the max of the
        absolute values of the entries.

        Input: Matrix A with n columns (this).

        0. Rescale input matrix A to have integer entries.  This does
           not change echelon form and makes reduction modulo many
           primes significantly easier if there were denominators.
           Henceforth we assume A has integer entries.

        1. Let c be a guess for the height of the echelon form.  E.g.,
           c=1000, since matrix is sparse and application is modular
           symbols.

        2. Let M = n * c * H(A) + 1,
           where n is the number of columns of A.

        3. List primes p_1, p_2, ..., such that the product of
           the p_i is at least M.

        4. Try to compute the rational reconstruction CRT echelon form
           of A mod the product of the p_i.  Throw away those A mod p_i
           whose pivot sequence is not >= all other pivot sequences of
           A mod p_j.
           If rational reconstruction fails, compute 1 more echelon
           forms mod the next prime, and attempt again.  Let E be this
           matrix.

        5. Compute the denominator d of E.
           Try to prove that result is correct by checking that

                 H(d*E) < (prod of reduction primes)/(ncols*H(A)),

           where H denotes the height.   If this fails, do step 4 with
           a few more primes.

           (TODO: Possible idea for optimization: When doing the rational_recon lift,
            keep track of the lcm d of denominators found so far, and given
                             a (mod m)
            first check to see if a*d lifts to an integer with abs <= m/2.
            If so, no nded to do rational recon.  This should be the case
            for most a after a while, and should save substantial time!!!!)
        """
        B, _ = self._clear_denom()
        hA = B.height()
        if height_guess is None:
            height_guess = (2*hA)**(self._ncols/2+1)
        verbose("height_guess=%s"%height_guess)
        M = self._ncols * height_guess * hA  +  1
        p = START_PRIME
        X = []
        best_pivots = []
        prod = 1
        while True:
            while prod < M:
                verbose("p=%s"%p)
                A = B.matrix_modint(p)
                A.echelon()
                if self._nrows == self._ncols and len(A.pivots()) == self._ncols:
                    # special case -- the echelon form must be the identity matrix.
                    return Matrix_rational_identity(self._nrows)

                c = cmp_pivots(best_pivots, A.pivots())
                if c <= 0:
                    best_pivots = A.pivots()
                    X.append(A)
                    prod = prod * p
                else:
                    if get_verbose() > 1:
                        verbose("Excluding this prime (bad pivots).", level=2)
                    pass   # do not save A since it is bad.
                #p = previous_probab_prime_int(p)
                p = next_probab_prime_int(p)

            Y = []
            prod = 1
            # We recompute product, since may drop bad matrices
            for i from 0 <= i < len(X):
                # Here best_pivots is the best collection
                # of pivots found during any echelon form computation.
                # Here cmp_pivots returns a number <= 0 if
                # X[i].pivots() is at least as good.
                if cmp_pivots(best_pivots, X[i].pivots()) <= 0:
                    # append a good matrix to the list Y.
                    Y.append(X[i])
                    # multiply the product of the good primes by this good prime
                    prod = prod * X[i].prime()
            try:
                t = verbose("start rr")
                E = Matrix_rational_using_crt_and_rr(Y)
                verbose("done",t)
            except ValueError:
                for i from 0 <= i < 10:
                    M = M * START_PRIME
                verbose("(Failed to compute rational reconstruction -- redoing with several more primes", level=2)
                continue
            d = E.denom()
            Es = E.scalar_multiple(d)
            hdE = (Es).height()
            if hdE * hA * self._ncols < prod:
                self.__pivots = best_pivots
                E._set_pivots(list(best_pivots))
                return E
            for i from 0 <= i < 3:
                M = M * START_PRIME

    def multiply_multi_modular(self, Matrix_rational_dense right):
        """
        Multiply this matrix by right using a multimodular algorithm
        and return the result.
        """
        if self._ncols != right._nrows:
            raise IndexError, "Number of columns of self must equal number of rows of right."

        A, A_denom = self._clear_denom()
        B, B_denom = right._clear_denom()
        bound = 2 * A.height() * B.height() * A.ncols()
        p = 0
        X = []
        prod = 1
        while prod < bound:
            verbose('prod = %s, bound = %s'%(prod, bound))
            if p == 0:
                p = START_PRIME
            else:
                #p = previous_probab_prime_int(p)
                p = next_probab_prime_int(p)
            t = verbose("p=%s"%p)
            A_modp = A.matrix_modint(p)
            B_modp = B.matrix_modint(p)
            t = verbose("done reducing", t)
            C_modp = A_modp.strassen(B_modp)
            t = verbose("done multiplying", t)
            X.append(C_modp)
            prod = prod * p
        t = verbose("now doing CRT")
        C = Matrix_rational_CRT(X)
        verbose("finished CRT", t)
        return C

cdef object mpz_to_long(mpz_t x):
    return long(mpz_to_str(x))

# TODO -- update
#def Matrix_rational_random(nrows, ncols, bound):
#    x = []
#    for i in range(nrows*ncols):
#        x.append(gmp_randrange(-bound, bound))
#    return Matrix_rational_dense(nrows, ncols, x)

## def Matrix_rational_identity(n):
##     x = []
##     new_row = True
##     for i in range(n):
##         x.append(1)
##         for j in range(n):
##             x.append(0)
##     I = Matrix_rational(n,n, x[:n*n])
##     I._set_pivots(range(n))
##     return I
