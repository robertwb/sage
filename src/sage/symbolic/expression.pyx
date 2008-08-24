"""
EXAMPLES:
We mix Singular variables with symbolic variables:
    sage: R.<u,v> = QQ[]
    sage: var('a,b,c', ns=1)
    (a, b, c)
    sage: expand((u + v + a + b + c)^2)
    2*a*c + 2*a*b + 2*b*c + a^2 + b^2 + c^2 + (2*u + 2*v)*a + (2*u + 2*v)*b + (2*u + 2*v)*c + u^2 + 2*u*v + v^2
"""

include "../ext/stdsage.pxi"
include "../ext/cdefs.pxi"

import ring

from sage.structure.element cimport ModuleElement, RingElement, Element


from sage.rings.rational import Rational  # Used for sqrt.

cdef class Expression(CommutativeRingElement):
    def __dealloc__(self):
        """
        Delete memory occupied by this expression.
        """
        GEx_destruct(&self._gobj)

    def _repr_(self):
        """
        Return string representation of this symbolic expression.

        EXAMPLES:
            sage: var("x y", ns=1)
            (x, y)
            sage: (x+y)._repr_()
            'x + y'
        """
        return GEx_to_str(&self._gobj)

    def __float__(self):
        """
        Return float conversion of self, assuming self is constant.
        Otherwise, raise a TypeError.

        OUTPUT:
            float -- double precision evaluation of self

        EXAMPLES:
            sage: x = var('x', ns=1); SR = x.parent()
            sage: float(SR(12))
            12.0
            sage: float(SR(2/3))
            0.66666666666666663
            sage: float(sqrt(SR(2)))
            1.4142135623730951
            sage: float(x^2 + 1)
            Traceback (most recent call last):
            ...
            TypeError: float() argument must be a string or a number
            sage: float(SR(RIF(2)))
            Traceback (most recent call last):
            ...
            TypeError: float() argument must be a string or a number
        """
        cdef bint success
        cdef double ans = GEx_to_double(self._gobj, &success)
        if not success:
            raise TypeError, "float() argument must be a string or a number"
        return ans

    def __hash__(self):
        """
        Return hash of this expression.

        EXAMPLES:
            sage: x, y = var("x y", ns=1); S = x.parent()
            sage: hash(x)
            2013265920

        The hash of an object in Python or its coerced version into
        the symbolic ring is the same.
            sage: hash(S(19/23))
            4
            sage: hash(19/23)
            4
            sage: hash(x+y)
            -233442942
            sage: d = {x+y: 5}
            sage: d
            {x + y: 5}
        """
        return self._gobj.gethash()

    def __richcmp__(left, right, int op):
        """
        Create a formal symbolic inequality or equality.

        EXAMPLES:
            sage: var('x, y', ns=1)
            (x, y)
            sage: x + 2/3 < y^2
            x + 2/3 < y^2
            sage: x^3 -y <= y + x
            x^3 - y <= x + y
            sage: x^3 -y == y + x
            x^3 - y == x + y
            sage: x^3 - y^10 >= y + x^10
            x^3 - y^10 >= x^10 + y
            sage: x^2 > x
            x^2 > x
        """
        cdef Expression l = left
        cdef Expression r = right
        cdef GEx e
        if op == Py_LT:
            e = g_lt(l._gobj, r._gobj)
        elif op == Py_EQ:
            e = g_eq(l._gobj, r._gobj)
        elif op == Py_GT:
            e = g_gt(l._gobj, r._gobj)
        elif op == Py_LE:
            e = g_le(l._gobj, r._gobj)
        elif op == Py_NE:
            e = g_ne(l._gobj, r._gobj)
        elif op == Py_GE:
            e = g_ge(l._gobj, r._gobj)
        return new_Expression_from_GEx(e)

    def __nonzero__(self):
        """
        Return True if self is nonzero.

        EXAMPLES:
            sage: sage.symbolic.ring.NSR(0).__nonzero__()
            False
            sage: sage.symbolic.ring.NSR(1).__nonzero__()
            True
        """
        # TODO: Problem -- if self is a symbolic equality then
        # this is_zero isn't the right thing at all:
        #  sage: bool(x == x+1)
        #  True  # BAD
        # Solution is to probably look something up in ginac manual.
        return not self._gobj.is_zero()

    cdef Expression coerce_in(self, z):
        """
        Quickly coerce z to be an Expression.
        """
        cdef Expression w
        try:
            w = z
            return w
        except TypeError:
            return self._parent._coerce_c(z)

    cdef ModuleElement _add_c_impl(left, ModuleElement right):
        """
        Add left and right.

        EXAMPLES;
            sage.: var("x y", ns=1)
            (x, y)
            sage.: x + y + y + x
            2*x+2*y
        """
        return new_Expression_from_GEx(gadd(left._gobj, (<Expression>right)._gobj))

    cdef ModuleElement _sub_c_impl(left, ModuleElement right):
        """
            sage.: var("x y", ns=1)
            (x, y)
            sage.: x - x
            x-y
        """
        return new_Expression_from_GEx(gsub(left._gobj, (<Expression>right)._gobj))

    cdef RingElement _mul_c_impl(left, RingElement right):
        """
        Multiply left and right.

        EXAMPLES:
            sage: var("x y", ns=1)
            (x, y)
            sage: x*y*y
            x*y^2
        """
        return new_Expression_from_GEx(gmul(left._gobj, (<Expression>right)._gobj))

    cdef RingElement _div_c_impl(left, RingElement right):
        """
        Divide left and right.

            sage: var("x y", ns=1)
            (x, y)
            sage: x/y/y
            x*y^(-2)
        """
        return new_Expression_from_GEx(gdiv(left._gobj, (<Expression>right)._gobj))

    cdef int _cmp_c_impl(left, Element right) except -2:
        # TODO: this is never called, maybe, since I define
        # richcmp above to make formal symbolic expressions?
        return left._gobj.compare((<Expression>right)._gobj)

    def cmp(self, right):
        """
        Return -1, 0, or 1, depending on whether self < right,
        self == right, or self > right.
        """
        cdef Expression r = self.coerce_in(right)
        return self._gobj.compare(r._gobj)

    def __pow__(Expression self, exp, ignored):
        """
        Return self raised to the power of exp.

        INPUT:
            self -- symbolic expression
            exp -- something that coerces to a symbolic expressions

        OUTPUT:
            symbolic expression

        EXAMPLES:
            sage: var('x,y',ns=1); S=x.parent()
            (x, y)
            sage: x.__pow__(y)
            x^y
            sage: x^(3/5)
            x^(3/5)
            sage: x^sin(x)^cos(y)
            x^(sin(x)^cos(y))
        """
        cdef Expression nexp = self.coerce_in(exp)
        return new_Expression_from_GEx(g_pow(self._gobj, nexp._gobj))

    def expand(Expression self):
        """
        Return expanded form of his expression, obtained by multiplying out
        all products.

        OUTPUT:
            symbolic expression

        EXAMPLES:
            sage: var('x,y',ns=1)
            (x, y)
            sage: ((x + (2/3)*y)^3).expand()
            4/3*x*y^2 + 2*x^2*y + x^3 + 8/27*y^3
            sage: expand( (x*sin(x) - cos(y)/x)^2 )
            sin(x)^2*x^2 - 2*sin(x)*cos(y) + cos(y)^2*x^(-2)
            sage: f = (x-y)*(x+y); f
            (x - y)*(x + y)
            sage: f.expand()
            x^2 - y^2
        """
        return new_Expression_from_GEx(self._gobj.expand(0))

    def collect(Expression self, s):
        """
        INPUT:
            s -- a symbol

        OUTPUT:
            expression

        EXAMPLES:
            sage: var('x,y,z',ns=1)
            (x, y, z)
            sage: f = 4*x*y + x*z + 20*y^2 + 21*y*z + 4*z^2 + x^2*y^2*z^2
            sage: f.collect(x)
            21*y*z + x^2*y^2*z^2 + (4*y + z)*x + 20*y^2 + 4*z^2
            sage: f.collect(y)
            x*z + (4*x + 21*z)*y + (x^2*z^2 + 20)*y^2 + 4*z^2
            sage: f.collect(z)
            4*x*y + (x + 21*y)*z + (x^2*y^2 + 4)*z^2 + 20*y^2
        """
        cdef Expression s0 = self.coerce_in(s)
        return new_Expression_from_GEx(self._gobj.collect(s0._gobj, False))

    def __abs__(self):
        """
        Return the absolute value of this expression.

        EXAMPLES:
            sage: var('x, y', ns=1); S = parent(x)
            (x, y)

        The absolute value of a symbolic expression
            sage: abs(x^2+y^2)
            abs(x^2 + y^2)

        The absolute value of a number in the symbolic ring:
            sage: abs(S(-5))
            5
            sage: type(abs(S(-5)))
            <type 'sage.symbolic.expression.Expression'>
        """
        return new_Expression_from_GEx(g_abs(self._gobj))

    def step(self):
        """
        Return the value of the Heaviside step function, which is 0 for
        negative x, 1/2 for 0, and 1 for positive x.

        EXAMPLES:
            sage: x = var('x',ns=1); SR = x.parent()
            sage: SR(1.5).step()
            1
            sage: SR(0).step()
            1/2
            sage: SR(-1/2).step()
            0
            sage: SR(float(-1)).step()
            0
        """
        return new_Expression_from_GEx(g_step(self._gobj))

    def csgn(self):
        """
        Return the sign of self, which is -1 if self < 0, 0 if self ==
        0, and 1 if self > 0, or unevaluated when self is a nonconstant
        symbolic expression.

        It can be somewhat arbitrary when self is not real.

        EXAMPLES:
            sage: x = var('x', ns=1); SR = x.parent()
            sage: SR(-2).csgn()
            -1
            sage: SR(0.0).csgn()
            0
            sage: SR(10).csgn()
            1
            sage: x.csgn()
            csgn(x)
            sage: SR(CDF.0).csgn()
            1
        """
        return new_Expression_from_GEx(g_csgn(self._gobj))

    def conjugate(self):
        """
        Return the complex cnjugate of self.

        EXAMPLES:
            sage: x = var('x', ns=1); SR = x.parent()
            sage: SR(CDF.0).conjugate()
            -I
            sage: x.conjugate()
            conjugate(x)
            sage: SR(RDF(1.5)).conjugate()
            1.5
            sage: SR(float(1.5)).conjugate()
            1.0
        """
        return new_Expression_from_GEx(g_conjugate(self._gobj))

    def real_part(self):
        """
        Return the real part of self.

        EXAMPLES:
            sage: x = var('x', ns=1); SR = x.parent()
            sage: x.real_part()
            real_part(x)
            sage: SR(CDF(2,3)).real_part()
            2.0
            sage: SR(CC(2,3)).real_part()
            2.00000000000000
        """
        return new_Expression_from_GEx(g_real_part(self._gobj))

    def imag_part(self):
        """
        Return the imaginary part of self.

        EXAMPLES:
            sage: x = var('x', ns=1); SR = x.parent()
            sage: x.imag_part()
            imag_part(x)
            sage: SR(CC(2,3)).imag_part()
            3.00000000000000
            sage: SR(CDF(2,3)).imag_part()
            3.0
        """
        return new_Expression_from_GEx(g_imag_part(self._gobj))

    def sqrt(self):
        """
        EXAMPLES:
            sage: var('x, y', ns=1); S = parent(x)
            (x, y)
            sage: S(2).sqrt()
            sqrt(2)
            sage: (x^2+y^2).sqrt()
            sqrt(x^2 + y^2)
            sage: (x^2).sqrt()
            sqrt(x^2)
        """
        return new_Expression_from_GEx(g_sqrt(self._gobj))

    def sin(self):
        """
        EXAMPLES:
            sage: var('x, y', ns=1); S = parent(x)
            (x, y)
            sage: sin(x^2 + y^2)
            sin(x^2 + y^2)
            sage: sin(sage.symbolic.ring.pi)
            0
            sage: sin(S(1))
            sin(1)
            sage: sin(S(RealField(150)(1)))
            0.84147098480789650665250232163029899962256306
        """
        return new_Expression_from_GEx(g_sin(self._gobj))

    def cos(self):
        """
        Return the cosine of self.

        EXAMPLES:
            sage: var('x, y', ns=1); S = parent(x)
            (x, y)
            sage: cos(x^2 + y^2)
            cos(x^2 + y^2)
            sage: cos(sage.symbolic.ring.pi)
            -1
            sage: cos(S(1))
            cos(1)
            sage: cos(S(RealField(150)(1)))
            0.54030230586813971740093660744297660373231042
            sage: S(RR(1)).cos()
            0.540302305868140
            sage: S(float(1)).cos()
            0.54030230586813977
        """
        return new_Expression_from_GEx(g_cos(self._gobj))

    def tan(self):
        """
        EXAMPLES:
            sage: var('x, y', ns=1); S = parent(x)
            (x, y)
            sage: tan(x^2 + y^2)
            tan(x^2 + y^2)
            sage: tan(sage.symbolic.ring.pi/2)
            tan(1/2*Pi)
            sage: tan(S(1))
            tan(1)
            sage: tan(S(RealField(150)(1)))
            1.5574077246549022305069748074583601730872508
        """
        return new_Expression_from_GEx(g_tan(self._gobj))

    def arcsin(self):
        """
        Return the arcsin of x, i.e., the number y between -pi and pi
        such that sin(y) == x.

        EXAMPLES:
            sage: x = var('x', ns=1); SR = x.parent()
            sage: x.arcsin()
            asin(x)
            sage: SR(0.5).arcsin()
            0.523598775598299
            sage: SR(0.999).arcsin()
            1.52607123962616
            sage: SR(-0.999).arcsin()
            -1.52607123962616
        """
        return new_Expression_from_GEx(g_asin(self._gobj))

    def arccos(self):
        return new_Expression_from_GEx(g_acos(self._gobj))

    def arctan(self):
        return new_Expression_from_GEx(g_atan(self._gobj))

    def arctan2(self, Expression x):
        return new_Expression_from_GEx(g_atan2(self._gobj, x._gobj))

    def sinh(self):
        return new_Expression_from_GEx(g_sinh(self._gobj))

    def cosh(self):
        return new_Expression_from_GEx(g_cosh(self._gobj))

    def tanh(self):
        return new_Expression_from_GEx(g_tanh(self._gobj))

    def arcsinh(self):
        return new_Expression_from_GEx(g_asinh(self._gobj))

    def arccosh(self):
        return new_Expression_from_GEx(g_acosh(self._gobj))

    def arctanh(self):
        return new_Expression_from_GEx(g_atanh(self._gobj))

    def exp(self):
        return new_Expression_from_GEx(g_exp(self._gobj))

    def log(self):
        return new_Expression_from_GEx(g_log(self._gobj))

    def Li(self, Expression x):
        return new_Expression_from_GEx(g_Li(self._gobj, x._gobj))

    def zeta(self):
        return new_Expression_from_GEx(g_zeta(self._gobj))

    def factorial(self):
        """
        OUTPUT:
            symbolic expression

        EXAMPLES:
            sage: var('x, y', ns=1); S = parent(x)
            (x, y)
            sage: S(5).factorial()
            120
            sage: x.factorial()
            x!
            sage: (x^2+y^3).factorial()
            (x^2 + y^3)!
        """
        return new_Expression_from_GEx(g_factorial(self._gobj))

    def binomial(self, Expression k):
        """
        OUTPUT:
            symbolic expression

        EXAMPLES:
            sage: var('x, y', ns=1); S = parent(x)
            (x, y)
            sage: S(5).binomial(S(3))
            10
            sage: x.binomial(S(3))
            1/6*x^3 - 1/2*x^2 + 1/3*x
            sage: x.binomial(y)
            binomial(x,y)
        """
        return new_Expression_from_GEx(g_binomial(self._gobj, k._gobj))

    def Order(self):
        """
        Order, as in big oh notation.

        OUTPUT:
            symbolic expression

        EXAMPLES:
            sage: n = var('n', ns=1)
            sage: (17*n^3).Order()
            Order(n^3)
        """
        return new_Expression_from_GEx(g_Order(self._gobj))

    def lgamma(self):
       return new_Expression_from_GEx(g_lgamma(self._gobj))

    # Functions to add later, maybe.  These were in Ginac mainly
    # implemented using a lot from cln, and I had to mostly delete
    # their implementations.   They are pretty specialized for
    # physics apps, maybe.
    #def Li2(self):
    #    return new_Expression_from_GEx(g_Li2(self._gobj))
    #def G(self, Expression y):
    #    return new_Expression_from_GEx(g_G(self._gobj, y._gobj))
    #def G2(self, Expression s, Expression y):
    #    return new_Expression_from_GEx(g_G2(self._gobj, s._gobj, y._gobj))
    #def S(self, Expression p, Expression x):
    #return new_Expression_from_GEx(g_S(self._gobj, p._gobj, x._gobj))
    #def H(self, Expression x):
    #return new_Expression_from_GEx(g_H(self._gobj, x._gobj))
    #def zeta2(self, Expression s):
    #    return new_Expression_from_GEx(g_zeta2(self._gobj, s._gobj))
    #def zetaderiv(self, Expression x):
    #    return new_Expression_from_GEx(g_zetaderiv(self._gobj, x._gobj))
    #def tgamma(self):
    #    return new_Expression_from_GEx(g_tgamma(self._gobj))
    #def beta(self, Expression y):
    #    return new_Expression_from_GEx(g_beta(self._gobj, y._gobj))
    #def psi(self):
    #    return new_Expression_from_GEx(g_psi(self._gobj))
    #def psi2(self, Expression x):
    #    return new_Expression_from_GEx(g_psi2(self._gobj, x._gobj))



cdef Expression new_Expression_from_GEx(GEx juice):
    cdef Expression nex
    nex = <Expression>PY_NEW(Expression)
    GEx_construct_ex(&nex._gobj, juice)
    nex._parent = ring.NSR
    return nex
