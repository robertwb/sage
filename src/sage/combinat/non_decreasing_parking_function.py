r"""
Non Decreasing Parking Functions

A **non decreasing parking functions** of size `n` is a non decreasing
function `f` from `\{1,\dots,n\}` to itself such that for all `i`, one
has `f(i) \leq i`.

The number of non decreasing parking functions of size `n` is the `n`-th
:func:`catalan number<sage.combinat.combinat.catalan_number>`.

The set of non decreasing parking functions of size `n` is in bijection with
the set of :mod:`Dyck words<sage.combinat.dyck_word>` of size `n`.

AUTHORS:

-Florent Hivert
"""
#*****************************************************************************
#       Copyright (C) 2007 Florent Hivert <Florent.Hivert@univ-rouen.fr>,
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
from sage.rings.integer import Integer
from sage.sets.set import Set_object_enumerated
from combinat import (CombinatorialClass, CombinatorialObject,
                      InfiniteAbstractCombinatorialClass, catalan_number)
from composition import Compositions
from copy import copy


def NonDecreasingParkingFunctions(n=None):
    r"""
    Returns the combinatorial class of Non Decreasing Parking Functions.

    A *non decreasing parking functions* of size `n` is a non
    decreasing function `f` from `\{1,\dots,n\}` to itself such that
    for all `i`, one has `f(i) \leq i`.

    EXAMPLES:

    Here are all the non decreasing parking functions of size 5::

      sage: NonDecreasingParkingFunctions(3).list()
      [[1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 2, 2], [1, 2, 3]]

    If no size is specified, then NonDecreasingParkingFunctions
    returns the combinatorial class of all nondecreasing parking functions.

    ::

         sage: PF = NonDecreasingParkingFunctions(); PF
         Non decreasing parking functions
         sage: [] in PF
         True
         sage: [1] in PF
         True
         sage: [2] in PF
         False
         sage: [1,1,3] in PF
         True
         sage: [1,1,4] in PF
         False

    If the size `n` is specified, then NonDecreasingParkingFunctions returns
    combinatorial class of all nondecreasing parking functions of size `n`.

    ::

         sage: PF = NonDecreasingParkingFunctions(0)
         sage: PF.list()
         [[]]
         sage: PF = NonDecreasingParkingFunctions(1)
         sage: PF.list()
         [[1]]
         sage: PF = NonDecreasingParkingFunctions(3)
         sage: PF.list()
         [[1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 2, 2], [1, 2, 3]]

         sage: PF3 = NonDecreasingParkingFunctions(3); PF3
         Non decreasing parking functions of size 3
         sage: [] in PF3
         False
         sage: [1] in PF3
         False
         sage: [1,1,3] in PF3
         True
         sage: [1,1,4] in PF3
         False

    TESTS::

         sage: PF = NonDecreasingParkingFunctions(5)
         sage: len(PF.list()) == PF.cardinality()
         True

    """
    if n is None:
        return NonDecreasingParkingFunctions_all()
    else:
        assert(isinstance(n, (Integer, int)) and n >= 0)
        return NonDecreasingParkingFunctions_n(n)

def is_a(x, n=None):
    """
    Check whether a list is a non decreasing parking function of size `n`.

    TESTS::

        sage: from sage.combinat.non_decreasing_parking_function import is_a
        sage: is_a([1,1,2])
        True
        sage: is_a([1,1,4])
        False
        sage: is_a([1,1,3], 3)
        True
    """
    if not isinstance(x, list):
        return False
    for i in range(len(x)-1):
        if x[i] > x[i+1] or x[i] > i+1:
            return False
    if n is not None and n != len(x):
        return False
    return x==[] or x[len(x)-1] <= len(x)


class NonDecreasingParkingFunctions_all(InfiniteAbstractCombinatorialClass):
    def __init__(self):
        """
        TESTS::

            sage: DW = NonDecreasingParkingFunctions()
            sage: DW == loads(dumps(DW))
            True
        """
        pass

    def __repr__(self):
        """
        TESTS::

            sage: repr(NonDecreasingParkingFunctions())
            'Non decreasing parking functions'
        """
        return "Non decreasing parking functions"

    def __contains__(self, x):
        """
        TESTS::

            sage: [] in NonDecreasingParkingFunctions()
            True
            sage: [1] in NonDecreasingParkingFunctions()
            True
            sage: [2] in NonDecreasingParkingFunctions()
            False
            sage: [1,1,3] in NonDecreasingParkingFunctions()
            True
            sage: [1,1,4] in NonDecreasingParkingFunctions()
            False
        """
        if isinstance(x, NonDecreasingParkingFunction):
            return True
        return is_a(x)

    def _infinite_cclass_slice(self, n):
        """
        Needed by InfiniteAbstractCombinatorialClass to buid __iter__.

        TESTS:
            sage: (NonDecreasingParkingFunctions()._infinite_cclass_slice(4)
            ...    == NonDecreasingParkingFunctions(4))
            True
            sage: it = iter(NonDecreasingParkingFunctions()) # indirect doctest
            sage: [it.next() for i in range(8)]
            [[], [1], [1, 1], [1, 2], [1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 2, 2]]
         """
        return NonDecreasingParkingFunctions_n(n)


class NonDecreasingParkingFunctions_n(CombinatorialClass):
    """
    The combinatorial class of non decreasing parking functions of a given
    size n.

    A *non decreasing parking functions* of size `n` is a non
    decreasing function `f` from `\{1,\dots,n\}` to itself such that
    for all `i`, one has `f(i) \leq i`.

    The number of non decreasing parking functions of size `n` is the
    `n`-th catalan number.

    EXAMPLES::

        sage: PF = NonDecreasingParkingFunctions(3)
        sage: PF.list()
        [[1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 2, 2], [1, 2, 3]]
        sage: PF = NonDecreasingParkingFunctions(4)
        sage: PF.list()
        [[1, 1, 1, 1], [1, 1, 1, 2], [1, 1, 1, 3], [1, 1, 1, 4], [1, 1, 2, 2], [1, 1, 2, 3], [1, 1, 2, 4], [1, 1, 3, 3], [1, 1, 3, 4], [1, 2, 2, 2], [1, 2, 2, 3], [1, 2, 2, 4], [1, 2, 3, 3], [1, 2, 3, 4]]
        sage: [ NonDecreasingParkingFunctions(i).cardinality() for i in range(10)]
        [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862]

    .. warning::

       The precise order in which the parking function are generated or
       listed is not fixed, and may change in the future.

    AUTHORS:

    -Florent Hivert
    """
    def __init__(self, n):
        """
        TESTS::

            sage: PF = NonDecreasingParkingFunctions(3)
            sage: PF == loads(dumps(PF))
            True
        """
        self.n = n

    def __repr__(self):
        """
        TESTS::

            sage: repr(NonDecreasingParkingFunctions(3))
            'Non decreasing parking functions of size 3'
        """
        return "Non decreasing parking functions of size %s"%(self.n)

    def __contains__(self, x):
        """
        TESTS::

            sage: PF3 = NonDecreasingParkingFunctions(3); PF3
            Non decreasing parking functions of size 3
            sage: [] in PF3
            False
            sage: [1] in PF3
            False
            sage: [1,1,3] in PF3
            True
            sage: [1,1,1] in PF3
            True
            sage: [1,1,4] in PF3
            False
            sage: all([p in PF3 for p in PF3])
            True
        """
        if isinstance(x, NonDecreasingParkingFunction):
            return True
        return is_a(x, self.n)

    def cardinality(self):
        """
        Returns the number of non decreasing parking functions of size n. This
        number is given by the n-th Catalan number.

        EXAMPLES::

            sage: PF = NonDecreasingParkingFunctions(0)
            sage: PF.cardinality()
            1
            sage: PF = NonDecreasingParkingFunctions(1)
            sage: PF.cardinality()
            1
            sage: PF = NonDecreasingParkingFunctions(3)
            sage: PF.cardinality()
            5
            sage: PF = NonDecreasingParkingFunctions(5)
            sage: PF.cardinality()
            42
        """
        return catalan_number(self.n)

    def __iter__(self):
        """
        Returns an iterator for non decreasing parking functions of size n.

        .. warning::

           The precise order in which the parking function are
           generated is not fixed, and may change in the future.

        EXAMPLES::

            sage: PF = NonDecreasingParkingFunctions(0)
            sage: [e for e in PF]      # indirect doctest
            [[]]
            sage: PF = NonDecreasingParkingFunctions(1)
            sage: [e for e in PF]      # indirect doctest
            [[1]]
            sage: PF = NonDecreasingParkingFunctions(3)
            sage: [e for e in PF]      # indirect doctest
            [[1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 2, 2], [1, 2, 3]]
            sage: PF = NonDecreasingParkingFunctions(4)
            sage: [e for e in PF]      # indirect doctest
            [[1, 1, 1, 1], [1, 1, 1, 2], [1, 1, 1, 3], [1, 1, 1, 4], [1, 1, 2, 2], [1, 1, 2, 3], [1, 1, 2, 4], [1, 1, 3, 3], [1, 1, 3, 4], [1, 2, 2, 2], [1, 2, 2, 3], [1, 2, 2, 4], [1, 2, 3, 3], [1, 2, 3, 4]]

        TESTS::

            sage: PF = NonDecreasingParkingFunctions(5)
            sage: [e for e in PF] == PF.list()
            True
            sage: PF = NonDecreasingParkingFunctions(6)
            sage: [e for e in PF] == PF.list()
            True

        Complexity: constant amortized time.
        """
# FIXME : currently composition is extremenly slow.
# Activate the following code as soon as compositions use
# the integer_list_lex machinery
#         for i in range(self.n, self.n*(self.n+1)/2+1):
#             for z in Compositions(i, length=self.n, outer=range(1, self.n+1),
#                                   min_slope=0).__iter__():
#                 yield NonDecreasingParkingFunction(z._list)
#         return
        def iterator_rec(n):
            """
            TESTS::

                sage: PF = NonDecreasingParkingFunctions(2)
                sage: [e for e in PF]      # indirect doctest
                [[1, 1], [1, 2]]
            """
            if n==0:
                yield [ ]; return
            if n==1:
                yield [1]; return
            for res1 in iterator_rec(n-1):
                for i in range(res1[-1], n+1):
                    res = copy(res1)
                    res.append(i)
                    yield res
            return
        for res in iterator_rec(self.n):
            yield NonDecreasingParkingFunction(res)
        return

class NonDecreasingParkingFunction(CombinatorialObject):
    """
    A *non decreasing parking function* of size `n` is a non
    decreasing function `f` from `\{1,\dots,n\}` to itself such that
    for all `i`, one has `f(i) \leq i`.

    EXAMPLES::

        sage: NonDecreasingParkingFunction([])
        []
        sage: NonDecreasingParkingFunction([1])
        [1]
        sage: NonDecreasingParkingFunction([2])
        Traceback (most recent call last):
        ...
        AssertionError
        sage: NonDecreasingParkingFunction([1,2])
        [1, 2]
        sage: NonDecreasingParkingFunction([1,1,2])
        [1, 1, 2]
        sage: NonDecreasingParkingFunction([1,1,4])
        Traceback (most recent call last):
        ...
        AssertionError
    """
    def __init__(self, lst):
        """
        TESTS::

            sage: NonDecreasingParkingFunction([1, 1, 2, 2, 5, 6])
            [1, 1, 2, 2, 5, 6]
        """
        assert(is_a(lst))
        CombinatorialObject.__init__(self, lst)

    def __getitem__(self, key):
        """
        TESTS::

            sage: NonDecreasingParkingFunction([1, 1, 2, 2, 5, 6])[3]
            2
        """
        return self._list[key-1]

    def keys(self):
        """
        TESTS::

            sage: NonDecreasingParkingFunction([1, 1, 2, 2, 5, 6]).keys()
            [1, 2, 3, 4, 5, 6]
        """
        return range(1, len(self)+1)

    def __mul__(self, lp):
        """
        The composition of non decreasing parking functions.

        EXAMPLES::

            sage: p = NonDecreasingParkingFunction([1,1,3])
            sage: q = NonDecreasingParkingFunction([1,2,2])
            sage: p * q
            [1, 1, 1]
            sage: q * p
            [1, 1, 2]
        """
        lp = lp._list
        sp = self._list
        lp = lp[:] + [i+1 for i in range(len(lp), len(lp))]
        sp = sp[:] + [i+1 for i in range(len(sp), len(lp))]
        return NonDecreasingParkingFunction([ sp[i-1] for i in lp ])

    def to_dyck_word(self):
        """
        Implements the bijection to :class:`Dyck
        words<sage.combinat.dyck_word.DyckWords>`, which is defined as follow.
        Take a non decreasing parking function, say [1,1,2,4,5,5], and draw
        its graph::

                                                 .
                                              .  |
                                           .__.__|
                                        .__|  .  .
                                     .  |  .  .  .
                                  .  .__|  .  .  .
                               .__.__|  .  .  .  .
                                 1  1  2  4  5  5

        The corresponding dyck word [1,1,0,1,0,0,1,0,1,1,0,0] is then read of
        from the sequence of horizontal and vertical steps. The converse
        bijection is :meth:`.from_dyck_word`.

        EXAMPLES::

            sage: NonDecreasingParkingFunction([1,1,2,4,5,5]).to_dyck_word()
            [1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0]
            sage: NonDecreasingParkingFunction([]).to_dyck_word()
            []
            sage: NonDecreasingParkingFunction([1,1,1]).to_dyck_word()
            [1, 1, 1, 0, 0, 0]
            sage: NonDecreasingParkingFunction([1,2,3]).to_dyck_word()
            [1, 0, 1, 0, 1, 0]
            sage: NonDecreasingParkingFunction([1,1,3,3,4,6,6]).to_dyck_word()
            [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0]

        TEST::

            sage: ndpf=NonDecreasingParkingFunctions(5);
            sage: list(ndpf) == [pf.to_dyck_word().to_non_decreasing_parking_function() for pf in ndpf]
            True
        """
        from sage.combinat.dyck_word import DyckWord_class
        return DyckWord_class.from_non_decreasing_parking_function(self)

    @classmethod
    def from_dyck_word(cls, dw):
        """
        Bijection from :class:`Dyck
        words<sage.combinat.dyck_word.DyckWords>`. It is the inverse of the
        bijection :meth:`.to_dyck_word`. You can find there the matematical
        definition.

        EXAMPLES::

          sage: NonDecreasingParkingFunction.from_dyck_word([])
          []
          sage: NonDecreasingParkingFunction.from_dyck_word([1,0])
          [1]
          sage: NonDecreasingParkingFunction.from_dyck_word([1,1,0,0])
          [1, 1]
          sage: NonDecreasingParkingFunction.from_dyck_word([1,0,1,0])
          [1, 2]
          sage: NonDecreasingParkingFunction.from_dyck_word([1,0,1,1,0,1,0,0,1,0])
          [1, 2, 2, 3, 5]

        TEST::

          sage: ndpf=NonDecreasingParkingFunctions(5);
          sage: list(ndpf) == [NonDecreasingParkingFunction.from_dyck_word(pf.to_dyck_word()) for pf in ndpf]
          True
        """
        res = []
        val = 1
        for i in dw:
            if i == 0:
                val+=1
            else:
                res.append(val)
        return cls(res)
