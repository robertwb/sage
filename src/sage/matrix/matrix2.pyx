"""
Abstract base class for matrices.

For design documentation see matrix/docs.py.
"""

################################################################################
#       Copyright (C) 2005, 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL), version 2.
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
################################################################################

include "../ext/stdsage.pxi"
include "../ext/python.pxi"

import strassen

from   sage.structure.sequence import _combinations, Sequence
from   sage.misc.misc import verbose, get_verbose
from   sage.rings.number_field.all import is_NumberField

import sage.modules.free_module

cdef class Matrix(matrix1.Matrix):
    def prod_of_row_sums(self, cols):
        r"""
        Calculate the product of all row sums of a submatrix of $A$ for a
        list of selected columns \code{cols}.

        EXAMPLES:
            sage: a = matrix(QQ, 2,2, [1,2,3,2]); a
            [1 2]
            [3 2]
            sage: a.prod_of_row_sums([0,1])
            15

        Another example:
            sage: a = matrix(QQ, 2,3, [1,2,3,2,5,6]); a
            [1 2 3]
            [2 5 6]
            sage: a.prod_of_row_sums([1,2])
            55

        AUTHOR:
            -- Jaap Spies (2006-02-18)
        """
        cdef Py_ssize_t c, row
        pr = 1
        for row from 0 <= row < self._nrows:
            tmp = []
            for c in cols:
                if c<0 or c >= self._ncols:
                    raise IndexError, "matrix column index out of range"
                tmp.append(self.get_unsafe(row, c))
            pr = pr * sum(tmp)
        return pr

    def permanent(self):
        r"""
        Calculate and return the permanent of this $m \times n$ matrix using
        Ryser's algorithm.

        Let $A = (a_{i,j})$ be an $m \times n$ matrix over any
        commutative ring, with $m \le n$.   The permanent of $A$ is
        \[
        \text{per}(A) = \sum_\pi a_{1,\pi(1)}a_{2,\pi(2)} \cdots a_{m\,pi(m)}
        \]
        where the summation extends over all one-to-one functions $\pi$ from
        $\{1, \ldots, m\}$ to $\{1, \ldots, n\}$.

        The product $ a_{1,\pi(1)}a_{2,\pi(2)} \cdots a_{m,\pi(m)}$ is called
        diagonal product. So the permanent of an $m \times n$ matrix $A$ is the
        sum of all the diagonal products of $A$.

        Modification of theorem 7.1.1. from Brualdi and Ryser:
        Combinatorial Matrix Theory.
        Instead of deleting columns from $A$, we choose columns from $A$ and
        calculate the product of the row sums of the selected submatrix.

        INPUT:
            A -- matrix of size m x n with m <= n

        OUTPUT:
            permanent of matrix A

        EXAMPLES:
            sage: M = MatrixSpace(ZZ,4,4)
            sage: A = M([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
            sage: A.permanent()
            24

            sage: M = MatrixSpace(QQ,3,6)
            sage: A = M([1,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,1])
            sage: A.permanent()
            36

            sage: M = MatrixSpace(RR,3,6)
            sage: A = M([1.0,1.0,1.0,1.0,0,0,0,1.0,1.0,1.0,1.0,0,0,0,1.0,1.0,1.0,1.0])
            sage: A.permanent()
            36.0000000000000

        See Sloane's sequence OEIS A079908(3) = 36, "The Dancing School Problems"

            sage: print sloane_sequence(79908)                # optional (internet connection)
            Searching Sloane's online database...
            [79908, 'Solution to the Dancing School Problem with 3 girls: f(3,n).', [1, 4, 14, 36, 76, 140, 234, 364, 536, 756, 1030, 1364, 1764, 2236, 2786, 3420, 4144, 4964, 5886, 6916, 8060, 9324, 10714, 12236, 13896, 15700, 17654, 19764, 22036, 24476, 27090, 29884, 32864, 36036, 39406, 42980, 46764, 50764, 54986, 59436]]

            sage: M = MatrixSpace(ZZ,4,5)
            sage: A = M([1,1,0,1,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1,0])
            sage: A.permanent()
            32

            See Minc: Permanents, Example 2.1, p. 5.

            sage: M = MatrixSpace(QQ,2,2)
            sage: A = M([1/5,2/7,3/2,4/5])
            sage: A.permanent()
            103/175

            sage: R.<a> = PolynomialRing(ZZ)
            sage: A = MatrixSpace(R,2)([[a,1], [a,a+1]])
            sage: A.permanent()
            a^2 + 2*a

            sage: R.<x,y> = MPolynomialRing(ZZ,2)
            sage: A = MatrixSpace(R,2)([x, y, x^2, y^2])
            sage: A.permanent()
            x*y^2 + x^2*y


        AUTHOR:
            -- Jaap Spies (2006-02-16)
                Copyright (C) 2006 Jaap Spies <j.spies@hccnet.nl>
                Copyright (C) 2006 William Stein <wstein@gmail.com>
            -- Jaap Spies (2006-02-21): added definition of permanent

        NOTES:
            -- Currently optimized for dense matrices over QQ.
        """
        cdef Py_ssize_t m, n, r
        cdef int sn

        perm = 0
        m = self._nrows
        n = self._ncols
        if not m <= n:
            raise ValueError, "must have m <= n, but m (=%s) and n (=%s)"%(m,n)

        from sage.rings.arith import binomial
        for r from 1 <= r < m+1:
            lst = _combinations(range(n), r)
            tmp = []
            for cols in lst:
                tmp.append(self.prod_of_row_sums(cols))
            s = sum(tmp)
            # sn = (-1)^(m-r)
            if (m - r) % 2 == 0:
                sn = 1
            else:
                sn = -1
            perm = perm + sn * binomial(n-r, m-r) * s
        return perm


    def permanental_minor(self, Py_ssize_t k):
        r"""
        Calculates the permanental $k$-minor of a $m \times n$ matrix.

        This is the sum of the permanents of all possible $k$ by $k$
        submatices of $A$.

        See Brualdi and Ryser: Combinatorial Matrix Theory, p. 203.
        Note the typo $p_0(A) = 0$ in that reference!  For
        applications see Theorem 7.2.1 and Theorem 7.2.4.

        Note that the permanental $m$-minor equals $per(A)$.

        For a (0,1)-matrix $A$ the permanental $k$-minor counts the
        number of different selections of $k$ 1's of $A$ with no two
        of the 1's on the same line.

        INPUT:
            self -- matrix of size m x n with m <= n

        OUTPUT:
            permanental k-minor of matrix A

        EXAMPLES:
            sage: M = MatrixSpace(ZZ,4,4)
            sage: A = M([1,0,1,0,1,0,1,0,1,0,10,10,1,0,1,1])
            sage: A.permanental_minor(2)
            114

            sage: M = MatrixSpace(ZZ,3,6)
            sage: A = M([1,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,1])
            sage: A.permanental_minor(0)
            1
            sage: A.permanental_minor(1)
            12
            sage: A.permanental_minor(2)
            40
            sage: A.permanental_minor(3)
            36

        Note that if k == m the permanental k-minor equals per(A)

            sage: A.permanent()
            36

            sage: A.permanental_minor(5)
            0

        For C the "complement" of A:

            sage: M = MatrixSpace(ZZ,3,6)
            sage: C = M([0,0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0,0])
            sage: m, n = 3, 6
            sage: sum([(-1)^k * C.permanental_minor(k)*factorial(n-k)/factorial(n-m) for k in range(m+1)])
            36

            See Theorem 7.2.1 of Brualdi: and Ryser: Combinatorial Matrix Theory: per(A)

        AUTHOR:
            - Jaap Spies (2006-02-19)
        """
        m = self._nrows
        n = self._ncols
        if not m <= n:
            raise ValueError, "must have m <= n, but m (=%s) and n (=%s)"%(m,n)

        R = self._base_ring
        if k == 0:
            return R(1)
        if k > m:
            return R(0)

        k = int(k)
        pm = 0
        for cols in _combinations(range(n),k):
            for rows in _combinations(range(m),k):
                pm = pm + self.matrix_from_rows_and_columns(rows, cols).permanent()
        return pm

    def rook_vector(self, check = False):
        r"""
        Returns rook vector of this matrix.

        Let $A$ be a general $m$ by $n$ (0,1)-matrix with $m \le n$.
        We identify $A$ with a chessboard where rooks can be placed on
        the fields corresponding with $a_{ij} = 1$. The number $r_k =
        p_k(A)$ (the permanental $k$-minor) counts the number of ways
        to place $k$ rooks on this board so that no two rooks can
        attack another.

        The rook vector is the list consisting of $r_0, r_1, \ldots, r_m$.

        The rook polynomial is defined by $r(x) = \sum_{k=0}^m r_k x^k$.

        INPUT:
            self -- m by n matrix with m <= n
            check -- True or False (default), optional

        OUTPUT:
            rook vector

        EXAMPLES:
            sage: M = MatrixSpace(ZZ,3,6)
            sage: A = M([1,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,1])
            sage: A.rook_vector()
            [1, 12, 40, 36]

            sage: R.<x> = PolynomialRing(ZZ)
            sage: rv = A.rook_vector()
            sage: rook_polynomial = sum([rv[k] * x^k for k in range(len(rv))])
            sage: rook_polynomial
            36*x^3 + 40*x^2 + 12*x + 1

        AUTHOR:
            - Jaap Spies (2006-02-24)
        """
        m = self._nrows
        n = self._ncols
        if not m <= n:
            raise ValueError, "must have m <= n, but m (=%s) and n (=%s)"%(m,n)

        if check:
            # verify that self[i, j] in {0, 1}
            for i in range(m):
                for j in range(n):
                    x = self.get_unsafe(i, j)
                    if not (x == 0 or x == 1):
                        raise ValueError, "must have zero or one, but we have (=%s)"%x

        tmp = []
        for k in range(m+1):
            tmp.append(self.permanental_minor(k))
        return tmp


    def determinant(self):
        r"""
        Return the determinant of self.

        ALGORITHM: This is computed using the very stupid expansion by
        minors stupid \emph{naive generic algorithm}.  For matrices
        over more most rings more sophisticated algorithms can be
        used.  (Type \code{A.determinant?} to see what is done for a
        specific matrix A.)

        EXAMPLES:
            sage: A = MatrixSpace(Integers(8),3)([1,7,3, 1,1,1, 3,4,5])
            sage: A.determinant()
            6
            sage: A.determinant() is A.determinant()
            False
            sage: A.set_immutable()
            sage: A.determinant() is A.determinant()
            True

        We compute the determinant of the arbitrary 3x3 matrix:
            sage: R = PolynomialRing(QQ,9,'x')
            sage: A = matrix(R,3,R.gens())
            sage: A
            [x0 x1 x2]
            [x3 x4 x5]
            [x6 x7 x8]
            sage: A.determinant()
            -1*x2*x4*x6 + x2*x3*x7 + x1*x5*x6 - x1*x3*x8 - x0*x5*x7 + x0*x4*x8

        We create a matrix over $\Z[x,y]$ and compute its determinant.
            sage: R.<x,y> = MPolynomialRing(IntegerRing(),2)
            sage: A = MatrixSpace(R,2)([x, y, x**2, y**2])
            sage: A.determinant()
            x*y^2 - x^2*y
        """
        if self._nrows != self._ncols:
            raise ValueError, "self must be square"

        d = self.fetch('det')
        if not d is None: return d

        cdef Py_ssize_t i, n

        # if charpoly known, then det is easy.
        D = self.fetch('charpoly')
        if not D is None:
            c = D.iteritems()[0][1][0]
            if self._nrows % 2:
                c = -c
            d = self._coerce_element(c)
            self.cache('det', d)
            return d

        # if over an integral domain, get the det by computing charpoly.
        if self._base_ring.is_integral_domain():
            c = self.charpoly('x')[0]
            if self._nrows % 2:
                c = -c
            d = self._coerce_element(c)
            self.cache('det', d)
            return d

        # fall back to very very stupid algorithm
        # TODO: surely there is something much better, even in total generality...
        # this is ridiculous.
        n = self._ncols
        R = self.parent().base_ring()
        if n == 0:
            d = R(1)
            self.cache('det', d)
            return d

        elif n == 1:
            d = self.get_unsafe(0,0)
            self.cache('det', d)
            return d

        d = R(0)
        s = R(1)
        A = self.matrix_from_rows(range(1, n))
        sgn = R(-1)
        for i from 0 <= i < n:
            v = range(0,i) + range(i+1,n)
            B = A.matrix_from_columns(v)
            d = d + s*self.get_unsafe(0,i) * B.determinant()
            s = s*sgn

        self.cache('det', d)
        return d


    # shortcuts
    def det(self, *args, **kwds):
        """
        Synonym for self.determinant(...).

        EXAMPLES:
            sage: A = MatrixSpace(Integers(8),3)([1,7,3, 1,1,1, 3,4,5])
            sage: A.det()
            6
        """
        return self.determinant(*args, **kwds)

    def __abs__(self):
        """
        Synonym for self.determinant(...).

        EXAMPLES:
            sage: a = matrix(QQ, 2,2, [1,2,3,4]); a
            [1 2]
            [3 4]
            sage: abs(a)
            -2
        """
        return self.determinant()

    def characteristic_polynomial(self, *args, **kwds):
        """
        Synonym for self.charpoly(...).

        EXAMPLES:
            sage: a = matrix(QQ, 2,2, [1,2,3,4]); a
            [1 2]
            [3 4]
            sage: a.characteristic_polynomial('T')
            T^2 - 5*T - 2
        """
        return self.charpoly(*args, **kwds)

    def charpoly(self, var, algorithm="hessenberg"):
        r"""
        Return the characteristic polynomial of self, as a polynomial
        over the base ring.

        ALGORITHM: Compute the Hessenberg form of the matrix and read
        off the characteristic polynomial from that.  The result is
        cached.

        INPUT:
            var -- a variable name
            algorithm -- string:
                  'hessenberg' -- default (use Hessenberg form of matrix)

        EXAMPLES:
        First a matrix over $\Z$:
            sage: A = MatrixSpace(ZZ,2)( [1,2,  3,4] )
            sage: f = A.charpoly('x')
            sage: f
            x^2 - 5*x - 2
            sage: f.parent()
            Univariate Polynomial Ring in x over Integer Ring
            sage: f(A)
            [0 0]
            [0 0]

        An example over $\Q$:
            sage: A = MatrixSpace(QQ,3)(range(9))
            sage: A.charpoly('x')
            x^3 - 12*x^2 - 18*x
            sage: A.trace()
            12
            sage: A.determinant()
            0

        We compute the characteristic polynomial of a matrix over
        the polynomial ring $\Z[a]$:
            sage: R.<a> = PolynomialRing(ZZ)
            sage: M = MatrixSpace(R,2)([a,1,  a,a+1]); M
            [    a     1]
            [    a a + 1]
            sage: f = M.charpoly('x'); f
            x^2 + (-2*a - 1)*x + a^2
            sage: f.parent()
            Univariate Polynomial Ring in x over Univariate Polynomial Ring in a over Integer Ring
            sage: M.trace()
            2*a + 1
            sage: M.determinant()
            a^2

        We compute the characteristic polynomial of a matrix over the
        multi-variate polynomial ring $\Z[x,y]$:
            sage: R.<x,y> = MPolynomialRing(ZZ,2)
            sage: A = MatrixSpace(R,2)([x, y, x^2, y^2])
            sage: f = A.charpoly('x'); f
            x^2 + (-1*y^2 - x)*x + x*y^2 - x^2*y

        It's a little difficult to distinguish the variables.  To fix this,
        we temporarily view the indeterminate as $Z$:
            sage: with localvars(f.parent(), 'Z'): print f
            Z^2 + (-1*y^2 - x)*Z + x*y^2 - x^2*y

        We could also compute f in terms of Z from the start:
            sage: A.charpoly('Z')
            Z^2 + (-1*y^2 - x)*Z + x*y^2 - x^2*y
        """
        D = self.fetch('charpoly')
        if not D is None:
            if D.has_key(var):
                return D[var]
        else:
            D = {}
            self.cache('charpoly',D)

        f = self._charpoly_hessenberg(var)
        D[var] = f   # this caches it.
        return f


    def fcp(self, var):
        """
        Return the factorization of the characteristic polynomial of
        self.

        INPUT:
            var -- name of variable of charpoly

        EXAMPLES:
            sage: M = MatrixSpace(QQ,3,3)
            sage: A = M([1,9,-7,4/5,4,3,6,4,3])
            sage: A.fcp('x')
            (x^3 - 8*x^2 + 209/5*x - 286)
            sage: A = M([3, 0, -2, 0, -2, 0, 0, 0, 0])
            sage: A.fcp('x')
            (x - 3) * x * (x + 2)
        """
        return self.charpoly(var).factor()

##     def minimal_polynomial(self, var, algorithm=''):
##         """
##         Synonym for self.charpoly(...).

##         EXAMPLES:
##             sage: ???
##         """
##         return self.minpoly(*args, **kwds)

##     def minpoly(self, *args, **kwds):
##         """
##         EXAMPLES:
##             sage: ???
##         """
##         raise NotImplementedError

    def denominator(self):
        r"""
        Return the least common multiple of the denominators of the
        elements of self.

        If there is no denominator function for the base field, or no
        LCM function for the denominators, raise a TypeError.

        EXAMPLES:
            sage: A = MatrixSpace(QQ,2)(['1/2', '1/3', '1/5', '1/7'])
            sage: A.denominator()
            210

        Denominators are note defined for real numbers:
            sage: A = MatrixSpace(RealField(),2)([1,2,3,4])
            sage: A.denominator()
            Traceback (most recent call last):
            ...
            TypeError: denominator not defined for elements of the base ring

        We can even compute the denominator of matrix over the fraction field
        of $\Z[x]$.
            sage: K.<x> = Frac(ZZ['x'])
            sage: A = MatrixSpace(K,2)([1/x, 2/(x+1), 1, 5/(x^3)])
            sage: A.denominator()
            x^4 + x^3

        Here's an example involving a cyclotomic field:
            sage: K.<z> = CyclotomicField(3)
            sage: M = MatrixSpace(K,3,sparse=True)
            sage: A = M([(1+z)/3,(2+z)/3,z/3,1,1+z,-2,1,5,-1+z])
            sage: print A
            [1/3*z + 1/3 1/3*z + 2/3       1/3*z]
            [          1       z + 1          -2]
            [          1           5       z - 1]
            sage: print A.denominator()
            3
        """
        if self.nrows() == 0 or self.ncols() == 0:
            return integer.Integer(1)
        R = self.base_ring()
        x = self.list()
        try:
            d = x[0].denominator()
        except AttributeError:
            raise TypeError, "denominator not defined for elements of the base ring"
        try:
            for y in x:
                d = d.lcm(y.denominator())
        except AttributeError:
            raise TypeError, "lcm function not defined for elements of the base ring"
        return d


    def trace(self):
        """
        Return the trace of self, which is the sum of the
        diagonal entries of self.

        INPUT:
            self -- a square matrix
        OUTPUT:
            element of the base ring of self
        EXAMPLES:
        """
        if self._nrows != self._ncols:
            raise ArithmeticError, "matrix must be square"
        R = self._base_ring
        cdef Py_ssize_t i
        cdef object s
        s = R(0)
        for i from 0 <= i < self._nrows:
            s = s + self.get_unsafe(i,i)
        return s

    #####################################################################################
    # Generic Hessenberg Form and charpoly algorithm
    #####################################################################################
    def hessenberg_form(self):
        """
        Return Hessenberg form of self.

        If the base ring is merely an integral domain (and not a
        field), the Hessenberg form will (in general) only be defined
        over the fraction field of the base ring.

        EXAMPLES:
            sage: A = matrix(ZZ,4,[2, 1, 1, -2, 2, 2, -1, -1, -1,1,2,3,4,5,6,7])
            sage: h = A.hessenberg_form(); h
            [    2  -7/2 -19/5    -2]
            [    2   1/2 -17/5    -1]
            [    0  25/4  15/2   5/2]
            [    0     0  58/5     3]
            sage: parent(h)
            Full MatrixSpace of 4 by 4 dense matrices over Rational Field
            sage: A.hessenbergize()
            Traceback (most recent call last):
            ...
            TypeError: Hessenbergize only possible for matrices over a field
        """
        X = self.fetch('hessenberg_form')
        if not X is None:
            return X
        R = self._base_ring
        if not R.is_field():
            try:
                K = self._base_ring.fraction_field()
                H = self.change_ring(K)
                H.hessenbergize()
            except TypeError, msg:
                raise TypeError, "%s\nHessenberg form only possible for matrices over a field"%msg
        else:
            H = self.copy()
            H.hessenbergize()
        #end if
        self.cache('hessenberg_form', H)
        return H

    def hessenbergize(self):
        """
        Tranform self to Hessenberg form.

        The hessenberg form of a matrix $A$ is a matrix that is
        similar to $A$, so has the same characteristic polynomial as
        $A$, and is upper triangular except possible for entries right
        below the diagonal.

        ALGORITHM: See Henri Cohen's first book.

        EXAMPLES:
            sage: A = MatrixSpace(QQ,3)([2, 1, 1, -2, 2, 2, -1, -1, -1])
            sage: A.hessenberg_form()
            [  2 3/2   1]
            [ -2   3   2]
            [  0  -3  -2]

            sage: A = MatrixSpace(QQ,4)([2, 1, 1, -2, 2, 2, -1, -1, -1,1,2,3,4,5,6,7])
            sage: A.hessenberg_form()
            [    2  -7/2 -19/5    -2]
            [    2   1/2 -17/5    -1]
            [    0  25/4  15/2   5/2]
            [    0     0  58/5     3]
        """
        tm = verbose("Computing Hessenberg Normal Form of %sx%s matrix"%(n,n))

        if not self.is_square():
            raise TypeError, "self must be square"

        if not self._base_ring.is_field():
            raise TypeError, "Hessenbergize only possible for matrices over a field"

        self.check_mutability()

        cdef Py_ssize_t i, j, m, n, r
        zero = self._base_ring(0)
        one = self._base_ring(1)
        n = self._nrows
        for m from 1 <= m < n-1:
            # Search for a non-zero entry in column m-1
            i = -1
            for r from m+1 <= r < n:
                if self.get_unsafe(r, m-1) != zero:
                    i = r
                    break
            if i != -1:
                # Found a nonzero entry in column m-1 that is strictly below row m
                # Now set i to be the first nonzero position >= m in column m-1
                if self.get_unsafe(m,m-1) != zero:
                    i = m
                t = self.get_unsafe(i,m-1)
                t_inv = None
                if i > m:
                    self.swap_rows_c(i,m)
                    # We must do the corresponding column swap to
                    # maintain the characteristic polynomial (which is
                    # an invariant of Hessenberg form)
                    self.swap_columns_c(i,m)
                # Now the nonzero entry in position (m,m-1) is t.
                # Use t to clear the entries in column m-1 below m.
                for j from m+1 <= j < n:
                    x = self.get_unsafe(j, m-1)
                    if x != zero:
                        if t_inv is None:
                            t_inv = one / t
                        u = x * t_inv
                        self.add_multiple_of_row_c(j, m, -u, 0)
                        # To maintain charpoly, do the corresponding column operation,
                        # which doesn't mess up the matrix, since it only changes
                        # column m, and we're only worried about column m-1 right now.
                        # Add u*column_j to column_m.
                        self.add_multiple_of_column_c(m, j, u, 0)
        verbose("Finished Hessenberg Normal Form of %sx%s matrix"%(n,n),tm)



    def _charpoly_hessenberg(self, var):
        """
        Transforms self in place to its Hessenberg form then computes
        and returns the coefficients of the characteristic polynomial of
        this matrix.

        INPUT:
            var -- name of the indeterminate of the charpoly.

        The characteristic polynomial is represented as a vector of
        ints, where the constant term of the characteristic polynomial
        is the 0th coefficient of the vector.

        EXAMPLES:
            sage: matrix(QQ,3,range(9))._charpoly_hessenberg('Z')
            Z^3 - 12*Z^2 - 18*Z
            sage: matrix(ZZ,3,range(9))._charpoly_hessenberg('Z')
            Z^3 - 12*Z^2 - 18*Z
            sage: matrix(GF(7),3,range(9))._charpoly_hessenberg('Z')
            Z^3 + 2*Z^2 + 3*Z
            sage: matrix(QQ['x'],3,range(9))._charpoly_hessenberg('Z')
            Z^3 + (-12)*Z^2 + (-18)*Z
            sage: matrix(ZZ['ZZ'],3,range(9))._charpoly_hessenberg('Z')
            Z^3 + (-12)*Z^2 + (-18)*Z
        """
        if self._nrows != self._ncols:
            raise ArithmeticError, "charpoly not defined for non-square matrix."

        # Replace self by its Hessenberg form
        cdef Matrix H
        H = self.hessenberg_form()

        # We represent the intermediate polynomials that come up in
        # the calculations as rows of an (n+1)x(n+1) matrix, since
        # we've implemented basic arithmetic with such a matrix.
        # Please see the generic implementation of charpoly in
        # matrix.py to see more clearly how the following algorithm
        # actually works.  (The implementation is clearer (but slower)
        # if one uses polynomials to represent polynomials instead of
        # using the rows of a matrix.)  Also see Cohen's first GTM,
        # Algorithm 2.2.9.

        cdef Py_ssize_t i, m, n,
        n = self._nrows

        cdef Matrix c
        c = H.new_matrix(nrows=n+1,ncols=n+1)    # the 0 matrix
        one = H._coerce_element(1)
        c.set_unsafe(0,0,one)

        for m from 1 <= m <= n:
            # Set the m-th row of c to (x - H[m-1,m-1])*c[m-1] = x*c[m-1] - H[m-1,m-1]*c[m-1]
            # We do this by hand by setting the m-th row to c[m-1]
            # shifted to the right by one.  We then add
            # -H[m-1,m-1]*c[m-1] to the resulting m-th row.
            for i from 1 <= i <= n:
                c.set_unsafe(m, i, c.get_unsafe(m-1,i-1))
            c.add_multiple_of_row_c(m, m-1, -H.get_unsafe(m-1, m-1), 0)
            t = one
            for i from 1 <= i < m:
                t = t * H.get_unsafe(m-i,m-i-1)
                # Set the m-th row of c to c[m] - t*H[m-i-1,m-1]*c[m-i-1]
                c.add_multiple_of_row_c(m, m-i-1, - t*H.get_unsafe(m-i-1,m-1), 0)

        # The answer is now the n-th row of c.
        v = PyList_New(n+1)     # this is really sort of v = []..."
        for i from 0 <= i <= n:
            # Finally, set v[i] = c[n,i]
            o = c.get_unsafe(n,i)
            Py_INCREF(o); PyList_SET_ITEM(v, i, o)

        R = self._base_ring[var]    # polynomial ring over the base ring
        return R(v)

    #####################################################################################
    # Decomposition: kernel, image, decomposition
    #####################################################################################
    def nullity(self):
        """
        Return the nullity of this matrix, which is the dimension
        of the kernel.

        EXAMPLES:
            sage: A = matrix(QQ,3,range(9))
            sage: A.nullity()
            1

            sage: A = matrix(ZZ,3,range(9))
            sage: A.nullity()
            1
        """
        # Use that rank + nullity = number of columns
        return self.ncols() - self.rank()

    def kernel(self, *args, **kwds):
        r"""
        Return the kernel of this matrix, as a vector space.

        INPUT:
            -- all additional arguments to the kernel function
               are passed directly onto the echelon call.

        \algorithm{Elementary row operations don't change the kernel,
        since they are just right multiplication by an invertible
        matrix, so we instead compute kernel of the column echelon
        form.  More precisely, there is a basis vector of the kernel
        that corresponds to each non-pivot row.  That vector has a 1
        at the non-pivot row, 0's at all other non-pivot rows, and for
        each pivot row, the negative of the entry at the non-pivot row
        in the column with that pivot element.}

        \note{Since we view matrices as acting on the right, but have
        functions for reduced \emph{row} echelon forms, we instead
        compute the reduced row echelon form of the transpose of this
        matrix, which is the reduced column echelon form.}

        EXAMPLES:

        A kernel of dimension one over $\Q$:
            sage: A = MatrixSpace(QQ, 3)(range(9))
            sage: A.kernel()
            Vector space of degree 3 and dimension 1 over Rational Field
            Basis matrix:
            [ 1 -2  1]

        A trivial kernel:
            sage: A = MatrixSpace(QQ, 2)([1,2,3,4])
            sage: A.kernel()
            Vector space of degree 2 and dimension 0 over Rational Field
            Basis matrix:
            []

        Kernel of a zero matrix:
            sage: A = MatrixSpace(QQ, 2)(0)
            sage: A.kernel()
            Vector space of degree 2 and dimension 2 over Rational Field
            Basis matrix:
            [1 0]
            [0 1]

        Kernel of a non-square matrix:
            sage: A = MatrixSpace(QQ,3,2)(range(6))
            sage: A.kernel()
            Vector space of degree 3 and dimension 1 over Rational Field
            Basis matrix:
            [ 1 -2  1]

        The 2-dimensional kernel of a matrix over a cyclotomic field:
            sage: K = CyclotomicField(12); a=K.0
            sage: M = MatrixSpace(K,4,2)([1,-1, 0,-2, 0,-a**2-1, 0,a**2-1])
            sage: M
            [             1             -1]
            [             0             -2]
            [             0 -zeta12^2 - 1]
            [             0  zeta12^2 - 1]
            sage: M.kernel()
            Vector space of degree 4 and dimension 2 over Cyclotomic Field of order 12 and degree 4
            Basis matrix:
            [               0                1                0     -2*zeta12^2]
            [               0                0                1 -2*zeta12^2 + 1]

        A nontrivial kernel over a complicated base field.
            sage: K = FractionField(MPolynomialRing(QQ, 2, 'x'))
            sage: M = MatrixSpace(K, 2)([[K.1, K.0], [K.1, K.0]])
            sage: M
            [x1 x0]
            [x1 x0]
            sage: M.kernel()
            Vector space of degree 2 and dimension 1 over Fraction Field of Polynomial Ring in x0, x1 over Rational Field
            Basis matrix:
            [ 1 -1]
        """
        K = self.fetch('kernel')
        if not K is None:
            return K
        R = self._base_ring

        if self._nrows == 0:    # from a 0 space
            V = sage.modules.free_module.VectorSpace(R, self._nrows)
            Z = V.zero_subspace()
            self.cache('kernel', Z)
            return Z

        elif self._ncols == 0:  # to a 0 space
            Z = sage.modules.free_module.VectorSpace(R, self._nrows)
            self.cache('kernel', Z)
            return Z

        if is_NumberField(R):
            A = self._pari_().mattranspose()
            B = A.matker()
            n = self._nrows
            V = sage.modules.free_module.VectorSpace(R, n)
            basis = eval('[V([R(x) for x in b]) for b in B]', {'V':V, 'B':B, 'R':R})
            Z = V.subspace(basis)
            self.cache('kernel', Z)
            return Z

        E = self.transpose().echelon_form(*args, **kwds)
        pivots = E.pivots()
        pivots_set = set(pivots)
        basis = []
        VS = sage.modules.free_module.VectorSpace
        V = VS(R, self.nrows())
        ONE = R(1)
        for i in xrange(self._nrows):
            if not (i in pivots_set):
                v = V(0)
                v[i] = ONE
                for r in range(len(pivots)):
                    v[pivots[r]] = -E[r,i]
                basis.append(v)
        W = V.subspace(basis)
        if W.dimension() != len(basis):
            raise RuntimeError, "bug in kernel function in matrix.pyx -- basis got from echelon form not a basis."
        self.cache('kernel', W)
        return W



    def decomposition(self, is_diagonalizable=False, dual=False):
        """
        Returns the decomposition of the free module on which this
        matrix acts from the right, along with whether this matrix
        acts irreducibly on each factor.  The factors are guaranteed
        to be sorted in the same way as the corresponding factors of
        the characteristic polynomial.

        Let A be the matrix acting from the on the vector space V of
        column vectors.  Assume that A is square.  This function
        computes maximal subspaces W_1, ..., W_n corresponding to
        Galois conjugacy classes of eigenvalues of A.  More precisely,
        let f(X) be the characteristic polynomial of A.  This function
        computes the subspace $W_i = ker(g_(A)^n)$, where g_i(X) is an
        irreducible factor of f(X) and g_i(X) exactly divides f(X).
        If the optional parameter is_diagonalizable is True, then we
        let W_i = ker(g(A)), since then we know that ker(g(A)) =
        $ker(g(A)^n)$.

        If dual is True, also returns the corresponding decomposition
        of V under the action of the transpose of A.  The factors are
        guarenteed to correspond.

        OUTPUT:
            Sequence -- list of pairs (V,t), where V is a vector spaces
                    and t is a bool, and t is True exactly when the
                    charpoly of self on V is irreducible.

            (optional) list -- list of pairs (W,t), where W is a vector
                    space and t is a bool, and t is True exactly
                    when the charpoly of the transpose of self on W
                    is irreducible.

        EXAMPLES:
            sage: MS1 = MatrixSpace(ZZ,4)
            sage: MS2 = MatrixSpace(QQ,6)
            sage: A = MS1.matrix([3,4,5,6,7,3,8,10,14,5,6,7,2,2,10,9])
            sage: B = MS2(range(36))
            sage: B*11   # random output
            [-11  22 -11 -11 -11 -11]
            [ 11 -22 -11 -22  11  11]
            [-11 -11 -11 -22 -22 -11]
            [-22  22 -22  22 -11  11]
            [ 22 -11  11 -22  11  22]
            [ 11  11  11 -22  22  22]
            sage: decomposition(A)
            [
            (Ambient free module of rank 4 over the principal ideal domain Integer Ring, 1)
            ]
            sage: decomposition(B)
            [
            (Vector space of degree 6 and dimension 2 over Rational Field
            Basis matrix:
            [ 1  0 -1 -2 -3 -4]
            [ 0  1  2  3  4  5], 1),
            (Vector space of degree 6 and dimension 4 over Rational Field
            Basis matrix:
            [ 1  0  0  0 -5  4]
            [ 0  1  0  0 -4  3]
            [ 0  0  1  0 -3  2]
            [ 0  0  0  1 -2  1], 0)
            ]
        """
        if not self.is_square():
            raise ArithmeticError, "self must be a square matrix"

        if self.nrows() == 0:
            return decomp_seq([])

        f = self.charpoly('x')
        E = decomp_seq([])

        # Idea: For optimization, could compute powers of self
        #       up to max degree of any factor.  Then get g(self)
        #       by taking a linear combination.

        if dual:
            Edual = decomp_seq([])
        F = f.factor()
        if len(F) == 1:
            V = sage.modules.free_module.FreeModule(
                              self.base_ring(), self.nrows())
            m = F[0][1]
            if dual:
                return decomp_seq([(V,m==1)]), decomp_seq([(V,m==1)])
            else:
                return decomp_seq([(V,m==1)])
        F.sort()
        for g, m in f.factor():
            if is_diagonalizable:
                B = g(self)
            else:
                B = g(self) ** m
            E.append((B.kernel(), m==1))
            if dual:
                Edual.append((B.transpose().kernel(), m==1))
        if dual:
            return E, Edual
        return E

    def decomposition_of_subspace(self, M, is_diagonalizable=False):
        """
        Suppose the right action of self on M leaves M
        invariant. Return the decomposition of M as a list of pairs
        (W, is_irred) where is_irred is True if the charpoly of self
        acting on the factor W is irreducible.

        EXAMPLES:
            sage: t = matrix(QQ, 3, [3, 0, -2, 0, -2, 0, 0, 0, 0]); t
            [ 3  0 -2]
            [ 0 -2  0]
            [ 0  0  0]
            sage: t.fcp('X')   # factored charpoly
            (X - 3) * X * (X + 2)
            sage: v = kernel(t*(t+2)); v   # an invariant subspace
            Vector space of degree 3 and dimension 2 over Rational Field
            Basis matrix:
            [0 1 0]
            [0 0 1]
            sage: D = t.decomposition_of_subspace(v); D
            [
            (Vector space of degree 3 and dimension 1 over Rational Field
            Basis matrix:
            [0 0 1], 1),
            (Vector space of degree 3 and dimension 1 over Rational Field
            Basis matrix:
            [0 1 0], 1)
            ]
            sage: t.restrict(D[0][0])
            [0]
            sage: t.restrict(D[1][0])
            [-2]
        """
        if not sage.modules.free_module.is_FreeModule(M):
            raise TypeError, "M must be a free module."
        if not self.is_square():
            raise ArithmeticError, "matrix must be square"
        if M.base_ring() != self.base_ring():
            raise ArithmeticError, "base rings are incompatible"
        if M.degree() != self.ncols():
            raise ArithmeticError, \
               "M must be a subspace of an %s-dimensional space"%self.ncols()

        time = verbose(t=0)

        # 1. Restrict
        B = self.restrict(M)
        time0 = verbose("restrict -- ", time)

        # 2. Decompose restriction
        D = B.decomposition(is_diagonalizable=is_diagonalizable, dual=False)

        assert sum(eval('[A.dimension() for A,_ in D]',{'D':D})) == M.dimension(), \
               "bug in decomposition; " + \
               "the sum of the dimensions of the factors must equal the dimension of the acted on space."

        # 3. Lift decomposition to subspaces of ambient vector space.
        # Each basis vector for an element of D defines a linear combination
        # of the basis of W, and these linear combinations define the
        # corresponding subspaces of the ambient space M.

        verbose("decomposition -- ", time0)
        C = M.basis_matrix()
        Z = M.ambient_vector_space()

        D = eval('[(Z.subspace([x*C for x in W.basis()]), is_irred) for W, is_irred in D]',\
                 {'C':C, 'D':D, 'Z':Z})
        D = decomp_seq(D)

        verbose(t=time)
        return D

    def restrict(self, V, check=True):
        """
        Returns the matrix that defines the action of self on the
        chosen basis for the invariant subspace V.  If V is an
        ambient, returns self (not a copy of self).

        INPUT:
            V -- vector subspace
            check -- (optional) default: True; if False may not check
                     that V is invariant (hence can be faster).
        OUTPUT:
            a matrix

        WARNING:
        This function returns an nxn matrix, where V has dimension n.
        It does \emph{not} check that V is in fact invariant under
        self, unless check is True (not the default).

        EXAMPLES:
            sage: V = VectorSpace(QQ, 3)
            sage: M = MatrixSpace(QQ, 3)
            sage: A = M([1,2,0, 3,4,0, 0,0,0])
            sage: W = V.subspace([[1,0,0], [0,1,0]])
            sage: A.restrict(W)
            [1 2]
            [3 4]
            sage: A.restrict(W, check=True)
            [1 2]
            [3 4]

        We illustrate the warning about invariance not being checked
        by default, by giving a non-invariant subspace.  With the default
        check=False this function returns the 'restriction' matrix, which
        is meaningless as check=True reveals.
            sage: W2 = V.subspace([[1,0,0], [0,1,1]])
            sage: A.restrict(W2, check=False)
            [1 2]
            [3 4]
            sage: A.restrict(W2, check=True)
            Traceback (most recent call last):
            ...
            ArithmeticError: subspace is not invariant under matrix
        """
        if not isinstance(V, sage.modules.free_module.FreeModule_generic):
            raise TypeError, "V must be a Vector Space"
        if V.base_field() != self.base_ring():
            raise TypeError, "base rings must be the same"
        if V.degree() != self.nrows():
            raise IndexError, "degree of V (=%s) must equal number of rows of self (=%s)"%(\
                V.degree(), self.nrows())
        if V.rank() == 0:
            return self.new_matrix(nrows=0, ncols=0)

        if not check and V.base_ring().is_field() and not V.has_user_basis():
            B = V.echelonized_basis_matrix()
            P = B.pivots()
            return B*self.matrix_from_columns(P)
        else:
            n = V.rank()
            try:
                # todo optimize so only involves matrix multiplies ?
                C = eval('[V.coordinate_vector(b*self) for b in V.basis()]',{'V':V, 'self':self})
            except ArithmeticError:
                raise ArithmeticError, "subspace is not invariant under matrix"
            return self.new_matrix(n, n, C, sparse=False)

    def restrict_domain(self, V):
        """
        Compute the matrix relative to the basis for V on the domain
        obtained by restricting self to V, but not changing the
        codomain of the matrix.  This is the matrix whose rows are the
        images of the basis for V.

        INPUT:
            V -- vector space (subspace of ambient space on which self acts)

        SEE ALSO: restrict()

        EXAMPLES:
            sage: V = VectorSpace(QQ, 3)
            sage: M = MatrixSpace(QQ, 3)
            sage: A = M([1,2,0, 3,4,0, 0,0,0])
            sage: W = V.subspace([[1,0,0], [1,2,3]])
            sage: A.restrict_domain(W)
            [1 2 0]
            [3 4 0]
            sage: W2 = V.subspace_with_basis([[1,0,0], [1,2,3]])
            sage: A.restrict_domain(W2)
            [ 1  2  0]
            [ 7 10  0]
        """
        e = eval('[b*self for b in V.basis()]', {'self':self, 'V':V})
        return self.new_matrix(V.dimension(), self.ncols(), e)

    def eigenspaces(self, var='a'):
        """
        Return a list of pairs
             (e, V)
        where e runs through all eigenvalues (up to Galois conjugation)
        of this matrix, and V is the corresponding eigenspace.

        INPUT:
            var -- variable name used to represent elements of
                   the root field of each irreducible factor of
                   the characteristic polynomial
                   I.e., if var='a', then the root fields
                   will be in terms of a0, a1, a2, ..., ak.

        WARNING: Uses a somewhat naive algorithm (simply factors the
        characteristic polynomial and computes kernels directly over
        the extension field).  TODO: Implement the better algorithm
        that is in dual_eigenvector in sage/hecke/module.py.

        EXAMPLES:
        We compute the eigenspaces of the matrix of the Hecke operator
        $T_2$ on level 43 modular symbols.
            sage: # A = ModularSymbols(43).T(2).matrix()
            sage: A = matrix(QQ, 7, [3, 0, 0, 0, 0, 0, -1, 0, -2, 1, 0, 0, 0, 0, 0, -1, 1, 1, 0, -1, 0, 0, -1, 0, -1, 2, -1, 1, 0, -1, 0, 1, 1, -1, 1, 0, 0, -2, 0, 2, -2, 1, 0, 0, -1, 0, 1, 0, -1]); A
            [ 3  0  0  0  0  0 -1]
            [ 0 -2  1  0  0  0  0]
            [ 0 -1  1  1  0 -1  0]
            [ 0 -1  0 -1  2 -1  1]
            [ 0 -1  0  1  1 -1  1]
            [ 0  0 -2  0  2 -2  1]
            [ 0  0 -1  0  1  0 -1]
            sage: A.eigenspaces()
            [
            (3, [
            (1, 0, 1/7, 0, -1/7, 0, -2/7)
            ]),
            (-2, [
            (0, 1, 0, 1, -1, 1, -1),
            (0, 0, 1, 0, -1, 2, -1)
            ]),
            (a, [
            (0, 1, 0, -1, -a - 1, 1, -1),
            (0, 0, 1, 0, -1, 0, -a + 1)
            ])
            ]

        Next we compute the eigenspaces over the finite field
        of order 11:

            sage: # A = ModularSymbols(43, base_ring=GF(11), sign=1).T(2).matrix()
            sage: A = matrix(QQ, 4, [3, 9, 0, 0, 0, 9, 0, 1, 0, 10, 9, 2, 0, 9, 0, 2])
            sage: A.eigenspaces()
            [
            (9, [
            (0, 0, 1, 5)
            ]),
            (3, [
            (1, 6, 0, 6)
            ]),
            (x, [
            (0, 1, 0, 5*x + 10)
            ])
            ]

        Finally, we compute the eigenspaces of a $3\times 3$ matrix.

            sage: A = Matrix(QQ,3,3,range(9))
            sage: A.eigenspaces()
            [
            (0, [
            (1, -2, 1)
            ]),
            (a, [
            (1, 1/15*a + 2/5, 2/15*a - 1/5)
            ])
            ]
        """
        x = self.fetch('eigenvectors')
        if not x is None:
            return x
        f = self.charpoly('x')
        G = f.factor()
        V = []
        i = 0
        for h, e in G:
            F = h.root_field('%s%s'%(var,i))
            i = i + 1
            W = (self.change_ring(F) - F.gen(0)).kernel()
            V.append((F.gen(0), W.basis()))
        V = Sequence(V, cr=True)
        self.cache('eigenvectors', V)
        return V


    #####################################################################################
    # Generic Echelon Form
    ###################################################################################
    def echelonize(self, algorithm="default", cutoff=0):
        r"""
        Transform self into a matrix in echelon form over the same
        base ring as self.

        INPUT:
            algorithm -- string, which algorithm to use (default: 'default')
                   'default' -- use a default algorithm, chosen by SAGE
                   'strassen' -- use a Strassen divide and conquer algorithm (if available)
            cutoff -- integer; only used if the Strassen algorithm is selected.

        EXAMPLES:
            sage: a = matrix(QQ,3,range(9)); a
            [0 1 2]
            [3 4 5]
            [6 7 8]
            sage: a.echelonize()
            sage: a
            [ 1  0 -1]
            [ 0  1  2]
            [ 0  0  0]

        An immutable matrix cannot be transformed into echelon form.
        Use \code{self.echelon_form()} instead:

            sage: a = matrix(QQ,3,range(9)); a.set_immutable()
            sage: a.echelonize()
            Traceback (most recent call last):
            ...
            ValueError: matrix is immutable; please change a copy instead (use self.copy()).
            sage: a.echelon_form()
            [ 1  0 -1]
            [ 0  1  2]
            [ 0  0  0]

        Echelon form over the integers is what is also classically often known as
        Hermite normal form:
            sage: a = matrix(ZZ,3,range(9))
            sage: a.echelonize(); a
            [ 3  0 -3]
            [ 0  1  2]
            [ 0  0  0]

        Echelon form is not defined for any integral domain; you may have to explicitly
        base extend to the fraction field, if that is what you want.
            sage: R.<x,y> = QQ[]
            sage: a = matrix(R, 2, [x,y,x,y])
            sage: a.echelonize()
            Traceback (most recent call last):
            ...
            ValueError: Echelon form not defined over this base ring.
            sage: b = a.change_ring(R.fraction_field())
            sage: b.echelon_form()
            [  1 y/x]
            [  0   0]

        Echelon form is not defined over arbitrary rings:
            sage: a = matrix(Integers(9),3,range(9))
            sage: a.echelon_form()
            Traceback (most recent call last):
            ...
            ValueError: Echelon form not defined over this base ring.
        """
        self.check_mutability()
        if algorithm == 'default':
            if self._will_use_strassen_echelon():
                algorithm = 'strassen'
            else:
                algorithm = 'classical'
        try:
            if algorithm == 'classical':
                self._echelon_in_place_classical()
            elif algorithm == 'strassen':
                self._echelon_strassen(cutoff)
            else:
                raise ValueError, "Unknown algorithm '%s'"%algorithm
        except ArithmeticError, msg:
            print msg
            raise ValueError, "Echelon form not defined over this base ring."

    def echelon_form(self, algorithm="default", cutoff=0):
        """
        Return the echelon form of self.

        INPUT:
            matrix -- an element A of a MatrixSpace

        OUTPUT:
            matrix -- The reduced row echelon form of A, as an
            immutable matrix.  Note that self is *not* changed by this
            command.  Use A.echelonize() to change A in place.

        EXAMPLES:
           sage: MS = MatrixSpace(QQ,2,3)
           sage: C = MS.matrix([1,2,3,4,5,6])
           sage: C.rank()
           2
           sage: C.nullity()
           1
           sage: C.echelon_form()
           [ 1  0 -1]
           [ 0  1  2]
        """
        x = self.fetch('echelon_form')
        if not x is None:
            return x
        E = self.copy()
        E.echelonize(algorithm = algorithm, cutoff=cutoff)
        E.set_immutable()  # so we can cache the echelon form.
        self.cache('echelon_form', E)
        self.cache('pivots', E.pivots())
        return E

    def _echelon_classical(self):
        """
        Return the echelon form of self.
        """
        E = self.fetch('echelon_classical')
        if not E is None:
            return E
        E = self.copy()
        E._echelon_in_place_classical()
        self.cache('echelon_classical', E)
        return E

    def _echelon_in_place_classical(self):
        """
        Return the echelon form of self and set the pivots of self.
        """
        cdef Py_ssize_t start_row, c, r, nr, nc, i
        if self.fetch('in_echelon_form'):
            return

        if not self._base_ring.is_field():
            raise ValueError, "Echelon form not defined over this base ring."

        self.check_mutability()

        start_row = 0
        nr = self._nrows
        nc = self._ncols
        pivots = []

        for c from 0 <= c < nc:
            if PyErr_CheckSignals(): raise KeyboardInterrupt
            for r from start_row <= r < nr:
                if self.get_unsafe(r, c) != 0:
                    pivots.append(c)
                    a_inverse = ~self.get_unsafe(r,c)
                    self.rescale_row(r, a_inverse, c)
                    self.swap_rows(r, start_row)
                    for i from 0 <= i < nr:
                        if i != start_row:
                            if self.get_unsafe(i,c) != 0:
                                minus_b = -self.get_unsafe(i, c)
                                self.add_multiple_of_row(i, start_row, minus_b, c)
                    start_row = start_row + 1
                    break
        self.cache('pivots', pivots)
        self.cache('in_echelon_form', True)

    #####################################################################################
    # Windowed Strassen Matrix Multiplication and Echelon
    # Precise algorithms invented and implemented by David Harvey and Robert Bradshaw
    # at William Stein's MSRI 2006 Summer Workshop on Modular Forms.
    #####################################################################################
    def _multiply_strassen(self, Matrix right, int cutoff=0):
        """
        Multiply self by the matrix right using a Strassen-based
        asymptotically fast arithmetic algorithm.

        ALGORITHM: Custom algorithm for arbitrary size matrices
        designed by David Harvey and Robert Bradshaw, based on
        Strassen's algorithm.

        INPUT:
            cutoff -- integer (default: 0 -- let class decide).

        EXAMPLES:
        sage: a = matrix(ZZ,4,range(16))
        sage: a._multiply_strassen(a,2)
        [ 56  62  68  74]
        [152 174 196 218]
        [248 286 324 362]
        [344 398 452 506]
        """
        if self._ncols != right._nrows:
            raise ArithmeticError, "Number of columns of self must equal number of rows of right."
        if not self._base_ring is right.base_ring():
            raise TypeError, "Base rings must be the same."

        if cutoff == 0:
            cutoff = self._strassen_default_cutoff(right)

        if cutoff <= 0:
            raise ValueError, "cutoff must be at least 1"

        output = self.new_matrix(self._nrows, right._ncols)

        self_window   = self.matrix_window()
        right_window  = right.matrix_window()
        output_window = output.matrix_window()

        strassen.strassen_window_multiply(output_window, self_window, right_window, cutoff)
        return output

    def _echelon_strassen(self, int cutoff=0):
        """
        In place Strassen echelon of self, and sets the pivots.

        ALGORITHM: Custom algorithm for arbitrary size matrices
        designed by David Harvey and Robert Bradshaw, based on
        Strassen's algorithm.

        EXAMPLES:
            sage: ?
        """
        self.check_mutability()

        if not self._base_ring.is_field():
            raise ValueError, "Echelon form not defined over this base ring."

        if cutoff == 0:
            cutoff = self._strassen_default_echelon_cutoff()

        if cutoff <= 0:
            raise ValueError, "cutoff must be at least 1"

        if self._nrows < cutoff or self._ncols < cutoff:
            self._echelon_in_place_classical()
            return

        pivots = strassen.strassen_echelon(self.matrix_window(), cutoff)
        self._set_pivots(pivots)


    def matrix_window(self, Py_ssize_t row=0, Py_ssize_t col=0,
                      Py_ssize_t nrows=-1, Py_ssize_t ncols=-1):
        """
        Return the requested matrix window.

        EXAMPLES:
            sage: ?
        """
        if nrows == -1:
            nrows = self._nrows
            ncols = self._ncols
        return matrix_window.MatrixWindow(self, row, col, nrows, ncols)

cdef decomp_seq(v):
    return Sequence(v, universe=tuple, check=False, cr=True)
