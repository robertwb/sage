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

include "../ext/stdsage.pxi"
include "../ext/python_sequence.pxi"
include "../ext/python_list.pxi"
include "../ext/python_tuple.pxi"

cdef extern from *:
    bint PyGen_Check(x)


def running_total(L, start=None):
    """
    Returns a list where the i-th entry is the sum of all entries up to (and incling) i.

    INPUT:
        L     -- the list
        start -- (optional) a default start value

    EXAMPLES:
        sage: running_total(range(5))
        [0, 1, 3, 6, 10]
        sage: running_total("abcdef")
        ['a', 'ab', 'abc', 'abcd', 'abcde', 'abcdef']
        sage: running_total([1..10], start=100)
        [101, 103, 106, 110, 115, 121, 128, 136, 145, 155]
    """
    cdef bint first = 1
    for x in L:
        if first:
            total = L[0] if start is None else L[0]+start
            running = [total]
            first = 0
            continue
        total += x
        PyList_Append(running, total)
    return running


def prod(x, z=None, Py_ssize_t recursion_cutoff = 5):
    """
    Return the product of the elements in the list x.  If optional
    argument z is not given, start the product with the first element
    of the list, otherwise use z.  The empty product is the int 1 if z
    is not specified, and is z if given.

    This assumes that your multiplication is associative; we don't promise
    which end of the list we start at.

    EXAMPLES:
        sage: prod([1,2,34])
        68
        sage: prod([2,3], 5)
        30
        sage: prod((1,2,3), 5)
        30
        sage: F = factor(-2006); F
        -1 * 2 * 17 * 59
        sage: prod(F)
        -2006

    AUTHORS:
        Joel B. Mohler (2007-10-03 -- Reimplemented in Cython and optimized)
        Robert Bradshaw (2007-10-26) -- Balanced product tree, other optimizations, (lazy) generator support
    """
    if not PyList_CheckExact(x) and not PyTuple_CheckExact(x):

        if PyGen_Check(x):
            # lazy list, do lazy product
            try:
                prod = x.next() if z is None else z * x.next()
                for a in x:
                    prod *= a
                return prod
            except StopIteration:
                x = []

        else:

            try:
                return x.prod()
            except AttributeError:
                pass

            try:
                return x.mul()
            except AttributeError:
                pass

            x = list(x)

    cdef Py_ssize_t n = len(x)

    if n == 0:
        if z is None:
            import sage.rings.integer
            return sage.rings.integer.Integer(1)
        else:
            return z

    prod = balanced_list_prod(x, 0, n, recursion_cutoff)

    if z is not None:
        prod = z*prod

    return prod


cdef balanced_list_prod(L, Py_ssize_t offset, Py_ssize_t count, Py_ssize_t cutoff):
    """
    INPUT:
        L      -- the terms (MUST be a tuple or list)
        off    -- offset in the list from which to start
        count  -- how many terms in the product
        cutoff -- the minimum count to recurse on

    OUTPUT:
        L[offset] * L[offset+1] * ... * L[offset+count-1]

    NOTE: The parameter cutoff must be at least 1, and there is no reason to
          ever make it less than 3. However, there are at least two advantages
          to setting it higher (and consequently not recursing all the way
          down the tree). First, one avoids the overhead of the function
          calls at the base of the tree (which is the majority of them) and
          second, it allows one to save on object creation if inplace
          operations are used. The asymptotic gains should usually be at the
          top of the tree anyway.
    """
    cdef Py_ssize_t k
    if count <= cutoff:
        prod = <object>PySequence_Fast_GET_ITEM(L, offset)
        for k from offset < k < offset+count:
            prod *= <object>PySequence_Fast_GET_ITEM(L, k)
        return prod
    else:
        k = (1+count) >> 1
        return balanced_list_prod(L, offset, k, cutoff) * balanced_list_prod(L, offset+k, count-k, cutoff)


class NonAssociative:
    """
    This class is to test the balance nature of prod.

    EXAMPLES:
        sage: from sage.misc.misc_c import NonAssociative
        sage: L = [NonAssociative(label) for label in 'abcdef']
        sage: prod(L)
        (((a*b)*c)*((d*e)*f))
        sage: L = [NonAssociative(label) for label in range(20)]
        sage: prod(L, recursion_cutoff=5)
        ((((((0*1)*2)*3)*4)*((((5*6)*7)*8)*9))*(((((10*11)*12)*13)*14)*((((15*16)*17)*18)*19)))
        sage: prod(L, recursion_cutoff=1)
        (((((0*1)*2)*(3*4))*(((5*6)*7)*(8*9)))*((((10*11)*12)*(13*14))*(((15*16)*17)*(18*19))))
        sage: L = [NonAssociative(label) for label in range(14)]
        sage: prod(L, recursion_cutoff=1)
        ((((0*1)*(2*3))*((4*5)*6))*(((7*8)*(9*10))*((11*12)*13)))
    """
    def __init__(self, left, right=None):
        """
        EXAMPLES:
            sage: from sage.misc.misc_c import NonAssociative
            sage: NonAssociative('a')
            a
            sage: NonAssociative('a','b')
            (a*b)
        """
        self.left = left
        self.right = right

    def __repr__(self):
        """
        EXAMPLES:
            sage: from sage.misc.misc_c import NonAssociative
            sage: NonAssociative(1)
            1
            sage: NonAssociative(2,3)
            (2*3)
        """
        if self.right is None:
            return str(self.left)
        else:
            return "(%s*%s)" % (self.left, self.right)

    def __mul__(self, other):
        """
        EXAMPLES:
            sage: from sage.misc.misc_c import NonAssociative
            sage: a, b, c = [NonAssociative(label) for label in 'abc']
            sage: (a*b)*c
            ((a*b)*c)
            sage: a*(b*c)
            (a*(b*c))
        """
        return NonAssociative(self, other)


#############################################################################
# Bitset Testing
#############################################################################

include "bitset.pxi"

def test_bitset(py_a, py_b, long n):
    """
    TESTS:
        sage: from sage.misc.misc_c import test_bitset
        sage: test_bitset('00101', '01110', 4)
        a 00101
        a.size 5
        a.limbs 1
        b 01110
        a.check(n)   True
        a.set(n)     00101
        a.unset(n)   00100
        a.set_to(n)  00101
        a.flip(n)    00100
        a.is_zero()  False
        a.is_equal(b) False
        a.cmp(b)     1
        a.copy()     00101
        r.zero()     00000
        not a        11010
        a and b      00100
        a or b       01111
        a xor b      01011
        a.rshift(n)  10000
        a.lshift(n)  00000
        a.first()           2
        a.next(n)           4
        a.first_diff(b)     1
        a.next_diff(b, n)   4
        a.hamming_weight()  2
        a.hamming_weight_sparse()  2

    Large enough to span multiple limbs:
        sage: test_bitset('111001'*25, RealField(151)(pi).str(2)[2:], 69)
        a 111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001
        a.size 150
        a.limbs 5
        b 000100100001111110110101010001000100001011010001100001000110100110001001100011001100010100010111000000011011100000111001101000100101001000000100100111
        a.check(n)   False
        a.set(n)     111001111001111001111001111001111001111001111001111001111001111001111101111001111001111001111001111001111001111001111001111001111001111001111001111001
        a.unset(n)   111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001
        a.set_to(n)  111001111001111001111001111001111001111001111001111001111001111001111101111001111001111001111001111001111001111001111001111001111001111001111001111001
        a.flip(n)    111001111001111001111001111001111001111001111001111001111001111001111101111001111001111001111001111001111001111001111001111001111001111001111001111001
        a.is_zero()  False
        a.is_equal(b) False
        a.cmp(b)     -1
        a.copy()     111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001111001
        r.zero()     000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        not a        000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110000110
        a and b      000000100001111000110001010001000000001001010001100001000000100000001001100001001000010000010001000000011001100000111001101000100001001000000000100001
        a or b       111101111001111111111101111001111101111011111001111001111111111111111001111011111101111101111111111001111011111001111001111001111101111001111101111111
        a xor b      111101011000000111001100101000111101110010101000011000111111011111110000011010110101101101101110111001100010011001000000010001011100110001111101011110
        a.rshift(n)  001111001111001111001111001111001111001111001111001111001111001111001111001111001000000000000000000000000000000000000000000000000000000000000000000000
        a.lshift(n)  000000000000000000000000000000000000000000000000000000000000000000000111001111001111001111001111111101001111001111001111001111001100101111001111001111
        a.first()           0
        a.next(n)           71
        a.first_diff(b)     0
        a.next_diff(b, n)   73
        a.hamming_weight()  100
        a.hamming_weight_sparse()  100
    """
    cdef bint bit = True
    cdef bitset_t a, b, r

    bitset_from_str(a, py_a)
    bitset_from_str(b, py_b)

    print "a", bitset_string(a)
    print "a.size", a.size
    print "a.limbs", a.limbs
    print "b", bitset_string(b)
    print "a.check(n)  ", bitset_check(a, n)
    bitset_set(a, n)
    print "a.set(n)    ", bitset_string(a)
    bitset_from_str(a, py_a)
    bitset_unset(a, n)
    print "a.unset(n)  ", bitset_string(a)
    bitset_from_str(a, py_a)
    bitset_set_to(a, n, bit)
    print "a.set_to(n) ", bitset_string(a)
    bitset_from_str(a, py_a)
    bitset_flip(a, n)
    print "a.flip(n)   ", bitset_string(a)

    bitset_from_str(a, py_a)
    bitset_from_str(b, py_b)
    print "a.is_zero() ", bitset_is_zero(a)
    print "a.is_equal(b)", bitset_is_equal(a, b)
    print "a.cmp(b)    ", bitset_cmp(a, b)

    bitset_from_str(a, py_a)
    bitset_from_str(b, py_b)

    bitset_init(r, a.size)
    bitset_copy(r, a)
    print "a.copy()    ", bitset_string(r)
    bitset_zero(r)
    print "r.zero()    ", bitset_string(r)
    bitset_not(r, a)
    print "not a       ", bitset_string(r)
    bitset_and(r, a, b)
    print "a and b     ", bitset_string(r)
    bitset_or(r, a, b)
    print "a or b      ", bitset_string(r)
    bitset_xor(r, a, b)
    print "a xor b     ", bitset_string(r)

    bitset_rshift(r, a, n)
    print "a.rshift(n) ", bitset_string(r)

    bitset_lshift(r, a, n)
    print "a.lshift(n) ", bitset_string(r)

    print "a.first()          ", bitset_first(a)
    print "a.next(n)          ", bitset_next(a, n)
    print "a.first_diff(b)    ", bitset_first_diff(a, b)
    print "a.next_diff(b, n)  ", bitset_next_diff(a, b, n)

    print "a.hamming_weight() ", bitset_hamming_weight(a)
    print "a.hamming_weight_sparse() ", bitset_hamming_weight_sparse(a)

    bitset_clear(a)
    bitset_clear(b)
    bitset_clear(r)
