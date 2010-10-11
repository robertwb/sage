r"""
Dense univariate polynomials over `\RR`, implemented using MPFR
"""
include "../../ext/stdsage.pxi"
include "../../ext/interrupt.pxi"

from python_int cimport PyInt_AS_LONG
from python_float cimport PyFloat_AS_DOUBLE

from sage.structure.parent cimport Parent
from polynomial_element cimport Polynomial
from sage.rings.real_mpfr cimport RealField_class, RealNumber
from sage.rings.integer cimport Integer
from sage.rings.rational cimport Rational

from sage.structure.element cimport Element, ModuleElement, RingElement
from sage.structure.element import parent, canonical_coercion, bin_op, gcd, coerce_binop
from sage.libs.mpfr cimport *

from sage.libs.all import pari_gen

cdef class PolynomialRealDense(Polynomial):

    cdef Py_ssize_t _degree
    cdef mpfr_t* _coeffs
    cdef RealField_class _base_ring

    def __cinit__(self):
        """
        TESTS::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: PolynomialRealDense(RR['x'])
            0
        """
        self._coeffs = NULL

    def __init__(self, Parent parent, x=0, check=None, bint is_gen=False, construct=None):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: PolynomialRealDense(RR['x'], [1, int(2), RR(3), 4/1, pi])
            3.14159265358979*x^4 + 4.00000000000000*x^3 + 3.00000000000000*x^2 + 2.00000000000000*x + 1.00000000000000
        """
        Polynomial.__init__(self, parent, is_gen=is_gen)
        self._base_ring = parent._base
        cdef Py_ssize_t i, degree
        cdef int prec = self._base_ring.__prec
        cdef mp_rnd_t rnd = self._base_ring.rnd
        if is_gen:
            x = [0, 1]
        elif isinstance(x, (int, float, Integer, Rational, RealNumber)):
            x = [x]
        elif isinstance(x, dict):
            degree = max(x.keys())
            coeffs = [0] * (degree+1)
            for i, a in x.items():
                coeffs[i] = a
            x = coeffs
        elif isinstance(x, pari_gen):
            x = [self._base_ring(w) for w in x.Vecrev()]
        elif not isinstance(x, list):
            try:
                x = list(x)
            except:
                x = [self._base_ring(x)]
        degree = self._degree = len(x) - 1
        self._coeffs = <mpfr_t*>sage_malloc(sizeof(mpfr_t)*(degree+1))
        for i from 0 <= i <= degree:
            mpfr_init2(self._coeffs[i], prec)
            a = x[i]
            if PY_TYPE_CHECK_EXACT(a, RealNumber):
                mpfr_set(self._coeffs[i], (<RealNumber>a).value, rnd)
            elif PY_TYPE_CHECK_EXACT(a, int):
                mpfr_set_si(self._coeffs[i], PyInt_AS_LONG(a), rnd)
            elif PY_TYPE_CHECK_EXACT(a, float):
                mpfr_set_d(self._coeffs[i], PyFloat_AS_DOUBLE(a), rnd)
            elif PY_TYPE_CHECK_EXACT(a, Integer):
                mpfr_set_z(self._coeffs[i], (<Integer>a).value, rnd)
            elif PY_TYPE_CHECK_EXACT(a, Rational):
                mpfr_set_q(self._coeffs[i], (<Rational>a).value, rnd)
            else:
                a = self._base_ring(a)
                mpfr_set(self._coeffs[i], (<RealNumber>a).value, rnd)
        self._normalize()

    def __dealloc__(self):
        cdef Py_ssize_t i
        if self._coeffs != NULL:
            for i from 0 <= i <= self._degree:
                mpfr_clear(self._coeffs[i])
            sage_free(self._coeffs)

    def __reduce__(self):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-2, 0, 1])
            sage: loads(dumps(f)) == f
            True
        """
        return make_PolynomialRealDense, (self._parent, self.list())

    cdef _normalize(self):
        """
        Remove all leading 0's.
        """
        cdef Py_ssize_t i
        if self._degree >= 0 and mpfr_zero_p(self._coeffs[self._degree]):
            i = self._degree
            while i >= 0 and mpfr_zero_p(self._coeffs[i]):
                mpfr_clear(self._coeffs[i])
                i -= 1
            if i == -1:
                sage_free(self._coeffs)
                self._coeffs = NULL
            else:
                self._coeffs = <mpfr_t*>sage_realloc(self._coeffs, sizeof(mpfr_t) * (i+1))
            self._degree = i

    def __getitem__(self, ix):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], range(5)); f
            4.00000000000000*x^4 + 3.00000000000000*x^3 + 2.00000000000000*x^2 + x
            sage: f[0]
            0.000000000000000
            sage: f[3]
            3.00000000000000
            sage: f[5]
            0.000000000000000

        Test slices::

            sage: R.<x> = RealField(10)[]
            sage: f = (x+1)^5; f
            x^5 + 5.0*x^4 + 10.*x^3 + 10.*x^2 + 5.0*x + 1.0
            sage: f[:3]
            10.*x^2 + 5.0*x + 1.0
            sage: f[3:]
            x^5 + 5.0*x^4 + 10.*x^3
            sage: f[1:4]
            10.*x^3 + 10.*x^2 + 5.0*x

        """
        if isinstance(ix, slice):
            if ix.stop is None:
                chopped = self
            else:
                chopped = self.truncate(ix.stop)
            if ix.start is None:
                return chopped
            else:
                return (chopped >> ix.start) << ix.start
        cdef RealNumber r = <RealNumber>RealNumber(self._base_ring)
        cdef Py_ssize_t i = ix
        if 0 <= i <= self._degree:
            mpfr_set(r.value, self._coeffs[i], self._base_ring.rnd)
        else:
            mpfr_set_ui(r.value, 0, self._base_ring.rnd)
        return r

    cdef PolynomialRealDense _new(self, Py_ssize_t degree):
        cdef Py_ssize_t i
        cdef int prec = self._base_ring.__prec
        cdef PolynomialRealDense f = <PolynomialRealDense>PY_NEW(PolynomialRealDense)
        f._parent = self._parent
        f._base_ring = self._base_ring
        f._degree = degree
        if degree >= 0:
            f._coeffs = <mpfr_t*>sage_malloc(sizeof(mpfr_t)*(degree+1))
            for i from 0 <= i <= degree:
                mpfr_init2(f._coeffs[i], prec)
        return f

    cpdef Py_ssize_t degree(self):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [1, 2, 3]); f
            3.00000000000000*x^2 + 2.00000000000000*x + 1.00000000000000
            sage: f.degree()
            2
        """
        return self._degree

    cpdef Polynomial truncate(self, long n):
        r"""
        Returns the polynomial of degree `< n` which is equivalent to self
        modulo `x^n`.

        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RealField(10)['x'], [1, 2, 4, 8])
            sage: f.truncate(3)
            4.0*x^2 + 2.0*x + 1.0
            sage: f.truncate(100)
            8.0*x^3 + 4.0*x^2 + 2.0*x + 1.0
            sage: f.truncate(1)
            1.0
            sage: f.truncate(0)
            0
        """
        if n <= 0:
            return self._new(-1)
        if n > self._degree:
            return self
        cdef PolynomialRealDense f = self._new(n-1)
        cdef Py_ssize_t i
        for i from 0 <= i < n:
            mpfr_set(f._coeffs[i], self._coeffs[i], self._base_ring.rnd)
        f._normalize()
        return f

    def truncate_abs(self, RealNumber bound):
        """
        Truncate all high order coefficients below bound.

        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RealField(10)['x'], [10^-k for k in range(10)])
            sage: f
            1.0e-9*x^9 + 1.0e-8*x^8 + 1.0e-7*x^7 + 1.0e-6*x^6 + 0.000010*x^5 + 0.00010*x^4 + 0.0010*x^3 + 0.010*x^2 + 0.10*x + 1.0
            sage: f.truncate_abs(0.5e-6)
            1.0e-6*x^6 + 0.000010*x^5 + 0.00010*x^4 + 0.0010*x^3 + 0.010*x^2 + 0.10*x + 1.0
            sage: f.truncate_abs(10.0)
            0
            sage: f.truncate_abs(1e-100) == f
            True
        """
        cdef Py_ssize_t i
        for i from self._degree >= i >= 0:
            if mpfr_cmpabs(self._coeffs[i], bound.value) >= 0:
                return self.truncate(i+1)
        return self._new(-1)

    cpdef shift(self, Py_ssize_t n):
        r"""
        Returns this polynomial multiplied by the power `x^n`. If `n`
        is negative, terms below `x^n` will be discarded. Does not
        change this polynomial.

        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [1, 2, 3]); f
            3.00000000000000*x^2 + 2.00000000000000*x + 1.00000000000000
            sage: f.shift(10)
            3.00000000000000*x^12 + 2.00000000000000*x^11 + x^10
            sage: f.shift(-1)
            3.00000000000000*x + 2.00000000000000
            sage: f.shift(-10)
            0

        TESTS::

            sage: f = RR['x'](0)
            sage: f.shift(3).is_zero()
            True
            sage: f.shift(-3).is_zero()
            True
        """
        cdef Py_ssize_t i
        cdef Py_ssize_t nn = 0 if n < 0 else n
        cdef PolynomialRealDense f
        if n == 0 or self._degree < 0:
            return self
        elif self._degree < -n:
            return self._new(-1)
        else:
            f = self._new(self._degree + n)
            for i from 0 <= i < n:
                mpfr_set_ui(f._coeffs[i], 0, self._base_ring.rnd)
            for i from nn <= i <= self._degree + n:
                mpfr_set(f._coeffs[i], self._coeffs[i-n], self._base_ring.rnd)
        return f

    def list(self):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [1, 0, -2]); f
            -2.00000000000000*x^2 + 1.00000000000000
            sage: f.list()
            [1.00000000000000, 0.000000000000000, -2.00000000000000]
        """
        cdef RealNumber r
        cdef Py_ssize_t i
        cdef list L = []
        for i from 0 <= i <= self._degree:
            r = <RealNumber>RealNumber(self._base_ring)
            mpfr_set(r.value, self._coeffs[i], self._base_ring.rnd)
            L.append(r)
        return L

    def __neg__(self):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-2,0,1])
            sage: -f
            -x^2 + 2.00000000000000
        """
        cdef Py_ssize_t i
        cdef mp_rnd_t rnd = self._base_ring.rnd
        cdef PolynomialRealDense f = self._new(self._degree)
        for i from 0 <= i <= f._degree:
            mpfr_neg(f._coeffs[i], self._coeffs[i], rnd)
        return f

    cpdef ModuleElement _add_(left, ModuleElement _right):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-2,0,1]); f
            x^2 - 2.00000000000000
            sage: g = PolynomialRealDense(RR['x'], range(5)); g
            4.00000000000000*x^4 + 3.00000000000000*x^3 + 2.00000000000000*x^2 + x
            sage: f+g
            4.00000000000000*x^4 + 3.00000000000000*x^3 + 3.00000000000000*x^2 + x - 2.00000000000000
            sage: g + f == f + g
            True
            sage: f + (-f)
            0
        """
        cdef Py_ssize_t i
        cdef mp_rnd_t rnd = left._base_ring.rnd
        cdef PolynomialRealDense right = _right
        cdef Py_ssize_t min = left._degree if left._degree < right._degree else right._degree
        cdef Py_ssize_t max = left._degree if left._degree > right._degree else right._degree
        cdef PolynomialRealDense f = left._new(max)
        for i from 0 <= i <= min:
            mpfr_add(f._coeffs[i], left._coeffs[i], right._coeffs[i], rnd)
        if left._degree < right._degree:
            for i from min < i <= max:
                mpfr_set(f._coeffs[i], right._coeffs[i], rnd)
        else:
            for i from min < i <= max:
                mpfr_set(f._coeffs[i], left._coeffs[i], rnd)
        f._normalize()
        return f

    cpdef ModuleElement _sub_(left, ModuleElement _right):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-3,0,1]); f
            x^2 - 3.00000000000000
            sage: g = PolynomialRealDense(RR['x'], range(4)); g
            3.00000000000000*x^3 + 2.00000000000000*x^2 + x
            sage: f-g
            -3.00000000000000*x^3 - x^2 - x - 3.00000000000000
            sage: (f-g) == -(g-f)
            True
        """
        cdef Py_ssize_t i
        cdef mp_rnd_t rnd = left._base_ring.rnd
        cdef PolynomialRealDense right = _right
        cdef Py_ssize_t min = left._degree if left._degree < right._degree else right._degree
        cdef Py_ssize_t max = left._degree if left._degree > right._degree else right._degree
        cdef PolynomialRealDense f = left._new(max)
        for i from 0 <= i <= min:
            mpfr_sub(f._coeffs[i], left._coeffs[i], right._coeffs[i], rnd)
        if left._degree < right._degree:
            for i from min < i <= max:
                mpfr_neg(f._coeffs[i], right._coeffs[i], rnd)
        else:
            for i from min < i <= max:
                mpfr_set(f._coeffs[i], left._coeffs[i], rnd)
        f._normalize()
        return f

    cpdef ModuleElement _rmul_(self, RingElement c):
        return self._lmul_(c)

    cpdef ModuleElement _lmul_(self, RingElement c):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-5,0,0,1]); f
            x^3 - 5.00000000000000
            sage: 4.0 * f
            4.00000000000000*x^3 - 20.0000000000000
            sage: f * -0.2
            -0.200000000000000*x^3 + 1.00000000000000
        """
        cdef Py_ssize_t i
        cdef RealNumber a = c
        if mpfr_zero_p(a.value):
            return self._new(-1)
        cdef mp_rnd_t rnd = self._base_ring.rnd
        cdef PolynomialRealDense f = self._new(self._degree)
        for i from 0 <= i <= self._degree:
            mpfr_mul(f._coeffs[i], self._coeffs[i], a.value, rnd)
        return f

    cpdef RingElement _mul_(left, RingElement _right):
        """
        Here we use the naive `O(n^2)` algorithm, as asymptotically faster algorithms such
        as Karatsuba can have very inaccurate results due to intermediate rounding errors.

        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [1e20, 1])
            sage: g = PolynomialRealDense(RR['x'], [1e30, 1])
            sage: f*g
            x^2 + 1.00000000010000e30*x + 1.00000000000000e50
            sage: f._mul_karatsuba(g)
            x^2 + 1.00000000000000e50
            sage: f = PolynomialRealDense(RR['x'], range(5))
            sage: g = PolynomialRealDense(RR['x'], range(3))
            sage: f*g
            8.00000000000000*x^6 + 10.0000000000000*x^5 + 7.00000000000000*x^4 + 4.00000000000000*x^3 + x^2
        """
        cdef Py_ssize_t i, j
        cdef mp_rnd_t rnd = left._base_ring.rnd
        cdef PolynomialRealDense right = _right
        cdef PolynomialRealDense f
        cdef mpfr_t tmp
        if left._degree < 0 or right._degree < 0:
            f = left._new(-1)
        else:
            f = left._new(left._degree + right._degree)
        sig_on()
        mpfr_init2(tmp, left._base_ring.__prec)
        for i from 0 <= i <= f._degree:
            # Yes, we could make this more efficient by initializing with
            # a multiple of left rather than all zeros...
            mpfr_set_ui(f._coeffs[i], 0, rnd)
        for i from 0 <= i <= left._degree:
            for j from 0 <= j <= right._degree:
                mpfr_mul(tmp, left._coeffs[i], right._coeffs[j], rnd)
                mpfr_add(f._coeffs[i+j], f._coeffs[i+j], tmp, rnd)
        mpfr_clear(tmp)
        sig_off()
        return f

    def _derivative(self, var=None):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [pi, 0, 2, 1]);
            sage: f.derivative()
            3.00000000000000*x^2 + 4.00000000000000*x
        """
        if var is not None and var != self._parent.gen():
            return self._new(-1)
        cdef mp_rnd_t rnd = self._base_ring.rnd
        cdef PolynomialRealDense f = self._new(self._degree-1)
        for i from 0 <= i < self._degree:
            mpfr_mul_ui(f._coeffs[i], self._coeffs[i+1], i+1, rnd)
        return f

    def integral(self):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [3, pi, 1])
            sage: f.integral()
            0.333333333333333*x^3 + 1.57079632679490*x^2 + 3.00000000000000*x
        """
        cdef mp_rnd_t rnd = self._base_ring.rnd
        cdef PolynomialRealDense f = self._new(self._degree+1)
        mpfr_set_ui(f._coeffs[0], 0, rnd)
        for i from 0 <= i <= self._degree:
            mpfr_div_ui(f._coeffs[i+1], self._coeffs[i], i+1, rnd)
        return f

    def reverse(self):
        """
        Returns `x^d f(1/x)` where `d` is the degree of `f`.

        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-3, pi, 0, 1])
            sage: f.reverse()
            -3.00000000000000*x^3 + 3.14159265358979*x^2 + 1.00000000000000
        """
        cdef mp_rnd_t rnd = self._base_ring.rnd
        cdef PolynomialRealDense f = self._new(self._degree)
        for i from 0 <= i <= self._degree:
            mpfr_set(f._coeffs[self._degree-i], self._coeffs[i], rnd)
        f._normalize()
        return f

    @coerce_binop
    def quo_rem(self, PolynomialRealDense other):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-2, 0, 1])
            sage: g = PolynomialRealDense(RR['x'], [5, 1])
            sage: q, r = f.quo_rem(g)
            sage: q
            x - 5.00000000000000
            sage: r
            23.0000000000000
            sage: q*g + r == f
            True
            sage: fg = f*g
            sage: fg.quo_rem(f)
            (x + 5.00000000000000, 0)
            sage: fg.quo_rem(g)
            (x^2 - 2.00000000000000, 0)

            sage: f = PolynomialRealDense(RR['x'], range(5))
            sage: g = PolynomialRealDense(RR['x'], [pi,3000,4])
            sage: q, r = f.quo_rem(g)
            sage: g*q + r == f
            True
        """
        if other._degree < 0:
            raise ZeroDivisionError, "other must be nonzero"
        cdef mp_rnd_t rnd = self._base_ring.rnd
        cdef PolynomialRealDense q, r
        cdef Py_ssize_t i, j
        cdef mpfr_t tmp
        # Make divisor monic for simplicity
        leading = other[other._degree]
        other = other * ~leading
        r = self * ~leading
        q = self._new(self._degree - other._degree)
        # This is the standard division algorithm
        sig_on()
        mpfr_init2(tmp, self._base_ring.__prec)
        for i from self._degree >= i >= other._degree:
            mpfr_set(q._coeffs[i-other._degree], r._coeffs[i], rnd)
            for j from 0 <= j < other._degree:
                mpfr_mul(tmp, r._coeffs[i], other._coeffs[j], rnd)
                mpfr_sub(r._coeffs[i-other._degree+j], r._coeffs[i-other._degree+j], tmp, rnd)
            r._degree -= 1
            mpfr_clear(r._coeffs[i])
        mpfr_clear(tmp)
        sig_off()
        r._normalize()
        return q, r * leading

    @coerce_binop
    def gcd(self, other):
        """
        Returns the gcd of self and other as a monic polynomial. Due to the
        inherit instability of division in this inexact ring, the results may
        not be entirely stable.

        EXAMPLES::

            sage: R.<x> = RR[]
            sage: (x^3).gcd(x^5+1)
            1.00000000000000
            sage: (x^3).gcd(x^5+x^2)
            x^2
            sage: f = (x+3)^2 * (x-1)
            sage: g = (x+3)^5
            sage: f.gcd(g)
            x^2 + 6.00000000000000*x + 9.00000000000000

        Unless the division is exact (i.e. no rounding occurs) the returned gcd is
        almost certain to be 1. ::

            sage: f = (x+RR.pi())^2 * (x-1)
            sage: g = (x+RR.pi())^5
            sage: f.gcd(g)
            1.00000000000000

        """
        aval = self.valuation()
        a = self >> aval
        bval = other.valuation()
        b = other >> bval
        if b.degree() > a.degree():
            a, b = b, a
        while b: # this will be exactly zero when the previous b is degree 0
            q, r = a.quo_rem(b)
            a, b = b, r
        if a.degree() == 0:
            # make sure gcd of "relatively prime" things is exactly 1
            return self._parent(1) << min(aval, bval)
        else:
            return a * ~a[a.degree()] << min(aval, bval)

    def __call__(self, xx):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-2, 0, 1])
            sage: f(10)
            98.0000000000000
            sage: f(CC.0)
            -3.00000000000000
            sage: f(2.0000000000000000000000000000000000000000000)
            2.00000000000000
            sage: f(RealField(10)(2))
            2.0
            sage: f(pi)
            pi^2 - 2.00000000000000


            sage: f = PolynomialRealDense(RR['x'], range(5))
            sage: f(1)
            10.0000000000000
            sage: f(-1)
            2.00000000000000
            sage: f(0)
            0.000000000000000
            sage: f = PolynomialRealDense(RR['x'])
            sage: f(12)
            0.000000000000000
        """
        if not PY_TYPE_CHECK(xx, RealNumber):
            if self._base_ring.has_coerce_map_from(parent(xx)):
                xx = self._base_ring(xx)
            else:
                return Polynomial.__call__(self, xx)
        cdef Py_ssize_t i
        cdef mp_rnd_t rnd = self._base_ring.rnd
        cdef RealNumber x = <RealNumber>xx
        cdef RealNumber res
        if (<RealField_class>x._parent).__prec < self._base_ring.__prec:
            res = RealNumber(x._parent)
        else:
            res = RealNumber(self._base_ring)
        # Optimize some very useful and common cases:
        if self._degree < 0:
            mpfr_set_ui(res.value, 0, rnd)
        elif mpfr_zero_p(x.value):
            mpfr_set(res.value, self._coeffs[0], rnd)
        elif mpfr_cmp_ui(x.value, 1) == 0:
            mpfr_set(res.value, self._coeffs[0], rnd)
            for i from 0 < i <= self._degree:
                mpfr_add(res.value, res.value, self._coeffs[i], rnd)
        elif mpfr_cmp_si(x.value, -1) == 0:
            mpfr_set(res.value, self._coeffs[0], rnd)
            for i from 2 <= i <= self._degree by 2:
                mpfr_add(res.value, res.value, self._coeffs[i], rnd)
            for i from 1 <= i <= self._degree by 2:
                mpfr_sub(res.value, res.value, self._coeffs[i], rnd)
        else:
            mpfr_set(res.value, self._coeffs[self._degree], rnd)
            for i from self._degree > i >= 0:
                mpfr_mul(res.value, res.value, x.value, rnd)
                mpfr_add(res.value, res.value, self._coeffs[i], rnd)
        return res

    def change_ring(self, R):
        """
        EXAMPLES::

            sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense
            sage: f = PolynomialRealDense(RR['x'], [-2, 0, 1.5])
            sage: f.change_ring(QQ)
            3/2*x^2 - 2
            sage: f.change_ring(RealField(10))
            1.5*x^2 - 2.0
            sage: f.change_ring(RealField(100))
            1.5000000000000000000000000000*x^2 - 2.0000000000000000000000000000
        """
        cdef Py_ssize_t i
        cdef mp_rnd_t rnd = self._base_ring.rnd
        cdef PolynomialRealDense f
        if isinstance(R, RealField_class):
            f = PolynomialRealDense(R[self.variable_name()])
            f = f._new(self._degree)
            for i from 0 <= i <= self._degree:
                mpfr_set(f._coeffs[i], self._coeffs[i], rnd)
            return f
        else:
            return Polynomial.change_ring(self, R)


def make_PolynomialRealDense(parent, data):
    """
    EXAMPLES::

        sage: from sage.rings.polynomial.polynomial_real_mpfr_dense import make_PolynomialRealDense
        sage: make_PolynomialRealDense(RR['x'], [1,2,3])
        3.00000000000000*x^2 + 2.00000000000000*x + 1.00000000000000
    """
    return PolynomialRealDense(parent, data)
