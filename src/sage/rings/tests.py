"""
TESTS:
    sage: K.<x>=FractionField(QQ['x'])
    sage: V.<z> = K[]
    sage: x+z
    z + x

    sage: (1/2)^(2^100)
    Traceback (most recent call last):
    ...
    RuntimeError: exponent must be at most 9223372036854775807     # 64-bit
    RuntimeError: exponent must be at most 2147483647              # 32-bit
"""

import random


from sage.misc.all import get_memory_usage

def prime_finite_field():
    """
    Create a random prime finite field with cardinality at most 10^20.

    OUTPUT:
        a prime finite field

    EXAMPLES:
        sage: sage.rings.tests.prime_finite_field()
        Finite Field of size 64748301524082521489
    """
    from sage.all import ZZ, GF
    return GF(ZZ.random_element(x=2, y=10**20 - 12).next_prime())

def finite_field():
    """
    Create a random finite field with degree at most 20 and prime at most 10^6.

    OUTPUT:
        a finite field

    EXAMPLES:
        sage: sage.rings.tests.finite_field()
        Finite Field in a of size 161123^4
    """
    from sage.all import ZZ, GF
    p = ZZ.random_element(x=2, y=10**6-18).next_prime()
    d = ZZ.random_element(x=1, y=20)
    return GF(p**d,'a')

def small_finite_field():
    """
    Create a random finite field with cardinality at most 2^16.

    OUTPUT:
        a finite field

    EXAMPLES:
        sage: sage.rings.tests.small_finite_field()
        Finite Field of size 30029
    """
    from sage.all import ZZ, GF
    while True:
        q = ZZ.random_element(x=2,y=2**16)
        if q.is_prime_power():
            return GF(q,'a')

def integer_mod_ring():
    """
    Return a random ring of integers modulo n with n at most 50000.

    EXAMPLES:
        sage: sage.rings.tests.integer_mod_ring()
        Ring of integers modulo 30029
    """
    from sage.all import ZZ, IntegerModRing
    n = ZZ.random_element(x=2,y=50000)
    return IntegerModRing(n)

def quadratic_number_field():
    """
    Return a quadratic extension of QQ.

    EXAMPLES:
        sage: sage.rings.tests.quadratic_number_field()
        Number Field in a with defining polynomial x^2 - 61099
    """
    from sage.all import ZZ, QuadraticField
    while True:
        d = ZZ.random_element(x=-10**5, y=10**5)
        if not d.is_square():
            return QuadraticField(d,'a')

def absolute_number_field(maxdeg=10):
    """
    Return an absolute extension of QQ of degree at most 10.

    EXAMPLES:
        sage: sage.rings.tests.absolute_number_field()
        Number Field in a with defining polynomial x^5 + 82*x^4 - 46*x^3 + 39*x^2 - x - 41
    """
    from sage.all import ZZ, NumberField
    R = ZZ['x']
    while True:
        f = R.random_element(degree=ZZ.random_element(x=1,y=maxdeg),x=-100,y=100)
        if f.degree() <= 0: continue
        f = f + R.gen()**(f.degree()+1)  # make monic
        if f.is_irreducible():
            return NumberField(f, 'a')

def relative_number_field(n=2, maxdeg=2):
    """
    Return a tower of at most n extensions each of degree at most maxdeg.

    EXAMPLES:
        sage: sage.rings.tests.relative_number_field(3)
        Number Field in aaa with defining polynomial x^2 - 15*x + 17 over its base field
    """
    from sage.all import ZZ
    K = absolute_number_field(maxdeg)
    n -= 1
    var = 'aa'
    R = ZZ['x']
    while n >= 1:
        while True:
            f = R.random_element(degree=ZZ.random_element(x=1,y=maxdeg),x=-100,y=100)
            if f.degree() <= 0: continue
            f = f * f.denominator()  # bug trac #4781
            f = f + R.gen()**maxdeg  # make monic
            if f.is_irreducible():
                break
        K = K.extension(f,var)
        var += 'a'
        n -= 1
    return K


def rings0():
    """
    Return a list of pairs (f, desc), where f is a function that when
    called creates a random ring of a certain representative type
    described by desc.

    RINGS::
       - ZZ
       - QQ
       - ZZ/nZZ
       - GF(p)
       - GF(q)
       - quadratic number fields
       - absolute number fields
       - relative number fields

    EXAMPLES:
        sage: type(sage.rings.tests.rings0())
        <type 'list'>
    """
    from sage.all import IntegerRing, RationalField, ZZ, IntegerModRing
    v = [(IntegerRing, 'ring of integers'),
         (RationalField, 'field of rational numbers'),
         (integer_mod_ring, 'integers modulo n for n at most 50000'),
         (prime_finite_field, 'a prime finite field with cardinality at most 10^20'),
         (finite_field, 'finite field with degree at most 20 and prime at most 10^6'),
         (small_finite_field, 'finite field with cardinality at most 2^16'),
         (quadratic_number_field, 'a quadratic number field'),
         (absolute_number_field, 'an absolute number field of degree at most 10'),
         (relative_number_field, 'a tower of at most 2 extensions each of degree at most 2'),
         ]

    return v

def rings1():
    """
    Return an iterator over random rings.
    Return a list of pairs (f, desc), where f is a function that
    outputs a random ring that takes a ring and possibly
    some other data as constructor.

    RINGS::
        - polynomial ring in one variable over a rings0() ring.
        - polynomial ring over a rings1() ring.
        - multivariate polynomials

    EXAMPLES:
        sage: type(sage.rings.tests.rings0())
        <type 'list'>
    """
    v = rings0()
    X = random_rings(level=0)
    from sage.all import PolynomialRing, ZZ
    v = [(lambda : PolynomialRing(X.next(), names='x'), 'univariate polynomial ring over level 0 ring'),
         (lambda : PolynomialRing(X.next(), abs(ZZ.random_element(x=2,y=10)), names='x'),
                     'multivariate polynomial ring in between 2 and 10 variables over a level 0 ring')]
    return v

MAX_LEVEL=99999

def random_rings(level=MAX_LEVEL):
    """
    Return an iterator over random rings up to the given "level" of complexity.

    EXAMPLES:
        sage: type(sage.rings.tests.random_rings())
        <type 'generator'>
    """
    v = rings0()
    if level >= 1:
        v += rings1()
    while True:
        yield random.choice(v)[0]()

def test_random_elements(level=MAX_LEVEL, trials=None):
    """
    Create random elements of random rings until a crash occurs, in
    which case an exception is raised.  If trials is given, stop after
    that many trials.

    INPUT:
        level -- (default: MAX_LEVEL); controls the types of rings to use
        trials -- None or a positive integer.

    EXAMPLES:
        sage: sage.rings.tests.test_random_elements(trials=10)
        survived 0 tests...
        sage: sage.rings.tests.test_random_elements(trials=1000)  # long time (5 seconds)
        survived 0 tests...
    """
    r = random_rings(level)
    i = 0
    for R in r:
        print "survived %s tests (memory usage = %s)"%(i, get_memory_usage())
        i += 1
        print R
        print R.random_element()
        print "----"
        if trials and i >= trials:
            return

def test_random_arith(level=MAX_LEVEL, trials=None):
    """
    Create random elements of random rings and does some arithmetic
    with them, until a crash occurs, in which case an exception is
    raised.  If trials is given, stop after that many trials.

    INPUT:
        level -- (default: MAX_LEVEL); controls the types of rings to use
        trials -- None or a positive integer.

    EXAMPLES:
        sage: sage.rings.tests.test_random_arith(trials=10)
        survived 0 tests...
        sage: sage.rings.tests.test_random_arith(trials=1000)   # long time (5 seconds?)
        survived 0 tests...
    """
    i = 0
    for x in random_rings(level):
        print "survived %s tests (memory usage = %s)"%(i, get_memory_usage())
        i += 1
        print x
        a = x.random_element(); b = x.random_element()
        print a, b
        print a*b+a-b+1
        if trials and i >= trials:
            return
