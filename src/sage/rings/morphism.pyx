r"""
Homomorphisms of rings

We give a large number of examples of ring homomorphisms.

EXAMPLE: Natural inclusion
`\ZZ \hookrightarrow \QQ`.

::

    sage: H = Hom(ZZ, QQ)
    sage: phi = H([1])
    sage: phi(10)
    10
    sage: phi(3/1)
    3
    sage: phi(2/3)
    Traceback (most recent call last):
    ...
    TypeError: 2/3 fails to convert into the map's domain Integer Ring, but a `pushforward` method is not properly implemented

There is no homomorphism in the other direction::

    sage: H = Hom(QQ, ZZ)
    sage: H([1])
    Traceback (most recent call last):
    ...
    TypeError: images do not define a valid homomorphism

EXAMPLE: Reduction to finite field.

::

    sage: H = Hom(ZZ, GF(9, 'a'))
    sage: phi = H([1])
    sage: phi(5)
    2
    sage: psi = H([4])
    sage: psi(5)
    2

EXAMPLE: Map from single variable polynomial ring.

::

    sage: R, x = PolynomialRing(ZZ, 'x').objgen()
    sage: phi = R.hom([2], GF(5))
    sage: phi
    Ring morphism:
      From: Univariate Polynomial Ring in x over Integer Ring
      To:   Finite Field of size 5
      Defn: x |--> 2
    sage: phi(x + 12)
    4

EXAMPLE: Identity map on the real numbers.

::

    sage: f = RR.hom([RR(1)]); f
    Ring endomorphism of Real Field with 53 bits of precision
      Defn: 1.00000000000000 |--> 1.00000000000000
    sage: f(2.5)
    2.50000000000000
    sage: f = RR.hom( [2.0] )
    Traceback (most recent call last):
    ...
    TypeError: images do not define a valid homomorphism

EXAMPLE: Homomorphism from one precision of field to another.

From smaller to bigger doesn't make sense::

    sage: R200 = RealField(200)
    sage: f = RR.hom( R200 )
    Traceback (most recent call last):
    ...
    TypeError: Natural coercion morphism from Real Field with 53 bits of precision to Real Field with 200 bits of precision not defined.

From bigger to small does::

    sage: f = RR.hom( RealField(15) )
    sage: f(2.5)
    2.500
    sage: f(RR.pi())
    3.142

EXAMPLE: Inclusion map from the reals to the complexes::

    sage: i = RR.hom([CC(1)]); i
    Ring morphism:
      From: Real Field with 53 bits of precision
      To:   Complex Field with 53 bits of precision
      Defn: 1.00000000000000 |--> 1.00000000000000
    sage: i(RR('3.1'))
    3.10000000000000

EXAMPLE: A map from a multivariate polynomial ring to itself::

    sage: R.<x,y,z> = PolynomialRing(QQ,3)
    sage: phi = R.hom([y,z,x^2]); phi
    Ring endomorphism of Multivariate Polynomial Ring in x, y, z over Rational Field
      Defn: x |--> y
            y |--> z
            z |--> x^2
    sage: phi(x+y+z)
    x^2 + y + z

EXAMPLE: An endomorphism of a quotient of a multi-variate
polynomial ring::

    sage: R.<x,y> = PolynomialRing(QQ)
    sage: S.<a,b> = quo(R, ideal(1 + y^2))
    sage: phi = S.hom([a^2, -b])
    sage: phi
    Ring endomorphism of Quotient of Multivariate Polynomial Ring in x, y over Rational Field by the ideal (y^2 + 1)
      Defn: a |--> a^2
            b |--> -b
    sage: phi(b)
    -b
    sage: phi(a^2 + b^2)
    a^4 - 1

EXAMPLE: The reduction map from the integers to the integers modulo
8, viewed as a quotient ring::

    sage: R = ZZ.quo(8*ZZ)
    sage: pi = R.cover()
    sage: pi
    Ring morphism:
      From: Integer Ring
      To:   Ring of integers modulo 8
      Defn: Natural quotient map
    sage: pi.domain()
    Integer Ring
    sage: pi.codomain()
    Ring of integers modulo 8
    sage: pi(10)
    2
    sage: pi.lift()
    Set-theoretic ring morphism:
      From: Ring of integers modulo 8
      To:   Integer Ring
      Defn: Choice of lifting map
    sage: pi.lift(13)
    5

EXAMPLE: Inclusion of GF(2) into GF(4,'a').

::

    sage: k = GF(2)
    sage: i = k.hom(GF(4, 'a'))
    sage: i
    Ring Coercion morphism:
      From: Finite Field of size 2
      To:   Finite Field in a of size 2^2
    sage: i(0)
    0
    sage: a = i(1); a.parent()
    Finite Field in a of size 2^2

We next compose the inclusion with reduction from the integers to
GF(2).

::

    sage: pi = ZZ.hom(k)
    sage: pi
    Ring Coercion morphism:
      From: Integer Ring
      To:   Finite Field of size 2
    sage: f = i * pi
    sage: f
    Composite map:
      From: Integer Ring
      To:   Finite Field in a of size 2^2
      Defn:   Ring Coercion morphism:
              From: Integer Ring
              To:   Finite Field of size 2
            then
              Ring Coercion morphism:
              From: Finite Field of size 2
              To:   Finite Field in a of size 2^2
    sage: a = f(5); a
    1
    sage: a.parent()
    Finite Field in a of size 2^2

EXAMPLE: Inclusion from `\QQ` to the 3-adic field.

::

    sage: phi = QQ.hom(Qp(3, print_mode = 'series'))
    sage: phi
    Ring Coercion morphism:
      From: Rational Field
      To:   3-adic Field with capped relative precision 20
    sage: phi.codomain()
    3-adic Field with capped relative precision 20
    sage: phi(394)
    1 + 2*3 + 3^2 + 2*3^3 + 3^4 + 3^5 + O(3^20)

EXAMPLE: An automorphism of a quotient of a univariate polynomial
ring.

::

    sage: R.<x> = PolynomialRing(QQ)
    sage: S.<sqrt2> = R.quo(x^2-2)
    sage: sqrt2^2
    2
    sage: (3+sqrt2)^10
    993054*sqrt2 + 1404491
    sage: c = S.hom([-sqrt2])
    sage: c(1+sqrt2)
    -sqrt2 + 1

Note that Sage verifies that the morphism is valid::

    sage: (1 - sqrt2)^2
    -2*sqrt2 + 3
    sage: c = S.hom([1-sqrt2])    # this is not valid
    Traceback (most recent call last):
    ...
    TypeError: images do not define a valid homomorphism

EXAMPLE: Endomorphism of power series ring.

::

    sage: R.<t> = PowerSeriesRing(QQ); R
    Power Series Ring in t over Rational Field
    sage: f = R.hom([t^2]); f
    Ring endomorphism of Power Series Ring in t over Rational Field
      Defn: t |--> t^2
    sage: R.set_default_prec(10)
    sage: s = 1/(1 + t); s
    1 - t + t^2 - t^3 + t^4 - t^5 + t^6 - t^7 + t^8 - t^9 + O(t^10)
    sage: f(s)
    1 - t^2 + t^4 - t^6 + t^8 - t^10 + t^12 - t^14 + t^16 - t^18 + O(t^20)

EXAMPLE: Frobenius on a power series ring over a finite field.

::

    sage: R.<t> = PowerSeriesRing(GF(5))
    sage: f = R.hom([t^5]); f
    Ring endomorphism of Power Series Ring in t over Finite Field of size 5
      Defn: t |--> t^5
    sage: a = 2 + t + 3*t^2 + 4*t^3 + O(t^4)
    sage: b = 1 + t + 2*t^2 + t^3 + O(t^5)
    sage: f(a)
    2 + t^5 + 3*t^10 + 4*t^15 + O(t^20)
    sage: f(b)
    1 + t^5 + 2*t^10 + t^15 + O(t^25)
    sage: f(a*b)
    2 + 3*t^5 + 3*t^10 + t^15 + O(t^20)
    sage: f(a)*f(b)
    2 + 3*t^5 + 3*t^10 + t^15 + O(t^20)

EXAMPLE: Homomorphism of Laurent series ring.

::

    sage: R.<t> = LaurentSeriesRing(QQ)
    sage: f = R.hom([t^3 + t]); f
    Ring endomorphism of Laurent Series Ring in t over Rational Field
      Defn: t |--> t + t^3
    sage: R.set_default_prec(10)
    sage: s = 2/t^2 + 1/(1 + t); s
    2*t^-2 + 1 - t + t^2 - t^3 + t^4 - t^5 + t^6 - t^7 + t^8 - t^9 + O(t^10)
    sage: f(s)
    2*t^-2 - 3 - t + 7*t^2 - 2*t^3 - 5*t^4 - 4*t^5 + 16*t^6 - 9*t^7 + O(t^8)
    sage: f = R.hom([t^3]); f
    Ring endomorphism of Laurent Series Ring in t over Rational Field
      Defn: t |--> t^3
    sage: f(s)
    2*t^-6 + 1 - t^3 + t^6 - t^9 + t^12 - t^15 + t^18 - t^21 + t^24 - t^27 + O(t^30)

Note that the homomorphism must result in a converging Laurent
series, so the valuation of the image of the generator must be
positive::

    sage: R.hom([1/t])
    Traceback (most recent call last):
    ...
    TypeError: images do not define a valid homomorphism
    sage: R.hom([1])
    Traceback (most recent call last):
    ...
    TypeError: images do not define a valid homomorphism

EXAMPLE: Complex conjugation on cyclotomic fields.

::

    sage: K.<zeta7> = CyclotomicField(7)
    sage: c = K.hom([1/zeta7]); c
    Ring endomorphism of Cyclotomic Field of order 7 and degree 6
      Defn: zeta7 |--> -zeta7^5 - zeta7^4 - zeta7^3 - zeta7^2 - zeta7 - 1
    sage: a = (1+zeta7)^5; a
    zeta7^5 + 5*zeta7^4 + 10*zeta7^3 + 10*zeta7^2 + 5*zeta7 + 1
    sage: c(a)
    5*zeta7^5 + 5*zeta7^4 - 4*zeta7^2 - 5*zeta7 - 4
    sage: c(zeta7 + 1/zeta7)       # this element is obviously fixed by inversion
    -zeta7^5 - zeta7^4 - zeta7^3 - zeta7^2 - 1
    sage: zeta7 + 1/zeta7
    -zeta7^5 - zeta7^4 - zeta7^3 - zeta7^2 - 1

EXAMPLE: Embedding a number field into the reals.

::

    sage: R.<x> = PolynomialRing(QQ)
    sage: K.<beta> = NumberField(x^3 - 2)
    sage: alpha = RR(2)^(1/3); alpha
    1.25992104989487
    sage: i = K.hom([alpha],check=False); i
    Ring morphism:
      From: Number Field in beta with defining polynomial x^3 - 2
      To:   Real Field with 53 bits of precision
      Defn: beta |--> 1.25992104989487
    sage: i(beta)
    1.25992104989487
    sage: i(beta^3)
    2.00000000000000
    sage: i(beta^2 + 1)
    2.58740105196820

An example from Jim Carlson::

    sage: K = QQ # by the way :-)
    sage: R.<a,b,c,d> = K[]; R
    Multivariate Polynomial Ring in a, b, c, d over Rational Field
    sage: S.<u> = K[]; S
    Univariate Polynomial Ring in u over Rational Field
    sage: f = R.hom([0,0,0,u], S); f
    Ring morphism:
      From: Multivariate Polynomial Ring in a, b, c, d over Rational Field
      To:   Univariate Polynomial Ring in u over Rational Field
      Defn: a |--> 0
            b |--> 0
            c |--> 0
            d |--> u
    sage: f(a+b+c+d)
    u
    sage: f( (a+b+c+d)^2 )
    u^2

TESTS::

    sage: H = Hom(ZZ, QQ)
    sage: H == loads(dumps(H))
    True

::

    sage: K.<zeta7> = CyclotomicField(7)
    sage: c = K.hom([1/zeta7])
    sage: c == loads(dumps(c))
    True

::

    sage: R.<t> = PowerSeriesRing(GF(5))
    sage: f = R.hom([t^5])
    sage: f == loads(dumps(f))
    True
"""

#*****************************************************************************
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

include "../ext/cdefs.pxi"
include "../ext/stdsage.pxi"

import ideal

import homset

def is_RingHomomorphism(phi):
    """
    Return True if phi is of type RingHomomorphism.

    EXAMPLES::

        sage: f = Zmod(8).cover()
        sage: sage.rings.morphism.is_RingHomomorphism(f)
        True
        sage: sage.rings.morphism.is_RingHomomorphism(2/3)
        False
    """
    return PY_TYPE_CHECK(phi, RingHomomorphism)

cdef class RingMap(Morphism):
    """
    Set-theoretic map between rings.
    """
    def __init__(self, parent):
        """
        This is an abstract base class that isn't directly
        instantiated, but we will do so anyways as a test.

        TESTS::

            sage: f = sage.rings.morphism.RingMap(ZZ.Hom(ZZ))
            sage: type(f)
            <type 'sage.rings.morphism.RingMap'>
        """
        Morphism.__init__(self, parent)

    def _repr_type(self):
        """
        TESTS::

            sage: f = sage.rings.morphism.RingMap(ZZ.Hom(ZZ))
            sage: type(f)
            <type 'sage.rings.morphism.RingMap'>
            sage: f._repr_type()
            'Set-theoretic ring'
            sage: f
            Set-theoretic ring endomorphism of Integer Ring
        """
        return "Set-theoretic ring"

cdef class RingMap_lift(RingMap):
    r"""
    Given rings `R` and `S` such that for any
    `x \in R` the function ``x.lift()`` is an
    element that naturally coerces to `S`, this returns the
    set-theoretic ring map `R \to S` sending `x` to
    ``x.lift()``.

    EXAMPLES::

        sage: R, (x,y) = PolynomialRing(QQ, 2, 'xy').objgens()
        sage: S.<xbar,ybar> = R.quo( (x^2 + y^2, y) )
        sage: S.lift()
        Set-theoretic ring morphism:
          From: Quotient of Multivariate Polynomial Ring in x, y over Rational Field by the ideal (x^2 + y^2, y)
          To:   Multivariate Polynomial Ring in x, y over Rational Field
          Defn: Choice of lifting map
        sage: S.lift() == 0
        False

    Since trac ticket #11068, it is possible to create
    quotient rings of non-commutative rings by two-sided
    ideals. It was needed to modify :class:`RingMap_lift`
    so that rings can be accepted that are no instances
    of :class:`sage.rings.ring.Ring`, as in the following
    example::

        sage: MS = MatrixSpace(GF(5),2,2)
        sage: I = MS*[MS.0*MS.1,MS.2+MS.3]*MS
        sage: Q = MS.quo(I)
        sage: Q.0*Q.1   # indirect doctest
        [0 1]
        [0 0]

    """
    def __init__(self, R, S):
        """
        Create a lifting ring map.

        EXAMPLES::

            sage: f = Zmod(8).lift()          # indirect doctest
            sage: f(3)
            3
            sage: type(f(3))
            <type 'sage.rings.integer.Integer'>
            sage: type(f)
            <type 'sage.rings.morphism.RingMap_lift'>
        """
        from sage.categories.sets_cat import Sets
        H = R.Hom(S, Sets())
        RingMap.__init__(self, H)
        self.S = S  # for efficiency
        try:
            S._coerce_(R(0).lift())
        except TypeError:
            raise TypeError, "No natural lift map"

    cdef _update_slots(self, _slots):
        self.S = _slots['S']
        Morphism._update_slots(self, _slots)

    cdef _extra_slots(self, _slots):
        _slots['S'] = self.S
        return Morphism._extra_slots(self, _slots)

    def __cmp__(self, other):
        """
        Compare a ring lifting maps self to other.  Ring lifting maps
        never compare equal to any other data type.  If other is a
        ring lifting maps, the parents of self and other are compared.

        EXAMPLES::

            sage: f = Zmod(8).lift()
            sage: g = Zmod(10).lift()
            sage: f == f
            True
            sage: f == g
            False
            sage: f < g
            True
            sage: f > g
            False

        Verify that trac #5758 has been fixed::

            sage: Zmod(8).lift() == 1
            False
        """
        if not PY_TYPE_CHECK(other, RingMap_lift):
            return cmp(type(self), type(other))

        # Since they are lifting maps they are determined by their
        # parents, i.e., by the domain and codomain, since we just
        # compare those.
        return cmp(self.parent(), other.parent())

    def _repr_defn(self):
        """
        Used in printing out lifting maps.

        EXAMPLES::

            sage: f = Zmod(8).lift()
            sage: f._repr_defn()
            'Choice of lifting map'
            sage: f
            Set-theoretic ring morphism:
              From: Ring of integers modulo 8
              To:   Integer Ring
              Defn: Choice of lifting map
        """
        return "Choice of lifting map"

    cpdef Element _call_(self, x):
        """
        Evaluate this function at x.

        EXAMPLE::

            sage: f = Zmod(8).lift()
            sage: type(f)
            <type 'sage.rings.morphism.RingMap_lift'>
            sage: f(-1)                       # indirect doctest
            7
            sage: type(f(-1))
            <type 'sage.rings.integer.Integer'>
        """
        return self.S._coerce_c(x.lift())

cdef class RingHomomorphism(RingMap):
    """
    Homomorphism of rings.
    """
    def __init__(self, parent):
        """
        EXAMPLES:

            sage: f = ZZ.hom(Zmod(6)); f
            Ring Coercion morphism:
              From: Integer Ring
              To:   Ring of integers modulo 6
            sage: isinstance(f, sage.rings.morphism.RingHomomorphism)
            True
        """
        if not homset.is_RingHomset(parent):
            raise TypeError, "parent must be a ring homset"
        RingMap.__init__(self, parent)

    def __nonzero__(self):
        """
        Every ring map is nonzero unless the domain or codomain is the
        0 ring, since there is no zero map between rings, since 1 goes
        to 1.

        EXAMPLES::

        Usually ring morphisms are nonzero::

            sage: bool(ZZ.hom(QQ,[1]))
            True

        However, they aren't if 1==0 in the codomain::

            sage: R1 = Zmod(1)
            sage: phi = R1.hom(R1, [1])
            sage: bool(phi)
            False
            sage: bool(ZZ.hom(R1, [1]))
            False
        """
        return bool(self.codomain().one_element())

    def _repr_type(self):
        """
        Used internally in printing this morphism.

        TESTS::

        This never actually gets called, since derived classes
        override it.  Nevertheless, we call it directly to illustrate
        that it works as a default.::

            sage: phi = ZZ.hom(QQ,[1])
            sage: phi._repr_type()
            'Ring Coercion'
            sage: sage.rings.morphism.RingHomomorphism._repr_type(phi)
            'Ring'
        """
        return "Ring"

    def _set_lift(self, lift):
        """
        Used internally to define a lifting homomorphism associated to
        this homomorphism, which goes in the other direction.  I.e.,
        if self is from R to S, then the lift must be a set-theoretic
        map from S to R such that self(lift(x)) == x.

        INPUT:
            - ``lift`` -- a ring map

        OUTPUT:
            changes the state of self.

        EXAMPLES::

            sage: f = ZZ.hom(Zmod(7))
            sage: f._set_lift(Zmod(7).lift())
            sage: f.lift()
            Set-theoretic ring morphism:
              From: Ring of integers modulo 7
              To:   Integer Ring
              Defn: Choice of lifting map
        """
        if not PY_TYPE_CHECK(lift, RingMap):
            raise TypeError, "lift must be a RingMap"
        if lift.domain() != self.codomain():
            raise TypeError, "lift must have correct domain"
        if lift.codomain() != self.domain():
            raise TypeError, "lift must have correct codomain"
        self._lift = lift

    cdef _update_slots(self, _slots):
        if _slots.has_key('_lift'):
            self._lift = _slots['_lift']
        Morphism._update_slots(self, _slots)

    cdef _extra_slots(self, _slots):
        try:
            _slots['_lift'] = self._lift
        except AttributeError:
            pass
        return Morphism._extra_slots(self, _slots)

    def _composition_(self, right, homset):
        """
        If ``homset`` is a homset of rings and ``right`` is a
        ring homomorphism given by the images of generators,
        (indirectly in the case of homomorphisms from relative
        number fields), the composition with ``self`` will be
        of the appropriate type.

        Otherwise, a formal composite map is returned.

        EXAMPLES::

            sage: R.<x,y> = QQ[]
            sage: S.<a,b> = QQ[]
            sage: f = R.hom([a+b,a-b])
            sage: g = S.hom(Frac(S))
            sage: g*f
            Ring morphism:
              From: Multivariate Polynomial Ring in x, y over Rational Field
              To:   Fraction Field of Multivariate Polynomial Ring in a, b over Rational Field
              Defn: x |--> a + b
                    y |--> a - b

        When ``right`` is defined by the images of generators, the
        result has the type of a homomorphism between its domain and
        codomain::

            sage: C = CyclotomicField(24)
            sage: f = End(C)[1]
            sage: type(f*f) == type(f)
            True

        An example where the domain of ``right`` is a relative number field::
            sage: PQ.<X> = QQ[]
            sage: K.<a, b> = NumberField([X^2 - 2, X^2 - 3])
            sage: e, u, v, w = End(K)
            sage: u*v
            Relative number field endomorphism of Number Field in a with defining polynomial X^2 - 2 over its base field
              Defn: a |--> -a
                    b |--> b

        An example where ``right`` is not a ring homomorphism::

            sage: from sage.categories.morphism import SetMorphism
            sage: h = SetMorphism(Hom(R,S,Rings()), lambda p: p[0])
            sage: g*h
            Composite map:
              From: Multivariate Polynomial Ring in x, y over Rational Field
              To:   Fraction Field of Multivariate Polynomial Ring in a, b over Rational Field
              Defn:   Generic morphism:
                      From: Multivariate Polynomial Ring in x, y over Rational Field
                      To:   Multivariate Polynomial Ring in a, b over Rational Field
                    then
                      Ring Coercion morphism:
                      From: Multivariate Polynomial Ring in a, b over Rational Field
                      To:   Fraction Field of Multivariate Polynomial Ring in a, b over Rational Field

        AUTHORS:

        -- Simon King (2010-05)
        -- Francis Clarke (2011-02)

        """
        from sage.all import Rings
        if homset.homset_category().is_subcategory(Rings()):
            if isinstance(right, RingHomomorphism_im_gens):
                try:
                    return homset([self(g) for g in right.im_gens()])
                except ValueError:
                    pass
            from sage.rings.number_field.morphism import RelativeNumberFieldHomomorphism_from_abs
            if isinstance(right, RelativeNumberFieldHomomorphism_from_abs):
                try:
                    return homset(self*right.abs_hom())
                except ValueError:
                    pass
        return sage.categories.map.Map._composition_(self, right, homset)

    def is_injective(self):
        """
        Return whether or not this morphism is injective, or raise
        a NotImplementedError.

        EXAMPLES:

        Note that currently this is not implemented in most
        interesting cases::

            sage: f = ZZ.hom(QQ)
            sage: f.is_injective()
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def is_zero(self):
        r"""
        Return True if this is the zero map and False otherwise.

        A *ring* homomorphism is considered to be 0 if and only if it
        sends the 1 element of the domain to the 0 element of the codomain.
        Since rings in Sage all have a 1 element, the zero homomorphism is
        only to a ring of order 1, where 1==0, e.g., the ring
        ``Integers(1)``.

        EXAMPLES:

        First an example of a map that is obviously nonzero.

        ::

            sage: h = Hom(ZZ, QQ)
            sage: f = h.natural_map()
            sage: f.is_zero()
            False

        Next we make the zero ring as `\ZZ/1\ZZ`.

        ::

            sage: R = Integers(1)
            sage: R
            Ring of integers modulo 1
            sage: h = Hom(ZZ, R)
            sage: f = h.natural_map()
            sage: f.is_zero()
            True

        Finally we check an example in characteristic 2.

        ::

            sage: h = Hom(ZZ, GF(2))
            sage: f = h.natural_map()
            sage: f.is_zero()
            False
        """
        return self(self.domain()(1)) == self.codomain()(0)

    def pushforward(self, I):
        """
        Returns the pushforward of the ideal `I` under this ring
        homomorphism.

        EXAMPLES::

            sage: R.<x,y> = QQ[]; S.<xx,yy> = R.quo([x^2,y^2]);  f = S.cover()
            sage: f.pushforward(R.ideal([x,3*x+x*y+y^2]))
            Ideal (xx, xx*yy + 3*xx) of Quotient of Multivariate Polynomial Ring in x, y over Rational Field by the ideal (x^2, y^2)
        """
        if not ideal.is_Ideal(I):
            raise TypeError, "I must be an ideal"
        R = self.codomain()
        return R.ideal([self(y) for y in I.gens()])

    def inverse_image(self, I):
        """
        Return the inverse image of the ideal `I` under this ring
        homomorphism.

        EXAMPLES:

        This is not implemented in any generality yet::

            sage: f = ZZ.hom(ZZ)
            sage: f.inverse_image(ZZ.ideal(2))
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def lift(self, x=None):
        """
        Return a lifting homomorphism associated to this homomorphism, if
        it has been defined.

        If x is not None, return the value of the lift morphism on x.

        EXAMPLES::

            sage: R.<x,y> = QQ[]
            sage: f = R.hom([x,x])
            sage: f(x+y)
            2*x
            sage: f.lift()
            Traceback (most recent call last):
            ...
            ValueError: no lift map defined
            sage: g = R.hom(R)
            sage: f._set_lift(g)
            sage: f.lift() == g
            True
            sage: f.lift(x)
            x
        """
        if self._lift is None:
            raise ValueError, "no lift map defined"
        if x is None:
            return self._lift
        return self._lift(x)

cdef class RingHomomorphism_coercion(RingHomomorphism):
    def __init__(self, parent, check = True):
        """
        INPUT:
            - ``parent`` -- ring homset
            - ``check`` -- bool (default: True)

        EXAMPLES::

            sage: f = ZZ.hom(QQ); f                    # indirect doctest
            Ring Coercion morphism:
              From: Integer Ring
              To:   Rational Field

            sage: f == loads(dumps(f))
            True
        """
        RingHomomorphism.__init__(self, parent)
        # putting in check allows us to define subclasses of RingHomomorphism_coercion that implement _coerce_map_from
        if check and not self.codomain().has_coerce_map_from(self.domain()):
            raise TypeError, "Natural coercion morphism from %s to %s not defined."%(self.domain(), self.codomain())

    def _repr_type(self):
        """
        Used internally when printing this.

        EXAMPLES::

            sage: f = ZZ.hom(QQ)
            sage: type(f)
            <type 'sage.rings.morphism.RingHomomorphism_coercion'>
            sage: f._repr_type()
            'Ring Coercion'
        """
        return "Ring Coercion"

    def __cmp__(self, other):
        """
        Compare a ring coercion morphism self to other.  Ring coercion
        morphisms never compare equal to any other data type.  If
        other is a ring coercion morphism, the parents of self and
        other are compared.

        EXAMPLES::

            sage: f = ZZ.hom(QQ)
            sage: g = ZZ.hom(ZZ)
            sage: f == g
            False
            sage: f > g
            True
            sage: f < g
            False
            sage: h = Zmod(6).lift()
            sage: f == h
            False
        """
        if not PY_TYPE_CHECK(other, RingHomomorphism_coercion):
            return cmp(type(self), type(other))

        # Since they are coercion morphisms they are determined by
        # their parents, i.e., by the domain and codomain, so we just
        # compare those.
        return cmp(self.parent(), other.parent())

    cpdef Element _call_(self, x):
        """
        Evaluate this coercion morphism at x.

        EXAMPLES::

            sage: f = ZZ.hom(QQ); type(f)
            <type 'sage.rings.morphism.RingHomomorphism_coercion'>
            sage: f(2) == 2
            True
            sage: type(f(2))          # indirect doctest
            <type 'sage.rings.rational.Rational'>
        """
        return self.codomain().coerce(x)

import sage.structure.all

cdef class RingHomomorphism_im_gens(RingHomomorphism):
    """
    A ring homomorphism determined by the images of generators.
    """
    def __init__(self, parent, im_gens, check=True):
        """
        EXAMPLES::

            sage: R.<x,y> = QQ[]
            sage: phi = R.hom([x,x+y]); phi
            Ring endomorphism of Multivariate Polynomial Ring in x, y over Rational Field
              Defn: x |--> x
                    y |--> x + y
            sage: type(phi)
            <type 'sage.rings.morphism.RingHomomorphism_im_gens'>

        Here's another example where the domain isn't free::

            sage: S.<xx,yy> = R.quotient(x - y)
            sage: phi = S.hom([xx+1,xx+1])

        Note that one has to specify valid images::

            sage: phi = S.hom([xx+1,xx-1])
            Traceback (most recent call last):
            ...
            TypeError: images do not define a valid homomorphism

        There is a check option, but it may be ignored in some cases
        -- it's purpose isn't so you can lie to Sage, but to sometimes
        speed up creation of a homomorphism:

            sage: phi = S.hom([xx+1,xx-1],check=False)
            Traceback (most recent call last):
            ...
            TypeError: images do not define a valid homomorphism
        """
        RingHomomorphism.__init__(self, parent)
        if not isinstance(im_gens, sage.structure.sequence.Sequence_generic):
            if not isinstance(im_gens, (tuple, list)):
                im_gens = [im_gens]
            im_gens = sage.structure.all.Sequence(im_gens, parent.codomain())
        if check:
            if len(im_gens) != parent.domain().ngens():
                raise ValueError, "number of images must equal number of generators"
            t = parent.domain()._is_valid_homomorphism_(parent.codomain(), im_gens)
            if not t:
                raise ValueError, "relations do not all (canonically) map to 0 under map determined by images of generators."
        self.__im_gens = im_gens

    def im_gens(self):
        """
        Return the images of the generators of the domain.

        OUTPUT:
            - ``list`` -- a copy of the list of gens (it is safe to change this)

        EXAMPLES::

            sage: R.<x,y> = QQ[]
            sage: f = R.hom([x,x+y])
            sage: f.im_gens()
            [x, x + y]

        We verify that the returned list of images of gens is a copy,
        so changing it doesn't change f::

            sage: f.im_gens()[0] = 5
            sage: f.im_gens()
            [x, x + y]
        """
        return list(self.__im_gens)

    cdef _update_slots(self, _slots):
        self.__im_gens = _slots['__im_gens']
        RingHomomorphism._update_slots(self, _slots)

    cdef _extra_slots(self, _slots):
        _slots['__im_gens'] = self.__im_gens
        return RingHomomorphism._extra_slots(self, _slots)

    def __richcmp__(left, right, int op):
        """
        Used internally by the cmp method.

        TESTS::

            sage: R.<x,y> = QQ[]; f = R.hom([x,x+y]); g = R.hom([y,x])
            sage: cmp(f,g)             # indirect doctest
            1
            sage: cmp(g,f)
            -1

        """
        return (<Element>left)._richcmp(right, op)

    cdef int _cmp_c_impl(self, Element other) except -2:
        """
        EXAMPLES:

        A single variate quotient over QQ.

        ::

            sage: R.<x> = QQ[]
            sage: Q.<a> = R.quotient(x^2 + x + 1)
            sage: f1 = R.hom([a])
            sage: f2 = R.hom([a + a^2 + a + 1])
            sage: f1 == f2
            True
            sage: f1 == R.hom([a^2])
            False
            sage: f1(x^3 + x)
            a + 1
            sage: f2(x^3 + x)
            a + 1

        TESTS::

            sage: loads(dumps(f2)) == f2
            True

        EXAMPLES:

        A multivariate quotient over a finite field.

        ::

            sage: R.<x,y> = GF(7)[]
            sage: Q.<a,b> = R.quotient([x^2 + x + 1, y^2 + y + 1])
            sage: f1 = R.hom([a, b])
            sage: f2 = R.hom([a + a^2 + a + 1, b + b^2 + b + 1])
            sage: f1 == f2
            True
            sage: f1 == R.hom([b,a])
            False
            sage: x^3 + x + y^2
            x^3 + y^2 + x
            sage: f1(x^3 + x + y^2)
            a - b
            sage: f2(x^3 + x + y^2)
            a - b

        TEST::

            sage: loads(dumps(f2)) == f2
            True
        """
        if not PY_TYPE_CHECK(other, RingHomomorphism_im_gens):
            return cmp(type(self), type(other))
        return cmp(self.__im_gens, (<RingHomomorphism_im_gens>other).__im_gens)

    def _repr_defn(self):
        """
        Used in constructing string representation of self.

        EXAMPLES::

            sage: R.<x,y> = QQ[]; f = R.hom([x^2,x+y])
            sage: print f._repr_defn()
            x |--> x^2
            y |--> x + y
        """
        D = self.domain()
        ig = self.__im_gens
        return '\n'.join(['%s |--> %s'%(D.gen(i), ig[i]) for\
                       i in range(D.ngens())])

    cpdef Element _call_(self, x):
        """
        Evaluate this homomorphism at x.

        EXAMPLES::

            sage: R.<x,y,z> = ZZ[]; f = R.hom([2*x,z,y])
            sage: f(x+2*y+3*z)             # indirect doctest
            2*x + 3*y + 2*z
        """
        return x._im_gens_(self.codomain(), self.im_gens())

cdef class RingHomomorphism_from_base(RingHomomorphism):
    """
    A ring homomorphism determined by a ring homomorphism of the base ring.

    AUTHOR:

    - Simon King (initial version, 2010-04-30)

    EXAMPLE:

    We define two polynomial rings and a ring homomorphism.
    ::

        sage: R.<x,y> = QQ[]
        sage: S.<z> = QQ[]
        sage: f = R.hom([2*z,3*z],S)

    Now we construct polynomial rings based on ``R`` and ``S``, and let ``f`` act
    on the coefficients::

        sage: PR.<t> = R[]
        sage: PS = S['t']
        sage: Pf = PR.hom(f,PS)
        sage: Pf
        Ring morphism:
          From: Univariate Polynomial Ring in t over Multivariate Polynomial Ring in x, y over Rational Field
          To:   Univariate Polynomial Ring in t over Univariate Polynomial Ring in z over Rational Field
          Defn: Induced from base ring by
                Ring morphism:
                  From: Multivariate Polynomial Ring in x, y over Rational Field
                  To:   Univariate Polynomial Ring in z over Rational Field
                  Defn: x |--> 2*z
                        y |--> 3*z
        sage: p = (x - 4*y + 1/13)*t^2 + (1/2*x^2 - 1/3*y^2)*t + 2*y^2 + x
        sage: Pf(p)
        (-10*z + 1/13)*t^2 - z^2*t + 18*z^2 + 2*z

    Similarly, we can construct the induced homomorphism on a matrix ring over our polynomial rings::

        sage: MR = MatrixSpace(R,2,2)
        sage: MS = MatrixSpace(S,2,2)
        sage: M = MR([x^2 + 1/7*x*y - y^2, - 1/2*y^2 + 2*y + 1/6, 4*x^2 - 14*x, 1/2*y^2 + 13/4*x - 2/11*y])
        sage: Mf = MR.hom(f,MS)
        sage: Mf
        Ring morphism:
          From: Full MatrixSpace of 2 by 2 dense matrices over Multivariate Polynomial Ring in x, y over Rational Field
          To:   Full MatrixSpace of 2 by 2 dense matrices over Univariate Polynomial Ring in z over Rational Field
          Defn: Induced from base ring by
                Ring morphism:
                  From: Multivariate Polynomial Ring in x, y over Rational Field
                  To:   Univariate Polynomial Ring in z over Rational Field
                  Defn: x |--> 2*z
                        y |--> 3*z
        sage: Mf(M)
        [           -29/7*z^2 -9/2*z^2 + 6*z + 1/6]
        [       16*z^2 - 28*z   9/2*z^2 + 131/22*z]

    The construction of induced homomorphisms is recursive, and so we have::

        sage: MPR = MatrixSpace(PR, 2)
        sage: MPS = MatrixSpace(PS, 2)
        sage: M = MPR([(- x + y)*t^2 + 58*t - 3*x^2 + x*y, (- 1/7*x*y - 1/40*x)*t^2 + (5*x^2 + y^2)*t + 2*y, (- 1/3*y + 1)*t^2 + 1/3*x*y + y^2 + 5/2*y + 1/4, (x + 6*y + 1)*t^2])
        sage: MPf = MPR.hom(f,MPS); MPf
        Ring morphism:
          From: Full MatrixSpace of 2 by 2 dense matrices over Univariate Polynomial Ring in t over Multivariate Polynomial Ring in x, y over Rational Field
          To:   Full MatrixSpace of 2 by 2 dense matrices over Univariate Polynomial Ring in t over Univariate Polynomial Ring in z over Rational Field
          Defn: Induced from base ring by
                Ring morphism:
                  From: Univariate Polynomial Ring in t over Multivariate Polynomial Ring in x, y over Rational Field
                  To:   Univariate Polynomial Ring in t over Univariate Polynomial Ring in z over Rational Field
                  Defn: Induced from base ring by
                        Ring morphism:
                          From: Multivariate Polynomial Ring in x, y over Rational Field
                          To:   Univariate Polynomial Ring in z over Rational Field
                          Defn: x |--> 2*z
                                y |--> 3*z
        sage: MPf(M)
        [                    z*t^2 + 58*t - 6*z^2 (-6/7*z^2 - 1/20*z)*t^2 + 29*z^2*t + 6*z]
        [    (-z + 1)*t^2 + 11*z^2 + 15/2*z + 1/4                           (20*z + 1)*t^2]


    """
    def __init__(self, parent, underlying):
        """
        TEST::

            sage: from sage.rings.morphism import RingHomomorphism_from_base
            sage: R.<x> = ZZ[]
            sage: f = R.hom([2*x],R)
            sage: P = MatrixSpace(R,2).Hom(MatrixSpace(R,2))
            sage: g = RingHomomorphism_from_base(P,f)
            sage: g
            Ring endomorphism of Full MatrixSpace of 2 by 2 dense matrices over Univariate Polynomial Ring in x over Integer Ring
              Defn: Induced from base ring by
                    Ring endomorphism of Univariate Polynomial Ring in x over Integer Ring
                      Defn: x |--> 2*x

        Note that an induced homomorphism only makes sense if domain and codomain are constructed in a
        compatible way. So, the following results in an error::

            sage: P = MatrixSpace(R,2).Hom(R['t'])
            sage: g = RingHomomorphism_from_base(P,f)
            Traceback (most recent call last):
            ...
            ValueError: Domain and codomain must have the same functorial construction over their base rings

        """
        RingHomomorphism.__init__(self, parent)
        if not is_RingHomomorphism(underlying):
            raise TypeError, "Homomorphism of the base ring expected"
        if underlying.domain() != parent.domain().base():
            raise ValueError, "The given homomorphism has to have the domain %s"%parent.domain().base()
        if underlying.codomain() != parent.codomain().base():
            raise ValueError, "The given homomorphism has to have the codomain %s"%parent.codomain().base()
        if parent.domain().construction()[0] != parent.codomain().construction()[0]:
            raise ValueError, "Domain and codomain must have the same functorial construction over their base rings"
        self.__underlying = underlying

    def underlying_map(self):
        """
        Return the underlying homomorphism of the base ring.

        EXAMPLE::

            sage: R.<x,y> = QQ[]
            sage: S.<z> = QQ[]
            sage: f = R.hom([2*z,3*z],S)
            sage: MR = MatrixSpace(R,2)
            sage: MS = MatrixSpace(S,2)
            sage: g = MR.hom(f,MS)
            sage: g.underlying_map() == f
            True

        """
        return self.__underlying

    cdef _update_slots(self, _slots):
        self.__underlying = _slots['__underlying']
        RingHomomorphism._update_slots(self, _slots)

    cdef _extra_slots(self, _slots):
        _slots['__underlying'] = self.__underlying
        return RingHomomorphism._extra_slots(self, _slots)

    def __richcmp__(left, right, int op):
        """
        Used internally by the cmp method.

        TESTS::

            sage: R.<x,y> = QQ[]; f = R.hom([x,x+y]); g = R.hom([y,x])
            sage: S.<z> = R[]
            sage: fS = S.hom(f,S); gS = S.hom(g,S)
            sage: cmp(fS,gS)   # indirect doctest
            1
            sage: cmp(gS,fS)   # indirect doctest
            -1

        """
        return (<Element>left)._richcmp(right, op)

    cdef int _cmp_c_impl(self, Element other) except -2:
        """
        EXAMPLE:

        A multivariate polynomial ring over a single variate quotient over QQ.

            sage: R.<x> = QQ[]
            sage: Q.<a> = R.quotient(x^2 + x + 1)
            sage: f1 = R.hom([a])
            sage: f2 = R.hom([a + a^2 + a + 1])
            sage: PR.<s,t> = R[]
            sage: PQ = Q['s','t']
            sage: f1P = PR.hom(f1,PQ)
            sage: f2P = PR.hom(f2,PQ)
            sage: f1P == f2P
            True

        TEST::

            sage: f1P == loads(dumps(f1P))
            True

        EXAMPLE:

        A matrix ring over a multivariate quotient over a finite field.

        ::

            sage: R.<x,y> = GF(7)[]
            sage: Q.<a,b> = R.quotient([x^2 + x + 1, y^2 + y + 1])
            sage: f1 = R.hom([a, b])
            sage: f2 = R.hom([a + a^2 + a + 1, b + b^2 + b + 1])
            sage: MR = MatrixSpace(R,2)
            sage: MQ = MatrixSpace(Q,2)
            sage: f1M = MR.hom(f1,MQ)
            sage: f2M = MR.hom(f2,MQ)
            sage: f1M == f2M
            True

        TEST::

            sage: f1M == loads(dumps(f1M))
            True

        """
        if not PY_TYPE_CHECK(other, RingHomomorphism_from_base):
            return cmp(type(self), type(other))
        return cmp(self.__underlying, (<RingHomomorphism_from_base>other).__underlying)

    def _repr_defn(self):
        """
        Used in constructing string representation of self.

        EXAMPLE:

        We use a matrix ring over univariate polynomial ring over the fraction field
        over a multivariate polynomial ring.

        ::

            sage: R1.<x,y> = ZZ[]
            sage: f = R1.hom([x+y,x-y])
            sage: R2 = MatrixSpace(FractionField(R1)['t'],2)
            sage: g = R2.hom(f,R2)
            sage: g         #indirect doctest
            Ring endomorphism of Full MatrixSpace of 2 by 2 dense matrices over Univariate Polynomial Ring in t over Fraction Field of Multivariate Polynomial Ring in x, y over Integer Ring
              Defn: Induced from base ring by
                    Ring endomorphism of Univariate Polynomial Ring in t over Fraction Field of Multivariate Polynomial Ring in x, y over Integer Ring
                      Defn: Induced from base ring by
                            Ring endomorphism of Fraction Field of Multivariate Polynomial Ring in x, y over Integer Ring
                              Defn: x |--> x + y
                                    y |--> x - y

        """
        U = repr(self.__underlying).split('\n')
        return 'Induced from base ring by\n'+'\n'.join(U)

    cpdef Element _call_(self, x):
        """
        Evaluate this homomorphism at x.

        EXAMPLES::

        """
        P = self.codomain()
        try:
            return P(dict([(a, self.__underlying(b)) for a,b in x.dict().items()]))
        except StandardError:
            pass
        try:
            return P([self.__underlying(b) for b in x])
        except StandardError:
            pass
        try:
            return P(self.__underlying(x.numerator()))/P(self.__underlying(x.denominator()))
        except StandardError:
            raise TypeError, "invalid argument %s"%repr(x)

cdef class RingHomomorphism_cover(RingHomomorphism):
    r"""
    A homomorphism induced by quotienting a ring out by an ideal.

    EXAMPLES::

        sage: R.<x,y> = PolynomialRing(QQ, 2)
        sage: S.<a,b> = R.quo(x^2 + y^2)
        sage: phi = S.cover(); phi
        Ring morphism:
          From: Multivariate Polynomial Ring in x, y over Rational Field
          To:   Quotient of Multivariate Polynomial Ring in x, y over Rational Field by the ideal (x^2 + y^2)
          Defn: Natural quotient map
        sage: phi(x+y)
        a + b
    """
    def __init__(self, parent):
        """
        Create a covering ring homomorphism, induced by quotienting out by an ideal.

        EXAMPLES::

            sage: f = Zmod(6).cover(); f    # implicit test
            Ring morphism:
              From: Integer Ring
              To:   Ring of integers modulo 6
              Defn: Natural quotient map
            sage: type(f)
            <type 'sage.rings.morphism.RingHomomorphism_cover'>
        """
        RingHomomorphism.__init__(self, parent)

    cpdef Element _call_(self, x):
        """
        Evaluate this covering homomorphism at x, which just involves
        coercing x into the domain, then codomain.

        EXAMPLES::

            sage: f = Zmod(6).cover()
            sage: type(f)
            <type 'sage.rings.morphism.RingHomomorphism_cover'>
            sage: f(-5)                 # indirect doctest
            1

        TESTS::

        We verify that calling directly raises the expected error
        (just coercing into the codomain), but calling with __call__
        (the second call below) gives a TypeError since 1/2 can't be
        coerced into the domain.

            sage: f._call_(1/2)
            Traceback (most recent call last):
            ...
            ZeroDivisionError: Inverse does not exist.
            sage: f(1/2)
            Traceback (most recent call last):
            ...
            TypeError: 1/2 fails to convert into the map's domain Integer Ring, but a `pushforward` method is not properly implemented
        """
        return self.codomain()(x)

    def _repr_defn(self):
        """
        Used internally for printing covering morphisms.

        EXAMPLES::

            sage: f = Zmod(6).cover()
            sage: f._repr_defn()
            'Natural quotient map'
            sage: type(f)
            <type 'sage.rings.morphism.RingHomomorphism_cover'>
        """
        return "Natural quotient map"

    def kernel(self):
        """
        Return the kernel of this covering morphism, which is the ideal that
        was quotiented out by.

        EXAMPLES::

            sage: f = Zmod(6).cover()
            sage: f.kernel()
            Principal ideal (6) of Integer Ring
        """
        return self.codomain().defining_ideal()

    def __cmp__(self, other):
        """
        EXAMPLES::

            sage: R.<x,y> = PolynomialRing(QQ, 2)
            sage: S.<a,b> = R.quo(x^2 + y^2)
            sage: phi = S.cover()
            sage: phi == loads(dumps(phi))
            True
            sage: phi == R.quo(x^2 + y^3).cover()
            False
        """
        if not PY_TYPE_CHECK(other, RingHomomorphism_cover):
            return cmp(type(self), type(other))
        return cmp(self.parent(), other.parent())

cdef class RingHomomorphism_from_quotient(RingHomomorphism):
    r"""
    A ring homomorphism with domain a generic quotient ring.

    INPUT:


    -  ``parent`` - a ring homset Hom(R,S)

    -  ``phi`` - a ring homomorphism C --> S, where C is the
       domain of R.cover()


    OUTPUT: a ring homomorphism

    The domain `R` is a quotient object `C \to R`, and
    ``R.cover()`` is the ring homomorphism
    `\varphi: C \to R`. The condition on the elements
    ``im_gens`` of `S` is that they define a
    homomorphism `C \to S` such that each generator of the
    kernel of `\varphi` maps to `0`.

    EXAMPLES::

        sage: R.<x, y, z> = PolynomialRing(QQ, 3)
        sage: S.<a, b, c> = R.quo(x^3 + y^3 + z^3)
        sage: phi = S.hom([b, c, a]); phi
        Ring endomorphism of Quotient of Multivariate Polynomial Ring in x, y, z over Rational Field by the ideal (x^3 + y^3 + z^3)
          Defn: a |--> b
                b |--> c
                c |--> a
        sage: phi(a+b+c)
        a + b + c
        sage: loads(dumps(phi)) == phi
        True

    Validity of the homomorphism is determined, when possible, and a
    TypeError is raised if there is no homomorphism sending the
    generators to the given images.

    ::

        sage: S.hom([b^2, c^2, a^2])
        Traceback (most recent call last):
        ...
        TypeError: images do not define a valid homomorphism
    """
    def __init__(self, parent, phi):
        """
        EXAMPLES:

            sage: R.<x,y> = QQ[]; S.<xx,yy> = R.quo([x^2,y^2]); S.hom([yy,xx])
            Ring endomorphism of Quotient of Multivariate Polynomial Ring in x, y over Rational Field by the ideal (x^2, y^2)
              Defn: xx |--> yy
                    yy |--> xx
        """
        RingHomomorphism.__init__(self, parent)
        R = parent.domain()
        pi = R.cover()  # the covering map, which should be a RingHomomorphism
        if not PY_TYPE_CHECK(pi, RingHomomorphism):
            raise TypeError, "pi should be a ring homomorphism"
        if not PY_TYPE_CHECK(phi, RingHomomorphism):
            raise TypeError, "phi should be a ring homomorphism"
        if pi.domain() != phi.domain():
            raise ValueError, "Domain of phi must equal domain of covering (%s != %s)."%(pi.domain(), phi.domain())
        for x in pi.kernel().gens():
            if phi(x) != 0:
                raise ValueError, "relations do not all (canonically) map to 0 under map determined by images of generators."
        self._lift = pi.lift()
        self.phi = phi

    cdef _update_slots(self, _slots):
        self.phi = _slots['phi']
        RingHomomorphism._update_slots(self, _slots)

    cdef _extra_slots(self, _slots):
        _slots['phi'] = self.phi
        return RingHomomorphism._extra_slots(self, _slots)

    def _phi(self):
        """
        Underlying morphism used to define this quotient map, i.e.,
        morphism from the cover of the domain.

        EXAMPLES::

            sage: R.<x,y> = QQ[]; S.<xx,yy> = R.quo([x^2,y^2]); f = S.hom([yy,xx])
            sage: f._phi()
            Ring morphism:
              From: Multivariate Polynomial Ring in x, y over Rational Field
              To:   Quotient of Multivariate Polynomial Ring in x, y over Rational Field by the ideal (x^2, y^2)
              Defn: x |--> yy
                    y |--> xx
        """
        return self.phi

    def morphism_from_cover(self):
        """
        Underlying morphism used to define this quotient map, i.e.,
        the morphism from the cover of the domain.

        EXAMPLES::

            sage: R.<x,y> = QQ[]; S.<xx,yy> = R.quo([x^2,y^2])
            sage: S.hom([yy,xx]).morphism_from_cover()
            Ring morphism:
              From: Multivariate Polynomial Ring in x, y over Rational Field
              To:   Quotient of Multivariate Polynomial Ring in x, y over Rational Field by the ideal (x^2, y^2)
              Defn: x |--> yy
                    y |--> xx
        """
        return self.phi

    def __cmp__(self, other):
        """
        EXAMPLES::

            sage: R.<x, y, z> = PolynomialRing(GF(19), 3)
            sage: S.<a, b, c> = R.quo(x^3 + y^3 + z^3)
            sage: phi = S.hom([b, c, a])
            sage: psi = S.hom([c, b, a])
            sage: f = S.hom([b, c, a + a^3 + b^3 + c^3])
            sage: phi == psi
            False
            sage: phi == f
            True
        """
        if not PY_TYPE_CHECK(other, RingHomomorphism_from_quotient):
            return cmp(type(self), type(other))
        return cmp(self.phi, (<RingHomomorphism_from_quotient>other).phi)

    def _repr_defn(self):
        """
        Used internally for printing this function.

        EXAMPLES::

            sage: R.<x,y> = QQ[]; S.<xx,yy> = R.quo([x^2,y^2]); f = S.hom([yy,xx])
            sage: print f._repr_defn()
            xx |--> yy
            yy |--> xx
        """
        D = self.domain()
        ig = self.phi.im_gens()
        return '\n'.join(['%s |--> %s'%(D.gen(i), ig[i]) for\
                          i in range(D.ngens())])

    cpdef Element _call_(self, x):
        """
        Evaluate this function at x.

        EXAMPLES::

            sage: R.<x,y> = QQ[]; S.<xx,yy> = R.quo([x^2,y^2]); f = S.hom([yy,xx])
            sage: f(3*x + (1/2)*y)   # indirect doctest
            1/2*xx + 3*yy
        """
        return self.phi(self.lift(x))
