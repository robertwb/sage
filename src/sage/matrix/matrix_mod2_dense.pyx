"""
Dense matrices over GF(2) using the M4RI library.

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
    TypeError: unsupported operand parent(s) for '*': 'Full MatrixSpace of 3 by 3 dense matrices over Finite Field of size 2' and 'Full MatrixSpace of 2 by 3 dense matrices over Finite Field of size 2'
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

TESTS:
    sage: FF = FiniteField(2)
    sage: V = VectorSpace(FF,2)
    sage: v = V([0,1]); v
    (0, 1)
    sage: W = V.subspace([v])
    sage: W
    Vector space of degree 2 and dimension 1 over Finite Field of size 2
    Basis matrix:
    [0 1]
    sage: v in W
    True

    sage: M = Matrix(GF(2), [[1,1,0],[0,1,0]])
    sage: M.row_space()
    Vector space of degree 3 and dimension 2 over Finite Field of size 2
    Basis matrix:
    [1 0 0]
    [0 1 0]

    sage: M = Matrix(GF(2), [[1,1,0],[0,0,1]])
    sage: M.row_space()
    Vector space of degree 3 and dimension 2 over Finite Field of size 2
    Basis matrix:
    [1 1 0]
    [0 0 1]

TODO:
   - make linbox frontend and use it
     - charpoly ?
     - minpoly ?
   - make Matrix_modn_frontend and use it (?)
"""

##############################################################################
#       Copyright (C) 2004,2005,2006 William Stein <wstein@gmail.com>
#       Copyright (C) 2007,2008 Martin Albrecht <M.R.Albrecht@rhul.ac.uk>
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

cdef extern from "gd.h":
    ctypedef struct gdImagePtr "gdImagePtr":
        pass

    gdImagePtr gdImageCreateFromPng(FILE *f)
    gdImagePtr gdImageCreateFromPngPtr(int size, void *s)
    gdImagePtr gdImageCreate(int x, int y)
    void gdImagePng(gdImagePtr im, FILE *out)
    void *gdImagePngPtr(gdImagePtr im, int *size)
    void gdImageDestroy(gdImagePtr im)
    int gdImageSX(gdImagePtr im)
    int gdImageSY(gdImagePtr im)
    int gdImageGetPixel(gdImagePtr im, int x, int y)
    void gdImageSetPixel(gdImagePtr im, int x, int y, int value)
    int gdImageColorAllocate(gdImagePtr im, int r, int g, int b)
    void gdImageFilledRectangle(gdImagePtr im, int x1, int y1, int x2, int y2, int color)
    void gdFree(void *m)

## from sage.libs.linbox.linbox cimport Linbox_mod2_dense
## cdef Linbox_mod2_dense linbox
## linbox = Linbox_mod2_dense()

cdef object called

cdef void init_m4ri():
    global called
    if called is None:
        m4ri_build_all_codes()
        called = True

init_m4ri()

def free_m4ri():
    """
    Free global Gray code tables.
    """
    m4ri_destroy_all_codes()



cdef class Matrix_mod2_dense(matrix_dense.Matrix_dense):   # dense or sparse
    r"""
    Dense matrix over GF(2).
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

        if alloc and self._nrows and self._ncols:
            self._entries = mzd_init(self._nrows, self._ncols)

        # cache elements
        self._zero = self._base_ring(0)
        self._one = self._base_ring(1)

    def __dealloc__(self):
        if self._entries:
            mzd_free(self._entries)
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

        TESTS:
            sage: Matrix(GF(2),0,0)
            []
            sage: Matrix(GF(2),2,0)
            []
            sage: Matrix(GF(2),0,2)
            []
        """
        cdef int i,j,e

        if entries is None:
            return

        # scalar ?
        if not isinstance(entries, list):
            if self._nrows and self._ncols and int(entries) % 2 == 1:
                mzd_set_ui(self._entries, 1)
            return

        # all entries are given as a long list
        if len(entries) != self._nrows * self._ncols:
            raise IndexError, "The vector of entries has the wrong length."

        k = 0
        R = self.base_ring()

        for i from 0 <= i < self._nrows:
            if PyErr_CheckSignals(): raise KeyboardInterrupt
            for j from 0 <= j < self._ncols:
                mzd_write_bit(self._entries,i,j, int(entries[k]) % 2)
                k = k + 1

    def __richcmp__(Matrix self, right, int op):  # always need for mysterious reasons.
        r"""

        Compares \code{self} with \code{right}. While equality and
        inequality are clearly defined, $<$ and $>$ are not.  For
        those first the matrix dimensions of \code{self} and
        \code{right} are compared. If these match then $<$ means that
        there is a position smallest (i,j) in \code{self} where
        \code{self[i,j]} is zero but \code{right[i,j]} is one. This
        (i,j) is smaller than the (i,j) if \code{self} and
        \code{right} are exchanged for the comparision.

        INPUT:
            right -- a matrix
            op -- comparison operation

        EXAMPLE:
            sage: A = random_matrix(GF(2),2,2)
            sage: B = random_matrix(GF(2),3,3)
            sage: A < B
            True
            sage: A = MatrixSpace(GF(2),3,3)(1)
            sage: B = MatrixSpace(GF(2),3,3)(1)
            sage: B[0,1] = 1
            sage: A < B
            True

        TESTS:
            sage: A = matrix(GF(2),2,0)
            sage: B = matrix(GF(2),2,0)
            sage: A < B
            False
        """
        return self._richcmp(right, op)

    def __hash__(self):
        """
        The has of a matrix is computed as $\oplus i*a_i$ where the $a_i$ are
        the flattened entries in a matrix (by row, then by column).

        EXAMPLE:
            sage: B = random_matrix(GF(2),3,3)
            sage: B.set_immutable()
            sage: {B:0} # indirect doctest
            {[0 1 0]
            [0 1 1]
            [0 0 0]: 0}
            sage: M = random_matrix(GF(2), 123, 321)
            sage: M.set_immutable()
            sage: MZ = M.change_ring(ZZ)
            sage: MZ.set_immutable()
            sage: hash(M) == hash(MZ)
            True
            sage: MS = M.sparse_matrix()
            sage: MS.set_immutable()
            sage: hash(M) == hash(MS)
            True

        TEST:
            sage: A = matrix(GF(2),2,0)
            sage: hash(A)
            Traceback (most recent call last):
            ...
            TypeError: mutable matrices are unhashable
            sage: A.set_immutable()
            sage: hash(A)
            0

        """
        if not self._mutability._is_immutable:
            raise TypeError, "mutable matrices are unhashable"

        x = self.fetch('hash')
        if not x is None:
            return x

        if self._nrows == 0 or self._ncols == 0:
            return 0

        cdef unsigned long i, j, truerow
        cdef unsigned long start, shift
        cdef word row_xor
        cdef word end_mask = ~(((<word>1)<<(RADIX - self._ncols%RADIX))-1)
        cdef word top_mask, bot_mask
        cdef word cur
        cdef word* row

        # running_xor is the xor of all words in the matrix, as if the rows
        # in the matrix were written out consecutively, without regard to
        # word boundaries.
        cdef word running_xor = 0
        # running_parity is the number of extra words that must be xor'd.
        cdef unsigned long running_parity = 0


        for i from 0 <= i < self._entries.nrows:

            # All this shifting and masking is because the
            # rows are word-aligned.
            truerow = self._entries.rowswap[i]
            row = self._entries.values + truerow
            start = (i*self._entries.ncols) >> 6
            shift = (i*self._entries.ncols) & 0x3F
            bot_mask = (~(<word>0)) << shift
            top_mask = ~bot_mask

            if self._entries.width > 1:
                row_xor = row[0]
                running_parity ^= start & parity_mask(row[0] & bot_mask)

                for j from 1 <= j < self._entries.width - 1:
                    row_xor ^= row[j]
                    cur = ((row[j-1] << (63-shift)) << 1) ^ (row[j] >> shift)
                    running_parity ^= (start+j) & parity_mask(cur)

                running_parity ^= (start+j) & parity_mask(row[j-1] & top_mask)

            else:
                j = 0
                row_xor = 0

            cur = row[j] & end_mask
            row_xor ^= cur
            running_parity ^= (start+j) & parity_mask(cur & bot_mask)
            running_parity ^= (start+j+1) & parity_mask(cur & top_mask)

            start = (i*self._entries.ncols) & (RADIX-1)
            running_xor ^= (row_xor >> start) ^ ((row_xor << (RADIX-1-start)) << 1)

        cdef unsigned long bit_is_set
        cdef unsigned long h

        # Now we assemble the running_parity and running_xor to get the hash.
        # Viewing the flattened matrix as a list of a_i, the hash is the xor
        # of the i for which a_i is non-zero. We split i into the lower RADIX
        # bits and the rest, so i = i1 << RADIX + i0. Now two matching i0
        # would cancel, so we only need the parity of how many of each
        # possible i0 occur. This is stored in the bits of running_xor.
        # Similarly, running_parity is the xor of the i1 needed. It's called
        # parity because i1 is constant accross a word, and for each word
        # the number of i1 to add is equal to the number of set bits in that
        # word (but because two cancel, we only need keep track of the
        # parity.
        h = RADIX * running_parity
        for i from 0 <= i < RADIX:
            bit_is_set = (running_xor >> (RADIX-1-i)) & 1
            h ^= (RADIX-1) & ~(bit_is_set-1) & i

        if h == -1:
            h = -2

        self.cache('hash', h)
        return h

    # this exists for compatibility with matrix_modn_dense
    cdef set_unsafe_int(self, Py_ssize_t i, Py_ssize_t j, int value):
        """
        Set the (i,j) entry of self to the int value.
        """
        mzd_write_bit(self._entries, i, j, int(value))

    cdef set_unsafe(self, Py_ssize_t i, Py_ssize_t j, value):
        mzd_write_bit(self._entries, i, j, int(value))

    cdef get_unsafe(self, Py_ssize_t i, Py_ssize_t j):
        if mzd_read_bit(self._entries, i, j):
            return self._one
        else:
            return self._zero


    def str(self):
        """
        EXAMPLE:
            sage: B = random_matrix(GF(2),3,3)
            sage: B # indirect doctest
            [0 1 0]
            [0 1 1]
            [0 0 0]
        """
        if self._nrows ==0 or self._ncols == 0:
            return "[]"
        cdef int i,j
        s = []
        for i from 0 <= i < self._nrows:
            rl = []
            for j from 0 <= j < self._ncols:
                rl.append(str(mzd_read_bit(self._entries,i,j)))
            s.append( " ".join(rl) )
        return "[" + "]\n[".join(s) + "]"

    ########################################################################
    # LEVEL 2 functionality
    #   * def _pickle
    #   * def _unpickle
    #   * cdef _mul_
    #   * cdef _cmp_c_impl
    #   * _list -- list of underlying elements (need not be a copy)
    #   * _dict -- sparse dictionary of underlying elements (need not be a copy)
    ########################################################################
    # def _pickle(self):
    # def _unpickle(self, data, int version):   # use version >= 0

    cpdef ModuleElement _add_(self, ModuleElement right):
        """
        Matrix addition.

        INPUT:
            right -- matrix of dimension self.nrows() x self.ncols()

        EXAMPLES:
            sage: A = random_matrix(GF(2),10,10)
            sage: A + A == Matrix(GF(2),10,10,0)
            True

            sage: A = random_matrix(GF(2),257,253)
            sage: A + A == Matrix(GF(2),257,253,0)
            True

        TESTS:
            sage: A = matrix(GF(2),2,0)
            sage: A+A
            []
            sage: A = matrix(GF(2),0,2)
            sage: A+A
            []
            sage: A = matrix(GF(2),0,0)
            sage: A+A
            []
        """
        cdef Matrix_mod2_dense A
        A = Matrix_mod2_dense.__new__(Matrix_mod2_dense, self._parent, 0, 0, 0, alloc=False)
        if self._nrows == 0 or self._ncols == 0:
            return A
        A._entries = mzd_add(NULL, self._entries,(<Matrix_mod2_dense>right)._entries)

        return A

    cpdef ModuleElement _sub_(self, ModuleElement right):
        """
        Matrix addition.

        INPUT:
            right -- matrix of dimension self.nrows() x self.ncols()

        EXAMPLES:
            sage: A = random_matrix(GF(2),10,10)
            sage: A - A == Matrix(GF(2),10,10,0)
            True
        """
        return self._add_(right)

    cdef Matrix _matrix_times_matrix_(self, Matrix right):
        """
        Matrix multiplication.

        ALGORITHM: Uses the 'Method of the Four Russians
        Multiplication', see self._multiply_m4rm.
        """
        if get_verbose() >= 2:
            verbose('matrix multiply of %s x %s matrix by %s x %s matrix'%(
                self._nrows, self._ncols, right._nrows, right._ncols))

        return self._multiply_strassen(right, 0)

    cpdef Matrix_mod2_dense _multiply_m4rm(Matrix_mod2_dense self, Matrix_mod2_dense right, int k):
        """
        Multiply matrices using the 'Method of the Four Russians
        Multiplication' (M4RM) or Konrod's method.

        The algorithm is based on an algorithm by Arlazarov, Dinic,
        Kronrod, and Faradzev [ADKF70] and appeared in [AHU]. This
        implementation is based on a description given in Gregory
        Bard's 'Method of the Four Russians Inversion' paper [B06].

        INPUT:
            right -- Matrix
            k -- parameter $k$ for the Gray Code table size. If $k=0$ a
                 suitable value is chosen by the function.
		 ($0<= k <= 16$, default: 0)

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
              sage: A._multiply_m4rm(B, 0)
              [0 0 0 0]
              [1 0 0 1]
              [0 1 0 1]
              [1 1 0 0]

        TESTS:
            sage: A = random_matrix(GF(2),0,0)
            sage: B = random_matrix(GF(2),0,0)
            sage: A._multiply_m4rm(B, 0)
            []
            sage: A = random_matrix(GF(2),3,0)
            sage: B = random_matrix(GF(2),0,3)
            sage: A._multiply_m4rm(B, 0)
            [0 0 0]
            [0 0 0]
            [0 0 0]
            sage: A = random_matrix(GF(2),0,3)
            sage: B = random_matrix(GF(2),3,0)
            sage: A._multiply_m4rm(B, 0)
            []

        ALGORITHM: Uses the 'Method of the Four Russians'
        multiplication as implemented in the M4RI library.

        REFERENCES:
	    [AHU] A. Aho, J. Hopcroft, and J. Ullman. 'Chapter 6:
                     Matrix Multiplication and Related Operations.'
                     The Design and Analysis of Computer
                     Algorithms. Addison-Wesley, 1974.

            [ADKF70] V. Arlazarov, E. Dinic, M. Kronrod, and
                     I. Faradzev. 'On Economical Construction of the
                     Transitive Closure of a Directed Graph.'
                     Dokl. Akad. Nauk. SSSR No. 194 (in Russian),
                     English Translation in Soviet Math Dokl. No. 11,
                     1970.

            [Bard06] G. Bard. 'Accelerating Cryptanalysis with the
                     Method of Four Russians'. Cryptography E-Print
                     Archive (http://eprint.iacr.org/2006/251.pdf),
                     2006.
        """
        if self._ncols != right._nrows:
            raise ArithmeticError, "left ncols must match right nrows"

        if get_verbose() >= 2:
            verbose('m4rm multiply of %s x %s matrix by %s x %s matrix'%(
                self._nrows, self._ncols, right._nrows, right._ncols))

        cdef Matrix_mod2_dense ans

        ans = self.new_matrix(nrows = self.nrows(), ncols = right.ncols())
        if self._nrows == 0 or self._ncols == 0 or right._ncols == 0:
            return ans
        _sig_on
        ans._entries = mzd_mul_m4rm(ans._entries, self._entries, right._entries, k)
        _sig_off
        return ans

    def _multiply_classical(Matrix_mod2_dense self, Matrix_mod2_dense right):
        r"""
        Classical $O(n^3)$ multiplication.

        This can be quite fast for matrix vector multiplication but
        the other routines fall back to this implementation in that
        case anyway.

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

        TESTS:
            sage: A = random_matrix(GF(2),0,0)
            sage: B = random_matrix(GF(2),0,0)
            sage: A._multiply_classical(B)
            []
            sage: A = random_matrix(GF(2),3,0)
            sage: B = random_matrix(GF(2),0,3)
            sage: A._multiply_classical(B)
            [0 0 0]
            [0 0 0]
            [0 0 0]
            sage: A = random_matrix(GF(2),0,3)
            sage: B = random_matrix(GF(2),3,0)
            sage: A._multiply_classical(B)
            []
        """
        cdef Matrix_mod2_dense A
        A = self.new_matrix(nrows = self.nrows(), ncols = right.ncols())
        if self._nrows == 0 or self._ncols == 0 or right._ncols == 0:
            return A
        A._entries = mzd_mul_naive(A._entries, self._entries,(<Matrix_mod2_dense>right)._entries)
        return A

    cpdef Matrix_mod2_dense _multiply_strassen(Matrix_mod2_dense self, Matrix_mod2_dense right, int cutoff):
        """
        Strassen-Winograd $O(n^{2.807})$ multiplication [Str69].

        This implementation in M4RI is inspired by Sage's generic
        Strassen implementation [BHS08] but uses a more memory
        efficient operation schedule [DP08].

        The performance of this routine depends on the parameter
        cutoff. On many modern machines 2048 should give acceptable
        performance, a good rule of thumb for calculating the optimal
        cutoff would that two matrices of the cutoff size should fit
        in L2 cache, so: $cutoff = \sqrt{L2 * 8 * 1024^2 / 2}$ where
        $L2$ is the size of the L2 cache in MB.

        INPUT:
            right -- a matrix of matching dimensions.
            cutoff -- matrix dimension where M4RM should be used
                      instead of Strassen (default: let M4RI decide)

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
              sage: A._multiply_strassen(B, 0)
              [0 0 0 0]
              [1 0 0 1]
              [0 1 0 1]
              [1 1 0 0]
              sage: A = random_matrix(GF(2),2701,3000)
              sage: B = random_matrix(GF(2),3000,3172)
              sage: A._multiply_strassen(B, 256) == A._multiply_m4rm(B, 0)
              True

        TESTS:
            sage: A = random_matrix(GF(2),0,0)
            sage: B = random_matrix(GF(2),0,0)
            sage: A._multiply_strassen(B, 0)
            []
            sage: A = random_matrix(GF(2),3,0)
            sage: B = random_matrix(GF(2),0,3)
            sage: A._multiply_strassen(B, 0)
            [0 0 0]
            [0 0 0]
            [0 0 0]
            sage: A = random_matrix(GF(2),0,3)
            sage: B = random_matrix(GF(2),3,0)
            sage: A._multiply_strassen(B, 0)
            []

        ALGORITHM: Uses Strassen-Winograd matrix multiplication with
        M4RM as base case as implemented in the M4RI library.

        REFERENCES:
            [Str69] Volker Strassen. Gaussian elimination is not
                    optimal. Numerische Mathematik, 13:354-356, 1969.

            [BHS08] Robert Bradshaw, David Harvey and William
                    Stein. strassen_window_multiply_c. strassen.pyx,
                    Sage 3.0, 2008. http://www.sagemath.org

            [DP08] Jean-Guillaume Dumas and Clement Pernet. Memory
                   efficient scheduling of Strassen-Winograd's matrix
                   multiplication algorithm. arXiv:0707.2347v1, 2008.
        """
        if self._ncols != right._nrows:
            raise ArithmeticError, "left ncols must match right nrows"

        cdef Matrix_mod2_dense ans
        ans = self.new_matrix(nrows = self.nrows(), ncols = right.ncols())
        if self._nrows == 0 or self._ncols == 0 or right._ncols == 0:
            return ans

        _sig_on
        ans._entries = mzd_mul(ans._entries, self._entries, right._entries, cutoff)
        _sig_off
        return ans

    def __neg__(self):
        """
        EXAMPLES:
            sage: A = random_matrix(GF(2),100,100)
            sage: A - A == A - -A
            True
        """
        return self.copy()

    def __invert__(self):
        r"""
        Inverts self using the 'Method of the Four Russians'
        inversion.

        If \code{self} is not invertible a \code{ZeroDivisionError} is
        raised.

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

        TESTS:
            sage: A = matrix(GF(2),0,0)
            sage: A^(-1)
            Traceback (most recent call last):
            ...
            ZeroDivisionError
        """
        cdef int k = 0
        cdef packedmatrix *I
        cdef Matrix_mod2_dense A

        if self._nrows != self._ncols:
            raise ArithmeticError, "self must be a square matrix"

        if self._ncols == 0:
            return self.copy()

        I = mzd_init(self._nrows,self._ncols)
        mzd_set_ui(I, 1)

        A = Matrix_mod2_dense.__new__(Matrix_mod2_dense, self._parent, 0, 0, 0, alloc = False)
        _sig_on
        A._entries = mzd_invert_m4ri(self._entries, I, k)
        _sig_off
        mzd_free(I)

        if A._entries==NULL:
            raise ZeroDivisionError, "self is not invertible"
        else:
            return A

    def __copy__(self):
        r"""
        Returns a copy of \code{self}.

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
        A = Matrix_mod2_dense.__new__(Matrix_mod2_dense, self._parent, 0, 0, 0)

        if self._nrows and self._ncols:
            mzd_copy(A._entries, self._entries)

        if self.subdivisions is not None:
            A.subdivide(*self.get_subdivisions())

        return A

    def _list(self):
        r"""
        Returns list of the elements of \code{self} in row major
        ordering.

        EXAMPLE:
            sage: A = Matrix(GF(2),2,2,[1,0,1,1])
            sage: A
            [1 0]
            [1 1]
            sage: A.list() #indirect doctest
            [1, 0, 1, 1]

        TESTS:
            sage: A = Matrix(GF(2),3,0)
            sage: A.list()
            []
        """
        cdef int i,j
        l = []
        for i from 0 <= i < self._nrows:
            for j from 0 <= j < self._ncols:
                if mzd_read_bit(self._entries,i,j):
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

    def echelonize(self, algorithm='m4ri', cutoff=0, reduced=True, **kwds):
        """
        Puts self in (reduced) row echelon form.

        INPUT:
            self -- a mutable matrix
            algorithm -- 'm4ri' -- uses M4RI (default)
                         'classical' -- uses classical Gaussian elimination
                         'pluq' -- uses PLUQ factorization
            k --  the parameter 'k' of the M4RI algorithm. It MUST be between
                  1 and 16 (inclusive). If it is not specified it will be calculated as
                  3/4 * log_2( min(nrows, ncols) ) as suggested in the M4RI paper.
            reduced -- return reduced row echelon form (default:True)

        EXAMPLE:
             sage: A = random_matrix(GF(2), 10, 10)
             sage: B = A.copy(); B.echelonize() # fastest
             sage: C = A.copy(); C.echelonize(k=2) # force k
             sage: E = A.copy(); E.echelonize(algorithm='classical') # force Gaussian elimination
             sage: B == C == E
             True

        TESTS:
             sage: VF2 = VectorSpace(GF(2),2)
             sage: WF2 = VF2.submodule([VF2([1,1])])
             sage: WF2
             Vector space of degree 2 and dimension 1 over Finite Field of size 2
             Basis matrix:
             [1 1]

             sage: A2 = matrix(GF(2),2,[1,0,0,1])
             sage: A2.kernel()
             Vector space of degree 2 and dimension 0 over Finite Field of size 2
             Basis matrix:
             []

        ALGORITHM: Uses M4RI library

        REFERENCES:
            [Bard06] G. Bard. 'Accelerating Cryptanalysis with the Method of Four Russians'. Cryptography
                     E-Print Archive (http://eprint.iacr.org/2006/251.pdf), 2006.
        """
        if self._nrows == 0 or self._ncols == 0:
            self.cache('in_echelon_form',True)
            self.cache('rank', 0)
            self.cache('pivots', [])
            return self
        cdef int k, n, full

        full = int(reduced)

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
                #n = min(self._nrows, self._ncols)
                #k = round(min(0.75 * log(n,2), 16))
                #if k<1:
                #    k = 1
                k = 0

            _sig_on
            r =  mzd_echelonize_m4ri(self._entries, full, k, NULL, NULL)
            _sig_off

            self.cache('in_echelon_form',True)
            self.cache('rank', r)
            self.cache('pivots', self._pivots())


        elif algorithm == 'pluq':

            self.check_mutability()
            self.clear_cache()

            _sig_on
            r =  mzd_echelonize_pluq(self._entries, full)
            _sig_off

            self.cache('in_echelon_form',True)
            self.cache('rank', r)
            self.cache('pivots', self._pivots())

        elif algorithm == 'linbox':

            #self._echelonize_linbox()
            raise NotImplementedError

        elif algorithm == 'classical':

            # for debugging purposes only, it is slow
            self._echelon_in_place_classical()
        else:
            raise ValueError, "no algorithm '%s'"%algorithm

    def _pivots(self):
        r"""
        Returns the pivot columns of \code{self} if \code{self} is in
        row echelon form.

        EXAMPLE:
            sage: A = matrix(GF(2),5,5,[0,1,0,1,0,0,1,0,1,1,0,1,0,1,0,0,0,0,1,0,0,0,1,0,1])
            sage: E = A.echelon_form()
            sage: E
            [0 1 0 0 0]
            [0 0 1 0 0]
            [0 0 0 1 0]
            [0 0 0 0 1]
            [0 0 0 0 0]
            sage: E._pivots()
            [1, 2, 3, 4]
        """
        if not self.fetch('in_echelon_form'):
            raise RuntimeError, "self must be in reduced row echelon form first."
        pivots = []
        cdef Py_ssize_t i, j, nc
        nc = self._ncols
        i = 0
        while i < self._nrows:
            for j from i <= j < nc:
                if mzd_read_bit(self._entries, i, j):
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

        EXAMPLES:
            sage: A = matrix(GF(2), 5, 5, 0)
            sage: A.randomize(0.5); A
            [0 0 0 1 1]
            [0 1 0 0 1]
            [1 0 0 0 0]
            [0 1 0 0 0]
            [0 0 0 1 0]
            sage: A.randomize(); A
            [0 0 1 1 0]
            [1 1 0 0 1]
            [1 1 1 1 0]
            [1 1 1 1 1]
            [0 0 1 1 0]

        TESTS:
        With the libc random number generator random(), we had problems
        where the ranks of all of these matrices would be the same
        (and they would all be far too low).  This verifies that the
        problem is gone, with Mersenne Twister.
            sage: MS2 = MatrixSpace(GF(2), 1000)
            sage: [MS2.random_element().rank() for i in range(5)]
            [999, 998, 1000, 999, 999]

        Testing corner case.
            sage: A = random_matrix(GF(2),3,0)
            sage: A
            []
        """
        if self._ncols == 0 or self._nrows == 0:
            return

        density = float(density)
        if density == 0:
            return

        self.check_mutability()
        self.clear_cache()

        cdef randstate rstate = current_randstate()

        cdef int i, j, k
        cdef int nc
        cdef int truerow
        cdef unsigned int low, high
        cdef word mask = 1

        if density == 1:
            assert(sizeof(word) == 8)
            mask = ~((mask<<(RADIX - self._entries.ncols%RADIX))-1)
            for i from 0 <= i < self._nrows:
                truerow = self._entries.rowswap[i]
                for j from 0 <= j < self._entries.width:
                    # for portability we get 32-bit twice rather than 64-bit once
                    low = gmp_urandomb_ui(rstate.gmp_state, 32)
                    high = gmp_urandomb_ui(rstate.gmp_state, 32)
                    self._entries.values[truerow + j] = ((<unsigned long long>high)<<32)| (<unsigned long long>low)
                j = truerow + self._entries.width - 1
                self._entries.values[j] &= mask
        else:
            nc = self._ncols
            num_per_row = int(density * nc)
            _sig_on
            for i from 0 <= i < self._nrows:
                for j from 0 <= j < num_per_row:
                    k = rstate.c_random()%nc
                    mzd_write_bit(self._entries, i, k, rstate.c_random() % 2)
            _sig_off


    cdef rescale_row_c(self, Py_ssize_t row, multiple, Py_ssize_t start_col):
        """
        EXAMPLE:
            sage: A = random_matrix(GF(2),3,3); A
            [0 1 0]
            [0 1 1]
            [0 0 0]
            sage: A.rescale_row(0,0,0); A
            [0 0 0]
            [0 1 1]
            [0 0 0]
        """
        if (int(multiple)%2) == 0:
            mzd_row_clear_offset(self._entries, row, start_col);

    cdef add_multiple_of_row_c(self,  Py_ssize_t row_to, Py_ssize_t row_from, multiple,
                               Py_ssize_t start_col):
        """
        EXAMPLE:
            sage: A = random_matrix(GF(2),3,3); A
            [0 1 0]
            [0 1 1]
            [0 0 0]
            sage: A.add_multiple_of_row(0,1,1,0); A
            [0 0 1]
            [0 1 1]
            [0 0 0]
        """
        if (int(multiple)%2) != 0:
            mzd_row_add_offset(self._entries, row_to, row_from, start_col)

    cdef swap_rows_c(self, Py_ssize_t row1, Py_ssize_t row2):
        """
        EXAMPLE:
            sage: A = random_matrix(GF(2),3,3)
            sage: A
            [0 1 0]
            [0 1 1]
            [0 0 0]
            sage: A.swap_rows(0,1); A
            [0 1 1]
            [0 1 0]
            [0 0 0]
        """
        mzd_row_swap(self._entries, row1, row2)

    cdef swap_columns_c(self, Py_ssize_t col1, Py_ssize_t col2):
        """
        EXAMPLE:
            sage: A = random_matrix(GF(2),3,3)
            sage: A
            [0 1 0]
            [0 1 1]
            [0 0 0]
            sage: A.swap_columns(0,1); A
            [1 0 0]
            [1 0 1]
            [0 0 0]

            sage: A = random_matrix(GF(2),3,65)

            sage: B = A.copy()
            sage: B.swap_columns(0,1)
            sage: B.swap_columns(0,1)
            sage: A == B
            True

            sage: A.swap_columns(0,64)
            sage: A.column(0) == B.column(64)
            True
            sage: A.swap_columns(63,64)
            sage: A.column(63) == B.column(0)
            True
        """
        mzd_col_swap(self._entries, col1, col2)



    def _magma_init_(self, magma):
        r"""
        Returns a string of self in \Magma form. Does not return \Magma
        object but string.

        EXAMPLE:
            sage: A = random_matrix(GF(2),3,3)
            sage: A._magma_init_(magma)                             # optional - magma
            'Matrix(GF(2),3,3,StringToIntegerSequence("0 1 0 0 1 1 0 0 0"))'
            sage: A = random_matrix(GF(2),100,100)
            sage: B = random_matrix(GF(2),100,100)
            sage: magma(A*B) == magma(A) * magma(B)                 # optional - magma
            True

        TESTS:
            sage: A = random_matrix(GF(2),0,3)
            sage: magma(A)                          # optional - magma
            Matrix with 0 rows and 3 columns
            sage: A = matrix(GF(2),2,3,[0,1,1,1,0,0])
            sage: A._magma_init_(magma)             # optional - magma
            'Matrix(GF(2),2,3,StringToIntegerSequence("0 1 1 1 0 0"))'
            sage: magma(A)                          # optional - magma
            [0 1 1]
            [1 0 0]
        """
        s = self.base_ring()._magma_init_(magma)
        return 'Matrix(%s,%s,%s,StringToIntegerSequence("%s"))'%(
            s, self._nrows, self._ncols, self._export_as_string())

    def determinant(self):
        """
        Return the determinant of this matrix over GF(2).

        EXAMPLES:
            sage: matrix(GF(2),2,[1,1,0,1]).determinant()
            1
            sage: matrix(GF(2),2,[1,1,1,1]).determinant()
            0
        """
        if not self.is_square():
            raise ValueError, "self must be square"
        return self.base_ring()(1 if self.rank() == self.nrows() else 0)

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

        TESTS:
            sage: A = random_matrix(GF(2),0,40)
            sage: A.transpose()
            40 x 0 dense matrix over Finite Field of size 2
        """
        cdef Matrix_mod2_dense A = self.new_matrix(ncols = self._nrows,  nrows = self._ncols)
        if self._nrows == 0 or self._ncols == 0:
            return A

        A._entries = mzd_transpose(A._entries, self._entries)
        if self.subdivisions is not None:
            A.subdivide(*self.get_subdivisions())
        return A

    cdef int _cmp_c_impl(self, Element right) except -2:
        if self._nrows == 0 or self._ncols == 0:
            return 0
        return mzd_cmp(self._entries, (<Matrix_mod2_dense>right)._entries)


    def augment(self, Matrix_mod2_dense right):
        r"""
        Augments \code{self} with \code{right}.

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

        TESTS:
            sage: A = random_matrix(GF(2),2,3)
            sage: B = random_matrix(GF(2),2,0)
            sage: A.augment(B)
            [0 1 0]
            [0 1 1]
            sage: B.augment(A)
            [0 1 0]
            [0 1 1]
            sage: M = Matrix(GF(2), 0, 0, 0)
            sage: N = Matrix(GF(2), 0, 19, 0)
            sage: W = M.augment(N)
            sage: W.ncols()
            19
            sage: M = Matrix(GF(2), 0, 1, 0)
            sage: N = Matrix(GF(2), 0, 1, 0)
            sage: M.augment(N)
            []
        """
        cdef Matrix_mod2_dense A

        if self._nrows != right._nrows:
            raise TypeError, "Both numbers of rows must match."

        if self._ncols == 0:
            return right.copy()
        if right._ncols == 0:
            return self.copy()

        A = self.new_matrix(ncols = self._ncols + right._ncols)
        if self._nrows == 0:
            return A
        A._entries = mzd_concat(A._entries, self._entries, right._entries)
        return A

    def stack(self, Matrix_mod2_dense other):
        r"""
        Stack \code{self} on top of \code{other}.

        EXAMPLE:
            sage: A = matrix(GF(2),2,2,[1,0,0,1])
            sage: B = matrix(GF(2),2,2,[0,1,1,0])
            sage: A.stack(B)
            [1 0]
            [0 1]
            [0 1]
            [1 0]
            sage: B.stack(A)
            [0 1]
            [1 0]
            [1 0]
            [0 1]

        TESTS:
            sage: A = random_matrix(GF(2),0,3)
            sage: B = random_matrix(GF(2),3,3)
            sage: A.stack(B)
            [0 1 0]
            [0 1 1]
            [0 0 0]
            sage: B.stack(A)
            [0 1 0]
            [0 1 1]
            [0 0 0]
            sage: M = Matrix(GF(2), 0, 0, 0)
            sage: N = Matrix(GF(2), 19, 0, 0)
            sage: W = M.stack(N)
            sage: W.nrows()
            19
            sage: M = Matrix(GF(2), 1, 0, 0)
            sage: N = Matrix(GF(2), 1, 0, 0)
            sage: M.stack(N)
            []
        """
        if self._ncols != other._ncols:
            raise TypeError, "Both numbers of columns must match."

        if self._nrows == 0:
            return other.copy()
        if other._nrows == 0:
            return self.copy()

        cdef Matrix_mod2_dense A
        A = self.new_matrix(nrows = self._nrows + other._nrows)
        if self._ncols == 0:
            return A
        A._entries = mzd_stack(A._entries, self._entries, other._entries)
        return A

    def submatrix(self, lowr, lowc, nrows , ncols):
        """
	Return submatrix from the index lowr,lowc (inclusive) with
	dimension nrows x ncols.

        INPUT:
            lowr -- index of start row
            lowc -- index of start column
            nrows -- number of rows of submatrix
            ncols -- number of columns of submatrix

        EXAMPLES:
             sage: A = random_matrix(GF(2),200,200)
             sage: A[0:2,0:2] == A.submatrix(0,0,2,2)
             True
             sage: A[0:100,0:100] == A.submatrix(0,0,100,100)
             True
             sage: A == A.submatrix(0,0,200,200)
             True

             sage: A[1:3,1:3] == A.submatrix(1,1,2,2)
             True
             sage: A[1:100,1:100] == A.submatrix(1,1,99,99)
             True
             sage: A[1:200,1:200] == A.submatrix(1,1,199,199)
             True
	"""
        cdef Matrix_mod2_dense A

        cdef int highr, highc

        highr = lowr + nrows
        highc = lowc + ncols

        if nrows <= 0 or ncols <= 0:
            raise TypeError, "Expected nrows, ncols to be > 0, but got %d,%d instead."%(nrows, ncols)

        if highc > self._entries.ncols:
            raise TypeError, "Expected highc <= self.ncols(), but got %d > %d instead."%(highc, self._entries.ncols)

        if highr > self._entries.nrows:
            raise TypeError, "Expected highr <= self.nrows(), but got %d > %d instead."%(highr, self._entries.nrows)

        if lowr < 0:
            raise TypeError, "Expected lowr >= 0, but got %d instead."%lowr

        if lowc < 0:
            raise TypeError, "Expected lowc >= 0, but got %d instead."%lowc

        A = self.new_matrix(nrows = nrows, ncols = ncols)
        if self._ncols == 0 or self._nrows == 0:
            return A
        A._entries = mzd_submatrix(A._entries, self._entries, lowr, lowc, highr, highc)
        return A

    def __reduce__(self):
        r"""
        Serialize \code{self}.

        EXAMPLE:
            sage: A = random_matrix(GF(2),10,10)
            sage: f,s = A.__reduce__()
            sage: f(*s) == A
            True
        """
        cdef int i,j, r,c, size

        r, c = self.nrows(), self.ncols()
        if r == 0 or c == 0:
            return unpickle_matrix_mod2_dense_v1, (r, c, None, 0)

        _sig_on
        cdef gdImagePtr im = gdImageCreate(c, r)
        _sig_off
        cdef int black = gdImageColorAllocate(im, 0, 0, 0)
        cdef int white = gdImageColorAllocate(im, 255, 255, 255)
        gdImageFilledRectangle(im, 0, 0, c-1, r-1, white)
        for i from 0 <= i < r:
            for j from 0 <= j < c:
                if mzd_read_bit(self._entries, i, j):
                    gdImageSetPixel(im, j, i, black )

        cdef char *buf = <char*>gdImagePngPtr(im, &size)

        data = [buf[i] for i in range(size)]
        gdFree(buf)
        gdImageDestroy(im)
        return unpickle_matrix_mod2_dense_v1, (r,c, data, size)

    cpdef _export_as_string(self):
        """
        Return space separated string of the entries in this matrix.

        EXAMPLES:
            sage: w = matrix(GF(2),2,3,[1,0,1,1,1,0])
            sage: w._export_as_string()
            '1 0 1 1 1 0'
        """
        cdef Py_ssize_t i, j, k, n
        cdef char *s, *t

        if self._nrows == 0 or self._ncols == 0:
            data = ''
        else:
            n = self._nrows*self._ncols*2 + 2
            s = <char*> sage_malloc(n * sizeof(char))
            k = 0
            _sig_on
            for i in range(self._nrows):
                for j in range(self._ncols):
                    s[k] = <char>(48 + (1 if mzd_read_bit(self._entries,i,j) else 0))  # "0" or "1"
                    k += 1
                    s[k] = <char>32  # space
                    k += 1
            _sig_off
            s[k-1] = <char>0
            data = str(s)
            sage_free(s)
        return data

    def density(self, approx=False):
        """
        Return the density of this matrix.

        By density we understand the ration of the number of nonzero
        positions and the self.nrows() * self.ncols(), i.e. the number
        of possible nonzero positions.

        INPUT:
            approx -- return floating point approximation (default: False)

        EXAMPLE:
            sage: A = random_matrix(GF(2),1000,1000)
            sage: d = A.density(); d
            62483/125000
            sage: float(d)
            0.499863...
            sage: A.density(approx=True)
            0.499773...
            sage: float(len(A.nonzero_positions())/1000^2)
            0.499863...
        """
        if approx:
            from sage.rings.real_mpfr import create_RealNumber
            return create_RealNumber(mzd_density(self._entries, 1))
        else:
            return matrix_dense.Matrix_dense.density(self)

# Used for hashing
cdef int i, k
cdef unsigned long parity_table[256]
for i from 0 <= i < 256:
    parity_table[i] = 1 & ((i) ^ (i>>1) ^ (i>>2) ^ (i>>3) ^
                           (i>>4) ^ (i>>5) ^ (i>>6) ^ (i>>7))

# gmp's ULONG_PARITY may use special
# assembly instructions, could be faster
cpdef inline unsigned long parity(word a):
    """
    Returns the parity of the number of bits in a.

    EXAMPLES:
        sage: from sage.matrix.matrix_mod2_dense import parity
        sage: parity(1)
        1L
        sage: parity(3)
        0L
        sage: parity(0x10000101011)
        1L
    """
    if sizeof(word) == 8:
        a ^= a >> 32
    a ^= a >> 16
    a ^= a >> 8
    return parity_table[a & 0xFF]

cdef inline unsigned long parity_mask(word a):
    return -parity(a)


def unpickle_matrix_mod2_dense_v1(r, c, data, size):
    r"""
    Deserialize a matrix encoded in the string \code{s}.

    INPUT:
        r -- number of rows of matrix
        c -- number of columns of matrix
        s -- a string
        size -- length of the string s

    EXAMPLE:
        sage: A = random_matrix(GF(2),100,101)
        sage: _,(r,c,s,s2) = A.__reduce__()
        sage: from sage.matrix.matrix_mod2_dense import unpickle_matrix_mod2_dense_v1
        sage: unpickle_matrix_mod2_dense_v1(r,c,s,s2) == A
        True
        sage: loads(dumps(A)) == A
        True
    """
    from sage.matrix.constructor import Matrix
    from sage.rings.finite_field import FiniteField as GF

    cdef int i, j
    cdef Matrix_mod2_dense A

    A = <Matrix_mod2_dense>Matrix(GF(2),r,c)
    if r == 0 or c == 0:
        return A

    cdef char *buf = <char*>sage_malloc(size)
    for i from 0 <= i < size:
        buf[i] = data[i]

    _sig_on
    cdef gdImagePtr im = gdImageCreateFromPngPtr(size, buf)
    _sig_off

    sage_free(buf)

    if gdImageSX(im) != c or gdImageSY(im) != r:
        raise TypeError, "Pickled data dimension doesn't match."


    for i from 0 <= i < r:
        for j from 0 <= j < c:
            mzd_write_bit(A._entries, i, j, 1-gdImageGetPixel(im, j, i))
    gdImageDestroy(im)
    return A

def from_png(filename):
    r"""
    Returns a dense matrix over GF(2) from a 1-bit PNG image read from
    \code{filename}. No attempt is made to verify that the filname string
    actually points to a PNG image.

    INPUT:
        filename -- a string

    EXAMPLE:
        sage: from sage.matrix.matrix_mod2_dense import from_png, to_png
        sage: A = random_matrix(GF(2),10,10)
        sage: fn = tmp_filename()
        sage: to_png(A, fn)
        sage: B = from_png(fn)
        sage: A == B
        True
    """
    from sage.matrix.constructor import Matrix
    from sage.rings.finite_field import FiniteField as GF

    cdef int i,j,r,c
    cdef Matrix_mod2_dense A

    fn = open(filename,"r") # check filename
    fn.close()

    cdef FILE *f = fopen(filename, "rb")
    _sig_on
    cdef gdImagePtr im = gdImageCreateFromPng(f)
    _sig_off

    c, r = gdImageSX(im), gdImageSY(im)

    A = <Matrix_mod2_dense>Matrix(GF(2),r,c)

    for i from 0 <= i < r:
        for j from 0 <= j < c:
            mzd_write_bit(A._entries, i, j, 1-gdImageGetPixel(im, j, i))
    fclose(f)
    gdImageDestroy(im)
    return A

def to_png(Matrix_mod2_dense A, filename):
    r"""
    Saves the matrix \code{A} to filename as a 1-bit PNG image.

    INPUT:
        A -- a matrix over GF(2)
        filename -- a string for a file in a writeable position

    EXAMPLE:
        sage: from sage.matrix.matrix_mod2_dense import from_png, to_png
        sage: A = random_matrix(GF(2),10,10)
        sage: fn = tmp_filename()
        sage: to_png(A, fn)
        sage: B = from_png(fn)
        sage: A == B
        True
    """
    cdef int i,j, r,c
    r, c = A.nrows(), A.ncols()
    if r == 0 or c == 0:
        raise TypeError, "Cannot write image with dimensions %d x %d"%(c,r)
    fn = open(filename,"w") # check filename
    fn.close()
    cdef gdImagePtr im = gdImageCreate(c, r)
    cdef FILE * out = fopen(filename, "wb")
    cdef int black = gdImageColorAllocate(im, 0, 0, 0)
    cdef int white = gdImageColorAllocate(im, 255, 255, 255)
    gdImageFilledRectangle(im, 0, 0, c-1, r-1, white)
    for i from 0 <= i < r:
        for j from 0 <= j < c:
            if mzd_read_bit(A._entries, i, j):
                gdImageSetPixel(im, j, i, black )

    gdImagePng(im, out)
    gdImageDestroy(im)
    fclose(out)

def pluq(Matrix_mod2_dense A, algorithm="standard", int param=0):
    """
    Return PLUQ factorization of A.

    INPUT:
        A -- matrix
        algorithm -- 'standard' asymptotically fast (default)
                     'mmpf' M4RI inspired
                     'naive' naive cubic
        param -- either k for 'mmpf' is chosen or matrix multiplication
                 cutoff for 'standard' (default: 0)

    EXAMPLE:
        sage: from sage.matrix.matrix_mod2_dense import pluq
        sage: A = random_matrix(GF(2),4,4); A
        [0 1 0 1]
        [0 1 1 1]
        [0 0 0 1]
        [0 1 1 0]

        sage: LU, P, Q = pluq(A)
        sage: LU
        [1 0 1 0]
        [1 1 0 0]
        [0 0 1 0]
        [1 1 1 0]

        sage: P
        [0, 1, 2, 3]

        sage: Q
        [1, 2, 3, 3]
    """
    cdef Matrix_mod2_dense B = A.copy()
    cdef permutation *p = mzp_init(A._entries.nrows)
    cdef permutation *q = mzp_init(A._entries.ncols)

    if algorithm == "standard":
        _sig_on
        mzd_pluq(B._entries, p, q, param)
        _sig_off
    elif algorithm == "mmpf":
        _sig_on
        _mzd_pluq_mmpf(B._entries, p, q, param)
        _sig_off
    elif algorithm == "naive":
        _sig_on
        _mzd_pluq_naive(B._entries, p, q)
        _sig_off
    else:
        raise ValueError("Algorithm '%s' unknown."%algorithm)

    P = [p.values[i] for i in range(A.nrows())]
    Q = [q.values[i] for i in range(A.ncols())]
    mzp_free(p)
    mzp_free(q)
    return B,P,Q
