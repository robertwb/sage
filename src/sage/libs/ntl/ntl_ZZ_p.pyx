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

include "../../ext/interrupt.pxi"
include "../../ext/stdsage.pxi"
include "../../ext/cdefs.pxi"
include 'misc.pxi'
include 'decl.pxi'

from sage.rings.integer import Integer
from sage.rings.integer_ring import IntegerRing
from sage.rings.integer cimport Integer
from sage.libs.ntl.ntl_ZZ cimport ntl_ZZ
from sage.rings.integer cimport Integer
from sage.rings.integer_ring cimport IntegerRing_class

from sage.libs.ntl.ntl_ZZ import unpickle_class_args

from sage.libs.ntl.ntl_ZZ_pContext cimport ntl_ZZ_pContext_class
from sage.libs.ntl.ntl_ZZ_pContext import ntl_ZZ_pContext

ZZ_sage = IntegerRing()

def set_ZZ_p_modulus(ntl_ZZ p):
    ntl_ZZ_set_modulus(&p.x)

def ntl_ZZ_p_random():
    """
    Return a random number modulo p.
    """
    cdef ntl_ZZ_p y = ntl_ZZ_p()
    _sig_on
    ZZ_p_random(y.x)
    _sig_off
    return y


##############################################################################
#
# ZZ_p_c: integers modulo p
#
##############################################################################
cdef class ntl_ZZ_p:
    r"""
    The \class{ZZ_p} class is used to represent integers modulo $p$.
    The modulus $p$ may be any positive integer, not necessarily prime.

    Objects of the class \class{ZZ_p} are represented as a \code{ZZ} in the
    range $0, \ldots, p-1$.

    Each \class{ZZ_p} contains a pointer of a \class{ZZ_pContext} which
    contains pre-computed data for NTL.  These can be explicitly constructed
    and passed to the constructor of a \class{ZZ_p} or the \class{ZZ_pContext}
    method \code{ZZ_p} can be used to construct a \class{ZZ_p} element.

    This class takes care of making sure that the C++ library NTL global
    variable is set correctly before performing any arithmetic.
    """
    def __init__(self, v=None, modulus=None):
        r"""
        Initializes an NTL integer mod p.

        EXAMPLES:
            sage: c=ntl.ZZ_pContext(ntl.ZZ(11))
            sage: c.ZZ_p(12r)
            1
            sage: c.ZZ_p(Integer(95413094))
            7
            sage: c.ZZ_p(long(223895239852389582988))
            5
            sage: c.ZZ_p('-1')
            10

        AUTHOR: Joel B. Mohler (2007-06-14)
        """
        if PY_TYPE_CHECK( modulus, ntl_ZZ_pContext_class ):
            self.c = <ntl_ZZ_pContext_class>modulus
        elif modulus is not None:
            self.c = <ntl_ZZ_pContext_class>ntl_ZZ_pContext(ntl_ZZ(modulus))
        else:
            raise ValueError, "You must specify a modulus when creating a ZZ_p."

        self.c.restore_c()

        cdef ZZ_c temp
        if v is not None:
            _sig_on
            if PY_TYPE_CHECK(v, ntl_ZZ_p):
                self.x = (<ntl_ZZ_p>v).x
            elif PyInt_Check(v):
                self.x = int_to_ZZ_p(v)
            elif PyLong_Check(v):
                ZZ_set_pylong(temp, v)
                self.x = ZZ_to_ZZ_p(temp)
            elif isinstance(v, Integer):
                (<Integer>v)._to_ZZ(&temp)
                self.x = ZZ_to_ZZ_p(temp)
            else:
                v = str(v)
                ZZ_p_from_str(&self.x, v)
            _sig_off

    def __new__(self, v=None, modulus=None):
        ZZ_p_construct(&self.x)

    def __dealloc__(self):
        if <object>self.c is not None:
            self.c.restore_c()
        ZZ_p_destruct(&self.x)

    cdef ntl_ZZ_p _new(self):
        cdef ntl_ZZ_p r
        r = PY_NEW(ntl_ZZ_p)
        r.c = self.c
        return r

    def __reduce__(self):
        """
        sage: a = ntl.ZZ_p(4,7)
        sage: loads(dumps(a)) == a
        True
        """
        return unpickle_class_args, (ntl_ZZ_p, (self.lift(), self.get_modulus_context()))

    def get_modulus_context(self):
        return self.c

    def __repr__(self):
        self.c.restore_c()
        _sig_on
        return string_delete(ZZ_p_to_str(&self.x))

    def __richcmp__(ntl_ZZ_p self, ntl_ZZ_p other, op):
        r"""
        EXAMPLES:
            sage: c=ntl.ZZ_pContext(ntl.ZZ(11))
            sage: c.ZZ_p(12r)==c.ZZ_p(1)
            True
            sage: c.ZZ_p(35r)==c.ZZ_p(1)
            False
        """
        self.c.restore_c()
        if op != 2 and op != 3:
            raise TypeError, "Integers mod p are not ordered."

        cdef int t
#        cdef ntl_ZZ_p y
#        if not isinstance(other, ntl_ZZ_p):
#            other = ntl_ZZ_p(other)
#        y = other
        _sig_on
        t = ZZ_p_eq(&self.x, &other.x)
        _sig_off
        # t == 1 if self == other
        if op == 2:
            return t == 1
        elif op == 3:
            return t == 0

    def __invert__(ntl_ZZ_p self):
        r"""
        EXAMPLES:
            sage: c=ntl.ZZ_pContext(ntl.ZZ(11))
            sage: ~ntl.ZZ_p(2r,modulus=c)
            6
        """
        cdef ntl_ZZ_p r = self._new()
        _sig_on
        self.c.restore_c()
        ZZ_p_inv(r.x, self.x)
        _sig_off
        return r

    def __mul__(ntl_ZZ_p self, other):
        cdef ntl_ZZ_p y
        cdef ntl_ZZ_p r = self._new()
        if not PY_TYPE_CHECK(other, ntl_ZZ_p):
            other = ntl_ZZ_p(other,self.c)
        elif self.c is not (<ntl_ZZ_p>other).c:
            raise ValueError, "You can not perform arithmetic with elements of different moduli."
        y = other
        self.c.restore_c()
        ZZ_p_mul(r.x, self.x, y.x)
        return r

    def __sub__(ntl_ZZ_p self, other):
        if not PY_TYPE_CHECK(other, ntl_ZZ_p):
            other = ntl_ZZ_p(other,self.c)
        elif self.c is not (<ntl_ZZ_p>other).c:
            raise ValueError, "You can not perform arithmetic with elements of different moduli."
        cdef ntl_ZZ_p r = self._new()
        self.c.restore_c()
        ZZ_p_sub(r.x, self.x, (<ntl_ZZ_p>other).x)
        return r

    def __add__(ntl_ZZ_p self, other):
        cdef ntl_ZZ_p y
        cdef ntl_ZZ_p r = ntl_ZZ_p(modulus=self.c)
        if not PY_TYPE_CHECK(other, ntl_ZZ_p):
            other = ntl_ZZ_p(other,modulus=self.c)
        elif self.c is not (<ntl_ZZ_p>other).c:
            raise ValueError, "You can not perform arithmetic with elements of different moduli."
        y = other
        _sig_on
        self.c.restore_c()
        ZZ_p_add(r.x, self.x, y.x)
        _sig_off
        return r

    def __neg__(ntl_ZZ_p self):
        cdef ntl_ZZ_p r = ntl_ZZ_p(modulus=self.c)
        _sig_on
        self.c.restore_c()
        ZZ_p_negate(r.x, self.x)
        _sig_off
        return r

    def __pow__(ntl_ZZ_p self, long e, ignored):
        cdef ntl_ZZ_p r = ntl_ZZ_p(modulus=self.c)
        _sig_on
        self.c.restore_c()
        ZZ_p_power(r.x, self.x, e)
        _sig_off
        return r

    def __int__(self):
        return self.get_as_int()

    cdef int get_as_int(ntl_ZZ_p self):
        r"""
        Returns value as C int.
        Return value is only valid if the result fits into an int.

        AUTHOR: David Harvey (2006-08-05)
        """
        self.c.restore_c()
        return ZZ_p_to_int(self.x)

    def get_as_int_doctest(self):
        r"""
        This method exists solely for automated testing of get_as_int().

        sage: c=ntl.ZZ_pContext(ntl.ZZ(20))
        sage: x = ntl.ZZ_p(42,modulus=c)
        sage: i = x.get_as_int_doctest()
        sage: print i
        2
        sage: print type(i)
         <type 'int'>
        """
        self.c.restore_c()
        return self.get_as_int()

    cdef void set_from_int(ntl_ZZ_p self, int value):
        r"""
        Sets the value from a C int.

        AUTHOR: David Harvey (2006-08-05)
        """
        self.c.restore_c()
        self.x = int_to_ZZ_p(value)

    def set_from_int_doctest(self, value):
        r"""
        This method exists solely for automated testing of set_from_int().

        sage: c=ntl.ZZ_pContext(ntl.ZZ(20))
        sage: x = ntl.ZZ_p(modulus=c)
        sage: x.set_from_int_doctest(42)
        sage: x
         2
        """
        self.c.restore_c()
        self.set_from_int(int(value))

    def lift(self):
        cdef ntl_ZZ r = ntl_ZZ()
        self.c.restore_c()
        r.x = ZZ_p_rep(self.x)
        return r

    def modulus(self):
        r"""
        Returns the modulus as an NTL ZZ.

        sage: c=ntl.ZZ_pContext(ntl.ZZ(20))
        sage: n=ntl.ZZ_p(2983,c)
        sage: n.modulus()
        20
        """
        cdef ntl_ZZ r = ntl_ZZ()
        self.c.restore_c()
        ZZ_p_modulus( &r.x, &self.x )
        return r

    def _sage_(self):
        r"""
        Returns the value as a sage IntegerModRing.

        sage: c=ntl.ZZ_pContext(ntl.ZZ(20))
        sage: n=ntl.ZZ_p(2983,c)
        sage: type(n._sage_())
        <type 'sage.rings.integer_mod.IntegerMod_int'>
        sage: n
        3

        AUTHOR: Joel B. Mohler
        """
        from sage.rings.integer_mod_ring import IntegerModRing

        cdef ZZ_c rep
        self.c.restore_c()
        rep = ZZ_p_rep(self.x)
        return IntegerModRing(self.modulus().get_as_sage_int())((<IntegerRing_class>ZZ_sage)._coerce_ZZ(&rep))

    # todo: add wrapper for int_to_ZZ_p in wrap.cc?
