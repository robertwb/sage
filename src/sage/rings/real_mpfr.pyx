r"""
Field of Arbitrary Precision Real Numbers

AUTHORS:

- Kyle Schalm (2005-09)

- William Stein: bug fixes, examples, maintenance

- Didier Deshommes (2006-03-19): examples

- David Harvey (2006-09-20): compatibility with Element._parent

- William Stein (2006-10): default printing truncates to avoid base-2
  rounding confusing (fix suggested by Bill Hart)

- Didier Deshommes: special constructor for QD numbers

- Paul Zimmermann (2008-01): added new functions from mpfr-2.3.0,
  replaced some, e.g., sech = 1/cosh, by their original mpfr version.

- Carl Witty (2008-02): define floating-point rank and associated
  functions; add some documentation

- Robert Bradshaw (2009-09): decimal literals, optimizations

This is a binding for the MPFR arbitrary-precision floating point
library.

We define a class ``RealField``, where each instance of
``RealField`` specifies a field of floating-point
numbers with a specified precision and rounding mode. Individual
floating-point numbers are of class ``RealNumber``.

In Sage (as in MPFR), floating-point numbers of precision
`p` are of the form `s m 2^{e-p}`, where
`s \in \{-1, 1\}`, `2^{p-1} \leq m < 2^p`, and
`-2^{30} + 1 \leq e \leq 2^{30} - 1`; plus the special
values ``+0``, ``-0``,
``+infinity``, ``-infinity``, and
``NaN`` (which stands for Not-a-Number).

Operations in this module which are direct wrappers of MPFR
functions are "correctly rounded"; we briefly describe what this
means. Assume that you could perform the operation exactly, on real
nunbers, to get a result `r`. If this result can be
represented as a floating-point number, then we return that
number.

Otherwise, the result `r` is between two floating-point
numbers. For the directed rounding modes (round to plus infinity,
round to minus infinity, round to zero), we return the
floating-point number in the indicated direction from `r`.
For round to nearest, we return the floating-point number which is
nearest to `r`.

This leaves one case unspecified: in round to nearest mode, what
happens if `r` is exactly halfway between the two nearest
floating-point numbers? In that case, we round to the number with
an even mantissa (the mantissa is the number `m` in the
representation above).

Consider the ordered set of floating-point numbers of precision
`p`. (Here we identify ``+0`` and
``-0``, and ignore ``NaN``.) We can give a
bijection between these floating-point numbers and a segment of the
integers, where 0 maps to 0 and adjacent floating-point numbers map
to adjacent integers. We call the integer corresponding to a given
floating-point number the "floating-point rank" of the number.
(This is not standard terminology; I just made it up.)

EXAMPLES: A difficult conversion::

    sage: RR(sys.maxint)
    9.22337203685478e18      # 64-bit
    2.14748364700000e9       # 32-bit

TESTS::

    sage: -1e30
    -1.00000000000000e30

Make sure we don't have a new field for every new literal::

    sage: parent(2.0) is parent(2.0)
    True
    sage: RealField(100, rnd='RNDZ') is RealField(100, rnd='RNDD')
    False
    sage: RealField(100, rnd='RNDZ') is RealField(100, rnd='RNDZ')
    True
"""

#*****************************************************************************
#
#   SAGE: System for Algebra and Geometry Experimentation
#
#       Copyright (C) 2005-2006 William Stein <wstein@gmail.com>
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

import math # for log
import sys
import weakref
import re

include '../ext/interrupt.pxi'
include "../ext/stdsage.pxi"
include "../ext/random.pxi"

cimport sage.rings.ring
import  sage.rings.ring

cimport sage.structure.element
from sage.structure.element cimport RingElement, Element, ModuleElement
import  sage.structure.element

import sage.misc.misc as misc

import operator

from sage.libs.pari.gen import PariInstance, gen
from sage.libs.pari.gen cimport PariInstance, gen

from integer import Integer
from integer cimport Integer
from rational import Rational
from rational cimport Rational

from sage.categories.map cimport Map

cdef ZZ, QQ, RDF
from integer_ring import ZZ
from rational_field import QQ
from real_double import RDF
from real_double cimport RealDoubleElement

import sage.rings.rational_field

import sage.rings.infinity

from sage.structure.parent_gens cimport ParentWithGens

cdef class RealNumber(sage.structure.element.RingElement)

#*****************************************************************************
#
#       Implementation
#
#*****************************************************************************

_re_skip_zeroes = re.compile(r'^(.+?)0*$')

#*****************************************************************************
#
#       External Python access to constants
#
#*****************************************************************************

def mpfr_prec_min():
    """
    Return the mpfr variable MPFR_PREC_MIN.
    """
    return MPFR_PREC_MIN

cdef int MY_MPFR_PREC_MAX = 16777216
def mpfr_prec_max():
    global MY_MPFR_PREC_MAX
    # lots of things in mpfr *crash* if we use MPFR_PREC_MAX!
    # So don't.   Using 2**24 seems to work well. (see above)
    return MY_MPFR_PREC_MAX

#*****************************************************************************
#
#       Real Field
#
#*****************************************************************************
# The real field is in Pyrex, so mpfr elements will have access to
# their parent via direct C calls, which will be faster.

_rounding_modes = ['RNDN', 'RNDZ', 'RNDU', 'RNDD']

cdef object RealField_cache = weakref.WeakValueDictionary()

def RealField_constructor(int prec=53, int sci_not=0, rnd="RNDN"):
    """
    RealField(prec, sci_not, rnd):

    INPUT:


    -  ``prec`` - (integer) precision; default = 53 prec is
       the number of bits used to represent the mantissa of a
       floating-point number. The precision can be any integer between
       mpfr_prec_min() and mpfr_prec_max(). In the current
       implementation, mpfr_prec_min() is equal to 2.


    -  ``sci_not`` - (default: False) if True, always display using
       scientific notation; if False, display using scientific notation
       only for very large or very small numbers

    -  ``rnd`` - (string) the rounding mode

      - RNDN - (default) round to nearest:
        Knuth says this is the best choice to prevent "floating point
        drift".

      - RNDD - round towards minus infinity

      - RNDZ - round towards zero

      - RNDU - round towards plus infinity

    EXAMPLES::

        sage: RealField(10)
        Real Field with 10 bits of precision
        sage: RealField()
        Real Field with 53 bits of precision
        sage: RealField(100000)
        Real Field with 100000 bits of precision

    .. note::

       The default precision is 53, since according to the MPFR
       manual: 'mpfr should be able to exactly reproduce all
       computations with double-precision machine floating-point
       numbers (double type in C), except the default exponent range
       is much wider and subnormal numbers are not implemented.'
    """
    try:
        return RealField_cache[prec, sci_not, rnd]
    except KeyError:
        RealField_cache[prec, sci_not, rnd] = R = RealField(prec=prec, sci_not=sci_not, rnd=rnd)
        return R

cdef class RealField(sage.rings.ring.Field):
    """
    An approximation to the field of real numbers using floating point
    numbers with any specified precision. Answers derived from
    calculations in this approximation may differ from what they would
    be if those calculations were performed in the true field of real
    numbers. This is due to the rounding errors inherent to finite
    precision calculations.

    See the documentation for the module sage.rings.real_mpfr for more
    details.
    """

    def __init__(self, int prec=53, int sci_not=0, rnd="RNDN"):
        global MY_MPFR_PREC_MAX
        cdef RealNumber rn
        if prec < MPFR_PREC_MIN or prec > MY_MPFR_PREC_MAX:
            raise ValueError, "prec (=%s) must be >= %s and <= %s."%(
                prec, MPFR_PREC_MIN, MY_MPFR_PREC_MAX)
        self.__prec = prec
        if not isinstance(rnd, str):
            raise TypeError, "rnd must be a string"
        self.sci_not = sci_not
        n = _rounding_modes.index(rnd)
        if n == -1:
            raise ValueError, "rnd (=%s) must be one of RNDN, RNDZ, RNDU, or RNDD"%rnd
        self.rnd = n
        self.rnd_str = rnd
        ParentWithGens.__init__(self, self, tuple([]), False)

        # hack, we cannot call the constructor here
        rn = PY_NEW(RealNumber)
        rn._parent = self
        mpfr_init2(rn.value, self.__prec)
        rn.init = 1
        mpfr_set_d(rn.value, 0.0, self.rnd)
        self._zero_element = rn

        rn = PY_NEW(RealNumber)
        rn._parent = self
        mpfr_init2(rn.value, self.__prec)
        rn.init = 1
        mpfr_set_d(rn.value, 1.0, self.rnd)
        self._one_element = rn

        self._populate_coercion_lists_(convert_method_name='_mpfr_')

    cdef RealNumber _new(self):
        """
        Return a new real number with parent self.
        """
        cdef RealNumber x
        x = PY_NEW(RealNumber)
        x._parent = self
        mpfr_init2(x.value, self.__prec)
        x.init = 1
        return x

    def _repr_(self):
        s = "Real Field with %s bits of precision"%self.__prec
        if self.rnd != GMP_RNDN:
            s = s + " and rounding %s"%(self.rnd_str)
        return s

    def _latex_(self):
        return "\\Bold{R}"

    def _sage_input_(self, sib, coerce):
        r"""
        Produce an expression which will reproduce this value when
        evaluated.

        EXAMPLES::

            sage: sage_input(RR, verify=True)
            # Verified
            RR
            sage: sage_input(RealField(25, rnd='RNDZ'), verify=True)
            # Verified
            RealField(25, rnd='RNDZ')
            sage: k = (RR, RealField(75, rnd='RNDU'), RealField(13))
            sage: sage_input(k, verify=True)
            # Verified
            (RR, RealField(75, rnd='RNDU'), RealField(13))
            sage: sage_input((k, k), verify=True)
            # Verified
            RR75u = RealField(75, rnd='RNDU')
            RR13 = RealField(13)
            ((RR, RR75u, RR13), (RR, RR75u, RR13))
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: RealField(99, rnd='RNDD')._sage_input_(SageInputBuilder(), False)
            {call: {atomic:RealField}({atomic:99}, rnd={atomic:'RNDD'})}
        """
        if self.rnd == GMP_RNDN and self.prec() == 53:
            return sib.name('RR')

        if self.rnd != GMP_RNDN:
            rnd_abbrev = self.rnd_str[-1:].lower()
            v = sib.name('RealField')(sib.int(self.prec()), rnd=self.rnd_str)
        else:
            rnd_abbrev = ''
            v = sib.name('RealField')(sib.int(self.prec()))

        name = 'RR%d%s' % (self.prec(), rnd_abbrev)
        sib.cache(self, v, name)
        return v

    cpdef bint is_exact(self) except -2:
        return False

    def _element_constructor_(self, x, base=10):
        """
        Coerce x into this real field.

        EXAMPLES::

            sage: R = RealField(20)
            sage: R('1.234')
            1.2340
            sage: R('2', base=2)
            Traceback (most recent call last):
            ...
            TypeError: Unable to convert x (='2') to real number.
            sage: a = R('1.1001', base=2); a
            1.5625
            sage: a.str(2)
            '1.1001000000000000000'
        """
        if hasattr(x, '_mpfr_'):
            return x._mpfr_(self)
        cdef RealNumber z
        z = self._new()
        z._set(x, base)
        return z

    cpdef _coerce_map_from_(self, S):
        """
        Canonical coercion of x to this mpfr real field.

        The rings that canonically coerce to this mpfr real field are:

        - Any mpfr real field with precision that is as large as this one

        - int, long, integer, and rational rings.

        - the field of algebraic reals

        - floats and RDF if self.prec = 53

        EXAMPLES::

            sage: RR.has_coerce_map_from(ZZ)
            True
            sage: RR.has_coerce_map_from(float)
            True
            sage: RealField(100).has_coerce_map_from(float)
            False
            sage: RR.has_coerce_map_from(RealField(200))
            True
            sage: RR.has_coerce_map_from(RealField(20))
            False
            sage: RR.has_coerce_map_from(RDF)
            True
            sage: RR.coerce_map_from(ZZ)(2)
            2.00000000000000
            sage: RR.coerce(3.4r)
            3.40000000000000
            sage: RR.coerce(3.4)
            3.40000000000000
            sage: RR.coerce(3.4r)
            3.40000000000000
            sage: RR.coerce(3.400000000000000000000000000000000000000000)
            3.40000000000000
            sage: RealField(100).coerce(3.4)
            Traceback (most recent call last):
            ...
            TypeError: no canonical coercion from Real Field with 53 bits of precision to Real Field with 100 bits of precision
            sage: RR.coerce(17/5)
            3.40000000000000
            sage: RR.coerce(2^4000)
            1.31820409343094e1204

            sage: RR.coerce_map_from(float)
            Generic map:
              From: Set of Python objects of type 'float'
              To:   Real Field with 53 bits of precision


        TESTS::

            sage: 1.0 - ZZ(1) - int(1) - long(1) - QQ(1) - RealField(100)(1) - AA(1) - RLF(1)
            -6.00000000000000
            sage: RR['x'].get_action(ZZ)
            Right scalar multiplication by Integer Ring on Univariate Polynomial Ring in x over Real Field with 53 bits of precision
        """
        if S is ZZ:
            return ZZtoRR(ZZ, self)
        elif S is QQ:
            return QQtoRR(QQ, self)
        elif (S is RDF or S is float) and self.__prec <= 53:
            return double_toRR(S, self)
        elif S is int:
            return int_toRR(int, self)
        elif isinstance(S, RealField) and S.prec() >= self.__prec:
            return RRtoRR(S, self)
        elif QQ.has_coerce_map_from(S):
            return QQtoRR(QQ, self) * QQ.coerce_map_from(S)
        from sage.rings.qqbar import AA
        from sage.rings.real_lazy import RLF
        if S == AA or S is RLF:
            return self._generic_convert_map(S)
        return self._coerce_map_via([RLF], S)

    def __cmp__(self, other):
        """
        EXAMPLES::

            sage: RealField(10) == RealField(11)
            False
            sage: RealField(10) == RealField(10)
            True
            sage: RealField(10,rnd='RNDN') == RealField(10,rnd='RNDZ')
            False

        Scientific notation affects only printing, not mathematically how
        the field works, so this does not affect equality testing.

        ::

            sage: RealField(10,sci_not=True) == RealField(10,sci_not=False)
            True
            sage: RealField(10) == IntegerRing()
            False

        ::

            sage: RS = RealField(sci_not=True)
            sage: RR == RS
            True
            sage: RS.scientific_notation(False)
            sage: RR == RS
            True
        """
        if not isinstance(other, RealField):
            return -1
        cdef RealField _other
        _other = other  # to access C structure
        if self.__prec == _other.__prec and self.rnd == _other.rnd: \
               #and self.sci_not == _other.sci_not:
            return 0
        return 1

    def __reduce__(self):
        """
        EXAMPLES::

            sage: R = RealField(sci_not=1, prec=200, rnd='RNDU')
            sage: loads(dumps(R)) == R
            True
        """
        return __create__RealField_version0, (self.__prec, self.sci_not, self.rnd_str)

    def construction(self):
        """
        Returns the functorial construction of self, namely, completion of
        the rational numbers with respect to the prime at
        `\infty`.

        Also preserves other information that makes this field unique (e.g.
        precision, rounding, print mode).

        EXAMPLES::

            sage: R = RealField(100, rnd='RNDU')
            sage: c, S = R.construction(); S
            Rational Field
            sage: R == c(S)
            True
        """
        from sage.categories.pushout import CompletionFunctor
        return (CompletionFunctor(sage.rings.infinity.Infinity,
                                  self.prec(),
                                  {'sci_not': self.scientific_notation(), 'rnd': self.rounding_mode()}),
               sage.rings.rational_field.QQ)

    def gen(self, i=0):
        if i == 0:
            return self(1)
        else:
            raise IndexError

    def complex_field(self):
        """
        Return complex field of the same precision.
        """
        import sage.rings.complex_field
        return sage.rings.complex_field.ComplexField(self.prec())

    def algebraic_closure(self):
        """
        Returns the algebraic closure of self, ie the complex field with
        the same precision.
        """
        return self.complex_field()

    def ngens(self):
        return 1

    def gens(self):
        return [self.gen()]

    def _is_valid_homomorphism_(self, codomain, im_gens):
        try:
            s = codomain.coerce(self(1))
        except TypeError:
            return False
        return s == im_gens[0]

    def is_atomic_repr(self):
        """
        Returns True, to signify that elements of this field print without
        sums, so parenthesis aren't required, e.g., in coefficients of
        polynomials.

        EXAMPLES::

            sage: RealField(10).is_atomic_repr()
            True
        """
        return True

    def is_finite(self):
        """
        Returns False, since the field of real numbers is not finite.

        EXAMPLES::

            sage: RealField(10).is_finite()
            False
        """
        return False

    def characteristic(self):
        """
        Returns 0, since the field of real numbers has characteristic 0.

        EXAMPLES::

            sage: RealField(10).characteristic()
            0
        """
        return 0

    def name(self):
        return "RealField%s_%s"%(self.__prec,self.rnd)

    def __hash__(self):
        return hash(self.name())

    def precision(self):
        return self.__prec

    def prec(self):
        return self.__prec

    def _magma_init_(self, magma):
        r"""
        Return a string representation of self in the Magma language.

        EXAMPLES::

            sage: magma(RealField(70)) # optional - magma
            Real field of precision 21
            sage: 10^21 < 2^70 < 10^22
            True
            sage: s = magma(RealField(70)).sage(); s # optional - magma
            Real Field with 70 bits of precision
        """
        return "RealField(%s : Bits := true)" % self.prec()

    def to_prec(self, prec):
        """
        Returns the real field that is identical to self, except at the
        specified precision.

        EXAMPLES::

            sage: RR.to_prec(212)
            Real Field with 212 bits of precision
            sage: R = RealField(30, rnd="RNDZ")
            sage: R.to_prec(300)
            Real Field with 300 bits of precision and rounding RNDZ
        """
        if prec == self.__prec:
            return self
        else:
            return RealField_constructor(prec, self.sci_not, _rounding_modes[self.rnd])

    # int mpfr_const_pi (mpfr_t rop, mp_rnd_t rnd)
    def pi(self):
        """
        Returns pi to the precision of this field.

        EXAMPLES::

            sage: R = RealField(100)
            sage: R.pi()
            3.1415926535897932384626433833
            sage: R.pi().sqrt()/2
            0.88622692545275801364908374167
            sage: R = RealField(150)
            sage: R.pi().sqrt()/2
            0.88622692545275801364908374167057259139877473
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        # The docs for mpfr_free_cache say "Free the cache used by
        # the functions computing constants if needed (currently
        # mpfr_const_log2, mpfr_const_pi and mpfr_const_euler)", so
        # this isn't a seriously bad thing to do.  This prevents trac
        # #5689.  This is needed for all constants, despite what the docs say.
        # NOTE: The MPFR docs at this time leave off several mpfr_const
        # functions, but this free is needed for them too!
        mpfr_free_cache()
        mpfr_const_pi(x.value, self.rnd)
        _sig_off
        return x


    # int mpfr_const_euler (mpfr_t rop, mp_rnd_t rnd)
    def euler_constant(self):
        """
        Returns Euler's gamma constant to the precision of this field.

        EXAMPLES::

            sage: RealField(100).euler_constant()
            0.57721566490153286060651209008
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_free_cache()
        mpfr_const_euler(x.value, self.rnd)
        _sig_off
        return x

    # int mpfr_const_catalan (mpfr_t rop, mp_rnd_t rnd)
    def catalan_constant(self):
        """
        Returns Catalan's constant to the precision of this field.

        EXAMPLES::

            sage: RealField(100).catalan_constant()
            0.91596559417721901505460351493
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_free_cache()
        mpfr_const_catalan(x.value, self.rnd)
        _sig_off
        return x

    # int mpfr_const_log2 (mpfr_t rop, mp_rnd_t rnd)
    def log2(self):
        """
        Returns log(2) to the precision of this field.

        EXAMPLES::

            sage: R=RealField(100)
            sage: R.log2()
            0.69314718055994530941723212146
            sage: R(2).log()
            0.69314718055994530941723212146
        """
        cdef RealNumber x = self._new()
        _sig_on
        mpfr_free_cache()
        mpfr_const_log2(x.value, self.rnd)
        _sig_off
        return x

    def random_element(self, min=-1, max=1, distribution=None):
        """
        Returns a uniformly distributed random number between min and max
        (default -1 to 1).

        EXAMPLES::

            sage: RealField(100).random_element(-5, 10)
            1.9305310520925994224072377281
            sage: RealField(10).random_element()
            -0.84

        TESTS::

            sage: RealField(31).random_element()
            -0.207006278
            sage: RealField(32).random_element()
            -0.757827933
            sage: RealField(33).random_element()
            -0.530834221
            sage: RealField(63).random_element()
            0.918013195263849341
            sage: RealField(64).random_element()
            -0.805114150788947694
            sage: RealField(65).random_element()
            0.2035927570696802284
            sage: RealField(10).random_element()
            -0.59
            sage: RealField(10).random_element()
            0.57
            sage: RR.random_element()
            0.931242676441124
            sage: RR.random_element()
            0.979095507956490
        """
        cdef RealNumber x = self._new()
        cdef randstate rstate = current_randstate()
        if sizeof(long) == 4:
            # This is a gross hack that depends on the internals of
            # MPFR... but that's OK, because if MPFR changes it will
            # be instantly caught by the doctests above.
            # MPFR rounds up the precision to a multiple of the
            # current word size, then requests that many bits from
            # .gmp_state .  So if (1 <= precision mod 64 <= 32),
            # a 64-bit machine will request 32 more bits than a 32-bit
            # machine, and the random numbers will get out of sync.
            # We work around this problem by requesting an extra
            # 32 bits on a 32-bit machine.
            if 1 <= self.__prec % 64 <= 32:
                rstate.c_random()
        mpfr_urandomb(x.value, rstate.gmp_state)
        if min == 0 and max == 1:
            return x
        else:
            return (max-min)*x + min

    def factorial(self, int n):
        """
        Return the factorial of the integer n as a real number.
        """
        cdef RealNumber x
        if n < 0:
            raise ArithmeticError, "n must be nonnegative"
        x = self._new()
        _sig_on
        mpfr_fac_ui(x.value, n, self.rnd)
        _sig_off
        return x

    def rounding_mode(self):
        return _rounding_modes[self.rnd]

    def scientific_notation(self, status=None):
        """
        Set or return the scientific notation printing flag. If this flag
        is True then real numbers with this space as parent print using
        scientific notation.

        INPUT:


        -  ``status`` - (bool -) optional flag
        """
        if status is None:
            return self.sci_not
        else:
            self.sci_not = status

    def zeta(self, n=2):
        """
        Return an `n`-th root of unity in the real field, if one
        exists, or raise a ValueError otherwise.

        EXAMPLES::

            sage: R = RealField()
            sage: R.zeta()
            -1.00000000000000
            sage: R.zeta(1)
            1.00000000000000
            sage: R.zeta(5)
            Traceback (most recent call last):
            ...
            ValueError: No 5th root of unity in self
        """
        if n == 1:
            return self(1)
        elif n == 2:
            return self(-1)
        raise ValueError, "No %sth root of unity in self"%n

R = RealField()

#*****************************************************************************
#
#     RealNumber -- element of Real Field
#
#
#
#*****************************************************************************

cdef class RealLiteral(RealNumber)

cdef class RealNumber(sage.structure.element.RingElement):
    """
    A floating point approximation to a real number using any specified
    precision. Answers derived from calculations with such
    approximations may differ from what they would be if those
    calculations were performed with true real numbers. This is due to
    the rounding errors inherent to finite precision calculations.

    The approximation is printed to slightly fewer digits than its
    internal precision, in order to avoid confusing roundoff issues
    that occur because numbers are stored internally in binary.
    """
    cdef RealNumber _new(self):
        """
        Return a new real number with same parent as self.
        """
        cdef RealNumber x
        x = PY_NEW(RealNumber)
        x._parent = self._parent
        mpfr_init2(x.value, (<RealField>self._parent).__prec)
        x.init = 1
        return x

    def __init__(self, RealField parent, x=0, int base=10):
        """
        Create a real number. Should be called by first creating a
        RealField, as illustrated in the examples.

        EXAMPLES::

            sage: R = RealField()
            sage: R('1.2456')
            1.24560000000000
            sage: R = RealField(3)
            sage: R('1.2456')
            1.2

        EXAMPLE: Rounding Modes

        ::

            sage: w = RealField(3)(5/2)
            sage: RealField(2, rnd="RNDZ")(w).str(2)
            '10.'
            sage: RealField(2, rnd="RNDD")(w).str(2)
            '10.'
            sage: RealField(2, rnd="RNDU")(w).str(2)
            '11.'
            sage: RealField(2, rnd="RNDN")(w).str(2)
            '10.'

        .. note::

           A real number is an arbitrary precision mantissa with a
           limited precision exponent. A real number can have three
           special values: Not-a-Number (NaN) or plus or minus
           Infinity. NaN represents an uninitialized object, the
           result of an invalid operation (like 0 divided by 0), or a
           value that cannot be determined (like +Infinity minus
           +Infinity). Moreover, like in the IEEE 754-1985 standard,
           zero is signed, i.e. there are both +0 and -0; the behavior
           is the same as in the IEEE 754-1985 standard and it is
           generalized to the other functions supported by MPFR.
        """
        self.init = 0
        if parent is None:
            raise TypeError
        self._parent = parent
        mpfr_init2(self.value, parent.__prec)
        self.init = 1
        if x is None: return
        self._set(x, base)

    def _magma_init_(self, magma):
        r"""
        Return a string representation of self in the Magma language.

        EXAMPLES::

            sage: magma(RR(10.5)) # optional - magma
            10.5000000000000
            sage: RealField(200)(10.5) # optional - magma
            10.500000000000000000000000000000000000000000000000000000000
        """
        return "%s!%s" % (self.parent()._magma_init_(magma), self)

    cdef _set(self, x, int base):
        # This should not be called except when the number is being created.
        # Real Numbers are supposed to be immutable.
        cdef RealNumber n, d
        cdef RealField parent
        cdef gen _gen
        parent = self._parent
        if PY_TYPE_CHECK(x, RealNumber):
            if PY_TYPE_CHECK(x, RealLiteral):
                s = (<RealLiteral>x).literal
                base = (<RealLiteral>x).base
                if mpfr_set_str(self.value, s, base, parent.rnd):
                    self._set(s, base)
            else:
                mpfr_set(self.value, (<RealNumber>x).value, parent.rnd)
        elif PY_TYPE_CHECK(x, Integer):
            mpfr_set_z(self.value, (<Integer>x).value, parent.rnd)
        elif PY_TYPE_CHECK(x, Rational):
            mpfr_set_q(self.value, (<Rational>x).value, parent.rnd)
        elif PY_TYPE_CHECK(x, gen) and typ((<gen>x).g) == t_REAL:
            _gen = x
            self._set_from_GEN_REAL(_gen.g)
        elif isinstance(x, int):
            mpfr_set_si(self.value, x, parent.rnd)
        elif isinstance(x, long):
            x = Integer(x)
            mpfr_set_z(self.value, (<Integer>x).value, parent.rnd)
        elif isinstance(x, float):
            mpfr_set_d(self.value, x, parent.rnd)
        elif PY_TYPE_CHECK(x, RealDoubleElement):
            mpfr_set_d(self.value, (<RealDoubleElement>x)._value, parent.rnd)
        else:
            s = str(x).replace(' ','')
            if mpfr_set_str(self.value, s, base, parent.rnd):
                if s == 'NaN' or s == '@NaN@':
                    mpfr_set_nan(self.value)
                elif s == '+infinity':
                    mpfr_set_inf(self.value, 1)
                elif s == '-infinity':
                    mpfr_set_inf(self.value, -1)
                else:
                    raise TypeError, "Unable to convert x (='%s') to real number."%s

    cdef _set_from_GEN_REAL(self, GEN g):
        """
        EXAMPLES::

            sage: rt2 = sqrt(pari('2.0'))
            sage: rt2
            1.41421356237310
            sage: rt2.python()
            1.414213562373095048801688724              # 32-bit
            1.4142135623730950488016887242096980786    # 64-bit
            sage: rt2.python().prec()
            96                                         # 32-bit
            128                                        # 64-bit
            sage: pari(rt2.python()) == rt2
            True
            sage: for i in xrange(1, 1000):
            ...       assert(sqrt(pari(i)) == pari(sqrt(pari(i)).python()))
            sage: (-3.1415)._pari_().python()
            -3.14150000000000000
        """
        cdef int sgn
        sgn = signe(g)

        if sgn == 0:
            mpfr_set_ui(self.value, 0, GMP_RNDN)
            return

        cdef int wordsize

        if sage.misc.misc.is_64_bit:
            wordsize = 64
        else:
            wordsize = 32

        cdef mpz_t mantissa
        mpz_init(mantissa)

        mpz_import(mantissa, lg(g) - 2, 1, wordsize/8, 0, 0, &g[2])

        cdef int exponent
        exponent = expo(g)

        # Round to nearest for best results when setting a low-precision
        # MPFR from a high-precision GEN
        mpfr_set_z(self.value, mantissa, GMP_RNDN)
        mpfr_mul_2si(self.value, self.value, exponent - wordsize * (lg(g) - 2) + 1, GMP_RNDN)

        if sgn < 0:
            mpfr_neg(self.value, self.value, GMP_RNDN)

        mpz_clear(mantissa)

    def __reduce__(self):
        """
        EXAMPLES::

            sage: R = RealField(sci_not=1, prec=200, rnd='RNDU')
            sage: b = R('393.39203845902384098234098230948209384028340')
            sage: loads(dumps(b)) == b
            True
            sage: b = R(1)/R(0); b
            +infinity
            sage: loads(dumps(b)) == b
            True
            sage: b = R(-1)/R(0); b
            -infinity
            sage: loads(dumps(b)) == b
            True
            sage: b = R(-1).sqrt(); b
            1.0000000000000000000000000000000000000000000000000000000000*I
            sage: loads(dumps(b)) == b
            True
        """
        s = self.str(32, no_sci=False, e='@')
        return (__create__RealNumber_version0, (self._parent, s, 32))

    def  __dealloc__(self):
        if self.init:
            mpfr_clear(self.value)

    def __repr__(self):
        return self.str(10)

    def _latex_(self):
        s = self.str()
        parts = s.split('e')
        if len(parts) > 1:
            # scientific notation
            if parts[1][0] == '+':
                parts[1] = parts[1][1:]
            s = "%s \\times 10^{%s}" % (parts[0], parts[1])
        return s

    def _interface_init_(self, I=None):
        """
        Return string representation of self in base 10, avoiding
        scientific notation except for very large or very small numbers.

        This is most likely to make sense in other computer algebra systems
        (this function is the default for exporting to other computer
        algebra systems).

        EXAMPLES::

            sage: n = 1.3939494594
            sage: n._interface_init_()
            '1.3939494593999999'
            sage: s1 = RR(sin(1)); s1
            0.841470984807897
            sage: s1._interface_init_()
            '0.84147098480789650'
            sage: s1 == RR(gp(s1))
            True
        """
        return self.str(10, no_sci=True, truncate=False)

    def _sage_input_(self, sib, coerced):
        r"""
        Produce an expression which will reproduce this value when
        evaluated.

        EXAMPLES::

            sage: for prec in (2, 53, 200):
            ...       for rnd_dir in ('RNDN', 'RNDD', 'RNDU', 'RNDZ'):
            ...           fld = RealField(prec, rnd=rnd_dir)
            ...           var = polygen(fld)
            ...           for v in [NaN, -infinity, -20, -e, 0, 1, 2^500, -2^4000, -2^-500, 2^-4000] + [fld.random_element() for _ in range(5)]:
            ...               for preparse in (True, False, None):
            ...                   _ = sage_input(fld(v), verify=True, preparse=preparse)
            ...                   _ = sage_input(fld(v) * var, verify=True, preparse=preparse)
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: sib_np = SageInputBuilder(preparse=False)
            sage: RR60 = RealField(60)
            sage: RR(-infinity)._sage_input_(sib, True)
            {unop:- {call: {atomic:RR}({atomic:Infinity})}}
            sage: RR(NaN)._sage_input_(sib, True)
            {call: {atomic:RR}({atomic:NaN})}
            sage: RR(12345)._sage_input_(sib, True)
            {atomic:12345}
            sage: RR(-12345)._sage_input_(sib, False)
            {unop:- {call: {atomic:RR}({atomic:12345})}}
            sage: RR(1.579)._sage_input_(sib, True)
            {atomic:1.579}
            sage: RR(1.579)._sage_input_(sib_np, True)
            {atomic:1.579}
            sage: RR60(1.579)._sage_input_(sib, True)
            {atomic:1.5790000000000000008}
            sage: RR60(1.579)._sage_input_(sib_np, True)
            {call: {call: {atomic:RealField}({atomic:60})}({atomic:'1.5790000000000000008'})}
            sage: RR(1.579)._sage_input_(sib_np, False)
            {call: {atomic:RR}({atomic:1.579})}
            sage: RR(1.579)._sage_input_(sib_np, 2)
            {atomic:1.579}
            sage: RealField(150)(pi)._sage_input_(sib, True)
            {atomic:3.1415926535897932384626433832795028841971694008}
            sage: RealField(150)(pi)._sage_input_(sib_np, True)
            {call: {call: {atomic:RealField}({atomic:150})}({atomic:'3.1415926535897932384626433832795028841971694008'})}
        """
        # We have a bewildering array of conditions to deal with:
        # 1) number, or NaN or infinity
        # 2) rounding direction: up, down, or nearest
        # 3) preparser enabled: yes, no, or maybe
        # 4) is this number equal to some Python float: yes or no
        # 5) coerced

        # First, handle NaN and infinity
        if not mpfr_number_p(self.value):
            if mpfr_inf_p(self.value):
                v = sib.name('Infinity')
            else:
                v = sib.name('NaN')
            v = sib(self._parent)(v)
            if mpfr_sgn(self.value) < 0:
                v = -v
            return v

        from sage.rings.integer_ring import ZZ

        cdef mpfr_rnd_t rnd = (<RealField>self._parent).rnd

        cdef bint negative = mpfr_sgn(self.value) < 0
        if negative:
            self = -self

        # There are five possibilities for printing this floating-point
        # number, ordered from prettiest to ugliest (IMHO).
        # 1) An integer: 42
        # 2) A simple literal: 3.14159
        # 3) A coerced integer: RR(42)
        # 4) A coerced literal: RR(3.14159)
        # 5) A coerced string literal: RR('3.14159')

        # To use choice 1 or choice 3, this number must be an integer.
        cdef bint can_use_int_literal = \
            self.abs() < (Integer(1) << self.prec()) and self in ZZ

        # If "not coerced", then we will introduce a conversion
        # ourselves.  If coerced==2, then there will be an external conversion.
        # On the other hand, if coerced==1 (or True), then we only
        # have a coercion, not a conversion; which means we need to read
        # in a number with at least the number of bits we need.
        will_convert = (coerced == 2 or not coerced)

        self_str = self.str(truncate=False,
                            skip_zeroes=(will_convert or self.prec() <= 53))

        # To use choice 2 or choice 4, we must be able to read
        # numbers of this precision as a literal.  We support this
        # only for the default rounding mode; "pretty" output for
        # other rounding modes is a lot of work for very little gain
        # (since other rounding modes are very rarely used).
        # (One problem is that we don't know whether it will be the
        # positive or negative value that will be coerced into the
        # desired parent; for example, this differs between "x^2 - 1.3*x"
        # and "-1.3*x".)
        cdef bint can_use_float_literal = \
            rnd == GMP_RNDN and (sib.preparse() or
                                 ((will_convert or self.prec() <= 53) and
                                  self._parent(float(self_str)) == self))

        if can_use_int_literal or can_use_float_literal:
            if can_use_int_literal:
                v = sib.int(self._integer_())
            else:
                v = sib.float_str(self_str)
            if not coerced and (can_use_int_literal or not sib.preparse() or create_RealNumber(self_str).prec() != self.prec()):
                v = sib(self.parent())(v)
        else:
            if rnd == GMP_RNDN:
                s = self_str
            else:
                # This is tricky.  str() uses mpfr_get_str() with
                # reqdigits=0; this guarantees to give enough digits
                # to recreate the input, if we print and read with
                # round-to-nearest.  However, we are not going to
                # read with round-to-nearest, so we might need more digits.
                # If we're going to read with round-down, then we need
                # to print with round-up; and we'll use one more bit
                # to make sure we have enough digits.
                # Since we always read nonnegative numbers, reading with
                # RNDZ is the same as reading with RNDD.
                if rnd == GMP_RNDD or rnd == GMP_RNDZ:
                    fld = RealField(self.prec() + 1, rnd='RNDU')
                else:
                    fld = RealField(self.prec() + 1, rnd='RNDD')
                s = fld(self).str(truncate=False)
            v = sib(self.parent())(sib.float_str(repr(s)))

        if negative:
            v = -v

        return v

    def __hash__(self):
        """
        Returns the hash of self, which coincides with the python float
        (and often int) type.

        This has the drawback that two very close high precision numbers
        will have the same hash, but allows them to play nicely with other
        real types.

        EXAMPLE::

            sage: hash(RR(1.2)) == hash(1.2r)
            True
        """
        return hash(float(self))

    def _im_gens_(self, codomain, im_gens):
        return codomain(self) # since 1 |--> 1

    def real(self):
        """
        Return the real part of self.

        (Since self is a real number, this simply returns self.)
        """
        return self

    def parent(self):
        """
        EXAMPLES::

            sage: R = RealField()
            sage: a = R('1.2456')
            sage: a.parent()
            Real Field with 53 bits of precision
        """
        return self._parent

    def str(self, int base=10, no_sci=None, e=None, int truncate=1, bint skip_zeroes=0):
        """
        INPUT:


        -  ``base`` - base for output

        -  ``no_sci`` - if 2, never print using scientific
           notation; if 1 or True, print using scientific notation only for
           very large or very small numbers; if 0 or False always print with
           scientific notation; if None (the default), print how the parent
           prints.

        -  ``e`` - symbol used in scientific notation; defaults to 'e' for
           base=10, and '@' otherwise

        -  ``truncate`` - if True, round off the last digits in
           printing to lessen confusing base-2 roundoff issues.

        -  ``skip_zeroes`` - if True, skip trailing zeroes in mantissa

        EXAMPLES::

            sage: a = 61/3.0; a
            20.3333333333333
            sage: a.str(truncate=False)
            '20.333333333333332'
            sage: a.str(2)
            '10100.010101010101010101010101010101010101010101010101'
            sage: a.str(no_sci=False)
            '2.03333333333333e1'
            sage: a.str(16, no_sci=False)
            '1.4555555555555@1'
            sage: b = 2.0^99
            sage: b.str()
            '6.33825300114115e29'
            sage: b.str(no_sci=False)
            '6.33825300114115e29'
            sage: b.str(no_sci=True)
            '6.33825300114115e29'
            sage: c = 2.0^100
            sage: c.str()
            '1.26765060022823e30'
            sage: c.str(no_sci=False)
            '1.26765060022823e30'
            sage: c.str(no_sci=True)
            '1.26765060022823e30'
            sage: c.str(no_sci=2)
            '1267650600228230000000000000000.'
            sage: 0.5^53
            1.11022302462516e-16
            sage: 0.5^54
            5.55111512312578e-17
            sage: (0.01).str()
            '0.0100000000000000'
            sage: (0.01).str(skip_zeroes=True)
            '0.01'
            sage: (-10.042).str()
            '-10.0420000000000'
            sage: (-10.042).str(skip_zeroes=True)
            '-10.042'
            sage: (389.0).str(skip_zeroes=True)
            '389.'
        """
        if base < 2 or base > 36:
            raise ValueError, "the base (=%s) must be between 2 and 36"%base
        if mpfr_nan_p(self.value):
            if base >= 24:
                return "@NaN@"
            else:
                return "NaN"
        elif mpfr_inf_p(self.value):
            if mpfr_sgn(self.value) > 0:
                return "+infinity"
            else:
                return "-infinity"

        if e is None:
            if base > 10:
                e = '@'
            else:
                e = 'e'

        cdef char *s
        cdef mp_exp_t exponent

        cdef int reqdigits

        reqdigits = 0

        if base == 10 and truncate:

            # This computes reqdigits == floor(log_{10}(2^(b-1))),
            # which is the number of *decimal* digits that are
            # "right", given that the last binary bit of the binary
            # number can be off.  That is, if this real is within a
            # relative error of 2^(-b) of an exact decimal with
            # reqdigits digits, that decimal will be returned.
            # This is equivalent to saying that exact decimals with
            # reqdigits digits differ by at least 2*2^(-b) (relative).

            # (Depending on the precision and the exact number involved,
            # adjacent exact decimals can differ by far more than 2*2^(-b)
            # (relative).)

            # This avoids the confusion a lot of people have with the last
            # 1-2 binary digits being wrong due to rounding coming from
            # representating numbers in binary.

            reqdigits = <int>(((<RealField>self._parent).__prec - 1) * 0.3010299956)
            if reqdigits <= 1: reqdigits = 2

        _sig_on
        s = mpfr_get_str(<char*>0, &exponent, base, reqdigits,
                         self.value, (<RealField>self._parent).rnd)
        _sig_off
        if s == <char*> 0:
            raise RuntimeError, "Unable to convert an mpfr number to a string."
        t = str(s)
        mpfr_free_str(s)

        if skip_zeroes:
            t = _re_skip_zeroes.match(t).group(1)

        cdef int digits
        digits = len(t)
        if t[0] == "-":
            digits = digits - 1

        if no_sci is None:
            no_sci = not (<RealField>self._parent).sci_not

        if no_sci is True and ( abs(exponent-1) >=6 ):
            no_sci = False

        if no_sci==False:
            if t[0] == "-":
                return "-%s.%s%s%s"%(t[1:2], t[2:], e, exponent-1)
            return "%s.%s%s%s"%(t[0], t[1:], e, exponent-1)

        lpad = ''

        if exponent <= 0:
            n = len(t)
            lpad = '0.' + '0'*abs(exponent)
        else:
            n = exponent

        if t[0] == '-':
            lpad = '-' + lpad
            t = t[1:]
        z = lpad + str(t[:n])
        w = t[n:]

        if len(w) > 0 and '.' not in z:
            z = z + ".%s"%w
        elif exponent > 0:
            z = z + '0'*(n-len(t))
        if '.' not in z:
            z = z + "."

        return z

    def __copy__(self):
        """
        Return copy of self - since self is immutable, we just return self
        again.

        EXAMPLES::

            sage: a = 3.5
            sage: copy(a) is  a
            True
        """
        return self    # since object is immutable.

    def _integer_(self, Z=None):
        """
        If this floating-point number is actually an integer, return that
        integer. Otherwise, raise an exception.

        EXAMPLES::

            sage: ZZ(237.0)
            237
            sage: ZZ(0.0/0.0)
            Traceback (most recent call last):
            ...
            TypeError: Attempt to coerce non-integral RealNumber to Integer
            sage: ZZ(1.0/0.0)
            Traceback (most recent call last):
            ...
            TypeError: Attempt to coerce non-integral RealNumber to Integer
            sage: ZZ(-123456789.0)
            -123456789
            sage: ZZ(RealField(300)(2.0)^290)
            1989292945639146568621528992587283360401824603189390869761855907572637988050133502132224
            sage: ZZ(-2345.67)
            Traceback (most recent call last):
            ...
            TypeError: Attempt to coerce non-integral RealNumber to Integer
        """
        cdef Integer n

        if mpfr_integer_p(self.value):
            n = PY_NEW(Integer)
            mpfr_get_z(n.value, self.value, GMP_RNDN)
            return n

        raise TypeError, "Attempt to coerce non-integral RealNumber to Integer"

    def integer_part(self):
        """
        If in decimal this number is written n.defg, returns n.

        OUTPUT: a Sage Integer

        EXAMPLE::

            sage: a = 119.41212
            sage: a.integer_part()
            119
            sage: a = -123.4567
            sage: a.integer_part()
            -123

        A big number with no decimal point::

            sage: a = RR(10^17); a
            1.00000000000000e17
            sage: a.integer_part()
            100000000000000000
        """
        if not mpfr_number_p(self.value):
            raise ValueError, 'Cannot convert infinity or NaN to SAGE Integer'

        cdef Integer z = Integer()
        mpfr_get_z(z.value, self.value, GMP_RNDZ)
        return z

    def fp_rank(self):
        r"""
        Returns the floating-point rank of this number. That is, if you
        list the floating-point numbers of this precision in order, and
        number them starting with 0.0 `\rightarrow` 0 and extending
        the list to positive and negative infinity, returns the number
        corresponding to this floating-point number.

        EXAMPLES::

            sage: RR(0).fp_rank()
            0
            sage: RR(0).nextabove().fp_rank()
            1
            sage: RR(0).nextbelow().nextbelow().fp_rank()
            -2
            sage: RR(1).fp_rank()
            4835703278458516698824705
            sage: RR(-1).fp_rank()
            -4835703278458516698824705
            sage: RR(1).fp_rank() - RR(1).nextbelow().fp_rank()
            1
            sage: RR(-infinity).fp_rank()
            -9671406552413433770278913
            sage: RR(-infinity).fp_rank() - RR(-infinity).nextabove().fp_rank()
            -1
        """
        if mpfr_nan_p(self.value):
            raise ValueError, "Cannot compute fp_rank of NaN"

        cdef Integer z = PY_NEW(Integer)

        cdef mp_exp_t EXP_MIN = -(1<<30) + 1
        cdef mp_exp_t EXP_MAX = (1<<30) - 1
        # fp_rank(0.0) = 0
        # fp_rank(m*2^e-p) = (m-2^{p-1})+(e-EXP_MIN)*2^{p-1}+1
        #                  = m+(e-EXP_MIN-1)*2^{p-1}+1
        # fp_rank(infinity) = (EXP_MAX+1-EXP_MIN)*2^{p-1}+1
        # fp_rank(-x) = -fp_rank(x)

        cdef int sgn = mpfr_sgn(self.value)

        if sgn == 0:
            return z

        cdef int prec = (<RealField>self._parent).__prec

        if mpfr_inf_p(self.value):
            mpz_set_ui(z.value, EXP_MAX+1-EXP_MIN)
            mpz_mul_2exp(z.value, z.value, prec-1)
            mpz_add_ui(z.value, z.value, 1)
            if sgn < 0:
                mpz_neg(z.value, z.value)
            return z

        cdef mpz_t mantissa
        mpz_init(mantissa)
        cdef mp_exp_t exponent = mpfr_get_z_exp(mantissa, self.value)
        mpz_set_si(z.value, exponent+prec-EXP_MIN-1)
        mpz_mul_2exp(z.value, z.value, prec-1)
        mpz_add_ui(z.value, z.value, 1)
        if sgn > 0:
            mpz_add(z.value, z.value, mantissa)
        else:
            mpz_sub(z.value, z.value, mantissa)
            mpz_neg(z.value, z.value)
        mpz_clear(mantissa)
        return z

    def fp_rank_delta(self, RealNumber other):
        r"""
        Return the floating-point rank delta between ``self``
        and ``other``. That is, if the return value is
        positive, this is the number of times you have to call
        ``.nextabove()`` to get from ``self`` to
        ``other``.

        EXAMPLES::

            sage: [x.fp_rank_delta(x.nextabove()) for x in
            ...      (RR(-infinity), -1.0, 0.0, 1.0, RR(pi), RR(infinity))]
            [1, 1, 1, 1, 1, 0]

        In the 2-bit floating-point field, one subsegment of the
        floating-point numbers is: 1, 1.5, 2, 3, 4, 6, 8, 12, 16, 24, 32

        ::

            sage: R2 = RealField(2)
            sage: R2(1).fp_rank_delta(R2(2))
            2
            sage: R2(2).fp_rank_delta(R2(1))
            -2
            sage: R2(1).fp_rank_delta(R2(1048576))
            40
            sage: R2(24).fp_rank_delta(R2(4))
            -5
            sage: R2(-4).fp_rank_delta(R2(-24))
            -5

        There are lots of floating-point numbers around 0::

            sage: R2(-1).fp_rank_delta(R2(1))
            4294967298
        """

        # We create the API for forward compatibility, because it can have
        # a (somewhat) more efficient implementation than this; but for now,
        # we just go with the stupid implementation.
        return other.fp_rank() - self.fp_rank()

    ########################
    #   Basic Arithmetic
    ########################

    cpdef ModuleElement _add_(self, ModuleElement other):
        """
        Add two real numbers with the same parent.

        EXAMPLES::

            sage: R = RealField()
            sage: R(-1.5) + R(2.5)
            1.00000000000000
        """
        cdef RealNumber x
        x = self._new()
        mpfr_add(x.value, self.value, (<RealNumber>other).value, (<RealField>self._parent).rnd)
        return x

    def __invert__(self):
        return self._parent(1) / self

    cpdef ModuleElement _sub_(self, ModuleElement right):
        """
        Subtract two real numbers with the same parent.

        EXAMPLES::

            sage: R = RealField()
            sage: R(-1.5) - R(2.5)
            -4.00000000000000
        """
        cdef RealNumber x
        x = self._new()
        mpfr_sub(x.value, self.value, (<RealNumber>right).value, (<RealField> self._parent).rnd)
        return x

    cpdef RingElement _mul_(self, RingElement right):
        """
        Multiply two real numbers with the same parent.

        EXAMPLES::

            sage: R = RealField()
            sage: R(-1.5) * R(2.5)
            -3.75000000000000

        If two elements have different precision, arithmetic operations are
        performed after coercing to the lower precision.

        ::

            sage: R20 = RealField(20)
            sage: R100 = RealField(100)
            sage: a = R20('393.3902834028345')
            sage: b = R100('393.3902834028345')
            sage: a
            393.39
            sage: b
            393.39028340283450000000000000
            sage: a*b
            154760.
            sage: b*a
            154760.
            sage: parent(b*a)
            Real Field with 20 bits of precision
        """
        cdef RealNumber x
        x = self._new()
        mpfr_mul(x.value, self.value, (<RealNumber>right).value, (<RealField>self._parent).rnd)
        return x


    cpdef RingElement _div_(self, RingElement right):
        """
        Divide self by other, where both are real numbers with the same
        parent.

        EXAMPLES::

            sage: RR(1)/RR(3)
            0.333333333333333
            sage: RR(1)/RR(0)
            +infinity

        ::

            sage: R = RealField()
            sage: R(-1.5) / R(2.5)
            -0.600000000000000
        """
        cdef RealNumber x
        x = self._new()
        mpfr_div((<RealNumber>x).value, self.value,
                 (<RealNumber>right).value, (<RealField>self._parent).rnd)
        return x

    cpdef ModuleElement _neg_(self):
        cdef RealNumber x
        x = self._new()
        mpfr_neg(x.value, self.value, (<RealField>self._parent).rnd)
        return x

    def __abs__(self):
        return self.abs()

    cdef RealNumber abs(RealNumber self):
        cdef RealNumber x
        x = self._new()
        mpfr_abs(x.value, self.value, (<RealField>self._parent).rnd)
        return x

    # Bit shifting
    def _lshift_(RealNumber self, n):
        cdef RealNumber x
        if n > sys.maxint:
            raise OverflowError, "n (=%s) must be <= %s"%(n, sys.maxint)
        x = self._new()
        mpfr_mul_2exp(x.value, self.value, n, (<RealField>self._parent).rnd)
        return x

    def __lshift__(x, y):
        """
        EXAMPLES::

            sage: 1.0 << 32
            4.29496729600000e9
            sage: 1.5 << 2.5
            Traceback (most recent call last):
            ...
            TypeError: unsupported operands for <<
        """
        if not PY_TYPE_CHECK(x, RealNumber):
            raise TypeError, "unsupported operands for <<"
        try:
            return x._lshift_(Integer(y))
        except TypeError:
            raise TypeError, "unsupported operands for <<"

    def _rshift_(RealNumber self, n):
        if n > sys.maxint:
            raise OverflowError, "n (=%s) must be <= %s"%(n, sys.maxint)
        cdef RealNumber x
        x = self._new()
        mpfr_div_2exp(x.value, self.value, n, (<RealField>self._parent).rnd)
        return x

    def __rshift__(x, y):
        """
        EXAMPLES::

            sage: 1024.0 >> 7
            8.00000000000000
            sage: 1.5 >> 2.5
            Traceback (most recent call last):
            ...
            TypeError: unsupported operands for >>
        """
        if not PY_TYPE_CHECK(x, RealNumber):
            raise TypeError, "unsupported operands for >>"
        try:
            return x._rshift_(Integer(y))
        except TypeError:
            raise TypeError, "unsupported operands for >>"


    def multiplicative_order(self):
        if self == 1:
            return 1
        elif self == -1:
            return -1
        return sage.rings.infinity.infinity

    def sign(self):
        return mpfr_sgn(self.value)

    def prec(self):
        return (<RealField>self._parent).__prec

    def conjugate(self):
        """
        Return the complex conjugate of this real number, which is the
        number itself.

        EXAMPLES:
            sage: x = RealField(100)(1.238)
            sage: x.conjugate()
            1.2380000000000000000000000000
        """
        return self

    def ulp(self):
        """
        Returns the unit of least precision of self, which is the weight of
        the least significant bit of self. Unless self is exactly a power of
        two, it is gap between this number and the next closest distinct
        number that can be represented.

        EXAMPLES:
            sage: a = 1.0
            sage: a + a.ulp() == a
            False
            sage: a + a.ulp()/2 == a
            True

            sage: a = RealField(500).pi()
            sage: b = a + a.ulp()
            sage: (a+b)/2 in [a,b]
            True

            sage: a = RR(infinity)
            sage: a.ulp()
            +infinity
            sage: (-a).ulp()
            +infinity
            sage: a = RR('nan')
            sage: a.ulp() is a
            True
        """
        cdef RealNumber x
        if mpfr_nan_p(self.value):
            return self
        elif mpfr_inf_p(self.value):
            if mpfr_sgn(self.value) == 1:
                return self
            else:
                return -self
        else:
            x = self._new()
            mpfr_set(x.value, self.value, (<RealField>self._parent).rnd)
            if mpfr_sgn(self.value) == 1:
                mpfr_nextabove(x.value)
            else:
                mpfr_nextbelow(x.value)
            mpfr_sub(x.value, x.value, self.value, (<RealField>self._parent).rnd)
            mpfr_abs(x.value, x.value, (<RealField>self._parent).rnd)
            return x


    ###################
    # Rounding etc
    ###################

    def __mod__(left, right):
        """
        Return the value of left - n*right, rounded according to the rounding
        mode of the parent, where n is the integer quotient of x divided by y.
        The integer n is rounded toward the nearest integer (ties rounded
        to even).

        EXAMPLES:
            sage: 10.0 % 2r
            0.000000000000000
            sage: 20r % .5
            0.000000000000000

            sage 1.1 % 0.25
            0.100000000000000
        """
        if not PY_TYPE_CHECK(left, Element) or \
                not PY_TYPE_CHECK(right, Element) or \
                (<Element>left)._parent is not (<Element>right)._parent:
            from sage.structure.element import canonical_coercion
            left, right = canonical_coercion(left, right)
            return left % right

        cdef RealNumber x
        x = (<RealNumber>left)._new()
        mpfr_remainder (x.value, (<RealNumber>left).value,
                (<RealNumber>right).value,
                (<RealField>(<RealNumber>left)._parent).rnd)
        return x

    def round(self):
        """
         Rounds self to the nearest integer. The rounding mode of the parent
         field has no effect on this function.

         EXAMPLES::

             sage: RR(0.49).round()
             0
             sage: RR(0.5).round()
             1
             sage: RR(-0.49).round()
             0
             sage: RR(-0.5).round()
             -1
         """
        cdef RealNumber x
        x = self._new()
        mpfr_round(x.value, self.value)
        return x.integer_part()

    def floor(self):
        """
        Returns the floor of this number

        EXAMPLES::

            sage: R = RealField()
            sage: (2.99).floor()
            2
            sage: (2.00).floor()
            2
            sage: floor(RR(-5/2))
            -3
            sage: floor(RR(+infinity))
            Traceback (most recent call last):
            ...
            ValueError: Calling floor() on infinity or NaN
        """
        cdef RealNumber x
        if not mpfr_number_p(self.value):
            raise ValueError, 'Calling floor() on infinity or NaN'
        x = self._new()
        mpfr_floor(x.value, self.value)
        return x.integer_part()

    def ceil(self):
        """
        Returns the ceiling of this number

        OUTPUT: integer

        EXAMPLES::

            sage: (2.99).ceil()
            3
            sage: (2.00).ceil()
            2
            sage: (2.01).ceil()
            3

        ::

            sage: ceil(10^16 * 1.0)
            10000000000000000
            sage: ceil(10^17 * 1.0)
            100000000000000000
            sage: ceil(RR(+infinity))
            Traceback (most recent call last):
            ...
            ValueError: Calling ceil() on infinity or NaN
        """
        cdef RealNumber x
        if not mpfr_number_p(self.value):
            raise ValueError, 'Calling ceil() on infinity or NaN'
        x = self._new()
        mpfr_ceil(x.value, self.value)
        return x.integer_part()

    def ceiling(self):
        return self.ceil()

    def trunc(self):
        """
        Truncates this number

        EXAMPLES::

            sage: (2.99).trunc()
            2
            sage: (-0.00).trunc()
            0
            sage: (0.00).trunc()
            0
        """
        cdef RealNumber x
        x = self._new()
        mpfr_trunc(x.value, self.value)
        return x.integer_part()

    def frac(self):
        """
        frac returns a real number > -1 and < 1. it satisfies the relation: x =
        x.trunc() + x.frac()

        EXAMPLES::

            sage: (2.99).frac()
            0.990000000000000
            sage: (2.50).frac()
            0.500000000000000
            sage: (-2.79).frac()
            -0.790000000000000
        """
        cdef RealNumber x
        x = self._new()
        mpfr_frac(x.value, self.value, (<RealField>self._parent).rnd)
        return x

    def nexttoward(self, other):
        """
        Returns the floating-point number adjacent to self which is closer
        to other. If self or other is NaN, returns NaN; if self equals
        other, returns self.

        EXAMPLES::

            sage: (1.0).nexttoward(2).str(truncate=False)
            '1.0000000000000002'
            sage: (1.0).nexttoward(RR('-infinity')).str(truncate=False)
            '0.99999999999999989'
            sage: RR(infinity).nexttoward(0)
            2.09857871646739e323228496
            sage: RR(pi).str(truncate=False)
            '3.1415926535897931'
            sage: RR(pi).nexttoward(22/7).str(truncate=False)
            '3.1415926535897936'
            sage: RR(pi).nexttoward(21/7).str(truncate=False)
            '3.1415926535897927'
        """
        cdef RealNumber other_rn
        if PY_TYPE_CHECK(other, RealNumber):
            other_rn = other
        else:
            other_rn = self._parent(other)

        cdef RealNumber x
        x = self._new()

        mpfr_set(x.value, self.value, GMP_RNDN)
        mpfr_nexttoward(x.value, other_rn.value)

        return x

    def nextabove(self):
        """
        Returns the next floating-point number larger than self.

        EXAMPLES::

            sage: RR('-infinity').nextabove()
            -2.09857871646739e323228496
            sage: RR(0).nextabove()
            2.38256490488795e-323228497
            sage: RR('+infinity').nextabove()
            +infinity
            sage: RR(-sqrt(2)).str(truncate=False)
            '-1.4142135623730951'
            sage: RR(-sqrt(2)).nextabove().str(truncate=False)
            '-1.4142135623730949'
        """

        cdef RealNumber x
        x = self._new()
        mpfr_set(x.value, self.value, GMP_RNDN)
        mpfr_nextabove(x.value)

        return x

    def nextbelow(self):
        """
        Returns the next floating-point number smaller than self.

        EXAMPLES::

            sage: RR('-infinity').nextbelow()
            -infinity
            sage: RR(0).nextbelow()
            -2.38256490488795e-323228497
            sage: RR('+infinity').nextbelow()
            2.09857871646739e323228496
            sage: RR(-sqrt(2)).str(truncate=False)
            '-1.4142135623730951'
            sage: RR(-sqrt(2)).nextbelow().str(truncate=False)
            '-1.4142135623730954'
        """

        cdef RealNumber x
        x = self._new()
        mpfr_set(x.value, self.value, GMP_RNDN)
        mpfr_nextbelow(x.value)

        return x

    ###########################################
    # Conversions
    ###########################################

    def __float__(self):
        return mpfr_get_d(self.value, (<RealField>self._parent).rnd)

    def _rpy_(self):
        """
        Returns self.__float__() for rpy to convert into the
        appropriate R object.

        EXAMPLES::

            sage: n = RealNumber(2.0)
            sage: n._rpy_()
            2.0
            sage: type(n._rpy_())
            <type 'float'>
        """
        return self.__float__()

    def __int__(self):
        """
        Returns integer truncation of this real number.
        """
        if not mpfr_number_p(self.value):
            raise ValueError, 'Cannot convert infinity or NaN to Python int'

        cdef Integer z = Integer()
        mpfr_get_z(z.value, self.value, GMP_RNDZ)
        return z.__int__()

    def __long__(self):
        """
        Returns long integer truncation of this real number.
        """
        if not mpfr_number_p(self.value):
            raise ValueError, 'Cannot convert infinity or NaN to Python long'

        cdef Integer z = Integer()
        mpfr_get_z(z.value, self.value, GMP_RNDZ)
        return z.__long__()

    def __complex__(self):
        return complex(float(self))

    def _complex_number_(self):
        import sage.rings.complex_field
        return sage.rings.complex_field.ComplexField(self.prec())(self)

    def _axiom_(self, axiom):
        """
        Returns self as a floating point number in Axiom.

        EXAMPLES::

            sage: R = RealField(100)
            sage: R(pi)
            3.1415926535897932384626433833
            sage: axiom(R(pi))  # optional - axiom
            3.1415926535 8979323846 26433833
            sage: fricas(R(pi)) # optional - fricas
            3.1415926535 8979323846 26433833

        """
        prec = self.parent().prec()

        #Set the precision in Axiom
        old_prec = axiom('precision(%s)$Float'%prec)
        res = axiom('%s :: Float'%self.exact_rational())
        axiom.eval('precision(%s)$Float'%old_prec)

        return res

    _fricas_ = _axiom_

    def _pari_(self):
        """
        Returns self as a Pari floating-point number.

        EXAMPLES::

            sage: RR(2.0)._pari_()
            2.00000000000000

        The current Pari precision affects the printing of this number, but
        Pari does maintain the same 250-bit number on both 32-bit and
        64-bit platforms.

        ::

            sage: RealField(250).pi()._pari_()
            3.14159265358979
            sage: RR(0.0)._pari_()
            0.E-19
            sage: RR(-1.234567)._pari_()
            -1.23456700000000
            sage: RR(2.0).sqrt()._pari_()
            1.41421356237310
            sage: RR(2.0).sqrt()._pari_().python()
            1.41421356237309515
            sage: RR(2.0).sqrt()._pari_().python().prec()
            64
            sage: RealField(70)(pi)._pari_().python().prec()
            96                                         # 32-bit
            128                                        # 64-bit
            sage: for i in xrange(1, 1000):
            ...       assert(RR(i).sqrt() == RR(i).sqrt()._pari_().python())
        """
        # return sage.libs.pari.all.pari.new_with_bits_prec(str(self), (<RealField>self._parent).__prec)

        # This uses interfaces of MPFR and Pari which are documented
        # (and not marked subject-to-change).  It could be faster
        # by using internal interfaces of MPFR, which are documented
        # as subject-to-change.

        if mpfr_nan_p(self.value) or mpfr_inf_p(self.value):
            raise ValueError, 'Cannot convert NaN or infinity to Pari float'

        cdef int wordsize

        if sage.misc.misc.is_64_bit:
            wordsize = 64
        else:
            wordsize = 32

        cdef int prec
        prec = (<RealField>self._parent).__prec

        # We round up the precision to the nearest multiple of wordsize.
        cdef int rounded_prec
        rounded_prec = (self.prec() + wordsize - 1) & ~(wordsize - 1)

        # Yes, assigning to self works fine, even in Pyrex.
        if rounded_prec > prec:
            self = RealField(rounded_prec)(self)

        # Now we can extract the mantissa, and it will be normalized
        # (the most significant bit of the most significant word will be 1).
        cdef mpz_t mantissa
        cdef mp_exp_t exponent
        mpz_init(mantissa)

        exponent = mpfr_get_z_exp(mantissa, self.value)

        cdef GEN pari_float
        pari_float = cgetr(2 + rounded_prec / wordsize)

        mpz_export(&pari_float[2], NULL, 1, wordsize/8, 0, 0, mantissa)

        if mpfr_zero_p(self.value):
            setexpo(pari_float, -rounded_prec)
        else:
            setexpo(pari_float, exponent + rounded_prec - 1)
        setsigne(pari_float, mpfr_sgn(self.value))

        cdef PariInstance P
        P = sage.libs.pari.all.pari

        gen = P.new_gen(pari_float)

        mpz_clear(mantissa)

        return gen

    def exact_rational(self):
        """
        Returns the exact rational representation of this floating-point
        number.

        EXAMPLES::

            sage: RR(0).exact_rational()
            0
            sage: RR(1/3).exact_rational()
            6004799503160661/18014398509481984
            sage: RR(37/16).exact_rational()
            37/16
            sage: RR(3^60).exact_rational()
            42391158275216203520420085760
            sage: RR(3^60).exact_rational() - 3^60
            6125652559
            sage: RealField(5)(-pi).exact_rational()
            -25/8

        TESTS::

            sage: RR('nan').exact_rational()
            Traceback (most recent call last):
            ...
            ValueError: Cannot convert NaN or infinity to rational number
            sage: RR('-infinity').exact_rational()
            Traceback (most recent call last):
            ...
            ValueError: Cannot convert NaN or infinity to rational number
        """
        if not mpfr_number_p(self.value):
            raise ValueError, 'Cannot convert NaN or infinity to rational number'

        cdef Integer mantissa = Integer()
        cdef mp_exp_t exponent

        if not mpfr_number_p(self.value):
            raise ValueError, 'Calling exact_rational() on infinity or NaN'

        if mpfr_sgn(self.value) == 0:
            return Rational(0)

        exponent = mpfr_get_z_exp(mantissa.value, self.value)

        return Rational(mantissa) * Integer(2) ** exponent

    def simplest_rational(self):
        """
        Returns the simplest rational which is equal to self (in the Sage
        sense). Recall that Sage defines the equality operator by coercing
        both sides to a single type and then comparing; thus, this finds
        the simplest rational which (when coerced to this RealField) is
        equal to self.

        Given rationals a/b and c/d (both in lowest terms), the former is
        simpler if b<d or if b==d and `|a|<|c|`.

        The effect of rounding modes is slightly counter-intuitive.
        Consider the case of round-toward-minus-infinity. This rounding is
        performed when coercing a rational to a floating-point number; so
        the simplest_rational() of a round-to-minus-infinity number will
        be either exactly equal to or slightly larger than the number.

        EXAMPLES::

            sage: RRd = RealField(53, rnd='RNDD')
            sage: RRz = RealField(53, rnd='RNDZ')
            sage: RRu = RealField(53, rnd='RNDU')
            sage: def check(x):
            ...       rx = x.simplest_rational()
            ...       assert(x == rx)
            ...       return rx
            sage: RRd(1/3) < RRu(1/3)
            True
            sage: check(RRd(1/3))
            1/3
            sage: check(RRu(1/3))
            1/3
            sage: check(RRz(1/3))
            1/3
            sage: check(RR(1/3))
            1/3
            sage: check(RRd(-1/3))
            -1/3
            sage: check(RRu(-1/3))
            -1/3
            sage: check(RRz(-1/3))
            -1/3
            sage: check(RR(-1/3))
            -1/3
            sage: check(RealField(20)(pi))
            355/113
            sage: check(RR(pi))
            245850922/78256779
            sage: check(RR(2).sqrt())
            131836323/93222358
            sage: check(RR(1/2^210))
            1/1645504557321205859467264516194506011931735427766374553794641921
            sage: check(RR(2^210))
            1645504557321205950811116849375918117252433820865891134852825088
            sage: (RR(17).sqrt()).simplest_rational()^2 - 17
            -1/348729667233025
            sage: (RR(23).cube_root()).simplest_rational()^3 - 23
            -1404915133/264743395842039084891584
            sage: RRd5 = RealField(5, rnd='RNDD')
            sage: RRu5 = RealField(5, rnd='RNDU')
            sage: RR5 = RealField(5)
            sage: below1 = RR5(1).nextbelow()
            sage: check(RRd5(below1))
            31/32
            sage: check(RRu5(below1))
            16/17
            sage: check(below1)
            21/22
            sage: below1.exact_rational()
            31/32
            sage: above1 = RR5(1).nextabove()
            sage: check(RRd5(above1))
            10/9
            sage: check(RRu5(above1))
            17/16
            sage: check(above1)
            12/11
            sage: above1.exact_rational()
            17/16
            sage: check(RR(1234))
            1234
            sage: check(RR5(1234))
            1185
            sage: check(RR5(1184))
            1120
            sage: RRd2 = RealField(2, rnd='RNDD')
            sage: RRu2 = RealField(2, rnd='RNDU')
            sage: RR2 = RealField(2)
            sage: check(RR2(8))
            7
            sage: check(RRd2(8))
            8
            sage: check(RRu2(8))
            7
            sage: check(RR2(13))
            11
            sage: check(RRd2(13))
            12
            sage: check(RRu2(13))
            13
            sage: check(RR2(16))
            14
            sage: check(RRd2(16))
            16
            sage: check(RRu2(16))
            13
            sage: check(RR2(24))
            21
            sage: check(RRu2(24))
            17
            sage: check(RR2(-24))
            -21
            sage: check(RRu2(-24))
            -24

        TESTS::

            sage: RR('nan').simplest_rational()
            Traceback (most recent call last):
            ...
            ValueError: Cannot convert NaN or infinity to rational number
            sage: RR('-infinity').simplest_rational()
            Traceback (most recent call last):
            ...
            ValueError: Cannot convert NaN or infinity to rational number
        """
        if not mpfr_number_p(self.value):
            raise ValueError, 'Cannot convert NaN or infinity to rational number'

        if mpfr_zero_p(self.value):
            return Rational(0)

        from real_mpfi import RealIntervalField

        cdef mpfr_rnd_t rnd = (<RealField>self._parent).rnd
        cdef int prec = (<RealField>self._parent).__prec

        cdef RealNumber low, high
        cdef int odd

        if rnd == GMP_RNDN:
            # hp == "high precision"
            hp_field = RealField(prec + 1)
            hp_val = hp_field(self)
            hp_intv_field = RealIntervalField(prec + 1)
            low = hp_val.nextbelow()
            high = hp_val.nextabove()
            hp_intv = hp_intv_field(low, high)
            # In GMP_RNDN mode, we round to nearest, preferring even mantissas
            # if we are exactly halfway between representable floats.
            # Thus, the values low and high will round to self iff the
            # mantissa of self is even.  (Note that this only matters
            # if low or high is an integer; if they are not integers,
            # then self is simpler than either low or high.)
            # Is there a better (faster) way to check this?
            odd = self._parent(low) != self
            return hp_intv.simplest_rational(low_open=odd, high_open=odd)

        if rnd == GMP_RNDZ:
            if mpfr_sgn(self.value) > 0:
                rnd = GMP_RNDD
            else:
                rnd = GMP_RNDU

        intv_field = RealIntervalField(prec)

        if rnd == GMP_RNDD:
            intv = intv_field(self, self.nextabove())
            return intv.simplest_rational(high_open = True)
        if rnd == GMP_RNDU:
            intv = intv_field(self.nextbelow(), self)
            return intv.simplest_rational(low_open = True)

    def nearby_rational(self, max_error=None, max_denominator=None):
        """
        Find a rational near to self. Exactly one of max_error or
        max_denominator must be specified. If max_error is specified,
        then this returns the simplest rational in the range
        [self-max_error .. self+max_error]. If max_denominator is
        specified, then this returns the rational closest to self with
        denominator at most max_denominator. (In case of ties, we pick the
        simpler rational.)

        EXAMPLES::

            sage: (0.333).nearby_rational(max_error=0.001)
            1/3
            sage: (0.333).nearby_rational(max_error=1)
            0
            sage: (-0.333).nearby_rational(max_error=0.0001)
            -257/772

        ::

            sage: (0.333).nearby_rational(max_denominator=100)
            1/3
            sage: RR(1/3 + 1/1000000).nearby_rational(max_denominator=2999999)
            777780/2333333
            sage: RR(1/3 + 1/1000000).nearby_rational(max_denominator=3000000)
            1000003/3000000
            sage: (-0.333).nearby_rational(max_denominator=1000)
            -333/1000
            sage: RR(3/4).nearby_rational(max_denominator=2)
            1
            sage: RR(pi).nearby_rational(max_denominator=120)
            355/113
            sage: RR(pi).nearby_rational(max_denominator=10000)
            355/113
            sage: RR(pi).nearby_rational(max_denominator=100000)
            312689/99532
            sage: RR(pi).nearby_rational(max_denominator=1)
            3
            sage: RR(-3.5).nearby_rational(max_denominator=1)
            -3

        TESTS::

            sage: RR('nan').nearby_rational(max_denominator=1000)
            Traceback (most recent call last):
            ...
            ValueError: Cannot convert NaN or infinity to rational number
            sage: RR('nan').nearby_rational(max_error=0.01)
            Traceback (most recent call last):
            ...
            ValueError: Cannot convert NaN or infinity to rational number
            sage: RR('infinity').nearby_rational(max_denominator=1000)
            Traceback (most recent call last):
            ...
            ValueError: Cannot convert NaN or infinity to rational number
            sage: RR('infinity').nearby_rational(max_error=0.01)
            Traceback (most recent call last):
            ...
            ValueError: Cannot convert NaN or infinity to rational number
        """

        if not mpfr_number_p(self.value):
            raise ValueError, 'Cannot convert NaN or infinity to rational number'

        if ((max_error is None and max_denominator is None) or
            (max_error is not None and max_denominator is not None)):
            raise ValueError, 'Must specify exactly one of max_error or max_denominator in nearby_rational()'

        if max_error is not None:
            from real_mpfi import RealIntervalField

            intv_field = RealIntervalField(self.prec())
            intv = intv_field(self - max_error, self + max_error)

            return intv.simplest_rational()

        cdef int sgn = mpfr_sgn(self.value)

        if sgn == 0:
            return Rational(0)

        cdef Rational self_r = self.exact_rational()

        cdef Integer self_d = self_r.denominator()

        if self_d <= max_denominator:
            return self_r

        if sgn < 0:
            self_r = -self_r

        cdef Integer fl = self_r.floor()
        cdef Rational target = self_r - fl

        cdef int low_done = 0
        cdef int high_done = 0

        # We use the Stern-Brocot tree to find the nearest neighbors of
        # self with denominator at most max_denominator.  However,
        # navigating the Stern-Brocot tree in the straightforward way
        # can be very slow; for instance, to get to 1/1000000 takes a
        # million steps.  Instead, we perform many steps at once;
        # this probably slows down the average case, but it drastically
        # speeds up the worst case.

        # Suppose we have a/b < c/d < e/f, where a/b and e/f are
        # neighbors in the Stern-Brocot tree and c/d is the target.
        # We alternate between moving the low and the high end toward
        # the target as much as possible.  Suppose that there are
        # k consecutive rightward moves in the Stern-Brocot tree
        # traversal; then we end up with (a+k*e)/(b+k*f).  We have
        # two constraints on k.  First, the result must be <= c/d;
        # this gives us the following:
        # (a+k*e)/(b+k*f) <= c/d
        # d*a + k*(d*e) <= c*b + k*(c*f)
        # k*(d*e) - k*(c*f) <= c*b - d*a
        # k <= (c*b - d*a)/(d*e - c*f)
        # when moving the high side, we get
        # (k*a+e)/(k*b+f) >= c/d
        # k*(d*a) + d*e >= k*(c*b) + c*f
        # d*e - c*f >= k*(c*b - d*a)
        # k <= (d*e - c*f)/(c*b - d*a)

        # We also need the denominator to be <= max_denominator; this
        # gives (b+k*f) <= max_denominator or
        # k <= (max_denominator - b)/f
        # or
        # k <= (max_denominator - f)/b

        # We use variables with the same names as in the math above.

        cdef Integer a = Integer(0)
        cdef Integer b = Integer(1)
        cdef Integer c = target.numerator()
        cdef Integer d = target.denominator()
        cdef Integer e = Integer(1)
        cdef Integer f = Integer(1)

        cdef Integer k

        while (not low_done) or (not high_done):
            # Move the low side
            k = (c*b - d*a) // (d*e - c*f)

            if b+k*f > max_denominator:
                k = (max_denominator - b) // f
                low_done = True

            if k == 0:
                low_done = True

            a = a + k*e
            b = b + k*f

            # Move the high side
            k = (d*e - c*f) // (c*b - d*a)

            if k*b + f >= max_denominator:
                k = (max_denominator - f) // b
                high_done = True

            if k == 0:
                high_done = True

            e = k*a + e
            f = k*b + f

        # Now a/b and e/f are rationals surrounding c/d.  We know that
        # neither is equal to c/d, since d > max_denominator and
        # b and f are both <= max_denominator.  (We know that
        # d > max_denominator because we return early (before we
        # get here) if d <= max_denominator.)

        low = a/b
        high = e/f

        cdef int compare = cmp(target - low, high - target)

        if compare > 0:
            result = high
        elif compare < 0:
            result = low
        else:
            compare = cmp(b, f)
            if compare > 0:
                result = high
            elif compare < 0:
                result = low
            else:
                compare = cmp(a, e)
                if compare > 0:
                    result = high
                else:
                    result = low

        result = fl + result

        if sgn < 0:
            return -result
        return result


    ###########################################
    # Comparisons: ==, !=, <, <=, >, >=
    ###########################################

    def is_NaN(self):
        return mpfr_nan_p(self.value)

    def is_positive_infinity(self):
        """
        EXAMPLES::

            sage: a = RR('1.494') / RR(0); a
            +infinity
            sage: a.is_positive_infinity()
            True
            sage: a = -RR('1.494') / RR(0); a
            -infinity
            sage: RR(1.5).is_positive_infinity()
            False
            sage: a.is_positive_infinity()
            False
        """
        return mpfr_inf_p(self.value) and mpfr_sgn(self.value) > 0

    def is_negative_infinity(self):
        """
        EXAMPLES::

            sage: a = RR('1.494') / RR(0); a
            +infinity
            sage: a.is_negative_infinity()
            False
            sage: a = -RR('1.494') / RR(0); a
            -infinity
            sage: RR(1.5).is_negative_infinity()
            False
            sage: a.is_negative_infinity()
            True
        """
        return mpfr_inf_p(self.value) and mpfr_sgn(self.value) < 0

    def is_infinity(self):
        """
        EXAMPLES::

            sage: a = RR('1.494') / RR(0); a
            +infinity
            sage: a.is_infinity()
            True
            sage: a = -RR('1.494') / RR(0); a
            -infinity
            sage: a.is_infinity()
            True
            sage: RR(1.5).is_infinity()
            False
        """
        return mpfr_inf_p(self.value)

    def is_unit(self):
        return mpfr_sgn(self.value) != 0

    def __nonzero__(self):
        return mpfr_sgn(self.value) != 0

    def __richcmp__(left, right, int op):
        return (<RingElement>left)._richcmp(right, op)

    cdef int _cmp_c_impl(left, Element right) except -2:
        cdef RealNumber self, x
        self = left
        x = right

        cdef int a,b
        a = mpfr_nan_p(self.value)
        b = mpfr_nan_p(x.value)
        if a != b:
            return -1    # nothing is equal to Nan
        cdef int i
        i = mpfr_cmp(self.value, x.value)
        if i < 0:
            return -1
        elif i == 0:
            return 0
        else:
            return 1


    ############################
    # Special Functions
    ############################

    def sqrt(self, extend=True, all=False):
        r"""
        The square root function.

        INPUT:


        -  ``extend`` - bool (default: True); if True, return a
           square root in a complex field if necessary if self is negative;
           otherwise raise a ValueError

        -  ``all`` - bool (default: False); if True, return a
           list of all square roots.


        EXAMPLES::

            sage: r = -2.0
            sage: r.sqrt()
            1.41421356237310*I

        ::

            sage: r = 4.0
            sage: r.sqrt()
            2.00000000000000
            sage: r.sqrt()^2 == r
            True

        ::

            sage: r = 4344
            sage: r.sqrt()
            2*sqrt(1086)

        ::

            sage: r = 4344.0
            sage: r.sqrt()^2 == r
            True
            sage: r.sqrt()^2 - r
            0.000000000000000

        ::

            sage: r = -2.0
            sage: r.sqrt()
            1.41421356237310*I
        """
        cdef RealNumber x
        if mpfr_cmp_ui(self.value, 0) >= 0:
            x = self._new()
            _sig_on
            mpfr_sqrt(x.value, self.value, (<RealField>self._parent).rnd)
            _sig_off
            if all:
                if x.is_zero():
                    return [x]
                else:
                    return [x, -x]
            return x
        if not extend:
            raise ValueError, "negative number %s does not have a square root in the real field"%self
        return self._complex_number_().sqrt(all=all)

    def is_square(self):
        """
        Returns whether or not this number is a square in this field. For
        the real numbers, this is True if and only if self is
        non-negative.

        EXAMPLES::

            sage: r = 3.5
            sage: r.is_square()
            True
            sage: r = 0.0
            sage: r.is_square()
            True
            sage: r = -4.0
            sage: r.is_square()
            False
        """
        return mpfr_sgn(self.value) >= 0

    def cube_root(self):
        """
        Return the cubic root (defined over the real numbers) of self.

        EXAMPLES::

            sage: r = 125.0; r.cube_root()
            5.00000000000000
            sage: r = -119.0
            sage: r.cube_root()^3 - r       # illustrates precision loss
            -1.42108547152020e-14
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_cbrt(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def __pow(self, RealNumber exponent):
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_pow(x.value, self.value, exponent.value, (<RealField>self._parent).rnd)
        _sig_off
        if mpfr_nan_p(x.value):
            return self._complex_number_()**exponent._complex_number_()
        return x

    def __pow__(self, exponent, modulus):
        """
        Compute self raised to the power of exponent, rounded in the
        direction specified by the parent of self.

        If the result is not a real number, self and the exponent are both
        coerced to complex numbers (with sufficient precision), then the
        exponentiation is computed in the complex numbers. Thus this
        function can return either a real or complex number.

        EXAMPLES::

            sage: R = RealField(30)
            sage: a = R('1.23456')
            sage: a^20
            67.646297
            sage: a^a
            1.2971115
            sage: b = R(-1)
            sage: b^(1/2)
            -8.7055157e-10 + 1.0000000*I

        We raise a real number to a symbolic object::

            sage: x, y = var('x,y')
            sage: 1.5^x
            1.50000000000000^x
            sage: -2.3^(x+y^3+sin(x))
            -2.30000000000000^(y^3 + x + sin(x))
        """
        cdef RealNumber x
        if not PY_TYPE_CHECK(self, RealNumber):
            return self.__pow__(float(exponent))
        if not PY_TYPE_CHECK(exponent, RealNumber):
            try:
                x = self
                exponent = x._parent(exponent)
            except TypeError:
                try:
                    return exponent.parent()(self)**exponent
                except AttributeError:
                    raise TypeError
        return self.__pow(exponent)

    def log(self, base='e'):
        """
        EXAMPLES::

            sage: R = RealField()
            sage: R(2).log()
            0.693147180559945
        """
        cdef RealNumber x
        if base == 'e':
            x = self._new()
            _sig_on
            mpfr_log(x.value, self.value, (<RealField>self._parent).rnd)
            _sig_off
            return x
        elif base == 10:
            return self.log10()
        elif base == 2:
            return self.log2()
        else:
            return self.log() / (self.parent()(base)).log()

    def log2(self):
        """
        Returns log to the base 2 of self

        EXAMPLES::

            sage: r = 16.0
            sage: r.log2()
            4.00000000000000

        ::

            sage: r = 31.9; r.log2()
            4.99548451887751

        ::

            sage: r = 0.0
            sage: r.log2()
            -infinity
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_log2(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def log10(self):
        """
        Returns log to the base 10 of self

        EXAMPLES::

            sage: r = 16.0; r.log10()
            1.20411998265592
            sage: r.log() / log(10.0)
            1.20411998265592

        ::

            sage: r = 39.9; r.log10()
            1.60097289568675

        ::

            sage: r = 0.0
            sage: r.log10()
            -infinity

        ::

            sage: r = -1.0
            sage: r.log10()
            NaN
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_log10(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def log1p(self):
        """
        Returns log of 1 + self

        EXAMPLES::

            sage: r = 15.0; r.log1p()
            2.77258872223978
            sage: (r+1).log()
            2.77258872223978

        ::

            sage: r = 38.9; r.log1p()
            3.68637632389582

        ::

            sage: r = -1.0
            sage: r.log1p()
            -infinity

        ::

            sage: r = -2.0
            sage: r.log1p()
            NaN
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_log1p(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def exp(self):
        r"""
        Returns `e^\mathtt{self}`

        EXAMPLES::

            sage: r = 0.0
            sage: r.exp()
            1.00000000000000

        ::

            sage: r = 32.3
            sage: a = r.exp(); a
            1.06588847274864e14
            sage: a.log()
            32.3000000000000

        ::

            sage: r = -32.3
            sage: r.exp()
            9.38184458849869e-15
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_exp(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def exp2(self):
        """
        Returns `2^\mathtt{self}`

        EXAMPLES::

            sage: r = 0.0
            sage: r.exp2()
            1.00000000000000

        ::

            sage: r = 32.0
            sage: r.exp2()
            4.29496729600000e9

        ::

            sage: r = -32.3
            sage: r.exp2()
            1.89117248253021e-10
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_exp2(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def exp10(self):
        r"""
        Returns `10^\mathtt{self}`

        EXAMPLES::

            sage: r = 0.0
            sage: r.exp10()
            1.00000000000000

        ::

            sage: r = 32.0
            sage: r.exp10()
            1.00000000000000e32

        ::

            sage: r = -32.3
            sage: r.exp10()
            5.01187233627276e-33
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_exp10(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def expm1(self):
        """
        Returns `e^\mathtt{self}-1`, avoiding cancellation
        near 0.

        EXAMPLES::

            sage: r = 1.0
            sage: r.expm1()
            1.71828182845905

        ::

            sage: r = 1e-16
            sage: exp(r)-1
            0.000000000000000
            sage: r.expm1()
            1.00000000000000e-16
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_expm1(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def eint(self):
        """
        Returns the exponential integral of this number.

        EXAMPLES::

            sage: r = 1.0
            sage: r.eint()
            1.89511781635594

        ::

            sage: r = -1.0
            sage: r.eint()
            NaN
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_eint(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def cos(self):
        """
        Returns the cosine of this number

        EXAMPLES::

            sage: t=RR.pi()/2
            sage: t.cos()
            6.12323399573677e-17
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_cos(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    ##########################################################
    # it would be nice to get zero back here:
    # sage: R(-1).acos().sin()
    # _57 = -0.50165576126683320234e-19
    # i think this could be "fixed" by using MPFI. (put on to-do list.)
    #
    # this seems to work ok:
    # sage: R(-1).acos().cos()
    # _58 = -0.10000000000000000000e1
    def sin(self):
        """
        Returns the sine of this number

        EXAMPLES::

            sage: R = RealField(100)
            sage: R(2).sin()
            0.90929742682568169539601986591
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_sin(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def tan(self):
        """
        Returns the tangent of this number

        EXAMPLES::

            sage: q = RR.pi()/3
            sage: q.tan()
            1.73205080756888
            sage: q = RR.pi()/6
            sage: q.tan()
            0.577350269189626
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_tan(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def sincos(self):
        """
        Returns a pair consisting of the sine and cosine.

        EXAMPLES::

            sage: R = RealField()
            sage: t = R.pi()/6
            sage: t.sincos()
            (0.500000000000000, 0.866025403784439)
        """
        cdef RealNumber x,y
        x = self._new()
        y = self._new()
        _sig_on
        mpfr_sin_cos(x.value, y.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x,y


    # int mpfr_sin_cos (mpfr_t rop, mpfr_t op, mpfr_t, mp_rnd_t rnd)

    def arccos(self):
        """
        Returns the inverse cosine of this number

        EXAMPLES::

            sage: q = RR.pi()/3
            sage: i = q.cos()
            sage: i.arccos() == q
            True
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_acos(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def arcsin(self):
        """
        Returns the inverse sine of this number

        EXAMPLES::

            sage: q = RR.pi()/5
            sage: i = q.sin()
            sage: i.arcsin() == q
            True
            sage: i.arcsin() - q
            0.000000000000000
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_asin(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def arctan(self):
        """
        Returns the inverse tangent of this number

        EXAMPLES::

            sage: q = RR.pi()/5
            sage: i = q.tan()
            sage: i.arctan() == q
            True
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_atan(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    #int mpfr_acos _PROTO ((mpfr_ptr, mpfr_srcptr, mp_rnd_t));
    #int mpfr_asin _PROTO ((mpfr_ptr, mpfr_srcptr, mp_rnd_t));
    #int mpfr_atan _PROTO ((mpfr_ptr, mpfr_srcptr, mp_rnd_t));

    def cosh(self):
        """
        Returns the hyperbolic cosine of this number

        EXAMPLES::

            sage: q = RR.pi()/12
            sage: q.cosh()
            1.03446564009551
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_cosh(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def sinh(self):
        """
        Returns the hyperbolic sine of this number

        EXAMPLES::

            sage: q = RR.pi()/12
            sage: q.sinh()
            0.264800227602271
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_sinh(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def tanh(self):
        """
        Returns the hyperbolic tangent of this number

        EXAMPLES::

            sage: q = RR.pi()/11
            sage: q.tanh()
            0.278079429295850
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_tanh(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def coth(self):
        """
        Returns the hyperbolic cotangent of this number

        EXAMPLES::

            sage: RealField(100)(2).coth()
            1.0373147207275480958778097648
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_coth(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def arccoth(self):
        """
        Returns the inverse hyperbolic cotangent of this number

        EXAMPLES::

            sage: q = RR.pi()/5
            sage: i = q.coth()
            sage: i.arccoth() == q
            True
        """
        return (~self).arctanh()

    def cot(self):
        """
        Returns the cotangent of this number

        EXAMPLES::

            sage: RealField(100)(2).cot()
            -0.45765755436028576375027741043
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_cot(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def csch(self):
        """
        Returns the hyperbolic cosecant of this number

        EXAMPLES::

            sage: RealField(100)(2).csch()
            0.27572056477178320775835148216
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_csch(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def arccsch(self):
        """
        Returns the inverse hyperbolic cosecant of this number

        EXAMPLES::

            sage: i = RR.pi()/5
            sage: q = i.csch()
            sage: q.arccsch() == i
            True
        """
        return (~self).arcsinh()

    def csc(self):
        """
        Returns the cosecant of this number

        EXAMPLES::

            sage: RealField(100)(2).csc()
            1.0997501702946164667566973970
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_csc(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def sech(self):
        """
        Returns the hyperbolic secant of this number

        EXAMPLES::

            sage: RealField(100)(2).sech()
            0.26580222883407969212086273982
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_sech(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def arcsech(self):
        """
        Returns the inverse hyperbolic secant of this number

        EXAMPLES::

            sage: i = RR.pi()/3
            sage: q = i.sech()
            sage: q.arcsech() == i
            True
        """
        return (~self).arccosh()

    def sec(self):
        """
        Returns the secant of this number

        EXAMPLES::

            sage: RealField(100)(2).sec()
            -2.4029979617223809897546004014
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_sec(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def arccosh(self):
        """
        Returns the hyperbolic inverse cosine of this number

        EXAMPLES::

            sage: q = RR.pi()/2
            sage: i = q.cosh() ; i
            2.50917847865806
            sage: q == i.arccosh()
            True
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_acosh(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def arcsinh(self):
        """
        Returns the hyperbolic inverse sine of this number

        EXAMPLES::

            sage: q = RR.pi()/7
            sage: i = q.sinh() ; i
            0.464017630492991
            sage: i.arcsinh() - q
            0.000000000000000
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_asinh(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def arctanh(self):
        """
        Returns the hyperbolic inverse tangent of this number

        EXAMPLES::

            sage: q = RR.pi()/7
            sage: i = q.tanh() ; i
            0.420911241048535
            sage: i.arctanh() - q
            0.000000000000000
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_atanh(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def agm(self, other):
        """
        Return the arithmetic-geometric mean of self and other. The
        arithmetic-geometric mean is the common limit of the sequences
        `u_n` and `v_n`, where `u_0` is self,
        `v_0` is other, `u_{n+1}` is the arithmetic mean
        of `u_n` and `v_n`, and `v_{n+1}` is the
        geometric mean of u_n and v_n. If any operand is negative, the
        return value is ``NaN``.
        """
        cdef RealNumber x, _other
        if not isinstance(other, RealNumber) or other.parent() != self._parent:
            _other = self._parent(other)
        else:
            _other = other
        x = self._new()
        _sig_on
        mpfr_agm(x.value, self.value, _other.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def erf(self):
        """
        Returns the value of the error function on self.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(2).erf()
            0.995322265018953
            sage: R(6).erf()
            1.00000000000000
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_erf(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def erfc(self):
        """
        Returns the value of the complementary error function on self,
        i.e., `1-\mathtt{erf}(\mathtt{self})`.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(2).erfc()
            0.00467773498104727
            sage: R(6).erfc()
            2.15197367124989e-17
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_erfc(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def j0(self):
        """
        Returns the value of the Bessel J function of order 0 at self.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(2).j0()
            0.223890779141236
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_j0(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def j1(self):
        """
        Returns the value of the Bessel J function of order 1 at self.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(2).j1()
            0.576724807756873
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_j1(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def jn(self, long n):
        """
        Returns the value of the Bessel J function of order `n` at
        self.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(2).jn(3)
            0.128943249474402
            sage: R(2).jn(-17)
            -2.65930780516787e-15
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_jn(x.value, n, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def y0(self):
        """
        Returns the value of the Bessel Y function of order 0 at self.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(2).y0()
            0.510375672649745
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_y0(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def y1(self):
        """
        Returns the value of the Bessel Y function of order 1 at self.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(2).y1()
            -0.107032431540938
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_y1(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def yn(self, long n):
        """
        Returns the value of the Bessel Y function of order `n` at
        self.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(2).yn(3)
            -1.12778377684043
            sage: R(2).yn(-17)
            7.09038821729481e12
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_yn(x.value, n, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def gamma(self):
        """
        The Euler gamma function. Return gamma of self.

        EXAMPLES::

            sage: R = RealField()
            sage: R(6).gamma()
            120.000000000000
            sage: R(1.5).gamma()
            0.886226925452758
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_gamma(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def lngamma(self):
        """
        Return the logarithm of gamma of self.

        EXAMPLES::

            sage: R = RealField(53)
            sage: R(6).lngamma()
            4.78749174278205
            sage: R(1e10).lngamma()
            2.20258509288811e11
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_lngamma(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def zeta(self):
        r"""
        Return the Riemann zeta function evaluated at this real number.

        .. note:

           PARI is vastly more efficient at computing the Riemann zeta
           function. See the example below for how to use it.

        EXAMPLES::

            sage: R = RealField()
            sage: R(2).zeta()
            1.64493406684823
            sage: R.pi()^2/6
            1.64493406684823
            sage: R(-2).zeta()
            0.000000000000000
            sage: R(1).zeta()
            +infinity

        Computing zeta using PARI is much more efficient in difficult
        cases. Here's how to compute zeta with at least a given precision::

            sage: z = pari(2).zeta(precision=53); z
            1.64493406684823
            sage: pari(2).zeta(precision=128).python().prec()
            128
            sage: pari(2).zeta(precision=65).python().prec()
            128                                                # 64-bit
            96                                                 # 32-bit

        Note that the number of bits of precision in the constructor only
        effects the internal precision of the pari number, which is rounded
        up to the nearest multiple of 32 or 64. To increase the number of
        digits that gets displayed you must use
        ``pari.set_real_precision``.

        ::

            sage: type(z)
            <type 'sage.libs.pari.gen.gen'>
            sage: R(z)
            1.64493406684823
        """
        cdef RealNumber x
        x = self._new()
        _sig_on
        mpfr_zeta(x.value, self.value, (<RealField>self._parent).rnd)
        _sig_off
        return x

    def algdep(self, n):
        """
        Returns a polynomial of degree at most `n` which is
        approximately satisfied by this number. Note that the returned
        polynomial need not be irreducible, and indeed usually won't be if
        this number is a good approximation to an algebraic number of
        degree less than `n`.

        ALGORITHM: Uses the PARI C-library algdep command.

        EXAMPLE::

            sage: r = sqrt(2.0); r
            1.41421356237310
            sage: r.algdep(5)
            x^2 - 2
        """
        return sage.rings.arith.algdep(self,n)

    def algebraic_dependency(self, n):
        """
        Returns a polynomial of degree at most `n` which is
        approximately satisfied by this number. Note that the returned
        polynomial need not be irreducible, and indeed usually won't be if
        this number is a good approximation to an algebraic number of
        degree less than `n`.

        ALGORITHM: Uses the PARI C-library algdep command.

        EXAMPLE::

            sage: r = sqrt(2.0); r
            1.41421356237310
            sage: r.algdep(5)
            x^2 - 2
        """
        return sage.rings.arith.algdep(self,n)

    def nth_root(self, int n, int algorithm=0):
        r"""
        Returns an `n^{th}` root of self.

        INPUT:


        -  ``n`` - A positive number, rounded down to the
           nearest integer. Note that `n` should be less than
           ```sys.maxint```.

        -  ``algorithm`` - Set this to 1 to call mpfr directly,
           set this to 2 to use interval arithmetic and logarithms, or leave
           it at the default of 0 to choose the algorithm which is estimated
           to be faster.


        AUTHORS:

        - Carl Witty (2007-10)

        EXAMPLES::

            sage: R = RealField()
            sage: R(8).nth_root(3)
            2.00000000000000
            sage: R(8).nth_root(3.7)    # illustrate rounding down
            2.00000000000000
            sage: R(-8).nth_root(3)
            -2.00000000000000
            sage: R(0).nth_root(3)
            0.000000000000000
            sage: R(32).nth_root(-1)
            Traceback (most recent call last):
            ...
            ValueError: n must be positive
            sage: R(32).nth_root(1.0)
            32.0000000000000
            sage: R(4).nth_root(4)
            1.41421356237310
            sage: R(4).nth_root(40)
            1.03526492384138
            sage: R(4).nth_root(400)
            1.00347174850950
            sage: R(4).nth_root(4000)
            1.00034663365385
            sage: R(4).nth_root(4000000)
            1.00000034657365
            sage: R(-27).nth_root(3)
            -3.00000000000000
            sage: R(-4).nth_root(3999999)
            -1.00000034657374

        Note that for negative numbers, any even root throws an exception

        ::

            sage: R(-2).nth_root(6)
            Traceback (most recent call last):
            ...
            ValueError: taking an even root of a negative number

        The `n^{th}` root of 0 is defined to be 0, for any
        `n`

        ::

            sage: R(0).nth_root(6)
            0.000000000000000

        ::

            sage: R(0).nth_root(7)
            0.000000000000000

        TESTS: The old and new algorithms should give exactly the same
        results in all cases.

        ::

            sage: def check(x, n):
            ...       answers = []
            ...       for sign in (1, -1):
            ...           if is_even(n) and sign == -1:
            ...               continue
            ...           for rounding in ('RNDN', 'RNDD', 'RNDU', 'RNDZ'):
            ...               fld = RealField(x.prec(), rnd=rounding)
            ...               fx = fld(sign * x)
            ...               alg_mpfr = fx.nth_root(n, algorithm=1)
            ...               alg_mpfi = fx.nth_root(n, algorithm=2)
            ...               assert(alg_mpfr == alg_mpfi)
            ...               if sign == 1: answers.append(alg_mpfr)
            ...       return answers

        Check some perfect powers (and nearby numbers).

        ::

            sage: check(16.0, 4)
            [2.00000000000000, 2.00000000000000, 2.00000000000000, 2.00000000000000]
            sage: check((16.0).nextabove(), 4)
            [2.00000000000000, 2.00000000000000, 2.00000000000001, 2.00000000000000]
            sage: check((16.0).nextbelow(), 4)
            [2.00000000000000, 1.99999999999999, 2.00000000000000, 1.99999999999999]
            sage: check(((9.0 * 256)^7), 7)
            [2304.00000000000, 2304.00000000000, 2304.00000000000, 2304.00000000000]
            sage: check(((9.0 * 256)^7).nextabove(), 7)
            [2304.00000000000, 2304.00000000000, 2304.00000000001, 2304.00000000000]
            sage: check(((9.0 * 256)^7).nextbelow(), 7)
            [2304.00000000000, 2303.99999999999, 2304.00000000000, 2303.99999999999]
            sage: check(((5.0 / 512)^17), 17)
            [0.00976562500000000, 0.00976562500000000, 0.00976562500000000, 0.00976562500000000]
            sage: check(((5.0 / 512)^17).nextabove(), 17)
            [0.00976562500000000, 0.00976562500000000, 0.00976562500000001, 0.00976562500000000]
            sage: check(((5.0 / 512)^17).nextbelow(), 17)
            [0.00976562500000000, 0.00976562499999999, 0.00976562500000000, 0.00976562499999999]

        And check some non-perfect powers::

            sage: check(2.0, 3)
            [1.25992104989487, 1.25992104989487, 1.25992104989488, 1.25992104989487]
            sage: check(2.0, 4)
            [1.18920711500272, 1.18920711500272, 1.18920711500273, 1.18920711500272]
            sage: check(2.0, 5)
            [1.14869835499704, 1.14869835499703, 1.14869835499704, 1.14869835499703]

        And some different precisions::

            sage: check(RealField(20)(22/7), 19)
            [1.0621, 1.0621, 1.0622, 1.0621]
            sage: check(RealField(200)(e), 4)
            [1.2840254166877414840734205680624364583362808652814630892175, 1.2840254166877414840734205680624364583362808652814630892175, 1.2840254166877414840734205680624364583362808652814630892176, 1.2840254166877414840734205680624364583362808652814630892175]
        """
        if n <= 0:
            raise ValueError, "n must be positive"

        cdef int odd = (n & 1)

        cdef int sgn = mpfr_sgn(self.value)

        if sgn < 0 and not odd:
            raise ValueError, "taking an even root of a negative number"

        if sgn == 0 or n == 1 or not mpfr_number_p(self.value):
            return self

        cdef RealField fld = <RealField>self._parent

        if algorithm == 0 and fld.__prec * n < 10000:
            # This is a rough estimate for when it is probably
            # faster to call mpfr directly.  (This is a pretty
            # good estimate on one particular machine, a
            # Core 2 Duo in 32-bit mode, but has not been tested
            # on other machines.)
            algorithm = 1

        cdef RealNumber x

        if algorithm == 1:
            x = self._new()
            _sig_on
            mpfr_root(x.value, self.value, n, (<RealField>self._parent).rnd)
            _sig_off
            return x

        cdef mpfr_rnd_t rnd = (<RealField>self._parent).rnd

        cdef Integer mantissa
        cdef mp_exp_t exponent
        cdef int pow2
        cdef int exact

        if rnd != GMP_RNDN:
            # We are going to implement nth_root using interval
            # arithmetic.  To guarantee correct rounding, we will
            # increase the precision of the interval arithmetic until
            # the resulting interval is small enough...until the
            # interval is entirely within the interval represented
            # by a single floating-point number.

            # This always works, unless the correct answer is exactly
            # on the boundary point between the intervals of two
            # floating-point numbers.  In round-to-nearest mode, this
            # is impossible; the boundary points are the
            # numbers which can be exactly represented as precision-{k+1}
            # floating-point numbers, but not precision-{k} numbers.
            # A precision-{k} floating-point number cannot be a perfect
            # n'th power (n >= 2) of such a number.

            # However, in the directed rounding modes, the boundary points
            # are the floating-point numbers themselves.  So in a
            # directed rounding mode, we need to check whether this
            # floating-point number is a perfect n'th power.

            # Suppose this number is (a * 2^k)^n, for odd integer a
            # and arbitrary integer k.  Then this number is
            # (a^n) * 2^(k*n), where a^n is odd.

            # We start by extracting the mantissa and exponent of (the
            # absolute value of) this number.

            mantissa = Integer()
            _sig_on
            exponent = mpfr_get_z_exp(mantissa.value, self.value)
            _sig_off
            mpz_abs(mantissa.value, mantissa.value)

            # Now, we want to divide out any powers of two in mantissa,
            # leaving it as an odd number.

            _sig_on
            pow2 = mpz_scan1(mantissa.value, 0)
            _sig_off

            if pow2 > 0:
                exponent = exponent + pow2
                _sig_on
                mpz_fdiv_q_2exp(mantissa.value, mantissa.value, pow2)
                _sig_off

            # Our floating-point number is equal to mantissa * 2^exponent,
            # and we know that mantissa is odd.

            if exponent % n == 0:
                # The exponent is a multiple of n, so it's possible that
                # we have a perfect power.  Now we need to check the
                # mantissa.

                _sig_on
                exact = mpz_root(mantissa.value, mantissa.value, n)
                _sig_off

                if exact:
                    # Yes, we are a perfect power.  We've replaced mantissa
                    # with its n'th root, so we can just build
                    # the resulting floating-point number.

                    x = self._new()

                    _sig_on
                    mpfr_set_z(x.value, mantissa.value, GMP_RNDN)
                    _sig_off
                    mpfr_mul_2si(x.value, x.value, exponent / n, GMP_RNDN)
                    if sgn < 0:
                        mpfr_neg(x.value, x.value, GMP_RNDN)

                    return x

        # If we got here, then we're not a perfect power of a boundary
        # point, so it's safe to use the interval arithmetic technique.

        from real_mpfi import RealIntervalField

        cdef int prec = fld.__prec + 10

        cdef RealNumber lower
        cdef RealNumber upper

        while True:
            ifld = RealIntervalField(prec)
            intv = ifld(self)
            if sgn < 0:
                intv = -intv
            intv = (intv.log() / n).exp()
            if sgn < 0:
                intv = -intv
            lower = fld(intv.lower())
            upper = fld(intv.upper())

            if mpfr_equal_p(lower.value, upper.value):
                # Yes, we found the answer
                return lower

            prec = prec + 20

cdef class RealLiteral(RealNumber):

    cdef readonly literal
    cdef readonly int base

    def __init__(self, RealField parent, x=0, int base=10):
        """
        RealLiterals are created in preparsing and provide a way to allow
        casting into higher precision rings.

        EXAMPLES::

            sage: RealField(200)(float(1.3))
            1.3000000000000000444089209850062616169452667236328125000000
            sage: RealField(200)(1.3)
            1.3000000000000000000000000000000000000000000000000000000000
            sage: 1.3 + 1.2
            2.50000000000000
        """
        RealNumber.__init__(self, parent, x, base)
        if PY_TYPE_CHECK(x, str):
            self.base = base
            self.literal = x

    def __neg__(self):
        """
        EXAMPLES::

            sage: RealField(300)(-1.2)
            -1.20000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
            sage: RealField(300)(-(-1.2))
            1.20000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        """
        if self.literal is not None and self.literal[0] == '-':
            return RealLiteral(self._parent, self.literal[1:], self.base)
        else:
            return RealLiteral(self._parent, '-'+self.literal, self.base)

RR = RealField_constructor()


def create_RealNumber(s, int base=10, int pad=0, rnd="RNDN", int min_prec=53):
    r"""
    Return the real number defined by the string s as an element of
    ``RealField(prec=n)``, where n potentially has slightly
    more (controlled by pad) bits than given by s.

    INPUT:


    -  ``s`` - a string that defines a real number (or
       something whose string representation defines a number)

    -  ``base`` - an integer between 2 and 36

    -  ``pad`` - an integer = 0.

    -  ``rnd`` - rounding mode: RNDN, RNDZ, RNDU, RNDD

    -  ``min_prec`` - number will have at least this many
       bits of precision, no matter what.


    EXAMPLES::

        sage: RealNumber('2.3')
        2.30000000000000
        sage: RealNumber(10)
        10.0000000000000
        sage: RealNumber('1.0000000000000000000000000000000000')
        1.0000000000000000000000000000000000
        sage: RealField(200)(1.2)
        1.2000000000000000000000000000000000000000000000000000000000
        sage: (1.2).parent() is RR
        True
    """
    if not isinstance(s, str):
        s = str(s)

    if base == 10 and min_prec == 53 and len(s) <= 15:
        R = RR

    else:

        if 'e' in s or 'E' in s:
            #Figure out the exponent
            index = max( s.find('e'), s.find('E') )
            exponent = int(s[index+1:])
            rest = s[:index]

            #Find the first nonzero entry in rest
            sigfigs = 0
            for i in range(len(rest)):
                if rest[i] != '.' and rest[i] != '0':
                    sigfigs = len(rest) - i
                    break

            if base == 10:
                bits = int(3.32192*sigfigs)+1
            else:
                bits = int(math.log(base,2)*sigfigs)+1
        else:
            #Find the first nonzero entry in s
            sigfigs = 0
            for i in range(len(s)):
                if s[i] != '.' and s[i] != '0':
                    sigfigs = len(s) - i
                    break

            if base == 10:
                bits = int(3.32192*sigfigs)+1
            else:
                bits = int(math.log(base,2)*sigfigs)+1

        R = RealField_constructor(prec=max(bits+pad, min_prec), rnd=rnd)

    return RealLiteral(R, s, base)


# here because this imports the other two real fields
def create_RealField(prec=53, type="MPFR", rnd="RNDN", sci_not=0):
    if type == "RDF":
        return RDF
    elif type == "RQDF":
        from real_rqdf import RQDF
        return RQDF
    elif type == "Interval":
        from real_mpfi import RealIntervalField
        return RealIntervalField(prec, sci_not)
    elif type == "RLF":
        from real_lazy import RLF
        return RLF
    else:
        return RealField_constructor(prec, sci_not, rnd)


def is_RealField(x):
    return PY_TYPE_CHECK(x, RealField)

def is_RealNumber(x):
    """
    Return True if x is of type RealNumber, meaning that it is an
    element of the MPFR real field with some precision.

    EXAMPLES::

        sage: from sage.rings.real_mpfr import is_RealNumber
        sage: is_RealNumber(2.5)
        True
        sage: is_RealNumber(float(2.3))
        False
        sage: is_RealNumber(RDF(2))
        False
        sage: is_RealNumber(pi)
        False
    """
    return PY_TYPE_CHECK(x, RealNumber)

def __create__RealField_version0(prec, sci_not, rnd):
    return RealField(prec, sci_not, rnd)

def __create__RealNumber_version0(parent, x, base=10):
    return RealNumber(parent, x, base=base)


cdef inline RealNumber empty_RealNumber(RealField parent):
    cdef RealNumber y = <RealNumber>PY_NEW(RealNumber)
    y._parent = parent
    mpfr_init2(y.value, parent.__prec)
    y.init = 1
    return y

cdef class RRtoRR(Map):
    cpdef Element _call_(self, x):
        """
        EXAMPLES::

            sage: from sage.rings.real_mpfr import RRtoRR
            sage: R10 = RealField(10)
            sage: R100 = RealField(100)
            sage: f = RRtoRR(R100, R10)
            sage: a = R100(1.2)
            sage: f(a)
            1.2
            sage: g = f.section()
            sage: g
            Generic map:
              From: Real Field with 10 bits of precision
              To:   Real Field with 100 bits of precision
            sage: g(f(a))
            1.1992187500000000000000000000
            sage: b = R10(2).sqrt()
            sage: f(g(b))
            1.4
            sage: f(g(b)) == b
            True
        """
        cdef RealField parent = <RealField>self._codomain
        cdef RealNumber y = empty_RealNumber(parent)
        if PY_TYPE_CHECK_EXACT(x, RealLiteral):
            mpfr_set_str(y.value, (<RealLiteral>x).literal, (<RealLiteral>x).base, parent.rnd)
        else:
            mpfr_set(y.value, (<RealNumber>x).value, parent.rnd)
        return y

    def section(self):
        """
        EXAMPLES::

            sage: from sage.rings.real_mpfr import RRtoRR
            sage: R10 = RealField(10)
            sage: R100 = RealField(100)
            sage: f = RRtoRR(R100, R10)
            sage: f.section()
            Generic map:
              From: Real Field with 10 bits of precision
              To:   Real Field with 100 bits of precision
        """
        return RRtoRR(self._codomain, self._domain)

cdef class ZZtoRR(Map):
    cpdef Element _call_(self, x):
        """
        EXAMPLES::

            sage: from sage.rings.real_mpfr import ZZtoRR
            sage: f = ZZtoRR(ZZ, RealField(20))
            sage: f(123456789)
            1.2346e8
        """
        cdef RealField parent = <RealField>self._codomain
        cdef RealNumber y = empty_RealNumber(parent)
        mpfr_set_z(y.value, (<Integer>x).value, parent.rnd)
        return y

cdef class QQtoRR(Map):
    cpdef Element _call_(self, x):
        """
        EXAMPLES::

            sage: from sage.rings.real_mpfr import QQtoRR
            sage: f = QQtoRR(QQ, RealField(200))
            sage: f(-1/3)
            -0.33333333333333333333333333333333333333333333333333333333333
        """
        cdef RealField parent = <RealField>self._codomain
        cdef RealNumber y = empty_RealNumber(parent)
        mpfr_set_q(y.value, (<Rational>x).value, parent.rnd)
        return y

cdef class double_toRR(Map):
    cpdef Element _call_(self, x):
        """
        Takes anything that can be converted to a double.

        EXAMPLES::

            sage: from sage.rings.real_mpfr import double_toRR
            sage: f = double_toRR(RDF, RealField(22))
            sage: f(RDF.pi())
            3.14159
            sage: f = double_toRR(RDF, RealField(200))
            sage: f(RDF.pi())
            3.1415926535897931159979634685441851615905761718750000000000
        """
        cdef RealField parent = <RealField>self._codomain
        cdef RealNumber y = empty_RealNumber(parent)
        mpfr_set_d(y.value, x, parent.rnd)
        return y

cdef class int_toRR(Map):
    cpdef Element _call_(self, x):
        """
        Takes anything that can be converted to a long.

        EXAMPLES::

            sage: from sage.rings.real_mpfr import int_toRR
            sage: f = int_toRR(int, RR)
            sage: f(-10r)
            -10.0000000000000
            sage: f(2^75)
            Traceback (most recent call last):
            ...
            OverflowError: long int too large to convert to int

        ::

            sage: R.<x> = ZZ[]
            sage: f = int_toRR(R, RR)
            sage: f(x-x+1)
            1.00000000000000
        """
        cdef RealField parent = <RealField>self._codomain
        cdef RealNumber y = empty_RealNumber(parent)
        mpfr_set_si(y.value, x, parent.rnd)
        return y
