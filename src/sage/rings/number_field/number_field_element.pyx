"""
Number Field Elements

AUTHORS:
    -- William Stein version before it got cython'd
    -- Joel B. Mohler (2007-03-09): First reimplementation into cython
    -- William Stein (2007-09-04): add doctests
    -- Robert Bradshaw (2007-09-15): specialized classes for relative and absolute elements
"""

# TODO -- relative extensions need to be completely rewritten, so one
# can get easy access to representation of elements in their relative
# form.  Functions like matrix below can't be done until relative
# extensions are re-written this way.  Also there needs to be class
# hierarchy for number field elements, integers, etc.  This is a
# nontrivial project, and it needs somebody to attack it.  I'm amazed
# how long this has gone unattacked.

# Relative elements need to be a derived class or something.  This is
# terrible as it is now.

#*****************************************************************************
#       Copyright (C) 2004, 2007 William Stein <wstein@gmail.com>
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

import operator

include '../../ext/interrupt.pxi'
include '../../ext/python_int.pxi'
include "../../ext/stdsage.pxi"
cdef extern from *:
    # TODO: move to stdsage.pxi
    object PY_NEW_SAME_TYPE(object o)

import sage.rings.field_element
import sage.rings.infinity
import sage.rings.polynomial.polynomial_element
import sage.rings.polynomial.polynomial_ring
import sage.rings.rational_field
import sage.rings.rational
import sage.rings.integer_ring
import sage.rings.integer
import sage.rings.arith

import number_field

from sage.libs.ntl.ntl_ZZ cimport ntl_ZZ
from sage.libs.ntl.ntl_ZZX cimport ntl_ZZX
from sage.rings.integer_ring cimport IntegerRing_class

from sage.libs.all import pari_gen
from sage.libs.pari.gen import PariError

QQ = sage.rings.rational_field.QQ
ZZ = sage.rings.integer_ring.ZZ
Integer_sage = sage.rings.integer.Integer


def is_NumberFieldElement(x):
    """
    Return True if x is of type NumberFieldElement, i.e., an
    element of a number field.

    EXAMPLES:
        sage: is_NumberFieldElement(2)
        False
        sage: k.<a> = NumberField(x^7 + 17*x + 1)
        sage: is_NumberFieldElement(a+1)
        True
    """
    return PY_TYPE_CHECK(x, NumberFieldElement)

def __create__NumberFieldElement_version0(parent, poly):
    """
    Used in unpickling elements of number fields.

    EXAMPLES:
    Since this is just used in unpickling, we unpickle.

        sage: k.<a> = NumberField(x^3 - 2)
        sage: loads(dumps(a+1)) == a + 1
        True
    """
    return NumberFieldElement(parent, poly)

def __create__NumberFieldElement_version1(parent, cls, poly):
    """
    Used in unpickling elements of number fields.

    EXAMPLES:
    Since this is just used in unpickling, we unpickle.

        sage: k.<a> = NumberField(x^3 - 2)
        sage: loads(dumps(a+1)) == a + 1
        True
    """
    return cls(parent, poly)

cdef class NumberFieldElement(FieldElement):
    """
    An element of a number field.

    EXAMPLES:
        sage: k.<a> = NumberField(x^3 + x + 1)
        sage: a^3
        -a - 1
    """
    cdef NumberFieldElement _new(self):
        """
        Quickly creates a new initialized NumberFieldElement with the
        same parent as self.
        """
        cdef NumberFieldElement x
        x = <NumberFieldElement>PY_NEW_SAME_TYPE(self)
        x._parent = self._parent
        return x

    def __init__(self, parent, f):
        """
        INPUT:
            parent -- a number field
            f -- defines an element of a number field.

        EXAMPLES:
        The following examples illustrate creation of elements of
        number fields, and some basic arithmetic.

        First we define a polynomial over Q.
            sage: R.<x> = PolynomialRing(QQ)
            sage: f = x^2 + 1

        Next we use f to define the number field.
            sage: K.<a> = NumberField(f); K
            Number Field in a with defining polynomial x^2 + 1
            sage: a = K.gen()
            sage: a^2
            -1
            sage: (a+1)^2
            2*a
            sage: a^2
            -1
            sage: z = K(5); 1/z
            1/5

        We create a cube root of 2.
            sage: K.<b> = NumberField(x^3 - 2)
            sage: b = K.gen()
            sage: b^3
            2
            sage: (b^2 + b + 1)^3
            12*b^2 + 15*b + 19

        This example illustrates save and load:
            sage: K.<a> = NumberField(x^17 - 2)
            sage: s = a^15 - 19*a + 3
            sage: loads(s.dumps()) == s
            True
        """
        sage.rings.field_element.FieldElement.__init__(self, parent)

        cdef ZZ_c coeff
        if isinstance(f, (int, long, Integer_sage)):
            # set it up and exit immediately
            # fast pathway
            (<Integer>ZZ(f))._to_ZZ(&coeff)
            ZZX_SetCoeff( self.__numerator, 0, coeff )
            conv_ZZ_int( self.__denominator, 1 )
            return

        elif isinstance(f, NumberFieldElement):
            if PY_TYPE(self) is PY_TYPE(f):
                self.__numerator = (<NumberFieldElement>f).__numerator
                self.__denominator = (<NumberFieldElement>f).__denominator
                return
            else:
                f = f.polynomial()

        ppr = parent.polynomial_ring()
        if isinstance(parent, number_field.NumberField_relative):
            ppr = parent.base_field().polynomial_ring()

        if isinstance(f, pari_gen):
            f = f.lift()
            f = ppr(f)
        if not isinstance(f, sage.rings.polynomial.polynomial_element.Polynomial):
            f = ppr(f)
        if f.degree() >= parent.absolute_degree():
            if f.variable_name() != 'x':
                f = f.change_variable_name('x')
            if isinstance(parent, number_field.NumberField_relative):
                f %= parent.absolute_polynomial()
            else:
                f %= parent.polynomial()

        # Set Denominator
        den = f.denominator()
        (<Integer>ZZ(den))._to_ZZ(&self.__denominator)

        cdef long i
        num = f * den
        for i from 0 <= i <= num.degree():
            (<Integer>ZZ(num[i]))._to_ZZ(&coeff)
            ZZX_SetCoeff( self.__numerator, i, coeff )

    def __new__(self, parent = None, f = None):
        ZZX_construct(&self.__numerator)
        ZZ_construct(&self.__denominator)

    def __dealloc__(self):
        ZZX_destruct(&self.__numerator)
        ZZ_destruct(&self.__denominator)

    def _lift_cyclotomic_element(self, new_parent):
        """
        Creates an element of the passed field from this field.  This
        is specific to creating elements in a cyclotomic field from
        elements in another cyclotomic field.  This function aims to
        make this common coercion extremely fast!

        EXAMPLES:
            sage: C.<zeta5>=CyclotomicField(5)
            sage: CyclotomicField(10)(zeta5+1)  # The function _lift_cyclotomic_element does the heavy lifting in the background
            zeta10^2 + 1
            sage: (zeta5+1)._lift_cyclotomic_element(CyclotomicField(10))  # There is rarely a purpose to call this function directly
            zeta10^2 + 1

        AUTHOR:
            Joel B. Mohler
        """
        # Right now, I'm a little confused why quadratic extension fields have a zeta_order function
        # I would rather they not have this function since I don't want to do this isinstance check here.
        if not isinstance(self.parent(), number_field.NumberField_cyclotomic) or not isinstance(new_parent, number_field.NumberField_cyclotomic):
            raise TypeError, "The field and the new parent field must both be cyclotomic fields."

        try:
            small_order = self.parent().zeta_order()
            large_order = new_parent.zeta_order()
        except AttributeError:
            raise TypeError, "The field and the new parent field must both be cyclotomic fields."

        try:
            _rel = ZZ(large_order / small_order)
        except TypeError:
            raise TypeError, "The zeta_order of the new field must be a multiple of the zeta_order of the original."

        cdef NumberFieldElement x = <NumberFieldElement>PY_NEW_SAME_TYPE(self)
        x._parent = <ParentWithBase>new_parent
        x.__denominator = self.__denominator
        cdef ZZX_c result
        cdef ZZ_c tmp
        cdef int i
        cdef int rel = _rel
        cdef ntl_ZZX _num
        cdef ntl_ZZ _den
        _num, _den = new_parent.polynomial_ntl()
        for i from 0 <= i <= ZZX_deg(self.__numerator):
            tmp = ZZX_coeff(self.__numerator, i)
            ZZX_SetCoeff(result, i*rel, tmp)
        rem_ZZX(x.__numerator, result, _num.x)
        return x

    def __reduce__(self):
        """
        Used in pickling number field elements.

        EXAMPLES:
            sage: k.<a> = NumberField(x^3 - 17*x^2 + 1)
            sage: t = a.__reduce__(); t
            (<built-in function __create__NumberFieldElement_version1>, (Number Field in a with defining polynomial x^3 - 17*x^2 + 1, <type 'sage.rings.number_field.number_field_element.NumberFieldElement_absolute'>, x))
            sage: t[0](*t[1]) == a
            True
        """
        return __create__NumberFieldElement_version1, \
               (self.parent(), type(self), self.polynomial())

    def __repr__(self):
        """
        String representation of this number field element,
        which is just a polynomial in the generator.

        EXAMPLES:
            sage: k.<a> = NumberField(x^2 + 2)
            sage: b = (2/3)*a + 3/5
            sage: b.__repr__()
            '2/3*a + 3/5'
        """
        x = self.polynomial()
        return str(x).replace(x.parent().variable_name(),self.parent().variable_name())

    def _im_gens_(self, codomain, im_gens):
        """
        This is used in computing homomorphisms between number fields.

        EXAMPLES:
            sage: k.<a> = NumberField(x^2 - 2)
            sage: m.<b> = NumberField(x^4 - 2)
            sage: phi = k.hom([b^2])
            sage: phi(a+1)
            b^2 + 1
            sage: (a+1)._im_gens_(m, [b^2])
            b^2 + 1
        """
        # NOTE -- if you ever want to change this so relative number fields are
        # in terms of a root of a poly.
        # The issue is that elements of a relative number field are represented in terms
        # of a generator for the absolute field.  However the morphism gives the image
        # of gen, which need not be a generator for the absolute field.  The morphism
        # has to be *over* the relative element.
        return codomain(self.polynomial()(im_gens[0]))

    def _latex_(self):
        """
        Returns the latex representation for this element.

        EXAMPLES:
            sage: C,zeta12=CyclotomicField(12).objgen()
            sage: latex(zeta12^4-zeta12)
            \zeta_{12}^{2} - \zeta_{12} - 1
        """
        return self.polynomial()._latex_(name=self.parent().latex_variable_name())

    def _pari_(self, var='x'):
        raise NotImplementedError, "NumberFieldElement sub-classes must override _pari_"

    def _pari_init_(self, var='x'):
        """
        Return GP/PARI string representation of self. This is used for
        converting this number field element to GP/PARI.  The returned
        string defines a pari Mod in the variable is var, which is by
        default 'x' -- not the name of the generator of the number
        field.

        INPUT:
            var -- (default: 'x') the variable of the pari Mod.

        EXAMPLES:
            sage: K.<a> = NumberField(x^5 - x - 1)
            sage: ((1 + 1/3*a)^4)._pari_init_()
            'Mod(1/81*x^4 + 4/27*x^3 + 2/3*x^2 + 4/3*x + 1, x^5 - x - 1)'
            sage: ((1 + 1/3*a)^4)._pari_init_('a')
            'Mod(1/81*a^4 + 4/27*a^3 + 2/3*a^2 + 4/3*a + 1, a^5 - a - 1)'

        Note that _pari_init_ can fail because of reserved words in PARI,
        and since it actually works by obtaining the PARI representation
        of something.
            sage: K.<theta> = NumberField(x^5 - x - 1)
            sage: b = (1/2 - 2/3*theta)^3; b
            -8/27*theta^3 + 2/3*theta^2 - 1/2*theta + 1/8
            sage: b._pari_init_('theta')
            Traceback (most recent call last):
            ...
            PariError: unexpected character (2)

        Fortunately pari_init returns everything in terms of x by default.
            sage: pari(b)
            Mod(-8/27*x^3 + 2/3*x^2 - 1/2*x + 1/8, x^5 - x - 1)
        """
        return repr(self._pari_(var=var))
##         if var == None:
##             var = self.parent().variable_name()
##         if isinstance(self.parent(), sage.rings.number_field.number_field.NumberField_relative):
##             f = self.polynomial()._pari_()
##             g = str(self.parent().pari_relative_polynomial())
##             base = self.parent().base_ring()
##             gsub = base.gen()._pari_()
##             gsub = str(gsub).replace(base.variable_name(), "y")
##             g = g.replace("y", gsub)
##         else:
##             f = str(self.polynomial()).replace("x",var)
##             g = str(self.parent().polynomial()).replace("x",var)
##         return 'Mod(%s, %s)'%(f,g)

    def __getitem__(self, n):
        """
        Return the n-th coefficient of this number field element, written
        as a polynomial in the generator.

        Note that $n$ must be between 0 and $d-1$, where $d$ is the
        degree of the number field.

        EXAMPLES:
            sage: m.<b> = NumberField(x^4 - 1789)
            sage: c = (2/3-4/5*b)^3; c
            -64/125*b^3 + 32/25*b^2 - 16/15*b + 8/27
            sage: c[0]
            8/27
            sage: c[2]
            32/25
            sage: c[3]
            -64/125

        We illustrate bounds checking:
            sage: c[-1]
            Traceback (most recent call last):
            ...
            IndexError: index must be between 0 and degree minus 1.
            sage: c[4]
            Traceback (most recent call last):
            ...
            IndexError: index must be between 0 and degree minus 1.

        The list method implicitly calls __getitem__:
            sage: list(c)
            [8/27, -16/15, 32/25, -64/125]
            sage: m(list(c)) == c
            True
        """
        if n < 0 or n >= self.parent().degree():     # make this faster.
            raise IndexError, "index must be between 0 and degree minus 1."
        return self.polynomial()[n]

    cdef int _cmp_c_impl(left, sage.structure.element.Element right) except -2:
        cdef NumberFieldElement _right = right
        return not (ZZX_equal(&left.__numerator, &_right.__numerator) and ZZ_equal(&left.__denominator, &_right.__denominator))

    def __abs__(self):
        r"""
        Return the numerical absolute value of this number field
        element with respect to the first archimedean embedding, to
        double precision.

        This is the \code{abs( )} Python function.  If you want a different
        embedding or precision, use \code{self.abs(...)}.

        EXAMPLES:
            sage: k.<a> = NumberField(x^3 - 2)
            sage: abs(a)
            1.25992104989
            sage: abs(a)^3
            2.0
            sage: a.abs(prec=128)
            1.2599210498948731647672106072782283506
        """
        return self.abs(prec=53, i=0)

    def abs(self, prec=53, i=0):
        """
        Return the absolute value of this element with respect to the
        ith complex embedding of parent, to the given precision.

        INPUT:
            prec -- (default: 53) integer bits of precision
            i -- (default: ) integer, which embedding to use

        EXAMPLES:
            sage: z = CyclotomicField(7).gen()
            sage: abs(z)
            1.00000000000000
            sage: abs(z^2 + 17*z - 3)
            16.0604426799931
            sage: K.<a> = NumberField(x^3+17)
            sage: abs(a)
            2.57128159066
            sage: a.abs(prec=100)
            2.5712815906582353554531872087
            sage: a.abs(prec=100,i=1)
            2.5712815906582353554531872087
            sage: a.abs(100, 2)
            2.5712815906582353554531872087

        Here's one where the absolute value depends on the embedding.
            sage: K.<b> = NumberField(x^2-2)
            sage: a = 1 + b
            sage: a.abs(i=0)
            0.414213562373
            sage: a.abs(i=1)
            2.41421356237
        """
        P = self.parent().complex_embeddings(prec)[i]
        return abs(P(self))

    def coordinates_in_terms_of_powers(self):
        r"""
        Let $\alpha$ be self.  Return a Python function that takes any
        element of the parent of self in $\QQ(\alpha)$ and writes it in
        terms of the powers of $\alpha$: $1, \alpha, \alpha^2, ...$.

        (NOT CACHED).

        EXAMPLES:
        This function allows us to write elements of a number field in
        terms of a different generator without having to construct a
        whole separate number field.

            sage: y = polygen(QQ,'y'); K.<beta> = NumberField(y^3 - 2); K
            Number Field in beta with defining polynomial y^3 - 2
            sage: alpha = beta^2 + beta + 1
            sage: c = alpha.coordinates_in_terms_of_powers(); c
            Coordinate function that writes elements in terms of the powers of beta^2 + beta + 1
            sage: c(beta)
            [-2, -3, 1]
            sage: c(alpha)
            [0, 1, 0]
            sage: c((1+beta)^5)
            [3, 3, 3]
            sage: c((1+beta)^10)
            [54, 162, 189]

        This function works even if self only generates a subfield
        of this number field.
            sage: k.<a> = NumberField(x^6 - 5)
            sage: alpha = a^3
            sage: c = alpha.coordinates_in_terms_of_powers()
            sage: c((2/3)*a^3 - 5/3)
            [-5/3, 2/3]
            sage: c
            Coordinate function that writes elements in terms of the powers of a^3
            sage: c(a)
            Traceback (most recent call last):
            ...
            ArithmeticError: vector is not in free module
        """
        K = self.parent()
        V, from_V, to_V = K.absolute_vector_space()
        h = K(1)
        B = [to_V(h)]
        f = self.minpoly()
        for i in range(f.degree()-1):
            h *= self
            B.append(to_V(h))
        W = V.span_of_basis(B)
        return CoordinateFunction(self, W, to_V)

    def complex_embeddings(self, prec=53):
        """
        Return the images of this element in the floating point
        complex numbers, to the given bits of precision.

        INPUT:
            prec -- integer (default: 53) bits of precision

        EXAMPLES:
            sage: k.<a> = NumberField(x^3 - 2)
            sage: a.complex_embeddings()
            [-0.629960524947 - 1.09112363597*I, -0.629960524947 + 1.09112363597*I, 1.25992104989]
            sage: a.complex_embeddings(10)
            [-0.63 - 1.1*I, -0.63 + 1.1*I, 1.3]
            sage: a.complex_embeddings(100)
            [-0.62996052494743658238360530364 - 1.0911236359717214035600726142*I, -0.62996052494743658238360530364 + 1.0911236359717214035600726142*I, 1.2599210498948731647672106073]
        """
        phi = self.parent().complex_embeddings(prec)
        return [f(self) for f in phi]

    def complex_embedding(self, prec=53, i=0):
        """
        Return the i-th embedding of self in the complex numbers, to
        the given precision.

        EXAMPLES:
            sage: k.<a> = NumberField(x^3 - 2)
            sage: a.complex_embedding()
            -0.629960524947 - 1.09112363597*I
            sage: a.complex_embedding(10)
            -0.63 - 1.1*I
            sage: a.complex_embedding(100)
            -0.62996052494743658238360530364 - 1.0911236359717214035600726142*I
            sage: a.complex_embedding(20, 1)
            -0.62996 + 1.0911*I
            sage: a.complex_embedding(20, 2)
            1.2599
        """
        return self.parent().complex_embeddings(prec)[i](self)

    def is_square(self, root=False):
        """
        Return True if self is a square in its parent number field and
        otherwise return False.

        INPUT:
            root -- if True, also return a square root (or None if self
                    is not a perfect square)

        EXAMPLES:
            sage: m.<b> = NumberField(x^4 - 1789)
            sage: b.is_square()
            False
            sage: c = (2/3*b + 5)^2; c
            4/9*b^2 + 20/3*b + 25
            sage: c.is_square()
            True
            sage: c.is_square(True)
            (True, 2/3*b + 5)

        We also test the functional notation.
            sage: is_square(c, True)
            (True, 2/3*b + 5)
            sage: is_square(c)
            True
            sage: is_square(c+1)
            False
        """
        v = self.sqrt(all=True)
        t = len(v) > 0
        if root:
            if t:
                return t, v[0]
            else:
                return False, None
        else:
            return t

    def sqrt(self, all=False):
        """
        Returns the square root of this number in the given number field.

        EXAMPLES:
            sage: K.<a> = NumberField(x^2 - 3)
            sage: K(3).sqrt()
            a
            sage: K(3).sqrt(all=True)
            [a, -a]
            sage: K(a^10).sqrt()
            9*a
            sage: K(49).sqrt()
            7
            sage: K(1+a).sqrt()
            Traceback (most recent call last):
            ...
            ValueError: a + 1 not a square in Number Field in a with defining polynomial x^2 - 3
            sage: K(0).sqrt()
            0
            sage: K((7+a)^2).sqrt(all=True)
            [a + 7, -a - 7]

            sage: K.<a> = CyclotomicField(7)
            sage: a.sqrt()
            a^4

            sage: K.<a> = NumberField(x^5 - x + 1)
            sage: (a^4 + a^2 - 3*a + 2).sqrt()
            a^3 - a^2

        ALGORITHM:
            Use Pari to factor $x^2$ - \code{self} in K.

        """
        # For now, use pari's factoring abilities
        R = sage.rings.polynomial.polynomial_ring.PolynomialRing(self._parent, 't')
        f = R([-self, 0, 1])
        roots = f.roots()
        if all:
            return [r[0] for r in roots]
        elif len(roots) > 0:
            return roots[0][0]
        else:
            raise ValueError, "%s not a square in %s"%(self, self._parent)

    cdef void _reduce_c_(self):
        """
        Pull out common factors from the numerator and denominator!
        """
        cdef ZZ_c gcd
        cdef ZZ_c t1
        cdef ZZX_c t2
        content(t1, self.__numerator)
        GCD_ZZ(gcd, t1, self.__denominator)
        if sign(gcd) != sign(self.__denominator):
            ZZ_negate(t1, gcd)
            gcd = t1
        div_ZZX_ZZ(t2, self.__numerator, gcd)
        div_ZZ_ZZ(t1, self.__denominator, gcd)
        self.__numerator = t2
        self.__denominator = t1

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        cdef NumberFieldElement x
        cdef NumberFieldElement _right = right
        x = self._new()
        mul_ZZ(x.__denominator, self.__denominator, _right.__denominator)
        cdef ZZX_c t1, t2
        mul_ZZX_ZZ(t1, self.__numerator, _right.__denominator)
        mul_ZZX_ZZ(t2, _right.__numerator, self.__denominator)
        add_ZZX(x.__numerator, t1, t2)
        x._reduce_c_()
        return x

    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        cdef NumberFieldElement x
        cdef NumberFieldElement _right = right
        x = self._new()
        mul_ZZ(x.__denominator, self.__denominator, _right.__denominator)
        cdef ZZX_c t1, t2
        mul_ZZX_ZZ(t1, self.__numerator, _right.__denominator)
        mul_ZZX_ZZ(t2, _right.__numerator, self.__denominator)
        sub_ZZX(x.__numerator, t1, t2)
        x._reduce_c_()
        return x

    cdef RingElement _mul_c_impl(self, RingElement right):
        """
        Returns the product of self and other as elements of a number field.

        EXAMPLES:
            sage: C.<zeta12>=CyclotomicField(12)
            sage: zeta12*zeta12^11
            1
            sage: G.<a> = NumberField(x^3 + 2/3*x + 1)
            sage: a^3
            -2/3*a - 1
            sage: a^3+a
            1/3*a - 1
        """
        cdef NumberFieldElement x
        cdef NumberFieldElement _right = right
        cdef ZZX_c temp
        cdef ZZ_c temp1
        cdef ZZ_c parent_den
        cdef ZZX_c parent_num
        self._parent_poly_c_( &parent_num, &parent_den )
        x = self._new()
        _sig_on
        # MulMod doesn't handle non-monic polynomials.
        # Therefore, we handle the non-monic case entirely separately.
        if ZZX_is_monic( &parent_num ):
            mul_ZZ(x.__denominator, self.__denominator, _right.__denominator)
            MulMod_ZZX(x.__numerator, self.__numerator, _right.__numerator, parent_num)
        else:
            mul_ZZ(x.__denominator, self.__denominator, _right.__denominator)
            mul_ZZX(x.__numerator, self.__numerator, _right.__numerator)
            if ZZX_degree(&x.__numerator) >= ZZX_degree(&parent_num):
                mul_ZZX_ZZ( x.__numerator, x.__numerator, parent_den )
                mul_ZZX_ZZ( temp, parent_num, x.__denominator )
                power_ZZ(temp1,LeadCoeff_ZZX(temp),ZZX_degree(&x.__numerator)-ZZX_degree(&parent_num)+1)
                PseudoRem_ZZX(x.__numerator, x.__numerator, temp)
                mul_ZZ(x.__denominator, x.__denominator, parent_den)
                mul_ZZ(x.__denominator, x.__denominator, temp1)
        _sig_off
        x._reduce_c_()
        return x

        #NOTES: In LiDIA, they build a multiplication table for the
        #number field, so it's not necessary to reduce modulo the
        #defining polynomial every time:
        #     src/number_fields/algebraic_num/order.cc: compute_table
        # but asymptotically fast poly multiplication means it's
        # actually faster to *not* build a table!?!

    cdef RingElement _div_c_impl(self, RingElement right):
        """
        Returns the quotient of self and other as elements of a number field.

        EXAMPLES:
            sage: C.<I>=CyclotomicField(4)
            sage: 1/I
            -I
            sage: I/0
            Traceback (most recent call last):
            ...
            ZeroDivisionError: Number field element division by zero

            sage: G.<a> = NumberField(x^3 + 2/3*x + 1)
            sage: a/a
            1
            sage: 1/a
            -a^2 - 2/3
            sage: a/0
            Traceback (most recent call last):
            ...
            ZeroDivisionError: Number field element division by zero
        """
        cdef NumberFieldElement x
        cdef NumberFieldElement _right = right
        cdef ZZX_c inv_num
        cdef ZZ_c inv_den
        cdef ZZ_c parent_den
        cdef ZZX_c parent_num
        cdef ZZX_c temp
        cdef ZZ_c temp1
        if not _right:
            raise ZeroDivisionError, "Number field element division by zero"
        self._parent_poly_c_( &parent_num, &parent_den )
        x = self._new()
        _sig_on
        _right._invert_c_(&inv_num, &inv_den)
        if ZZX_is_monic( &parent_num ):
            mul_ZZ(x.__denominator, self.__denominator, inv_den)
            MulMod_ZZX(x.__numerator, self.__numerator, inv_num, parent_num)
        else:
            mul_ZZ(x.__denominator, self.__denominator, inv_den)
            mul_ZZX(x.__numerator, self.__numerator, inv_num)
            if ZZX_degree(&x.__numerator) >= ZZX_degree(&parent_num):
                mul_ZZX_ZZ( x.__numerator, x.__numerator, parent_den )
                mul_ZZX_ZZ( temp, parent_num, x.__denominator )
                power_ZZ(temp1,LeadCoeff_ZZX(temp),ZZX_degree(&x.__numerator)-ZZX_degree(&parent_num)+1)
                PseudoRem_ZZX(x.__numerator, x.__numerator, temp)
                mul_ZZ(x.__denominator, x.__denominator, parent_den)
                mul_ZZ(x.__denominator, x.__denominator, temp1)
        x._reduce_c_()
        _sig_off
        return x

    def __floordiv__(self, other):
        """
        Return the quotient of self and other.  Since these are field
        elements the floor division is exactly the same as usual
        division.

        EXAMPLES:
            sage: m.<b> = NumberField(x^4 + x^2 + 2/3)
            sage: c = (1+b) // (1-b); c
            3/4*b^3 + 3/4*b^2 + 3/2*b + 1/2
            sage: (1+b) / (1-b) == c
            True
            sage: c * (1-b)
            b + 1
        """
        return self / other

    def __nonzero__(self):
        """
        Return True if this number field element is nonzero.

        EXAMPLES:
            sage: m.<b> = CyclotomicField(17)
            sage: m(0).__nonzero__()
            False
            sage: b.__nonzero__()
            True

        Nonzero is used by the bool command:
            sage: bool(b + 1)
            True
            sage: bool(m(0))
            False
        """
        return not IsZero_ZZX(self.__numerator)

    cdef ModuleElement _neg_c_impl(self):
        cdef NumberFieldElement x
        x = self._new()
        mul_ZZX_long(x.__numerator, self.__numerator, -1)
        x.__denominator = self.__denominator
        return x

    def __copy__(self):
        cdef NumberFieldElement x
        x = self._new()
        x.__numerator = self.__numerator
        x.__denominator = self.__denominator
        return x

    def __int__(self):
        """
        Attempt to convert this number field element to a Python integer,
        if possible.

        EXAMPLES:
            sage: C.<I>=CyclotomicField(4)
            sage: int(1/I)
            Traceback (most recent call last):
            ...
            TypeError: cannot coerce nonconstant polynomial to int
            sage: int(I*I)
            -1

            sage: K.<a> = NumberField(x^10 - x - 1)
            sage: int(a)
            Traceback (most recent call last):
            ...
            TypeError: cannot coerce nonconstant polynomial to int
            sage: int(K(9390283))
            9390283

        The semantics are like in Python, so the value does not have
        to preserved.
            sage: int(K(393/29))
            13
        """
        return int(self.polynomial())

    def __long__(self):
        """
        Attempt to convert this number field element to a Python long,
        if possible.

        EXAMPLES:
            sage: K.<a> = NumberField(x^10 - x - 1)
            sage: long(a)
            Traceback (most recent call last):
            ...
            TypeError: cannot coerce nonconstant polynomial to long
            sage: long(K(1234))
            1234L

        The value does not have to be preserved, in the case of fractions.
            sage: long(K(393/29))
            13L
        """
        return long(self.polynomial())

    cdef void _parent_poly_c_(self, ZZX_c *num, ZZ_c *den):
        raise NotImplementedError, "NumberFieldElement subclasses must override _parent_poly_c_()"
        cdef long i
        cdef ZZ_c coeff
        cdef ntl_ZZX _num
        cdef ntl_ZZ _den
        if isinstance(self.parent(), number_field.NumberField_relative):
            # ugly temp code
            f = self.parent().absolute_polynomial()

            __den = f.denominator()
            (<Integer>ZZ(__den))._to_ZZ(den)

            __num = f * __den
            for i from 0 <= i <= __num.degree():
                (<Integer>ZZ(__num[i]))._to_ZZ(&coeff)
                ZZX_SetCoeff( num[0], i, coeff )
        else:
            _num, _den = self.parent().polynomial_ntl()
            num[0] = _num.x
            den[0] = _den.x

    cdef void _invert_c_(self, ZZX_c *num, ZZ_c *den):
        """
        Computes the numerator and denominator of the multiplicative inverse of this element.

        Suppose that this element is x/d and the parent mod'ding polynomial is M/D.  The NTL function
        XGCD( r, s, t, a, b ) computes r,s,t such that $r=s*a+t*b$.  We compute
        XGCD( r, s, t, x*D, M*d ) and set
        num=s*D*d
        den=r

        EXAMPLES:
            I'd love to, but since we are dealing with c-types, I can't at this level.
            Check __invert__ for doc-tests that rely on this functionality.
        """
        cdef ZZ_c parent_den
        cdef ZZX_c parent_num
        self._parent_poly_c_( &parent_num, &parent_den )

        cdef ZZX_c t # unneeded except to be there
        cdef ZZX_c a, b
        mul_ZZX_ZZ( a, self.__numerator, parent_den )
        mul_ZZX_ZZ( b, parent_num, self.__denominator )
        XGCD_ZZX( den[0], num[0],  t, a, b, 1 )
        mul_ZZX_ZZ( num[0], num[0], parent_den )
        mul_ZZX_ZZ( num[0], num[0], self.__denominator )

    def __invert__(self):
        """
        Returns the multiplicative inverse of self in the number field.

        EXAMPLES:
            sage: C.<I>=CyclotomicField(4)
            sage: ~I
            -I
            sage: (2*I).__invert__()
            -1/2*I
        """
        if IsZero_ZZX(self.__numerator):
            raise ZeroDivisionError
        cdef NumberFieldElement x
        x = self._new()
        self._invert_c_(&x.__numerator, &x.__denominator)
        x._reduce_c_()
        return x
#        K = self.parent()
#        quotient = K(1)._pari_('x') / self._pari_('x')
#        if isinstance(K, sage.rings.number_field.number_field.NumberField_relative):
#            return K(K.pari_rnf().rnfeltreltoabs(quotient))
#        else:
#            return K(quotient)

    def _integer_(self):
        """
        Returns a rational integer if this element is actually a rational integer.

        EXAMPLES:
            sage: C.<I>=CyclotomicField(4)
            sage: (~I)._integer_()
            Traceback (most recent call last):
            ...
            TypeError: Unable to coerce -I to an integer
            sage: (2*I*I)._integer_()
            -2
        """
        if ZZX_deg(self.__numerator) >= 1:
            raise TypeError, "Unable to coerce %s to an integer"%self
        return ZZ(self._rational_())

    def _rational_(self):
        """
        Returns a rational number if this element is actually a rational number.

        EXAMPLES:
            sage: C.<I>=CyclotomicField(4)
            sage: (~I)._rational_()
            Traceback (most recent call last):
            ...
            TypeError: Unable to coerce -I to a rational
            sage: (I*I/2)._rational_()
            -1/2
        """
        if ZZX_deg(self.__numerator) >= 1:
            raise TypeError, "Unable to coerce %s to a rational"%self
        cdef Integer num
        num = PY_NEW(Integer)
        ZZX_getitem_as_mpz(&num.value, &self.__numerator, 0)
        return num / (<IntegerRing_class>ZZ)._coerce_ZZ(&self.__denominator)

    def galois_conjugates(self, K=None):
        r"""
        Return all Gal(Qbar/Q)-conjugates of this number field element in
        the Galois closure of the parent field if K is not given, or
        in K if K is given.

        EXAMPLES:
        In the first example the conjugates are obvious:
            sage: K.<a> = NumberField(x^2 - 2)
            sage: a.galois_conjugates()
            [a, -a]
            sage: K(3).galois_conjugates()
            [3]

        In this example the field is not Galois, so we have to pass
        to an extension to obtain the Galois conjugates.
            sage: K.<a> = NumberField(x^3 - 2)
            sage: a.galois_conjugates()
            [1/84*a1^4 + 13/42*a1, -1/252*a1^4 - 55/126*a1, -1/126*a1^4 + 8/63*a1]
            sage: K.<a> = NumberField(x^3 - 2)
            sage: c = a.galois_conjugates(); c
            [1/84*a1^4 + 13/42*a1, -1/252*a1^4 - 55/126*a1, -1/126*a1^4 + 8/63*a1]
            sage: c[0]^3
            2
            sage: parent(c[0])
            Number Field in a1 with defining polynomial x^6 + 40*x^3 + 1372
            sage: parent(c[0]).is_galois()
            True

        There is only one Galois conjugate of $\sqrt[3]{2}$ in
        $\QQ(\sqrt[3]{2})$.
            sage: a.galois_conjugates(K)
            [a]

        Galois conjugates of $\sqrt[3]{2}$ in the field $\QQ(\zeta_3,\sqrt[3]{2})$:
            sage: L.<a> = CyclotomicField(3).extension(x^3 - 2)
            sage: a.galois_conjugates()
            [a, (-zeta3 - 1)*a, zeta3*a]
        """
        if K is None:
            L = self.parent()
            K = L.galois_closure()
        f = self.absolute_minpoly()
        g = K['x'](f)
        return [a for a,_ in g.roots()]

    def conjugate(self):
        """
        Return the complex conjugate of the number field element.  Currently,
        this is implemented for cyclotomic fields and quadratic extensions of Q.
        It seems likely that there are other number fields for which the idea of
        a conjugate would be easy to compute.

        EXAMPLES:
            sage: k.<I> = QuadraticField(-1)
            sage: I.conjugate()
            -I
            sage: (I/(1+I)).conjugate()
            -1/2*I + 1/2
            sage: z6=CyclotomicField(6).gen(0)
            sage: (2*z6).conjugate()
            -2*zeta6 + 2

            sage: K.<b> = NumberField(x^3 - 2)
            sage: b.conjugate()
            Traceback (most recent call last):
            ...
            NotImplementedError: complex conjugation is not implemented (or doesn't make sense).
        """
        coeffs = self.parent().polynomial().list()
        if len(coeffs) == 3 and coeffs[2] == 1 and coeffs[1] == 0:
            # polynomial looks like x^2+d
            # i.e. we live in a quadratic extension of QQ
            if coeffs[0] > 0:
                gen = self.parent().gen()
                return self.polynomial()(-gen)
            else:
                return self
        elif isinstance(self.parent(), number_field.NumberField_cyclotomic):
            # We are in a cyclotomic field
            # Replace the generator zeta_n with (zeta_n)^(n-1)
            gen = self.parent().gen()
            return self.polynomial()(gen ** (gen.multiplicative_order()-1))
        else:
            raise NotImplementedError, "complex conjugation is not implemented (or doesn't make sense)."

    def polynomial(self, var='x'):
        """
        Return the underlying polynomial corresponding to this
        number field element.

        The resulting polynomial is currently *not* cached.

        EXAMPLES:
            sage: K.<a> = NumberField(x^5 - x - 1)
            sage: f = (-2/3 + 1/3*a)^4; f
            1/81*a^4 - 8/81*a^3 + 8/27*a^2 - 32/81*a + 16/81
            sage: g = f.polynomial(); g
            1/81*x^4 - 8/81*x^3 + 8/27*x^2 - 32/81*x + 16/81
            sage: parent(g)
            Univariate Polynomial Ring in x over Rational Field

        Note that the result of this function is not cached (should this
        be changed?):
            sage: g is f.polynomial()
            False
        """
        return QQ[var](self._coefficients())

    def _coefficients(self):
        """
        Return the coefficients of the underlying polynomial corresponding to this
        number field element.

        OUTPUT:
             -- a list whose length corresponding to the degree of this element
                written in terms of a generator.

        EXAMPLES:

        """
        coeffs = []
        cdef Integer den = (<IntegerRing_class>ZZ)._coerce_ZZ(&self.__denominator)
        cdef Integer numCoeff
        cdef int i
        for i from 0 <= i <= ZZX_deg(self.__numerator):
            numCoeff = PY_NEW(Integer)
            ZZX_getitem_as_mpz(&numCoeff.value, &self.__numerator, i)
            coeffs.append( numCoeff / den )
        return coeffs

    cdef void _ntl_coeff_as_mpz(self, mpz_t* z, long i):
        if i > ZZX_deg(self.__numerator):
            mpz_set_ui(z[0], 0)
        else:
            ZZX_getitem_as_mpz(z, &self.__numerator, i)

    cdef void _ntl_denom_as_mpz(self, mpz_t* z):
        cdef Integer denom = (<IntegerRing_class>ZZ)._coerce_ZZ(&self.__denominator)
        mpz_set(z[0], denom.value)

    def denominator(self):
        """
        Return the denominator of this element, which is by definition
        the denominator of the corresponding polynomial
        representation.  I.e., elements of number fields are
        represented as a polynomial (in reduced form) modulo the
        modulus of the number field, and the denominator is the
        denominator of this polynomial.

        EXAMPLES:
            sage: K.<z> = CyclotomicField(3)
            sage: a = 1/3 + (1/5)*z
            sage: print a.denominator()
            15
        """
        return (<IntegerRing_class>ZZ)._coerce_ZZ(&self.__denominator)

    def _set_multiplicative_order(self, n):
        """
        Set the multiplicative order of this number field element.

        WARNING -- use with caution -- only for internal use!  End
        users should never call this unless they have a very good
        reason to do so.

        EXAMPLES:
            sage: K.<a> = NumberField(x^2 + x + 1)
            sage: a._set_multiplicative_order(3)
            sage: a.multiplicative_order()
            3

        You can be evil with this so be careful.  That's why the function
        name begins with an underscore.
            sage: a._set_multiplicative_order(389)
            sage: a.multiplicative_order()
            389
        """
        self.__multiplicative_order = n

    def multiplicative_order(self):
        """
        Return the multiplicative order of this number field element.

        EXAMPLES:
            sage: K.<z> = CyclotomicField(5)
            sage: z.multiplicative_order()
            5
            sage: (-z).multiplicative_order()
            10
            sage: (1+z).multiplicative_order()
            +Infinity
        """
        if self.__multiplicative_order is not None:
            return self.__multiplicative_order

        if self.is_rational_c():
            self.__multiplicative_order = self._rational_().multiplicative_order()
            return self.__multiplicative_order

        if isinstance(self.parent(), number_field.NumberField_cyclotomic):
            t = self.parent()._multiplicative_order_table()
            f = self.polynomial()
            if t.has_key(f):
                self.__multiplicative_order = t[f]
                return self.__multiplicative_order

        ####################################################################
        # VERY DUMB Algorithm to compute the multiplicative_order of
        # an element x of a number field K.
        #
        # 1. Find an integer B such that if n>=B then phi(n) > deg(K).
        #    For this use that for n>6 we have phi(n) >= log_2(n)
        #    (to see this think about the worst prime factorization
        #    in the multiplicative formula for phi.)
        # 2. Compute x, x^2, ..., x^B in order to determine the multiplicative_order.
        #
        # todo-- Alternative: Only do the above if we don't require an optional
        # argument which gives a multiple of the order, which is usually
        # something available in any actual application.
        #
        # BETTER TODO: Factor cyclotomic polynomials over K to determine
        # possible orders of elements?  Is there something even better?
        #
        ####################################################################
        d = self.parent().degree()
        B = max(7, 2**d+1)
        x = self
        i = 1
        while i < B:
            if x == 1:
                self.__multiplicative_order = i
                return self.__multiplicative_order
            x *= self
            i += 1

        # it must have infinite order
        self.__multiplicative_order = sage.rings.infinity.infinity
        return self.__multiplicative_order

    cdef bint is_rational_c(self):
        return ZZX_deg(self.__numerator) == 0

    def trace(self, K=None):
        """
        Return the absolute or relative trace of this number field
        element.

        If K is given then K must be a subfield of the parent L of
        self, in which case the trace is the relative trace from L to K.
        In all other cases, the trace is the absolute trace down to QQ.

        EXAMPLES:
            sage: K.<a> = NumberField(x^3 -132/7*x^2 + x + 1); K
            Number Field in a with defining polynomial x^3 - 132/7*x^2 + x + 1
            sage: a.trace()
            132/7
            sage: (a+1).trace() == a.trace() + 3
            True
        """
        if K is None:
            return QQ(self._pari_('x').trace())
        return self.matrix(K).trace()

    def norm(self, K=None):
        """
        Return the absolute or relative norm of this number field
        element.

        If K is given then K must be a subfield of the parent L of
        self, in which case the norm is the relative norm from L to K.
        In all other cases, the norm is the absolute norm down to QQ.

        EXAMPLES:
            sage: K.<a> = NumberField(x^3 + x^2 + x + -132/7); K
            Number Field in a with defining polynomial x^3 + x^2 + x - 132/7
            sage: a.norm()
            132/7
            sage: factor(a.norm())
            2^2 * 3 * 7^-1 * 11
            sage: K(0).norm()
            0

        Some complicated relatives norms in a tower of number fields.
            sage: K.<a,b,c> = NumberField([x^2 + 1, x^2 + 3, x^2 + 5])
            sage: L = K.base_field(); M = L.base_field()
            sage: a.norm()
            1
            sage: a.norm(L)
            1
            sage: a.norm(M)
            1
            sage: a
            a
            sage: (a+b+c).norm()
            121
            sage: (a+b+c).norm(L)
            2*c*b + -7
            sage: (a+b+c).norm(M)
            -11

        We illustrate that norm is compatible with towers:
            sage: z = (a+b+c).norm(L); z.norm(M)
            -11
        """
        if K is None:
            return QQ(self._pari_('x').norm())
        return self.matrix(K).determinant()

    def charpoly(self, var='x'):
        raise NotImplementedError, "Subclasses of NumberFieldElement must override charpoly()"

    def minpoly(self, var='x'):
        """
        Return the minimal polynomial of this number field element.

        EXAMPLES:
            sage: K.<a> = NumberField(x^2+3)
            sage: a.minpoly('x')
            x^2 + 3
            sage: R.<X> = K['X']
            sage: L.<b> = K.extension(X^2-(22 + a))
            sage: b.minpoly('t')
            t^2 + -a - 22
            sage: b.absolute_minpoly('t')
            t^4 - 44*t^2 + 487
            sage: b^2 - (22+a)
            0
        """
        return self.charpoly(var).radical() # square free part of charpoly

    def is_integral(self):
        r"""
        Determine if a number is in the ring of integers
        of this number field.

        EXAMPLES:
            sage: K.<a> = NumberField(x^2 + 23, 'a')
            sage: a.is_integral()
            True
            sage: t = (1+a)/2
            sage: t.is_integral()
            True
            sage: t.minpoly()
            x^2 - x + 6
            sage: t = a/2
            sage: t.is_integral()
            False
            sage: t.minpoly()
            x^2 + 23/4
        """
        return all([a in ZZ for a in self.minpoly()])

    def matrix(self, base=None):
        r"""
        If base is None, return the matrix of right multiplication by
        the element on the power basis $1, x, x^2, \ldots, x^{d-1}$
        for the number field.  Thus the {\em rows} of this matrix give
        the images of each of the $x^i$.

        If base is not None, then base must be either a field that
        embeds in the parent of self or a morphism to the parent of
        self, in which case this function returns the matrix of
        multiplication by self on the power basis, where we view the
        parent field as a field over base.

        INPUT:
            base -- field or morphism

        EXAMPLES:
        Regular number field:
            sage: K.<a> = NumberField(QQ['x'].0^3 - 5)
            sage: M = a.matrix(); M
            [0 1 0]
            [0 0 1]
            [5 0 0]
            sage: M.base_ring() is QQ
            True

        Relative number field:
            sage: L.<b> = K.extension(K['x'].0^2 - 2)
            sage: M = b.matrix(); M
            [0 1]
            [2 0]
            sage: M.base_ring() is K
            True

        Absolute number field:
            sage: M = L.absolute_field('c').gen().matrix(); M
            [  0   1   0   0   0   0]
            [  0   0   1   0   0   0]
            [  0   0   0   1   0   0]
            [  0   0   0   0   1   0]
            [  0   0   0   0   0   1]
            [-17 -60 -12 -10   6   0]
            sage: M.base_ring() is QQ
            True

        More complicated relative number field:
            sage: L.<b> = K.extension(K['x'].0^2 - a); L
            Number Field in b with defining polynomial x^2 + -a over its base field
            sage: M = b.matrix(); M
            [0 1]
            [a 0]
            sage: M.base_ring() is K
            True

        An example where we explicitly give the subfield or the embedding:
            sage: K.<a> = NumberField(x^4 + 1); L.<a2> = NumberField(x^2 + 1)
            sage: a.matrix(L)
            [ 0  1]
            [a2  0]

        Notice that if we compute all embeddings and choose a different one,
        then the matrix is changed as it should be:
            sage: v = L.embeddings(K)
            sage: a.matrix(v[1])
            [  0   1]
            [-a2   0]

        The norm is also changed:
            sage: a.norm(v[1])
            a2
            sage: a.norm(v[0])
            -a2
        """
        if base is not None:
            if number_field.is_NumberField(base):
                return self._matrix_over_base(base)
            else:
                return self._matrix_over_base_morphism(base)
        # Mutiply each power of field generator on
        # the left by this element; make matrix
        # whose rows are the coefficients of the result,
        # and transpose.
        if self.__matrix is None:
            K = self.parent()
            v = []
            x = K.gen()
            a = K(1)
            d = K.degree()
            for n in range(d):
                v += (a*self).list()
                a *= x
            k = K.base_ring()
            import sage.matrix.matrix_space
            M = sage.matrix.matrix_space.MatrixSpace(k, d)
            self.__matrix = M(v)
        return self.__matrix

    def _matrix_over_base(self, L):
        K = self.parent()
        E = L.embeddings(K)
        if len(E) == 0:
            raise ValueError, "no way to embed L into parent's base ring K"
        phi = E[0]
        return self._matrix_over_base_morphism(phi)

    def _matrix_over_base_morphism(self, phi):
        L = phi.domain()
        alpha = L.primitive_element()
        beta = phi(alpha)
        K = phi.codomain()
        if K != self.parent():
            raise ValueError, "codomain of phi must be parent of self"

        # Construct a relative extension over L (= QQ(beta))
        M = K.relativize(beta, ('a','b'))
                     # variable name a is OK, since this is temporary

        # Carry self over to M.
        from_M, to_M = M.structure()
        try:
            z = to_M(self)
        except Exception:
            return to_M, self, K, beta

        # Compute the relative matrix of self, but in M
        R = z.matrix()

        # Map back to L.
        psi = M.base_field().hom([alpha])
        return R.apply_morphism(psi)


    def list(self):
        """
        Return list of coefficients of self written in terms of a power basis.
        """
        # Power basis list is total nonsense, unless the parent of self is an
        # absolute extension.
        raise NotImplementedError


cdef class NumberFieldElement_absolute(NumberFieldElement):

    def _pari_(self, var='x'):
        """
        Return PARI C-library object corresponding to self.

        EXAMPLES:
            sage: k.<j> = QuadraticField(-1)
            sage: j._pari_('j')
            Mod(j, j^2 + 1)
            sage: pari(j)
            Mod(x, x^2 + 1)

            sage: y = QQ['y'].gen()
            sage: k.<j> = NumberField(y^3 - 2)
            sage: pari(j)
            Mod(x, x^3 - 2)

        By default the variable name is 'x', since in PARI many variable
        names are reserved:
            sage: theta = polygen(QQ, 'theta')
            sage: M.<theta> = NumberField(theta^2 + 1)
            sage: pari(theta)
            Mod(x, x^2 + 1)

        If you try do coerce a generator called I to PARI, hell may
        break loose:
            sage: k.<I> = QuadraticField(-1)
            sage: I._pari_('I')
            Traceback (most recent call last):
            ...
            PariError: forbidden (45)

        Instead, request the variable be named different for the coercion:
            sage: pari(I)
            Mod(x, x^2 + 1)
            sage: I._pari_('i')
            Mod(i, i^2 + 1)
            sage: I._pari_('II')
            Mod(II, II^2 + 1)
        """
        try:
            return self.__pari[var]
        except KeyError:
            pass
        except TypeError:
            self.__pari = {}
        if var is None:
            var = self.parent().variable_name()
        f = self.polynomial()._pari_()
        gp = self.parent().polynomial()
        if gp.name() != 'x':
            gp = gp.change_variable_name('x')
        g = gp._pari_()
        gv = str(gp.parent().gen())
        if var != 'x':
            f = f.subst("x",var)
        if var != gv:
            g = g.subst(gv, var)
        h = f.Mod(g)
        self.__pari[var] = h
        return h

    cdef void _parent_poly_c_(self, ZZX_c *num, ZZ_c *den):
        cdef ntl_ZZX _num
        cdef ntl_ZZ _den
        _num, _den = self.parent().polynomial_ntl()
        num[0] = _num.x
        den[0] = _den.x

    def absolute_charpoly(self, var='x'):
        r"""
        Return the characteristic polynomial of this element over $\QQ$.
        """
        return self.charpoly(var=var)

    def absolute_minpoly(self, var='x'):
        r"""
        Return the minimal polynomial of this element over $\QQ$.

        EXAMPLES:


        """
        return self.minpoly(var=var)

    def charpoly(self, var='x'):
        r"""
        The characteristic polynomial of this element over $\QQ$.

        This is the same as \code{self.absolute_charpoly} since this
        is an element of an absolute extension.

        EXAMPLES:

        We compute the charpoly of cube root of $2$.

            sage: R.<x> = QQ[]
            sage: K.<a> = NumberField(x^3-2)
            sage: a.charpoly('x')
            x^3 - 2

        """
        R = self.parent().base_ring()[var]
        return R(self._pari_('x').charpoly())

    def list(self):
        """
        Return list of coefficients of self written in terms of a power basis.

        EXAMPLE:
            sage: K.<z> = CyclotomicField(3)
            sage: (2+3/5*z).list()
            [2, 3/5]
            sage: (5*z).list()
            [0, 5]
            sage: K(3).list()
            [3, 0]
        """
        n = self.parent().degree()
        v = self._coefficients()
        z = sage.rings.rational.Rational(0)
        return v + [z]*(n - len(v))



cdef class NumberFieldElement_relative(NumberFieldElement):
    def list(self):
        """
        Return list of coefficients of self written in terms of a
        power basis.

        EXAMPLES:
            sage: K.<a,b> = NumberField([x^3+2, x^2+1])
            sage: a.list()
            [0, 1, 0]
            sage: v = (K.base_field().0 + a)^2 ; v
            a^2 + 2*b*a + -1
            sage: v.list()
            [-1, 2*b, 1]
        """
        return self.vector().list()

    def _pari_(self, var='x'):
        """
        Return PARI C-library object corresponding to self.

        EXAMPLES:
        By default the variable name is 'x', since in PARI many variable
        names are reserved.
            sage: y = QQ['y'].gen()
            sage: k.<j> = NumberField([y^2 - 7, y^3 - 2])
            sage: pari(j)
            Mod(42/5515*x^5 - 9/11030*x^4 - 196/1103*x^3 + 273/5515*x^2 + 10281/5515*x + 4459/11030, x^6 - 21*x^4 + 4*x^3 + 147*x^2 + 84*x - 339)
            sage: j^2
            7
            sage: pari(j)^2
            Mod(7, x^6 - 21*x^4 + 4*x^3 + 147*x^2 + 84*x - 339)
        """
        try:
            return self.__pari[var]
        except KeyError:
            pass
        except TypeError:
            self.__pari = {}
        if var is None:
            var = self.parent().variable_name()
        f = self.polynomial()._pari_()
        g = str(self.parent().pari_polynomial())
        base = self.parent().base_ring()
        gsub = base.gen()._pari_()
        gsub = str(gsub).replace('x', 'y')
        g = g.replace('y', gsub)
        h = f.Mod(g)
        self.__pari[var] = h
        return h

    cdef void _parent_poly_c_(self, ZZX_c *num, ZZ_c *den):
        cdef long i
        cdef ZZ_c coeff
        cdef ntl_ZZX _num
        cdef ntl_ZZ _den
        # ugly temp code
        f = self.parent().absolute_polynomial()

        __den = f.denominator()
        (<Integer>ZZ(__den))._to_ZZ(den)

        __num = f * __den
        for i from 0 <= i <= __num.degree():
            (<Integer>ZZ(__num[i]))._to_ZZ(&coeff)
            ZZX_SetCoeff( num[0], i, coeff )

    def __repr__(self):
        K = self.parent()
        # Compute representation of self in terms of relative vector space.
        w = self.vector()
        R = K.base_field()[K.variable_name()]
        return repr(R(w.list()))

    def vector(self):
        return self.parent().vector_space()[2](self)

    def charpoly(self, var='x'):
        r"""
        The characteristic polynomial of this element over its base field.

        EXAMPLES:

        """
        return self.matrix().charpoly(var)

    def absolute_charpoly(self, var='x'):
        r"""
        The characteristic polynomial of this element over $\QR$.

        We construct a relative extension and find the characteristic
        polynomial over $\QQ$.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: K.<a> = NumberField(x^3-2)
            sage: S.<X> = K[]
            sage: L.<b> = NumberField(X^3 + 17); L
            Number Field in b with defining polynomial X^3 + 17 over its base field
            sage: b.absolute_charpoly()
            x^9 + 51*x^6 + 867*x^3 + 4913
            sage: b.charpoly()(b)
            0
            sage: a = L.0; a
            b
            sage: a.absolute_charpoly('x')
            x^9 + 51*x^6 + 867*x^3 + 4913
            sage: a.absolute_charpoly('y')
            y^9 + 51*y^6 + 867*y^3 + 4913
        """
        g = self.polynomial()  # in QQ[x]
        R = g.parent()
        f = self.parent().pari_polynomial()  # # field is QQ[x]/(f)
        return R( (g._pari_().Mod(f)).charpoly() ).change_variable_name(var)

    def absolute_minpoly(self, var='x'):
        r"""
        Return the minpoly over $\QQ$ of this element.

        EXAMPLES:
        """
        return self.absolute_charpoly(var).radical()

## This might be useful for computing relative charpoly.
## BUT -- currently I don't even know how to view elements
## as being in terms of the right thing, i.e., this code
## below as is lies.
##             nf = self.parent()._pari_base_nf()
##             prp = self.parent().pari_relative_polynomial()
##             elt = str(self.polynomial()._pari_())
##             return R(nf.rnfcharpoly(prp, elt))
##         # return self.matrix().charpoly('x')


cdef class OrderElement_absolute(NumberFieldElement_absolute):
    """
    Element of an order in an absolute number field.

    EXAMPLES:
        sage: k.<a> = NumberField(x^2 + 1)
    """
    def __init__(self, order, f):
        K = order.number_field()
        NumberFieldElement_absolute.__init__(self, K, f)
        self._order = order

cdef class OrderElement_relative(NumberFieldElement_relative):
    """
    Element of an order in a relative number field.
    """
    def __init__(self, order, f):
        K = order.number_field()
        NumberFieldElement_relative.__init__(self, K, f)
        self._order = order




class CoordinateFunction:
    def __init__(self, alpha, W, to_V):
        self.__alpha = alpha
        self.__W = W
        self.__to_V = to_V
        self.__K = alpha.parent()

    def __repr__(self):
        return "Coordinate function that writes elements in terms of the powers of %s"%self.__alpha

    def alpha(self):
        return self.__alpha

    def __call__(self, x):
        return self.__W.coordinates(self.__to_V(self.__K(x)))
