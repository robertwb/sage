"""
Transcendental Functions
"""

#*****************************************************************************
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

import sys
from sage.libs.mpmath import utils as mpmath_utils
import  sage.libs.pari.all
from sage.libs.pari.all import pari, PariError
import sage.rings.complex_field as complex_field
import sage.rings.real_double as real_double
import sage.rings.complex_number
from sage.gsl.integration import numerical_integral
from sage.structure.parent import Parent
from sage.structure.coerce import parent
from sage.symbolic.expression import Expression
from sage.functions.log import exp

from sage.rings.all import (is_RealNumber, RealField,
                            is_ComplexNumber, ComplexField,
                            ZZ, RR, RDF, CDF, prime_range)

from sage.symbolic.function import GinacFunction, BuiltinFunction, is_inexact
from sage.symbolic.ring import SR

import sage.plot.all

CC = complex_field.ComplexField()
I = CC.gen(0)

def exponential_integral_1(x, n=0):
    r"""
    Returns the exponential integral `E_1(x)`. If the optional
    argument `n` is given, computes list of the first
    `n` values of the exponential integral
    `E_1(x m)`.

    The exponential integral `E_1(x)` is

    .. math::

                      E_1(x) = \int_{x}^{\infty} e^{-t}/t dt



    INPUT:


    -  ``x`` - a positive real number

    -  ``n`` - (default: 0) a nonnegative integer; if
       nonzero, then return a list of values E_1(x\*m) for m =
       1,2,3,...,n. This is useful, e.g., when computing derivatives of
       L-functions.


    OUTPUT:


    -  ``float`` - if n is 0 (the default) or

    -  ``list`` - list of floats if n 0


    EXAMPLES::

        sage: exponential_integral_1(2)
        0.048900510708061118
        sage: w = exponential_integral_1(2,4); w
        [0.048900510708061118, 0.0037793524098489067, 0.00036008245216265873, 3.7665622843924751e-05] # 32-bit
        [0.048900510708061118, 0.0037793524098489063, 0.00036008245216265873, 3.7665622843924534e-05] # 64-bit

    IMPLEMENTATION: We use the PARI C-library functions eint1 and
    veceint1.

    REFERENCE:

    - See page 262, Prop 5.6.12, of Cohen's book "A Course in
      Computational Algebraic Number Theory".

    REMARKS: When called with the optional argument n, the PARI
    C-library is fast for values of n up to some bound, then very very
    slow. For example, if x=5, then the computation takes less than a
    second for n=800000, and takes "forever" for n=900000.
    """
    if n <= 0:
        return float(pari(x).eint1())
    else:
        return [float(z) for z in pari(x).eint1(n)]


class Function_zeta(GinacFunction):
    def __init__(self):
        r"""
        Riemann zeta function at s with s a real or complex number.

        INPUT:

        -  ``s`` - real or complex number

        If s is a real number the computation is done using the MPFR
        library. When the input is not real, the computation is done using
        the PARI C library.

        EXAMPLES::

            sage: zeta(x)
            zeta(x)
            sage: zeta(2)
            1/6*pi^2
            sage: zeta(2.)
            1.64493406684823
            sage: RR = RealField(200)
            sage: zeta(RR(2))
            1.6449340668482264364724151666460251892189499012067984377356
            sage: zeta(I)
            zeta(I)
            sage: zeta(I).n()
            0.00330022368532410 - 0.418155449141322*I

        TESTS::

            sage: latex(zeta(x))
            \zeta(x)
            sage: a = loads(dumps(zeta(x)))
            sage: a.operator() == zeta
            True

            sage: zeta(1)
            Infinity
            sage: zeta(x).subs(x=1)
            Infinity
        """
        GinacFunction.__init__(self, "zeta")

zeta = Function_zeta()

class Function_zetaderiv(GinacFunction):
    def __init__(self):
        """
        Derivatives of the Riemann zeta function.

        EXAMPLES::

            sage: zetaderiv(1, x)
            zetaderiv(1, x)
            sage: zetaderiv(1, x).diff(x)
            zetaderiv(2, x)
            sage: var('n')
            n
            sage: zetaderiv(n,x)
            zetaderiv(n, x)

        TESTS::

            sage: latex(zetaderiv(2,x))
            \zeta^\prime\left(2, x\right)
            sage: a = loads(dumps(zetaderiv(2,x)))
            sage: a.operator() == zetaderiv
            True
        """
        GinacFunction.__init__(self, "zetaderiv", nargs=2)

zetaderiv = Function_zetaderiv()

def zeta_symmetric(s):
    r"""
    Completed function `\xi(s)` that satisfies
    `\xi(s) = \xi(1-s)` and has zeros at the same points as the
    Riemann zeta function.

    INPUT:


    -  ``s`` - real or complex number


    If s is a real number the computation is done using the MPFR
    library. When the input is not real, the computation is done using
    the PARI C library.

    More precisely,

    .. math::

                xi(s) = \gamma(s/2 + 1) * (s-1) * \pi^{-s/2} * \zeta(s).



    EXAMPLES::

        sage: zeta_symmetric(0.7)
        0.497580414651127
        sage: zeta_symmetric(1-0.7)
        0.497580414651127
        sage: RR = RealField(200)
        sage: zeta_symmetric(RR(0.7))
        0.49758041465112690357779107525638385212657443284080589766062
        sage: C.<i> = ComplexField()
        sage: zeta_symmetric(0.5 + i*14.0)
        0.000201294444235258 + 1.49077798716757e-19*I
        sage: zeta_symmetric(0.5 + i*14.1)
        0.0000489893483255687 + 4.40457132572236e-20*I
        sage: zeta_symmetric(0.5 + i*14.2)
        -0.0000868931282620101 + 7.11507675693612e-20*I

    REFERENCE:

    - I copied the definition of xi from
      http://www.math.ubc.ca/~pugh/RiemannZeta/RiemannZetaLong.html
    """
    if not (is_ComplexNumber(s) or is_RealNumber(s)):
        s = ComplexField()(s)

    R = s.parent()
    if s == 1:  # deal with poles, hopefully
        return R(0.5)

    return (s/2 + 1).gamma()   *    (s-1)   * (R.pi()**(-s/2))  *  s.zeta()


##     # Use PARI on complex nubmer
##     prec = s.prec()
##     s = pari.new_with_bits_prec(s, prec)
##     pi = pari.pi()
##     w = (s/2 + 1).gamma() * (s-1) * pi **(-s/2) * s.zeta()
##     z = w._sage_()
##     if z.prec() < prec:
##         raise RuntimeError, "Error computing zeta_symmetric(%s) -- precision loss."%s
##     return z


#def pi_approx(prec=53):
#    """
#    Return pi computed to prec bits of precision.
#    """
#   return real_field.RealField(prec).pi()


class Function_exp_integral(BuiltinFunction):
    def __init__(self):
        """
        Return the value of the complex exponential integral Ei(z) at a
        complex number z.

        EXAMPLES::

            sage: Ei(10)
            Ei(10)
            sage: Ei(I)
            Ei(I)
            sage: Ei(3+I)
            Ei(I + 3)
            sage: Ei(1.3)
            2.72139888023202

        The branch cut for this function is along the negative real axis::

            sage: Ei(-3 + 0.1*I)
            -0.0129379427181693 + 3.13993830250942*I
            sage: Ei(-3 - 0.1*I)
            -0.0129379427181693 - 3.13993830250942*I

        ALGORITHM: Uses mpmath.
        """
        BuiltinFunction.__init__(self, "Ei")

    def _eval_(self, x ):
        """
        EXAMPLES::

            sage: Ei(10)
            Ei(10)
            sage: Ei(I)
            Ei(I)
            sage: Ei(1.3)
            2.72139888023202
            sage: Ei(10r)
            Ei(10)
            sage: Ei(1.3r)
            2.72139888023202
        """
        if not isinstance(x, Expression) and is_inexact(x):
            return self._evalf_(x, parent(x))
        return None

    def _evalf_(self, x, parent=None):
        """
        EXAMPLES::

            sage: Ei(10).n()
            2492.22897624188
            sage: Ei(20).n()
            2.56156526640566e7
            sage: Ei(I).n()
            0.337403922900968 + 2.51687939716208*I
            sage: Ei(3+I).n()
            7.82313467600158 + 6.09751978399231*I
        """
        import mpmath
        if isinstance(parent, Parent) and hasattr(parent, 'prec'):
            prec = parent.prec()
        else:
            prec = 53
        return mpmath_utils.call(mpmath.ei, x, prec=prec)

    def __call__(self, x, prec=None, coerce=True, hold=False ):
        """
        Note that the ``prec`` argument is deprecated. The precision for
        the result is deduced from the precision of the input. Convert
        the input to a higher precision explicitly if a result with higher
        precision is desired.

        EXAMPLES::

            sage: t = Ei(RealField(100)(2.5)); t
            7.0737658945786007119235519625
            sage: t.prec()
            100

            sage: Ei(1.1, prec=300)
            doctest:...: DeprecationWarning: The prec keyword argument is deprecated. Explicitly set the precision of the input, for example Ei(RealField(300)(1)), or use the prec argument to .n() for exact inputs, e.g., Ei(1).n(300), instead.
            2.16737827956340306615064476647912607220394065907142504328679588538509331805598360907980986
        """
        if prec is not None:
            from sage.misc.misc import deprecation
            deprecation("The prec keyword argument is deprecated. Explicitly set the precision of the input, for example Ei(RealField(300)(1)), or use the prec argument to .n() for exact inputs, e.g., Ei(1).n(300), instead.")

            import mpmath
            return mpmath_utils.call(mpmath.ei, x, prec=prec)

        return BuiltinFunction.__call__(self, x, coerce=coerce, hold=hold)

    def _derivative_(self, x, diff_param=None):
        """
        EXAMPLES::

            sage: Ei(x).diff(x)
            e^x/x
            sage: Ei(x).diff(x).subs(x=1)
            e
            sage: Ei(x^2).diff(x)
            2*e^(x^2)/x
            sage: f = function('f')
            sage: Ei(f(x)).diff(x)
            e^f(x)*D[0](f)(x)/f(x)
        """
        return exp(x)/x

Ei = Function_exp_integral()


def Li(x, eps_rel=None, err_bound=False):
    r"""
    Return value of the function Li(x) as a real double field element.

    This is the function

    .. math::

                \int_2^{x} dt / \log(t).



    The function Li(x) is an approximation for the number of primes up
    to `x`. In fact, the famous Riemann Hypothesis is
    equivalent to the statement that for `x \geq 2.01` we have

    .. math::

                 |\pi(x) - Li(x)| \leq \sqrt{x} \log(x).


    For "small" `x`, `Li(x)` is always slightly bigger
    than `\pi(x)`. However it is a theorem that there are (very
    large, e.g., around `10^{316}`) values of `x` so
    that `\pi(x) > Li(x)`. See
    "A new bound for the smallest x with `\pi(x) > li(x)`",
    Bays and Hudson, Mathematics of Computation, 69 (2000) 1285-1296.

    ALGORITHM: Computed numerically using GSL.

    INPUT:


    -  ``x`` - a real number = 2.


    OUTPUT:


    -  ``x`` - a real double


    EXAMPLES::

        sage: Li(2)
        0.0
        sage: Li(5)
        2.58942452992
        sage: Li(1000)
        176.56449421
        sage: Li(10^5)
        9628.76383727
        sage: prime_pi(10^5)
        9592
        sage: Li(1)
        Traceback (most recent call last):
        ...
        ValueError: Li only defined for x at least 2.

    ::

        sage: for n in range(1,7):
        ...    print '%-10s%-10s%-20s'%(10^n, prime_pi(10^n), Li(10^n))
        10        4         5.12043572467
        100       25        29.080977804
        1000      168       176.56449421
        10000     1229      1245.09205212
        100000    9592      9628.76383727
        1000000   78498     78626.5039957
    """
    x = float(x)
    if x < 2:
        raise ValueError, "Li only defined for x at least 2."
    if eps_rel:
        ans = numerical_integral(_one_over_log, 2, float(x),
                             eps_rel=eps_rel)
    else:
        ans = numerical_integral(_one_over_log, 2, float(x))
    if err_bound:
        return real_double.RDF(ans[0]), ans[1]
    else:
        return real_double.RDF(ans[0])
    # Old PARI version -- much much slower
    #x = RDF(x)
    #return RDF(gp('intnum(t=2,%s,1/log(t))'%x))

import math
def _one_over_log(t):
    """
    Internal function for quick computation of log integrals.

    TESTS::

        sage: from sage.functions.transcendental import _one_over_log
        sage: _one_over_log(e)
        1.0
        sage: _one_over_log(2)
        1.4426950408889634
        sage: Li(100)
        29.080977804
    """
    return 1/math.log(t)

from sage.rings.polynomial.polynomial_real_mpfr_dense import PolynomialRealDense

class DickmanRho(BuiltinFunction):
    r"""
    Dickman's function is the continuous function satisfying the
    differential equation

    .. math::

         x \rho'(x) + \rho(x-1) = 0

    with initial conditions `\rho(x)=1` for
    `0 \le x \le 1`. It is useful in estimating the frequency
    of smooth numbers as asymptotically

    .. math::

         \Psi(a, a^{1/s}) \sim a \rho(s)

    where `\Psi(a,b)` is the number of `b`-smooth
    numbers less than `a`.

    ALGORITHM:

    Dickmans's function is analytic on the interval
    `[n,n+1]` for each integer `n`. To evaluate at
    `n+t, 0 \le t < 1`, a power series is recursively computed
    about `n+1/2` using the differential equation stated above.
    As high precision arithmetic may be needed for intermediate results
    the computed series are cached for later use.

    Simple explicit formulas are used for the intervals [0,1] and
    [1,2].

    EXAMPLES::

        sage: dickman_rho(2)
        0.306852819440055
        sage: dickman_rho(10)
        2.77017183772596e-11
        sage: dickman_rho(10.00000000000000000000000000000000000000)
        2.77017183772595898875812120063434232634e-11
        sage: plot(log(dickman_rho(x)), (x, 0, 15))

    AUTHORS:

    - Robert Bradshaw (2008-09)

    REFERENCES:

    - G. Marsaglia, A. Zaman, J. Marsaglia. "Numerical
      Solutions to some Classical Differential-Difference Equations."
      Mathematics of Computation, Vol. 53, No. 187 (1989).
    """
    def __init__(self):
        """
        Constructs an object to represent Dickman's rho function.

        TESTS::

            sage: dickman_rho(x)
            dickman_rho(x)
            sage: dickman_rho(3)
            0.0486083882911316
            sage: dickman_rho(pi)
            0.0359690758968463
        """
        self._cur_prec = 0
        BuiltinFunction.__init__(self, "dickman_rho", 1)

    def _eval_(self, x):
        """
        EXAMPLES::

            sage: [dickman_rho(n) for n in [1..10]]
            [1.00000000000000, 0.306852819440055, 0.0486083882911316, 0.00491092564776083, 0.000354724700456040, 0.0000196496963539553, 8.74566995329392e-7, 3.23206930422610e-8, 1.01624828273784e-9, 2.77017183772596e-11]
            sage: dickman_rho(0)
            1.00000000000000
        """
        if not is_RealNumber(x):
            try:
                x = RR(x)
            except (TypeError, ValueError):
                return None #PrimitiveFunction.__call__(self, SR(x))
        if x < 0:
            return x.parent()(0)
        elif x <= 1:
            return x.parent()(1)
        elif x <= 2:
            return 1 - x.log()
        n = x.floor()
        if self._cur_prec < x.parent().prec() or not self._f.has_key(n):
            self._cur_prec = rel_prec = x.parent().prec()
            # Go a bit beyond so we're not constantly re-computing.
            max = x.parent()(1.1)*x + 10
            abs_prec = (-self.approximate(max).log2() + rel_prec + 2*max.log2()).ceil()
            self._f = {}
            if sys.getrecursionlimit() < max + 10:
                sys.setrecursionlimit(int(max) + 10)
            self._compute_power_series(max.floor(), abs_prec, cache_ring=x.parent())
        return self._f[n](2*(x-n-x.parent()(0.5)))

    def power_series(self, n, abs_prec):
        """
        This function returns the power series about `n+1/2` used
        to evaluate Dickman's function. It is scaled such that the interval
        `[n,n+1]` corresponds to x in `[-1,1]`.

        INPUT:

        -  ``n`` - the lower endpoint of the interval for which
           this power series holds

        -  ``abs_prec`` - the absolute precision of the
           resulting power series

        EXAMPLES::

            sage: f = dickman_rho.power_series(2, 20); f
            -9.9376e-8*x^11 + 3.7722e-7*x^10 - 1.4684e-6*x^9 + 5.8783e-6*x^8 - 0.000024259*x^7 + 0.00010341*x^6 - 0.00045583*x^5 + 0.0020773*x^4 - 0.0097336*x^3 + 0.045224*x^2 - 0.11891*x + 0.13032
            sage: f(-1), f(0), f(1)
            (0.30685, 0.13032, 0.048608)
            sage: dickman_rho(2), dickman_rho(2.5), dickman_rho(3)
            (0.306852819440055, 0.130319561832251, 0.0486083882911316)
        """
        return self._compute_power_series(n, abs_prec, cache_ring=None)

    def _compute_power_series(self, n, abs_prec, cache_ring=None):
        """
        Compute the power series giving Dickman's function on [n, n+1], by
        recursion in n. For internal use; self.power_series() is a wrapper
        around this intended for the user.

        INPUT:

        -  ``n`` - the lower endpoint of the interval for which
           this power series holds

        -  ``abs_prec`` - the absolute precision of the
           resulting power series

        -  ``cache_ring`` - for internal use, caches the power
           series at this precision.

        EXAMPLES::

            sage: f = dickman_rho.power_series(2, 20); f
            -9.9376e-8*x^11 + 3.7722e-7*x^10 - 1.4684e-6*x^9 + 5.8783e-6*x^8 - 0.000024259*x^7 + 0.00010341*x^6 - 0.00045583*x^5 + 0.0020773*x^4 - 0.0097336*x^3 + 0.045224*x^2 - 0.11891*x + 0.13032
        """
        if n <= 1:
            if n <= -1:
                return PolynomialRealDense(RealField(abs_prec)['x'])
            if n == 0:
                return PolynomialRealDense(RealField(abs_prec)['x'], [1])
            elif n == 1:
                nterms = (RDF(abs_prec) * RDF(2).log()/RDF(3).log()).ceil()
                R = RealField(abs_prec)
                neg_three = ZZ(-3)
                coeffs = [1 - R(1.5).log()] + [neg_three**-k/k for k in range(1, nterms)]
                f = PolynomialRealDense(R['x'], coeffs)
                if cache_ring is not None:
                    self._f[n] = f.truncate_abs(f[0] >> (cache_ring.prec()+1)).change_ring(cache_ring)
                return f
        else:
            f = self._compute_power_series(n-1, abs_prec, cache_ring)
            # integrand = f / (2n+1 + x)
            # We calculate this way because the most significant term is the constant term,
            # and so we want to push the error accumulation and remainder out to the least
            # significant terms.
            integrand = f.reverse().quo_rem(PolynomialRealDense(f.parent(), [1, 2*n+1]))[0].reverse()
            integrand = integrand.truncate_abs(RR(2)**-abs_prec)
            iintegrand = integrand.integral()
            ff = PolynomialRealDense(f.parent(), [f(1) + iintegrand(-1)]) - iintegrand
            i = 0
            while abs(f[i]) < abs(f[i+1]):
                i += 1
            rel_prec = int(abs_prec + abs(RR(f[i])).log2())
            if cache_ring is not None:
                self._f[n] = ff.truncate_abs(ff[0] >> (cache_ring.prec()+1)).change_ring(cache_ring)
            return ff.change_ring(RealField(rel_prec))

    def approximate(self, x, parent=None):
        r"""
        Approximate using de Bruijn's formula

        .. math::

             \rho(x) \sim \frac{exp(-x \xi + Ei(\xi))}{\sqrt{2\pi x}\xi}

        which is asymptotically equal to Dickman's function, and is much
        faster to compute.

        REFERENCES:

        - N. De Bruijn, "The Asymptotic behavior of a function
          occurring in the theory of primes." J. Indian Math Soc. v 15.
          (1951)

        EXAMPLES::

            sage: dickman_rho.approximate(10)
            2.41739196365564e-11
            sage: dickman_rho(10)
            2.77017183772596e-11
            sage: dickman_rho.approximate(1000)
            4.32938809066403e-3464
        """
        log, exp, sqrt, pi = math.log, math.exp, math.sqrt, math.pi
        x = float(x)
        xi = log(x)
        y = (exp(xi)-1.0)/xi - x
        while abs(y) > 1e-12:
            dydxi = (exp(xi)*(xi-1.0) + 1.0)/(xi*xi)
            xi -= y/dydxi
            y = (exp(xi)-1.0)/xi - x
        return (-x*xi + RR(xi).eint()).exp() / (sqrt(2*pi*x)*xi)

dickman_rho = DickmanRho()
