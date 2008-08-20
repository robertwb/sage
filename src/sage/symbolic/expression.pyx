include "../ext/interrupt.pxi"
include "../ext/stdsage.pxi"
include "../ext/cdefs.pxi"

import ring

from sage.structure.element cimport ModuleElement, RingElement, Element


from sage.rings.rational import Rational  # Used for sqrt.

cdef class Expression(CommutativeRingElement):
    def __dealloc__(self):
        GEx_destruct(&self._gobj)

    def _repr_(self):
        """
            sage: var("x y", ns=1)
            (x, y)
            sage: x+y
            x+y
        """
        return GEx_to_str(&self._gobj)

    def __hash__(self):
        """
            sage: var("x y", ns=1)
            (x, y)
            sage: hash(x+y)
            46142460
            sage: d = {x+y: 5}
            sage: d
            {x+y: 5}
        """
        return self._gobj.gethash()

    def __richcmp__(left, right, int op):
        cdef Expression l = left
        cdef Expression r = right
        cdef GEx e
        _sig_on
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
        _sig_off
        return new_Expression_from_GEx(e)

    def __nonzero__(self):
        # TODO: Problem -- if self is a symbolic equality then
        # this is_zero isn't the right thing at all:
        #  sage: bool(x == x+1)
        #  True  # BAD
        # Solution is to probably look something up in ginac manual.
        _sig_on
        cdef bint x = not self._gobj.is_zero()
        _sig_off
        return x

    cdef ModuleElement _add_c_impl(left, ModuleElement right):
        """
            sage.: var("x y", ns=1)
            (x, y)
            sage.: x+y+y+x
            2*x+2*y
        """
        _sig_on
        cdef GEx e = gadd(left._gobj, (<Expression>right)._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    cdef ModuleElement _sub_c_impl(left, ModuleElement right):
        """
            sage.: var("x y", ns=1)
            (x, y)
            sage.: x - x
            x-y
        """
        _sig_on
        cdef GEx e = gsub(left._gobj, (<Expression>right)._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    cdef RingElement _mul_c_impl(left, RingElement right):
        """
            sage: var("x y", ns=1)
            (x, y)
            sage: x*y*y
            x*y^2
        """
        _sig_on
        cdef GEx e = gmul(left._gobj, (<Expression>right)._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    cdef RingElement _div_c_impl(left, RingElement right):
        """
            sage: var("x y", ns=1)
            (x, y)
            sage: x/y/y
            x*y^(-2)
        """
        _sig_on
        cdef GEx e = gdiv(left._gobj, (<Expression>right)._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    cdef int _cmp_c_impl(left, Element right) except -2:
        return left._gobj.compare((<Expression>right)._gobj)

    def _add_benchmark(self):
        gadd(self._gobj, self._gobj)

    def __pow__(Expression self, exp, ignored):
        cdef Expression nexp = self._parent._coerce_c(exp)
        _sig_on
        cdef GEx e = g_pow(self._gobj, nexp._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def expand(Expression self):
        _sig_on
        cdef GEx e = self._gobj.expand(0)
        _sig_off
        return new_Expression_from_GEx(e)

    def collect(Expression self, Expression s):
        #TODO convert second argument if necessary
        _sig_on
        cdef GEx e = self._gobj.collect(s._gobj, False)
        _sig_off
        return new_Expression_from_GEx(e)

    def abs(self):
        _sig_on
        cdef GEx e = g_abs(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def step(self):
        _sig_on
        cdef GEx e = g_step(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def csgn(self):
        _sig_on
        cdef GEx e = g_csgn(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def conjugate(self):
        _sig_on
        cdef GEx e = g_conjugate(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def real_part(self):
        _sig_on
        cdef GEx e = g_real_part(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def imag_part(self):
        _sig_on
        cdef GEx e = g_imag_part(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def sqrt(self):
        # do not use sqrt(...) since it doesn't seem to work
        # and there is a remark in decl.pxi about it just being
        # some broken alias.
        return self**Rational((1,2))

    def sin(self):
        _sig_on
        cdef GEx e = g_sin(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def cos(self):
        _sig_on
        cdef GEx e = g_cos(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def tan(self):
        _sig_on
        cdef GEx e = g_tan(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def arcsin(self):
        _sig_on
        cdef GEx e = g_asin(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def arccos(self):
        _sig_on
        cdef GEx e = g_acos(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def arctan(self):
        _sig_on
        cdef GEx e = g_atan(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def arctan2(self, Expression x):
        _sig_on
        cdef GEx e = g_atan2(self._gobj, x._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def sinh(self):
        _sig_on
        cdef GEx e = g_sinh(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def cosh(self):
        _sig_on
        cdef GEx e = g_cosh(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def tanh(self):
        _sig_on
        cdef GEx e = g_tanh(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def arcsinh(self):
        _sig_on
        cdef GEx e = g_asinh(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def arccosh(self):
        _sig_on
        cdef GEx e = g_acosh(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def arctanh(self):
        _sig_on
        cdef GEx e = g_atanh(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def exp(self):
        _sig_on
        cdef GEx e = g_exp(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def log(self):
        _sig_on
        cdef GEx e = g_log(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def Li2(self):
        _sig_on
        cdef GEx e = g_Li2(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def Li(self, Expression x):
        _sig_on
        cdef GEx e = g_Li(self._gobj, x._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def G(self, Expression y):
        _sig_on
        cdef GEx e = g_G(self._gobj, y._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def G2(self, Expression s, Expression y):
        _sig_on
        cdef GEx e = g_G2(self._gobj, s._gobj, y._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def S(self, Expression p, Expression x):
        _sig_on
        cdef GEx e = g_S(self._gobj, p._gobj, x._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def H(self, Expression x):
        _sig_on
        cdef GEx e = g_H(self._gobj, x._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def zeta(self):
        _sig_on
        cdef GEx e = g_zeta(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def zeta2(self, Expression s):
        _sig_on
        cdef GEx e = g_zeta2(self._gobj, s._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def zetaderiv(self, Expression x):
        _sig_on
        cdef GEx e = g_zetaderiv(self._gobj, x._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def tgamma(self):
        _sig_on
        cdef GEx e = g_tgamma(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def lgamma(self):
        _sig_on
        cdef GEx e = g_lgamma(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def beta(self, Expression y):
        _sig_on
        cdef GEx e = g_beta(self._gobj, y._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def psi(self):
        _sig_on
        cdef GEx e = g_psi(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def psi2(self, Expression x):
        _sig_on
        cdef GEx e = g_psi2(self._gobj, x._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def factorial(self):
        _sig_on
        cdef GEx e = g_factorial(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def binomial(self, Expression k):
        _sig_on
        cdef GEx e = g_binomial(self._gobj, k._gobj)
        _sig_off
        return new_Expression_from_GEx(e)

    def Order(self):
        _sig_on
        cdef GEx e = g_Order(self._gobj)
        _sig_off
        return new_Expression_from_GEx(e)



cdef Expression new_Expression_from_GEx(GEx juice):
    cdef Expression nex
    nex = <Expression>PY_NEW(Expression)
    GEx_construct_ex(&nex._gobj, juice)
    nex._parent = ring.NSR
    return nex
