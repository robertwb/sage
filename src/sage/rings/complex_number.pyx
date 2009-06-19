"""
Arbitrary Precision Complex Numbers

AUTHORS:

- William Stein (2006-01-26): complete rewrite

- Joel B. Mohler (2006-12-16): naive rewrite into pyrex

- William Stein(2007-01): rewrite of Mohler's rewrite
"""

#################################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import math
import operator

from sage.structure.element cimport FieldElement, RingElement, Element, ModuleElement
from sage.categories.map cimport Map

from complex_double cimport ComplexDoubleElement
from real_mpfr cimport RealNumber

import complex_field
import sage.misc.misc
import integer
import infinity

from sage.libs.mpmath.utils cimport mpfr_to_mpfval

include "../ext/stdsage.pxi"

cdef mp_rnd_t rnd
rnd = GMP_RNDN

def set_global_complex_round_mode(n):
    global rnd
    rnd = n

#from sage.databases.odlyzko import zeta_zeroes

def is_ComplexNumber(x):
    r"""
    Returns True if x is a complex number. In particular, if x is of
    the ``ComplexNumber`` type.

    EXAMPLES::

        sage: from sage.rings.complex_number import is_ComplexNumber
        sage: a = ComplexNumber(1,2); a
        1.00000000000000 + 2.00000000000000*I
        sage: is_ComplexNumber(a)
        True
        sage: b = ComplexNumber(1); b
        1.00000000000000
        sage: is_ComplexNumber(b)
        True

    Note that the global element I is of type
    ``SymbolicConstant``. However, elements of the class
    ``ComplexField_class`` are of type
    ``ComplexNumber``::

        sage: c = 1 + 2*I
        sage: is_ComplexNumber(c)
        False
        sage: d = CC(1 + 2*I)
        sage: is_ComplexNumber(d)
        True
    """
    return isinstance(x, ComplexNumber)

cdef class ComplexNumber(sage.structure.element.FieldElement):
    """
    A floating point approximation to a complex number using any
    specified precision. Answers derived from calculations with such
    approximations may differ from what they would be if those
    calculations were performed with true complex numbers. This is due
    to the rounding errors inherent to finite precision calculations.

    EXAMPLES::

        sage: I = CC.0
        sage: b = 1.5 + 2.5*I
        sage: loads(b.dumps()) == b
        True
    """

    cdef ComplexNumber _new(self):
        """
        Quickly creates a new initialized complex number with the same
        parent as self.
        """
        cdef ComplexNumber x
        x = PY_NEW(ComplexNumber)
        x._parent = self._parent
        x._prec = self._prec
        x._multiplicative_order = None
        mpfr_init2(x.__re, self._prec)
        mpfr_init2(x.__im, self._prec)
        return x

    def __init__(self, parent, real, imag=None):
        r"""
        Initialize ``ComplexNumber`` instance.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: a.__init__(CC,2,1)
            sage: a
            2.00000000000000 + 1.00000000000000*I
            sage: parent(a)
            Complex Field with 53 bits of precision
            sage: real(a)
            2.00000000000000
            sage: imag(a)
            1.00000000000000
        """
        cdef real_mpfr.RealNumber rr, ii
        self._parent = parent
        self._prec = self._parent._prec
        self._multiplicative_order = None

        mpfr_init2(self.__re, self._prec)
        mpfr_init2(self.__im, self._prec)

        if imag is None:
            if real is None: return

            if PY_TYPE_CHECK(real, ComplexNumber):
                real, imag = (<ComplexNumber>real).real(), (<ComplexNumber>real).imag()
            elif isinstance(real, sage.libs.pari.all.pari_gen):
                real, imag = real.real(), real.imag()
            elif isinstance(real, list) or isinstance(real, tuple):
                re, imag = real
                real = re
            elif isinstance(real, complex):
                real, imag = real.real, real.imag
            else:
                imag = 0
        try:
            R = parent._real_field()
            rr = R(real)
            ii = R(imag)
            mpfr_set(self.__re, <mpfr_t> rr.value, rnd)
            mpfr_set(self.__im, <mpfr_t> ii.value, rnd)
        except TypeError:
            raise TypeError, "unable to coerce to a ComplexNumber: %s" % type(real)


    def  __dealloc__(self):
        mpfr_clear(self.__re)
        mpfr_clear(self.__im)

    def _interface_init_(self, I=None):
        """
        Returns self formatted as a string, suitable as input to another
        computer algebra system. (This is the default function used for
        exporting to other computer algebra systems.)

        EXAMPLES::

            sage: s1 = CC(exp(I)); s1
            0.540302305868140 + 0.841470984807897*I
            sage: s1._interface_init_()
            '0.54030230586813977 + 0.84147098480789650*I'
            sage: s1 == CC(gp(s1))
            True
        """
        return self.str(truncate=False)

    def _sage_input_(self, sib, coerced):
        r"""
        Produce an expression which will reproduce this value when evaluated.

        EXAMPLES:
            sage: for prec in (2, 53, 200):
            ...       fld = ComplexField(prec)
            ...       var = polygen(fld)
            ...       ins = [-20, 0, 1, -2^4000, 2^-4000] + [fld._real_field().random_element() for _ in range(3)]
            ...       for v1 in ins:
            ...           for v2 in ins:
            ...               v = fld(v1, v2)
            ...               _ = sage_input(fld(v), verify=True)
            ...               _ = sage_input(fld(v) * var, verify=True)
            sage: x = polygen(CC)
            sage: for v1 in [-2, 0, 2]:
            ...       for v2 in [-2, -1, 0, 1, 2]:
            ...           print str(sage_input(x + CC(v1, v2))).splitlines()[1]
            x + CC(-2 - 2*I)
            x + CC(-2 - I)
            x - 2
            x + CC(-2 + I)
            x + CC(-2 + 2*I)
            x - CC(2*I)
            x - CC(I)
            x
            x + CC(I)
            x + CC(2*I)
            x + CC(2 - 2*I)
            x + CC(2 - I)
            x + 2
            x + CC(2 + I)
            x + CC(2 + 2*I)
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: sib_np = SageInputBuilder(preparse=False)
            sage: CC(-infinity)._sage_input_(sib, True)
            {unop:- {call: {atomic:RR}({atomic:Infinity})}}
            sage: CC(0, infinity)._sage_input_(sib, True)
            {call: {atomic:CC}({call: {atomic:RR}({atomic:0})}, {call: {atomic:RR}({atomic:Infinity})})}
            sage: CC(NaN, 5)._sage_input_(sib, True)
            {call: {atomic:CC}({call: {atomic:RR}({atomic:NaN})}, {call: {atomic:RR}({atomic:5})})}
            sage: CC(5, NaN)._sage_input_(sib, True)
            {call: {atomic:CC}({call: {atomic:RR}({atomic:5})}, {call: {atomic:RR}({atomic:NaN})})}
            sage: CC(12345)._sage_input_(sib, True)
            {atomic:12345}
            sage: CC(-12345)._sage_input_(sib, False)
            {unop:- {call: {atomic:CC}({atomic:12345})}}
            sage: CC(0, 12345)._sage_input_(sib, True)
            {call: {atomic:CC}({binop:* {atomic:12345} {atomic:I}})}
            sage: CC(0, -12345)._sage_input_(sib, False)
            {unop:- {call: {atomic:CC}({binop:* {atomic:12345} {atomic:I}})}}
            sage: CC(1.579)._sage_input_(sib, True)
            {atomic:1.579}
            sage: CC(1.579)._sage_input_(sib_np, True)
            {atomic:1.579}
            sage: ComplexField(150).zeta(37)._sage_input_(sib, True)
            {call: {call: {atomic:ComplexField}({atomic:150})}({binop:+ {atomic:0.98561591034770846226477029397621845736859851519} {binop:* {atomic:0.16900082032184907409303555538443060626072476297} {atomic:I}}})}
            sage: ComplexField(150).zeta(37)._sage_input_(sib_np, True)
            {call: {call: {atomic:ComplexField}({atomic:150})}({binop:+ {call: {call: {atomic:RealField}({atomic:150})}({atomic:'0.98561591034770846226477029397621845736859851519'})} {binop:* {call: {call: {atomic:RealField}({atomic:150})}({atomic:'0.16900082032184907409303555538443060626072476297'})} {atomic:I}}})}
        """
        if coerced and self.imag() == 0:
            return sib(self.real(), True)

        # The body will be coerced first to symbolics and then to CC.
        # This works fine if we produce integer or float literals, but
        # not for infinity or NaN.
        if not (mpfr_number_p(self.__re) and mpfr_number_p(self.__im)):
            return sib(self.parent())(self.real(), self.imag())

        # The following uses of .sum() and .prod() will simplify
        # 3+0*I to 3, 0+1*I to I, etc.
        real_part = sib(self.real(), 2)
        imag_part = sib.prod([sib(self.imag(), 2), sib.name('I')],
                             simplify=True)
        sum = sib.sum([real_part, imag_part], simplify=True)
        if sum._sie_is_negation():
            return -sib(self.parent())(sum._sie_operand)
        else:
            return sib(self.parent())(sum)

        # The following is an (untested) implementation that produces
        # CC_I = CC.gen()
        # 2 + 3*CC_I
        # instead of CC(2 + 3*I)
#         cdef int prec

#         if self.real().is_zero() and self.imag() == 1:
#             v = sib(self.parent()).gen()
#             prec = self.prec()
#             if prec == 53:
#                 gen_name = 'CC_I'
#             else:
#                 gen_name = 'CC%d_I' % prec
#             sib.cache(self, v, gen_name)

#         real_part = sib(self.real())
#         imag_part = sib.prod([self.imag(), self.parent().gen()], simplify=True)
#         return sib.sum([real_part, imag_part], simplify=True)

    def _repr_(self):
        r"""
        Returns self formatted as a string.

        EXAMPLES::

            sage: a = ComplexNumber(2,1); a
            2.00000000000000 + 1.00000000000000*I
            sage: a._repr_()
            '2.00000000000000 + 1.00000000000000*I'
        """
        return self.str(10)

    def __hash__(self):
        """
        Returns the hash of self, which coincides with the python complex
        and float (and often int) types.

        This has the drawback that two very close high precision numbers
        will have the same hash, but allows them to play nicely with other
        real types.

        EXAMPLE::

            sage: hash(CC(1.2, 33)) == hash(complex(1.2, 33))
            True
        """
        return hash(complex(self))

    def __getitem__(self, i):
        r"""
        Returns either the real or imaginary component of self depending on
        the choice of i: real (i=0), imaginary (i=1)

        INPUTS:

        - ``i`` - 0 or 1

          - ``0`` - will return the real component of self

          - ``1`` - will return the imaginary component of self

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: a.__getitem__(0)
            2.00000000000000
            sage: a.__getitem__(1)
            1.00000000000000

        ::

            sage: b = CC(42,0)
            sage: b
            42.0000000000000
            sage: b.__getitem__(1)
            0.000000000000000
        """
        if i == 0:
            return self.real()
        elif i == 1:
            return self.imag()
        raise IndexError, "i must be between 0 and 1."

    def __reduce__( self ):
        """
        Pickling support

        EXAMPLES::

            sage: a = CC(1 + I)
            sage: loads(dumps(a)) == a
            True
        """
        # TODO: This is potentially slow -- make a 1 version that
        # is native and much faster -- doesn't use .real()/.imag()
        return (make_ComplexNumber0, (self._parent, self._multiplicative_order, self.real(), self.imag()))

    def _set_multiplicative_order(self, n):
        r"""
        Function for setting the ``ComplexNumber`` class
        attribute ``multiplicative_order`` of self.

        INPUTS: n - an integer which will define the multiplicative order
        of self

        EXAMPLES: Note that it is not advised to explicity call
        ``_set_multiplicative_order`` for explicity declared
        complex numbers.

        ::

            sage: a = ComplexNumber(2,1)
            sage: a.multiplicative_order()
            +Infinity
            sage: a._set_multiplicative_order(5)
            sage: a.multiplicative_order()
            5
            sage: a^5
            -38.0000000000000 + 41.0000000000000*I
        """
        self._multiplicative_order = integer.Integer(n)

    def str(self, base=10, truncate=True):
        r"""
        Return a string representation of this number.

        INPUTS:

        - ``base`` - The base to use for printing (default 10)

        - ``truncate`` - (default: ``True``) Whether to print fewer
          digits than are available, to mask errors in the last bits.

        EXAMPLES::

            sage: a = CC(pi + I*e)
            sage: a.str()
            '3.14159265358979 + 2.71828182845905*I'
            sage: a.str(truncate=False)
            '3.1415926535897931 + 2.7182818284590451*I'
            sage: a.str(base=2)
            '11.001001000011111101101010100010001000010110100011000 + 10.101101111110000101010001011000101000101011101101001*I'
            sage: CC(0.5 + 0.625*I).str(base=2)
            '0.10000000000000000000000000000000000000000000000000000 + 0.10100000000000000000000000000000000000000000000000000*I'
            sage: a.str(base=16)
            '3.243f6a8885a30 + 2.b7e151628aed2*I'
            sage: a.str(base=36)
            '3.53i5ab8p5fc + 2.puw5nggjf8f*I'
        """

        s = ""
        if self.real() != 0:
            s = self.real().str(base, truncate=truncate)
        if self.imag() != 0:
            y  =  self.imag()
            if s!="":
                if y < 0:
                    s = s+" - "
                    y = -y
                else:
                    s = s+" + "
            s = s+"%s*I"%y.str(base, truncate=truncate)
        if len(s) == 0:
            s = "0"
        return s

    def _latex_(self):
        r"""
        Method for converting self to a string with latex formatting.
        Called by the global function ``latex``.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: a
            2.00000000000000 + 1.00000000000000*I
            sage: latex(a)
            2.00000000000000 + 1.00000000000000i
            sage: a._latex_()
            '2.00000000000000 + 1.00000000000000i'

        ::

            sage: b = ComplexNumber(7,4,min_prec=16)
            sage: b
            7.000 + 4.000*I
            sage: latex(b)
            7.000 + 4.000i
            sage: b._latex_()
            '7.000 + 4.000i'
        """
        import re
        s = self.str().replace('*I', 'i')
        return re.sub(r"e(-?\d+)", r" \\times 10^{\1}", s)

    def _pari_(self):
        r"""
        Coerces self into a Pari ``complex`` object.

        EXAMPLES: Coerce the object using the ``pari``
        function::

            sage: a = ComplexNumber(2,1)
            sage: pari(a)
            2.00000000000000 + 1.00000000000000*I
            sage: type(pari(a))
            <type 'sage.libs.pari.gen.gen'>
            sage: a._pari_()
            2.00000000000000 + 1.00000000000000*I
            sage: type(a._pari_())
            <type 'sage.libs.pari.gen.gen'>
        """
        return sage.libs.pari.all.pari.complex(self.real()._pari_(), self.imag()._pari_())

    def _mpmath_(self, prec=None, rounding=None):
        """
        Returns an mpmath version of this ComplexNumber.

        .. note::

           Currently, the rounding mode is ignored.

        EXAMPLES::

            sage: CC(1,2)._mpmath_()
            mpc(real='1.0', imag='2.0')
        """
        if prec is not None:
            return self.n(prec=prec)._mpmath_()
        from sage.libs.mpmath.all import make_mpc
        re = mpfr_to_mpfval(self.__re)
        im = mpfr_to_mpfval(self.__im)
        return make_mpc((re, im))

    cpdef ModuleElement _add_(self, ModuleElement right):
        cdef ComplexNumber x
        x = self._new()
        mpfr_add(x.__re, self.__re, (<ComplexNumber>right).__re, rnd)
        mpfr_add(x.__im, self.__im, (<ComplexNumber>right).__im, rnd)
        return x

    cpdef ModuleElement _sub_(self, ModuleElement right):
        cdef ComplexNumber x
        x = self._new()
        mpfr_sub(x.__re, self.__re, (<ComplexNumber>right).__re, rnd)
        mpfr_sub(x.__im, self.__im, (<ComplexNumber>right).__im, rnd)
        return x

    cpdef RingElement _mul_(self, RingElement right):
        cdef ComplexNumber x
        x = self._new()
        cdef mpfr_t t0, t1
        mpfr_init2(t0, self._prec)
        mpfr_init2(t1, self._prec)
        mpfr_mul(t0, self.__re, (<ComplexNumber>right).__re, rnd)
        mpfr_mul(t1, self.__im, (<ComplexNumber>right).__im, rnd)
        mpfr_sub(x.__re, t0, t1, rnd)
        mpfr_mul(t0, self.__re, (<ComplexNumber>right).__im, rnd)
        mpfr_mul(t1, self.__im, (<ComplexNumber>right).__re, rnd)
        mpfr_add(x.__im, t0, t1, rnd)
        mpfr_clear(t0)
        mpfr_clear(t1)
        return x

    def norm(self):
        r"""
        Returns the norm of self.

        `norm(a + bi) = a^2 + b^2`

        EXAMPLES: This indeed acts as the square function when the
        imaginary component of self is equal to zero::

            sage: a = ComplexNumber(2,1)
            sage: a.norm()
            5.00000000000000
            sage: b = ComplexNumber(4.2,0)
            sage: b.norm()
            17.6400000000000
            sage: b^2
            17.6400000000000
        """
        return self.norm_c()

    cdef real_mpfr.RealNumber norm_c(ComplexNumber self):
        cdef real_mpfr.RealNumber x
        x = real_mpfr.RealNumber(self._parent._real_field(), None)

        cdef mpfr_t t0, t1
        mpfr_init2(t0, self._prec)
        mpfr_init2(t1, self._prec)

        mpfr_mul(t0, self.__re, self.__re, rnd)
        mpfr_mul(t1, self.__im, self.__im, rnd)

        mpfr_add(<mpfr_t> x.value, t0, t1, rnd)

        mpfr_clear(t0)
        mpfr_clear(t1)
        return x

    cdef real_mpfr.RealNumber abs_c(ComplexNumber self):
        cdef real_mpfr.RealNumber x
        x = real_mpfr.RealNumber(self._parent._real_field(), None)

        cdef mpfr_t t0, t1
        mpfr_init2(t0, self._prec)
        mpfr_init2(t1, self._prec)

        mpfr_mul(t0, self.__re, self.__re, rnd)
        mpfr_mul(t1, self.__im, self.__im, rnd)

        mpfr_add(<mpfr_t> x.value, t0, t1, rnd)
        mpfr_sqrt(<mpfr_t> x.value, <mpfr_t> x.value, rnd)

        mpfr_clear(t0)
        mpfr_clear(t1)
        return x

    cpdef RingElement _div_(self, RingElement right):
        cdef ComplexNumber x
        x = self._new()
        cdef mpfr_t a, b, t0, t1, right_nm
        mpfr_init2(t0, self._prec)
        mpfr_init2(t1, self._prec)
        mpfr_init2(a, self._prec)
        mpfr_init2(b, self._prec)
        mpfr_init2(right_nm, self._prec)

        mpfr_mul(t0, (<ComplexNumber>right).__re, (<ComplexNumber>right).__re, rnd)
        mpfr_mul(t1, (<ComplexNumber>right).__im, (<ComplexNumber>right).__im, rnd)
        mpfr_add(right_nm, t0, t1, rnd)

        mpfr_div(a, (<ComplexNumber>right).__re, right_nm, rnd)
        mpfr_div(b, (<ComplexNumber>right).__im, right_nm, rnd)

        ## Do this: x.__re =  a * self.__re + b * self.__im
        mpfr_mul(t0, a, self.__re, rnd)
        mpfr_mul(t1, b, self.__im, rnd)
        mpfr_add(x.__re, t0, t1, rnd)

        ## Do this: x.__im =  a * self.__im - b * self.__re
        mpfr_mul(t0, a, self.__im, rnd)
        mpfr_mul(t1, b, self.__re, rnd)
        mpfr_sub(x.__im, t0, t1, rnd)
        mpfr_clear(t0)
        mpfr_clear(t1)
        mpfr_clear(a)
        mpfr_clear(b)
        mpfr_clear(right_nm)
        return x

    def __rdiv__(self, left):
        r"""
        Returns the quotient of left with self, that is:

        left/self

        as a complex number.

        INPUTS:

        - ``left`` - a complex number to divide by self

        EXAMPLES::

            sage: a = ComplexNumber(2,0)
            sage: a.__rdiv__(CC(1))
            0.500000000000000
            sage: CC(1)/a
            0.500000000000000
        """
        return ComplexNumber(self._parent, left)/self

    def __pow__(self, right, modulus):
        """
        EXAMPLES::

            sage: C.<i> = ComplexField(20)
            sage: a = i^2; a
            -1.0000
            sage: a.parent()
            Complex Field with 20 bits of precision
            sage: a = (1+i)^i; a
            0.42883 + 0.15487*I
            sage: (1+i)^(1+i)
            0.27396 + 0.58370*I
            sage: a.parent()
            Complex Field with 20 bits of precision
            sage: i^i
            0.20788
            sage: (2+i)^(0.5)
            1.4553 + 0.34356*I
        """
        if isinstance(right, (int, long, integer.Integer)):
            return sage.rings.ring_element.RingElement.__pow__(self, right)

        try:
            return (self.log()*right).exp()
        except TypeError:
            pass

        try:
            self = right.parent()(self)
            return self**right
        except AttributeError:
            raise TypeError

    def _magma_init_(self, magma):
        r"""
        EXAMPLES::

            sage: magma(CC([1, 2])) # optional - magma
            1.00000000000000 + 2.00000000000000*$.1
            sage: v = magma(CC([1, 2])).sage(); v # optional - magma
            1.00000000000000 + 2.00000000000000*I
            sage: v.parent() # optional - magma
            Complex Field with 53 bits of precision
        """
        return "%s![%s, %s]" % (self.parent()._magma_init_(magma), self.real(), self.imag())

    def __nonzero__(self):
        """
        Return True if self is not zero. This is an internal function; use
        self.is_zero() instead.

        EXAMPLES::

            sage: z = 1 + CC(I)
            sage: z.is_zero()
            False
        """
        return not (mpfr_zero_p(self.__re) and mpfr_zero_p(self.__im))

    def prec(self):
        """
        Return precision of this complex number.

        EXAMPLES::

            sage: i = ComplexField(2000).0
            sage: i.prec()
            2000
        """
        return self._parent.prec()

    def real(self):
        """
        Return real part of self.

        EXAMPLES::

            sage: i = ComplexField(100).0
            sage: z = 2 + 3*i
            sage: x = z.real(); x
            2.0000000000000000000000000000
            sage: x.parent()
            Real Field with 100 bits of precision
        """
        cdef real_mpfr.RealNumber x
        x = real_mpfr.RealNumber(self._parent._real_field(), None)
        mpfr_set(<mpfr_t> x.value, self.__re, rnd)
        return x

    def imag(self):
        """
        Return imaginary part of self.

        EXAMPLES::

            sage: i = ComplexField(100).0
            sage: z = 2 + 3*i
            sage: x = z.imag(); x
            3.0000000000000000000000000000
            sage: x.parent()
            Real Field with 100 bits of precision
        """
        cdef real_mpfr.RealNumber x
        x = real_mpfr.RealNumber(self._parent._real_field(), None)
        mpfr_set(<mpfr_t> x.value, self.__im, rnd)
        return x

    def __neg__(self):
        r"""
        Method for computing the negative of self.

        -(a + bi) = -a - bi

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: -a
            -2.00000000000000 - 1.00000000000000*I
            sage: a.__neg__()
            -2.00000000000000 - 1.00000000000000*I
        """
        cdef ComplexNumber x
        x = self._new()
        mpfr_neg(x.__re, self.__re, rnd)
        mpfr_neg(x.__im, self.__im, rnd)
        return x

    def __pos__(self):
        r"""
        Method for computing the "positive" of self.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: +a
            2.00000000000000 + 1.00000000000000*I
            sage: a.__pos__()
            2.00000000000000 + 1.00000000000000*I
        """
        return self

    def __abs__(self):
        r"""
        Method for computing the absolute value or modulus of self

        `|a + bi| = sqrt(a^2 + b^2)`

        EXAMPLES: Note that the absolute value of a complex number with
        imaginary component equal to zero is the absolute value of the real
        component.

        ::

            sage: a = ComplexNumber(2,1)
            sage: abs(a)
            2.23606797749979
            sage: a.__abs__()
            2.23606797749979
            sage: float(sqrt(2^2 + 1^1))
            2.2360679774997898

        ::

            sage: b = ComplexNumber(42,0)
            sage: abs(b)
            42.0000000000000
            sage: b.__abs__()
            42.0000000000000
            sage: b
            42.0000000000000
        """
        return self.abs_c()

    def __invert__(self):
        """
        Return the multiplicative inverse.

        EXAMPLES::

            sage: I = CC.0
            sage: a = ~(5+I)
            sage: a * (5+I)
            1.00000000000000
        """
        cdef ComplexNumber x
        x = self._new()

        cdef mpfr_t t0, t1
        mpfr_init2(t0, self._prec)
        mpfr_init2(t1, self._prec)

        mpfr_mul(t0, self.__re, self.__re, rnd)
        mpfr_mul(t1, self.__im, self.__im, rnd)

        mpfr_add(t0, t0, t1, rnd)         # now t0 is the norm
        mpfr_div(x.__re, self.__re, t0, rnd)   #     x.__re = self.__re/norm

        mpfr_neg(t1, self.__im, rnd)
        mpfr_div(x.__im, t1, t0, rnd)  #     x.__im = -self.__im/norm

        mpfr_clear(t0)
        mpfr_clear(t1)

        return x

    def __int__(self):
        r"""
        Method for converting self to type int. Called by the
        ``int`` function. Note that calling this method returns
        an error since, in general, complex numbers cannot be coerced into
        integers.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: int(a)
            Traceback (most recent call last):
            ...
            TypeError: can't convert complex to int; use int(abs(z))
            sage: a.__int__()
            Traceback (most recent call last):
            ...
            TypeError: can't convert complex to int; use int(abs(z))
        """
        raise TypeError, "can't convert complex to int; use int(abs(z))"

    def __long__(self):
        r"""
        Method for converting self to type long. Called by the
        ``long`` function. Note that calling this method
        returns an error since, in general, complex numbers cannot be
        coerced into integers.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: long(a)
            Traceback (most recent call last):
            ...
            TypeError: can't convert complex to long; use long(abs(z))
            sage: a.__long__()
            Traceback (most recent call last):
            ...
            TypeError: can't convert complex to long; use long(abs(z))
        """
        raise TypeError, "can't convert complex to long; use long(abs(z))"

    def __float__(self):
        r"""
        Method for converting self to type float. Called by the
        ``float`` function. Note that calling this method
        returns an error since, in general, complex numbers cannot be
        coerced into floats.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: float(a)
            Traceback (most recent call last):
            ...
            TypeError: can't convert complex to float; use abs(z)
            sage: a.__float__()
            Traceback (most recent call last):
            ...
            TypeError: can't convert complex to float; use abs(z)
        """
        raise TypeError, "can't convert complex to float; use abs(z)"

    def __complex__(self):
        r"""
        Method for converting self to type complex. Called by the
        ``complex`` function.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: complex(a)
            (2+1j)
            sage: type(complex(a))
            <type 'complex'>
            sage: a.__complex__()
            (2+1j)
        """
        return complex(mpfr_get_d(self.__re, rnd),
                       mpfr_get_d(self.__im, rnd))
        # return complex(float(self.__re), float(self.__im))

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    cdef int _cmp_c_impl(left, sage.structure.element.Element right) except -2:
        cdef int a, b
        a = mpfr_nan_p(left.__re)
        b = mpfr_nan_p((<ComplexNumber>right).__re)
        if a != b:
            return -1

        cdef int i
        i = mpfr_cmp(left.__re, (<ComplexNumber>right).__re)
        if i < 0:
            return -1
        elif i > 0:
            return 1
        i = mpfr_cmp(left.__im, (<ComplexNumber>right).__im)
        if i < 0:
            return -1
        elif i > 0:
            return 1
        return 0

    def multiplicative_order(self):
        """
        Return the multiplicative order of this complex number, if known,
        or raise a NotImplementedError.

        EXAMPLES::

            sage: C.<i> = ComplexField()
            sage: i.multiplicative_order()
            4
            sage: C(1).multiplicative_order()
            1
            sage: C(-1).multiplicative_order()
            2
            sage: C(i^2).multiplicative_order()
            2
            sage: C(-i).multiplicative_order()
            4
            sage: C(2).multiplicative_order()
            +Infinity
            sage: w = (1+sqrt(-3.0))/2; w
            0.500000000000000 + 0.866025403784439*I
            sage: abs(w)
            1.00000000000000
            sage: w.multiplicative_order()
            Traceback (most recent call last):
            ...
            NotImplementedError: order of element not known
        """
        if self == 1:
            return integer.Integer(1)
        elif self == -1:
            return integer.Integer(2)
        elif self == self._parent.gen():
            return integer.Integer(4)
        elif self == -self._parent.gen():
            return integer.Integer(4)
        elif not self._multiplicative_order is None:
            return integer.Integer(self._multiplicative_order)
        elif abs(abs(self) - 1) > 0.1:  # clearly not a root of unity
            return infinity.infinity
        raise NotImplementedError, "order of element not known"


    ########################################################################
    # Transcendental (and other) functions
    ########################################################################


    # Trig functions
    def arccos(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).arccos()
            0.904556894302381 - 1.06127506190504*I
        """
        return self._parent(self._pari_().acos())

    def arccosh(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).arccosh()
            1.06127506190504 + 0.904556894302381*I
        """
        return self._parent(self._pari_().acosh())

    def arcsin(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).arcsin()
            0.666239432492515 + 1.06127506190504*I
        """
        return self._parent(self._pari_().asin())

    def arcsinh(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).arcsinh()
            1.06127506190504 + 0.666239432492515*I
        """
        return self._parent(self._pari_().asinh())

    def arctan(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).arctan()
            1.01722196789785 + 0.402359478108525*I
        """
        return self._parent(self._pari_().atan())

    def arctanh(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).arctanh()
            0.402359478108525 + 1.01722196789785*I
        """
        return self._parent(self._pari_().atanh())

    def coth(self):
        """
        EXAMPLES::

            sage: ComplexField(100)(1,1).coth()
            0.86801414289592494863584920892 - 0.21762156185440268136513424361*I
        """
        return ~(self.tanh())

    def arccoth(self):
        """
        EXAMPLES::

            sage: ComplexField(100)(1,1).arccoth()
            0.40235947810852509365018983331 - 0.55357435889704525150853273009*I
        """
        return (~self).arctanh()

    def csc(self):
        """
        EXAMPLES::

            sage: ComplexField(100)(1,1).csc()
            0.62151801717042842123490780586 - 0.30393100162842645033448560451*I
        """
        return ~(self.sin())

    def csch(self):
        """
        EXAMPLES::

            sage: ComplexField(100)(1,1).csch()
            0.30393100162842645033448560451 - 0.62151801717042842123490780586*I
        """
        return ~(self.sinh())

    def arccsch(self):
        """
        EXAMPLES::

            sage: ComplexField(100)(1,1).arccsch()
            0.53063753095251782601650945811 - 0.45227844715119068206365839783*I
        """
        return (~self).arcsinh()

    def sec(self):
        """
        EXAMPLES::

            sage: ComplexField(100)(1,1).sec()
            0.49833703055518678521380589177 + 0.59108384172104504805039169297*I
        """
        return ~(self.cos())

    def sech(self):
        """
        EXAMPLES::

            sage: ComplexField(100)(1,1).sech()
            0.49833703055518678521380589177 - 0.59108384172104504805039169297*I
        """
        return ~(self.cosh())

    def arcsech(self):
        """
        EXAMPLES::

            sage: ComplexField(100)(1,1).arcsech()
            -0.53063753095251782601650945811 + 1.1185178796437059371676632938*I
        """
        return (~self).arccosh()

    def cotan(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).cotan()
            0.217621561854403 - 0.868014142895925*I
            sage: i = ComplexField(200).0
            sage: (1+i).cotan()
            0.21762156185440268136513424360523807352075436916785404091068 - 0.86801414289592494863584920891627388827343874994609327121115*I
            sage: i = ComplexField(220).0
            sage: (1+i).cotan()
            0.21762156185440268136513424360523807352075436916785404091068124239 - 0.86801414289592494863584920891627388827343874994609327121115071646*I
        """
        return ~(self.tan())

    def cos(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).cos()
            0.833730025131149 - 0.988897705762865*I
        """
        # write self = a + i*b, then
        # cos(self) = cosh(b)*cos(a) - i*sinh(b)*sin(a)
        cdef ComplexNumber z
        z = self._new()
        cdef mpfr_t ch, sh
        mpfr_init2(sh, self._prec)
        mpfr_sinh(sh, self.__im, rnd)
        mpfr_init2(ch, self._prec)
        mpfr_sqr(ch, sh, rnd)
        mpfr_add_ui(ch, ch, 1, rnd)
        mpfr_sqrt(ch, ch, rnd)
        mpfr_neg(sh, sh, rnd)
        mpfr_sin_cos(z.__im, z.__re, self.__re, rnd)
        mpfr_mul(z.__re, z.__re, ch, rnd)
        mpfr_mul(z.__im, z.__im, sh, rnd)
        mpfr_clear(sh)
        mpfr_clear(ch)
        return z

    def cosh(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).cosh()
            0.833730025131149 + 0.988897705762865*I
        """
        # write self = a + i*b, then
        # cosh(self) = cosh(a)*cos(b) + i*sinh(a)*sin(b)
        cdef ComplexNumber z
        z = self._new()
        cdef mpfr_t ch, sh
        mpfr_init2(sh, self._prec)
        mpfr_sinh(sh, self.__re, rnd)
        mpfr_init2(ch, self._prec)
        mpfr_sqr(ch, sh, rnd)
        mpfr_add_ui(ch, ch, 1, rnd)
        mpfr_sqrt(ch, ch, rnd)
        mpfr_sin_cos(z.__im, z.__re, self.__im, rnd)
        mpfr_mul(z.__re, z.__re, ch, rnd)
        mpfr_mul(z.__im, z.__im, sh, rnd)
        mpfr_clear(sh)
        mpfr_clear(ch)
        return z



    def eta(self, omit_frac=False):
        r"""
        Return the value of the Dedekind `\eta` function on self,
        intelligently computed using `\mathbb{SL}(2,\ZZ)`
        transformations.

        INPUT:

        -  ``self`` - element of the upper half plane (if not,
           raises a ValueError).

        -  ``omit_frac`` - (bool, default: False), if True,
           omit the `e^{\pi i z / 12}` factor.


        OUTPUT: a complex number

        The `\eta` function is

        .. math::

                        \eta(z) = e^{\pi i z / 12} \prod_{n=1}^{\infty}(1-e^{2\pi inz})



        ALGORITHM: Uses the PARI C library.

        EXAMPLES:

        First we compute `\eta(1+i)`::

            sage: i = CC.0
            sage: z = 1+i; z.eta()
            0.742048775836565 + 0.198831370229911*I

        We compute eta to low precision directly from the definition.

        ::

            sage: z = 1 + i; z.eta()
            0.742048775836565 + 0.198831370229911*I
            sage: pi = CC(pi)        # otherwise we will get a symbolic result.
            sage: exp(pi * i * z / 12) * prod([1-exp(2*pi*i*n*z) for n in range(1,10)])
            0.742048775836565 + 0.198831370229911*I

        The optional argument allows us to omit the fractional part::

            sage: z = 1 + i
            sage: z.eta(omit_frac=True)
            0.998129069925959 - 8.12769318...e-22*I
            sage: prod([1-exp(2*pi*i*n*z) for n in range(1,10)])
            0.998129069925958 + 4.59099857829247e-19*I

        We illustrate what happens when `z` is not in the upper
        half plane.

        ::

            sage: z = CC(1)
            sage: z.eta()
            Traceback (most recent call last):
            ...
            ValueError: value must be in the upper half plane

        You can also use functional notation.

        ::

            sage: eta(1+CC(I))
            0.742048775836565 + 0.198831370229911*I
        """
        try:
            return self._parent(self._pari_().eta(not omit_frac))
        except sage.libs.pari.all.PariError:
            raise ValueError, "value must be in the upper half plane"


    def sin(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).sin()
            1.29845758141598 + 0.634963914784736*I
        """
        # write self = a + i*b, then
        # sin(self) = cosh(b)*sin(a) + i*sinh(b)*cos(a)
        cdef ComplexNumber z
        z = self._new()
        cdef mpfr_t ch, sh
        mpfr_init2(sh, self._prec)
        mpfr_sinh(sh, self.__im, rnd)
        mpfr_init2(ch, self._prec)
        mpfr_sqr(ch, sh, rnd)
        mpfr_add_ui(ch, ch, 1, rnd)
        mpfr_sqrt(ch, ch, rnd)
        mpfr_sin_cos(z.__re, z.__im, self.__re, rnd)
        mpfr_mul(z.__re, z.__re, ch, rnd)
        mpfr_mul(z.__im, z.__im, sh, rnd)
        mpfr_clear(sh)
        mpfr_clear(ch)
        return z

    def sinh(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).sinh()
            0.634963914784736 + 1.29845758141598*I
        """
        # write self = a + i*b, then
        # sinh(self) = sinh(a)*cos(b) + i*cosh(a)*sin(b)
        cdef ComplexNumber z
        z = self._new()
        cdef mpfr_t ch, sh
        mpfr_init2(sh, self._prec)
        mpfr_sinh(sh, self.__re, rnd)
        mpfr_init2(ch, self._prec)
        mpfr_sqr(ch, sh, rnd)
        mpfr_add_ui(ch, ch, 1, rnd)
        mpfr_sqrt(ch, ch, rnd)
        mpfr_sin_cos(z.__im, z.__re, self.__im, rnd)
        mpfr_mul(z.__re, z.__re, sh, rnd)
        mpfr_mul(z.__im, z.__im, ch, rnd)
        mpfr_clear(sh)
        mpfr_clear(ch)
        return z

    def tan(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).tan()
            0.271752585319512 + 1.08392332733869*I
        """
        # write self = a + i*b, then
        # tan(self) = [cos(a)*sin(a) + i*cosh(b)*sinh(b)]/[sinh^2(b)+cos^2(a)]
        cdef ComplexNumber z
        z = self._new()
        cdef mpfr_t ch, sh, c, s, a, b
        mpfr_init2(sh, self._prec)
        mpfr_sinh(sh, self.__im, rnd)
        mpfr_init2(ch, self._prec)
        mpfr_init2(a, self._prec)
        mpfr_sqr(a, sh, rnd)
        mpfr_add_ui(ch, a, 1, rnd)
        mpfr_sqrt(ch, ch, rnd)
        mpfr_init2(c, self._prec)
        mpfr_init2(s, self._prec)
        mpfr_sin_cos(s, c, self.__re, rnd)
        mpfr_init2(b, self._prec)
        mpfr_sqr(b, c, rnd)
        mpfr_add(a, a, b, rnd)
        mpfr_mul(z.__re, c, s, rnd)
        mpfr_div(z.__re, z.__re, a, rnd)
        mpfr_mul(z.__im, ch, sh, rnd)
        mpfr_div(z.__im, z.__im, a, rnd)
        mpfr_clear(sh)
        mpfr_clear(ch)
        mpfr_clear(c)
        mpfr_clear(s)
        mpfr_clear(b)
        mpfr_clear(a)
        return z


    def tanh(self):
        """
        EXAMPLES::

            sage: (1+CC(I)).tanh()
            1.08392332733869 + 0.271752585319512*I
        """
        # write self = a + i*b, then
        # tanh(self) = [cosh(a)*sinh(a) + i*cos(b)*sin(b)]/[sinh^2(a)+cos^2(b)]
        cdef ComplexNumber z
        z = self._new()
        cdef mpfr_t ch, sh, c, s, a, b
        mpfr_init2(sh, self._prec)
        mpfr_sinh(sh, self.__re, rnd)
        mpfr_init2(ch, self._prec)
        mpfr_init2(a, self._prec)
        mpfr_sqr(a, sh, rnd)
        mpfr_add_ui(ch, a, 1, rnd)
        mpfr_sqrt(ch, ch, rnd)
        mpfr_init2(c, self._prec)
        mpfr_init2(s, self._prec)
        mpfr_sin_cos(s, c, self.__im, rnd)
        mpfr_init2(b, self._prec)
        mpfr_sqr(b, c, rnd)
        mpfr_add(a, a, b, rnd)
        mpfr_mul(z.__im, c, s, rnd)
        mpfr_div(z.__im, z.__im, a, rnd)
        mpfr_mul(z.__re, ch, sh, rnd)
        mpfr_div(z.__re, z.__re, a, rnd)
        mpfr_clear(sh)
        mpfr_clear(ch)
        mpfr_clear(c)
        mpfr_clear(s)
        mpfr_clear(b)
        mpfr_clear(a)
        return z

    # Other special functions
    def agm(self, right):
        """
        EXAMPLES::

            sage: (1+CC(I)).agm(2-I)
            1.62780548487271 + 0.136827548397369*I
        """
        t = self._parent(right)._pari_()
        return self._parent(self._pari_().agm(t))


    def argument(self):
        r"""
        The argument (angle) of the complex number, normalized so that
        `-\pi < \theta \leq \pi`.

        EXAMPLES::

            sage: i = CC.0
            sage: (i^2).argument()
            3.14159265358979
            sage: (1+i).argument()
            0.785398163397448
            sage: i.argument()
            1.57079632679490
            sage: (-i).argument()
            -1.57079632679490
            sage: (RR('-0.001') - i).argument()
            -1.57179632646156
        """
        cdef real_mpfr.RealNumber x
        x = real_mpfr.RealNumber(self._parent._real_field(), None)
        mpfr_atan2(<mpfr_t> x.value, self.__im, self.__re, rnd)
        return x


    def arg(self):
        """
        Same as argument.

        EXAMPLES::

            sage: i = CC.0
            sage: (i^2).arg()
            3.14159265358979
        """
        return self.argument()

    def conjugate(self):
        """
        Return the complex conjugate of this complex number.

        EXAMPLES::

            sage: i = CC.0
            sage: (1+i).conjugate()
            1.00000000000000 - 1.00000000000000*I
        """
        cdef ComplexNumber x
        x = self._new()

        cdef mpfr_t i
        mpfr_init2(i, self._prec)
        mpfr_neg(i, self.__im, rnd)
        mpfr_set(x.__re, self.__re, rnd)
        mpfr_set(x.__im, i, rnd)
        mpfr_clear(i)
        return x

    def dilog(self):
        r"""
        Returns the complex dilogarithm of self. The complex dilogarithm,
        or Spence's function, is defined by

        `Li_2(z) = - \int_0^z \frac{\log|1-\zeta|}{\zeta} d(\zeta)`

        `= \sum_{k=1}^\infty \frac{z^k}{k}`

        Note that the series definition can only be used for
        `|z| < 1`

        EXAMPLES::

            sage: a = ComplexNumber(1,0)
            sage: a.dilog()
            1.64493406684823
            sage: float(pi^2/6)
            1.6449340668482262

        ::

            sage: b = ComplexNumber(0,1)
            sage: b.dilog()
            -0.205616758356028 + 0.915965594177219*I

        ::

            sage: c = ComplexNumber(0,0)
            sage: c.dilog()
            0
        """
        return self._parent(self._pari_().dilog())

    def exp(ComplexNumber self):
        """
        Compute exp(z).

        EXAMPLES::

            sage: i = ComplexField(300).0
            sage: z = 1 + i
            sage: z.exp()
            1.46869393991588515713896759732660426132695673662900872279767567631093696585951213872272450 + 2.28735528717884239120817190670050180895558625666835568093865811410364716018934540926734485*I
        """
        # write self = a + i*b, then
        # exp(self) = exp(a)*(cos(b) + i*sin(b))
        cdef ComplexNumber z
        z = self._new()
        cdef mpfr_t r
        mpfr_init2(r, self._prec)
        mpfr_exp(r, self.__re, rnd)
        mpfr_sin_cos(z.__im, z.__re, self.__im, rnd)
        mpfr_mul(z.__re, z.__re, r, rnd)
        mpfr_mul(z.__im, z.__im, r, rnd)
        mpfr_clear(r)
        return z

    def gamma(self):
        """
        Return the Gamma function evaluated at this complex number.

        EXAMPLES::

            sage: i = ComplexField(30).0
            sage: (1+i).gamma()
            0.49801567 - 0.15494983*I

        TESTS::

            sage: CC(0).gamma()
            Infinity

        ::

            sage: CC(-1).gamma()
            Infinity
        """
        try:
            return self._parent(self._pari_().gamma())
        except sage.libs.pari.all.PariError:
            from sage.rings.infinity import UnsignedInfinityRing
            return UnsignedInfinityRing.gen()

    def gamma_inc(self, t):
        """
        Return the incomplete Gamma function evaluated at this complex
        number.

        EXAMPLES::

            sage: C, i = ComplexField(30).objgen()
            sage: (1+i).gamma_inc(2 + 3*i)
            0.0020969149 - 0.059981914*I
            sage: (1+i).gamma_inc(5)
            -0.0013781309 + 0.0065198200*I
            sage: C(2).gamma_inc(1 + i)
            0.70709210 - 0.42035364*I
            sage: gamma_inc(2, 1 + i)
            0.70709210 - 0.42035364*I
            sage: gamma_inc(2, 5)
            0.0404276819945128
        """
        return self._parent(self._pari_().incgam(t))

    def log(self):
        r"""
        Complex logarithm of z with branch chosen as follows: Write
        `z = \rho e^{i \theta} with `-\pi <= \theta < pi`. Then
        `\mathrm{log}(z) = \mathrm{log}(\rho) + i \theta`.

        .. warning::

           Currently the real log is computed using floats, so there
           is potential precision loss.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: a.log()
            0.804718956217050 + 0.463647609000806*I
            sage: log(a.abs())
            0.804718956217050
            sage: a.argument()
            0.463647609000806

        ::

            sage: b = ComplexNumber(float(exp(42)),0)
            sage: b.log()
            41.99999999999971
        """
        theta = self.argument()
        rho = abs(self)
        return ComplexNumber(self._parent, rho.log(), theta)

    def additive_order(self):
        """
        EXAMPLES::

            sage: CC(0).additive_order()
            1
            sage: CC.gen().additive_order()
            +Infinity
        """
        if self == 0:
            return 1
        else:
            return infinity.infinity

    def sqrt(self, all=False):
        """
        The square root function, taking the branch cut to be the negative
        real axis.

        INPUT:


        -  ``all`` - bool (default: False); if True, return a
           list of all square roots.


        EXAMPLES::

            sage: C.<i> = ComplexField(30)
            sage: i.sqrt()
            0.70710678 + 0.70710678*I
            sage: (1+i).sqrt()
            1.0986841 + 0.45508986*I
            sage: (C(-1)).sqrt()
            1.0000000*I
            sage: (1 + 1e-100*i).sqrt()^2
            1.0000000 + 1.0000000e-100*I
            sage: i = ComplexField(200).0
            sage: i.sqrt()
            0.70710678118654752440084436210484903928483593768847403658834 + 0.70710678118654752440084436210484903928483593768847403658834*I
        """
        cdef ComplexNumber z = self._new()
        if mpfr_zero_p(self.__im):
            if mpfr_sgn(self.__re) >= 0:
                mpfr_set_ui(z.__im, 0, rnd)
                mpfr_sqrt(z.__re, self.__re, rnd)
            else:
                mpfr_set_ui(z.__re, 0, rnd)
                mpfr_neg(z.__im, self.__re, rnd)
                mpfr_sqrt(z.__im, z.__im, rnd)
            if all:
                return [z, -z] if z else [z]
            else:
                return z
        # self = x + yi = (a+bi)^2
        # expand, substitute, solve
        # a^2 = (x + sqrt(x^2+y^2))/2
        cdef bint avoid_branch = mpfr_sgn(self.__re) < 0 and mpfr_cmpabs(self.__im, self.__re) < 0
        cdef mpfr_t a2
        mpfr_init2(a2, self._prec)
        mpfr_hypot(a2, self.__re, self.__im, rnd)
        if avoid_branch:
            # x + sqrt(x^2+y^2) numerically unstable for x near negative real axis
            # so we compute sqrt of (-z) and shift by i at the end
            mpfr_sub(a2, a2, self.__re, rnd)
        else:
            mpfr_add(a2, a2, self.__re, rnd)
        mpfr_mul_2si(a2, a2, -1, rnd)
        # a = sqrt(a2)
        mpfr_sqrt(z.__re, a2, rnd)
        # b = y/(2a)
        mpfr_div(z.__im, self.__im, z.__re, rnd)
        mpfr_mul_2si(z.__im, z.__im, -1, rnd)
        mpfr_clear(a2)
        if avoid_branch:
            mpfr_swap(z.__re, z.__im)
            # Note that y (hence b) was never negated, so we have z=i*sqrt(self).
            # if we were below the branch cut, we want the other branch
            if mpfr_sgn(self.__im) < 0:
                mpfr_neg(z.__re, z.__re, rnd)
                mpfr_neg(z.__im, z.__im, rnd)
        if all:
            return [z, -z]
        else:
            return z

    def nth_root(self, n, all=False):
        """
        The n-th root function.

        INPUT:


        -  ``all`` - bool (default: False); if True, return a
           list of all n-th roots.


        EXAMPLES::

            sage: a = CC(27)
            sage: a.nth_root(3)
            3.00000000000000
            sage: a.nth_root(3, all=True)
            [3.00000000000000, -1.50000000000000 + 2.59807621135332*I, -1.50000000000000 - 2.59807621135332*I]
            sage: a = ComplexField(20)(2,1)
            sage: [r^7 for r in a.nth_root(7, all=True)]
            [2.0000 + 1.0000*I, 2.0000 + 1.0000*I, 2.0000 + 1.0000*I, 2.0000 + 1.0000*I, 2.0000 + 1.0000*I, 2.0000 + 1.0001*I, 2.0000 + 1.0001*I]
        """
        if self.is_zero():
            return [self] if all else self

        cdef ComplexNumber z
        z = self._new()

        cdef real_mpfr.RealNumber arg, rho
        cdef mpfr_t r
        rho = abs(self)
        arg = self.argument() / n
        mpfr_init2(r, self._prec)
        mpfr_root(r, <mpfr_t> rho.value, n, rnd)

        mpfr_sin_cos(z.__im, z.__re, <mpfr_t> arg.value, rnd)
        mpfr_mul(z.__re, z.__re, r, rnd)
        mpfr_mul(z.__im, z.__im, r, rnd)

        if not all:
            mpfr_clear(r)
            return z

        R = self._parent._real_field()
        cdef real_mpfr.RealNumber theta
        theta = R.pi()*2/n
        zlist = [z]
        for k in range(1, n):
            z = self._new()
            arg += theta
            mpfr_sin_cos(z.__im, z.__re, <mpfr_t> arg.value, rnd)
            mpfr_mul(z.__re, z.__re, r, rnd)
            mpfr_mul(z.__im, z.__im, r, rnd)
            zlist.append(z)

        mpfr_clear(r)
        return zlist


    def is_square(self):
        """
        This function always returns true as `\CC` is
        algebraically closed.

        EXAMPLES::

            sage: a = ComplexNumber(2,1)
            sage: a.is_square()
            True

        `\CC` is algebraically closed, hence every element
        is a square::

            sage: b = ComplexNumber(5)
            sage: b.is_square()
            True
        """
        return True

    def is_real(self):
        """
        Return True if self is real, i.e. has imaginary part zero.

        EXAMPLES::

            sage: CC(1.23).is_real()
            True
            sage: CC(1+i).is_real()
            False
        """
        return (mpfr_zero_p(self.__im) <> 0)

    def is_imaginary(self):
        """
        Return True if self is imaginary, i.e. has real part zero.

        EXAMPLES::

            sage: CC(1.23*i).is_imaginary()
            True
            sage: CC(1+i).is_imaginary()
            False
        """
        return (mpfr_zero_p(self.__re) <> 0)

    def zeta(self):
        """
        Return the Riemann zeta function evaluated at this complex number.

        EXAMPLES::

            sage: i = ComplexField(30).gen()
            sage: z = 1 + i
            sage: z.zeta()
            0.58215806 - 0.92684856*I
            sage: zeta(z)
            0.58215806 - 0.92684856*I
        """
        return self._parent(self._pari_().zeta())

    def algdep(self, n, **kwds):
        """
        Returns a polynomial of degree at most `n` which is
        approximately satisfied by this complex number. Note that the
        returned polynomial need not be irreducible, and indeed usually
        won't be if `z` is a good approximation to an algebraic
        number of degree less than `n`.

        ALGORITHM: Uses the PARI C-library algdep command.

        INPUT: Type algdep? at the top level prompt. All additional
        parameters are passed onto the top-level algdep command.

        EXAMPLE::

            sage: C = ComplexField()
            sage: z = (1/2)*(1 + sqrt(3.0) *C.0); z
            0.500000000000000 + 0.866025403784439*I
            sage: p = z.algdep(5); p
            x^5 + x^2
            sage: p.factor()
            (x + 1) * x^2 * (x^2 - x + 1)
            sage: z^2 - z + 1
            1.11022302462516e-16
        """
        import sage.rings.arith
        return sage.rings.arith.algdep(self,n, **kwds)

    def algebraic_dependancy( self, n ):
        """
        Returns a polynomial of degree at most `n` which is
        approximately satisfied by this complex number. Note that the
        returned polynomial need not be irreducible, and indeed usually
        won't be if `z` is a good approximation to an algebraic
        number of degree less than `n`.

        ALGORITHM: Uses the PARI C-library algdep command.

        INPUT: Type algdep? at the top level prompt. All additional
        parameters are passed onto the top-level algdep command.

        EXAMPLE::

            sage: C = ComplexField()
            sage: z = (1/2)*(1 + sqrt(3.0) *C.0); z
            0.500000000000000 + 0.866025403784439*I
            sage: p = z.algebraic_dependancy(5); p
            x^5 + x^2
            sage: p.factor()
            (x + 1) * x^2 * (x^2 - x + 1)
            sage: z^2 - z + 1
            1.11022302462516e-16
        """
        return self.algdep( n )

def make_ComplexNumber0( fld, mult_order, re, im ):
    x = ComplexNumber( fld, re, im )
    x._set_multiplicative_order( mult_order )
    return x



def create_ComplexNumber(s_real, s_imag=None, int pad=0, min_prec=53):
    r"""
    Return the complex number defined by the strings s_real and
    s_imag as an element of ``ComplexField(prec=n)``,
    where n potentially has slightly more (controlled by pad) bits than
    given by s.

    INPUT:

    -  ``s_real`` - a string that defines a real number
       (or something whose string representation defines a number)

    -  ``s_imag`` - a string that defines a real number
       (or something whose string representation defines a number)

    -  ``pad`` - an integer >= 0.

    -  ``min_prec`` - number will have at least this many
       bits of precision, no matter what.


    EXAMPLES::

        sage: ComplexNumber('2.3')
        2.30000000000000
        sage: ComplexNumber('2.3','1.1')
        2.30000000000000 + 1.10000000000000*I
        sage: ComplexNumber(10)
        10.0000000000000
        sage: ComplexNumber(10,10)
        10.0000000000000 + 10.0000000000000*I
        sage: ComplexNumber(1.000000000000000000000000000,2)
        1.000000000000000000000000000 + 2.000000000000000000000000000*I
        sage: ComplexNumber(1,2.000000000000000000000)
        1.000000000000000000000 + 2.000000000000000000000*I

    ::

        sage: sage.rings.complex_number.create_ComplexNumber(s_real=2,s_imag=1)
        2.00000000000000 + 1.00000000000000*I
    """
    if s_imag is None:
        s_imag = 0

    if not isinstance(s_real, str):
        s_real = str(s_real).strip()
    if not isinstance(s_imag, str):
        s_imag = str(s_imag).strip()
    #if base == 10:
    bits = max(int(3.32192*len(s_real)),int(3.32192*len(s_imag)))
    #else:
    #    bits = max(int(math.log(base,2)*len(s_imag)),int(math.log(base,2)*len(s_imag)))

    C = complex_field.ComplexField(prec=max(bits+pad, min_prec))

    return ComplexNumber(C, s_real, s_imag)


cdef class RRtoCC(Map):

    cdef ComplexNumber _zero

    def __init__(self, RR, CC):
        """
        EXAMPLES::

            sage: from sage.rings.complex_number import RRtoCC
            sage: RRtoCC(RR, CC)
            Natural map:
              From: Real Field with 53 bits of precision
              To:   Complex Field with 53 bits of precision
        """
        Map.__init__(self, RR, CC)
        self._zero = ComplexNumber(CC, 0)
        self._repr_type_str = "Natural"

    cpdef Element _call_(self, x):
        """
        EXAMPLES::

            sage: from sage.rings.complex_number import RRtoCC
            sage: f = RRtoCC(RealField(100), ComplexField(10))
            sage: f(1/3)
            0.33
        """
        cdef ComplexNumber z = self._zero._new()
        mpfr_set(z.__re, (<RealNumber>x).value, rnd)
        mpfr_set_ui(z.__im, 0, rnd)
        return z


cdef class CCtoCDF(Map):

    cpdef Element _call_(self, x):
        """
        EXAMPLES::

            sage: from sage.rings.complex_number import CCtoCDF
            sage: f = CCtoCDF(CC, CDF)
            sage: f(CC.0)
            1.0*I
            sage: f(exp(pi*CC.0/4))
            0.707106781187 + 0.707106781187*I
        """
        cdef ComplexDoubleElement z = <ComplexDoubleElement>PY_NEW(ComplexDoubleElement)
        z._complex.dat[0] = mpfr_get_d((<ComplexNumber>x).__re, GMP_RNDN)
        z._complex.dat[1] = mpfr_get_d((<ComplexNumber>x).__im, GMP_RNDN)
        return z
