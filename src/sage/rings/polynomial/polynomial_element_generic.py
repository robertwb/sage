"""
Univariate Polynomials

AUTHORS:
    -- William Stein: first version
    -- Martin Albrecht: Added singular coercion.
    -- David Harvey: split off polynomial_integer_dense_ntl.pyx (2007-09)

TESTS:

We test coercion in a particularly complicated situation:
    sage: W.<w>=QQ['w']
    sage: WZ.<z>=W['z']
    sage: m = matrix(WZ,2,2,[1,z,z,z^2])
    sage: a = m.charpoly()
    sage: R.<x> = WZ[]
    sage: R(a)
    x^2 + ((-1)*z^2 + -1)*x
"""

################################################################################
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
################################################################################

import copy

from sage.rings.polynomial.polynomial_element import Polynomial, is_Polynomial, Polynomial_generic_dense
from sage.structure.element import (IntegralDomainElement, EuclideanDomainElement,
                                    PrincipalIdealDomainElement)

from sage.rings.polynomial.polynomial_singular_interface import Polynomial_singular_repr

from sage.libs.all import pari, pari_gen
from sage.libs.ntl.all import ZZ as ntl_ZZ, ZZX, zero_ZZX, ZZ_p, ZZ_pX, set_modulus
from sage.structure.factorization import Factorization

from sage.rings.infinity import infinity
from sage.rings.rational_field import QQ
from sage.rings.integer_ring import ZZ
import sage.rings.integer as integer
import sage.rings.complex_field as complex_field
import sage.rings.arith as arith

import sage.rings.fraction_field_element as fraction_field_element
import sage.rings.polynomial.polynomial_ring


class Polynomial_generic_sparse(Polynomial):
    """
    A generic sparse polynomial.

    EXAMPLES:
        sage: R.<x> = PolynomialRing(PolynomialRing(QQ, 'y'), sparse=True)
        sage: f = x^3 - x + 17
        sage: type(f)
        <class 'sage.rings.polynomial.polynomial_element_generic.Polynomial_generic_sparse'>
        sage: loads(f.dumps()) == f
        True
    """
    def __init__(self, parent, x=None, check=True, is_gen=False, construct=False):
        Polynomial.__init__(self, parent, is_gen=is_gen)
        if x is None:
            self.__coeffs = {}
            return
        R = parent.base_ring()
        if isinstance(x, Polynomial):
            if x.parent() == self.parent():
                x = dict(x.dict())
            elif x.parent() == R:
                x = {0:x}
            else:
                w = {}
                for n, c in x.dict().iteritems():
                    w[n] = R(c)
                #raise TypeError, "Cannot coerce %s into %s."%(x, parent)
        elif isinstance(x, list):
            y = {}
            for i in xrange(len(x)):
                if x[i] != 0:
                    y[i] = x[i]
            x = y
        elif not isinstance(x, dict):
            x = {0:x}   # constant polynomials
        elif isinstance(x, pari_gen):
            x = [R(w) for w in x.Vecrev()]
            check = True
        if check:
            self.__coeffs = {}
            for i, z in x.iteritems():
                self.__coeffs[i] = R(z)
        else:
            self.__coeffs = x
        if check:
            self.__normalize()

    def dict(self):
        """
        Return a new copy of the dict of the underlying
        elements of self.

        EXAMPLES:
            sage: R.<w> = PolynomialRing(Integers(8), sparse=True)
            sage: f = 5 + w^1997 - w^10000; f
            7*w^10000 + w^1997 + 5
            sage: d = f.dict(); d
            {0: 5, 10000: 7, 1997: 1}
            sage: d[0] = 10
            sage: f.dict()
            {0: 5, 10000: 7, 1997: 1}
        """
        return dict(self.__coeffs)

    def valuation(self):
        """
        EXAMPLES:
            sage: R.<w> = PolynomialRing(GF(9,'a'), sparse=True)
            sage: f = w^1997 - w^10000
            sage: f.valuation()
            1997
            sage: R(19).valuation()
            0
            sage: R(0).valuation()
            +Infinity
        """
        c = self.__coeffs.keys()
        if len(c) == 0:
            return infinity
        return ZZ(min(self.__coeffs.keys()))

    def derivative(self):
        """
        EXAMPLES:
            sage: R.<w> = PolynomialRing(ZZ, sparse=True)
            sage: f = R(range(9)); f
            8*w^8 + 7*w^7 + 6*w^6 + 5*w^5 + 4*w^4 + 3*w^3 + 2*w^2 + w
            sage: f.derivative()
            64*w^7 + 49*w^6 + 36*w^5 + 25*w^4 + 16*w^3 + 9*w^2 + 4*w + 1
        """
        d = {}
        for n, c in self.__coeffs.iteritems():
            d[n-1] = n*c
        if d.has_key(-1):
            del d[-1]
        return self.polynomial(d)

    def _dict_unsafe(self):
        """
        Return unsafe access to the underlying dictionary of coefficients.

        ** DO NOT use this, unless you really really know what you are doing. **

        EXAMPLES:
            sage: R.<w> = PolynomialRing(ZZ, sparse=True)
            sage: f = w^15 - w*3; f
            w^15 - 3*w
            sage: d = f._dict_unsafe(); d
            {1: -3, 15: 1}
            sage: d[1] = 10; f
            w^15 + 10*w
        """
        return self.__coeffs

    def _repr(self, name=None):
        r"""
        EXAMPLES:
            sage: R.<w> = PolynomialRing(CDF, sparse=True)
            sage: f = CDF(1,2) + w^5 - CDF(pi)*w + CDF(e)
            sage: f._repr()
            '1.0*w^5 + (-3.14159265359)*w + 3.71828182846 + 2.0*I'
            sage: f._repr(name='z')
            '1.0*z^5 + (-3.14159265359)*z + 3.71828182846 + 2.0*I'

        AUTHOR:
            -- David Harvey (2006-08-05), based on Polynomial._repr()
        """
        s = " "
        m = self.degree() + 1
        if name is None:
            name = self.parent().variable_name()
        atomic_repr = self.parent().base_ring().is_atomic_repr()
        coeffs = list(self.__coeffs.iteritems())
        coeffs.sort()
        for (n, x) in reversed(coeffs):
            if x != 0:
                if n != m-1:
                    s += " + "
                x = repr(x)
                if not atomic_repr and n > 0 and (x.find("+") != -1 or x.find("-") != -1):
                    x = "(%s)"%x
                if n > 1:
                    var = "*%s^%s"%(name,n)
                elif n==1:
                    var = "*%s"%name
                else:
                    var = ""
                s += "%s%s"%(x,var)
        if atomic_repr:
            s = s.replace(" + -", " - ")
        s = s.replace(" 1*"," ")
        s = s.replace(" -1*", " -")
        if s==" ":
            return "0"
        return s[1:]

    def __normalize(self):
        x = self.__coeffs
        zero = self.base_ring()(0)
        D = [n for n, z in x.iteritems() if not z]
        for n in D:
            del x[n]

    def __getitem__(self,n):
        """
        Return the n-th coefficient of this polynomial.

        Negative indexes are allowed and always return 0 (so you can
        view the polynomial as embedding Laurent series).

        EXAMPLES:
            sage: R.<w> = PolynomialRing(RDF, sparse=True)
            sage: e = RDF(e)
            sage: f = sum(e^n*w^n for n in range(4)); f
            20.0855369232*w^3 + 7.38905609893*w^2 + 2.71828182846*w + 1.0
            sage: f[1]
            2.71828182846
            sage: f[5]
            0.0
            sage: f[-1]
            0.0
        """
        if not self.__coeffs.has_key(n):
            return self.base_ring()(0)
        return self.__coeffs[n]

    def __getslice__(self, i, j):
        """
        EXAMPLES:
            sage: R.<x> = PolynomialRing(RealField(19), sparse=True)
            sage: f = (2-3.5*x)^3; f
            -42.875*x^3 + 73.500*x^2 - 42.000*x + 8.0000
            sage: f[1:3]
            73.500*x^2 - 42.000*x
            sage: f[:2]
            -42.000*x + 8.0000
            sage: f[2:]
            -42.875*x^3 + 73.500*x^2
        """
        if i < 0:
            i = 0
        v = {}
        x = self.__coeffs
        for k in x.keys():
            if i <= k and k < j:
                v[k] = x[k]
        P = self.parent()
        return P(v)

    def _unsafe_mutate(self, n, value):
        r"""
        Change the coefficient of $x^n$ to value.

        ** NEVER USE THIS ** -- unless you really know what you are doing.

        EXAMPLES:
            sage: R.<z> = PolynomialRing(CC, sparse=True)
            sage: f = z^2 + CC.0; f
            1.00000000000000*z^2 + 1.00000000000000*I
            sage: f._unsafe_mutate(0, 10)
            sage: f
            1.00000000000000*z^2 + 10.0000000000000

        Much more nasty:
            sage: z._unsafe_mutate(1, 0)
            sage: z
            0
        """
        n = int(n)
        value = self.base_ring()(value)
        x = self.__coeffs
        if n < 0:
            raise IndexError, "polynomial coefficient index must be nonnegative"
        if value == 0:
            if x.has_key(n):
                del x[n]
        else:
            x[n] = value

    def list(self):
        """
        Return a new copy of the list of the underlying
        elements of self.

        EXAMPLES:
            sage: R.<z> = PolynomialRing(Integers(100), sparse=True)
            sage: f = 13*z^5 + 15*z^2 + 17*z
            sage: f.list()
            [0, 17, 15, 0, 0, 13]
        """
        zero = self.base_ring()(0)
        v = [zero] * (self.degree()+1)
        for n, x in self.__coeffs.iteritems():
            v[n] = x
        return v

    #def _pari_(self, variable=None):
    #    if variable is None:
    #        return self.__pari
    #    else:
    #        return self.__pari.subst('x',variable)

    def degree(self):
        """
        Return the degree of this sparse polynomial.

        EXAMPLES:
            sage: R.<z> = PolynomialRing(ZZ, sparse=True)
            sage: f = 13*z^50000 + 15*z^2 + 17*z
            sage: f.degree()
            50000
        """
        v = self.__coeffs.keys()
        if len(v) == 0:
            return -1
        return max(v)

    def _add_(self, right):
        r"""
        EXAMPLES:
            sage: R.<x> = PolynomialRing(Integers(), sparse=True)
            sage: (x^100000 + 2*x^50000) + (4*x^75000 - 2*x^50000 + 3*x)
            x^100000 + 4*x^75000 + 3*x

        AUTHOR:
            -- David Harvey (2006-08-05)
        """
        output = dict(self.__coeffs)

        for (index, coeff) in right.__coeffs.iteritems():
            if index in output:
                output[index] += coeff
            else:
                output[index] = coeff

        output = self.polynomial(output, check=False)
        output.__normalize()
        return output

    def _mul_(self, right):
        r"""
        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ, sparse=True)
            sage: (x^100000 - x^50000) * (x^100000 + x^50000)
             x^200000 - x^100000
            sage: (x^100000 - x^50000) * R(0)
             0

        AUTHOR:
            -- David Harvey (2006-08-05)
        """
        output = {}

        for (index1, coeff1) in self.__coeffs.iteritems():
            for (index2, coeff2) in right.__coeffs.iteritems():
                product = coeff1 * coeff2
                index = index1 + index2
                if index in output:
                    output[index] += product
                else:
                    output[index] = product

        output = self.polynomial(output, check=False)
        output.__normalize()
        return output

    def shift(self, n):
        r"""
        Returns this polynomial multiplied by the power $x^n$. If $n$ is negative,
        terms below $x^n$ will be discarded. Does not change this polynomial.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ, sparse=True)
            sage: p = x^100000 + 2*x + 4
            sage: type(p)
            <class 'sage.rings.polynomial.polynomial_element_generic.Polynomial_generic_sparse'>
            sage: p.shift(0)
             x^100000 + 2*x + 4
            sage: p.shift(-1)
             x^99999 + 2
            sage: p.shift(-100002)
             0
            sage: p.shift(2)
             x^100002 + 2*x^3 + 4*x^2

        AUTHOR:
            -- David Harvey (2006-08-06)
        """
        n = int(n)
        if n == 0:
            return self
        if n > 0:
            output = {}
            for (index, coeff) in self.__coeffs.iteritems():
                output[index + n] = coeff
            return self.polynomial(output, check=False)
        if n < 0:
            output = {}
            for (index, coeff) in self.__coeffs.iteritems():
                if index + n >= 0:
                    output[index + n] = coeff
            return self.polynomial(output, check=False)


class Polynomial_generic_domain(Polynomial, IntegralDomainElement):
    def __init__(self, parent, is_gen=False, construct=False):
        Polynomial.__init__(self, parent, is_gen=is_gen)

    def is_unit(self):
        r"""
        Return True if this polynomial is a unit.

        EXERCISE (Atiyah-McDonald, Ch 1): Let $A[x]$ be a polynomial
        ring in one variable.  Then $f=\sum a_i x^i \in A[x]$ is a
        unit if and only if $a_0$ is a unit and $a_1,\ldots, a_n$ are
        nilpotent.

        EXAMPLES:
            sage: R.<z> = PolynomialRing(ZZ, sparse=True)
            sage: (2 + z^3).is_unit()
            False
            sage: f = -1 + 3*z^3; f
            3*z^3 - 1
            sage: f.is_unit()
            False
            sage: R(-3).is_unit()
            False
            sage: R(-1).is_unit()
            True
            sage: R(0).is_unit()
            False
        """
        if self.degree() > 0:
            return False
        return self[0].is_unit()

class Polynomial_generic_field(Polynomial_singular_repr,
                               Polynomial_generic_domain,
                               EuclideanDomainElement):

    def quo_rem(self, other):
        """
        Returns a tuple (quotient, remainder) where
            self = quotient*other + remainder.

        EXAMPLES:
            sage: R.<y> = PolynomialRing(QQ)
            sage: K.<t> = NumberField(y^2 - 2)
            sage: P.<x> = PolynomialRing(K)
            sage: x.quo_rem(K(1))
            (x, 0)
            sage: x.xgcd(K(1))
            (1, 0, 1)
        """
        other = self.parent()(other)
        if other.is_zero():
            raise ZeroDivisionError, "other must be nonzero"

        # This is algorithm 3.1.1 in Cohen GTM 138
        A = self
        B = other
        R = A
        Q = self.polynomial(0)
        X = self.parent().gen()
        while R.degree() >= B.degree():
            aaa = (R.leading_coefficient()/B.leading_coefficient())
            bbb = X**(R.degree()-B.degree())
            S =  (R.leading_coefficient()/B.leading_coefficient()) * X**(R.degree()-B.degree())
            Q += S
            R -= S*B
        return (Q, R)

    def _gcd(self, other):
        """
        Return the GCD of self and other, as a monic polynomial.
        """
        g = EuclideanDomainElement._gcd(self, other)
        c = g.leading_coefficient()
        if c.is_unit():
            return (1/c)*g
        return g


class Polynomial_generic_sparse_field(Polynomial_generic_sparse, Polynomial_generic_field):
    """
    EXAMPLES:
        sage: R.<x> = PolynomialRing(RR, sparse=True)
        sage: f = x^3 - x + 17
        sage: type(f)
        <class 'sage.rings.polynomial.polynomial_element_generic.Polynomial_generic_sparse_field'>
        sage: loads(f.dumps()) == f
        True
    """
    def __init__(self, parent, x=None, check=True, is_gen = False, construct=False):
        Polynomial_generic_sparse.__init__(self, parent, x, check, is_gen)


class Polynomial_generic_dense_field(Polynomial_generic_dense, Polynomial_generic_field):
    def __init__(self, parent, x=None, check=True, is_gen = False, construct=False):
        Polynomial_generic_dense.__init__(self, parent, x, check, is_gen)


class Polynomial_rational_dense(Polynomial_generic_field):
    """
    A dense polynomial over the rational numbers.
    """
    def __init__(self, parent, x=None, check=True, is_gen=False, construct=False):
        Polynomial.__init__(self, parent, is_gen=is_gen)

        if construct:
            self.__poly = x
            return

        self.__poly = pari([]).Polrev()

        if x is None:
            return         # leave initialized to 0 polynomial.


        if fraction_field_element.is_FractionFieldElement(x):
            if not x.denominator().is_unit():
                raise TypeError, "denominator must be a unit"
            elif x.denominator() != 1:
                x = x.numerator() * x.denominator().inverse_of_unit()
            else:
                x = x.numerator()

        if isinstance(x, Polynomial):
            if x.parent() == self.parent():
                self.__poly = x.__poly.copy()
                return
            else:
                x = [QQ(a) for a in x.list()]
                check = False

        elif isinstance(x, dict):
            x = self._dict_to_list(x, QQ(0))


        elif isinstance(x, pari_gen):
            f = x.Polrev()
            self.__poly = f
            assert self.__poly.type() == "t_POL"
            return

        elif not isinstance(x, list):
            x = [x]   # constant polynomials

        if check:
            x = [QQ(z) for z in x]

        self.__list = list(x)
        while len(self.__list) > 0 and not self.__list[-1]:
            del self.__list[-1]

        # NOTE: It is much faster to convert to string and let pari's parser at it,
        # which is why we pass str(x) in.
        self.__poly = pari(str(x)).Polrev()
        assert self.__poly.type() == "t_POL"

    def _repr(self, name=None):
        if name is None:
            name = self.parent().variable_name()
        return str(self.__poly).replace("x", name)

    def _repr_(self):
        return self._repr()

    def __reduce__(self):
        return Polynomial_rational_dense, \
               (self.parent(), self.list(), False, self.is_gen())

    def __getitem__(self, n):
        return QQ(self.__poly[n])

    def __getslice__(self, i, j):
        if i < 0:
            i = 0
        v = [QQ(x) for x in self.__poly[i:j]]
        P = self.parent()
        return P([0]*int(i) + v)

    def _pow(self, n):
        if self.degree() <= 0:
            return self.parent()(self[0]**n)
        if n < 0:
            return (~self)**(-n)
        return Polynomial_rational_dense(self.parent(), self.__poly**n, construct=True)

    def _add_(self, right):
        return Polynomial_rational_dense(self.parent(),
                                         self.__poly + right.__poly, construct=True)

    def is_irreducible(self):
        """
        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: (x^2 + 2).is_irreducible()
            True
            sage: (x^2 - 1).is_irreducible()
            False
        """
        try:
            return self.__poly.polisirreducible()
        except NotImplementedError:
            F = self.__poly.factor()
            if len(F) > 1 or F[0][1] > 1:
                return False
            return True

    def galois_group(self, pari_group=False, use_kash=False):
        r"""
        Return the Galois group of f as a permutation group.

        INPUT:
            self -- an irreducible polynomial

            pari_group -- bool (default: False); if True instead return
                          the Galois group as a PARI group.  This has
                          a useful label in it, and may be slightly faster
                          since it doesn't require looking up a group in
                          Gap.  To get a permutation group from a PARI
                          group P, type PermutationGroup(P).

            use_kash --   bool (default: False); if True use KASH's Galois
                          command instead of using the PARI C library.
                          An attempt is always made to use KASH if the
                          degree of the polynomial is >= 12.

        ALGORITHM: The Galois group is computed using PARI in C
        library mode, or possibly kash if available.

        \note{ The PARI documentation contains the following warning:
        The method used is that of resolvent polynomials and is
        sensitive to the current precision. The precision is updated
        internally but, in very rare cases, a wrong result may be
        returned if the initial precision was not sufficient.}

        EXAMPLES:
            sage: R.<x> = PolynomialRing(QQ)
            sage: f = x^4 - 17*x^3 - 2*x + 1
            sage: G = f.galois_group(); G            # uses optional database_gap package
            Transitive group number 5 of degree 4
            sage: G.gens()                           # uses optional database_gap package
            ((1,2,3,4), (1,2))
            sage: G.order()                          # uses optional database_gap package
            24

        It is potentially useful to instead obtain the corresponding
        PARI group, which is little more than a $4$-tuple.  See the
        PARI manual for the exact details.  (Note that the third
        entry in the tuple is in the new standard ordering.)
            sage: f = x^4 - 17*x^3 - 2*x + 1
            sage: G = f.galois_group(pari_group=True); G
            PARI group [24, -1, 5, "S4"] of degree 4
            sage: PermutationGroup(G)                # uses optional database_gap package
            Transitive group number 5 of degree 4

        You can use KASH to compute Galois groups as well.  The
        avantage is that KASH can compute Galois groups of fields up
        to degree 23, whereas PARI only goes to degree 11.  (In my
        not-so-thorough experiments PARI is faster than KASH.)

            sage: f = x^4 - 17*x^3 - 2*x + 1
            sage: f.galois_group(use_kash=true)      # requires optional KASH
            Transitive group number 5 of degree 4

        """
        from sage.groups.all import PariGroup, PermutationGroup, TransitiveGroup
        if not self.is_irreducible():
            raise ValueError, "polynomial must be irreducible"
        if self.degree() > 11 or use_kash:
            # TODO -- maybe use KASH if available or print message that user should install KASH?
            try:
                from sage.interfaces.all import kash
                kash.eval('X := PolynomialRing(RationalField()).1')
                s = self._repr(name='X')
                G = kash('Galois(%s)'%s)
                d = int(kash.eval('%s.ext1'%G.name()))
                n = int(kash.eval('%s.ext2'%G.name()))
                return TransitiveGroup(d, n)
            except RuntimeError:
                raise NotImplementedError, "Sorry, computation of Galois groups of fields of degree bigger than 11 is not yet implemented.  Try installing the optional free (closed source) KASH package, which supports up to degree $23$."
        G = self.__poly.polgalois()
        H = PariGroup(G, self.degree())
        if pari_group:
            return H
        else:
            return PermutationGroup(H)

    def quo_rem(self, right):
        """
        Returns a tuple (quotient, remainder) where
            self = quotient*right + remainder.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x^5 + 17*x + 3
            sage: g = x^3 - 19
            sage: q,r = f.quo_rem(g)
            sage: q*g + r
            x^5 + 17*x + 3
        """
        if not isinstance(right, Polynomial_rational_dense):
            right = self.parent()(right)
        if right.parent() != self.parent():
            raise TypeError
        v = self.__poly.divrem(right.__poly)
        return Polynomial_rational_dense(self.parent(), v[0], construct=True), \
               Polynomial_rational_dense(self.parent(), v[1], construct=True)


    def _mul_(self, right):
        """
        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: (x - QQ('2/3'))*(x^2 - 8*x + 16)
            x^3 - 26/3*x^2 + 64/3*x - 32/3
        """
        return self.parent()(self.__poly * right.__poly, construct=True)

    def _sub_(self, right):
        """
        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: x^5 + 17*x^3 + x+ 3 - (x^3 - 19)
            x^5 + 16*x^3 + x + 22
        """
        return self.parent()(self.__poly - right.__poly, construct=True)

    def _unsafe_mutate(self, n, value):
        try:
            del self.__list
        except AttributeError:
            pass
        n = int(n)
        if n < 0:
            raise IndexError, "n must be >= 0"
        if n <= self.__poly.poldegree():
            self.__poly[n] = QQ(value)
        else:
            self.__poly = self.__poly + pari('(%s)*x^%s'%(QQ(value),n))
        if hasattr(self, "__list"):
            del self.__list

    def complex_roots(self, flag=0):
        """
        Returns the complex roots of this polynomial.
        INPUT:
            flag -- optional, and can be
                    0: (default), uses Schonhage's method modified by Gourdon,
                    1: uses a modified Newton method.
        OUTPUT:
            list of complex roots of this polynomial, counted with multiplicities.

        NOTE: Calls the pari function polroots.

        EXAMPLE:
        We compute the roots of the characteristic polynomial of some Salem numbers:
            sage: R.<x> = PolynomialRing(QQ)
            sage: f = 1 - x^2 - x^3 - x^4 + x^6
            sage: f.complex_roots()[0]
            0.713639173536901
        """
        R = self.__poly.polroots(flag)
        C = complex_field.ComplexField()
        return [C(a) for a in R]

    def real_roots(self):
        """
        Returns isolating intervals for the real roots of this polynomial.

        EXAMPLE:
            sage: R.<x> = PolynomialRing(QQ)
            sage: f = (x - 1/2) * (x - 3/4) * (x - 3/2)
            sage: f.real_roots()
            [(879/2048, 4395/8192), (2637/4096, 6153/8192), (879/1024, 879/512)]
        """

        from sage.rings.polynomial.real_roots import real_roots

        return real_roots(self)

    def copy(self):
        """
        Return a copy of this polynomial.
        """
        f = Polynomial_rational_dense(self.parent())
        f.__poly = self.__poly.copy()
        return f

    def degree(self):
        """
        Return the degree of this polynomial.  The zero polynomial
        has degree -1.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: (x^5 + 17*x^3 + x+ 3).degree()
            5
            sage: R(0).degree()
            -1
            sage: type(x.degree())
            <type 'sage.rings.integer.Integer'>
        """
        return ZZ(max(self.__poly.poldegree(), -1))

    def discriminant(self):
        """
        EXAMPLES:
            sage: _.<x> = PolynomialRing(QQ)
            sage: f = x^3 + 3*x - 17
            sage: f.discriminant()
            -7911
        """
        return QQ(self.__poly.poldisc())

    def disc(self):
        """
        Same as discriminant().
        """
        return self.discriminant()

    def factor_mod(self, p):
        """
        Return the factorization of self modulo the prime p.

        INPUT:
            p -- prime

        OUTPUT:
            factorization of self reduced modulo p.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: (x^5 + 17*x^3 + x+ 3).factor_mod(3)
            x * (x^2 + 1)^2
            sage: (x^5 + 2).factor_mod(5)
            (x + 2)^5
        """
        import sage.rings.finite_field as finite_field
        p = integer.Integer(p)
        if not p.is_prime():
            raise ValueError, "p must be prime"
        G = self._pari_().factormod(p)
        K = finite_field.FiniteField(p)
        R = sage.rings.polynomial.polynomial_ring.PolynomialRing(K, names=self.parent().variable_name())
        return R(1)._factor_pari_helper(G, unit=R(self).leading_coefficient())

    def factor_padic(self, p, prec=10):
        """
        Return p-adic factorization of self to given precision.

        INPUT:
            p -- prime
            prec -- integer; the precision

        OUTPUT:
            factorization of self viewed as a polynomial over the p-adics

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x^3 - 2
            sage.: f.factor_padic(2)
            (1 + O(2^10))*x^3 + O(2^10)*x^2 + O(2^10)*x + (2 + 2^2 + 2^3 + 2^4 + 2^5 + 2^6 + 2^7 + 2^8 + 2^9 + O(2^10))
            sage.: f.factor_padic(3)
            (1 + O(3^10))*x^3 + O(3^10)*x^2 + O(3^10)*x + (1 + 2*3 + 2*3^2 + 2*3^3 + 2*3^4 + 2*3^5 + 2*3^6 + 2*3^7 + 2*3^8 + 2*3^9 + O(3^10))
            sage.: f.factor_padic(5)
            ((1 + O(5^10))*x + (2 + 4*5 + 2*5^2 + 2*5^3 + 5^4 + 3*5^5 + 4*5^7 + 2*5^8 + 5^9 + O(5^10))) * ((1 + O(5^10))*x^2 + (3 + 2*5^2 + 2*5^3 + 3*5^4 + 5^5 + 4*5^6 + 2*5^8 + 3*5^9 + O(5^10))*x + (4 + 5 + 2*5^2 + 4*5^3 + 4*5^4 + 3*5^5 + 3*5^6 + 4*5^7 + 4*5^9 + O(5^10)))
        """
        from sage.rings.padics.factory import Qp
        p = integer.Integer(p)
        if not p.is_prime():
            raise ValueError, "p must be prime"
        prec = integer.Integer(prec)
        if prec <= 0:
            raise ValueError, "prec must be positive"
        K = Qp(p, prec, type='capped-rel')
        R = sage.rings.polynomial.polynomial_ring.PolynomialRing(K, names=self.parent().variable_name())
        return R(self).factor(absprec = prec)

    def list(self):
        """
        Return a new copy of the list of the underlying
        elements of self.

        EXAMPLES:
            sage: _.<x> = PolynomialRing(QQ)
            sage: f = x^3 + 3*x - 17/13; f
            x^3 + 3*x - 17/13
            sage: v = f.list(); v
            [-17/13, 3, 0, 1]
            sage: v[0] = 0
            sage: f
            x^3 + 3*x - 17/13
            sage: f.list()
            [-17/13, 3, 0, 1]
        """
        return [QQ(x) for x in self.__poly.Vecrev()]

##     def partial_fraction(self, g):
##         """
##         Return partial fraction decomposition of self/g, where g
##         has the same parent as self.
##         """
##         g = self.parent()(g)
##         from sage.interfaces.maxima import maxima
##         h = maxima(self)/maxima(g)
##         k = h.partfrac(self.parent().variable())

    def rescale(self, a):
        """
        Return f(a*X).
        """
        b = 1
        c = []
        for i in range(self.degree()+1):
            c.append(b*self[i])
            b *= a
        return self.parent()(c)

    def hensel_lift(self, p, e):
        """
        Assuming that self factors modulo $p$ into distinct factors,
        computes the Hensel lifts of these factors modulo $p^e$.  We
        assume that $p$ has integer coefficients.
        """
        p = integer.Integer(p)
        if not p.is_prime():
            raise ValueError, "p must be prime"
        e = integer.Integer(e)
        if e < 1:
            raise ValueError, "e must be at least 1"
        F = self.factor_mod(p)
        y = []
        for g, n in F:
            if n > 1:
                raise ArithmeticError, "The polynomial must be square free modulo p."
            y.append(g)
        H = self._pari_().polhensellift(y, p, e)
        R = integer_mod_ring.IntegerModRing(p**e)
        S = sage.rings.polynomial.polynomial_ring.PolynomialRing(R, self.parent().variable_name())
        return [S(eval(str(m.Vec().Polrev().Vec()))) for m in H]

class Polynomial_padic_generic_dense(Polynomial_generic_dense, Polynomial_generic_domain):
    def __init__(self, parent, x=None, check=True, is_gen = False, construct=False, absprec=None):
        Polynomial_generic_dense.__init__(self, parent, x, check, is_gen, absprec=absprec)

    def _mul_(self, right):
        return self._mul_generic(right)

    def __pow__(self, right):
        #computing f^p in this way loses precision
        return self._pow(right)

    def clear_zeros(self):
        """
        This function replaces coefficients of the polynomial that evaluate as equal to 0 with the zero element of the base ring that has the maximum possible precision.

        WARNING: this function mutates the underlying polynomial.
        """
        coeffs = self._Polynomial_generic_dense__coeffs
        for n in range(len(coeffs)):
            if not coeffs[n]:
                self._Polynomial_generic_dense__coeffs[n] = self.base_ring()(0)

    def _repr(self, name=None):
        r"""
        EXAMPLES:
            sage: R.<w> = PolynomialRing(Zp(5, prec=5, type = 'capped-abs', print_mode = 'val-unit'))
            sage: f = 24 + R(4/3)*w + w^4
            sage: f._repr()
            '(1 + O(5^5))*w^4 + (1043 + O(5^5))*w + (24 + O(5^5))'
            sage: f._repr(name='z')
            '(1 + O(5^5))*z^4 + (1043 + O(5^5))*z + (24 + O(5^5))'

        AUTHOR:
            -- David Roe (2007-03-03), based on Polynomial_generic_dense._repr()
        """
        s = " "
        n = m = self.degree()
        if name is None:
            name = self.parent().variable_name()
        atomic_repr = self.parent().base_ring().is_atomic_repr()
        coeffs = self.list()
        for x in reversed(coeffs):
            if x.valuation() != infinity:
                if n != m:
                    s += " + "
                x = repr(x)
                x = "(%s)"%x
                if n > 1:
                    var = "*%s^%s"%(name,n)
                elif n==1:
                    var = "*%s"%name
                else:
                    var = ""
                s += "%s%s"%(x,var)
            n -= 1
        if s==" ":
            return "0"
        return s[1:]


    def factor(self, absprec = None):
        if self == 0:
            raise ValueError, "Factorization of 0 not defined"
        if absprec is None:
            absprec = min([x.precision_absolute() for x in self.list()])
        else:
            absprec = integer.Integer(absprec)
        if absprec <= 0:
            raise ValueError, "absprec must be positive"
        G = self._pari_().factorpadic(self.base_ring().prime(), absprec)
        pols = G[0]
        exps = G[1]
        F = []
        R = self.parent()
        for i in xrange(len(pols)):
            f = R(pols[i], absprec = absprec)
            e = int(exps[i])
            F.append((f,e))

        if R.base_ring().is_field():
            # When the base ring is a field we normalize
            # the irreducible factors so they have leading
            # coefficient 1.
            for i in range(len(F)):
                cur = F[i][0].leading_coefficient()
                if cur != 1:
                    F[i] = (F[i][0].monic(), F[i][1])
            return Factorization(F, self.leading_coefficient())
        else:
            # When the base ring is not a field, we normalize
            # the irreducible factors so that the leading term
            # is a power of p.  We also ensure that the gcd of
            # the coefficients of each term is 1.
            c = self.leading_coefficient().valuation()
            u = self.base_ring()(1)
            for i in range(len(F)):
                upart = F[i][0].leading_coefficient().unit_part()
                lval = F[i][0].leading_coefficient().valuation()
                if upart != 1:
                    F[i] = (F[i][0] // upart, F[i][1])
                    u *= upart ** F[i][1]
                c -= lval
            if c != 0:
                F.append((self.parent()(self.base_ring().prime_pow(c)), 1))
            return Factorization(F, u)

class Polynomial_padic_ring_dense(Polynomial_padic_generic_dense):
    def content(self):
        if self == 0:
            return self.base_ring()(0)
        else:
            return self.base_ring()(self.base_ring().prime_pow(min([x.valuation() for x in self.list()])))

class Polynomial_padic_field_dense(Polynomial_padic_generic_dense, Polynomial_generic_dense_field):
    def content(self):
        if self != 0:
            return self.base_ring()(1)
        else:
            return self.base_ring()(0)

    def _xgcd(self, other):
        H = Polynomial_generic_dense_field._xgcd(self, other)
        c = ~H[0].leading_coefficient()
        return c * H[0], c * H[1], c * H[2]


class Polynomial_padic_ring_lazy_dense(Polynomial_padic_ring_dense):
    pass

class Polynomial_padic_field_lazy_dense(Polynomial_padic_field_dense):
    pass

class Polynomial_dense_mod_n(Polynomial):
    """
    A dense polynomial over the integers modulo n, where n is composite.

    Much of the underlying arithmetic is done using NTL.

    EXAMPLES:

        sage: R.<x> = PolynomialRing(Integers(16))
        sage: f = x^3 - x + 17
        sage: f^2
        x^6 + 14*x^4 + 2*x^3 + x^2 + 14*x + 1

        sage: loads(f.dumps()) == f
        True

        sage: R.<x> = Integers(100)[]
        sage: p = 3*x
        sage: q = 7*x
        sage: p+q
        10*x
        sage: R.<x> = Integers(8)[]
        sage: parent(p)
        Univariate Polynomial Ring in x over Ring of integers modulo 100
        sage: p + q
        10*x

    """
    def __init__(self, parent, x=None, check=True,
                 is_gen=False, construct=False):
        Polynomial.__init__(self, parent, is_gen=is_gen)

        if construct:
            if isinstance(x, ZZ_pX):
                self.__poly = x
                return
            self.__poly = ZZ_pX(x, parent.modulus())
            return

        self.__poly = ZZ_pX([], parent.modulus())

        if x is None:
            return         # leave initialized to 0 polynomial.

        if isinstance(x, Polynomial):
            if x.parent() == self.parent():
                self.__poly = x.__poly.__copy__()
                return
            else:
                R = parent.base_ring()
                x = [ZZ(R(a)) for a in x.list()]
                check = False

        elif isinstance(x, dict):
            x = self._dict_to_list(x, R(0))


        elif isinstance(x, ZZX):
            self.__poly = x.copy()
            return

        elif isinstance(x, pari_gen):
            x = [ZZ(w) for w in x.Vecrev()]
            check = False

        elif isinstance(x, fraction_field_element.FractionFieldElement) and \
                 isinstance(x.numerator(), Polynomial_dense_mod_n):
            if x.denominator() == 1:
                x = x.numerator().__poly
                check = False

        elif not isinstance(x, list):
            x = [x]   # constant polynomials

        if check:
            R = parent.base_ring()
            x = [ZZ(R(a)) for a in x]

        self.__poly = ZZ_pX(x, parent.modulus())

    def _ntl_set_modulus(self):
        self.parent()._ntl_set_modulus()

    def __reduce__(self):
        return Polynomial_dense_mod_n, \
               (self.parent(), self.list(), False, self.is_gen())

    def int_list(self):
        return eval(str(self.__poly).replace(' ',','))

    def _pari_(self, variable=None):
        """
        EXAMPLES:
            sage: t = PolynomialRing(IntegerModRing(17),"t").gen()
            sage: f = t^3 + 3*t - 17
            sage: pari(f)
            Mod(1, 17)*t^3 + Mod(3, 17)*t
        """
        if variable is None:
            variable = self.parent().variable_name()
        return pari(self.int_list()).Polrev(variable) * \
               pari(1).Mod(self.parent().base_ring().order())

    def ntl_ZZ_pX(self):
        r"""
        Return underlying NTL representation of this polynomial.
        Additional ``bonus'' functionality is available through this
        function.

        WARNING:
        You must call \code{ntl.set_modulus(ntl.ZZ(n))} before doing
        arithmetic with this object!
        """
        return self.__poly

    def __getitem__(self, n):
        return self.parent().base_ring()(self.__poly[n]._sage_())

    def __getslice__(self, i, j):
        R = self.base_ring()
        if i < 0:
            i = 0
        if j > self.__poly.degree()+1:
            j = self.__poly.degree()+1
        v = [R(self.__poly[k]._sage_()) for k in range(i,j)]
        return self.parent()([0]*int(i) + v)

    def _unsafe_mutate(self, n, value):
        n = int(n)
        if n < 0:
            raise IndexError, "n must be >= 0"
        self._ntl_set_modulus()
        self.__poly[n] = int(value)

    def _pow(self, n):
        n = int(n)
        self._ntl_set_modulus()
        if self.degree() <= 0:
            return self.parent()(self[0]**n)
        if n < 0:
            return (~self)**(-n)
        return self.parent()(self.__poly**n, construct=True)

    def _add_(self, right):
        self._ntl_set_modulus()
        return self.parent()(self.__poly + right.__poly, construct=True)

    def _mul_(self, right):
        """
        EXAMPLES:
            sage: x = PolynomialRing(Integers(100), 'x').0
            sage: (x - 2)*(x^2 - 8*x + 16)
            x^3 + 90*x^2 + 32*x + 68
        """
        self._ntl_set_modulus()
        return self.parent()(self.__poly * right.__poly, construct=True)

    def _rmul_(self, c):
        try:
            self._ntl_set_modulus()
            return self.parent()(ZZ_pX([c], self.parent().modulus()) * self.__poly, construct=True)
        except RuntimeError, msg: # should this realy be a TypeError
            raise TypeError, msg

    def _lmul_(self, c):
        try:
            self._ntl_set_modulus()
            return self.parent()(ZZ_pX([c], self.parent().modulus()) * self.__poly, construct=True)
        except RuntimeError, msg: # should this realy be a TypeError
            raise TypeError, msg

    def quo_rem(self, right):
        """
        Returns a tuple (quotient, remainder) where
            self = quotient*other + remainder.
        """
        if not isinstance(right, Polynomial_dense_mod_n):
            right = self.parent()(right)
        elif self.parent() != right.parent():
            raise TypeError
        self._ntl_set_modulus()
        v = self.__poly.quo_rem(right.__poly)
        P = self.parent()
        return (P(v[0], construct=True), P(v[1], construct=True) )

    def shift(self, n):
        r"""
        Returns this polynomial multiplied by the power $x^n$. If $n$ is negative,
        terms below $x^n$ will be discarded. Does not change this polynomial.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(Integers(12345678901234567890))
            sage: p = x^2 + 2*x + 4
            sage: p.shift(0)
             x^2 + 2*x + 4
            sage: p.shift(-1)
             x + 2
            sage: p.shift(-5)
             0
            sage: p.shift(2)
             x^4 + 2*x^3 + 4*x^2

        AUTHOR:
            -- David Harvey (2006-08-06)
        """
        if n == 0:
            return self
        self._ntl_set_modulus()
        return self.parent()(self.__poly.left_shift(n),
                             construct=True)

    def _sub_(self, right):
        self._ntl_set_modulus()
        return self.parent()(self.__poly - right.__poly, construct=True)

    def __floordiv__(self, right):
        if is_Polynomial(right) and right.is_constant() and \
                         right[0] in self.parent().base_ring():
            d = right[0]
        elif (right in self.parent().base_ring()):
            d = right
        else:
            return Polynomial.__floordiv__(self, right)
        return self.parent()([c // d for c in self.list()], construct=True)

##     def __copy__(self):
##         self.parent()._ntl_set_modulus()
##         f = self.parent()()
##         f.__poly = self.__poly.copy()
##         return f

    def degree(self):
        """
        Return the degree of this polynomial.  The zero polynomial
        has degree -1.
        """
        return max(self.__poly.degree(), -1)

    def is_irreducible(self):
        return bool(self._pari_().polisirreducible())

    def list(self):
        """
        Return a new copy of the list of the underlying
        elements of self.

        EXAMPLES:
            sage: _.<x> = Integers(100)[]
            sage: f = x^3 + 3*x - 17
            sage: f.list()
            [83, 3, 0, 1]
        """
        R = self.base_ring()
        return [R(x) for x in self.int_list()]

    def ntl_set_directly(self, v):
        r"""
        Set the value of this polynomial directly from a vector or string.

        Polynomials over the integers modulo n are stored internally
        using NTL's ZZ_pX class.  Use this function to set the value
        of this polynomial using the NTL constructor, which is
        potentially \emph{very} fast.  The input v is either a vector
        of ints or a string of the form '[ n1 n2 n3 ... ]' where the
        ni are integers and there are no commas between them.  The
        optimal input format is the string format, since that's what
        NTL uses by default.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(Integers(100))
            sage: R([1,-2,3])
            3*x^2 + 98*x + 1
            sage: f = R(0)
            sage: f.ntl_set_directly([1,-2,3])
            sage: f
            3*x^2 + 98*x + 1
            sage: f.ntl_set_directly('[1 -2 3 4]')
            sage: f
            4*x^3 + 3*x^2 + 98*x + 1
        """
        if self.is_gen():
            raise TypeError, "Cannot change the value of the generator."
        self._ntl_set_modulus()
        self.__poly = ZZ_pX(v, self.parent().modulus())
        try:
            del self.__list
        except AttributeError:
            pass


class Polynomial_dense_mod_p(Polynomial_dense_mod_n,
                             Polynomial_singular_repr,
                             PrincipalIdealDomainElement):
    """
    A dense polynomial over the integers modulo p, where p is prime.
    """
    def __reduce__(self):
        return Polynomial_dense_mod_p, \
               (self.parent(), self.list(), False, self.is_gen())

    def _gcd(self, right):
        """
        Return the GCD of self and other, as a monic polynomial.
        """
        if not isinstance(right, Polynomial_dense_mod_p):
            right = self.parent()(right)
        elif self.parent() != right.parent():
            raise TypeError
        g = self.ntl_ZZ_pX().gcd(right.ntl_ZZ_pX())
        return self.parent()(g, construct=True)

    def _xgcd(self, right):
        """
        Return $g, u, v$ such that \code{g = u*self + v*right}.
        """
        r, s, t = self.ntl_ZZ_pX().xgcd(right.ntl_ZZ_pX())
        return self.parent()(r, construct=True), self.parent()(s, construct=True), \
               self.parent()(t, construct=True)

    def resultant(self, other):
        """
        Returns the resultant of self and other, which must lie in the same
        polynomial ring.

        INPUT:
            other -- a polynomial
        OUTPUT:
            an element of the base ring of the polynomial ring

        EXAMPLES:
            sage: R.<x> = GF(19)['x']
            sage: f = x^3 + x + 1;  g = x^3 - x - 1
            sage: r = f.resultant(g); r
            11
            sage: r.parent() is GF(19)
            True
        """
        self.parent()._ntl_set_modulus()
        other = self.parent()._coerce_(other)
        return self.base_ring()(str(self.ntl_ZZ_pX().resultant(other.ntl_ZZ_pX())))

    def discriminant(self):
        """
        EXAMPLES:
            sage: _.<x> = PolynomialRing(GF(19))
            sage: f = x^3 + 3*x - 17
            sage: f.discriminant()
            12
        """
        self.parent()._ntl_set_modulus()
        return self.base_ring()(str(self.ntl_ZZ_pX().discriminant()))

    # PARI is way better than NTL for poly factor for certain degrees, and is called
    # by default in the base class.
    #def factor(self, verbose=False):
    #    M = self.monic()
    #    self.parent()._ntl_set_modulus()
    #    F = [(self.parent()(f, construct=True), n) for f, n in M.ntl_ZZ_pX().factor(verbose)]
    #    return factorization.Factorization(F)
