r"""
FiniteSemigroups
"""
#*****************************************************************************
#  Copyright (C) 2008      Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#                2008-2009 Florent Hivert <florent.hivert at univ-rouen.fr>
#                2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.cachefunc import cached_method
from sage.misc.misc import attrcall
from sage.categories.category import Category
from sage.categories.semigroups import Semigroups
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets

class FiniteSemigroups(Category):
    r"""
    The category of (multiplicative) finite semigroups,
    i.e. enumerated sets with an associative operation ``*``.

    EXAMPLES::

        sage: FiniteSemigroups()
        Category of finite semigroups
        sage: FiniteSemigroups().super_categories()
        [Category of semigroups, Category of finite enumerated sets]
        sage: FiniteSemigroups().all_super_categories()
        [Category of finite semigroups,
         Category of semigroups,
         Category of finite enumerated sets,
         Category of enumerated sets,
         Category of sets,
         Category of objects]
        sage: FiniteSemigroups().example()
        An example of a finite semigroup: the left regular band generated by ('a', 'b', 'c', 'd')

    TESTS::

        sage: C = FiniteSemigroups()
        sage: TestSuite(C).run(verbose = True)
        running ._test_category() . . . pass
        running ._test_not_implemented_methods() . . . pass
        running ._test_pickling() . . . pass

    """
    @cached_method
    def super_categories(self):
        r"""
        Returns a list of the (immediate) super categories of ``self``.

        EXAMPLES::

            sage: FiniteSemigroups().super_categories()
            [Category of semigroups, Category of finite enumerated sets]

        """
        return [Semigroups(), FiniteEnumeratedSets()]

    class ParentMethods:
        r"""
        Collection of methods shared by all finite semigroups.
        """
        def some_elements(self):
            r"""
            Returns an iterable containing some elements of the semigroup.

            .. note:

               Since the semigroup is finite, this method returns self.

            EXAMPLES::

                sage: S = FiniteSemigroups().example(alphabet=('x','y'))
                sage: S.some_elements()
                An example of a finite semigroup: the left regular band generated by ('x', 'y')
                sage: list(S)
                ['y', 'x', 'xy', 'yx']

            """
            return self

        def idempotents(self):
            r"""
            Returns the idempotents of the semigroup

            EXAMPLES::

                sage: S = FiniteSemigroups().example(alphabet=('x','y'))
                sage: S.idempotents()
                ['y', 'x', 'xy', 'yx']

            """
            return [x for x in self if x.is_idempotent()]

        def succ_generators(self, side="twosided"):
            r"""
            Returns the the successor function of the ``side``-sided Cayley
            graph of ``self``.

            This is a function that maps an element of ``self`` to all the
            products of ``x`` by a generator of this semigroup, where the
            product is taken on the left, right or both sides.

            INPUT::

             - ``side``: "left", "right", or "twosided"

            FIXME: find a better name for this method
            FIXME: should we return a set? a family?

            EXAMPLES::

                sage: S = FiniteSemigroups().example()
                sage: S.succ_generators("left" )(S('ca'))
                ('ac', 'bca', 'ca', 'dca')
                sage: S.succ_generators("right")(S('ca'))
                ('ca', 'cab', 'ca', 'cad')
                sage: S.succ_generators("twosided" )(S('ca'))
                ('ac', 'bca', 'ca', 'dca', 'ca', 'cab', 'ca', 'cad')

            """
            left  = (side == "left"  or side == "twosided")
            right = (side == "right" or side == "twosided")
            generators = self.semigroup_generators()
            return lambda x: (tuple(g * x for g in generators) if left  else ()) + (tuple(x * g for g in generators) if right else ())

        def __iter__(self):
            """
            Returns an iterator over the elements of ``self``.

            EXAMPLES::

                sage: S = FiniteSemigroups().example(alphabet=('x','y'))
                sage: it = S.__iter__()
                sage: list(it)
                ['y', 'x', 'xy', 'yx']

            """
            from sage.combinat.backtrack import TransitiveIdeal
            return TransitiveIdeal(self.succ_generators(side = "right"), self.semigroup_generators()).__iter__()

        def ideal(self, gens, side="twosided"):
            r"""
            Returns the ``side``-sided ideal generated by ``gens``.

            INPUT::

             - ``gens``: a list (or iterable) of elements of ``self``
             - ``side``: [default: "twosided"] "left", "right" or "twosided"

            EXAMPLES::

                sage: S = FiniteSemigroups().example()
                sage: list(S.ideal([S('cab')], side="left"))
                ['cab', 'dcab', 'adcb', 'acb', 'bdca', 'bca', 'abdc',
                'cadb', 'acdb', 'bacd', 'abcd', 'cbad', 'abc', 'acbd',
                'dbac', 'dabc', 'cbda', 'bcad', 'cabd', 'dcba',
                'bdac', 'cba', 'badc', 'bac', 'cdab', 'dacb', 'dbca',
                'cdba', 'adbc', 'bcda']
                sage: list(S.ideal([S('cab')], side="right"))
                ['cab', 'cabd']
                sage: list(S.ideal([S('cab')], side="twosided"))
                ['cab', 'dcab', 'acb', 'adcb', 'acbd', 'bdca', 'bca',
                'cabd', 'abdc', 'cadb', 'acdb', 'bacd', 'abcd', 'cbad',
                'abc', 'dbac', 'dabc', 'cbda', 'bcad', 'dcba', 'bdac',
                'cba', 'cdab', 'bac', 'badc', 'dacb', 'dbca', 'cdba',
                'adbc', 'bcda']
                sage: list(S.ideal([S('cab')]))
                ['cab', 'dcab', 'acb', 'adcb', 'acbd', 'bdca', 'bca',
                'cabd', 'abdc', 'cadb', 'acdb', 'bacd', 'abcd', 'cbad',
                'abc', 'dbac', 'dabc', 'cbda', 'bcad', 'dcba', 'bdac',
                'cba', 'cdab', 'bac', 'badc', 'dacb', 'dbca', 'cdba',
                'adbc', 'bcda']

            """
            from sage.combinat.backtrack import TransitiveIdeal
            return TransitiveIdeal(self.succ_generators(side = side), gens)

        def cayley_graph(self, side="twosided", simple=False):
            r"""
            Returns the Cayley graph of the semigroup.

            INPUT::

             - ``side`` -- [default:"twosided"] the side on which the
               generators act
             - ``simple`` -- [default:False] if True, then returns a simple
               (no loops or multiple edges) graph

            OUTPUT::

             - :class:`DiGraph`

            EXAMPLES::

                sage: S = FiniteSemigroups().example(alphabet=('a','b'))
                sage: g = S.cayley_graph(side="right", simple=True)
                sage: g.vertices()
                ['a', 'ab', 'b', 'ba']
                sage: g.edges()
                [('a', 'ab', None), ('b', 'ba', None)]

            ::

                sage: g = S.cayley_graph(side="left", simple=True)
                sage: g.vertices()
                ['a', 'ab', 'b', 'ba']
                sage: g.edges()
                [('a', 'ba', None), ('ab', 'ba', None), ('b', 'ab', None),
                ('ba', 'ab', None)]

            ::

                sage: g = S.cayley_graph(side="twosided", simple=True)
                sage: g.vertices()
                ['a', 'ab', 'b', 'ba']
                sage: g.edges()
                [('a', 'ab', None), ('a', 'ba', None), ('ab', 'ba', None),
                ('b', 'ab', None), ('b', 'ba', None), ('ba', 'ab', None)]

            TODO: add an option to specify a subset of module generators and module operators, and a predicate to stop the iteration

            """
            from sage.graphs.digraph import DiGraph
            if simple:
                result = DiGraph()
            else:
                result = DiGraph(multiedges = True, loops = True)
            result.add_vertices([x for x in self])
            generators = self.semigroup_generators()
            left  = (side == "left"  or side == "twosided")
            right = (side == "right" or side == "twosided")
            def edge(source, target, label):
                if simple:
                    return [source, target]
                else:
                    return [source, target, label]
            for x in self:
                for i in generators.keys():
                    if left:
                        result.add_edge(edge(x, generators[i]*x, (i, "left" )))
                    if right:
                        result.add_edge(edge(x, x*generators[i], (i, "right")))
            return result

        @cached_method
        def j_classes(self):
            r"""
            Returns the $J$-classes of the semigroup.

            Two elements $u$ and $v$ of a monoid are in the same $J$-class
            if $u$ divides $v$ and $v$ divides $u$.

            OUTPUT::

             All the $J$-classes of self, as a list of lists.

            EXAMPLES::

                sage: S = FiniteSemigroups().example(alphabet=('a','b', 'c'))
                sage: S.j_classes()
                [['acb', 'cab', 'bca', 'abc', 'bac', 'cba'], ['ac', 'ca'],
                ['ab', 'ba'], ['bc', 'cb'], ['a'], ['c'], ['b']]

            """
            return self.cayley_graph(side="twosided", simple=True).strongly_connected_components()

        @cached_method
        def j_classes_of_idempotents(self):
            r"""
            Returns all the idempotents of self, grouped by J-class.

            OUTPUT::

             a list of lists.

            EXAMPLES::

                sage: S = FiniteSemigroups().example(alphabet=('a','b', 'c'))
                sage: sorted(map(sorted, S.j_classes_of_idempotents()))
                [['a'], ['ab', 'ba'], ['abc', 'acb', 'bac', 'bca', 'cab', 'cba'], ['ac', 'ca'], ['b'], ['bc', 'cb'], ['c']]
            """
            return filter(lambda l: len(l) > 0,
                          map(lambda cl: filter(attrcall('is_idempotent'), cl),
                              self.j_classes()))

        @cached_method
        def j_transversal_of_idempotents(self):
            r"""
            Returns a list of one idempotent per regular J-class

            EXAMPLES::

                sage: S = FiniteSemigroups().example(alphabet=('a','b', 'c'))
                sage: sorted(S.j_transversal_of_idempotents())
                ['a', 'ab', 'ac', 'acb', 'b', 'bc', 'c']
            """
            def first_idempotent(l):
                for x in l:
                    if x.is_idempotent():
                        return x
                return None
            return filter(lambda x: not x is None,
                          map(first_idempotent, self.j_classes()))

        # TODO: compute eJe, where J is the J-class of e
        # TODO: construct the action of self on it, as a permutation group
