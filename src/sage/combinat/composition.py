r"""
Integer compositions

A composition `c` of a nonnegative integer `n` is a list of positive integers
(the *parts* of the compositions) with total sum `n`.

This module provides tools for manipulating compositions and enumerated
sets of compositions.

EXAMPLES::

    sage: Composition([5, 3, 1, 3])
    [5, 3, 1, 3]
    sage: list(Compositions(4))
    [[1, 1, 1, 1], [1, 1, 2], [1, 2, 1], [1, 3], [2, 1, 1], [2, 2], [3, 1], [4]]


AUTHORS:

- Mike Hansen, Nicolas M. Thiery
- MuPAD-Combinat developers (algorithms and design inspiration)
- Travis Scrimshaw (2013-02-03): Removed ``CombinatorialClass``
"""
#*****************************************************************************
#       Copyright (C) 2007 Mike Hansen       <mhansen@gmail.com>
#                     2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#              http://www.gnu.org/licenses/
#*****************************************************************************

from sage.categories.infinite_enumerated_sets import InfiniteEnumeratedSets
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.structure.element import Element
from sage.misc.classcall_metaclass import ClasscallMetaclass
from sage.misc.superseded import deprecated_function_alias
from sage.rings.all import ZZ
import sage.combinat.skew_partition
from combinat import CombinatorialObject
from cartesian_product import CartesianProduct
from integer_list import IntegerListsLex
import __builtin__
from sage.rings.integer import Integer

class Composition(CombinatorialObject, Element):
    r"""
    Integer compositions

    A composition of a nonnegative integer `n` is a list
    `(i_1, \ldots, i_k)` of positive integers with total sum `n`.

    EXAMPLES:

    The simplest way to create a composition is by specifying its
    entries as a list, tuple (or other iterable)::

        sage: Composition([3,1,2])
        [3, 1, 2]
        sage: Composition((3,1,2))
        [3, 1, 2]
        sage: Composition(i for i in range(2,5))
        [2, 3, 4]

    You can also create a composition from its code. The *code* of
    a composition `(i_1, i_2, \ldots, i_k)` of `n` is a list of length `n`
    that consists of a `1` followed by `i_1-1` zeros, then a `1` followed
    by `i_2-1` zeros, and so on.

    ::

        sage: Composition([4,1,2,3,5]).to_code()
        [1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        sage: Composition(code=_)
        [4, 1, 2, 3, 5]
        sage: Composition([3,1,2,3,5]).to_code()
        [1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        sage: Composition(code=_)
        [3, 1, 2, 3, 5]

    You can also create the composition of `n` corresponding to a subset of
    `\{1, 2, \ldots, n-1\}` under the bijection that maps the composition
    `(i_1, i_2, \ldots, i_k)` of `n` to the subset
    `\{i_1, i_1 + i_2, i_1 + i_2 + i_3, \ldots, i_1 + \cdots + i_{k-1}\}`
    (see :meth:`to_subset`)::

        sage: Composition(from_subset=({1, 2, 4}, 5))
        [1, 1, 2, 1]
        sage: Composition([1, 1, 2, 1]).to_subset()
        {1, 2, 4}

    The following notation equivalently specifies the composition from the
    set `\{i_1 - 1, i_1 + i_2 - 1, i_1 + i_2 + i_3 - 1, \dots, i_1 + \cdots
    + i_{k-1} - 1, n-1\}` or `\{i_1 - 1, i_1 + i_2 - 1, i_1 + i_2 + i_3
    - 1, \dots, i_1 + \cdots + i_{k-1} - 1\}` and `n`. This provides
    compatibility with Python's `0`-indexing.

    ::

        sage: Composition(descents=[1,0,4,8,11])
        [1, 1, 3, 4, 3]
        sage: Composition(descents=[0,1,3,4])
        [1, 1, 2, 1]
        sage: Composition(descents=([0,1,3],5))
        [1, 1, 2, 1]
        sage: Composition(descents=({0,1,3},5))
        [1, 1, 2, 1]
    """
    __metaclass__ = ClasscallMetaclass

    @staticmethod
    def __classcall_private__(cls, co=None, descents=None, code=None, from_subset=None):
        """
        This constructs a list from optional arguments and delegates the
        construction of a :class:`Composition` to the ``element_class()`` call
        of the appropriate parent.

        EXAMPLES::

            sage: Composition([3,2,1])
            [3, 2, 1]
            sage: Composition(from_subset=({1, 2, 4}, 5))
            [1, 1, 2, 1]
            sage: Composition(descents=[1,0,4,8,11])
            [1, 1, 3, 4, 3]
            sage: Composition([4,1,2,3,5]).to_code()
            [1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]
            sage: Composition(code=_)
            [4, 1, 2, 3, 5]
        """
        if descents is not None:
            if isinstance(descents, tuple):
                return Compositions().from_descents(descents[0], nps=descents[1])
            else:
                return Compositions().from_descents(descents)
        elif code is not None:
            return Compositions().from_code(code)
        elif from_subset is not None:
            return Compositions().from_subset(*from_subset)
        elif isinstance(co, Composition):
            return co
        else:
            return Compositions()(list(co))

    def __init__(self, parent, lst):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: C = Composition([3,1,2])
            sage: TestSuite(C).run()
        """
        CombinatorialObject.__init__(self, lst)
        Element.__init__(self, parent)

    def __setstate__(self, state):
        r"""
        In order to maintain backwards compatibility and be able to unpickle a
        old pickle from ``Partition_class`` we have to override the default
        ``__setstate__``.

        EXAMPLES::

            sage: loads("x\x9ck`J.NLO\xd5K\xce\xcfM\xca\xccK,\x011\n\xf2\x8b3K2\xf3\xf3\xb8\x9c\x11\xec\xf8\xe4\x9c\xc4\xe2b\xaeBF\xcd\xc6B\xa6\xdaBf\x8dP\xd6\xf8\x8c\xc4\xe2\x8cB\x16? +'\xb3\xb8\xa4\x905\xb6\x90M\x03bZQf^z\xb1^f^Ijzj\x11Wnbvj<\x8cS\xc8\x1e\xcah\xd8\x1aT\xc8\x91\x01d\x18\x01\x19\x9c\x19P\x11\xae\xd4\xd2$=\x00eW0g")
            [1, 2, 1]
            sage: loads(dumps( Composition([1,2,1]) ))  # indirect doctest
            [1, 2, 1]
        """
        if isinstance(state, dict):   # for old pickles from Composition_class
            self._set_parent(Compositions())
            self.__dict__ = state
        else:
            self._set_parent(state[0])
            self.__dict__ = state[1]

    def conjugate(self):
        r"""
        Returns the conjugate of the composition comp.

        Algorithm from mupad-combinat.

        EXAMPLES::

            sage: Composition([1, 1, 3, 1, 2, 1, 3]).conjugate()
            [1, 1, 3, 3, 1, 3]
        """
        comp = self
        if comp == []:
            return Composition([])
        n = len(comp)
        coofcp = [sum(comp[:j])-j+1 for j in range(1,n+1)]

        cocjg = []
        for i in range(n-1):
            cocjg += [i+1 for _ in range(0, (coofcp[n-i-1]-coofcp[n-i-2]))]
        cocjg += [n for j in range(coofcp[0])]

        return self.parent()([cocjg[0]] + [cocjg[i]-cocjg[i-1]+1 for i in range(1,len(cocjg))])

    def reversed(self):
        """
        Return the reverse composition of ``self``.

        EXAMPLES::

            sage: Composition([1, 1, 3, 1, 2, 1, 3]).reversed()
            [3, 1, 2, 1, 3, 1, 1]
        """
        return self.parent()(reversed(self))

    def complement(self):
        """
        Return the complement composition of ``self``. The complement is the
        reverse of the conjugate composition of ``self``.

        EXAMPLES::

            sage: Composition([1, 1, 3, 1, 2, 1, 3]).conjugate()
            [1, 1, 3, 3, 1, 3]
            sage: Composition([1, 1, 3, 1, 2, 1, 3]).complement()
            [3, 1, 3, 3, 1, 1]
        """
        return self.conjugate().reversed()

    def __add__(self, other):
        """
        Return the concatenation of two compositions.

        EXAMPLES::

            sage: Composition([1, 1, 3]) + Composition([4, 1, 2])
            [1, 1, 3, 4, 1, 2]

        TESTS::

            sage: Composition([]) + Composition([]) == Composition([])
            True
        """
        return Composition(list(self)+list(other))

    def size(self):
        """
        Return the size of ``self``, that is the sum of its parts.

        EXAMPLES::

            sage: Composition([7,1,3]).size()
            11
        """
        return sum(self)

    @staticmethod
    def sum(compositions):
        """
        Return the concatenation of the given compositions.

        INPUT:

        - ``compositions`` -- a list (or iterable) of compositions

        EXAMPLES::

            sage: Composition.sum([Composition([1, 1, 3]), Composition([4, 1, 2]), Composition([3,1])])
            [1, 1, 3, 4, 1, 2, 3, 1]

        Any iterable can be provided as input::

            sage: Composition.sum([Composition([i,i]) for i in [4,1,3]])
            [4, 4, 1, 1, 3, 3]

        Empty inputs are handled gracefully::

            sage: Composition.sum([]) == Composition([])
            True
        """
        return sum(compositions, Composition([]))

    def finer(self):
        """
        Return the set of compositions which are finer than ``self``.

        EXAMPLES::

            sage: C = Composition([3,2]).finer()
            sage: C.cardinality()
            8
            sage: list(C)
            [[1, 1, 1, 1, 1], [1, 1, 1, 2], [1, 2, 1, 1], [1, 2, 2], [2, 1, 1, 1], [2, 1, 2], [3, 1, 1], [3, 2]]
        """
        return CartesianProduct(*[Compositions(i) for i in self]).map(Composition.sum)

    def is_finer(self, co2):
        """
        Return ``True`` if the composition ``self`` is finer than the
        composition ``co2``; otherwise, it returns ``False``.

        EXAMPLES::

            sage: Composition([4,1,2]).is_finer([3,1,3])
            False
            sage: Composition([3,1,3]).is_finer([4,1,2])
            False
            sage: Composition([1,2,2,1,1,2]).is_finer([5,1,3])
            True
            sage: Composition([2,2,2]).is_finer([4,2])
            True
        """
        co1 = self
        if sum(co1) != sum(co2):
            raise ValueError("compositions self (= %s) and co2 (= %s) must be of the same size"%(self, co2))

        sum1 = 0
        sum2 = 0
        i1 = 0
        for i2 in range(len(co2)):
            sum2 += co2[i2]
            while sum1 < sum2:
                sum1 += co1[i1]
                i1 += 1
            if sum1 > sum2:
                return False

        return True

    def fatten(self, grouping):
        r"""
        Return the composition fatter than ``self``, obtained by grouping
        together consecutive parts according to grouping.

        INPUT:

        - ``grouping`` -- a composition whose sum is the length of ``self``

        EXAMPLES:

        Let us start with the composition::

            sage: c = Composition([4,5,2,7,1])

        With ``grouping`` equal to `(1, \ldots, 1)`, `c` is left unchanged::

            sage: c.fatten(Composition([1,1,1,1,1]))
            [4, 5, 2, 7, 1]

        With ``grouping`` equal to `(\ell)` where `\ell` is the length of
        ``self``, this yields the coarser composition above `c`::

            sage: c.fatten(Composition([5]))
            [19]

        Other values for ``grouping`` yield (all the) other compositions
        coarser to `c`::

            sage: c.fatten(Composition([2,1,2]))
            [9, 2, 8]
            sage: c.fatten(Composition([3,1,1]))
            [11, 7, 1]

        TESTS::

            sage: Composition([]).fatten(Composition([]))
            []
            sage: c.fatten(Composition([3,1,1])).__class__ == c.__class__
            True
        """
        result = [None] * len(grouping)
        j = 0
        for i in range(len(grouping)):
            result[i] = sum(self[j:j+grouping[i]])
            j += grouping[i]
        return Composition(result)

    def fatter(self):
        """
        Return the set of compositions which are fatter than ``self``.

        Complexity for generation: `O(|c|)` memory, `O(|r|)` time where `|c|`
        is the size of ``self`` and `r` is the result.

        EXAMPLES::

            sage: C = Composition([4,5,2]).fatter()
            sage: C.cardinality()
            4
            sage: list(C)
            [[4, 5, 2], [4, 7], [9, 2], [11]]

        Some extreme cases::

            sage: list(Composition([5]).fatter())
            [[5]]
            sage: list(Composition([]).fatter())
            [[]]
            sage: list(Composition([1,1,1,1]).fatter()) == list(Compositions(4))
            True
        """
        return Compositions(len(self)).map(self.fatten)

    def refinement_splitting(self, J):
        r"""
        Return the refinement splitting of ``self`` according to ``J``.

        INPUT:

        - ``J`` -- A composition such that ``I`` is finer than ``J``

        OUTPUT:

        - the unique list of compositions `(I^{(p)})_{p=1\ldots m}`,
          obtained by splitting `I`, such that
          `|I^{(p)}| = J_p` for all `p = 1, \ldots, m`.

        .. SEEALSO::

            :meth:`refinement_splitting_lengths`

        EXAMPLES::

            sage: Composition([1,2,2,1,1,2]).refinement_splitting([5,1,3])
            [[1, 2, 2], [1], [1, 2]]
            sage: Composition([]).refinement_splitting([])
            []
            sage: Composition([3]).refinement_splitting([2])
            Traceback (most recent call last):
            ...
            ValueError: compositions self (= [3]) and J (= [2]) must be of the same size
            sage: Composition([2,1]).refinement_splitting([1,2])
            Traceback (most recent call last):
            ...
            ValueError: composition J (= [2, 1]) does not refine self (= [1, 2])
        """
        I = self
        if sum(I) != sum(J):
            #Error: compositions are not of the same size
            raise ValueError("compositions self (= %s) and J (= %s) must be of the same size"%(I, J))
        sum1 = 0
        sum2 = 0
        i1 = -1
        decomp = []
        for i2 in range(len(J)):
            new_comp = []
            sum2 += J[i2]
            while sum1 < sum2:
                i1 += 1
                new_comp.append(I[i1])
                sum1 += new_comp[-1]
            if sum1 > sum2:
                raise ValueError("composition J (= %s) does not refine self (= %s)"%(I, J))
            decomp.append(Composition(new_comp))
        return decomp

    def refinement_splitting_lengths(self, J):
        """
        Return the lengths of the compositions in the refinement splitting of
        ``I=self`` according to ``J``.

        .. SEEALSO::

            :meth:`refinement_splitting` for the definition of refinement splitting

        EXAMPLES::

            sage: Composition([1,2,2,1,1,2]).refinement_splitting_lengths([5,1,3])
            [3, 1, 2]
            sage: Composition([]).refinement_splitting_lengths([])
            []
            sage: Composition([3]).refinement_splitting_lengths([2])
            Traceback (most recent call last):
            ...
            ValueError: compositions self (= [3]) and J (= [2]) must be of the same size
            sage: Composition([2,1]).refinement_splitting_lengths([1,2])
            Traceback (most recent call last):
            ...
            ValueError: composition J (= [2, 1]) does not refine self (= [1, 2])
        """
        return Composition(map(len,self.refinement_splitting(J)))

    refinement = deprecated_function_alias(13243, refinement_splitting_lengths)

    def major_index(self):
        """
        Return the major index of ``self``. The major index is
        defined as the sum of the descents.

        EXAMPLES::

            sage: Composition([1, 1, 3, 1, 2, 1, 3]).major_index()
            31
        """
        co = self
        lv = len(co)
        if lv == 1:
            return 0
        else:
            return sum([(lv-(i+1))*co[i] for i in range(lv)])

    def to_code(self):
        """
        Return the code of the composition ``self``. The code of a composition
        is a list of length ``self.size()`` of 1s and 0s such that there is a 1
        wherever a new part starts.

        EXAMPLES::

            sage: Composition([4,1,2,3,5]).to_code()
            [1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        """
        if self == []:
            return [0]

        code = []
        for i in range(len(self)):
            code += [1] + [0]*(self[i]-1)

        return code

    def partial_sums(self, final=True):
        r"""
        The partial sums of the sequence defined by the entries of the
        composition.

        If `I = (i_1, \ldots, i_m)` is a composition, then the partial sums of
        the entries of the composition are
        `[i_1, i_1 + i_2, \ldots, i_1 + i_2 + \cdots + i_{m}]`.

        INPUT:

        - ``final`` -- (default: ``True``) whether or not to include the final
          partial sum, which is always the size of the composition.

        .. SEEALSO::

            :meth:`to_subset`

        EXAMPLES::

            sage: Composition([1,1,3,1,2,1,3]).partial_sums()
            [1, 2, 5, 6, 8, 9, 12]

        With ``final = False``, the last partial sum is not included::

            sage: Composition([1,1,3,1,2,1,3]).partial_sums(final=False)
            [1, 2, 5, 6, 8, 9]

        """
        s = 0
        partial_sums = []
        for i in self:
            s += i
            partial_sums.append(s)
        if final is False:
            partial_sums.pop()
        return partial_sums

    def to_subset(self, final=False):
        r"""
        The subset corresponding to ``self`` under the bijection (see below)
        between compositions of `n` and subsets of `\{1, 2, \ldots, n-1\}`.

        The bijection maps a composition `(i_1, \ldots, i_k)` of `n` to
        `\{i_1, i_1 + i_2, i_1 + i_2 + i_3, \ldots, i_1 + \cdots + i_{k-1}\}`.

        INPUT:

        - ``final`` -- (default: ``False``) whether or not to include the final
          partial sum, which is always the size of the composition.

        .. SEEALSO::

            :meth:`partial_sums`

        EXAMPLES::

            sage: Composition([1,1,3,1,2,1,3]).to_subset()
            {1, 2, 5, 6, 8, 9}
            sage: for I in Compositions(3): print I.to_subset()
            {1, 2}
            {1}
            {2}
            {}

        With ``final=True``, the sum of all the elements of the composition is
        included in the subset::

            sage: Composition([1,1,3,1,2,1,3]).to_subset(final=True)
            {1, 2, 5, 6, 8, 9, 12}

        TESTS:

        We verify that ``to_subset`` is indeed a bijection for compositions of
        size `n = 8`::

            sage: n = 8
            sage: all(Composition(from_subset=(S, n)).to_subset() == S \
            ...       for S in Subsets(n-1))
            True
            sage: all(Composition(from_subset=(I.to_subset(), n)) == I \
            ...       for I in Compositions(n))
            True

        """
        from sage.sets.set import Set
        return Set(self.partial_sums(final=final))

    def descents(self, final_descent=False):
        r"""
        This gives one fewer than the partial sums of the composition.

        This is here to maintain some sort of backward compatibility, even
        through the original implementation was broken (it gave the wrong
        answer). The same information can be found in :meth:`partial_sums`.

        .. SEEALSO::

            :meth:`partial_sums`

        INPUT:

        - ``final_descent`` -- (Default: ``False``) a boolean integer

        OUTPUT:

        - Returns the list of partial sums of ``self`` with each part
          subtracted by `1`. This includes the sum of all entries when
          ``final_descent`` is ``True``.

        EXAMPLES::

            sage: c = Composition([2,1,3,2])
            sage: c.descents()
            [1, 2, 5]
            sage: c.descents(final_descent=True)
            [1, 2, 5, 7]
        """
        return [i - 1 for i in self.partial_sums(final=final_descent)]

    def peaks(self):
        """
        Return a list of the peaks of the composition ``self``. The
        peaks of a composition are the descents which do not
        immediately follow another descent.

        EXAMPLES::

            sage: Composition([1, 1, 3, 1, 2, 1, 3]).peaks()
            [4, 7]
        """
        descents = dict((d-1,True) for d in self.to_subset(final=True))
        return [i+1 for i in range(len(self))
                if i not in descents and i+1 in descents]

    def to_partition(self):
        """
        Sorts ``self`` into decreasing order and returns the corresponding
        partition.

        EXAMPLES::

            sage: Composition([2,1,3]).to_partition()
            [3, 2, 1]
            sage: Composition([4,2,2]).to_partition()
            [4, 2, 2]
        """
        from sage.combinat.partition import Partition
        return Partition(sorted(self, reverse=True))

    def to_skew_partition(self, overlap=1):
        """
        Return the skew partition obtained from ``self``. The
        parameter overlap indicates the number of cells that are covered by
        cells of the previous line.

        EXAMPLES::

            sage: Composition([3,4,1]).to_skew_partition()
            [[6, 6, 3], [5, 2]]
            sage: Composition([3,4,1]).to_skew_partition(overlap=0)
            [[8, 7, 3], [7, 3]]
        """
        outer = []
        inner = []
        sum_outer = -1*overlap

        for k in range(len(self)-1):
            outer += [ self[k]+sum_outer+overlap  ]
            sum_outer += self[k]-overlap
            inner += [ sum_outer + overlap ]

        if self != []:
            outer += [self[-1]+sum_outer+overlap]
        else:
            return [[],[]]

        return sage.combinat.skew_partition.SkewPartition(
            [ filter(lambda x: x != 0, [l for l in reversed(outer)]),
              filter(lambda x: x != 0, [l for l in reversed(inner)])])


    def shuffle_product(self, other, overlap=False):
        r"""
        The (overlapping) shuffles of ``self`` and ``other``.

        Suppose `I = (i_1, \ldots, i_k)` and `J = (j_1, \ldots, j_l)` are two
        compositions. A *shuffle* of `I` and `J` is a composition of length
        `k + l` that contains both `I` and `J` as subsequences.

        More generally, an *overlapping shuffle* of `I` and `J` is obtained by
        distributing the elements of `I` and `J` (preserving the relative
        ordering of these elements) among the positions of an empty list; an
        element of `I` and an element of `J` are permitted to share the same
        position, in which case they are replaced by their sum. In particular,
        a shuffle of `I` and `J` is an overlapping shuffle of `I` and `J`.

        INPUT:

        -  ``other`` -- composition

        -  ``overlap`` -- boolean (default: ``False``); if ``True``, the
           overlapping shuffle product is returned.

        OUTPUT:

        An enumerated set (allowing for mutliplicities)

        EXAMPLES:

        The shuffle product of `[2,2]` and `[1,1,3]`::

            sage: alph = Composition([2,2])
            sage: beta = Composition([1,1,3])
            sage: S = alph.shuffle_product(beta); S
            Shuffle product of [2, 2] and [1, 1, 3]
            sage: S.list()
            [[2, 2, 1, 1, 3], [2, 1, 2, 1, 3], [2, 1, 1, 2, 3], [2, 1, 1, 3, 2], [1, 2, 2, 1, 3], [1, 2, 1, 2, 3], [1, 2, 1, 3, 2], [1, 1, 2, 2, 3], [1, 1, 2, 3, 2], [1, 1, 3, 2, 2]]

        The *overlapping* shuffle product of `[2,2]` and `[1,1,3]`::

            sage: alph = Composition([2,2])
            sage: beta = Composition([1,1,3])
            sage: O = alph.shuffle_product(beta, overlap=True); O
            Overlapping shuffle product of [2, 2] and [1, 1, 3]
            sage: O.list()
            [[2, 2, 1, 1, 3], [2, 1, 2, 1, 3], [2, 1, 1, 2, 3], [2, 1, 1, 3, 2], [1, 2, 2, 1, 3], [1, 2, 1, 2, 3], [1, 2, 1, 3, 2], [1, 1, 2, 2, 3], [1, 1, 2, 3, 2], [1, 1, 3, 2, 2], [3, 2, 1, 3], [2, 3, 1, 3], [3, 1, 2, 3], [2, 1, 3, 3], [3, 1, 3, 2], [2, 1, 1, 5], [1, 3, 2, 3], [1, 2, 3, 3], [1, 3, 3, 2], [1, 2, 1, 5], [1, 1, 5, 2], [1, 1, 2, 5], [3, 3, 3], [3, 1, 5], [1, 3, 5]]

        Note that the shuffle product of two compositions can include the same
        composition more than once since a composition can be a shuffle of two
        compositions in several ways. For example::

            sage: S = Composition([1]).shuffle_product([1]); S
            Shuffle product of [1] and [1]
            sage: S.list()
            [[1, 1], [1, 1]]
            sage: O = Composition([1]).shuffle_product([1], overlap=True); O
            Overlapping shuffle product of [1] and [1]
            sage: O.list()
            [[1, 1], [1, 1], [2]]

        TESTS::

            sage: Composition([]).shuffle_product([]).list()
            [[]]

        """
        if overlap:
            from sage.combinat.words.shuffle_product import ShuffleProduct_overlapping
            return ShuffleProduct_overlapping(self, other)
        else:
            from sage.combinat.words.shuffle_product import ShuffleProduct_w1w2
            return ShuffleProduct_w1w2(self, other)

##############################################################

class Compositions(Parent, UniqueRepresentation):
    r"""
    Set of integer compositions.

    A composition `c` of a nonnegative integer `n` is a list of
    positive integers with total sum `n`.

    .. SEEALSO::

        - :class:`Composition`
        - :class:`Partitions`
        - :class:`IntegerVectors`

    EXAMPLES:

    There are 8 compositions of 4::

        sage: Compositions(4).cardinality()
        8

    Here is the list of them::

        sage: Compositions(4).list()
        [[1, 1, 1, 1], [1, 1, 2], [1, 2, 1], [1, 3], [2, 1, 1], [2, 2], [3, 1], [4]]

    You can use the ``.first()`` method to get the 'first' composition of
    a number::

        sage: Compositions(4).first()
        [1, 1, 1, 1]

    You can also calculate the 'next' composition given the current
    one::

        sage: Compositions(4).next([1,1,2])
        [1, 2, 1]

    If `n` is not specified, this returns the combinatorial class of
    all (non-negative) integer compositions::

        sage: Compositions()
        Compositions of non-negative integers
        sage: [] in Compositions()
        True
        sage: [2,3,1] in Compositions()
        True
        sage: [-2,3,1] in Compositions()
        False

    If `n` is specified, it returns the class of compositions of `n`::

        sage: Compositions(3)
        Compositions of 3
        sage: list(Compositions(3))
        [[1, 1, 1], [1, 2], [2, 1], [3]]
        sage: Compositions(3).cardinality()
        4

    The following examples show how to test whether or not an object
    is a composition::

        sage: [3,4] in Compositions()
        True
        sage: [3,4] in Compositions(7)
        True
        sage: [3,4] in Compositions(5)
        False

    Similarly, one can check whether or not an object is a composition
    which satisfies further constraints::

        sage: [4,2] in Compositions(6, inner=[2,2])
        True
        sage: [4,2] in Compositions(6, inner=[2,3])
        False
        sage: [4,1] in Compositions(5, inner=[2,1], max_slope = 0)
        True

    Note that the given constraints should be compatible::

        sage: [4,2] in Compositions(6, inner=[2,2], min_part=3)
        True

    The options ``length``, ``min_length``, and ``max_length`` can be used
    to set length constraints on the compositions. For example, the
    compositions of 4 of length equal to, at least, and at most 2 are
    given by::

        sage: Compositions(4, length=2).list()
        [[3, 1], [2, 2], [1, 3]]
        sage: Compositions(4, min_length=2).list()
        [[3, 1], [2, 2], [2, 1, 1], [1, 3], [1, 2, 1], [1, 1, 2], [1, 1, 1, 1]]
        sage: Compositions(4, max_length=2).list()
        [[4], [3, 1], [2, 2], [1, 3]]

    Setting both ``min_length`` and ``max_length`` to the same value is
    equivalent to setting ``length`` to this value::

        sage: Compositions(4, min_length=2, max_length=2).list()
        [[3, 1], [2, 2], [1, 3]]

    The options ``inner`` and ``outer`` can be used to set part-by-part
    containment constraints. The list of compositions of 4 bounded
    above by ``[3,1,2]`` is given by::

        sage: list(Compositions(4, outer=[3,1,2]))
        [[3, 1], [2, 1, 1], [1, 1, 2]]

    ``outer`` sets ``max_length`` to the length of its argument. Moreover, the
    parts of ``outer`` may be infinite to clear the constraint on specific
    parts. This is the list of compositions of 4 of length at most 3
    such that the first and third parts are at most 1::

        sage: Compositions(4, outer=[1,oo,1]).list()
        [[1, 3], [1, 2, 1]]

    This is the list of compositions of 4 bounded below by ``[1,1,1]``::

        sage: Compositions(4, inner=[1,1,1]).list()
        [[2, 1, 1], [1, 2, 1], [1, 1, 2], [1, 1, 1, 1]]

    The options ``min_slope`` and ``max_slope`` can be used to set constraints
    on the slope, that is the difference ``p[i+1]-p[i]`` of two
    consecutive parts. The following is the list of weakly increasing
    compositions of 4::

        sage: Compositions(4, min_slope=0).list()
        [[4], [2, 2], [1, 3], [1, 1, 2], [1, 1, 1, 1]]

    Here are the weakly decreasing ones::

        sage: Compositions(4, max_slope=0).list()
        [[4], [3, 1], [2, 2], [2, 1, 1], [1, 1, 1, 1]]


    The following is the list of compositions of 4 such that two
    consecutive parts differ by at most one::

        sage: Compositions(4, min_slope=-1, max_slope=1).list()
        [[4], [2, 2], [2, 1, 1], [1, 2, 1], [1, 1, 2], [1, 1, 1, 1]]

    The constraints can be combined together in all reasonable ways.
    This is the list of compositions of 5 of length between 2 and 4
    such that the difference between consecutive parts is between -2
    and 1::

        sage: Compositions(5, max_slope=1, min_slope=-2, min_length=2, max_length=4).list()
        [[3, 2], [3, 1, 1], [2, 3], [2, 2, 1], [2, 1, 2], [2, 1, 1, 1], [1, 2, 2], [1, 2, 1, 1], [1, 1, 2, 1], [1, 1, 1, 2]]

    We can do the same thing with an outer constraint::

        sage: Compositions(5, max_slope=1, min_slope=-2, min_length=2, max_length=4, outer=[2,5,2]).list()
        [[2, 3], [2, 2, 1], [2, 1, 2], [1, 2, 2]]

    However, providing incoherent constraints may yield strange
    results. It is up to the user to ensure that the inner and outer
    compositions themselves satisfy the parts and slope constraints.

    Note that if you specify ``min_part=0``, then the objects produced may
    have parts equal to zero. This violates the internal assumptions
    that the composition class makes. Use at your own risk, or
    preferably consider using ``IntegerVectors`` instead::

        sage: Compositions(2, length=3, min_part=0).list()
        doctest:... RuntimeWarning: Currently, setting min_part=0 produces Composition objects which violate internal assumptions.  Calling methods on these objects may produce errors or WRONG results!
        [[2, 0, 0], [1, 1, 0], [1, 0, 1], [0, 2, 0], [0, 1, 1], [0, 0, 2]]

        sage: list(IntegerVectors(2, 3))
        [[2, 0, 0], [1, 1, 0], [1, 0, 1], [0, 2, 0], [0, 1, 1], [0, 0, 2]]

    The generation algorithm is constant amortized time, and handled
    by the generic tool :class:`IntegerListsLex`.

    TESTS::

        sage: C = Compositions(4, length=2)
        sage: C == loads(dumps(C))
        True

        sage: Compositions(6, min_part=2, length=3)
        Compositions of the integer 6 satisfying constraints length=3, min_part=2

        sage: [2, 1] in Compositions(3, length=2)
        True
        sage: [2,1,2] in Compositions(5, min_part=1)
        True
        sage: [2,1,2] in Compositions(5, min_part=2)
        False

        sage: Compositions(4, length=2).cardinality()
        3
        sage: Compositions(4, min_length=2).cardinality()
        7
        sage: Compositions(4, max_length=2).cardinality()
        4
        sage: Compositions(4, max_part=2).cardinality()
        5
        sage: Compositions(4, min_part=2).cardinality()
        2
        sage: Compositions(4, outer=[3,1,2]).cardinality()
        3

        sage: Compositions(4, length=2).list()
        [[3, 1], [2, 2], [1, 3]]
        sage: Compositions(4, min_length=2).list()
        [[3, 1], [2, 2], [2, 1, 1], [1, 3], [1, 2, 1], [1, 1, 2], [1, 1, 1, 1]]
        sage: Compositions(4, max_length=2).list()
        [[4], [3, 1], [2, 2], [1, 3]]
        sage: Compositions(4, max_part=2).list()
        [[2, 2], [2, 1, 1], [1, 2, 1], [1, 1, 2], [1, 1, 1, 1]]
        sage: Compositions(4, min_part=2).list()
        [[4], [2, 2]]
        sage: Compositions(4, outer=[3,1,2]).list()
        [[3, 1], [2, 1, 1], [1, 1, 2]]
        sage: Compositions(3, outer = Composition([3,2])).list()
        [[3], [2, 1], [1, 2]]
        sage: Compositions(4, outer=[1,oo,1]).list()
        [[1, 3], [1, 2, 1]]
        sage: Compositions(4, inner=[1,1,1]).list()
        [[2, 1, 1], [1, 2, 1], [1, 1, 2], [1, 1, 1, 1]]
        sage: Compositions(4, inner=Composition([1,2])).list()
        [[2, 2], [1, 3], [1, 2, 1]]
        sage: Compositions(4, min_slope=0).list()
        [[4], [2, 2], [1, 3], [1, 1, 2], [1, 1, 1, 1]]
        sage: Compositions(4, min_slope=-1, max_slope=1).list()
        [[4], [2, 2], [2, 1, 1], [1, 2, 1], [1, 1, 2], [1, 1, 1, 1]]
        sage: Compositions(5, max_slope=1, min_slope=-2, min_length=2, max_length=4).list()
        [[3, 2], [3, 1, 1], [2, 3], [2, 2, 1], [2, 1, 2], [2, 1, 1, 1], [1, 2, 2], [1, 2, 1, 1], [1, 1, 2, 1], [1, 1, 1, 2]]
        sage: Compositions(5, max_slope=1, min_slope=-2, min_length=2, max_length=4, outer=[2,5,2]).list()
        [[2, 3], [2, 2, 1], [2, 1, 2], [1, 2, 2]]
    """
    @staticmethod
    def __classcall_private__(self, n=None, **kwargs):
        """
        Return the correct parent based upon the input.

        EXAMPLES::

            sage: C = Compositions(3)
            sage: C2 = Compositions(int(3))
            sage: C is C2
            True
        """
        if n is None:
            if len(kwargs) != 0:
                raise ValueError("Incorrect number of arguments")
            return Compositions_all()
        else:
            if len(kwargs) == 0:
                if isinstance(n, (int,Integer)):
                    return Compositions_n(n)
                else:
                    raise ValueError("n must be an integer")
            else:
                # FIXME: should inherit from IntegerListLex, and implement repr, or _name as a lazy attribute
                kwargs['name'] = "Compositions of the integer %s satisfying constraints %s"%(n, ", ".join( ["%s=%s"%(key, kwargs[key]) for key in sorted(kwargs.keys())] ))
                kwargs['element_class'] = Composition
                if 'min_part' not in kwargs:
                    kwargs['min_part'] = 1
                elif kwargs['min_part'] == 0:
                    from warnings import warn
                    warn("Currently, setting min_part=0 produces Composition objects which violate internal assumptions.  Calling methods on these objects may produce errors or WRONG results!", RuntimeWarning)

                if 'outer' in kwargs:
                    kwargs['ceiling'] = list(kwargs['outer'])
                    if 'max_length' in kwargs:
                        kwargs['max_length'] = min(len(kwargs['outer']), kwargs['max_length'])
                    else:
                        kwargs['max_length'] = len(kwargs['outer'])
                    del kwargs['outer']

                if 'inner' in kwargs:
                    inner = list(kwargs['inner'])
                    kwargs['floor'] = inner
                    del kwargs['inner']
                    # Should this be handled by integer lists lex?
                    if 'min_length' in kwargs:
                        kwargs['min_length'] = max(len(inner), kwargs['min_length'])
                    else:
                        kwargs['min_length'] = len(inner)
                return IntegerListsLex(n, **kwargs)

    def __init__(self, is_infinite=False):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: C = Compositions()
            sage: TestSuite(C).run()
        """
        if is_infinite:
            Parent.__init__(self, category=InfiniteEnumeratedSets())
        else:
            Parent.__init__(self, category=FiniteEnumeratedSets())

    Element = Composition

    def _element_constructor_(self, lst):
        """
        Construct an element with ``self`` as parent.

        EXAMPLES::

            sage: P = Compositions()
            sage: P([3,3,1]) # indirect doctest
            [3, 3, 1]
        """
        if isinstance(lst, Composition):
            lst = list(lst)
        elt = self.element_class(self, lst)
        if elt not in self:
            raise ValueError("%s not in %s"%(elt, self))
        return elt

    def __contains__(self, x):
        """
        TESTS::

            sage: [2,1,3] in Compositions()
            True
            sage: [] in Compositions()
            True
            sage: [-2,-1] in Compositions()
            False
            sage: [0,0] in Compositions()
            True
        """
        if isinstance(x, Composition):
            return True
        elif isinstance(x, __builtin__.list):
            for i in range(len(x)):
                if (not isinstance(x[i], (int, Integer))) and x[i] not in ZZ:
                    return False
                if x[i] < 0:
                    return False
            return True
        else:
            return False

    def from_descents(self, descents, nps=None):
        """
        Returns a composition from the list of descents.

        INPUT:

        - ``descents`` -- an iterable

        - ``nps`` -- (default: ``None``) an integer or ``None``; if ``None``, then
          ``nps`` is taken to be `1` plus the maximum element of ``descents``.

        EXAMPLES::

            sage: [x-1 for x in Composition([1, 1, 3, 4, 3]).to_subset()]
            [0, 1, 4, 8]
            sage: Compositions().from_descents([1,0,4,8],12)
            [1, 1, 3, 4, 3]
            sage: Compositions().from_descents([1,0,4,8,11])
            [1, 1, 3, 4, 3]
        """
        d = [x+1 for x in sorted(descents)]
        if nps is None:
            nps = d.pop()
        return self.from_subset(d, nps)

    def from_subset(self, S, n):
        r"""
        The composition of `n` corresponding to the subset ``S`` of
        `\{1, 2, \ldots, n-1\}` under the bijection that maps the composition
        `(i_1, i_2, \ldots, i_k)` of `n` to the subset
        `\{i_1, i_1 + i_2, i_1 + i_2 + i_3, \ldots, i_1 + \cdots + i_{k-1}\}`
        (see :meth:`Composition.to_subset`).

        INPUT:

        - ``S`` -- an iterable, a subset of `n-1`

        - ``n`` -- an integer

        EXAMPLES::

            sage: Compositions().from_subset([2,1,5,9], 12)
            [1, 1, 3, 4, 3]
            sage: Compositions().from_subset({2,1,5,9}, 12)
            [1, 1, 3, 4, 3]

        TESTS::

            sage: Compositions().from_subset([2,1,5,9],9)
            Traceback (most recent call last):
            ...
            ValueError: S (=[1, 2, 5, 9]) is not a subset of {1, ..., 8}
        """
        d = sorted(S)

        if d == []:
            if n == 0:
                return self.element_class(self, [])
            else:
                return self.element_class(self, [n])

        if n <= max(d):
            raise ValueError, "S (=%s) is not a subset of {1, ..., %s}" % (d,n-1)
        elif n > max(d):
            d.append(n)

        co = [d[0]]
        for i in range(len(d)-1):
            co += [ d[i+1]-d[i] ]

        return self.element_class(self, co)

    def from_code(self, code):
        """
        Return the composition from its code. The code of a composition is a
        list of length ``self.size()`` of 1s and 0s such that there is a 1
        wherever a new part starts.

        EXAMPLES::

            sage: Composition([4,1,2,3,5]).to_code()
            [1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]
            sage: Compositions().from_code(_)
            [4, 1, 2, 3, 5]
            sage: Composition([3,1,2,3,5]).to_code()
            [1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]
            sage: Compositions().from_code(_)
            [3, 1, 2, 3, 5]
        """
        if code == [0]:
            return []

        L = filter(lambda x: code[x]==1, range(len(code))) #the positions of the letter 1
        return self.element_class(self, [L[i]-L[i-1] for i in range(1, len(L))] + [len(code)-L[-1]])

# Allows to unpickle old constrained Compositions_constraints objects.
class Compositions_constraints(IntegerListsLex):
    def __setstate__(self, data):
        """
        TESTS::

            # This is the unpickling sequence for Compositions(4, max_part=2) in sage <= 4.1.1
            sage: pg_Compositions_constraints = unpickle_global('sage.combinat.composition', 'Compositions_constraints')
            sage: si = unpickle_newobj(pg_Compositions_constraints, ())
            sage: pg_make_integer = unpickle_global('sage.rings.integer', 'make_integer')
            sage: unpickle_build(si, {'constraints':{'max_part':pg_make_integer('2')}, 'n':pg_make_integer('4')})
            sage: si
            Integer lists of sum 4 satisfying certain constraints
            sage: si.list()
            [[2, 2], [2, 1, 1], [1, 2, 1], [1, 1, 2], [1, 1, 1, 1]]
        """
        n = data['n']
        self.__class__ = IntegerListsLex
        constraints = {'min_part' : 1,
                       'element_class' : Composition}
        constraints.update(data['constraints'])
        self.__init__(n, **constraints)

class Compositions_all(Compositions):
    """
    Class of all compositions.
    """
    def __init__(self):
        """
        Initialize ``self``.

        TESTS::

            sage: C = Compositions()
            sage: TestSuite(C).run()
        """
        Compositions.__init__(self, True)

    def _repr_(self):
        """
        Return a string representation of ``self``.

        TESTS::

            sage: repr(Compositions())
            'Compositions of non-negative integers'
        """
        return "Compositions of non-negative integers"

    def subset(self, size=None):
        """
        Return the set of compositions of the given size.

        EXAMPLES::

            sage: C = Compositions()
            sage: C.subset(4)
            Compositions of 4
            sage: C.subset(size=3)
            Compositions of 3
        """
        if size is None:
            return self
        return Compositions(size)

    def __iter__(self):
        """
        Iterate over all compositions.

        TESTS::

            sage: C = Compositions()
            sage: it = C.__iter__()
            sage: [it.next() for i in range(10)]
            [[], [1], [1, 1], [2], [1, 1, 1], [1, 2], [2, 1], [3], [1, 1, 1, 1], [1, 1, 2]]
        """
        n = 0
        while True:
            for c in Compositions(n):
                yield self.element_class(self, list(c))
            n += 1

class Compositions_n(Compositions):
    """
    Class of compositions of a fixed `n`.
    """
    @staticmethod
    def __classcall_private__(cls, n):
        """
        Standardize input to ensure a unique representation.

        EXAMPLES::

            sage: C = Compositions(5)
            sage: C2 = Compositions(int(5))
            sage: C3 = Compositions(ZZ(5))
            sage: C is C2
            True
            sage: C is C3
            True
        """
        return super(Compositions_n, cls).__classcall__(cls, Integer(n))

    def __init__(self, n):
        """
        TESTS::

            sage: C = Compositions(3)
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()
        """
        self.n = n
        Compositions.__init__(self, False)

    def _repr_(self):
        """
        Return a string representation of ``self``.

        TESTS::

            sage: repr(Compositions(3))
            'Compositions of 3'
        """
        return "Compositions of %s"%self.n

    def __contains__(self, x):
        """
        TESTS::

            sage: [2,1,3] in Compositions(6)
            True
            sage: [2,1,2] in Compositions(6)
            False
            sage: [] in Compositions(0)
            True
            sage: [0] in Compositions(0)
            True
        """
        return x in Compositions() and sum(x) == self.n

    def cardinality(self):
        """
        Return the number of compositions of `n`.

        TESTS::

            sage: Compositions(3).cardinality()
            4
            sage: Compositions(0).cardinality()
            1
        """
        if self.n >= 1:
            return 2**(self.n-1)
        elif self.n == 0:
            return 1
        else:
            return 0

    def __iter__(self):
        """
        Iterate over the compositions of `n`.

        TESTS::

            sage: Compositions(4).list()
            [[1, 1, 1, 1], [1, 1, 2], [1, 2, 1], [1, 3], [2, 1, 1], [2, 2], [3, 1], [4]]
            sage: Compositions(0).list()
            [[]]
        """
        if self.n == 0:
            yield self.element_class(self, [])
            return

        for i in range(1,self.n+1):
            for c in Compositions_n(self.n-i):
                yield self.element_class(self, [i]+list(c))

def from_descents(descents, nps=None):
    r"""
    This has been deprecated in :trac:`14063`. Use
    :meth:`Compositions.from_descents()` instead.

    EXAMPLES::

        sage: [x-1 for x in Composition([1, 1, 3, 4, 3]).to_subset()]
        [0, 1, 4, 8]
        sage: sage.combinat.composition.from_descents([1,0,4,8],12)
        doctest:1: DeprecationWarning: from_descents is deprecated. Use Compositions().from_descents instead.
        See http://trac.sagemath.org/14063 for details.
        [1, 1, 3, 4, 3]
    """
    from sage.misc.superseded import deprecation
    deprecation(14063, 'from_descents is deprecated. Use Compositions().from_descents instead.')
    return Compositions().from_descents(descents, nps)

def composition_from_subset(S, n):
    r"""
    This has been deprecated in :trac:`14063`. Use
    :meth:`Compositions.from_subset()` instead.

    EXAMPLES::

        sage: from sage.combinat.composition import composition_from_subset
        sage: composition_from_subset([2,1,5,9], 12)
        doctest:1: DeprecationWarning: composition_from_subset is deprecated. Use Compositions().from_subset instead.
        See http://trac.sagemath.org/14063 for details.
        [1, 1, 3, 4, 3]
    """
    from sage.misc.superseded import deprecation
    deprecation(14063, 'composition_from_subset is deprecated. Use Compositions().from_subset instead.')
    return Compositions().from_subset(S, n)

def from_code(code):
    r"""
    This has been deprecated in :trac:`14063`. Use
    :meth:`Compositions.from_code()` instead.

    EXAMPLES::

        sage: import sage.combinat.composition as composition
        sage: Composition([4,1,2,3,5]).to_code()
        [1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]
        sage: composition.from_code(_)
        doctest:1: DeprecationWarning: from_code is deprecated. Use Compositions().from_code instead.
        See http://trac.sagemath.org/14063 for details.
        [4, 1, 2, 3, 5]
    """
    from sage.misc.superseded import deprecation
    deprecation(14063, 'from_code is deprecated. Use Compositions().from_code instead.')
    return Compositions().from_code(code)

from sage.structure.sage_object import register_unpickle_override
register_unpickle_override('sage.combinat.composition', 'Composition_class', Composition)
