"""
Base class for modular abelian varieties
"""

###########################################################################
#       Copyright (C) 2004,2007 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
###########################################################################

from sage.structure.sage_object import SageObject
from hecke_operator             import HeckeOperator
from torsion_subgroup           import TorsionSubgroup
from cuspidal_subgroup          import CuspidalSubgroup, RationalCuspidalSubgroup
from sage.rings.all             import ZZ, QQ

import homology

def is_ModularAbelianVariety(x):
    return isinstance(x, ModularAbelianVariety)

class ModularAbelianVariety(SageObject):
    def __init__(self, level, base_ring):
        self._level = level
        self._base_ring = base_ring


    def _repr_(self):
        return "Modular abelian variety of level %s over %s"%(self._level, self._base_ring)

    def level(self):
        """
        Return the level of this modular abelian variety, which is an integer
        N (usually minimal) such that this modular abelian variety is a quotient
        of $J_1(N)$.

        EXAMPLES:
            sage: J1(5077).level()
            5077
            sage: JH(389,[4]).level()
            389
        """
        return self._level

    def base_ring(self):
        return self._base_ring

    def homology(self, base_ring=ZZ):
        """
        Return the homology of this modular abelian variety.

        WARNING: For efficiency reasons the basis of the integral
        homology need not be the same as the basis for the rational
        homology.

        EXAMPLES:
            sage: J0(389).homology(GF(7))
            Homology with coefficients in Finite Field of size 7 of Jacobian of the modular curve associated to the congruence subgroup Gamma0(389)
            sage: J0(389).homology(QQ)
            Rational Homology of Jacobian of the modular curve associated to the congruence subgroup Gamma0(389)
            sage: J0(389).homology(ZZ)
            Integral Homology of Jacobian of the modular curve associated to the congruence subgroup Gamma0(389)
        """
        try:
            return self._homology[base_ring]
        except AttributeError:
            self._homology = {}
        except KeyError:
            pass
        if base_ring == ZZ:
            H = homology.IntegralHomology(self)
        elif base_ring == QQ:
            H = homology.RationalHomology(self)
        else:
            H = homology.Homology_over_base(self, base_ring)
        self._homology[base_ring] = H
        return H

    def integral_homology(self):
        return self.homology(ZZ)

    def rational_homology(self):
        return self.homology(QQ)

    def hecke_operator(self, n):
        try:
            return self._hecke_operator[n]
        except AttributeError:
            self._hecke_operator = {}
        except KeyError:
            pass
        Tn = HeckeOperator(self, n)
        self._hecke_operator[n] = Tn
        return Tn

    def hecke_polynomial(self, n, var='x'):
        """
        Return the characteristic polynomial of the n-th Hecke
        operator on self.

        NOTE: If self has dimension d, then this is a polynomial of
        degree d.  It is not of degree 2*d, so it is the square root
        of the characteristic polynomial of the Hecke operator on
        integral or rational homology (which has degree degree 2*d).

        EXAMPLES:
            sage: factor(J0(11).hecke_polynomial(2))
            x + 2
            sage: factor(J0(23).hecke_polynomial(2))
            x^2 + x - 1
            sage: factor(J1(13).hecke_polynomial(2))
            x^2 + 3*x + 3
            sage: factor(J0(43).hecke_polynomial(2))
            (x + 2) * (x^2 - 2)

        The Hecke polynomial is the square root of the characteristic
        polynomial:
            sage: factor(J0(43).hecke_operator(2).charpoly())
            (x + 2)^2 * (x^2 - 2)^2
        """
        return self.modular_symbols(sign=1).hecke_polynomial(n, var)

    def torsion_subgroup(self):
        try:
            return self._torsion_subgroup
        except AttributeError:
            T = TorsionSubgroup(self)
            self._torsion_subgroup = T
            return T

    def cuspidal_subgroup(self):
        try:
            return self._cuspidal_subgroup
        except AttributeError:
            T = CuspidalSubgroup(self)
            self._cuspidal_subgroup = T
            return T

    def rational_cuspidal_subgroup(self):
        try:
            return self._rational_cuspidal_subgroup
        except AttributeError:
            T = RationalCuspidalSubgroup(self)
            self._rational_cuspidal_subgroup = T
            return T


    ####################################################
    # Derived classes must overload these:
    def dimension(self):
        raise NotImplementedError

    ####################################################
    # Derived class should overload these
    def change_ring(self, R):
        raise NotImplementedError

    def modular_symbols(self, sign=0):
        """
        Return the modular symbols space associated to self.

        This raises a ValueError if there is no associated modular
        symbols space.
        """
        raise ValueError, "no associated modular symbols space"

    def _integral_hecke_matrix(self, n):
        # this is allowed to raise an error if
        # associated modular symbols space.
        raise ValueError, "no action of Hecke operators over ZZ"

    def _rational_hecke_matrix(self, n):
        raise ValueError, "no action of Hecke operators over QQ"
