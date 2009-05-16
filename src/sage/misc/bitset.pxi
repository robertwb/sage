"""
A fast bitset datatype in Cython.

Operations between bitsets are only guaranteed to work if the bitsets
have the same size.  Similarly, you should not try to access elements
of a bitset beyond the size.
"""

#*****************************************************************************
#     Copyright (C) 2008 Robert Bradshaw <robertwb@math.washington.edu>
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


# Doctests for the functions in this file are in misc_c.pyx


#############################################################################
# Bitset Initalization
#############################################################################

cdef inline bint bitset_init(bitset_t bits, unsigned long size) except -1:
    """
    Allocates a bitset of size size.  The set will probably be filled
    with random elements.
    """
    bits.size = size
    bits.limbs = (size - 1)/(8*sizeof(unsigned long)) + 1
    bits.bits = <unsigned long*>sage_malloc(bits.limbs * sizeof(unsigned long))
    if bits.bits == NULL:
        raise MemoryError
    bits.bits[bits.limbs-1] = 0 #Set entries beyond the end of the set to zero.


cdef inline void bitset_free(bitset_t bits):
    """
    Deallocates the memory in bits.
    """
    sage_free(bits.bits)

cdef inline void bitset_clear(bitset_t bits):
    """
    Removes all elements from the set
    """
    memset(bits.bits, 0, bits.limbs * sizeof(unsigned long))

cdef inline void bitset_zero(bitset_t bits):
    """
    Removes all elements from the set

    This function is the same as bitset_clear(bits).
    """
    bitset_clear(bits)

cdef inline void bitset_copy(bitset_t dst, bitset_t src):
    """
    Copy the bitset src over the bitset dst, overwriting dst.

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    memcpy(dst.bits, src.bits, dst.limbs * sizeof(unsigned long))

#############################################################################
# Bitset Comparison
#############################################################################

cdef inline bint bitset_isempty(bitset_t bits):
    """
    Tests whether bits is empty.  Returns True (i.e., 1) if the set is
    empty, False (i.e., 0) otherwise.
    """
    cdef long i
    for i from 0 <= i < bits.limbs:
        if bits.bits[i] != 0:
            return False
    return True

cdef inline bint bitset_is_zero(bitset_t bits):
    """
    Tests whether bits is empty (i.e., zero).  Returns True (1) if
    the set is empty, False (0) otherwise.

    This function is the same as bitset_is_empty(bits).
    """
    return bitset_isempty(bits)

cdef inline bint bitset_eq(bitset_t a, bitset_t b):
    """
    Compares bitset a and b.  Returns True (i.e., 1) if the sets are
    equal, and False (i.e., 0) otherwise.

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    return memcmp(a.bits, b.bits, a.limbs * sizeof(unsigned long)) == 0

cdef inline int bitset_cmp(bitset_t a, bitset_t b):
    """
    Compares bitsets a and b.  Returns 0 if the two sets are
    identical, and consistently returns -1 or 1 for two sets that are
    not equal.

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    cdef long i
    for i from a.limbs > i >= 0:
        if a.bits[i] != b.bits[i]:
            if a.bits[i] < b.bits[i]:
                return -1
            else:
                return 1
    return 0

cdef inline bint bitset_issubset(bitset_t a, bitset_t b):
    """
    Test whether a is a subset of b (i.e., every element in a is also
    in b).

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    cdef long i
    for i from 0 <= i < a.limbs:
        if (a.bits[i] & ~b.bits[i]) != 0:
            return False
    return True

cdef inline bint bitset_issuperset(bitset_t a, bitset_t b):
    """
    Test whether a is a superset of b (i.e., every element in b is also
    in a).

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    return bitset_issubset(b, a)



#############################################################################
# Bitset Bit Manipulation
#############################################################################

cdef inline bint bitset_in(bitset_t bits, unsigned long n):
    """
    Checks if n is in bits.  Returns True (i.e., 1) if n is in the
    set, False (i.e., 0) otherwise.
    """
    return (bits.bits[n >> index_shift] >> (n & offset_mask)) & 1

cdef inline bint bitset_check(bitset_t bits, unsigned long n):
    """
    Checks if n is in bits.  Returns True (i.e., 1) if n is in the
    set, False (i.e., 0) otherwise.

    This function is the same as bitset_in(bits, n).
    """
    return bitset_in(bits, n)

cdef inline bint bitset_not_in(bitset_t bits, unsigned long n):
    """
    Checks if n is not in bits.  Returns True (i.e., 1) if n is not in the
    set, False (i.e., 0) otherwise.
    """
    return not bitset_in(bits, n)


cdef inline bint bitset_remove(bitset_t bits, unsigned long n) except -1:
    """
    Removes n from bits.  Raises KeyError if n is not contained in bits.
    """
    if not bitset_in(bits, n):
        raise KeyError, n
    bitset_discard(bits, n)

cdef inline void bitset_discard(bitset_t bits, unsigned long n):
    """
    Removes n from bits.
    """
    bits.bits[n >> index_shift] &= ~((<unsigned long>1) << (n & offset_mask))

cdef inline void bitset_unset(bitset_t bits, unsigned long n):
    """
    Removes n from bits.

    This function is the same as bitset_discard(bits, n).
    """
    bitset_discard(bits, n)


cdef inline void bitset_add(bitset_t bits, unsigned long n):
    """
    Adds n to bits.
    """
    bits.bits[n >> index_shift] |= (<unsigned long>1) << (n & offset_mask)

cdef inline void bitset_set(bitset_t bits, unsigned long n):
    """
    Adds n to bits.

    This function is the same as bitset_add(bits, n).
    """
    bitset_add(bits, n)


cdef inline void bitset_set_to(bitset_t bits, unsigned long n, bint b):
    """
    If b is True, adds n to bits.  If b is False, removes n from bits.
    """
    bitset_unset(bits, n)
    bits.bits[n >> index_shift] |= (<unsigned long>b) << (n & offset_mask)

cdef inline void bitset_flip(bitset_t bits, unsigned long n):
    """
    If n is in bits, removes n from bits.  If n is not in bits, add n
    to bits.
    """
    bits.bits[n >> index_shift] ^= (<unsigned long>1) << (n & offset_mask)

#############################################################################
# Bitset Searching
#############################################################################

cdef inline long _bitset_first_in_limb(unsigned long limb):
    """
    Given a limb of a bitset, return the index of the first nonzero
    bit.  If there are no bits set in the limb, return -1.
    """
    cdef long j
    # First, we see if the first half of the limb is zero or not
    if limb & (((<unsigned long>1) << 4*sizeof(unsigned long)) - 1):
        for j from 0 <= j < 4*sizeof(unsigned long):
            if limb & ((<unsigned long>1) << j):
                return j
    else:
        # First half of the limb is zero, so first nonzero bit is in
        # the second half.
        for j from 4*sizeof(unsigned long) <= j < 8*sizeof(unsigned long):
            if limb & ((<unsigned long>1) << j):
                return j
    return -1

cdef inline long bitset_first(bitset_t a):
    """
    Calculate the index of the first element in the set.  If the set
    is empty, returns -1.
    """
    cdef long i
    for i from 0 <= i < a.limbs:
        if a.bits[i]:
            return (i << index_shift) | _bitset_first_in_limb(a.bits[i])
    return -1

cdef inline long bitset_pop(bitset_t a) except -1:
    """
    Remove and return an arbitrary element from the set. Raises
    KeyError if the set is empty.
    """
    cdef long i = bitset_first(a)
    if i == -1:
        raise KeyError, 'pop from an empty set'
    bitset_discard(a, i)
    return i

cdef inline long bitset_first_diff(bitset_t a, bitset_t b):
    """
    Calculate the index of the first difference between a and b.  If a
    and b are equal, then return -1.

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    cdef long i
    for i from 0 <= i < a.limbs:
        if a.bits[i] != b.bits[i]:
            return (i << index_shift) | _bitset_first_in_limb(a.bits[i] ^ b.bits[i])
    return -1

cdef inline long bitset_next(bitset_t a, long n):
    """
    Calculate the index of the next element in the set, starting at
    (and including) n.  Return -1 if there are no elements from n
    onwards.
    """
    if n >= a.size:
        return -1
    cdef long i
    cdef unsigned long limb = a.bits[n >> index_shift] & ~(((<unsigned long>1) << (n & offset_mask)) - 1)
    cdef long ret = _bitset_first_in_limb(limb)
    if ret != -1:
        return (n & ~offset_mask) | ret
    for i from (n >> index_shift) < i < a.limbs:
        if a.bits[i]:
            return (i << index_shift) | _bitset_first_in_limb(a.bits[i])
    return -1

cdef inline long bitset_next_diff(bitset_t a, bitset_t b, long n):
    """
    Calculate the index of the next element that differs between a and
    b, starting at (and including) n.  Return -1 if there are no
    elements differing between a and b from n onwards.

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    if n >= a.size:
        return -1
    cdef long i
    cdef long limb = (a.bits[n >> index_shift] ^ b.bits[n >> index_shift]) \
        & ~(((<unsigned long>1) << (n & offset_mask)) - 1)
    cdef long ret = _bitset_first_in_limb(limb)
    if ret != -1:
        return (n & ~offset_mask) | ret
    for i from (n >> index_shift) < i < a.limbs:
        if a.bits[i] != b.bits[i]:
            return (i << index_shift) | _bitset_first_in_limb(a.bits[i] ^ b.bits[i])
    return -1



cdef inline long bitset_len(bitset_t bits):
    """
    Calculate the number of items in the set (i.e., the number of nonzero bits).
    """
    cdef long len = 0
    cdef long i = bitset_first(bits)
    while i>=0:
        len += 1
        i=bitset_next(bits, i+1)
    return len


#############################################################################
# Bitset Arithmetic
#############################################################################

cdef inline void bitset_complement(bitset_t r, bitset_t a):
    """
    Set r to be the complement of a, overwriting r.

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    cdef long i
    for i from 0 <= i < r.limbs:
        r.bits[i] = ~a.bits[i]
    if r.size & offset_mask != 0:
        # If the last limb has extra bits beyond the size of r,
        # then zero out those extra bits
        r.bits[r.limbs-1] &= ((<unsigned long>1) << ((r.size) & offset_mask)) - 1

cdef inline void bitset_not(bitset_t r, bitset_t a):
    """
    Set r to be the complement of a, overwriting r.

    We assume the two sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.

    This function is the same as bitset_complement(r, a).
    """
    bitset_complement(r, a)

cdef inline void bitset_intersection(bitset_t r, bitset_t a, bitset_t b):
    """
    Set r to the intersection of a and b, overwriting r.

    We assume the three sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    cdef long i
    for i from 0 <= i < r.limbs:
        r.bits[i] = a.bits[i] & b.bits[i]


cdef inline void bitset_and(bitset_t r, bitset_t a, bitset_t b):
    """
    Set r to the intersection of a and b, overwriting r.

    We assume the three sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.

    This function is the same as bitset_intersection(r, a, b).
    """
    bitset_intersection(r, a, b)

cdef inline void bitset_union(bitset_t r, bitset_t a, bitset_t b):
    """
    Set r to the union of a and b, overwriting r.

    We assume the three sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    cdef long i
    for i from 0 <= i < r.limbs:
        r.bits[i] = a.bits[i] | b.bits[i]

cdef inline void bitset_or(bitset_t r, bitset_t a, bitset_t b):
    """
    Set r to the union of a and b, overwriting r.

    We assume the three sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.

    This function is the same as bitset_union(r, a, b).
    """
    bitset_union(r, a, b)

cdef inline void bitset_difference(bitset_t r, bitset_t a, bitset_t b):
    """
    Set r to the difference of a and b (i.e., things in a that are not
    in b), overwriting r.

    We assume the three sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    cdef long i
    for i from 0 <= i < r.limbs:
        r.bits[i] = a.bits[i] & ~b.bits[i]

cdef inline void bitset_symmetric_difference(bitset_t r, bitset_t a, bitset_t b):
    """
    Set r to the symmetric difference of a and b, overwriting r.

    We assume the three sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.
    """
    cdef long i
    for i from 0 <= i < r.limbs:
        r.bits[i] = a.bits[i] ^ b.bits[i]

cdef inline void bitset_xor(bitset_t r, bitset_t a, bitset_t b):
    """
    Set r to the symmetric difference of a and b, overwriting r.

    We assume the three sets have the same size.  Otherwise, the
    behavior of this function is undefined and the function may
    segfault.

    This function is the same as bitset_symmetric_difference(r, a, b).
    """
    bitset_symmetric_difference(r, a, b)

cdef void bitset_rshift(bitset_t r, bitset_t a, long n):
    if n <= 0:
        if n != 0:
            bitset_lshift(r, a, -n)
        else:
            bitset_copy(r, a)
        return
    elif n >= a.size:
        bitset_clear(r)
        return
    cdef long i
    cdef long off = n >> index_shift
    cdef int shift = offset_mask & n
    cdef int shift2 = 8*sizeof(unsigned long) - shift
    if shift == 0:
        for i from 0 <= i < r.limbs - off:
            r.bits[i] = a.bits[i+off]

    else:
        for i from 0 <= i < r.limbs - off - 1:
            r.bits[i] = (a.bits[i+off] >> shift) | (a.bits[i+off+1] << shift2)
        r.bits[r.limbs - off - 1] = a.bits[r.limbs - 1] >> shift

    if off > 0:
        memset(r.bits + r.limbs - off, 0, off * sizeof(unsigned long))

cdef void bitset_lshift(bitset_t r, bitset_t  a, long n):
    if n <= 0:
        if n != 0:
            bitset_rshift(r, a, -n)
        else:
            bitset_copy(r, a)
        return
    elif n >= a.size:
        bitset_clear(r)
        return
    cdef long i
    cdef long off = n >> index_shift
    cdef int shift = offset_mask & n
    cdef int shift2 = 8*sizeof(unsigned long) - shift
    if shift == 0:
        for i from r.limbs - off > i >= 0:
            r.bits[i+off] = a.bits[i]

    else:
        for i from r.limbs - off > i >= 1:
            r.bits[i+off] = (a.bits[i] << shift) | (a.bits[i-1] >> shift2)
        r.bits[off] = a.bits[0] << shift

    if off > 0:
        memset(r.bits, 0, off * sizeof(unsigned long))

#############################################################################
# Hamming Weights
#############################################################################

cdef enum:
    _bitset_hamming_table_bits = 8

cdef int _bitset_hamming_table[1 << _bitset_hamming_table_bits]

cdef void _bitset_fill_hamming_table():
    cdef int i, j
    for i from 0 <= i < (1 << _bitset_hamming_table_bits):
        _bitset_hamming_table[i] = 0
        for j from 0 <= j < _bitset_hamming_table_bits:
            _bitset_hamming_table[i] += (i >> j) & 1

_bitset_fill_hamming_table()

cdef inline int bitset_hamming_weight(bitset_t a):
    cdef long i, j
    cdef long w = 0
    cdef unsigned long limb
    for i from 0 <= i < a.limbs:
        limb = a.bits[i]
        for j from 0 <= j < (8*sizeof(unsigned long) + _bitset_hamming_table_bits - 1) / _bitset_hamming_table_bits:
            w += _bitset_hamming_table[(limb >> (j*_bitset_hamming_table_bits)) & ((1 << _bitset_hamming_table_bits) - 1)]
    return w

cdef inline long bitset_hamming_weight_sparse(bitset_t a):
    cdef long i
    cdef long w = 0
    cdef unsigned long limb
    for i from 0 <= i < a.limbs:
        limb = a.bits[i]
        while limb:
            w += _bitset_hamming_table[limb & ((1 << _bitset_hamming_table_bits) - 1)]
            limb = limb >> _bitset_hamming_table_bits
    return w

#############################################################################
# Bitset Conversion
#############################################################################

cdef char* bitset_chars(char* s, bitset_t bits, char zero=c'0', char one=c'1'):
    """
    Return a string representation of the bitset in s, using zero for
    the character representing the items not in the bitset and one for
    the character representing the items in the bitset.

    The string is both stored in s and returned.  If s is NULL, then a
    new string is allocated.
    """
    cdef long i
    if s == NULL:
        s = <char *>sage_malloc(bits.size+1)
    for i from 0 <= i < bits.size:
        s[i] = one if bitset_in(bits, i) else zero
    s[bits.size] = 0
    return s

cdef void bitset_from_str(bitset_t bits, char* s, char zero=c'0', char one=c'1'):
    """
    Initialize a bitset with a set derived from the character string
    s, where one represents the character indicating set membership.
    """
    bitset_init(bits, strlen(s))
    cdef long i
    for i from 0 <= i < bits.size:
        bitset_set_to(bits, i, s[i] == one)

cdef bitset_string(bitset_t bits):
    """
    Return a python string representing the bitset.
    """
    cdef char* s = bitset_chars(NULL, bits)
    py_s = s
    sage_free(s)
    return py_s


#############################################################################
# Aliases for functions
#############################################################################
