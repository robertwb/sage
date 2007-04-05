"""
Quaternion algebras

AUTHOR: David Kohel, 2005-09

TESTS:
    sage: A = QuaternionAlgebra(QQ, -1,-1, names=list('ijk'))
    sage: A == loads(dumps(A))
    True
    sage: i, j, k = A.gens()
    sage: i == loads(dumps(i))
    True

"""

#*****************************************************************************
#  Copyright (C) 2005 David Kohel <kohel@maths.usyd.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty
#    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License for more details; the full text
#  is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.misc import mul
from sage.rings.arith import kronecker, GCD, hilbert_symbol
from sage.rings.integer import Integer
from sage.rings.all import (IntegerRing, RationalField, PolynomialRing, is_Field)
from sage.modules.free_module import FreeModule
from sage.modules.free_module import VectorSpace
from sage.matrix.matrix_space import MatrixSpace
from sage.algebras.free_algebra import FreeAlgebra
from sage.algebras.free_algebra_quotient import FreeAlgebraQuotient
from sage.algebras.algebra_element import AlgebraElement
from sage.algebras.free_algebra_quotient_element import FreeAlgebraQuotientElement
from sage.algebras.quaternion_algebra_element import QuaternionAlgebraElement

import weakref

def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

def fundamental_discriminant(D):
    D = Integer(D)
    D = D.square_free_part()
    if D%4 in (0,1):
        return D
    return 4*D

def ramified_primes(a,b):
    a = Integer(a); b = Integer(b)
    if a.is_square() or b.is_square() or (a+b).is_square():
        return [ ]
    a = a.square_free_part()
    b = b.square_free_part()
    c = Integer(GCD(a,b))
    if c != 1:
        p = c.factor()[0][0]
        ram_prms = ramified_primes(p,-(b//p))
        for p in ramified_primes(a//p,b):
            if p in ram_prms:
                ram_prms.remove(p)
            else:
                ram_prms.append(p)
        ram_prms.sort()
        return ram_prms
    ram_prms = [ ]
    S1 = [ p[0] for p in abs(a).factor() ]
    for p in S1:
        if p == 2 and b%4 == 3:
            if kronecker(a+b,p) == -1:
                ram_prms.append(p)
        elif kronecker(b,p) == -1:
            ram_prms.append(p)
    S2 = [ p[0] for p in abs(b).factor() ]
    for q in S2:
        if q == 2 and a%4 == 3:
            if kronecker(a+b,q) == -1:
                ram_prms.append(q)
        elif kronecker(a,q) == -1:
            ram_prms.append(q)
    if not 2 in ram_prms and a%4 == 3 and b%4 == 3:
        ram_prms.append(2)
    ram_prms.sort()
    return ram_prms

def ramified_primes_from_discs(D1,D2,T):
    M = Integer(GCD([D1,D2,T]))
    D3 = (T**2 - D1*D2)//4
    facs = D3.factor()
    D1 = fundamental_discriminant(D1)
    D2 = fundamental_discriminant(D2)
    D3 = fundamental_discriminant(D3)
    ram_prms = []
    for pow in facs:
        p = pow[0]
        if pow[1]%2 == 1:
            chi = (kronecker(D,p) for D in (D1,D2,D3))
            if -1 in chi:
                ram_prms.append(p)
            elif not 1 in chi and hilbert_symbol(D1,D3,p) == -1:
                ram_prms.append(p)
        elif D1%p == 0 and D2%p == 0:
            chi = (kronecker(D,p) for D in (D1,D2,D3))
            if hilbert_symbol(D1,D3,p) == -1:
                ram_prms.append(p)
    return ram_prms

_cache = {}

def QuaternionAlgebra(K, a, b, names, denom=1):
    """
    Return the quaternion algebra over $K$ generated by $i$, $j$, and $k$
    such that $i^2 = a$, $j^2 = b$, and $ij=-ji=k$.

    INPUT:
        K -- field
        a -- element of K
        b -- element of K
        names -- list of three strings
        denom -- (optional, default 1)

    EXAMPLES:
        sage: A.<i,j,k> = QuaternionAlgebra(QQ, -1,-1)
        sage: i^2
        -1
        sage: j^2
        -1
        sage: i*j
        k
        sage: j*i
        -k
        sage: (i + j + k)^2
        -3
        sage: A.ramified_primes()
        [2]
    """
    if not is_Field(K):
        raise ValueError, "Base ring K (= %s) must be a field."%K

    if a == 0 or b == 0:
        raise ValueError, "Arguments a = %s and b = %s must be nonzero."%(a,b)

    if denom == 0:
        raise ValueError, "Argument denom (= %s) must be a nonzero."%denom

    if isinstance(names, list):
	names = tuple(names)

    key = (K, a, b, names, denom)
    global _cache
    if _cache.has_key(key):
	A = _cache[key]()
        if not A is None:
            return A

    if K is RationalField():
        prms = ramified_primes(a,b)
        H = QuaternionAlgebra_generic(K, prms)
    else:
        H = QuaternionAlgebra_generic(K)
    A = FreeAlgebra(K,3, names=names)
    F = A.monoid()
    mons = [ F(1) ] + [ F.gen(i) for i in range(3) ]
    M = MatrixSpace(K,4)
    m = denom
    c = a/m
    d = b/m
    mats = [
        M([0,1,0,0, a,0,0,0, 0,0,0,-m, 0,0,-c,0]),
        M([0,0,1,0, 0,0,0,m, b,0,0,0, 0,d,0,0]),
        M([0,0,0,1, 0,0,c,0, 0,-d,0,0, -c*d,0,0,0]) ]
    FreeAlgebraQuotient.__init__(H, A, mons=mons, mats=mats, names=names)
    _cache[key] = weakref.ref(H)
    return H

def QuaternionAlgebraWithInnerProduct(K, norms, traces, names):
    """
    """
    (n1,n2,n3) = norms
    (t1,t2,t3,t12,t13,t23) = traces
    T = t1*t23 + t2*t13 - t3*t12
    N = (t1*t2 - t12)*t13*t23 \
        + t23*(t23 - t2*t3)*n1 \
        + t13*(t13 - t1*t3)*n2 \
        + t12*(t12 - t1*t2)*n3 \
        + t1**2*n2*n3 + t2**2*n1*n3 + t3**2*n1*n2 - 4*n1*n2*n3
    if True and K(2).is_unit():
        D = T**2 - 4*N
        try:
            S = D.square_root()
        except ArithmeticError:
            raise ValueError, "Invalid inner product input."
        assert bool
        x = (T + S)/2
    else:
        # In characteristic 2 we can't diagonalize the quadratic
        # form so we solve for its roots.
        X = PolynomialRing(K).gen()
        try:
            x = (X**2 - T*X + N).roots()[0][0]
        except IndexError:
            raise ValueError, "Invalid inner product input."
    assert (x**2 - T*x + N) == 0
    M = MatrixSpace(K,5)
    m = M([ [    2,  t1,  t2, t3, t1*t2-t12 ],
            [   t1, 2*n1,  t12, t13, t2*n1  ],
            [   t2,  t12, 2*n2, t23, t1*n2  ],
            [   t3,  t13,  t23, 2*n3,  x ],
            [ t1*t2-t12, t2*n1, t1*n2, x, 2*n1*n2] ])
    v = m.kernel().gen(0)
    r4 = -1/v[4]
    V = VectorSpace(K,4)
    vij = V([ r4*v[i] for i in range(4) ])
    (s0,s1,s2,s3) = vij.list()
    r3 = 1/s3
    vik = r3 * (V([ s1*n1, -(s0+s1*t1), -n1, 0 ]) + (t1-s2)*vij)
    vkj = r3 * (V([ s2*n2, -n2, -(s0+s2*t2), 0 ]) + (t2-s1)*vij)
    vji = V([ -t12, t2, t1, 0 ]) - vij
    vki = V([ -t13, t3, 0, t1 ]) - vik
    vjk = V([ -t23, 0, t3, t2 ]) - vkj
    H = QuaternionAlgebra_generic(K)
    A = FreeAlgebra(K,3, names=names)
    F = A.monoid()
    mons = [ F(1) ] + [ F.gen(i) for i in range(3) ]
    M = MatrixSpace(K,4)
    mi = M([ [0,1,0,0], [-n1,t1,0,0], vji.list(), vki.list() ])
    mj = M([ [0,0,1,0], vij.list(), [-n2,0,t2,0], vkj.list() ])
    mk = M([ [0,0,0,1], vik.list(), vjk.list(), [-n3,0,0,t3] ])
    mats = [mi,mj,mk]
    FreeAlgebraQuotient.__init__(H, A, mons=mons, mats=mats, names=names)
    return H

def QuaternionAlgebraWithGramMatrix(K, gram, names):
    """
    """
    if not isinstance(gram,Matrix) or not gram.is_symmetric:
        raise AttributeError, "Argument gram (= %s) must be a symmetric matrix"%gram
    (q0,t01,t02,t03,_,q1,t12,t13,_,_,q3,t23,_,_,_,q4) = gram.list()
    n1 = q1/2
    n2 = q2/2
    n3 = q3/2
    return QuaternionAlgebraWithInnerProduct(K,norms,traces,names=names)

def QuaternionAlgebraWithDiscriminants(D1, D2, T, names, M=2):
    r"""
    Return the quaternion algebra over the rationals generated by $i$,
    $j$, and $k = (ij - ji)/M$ where $\Z[i]$, $\Z[j]$, and $\Z[k]$ are
    quadratic suborders of discriminants $D_1$, $D_2$, and $D_3 = (D_1
    D_2 - T^2)/M^2$, respectively.  The traces of $i$ and $j$ are
    chosen in $\{0,1\}$.

    The integers $D_1$, $D_2$ and $T$ must all be even or all odd, and
    $D_1$, $D_2$ and $D_3$ must each be the discriminant of some
    quadratic order, i.e. nonsquare integers = 0, 1 (mod 4).

    INPUT:
        D1 -- Integer
        D2 -- Integer
        T  -- Integer
        M -- Integer (default: 2)

    OUTPUT:
        A quaternion algebra.

    EXAMPLES:
        sage: A = QuaternionAlgebraWithDiscriminants(-7,-47,1, names=['i','j','k'])
        sage: print A
        Quaternion algebra with generators (i, j, k) over Rational Field
        sage: i, j, k = A.gens()
        sage: i**2
        -2 + i
        sage: j**2
        -12 + j
        sage: k**2
        -24 + k
        sage: i.minimal_polynomial('x')
        x^2 - x + 2
        sage: j.minimal_polynomial('x')
        x^2 - x + 12
    """
    QQ = RationalField()
    ZZ = IntegerRing()
    if M != 2:
        raise ValueError, "Not implemented: Argument denom (= %s) must be 2."%M
    # adapt types of input arguments
    D1 = ZZ(D1); D2 = ZZ(D2); T = ZZ(T)
    if (D1*D2)%M**2-(T**2)%M**2 != 0:
        raise ArithmeticError, \
              "Each of (D1 D2 - T^2) = %s must be 0 mod M^2 = %s"%(D3,M**2)
    # Check that the D_i are 0 or 1 mod 4 and non-square:
    if D1.is_square() or D2.is_square():
        raise ArithmeticError, "D1 (=%s) and D2 (=%s) must be nonsquare."%(D1,D2)
    t1 = D1%4; t2 = D2%4
    if t1 in [2,3] or t2 in [2,3]:
        raise ArithmeticError, "D1 (=%s) and D2 (=%s) must be in {0,1} mod 4."%(D1,D2)
    n1 = (t1-D1)//4; n2 = (t2-D2)//4
    t12 = (t1*t2 - T)//2
    A = FreeAlgebra(RationalField(),3,names=names)
    i, j, k = A.monoid().gens()
    # Right matrix action on algebra:
    MQ = MatrixSpace(QQ,4)
    mi = MQ([0,1,0,0, -n1,t1,0,0, -t12,t2,t1,-1, -n1*t2,t1*t2-t12,n1,0])
    mj = MQ([0,0,1,0, 0,0,0,1, -n2,0,t2,0, 0,-n2,0,t2])
    # N.B. mk = mi*mj
    mk = MQ([0,0,0,1, 0,0,-n1,t1,  -n2*t1,n2,t1*t2-t12,0, -n1*n2,0,0,t1*t2-t12])
    mats = [ mi, mj, mk ]
    prms = ramified_primes_from_discs(D1,D2,T)
    H = QuaternionAlgebra_generic(QQ, prms)
    A = FreeAlgebra(QQ,3, names=names)
    F = A.monoid()
    mons = [ F(1) ] + [ F.gen(i) for i in range(3) ]
    FreeAlgebraQuotient.__init__(H, A, mons=mons, mats=mats, names=names)
    return H

class QuaternionAlgebra_generic(FreeAlgebraQuotient):

    def __init__(self, K, ramified_primes=None):
        """
        """
        self.__vector_space = VectorSpace(K,4)
        if ramified_primes != None:
            self.__ramified_primes = ramified_primes

    def __call__(self, x):
        if isinstance(x, QuaternionAlgebraElement) and x.parent() is self:
            return x
        return QuaternionAlgebraElement(self,x)

    def __repr__(self):
        return "Quaternion algebra with generators %s over %s"%(
            self.gens(), self.base_ring())

    def gen(self,i):
        """
        The i-th generator of the quaternion algebra.
        """
        if i < 0 or not i < 4:
            raise IndexError, \
                "Argument i (= %s) must be between 0 and %s."%(i, 3)
        K = self.base_ring()
        F = self.free_algebra().monoid()
        return QuaternionAlgebraElement(self,{F.gen(i):K(1)})

    def basis(self):
        return (self(1), self([0,1,0,0]), self([0,0,1,0]), self([0,0,0,1]))

    def discriminant(self):
        return self.gram_matrix().determinant()

    def gram_matrix(self):
        V = self.__vector_space
        if not V._FreeModule_generic__inner_product_is_dot_product:
            return V.inner_product_matrix()
        K = self.base_ring()
        M = MatrixSpace(K,4)(0)
        B = self.basis()
        for i in range(4):
            x = B[i]
            M[i,i] = 2*(x.reduced_norm())
            for j in range(i+1,4):
                y = B[j]
                c = (x * y.conjugate()).reduced_trace()
                M[i,j] = c
                M[j,i] = c
        # TODO: Make it so one can correctly set these things.
        V._FreeModule_generic__inner_product_is_dot_product = False
        V._FreeModule_generic__inner_product_matrix = M
        return M

    def inner_product_matrix(self):
        return self.gram_matrix()

    def is_commutative(self):
        """
        EXAMPLES:
            sage: Q.<i,j,k> = QuaternionAlgebra(QQ, -3,-7)
            sage: Q.is_commutative()
            False
        """
        return False

    def _set_ramified_primes(self, prms):
        self.__ramified_primes = prms

    def ramified_primes(self):
        try:
            return self.__ramified_primes
        except:
            raise AttributeError, "Ramified primes have not been computed."

    def random_element(self):
        K = self.base_ring()
        return self([ K.random_element() for _ in range(4) ])

    def vector_space(self):
        V = self.__vector_space
        try:
            _ = V._FreeModule_generic__inner_product_matrix
        except:
            V._FreeModule_generic__inner_product_matrix = self.gram_matrix()
        return self.__vector_space
