r"""
Congruence subgroups of SL2(Z)

\sage can compute with the congruence subgroups $\Gamma_0(N)$,
$\Gamma_1(N)$, and $\Gamma_H(N)$.

AUTHOR:
    -- William Stein
"""


#TODO:
#    -- added "gens" functions for each subgroup (since this is such a
#       frequently requested features).

################################################################################
#
#       Copyright (C) 2004, 2006 William Stein <wstein@gmail.com>
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

from sage.rings.integer_ring import IntegerRing, ZZ
from sage.rings.integer_mod_ring import IntegerModRing


from sage.rings.infinity import infinity


from congroup_element import CongruenceSubgroupElement

import sage.modular.modsym.p1list

from math import sqrt
import sage.ext.arith as fast_arith

from sage.rings.all import QQ, divisors

def get_gcd(order):
    if order <= 46340:   # todo: don't hard code
        return fast_arith.arith_int().gcd_int
    elif order <= 2147483647:   # todo: don't hard code
        return fast_arith.arith_llong().gcd_longlong
    raise NotImplementedError

def get_inverse_mod(order):
    if order <= 46340:   # todo: don't hard code
        return fast_arith.arith_int().inverse_mod_int
    elif order <= 2147483647:   # todo: don't hard code
        return fast_arith.arith_llong().inverse_mod_longlong
    raise NotImplementedError


def is_CongruenceSubgroup(x):
    return isinstance(x, CongruenceSubgroup)

class CongruenceSubgroup(Group):
    def __init__(self, level):
        level = ZZ(level)
        if level <= 0:
            raise ArithmeticError, "Congruence groups only defined for positive levels."
        self.__level = level

    def _repr_(self):
        return "Generic congruence subgroup"

    def __hash__(self):
        return hash(str(self))

    def modular_symbols(self, sign=0, weight=2, base_ring=QQ):
        """
        EXAMPLES:
            sage: G = Gamma0(23)
            sage: G.modular_symbols()
            Modular Symbols space of dimension 5 for Gamma_0(23) of weight 2 with sign 0 over Rational Field
            sage: G.modular_symbols(weight=4)
            Modular Symbols space of dimension 12 for Gamma_0(23) of weight 4 with sign 0 over Rational Field
            sage: G.modular_symbols(base_ring=GF(7))
            Modular Symbols space of dimension 5 for Gamma_0(23) of weight 2 with sign 0 over Finite Field of size 7
            sage: G.modular_symbols(sign=1)
            Modular Symbols space of dimension 3 for Gamma_0(23) of weight 2 with sign 1 over Rational Field
        """
        from sage.modular.modsym.modsym import ModularSymbols
        return ModularSymbols(self, sign=sign, weight=weight, base_ring=base_ring)

    def modular_abelian_variety(self):
        """
        Return the corresponding modular abelian variety.

        EXAMPLES:
            sage: Gamma0(11).modular_abelian_variety()
            Jacobian of the modular curve associated to the congruence subgroup Gamma0(11)
            sage: Gamma1(11).modular_abelian_variety()
            Jacobian of the modular curve associated to the congruence subgroup Gamma1(11)
            sage: GammaH(11,[3]).modular_abelian_variety()
            Jacobian of the modular curve associated to the congruence subgroup Gamma_H(11) with H generated by [3]
        """
        from sage.modular.abvar.abvar_ambient_jacobian import ModAbVar_ambient_jacobian
        return ModAbVar_ambient_jacobian(self)

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

    def is_odd(self):
        """
        Return True precisely if this subgroup does not contain the
        matrix -1.
        """
        return not self.is_even()

    def is_even(self):
        """
        Return True precisely if this subgroup contains the matrix -1.
        """
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


def is_Gamma0(x):
    return isinstance(x, Gamma0)

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

    def _generators_for_H(self):
        """
        EXAMPLES:
            sage: Gamma0(15)._generators_for_H()
            [11, 7]
        """
        try:
            return self.__generators_for_H
        except AttributeError:
            self.__generators_for_H = [int(x) for x in IntegerModRing(self.level()).unit_gens()]
            return self.__generators_for_H

    def _list_of_elements_in_H(self):
        """
        Returns a sorted list of Python ints that are representatives
        between 0 and N-1 of the elements of H.

        EXAMPLES:
            sage: G = Gamma0(11)
            sage: G._list_of_elements_in_H()
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        """
        return range(1, self.level())

    def __cmp__(self, right):
        if not isinstance(right, Gamma0):
            return -1
        if self.level() < right.level():
            return -1
        elif self.level() > right.level():
            return 1
        return 0

    def is_even(self):
        """
        Return True precisely if this subgroup contains the matrix -1.
        """
        return True

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
        congruence subgroup in ${\rm SL}_2(\Z)$ as a generator.

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
        (Todd-Coxeter?), and generators for ${\rm SL}_2(\Z)$.

        ALGORITHM: Given coset representatives for a finite index
        subgroup~$G$ of ${\rm SL}_2(\Z)$ we compute generators for~$G$ as
        follows.  Let $R$ be a set of coset representatives for $G$.
        Let $S, T \in {\rm SL}_2(\Z)$ be defined by \code{0,-1,1,0]} and
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

        raise NotImplementedError
        D = {}
        for r in self.coset_reps():
            c,d = (r[1,0], r[1,1])

    def gamma_h_subgroups(self):
        r"""
        Return the subgrops of the form $\Gamma_H(N)$ contained
        in self, where $N$ is the level of self.

        EXAMPLES:
            sage: G = Gamma0(11)
            sage: G.gamma_h_subgroups()
            [Congruence Subgroup Gamma_H(11) with H generated by [2], Congruence Subgroup Gamma_H(11) with H generated by [4], Congruence Subgroup Gamma_H(11) with H generated by [10], Congruence Subgroup Gamma_H(11) with H generated by []]
            sage: G = Gamma0(12)
            sage: G.gamma_h_subgroups()
            [Congruence Subgroup Gamma_H(12) with H generated by [5, 7], Congruence Subgroup Gamma_H(12) with H generated by [7], Congruence Subgroup Gamma_H(12) with H generated by [5], Congruence Subgroup Gamma_H(12) with H generated by []]
        """
        N = self.level()
        R = IntegerModRing(N)
        return [GammaH(N, H) for H in R.multiplicative_subgroups()]


def is_SL2Z(x):
    return isinstance(x, SL2Z)

class SL2Z(Gamma0):
    r"""
    The modular group ${\rm SL}_2(\Z)$.

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

    def is_even(self):
        """
        Return True precisely if this subgroup contains the matrix -1.
        """
        return True

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


def is_Gamma1(x):
    return isinstance(x, Gamma1)

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

    def is_even(self):
        """
        Return True precisely if this subgroup contains the matrix -1.
        """
        return self.level() in [1,2]

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

def GammaH(level, H):
    r"""
    Return the congruence subgroup $\Gamma_H(N)$.

    INPUT:
        level -- an integer
        H -- either 0, 1, or a list
             * If H is a list, return $\Gamma_H(N)$, where $H$
               is the subgroup of $(\Z/N\Z)^*$ *generated* by the
               elements of the list.
             * If H = 0, returns $\Gamma_0(N)$.
             * If H = 1, returns $\Gamma_1(N)$.

    EXAMPLES:
        sage: GammaH(11,0)
        Congruence Subgroup Gamma0(11)
        sage: GammaH(11,1)
        Congruence Subgroup Gamma1(11)
        sage: GammaH(11,[2])
        Congruence Subgroup Gamma_H(11) with H generated by [2]
        sage: GammaH(11,[2,1])
        Congruence Subgroup Gamma_H(11) with H generated by [2]
    """
    if H == 0:
        return Gamma0(level)
    elif H == 1:
        return Gamma1(level)
    return GammaH_class(level, H)

def is_GammaH(x):
    return isinstance(x, GammaH_class)

class GammaH_class(CongruenceSubgroup):
    r"""
    The congruence subgroup $\Gamma_H(N)$.
    """
    def __init__(self, level, H):
        CongruenceSubgroup.__init__(self, level)
        if not isinstance(H, list):
            raise TypeError, "H must be a list."
        H = list(set(H))
        H.sort()
        if 1 in H:
            H.remove(1)
        self.__H = H

    def restrict(self, M):
        r"""
        Return the subgroup of $\Gamma_0(M)$ obtained by taking $H$ to be the
        iamge of the $H$ at level $N$ modulo $M$.

        EXAMPLES:
            sage: G = GammaH(33,[2])
            sage: G.restrict(11)
            Congruence Subgroup Gamma_H(11) with H generated by [2]
            sage: G.restrict(1)
            Congruence Subgroup Gamma_H(1) with H generated by []
            sage: G.restrict(15)
            Traceback (most recent call last):
            ...
            ValueError: M (=15) must be a divisor of the level (33) of self
        """
        N = self.level()
        M = ZZ(M)
        if N % M:
            raise ValueError, "M (=%s) must be a divisor of the level (%s) of self"%(M, N)
        if N == M:
            return self
        v = self.__H
        w = [a % M for a in v if a%M]
        return GammaH(M, w)

    def divisor_subgroups(self):
        r"""
        Given this congruence subgroup $\Gamma_H(N)$, return all
        subgroups $\Gamma_G(M)$ for $M$ a divisor of $N$ and such that
        $G$ is equal to the image of $H$ modulo $M$.

        EXAMPLES:
            sage: G = GammaH(33,[2]); G
            Congruence Subgroup Gamma_H(33) with H generated by [2]
            sage: G._list_of_elements_in_H()
            [1, 2, 4, 8, 16, 17, 25, 29, 31, 32]
            sage: G.divisor_subgroups()
            [Congruence Subgroup Gamma_H(1) with H generated by [],
             Congruence Subgroup Gamma_H(3) with H generated by [2],
             Congruence Subgroup Gamma_H(11) with H generated by [2],
             Congruence Subgroup Gamma_H(33) with H generated by [2]]
        """
        v = self.__H
        ans = []
        for M in divisors(self.level()):
            w = [a % M for a in v if a%M]
            ans.append(GammaH(M, w))
        return ans

    def __cmp__(self, other):
        if not isinstance(other, CongruenceSubgroup):
            return cmp(type(self), type(other))
        if isinstance(other, GammaH_class):
            c = cmp(self.level(), other.level())
            if c: return c
            return cmp(self._list_of_elements_in_H(), other._list_of_elements_in_H())
        return cmp(type(self), type(other))

    def _generators_for_H(self):
        return self.__H

    def _repr_(self):
        return "Congruence Subgroup Gamma_H(%s) with H generated by %s"%(self.level(), self.__H)

    def _latex_(self):
        return "\\Gamma_H(%s)"%self.level()

    def _list_of_elements_in_H(self):
        """
        Returns a sorted list of Python ints that are representatives
        between 0 and N-1 of the elements of H.

        WARNING: Do not change this returned list.

        EXAMPLES:
            sage: G = GammaH(11,[3]); G
            Congruence Subgroup Gamma_H(11) with H generated by [3]
            sage: G._list_of_elements_in_H()
            [1, 3, 4, 5, 9]
        """
        try:
            return self.__list_of_elements_in_H
        except AttributeError:
            pass
        N = self.level()
        if N == 1:
            self.__list_of_elements_in_H = [1]
            return [1]
        gens = self.__H

        H = set([1])
        N = int(N)
        for g in gens:
            if sage.rings.arith.gcd(g, N) != 1:
                raise ValueError, "gen (=%s) is not in (Z/%sZ)^*"%(g,N)
            gk = int(g) % N
            sbgrp = [gk]
            while not (gk in H):
                gk = (gk * g)%N
                sbgrp.append(gk)
            H = set([(x*h)%N for x in sbgrp for h in H])
        H = list(H)
        H.sort()
        self.__list_of_elements_in_H = H
        return H

    def is_even(self):
        """
        Return True precisely if this subgroup contains the matrix -1.
        """
        if self.level() == 1:
            return True
        v = self._list_of_elements_in_H()
        return int(self.level() - 1) in v

    def _coset_reduction_data_first_coord(G):
        """
        Compute data used for determining the canonical coset
        representative of an element of SL_2(Z) modulo G.  This function
        specfically returns data needed for the first part of the
        reduction step (the first coordinate).

        INPUT:
            G -- a congruence subgroup Gamma_0(N), Gamma_1(N), or Gamma_H(N).

        OUTPUT:
            A list v such that
                v[u] = (min(u*h: h in H),
                        gcd(u,N) ,
                        an h such that h*u = min(u*h: h in H)).

        EXAMPLES:
            sage: G = GammaH(12,[-1,5]); G
            Congruence Subgroup Gamma_H(12) with H generated by [-1, 5]
            sage: G._coset_reduction_data_first_coord()
            [(0, 12, 0), (1, 1, 1), (2, 2, 1), (3, 3, 1), (4, 4, 1), (1, 1, 5), (6, 6, 1),
            (1, 1, 7), (4, 4, 5), (3, 3, 7), (2, 2, 5), (1, 1, 11)]
        """
        H = G._list_of_elements_in_H()
        N = int(G.level())
        SQN = int(sqrt(N))

        # Get some useful fast functions for inverse and gcd
        inverse_mod = get_inverse_mod(N)   # optimal gcd function
        gcd = get_gcd(N)   # optimal gcd function

        # We will be adding to this list below.
        reduct_data = [(0,0,N,0)] + [ (u, 1, 1, inverse_mod(u, N)) for u in H ]
        not_yet_done = list(set(range(1,N)).difference(set(H)))
        not_yet_done.sort()

        # Make a table of the reduction of H (mod N/d),
        # one for each divisor d <= sqrt(N).
        repr_H_mod_N_over_d = {}
        for d in divisors(N):
            N_over_d = N//d
            w = [1]
            z = [1]
            for x in H:
                if not (x % N_over_d  in  w):
                    w.append(x % N_over_d)
                    z.append(x)
            repr_H_mod_N_over_d[d] = z

        # Compute the rest of the tuples
        while len(not_yet_done) > 0:
            u = not_yet_done[0]
            d = gcd(u, N)
            z = repr_H_mod_N_over_d[d]
            v = [((u*x) % N,  u, d, inverse_mod(x, N)) for x in z]
            reduct_data += v
            not_yet_done = list(set(not_yet_done).difference(set([a[0] for a in v])))
            not_yet_done.sort()

        # delete first entry.
        reduct_data.sort()
        reduct_data = [(a,b,c) for _,a,b,c in reduct_data]
        return reduct_data

    def _coset_reduction_data_second_coord(G):
        """
        Compute data used for determining the canonical coset
        representative of an element of SL_2(Z) modulo G.  This function
        specfically returns data needed for the first part of the
        reduction step (the first coordinate).

        INPUT:
            G -- a congruence subgroup Gamma_0(N), Gamma_1(N), or Gamma_H(N).

        OUTPUT:
            dictionary v with keys the divisors of N that are < sqrt(N)
            such that v[d] is the subgroup {h in H : h = 1 (mod N/d)}.

        EXAMPLES:
            sage: G = GammaH(1200,[-1,7]); G
            Congruence Subgroup Gamma_H(1200) with H generated by [-1, 7]
            sage: G._coset_reduction_data_second_coord()
            {1: [1], 2: [1], 3: [1], 4: [1], 5: [1], 6: [1], 8: [1], 10: [1], 12: [1],
            15: [1], 16: [1], 20: [1], 24: [1, 1151], 25: [1, 49], 30: [1]}
        """
        H = G._list_of_elements_in_H()
        N = int(G.level())
        SQN = int(sqrt(N))
        v = { 1: [1] }
        for d in [x for x in divisors(N) if x > 1 and x <= SQN]:
            N_over_d = N // d
            v[d] = [x for x in H if x % N_over_d == 1]
        return v

    def _coset_reduction_data(self):
        """
        Compute data used for determining the canonical coset
        representative of an element of SL_2(Z) modulo G.

        EXAMPLES:
            sage: G = GammaH(12,[-1,7]); G
            Congruence Subgroup Gamma_H(12) with H generated by [-1, 7]
            sage: G._coset_reduction_data()
            ([(0, 12, 0), (1, 1, 1), (2, 2, 1), (3, 3, 1), (4, 4, 1), (1, 1, 5), (6, 6, 1),
              (1, 1, 7), (4, 4, 5), (3, 3, 7), (2, 2, 5), (1, 1, 11)],
              {1: [1], 2: [1, 7], 3: [1, 5]})
        """
        try:
            return self.__coset_reduction_data
        except AttributeError:
            pass
        self.__coset_reduction_data = (self._coset_reduction_data_first_coord(),
                                       self._coset_reduction_data_second_coord())
        return self.__coset_reduction_data


    def _reduce_coset(self, uu, vv):
        """
        Compute a canonical form for a given Manin symbol.

        INPUT:
        Two integers (uu,vv) that define an element of $(Z/NZ)^2$.
            uu -- an integer
            vv -- an integer

        OUTPUT:
           pair of integers that are equivalent to (uu,vv).

        NOTE: We do *not* require that gcd(uu,vv,N) = 1.  If the gcd is
        not 1, we return (0,0).

        EXAMPLE:
        An example at level 9.
            sage: G = GammaH(9,[7]); G
            Congruence Subgroup Gamma_H(9) with H generated by [7]
            sage: a = []
            sage: for i in range(G.level()):
            ...     for j in range(G.level()):
            ...       a.append(G._reduce_coset(i,j))
            sage: v = list(set(a))
            sage: v.sort()
            sage: v
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (3, 1), (3, 2), (6, 1), (6, 2)]

        An example at level 100.
            sage: G = GammaH(100,[3,7]); G
            Congruence Subgroup Gamma_H(100) with H generated by [3, 7]
            sage: a = []
            sage: for i in range(G.level()):
            ...   for j in range(G.level()):
            ...       a.append(G._reduce_coset(i,j))
            sage: v = list(set(a))
            sage: v.sort()
            sage: len(v)
            361
        """
        N = int(self.level())
        u = uu % N
        v = vv % N
        first, second = self._coset_reduction_data()
        gcd_u_N = first[u][1]
        gcd_v_N = first[v][1]
        if arith.gcd(gcd_u_N, gcd_v_N) != 1:
            return (0, 0)

        if u == 0:
            return (0, first[v][0])
        if v == 0:
            return (first[u][0], 0)

        def f(u,v):
            v = (v*first[u][2]) % N
            d = first[u][1]   # gcd(u,N)
            u = first[u][0]
            H_cong1_mod_N_over_d = second[d]
            if len(H_cong1_mod_N_over_d) > 1:
                vmin = v
                for x in H_cong1_mod_N_over_d:
                    v1 = (v*x) % N
                    if v1 < vmin:
                        vmin = v1
                    v = vmin
            return u,v

        if gcd_u_N <= gcd_v_N:
            (u,v) = f(u,v)
        else:
            (v,u) = f(v,u)

        return (u,v)


    def _reduce_cusp(self, c):
        """
        Compute a canonical form for the cusp $uu/vv$.

        INPUT:
            cusp
        OUTPUT:
            cusp


        OUTPUT:
            bool -- True if self and other are equivalent
            int -- $1$, $0$, or $-1$,
                   If the two cusps are $u1/v1$ and $u2/v2$, then they are
                   equivalent modulo Gamma_H(N) if and only if
                        $v1 =  h*v2 (mod N)$ and $u1 =  h^(-1)*u2 (mod gcd(v1,N))$
                   or
                        $v1 = -h*v2 (mod N)$ and $u1 = -h^(-1)*u2 (mod gcd(v1,N))$
                   where $h \in H$.   In the first case we return $1$, and in
                   the second we return $-1$.   We return $0$ if the two
                   cusps are not equivalent.

        EXAMPLE:
        """
        from sage.rings.integer import Integer
        N = int(self.level())
        Cusps = c.parent()
        u = int(c.numerator() % N)
        v = int(c.denominator() % N)
        first, second = self._coset_reduction_data()
        gcd_u_N = first[u][1]
        gcd_v_N = first[v][1]

        if u == 0:
            return Cusps(0), 1
        if v == 0:
            return Cusps((1,0)), 1

        def f(u,v):
            h = first[v][2]
            v = first[v][0]
            hinv = int(Integer(h).inverse_mod(gcd_v_N))     # optimize
            d = first[v][1]   # d = gcd(v,N)
            if d == 1:
                return 0, 1, h
            u = (hinv * u) % d
            H_cong1_mod_N_over_d = second[d]
            if len(H_cong1_mod_N_over_d) > 1:
                umin = u
                for x in H_cong1_mod_N_over_d:
                    u1 = (u*x) % d
                    if u1 < umin:
                        umin = u1
                    u = umin
            return u,v, h

        u, v, h = f(u,v)
        N_over_2 = N//2
        if u > N_over_2:
            u = N_over_2 - u
            v = N_over_2 - v
            t = -1
        else:
            t = 1

        return Cusps((u,v)), t


import congroup_pyx
degeneracy_coset_representatives_gamma0 = congroup_pyx.degeneracy_coset_representatives_gamma0
degeneracy_coset_representatives_gamma1 = congroup_pyx.degeneracy_coset_representatives_gamma1



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
##            $[a',b';c',d']$ of $\Gamma_0(N/t,t)$ in ${\rm SL}_2(\Z)$
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
