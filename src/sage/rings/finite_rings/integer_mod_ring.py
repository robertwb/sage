r"""
Ring `\ZZ/n\ZZ` of integers modulo `n`

EXAMPLES::

    sage: R = Integers(97)
    sage: a = R(5)
    sage: a**100000000000000000000000000000000000000000000000000000000000000
    61

This example illustrates the relation between
`\ZZ/p\ZZ` and `\GF{p}`. In
particular, there is a canonical map to `\GF{p}`, but not in
the other direction.

::

    sage: r = Integers(7)
    sage: s = GF(7)
    sage: r.has_coerce_map_from(s)
    False
    sage: s.has_coerce_map_from(r)
    True
    sage: s(1) + r(1)
    2
    sage: parent(s(1) + r(1))
    Finite Field of size 7
    sage: parent(r(1) + s(1))
    Finite Field of size 7

We list the elements of `\ZZ/3\ZZ`

::

    sage: R = Integers(3)
    sage: list(R)
    [0, 1, 2]

AUTHORS:

- William Stein (initial code)

- David Joyner (2005-12-22): most examples

- Robert Bradshaw (2006-08-24): convert to SageX (Cython)

- William Stein (2007-04-29): square_roots_of_one
"""

#*****************************************************************************
#
#   Sage: System for Algebra and Geometry Experimentation
#
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
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

import sage.misc.prandom as random
import weakref

from sage.rings.arith import is_prime, factor, CRT_basis, LCM, prime_divisors, euler_phi
import sage.rings.commutative_ring as commutative_ring
import sage.rings.field as field
import integer_mod
import sage.rings.integer as integer
import sage.rings.integer_ring as integer_ring
import sage.rings.rational as rational
import sage.rings.quotient_ring as quotient_ring
import sage.rings.ideal as ideal
import element_ext_pari
from sage.structure.parent_gens import ParentWithGens

from sage.libs.pari.all import pari, PariError

import sage.interfaces.all


from sage.structure.factory import UniqueFactory

class IntegerModFactory(UniqueFactory):
    r"""
    Return the quotient ring `\ZZ / n\ZZ`.

    INPUT:


    -  ``order`` - integer (default: 0), positive or
       negative


    EXAMPLES::

        sage: IntegerModRing(15)
        Ring of integers modulo 15
        sage: IntegerModRing(7)
        Ring of integers modulo 7
        sage: IntegerModRing(-100)
        Ring of integers modulo 100

    Note that you can also use ``Integers``, which is a
    synonym for ``IntegerModRing``.

    ::

        sage: Integers(18)
        Ring of integers modulo 18
        sage: Integers() is Integers(0) is ZZ
        True
    """
    def create_key(self, order=0):
        return order

    def create_object(self, version, order):
        """
        EXAMPLES::

            sage: R = Integers(10)
            sage: TestSuite(R).run() # indirect doctest
        """
        if order < 0:
            order = -order
        if order == 0:
            return integer_ring.IntegerRing()
        else:
            return IntegerModRing_generic(order)

Zmod = Integers = IntegerModRing = IntegerModFactory("IntegerModRing")


def is_IntegerModRing(x):
    """
    Return True if x is an integer modulo ring.

    EXAMPLES::

        sage: from sage.rings.finite_rings.integer_mod_ring import is_IntegerModRing
        sage: R = IntegerModRing(17)
        sage: is_IntegerModRing(R)
        True
        sage: is_IntegerModRing(GF(13))
        True
        sage: is_IntegerModRing(GF(4, 'a'))
        False
        sage: is_IntegerModRing(10)
        False
        sage: is_IntegerModRing(ZZ)
        False
    """
    return isinstance(x, IntegerModRing_generic)

class IntegerModRing_generic(quotient_ring.QuotientRing_generic):
    """
    The ring of integers modulo N, with N composite.

    EXAMPLES::

        sage: R = IntegerModRing(97)
        sage: a = R(5)
        sage: a**(10^62)
        61
    """
    def __init__(self, order, cache=None, category=None):
        """
        Create with the command IntegerModRing(order)

        INPUT:


        -  ``order`` - an integer 1

        - ``category`` - a subcategory of ``CommutativeRings()`` (the default)
          (currently only available for subclasses)

        OUTPUT:


        -  ``IntegerModRing`` - the ring of integers modulo
           N.


        EXAMPLES:

        First we compute with integers modulo `17`.

        ::

            sage: FF = IntegerModRing(17)
            sage: FF
            Ring of integers modulo 17
            sage: FF.category()
            Join of Category of commutative rings and Category of finite enumerated sets
            sage: FF.is_field()
            True
            sage: FF.characteristic()
            17
            sage: FF.order()
            17
            sage: gens = FF.unit_gens()
            sage: a = gens[0]
            sage: a
            3
            sage: a.is_square()
            False
            sage: def pow(i): return a**i
            sage: [pow(i) for i in range(16)]
            [1, 3, 9, 10, 13, 5, 15, 11, 16, 14, 8, 7, 4, 12, 2, 6]
            sage: TestSuite(FF).run()

        One can force `FF` to be in the category of fields::

            sage: FF = IntegerModRing(17, category = Fields()) # todo: not implemented
            sage: FF.category()                                # todo: not implemented
            Join of Category of fields and Category of finite enumerated sets
            sage: TestSuite(FF).run()                          # todo: not implemented

        Next we compute with the integers modulo `16`.

        ::

            sage: Z16 = IntegerModRing(16)
            sage: Z16.category()
            Join of Category of commutative rings and Category of finite enumerated sets
            sage: Z16.is_field()
            False
            sage: Z16.order()
            16
            sage: Z16.characteristic()
            16
            sage: gens = Z16.unit_gens()
            sage: gens
            [15, 5]
            sage: a = gens[0]
            sage: b = gens[1]
            sage: def powa(i): return a**i
            sage: def powb(i): return b**i
            sage: gp_exp = FF.unit_group_exponent()
            sage: gp_exp
            16
            sage: [powa(i) for i in range(15)]
            [1, 15, 1, 15, 1, 15, 1, 15, 1, 15, 1, 15, 1, 15, 1]
            sage: [powb(i) for i in range(15)]
            [1, 5, 9, 13, 1, 5, 9, 13, 1, 5, 9, 13, 1, 5, 9]
            sage: a.multiplicative_order()
            2
            sage: b.multiplicative_order()
            4
            sage: TestSuite(Z16).run()

        Saving and loading::

            sage: R = Integers(100000)
            sage: TestSuite(R).run()  # long time (17s on sage.math, 2011)
        """
        ZZ = integer_ring.IntegerRing()
        order = ZZ(order)
        if order <= 0:
            raise ZeroDivisionError, "order must be positive"
        self.__order = order
        self._pyx_order = integer_mod.NativeIntStruct(order)
        self.__unit_group_exponent = None
        self.__factored_order = None
        self.__factored_unit_order = None
        quotient_ring.QuotientRing_generic.__init__(self, ZZ, ZZ.ideal(order), names=None)
        if category is None:
            from sage.categories.commutative_rings import CommutativeRings
            from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
            from sage.categories.category import Category
            category = Category.join([CommutativeRings(), FiniteEnumeratedSets()])
        ParentWithGens.__init__(self, self, category = category)
        if cache is None:
            cache = order < 500
        if cache:
            self._precompute_table()
        self._zero_element = integer_mod.IntegerMod(self, 0)
        self._one_element = integer_mod.IntegerMod(self, 1)

    def _macaulay2_init_(self):
        """
        EXAMPLES::

            sage: macaulay2(Integers(7))  # optional - macaulay2
            ZZ
            --
             7

        ::

            sage: macaulay2(Integers(10)) # optional - macaulay2
            Traceback (most recent call last):
            ...
            TypeError: Error evaluating Macaulay2 code.
            IN:sage1=ZZ/10;
            OUT:stdio:3:9:(1):[0]: ZZ/n not implemented yet for composite n
        """
        return "ZZ/%s"%self.order()

    def _axiom_init_(self):
        """
        Returns a string representation of self in (Pan)Axiom.

        EXAMPLES::

            sage: Z7 = Integers(7)
            sage: Z7._axiom_init_()
            'IntegerMod(7)'

            sage: axiom(Z7)  #optional - axiom
            IntegerMod 7

            sage: fricas(Z7) #optional - fricas
            IntegerMod(7)
        """
        return 'IntegerMod(%s)'%self.order()

    _fricas_init_ = _axiom_init_

    def krull_dimension(self):
        """
        EXAMPLES::

            sage: Integers(18).krull_dimension()
            0
        """
        return integer.Integer(0)

    def is_noetherian(self):
        """
        EXAMPLES::

            sage: Integers(8).is_noetherian()
            True
        """
        return True

    def is_prime_field(self):
        """
        Return ``True`` if the order is prime.

        EXAMPLES::

            sage: Zmod(7).is_prime_field()
            True
            sage: Zmod(8).is_prime_field()
            False
        """
        return self.__order.is_prime()


    def _precompute_table(self):
        self._pyx_order.precompute_table(self)

    def list_of_elements_of_multiplicative_group(self):
        import sage.rings.fast_arith as a
        if self.__order <= 46340:   # todo: don't hard code
            gcd = a.arith_int().gcd_int
        elif self.__order <= 2147483647:   # todo: don't hard code
            gcd = a.arith_llong().gcd_longlong
        else:
            raise MemoryError, "creating the list would exhaust memory."
        N = self.__order
        H = [i for i in range(N) if gcd(i, N) == 1]
        return H

    def multiplicative_subgroups(self):
        r"""
        Return generators for each subgroup of
        `(\ZZ/N\ZZ)^*`.

        EXAMPLES::

            sage: Integers(5).multiplicative_subgroups()
            [[2], [4], []]
            sage: Integers(15).multiplicative_subgroups()
            [[11, 7], [4, 11], [8], [11], [14], [7], [4], []]
            sage: Integers(2).multiplicative_subgroups()
            [[]]
            sage: len(Integers(341).multiplicative_subgroups())
            80
        """
        from sage.groups.abelian_gps.abelian_group import AbelianGroup
        from sage.misc.misc import mul
        U = self.unit_gens()
        G = AbelianGroup([x.multiplicative_order() for x in U])
        rawsubs = G.subgroups()
        mysubs = []
        for G in rawsubs:
            mysubs.append([])
            for s in G.gens():
                mysubs[-1].append(mul([U[i] ** s.list()[i] for i in xrange(len(U))]))
        return mysubs

    def is_finite(self):
        """
        Return True since Z/NZ is finite for all positive N.

        EXAMPLES::

            sage: R = IntegerModRing(18)
            sage: R.is_finite()
            True
        """
        return True

    def is_integral_domain(self, proof = True):
        """
        Return True if and only if the order of self is prime.

        EXAMPLES::

            sage: Integers(389).is_integral_domain()
            True
            sage: Integers(389^2).is_integral_domain()
            False
        """
        return is_prime(self.order())

    def is_field(self, proof = True):
        """
        Return True precisely if the order is prime.

        EXAMPLES::

            sage: R = IntegerModRing(18)
            sage: R.is_field()
            False
            sage: FF = IntegerModRing(17)
            sage: FF.is_field()
            True
        """
        return self.order().is_prime()

    def field(self):
        """
        If this ring is a field, return the corresponding field as a finite
        field, which may have extra functionality and structure. Otherwise,
        raise a ValueError.

        EXAMPLES::

            sage: R = Integers(7); R
            Ring of integers modulo 7
            sage: R.field()
            Finite Field of size 7
            sage: R = Integers(9)
            sage: R.field()
            Traceback (most recent call last):
            ...
            ValueError: self must be a field
        """
        try:
            return self.__field
        except AttributeError:
            if not self.is_field():
                raise ValueError, "self must be a field"
            import constructor
            k = constructor.FiniteField(self.order())
            self.__field = k
            return k

    def _pseudo_fraction_field(self):
        """
        If self is composite, we may still want to do division by elements
        of self.

        EXAMPLES::

            sage: Integers(15).fraction_field()
            Traceback (most recent call last):
            ...
            TypeError: self must be an integral domain.
            sage: Integers(15)._pseudo_fraction_field()
            Ring of integers modulo 15
            sage: R.<x> = Integers(15)[]
            sage: (x+5)/2
            8*x + 10

        This should be very fast::

            sage: R.<x> = Integers(next_prime(10^101)*next_prime(10^100))[]
            sage: x / R.base_ring()(2)
            500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000013365000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000401*x
        """
        return self

    def multiplicative_group_is_cyclic(self):
        """
        Return True if the multiplicative group of this field is cyclic.
        This is the case exactly when the order is less than 8, a power
        of an odd prime, or twice a power of an odd prime.

        EXAMPLES::

            sage: R = Integers(7); R
            Ring of integers modulo 7
            sage: R.multiplicative_group_is_cyclic()
            True
            sage: R = Integers(9)
            sage: R.multiplicative_group_is_cyclic()
            True
            sage: Integers(8).multiplicative_group_is_cyclic()
            False
            sage: Integers(4).multiplicative_group_is_cyclic()
            True
            sage: Integers(25*3).multiplicative_group_is_cyclic()
            False

        We test that #5250 is fixed::

            sage: Integers(162).multiplicative_group_is_cyclic()
            True
        """
        n = self.order()
        if n < 8:
            return True

        if n % 4 == 0:
            return False # know n > 7, so n=4 case not a problem
        if n % 4 == 2:
            n = n // 2

        if n.is_prime_power():
            return True
        else:
            return False


    def multiplicative_generator(self):
        """
        Return a generator for the multiplicative group of this ring,
        assuming the multiplicative group is cyclic.

        Use the unit_gens function to obtain generators even in the
        non-cyclic case.

        EXAMPLES::

            sage: R = Integers(7); R
            Ring of integers modulo 7
            sage: R.multiplicative_generator()
            3
            sage: R = Integers(9)
            sage: R.multiplicative_generator()
            2
            sage: Integers(8).multiplicative_generator()
            Traceback (most recent call last):
            ...
            ValueError: multiplicative group of this ring is not cyclic
            sage: Integers(4).multiplicative_generator()
            3
            sage: Integers(25*3).multiplicative_generator()
            Traceback (most recent call last):
            ...
            ValueError: multiplicative group of this ring is not cyclic
            sage: Integers(25*3).unit_gens()
            [26, 52]
            sage: Integers(162).unit_gens()
            [83]
        """
        try:
            return self.__mult_gen
        except AttributeError:
            if self.is_field():
                a = self(self.field().multiplicative_generator())
            elif self.multiplicative_group_is_cyclic():
                v = self.unit_gens()
                if len(v) != 1:
                    raise ArithmeticError
                return v[0]
            else:
                raise ValueError, "multiplicative group of this ring is not cyclic"
            self.__mult_gen = a
            return a

    def quadratic_nonresidue(self):
        """
        Return a quadratic non-residue in self.

        EXAMPLES::

            sage: R = Integers(17)
            sage: R.quadratic_nonresidue()
            3
            sage: R(3).is_square()
            False
        """
        try:
            return self._nonresidue
        except AttributeError:
            for a in self:
                if not a.is_square():
                    self._nonresidue = a
                    return a

    def square_roots_of_one(self):
        """
        Return all square roots of 1 in self, i.e., all solutions to
        `x^2 - 1 = 0`.

        OUTPUT:


        -  ``tuple`` - the square roots of 1 in self.


        EXAMPLES::

            sage: R = Integers(2^10)
            sage: [x for x in R if x^2 == 1]
            [1, 511, 513, 1023]
            sage: R.square_roots_of_one()
            (1, 511, 513, 1023)

        ::

            sage: v = Integers(9*5).square_roots_of_one(); v
            (1, 19, 26, 44)
            sage: [x^2 for x in v]
            [1, 1, 1, 1]
            sage: v = Integers(9*5*8).square_roots_of_one(); v
            (1, 19, 71, 89, 91, 109, 161, 179, 181, 199, 251, 269, 271, 289, 341, 359)
            sage: [x^2 for x in v]
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        """
        try:
            return self.__square_roots_of_one
        except AttributeError:
            pass
        n = self.__order
        if n.is_prime_power():
            if n % 2 == 0:
                # power of 2
                if n == 2:
                    v = [self(1)]
                elif n == 4:
                    v = [self(1), self(3)]
                else: # n >= 8
                    half_ord = n//2
                    v = [self(1), self(-1), self(half_ord-1), self(half_ord+1)]
            else:
                v = [self(1), self(-1)]
        else:
            # Reduce to the prime power case.
            F = self.factored_order()
            vmod = []
            moduli = []
            for p, e in F:
                k = p**e
                R = IntegerModRing(p**e)
                w = [self(x) for x in R.square_roots_of_one()]
                vmod.append(w)
                moduli.append(k)
            # Now combine in all possible ways using the CRT
            from sage.rings.arith import CRT_basis
            basis = CRT_basis(moduli)
            from sage.misc.mrange import cartesian_product_iterator
            v = []
            for x in cartesian_product_iterator(vmod):
                # x is a specific choice of roots modulo each prime power divisor
                a = sum([basis[i]*x[i] for i in range(len(x))])
                v.append(a)
            #end for
        #end if

        v.sort()
        v = tuple(v)
        self.__square_roots_of_one = v
        return v

    def factored_order(self):
        """
        EXAMPLES::

            sage: R = IntegerModRing(18)
            sage: FF = IntegerModRing(17)
            sage: R.factored_order()
            2 * 3^2
            sage: FF.factored_order()
            17
        """
        if self.__factored_order is not None:
            return self.__factored_order
        self.__factored_order = factor(self.__order, int_=(self.__order < 2**31))
        return self.__factored_order

    def factored_unit_order(self):
        """
        Returns a list of Factorization objects, each the factorization of the
        order of the units in a `\ZZ / p^n \ZZ` component of this group (using
        the Chinese Remainder Theorem).

        EXAMPLES::

            sage: R = Integers(8*9*25*17*29)
            sage: R.factored_unit_order()
            [2^2, 2 * 3, 2^2 * 5, 2^4, 2^2 * 7]
        """
        ans = []
        from sage.structure.factorization import Factorization
        for p, e in self.factored_order():
            ans.append(Factorization([(p,e-1)]) * factor(p-1, int_=(self.__order < 2**31)))
        return ans

    def characteristic(self):
        """
        EXAMPLES::

            sage: R = IntegerModRing(18)
            sage: FF = IntegerModRing(17)
            sage: FF.characteristic()
            17
            sage: R.characteristic()
            18
        """
        return self.__order

    def _repr_(self):
        return "Ring of integers modulo %s"%self.__order

    def _latex_(self):
        return "\ZZ/%s\ZZ" % self.__order

    def modulus(self):
        r"""
        Return the polynomial `x - 1` over this ring.

        .. note::

           This function exists for consistency with the finite-field
           modulus function.

        EXAMPLES::

            sage: R = IntegerModRing(18)
            sage: R.modulus()
            x + 17
            sage: R = IntegerModRing(17)
            sage: R.modulus()
            x + 16
        """
        try:
            return self.__modulus
        except AttributeError:
            x = self['x'].gen()
            self.__modulus = x - 1
            return self.__modulus

    def order(self):
        return self.__order

    def cardinality(self):
        return self.order()

    def _pari_order(self):
        try:
            return self.__pari_order
        except AttributeError:
            self.__pari_order = pari(self.order())
            return self.__pari_order

    def _element_constructor_(self, x):
        """
        TESTS::

            sage: K2 = GF(2)
            sage: K3 = GF(3)
            sage: K8 = GF(8,'a')
            sage: K8(5)
            1
            sage: K8('a+1')
            a + 1
            sage: K8(K2(1))
            1

        The following test refers to Trac Ticket number 6468::

            sage: class foo_parent(Parent):
            ...       pass
            sage: class foo(RingElement):
            ...       def lift(self):
            ...           raise PariError
            sage: P = foo_parent()
            sage: F = foo(P)
            sage: GF(2)(F)
            Traceback (most recent call last):
            ...
            TypeError: error coercing to finite field

        The following test refers to ticket #8970::

            sage: R = Zmod(13); a = R(2)
            sage: a == R(gap(a))
            True

        """
        try:
            return integer_mod.IntegerMod(self, x)
        except (NotImplementedError, PariError):
            raise TypeError, "error coercing to finite field"
        except TypeError:
            if sage.interfaces.all.is_GapElement(x):
                from sage.interfaces.gap import intmod_gap_to_sage
                try:
                    y = intmod_gap_to_sage(x)
                    return self.coerce(y)
                except (ValueError, IndexError, TypeError), msg:
                    raise TypeError, "%s\nerror coercing to finite field"%msg
            else:
                raise


    def __iter__(self):
        """
        EXAMPLES::

            sage: R = IntegerModRing(3)
            sage: for i in R:
            ...    print i
            0
            1
            2
            sage: L = [i for i in R]
            sage: L[0].parent()
            Ring of integers modulo 3
        """
        i = 0
        order = int(self.__order)
        while i < order:
            yield self(i)
            i = i + 1

    def _coerce_map_from_(self, S):
        """
        EXAMPLES::

            sage: R = Integers(15)
            sage: f = R.coerce_map_from(Integers(450)); f
            Natural morphism:
              From: Ring of integers modulo 450
              To:   Ring of integers modulo 15
            sage: f(-1)
            14
            sage: f = R.coerce_map_from(int); f
            Native morphism:
              From: Set of Python objects of type 'int'
              To:   Ring of integers modulo 15
            sage: f(-1r)
            14
            sage: f = R.coerce_map_from(ZZ); f
            Natural morphism:
              From: Integer Ring
              To:   Ring of integers modulo 15
            sage: f(-1)
            14
            sage: f = R.coerce_map_from(Integers(10)); print f
            None
            sage: f = R.coerce_map_from(QQ); print f
            None

            sage: R = IntegerModRing(17)
            sage: a = R(3)
            sage: b = R._coerce_(3)
            sage: b
            3
            sage: a==b
            True

        This is allowed::

            sage: R(2/3)
            12

        But this is not, since there is no (canonical or not!) ring
        homomorphism from `\QQ` to `\GF{17}`.

        ::

            sage: R._coerce_(2/3)
            Traceback (most recent call last):
            ...
            TypeError: no canonical coercion from Rational Field to Ring of integers modulo 17

        We do not allow the coercion GF(p) - Z/pZ, because in case of a
        canonical isomorphism, there is a coercion map in only one
        direction, i.e., to the object in the smaller category.
        """
        if S is int:
            return integer_mod.Int_to_IntegerMod(self)
        elif S is integer_ring.ZZ:
            return integer_mod.Integer_to_IntegerMod(self)
        elif isinstance(S, IntegerModRing_generic):
            if isinstance(S, field.Field):
                return None
            try:
                return integer_mod.IntegerMod_to_IntegerMod(S, self)
            except TypeError:
                pass
        to_ZZ = integer_ring.ZZ.coerce_map_from(S)
        if to_ZZ is not None:
            return integer_mod.Integer_to_IntegerMod(self) * to_ZZ

    def __cmp__(self, other):
        """
        EXAMPLES::

            sage: Z11 = IntegerModRing(11); Z11
            Ring of integers modulo 11
            sage: Z12 = IntegerModRing(12); Z12
            Ring of integers modulo 12
            sage: Z13 = IntegerModRing(13); Z13
            Ring of integers modulo 13
            sage: F = GF(11); F
            Finite Field of size 11
            sage: Z11 == Z11, Z11 == Z12, Z11 == Z13, Z11 == F
            (True, False, False, False)
        """
        if type(other) is not type(self):   # so that GF(p) =/= Z/pZ
            return cmp(type(self), type(other))
        return cmp(self.__order, other.__order)

    # The following __unit_gens functions are here since I just factored
    # them out from the unit_gens function.  They are only called by
    # the unit_gens function.
    def __unit_gens_primecase(self, p):
        if p==2:
            return integer_mod.Mod(1,p)
        P = prime_divisors(p-1)
        ord = integer.Integer(p-1)
        one = integer_mod.Mod(1,p)
        x = 2
        while x < p:
            generator = True
            z = integer_mod.Mod(x,p)
            for q in P:
                if z**(ord//q) == one:
                    generator = False
                    break
            if generator:
                return z
            x += 1
        #end for
        assert False, "didn't find primitive root for p=%s"%p

    def __unit_gens_primepowercase(self, p, r):
        r"""
        Find smallest generator for
        `(\ZZ/p^r\ZZ)^*`.
        """
        if r==1:
            return [self.__unit_gens_primecase(p)]
        elif p==2:
            if r==1:
                return []
            elif r==2:
                return [integer_mod.Mod(-1,2**r)]
            elif r>=3:
                pr=2**r
                a = integer_mod.Mod(5, pr)
                return [integer_mod.Mod(-1,pr), a]
            assert False, "p=2, r=%s should be >=1"%r
        else:  # odd prime
            pr = p**r
            R = IntegerModRing(pr)
            x = R(self.__unit_gens_primecase(p).lift())
            n = p**(r-2)*(p-1)
            one = integer_mod.Mod(1,pr)
            for b in range(0,p):
                z = x+R(b*p)
                if z**n != one:
                    a = integer_mod.Mod(z,pr)
                    return [a]
            assert False, "p=%s, r=%s, couldn't find generator"%(p,r)

    def unit_gens(self):
        r"""
        Returns generators for the unit group `(\ZZ/N\ZZ)^*`.

        We compute the list of generators using a deterministic algorithm, so
        the generators list will always be the same. For each odd prime divisor
        of N there will be exactly one corresponding generator; if N is even
        there will be 0, 1 or 2 generators according to whether 2 divides N to
        order 1, 2 or `\ge 3`.

        INPUT: (none)

        OUTPUT:

        -  ``list`` - a list of elements of self

        EXAMPLES::

            sage: R = IntegerModRing(18)
            sage: R.unit_gens()
            [11]
            sage: R = IntegerModRing(17)
            sage: R.unit_gens()
            [3]
            sage: IntegerModRing(next_prime(10^30)).unit_gens()
            [5]
        """
        try:
            return self.__unit_gens
        except AttributeError:
            self.__unit_gens = []
        n = self.__order
        if n == 1:
            self.__unit_gens = [self(1)]
            return self.__unit_gens
        for p,r in self.factored_order():
            m = n/(p**r)
            for g in self.__unit_gens_primepowercase(p, r):
                x = g.crt(integer_mod.Mod(1,m))
                if x != 1:
                    self.__unit_gens.append(x)
        return self.__unit_gens

    def unit_group_exponent(self):
        """
        EXAMPLES::

            sage: R = IntegerModRing(17)
            sage: R.unit_group_exponent()
            16
            sage: R = IntegerModRing(18)
            sage: R.unit_group_exponent()
            6
        """
        if self.__unit_group_exponent != None:
            return self.__unit_group_exponent
        a = []
        for p, r in self.factored_order():
            if p != 2:
                a.append((p-1)*(p**(r-1)))   # phi(p**r)
            else:  # p=2
                if r==2:
                    a.append(2)
                elif r>2:
                    a.append(2**(r-2))
            #endif
        #endfor
        self.__unit_group_exponent = int(LCM(a))
        return self.__unit_group_exponent

    def unit_group_order(self):
        """
        Return the order of the unit group of this residue class ring.

        EXAMPLES;

        ::

            sage: R = Integers(500)
            sage: R.unit_group_order()
            200
        """
        return euler_phi(self.order())

    def random_element(self, bound=None):
        """
        Return a random element of this ring.

        If bound is not None, return the coercion of an integer in the
        interval [-bound, bound] into this ring.

        EXAMPLES::

            sage: R = IntegerModRing(18)
            sage: R.random_element()
            2
        """
        if not (bound is None):
            return commutative_ring.CommutativeRing.random_element(self, bound)
        a = random.randint(0,self.order()-1)
        return self(a)

    #######################################################
    # Suppose for interfaces
    #######################################################
    def _gap_init_(self):
        """
        EXAMPLES::

            sage: R = Integers(12345678900)
            sage: R
            Ring of integers modulo 12345678900
            sage: gap(R)
            (Integers mod 12345678900)
        """
        return 'ZmodnZ(%s)'%self.order()

    def _magma_init_(self, magma):
        """
        EXAMPLES::

            sage: R = Integers(12345678900)
            sage: R
            Ring of integers modulo 12345678900
            sage: magma(R)                                          # optional - magma
            Residue class ring of integers modulo 12345678900
        """
        return 'Integers(%s)'%self.order()


    def degree(self):
        """
        Return 1.

        EXAMPLE::

            sage: R = Integers(12345678900)
            sage: R.degree()
            1
        """
        return integer.Integer(1)

Zmod = IntegerModRing
Integers = IntegerModRing

# Register unpickling methods for backward compatibility.

from sage.structure.sage_object import register_unpickle_override
register_unpickle_override('sage.rings.integer_mod_ring', 'IntegerModRing_generic', IntegerModRing_generic)

## def GF(p):
##     """
##     EXAMPLES:
##         sage: F = GF(11)
##         sage: F
##         Finite field of size 11
##     """
##     if not arith.is_prime(p):
##         raise NotImplementedError, "Only prime fields currently implemented."
##     return IntegerModRing(p)

def crt(v):
    """
    INPUT: v - (list) a lift of elements of rings.IntegerMod(n), for
    various coprime moduli n.
    """
    if len(v) == 0:
        return IntegerModRing(1)(1)
    x = v[0]
    for i in range(1,len(v)):
        x = x.crt(v[i])
    return x
