r"""
Partitions

A partition `p` of a nonnegative integer `n` is a
non-increasing list of positive integers (the *parts* of the
partition) with total sum `n`.

A partition can be depicted by a diagram made of rows of cells,
where the number of cells in the `i^{th}` row starting from
the top is the `i^{th}` part of the partition.

The coordinate system related to a partition applies from the top
to the bottom and from left to right. So, the corners of the
partition are [[0,4], [1,2], [2,0]].

AUTHORS:

- Mike Hansen (2007): initial version

- Dan Drake (2009-03-28): deprecate RestrictedPartitions and implement
  Partitions_parts_in

- Travis Scrimshaw (2012-01-12): Implemented latex function to Partition_class
- Travis Scrimshaw (2012-05-09): Fixed Partitions(-1).list() infinite recursion
  loop by saying Partitions_n is the empty set.

- Travis Scrimshaw (2012-05-11): Fixed bug in inner where if the length was
  longer than the length of the inner partition, it would include 0's.

EXAMPLES:

There are 5 partitions of the integer 4::

    sage: Partitions(4).cardinality()
    5
    sage: Partitions(4).list()
    [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]

We can use the method .first() to get the 'first' partition of a
number::

    sage: Partitions(4).first()
    [4]

Using the method .next(), we can calculate the 'next' partition.
When we are at the last partition, None will be returned::

    sage: Partitions(4).next([4])
    [3, 1]
    sage: Partitions(4).next([1,1,1,1]) is None
    True

We can use ``iter`` to get an object which iterates over the partitions one
by one to save memory.  Note that when we do something like
``for part in Partitions(4)`` this iterator is used in the background::

    sage: g = iter(Partitions(4))

::

    sage: g.next()
    [4]
    sage: g.next()
    [3, 1]
    sage: g.next()
    [2, 2]
    sage: for p in Partitions(4): print p
    [4]
    [3, 1]
    [2, 2]
    [2, 1, 1]
    [1, 1, 1, 1]

We can add constraints to to the type of partitions we want. For
example, to get all of the partitions of 4 of length 2, we'd do the
following::

    sage: Partitions(4, length=2).list()
    [[3, 1], [2, 2]]

Here is the list of partitions of length at least 2 and the list of
ones with length at most 2::

    sage: Partitions(4, min_length=2).list()
    [[3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]
    sage: Partitions(4, max_length=2).list()
    [[4], [3, 1], [2, 2]]

The options min_part and max_part can be used to set constraints
on the sizes of all parts. Using max_part, we can select
partitions having only 'small' entries. The following is the list
of the partitions of 4 with parts at most 2::

    sage: Partitions(4, max_part=2).list()
    [[2, 2], [2, 1, 1], [1, 1, 1, 1]]

The min_part options is complementary to max_part and selects
partitions having only 'large' parts. Here is the list of all
partitions of 4 with each part at least 2::

    sage: Partitions(4, min_part=2).list()
    [[4], [2, 2]]

The options inner and outer can be used to set part-by-part
constraints. This is the list of partitions of 4 with [3, 1, 1] as
an outer bound::

    sage: Partitions(4, outer=[3,1,1]).list()
    [[3, 1], [2, 1, 1]]

Outer sets max_length to the length of its argument. Moreover, the
parts of outer may be infinite to clear constraints on specific
parts. Here is the list of the partitions of 4 of length at most 3
such that the second and third part are 1 when they exist::

    sage: Partitions(4, outer=[oo,1,1]).list()
    [[4], [3, 1], [2, 1, 1]]

Finally, here are the partitions of 4 with [1,1,1] as an inner
bound. Note that inner sets min_length to the length of its
argument::

    sage: Partitions(4, inner=[1,1,1]).list()
    [[2, 1, 1], [1, 1, 1, 1]]

The options min_slope and max_slope can be used to set
constraints on the slope, that is on the difference p[i+1]-p[i] of
two consecutive parts. Here is the list of the strictly decreasing
partitions of 4::

    sage: Partitions(4, max_slope=-1).list()
    [[4], [3, 1]]

The constraints can be combined together in all reasonable ways.
Here are all the partitions of 11 of length between 2 and 4 such
that the difference between two consecutive parts is between -3 and
-1::

    sage: Partitions(11,min_slope=-3,max_slope=-1,min_length=2,max_length=4).list()
    [[7, 4], [6, 5], [6, 4, 1], [6, 3, 2], [5, 4, 2], [5, 3, 2, 1]]

Partition objects can also be created individually with the
Partition function::

    sage: Partition([2,1])
    [2, 1]

Once we have a partition object, then there are a variety of
methods that we can use. For example, we can get the conjugate of a
partition. Geometrically, the conjugate of a partition is the
reflection of that partition through its main diagonal. Of course,
this operation is an involution::

    sage: Partition([4,1]).conjugate()
    [2, 1, 1, 1]
    sage: Partition([4,1]).conjugate().conjugate()
    [4, 1]

If we create a partition with extra zeros at the end, they will be dropped::

    sage: Partition([4,1,0,0])
    [4, 1]

The idea of a partition being followed by infinitely many parts of size `0` is
consistent with the ``get_part`` method::

    sage: p = Partition([5, 2])
    sage: p.get_part(0)
    5
    sage: p.get_part(10)
    0

We can go back and forth between the exponential notations of a
partition. The exponential notation can be padded with extra
zeros::

    sage: Partition([6,4,4,2,1]).to_exp()
    [1, 1, 0, 2, 0, 1]
    sage: Partition(exp=[1,1,0,2,0,1])
    [6, 4, 4, 2, 1]
    sage: Partition([6,4,4,2,1]).to_exp(5)
    [1, 1, 0, 2, 0, 1]
    sage: Partition([6,4,4,2,1]).to_exp(7)
    [1, 1, 0, 2, 0, 1, 0]
    sage: Partition([6,4,4,2,1]).to_exp(10)
    [1, 1, 0, 2, 0, 1, 0, 0, 0, 0]

We can get the coordinates of the corners of a partition::

    sage: Partition([4,3,1]).corners()
    [(0, 3), (1, 2), (2, 0)]

We can compute the core and quotient of a partition and build
the partition back up from them::

    sage: Partition([6,3,2,2]).core(3)
    [2, 1, 1]
    sage: Partition([7,7,5,3,3,3,1]).quotient(3)
    ([2], [1], [2, 2, 2])
    sage: p = Partition([11,5,5,3,2,2,2])
    sage: p.core(3)
    []
    sage: p.quotient(3)
    ([2, 1], [4], [1, 1, 1])
    sage: Partition(core=[],quotient=([2, 1], [4], [1, 1, 1]))
    [11, 5, 5, 3, 2, 2, 2]

We can compute the Frobenius coordinates (or beta numbers), and go back
and forth::

    sage: Partition([7,3,1]).frobenius_coordinates()
    ([6, 1], [2, 0])
    sage: Partition(frobenius_coordinates=([6,1],[2,0]))
    [7, 3, 1]
    sage: all(mu == Partition(frobenius_coordinates=mu.frobenius_coordinates()) for n in range(30)\
    for mu in Partitions(n))
    True

"""
#*****************************************************************************
#       Copyright (C) 2007 Mike Hansen <mhansen@gmail.com>,
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.interfaces.all import gap, gp
from sage.rings.all import QQ, ZZ, infinity, factorial, gcd
from sage.misc.all import prod
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
import sage.combinat.misc as misc
import sage.combinat.skew_partition
from sage.rings.integer import Integer
import __builtin__
from combinat import CombinatorialClass, CombinatorialObject, cyclic_permutations_iterator, InfiniteAbstractCombinatorialClass
import partitions as partitions_ext
from sage.libs.all import pari
import tableau
import permutation
import composition
from integer_vector import IntegerVectors
from cartesian_product import CartesianProduct
from integer_list import IntegerListsLex
from sage.misc.superseded import deprecation, deprecated_function_alias
from sage.misc.prandom import randrange
from sage.rings.infinity import infinity

def Partition(mu=None, **keyword):
    """
    A partition is a weakly decreasing ordered sequence of non-negative
    integers. This function returns a Sage partition object which can
    be specified in one of the following ways::

      * a list (the default)
      * using exponential notation
      * by Frobenius coordinates (also called beta numbers)
      * specifying the core and the quotient
      * specifying the core and the canonical quotient (TODO)

    See the examples below.

    Sage follows the usual python conventions when dealing with partitions,
    so that the first part of the partition ``mu=Partition([4,3,2,2])`` is
    ``mu[0]``, the second part is ``mu[1]`` and so on. As is usual, Sage ignores
    trailing zeros at the end of partitions.

    EXAMPLES::

        sage: Partition([3,2,1])
        [3, 2, 1]
        sage: Partition([3,2,1,0])
        [3, 2, 1]
        sage: Partition(exp=[2,1,1])
        [3, 2, 1, 1]
        sage: Partition(core=[2,1], quotient=[[2,1],[3],[1,1,1]])
        [11, 5, 5, 3, 2, 2, 2]
        sage: Partition(frobenius_coordinates=([3,2],[4,0]))
        [4, 4, 1, 1, 1]
        sage: [2,1] in Partitions()
        True
        sage: [2,1,0] in Partitions()
        False
        sage: Partition([1,2,3])
        Traceback (most recent call last):
        ...
        ValueError: [1, 2, 3] is not a valid partition
    """
    if mu is not None and len(keyword)==0:
        mu = [i for i in mu if i != 0]
        if mu in Partitions_all():
            return Partition_class(mu)
        else:
            raise ValueError, "%s is not a valid partition"%mu
    elif 'frobenius_coordinates' in keyword and len(keyword)==1:
        return from_frobenius_coordinates(keyword['frobenius_coordinates'])
    elif 'exp' in keyword and len(keyword)==1:
        return from_exp(keyword['exp'])
    elif 'core' in keyword and 'quotient' in keyword and len(keyword)==2:
        return from_core_and_quotient(keyword['core'], keyword['quotient'])
    elif 'core' in keyword and 'canonical_quotient' in keyword and len(keyword)==2:
        raise NotImplementedError
    elif 'core_and_quotient' in keyword and len(keyword)==1:
        deprecation(5790, '"core_and_quotient=(*)" is deprecated. Use "core=[*], quotient=[*]" instead.')
        return from_core_and_quotient(*keyword['core_and_quotient'])
    else:
        raise ValueError, 'incorrect syntax for Partition()'

def from_frobenius_coordinates(frobenius_coordinates):
    """
    Returns a partition from a couple of sequences of Frobenius coordinates

    .. note::

       This function is for internal use only;
       use Partition(frobenius_coordinates=*) instead.

    EXAMPLES::

        sage: Partition(frobenius_coordinates=([],[]))
        []
        sage: Partition(frobenius_coordinates=([0],[0]))
        [1]
        sage: Partition(frobenius_coordinates=([1],[1]))
        [2, 1]
        sage: Partition(frobenius_coordinates=([6,3,2],[4,1,0]))
        [7, 5, 5, 1, 1]
    """
    if len(frobenius_coordinates) <> 2:
        raise ValueError, '%s is not a valid partition, two sequences of coordinates are needed'%str(frobenius_coordinates)
    else:
        a = frobenius_coordinates[0]
        b = frobenius_coordinates[1]
        if len(a) <> len(b):
            raise ValueError, '%s is not a valid partition, the sequences of coordinates need to be the same length'%str(frobenius_coordinates)
            # should add tests to see if a and b are sorted down, nonnegative and strictly decreasing
    r = len(a)
    if r == 0:
        return Partition([])
    tmp = [a[i]+i+1 for i in range(r)]
    # should check that a is strictly decreasing
    if a[-1] < 0:
        raise ValueError, '%s is not a partition, no coordinate can be negative'%str(frobenius_coordinates)
    if b[-1] >= 0:
        tmp.extend([r]*b[r-1])
    else:
        raise ValueError, '%s is not a partition, no coordinate can be negative'%str(frobenius_coordinates)
    for i in xrange(r-1,0,-1):
        if b[i-1]-b[i] > 0:
            tmp.extend([i]*(b[i-1]-b[i]-1))
        else:
            raise ValueError, '%s is not a partition, the coordinates need to be strictly decreasing'%str(frobenius_coordinates)
    return Partition(tmp)

def from_exp(exp):
    """
    Returns a partition from its list of multiplicities.

    .. note::

       This function is for internal use only;
       use Partition(exp=*) instead.

    EXAMPLES::

        sage: Partition(exp=[1,2,1])
        [3, 2, 2, 1]
    """
    p = []
    for i in reversed(range(len(exp))):
        p += [i+1]*exp[i]
    return Partition(p)

def from_core_and_quotient(core, quotient):
    """
    ** This function is being deprecated - use Partition(core=*, quotient=*) instead **

    Returns a partition from its core and quotient.

    Algorithm from mupad-combinat.

    .. note::

       This function is for internal use only;
       use Partition(core=*, quotient=*) instead.

    EXAMPLES::

        sage: Partition(core=[2,1], quotient=[[2,1],[3],[1,1,1]])
        [11, 5, 5, 3, 2, 2, 2]

    TESTS:

    We check that #11412 is actually fixed::

        sage: test = lambda x, k: x == Partition(core=x.core(k),
        ...                                      quotient=x.quotient(k))
        sage: all(test(mu,k) for k in range(1,5)
        ...       for n in range(10) for mu in Partitions(n))
        True
        sage: test2 = lambda core, mus: (
        ...       Partition(core=core, quotient=mus).core(len(mus)) == core
        ...       and
        ...       Partition(core=core, quotient=mus).quotient(len(mus)) == mus)
        sage: all(test2(core,tuple(mus))  # long time (5s on sage.math, 2011)
        ...       for k in range(1,10)
        ...       for n_core in range(10-k)
        ...       for core in Partitions(n_core)
        ...       if core.core(k) == core
        ...       for n_mus in range(10-k)
        ...       for mus in PartitionTuples(n_mus,k))
        True
    """
    length = len(quotient)
    k = length*max(len(q) for q in quotient) + len(core)
    # k needs to be large enough. this seems to me like the smallest it can be
    v = [core[i]-i for i in range(len(core))] + [ -i for i in range(len(core),k) ]
    w = [ filter(lambda x: (x-i) % length == 0, v) for i in range(1, length+1) ]
    new_w = []
    for i in range(length):
        lw = len(w[i])
        lq = len(quotient[i])
        # k needs to be chosen so lw >= lq
        new_w += [ w[i][j] + length*quotient[i][j] for j in range(lq)]
        new_w += [ w[i][j] for j in range(lq,lw)]
    new_w.sort(reverse=True)
    return Partition([new_w[i]+i for i in range(len(new_w))])

class Partition_class(CombinatorialObject):

    def _latex_(self):
        r"""
        Returns a LaTeX version of self.

        EXAMPLES::

            sage: latex(Partition([2, 1]))
            {\def\lr#1{\multicolumn{1}{|@{\hspace{.6ex}}c@{\hspace{.6ex}}|}{\raisebox{-.3ex}{$#1$}}}
            \raisebox{-.6ex}{$\begin{array}[b]{cc}
            \cline{1-1}\cline{2-2}
            \lr{\phantom{x}}&\lr{\phantom{x}}\\
            \cline{1-1}\cline{2-2}
            \lr{\phantom{x}}\\
            \cline{1-1}
            \end{array}$}
            }
        """
        if len(self._list) == 0:
            return "{\\emptyset}"

        from sage.combinat.output import tex_from_array
        return tex_from_array([ ["\\phantom{x}"]*row_size for row_size in self._list ])

    def ferrers_diagram(self):
        """
        Return the Ferrers diagram of pi.

        INPUT:

        -  ``pi`` - a partition, given as a list of integers.


        EXAMPLES::

            sage: print Partition([5,5,2,1]).ferrers_diagram()
            *****
            *****
            **
            *
        """
        return '\n'.join(['*'*p for p in self])

    def pp(self):
        """
        EXAMPLES::

            sage: Partition([5,5,2,1]).pp()
            *****
            *****
            **
            *
        """
        print self.ferrers_diagram()

    def __div__(self, p):
        """
        Returns the skew partition self/p.

        EXAMPLES::

            sage: p = Partition([3,2,1])
            sage: p/[1,1]
            [[3, 2, 1], [1, 1]]
            sage: p/[3,2,1]
            [[3, 2, 1], [3, 2, 1]]
            sage: p/Partition([1,1])
            [[3, 2, 1], [1, 1]]
        """
        if not self.dominates(p):
            raise ValueError, "the partition must dominate p"

        return sage.combinat.skew_partition.SkewPartition([self[:], p])

    def power(self, k):
        """
        Returns the cycle type of the `k`-th power of any permutation
        with cycle type ``self`` (thus describes the powermap of
        symmetric groups).

        Wraps GAP's PowerPartition.

        EXAMPLES::

            sage: p = Partition([5,3])
            sage: p.power(1)
            [5, 3]
            sage: p.power(2)
            [5, 3]
            sage: p.power(3)
            [5, 1, 1, 1]
            sage: p.power(4)
            [5, 3]
            sage: Partition([3,2,1]).power(3)
            [2, 1, 1, 1, 1]

        Now let us compare this to the power map on `S_8`::

            sage: G = SymmetricGroup(8)
            sage: g = G([(1,2,3,4,5),(6,7,8)])
            sage: g
            (1,2,3,4,5)(6,7,8)
            sage: g^2
            (1,3,5,2,4)(6,8,7)
            sage: g^3
            (1,4,2,5,3)
            sage: g^4
            (1,5,4,3,2)(6,7,8)
        """
        res = []
        for i in self:
            g = gcd(i, k)
            res.extend( [ZZ(i//g)]*int(g) )
        res.sort(reverse=True)
        return Partition_class( res )

    def next(self):
        """
        Returns the partition that lexicographically follows the partition
        p. If p is the last partition, then it returns False.

        EXAMPLES::

            sage: Partition([4]).next()
            [3, 1]
            sage: Partition([1,1,1,1]).next()
            False
        """
        p = self
        n = 0
        m = 0
        for i in p:
            n += i
            m += 1

        next_p = p[:] + [1]*(n - len(p))

        #Check to see if we are at the last (all ones) partition
        if p == [1]*n:
            return False

        #
        #If we are not, then run the ZS1 algorithm.
        #

        #Let h be the number of non-one  entries in the
        #partition
        h = 0
        for i in next_p:
            if i != 1:
                h += 1

        if next_p[h-1] == 2:
            m += 1
            next_p[h-1] = 1
            h -= 1
        else:
            r = next_p[h-1] - 1
            t = m - h + 1
            next_p[h-1] = r

            while t >= r :
                h += 1
                next_p[h-1] = r
                t -= r

            if t == 0:
                m = h
            else:
                m = h + 1
                if t > 1:
                    h += 1
                    next_p[h-1] = t

        return Partition_class(next_p[:m])

    def size(self):
        """
        Returns the size of partition p.

        EXAMPLES::

            sage: Partition([2,2]).size()
            4
            sage: Partition([3,2,1]).size()
            6
        """
        return sum(self)

    def sign(self):
        r"""
        Returns the sign of any permutation with cycle type ``self``.

        This function corresponds to a homomorphism from the symmetric
        group `S_n` into the cyclic group of order 2, whose kernel
        is exactly the alternating group `A_n`. Partitions of sign
        `1` are called even partitions while partitions of sign
        `-1` are called odd.

        EXAMPLES::

            sage: Partition([5,3]).sign()
            1
            sage: Partition([5,2]).sign()
            -1

        Zolotarev's lemma states that the Legendre symbol
        `\left(\frac{a}{p}\right)` for an integer
        `a \pmod p` (`p` a prime number), can be computed
        as sign(p_a), where sign denotes the sign of a permutation and
        p_a the permutation of the residue classes `\pmod p`
        induced by modular multiplication by `a`, provided
        `p` does not divide `a`.

        We verify this in some examples.

        ::

            sage: F = GF(11)
            sage: a = F.multiplicative_generator();a
            2
            sage: plist = [int(a*F(x)) for x in range(1,11)]; plist
            [2, 4, 6, 8, 10, 1, 3, 5, 7, 9]

        This corresponds to the permutation (1, 2, 4, 8, 5, 10, 9, 7, 3, 6)
        (acting the set `\{1,2,...,10\}`) and to the partition
        [10].

        ::

            sage: p = PermutationGroupElement('(1, 2, 4, 8, 5, 10, 9, 7, 3, 6)')
            sage: p.sign()
            -1
            sage: Partition([10]).sign()
            -1
            sage: kronecker_symbol(11,2)
            -1

        Now replace `2` by `3`::

            sage: plist = [int(F(3*x)) for x in range(1,11)]; plist
            [3, 6, 9, 1, 4, 7, 10, 2, 5, 8]
            sage: range(1,11)
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            sage: p = PermutationGroupElement('(3,4,8,7,9)')
            sage: p.sign()
            1
            sage: kronecker_symbol(3,11)
            1
            sage: Partition([5,1,1,1,1,1]).sign()
            1

        In both cases, Zolotarev holds.

        REFERENCES:

        - http://en.wikipedia.org/wiki/Zolotarev's_lemma
        """
        return (-1)**(self.size()-self.length())

    def up(self):
        r"""
        Returns a generator for partitions that can be obtained from pi by
        adding a cell.

        EXAMPLES::

            sage: [p for p in Partition([2,1,1]).up()]
            [[3, 1, 1], [2, 2, 1], [2, 1, 1, 1]]
            sage: [p for p in Partition([3,2]).up()]
            [[4, 2], [3, 3], [3, 2, 1]]
            sage: [p for p in Partition([]).up()]
            [[1]]
        """
        p = self
        previous = p.get_part(0) + 1
        for i, current in enumerate(p):
            if current < previous:
                yield Partition(p[:i] + [ p[i] + 1 ] + p[i+1:])
            previous = current
        else:
            yield Partition(p + [1])

    def up_list(self):
        """
        Returns a list of the partitions that can be formed from the
        partition `p` by adding a cell.

        EXAMPLES::

            sage: Partition([2,1,1]).up_list()
            [[3, 1, 1], [2, 2, 1], [2, 1, 1, 1]]
            sage: Partition([3,2]).up_list()
            [[4, 2], [3, 3], [3, 2, 1]]
            sage: Partition([]).up_list()
            [[1]]
        """
        return [p for p in self.up()]

    def down(self):
        r"""
        Returns a generator for partitions that can be obtained from p by
        removing a cell.

        EXAMPLES::

            sage: [p for p in Partition([2,1,1]).down()]
            [[1, 1, 1], [2, 1]]
            sage: [p for p in Partition([3,2]).down()]
            [[2, 2], [3, 1]]
            sage: [p for p in Partition([3,2,1]).down()]
            [[2, 2, 1], [3, 1, 1], [3, 2]]

        TESTS: We check that #11435 is actually fixed::

            sage: Partition([]).down_list() #indirect doctest
            []
        """
        p = self
        l = len(p)
        for i in range(l-1):
            if p[i] > p[i+1]:
                yield Partition(p[:i] + [ p[i]-1 ] + p[i+1:])
        if l >= 1:
            last = p[-1]
            if last == 1:
                yield Partition(p[:-1])
            else:
                yield Partition(p[:-1] + [ p[-1] - 1 ])


    def down_list(self):
        """
        Returns a list of the partitions that can be obtained from the
        partition p by removing a cell.

        EXAMPLES::

            sage: Partition([2,1,1]).down_list()
            [[1, 1, 1], [2, 1]]
            sage: Partition([3,2]).down_list()
            [[2, 2], [3, 1]]
            sage: Partition([3,2,1]).down_list()
            [[2, 2, 1], [3, 1, 1], [3, 2]]
            sage: Partition([]).down_list()  #checks trac #11435
            []
        """
        return [p for p in self.down()]

    def frobenius_coordinates(self):
        """ Returns a couple of sequences of beta numbers aka Frobenius coordinates of the partition.
        These are two striclty decreasing sequences of nonnegative integers, of the same length.

        EXAMPLES::
            sage: Partition([]).frobenius_coordinates()
            ([], [])
            sage: Partition([1]).frobenius_coordinates()
            ([0], [0])
            sage: Partition([3,3,3]).frobenius_coordinates()
            ([2, 1, 0], [2, 1, 0])
            sage: Partition([9,1,1,1,1,1,1]).frobenius_coordinates()
            ([8], [6])

        """
        mu = self
        muconj = mu.conjugate()     # Naive implementation
        if len(mu) <= len(muconj):
            a = filter(lambda x: x>=0, [val-i-1 for i, val in enumerate(mu)])
            b = filter(lambda x: x>=0, [muconj[i]-i-1 for i in range(len(a))])
        else:
            b = filter(lambda x: x>=0, [val-i-1 for i, val in enumerate(muconj)])
            a = filter(lambda x: x>=0, [mu[i]-i-1 for i in range(len(b))])
        return (a,b)

    beta_numbers = frobenius_coordinates

    def frobenius_rank(self):
        """ Returns the Frobenius rank of the partition, which is the number of cells on the main diagonal.

        EXAMPLES::
            sage: Partition([]).frobenius_rank()
            0
            sage: Partition([1]).frobenius_rank()
            1
            sage: Partition([3,3,3]).frobenius_rank()
            3
            sage: Partition([9,1,1,1,1,1]).frobenius_rank()
            1
            sage: Partition([2,1,1,1,1,1]).frobenius_rank()
            1
            sage: Partition([2,2,1,1,1,1]).frobenius_rank()
            2
        """
        mu = self
        if mu == []:
            return 0
        if len(mu) <= mu[0]:
            return len(filter(lambda x: x>=0, [val-i-1 for i, val in enumerate(mu)]))
        else:
            muconj = mu.conjugate()
            return len(filter(lambda x: x>=0, [val-i-1 for i, val in enumerate(muconj)]))


    def dominates(self, p2):
        r"""
        Returns True if partition p1 dominates partitions p2. Otherwise, it
        returns False.

        EXAMPLES::

            sage: p = Partition([3,2])
            sage: p.dominates([3,1])
            True
            sage: p.dominates([2,2])
            True
            sage: p.dominates([2,1,1])
            True
            sage: p.dominates([3,3])
            False
            sage: p.dominates([4])
            False
            sage: Partition([4]).dominates(p)
            False
            sage: Partition([]).dominates([1])
            False
            sage: Partition([]).dominates([])
            True
            sage: Partition([1]).dominates([])
            True
        """
        p1 = self
        sum1 = 0
        sum2 = 0
        min_length = min(len(p1), len(p2))
        if min_length == 0:
            return len(p1) >= len(p2)

        for i in range(min_length):
            sum1 += p1[i]
            sum2 += p2[i]
            if sum2 > sum1:
                return False
        return bool(sum(p1) >= sum(p2))

    def cells(self):
        """
        Return the coordinates of the cells of self. Coordinates are given
        as (row-index, column-index) and are 0 based.

        EXAMPLES::

            sage: Partition([2,2]).cells()
            [(0, 0), (0, 1), (1, 0), (1, 1)]
            sage: Partition([3,2]).cells()
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
        """
        res = []
        for i in range(len(self)):
            for j in range(self[i]):
                res.append( (i,j) )
        return res


    boxes = deprecated_function_alias(7515, cells)

    def generalized_pochhammer_symbol(self, a, alpha):
        r"""
        Returns the generalized Pochhammer symbol
        `(a)_{self}^{(\alpha)}`. This is the product over all
        cells (i,j) in p of `a - (i-1) / \alpha + j - 1`.

        EXAMPLES::

            sage: Partition([2,2]).generalized_pochhammer_symbol(2,1)
            12
        """
        res = 1
        for (i,j) in self.cells():
            res *= (a - (i-1)/alpha+j-1)
        return res

    def get_part(self, i, default=Integer(0)):
        r"""
        Return the `i^{th}` part of self, or ``default`` if it does not exist.

        EXAMPLES::

            sage: p = Partition([2,1])
            sage: p.get_part(0), p.get_part(1), p.get_part(2)
            (2, 1, 0)
            sage: p.get_part(10,-1)
            -1
            sage: Partition([]).get_part(0)
            0
        """
        if i < len(self._list):
            return self._list[i]
        else:
            return default


    def conjugate(self):
        """
        Returns the conjugate partition of the partition ``self``. This
        is also called the associated partition in the literature.

        EXAMPLES::

            sage: Partition([2,2]).conjugate()
            [2, 2]
            sage: Partition([6,3,1]).conjugate()
            [3, 2, 2, 1, 1, 1]

        The conjugate partition is obtained by transposing the Ferrers
        diagram of the partition (see :meth:`.ferrers_diagram`)::

            sage: print Partition([6,3,1]).ferrers_diagram()
            ******
            ***
            *
            sage: print Partition([6,3,1]).conjugate().ferrers_diagram()
            ***
            **
            **
            *
            *
            *
        """
        p = self
        if p == []:
            return Partition_class([])
        else:
            l = len(p)
            conj =  [l]*p[-1]
            for i in xrange(l-1,0,-1):
                conj.extend([i]*(p[i-1] - p[i]))
            return Partition_class(conj)

    def reading_tableau(self):
        """
        EXAMPLES::

            sage: Partition([3,2,1]).reading_tableau()
            [[1, 3, 6], [2, 5], [4]]
        """
        st = tableau.StandardTableaux(self).first()
        word = st.to_word()
        perm = permutation.Permutation(word)
        return perm.robinson_schensted()[1]

    associated = deprecated_function_alias(6655, conjugate)

    def arm_length(self, i, j):
        """
        Returns the length of the arm of cell (i,j) in partition p.

        INPUT: ``i`` and ``j``: two integers

        OUPUT: an integer or a ValueError

        The arm of cell (i,j) is the cells that appear to the right of cell
        (i,j). Note that i and j are 0-based indices. If your coordinates are
        in the form (i,j), use Python's \*-operator.

        EXAMPLES::

            sage: p = Partition([2,2,1])
            sage: p.arm_length(0, 0)
            1
            sage: p.arm_length(0, 1)
            0
            sage: p.arm_length(2, 0)
            0
            sage: Partition([3,3]).arm_length(0, 0)
            2
            sage: Partition([3,3]).arm_length(*[0,0])
            2
        """
        p = self
        if i < len(p) and j < p[i]:
            return p[i]-(j+1)
        else:
            raise ValueError, "The cells is not in the diagram"

    arm = deprecated_function_alias(6655, arm_length)

    def arm_lengths(self, flat=False):
        """
        Returns a tableau of shape p where each cell is filled its arm
        length. The optional boolean parameter flat provides the option of
        returning a flat list.

        EXAMPLES::

            sage: Partition([2,2,1]).arm_lengths()
            [[1, 0], [1, 0], [0]]
            sage: Partition([2,2,1]).arm_lengths(flat=True)
            [1, 0, 1, 0, 0]
            sage: Partition([3,3]).arm_lengths()
            [[2, 1, 0], [2, 1, 0]]
            sage: Partition([3,3]).arm_lengths(flat=True)
            [2, 1, 0, 2, 1, 0]
        """
        p = self
        res = [[p[i]-(j+1) for j in range(p[i])] for i in range(len(p))]
        if flat:
            return sum(res, [])
        else:
            return res

    def arm_cells(self, i, j):
        r"""
        Returns the list of the cells of the arm of cell (i,j) in partition p.

        INPUT: ``i`` and ``j``: two integers

        OUTPUT: a list of pairs of integers

        The arm of cell (i,j) is the boxes that appear to the right of cell
        (i,j). Note that i and j are 0-based indices. If your coordinates are
        in the form (i,j), use Python's \*-operator.

        Examples::

            sage: Partition([4,4,3,1]).arm_cells(1,1)
            [(1, 2), (1, 3)]

            sage: Partition([]).arm_cells(0,0)
            Traceback (most recent call last):
            ...
            ValueError: The cells is not in the diagram

        """
        p = self
        if i < len(p) and j < p[i]:
            return [ (i, x) for x in range(j+1, p[i]) ]
        else:
            raise ValueError, "The cells is not in the diagram"

    def leg_length(self, i, j):
        """
        Returns the length of the leg of cell (i,j) in partition p.

        INPUT: ``i`` and ``j``: two integers

        OUPUT: an integer or a ValueError

        The leg of cell (i,j) is defined to be the cells below it in partition
        p (in English convention). Note that i and j are 0-based. If your
        coordinates are in the form (i,j), use Python's \*-operator.

        EXAMPLES::

            sage: p = Partition([2,2,1])
            sage: p.leg_length(0, 0)
            2
            sage: p.leg_length(0,1)
            1
            sage: p.leg_length(2,0)
            0
            sage: Partition([3,3]).leg_length(0, 0)
            1
            sage: cell = [0,0]; Partition([3,3]).leg_length(*cell)
            1
        """

        conj = self.conjugate()
        if j < len(conj) and i < conj[j]:
            return conj[j]-(i+1)
        else:
            raise ValueError, "The cells is not in the diagram"

    leg = deprecated_function_alias(6655, leg_length)

    def leg_lengths(self, flat=False):
        """
        Returns a tableau of shape p with each cell filled in with its leg
        length.  The optional boolean parameter flat provides the option of
        returning a flat list.

        EXAMPLES::

            sage: Partition([2,2,1]).leg_lengths()
            [[2, 1], [1, 0], [0]]
            sage: Partition([2,2,1]).leg_lengths(flat=True)
            [2, 1, 1, 0, 0]
            sage: Partition([3,3]).leg_lengths()
            [[1, 1, 1], [0, 0, 0]]
            sage: Partition([3,3]).leg_lengths(flat=True)
            [1, 1, 1, 0, 0, 0]
        """
        p = self
        conj = p.conjugate()
        res = [[conj[j]-(i+1) for j in range(p[i])] for i in range(len(p))]
        if flat:
            return sum(res, [])
        else:
            return res

    def leg_cells(self, i, j):
        r"""
        Returns the list of the cells of the leg of cell (i,j) in partition p.

        INPUT: ``i`` and ``j``: two integers

        OUTPUT: a list of pairs of integers

        The leg of cell (i,j) is defined to be the cells below it in partition
        p (in English convention). Note that i and j are 0-based. If your
        coordinates are in the form (i,j), use Python's \*-operator.

        Examples::

            sage: Partition([4,4,3,1]).leg_cells(1,1)
            [(2, 1)]
            sage: Partition([4,4,3,1]).leg_cells(0,1)
            [(1, 1), (2, 1)]

            sage: Partition([]).leg_cells(0,0)
            Traceback (most recent call last):
            ...
            ValueError: The cells is not in the diagram
        """
        l = self.leg_length(i, j)
        return [(x, j) for x in range(i+1, i+l+1)]

    def dominate(self, rows=None):
        """
        Returns a list of the partitions dominated by n. If n is specified,
        then it only returns the ones with = rows rows.

        EXAMPLES::

            sage: Partition([3,2,1]).dominate()
            [[3, 2, 1], [3, 1, 1, 1], [2, 2, 2], [2, 2, 1, 1], [2, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]]
            sage: Partition([3,2,1]).dominate(rows=3)
            [[3, 2, 1], [2, 2, 2]]
        """
        #Naive implementation
        res = [x for x in Partitions_n(self.size()) if self.dominates(x)]
        if rows:
            return [x for x in res if len(x) <= rows]
        else:
            return res

    def contains(self, x):
        """
        Returns True if p2 is a partition whose Ferrers diagram is
        contained in the Ferrers diagram of self

        EXAMPLES::

            sage: p = Partition([3,2,1])
            sage: p.contains([2,1])
            True
            sage: all(p.contains(mu) for mu in Partitions(3))
            True
            sage: all(p.contains(mu) for mu in Partitions(4))
            False
        """
        return len(self) >= len(x) and all(self[i] >= x[i] for i in range(len(x)))

    def hook_product(self, a):
        """
        Returns the Jack hook-product.

        EXAMPLES::

            sage: Partition([3,2,1]).hook_product(x)
            (x + 2)^2*(2*x + 3)
            sage: Partition([2,2]).hook_product(x)
            2*(x + 1)*(x + 2)
        """

        nu = self.conjugate()
        res = 1
        for i in range(len(self)):
            for j in range(self[i]):
                res *= a*(self[i]-j-1)+nu[j]-i
        return res

    def hook_polynomial(self, q, t):
        """
        Returns the two-variable hook polynomial.

        EXAMPLES::

            sage: R.<q,t> = PolynomialRing(QQ)
            sage: a = Partition([2,2]).hook_polynomial(q,t)
            sage: a == (1 - t)*(1 - q*t)*(1 - t^2)*(1 - q*t^2)
            True
            sage: a = Partition([3,2,1]).hook_polynomial(q,t)
            sage: a == (1 - t)^3*(1 - q*t^2)^2*(1 - q^2*t^3)
            True
        """
        nu = self.conjugate()
        res = 1
        for i in range(len(self)):
            for j in range(self[i]):
                res *= 1-q**(self[i]-j-1)*t**(nu[j]-i)
        return res


    def hook_length(self, i, j):
        """
        Returns the length of the hook of cell (i,j) in the partition p. The
        hook of cell (i,j) is defined as the cells to the right or below (in
        the English convention). Note that i and j are 0-based. If your
        coordinates are in the form (i,j), use Python's \*-operator.

        EXAMPLES::

            sage: p = Partition([2,2,1])
            sage: p.hook_length(0, 0)
            4
            sage: p.hook_length(0, 1)
            2
            sage: p.hook_length(2, 0)
            1
            sage: Partition([3,3]).hook_length(0, 0)
            4
            sage: cell = [0,0]; Partition([3,3]).hook_length(*cell)
            4
        """
        return self.leg_length(i,j)+self.arm_length(i,j)+1

    hook = deprecated_function_alias(7515, hook_length)

    def hooks(self):
        """
        Returns a sorted list of the hook lengths in self.

        EXAMPLES::

            sage: Partition([3,2,1]).hooks()
            [5, 3, 3, 1, 1, 1]
        """
        res = []
        for row in self.hook_lengths():
            res += row
        res.sort(reverse=True)
        return res

    def hook_lengths(self):
        r"""
        Returns a tableau of shape p with the cells filled in with the
        hook lengths.

        In each cell, put the sum of one plus the number of cells
        horizontally to the right and vertically below the cell (the
        hook length).

        For example, consider the partition [3,2,1] of 6 with Ferrers
        Diagram::

            # # #
            # #
            #

        When we fill in the cells with the hook lengths, we obtain::

            5 3 1
            3 1
            1

        EXAMPLES::

            sage: Partition([2,2,1]).hook_lengths()
            [[4, 2], [3, 1], [1]]
            sage: Partition([3,3]).hook_lengths()
            [[4, 3, 2], [3, 2, 1]]
            sage: Partition([3,2,1]).hook_lengths()
            [[5, 3, 1], [3, 1], [1]]
            sage: Partition([2,2]).hook_lengths()
            [[3, 2], [2, 1]]
            sage: Partition([5]).hook_lengths()
            [[5, 4, 3, 2, 1]]

        REFERENCES:

        - http://mathworld.wolfram.com/HookLengthFormula.html
        """
        p = self
        conj = p.conjugate()
        return [[p[i]-(i+1)+conj[j]-(j+1)+1 for j in range(p[i])] for i in range(len(p))]

    def upper_hook(self, i, j, alpha):
        r"""
        Returns the upper hook length of the cell (i,j) in self. When alpha
        == 1, this is just the normal hook length. As usual, indices are 0
        based.

        The upper hook length of a cell (i,j) in a partition
        `\kappa` is defined by

        .. math::

             h_*^\kappa(i,j) = \kappa_j^\prime-i+\alpha(\kappa_i - j+1).



        EXAMPLES::

            sage: p = Partition([2,1])
            sage: p.upper_hook(0,0,1)
            3
            sage: p.hook_length(0,0)
            3
            sage: [ p.upper_hook(i,j,x) for i,j in p.cells() ]
            [2*x + 1, x, x]
        """
        p = self
        conj = self.conjugate()
        return conj[j]-(i+1)+alpha*(p[i]-(j+1)+1)

    def upper_hook_lengths(self, alpha):
        r"""
        Returns the upper hook lengths of the partition. When alpha == 1,
        these are just the normal hook lengths.

        The upper hook length of a cell (i,j) in a partition
        `\kappa` is defined by

        .. math::

             h_*^\kappa(i,j) = \kappa_j^\prime-i+1+\alpha(\kappa_i - j).



        EXAMPLES::

            sage: Partition([3,2,1]).upper_hook_lengths(x)
            [[3*x + 2, 2*x + 1, x], [2*x + 1, x], [x]]
            sage: Partition([3,2,1]).upper_hook_lengths(1)
            [[5, 3, 1], [3, 1], [1]]
            sage: Partition([3,2,1]).hook_lengths()
            [[5, 3, 1], [3, 1], [1]]
        """
        p = self
        conj = p.conjugate()
        return [[conj[j]-(i+1)+alpha*(p[i]-(j+1)+1) for j in range(p[i])] for i in range(len(p))]

    def lower_hook(self, i, j, alpha):
        r"""
        Returns the lower hook length of the cell (i,j) in self. When alpha
        == 1, this is just the normal hook length. Indices are 0-based.

        The lower hook length of a cell (i,j) in a partition
        `\kappa` is defined by

        .. math::

             h_*^\kappa(i,j) = \kappa_j^\prime-i+1+\alpha(\kappa_i - j).



        EXAMPLES::

            sage: p = Partition([2,1])
            sage: p.lower_hook(0,0,1)
            3
            sage: p.hook_length(0,0)
            3
            sage: [ p.lower_hook(i,j,x) for i,j in p.cells() ]
            [x + 2, 1, 1]
        """
        p = self
        conj = self.conjugate()
        return conj[j]-(i+1)+1+alpha*(p[i]-(j+1))


    def lower_hook_lengths(self, alpha):
        r"""
        Returns the lower hook lengths of the partition. When alpha == 1,
        these are just the normal hook lengths.

        The lower hook length of a cell (i,j) in a partition
        `\kappa` is defined by

        .. math::

             h_\kappa^*(i,j) = \kappa_j^\prime-i+\alpha(\kappa_i - j + 1).



        EXAMPLES::

            sage: Partition([3,2,1]).lower_hook_lengths(x)
            [[2*x + 3, x + 2, 1], [x + 2, 1], [1]]
            sage: Partition([3,2,1]).lower_hook_lengths(1)
            [[5, 3, 1], [3, 1], [1]]
            sage: Partition([3,2,1]).hook_lengths()
            [[5, 3, 1], [3, 1], [1]]
        """
        p = self
        conj = p.conjugate()
        return [[conj[j]-(i+1)+1+alpha*(p[i]-(j+1)) for j in range(p[i])] for i in range(len(p))]


    def weighted_size(self):
        """
        Returns sum([i\*p[i] for i in range(len(p))]). It is also the
        sum of the leg length of every cell in b, or the sum of
        binomial(s[i],2) for s the conjugate partition of p.

        EXAMPLES::

            sage: Partition([2,2]).weighted_size()
            2
            sage: Partition([3,3,3]).weighted_size()
            9
            sage: Partition([5,2]).weighted_size()
            2
        """
        p = self
        return sum([i*p[i] for i in range(len(p))])


    def length(self):
        """
        Returns the number of parts in self.

        EXAMPLES::

            sage: Partition([3,2]).length()
            2
            sage: Partition([2,2,1]).length()
            3
            sage: Partition([]).length()
            0
        """
        return len(self)

    def to_exp(self, k=0):
        """
        Return a list of the multiplicities of the parts of a partition.
        Use the optional parameter k to get a return list of length at
        least k.

        EXAMPLES::

            sage: Partition([3,2,2,1]).to_exp()
            [1, 2, 1]
            sage: Partition([3,2,2,1]).to_exp(5)
            [1, 2, 1, 0, 0]
        """
        p = self
        if len(p) > 0:
            k = max(k, p[0])
        a = [ 0 ] * (k)
        for i in p:
            a[i-1] += 1
        return a

    def evaluation(self):
        """
        Returns the evaluation of the partition.

        EXAMPLES::

            sage: Partition([4,3,1,1]).evaluation()
            [2, 0, 1, 1]
        """
        return self.to_exp()

    def to_exp_dict(self):
        """
        Returns a dictionary containing the multiplicities of the
        parts of this partition.

        EXAMPLES::

            sage: p = Partition([4,2,2,1])
            sage: d = p.to_exp_dict()
            sage: d[4]
            1
            sage: d[2]
            2
            sage: d[1]
            1
            sage: 5 in d
            False
        """
        d = {}
        for part in self:
            d[part] = d.get(part, 0) + 1
        return d

    def centralizer_size(self, t=0, q=0):
        r"""
        Returns the size of the centralizer of any permutation of cycle type
        ``self``. If `m_i` is the multiplicity of `i` as a part of `p`, this is given
        by

        .. math::

           \prod_i m_i! i^{m_i}.

        Including the optional
        parameters `t` and `q` gives the `q`-`t` analog which is the former product
        times

        .. math::

           \prod_{i=1}^{\mathrm{length}(p)} \frac{1 - q^{p_i}}{1 - t^{p_i}}.

        EXAMPLES::

            sage: Partition([2,2,1]).centralizer_size()
            8
            sage: Partition([2,2,2]).centralizer_size()
            48

        REFERENCES:

        - Kerber, A. 'Algebraic Combinatorics via Finite Group Action',
          1.3 p24
        """
        p = self
        a = p.to_exp()
        size = prod([(i+1)**a[i]*factorial(a[i]) for i in range(len(a))])
        size *= prod( [ (1-q**p[i])/(1-t**p[i]) for i in range(len(p)) ] )

        return size

    def aut(self):
        r"""
        Returns a factor for the number of permutations with cycle type
        ``self``. self.aut() returns
        `1^{j_1}j_1! \cdots n^{j_n}j_n!` where `j_k`
        is the number of parts in self equal to k.

        The number of permutations having `p` as a cycle type is
        given by

        .. math::

             \frac{n!}{1^{j_1}j_1! \cdots n^{j_n}j_n!} .

        EXAMPLES::

            sage: Partition([2,1]).aut()
            2
        """
        m = self.to_exp()
        return prod([(i+1)**m[i]*factorial(m[i]) for i in range(len(m)) if m[i] > 0])

    def content(self, i, j):
        r"""
        Returns the content statistic of the given cell, which is simply
        defined by j - i. This doesn't technically depend on the partition,
        but is included here because it is often useful in the context of
        partitions.

        EXAMPLES::

            sage: Partition([2,1]).content(0,1)
            1
            sage: p = Partition([3,2])
            sage: sum([p.content(*c) for c in p.cells()])
            2
        """

        return j - i

    def conjugacy_class_size(self):
        """
        Returns the size of the conjugacy class of the symmetric group
        indexed by the partition p.

        EXAMPLES::

            sage: Partition([2,2,2]).conjugacy_class_size()
            15
            sage: Partition([2,2,1]).conjugacy_class_size()
            15
            sage: Partition([2,1,1]).conjugacy_class_size()
            6

        REFERENCES:

        - Kerber, A. 'Algebraic Combinatorics via Finite Group Action'
          1.3 p24
        """

        return factorial(sum(self))/self.centralizer_size()


    def corners(self):
        """
        Returns a list of the corners of the partitions. These are the
        positions where we can remove a cell. Indices are of the form (i,j)
        where i is the row-index and j is the column-index, and are
        0-based.

        EXAMPLES::

            sage: Partition([3,2,1]).corners()
            [(0, 2), (1, 1), (2, 0)]
            sage: Partition([3,3,1]).corners()
            [(1, 2), (2, 0)]
        """
        p = self
        if p == []:
            return []

        lcors = [[0,p[0]-1]]
        nn = len(p)
        if nn == 1:
            return map(tuple, lcors)

        lcors_index = 0
        for i in range(1, nn):
            if p[i] == p[i-1]:
                lcors[lcors_index][0] += 1
            else:
                lcors.append([i,p[i]-1])
                lcors_index += 1

        return map(tuple, lcors)


    def outside_corners(self):
        """
        Returns a list of the positions where we can add a cell so that the
        shape is still a partition. Indices are of the form (i,j) where i
        is the row-index and j is the column-index, and are 0-based.

        EXAMPLES::

            sage: Partition([2,2,1]).outside_corners()
            [(0, 2), (2, 1), (3, 0)]
            sage: Partition([2,2]).outside_corners()
            [(0, 2), (2, 0)]
            sage: Partition([6,3,3,1,1,1]).outside_corners()
            [(0, 6), (1, 3), (3, 1), (6, 0)]
            sage: Partition([]).outside_corners()
            [(0, 0)]
        """
        p = self
        if p == Partition([]):
            return [(0,0)]
        res = [ (0, p[0]) ]
        for i in range(1, len(p)):
            if p[i-1] != p[i]:
                res.append((i,p[i]))
        res.append((len(p), 0))

        return res

    def rim(self):
        r"""
        Returns the rim of ``self``.

        The rim of a partition `p` is defined as the cells which belong to
        `p` and which are adjacent to cells not in `p`.

        EXAMPLES:

        The rim of the partition `[5,5,2,1]` consists of the cells marked with
        ``#`` below::

            ****#
            *####
            ##
            #

            sage: Partition([5,5,2,1]).rim()
            [(3, 0), (2, 0), (2, 1), (1, 1), (1, 2), (1, 3), (1, 4), (0, 4)]

            sage: Partition([2,2,1]).rim()
            [(2, 0), (1, 0), (1, 1), (0, 1)]
            sage: Partition([2,2]).rim()
            [(1, 0), (1, 1), (0, 1)]
            sage: Partition([6,3,3,1,1]).rim()
            [(4, 0), (3, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 3), (0, 4), (0, 5)]
            sage: Partition([]).rim()
            []
        """
        p = self
        res = []
        prevLen = 1
        for i in range(len(p)-1, -1, -1):
            for c in range(prevLen-1, p[i]):
                res.append((i,c))
            prevLen = p[i]
        return res

    def outer_rim(self):
        """
        Returns the outer rim of ``self``.

        The outer rim of a partition `p` is defined as the cells which do not
        belong to `p` and which are adjacent to cells in `p`.

        EXAMPLES:

        The outer rim of the partition `[4,1]` consists of the cells marked
        with ``#`` below::

            ****#
            *####
            ##

            sage: Partition([4,1]).outer_rim()
            [(2, 0), (2, 1), (1, 1), (1, 2), (1, 3), (1, 4), (0, 4)]

            sage: Partition([2,2,1]).outer_rim()
            [(3, 0), (3, 1), (2, 1), (2, 2), (1, 2), (0, 2)]
            sage: Partition([2,2]).outer_rim()
            [(2, 0), (2, 1), (2, 2), (1, 2), (0, 2)]
            sage: Partition([6,3,3,1,1]).outer_rim()
            [(5, 0), (5, 1), (4, 1), (3, 1), (3, 2), (3, 3), (2, 3), (1, 3), (1, 4), (1, 5), (1, 6), (0, 6)]
            sage: Partition([]).outer_rim()
            [(0, 0)]
        """
        p = self
        res = []
        prevLen = 0
        for i in range(len(p)-1, -1, -1):
            for c in range(prevLen, p[i]+1):
                res.append((i+1,c))
            prevLen = p[i]
        res.append((0, prevLen))
        return res

    def core(self, length):
        """
        Returns the core of the partition -- in the literature the core is
        commonly referred to as the `k`-core, `p`-core, `r`-core, ... . The
        construction of the core can be visualized by repeatedly removing
        border strips of size `r` from ``self`` until this is no longer possible.
        The remaining partition is the core.

        EXAMPLES::

            sage: Partition([6,3,2,2]).core(3)
            [2, 1, 1]
            sage: Partition([]).core(3)
            []
            sage: Partition([8,7,7,4,1,1,1,1,1]).core(3)
            [2, 1, 1]

        TESTS::

            sage: Partition([3,3,3,2,1]).core(3)
            []
            sage: Partition([10,8,7,7]).core(4)
            []
            sage: Partition([21,15,15,9,6,6,6,3,3]).core(3)
            []
        """
        p = self
        #Normalize the length
        remainder = len(p) % length
        part = p[:] + [0]*remainder

        #Add the canonical vector to the partition
        part = [part[i-1] + len(part)-i for i in range(1, len(part)+1)]

        for e in range(length):
            k = e
            for i in reversed(range(1,len(part)+1)):
                if part[i-1] % length == e:
                    part[i-1] = k
                    k += length
        part.sort()
        part.reverse()

        #Remove the canonical vector
        part = [part[i-1]-len(part)+i for i in range(1, len(part)+1)]
        #Select the r-core
        return Partition_class(filter(lambda x: x != 0, part))

    r_core = deprecated_function_alias(11165, core)

    def quotient(self, length):
        """
        Returns the quotient of the partition  -- in the literature the
        core is commonly referred to as the `k`-core, `p`-core, `r`-core, ... . The
        quotient is a list of `r` partitions, constructed in the following
        way. Label each cell in `p` with its content, modulo `r`. Let `R_i` be
        the set of rows ending in a cell labelled `i`, and `C_i` be the set of
        columns ending in a cell labelled `i`. Then the `j`-th component of the
        quotient of `p` is the partition defined by intersecting `R_j` with
        `C_j+1`.

        EXAMPLES::

            sage: Partition([7,7,5,3,3,3,1]).quotient(3)
            ([2], [1], [2, 2, 2])

        TESTS::

            sage: Partition([8,7,7,4,1,1,1,1,1]).quotient(3)
            ([2, 1], [2, 2], [2])
            sage: Partition([10,8,7,7]).quotient(4)
            ([2], [3], [2], [1])
            sage: Partition([6,3,3]).quotient(3)
            ([1], [1], [2])
            sage: Partition([3,3,3,2,1]).quotient(3)
            ([1], [1, 1], [1])
            sage: Partition([6,6,6,3,3,3]).quotient(3)
            ([2, 1], [2, 1], [2, 1])
            sage: Partition([21,15,15,9,6,6,6,3,3]).quotient(3)
            ([5, 2, 1], [5, 2, 1], [7, 3, 2])
            sage: Partition([21,15,15,9,6,6,3,3]).quotient(3)
            ([5, 2], [5, 2, 1], [7, 3, 1])
            sage: Partition([14,12,11,10,10,10,10,9,6,4,3,3,2,1]).quotient(5)
            ([3, 3], [2, 2, 1], [], [3, 3, 3], [1])

            sage: all(p == Partition(core=p.core(k), quotient=p.quotient(k))
            ...       for i in range(10) for p in Partitions(i)
            ...       for k in range(1,6))
            True
        """
        p = self
        #Normalize the length
        remainder = len(p) % length
        part = p[:] + [0]*(length-remainder)


        #Add the canonical vector to the partition
        part = [part[i-1] + len(part)-i for i in range(1, len(part)+1)]
        result = [None]*length

        #Reducing vector
        for e in range(length):
            k = e
            tmp = []
            for i in reversed(range(len(part))):
                if part[i] % length == e:
                    tmp.append(ZZ((part[i]-k)/length))
                    k += length

            a = [i for i in tmp if i != 0]
            a.reverse()
            result[e] = a

        return tuple(map(Partition_class, result))

    r_quotient = deprecated_function_alias(7515, quotient)

    def is_core(self, k):
        r"""
        Tests whether the partition is a `k`-core or not. Visuallly, this can be checked
        by trying to remove border strips of size `k` from ``self``. If this is not possible,
        then ``self`` is a `k`-core.

        EXAMPLES::

            sage: p = Partition([12,8,5,5,2,2,1])
            sage: p.is_core(4)
            False
            sage: p.is_core(5)
            True
            sage: p.is_core(0)
            True
        """
        return not k in self.hooks()

    def k_interior(self, k):
        r"""
        Returns the partition consisting of the cells of ``self``,
        whose hook lengths are greater than `k`.

        EXAMPLES::

            sage: p = Partition([3,2,1])
            sage: p.hook_lengths()
            [[5, 3, 1], [3, 1], [1]]
            sage: p.k_interior(2)
            [2, 1]
            sage: p.k_interior(3)
            [1]

            sage: p = Partition([])
            sage: p.k_interior(3)
            []
        """
        return Partition([len([i for i in row if i > k])
                          for row in self.hook_lengths()])

    def k_boundary(self, k):
        r"""
        Returns the skew partition formed by removing the cells of the
        `k`-interior, see :meth:`k_interior`.

        EXAMPLES::

            sage: p = Partition([3,2,1])
            sage: p.k_boundary(2)
            [[3, 2, 1], [2, 1]]
            sage: p.k_boundary(3)
            [[3, 2, 1], [1]]

            sage: p = Partition([12,8,5,5,2,2,1])
            sage: p.k_boundary(4)
            [[12, 8, 5, 5, 2, 2, 1], [8, 5, 2, 2]]
        """
        # bypass the checks
        return sage.combinat.skew_partition.SkewPartition_class(
            (self, self.k_interior(k)))

    def add_cell(self, i, j = None):
        r"""
        Returns a partition corresponding to self with a cell added in row
        i. i and j are 0-based row and column indices. This does not change
        p.

        Note that if you have coordinates in a list, you can call this
        function with python's \* notation (see the examples below).

        EXAMPLES::

            sage: Partition([3, 2, 1, 1]).add_cell(0)
            [4, 2, 1, 1]
            sage: cell = [4, 0]; Partition([3, 2, 1, 1]).add_cell(*cell)
            [3, 2, 1, 1, 1]
        """

        if j is None:
            if i >= len(self):
                j = 0
            else:
                j = self[i]

        if (i,j) in self.outside_corners():
            pl = self.to_list()
            if i == len(pl):
                pl.append(1)
            else:
                pl[i] += 1
            return Partition(pl)

        raise ValueError, "[%s, %s] is not an addable cell"%(i,j)

    add_box = deprecated_function_alias(7515, add_cell)

    def remove_cell(self, i, j = None):
        """
        Returns the partition obtained by removing a cell at the end of row
        i.

        EXAMPLES::

            sage: Partition([2,2]).remove_cell(1)
            [2, 1]
            sage: Partition([2,2,1]).remove_cell(2)
            [2, 2]
            sage: #Partition([2,2]).remove_cell(0)

        ::

            sage: Partition([2,2]).remove_cell(1,1)
            [2, 1]
            sage: #Partition([2,2]).remove_cell(1,0)
        """

        if i >= len(self):
            raise ValueError, "i must be less than the length of the partition"

        if j is None:
            j = self[i] - 1

        if (i,j) not in self.corners():
            raise ValueError, "[%d,%d] is not a corner of the partition" % (i,j)

        if self[i] == 1:
            return Partition(self[:-1])
        else:
            return Partition(self[:i] + [ self[i:i+1][0] - 1 ] + self[i+1:])

    remove_box = deprecated_function_alias(7515, remove_cell)

    def k_skew(self, k):
        r"""
        Returns the `k`-skew partition.

        The `k`-skew diagram of a `k`-bounded partition is the skew diagram
        denoted `\lambda/^k` satisfying the conditions:

        1. row i of `\lambda/^k` has length `\lambda_i`

        2. no cell in `\lambda/^k` has hook-length exceeding k

        3. every square above the diagram of `\lambda/^k` has hook
           length exceeding k.

        REFERENCES:

        - Lapointe, L. and Morse, J. 'Order Ideals in Weak Subposets
          of Young's Lattice and Associated Unimodality Conjectures'

        EXAMPLES::

            sage: p = Partition([4,3,2,2,1,1])
            sage: p.k_skew(4)
            [[9, 5, 3, 2, 1, 1], [5, 2, 1]]
        """

        if len(self) == 0:
            return sage.combinat.skew_partition.SkewPartition([[],[]])

        if self[0] > k:
            raise ValueError, "the partition must be %d-bounded" % k

        #Find the k-skew diagram of the partition formed
        #by removing the first row
        s = Partition(self[1:]).k_skew(k)

        s_inner = s.inner()
        s_outer = s.outer()
        s_conj_rl = s.conjugate().row_lengths()

        #Find the leftmost column with less than
        # or equal to kdiff cells
        kdiff = k - self[0]

        if s_outer == []:
            spot = 0
        else:
            spot = s_outer[0]

        for i in range(len(s_conj_rl)):
            if s_conj_rl[i] <= kdiff:
                spot = i
                break

        outer = [ self[0] + spot ] + s_outer[:]
        if spot > 0:
            inner = [ spot ] + s_inner[:]
        else:
            inner = s_inner[:]

        return sage.combinat.skew_partition.SkewPartition([outer, inner])

    def to_core(self, k):
        r"""
        Maps the `k`-bounded partition ``self`` to its corresponding `k+1`-core.

        See also :meth:`k_skew`.

        EXAMPLES::

            sage: p = Partition([4,3,2,2,1,1])
            sage: c = p.to_core(4); c
            [9, 5, 3, 2, 1, 1]
            sage: type(c)
            <class 'sage.combinat.core.Cores_length_with_category.element_class'>
            sage: c.to_bounded_partition() == p
            True
        """
        return sage.combinat.core.Core(self.k_skew(k)[0],k+1)

    def from_kbounded_to_reduced_word(self, k):
        r"""
        Maps a `k`-bounded partition to a reduced word for an element in
        the affine permutation group.

        This uses the fact that there is a bijection between `k`-bounded partitions
        and `(k+1)`-cores and an action of the affine nilCoxeter algebra of type
        `A_k^{(1)}` on `(k+1)`-cores as described in [LM2006]_.

        REFERENCES:

            .. [LM2006] MR2167475 (2006j:05214)
               L. Lapointe, J. Morse. Tableaux on `k+1`-cores, reduced words for affine permutations, and `k`-Schur expansions.
               J. Combin. Theory Ser. A 112 (2005), no. 1, 44--81.

        EXAMPLES::

            sage: p=Partition([2,1,1])
            sage: p.from_kbounded_to_reduced_word(2)
            [2, 1, 2, 0]
            sage: p=Partition([3,1])
            sage: p.from_kbounded_to_reduced_word(3)
            [3, 2, 1, 0]
            sage: p.from_kbounded_to_reduced_word(2)
            Traceback (most recent call last):
            ...
            ValueError: the partition must be 2-bounded
            sage: p=Partition([])
            sage: p.from_kbounded_to_reduced_word(2)
            []
        """
        p=self.k_skew(k)[0]
        result = []
        while p != []:
            corners = p.corners()
            c = p.content(corners[0][0],corners[0][1])%(k+1)
            result.append(Integer(c))
            list = [x for x in corners if p.content(x[0],x[1])%(k+1) ==c]
            for x in list:
                p = p.remove_cell(x[0])
        return result

    def from_kbounded_to_grassmannian(self, k):
        r"""
        Maps a `k`-bounded partition to a Grassmannian element in
        the affine Weyl group of type `A_k^{(1)}`.

        For details, see the documentation of the method
        :meth:`from_kbounded_to_reduced_word` .

        EXAMPLES::

            sage: p=Partition([2,1,1])
            sage: p.from_kbounded_to_grassmannian(2)
            [-1  1  1]
            [-2  2  1]
            [-2  1  2]
            sage: p=Partition([])
            sage: p.from_kbounded_to_grassmannian(2)
            [1 0 0]
            [0 1 0]
            [0 0 1]
        """
        from sage.combinat.root_system.weyl_group import WeylGroup
        W=WeylGroup(['A',k,1])
        return W.from_reduced_word(self.from_kbounded_to_reduced_word(k))

    def to_list(self):
        r"""
        Return self as a list.

        EXAMPLES::

            sage: p = Partition([2,1]).to_list(); p
            [2, 1]
            sage: type(p)
            <type 'list'>

        TESTS::

            sage: p = Partition([2,1])
            sage: pl = p.to_list()
            sage: pl[0] = 0; p
            [2, 1]
        """
        return self._list[:]

    def add_vertical_border_strip(self, k):
        """
        Returns a list of all the partitions that can be obtained by adding
        a vertical border strip of length k to self.

        EXAMPLES::

            sage: Partition([]).add_vertical_border_strip(0)
            [[]]
            sage: Partition([]).add_vertical_border_strip(2)
            [[1, 1]]
            sage: Partition([2,2]).add_vertical_border_strip(2)
            [[3, 3], [3, 2, 1], [2, 2, 1, 1]]
            sage: Partition([3,2,2]).add_vertical_border_strip(2)
            [[4, 3, 2], [4, 2, 2, 1], [3, 3, 3], [3, 3, 2, 1], [3, 2, 2, 1, 1]]
        """
        return [p.conjugate() for p in self.conjugate().add_horizontal_border_strip(k)]

    def add_horizontal_border_strip(self, k):
        """
        Returns a list of all the partitions that can be obtained by adding
        a horizontal border strip of length k to self.

        EXAMPLES::

            sage: Partition([]).add_horizontal_border_strip(0)
            [[]]
            sage: Partition([]).add_horizontal_border_strip(2)
            [[2]]
            sage: Partition([2,2]).add_horizontal_border_strip(2)
            [[2, 2, 2], [3, 2, 1], [4, 2]]
            sage: Partition([3,2,2]).add_horizontal_border_strip(2)
            [[3, 2, 2, 2], [3, 3, 2, 1], [4, 2, 2, 1], [4, 3, 2], [5, 2, 2]]

        TODO: reimplement like remove_horizontal_border_strip using IntegerListsLex
        """
        conj = self.conjugate().to_list()
        shelf = []
        res = []
        i = 0
        while i < len(conj):
            tmp = 1
            while i+1 < len(conj) and conj[i] == conj[i+1]:
                tmp += 1
                i += 1
            if i == len(conj)-1 and i > 0 and conj[i] != conj[i-1]:
                tmp = 1
            shelf.append(tmp)
            i += 1

        #added the last shelf on the right side of
        #the first line
        shelf.append(k)

        #list all of the positions for cells
        #filling each self from the left to the right
        l = IntegerVectors(k, len(shelf), outer=shelf).list()
        for iv in l:
            tmp = conj + [0]*k
            j = 0
            for t in range(len(iv)):
                while iv[t] > 0:
                    tmp[j] += 1
                    iv[t] -= 1
                    j += 1
                j = sum(shelf[:t+1])
            res.append(Partition_class([i for i in tmp if i != 0]).conjugate())
        return res

    def remove_horizontal_border_strip(self, k):
        """
        Returns the partitions obtained from self by removing an
        horizontal border strip of length k

        EXAMPLES::

            sage: Partition([5,3,1]).remove_horizontal_border_strip(0).list()
            [[5, 3, 1]]
            sage: Partition([5,3,1]).remove_horizontal_border_strip(1).list()
            [[5, 3], [5, 2, 1], [4, 3, 1]]
            sage: Partition([5,3,1]).remove_horizontal_border_strip(2).list()
            [[5, 2], [5, 1, 1], [4, 3], [4, 2, 1], [3, 3, 1]]
            sage: Partition([5,3,1]).remove_horizontal_border_strip(3).list()
            [[5, 1], [4, 2], [4, 1, 1], [3, 3], [3, 2, 1]]
            sage: Partition([5,3,1]).remove_horizontal_border_strip(4).list()
            [[4, 1], [3, 2], [3, 1, 1]]
            sage: Partition([5,3,1]).remove_horizontal_border_strip(5).list()
            [[3, 1]]
            sage: Partition([5,3,1]).remove_horizontal_border_strip(6).list()
            []

        The result is returned as a combinatorial class::

            sage: Partition([5,3,1]).remove_horizontal_border_strip(5)
            The subpartitions of [5, 3, 1] obtained by removing an horizontal border strip of length 5

        TESTS::

            sage: Partition([3,2,2]).remove_horizontal_border_strip(2).list()
            [[3, 2], [2, 2, 1]]
            sage: Partition([3,2,2]).remove_horizontal_border_strip(2).first().parent()
            Partitions...
            sage: Partition([]).remove_horizontal_border_strip(0).list()
            [[]]
            sage: Partition([]).remove_horizontal_border_strip(6).list()
            []
        """
        return IntegerListsLex(n          = self.size()-k,
                               min_length = len(self)-1,
                               max_length = len(self),
                               floor      = self[1:]+[0],
                               ceiling    = self[:],
                               max_slope  = 0,
                               element_constructor = Partition,
                               name = "The subpartitions of %s obtained by removing an horizontal border strip of length %s"%(self,k))

    def k_conjugate(self, k):
        """
        Returns the k-conjugate of the partition.

        The k-conjugate is the partition that is given by the columns of
        the k-skew diagram of the partition.

        EXAMPLES::

            sage: p = Partition([4,3,2,2,1,1])
            sage: p.k_conjugate(4)
            [3, 2, 2, 1, 1, 1, 1, 1, 1]
        """
        return Partition(self.k_skew(k).conjugate().row_lengths())

    def parent(self):
        """
        Returns the combinatorial class of partitions of sum(self).

        EXAMPLES::

            sage: Partition([3,2,1]).parent()
            Partitions of the integer 6
        """
        return Partitions(sum(self[:]))

    def arms_legs_coeff(self, i, j):
        """
        This is a statistic on a cell c=(i,j) in the diagram of partition p
        given by

        .. math::

             [ (1 - q^{arm_length(c)} * t^{leg_length(c) + 1}) ] /            [ (1 - q^{arm_length(c) + 1} * t^{leg_length(c)}) ]



        EXAMPLES::

            sage: Partition([3,2,1]).arms_legs_coeff(1,1)
            (-t + 1)/(-q + 1)
            sage: Partition([3,2,1]).arms_legs_coeff(0,0)
            (-q^2*t^3 + 1)/(-q^3*t^2 + 1)
            sage: Partition([3,2,1]).arms_legs_coeff(*[0,0])
            (-q^2*t^3 + 1)/(-q^3*t^2 + 1)
        """
        QQqt = PolynomialRing(QQ, ['q', 't'])
        (q,t) = QQqt.gens()
        if i < len(self) and j < self[i]:
            res =  (1-q**self.arm_length(i,j) * t**(self.leg_length(i,j)+1))
            res /= (1-q**(self.arm_length(i,j)+1) * t**self.leg_length(i,j))
            return res
        else:
            return ZZ(1)

    def atom(self):
        """
        Returns a list of the standard tableaux of size self.size() whose
        atom is equal to self.

        EXAMPLES::

            sage: Partition([2,1]).atom()
            [[[1, 2], [3]]]
            sage: Partition([3,2,1]).atom()
            [[[1, 2, 3, 6], [4, 5]], [[1, 2, 3], [4, 5], [6]]]
        """
        res = []
        for tab in tableau.StandardTableaux_n(self.size()):
            if tab.atom() == self:
                res.append(tab)
        return res

    def k_atom(self, k):
        """
        EXAMPLES::

            sage: p = Partition([3,2,1])
            sage: p.k_atom(1)
            []
            sage: p.k_atom(3)
            [[[1, 1, 1], [2, 2], [3]],
             [[1, 1, 1, 2], [2], [3]],
             [[1, 1, 1, 3], [2, 2]],
             [[1, 1, 1, 2, 3], [2]]]
            sage: Partition([3,2,1]).k_atom(4)
            [[[1, 1, 1], [2, 2], [3]], [[1, 1, 1, 3], [2, 2]]]

        TESTS::

            sage: Partition([1]).k_atom(1)
            [[[1]]]
            sage: Partition([1]).k_atom(2)
            [[[1]]]
            sage: Partition([]).k_atom(1)
            [[]]
        """
        res = [ tableau.Tableau_class([]) ]
        for i in range(len(self)):
            res = [ x.promotion_operator( self[-i-1] ) for x in res]
            res = sum(res, [])
            res = [ y.katabolism_projector(Partition_class(self[-i-1:]).k_split(k)) for y in res]
            res = [ i for i in res if i !=0 and i != [] ]
        return res

    def k_split(self, k):
        """
        Returns the k-split of self.

        EXAMPLES::

            sage: Partition([4,3,2,1]).k_split(3)
            []
            sage: Partition([4,3,2,1]).k_split(4)
            [[4], [3, 2], [1]]
            sage: Partition([4,3,2,1]).k_split(5)
            [[4, 3], [2, 1]]
            sage: Partition([4,3,2,1]).k_split(6)
            [[4, 3, 2], [1]]
            sage: Partition([4,3,2,1]).k_split(7)
            [[4, 3, 2, 1]]
            sage: Partition([4,3,2,1]).k_split(8)
            [[4, 3, 2, 1]]
        """
        if self == []:
            return []
        elif k < self[0]:
            return []
        else:
            res = []
            part = list(self)
            while part != [] and part[0]+len(part)-1 >= k:
                p = k - part[0]
                res.append( part[:p+1] )
                part = part[p+1:]
            if part != []:
                res.append(part)
        return res

    def jacobi_trudi(self):
        """
        EXAMPLES::

            sage: part = Partition([3,2,1])
            sage: jt = part.jacobi_trudi(); jt
            [h[3] h[1]    0]
            [h[4] h[2]  h[]]
            [h[5] h[3] h[1]]
            sage: s = SymmetricFunctions(QQ).schur()
            sage: h = SymmetricFunctions(QQ).homogeneous()
            sage: h( s(part) )
            h[3, 2, 1] - h[3, 3] - h[4, 1, 1] + h[5, 1]
            sage: jt.det()
            h[3, 2, 1] - h[3, 3] - h[4, 1, 1] + h[5, 1]
        """
        return sage.combinat.skew_partition.SkewPartition([ self, [] ]).jacobi_trudi()


    def character_polynomial(self):
        r"""
        Returns the character polynomial associated to the partition self.
        The character polynomial `q_\mu` is defined by


        .. math::

           q_\mu(x_1, x_2, \ldots, x_k) = \downarrow \sum_{\alpha \vdash k}\frac{ \chi^\mu_\alpha }{1^{a_1}2^{a_2}\cdots k^{a_k}a_1!a_2!\cdots a_k!} \prod_{i=1}^{k} (ix_i-1)^{a_i}


        where `a_i` is the multiplicity of `i` in
        `\alpha`.

        It is computed in the following manner.

        1. Expand the Schur function `s_\mu` in the power-sum
           basis.

        2. Replace each `p_i` with `ix_i-1`

        3. Apply the umbral operator `\downarrow` to the resulting
           polynomial.

        EXAMPLES::

            sage: Partition([1]).character_polynomial()
            x - 1
            sage: Partition([1,1]).character_polynomial()
            1/2*x0^2 - 3/2*x0 - x1 + 1
            sage: Partition([2,1]).character_polynomial()
            1/3*x0^3 - 2*x0^2 + 8/3*x0 - x2
        """

        #Create the polynomial ring we will use
        k = self.size()
        P = PolynomialRing(QQ, k, 'x')
        x = P.gens()

        #Expand s_mu in the power sum basis
        from sage.combinat.sf.sf import SymmetricFunctions
        Sym = SymmetricFunctions(QQ)
        s = Sym.schur()
        p = Sym.power()
        ps_mu = p(s(self))

        #Replace each p_i by i*x_i-1
        items = ps_mu.monomial_coefficients().items()  #items contains a list of (partition, coeff) pairs
        partition_to_monomial = lambda part: prod([ (i*x[i-1]-1) for i in part ])
        res = [ [partition_to_monomial(mc[0]), mc[1]] for mc in items ]

        #Write things in the monomial basis
        res = [ prod(pair) for pair in res ]
        res = sum( res )

        #Apply the umbral operator and return the result
        return misc.umbral_operation(res)

    def dimension(self, smaller = [], k = 1):
        r"""
        This function computes the number of paths from the
        ``smaller`` partition to the partition ``self``, where each step
        consists of adding a `k`-ribbon while keeping a partition.

        Note that a 1-ribbon is just a single cell, so this gives path
        lengths in the Young graph when `k=1`.

        Note also that the defaut case (`k=1` and ``smaller=[]``) gives the
        dimension of characters of the symmetric groups.

        INPUT:

        - ``self`` - a partition
        - ``smaller`` - a partition (default: empty)
        - `k` - a positive integer (default: 1)

        OUTPUT:

        integer -- the number of such paths

        EXAMPLES:

        Looks at the number of ways of getting from [5,4] to the empty partition, removing one cell at a time::

            sage: mu = Partition([5,4])
            sage: mu.dimension()
            42

        Same, but removing one 3-ribbon at a time. Note that the 3-core of mu is empty::

            sage: mu.dimension(k=3)
            3

        The 2-core of mu is not the empty partition::

            sage: mu.dimension(k=2)
            0

        Indeed, the 2-core of mu is [1]::

            sage: mu.dimension(Partition([1]),k=2)
            2

        TESTS:

        Checks that the sum of squares of dimensions of characters of the symmetric group is the order of the group::

            sage: all(sum(mu.dimension()^2 for mu in Partitions(i))==factorial(i) for i in range(10))
            True

        A check coming from the theory of `k`-differentiable posets::

            sage: k=2; core = Partition([2,1])
            sage: all(sum(mu.dimension(core,k=2)^2 for mu in Partitions(3+i*2) if mu.core(2) == core)==2^i*factorial(i) for i in range(10))
            True

        Checks that the dimension satisfies the obvious recursion relation::

            sage: test = lambda larger, smaller: larger.dimension(smaller) == sum(mu.dimension(smaller) for mu in larger.down())
            sage: all(test(larger,smaller) for l in xrange(1,10) for s in xrange(0,10) for larger in Partitions(l) for smaller in Partitions(s) if smaller<>larger)
            True

        ALGORITHM:

        Depending on the parameters given, different simplifications
        occur. When `k=1` and ``smaller`` is empty, this function uses
        the hook formula. When `k=1` and ``smaller`` is not empty, it
        uses a formula from [ORV]_.

        When `k \not{=} 1`, we first check that both ``self`` and
        ``smaller`` have the same `k`-core, then use the `k`-quotients
        and the same algorithm on each of the `k`-quotients.

        REFERENCES:

        .. [ORV] Olshanski, Regev, Vershik, "Frobenius-Schur functions"

        AUTHORS:

        - Paul-Olivier Dehaye (2011-06-07)

        """
        larger = self
        if smaller == []:
            smaller = Partition([])
        if k == 1:
            if smaller == Partition([]):        # In this case, use the hook dimension formula
                return factorial(larger.size())/prod(larger.hooks())
            else:
                if not larger.contains(smaller):    # easy case
                    return 0
                else:
                    # relative dimension
                    # Uses a formula of Olshanski, Regev, Vershik (see reference)
                    def inv_factorial(i):
                        if i < 0:
                            return 0
                        else:
                            return 1/factorial(i)
                    len_range = range(larger.length())
                    from sage.matrix.constructor import matrix
                    M = matrix(QQ,[[inv_factorial(larger.get_part(i)-smaller.get_part(j)-i+j) for i in len_range] for j in len_range])
                    return factorial(larger.size()-smaller.size())*M.determinant()
        else:
            larger_core = larger.core(k)
            smaller_core = smaller.core(k)
            if smaller_core <> larger_core:     #   easy case
                return 0
            larger_quotients = larger.quotient(k)
            smaller_quotients = smaller.quotient(k)

            def multinomial_with_partitions(sizes,path_counts):
            # count the number of ways of performing the k paths in parallel,
            # if we know the total length alloted for each of the paths (sizes), and the number
            # of paths for each component. A multinomial picks the ordering of the components where
            # each step is taken.
                return prod(path_counts)*factorial(sum(sizes))/prod(map(factorial,sizes))

            sizes = [larger_quotients[i].size()-smaller_quotients[i].size() for i in range(k)]
            path_counts = [larger_quotients[i].dimension(smaller_quotients[i]) for i in range(k)]
            return multinomial_with_partitions(sizes,path_counts)


##################################################

def number_of_partitions_list(n,k=None):
    r"""
    This function will be deprecated in a future version of Sage and
    eventually removed. Use Partitions(n).cardinality() or Partitions(n,
    length=k).cardinality() instead.

    Original docstring follows.

    Returns the size of partitions_list(n,k).

    Wraps GAP's NrPartitions.

    It is possible to associate with every partition of the integer n a
    conjugacy class of permutations in the symmetric group on n points
    and vice versa. Therefore p(n) = NrPartitions(n) is the number of
    conjugacy classes of the symmetric group on n points.

    ``number_of_partitions(n)`` is also available in
    PARI, however the speed seems the same until `n` is in the
    thousands (in which case PARI is faster).

    EXAMPLES::

        sage: partition.number_of_partitions_list(10,2)
        5
        sage: partition.number_of_partitions_list(10)
        42

    A generating function for p(n) is given by the reciprocal of
    Euler's function:

    .. math::

             \sum_{n=0}^\infty p(n)x^n = \prod_{k=1}^\infty \left(\frac {1}{1-x^k} \right).


    Sage verifies that the first several coefficients do instead
    agree::

        sage: q = PowerSeriesRing(QQ, 'q', default_prec=9).gen()
        sage: prod([(1-q^k)^(-1) for k in range(1,9)])  ## partial product of
        1 + q + 2*q^2 + 3*q^3 + 5*q^4 + 7*q^5 + 11*q^6 + 15*q^7 + 22*q^8 + O(q^9)
        sage: [partition.number_of_partitions_list(k) for k in range(2,10)]
        [2, 3, 5, 7, 11, 15, 22, 30]

    REFERENCES:

    - http://en.wikipedia.org/wiki/Partition\_(number\_theory)
    """
    if k is None:
        ans=gap.eval("NrPartitions(%s)"%(ZZ(n)))
    else:
        ans=gap.eval("NrPartitions(%s,%s)"%(ZZ(n),ZZ(k)))
    return ZZ(ans)


######################
# Ordered Partitions #
######################
def OrderedPartitions(n, k=None):
    """
    Returns the combinatorial class of ordered partitions of n. If k is
    specified, then only the ordered partitions of length k are
    returned.

    .. note::

       It is recommended that you use Compositions instead as
       OrderedPartitions wraps GAP. See also ordered_partitions.

    EXAMPLES::

        sage: OrderedPartitions(3)
        Ordered partitions of 3
        sage: OrderedPartitions(3).list()
        [[3], [2, 1], [1, 2], [1, 1, 1]]
        sage: OrderedPartitions(3,2)
        Ordered partitions of 3 of length 2
        sage: OrderedPartitions(3,2).list()
        [[2, 1], [1, 2]]
    """
    return OrderedPartitions_nk(n,k)

class OrderedPartitions_nk(CombinatorialClass):
    def __init__(self, n, k=None):
        """
        EXAMPLES::

            sage: o = OrderedPartitions(4,2)
            sage: o == loads(dumps(o))
            True
        """
        self.n = n
        self.k = k

    def __contains__(self, x):
        """
        EXAMPLES::

            sage: o = OrderedPartitions(4,2)
            sage: [2,1] in o
            False
            sage: [2,2] in o
            True
            sage: [1,2,1] in o
            False
        """
        return x in composition.Compositions(self.n, length=self.k)

    def __repr__(self):
        """
        EXAMPLES::

            sage: OrderedPartitions(3).__repr__()
            'Ordered partitions of 3'
            sage: OrderedPartitions(3,2).__repr__()
            'Ordered partitions of 3 of length 2'
        """
        string = "Ordered partitions of %s"%self.n
        if self.k is not None:
            string += " of length %s"%self.k
        return string

    def list(self):
        """
        EXAMPLES::

            sage: OrderedPartitions(3).list()
            [[3], [2, 1], [1, 2], [1, 1, 1]]
            sage: OrderedPartitions(3,2).list()
            [[2, 1], [1, 2]]
        """
        n = self.n
        k = self.k
        if self.k is None:
            ans=gap.eval("OrderedPartitions(%s)"%(ZZ(n)))
        else:
            ans=gap.eval("OrderedPartitions(%s,%s)"%(ZZ(n),ZZ(k)))
        result = eval(ans.replace('\n',''))
        result.reverse()
        return result

    def cardinality(self):
        """
        EXAMPLES::

            sage: OrderedPartitions(3).cardinality()
            4
            sage: OrderedPartitions(3,2).cardinality()
            2
        """
        n = self.n
        k = self.k
        if k is None:
            ans=gap.eval("NrOrderedPartitions(%s)"%(n))
        else:
            ans=gap.eval("NrOrderedPartitions(%s,%s)"%(n,k))
        return ZZ(ans)

##########################
# Partitions Greatest LE #
##########################
class PartitionsGreatestLE(IntegerListsLex):
    """
    Returns the combinatorial class of all (unordered) "restricted"
    partitions of the integer n having parts less than or equal to the
    integer k.

    EXAMPLES::

        sage: PartitionsGreatestLE(10,2)
        Partitions of 10 having parts less than or equal to 2
        sage: PartitionsGreatestLE(10,2).list()
        [[2, 2, 2, 2, 2],
         [2, 2, 2, 2, 1, 1],
         [2, 2, 2, 1, 1, 1, 1],
         [2, 2, 1, 1, 1, 1, 1, 1],
         [2, 1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

        sage: [4,3,2,1] in PartitionsGreatestLE(10,2)
        False
        sage: [2,2,2,2,2] in PartitionsGreatestLE(10,2)
        True
        sage: PartitionsGreatestLE(10,2).first().parent()
        Partitions...
    """

    def __init__(self, n, k):
        """
        TESTS::

            sage: p = PartitionsGreatestLE(10,2)
            sage: p == loads(dumps(p))
            True
            sage: p.n, p.k
            (10, 2)
        """
        IntegerListsLex.__init__(self, n, max_slope = 0, min_part=1, max_part = k)
        self.k = k

    def _repr_(self):
        """
        TESTS::

            sage: PartitionsGreatestLE(10, 2).__repr__()
            'Partitions of 10 having parts less than or equal to 2'
        """
        return "Partitions of %s having parts less than or equal to %s"%(self.n, self.k)

    _element_constructor_ = Partition_class

# For unpickling PartitionsGreatestLE objects created with sage <= 3.4.1
class PartitionsGreatestLE_nk(PartitionsGreatestLE):
    def __setstate__(self, data):
        r"""
        TESTS::

            sage: p = loads('x\x9c\x85\x8e\xbd\xaa\xc2@\x10\x85\x89\xff.>\xc4\x94\xda\x04\x15|\x04\xb1\xb1\x90\x0b[\x87I\x18\x935\xc9\xae\xb33\xda\t\xd7\xc2\xf76"biw\x0e\x9c\x9f\xef\xbfW\x08\x96\x94\x16\xa1\xcd\x9dGM\xcf\x18\xd5\xa9\x0b\xde\x1c>Jv\x91PIt\xbf\xcd|m8Y\xdc\xb9w\xe3\xfe\xdc&\xf5\xbb\x1d\x9d/%u^\xa9\xa4hZ\xac)\xfb\x18\x1e\xd8d\xfd\xf8\xe3\xa1\x1df\x1e[\xe2\x91\xdd|\x97!\x1ca\xb5\x84\n\xaf\xdd\x02\xbc\xbe\x05\x1a\x12\x01\xad\xd0C\x88@|\xc1\x064\xc0\x9a\xc7v\x16\xf2\x13\x15\x9a\x15\r\x8a\xf0\xe47\xf9;ixj\x13_u \xd8\x81\x98K\x9e>\x01\x13iVH')
            sage: p == PartitionsGreatestLE(10,2)
            True
        """
        self.__class__ = PartitionsGreatestLE
        self.__init__(data['n'], data['k'])

##########################
# Partitions Greatest EQ #
##########################
class PartitionsGreatestEQ(IntegerListsLex):
    """
    Returns combinatorial class of all (unordered) "restricted"
    partitions of the integer n having its greatest part equal to the
    integer k.

    EXAMPLES::

        sage: PartitionsGreatestEQ(10,2)
        Partitions of 10 having greatest part equal to 2
        sage: PartitionsGreatestEQ(10,2).list()
        [[2, 2, 2, 2, 2],
         [2, 2, 2, 2, 1, 1],
         [2, 2, 2, 1, 1, 1, 1],
         [2, 2, 1, 1, 1, 1, 1, 1],
         [2, 1, 1, 1, 1, 1, 1, 1, 1]]

        sage: [4,3,2,1] in PartitionsGreatestEQ(10,2)
        False
        sage: [2,2,2,2,2] in PartitionsGreatestEQ(10,2)
        True
        sage: [1]*10 in PartitionsGreatestEQ(10,2)
        False

        sage: PartitionsGreatestEQ(10,2).first().parent()
        Partitions...

    """

    def __init__(self, n, k):
        """
        TESTS::

            sage: p = PartitionsGreatestEQ(10,2)
            sage: p == loads(dumps(p))
            True
            sage: p.n, p.k
            (10, 2)
        """
        IntegerListsLex.__init__(self, n, max_slope = 0, max_part=k, floor = [k])
        self.k = k

    def _repr_(self):
        """
        TESTS::

            sage: PartitionsGreatestEQ(10,2).__repr__()
            'Partitions of 10 having greatest part equal to 2'
        """
        return "Partitions of %s having greatest part equal to %s"%(self.n, self.k)

    _element_constructor_ = Partition_class

# For unpickling PartitionsGreatestLE objects created with sage <= 3.4.1
class PartitionsGreatestEQ_nk(PartitionsGreatestEQ):
    def __setstate__(self, data):
        r"""
        TESTS::

            sage: p = loads('x\x9c\x85\x8e\xbd\x0e\x820\x14\x85\x03\x8a?\x8d\x0f\xd1Q\x97\x06y\x07\xe3\xaa&\x9d\xc9\xa5\xb9\x96\n\xb4^Z\xdcLt\xf0\xbd\xc5 qt;\'9?\xdf#V\x1e4\n\xe5\x9a\xc2X\x08\xe2\nm0\xc18\xcb\x0e\xa3\xf2\xfb\x16!\xa0\x0f\xbbcn+F\xd1\xe6I\xf1\x9d&k\x19UC\xbb5V{al@\x8d-k\xa0\xc2|44\x95Q\xf6:Q"\x93\xdcB\x834\x93\xe9o\x99\xbb3\xdf\xa6\xbc\x84[\xbf\xc0\xf5\xf7\x87\x7f 8R\x075\x0f\x8eg4\x97+W\\P\x85\\\xd5\xe0=-\xfeC\x0fIFK\x19\xd9\xb2g\x80\x9e\x81u\x85x\x03w\x0eT\xb1')
            sage: p == PartitionsGreatestEQ(10,2)
            True
    """
        self.__class__ = PartitionsGreatestEQ
        self.__init__(data['n'], data['k'])

#########################
# Restricted Partitions #
#########################
def RestrictedPartitions(n, S, k=None):
    r"""
    This function has been deprecated and will be removed in a
    future version of Sage; use Partitions() with the ``parts_in``
    keyword.

    Original docstring follows.

    A restricted partition is, like an ordinary partition, an unordered
    sum `n = p_1+p_2+\ldots+p_k` of positive integers and is
    represented by the list `p = [p_1,p_2,\ldots,p_k]`, in
    nonincreasing order. The difference is that here the `p_i`
    must be elements from the set `S`, while for ordinary
    partitions they may be elements from `[1..n]`.

    Returns the list of all restricted partitions of the positive
    integer n into sums with k summands with the summands of the
    partition coming from the set S. If k is not given all restricted
    partitions for all k are returned.

    Wraps GAP's RestrictedPartitions.

    EXAMPLES::

        sage: RestrictedPartitions(5,[3,2,1])
        doctest:...: DeprecationWarning: RestrictedPartitions is deprecated; use Partitions with the parts_in keyword instead.
        See http://trac.sagemath.org/5478 for details.
        Partitions of 5 restricted to the values [1, 2, 3]
        sage: RestrictedPartitions(5,[3,2,1]).list()
        [[3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]]
        sage: RestrictedPartitions(5,[3,2,1],4)
        Partitions of 5 restricted to the values [1, 2, 3] of length 4
        sage: RestrictedPartitions(5,[3,2,1],4).list()
        [[2, 1, 1, 1]]
    """
    from sage.misc.superseded import deprecation
    deprecation(5478, 'RestrictedPartitions is deprecated; use Partitions with the parts_in keyword instead.')
    return RestrictedPartitions_nsk(n, S, k)

class RestrictedPartitions_nsk(CombinatorialClass):
    r"""
    We are deprecating RestrictedPartitions, so this class should
    be deprecated too.

    """
    def __init__(self, n, S, k=None):
        """
        TESTS::

            sage: r = RestrictedPartitions(5,[3,2,1])
            doctest:...: DeprecationWarning: RestrictedPartitions is deprecated; use Partitions with the parts_in keyword instead.
            See http://trac.sagemath.org/5478 for details.
            sage: r == loads(dumps(r))
            True
        """
        from sage.misc.superseded import deprecation
        deprecation(5478, 'RestrictedPartitions_nsk is deprecated; use Partitions with the parts_in keyword instead.')
        self.n = n
        self.S = S
        self.S.sort()
        self.k = k

    Element = Partition_class

    def __contains__(self, x):
        """
        EXAMPLES::

            sage: [4,1] in RestrictedPartitions(5,[3,2,1])
            doctest:...: DeprecationWarning: RestrictedPartitions is deprecated; use Partitions with the parts_in keyword instead.
            See http://trac.sagemath.org/5478 for details.
            False
            sage: [3,2] in RestrictedPartitions(5,[3,2,1])
            True
            sage: [3,2] in RestrictedPartitions(5,[3,2,1],4)
            False
            sage: [2,1,1,1] in RestrictedPartitions(5,[3,2,1],4)
            True
        """
        return x in Partitions_n(self.n) and all(i in self.S for i in x) \
               and (self.k is None or len(x) == self.k)

    def __repr__(self):
        """
        EXAMPLES::

            sage: RestrictedPartitions(5,[3,2,1]).__repr__()
            doctest:...: DeprecationWarning: RestrictedPartitions is deprecated; use Partitions with the parts_in keyword instead.
            See http://trac.sagemath.org/5478 for details.
            'Partitions of 5 restricted to the values [1, 2, 3] '
            sage: RestrictedPartitions(5,[3,2,1],4).__repr__()
            'Partitions of 5 restricted to the values [1, 2, 3] of length 4'
        """
        string = "Partitions of %s restricted to the values %s "%(self.n, self.S)
        if self.k is not None:
            string += "of length %s" % self.k
        return string

    def list(self):
        r"""
        Returns the list of all restricted partitions of the positive
        integer n into sums with k summands with the summands of the
        partition coming from the set `S`. If k is not given all
        restricted partitions for all k are returned.

        Wraps GAP's RestrictedPartitions.

        EXAMPLES::

            sage: RestrictedPartitions(8,[1,3,5,7]).list()
            doctest:...: DeprecationWarning: RestrictedPartitions is deprecated; use Partitions with the parts_in keyword instead.
            See http://trac.sagemath.org/5478 for details.
            [[7, 1], [5, 3], [5, 1, 1, 1], [3, 3, 1, 1], [3, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]]
            sage: RestrictedPartitions(8,[1,3,5,7],2).list()
            [[7, 1], [5, 3]]
        """
        n = self.n
        k = self.k
        S = self.S
        if k is None:
            ans=gap.eval("RestrictedPartitions(%s,%s)"%(n,S))
        else:
            ans=gap.eval("RestrictedPartitions(%s,%s,%s)"%(n,S,k))
        result = eval(ans)
        result.reverse()
        return [Partition(p) for p in result]

    def cardinality(self):
        """
        Returns the size of RestrictedPartitions(n,S,k). Wraps GAP's
        NrRestrictedPartitions.

        EXAMPLES::

            sage: RestrictedPartitions(8,[1,3,5,7]).cardinality()
            doctest:...: DeprecationWarning: RestrictedPartitions is deprecated; use Partitions with the parts_in keyword instead.
            See http://trac.sagemath.org/5478 for details.
            doctest:...: DeprecationWarning: RestrictedPartitions_nsk is deprecated; use Partitions with the parts_in keyword instead.
            See http://trac.sagemath.org/5478 for details.
            6
            sage: RestrictedPartitions(8,[1,3,5,7],2).cardinality()
            2
        """
        n = self.n
        k = self.k
        S = self.S
        if k is None:
            ans=gap.eval("NrRestrictedPartitions(%s,%s)"%(ZZ(n),S))
        else:
            ans=gap.eval("NrRestrictedPartitions(%s,%s,%s)"%(ZZ(n),S,ZZ(k)))
        return ZZ(ans)

####################
# Partition Tuples #
####################
def PartitionTuples(n,k):
    """
    Returns the combinatorial class of k-tuples of partitions of n.
    These are are ordered list of k partitions whose sizes add up to

    TODO: reimplement in term of species.ProductSpecies and Partitions

    These describe the classes and the characters of wreath products of
    groups with k conjugacy classes with the symmetric group
    `S_n`.

    EXAMPLES::

        sage: PartitionTuples(4,2)
        2-tuples of partitions of 4
        sage: PartitionTuples(3,2).list()
        [[[3], []],
         [[2, 1], []],
         [[1, 1, 1], []],
         [[2], [1]],
         [[1, 1], [1]],
         [[1], [2]],
         [[1], [1, 1]],
         [[], [3]],
         [[], [2, 1]],
         [[], [1, 1, 1]]]
    """
    return PartitionTuples_nk(n,k)

class PartitionTuples_nk(CombinatorialClass):
    def __init__(self, n, k):
        """
        TESTS::

            sage: p = PartitionTuples(4,2)
            sage: p == loads(dumps(p))
            True
        """
        self.n = n
        self.k = k

    Element = Partition_class


    def __contains__(self, x):
        """
        EXAMPLES::

            sage: [[], [1, 1, 1]] in PartitionTuples(3,2)
            True
            sage: [[1], [1, 1, 1]] in PartitionTuples(3,2)
            False
        """
        p = Partitions_all()
        return len(x) == self.k and all(i in p for i in x)\
               and sum(sum(i) for i in x) == self.n

    def __repr__(self):
        """
        EXAMPLES::

            sage: PartitionTuples(4,2).__repr__()
            '2-tuples of partitions of 4'
        """
        return "%s-tuples of partitions of %s"%(self.k, self.n)

    def __iter__(self):
        r"""
        Returns an iterator for all k-tuples of partitions which together
        form a partition of n.

        EXAMPLES::

            sage: PartitionTuples(2,0).list() #indirect doctest
            []
            sage: PartitionTuples(2,1).list() #indirect doctest
            [[[2]], [[1, 1]]]
            sage: PartitionTuples(2,2).list() #indirect doctest
            [[[2], []], [[1, 1], []], [[1], [1]], [[], [2]], [[], [1, 1]]]
            sage: PartitionTuples(3,2).list() #indirect doctest
            [[[3], []], [[2, 1], []], [[1, 1, 1], []], [[2], [1]], [[1, 1], [1]], [[1], [2]], [[1], [1, 1]], [[], [3]], [[], [2, 1]], [[], [1, 1, 1]]]
        """
        p = [Partitions(i) for i in range(self.n+1)]
        for iv in IntegerVectors(self.n,self.k):
            for cp in CartesianProduct(*[p[i] for i in iv]):
                yield cp


    def cardinality(self):
        r"""
        Returns the number of k-tuples of partitions which together form a
        partition of n.

        Wraps GAP's NrPartitionTuples.

        EXAMPLES::

            sage: PartitionTuples(3,2).cardinality()
            10
            sage: PartitionTuples(8,2).cardinality()
            185

        Now we compare that with the result of the following GAP
        computation::

            gap> S8:=Group((1,2,3,4,5,6,7,8),(1,2));
            Group([ (1,2,3,4,5,6,7,8), (1,2) ])
            gap> C2:=Group((1,2));
            Group([ (1,2) ])
            gap> W:=WreathProduct(C2,S8);
            <permutation group of size 10321920 with 10 generators>
            gap> Size(W);
            10321920     ## = 2^8*Factorial(8), which is good:-)
            gap> Size(ConjugacyClasses(W));
            185
        """
        return ZZ(gp.eval('polcoeff(1/eta(x)^%s, %s, x)'%(self.k, self.n)))


##############
# Partitions #
##############

def Partitions(n=None, **kwargs):
    """
    Partitions(n, \*\*kwargs) returns the combinatorial class of
    integer partitions of `n`, subject to the constraints given by the
    keywords.

    Valid keywords are: ``starting``, ``ending``, ``min_part``,
    ``max_part``, ``max_length``, ``min_length``, ``length``,
    ``max_slope``, ``min_slope``, ``inner``, ``outer``, and
    ``parts_in``. They have the following meanings:

    - ``starting=p`` specifies that the partitions should all be greater
      than or equal to `p` in reverse lex order.

    - ``length=k`` specifies that the partitions have
      exactly `k` parts.

    - ``min_length=k`` specifies that the partitions have
      at least `k` parts.

    - ``min_part=k`` specifies that all parts of the
      partitions are at least `k`.

    - ``outer=p`` specifies that the partitions
      be contained inside the partition `p`.

    - ``min_slope=k`` specifies that the partitions have slope at least
      `k`; the slope is the difference between successive parts.

    - ``parts_in=S`` specifies that the partitions have parts in the set
      `S`, which can be any sequence of positive integers.

    The ``max_*`` versions, along with ``inner`` and ``ending``, work
    analogously.

    Right now, the ``parts_in``, ``starting``, and ``ending`` keyword
    arguments are mutually exclusive, both of each other and of other
    keyword arguments. If you specify, say, ``parts_in``, all other
    keyword arguments will be ignored; ``starting`` and ``ending`` work
    the same way.

    EXAMPLES: If no arguments are passed, then the combinatorial class
    of all integer partitions is returned.

    ::

        sage: Partitions()
        Partitions
        sage: [2,1] in Partitions()
        True

    If an integer `n` is passed, then the combinatorial class of integer
    partitions of `n` is returned.

    ::

        sage: Partitions(3)
        Partitions of the integer 3
        sage: Partitions(3).list()
        [[3], [2, 1], [1, 1, 1]]

    If ``starting=p`` is passed, then the combinatorial class of partitions
    greater than or equal to `p` in lexicographic order is returned.

    ::

        sage: Partitions(3, starting=[2,1])
        Partitions of the integer 3 starting with [2, 1]
        sage: Partitions(3, starting=[2,1]).list()
        [[2, 1], [1, 1, 1]]

    If ``ending=p`` is passed, then the combinatorial class of
    partitions at most `p` in lexicographic order is returned.

    ::

        sage: Partitions(3, ending=[2,1])
        Partitions of the integer 3 ending with [2, 1]
        sage: Partitions(3, ending=[2,1]).list()
        [[3], [2, 1]]

    Using ``max_slope=-1`` yields partitions into distinct parts -- each
    part differs from the next by at least 1. Use a different
    ``max_slope`` to get parts that differ by, say, 2.

    ::

        sage: Partitions(7, max_slope=-1).list()
        [[7], [6, 1], [5, 2], [4, 3], [4, 2, 1]]
        sage: Partitions(15, max_slope=-1).cardinality()
        27

    The number of partitions of `n` into odd parts equals the number of
    partitions into distinct parts. Let's test that for `n` from 10 to 20.

    ::

        sage: test = lambda n: Partitions(n, max_slope=-1).cardinality() == Partitions(n, parts_in=[1,3..n]).cardinality()
        sage: all(test(n) for n in [10..20])
        True

    The number of partitions of `n` into distinct parts that differ by
    at least 2 equals the number of partitions into parts that equal 1
    or 4 modulo 5; this is one of the Rogers-Ramanujan identities.

    ::

        sage: test = lambda n: Partitions(n, max_slope=-2).cardinality() == Partitions(n, parts_in=([1,6..n] + [4,9..n])).cardinality()
        sage: all(test(n) for n in [10..20])
        True

    Here are some more examples illustrating ``min_part``, ``max_part``,
    and ``length``.

    ::

        sage: Partitions(5,min_part=2)
        Partitions of the integer 5 satisfying constraints min_part=2
        sage: Partitions(5,min_part=2).list()
        [[5], [3, 2]]

    ::

        sage: Partitions(3,max_length=2).list()
        [[3], [2, 1]]

    ::

        sage: Partitions(10, min_part=2, length=3).list()
        [[6, 2, 2], [5, 3, 2], [4, 4, 2], [4, 3, 3]]


    Here are some further examples using various constraints::

        sage: [x for x in Partitions(4)]
        [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]
        sage: [x for x in Partitions(4, length=2)]
        [[3, 1], [2, 2]]
        sage: [x for x in Partitions(4, min_length=2)]
        [[3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]
        sage: [x for x in Partitions(4, max_length=2)]
        [[4], [3, 1], [2, 2]]
        sage: [x for x in Partitions(4, min_length=2, max_length=2)]
        [[3, 1], [2, 2]]
        sage: [x for x in Partitions(4, max_part=2)]
        [[2, 2], [2, 1, 1], [1, 1, 1, 1]]
        sage: [x for x in Partitions(4, min_part=2)]
        [[4], [2, 2]]
        sage: [x for x in Partitions(4, outer=[3,1,1])]
        [[3, 1], [2, 1, 1]]
        sage: [x for x in Partitions(4, outer=[infinity, 1, 1])]
        [[4], [3, 1], [2, 1, 1]]
        sage: [x for x in Partitions(4, inner=[1,1,1])]
        [[2, 1, 1], [1, 1, 1, 1]]
        sage: [x for x in Partitions(4, max_slope=-1)]
        [[4], [3, 1]]
        sage: [x for x in Partitions(4, min_slope=-1)]
        [[4], [2, 2], [2, 1, 1], [1, 1, 1, 1]]
        sage: [x for x in Partitions(11, max_slope=-1, min_slope=-3, min_length=2, max_length=4)]
        [[7, 4], [6, 5], [6, 4, 1], [6, 3, 2], [5, 4, 2], [5, 3, 2, 1]]
        sage: [x for x in Partitions(11, max_slope=-1, min_slope=-3, min_length=2, max_length=4, outer=[6,5,2])]
        [[6, 5], [6, 4, 1], [6, 3, 2], [5, 4, 2]]

    Note that if you specify min_part=0, then the objects produced will have
    parts equal to zero which violates some internal assumptions that the
    Partition class makes.

    ::

        sage: [x for x in Partitions(4, length=3, min_part=0)]
        doctest:... RuntimeWarning: Currently, setting min_part=0 produces Partition objects which violate internal assumptions.  Calling methods on these objects may produce errors or WRONG results!
        [[4, 0, 0], [3, 1, 0], [2, 2, 0], [2, 1, 1]]
        sage: [x for x in Partitions(4, min_length=3, min_part=0)]
        [[4, 0, 0], [3, 1, 0], [2, 2, 0], [2, 1, 1], [1, 1, 1, 1]]

    Except for very special cases, counting is done by brute force iteration
    through all the partitions. However the iteration itself has a reasonable
    complexity (constant memory, constant amortized time), which allow for
    manipulating large partitions::

        sage: Partitions(1000, max_length=1).list()
        [[1000]]

    In particular, getting the first element is also constant time::

        sage: Partitions(30, max_part=29).first()
        [29, 1]

    TESTS::

        sage: P = Partitions(5, min_part=2)
        sage: P == loads(dumps(P))
        True

        sage: repr( Partitions(5, min_part=2) )
        'Partitions of the integer 5 satisfying constraints min_part=2'

        sage: P = Partitions(5, min_part=2)
        sage: P.first().parent()
        Partitions...
        sage: [2,1] in P
        False
        sage: [2,2,1] in P
        False
        sage: [3,2] in P
        True

        sage: Partitions(5, inner=[2,1], min_length=3).list()
        [[3, 1, 1], [2, 2, 1], [2, 1, 1, 1]]
        sage: Partitions(5, inner=[2,0,0,0,0,0]).list()
        [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1]]
        sage: Partitions(6, length=2, max_slope=-1).list()
        [[5, 1], [4, 2]]
    """
    assert n != infinity, "n cannot be infinite"
    if n is None:
        assert(len(kwargs) == 0)
        return Partitions_all()
    else:
        if len(kwargs) == 0:
            if isinstance(n, (int,Integer)):
                return Partitions_n(n)
            else:
                raise ValueError, "n must be an integer"
        else:
            # FIXME: should inherit from IntegerListLex, and implement repr, or _name as a lazy attribute
            kwargs['name'] = "Partitions of the integer %s satisfying constraints %s"%(n, ", ".join( ["%s=%s"%(key, kwargs[key]) for key in sorted(kwargs.keys())] ))
            kwargs['element_constructor'] = Partition_class
            if 'parts_in' in kwargs:
                return Partitions_parts_in(n, kwargs['parts_in'])
            elif 'starting' in kwargs:
                return Partitions_starting(n, kwargs['starting'])
            elif 'ending' in kwargs:
                return Partitions_ending(n, kwargs['ending'])
            else:
                if 'min_part' not in kwargs:
                    kwargs['min_part'] = 1
                elif kwargs['min_part'] == 0:
                    from warnings import warn
                    warn("Currently, setting min_part=0 produces Partition objects which violate internal assumptions.  Calling methods on these objects may produce errors or WRONG results!", RuntimeWarning)

                if 'max_slope' not in kwargs:
                    kwargs['max_slope'] = 0
                if 'outer' in kwargs:
                    kwargs['ceiling'] = kwargs['outer']
                    if 'max_length' in kwargs:
                        kwargs['max_length'] = min( len(kwargs['outer']), kwargs['max_length'])
                    else:
                        kwargs['max_length'] = len(kwargs['outer'])
                    del kwargs['outer']

                if 'inner' in kwargs:
                    # Keep only elements that contribute
                    # We assume that inner is a partition
                    inner = [x for x in kwargs['inner'] if x > 0]
                    kwargs['floor'] = lambda i: inner[i] if i < len(inner) else 1
                    if 'min_length' in kwargs:
                        kwargs['min_length'] = max( len(inner), kwargs['min_length'])
                    else:
                        kwargs['min_length'] = len(inner)
                    del kwargs['inner']
                return IntegerListsLex(n, **kwargs)
#                return Partitions_constraints(n, **kwargs)


# Allows to pickle old constrained Partitions_constraints objects.
class Partitions_constraints(IntegerListsLex):
    def __setstate__(self, data):
        r"""
        TESTS::

            sage: dmp = 'x\x9ck`J.NLO\xd5K\xce\xcfM\xca\xccK,\xd1+H,*\xc9,\xc9\xcc\xcf\xe3\n\x80\xb1\x8a\xe3\x93\x81DIQbf^I1W!\xa3fc!Sm!\xb3F(7\x92x!Km!k(GnbE<\xc8\x88B6\x88\xb9E\x99y\xe9\xc5z@\x05\xa9\xe9\xa9E\\\xb9\x89\xd9\xa9\xf10N!{(\xa3QkP!Gq(c^\x06\x90c\x0c\xe4p\x96&\xe9\x01\x00\xc2\xe53\xfd'
            sage: sp = loads(dmp); sp
            Integer lists of sum 3 satisfying certain constraints
            sage: sp.list()
            [[2, 1], [1, 1, 1]]
        """
        n = data['n']
        self.__class__ = IntegerListsLex
        constraints = {'max_slope' : 0,
                       'min_part' : 1,
                       'element_constructor' : Partition_class}
        constraints.update(data['constraints'])
        self.__init__(n, **constraints)


class Partitions_all(InfiniteAbstractCombinatorialClass):
    def __init__(self):
        """
        TESTS::

            sage: P = Partitions()
            sage: P == loads(dumps(P))
            True
        """
        pass

    Element = Partition_class


    def cardinality(self):
        """
        Returns the number of integer partitions.

        EXAMPLES::

            sage: Partitions().cardinality()
            +Infinity
        """
        return infinity

    def __contains__(self, x):
        """
        TESTS::

            sage: P = Partitions()
            sage: Partition([2,1]) in P
            True
            sage: [2,1] in P
            True
            sage: [3,2,1] in P
            True
            sage: [1,2] in P
            False
            sage: [] in P
            True
            sage: [0] in P
            False
        """
        if isinstance(x, Partition_class):
            return True
        elif isinstance(x, __builtin__.list):
            for i in range(len(x)):
                if not isinstance(x[i], (int, Integer)):
                    return False
                if x[i] <= 0:
                    return False
                if i == 0:
                    prev = x[i]
                    continue
                if x[i] > prev:
                    return False
                prev = x[i]
            return True
        else:
            return False

    def __repr__(self):
        """
        TESTS::

            sage: repr(Partitions())
            'Partitions'
        """
        return "Partitions"

    def _infinite_cclass_slice(self, n):
        """
        Needed by InfiniteAbstractCombinatorialClass to build __iter__.

        TESTS:
            sage: Partitions()._infinite_cclass_slice(4) == Partitions(4)
            True
            sage: it = iter(Partitions())    # indirect doctest
            sage: [it.next() for i in range(10)]
            [[], [1], [2], [1, 1], [3], [2, 1], [1, 1, 1], [4], [3, 1], [2, 2]]
         """
        return Partitions_n(n)





class Partitions_n(CombinatorialClass):
    Element = Partition_class
    def __init__(self, n):
        """
        TESTS::

            sage: p = Partitions(5)
            sage: p == loads(dumps(p))
            True
        """
        self.n = n

    def __contains__(self, x):
        """
        TESTS::

            sage: p = Partitions(5)
            sage: [2,1] in p
            False
            sage: [2,2,1] in p
            True
            sage: [3,2] in p
            True
        """
        return x in Partitions_all() and sum(x)==self.n

    def __repr__(self):
        """
        TESTS::

            sage: repr( Partitions(5) )
            'Partitions of the integer 5'
        """
        return "Partitions of the integer %s"%self.n

    def _an_element_(self):
        """
        Returns a partition in ``self``.

        EXAMPLES::

            sage: Partitions(4)._an_element_()
            [3, 1]
            sage: Partitions(0)._an_element_()
            []
            sage: Partitions(1)._an_element_()
            [1]
        """
        if self.n == 0:
            lst = []
        elif self.n == 1:
            lst = [1]
        else:
            lst = [self.n-1, 1]
        return self._element_constructor_(lst)

    def cardinality(self, algorithm='default'):
        r"""
        INPUT:

        - ``algorithm``

          - (default: ``default``)

          - ``'bober'`` - use Jonathan Bober's implementation (*very*
            fast, but relatively new)

          - ``'gap'`` - use GAP (VERY *slow*)

          - ``'pari'`` - use PARI. Speed seems the same as GAP until
            `n` is in the thousands, in which case PARI is faster.

          - ``'default'`` - ``'bober'`` when k is not specified;
            otherwise use ``'gap'``.

        Use the function ``partitions(n)`` to return a
        generator over all partitions of `n`.

        It is possible to associate with every partition of the integer n a
        conjugacy class of permutations in the symmetric group on n points
        and vice versa. Therefore p(n) = NrPartitions(n) is the number of
        conjugacy classes of the symmetric group on n points.

        EXAMPLES::

            sage: v = Partitions(5).list(); v
            [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]]
            sage: len(v)
            7
            sage: Partitions(5).cardinality(algorithm='gap')
            7
            sage: Partitions(5).cardinality(algorithm='pari')
            7
            sage: Partitions(5).cardinality(algorithm='bober')
            7

        The input must be a nonnegative integer or a ValueError is raised.

        ::

            sage: Partitions(10).cardinality()
            42
            sage: Partitions(3).cardinality()
            3
            sage: Partitions(10).cardinality()
            42
            sage: Partitions(3).cardinality(algorithm='pari')
            3
            sage: Partitions(10).cardinality(algorithm='pari')
            42
            sage: Partitions(40).cardinality()
            37338
            sage: Partitions(100).cardinality()
            190569292

        A generating function for p(n) is given by the reciprocal of
        Euler's function:


        .. math::

           \sum_{n=0}^\infty p(n)x^n = \prod_{k=1}^\infty \left(\frac {1}{1-x^k} \right).



        We use Sage to verify that the first several coefficients do
        instead agree::

            sage: q = PowerSeriesRing(QQ, 'q', default_prec=9).gen()
            sage: prod([(1-q^k)^(-1) for k in range(1,9)])  ## partial product of
            1 + q + 2*q^2 + 3*q^3 + 5*q^4 + 7*q^5 + 11*q^6 + 15*q^7 + 22*q^8 + O(q^9)
            sage: [Partitions(k) .cardinality()for k in range(2,10)]
            [2, 3, 5, 7, 11, 15, 22, 30]

        REFERENCES:

        - http://en.wikipedia.org/wiki/Partition\_(number\_theory)
        """
        return number_of_partitions(self.n, algorithm=algorithm)


    def random_element(self, measure = 'uniform'):
        """
        Returns a random partitions of `n` for the specified measure.

        INPUT:

         - ``measure`` -

            - ``uniform`` - (default) pick a element for the uniform mesure.
                            see :meth:`random_element_uniform`

            - ``Plancherel`` - use plancherel measure.
                            see :meth:`random_element_plancherel`

        EXAMPLES::

            sage: Partitions(5).random_element() # random
            [2, 1, 1, 1]
            sage: Partitions(5).random_element(measure='Plancherel') # random
            [2, 1, 1, 1]
        """
        if measure == 'uniform':
            return self.random_element_uniform()
        elif measure == 'Plancherel':
            return self.random_element_plancherel()
        else:
            raise ValueError("Unkown measure: %s"%(measure))

    def random_element_uniform(self):
        """
        Returns a random partitions of `n` with uniform probability.

        EXAMPLES::

            sage: Partitions(5).random_element_uniform()  # random
            [2, 1, 1, 1]
            sage: Partitions(20).random_element_uniform() # random
            [9, 3, 3, 2, 2, 1]

        TESTS::

            sage: all(Part.random_element_uniform() in Part
            ...       for Part in map(Partitions, range(10)))
            True

        ALGORITHM:

         - It is a python Implementation of RANDPAR, see [nw] below.  The
           complexity is unkown, there may be better algorithms.  TODO: Check
           in Knuth AOCP4.

         - There is also certainly a lot of room for optimizations, see
           comments in the code.

        REFERENCES:

         - [nw] Nijenhuis, Wilf, Combinatorial Algorithms, Academic Press (1978).

        AUTHOR:

         - Florent Hivert (2009-11-23)
        """
        n = self.n
        res = [] # A dictionary of multiplicities could be faster.
        while n > 0:
            # Choose a pair d,j = 1,2..., with d*j <= n with probability
            #        d*numpart(n-d*j) / n / numpart(n)
            # and add d^j to the result partition. The resulting partitions is
            # equiprobable.

            # The following could be made faster by a clever use of floats
            rand = randrange(0, n*_numpart(n))  # cached number_of_partition

            # It is better to start by the j = 1 pairs because they are the
            # most probable. Maybe there is an even more clever order.
            for j in range(1, n+1):
                d = 1
                r = n-j        # n - d*j
                while  r >= 0:
                    rand -= d * _numpart(r)
                    if rand < 0: break
                    d +=1
                    r -= j
                else:
                    continue
                break
            res.extend([d]*j)
            n = r
        res.sort(reverse=True)
        return Partition(res)

    def random_element_plancherel(self):
        """
        Returns a random partitions of `n`.

        EXAMPLES::

            sage: Partitions(5).random_element_plancherel()   # random
            [2, 1, 1, 1]
            sage: Partitions(20).random_element_plancherel()  # random
            [9, 3, 3, 2, 2, 1]

        TESTS::

            sage: all(Part.random_element_plancherel() in Part
            ...       for Part in map(Partitions, range(10)))
            True

        ALGORITHM:

         - insert by robinson-schensted a uniform random permutations of n and
           returns the shape of the resulting tableau. The complexity is
           `O(n\ln(n))` which is likely optimal. However, the implementation
           could be optimized.

        AUTHOR:

         - Florent Hivert (2009-11-23)
        """
        return permutation.Permutations(self.n).random_element().left_tableau().shape()

    def first(self):
        """
        Returns the lexicographically first partition of a positive integer
        n. This is the partition [n].

        EXAMPLES::

            sage: Partitions(4).first()
            [4]
        """
        return Partition([self.n])

    def last(self):
        """
        Returns the lexicographically last partition of the positive
        integer n. This is the all-ones partition.

        EXAMPLES::

            sage: Partitions(4).last()
            [1, 1, 1, 1]
        """

        return Partition_class([1]*self.n)


    def __iter__(self):
        """
        An iterator for the partitions of n.

        EXAMPLES::

            sage: [x for x in Partitions(4)]
            [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]
        """
        for p in self._fast_iterator():
            yield Partition_class(p)


    def _fast_iterator(self):
        """
        A fast iterator for the partitions of n which returns lists and not
        partition types.

        EXAMPLES::

            sage: p = Partitions(4)
            sage: it = p._fast_iterator()
            sage: it.next()
            [4]
            sage: type(_)
            <type 'list'>
            sage: Partitions(-1).list()
            []
        """
        # If n is less than 0, there are no partitions
        if self.n < 0:
            return

        # base case of the recursion: zero is the sum of the empty tuple
        if self.n == 0:
            yield []
            return

        # modify the partitions of n-1 to form the partitions of n
        for p in Partitions_n(self.n-1)._fast_iterator():
            if p and (len(p) < 2 or p[-2] > p[-1]):
                yield p[:-1] + [p[-1] + 1]
            yield p + [1]


class Partitions_parts_in(CombinatorialClass):
    Element = Partition_class
    def __init__(self, n, parts):
        """
        TESTS::

            sage: p = Partitions(5, parts_in=[1,2,3])
            sage: p == loads(dumps(p))
            True
        """
        self.n = ZZ(n)
        self.parts = sorted(parts)

    def __contains__(self, x):
        """
        TESTS::

            sage: p = Partitions(5, parts_in=[1,2])
            sage: [2,1,1,1] in p
            True
            sage: [4,1] in p
            False
        """
        return (x in Partitions_all() and sum(x) == self.n and
                all(p in self.parts for p in x))

    def __repr__(self):
        """
        TESTS::

            sage: repr(Partitions(5, parts_in=[1,2,3]))
            'Partitions of the integer 5 with parts in [1, 2, 3]'
        """
        return "Partitions of the integer %s with parts in %s" % (self.n, self.parts)

    def cardinality(self):
        r"""
        Return the number of partitions with parts in `S`. Wraps GAP's
        ``NrRestrictedPartitions``.

        EXAMPLES::

            sage: Partitions(15, parts_in=[2,3,7]).cardinality()
            5

        If you can use all parts 1 through `n`, we'd better get `p(n)`::

            sage: Partitions(20, parts_in=[1..20]).cardinality() == Partitions(20).cardinality()
            True

        TESTS:

        Let's check the consistency of GAP's function and our own
        algorithm that actually generates the partitions.

        ::

            sage: ps = Partitions(15, parts_in=[1,2,3])
            sage: ps.cardinality() == len(ps.list())
            True
            sage: ps = Partitions(15, parts_in=[])
            sage: ps.cardinality() == len(ps.list())
            True
            sage: ps = Partitions(3000, parts_in=[50,100,500,1000])
            sage: ps.cardinality() == len(ps.list())
            True
            sage: ps = Partitions(10, parts_in=[3,6,9])
            sage: ps.cardinality() == len(ps.list())
            True
            sage: ps = Partitions(0, parts_in=[1,2])
            sage: ps.cardinality() == len(ps.list())
            True
        """
        # GAP complains if you give it an empty list
        if self.parts:
            return ZZ(gap.eval("NrRestrictedPartitions(%s,%s)" % (ZZ(self.n), self.parts)))
        else:
            return Integer(self.n == 0)

    def first(self):
        """
        Return the lexicographically first partition of a positive
        integer `n` with the specified parts, or None if no such
        partition exists.

        EXAMPLES::

            sage: Partitions(9, parts_in=[3,4]).first()
            [3, 3, 3]
            sage: Partitions(6, parts_in=[1..6]).first()
            [6]
            sage: Partitions(30, parts_in=[4,7,8,10,11]).first()
            [11, 11, 8]
        """
        try:
            return Partition_class(self._findfirst(self.n, self.parts[:]))
        except TypeError:
            return None

    def _findfirst(self, n, parts):
        """
        TESTS::

            sage: p = Partitions(9, parts_in=[3,4])
            sage: p._findfirst(p.n, p.parts[:])
            [3, 3, 3]
            sage: p._findfirst(0, p.parts[:])
            []
            sage: p._findfirst(p.n, [10])

        """
        if n == 0:
            return []
        else:
            while parts:
                p = parts.pop()
                for k in range(n.quo_rem(p)[0], 0, -1):
                    try:
                        return k * [p] + self._findfirst(n - k * p, parts[:])
                    except TypeError:
                        pass

    def last(self):
        """
        Returns the lexicographically last partition of the positive
        integer `n` with the specified parts, or None if no such
        partition exists.

        EXAMPLES::

            sage: Partitions(15, parts_in=[2,3]).last()
            [3, 2, 2, 2, 2, 2, 2]
            sage: Partitions(30, parts_in=[4,7,8,10,11]).last()
            [7, 7, 4, 4, 4, 4]
            sage: Partitions(10, parts_in=[3,6]).last() is None
            True
            sage: Partitions(50, parts_in=[11,12,13]).last()
            [13, 13, 12, 12]
            sage: Partitions(30, parts_in=[4,7,8,10,11]).last()
            [7, 7, 4, 4, 4, 4]

        TESTS::

            sage: Partitions(6, parts_in=[1..6]).last()
            [1, 1, 1, 1, 1, 1]
            sage: Partitions(0, parts_in=[]).last()
            []
            sage: Partitions(50, parts_in=[11,12]).last() is None
            True
        """
        try:
            return Partition_class(self._findlast(self.n, self.parts))
        except TypeError:
            return None

    def _findlast(self, n, parts):
        """
        Return the lexicographically largest partition of `n` using the
        given parts, or None if no such partition exists. This function
        is not intended to be called directly.

        INPUT:

        - ``n``: nonnegative integer
        - ``parts``: a sorted list of positive integers.

        OUTPUT::

        A list of integers in weakly decreasing order, or None. The
        output is just a list, not a Partition object.

        EXAMPLES::

            sage: ps = Partitions(1, parts_in=[1])
            sage: ps._findlast(15, [2,3])
            [3, 2, 2, 2, 2, 2, 2]
            sage: ps._findlast(9, [2,4]) is None
            True
            sage: ps._findlast(0, [])
            []
            sage: ps._findlast(100, [9,17,31])
            [31, 17, 17, 17, 9, 9]
        """
        if n < 0:
            return None
        elif n == 0:
            return []
        elif parts != []:
            p = parts[0]
            q, r = n.quo_rem(p)
            if r == 0:
                return [p] * q
            # If the smallest part doesn't divide n, try using the next
            # largest part
            else:
                for i, p in enumerate(parts[1:]):
                    rest = self._findlast(n - p, parts[:i+2])
                    if rest is not None:
                        return [p] + rest
        # If we get to here, nothing ever worked, so there's no such
        # partitions, and we return None.
        return None


    def __iter__(self):
        """
        An iterator a list of the partitions of n.

        EXAMPLES::

            sage: [x for x in Partitions(4)]
            [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]
        """
        for p in self._fast_iterator(self.n, self.parts[:]):
            yield Partition_class(p)


    def _fast_iterator(self, n, parts):
        """
        A fast iterator for the partitions of n which returns lists and
        not partition types. This function is not intended to be called
        directly.

        INPUT:

        - ``n``: nonnegative integer.

        - ``parts``: a list of parts to use. This list will be
         destroyed, so pass things here with ``foo[:]`` (or something
         equivalent) if you want to preserve your list. In particular,
         the __iter__ method needs to use ``self.parts[:]``, or else we
         forget which parts we're using!

        OUTPUT:

        A generator object for partitions of `n` with parts in
        ``parts``.

        If the parts in ``parts`` are sorted in increasing order, this
        function returns weakly decreasing lists. If ``parts`` is not
        sorted, your lists won't be, either.

        EXAMPLES::

            sage: p = Partitions(4)
            sage: it = p._fast_iterator()
            sage: it.next()
            [4]
            sage: type(_)
            <type 'list'>
        """
        if n == 0:
            yield []
        else:
            while parts:
                p = parts.pop()
                for k in range(n.quo_rem(p)[0], 0, -1):
                    for q in self._fast_iterator(n - k * p, parts[:]):
                        yield k * [p] + q

class Partitions_starting(CombinatorialClass):
    def __init__(self, n, starting_partition):
        """
        EXAMPLES::

            sage: Partitions(3, starting=[2,1])
            Partitions of the integer 3 starting with [2, 1]
            sage: Partitions(3, starting=[2,1]).list()
            [[2, 1], [1, 1, 1]]

        TESTS::

            sage: p = Partitions(3, starting=[2,1])
            sage: p == loads(dumps(p))
            True
        """
        self.n = n
        self._starting = Partition(starting_partition)

    def __repr__(self):
        """
        EXAMPLES::

            sage: Partitions(3, starting=[2,1]).__repr__()
            'Partitions of the integer 3 starting with [2, 1]'
        """
        return "Partitions of the integer %s starting with %s"%(self.n, self._starting)

    def __contains__(self, x):
        """
        EXAMPLES::

            sage: p = Partitions(3, starting=[2,1])
            sage: [1,1] in p
            False
            sage: [2,1] in p
            True
            sage: [1,1,1] in p
            True
            sage: [3] in p
            False
        """
        return x in Partitions_n(self.n) and x <= self._starting

    def first(self):
        """
        EXAMPLES::

            sage: Partitions(3, starting=[2,1]).first()
            [2, 1]
        """
        return self._starting

    def next(self, part):
        """
        EXAMPLES::

            sage: Partitions(3, starting=[2,1]).next(Partition([2,1]))
            [1, 1, 1]
        """
        return part.next()

class Partitions_ending(CombinatorialClass):
    def __init__(self, n, ending_partition):
        """
        EXAMPLES::

            sage: Partitions(4, ending=[1,1,1,1]).list()
            [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]
            sage: Partitions(4, ending=[2,2]).list()
            [[4], [3, 1], [2, 2]]
            sage: Partitions(4, ending=[4]).list()
            [[4]]

        TESTS::

            sage: p = Partitions(4, ending=[1,1,1,1])
            sage: p == loads(dumps(p))
            True
        """
        self.n = n
        self._ending = Partition(ending_partition)

    def __repr__(self):
        """
        EXAMPLES::

            sage: Partitions(4, ending=[1,1,1,1]).__repr__()
            'Partitions of the integer 4 ending with [1, 1, 1, 1]'
        """
        return "Partitions of the integer %s ending with %s"%(self.n, self._ending)

    def __contains__(self, x):
        """
        EXAMPLES::

            sage: p = Partitions(4, ending=[2,2])
            sage: [4] in p
            True
            sage: [2,1,1] in p
            False
            sage: [2,1] in p
            False
        """
        return x in Partitions_n(self.n) and x >= self._ending

    def first(self):
        """
        EXAMPLES::

            sage: Partitions(4, ending=[1,1,1,1]).first()
            [4]
        """
        return Partition_class([self.n])

    def next(self, part):
        """
        EXAMPLES::

            sage: Partitions(4, ending=[1,1,1,1]).next(Partition([4]))
            [3, 1]
            sage: Partitions(4, ending=[1,1,1,1]).next(Partition([1,1,1,1])) is None
            True
        """
        if part == self._ending:
            return None
        else:
            return part.next()


def PartitionsInBox(h, w):
    """
    Returns the combinatorial class of partitions that fit in a h by w
    box.

    EXAMPLES::

        sage: PartitionsInBox(2,2)
        Integer partitions which fit in a 2 x 2 box
        sage: PartitionsInBox(2,2).list()
        [[], [1], [1, 1], [2], [2, 1], [2, 2]]
    """
    return PartitionsInBox_hw(h, w)

class PartitionsInBox_hw(CombinatorialClass):
    def __init__(self, h, w):
        """
        TESTS::

            sage: p = PartitionsInBox(2,2)
            sage: p == loads(dumps(p))
            True
        """
        self.h = h
        self.w = w
        self._name = "Integer partitions which fit in a %s x %s box" % (self.h, self.w)

    Element = Partition_class

    def __contains__(self, x):
        """
        EXAMPLES::

            sage: [] in PartitionsInBox(2,2)
            True
            sage: [2,1] in PartitionsInBox(2,2)
            True
            sage: [3,1] in PartitionsInBox(2,2)
            False
            sage: [2,1,1] in PartitionsInBox(2,2)
            False
        """
        return x in Partitions_all() and len(x) <= self.h \
               and (len(x) == 0 or x[0] <= self.w)

    def list(self):
        """
        Returns a list of all the partitions inside a box of height h and
        width w.

        EXAMPLES::

            sage: PartitionsInBox(2,2).list()
            [[], [1], [1, 1], [2], [2, 1], [2, 2]]

         TESTS::

            sage: type(PartitionsInBox(0,0)[0]) # check for 10890
            <class 'sage.combinat.partition.Partition_class'>
        """
        h = self.h
        w = self.w
        if h == 0:
            return [Partition([])]
        else:
            l = [[i] for i in range(0, w+1)]
            add = lambda x: [ x+[i] for i in range(0, x[-1]+1)]
            for i in range(h-1):
                new_list = []
                for element in l:
                    new_list += add(element)
                l = new_list

            return [Partition(filter(lambda x: x!=0, p)) for p in l]


#########################################################################

#### partitions

def partitions_set(S,k=None, use_file=True):
    r"""
    An unordered partition of a set `S` is a set of pairwise
    disjoint nonempty subsets with union `S` and is represented
    by a sorted list of such subsets.

    partitions_set returns the list of all unordered partitions of the
    list `S` of increasing positive integers into k pairwise
    disjoint nonempty sets. If k is omitted then all partitions are
    returned.

    The Bell number `B_n`, named in honor of Eric Temple Bell,
    is the number of different partitions of a set with n elements.

    .. warning::

       Wraps GAP - hence S must be a list of objects that have string
       representations that can be interpreted by the GAP
       interpreter. If mset consists of at all complicated Sage
       objects, this function does *not* do what you expect. See
       SetPartitions in ``combinat/set_partition``.

    .. warning::

       This function is inefficient. The runtime is dominated by
       parsing the output from GAP.

    Wraps GAP's PartitionsSet.

    EXAMPLES::

        sage: S = [1,2,3,4]
        sage: partitions_set(S,2)
        [[[1], [2, 3, 4]],
         [[1, 2], [3, 4]],
         [[1, 2, 3], [4]],
         [[1, 2, 4], [3]],
         [[1, 3], [2, 4]],
         [[1, 3, 4], [2]],
         [[1, 4], [2, 3]]]

    REFERENCES:

    - http://en.wikipedia.org/wiki/Partition_of_a_set
    """
    if k is None:
        ans=gap("PartitionsSet(%s)"%S).str(use_file=use_file)
    else:
        ans=gap("PartitionsSet(%s,%s)"%(S,k)).str(use_file=use_file)
    return eval(ans)

def number_of_partitions_set(S,k):
    r"""
    Returns the size of ``partitions_set(S,k)``. Wraps
    GAP's NrPartitionsSet.

    The Stirling number of the second kind is the number of partitions
    of a set of size n into k blocks.

    EXAMPLES::

        sage: mset = [1,2,3,4]
        sage: number_of_partitions_set(mset,2)
        7
        sage: stirling_number2(4,2)
        7

    REFERENCES

    - http://en.wikipedia.org/wiki/Partition_of_a_set
    """
    if k is None:
        ans=gap.eval("NrPartitionsSet(%s)"%S)
    else:
        ans=gap.eval("NrPartitionsSet(%s,%s)"%(S,ZZ(k)))
    return ZZ(ans)

def partitions_list(n,k=None):
    r"""
    This function will be deprecated in a future version of Sage and
    eventually removed. Use Partitions(n).list() or Partitions(n,
    length=k).list() instead.

    Original docstring follows.

    An unordered partition of `n` is an unordered sum
    `n = p_1+p_2 +\ldots+ p_k` of positive integers and is
    represented by the list `p = [p_1,p_2,\ldots,p_k]`, in
    nonincreasing order, i.e., `p1\geq p_2 ...\geq p_k`.

    INPUT:


    -  ``n, k`` - positive integer


    ``partitions_list(n,k)`` returns the list of all
    (unordered) partitions of the positive integer n into sums with k
    summands. If k is omitted then all partitions are returned.

    Do not call partitions_list with an n much larger than 40, in
    which case there are 37338 partitions, since the list will simply
    become too large.

    Wraps GAP's Partitions.

    EXAMPLES::

        sage: partitions_list(10,2)
        [[5, 5], [6, 4], [7, 3], [8, 2], [9, 1]]
        sage: partitions_list(5)
        [[1, 1, 1, 1, 1], [2, 1, 1, 1], [2, 2, 1], [3, 1, 1], [3, 2], [4, 1], [5]]
    """
    n = ZZ(n)
    if n <= 0:
        raise ValueError, "n (=%s) must be a positive integer"%n
    if k is None:
        ans=gap.eval("Partitions(%s)"%(n))
    else:
        ans=gap.eval("Partitions(%s,%s)"%(n,k))
    return eval(ans.replace('\n',''))


def number_of_partitions(n,k=None, algorithm='default'):
    r"""
    Returns the size of partitions_list(n,k).

    INPUT:


    -  ``n`` - an integer

    -  ``k`` - (default: None); if specified, instead
       returns the cardinality of the set of all (unordered) partitions of
       the positive integer n into sums with k summands.

    -  ``algorithm`` - (default: 'default')

    -  ``'default'`` - If k is not None, then use Gap (very
       slow). If k is None, use Jonathan Bober's highly optimized
       implementation (this is the fastest code in the world for this
       problem).

    -  ``'bober'`` - use Jonathan Bober's implementation

    -  ``'gap'`` - use GAP (VERY *slow*)

    -  ``'pari'`` - use PARI. Speed seems the same as GAP until
       `n` is in the thousands, in which case PARI is
       faster. *But* PARI has a bug, e.g., on 64-bit Linux
       PARI-2.3.2 outputs numbpart(147007)%1000 as 536 when it should
       be 533!. So do not use this option.


    IMPLEMENTATION: Wraps GAP's NrPartitions or PARI's numbpart
    function.

    Use the function ``partitions(n)`` to return a
    generator over all partitions of `n`.

    It is possible to associate with every partition of the integer n a
    conjugacy class of permutations in the symmetric group on n points
    and vice versa. Therefore p(n) = NrPartitions(n) is the number of
    conjugacy classes of the symmetric group on n points.

    EXAMPLES::

        sage: v = list(partitions(5)); v
        [(1, 1, 1, 1, 1), (1, 1, 1, 2), (1, 2, 2), (1, 1, 3), (2, 3), (1, 4), (5,)]
        sage: len(v)
        7
        sage: number_of_partitions(5, algorithm='gap')
        7
        sage: number_of_partitions(5, algorithm='pari')
        7
        sage: number_of_partitions(5, algorithm='bober')
        7

    The input must be a nonnegative integer or a ValueError is raised.

    ::

        sage: number_of_partitions(-5)
        Traceback (most recent call last):
        ...
        ValueError: n (=-5) must be a nonnegative integer

    ::

        sage: number_of_partitions(10,2)
        5
        sage: number_of_partitions(10)
        42
        sage: number_of_partitions(3)
        3
        sage: number_of_partitions(10)
        42
        sage: number_of_partitions(3, algorithm='pari')
        3
        sage: number_of_partitions(10, algorithm='pari')
        42
        sage: number_of_partitions(40)
        37338
        sage: number_of_partitions(100)
        190569292
        sage: number_of_partitions(100000)
        27493510569775696512677516320986352688173429315980054758203125984302147328114964173055050741660736621590157844774296248940493063070200461792764493033510116079342457190155718943509725312466108452006369558934464248716828789832182345009262853831404597021307130674510624419227311238999702284408609370935531629697851569569892196108480158600569421098519

    A generating function for p(n) is given by the reciprocal of
    Euler's function:


    .. math::

             \sum_{n=0}^\infty p(n)x^n = \prod_{k=1}^\infty \left(\frac {1}{1-x^k} \right).



    We use Sage to verify that the first several coefficients do
    instead agree::

        sage: q = PowerSeriesRing(QQ, 'q', default_prec=9).gen()
        sage: prod([(1-q^k)^(-1) for k in range(1,9)])  ## partial product of
        1 + q + 2*q^2 + 3*q^3 + 5*q^4 + 7*q^5 + 11*q^6 + 15*q^7 + 22*q^8 + O(q^9)
        sage: [number_of_partitions(k) for k in range(2,10)]
        [2, 3, 5, 7, 11, 15, 22, 30]

    REFERENCES:

    - http://en.wikipedia.org/wiki/Partition\_(number\_theory)

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

        sage: len([n for n in [1..500] if number_of_partitions(n) != number_of_partitions(n,algorithm='pari')])
        0
    """
    n = ZZ(n)
    if n < 0:
        raise ValueError, "n (=%s) must be a nonnegative integer"%n
    elif n == 0:
        return ZZ(1)

    if algorithm == 'default':
        if k is None:
            algorithm = 'bober'
        else:
            algorithm = 'gap'

    if algorithm == 'gap':
        if k is None:
            ans=gap.eval("NrPartitions(%s)"%(ZZ(n)))
        else:
            ans=gap.eval("NrPartitions(%s,%s)"%(ZZ(n),ZZ(k)))
        return ZZ(ans)

    if k is not None:
        raise ValueError, "only the GAP algorithm works if k is specified."

    if algorithm == 'bober':
        return partitions_ext.number_of_partitions(n)

    elif algorithm == 'pari':
        return ZZ(pari(ZZ(n)).numbpart())

    raise ValueError, "unknown algorithm '%s'"%algorithm


# Some function e.g.: Partitions(n).random() heavily use number_of_partitions
# so I'm caching the result
from sage.misc.all import cached_function
_numpart = cached_function(number_of_partitions)

def partitions(n):
    r"""
    Generator of all the partitions of the integer `n`.

    INPUT:


    -  ``n`` - int


    To compute the number of partitions of `n` use
    ``number_of_partitions(n)``.

    EXAMPLES::

        sage: partitions(3)
        <generator object partitions at 0x...>
        sage: list(partitions(3))
        [(1, 1, 1), (1, 2), (3,)]

    AUTHORS:

    - Adapted from David Eppstein, Jan Van lent, George Yoshida;
      Python Cookbook 2, Recipe 19.16.
    """
    n = ZZ(n)
    # base case of the recursion: zero is the sum of the empty tuple
    if n == 0:
        yield ( )
        return
    # modify the partitions of n-1 to form the partitions of n
    for p in partitions(n-1):
        yield (1,) + p
        if p and (len(p) < 2 or p[1] > p[0]):
            yield (p[0] + 1,) + p[1:]

def cyclic_permutations_of_partition(partition):
    """
    Returns all combinations of cyclic permutations of each cell of the
    partition.

    AUTHORS:

    - Robert L. Miller

    EXAMPLES::

        sage: from sage.combinat.partition import cyclic_permutations_of_partition
        sage: cyclic_permutations_of_partition([[1,2,3,4],[5,6,7]])
        [[[1, 2, 3, 4], [5, 6, 7]],
         [[1, 2, 4, 3], [5, 6, 7]],
         [[1, 3, 2, 4], [5, 6, 7]],
         [[1, 3, 4, 2], [5, 6, 7]],
         [[1, 4, 2, 3], [5, 6, 7]],
         [[1, 4, 3, 2], [5, 6, 7]],
         [[1, 2, 3, 4], [5, 7, 6]],
         [[1, 2, 4, 3], [5, 7, 6]],
         [[1, 3, 2, 4], [5, 7, 6]],
         [[1, 3, 4, 2], [5, 7, 6]],
         [[1, 4, 2, 3], [5, 7, 6]],
         [[1, 4, 3, 2], [5, 7, 6]]]

    Note that repeated elements are not considered equal::

        sage: cyclic_permutations_of_partition([[1,2,3],[4,4,4]])
        [[[1, 2, 3], [4, 4, 4]],
         [[1, 3, 2], [4, 4, 4]],
         [[1, 2, 3], [4, 4, 4]],
         [[1, 3, 2], [4, 4, 4]]]
    """
    return list(cyclic_permutations_of_partition_iterator(partition))

def cyclic_permutations_of_partition_iterator(partition):
    """
    Iterates over all combinations of cyclic permutations of each cell
    of the partition.

    AUTHORS:

    - Robert L. Miller

    EXAMPLES::

        sage: from sage.combinat.partition import cyclic_permutations_of_partition
        sage: list(cyclic_permutations_of_partition_iterator([[1,2,3,4],[5,6,7]]))
        [[[1, 2, 3, 4], [5, 6, 7]],
         [[1, 2, 4, 3], [5, 6, 7]],
         [[1, 3, 2, 4], [5, 6, 7]],
         [[1, 3, 4, 2], [5, 6, 7]],
         [[1, 4, 2, 3], [5, 6, 7]],
         [[1, 4, 3, 2], [5, 6, 7]],
         [[1, 2, 3, 4], [5, 7, 6]],
         [[1, 2, 4, 3], [5, 7, 6]],
         [[1, 3, 2, 4], [5, 7, 6]],
         [[1, 3, 4, 2], [5, 7, 6]],
         [[1, 4, 2, 3], [5, 7, 6]],
         [[1, 4, 3, 2], [5, 7, 6]]]

    Note that repeated elements are not considered equal::

        sage: list(cyclic_permutations_of_partition_iterator([[1,2,3],[4,4,4]]))
        [[[1, 2, 3], [4, 4, 4]],
         [[1, 3, 2], [4, 4, 4]],
         [[1, 2, 3], [4, 4, 4]],
         [[1, 3, 2], [4, 4, 4]]]
    """
    if len(partition) == 1:
        for i in cyclic_permutations_iterator(partition[0]):
            yield [i]
    else:
        for right in cyclic_permutations_of_partition_iterator(partition[1:]):
            for perm in cyclic_permutations_iterator(partition[0]):
                yield [perm] + right

def ferrers_diagram(pi):
    """
    Return the Ferrers diagram of pi.

    INPUT:


    -  ``pi`` - a partition, given as a list of integers.


    EXAMPLES::

        sage: print Partition([5,5,2,1]).ferrers_diagram()
        *****
        *****
        **
        *
    """
    from sage.misc.superseded import deprecation
    deprecation(5790, '"ferrers_diagram deprecated. Use Partition(pi).ferrers_diagram() instead')
    return Partition(pi).ferrers_diagram()


def ordered_partitions(n,k=None):
    r"""
    An ordered partition of `n` is an ordered sum

    .. math::

                n = p_1+p_2 + \cdots + p_k


    of positive integers and is represented by the list
    `p = [p_1,p_2,\cdots ,p_k]`. If `k` is omitted
    then all ordered partitions are returned.

    ``ordered_partitions(n,k)`` returns the list of all
    (ordered) partitions of the positive integer n into sums with k
    summands.

    Do not call ``ordered_partitions`` with an n much
    larger than 15, since the list will simply become too large.

    Wraps GAP's OrderedPartitions.

    The number of ordered partitions `T_n` of
    `\{ 1, 2, ..., n \}` has the generating function is

    .. math::

             \sum_n {T_n \over n!} x^n = {1 \over 2-e^x}.



    EXAMPLES::

        sage: ordered_partitions(10,2)
        [[1, 9], [2, 8], [3, 7], [4, 6], [5, 5], [6, 4], [7, 3], [8, 2], [9, 1]]

    ::

        sage: ordered_partitions(4)
        [[1, 1, 1, 1], [1, 1, 2], [1, 2, 1], [1, 3], [2, 1, 1], [2, 2], [3, 1], [4]]

    REFERENCES:

    - http://en.wikipedia.org/wiki/Ordered_partition_of_a_set
    """
    if k is None:
        ans=gap.eval("OrderedPartitions(%s)"%(ZZ(n)))
    else:
        ans=gap.eval("OrderedPartitions(%s,%s)"%(ZZ(n),ZZ(k)))
    return eval(ans.replace('\n',''))

def number_of_ordered_partitions(n,k=None):
    """
    Returns the size of ordered_partitions(n,k). Wraps GAP's
    NrOrderedPartitions.

    It is possible to associate with every partition of the integer n a
    conjugacy class of permutations in the symmetric group on n points
    and vice versa. Therefore p(n) = NrPartitions(n) is the number of
    conjugacy classes of the symmetric group on n points.

    EXAMPLES::

        sage: number_of_ordered_partitions(10,2)
        9
        sage: number_of_ordered_partitions(15)
        16384
    """
    if k is None:
        ans=gap.eval("NrOrderedPartitions(%s)"%(n))
    else:
        ans=gap.eval("NrOrderedPartitions(%s,%s)"%(n,k))
    return ZZ(ans)

def partitions_greatest(n,k):
    """
    Returns the list of all (unordered) "restricted" partitions of the
    integer n having parts less than or equal to the integer k.

    Wraps GAP's PartitionsGreatestLE.

    EXAMPLES::

        sage: partitions_greatest(10,2)
        [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [2, 1, 1, 1, 1, 1, 1, 1, 1],
         [2, 2, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 1, 1, 1, 1],
         [2, 2, 2, 2, 1, 1],
         [2, 2, 2, 2, 2]]
    """
    return eval(gap.eval("PartitionsGreatestLE(%s,%s)"%(ZZ(n),ZZ(k))))

def partitions_greatest_eq(n,k):
    """
    Returns the list of all (unordered) "restricted" partitions of the
    integer n having at least one part equal to the integer k.

    Wraps GAP's PartitionsGreatestEQ.

    EXAMPLES::

        sage: partitions_greatest_eq(10,2)
        [[2, 1, 1, 1, 1, 1, 1, 1, 1],
         [2, 2, 1, 1, 1, 1, 1, 1],
         [2, 2, 2, 1, 1, 1, 1],
         [2, 2, 2, 2, 1, 1],
         [2, 2, 2, 2, 2]]
    """
    ans = gap.eval("PartitionsGreatestEQ(%s,%s)"%(n,k))
    return eval(ans)

def partitions_restricted(n,S,k=None):
    r"""
    This function will be deprecated in a future version of Sage and
    eventually removed. Use RestrictedPartitions(n, S, k).list()
    instead.

    Original docstring follows.

    A restricted partition is, like an ordinary partition, an unordered
    sum `n = p_1+p_2+\ldots+p_k` of positive integers and is
    represented by the list `p = [p_1,p_2,\ldots,p_k]`, in
    nonincreasing order. The difference is that here the `p_i`
    must be elements from the set `S`, while for ordinary
    partitions they may be elements from `[1..n]`.

    Returns the list of all restricted partitions of the positive
    integer n into sums with k summands with the summands of the
    partition coming from the set `S`. If k is not given all
    restricted partitions for all k are returned.

    Wraps GAP's RestrictedPartitions.

    EXAMPLES::

        sage: partitions_restricted(8,[1,3,5,7])
        [[1, 1, 1, 1, 1, 1, 1, 1],
         [3, 1, 1, 1, 1, 1],
         [3, 3, 1, 1],
         [5, 1, 1, 1],
         [5, 3],
         [7, 1]]
        sage: partitions_restricted(8,[1,3,5,7],2)
        [[5, 3], [7, 1]]
    """
    if k is None:
        ans=gap.eval("RestrictedPartitions(%s,%s)"%(n,S))
    else:
        ans=gap.eval("RestrictedPartitions(%s,%s,%s)"%(n,S,k))
    return eval(ans)

def number_of_partitions_restricted(n,S,k=None):
    """
    This function will be deprecated in a future version of Sage and
    eventually removed. Use RestrictedPartitions(n, S, k).cardinality()
    instead.

    Original docstring follows.

    Returns the size of partitions_restricted(n,S,k). Wraps GAP's
    NrRestrictedPartitions.

    EXAMPLES::

        sage: number_of_partitions_restricted(8,[1,3,5,7])
        6
        sage: number_of_partitions_restricted(8,[1,3,5,7],2)
        2
    """
    if k is None:
        ans=gap.eval("NrRestrictedPartitions(%s,%s)"%(ZZ(n),S))
    else:
        ans=gap.eval("NrRestrictedPartitions(%s,%s,%s)"%(ZZ(n),S,ZZ(k)))
    return ZZ(ans)

def partitions_tuples(n,k):
    """
    partition_tuples( n, k ) returns the list of all k-tuples of
    partitions which together form a partition of n.

    k-tuples of partitions describe the classes and the characters of
    wreath products of groups with k conjugacy classes with the
    symmetric group `S_n`.

    Wraps GAP's PartitionTuples.

    EXAMPLES::

        sage: partitions_tuples(3,2)
        [[[1, 1, 1], []],
         [[1, 1], [1]],
         [[1], [1, 1]],
         [[], [1, 1, 1]],
         [[2, 1], []],
         [[1], [2]],
         [[2], [1]],
         [[], [2, 1]],
         [[3], []],
         [[], [3]]]
    """
    ans=gap.eval("PartitionTuples(%s,%s)"%(ZZ(n),ZZ(k)))
    return eval(ans)

def number_of_partitions_tuples(n,k):
    r"""
    number_of_partition_tuples( n, k ) returns the number of
    partition_tuples(n,k).

    Wraps GAP's NrPartitionTuples.

    EXAMPLES::

        sage: number_of_partitions_tuples(3,2)
        10
        sage: number_of_partitions_tuples(8,2)
        185

    Now we compare that with the result of the following GAP
    computation::

                gap> S8:=Group((1,2,3,4,5,6,7,8),(1,2));
                Group([ (1,2,3,4,5,6,7,8), (1,2) ])
                gap> C2:=Group((1,2));
                Group([ (1,2) ])
                gap> W:=WreathProduct(C2,S8);
                <permutation group of size 10321920 with 10 generators>
                gap> Size(W);
                10321920     ## = 2^8*Factorial(8), which is good:-)
                gap> Size(ConjugacyClasses(W));
                185
    """
    ans=gap.eval("NrPartitionTuples(%s,%s)"%(ZZ(n),ZZ(k)))
    return ZZ(ans)

def partition_power(pi,k):
    """
    partition_power( pi, k ) returns the partition corresponding to
    the `k`-th power of a permutation with cycle structure ``pi``
    (thus describes the powermap of symmetric groups).

    Wraps GAP's PowerPartition.

    EXAMPLES::

        sage: partition_power([5,3],1)
        [5, 3]
        sage: partition_power([5,3],2)
        [5, 3]
        sage: partition_power([5,3],3)
        [5, 1, 1, 1]
        sage: partition_power([5,3],4)
        [5, 3]

    Now let us compare this to the power map on `S_8`::

        sage: G = SymmetricGroup(8)
        sage: g = G([(1,2,3,4,5),(6,7,8)])
        sage: g
        (1,2,3,4,5)(6,7,8)
        sage: g^2
        (1,3,5,2,4)(6,8,7)
        sage: g^3
        (1,4,2,5,3)
        sage: g^4
        (1,5,4,3,2)(6,7,8)
    """
    ans=gap.eval("PowerPartition(%s,%s)"%(pi,ZZ(k)))
    return eval(ans)

def partition_sign(pi):
    r"""
    ** This function is being deprecated -- use Partition(*).sign() instead.  **

    Partition( pi ).sign() returns the sign of a permutation with cycle
    structure given by the partition pi.

    This function corresponds to a homomorphism from the symmetric
    group `S_n` into the cyclic group of order 2, whose kernel
    is exactly the alternating group `A_n`. Partitions of sign
    `1` are called even partitions while partitions of sign
    `-1` are called odd.

    This function is deprecated: use Partition( pi ).sign() instead.

    EXAMPLES::

        sage: Partition([5,3]).sign()
        1
        sage: Partition([5,2]).sign()
        -1

    Zolotarev's lemma states that the Legendre symbol
    `\left(\frac{a}{p}\right)` for an integer
    `a \pmod p` (`p` a prime number), can be computed
    as sign(p_a), where sign denotes the sign of a permutation and
    p_a the permutation of the residue classes `\pmod p`
    induced by modular multiplication by `a`, provided
    `p` does not divide `a`.

    We verify this in some examples.

    ::

        sage: F = GF(11)
        sage: a = F.multiplicative_generator();a
        2
        sage: plist = [int(a*F(x)) for x in range(1,11)]; plist
        [2, 4, 6, 8, 10, 1, 3, 5, 7, 9]

    This corresponds to the permutation (1, 2, 4, 8, 5, 10, 9, 7, 3, 6)
    (acting the set `\{1,2,...,10\}`) and to the partition
    [10].

    ::

        sage: p = PermutationGroupElement('(1, 2, 4, 8, 5, 10, 9, 7, 3, 6)')
        sage: p.sign()
        -1
        sage: Partition([10]).sign()
        -1
        sage: kronecker_symbol(11,2)
        -1

    Now replace `2` by `3`::

        sage: plist = [int(F(3*x)) for x in range(1,11)]; plist
        [3, 6, 9, 1, 4, 7, 10, 2, 5, 8]
        sage: range(1,11)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        sage: p = PermutationGroupElement('(3,4,8,7,9)')
        sage: p.sign()
        1
        sage: kronecker_symbol(3,11)
        1
        sage: Partition([5,1,1,1,1,1]).sign()
        1

    In both cases, Zolotarev holds.

    REFERENCES:

    - http://en.wikipedia.org/wiki/Zolotarev's_lemma
    """
    from sage.misc.superseded import deprecation
    deprecation(5790, '"partition_sign deprecated. Use Partition(pi).sign() instead')
    return Partition(pi).sign()

def partition_associated(pi):
    """
    ** This function is being deprecated -- use Partition(*).conjugate() instead.  **

    partition_associated( pi ) returns the "associated" (also called
    "conjugate" in the literature) partition of the partition pi which
    is obtained by transposing the corresponding Ferrers diagram.

    EXAMPLES::

        sage: Partition([2,2]).conjugate()
        [2, 2]
        sage: Partition([6,3,1]).conjugate()
        [3, 2, 2, 1, 1, 1]
        sage: print Partition([6,3,1]).ferrers_diagram()
        ******
        ***
        *
        sage: print Partition([6,3,1]).conjugate().ferrers_diagram()
        ***
        **
        **
        *
        *
        *
    """
    from sage.misc.superseded import deprecation
    deprecation(5790, '"partition_associated deprecated. Use Partition(pi).conjugte() instead')
    return Partition(pi).conjugate()
