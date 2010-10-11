"""
PowComputer.

A class for computing and caching powers of the same integer.

This class is designed to be used as a field of p-adic rings and
fields.  Since elements of p-adic rings and fields need to use powers
of p over and over, this class precomputes and stores powers of p.
There is no reason that the base has to be prime however.

EXAMPLES::

    sage: X = PowComputer(3, 4, 10)
    sage: X(3)
    27
    sage: X(10) == 3^10
    True

AUTHORS:

- David Roe
"""

#*****************************************************************************
#       Copyright (C) 2007 David Roe <roed@math.harvard.edu>
#                          William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************



import weakref
from sage.rings.infinity import infinity

include "../../ext/gmp.pxi"
include "../../ext/interrupt.pxi"
include "../../ext/stdsage.pxi"

cdef long maxpreccap = (1L << (sizeof(long) * 8 - 2)) - 1

cdef class PowComputer_class(SageObject):
    def __cinit__(self, Integer prime, long cache_limit, long prec_cap, long ram_prec_cap, bint in_field, poly=None, shift_seed=None):
        """
        Creates a new PowComputer_class.

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC.pow_Integer_Integer(2)
            9
        """
        self.prime = prime
        self.in_field = in_field
        self.cache_limit = cache_limit
        self.prec_cap = prec_cap

    def __init__(self, Integer prime, long cache_limit, long prec_cap, long ram_prec_cap, bint in_field, poly=None, shift_seed=None):
        """
        Initializes self.

        INPUT::

            * prime -- the prime that is the base of the exponentials
              stored in this pow_computer.

            * cache_limit -- how high to cache powers of prime.

            * prec_cap -- data stored for p-adic elements using this
              pow_computer (so they have C-level access to fields
              common to all elements of the same parent).

            * ram_prec_cap -- prec_cap * e

            * in_field -- same idea as prec_cap

            * poly -- same idea as prec_cap

            * shift_seed -- same idea as prec_cap

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC.pow_Integer_Integer(2)
            9
        """
        self._initialized = 1

    def __cmp__(self, other):
        """
        Compares self to other

        EXAMPLES::

            sage: P = PowComputer(3, 4, 9)
            sage: P == 7
            False
            sage: Q = PowComputer(3, 6, 9)
            sage: P == Q
            False
            sage: Q = PowComputer(3, 4, 9)
            sage: P == Q
            True
            sage: P is Q
            True
        """
        a = cmp(type(self), type(other))
        cdef PowComputer_class o
        if a == 0:
            o = <PowComputer_class>other
            if self.prime < o.prime:
                return -1
            elif self.prime > o.prime:
                return 1
            elif self.prec_cap < o.prec_cap:
                return -1
            elif self.prec_cap > o.prec_cap:
                return 1
            elif self.cache_limit < o.cache_limit:
                return -1
            elif self.cache_limit > o.cache_limit:
                return 1
            elif self.in_field < o.in_field:
                return -1
            elif self.in_field > o.in_field:
                return 1
            else:
                return 0
        else:
            return cmp(type(self), type(other))

    cdef Integer pow_Integer(self, long n):
        """
        Returns self.prime^n

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC.pow_Integer_Integer(2) #indirect doctest
            9
        """
        cdef Integer ans = PY_NEW(Integer)
        mpz_set(ans.value, self.pow_mpz_t_tmp(n)[0])
        return ans

    def pow_Integer_Integer(self, n):
        """
        Tests the pow_Integer function.

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC.pow_Integer_Integer(4)
            81
            sage: PC.pow_Integer_Integer(6)
            729
            sage: PC.pow_Integer_Integer(0)
            1
            sage: PC.pow_Integer_Integer(10)
            59049
            sage: PC = PowComputer_ext_maker(3, 5, 10, 20, False, ntl.ZZ_pX([-3,0,1], 3^10), 'big','e',ntl.ZZ_pX([1],3^10))
            sage: PC.pow_Integer_Integer(4)
            81
            sage: PC.pow_Integer_Integer(6)
            729
            sage: PC.pow_Integer_Integer(0)
            1
            sage: PC.pow_Integer_Integer(10)
            59049
        """
        cdef Integer _n = Integer(n)
        cdef Integer ans
        if _n < 0:
            if mpz_fits_ulong_p((<Integer>-_n).value) == 0:
                raise ValueError, "result too big"
            return ~self.pow_Integer(mpz_get_ui((<Integer>-_n).value))
        else:
            if mpz_fits_ulong_p(_n.value) == 0:
                raise ValueError, "result too big"
            return self.pow_Integer(mpz_get_ui(_n.value))

    cdef mpz_t* pow_mpz_t_tmp(self, long n):
        """
        Provides fast access to an mpz_t* pointing to self.prime^n.

        The location pointed to depends on the underlying
        representation.  In no circumstances should you mpz_clear the
        result.  The value pointed to may be an internal temporary
        variable for the class.  In particular, you should not try to
        refer to the results of two pow_mpz_t_tmp calls at the same
        time, because the second call may overwrite the memory pointed
        to by the first.

        See pow_mpz_t_tmp_demo for an example of this phenomenon.
        """
        ## READ THE DOCSTRING
        raise NotImplementedError

    def _pow_mpz_t_tmp_demo(self, m, n):
        """
        This function demonstrates a danger in using pow_mpz_t_tmp.

        EXAMPLES::

            sage: PC = PowComputer(5, 5, 10)

            When you cal pow_mpz_t_tmp with an input that is not stored
            (ie n > self.cache_limit and n != self.prec_cap),
            it stores the result in self.temp_m and returns a pointer
            to that mpz_t.  So if you try to use the results of two
            calls at once, things will break.
            sage: PC._pow_mpz_t_tmp_demo(6, 8) # 244140625 on some architectures and 152587890625 on others: random
            244140625
            sage: 5^6*5^8
            6103515625
            sage: 5^6*5^6
            244140625

            Note that this does not occur if you try a stored value,
            because the result of one of the calls points to that
            stored value.
            sage: PC._pow_mpz_t_tmp_demo(6, 10)
            152587890625
            sage: 5^6*5^10
            152587890625
        """
        m = Integer(m)
        n = Integer(n)
        if m < 0 or n < 0:
            raise ValueError, "m, n must be non-negative"
        cdef Integer ans = PY_NEW(Integer)
        mpz_mul(ans.value, self.pow_mpz_t_tmp(mpz_get_ui((<Integer>m).value))[0], self.pow_mpz_t_tmp(mpz_get_ui((<Integer>n).value))[0])
        return ans

    def _pow_mpz_t_tmp_test(self, n):
        """
        Tests the pow_mpz_t_tmp function.

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC._pow_mpz_t_tmp_test(4)
            81
            sage: PC._pow_mpz_t_tmp_test(6)
            729
            sage: PC._pow_mpz_t_tmp_test(0)
            1
            sage: PC._pow_mpz_t_tmp_test(10)
            59049
            sage: PC = PowComputer_ext_maker(3, 5, 10, 20, False, ntl.ZZ_pX([-3,0,1], 3^10), 'big','e',ntl.ZZ_pX([1],3^10))
            sage: PC._pow_mpz_t_tmp_test(4)
            81
            sage: PC._pow_mpz_t_tmp_test(6)
            729
            sage: PC._pow_mpz_t_tmp_test(0)
            1
            sage: PC._pow_mpz_t_tmp_test(10)
            59049
        """
        cdef Integer _n = Integer(n)
        cdef Integer ans = PY_NEW(Integer)
        mpz_set(ans.value, self.pow_mpz_t_tmp(mpz_get_ui(_n.value))[0])
        return ans

    cdef mpz_t* pow_mpz_t_top(self):
        """
        Returns a pointer to self.prime^self.prec_cap as an mpz_t*.

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC._pow_mpz_t_top_test() #indirect doctest
            59049
        """
        raise NotImplementedError

    def _pow_mpz_t_top_test(self):
        """
        Tests the pow_mpz_t_top function.

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC._pow_mpz_t_top_test()
            59049
            sage: PC = PowComputer_ext_maker(3, 5, 10, 20, False, ntl.ZZ_pX([-3,0,1], 3^10), 'big','e',ntl.ZZ_pX([1],3^10))
            sage: PC._pow_mpz_t_top_test()
            59049
        """
        cdef Integer ans = PY_NEW(Integer)
        mpz_set(ans.value, self.pow_mpz_t_top()[0])
        return ans

    def __repr__(self):
        """
        Returns a string representation of self.

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10); PC
            PowComputer for 3
        """
        return "PowComputer for %s"%(self.prime)

    def _prime(self):
        """
        Returns the base that the PowComputer is exponentiating.

        EXAMPLES::

            sage: P = PowComputer(6, 10, 15)
            sage: P._prime()
            6
        """
        return self.prime

    def _in_field(self):
        """
        Returns whether or not self is attached to a field.

        EXAMPLES::

            sage: P = PowComputer(3, 5, 10)
            sage: P._in_field()
            False
        """
        return self.in_field

    def _cache_limit(self):
        """
        Returns the limit to which powers of prime are computed.

        EXAMPLES::

            sage: P = PowComputer(3, 5, 10)
            sage: P._cache_limit()
            5
        """
        cdef Integer ans
        ans = PY_NEW(Integer)
        mpz_set_ui(ans.value, self.cache_limit)
        return ans

    def _prec_cap(self):
        """
        Returns prec_cap, a single value that for which
        self._prime()^prec_cap is stored

        EXAMPLES::

            sage: P = PowComputer(3, 5, 10)
            sage: P._prec_cap()
            10
        """
        cdef Integer ans
        ans = PY_NEW(Integer)
        mpz_set_ui(ans.value, self.prec_cap)
        return ans

    def _top_power(self):
        """
        Returns self._prime()^self._prec_cap()

        EXAMPLES::

            sage: P = PowComputer(3, 4, 6)
            sage: P._top_power()
            729
        """
        cdef Integer ans
        ans = PY_NEW(Integer)
        mpz_set(ans.value, self.pow_mpz_t_top()[0])
        return ans

    def __call__(self, n):
        """
        Returns self.prime^n.

        EXAMPLES::

            sage: P = PowComputer(3, 4, 6)
            sage: P(3)
            27
            sage: P(6)
            729
            sage: P(5)
            243
            sage: P(7)
            2187
            sage: P(0)
            1
            sage: P(-2)
            1/9
        """
        cdef Integer z, _n
        cdef mpz_t tmp
        if n is infinity:
            return Integer(0)
        if not PY_TYPE_CHECK(n, Integer):
            _n = Integer(n)
        else:
            _n = <Integer>n
        if mpz_fits_slong_p(_n.value) == 0:
            raise ValueError, "n too big"
        if _n < 0:
            return ~self.pow_Integer(-mpz_get_si(_n.value))
        else:
            return self.pow_Integer(mpz_get_ui(_n.value))

cdef class PowComputer_base(PowComputer_class):
    def __cinit__(self, Integer prime, long cache_limit, long prec_cap, long ram_prec_cap, bint in_field, poly=None, shift_seed=None):
        """
        Initializes a PowComputer_base.

        EXAMPLES::

            sage: PC = PowComputer(5, 7, 10)
            sage: PC(3)
            125
        """
        (<PowComputer_class>self)._initialized = 0
        sig_on()
        self.small_powers = <mpz_t *>sage_malloc(sizeof(mpz_t) * (cache_limit + 1))
        sig_off()
        if self.small_powers == NULL:
            raise MemoryError, "out of memory allocating power storing"
        mpz_init(self.top_power)
        mpz_init(self.temp_m)

        cdef Py_ssize_t i
        cdef Integer x

        mpz_init_set_ui(self.small_powers[0], 1)
        if cache_limit > 0:
            mpz_init_set(self.small_powers[1], prime.value)

        for i from 2 <= i <= cache_limit:
            mpz_init(self.small_powers[i])
            mpz_mul(self.small_powers[i], self.small_powers[i - 1], prime.value)
        mpz_pow_ui(self.top_power, prime.value, prec_cap)
        (<PowComputer_class>self)._initialized = 1

    def __dealloc__(self):
        """
        Deletion.

        EXAMPLES::

            sage: P = PowComputer(5, 7, 10)
            sage: del P
            sage: PowComputer(5, 7, 10)
            PowComputer for 5
        """
        cdef Py_ssize_t i
        if (<PowComputer_class>self)._initialized:
            for i from 0 <= i <= self.cache_limit:
                mpz_clear(self.small_powers[i])
            sage_free(self.small_powers)
            mpz_clear(self.top_power)
            mpz_clear(self.temp_m)


    def __reduce__(self):
        """
        Pickling.

        EXAMPLES::

            sage: P = PowComputer(5, 7, 10)
            sage: R = loads(dumps(P))
            sage: P == R
            True
        """
        return PowComputer, (self.prime, self.cache_limit, self.prec_cap, self.in_field)

    cdef mpz_t* pow_mpz_t_top(self):
        """
        Returns a pointer to self.prime^self.prec_cap as an mpz_t*.

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC._pow_mpz_t_top_test() #indirect doctest
            59049
        """
        return &self.top_power

    cdef mpz_t* pow_mpz_t_tmp(self, long n):
        """
        Computes self.prime^n.

        EXAMPLES::

            sage: PC = PowComputer(3, 5, 10)
            sage: PC._pow_mpz_t_tmp_test(4)
            81
        """
        if n <= self.cache_limit:
            return &(self.small_powers[n])
        if n == self.prec_cap:
            return &(self.top_power)
        mpz_pow_ui(self.temp_m, self.prime.value, n)
        return &(self.temp_m)

pow_comp_cache = {}
cdef PowComputer_base PowComputer_c(Integer m, Integer cache_limit, Integer prec_cap, in_field):
    """
    Returns a PowComputer.

    EXAMPLES::

        sage: PC = PowComputer(3, 5, 10) # indirect doctest
        sage: PC(4)
        81
    """
    if cache_limit < 0:
        raise ValueError, "cache_limit must be non-negative."
    if prec_cap < 0:
        raise ValueError, "prec_cap must be non-negative."
    if mpz_cmp_si((<Integer>prec_cap).value, maxpreccap) >= 0:
        raise ValueError, "cannot create p-adic parents with precision cap larger than (1 << (sizeof(long)*8 - 2))"

    key = (m, cache_limit, prec_cap, in_field)
    if pow_comp_cache.has_key(key):
        PC = pow_comp_cache[key]()
        if PC is not None:
            return PC
    PC = PowComputer_base(m, mpz_get_ui(cache_limit.value), mpz_get_ui(prec_cap.value), mpz_get_ui(prec_cap.value), in_field)
    pow_comp_cache[key] = weakref.ref(PC)
    return PC

# To speed up the creation of PowComputers with the same m, we might eventually want to copy over data from an existing PowComputer.

def PowComputer(m, cache_limit, prec_cap, in_field = False):
    r"""
    Returns a PowComputer that caches the values $1, m, m^2, \ldots, m^{C}$,
    where $C$ is ``cache_limit``.

    Once you create a PowComputer, merely call it to get values out.

    You can input any integer, even if it's outside of the precomputed
    range.

    INPUT::

        * m -- An integer, the base that you want to exponentiate.
        * cache_limit -- A positive integer that you want to cache powers up to.

    EXAMPLES::

        sage: PC = PowComputer(3, 5, 10)
        sage: PC
        PowComputer for 3
        sage: PC(4)
        81
        sage: PC(6)
        729
        sage: PC(-1)
        1/3
    """
    if not PY_TYPE_CHECK(m, Integer):
        m = Integer(m)
    if not PY_TYPE_CHECK(cache_limit, Integer):
        cache_limit = Integer(cache_limit)
    if not PY_TYPE_CHECK(prec_cap, Integer):
        prec_cap = Integer(prec_cap)
    return PowComputer_c(m, cache_limit, prec_cap, in_field)
