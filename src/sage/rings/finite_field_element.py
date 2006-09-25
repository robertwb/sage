"""
Elements of Finite Fields

EXAMPLES:
    sage: K = FiniteField(2)
    sage: V = VectorSpace(K,3)
    sage: w = V([0,1,2])
    sage: K(1)*w
    (0, 1, 0)
"""


import operator

import sage.structure.element as element
import finite_field
import arith
import integer_ring
from integer import Integer
import rational
import polynomial_ring
from sage.libs.all import pari, pari_gen
from sage.rings.coerce import bin_op
import field_element


class FiniteFieldElement(field_element.FieldElement):
    """
    An element of a finite field.

    Create elements by first defining the finite field F, then use
    the notation F(n), for n an integer. or let a = F.gen() and
    write the element in terms of a.

    EXAMPLES:
        sage: K = GF(10007^10, 'a')
        sage: a = K.gen(); a
        a
        sage: loads(a.dumps()) == a
        True
        sage: K = GF(10007)
        sage: a = K(938); a
        938
        sage: loads(a.dumps()) == a
        True
    """
    def __init__(self, parent, value):
        """
        Create element of a finite field.

        EXAMPLES:
            sage: k = GF(9)
            sage: a = k(11); a
            2
            sage: a.parent()
            Finite Field in a of size 3^2
        """
        field_element.FieldElement.__init__(self, parent)
        self.__parent = parent
        if isinstance(value, str):
            raise TypeError, "value must not be a string"
        try:
            if isinstance(value, pari_gen):
                if value.type()[-3:] == "MOD" :
                    self.__value = value
                else:
                    try:
                        self.__value = value.Mod(parent._pari_modulus())*parent._pari_one()
                    except RuntimeError:
                        raise TypeError, "no possible coercion implemented"
                return
            elif isinstance(value, FiniteFieldElement):
                if parent != value.parent():
                    raise TypeError, "no coercion implemented"
                else:
                    self.__value = value.__value
                    return
            try:
                self.__value = pari(value).Mod(parent._pari_modulus())*parent._pari_one()
            except RuntimeError:
                raise TypeError, "no coercion implemented"

        except (AttributeError, TypeError):
            raise TypeError, "unable to coerce"

    def polynomial(self):
        """
        Elements of a finite field are represented as a polynomial
        modulo a modulus.  This functions returns the representating
        polynomial as an element of the polynomial ring over the
        prime finite field, with the same variable as the finite field.

        EXAMPLES:
        The default variable is a:
            sage: k = GF(3**2)
            sage: k.gen().polynomial()
            a

        The variable can be any string.
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

        EXAMPLES:
            sage: k = GF(3**2)
            sage: a = k.gen()
            sage: a.is_square()
            False
            sage: (a**2).is_square()
            True
            sage: k = GF(2**2)
            sage: a = k.gen()
            sage: (a**2).is_square()
            True
            sage: k = GF(17**5); a = k.gen()
            sage: (a**2).is_square()
            True
            sage: a.is_square()
            False
        """
        K = self.parent()
        if K.characteristic() == 2:
            return True
        n = K.order() - 1
        a = self**(n / 2)
        return a == 1

    def square_root(self):
        """
        Return a square root of this finite field element in its
        finite field, if there is one.  Otherwise, raise a ValueError.

        EXAMPLES:
          sage: F = GF(7^2)
          sage: F(2).square_root()
          3
          sage: F(3).square_root()
          2*a + 6
          sage: F(3).square_root()**2
          3
          sage: F(4).square_root()
          2
          sage: K = GF(7^3)
          sage: K(3).square_root()
          Traceback (most recent call last):
          ...
          ValueError: must be a perfect square.

        """
        R = polynomial_ring.PolynomialRing(self.parent())
        f = R([-self, 0, 1])
        g = f.factor()
        if len(g) == 2 or g[0][1] == 2:
            return -g[0][0][0]
        raise ValueError, "must be a perfect square."

    def sqrt(self):
        """
        See self.square_root().
        """
        return self.square_root()


    def rational_reconstruction(self):
        """
        If the parent field is a prime field, uses rational reconstruction to
        try to find a lift of this element to the rational numbers.

        EXAMPLES:
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
        Returns the \emph{multiplicative} order of this element, which
        must be nonzero.

        EXAMPLES:
            sage: a = GF(5**3, 'a').0
            sage: a.multiplicative_order()
            124
            sage: a**124
            1
        """
        try:
            return self.__multiplicative_order
        except AttributeError:
            if self.is_zero():
                return ArithmeticError, "Multiplicative order of 0 not defined."
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

    def copy(self):
        """
        Return a copy of this element.

        EXAMPLES:
            sage: k = GF(3**3)
            sage: a = k(5)
            sage: a
            2
            sage: a.copy()
            2
            sage: b = a.copy()
            sage: a == b
            True
            sage: a is b
            False
            sage: a is a
            True
        """
        return FiniteFieldElement(self.__parent, self.__value)

    def _pari_(self):
        """
        Return PARI object corresponding to this finite field element.

        EXAMPLES:
            sage: k = GF(3**3)
            sage: a = k.gen()
            sage: b = a**2 + 2*a + 1
            sage: b._pari_()
            Mod(Mod(1, 3)*a^2 + Mod(2, 3)*a + Mod(1, 3), Mod(1, 3)*a^3 + Mod(2, 3)*a + Mod(1, 3))

        Looking at the PARI representation of a finite field element, it's no wonder people
        find PARI difficult to work with directly.  Compare our representation:

            sage: b
            a^2 + 2*a + 1
            sage: b.parent()
            Finite Field in a of size 3^3
        """
        return self.__value

    def _pari_init_(self):
        return str(self.__value)

    def _gap_init_(self):
        """
        Supports returning corresponding GAP object.  This can be slow
        since non-prime GAP finite field elements are represented as
        powers of a generator for the multiplicative group, so the
        discrete log problem must be solved.

        \note{The order of the parent field must be $\leq 65536$.}


        EXAMPLES:
            sage: F = GF(8)
            sage: a = F.multiplicative_generator()
            sage: gap(a)
            Z(2^3)
            sage: b = F.multiplicative_generator()
            sage: a = b^3
            sage: gap(a)
            Z(2^3)^3
            sage: gap(a^3)
            Z(2^3)^2

        You can specify the instance of the Gap interpreter that is used:

            sage: F = GF(next_prime(200)^2)
            sage: a = F.multiplicative_generator ()
            sage: a._gap_ (gap)
            Z(211^2)
            sage: (a^20)._gap_(gap)
            Z(211^2)^20

        Gap only supports relatively small finite fields.
            sage: F = GF(next_prime(1000)^2)
            sage: a = F.multiplicative_generator ()
            sage: gap(a)
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
        n = g.log(self)
        return 'Z(%s)^%s'%(F.order(), n)

    def charpoly(self):
        """
        Returns the characteristic polynomial of this element.

        EXAMPLES:
            sage: k = GF(3**3)
            sage: a = k.gen()
            sage: a.charpoly()
            x^3 + 2*x + 1
            sage: k.modulus()
            x^3 + 2*x + 1
            sage: b = a**2 + 1
            sage: b.charpoly()
            x^3 + x^2 + 2*x + 1
        """
        R = polynomial_ring.PolynomialRing(self.parent().prime_subfield())
        return R(self.__value.charpoly().lift())

    def trace(self):
        """
        Returns the trace of this element.

        EXAMPLES:
            sage: k = GF(3**3); a = k.gen()
            sage: b = a**2 + 2
            sage: b.charpoly()
            x^3 + x^2 + 2
            sage: b.trace()
            2
            sage: b.norm()
            2
        """
        return self.parent().prime_subfield()(self.__value.trace().lift())

    def norm(self):
        """
        Returns the norm of this element, which is the constant term
        of the characteristic polynomial, i.e., the determinant of left
        multiplication.

        EXAMPLES:
            sage: k = GF(3**3); a = k.gen()
            sage: b = a**2 + 2
            sage: b.charpoly()
            x^3 + x^2 + 2
            sage: b.trace()
            2
            sage: b.norm()
            2
        """
        return self.charpoly()[0]

    def log(self, a):
        """
        Return $x$ such that $b^x = a$, where $b$ is self.

        INPUT:
            self, a are elements of a finite field.

        OUTPUT:
            Integer $x$ such that $a^x = b$, if it exists.
            Raises a ValueError exception if no such $x$ exists.

        EXAMPLES:
            sage: F = GF(17)
            sage: F(2).log(F(8))
            3
            sage: F = GF(113)
            sage: F(2).log(F(81))
            19
            sage: F = GF(next_prime(10000))
            sage: F(23).log(F(8111))
            8393

            sage: F = GF(2^10)
            sage: g = F.gen()
            sage: b = g; a = g^37
            sage: b.log(a)
            37
            sage: b^37; a
            a^8 + a^7 + a^4 + a + 1
            a^8 + a^7 + a^4 + a + 1

        AUTHOR: David Joyner and William Stein (2005-11)
        """
        q = (self.parent()).order() - 1
        return arith.discrete_log_generic(self, a, q)

    def order(self):
        """
        Return the additive order of this finite field element.
        """
        if self.is_zero():
            return Integer(1)
        return self.parent().characteristic()

    def _repr_(self):
        return ("%s"%(self.__value.lift().lift())).replace('a',self.parent().variable_name())

    def _latex_(self):
        """
        EXAMPLES:
            sage: print latex(Set(GF(9,'z')))
            \left\{2z + 2, 2z + 1, 2z, 1, 0, 2, z, z + 1, z + 2\right\}
        """
        return self.polynomial()._latex_()

    def __compat(self, other):
        if self.parent() != other.parent():
            raise TypeError, "Parents of finite field elements must be equal."

    def __add__(self, right):
        if not isinstance(right, FiniteFieldElement):
            return bin_op(self, right, operator.add)
        self.__compat(right)
        return FiniteFieldElement(self.__parent, self.__value + right.__value)

    def __sub__(self, right):
        if not isinstance(right, FiniteFieldElement):
            return bin_op(self, right, operator.sub)
        self.__compat(right)
        return FiniteFieldElement(self.__parent, self.__value - right.__value)

    def __mul__(self, right):
        if not isinstance(right, FiniteFieldElement):
            return bin_op(self, right, operator.mul)
        self.__compat(right)
        return FiniteFieldElement(self.__parent, self.__value * right.__value)

    def __div__(self, right):
        if not isinstance(right, FiniteFieldElement):
            return bin_op(self, right, operator.div)
        self.__compat(right)
        if right.__value == 0:
            raise ZeroDivisionError
        return FiniteFieldElement(self.__parent, self.__value / right.__value)

    def __int__(self):
        try:
            return int(self.__value.lift().lift())
        except ValueError:
            raise TypeError, "cannot coerce to int"

    def _integer_(self):
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

    def __rdiv__(self, left):
        return self.parent()(left)/self

    # commented out because PARI (used for .__value) prints
    # out crazy warnings when the exponent is LARGE -- this
    # is even a problem in gp!!!
    # (Commenting out causes this to use a generic algorithm)
    #def __pow__(self, right):
    #    right = int(right)
    #    return FiniteFieldElement(self.__parent, self.__value**right)

    def __neg__(self):
        return FiniteFieldElement(self.__parent, -self.__value)

    def __pos__(self):
        return self

    def __abs__(self):
        raise ArithmeticError, "absolute value not defined"

    def __invert__(self):
        """
        EXAMPLES:
            sage: k = GF(9); a = k.gen()
            sage: ~a
            a + 2
            sage: (a+1)*a
            2*a + 1
        """

        if self.__value == 0:
            raise ZeroDivisionError, "Cannot invert 0"
        return FiniteFieldElement(self.__parent, ~self.__value)

    def lift(self):
        """
        If this element lies in a prime finite field, return a lift of this
        element to an integer.

        EXAMPLES:
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

        Compare an element of a finite field with other.  If other is
        not an element of a finite field, an attempt is made to coerce
        it so it is one.

        EXAMPLES:
            sage: k = GF(3**3); a = k.gen()
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
        if self is other: return 0
        if not isinstance(other, FiniteFieldElement):
            try:
                other = self.parent()(other)
            except TypeError:
                return -1
        #if self.parent() != other.parent():
        #    return -1
        if self.__value == other.__value:
            return 0
        return -1
