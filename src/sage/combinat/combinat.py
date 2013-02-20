r"""
Combinatorial Functions

This module implements some combinatorial functions, as listed
below. For a more detailed description, see the relevant
docstrings.

**Sequences:**


-  Bell numbers, :func:`bell_number`

-  Catalan numbers, :func:`catalan_number` (not to be
   confused with the Catalan constant)

-  Eulerian/Euler numbers, :func:`euler_number` (Maxima)

-  Fibonacci numbers, :func:`fibonacci` (PARI) and
   :func:`fibonacci_number` (GAP) The PARI version is
   better.

-  Lucas numbers, :func:`lucas_number1`,
   :func:`lucas_number2`.

-  Stirling numbers, :func:`stirling_number1`,
   :func:`stirling_number2`.

**Set-theoretic constructions:**

-  Derangements of a multiset, :func:`derangements` and
   :func:`number_of_derangements`.

-  Tuples of a multiset, :func:`tuples` and
   :func:`number_of_tuples`. An ordered tuple of length k of
   set S is a ordered selection with repetitions of S and is
   represented by a sorted list of length k containing elements from
   S.

-  Unordered tuples of a set, :func:`unordered_tuples` and
   :func:`number_of_unordered_tuples`. An unordered tuple
   of length k of set S is an unordered selection with repetitions of S
   and is represented by a sorted list of length k containing elements
   from S.

.. WARNING::

   The following functions are deprecated and will soon be removed.

    - Combinations of a multiset, :func:`combinations`,
      :func:`combinations_iterator`, and :func:`number_of_combinations`. These
      are unordered selections without repetition of k objects from a multiset
      S.

    - Arrangements of a multiset, :func:`arrangements` and
      :func:`number_of_arrangements` These are ordered selections without
      repetition of k objects from a multiset S.

    - Permutations of a multiset, :func:`permutations`,
      :func:`permutations_iterator`, :func:`number_of_permutations`. A
      permutation is a list that contains exactly the same elements but possibly
      in different order.

**Partitions:**

-  Partitions of a set, :func:`partitions_set`,
   :func:`number_of_partitions_set`. An unordered partition
   of set S is a set of pairwise disjoint nonempty sets with union S
   and is represented by a sorted list of such sets.

-  Partitions of an integer, :func:`Partitions`.
   An unordered partition of n is an unordered sum
   `n = p_1+p_2 +\ldots+ p_k` of positive integers and is
   represented by the list `p = [p_1,p_2,\ldots,p_k]`, in
   nonincreasing order, i.e., `p1\geq p_2 ...\geq p_k`.

-  Ordered partitions of an integer,
   :func:`ordered_partitions`,
   :func:`number_of_ordered_partitions`. An ordered
   partition of n is an ordered sum
   `n = p_1+p_2 +\ldots+ p_k` of positive integers and is
   represented by the list `p = [p_1,p_2,\ldots,p_k]`, in
   nonincreasing order, i.e., `p1\geq p_2 ...\geq p_k`.

-  :func:`partitions_greatest` implements a special type
   of restricted partition.

-  :func:`partitions_greatest_eq` is another type of
   restricted partition.

-  Tuples of partitions, :class:`PartitionTuples`. A `k`-tuple of partitions is
   represented by a list of all `k`-tuples of partitions which together form a
   partition of `n`.

**Related functions:**

-  Bernoulli polynomials, :func:`bernoulli_polynomial`

**Implemented in other modules (listed for completeness):**

The ``sage.rings.arith`` module contains the following
combinatorial functions:

-  binomial the binomial coefficient (wrapped from PARI)

-  factorial (wrapped from PARI)

-  partition (from the Python Cookbook) Generator of the list of
   all the partitions of the integer `n`.

-  :func:`number_of_partitions` (wrapped from PARI) the
   *number* of partitions:

-  :func:`falling_factorial` Definition: for integer
   `a \ge 0` we have `x(x-1) \cdots (x-a+1)`. In all
   other cases we use the GAMMA-function:
   `\frac {\Gamma(x+1)} {\Gamma(x-a+1)}`.

-  :func:`rising_factorial` Definition: for integer
   `a \ge 0` we have `x(x+1) \cdots (x+a-1)`. In all
   other cases we use the GAMMA-function:
   `\frac {\Gamma(x+a)} {\Gamma(x)}`.

-  gaussian_binomial the gaussian binomial

.. math::

             \binom{n}{k}_q = \frac{(1-q^m)(1-q^{m-1})\cdots (1-q^{m-r+1})}                              {(1-q)(1-q^2)\cdots (1-q^r)}.

The ``sage.groups.perm_gps.permgroup_elements``
contains the following combinatorial functions:


-  matrix method of PermutationGroupElement yielding the
   permutation matrix of the group element.

.. TODO::

    GUAVA commands:
        * MOLS returns a list of n Mutually Orthogonal Latin Squares (MOLS).
        * VandermondeMat
        * GrayMat returns a list of all different vectors of length n over
          the field F, using Gray ordering.
    Not in GAP:
        * Rencontres numbers
          http://en.wikipedia.org/wiki/Rencontres_number

REFERENCES:

- http://en.wikipedia.org/wiki/Twelvefold_way (general reference)

AUTHORS:

- David Joyner (2006-07): initial implementation.

- William Stein (2006-07): editing of docs and code; many
  optimizations, refinements, and bug fixes in corner cases

- David Joyner (2006-09): bug fix for combinations, added
  permutations_iterator, combinations_iterator from Python Cookbook,
  edited docs.

- David Joyner (2007-11): changed permutations, added hadamard_matrix

- Florent Hivert (2009-02): combinatorial class cleanup

- Fredrik Johansson (2010-07): fast implementation of ``stirling_number2``

- Punarbasu Purkayastha (2012-12): deprecate arrangements, combinations,
  combinations_iterator, and clean up very old deprecated methods.

Functions and classes
---------------------
"""

#*****************************************************************************
#       Copyright (C) 2006 David Joyner <wdjoyner@gmail.com>,
#                     2007 Mike Hansen <mhansen@gmail.com>,
#                     2006 William Stein <wstein@gmail.com>
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
from sage.interfaces.all import gap, maxima
from sage.rings.all import QQ, ZZ, Integer
from sage.rings.arith import bernoulli, binomial
from sage.rings.polynomial.polynomial_element import Polynomial
from sage.misc.sage_eval import sage_eval
from sage.libs.all import pari
from sage.misc.prandom import randint
from sage.misc.misc import prod
from sage.structure.sage_object import SageObject
from sage.structure.parent import Parent
from sage.misc.lazy_attribute import lazy_attribute
from sage.misc.superseded import deprecation
from combinat_cython import _stirling_number2
######### combinatorial sequences

def bell_number(n):
    r"""
    Returns the n-th Bell number (the number of ways to partition a set
    of n elements into pairwise disjoint nonempty subsets).

    If `n \leq 0`, returns `1`.

    Wraps GAP's Bell.

    EXAMPLES::

        sage: bell_number(10)
        115975
        sage: bell_number(2)
        2
        sage: bell_number(-10)
        1
        sage: bell_number(1)
        1
        sage: bell_number(1/3)
        Traceback (most recent call last):
        ...
        TypeError: no conversion of this rational to integer
    """
    ans=gap.eval("Bell(%s)"%ZZ(n))
    return ZZ(ans)

def catalan_number(n):
    r"""
    Returns the n-th Catalan number

    Catalan numbers: The `n`-th Catalan number is given
    directly in terms of binomial coefficients by

    .. math::

               C_n = \frac{1}{n+1}{2n\choose n} = \frac{(2n)!}{(n+1)!\,n!}              \qquad\mbox{ for }\quad n\ge 0.



    Consider the set `S = \{ 1, ..., n \}`. A noncrossing
    partition of `S` is a partition in which no two blocks
    "cross" each other, i.e., if a and b belong to one block and x and
    y to another, they are not arranged in the order axby.
    `C_n` is the number of noncrossing partitions of the set
    `S`. There are many other interpretations (see
    REFERENCES).

    When `n=-1`, this function raises a ZeroDivisionError; for
    other `n<0` it returns `0`.

    INPUT:

    - ``n`` - integer

    OUTPUT: integer



    EXAMPLES::

        sage: [catalan_number(i) for i in range(7)]
        [1, 1, 2, 5, 14, 42, 132]
        sage: taylor((-1/2)*sqrt(1 - 4*x^2), x, 0, 15)
        132*x^14 + 42*x^12 + 14*x^10 + 5*x^8 + 2*x^6 + x^4 + x^2 - 1/2
        sage: [catalan_number(i) for i in range(-7,7) if i != -1]
        [0, 0, 0, 0, 0, 0, 1, 1, 2, 5, 14, 42, 132]
        sage: catalan_number(-1)
        Traceback (most recent call last):
        ...
        ZeroDivisionError
        sage: [catalan_number(n).mod(2) for n in range(16)]
        [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1]

    REFERENCES:

    -  http://en.wikipedia.org/wiki/Catalan_number

    -  http://www-history.mcs.st-andrews.ac.uk/~history/Miscellaneous/CatalanNumbers/catalan.html
    """
    from sage.rings.arith import binomial
    n = ZZ(n)
    return binomial(2*n,n).divide_knowing_divisible_by(n+1)

def euler_number(n):
    """
    Returns the n-th Euler number

    IMPLEMENTATION: Wraps Maxima's euler.

    EXAMPLES::

        sage: [euler_number(i) for i in range(10)]
        [1, 0, -1, 0, 5, 0, -61, 0, 1385, 0]
        sage: maxima.eval("taylor (2/(exp(x)+exp(-x)), x, 0, 10)")
        '1-x^2/2+5*x^4/24-61*x^6/720+277*x^8/8064-50521*x^10/3628800'
        sage: [euler_number(i)/factorial(i) for i in range(11)]
        [1, 0, -1/2, 0, 5/24, 0, -61/720, 0, 277/8064, 0, -50521/3628800]
        sage: euler_number(-1)
        Traceback (most recent call last):
        ...
        ValueError: n (=-1) must be a nonnegative integer

    REFERENCES:

    - http://en.wikipedia.org/wiki/Euler_number
    """
    n = ZZ(n)
    if n < 0:
        raise ValueError, "n (=%s) must be a nonnegative integer"%n
    return ZZ(maxima.eval("euler(%s)"%n))

def fibonacci(n, algorithm="pari"):
    """
    Returns the n-th Fibonacci number. The Fibonacci sequence
    `F_n` is defined by the initial conditions
    `F_1=F_2=1` and the recurrence relation
    `F_{n+2} = F_{n+1} + F_n`. For negative `n` we
    define `F_n = (-1)^{n+1}F_{-n}`, which is consistent with
    the recurrence relation.

    INPUT:


    -  ``algorithm`` - string:

    -  ``"pari"`` - (default) - use the PARI C library's
       fibo function.

    -  ``"gap"`` - use GAP's Fibonacci function


    .. note::

       PARI is tens to hundreds of times faster than GAP here;
       moreover, PARI works for every large input whereas GAP doesn't.

    EXAMPLES::

        sage: fibonacci(10)
        55
        sage: fibonacci(10, algorithm='gap')
        55

    ::

        sage: fibonacci(-100)
        -354224848179261915075
        sage: fibonacci(100)
        354224848179261915075

    ::

        sage: fibonacci(0)
        0
        sage: fibonacci(1/2)
        Traceback (most recent call last):
        ...
        TypeError: no conversion of this rational to integer
    """
    n = ZZ(n)
    if algorithm == 'pari':
        return ZZ(pari(n).fibonacci())
    elif algorithm == 'gap':
        return ZZ(gap.eval("Fibonacci(%s)"%n))
    else:
        raise ValueError, "no algorithm %s"%algorithm

def lucas_number1(n,P,Q):
    """
    Returns the n-th Lucas number "of the first kind" (this is not
    standard terminology). The Lucas sequence `L^{(1)}_n` is
    defined by the initial conditions `L^{(1)}_1=0`,
    `L^{(1)}_2=1` and the recurrence relation
    `L^{(1)}_{n+2} = P*L^{(1)}_{n+1} - Q*L^{(1)}_n`.

    Wraps GAP's Lucas(...)[1].

    P=1, Q=-1 gives the Fibonacci sequence.

    INPUT:


    -  ``n`` - integer

    -  ``P, Q`` - integer or rational numbers


    OUTPUT: integer or rational number

    EXAMPLES::

        sage: lucas_number1(5,1,-1)
        5
        sage: lucas_number1(6,1,-1)
        8
        sage: lucas_number1(7,1,-1)
        13
        sage: lucas_number1(7,1,-2)
        43

    ::

        sage: lucas_number1(5,2,3/5)
        229/25
        sage: lucas_number1(5,2,1.5)
        Traceback (most recent call last):
        ...
        TypeError: no canonical coercion from Real Field with 53 bits of precision to Rational Field

    There was a conjecture that the sequence `L_n` defined by
    `L_{n+2} = L_{n+1} + L_n`, `L_1=1`,
    `L_2=3`, has the property that `n` prime implies
    that `L_n` is prime.

    ::

        sage: lucas = lambda n : Integer((5/2)*lucas_number1(n,1,-1)+(1/2)*lucas_number2(n,1,-1))
        sage: [[lucas(n),is_prime(lucas(n)),n+1,is_prime(n+1)] for n in range(15)]
        [[1, False, 1, False],
         [3, True, 2, True],
         [4, False, 3, True],
         [7, True, 4, False],
         [11, True, 5, True],
         [18, False, 6, False],
         [29, True, 7, True],
         [47, True, 8, False],
         [76, False, 9, False],
         [123, False, 10, False],
         [199, True, 11, True],
         [322, False, 12, False],
         [521, True, 13, True],
         [843, False, 14, False],
         [1364, False, 15, False]]

    Can you use Sage to find a counterexample to the conjecture?
    """
    ans=gap.eval("Lucas(%s,%s,%s)[1]"%(QQ._coerce_(P),QQ._coerce_(Q),ZZ(n)))
    return sage_eval(ans)

def lucas_number2(n,P,Q):
    r"""
    Returns the n-th Lucas number "of the second kind" (this is not
    standard terminology). The Lucas sequence `L^{(2)}_n` is
    defined by the initial conditions `L^{(2)}_1=2`,
    `L^{(2)}_2=P` and the recurrence relation
    `L^{(2)}_{n+2} = P*L^{(2)}_{n+1} - Q*L^{(2)}_n`.

    Wraps GAP's Lucas(...)[2].

    INPUT:


    -  ``n`` - integer

    -  ``P, Q`` - integer or rational numbers


    OUTPUT: integer or rational number

    EXAMPLES::

        sage: [lucas_number2(i,1,-1) for i in range(10)]
        [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]
        sage: [fibonacci(i-1)+fibonacci(i+1) for i in range(10)]
        [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]

    ::

        sage: n = lucas_number2(5,2,3); n
        2
        sage: type(n)
        <type 'sage.rings.integer.Integer'>
        sage: n = lucas_number2(5,2,-3/9); n
        418/9
        sage: type(n)
        <type 'sage.rings.rational.Rational'>

    The case P=1, Q=-1 is the Lucas sequence in Brualdi's Introductory
    Combinatorics, 4th ed., Prentice-Hall, 2004::

        sage: [lucas_number2(n,1,-1) for n in range(10)]
        [2, 1, 3, 4, 7, 11, 18, 29, 47, 76]
    """
    ans=gap.eval("Lucas(%s,%s,%s)[2]"%(QQ._coerce_(P),QQ._coerce_(Q),ZZ(n)))
    return sage_eval(ans)

def stirling_number1(n,k):
    """
    Returns the n-th Stilling number `S_1(n,k)` of the first
    kind (the number of permutations of n points with k cycles). Wraps
    GAP's Stirling1.

    EXAMPLES::

        sage: stirling_number1(3,2)
        3
        sage: stirling_number1(5,2)
        50
        sage: 9*stirling_number1(9,5)+stirling_number1(9,4)
        269325
        sage: stirling_number1(10,5)
        269325

    Indeed, `S_1(n,k) = S_1(n-1,k-1) + (n-1)S_1(n-1,k)`.
    """
    return ZZ(gap.eval("Stirling1(%s,%s)"%(ZZ(n),ZZ(k))))

def stirling_number2(n, k, algorithm=None):
    """
    Returns the n-th Stirling number `S_2(n,k)` of the second
    kind (the number of ways to partition a set of n elements into k
    pairwise disjoint nonempty subsets). (The n-th Bell number is the
    sum of the `S_2(n,k)`'s, `k=0,...,n`.)

    INPUT:

       *  ``n`` - nonnegative machine-size integer
       *  ``k`` - nonnegative machine-size integer
       * ``algorithm``:

         * None (default) - use native implementation
         * ``"maxima"`` - use Maxima's stirling2 function
         * ``"gap"`` - use GAP's Stirling2 function

    EXAMPLES:

    Print a table of the first several Stirling numbers of the second kind::

        sage: for n in range(10):
        ...       for k in range(10):
        ...           print str(stirling_number2(n,k)).rjust(k and 6),
        ...       print
        ...
        1      0      0      0      0      0      0      0      0      0
        0      1      0      0      0      0      0      0      0      0
        0      1      1      0      0      0      0      0      0      0
        0      1      3      1      0      0      0      0      0      0
        0      1      7      6      1      0      0      0      0      0
        0      1     15     25     10      1      0      0      0      0
        0      1     31     90     65     15      1      0      0      0
        0      1     63    301    350    140     21      1      0      0
        0      1    127    966   1701   1050    266     28      1      0
        0      1    255   3025   7770   6951   2646    462     36      1

    Stirling numbers satisfy `S_2(n,k) = S_2(n-1,k-1) + kS_2(n-1,k)`::

         sage: 5*stirling_number2(9,5) + stirling_number2(9,4)
         42525
         sage: stirling_number2(10,5)
         42525

    TESTS::

        sage: stirling_number2(500,501)
        0
        sage: stirling_number2(500,500)
        1
        sage: stirling_number2(500,499)
        124750
        sage: stirling_number2(500,498)
        7739801875
        sage: stirling_number2(500,497)
        318420320812125
        sage: stirling_number2(500,0)
        0
        sage: stirling_number2(500,1)
        1
        sage: stirling_number2(500,2)
        1636695303948070935006594848413799576108321023021532394741645684048066898202337277441635046162952078575443342063780035504608628272942696526664263794687
        sage: stirling_number2(500,3)
        6060048632644989473730877846590553186337230837666937173391005972096766698597315914033083073801260849147094943827552228825899880265145822824770663507076289563105426204030498939974727520682393424986701281896187487826395121635163301632473646
        sage: stirling_number2(500,30)
        13707767141249454929449108424328432845001327479099713037876832759323918134840537229737624018908470350134593241314462032607787062188356702932169472820344473069479621239187226765307960899083230982112046605340713218483809366970996051181537181362810003701997334445181840924364501502386001705718466534614548056445414149016614254231944272872440803657763210998284198037504154374028831561296154209804833852506425742041757849726214683321363035774104866182331315066421119788248419742922490386531970053376982090046434022248364782970506521655684518998083846899028416459701847828711541840099891244700173707021989771147674432503879702222276268661726508226951587152781439224383339847027542755222936463527771486827849728880
        sage: stirling_number2(500,31)
        5832088795102666690960147007601603328246123996896731854823915012140005028360632199516298102446004084519955789799364757997824296415814582277055514048635928623579397278336292312275467402957402880590492241647229295113001728653772550743446401631832152281610081188041624848850056657889275564834450136561842528589000245319433225808712628826136700651842562516991245851618481622296716433577650218003181535097954294609857923077238362717189185577756446945178490324413383417876364657995818830270448350765700419876347023578011403646501685001538551891100379932684279287699677429566813471166558163301352211170677774072447414719380996777162087158124939742564291760392354506347716119002497998082844612434332155632097581510486912
        sage: n = stirling_number2(20,11)
        sage: n
        1900842429486
        sage: type(n)
        <type 'sage.rings.integer.Integer'>
        sage: n = stirling_number2(20,11,algorithm='gap')
        sage: n
        1900842429486
        sage: type(n)
        <type 'sage.rings.integer.Integer'>
        sage: n = stirling_number2(20,11,algorithm='maxima')
        sage: n
        1900842429486
        sage: type(n)
        <type 'sage.rings.integer.Integer'>

     Sage's implementation splitting the computation of the Stirling
     numbers of the second kind in two cases according to `n`, let us
     check the result it gives agree with both maxima and gap.

     For `n<200`::

         sage: for n in Subsets(range(100,200), 5).random_element():
         ...      for k in Subsets(range(n), 5).random_element():
         ...         s_sage = stirling_number2(n,k)
         ...         s_maxima = stirling_number2(n,k, algorithm = "maxima")
         ...         s_gap = stirling_number2(n,k, algorithm = "gap")
         ...         if not (s_sage == s_maxima and s_sage == s_gap):
         ...             print "Error with n<200"

     For `n\geq 200`::

         sage: for n in Subsets(range(200,300), 5).random_element():
         ...      for k in Subsets(range(n), 5).random_element():
         ...         s_sage = stirling_number2(n,k)
         ...         s_maxima = stirling_number2(n,k, algorithm = "maxima")
         ...         s_gap = stirling_number2(n,k, algorithm = "gap")
         ...         if not (s_sage == s_maxima and s_sage == s_gap):
         ...             print "Error with n<200"


     TESTS:

     Checking an exception is raised whenever a wrong value is given
     for ``algorithm``::

         sage: s_sage = stirling_number2(50,3, algorithm = "CloudReading")
         Traceback (most recent call last):
         ...
         ValueError: unknown algorithm: CloudReading
     """
    if algorithm is None:
        return _stirling_number2(n, k)
    elif algorithm == 'gap':
        return ZZ(gap.eval("Stirling2(%s,%s)"%(ZZ(n),ZZ(k))))
    elif algorithm == 'maxima':
        return ZZ(maxima.eval("stirling2(%s,%s)"%(ZZ(n),ZZ(k))))
    else:
        raise ValueError("unknown algorithm: %s" % algorithm)

class CombinatorialObject(SageObject):
    def __init__(self, l):
        """
        CombinatorialObject provides a thin wrapper around a list. The main
        differences are that __setitem__ is disabled so that
        CombinatorialObjects are shallowly immutable, and the intention is
        that they are semantically immutable.

        Because of this, CombinatorialObjects provide a __hash__
        function which computes the hash of the string representation of a
        list and the hash of its parent's class. Thus, each
        CombinatorialObject should have a unique string representation.

        INPUT:

        -  ``l`` - a list or any object that can be convert to a list by
                   ``list``

        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: c == loads(dumps(c))
            True
            sage: c._list
            [1, 2, 3]
            sage: c._hash is None
            True
        """
        if isinstance(l, list):
            self._list = l
        else:
            self._list = list(l)
        self._hash = None

    def __str__(self):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: str(c)
            '[1, 2, 3]'
        """
        return str(self._list)

    def __cmp__(self, other):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: d = CombinatorialObject([3,2,1])
            sage: cmp(c, d)
            -1
            sage: cmp(d, c)
            1
            sage: cmp(c, c)
            0

        Check that :trac:`14065` is fixed::

            sage: from sage.structure.element import Element
            sage: class Foo(CombinatorialObject, Element): pass
            sage: L = [Foo([4-i]) for i in range(4)]; L
            [[4], [3], [2], [1]]
            sage: sorted(L, cmp)
            [[1], [2], [3], [4]]
            sage: f = Foo([4])
            sage: f == None
            False
            sage: f != None
            True

        .. WARNING::

            :class:`CombinatorialObject` must come **before** :class:`Element`
            for this to work becuase :class:`Element` is ahead of
            :class:`CombinatorialObject` in the MRO (method resolution
            order)::

                sage: from sage.structure.element import Element
                sage: class Bar(Element, CombinatorialObject):
                ...       def __init__(self, l):
                ...           CombinatorialObject.__init__(self, l)
                ...
                sage: L = [Bar([4-i]) for i in range(4)]
                sage: sorted(L, cmp)
                Traceback (most recent call last):
                ...
                NotImplementedError: BUG: sort algorithm for elements of 'None' not implemented
        """
        if isinstance(other, CombinatorialObject):
            return cmp(self._list, other._list)
        else:
            return cmp(self._list, other)

    def _repr_(self):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: c.__repr__()
            '[1, 2, 3]'
        """
        return self._list.__repr__()

    def __eq__(self, other):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: d = CombinatorialObject([2,3,4])
            sage: c == [1,2,3]
            True
            sage: c == [2,3,4]
            False
            sage: c == d
            False
        """

        if isinstance(other, CombinatorialObject):
            return self._list.__eq__(other._list)
        else:
            return self._list.__eq__(other)

    def __lt__(self, other):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: d = CombinatorialObject([2,3,4])
            sage: c < d
            True
            sage: c < [2,3,4]
            True
        """

        if isinstance(other, CombinatorialObject):
            return self._list.__lt__(other._list)
        else:
            return self._list.__lt__(other)

    def __le__(self, other):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: d = CombinatorialObject([2,3,4])
            sage: c <= c
            True
            sage: c <= d
            True
            sage: c <= [1,2,3]
            True
        """
        if isinstance(other, CombinatorialObject):
            return self._list.__le__(other._list)
        else:
            return self._list.__le__(other)

    def __gt__(self, other):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: d = CombinatorialObject([2,3,4])
            sage: c > c
            False
            sage: c > d
            False
            sage: c > [1,2,3]
            False
        """
        if isinstance(other, CombinatorialObject):
            return self._list.__gt__(other._list)
        else:
            return self._list.__gt__(other)

    def __ge__(self, other):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: d = CombinatorialObject([2,3,4])
            sage: c >= c
            True
            sage: c >= d
            False
            sage: c >= [1,2,3]
            True
        """
        if isinstance(other, CombinatorialObject):
            return self._list.__ge__(other._list)
        else:
            return self._list.__ge__(other)

    def __ne__(self, other):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: d = CombinatorialObject([2,3,4])
            sage: c != c
            False
            sage: c != d
            True
            sage: c != [1,2,3]
            False
        """
        if isinstance(other, CombinatorialObject):
            return self._list.__ne__(other._list)
        else:
            return self._list.__ne__(other)

    def __add__(self, other):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: c + [4]
            [1, 2, 3, 4]
            sage: type(_)
            <type 'list'>
        """
        return self._list + other

    def __hash__(self):
        """
        Computes the hash of self by computing the hash of the string
        representation of self._list. The hash is cached and stored in
        self._hash.

        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: c._hash is None
            True
            sage: hash(c) #random
            1335416675971793195
            sage: c._hash #random
            1335416675971793195
        """
        if self._hash is None:
            self._hash = str(self._list).__hash__()
        return self._hash

    def __nonzero__(self):
        """
        Return ``True`` if ``self`` is non-zero.

        We consider a list to be zero if it has length zero.

        TESTS::

            sage: c = CombinatorialObject([1,2,3])
            sage: not c
            False
            sage: c = CombinatorialObject([])
            sage: not c
            True

        Check that :trac:`14065` is fixed::

            sage: from sage.structure.element import Element
            sage: class Foo(CombinatorialObject, Element): pass
            ...
            sage: f = Foo([4])
            sage: not f
            False
            sage: f = Foo([])
            sage: not f
            True

        .. WARNING::

            :class:`CombinatorialObject` must come **before** :class:`Element`
            for this to work becuase :class:`Element` is ahead of
            :class:`CombinatorialObject` in the MRO (method resolution
            order)::

                sage: from sage.structure.element import Element
                sage: class Bar(Element, CombinatorialObject):
                ...       def __init__(self, l):
                ...           CombinatorialObject.__init__(self, l)
                ...
                sage: b = Bar([4])
                sage: not b
                Traceback (most recent call last):
                ...
                AttributeError: 'NoneType' object has no attribute 'zero_element'
        """
        return bool(self._list)

    def __len__(self):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: len(c)
            3
            sage: c.__len__()
            3
        """
        return self._list.__len__()

    def __getitem__(self, key):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: c[0]
            1
            sage: c[1:]
            [2, 3]
            sage: type(_)
            <type 'list'>
        """
        return self._list.__getitem__(key)

    def __iter__(self):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: list(iter(c))
            [1, 2, 3]
        """
        return self._list.__iter__()

    def __contains__(self, item):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: 1 in c
            True
            sage: 5 in c
            False
        """
        return self._list.__contains__(item)


    def index(self, key):
        """
        EXAMPLES::

            sage: c = CombinatorialObject([1,2,3])
            sage: c.index(1)
            0
            sage: c.index(3)
            2
        """
        return self._list.index(key)


from sage.misc.classcall_metaclass import ClasscallMetaclass
from sage.categories.enumerated_sets import EnumeratedSets
class CombinatorialClass(Parent):
    """
    This class is deprecated, and will disappear as soon as all derived
    classes in Sage's library will have been fixed. Please derive
    directly from Parent and use the category :class:`EnumeratedSets`,
    :class:`FiniteEnumeratedSets`, or :class:`InfiniteEnumeratedSets`, as
    appropriate.

    For examples, see::

        sage: FiniteEnumeratedSets().example()
        An example of a finite enumerated set: {1,2,3}
        sage: InfiniteEnumeratedSets().example()
        An example of an infinite enumerated set: the non negative integers
    """
    __metaclass__ = ClasscallMetaclass

    def __init__(self, category = None, *keys, **opts):
        """
        TESTS::

            sage: C = sage.combinat.combinat.CombinatorialClass()
            sage: C.category()
            Category of enumerated sets
            sage: C.__class__
            <class 'sage.combinat.combinat.CombinatorialClass_with_category'>
            sage: isinstance(C, Parent)
            True
            sage: C = sage.combinat.combinat.CombinatorialClass(category = FiniteEnumeratedSets())
            sage: C.category()
            Category of finite enumerated sets
        """
        Parent.__init__(self, category = EnumeratedSets().or_subcategory(category))


    def __len__(self):
        """
        __len__ has been removed ! to get the number of element in a
        combinatorial class, use .cardinality instead.


        TEST::

            sage: len(Partitions(5))
            Traceback (most recent call last):
            ...
            AttributeError: __len__ has been removed; use .cardinality() instead
        """
        raise AttributeError, "__len__ has been removed; use .cardinality() instead"

    def is_finite(self):
        """
        Returns whether self is finite or not.

        EXAMPLES::

            sage: Partitions(5).is_finite()
            True
            sage: Permutations().is_finite()
            False
        """
        from sage.rings.all import infinity
        return self.cardinality() != infinity

    def __getitem__(self, i):
        """
        Returns the combinatorial object of rank i.

        EXAMPLES::

            sage: p5 = Partitions(5)
            sage: p5[0]
            [5]
            sage: p5[6]
            [1, 1, 1, 1, 1]
            sage: p5[7]
            Traceback (most recent call last):
            ...
            ValueError: the value must be between 0 and 6 inclusive
        """
        return self.unrank(i)

    def __str__(self):
        """
        Returns a string representation of self.

        EXAMPLES::

            sage: str(Partitions(5))
            'Partitions of the integer 5'
        """
        return self.__repr__()

    def _repr_(self):
        """
        EXAMPLES::

            sage: repr(Partitions(5))   # indirect doctest
            'Partitions of the integer 5'
        """
        if hasattr(self, '_name') and self._name:
            return self._name
        else:
            return "Combinatorial Class -- REDEFINE ME!"

    def __contains__(self, x):
        """
        Tests whether or not the combinatorial class contains the object x.
        This raises a NotImplementedError as a default since _all_
        subclasses of CombinatorialClass should override this.

        Note that we could replace this with a default implementation that
        just iterates through the elements of the combinatorial class and
        checks for equality. However, since we use __contains__ for
        type checking, this operation should be cheap and should be
        implemented manually for each combinatorial class.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: x in C
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def __cmp__(self, x):
        """
        Compares two different combinatorial classes. For now, the
        comparison is done just on their repr's.

        EXAMPLES::

            sage: p5 = Partitions(5)
            sage: p6 = Partitions(6)
            sage: repr(p5) == repr(p6)
            False
            sage: p5 == p6
            False
        """
        return cmp(repr(self), repr(x))

    def __cardinality_from_iterator(self):
        """
        Default implementation of cardinality which just goes through the iterator
        of the combinatorial class to count the number of objects.

        EXAMPLES::

            sage: class C(CombinatorialClass):
            ...     def __iter__(self):
            ...          return iter([1,2,3])
            ...
            sage: C().cardinality() #indirect doctest
            3
        """
        c = Integer(0)
        one = Integer(1)
        for _ in self:
            c += one
        return c
    cardinality = __cardinality_from_iterator

    # __call__, element_class, and _element_constructor_ are poor
    # man's versions of those from Parent. This is for transition,
    # until all combinatorial classes are proper parents (in Parent)
    # and use coercion, etcc

    def __call__(self, x):
        """
        Returns x as an element of the combinatorial class's object class.

        EXAMPLES::

            sage: p5 = Partitions(5)
            sage: a = [2,2,1]
            sage: type(a)
            <type 'list'>
            sage: a = p5(a)
            sage: type(a)
            <class 'sage.combinat.partition.Partition_class'>
            sage: p5([2,1])
            Traceback (most recent call last):
            ...
            ValueError: [2, 1] not in Partitions of the integer 5
        """
        if x in self:
            return self._element_constructor_(x)
        else:
            raise ValueError, "%s not in %s"%(x, self)

    Element = CombinatorialObject # mostly for backward compatibility

    @lazy_attribute
    def element_class(self):
        """
        This function is a temporary helper so that a CombinatorialClass
        behaves as a parent for creating elements. This will disappear when
        combinatorial classes will be turned into actual parents (in the
        category EnumeratedSets).

        TESTS::

            sage: P5 = Partitions(5)
            sage: P5.element_class
            <class 'sage.combinat.partition.Partition_class'>
        """
        # assert not isinstance(self, Parent) # Raises an alert if we override the proper definition from Parent
        if hasattr(self, "object_class"):
            deprecation(5891, "Using object_class for specifying the class "
                        "of the elements of a combinatorial class is "
                        "deprecated. Please use Element instead.")
        return self.Element

    def _element_constructor_(self, x):
        """
        This function is a temporary helper so that a CombinatorialClass
        behaves as a parent for creating elements. This will disappear when
        combinatorial classes will be turned into actual parents (in the
        category EnumeratedSets).

        TESTS::

            sage: P5 = Partitions(5)
            sage: p = P5([3,2])      # indirect doctest
            sage: type(p)
            <class 'sage.combinat.partition.Partition_class'>
        """
        # assert not isinstance(self, Parent) # Raises an alert if we override the proper definition from Parent
        return self.element_class(x)

    def __list_from_iterator(self):
        """
        The default implementation of list which builds the list from the
        iterator.

        EXAMPLES::

            sage: class C(CombinatorialClass):
            ...     def __iter__(self):
            ...          return iter([1,2,3])
            ...
            sage: C().list() #indirect doctest
            [1, 2, 3]
        """
        return [x for x in self]

    #Set list to the default implementation
    list  = __list_from_iterator

    #Set the default object class to be CombinatorialObject
    Element = CombinatorialObject

    def __iterator_from_next(self):
        """
        An iterator to use when .first() and .next() are provided.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.first = lambda: 0
            sage: C.next  = lambda c: c+1
            sage: it = iter(C) # indirect doctest
            sage: [it.next() for _ in range(4)]
            [0, 1, 2, 3]
        """
        f = self.first()
        yield f
        while True:
            try:
                f = self.next(f)
            except (TypeError, ValueError ):
                break

            if f is None or f is False :
                break
            else:
                yield f

    def __iterator_from_previous(self):
        """
        An iterator to use when .last() and .previous() are provided. Note
        that this requires the combinatorial class to be finite. It is not
        recommended to implement combinatorial classes using last and
        previous.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.last = lambda: 4
            sage: def prev(c):
            ...       if c <= 1:
            ...           return None
            ...       else:
            ...           return c-1
            ...
            sage: C.previous  = prev
            sage: it = iter(C) # indirect doctest
            sage: [it.next() for _ in range(4)]
            [1, 2, 3, 4]
        """
        l = self.last()
        li = [l]
        while True:
            try:
                l = self.previous(l)
            except (TypeError, ValueError):
                break

            if l == None:
                break
            else:
                li.append(l)
        return reversed(li)

    def __iterator_from_unrank(self):
        """
        An iterator to use when .unrank() is provided.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: l = [1,2,3]
            sage: C.unrank = lambda c: l[c]
            sage: list(C) # indirect doctest
            [1, 2, 3]
        """
        r = 0
        u = self.unrank(r)
        yield u
        while True:
            r += 1
            try:
                u = self.unrank(r)
            except (TypeError, ValueError, IndexError):
                break

            if u == None:
                break
            else:
                yield u

    def __iterator_from_list(self):
        """
        An iterator to use when .list() is provided()

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.list = lambda: [1, 2, 3]
            sage: list(C) # indirect doctest
            [1, 2, 3]
        """
        for x in self.list():
            yield x

    def __iter__(self):
        """
        Allows the combinatorial class to be treated as an iterator. Default
        implementation.

        EXAMPLES::

            sage: p5 = Partitions(5)
            sage: [i for i in p5]
            [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]]
            sage: C = CombinatorialClass()
            sage: iter(C)
            Traceback (most recent call last):
            ...
            NotImplementedError: iterator called but not implemented
        """
        #Check to see if .first() and .next() are overridden in the subclass
        if ( self.first != self.__first_from_iterator and
             self.next  != self.__next_from_iterator ):
            return self.__iterator_from_next()
        #Check to see if .last() and .previous() are overridden in the subclass
        elif ( self.last != self.__last_from_iterator and
               self.previous != self.__previous_from_iterator):
            return self.__iterator_from_previous()
        #Check to see if .unrank() is overridden in the subclass
        elif self.unrank != self.__unrank_from_iterator:
            return self.__iterator_from_unrank()
        #Finally, check to see if .list() is overridden in the subclass
        elif self.list != self.__list_from_iterator:
            return self.__iterator_from_list()
        else:
            raise NotImplementedError, "iterator called but not implemented"

    def __unrank_from_iterator(self, r):
        """
        Default implementation of unrank which goes through the iterator.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.list = lambda: [1,2,3]
            sage: C.unrank(1) # indirect doctest
            2
        """
        counter = 0
        for u in self:
            if counter == r:
                return u
            counter += 1
        raise ValueError, "the value must be between %s and %s inclusive"%(0,counter-1)

    #Set the default implementation of unrank
    unrank = __unrank_from_iterator


    def __random_element_from_unrank(self):
        """
        Default implementation of random which uses unrank.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.list = lambda: [1,2,3]
            sage: C.random_element()       # indirect doctest
            1
        """
        c = self.cardinality()
        r = randint(0, c-1)
        return self.unrank(r)


    #Set the default implementation of random
    random_element = __random_element_from_unrank

    def random(self):
        """
        Deprecated. Use self.random_element() instead.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.random()
            Traceback (most recent call last):
            ...
            NotImplementedError: Deprecated: use random_element() instead
        """
        raise NotImplementedError, "Deprecated: use random_element() instead"

    def __rank_from_iterator(self, obj):
        """
        Default implementation of rank which uses iterator.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.list = lambda: [1,2,3]
            sage: C.rank(3) # indirect doctest
            2
        """
        r = 0
        for i in self:
            if i == obj:
                return r
            r += 1
        raise ValueError

    rank =  __rank_from_iterator

    def __first_from_iterator(self):
        """
        Default implementation for first which uses iterator.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.list = lambda: [1,2,3]
            sage: C.first() # indirect doctest
            1
        """
        for i in self:
            return i

    first = __first_from_iterator

    def __last_from_iterator(self):
        """
        Default implementation for first which uses iterator.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.list = lambda: [1,2,3]
            sage: C.last() # indirect doctest
            3
        """
        for i in self:
            pass
        return i

    last = __last_from_iterator

    def __next_from_iterator(self, obj):
        """
        Default implementation for next which uses iterator.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.list = lambda: [1,2,3]
            sage: C.next(2) # indirect doctest
            3
        """
        found = False
        for i in self:
            if found:
                return i
            if i == obj:
                found = True
        return None

    next = __next_from_iterator

    def __previous_from_iterator(self, obj):
        """
        Default implementation for next which uses iterator.

        EXAMPLES::

            sage: C = CombinatorialClass()
            sage: C.list = lambda: [1,2,3]
            sage: C.previous(2) # indirect doctest
            1
        """
        prev = None
        for i in self:
            if i == obj:
                break
            prev = i
        return prev

    previous = __previous_from_iterator

    def filter(self, f, name=None):
        """
        Returns the combinatorial subclass of f which consists of the
        elements x of self such that f(x) is True.

        EXAMPLES::

            sage: P = Permutations(3).filter(lambda x: x.avoids([1,2]))
            sage: P.list()
            [[3, 2, 1]]
        """
        return FilteredCombinatorialClass(self, f, name=name)

    def union(self, right_cc, name=None):
        """
        Returns the combinatorial class representing the union of self and
        right_cc.

        EXAMPLES::

            sage: P = Permutations(2).union(Permutations(1))
            sage: P.list()
            [[1, 2], [2, 1], [1]]
        """
        if not isinstance(right_cc, CombinatorialClass):
            raise TypeError, "right_cc must be a CombinatorialClass"
        return UnionCombinatorialClass(self, right_cc, name=name)

    def map(self, f, name=None):
        r"""
        Returns the image `\{f(x) | x \in \text{self}\}` of this combinatorial
        class by `f`, as a combinatorial class.

        `f` is supposed to be injective.

        EXAMPLES::

            sage: R = Permutations(3).map(attrcall('reduced_word')); R
            Image of Standard permutations of 3 by *.reduced_word()
            sage: R.cardinality()
            6
            sage: R.list()
            [[], [2], [1], [1, 2], [2, 1], [2, 1, 2]]
            sage: [ r for r in R]
            [[], [2], [1], [1, 2], [2, 1], [2, 1, 2]]

            If the function is not injective, then there may be repeated elements:
            sage: P = Partitions(4)
            sage: P.list()
            [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]
            sage: P.map(len).list()
            [1, 2, 2, 3, 4]

        TESTS::

            sage: R = Permutations(3).map(attrcall('reduced_word'))
            sage: R == loads(dumps(R))
            True
        """
        return MapCombinatorialClass(self, f, name)

class FilteredCombinatorialClass(CombinatorialClass):
    def __init__(self, combinatorial_class, f, name=None):
        """
        A filtered combinatorial class F is a subset of another
        combinatorial class C specified by a function f that takes in an
        element c of C and returns True if and only if c is in F.

        TESTS::

            sage: Permutations(3).filter(lambda x: x.avoids([1,2]))
            Filtered sublass of Standard permutations of 3
        """
        self.f = f
        self.combinatorial_class = combinatorial_class
        self._name = name

    def __repr__(self):
        """
        EXAMPLES::

            sage: P = Permutations(3).filter(lambda x: x.avoids([1,2]))
            sage: P.__repr__()
            'Filtered sublass of Standard permutations of 3'
            sage: P._name = 'Permutations avoiding [1, 2]'
            sage: P.__repr__()
            'Permutations avoiding [1, 2]'
        """
        if self._name:
            return self._name
        else:
            return "Filtered sublass of " + repr(self.combinatorial_class)

    def __contains__(self, x):
        """
        EXAMPLES::

            sage: P = Permutations(3).filter(lambda x: x.avoids([1,2]))
            sage: 'cat' in P
            False
            sage: [4,3,2,1] in P
            False
            sage: Permutation([1,2,3]) in P
            False
            sage: Permutation([3,2,1]) in P
            True
        """
        return x in self.combinatorial_class and self.f(x)

    def cardinality(self):
        """
        EXAMPLES::

            sage: P = Permutations(3).filter(lambda x: x.avoids([1,2]))
            sage: P.cardinality()
            1
        """
        c = 0
        for _ in self:
            c += 1
        return c

    def __iter__(self):
        """
        EXAMPLES::

            sage: P = Permutations(3).filter(lambda x: x.avoids([1,2]))
            sage: list(P)
            [[3, 2, 1]]
        """
        for x in self.combinatorial_class:
            if self.f(x):
                yield x

class UnionCombinatorialClass(CombinatorialClass):
    def __init__(self, left_cc, right_cc, name=None):
        """
        A UnionCombinatorialClass is a union of two other combinatorial
        classes.

        TESTS::

            sage: P = Permutations(3).union(Permutations(2))
            sage: P == loads(dumps(P))
            True
        """
        self.left_cc = left_cc
        self.right_cc = right_cc
        self._name = name

    def __repr__(self):
        """
        TESTS::

            sage: print repr(Permutations(3).union(Permutations(2)))
            Union combinatorial class of
                Standard permutations of 3
            and
                Standard permutations of 2
        """
        if self._name:
            return self._name
        else:
            return "Union combinatorial class of \n    %s\nand\n    %s"%(self.left_cc, self.right_cc)

    def __contains__(self, x):
        """
        EXAMPLES::

            sage: P = Permutations(3).union(Permutations(2))
            sage: [1,2] in P
            True
            sage: [3,2,1] in P
            True
            sage: [1,2,3,4] in P
            False
        """
        return x in self.left_cc or x in self.right_cc

    def cardinality(self):
        """
        EXAMPLES::

            sage: P = Permutations(3).union(Permutations(2))
            sage: P.cardinality()
            8
        """
        return self.left_cc.cardinality() + self.right_cc.cardinality()

    def list(self):
        """
        EXAMPLES::

            sage: P = Permutations(3).union(Permutations(2))
            sage: P.list()
            [[1, 2, 3],
             [1, 3, 2],
             [2, 1, 3],
             [2, 3, 1],
             [3, 1, 2],
             [3, 2, 1],
             [1, 2],
             [2, 1]]
        """
        return self.left_cc.list() + self.right_cc.list()


    def __iter__(self):
        """
        EXAMPLES::

            sage: P = Permutations(3).union(Permutations(2))
            sage: list(P)
            [[1, 2, 3],
             [1, 3, 2],
             [2, 1, 3],
             [2, 3, 1],
             [3, 1, 2],
             [3, 2, 1],
             [1, 2],
             [2, 1]]
        """
        for x in self.left_cc:
            yield x
        for x in self.right_cc:
            yield x

    def first(self):
        """
        EXAMPLES::

            sage: P = Permutations(3).union(Permutations(2))
            sage: P.first()
            [1, 2, 3]
        """
        return self.left_cc.first()

    def last(self):
        """
        EXAMPLES::

            sage: P = Permutations(3).union(Permutations(2))
            sage: P.last()
            [2, 1]
        """
        return self.right_cc.last()

    def rank(self, x):
        """
        EXAMPLES::

            sage: P = Permutations(3).union(Permutations(2))
            sage: P.rank(Permutation([2,1]))
            7
            sage: P.rank(Permutation([1,2,3]))
            0
        """
        try:
            return self.left_cc.rank(x)
        except (TypeError, ValueError):
            return self.left_cc.cardinality() + self.right_cc.rank(x)

    def unrank(self, x):
        """
        EXAMPLES::

            sage: P = Permutations(3).union(Permutations(2))
            sage: P.unrank(7)
            [2, 1]
            sage: P.unrank(0)
            [1, 2, 3]
        """
        try:
            return self.left_cc.unrank(x)
        except (TypeError, ValueError):
            return self.right_cc.unrank(x - self.left_cc.cardinality())


##############################################################################
class MapCombinatorialClass(CombinatorialClass):
    r"""
    A MapCombinatorialClass models the image of a combinatorial
    class through a function which is assumed to be injective

    See CombinatorialClass.map for examples
    """
    def __init__(self, cc, f, name=None):
        """
        TESTS::

            sage: Partitions(3).map(attrcall('conjugate'))
            Image of Partitions of the integer 3 by *.conjugate()
        """
        self.cc = cc
        self.f  = f
        self._name = name

    def __repr__(self):
        """
        TESTS::

            sage: Partitions(3).map(attrcall('conjugate'))
            Image of Partitions of the integer 3 by *.conjugate()

        """
        if self._name:
            return self._name
        else:
            return "Image of %s by %s"%(self.cc, self.f)

    def cardinality(self):
        """
        Returns the cardinality of this combinatorial class

        EXAMPLES::

            sage: R = Permutations(10).map(attrcall('reduced_word'))
            sage: R.cardinality()
            3628800

        """
        return self.cc.cardinality()

    def __iter__(self):
        """
        Returns an iterator over the elements of this combinatorial class

        EXAMPLES::

            sage: R = Permutations(10).map(attrcall('reduced_word'))
            sage: R.cardinality()
            3628800
        """
        for x in self.cc:
            yield self.f(x)

    def an_element(self):
        """
        Returns an element of this combinatorial class

        EXAMPLES::

            sage: R = SymmetricGroup(10).map(attrcall('reduced_word'))
            sage: R.an_element()
            [9, 8, 7, 6, 5, 4, 3, 2, 1]
        """
        return self.f(self.cc.an_element())

##############################################################################
from sage.rings.all import infinity
class InfiniteAbstractCombinatorialClass(CombinatorialClass):
    r"""
    This is an internal class that should not be used directly.  A class which
    inherits from InfiniteAbstractCombinatorialClass inherits the standard
    methods list and count.

    If self._infinite_cclass_slice exists then self.__iter__ returns an
    iterator for self, otherwise raise NotImplementedError. The method
    self._infinite_cclass_slice is supposed to accept any integer as an
    argument and return something which is iterable.
    """
    def cardinality(self):
        """
        Counts the elements of the combinatorial class.

        EXAMPLES:
            sage: R = InfiniteAbstractCombinatorialClass()
            sage: R.cardinality()
            +Infinity
        """
        return infinity

    def list(self):
        """
        Returns an error since self is an infinite combinatorial class.

        EXAMPLES:
            sage: R = InfiniteAbstractCombinatorialClass()
            sage: R.list()
            Traceback (most recent call last):
            ...
            NotImplementedError: infinite list
        """
        raise NotImplementedError, "infinite list"

    def __iter__(self):
        """
        Returns an iterator for the infinite combinatorial class self if
        possible or raise a NotImplementedError.

        EXAMPLES:
            sage: R = InfiniteAbstractCombinatorialClass()
            sage: iter(R).next()
            Traceback (most recent call last):
            ...
            NotImplementedError

            sage: c = iter(Compositions()) # indirect doctest
            sage: c.next(), c.next(), c.next(), c.next(), c.next(), c.next()
            ([], [1], [1, 1], [2], [1, 1, 1], [1, 2])
            sage: c.next(), c.next(), c.next(), c.next(), c.next(), c.next()
            ([2, 1], [3], [1, 1, 1, 1], [1, 1, 2], [1, 2, 1], [1, 3])
        """
        try:
            finite = self._infinite_cclass_slice
        except AttributeError:
            raise NotImplementedError
        i = 0
        while True:
            for c in finite(i):
                yield c
            i+=1



def hurwitz_zeta(s,x,N):
    """
    Returns the value of the `\zeta(s,x)` to `N`
    decimals, where s and x are real.

    The Hurwitz zeta function is one of the many zeta functions. It
    defined as

    .. math::

             \zeta(s,x) = \sum_{k=0}^\infty (k+x)^{-s}.


    When `x = 1`, this coincides with Riemann's zeta function.
    The Dirichlet L-functions may be expressed as a linear combination
    of Hurwitz zeta functions.

    Note that if you use floating point inputs, then the results may be
    slightly off.

    EXAMPLES::

        sage: hurwitz_zeta(3,1/2,6)
        8.41439000000000
        sage: hurwitz_zeta(11/10,1/2,6)
        12.1041000000000
        sage: hurwitz_zeta(11/10,1/2,50)
        12.10381349568375510570907741296668061903364861809

    REFERENCES:

    - http://en.wikipedia.org/wiki/Hurwitz_zeta_function
    """
    maxima.eval('load ("bffac")')
    s = maxima.eval("bfhzeta (%s,%s,%s)"%(s,x,N))

    #Handle the case where there is a 'b' in the string
    #'1.2000b0' means 1.2000 and
    #'1.2000b1' means 12.000
    i = s.rfind('b')
    if i == -1:
        return sage_eval(s)
    else:
        if s[i+1:] == '0':
            return sage_eval(s[:i])
        else:
            return sage_eval(s[:i])*10**sage_eval(s[i+1:])

    return s  ## returns an odd string


#####################################################
#### combinatorial sets/lists

def combinations(mset,k):
    r"""
    A combination of a multiset (a list of objects which may contain
    the same object several times) mset is an unordered selection
    without repetitions and is represented by a sorted sublist of ``mset``.
    Returns the set of all combinations of the multiset ``mset`` with ``k``
    elements.

    INPUT:

    - ``mset`` -- (list) the multiset presented as a list of objects.

    - ``k`` -- (integer) the size of each set.

    .. NOTE::

        This function is deprecated in favor of
        :func:`sage.combinat.combination.Combinations`. Use
        ``Combinations(mset, k).list()`` directly to get the list of
        combinations of ``mset``.

    EXAMPLES::

        sage: combinations([1,2,3], 2)
        doctest:...: DeprecationWarning: Use Combinations(mset,k).list()
        instead. See http://trac.sagemath.org/13821 for details.
        [[1, 2], [1, 3], [2, 3]]
        sage: mset = [1,1,2,3,4,4,5]
        sage: combinations(mset,2)
        [[1, 1],
         [1, 2],
         [1, 3],
         [1, 4],
         [1, 5],
         [2, 3],
         [2, 4],
         [2, 5],
         [3, 4],
         [3, 5],
         [4, 4],
         [4, 5]]
         sage: mset = ["d","a","v","i","d"]
         sage: combinations(mset,3)
         [['d', 'd', 'a'],
         ['d', 'd', 'v'],
         ['d', 'd', 'i'],
         ['d', 'a', 'v'],
         ['d', 'a', 'i'],
         ['d', 'v', 'i'],
         ['a', 'v', 'i']]

    It is possible to take combinations of Sage objects::

        sage: combinations([vector([1,1]), vector([2,2]), vector([3,3])], 2)
        [[(1, 1), (2, 2)], [(1, 1), (3, 3)], [(2, 2), (3, 3)]]
    """
    from sage.combinat.combination import Combinations
    deprecation(13821, 'Use Combinations(mset,k).list() instead.')
    return Combinations(mset, k).list()

def combinations_iterator(mset, k=None):
    """
    An iterator for combinations of the elements of a multiset ``mset``.

    INPUT:

    - ``mset`` -- (list) the multiset presented as a list of objects.

    - ``k`` -- (integer, default: None) the size of each set.

    .. NOTE::

        This function is deprecated in favor of
        :func:`sage.combinat.combination.Combinations`. Use
        ``Combinations(mset, k)`` instead.

    EXAMPLES::

        sage: X = combinations_iterator([1,2,3,4,5],3)
        doctest:...: DeprecationWarning: Use Combinations(mset,k) instead.
        See http://trac.sagemath.org/13821 for details.
        sage: [x for x in X]
        [[1, 2, 3],
         [1, 2, 4],
         [1, 2, 5],
         [1, 3, 4],
         [1, 3, 5],
         [1, 4, 5],
         [2, 3, 4],
         [2, 3, 5],
         [2, 4, 5],
         [3, 4, 5]]
    """
    # It is not possible to use deprecated_function_alias since it leads to
    # a circular import of combinat from combination and
    # combination.Combinations from combinat.
    from sage.combinat.combination import Combinations
    deprecation(13821, 'Use Combinations(mset,k) instead.')
    return Combinations(mset, k)

def number_of_combinations(mset,k):
    """
    Returns the size of combinations(mset,k). IMPLEMENTATION: Wraps
    GAP's NrCombinations.

    EXAMPLES::

        sage: mset = [1,1,2,3,4,4,5]
        sage: number_of_combinations(mset,2)
        doctest:1: DeprecationWarning: Use Combinations(mset,k).cardinality() instead.
        See http://trac.sagemath.org/14138 for details.
        12
    """
    from sage.combinat.combination import Combinations
    deprecation(14138, 'Use Combinations(mset,k).cardinality() instead.')
    return Combinations(mset,k).cardinality()

def arrangements(mset,k):
    r"""
    An arrangement of ``mset`` is an ordered selection without repetitions
    and is represented by a list that contains only elements from mset,
    but maybe in a different order.

    ``arrangements`` returns the set of arrangements of the
    multiset ``mset`` that contain ``k`` elements.

    INPUT:

    - ``mset`` -- (list) the multiset presented as a list of objects.

    - ``k`` -- (integer) the size of each set.

    .. NOTE::

        This function is deprecated in favor of
        :func:`sage.combinat.permutation.Arrangements`. Use
        ``Arrangements(mset, k).list()`` directly to get the list of
        arrangements of ``mset``.

    EXAMPLES::

        sage: arrangements([1,2,3], 2)
        doctest:...: DeprecationWarning: Use Arrangements(mset,k).list()
        instead. See http://trac.sagemath.org/13821 for details.
        [[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]]
        sage: mset = [1,1,2,3,4,4,5]
        sage: arrangements(mset,2)
        [[1, 1],
         [1, 2],
         [1, 3],
         [1, 4],
         [1, 5],
         [2, 1],
         [2, 3],
         [2, 4],
         [2, 5],
         [3, 1],
         [3, 2],
         [3, 4],
         [3, 5],
         [4, 1],
         [4, 2],
         [4, 3],
         [4, 4],
         [4, 5],
         [5, 1],
         [5, 2],
         [5, 3],
         [5, 4]]
         sage: arrangements( ["c","a","t"], 2 )
         [['c', 'a'], ['c', 't'], ['a', 'c'],
          ['a', 't'], ['t', 'c'], ['t', 'a']]
         sage: arrangements( ["c","a","t"], 3 )
         [['c', 'a', 't'], ['c', 't', 'a'], ['a', 'c', 't'],
          ['a', 't', 'c'], ['t', 'c', 'a'], ['t', 'a', 'c']]
    """
    from sage.combinat.permutation import Arrangements
    deprecation(13821, 'Use Arrangements(mset,k).list() instead.')
    return Arrangements(mset, k).list()

def number_of_arrangements(mset,k):
    """
    Returns the size of arrangements(mset,k).

    EXAMPLES::

        sage: mset = [1,1,2,3,4,4,5]
        sage: number_of_arrangements(mset,2)
        doctest:1: DeprecationWarning: Use Arrangements(mset,k).cardinality() instead.
        See http://trac.sagemath.org/14138 for details.
        22
    """
    from sage.combinat.permutation import Arrangements
    deprecation(14138, 'Use Arrangements(mset,k).cardinality() instead.')
    return Arrangements(mset, k).cardinality()

def derangements(mset):
    """
    A derangement is a fixed point free permutation of list and is
    represented by a list that contains exactly the same elements as
    mset, but possibly in different order. Derangements returns the set
    of all derangements of a multiset.

    Wraps GAP's Derangements.

    .. warning::

       Wraps GAP - hence mset must be a list of objects that have
       string representations that can be interpreted by the GAP
       interpreter. If mset consists of at all complicated Sage
       objects, this function does *not* do what you expect. A proper
       function should be written! (TODO!)

    EXAMPLES::

        sage: mset = [1,2,3,4]
        sage: derangements(mset)
        [[2, 1, 4, 3],
         [2, 3, 4, 1],
         [2, 4, 1, 3],
         [3, 1, 4, 2],
         [3, 4, 1, 2],
         [3, 4, 2, 1],
         [4, 1, 2, 3],
         [4, 3, 1, 2],
         [4, 3, 2, 1]]
         sage: derangements(["c","a","t"])
         ['atc', 'tca']
    """
    ans=gap.eval("Derangements(%s)"%mset)
    return eval(ans)

def number_of_derangements(mset):
    """
    Returns the size of derangements(mset). Wraps GAP's
    NrDerangements.

    EXAMPLES::

        sage: mset = [1,2,3,4]
        sage: number_of_derangements(mset)
        9
    """
    ans=gap.eval("NrDerangements(%s)"%mset)
    return ZZ(ans)

def tuples(S,k):
    """
    An ordered tuple of length k of set is an ordered selection with
    repetition and is represented by a list of length k containing
    elements of set. tuples returns the set of all ordered tuples of
    length k of the set.

    EXAMPLES::

        sage: S = [1,2]
        sage: tuples(S,3)
        [[1, 1, 1], [2, 1, 1], [1, 2, 1], [2, 2, 1], [1, 1, 2], [2, 1, 2], [1, 2, 2], [2, 2, 2]]
        sage: mset = ["s","t","e","i","n"]
        sage: tuples(mset,2)
        [['s', 's'], ['t', 's'], ['e', 's'], ['i', 's'], ['n', 's'], ['s', 't'], ['t', 't'],
         ['e', 't'], ['i', 't'], ['n', 't'], ['s', 'e'], ['t', 'e'], ['e', 'e'], ['i', 'e'],
         ['n', 'e'], ['s', 'i'], ['t', 'i'], ['e', 'i'], ['i', 'i'], ['n', 'i'], ['s', 'n'],
         ['t', 'n'], ['e', 'n'], ['i', 'n'], ['n', 'n']]

    The Set(...) comparisons are necessary because finite fields are
    not enumerated in a standard order.

    ::

        sage: K.<a> = GF(4, 'a')
        sage: mset = [x for x in K if x!=0]
        sage: tuples(mset,2)
        [[a, a], [a + 1, a], [1, a], [a, a + 1], [a + 1, a + 1], [1, a + 1], [a, 1], [a + 1, 1], [1, 1]]

    AUTHORS:

    - Jon Hanke (2006-08)
    """
    import copy
    if k<=0:
        return [[]]
    if k==1:
        return [[x] for x in S]
    ans = []
    for s in S:
        for x in tuples(S,k-1):
            y = copy.copy(x)
            y.append(s)
            ans.append(y)
    return ans

def number_of_tuples(S,k):
    """
    Returns the size of tuples(S,k). Wraps GAP's NrTuples.

    EXAMPLES::

        sage: S = [1,2,3,4,5]
        sage: number_of_tuples(S,2)
        25
        sage: S = [1,1,2,3,4,5]
        sage: number_of_tuples(S,2)
        25
    """
    ans=gap.eval("NrTuples(%s,%s)"%(S,ZZ(k)))
    return ZZ(ans)

def unordered_tuples(S,k):
    """
    An unordered tuple of length k of set is a unordered selection with
    repetitions of set and is represented by a sorted list of length k
    containing elements from set.

    unordered_tuples returns the set of all unordered tuples of length
    k of the set. Wraps GAP's UnorderedTuples.

    .. warning::

       Wraps GAP - hence mset must be a list of objects that have
       string representations that can be interpreted by the GAP
       interpreter. If mset consists of at all complicated Sage
       objects, this function does *not* do what you expect. A proper
       function should be written! (TODO!)

    EXAMPLES::

        sage: S = [1,2]
        sage: unordered_tuples(S,3)
        [[1, 1, 1], [1, 1, 2], [1, 2, 2], [2, 2, 2]]
        sage: unordered_tuples(["a","b","c"],2)
        ['aa', 'ab', 'ac', 'bb', 'bc', 'cc']
    """
    ans=gap.eval("UnorderedTuples(%s,%s)"%(S,ZZ(k)))
    return eval(ans)

def number_of_unordered_tuples(S,k):
    """
    Returns the size of unordered_tuples(S,k). Wraps GAP's
    NrUnorderedTuples.

    EXAMPLES::

        sage: S = [1,2,3,4,5]
        sage: number_of_unordered_tuples(S,2)
        15
    """
    ans=gap.eval("NrUnorderedTuples(%s,%s)"%(S,ZZ(k)))
    return ZZ(ans)

def permutations(mset):
    """
    A permutation is represented by a list that contains exactly the
    same elements as mset, but possibly in different order. If mset is
    a proper set there are `|mset| !` such permutations.
    Otherwise if the first elements appears `k_1` times, the
    second element appears `k_2` times and so on, the number
    of permutations is `|mset|! / (k_1! k_2! \ldots)`, which
    is sometimes called a multinomial coefficient.

    permutations returns the set of all permutations of a multiset.
    Calls a function written by Mike Hansen, not GAP.

    EXAMPLES::

        sage: mset = [1,1,2,2,2]
        sage: permutations(mset)
        [[1, 1, 2, 2, 2],
         [1, 2, 1, 2, 2],
         [1, 2, 2, 1, 2],
         [1, 2, 2, 2, 1],
         [2, 1, 1, 2, 2],
         [2, 1, 2, 1, 2],
         [2, 1, 2, 2, 1],
         [2, 2, 1, 1, 2],
         [2, 2, 1, 2, 1],
         [2, 2, 2, 1, 1]]
        sage: MS = MatrixSpace(GF(2),2,2)
        sage: A = MS([1,0,1,1])
        sage: permutations(A.rows())
        [[(1, 0), (1, 1)], [(1, 1), (1, 0)]]
    """
    from sage.combinat.permutation import Permutations
    ans = Permutations(mset)
    return ans.list()

def permutations_iterator(mset,n=None):
    """
    Do not use this function. It will be deprecated in future version
    of Sage and eventually removed. Use Permutations instead; instead
    of

    for p in permutations_iterator(range(1, m+1), n)

    use

    for p in Permutations(m, n).

    Note that Permutations, unlike this function, treats repeated
    elements as identical.

    If you insist on using this now:

    Returns an iterator (http://docs.python.org/lib/typeiter.html)
    which can be used in place of permutations(mset) if all you need it
    for is a 'for' loop.

    Posted by Raymond Hettinger, 2006/03/23, to the Python Cookbook:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/474124

    Note- This function considers repeated elements as different
    entries, so for example::

        sage: from sage.combinat.combinat import permutations, permutations_iterator
        sage: mset = [1,2,2]
        sage: permutations(mset)
        [[1, 2, 2], [2, 1, 2], [2, 2, 1]]
        sage: for p in permutations_iterator(mset): print p
        doctest:1: DeprecationWarning: Use the Permutations object instead.
        See http://trac.sagemath.org/14138 for details.
        [1, 2, 2]
        [2, 1, 2]
        [2, 2, 1]
        [2, 1, 2]
        [2, 2, 1]

    EXAMPLES::

        sage: X = permutations_iterator(range(3),2)
        sage: [x for x in X]
        [[0, 1], [0, 2], [1, 0], [1, 2], [2, 0], [2, 1]]
    """
    deprecation(14138, 'Use the Permutations object instead.')
    items = mset
    if n is None:
        n = len(items)
    from sage.combinat.permutation import Permutations
    for i in range(len(items)):
        v = items[i:i+1]
        if n == 1:
            yield v
        else:
            rest = items[:i] + items[i+1:]
            for p in Permutations(rest, n-1):
                yield v + p

def number_of_permutations(mset):
    """
    Do not use this function. It will be deprecated in future version
    of Sage and eventually removed. Use Permutations instead; instead
    of

    number_of_permutations(mset)

    use

    Permutations(mset).cardinality().

    If you insist on using this now:

    Returns the size of permutations(mset).

    AUTHORS:

    - Robert L. Miller

    EXAMPLES::

        sage: mset = [1,1,2,2,2]
        sage: number_of_permutations(mset)
        doctest:1: DeprecationWarning: Use the Permutations object instead.
        See http://trac.sagemath.org/14138 for details.
        10
    """
    deprecation(14138, 'Use the Permutations object instead.')
    from sage.combinat.permutation import Permutations
    return Permutations(mset).cardinality()

def cyclic_permutations(mset):
    """
    Returns a list of all cyclic permutations of mset. Treats mset as a
    list, not a set, i.e. entries with the same value are distinct.

    AUTHORS:

    - Emily Kirkman

    EXAMPLES::

        sage: from sage.combinat.combinat import cyclic_permutations, cyclic_permutations_iterator
        sage: cyclic_permutations(range(4))
        [[0, 1, 2, 3], [0, 1, 3, 2], [0, 2, 1, 3], [0, 2, 3, 1], [0, 3, 1, 2], [0, 3, 2, 1]]
        sage: for cycle in cyclic_permutations(['a', 'b', 'c']):
        ...       print cycle
        ['a', 'b', 'c']
        ['a', 'c', 'b']

    Since :trac:`14138` some repetitions are handled as expected::

        sage: cyclic_permutations([1,1,1])
        [[1, 1, 1]]
    """
    return list(cyclic_permutations_iterator(mset))

def cyclic_permutations_iterator(mset):
    """
    Iterates over all cyclic permutations of mset in cycle notation.
    Treats mset as a list, not a set, i.e. entries with the same value
    are distinct.

    AUTHORS:

    - Emily Kirkman

    EXAMPLES::

        sage: from sage.combinat.combinat import cyclic_permutations, cyclic_permutations_iterator
        sage: cyclic_permutations(range(4))
        [[0, 1, 2, 3], [0, 1, 3, 2], [0, 2, 1, 3], [0, 2, 3, 1], [0, 3, 1, 2], [0, 3, 2, 1]]
        sage: for cycle in cyclic_permutations(['a', 'b', 'c']):
        ...       print cycle
        ['a', 'b', 'c']
        ['a', 'c', 'b']

    Since :trac:`14138` some repetitions are handled as expected::

        sage: cyclic_permutations([1,1,1])
        [[1, 1, 1]]
    """
    if len(mset) > 2:
        from sage.combinat.permutation import Permutations

        for perm in Permutations(mset[1:]):
            yield [mset[0]] + perm
    else:
        yield mset

def bell_polynomial(n, k):
    r"""
    This function returns the Bell Polynomial

    .. math::

       B_{n,k}(x_1, x_2, \ldots, x_{n-k+1}) = \sum_{\sum{j_i}=k, \sum{i j_i}
       =n} \frac{n!}{j_1!j_2!\ldots} \frac{x_1}{1!}^j_1 \frac{x_2}{2!}^j_2
       \ldots

    INPUT:

    - ``n`` - integer

    - ``k`` - integer

    OUTPUT:

    - polynomial expression (SymbolicArithmetic)

    EXAMPLES::

        sage: bell_polynomial(6,2)
        10*x_3^2 + 15*x_2*x_4 + 6*x_1*x_5
        sage: bell_polynomial(6,3)
        15*x_2^3 + 60*x_1*x_2*x_3 + 15*x_1^2*x_4

    REFERENCES:

    - E.T. Bell, "Partition Polynomials"

    AUTHORS:

    - Blair Sutton (2009-01-26)
    """
    from sage.combinat.partition import Partitions
    from sage.rings.arith import factorial
    vars = ZZ[tuple(['x_'+str(i) for i in range(1, n-k+2)])].gens()
    result = 0
    for p in Partitions(n, length=k):
        factorial_product  = 1
        power_factorial_product = 1
        for part, count in p.to_exp_dict().iteritems():
            factorial_product *= factorial(count)
            power_factorial_product *= factorial(part)**count

        coefficient = factorial(n) / (factorial_product * power_factorial_product)
        result += coefficient *  prod([vars[i-1] for i in p])

    return result

def fibonacci_sequence(start, stop=None, algorithm=None):
    r"""
    Returns an iterator over the Fibonacci sequence, for all fibonacci
    numbers `f_n` from ``n = start`` up to (but
    not including) ``n = stop``

    INPUT:


    -  ``start`` - starting value

    -  ``stop`` - stopping value

    -  ``algorithm`` - default (None) - passed on to
       fibonacci function (or not passed on if None, i.e., use the
       default).


    EXAMPLES::

        sage: fibs = [i for i in fibonacci_sequence(10, 20)]
        sage: fibs
        [55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181]

    ::

        sage: sum([i for i in fibonacci_sequence(100, 110)])
        69919376923075308730013

    .. seealso::

       :func:`fibonacci_xrange`

    AUTHORS:

    - Bobby Moretti
    """
    if stop is None:
        stop = ZZ(start)
        start = ZZ(0)
    else:
        start = ZZ(start)
        stop = ZZ(stop)

    if algorithm:
        for n in xrange(start, stop):
            yield fibonacci(n, algorithm=algorithm)
    else:
        for n in xrange(start, stop):
            yield fibonacci(n)

def fibonacci_xrange(start, stop=None, algorithm='pari'):
    r"""
    Returns an iterator over all of the Fibonacci numbers in the given
    range, including ``f_n = start`` up to, but not
    including, ``f_n = stop``.

    EXAMPLES::

        sage: fibs_in_some_range =  [i for i in fibonacci_xrange(10^7, 10^8)]
        sage: len(fibs_in_some_range)
        4
        sage: fibs_in_some_range
        [14930352, 24157817, 39088169, 63245986]

    ::

        sage: fibs = [i for i in fibonacci_xrange(10, 100)]
        sage: fibs
        [13, 21, 34, 55, 89]

    ::

        sage: list(fibonacci_xrange(13, 34))
        [13, 21]

    A solution to the second Project Euler problem::

        sage: sum([i for i in fibonacci_xrange(10^6) if is_even(i)])
        1089154

    .. seealso::

       :func:`fibonacci_sequence`

    AUTHORS:

    - Bobby Moretti
    """
    if stop is None:
        stop = ZZ(start)
        start = ZZ(0)
    else:
        start = ZZ(start)
        stop = ZZ(stop)

    # iterate until we've gotten high enough
    fn = 0
    n = 0
    while fn < start:
        n += 1
        fn = fibonacci(n)

    while True:
        fn = fibonacci(n)
        n += 1
        if fn < stop:
            yield fn
        else:
            return

def bernoulli_polynomial(x, n):
    r"""
    Return the nth Bernoulli polynomial evaluated at x.

    The generating function for the Bernoulli polynomials is

    .. math::

       \frac{t e^{xt}}{e^t-1}= \sum_{n=0}^\infty B_n(x) \frac{t^n}{n!},

    and they are given directly by

    .. math::

       B_n(x) = \sum_{i=0}^n \binom{n}{i}B_{n-i}x^i.

    One has `B_n(x) = - n\zeta(1 - n,x)`, where
    `\zeta(s,x)` is the Hurwitz zeta function. Thus, in a
    certain sense, the Hurwitz zeta function generalizes the
    Bernoulli polynomials to non-integer values of n.

    EXAMPLES::

        sage: y = QQ['y'].0
        sage: bernoulli_polynomial(y, 5)
        y^5 - 5/2*y^4 + 5/3*y^3 - 1/6*y
        sage: bernoulli_polynomial(y, 5)(12)
        199870
        sage: bernoulli_polynomial(12, 5)
        199870
        sage: bernoulli_polynomial(y^2 + 1, 5)
        y^10 + 5/2*y^8 + 5/3*y^6 - 1/6*y^2
        sage: P.<t> = ZZ[]
        sage: p = bernoulli_polynomial(t, 6)
        sage: p.parent()
        Univariate Polynomial Ring in t over Rational Field

    We verify an instance of the formula which is the origin of
    the Bernoulli polynomials (and numbers)::

        sage: power_sum = sum(k^4 for k in range(10))
        sage: 5*power_sum == bernoulli_polynomial(10, 5) - bernoulli(5)
        True


    REFERENCES:

    - http://en.wikipedia.org/wiki/Bernoulli_polynomials
    """
    try:
        n = ZZ(n)
        if n < 0:
            raise TypeError
    except TypeError:
        raise ValueError, "The second argument must be a non-negative integer"

    if n == 0:
        return ZZ(1)

    if n == 1:
        return x - ZZ(1)/2

    k = n.mod(2)
    coeffs = [0]*k + sum(([binomial(n, i)*bernoulli(n-i), 0]
                          for i in range(k, n+1, 2)), [])
    coeffs[-3] = -n/2

    if isinstance(x, Polynomial):
        try:
            return x.parent()(coeffs)(x)
        except TypeError:
            pass

    x2 = x*x
    xi = x**k
    s = 0
    for i in range(k, n-1, 2):
        s += coeffs[i]*xi
        t = xi
        xi *= x2
    s += xi - t*x*n/2
    return s
