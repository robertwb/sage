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
include 'misc.pxi'
include 'decl.pxi'

from ntl_GF2X cimport ntl_GF2X

cdef make_GF2X(GF2X_c *x):
    """
    These make_XXXX functions are deprecated and should be phased out.
    """
    cdef ntl_GF2X y
    _sig_off
    y = ntl_GF2X()
    y.x = x[0]
    GF2X_delete(x)
    return y

##############################################################################
#
# ntl_GF2E: GF(2**x) via NTL
#
# AUTHORS:
#  - Martin Albrecht <malb@informatik.uni-bremen.de>
#    2006-01: initial version (based on cody by William Stein)
#
##############################################################################

def GF2X_hex_repr(have_hex=None):
    """
    Represent GF2X and GF2E elements in the more compact
    hexadecimal form to the user.

    If no parameter is provided the currently set value will be
    returned.

    INPUT:
        have_hex if True hex representation will be used

    EXAMPLES:
        sage: m = ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
        sage: x = ntl.GF2E([1,0,1,0,1]) ; x
        [1 0 1 0 1]

        sage: ntl.hex_output() ## indirect doctest
        False
        sage: ntl.hex_output(True)
        sage: ntl.hex_output()
        True

        sage: x
        0x51

        sage: ntl.hex_output(False)
        sage: x
        [1 0 1 0 1]
    """
    if have_hex==None:
        return bool(GF2XHexOutput[0])

    if have_hex==True:
        GF2XHexOutput[0] = 1
    else:
        GF2XHexOutput[0] = 0

def ntl_GF2E_modulus(p=None):
    """
    Initializes the current modulus to P; required: deg(P) >= 1

    The input is either ntl.GF2X or is tried to be converted to a
    ntl.GF2X element.

    If no parameter p is given: Yields copy of the current GF2E
    modulus.

    INPUT:
        p -- modulus

    EXAMPLES:
        sage: ntl.GF2E_modulus([1,1,0,1,1,0,0,0,1])
        sage: hex(ntl.GF2E_modulus())
        '0xb11'
    """
    global __have_GF2E_modulus
    cdef ntl_GF2X elem

    if p is None:
        if __have_GF2E_modulus:
            return make_GF2X(<GF2X_c*>GF2E_modulus())
        else:
            raise "NoModulus"

    if not isinstance(p,ntl_GF2X):
        elem = ntl_GF2X(p)
    else:
        elem = p

    if(elem.deg()<1):
        raise "DegreeToSmall"

    ntl_GF2E_set_modulus(<GF2X_c*>&elem.x)
    __have_GF2E_modulus = True

def ntl_GF2E_modulus_degree():
    """
    Returns deg(modulus) for GF2E elements

    EXAMPLES:
        sage: ntl.GF2E_modulus([1,1,0,1,1,0,0,0,1])
        sage: ntl.GF2E_degree()
        8
    """
    if __have_GF2E_modulus:
        return GF2E_degree()
    else:
        raise "NoModulus"

def ntl_GF2E_sage(names='a'):
    """
    Returns a SAGE FiniteField element matching the current modulus.

    EXAMPLES:
        sage: ntl.GF2E_modulus([1,1,0,1,1,0,0,0,1])
        sage: ntl.GF2E_sage()
        Finite Field in a of size 2^8
    """
    from sage.rings.finite_field import FiniteField
    f = ntl_GF2E_modulus()._sage_()
    return FiniteField(int(2)**GF2E_degree(),modulus=f,name=names)


def ntl_GF2E_random():
    """
    Returns a random element from GF2E modulo the current modulus.

    EXAMPLES:
        sage: ntl.GF2E_modulus([1,1,0,1,1,0,0,0,1])
        sage: ntl.GF2E_random() # random
        [0 0 0 0 1 1 1]
    """
    cdef ntl_GF2E r = ntl_GF2E()
    _sig_on
    r.gf2e_x = GF2E_random()
    _sig_off
    return r

def unpickle_GF2E(hex, mod):
    """
    Used for unpickling.

    EXAMPLES:
        sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
        sage: x = ntl.GF2E([1,0,1,0,1])
        sage: y = loads(dumps(x))
        sage: x == y
        True
        sage: x is y
        False
    """
    ntl_GF2E_modulus(mod)
    return ntl_GF2E(hex)


# make sure not to segfault
__have_GF2E_modulus = False


cdef class ntl_GF2E(ntl_GF2X):
    r"""
    The \\class{GF2E} represents a finite extension field
    over GF(2) using NTL. Elements are represented as polynomials
    over GF(2) modulo \\code{ntl.GF2E_modulus()}.

    This modulus must be set using \\code{ ntl.GF2E_modulus(p) }
    and is unique for all elements in ntl.GF2E. So it is not
    possible at the moment e.g. to have elements in GF(2**4) and
    GF(2**8) at the same time. You might however be lucky and get
    away with not touch the elements in GF(2**4) while having the
    GF(2**8) modulus set and vice versa.
    """

    def __init__(self,x=[]):
        """
        Constructs a new  finite field element in GF(2**x).

        A modulus \emph{must} have been set with
        \code{ntl.GF2E_modulus(ntl.GF2X(<value>))} when calling this
        constructor.  A value may be passed to this constructor. If
        you pass a string to the constructor please note that byte
        sequences and the hexadecimal notation are Little Endian in NTL.
        So e.g. '[0 1]' == '0x2' == x.

        INPUT:
            x -- value to be assigned to this element. Same types as
                 ntl.GF2X() are accepted.

        OUTPUT:
            a new ntl.GF2E element

        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: ntl.GF2E(ntl.ZZ_pX([1,1,3],2))
            [1 1 1]
            sage: ntl.GF2E('0x1c')
            [1 0 0 0 0 0 1 1]
            sage: ntl.GF2E('[1 0 1 0]')
            [1 0 1]
            sage: ntl.GF2E([1,0,1,0])
            [1 0 1]
            sage: ntl.GF2E(GF(2**8,'a').gen()**20)
            [0 0 1 0 1 1 0 1]
        """
        if not __have_GF2E_modulus:
            raise "NoModulus"

        s = str(ntl_GF2X(x))
        _sig_on
        GF2E_from_str(&self.gf2e_x, s)
        self.x = GF2E_rep(self.gf2e_x)
        _sig_off

    def __new__(self, x=[]):
        GF2E_construct(&self.gf2e_x)

    def __dealloc__(self):
        GF2E_destruct(&self.gf2e_x)

    def __reduce__(self):
        """
        EXAMPES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: a = ntl.GF2E(ntl.ZZ_pX([1,1,3],2))
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,1,0,1]))
            sage: loads(dumps(a)) == a
            True
        """
        return unpickle_GF2E, (hex(self.ntl_GF2X()), ntl_GF2E_modulus())

    def __repr__(self):
        """
        Return the string representation of self.

        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: ntl.GF2E([1,1,0,1]).__repr__()
            '[1 1 0 1]'
        """
        return GF2E_to_PyString(&self.gf2e_x)

    def __mul__(ntl_GF2E self, other):
        """
        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = ntl.GF2E([1,1,0,1,1])
            sage: x*y ## indirect doctest
            [0 0 1 1 1 0 1 1]
        """
        cdef ntl_GF2E y
        cdef ntl_GF2E r = ntl_GF2E()
        if not isinstance(other, ntl_GF2E):
            other = ntl_GF2E(other)
        y = other
        _sig_on
        GF2E_mul(r.gf2e_x, self.gf2e_x, y.gf2e_x)
        _sig_off
        return r

    def __sub__(ntl_GF2E self, other):
        """
        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = ntl.GF2E([1,1,0,1,1])
            sage: x-y ## indirect doctest
            [0 1 1 1]
        """
        cdef ntl_GF2E y
        cdef ntl_GF2E r = ntl_GF2E()
        if not isinstance(other, ntl_GF2E):
            other = ntl_GF2E(other)
        y = other
        _sig_on
        GF2E_sub(r.gf2e_x, self.gf2e_x, y.gf2e_x)
        _sig_off
        return r

    def __add__(ntl_GF2E self, other):
        """
        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = ntl.GF2E([1,1,0,1,1])
            sage: x+y ## indirect doctest
            [0 1 1 1]
        """
        cdef ntl_GF2E y
        cdef ntl_GF2E r = ntl_GF2E()
        if not isinstance(other, ntl_GF2E):
            other = ntl_GF2E(other)
        y = other
        _sig_on
        GF2E_add(r.gf2e_x, self.gf2e_x, y.gf2e_x)
        _sig_off
        return r

    def __neg__(ntl_GF2E self):
        """
        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1])
            sage: -x ## indirect doctest
            [1 0 1 0 1]
        """
        cdef ntl_GF2E r = ntl_GF2E()
        _sig_on
        GF2E_negate(r.gf2e_x, self.gf2e_x)
        _sig_off
        return r

    def __pow__(ntl_GF2E self, long e, ignored):
        """
        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1])
            sage: x**2 ## indirect doctest
            [0 1 0 1]
        """
        cdef ntl_GF2E y
        cdef ntl_GF2E r
        r = ntl_GF2E()
        _sig_on
        GF2E_power(r.gf2e_x, self.gf2e_x, e)
        _sig_off
        return r

    def __cmp__(ntl_GF2E self, ntl_GF2E other):
        """
        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = ntl.GF2E([1,1,0,1,1])
            sage: x < y ## indirect doctest
            False
            sage: x == x
            True
        """
        cdef int t
        _sig_on
        t = GF2E_equal(self.gf2e_x, other.gf2e_x)
        _sig_off
        if t:
            return 0
        return 1

    def is_zero(ntl_GF2E self):
        """
        Returns True if this element equals zero, False otherwise.

        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = ntl.GF2E([1,1,0,1,1,0,0,0,1])
            sage: x.is_zero()
            False
            sage: y.is_zero()
            True
        """
        return bool(GF2E_IsZero(self.gf2e_x))

    def is_one(ntl_GF2E self):
        """
        Returns True if this element equals one, False otherwise.

        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = ntl.GF2E([0,1,0,1,1,0,0,0,1])
            sage: x.is_one()
            False
            sage: y.is_one()
            True
        """
        return bool(GF2E_IsOne(self.gf2e_x))

    def __copy__(self):
        """
        Returns a copy of this element.

        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = x.__copy__()
            sage: x is y
            False
            sage: x == y
            True
        """
        cdef ntl_GF2E r = ntl_GF2E()
        _sig_on
        r.gf2e_x = self.gf2e_x
        r.x = self.x
        _sig_off
        return r

    def copy(ntl_GF2E self):
        """
        Returns a copy of this element.

        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = x.copy()
            sage: x is y
            False
            sage: x == y
            True
        """
        cdef ntl_GF2E r = ntl_GF2E()
        _sig_on
        r.gf2e_x = self.gf2e_x
        r.x = self.x
        _sig_off
        return r

    def trace(ntl_GF2E self):
        """
        Returns the trace of this element.

        EXAMPLES:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: x = ntl.GF2E([1,0,1,0,1]) ; y = ntl.GF2E([0,1,1,0,1,1])
            sage: x.trace()
            0
            sage: y.trace()
            1
        """
        return GF2E_trace(&self.gf2e_x)

    def ntl_GF2X(ntl_GF2E self):
        """
        Returns a ntl.GF2X copy of this element.

        EXAMPLE:
            sage: m=ntl.GF2E_modulus(ntl.GF2X([1,1,0,1,1,0,0,0,1]))
            sage: a = ntl.GF2E('0x1c')
            sage: a.ntl_GF2X()
            [1 0 0 0 0 0 1 1]
            sage: a.copy().ntl_GF2X()
            [1 0 0 0 0 0 1 1]
        """
        cdef ntl_GF2X x = ntl_GF2X()
        x.x = self.x
        return x

    def _sage_(ntl_GF2E self, k=None):
        """
        Returns a \class{FiniteFieldElement} representation
        of this element. If a \class{FiniteField} k is provided
        it is constructed in this field if possible. A \class{FiniteField}
        will be constructed if none is provided.

        INPUT:
            self  -- \class{GF2E} element
            k     -- optional GF(2**deg)

        OUTPUT:
            FiniteFieldElement over k

        EXAMPLE:
            sage: ntl.GF2E_modulus([1,1,0,1,1,0,0,0,1])
            sage: e = ntl.GF2E([0,1])
            sage: a = e._sage_(); a
            a
        """
        cdef int i
        cdef int length
        deg= GF2E_degree()

        if k is None:
            from sage.rings.finite_field import FiniteField
            f = ntl_GF2E_modulus()._sage_()
            k = FiniteField(2**deg,name='a',modulus=f)

        a=k.gen()
        l = self.list()

        length = len(l)
        ret = 0

        for i from 0 <= i < length:
            if l[i]==1:
                ret = ret + a**i

        return ret
