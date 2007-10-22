"""
Misc matrix algorithms

Code goes here mainly when it needs access to the internal structure
of several classes, and we want to avoid circular cimports.
"""

include "../ext/interrupt.pxi"
include "../ext/cdefs.pxi"
include '../ext/stdsage.pxi'

include '../modules/binary_search.pxi'
include '../modules/vector_integer_sparse_h.pxi'
include '../modules/vector_integer_sparse_c.pxi'
include '../modules/vector_rational_sparse_h.pxi'
include '../modules/vector_rational_sparse_c.pxi'
include '../modules/vector_modn_sparse_h.pxi'
include '../modules/vector_modn_sparse_c.pxi'

# mod_int isn't defined in stdio.h -- this is to fool SageX.
# cdef extern from "stdio.h":
#     ctypedef int mod_int
cdef extern from "../ext/multi_modular.h":
    ctypedef unsigned long mod_int
    mod_int MOD_INT_OVERFLOW


from matrix0 cimport Matrix
from matrix_modn_dense cimport Matrix_modn_dense
from matrix_modn_sparse cimport Matrix_modn_sparse
from matrix_integer_dense cimport Matrix_integer_dense
from matrix_integer_sparse cimport Matrix_integer_sparse
from matrix_rational_dense cimport Matrix_rational_dense
from matrix_rational_sparse cimport Matrix_rational_sparse

import matrix_modn_dense
import matrix_modn_sparse

from sage.rings.integer_ring   import ZZ
from sage.rings.rational_field import QQ
from sage.rings.integer cimport Integer
from sage.rings.arith import previous_prime, CRT_basis


from sage.misc.misc import verbose, get_verbose


def matrix_modn_dense_lift(Matrix_modn_dense A):
    cdef Py_ssize_t i, j
    cdef Matrix_integer_dense L
    L = Matrix_integer_dense.__new__(Matrix_integer_dense,
                                     A.parent().change_ring(ZZ),
                                     0, 0, 0)
    cdef mpz_t* L_row
    cdef mod_int* A_row
    for i from 0 <= i < A._nrows:
        L_row = L._matrix[i]
        A_row = A._matrix[i]
        for j from 0 <= j < A._ncols:
            mpz_init_set_si(L_row[j], A_row[j])
    L._initialized = 1
    return L

def matrix_modn_sparse_lift(Matrix_modn_sparse A):
    cdef Py_ssize_t i, j
    cdef Matrix_integer_sparse L
    L = Matrix_integer_sparse.__new__(Matrix_integer_sparse,
                                     A.parent().change_ring(ZZ),
                                     0, 0, 0)

    cdef mpz_vector* L_row
    cdef c_vector_modint* A_row
    for i from 0 <= i < A._nrows:
        L_row = &(L._matrix[i])
        A_row = &(A.rows[i])
        sage_free(L_row.entries)
        L_row.entries = <mpz_t*> sage_malloc(sizeof(mpz_t)*A_row.num_nonzero)
        L_row.num_nonzero = A_row.num_nonzero
        if L_row.entries == NULL:
            raise MemoryError, "error allocating space for sparse vector during sparse lift"
        sage_free(L_row.positions)
        L_row.positions = <Py_ssize_t*> sage_malloc(sizeof(Py_ssize_t)*A_row.num_nonzero)
        if L_row.positions == NULL:
            sage_free(L_row.entries)
            L_row.entries = NULL
            raise MemoryError, "error allocating space for sparse vector during sparse lift"
        for j from 0 <= j < A_row.num_nonzero:
            L_row.positions[j] = A_row.positions[j]
            mpz_init_set_si(L_row.entries[j], A_row.entries[j])
    return L


## VERSION without denom trick -- vastly slower!
##
## def matrix_integer_dense_rational_reconstruction(Matrix_integer_dense A, Integer N):
##     cdef Matrix_rational_dense R
##     R = Matrix_rational_dense.__new__(Matrix_rational_dense,
##                                       A.parent().change_ring(QQ), 0,0,0)
##     #cdef mpz_t denom   # lcm of denoms so far
##     for i from 0 <= i < A._nrows:
##         for j from 0 <= j < A._ncols:
##             mpq_rational_reconstruction(R._matrix[i][j], A._matrix[i][j], N.value)
##     return R

def matrix_integer_dense_rational_reconstruction(Matrix_integer_dense A, Integer N):
    cdef Matrix_rational_dense R
    R = Matrix_rational_dense.__new__(Matrix_rational_dense,
                                      A.parent().change_ring(QQ), 0,0,0)

    cdef mpz_t a, bnd, other_bnd, one, denom
    mpz_init_set_si(denom, 1)
    mpz_init(a)
    mpz_init_set_si(one, 1)
    mpz_init(other_bnd)

    cdef Integer _bnd
    import math
    _bnd = Integer(int((N//2).sqrt_approx()))
    mpz_init_set(bnd, _bnd.value)
    mpz_sub(other_bnd, N.value, bnd)

    cdef Py_ssize_t i, j
    cdef int do_it

    for i from 0 <= i < A._nrows:
        for j from 0 <= j < A._ncols:
            mpz_set(a, A._matrix[i][j])
            if mpz_cmp(denom, one) != 0:
                mpz_mul(a, a, denom)
            mpz_fdiv_r(a, a, N.value)
            do_it = 0
            if mpz_cmp(a, bnd) <= 0:
                do_it = 1
            elif mpz_cmp(a, other_bnd) >= 0:
                mpz_sub(a, a, N.value)
                do_it = 1
            if do_it:
                mpz_set(mpq_numref(R._matrix[i][j]), a)
                if mpz_cmp(denom, one) != 0:
                    mpz_set(mpq_denref(R._matrix[i][j]), denom)
                    mpq_canonicalize(R._matrix[i][j])
                else:
                    mpz_set_si(mpq_denref(R._matrix[i][j]), 1)
            else:
                # Otherwise have to do it the hard way
                mpq_rational_reconstruction(R._matrix[i][j], A._matrix[i][j], N.value)
                mpz_lcm(denom, denom, mpq_denref(R._matrix[i][j]))

    mpz_clear(denom)
    mpz_clear(a)
    mpz_clear(one)
    mpz_clear(other_bnd)
    mpz_clear(bnd)
    return R

## Old slow version
## def xxx_matrix_integer_sparse_rational_reconstruction(Matrix_integer_sparse A, Integer N):
##     cdef Matrix_rational_sparse R
##     R = Matrix_rational_sparse.__new__(Matrix_rational_sparse,
##                                       A.parent().change_ring(QQ), 0,0,0)

##     # todo -- use lcm of denoms so far trick...
##     #cdef mpz_t denom   # lcm of denoms so far

##     cdef mpq_t x
##     mpq_init(x)
##     cdef mpz_vector* A_row
##     cdef mpq_vector* R_row
##     for i from 0 <= i < A._nrows:
##         A_row = &A._matrix[i]
##         R_row = &R._matrix[i]
##         for j from 0 <= j < A_row.num_nonzero:
##             mpq_rational_reconstruction(x, A_row.entries[j], N.value)
##             mpq_vector_set_entry(R_row, A_row.positions[j], x)

##     mpq_clear(x)
##     return R

def matrix_integer_sparse_rational_reconstruction(Matrix_integer_sparse A, Integer N):
    cdef Matrix_rational_sparse R
    R = Matrix_rational_sparse.__new__(Matrix_rational_sparse,
                                      A.parent().change_ring(QQ), 0,0,0)

    cdef mpq_t t
    mpq_init(t)

    cdef mpz_t a, bnd, other_bnd, one, denom
    mpz_init_set_si(denom, 1)
    mpz_init(a)
    mpz_init_set_si(one, 1)
    mpz_init(other_bnd)

    cdef Integer _bnd
    import math
    _bnd = Integer(int((N//2).sqrt_approx()))
    mpz_init_set(bnd, _bnd.value)
    mpz_sub(other_bnd, N.value, bnd)

    cdef Py_ssize_t i, j
    cdef int do_it
    cdef mpz_vector* A_row
    cdef mpq_vector* R_row

    for i from 0 <= i < A._nrows:
        A_row = &A._matrix[i]
        R_row = &R._matrix[i]
        reallocate_mpq_vector(R_row, A_row.num_nonzero)
        R_row.num_nonzero = A_row.num_nonzero
        R_row.degree = A_row.degree
        for j from 0 <= j < A_row.num_nonzero:
            mpz_set(a, A_row.entries[j])
            if mpz_cmp(denom, one) != 0:
                mpz_mul(a, a, denom)
            mpz_fdiv_r(a, a, N.value)
            do_it = 0
            if mpz_cmp(a, bnd) <= 0:
                do_it = 1
            elif mpz_cmp(a, other_bnd) >= 0:
                mpz_sub(a, a, N.value)
                do_it = 1
            if do_it:
                mpz_set(mpq_numref(t), a)
                if mpz_cmp(denom, one) != 0:
                    mpz_set(mpq_denref(t), denom)
                    mpq_canonicalize(t)
                else:
                    mpz_set_si(mpq_denref(t), 1)
                mpq_set(R_row.entries[j], t)
                R_row.positions[j] = A_row.positions[j]
            else:
                # Otherwise have to do it the hard way
                mpq_rational_reconstruction(t, A_row.entries[j], N.value)
                mpq_set(R_row.entries[j], t)
                R_row.positions[j] = A_row.positions[j]
                mpz_lcm(denom, denom, mpq_denref(t))

    mpq_clear(t)

    mpz_clear(denom)
    mpz_clear(a)
    mpz_clear(one)
    mpz_clear(other_bnd)
    mpz_clear(bnd)
    return R


## def matrix_modn_sparse_lift(Matrix_modn_sparse A):
##     raise NotImplementedError
##     cdef Py_ssize_t i, j
##     cdef Matrix_integer_sparse L
##     L = Matrix_integer_sparse.__new__(Matrix_integer_sparse,
##                                      A.parent().change_ring(ZZ),
##                                      0, 0, 0)
##     cdef mpz_t* L_row
##     cdef mod_int* A_row
##     for i from 0 <= i < A._nrows:
##         L_row = L._matrix[i]
##         A_row = A._matrix[i]
##         for j from 0 <= j < A._ncols:
##             mpz_init_set_si(L_row[j], A_row[j])
##     L._initialized = 1
##     return L

## def matrix_integer_sparse_rational_reconstruction(Matrix_integer_sparse A, Integer N):
##     raise NotImplementedError
##     cdef Matrix_rational_sparse R
##     R = Matrix_rational_sparse.__new__(Matrix_rational_sparse,
##                                       A.parent().change_ring(QQ), 0,0,0)

##     cdef mpz_t denom   # lcm of denoms so far
##     for i from 0 <= i < A._nrows:
##         for j from 0 <= j < A._ncols:
##             mpq_rational_reconstruction(R._matrix[i][j], A._matrix[i][j], N.value)
##     return R




def matrix_rational_echelon_form_multimodular(Matrix self, height_guess=None, proof=None):
    """
    Returns reduced row-echelon form using a multi-modular
    algorithm.  Does not change self.

    REFERENCE: Chapter 7 of Stein's "Explicitly Computing Modular Forms".

    INPUT:
        height_guess -- integer or None
        proof -- boolean or None (default: None, see proof.linear_algebra or
                               sage.structure.proof).
                        Note that the global Sage default is proof=True

    ALGORITHM:
    The following is a modular algorithm for computing the echelon
    form.  Define the height of a matrix to be the max of the
    absolute values of the entries.

    Given Matrix A with n columns (self).

     0. Rescale input matrix A to have integer entries.  This does
        not change echelon form and makes reduction modulo lots of
        primes significantly easier if there were denominators.
        Henceforth we assume A has integer entries.

     1. Let c be a guess for the height of the echelon form.  E.g.,
        c=1000, e.g., if matrix is very sparse and application is to
        computing modular symbols.

     2. Let M = n * c * H(A) + 1,
        where n is the number of columns of A.

     3. List primes p_1, p_2, ..., such that the product of
        the p_i is at least M.

     4. Try to compute the rational reconstruction CRT echelon form
        of A mod the product of the p_i.  If rational
        reconstruction fails, compute 1 more echelon forms mod the
        next prime, and attempt again.  Make sure to keep the
        result of CRT on the primes from before, so we don't have
        to do that computation again.  Let E be this matrix.

     5. Compute the denominator d of E.
        Attempt to prove that result is correct by checking that

              H(d*E)*ncols(A)*H(A) < (prod of reduction primes)

        where H denotes the height.   If this fails, do step 4 with
        a few more primes.
    """

    if proof is None:
        from sage.structure.proof.proof import get_flag
        proof = get_flag(proof, "linear_algebra")

    verbose("Multimodular echelon algorithm on %s x %s matrix"%(self._nrows, self._ncols), caller_name="multimod echelon")
    cdef Matrix E
    if self._nrows == 0 or self._ncols == 0:
        self.cache('in_echelon_form', True)
        self.cache('echelon_form', self)
        self.cache('pivots', [])
        return self

    B, _ = self._clear_denom()

    height = self.height()
    if height_guess is None:
        height_guess = 10000000*(height+100)
    tm = verbose("height_guess = %s"%height_guess, level=2, caller_name="multimod echelon")

    if proof:
        M = self._ncols * height_guess * height  +  1
    else:
        M = height_guess + 1

    if self.is_sparse():
        p = matrix_modn_sparse.MAX_MODULUS + 1
    else:
        p = matrix_modn_dense.MAX_MODULUS + 1
    X = []
    best_pivots = []
    prod = 1
    problem = 0
    lifts = {}
    while True:
        p = previous_prime(p)
        while prod < M:
            problem = problem + 1
            if problem > 50:
                verbose("echelon multi-modular possibly not converging?", caller_name="multimod echelon")
            t = verbose("echelon modulo p=%s (%.2f%% done)"%(
                       p, 100*float(len(str(prod))) / len(str(M))), level=2, caller_name="multimod echelon")

            # We use denoms=False, since we made self integral by calling clear_denom above.
            A = B._mod_int(p)
            t = verbose("time to reduce matrix mod p:",t, level=2, caller_name="multimod echelon")
            A.echelonize()
            t = verbose("time to put reduced matrix in echelon form:",t, level=2, caller_name="multimod echelon")

            # a worthwhile check / shortcut.
            if self._nrows == self._ncols and len(A.pivots()) == self._nrows:
                verbose("done: the echelon form mod p is the identity matrix", caller_name="multimod echelon")
                E = self.parent().identity_matrix()
                E.cache('pivots', range(self._nrows))
                E.cache('in_echelon_form', True)
                self.cache('in_echelon_form', True)
                self.cache('echelon_form', E)
                self.cache('pivots', range(self._nrows))
                return E

            c = cmp_pivots(best_pivots, A.pivots())
            if c <= 0:
                best_pivots = A.pivots()
                X.append(A)
                prod = prod * p
            else:
                # do not save A since it is bad.
                verbose("Excluding this prime (bad pivots).", caller_name="multimod echelon")
            t = verbose("time for pivot compare", t, level=2, caller_name="multimod echelon")
            p = previous_prime(p)
        # Find set of best matrices.
        Y = []
        # recompute product, since may drop bad matrices
        prod = 1
        t = verbose("now comparing pivots and dropping any bad ones", level=2, t=t, caller_name="multimod echelon")
        for i in range(len(X)):
            if cmp_pivots(best_pivots, X[i].pivots()) <= 0:
                p = X[i].base_ring().order()
                if not lifts.has_key(p):
                    t0 = verbose("Lifting a good matrix", level=2, caller_name = "multimod echelon")
                    if X[i].is_dense():
                        lift = matrix_modn_dense_lift(X[i])
                    else:
                        lift = matrix_modn_sparse_lift(X[i])
                    lifts[p] = (lift, p)
                    verbose("Finished lift", level=2, caller_name= "multimod echelon", t=t0)
                Y.append(lifts[p])
                prod = prod * X[i].base_ring().order()
        verbose("finished comparing pivots", level=2, t=t, caller_name="multimod echelon")
        try:
            if len(Y) == 0:
                raise ValueError, "not enough primes"
            t = verbose("start crt linear combination", level=2, caller_name="multimod echelon")
            a = CRT_basis([w[1] for w in Y])
            t = verbose('got crt basis', level=2, t=t, caller_name="multimod echelon")

            # take the linear combination of the lifts of the elements
            # of Y times coefficients in a
            L = a[0]*(Y[0][0])
            assert Y[0][0].is_sparse() == L.is_sparse()
            for j in range(1,len(Y)):
                L += a[j]*(Y[j][0])
            verbose("time to take linear combination of matrices over ZZ is",t, level=2, caller_name="multimod echelon")
            t = verbose("now doing rational reconstruction", level=2, caller_name="multimod echelon")
            E = L.rational_reconstruction(prod)
            L = 0  # free memory
            verbose('rational reconstruction completed', t, level=2, caller_name="multimod echelon")
        except ValueError, msg:
            verbose(msg, level=2)
            verbose("Not enough primes to do CRT lift; redoing with several more primes.", level=2, caller_name="multimod echelon")
            M = prod * p*p*p
            continue

        if not proof:
            verbose("Not checking validity of result (since proof=False).", level=2, caller_name="multimod echelon")
            break
        d   = E.denominator()
        hdE = long(E.height())
        if True or hdE * self.ncols() * height < prod:
            break
        M = prod * p*p*p
    #end while
    verbose("total time",tm, level=2, caller_name="multimod echelon")
    self.cache('pivots', best_pivots)
    E.cache('pivots', best_pivots)
    return E


###########################

def cmp_pivots(x,y):
    """
    Compare two sequences of pivot columns.
    If x is short than y, return -1, i.e., x < y, "not as good".
    If x is longer than y, x > y, "better"
    If the length is the same then x is better, i.e., x > y
        if the entries of x are correspondingly >= those of y with
        one being greater.
    I
    """
    if len(x) < len(y):
        return -1
    if len(x) > len(y):
        return 1
    if x < y:
        return 1
    elif x == y:
        return 0
    else:
        return -1



#######################################

def matrix_rational_sparse__dense_matrix(Matrix_rational_sparse self):
    cdef Matrix_rational_dense B
    cdef mpq_vector* v

    B = self.matrix_space(sparse=False).zero_matrix()
    for i from 0 <= i < self._nrows:
        v = &(self._matrix[i])
        for j from 0 <= j < v.num_nonzero:
            mpq_set(B._matrix[i][v.positions[j]], v.entries[j])
    return B
