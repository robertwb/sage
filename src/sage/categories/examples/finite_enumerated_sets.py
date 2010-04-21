r"""
Examples of finite enumerated sets
"""
#*****************************************************************************
#  Copyright (C) 2009 Florent Hivert <Florent.Hivert@univ-rouen.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper import ElementWrapper
from sage.categories.enumerated_sets import EnumeratedSets
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from sage.rings.integer import Integer

class Example(UniqueRepresentation, Parent):
    r"""
    An example of a finite enumerated set: `\{1,2,3\}`

    This class provides a minimal implementation of a finite enumerated set.

    See :class:`FiniteEnumeratedSet` for a full featured implementation.

    EXAMPLES::

        sage: C = FiniteEnumeratedSets().example()
        sage: C.cardinality()
        3
        sage: C.list()
        [1, 2, 3]
        sage: C.an_element()
        1

    This checks that the different methods of the enumerated set `C`
    return consistent results::

        sage: TestSuite(C).run(verbose = True)
        running ._test_an_element() . . .
          The set doesn't seems to implement __call__; skipping test of construction idempotency
         pass
        running ._test_category() . . . pass
        running ._test_elements() . . .
          Running the test suite of self.an_element()
          running ._test_category() . . . pass
          running ._test_eq() . . . pass
          running ._test_not_implemented_methods() . . . pass
          running ._test_pickling() . . . pass
          pass
        running ._test_elements_eq() . . . pass
        running ._test_enumerated_set_contains() . . . pass
        running ._test_enumerated_set_iter_cardinality() . . . pass
        running ._test_enumerated_set_iter_list() . . . pass
        running ._test_eq() . . . pass
        running ._test_not_implemented_methods() . . . pass
        running ._test_pickling() . . . pass
        running ._test_some_elements() . . . pass
    """

    def __init__(self):
        """
        TESTS::

            sage: C = FiniteEnumeratedSets().example()
            sage: C
            An example of a finite enumerated set: {1,2,3}
            sage: C.category()
            Category of finite enumerated sets
            sage: TestSuite(C).run()
        """
        self._set = map(Integer, [1,2,3])
        Parent.__init__(self, category = FiniteEnumeratedSets())

    def _repr_(self):
        """
        TESTS::

            sage: FiniteEnumeratedSets().example() # indirect doctest
            An example of a finite enumerated set: {1,2,3}
        """
        return "An example of a finite enumerated set: {1,2,3}"

    def __contains__(self, o):
        """
        EXAMPLES::

            sage: C = FiniteEnumeratedSets().example()
            sage: 1 in C
            True
            sage: 0 in C
            False
        """
        return o in self._set

    def __iter__(self):
        """
        EXAMPLES::

            sage: list(FiniteEnumeratedSets().example()) # indirect doctest
            [1, 2, 3]

        """
        return iter(self._set)

    # temporarily needed because parent overloads it.
    an_element = EnumeratedSets.ParentMethods._an_element_
