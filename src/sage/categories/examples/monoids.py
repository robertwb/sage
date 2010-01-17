r"""
Examples of monoids
"""
#*****************************************************************************
#  Copyright (C) 2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.cachefunc import cached_method
from sage.structure.parent import Parent
from sage.structure.element import Element
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper import ElementWrapper
from sage.categories.all import Monoids
from sage.sets.family import Family
from semigroups import FreeSemigroup

class FreeMonoid(FreeSemigroup):
    r"""
    An example of a monoid: the free monoid

    This class illustrates a minimal implementation of a monoid.

    EXAMPLES::

        sage: S = Monoids().example(); S
        An example of a monoid: the free monoid generated by ('a', 'b', 'c', 'd')

        sage: S.category()
        Category of monoids

    This is the free semigroup generated by::

        sage: S.semigroup_generators()
        Family ('a', 'b', 'c', 'd')

    with product rule given by $a \times b = a$ for all $a, b$::

        sage: S('dab') * S('acb')
        'dabacb'

    We conclude by running systematic tests on this monoid::

        sage: TestSuite(S).run(verbose = True)
        running ._test_an_element() . . . pass
        running ._test_associativity() . . . pass
        running ._test_category() . . . pass
        running ._test_elements() . . .
          Running the test suite of self.an_element()
          running ._test_category() . . . pass
          running ._test_not_implemented_methods() . . . pass
          running ._test_pickling() . . . pass
          pass
        running ._test_not_implemented_methods() . . . pass
        running ._test_one() . . . pass
        running ._test_pickling() . . . pass
        running ._test_prod() . . . pass
        running ._test_some_elements() . . . pass
    """

    def __init__(self, alphabet=('a','b','c','d')):
        r"""
        The free monoid

        INPUT::

        - ``alphabet`` -- a tuple of strings: the generators of the monoid

        EXAMPLES::

            sage: M = Monoids().example(alphabet=('a','b','c')); M
            An example of a monoid: the free monoid generated by ('a', 'b', 'c')

        TESTS::

            sage: TestSuite(M).run()

        """
        self.alphabet = alphabet
        Parent.__init__(self, category = Monoids())

    def _repr_(self):
        r"""
        TESTS::

            sage: M = Monoids().example(alphabet=('a','b','c'))
            sage: M._repr_()
            "An example of a monoid: the free monoid generated by ('a', 'b', 'c')"

        """
        return "An example of a monoid: the free monoid generated by %s"%(self.alphabet,)

    @cached_method
    def one(self):
        r"""
        Returns the one of the monoid, as per :meth:`Monoids.ParentMethods.one`.

        EXAMPLES::

            sage: M = Monoids().example(); M
            An example of a monoid: the free monoid generated by ('a', 'b', 'c', 'd')
            sage: M.one()
            ''

        """
        return self("")

    class Element (ElementWrapper):
        wrapped_class = str

Example = FreeMonoid
