"""
Univariate Polynomial Base Class

AUTHORS:
    -- William Stein: first version
    -- Martin Albrecht: Added singular coercion.
    -- Robert Bradshaw: Move Polynomial_generic_dense to SageX

TESTS:
     sage: R.<x> = ZZ[]
     sage: f = x^5 + 2*x^2 + (-1)
     sage: f == loads(dumps(f))
     True
"""

################################################################################
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
################################################################################

import operator

import copy

import sage.rings.rational
import sage.rings.integer
import polynomial_ring
import sage.rings.arith
#import sage.rings.ring_element
import sage.rings.integer_ring
import sage.rings.rational_field
import sage.rings.integer_mod_ring
import sage.rings.complex_field
import sage.rings.fraction_field_element
from sage.rings.infinity import infinity
#import sage.misc.misc as misc
from sage.misc.sage_eval import sage_eval
from sage.misc.latex import latex
from sage.structure.factorization import Factorization

from sage.interfaces.all import singular as singular_default, is_SingularElement
from sage.libs.all import pari, pari_gen, PariError

from sage.rings.real_mpfr import RealField, is_RealNumber, is_RealField
RR = RealField()

import sage.rings.real_double
import sage.rings.complex_double

from sage.structure.element import RingElement, generic_power
from sage.structure.element cimport Element, RingElement, ModuleElement, MonoidElement

from sage.rings.rational_field import QQ
from sage.rings.integer_ring import ZZ

from sage.rings.integral_domain import is_IntegralDomain

import polynomial_fateman

def is_Polynomial(f):
    return PY_TYPE_CHECK(f, Polynomial)

from polynomial_compiled cimport CompiledPolynomialFunction

#from polynomial_ring_constructor import PolynomialRing
from polydict import ETuple

cdef class Polynomial(CommutativeAlgebraElement):
    """
    A polynomial.

    EXAMPLE:
        sage: R.<y> = QQ['y']
        sage: S.<x> = R['x']
        sage: f = x*y; f
        y*x
        sage: type(f)
        <type 'sage.rings.polynomial.polynomial_element.Polynomial_generic_dense'>
        sage: p = (y+1)^10; p(1)
        1024
    """

    def __init__(self, parent, is_gen = False, construct=False):
        """
        The following examples illustrate creation of elements of
        polynomial rings, and some basic arithmetic.

        First we make a polynomial over the integers and do some arithmetic:
            sage: R.<x> = ZZ[]
            sage: f = x^5 + 2*x^2 + (-1); f
            x^5 + 2*x^2 - 1
            sage: f^2
            x^10 + 4*x^7 - 2*x^5 + 4*x^4 - 4*x^2 + 1

        Next we do arithmetic in a sparse polynomial ring over the integers:
            sage: R.<x> = ZZ[ ]; R
            Univariate Polynomial Ring in x over Integer Ring
            sage: S.<Z> = R[ ]; S
            Univariate Polynomial Ring in Z over Univariate Polynomial Ring in x over Integer Ring
            sage: f = Z^3 + (x^2-2*x+1)*Z - 3; f
            Z^3 + (x^2 - 2*x + 1)*Z + -3
            sage: f*f
            Z^6 + (2*x^2 - 4*x + 2)*Z^4 + (-6)*Z^3 + (x^4 - 4*x^3 + 6*x^2 - 4*x + 1)*Z^2 + (-6*x^2 + 12*x - 6)*Z + 9
            sage: f^3 == f*f*f
            True
        """
        CommutativeAlgebraElement.__init__(self, parent)
        self._is_gen = is_gen

    def _dict_to_list(self, x, zero):
          if len(x) == 0:
              return []
          n = max(x.keys())
          if PY_TYPE_CHECK(n, tuple): # a mpoly dict
              n = n[0]
              v = [zero] * (n+1)
              for i, z in x.iteritems():
                  v[i[0]] = z
          else:
              v = [zero] * (n+1)
              for i, z in x.iteritems():
                  v[i] = z
          return v

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        cdef Py_ssize_t i, min
        x = self.list()
        y = right.list()

        if len(x) > len(y):
            min = len(y)
            high = x[min:]
        elif len(x) < len(y):
            min = len(x)
            high = y[min:]
        else:
            min = len(x)
            high = []

        low = [x[i] + y[i] for i from 0 <= i < min]
        return self.polynomial(low + high)

    cdef ModuleElement _neg_c_impl(self):
        return self.polynomial([-x for x in self.list()])

    def plot(self, xmin=None, xmax=None, *args, **kwds):
        """
        Return a plot of this polynomial.

        INPUT:
            xmin -- float
            xmax -- float
            *args, **kwds -- passed to either point or point

        OUTPUT:
            returns a graphic object.

        EXAMPLES:
            sage: x = polygen(GF(389))
            sage: plot(x^2 + 1, rgbcolor=(0,0,1)).save()
            sage: x = polygen(QQ)
            sage: plot(x^2 + 1, rgbcolor=(1,0,0)).save()
        """
        R = self.base_ring()
        from sage.plot.plot import plot, point, line
        if R.characteristic() == 0:
            return plot(self.__call__, xmin=xmin, xmax=xmax, *args, **kwds)
        else:
            if R.is_finite():
                v = list(R)
                v.sort()
                w = dict([(v[i],i) for i in range(len(v))])
                z = [(i, w[self(v[i])]) for i in range(len(v))]
                return point(z, *args, **kwds)
        raise NotImplementedError, "plotting of polynomials over %s not implemented"%R

    cdef ModuleElement _lmul_c_impl(self, RingElement left):
        """
        Multiply self on the left by a scalar.

        EXAMPLE:
            sage: R.<x> = ZZ[]
            sage: f = (x^3 + x + 5)
            sage: f._lmul_(7)
            7*x^3 + 7*x + 35
            sage: 7*f
            7*x^3 + 7*x + 35
        """
        # todo -- should multiply individual coefficients??
        #         that could be in derived class.
        #         Note that we are guaranteed that right is in the base ring, so this could be fast.
        if left == 0:
            return self.parent()(0)
        return self.parent()(left) * self

    cdef ModuleElement _rmul_c_impl(self, RingElement right):
        """
        Multiply self on the right by a scalar.

        EXAMPLE:
            sage: R.<x> = ZZ[]
            sage: f = (x^3 + x + 5)
            sage: f._rmul_(7)
            7*x^3 + 7*x + 35
            sage: f*7
            7*x^3 + 7*x + 35
        """
        # todo -- Should multiply individual coefficients??
        #         that could be in derived class.
        #         Note that we are guaranteed that right is in the base ring, so this could be fast.
        if right == 0:
            return self.parent()(0)
        return self * self.parent()(right)

    def subs(self, *x, **kwds):
        r"""
        Identical to self(*x).

        See the docstring for \code{self.__call__}.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x^3 + x - 3
            sage: f.subs(x=5)
            127
            sage: f.subs(5)
            127
        """
        return self.__call__(*x, **kwds)

    def __call__(self, *x, **kwds):
        """
        Evaluate polynomial at x=a.

        INPUT:
            a -- ring element a; need not be in the coefficient
                 ring of the polynomial.
          -- or --
            a dictionary for kwds:value pairs.  If the variable
            name of the polynomial is a kwds it is substituted in;
            otherwise this polynomial is returned unchanged.

        OUTPUT:
            the value of f at a.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x/2 - 5
            sage: f(3)
            -7/2
            sage: R.<x> = ZZ[]
            sage: f = (x-1)^5
            sage: f(2/3)
            -1/243

        We evaluate a polynomial over a quaternion algebra:
            sage: A.<i,j,k> = QuaternionAlgebra(QQ, -1,-1)
            sage: R.<w> = PolynomialRing(A,sparse=True)
            sage: f = i*j*w^5 - 13*i*w^2 + (i+j)*w + i
            sage: f(i+j+1)
            24 + 26*i - 10*j - 25*k
            sage: w = i+j+1; i*j*w^5 - 13*i*w^2 + (i+j)*w + i
            24 + 26*i - 10*j - 25*k

        The parent ring of the answer always "starts" with the parent
        of the object at which we are evaluating.  Thus, e.g., if
        we input a matrix, we are guaranteed to get a matrix out,
        though the base ring of that matrix may change depending on
        the base of the polynomial ring.
            sage: R.<x> = QQ[]
            sage: f = R(2/3)
            sage: a = matrix(ZZ,2)
            sage: b = f(a); b
            [2/3   0]
            [  0 2/3]
            sage: b.parent()
            Full MatrixSpace of 2 by 2 dense matrices over Rational Field
            sage: f = R(1)
            sage: b = f(a); b
            [1 0]
            [0 1]
            sage: b.parent()
            Full MatrixSpace of 2 by 2 dense matrices over Rational Field

            sage: R.<w> = GF(17)[]
            sage: f = w^3 + 3*w +2
            sage: f(5)
            6
            sage: f(w=5)
            6
            sage: f(x=10)   # x isn't mention
            w^3 + 3*w + 2

        Nested polynomial ring elements can be called like multi-variate polynomials.
            sage: R.<x> = QQ[]; S.<y> = R[]
            sage: f = x+y*x+y^2
            sage: f.parent()
            Univariate Polynomial Ring in y over Univariate Polynomial Ring in x over Rational Field
            sage: f(2)
            3*x + 4
            sage: f(2,4)
            16
            sage: f(y=2,x=4)
            16
            sage: f(2,x=4)
            16
            sage: f(2,x=4,z=5)
            16
            sage: f(2,4, z=10)
            16
            sage: f(y=x)
            2*x^2 + x
            sage: f(x=y)
            2*y^2 + y

        The following results in an element of the symbolic ring.
            sage: f(x=sqrt(2))
            y*(y + sqrt(2)) + sqrt(2)

            sage: R.<t> = PowerSeriesRing(QQ, 't'); S.<x> = R[]
            sage: f = 1 + x*t^2 + 3*x*t^4
            sage: f(2)
            1 + 2*t^2 + 6*t^4
            sage: f(2, 1/2)
            15/8

        AUTHORS:
            -- David Joyner, 2005-04-10
            -- William Stein, 2006-01-22; change so parent
               is determined by the arithmetic
            -- William Stein, 2007-03-24: fix parent being determined in the constant case!
            -- Robert Bradshaw, 2007-04-09: add support for nested calling
            -- Tom Boothby, 2007-05-01: evaluation done by CompiledPolynomialFunction
            -- William Stein, 2007-06-03: add support for keyword arguments.
        """
        cdef long i, d = self.degree()

        if len(kwds) >= 1:
            P = self.parent()
            name = P.variable_name()
            if kwds.has_key(name):
                if len(x) > 0:
                    raise ValueError, "must not specify both a keyword and positional argument"
                a = self(kwds[name])
                del kwds[name]
                try:
                    return a(**kwds)
                except TypeError:
                    return a
            elif len(x) > 0:
                a = self(*x)
                try:
                    return a(**kwds)
                except TypeError:
                    return a
            else:
                result = self[d]
                a = P.gen()
                i = d - 1
                while i >= 0:
                    try:
                        s = self[i](**kwds)
                    except TypeError:
                        s = self[i]
                    result = result * a + s
                    i -= 1
                return result

        if len(x) == 0:
            return self

        if isinstance(x[0], tuple):
            x = x[0]
        a = x[0]

        result = self[d]
        if len(x) > 1:
            other_args = x[1:]
            if hasattr(result, '__call__'):
                result = result(other_args)
            else:
                raise TypeError, "Wrong number of arguments"

        if d == 0:
            try:
                return a.parent()(1) * result
            except AttributeError:
                return result

        i = d - 1
        if len(x) > 1:
            while i >= 0:
                result = result * a + self[i](other_args)
                i -= 1
        elif d < 4 and self._compiled is None:
            while i >= 0:
                result = result * a + self[i]
                i -= 1
        else:
            if self._compiled is None:
                self._compiled = CompiledPolynomialFunction(self.list())
            result = self._compiled.eval(a)
        return result

    def _compile(self):
        # For testing
        self._compiled = CompiledPolynomialFunction(self.list())
        return self._compiled

    cdef int _cmp_c_impl(self, Element other) except -2:
        """
        Compare the two polynomials self and other.

        We order polynomials first by degree, then in dictionary order
        starting with the coefficient of largest degree.

        EXAMPLES:
            sage: R.<x> = QQ['x']
            sage: 3*x^3  + 5 > 10*x^2 + 19
            True
            sage: x^2 - 2*x - 1 < x^2 - 1
            True
            sage: x^2 - 2*x - 1 > x^2 - 1
            False
            sage: R(-1) < 0
            False
            sage: x^3 - 3 > 393939393
            True
        """
        d1 = self.degree(); d2 = other.degree()
        c = cmp(d1, d2)
        if c: return c
        for i in reversed(xrange(d1+1)):
            c = cmp(self[i], other[i])
            if c: return c
        return 0

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    def __nonzero__(self):
        """
        EXAMPLES:
            sage: P = PolynomialRing(ZZ,'x')(0)
            sage: bool(P)
            False
            sage: P = PolynomialRing(ZZ, 'x')([1,2,3])
            sage: bool(P)
            True
        """
        return self.degree() >= 0

    def __getitem__(self, n):
        raise NotImplementedError

    def __iter__(self):
        return iter(self.list())

    def __hash__(self):
        if self.degree() >= 1:
            return hash(tuple(self.list()))
        else:
            return hash(self[0])

    def __float__(self):
         if self.degree() > 0:
             raise TypeError, "cannot coerce nonconstant polynomial to float"
         return float(self[0])

    def __int__(self):
        if self.degree() > 0:
            raise TypeError, "cannot coerce nonconstant polynomial to int"
        return int(self[0])

    def _im_gens_(self, codomain, im_gens):
        """
        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: H = Hom(R, QQ); H
            Set of Homomorphisms from Univariate Polynomial Ring in x over Integer Ring to Rational Field
            sage: f = H([5]); f
            Ring morphism:
              From: Univariate Polynomial Ring in x over Integer Ring
              To:   Rational Field
              Defn: x |--> 5
            sage: f(x)
            5
            sage: f(x^2 + 3)
            28
        """
        a = im_gens[0]
        P = a.parent()
        d = self.degree()
        result = P._coerce_(self[d])
        i = d - 1
        while i >= 0:
            result = result * a + P._coerce_(self[i])
            i -= 1
        return result

    def _integer_(self):
        if self.degree() > 0:
            raise TypeError, "cannot coerce nonconstant polynomial"
        return sage.rings.integer.Integer(self[0])

    def __invert__(self):
        """
        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x - 90283
            sage: f.__invert__()
            1/(x - 90283)
            sage: ~f
            1/(x - 90283)
        """
        return self.parent()(1)/self

    def inverse_of_unit(self):
        """
        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x - 90283
            sage: f.inverse_of_unit()
            Traceback (most recent call last):
            ...
            ValueError: self is not a unit.
            sage: f = R(-90283); g = f.inverse_of_unit(); g
            -1/90283
            sage: parent(g)
            Univariate Polynomial Ring in x over Rational Field
        """
        if self.degree() > 0:
            if not self.is_unit():
                raise ValueError, "self is not a unit."
            else:
                raise NotImplementedError, "polynomial inversion over non-integral domains not implemented"
        return self.parent()(~(self[0]))

    def inverse_mod(a, m):
        """
        Inverts the polynomial a with respect to m, or throw a
        ValueError if no such inverse exists.

        EXAMMPLES:
            sage: S.<t> = QQ[]
            sage: f = inverse_mod(t^2 + 1, t^3 + 1); f
            -1/2*t^2 - 1/2*t + 1/2
            sage: f * (t^2 + 1) % (t^3 + 1)
            1
            sage: f = t.inverse_mod((t+1)^7); f
            -t^6 - 7*t^5 - 21*t^4 - 35*t^3 - 35*t^2 - 21*t - 7
            sage: (f * t) + (t+1)^7
            1

        It also works over in-exact rings, but note that due to rounding
        error the product is only guerenteed to be withing epsilon of the
        constant polynomial 1.
            sage: R.<x> = RDF[]
            sage: f = inverse_mod(x^2 + 1, x^5 + x + 1); f
            0.4*x^4 - 0.2*x^3 - 0.4*x^2 + 0.2*x + 0.8
            sage: f * (x^2 + 1) % (x^5 + x + 1)
            5.55111512313e-17*x^3 + 1.66533453694e-16*x^2 + 5.55111512313e-17*x + 1.0
            sage: f = inverse_mod(x^3 - x + 1, x - 2); f
            0.142857142857
            sage: f * (x^3 - x + 1) % (x - 2)
            1.0

        ALGORITHM:
            Solve the system as + mt = 1, returning s as the inverse
            of a mod m.

            Uses the Euclidean algorithm for exact rings, and solves a
            linear system for the coefficients of s and t for inexact rings
            (as the Euclidean algorithm may not converge in that case).

        AUTHOR:
            -- Robert Bradshaw (2007-05-31)
        """
        if m.degree() == 1 and m[1].is_unit():
            # a(x) mod (x-r) = a(r)
            r = -m[0]
            if not m[1].is_one():
                r *= m.base_ring()(~m[1])
            u = a(r)
            if u.is_unit():
                return a.parent()(~u)
        if a.parent().is_exact():
            # use xgcd
            g, s, _ = a.xgcd(m)
            if g == 1:
                return s
            elif g.is_unit():
                return g.inverse_of_unit() * s
            else:
                raise ValueError, "Impossible inverse modulo"
        else:
            # xgcd may not converge for inexact rings.
            # Instead solve for the coefficients of
            # s (degree n-1) and t (degree n-2) in
            #               as + mt = 1
            # as a linear system.
            from sage.matrix.constructor import matrix
            from sage.modules.free_module_element import vector
            a %= m
            n = m.degree()
            R = a.parent().base_ring()
            M = matrix(R, 2*n-1)
            # a_i s_j x^{i+j} terms
            for i in range(n):
                for j in range(n):
                    M[i+j, j] = a[i]
            # m_i t_j x^{i+j} terms
            for i in range(n+1):
                for j in range(n-1):
                    M[i+j, j+n] = m[i]
            v = vector(R, [R(1)] + [R(0)]*(2*n-2)) # the constant polynomial 1
            if M.is_invertible():
                x = M.solve_right(v) # there has to be a better way to solve
                return a.parent()(list(x)[0:n])
            else:
                raise ValueError, "Impossible inverse modulo"


    def __long__(self):
        """
        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: f = x - 902384
            sage: long(f)
            Traceback (most recent call last):
            ...
            TypeError: cannot coerce nonconstant polynomial to long
            sage: long(R(939392920202))
            939392920202L
        """
        if self.degree() > 0:
            raise TypeError, "cannot coerce nonconstant polynomial to long"
        return long(self[0])

    cdef RingElement _mul_c_impl(self, RingElement right):
        """
        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: (x - 4)*(x^2 - 8*x + 16)
            x^3 - 12*x^2 + 48*x - 64
        """
        if right == 0 or self == 0:
            return self.polynomial(0)
        return self._mul_karatsuba(right)

    def square(self):
        """
        Returns the square of this polynomial.

        TODO:
          -- This is just a placeholder; for now it just uses ordinary
          multiplication. But generally speaking, squaring is faster than
          ordinary multiplication, and it's frequently used, so subclasses
          may choose to provide a specialised squaring routine.

          -- Perhaps this even belongs at a lower level? ring_element
          or something?

        AUTHOR:
          -- David Harvey (2006-09-09)

        """
        return self * self

    def __div__(self, right):
        """
        EXAMPLES:
            sage: x = QQ['x'].0
            sage: f = (x^3 + 5)/3; f
            1/3*x^3 + 5/3
            sage: f.parent()
            Univariate Polynomial Ring in x over Rational Field

        If we do the same over $\ZZ$ the result is in the polynomial
        ring over $\QQ$.

            sage: x  = ZZ['x'].0
            sage: f = (x^3 + 5)/3; f
            1/3*x^3 + 5/3
            sage: f.parent()
            Univariate Polynomial Ring in x over Rational Field

        Divides can make elements of the fraction field:

            sage: R.<x> = QQ['x']
            sage: f = x^3 + 5
            sage: g = R(3)
            sage: h = f/g; h
            1/3*x^3 + 5/3
            sage: h.parent()
            Fraction Field of Univariate Polynomial Ring in x over Rational Field

        This is another example over a non-prime finite field
        (submited by a student of Jon Hanke).  It illustrates
        cancellation between the numerator and denominator
        over a non-prime finite field.
            sage: R.<x> = PolynomialRing(GF(5^2, 'a'), 'x')
            sage: f = x^3 + 4*x
            sage: f / (x - 1)
            x^2 + x

        Be careful about coercions (this used to be broken):
            sage: R.<x> = ZZ['x']
            sage: f = x / Mod(2,5); f
            3*x
            sage: f.parent()
            Univariate Polynomial Ring in x over Ring of integers modulo 5
        """
        try:
            if not isinstance(right, Element) or right.parent() != self.parent():
                R = self.parent().base_ring()
                x = R._coerce_(right)
                return self * ~x
        except (TypeError, ValueError, ZeroDivisionError):
            pass
        return RingElement.__div__(self, right)


    def __pow__(self, right, dummy):
        """
        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: f = x - 1
            sage: f._pow(3)
            x^3 - 3*x^2 + 3*x - 1
            sage: f^3
            x^3 - 3*x^2 + 3*x - 1
        """
        if self.degree() <= 0:
            return self.parent()(self[0]**right)
        if right < 0:
            return (~self)**(-right)
        if (<Polynomial>self)._is_gen:   # special case x**n should be faster!
            P = self.parent()
            R = P.base_ring()
            if P.is_sparse():
                v = {right:R(1)}
            else:
                v = [R(0)]*right + [R(1)]
            return self.parent()(v, check=False)
        return generic_power(self, right)

    def _pow(self, right):
        # TODO: fit __pow__ into the arithmatic structure
        if self.degree() <= 0:
            return self.parent()(self[0]**right)
        if right < 0:
            return (~self)**(-right)
        if (<Polynomial>self)._is_gen:   # special case x**n should be faster!
            v = [0]*right + [1]
            return self.parent()(v, check=True)
        return generic_power(self, right)

    def _repr(self, name=None):
        s = " "
        m = self.degree() + 1
        r = reversed(xrange(m))
        if name is None:
            name = self.parent().variable_name()
        atomic_repr = self.parent().base_ring().is_atomic_repr()
        coeffs = self.list()
        for n in reversed(xrange(m)):
            x = coeffs[n]
            if x != 0:
                if n != m-1:
                    s += " + "
                x = repr(x)
                if not atomic_repr and n > 0 and (x.find("+") != -1 or x.find("-") != -1):
                    x = "(%s)"%x
                if n > 1:
                    var = "*%s^%s"%(name,n)
                elif n==1:
                    var = "*%s"%name
                else:
                    var = ""
                s += "%s%s"%(x,var)
        if atomic_repr:
            s = s.replace(" + -", " - ")
        s = s.replace(" 1*"," ")
        s = s.replace(" -1*", " -")
        if s==" ":
            return "0"
        return s[1:]

    def _repr_(self):
        r"""
        Return string representatin of this polynomial.

        EXAMPLES:
            sage: x = polygen(QQ)
            sage: f = x^3+2/3*x^2 - 5/3
            sage: f._repr_()
            'x^3 + 2/3*x^2 - 5/3'
            sage: f.rename('vaughn')
            sage: f
            vaughn
        """
        return self._repr()

    def _latex_(self, name=None):
        r"""
        EXAMPLES:
			sage: x = polygen(QQ)
            sage: latex(x^3+2/3*x^2 - 5/3)
             x^{3} + \frac{2}{3}x^{2} - \frac{5}{3}
        """
        s = " "
        m = self.degree() + 1
        r = reversed(xrange(m))
        if name is None:
            name = self.parent().variable_name()
        atomic_repr = self.parent().base_ring().is_atomic_repr()
        coeffs = self.list()
        for n in reversed(xrange(m)):
            x = coeffs[n]
            if x != 0:
                if n != m-1:
                    s += " + "
                x = latex(x)
                if not atomic_repr and n > 0 and (x.find("+") != -1 or x.find("-") != -1):
                    x = "\\left(%s\\right)"%x
                if n > 1:
                    var = "|%s^{%s}"%(name,n)
                elif n==1:
                    var = "|%s"%name
                else:
                    var = ""
                s += "%s%s"%(x,var)
        if atomic_repr:
            s = s.replace(" + -", " - ")
        s = s.replace(" 1|"," ")
        s = s.replace(" -1|", " -")
        s = s.replace("|","")
        if s==" ":
            return "0"
        return s[1:]


    def __setitem__(self, n, value):
        raise IndexError, "polynomials are immutable"


    def __floordiv__(self,right):
        """
        Quotient of division of self by other.  This is denoted //.
        """
        Q, _ = self.quo_rem(right)
        return Q

    def div(self,right):
        """
        Quotient of division of self by other.
        """
        Q, _ = self.quo_rem(right)
        return Q

    def __mod__(self, other):
        """
        Remainder of division of self by other.
        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: x % (x+1)
            -1
            sage: (x^3 + x - 1) % (x^2 - 1)
            2*x - 1
        """
        _, R = self.quo_rem(other)
        return R

    def _is_atomic(self):
        return self.degree() == self.valuation()

    def _mul_generic(self, right):
        if self is right:
            return self._square_generic()
        x = self.list()
        y = right.list()
        cdef Py_ssize_t i, k, start, end
        cdef Py_ssize_t d1 = len(x)-1, d2 = len(y)-1
        if d1 == -1:
            return self
        elif d2 == -1:
            return right
        elif d1 == 0:
            c = x[0]
            return self._parent([c*a for a in y])
        elif d2 == 0:
            c = y[0]
            return self._parent([a*c for a in x])
        coeffs = []
        for k from 0 <= k <= d1+d2:
            start = 0 if k <= d2 else k-d2 # max(0, k-d2)
            end =   k if k <= d1 else d1    # min(k, d1)
            sum = x[start] * y[k-start]
            for i from start < i <= end:
                sum += x[i] * y[k-i]
            coeffs.append(sum)
        return self._parent(coeffs)

    def _square_generic(self):
        x = self.list()
        cdef Py_ssize_t i, j
        cdef Py_ssize_t d = len(x)-1
        zero = self._parent.base_ring()(0)
        two = self._parent.base_ring()(2)
        coeffs = [zero] * (2 * d + 1)
        for i from 0 <= i <= d:
            coeffs[2*i] = x[i] * x[i]
            for j from 0 <= j < i:
                coeffs[i+j] += two * x[i] * x[j]
        return self._parent(coeffs)

    def _mul_fateman(self, right):
        r"""
        Returns the product of two polynomials using Kronecker's trick
        to do the multiplication.  This could be used used over a
        generic base ring.

        NOTES:
        \begin{itemize}
          \item Since this is implemented in interpreted Python, it
                could be hugely sped up by reimplementing it in Pyrex.
          \item Over the reals there is precision loss, at least in
                the current implementation.
        \end{itemize}

        INPUT:
           self -- Polynomial
           right -- Polynomial (over same base ring as self)

        OUTPUT: Polynomial
           The product self*right.

        ALGORITHM:
        Based on a paper by R. Fateman

          {\tt http://www.cs.berkeley.edu/~fateman/papers/polysbyGMP.pdf}

        The idea is to encode dense univariate polynomials as big
        integers, instead of sequences of coefficients. The paper
        argues that because integer multiplication is so cheap, that
        encoding 2 polynomials to big numbers and then decoding the
        result might be faster than popular multiplication algorithms.
        This seems true when the degree is larger than 200.

        EXAMPLES:
            sage: S.<y> = PolynomialRing(RR)
            sage: f = y^10 - 1.393493*y + 0.3
            sage: f._mul_karatsuba(f)
            1.00000000000000*y^20 - 2.78698600000000*y^11 + 0.600000000000000*y^10 + 0.000000000000000111022302462516*y^8 - 0.000000000000000111022302462516*y^6 - 0.000000000000000111022302462516*y^3 + 1.94182274104900*y^2 - 0.836095800000000*y + 0.0900000000000000
            sage: f._mul_fateman(f)
            1.00000000000000*y^20 - 2.78698600000000*y^11 + 0.600000000000000*y^10 + 1.94182274104900*y^2 - 0.836095800000000*y + 0.0900000000000000

        Advantages:

        \begin{itemize}

        \item Faster than Karatsuba over $\Q$ and $\Z$
             (but much slower still than calling NTL's
             optimized C++ implementation, which is the
             default over $\Z$)

        \item Potentially less complicated.

        \end{itemize}

        Drawbacks:
        \begin{itemize}
        \item Slower over R when the degree of both of polynomials is less
              than 250 (roughly).
        \item Over R, results may not be as accurate as the Karatsuba
              case. This is because we represent coefficients of
              polynomials over R as fractions, then convert them back to
              floating-point numbers.
        \end{itemize}

        AUTHOR:
           -- Didier Deshommes (2006-05-25)
        """
        return self.parent()(polynomial_fateman._mul_fateman_mul(self,right))

    def _mul_karatsuba(self, right):
        r"""
        Returns the product of two polynomials using the Karatsuba
        divide and conquer multiplication algorithm.  This is only
        used over a generic base ring.  (Special libraries like NTL
        are used, e.g., for the integers and rationals, which are much
        faster.)

        INPUT:
           self: Polynomial
           right: Polynomial (over same base ring as self)

        OUTPUT: Polynomial
           The product self*right.

        ALGORITHM:
           The basic idea is to use that
           $$
               (aX + b) (cX + d) = acX^2 + ((a+b)(c+d)-ac-bd)X + bd
           $$
           where ac=a*c and bd=b*d, which requires three
           multiplications instead of the naive four.  (In my examples,
           strangely just doing the above with four multiplications
           does tend to speed things up noticeably.)
           Given f and g of arbitrary degree bigger than one, let e
           be min(deg(f),deg(g))/2.  Write
           $$
                  f = a X^e + b   \text{ and }   g = c X^e + d
           $$
           and use the identity
           $$
                 (aX^e + b) (cX^e + d) = ac X^{2e} +((a+b)(c+d) - ac - bd)X^e + bd
           $$
           to recursively compute $fg$.

        TIMINGS:
        On a Pentium M 1.8Ghz laptop:
           f=R.random(1000,bound=100)
           g=R.random(1000,bound=100)
           time h=f._mul_karatsuba(g)
           Time: 0.42 seconds
           The naive multiplication algorithm takes 14.58 seconds.
           In contrast, MAGMA does this sort of product almost
           instantly, and can easily deal with degree 5000.  Basically
           MAGMA is 100 times faster at polynomial multiplication.

           Over Z using NTL, multiplying two polynomials constructed
           using R.random(10000,bound=100) takes 0.10 seconds.  Using
           MAGMA V2.11-10 the same takes 0.14 seconds.  So in this
           case NTL is somewhat faster than MAGMA.

           Over Q using PARI, multiplying two polynomials constructed
           using R.random(10000,bound=100) takes 1.23 seconds.  Not
           good!  TODO: use NTL polynomials over Z with a denominator
           instead of PARI.

        NOTES:
         * Karatsuba multiplication of polynomials is also implemented in PARI in
                src/basemath/polarit3.c
         * The MAGMA documentation appears to give no information about how
           polynomial multiplication is implemented.
        """
        return self._parent(do_karatsuba(self.list(), right.list()))

    def base_ring(self):
        """
        Return the base ring of the parent of self.

        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: x.base_ring()
            Integer Ring
            sage: (2*x+3).base_ring()
            Integer Ring
        """
        return self.parent().base_ring()

    def base_extend(self, R):
        """
        Return a copy of this polynomial but with coefficients in R, if there
        is a natural map from coefficient ring of self to R.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x^3 - 17*x + 3
            sage: f.base_extend(GF(7))
            Traceback (most recent call last):
            ...
            TypeError: no such base extension
            sage: f.change_ring(GF(7))
            x^3 + 4*x + 3
        """
        S = self.parent().base_extend(R)
        return S(self)

    def change_variable_name(self, var):
        """
        Return a new polynomial over the same base ring but in a different
        variable.

        EXAMPLES:
            sage: x = polygen(QQ,'x')
            sage: f = -2/7*x^3 + (2/3)*x - 19/993; f
            -2/7*x^3 + 2/3*x - 19/993
            sage: f.change_variable_name('theta')
            -2/7*theta^3 + 2/3*theta - 19/993
        """
        R = self.parent().base_ring()[var]
        return R(self.list())


    def change_ring(self, R):
        """
        Return a copy of this polynomial but with coefficients in R, if at
        all possible.

        EXAMPLES:
            sage: K.<z> = CyclotomicField(3)
            sage: f = K.defining_polynomial()
            sage: f.change_ring(GF(7))
            x^2 + x + 1
        """
        S = self.parent().change_ring(R)
        return S(self)

    def _mpoly_dict_recursive(self, vars=None, base_ring=None):
        """
        Return a dict of coefficent entries suitable for construction of a MPolynomial_polydict
        with the given variables.
        """
        if not self:
            return {}

        var = self.parent().variable_name()
        if vars is None:
            vars = self.parent().variable_names_recursive()
        if not var in vars:
            x = base_ring(self) if base_ring else self
            const_ix = ETuple((0,)*len(vars))
            return { const_ix: x }

        prev_vars = vars[:list(vars).index(var)]
        const_ix = ETuple((0,)*len(prev_vars))
        mpolys = None

        if len(prev_vars) > 0:
            try:
                mpolys = [a._mpoly_dict_recursive(prev_vars, base_ring) for a in self]
            except AttributeError, msg:
                pass

        if mpolys is None:
            if base_ring is not None and base_ring is not self.base_ring():
                mpolys = [{const_ix:base_ring(a)} if a else {} for a in self]
            else:
                mpolys = [{const_ix:a} if a else {} for a in self]

        D = {}
        leftovers = (0,) * (len(vars) - len(prev_vars) - 1)
        for k in range(len(mpolys)):
            for i,a in mpolys[k].iteritems():
                j = ETuple((k,) + leftovers)
                D[i + j] = a

        return D


    def __copy__(self):
        """
        Return a "copy" of self.  This is just self, since in SAGE polynomials are
        immutable this just returns self again.

        EXAMPLES:
        We create the polynomial $f=x+3$, then note that the copy is just
        the same polynomial again, which is fine since polynomials are immutable.

            sage: x = ZZ['x'].0
            sage: f = x + 3
            sage: g = copy(f)
            sage: g is f
            True
        """
        return self

    def degree(self):
        """
        Return the degree of this polynomial.  The zero polynomial
        has degree -1.

        EXAMPLES:
            sage: x = ZZ['x'].0
            sage: f = x^93 + 2*x + 1
            sage: f.degree()
            93
            sage: x = PolynomialRing(QQ, 'x', sparse=True).0
            sage: f = x^100000
            sage: f.degree()
            100000

            sage: x = QQ['x'].0
            sage: f = 2006*x^2006 - x^2 + 3
            sage: f.degree()
            2006
            sage: f = 0*x
            sage: f.degree()
            -1
            sage: f = x + 33
            sage: f.degree()
            1

        AUTHORS:
            -- Naqi Jaffery (2006-01-24): examples
        """
        raise NotImplementedError

    def denominator(self):
        """
        Return the least common multiple of the denominators of
        the entries of self, when this makes sense, i.e., when the
        coefficients have a denominator function.

        WARNING: This is not the denominator of the rational function
        defined by self, which would always be 1 since self is a polynomial.

        EXAMPLES:
        First we compute the denominator of a polynomial with integer
        coefficients, which is of course 1.
            sage: R.<x> = ZZ[]
            sage: f = x^3 + 17*x + 1
            sage: f.denominator()
            1

        Next we compute the denominator of a polynomial with rational coefficients.
            sage: R.<x> = PolynomialRing(QQ)
            sage: f = (1/17)*x^19 - (2/3)*x + 1/3; f
            1/17*x^19 - 2/3*x + 1/3
            sage: f.denominator()
            51

        Finally, we try to compute the denominator of a polynomial with
        coefficients in the real numbers, which is a ring whose elements
        do not have a denominator method.
            sage: R.<x> = RR[]
            sage: f = x + RR('0.3'); f
            1.00000000000000*x + 0.300000000000000
            sage: f.denominator()
            Traceback (most recent call last):
            ...
            AttributeError: 'sage.rings.real_mpfr.RealNumber' object has no attribute 'denominator'
        """
        if self.degree() == -1:
            return 1
        R = self.base_ring()
        x = self.list()
        d = x[0].denominator()
        for y in x:
            d = d.lcm(y.denominator())
        return d

    def derivative(self):
        if self.is_zero():
            return self
        cdef Py_ssize_t n, degree = self.degree()
        if degree == 0:
            return self.parent()(0)
        coeffs = self.list()
        return self.polynomial([n*coeffs[n] for n from 1 <= n <= degree])

    def integral(self):
        cdef Py_ssize_t n, degree = self.degree()
        if degree < 0:
            return self.parent()(0)
        try:
            coeffs = self.list()
            return self.polynomial([0, coeffs[0]] + [coeffs[n]/(n+1) for n from 1 <= n <= degree])
        except TypeError:
            raise ArithmeticError, "coefficients of integral cannot be coerced into the base ring"


    def dict(self):
        """
        Return a sparse dictionary representation of this univariate polynomial.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x^3 + -1/7*x + 13
            sage: f.dict()
            {0: 13, 1: -1/7, 3: 1}
        """
        X = {}
        Y = self.list()
        for i in xrange(len(Y)):
            c = Y[i]
            if c:
                X[i] = c
        return X

    def factor(self):
        r"""
        Return the factorization of self over the base field of this polynomial.

        INPUT:
            a polynomial

        OUTPUT:
            Factorization -- the factorization of self, which is
            a product of a unit with a product of powers of irreducible
            factors.

        Over a field the irreducible factors are all monic.

        EXAMPLES:
        We factor some polynomials over $\Q$.
            sage: x = QQ['x'].0
            sage: f = (x^3 - 1)^2
            sage: f.factor()
            (x - 1)^2 * (x^2 + x + 1)^2

        Notice that over the field $\Q$ the irreducible factors are monic.
            sage: f = 10*x^5 - 1
            sage: f.factor()
            (10) * (x^5 - 1/10)
            sage: f = 10*x^5 - 10
            sage: f.factor()
            (10) * (x - 1) * (x^4 + x^3 + x^2 + x + 1)

        Over $\Z$ the irreducible factors need not be monic:
            sage: x = ZZ['x'].0
            sage: f = 10*x^5 - 1
            sage: f.factor()
            10*x^5 - 1


        We factor a non-monic polynomial over the finite field $F_{25}$.
            sage: k.<a> = GF(25)
            sage: R.<x> = k[]
            sage: f = 2*x^10 + 2*x + 2*a
            sage: F = f.factor(); F
            (2) * (x + a + 2) * (x^2 + 3*x + 4*a + 4) * (x^2 + (a + 1)*x + a + 2) * (x^5 + (3*a + 4)*x^4 + (3*a + 3)*x^3 + 2*a*x^2 + (3*a + 1)*x + 3*a + 1)

        Notice that the unit factor is included when we multiply $F$ back out.
            sage: expand(F)
            2*x^10 + 2*x + 2*a

        Factorization also works even if the variable of the finite field is nefariously
        labeled "x".
            sage: x = GF(3^2, 'a')['x'].0
            sage: f = x^10 +7*x -13
            sage: G = f.factor(); G
            (x + a) * (x + 2*a + 1) * (x^4 + (a + 2)*x^3 + (2*a + 2)*x + 2) * (x^4 + 2*a*x^3 + (a + 1)*x + 2)
            sage: prod(G) == f
            True

            sage: f.parent().base_ring()._assign_names(['a'])
            sage: f.factor()
            (x + a) * (x + 2*a + 1) * (x^4 + (a + 2)*x^3 + (2*a + 2)*x + 2) * (x^4 + 2*a*x^3 + (a + 1)*x + 2)

            sage: k = GF(9,'x')    # purposely calling it x to test robustness
            sage: x = PolynomialRing(k,'x0').gen()
            sage: f = x^3 + x + 1
            sage: f.factor()
            (x0 + 2) * (x0 + x) * (x0 + 2*x + 1)
            sage: f = 0*x
            sage: f.factor()
            Traceback (most recent call last):
            ...
            ValueError: factorization of 0 not defined

            sage: f = x^0
            sage: f.factor()
            1

        Arbitrary precision real and complex factorization:
            sage: R.<x> = RealField(100)[]
            sage: F = factor(x^2-3); F
            (1.0000000000000000000000000000*x + 1.7320508075688772935274463415) * (1.0000000000000000000000000000*x - 1.7320508075688772935274463415)
            sage: expand(F)
            1.0000000000000000000000000000*x^2 - 3.0000000000000000000000000000
            sage: factor(x^2 + 1)
            1.0000000000000000000000000000*x^2 + 1.0000000000000000000000000000
            sage: C = ComplexField(100)
            sage: R.<x> = C[]
            sage: F = factor(x^2+3); F
            (1.0000000000000000000000000000*x + -1.7320508075688772935274463415*I) * (1.0000000000000000000000000000*x + 1.7320508075688772935274463415*I)
            sage: expand(F)
            1.0000000000000000000000000000*x^2 + 3.0000000000000000000000000000
            sage: factor(x^2+1)
            (1.0000000000000000000000000000*x + -1.0000000000000000000000000000*I) * (1.0000000000000000000000000000*x + 1.0000000000000000000000000000*I)
            sage: f = C.0 * (x^2 + 1) ; f
            1.0000000000000000000000000000*I*x^2 + 1.0000000000000000000000000000*I
            sage: F = factor(f); F
            (1.0000000000000000000000000000*I) * (1.0000000000000000000000000000*x + -1.0000000000000000000000000000*I) * (1.0000000000000000000000000000*x + 1.0000000000000000000000000000*I)
            sage: expand(F)
            1.0000000000000000000000000000*I*x^2 + 1.0000000000000000000000000000*I

        Over a complicated number field:
            sage: x = polygen(QQ, 'x')
            sage: f = x^6 + 10/7*x^5 - 867/49*x^4 - 76/245*x^3 + 3148/35*x^2 - 25944/245*x + 48771/1225
            sage: K.<a> = NumberField(f)
            sage: S.<T> = K[]
            sage: ff = S(f); ff
            T^6 + 10/7*T^5 + (-867/49)*T^4 + (-76/245)*T^3 + 3148/35*T^2 + (-25944/245)*T + 48771/1225
            sage: F = ff.factor()
            sage: len(F)
            4
            sage: F[:2]
            [(T + -a, 1), (T + -40085763200/924556084127*a^5 - 145475769880/924556084127*a^4 + 527617096480/924556084127*a^3 + 1289745809920/924556084127*a^2 - 3227142391585/924556084127*a - 401502691578/924556084127, 1)]
            sage: expand(F)
            T^6 + 10/7*T^5 + (-867/49)*T^4 + (-76/245)*T^3 + 3148/35*T^2 + (-25944/245)*T + 48771/1225

        Over the real double field:
            sage: x = polygen(RDF)
            sage: f = (x-1)^3
            sage: f.factor() # random output (unfortunately)
            (1.0*x - 1.00000859959) * (1.0*x^2 - 1.99999140041*x + 0.999991400484)

        Note that this factorization suffers from the roots function:
            sage: f.roots() # random output (unfortunately)
            [1.00000859959, 0.999995700205 + 7.44736245561e-06*I, 0.999995700205 - 7.44736245561e-06*I]

        Over the complex double field.  Because this approximate, all factors will occur
        with multiplicity 1.
            sage: x = CDF['x'].0; i = CDF.0
            sage: f = (x^2 + 2*i)^3
            sage: f.factor()
            (1.0*x + -0.999994409957 + 1.00001040378*I) * (1.0*x + -0.999993785062 + 0.999989956987*I) * (1.0*x + -1.00001180498 + 0.999999639235*I) * (1.0*x + 0.999995530902 - 0.999987780431*I) * (1.0*x + 1.00001281704 - 1.00000223945*I) * (1.0*x + 0.999991652054 - 1.00000998012*I)
            sage: f(-f.factor()[0][0][0])
            -2.38358052913e-14 - 2.57571741713e-14*I


        Over a relative number field:
            sage: x = QQ['x'].0
            sage: L.<a> = CyclotomicField(3).extension(x^3 - 2)
            sage: x = L['x'].0
            sage: f = (x^3 + x + a)*(x^5 + x + L.1); f
            x^8 + x^6 + a*x^5 + x^4 + zeta3*x^3 + x^2 + (a + zeta3)*x + zeta3*a
            sage: f.factor()
            (x^3 + x + a) * (x^5 + x + zeta3)
        """

        # PERFORMANCE NOTE:
        #     In many tests with SMALL degree PARI is substantially
        #     better than NTL.  (And magma is better yet.)  And the
        #     timing difference has nothing to do with moving Python
        #     data to NTL and back.
        #     For large degree ( > 1500) in the one test I tried, NTL was
        #     *much* better than MAGMA, and far better than PARI.  So probably
        #     NTL's implementation is asymptotically better.  I could use
        #     PARI for smaller degree over other rings besides Z, and use
        #     NTL in general.

        R = self.parent().base_ring()
        if self.degree() < 0:
            raise ValueError, "factorization of 0 not defined"
        G = None

        from sage.rings.number_field.all import is_NumberField, is_RelativeNumberField
        from sage.rings.finite_field import is_FiniteField

        n = None
        if sage.rings.integer_mod_ring.is_IntegerModRing(R) or \
              sage.rings.integer_ring.is_IntegerRing(R) or \
              sage.rings.rational_field.is_RationalField(R):

            try:
                G = list(self._pari_with_name('x').factor())
            except PariError:
                raise NotImplementedError

        elif is_RelativeNumberField(R):

            M, from_M, to_M = R.absolute_field()
            g = M['x']([to_M(x) for x in self.list()])
            F = g.factor()
            S = R['x']
            v = [(S([from_M(x) for x in f.list()]), e) for f, e in g.factor()]
            return Factorization(v, from_M(F.unit()))


        elif is_NumberField(R) or is_FiniteField(R):

            v = [x._pari_("a") for x in self.list()]
            f = pari(v).Polrev()
            G = list(f.factor())

        elif is_RealField(R):
            n = pari.set_real_precision(int(3.5*R.prec()) + 1)
            G = list(self._pari_with_name('x').factor())

        elif sage.rings.complex_double.is_ComplexDoubleField(R):
            unit = self.leading_coefficient()
            f = (~unit)*self
            roots = f.roots(multiplicities=False)
            assert len(roots) == self.degree()   # all roots appear with multiplicity...
            x = self.parent().gen()
            v = [(x - a, 1) for a in roots]
            return Factorization(v, unit)

        elif sage.rings.real_double.is_RealDoubleField(R):
            roots = self.change_ring(sage.rings.complex_double.CDF).roots(multiplicities=False)
            assert len(roots) == self.degree()   # all roots appear with multiplicity...
            G = [[],[]]
            real_roots = []
            non_real_roots = []
            for r in roots:
                if r.imag().is_zero():
                    for i in xrange(len(real_roots)):
                        if real_roots[i][0] == r:
                            real_roots[i][1] += 1
                            r = None
                            break
                    if r is not None:
                        real_roots.append([r,1])
                else:
                    for i in xrange(len(non_real_roots)):
                        if non_real_roots[i][0] == r or non_real_roots[i][0] == r.conj():
                            non_real_roots[i][1] += 1
                            r = None
                            break
                    if r is not None:
                        non_real_roots.append([r,1])
            x = self.parent().objgen()[1]
            for r in real_roots:
                G[0].append( x - r[0].real() )
                G[1].append( r[1] )
            for z in non_real_roots:
                a = ( z[0] + z[0].conj() ).real()
                b = ( z[0]*(z[0].conj()) ).real()
                G[0].append( x**2 - a*x + b )
                G[1].append( z[1]/2 )

        elif sage.rings.complex_field.is_ComplexField(R):
            # This is a hack to make the polynomial have complex coefficients, since
            # otherwise PARI will factor over RR.
            n = pari.set_real_precision(int(3.5*R.prec()) + 1)
            if self.leading_coefficient() != R.gen():
                G = list((pari(R.gen())*self._pari_with_name('x')).factor())
            else:
                G = self._pari_with_name('x').factor()

        #elif padic_field.is_pAdicField(R):
        #    G = list(self._pari_with_name('x').factorpadic(R.prime(), R.prec()))

        if G is None:
            raise NotImplementedError

        return self._factor_pari_helper(G, n)

    def _factor_pari_helper(self, G, n=None, unit=None):
        pols = G[0]
        exps = G[1]
        F = []
        R = self.parent()
        c = R.base_ring()(1)
        for i in xrange(len(pols)):
            f = R(pols[i])
            e = int(exps[i])
            if unit is None:
                c *= f.leading_coefficient()
            F.append((f,e))

        if unit is None:

            unit = R.base_ring()(self.leading_coefficient()/c)

        if not unit.is_unit():

            F.append((R(unit), ZZ(1)))
            unit = R.base_ring()(1)

        elif R.base_ring().is_field():
            # When the base ring is a field we normalize
            # the irreducible factors so they have leading
            # coefficient 1.
            one = R.base_ring()(1)
            for i in range(len(F)):
                c = F[i][0].leading_coefficient()
                if c != 1:
                    unit *= c
                    F[i] = (F[i][0].monic(), F[i][1])

        if not n is None:
            pari.set_real_precision(n)  # restore precision
        return Factorization(F, unit)

    def _lcm(self, other):
        """
        Let f and g be two polynomials.  Then this function
        returns the monic least common multiple of f and g.
        """
        f = self*other
        g = self.gcd(other)
        q = f//g
        return ~(q.leading_coefficient())*q  # make monic  (~ is inverse in python)

    def is_constant(self):
        return self.degree() <= 0

    def root_field(self, names, check_irreducible=True):
        """
        Return the field generated by the roots of self.  The output
        is either a number field, relative number field, a quotient of
        a polynomial ring over a field, or the fraction field of the
        base ring.

        EXAMPLES:
            sage: R.<x> = QQ['x']
            sage: f = x^3 + x + 17
            sage: f.root_field('a')
            Number Field in a with defining polynomial x^3 + x + 17

            sage: R.<x> = QQ['x']
            sage: f = x - 3
            sage: f.root_field('b')
            Rational Field

            sage: R.<x> = ZZ['x']
            sage: f = x^3 + x + 17
            sage: f.root_field('b')
            Number Field in b with defining polynomial x^3 + x + 17

            sage: y = QQ['x'].0
            sage: L.<a> = NumberField(y^3-2)
            sage: R.<x> = L['x']
            sage: f = x^3 + x + 17
            sage: f.root_field('c')
            Number Field in c with defining polynomial x^3 + x + 17 over its base field

            sage: R.<x> = PolynomialRing(GF(9,'a'))
            sage: f = x^3 + x^2 + 8
            sage: K.<alpha> = f.root_field(); K
            Univariate Quotient Polynomial Ring in alpha over Finite Field in a of size 3^2 with modulus x^3 + x^2 + 2
            sage: alpha^2 + 1
            alpha^2 + 1
            sage: alpha^3 + alpha^2
            1
        """
        from sage.rings.number_field.number_field import is_NumberField, NumberField

        R = self.base_ring()
        if not is_IntegralDomain(R):
            raise ValueError, "the base ring must be a domain"

        if self.degree() <= 1:
            return R.fraction_field()

        if sage.rings.integer_ring.is_IntegerRing(R):
            return NumberField(self, names)


        if sage.rings.rational_field.is_RationalField(R) or is_NumberField(R):
            return NumberField(self, names)

        if check_irreducible and not self.is_irreducible():
            raise ValueError, "polynomial must be irreducible"

        return polynomial_ring.PolynomialRing(R.fraction_field(),
                              self.parent().variable_name()).quotient(self, names)


    def constant_coefficient(self):
        return self[0]

    def is_monic(self):
        """
        Returns True if this polynomial is monic.  The zero
        polynomial is by definition not monic.

        EXAMPLES:
            sage: x = QQ['x'].0
            sage: f = x + 33
            sage: f.is_monic()
            True
            sage: f = 0*x
            sage: f.is_monic()
            False
            sage: f = 3*x^3 + x^4 + x^2
            sage: f.is_monic()
            True
            sage: f = 2*x^2 + x^3 + 56*x^5
            sage: f.is_monic()
            False

        AUTHORS:
            -- Naqi Jaffery (2006-01-24): examples
        """
        return not self.is_zero() and self[self.degree()] == 1

    def is_unit(self):
        r"""
        Return True if this polynomial is a unit.

        EXAMPLES:
            sage: a = Integers(90384098234^3)
            sage: b = a(2*191*236607587)
            sage: b.is_nilpotent()
            True
            sage: R.<x> = a[]
            sage: f = 3 + b*x + b^2*x^2
            sage: f.is_unit()
            True
            sage: f = 3 + b*x + b^2*x^2 + 17*x^3
            sage: f.is_unit()
            False

        EXERCISE (Atiyah-McDonald, Ch 1): Let $A[x]$ be a polynomial
        ring in one variable.  Then $f=\sum a_i x^i \in A[x]$ is a
        unit if and only if $a_0$ is a unit and $a_1,\ldots, a_n$ are
        nilpotent.
        """
        if self.degree() > 0:
            for i in range(1,self.degree()+1):
                if not self[i].is_nilpotent():
                    return False
        return self[0].is_unit()

    def is_nilpotent(self):
        r"""
        Return True if this polynomial is nilpotent.

        EXAMPLES:
            sage: R = Integers(12)
            sage: S.<x> = R[]
            sage: f = 5 + 6*x
            sage: f.is_nilpotent()
            False
            sage: f = 6 + 6*x^2
            sage: f.is_nilpotent()
            True
            sage: f^2
            0

        EXERCISE (Atiyah-McDonald, Ch 1): Let $A[x]$ be a polynomial
        ring in one variable.  Then $f=\sum a_i x^i \in A[x]$ is
        nilpotent if and only if every $a_i$ is nilpotent.
        """
        for i in range(self.degree()+1):
            if not self[i].is_nilpotent():
                return False
        return True

    def is_gen(self):
        return bool(self._is_gen)

    def leading_coefficient(self):
        return self[self.degree()]

    def monic(self):
        """
        Return this polynomial divided by its leading coefficient.
        Does not change this polynomial.

        EXAMPLES:
            sage: x = QQ['x'].0
            sage: f = 2*x^2 + x^3 + 56*x^5
            sage: f.monic()
            x^5 + 1/56*x^3 + 1/28*x^2
            sage: f = (1/4)*x^2 + 3*x + 1
            sage: f.monic()
            x^2 + 12*x + 4

    The following happens because $f = 0$ cannot be made into a monic polynomial
            sage: f = 0*x
            sage: f.monic()
            Traceback (most recent call last):
            ...
            ZeroDivisionError: rational division by zero

        Notice that the monic version of a polynomial over the
        integers is defined over the rationals.
            sage: x = ZZ['x'].0
            sage: f = 3*x^19 + x^2 - 37
            sage: g = f.monic(); g
            x^19 + 1/3*x^2 - 37/3
            sage: g.parent()
            Univariate Polynomial Ring in x over Rational Field


        AUTHORS:
            -- Naqi Jaffery (2006-01-24): examples
        """
        if self.is_monic():
            return self
        a = ~self.leading_coefficient()
        R = self.parent()
        if a.parent() != R.base_ring():
            S = R.base_extend(a.parent())
            return a*S(self)
        else:
            return a*self


    def list(self):
        """
        Return a new copy of the list of the underlying
        elements of self.
        """
        raise NotImplementedError

    def prec(self):
        """
        Return the precision of this polynomials.  This is
        always infinity, since polynomials are of infinite
        precision by definition (there is no big-oh).

        EXAMPLES:
            sage: x = polygen(ZZ)
            sage: (x^5 + x + 1).prec()
            +Infinity
            sage: x.prec()
            +Infinity
        """
        return infinity

    def padded_list(self, n=None):
        """
        Return list of coefficients of self up to (but not include $q^n$).

        Includes 0's in the list on the right so that the list has
        length $n$.

        INPUT:
            n -- (default: None); if given, an integer that is at least 0

        EXAMPLES:
            sage: x = polygen(QQ)
            sage: f = 1 + x^3 + 23*x^5
            sage: f.padded_list()
            [1, 0, 0, 1, 0, 23]
            sage: f.padded_list(10)
            [1, 0, 0, 1, 0, 23, 0, 0, 0, 0]
            sage: len(f.padded_list(10))
            10
            sage: f.padded_list(3)
            [1, 0, 0]
            sage: f.padded_list(0)
            []
            sage: f.padded_list(-1)
            Traceback (most recent call last):
            ...
            ValueError: n must be at least 0
        """
        v = self.list()
        if n is None:
            return v
        if n < 0:
            raise ValueError, "n must be at least 0"
        if len(v) < n:
            z = self._parent.base_ring()(0)
            return v + [z]*(n - len(v))
        else:
            return v[:int(n)]

    def coeffs(self):
        r"""
        Returns \code{self.list()}.

        (It potentially slightly faster better to use
        \code{self.list()} directly.)

        EXAMPLES:
            sage: x = QQ['x'].0
            sage: f = 10*x^3 + 5*x + 2/17
            sage: f.coeffs()
            [2/17, 5, 0, 10]
        """
        return self.list()

    def newton_raphson(self, n, x0):
        """
        Return a list of n iterative approximations to a root of this
        polynomial, computed using the Newton-Raphson method.

        The Newton-Raphson method is an iterative root-finding algorithm.
        For f(x) a polynomial, as is the case here, this is essentially
        the same as Horner's method.

        INPUT:
           n -- an integer (=the number of iterations),
           x0 -- an initial guess x0.

        OUTPUT:
           A list of numbers hopefully approximating a root of f(x)=0.

           ** If one of the iterates is a critical point of f then
              a ZeroDivisionError exception is raised.

        EXAMPLES:
            sage: x = PolynomialRing(RealField(), 'x').gen()
            sage: f = x^2 - 2
            sage: f.newton_raphson(4, 1)
            [1.50000000000000, 1.41666666666667, 1.41421568627451, 1.41421356237469]

        AUTHORS: David Joyner and William Stein (2005-11-28)
        """
        n = sage.rings.integer.Integer(n)
        df = self.derivative()
        K = self.parent().base_ring()
        a = K(x0)
        L = []
        for i in range(n):
            a -= self(a) / df(a)
            L.append(a)
        return L

    def polynomial(self, *args, **kwds):
        return self._parent(*args, **kwds)

    def newton_slopes(self, p):
        """
        Return the $p$-adic slopes of the Newton polygon of self,
        when this makes sense.

        OUTPUT:
            -- list of rational numbers

        EXAMPLES:
            sage: x = QQ['x'].0
            sage: f = x^3 + 2
            sage: f.newton_slopes(2)
            [1/3, 1/3, 1/3]

        ALGORITHM: Uses PARI.
        """
        f = self._pari_()
        v = list(f.newtonpoly(p))
        return [sage.rings.rational.Rational(x) for x in v]


    #####################################################################
    # Conversions to other systems
    #####################################################################
    def _pari_(self):
        r"""
        Return polynomial as a PARI object.

        SAGE does not handle PARI's variable ordering requirements gracefully
        at this time.  In practice, this means that the variable \code{x}
        needs to be the topmost variable, as in the example.

        EXAMPLES:
            sage: f = QQ['x']([0,1,2/3,3])
            sage: pari(f)
            3*x^3 + 2/3*x^2 + x

            sage: S.<a> = QQ['a']
            sage: R.<x> = S['x']
            sage: f = R([0, a]) + R([0, 0, 2/3])
            sage: pari(f)
            2/3*x^2 + a*x

        TESTS:
            Unfortunately, variable names matter:
                sage: R.<x, y> = QQ[]
                sage: S.<a> = R[]
                sage: f = x^2 + a; g = y^3 + a
                sage: pari(f)
                Traceback (most recent call last):
                ...
                PariError: (8)

            Stacked polynomial rings, first with a univariate ring on the bottom:
                sage: S.<a> = QQ['a']
                sage: R.<x> = S['x']
                sage: pari(x^2 + 2*x)
                x^2 + 2*x
                sage: pari(a*x + 2*x^3)
                2*x^3 + a*x

            Stacked polynomial rings, second with a multivariate ring on the bottom:
                sage: S.<a, b> = ZZ['a', 'b']
                sage: R.<x> = S['x']
                sage: pari(x^2 + 2*x)
                x^2 + 2*x
                sage: pari(a*x + 2*b*x^3)
                2*b*x^3 + a*x

            Stacked polynomial rings with exotic base rings:
                sage: S.<a, b> = GF(7)['a', 'b']
                sage: R.<x> = S['x']
                sage: pari(x^2 + 9*x)
                x^2 + 2*x
                sage: pari(a*x + 9*b*x^3)
                2*b*x^3 + a*x

                sage: S.<a> = Integers(8)['a']
                sage: R.<x> = S['x']
                sage: pari(x^2 + 2*x)
                Mod(1, 8)*x^2 + Mod(2, 8)*x
                sage: pari(a*x + 10*x^3)
                Mod(2, 8)*x^3 + (Mod(1, 8)*a)*x
        """
        return self._pari_with_name(self.parent().variable_name())

    def _pari_with_name(self, name):
        r"""
        Return polynomial as a PARI object with topmost variable \code{name}.

        For internal use only.
        """
        K = self.base_ring()
        oldprec = None
        if is_RealField(K) or sage.rings.complex_field.is_ComplexField(K):
            oldprec = pari.get_real_precision()
            pari.set_real_precision(int(K.prec()*3.5)+1)
        vals = [x._pari_() for x in self.list()]
        temp = pari(vals).Polrev(name)
        if oldprec is not None:
            pari.set_real_precision(oldprec)
        return temp

    def _pari_init_(self):
        return repr(self._pari_())

    def _magma_init_(self):
        """
        Return a string that evaluates in Magma to this polynomial.

        EXAMPLES:
            sage: R.<y> = ZZ[]
            sage: f = y^3 - 17*y + 5
            sage: f._magma_init_()
            'Polynomial(IntegerRing(), [5,-17,0,1])'
        """
        return 'Polynomial(%s, [%s])'%(self.base_ring()._magma_init_(), ','.join([a._magma_init_() for a in self.list()]))

    def _magma_(self, G=None):
        """
        Return the Magma version of this polynomial.

        EXAMPLES:
            sage: R.<y> = ZZ[]
            sage: f = y^3 - 17*y + 5
            sage: g = magma(f); g              # optional -- requires Magma
            y^3 - 17*y + 5

        Note that in Magma there is only one polynomial ring over each base,
        so if we make the polynomial ring over ZZ with variable $z$, then
        this changes the variable name of the polynomial we already defined:
            sage: R.<z> = ZZ[]
            sage: magma(R)                     # optional -- requires Magma
            Univariate Polynomial Ring in z over Integer Ring
            sage: g                            # optional -- requires Magma
            z^3 - 17*z + 5

        In SAGE the variable name does not change:
            sage: f
            y^3 - 17*y + 5
        """
        if G is None:
            import sage.interfaces.magma
            G = sage.interfaces.magma.magma
        self.parent()._magma_(G)  # defines the variable name
        f = G(self._magma_init_())
        return f

    def _gap_init_(self):
        return repr(self)

    def _gap_(self, G):
        """
        EXAMPLES:
            sage: R.<y> = ZZ[]
            sage: f = y^3 - 17*y + 5
            sage: g = gap(f); g
            y^3-17*y+5
            sage: f._gap_init_()
            'y^3 - 17*y + 5'
            sage: R.<z> = ZZ[]
            sage: gap(R)
            PolynomialRing(..., [ z ])
            sage: g
            y^3-17*y+5
            sage: gap(z^2 + z)
            z^2+z

        We coerce a polynomial with coefficients in a finite field:

            sage: R.<y> = GF(7)[]
            sage: f = y^3 - 17*y + 5
            sage: g = gap(f); g
            y^3+Z(7)^4*y+Z(7)^5
            sage: g.Factors()
            [ y+Z(7)^0, y+Z(7)^0, y+Z(7)^5 ]
            sage: f.factor()
            (y + 1)^2 * (y + 5)
        """
        if G is None:
            import sage.interfaces.gap
            G = sage.interfaces.gap.gap
        self.parent()._gap_(G)
        return G(self._gap_init_())

    ######################################################################


    def resultant(self, other):
        r"""
        Returns the resultant of self and other.

        INPUT:
            other -- a polynomial

        OUTPUT:
            an element of the base ring of the polynomial ring

        NOTES:
            Implemented using PARI's \code{polresultant} function.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = x^3 + x + 1;  g = x^3 - x - 1
            sage: r = f.resultant(g); r
            -8
            sage: r.parent() is QQ
            True

        We can also compute resultants over univariate and
        multivariate polynomial rings, providing that PARI's variable
        ordering requirements are respected.  Usually, your resultants
        will work if you always ask for them in the variable \code{x}:

            sage: R.<a> = QQ[]
            sage: S.<x> = R[]
            sage: f = x^2 + a; g = x^3 + a
            sage: r = f.resultant(g); r
            a^3 + a^2
            sage: r.parent() is R
            True

            sage: R.<a, b> = QQ[]
            sage: S.<x> = R[]
            sage: f = x^2 + a; g = x^3 + b
            sage: r = f.resultant(g); r
            a^3 + b^2
            sage: r.parent() is R
            True

        Unfortunately SAGE does not handle PARI's variable ordering requirements
        gracefully, so the following fails:

            sage: R.<x, y> = QQ[]
            sage: S.<a> = R[]
            sage: f = x^2 + a; g = y^3 + a
            sage: f.resultant(g)
            Traceback (most recent call last):
            ...
            PariError: (8)
        """
        other = self.parent()._coerce_(other)
        variable = self.parent().gen()._pari_()
        # The 0 flag tells PARI to use exact arithmetic
        res = self._pari_().polresultant(other._pari_(), variable, 0)
        return self.parent().base_ring()(res)

    def reverse(self):
        v = list(self.list())
        v.reverse()
        return self.parent()(v)

    def roots(self, multiplicities=True):
        """
        Return all roots of this polynomial in the base field of this polynomial.

        INPUT:
            multiplicities -- bool (default: True)
                   if True return list of pairs (r, n), where r is
                   the root and n is the multiplicity.
                   If False, just return the unique roots, with
                   no information about multiplicities.

        If the polynomial is over RR or CC returns all roots in CC
        with multiplicities all set to 1.

        Over all other rings it just returns the roots that lie in the
        base ring.

        EXAMPLES:
            sage: x = QQ['x'].0
            sage: f = x^3 - 1
            sage: f.roots()
            [(1, 1)]
            sage: f = (x^3 - 1)^2
            sage: f.roots()
            [(1, 2)]

            sage: f = -19*x + 884736
            sage: f.roots()
            [(884736/19, 1)]
            sage: (f^20).roots()
            [(884736/19, 20)]

            sage: K.<z> = CyclotomicField(3)
            sage: f = K.defining_polynomial()
            sage: g = f.change_ring(GF(7))
            sage: g.roots()
            [(4, 1), (2, 1)]
            sage: g.roots(multiplicities=False)
            [4, 2]

        An example over RR, which illustrates that only the roots in RR are returned:
            sage: x = RR['x'].0
            sage: f = x^3 -2
            sage: f.roots()
            [(1.25992104989487, 1)]
            sage: f.factor()
            (1.00000000000000*x - 1.25992104989487) * (1.00000000000000*x^2 + 1.25992104989487*x + 1.58740105196820)
            sage: x = RealField(100)['x'].0
            sage: f = x^3 -2
            sage: f.roots()
            [(1.2599210498948731647672106073, 1)]

            sage: x = CC['x'].0
            sage: f = x^3 -2
            sage: f.roots()
            [(1.25992104989487, 1), (-0.629960524947437 + 1.09112363597172*I, 1), (-0.629960524947437 - 1.09112363597172*I, 1)]

        An example involving large numbers:
            sage: x = RR['x'].0
            sage: f = x^2 - 1e100
            sage: f.roots()
            [(-1.00000000000000e50, 1), (1.00000000000000e50, 1)]
            sage: f = x^10 - 2*(5*x-1)^2
            sage: f.roots(multiplicities=False)
            [-1.67726703399418, 0.199954796285057, 0.200045306115242, 1.57630351618444]

            sage: x = CC['x'].0
            sage: i = CC.0
            sage: f = (x - 1)*(x - i)
            sage: f.roots(multiplicities=False)
            [1.00000000000000*I, 1.00000000000000]

        A purely symbolic roots example:
            sage: X = var('X')
            sage: f = expand((X-1)*(X-I)^3*(X^2 - sqrt(2))); f
            X^6 - 3*I*X^5 - X^5 + 3*I*X^4 - sqrt(2)*X^4 - 3*X^4 + 3*sqrt(2)*I*X^3 + I*X^3 + sqrt(2)*X^3 + 3*X^3 - 3*sqrt(2)*I*X^2 - I*X^2 + 3*sqrt(2)*X^2 - sqrt(2)*I*X - 3*sqrt(2)*X + sqrt(2)*I
            sage: print f.roots()
            [(I, 3), (-2^(1/4), 1), (2^(1/4), 1), (1, 1)]

        An example where the base ring doesn't have a factorization algorithm (yet).  Note
        that this is currently done via naive enumeration, so could be very slow:
            sage: R = Integers(6)
            sage: S.<x> = R['x']
            sage: p = x^2-1
            sage: p.roots()
            Traceback (most recent call last):
            ...
            NotImplementedError: root finding with multiplicities for this polynomial not implemented (try the multiplicities=False option)
            sage: p.roots(multiplicities=False)
            [1, 5]

        An example over the complex double field (where root finding
        is fast, thanks to numpy):
            sage: R.<x> = CDF[]
            sage: f = R.cyclotomic_polynomial(5); f
            1.0*x^4 + 1.0*x^3 + 1.0*x^2 + 1.0*x + 1.0
            sage: f.roots(multiplicities=False)   # slightly random
            [0.309016994375 + 0.951056516295*I, 0.309016994375 - 0.951056516295*I, -0.809016994375 + 0.587785252292*I, -0.809016994375 - 0.587785252292*I]
            sage: [z^5 for z in f.roots(multiplicities=False)]     # slightly random
            [1.0 - 2.44929359829e-16*I, 1.0 + 2.44929359829e-16*I, 1.0 - 4.89858719659e-16*I, 1.0 + 4.89858719659e-16*I]
            sage: f = CDF['x']([1,2,3,4]); f
            4.0*x^3 + 3.0*x^2 + 2.0*x + 1.0
            sage: r = f.roots(multiplicities=False)
            sage: [f(a) for a in r]    # slightly random
            [2.55351295664e-15, -4.4408920985e-16 - 2.08166817117e-16*I, -4.4408920985e-16 + 2.08166817117e-16*I]

        Another example over RDF:
            sage: x = RDF['x'].0
            sage: ((x^3 -1)).roots()
            [(1.0, 1)]
            sage: ((x^3 -1)).roots(multiplicities=False)
            [1.0]

        Another examples involving the complex double field:
            sage: x = CDF['x'].0
            sage: i = CDF.0
            sage: f = x^3 + 2*i; f
            1.0*x^3 + 2.0*I
            sage: f.roots()
            [(-1.09112363597 - 0.629960524947*I, 1), (6.66133814775e-16 + 1.25992104989*I, 1), (1.09112363597 - 0.629960524947*I, 1)]
            sage: f.roots(multiplicities=False)
            [-1.09112363597 - 0.629960524947*I, 6.66133814775e-16 + 1.25992104989*I, 1.09112363597 - 0.629960524947*I]
            sage: [f(z) for z in f.roots(multiplicities=False)]
            [-3.10862446895e-15 - 4.4408920985e-16*I, -3.17226455498e-15 + 3.99680288865e-15*I, -5.55111512313e-16 - 8.881784197e-16*I]
            sage: f = i*x^3 + 2; f
            1.0*I*x^3 + 2.0
            sage: f.roots()
            [(-1.09112363597 + 0.629960524947*I, 1), (6.66133814775e-16 - 1.25992104989*I, 1), (1.09112363597 + 0.629960524947*I, 1)]
            sage: f(f.roots()[0][0])
            -4.4408920985e-16 - 3.10862446895e-15*I

        NOTE: This is a note about numerical root finding when the
        input polynomial is double precision:  Multiple roots are a
        very bad case for floating-point root finding.  Unless the
        solver includes special-purpose heuristics to detect multiple
        roots, it's basically impossible to get an "accurate" result;
        if your input is given to  n bits of precision, you should not expect
        more than n/k good bits for a k-fold root.  (As William points out,
        you can get solutions that make the polynomial evaluate to a number
        very close to zero; basically the problem is that with a multiple
        root, there are many such numbers, and it's difficult to choose
        between them.)

        To see why this is true, consider the naive floating-point error
        analysis model where you just pretend that all floating-point numbers
        are somewhat imprecise -- a little "fuzzy", if you will.  Then the
        graph of a floating-point polynomial will be a fuzzy line.  Consider
        the graph of $(x-1)^3$; this will be a fuzzy line with a horizontal
        tangent at $x=1$, $y=0$.  If the fuzziness extends up and down by about j,
        then it will extend left and right by about cube_root(j).

          -- Carl Witty
        """
        seq = []

        K = self.parent().base_ring()

        if is_RealField(K) or sage.rings.complex_field.is_ComplexField(K):
            if is_RealField(K):
                L = K.complex_field()
            else:
                L = K
            n = pari.get_real_precision()
            pari.set_real_precision(int(L.prec()/3.2)+1)
            r = pari(self).polroots()
            if is_RealField(K):
                seq = [K(root.real()) for root in r if root.imag() == 0]
            else:
                seq = [L(root) for root in r]

            pari.set_real_precision(n)

            if multiplicities:
                return [(x, ZZ(1)) for x in seq]
            else:
                return seq

        elif sage.rings.real_double.is_RealDoubleField(K):
            import numpy
            r = numpy.roots(numpy.array(list(reversed(self.list())), dtype='double'))
            RDF = sage.rings.real_double.RDF
            v = [RDF(z) for z in r if z.imag == 0]
            if multiplicities:
                return [(x, ZZ(1)) for x in v]
            else:
                return v

        elif sage.rings.complex_double.is_ComplexDoubleField(K):
            import numpy
            v = [complex(x) for x in reversed(self.list())]
            r = numpy.roots(numpy.array(v, dtype='complex'))
            CDF = sage.rings.complex_double.CDF
            v = [CDF(z) for z in r]
            if multiplicities:
                return [(x, ZZ(1)) for x in v]
            else:
                return v

        try:
            rts = self.factor()
        except NotImplementedError:
            if K.is_finite():
                if multiplicities:
                    raise NotImplementedError, "root finding with multiplicities for this polynomial not implemented (try the multiplicities=False option)"
                else:
                    return [a for a in K if not self(a)]

            raise NotImplementedError, "root finding for this polynomial not implemented"
        for fac in rts:
            g = fac[0]
            if g.degree() == 1:
                if multiplicities:
                    seq.append((-g[0]/g[1],fac[1]))
                else:
                    seq.append(-g[0]/g[1])
        return seq

    def variable_name(self):
        """
        Return name of variable used in this polynomial as a string.

        OUTPUT:
            string

        EXAMPLES:
            sage: R.<t> = QQ[]
            sage: f = t^3 + 3/2*t + 5
            sage: f.variable_name()
            't'
        """
        return self.parent().variable_name()

    def valuation(self, p=None):
        r"""
        If $f = a_r x^r + a_{r+1}x^{r+1} + \cdots$, with $a_r$ nonzero,
        then the valuation of $f$ is $r$.  The valuation of the zero
        polynomial is $\infty$.

        If a prime (or non-prime) $p$ is given, then the valuation is
        the largest power of $p$ which divides self.

        The valuation at $\infty$ is -self.degree().

        EXAMPLES:
        sage: P,x=PolynomialRing(ZZ,'x').objgen()
        sage: (x^2+x).valuation()
        1
        sage: (x^2+x).valuation(x+1)
        1
        sage: (x^2+1).valuation()
        0
        sage: (x^3+1).valuation(infinity)
        -3
        sage: P(0).valuation()
        +Infinity
        """
        cdef int k

        if not self:
            return infinity

        if p is infinity:
            return -self.degree()

        if p is None:
            for k from 0 <= k <= self.degree():
                if self[k]:
                    return ZZ(k)

        if not isinstance(p, Polynomial) or not p.parent() is self.parent():
            raise TypeError, "The polynomial, p, must have the same parent as self."

        if p.degree() == 0:
            raise ArithmeticError, "The polynomial, p, must have positive degree."
        k = 0
        while self % p == 0:
            k = k + 1
            self = self.__floordiv__(p)
        return sage.rings.integer.Integer(k)
        raise RuntimeError, "bug in computing valuation of polynomial"

    def ord(self, p=None):
        """Synonym for valuation

        EXAMPLES:
        sage: P,x=PolynomialRing(ZZ,'x').objgen()
        sage: (x^2+x).ord(x+1)
        1
        """
        return self.valuation(p)

    def name(self):
        return self.parent().variable_name()

    def _xgcd(self, other):
        r"""
        Extended gcd of self and polynomial other.

        Returns g, u, and v such that
              \code{g = u*self + v*other.}

        EXAMPLES:
            sage: P.<x> = QQ[]
            sage: F = (x^2 + 2)*x^3; G = (x^2+2)*(x-3)
            sage: g, u, v = F.xgcd(G)
            sage: g, u, v
            (27*x^2 + 54, 1, -x^2 - 3*x - 9)
            sage: u*F + v*G
            27*x^2 + 54
            sage: x.xgcd(P(0))
            (1, 0, x)
            sage: f = P(0)
            sage: f.xgcd(x)
            (x, 0, 1)
        """
        if other.is_zero():
            R = self.parent()
            return R(1), R(0), self
        # Algorithm 3.2.2 of Cohen, GTM 138
        R = self.parent()
        A = self
        B = other
        U = R(1)
        G = A
        V1 = R(0)
        V3 = B
        while not V3.is_zero():
            Q, R = G.quo_rem(V3)
            T = U - V1*Q
            U = V1
            G = V3
            V1 = T
            V3 = R
        V = (G-A*U)//B
        return G, U, V

    def is_irreducible(self):
        """
        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: (x^3 + 1).is_irreducible()
            False
            sage: (x^2 - 1).is_irreducible()
            False
            sage: (x^3 + 2).is_irreducible()
            True
            sage: R(0).is_irreducible()
            Traceback (most recent call last):
            ...
            ValueError: self must be nonzero

        $4$ is irreducible as a polynomial, since as a polynomial
        it doesn't factor:
            sage: R(4).is_irreducible()
            True
        """
        if self.is_zero():
            raise ValueError, "self must be nonzero"
        if self.degree() == 0:
            return True

        F = self.factor()
        if len(F) > 1 or F[0][1] > 1:
            return False
        return True

    def shift(self, n):
        r"""
        Returns this polynomial multiplied by the power $x^n$. If $n$ is negative,
        terms below $x^n$ will be discarded. Does not change this polynomial (since
        polynomials are immutable).

        EXAMPLES:
            sage: R.<x> = PolynomialRing(PolynomialRing(QQ,'w'),'x')
            sage: p = x^2 + 2*x + 4
            sage: p.shift(0)
             x^2 + 2*x + 4
            sage: p.shift(-1)
             x + 2
            sage: p.shift(-5)
             0
            sage: p.shift(2)
             x^4 + 2*x^3 + 4*x^2

        One can also use the infix shift operator:
            sage: f = x^3 + x
            sage: f >> 2
            x
            sage: f << 2
            x^5 + x^3

        AUTHOR:
            -- David Harvey (2006-08-06)
            -- Robert Bradshaw (2007-04-18) Added support for infix operator.
        """
        if n == 0:
            return self   # safe because immutable.
        if n > 0:
            output = [self.base_ring()(0)] * n
            output.extend(self.coeffs())
            return self.polynomial(output, check=False)
        if n < 0:
            if n > self.degree():
                return self.polynomial([])
            else:
                return self.polynomial(self.coeffs()[-int(n):], check=False)

    def __lshift__(self, k):
        return self.shift(k)

    def __rshift__(self, k):
        return self.shift(-k)

    def truncate(self, long n):
        r"""
        Returns the polynomial of degree $ < n$ which is equivalent to self
        modulo $x^n$.
        """
        return self._parent(self[:n], check=False)

    def is_squarefree(self):
        """
        Return True if this polynomial is square free.

        EXAMPLES:
            sage: x = polygen(QQ)
            sage: f = (x-1)*(x-2)*(x^2-5)*(x^17-3); f
            x^21 - 3*x^20 - 3*x^19 + 15*x^18 - 10*x^17 - 3*x^4 + 9*x^3 + 9*x^2 - 45*x + 30
            sage: f.is_squarefree()
            True
            sage: (f*(x^2-5)).is_squarefree()
            False
        """
        return self.derivative().gcd(self).degree() <= 0

    def radical(self):
        """
        Returns the radical of self; over a field, this is the product of the
        distinct irreducible factors of self. (This is also sometimes called the
        "square-free part" of self, but that term is ambiguous; it is sometimes used
        to mean the quotient of self by its maximal square factor.)

        EXAMPLES:
            sage: P.<x> = ZZ[]
            sage: t = (x^2-x+1)^3 * (3*x-1)^2
            sage: t.radical()
            3*x^3 - 4*x^2 + 4*x - 1
        """
        return self // self.gcd(self.derivative())

    def norm(self, p):
        r"""
        Return the $p$-norm of this polynomial.

        DEFINITION: For integer $p$, the $p$-norm of a polynomial is
        the $p$th root of the sum of the $p$th powers of the absolute
        values of the coefficients of the polynomial.

        INPUT:
           p -- (positive integer or +infinity) the degree of
                the norm

        EXAMPLES:
            sage: R.<x> =RR[]
            sage: f = x^6 + x^2 + -x^4 - 2*x^3
            sage: f.norm(2)
            2.64575131106459
            sage: (sqrt(1^2 + 1^2 + (-1)^2 + (-2)^2)).n()
            2.64575131106459

            sage: f.norm(1)
            5.00000000000000
            sage: f.norm(infinity)
            2.00000000000000

            sage: f.norm(-1)
            Traceback (most recent call last):
            ...
            ValueError: The degree of the norm must be positive

        TESTS:
            sage: R.<x> = RR[]
            sage: f = x^6 + x^2 + -x^4 -x^3
            sage: f.norm(int(2))
            2.00000000000000

        AUTHOR:
            -- didier deshommes
            -- William Stein: fix bugs, add definition, etc.
        """
        if p <= 0 :
            raise ValueError, "The degree of the norm must be positive"

        coeffs = self.coeffs()
        if p == infinity:
            return RR(max([abs(i) for i in coeffs]))

        p = sage.rings.integer.Integer(p)  # because we'll do 1/p below.

        if p == 1:
            return RR(sum([abs(i) for i in coeffs]))

        return RR(sum([abs(i)**p for i in coeffs]))**(1/p)

# ----------------- inner functions -------------
# Sagex can't handle function definitions inside other function


cdef _karatsuba_sum(v,w):
    if len(v)>=len(w):
        x = list(v)
        y = w
    else:
        x = list(w)
        y = v
    for i in range(len(y)):
        x[i] = x[i] + y[i]
    return x

cdef _karatsuba_dif(v,w):
    if len(v)>=len(w):
        x = list(v)
        y = w
    else:
        x = list(w)
        y = v
    for i in range(len(y)):
        x[i] -= y[i]
    return x

cdef do_karatsuba(left, right):
    if len(left) == 0 or len(right) == 0:
        return []
    if len(left) == 1:
        c = left[0]
        return [c*a for a in right]
    if len(right) == 1:
        c = right[0]
        return [c*a for a in left]
    if len(left) == 2 and len(right) == 2:
        b = left[0]
        a = left[1]
        d = right[0]
        c = right[1]
        ac = a*c
        bd = b*d
        return [bd,(a+b)*(c+d)-ac-bd,ac]
    e = min(len(left), len(right))/2
    assert e>=1, "bug in karatsuba"
    a, b = left[e:], left[:e]
    c, d = right[e:], right[:e]
    ac = do_karatsuba(a,c)
    bd = do_karatsuba(b,d)
    zeros = [0] * e
    t2 = zeros + zeros + ac
    t1 = zeros + _karatsuba_dif(do_karatsuba(_karatsuba_sum(a,b),_karatsuba_sum(c,d)),_karatsuba_sum(ac,bd))
    t0 = bd
    return _karatsuba_sum(t0,_karatsuba_sum(t1,t2))

cdef class Polynomial_generic_dense(Polynomial):
    """
    A generic dense polynomial.

    EXAMPLES:
        sage: R.<x> = PolynomialRing(PolynomialRing(QQ,'y'))
        sage: f = x^3 - x + 17
        sage: type(f)
        <type 'sage.rings.polynomial.polynomial_element.Polynomial_generic_dense'>
        sage: loads(f.dumps()) == f
        True
    """
    def __init__(self, parent, x=None, int check=1, is_gen=False, int construct=0, absprec=None):
        Polynomial.__init__(self, parent, is_gen=is_gen)

        if x is None:
            self.__coeffs = []
            return
        R = parent.base_ring()

        if sage.rings.fraction_field_element.is_FractionFieldElement(x):
            if x.denominator() != 1:
                raise TypeError, "denominator must be 1"
            else:
                x = x.numerator()

        if PY_TYPE_CHECK(x, Polynomial):
            if (<Element>x)._parent is self._parent:
                x = list(x.list())
            elif (<Element>x)._parent is R or (<Element>x)._parent == R:
                x = [x]
            elif absprec is None:
                x = [R(a) for a in x.list()]
                check = 0
            else:
                x = [R(a, absprec = absprec) for a in x.list()]
                check = 0

        elif PY_TYPE_CHECK(x, list):
            pass

        elif PY_TYPE_CHECK(x, int) and x == 0:
            self.__coeffs = []
            return

        elif isinstance(x, dict):
            x = self._dict_to_list(x, R(0))

        elif isinstance(x, pari_gen):
            if absprec is None:
                x = [R(w) for w in x.Vecrev()]
            else:
                x = [R(w, absprec = absprec) for w in x.Vecrev()]
            check = 1
        elif not isinstance(x, list):
            x = [x]   # constant polynomials
        if check:
            if absprec is None:
                self.__coeffs = [R(z) for z in x]
            else:
                self.__coeffs = [R(z, absprec=absprec) for z in x]
        else:
            self.__coeffs = x
        if check:
            self.__normalize()


    def __reduce__(self):
        return make_generic_polynomial, (self._parent, self.__coeffs)

    def __nonzero__(self):
        return len(self.__coeffs) > 0

    def __hash__(self):
        if len(self.__coeffs) > 1:
            return hash(tuple(self.__coeffs))
        elif len(self.__coeffs) == 1:
            return hash(self[0])
        else:
            return 0

    cdef void __normalize(self):
        x = self.__coeffs
        cdef Py_ssize_t n = len(x) - 1
        while n >= 0 and x[n].is_zero():
#        while n > 0 and x[n] == 0:
            del x[n]
            n -= 1

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    def __getitem__(self, Py_ssize_t n):
        """
        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: f = (1+2*x)^5; f
            32*x^5 + 80*x^4 + 80*x^3 + 40*x^2 + 10*x + 1
            sage: f[-1]
            0
            sage: f[2]
            40
            sage: f[6]
            0
        """
        if n < 0 or n >= len(self.__coeffs):
            return self.base_ring()(0)
        return self.__coeffs[n]

    def __getslice__(self, Py_ssize_t i, j):
        """
        EXAMPLES:
            sage: R.<x> = RDF[]
            sage: f = (1+2*x)^5; f
            32.0*x^5 + 80.0*x^4 + 80.0*x^3 + 40.0*x^2 + 10.0*x + 1.0
            sage: f[:3]
            40.0*x^2 + 10.0*x + 1.0
            sage: f[2:5]
            80.0*x^4 + 80.0*x^3 + 40.0*x^2
            sage: f[2:]
            32.0*x^5 + 80.0*x^4 + 80.0*x^3 + 40.0*x^2
        """
        if i <= 0:
            i = 0
            zeros = []
        elif i > 0:
            zeros = [self._parent.base_ring()(0)] * i
        return self._parent(zeros + self.__coeffs[i:j])

    def _unsafe_mutate(self, n, value):
        """
        Never use this unless you really know what you are doing.

        WARNING: This could easily introduce subtle bugs, since SAGE
        assumes everywhere that polynomials are immutable.  It's OK to
        use this if you really know what you're doing.

        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: f = (1+2*x)^2; f
            4*x^2 + 4*x + 1
            sage: f._unsafe_mutate(1, -5)
            sage: f
            4*x^2 - 5*x + 1
        """
        n = int(n)
        value = self.base_ring()(value)
        if n >= 0 and n < len(self.__coeffs):
            self.__coeffs[n] = value
            if n == len(self.__coeffs) and value == 0:
                self.__normalize()
        elif n < 0:
            raise IndexError, "polynomial coefficient index must be nonnegative"
        elif value != 0:
            zero = self.base_ring()(0)
            for _ in xrange(len(self.__coeffs), n):
                self.__coeffs.append(zero)
            self.__coeffs.append(value)

    def __floordiv__(self, right):
        """
        Return the quotient upon division (no remainder).

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: f = (1+2*x)^3 + 3*x; f
            8*x^3 + 12*x^2 + 9*x + 1
            sage: g = f // (1+2*x); g
            4*x^2 + 4*x + 5/2
            sage: f - g * (1+2*x)
            -3/2
            sage: f.quo_rem(1+2*x)
            (4*x^2 + 4*x + 5/2, -3/2)
        """
        if right.parent() == self.parent():
            return Polynomial.__floordiv__(self, right)
        d = self.parent().base_ring()(right)
        return self.polynomial([c // d for c in self.__coeffs], check=False)

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        cdef Py_ssize_t check=0, i, min
        x = (<Polynomial_generic_dense>self).__coeffs
        y = (<Polynomial_generic_dense>right).__coeffs
        if len(x) > len(y):
            min = len(y)
            high = x[min:]
        elif len(x) < len(y):
            min = len(x)
            high = y[min:]
        else:
            min = len(x)
        low = [x[i] + y[i] for i from 0 <= i < min]
        if len(x) == len(y):
            res = self._parent(low, check=0)
            (<Polynomial_generic_dense>res).__normalize()
            return res
        else:
            return self._parent(low + high, check=0)

    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        cdef Py_ssize_t check=0, i, min
        x = (<Polynomial_generic_dense>self).__coeffs
        y = (<Polynomial_generic_dense>right).__coeffs
        if len(x) > len(y):
            min = len(y)
            high = x[min:]
        elif len(x) < len(y):
            min = len(x)
            high = [-y[i] for i from min <= i < len(y)]
        else:
            min = len(x)
        low = [x[i] - y[i] for i from 0 <= i < min]
        if len(x) == len(y):
            res = self._parent(low, check=0)
            (<Polynomial_generic_dense>res).__normalize()
            return res
        else:
            return self._parent(low + high, check=0)

    cdef ModuleElement _rmul_c_impl(self, RingElement c):
        if len(self.__coeffs) == 0:
            return self
        if c._parent is not (<Element>self.__coeffs[0])._parent:
            c = (<Element>self.__coeffs[0])._parent._coerce_c(c)
        v = [c * a for a in self.__coeffs]
        res = self._parent(v, check=0)
        if not v[len(v)-1]:
            (<Polynomial_generic_dense>res).__normalize()
        return res

    cdef ModuleElement _lmul_c_impl(self, RingElement c):
        if len(self.__coeffs) == 0:
            return self
        if c._parent is not (<Element>self.__coeffs[0])._parent:
            c = (<Element>self.__coeffs[0])._parent._coerce_c(c)
        v = [a * c for a in self.__coeffs]
        res = self._parent(v, check=0)
        if not v[len(v)-1]:
            (<Polynomial_generic_dense>res).__normalize()
        return res

    def list(self, copy=True):
        """
        Return a new copy of the list of the underlying
        elements of self.

        EXAMPLES:
            sage: R.<x> = GF(17)[]
            sage: f = (1+2*x)^3 + 3*x; f
            8*x^3 + 12*x^2 + 9*x + 1
            sage: f.list()
            [1, 9, 12, 8]
        """
        if copy:
            return list(self.__coeffs)
        else:
            return self.__coeffs

    def degree(self):
        """
        EXAMPLES:
            sage: R.<x> = RDF[]
            sage: f = (1+2*x^7)^5
            sage: f.degree()
            35
        """
        return len(self.__coeffs) - 1

    def shift(self, Py_ssize_t n):
        r"""
        Returns this polynomial multiplied by the power $x^n$. If $n$
        is negative, terms below $x^n$ will be discarded. Does not
        change this polynomial.

        EXAMPLES:
            sage: R.<x> = PolynomialRing(PolynomialRing(QQ,'y'), 'x')
            sage: p = x^2 + 2*x + 4
            sage: type(p)
            <type 'sage.rings.polynomial.polynomial_element.Polynomial_generic_dense'>
            sage: p.shift(0)
             x^2 + 2*x + 4
            sage: p.shift(-1)
             x + 2
            sage: p.shift(2)
             x^4 + 2*x^3 + 4*x^2

        AUTHOR:
            -- David Harvey (2006-08-06)
        """
        if n == 0:
            return self
        if n > 0:
            output = [self.base_ring()(0)] * n
            output.extend(self.__coeffs)
            return self.polynomial(output, check=False)
        if n < 0:
            if n > len(self.__coeffs) - 1:
                return self.polynomial([])
            else:
                return self.polynomial(self.__coeffs[-int(n):], check=False)

    def truncate(self, long n):
        r"""
        Returns the polynomial of degree $ < n$ which is equivalent to self
        modulo $x^n$.
        """
        return self._parent(self.__coeffs[:n], check=False)



def make_generic_polynomial(parent, coeffs):
    return parent(coeffs)
