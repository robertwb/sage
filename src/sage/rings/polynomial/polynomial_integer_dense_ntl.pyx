"""
Dense univariate polynomials over Z, implemented using NTL.

AUTHORS:
    -- David Harvey: split off from polynomial_element_generic.py (2007-09)
    -- David Harvey: rewrote to talk to NTL directly, instead of via ntl.pyx (2007-09);
               a lot of this was based on Joel Mohler's recent rewrite of the NTL wrapper

"""

################################################################################
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
################################################################################

include "../../ext/stdsage.pxi"
include "sage/ext/interrupt.pxi"

from sage.rings.polynomial.polynomial_element cimport Polynomial
from sage.structure.element cimport ModuleElement, RingElement

from sage.rings.integer_ring import IntegerRing
from sage.rings.integer_ring cimport IntegerRing_class
ZZ_sage = IntegerRing()


from sage.rings.polynomial.polynomial_element import is_Polynomial

from sage.libs.ntl.ntl_ZZX cimport ntl_ZZX

from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ
from sage.rings.integer import Integer
from sage.rings.integer cimport Integer

from sage.libs.all import pari, pari_gen
from sage.structure.factorization import Factorization

from sage.rings.fraction_field_element import FractionFieldElement
from sage.rings.arith import lcm
import sage.rings.polynomial.polynomial_ring


cdef class Polynomial_integer_dense_ntl(Polynomial):
    r"""
    A dense polynomial over the integers, implemented via NTL.
    """

    def __new__(self, parent=None, x=None, check=True, is_gen=False, construct=False):
        r"""
        calls the underlying NTL constructor
        """
        ZZX_construct(&self.__poly)


    def __dealloc__(self):
        r"""
        calls the underlying NTL destructor
        """
        ZZX_destruct(&self.__poly)


    cdef Polynomial_integer_dense_ntl _new(self):
        r"""
        Quickly creates a new initialized Polynomial_integer_dense_ntl
        with the correct parent and _is_gen == 0.
        """
        cdef Polynomial_integer_dense_ntl x = PY_NEW(Polynomial_integer_dense_ntl)
        x._parent = self._parent
        x._is_gen = 0
        return x


    def __init__(self, parent, x=None, check=True, is_gen=False, construct=False):
        r"""
        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: x
            x

        Construct from list:
            sage: R([])
            0
            sage: R([1, -2, 3])
            3*x^2 - 2*x + 1

        Coercions from other rings are attempted automatically:
            sage: R([1, -6/3, 3])
            3*x^2 - 2*x + 1
            sage: R([1, 5/2, 2])
            Traceback (most recent call last):
            ...
            TypeError: no coercion of this rational to integer

        Construct from constant:
            sage: R(3)
            3

        Coercion from PARI polynomial:
            sage: f = R([-1, 2, 5]); f
            5*x^2 + 2*x - 1
            sage: type(f)
            <type 'sage.rings.polynomial.polynomial_integer_dense_ntl.Polynomial_integer_dense_ntl'>
            sage: type(pari(f))
            <type 'sage.libs.pari.gen.gen'>
            sage: type(R(pari(f)))
            <type 'sage.rings.polynomial.polynomial_integer_dense_ntl.Polynomial_integer_dense_ntl'>
            sage: R(pari(f))
            5*x^2 + 2*x - 1

        Coercion from NTL polynomial:
            sage: f = ntl.ZZX([1, 2, 3])
            sage: print R(f)
            3*x^2 + 2*x + 1

        Coercion from dictionary:
            sage: f = R({2: -4, 3: 47}); f
            47*x^3 - 4*x^2

        Coercion from fraction field element with trivial denominator:
            sage: f = (x^3 - 1) / (x - 1)
            sage: type(f)
            <class 'sage.rings.fraction_field_element.FractionFieldElement'>
            sage: g = R(f); g
            x^2 + x + 1

        NTL polynomials are limited in size to slightly under the word length:
            sage: ZZ['x']({2^3: 1})
            x^8
            sage: ZZ['x']({2^30: 1})               # 32-bit
            sage: ZZ['x']({2^62: 1})               # 64-bit
            Traceback (most recent call last):
            ...
            OverflowError: Dense NTL integer polynomials have a maximum degree of 268435455    # 32-bit
            OverflowError: Dense NTL integer polynomials have a maximum degree of 1152921504606846975    # 64-bit
        """
        Polynomial.__init__(self, parent, is_gen=is_gen)

        cdef Py_ssize_t degree
        cdef Py_ssize_t i
        cdef ZZ_c y

        if x is None:
            return         # leave initialized to 0 polynomial.

        if isinstance(x, Polynomial):
            if x.parent() is self.parent():
                # copy with NTL assignment operator
                self.__poly = (<Polynomial_integer_dense_ntl>x).__poly
                return
            else:
                # coerce coefficients into SAGE integers
                x = [Integer(a) for a in x.list()]
                check = False

        elif isinstance(x, dict):
            x = x.items()
            degree = 0
            # find max degree to allocate only once
            for ii, a in x:
                i = ii[0] if PY_TYPE_CHECK_EXACT(ii, tuple) else ii # mpoly dict style has tuple keys
                if i < 0:
                    raise ValueError, "Negative monomial degrees not allowed: %s" % i
                elif i > degree:
                    degree = i
            if degree >= NTL_OVFBND:
                raise OverflowError, "Dense NTL integer polynomials have a maximum degree of %s" % (NTL_OVFBND-1)
            ZZX_SetCoeff_long(self.__poly, degree, 1)
            # now fill them in
            for ii, a in x:
                i = ii[0] if PY_TYPE_CHECK_EXACT(ii, tuple) else ii
                if PY_TYPE_CHECK_EXACT(a, int):
                    ZZX_SetCoeff_long(self.__poly, i, a)
                else:
                    if not PY_TYPE_CHECK(a, Integer):
                        a = ZZ(a)
                    mpz_to_ZZ(&y, &(<Integer>a).value)
                    ZZX_SetCoeff(self.__poly, i, y)
            return

        elif isinstance(x, pari_gen):
            x = [Integer(w) for w in x.Vecrev()]
            check = False

        elif isinstance(x, ntl_ZZX):    # coercion from ntl.pyx object
            # copy with NTL assignment operator
            self.__poly = (<ntl_ZZX>x).x
            return

        elif isinstance(x, FractionFieldElement) and \
                 isinstance(x.numerator(), Polynomial_integer_dense_ntl):
            if x.denominator() == 1:
                # fraction of the form f(x)/1
                self.__poly = (<Polynomial_integer_dense_ntl>x.numerator()).__poly
                return

        elif not isinstance(x, list):
            x = [x]   # constant polynomials

        if len(x) >= NTL_OVFBND:
            raise OverflowError, "Dense NTL integer polynomials have a maximum degree of %s" % (NTL_OVFBND-1)

        for i from 0 <= i < len(x):
            a = x[i]
            if PY_TYPE_CHECK_EXACT(a, int):
                ZZX_SetCoeff_long(self.__poly, i, a)
            else:
                if not PY_TYPE_CHECK(a, Integer):
                    a = ZZ(a)
                mpz_to_ZZ(&y, &(<Integer>a).value)
                ZZX_SetCoeff(self.__poly, i, y)


    def content(self):
        r"""
        Return the greatest common divisor of the coefficients of this
        polynomial. The sign is the sign of the leading coefficient.
        The content of the zero polynomial is zero.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: (2*x^2 - 4*x^4 + 14*x^7).content()
            2
            sage: (2*x^2 - 4*x^4 - 14*x^7).content()
            -2
            sage: x.content()
            1
            sage: R(1).content()
            1
            sage: R(0).content()
            0
        """
        cdef ZZ_c y
        cdef Integer z = PY_NEW(Integer)
        ZZX_content(y, self.__poly)
        ZZ_to_mpz(&z.value, &y)
        return z


    def __reduce__(self):
        r"""
        Used for pickling.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: loads(dumps(x)) == x
            True
            sage: f = 2*x + 3
            sage: loads(dumps(f)) == f
            True
        """
        return Polynomial_integer_dense_ntl, \
               (self.parent(), self.list(), False, self.is_gen())

    def __getitem__(self, long n):
        r"""
        Returns coefficient of x^n, or zero if n is negative.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = 2*x^2 - 3
            sage: f[0]
            -3
            sage: f[1]
            0
            sage: f[2]
            2
            sage: f[3]
            0
            sage: f[-1]
            0
        """
        cdef Integer z = PY_NEW(Integer)
        if n < 0 or n > ZZX_deg(self.__poly):
            return z
        else:
            # Note that the NTL documentation blesses this direct access of the "rep" member in ZZX.txt.
            #  Check the "Miscellany" section.
            ZZ_to_mpz(&z.value, &self.__poly.rep.elts()[n])
            return z

    def __getslice__(self, long i, long j):
        r"""
        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = 1 + x + 2*x^2 + 3*x^3 + 4*x^4 + 5*x^5
            sage: f[2:4]
            3*x^3 + 2*x^2
            sage: f[-2:4]
            3*x^3 + 2*x^2 + x + 1
            sage: f[4:100]
            5*x^5 + 4*x^4
        """
        cdef long k
        i = max(0, i)
        j = min(j, self.degree()+1)
        v = [self[k] for k from i <= k < j]
        P = self.parent()
        return P([0] * int(i) + v)

    def _repr(self, name=None, bint latex=False):
        """
        Return string representatin of this polynomial.

        EXAMPLES:
            sage: R.<x> = ZZ['x']
            sage: (-x+1)^5
            -x^5 + 5*x^4 - 10*x^3 + 10*x^2 - 5*x + 1
        """
        if name is None:
            name = self.parent().variable_name()
        cdef long i
        all = []
        for i from ZZX_deg(self.__poly) >= i >= 0:
            sign = ZZ_sign(ZZX_coeff(self.__poly, i))
            if sign:
                if sign > 0:
                    sign_str = '+'
                    coeff_str = ZZ_to_PyString(&self.__poly.rep.elts()[i])
                else:
                    sign_str = '-'
                    coeff_str = ZZ_to_PyString(&self.__poly.rep.elts()[i])[1:]
                if i > 0:
                    if coeff_str == '1':
                        coeff_str = ''
                    elif not latex:
                        coeff_str = coeff_str + '*'
                if i > 1:
                    if latex:
                        PyList_Append(all, " %s %s%s^{%s}" % (sign_str, coeff_str, name, i))
                    else:
                        PyList_Append(all, " %s %s%s^%s" % (sign_str, coeff_str, name, i))
                elif i == 1:
                    PyList_Append(all, " %s %s%s" % (sign_str, coeff_str, name))
                else:
                    PyList_Append(all, " %s %s" % (sign_str, coeff_str))
        if len(all) == 0:
            return '0'
        leading = all[0]
        if leading[1] == '+':
            all[0] = leading[3:]
        else:
            all[0] = '-' + leading[3:]
        return ''.join(all)

    def _latex_(self, name=None):
        """
        Return the latex representation of this polynomial.

        EXAMPLES:
            sage: R.<t> = ZZ['t']
            sage: latex(t^10-t^2-5*t+1)
            t^{10} - t^{2} - 5t + 1
            sage: latex(cyclotomic_polynomial(10^5))
            x^{40000} - x^{30000} + x^{20000} - x^{10000} + 1
        """
        if name is None:
            name = self.parent().latex_variable_names()[0]
        return self._repr(name, latex=True)

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        r"""
        Returns self plus right.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = 2*x + 1
            sage: g = -3*x^2 + 6
            sage: f + g
            -3*x^2 + 2*x + 7
        """
        cdef Polynomial_integer_dense_ntl x = self._new()
        ZZX_add(x.__poly, self.__poly,
                (<Polynomial_integer_dense_ntl>right).__poly)
        return x


    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        r"""
        Return self minus right.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = 2*x + 1
            sage: g = -3*x^2 + 6
            sage: f - g
            3*x^2 + 2*x - 5
        """
        cdef Polynomial_integer_dense_ntl x = self._new()
        ZZX_sub(x.__poly, self.__poly,
                (<Polynomial_integer_dense_ntl>right).__poly)
        return x


    cdef ModuleElement _neg_c_impl(self):
        r"""
        Returns negative of self.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = 2*x - 1
            sage: -f
            -2*x + 1
        """
        cdef Polynomial_integer_dense_ntl x = self._new()
        ZZX_negate(x.__poly, self.__poly)
        return x


    def quo_rem(self, right):
        r"""
        Attempts to divide self by right, and return a quotient and remainder.

        If right is monic, then it returns (q, r) where
            self = q * right + r
        and deg(r) < deg(right).

        If right is not monic, then it returns (q, 0) where q = self/right
        if right exactly divides self, otherwise it raises an exception.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = R(range(10)); g = R([-1, 0, 1])
            sage: q, r = f.quo_rem(g)
            sage: q, r
            (9*x^7 + 8*x^6 + 16*x^5 + 14*x^4 + 21*x^3 + 18*x^2 + 24*x + 20, 25*x + 20)
            sage: q*g + r == f
            True

            sage: f = x^2
            sage: f.quo_rem(0)
            Traceback (most recent call last):
            ...
            ArithmeticError: division by zero polynomial

            sage: f = (x^2 + 3) * (2*x - 1)
            sage: f.quo_rem(2*x - 1)
            (x^2 + 3, 0)

            sage: f = x^2
            sage: f.quo_rem(2*x - 1)
            Traceback (most recent call last):
            ...
            ArithmeticError: division not exact in Z[x] (consider coercing to Q[x] first)

        """
        if not isinstance(right, Polynomial_integer_dense_ntl):
            right = self.parent()(right)
        elif self.parent() is not right.parent():
            raise TypeError

        cdef Polynomial_integer_dense_ntl _right = <Polynomial_integer_dense_ntl> right

        if ZZX_IsZero(_right.__poly):
            raise ArithmeticError, "division by zero polynomial"

        cdef ZZX_c *q, *r
        cdef Polynomial_integer_dense_ntl qq = self._new()
        cdef Polynomial_integer_dense_ntl rr = self._new()
        cdef int divisible

        if ZZ_IsOne(ZZX_LeadCoeff(_right.__poly)):
            # divisor is monic. Just do the division and remainder
            ZZX_quo_rem(&self.__poly, &_right.__poly, &r, &q)
            ZZX_swap(qq.__poly, q[0])
            ZZX_swap(rr.__poly, r[0])
            ZZX_delete(q)
            ZZX_delete(r)
        else:
            # Non-monic divisor. Check whether it divides exactly.
            q = ZZX_div(&self.__poly, &_right.__poly, &divisible)
            if divisible:
                # exactly divisible
                ZZX_swap(q[0], qq.__poly)
                ZZX_delete(q)
            else:
                # division failed: clean up and raise exception
                ZZX_delete(q)
                raise ArithmeticError, "division not exact in Z[x] (consider coercing to Q[x] first)"

        return qq, rr



    def gcd(self, right):
        r"""
        Return the GCD of self and right.  The leading
        coefficient need not be 1.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = (6*x + 47)*(7*x^2 - 2*x + 38)
            sage: g = (6*x + 47)*(3*x^3 + 2*x + 1)
            sage: f.gcd(g)
            6*x + 47
        """
        if not isinstance(right, Polynomial_integer_dense_ntl):
            right = self.parent()(right)
        elif self.parent() is not right.parent():
            raise TypeError

        # todo: we're doing an unnecessary copy here
        cdef Polynomial_integer_dense_ntl x = self._new()
        cdef ZZX_c* temp = ZZX_gcd(&self.__poly, &(<Polynomial_integer_dense_ntl>right).__poly)
        x.__poly = temp[0]
        ZZX_delete(temp)
        return x


    def lcm(self, right):
        """
        Return the LCM of self and right.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = (6*x + 47)*(7*x^2 - 2*x + 38)
            sage: g = (6*x + 47)*(3*x^3 + 2*x + 1)
            sage: h = f.lcm(g); h
            126*x^6 + 951*x^5 + 486*x^4 + 6034*x^3 + 585*x^2 + 3706*x + 1786
            sage: h == (6*x + 47)*(7*x^2 - 2*x + 38)*(3*x^3 + 2*x + 1)
            True
        """
        if not isinstance(right, Polynomial_integer_dense_ntl):
            right = self.parent()(right)
        elif self.parent() is not right.parent():
            raise TypeError

        g = self.gcd(right)
        return (self * right).quo_rem(g)[0]


    def xgcd(self, right):
        """
        Return $g, u, v$ such that \code{g = u*self + v*right}.

        If self and right are coprime as polynomials over the
        rationals, then $g$ is guaranteed to be the resultant of self
        and right, as a constant polynomial.

        EXAMPLES:
            sage: P.<x> = PolynomialRing(ZZ)
            sage: F = (x^2 + 2)*x^3; G = (x^2+2)*(x-3)
            sage: g, u, v = F.xgcd(G)
            sage: g, u, v
            (27*x^2 + 54, 1, -x^2 - 3*x - 9)
            sage: u*F + v*G
            27*x^2 + 54
            sage: x.xgcd(P(0))
            (x, 1, 0)
            sage: f = P(0)
            sage: f.xgcd(x)
            (x, 0, 1)
            sage: F = (x-3)^3; G = (x-15)^2
            sage: g, u, v = F.xgcd(G)
            sage: g, u, v
            (2985984, -432*x + 8208, 432*x^2 + 864*x + 14256)
            sage: u*F + v*G
            2985984
        """
        if not isinstance(right, Polynomial_integer_dense_ntl):
            right = self.parent()(right)
        elif self.parent() is not right.parent():
            raise TypeError

        cdef ZZX_c *s, *t
        cdef ZZ_c *r

        ZZX_xgcd(&self.__poly, &(<Polynomial_integer_dense_ntl>right).__poly, &r, &s, &t, 1)    # proof = 1
        cdef Integer rr = PY_NEW(Integer)
        ZZ_to_mpz(&rr.value, r)
        cdef Polynomial_integer_dense_ntl ss = self._new()
        cdef Polynomial_integer_dense_ntl tt = self._new()
        ss.__poly = s[0]
        tt.__poly = t[0]
        ZZ_delete(r)
        ZZX_delete(s)
        ZZX_delete(t)

        if rr == 0:
            f = self.base_extend(QQ)
            g, u, v = f.xgcd(right.base_extend(QQ))
            d = lcm([g.denominator(), u.denominator(), v.denominator()])
            R = self.parent()
            return R(d*g), R(d*u), R(d*v)
        else:
            S = self.parent()
            return S(rr), ss, tt


    cdef RingElement _mul_c_impl(self, RingElement right):
        r"""
        Returns self multiplied by right.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: (x - 2)*(x^2 - 8*x + 16)
            x^3 - 10*x^2 + 32*x - 32
        """
        cdef Polynomial_integer_dense_ntl x = self._new()
        ZZX_mul(x.__poly, self.__poly,
                (<Polynomial_integer_dense_ntl>right).__poly)
        return x


    cdef ModuleElement _lmul_c_impl(self, RingElement right):
        r"""
        Returns self multiplied by right, where right is a scalar (integer).

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: x*3
            3*x
            sage: (2*x^2 + 4)*3
            6*x^2 + 12
        """
        cdef Polynomial_integer_dense_ntl x = self._new()
        cdef ZZ_c _right

        mpz_to_ZZ(&_right, &(<Integer>right).value)
        ZZX_mul_ZZ(x.__poly, self.__poly, _right)
        return x


    cdef ModuleElement _rmul_c_impl(self, RingElement right):
        r"""
        Returns self multiplied by right, where right is a scalar (integer).

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: 3*x
            3*x
            sage: 3*(2*x^2 + 4)
            6*x^2 + 12
        """
        cdef Polynomial_integer_dense_ntl x = self._new()
        cdef ZZ_c _right

        mpz_to_ZZ(&_right, &(<Integer>right).value)
        ZZX_mul_ZZ(x.__poly, self.__poly, _right)
        return x


    def __floordiv__(self, right):
        """
        todo: write a doctest for this as soon as someone figures out
        what it's actually supposed to do
        """
        if is_Polynomial(right) and right.is_constant() and right[0] in ZZ:
            d = ZZ(right[0])
        elif (right in self.parent().base_ring()):
            d = ZZ(right)
        else:
            return Polynomial.__floordiv__(self, right)
        return self.parent()([c // d for c in self.list()], construct=True)


    def _unsafe_mutate(self, long n, value):
        r"""
        Sets coefficient of x^n to value.

        This is very unsafe, because SAGE polynomials are supposed
        to be immutable. (Shhhh don't tell anyone!)

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = 2*x^2 + 3; f
            2*x^2 + 3
            sage: f._unsafe_mutate(1, 42); f
            2*x^2 + 42*x + 3
        """
        n = int(n)
        if n < 0:
            raise IndexError, "n must be >= 0"
        value = Integer(value)
        cdef ZZ_c y
        mpz_to_ZZ(&y, &(<Integer>value).value)
        ZZX_SetCoeff(self.__poly, n, y)


    def real_root_intervals(self):
        """
        Returns isolating intervals for the real roots of this polynomial.

        EXAMPLE:
        We compute the roots of the characteristic polynomial of some Salem numbers:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = 1 - x^2 - x^3 - x^4 + x^6
            sage: f.real_root_intervals()
            [((1/2, 3/4), 1), ((1, 3/2), 1)]
        """

        from sage.rings.polynomial.real_roots import real_roots

        return real_roots(self)

##     def __copy__(self):
##         f = Polynomial_integer_dense(self.parent())
##         f.__poly = self.__poly.copy()
##         return f


    def degree(self):
        """
        Return the degree of this polynomial.  The zero polynomial
        has degree -1.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: x.degree()
            1
            sage: (x^2).degree()
            2
            sage: R(1).degree()
            0
            sage: R(0).degree()
            -1
        """
        return ZZX_deg(self.__poly)


    def discriminant(self, proof=True):
        r"""
        Return the discriminant of self, which is by definition
        $$
            (-1)^{m(m-1)/2} {\mbox{\tt resultant}}(a, a')/lc(a),
        $$
        where m = deg(a), and lc(a) is the leading coefficient of a.
        If proof is False (the default is True), then this function
        may use a randomized strategy that errors with probability no
        more than $2^{-80}$.

        EXAMPLES:
            sage: f = ntl.ZZX([1,2,0,3])
            sage: f.discriminant()
            -339
            sage: f.discriminant(proof=False)
            -339
        """
        cdef ZZ_c* temp = ZZX_discriminant(&self.__poly, proof)
        cdef Integer x = PY_NEW(Integer)
        ZZ_to_mpz(&x.value, temp)
        ZZ_delete(temp)
        return x


    def _pari_(self, variable=None):
        """
        EXAMPLES:
            sage: t = PolynomialRing(ZZ,"t").gen()
            sage: f = t^3 + 3*t - 17
            sage: pari(f)
            t^3 + 3*t - 17
        """
        if variable is None:
            variable = self.parent().variable_name()
        return pari(self.list()).Polrev(variable)


    def squarefree_decomposition(self):
        """
        Return the square-free decomposition of self.  This is
        a partial factorization of self into square-free, relatively
        prime polynomials.

        This is a wrapper for the NTL function SquareFreeDecomp.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: p = 37 * (x-1)^2 * (x-2)^2 * (x-3)^3 * (x-4)
            sage: p.squarefree_decomposition()
            (37) * (x - 4) * (x^2 - 3*x + 2)^2 * (x - 3)^3
        """

        cdef Polynomial_integer_dense_ntl p = self
        c = p.content()
        if c != 1:
            p = self.parent()(p / c)

        cdef ZZX_c** v
        cdef long* e
        cdef long i, n
        cdef Polynomial_integer_dense_ntl z
        ZZX_squarefree_decomposition(&v, &e, &n, &p.__poly)
        F = []
        for i from 0 <= i < n:
            z = self._new()
            z.__poly = v[i][0]
            F.append((z, e[i]))
            ZZX_delete(v[i])
        free(v)
        free(e)
        return Factorization(F, unit=c, sort=False)

    def _factor_pari(self):
        return Polynomial.factor(self) # uses pari for integers over ZZ

    def _factor_ntl(self):
        """
        There are ample doc-tests elsewhere that test this functionality.
        AUTHOR:
            -- Joel B. Mohler
        """
        cdef Polynomial_integer_dense_ntl fac_py
        cdef ZZ_c content
        cdef vec_pair_ZZX_long_c factors
        cdef long i
        cdef int sig_me = ZZX_deg(self.__poly)
        if sig_me > 10:
            _sig_on
        ZZX_factor(content, factors, self.__poly, 0, 0)
        if sig_me > 10:
            _sig_off
        results = []
        unit = None
        if not ZZ_IsOne(content):
            fac_py = self._new()
            ZZX_SetCoeff(fac_py.__poly, 0, content)
            if ZZX_deg(fac_py.__poly) == 0 and ZZ_to_int(fac_py.__poly.rep.elts())==-1:
                unit = fac_py
            else:
                results.append( (fac_py,1) )
        for i from 0 <= i < factors.length():
            fac_py = self._new()
            fac_py.__poly = factors.RawGet(i).a
            results.append( (fac_py,factors.RawGet(i).b) )
        return Factorization(results, unit = unit)

    def factor(self):
        """
        This function overrides the generic polynomial factorization to
        make a somewhat intelligent decision to use Pari or NTL based on
        some benchmarking.

        EXAMPLES:
            sage: R.<x>=ZZ[]
            sage: f=x^4-1
            sage: f.factor()
            (x - 1) * (x + 1) * (x^2 + 1)
            sage: f=1-x
            sage: f.factor()
            (-1) * (x - 1)
            sage: f.factor().unit()
            -1
        """
        cdef int i
        cdef int deg = ZZX_deg(self.__poly)
        # it appears that pari has a window from about degrees 30 and 300 in which it beats NTL.
        if deg < 30 or deg > 300:
            return self._factor_ntl()
        else:
            return self._factor_pari()

    def factor_mod(self, p):
        """
        Return the factorization of self modulo the prime p.

        INPUT:
            p -- prime

        OUTPUT:
            factorization of self reduced modulo p.

        EXAMPLES:
            sage: R.<x> = ZZ['x']
            sage: f = -3*x*(x-2)*(x-9) + x
            sage: f.factor_mod(3)
            x
            sage: f = -3*x*(x-2)*(x-9)
            sage: f.factor_mod(3)
            Traceback (most recent call last):
            ...
            ValueError: factorization of 0 not defined

            sage: f = 2*x*(x-2)*(x-9)
            sage: f.factor_mod(7)
            (2) * x * (x + 5)^2
        """
        from sage.rings.finite_field import FiniteField
        p = Integer(p)
        if not p.is_prime():
            raise ValueError, "p must be prime"
        f = self._pari_()
        if f * pari('Mod(1,%s)'%p) == pari(0):
            raise ValueError, "factorization of 0 not defined"
        G = f.factormod(p)
        k = FiniteField(p)
        R = sage.rings.polynomial.polynomial_ring.PolynomialRing(k, names=self.parent().variable_name())
        return R(1)._factor_pari_helper(G, unit=R(self).leading_coefficient())


    def factor_padic(self, p, prec=10):
        """
        Return p-adic factorization of self to given precision.

        INPUT:
            p -- prime
            prec -- integer; the precision

        OUTPUT:
            factorization of self reduced modulo p.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = x^2 + 1
            sage: f.factor_padic(5, 4)
            ((1 + O(5^4))*x + (2 + 5 + 2*5^2 + 5^3 + O(5^4))) * ((1 + O(5^4))*x + (3 + 3*5 + 2*5^2 + 3*5^3 + O(5^4)))

        """
        from sage.rings.padics.factory import Zp
        p = Integer(p)
        if not p.is_prime():
            raise ValueError, "p must be prime"
        prec = Integer(prec)
        if prec <= 0:
            raise ValueError, "prec must be positive"
        K = Zp(p, prec, type='capped-abs')
        R = sage.rings.polynomial.polynomial_ring.PolynomialRing(K, names=self.parent().variable_name())
        return R(self).factor()


    def list(self):
        """
        Return a new copy of the list of the underlying
        elements of self.

        EXAMPLES:
            sage: x = PolynomialRing(ZZ,'x').0
            sage: f = x^3 + 3*x - 17
            sage: f.list()
            [-17, 3, 0, 1]
            sage: f = PolynomialRing(ZZ,'x')(0)
            sage: f.list()
            []
        """
        return [self[i] for i in range(self.degree()+1)]


    def resultant(self, other, proof=True):
        """
        Returns the resultant of self and other, which must lie in the same
        polynomial ring.

        If proof = False (the default is proof=True), then this function may use a
        randomized strategy that errors with probability no more than $2^{-80}$.

        INPUT:
            other -- a polynomial

        OUTPUT:
            an element of the base ring of the polynomial ring

        EXAMPLES:
            sage: x = PolynomialRing(ZZ,'x').0
            sage: f = x^3 + x + 1;  g = x^3 - x - 1
            sage: r = f.resultant(g); r
            -8
            sage: r.parent() is ZZ
            True
        """
        cdef Polynomial_integer_dense_ntl _other = <Polynomial_integer_dense_ntl>(self.parent()._coerce_(other))
        cdef ZZ_c* temp = ZZX_resultant(&self.__poly, &_other.__poly, proof)
        cdef Integer x = PY_NEW(Integer)
        ZZ_to_mpz(&x.value, temp)
        ZZ_delete(temp)
        return x
