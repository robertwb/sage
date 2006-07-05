r"""
Congruence subgroups of $\SL_2(\Z)$

AUTHOR:
    -- William Stein

TODO:
    -- added "gens" functions for each subgroup (since this is such a
       frequently requested features).
"""

################################################################################
#
#       Copyright (C) 2004, 2006 William Stein <wstein@ucsd.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#
################################################################################

import random

import sage.rings.arith as arith

from sage.groups.group import Group

from sage.rings.integer_ring import IntegerRing

from sage.rings.infinity import infinity

from congroup_element import CongruenceSubgroupElement

import sage.modular.modsym.p1list

class CongruenceSubgroup(Group):
    def __init__(self, level):
        level=int(level)
        if level <= 0:
            raise ArithmeticError, "Congruence groups only defined for positive levels."
        self.__level = level

    def _repr_(self):
        return "Generic congruence subgroup"

    def __hash__(self):
        return hash(str(self))

    def are_equivalent(self, x, y):
        raise NotImplementedError

    def coset_reps(self):
        raise NotImplementedError

    def generators(self):
        raise NotImplementedError

    def level(self):
        return self.__level

    def __cmp__(self, right):
        raise NotImplementedError

    def is_abelian(self):
        return False

    def is_finite(self):
        return False

    def is_subgroup(self, right):
        raise NotImplementedError

    def order(self):
        return infinity

    def __call__(self, x, check=True):
        if isinstance(x, CongruenceSubgroupElement) and x.parent() == self:
            return x
        raise NotImplementedError


# Just for now until we make an SL_2 group type.
from sage.matrix.matrix_space import MatrixSpace
Mat2Z = MatrixSpace(IntegerRing(),2)

def lift_to_sl2z(c, d, N):
    """
    If this Manin symbol is (c,d) viewed modulo N, this function
    computes and returns a list [a,b, c',d'] that defines a 2x2
    matrix with determinant 1 and integer entries, such that
    c=c'(mod N) and d=d'(mod N).
    """
    if N == 1:
        return [1,0,0,1]
    g, z1, z2 = arith.XGCD(c,d)

    # We're lucky: z1*c + z2*d = 1.
    if g==1:
        return [z2, -z1, c, d]

    # Have to try harder.
    if c == 0:
        c += N;
    if d == 0:
        d += N;
    m = c;

    # compute prime-to-d part of m.
    while True:
        g = arith.GCD(m,d)
        if g == 1:
            break
        m //= g

    # compute prime-to-N part of m.
    while True:
        g = arith.GCD(m,N);
        if g == 1:
            break
        m //= g
    d += N*m
    g, z1, z2 = arith.XGCD(c,d)

    assert g==1

    return Mat2Z([z2, -z1, c, d])


class Gamma0(CongruenceSubgroup):
    r"""
    The congruence subgroup $\Gamma_0(N)$.

    EXAMPLES:
        sage: G = Gamma0(11); G
        Congruence Subgroup Gamma0(11)
        sage: loads(G.dumps()) == G
        True
    """
    def __init__(self, level):
        CongruenceSubgroup.__init__(self, level)

    def _repr_(self):
        return "Congruence Subgroup Gamma0(%s)"%self.level()

    def _latex_(self):
        return "\\Gamma_0(%s)"%self.level()

    def __cmp__(self, right):
        if not isinstance(right, Gamma0):
            return -1
        if self.level() < right.level():
            return -1
        elif self.level() > right.level():
            return 1
        return 0

    def is_subgroup(self, right):
        """
        Return True if self is a subgroup of right.
        """
        if right.level() == 1:
            return True
        if isinstance(right, Gamma0):
            return self.level() % right.level() == 0
        if isinstance(right, Gamma1):
            if right.level() >= 3:
                return False
            elif right.level() == 2:
                return self.level() == 2
            # case level 1 dealt with above
        raise NotImplementedError

    def coset_reps(self):
        r"""
        Return representatives for the right cosets of this
        congruence subgroup in $\SL_2(\Z)$ as a generator.

        Use \code{list(self.coset_reps())} to obtain coset reps as a
        list.
        """
        N = self.level()
        for z in sage.modular.modsym.p1list.P1List(N):
            yield lift_to_sl2z(z[0], z[1], N)

    def generators(self):
        r"""
        Return generators for this congruence subgroup.  These are
        computed using coset representatives, a naive algorithm
        (Todd-Coxeter?), and generators for $\SL_2(\Z)$.

        ALGORITHM: Given coset representatives for a finite index
        subgroup~$G$ of $\SL_2(\Z)$ we compute generators for~$G$ as
        follows.  Let $R$ be a set of coset representatives for $G$.
        Let $S, T \in \SL_2(\Z)$ be defined by \code{0,-1,1,0]} and
        \code{1,1,0,1}, respectively.  Define maps $s, t: R \to G$ as
        follows. If $r \in R$, then there exists a unique $r' \in R$
        such that $GrS = Gr'$. Let $s(r) = rSr'^{-1}$. Likewise, there
        is a unique $r'$ such that $GrT = Gr'$ and we let $t(r) =
        rTr'^{-1}$. Note that $s(r)$ and $t(r)$ are in $G$ for
        all~$r$.  Then $G$ is generated by $s(R)\cup t(R)$.  There are
        more sophisticated algorithms using group actions on trees
        (and Farey symbols) that give smaller generating sets.
        """
        # 1. Make a dictionary
        #       (c,d) mod N --> matrix (a,b,lift c, lift d) in SL_2(Z)
        # 2. To compute the above maps efficiently, use right matrix
        #    multiplication and reduce bottom two entries then use dictionary.

        raise NotImplemented
        D = {}
        for r in self.coset_reps():
            c,d = (r[1,0], r[1,1])




class SL2Z(Gamma0):
    r"""
    The modular group $\SL_2(\Z)$.

    EXAMPLES:
        sage: G = SL2Z(); G
        Modular Group SL(2,Z)
        sage: G.gens()
        ([ 0 -1]
        [ 1  0], [1 1]
        [0 1])
        sage: G.0
        [ 0 -1]
        [ 1  0]
        sage: G.1
        [1 1]
        [0 1]
        sage: latex(G)
        \mbox{\rm SL}_2(\mathbf{Z})
        sage: G([1,-1,0,1])
        [ 1 -1]
        [ 0  1]
        sage: loads(G.dumps()) == G
        True
    """
    def __init__(self):
        Gamma0.__init__(self, 1)

    def _repr_(self):
        return "Modular Group SL(2,Z)"

    def _latex_(self):
        return "\\mbox{\\rm SL}_2(%s)"%(IntegerRing()._latex_())

    def is_subgroup(self, right):
        """
        Return True if self is a subgroup of right.
        """
        return right.level() == 1

    def gens(self):
        try:
            return self.__gens
        except AttributeError:
            self.__gens = (self([0, -1, 1, 0]), self([1, 1, 0, 1]))
            return self.__gens

    def gen(self, n):
        return self.gens()[n]

    def ngens(self):
        return 2

    def __call__(self, x, check=True):
        if isinstance(x, CongruenceSubgroupElement) and x.parent() == self:
            return x
        return CongruenceSubgroupElement(self, x, check=check)


class Gamma1(CongruenceSubgroup):
    r"""
    The congruence subgroup $\Gamma_1(N)$.

    EXAMPLES:
        sage: G = Gamma1(11); G
        Congruence Subgroup Gamma1(11)
        sage: loads(G.dumps()) == G
        True
    """
    def __init__(self, level):
        CongruenceSubgroup.__init__(self, level)

    def _repr_(self):
        return "Congruence Subgroup Gamma1(%s)"%self.level()

    def _latex_(self):
        return "\\Gamma_1(%s)"%self.level()

    def __cmp__(self, right):
        if not isinstance(right, Gamma1):
            return -1
        if self.level() < right.level():
            return -1
        elif self.level() > right.level():
            return 1
        return 0

    def is_subgroup(self, right):
        """
        Return True if self is a subgroup of right.

        EXAMPLES:
            sage: Gamma1(3).is_subgroup(SL2Z())
            True
            sage: Gamma1(3).is_subgroup(Gamma1(5))
            False
            sage: Gamma1(3).is_subgroup(Gamma1(6))
            False
            sage: Gamma1(6).is_subgroup(Gamma1(3))
            True

        """
        if right.level() == 1:
            return True
        if isinstance(right, (Gamma1, Gamma0)):
            return self.level() % right.level() == 0
        raise NotImplementedError

class GammaH(CongruenceSubgroup):
    r"""
    The congruence subgroup $\Gamma_H(N)$.

    TODO: This is NOT really implemented yet.
    """
    def __init__(self, level, H):
        CongruenceSubgroup.__init__(self, level)
        self.__H = H

    def _repr_(self):
        return "Congruence Subgroup Gamma_H(%s,H=%s)"%(self.level(), self.__H)

    def _latex_(self):
        return "\\Gamma_H(%s)"%self.level()



import sage.ext.congroup_pyx
degeneracy_coset_representatives_gamma0 = sage.ext.congroup_pyx.degeneracy_coset_representatives_gamma0
degeneracy_coset_representatives_gamma1 = sage.ext.congroup_pyx.degeneracy_coset_representatives_gamma1



## def xxx_degeneracy_coset_representatives_gamma0(N, M, t):
##     r"""
##     Let $N$ be a positive integer and $M$ a multiple of $N$.  Let $t$ be a
##     divisor of $N/M$, and let $T$ be the $2x2$ matrix $T=[0,0; 0,t]$.
##     This function returns representatives for the orbit set
##     $\Gamma_0(N) \backslash T \Gamma_0(M)$, where $\Gamma_0(N)$
##     acts on the left on $T \Gamma_0(M)$.

##     INPUT:
##         N -- int
##         M -- int (divisor of N)
##         t -- int (divisors of N/M)

##     OUTPUT:
##         list -- list of lists [a,b,c,d], where [a,b,c,d] should
##                 be viewed as a 2x2 matrix.

##     This function is used for computation of degeneracy maps between
##     spaces of modular symbols, hence its name.

##     We use that $T^{-1}*(a,b;c,d)*T = (a,bt,c/t,d),$
##     that the group $T^{-1}Gamma_0(N) T$ is contained in $\Gamma_0(M)$,
##     and that $\Gamma_0(N) T$ is contained in $T \Gamma_0(M)$.

##     ALGORITHM:
##     \begin{enumerate}
##     \item Compute representatives for $\Gamma_0(N/t,t)$ inside of $\Gamma_0(M)$:
##           COSET EQUIVALENCE:
##            Two right cosets represented by $[a,b;c,d]$ and
##            $[a',b';c',d']$ of $\Gamma_0(N/t,t)$ in $\SL_2(\Z)$
##            are equivalent if and only if
##            $(a,b)=(a',b')$ as points of $\P^1(\Z/t\Z)$,
##            i.e., $ab' \con ba' \pmod{t}$,
##            and $(c,d) = (c',d')$ as points of $\P^1(\Z/(N/t)\Z)$.

##         ALGORITHM to list all cosets:
##         \begin{enumerate}
##            \item Compute the number of cosets.
##            \item Compute a random element x of Gamma_0(M).
##            \item Check if x is equivalent to anything generated so
##                far; if not, add x to the list.
##            \item Continue until the list is as long as the bound
##                computed in A.
##         \end{enumerate}

##     \item There is a bijection between $\Gamma_0(N)\backslash T \Gamma_0(M)$
##           and $\Gamma_0(N/t,t) \Gamma_0(M)$ given by $T r$ corresponds to $r$.
##           Consequently we obtain coset representatives for
##           $\Gamma_0(N)\backslash T \Gamma_0(M)$ by left multiplying by $T$ each
##           coset representative of $\Gamma_0(N/t,t) \Gamma_0(M)$ found
##           in step 1.
##     \end{enumerate}
##     """
##     import sage.modular.dims as dims
##     N = int(N); M = int(M); t = int(t)
##     if N % M != 0:
##         raise ArithmeticError, "M (=%s) must be a divisor of N (=%s)"%(M,N)
##     n     = dims.idxG0(N) // dims.idxG0(M)          # number of coset representatives.
##     Ndivd = N // t
##     R     = []                        # coset reps found so far.
##     halfmax = 2*(n+10)
##     while len(R) < n:
##         # try to find another coset representative.
##         cc = M*random.randrange(-halfmax, halfmax+1)
##         dd =   random.randrange(-halfmax, halfmax+1)
##         g, bb, aa = arith.xgcd(-cc,dd)
##         if g == 0: continue
##         cc //= g
##         dd //= g
##         if cc % M != 0: continue
##         # Test if we've found a new coset representative.
##         is_new = True
##         for r in R:
##             if ((r[1]*aa - r[0]*bb) % t == 0) and \
##                      ((r[3]*cc - r[2]*dd) % Ndivd == 0):
##                 is_new = False
##                 break
##         # If our matrix is new add it to the list.
##         if is_new: R.append([aa,bb,cc,dd])
##     # Return the list left multiplied by T.
##     return [[r[0], r[1], r[2]*t, r[3]*t] for r in R]
