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
from sage.libs.ntl.ntl_ZZ_p cimport ntl_ZZ_p
from sage.rings.integer cimport Integer
from sage.rings.integer_ring cimport IntegerRing_class

from sage.libs.ntl.ntl_ZZ import unpickle_class_args

from sage.libs.ntl.ntl_ZZ_pContext cimport ntl_ZZ_pContext_class
from sage.libs.ntl.ntl_ZZ_pContext import ntl_ZZ_pContext

from sage.libs.ntl.ntl_ZZ_pEContext cimport ntl_ZZ_pEContext_class
from sage.libs.ntl.ntl_ZZ_pEContext import ntl_ZZ_pEContext


ZZ_sage = IntegerRing()

#def set_ZZ_pE_modulus(ntl_ZZ_pX f):
#    f.c.restore_c()
#    c = ntl_ZZ_pEContext_class(f)
#    c.restore_c()
#    return c

#def ntl_ZZ_pE_random():
#    """
#    Return a random number modulo p.
#    """
#    cdef ntl_ZZ_pE y = ntl_ZZ_pE()
#    _sig_on
#    y.x = *(<ntl_ZZ_pE_c>ZZ_pE_random())
#    _sig_off
#    return y


##############################################################################
#
# ZZ_pE_c: An extension of the integers modulo p
#
##############################################################################
cdef class ntl_ZZ_pE:
    r"""
    The \class{ZZ_pE} class is used to model $\Z / p\Z [x] / (f(x))$.
    The modulus $p$ may be any positive integer, not necessarily prime,
    and the modulus f is not required to be irreducible.

    Objects of the class \class{ZZ_pE} are represented as a \code{ZZ_pX} of
    degree less than the degree of $f$.

    Each \class{ZZ_pE} contains a pointer of a \class{ZZ_pEContext} which
    contains pre-computed data for NTL.  These can be explicitly constructed
    and passed to the constructor of a \class{ZZ_pE} or the \class{ZZ_pEContext}
    method \code{ZZ_pE} can be used to construct a \class{ZZ_pE} element.

    This class takes care of making sure that the C++ library NTL global
    variable is set correctly before performing any arithmetic.
    """
    def __init__(self, v=None, modulus=None):
        r"""
        Initializes an ntl ZZ_pE.

        EXAMPLES:
            sage: c=ntl.ZZ_pEContext(ntl.ZZ_pX([1,1,1],11))
            sage: c.ZZ_pE([13,4,1])
            [1 3]
            sage: c.ZZ_pE(Integer(95413094))
            [7]
            sage: c.ZZ_pE(long(223895239852389582988))
            [5]
            sage: c.ZZ_pE('[1]')
            [1]

        AUTHOR: David Roe (2007-9-25)
        """
        if PY_TYPE_CHECK( modulus, ntl_ZZ_pEContext_class ):
            self.c = <ntl_ZZ_pEContext_class>modulus
        elif PY_TYPE_CHECK( modulus, ntl_ZZ_pX ):
            modulus.get_modulus_context().restore()
            self.c = <ntl_ZZ_pEContext_class>ntl_ZZ_pEContext(<ntl_ZZ_pX>modulus)
        elif PY_TYPE_CHECK(v, ntl_ZZ_pE):
            self.c = (<ntl_ZZ_pE>v).c
        elif PY_TYPE_CHECK(v, tuple) and len(v) == 2 and PY_TYPE_CHECK(v[1], ntl_ZZ_pEContext_class):
            self.c = v[1]
            v = v[0]
        else:
            raise ValueError, "You must specify a modulus when creating a ZZ_pE."
        self.c.restore_c()

        cdef ZZ_c temp
        if v is not None:
            _sig_on
            if PY_TYPE_CHECK(v, ntl_ZZ_pE):
                if (<ntl_ZZ_pE>v).c is not self.c:
                    raise ValueError, "You cannot cast between rings with different moduli"
                self.x = (<ntl_ZZ_pE>v).x
            elif PY_TYPE_CHECK(v, ntl_ZZ_pX):
                if (<ntl_ZZ_pX>v).c is not self.c.pc:
                    raise ValueError, "You cannot cast between rings with different moduli"
                self.x = ZZ_pX_to_ZZ_pE((<ntl_ZZ_pX>v).x)
            elif PY_TYPE_CHECK(v, list) or PY_TYPE_CHECK(v, tuple):
                self.x = ZZ_pX_to_ZZ_pE((<ntl_ZZ_pX>ntl_ZZ_pX(v, self.c.pc)).x)
            elif PyInt_Check(v):
                self.x = long_to_ZZ_pE(v)
            elif PY_TYPE_CHECK(v, ntl_ZZ_p):
                self.x = ZZ_p_to_ZZ_pE((<ntl_ZZ_p>v).x)
            elif PyLong_Check(v):
                ZZ_set_pylong(temp, v)
                self.x = ZZ_to_ZZ_pE(temp)
            elif PY_TYPE_CHECK(v, ntl_ZZ):
                self.x = ZZ_to_ZZ_pE((<ntl_ZZ>v).x)
            elif PY_TYPE_CHECK(v, Integer):
                (<Integer>v)._to_ZZ(&temp)
                self.x = ZZ_to_ZZ_pE(temp)
            else:
                v = str(v)
                ZZ_pE_from_str(&self.x, PyString_AsString(v))
            _sig_off

    def __new__(ntl_ZZ_pE self, v=None, modulus=None):
        #################### WARNING ###################
        ## Before creating a ZZ_pE, you must create a ##
        ## ZZ_pEContext, and restore it.  In Python,  ##
        ## the error checking in __init__ will prevent##
        ## you from constructing an ntl_ZZ_pE         ##
        ## inappropriately.  However, from Cython, you##
        ## could do r = PY_NEW(ntl_ZZ_pE) without     ##
        ## first restoring a ZZ_pEContext, which could##
        ## have unforetunate consequences.  See _new  ##
        ## defined below for an example of the right  ##
        ## way to short-circuit __init__ (or just call##
        ## _new in your own code).                    ##
        ################################################
        if modulus is None:
            ZZ_pE_construct(&self.x)
            return
        if PY_TYPE_CHECK( modulus, ntl_ZZ_pEContext_class ):
            self.c = <ntl_ZZ_pEContext_class>modulus
            self.c.restore_c()
            ZZ_pE_construct(&self.x)
        else:
            self.c = <ntl_ZZ_pEContext_class>ntl_ZZ_pEContext(modulus)
            self.c.restore_c()
            ZZ_pE_construct(&self.x)

    def __dealloc__(ntl_ZZ_pE self):
        if <object>self.c is not None:
            self.c.restore_c()
        ZZ_pE_destruct(&self.x)

    cdef ntl_ZZ_pE _new(self):
        cdef ntl_ZZ_pE r
        self.c.restore_c()
        r = PY_NEW(ntl_ZZ_pE)
        r.c = self.c
        return r

    def __reduce__(self):
        """
        sage: a = ntl.ZZ_pE([4],ntl.ZZ_pX([1,1,1],ntl.ZZ(7)))
        sage: loads(dumps(a)) == a
        True
        """
        return make_ZZ_pE, (self.get_as_ZZ_pX(), self.get_modulus_context())

    def get_modulus_context(self):
        return self.c

    def __repr__(self):
        #return self.get_as_ZZ_pX().__repr__()
        self.c.restore_c()
        #_sig_on
        return ZZ_pE_to_PyString(&self.x)
        #return string_delete(ans)


    def __richcmp__(ntl_ZZ_pE self, ntl_ZZ_pE other, op):
        r"""
        EXAMPLES:
            sage: c=ntl.ZZ_pEContext(ntl.ZZ_pX([1,1,1],11))
            sage: c.ZZ_pE([13,1,1])==c.ZZ_pE(1)
            True
            sage: c.ZZ_pE(35r)==c.ZZ_pE(1)
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
        t = ZZ_pE_equal(self.x, other.x)
        _sig_off
        # t == 1 if self == other
        if op == 2:
            return t == 1
        elif op == 3:
            return t == 0
        # And what about other op values?

    def __invert__(ntl_ZZ_pE self):
        r"""
        EXAMPLES:
            sage: c=ntl.ZZ_pEContext(ntl.ZZ_pX([2,7,1],11))
            sage: ~ntl.ZZ_pE([1,1],modulus=c)
            [7 3]
        """
        cdef ntl_ZZ_pE r = self._new()
        _sig_on
        self.c.restore_c()
        ZZ_pE_inv(r.x, self.x)
        _sig_off
        return r

    def __mul__(ntl_ZZ_pE self, other):
        cdef ntl_ZZ_pE y
        cdef ntl_ZZ_pE r = self._new()
        if not PY_TYPE_CHECK(other, ntl_ZZ_pE):
            other = ntl_ZZ_pE(other,self.c)
        elif self.c is not (<ntl_ZZ_pE>other).c:
            raise ValueError, "You can not perform arithmetic with elements of different moduli."
        y = other
        self.c.restore_c()
        ZZ_pE_mul(r.x, self.x, y.x)
        return r

    def __sub__(ntl_ZZ_pE self, other):
        if not PY_TYPE_CHECK(other, ntl_ZZ_pE):
            other = ntl_ZZ_pE(other,self.c)
        elif self.c is not (<ntl_ZZ_pE>other).c:
            raise ValueError, "You can not perform arithmetic with elements of different moduli."
        cdef ntl_ZZ_pE r = self._new()
        self.c.restore_c()
        ZZ_pE_sub(r.x, self.x, (<ntl_ZZ_pE>other).x)
        return r

    def __add__(ntl_ZZ_pE self, other):
        cdef ntl_ZZ_pE y
        cdef ntl_ZZ_pE r = self._new()
        if not PY_TYPE_CHECK(other, ntl_ZZ_pE):
            other = ntl_ZZ_pE(other,modulus=self.c)
        elif self.c is not (<ntl_ZZ_pE>other).c:
            raise ValueError, "You can not perform arithmetic with elements of different moduli."
        y = other
        _sig_on
        self.c.restore_c()
        ZZ_pE_add(r.x, self.x, y.x)
        _sig_off
        return r

    def __neg__(ntl_ZZ_pE self):
        cdef ntl_ZZ_pE r = self._new()
        _sig_on
        self.c.restore_c()
        ZZ_pE_negate(r.x, self.x)
        _sig_off
        return r

    def __pow__(ntl_ZZ_pE self, long e, ignored):
        cdef ntl_ZZ_pE r = self._new()
        _sig_on
        self.c.restore_c()
        ZZ_pE_power(r.x, self.x, e)
        _sig_off
        return r


    cdef ntl_ZZ_pX get_as_ZZ_pX(ntl_ZZ_pE self):
        r"""
        Returns value as ntl_ZZ_pX.
        """
        self.c.restore_c()
        cdef ntl_ZZ_pX y = ntl_ZZ_pX(v = None, modulus = self.c.pc)
        y.x = ZZ_pE_to_ZZ_pX(&self.x)[0]
        return y

    def get_as_ZZ_pX_doctest(self):
        r"""
        This method exists solely for automated testing of get_as_ZZ_pX().

        sage: c=ntl.ZZ_pEContext(ntl.ZZ_pX([1,1,1],11))
        sage: x = ntl.ZZ_pE([42,1],modulus=c)
        sage: i = x.get_as_ZZ_pX_doctest()
        sage: print i
        [9 1]
        sage: print type(i)
        <type 'sage.libs.ntl.ntl_ZZ_pX.ntl_ZZ_pX'>
        """
        return self.get_as_ZZ_pX()

    cdef void set_from_ZZ_pX(ntl_ZZ_pE self, ntl_ZZ_pX value):
        r"""
        Sets the value from a ZZ_pX.
        """
        self.c.restore_c()
        self.x = ZZ_pX_to_ZZ_pE(value.x)

    def set_from_ZZ_pX_doctest(self, value):
        r"""
        This method exists solely for automated testing of set_from_ZZ_pX().

        sage: c=ntl.ZZ_pEContext(ntl.ZZ_pX([1,1,1],11))
        sage: x = ntl.ZZ_pE(modulus=c)
        sage: x.set_from_ZZ_pX_doctest(ntl.ZZ_pX([5,2,1],11))
        sage: x
        [4 1]
        """
        self.set_from_ZZ_pX(value)

    #def lift(self):
    #    cdef ntl_ZZ r = ntl_ZZ()
    #    self.c.restore_c()
    #    r.x = rep(self.x)
    #    return r

    def modulus(self):
        r"""
        Returns the modulus as an NTL ZZ_pX.

        sage: c=ntl.ZZ_pEContext(ntl.ZZ_pX([1,1,1],11))
        sage: n=ntl.ZZ_pE([2983,233],c)
        sage: n.modulus()
        [1 1 1]
        """
        self.c.restore_c()
        cdef ntl_ZZ_pX r = ntl_ZZ_pX(v = None, modulus=self.c.pc)
        r.x = (<ntl_ZZ_pX>self.c.f).x
        return r

def make_ZZ_pE(x, c):
    """
    Here for unpickling.

    EXAMPLES:
    sage: c = ntl.ZZ_pEContext(ntl.ZZ_pX([-5,0,1],25))
    sage: sage.libs.ntl.ntl_ZZ_pE.make_ZZ_pE(ntl.ZZ_pE, [4,3], c)
    [4 3]
    sage: type(sage.libs.ntl.ntl_ZZ_pE.make_ZZ_pE(ntl.ZZ_pE, [4,3], c))
    <type 'sage.libs.ntl.ntl_ZZ_pE.ntl_ZZ_pE'>
    """
    return ntl_ZZ_pE(x, c)
