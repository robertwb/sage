"""
Quotients of Univariate Polynomial Rings

EXAMPLES:
    sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
    sage: S = R.quotient(x**3-3*x+1, 'alpha')
    sage: S.gen()**2 in S
    True
    sage: x in S
    True
    sage: S.gen() in R
    False
    sage: 1 in S
    True
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@ucsd.edu>
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

import number_field.all
import polynomial_element
import polynomial_ring
import rational_field

import commutative_ring
import field
import integral_domain

import polynomial_quotient_ring_element

def PolynomialQuotientRing(ring, polynomial, name=None):
    r"""
    Create a quotient of a polynomial ring.

    INPUT:
        ring -- a univariate polynomial ring in one variable.
        polynomial -- element
        name -- (optional) name for the variable

    OUTPUT:
        Creates the quotient ring R/I, where R is the ring and I is
        the principal ideal generated by the polynomial.

    EXAMPLES:

    We create the quotient ring $\Z[x]/(x^3+7)$, and demonstrate many
    basic functions with it:

        sage: Z = IntegerRing()
        sage: R = PolynomialRing(Z,'x'); x = R.gen()
        sage: S = R.quotient(x^3 + 7, 'a'); a = S.gen()
        sage: S
        Univariate Quotient Polynomial Ring in a over Integer Ring with modulus x^3 + 7
        sage: a^3
        -7
        sage: S.is_field()
        False
        sage: a in S
        True
        sage: x in S
        True
        sage: a in R
        False
        sage: S.polynomial_ring()
        Univariate Polynomial Ring in x over Integer Ring
        sage: S.modulus()
        x^3 + 7
        sage: S.degree()
        3

    We create the ``iterated'' polynomial ring quotient
    $$
           R = (\F_2[y]/(y^{2}+y+1))[x]/(x^3 - 5).
    $$

        sage: A = PolynomialRing(GF(2),'y'); y=A.gen(); print A
        Univariate Polynomial Ring in y over Finite Field of size 2
        sage: B = A.quotient(y^2 + y + 1, 'y2'); print B
        Univariate Quotient Polynomial Ring in y2 over Finite Field of size 2 with modulus y^2 + y + 1
        sage: C = PolynomialRing(B, 'x'); x=C.gen(); print C
        Univariate Polynomial Ring in x over Univariate Quotient Polynomial Ring in y2 over Finite Field of size 2 with modulus y^2 + y + 1
        sage: R = C.quotient(x^3 - 5); print R
        Univariate Quotient Polynomial Ring in x over Univariate Quotient Polynomial Ring in y2 over Finite Field of size 2 with modulus y^2 + y + 1 with modulus x^3 + 1


    Next we create a number field, but viewed as a quotient of a
    polynomial ring over $\Q$:
        sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
        sage: S = R.quotient(x^3 + 2*x - 5, 'a')
        sage: S
        Univariate Quotient Polynomial Ring in a over Rational Field with modulus x^3 + 2*x - 5
        sage: S.is_field()
        True
        sage: S.degree()
        3

    There are conversion functions for easily going back and forth
    between quotients of polynomial rings over $\Q$ and number
    fields:
        sage: K = S.number_field(); K
        Number Field in a with defining polynomial x^3 + 2*x - 5
        sage: K.polynomial_quotient_ring()
        Univariate Quotient Polynomial Ring in a over Rational Field with modulus x^3 + 2*x - 5

    The leading coefficient must be a unit (but need not be 1).
        sage: R = PolynomialRing(Integers(9), 'x'); x = R.gen()
        sage: S = R.quotient(2*x^4 + 2*x^3 + x + 2, 'a')
        sage: S = R.quotient(3*x^4 + 2*x^3 + x + 2, 'a')
        Traceback (most recent call last):
        ...
        TypeError: polynomial (=3*x^4 + 2*x^3 + x + 2) must have unit leading coefficient

    Another example:
        sage: R, x = PolynomialRing(IntegerRing()).objgen()
        sage: f = x^2 + 1
        sage: R.quotient(f)
        Univariate Quotient Polynomial Ring in x over Integer Ring with modulus x^2 + 1
    """
    if not isinstance(ring, polynomial_ring.PolynomialRing_generic):
        raise TypeError, "ring (=%s) must be a polynomial ring"%ring
    if not isinstance(polynomial, polynomial_element.Polynomial):
        raise TypeError, "polynomial (=%s) must be a polynomial"%polynomial
    if not polynomial.parent() == ring:
        raise TypeError, "polynomial (=%s) must be in ring (=%s)%"%(polynomial,ring)
    c = polynomial.leading_coefficient()
    if not c.is_unit():
        raise TypeError, "polynomial (=%s) must have unit leading coefficient"%polynomial
    R = ring.base_ring()
    if isinstance(R, integral_domain.IntegralDomain):
        try:
            if polynomial.is_irreducible():
                if isinstance(R, field.Field):
                    return PolynomialQuotientRing_field(ring, polynomial, name)
                else:
                    return PolynomialQuotientRing_domain(ring, polynomial, name)
        except NotImplementedError:   # is_irreducible sometimes not implemented
            pass
    return PolynomialQuotientRing_generic(ring, polynomial, name)


def is_PolynomialQuotientRing(x):
    return isinstance(x, PolynomialQuotientRing_generic)


class PolynomialQuotientRing_generic(commutative_ring.CommutativeRing):
    """
    Quotient of a univariate polynomial ring by an ideal.

    EXAMPLES:
        sage: R, x = PolynomialRing(Integers(8)).objgen(); R
        Univariate Polynomial Ring in x over Ring of integers modulo 8
        sage: S, xbar = R.quotient(x^2 + 1, 'xbar').objgen(); S
        Univariate Quotient Polynomial Ring in xbar over Ring of integers modulo 8 with modulus x^2 + 1

    We demonstrate object persistence.
        sage: loads(S.dumps()) == S
        True
        sage: loads(xbar.dumps()) == xbar
        True

    We create some sample homomorphisms;
        sage: R, x = PolynomialRing(ZZ).objgen()
        sage: S = R/(x^2-4)
        sage: f = S.hom([2])
        sage: f
        Ring morphism:
          From: Univariate Quotient Polynomial Ring in x over Integer Ring with modulus x^2 - 4
          To:   Integer Ring
          Defn: x |--> 2
        sage: f(x)
        2
        sage: f(x^2 - 4)
        0
        sage: f(x^2)
        4
    """
    def __init__(self, ring, polynomial, name=None):
        if not isinstance(ring, polynomial_ring.PolynomialRing_generic):
            raise TypeError, "R must be a univariate polynomial ring."

        if not isinstance(polynomial, polynomial_element.Polynomial):
            raise TypeError, "f must be a Polynomial"

        if polynomial.parent() != ring:
            raise TypeError, "f must have parent R"

        self.__ring = ring
        self.__polynomial = polynomial
        self.assign_names(name)

    def __reduce__(self):
        return PolynomialQuotientRing_generic, (self.__ring, self.__polynomial, self.variable_names())

    def __call__(self, x):
        """
        Coerce x into this quotient ring.  Anything that can be
        coerced into the polynomial ring can be coerced into the
        quotient.

        INPUT:
            x -- object to be coerced

        OUTPUT:
            an element obtained by coercing x into this ring.

        EXAMPLES:
            sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
            sage: S = R.quotient(x^3-3*x+1, 'alpha')
            sage: S(x)
            alpha
            sage: S(x^3)
            3*alpha - 1
            sage: S([1,2])
            2*alpha + 1
            sage: S([1,2,3,4,5])
            18*alpha^2 + 9*alpha - 3
            sage: S(S.gen()+1)
            alpha + 1
            sage: S(S.gen()^10+1)
            90*alpha^2 - 109*alpha + 28
        """
        if isinstance(x, polynomial_quotient_ring_element.PolynomialQuotientRingElement):
            if x.parent() == self:
                return x
        return polynomial_quotient_ring_element.PolynomialQuotientRingElement(
                        self, self.__ring(x) , check=True)

    def _is_valid_homomorphism_(self, codomain, im_gens):
        try:
            # We need that elements of the base ring of the polynomial
            # ring map canonically into codomain.

            codomain._coerce_(self.base_ring()(1))

            # We also need that the polynomial modulus maps to 0.
            f = self.modulus()
            return codomain(f(im_gens[0])) == 0
        except TypeError, ValueError:
            return False

    def _coerce_(self, x):
        if isinstance(x, polynomial_quotient_ring_element.PolynomialQuotientRingElement):
            if x.parent() == self:
                return x
        if x in self.__ring:
            return polynomial_quotient_ring_element.PolynomialQuotientRingElement(
                self, self.__ring(x) , check=True)
        raise TypeError

    def __cmp__(self, other):
        """
        Compare self and other.

        EXAMPLES:
            sage: Rx = PolynomialRing(RationalField(), 'x'); x = Rx.gen()
            sage: Ry = PolynomialRing(RationalField(), 'y'); y = Ry.gen()
            sage: Rx == Ry
            False
            sage: Qx = Rx.quotient(x^2+1)
            sage: Qy = Ry.quotient(y^2+1)
            sage: Qx == Qy
            False
            sage: Qx == Qx
            True
            sage: Qz = Rx.quotient(x^2+1)
            sage: Qz == Qx
            True
        """
        if not isinstance(other, PolynomialQuotientRing_generic):
            return -1
        if self.polynomial_ring() != other.polynomial_ring():
            return -1
        return self.modulus().__cmp__(other.modulus())


    def __repr__(self):
        return "Univariate Quotient Polynomial Ring in %s over %s with modulus %s"%(
            self.variable_name(), self.base_ring(), self.modulus())


    def base_ring(self):
        r"""
        Return the base base ring of the polynomial ring, of which
        this ring is a quotient.

        EXAMPLES:
        The base ring of $\Z[z]/(z^3 + z^2 + z + 1)$ is $\Z$.
            sage: R = PolynomialRing(IntegerRing(), 'z'); z = R.gen()
            sage: S = R.quotient(z^3 + z^2 + z + 1, 'beta')
            sage: S.base_ring()
            Integer Ring

        Next we make a polynomial quotient ring over $S$ and ask for its basering.
            sage: T = PolynomialRing(S); W = T.quotient(T.gen()^99 + 99)
            sage: W.base_ring()
            Univariate Quotient Polynomial Ring in beta over Integer Ring with modulus z^3 + z^2 + z + 1
        """
        return self.__ring.base_ring()

    def characteristic(self):
        """
        Return the characteristic of this quotient ring.

        This is always the same as the characteristic of the base ring.

        EXAMPLES:
            sage: R = PolynomialRing(IntegerRing(), 'z'); z = R.gen()
            sage: S = R.quotient(z - 19, 'a')
            sage: S.characteristic()
            0
            sage: R = PolynomialRing(GF(9), 'x'); x = R.gen()
            sage: S = R.quotient(x^3 + 1)
            sage: S.characteristic()
            3
        """
        return self.base_ring().characteristic()

    def degree(self):
        """
        Return the degree of this quotient ring.  The degree is the
        degree of the polynomial that we quotiented out by.

        EXAMPLES:
            sage: R = PolynomialRing(GF(3), 'x'); x = R.gen()
            sage: S = R.quotient(x^2005 + 1)
            sage: S.degree()
            2005
        """
        return self.modulus().degree()

    def discriminant(self, v=None):
        """
        Return the discriminant of this ring over the base ring.  This
        is by definition the discriminant of the polynomial that we
        quotiented out by.

        EXAMPLES:
            sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
            sage: S = R.quotient(x^3 + x^2 + x + 1)
            sage: S.discriminant()
            -16
            sage: S = R.quotient((x + 1) * (x + 1))
            sage: S.discriminant()
            0

        The discriminant of the quotient polynomial ring need not
        equal the discriminant of the corresponding number field,
        since the discriminant of a number field is by definition the
        discriminant of the ring ring of integers of the number field:
            sage: S = R.quotient(x^2 - 8)
            sage: S.number_field().discriminant()
            8
            sage: S.discriminant()
            32
        """
        return self.modulus().discriminant()

    def gen(self, n=0):
        """
        Return the generator of this quotient ring.  This is the
        equivalence class of the image of the generator of the
        polynomial ring.

        EXAMPLES:
            sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
            sage: S = R.quotient(x^2 - 8, 'gamma')
            sage: S.gen()
            gamma
        """
        if n != 0:
            raise IndexError, "Only one generator."
        try:
            return self.__gen
        except AttributeError:
            self.__gen = self(self.polynomial_ring().gen())
            return self.__gen

    def is_field(self):
        """
        Return whether or not this quotient ring is a field.

        EXAMPLES:
            sage: R = PolynomialRing(IntegerRing(), 'z'); z = R.gen()
            sage: S = R.quotient(z^2-2)
            sage: S.is_field()
            False
            sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
            sage: S = R.quotient(x^2 - 2)
            sage: S.is_field()
            True
        """
        return self.base_ring().is_field() and self.modulus().is_irreducible()

    def krull_dimension(self):
        return self.base_ring().krull_dimension()

    def modulus(self):
        """
        Return the polynomial modulus of this quotient ring.

        EXAMPLES:
            sage: R = PolynomialRing(GF(3), 'x'); x = R.gen()
            sage: S = R.quotient(x^2 - 2)
            sage: S.modulus()
            x^2 + 1
        """
        return self.__polynomial

    def ngens(self):
        """
        Return the number of generators of this quotient ring over the
        base ring.  This function always returns 1.

        EXAMPLES:
            sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
            sage: S = PolynomialRing(R, 'y'); y = S.gen()
            sage: T = S.quotient(y + x, 'z')
            sage: T
            Univariate Quotient Polynomial Ring in z over Univariate Polynomial Ring in x over Rational Field with modulus y + x
            sage: T.ngens()
            1
        """
        return 1

    def number_field(self):
        """
        Return the number field isomorphic to this quotient polynomial
        ring, if possible.

        EXAMPLES:
            sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
            sage: S = R.quotient(x^29 - 17*x - 1, 'alpha')
            sage: K = S.number_field()
            sage: K
            Number Field in alpha with defining polynomial x^29 - 17*x - 1
            sage: alpha = K.gen()
            sage: alpha^29
            17*alpha + 1
        """
        if self.characteristic() != 0:
            raise ArithmeticError, "Polynomial quotient ring is not isomorphic to a number field (it has positive characteristic)."

        if not isinstance(self.base_ring(), rational_field.RationalField):
            raise NotImplementedError, "Computation of number field only implemented for quotients of the polynomial ring over the rational field."
        return number_field.all.NumberField(self.modulus(), self.variable_name())

    def polynomial_ring(self):
        """
        Return the polynomial ring of which this ring is the quotient.

        EXAMPLES:
            sage: R = PolynomialRing(RationalField(), 'x'); x = R.gen()
            sage: S = R.quotient(x^2-2)
            sage: S.polynomial_ring()
            Univariate Polynomial Ring in x over Rational Field
        """
        return self.__ring


class PolynomialQuotientRing_domain(PolynomialQuotientRing_generic, integral_domain.IntegralDomain):
    """
    EXAMPLES:
        sage: R, x = PolynomialRing(ZZ).objgen()
        sage: S, xbar = R.quotient(x^2 + 1, 'xbar').objgen()
        sage: S
        Univariate Quotient Polynomial Ring in xbar over Integer Ring with modulus x^2 + 1
        sage: loads(S.dumps()) == S
        True
        sage: loads(xbar.dumps()) == xbar
        True
    """
    def __init__(self, ring, polynomial, name=None):
        PolynomialQuotientRing_generic.__init__(self, ring, polynomial, name)

    def __reduce__(self):
        return PolynomialQuotientRing_domain, (self.polynomial_ring(),
                                         self.modulus(), self.variable_names())


class PolynomialQuotientRing_field(PolynomialQuotientRing_domain, field.Field):
    """
    EXAMPLES:
        sage: R.<x> = PolynomialRing(QQ)
        sage: S.<xbar> = R.quotient(x^2 + 1)
        sage: S
        Univariate Quotient Polynomial Ring in xbar over Rational Field with modulus x^2 + 1
        sage: loads(S.dumps()) == S
        True
        sage: loads(xbar.dumps()) == xbar
        True
    """
    def __init__(self, ring, polynomial, name=None):
        PolynomialQuotientRing_domain.__init__(self, ring, polynomial, name)

    def __reduce__(self):
        return PolynomialQuotientRing_field, (self.polynomial_ring(),
                                        self.modulus(), self.variable_names())
