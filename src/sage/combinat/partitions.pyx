"""
Number of partitions of integer

AUTHOR:
    -- William Stein (2007-07-28): initial version
    -- Jonathan Bober (2007-07-28): wrote the program partitions_c.cc
                  that does all the actual heavy lifting.
"""

import sys

cdef extern from "gmp.h":
    ctypedef void* mpz_t

cdef extern from "partitions_c.h":
    int part(mpz_t answer, unsigned int n)
    int test(bint longtest, bint forever)

include "../ext/interrupt.pxi"

from sage.rings.integer cimport Integer

def number_of_partitions(n):
    """
    Returns the number of partitions of the integer n.

    EXAMPLES::

        sage: from sage.combinat.partitions import number_of_partitions
        sage: number_of_partitions(3)
        3
        sage: number_of_partitions(10)
        42
        sage: number_of_partitions(40)
        37338
        sage: number_of_partitions(100)
        190569292
        sage: number_of_partitions(100000)
        27493510569775696512677516320986352688173429315980054758203125984302147328114964173055050741660736621590157844774296248940493063070200461792764493033510116079342457190155718943509725312466108452006369558934464248716828789832182345009262853831404597021307130674510624419227311238999702284408609370935531629697851569569892196108480158600569421098519

    TESTS::

        sage: n = 500 + randint(0,500)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0
        True
        sage: n = 1500 + randint(0,1500)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0
        True
        sage: n = 1000000 + randint(0,1000000)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0
        True
        sage: n = 1000000 + randint(0,1000000)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0
        True
        sage: n = 1000000 + randint(0,1000000)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0
        True
        sage: n = 1000000 + randint(0,1000000)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0
        True
        sage: n = 1000000 + randint(0,1000000)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0
        True
        sage: n = 1000000 + randint(0,1000000)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0
        True
        sage: n = 100000000 + randint(0,100000000)
        sage: number_of_partitions( n - (n % 385) + 369) % 385 == 0  # long time (4s on sage.math, 2011)
        True

    Another consistency test for n up to 500::

        sage: len([n for n in [1..500] if number_of_partitions(n) != Partitions(n).cardinality(algorithm='pari')])
        0

    """
    n = Integer(n)
    if n < 0:
        raise ValueError, "n (=%s) must be a nonnegative integer"%n
    elif n <= 1:
        return Integer(1)  # part hangs on n=1 as input.
    if n >= Integer('4294967296'):
        raise ValueError, "input must be a nonnegative integer less than 4294967296."
    cdef unsigned int nn = n

    cdef Integer ans = Integer(0)

    sig_on()
    part(ans.value, nn)
    sig_off()

    return ans

def run_tests(bint longtest=False, bint forever=False):
    sig_on()
    error = test(longtest, forever)
    sig_off()
    print "Done."
    if error:
        return error
