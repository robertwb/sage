"""
Other functions
"""
from sage.symbolic.function import GinacFunction, BuiltinFunction
from sage.symbolic.expression import Expression
from sage.libs.pari.gen import pari
from sage.symbolic.all import SR
from sage.rings.all import Integer, Rational, RealField, CC, RR
from sage.misc.latex import latex
import math

one_half = ~SR(2)

class Function_erf(BuiltinFunction):
    def __init__(self):
        r"""
        The error function, defined as
        `\text{erf}(x) = \frac{2}{\sqrt{\pi}} \int_0^x e^{-t^2} dt`.

        Sage currently only implements the error function (via a call to
        PARI) when the input is real.

        EXAMPLES::

            sage: erf(2)
            erf(2)
            sage: erf(2).n()
            0.995322265018953
            sage: loads(dumps(erf))
            erf

        The following fails because we haven't implemented
        erf yet for complex values::

            sage: complex(erf(3*I))
            Traceback (most recent call last):
            ...
            TypeError: unable to simplify to complex approximation
        """
        BuiltinFunction.__init__(self, "erf", latex_name=r"\text{erf}")

    def _evalf_(self, x, parent=None):
        """
        EXAMPLES::

            sage: erf(2).n()
            0.995322265018953
            sage: erf(2).n(150)
            Traceback (most recent call last):
            ...
            NotImplementedError: erf not implemented for precision higher than 53
        """
        try:
            prec = parent.prec()
        except AttributeError: # not a Sage parent
            prec = 0
        if prec > 53:
            raise NotImplementedError, "erf not implemented for precision higher than 53"
        return parent(1 - pari(float(x)).erfc())

erf = Function_erf()

class Function_abs(GinacFunction):
    def __init__(self):
        """
        The absolute value function.

        EXAMPLES::

            sage: var('x y')
            (x, y)
            sage: abs(x)
            abs(x)
            sage: abs(x^2 + y^2)
            abs(x^2 + y^2)
            sage: abs(-2)
            2
            sage: sqrt(x^2)
            sqrt(x^2)
            sage: abs(sqrt(x))
            abs(sqrt(x))
            sage: complex(abs(3*I))
            (3+0j)

            sage: f = sage.functions.other.Function_abs()
            sage: latex(f)
            \mathrm{abs}
            sage: latex(abs(x))
            {\left| x \right|}
        """
        GinacFunction.__init__(self, "abs", latex_name=r"\mathrm{abs}")

abs = abs_symbolic = Function_abs()

class Function_ceil(BuiltinFunction):
    def __init__(self):
        r"""
        The ceiling function.

        The ceiling of `x` is computed in the following manner.


        #. The ``x.ceil()`` method is called and returned if it
           is there. If it is not, then Sage checks if `x` is one of
           Python's native numeric data types. If so, then it calls and
           returns ``Integer(int(math.ceil(x)))``.

        #. Sage tries to convert `x` into a
           ``RealIntervalField`` with 53 bits of precision. Next,
           the ceilings of the endpoints are computed. If they are the same,
           then that value is returned. Otherwise, the precision of the
           ``RealIntervalField`` is increased until they do match
           up or it reaches ``maximum_bits`` of precision.

        #. If none of the above work, Sage returns a
           ``Expression`` object.


        EXAMPLES::

            sage: a = ceil(2/5 + x)
            sage: a
            ceil(x + 2/5)
            sage: a(x=4)
            5
            sage: a(x=4.0)
            5
            sage: ZZ(a(x=3))
            4
            sage: a = ceil(x^3 + x + 5/2); a
            ceil(x^3 + x + 5/2)
            sage: a.simplify()
            ceil(x^3 + x + 1/2) + 2
            sage: a(x=2)
            13

        ::

            sage: ceil(log(8)/log(2))
            3

        ::

            sage: ceil(5.4)
            6
            sage: type(ceil(5.4))
            <type 'sage.rings.integer.Integer'>

        ::

            sage: ceil(factorial(50)/exp(1))
            11188719610782480504630258070757734324011354208865721592720336801
            sage: ceil(SR(10^50 + 10^(-50)))
            100000000000000000000000000000000000000000000000001
            sage: ceil(SR(10^50 - 10^(-50)))
            100000000000000000000000000000000000000000000000000

            sage: ceil(sec(e))
            -1

            sage: latex(ceil(x))
            \left \lceil x \right \rceil
        """
        BuiltinFunction.__init__(self, "ceil",
                                   conversions=dict(maxima='ceiling'))

    def _print_latex_(self, x):
        r"""
        EXAMPLES::

            sage: latex(ceil(x)) # indirect doctest
            \left \lceil x \right \rceil
        """
        return r"\left \lceil %s \right \rceil"%latex(x)

    #FIXME: this should be moved to _eval_
    def __call__(self, x, maximum_bits=20000):
        try:
            return x.ceil()
        except AttributeError:
            if isinstance(x, (int, long)):
                return Integer(x)
            elif isinstance(x, (float, complex)):
                return Integer(int(math.ceil(x)))

        x_original = x

        from sage.rings.all import RealIntervalField
        # If x can be coerced into a real interval, then we should
        # try increasing the number of bits of precision until
        # we get the ceiling at each of the endpoints is the same.
        # The precision will continue to be increased up to maximum_bits
        # of precision at which point it will raise a value error.
        bits = 53
        try:
            x_interval = RealIntervalField(bits)(x)
            upper_ceil = x_interval.upper().ceil()
            lower_ceil = x_interval.lower().ceil()

            while upper_ceil != lower_ceil and bits < maximum_bits:
                bits += 100
                x_interval = RealIntervalField(bits)(x)
                upper_ceil = x_interval.upper().ceil()
                lower_ceil = x_interval.lower().ceil()

            if bits < maximum_bits:
                return lower_ceil
            else:
                try:
                    return ceil(SR(x).full_simplify())
                except ValueError:
                    pass
                raise ValueError, "x (= %s) requires more than %s bits of precision to compute its ceiling"%(x, maximum_bits)

        except TypeError:
            # If x cannot be coerced into a RealField, then
            # it should be left as a symbolic expression.
            return BuiltinFunction.__call__(self, SR(x_original))

    def _eval_(self, x):
        """
        EXAMPLES::

            sage: ceil(x).subs(x==7.5)
            8
            sage: ceil(x)
            ceil(x)
        """
        try:
            return x.ceil()
        except AttributeError:
            if isinstance(x, (int, long)):
                return Integer(x)
            elif isinstance(x, (float, complex)):
                return Integer(int(math.ceil(x)))
        return None

ceil = Function_ceil()


class Function_floor(BuiltinFunction):
    def __init__(self):
        r"""
        The floor function.

        The floor of `x` is computed in the following manner.


        #. The ``x.floor()`` method is called and returned if
           it is there. If it is not, then Sage checks if `x` is one
           of Python's native numeric data types. If so, then it calls and
           returns ``Integer(int(math.floor(x)))``.

        #. Sage tries to convert `x` into a
           ``RealIntervalField`` with 53 bits of precision. Next,
           the floors of the endpoints are computed. If they are the same,
           then that value is returned. Otherwise, the precision of the
           ``RealIntervalField`` is increased until they do match
           up or it reaches ``maximum_bits`` of precision.

        #. If none of the above work, Sage returns a
           symbolic ``Expression`` object.


        EXAMPLES::

            sage: floor(5.4)
            5
            sage: type(floor(5.4))
            <type 'sage.rings.integer.Integer'>
            sage: var('x')
            x
            sage: a = floor(5.4 + x); a
            floor(x + 5.40000000000000)
            sage: a.simplify()
            floor(x + 0.4) + 5
            sage: a(x=2)
            7

        ::

            sage: floor(log(8)/log(2))
            3

        ::

            sage: floor(factorial(50)/exp(1))
            11188719610782480504630258070757734324011354208865721592720336800
            sage: floor(SR(10^50 + 10^(-50)))
            100000000000000000000000000000000000000000000000000
            sage: floor(SR(10^50 - 10^(-50)))
            99999999999999999999999999999999999999999999999999
            sage: floor(int(10^50))
            100000000000000000000000000000000000000000000000000
        """
        BuiltinFunction.__init__(self, "floor")

    def _print_latex_(self, x):
        r"""
        EXAMPLES::

            sage: latex(floor(x))
            \left \lfloor x \right \rfloor
        """
        return r"\left \lfloor %s \right \rfloor"%latex(x)

    #FIXME: this should be moved to _eval_
    def __call__(self, x, maximum_bits=20000):
        try:
            return x.floor()
        except AttributeError:
            if isinstance(x, (int, long)):
                return Integer(x)
            elif isinstance(x, (float, complex)):
                return Integer(int(math.floor(x)))

        x_original = x

        from sage.rings.all import RealIntervalField

        # If x can be coerced into a real interval, then we should
        # try increasing the number of bits of precision until
        # we get the floor at each of the endpoints is the same.
        # The precision will continue to be increased up to maximum_bits
        # of precision at which point it will raise a value error.
        bits = 53
        try:
            x_interval = RealIntervalField(bits)(x)
            upper_floor = x_interval.upper().floor()
            lower_floor = x_interval.lower().floor()

            while upper_floor != lower_floor and bits < maximum_bits:
                bits += 100
                x_interval = RealIntervalField(bits)(x)
                upper_floor = x_interval.upper().floor()
                lower_floor = x_interval.lower().floor()

            if bits < maximum_bits:
                return lower_floor
            else:
                try:
                    return floor(SR(x).full_simplify())
                except ValueError:
                    pass
                raise ValueError, "x (= %s) requires more than %s bits of precision to compute its floor"%(x, maximum_bits)

        except TypeError:
            # If x cannot be coerced into a RealField, then
            # it should be left as a symbolic expression.
            return BuiltinFunction.__call__(self, SR(x_original))

    def _eval_(self, x):
        """
        EXAMPLES::

            sage: floor(x).subs(x==7.5)
            7
            sage: floor(x)
            floor(x)
        """
        try:
            return x.floor()
        except AttributeError:
            if isinstance(x, (int, long)):
                return Integer(x)
            elif isinstance(x, (float, complex)):
                return Integer(int(math.floor(x)))
        return None

floor = Function_floor()

class Function_gamma(GinacFunction):
    def __init__(self):
        r"""
        The Gamma function.  This is defined by
        `\Gamma(z) = \int_0^\infty t^{z-1}e^{-t} dt`
        for complex input `z` with real part greater than zero, and by
        analytic continuation on the rest of the complex plane (except
        for negative integers, which are poles).

        It is computed by various libraries within Sage, depending on
        the input type.

        EXAMPLES::

            sage: gamma(CDF(0.5,14))
            -4.05370307804e-10 - 5.77329983455e-10*I
            sage: gamma(CDF(I))
            -0.154949828302 - 0.498015668118*I

        Recall that `\Gamma(n)` is `n-1` factorial::

            sage: gamma(11) == factorial(10)
            True
            sage: gamma(6)
            120
            sage: gamma(1/2)
            sqrt(pi)
            sage: gamma(-1)
            Infinity
            sage: gamma(I)
            gamma(I)
            sage: gamma(x/2)(x=5)
            3/4*sqrt(pi)

            sage: gamma(float(6))
            120.0
            sage: gamma(x)
            gamma(x)

        ::

            sage: gamma(pi)
            gamma(pi)
            sage: gamma(i)
            gamma(I)
            sage: gamma(i).n()
            -0.154949828301811 - 0.498015668118356*I
            sage: gamma(int(5))
            24


            sage: plot(gamma(x),(x,1,5))

        The gamma function only works with input that can be coerced to the
        Symbolic Ring::

            sage: Q.<i> = NumberField(x^2+1)
            sage: gamma(i)
            doctest:...: DeprecationWarning: Calling symbolic functions with arguments that cannot be coerced into symbolic expressions is deprecated.
            -0.154949828301811 - 0.498015668118356*I

        We make an exception for elements of AA or QQbar, which cannot be
        coerced into symbolic expressions to allow this usage::

            sage: t = QQbar(sqrt(2)) + sqrt(3); t
            3.146264369941973?
            sage: t.parent()
            Algebraic Field

        Symbolic functions convert the arguments to symbolic expressions if they
        are in QQbar or AA::

            sage: gamma(QQbar(I))
            -0.154949828301811 - 0.498015668118356*I

        TESTS:

        We verify that we can convert this function to Maxima and
        convert back to Sage::

            sage: z = var('z')
            sage: maxima(gamma(z)).sage()
            gamma(z)
            sage: latex(gamma(z))
            \Gamma\left(z\right)

        Test that Trac ticket 5556 is fixed::

            sage: gamma(3/4)
            gamma(3/4)

            sage: gamma(3/4).n(100)
            1.2254167024651776451290983034

        Check that negative integer input works::

            sage: (-1).gamma()
            Infinity
            sage: (-1.).gamma()
            NaN
            sage: CC(-1).gamma()
            Infinity
            sage: RDF(-1).gamma()
            NaN
            sage: CDF(-1).gamma()
            Infinity
        """
        GinacFunction.__init__(self, "gamma", latex_name=r'\Gamma',
                ginac_name='tgamma')

    def __call__(self, x, coerce=True, hold=False, prec=None):
        """
        Note that the ``prec`` argument is deprecated. The precision for
        the result is deduced from the precision of the input. Convert
        the input to a higher precision explicitly if a result with higher
        precision is desired.::

            sage: t = gamma(RealField(100)(2.5)); t
            1.3293403881791370204736256125
            sage: t.prec()
            100


            sage: gamma(6, prec=53)
            doctest:...: DeprecationWarning: The prec keyword argument is deprecated. Explicitly set the precision of the input, for example gamma(RealField(300)(1)), or use the prec argument to .n() for exact inputs, e.g., gamma(1).n(300), instead.
            120.000000000000

        TESTS::

            sage: gamma(pi,prec=100)
            2.2880377953400324179595889091

            sage: gamma(3/4,prec=100)
            1.2254167024651776451290983034
        """
        if prec is not None:
            from sage.misc.misc import deprecation
            deprecation("The prec keyword argument is deprecated. Explicitly set the precision of the input, for example gamma(RealField(300)(1)), or use the prec argument to .n() for exact inputs, e.g., gamma(1).n(300), instead.")

        # this is a kludge to keep
        #     sage: Q.<i> = NumberField(x^2+1)
        #     sage: gamma(i)
        # working, since number field elements cannot be coerced into SR
        # without specifying an explicit embedding into CC any more
        try:
            res = GinacFunction.__call__(self, x, coerce=coerce, hold=hold)
        except TypeError, err:
            # the __call__() method returns a TypeError for fast float arguments
            # as well, we only proceed if the error message says that
            # the arguments cannot be coerced to SR
            if not str(err).startswith("cannot coerce"):
                raise

            from sage.misc.misc import deprecation
            deprecation("Calling symbolic functions with arguments that cannot be coerced into symbolic expressions is deprecated.")
            parent = RR if prec is None else RealField(prec)
            try:
                x = parent(x)
            except (ValueError, TypeError):
                x = parent.complex_field()(x)
            res = GinacFunction.__call__(self, x, coerce=coerce, hold=hold)

        if prec is not None:
            return res.n(prec)

        return res

gamma = Function_gamma()

class Function_factorial(GinacFunction):
    def __init__(self):
        r"""
        Returns the factorial of `n`.

        INPUT:


        -  ``n`` - an integer, or symbolic expression

        -  ``algorithm`` - string (default: 'gmp')

        -  ``'gmp'`` - use the GMP C-library factorial
           function

        -  ``'pari'`` - use PARI's factorial function This
           option has no effect if n is a symbolic expression.


        OUTPUT: an integer or symbolic expression

        EXAMPLES::

            sage: x = var('x')
            sage: factorial(0)
            1
            sage: factorial(4)
            24
            sage: factorial(10)
            3628800
            sage: factorial(6) == 6*5*4*3*2
            True
            sage: f = factorial(x + factorial(x)); f
            factorial(x + factorial(x))
            sage: f(x=3)
            362880
            sage: factorial(x)^2
            factorial(x)^2

        ::

            sage: factorial(-32)
            Traceback (most recent call last):
            ...
            ValueError: factorial -- must be nonnegative

        TESTS:

        We verify that we can convert this function to Maxima and
        bring it back into Sage.::

            sage: z = var('z')
            sage: factorial._maxima_init_()
            'factorial'
            sage: maxima(factorial(z))
            z!
            sage: _.sage()
            factorial(z)
            sage: k = var('k')
            sage: factorial(k)
            factorial(k)

            sage: factorial(3.14)
            7.173269190187...

        Test latex typesetting::

            sage: latex(factorial(x))
            x!
            sage: latex(factorial(2*x))
            \left(2 \, x\right)!
            sage: latex(factorial(sin(x)))
            \sin\left(x\right)!
            sage: latex(factorial(sqrt(x+1)))
            \left(\sqrt{x + 1}\right)!
            sage: latex(factorial(sqrt(x)))
            \sqrt{x}!
            sage: latex(factorial(x^(2/3)))
            \left(x^{\frac{2}{3}}\right)!

            sage: latex(factorial)
            {\rm factorial}
        """
        GinacFunction.__init__(self, "factorial", latex_name='{\\rm factorial}',
                conversions=dict(maxima='factorial', mathematica='Factorial'))

factorial = Function_factorial()

class Function_binomial(GinacFunction):
    def __init__(self):
        r"""
        Return the binomial coefficient

        .. math::

                    \binom{x}{m} = x (x-1) \cdots (x-m+1) / m!


        which is defined for `m \in \ZZ` and any
        `x`. We extend this definition to include cases when
        `x-m` is an integer but `m` is not by

        .. math::

            \binom{x}{m}= \binom{x}{x-m}

        If `m < 0`, return `0`.

        INPUT:

        -  ``x``, ``m`` - numbers or symbolic expressions. Either ``m``
           or ``x-m`` must be an integer, else the output is symbolic.

        OUTPUT: number or symbolic expression (if input is symbolic)

        EXAMPLES::

            sage: binomial(5,2)
            10
            sage: binomial(2,0)
            1
            sage: binomial(1/2, 0)
            1
            sage: binomial(3,-1)
            0
            sage: binomial(20,10)
            184756
            sage: binomial(-2, 5)
            -6
            sage: binomial(RealField()('2.5'), 2)
            1.87500000000000
            sage: n=var('n'); binomial(n,2)
            1/2*(n - 1)*n
            sage: n=var('n'); binomial(n,n)
            1
            sage: n=var('n'); binomial(n,n-1)
            n
            sage: binomial(2^100, 2^100)
            1

        ::
            sage: k, i = var('k,i')
            sage: binomial(k,i)
            binomial(k, i)

        TESTS: We verify that we can convert this function to Maxima and
        bring it back into Sage.

        ::

            sage: n,k = var('n,k')
            sage: maxima(binomial(n,k))
            binomial(n,k)
            sage: _.sage()
            binomial(n, k)
            sage: sage.functions.other.binomial._maxima_init_() # temporary workaround until we can get symbolic binomial to import in global namespace, if that's desired
            'binomial'
        """
        GinacFunction.__init__(self, "binomial", nargs=2,
                conversions=dict(maxima='binomial', mathematica='Binomial'))

binomial = Function_binomial()

def _do_sqrt(x, prec=None, extend=True, all=False):
        """
        Used internally to compute the square root of x.

        INPUT:

        -  ``x`` - a number

        -  ``prec`` - None (default) or a positive integer
           (bits of precision) If not None, then compute the square root
           numerically to prec bits of precision.

        -  ``extend`` - bool (default: True); this is a place
           holder, and is always ignored since in the symbolic ring everything
           has a square root.

        -  ``extend`` - bool (default: True); whether to extend
           the base ring to find roots. The extend parameter is ignored if
           prec is a positive integer.

        -  ``all`` - bool (default: False); whether to return
           a list of all the square roots of x.


        EXAMPLES::

            sage: from sage.functions.other import _do_sqrt
            sage: _do_sqrt(3)
            sqrt(3)
            sage: _do_sqrt(3,prec=10)
            1.7
            sage: _do_sqrt(3,prec=100)
            1.7320508075688772935274463415
            sage: _do_sqrt(3,all=True)
            [sqrt(3), -sqrt(3)]

        Note that the extend parameter is ignored in the symbolic ring::

            sage: _do_sqrt(3,extend=False)
            sqrt(3)
        """
        from sage.rings.all import RealField, ComplexField
        if prec:
            if x >= 0:
                 return RealField(prec)(x).sqrt(all=all)
            else:
                 return ComplexField(prec)(x).sqrt(all=all)
        if x == -1:
            from sage.symbolic.pynac import I
            z = I
        else:
            z = SR(x) ** one_half

        if all:
            if z:
                return [z, -z]
            else:
                return [z]
        return z

def sqrt(x, *args, **kwds):
        """
        INPUT:

        -  ``x`` - a number

        -  ``prec`` - integer (default: None): if None, returns
           an exact square root; otherwise returns a numerical square root if
           necessary, to the given bits of precision.

        -  ``extend`` - bool (default: True); this is a place
           holder, and is always ignored or passed to the sqrt function for x,
           since in the symbolic ring everything has a square root.

        -  ``all`` - bool (default: False); if True, return all
           square roots of self, instead of just one.

        EXAMPLES:

        This illustrates that the bug reported in #6171 has been fixed::

            sage: a = 1.1
            sage: a.sqrt(prec=100)  # this is supposed to fail
            Traceback (most recent call last):
            ...
            TypeError: sqrt() got an unexpected keyword argument 'prec'
            sage: sqrt(a, prec=100)
            1.0488088481701515469914535137
            sage: sqrt(4.00, prec=250)
            2.0000000000000000000000000000000000000000000000000000000000000000000000000
            sage: sqrt(-1)
            I
            sage: sqrt(2)
            sqrt(2)
            sage: sqrt(2)^2
            2
            sage: sqrt(4)
            2
            sage: sqrt(4,all=True)
            [2, -2]
            sage: sqrt(x^2)
            sqrt(x^2)
            sage: sqrt(2).n()
            1.41421356237310
        """
        if isinstance(x, float):
            return math.sqrt(x)
        try:
            return x.sqrt(*args, **kwds)
        # The following includes TypeError to catch cases where sqrt
        # is called with a "prec" keyword, for example, but the sqrt
        # method for x doesn't accept such a keyword.
        except (AttributeError, TypeError):
            pass
        return _do_sqrt(x, *args, **kwds)

# register sqrt in pynac symbol_table for conversion back from maxima
from sage.symbolic.pynac import register_symbol#, symbol_table
register_symbol(sqrt, dict(maxima='sqrt', mathematica='Sqrt', maple='sqrt'))

Function_sqrt = type('deprecated_sqrt', (),
        {'__call__': staticmethod(sqrt),
            '__setstate__': lambda x, y: None})

############################
# Real and Imaginary Parts #
############################
class Function_real_part(GinacFunction):
    def __init__(self):
        """
        EXAMPLES::

            sage: z = 1+2*I
            sage: real(z)
            1
            sage: real(5/3)
            5/3
            sage: a = 2.5
            sage: real(a)
            2.50000000000000
            sage: type(real(a))
            <type 'sage.rings.real_mpfr.RealLiteral'>
            sage: real(1.0r)
            1.0

        TESTS::

            sage: loads(dumps(real_part))
            real_part

        Check if #6401 is fixed::

            sage: latex(x.real())
            \Re \left( x \right)

            sage: f(x) = function('f',x)
            sage: latex( f(x).real())
            \Re \left( f\left(x\right) \right)
        """
        GinacFunction.__init__(self, "real_part",
                                   conversions=dict(maxima='realpart'))

real = real_part = Function_real_part()

class Function_imag_part(GinacFunction):
    def __init__(self):
        """
        TESTS::

            sage: z = 1+2*I
            sage: imaginary(z)
            2
            sage: imag(z)
            2
            sage: loads(dumps(imag_part))
            imag_part

        Check if #6401 is fixed::

            sage: latex(x.imag())
            \Im \left( x \right)

            sage: f(x) = function('f',x)
            sage: latex( f(x).imag())
            \Im \left( f\left(x\right) \right)
        """
        GinacFunction.__init__(self, "imag_part",
                                   conversions=dict(maxima='imagpart'))

imag = imag_part = imaginary = Function_imag_part()


############################
# Complex Conjugate        #
############################
class Function_conjugate(GinacFunction):
    def __init__(self):
        r"""
        TESTS::

            sage: x,y = var('x,y')
            sage: x.conjugate()
            conjugate(x)
            sage: latex(conjugate(x))
            \overline{x}
            sage: f = function('f')
            sage: latex(f(x).conjugate())
            \overline{f\left(x\right)}
            sage: f = function('psi',x,y)
            sage: latex(f.conjugate())
            \overline{\psi\left(x, y\right)}
            sage: x.conjugate().conjugate()
            x
            sage: x.conjugate().operator()
            conjugate
            sage: x.conjugate().operator() == conjugate
            True

        """
        GinacFunction.__init__(self, "conjugate")

conjugate = Function_conjugate()
