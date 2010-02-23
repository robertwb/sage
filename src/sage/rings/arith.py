"""
Miscellaneous arithmetic functions
"""

###########################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
###########################################################################

import math
import sys
import sage.misc.misc as misc
import sage.misc.search
from sage.libs.pari.gen import pari, PariError, vecsmall_to_intlist

from sage.rings.rational_field import QQ
import sage.rings.rational
import sage.rings.complex_field
import sage.rings.complex_number
import sage.rings.real_mpfr
import sage.structure.factorization as factorization
from sage.structure.element import RingElement, canonical_coercion, bin_op, parent
from sage.interfaces.all import gp
from sage.misc.misc import prod, union
from sage.rings.fraction_field_element import is_FractionFieldElement

import fast_arith

from integer_ring import ZZ
import integer

##################################################################
# Elementary Arithmetic
##################################################################

def algdep(z, n, known_bits=None, use_bits=None, known_digits=None, use_digits=None):
    """
    Returns a polynomial of degree at most `n` which is
    approximately satisfied by the number `z`. Note that the
    returned polynomial need not be irreducible, and indeed usually
    won't be if `z` is a good approximation to an algebraic
    number of degree less than `n`.

    You can specify the number of known bits or digits with ``known_bits=k`` or
    ``known_digits=k``; Pari is then told to compute the result using `0.8k`
    of these bits/digits. (The Pari documentation recommends using a factor
    between .6 and .9, but internally defaults to .8.) Or, you can specify the
    precision to use directly with ``use_bits=k`` or ``use_digits=k``. If none
    of these are specified, then the precision is taken from the input value.

    ALGORITHM: Uses the PARI C-library algdep command.

    Note that ``algebraic_dependency`` is a synonym for ``algdep``.

    INPUT:


    -  ``z`` - real, complex, or `p`-adic number

    -  ``n`` - an integer


    EXAMPLES::

        sage: algdep(1.888888888888888, 1)
        9*x - 17
        sage: algdep(0.12121212121212,1)
        33*x - 4
        sage: algdep(sqrt(2),2)
        x^2 - 2

    This example involves a complex number.

    ::

        sage: z = (1/2)*(1 + RDF(sqrt(3)) *CC.0); z
        0.500000000000000 + 0.866025403784439*I
        sage: p = algdep(z, 6); p
        x^3 + 1
        sage: p.factor()
        (x + 1) * (x^2 - x + 1)
        sage: z^2 - z + 1
        0

    This example involves a `p`-adic number.

    ::

        sage: K = Qp(3, print_mode = 'series')
        sage: a = K(7/19); a
        1 + 2*3 + 3^2 + 3^3 + 2*3^4 + 2*3^5 + 3^8 + 2*3^9 + 3^11 + 3^12 + 2*3^15 + 2*3^16 + 3^17 + 2*3^19 + O(3^20)
        sage: algdep(a, 1)
        19*x - 7

    These examples show the importance of proper precision control. We
    compute a 200-bit approximation to sqrt(2) which is wrong in the
    33'rd bit.

    ::

        sage: z = sqrt(RealField(200)(2)) + (1/2)^33
        sage: p = algdep(z, 4); p
        177858662573*x^4 + 59566570004*x^3 - 221308611561*x^2 - 84791308378*x - 317384111411
        sage: factor(p)
        177858662573*x^4 + 59566570004*x^3 - 221308611561*x^2 - 84791308378*x - 317384111411
        sage: algdep(z, 4, known_bits=32)
        x^2 - 2
        sage: algdep(z, 4, known_digits=10)
        x^2 - 2
        sage: algdep(z, 4, use_bits=25)
        x^2 - 2
        sage: algdep(z, 4, use_digits=8)
        x^2 - 2
    """

    # TODO -- change to use PARI C library???
    from sage.rings.polynomial.polynomial_ring import polygen
    x = polygen(ZZ)

    if isinstance(z, (int, long, integer.Integer)):
        return x - ZZ(z)

    n = ZZ(n)

    if isinstance(z, (sage.rings.rational.Rational)):
        return z.denominator()*x - z.numerator()

    if isinstance(z, float):
        z = sage.rings.real_mpfr.RealField()(z)
    elif isinstance(z, complex):
        z = sage.rings.complex_field.ComplexField()(z)

    if isinstance(z, (sage.rings.real_mpfr.RealNumber,
                      sage.rings.complex_number.ComplexNumber)):
        # We need to specify a precision.  Otherwise, Pari will default
        # to using 80% of the bits in the Pari value; for certain precisions,
        # this could be very wrong.  (On a 32-bit machine, a RealField(33)
        # value gets translated to a 64-bit Pari value; so Pari would
        # try to use about 51 bits of our 32-bit value.  Similarly
        # bad things would happen on a 64-bit machine with RealField(65).)
        log2 = 0.301029995665
        digits = int(log2 * z.prec()) - 2
        if known_bits is not None:
            known_digits = log2 * known_bits
        if known_digits is not None:
            use_digits = known_digits * 0.8
        if use_bits is not None:
            use_digits = log2 * use_bits
        if use_digits is not None:
            digits = int(use_digits)
        if digits == 0:
            digits = 1
        f = pari(z).algdep(n, digits)
    else:
        y = pari(z)
        f = y.algdep(n)

    return x.parent()(f)


algebraic_dependency = algdep

def bernoulli(n, algorithm='default', num_threads=1):
    r"""
    Return the n-th Bernoulli number, as a rational number.

    INPUT:

    -  ``n`` - an integer
    -  ``algorithm``:

       -  ``'default'`` - (default) use 'pari' for n <= 30000, and 'bernmm' for
          n > 30000 (this is just a heuristic, and not guaranteed to be optimal
          on all hardware)
       -  ``'pari'`` - use the PARI C library
       -  ``'gap'`` - use GAP
       -  ``'gp'`` - use PARI/GP interpreter
       -  ``'magma'`` - use MAGMA (optional)
       -  ``'bernmm'`` - use bernmm package (a multimodular algorithm)

    -  ``num_threads`` - positive integer, number of
       threads to use (only used for bernmm algorithm)

    EXAMPLES::

        sage: bernoulli(12)
        -691/2730
        sage: bernoulli(50)
        495057205241079648212477525/66

    We demonstrate each of the alternative algorithms::

        sage: bernoulli(12, algorithm='gap')
        -691/2730
        sage: bernoulli(12, algorithm='gp')
        -691/2730
        sage: bernoulli(12, algorithm='magma')           # optional - magma
        -691/2730
        sage: bernoulli(12, algorithm='pari')
        -691/2730
        sage: bernoulli(12, algorithm='bernmm')
        -691/2730
        sage: bernoulli(12, algorithm='bernmm', num_threads=4)
        -691/2730

    TESTS::

        sage: algs = ['gap','gp','pari','bernmm']
        sage: test_list = [ZZ.random_element(2, 2255) for _ in range(500)]
        sage: vals = [[bernoulli(i,algorithm = j) for j in algs] for i in test_list] #long time (19s)
        sage: union([len(union(x))==1 for x in vals]) #long time (depends on previous line)
        [True]
        sage: algs = ['gp','pari','bernmm']
        sage: test_list = [ZZ.random_element(2256, 5000) for _ in range(500)]
        sage: vals = [[bernoulli(i,algorithm = j) for j in algs] for i in test_list] #long time (21s)
        sage: union([len(union(x))==1 for x in vals]) #long time (depends on previous line)
        [True]

    AUTHOR:

    - David Joyner and William Stein
    """
    from sage.rings.all import Integer, Rational
    n = Integer(n)

    if algorithm == 'default':
        algorithm = 'pari' if n <= 30000 else 'bernmm'

    if algorithm == 'pari':
        x = pari(n).bernfrac()         # Use the PARI C library
        return Rational(x)
    elif algorithm == 'gap':
        import sage.interfaces.gap
        x = sage.interfaces.gap.gap('Bernoulli(%s)'%n)
        return Rational(x)
    elif algorithm == 'magma':
        import sage.interfaces.magma
        x = sage.interfaces.magma.magma('Bernoulli(%s)'%n)
        return Rational(x)
    elif algorithm == 'gp':
        import sage.interfaces.gp
        x = sage.interfaces.gp.gp('bernfrac(%s)'%n)
        return Rational(x)
    elif algorithm == 'bernmm':
        import sage.rings.bernmm
        return sage.rings.bernmm.bernmm_bern_rat(n, num_threads)
    else:
        raise ValueError, "invalid choice of algorithm"


def factorial(n, algorithm='gmp'):
    r"""
    Compute the factorial of `n`, which is the product
    `1\cdot 2\cdot 3 \cdots (n-1)\cdot n`.

    INPUT:

    -  ``n`` - an integer

    -  ``algorithm`` - string (default: 'gmp'):

       -  ``'gmp'`` - use the GMP C-library factorial function

       -  ``'pari'`` - use PARI's factorial function

    OUTPUT: an integer

    EXAMPLES::

        sage: from sage.rings.arith import factorial
        sage: factorial(0)
        1
        sage: factorial(4)
        24
        sage: factorial(10)
        3628800
        sage: factorial(1) == factorial(0)
        True
        sage: factorial(6) == 6*5*4*3*2
        True
        sage: factorial(1) == factorial(0)
        True
        sage: factorial(71) == 71* factorial(70)
        True
        sage: factorial(-32)
        Traceback (most recent call last):
        ...
        ValueError: factorial -- must be nonnegative

    PERFORMANCE: This discussion is valid as of April 2006. All timings
    below are on a Pentium Core Duo 2Ghz MacBook Pro running Linux with
    a 2.6.16.1 kernel.


    -  It takes less than a minute to compute the factorial of
       `10^7` using the GMP algorithm, and the factorial of
       `10^6` takes less than 4 seconds.

    -  The GMP algorithm is faster and more memory efficient than the
       PARI algorithm. E.g., PARI computes `10^7` factorial in 100
       seconds on the core duo 2Ghz.

    -  For comparison, computation in Magma `\leq` 2.12-10 of
       `n!` is best done using ``*[1..n]``. It takes
       113 seconds to compute the factorial of `10^7` and 6
       seconds to compute the factorial of `10^6`. Mathematica
       V5.2 compute the factorial of `10^7` in 136 seconds and the
       factorial of `10^6` in 7 seconds. (Mathematica is notably
       very efficient at memory usage when doing factorial
       calculations.)
    """
    if n < 0:
        raise ValueError, "factorial -- must be nonnegative"
    if algorithm == 'gmp':
        return ZZ(n).factorial()
    elif algorithm == 'pari':
        return pari.factorial(n)
    else:
        raise ValueError, 'unknown algorithm'

def is_prime(n):
    r"""
    Returns ``True`` if `n` is prime, and ``False`` otherwise.

    AUTHORS:

    - Kevin Stueve kstueve@uw.edu (2010-01-17):
      delegated calculation to ``n.is_prime()``

    INPUT:

    -  ``n`` - the object for which to determine primality

    OUTPUT:

    -  ``bool`` - ``True`` or ``False``

    EXAMPLES::

        sage: is_prime(389)
        True
        sage: is_prime(2000)
        False
        sage: is_prime(2)
        True
        sage: is_prime(-1)
        False
        sage: factor(-6)
        -1 * 2 * 3
        sage: is_prime(1)
        False
        sage: is_prime(-2)
        False

    ALGORITHM:

    Calculation is delegated to the ``n.is_prime()`` method, or in special
    cases (e.g., Python ``int``s) to ``Integer(n).is_prime()``.  If an
    ``n.is_prime()`` method is not available, it otherwise raises a
    ``TypeError``.
    """
    if isinstance(n, sage.symbolic.expression.Expression):
        try:
            n = n.pyobject()
        except TypeError:
            pass
    if isinstance(n, int) or isinstance(n, long):
        from sage.rings.integer import Integer
        return Integer(n).is_prime()

    try:
        return n.is_prime()
    except AttributeError:
        raise TypeError, "is_prime() is not written for this type"

def is_pseudoprime(n, flag=0):
    r"""
    Returns True if `x` is a pseudo-prime, and False otherwise.
    The result is *NOT* proven correct -
    *this is a pseudo-primality test!*.

    INPUT:

    -  ``flag`` - int

       - ``0`` (default): checks whether x is a Baillie-Pomerance-
         Selfridge-Wagstaff pseudo prime (strong Rabin-Miller pseudo
         prime for base 2, followed by strong Lucas test for the
         sequence (P,-1), P smallest positive integer such that
         `P^2 - 4` is not a square mod x).

       - ``>0``: checks whether x is a strong Miller-Rabin pseudo
         prime for flag randomly chosen bases (with end-matching to
         catch square roots of -1).

    OUTPUT:

    -  ``bool`` - True or False

    .. note::

       We do not consider negatives of prime numbers as prime.

    EXAMPLES:::

        sage: is_pseudoprime(389)
        True
        sage: is_pseudoprime(2000)
        False
        sage: is_pseudoprime(2)
        True
        sage: is_pseudoprime(-1)
        False
        sage: factor(-6)
        -1 * 2 * 3
        sage: is_pseudoprime(1)
        False
        sage: is_pseudoprime(-2)
        False

    IMPLEMENTATION: Calls the PARI ispseudoprime function.
    """
    n = ZZ(n)
    return pari(n).ispseudoprime()

def is_prime_power(n, flag=0):
    r"""
    Returns True if `x` is a prime power, and False otherwise.
    The result is proven correct -
    *this is NOT a  pseudo-primality test!*.

    INPUT:


    -  ``n`` - an integer

    -  ``flag (for primality testing)`` - int

       - ``0`` (default): use a combination of algorithms.

       - ``1``: certify primality using the Pocklington-Lehmer Test.

       - ``2``: certify primality using the APRCL test.


    EXAMPLES:::

        sage: is_prime_power(389)
        True
        sage: is_prime_power(2000)
        False
        sage: is_prime_power(2)
        True
        sage: is_prime_power(1024)
        True
        sage: is_prime_power(-1)
        False
        sage: is_prime_power(1)
        True
        sage: is_prime_power(997^100)
        True
    """
    return ZZ(n).is_prime_power(flag=flag)

def valuation(m, p):
    """
    The exact power of p that divides m.

    m should be an integer or rational (but maybe other types work
    too.)

    This actually just calls the m.valuation() method.

    If m is 0, this function returns rings.infinity.

    EXAMPLES::

        sage: valuation(512,2)
        9
        sage: valuation(1,2)
        0
        sage: valuation(5/9, 3)
        -2

    Valuation of 0 is defined, but valuation with respect to 0 is not::

        sage: valuation(0,7)
        +Infinity
        sage: valuation(3,0)
        Traceback (most recent call last):
        ...
        ValueError: You can only compute the valuation with respect to a integer larger than 1.

    Here are some other examples::

        sage: valuation(100,10)
        2
        sage: valuation(200,10)
        2
        sage: valuation(243,3)
        5
        sage: valuation(243*10007,3)
        5
        sage: valuation(243*10007,10007)
        1
    """
    if hasattr(m, 'valuation'):
        return m.valuation(p)
    if m == 0:
        import sage.rings.all
        return sage.rings.all.infinity
    if is_FractionFieldElement(m):
        return valuation(m.numerator()) - valuation(m.denominator())
    r = 0
    power = p
    while not (m % power): # m % power == 0
        r += 1
        power *= p
    return r

def prime_powers(start, stop=None):
    r"""
    List of all positive primes powers between start and stop-1,
    inclusive. If the second argument is omitted, returns the primes up
    to the first argument.

    EXAMPLES::

        sage: prime_powers(20)
        [1, 2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19]
        sage: len(prime_powers(1000))
        194
        sage: len(prime_range(1000))
        168
        sage: a = [z for z in range(95,1234) if is_prime_power(z)]
        sage: b = prime_powers(95,1234)
        sage: len(b)
        194
        sage: len(a)
        194
        sage: a[:10]
        [97, 101, 103, 107, 109, 113, 121, 125, 127, 128]
        sage: b[:10]
        [97, 101, 103, 107, 109, 113, 121, 125, 127, 128]
        sage: a == b
        True

    TESTS::

        sage: v = prime_powers(10)
        sage: type(v[0])      # trac #922
        <type 'sage.rings.integer.Integer'>
    """
    if stop is None:
        start, stop = 1, integer.Integer(start)
    from math import log
    from bisect import bisect
    v = fast_arith.prime_range(stop)
    i = bisect(v, start)
    if start > 2:
        if v[i] == start:
            i -= 1
        w = list(v[i:])
    else:
        w = list(v)
    if start <= 1:
        w.insert(0, integer.Integer(1))
    log_stop = log(stop)
    for p in v:
        q = p*p
        n = int(log(stop)/log(p))
        if n <= 1:
            break
        for i in xrange(1,n):
            if q >= start:
                w.append(q)
            q *= p
    w.sort()
    return w


def primes_first_n(n, leave_pari=False):
    r"""
    Return the first `n` primes.

    INPUT:

    - `n` - a nonnegative integer

    OUTPUT:

    - a list of the first `n` prime numbers.

    EXAMPLES::

        sage: primes_first_n(10)
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        sage: len(primes_first_n(1000))
        1000
        sage: primes_first_n(0)
        []
    """
    if n < 0:
        raise ValueError, "n must be nonnegative"
    if n < 1:
        return []
    return fast_arith.prime_range(pari.nth_prime(n) + 1)

#
# This is from
#    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/366178
# It's impressively fast given that it's in Pure Python.
#
def eratosthenes(n):
    r"""
    Return a list of the primes `\leq n`.

    This is extremely slow and is for educational purposes only.

    INPUT:

    -  ``n`` - a positive integer

    OUTPUT:

    - a list of primes less than or equal to n.


    EXAMPLES::

        sage: len(eratosthenes(100))
        25
        sage: eratosthenes(3)
        [2, 3]
    """
    n = int(n)
    if n == 2:
        return [2]
    elif n<2:
        return []
    s = range(3,n+3,2)
    mroot = n ** 0.5
    half = (n+1)/2
    i = 0
    m = 3
    while m <= mroot:
        if s[i]:
            j = (m*m-3)/2
            s[j] = 0
            while j < half:
                s[j] = 0
                j += m
        i = i+1
        m = 2*i+3
    return [ZZ(2)] + [ZZ(x) for x in s if x and x <= n]

# My old versions; not as fast as the above.
## def eratosthenes(n):
##     """
##     Returns a list of the primes up to n, computed
##     using the Sieve of Eratosthenes.
##     Input:
##         n -- a positive integer
##     Output:
##         list -- a list of the primes up to n
##     Examples:
##     sage: eratosthenes(7)
##     [2, 3, 5, 7]
##     sage: eratosthenes(45)
##     [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
##     """
##     if n <= 1: return []
##     X = [i for i in range(3,n+1) if i%2 != 0]
##     P = [2]
##     sqrt_n = sqrt(n)
##     while len(X) > 0 and X[0] <= sqrt_n:
##         p = X[0]
##         P.append(p)
##         X = [a for a in X if a%p != 0]
##     return P + X

def primes(start, stop=None):
    r"""
    Returns an iterator over all primes between start and stop-1,
    inclusive. This is much slower than ``prime_range``,
    but potentially uses less memory.

    This command is like the xrange command, except it only iterates
    over primes. In some cases it is better to use primes than
    prime_range, because primes does not build a list of all primes in
    the range in memory all at once. However it is potentially much
    slower since it simply calls the ``next_prime``
    function repeatedly, and ``next_prime`` is slow,
    partly because it proves correctness.

    EXAMPLES::

        sage: for p in primes(5,10):
        ...     print p
        ...
        5
        7
        sage: list(primes(11))
        [2, 3, 5, 7]
        sage: list(primes(10000000000, 10000000100))
        [10000000019, 10000000033, 10000000061, 10000000069, 10000000097]
    """

    start = ZZ(start)
    if stop == None:
        stop = start
        start = ZZ(2)
    else:
        stop = ZZ(stop)
    n = start - 1
    while True:
        n = next_prime(n)
        if n < stop:
            yield n
        else:
            return

def next_prime_power(n):
    """
    The next prime power greater than the integer n. If n is a prime
    power, then this function does not return n, but the next prime
    power after n.

    EXAMPLES::

        sage: next_prime_power(-10)
        1
        sage: is_prime_power(1)
        True
        sage: next_prime_power(0)
        1
        sage: next_prime_power(1)
        2
        sage: next_prime_power(2)
        3
        sage: next_prime_power(10)
        11
        sage: next_prime_power(7)
        8
        sage: next_prime_power(99)
        101
    """
    if n < 0:   # negatives are not prime.
        return ZZ(1)
    if n == 2:
        return ZZ(3)
    n = ZZ(n) + 1
    while not is_prime_power(n):  # pari isprime is provably correct
        n += 1
    return n

def next_probable_prime(n):
    """
    Returns the next probable prime after self, as determined by PARI.

    INPUT:


    -  ``n`` - an integer


    EXAMPLES::

        sage: next_probable_prime(-100)
        2
        sage: next_probable_prime(19)
        23
        sage: next_probable_prime(int(999999999))
        1000000007
        sage: next_probable_prime(2^768)
        1552518092300708935148979488462502555256886017116696611139052038026050952686376886330878408828646477950487730697131073206171580044114814391444287275041181139204454976020849905550265285631598444825262999193716468750892846853816058039
    """
    return ZZ(n).next_probable_prime()

def next_prime(n, proof=None):
    """
    The next prime greater than the integer n. If n is prime, then this
    function does not return n, but the next prime after n. If the
    optional argument proof is False, this function only returns a
    pseudo-prime, as defined by the PARI nextprime function. If it is
    None, uses the global default (see :mod:`sage.structure.proof.proof`)

    INPUT:


    -  ``n`` - integer

    -  ``proof`` - bool or None (default: None)


    EXAMPLES::

        sage: next_prime(-100)
        2
        sage: next_prime(1)
        2
        sage: next_prime(2)
        3
        sage: next_prime(3)
        5
        sage: next_prime(4)
        5

    Notice that the next_prime(5) is not 5 but 7.

    ::

        sage: next_prime(5)
        7
        sage: next_prime(2004)
        2011
    """
    try:
        return n.next_prime(proof)
    except AttributeError:
        return ZZ(n).next_prime(proof)

def previous_prime(n):
    """
    The largest prime < n. The result is provably correct. If n <= 1,
    this function raises a ValueError.

    EXAMPLES::

        sage: previous_prime(10)
        7
        sage: previous_prime(7)
        5
        sage: previous_prime(8)
        7
        sage: previous_prime(7)
        5
        sage: previous_prime(5)
        3
        sage: previous_prime(3)
        2
        sage: previous_prime(2)
        Traceback (most recent call last):
        ...
        ValueError: no previous prime
        sage: previous_prime(1)
        Traceback (most recent call last):
        ...
        ValueError: no previous prime
        sage: previous_prime(-20)
        Traceback (most recent call last):
        ...
        ValueError: no previous prime
    """
    n = ZZ(n)-1
    if n <= 1:
        raise ValueError, "no previous prime"
    if n <= 3:
        return ZZ(n)
    if n%2 == 0:
        n -= 1
    while not is_prime(n):
        n -= 2
    return ZZ(n)

def previous_prime_power(n):
    r"""
    The largest prime power `< n`. The result is provably
    correct. If `n \leq 2`, this function returns `-x`,
    where `x` is prime power and `-x < n` and no larger
    negative of a prime power has this property.

    EXAMPLES::

        sage: previous_prime_power(2)
        1
        sage: previous_prime_power(10)
        9
        sage: previous_prime_power(7)
        5
        sage: previous_prime_power(127)
        125

    ::

        sage: previous_prime_power(0)
        Traceback (most recent call last):
        ...
        ValueError: no previous prime power
        sage: previous_prime_power(1)
        Traceback (most recent call last):
        ...
        ValueError: no previous prime power

    ::

        sage: n = previous_prime_power(2^16 - 1)
        sage: while is_prime(n):
        ...    n = previous_prime_power(n)
        sage: factor(n)
        251^2
    """
    n = ZZ(n)-1
    if n <= 0:
        raise ValueError, "no previous prime power"
    while not is_prime_power(n):
        n -= 1
    return n

def random_prime(n, proof=None, lbound=2):
    """
    Returns a random prime p between `lbound` and n (i.e. `lbound <= p <= n`).
    The returned prime is chosen uniformly at random from the set of prime
    numbers less than or equal to n.

    INPUT:


    -  ``n`` - an integer >= 2.

    -  ``proof`` - bool or None (default: None) If False, the function uses a
       pseudo-primality test, which is much faster for really big numbers but
       does not provide a proof of primality. If None, uses the global default
       (see :mod:`sage.structure.proof.proof`)

    - ``lbound`` - an integer >= 2
      lower bound for the chosen primes


    EXAMPLES::

        sage: random_prime(100000)
        88237
        sage: random_prime(2)
        2

    TESTS::

        sage: type(random_prime(2))
        <type 'sage.rings.integer.Integer'>
        sage: type(random_prime(100))
        <type 'sage.rings.integer.Integer'>

    AUTHORS:

    - Jon Hanke (2006-08-08): with standard Stein cleanup

    - Jonathan Bober (2007-03-17)
    """
    # since we don't want current_randstate to get
    # pulled when you say "from sage.arith import *".
    from sage.misc.randstate import current_randstate
    from sage.structure.proof.proof import get_flag
    proof = get_flag(proof, "arithmetic")
    n = ZZ(n)
    if n < lbound:
        raise ValueError, "n must be greater than lbound: %s"%(lbound)
    elif n == 2:
        return ZZ(n)
    else:
        if not proof:
            prime_test = is_pseudoprime
        else:
            prime_test = is_prime
        randint = current_randstate().python_random().randint
        while(1):
            # In order to ensure that the returned prime is chosen
            # uniformly from the set of primes it is necessary to
            # choose a random number and then test for primality.
            # The method of choosing a random number and then returning
            # the closest prime smaller than it would typically not,
            # for example, return the first of a pair of twin primes.
            p = randint(lbound,n)
            if prime_test(p):
                return ZZ(p)


def divisors(n):
    """
    Returns a list of all positive integer divisors of the nonzero
    integer n.

    INPUT:


    -  ``n`` - the element


    EXAMPLES::

        sage: divisors(-3)
        [1, 3]
        sage: divisors(6)
        [1, 2, 3, 6]
        sage: divisors(28)
        [1, 2, 4, 7, 14, 28]
        sage: divisors(2^5)
        [1, 2, 4, 8, 16, 32]
        sage: divisors(100)
        [1, 2, 4, 5, 10, 20, 25, 50, 100]
        sage: divisors(1)
        [1]
        sage: divisors(0)
        Traceback (most recent call last):
        ...
        ValueError: n must be nonzero
        sage: divisors(2^3 * 3^2 * 17)
        [1, 2, 3, 4, 6, 8, 9, 12, 17, 18, 24, 34, 36, 51, 68, 72, 102, 136, 153, 204, 306, 408, 612, 1224]

    This function works whenever one has unique factorization::

        sage: K.<a> = QuadraticField(7)
        sage: divisors(K.ideal(7))
        [Fractional ideal (1), Fractional ideal (-a), Fractional ideal (7)]
        sage: divisors(K.ideal(3))
        [Fractional ideal (1), Fractional ideal (3), Fractional ideal (a - 2), Fractional ideal (-a - 2)]
        sage: divisors(K.ideal(35))
        [Fractional ideal (1), Fractional ideal (35), Fractional ideal (-5*a), Fractional ideal (5), Fractional ideal (-a), Fractional ideal (7)]

    TESTS::

        sage: divisors(int(300))
        [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 25, 30, 50, 60, 75, 100, 150, 300]
    """
    if not n:
        raise ValueError, "n must be nonzero"

    R = parent(n)
    if R in [int, long]:
        n = ZZ(n) # we have specialized code for this case, make sure it gets used
    try:
        return n.divisors()
    except AttributeError:
        pass
    f = factor(n)
    one = R(1)
    all = [one]
    for p, e in f:
        prev = all[:]
        pn = one
        for i in range(e):
            pn *= p
            all.extend([a*pn for a in prev])
    all.sort()
    return all

class Sigma:
    """
    Return the sum of the k-th powers of the divisors of n.

    INPUT:


    -  ``n`` - integer

    -  ``k`` - integer (default: 1)


    OUTPUT: integer

    EXAMPLES::

        sage: sigma(5)
        6
        sage: sigma(5,2)
        26

    The sigma function also has a special plotting method.

    ::

        sage: P = plot(sigma, 1, 100)

    This method also works with k-th powers.

    ::

        sage: P = plot(sigma, 1, 100, k=2)

    AUTHORS:

    - William Stein: original implementation

    - Craig Citro (2007-06-01): rewrote for huge speedup

    TESTS::

        sage: sigma(100,4)
        106811523
        sage: sigma(factorial(100),3).mod(144169)
        3672
        sage: sigma(factorial(150),12).mod(691)
        176
        sage: RR(sigma(factorial(133),20))
        2.80414775675747e4523
        sage: sigma(factorial(100),0)
        39001250856960000
        sage: sigma(factorial(41),1)
        229199532273029988767733858700732906511758707916800
    """
    def __repr__(self):
        """
        A description of this class, which computes the sum of the
        k-th powers of the divisors of n.

        EXAMPLES::

            sage: Sigma().__repr__()
            'Function that adds up (k-th powers of) the divisors of n'
        """
        return "Function that adds up (k-th powers of) the divisors of n"

    def __call__(self, n, k=1):
        """
        Computes the sum of (the k-th powers of) the divisors of n.

        EXAMPLES::

            sage: q = Sigma()
            sage: q(10)
            18
            sage: q(10,2)
            130
        """
        n = ZZ(n)
        k = ZZ(k)
        one = ZZ(1)

        if (k == ZZ(0)):
            return prod([ expt+one for p, expt in factor(n) ])
        elif (k == one):
            return prod([ (p**(expt+one) - one).divide_knowing_divisible_by(p - one)
                          for p, expt in factor(n) ])
        else:
            return prod([ (p**((expt+one)*k)-one).divide_knowing_divisible_by(p**k-one)
                          for p,expt in factor(n) ])

    def plot(self, xmin=1, xmax=50, k=1, pointsize=30, rgbcolor=(0,0,1), join=True,
             **kwds):
        """
        Plot the sigma (sum of k-th powers of divisors) function.

        INPUT:


        -  ``xmin`` - default: 1

        -  ``xmax`` - default: 50

        -  ``k`` - default: 1

        -  ``pointsize`` - default: 30

        -  ``rgbcolor`` - default: (0,0,1)

        -  ``join`` - default: True; whether to join the
           points.

        -  ``**kwds`` - passed on

        EXAMPLES::

            sage: p = Sigma().plot()
            sage: p.ymax()
            124.0
        """
        v = [(n,sigma(n,k)) for n in range(xmin,xmax + 1)]
        from sage.plot.all import list_plot
        P = list_plot(v, pointsize=pointsize, rgbcolor=rgbcolor, **kwds)
        if join:
            P += list_plot(v, plotjoined=True, rgbcolor=(0.7,0.7,0.7), **kwds)
        return P

sigma = Sigma()

def gcd(a, b=None, **kwargs):
    r"""
    The greatest common divisor of a and b, or if a is a list and b is
    omitted the greatest common divisor of all elements of a.

    INPUT:


    -  ``a,b`` - two elements of a ring with gcd or

    -  ``a`` - a list or tuple of elements of a ring with
       gcd


    Additional keyword arguments are passed to the respectively called
    methods.

    EXAMPLES::

        sage: GCD(97,100)
        1
        sage: GCD(97*10^15, 19^20*97^2)
        97
        sage: GCD(2/3, 4/3)
        1
        sage: GCD([2,4,6,8])
        2
        sage: GCD(srange(0,10000,10))  # fast  !!
        10

    Note that to take the gcd of  `n` elements for `n \not= 2` you must
    put the elements into a list by enclosing them in ``[..]``.  Before
    #4988 the following wrongly returned 3 since the third parameter
    was just ignored::

        sage: gcd(3,6,2)
        Traceback (most recent call last):
        ...
        TypeError: gcd() takes at most 2 arguments (3 given)
        sage: gcd([3,6,2])
        1

    Similarly, giving just one element (which is not a list) gives an error::

        sage: gcd(3)
        Traceback (most recent call last):
        ...
        TypeError: 'sage.rings.integer.Integer' object is not iterable

    By convention, the gcd of the empty list is (the integer) 0::

        sage: gcd([])
        0
        sage: type(gcd([]))
        <type 'sage.rings.integer.Integer'>
    """
    # Most common use case first:
    if b is not None:
        if hasattr(a, "gcd"):
            return a.gcd(b, **kwargs)
        else:
            try:
                return ZZ(a).gcd(ZZ(b))
            except TypeError:
                raise TypeError, "unable to find gcd of %s and %s"%(a,b)

    from sage.structure.sequence import Sequence
    seq = Sequence(a)
    U = seq.universe()
    if U is ZZ or U is int or U is long:# ZZ.has_coerce_map_from(U):
        return sage.rings.integer.GCD_list(a)
    return __GCD_sequence(seq, **kwargs)

GCD = gcd

def __GCD_sequence(v, **kwargs):
    """
    Internal function returning the gcd of the elements of a sequence

    INPUT:


    -  ``v`` - A sequence (possibly empty)


    OUTPUT: The gcd of the elements of the sequence as an element of
    the sequence's universe, or the integer 0 if the sequence is
    empty.

    EXAMPLES::

        sage: from sage.rings.arith import __GCD_sequence
        sage: from sage.structure.sequence import Sequence
        sage: l = ()
        sage: __GCD_sequence(l)
        0
        sage: __GCD_sequence(Sequence(srange(10)))
        1
        sage: X=polygen(QQ)
        sage: __GCD_sequence(Sequence((2*X+4,2*X^2,2)))
        1
        sage: X=polygen(ZZ)
        sage: __GCD_sequence(Sequence((2*X+4,2*X^2,2)))
        2
    """
    if len(v) == 0:
        return ZZ(0)
    if hasattr(v,'universe'):
        g = v.universe()(0)
    else:
        g = ZZ(0)
    one = v.universe()(1)
    for vi in v:
        g = vi.gcd(g, **kwargs)
        if g == one:
            return g
    return g

def lcm(a, b=None):
    """
    The least common multiple of a and b, or if a is a list and b is
    omitted the least common multiple of all elements of a.

    Note that LCM is an alias for lcm.

    INPUT:


    -  ``a,b`` - two elements of a ring with lcm or

    -  ``a`` - a list or tuple of elements of a ring with
       lcm


    EXAMPLES::

        sage: lcm(97,100)
        9700
        sage: LCM(97,100)
        9700
        sage: LCM(0,2)
        0
        sage: LCM(-3,-5)
        15
        sage: LCM([1,2,3,4,5])
        60
        sage: v = LCM(range(1,10000))   # *very* fast!
        sage: len(str(v))
        4349
    """
    # Most common use case first:
    if b is not None:
        if hasattr(a, "lcm"):
            return a.lcm(b)
        else:
            try:
                return ZZ(a).lcm(ZZ(b))
            except TypeError:
                raise TypeError, "unable to find gcd of %s and %s"%(a,b)

    from sage.structure.sequence import Sequence
    seq = Sequence(a)
    U = seq.universe()
    if U is ZZ or U is int or U is long:
        return sage.rings.integer.LCM_list(a)
    return __LCM_sequence(seq)

LCM = lcm

def __LCM_sequence(v):
    """
    Internal function returning the lcm of the elements of a sequence

    INPUT:


    -  ``v`` - A sequence (possibly empty)


    OUTPUT: The lcm of the elements of the sequence as an element of
    the sequence's universe, or the integer 1 if the sequence is
    empty.

    EXAMPLES::

        sage: from sage.structure.sequence import Sequence
        sage: from sage.rings.arith import __LCM_sequence
        sage: l = Sequence(())
        sage: __LCM_sequence(l)
        1

    This is because lcm(0,x)=0 for all x (by convention)

    ::

        sage: __LCM_sequence(Sequence(srange(100)))
        0

    So for the lcm of all integers up to 10 you must do this::

        sage: __LCM_sequence(Sequence(srange(1,100)))
        69720375229712477164533808935312303556800

    Note that the following example did not work in QQ[] as of 2.11,
    but does in 3.1.4; the answer is different, though equivalent::

        sage: R.<X>=ZZ[]
        sage: __LCM_sequence(Sequence((2*X+4,2*X^2,2)))
        2*X^3 + 4*X^2
        sage: R.<X>=QQ[]
        sage: __LCM_sequence(Sequence((2*X+4,2*X^2,2)))
        4*X^3 + 8*X^2
    """
    if len(v) == 0:
        return ZZ(1)
    try:
        g = v.universe()(1)
    except AttributeError:
        g = ZZ(1)
    one = v.universe()(1)
    for vi in v:
        g = vi.lcm(g)
        if not g:
            return g
    return g

def xlcm(m,n):
    r"""
    Extended lcm function: given two positive integers `m,n`, returns
    a triple `(l,m_1,n_1)` such that `l=\mathop{\mathrm{lcm}}(m,n)=m_1
    \cdot n_1` where `m_1|m`, `n_1|n` and `\gcd(m_1,n_1)=1`, all with no
    factorization.

    Used to construct an element of order `l` from elements of orders `m,n`
    in any group: see sage/groups/generic.py for examples.

    EXAMPLES::

        sage: xlcm(120,36)
        (360, 40, 9)
    """
    m0=m; n0=n
    g=gcd(m,n)
    l=m*n//g      # = lcm(m,n)
    g=gcd(m,n//g) # divisible by those primes which divide n to a
                  # higher power than m

    while not g==1:
        m//=g
        g=gcd(m,g)

    n=l//m;
    return (l,m,n)

def xgcd(a, b):
    r"""
    Return a triple ``(g,s,t)`` such that `g = s\cdot a+t\cdot b = \gcd(a,b)`.

    .. note::

       One exception is if `a` and `b` are not in a PID, e.g., they are
       both polynomials over the integers, then this function can't in
       general return ``(g,s,t)`` as above, since they need not exist.
       Instead, over the integers, we first multiply `g` by a divisor of
       the resultant of `a/g` and `b/g`, up to sign.

    INPUT:


    -  ``a, b`` - integers or univariate polynomials (or
       any type with an xgcd method).


    OUTPUT:

    -  ``g, s, t`` - such that `g = s\cdot a + t\cdot b`


    .. note::

       There is no guarantee that the returned cofactors (s and t) are
       minimal. In the integer case, see
       :meth:`sage.rings.integer.Integer._xgcd()` for minimal
       cofactors.

    EXAMPLES::

        sage: xgcd(56, 44)
        (4, 4, -5)
        sage: 4*56 + (-5)*44
        4
        sage: g, a, b = xgcd(5/1, 7/1); g, a, b
        (1, 3, -2)
        sage: a*(5/1) + b*(7/1) == g
        True
        sage: x = polygen(QQ)
        sage: xgcd(x^3 - 1, x^2 - 1)
        (x - 1, 1, -x)
        sage: K.<g> = NumberField(x^2-3)
        sage: R.<a,b> = K[]
        sage: S.<y> = R.fraction_field()[]
        sage: xgcd(y^2, a*y+b)
        (1, a^2/b^2, ((-a)/b^2)*y + 1/b)
        sage: xgcd((b+g)*y^2, (a+g)*y+b)
        (1, (a^2 + (2*g)*a + 3)/(b^3 + (g)*b^2), ((-a + (-g))/b^2)*y + 1/b)

    We compute an xgcd over the integers, where the linear combination
    is not the gcd but the resultant::

        sage: R.<x> = ZZ[]
        sage: gcd(2*x*(x-1), x^2)
        x
        sage: xgcd(2*x*(x-1), x^2)
        (2*x, -1, 2)
        sage: (2*(x-1)).resultant(x)
        2
    """
    try:
        return a.xgcd(b)
    except AttributeError:
        pass
    if not isinstance(a, sage.rings.integer.Integer):
        a = ZZ(a)
    return a.xgcd(ZZ(b))

XGCD = xgcd

## def XGCD_python(a, b):
##     """
##     Returns triple (g,p,q) such that g = p*a+b*q = GCD(a,b).
##     This function should behave exactly the same as XGCD,
##     but is implemented in pure python.
##     """
##     if a == 0 and b == 0:
##         return (0,0,1)
##     if a == 0:
##         return (abs(b), 0, b/abs(b))
##     if b == 0:
##         return (abs(a), a/abs(a), 0)
##     psign = 1
##     qsign = 1
##     if a < 0:
##         a = -a
##         psign = -1
##     if b < 0:
##         b = -b
##         qsign = -1
##     p = 1; q = 0; r = 0; s = 1
##     while b != 0:
##         c = a % b
##         quot = a/b
##         a = b; b = c
##         new_r = p - quot*r
##         new_s = q - quot*s
##         p = r; q = s
##         r = new_r; s = new_s
##     return (a, p*psign, q*qsign)

def inverse_mod(a, m):
    """
    The inverse of the ring element a modulo m.

    If no special inverse_mod is defined for the elements, it tries to
    coerce them into integers and perform the inversion there

    ::

        sage: inverse_mod(7,1)
        0
        sage: inverse_mod(5,14)
        3
        sage: inverse_mod(3,-5)
        2
    """
    try:
        return a.inverse_mod(m)
    except AttributeError:
        return integer.Integer(a).inverse_mod(m)

#######################################################
# Functions to find the fastest available commands
# for gcd and inverse_mod
#######################################################

def get_gcd(order):
    """
    Return the fastest gcd function for integers of size no larger than
    order.

    EXAMPLES::

        sage: sage.rings.arith.get_gcd(4000)
        <built-in method gcd_int of sage.rings.fast_arith.arith_int object at ...>
        sage: sage.rings.arith.get_gcd(400000)
        <built-in method gcd_longlong of sage.rings.fast_arith.arith_llong object at ...>
        sage: sage.rings.arith.get_gcd(4000000000)
        <function gcd at ...>
    """
    if order <= 46340:   # todo: don't hard code
        return fast_arith.arith_int().gcd_int
    elif order <= 2147483647:   # todo: don't hard code
        return fast_arith.arith_llong().gcd_longlong
    else:
        return gcd

def get_inverse_mod(order):
    """
    Return the fastest inverse_mod function for integers of size no
    larger than order.

    EXAMPLES::

        sage: sage.rings.arith.get_inverse_mod(6000)
        <built-in method inverse_mod_int of sage.rings.fast_arith.arith_int object at ...>
        sage: sage.rings.arith.get_inverse_mod(600000)
        <built-in method inverse_mod_longlong of sage.rings.fast_arith.arith_llong object at ...>
        sage: sage.rings.arith.get_inverse_mod(6000000000)
        <function inverse_mod at ...>
    """
    if order <= 46340:   # todo: don't hard code
        return fast_arith.arith_int().inverse_mod_int
    elif order <= 2147483647:   # todo: don't hard code
        return fast_arith.arith_llong().inverse_mod_longlong
    else:
        return inverse_mod

# def sqrt_mod(a, m):
#     """A square root of a modulo m."""

# def xxx_inverse_mod(a, m):
#     """The inverse of a modulo m."""
#     g,s,t = XGCD(a,m)
#     if g != 1:
#         raise "inverse_mod(a=%s,m=%s), error since GCD=%s"%(a,m,g)
#     return s

def power_mod(a,n,m):
    """
    The n-th power of a modulo the integer m.

    EXAMPLES::

        sage: power_mod(0,0,5)
        Traceback (most recent call last):
        ...
        ArithmeticError: 0^0 is undefined.
        sage: power_mod(2,390,391)
        285
        sage: power_mod(2,-1,7)
        4
        sage: power_mod(11,1,7)
        4
        sage: R.<x> = ZZ[]
        sage: power_mod(3*x, 10, 7)
        4*x^10

        sage: power_mod(11,1,0)
        Traceback (most recent call last):
        ...
        ZeroDivisionError: modulus must be nonzero.
    """
    if m==0:
        raise ZeroDivisionError, "modulus must be nonzero."
    if m==1:
        return 0
    if n < 0:
        ainv = inverse_mod(a,m)
        return power_mod(ainv, -n, m)
    if n==0:
        if a == 0:
            raise ArithmeticError, "0^0 is undefined."
        return 1

    apow = a % m
    while n&1 == 0:
        apow = (apow*apow) % m
        n = n >> 1
    power = apow
    n = n >> 1
    while n != 0:
        apow = (apow*apow) % m
        if n&1 != 0:
            power = (power*apow) % m
        n = n >> 1

    return power


def rational_reconstruction(a, m, algorithm='fast'):
    r"""
    This function tries to compute `x/y`, where `x/y` is a rational number in
    lowest terms such that the reduction of `x/y` modulo `m` is equal to `a` and
    the absolute values of `x` and `y` are both `\le \sqrt{m/2}`. If such `x/y`
    exists, that pair is unique and this function returns it. If no
    such pair exists, this function raises ZeroDivisionError.

    An efficient algorithm for computing rational reconstruction is
    very similar to the extended Euclidean algorithm. For more details,
    see Knuth, Vol 2, 3rd ed, pages 656-657.

    INPUT:

    - ``a`` - an integer

    - ``m`` - a modulus

    - ``algorithm`` - (default: 'fast')

      - ``'fast'`` - a fast compiled implementation

      - ``'python'`` - a slow pure python implementation

    OUTPUT:

    Numerator and denominator `n`, `d` of the unique rational number
    `r=n/d`, if it exists, with `n` and `|d| \le \sqrt{N/2}`. Return
    `(0,0)` if no such number exists.

    The algorithm for rational reconstruction is described (with a
    complete nontrivial proof) on pages 656-657 of Knuth, Vol 2, 3rd
    ed. as the solution to exercise 51 on page 379. See in particular
    the conclusion paragraph right in the middle of page 657, which
    describes the algorithm thus:

        This discussion proves that the problem can be solved
        efficiently by applying Algorithm 4.5.2X with `u=m` and `v=a`,
        but with the following replacement for step X2: If
        `v3 \le \sqrt{m/2}`, the algorithm terminates. The pair
        `(x,y)=(|v2|,v3*\mathrm{sign}(v2))` is then the unique
        solution, provided that `x` and `y` are coprime and
        `x \le \sqrt{m/2}`; otherwise there is no solution. (Alg 4.5.2X is
        the extended Euclidean algorithm.)

    Knuth remarks that this algorithm is due to Wang, Kornerup, and
    Gregory from around 1983.

    EXAMPLES::

        sage: m = 100000
        sage: (119*inverse_mod(53,m))%m
        11323
        sage: rational_reconstruction(11323,m)
        119/53

    ::

        sage: rational_reconstruction(400,1000)
        Traceback (most recent call last):
        ...
        ValueError: Rational reconstruction of 400 (mod 1000) does not exist.

    ::

        sage: rational_reconstruction(3,292393, algorithm='python')
        3
        sage: a = Integers(292393)(45/97); a
        204977
        sage: rational_reconstruction(a,292393, algorithm='python')
        45/97
        sage: a = Integers(292393)(45/97); a
        204977
        sage: rational_reconstruction(a,292393, algorithm='fast')
        45/97
        sage: rational_reconstruction(293048,292393, algorithm='fast')
        Traceback (most recent call last):
        ...
        ValueError: Rational reconstruction of 655 (mod 292393) does not exist.
        sage: rational_reconstruction(293048,292393, algorithm='python')
        Traceback (most recent call last):
        ...
        ValueError: Rational reconstruction of 655 (mod 292393) does not exist.
    """
    if algorithm == 'fast':
        return ZZ(a).rational_reconstruction(m)
    elif algorithm == 'python':
        return _rational_reconstruction_python(a,m)
    else:
        raise ValueError, "unknown algorithm"

def _rational_reconstruction_python(a,m):
    """
    Internal fallback function for rational_reconstruction; see
    documentation of that function for details.

    INPUT:

    - ``a`` - an integer

    - ``m`` - a modulus

    EXAMPLES::

        sage: from sage.rings.arith import _rational_reconstruction_python
        sage: _rational_reconstruction_python(20,31)
        -2/3
        sage: _rational_reconstruction_python(11323,100000)
        119/53
    """
    a = int(a); m = int(m)
    a %= m
    if a == 0 or m==0:
        return ZZ(0)/ZZ(1)
    if m < 0:
        m = -m
    if a < 0:
        a = m-a
    if a == 1:
        return ZZ(1)/ZZ(1)
    u = m
    v = a
    bnd = math.sqrt(m/2)
    U = (1,0,u)
    V = (0,1,v)
    while abs(V[2]) > bnd:
        q = U[2]/V[2]  # floor is implicit
        T = (U[0]-q*V[0], U[1]-q*V[1], U[2]-q*V[2])
        U = V
        V = T
    x = abs(V[1])
    y = V[2]
    if V[1] < 0:
        y *= -1
    if x <= bnd and GCD(x,y) == 1:
        return ZZ(y) / ZZ(x)
    raise ValueError, "Rational reconstruction of %s (mod %s) does not exist."%(a,m)

def mqrr_rational_reconstruction(u, m, T):
    r"""
    Maximal Quotient Rational Reconstruction.

    For research purposes only - this is pure Python, so slow.

    INPUT:

    - ``u, m, T`` -  integers such that `m > u \ge 0`, `T > 0`.

    OUTPUT:

    Either integers `n,d` such that `d>0`, `\mathop{\mathrm{gcd}}(n,d)=1`, `n/d=u \bmod m`, and
    `T \cdot d \cdot |n| < m`, or ``None``.

    Reference: Monagan, Maximal Quotient Rational Reconstruction: An
    Almost Optimal Algorithm for Rational Reconstruction (page 11)

    This algorithm is probabilistic.

    EXAMPLES::

        sage: mqrr_rational_reconstruction(21,3100,13)
        (21, 1)
    """
    if u == 0:
        if m > T:
            return (0,1)
        else:
            return None
    n, d = 0, 0
    t0, r0 = 0, m
    t1, r1 = 1, u
    while r1 != 0 and r0 > T:
        q = r0/r1   # C division implicit floor
        if q > T:
            n, d, T = r1, t1, q
        r0, r1 = r1, r0 - q*r1
        t0, t1 = t1, t0 - q*t1
    if d != 0 and GCD(n,d) == 1:
        return (n,d)
    return None


######################


def trial_division(n, bound=None):
    """
    Return the smallest prime divisor <= bound of the positive integer
    n, or n if there is no such prime. If the optional argument bound
    is omitted, then bound <= n.

    INPUT:

    -  ``n`` - a positive integer

    - ``bound`` - (optional) a positive integer

    OUTPUT:

    -  ``int`` - a prime p=bound that divides n, or n if
       there is no such prime.


    EXAMPLES::

        sage: trial_division(15)
        3
        sage: trial_division(91)
        7
        sage: trial_division(11)
        11
        sage: trial_division(387833, 300)
        387833
        sage: # 300 is not big enough to split off a
        sage: # factor, but 400 is.
        sage: trial_division(387833, 400)
        389
    """
    if n == 1: return 1
    for p in [2, 3, 5]:
        if n%p == 0: return p
    if bound == None: bound = n
    dif = [6, 4, 2, 4, 2, 4, 6, 2]
    m = 7; i = 1
    while m <= bound and m*m <= n:
        if n%m == 0:
            return m
        m += dif[i%8]
        i += 1
    return n

def __factor_using_trial_division(n):
    """
    Returns the factorization of the integer n as a sorted list of
    tuples (p,e).

    INPUT:


    -  ``n`` - an integer


    OUTPUT:


    -  ``list`` - factorization of n

    EXAMPLES::

        sage: from sage.rings.arith import __factor_using_trial_division
        sage: __factor_using_trial_division(100)
        [(2, 2), (5, 2)]
    """
    if n in [-1, 0, 1]: return []
    if n < 0: n = -n
    F = []
    while n != 1:
        p = trial_division(n)
        e = 1
        n /= p
        while n%p == 0:
            e += 1; n /= p
        F.append((p,e))
    F.sort()
    return F

def __factor_using_pari(n, int_=False, debug_level=0, proof=None):
    """
    Factors an integer using pari.

    INPUT:

    -  ``n`` - an integer

    EXAMPLES::

        sage: from sage.rings.arith import __factor_using_pari
        sage: __factor_using_pari(100)
        [(2, 2), (5, 2)]
        sage: __factor_using_pari(720)
        [(2, 4), (3, 2), (5, 1)]
    """
    if proof is None:
        from sage.structure.proof.proof import get_flag
        proof = get_flag(proof, "arithmetic")
    if int_:
        Z = int
    else:
        Z = ZZ
    prev = pari.get_debug_level()

    if prev != debug_level:
        pari.set_debug_level(debug_level)

    F = pari(n).factor(proof=proof)
    B = F[0]
    e = F[1]
    v = [(Z(B[i]),Z(e[i])) for i in xrange(len(B))]

    if prev != debug_level:
        pari.set_debug_level(prev)

    return v


#todo: add a limit option to factor, so it will only split off
# primes at most a given limit.

def factor(n, proof=None, int_=False, algorithm='pari', verbose=0, **kwds):
    """
    Returns the factorization of n. The result depends on the type of
    n.

    If n is an integer, factor returns the factorization of the
    integer n as an object of type Factorization.

    If n is not an integer, ``n.factor(proof=proof, **kwds)`` gets called.
    See ``n.factor??`` for more documentation in this case.

    .. warning::

       This means that applying factor to an integer result of
       a symbolic computation will not factor the integer, because it is
       considered as an element of a larger symbolic ring.

       EXAMPLE::

           sage: f(n)=n^2
           sage: is_prime(f(3))
           False
           sage: factor(f(3))
           9

    INPUT:

    -  ``n`` - an nonzero integer

    -  ``proof`` - bool or None (default: None)

    -  ``int_`` - bool (default: False) whether to return
       answers as Python ints

    -  ``algorithm`` - string

       - ``'pari'`` - (default) use the PARI c library

       - ``'kash'`` - use KASH computer algebra system (requires the
         optional kash package be installed)

       - ``'magma'`` - use Magma (requires magma be installed)

    -  ``verbose`` - integer (default 0); pari's debug
       variable is set to this; e.g., set to 4 or 8 to see lots of output
       during factorization.


    OUTPUT: factorization of n

    The qsieve and ecm commands give access to highly optimized
    implementations of algorithms for doing certain integer
    factorization problems. These implementations are not used by the
    generic factor command, which currently just calls PARI (note that
    PARI also implements sieve and ecm algorithms, but they aren't as
    optimized). Thus you might consider using them instead for certain
    numbers.

    The factorization returned is an element of the class
    :class:`~sage.structure.factorization.Factorization`; see Factorization??
    for more details, and examples below for usage. A Factorization contains
    both the unit factor (+1 or -1) and a sorted list of (prime, exponent)
    pairs.

    The factorization displays in pretty-print format but it is easy to
    obtain access to the (prime,exponent) pairs and the unit, to
    recover the number from its factorization, and even to multiply two
    factorizations. See examples below.

    EXAMPLES::

        sage: factor(500)
        2^2 * 5^3
        sage: factor(-20)
        -1 * 2^2 * 5
        sage: f=factor(-20)
        sage: list(f)
        [(2, 2), (5, 1)]
        sage: f.unit()
        -1
        sage: f.value()
        -20

    ::

        sage: factor(-500, algorithm='kash')      # optional - kash
        -1 * 2^2 * 5^3

    ::

        sage: factor(-500, algorithm='magma')     # optional - magma
        -1 * 2^2 * 5^3

    ::

        sage: factor(0)
        Traceback (most recent call last):
        ...
        ArithmeticError: Prime factorization of 0 not defined.
        sage: factor(1)
        1
        sage: factor(-1)
        -1
        sage: factor(2^(2^7)+1)
        59649589127497217 * 5704689200685129054721

    Sage calls PARI's factor, which has proof False by default. Sage
    has a global proof flag, set to True by default (see
    :mod:`sage.structure.proof.proof`, or proof.[tab]). To override the default,
    call this function with proof=False.

    ::

        sage: factor(3^89-1, proof=False)
        2 * 179 * 1611479891519807 * 5042939439565996049162197

    ::

        sage: factor(2^197 + 1)       # takes a long time (e.g., 3 seconds!)
        3 * 197002597249 * 1348959352853811313 * 251951573867253012259144010843

    To access the data in a factorization::

        sage: f = factor(420); f
        2^2 * 3 * 5 * 7
        sage: [x for x in f]
        [(2, 2), (3, 1), (5, 1), (7, 1)]
        sage: [p for p,e in f]
        [2, 3, 5, 7]
        sage: [e for p,e in f]
        [2, 1, 1, 1]
        sage: [p^e for p,e in f]
        [4, 3, 5, 7]
    """
    if not isinstance(n, (int,long, integer.Integer)):
        # this happens for example if n = x**2 + y**2 + 2*x*y
        try:
            return n.factor(proof=proof, **kwds)
        except AttributeError:
            raise TypeError, "unable to factor n"
        except TypeError:  # just in case factor method doesn't have a proof option.
            try:
                return n.factor(**kwds)
            except AttributeError:
                raise TypeError, "unable to factor n"
    #n = abs(n)
    n = ZZ(n)
    if n < 0:
        unit = ZZ(-1)
        n = -n
    else:
        unit = ZZ(1)

    if n == 0:
        raise ArithmeticError, "Prime factorization of 0 not defined."
    if n == 1:
        return factorization.Factorization([], unit)
    #if n < 10000000000: return __factor_using_trial_division(n)
    if algorithm == 'pari':
        return factorization.Factorization(__factor_using_pari(n,
                                   int_=int_, debug_level=verbose, proof=proof), unit)
    elif algorithm in ['kash', 'magma']:
        if algorithm == 'kash':
            from sage.interfaces.all import kash as I
        else:
            from sage.interfaces.all import magma as I
        F = I.eval('Factorization(%s)'%n)
        i = F.rfind(']') + 1
        F = F[:i]
        F = F.replace("<","(").replace(">",")")
        F = eval(F)
        if not int_:
            F = [(ZZ(a), ZZ(b)) for a,b in F]
        return factorization.Factorization(F, unit)
    else:
        raise ValueError, "Algorithm is not known"


def prime_divisors(n):
    """
    The prime divisors of the integer n, sorted in increasing order. If
    n is negative, we do *not* include -1 among the prime divisors,
    since -1 is not a prime number.

    EXAMPLES::

        sage: prime_divisors(1)
        []
        sage: prime_divisors(100)
        [2, 5]
        sage: prime_divisors(-100)
        [2, 5]
        sage: prime_divisors(2004)
        [2, 3, 167]
    """
    return [p for p,_ in factor(n) if p != -1]

prime_factors = prime_divisors

def odd_part(n):
    r"""
    The odd part of the integer `n`. This is `n / 2^v`,
    where `v = \mathrm{valuation}(n,2)`.

    EXAMPLES::

        sage: odd_part(5)
        5
        sage: odd_part(4)
        1
        sage: odd_part(factorial(31))
        122529844256906551386796875
    """
    n = ZZ(n)
    return n._shift_helper(n.valuation(2), -1)

def prime_to_m_part(n,m):
    """
    Returns the prime-to-m part of n, i.e., the largest divisor of n
    that is coprime to m.

    INPUT:


    -  ``n`` - Integer (nonzero)

    -  ``m`` - Integer


    OUTPUT: Integer

    EXAMPLES::

        sage: z = 43434
        sage: z.prime_to_m_part(20)
        21717
    """
    if n == 0:
        raise ValueError, "n must be nonzero."
    if m == 0:
        return ZZ(1)
    n = ZZ(n)
    m = ZZ(m)
    while True:
        g = gcd(n,m)
        if g == 1:
            return n
        n = n // g


def is_square(n, root=False):
    """
    Returns whether or not n is square, and if n is a square also
    returns the square root. If n is not square, also returns None.

    INPUT:


    -  ``n`` - an integer

    -  ``root`` - whether or not to also return a square
       root (default: False)


    OUTPUT:


    -  ``bool`` - whether or not a square

    -  ``object`` - (optional) an actual square if found,
       and None otherwise.


    EXAMPLES::

        sage: is_square(2)
        False
        sage: is_square(4)
        True
        sage: is_square(2.2)
        True
        sage: is_square(-2.2)
        False
        sage: is_square(CDF(-2.2))
        True
        sage: is_square((x-1)^2)
        True

    ::

        sage: is_square(4, True)
        (True, 2)
    """
    try:
        if root:
            try:
                return n.is_square(root)
            except TypeError:
                if n.is_square():
                    return True, n.sqrt()
                else:
                    return False, None
        return n.is_square()
    except AttributeError:
        pass
    t, x = pari(n).issquare(find_root=True)
    if root:
        if t:
            if hasattr(n, 'parent'):
                x = n.parent()(str(x))
            else:
                x = x.python()
        return t, x
    return t


def is_squarefree(n):
    """
    Returns True if and only if n is not divisible by the square of an
    integer > 1.

    EXAMPLES::

        sage: is_squarefree(100)
        False
        sage: is_squarefree(101)
        True
    """
    if n==0:
        return False
    for p, r in factor(n):
        if r>1:
            return False
    return True


#################################################################
# Euler phi function
#################################################################
class Euler_Phi:
    r"""
    Return the value of the Euler phi function on the integer n. We
    defined this to be the number of positive integers <= n that are
    relatively prime to n. Thus if n<=0 then
    ``euler_phi(n)`` is defined and equals 0.

    INPUT:


    -  ``n`` - an integer


    EXAMPLES::

        sage: euler_phi(1)
        1
        sage: euler_phi(2)
        1
        sage: euler_phi(3)
        2
        sage: euler_phi(12)
        4
        sage: euler_phi(37)
        36

    Notice that euler_phi is defined to be 0 on negative numbers and
    0.

    ::

        sage: euler_phi(-1)
        0
        sage: euler_phi(0)
        0
        sage: type(euler_phi(0))
        <type 'sage.rings.integer.Integer'>

    We verify directly that the phi function is correct for 21.

    ::

        sage: euler_phi(21)
        12
        sage: [i for i in range(21) if gcd(21,i) == 1]
        [1, 2, 4, 5, 8, 10, 11, 13, 16, 17, 19, 20]

    The length of the list of integers 'i' in range(n) such that the
    gcd(i,n) == 1 equals euler_phi(n).

    ::

        sage: len([i for i in range(21) if gcd(21,i) == 1]) == euler_phi(21)
        True

    The phi function also has a special plotting method.

    ::

        sage: P = plot(euler_phi, -3, 71)

    AUTHORS:

    - William Stein

    - Alex Clemesha (2006-01-10): some examples
    """
    def __repr__(self):
        """
        Returns a string describing this class.

        EXAMPLES::

            sage: Euler_Phi().__repr__()
            'Number of positive integers <=n but relatively prime to n'
        """
        return "Number of positive integers <=n but relatively prime to n"

    def __call__(self, n):
        """
        Calls the euler_phi function.

        EXAMPLES::

            sage: Euler_Phi()(10)
            4
            sage: Euler_Phi()(720)
            192
        """
        if n<=0:
            return ZZ(0)
        if n<=2:
            return ZZ(1)
        return ZZ(pari(n).phi())
        #return misc.mul([(p-1)*p**(r-1) for p, r in factor(n)])

    def plot(self, xmin=1, xmax=50, pointsize=30, rgbcolor=(0,0,1), join=True,
             **kwds):
        """
        Plot the Euler phi function.

        INPUT:


        -  ``xmin`` - default: 1

        -  ``xmax`` - default: 50

        -  ``pointsize`` - default: 30

        -  ``rgbcolor`` - default: (0,0,1)

        -  ``join`` - default: True; whether to join the
           points.

        -  ``**kwds`` - passed on

        EXAMPLES::

            sage: p = Euler_Phi().plot()
            sage: p.ymax()
            46.0
        """
        v = [(n,euler_phi(n)) for n in range(xmin,xmax + 1)]
        from sage.plot.all import list_plot
        P = list_plot(v, pointsize=pointsize, rgbcolor=rgbcolor, **kwds)
        if join:
            P += list_plot(v, plotjoined=True, rgbcolor=(0.7,0.7,0.7), **kwds)
        return P

euler_phi = Euler_Phi()

def crt(a,b,m=None,n=None):
    r"""
    Use the Chinese Remainder Theorem to find some `x` such that
    `x=a \bmod m` and `x=b \bmod n`. Note that `x` is only well-defined
    modulo `m*n`.

    EXAMPLES::

        sage: crt(2, 1, 3, 5)
        -4
        sage: crt(13,20,100,301)
        -2087

    You can also use upper case::

        sage: c = CRT(2,3, 3, 5); c
        8
        sage: c % 3 == 2
        True
        sage: c % 5 == 3
        True

    Note that this also works for polynomial rings::

        sage: K.<a> = NumberField(x^3 - 7)
        sage: R.<y> = K[]
        sage: f = y^2 + 3
        sage: g = y^3 - 5
        sage: CRT(1,3,f,g)
        -3/26*y^4 + 5/26*y^3 + 15/26*y + 53/26
        sage: CRT(1,a,f,g)
        (-3/52*a + 3/52)*y^4 + (5/52*a - 5/52)*y^3 + (15/52*a - 15/52)*y + 27/52*a + 25/52

    You can also do this for any number of moduli::

        sage: K.<a> = NumberField(x^3 - 7)
        sage: R.<x> = K[]
        sage: CRT([], [])
        0
        sage: CRT([a], [x])
        a
        sage: f = x^2 + 3
        sage: g = x^3 - 5
        sage: h = x^5 + x^2 - 9
        sage: k = CRT([1, a, 3], [f, g, h]); k
        (127/26988*a - 5807/386828)*x^9 + (45/8996*a - 33677/1160484)*x^8 + (2/173*a - 6/173)*x^7 + (133/6747*a - 5373/96707)*x^6 + (-6/2249*a + 18584/290121)*x^5 + (-277/8996*a + 38847/386828)*x^4 + (-135/4498*a + 42673/193414)*x^3 + (-1005/8996*a + 470245/1160484)*x^2 + (-1215/8996*a + 141165/386828)*x + 621/8996*a + 836445/386828
        sage: k.mod(f)
        1
        sage: k.mod(g)
        a
        sage: k.mod(h)
        3


    """
    if isinstance(a,list):
        return CRT_list(a,b)
    g, alpha, beta = XGCD(m,n)
    if g != 1:
        raise ValueError, "arguments a and b must be coprime"
    return a+(b-a)*alpha*m

CRT = crt

def CRT_list(v, moduli):
    r""" Given a list ``v`` of elements and a list of corresponding
    ``moduli``, find a single element that reduces to each element of
    ``v`` modulo the corresponding moduli.

    EXAMPLES::

        sage: CRT_list([2,3,2], [3,5,7])
        23
        sage: x = polygen(QQ)
        sage: c = CRT_list([3], [x]); c
        3
        sage: c.parent()
        Univariate Polynomial Ring in x over Rational Field

    The arguments must be lists::

        sage: CRT_list([1,2,3],"not a list")
        Traceback (most recent call last):
        ...
        ValueError: Arguments to CRT_list should be lists
        sage: CRT_list("not a list",[2,3])
        Traceback (most recent call last):
        ...
        ValueError: Arguments to CRT_list should be lists

    The list of moduli must have the same length as the list of elements::

        sage: CRT_list([1,2,3],[2,3,5])
        23
        sage: CRT_list([1,2,3],[2,3])
        Traceback (most recent call last):
        ...
        ValueError: Arguments to CRT_list should be lists of the same length
        sage: CRT_list([1,2,3],[2,3,5,7])
        Traceback (most recent call last):
        ...
        ValueError: Arguments to CRT_list should be lists of the same length


    """
    if not isinstance(v,list) or not isinstance(moduli,list):
        raise ValueError, "Arguments to CRT_list should be lists"
    if len(v) != len(moduli):
        raise ValueError, "Arguments to CRT_list should be lists of the same length"
    if len(v) == 0:
        return ZZ(0)
    if len(v) == 1:
        return moduli[0].parent()(v[0])
    x = v[0]
    m = moduli[0]
    for i in range(1,len(v)):
        x = CRT(x,v[i],m,moduli[i])
        m *= moduli[i]
    return x%m

def CRT_basis(moduli):
    r"""
    Returns a CRT basis for the given moduli.

    INPUT:

    - ``moduli`` - list of pairwise coprime moduli `m` which admit an
       extended Euclidean algorithm

    OUTPUT:

    - a list of elements `a_i` of the same length as `m` such that
      `a_i` is congruent to 1 modulo `m_i` and to 0 modulo `m_j` for
      `j\not=i`.

    .. note::

       The pairwise coprimality of the input is not checked.

    EXAMPLES::

        sage: a1 = ZZ(mod(42,5))
        sage: a2 = ZZ(mod(42,13))
        sage: c1,c2 = CRT_basis([5,13])
        sage: mod(a1*c1+a2*c2,5*13)
        42

    A polynomial example::

        sage: x=polygen(QQ)
        sage: mods = [x,x^2+1,2*x-3]
        sage: b = CRT_basis(mods)
        sage: b
        [-2/3*x^3 + x^2 - 2/3*x + 1, 6/13*x^3 - x^2 + 6/13*x, 8/39*x^3 + 8/39*x]
        sage: [[bi % mj for mj in mods] for bi in b]
        [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    """
    n = len(moduli)
    if n == 0:
        return []
    M = prod(moduli)
    return [((xgcd(m,M//m)[2])*(M//m))%M for m in moduli]

def CRT_vectors(X, moduli):
    r"""
    Vector form of the Chinese Remainder Theorem: given a list of integer
    vectors `v_i` and a list of coprime moduli `m_i`, find a vector `w` such
    that `w = v_i \pmod m_i` for all `i`. This is more efficient than applying
    :func:`CRT` to each entry.

    INPUT:

    -  ``X`` - list or tuple, consisting of lists/tuples/vectors/etc of
       integers of the same length
    -  ``moduli`` - list of len(X) moduli

    OUTPUT:

    -  ``list`` - application of CRT componentwise.

    EXAMPLES::

        sage: CRT_vectors([[3,5,7],[3,5,11]], [2,3])
        [3, 5, 5]

        sage: CRT_vectors([vector(ZZ, [2,3,1]), Sequence([1,7,8],ZZ)], [8,9])
        [10, 43, 17]
    """
    # First find the CRT basis:
    if len(X) == 0 or len(X[0]) == 0:
        return []
    n = len(X)
    if n != len(moduli):
        raise ValueError, "number of moduli must equal length of X"
    a = CRT_basis(moduli)
    modulus = misc.prod(moduli)
    return [sum([a[i]*X[i][j] for i in range(n)]) % modulus for j in range(len(X[0]))]

def binomial(x,m):
    r"""
    Return the binomial coefficient

    .. math::

                \binom{x}{m} = x (x-1) \cdots (x-m+1) / m!


    which is defined for `m \in \ZZ` and any
    `x`. We extend this definition to include cases when
    `x-m` is an integer but `m` is not by

    .. math::

        \binom{x}{m}= \binom{x}{x-m}

    If `m < 0`, return `0`.

    INPUT:

    -  ``x``, ``m`` - numbers or symbolic expressions. Either ``m``
       or ``x-m`` must be an integer.

    OUTPUT: number or symbolic expression (if input is symbolic)

    EXAMPLES::

        sage: binomial(5,2)
        10
        sage: binomial(2,0)
        1
        sage: binomial(1/2, 0)
        1
        sage: binomial(3,-1)
        0
        sage: binomial(20,10)
        184756
        sage: binomial(-2, 5)
        -6
        sage: binomial(RealField()('2.5'), 2)
        1.87500000000000
        sage: n=var('n'); binomial(n,2)
        1/2*(n - 1)*n
        sage: n=var('n'); binomial(n,n)
        1
        sage: n=var('n'); binomial(n,n-1)
        n
        sage: binomial(2^100, 2^100)
        1

        sage: k, i = var('k,i')
        sage: binomial(k,i)
        binomial(k, i)

    TESTS:

    We test that certain binomials are very fast (this should be
    instant) -- see trac 3309::

        sage: a = binomial(RR(1140000.78), 42000000)

    We test conversion of arguments to Integers -- see trac 6870::

        sage: binomial(1/2,1/1)
        1/2
        sage: binomial(10^20+1/1,10^20)
        100000000000000000001
        sage: binomial(SR(10**7),10**7)
        1
        sage: binomial(3/2,SR(1/1))
        3/2

    Some floating point cases -- see trac 7562::

        sage: binomial(1.,3)
        0.000000000000000
        sage: binomial(-2.,3)
        -4.00000000000000
    """
    if isinstance(m,sage.symbolic.expression.Expression):
        try:
            # For performance reasons, we avoid to try to coerce
            # to Integer in the symbolic case (see #6870)
            m=m.pyobject()
            m=ZZ(m)
        except TypeError:
            pass
    else:
        try:
            m=ZZ(m)
        except TypeError:
            pass
    if not isinstance(m,integer.Integer):
        try:
            m = ZZ(x-m)
        except TypeError:
            try:
                return x.binomial(m)
            except AttributeError:
                pass
            raise TypeError, 'Either m or x-m must be an integer'
    # a (hopefully) temporary fix for #3309; eventually Pari should do
    # this for us.
    if isinstance(x, (float, sage.rings.real_mpfr.RealNumber,
                      sage.rings.real_mpfr.RealLiteral)):
        P = x.parent()
        if m < 0:
            return P(0)
        from sage.functions.all import gamma
        if x > -1/2:
            a = gamma(x-m+1)
            if a:
                return gamma(x+1)/gamma(P(m+1))/a
            else:
                return P(0)
        else:
            return (-1)**m*gamma(m-x)/gamma(P(m+1))/gamma(-x)
    if isinstance(x,sage.symbolic.expression.Expression):
        try:
            x=x.pyobject()
            x=ZZ(x)
        except TypeError:
            pass
    else:
        try:
            x=ZZ(x)
        except TypeError:
            pass
    if isinstance(x,integer.Integer):
        if x >= 0 and (m < 0 or m > x):
            return ZZ(0)

        if m > sys.maxint:
            m = x - m
            if m > sys.maxint:
                raise ValueError, "binomial not implemented for m >= 2^32.\nThis is probably OK, since the answer would have billions of digits."

        return ZZ(pari(x).binomial(m))
    try:
        P = x.parent()
    except AttributeError:
        P = type(x)
    if m < 0:
        return P(0)
    return misc.prod([x-i for i in xrange(m)]) / P(factorial(m))

def multinomial(*ks):
    r"""
    Return the multinomial coefficient

    INPUT:

    - An arbitrary number of integer arguments `k_1,\dots,k_n`
    - A list of integers `[k_1,\dots,k_n]`

    OUTPUT:

    Returns the integer:

    .. math::

           \binom{k_1 + \cdots + k_n}{k_1, \cdots, k_n}
           =\frac{\left(\sum_{i=1}^n k_i\right)!}{\prod_{i=1}^n k_i!}
           = \prod_{i=1}^n \binom{\sum_{j=1}^i k_j}{k_i}

    EXAMPLES::

        sage: multinomial(0, 0, 2, 1, 0, 0)
        3
        sage: multinomial([0, 0, 2, 1, 0, 0])
        3
        sage: multinomial(3, 2)
        10
        sage: multinomial(2^30, 2, 1)
        618970023101454657175683075
        sage: multinomial([2^30, 2, 1])
        618970023101454657175683075

    AUTHORS:

    - Gabriel Ebner
    """
    if isinstance(ks[0],list):
        if len(ks) >1:
            raise ValueError, "multinomial takes only one list argument"
        ks=ks[0]

    s, c = 0, 1
    for k in ks:
        s += k
        c *= binomial(s, k)
    return c

def binomial_coefficients(n):
    r"""
    Return a dictionary containing pairs
    `\{(k_1,k_2) : C_{k,n}\}` where `C_{k_n}` are
    binomial coefficients and `n = k_1 + k_2`.

    INPUT:


    -  ``n`` - an integer


    OUTPUT: dict

    EXAMPLES::

        sage: sorted(binomial_coefficients(3).items())
        [((0, 3), 1), ((1, 2), 3), ((2, 1), 3), ((3, 0), 1)]

    Notice the coefficients above are the same as below::

        sage: R.<x,y> = QQ[]
        sage: (x+y)^3
        x^3 + 3*x^2*y + 3*x*y^2 + y^3

    AUTHORS:

    - Fredrik Johansson
    """
    d = {(0, n):1, (n, 0):1}
    a = 1
    for k in xrange(1, n//2+1):
        a = (a * (n-k+1))//k
        d[k, n-k] = d[n-k, k] = a
    return d

def multinomial_coefficients(m, n, _tuple=tuple, _zip=zip):
    r"""
    Return a dictionary containing pairs
    `\{(k_1,k_2,...,k_m) : C_{k,n}\}` where
    `C_{k,n}` are multinomial coefficients such that
    `n = k_1 + k_2 + ...+ k_m`.

    INPUT:


    -  ``m`` - integer

    -  ``n`` - integer

    -  ``_tuple, _zip`` - hacks for speed; don't set
       these as a user.


    OUTPUT: dict

    EXAMPLES::

        sage: sorted(multinomial_coefficients(2,5).items())
        [((0, 5), 1), ((1, 4), 5), ((2, 3), 10), ((3, 2), 10), ((4, 1), 5), ((5, 0), 1)]

    Notice that these are the coefficients of `(x+y)^5`::

        sage: R.<x,y> = QQ[]
        sage: (x+y)^5
        x^5 + 5*x^4*y + 10*x^3*y^2 + 10*x^2*y^3 + 5*x*y^4 + y^5

    ::

        sage: sorted(multinomial_coefficients(3,2).items())
        [((0, 0, 2), 1), ((0, 1, 1), 2), ((0, 2, 0), 1), ((1, 0, 1), 2), ((1, 1, 0), 2), ((2, 0, 0), 1)]

    ALGORITHM: The algorithm we implement for computing the multinomial
    coefficients is based on the following result:

    Consider a polynomial and its `n`-th exponent:


    .. math::

         P(x) = \sum_{i=0}^m p_i x^k




    .. math::

         P(x)^n = \sum_{k=0}^{m n} a(n,k) x^k



    We compute the coefficients `a(n,k)` using the J.C.P.
    Miller Pure Recurrence [see D.E.Knuth, Seminumerical Algorithms,
    The art of Computer Programming v.2, Addison Wesley, Reading,
    1981].

    .. math::

                  a(n,k) = 1/(k p_0) \sum_{i=1}^m p_i ((n+1)i-k) a(n,k-i),


    where `a(n,0) = p_0^n`.

    AUTHORS:

    - Pearu Peterson
    """
    if m == 2:
        return binomial_coefficients(n)
    symbols = [(0,)*i + (1,) + (0,)*(m-i-1) for i in range(m)]
    s0 = symbols[0]
    p0 = [_tuple(aa-bb for aa,bb in _zip(s,s0)) for s in symbols]
    r = {_tuple(aa*n for aa in s0):1}
    r_get = r.get
    r_update = r.update
    l = [0] * (n*(m-1)+1)
    l[0] = r.items()
    for k in xrange(1, n*(m-1)+1):
        d = {}
        d_get = d.get
        for i in xrange(1, min(m,k+1)):
            nn = (n+1)*i-k
            if not nn:
                continue
            t = p0[i]
            for t2, c2 in l[k-i]:
                tt = _tuple([aa+bb for aa,bb in _zip(t2,t)])
                cc = nn * c2
                b = d_get(tt)
                if b is None:
                    d[tt] = cc
                else:
                    cc = b + cc
                    if cc:
                        d[tt] = cc
                    else:
                        del d[tt]
        r1 = [(t, c//k) for (t, c) in d.iteritems()]
        l[k] = r1
        r_update(r1)
    return r


def gaussian_binomial(n,k,q=None):
    r"""
    Return the gaussian binomial

    .. math::

       \binom{n}{k}_q = \frac{(1-q^n)(1-q^{n-1})\cdots (1-q^{n-k+1})}{(1-q)(1-q^2)\cdots (1-q^k)}.

    EXAMPLES::

        sage: gaussian_binomial(5,1)
        q^4 + q^3 + q^2 + q + 1
        sage: gaussian_binomial(5,1).subs(q=2)
        31
        sage: gaussian_binomial(5,1,2)
        31

    AUTHORS:

    - David Joyner and William Stein
    """
    if q is None:
        from sage.rings.polynomial.polynomial_ring import polygen
        q = polygen(ZZ, name='q')
    n = misc.prod([1 - q**i for i in range((n-k+1),n+1)])
    d = misc.prod([1 - q**i for i in range(1,k+1)])
    return n/d

def kronecker_symbol(x,y):
    """
    The Kronecker symbol `(x|y)`.

    INPUT:

    -  ``x`` - integer

    -  ``y`` - integer

    EXAMPLES::

        sage: kronecker_symbol(13,21)
        -1
        sage: kronecker_symbol(101,4)
        1

    IMPLEMENTATION: Using GMP.
    """
    x = QQ(x).numerator() * QQ(x).denominator()
    return ZZ(x.kronecker(y))

def kronecker(x,y):
    r"""
    Synonym for :func:`kronecker_symbol`.

    The Kronecker symbol `(x|y)`.

    INPUT:

    -  ``x`` - integer

    -  ``y`` - integer

    OUTPUT:

    - an integer

    EXAMPLES::

        sage: kronecker(3,5)
        -1
        sage: kronecker(3,15)
        0
        sage: kronecker(2,15)
        1
        sage: kronecker(-2,15)
        -1
        sage: kronecker(2/3,5)
        1
    """
    return kronecker_symbol(x,y)

def legendre_symbol(x,p):
    r"""
    The Legendre symbol `(x|p)`, for `p` prime.

    .. note::

       The :func:`kronecker_symbol` command extends the Legendre
       symbol to composite moduli and `p=2`.

    INPUT:


    -  ``x`` - integer

    -  ``p`` - an odd prime number


    EXAMPLES::

        sage: legendre_symbol(2,3)
        -1
        sage: legendre_symbol(1,3)
        1
        sage: legendre_symbol(1,2)
        Traceback (most recent call last):
        ...
        ValueError: p must be odd
        sage: legendre_symbol(2,15)
        Traceback (most recent call last):
        ...
        ValueError: p must be a prime
        sage: kronecker_symbol(2,15)
        1
        sage: legendre_symbol(2/3,7)
        -1
    """
    x = QQ(x).numerator() * QQ(x).denominator()
    p = ZZ(p)
    if not p.is_prime():
        raise ValueError, "p must be a prime"
    if p == 2:
        raise ValueError, "p must be odd"
    return x.kronecker(p)

def primitive_root(n):
    """
    Return a generator for the multiplicative group of integers modulo
    `n`, if one exists.

    EXAMPLES::

        sage: primitive_root(23)
        5
        sage: print [primitive_root(p) for p in primes(100)]
        [1, 2, 2, 3, 2, 2, 3, 2, 5, 2, 3, 2, 6, 3, 5, 2, 2, 2, 2, 7, 5, 3, 2, 3, 5]
    """
    try:
        return ZZ(pari(ZZ(n)).znprimroot())
    except RuntimeError:
        raise ArithmeticError, "There is no primitive root modulo n"

def nth_prime(n):
    """
    EXAMPLES::

        sage: nth_prime(3)
        5
        sage: nth_prime(10)
        29

    ::

        sage: nth_prime(0)
        Traceback (most recent call last):
        ...
        ValueError: nth prime meaningless for non-positive n (=0)
    """
    return ZZ(pari.nth_prime(n))

def quadratic_residues(n):
    r"""
    Return a sorted list of all squares modulo the integer `n`
    in the range `0\leq x < |n|`.

    EXAMPLES::

        sage: quadratic_residues(11)
        [0, 1, 3, 4, 5, 9]
        sage: quadratic_residues(1)
        [0]
        sage: quadratic_residues(2)
        [0, 1]
        sage: quadratic_residues(8)
        [0, 1, 4]
        sage: quadratic_residues(-10)
        [0, 1, 4, 5, 6, 9]
        sage: v = quadratic_residues(1000); len(v);
        159
    """
    n = abs(int(n))
    X = list(set([ZZ((a*a)%n) for a in range(n/2+1)]))
    X.sort()
    return X

## This much slower than above, for obvious reasons.
## def quadratic_residues2(p):
##     return [x for x in range(p-1) if kronecker_symbol(x,p)==1]

class Moebius:
    r"""
    Returns the value of the Moebius function of abs(n), where n is an
    integer.

    DEFINITION: `\mu(n)` is 0 if `n` is not square
    free, and otherwise equals `(-1)^r`, where `n` has
    `r` distinct prime factors.

    For simplicity, if `n=0` we define `\mu(n) = 0`.

    IMPLEMENTATION: Factors or - for integers - uses the PARI C
    library.

    INPUT:


    -  ``n`` - anything that can be factored.


    OUTPUT: 0, 1, or -1

    EXAMPLES::

        sage: moebius(-5)
        -1
        sage: moebius(9)
        0
        sage: moebius(12)
        0
        sage: moebius(-35)
        1
        sage: moebius(-1)
        1
        sage: moebius(7)
        -1

    ::

        sage: moebius(0)   # potentially nonstandard!
        0

    The moebius function even makes sense for non-integer inputs.

    ::

        sage: x = GF(7)['x'].0
        sage: moebius(x+2)
        -1
    """
    def __call__(self, n):
        """
        EXAMPLES::

            sage: Moebius().__call__(7)
            -1
        """
        if isinstance(n, (int, long)):
            n = ZZ(n)
        elif not isinstance(n, integer.Integer):
            # Use a generic algorithm.
            if n < 0:
                n = -n
            F = factor(n)
            for _, e in F:
                if e >= 2:
                    return 0
            return (-1)**len(F)

        # Use fast PARI algorithm
        if n == 0:
            return integer.Integer(0)
        return ZZ(pari(n).moebius())


    def __repr__(self):
        """
        Returns a description of this function.

        EXAMPLES::

            sage: q = Moebius()
            sage: q.__repr__()
            'The Moebius function'
        """
        return "The Moebius function"

    def plot(self, xmin=0, xmax=50, pointsize=30, rgbcolor=(0,0,1), join=True,
             **kwds):
        """
        Plot the Moebius function.

        INPUT:


        -  ``xmin`` - default: 0

        -  ``xmax`` - default: 50

        -  ``pointsize`` - default: 30

        -  ``rgbcolor`` - default: (0,0,1)

        -  ``join`` - default: True; whether to join the points
           (very helpful in seeing their order).

        -  ``**kwds`` - passed on

        EXAMPLES::

            sage: p = Moebius().plot()
            sage: p.ymax()
            1.0
        """
        values = self.range(xmin, xmax + 1)
        v = [(n,values[n-xmin]) for n in range(xmin,xmax + 1)]
        from sage.plot.all import list_plot
        P = list_plot(v, pointsize=pointsize, rgbcolor=rgbcolor, **kwds)
        if join:
            P += list_plot(v, plotjoined=True, rgbcolor=(0.7,0.7,0.7), **kwds)
        return P

    def range(self, start, stop=None, step=None):
        """
        Return the Moebius function evaluated at the given range of values,
        i.e., the image of the list range(start, stop, step) under the
        Mobius function.

        This is much faster than directly computing all these values with a
        list comprehension.

        EXAMPLES::

            sage: v = moebius.range(-10,10); v
            [1, 0, 0, -1, 1, -1, 0, -1, -1, 1, 0, 1, -1, -1, 0, -1, 1, -1, 0, 0]
            sage: v == [moebius(n) for n in range(-10,10)]
            True
            sage: v = moebius.range(-1000, 2000, 4)
            sage: v == [moebius(n) for n in range(-1000,2000, 4)]
            True
        """
        if stop is None:
            start, stop = 1, int(start)
        else:
            start = int(start)
            stop = int(stop)
        if step is None:
            step = 1
        else:
            step = int(step)

        Z = integer.Integer

        if start <= 0 and 0 < stop and start % step == 0:
            return self.range(start, 0, step) + [Z(0)] +\
                   self.range(step, stop, step)

        if step == 1:
            v = pari('vector(%s, i, moebius(i-1+%s))'%(
                stop-start, start))
        else:
            n = len(range(start, stop, step)) # stupid
            v = pari('vector(%s, i, moebius(%s*(i-1) + %s))'%(
                n, step, start))
        w = vecsmall_to_intlist(v.Vecsmall())
        return [Z(x) for x in w]

moebius = Moebius()

def farey(v, lim):
    """
    Return the Farey sequence associated to the floating point number
    v.

    INPUT:


    -  ``v`` - float (automatically converted to a float)

    -  ``lim`` - maximum denominator.


    OUTPUT: Results are (numerator, denominator); (1, 0) is "infinity".

    EXAMPLES::

        sage: farey(2.0, 100)
        (2, 1)
        sage: farey(2.0, 1000)
        (2, 1)
        sage: farey(2.1, 1000)
        (21, 10)
        sage: farey(2.1, 100000)
        (21, 10)
        sage: farey(pi, 100000)
        (312689, 99532)

    AUTHORS:

    - Scott David Daniels: Python Cookbook, 2nd Ed., Recipe 18.13
    """
    v = float(v)
    if v < 0:
        n, d = farey(-v, lim)
        return -n, d
    z = lim - lim    # Get a "0 of the right type" for denominator
    lower, upper = (z, z+1), (z+1, z)
    while True:
        mediant = (lower[0] + upper[0]), (lower[1] + upper[1])
        if v * mediant[1] > mediant[0]:
            if lim < mediant[1]:
                return upper
            lower = mediant
        elif v * mediant[1] == mediant[0]:
            if lim >= mediant[1]:
                return mediant
            if lower[1] < upper[1]:
                return lower
            return upper
        else:
            if lim < mediant[1]:
                return lower
            upper = mediant


## def convergents_pnqn(x):
##     """
##     Return the pairs (pn,qn) that are the numerators and denominators
##     of the partial convergents of the continued fraction of x.  We
##     include (0,1) and (1,0) at the beginning of the list (these are
##     the -2 and -1 th convergents).
##     """
##     v = pari(x).contfrac()
##     w = [(0,1), (1,0)]
##     for n in range(len(v)):
##         pn = w[n+1][0]*v[n] + w[n][0]
##         qn = w[n+1][1]*v[n] + w[n][1]
##         w.append(int(pn), int(qn))
##     return w

def continued_fraction_list(x, partial_convergents=False, bits=None):
    r"""
    Returns the continued fraction of x as a list.

    .. note::

       This may be slow for real number input, since it's implemented in pure
       Python. For rational number input the PARI C library is used.

    EXAMPLES::

        sage: continued_fraction_list(45/17)
        [2, 1, 1, 1, 5]
        sage: continued_fraction_list(e, bits=20)
        [2, 1, 2, 1, 1, 4, 1, 1, 6]
        sage: continued_fraction_list(e, bits=30)
        [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1]
        sage: continued_fraction_list(sqrt(2))
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1]
        sage: continued_fraction_list(sqrt(4/19))
        [0, 2, 5, 1, 1, 2, 1, 16, 1, 2, 1, 1, 5, 4, 5, 1, 1, 2, 1, 15, 2]
        sage: continued_fraction_list(RR(pi), partial_convergents=True)
        ([3, 7, 15, 1, 292, 1, 1, 1, 2, 1, 3, 1, 14, 3],
         [(3, 1),
          (22, 7),
          (333, 106),
          (355, 113),
          (103993, 33102),
          (104348, 33215),
          (208341, 66317),
          (312689, 99532),
          (833719, 265381),
          (1146408, 364913),
          (4272943, 1360120),
          (5419351, 1725033),
          (80143857, 25510582),
          (245850922, 78256779)])
        sage: continued_fraction_list(e)
        [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, 11]
        sage: continued_fraction_list(RR(e))
        [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, 11]
        sage: continued_fraction_list(RealField(200)(e))
        [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, 14, 1, 1, 16, 1, 1, 18, 1, 1, 20, 1, 1, 22, 1, 1, 24, 1, 1, 26, 1, 1, 28, 1, 1, 30, 1, 1, 32, 1, 1, 34, 1, 1, 36, 1, 1, 38, 1, 1]
    """
    from sage.symbolic.expression import Expression

    if bits is not None:
        try:
            x = sage.rings.real_mpfr.RealField(bits)(x)
        except  TypeError:
            raise TypeError, "can only find the continued fraction of a real number"
    elif isinstance(x, float):
        from real_double import RDF
        x = RDF(x)
    elif isinstance(x, Expression):
        # if x is a SymbolicExpression, try coercing it to a real number with 53 bits precision
        try:
            x = sage.rings.real_mpfr.RR(x)
        except TypeError:
            raise TypeError, "can only find the continued fraction of a real number"
    elif not partial_convergents and \
           isinstance(x, (integer.Integer, sage.rings.rational.Rational,
                      int, long)):
        return pari(x).contfrac().python()

    x_in = x
    v = []
    w = [(0,1), (1,0)] # keep track of convergents
    start = x
    i = 0
    try:
        last = None
        while True:
            i += 1
            a = ZZ(int(x.floor()))
            v.append(a)
            n = len(v)-1
            pn = v[n]*w[n+1][0] + w[n][0]
            qn = v[n]*w[n+1][1] + w[n][1]
            w.append((pn, qn))
            x -= a
            s = start - pn/qn
            if abs(s) == 0 or (not last is None  and last == s):
                del w[0]; del w[0]
                if partial_convergents:
                    return v, w
                else:
                    return v
            last = s
            x = 1/x
    except (AttributeError, NotImplementedError, TypeError), msg:
        raise NotImplementedError, "%s\ncomputation of continued fraction of x not implemented; try computing continued fraction of RR(x) instead."%msg

def convergent(v, n):
    r"""
    Return the n-th continued fraction convergent of the continued
    fraction defined by the sequence of integers v. We assume
    `n \geq 0`.

    INPUT:


    -  ``v`` - list of integers

    -  ``n`` - integer


    OUTPUT: a rational number

    If the continued fraction integers are

    .. math::

       v = [a_0, a_1, a_2, \ldots, a_k]


    then ``convergent(v,2)`` is the rational number

    .. math::

       a_0 + 1/a_1

    and ``convergent(v,k)`` is the rational number

    .. math::

       a1 + 1/(a2+1/(...) ... )

    represented by the continued fraction.

    EXAMPLES::

        sage: convergent([2, 1, 2, 1, 1, 4, 1, 1], 7)
        193/71
    """
    if hasattr(v, 'convergent'):
        return v.convergent(n)
    i = int(n)
    x = QQ(v[i])
    i -= 1
    while i >= 0:
        x = QQ(v[i]) + 1/x
        i -= 1
    return x


def convergents(v):
    """
    Return all the partial convergents of a continued fraction defined
    by the sequence of integers v.

    If v is not a list, compute the continued fraction of v and return
    its convergents (this is potentially much faster than calling
    continued_fraction first, since continued fractions are
    implemented using PARI and there is overhead moving the answer back
    from PARI).

    INPUT:


    -  ``v`` - list of integers or a rational number


    OUTPUT:


    -  ``list`` - of partial convergents, as rational
       numbers


    EXAMPLES::

        sage: convergents([2, 1, 2, 1, 1, 4, 1, 1])
        [2, 3, 8/3, 11/4, 19/7, 87/32, 106/39, 193/71]
    """
    if hasattr(v, 'convergents'):
        return v.convergents()
    if not isinstance(v, list):
        v = pari(v).contfrac()
    w = [(0,1), (1,0)]
    for n in range(len(v)):
        pn = w[n+1][0]*v[n] + w[n][0]
        qn = w[n+1][1]*v[n] + w[n][1]
        w.append((pn, qn))
    return [QQ(x) for x in w[2:]]


## def continuant(v, n=None):
##     """
##     Naive implementation with recursion.
##
##     See Graham, Knuth and Patashnik: Concrete Mathematics: 6.7 Continuants
##     """
##     m = len(v)
##     if n == None or m < n:
##         n = m
##     if n == 0:
##         return 1
##     if n == 1:
##         return v[0]
##     return continuant(v[:n-1])*v[n-1] + continuant(v[:n-2])

def continuant(v, n=None):
    r"""
    Function returns the continuant of the sequence `v` (list
    or tuple).

    Definition: see Graham, Knuth and Patashnik, *Concrete Mathematics*,
    section 6.7: Continuants. The continuant is defined by

    - `K_0() = 1`
    - `K_1(x_1) = x_1`
    - `K_n(x_1, \cdots, x_n) = K_{n-1}(x_n, \cdots x_{n-1})x_n + K_{n-2}(x_1,  \cdots, x_{n-2})`

    If ``n = None`` or ``n > len(v)`` the default
    ``n = len(v)`` is used.

    INPUT:

    -  ``v`` - list or tuple of elements of a ring
    -  ``n`` - optional integer

    OUTPUT: element of ring (integer, polynomial, etcetera).

    EXAMPLES::

        sage: continuant([1,2,3])
        10
        sage: p = continuant([2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10])
        sage: q = continuant([1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10])
        sage: p/q
        517656/190435
        sage: convergent([2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10],14)
        517656/190435
        sage: x = PolynomialRing(RationalField(),'x',5).gens()
        sage: continuant(x)
        x0*x1*x2*x3*x4 + x0*x1*x2 + x0*x1*x4 + x0*x3*x4 + x2*x3*x4 + x0 + x2 + x4
        sage: continuant(x, 3)
        x0*x1*x2 + x0 + x2
        sage: continuant(x,2)
        x0*x1 + 1

    We verify the identity

    .. math::

        K_n(z,z,\cdots,z) = \sum_{k=0}^n \binom{n-k}{k} z^{n-2k}

    for `n = 6` using polynomial arithmetic::

        sage: z = QQ['z'].0
        sage: continuant((z,z,z,z,z,z,z,z,z,z,z,z,z,z,z),6)
        z^6 + 5*z^4 + 6*z^2 + 1

        sage: continuant(9)
        Traceback (most recent call last):
        ...
        TypeError: object of type 'sage.rings.integer.Integer' has no len()

    AUTHORS:

    - Jaap Spies (2007-02-06)
    """
    m = len(v)
    if n == None or m < n:
        n = m
    if n == 0:
        return 1
    if n == 1:
        return v[0]
    a, b = 1, v[0]
    for k in range(1,n):
        a, b = b, a + b*v[k]
    return b

def number_of_divisors(n):
    """
    Return the number of divisors of the integer n.

    INPUT:

    - ``n`` - a nonzero integer

    OUTPUT:

    - an integer, the number of divisors of n

    EXAMPLES::

        sage: number_of_divisors(100)
        9
        sage: number_of_divisors(-720)
        30
    """
    m = ZZ(n)
    if m.is_zero():
        raise ValueError, "input must be nonzero"
    return ZZ(pari(m).numdiv())



def hilbert_symbol(a, b, p, algorithm="pari"):
    """
    Returns 1 if `ax^2 + by^2` `p`-adically represents
    a nonzero square, otherwise returns `-1`. If either a or b
    is 0, returns 0.

    INPUT:


    -  ``a, b`` - integers

    -  ``p`` - integer; either prime or -1 (which
       represents the archimedean place)

    -  ``algorithm`` - string

       -  ``'pari'`` - (default) use the PARI C library

       -  ``'direct'`` - use a Python implementation

       -  ``'all'`` - use both PARI and direct and check that
          the results agree, then return the common answer


    OUTPUT: integer (0, -1, or 1)

    EXAMPLES::

        sage: hilbert_symbol (-1, -1, -1, algorithm='all')
        -1
        sage: hilbert_symbol (2,3, 5, algorithm='all')
        1
        sage: hilbert_symbol (4, 3, 5, algorithm='all')
        1
        sage: hilbert_symbol (0, 3, 5, algorithm='all')
        0
        sage: hilbert_symbol (-1, -1, 2, algorithm='all')
        -1
        sage: hilbert_symbol (1, -1, 2, algorithm='all')
        1
        sage: hilbert_symbol (3, -1, 2, algorithm='all')
        -1

        sage: hilbert_symbol(QQ(-1)/QQ(4), -1, 2) == -1
        True
        sage: hilbert_symbol(QQ(-1)/QQ(4), -1, 3) == 1
        True

    AUTHORS:

    - William Stein and David Kohel (2006-01-05)
    """
    p = ZZ(p)
    if p != -1 and not p.is_prime():
        raise ValueError, "p must be prime or -1"
    a = QQ(a).numerator() * QQ(a).denominator()
    b = QQ(b).numerator() * QQ(b).denominator()

    if algorithm == "pari":
        return ZZ(pari(a).hilbert(b,p))

    elif algorithm == 'direct':
        if a == 0 or b == 0:
            return ZZ(0)

        p = ZZ(p)
        one = ZZ(1)

        if p != -1:
            p_sqr = p**2
            while a%p_sqr == 0: a //= p_sqr
            while b%p_sqr == 0: b //= p_sqr

        if p != 2 and True in ( kronecker(x,p) == 1 for x in (a,b,a+b) ):
            return one
        if a%p == 0:
            if b%p == 0:
                return hilbert_symbol(p,-(b//p),p)*hilbert_symbol(a//p,b,p)
            elif p == 2 and (b%4) == 3:
                if kronecker(a+b,p) == -1:
                    return -one
            elif kronecker(b,p) == -1:
                return -one
        elif b%p == 0:
            if p == 2 and (a%4) == 3:
                if kronecker(a+b,p) == -1:
                    return -one
            elif kronecker(a,p) == -1:
                return -one
        elif p == 2 and (a%4) == 3 and (b%4) == 3:
            return -one
        return one
    elif algorithm == 'all':
        ans_pari = hilbert_symbol(a,b,p,algorithm='pari')
        ans_direct = hilbert_symbol(a,b,p,algorithm='direct')
        if ans_pari != ans_direct:
            raise RuntimeError, "There is a bug in hilbert_symbol; two ways of computing the Hilbert symbol (%s,%s)_%s disagree"%(a,b,p)
        return ans_pari
    else:
        raise ValueError, "Algorithm %s not defined"%algorithm


def hilbert_conductor(a, b):
    """
    This is the product of all (finite) primes where the Hilbert symbol is -1.
    What is the same, this is the (reduced) discriminant of the quaternion
    algebra `(a,b)` over `\QQ`.

    INPUT:

    - ``a``, ``b`` -- integers

    OUTPUT:

    - squarefree positive integer

    EXAMPLES::

        sage: hilbert_conductor(-1, -1)
        2
        sage: hilbert_conductor(-1, -11)
        11
        sage: hilbert_conductor(-2, -5)
        5
        sage: hilbert_conductor(-3, -17)
        17

    AUTHOR:

    - Gonzalo Tornaria (2009-03-02)
    """
    a, b = ZZ(a), ZZ(b)
    d = ZZ(1)
    for p in union(union( [2], prime_divisors(a) ), prime_divisors(b) ):
        if hilbert_symbol(a, b, p) == -1:
            d *= p
    return d

def hilbert_conductor_inverse(d):
    """
    Finds a pair of integers `(a,b)` such that ``hilbert_conductor(a,b) == d``.
    The quaternion algebra `(a,b)` over `\QQ` will then have (reduced)
    discriminant `d`.

    INPUT:

    - ``d`` -- square-free positive integer

    OUTPUT: pair of integers

    EXAMPLES::

        sage: hilbert_conductor_inverse(2)
        (-1, -1)
        sage: hilbert_conductor_inverse(3)
        (-1, -3)
        sage: hilbert_conductor_inverse(6)
        (-1, 3)
        sage: hilbert_conductor_inverse(30)
        (-3, -10)
        sage: hilbert_conductor_inverse(4)
        Traceback (most recent call last):
        ...
        ValueError: d needs to be squarefree
        sage: hilbert_conductor_inverse(-1)
        Traceback (most recent call last):
        ...
        ValueError: d needs to be positive

    AUTHOR:

    - Gonzalo Tornaria (2009-03-02)

    TESTS::

        sage: for i in xrange(100):
        ...     d = ZZ.random_element(2**32).squarefree_part()
        ...     if hilbert_conductor(*hilbert_conductor_inverse(d)) != d:
        ...         print "hilbert_conductor_inverse failed for d =", d
    """
    Z = ZZ
    d = Z(d)
    if d <= 0:
        raise ValueError, "d needs to be positive"
    if d == 1:
        return (Z(-1), Z(1))
    if d == 2:
        return (Z(-1), Z(-1))
    if d.is_prime():
        if d%4 == 3:
            return (Z(-1), -d)
        if d%8 == 5:
            return (Z(-2), -d)
        q = 3
        while q%4 != 3 or kronecker_symbol(d,q) != -1:
            q = next_prime(q)
        return (Z(-q), -d)
    else:
        mo = moebius(d)
        if mo == 0:
            raise ValueError, "d needs to be squarefree"
        if d % 2 == 0 and mo*d % 16 != 2:
            dd = mo * d / 2
        else:
            dd = mo * d
        q = 1
        while hilbert_conductor(-q, dd) != d:
            q+=1;
        if dd%q == 0:
            dd /= q
        return (Z(-q), Z(dd))


##############################################################################
##  falling and rising factorials
##  By Jaap Spies
##
##       Copyright (C) 2006 Jaap Spies <j.spies@hccnet.nl>
##      Copyright (C) 2006 William Stein <wstein@gmail.com>
##
## Distributed under the terms of the GNU General Public License (GPL)
##                  http://www.gnu.org/licenses/
##############################################################################


def falling_factorial(x, a):
    r"""
    Returns the falling factorial `(x)_a`.

    The notation in the literature is a mess: often `(x)_a`,
    but there are many other notations: GKP: Concrete Mathematics uses
    `x^{\underline{a}}`.

    Definition: for integer `a \ge 0` we have
    `x(x-1) \cdots (x-a+1)`. In all other cases we use the
    GAMMA-function: `\frac {\Gamma(x+1)} {\Gamma(x-a+1)}`.

    INPUT:

    -  ``x`` - element of a ring

    -  ``a`` - a non-negative integer or

    OR

    -  ``x and a`` - any numbers

    OUTPUT: the falling factorial

    EXAMPLES::

        sage: falling_factorial(10, 3)
        720
        sage: falling_factorial(10, RR('3.0'))
        720.000000000000
        sage: falling_factorial(10, RR('3.3'))
        1310.11633396601
        sage: falling_factorial(10, 10)
        3628800
        sage: factorial(10)
        3628800
        sage: a = falling_factorial(1+I, I); a
        gamma(I + 2)
        sage: CC(a)
        0.652965496420167 + 0.343065839816545*I
        sage: falling_factorial(1+I, 4)
        4*I + 2
        sage: falling_factorial(I, 4)
        -10

    ::

        sage: M = MatrixSpace(ZZ, 4, 4)
        sage: A = M([1,0,1,0,1,0,1,0,1,0,10,10,1,0,1,1])
        sage: falling_factorial(A, 2) # A(A - I)
        [  1   0  10  10]
        [  1   0  10  10]
        [ 20   0 101 100]
        [  2   0  11  10]

    ::

        sage: x = ZZ['x'].0
        sage: falling_factorial(x, 4)
        x^4 - 6*x^3 + 11*x^2 - 6*x

    AUTHORS:

    - Jaap Spies (2006-03-05)
    """
    if isinstance(a, (integer.Integer, int, long)) and a >= 0:
        return misc.prod([(x - i) for i in range(a)])
    from sage.functions.all import gamma
    return gamma(x+1) / gamma(x-a+1)

def rising_factorial(x, a):
    r"""
    Returns the rising factorial `(x)^a`.

    The notation in the literature is a mess: often `(x)^a`,
    but there are many other notations: GKP: Concrete Mathematics uses
    `x^{\overline{a}}`.

    The rising factorial is also known as the Pochhammer symbol, see
    Maple and Mathematica.

    Definition: for integer `a \ge 0` we have
    `x(x+1) \cdots (x+a-1)`. In all other cases we use the
    GAMMA-function: `\frac {\Gamma(x+a)} {\Gamma(x)}`.

    INPUT:


    -  ``x`` - element of a ring

    -  ``a`` - a non-negative integer or

    -  ``x and a`` - any numbers


    OUTPUT: the rising factorial

    EXAMPLES::

        sage: rising_factorial(10,3)
        1320

    ::

        sage: rising_factorial(10,RR('3.0'))
        1320.00000000000

    ::

        sage: rising_factorial(10,RR('3.3'))
        2826.38895824964

    ::

        sage: a = rising_factorial(1+I, I); a
        gamma(2*I + 1)/gamma(I + 1)
        sage: CC(a)
        0.266816390637832 + 0.122783354006372*I

    ::

        sage: a = rising_factorial(I, 4); a
        -10

    See falling_factorial(I, 4).

    ::

        sage: x = polygen(ZZ)
        sage: rising_factorial(x, 4)
        x^4 + 6*x^3 + 11*x^2 + 6*x

    AUTHORS:

    - Jaap Spies (2006-03-05)
    """
    if isinstance(a, (integer.Integer, int, long)) and a >= 0:
        return misc.prod([(x + i) for i in range(a)])
    from sage.functions.all import gamma
    return gamma(x+a) / gamma(x)


def integer_ceil(x):
    """
    Return the ceiling of x.

    EXAMPLES::

        sage: integer_ceil(5.4)
        6
    """
    try:
        return sage.rings.all.Integer(x.ceil())
    except AttributeError:
        try:
            return sage.rings.all.Integer(int(math.ceil(float(x))))
        except TypeError:
            pass
    raise NotImplementedError, "computation of floor of %s not implemented"%repr(x)

def integer_floor(x):
    r"""
    Return the largest integer `\leq x`.

    INPUT:


    -  ``x`` - an object that has a floor method or is
       coercible to int


    OUTPUT: an Integer

    EXAMPLES::

        sage: integer_floor(5.4)
        5
        sage: integer_floor(float(5.4))
        5
        sage: integer_floor(-5/2)
        -3
        sage: integer_floor(RDF(-5/2))
        -3
    """
    try:
        return ZZ(x.floor())
    except AttributeError:
        try:
            return ZZ(int(math.floor(float(x))))
        except TypeError:
            pass
    raise NotImplementedError, "computation of floor of %s not implemented"%x



def two_squares(n, algorithm='gap'):
    """
    Write the integer n as a sum of two integer squares if possible;
    otherwise raise a ValueError.

    EXAMPLES::

        sage: two_squares(389)
        (10, 17)
        sage: two_squares(7)
        Traceback (most recent call last):
        ...
        ValueError: 7 is not a sum of two squares
        sage: a,b = two_squares(2009); a,b
        (28, 35)
        sage: a^2 + b^2
        2009

    TODO: Create an implementation using PARI's continued fraction
    implementation.
    """
    from sage.rings.all import Integer
    n = Integer(n)

    if algorithm == 'gap':
        import sage.interfaces.gap as gap
        a = gap.gap.eval('TwoSquares(%s)'%n)
        if a == 'fail':
            raise ValueError, "%s is not a sum of two squares"%n
        x, y = eval(a)
        return Integer(x), Integer(y)
    else:
        raise RuntimeError, "unknown algorithm '%s'"%algorithm

def _brute_force_four_squares(n):
    """
    Brute force search for decomposition into a sum of four squares,
    for cases that the main algorithm fails to handle.

    INPUT:

    - ``n`` - a positive integer

    OUTPUT:

    - a list of four numbers whose squares sum to n

    EXAMPLES::

        sage: from sage.rings.arith import _brute_force_four_squares
        sage: _brute_force_four_squares(567)
        [1, 1, 6, 23]
    """
    from math import sqrt
    for i in range(0,int(sqrt(n))+1):
        for j in range(i,int(sqrt(n-i**2))+1):
            for k in range(j, int(sqrt(n-i**2-j**2))+1):
                rem = n-i**2-j**2-k**2
                if rem >= 0:
                    l = int(sqrt(rem))
                    if rem-l**2==0:
                        return [i,j,k,l]

def four_squares(n):
    """
    Computes the decomposition into the sum of four squares,
    using an algorithm described by Peter Schorn at:
    http://www.schorn.ch/howto.html.

    INPUT:

    - ``n`` - an integer

    OUTPUT:

    - a list of four numbers whose squares sum to n

    EXAMPLES::

        sage: four_squares(3)
        [0, 1, 1, 1]
        sage: four_squares(130)
        [0, 0, 3, 11]
        sage: four_squares(1101011011004)
        [2, 1049178, 2370, 15196]
        sage: sum([i-sum([q^2 for q in four_squares(i)]) for i in range(2,10000)]) # long time
        0
    """
    from sage.rings.finite_rings.integer_mod import mod
    from math import sqrt
    from sage.rings.arith import _brute_force_four_squares
    try:
        ts = two_squares(n)
        return [0,0,ts[0],ts[1]]
    except ValueError:
        pass
    m = n
    v = 0
    while mod(m,4) == 0:
        v = v +1
        m = m // 4
    if mod(m,8) == 7:
        d = 1
        m = m - 1
    else:
        d = 0
    if mod(m,8)==3:
        x = int(sqrt(m))
        if mod(x,2) == 0:
            x = x - 1
        p = (m-x**2) // 2
        while not is_prime(p):
            x = x - 2
            p = (m-x**2) // 2
            if x < 0:
            # fall back to brute force
                m = m + d
                return [2**v*q for q in _brute_force_four_squares(m)]
        y,z = two_squares(p)
        return [2**v*q for q in [d,x,y+z,abs(y-z)]]
    x = int(sqrt(m))
    p = m - x**2
    if p == 1:
        return[2**v*q for q in [d,0,x,1]]
    while not is_prime(p):
        x = x - 1
        p = m - x**2
        if x < 0:
            # fall back to brute force
            m = m + d
            return [2**v*q for q in _brute_force_four_squares(m)]
    y,z = two_squares(p)
    return [2**v*q for q in [d,x,y,z]]


def subfactorial(n):
    r"""
    Subfactorial or rencontres numbers, or derangements: number of
    permutations of `n` elements with no fixed points.

    INPUT:


    -  ``n`` - non negative integer


    OUTPUT:


    -  ``integer`` - function value


    EXAMPLES::

        sage: subfactorial(0)
        1
        sage: subfactorial(1)
        0
        sage: subfactorial(8)
        14833

    AUTHORS:

    - Jaap Spies (2007-01-23)
    """
    return factorial(n)*sum(((-1)**k)/factorial(k) for k in range(n+1))


def is_power_of_two(n):
    r"""
    This function returns True if and only if `n` is a power of
    2

    INPUT:


    -  ``n`` - integer


    OUTPUT:


    -  ``True`` - if n is a power of 2

    -  ``False`` - if not


    EXAMPLES::

        sage: is_power_of_two(1024)
        True

    ::

        sage: is_power_of_two(1)
        True

    ::

        sage: is_power_of_two(24)
        False

    ::

        sage: is_power_of_two(0)
        False

    ::

        sage: is_power_of_two(-4)
        False

    AUTHORS:

    - Jaap Spies (2006-12-09)
    """
    # modification of is2pow(n) from the Programming Guide
    while n > 0 and n%2 == 0:
        n = n >> 1
    return n == 1

def differences(lis, n=1):
    """
    Returns the `n` successive differences of the elements in
    `lis`.

    EXAMPLES::

        sage: differences(prime_range(50))
        [1, 2, 2, 4, 2, 4, 2, 4, 6, 2, 6, 4, 2, 4]
        sage: differences([i^2 for i in range(1,11)])
        [3, 5, 7, 9, 11, 13, 15, 17, 19]
        sage: differences([i^3 + 3*i for i in range(1,21)])
        [10, 22, 40, 64, 94, 130, 172, 220, 274, 334, 400, 472, 550, 634, 724, 820, 922, 1030, 1144]
        sage: differences([i^3 - i^2 for i in range(1,21)], 2)
        [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 100, 106, 112]
        sage: differences([p - i^2 for i, p in enumerate(prime_range(50))], 3)
        [-1, 2, -4, 4, -4, 4, 0, -6, 8, -6, 0, 4]

    AUTHORS:

    - Timothy Clemans (2008-03-09)
    """
    n = ZZ(n)
    if n < 1:
        raise ValueError, 'n must be greater than 0'
    lis = [lis[i + 1] - num for i, num in enumerate(lis[:-1])]
    if n == 1:
        return lis
    return differences(lis, n - 1)

def _cmp_complex_for_display(a, b):
    r"""
    Compare two complex numbers in a "pretty" (but mathematically
    meaningless) fashion, for display only.

    Real numbers (with a zero imaginary part) come before complex numbers,
    and are sorted.  Complex numbers are sorted by their real part
    unless their real parts are quite close, in which case they are
    sorted by their imaginary part.

    EXAMPLES::

        sage: import sage.rings.arith
        sage: cmp_c = sage.rings.arith._cmp_complex_for_display
        sage: teeny = 3e-11
        sage: cmp_c(CC(5), CC(3, 3))
        -1
        sage: cmp_c(CC(3), CC(5, 5))
        -1
        sage: cmp_c(CC(5), CC(3))
        1
        sage: cmp_c(CC(teeny, -1), CC(-teeny, 1))
        -1
        sage: cmp_c(CC(teeny, 1), CC(-teeny, -1))
        1
        sage: cmp_c(CC(0, 1), CC(1, 0.5))
        -1
        sage: cmp_c(CC(3+teeny, -1), CC(3-teeny, 1))
        -1
        sage: CIF200 = ComplexIntervalField(200)
        sage: cmp_c(CIF200(teeny, -1), CIF200(-teeny, 1))
        -1
        sage: cmp_c(CIF200(teeny, 1), CIF200(-teeny, -1))
        1
        sage: cmp_c(CIF200(0, 1), CIF200(1, 0.5))
        -1
        sage: cmp_c(CIF200(3+teeny, -1), CIF200(3-teeny, 1))
        -1
    """
    ar = a.real(); br = b.real()
    ai = a.imag(); bi = b.imag()
    epsilon = ar.parent()(1e-10)
    if ai:
        if bi:
            if abs(br) < epsilon:
                if abs(ar) < epsilon:
                    return cmp(ai, bi)
                return cmp(ar, 0)
            if abs((ar - br) / br) < epsilon:
                return cmp(ai, bi)
            return cmp(ar, br)
        else:
            return 1
    else:
        if bi:
            return -1
        else:
            return cmp(ar, br)

def sort_complex_numbers_for_display(nums):
    r"""
    Given a list of complex numbers (or a list of tuples, where the
    first element of each tuple is a complex number), we sort the list
    in a "pretty" order.  First come the real numbers (with zero
    imaginary part), then the complex numbers sorted according to
    their real part.  If two complex numbers have a real part which is
    sufficiently close, then they are sorted according to their
    imaginary part.

    This is not a useful function mathematically (not least because
    there's no principled way to determine whether the real components
    should be treated as equal or not).  It is called by various
    polynomial root-finders; its purpose is to make doctest printing
    more reproducible.

    We deliberately choose a cumbersome name for this function to
    discourage use, since it is mathematically meaningless.

    EXAMPLES::

        sage: import sage.rings.arith
        sage: sort_c = sort_complex_numbers_for_display
        sage: nums = [CDF(i) for i in range(3)]
        sage: for i in range(3):
        ...       nums.append(CDF(i + RDF.random_element(-3e-11, 3e-11),
        ...                       RDF.random_element()))
        ...       nums.append(CDF(i + RDF.random_element(-3e-11, 3e-11),
        ...                       RDF.random_element()))
        sage: shuffle(nums)
        sage: sort_c(nums)
        [0, 1.0, 2.0, -2.862406201e-11 - 0.708874026302*I, 2.2108362707e-11 - 0.436810529675*I, 1.00000000001 - 0.758765473764*I, 0.999999999976 - 0.723896589334*I, 1.99999999999 - 0.456080101207*I, 1.99999999999 + 0.609083628313*I]
    """
    if len(nums) == 0:
        return nums

    if isinstance(nums[0], tuple):
        return sorted(nums, cmp=_cmp_complex_for_display, key=lambda t: t[0])
    else:
        return sorted(nums, cmp=_cmp_complex_for_display)

def fundamental_discriminant(D):
    r"""
    Return the discriminant of the quadratic extension
    `K=Q(\sqrt{D})`, i.e. an integer d congruent to either 0 or
    1, mod 4, and such that, at most, the only square dividing it is
    4.

    INPUT:

    - ``D`` - an integer

    OUTPUT:

    - an integer, the fundamental discriminant

    EXAMPLES::

        sage: fundamental_discriminant(102)
        408
        sage: fundamental_discriminant(720)
        5
        sage: fundamental_discriminant(2)
        8

    """
    from sage.rings.all import Integer
    D = Integer(D)
    D = D.squarefree_part()
    if D%4 == 1:
        return D
    return 4*D

def squarefree_divisors(x):
    """
    Iterator over the squarefree divisors (up to units) of the element x.

    Depends on the output of the prime_divisors function.

    INPUT::

        x -- an element of any ring for which the prime_divisors
             function works.

    EXAMPLES::

        sage: list(squarefree_divisors(7))
        [1, 7]
        sage: list(squarefree_divisors(6))
        [1, 2, 3, 6]
        sage: list(squarefree_divisors(12))
        [1, 2, 3, 6]

    """
    p_list = prime_divisors(x)
    from sage.misc.misc import powerset
    for a in powerset(p_list):
        yield prod(a,1)
