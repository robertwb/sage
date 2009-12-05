import sys

include "../ext/cdefs.pxi"
include "../ext/gmp.pxi"
include "../ext/interrupt.pxi"
include "../ext/stdsage.pxi"

from sage.rings.all import GF
from sage.libs.flint.zmod_poly cimport *
from sage.structure.element cimport Element, ModuleElement, RingElement
from sage.rings.integer_ring import ZZ
from sage.rings.fraction_field import FractionField_generic, FractionField_1poly_field
from sage.rings.finite_rings.integer_mod cimport IntegerMod_int
from sage.rings.integer cimport Integer
from sage.rings.polynomial.polynomial_zmod_flint cimport Polynomial_zmod_flint
import sage.algebras.algebra

from sage.rings.finite_rings.integer_mod cimport jacobi_int, mod_inverse_int, mod_pow_int

class FpT(FractionField_1poly_field):
    """
    This class represents the fraction field GF(p)(T) for `2 < p < 2^16`.

    EXAMPLES::

        sage: R.<T> = GF(71)[]
        sage: K = FractionField(R); K
        Fraction Field of Univariate Polynomial Ring in T over Finite Field of size 71
        sage: 1-1/T
        (T + 70)/T
        sage: parent(1-1/T) is K
        True
    """
    def __init__(self, R, names=None):  # we include names so that one can use the syntax K.<t> = FpT(GF(5)['t']).  It's actually ignored
        """
        INPUT:

        - ``R`` -- A polynomial ring over a finite field of prime order `p` with `2 < p < 2^16`

        EXAMPLES::

            sage: R.<x> = GF(31)[]
            sage: K = R.fraction_field(); K
            Fraction Field of Univariate Polynomial Ring in x over Finite Field of size 31
        """
        cdef long p = R.base_ring().characteristic()
        assert 2 < p < 2**16
        self.p = p
        self.poly_ring = R
        FractionField_1poly_field.__init__(self, R, element_class = FpTElement)
        self._populate_coercion_lists_(coerce_list=[Polyring_FpT_coerce(self), Fp_FpT_coerce(self), ZZ_FpT_coerce(self)])

    def __iter__(self):
        """
        Returns an iterator over this fraction field.

        EXAMPLES::

            sage: R.<t> = GF(3)[]; K = R.fraction_field()
            sage: iter(K)
            <sage.rings.fraction_field_FpT.FpT_iter object at ...>
        """
        return self.iter()

    def iter(self, bound=None, start=None):
        """
            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(5)['t'])
            sage: list(R.iter(2))[350:355]
            [(t^2 + t + 1)/(t + 2),
             (t^2 + t + 2)/(t + 2),
             (t^2 + t + 4)/(t + 2),
             (t^2 + 2*t + 1)/(t + 2),
             (t^2 + 2*t + 2)/(t + 2)]
        """
        return FpT_iter(self, bound, start)

cdef class FpTElement(RingElement):
    """
    An element of an FpT fraction field.
    """

    def __init__(self, parent, numer, denom=1, coerce=True, reduce=True):
        """
        INPUT:

        - parent -- the Fraction field containing this element
        - numer -- something that can be converted into the polynomial ring, giving the numerator
        - denom -- something that can be converted into the polynomial ring, giving the numerator (default 1)

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(5)['t'])
            sage: R(7)
            2

        """
        RingElement.__init__(self, parent)
        if coerce:
            numer = parent.poly_ring(numer)
            denom = parent.poly_ring(denom)
        self.p = parent.p
        zmod_poly_init(self._numer, self.p)
        zmod_poly_init(self._denom, self.p)
        self.initalized = True
        cdef long n
        for n, a in enumerate(numer):
            zmod_poly_set_coeff_ui(self._numer, n, a)
        for n, a in enumerate(denom):
            zmod_poly_set_coeff_ui(self._denom, n, a)
        if reduce:
            normalize(self._numer, self._denom, self.p)

    def __dealloc__(self):
        """
        Deallocation.

        EXAMPLES::

            sage: K = GF(11)['t'].fraction_field()
            sage: t = K.gen()
            sage: del t # indirect doctest
        """
        if self.initalized:
            zmod_poly_clear(self._numer)
            zmod_poly_clear(self._denom)

    def __reduce__(self):
        """
        For pickling.

        TESTS::

            sage: K = GF(11)['t'].fraction_field()
            sage: loads(dumps(K.gen()))
            t
            sage: loads(dumps(1/K.gen()))
            1/t
        """
        return (unpickle_FpT_element,
                (self._parent, self.numer(), self.denom()))

    cdef FpTElement _new_c(self):
        """
        Creates a new FpTElement in the same field, leaving the value to be initialized.
        """
        cdef FpTElement x = <FpTElement>PY_NEW(FpTElement)
        x._parent = self._parent
        x.p = self.p
        zmod_poly_init_precomp(x._numer, x.p, self._numer.p_inv)
        zmod_poly_init_precomp(x._denom, x.p, self._numer.p_inv)
        x.initalized = True
        return x

    cdef FpTElement _copy_c(self):
        """
        Creates a new FpTElement in the same field, with the same value as self.
        """
        cdef FpTElement x = <FpTElement>PY_NEW(FpTElement)
        x._parent = self._parent
        x.p = self.p
        zmod_poly_init2_precomp(x._numer, x.p, self._numer.p_inv, self._numer.length)
        zmod_poly_init2_precomp(x._denom, x.p, self._denom.p_inv, self._denom.length)
        zmod_poly_set(x._numer, self._numer)
        zmod_poly_set(x._denom, self._denom)
        x.initalized = True
        return x

    def numer(self):
        """
        Returns the numerator of this element, as an element of the polynomial ring.

        EXAMPLES::

            sage: K = GF(11)['t'].fraction_field()
            sage: t = K.gen(0); a = (t + 1/t)^3 - 1
            sage: a.numer()
            t^6 + 3*t^4 + 10*t^3 + 3*t^2 + 1
        """
        return self.numerator()

    cpdef numerator(self):
        """
        Returns the numerator of this element, as an element of the polynomial ring.

        EXAMPLES::

            sage: K = GF(11)['t'].fraction_field()
            sage: t = K.gen(0); a = (t + 1/t)^3 - 1
            sage: a.numerator()
            t^6 + 3*t^4 + 10*t^3 + 3*t^2 + 1
        """
        cdef Polynomial_zmod_flint res = <Polynomial_zmod_flint>PY_NEW(Polynomial_zmod_flint)
        zmod_poly_init2_precomp(&res.x, self.p, self._numer.p_inv, self._numer.length)
        zmod_poly_set(&res.x, self._numer)
        res._parent = self._parent.poly_ring
        return res

    def denom(self):
        """
        Returns the denominator of this element, as an element of the polynomial ring.

        EXAMPLES::

            sage: K = GF(11)['t'].fraction_field()
            sage: t = K.gen(0); a = (t + 1/t)^3 - 1
            sage: a.denom()
            t^3
        """
        return self.denominator()

    cpdef denominator(self):
        """
        Returns the denominator of this element, as an element of the polynomial ring.

        EXAMPLES::

            sage: K = GF(11)['t'].fraction_field()
            sage: t = K.gen(0); a = (t + 1/t)^3 - 1
            sage: a.denominator()
            t^3
        """
        cdef Polynomial_zmod_flint res = <Polynomial_zmod_flint>PY_NEW(Polynomial_zmod_flint)
        zmod_poly_init2_precomp(&res.x, self.p, self._denom.p_inv, self._denom.length)
        zmod_poly_set(&res.x, self._denom)
        res._parent = self._parent.poly_ring
        return res

    def __call__(self, *args, **kwds):
        """
        EXAMPLES::

            sage: K = Frac(GF(5)['t'])
            sage: t = K.gen()
            sage: t(3)
            3
            sage: f = t^2/(1-t)
            sage: f(2)
            1
            sage: f(t)
            4*t^2/(t + 4)
            sage: f(t^3)
            4*t^6/(t^3 + 4)
            sage: f((t+1)/t^3)
            (t^2 + 2*t + 1)/(t^6 + 4*t^4 + 4*t^3)
        """
        return self.numer()(*args, **kwds) / self.denom()(*args, **kwds)

    def subs(self, *args, **kwds):
        """
        EXAMPLES::

            sage: K = Frac(GF(11)['t'])
            sage: t = K.gen()
            sage: f = (t+1)/(t-1)
            sage: f.subs(t=2)
            3
            sage: f.subs(X=2)
            (t + 1)/(t + 10)
        """
        return self.numer().subs(*args, **kwds) / self.denom().subs(*args, **kwds)

    def valuation(self, v):
        """
        Returns the valuation of self at `v`.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: f = (t+1)^2 * (t^2+t+1) / (t-1)^3
            sage: f.valuation(t+1)
            2
            sage: f.valuation(t-1)
            -3
            sage: f.valuation(t)
            0
        """
        return self.numer().valuation(v) - self.denom().valuation(v)

    def factor(self):
        """
        EXAMPLES::

            sage: K = Frac(GF(5)['t'])
            sage: t = K.gen()
            sage: f = 2 * (t+1) * (t^2+t+1)^2 / (t-1)
            sage: factor(f)
            (2) * (t + 4)^-1 * (t + 1) * (t^2 + t + 1)^2
        """
        return self.numer().factor() / self.denom().factor()

    def _repr_(self):
        """
        Returns a string representation of this element.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(17)['t'])
            sage: -t # indirect doctest
            16*t
            sage: 1/t
            1/t
            sage: 1/(t+1)
            1/(t + 1)
            sage: 1-t/t
            0
            sage: (1-t)/t
            (16*t + 1)/t
        """
        if zmod_poly_degree(self._denom) == 0 and zmod_poly_get_coeff_ui(self._denom, 0) == 1:
            return repr(self.numer())
        else:
            numer_s = repr(self.numer())
            denom_s = repr(self.denom())
            if '-' in numer_s or '+' in numer_s:
                numer_s = "(%s)" % numer_s
            if '-' in denom_s or '+' in denom_s:
                denom_s = "(%s)" % denom_s
            return "%s/%s" % (numer_s, denom_s)

    def _latex_(self):
        r"""
        Returns a latex representation of this element.

        EXAMPLES::

            sage: K = GF(7)['t'].fraction_field(); t = K.gen(0)
            sage: latex(t^2 + 1) # indirect doctest
            t^{2} + 1
            sage: latex((t + 1)/(t-1))
            \frac{t + 1}{t + 6}
        """
        if zmod_poly_degree(self._denom) == 0 and zmod_poly_get_coeff_ui(self._denom, 0) == 1:
            return self.numer()._latex_()
        else:
            return "\\frac{%s}{%s}" % (self.numer()._latex_(), self.denom()._latex_())

    def __richcmp__(left, right, int op):
        """
        EXAMPLES::

            sage: K = Frac(GF(5)['t']); t = K.gen()
            sage: t == 1
            False
            sage: t + 1 < t^2
            True
        """
        return (<Element>left)._richcmp(right, op)

    cdef int _cmp_c_impl(self, Element other) except -2:
        """
        Compares this with another element.

        TESTS::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(7)['t'])
            sage: t == t
            True
            sage: t == -t
            False
            sage: -t == 6*t
            True
            sage: 1/t == 1/t
            True
            sage: 1/t == 1/(t+1)
            False
            sage: 2*t/t == 2
            True
            sage: 2*t/2 == t
            True
        """
        # They are normalized.
        if (zmod_poly_equal(self._numer, (<FpTElement>other)._numer) and
            zmod_poly_equal(self._denom, (<FpTElement>other)._denom)):
            return 0
        else:
            return -1

    def __hash__(self):
        """
        Returns a hash value for this element.

        TESTS::

            sage: from sage.rings.fraction_field_FpT import *
            sage: K.<t> = FpT(GF(7)['t'])
            sage: hash(K(0))
            0
            sage: hash(K(5))
            5
            sage: set([1, t, 1/t, t, t, 1/t, 1+1/t, t/t])
            set([1, t, 1/t, (t + 1)/t])
        """
        if self.denom() == 1:
            return hash(self.numer())
        return hash((self.numer(), self.numer()))

    def __neg__(self):
        """
        Negates this element.

        EXAMPLES::

            sage: K = GF(5)['t'].fraction_field(); t = K.gen(0)
            sage: a = (t^2 + 2)/(t-1)
            sage: -a # indirect doctest
            (4*t^2 + 3)/(t + 4)
        """
        cdef FpTElement x = self._copy_c()
        zmod_poly_neg(x._numer, x._numer)
        return x

    def __invert__(self):
        """
        Returns the multiplicative inverse of this element.

        EXAMPLES::

            sage: K = GF(5)['t'].fraction_field(); t = K.gen(0)
            sage: a = (t^2 + 2)/(t-1)
            sage: ~a # indirect doctest
            (t + 4)/(t^2 + 2)
        """
        if zmod_poly_degree(self._numer) == -1:
            raise ZeroDivisionError
        cdef FpTElement x = self._copy_c()
        zmod_poly_swap(x._numer, x._denom)
        return x

    cpdef ModuleElement _add_(self, ModuleElement _other):
        """
        Returns the sum of this fraction field element and another.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(7)['t'])
            sage: t + t # indirect doctest
            2*t
            sage: (t + 3) + (t + 10)
            2*t + 6
            sage: sum([t] * 7)
            0
            sage: 1/t + t
            (t^2 + 1)/t
            sage: 1/t + 1/t^2
            (t + 1)/t^2
        """
        cdef FpTElement other = <FpTElement>_other
        cdef FpTElement x = self._new_c()
        zmod_poly_mul(x._numer, self._numer, other._denom)
        zmod_poly_mul(x._denom, self._denom, other._numer) # use x._denom as a temp
        zmod_poly_add(x._numer, x._numer, x._denom)
        zmod_poly_mul(x._denom, self._denom, other._denom)
        normalize(x._numer, x._denom, self.p)
        return x

    cpdef ModuleElement _sub_(self, ModuleElement _other):
        """
        Returns the difference of this fraction field element and another.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(7)['t'])
            sage: t - t # indirect doctest
            0
            sage: (t + 3) - (t + 11)
            6
        """
        cdef FpTElement other = <FpTElement>_other
        cdef FpTElement x = self._new_c()
        zmod_poly_mul(x._numer, self._numer, other._denom)
        zmod_poly_mul(x._denom, self._denom, other._numer) # use x._denom as a temp
        zmod_poly_sub(x._numer, x._numer, x._denom)
        zmod_poly_mul(x._denom, self._denom, other._denom)
        normalize(x._numer, x._denom, self.p)
        return x

    cpdef RingElement _mul_(self, RingElement _other):
        """
        Returns the product of this fraction field element and another.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(7)['t'])
            sage: t * t # indirect doctest
            t^2
            sage: (t + 3) * (t + 10)
            t^2 + 6*t + 2
        """
        cdef FpTElement other = <FpTElement>_other
        cdef FpTElement x = self._new_c()
        zmod_poly_mul(x._numer, self._numer, other._numer)
        zmod_poly_mul(x._denom, self._denom, other._denom)
        normalize(x._numer, x._denom, self.p)
        return x

    cpdef RingElement _div_(self, RingElement _other):
        """
        Returns the quotient of this fraction field element and another.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(5)['t'])
            sage: t / t # indirect doctest
            1
            sage: (t + 3) / (t + 11)
            (t + 3)/(t + 1)
            sage: (t^2 + 2*t + 1) / (t + 1)
            t + 1
        """
        cdef FpTElement other = <FpTElement>_other
        if zmod_poly_degree(other._numer) == -1:
            raise ZeroDivisionError
        cdef FpTElement x = self._new_c()
        zmod_poly_mul(x._numer, self._numer, other._denom)
        zmod_poly_mul(x._denom, self._denom, other._numer)
        normalize(x._numer, x._denom, self.p)
        return x

    cpdef FpTElement next(self):
        """
        This function iterates through all polynomials, returning the "next" polynomial after this one.

        The strategy is as follows:

        - We always leave the denominator monic.

        - We progress through the elements with both numerator and denominator monic, and with the denominator less than the numerator.
          For each such, we output all the scalar multiples of it, then all of the scalar multiples of its inverse.

        - So if the leading coefficient of the numerator is less than p-1, we scale the numerator to increase it by 1.

        - Otherwise, we consider the multiple with numerator and denominator monic.

          - If the numerator is less than the denominator (lexicographically), we return the inverse of that element.

          - If the numerator is greater than the denominator, we invert, and then increase the numerator (remaining monic) until we either get something relatively prime to the new denominator, or we reach the new denominator.  In this case, we increase the denominator and set the numerator to 1.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(3)['t'])
            sage: a = R(0)
            sage: for _ in range(30):
            ...       a = a.next()
            ...       print a
            ...
            1
            2
            1/t
            2/t
            t
            2*t
            1/(t + 1)
            2/(t + 1)
            t + 1
            2*t + 2
            t/(t + 1)
            2*t/(t + 1)
            (t + 1)/t
            (2*t + 2)/t
            1/(t + 2)
            2/(t + 2)
            t + 2
            2*t + 1
            t/(t + 2)
            2*t/(t + 2)
            (t + 2)/t
            (2*t + 1)/t
            (t + 1)/(t + 2)
            (2*t + 2)/(t + 2)
            (t + 2)/(t + 1)
            (2*t + 1)/(t + 1)
            1/t^2
            2/t^2
            t^2
            2*t^2
        """
        cdef FpTElement next = self._copy_c()
        cdef long a, lead
        cdef zmod_poly_t g
        if zmod_poly_degree(self._numer) == -1:
            # self should be normalized, so denom == 1
            zmod_poly_set_coeff_ui(next._numer, 0, 1)
            return next
        lead = zmod_poly_leading(next._numer)
        if lead < self.p - 1:
            a = mod_inverse_int(lead, self.p)
            # no overflow since self.p < 2^16
            a = a * (lead + 1) % self.p
            zmod_poly_scalar_mul(next._numer, next._numer, a)
        else:
            a = mod_inverse_int(lead, self.p)
            zmod_poly_scalar_mul(next._numer, next._numer, a)
            # now both next._numer and next._denom are monic.  We figure out which is lexicographically bigger:
            a = zmod_poly_cmp(next._numer, next._denom)
            if a == 0:
                # next._numer and next._denom are relatively prime, so they're both 1.
                zmod_poly_inc(next._denom, True)
                return next
            zmod_poly_set(next._denom, next._numer)
            zmod_poly_set(next._numer, self._denom)
            if a < 0:
                # since next._numer is smaller, we flip and return the inverse.
                return next
            elif a > 0:
                # since next._numer is bigger, we're in the flipped phase.  We flip back, and increment the numerator (until we reach the denominator).
                zmod_poly_init(g, self.p)
                try:
                    while True:
                        zmod_poly_inc(next._numer, True)
                        if zmod_poly_equal(next._numer, next._denom):
                            # Since we've reached the denominator, we reset the numerator to 1 and increment the denominator.
                            zmod_poly_inc(next._denom, True)
                            zmod_poly_zero(next._numer)
                            zmod_poly_set_coeff_ui(next._numer, 0, 1)
                            break
                        else:
                            # otherwise, we keep incrementing until we have a relatively prime numerator.
                            zmod_poly_gcd(g, next._numer, next._denom)
                            if zmod_poly_is_one(g):
                                break
                finally:
                    zmod_poly_clear(g)
        return next

#         if zmod_poly_degree(self._numer) == -1:
#             zmod_poly_set_coeff_ui(x._numer, 0, 1)
#             zmod_poly_set_coeff_ui(x._denom, 0, 1)
#             return x
#         elif zmod_poly_degree(self._numer) == 0:
#             zmod_poly_set_coeff_ui(x._numer, 0, zmod_poly_get_coeff_ui(self._numer, 0) + 1)
#             zmod_poly_set_coeff_ui(x._denom, 0, 1)
#             if zmod_poly_get_coeff_ui(x._numer, 0) == 0:
#                 zmod_poly_set_coeff_ui(x._numer, 1, 1)
#             return x
#         cdef zmod_poly_t g
#         zmod_poly_init(g, self.p)
#         zmod_poly_set(x._numer, self._numer)
#         zmod_poly_set(x._denom, self._denom)
#         while True:
#             zmod_poly_inc(x._denom, True)
#             if zmod_poly_degree(x._numer) < zmod_poly_degree(x._denom):
#                 zmod_poly_inc(x._numer, False)
#                 zmod_poly_zero(x._denom)
#                 zmod_poly_set_coeff_ui(x._denom, 0, 1)
#             zmod_poly_gcd(g, x._numer, x._denom)
#             if zmod_poly_is_one(g):
#                 zmod_poly_clear(g)
#                 return x

    cpdef _sqrt_or_None(self):
        """
        Returns the squre root of self, or None. Differs from sqrt() by not raising an exception.

        TESTS::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(17)['t'])
            sage: sqrt(t^2) # indirect doctest
            t
            sage: sqrt(1/t^2)
            1/t
            sage: sqrt((1+t)^2)
            t + 1
            sage: sqrt((1+t)^2 / t^2)
            (t + 1)/t

            sage: sqrt(4 * (1+t)^2 / t^2)
            (2*t + 2)/t

            sage: sqrt(R(0))
            0
            sage: sqrt(R(-1))
            4

            sage: sqrt(t^4)
            t^2
            sage: sqrt(4*t^4/(1+t)^8)
            2*t^2/(t^4 + 4*t^3 + 6*t^2 + 4*t + 1)

            sage: R.<t> = FpT(GF(5)['t'])
            sage: [a for a in R.iter(2) if (a^2).sqrt() not in (a,-a)]
            []
            sage: [a for a in R.iter(2) if a.is_square() and a.sqrt()^2 != a]
            []

        """
        if zmod_poly_degree(self._numer) == -1:
            return self
        if not zmod_poly_sqrt_check(self._numer) or not zmod_poly_sqrt_check(self._denom):
            return None
        cdef zmod_poly_t numer
        cdef zmod_poly_t denom
        cdef FpTElement res
        try:
            zmod_poly_init(denom, self.p)
            zmod_poly_init(numer, self.p)
            if not zmod_poly_sqrt0(numer, self._numer):
                return None
            if not zmod_poly_sqrt0(denom, self._denom):
                return None
            res = self._new_c()
            zmod_poly_swap(numer, res._numer)
            zmod_poly_swap(denom, res._denom)
            return res
        finally:
            zmod_poly_clear(numer)
            zmod_poly_clear(denom)

    cpdef bint is_square(self):
        """
        Returns True if this element is the square of another element of the fraction field.

        EXAMPLES::

            sage: K = GF(13)['t'].fraction_field(); t = K.gen()
            sage: t.is_square()
            False
            sage: (1/t^2).is_square()
            True
            sage: K(0).is_square()
            True
        """
        return self._sqrt_or_None() is not None

    def sqrt(self, extend=True, all=False):
        """
        Returns the square root of this element.

        INPUT:

        -  ``extend`` - bool (default: True); if True, return a
           square root in an extension ring, if necessary. Otherwise, raise a
           ValueError if the square is not in the base ring.

        -  ``all`` - bool (default: False); if True, return all
           square roots of self, instead of just one.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: K = GF(7)['t'].fraction_field(); t = K.gen(0)
            sage: ((t + 2)^2/(3*t^3 + 1)^4).sqrt()
            (3*t + 6)/(t^6 + 3*t^3 + 4)
        """
        s = self._sqrt_or_None()
        if s is None:
            if extend:
                raise NotImplementedError, "function fields not yet implemented"
            else:
                raise ValueError, "not a perfect square"
        else:
            if all:
                if not s:
                    return [s]
                else:
                    return [s, -s]
            else:
                return s

    def __pow__(FpTElement self, Py_ssize_t e, dummy):
        """
        Returns the ``e``th power of this element.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: R.<t> = FpT(GF(7)['t'])
            sage: t^5
            t^5
            sage: t^-5
            1/t^5

            sage: a = (t+1)/(t-1); a
            (t + 1)/(t + 6)
            sage: a^5
            (t^5 + 5*t^4 + 3*t^3 + 3*t^2 + 5*t + 1)/(t^5 + 2*t^4 + 3*t^3 + 4*t^2 + 5*t + 6)
            sage: a^7
            (t^7 + 1)/(t^7 + 6)
            sage: a^14
            (t^14 + 2*t^7 + 1)/(t^14 + 5*t^7 + 1)

            sage: (a^2)^2 == a^4
            True
            sage: a^3 * a^2 == a^5
            True
            sage: a^47 * a^92 == a^(47+92)
            True
        """
        cdef long a
        assert dummy is None
        cdef FpTElement x = self._new_c()
        if e >= 0:
            zmod_poly_pow(x._numer, self._numer, e)
            zmod_poly_pow(x._denom, self._denom, e)
        else:
            zmod_poly_pow(x._denom, self._numer, -e)
            zmod_poly_pow(x._numer, self._denom, -e)
            if zmod_poly_leading(x._denom) != 1:
                a = mod_inverse_int(zmod_poly_leading(x._denom), self.p)
                zmod_poly_scalar_mul(x._numer, x._numer, a)
                zmod_poly_scalar_mul(x._denom, x._denom, a)
        return x


cdef class FpT_iter:
    """
    Returns a class that iterates over all elements of an FpT.

    EXAMPLES::

        sage: K = GF(3)['t'].fraction_field()
        sage: I = K.iter(1)
        sage: list(I)
        [0,
         1,
         2,
         t,
         t + 1,
         t + 2,
         2*t,
         2*t + 1,
         2*t + 2,
         1/t,
         2/t,
         (t + 1)/t,
         (t + 2)/t,
         (2*t + 1)/t,
         (2*t + 2)/t,
         1/(t + 1),
         2/(t + 1),
         t/(t + 1),
         (t + 2)/(t + 1),
         2*t/(t + 1),
         (2*t + 1)/(t + 1),
         1/(t + 2),
         2/(t + 2),
         t/(t + 2),
         (t + 1)/(t + 2),
         2*t/(t + 2),
         (2*t + 2)/(t + 2)]
    """
    def __init__(self, parent, degree=None, FpTElement start=None):
        """
        INPUTS:

        - parent -- The FpT that we're iterating over.

        - degree -- The maximum degree of the numerator and denominator of the elements over which we iterate.

        - start -- (default 0) The element on which to start.

        EXAMPLES::

            sage: K = GF(11)['t'].fraction_field()
            sage: I = K.iter(2) # indirect doctest
            sage: for a in I:
            ...       if a.denom()[0] == 3 and a.numer()[1] == 2:
            ...           print a; break
            2*t/(t + 3)
        """
        #if degree is None:
        #    raise NotImplementedError
        self.parent = parent
        self.cur = start
        self.degree = -2 if degree is None else degree

    def __cinit__(self, parent, *args, **kwds):
        """
        Memory allocation for the temp variable storing the gcd of the numerator and denominator.

        TESTS::

            sage: from sage.rings.fraction_field_FpT import FpT_iter
            sage: K = GF(7)['t'].fraction_field()
            sage: I = FpT_iter(K, 3) # indirect doctest
            sage: I
            <sage.rings.fraction_field_FpT.FpT_iter object at ...>
        """
        zmod_poly_init(self.g, parent.characteristic())

    def __dealloc__(self):
        """
        Deallocating of the self.g

        TESTS::

            sage: from sage.rings.fraction_field_FpT import FpT_iter
            sage: K = GF(7)['t'].fraction_field()
            sage: I = FpT_iter(K, 3)
            sage: del I # indirect doctest
        """
        zmod_poly_clear(self.g)

    def __iter__(self):
        """
        Returns this iterator.

        TESTS::

            sage: from sage.rings.fraction_field_FpT import FpT_iter
            sage: K = GF(3)['t'].fraction_field()
            sage: I = FpT_iter(K, 3)
            sage: for a in I: # indirect doctest
            ...       if a.numer()[1] == 1 and a.denom()[1] == 2 and a.is_square():
            ...            print a; break
            (t^2 + t + 1)/(t^2 + 2*t + 1)
        """
        return self

    def __next__(self):
        """
        Returns the next element to iterate over.

        This is achieved by iterating over monic denominators, and for each denominator,
        iterating over all numerators relatively prime to the given denominator.

        EXAMPLES::

            sage: from sage.rings.fraction_field_FpT import *
            sage: K.<t> = FpT(GF(3)['t'])
            sage: list(K.iter(1)) # indirect doctest
            [0,
             1,
             2,
             t,
             t + 1,
             t + 2,
             2*t,
             2*t + 1,
             2*t + 2,
             1/t,
             2/t,
             (t + 1)/t,
             (t + 2)/t,
             (2*t + 1)/t,
             (2*t + 2)/t,
             1/(t + 1),
             2/(t + 1),
             t/(t + 1),
             (t + 2)/(t + 1),
             2*t/(t + 1),
             (2*t + 1)/(t + 1),
             1/(t + 2),
             2/(t + 2),
             t/(t + 2),
             (t + 1)/(t + 2),
             2*t/(t + 2),
             (2*t + 2)/(t + 2)]

            sage: len(list(K.iter(3)))
            2187

            sage: K.<t> = FpT(GF(5)['t'])
            sage: L = list(K.iter(3)); len(L)
            78125
            sage: L[:10]
            [0, 1, 2, 3, 4, t, t + 1, t + 2, t + 3, t + 4]
            sage: L[2000]
            (3*t^3 + 3*t^2 + 3*t + 4)/(t + 2)
            sage: L[-1]
            (4*t^3 + 4*t^2 + 4*t + 4)/(t^3 + 4*t^2 + 4*t + 4)
        """
        cdef FpTElement next
        if self.cur is None:
            self.cur = self.parent(0)
        elif self.degree == -2:
            self.cur = self.cur.next()
        else:
            next = self.cur._copy_c()
            _sig_on
            while True:
                zmod_poly_inc(next._numer, False)
                if zmod_poly_degree(next._numer) > self.degree:
                    zmod_poly_inc(next._denom, True)
                    if zmod_poly_degree(next._denom) > self.degree:
                        raise StopIteration
                    zmod_poly_zero(next._numer)
                    zmod_poly_set_coeff_ui(next._numer, 0, 1)
                zmod_poly_gcd(self.g, next._numer, next._denom)
                if zmod_poly_is_one(self.g):
                    break
            _sig_off
            self.cur = next
#            self.cur = self.cur.next()
#            if zmod_poly_degree(self.cur._numer) > self.degree:
#                raise StopIteration
        return self.cur

cdef class Polyring_FpT_coerce(RingHomomorphism_coercion):
    cdef long p
    """
    This class represents the coercion map from GF(p)[t] to GF(p)(t)

    EXAMPLES::

        sage: R.<t> = GF(5)[]
        sage: K = R.fraction_field()
        sage: f = K.coerce_map_from(R); f
        Ring Coercion morphism:
          From: Univariate Polynomial Ring in t over Finite Field of size 5
          To:   Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 5
        sage: type(f)
        <type 'sage.rings.fraction_field_FpT.Polyring_FpT_coerce'>
    """
    def __init__(self, R):
        """
        INPUTS:

        - R -- An FpT

        EXAMPLES::

            sage: R.<t> = GF(next_prime(2000))[]
            sage: K = R.fraction_field() # indirect doctest
        """
        RingHomomorphism_coercion.__init__(self, R.ring_of_integers().Hom(R), check=False)
        self.p = R.base_ring().characteristic()

    cpdef Element _call_(self, _x):
        """
        Applies the coercion.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(R)
            sage: f(t^2 + 1) # indirect doctest
            t^2 + 1
        """
        cdef Polynomial_zmod_flint x = <Polynomial_zmod_flint?> _x
        cdef FpTElement ans = <FpTElement>PY_NEW(FpTElement)
        ans._parent = self._codomain
        ans.p = self.p
        zmod_poly_init(ans._numer, ans.p)
        zmod_poly_init(ans._denom, ans.p)
        zmod_poly_set(ans._numer, &x.x)
        zmod_poly_set_coeff_ui(ans._denom, 0, 1)
        ans.initalized = True
        return ans

    cpdef Element _call_with_args(self, _x, args=(), kwds={}):
        """
        This function allows the map to take multiple arguments, usually used to specify both numerator and denominator.

        If ``reduce`` is specified as False, then the result won't be normalized.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(R)
            sage: f(2*t + 2, t + 3) # indirect doctest
            (2*t + 2)/(t + 3)
            sage: f(2*t + 2, 2)
            t + 1
            sage: f(2*t + 2, 2, reduce=False)
            (2*t + 2)/2
        """
        cdef Polynomial_zmod_flint x = <Polynomial_zmod_flint?> _x
        cdef FpTElement ans = <FpTElement>PY_NEW(FpTElement)
        ans._parent = self._codomain
        ans.p = self.p
        zmod_poly_init(ans._numer, ans.p)
        zmod_poly_init(ans._denom, ans.p)
        cdef long r
        zmod_poly_set(ans._numer, &x.x)
        if len(args) == 0:
            zmod_poly_set_coeff_ui(ans._denom, 0, 1)
        elif len(args) == 1:
            y = args[0]
            if PY_TYPE_CHECK(y, Integer):
                r = mpz_fdiv_ui((<Integer>y).value, self.p)
                if r == 0:
                    raise ZeroDivisionError
                zmod_poly_set_coeff_ui(ans._denom, 0, r)
            else:
                # could use the coerce keyword being set to False to not check this...
                if not (PY_TYPE_CHECK(y, Element) and y.parent() is self._domain):
                    # We could special case integers and GF(p) elements here.
                    y = self._domain(y)
                zmod_poly_set(ans._denom, &((<Polynomial_zmod_flint?>y).x))
        else:
            raise ValueError, "FpT only supports two positional arguments"
        if not (kwds.has_key('reduce') and not kwds['reduce']):
            normalize(ans._numer, ans._denom, ans.p)
        ans.initalized = True
        return ans

    def section(self):
        """
        Returns the section of this inclusion: the partially defined map from ``GF(p)(t)``
        back to ``GF(p)[t]``, defined on elements with unit denominator.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(R)
            sage: g = f.section(); g
            Section map:
              From: Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 5
              To:   Univariate Polynomial Ring in t over Finite Field of size 5
            sage: t = K.gen()
            sage: g(t)
            t
            sage: g(1/t)
            Traceback (most recent call last):
            ...
            ValueError: not integral
        """
        return FpT_Polyring_section(self)

cdef class FpT_Polyring_section(Section):
    cdef long p
    """
    This class represents the section from GF(p)(t) back to GF(p)[t]

    EXAMPLES::

        sage: R.<t> = GF(5)[]
        sage: K = R.fraction_field()
        sage: f = R.convert_map_from(K); f
        Section map:
          From: Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 5
          To:   Univariate Polynomial Ring in t over Finite Field of size 5
        sage: type(f)
        <type 'sage.rings.fraction_field_FpT.FpT_Polyring_section'>
    """
    def __init__(self, Polyring_FpT_coerce f):
        """
        INPUTS:

        - f -- A Polyring_FpT_coerce homomorphism

        EXAMPLES::

            sage: R.<t> = GF(next_prime(2000))[]
            sage: K = R.fraction_field()
            sage: R(K.gen(0)) # indirect doctest
            t
        """
        self.p = f.p
        Section.__init__(self, f)

    cpdef Element _call_(self, _x):
        """
        Applies the section.

        EXAMPLES::

            sage: R.<t> = GF(7)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(R)
            sage: g = f.section(); g
            Section map:
              From: Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 7
              To:   Univariate Polynomial Ring in t over Finite Field of size 7
            sage: t = K.gen()
            sage: g(t^2) # indirect doctest
            t^2
            sage: g(1/t)
            Traceback (most recent call last):
            ...
            ValueError: not integral
        """
        cdef FpTElement x = <FpTElement?>_x
        cdef Polynomial_zmod_flint ans
        if zmod_poly_degree(x._denom) != 0:
            normalize(x._numer, x._denom, self.p)
            if zmod_poly_degree(x._denom) != 0:
                raise ValueError, "not integral"
        ans = PY_NEW(Polynomial_zmod_flint)
        if zmod_poly_get_coeff_ui(x._denom, 0) != 1:
            normalize(x._numer, x._denom, self.p)
        zmod_poly_init(&ans.x, self.p)
        zmod_poly_set(&ans.x, x._numer)
        ans._parent = self._codomain
        return ans

cdef class Fp_FpT_coerce(RingHomomorphism_coercion):
    cdef long p
    """
    This class represents the coercion map from GF(p) to GF(p)(t)

    EXAMPLES::

        sage: R.<t> = GF(5)[]
        sage: K = R.fraction_field()
        sage: f = K.coerce_map_from(GF(5)); f
        Ring Coercion morphism:
          From: Finite Field of size 5
          To:   Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 5
        sage: type(f)
        <type 'sage.rings.fraction_field_FpT.Fp_FpT_coerce'>
    """
    def __init__(self, R):
        """
        INPUTS:

        - R -- An FpT

        EXAMPLES::

            sage: R.<t> = GF(next_prime(3000))[]
            sage: K = R.fraction_field() # indirect doctest
        """
        RingHomomorphism_coercion.__init__(self, R.base_ring().Hom(R), check=False)
        self.p = R.base_ring().characteristic()

    cpdef Element _call_(self, _x):
        """
        Applies the coercion.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(GF(5))
            sage: f(GF(5)(3)) # indirect doctest
            3
        """
        cdef IntegerMod_int x = <IntegerMod_int?> _x
        cdef FpTElement ans = <FpTElement>PY_NEW(FpTElement)
        ans._parent = self._codomain
        ans.p = self.p
        zmod_poly_init(ans._numer, ans.p)
        zmod_poly_init(ans._denom, ans.p)
        zmod_poly_set_coeff_ui(ans._numer, 0, x.ivalue)
        zmod_poly_set_coeff_ui(ans._denom, 0, 1)
        ans.initalized = True
        return ans

    cpdef Element _call_with_args(self, _x, args=(), kwds={}):
        """
        This function allows the map to take multiple arguments, usually used to specify both numerator and denominator.

        If ``reduce`` is specified as False, then the result won't be normalized.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(GF(5))
            sage: f(1, t + 3) # indirect doctest
            1/(t + 3)
            sage: f(2, 2*t)
            1/t
            sage: f(2, 2*t, reduce=False)
            2/2*t
        """
        cdef IntegerMod_int x = <IntegerMod_int?> _x
        cdef FpTElement ans = <FpTElement>PY_NEW(FpTElement)
        ans._parent = self._codomain
        ans.p = self.p
        zmod_poly_init(ans._numer, ans.p)
        zmod_poly_init(ans._denom, ans.p)
        cdef long r
        zmod_poly_set_coeff_ui(ans._numer, 0, x.ivalue)
        if len(args) == 0:
            zmod_poly_set_coeff_ui(ans._denom, 0, 1)
        if len(args) == 1:
            y = args[0]
            if PY_TYPE_CHECK(y, Integer):
                r = mpz_fdiv_ui((<Integer>y).value, self.p)
                if r == 0:
                    raise ZeroDivisionError
                zmod_poly_set_coeff_ui(ans._denom, 0, r)
            else:
                R = self._codomain.ring_of_integers()
                # could use the coerce keyword being set to False to not check this...
                if not (PY_TYPE_CHECK(y, Element) and y.parent() is R):
                    # We could special case integers and GF(p) elements here.
                    y = R(y)
                zmod_poly_set(ans._denom, &((<Polynomial_zmod_flint?>y).x))
        else:
            raise ValueError, "FpT only supports two positional arguments"
        if not (kwds.has_key('reduce') and not kwds['reduce']):
            normalize(ans._numer, ans._denom, ans.p)
        ans.initalized = True
        return ans

    def section(self):
        """
        Returns the section of this inclusion: the partially defined map from ``GF(p)(t)``
        back to ``GF(p)``, defined on constant elements.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(GF(5))
            sage: g = f.section(); g
            Section map:
              From: Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 5
              To:   Finite Field of size 5
            sage: t = K.gen()
            sage: g(f(1,3,reduce=False))
            2
            sage: g(t)
            Traceback (most recent call last):
            ...
            ValueError: not constant
            sage: g(1/t)
            Traceback (most recent call last):
            ...
            ValueError: not integral
        """
        return FpT_Fp_section(self)

cdef class FpT_Fp_section(Section):
    cdef long p
    """
    This class represents the section from GF(p)(t) back to GF(p)[t]

    EXAMPLES::

        sage: R.<t> = GF(5)[]
        sage: K = R.fraction_field()
        sage: f = GF(5).convert_map_from(K); f
        Section map:
          From: Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 5
          To:   Finite Field of size 5
        sage: type(f)
        <type 'sage.rings.fraction_field_FpT.FpT_Fp_section'>
    """
    def __init__(self, Fp_FpT_coerce f):
        """
        INPUTS:

        - f -- An Fp_FpT_coerce homomorphism

        EXAMPLES::

            sage: R.<t> = GF(next_prime(2000))[]
            sage: K = R.fraction_field()
            sage: GF(next_prime(2000))(K(127)) # indirect doctest
            127
        """
        self.p = f.p
        Section.__init__(self, f)

    cpdef Element _call_(self, _x):
        """
        Applies the section.

        EXAMPLES::

            sage: R.<t> = GF(7)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(GF(7))
            sage: g = f.section(); g
            Section map:
              From: Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 7
              To:   Finite Field of size 7
            sage: t = K.gen()
            sage: g(t^2) # indirect doctest
            Traceback (most recent call last):
            ...
            ValueError: not constant
            sage: g(1/t)
            Traceback (most recent call last):
            ...
            ValueError: not integral
            sage: g(K(4))
            4
            sage: g(K(0))
            0
        """
        cdef FpTElement x = <FpTElement?>_x
        cdef IntegerMod_int ans
        if zmod_poly_degree(x._denom) != 0 or zmod_poly_degree(x._numer) > 0:
            normalize(x._numer, x._denom, self.p)
            if zmod_poly_degree(x._denom) != 0:
                raise ValueError, "not integral"
            if zmod_poly_degree(x._numer) > 0:
                raise ValueError, "not constant"
        ans = PY_NEW(IntegerMod_int)
        ans.__modulus = self._codomain._pyx_order
        if zmod_poly_get_coeff_ui(x._denom, 0) != 1:
            normalize(x._numer, x._denom, self.p)
        ans.ivalue = zmod_poly_get_coeff_ui(x._numer, 0)
        ans._parent = self._codomain
        return ans

cdef class ZZ_FpT_coerce(RingHomomorphism_coercion):
    cdef long p
    """
    This class represents the coercion map from ZZ to GF(p)(t)

    EXAMPLES::

        sage: R.<t> = GF(17)[]
        sage: K = R.fraction_field()
        sage: f = K.coerce_map_from(ZZ); f
        Ring Coercion morphism:
          From: Integer Ring
          To:   Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 17
        sage: type(f)
        <type 'sage.rings.fraction_field_FpT.ZZ_FpT_coerce'>
    """
    def __init__(self, R):
        """
        INPUTS:

        - R -- An FpT

        EXAMPLES::

            sage: R.<t> = GF(next_prime(3000))[]
            sage: K = R.fraction_field() # indirect doctest
        """
        RingHomomorphism_coercion.__init__(self, ZZ.Hom(R), check=False)
        self.p = R.base_ring().characteristic()

    cpdef Element _call_(self, _x):
        """
        Applies the coercion.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(ZZ)
            sage: f(3) # indirect doctest
            3
        """
        cdef Integer x = <Integer?> _x
        cdef FpTElement ans = <FpTElement>PY_NEW(FpTElement)
        ans._parent = self._codomain
        ans.p = self.p
        zmod_poly_init(ans._numer, ans.p)
        zmod_poly_init(ans._denom, ans.p)
        zmod_poly_set_coeff_ui(ans._numer, 0, mpz_fdiv_ui(x.value, self.p))
        zmod_poly_set_coeff_ui(ans._denom, 0, 1)
        ans.initalized = True
        return ans

    cpdef Element _call_with_args(self, _x, args=(), kwds={}):
        """
        This function allows the map to take multiple arguments, usually used to specify both numerator and denominator.

        If ``reduce`` is specified as False, then the result won't be normalized.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(ZZ)
            sage: f(1, t + 3) # indirect doctest
            1/(t + 3)
            sage: f(1,2)
            3
            sage: f(2, 2*t)
            1/t
            sage: f(2, 2*t, reduce=False)
            2/2*t
        """
        cdef Integer x = <Integer?> _x
        cdef FpTElement ans = <FpTElement>PY_NEW(FpTElement)
        ans._parent = self._codomain
        ans.p = self.p
        zmod_poly_init(ans._numer, ans.p)
        zmod_poly_init(ans._denom, ans.p)
        cdef long r
        zmod_poly_set_coeff_ui(ans._numer, 0, mpz_fdiv_ui(x.value, self.p))
        if len(args) == 0:
            zmod_poly_set_coeff_ui(ans._denom, 0, 1)
        if len(args) == 1:
            y = args[0]
            if PY_TYPE_CHECK(y, Integer):
                r = mpz_fdiv_ui((<Integer>y).value, self.p)
                if r == 0:
                    raise ZeroDivisionError
                zmod_poly_set_coeff_ui(ans._denom, 0, r)
            else:
                R = self._codomain.ring_of_integers()
                # could use the coerce keyword being set to False to not check this...
                if not (PY_TYPE_CHECK(y, Element) and y.parent() is R):
                    # We could special case integers and GF(p) elements here.
                    y = R(y)
                zmod_poly_set(ans._denom, &((<Polynomial_zmod_flint?>y).x))
        else:
            raise ValueError, "FpT only supports two positional arguments"
        if not (kwds.has_key('reduce') and not kwds['reduce']):
            normalize(ans._numer, ans._denom, ans.p)
        ans.initalized = True
        return ans

    def section(self):
        """
        Returns the section of this inclusion: the partially defined map from ``GF(p)(t)``
        back to ``ZZ``, defined on constant elements.

        EXAMPLES::

            sage: R.<t> = GF(5)[]
            sage: K = R.fraction_field()
            sage: f = K.coerce_map_from(ZZ)
            sage: g = f.section(); g
            Composite map:
              From: Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 5
              To:   Integer Ring
              Defn:   Section map:
                      From: Fraction Field of Univariate Polynomial Ring in t over Finite Field of size 5
                      To:   Finite Field of size 5
                    then
                      Conversion via _integer_ method map:
                      From: Finite Field of size 5
                      To:   Integer Ring
            sage: t = K.gen()
            sage: g(f(1,3,reduce=False))
            2
            sage: g(t)
            Traceback (most recent call last):
            ...
            ValueError: not constant
            sage: g(1/t)
            Traceback (most recent call last):
            ...
            ValueError: not integral
        """
        return ZZ.convert_map_from(self._codomain.base_ring()) * Fp_FpT_coerce(self._codomain).section()

cdef inline bint normalize(zmod_poly_t numer, zmod_poly_t denom, long p):
    """
    Puts numer/denom into a normal form: denominator monic and sharing no common factor with the numerator.

    The normalized form of 0 is 0/1.

    Returns True if numer and denom were changed.
    """
    cdef long a
    cdef bint changed
    if zmod_poly_degree(numer) == -1:
        if zmod_poly_degree(denom) > 0 or zmod_poly_leading(denom) != 1:
            changed = True
        else:
            changed = False
        zmod_poly_truncate(denom, 0)
        zmod_poly_set_coeff_ui(denom, 0, 1)
        return changed
    elif zmod_poly_degree(numer) == 0 or zmod_poly_degree(denom) == 0:
        if zmod_poly_leading(denom) != 1:
            a = mod_inverse_int(zmod_poly_leading(denom), p)
            zmod_poly_scalar_mul(numer, numer, a)
            zmod_poly_scalar_mul(denom, denom, a)
            return True
        return False
    cdef zmod_poly_t g
    changed = False
    try:
        zmod_poly_init_precomp(g, p, numer.p_inv)
        zmod_poly_gcd(g, numer, denom)
        if zmod_poly_degree(g) != 0:
            # Divide knowing divisible by? Can we get these quotients as a byproduct of the gcd?
            zmod_poly_div(numer, numer, g)
            zmod_poly_div(denom, denom, g)
            changed = True
        if zmod_poly_leading(denom) != 1:
            a = mod_inverse_int(zmod_poly_leading(denom), p)
            zmod_poly_scalar_mul(numer, numer, a)
            zmod_poly_scalar_mul(denom, denom, a)
            changed = True
        return changed
    finally:
        zmod_poly_clear(g)

cdef inline unsigned long zmod_poly_leading(zmod_poly_t poly):
    """
    Returns the leading coefficient of ``poly``.
    """
    return zmod_poly_get_coeff_ui(poly, zmod_poly_degree(poly))

cdef inline void zmod_poly_inc(zmod_poly_t poly, bint monic):
    """
    Sets poly to the "next" polynomial: this is just counting in base p.

    If monic is True then will only iterate through monic polynomials.
    """
    cdef long n
    cdef long a
    cdef long p = poly.p
    for n from 0 <= n <= zmod_poly_degree(poly) + 1:
        a = zmod_poly_get_coeff_ui(poly, n) + 1
        if a == p:
            zmod_poly_set_coeff_ui(poly, n, 0)
        else:
            zmod_poly_set_coeff_ui(poly, n, a)
            break
    if monic and a == 2 and n == zmod_poly_degree(poly):
        zmod_poly_set_coeff_ui(poly, n, 0)
        zmod_poly_set_coeff_ui(poly, n+1, 1)

cdef inline long zmod_poly_cmp(zmod_poly_t a, zmod_poly_t b):
    """
    Compares `a` and `b`, returning 0 if they are equal.

    - If the degree of `a` is less than that of `b`, returns -1.

    - If the degree of `b` is less than that of `a`, returns 1.

    - Otherwise, compares `a` and `b` lexicographically, starting at the leading terms.
    """
    cdef long ad = zmod_poly_degree(a)
    cdef long bd = zmod_poly_degree(b)
    if ad < bd:
        return -1
    elif ad > bd:
        return 1
    cdef long d = zmod_poly_degree(a)
    while d >= 0:
        ad = zmod_poly_get_coeff_ui(a, d)
        bd = zmod_poly_get_coeff_ui(b, d)
        if ad < bd:
            return -1
        elif ad > bd:
            return 1
        d -= 1
    return 0

cdef void zmod_poly_pow(zmod_poly_t res, zmod_poly_t poly, unsigned long e):
    """
    Raises poly to the `e`th power and stores the result in ``res``.
    """
    if zmod_poly_degree(poly) < 2:
        if zmod_poly_degree(poly) == -1:
            zmod_poly_zero(res)
            return
        elif zmod_poly_is_one(poly):
            zmod_poly_set(res, poly)
            return
        elif e > 1 and zmod_poly_degree(poly) == 1 and zmod_poly_get_coeff_ui(poly, 0) == 0 and zmod_poly_get_coeff_ui(poly, 1) == 1:
            zmod_poly_left_shift(res, poly, e-1)
            return

    # TODO: Could use the fact that (a+b)^p = a^p + b^p
    # Only seems to be a big gain for large p, large exponents...
    cdef zmod_poly_t pow2

    if e < 5:
        if e == 0:
            zmod_poly_zero(res)
            zmod_poly_set_coeff_ui(res, 0, 1)
        elif e == 1:
            zmod_poly_set(res, poly)
        elif e == 2:
            zmod_poly_sqr(res, poly)
        elif e == 3:
            zmod_poly_sqr(res, poly)
            zmod_poly_mul(res, res, poly)
        elif e == 4:
            zmod_poly_sqr(res, poly)
            zmod_poly_sqr(res, res)
    else:
        zmod_poly_init(pow2, poly.p)
        zmod_poly_zero(res)
        zmod_poly_set_coeff_ui(res, 0, 1)
        zmod_poly_set(pow2, poly)
        while True:
            if e & 1:
                zmod_poly_mul(res, res, pow2)
            e >>= 1
            if e == 0:
                break
            zmod_poly_sqr(pow2, pow2)
        zmod_poly_clear(pow2)


cdef long sqrt_mod_int(long a, long p) except -1:
    """
    Returns the square root of a modulo p, as a long.
    """
    return GF(p)(a).sqrt()

cdef bint zmod_poly_sqrt_check(zmod_poly_t poly):
    """
    Quick check to see if poly could possibly be a square.
    """
    return (zmod_poly_degree(poly) % 2 == 0
        and jacobi_int(zmod_poly_leading(poly), poly.p) == 1
        and jacobi_int(zmod_poly_get_coeff_ui(poly, 0), poly.p) != -1)

cdef bint zmod_poly_sqrt(zmod_poly_t res, zmod_poly_t poly):
    """
    Compute the square root of poly as res if res is a perfect square.

    Returns True on success, False on failure.
    """
    if not zmod_poly_sqrt_check(poly):
        return False
    return zmod_poly_sqrt0(res, poly)

cdef bint zmod_poly_sqrt0(zmod_poly_t res, zmod_poly_t poly):
    """
    Compute the square root of poly as res if res is a perfect square, assuming that poly passes zmod_poly_sqrt_check.

    Returns True on success, False on failure.
    """
    if zmod_poly_degree(poly) == -1:
        zmod_poly_zero(res)
        return True
    if zmod_poly_degree(poly) == 0:
        zmod_poly_zero(res)
        zmod_poly_set_coeff_ui(res, 0, sqrt_mod_int(zmod_poly_get_coeff_ui(poly, 0), poly.p))
        return True
    cdef zmod_poly_t g
    cdef long p = poly.p
    cdef long n, leading
    cdef zmod_poly_factor_t factors
    try:
        zmod_poly_init(g, p)
        zmod_poly_derivative(res, poly)
        zmod_poly_gcd(g, res, poly)
        if 2*zmod_poly_degree(g) < zmod_poly_degree(poly):
            return False

        elif 2*zmod_poly_degree(g) > zmod_poly_degree(poly):
            try:
                zmod_poly_factor_init(factors)
                leading = zmod_poly_leading(poly)
                if leading == 1:
                    zmod_poly_factor_square_free(factors, poly)
                else:
                    zmod_poly_scalar_mul(res, poly, mod_inverse_int(leading, p))
                    zmod_poly_factor_square_free(factors, res)
                for n in range(factors.num_factors):
                    if factors.exponents[n] % 2 != 0:
                        return False
                zmod_poly_pow(res, factors.factors[0], factors.exponents[0]//2)
                for n in range(1, factors.num_factors):
                    zmod_poly_pow(factors.factors[n], factors.factors[n], factors.exponents[n]//2)
                    zmod_poly_mul(res, res, factors.factors[n])
                if leading != 1:
                    zmod_poly_scalar_mul(res, res, sqrt_mod_int(zmod_poly_leading(poly), p))
                return True
            finally:
                zmod_poly_factor_clear(factors)

        else: # deg(g) == deg(poly)/2
            zmod_poly_sqr(res, g)
            leading = zmod_poly_leading(poly) * mod_inverse_int(zmod_poly_leading(res), p)
            zmod_poly_scalar_mul(res, res, leading)
            if zmod_poly_equal(res, poly):
                zmod_poly_scalar_mul(res, g, sqrt_mod_int(leading, p))
                return True
            else:
                return False
    finally:
        zmod_poly_clear(g)

def unpickle_FpT_element(K, numer, denom):
    """
    Used for pickling.

    TESTS::

        sage: from sage.rings.fraction_field_FpT import unpickle_FpT_element
        sage: R.<t> = GF(13)['t']
        sage: unpickle_FpT_element(Frac(R), t+1, t)
        (t + 1)/t
    """
    return FpTElement(K, numer, denom, coerce=False, reduce=False)
