"""
Heilbronn matrix computation
"""

#*****************************************************************************
#       Copyright (C) 2004 William Stein <wstein@gmail.com>
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

import sage.rings.arith

import sage.misc.misc

include '../../ext/cdefs.pxi'
include '../../ext/interrupt.pxi'
include '../../ext/stdsage.pxi'

cimport p1list
import  p1list
cdef p1list.export export
export = p1list.export()

ctypedef long long llong

cdef extern from "solaris_fix.h": pass

cdef int llong_prod_mod(int a, int b, int N):
    cdef int c
    c = <int> ( ((<llong> a) * (<llong> b)) % (<llong> N) )
    if c < 0:
        c = c + N
    return c

def HeilbronnCremonaList(int p):
    """
    The Heilbronn matrices of determinant p, as defined by Cremona.
    """
    cdef int r, x1, x2, y1, y2, a, b, c, x3, y3, q
    cdef object ans

    if p == 2:
        return [[1,0,0,2], [2,0,0,1], [2,1,0,1], [1,0,1,2]]

    #if cremona.has_key(p):
    #    return cremona[p]
    assert sage.rings.arith.is_prime(p), "Input must be a pseudoprime."

    ans = [[1,0,0,p]]
    # WARNING: In C (which is what we're writing in below!), -p/2 means
    # "round toward 0", but in Python it means "round down" (right now),
    # and in Python 3.0 it'll mean "make a float".
    _sig_on
    for r from -p/2 <= r < p/2+1:
        x1=p; x2=-r; y1=0; y2=1; a=-p; b=r; c=0; x3=0; y3=0; q=0
        ans.append([x1,x2,y1,y2])
        while b:
            q = <int>roundf(<float>a / <float> b)
            c = a - b*q
            a = -b
            b = c
            x3 = q*x2 - x1
            x1 = x2; x2 = x3; y3 = q*y2 - y1; y1 = y2; y2 = y3
            ans.append([x1,x2, y1,y2])
    _sig_off
    return ans

def HeilbronnMerelList(int n):
    """
    Set of Heilbronn matrices of determinant n, as defined by Merel.
    """
    cdef int a, q, d, b, c, bc
    cdef object H

    H = []
    _sig_on
    for a from 1 <= a <= n:
        ## We have ad-bc=n so c=0 and ad=n, or b=(ad-n)/c
        ## Must have ad - n >= 0, so d must be >= Ceiling(n/a).
        q = n/a
        if q*a == n:
          d = q
          for b from 0 <= b < a:
              H.append([a,b,0,d])
          for c from 1 <= c < d:
              H.append([a,0,c,d])
        for d from q+1 <= d <= n:
            bc = a*d-n
            ## Divisor c of bc must satisfy Floor(bc/c) lt a and c lt d.
            ## c ge (bc div a + 1)  <=>  Floor(bc/c) lt a  (for integers)
            ## c le d - 1           <=>  c lt d
            for c from bc/a + 1 <= c < d:
                if bc % c == 0:
                    H.append([a,bc/c,c,d])
    _sig_off
    return H

cdef struct list:
    int *v
    int i   # how many positions of list are filled
    int n   # how much memory has been allocated

cdef int* expand(int *v, int n, int new_length) except NULL:
    cdef int *w, i
    w = <int*>  sage_malloc(new_length*sizeof(int))
    if w == <int*> 0:
        return NULL
    if v:
        for i from 0 <= i < n:
            w[i] = v[i]
        sage_free(v)
    return w

cdef int list_append(list* L, int a) except -1:
    cdef int j
    if L.i >= L.n:
        j = 10 + 2*L.n
        L.v = expand(L.v, L.n, j)
        L.n = j
    L.v[L.i] = a
    L.i = L.i + 1

cdef int list_append4(list* L, int a, int b, int c, int d) except -1:
    list_append(L, a)
    list_append(L, b)
    list_append(L, c)
    list_append(L, d)

cdef void list_clear(list L):
    sage_free(L.v)

cdef void list_init(list* L):
    L.n = 16
    L.i = 0
    L.v = expand(<int*>0, 0, L.n)


cdef class Heilbronn:
    cdef int length
    cdef list list

    def __dealloc__(self):
        list_clear(self.list)

    def _initialize_list(self):
        raise NotImplementedError

    def __getitem__(self, int n):
        if n < 0 or n >= self.length:
            raise IndexError
        return [self.list.v[4*n], self.list.v[4*n+1], \
                self.list.v[4*n+2], self.list.v[4*n+3]]

    def __len__(self):
        return self.length

    def to_list(self):
        """
        EXAMPLES:
            sage: H = sage.modular.modsym.heilbronn.HeilbronnCremona(2); H
            The Cremona-Heilbronn matrices of determinant 2
            sage: H.to_list()
            [[1, 0, 0, 2], [2, 0, 0, 1], [2, 1, 0, 1], [1, 0, 1, 2]]
        """
        cdef int i
        L = []
        for i from 0 <= i < self.length:
            L.append([self.list.v[4*i], self.list.v[4*i+1], \
                      self.list.v[4*i+2], self.list.v[4*i+3]])
        return L

    cdef apply_only(self, int u, int v, int N, int* a, int* b):
        """
        INPUT:
            u, v, N -- integers
            a, b -- preallocated int arrays of the length self.
        OUTPUT:
            list

        Return a list of pairs ((c,d),m), which is obtained as follows:
          1) Compute the images (a,b) of the vector (u,v) (mod N) acted on by
             each of the HeilbronnCremona matrices in self.
          2) Reduce each (a,b) to canonical form (c,d) using p1normalize
          3) Sort.
          4) Create the list ((c,d),m), where m is the number of times
             that (c,d) appears in the list created in steps 1--3 above.
        Note that the pairs ((c,d),m) are sorted lexicographically by (c,d).

        EXAMPLES:
            sage: H = sage.modular.modsym.heilbronn.HeilbronnCremona(2); H
            The Cremona-Heilbronn matrices of determinant 2
            sage: H.apply(1,2,7)
            [((1, 5), 1), ((1, 6), 1), ((1, 1), 1), ((1, 4), 1)]
        """
        cdef int i
        _sig_on
        if N < 32768:   # use ints with no reduction modulo N
            for i from 0 <= i < self.length:
                a[i] = u*self.list.v[4*i] + v*self.list.v[4*i+2]
                b[i] = u*self.list.v[4*i+1] + v*self.list.v[4*i+3]
        elif N < 46340:    # use ints but reduce mod N so can add two
            for i from 0 <= i < self.length:
                a[i] = (u * self.list.v[4*i])%N + (v * self.list.v[4*i+2])%N
                b[i] = (u * self.list.v[4*i+1])%N + (v * self.list.v[4*i+3])%N
        else:
            for i from 0 <= i < self.length:
                a[i] = llong_prod_mod(u,self.list.v[4*i],N) + llong_prod_mod(v,self.list.v[4*i+2], N)
                b[i] = llong_prod_mod(u,self.list.v[4*i+1],N) + llong_prod_mod(v,self.list.v[4*i+3], N)
        _sig_off

    def apply(self, int u, int v, int N):
        """
        INPUT:
            u, v, N -- integers
        OUTPUT:
            list

        Return a list of pairs ((c,d),m), which is obtained as follows:
          1) Compute the images (a,b) of the vector (u,v) (mod N) acted on by
             each of the HeilbronnCremona matrices in self.
          2) Reduce each (a,b) to canonical form (c,d) using p1normalize
          3) Sort.
          4) Create the list ((c,d),m), where m is the number of times
             that (c,d) appears in the list created in steps 1--3 above.
        Note that the pairs ((c,d),m) are sorted lexicographically by (c,d).

        EXAMPLES:
            sage: H = sage.modular.modsym.heilbronn.HeilbronnCremona(2); H
            The Cremona-Heilbronn matrices of determinant 2
            sage: H.apply(1,2,7)
            [((1, 5), 1), ((1, 6), 1), ((1, 1), 1), ((1, 4), 1)]
        """
        cdef int i, a, b, c, d, s
        cdef object X
        M = {}
        t = sage.misc.misc.verbose("start making list M.",level=5)
        _sig_on
        if N < 32768:   # use ints with no reduction modulo N
            for i from 0 <= i < self.length:
                a = u*self.list.v[4*i] + v*self.list.v[4*i+2]
                b = u*self.list.v[4*i+1] + v*self.list.v[4*i+3]
                export.c_p1_normalize_int(N, a, b, &c, &d, &s, 0)
                X = (c,d)
                if M.has_key(X):
                    M[X] = M[X] + 1
                else:
                    M[X] = 1
        elif N < 46340:    # use ints but reduce mod N so can add two
            for i from 0 <= i < self.length:
                a = (u * self.list.v[4*i])%N + (v * self.list.v[4*i+2])%N
                b = (u * self.list.v[4*i+1])%N + (v * self.list.v[4*i+3])%N
                export.c_p1_normalize_int(N, a, b, &c, &d, &s, 0)
                X = (c,d)
                if M.has_key(X):
                    M[X] = M[X] + 1
                else:
                    M[X] = 1
        else:
            for i from 0 <= i < self.length:
                a = llong_prod_mod(u,self.list.v[4*i],N) + llong_prod_mod(v,self.list.v[4*i+2], N)
                b = llong_prod_mod(u,self.list.v[4*i+1],N) + llong_prod_mod(v,self.list.v[4*i+3], N)
                export.c_p1_normalize_llong(N, a, b, &c, &d, &s, 0)
                X = (c,d)
                if M.has_key(X):
                    M[X] = M[X] + 1
                else:
                    M[X] = 1
        t = sage.misc.misc.verbose("finished making list M.",t, level=5)
        mul = []
        for x,y in M.items():
            mul.append((x,y))
        t = sage.misc.misc.verbose("finished making mul list.",t, level=5)
        _sig_off
        return mul

cdef class HeilbronnCremona(Heilbronn):
    cdef public int p

    def __init__(self, int p):
        if p <= 1 or not sage.rings.arith.is_prime(p):
            raise ValueError, "p must be >= 2 and prime"
        self.p = p
        self._initialize_list()

    def __repr__(self):
        return "The Cremona-Heilbronn matrices of determinant %s"%self.p

    def _initialize_list(self):
        cdef int r, x1, x2, y1, y2, a, b, c, x3, y3, q, n, p
        cdef list *L
        list_init(&self.list)
        L = &self.list
        p = self.p

        list_append4(L, 1,0,0,p)

        # When p==2, then Heilbronn matrices are
        #    [[1,0,0,2], [2,0,0,1], [2,1,0,1], [1,0,1,2]]
        # which are not given by the algorithm below.
        if p == 2:
            list_append4(L, 2,0,0,1)
            list_append4(L, 2,1,0,1)
            list_append4(L, 1,0,1,2)
            self.length = 4
            return

        # NOTE: In C, -p/2 means "round toward 0", but in Python it
        # means "round down."
        _sig_on
        for r from -p/2 <= r < p/2+1:
            x1=p; x2=-r; y1=0; y2=1; a=-p; b=r; c=0; x3=0; y3=0; q=0
            list_append4(L, x1,x2,y1,y2)
            while b:
                q = <int>roundf(<float>a / <float> b)
                c = a - b*q
                a = -b
                b = c
                x3 = q*x2 - x1
                x1 = x2; x2 = x3; y3 = q*y2 - y1; y1 = y2; y2 = y3
                list_append4(L, x1,x2, y1,y2)
        self.length = L.i/4
        _sig_off

    def __getitem__(self, int n):
        if n < 0 or n >= self.length:
            raise IndexError
        return [self.list.v[4*n], self.list.v[4*n+1], \
                self.list.v[4*n+2], self.list.v[4*n+3]]



cdef class HeilbronnMerel(Heilbronn):
    cdef public int n

    def __init__(self, int n):
        if n <= 0:
            raise ValueError, "n (=%s) must be >= 1"%n
        self.n = n
        self._initialize_list()

    def __repr__(self):
        return "The Merel-Heilbronn matrices of determinant %s"%self.n

    def _initialize_list(self):
        cdef int a, q, d, b, c, bc, n
        cdef list *L
        list_init(&self.list)
        L = &self.list
        n = self.n

        _sig_on
        for a from 1 <= a <= n:
            ## We have ad-bc=n so c=0 and ad=n, or b=(ad-n)/c
            ## Must have ad - n >= 0, so d must be >= Ceiling(n/a).
            q = n/a
            if q*a == n:
                d = q
                for b from 0 <= b < a:
                    list_append4(L, a,b,0,d)
                for c from 1 <= c < d:
                    list_append4(L, a,0,c,d)
            for d from q+1 <= d <= n:
                bc = a*d-n
                ## Divisor c of bc must satisfy Floor(bc/c) lt a and c lt d.
                ## c ge (bc div a + 1)  <=>  Floor(bc/c) lt a  (for integers)
                ## c le d - 1           <=>  c lt d
                for c from bc/a + 1 <= c < d:
                    if bc % c == 0:
                        list_append4(L,a,bc/c,c,d)
        self.length = L.i/4
        _sig_off


############################################################################
# Fast application of Heilbronn operators to computation of
# systems of Hecke eigenvalues.
############################################################################

from sage.matrix.matrix_rational_dense cimport Matrix_rational_dense

def hecke_images_gamma0_weight2(int u, int v, int N, indices, R):
    """
    INPUT:
        u, v, N -- integers so that gcd(u,v,N) = 1
        indices -- a list of positive integers
        R       -- matrix over QQ that writes each elements of P1 =
                   P1List(N) in terms of a subset of P1.

    OUTPUT:
        a dense matrix with rational entries whose columns are
        the images T_n(x) for n in indices and x the Manin
        symbol (u,v), expressed in terms of the basis.
    """
    cdef p1list.P1List P1 = p1list.P1List(N)

    # Create a zero sparse matrix over QQ with len(indices) rows
    # and #P^1(N) columns.
    cdef Matrix_rational_dense T
    from sage.matrix.all import matrix
    from sage.rings.all import QQ
    T = matrix(QQ, len(indices), len(P1), sparse=False)

    cdef Py_ssize_t i, j
    cdef int *a, *b, k

    cdef Heilbronn H

    t = sage.misc.misc.verbose("computing non-reduced images of symbol under Hecke operators",
                               level=1, caller_name='hecke_images_gamma0_weight2')
    for i, n in enumerate(indices):
        # List the Heilbronn matrices of determinant n defined by Cremona
        if sage.rings.arith.is_prime(n):
            H = HeilbronnCremona(n)
        else:
            H = HeilbronnMerel(n)

        # Allocate memory to hold images of (u,v) under all Heilbronn matrices
        a = <int*> sage_malloc(sizeof(int)*H.length)
        if not a: raise MemoryError
        b = <int*> sage_malloc(sizeof(int)*H.length)
        if not b: raise MemoryError

        # Compute images of (u,v) under all Heilbronn matrices
        H.apply_only(u, v, N, a, b)

        # Compute the indexes of these images.
        # We just store them in the array a for simplicity.
        for j from 0 <= j < H.length:
            # Compute index of the symbol a[j], b[j] in the standard list.
            k = P1.index(a[j], b[j])

            # Now fill in row i of the sparse matrix T.
            if k != -1:
                 # The following line is just a dangerous direct way to do: T[i,k] += 1
                 T._add_ui_unsafe_assuming_int(i,k,1)
                 # The following is slightly faster, but is way scary.
                 #mpz_add_ui(mpq_numref(T._matrix[i][a[j]]), mpq_numref(T._matrix[i][a[j]]), 1)

        # Free a and b
        sage_free(a)
        sage_free(b)

    t = sage.misc.misc.verbose("finished computing non-reduced images",
                               t, level=1, caller_name='hecke_images_gamma0_weight2')

    t = sage.misc.misc.verbose("Now reducing images of symbol",
                               level=1, caller_name='hecke_images_gamma0_weight2')

    # Return the product T * R, whose rows are the image of (u,v) under
    # the Hecke operators T_n for n in indices.
    if max(indices) <= 30:   # In this case T tends to be very sparse
        ans = T.sparse_matrix()._matrix_times_matrix_dense(R)
        sage.misc.misc.verbose("did reduction using sparse multiplication",
                               t, level=1, caller_name='hecke_images_gamma0_weight2')
    elif R.is_sparse():
        ans = T * R.dense_matrix()
        sage.misc.misc.verbose("did reduction using dense multiplication",
                               t, level=1, caller_name='hecke_images_gamma0_weight2')
    else:
        ans = T * R
        sage.misc.misc.verbose("did reduction using dense multiplication",
                               t, level=1, caller_name='hecke_images_gamma0_weight2')

    return ans
