"""
Dense matrice over GF(2) based on code by Gregory Bard.

This implementation uses a packed representation of boolean matrices
and provides a quite fast echelon form implemenation (M4RI). For some
solutions LinBox is used.

AUTHOR: Martin Albrecht <malb@informatik.uni-bremen.de>

EXAMPLES:
    sage: a = matrix(GF(2),3,range(9),sparse=False); a
    [0 1 0]
    [1 0 1]
    [0 1 0]
    sage: a.rank()
    2
    sage: type(a)
    <type 'sage.matrix.matrix_mod2_dense.Matrix_mod2_dense'>
    sage: a[0,0] = 1
    sage: a.rank()
    3
    sage: parent(a)
    Full MatrixSpace of 3 by 3 dense matrices over Finite Field of size 2

    sage: a^2
    [0 1 1]
    [1 0 0]
    [1 0 1]
    sage: a+a
    [0 0 0]
    [0 0 0]
    [0 0 0]

    sage: b = a.new_matrix(2,3,range(6)); b
    [0 1 0]
    [1 0 1]

    sage: a*b
    Traceback (most recent call last):
    ...
    TypeError: incompatible dimensions
    sage: b*a
    [1 0 1]
    [1 0 0]

    sage: a == loads(dumps(a))
    True
    sage: b == loads(dumps(b))
    True

    sage: a.echelonize(); a
    [1 0 0]
    [0 1 0]
    [0 0 1]
    sage: b.echelonize(); b
    [1 0 1]
    [0 1 0]

TODO:
   - make linbox frontend and use it
     - charpoly ?
     - minpoly ?
     - rank ?
   - make Matrix_modn_frontend and use it (?)
"""

##############################################################################
#       Copyright (C) 2004,2005,2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
##############################################################################

include "../ext/interrupt.pxi"
include "../ext/cdefs.pxi"
include '../ext/stdsage.pxi'
include '../ext/random.pxi'

cimport matrix_dense
from sage.structure.element cimport Matrix
from sage.structure.element cimport ModuleElement, Element

from sage.misc.functional import log

from sage.misc.misc import verbose, get_verbose, cputime

from sage.libs.linbox.linbox cimport Linbox_mod2_dense
cdef Linbox_mod2_dense linbox
linbox = Linbox_mod2_dense()

cdef object called

cdef void init_m4ri():
    global called
    if called is None:
        # TODO: remove packingmask
        setupPackingMasks()
        buildAllCodes()
        called = True

init_m4ri()

cdef class Matrix_mod2_dense(matrix_dense.Matrix_dense):   # dense or sparse
    """

    """
    ########################################################################
    # LEVEL 1 functionality
    ########################################################################
    def __new__(self, parent, entries, copy, coerce, alloc=True):
        """
        Creates a new dense matrix over GF(2).

        INPUT:
            parent -- MatrixSpace (always)
            entries -- ignored
            copy -- ignored
            coerce -- ignored
            alloc -- if True a zero matrix is allocated (default:True)

        """
        matrix_dense.Matrix_dense.__init__(self, parent)

        if alloc:
            self._entries = createPackedMatrix(self._nrows, self._ncols)

        # cache elements
        self._zero = self._base_ring(0)
        self._one = self._base_ring(1)

    def __dealloc__(self):
        if self._entries:
            destroyPackedMatrix(self._entries)
            self._entries = NULL

    def __init__(self, parent, entries, copy, coerce):
        """
        Dense matrix over GF(2) constructor.

        INPUT:
            parent -- MatrixSpace.
            entries -- may be list or 0 or 1
            copy -- ignored, elements are always copied
            coerce -- ignored, elements are always coerced to ints % 2

        EXAMPLES:
            sage: type(random_matrix(GF(2),2,2))
            <type 'sage.matrix.matrix_mod2_dense.Matrix_mod2_dense'>

            sage: Matrix(GF(2),3,3,1)
            [1 0 0]
            [0 1 0]
            [0 0 1]

            sage: Matrix(GF(2),2,2,[1,1,1,0])
            [1 1]
            [1 0]

            sage: Matrix(GF(2),2,2,4)
            [0 0]
            [0 0]
        """
        cdef int i,j,e

        # scalar ?
        if not isinstance(entries, list):
            if int(entries) % 2 == 1:
                makeIdentityPacked(self._entries)
            return

        # all entries are given as a long list
        if len(entries) != self._nrows * self._ncols:
            raise IndexError, "The vector of entries has the wrong length."

        k = 0
        R = self.base_ring()

        cdef PyObject** w
        w = FAST_SEQ_UNSAFE(entries)

        for i from 0 <= i < self._nrows:
            if PyErr_CheckSignals(): raise KeyboardInterrupt
            for j from 0 <= j < self._ncols:
                writePackedCell(self._entries,i,j, int(<object> w[k]) % 2)
                k = k + 1

    def __richcmp__(Matrix self, right, int op):  # always need for mysterious reasons.
        return self._richcmp(right, op)

    def __hash__(self):
        return self._hash()

    cdef set_unsafe(self, Py_ssize_t i, Py_ssize_t j, value):
        writePackedCell(self._entries, i, j, int(value))

    cdef get_unsafe(self, Py_ssize_t i, Py_ssize_t j):
        if readPackedCell(self._entries, i, j):
            return self._one
        else:
            return self._zero


    def str(self):
        cdef int i,j
        s = []
        for i from 0 <= i < self._nrows:
            rl = []
            for j from 0 <= j < self._ncols:
                rl.append(str(readPackedCell(self._entries,i,j)))
            s.append( " ".join(rl) )
        return "[" + "]\n[".join(s) + "]"

    ########################################################################
    # LEVEL 2 functionality
    #   * def _pickle
    #   * def _unpickle
    #   * cdef _mul_c_impl
    #   * cdef _cmp_c_impl
    #   * _list -- list of underlying elements (need not be a copy)
    #   * _dict -- sparse dictionary of underlying elements (need not be a copy)
    ########################################################################
    # def _pickle(self):
    # def _unpickle(self, data, int version):   # use version >= 0

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        """
        Matrix addition.

        INPUT:
            right -- matrix of dimension self.nrows() x self.ncols()

        EXAMPLES:
            sage: A = random_matrix(GF(2),10,10)
            sage: A + A == Matrix(GF(2),10,10,0)
            True

        """
        cdef Matrix_mod2_dense A
        A = Matrix_mod2_dense.__new__(Matrix_mod2_dense, self._parent, 0, 0, 0, alloc=False)

        A._entries = addPacked(self._entries,(<Matrix_mod2_dense>right)._entries)

        return A

    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        """
        Matrix addition.

        INPUT:
            right -- matrix of dimension self.nrows() x self.ncols()

        EXAMPLES:
            sage: A = random_matrix(GF(2),10,10)
            sage: A - A == Matrix(GF(2),10,10,0)
            True
        """
        return self._add_c_impl(right)

    cdef Matrix _matrix_times_matrix_c_impl(self, Matrix right):
        """
        Matrix multiplication.

        If the dimension of the matrix is below 1000x1000 a naiv
        matrix multiplication is performed. If the dimension is larger
        LinBox's Strassen implementation is used. This uses much more
        memory but is significantly faster roughly starting at those
        sizes.

        EXAMPLES:
            sage: A = random_matrix(GF(2),200,200)
            sage: A*A == A._multiply_linbox(A)
            True

        ALGORITHM: Uses LinBox for some cases.

        """
        if get_verbose() >= 2:
            verbose('matrix multiply of %s x %s matrix by %s x %s matrix'%(
                self._nrows, self._ncols, right._nrows, right._ncols))

        if self._ncols < 1000 and right.nrows() < 1000:
             return self._multiply_classical(right)
        else:
            # uses way more RAM but is faster
             return self._multiply_linbox(right)

    def _multiply_linbox(Matrix_mod2_dense self, Matrix_mod2_dense right):
        """
        Multiply matrices using LinBox.

        INPUT:
            right -- Matrix

        EXAMPLE:
              sage: A = Matrix(GF(2), 4, 3, [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1] )
              sage: B = Matrix(GF(2), 3, 4, [0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0] )
              sage: A
              [0 0 0]
              [0 1 0]
              [0 1 1]
              [0 0 1]
              sage: B
              [0 0 1 0]
              [1 0 0 1]
              [1 1 0 0]
              sage: A._multiply_linbox(B)
              [0 0 0 0]
              [1 0 0 1]
              [0 1 0 1]
              [1 1 0 0]

        ALGORITHM: Uses LinBox

        """
        if get_verbose() >= 2:
            verbose('linbox multiply of %s x %s matrix by %s x %s matrix'%(
                self._nrows, self._ncols, right._nrows, right._ncols))
        cdef int e
        cdef Matrix_mod2_dense ans

        ans = self.new_matrix(nrows = self.nrows(), ncols = right.ncols())

        linbox.set(self._entries)

        _sig_on
        linbox.matrix_matrix_multiply(ans._entries, right._entries)
        _sig_off
        return ans

    def _multiply_classical(Matrix_mod2_dense self, Matrix_mod2_dense right):
        """
        Classical n^3 multiplication.


        EXAMPLE:
              sage: A = Matrix(GF(2), 4, 3, [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1] )
              sage: B = Matrix(GF(2), 3, 4, [0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0] )
              sage: A
              [0 0 0]
              [0 1 0]
              [0 1 1]
              [0 0 1]
              sage: B
              [0 0 1 0]
              [1 0 0 1]
              [1 1 0 0]
              sage: A._multiply_classical(B)
              [0 0 0 0]
              [1 0 0 1]
              [0 1 0 1]
              [1 1 0 0]

        """
        cdef Matrix_mod2_dense A
        A = self.new_matrix(nrows = self.nrows(), ncols = right.ncols())
        destroyPackedMatrix(A._entries)

        A._entries = matrixTimesMatrixPacked(self._entries,(<Matrix_mod2_dense>right)._entries)
        return A

    # cdef int _cmp_c_impl(self, Matrix right) except -2:

    def __neg__(self):
        """

        EXAMPLES:
            sage: A = random_matrix(GF(2),100,100)
            sage: A - A == A - -A
            True
        """
        return self.copy()

    def __invert__(self):
        """
        Inverts self using M4RI.

        If self is not invertible a ZeroDivisionError is raised.

        EXAMPLE:
              sage: A = Matrix(GF(2),3,3, [0, 0, 1, 0, 1, 1, 1, 0, 1])
              sage: MS = A.parent()
              sage: A
              [0 0 1]
              [0 1 1]
              [1 0 1]
              sage: ~A
              [1 0 1]
              [1 1 0]
              [1 0 0]
              sage: A * ~A == ~A * A == MS(1)
              True

        ALGORITHM: Uses M4RI.
        """
        cdef int k
        cdef packedmatrix *I
        cdef Matrix_mod2_dense A
        k = 8

        if self._nrows != self._ncols:
            raise ArithmeticError, "self must be a square matrix"

        I = createPackedMatrix(self._nrows,self._ncols)
        makeIdentityPacked(I)

        A = Matrix_mod2_dense.__new__(Matrix_mod2_dense, self._parent, 0, 0, 0, alloc = False)
        A._entries = invertPackedFlexRussian(self._entries, I, k)
        destroyPackedMatrix(I)

        if A._entries==NULL:
            raise ZeroDivisionError, "self is not invertible"
        else:
            return A

    def __copy__(self):
        """
        Returns a copy of self.

        EXAMPLES:
             sage: MS = MatrixSpace(GF(2),3,3)
             sage: A = MS(1)
             sage: A.copy() == A
             True
             sage: A.copy() is A
             False

             sage: A = random_matrix(GF(2),100,100)
             sage: A.copy() == A
             True
             sage: A.copy() is A
             False

             sage: A.echelonize()
             sage: A.copy() == A
             True

        """
        cdef Matrix_mod2_dense A
        cdef int width

        A = Matrix_mod2_dense.__new__(Matrix_mod2_dense, self._parent, 0, 0, 0)

        memcpy(A._entries.values, self._entries.values, (RADIX>>3) * self._entries.width * self._nrows)
        memcpy(A._entries.rowswap, self._entries.rowswap, self._nrows * sizeof(int))

        return A

    def _list(self):
        """
        Returns list of the elements of self in row major ordering.

        EXAMPLE:
            sage: A = Matrix(GF(2),2,2,[1,0,1,1])
            sage: A
            [1 0]
            [1 1]
            sage: A.list()
            [1, 0, 1, 1]

        """
        cdef int i,j
        l = []
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                if readPackedCell(self._entries,i,j):
                    l.append(self._one)
                else:
                    l.append(self._zero)
        return l

    # def _dict(self):

    ########################################################################
    # LEVEL 3 functionality (Optional)
    #    * __deepcopy__
    #    * Matrix windows -- only if you need strassen for that base
    ########################################################################

    def echelonize(self, algorithm='m4ri', cutoff=0, **kwds):
        """
        Puts self in reduced row echelon form.

        INPUT:
            self -- a mutable matrix
            algorithm -- 'm4ri' -- uses M4RI (default)
                      -- 'linbox' -- uses LinBox's Strassen algorithm
                                     (needs more RAM, slower for many examples, but
                                     asymtotically faster)
            k --  the parameter 'k' of the M4RI algorithm. It MUST be between
                  1 and 16 (inclusive). If it is not specified it will be calculated as
                  3/4 * log_2( min(nrows, ncols) ) as suggested in the M4RI paper.

        EXAMPLE:
             sage: A = random_matrix(GF(2), 10, 10)
             sage: B = A.copy(); B.echelonize() # fastest
             sage: C = A.copy(); C.echelonize(k=2) # force k
             sage: D = A.copy(); D.echelonize(algorithm='linbox') # force LinBox
             sage: E = A.copy(); E.echelonize(algorithm='classical') # force Gaussian elimination
             sage: B == C == D == E
             True

        ALGORITHM: Uses Gregory Bard's M4RI algorithm and implementation or
                   LinBox.

        """
        cdef int k, n

        x = self.fetch('in_echelon_form')
        if not x is None: return  # already known to be in echelon form

        if algorithm == 'm4ri':

            self.check_mutability()
            self.clear_cache()

            if 'k' in kwds:
                k = int(kwds['k'])

                if k<1 or k>16:
                    raise RuntimeError,"k must be between 1 and 16"
                k = round(k)
            else:
                n = min(self._nrows, self._ncols)
                k = round(min(0.75 * log(n,2), 16))

            _sig_on
            r =  simpleFourRussiansPackedFlex(self._entries, 1, k)
            _sig_off

            self.cache('in_echelon_form',True)
            self.cache('rank', r)
            self.cache('pivots', self._pivots())

        elif algorithm == 'linbox':

            self._echelonize_linbox()

        elif algorithm == 'classical':

            # for debugging purposes only, it is slow
            self._echelon_in_place_classical()
        else:
            raise ValueError, "no algorithm '%s'"%algorithm

    def _echelonize_linbox(self):
        """
        Puts self in row echelon form using LinBox.
        """
        self.check_mutability()
        self.clear_cache()

        t = verbose('calling linbox echelonize')
        _sig_on
        linbox.set(self._entries)
        r = linbox.echelonize()
        _sig_off
        verbose('done with linbox echelonize',t)

        self.cache('in_echelon_form',True)
        self.cache('rank', r)
        #self.cache('pivots', self._pivots())

    def _pivots(self):
        """
        Returns the pivot columns of self if self is in row echelon form.
        """
        if not self.fetch('in_echelon_form'):
            raise RuntimeError, "self must be in reduced row echelon form first."
        pivots = []
        cdef Py_ssize_t i, j, nc
        nc = self._ncols
        i = 0
        while i < self._nrows:
            for j from i <= j < nc:
                if readPackedCell(self._entries, i, j):
                    pivots.append(j)
                    i += 1
                    break
            if j == nc:
                break
        return pivots

    def randomize(self, density=1):
        """
        Randomize density proportion of the entries of this matrix,
        leaving the rest unchanged.

        NOTE: The random() function doesn't seem to be as random as
        expected. The lower-order bits seem to have a strong bias
        towards zero. Even stranger, if you create two 1000x1000
        matrices over GF(2) they always appear to have the same
        reduced row echelon form, i.e. they span the same space. The
        higher-order bits seem to be much more random and thus we
        shift first and mod p then.
        """

        density = float(density)
        if density == 0:
            return

        self.check_mutability()
        self.clear_cache()

        cdef int nc
        if density == 1:
            fillRandomlyPacked(self._entries)
        else:
            nc = self._ncols
            num_per_row = int(density * nc)
            _sig_on
            for i from 0 <= i < self._nrows:
                for j from 0 <= j < num_per_row:
                    k = ((random()>>16)+random())%nc # is this safe?
                    # 16-bit seems safe
                    writePackedCell(self._entries, i, j, (random()>>16) % 2)
            _sig_off


    cdef rescale_row_c(self, Py_ssize_t row, multiple, Py_ssize_t start_col):
        if (multiple%2) == 0:
            rowClearPackedOffset(self._entries, row, start_col);

##     cdef rescale_col_c(self, Py_ssize_t col, multiple, Py_ssize_t start_row):
##         pass

    cdef add_multiple_of_row_c(self,  Py_ssize_t row_to, Py_ssize_t row_from, multiple,
                               Py_ssize_t start_col):
        if (multiple%2) != 0:
            rowAddPackedOffset(self._entries, row_from, row_to, start_col)

##     cdef add_multiple_of_column_c(self, Py_ssize_t col_to, Py_ssize_t col_from, s,
##                                    Py_ssize_t start_row):
##         pass

    cdef swap_rows_c(self, Py_ssize_t row1, Py_ssize_t row2):
        rowSwapPacked(self._entries, row1, row2)

##     cdef swap_columns_c(self, Py_ssize_t col1, Py_ssize_t col2):
##         pass

    def _magma_init_(self):
        """
        Returns a string of self in MAGMA form. Does not return MAGMA
        object but string.
        """
        cdef int i,j
        K = self._base_ring._magma_init_()
        if self._nrows == self._ncols:
            s = 'MatrixAlgebra(%s, %s)'%(K, self.nrows())
        else:
            s = 'RMatrixSpace(%s, %s, %s)'%(K, self.nrows(), self.ncols())
        v = []
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                v.append(str(readPackedCell(self._entries,i,j)))
        return s + '![%s]'%(','.join(v))

    def transpose(self):
        """
        Returns transpose of self and leaves self untouched.

        EXAMPLE:
            sage: A = Matrix(GF(2),3,5,[1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0])
            sage: A
            [1 0 1 0 0]
            [0 1 1 0 0]
            [1 1 0 1 0]
            sage: B = A.transpose(); B
            [1 0 1]
            [0 1 1]
            [1 1 0]
            [0 0 1]
            [0 0 0]
            sage: B.transpose() == A
            True

        """
        cdef Matrix_mod2_dense A = self.new_matrix(ncols = self._nrows,  nrows = self._ncols)
        destroyPackedMatrix(A._entries)

        A._entries = transposePacked(self._entries)
        return A

    cdef int _cmp_c_impl(self, Element right) except -2:
        return comparePackedMatrix(self._entries, (<Matrix_mod2_dense>right)._entries)


    def augment(self, Matrix_mod2_dense right):
        """
        Augements self with right.

        EXAMPLE:
            sage: MS = MatrixSpace(GF(2),3,3)
            sage: A = MS([0, 1, 0, 1, 1, 0, 1, 1, 1]); A
            [0 1 0]
            [1 1 0]
            [1 1 1]
            sage: B = A.augment(MS(1)); B
            [0 1 0 1 0 0]
            [1 1 0 0 1 0]
            [1 1 1 0 0 1]
            sage: B.echelonize(); B
            [1 0 0 1 1 0]
            [0 1 0 1 0 0]
            [0 0 1 0 1 1]
            sage: C = B.matrix_from_columns([3,4,5]); C
            [1 1 0]
            [1 0 0]
            [0 1 1]
            sage: C == ~A
            True
            sage: C*A == MS(1)
            True

        """
        cdef Matrix_mod2_dense A

        A = self.new_matrix(ncols = self._ncols + right._ncols)
        destroyPackedMatrix(A._entries)

        A._entries = concatPacked(self._entries, right._entries)
        return A
