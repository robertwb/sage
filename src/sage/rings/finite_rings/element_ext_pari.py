"""
Elements of Finite Fields

EXAMPLES::

    sage: K = FiniteField(2)
    sage: V = VectorSpace(K,3)
    sage: w = V([0,1,2])
    sage: K(1)*w
    (0, 1, 0)

We do some arithmetic involving a bigger field and a Conway
polynomial, i.e., we verify compatibility condition.

::

    sage: f = conway_polynomial(2,63)
    sage: K.<a> = GF(2**63, name='a', modulus=f)
    sage: n = f.degree()
    sage: m = 3;
    sage: e = (2^n - 1) / (2^m - 1)
    sage: c = a^e
    sage: conway = conway_polynomial(2,m)
    sage: conway(c) == 0
    True
"""


import operator

import sage.structure.element as element
import sage.rings.arith as arith
import sage.rings.integer_ring as integer_ring
from sage.rings.integer import Integer
import sage.rings.rational as rational
from sage.libs.pari.all import pari, pari_gen
from sage.rings.finite_rings.element_base import FinitePolyExtElement
import sage.rings.field_element as field_element
import sage.rings.finite_rings.integer_mod as integer_mod
from element_base import is_FiniteFieldElement
from sage.modules.free_module_element import FreeModuleElement
from sage.structure.dynamic_class import dynamic_class
from sage.categories.finite_fields import FiniteFields

class FiniteField_ext_pariElement(FinitePolyExtElement):
    """
    An element of a finite field.

    Create elements by first defining the finite field F, then use the
    notation F(n), for n an integer. or let a = F.gen() and write the
    element in terms of a.

    EXAMPLES::

        sage: K = FiniteField(10007^10, 'a')
        sage: a = K.gen(); a
        a
        sage: loads(a.dumps()) == a
        True
        sage: K = GF(10007)
        sage: a = K(938); a
        938
        sage: loads(a.dumps()) == a
        True

    TESTS::

        sage: K.<a> = GF(2^16)
        sage: K(0).is_zero()
        True
        sage: (a - a).is_zero()
        True
        sage: a - a
        0
        sage: a == a
        True
        sage: a - a == 0
        True
        sage: a - a == K(0)
        True
    """
    def __init__(self, parent, value, check=True):
        """
        Create element of a finite field.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: k = FiniteField_ext_pari(9,'a')
            sage: a = k(11); a
            2
            sage: a.parent()
            Finite Field in a of size 3^2
            sage: V = k.vector_space(); v = V((1,2))
            sage: k(v)
            2*a + 1

        We create elements using a list and verify that #10486 has been fixed::

            sage: k = FiniteField_ext_pari(3^11, 't')
            sage: x = k([1,0,2,1]); x
            t^3 + 2*t^2 + 1
            sage: x + x + x
            0
            sage: pari(x)
            Mod(Mod(1, 3)*a^3 + Mod(2, 3)*a^2 + Mod(1, 3), Mod(1, 3)*a^11 + Mod(2, 3)*a^2 + Mod(1, 3))

        If the list is longer than the degree, we just get the result
        modulo the modulus::

            sage: R.<a> = PolynomialRing(GF(5))
            sage: k = FiniteField_ext_pari(5^2, 't', modulus=a^2-2)
            sage: x = k([0,0,0,1]); x
            2*t
            sage: pari(x)
            Mod(Mod(2, 5)*a, Mod(1, 5)*a^2 + Mod(3, 5))
        """
        field_element.FieldElement.__init__(self, parent)
        self.__class__ = dynamic_FiniteField_ext_pariElement
        if isinstance(value, str):
            raise TypeError, "value must not be a string"
        if not check:
            if not value:  # see comment below about this workaround
                self.__value = pari(0).Mod(parent._pari_modulus())*parent._pari_one()
            else:
                self.__value = value
            return
        try:
            if isinstance(value, pari_gen):
                try:
                    # In some cases we get two different versions of
                    # the 0 element of a finite field.  This has to do
                    # with how PARI's Mod function works -- it treats
                    # 0 differently.  In particular, if value is a a
                    # pari t_POLMOD that is 0, modding it simply
                    # doesn't work correctly.  We fix this by changing
                    # the value in the 0 case to the standard pari 0,
                    # which works correctly.  Note -- probably all
                    # this code should be replaced by much faster
                    # finite field arithmetic programmed against NTL.
                    if not value:
                        value = pari(0)
                    if value.type() == "t_POLMOD":
                        self.__value = value * parent._pari_one()
                    else:
                        self.__value = value.Mod(parent._pari_modulus())*parent._pari_one()
                except RuntimeError:
                    raise TypeError, "no possible coercion implemented"
            elif isinstance(value, FiniteField_ext_pariElement):
                if parent != value.parent():
                    raise TypeError, "no coercion implemented"
                else:
                    self.__value = value.__value
            elif isinstance(value, FreeModuleElement):
                if parent.vector_space() != value.parent():
                    raise TypeError, "e.parent must match self.vector_space"
                self.__value = pari(0).Mod(parent._pari_modulus())*parent._pari_one()
                for i in range(len(value)):
                    self.__value = self.__value + pari(int(value[i])).Mod(parent._pari_modulus())*pari("a^%s"%i)
            elif isinstance(value, list):
                # Make the list into a polynomial with variable "a",
                # multiply it with _pari_one (which equals Mod(1,p)) to
                # fix the characteristic and then mod out by the modulus.
                # See #10486.
                self.__value = (pari(value).Polrev("a") * parent._pari_one()).Mod(parent._pari_modulus())
            else:
                try:
                    self.__value = pari(value).Mod(parent._pari_modulus())*parent._pari_one()
                except RuntimeError:
                    raise TypeError, "no coercion implemented"

        except (AttributeError, TypeError):
            raise TypeError, "unable to coerce"

    def __hash__(self):
        return hash(self.polynomial())

    def polynomial(self):
        """
        Elements of a finite field are represented as a polynomial modulo a
        modulus. This function returns the representing polynomial as an
        element of the polynomial ring over the prime finite field, with
        the same variable as the finite field.

        EXAMPLES:

        The default variable is a::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: k = FiniteField_ext_pari(3**2,'a')
            sage: k.gen().polynomial()
            a

        The variable can be any string.

        ::

            sage: k = FiniteField(3**4, "alpha")
            sage: a = k.gen()
            sage: a.polynomial()
            alpha
            sage: (a**2 + 1).polynomial()
            alpha^2 + 1
            sage: (a**2 + 1).polynomial().parent()
            Univariate Polynomial Ring in alpha over Finite Field of size 3
        """
        return self.parent().polynomial_ring()(self.__value.lift())

    def is_square(self):
        """
        Returns True if and only if this element is a perfect square.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: k = FiniteField_ext_pari(3**2, 'a')
            sage: a = k.gen()
            sage: a.is_square()
            False
            sage: (a**2).is_square()
            True
            sage: k = FiniteField_ext_pari(2**2,'a')
            sage: a = k.gen()
            sage: (a**2).is_square()
            True
            sage: k = FiniteField_ext_pari(17**5,'a'); a = k.gen()
            sage: (a**2).is_square()
            True
            sage: a.is_square()
            False

        ::

            sage: k(0).is_square()
            True
        """
        K = self.parent()
        if K.characteristic() == 2:
            return True
        n = K.order() - 1
        a = self**(n // 2)
        return a == 1 or a == 0

    def square_root(self, extend=False, all=False):
        """
        The square root function.

        INPUT:


        -  ``extend`` - bool (default: True); if True, return a
           square root in an extension ring, if necessary. Otherwise, raise a
           ValueError if the root is not in the base ring. Warning: this
           option is not implemented!

        -  ``all`` - bool (default: False); if True, return all
           square roots of self, instead of just one.


        .. warning::

           The 'extend' option is not implemented (yet).

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: F = FiniteField_ext_pari(7^2, 'a')
            sage: F(2).square_root()
            4
            sage: F(3).square_root()
            5*a + 1
            sage: F(3).square_root()**2
            3
            sage: F(4).square_root()
            5
            sage: K = FiniteField_ext_pari(7^3, 'alpha')
            sage: K(3).square_root()
            Traceback (most recent call last):
            ...
            ValueError: must be a perfect square.
        """
        if extend:
            raise NotImplementedError
        R = self.parent()['x']
        f = R([-self, 0, 1])
        g = f.factor()
        if len(g) == 2 or g[0][1] == 2:
            if all:
                return [-g[0][0][0], g[0][0][0]]
            else:
                return -g[0][0][0]
        if all:
            return []
        else:
            raise ValueError, "must be a perfect square."

    def sqrt(self, extend=False, all = False):
        """
        See self.square_root().

        INPUT:


        -  ``extend`` - ignored
        """
        return self.square_root(extend=extend, all=all)

    def rational_reconstruction(self):
        """
        If the parent field is a prime field, uses rational reconstruction
        to try to find a lift of this element to the rational numbers.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: k = GF(97)
            sage: a = k(RationalField()('2/3'))
            sage: a
            33
            sage: a.rational_reconstruction()
            2/3
        """
        if self.parent().degree() != 1:
            raise ArithmeticError, "finite field must be prime"
        t = arith.rational_reconstruction(int(self), self.parent().characteristic())
        if t == None or t[1] == 0:
            raise ZeroDivisionError, "unable to compute rational reconstruction"
        return rational.Rational((t[0],t[1]))

    def multiplicative_order(self):
        r"""
        Returns the *multiplicative* order of this element, which must be
        nonzero.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: a = FiniteField_ext_pari(5**3, 'a').0
            sage: a.multiplicative_order()
            124
            sage: a**124
            1
        """
        try:
            return self.__multiplicative_order
        except AttributeError:
            if self.is_zero():
                raise ArithmeticError("Multiplicative order of 0 not defined.")
            n = self.parent().order() - 1
            order = 1
            for p, e in arith.factor(n):
                # Determine the power of p that divides the order.
                a = self**(n//(p**e))
                while a != 1:
                    order *= p
                    a = a**p
            self.__multiplicative_order = order
            return order

    def __copy__(self):
        """
        Return a copy of this element.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: k = FiniteField_ext_pari(3**3,'a')
            sage: a = k(5)
            sage: a
            2
            sage: copy(a)
            2
            sage: b = copy(a)
            sage: a == b
            True
            sage: a is b
            False
            sage: a is a
            True
        """
        return FiniteField_ext_pariElement(self.parent(), self.__value, check=False)

    def _pari_(self, var=None):
        """
        Return PARI object corresponding to this finite field element.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: k = FiniteField_ext_pari(3**3, 'a')
            sage: a = k.gen()
            sage: b = a**2 + 2*a + 1
            sage: b._pari_()
            Mod(Mod(1, 3)*a^2 + Mod(2, 3)*a + Mod(1, 3), Mod(1, 3)*a^3 + Mod(2, 3)*a + Mod(1, 3))

        Looking at the PARI representation of a finite field element, it's
        no wonder people find PARI difficult to work with directly. Compare
        our representation::

            sage: b
            a^2 + 2*a + 1
            sage: b.parent()
            Finite Field in a of size 3^3
        """
        if var is None:
            var = self.parent().variable_name()
        if var == 'a':
            return self.__value
        else:
            return self.__value.subst('a', var)

    def _pari_init_(self):
        return str(self.__value)

    def _magma_init_(self, magma):
        """
        Return a string representation of self that Magma can understand.

        EXAMPLES::

            sage: GF(7)(3)._magma_init_(magma)                 # optional - magma
            'GF(7)!3'
        """
        km = magma(self.parent())
        vn = km.gen(1).name()
        return ("%s"%(self.__value.lift().lift())).replace('a',vn)

    def _gap_init_(self):
        """
        Supports returning corresponding GAP object. This can be slow since
        non-prime GAP finite field elements are represented as powers of a
        generator for the multiplicative group, so the discrete log problem
        must be solved.

        .. note::

           The order of the parent field must be `\leq 65536`.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: F = FiniteField_ext_pari(8,'a')
            sage: a = F.multiplicative_generator()
            sage: gap(a)
            Z(2^3)
            sage: b = F.multiplicative_generator()
            sage: a = b^3
            sage: gap(a)
            Z(2^3)^3
            sage: gap(a^3)
            Z(2^3)^2

        You can specify the instance of the Gap interpreter that is used::

            sage: F = FiniteField_ext_pari(next_prime(200)^2, 'a')
            sage: a = F.multiplicative_generator ()
            sage: a._gap_ (gap)
            Z(211^2)
            sage: (a^20)._gap_(gap)
            Z(211^2)^20

        Gap only supports relatively small finite fields.

        ::

            sage: F = FiniteField_ext_pari(next_prime(1000)^2, 'a')
            sage: a = F.multiplicative_generator ()
            sage: gap._coerce_(a)
            Traceback (most recent call last):
            ...
            TypeError: order must be at most 65536
        """
        F = self.parent()
        if F.order() > 65536:
            raise TypeError, "order must be at most 65536"

        if self == 0:
            return '0*Z(%s)'%F.order()
        assert F.degree() > 1
        g = F.multiplicative_generator()
        n = self.log(g)
        return 'Z(%s)^%s'%(F.order(), n)

    def _repr_(self):
        return ("%s"%(self.__value.lift().lift())).replace('a',self.parent().variable_name())

    def __compat(self, other):
        if self.parent() != other.parent():
            raise TypeError, "Parents of finite field elements must be equal."

    def _add_(self, right):
        return FiniteField_ext_pariElement(self.parent(), self.__value + right.__value, check=False)

    def _sub_(self, right):
        return FiniteField_ext_pariElement(self.parent(), self.__value - right.__value, check=False)

    def _mul_(self, right):
        return FiniteField_ext_pariElement(self.parent(), self.__value * right.__value, check=False)

    def _div_(self, right):
        if right.__value == 0:
            raise ZeroDivisionError
        return FiniteField_ext_pariElement(self.parent(), self.__value / right.__value, check=False)

    def __int__(self):
        try:
            return int(self.__value.lift().lift())
        except ValueError:
            raise TypeError, "cannot coerce to int"

    def _integer_(self, ZZ=None):
        return self.lift()

    def __long__(self):
        try:
            return long(self.__value.lift().lift())
        except ValueError:
            raise TypeError, "cannot coerce to long"

    def __float__(self):
        try:
            return float(self.__value.lift().lift())
        except ValueError:
            raise TypeError, "cannot coerce to float"

    # commented out because PARI (used for .__value) prints
    # out crazy warnings when the exponent is LARGE -- this
    # is even a problem in gp!!!
    # (Commenting out causes this to use a generic algorithm)
    #def __pow__(self, _right):
    #    right = int(_right)
    #    if right != _right:
    #         raise ValueError
    #    return FiniteField_ext_pariElement(self.parent(), self.__value**right, check=False)

    def __neg__(self):
        return FiniteField_ext_pariElement(self.parent(), -self.__value, check=False)

    def __pos__(self):
        return self

    def __abs__(self):
        raise ArithmeticError, "absolute value not defined"

    def __invert__(self):
        """
        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: a = FiniteField_ext_pari(9, 'a').gen()
            sage: ~a
            a + 2
            sage: (a+1)*a
            2*a + 1
        """

        if self.__value == 0:
            raise ZeroDivisionError, "Cannot invert 0"
        return FiniteField_ext_pariElement(self.parent(), ~self.__value, check=False)

    def lift(self):
        """
        If this element lies in a prime finite field, return a lift of this
        element to an integer.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: k = GF(next_prime(10**10))
            sage: a = k(17)/k(19)
            sage: b = a.lift(); b
            7894736858
            sage: b.parent()
            Integer Ring
        """
        return integer_ring.IntegerRing()(self.__value.lift().lift())


    def __cmp__(self, other):
        """
        Compare an element of a finite field with other. If other is not an
        element of a finite field, an attempt is made to coerce it so it is
        one.

        EXAMPLES::

            sage: from sage.rings.finite_rings.finite_field_ext_pari import FiniteField_ext_pari
            sage: a = FiniteField_ext_pari(3**3, 'a').gen()
            sage: a == 1
            False
            sage: a**0 == 1
            True
            sage: a == a
            True
            sage: a < a**2
            True
            sage: a > a**2
            False
        """
        return cmp(self.__value, other.__value)

    def log(self, base):
        """
        Return `x` such that `b^x = a`, where `x`
        is `a` and `b` is the base.

        INPUT:


        -  ``self`` - finite field element

        -  ``b`` - finite field element that generates the
           multiplicative group.


        OUTPUT: Integer `x` such that `a^x = b`, if it
        exists. Raises a ValueError exception if no such `x`
        exists.

        EXAMPLES::

            sage: F = GF(17)
            sage: F(3^11).log(F(3))
            11
            sage: F = GF(113)
            sage: F(3^19).log(F(3))
            19
            sage: F = GF(next_prime(10000))
            sage: F(23^997).log(F(23))
            997

        ::

            sage: F = FiniteField(2^10, 'a')
            sage: g = F.gen()
            sage: b = g; a = g^37
            sage: a.log(b)
            37
            sage: b^37; a
            a^8 + a^7 + a^4 + a + 1
            a^8 + a^7 + a^4 + a + 1

        AUTHORS:

        - David Joyner and William Stein (2005-11)
        """
        from  sage.groups.generic import discrete_log

        b = self.parent()(base)
        # TODO: This function is TERRIBLE!
        return discrete_log(self, b)

dynamic_FiniteField_ext_pariElement = None
def _late_import():
    global dynamic_FiniteField_ext_pariElement
    dynamic_FiniteField_ext_pariElement = dynamic_class("%s_with_category"%FiniteField_ext_pariElement.__name__, (FiniteField_ext_pariElement, FiniteFields().element_class), doccls=FiniteField_ext_pariElement)

from sage.structure.sage_object import register_unpickle_override
register_unpickle_override('sage.rings.finite_field_element', 'FiniteField_ext_pariElement', FiniteField_ext_pariElement)
