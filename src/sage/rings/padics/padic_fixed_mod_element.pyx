"""
Elements of p-Adic Rings with Fixed Modulus

AUTHOR:
    -- David Roe
    -- Genya Zaytman: documentation
    -- David Harvey: doctests
"""

#*****************************************************************************
#       Copyright (C) 2007 David Roe <roed@math.harvard.edu>
#                          William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

include "../../ext/gmp.pxi"
include "../../ext/interrupt.pxi"
include "../../ext/stdsage.pxi"

cimport sage.rings.padics.padic_generic_element
from sage.rings.padics.padic_generic_element cimport pAdicGenericElement

cimport sage.rings.integer
cimport sage.rings.rational
cimport sage.rings.padics.pow_computer
from sage.rings.integer cimport Integer
from sage.rings.rational cimport Rational
from sage.rings.padics.pow_computer cimport PowComputer_class

#import sage.rings.padics.padic_ring_generic_element
#import sage.rings.padics.padic_field_generic_element
#import sage.rings.padics.padic_lazy_element
import sage.rings.integer_mod
import sage.libs.pari.gen
import sage.rings.integer
import sage.rings.rational

from sage.rings.infinity import infinity
from sage.rings.integer_mod import Mod
from sage.rings.padics.precision_error import PrecisionError

#pAdicLazyElement = sage.rings.padics.padic_lazy_element.pAdicLazyElement
#pAdicGenericElement = sage.rings.padics.padic_generic_element.pAdicGenericElement
pari = sage.libs.pari.gen.pari
pari_gen = sage.libs.pari.gen.gen
PariError = sage.libs.pari.gen.PariError

cdef class pAdicFixedModElement(pAdicBaseGenericElement):
    def __init__(pAdicFixedModElement self, parent, x, absprec = None, relprec = None, empty = False):
        r"""
        INPUT:
            parent -- a pAdicRingFixedMod object.

        Types currently supported:
            Integers
            Rationals -- denominator must be relatively prime to p
            FixedMod p-adics

        Types that should be supported:
            Finite precision p-adics
            Lazy p-adics
            Elements of local extensions of THIS p-adic ring that actually lie in Zp
            Elements of IntegerModRing(p^k) for k less than or equal to the modulus

        EXAMPLES:
            sage: R = Zp(5, 20, 'fixed-mod', 'terse')

        Construct from integers:
            sage: R(3)
            3 + O(5^20)
            sage: R(75)
            75 + O(5^20)
            sage: R(0)
            0 + O(5^20)

            sage: R(-1)
            95367431640624 + O(5^20)
            sage: R(-5)
            95367431640620 + O(5^20)

        Construct from rationals:
            sage: R(1/2)
            47683715820313 + O(5^20)
            sage: R(-7875/874)
            9493096742250 + O(5^20)
            sage: R(15/425)
            Traceback (most recent call last):
            ...
            ValueError: p divides the denominator

        # todo: the above error message does not agree with the error message
        # in the corresponding capped-relative constructor

        Construct from IntegerMod:
            sage: R(Integers(125)(3))
            3 + O(5^20)
            sage: R(Integers(5)(3))
            3 + O(5^20)
            sage: R(Integers(5^30)(3))
            3 + O(5^20)
            sage: R(Integers(5^30)(1+5^23))
            1 + O(5^20)
            sage: R(Integers(49)(3))
            Traceback (most recent call last):
            ...
            TypeError: cannot coerce from the given integer mod ring (not a power of the same prime)

            sage: R(Integers(48)(3))
            Traceback (most recent call last):
            ...
            TypeError: cannot coerce from the given integer mod ring (not a power of the same prime)

        Some other conversions:
            sage: R(R(5))
            5 + O(5^20)

        # todo: doctests for converting from other types of p-adic rings

        """
        mpz_init(self.value)
        pAdicGenericElement.__init__(self,parent)
        if empty:
            return
        cdef Integer tmp
        if PY_TYPE_CHECK(x, pAdicGenericElement):
            if x.valuation() < 0:
                raise ValueError, "element has negative valuation"
            if parent.prime() != x.parent().prime():
                raise TypeError, "Cannot coerce between p-adic parents with different primes."
        #if PY_TYPE_CHECK(x, pAdicLazyElement):
        #    try:
        #        x.set_precision_absolute(absprec)
        #    except PrecisionError:
        #        pass
        #    if mpz_cmp((<pAdicLazyElement>x).value, self.prime_pow.top_power) >= 0:
        #        mpz_mod(self.value, (<pAdicLazyElement>x).value, self.prime_pow.top_power)
        #    else:
        #        mpz_set(self.value, (<pAdicLazyElement>x).value)
        #    return
        if PY_TYPE_CHECK(x, pAdicBaseGenericElement):
            tmp = <Integer> x.lift()
            if mpz_cmp(tmp.value, self.prime_pow.pow_mpz_top()[0]) >= 0:
                mpz_mod(self.value, tmp.value, self.prime_pow.pow_mpz_top()[0])
            else:
                mpz_set(self.value, tmp.value)
            return

        if isinstance(x, pari_gen):
            if x.type() == "t_PADIC":
                x = x.lift()
            if x.type() == 't_INT':
                x = Integer(x)
            elif x.type() == 't_FRAC':
                x = Rational(x)
            else:
                raise TypeError, "unsupported coercion from pari: only p-adics, integers and rationals allowed"

        if sage.rings.integer_mod.is_IntegerMod(x):
            if (<Integer>x.modulus())._is_power_of(<Integer>parent.prime()):
                x = x.lift()
            else:
                raise TypeError, "cannot coerce from the given integer mod ring (not a power of the same prime)"

        #if sage.rings.finite_field_element.is_FiniteFieldElement(x):
        #    if x.parent().order() != parent.prime():
        #        raise TypeError, "can only create p-adic element out of finite field when order of field is p"
        #    x = x.lift()

        #Now use the code below to convert from integer or rational, so don't make the next line elif

        if PY_TYPE_CHECK(x, Integer):
            self.set_from_mpz((<Integer>x).value)
        elif isinstance(x, Rational):
            if self.prime_pow.prime.divides(x.denominator()):
                raise ValueError, "p divides the denominator"
            else:
                tmp = <Integer> x % parent.prime_pow(parent.precision_cap())
                self.set_from_mpz(tmp.value)
        elif isinstance(x, (int, long)):
            tmp = <Integer> Integer(x)
            self.set_from_mpz(tmp.value)
        else:
            raise TypeError, "unable to create p-adic element"

    def __dealloc__(self):
        mpz_clear(self.value)

    def __reduce__(self):
        """
        sage: a = ZpFM(5)(-3)
        sage: type(a)
        <type 'sage.rings.padics.padic_fixed_mod_element.pAdicFixedModElement'>
        sage: loads(dumps(a)) == a
        True
        """
        return make_pAdicFixedModElement, (self.parent(), self.lift())

    cdef void set_from_mpz(pAdicFixedModElement self, mpz_t value):
        if mpz_sgn(value) == -1 or mpz_cmp(value, self.prime_pow.pow_mpz_top()[0]) >= 0:
            mpz_mod(self.value, value, self.prime_pow.pow_mpz_top()[0])
        else:
            mpz_set(self.value, value)

    cdef pAdicFixedModElement _new_c(self):
        cdef pAdicFixedModElement x
        x = PY_NEW(pAdicFixedModElement)
        x._parent = self._parent
        mpz_init(x.value)
        x.prime_pow = self.prime_pow
        return x

    def __richcmp__(left, right, op):
        return (<Element>left)._richcmp(right, op)

    def __invert__(self):
        r"""
        Returns multiplicative inverse of this element. Its valuation
        must be zero.

        EXAMPLES:
            sage: R = Zp(7, 4, 'fixed-mod', 'series')
            sage: ~R(2)
            4 + 3*7 + 3*7^2 + 3*7^3 + O(7^4)
            sage: ~R(0)
            Traceback (most recent call last):
            ...
            ValueError: cannot invert non-unit
            sage: ~R(7)
            Traceback (most recent call last):
            ...
            ValueError: cannot invert non-unit
        """
        return self._invert_c_impl()

    cdef RingElement _invert_c_impl(self):
        cdef pAdicFixedModElement ans
        if mpz_divisible_p(self.value, self.prime_pow.prime.value) != 0:
            raise ValueError, "cannot invert non-unit"
        else:
            ans = self._new_c()
            _sig_on
            mpz_invert(ans.value, self.value, self.prime_pow.pow_mpz_top()[0])
            _sig_off
            return ans

    cdef pAdicFixedModElement _lshift_c(pAdicFixedModElement self, long shift):
        cdef pAdicFixedModElement ans
        cdef unsigned long prec_cap
        if shift < 0:
            return self._rshift_c(-shift)
        prec_cap = self.prime_pow._cache_limit
        if shift >= prec_cap:
            ans = self._new_c()
            mpz_set_ui(ans.value, 0)
            return ans
        elif shift > 0:
            ans = self._new_c()
            if mpz_cmp(self.value, self.prime_pow.pow_mpz_t_tmp(prec_cap - shift)[0]) >= 0:
                mpz_mod(ans.value, self.value, self.prime_pow.pow_mpz_t_tmp(prec_cap - shift)[0])
            else:
                mpz_set(ans.value, self.value)
            mpz_mul(ans.value, ans.value, self.prime_pow.pow_mpz_t_tmp(shift)[0])
            return ans
        else:
            return self

    def __lshift__(pAdicFixedModElement self, shift):
        cdef pAdicFixedModElement ans
        if not PY_TYPE_CHECK(shift, Integer):
            shift = Integer(shift)
        if mpz_fits_slong_p((<Integer>shift).value) == 0:
            ans = self._new_c()
            mpz_set_ui(ans.value, 0)
            return ans
        return self._lshift_c(mpz_get_si((<Integer>shift).value))

    cdef pAdicFixedModElement _rshift_c(pAdicFixedModElement self, long shift):
        cdef pAdicFixedModElement ans
        cdef unsigned long prec_cap
        if shift < 0:
            return self._lshift_c(-shift)
        prec_cap = self.prime_pow._cache_limit
        if shift >= prec_cap:
            ans = self._new_c()
            mpz_set_ui(ans.value, 0)
            return ans
        elif shift > 0:
            ans = self._new_c()
            mpz_fdiv_q(ans.value, self.value, self.prime_pow.pow_mpz_t_tmp(shift)[0])
            return ans
        else:
            return self

    def __rshift__(pAdicFixedModElement self, shift):
        cdef pAdicFixedModElement ans
        if not PY_TYPE_CHECK(shift, Integer):
            shift = Integer(shift)
        if mpz_fits_slong_p((<Integer>shift).value) == 0:
            ans = self._new_c()
            mpz_set_ui(ans.value, 0)
            return ans
        return self._rshift_c(mpz_get_si((<Integer>shift).value))

    cdef ModuleElement _neg_c_impl(self):
        r"""
        Returns negative of self.

        EXAMPLES:
            sage: R = Zp(7, 4, 'fixed-mod', 'series')
            sage: -R(7)
            6*7 + 6*7^2 + 6*7^3 + O(7^4)
        """
        if mpz_sgn(self.value) == 0:
            return self
        cdef pAdicFixedModElement ans
        ans = self._new_c()
        mpz_sub(ans.value, self.prime_pow.pow_mpz_top()[0], self.value)
        return ans

    def __pow__(pAdicFixedModElement self, right, m): # NOTE: m ignored, always use self.prime_pow.pow_mpz_top()[0]
        if not PY_TYPE_CHECK(right, Integer):
            right = Integer(right) #Need to make sure that this works for p-adic exponents
        if not right and not self:
            raise ArithmeticError, "0^0 is undefined."
        cdef pAdicFixedModElement ans
        ans = self._new_c()
        _sig_on
        mpz_powm(ans.value, self.value, (<Integer>right).value, self.prime_pow.pow_mpz_top()[0])
        _sig_off
        return ans

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        r"""
        Returns sum of self and right.

        EXAMPLES:
            sage: R = Zp(7, 4, 'fixed-mod', 'series')
            sage: x = R(1721); x
            6 + 5*7^3 + O(7^4)
            sage: y = R(1373); y
            1 + 4*7^3 + O(7^4)
            sage: x + y
            7 + 2*7^3 + O(7^4)
        """
        cdef pAdicFixedModElement ans
        ans = self._new_c()
        mpz_add(ans.value, self.value, (<pAdicFixedModElement>right).value)
        if mpz_cmp(ans.value, self.prime_pow.pow_mpz_top()[0]) >= 0:
            mpz_sub(ans.value, ans.value, self.prime_pow.pow_mpz_top()[0])
        return ans

    cdef RingElement _mul_c_impl(self, RingElement right):
        r"""
        Returns product of self and right.

        EXAMPLES:
            sage: R = Zp(7, 4, 'fixed-mod', 'series')
            sage: R(3) * R(2)
            6 + O(7^4)
            sage: R(1/2) * R(2)
            1 + O(7^4)
        """
        cdef pAdicFixedModElement ans
        ans = self._new_c()
        mpz_mul(ans.value, self.value, (<pAdicFixedModElement>right).value)
        mpz_fdiv_r(ans.value, ans.value, self.prime_pow.pow_mpz_top()[0])
        return ans

    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        r"""
        Returns difference of self and right.

        EXAMPLES:
            sage: R = Zp(7, 4, 'fixed-mod', 'series')
            sage: x = R(1721); x
            6 + 5*7^3 + O(7^4)
            sage: y = R(1373); y
            1 + 4*7^3 + O(7^4)
            sage: x - y
            5 + 7^3 + O(7^4)
        """
        cdef pAdicFixedModElement ans
        ans = self._new_c()
        mpz_sub(ans.value, self.value, (<pAdicFixedModElement>right).value)
        if mpz_sgn(ans.value) == -1:
            mpz_add(ans.value, ans.value, self.prime_pow.pow_mpz_top()[0])
        return ans

    cdef RingElement _div_c_impl(self, RingElement right):
        r"""
        Returns quotient of self and right. The latter must have
        valuation zero.

        EXAMPLES:
            sage: R = Zp(7, 4, 'fixed-mod', 'series')
            sage: R(3) / R(2)
            5 + 3*7 + 3*7^2 + 3*7^3 + O(7^4)
            sage: R(5) / R(0)
            Traceback (most recent call last):
            ...
            ValueError: cannot invert non-unit
            sage: R(7) / R(49)
            Traceback (most recent call last):
            ...
            ValueError: cannot invert non-unit
        """
        cdef int t
        cdef pAdicFixedModElement ans
        if mpz_divisible_p((<pAdicFixedModElement>right).value, self.prime_pow.prime.value) != 0:
            raise ValueError, "cannot invert non-unit"
        else:
            ans = self._new_c()
            _sig_on
            mpz_invert(ans.value, (<pAdicFixedModElement>right).value, self.prime_pow.pow_mpz_top()[0])
            mpz_mul(ans.value, ans.value, self.value)
            mpz_fdiv_r(ans.value, ans.value, self.prime_pow.pow_mpz_top()[0])
            _sig_off
            return ans

    def add_bigoh(self, absprec):
        """
        Returns a new element with precision decreased to absprec.

        INPUT:
            self -- a p-adic element
            absprec -- an integer
        OUTPUT:
            element -- self with precision set to the minimum of
                       self's precision and absprec

        EXAMPLES:
            sage: R = Zp(7,4,'fixed-mod','series'); a = R(8); a.add_bigoh(1)
            1 + O(7^4)
        """
        cdef pAdicFixedModElement ans
        if not PY_TYPE_CHECK(absprec, Integer):
            absprec = Integer(absprec)
        if mpz_cmp_ui((<Integer>absprec).value, self.prime_pow._cache_limit) >= 0:
            return self
        ans = self._new_c()
        mpz_mod(ans.value, self.value, self.prime_pow.pow_mpz_t_tmp(mpz_get_ui((<Integer>absprec).value))[0])
        return ans

    def copy(self):
        cdef pAdicFixedModElement ans
        ans = self._new_c()
        mpz_set(ans.value, self.value)
        return ans

    def exp_artin_hasse(self):
        raise NotImplementedError

    def gamma(self):
        raise NotImplementedError

    def is_zero(self, absprec = None):
        r"""
        Returns whether self is zero modulo $p^{\mbox{absprec}}$.

        INPUT:
            self -- a p-adic element
            absprec -- an integer
        OUTPUT:
            boolean -- whether self is zero

        """
        if absprec is None:
            return mpz_sgn(self.value) == 0
        if not PY_TYPE_CHECK(absprec, Integer):
            absprec = Integer(absprec)
        cdef unsigned long aprec
        aprec = mpz_get_ui((<Integer>absprec).value)
        if aprec >= self.prime_pow._cache_limit:
            return mpz_sgn(self.value) == 0
        cdef mpz_t tmp
        mpz_init(tmp)
        mpz_mod(tmp, self.value, self.prime_pow.pow_mpz_t_tmp(aprec)[0])
        if mpz_sgn(tmp) == 0:
            mpz_clear(tmp)
            return True
        else:
            mpz_clear(tmp)
            return False

    def is_equal_to(self, right, absprec = None): #assumes they have the same parent
        r"""
        Returns whether self is equal to right modulo $p^{\mbox{absprec}}$.

        INPUT:
            self -- a p-adic element
            right -- a p-addic element with the same parent
            absprec -- a positive integer
        OUTPUT:
            boolean -- whether self is equal to right

        """
        if absprec is None:
            return mpz_cmp(self.value, (<pAdicFixedModElement>right).value) == 0
        if not PY_TYPE_CHECK(absprec, Integer):
            absprec = Integer(absprec)
        if absprec < 0:
            return True
        cdef unsigned long aprec
        aprec = mpz_get_ui((<Integer>absprec).value)
        if aprec >= self.prime_pow._cache_limit:
            return mpz_cmp(self.value, (<pAdicFixedModElement>right).value) == 0
        cdef mpz_t tmp1, tmp2
        mpz_init(tmp1)
        mpz_init(tmp2)
        mpz_mod(tmp1, self.value, self.prime_pow.pow_mpz_t_tmp(aprec)[0])
        mpz_mod(tmp2, (<pAdicFixedModElement>right).value, self.prime_pow.pow_mpz_t_tmp(aprec)[0])
        if mpz_cmp(tmp1, tmp2) == 0:
            mpz_clear(tmp1)
            mpz_clear(tmp2)
            return True
        else:
            mpz_clear(tmp1)
            mpz_clear(tmp2)
            return False

    def lift(self):
        r"""
        Return an integer congruent to self modulo self's precision.

        INPUT:
            self -- a p-adic element
        OUTPUT:
            integer -- a integer congruent to self mod $p^{\mbox{prec}}$
        EXAMPLES:
            sage: R = Zp(7,4,'fixed-mod'); a = R(8); a.lift()
            8
            sage: type(a.lift())
            <type 'sage.rings.integer.Integer'>
        """
        return self.lift_c()

    cdef Integer lift_c(pAdicFixedModElement self):
        cdef Integer ans
        ans = PY_NEW(Integer)
        mpz_set(ans.value, self.value)
        return ans

    def lift_to_precision(self, absprec):
        return self

    def list(self, lift_mode = 'simple'):
        r"""
        Returns a list of coefficients of p starting with $p^0$
        INPUT:
            self -- a p-adic element
            lift_mode -- 'simple', 'smallest' or 'teichmuller' (default 'simple')
        OUTPUT:
            list -- the list of coeficients of self

        NOTES:
        Returns a list [a_0, a_1, \ldots, a_n] so that each a_i is an integer
        and \sum_{i = 0}^n a_i * p^i = self, modulo the precision cap.
        If lift_mode = 'simple', 0 <= a_i < p.
        If lift_mode = 'smallest', -p/2 < a_i <= p/2.
        If lift_mode = 'teichmuller', a_i^p = a_i, modulo the precision cap.

        EXAMPLES:
        sage: R = Zp(7,4,'fixed-mod'); a = R(2*7+7**2); a.list()
        [0, 2, 1]
        """
        if lift_mode == 'teichmuller':
            return self.teichmuller_list()
        return self.base_p_list(self.value, lift_mode)

    cdef object teichmuller_list(pAdicFixedModElement self):
        # May eventually want to add a dict to store teichmuller lifts already seen, if p small enough
        cdef unsigned long curpower, preccap
        cdef mpz_t tmp, tmp2
        cdef pAdicFixedModElement list_elt
        ans = PyList_New(0)
        preccap = self.prime_pow._cache_limit
        curpower = preccap
        mpz_init_set(tmp, self.value)
        while mpz_sgn(tmp) != 0:
            curpower -= 1
            list_elt = self._new_c()
            mpz_mod(list_elt.value, tmp, self.prime_pow.prime.value)
            tmp2 = self.prime_pow.pow_mpz_t(preccap)[0]
            sage.rings.padics.padic_generic_element.teichmuller_set_c(list_elt.value, self.prime_pow.prime.value, tmp2)
            if preccap > self.prime_pow.cache_limit and preccap != self.prime_pow.prec_cap:
                mpz_clear(tmp2)
            mpz_sub(tmp, tmp, list_elt.value)
            mpz_divexact(tmp, tmp, self.prime_pow.prime.value)
            mpz_mod(tmp, tmp, self.prime_pow.pow_mpz_t_tmp(curpower)[0])
            PyList_Append(ans, list_elt)
        mpz_clear(tmp)
        return ans

    def _teichmuller_set(self, Integer n, Integer absprec):
        cdef unsigned long aprec
        cdef mpz_t tmp
        mpz_set(self.value, n.value)
        if mpz_fits_ulong_p(absprec.value) == 0:
            aprec = self.prime_pow._cache_limit
        if mpz_sgn(absprec.value) != 1:
            raise ValueError, "can only compute to positive precision"
        aprec = mpz_get_ui(absprec.value)
        if aprec > self.prime_pow._cache_limit:
            aprec = self.prime_pow._cache_limit
        tmp = self.prime_pow.pow_mpz_t(aprec)[0]
        sage.rings.padics.padic_generic_element.teichmuller_set_c(self.value, self.prime_pow.prime.value, tmp)
        if aprec > self.prime_pow.cache_limit and aprec != self.prime_pow.prec_cap:
            mpz_clear(tmp)

    def multiplicative_order(self):
        r"""
        Returns the minimum possible multiplicative order of self.

        INPUT:
            self -- a p-adic element
        OUTPUT:
            integer -- the multiplicative order of self.  This is the minimum multiplicative order of all elements of Z_p lifting self to infinite precision.
        """
        cdef mpz_t tmp
        cdef Integer ans
        if mpz_divisible_p(self.value, self.prime_pow.prime.value):
            return infinity
        if mpz_cmp_ui(self.value, 1):
            ans = PY_NEW(Integer)
            mpz_set_ui(ans.value, 1)
            return ans
        mpz_init(tmp)
        mpz_sub_ui(tmp, self.prime_pow.pow_mpz_top()[0], 1)
        if mpz_cmp(self.value, tmp) == 0:
            ans = PY_NEW(Integer)
            mpz_set_ui(ans.value, 2)
            return ans
        # check if self is an approximation to a teichmuller lift:
        mpz_powm(tmp, self.value, self.prime_pow.prime.value, self.prime_pow.pow_mpz_top()[0])
        if mpz_cmp(tmp, self.value) == 0:
            mpz_clear(tmp)
            return self.residue(1).multiplicative_order()
        else:
            mpz_clear(tmp)
            return infinity

    def padded_list(self, n, list_mode = 'simple'):
        """
        Returns a list of coefficients of p starting with $p^0$ up to $p^n$ exclusive (padded with zeros if needed)
        INPUT:

            self -- a p-adic element
            n - an integer
        OUTPUT:
            list -- the list of coeficients of self
        EXAMPLES:
            sage: R = Zp(7,4,'fixed-mod'); a = R(2*7+7**2); a.padded_list(5)
                [0, 2, 1, 0, 0]

        NOTE:
            this differs from the padded_list method of padic_field_element
            the slice operators throw an error if asked for a slice above the precision, while this function works
        """
        if list_mode == 'simple' or list_mode == 'smallest':
            zero = Integer(0)
        else:
            zero = self.parent()(0)
        L = self.list()
        return L[:n] + [zero] * (n - len(L))

    def precision_absolute(self):
        """
        Returns the absolute precision of self
         INPUT:
            self -- a p-adic element
        OUTPUT:
            integer -- the absolute precision of self
        EXAMPLES:
            sage: R = Zp(7,4,'fixed-mod'); a = R(7); a.precision_absolute()
            4
        """
        return self.parent().precision_cap()

    def precision_relative(self):
        r"""
        Returns the relative precision of self
         INPUT:
            self -- a p-adic element
        OUTPUT:
            integer -- the relative precision of self
        EXAMPLES:
            sage: R = Zp(7,4,'fixed-mod'); a = R(7); a.precision_relative()
            3
            sage: a = R(0); a.precision_relative()
            0
        """
        cdef unsigned long diff
        cdef Integer ans
        ans = PY_NEW(Integer)
        diff = self.prime_pow._cache_limit - self.valuation_c()
        mpz_set_si(ans.value, diff)
        return ans

    def residue(self, absprec):
        r"""
        Reduces this mod $p^prec$

        INPUT:
            self -- a p-adic element
            prec - an integer

        OUTPUT:
            element of Z/(p^prec Z) -- self reduced mod p^prec

        EXAMPLES:
            sage: R = Zp(7,4,'fixed-mod'); a = R(8); a.residue(1)
            1
        """
        cdef Integer selfvalue, modulus
        selfvalue = PY_NEW(Integer)
        modulus = PY_NEW(Integer)
        mpz_set(selfvalue.value, self.value)
        cdef unsigned long aprec
        if not PY_TYPE_CHECK(absprec, Integer):
            absprec = Integer(absprec)
        if mpz_fits_ulong_p((<Integer>absprec).value) == 0:
            raise ValueError, "When calling residue, use the exponent of p, not the integer p^exp."
        else:
            aprec = mpz_get_ui((<Integer>absprec).value)
        if aprec > self.prime_pow._cache_limit:
            _sig_on
            mpz_pow_ui(modulus.value, self.prime_pow.prime.value, aprec)
            _sig_off
        else:
            mpz_set(modulus.value, self.prime_pow.pow_mpz_t_tmp(aprec)[0])
        return Mod(selfvalue, modulus)

    #def square_root(self):
    #    r"""
    #    Returns the square root of this p-adic number

    #    INPUT:
    #        self -- a p-adic element
    #    OUTPUT:
    #        p-adic element -- the square root of this p-adic number

    #        The square root chosen is the one whose reduction mod p is in
    #        the range [0, p/2).

    #        Note that because this is a fixed modulus ring, garbage digits
    #        may be introduced, if either
    #        (a) the valuation of the input is positive, or
    #        (b) p = 2.

    #        If no square root exists, a ValueError is raised.
    #        (This may be changed later to return an element of an extension
    #        field.)

    #    EXAMPLES:
    #        sage: R = Zp(3,20,'fixed-mod')
    #        sage: R(0).square_root()
    #            O(3^20)
    #        sage: R(1).square_root()
    #            1 + O(3^20)
    #        sage: R(2).square_root()
    #        Traceback (most recent call last):
    #        ...
    #        ValueError: element is not a square
    #        sage: R(4).square_root() == R(-2)
    #            True
    #        sage: R(9).square_root()
    #            3 + O(3^20)
    #        sage: R2 = Zp(2,20,'fixed-mod')
    #        sage: R2(0).square_root()
    #            O(2^20)
    #        sage: R2(1).square_root()
    #            1 + O(2^20)
    #        sage: R2(4).square_root()
    #            2 + O(2^20)
    #        sage: R2(9).square_root() == R2(3) or R2(9).square_root() == R2(-3)
    #            True
    #        sage: R2(17).square_root()
    #            1 + 2^3 + 2^5 + 2^6 + 2^7 + 2^9 + 2^10 + 2^13 + 2^16 + 2^17 + O(2^20)
    #        sage: R3 = Zp(5,20,'fixed-mod', 'terse')
    #        sage: R3(0).square_root()
    #            0 + O(5^20)
    #        sage: R3(1).square_root()
    #            1 + O(5^20)
    #        sage: R3(-1).square_root() == R3.teichmuller(2) or R3(-1).square_root() == R3.teichmuller(3)
    #            True
    #    """
    #    #todo: make more efficient
    #    try:
    #        # use pari
    #        return self.parent()(pari(self).sqrt())
    #    except PariError:
    #        # todo: should eventually change to return an element of
    #        # an extension field
    #        raise ValueError, "element is not a square"

    def unit_part(self):
        r"""
        Returns the unit part of self.

        If the valuation of self is positive, then the high digits of the
        result will be zero.

        INPUT:
            self -- a p-adic element

        OUTPUT:
            p-adic element -- the unit part of self

        EXAMPLES:
            sage: R = Zp(17, 4, 'fixed-mod')
            sage: R(5).unit_part()
            5 + O(17^4)
            sage: R(18*17).unit_part()
            1 + 17 + O(17^4)
            sage: R(0).unit_part()
            O(17^4)
            sage: type(R(5).unit_part())
            <type 'sage.rings.padics.padic_fixed_mod_element.pAdicFixedModElement'>
        """
        return self.unit_part_c()

    cdef pAdicFixedModElement unit_part_c(pAdicFixedModElement self):
        cdef pAdicFixedModElement ans
        if mpz_sgn(self.value) == 0:
            return self
        elif mpz_divisible_p(self.value, self.prime_pow.prime.value):
            ans = self._new_c()
            mpz_remove(ans.value, self.value, self.prime_pow.prime.value)
            return ans
        else:
            return self

    def valuation(self):
        """
        Returns the valuation of self.

        If self is zero, the valuation returned is the precision of the ring.

        INPUT:
            self -- a p-adic element
        OUTPUT:
            integer -- the valuation of self.

        EXAMPLES:
            sage: R = Zp(17, 4,'fixed-mod')
            sage: a = R(2*17^2)
            sage: a.valuation()
            2
            sage: R = Zp(5, 4,'fixed-mod')
            sage: R(0).valuation()
            4
            sage: R(1).valuation()
            0
            sage: R(2).valuation()
            0
            sage: R(5).valuation()
            1
            sage: R(10).valuation()
            1
            sage: R(25).valuation()
            2
            sage: R(50).valuation()
            2
        """
        cdef Integer ans
        ans = PY_NEW(Integer)
        mpz_set_si(ans.value, self.valuation_c())
        return ans

    cdef unsigned long valuation_c(self):
        if mpz_sgn(self.value) == 0:
            return self.prime_pow._cache_limit
        cdef mpz_t tmp
        cdef unsigned long ans
        mpz_init(tmp)
        ans = mpz_remove(tmp, self.value, self.prime_pow.prime.value)
        mpz_clear(tmp)
        return ans

    def val_unit(self):
        return self.val_unit_c()

    cdef val_unit_c(self):
        cdef Integer val
        cdef pAdicFixedModElement unit
        if mpz_sgn(self.value) == 0:
            return (self.parent().precision_cap(), self)
        val = PY_NEW(Integer)
        unit = self._new_c()
        mpz_set_ui(val.value, mpz_remove(unit.value, self.value, self.prime_pow.prime.value))
        return (val, unit)

    def __hash__(self):
        return hash(self.lift_c())

def make_pAdicFixedModElement(parent, value):
    return parent(value)
