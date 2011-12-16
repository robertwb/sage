"""
Power Series Methods

The class ``PowerSeries_poly`` provides additional methods for univariate power series.
"""


include "../ext/stdsage.pxi"

from power_series_ring_element cimport PowerSeries
from sage.structure.element cimport Element, ModuleElement, RingElement
from infinity import infinity, is_Infinite
import arith
from sage.libs.all import PariError
from power_series_ring_element import is_PowerSeries
import rational_field

cdef class PowerSeries_poly(PowerSeries):

    def __init__(self, parent, f=0, prec=infinity, int check=1, is_gen=0):
        """
        EXAMPLES::

            sage: R, q = PowerSeriesRing(CC, 'q').objgen()
            sage: R
            Power Series Ring in q over Complex Field with 53 bits of precision
            sage: loads(q.dumps()) == q
            True

            sage: R.<t> = QQ[[]]
            sage: f = 3 - t^3 + O(t^5)
            sage: a = f^3; a
            27 - 27*t^3 + O(t^5)
            sage: b = f^-3; b
            1/27 + 1/27*t^3 + O(t^5)
            sage: a*b
            1 + O(t^5)
        """
        R = parent._poly_ring()
        if PY_TYPE_CHECK(f, Element):
            if (<Element>f)._parent is R:
                pass
            elif (<Element>f)._parent == R.base_ring():
                f = R([f])
            elif PY_TYPE_CHECK(f, PowerSeries_poly):
                prec = (<PowerSeries_poly>f)._prec
                f = R((<PowerSeries_poly>f).__f)
            else:
                if f:
                    f = R(f, check=check)
                else:
                    f = R(None)
        else:
            if f:
                f = R(f, check=check)
            else: # None is supposed to yield zero
                f = R(None)

        self.__f = f
        if check and not (prec is infinity):
            self.__f = self.__f.truncate(prec)
        PowerSeries.__init__(self, parent, prec, is_gen)

    def __hash__(self):
        """
        Return a hash of self.

        EXAMPLES::

            sage: R.<t> = ZZ[[]]
            sage: t.__hash__()
            760233507         # 32-bit
            14848694839950883 # 64-bit
            sage: hash(t)
            760233507         # 32-bit
            14848694839950883 # 64-bit
        """
        return hash(self.__f)

    def __reduce__(self):
        """
        Used for pickling.

        EXAMPLES::

            sage: A.<z> = RR[[]]
            sage: f = z - z^3 + O(z^10)
            sage: f == loads(dumps(f)) # indirect doctest
            True
        """
        # do *not* delete old versions.
        return make_powerseries_poly_v0, (self._parent, self.__f, self._prec, self.__is_gen)

    def __richcmp__(left, right, int op):
       """
       Used for comparing power series.

       EXAMPLES::

           sage: R.<t> = ZZ[[]]
           sage: f = 1 + t + t^7 - 5*t^10
           sage: g = 1 + t + t^7 - 5*t^10 + O(t^15)
           sage: f == f
           True
           sage: f < g
           False
           sage: f == g
           True
       """
       return (<Element>left)._richcmp(right, op)

    def polynomial(self):
        """
        Return the underlying polynomial of self.

        EXAMPLE::

            sage: R.<t> = GF(7)[[]]
            sage: f = 3 - t^3 + O(t^5)
            sage: f.polynomial()
            6*t^3 + 3
        """
        return self.__f

    def valuation(self):
        """
        Return the valuation of self.

        EXAMPLES::

            sage: R.<t> = QQ[[]]
            sage: (5 - t^8 + O(t^11)).valuation()
            0
            sage: (-t^8 + O(t^11)).valuation()
            8
            sage: O(t^7).valuation()
            +Infinity
            sage: R(0).valuation()
            +Infinity
        """
        return self.__f.valuation()

    def degree(self):
        """
        Return the degree of the underlying polynomial of self. That
        is, if self is of the form f(x) + O(x^n), we return the degree
        of f(x). Note that if f(x) is 0, we return -1, just as with
        polynomials.

        EXAMPLES::

            sage: R.<t> = ZZ[[]]
            sage: (5 + t^3 + O(t^4)).degree()
            3
            sage: (5 + O(t^4)).degree()
            0
            sage: O(t^4).degree()
            -1
        """
        return self.__f.degree()

    def __nonzero__(self):
        """
        Return True if self is nonzero, and False otherwise.

        EXAMPLES::

            sage: R.<t> = GF(11)[[]]
            sage: (1 + t + O(t^18)).__nonzero__()
            True
            sage: R(0).__nonzero__()
            False
            sage: O(t^18).__nonzero__()
            False
        """
        return not not self.__f

    def __call__(self, *xs):
        """
        EXAMPLES::

            sage: R.<t> = GF(7)[[]]
            sage: f = 3 - t^3 + O(t^5)
            sage: f(1)
            2
            sage: f(f)
            4 + 6*t^3 + O(t^5)

            sage: S.<w> = R[[]]
            sage: g = w + 2*w^3 + t*w^4 + O(w^5)
            sage: g(1)
            3 + t
            sage: g(1)(1)
            4
        """
        if isinstance(xs[0], tuple):
            xs = xs[0]
        x = xs[0]
        try:
            if x.parent() is self._parent:
                if not (self.prec() is infinity):
                    if x.valuation() == 0:
                        x = x.add_bigoh(self.prec())
                    else:
                        x = x.add_bigoh(self.prec()*x.valuation())
                    xs = list(xs); xs[0] = x; xs = tuple(xs) # tuples are immutable
        except AttributeError:
            pass
        return self.__f(xs)

    def _unsafe_mutate(self, i, value):
        """
        Sage assumes throughout that commutative ring elements are immutable.
        This is relevant for caching, etc.  But sometimes you need to change
        a power series and you really know what you're doing.  That's
        when this function is for you.

        ** DO NOT USE THIS ** unless you know what you're doing.

        EXAMPLES::

            sage: R.<t> = GF(7)[[]]
            sage: f = 3 + 6*t^3 + O(t^5)
            sage: f._unsafe_mutate(0, 5)
            sage: f
            5 + 6*t^3 + O(t^5)
            sage: f._unsafe_mutate(2, 1) ; f
            5 + t^2 + 6*t^3 + O(t^5)

        - Mutating can even bump up the precision::

            sage: f._unsafe_mutate(6, 1) ; f
            5 + t^2 + 6*t^3 + t^6 + O(t^7)
            sage: f._unsafe_mutate(0, 0) ; f
            t^2 + 6*t^3 + t^6 + O(t^7)
            sage: f._unsafe_mutate(1, 0) ; f
            t^2 + 6*t^3 + t^6 + O(t^7)
            sage: f._unsafe_mutate(11,0) ; f
            t^2 + 6*t^3 + t^6 + O(t^12)

            sage: g = t + O(t^7)
            sage: g._unsafe_mutate(1,0) ; g
            O(t^7)
        """
        self.__f._unsafe_mutate(i, value)
        self._prec = max(self._prec, i+1)

    def __getitem__(self, n):
        """
        Return the nth coefficient of self.

        If n is a slice object, this will return a power series of the
        same precision, whose coefficients are the same as self for
        those indices in the slice, and 0 otherwise.

        Returns 0 for negative coefficients. Raises an IndexError if
        try to access beyond known coefficients.

        EXAMPLES::

            sage: R.<t> = QQ[[]]
            sage: f = 3/2 - 17/5*t^3 + O(t^5)
            sage: f[3]
            -17/5
            sage: f[-2]
            0
            sage: f[4]
            0
            sage: f[5]
            Traceback (most recent call last):
            ...
            IndexError: coefficient not known
            sage: f[1:4]
            -17/5*t^3 + O(t^5)

            sage: R.<t> = ZZ[[]]
            sage: f = (2-t)^5; f
            32 - 80*t + 80*t^2 - 40*t^3 + 10*t^4 - t^5
            sage: f[2:4]
            80*t^2 - 40*t^3
            sage: f[5:9]
            -t^5
            sage: f[2:7:2]
            80*t^2 + 10*t^4
            sage: f[10:20]
            0
            sage: f[10:]
            0
            sage: f[:4]
            32 - 80*t + 80*t^2 - 40*t^3

            sage: f = 1 + t^3 - 4*t^4 + O(t^7) ; f
            1 + t^3 - 4*t^4 + O(t^7)
            sage: f[2:4]
            t^3 + O(t^7)
            sage: f[4:9]
            -4*t^4 + O(t^7)
            sage: f[2:7:2]
            -4*t^4 + O(t^7)
            sage: f[10:20]
            O(t^7)
            sage: f[10:]
            O(t^7)
            sage: f[:4]
            1 + t^3 + O(t^7)
        """
        if isinstance(n, slice):
            # get values from slice object
            start = n.start if n.start is not None else 0
            stop = self.prec() if n.stop is None else n.stop
            if stop is infinity: stop = self.degree()+1
            step = 1 if n.step is None else n.step

            # find corresponding polynomial
            poly = self.__f[start:stop]
            if step is not None:
                coeffs = poly.padded_list(stop)
                for i in range(start, stop):
                    if (i-start) % step:
                        coeffs[i] = 0
                poly = self.__f.parent()(coeffs)

            # return the power series
            return PowerSeries_poly(self._parent, poly,
                                    prec=self._prec, check=False)
        elif n < 0:
            return self.base_ring()(0)
        elif n > self.__f.degree():
            if self._prec > n:
                return self.base_ring()(0)
            #elif isinstance(n, slice):
                # It makes no sense that this is needed and that
                # __getslice__ isn't just called by default...
            #    return self.__getslice__(slice[0],slice[1])
            else:
                raise IndexError, "coefficient not known"
        return self.__f[n]

    def __iter__(self):
        """
        Return an iterator over the coefficients of this power series.

        EXAMPLES::

            sage: R.<t> = QQ[[]]
            sage: f = t + 17/5*t^3 + 2*t^4 + O(t^5)
            sage: for a in f: print a,
            0 1 0 17/5 2
        """
        return iter(self.__f)

    def __neg__(self):
        """
        Return the negative of this power series.

        EXAMPLES::

            sage: R.<t> = QQ[[]]
            sage: f = t + 17/5*t^3 + 2*t^4 + O(t^5)
            sage: -f
            -t - 17/5*t^3 - 2*t^4 + O(t^5)
        """
        return PowerSeries_poly(self._parent, -self.__f,
                                         self._prec, check=False)

    cpdef ModuleElement _add_(self, ModuleElement right_m):
        """
        EXAMPLES::

            sage: R.<x> = PowerSeriesRing(ZZ)
            sage: f = x^4 + O(x^5); f
            x^4 + O(x^5)
            sage: g = x^2 + O(x^3); g
            x^2 + O(x^3)
            sage: f+g
            x^2 + O(x^3)

        TESTS:

        In the past this could die with EXC_BAD_ACCESS (trac #8029)::

            sage: A.<x> = RR['x']
            sage: B.<t> = PowerSeriesRing(A)
            sage: 1. + O(t)
            1.00000000000000 + O(t)
            sage: 1. + O(t^2)
            1.00000000000000 + O(t^2)
            sage: 1. + O(t^3)
            1.00000000000000 + O(t^3)
            sage: 1. + O(t^4)
            1.00000000000000 + O(t^4)
        """
        cdef PowerSeries_poly right = <PowerSeries_poly>right_m
        return PowerSeries_poly(self._parent, self.__f + right.__f, \
                                         self.common_prec_c(right), check=True)

    cpdef ModuleElement _iadd_(self, ModuleElement right_m):
        """
        EXAMPLES::

            sage: R.<x> = PowerSeriesRing(ZZ)
            sage: f = x^4
            sage: f += x; f
            x + x^4
            sage: g = x^2 + O(x^3); g
            x^2 + O(x^3)
            sage: f += g; f
            x + x^2 + O(x^3)
            sage: f._iadd_(g)
            x + 2*x^2 + O(x^3)
        """
        cdef PowerSeries_poly right = <PowerSeries_poly>right_m
        self.__f += right.__f
        if self._prec is not infinity:
            if self._prec < right._prec:
                self.__f = self.__f._inplace_truncate(self._prec)
            else:
                self.__f = self.__f._inplace_truncate(right._prec)
                self._prec = right._prec
        elif right._prec is not infinity:
            self.__f = self.__f._inplace_truncate(right._prec)
            self._prec = right._prec
        return self

    cpdef ModuleElement _sub_(self, ModuleElement right_m):
        """
        Return the difference of two power series.

        EXAMPLES::

            sage: k.<w> = ZZ[]
            sage: R.<t> = k[[]]
            sage: w*t^2 -w*t +13 - (w*t^2 + w*t)
            13 - 2*w*t
        """
        cdef PowerSeries_poly right = <PowerSeries_poly>right_m
        return PowerSeries_poly(self._parent, self.__f - right.__f, \
                                         self.common_prec_c(right), check=True)

    cpdef RingElement _mul_(self, RingElement right_r):
        """
        Return the product of two power series.

        EXAMPLES::

            sage: k.<w> = ZZ[[]]
            sage: (1+17*w+15*w^3+O(w^5))*(19*w^10+O(w^12))
            19*w^10 + 323*w^11 + O(w^12)
        """
        prec = self._mul_prec(right_r)
        return PowerSeries_poly(self._parent,
                                self.__f * (<PowerSeries_poly>right_r).__f,
                                prec = prec,
                                check = True)  # check, since truncation may be needed

    cpdef RingElement _imul_(self, RingElement right_r):
        """
        Set self to self * right_r, and return this result.

        EXAMPLES::

            sage: k.<w> = ZZ[[]]
            sage: f = (1+17*w+15*w^3+O(w^5))
            sage: f *= (19*w^10+O(w^12))
            sage: f
            19*w^10 + 323*w^11 + O(w^12)

            sage: f = 1 + w^2 + O(w^5)
            sage: f._imul_(w^3)
            w^3 + w^5 + O(w^8)
        """
        prec = self._mul_prec(right_r)
        self.__f *= (<PowerSeries_poly>right_r).__f
        if prec is not infinity:
            self.__f = self.__f._inplace_truncate(prec)
            self._prec = prec
        return self

    cpdef ModuleElement _rmul_(self, RingElement c):
        """
        Multiply self on the right by a scalar.

        EXAMPLES::

            sage: R.<t> = GF(7)[[]]
            sage: f = t + 3*t^4 + O(t^11)
            sage: f * GF(7)(3)
            3*t + 2*t^4 + O(t^11)
        """
        return PowerSeries_poly(self._parent, self.__f * c, self._prec, check=False)

    cpdef ModuleElement _lmul_(self, RingElement c):
        """
        Multiply self on the left by a scalar.

        EXAMPLES::

            sage: R.<t> = GF(11)[[]]
            sage: f = 1 + 3*t^4 + O(t^120)
            sage: 2 * f
            2 + 6*t^4 + O(t^120)
        """
        return PowerSeries_poly(self._parent, c * self.__f, self._prec, check=False)

    cpdef ModuleElement _ilmul_(self, RingElement c):
        """
        Set self to self left-multiplied by a scalar.

        EXAMPLES::

            sage: R.<t> = GF(13)[[]]
            sage: f = 3 + 7*t^3 + O(t^4)
            sage: f._ilmul_(2)
            6 + t^3 + O(t^4)
            sage: f *= 7 ; f
            3 + 7*t^3 + O(t^4)
        """
        self.__f *= c
        return self

    def __floordiv__(self, denom):
        """
        EXAMPLES::

            sage: R.<t> = ZZ[[]] ; f = t**10-1 ; g = 1+t+t^7 ; h = f.add_bigoh(20)
            sage: f // g
            -1 + t - t^2 + t^3 - t^4 + t^5 - t^6 + 2*t^7 - 3*t^8 + 4*t^9 - 4*t^10 + 5*t^11 - 6*t^12 + 7*t^13 - 9*t^14 + 12*t^15 - 16*t^16 + 20*t^17 - 25*t^18 + 31*t^19 + O(t^20)
            sage: (f // g) * g
            -1 + t^10 + O(t^20)
            sage: g // h
            -1 - t - t^7 - t^10 - t^11 - t^17 + O(t^20)
            sage: (g // h) * h
            1 + t + t^7 + O(t^20)
            sage: h // g
            -1 + t - t^2 + t^3 - t^4 + t^5 - t^6 + 2*t^7 - 3*t^8 + 4*t^9 - 4*t^10 + 5*t^11 - 6*t^12 + 7*t^13 - 9*t^14 + 12*t^15 - 16*t^16 + 20*t^17 - 25*t^18 + 31*t^19 + O(t^20)
            sage: (h // g) * g
            -1 + t^10 + O(t^20)
        """
        try:
            return PowerSeries.__div__(self, denom)
        except (PariError, ZeroDivisionError), e: # PariError to general?
            if is_PowerSeries(denom) and denom.degree() == 0 and denom[0] in self._parent.base_ring():
                denom = denom[0]
            elif not denom in self._parent.base_ring():
                raise ZeroDivisionError, e
            return PowerSeries_poly(self._parent,
                                             self.__f // denom, self._prec)

    def __lshift__(PowerSeries_poly self, n):
        """
        Shift self to the left by n, i.e. multiply by x^n.

        EXAMPLES::

            sage: R.<t> = QQ[[]]
            sage: f = 1 + t + t^4
            sage: f << 1
            t + t^2 + t^5
        """
        if n:
            return PowerSeries_poly(self._parent, self.__f << n, self._prec + n)
        else:
            return self

    def __rshift__(PowerSeries_poly self, n):
        """
        Shift self to the right by n, i.e. multiply by x^-n and
        remove any terms of negative exponent.

        EXAMPLES::

            sage: R.<t> = GF(2)[[]]
            sage: f = t + t^4 + O(t^7)
            sage: f >> 1
            1 + t^3 + O(t^6)
            sage: f >> 10
            O(t^0)
        """
        if n:
            return PowerSeries_poly(self._parent, self.__f >> n, max(0,self._prec - n))
        else:
            return self

    def truncate(self, prec=infinity):
        """
        The polynomial obtained from power series by truncation at
        precision ``prec``.

        EXAMPLES::

            sage: R.<I> = GF(2)[[]]
            sage: f = 1/(1+I+O(I^8)); f
            1 + I + I^2 + I^3 + I^4 + I^5 + I^6 + I^7 + O(I^8)
            sage: f.truncate(5)
            I^4 + I^3 + I^2 + I + 1
        """
        if prec is infinity:
            return self.__f
        else:
            return self.__f.truncate(prec)

    cdef _inplace_truncate(self, long prec):
        """
        Truncate self to precision ``prec`` in place.

        NOTE::

            This is very unsafe, since power series are supposed to
            be immutable in Sage. Use at your own risk!
        """
        self.__f = self.__f._inplace_truncate(prec)
        self.prec = prec
        return self

    def truncate_powerseries(self, long prec):
        r"""
        Given input ``prec`` = $n$, returns the power series of degree
        $< n$ which is equivalent to self modulo $x^n$.

        EXAMPLES::

            sage: R.<I> = GF(2)[[]]
            sage: f = 1/(1+I+O(I^8)); f
            1 + I + I^2 + I^3 + I^4 + I^5 + I^6 + I^7 + O(I^8)
            sage: f.truncate_powerseries(5)
            1 + I + I^2 + I^3 + I^4 + O(I^5)
        """
        return PowerSeries_poly(self._parent, self.__f.truncate(prec),
                                min(self._prec, prec), check=False)

    def list(self):
        """
        Return the list of known coefficients for self. This is just
        the list of coefficients of the underlying polynomial, so in
        particular, need not have length equal to self.prec().

        EXAMPLES::

            sage: R.<t> = ZZ[[]]
            sage: f = 1 - 5*t^3 + t^5 + O(t^7)
            sage: f.list()
            [1, 0, 0, -5, 0, 1]
        """
        return self.__f.list()

    def dict(self):
        """
        Return a dictionary of coefficients for self. This is simply a
        dict for the underlying polynomial, so need not have keys
        corresponding to every number smaller than self.prec().

        EXAMPLES::

            sage: R.<t> = ZZ[[]]
            sage: f = 1 + t^10 + O(t^12)
            sage: f.dict()
            {0: 1, 10: 1}
        """
        return self.__f.dict()

    def _derivative(self, var=None):
        """
        Return the derivative of this power series with respect
        to the variable var.

        If var is None or is the generator of this ring, we take the derivative
        with respect to the generator.

        Otherwise, we call _derivative(var) on each coefficient of
        the series.

        SEE ALSO::

            self.derivative()

        EXAMPLES::

            sage: R.<t> = PowerSeriesRing(QQ, sparse=True)
            sage: f = 2 + 3*t^2 + t^100000 + O(t^10000000); f
            2 + 3*t^2 + t^100000 + O(t^10000000)
            sage: f._derivative()
            6*t + 100000*t^99999 + O(t^9999999)
            sage: f._derivative(t)
            6*t + 100000*t^99999 + O(t^9999999)

            sage: R.<x> = PolynomialRing(ZZ)
            sage: S.<y> = PowerSeriesRing(R, sparse=True)
            sage: f = x^3*y^4 + O(y^5)
            sage: f._derivative()
            4*x^3*y^3 + O(y^4)
            sage: f._derivative(y)
            4*x^3*y^3 + O(y^4)
            sage: f._derivative(x)
            3*x^2*y^4 + O(y^5)
        """
        if var is not None and var is not self._parent.gen():
            # call _derivative() recursively on coefficients
            return PowerSeries_poly(self._parent, self.__f._derivative(var),
                                    self.prec(), check=False)

        # compute formal derivative with respect to generator
        return PowerSeries_poly(self._parent, self.__f._derivative(),
                                self.prec()-1, check=False)

    def integral(self):
        """
        The integral of this power series with 0 constant term.

        EXAMPLES::

            sage: k.<w> = QQ[[]]
            sage: (1+17*w+15*w^3+O(w^5)).integral()
            w + 17/2*w^2 + 15/4*w^4 + O(w^6)
            sage: (w^3 + 4*w^4 + O(w^7)).integral()
            1/4*w^4 + 4/5*w^5 + O(w^8)
            sage: (3*w^2).integral()
            w^3
        """
        return PowerSeries_poly(self._parent, self.__f.integral(),
                                         self.prec()+1, check=False)

    def reversion(self, precision=None):
        """
        Return the reversion of f, i.e., the series g such that g(f(x)) =
        x.  Given an optional argument ``precision``, return the reversion
        with given precision (note that the reversion can have precision at
        most ``f.prec()``).  If ``f`` has infinite precision, and the argument
        ``precision`` is not given, then the precision of the reversion
        defaults to the default precision of ``f.parent()``.

        Note that this is only possible if the valuation of self is exactly
        1.

        ALGORITHM:

        We first attempt to pass the computation to pari; if this fails, we
        use Lagrange inversion.  Using ``sage: set_verbose(1)`` will print
        a message if passing to pari fails.

        If the base ring has positive characteristic, then we attempt to
        lift to a characteristic zero ring and perform the reversion there.
        If this fails, an error is raised.

        EXAMPLES::

            sage: R.<x> = PowerSeriesRing(QQ)
            sage: f = 2*x + 3*x^2 - x^4 + O(x^5)
            sage: g = f.reversion()
            sage: g
            1/2*x - 3/8*x^2 + 9/16*x^3 - 131/128*x^4 + O(x^5)
            sage: f(g)
            x + O(x^5)
            sage: g(f)
            x + O(x^5)

            sage: A.<t> = PowerSeriesRing(ZZ)
            sage: a = t - t^2 - 2*t^4 + t^5 + O(t^6)
            sage: b = a.reversion(); b
            t + t^2 + 2*t^3 + 7*t^4 + 25*t^5 + O(t^6)
            sage: a(b)
            t + O(t^6)
            sage: b(a)
            t + O(t^6)

            sage: B.<b,c> = PolynomialRing(ZZ)
            sage: A.<t> = PowerSeriesRing(B)
            sage: f = t + b*t^2 + c*t^3 + O(t^4)
            sage: g = f.reversion(); g
            t - b*t^2 + (2*b^2 - c)*t^3 + O(t^4)
            sage: f(g)
            t + O(t^4)
            sage: g(f)
            t + O(t^4)

            sage: A.<t> = PowerSeriesRing(ZZ)
            sage: B.<s> = A[[]]
            sage: f = (1 - 3*t + 4*t^3 + O(t^4))*s + (2 + t + t^2 + O(t^3))*s^2 + O(s^3)
            sage: set_verbose(1)
            sage: g = f.reversion(); g
            verbose 1 (<module>) passing to pari failed; trying Lagrange inversion
            (1 + 3*t + 9*t^2 + 23*t^3 + O(t^4))*s + (-2 - 19*t - 118*t^2 + O(t^3))*s^2 + O(s^3)
            sage: set_verbose(0)
            sage: f(g) == g(f) == s
            True

        If the leading coefficient is not a unit, we pass to its fraction
        field if possible::

            sage: A.<t> = PowerSeriesRing(ZZ)
            sage: a = 2*t - 4*t^2 + t^4 - t^5 + O(t^6)
            sage: a.reversion()
            1/2*t + 1/2*t^2 + t^3 + 79/32*t^4 + 437/64*t^5 + O(t^6)

            sage: B.<b> = PolynomialRing(ZZ)
            sage: A.<t> = PowerSeriesRing(B)
            sage: f = 2*b*t + b*t^2 + 3*b^2*t^3 + O(t^4)
            sage: g = f.reversion(); g
            1/(2*b)*t - 1/(8*b^2)*t^2 + ((-3*b + 1)/(16*b^3))*t^3 + O(t^4)
            sage: g.base_ring()
            Fraction Field of Univariate Polynomial Ring in b over Integer Ring
            sage: f(g)
            t + O(t^4)
            sage: g(f)
            t + O(t^4)

        We can handle some base rings of positive characteristic::

            sage: A8.<t> = PowerSeriesRing(Zmod(8))
            sage: a = t - 15*t^2 - 2*t^4 + t^5 + O(t^6)
            sage: b = a.reversion(); b
            t + 7*t^2 + 2*t^3 + 5*t^4 + t^5 + O(t^6)
            sage: a(b)
            t + O(t^6)
            sage: b(a)
            t + O(t^6)

        The optional argument ``precision`` sets the precision of the output::

            sage: R.<x> = PowerSeriesRing(QQ)
            sage: f = 2*x + 3*x^2 - 7*x^3 + x^4 + O(x^5)
            sage: g = f.reversion(precision=3); g
            1/2*x - 3/8*x^2 + O(x^3)
            sage: f(g)
            x + O(x^3)
            sage: g(f)
            x + O(x^3)

        If the input series has infinite precision, the precision of the
        output is automatically set to the default precision of the parent
        ring::

            sage: R.<x> = PowerSeriesRing(QQ, default_prec=20)
            sage: (x - x^2).reversion() # get some Catalan numbers
            x + x^2 + 2*x^3 + 5*x^4 + 14*x^5 + 42*x^6 + 132*x^7 + 429*x^8 + 1430*x^9 + 4862*x^10 + 16796*x^11 + 58786*x^12 + 208012*x^13 + 742900*x^14 + 2674440*x^15 + 9694845*x^16 + 35357670*x^17 + 129644790*x^18 + 477638700*x^19 + O(x^20)
            sage: (x - x^2).reversion(precision=3)
            x + x^2 + O(x^3)


        TESTS::

            sage: R.<x> = PowerSeriesRing(QQ)
            sage: f = 1 + 2*x + 3*x^2 - x^4 + O(x^5)
            sage: f.reversion()
            Traceback (most recent call last):
            ...
            ValueError: Series must have valuation one for reversion.



        """
        if self.valuation() != 1:
            raise ValueError("Series must have valuation one for reversion.")

        f = self

        if f.prec() is infinity and precision is None:
            precision = f.parent().default_prec()
        if precision:
            f = f.add_bigoh(precision)

        out_prec = f.prec()

        if not f[1].is_unit():
            # if leading coefficient is not a unit, attempt passing
            # to fraction field
            try:
                f = f.change_ring(f.base_ring().fraction_field())
            except TypeError:
                raise TypeError("Leading coefficient must be a unit, or base ring must have a fraction field.")

        # set output parent after possibly passing to fraction field,
        # but before possibly lifting to characteristic zero
        out_parent = f.parent()

        # first, try reversion with pari; this is faster than Lagrange inversion
        try:
            f2 = f._pari_()
            g = f2.serreverse()
            return PowerSeries_poly(f.parent(),g.Vecrev(),out_prec)
        except (TypeError,ValueError,AttributeError,PariError):
            # if pari fails, continue with Lagrange inversion
            from sage.misc.all import verbose
            verbose("passing to pari failed; trying Lagrange inversion")


        if f.parent().characteristic() > 0:
            # over a ring of positive characteristic, attempt lifting to
            # characteristic zero ring
            verbose("parent ring has positive characteristic; attempting lift to characteristic zero")
            base_lift = f.base_ring().lift().codomain()
            verbose("characteristic zero base is "+str(base_lift))
            f_lift = f.change_ring(base_lift)
            verbose("f_lift is "+str(f_lift))
            rev_lift = f_lift.reversion()
            return rev_lift.change_ring(f.base_ring())

        t = f.parent().gen()
        R = f.parent().base_ring()

        h = t/f
        k = 1
        g = 0
        for i in range(1, out_prec):
            k *= h
            g += R(k.padded_list(i)[i - 1]/i)*t**i
        g = g.add_bigoh(out_prec)
        return PowerSeries_poly(out_parent, g, out_prec, check=False)


def make_powerseries_poly_v0(parent,  f, prec, is_gen):
    """
    Return the power series specified by f, prec, and is_gen.

    This function exists for the purposes of pickling. Do not delete
    this function -- if you change the internal representation,
    instead make a new function and make sure that both kinds of
    objects correctly unpickle as the new type.

    EXAMPLES::

        sage: R.<t> = QQ[[]]
        sage: sage.rings.power_series_poly.make_powerseries_poly_v0(R, t, infinity, True)
        t
    """
    return PowerSeries_poly(parent, f, prec, 0, is_gen)
