r"""
Elements of Laurent polynomial rings
"""
include "../../ext/stdsage.pxi"

import re
from sage.rings.integer import Integer
from sage.structure.element import is_Element
from sage.misc.latex import latex
from sage.misc.misc import union
from sage.structure.factorization import Factorization


cdef class LaurentPolynomial_mpair(CommutativeAlgebraElement):
    def __init__(self, parent, x, reduce=True):
        """
        Currently, one can only create LaurentPolynomials out of dictionaries
        and elements of the base ring.

        EXAMPLES::

            sage: L.<w,z> = LaurentPolynomialRing(QQ)
            sage: f = L({(-1,-1):1}); f
            w^-1*z^-1
            sage: f = L({(1,1):1}); f
            w*z
            sage: f =  L({(-1,-1):1, (1,3):4}); f
            4*w*z^3 + w^-1*z^-1
            sage: L(1/2)
            1/2
        """
        if isinstance(x, PolyDict):
            x = x.dict()
        if isinstance(x, dict):
            self._mon = ETuple({},int(parent.ngens()))
            for k in x.keys(): # ETuple-ize keys, set _mon
                if not isinstance(k, (tuple, ETuple)) or len(k) != parent.ngens():
                    self._mon = ETuple({}, int(parent.ngens()))
                    break
                if isinstance(k, tuple):
                    a = x[k]
                    del x[k]
                    k = ETuple(k)
                    x[k] = a
                self._mon = self._mon.emin(k) # point-wise min of _mon and k
            if len(self._mon.nonzero_positions()) != 0: # factor out _mon
                D = {}
                for k in x.keys():
                    D[k.esub(self._mon)] = x[k]
                x = D
        else: # since x should coerce into parent, _mon should be (0,...,0)
            self._mon = ETuple({}, int(parent.ngens()))
        self._poly = parent.polynomial_ring()(x)
        CommutativeAlgebraElement.__init__(self, parent)

    cdef _new_c(self):
        """
        Returns a new Laurent polynomial

        EXAMPLES::

            sage: L.<x,y> = LaurentPolynomialRing(QQ) # indirect doctest
            sage: x*y
            x*y
        """
        cdef LaurentPolynomial_mpair ans
        ans = PY_NEW(LaurentPolynomial_mpair)
        ans._parent = self._parent
        return ans

    def _normalize(self, i = None):
        """
        Removes the common monomials from self._poly and stores them in self._mon

        INPUT:

        - ``i`` -- an integer

        EXAMPLES::

            sage: L.<x,y> = LaurentPolynomialRing(QQ)
            sage: f = x*y + 2*y*x^2 + y
            sage: f.factor() #Notice the y has been factored out.
            (y) * (2*x^2 + x + 1)

        """
        D = self._poly._mpoly_dict_recursive(self.parent().variable_names(), self.parent().base_ring())
        if i is None:
            e = None
            for k in D.keys():
                if e is None:
                    e = k
                else:
                    e = e.emin(k)
            if len(e.nonzero_positions()) > 0:
                self._poly = self._poly / self._poly.parent()({e: 1})
                self._mon = self._mon.eadd(e)
        else:
            e = None
            for k in D.keys():
                if e is None or k[i] < e:
                    e = k[i]
            if e > 0:
                self._poly = self._poly / self._poly.parent().gen(i)
                self._mon = self._mon.eadd_p(e, i)


    def _dict(self):
        """
        EXAMPLES::

            sage: L.<w,z> = LaurentPolynomialRing(QQ)
            sage: a = w^2*z^-1+3; a
            w^2*z^-1 + 3
            sage: d = a._dict()
            sage: keys = list(sorted(d.keys())); keys
            [(0, 0), (2, -1)]
            sage: d[keys[0]]
            3
            sage: d[keys[1]]
            1

        """
        D = self._poly._mpoly_dict_recursive(self.parent().variable_names(), self.parent().base_ring())
        if len(self._mon.nonzero_positions()) > 0:
            DD = {}
            for k in D.keys():
                DD[k.eadd(self._mon)] = D[k]
            return DD
        else:
            return D

    def _compute_polydict(self):
        """
        EXAMPLES::

            sage: L.<w,z> = LaurentPolynomialRing(QQ)
            sage: a = w^2*z^-1+3
            sage: a._compute_polydict()
        """
        self._prod = PolyDict(self._dict(), force_etuples = False)

    def __repr__(self):
        """
        EXAMPLES::

            sage: L.<x,y> = LaurentPolynomialRing(QQ)
            sage: f = x^2 + x*y/2 + 2*y^-1
            sage: f.__repr__()
            'x^2 + 1/2*x*y + 2*y^-1'
        """
        if self._prod is None:
            self._compute_polydict()
        try:
            cmpfn = self.parent().term_order().compare_tuples
        except AttributeError:
            cmpfn = None
        return self._prod.poly_repr(self.parent().variable_names(), atomic_coefficients = self.parent().base_ring().is_atomic_repr(), cmpfn = cmpfn)

    def _latex_(self):
        """
        EXAMPLES::

            sage: L.<w,z> = LaurentPolynomialRing(QQ)
            sage: a = w^2*z^-1+3; a
            w^2*z^-1 + 3
            sage: latex(a)
            w^{2}z^{-1} + 3

        """
        if self._prod is None:
            self._compute_polydict()
        try:
            cmpfn = self.parent().term_order().compare_tuples
        except AttributeError:
            cmpfn = None
        return self._prod.latex(self.parent().variable_names(), atomic_coefficients = self.parent().base_ring().is_atomic_repr(), cmpfn = cmpfn)

    def __pow__(LaurentPolynomial_mpair self, n, m):
        """
        EXAMPLES::

            sage: L.<x,y> = LaurentPolynomialRing(QQ)
            sage: f = x + y
            sage: f^2
            x^2 + 2*x*y + y^2
            sage: f^(-1)
            1/(x + y)
        """
        cdef LaurentPolynomial_mpair ans
        if n < 0:
            E = self._poly.exponents()
            if len(E) == 0:
                raise ZeroDivisionError
            elif len(E) > 1:
                return self.parent()._R.fraction_field()(self)**n
            else:
                ans = self._new_c()
                ans._poly = self._poly.parent().change_ring(self.parent().base_ring().fraction_field())(self._poly.coefficients()[0]**n)
                ans._mon = self._mon.eadd(E[0]).emul(n)
        else:
            ans = self._new_c()
            ans._poly = self._poly**n
            ans._mon = self._mon.emul(n)
        return ans

    def coefficient(self, mon):
        """
        Return the coefficient of mon in self, where mon must have the
        same parent as self.  The coefficient is defined as follows.
        If f is this polynomial, then the coefficient is the sum T/mon
        where the sum is over terms T in f that are exactly divisible
        by mon.

        A monomial m(x,y) 'exactly divides' f(x,y) if m(x,y)|f(x,y)
        and neither x*m(x,y) nor y*m(x,y) divides f(x,y).

        INPUT:

        - ``mon`` -- a monomial

        OUTPUT:

        element of the parent of self

        EXAMPLES::

            sage: P.<x,y> = LaurentPolynomialRing(QQ)

        The coefficient returned is an element of the parent of self; in
        this case, P.

        ::

            sage: f = 2 * x * y
            sage: c = f.coefficient(x*y); c
            2
            sage: c.parent()
            Multivariate Laurent Polynomial Ring in x, y over Rational Field

            sage: P.<x,y> = LaurentPolynomialRing(QQ)
            sage: f = (y^2 - x^9 - 7*x*y^2 + 5*x*y)*x^-3; f
            -x^6 - 7*x^-2*y^2 + 5*x^-2*y + x^-3*y^2
            sage: f.coefficient(y)
            5*x^-2
            sage: f.coefficient(y^2)
            -7*x^-2 + x^-3
            sage: f.coefficient(x*y)
            0
            sage: f.coefficient(x^-2)
            -7*y^2 + 5*y
            sage: f.coefficient(x^-2*y^2)
            -7
            sage: f.coefficient(1)
            -x^6 - 7*x^-2*y^2 + 5*x^-2*y + x^-3*y^2
        """
        if mon.parent() is not self.parent():
            mon = self.parent()(mon)
        if self._prod is None:
            self._compute_polydict()
        if (<LaurentPolynomial_mpair>mon)._prod is None:
            mon._compute_polydict()
        return self.parent()(self._prod.coefficient((<LaurentPolynomial_mpair>mon).dict()))

    def coefficients(self):
        """
        Return the nonzero coefficients of this polynomial in a list.
        The returned list is decreasingly ordered by the term ordering
        of ``self.parent()``.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ,order='degrevlex')
            sage: f = 4*x^7*z^-1 + 3*x^3*y + 2*x^4*z^-2 + x^6*y^-7
            sage: f.coefficients()
            [4, 3, 2, 1]
            sage: L.<x,y,z> = LaurentPolynomialRing(QQ,order='lex')
            sage: f = 4*x^7*z^-1 + 3*x^3*y + 2*x^4*z^-2 + x^6*y^-7
            sage: f.coefficients()
            [4, 1, 2, 3]
        """
        return self._poly.coefficients()

    def variables(self, sort=True):
        """
        Return a list of all variables occurring in self.

        INPUT:

        - ``sort`` -- specifies whether the indices shall be sorted

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = 4*x^7*z^-1 + 3*x^3*y + 2*x^4*z^-2 + x^6*y^-7
            sage: f.variables()
            [z, y, x]
            sage: f.variables(sort=False) #random
            [y, z, x]
        """
        d = self.dict();
        g = self.parent().gens()
        nvars = len(g)
        vars = []
        for k in d.keys():
            vars = union(vars,k.nonzero_positions())
            if len(vars) == nvars:
                break
        v = [ g[i] for i in vars]
        if sort:
            v.sort()
        return v

    def dict(self):
        """
        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = 4*x^7*z^-1 + 3*x^3*y + 2*x^4*z^-2 + x^6*y^-7
            sage: list(sorted(f.dict().iteritems()))
            [((3, 1, 0), 3), ((4, 0, -2), 2), ((6, -7, 0), 1), ((7, 0, -1), 4)]
        """
        if self._prod is None:
            self._compute_polydict()
        return self._prod.dict()

    cpdef ModuleElement _add_(self, ModuleElement _right):
        """
        Returns the Laurent polynomial self + right.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + y^-1
            sage: g = y + z
            sage: f + g
            x + y + z + y^-1
        """
        cdef LaurentPolynomial_mpair ans = self._new_c()
        cdef LaurentPolynomial_mpair right = <LaurentPolynomial_mpair>_right
        ans._mon, a, b = self._mon.combine_to_positives(right._mon)
        if len(a.nonzero_positions()) > 0:
            ans._poly = self._poly * self._poly.parent()({a: 1})
        else:
            ans._poly = self._poly
        if len(b.nonzero_positions()) > 0:
            ans._poly += right._poly * self._poly.parent()({b: 1})
        else:
            ans._poly += right._poly
        return ans

    cpdef ModuleElement _sub_(self, ModuleElement _right):
        """
        Returns the Laurent polynomial self - right.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + y^-1
            sage: g = y + z + x
            sage: f - g
            -y - z + y^-1

        """
        cdef LaurentPolynomial_mpair ans = self._new_c()
        cdef LaurentPolynomial_mpair right = <LaurentPolynomial_mpair>_right
        cdef ETuple a, b
        ans._mon, a, b = self._mon.combine_to_positives(right._mon)
        if len(a.nonzero_positions()) > 0:
            ans._poly = self._poly * self._poly.parent()({a: 1})
        else:
            ans._poly = self._poly
        if len(b.nonzero_positions()) > 0:
            ans._poly -= right._poly * self._poly.parent()({b: 1})
        else:
            ans._poly -= right._poly
        return ans

    cpdef ModuleElement _neg_(self):
        """
        Returns -self.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + y^-1
            sage: -f
            -x - y^-1

        """
        cdef LaurentPolynomial_mpair ans = self._new_c()
        ans._mon = self._mon
        ans._poly = -self._poly
        return ans

    cpdef ModuleElement _lmul_(self, RingElement right):
        """
        Returns self * right where right is in self's base ring.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + y^-1
            sage: f*(1/2)
            1/2*x + 1/2*y^-1

        """
        cdef LaurentPolynomial_mpair ans = self._new_c()
        ans._mon = self._mon
        ans._poly = self._poly * right
        return ans

    cpdef ModuleElement _rmul_(self, RingElement left):
        """
        Returns left*self where left is in self's base ring.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + y^-1
            sage: (1/2)*f
            1/2*x + 1/2*y^-1

        """
        cdef LaurentPolynomial_mpair ans = self._new_c()
        ans._mon = self._mon
        ans._poly = left * self._poly
        return ans

    cpdef RingElement _mul_(self, RingElement right):
        """
        Return self*right.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + y^-1
            sage: g = y + z
            sage: f*g
            x*y + x*z + 1 + y^-1*z
        """
        cdef LaurentPolynomial_mpair ans = self._new_c()
        ans._mon = self._mon.eadd((<LaurentPolynomial_mpair>right)._mon)
        ans._poly = self._poly * (<LaurentPolynomial_mpair>right)._poly
        return ans

    cdef int _cmp_c_impl(self, Element right) except -2:
        """
        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + y^-1
            sage: g = y + z
            sage: f == f
            True
            sage: f == g
            False
            sage: f == 2
            False
        """
        if self._prod is None:
            self._compute_polydict()
        if (<LaurentPolynomial_mpair>right)._prod is None:
            right._compute_polydict()
        return cmp(self._prod, (<LaurentPolynomial_mpair>right)._prod)

    def exponents(self):
        """
        Returns a list of the exponents of self.

        EXAMPLES::

            sage: L.<w,z> = LaurentPolynomialRing(QQ)
            sage: a = w^2*z^-1+3; a
            w^2*z^-1 + 3
            sage: e = a.exponents()
            sage: e.sort(); e
            [(0, 0), (2, -1)]

        """
        return [a.eadd(self._mon) for a in self._poly.exponents()]

    def degree(self,x=None):
        """
        Returns the degree of x in self

        EXAMPLES::

            sage: R.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = 4*x^7*z^-1 + 3*x^3*y + 2*x^4*z^-2 + x^6*y^-7
            sage: f.degree(x)
            7
            sage: f.degree(y)
            1
            sage: f.degree(z)
            0
        """

        if not x:
            return self._poly.total_degree() + sum(self._mon)

        g = self.parent().gens()
        no_generator_found = True
        for i in range(len(g)):
            if g[i] is x:
                no_generator_found = False
                break
        if no_generator_found:
            raise TypeError, "x must be a generator of parent"
        return self._poly.degree(self.parent().polynomial_ring().gens()[i]) + self._mon[i]



    def has_inverse_of(self, i):
        """
        INPUT:

        - ``i`` -- The index of a generator of ``self.parent()``

        OUTPUT:

        Returns True if self contains a monomial including the inverse of
        ``self.parent().gen(i)``, False otherwise.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = 4*x^7*z^-1 + 3*x^3*y + 2*x^4*z^-2 + x^6*y^-7
            sage: f.has_inverse_of(0)
            False
            sage: f.has_inverse_of(1)
            True
            sage: f.has_inverse_of(2)
            True
        """
        if (not isinstance(i, (int, Integer))) or (i < 0) or (i >= self.parent().ngens()):
            raise TypeError, "argument is not the index of a generator"
        if self._mon[i] < 0:
            self._normalize(i)
            if self._mon[i] < 0:
                return True
            return False
        return False

    def has_any_inverse(self):
        """
        Returns True if self contains any monomials with a negative exponent, False otherwise.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = 4*x^7*z^-1 + 3*x^3*y + 2*x^4*z^-2 + x^6*y^-7
            sage: f.has_any_inverse()
            True
            sage: g = x^2 + y^2
            sage: g.has_any_inverse()
            False
        """
        for m in self._mon.nonzero_values(sort = False):
            if m < 0:
                return True
        return False

    def __call__(self, *x, **kwds):
        """

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + 2*y + 3*z
            sage: f(1,1,1)
            6
            sage: f = x^-1 + y + z
            sage: f(0,1,1)
            Traceback (most recent call last):
            ...
            ZeroDivisionError

        TESTS::

            sage: f = x + 2*y + 3*z
            sage: f(2)
            Traceback (most recent call last):
            ...
            TypeError: number of arguments does not match the number of generators in parent.
            sage: f(2,0)
            Traceback (most recent call last):
            ...
            TypeError: number of arguments does not match the number of generators in parent.
            sage: f( (1,1,1) )
            6
        """
        n = self.parent().ngens()

        if len(kwds) > 0:
            f = self.subs(**kwds)
            if len(x) > 0:
                return f(*x)
            else:
                return f

        cdef int l = len(x)

        if l == 1 and (PY_TYPE_CHECK(x[0], tuple) or PY_TYPE_CHECK(x[0], list)):
            x = x[0]
            l = len(x)

        if l != n:
            raise TypeError, "number of arguments does not match the number of generators in parent."

        #Check to make sure that we aren't dividing by zero
        for m in range(n):
            if x[m] == 0:
                if self.has_inverse_of(m):
                    raise ZeroDivisionError

        ans = self._poly(*x)
        if ans != 0:
            for m in self._mon.nonzero_positions():
                ans *= x[m]**self._mon[m]

        return ans

    def subs(self, in_dict=None, **kwds):
        """
        Note that this is a very unsophisticated implementation.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = x + 2*y + 3*z
            sage: f.subs(x=1)
            2*y + 3*z + 1
            sage: f.subs(y=1)
            x + 3*z + 2
            sage: f.subs(z=1)
            x + 2*y + 3
            sage: f.subs(x=1,y=1,z=1)
            6

            sage: f = x^-1
            sage: f.subs(x=2)
            1/2
            sage: f.subs({x:2})
            1/2

            sage: f = x + 2*y + 3*z
            sage: f.subs({x:1,y:1,z:1})
            6
            sage: f.substitute(x=1,y=1,z=1)
            6

        TESTS::

            sage: f = x + 2*y + 3*z
            sage: f(q=10)
            x + 2*y + 3*z

        """
        if in_dict is not None and kwds:
            raise ValueError, "you cannot specify both a dictionary and keyword arguments"

        g = self.parent().gens()
        repr_g = [repr(i) for i in g]
        vars = []

        if in_dict is None:
            for i in range(len(g)):
                if repr_g[i] in kwds:
                    vars.append(i)
        else:
            kwds = {}
            for i in range(len(g)):
                if g[i] in in_dict:
                    kwds[ repr(g[i]) ] = in_dict[ g[i] ]
                    vars.append(i)

        d = self._dict()
        out = 0
        for mon in d.keys():
            term = d[mon]
            for i in range(len(mon)):
                if i in vars:
                    term *= kwds[repr_g[i]]**mon[i]
                else:
                    term *= g[i]**mon[i]
            out += term

        return out


    def factor(self):
        """
        Returns a Laurent monomial (the unit part of the factorization) and a factored multi-polynomial.

        EXAMPLES::

            sage: L.<x,y,z> = LaurentPolynomialRing(QQ)
            sage: f = 4*x^7*z^-1 + 3*x^3*y + 2*x^4*z^-2 + x^6*y^-7
            sage: f.factor()
            (x^3*y^-7*z^-2) * (4*x^4*y^7*z + 3*y^8*z^2 + 2*x*y^7 + x^3*z^2)
        """
        pf = self._poly.factor()
        u = self.parent(pf.unit().dict()) # self.parent won't currently take polynomials

        g = self.parent().gens()
        for i in self._mon.nonzero_positions():
            u *= g[i]**self._mon[i]

        f = []
        for t in pf:
            d = t[0].dict()
            if len(d) == 1:  # monomials are units
                u *= self.parent(d)**t[1]
            else:
                f.append( (self.parent(d),t[1]) )

        return Factorization(f, unit=u)
