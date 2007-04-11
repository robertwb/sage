r"""
Elements of $\Z/n\Z$

An element of the integers modulo $n$.

AUTHORS:
    -- Robert Bradshaw (most of the work)
    -- Didier Deshommes (bit shifting)
    -- William Stein (editing and polishing; new arith architecture)

TESTS:
    sage: R = Integers(101^3)
    sage: a = R(824362); b = R(205942)
    sage: a * b
    851127
"""

include "../ext/interrupt.pxi"  # ctrl-c interrupt block support
include "../ext/stdsage.pxi"

import operator

import integer_mod_ring
import arith
import rational
from sage.libs.all import pari, PariError
import integer_ring

import commutative_ring_element
import sage.interfaces.all

import sage.rings.integer
cimport sage.rings.integer
from sage.rings.integer cimport Integer

import sage.structure.element
cimport sage.structure.element
from sage.structure.element cimport RingElement, ModuleElement, Element

from sage.structure.parent cimport Parent


def Mod(n, m, parent=None):
    """
    Return the equivalence class of n modulo m as an element of
    $\Z/m\Z$.

    EXAMPLES:
        sage: x = Mod(12345678, 32098203845329048)
        sage: x
        12345678
        sage: x^100
        1017322209155072

    You can also use the lowercase version:
        sage: mod(12,5)
        2
    """
    cdef IntegerMod_abstract x
    x = IntegerMod(integer_mod_ring.IntegerModRing(m), n)
    if parent is None:
        return x
    x._parent = parent
    return x


mod = Mod


def IntegerMod(parent, value):
    """
    Create an integer modulo $n$ with the given parent.

    This is mainly for internal use.
    """
    cdef NativeIntStruct modulus
    cdef Py_ssize_t res
    modulus = parent._pyx_order
    if modulus.table is not None:
        if PY_TYPE_CHECK(value, sage.rings.integer.Integer) or PY_TYPE_CHECK(value, int) or PY_TYPE_CHECK(value, long):
            res = value % modulus.int64
            if res < 0:
                res = res + modulus.int64
            return modulus.lookup(res)
    if modulus.int32 != -1:
        return IntegerMod_int(parent, value)
    elif modulus.int64 != -1:
        return IntegerMod_int64(parent, value)
    else:
        return IntegerMod_gmp(parent, value)


def is_IntegerMod(x):
    """
    Return try if and only if x is an integer modulo n.

    EXAMPLES:
        sage: is_IntegerMod(5)
        False
        sage: is_IntegerMod(Mod(5,10))
        True
    """
    return bool(isinstance(x, IntegerMod_abstract))

def makeNativeIntStruct(sage.rings.integer.Integer z):
    return NativeIntStruct(z)

cdef class NativeIntStruct:

    def __init__(NativeIntStruct self, sage.rings.integer.Integer z):
        self.int64 = -1
        self.int32 = -1
        self.table = None # NULL
        self.sageInteger = z
        if mpz_cmp_si(z.value, INTEGER_MOD_INT64_LIMIT) < 0:
            self.int64 = mpz_get_si(z.value)
            if self.int64 < INTEGER_MOD_INT32_LIMIT:
                self.int32 = self.int64

    def __reduce__(NativeIntStruct self):
        return sage.rings.integer_mod.makeNativeIntStruct, (self.sageInteger, )

    def precompute_table(NativeIntStruct self, parent):
        self.table = PyList_New(self.int64)
        cdef Py_ssize_t i
        if self.int32 != -1:
            for i from 0 <= i < self.int32:
                z = IntegerMod_int(parent, i)
                Py_INCREF(z); PyList_SET_ITEM(self.table, i, z)
        else:
            for i from 0 <= i < self.int64:
                z = IntegerMod_int64(parent, i)
                Py_INCREF(z); PyList_SET_ITEM(self.table, i, z)

    cdef lookup(NativeIntStruct self, Py_ssize_t value):
        return <object>PyList_GET_ITEM(self.table, value)


cdef class IntegerMod_abstract(sage.structure.element.CommutativeRingElement):

    def __init__(self, parent):
        """
        EXAMPLES:
            sage: a = Mod(10,30^10); a
            10
            sage: loads(a.dumps()) == a
            True
        """
        self._parent = parent
        self.__modulus = parent._pyx_order

    def __abs__(self):
        """
        Raise an error message, since abs(x) makes no sense when x is an
        integer modulo n.

        EXAMPLES:
            sage: abs(Mod(2,3))
            Traceback (most recent call last):
            ...
            ArithmeticError: absolute valued not defined on integers modulo n.
        """
        raise ArithmeticError, "absolute valued not defined on integers modulo n."

    def __reduce__(IntegerMod_abstract self):
        """
        EXAMPLES:
            sage: a = Mod(4,5); a
            4
            sage: loads(a.dumps()) == a
            True
            sage: a = Mod(-1,5^30)^25;
            sage: loads(a.dumps()) == a
            True
        """
        return sage.rings.integer_mod.mod, (self.lift(), self.modulus(), self.parent())

    def is_nilpotent(self):
        r"""
        Return True if self is nilpotent, i.e., some power of self is zero.

        EXAMPLES:
            sage: a = Integers(90384098234^3)
            sage: factor(a.order())
            2^3 * 191^3 * 236607587^3
            sage: b = a(2*191)
            sage: b.is_nilpotent()
            False
            sage: b = a(2*191*236607587)
            sage: b.is_nilpotent()
            True

        ALGORITHM: Let $m \geq  \log_2(n)$, where $n$ is the modulus.
        Then $x \in \ZZ/n\ZZ$ is nilpotent if and only if $x^m = 0$.

        PROOF: This is clear if you reduce to the prime power case,
        which you can do via the Chinese Remainder Theorem.

        We could alternatively factor n and check to see if the prime
        divisors of n all divide x.  This is asymptotically slower :-).
        """
        if self.is_zero():
            return True
        m = self.__modulus.sageInteger.exact_log(2) + 1
        return (self**m).is_zero()

    #################################################################
    # Interfaces
    #################################################################
    def _pari_init_(self):
        return 'Mod(%s,%s)'%(str(self), self.__modulus.sageInteger)

    def pari(self):
        return pari(self._pari_init_()) # TODO: is this called implicitly anywhere?

    def _gap_init_(self):
        r"""
        Return string representation of corresponding GAP object.

        This can be slow since non-prime GAP finite field elements are
        represented as powers of a generator for the multiplicative
        group, so the discrete log problem must be solved.

        \note{This function will create a meaningless GAP object if the
        modulus is not a power of a prime.  Also, the modulus must
        be $\leq 65536$.}

        EXAMPLES:
            sage: a = Mod(2,19)
            sage: gap(a)
            Z(19)
            sage: a._gap_(gap)
            Z(19)
            sage: gap(a).Int()
            2
            sage: b = Mod(0,25)
            sage: gap(b)
            0*Z(5)
        """
        R = self.parent()
        m = self.__modulus.sageInteger

        if m > 65536:
            raise ValueError, "order must be at most 65536."

        if self == 0:
            return '0*Z(%s)'%m

        # I couldn't find a guarentee in the GAP docs that the
        # root of unity they use must be the smallest.   This
        # was *not* the case in MAGMA once, so who knows, especially
        # when the order of the ring is not prime.  So we make
        # no such dangerous assumptions (for now).

        # Find the root of unity used by Gap.
        from sage.interfaces.all import gap        # here to reduce dependencies
        g = int(gap.eval('Int(Z(%s))'%m))
        n = self.log(R(g))
        return 'Z(%s)^%s'%(m, n)

    def _magma_init_(self):
        """
        Coercion to Magma.

        EXAMPLES:
            sage: a = Integers(15)(4)
            sage: b = magma(a)                # optional
            sage: b.Type()                    # optional
            RngIntResElt
            sage: b^2                         # optional
            1
        """
        return '%s!%s'%(self.parent()._magma_init_(), self)

    def log(self, b=None):
        r"""
        Return integer $x$ such that $b^x = a$, where $a$ is self.

        INPUT:
            self -- unit modulo N
            b -- a *generator* of the multiplicative group modulo N.
            If b is not given, R.multiplicative_generator() is used,
            where R is the parent of self.

        OUTPUT:
            Integer $x$ such that $b^x = a$.

        NOTE: The base must not be too big or the current
        implementation, which is in PARI, will fail.

        EXAMPLES:
            sage: r = Integers(125)
            sage: b = r.multiplicative_generator()^3
            sage: a = b^17
            sage: a.log(b)
            17
            sage: a.log()
            63

        A bigger example.
            sage: FF = FiniteField(2^32+61)
            sage: c = FF(4294967356)
            sage: x = FF(2)
            sage: a = c.log(x)
            sage: a
            2147483678
            sage: x^a
            4294967356

        Things that can go wrong.  E.g., if the base is not a
        generator for the multiplicative group, or not even a unit.
        You can sometimes use the function \code{discrete_log_generic}
        in general, but don't expect it to be very fast.

            sage: a = Mod(9, 100); b = Mod(3,100)
            sage: a.log(b)
            Traceback (most recent call last):
            ...
            ValueError: base (=3) for discrete log must generate multiplicative group
            sage: discrete_log_generic(b^2,b)
            2
            sage: a = Mod(16, 100); b = Mod(4,100)
            sage: a.log(b)
            Traceback (most recent call last):
            ...
            ValueError:  (8)
            PARI failed to compute discrete log (perhaps base is not a generator or is too large)
            sage: discrete_log_generic(a,b)
            Traceback (most recent call last):
            ...
            ArithmeticError: multiplicative order of 4 not defined since it is not a unit modulo 100

        AUTHOR:
            -- David Joyner and William Stein (2005-11)
            -- William Stein (2007-01-27): update to use PARI as requested by
               David Kohel.
        """
        if b is None:
            b = self._parent.multiplicative_generator()
        else:
            b = self._parent(b)
        cmd = 'b=Mod(%s,%s); if(znorder(b)!=eulerphi(%s),-1,znlog(%s,b))'%(b, self.__modulus.sageInteger,
                                                                           self.__modulus.sageInteger, self)
        try:
            n = Integer(pari(cmd))
            if n == -1:
                raise ValueError, "base (=%s) for discrete log must generate multiplicative group"%b
            return n
        except PariError, msg:
            raise ValueError, "%s\nPARI failed to compute discrete log (perhaps base is not a generator or is too large)"%msg


    def modulus(IntegerMod_abstract self):
        """
        EXAMPLES:
            sage: Mod(3,17).modulus()
            17
        """
        return self.__modulus.sageInteger


    def is_square(self):
        """
        EXAMPLES:
            sage: Mod(3,17).is_square()
            False
            sage: Mod(9,17).is_square()
            True
        """
        return bool(self.pari().issquare())

    def charpoly(self, var):
        """
        Returns the characteristic polynomial of this element.

        EXAMPLES:
            sage: k = GF(3)
            sage: a = k.gen()
            sage: a.charpoly('x')
            x + 2
            sage: a + 2
            0

        AUTHOR:
         -- Craig Citro
        """
        from polynomial.polynomial_ring import PolynomialRing
        R = PolynomialRing(self._parent, var)
        return R([-self,1])

    def norm(self):
        """
        Returns the norm of this element, which is itself. (This
        is here for compatibility with higher order finite fields.)

        EXAMPLES:
            sage: k = GF(691)
            sage: a = k(389)
            sage: a.norm()
            389

        AUTHOR:
         -- Craig Citro
        """
        return self

    def trace(self):
        """
        Returns the trace of this element, which is itself. (This
        is here for compatibility with higher order finite fields.)

        EXAMPLES:
            sage: k = GF(691)
            sage: a = k(389)
            sage: a.trace()
            389

        AUTHOR:
         -- Craig Citro
        """
        return self

    def sqrt(self):
        """
        Same as self.square_root().
        """
        return self.square_root()

    def square_root(self):
        """
        EXAMPLES:
            sage: mod(-1, 17).square_root()
            4
            sage: mod(5, 389).square_root()
            86
        """
        try:
            return self.parent()(self.pari().sqrt())  # TODO: implement directly
        except PariError:
            raise ValueError, "self must be a square."

    def rational_reconstruction(self):
        """
        EXAMPLES:
            sage: R = IntegerModRing(97)
            sage: a = R(2) / R(3)
            sage: a
            33
            sage: a.rational_reconstruction()
            2/3
        """
        return self.lift().rational_reconstruction(self.modulus())

    def crt(IntegerMod_abstract self, IntegerMod_abstract other):
        """
        Use the Chinese Remainder Theorem to find an element of the
        integers modulo the product of the moduli that reduces to self
        and to other.  The modulus of other must be coprime to the
        modulus of self.
        EXAMPLES:
            sage: a = mod(3,5)
            sage: b = mod(2,7)
            sage: a.crt(b)
            23

            sage: a = mod(37,10^8)
            sage: b = mod(9,3^8)
            sage: a.crt(b)
            125900000037

        AUTHOR:
            -- Robert Bradshaw
        """
        cdef int_fast64_t new_modulus
        if not isinstance(self, IntegerMod_gmp) and not isinstance(other, IntegerMod_gmp):

            if other.__modulus.int64 == 1: return self
            new_modulus = self.__modulus.int64 * other.__modulus.int64
            if new_modulus < INTEGER_MOD_INT32_LIMIT:
                return self.__crt(other)

            elif new_modulus < INTEGER_MOD_INT64_LIMIT:
                if not isinstance(self, IntegerMod_int64):
                    self = IntegerMod_int64(self._parent, self.lift())
                if not isinstance(other, IntegerMod_int64):
                    other = IntegerMod_int64(other._parent, other.lift())
                return self.__crt(other)

        if not isinstance(self, IntegerMod_gmp):
            self = IntegerMod_gmp(self._parent, self.lift())

        if not isinstance(other, IntegerMod_gmp):
            other = IntegerMod_gmp(other._parent, other.lift())

        return self.__crt(other)


    def additive_order(self):
        r"""
        Returns the additive order of self.

        This is the same as \code{self.order()}.

        EXAMPLES:
            sage: Integers(20)(2).additive_order()
            10
            sage: Integers(20)(7).additive_order()
            20
            sage: Integers(90308402384902)(2).additive_order()
            45154201192451
        """
        n = self.__modulus.sageInteger
        return sage.rings.integer.Integer(n.__floordiv__(self.lift().gcd(n)))

    def multiplicative_order(self):
        """
        Returns the multiplicative order of self.

        EXAMPLES:
            sage: Mod(-1,5).multiplicative_order()
            2
            sage: Mod(1,5).multiplicative_order()
            1
            sage: Mod(0,5).multiplicative_order()
            Traceback (most recent call last):
            ...
            ArithmeticError: multiplicative order of 0 not defined since it is not a unit modulo 5
        """
        try:
            return sage.rings.integer.Integer(self.pari().order())  # pari's "order" is by default multiplicative
        except PariError:
            raise ArithmeticError, "multiplicative order of %s not defined since it is not a unit modulo %s"%(
                self, self.__modulus.sageInteger)

    def _repr_(self):
        return str(self.lift())

    def _latex_(self):
        return str(self)

    def _integer_(self):
        return self.lift()

    def _rational_(self):
        return rational.Rational(self.lift())




######################################################################
#      class IntegerMod_gmp
######################################################################


cdef class IntegerMod_gmp(IntegerMod_abstract):
    """
    Elements of $\Z/n\Z$ for n not small enough to be operated on in word size
    AUTHORS:
        -- Robert Bradshaw (2006-08-24)
    """

    def __init__(IntegerMod_gmp self, parent, value, empty=False):
        """
        EXAMPLES:
            sage: a = mod(5,14^20)
            sage: type(a)
            <type 'sage.rings.integer_mod.IntegerMod_gmp'>
            sage: loads(dumps(a)) == a
            True
        """
        mpz_init(self.value)
        IntegerMod_abstract.__init__(self, parent)
        if empty:
            return
        cdef sage.rings.integer.Integer z
        if isinstance(value, sage.rings.integer.Integer):
            z = value
        elif isinstance(value, rational.Rational):
            z = value % self.__modulus.sageInteger
        else:
            z = sage.rings.integer_ring.Z(value)
        self.set_from_mpz(z.value)

    cdef IntegerMod_gmp _new_c(self):
        cdef IntegerMod_gmp x
        x = PY_NEW(IntegerMod_gmp)
        mpz_init(x.value)
        x.__modulus = self.__modulus
        x._parent = self._parent
        return x

    def __dealloc__(self):
        mpz_clear(self.value)

    cdef void set_from_mpz(IntegerMod_gmp self, mpz_t value):
        cdef sage.rings.integer.Integer modulus
        modulus = self.__modulus.sageInteger
        if mpz_sgn(value) == -1 or mpz_cmp(value, modulus.value) >= 0:
            mpz_mod(self.value, value, modulus.value)
        else:
            mpz_set(self.value, value)

    cdef mpz_t* get_value(IntegerMod_gmp self):
        return &self.value

    def __lshift__(IntegerMod_gmp self, int right):
        r"""
        Multiply self by $2^\text{right}$ very quickly via bit shifting.

        EXAMPLES:
            sage: e = Mod(19, 10^10)
            sage: e << 102
            9443608576
        """
        cdef IntegerMod_gmp x
        x = self._new_c()
        mpz_mul_2exp(x.value, self.value, right)
        mpz_fdiv_r(x.value, x.value, self.__modulus.sageInteger.value)
        return x

    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        EXAMPLES:
            sage: mod(5,13^20) == mod(5,13^20)
            True
            sage: mod(5,13^20) == mod(-5,13^20)
            False
            sage: mod(5,13^20) == mod(-5,13)
            False
        """
        cdef int i
        i = mpz_cmp((<IntegerMod_gmp>left).value, (<IntegerMod_gmp>right).value)
        if i < 0:
            return -1
        elif i == 0:
            return 0
        else:
            return 1

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)


    def is_one(IntegerMod_gmp self):
        """
        Returns \\code{True} if this is $1$, otherwise \\code{False}.

        EXAMPLES:
            sage: mod(1,5^23).is_one()
            True
            sage: mod(0,5^23).is_one()
            False
        """
        return bool(mpz_cmp_si(self.value, 1) == 0)

    def is_zero(IntegerMod_gmp self):
        """
        Returns \\code{True} if this is $0$, otherwise \\code{False}.

        EXAMPLES:
            sage: mod(13,5^23).is_zero()
            False
            sage: (mod(25,5^23)^23).is_zero()
            True
        """
        return bool(mpz_cmp_si(self.value, 0) == 0)

    def is_unit(self):
        return bool(self.lift().gcd(self.modulus()) == 1)

    def __crt(IntegerMod_gmp self, IntegerMod_gmp other):
        cdef IntegerMod_gmp lift, x
        cdef sage.rings.integer.Integer modulus, other_modulus

        modulus = self.__modulus.sageInteger
        other_modulus = other.__modulus.sageInteger
        lift = IntegerMod_gmp(integer_mod_ring.IntegerModRing(modulus*other_modulus), None, empty=True)
        try:
            if mpz_cmp(self.value, other.value) > 0:
                x = (other - IntegerMod_gmp(other._parent, self.lift())) / IntegerMod_gmp(other._parent, modulus)
                mpz_mul(lift.value, x.value, modulus.value)
                mpz_add(lift.value, lift.value, self.value)
            else:
                x = (self - IntegerMod_gmp(self._parent, other.lift())) / IntegerMod_gmp(self._parent, other_modulus)
                mpz_mul(lift.value, x.value, other_modulus.value)
                mpz_add(lift.value, lift.value, other.value)
            return lift
        except ZeroDivisionError:
            raise ZeroDivisionError, "moduli must be coprime"


    def __copy__(IntegerMod_gmp self):
        cdef IntegerMod_gmp x
        x = self._new_c()
        mpz_set(x.value, self.value)

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        """
        EXAMPLES:
            sage: R = Integers(10^10)
            sage: R(7) + R(8)
            15
        """
        cdef IntegerMod_gmp x
        x = self._new_c()
        mpz_add(x.value, self.value, (<IntegerMod_gmp>right).value)
        if mpz_cmp(x.value, self.__modulus.sageInteger.value)  >= 0:
            mpz_sub(x.value, x.value, self.__modulus.sageInteger.value)
        return x;

    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        """
        EXAMPLES:
            sage: R = Integers(10^10)
            sage: R(7) - R(8)
            9999999999
        """
        cdef IntegerMod_gmp x
        x = self._new_c()
        mpz_sub(x.value, self.value, (<IntegerMod_gmp>right).value)
        if mpz_sgn(x.value) == -1:
            mpz_add(x.value, x.value, self.__modulus.sageInteger.value)
        return x;

    cdef ModuleElement _neg_c_impl(self):
        """
        EXAMPLES:
            sage: -mod(5,10^10)
            9999999995
            sage: -mod(0,10^10)
            0
        """
        if mpz_cmp_si(self.value, 0) == 0:
            return self
        cdef IntegerMod_gmp x
        x = self._new_c()
        mpz_sub(x.value, self.__modulus.sageInteger.value, self.value)
        return x

    cdef RingElement _mul_c_impl(self, RingElement right):
        """
        EXAMPLES:
            sage: R = Integers(10^11)
            sage: R(700000) * R(800000)
            60000000000
        """
        cdef IntegerMod_gmp x
        x = self._new_c()
        mpz_mul(x.value, self.value,  (<IntegerMod_gmp>right).value)
        mpz_fdiv_r(x.value, x.value, self.__modulus.sageInteger.value)
        return x

    cdef RingElement _div_c_impl(self, RingElement right):
        """
        EXAMPLES:
            sage: R = Integers(10^11)
            sage: R(3) / R(7)
            71428571429
        """
        return self._mul_c(~right)

    def __int__(self):
        return int(self.lift())

    def __index__(self):
        """
        Needed so integers modulo n can be used as list indices.

        EXAMPLES:
            sage: v = [1,2,3,4,5]
            sage: v[Mod(3,10^20)]
            4
        """
        return int(self.lift())

    def __long__(self):
        return long(self.lift())

    def __mod__(self, right):
        right = int(right)
        if self.modulus() % right != 0:
            raise ZeroDivisionError, "Error - reduction modulo right not defined."
        return IntegerMod(integer_mod_ring.IntegerModRing(right, self))

    def __pow__(IntegerMod_gmp self, right, m): # NOTE: m ignored, always use modulus of parent ring
        """
        EXAMPLES:
            sage: R = Integers(10^10)
            sage: R(2)^1000
            5668069376
            sage: p = next_prime(11^10)
            sage: R = Integers(p)
            sage: R(9876)^(p-1)
            1
        """
        cdef sage.rings.integer.Integer exp
        exp = sage.rings.integer_ring.Z(right)
        cdef IntegerMod_gmp x
        x = self._new_c()
        _sig_on
        mpz_powm(x.value, self.value, exp.value, self.__modulus.sageInteger.value)
        _sig_off
        return x

    def __rshift__(IntegerMod_gmp self, int right):
        r"""
        Divide self by $2^{\text{right}}$ and take floor via bit shifting.

        EXAMPLES:
            sage: e = Mod(1000001, 2^32-1)
            sage: e >> 5
            31250
        """
        cdef IntegerMod_gmp x
        x = self._new_c()
        mpz_fdiv_q_2exp(x.value, self.value, right)
        return x

    def __invert__(IntegerMod_gmp self):
        """
        Return the multiplicative inverse of self.

        EXAMPLES:
            sage: a = mod(3,10^100); type(a)
            <type 'sage.rings.integer_mod.IntegerMod_gmp'>
            sage: ~a
            6666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666667
            sage: ~mod(2,10^100)
            Traceback (most recent call last):
            ...
            ZeroDivisionError: Inverse does not exist.
        """
        if self.is_zero():
            raise ZeroDivisionError, "Inverse does not exist."

        cdef IntegerMod_gmp x
        x = self._new_c()
        if (mpz_invert(x.value, self.value, self.__modulus.sageInteger.value)):
            return x
        else:
            raise ZeroDivisionError, "Inverse does not exist."

    def lift(IntegerMod_gmp self):
        """
        Lift an integer modulo $n$ to the integers.

        EXAMPLES:
            sage: a = Mod(8943, 2^70); type(a)
            <type 'sage.rings.integer_mod.IntegerMod_gmp'>
            sage: lift(a)
            8943
            sage: a.lift()
            8943
        """
        cdef sage.rings.integer.Integer z
        z = sage.rings.integer.Integer()
        z.set_from_mpz(self.value)
        return z

    def __float__(self):
        return float(self.lift())

    def __hash__(self):
        """
        EXAMPLES:
            sage: a = Mod(8943, 2^100)
            sage: hash(a)
            8943
        """
#        return mpz_pythonhash(self.value)
        return hash(self.lift())



######################################################################
#      class IntegerMod_int
######################################################################


cdef class IntegerMod_int(IntegerMod_abstract):
    """
    Elements of $\Z/n\Z$ for n small enough to be operated on in 32 bits
    AUTHORS:
        -- Robert Bradshaw (2006-08-24)
    """

    def __init__(self, parent, value, empty=False):
        """
        EXAMPLES:
            sage: a = Mod(10,30); a
            10
            sage: loads(a.dumps()) == a
            True
        """
        IntegerMod_abstract.__init__(self, parent)
        if empty:
            return
        cdef int_fast32_t x
        if PY_TYPE_CHECK(value, int):
            x = value
            self.ivalue = x % self.__modulus.int32
            if self.ivalue < 0:
                self.ivalue = self.ivalue + self.__modulus.int32
            return
        cdef sage.rings.integer.Integer z
        if PY_TYPE_CHECK(value, sage.rings.integer.Integer):
            z = value
        elif isinstance(value, rational.Rational):
            z = value % self.__modulus.sageInteger
        else:
            z = sage.rings.integer_ring.Z(value)
        self.set_from_mpz(z.value)

    cdef IntegerMod_int _new_c(self, int_fast32_t value):
        if self.__modulus.table is not None:
            return self.__modulus.lookup(value)
        cdef IntegerMod_int x
        x = PY_NEW(IntegerMod_int)
        x.__modulus = self.__modulus
        x._parent = self._parent
        x.ivalue = value
        return x

    cdef void set_from_mpz(IntegerMod_int self, mpz_t value):
        if mpz_sgn(value) == -1 or mpz_cmp_si(value, self.__modulus.int32) >= 0:
            self.ivalue = mpz_fdiv_ui(value, self.__modulus.int32)
        else:
            self.ivalue = mpz_get_si(value)

    cdef void set_from_int(IntegerMod_int self, int_fast32_t ivalue):
        if ivalue < 0:
            self.ivalue = self.__modulus.int32 + (ivalue % self.__modulus.int32)
        elif ivalue >= self.__modulus.int32:
            self.ivalue = ivalue % self.__modulus.int32
        else:
            self.ivalue = ivalue

    cdef int_fast32_t get_int_value(IntegerMod_int self):
        return self.ivalue



    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        EXAMPLES:
            sage: mod(5,13) == mod(-8,13)
            True
            sage: mod(5,13) == mod(8,13)
            False
            sage: mod(5,13) == mod(5,24)
            False
            sage: mod(0, 13) == 0
            True
            sage: mod(0, 13) == int(0)
            True
        """
        if (<IntegerMod_int>left).ivalue == (<IntegerMod_int>right).ivalue:
            return 0
        elif (<IntegerMod_int>left).ivalue < (<IntegerMod_int>right).ivalue:
            return -1
        else:
            return 1

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)


    def is_one(IntegerMod_int self):
        """
        Returns \\code{True} if this is $1$, otherwise \\code{False}.

        EXAMPLES:
            sage: mod(6,5).is_one()
            True
            sage: mod(0,5).is_one()
            False
        """
        return bool(self.ivalue == 1)

    def is_zero(IntegerMod_int self):
        """
        Returns \\code{True} if this is $0$, otherwise \\code{False}.

        EXAMPLES:
            sage: mod(13,5).is_zero()
            False
            sage: mod(25,5).is_zero()
            True
        """
        return bool(self.ivalue == 0)

    def is_unit(IntegerMod_int self):
        return bool(gcd_int(self.ivalue, self.__modulus.int32) == 1)

    def __crt(IntegerMod_int self, IntegerMod_int other):
        """
        Use the Chinese Remainder Theorem to find an element of the
        integers modulo the product of the moduli that reduces to self
        and to other.  The modulus of other must be coprime to the
        modulus of self.
        EXAMPLES:
            sage: a = mod(3,5)
            sage: b = mod(2,7)
            sage: a.crt(b)
            23

        AUTHOR:
            -- Robert Bradshaw
        """
        cdef IntegerMod_int lift
        cdef int_fast32_t x

        lift = IntegerMod_int(integer_mod_ring.IntegerModRing(self.__modulus.int32 * other.__modulus.int32), None, empty=True)

        try:
            x = (other.ivalue - self.ivalue % other.__modulus.int32) * mod_inverse_int(self.__modulus.int32, other.__modulus.int32)
            lift.set_from_int( x * self.__modulus.int32 + self.ivalue )
            return lift
        except ZeroDivisionError:
            raise ZeroDivisionError, "moduli must be coprime"


    def __copy__(IntegerMod_int self):
        return self._new_c(self.ivalue)

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        """
        EXAMPLES:
            sage: R = Integers(10)
            sage: R(7) + R(8)
            5
        """
        cdef int_fast32_t x
        x = self.ivalue + (<IntegerMod_int>right).ivalue
        if x >= self.__modulus.int32:
            x = x - self.__modulus.int32
        return self._new_c(x)

    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        """
        EXAMPLES:
            sage: R = Integers(10)
            sage: R(7) - R(8)
            9
        """
        cdef int_fast32_t x
        x = self.ivalue - (<IntegerMod_int>right).ivalue
        if x < 0:
            x = x + self.__modulus.int32
        return self._new_c(x)

    cdef ModuleElement _neg_c_impl(self):
        """
        EXAMPLES:
            sage: -mod(7,10)
            3
            sage: -mod(0,10)
            0
        """
        if self.ivalue == 0:
            return self
        return self._new_c(self.__modulus.int32 - self.ivalue)

    cdef RingElement _mul_c_impl(self, RingElement right):
        """
        EXAMPLES:
            sage: R = Integers(10)
            sage: R(7) * R(8)
            6
        """
        return self._new_c((self.ivalue * right.ivalue) % self.__modulus.int32)

    cdef RingElement _div_c_impl(self, RingElement right):
        """
        EXAMPLES:
            sage: R = Integers(10)
            sage: R(2)/3
            4
        """
        cdef int_fast32_t x
        x = (self.ivalue * mod_inverse_int(
            (<IntegerMod_int>right).ivalue, self.__modulus.int32) ) % self.__modulus.int32
        return self._new_c(x)

    def __int__(IntegerMod_int self):
        return self.ivalue

    def __index__(self):
        """
        Needed so integers can be used as list indices.

        EXAMPLES:
            sage: v = [1,2,3,4,5]
            sage: v[Mod(10,7)]
            4
        """
        return self.ivalue

    def __long__(IntegerMod_int self):
        return self.ivalue

    def __mod__(IntegerMod_int self, right):
        right = int(right)
        if self.__modulus.int32 % right != 0:
            raise ZeroDivisionError, "reduction modulo right not defined."
        return integer_mod_ring.IntegerModRing(right)(self)

    def __lshift__(IntegerMod_int self, int right):
        r"""
        Multiply self by $2^\text{right}$ very quickly via bit shifting.

        EXAMPLES:
            sage: e = Mod(5, 2^10 - 1)
            sage: e<<5
            160
            sage: e*2^5
            160
        """
        cdef IntegerMod_int x
        x = IntegerMod_int(self._parent, None, empty=True)
        x.ivalue = (self.ivalue << right) % self.__modulus.int32
        return x

    def __rshift__(IntegerMod_int self, int right):
        """
        Divide self by $2^{\text{right}}$ and take floor via bit shifting.

        EXAMPLES:
            sage: e = Mod(8, 2^5 - 1)
            sage: e >> 3
            1
            sage: int(e)/int(2^3)
            1
        """
        cdef IntegerMod_int x
        x = IntegerMod_int(self._parent, None, empty=True)
        x.ivalue = (self.ivalue >> right) % self.__modulus.int32
        return x

    def __pow__(IntegerMod_int self, right, m): # NOTE: m ignored, always use modulus of parent ring
        """
        EXAMPLES:
            sage: R = Integers(10)
            sage: R(2)^10
            4
            sage: R = Integers(389)
            sage: R(7)^388
            1
        """
        cdef sage.rings.integer.Integer exp, base
        exp = sage.rings.integer_ring.Z(right)
        cdef int_fast32_t x
        cdef mpz_t x_mpz
        if mpz_sgn(exp.value) >= 0 and mpz_cmp_si(exp.value, 100000) < 0:  # TODO: test to find a good threshold
            x = mod_pow_int(self.ivalue, mpz_get_si(exp.value), self.__modulus.int32)
        else:
            mpz_init(x_mpz)
            _sig_on
            base = self.lift()
            mpz_powm(x_mpz, base.value, exp.value, self.__modulus.sageInteger.value)
            _sig_off
            x = mpz_get_si(x_mpz)
            mpz_clear(x_mpz)
        return self._new_c(x)


    def __invert__(IntegerMod_int self):
        """
        Return the multiplicative inverse of self.

        EXAMPLES:
            sage: ~mod(7,100)
            43
        """
        return self._new_c(mod_inverse_int(self.ivalue, self.__modulus.int32))

    def lift(IntegerMod_int self):
        """
        Lift an integer modulo $n$ to the integers.

        EXAMPLES:
            sage: a = Mod(8943, 2^10); type(a)
            <type 'sage.rings.integer_mod.IntegerMod_int'>
            sage: lift(a)
            751
            sage: a.lift()
            751
        """
        cdef sage.rings.integer.Integer z
        z = sage.rings.integer.Integer()
        mpz_set_si(z.value, self.ivalue)
        return z

    def __float__(IntegerMod_int self):
        return float(self.ivalue)

    def __hash__(self):
        """
        EXAMPLES:
            sage: a = Mod(89, 2^10)
            sage: hash(a)
            89
        """
        return hash(self.ivalue)

### End of class


cdef int_fast32_t gcd_int(int_fast32_t a, int_fast32_t b):
    """
    Returns the gcd of a and b
    For use with IntegerMod_int
    AUTHOR:
      -- Robert Bradshaw
    """
    cdef int_fast32_t tmp
    if a < b:
        tmp = b
        b = a
        a = tmp
    while b:
        tmp = b
        b = a % b
        a = tmp
    return a


cdef int_fast32_t mod_inverse_int(int_fast32_t x, int_fast32_t n) except 0:
    """
    Returns y such that xy=1 mod n
    For use in IntegerMod_int
    AUTHOR:
      -- Robert Bradshaw
    """
    cdef int_fast32_t tmp, a, b, last_t, t, next_t, q
    a = n
    b = x
    t = 0
    next_t = 1
    while b:
        # a = s * n + t * x
        if b == 1:
            next_t = next_t % n
            if next_t < 0:
                next_t = next_t + n
            return next_t
        q = a / b
        tmp = b
        b = a % b
        a = tmp
        last_t = t
        t = next_t
        next_t = last_t - q * t
    raise ZeroDivisionError, "Inverse does not exist."


cdef int_fast32_t mod_pow_int(int_fast32_t base, int_fast32_t exp, int_fast32_t n):
    """
    Returns base^exp mod n
    For use in IntegerMod_int
    AUTHOR:
      -- Robert Bradshaw
    """
    cdef int_fast32_t prod, pow2
    if exp <= 5:
        if exp == 0: return 1
        if exp == 1: return base
        prod = base * base % n
        if exp == 2: return prod
        if exp == 3: return (prod * base) % n
        if exp == 4: return (prod * prod) % n

    pow2 = base
    if exp % 2: prod = base
    else: prod = 1
    exp = exp >> 1
    while(exp != 0):
        pow2 = pow2 * pow2
        if pow2 >= INTEGER_MOD_INT32_LIMIT: pow2 = pow2 % n
        if exp % 2:
            prod = prod * pow2
            if prod >= INTEGER_MOD_INT32_LIMIT: prod = prod % n
        exp = exp >> 1

    if prod > n:
        prod = prod % n
    return prod


def test_gcd(a, b):
    return gcd_int(int(a), int(b))

def test_mod_inverse(a, b):
    return mod_inverse_int(int(a), int(b))



######################################################################
#      class IntegerMod_int64
######################################################################

cdef class IntegerMod_int64(IntegerMod_abstract):
    """
    Elements of $\Z/n\Z$ for n small enough to be operated on in 64 bits
    AUTHORS:
        -- Robert Bradshaw (2006-09-14)
    """

    def __init__(self, parent, value, empty=False):
        """
        EXAMPLES:
            sage: a = Mod(10,3^10); a
            10
            sage: type(a)
            <type 'sage.rings.integer_mod.IntegerMod_int64'>
            sage: loads(a.dumps()) == a
            True
            sage: Mod(5, 2^31)
            5
        """
        IntegerMod_abstract.__init__(self, parent)
        if empty:
            return
        cdef int_fast64_t x
        if PY_TYPE_CHECK(value, int):
            x = value
            self.ivalue = x % self.__modulus.int64
            if self.ivalue < 0:
                self.ivalue = self.ivalue + self.__modulus.int64
            return
        cdef sage.rings.integer.Integer z
        if isinstance(value, sage.rings.integer.Integer):
            z = value
        elif isinstance(value, rational.Rational):
            z = value % self.__modulus.sageInteger
        else:
            z = sage.rings.integer_ring.Z(value)
        self.set_from_mpz(z.value)

    cdef IntegerMod_int64 _new_c(self, int_fast64_t value):
        cdef IntegerMod_int64 x
        x = PY_NEW(IntegerMod_int64)
        x.__modulus = self.__modulus
        x._parent = self._parent
        x.ivalue = value
        return x

    cdef void set_from_mpz(IntegerMod_int64 self, mpz_t value):
        if mpz_sgn(value) == -1 or mpz_cmp_si(value, self.__modulus.int64) >= 0:
            self.ivalue = mpz_fdiv_ui(value, self.__modulus.int64)
        else:
            self.ivalue = mpz_get_si(value)

    cdef void set_from_int(IntegerMod_int64 self, int_fast64_t ivalue):
        if ivalue < 0:
            self.ivalue = self.__modulus.int64 + (ivalue % self.__modulus.int64) # Is ivalue % self.__modulus.int64 actually negative?
        elif ivalue >= self.__modulus.int64:
            self.ivalue = ivalue % self.__modulus.int64
        else:
            self.ivalue = ivalue

    cdef int_fast64_t get_int_value(IntegerMod_int64 self):
        return self.ivalue


    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        EXAMPLES:
            sage: mod(5,13^5) == mod(13^5+5,13^5)
            True
            sage: mod(5,13^5) == mod(8,13^5)
            False
            sage: mod(5,13^5) == mod(5,13)
            True
            sage: mod(0, 13^5) == 0
            True
            sage: mod(0, 13^5) == int(0)
            True
        """
        if (<IntegerMod_int64>left).ivalue == (<IntegerMod_int64>right).ivalue: return 0
        elif (<IntegerMod_int64>left).ivalue < (<IntegerMod_int64>right).ivalue: return -1
        else: return 1

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)


    def is_one(IntegerMod_int64 self):
        """
        Returns \\code{True} if this is $1$, otherwise \\code{False}.

        EXAMPLES:
            sage: (mod(-1,5^10)^2).is_one()
            True
            sage: mod(0,5^10).is_one()
            False
        """
        return bool(self.ivalue == 1)

    def is_zero(IntegerMod_int64 self):
        """
        Returns \\code{True} if this is $0$, otherwise \\code{False}.

        EXAMPLES:
            sage: mod(13,5^10).is_zero()
            False
            sage: mod(5^12,5^10).is_zero()
            True
        """
        return bool(self.ivalue == 0)

    def is_unit(IntegerMod_int64 self):
        return bool(gcd_int64(self.ivalue, self.__modulus.int64) == 1)

    def __crt(IntegerMod_int64 self, IntegerMod_int64 other):
        """
        Use the Chinese Remainder Theorem to find an element of the
        integers modulo the product of the moduli that reduces to self
        and to other.  The modulus of other must be coprime to the
        modulus of self.
        EXAMPLES:
            sage: a = mod(3,5^10)
            sage: b = mod(2,7)
            sage: a.crt(b)
            29296878
            sage: type(a.crt(b)) == type(b.crt(a)) and type(a.crt(b)) == type(mod(1, 7 * 5^10))
            True

            sage: a = mod(3,10^10)
            sage: b = mod(2,9)
            sage: a.crt(b)
            80000000003
            sage: type(a.crt(b)) == type(b.crt(a)) and type(a.crt(b)) == type(mod(1, 9 * 10^10))
            True

        AUTHOR:
            -- Robert Bradshaw
        """
        cdef IntegerMod_int64 lift
        cdef int_fast64_t x

        lift = IntegerMod_int64(integer_mod_ring.IntegerModRing(self.__modulus.int64 * other.__modulus.int64), None, empty=True)

        try:
            x = (other.ivalue - self.ivalue % other.__modulus.int64) * mod_inverse_int64(self.__modulus.int64, other.__modulus.int64)
            lift.set_from_int( x * self.__modulus.int64 + self.ivalue )
            return lift
        except ZeroDivisionError:
            raise ZeroDivisionError, "moduli must be coprime"


    def __copy__(IntegerMod_int64 self):
        return self._new_c(self.ivalue)

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        """
        EXAMPLES:
            sage: R = Integers(10^5)
            sage: R(7) + R(8)
            15
        """
        cdef int_fast64_t x
        x = self.ivalue + (<IntegerMod_int64>right).ivalue
        if x >= self.__modulus.int64:
            x = x - self.__modulus.int64
        return self._new_c(x)

    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        """
        EXAMPLES:
            sage: R = Integers(10^5)
            sage: R(7) - R(8)
            99999
        """
        cdef int_fast64_t x
        x = self.ivalue - (<IntegerMod_int64>right).ivalue
        if x < 0:
            x = x + self.__modulus.int64
        return self._new_c(x)

    cdef ModuleElement _neg_c_impl(self):
        """
        EXAMPLES:
            sage: -mod(7,10^5)
            99993
            sage: -mod(0,10^6)
            0
        """
        if self.ivalue == 0:
            return self
        return self._new_c(self.__modulus.int64 - self.ivalue)

    cdef RingElement _mul_c_impl(self, RingElement right):
        """
        EXAMPLES:
            sage: R = Integers(10^5)
            sage: R(700) * R(800)
            60000
        """
        return self._new_c((self.ivalue * (<IntegerMod_int64>right).ivalue) % self.__modulus.int64)

    cdef RingElement _div_c_impl(self, RingElement right):
        """
        EXAMPLES:
            sage: R = Integers(10^5)
            sage: R(2)/3
            33334
        """
        return self._new_c((self.ivalue * mod_inverse_int64((<IntegerMod_int64>right).ivalue,
                                   self.__modulus.int64) ) % self.__modulus.int64)

    def __int__(IntegerMod_int64 self):
        return self.ivalue

    def __long__(IntegerMod_int64 self):
        return self.ivalue

    def __mod__(IntegerMod_int64 self, right):
        right = int(right)
        if self.__modulus.int64 % right != 0:
            raise ZeroDivisionError, "Error - reduction modulo right not defined."
        return integer_mod_ring.IntegerModRing(right)(self)

    def __pow__(IntegerMod_int64 self, right, m): # NOTE: m ignored, always use modulus of parent ring
        """
        EXAMPLES:
            sage: R = Integers(10)
            sage: R(2)^10
            4
            sage: p = next_prime(10^5)
            sage: R = Integers(p)
            sage: R(1234)^(p-1)
            1
        """
        cdef sage.rings.integer.Integer exp, base
        exp = sage.rings.integer_ring.Z(right)
        cdef int_fast64_t x
        cdef mpz_t x_mpz
        if mpz_sgn(exp.value) >= 0 and mpz_cmp_si(exp.value, 100000) < 0:  # TODO: test to find a good threshold
            x = mod_pow_int64(self.ivalue, mpz_get_si(exp.value), self.__modulus.int64)
        else:
            mpz_init(x_mpz)
            _sig_on
            base = self.lift()
            mpz_powm(x_mpz, base.value, exp.value, self.__modulus.sageInteger.value)
            _sig_off
            x = mpz_get_si(x_mpz)
            mpz_clear(x_mpz)
        return self._new_c(x)

    def __lshift__(IntegerMod_int64 self, int right):
        r"""
        EXAMPLES:
            sage: e = Mod(5, 2^31 - 1)
            sage: e<<32
            10
            sage: e*2^32
            10
        """
        return self._new_c((self.ivalue << right) % self.__modulus.int64)

    def __rshift__(IntegerMod_int64 self, int right):
        """
        Divide self by $2^{\text{right}}$ and take floor via bit shifting.

        EXAMPLES:
            sage: e = Mod(8, 2^31 - 1)
            sage: e >> 3
            1
            sage: int(e)/int(2^3)
            1
        """
        return self._new_c((self.ivalue >> right) % self.__modulus.int64)

    def __invert__(IntegerMod_int64 self):
        """
        Return the multiplicative inverse of self.

        EXAMPLES:
            sage: a = mod(7,2^40); type(a)
            <type 'sage.rings.integer_mod.IntegerMod_gmp'>
            sage: ~a
            471219269047
            sage: a
            7
        """
        return self._new_c(mod_inverse_int64(self.ivalue, self.__modulus.int64))

    def lift(IntegerMod_int64 self):
        """
        Lift an integer modulo $n$ to the integers.

        EXAMPLES:
            sage: a = Mod(8943, 2^25); type(a)
            <type 'sage.rings.integer_mod.IntegerMod_int64'>
            sage: lift(a)
            8943
            sage: a.lift()
            8943
        """
        cdef sage.rings.integer.Integer z
        z = sage.rings.integer.Integer()
        mpz_set_si(z.value, self.ivalue)
        return z

    def __float__(IntegerMod_int64 self):
        """
        Coerce self to a float.

        EXAMPLES:
            sage: a = Mod(8943, 2^35)
            sage: float(a)
            8943.0
        """
        return float(self.ivalue)

    def __hash__(self):
        """
        Compute hash of self.

        This is a combination of the hash of the underlying integer
        and the modulus.

        EXAMPLES:
            sage: a = Mod(8943, 2^35)
            sage: hash(a)
            8943
        """

        return hash(self.ivalue)

### End of class


cdef int_fast64_t gcd_int64(int_fast64_t a, int_fast64_t b):
    """
    Returns the gcd of a and b
    For use with IntegerMod_int64
    AUTHOR:
      -- Robert Bradshaw
    """
    cdef int_fast64_t tmp
    if a < b:
        tmp = b
        b = a
        a = tmp
    while b:
        tmp = b
        b = a % b
        a = tmp
    return a


cdef int_fast64_t mod_inverse_int64(int_fast64_t x, int_fast64_t n) except 0:
    """
    Returns y such that xy=1 mod n
    For use in IntegerMod_int64
    AUTHOR:
      -- Robert Bradshaw
    """
    cdef int_fast64_t tmp, a, b, last_t, t, next_t, q
    a = n
    b = x
    t = 0
    next_t = 1
    while b:
        # a = s * n + t * x
        if b == 1:
            next_t = next_t % n
            if next_t < 0:
                next_t = next_t + n
            return next_t
        q = a / b
        tmp = b
        b = a % b
        a = tmp
        last_t = t
        t = next_t
        next_t = last_t - q * t
    raise ZeroDivisionError, "Inverse does not exist."


cdef int_fast64_t mod_pow_int64(int_fast64_t base, int_fast64_t exp, int_fast64_t n):
    """
    Returns base^exp mod n
    For use in IntegerMod_int64
    AUTHOR:
      -- Robert Bradshaw
    """
    cdef int_fast64_t prod, pow2
    if exp <= 5:
        if exp == 0: return 1
        if exp == 1: return base
        prod = base * base % n
        if exp == 2: return prod
        if exp == 3: return (prod * base) % n
        if exp == 4: return (prod * prod) % n

    pow2 = base
    if exp % 2: prod = base
    else: prod = 1
    exp = exp >> 1
    while(exp != 0):
        pow2 = pow2 * pow2
        if pow2 >= INTEGER_MOD_INT32_LIMIT: pow2 = pow2 % n
        if exp % 2:
            prod = prod * pow2
            if prod >= INTEGER_MOD_INT32_LIMIT: prod = prod % n
        exp = exp >> 1

    if prod > n:
        prod = prod % n
    return prod
