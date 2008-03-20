"""
Cuspidal subgroups of modular abelian varieties

AUTHOR:
    -- William Stein (2007-03, 2008-02)

EXAMPLES:
We compute the cuspidal subgroup of $J_1(13)$:
    sage: A = J1(13)
    sage: C = A.cuspidal_subgroup(); C
    Finite subgroup with invariants [19, 19] over QQbar of Abelian variety J1(13) of dimension 2
    sage: C.gens()
    [[(1/19, 0, 0, 9/19)], [(0, 1/19, 1/19, 18/19)]]
    sage: C.order()
    361
    sage: C.invariants()
    [19, 19]

We compute the cuspidal subgroup of $J_0(54)$:
    sage: A = J0(54)
    sage: C = A.cuspidal_subgroup(); C
    Finite subgroup with invariants [3, 3, 3, 3, 3, 9] over QQbar of Abelian variety J0(54) of dimension 4
    sage: C.gens()
    [[(1/3, 0, 0, 0, 0, 1/3, 0, 2/3)], [(0, 1/3, 0, 0, 0, 2/3, 0, 1/3)], [(0, 0, 1/9, 1/9, 1/9, 1/9, 1/9, 2/9)], [(0, 0, 0, 1/3, 0, 1/3, 0, 0)], [(0, 0, 0, 0, 1/3, 1/3, 0, 1/3)], [(0, 0, 0, 0, 0, 0, 1/3, 2/3)]]
    sage: C.order()
    2187
    sage: C.invariants()
    [3, 3, 3, 3, 3, 9]

We compute the subgroup of the cuspidal subgroup generated by rational cusps.
    sage: C = J0(54).rational_cusp_subgroup(); C
    Finite subgroup with invariants [3, 3, 9] over QQbar of Abelian variety J0(54) of dimension 4
    sage: C.gens()
    [[(1/3, 0, 0, 1/3, 2/3, 1/3, 0, 1/3)], [(0, 0, 1/9, 1/9, 7/9, 7/9, 1/9, 8/9)], [(0, 0, 0, 0, 0, 0, 1/3, 2/3)]]
    sage: C.order()
    81
    sage: C.invariants()
    [3, 3, 9]

This might not give us the exact rational torsion subgroup, since it might
be bigger than order $81$:
    sage: J0(54).torsion_subgroup().multiple_of_order()
    243

TESTS:
    sage: C = J0(54).cuspidal_subgroup()
    sage: loads(dumps(C)) == C
    True
    sage: D = J0(54).rational_cusp_subgroup()
    sage: loads(dumps(D)) == D
    True
"""

###########################################################################
#       Copyright (C) 2007 William Stein <wstein@gmail.com>               #
#  Distributed under the terms of the GNU General Public License (GPL)    #
#                  http://www.gnu.org/licenses/                           #
###########################################################################

from finite_subgroup         import FiniteSubgroup
from sage.rings.all          import infinity, QQ, gcd
from sage.matrix.all         import matrix
from sage.modular.congroup   import is_Gamma0
from sage.modular.cusps      import Cusp

class CuspidalSubgroup_generic(FiniteSubgroup):
    def _compute_generators(self, rational_only=False):
        r"""
        Return a list of vectors that define elements of the rational
        homology that generate this finite subgroup.

        INPUT:
            rational_only -- bool (default: False); if \code{True}, only
            use rational cusps.

        OUTPUT:
            list -- list of vectors

        EXAMPLES:
            sage: J = J0(37)
            sage: C = sage.modular.abvar.cuspidal_subgroup.CuspidalSubgroup(J)
            sage: C._compute_generators()
            [(0, 0, 0, 1/3)]
            sage: J = J0(43)
            sage: C = sage.modular.abvar.cuspidal_subgroup.CuspidalSubgroup(J)
            sage: C._compute_generators()
            [(0, -1/7, 0, 1/7, 0, 2/7)]
            sage: J = J0(22)
            sage: C = sage.modular.abvar.cuspidal_subgroup.CuspidalSubgroup(J)
            sage: C._compute_generators()
            [(0, 0, 0, -1/5), (-1/5, -1/5, 1/5, 2/5), (-1/5, -1/5, 1/5, -2/5)]
            sage: J = J1(13)
            sage: C = sage.modular.abvar.cuspidal_subgroup.CuspidalSubgroup(J)
            sage: len(C._compute_generators())
            11
            sage: C._compute_generators()[:3]
            [(0, 1/19, 1/19, -1/19), (6/19, -2/19, -2/19, -1/19), (4/19, -2/19, -2/19, 0)]

        We compute with and without the optional \code{rational_only} option.
            sage: J = J0(27); G = sage.modular.abvar.cuspidal_subgroup.CuspidalSubgroup(J)
            sage: G._compute_generators()
            [(1/3, 0), (0, -1/3), (-1/3, 1/3), (1/3, 1/3), (-1/3, -1/3)]
            sage: G._compute_generators(rational_only=True)
            [(1/3, 0)]
        """
        A = self.abelian_variety()
        M = A.modular_symbols()
        I = M.integral_period_mapping().matrix()
        Amb = M.ambient_module()
        C = Amb.cusps()
        N = Amb.level()
        if rational_only:
            if not is_Gamma0(A.group()):
                raise NotImplementedError, 'computation of rational cusps only implemented in Gamma0 case.'
            if not N.is_squarefree():
                data = [n for n in range(2,N) if gcd(n,N) == 1]
                C = [c for c in C if is_rational_cusp_gamma0(c, N, data)]


        G = [Amb([infinity, alpha]).element() for alpha in C]
        J = matrix(QQ, len(G), Amb.dimension(), G)
        R = (J * I).rows()
        return [x for x in R if x.denominator() != 1]

    def _generators(self):
        """
        Returned cached tuple of vectors that define elements of the
        rational homology that generate this finite subgroup.

        OUTPUT:
            tuple -- cached

        EXAMPLES:
            sage: J = J0(27)
            sage: G = J.cuspidal_subgroup()
            sage: G._generators()
            ((1/3, 0), (0, 1/3))

        Test that the result is cached.
            sage: G._generators() is G._generators()
            True
        """
        try:
            return self.__gens
        except AttributeError:
            pass
        G = tuple(self._compute_generators(rational_only = False))
        self.__gens = G
        return G

class CuspidalSubgroup(CuspidalSubgroup_generic):
    """
    EXAMPLES:
        sage: a = J0(65)[2]
        sage: t = a.cuspidal_subgroup()
        sage: t.order()
        6
    """
    def _repr_(self):
        """
        String representation of the cuspidal subgroup.

        EXAMPLES:
            sage: G = J0(27).cuspidal_subgroup()
            sage: G._repr_()
            'Finite subgroup with invariants [3, 3] over QQbar of Abelian variety J0(27) of dimension 1'
        """
        return "Cuspidal subgroup %sover QQ of %s"%(self._invariants_repr(), self.abelian_variety())


class RationalCuspidalSubgroup(CuspidalSubgroup_generic):
    """
    EXAMPLES:
        sage: a = J0(65)[2]
        sage: t = a.rational_cusp_subgroup()
        sage: t.order()
        6
    """
    def _repr_(self):
        """
        String representation of the cuspidal subgroup.

        EXAMPLES:
            sage: G = J0(27).rational_cusp_subgroup()
            sage: G._repr_()
            'Finite subgroup with invariants [3] over QQbar of Abelian variety J0(27) of dimension 1'

        """
        return "Rational cuspidal subgroup %sover QQ of %s"%(self._invariants_repr(), self.abelian_variety())

    def _generators(self):
        """
        Returned cached tuple of vectors that define elements of the
        rational homology that generate this finite subgroup.

        OUTPUT:
            tuple -- cached

        EXAMPLES:
            sage: G = J0(27).rational_cusp_subgroup()
            sage: G._generators()
            ((1/3, 0),)

        Test that the result is cached.
            sage: G._generators() is G._generators()
            True
        """
        try:
            return self.__gens
        except AttributeError:
            pass
        G = tuple(self._compute_generators(rational_only = True))
        self.__gens = G
        return G


def is_rational_cusp_gamma0(c, N, data):
    """
    Return True if the rational number c is a rational cusp of level N.
    This uses remarks in Glenn Steven's Ph.D. thesis.

    INPUT:
        c -- a cusp
        N -- a positive integer
        data -- the list [n for n in range(2,N) if gcd(n,N) == 1], which is passed
                in as a parameter purely for efficiency reasons.

    EXAMPLES:
        sage: from sage.modular.abvar.cuspidal_subgroup import is_rational_cusp_gamma0
        sage: N = 27
        sage: data = [n for n in range(2,N) if gcd(n,N) == 1]
        sage: is_rational_cusp_gamma0(Cusp(1/3), N, data)
        False
        sage: is_rational_cusp_gamma0(Cusp(1), N, data)
        True
        sage: is_rational_cusp_gamma0(Cusp(oo), N, data)
        True
        sage: is_rational_cusp_gamma0(Cusp(2/9), N, data)
        False
    """
    num = c.numerator()
    den = c.denominator()
    for d in data:
        if not c.is_gamma0_equiv(Cusp(num,d*den), N):
            return False
    return True
