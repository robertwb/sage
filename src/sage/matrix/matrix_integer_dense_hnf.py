"""
Modular algorithm to compute Hermite normal forms of integer matrices.

AUTHORS:
    -- Clement Pernet and William Stein (2008-02-07): initial version

TODO:

   [ ] optimize double det
   [ ] more rows than columns
   [ ] more columns than rows
   [ ] degenerate cases -- fail nicely

"""

from copy import copy

from sage.misc.misc import verbose
from sage.matrix.constructor import random_matrix, matrix

from sage.rings.all import ZZ, QQ, previous_prime

def fastdet(A, times=1):
    """
    Likely to be correct fast det (no guarantee).
    """
    v = random_matrix(ZZ,A.nrows(), 1, x=-1,y=1)
    w = A.solve_right(v, check_rank=False)
    d = w.denominator()
    p = 46337
    for i in range(times):
        Amod = A._reduce(p)
        det = Amod.determinant() / d
        m = ZZ(det)
        if m >= p//2:
            m -= p
        d *= m
        p = previous_prime(p)
    return d

def doubleDet (A, b, c):
    """
    Compute the determinants of the stacked matrices A.stack(b) and A.stack(c).

    INPUT:
        A -- an (n-1) x n matrix
        b -- an 1 x n matrix
        c -- an 1 x n matrix

    OUTPUT:
        a pair of two integers.
    """
    t = verbose('starting double det')
    d1 = fastdet(A.stack(b))
    d2 = fastdet(A.stack(c))
    verbose('finished double det', t)
    return (d1,d2)

def add_column(B, H_B, a):
    """
    The add column procedure.

    INPUT:
        B   -- a non-singular square matrix
        H_B -- the Hermite normal form of B
        a   -- a column vector

    OUTPUT:
        x   -- a vector such that H' = H_B.augment(x) is the HNF of A = B.augment(a).
    """
    t0 = verbose('starting add_column')

    # We use a direct solve method without inverse.  This
    # is more clever than what is in Allan Steel's talk and
    # what is in that paper, in 2 ways -- (1) no inverse need
    # to be computed, and (2) we cleverly solve a vastly easier
    # system and recover the solution to the original system.

    t = verbose('starting optimized solve')

    # Here's how:
    # 1. We make a copy of B but with the last *nasty* row of B replaced
    #    by a random very nice row.
    C = copy(B)
    C[C.nrows()-1] = [1]*C.ncols()

    # 2. Then we find the unique solution to C * x = a
    #    (todo -- recover from bad case.)
    x = C.solve_right(a)

    # 3. We next delete the last row of B and find a basis vector k
    #    for the 1-dimensional kernel.
    D = B.matrix_from_rows(range(C.nrows()-1))
    N = D._rational_kernel_iml()
    if N.ncols() != 1:
        raise NotImplementedError, "need to recover gracefully from rank issues with matrix."
    k = N.matrix_from_columns([0])

    # 4. The sought for solution z to B*z = a is some linear combination
    #       z = x + alpha*k
    # and setting w to be the last row of B, this column vector z satisfies
    #       w * z = a'
    # where a' is the last entry of a.  Thus
    #       w * (x + alpha*k) = a'
    # so    w * x + alpha*w*k = a'
    # so    alpha*w*k  = a' - w*x.

    w = B[-1]  # last row of B
    a_prime = a[-1]
    lhs = w*k
    rhs = a_prime - w * x
    alpha = rhs[0] / lhs[0]
    z = x + alpha*k
    t = verbose('start matrix-vector multiply', t)
    HQ = H_B.change_ring(QQ)
    x = HQ * z
    verbose('done with matrix-vector multiply', t)
    x = x.change_ring(ZZ)

    verbose('finished add column -- overall time', t0)

    return x

def add_row(A, b, pivots):
    """
    The add row procedure.

    INPUT:
        A -- an n x (n-1) matrix in Hermite normal form
        b -- an n x 1 matrix
        pivots -- sorted list of integers; the pivot positions of A.

    OUTPUT:
        H -- the Hermite normal form of A.stack(b)
    """
    t = verbose('first add row')
    global X, v
    X = A
    v = b.row(0)
    z = A._add_row_and_maintain_echelon_form(b.row(0), pivots)
    verbose('finished add row', t)
    return z

def hnf(A):
    """
    INPUT:
        an n x m matrix A over the integers.
    OUTPUT:
        the Hermite normal form of A.
    """
    n = A.nrows()
    m = A.ncols()
    if n != m:
        raise NotImplementedError, "A must be square."

    t = verbose("starting slicings")
    B = A.matrix_from_rows(range(m-2)).matrix_from_columns(range(n-1))
    c = A.matrix_from_rows([m-2]).matrix_from_columns (range(n-1))
    d = A.matrix_from_rows([m-1]).matrix_from_columns (range(n-1))
    b = A.matrix_from_columns([n-1]).matrix_from_rows(range(m-2))
    verbose("done slicing", t)

    (d1,d2) = doubleDet (B,c,d)

    (g,k,l) = d1._xgcd (d2, minimal=True)

    W = B.stack (k*c + l*d)

    H = W._hnf_mod(2*g)

    x = add_column(B.stack(k*c+l*d), H, b.stack(matrix(1,1,[k*A[m-2,m-1] + l*A[m-1,m-1]])))

    Hprime = H.augment(x)

    pivots = range(Hprime.nrows())

    Hprime, pivots = add_row(Hprime, A.matrix_from_rows([m-2]), pivots)
    Hprime, pivots = add_row(Hprime, A.matrix_from_rows([m-1]), pivots)

    H = Hprime.matrix_from_rows(range(m))
    return H
