r"""
Commutative additive semigroups
"""
#*****************************************************************************
#  Copyright (C) 2008 Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.categories.category import Category
from sage.categories.category_singleton import Category_singleton
from sage.categories.additive_magmas import AdditiveMagmas
from sage.structure.sage_object import have_same_parent

class CommutativeAdditiveSemigroups(Category_singleton):
    """
    The category of additive abelian semigroups, i.e. sets with an
    associative and abelian operation +.

    EXAMPLES::

        sage: CommutativeAdditiveSemigroups()
        Category of commutative additive semigroups
        sage: CommutativeAdditiveSemigroups().super_categories()
        [Category of additive magmas]
        sage: CommutativeAdditiveSemigroups().all_super_categories()
        [Category of commutative additive semigroups, Category of additive magmas, Category of sets, Category of sets with partial maps, Category of objects]

    TESTS::

        sage: C = CommutativeAdditiveSemigroups()
        sage: TestSuite(C).run()

    """

    def super_categories(self):
        """
        EXAMPLES::

            sage: CommutativeAdditiveSemigroups().super_categories()
            [Category of additive magmas]
        """
        return [AdditiveMagmas()]

    class ParentMethods:
        def _test_additive_associativity(self, **options):
            r"""
            Test associativity for (not necessarily all) elements of this
            additive semigroup.

            INPUT:

             - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

            EXAMPLES:

            By default, this method tests only the elements returned by
            ``self.some_elements()``::

                sage: S = CommutativeAdditiveSemigroups().example()
                sage: S._test_additive_associativity()

            However, the elements tested can be customized with the
            ``elements`` keyword argument::

                sage: (a,b,c,d) = S.additive_semigroup_generators()
                sage: S._test_additive_associativity(elements = (a, b+c, d))

            See the documentation for :class:`TestSuite` for more information.
            """
            tester = self._tester(**options)
            # Better than use all.
            for x in tester.some_elements():
                for y in tester.some_elements():
                    for z in tester.some_elements():
                        tester.assert_((x + y) + z == x + (y + z))

        def summation(self, x, y):
            """
            The binary addition operator of the semigroup

            INPUT:

             - ``x``, ``y`` -- elements of this additive semigroup

            Returns the sum of ``x`` and ``y``

            EXAMPLES::

                sage: S = CommutativeAdditiveSemigroups().example()
                sage: (a,b,c,d) = S.additive_semigroup_generators()
                sage: S.summation(a, b)
                a + b

            A parent in ``CommutativeAdditiveSemigroups()`` must
            either implement :meth:`.summation` in the parent class or
            ``_add_`` in the element class. By default, the addition
            method on elements ``x._add_(y)`` calls
            ``S.summation(x,y)``, and reciprocally.


            As a bonus effect, ``S.summation`` by itself models the
            binary function from ``S`` to ``S``::

                sage: bin = S.summation
                sage: bin(a,b)
                a + b

            Here, ``S.summation`` is just a bound method. Whenever
            possible, it is recommended to enrich ``S.summation`` with
            extra mathematical structure. Lazy attributes can come
            handy for this.

            Todo: add an example.
            """
            return x._add_(y)

        summation_from_element_class_add = summation

        def __init_extra__(self):
            """
            TESTS::

                sage: S = CommutativeAdditiveSemigroups().example()
                sage: (a,b,c,d) = S.additive_semigroup_generators()
                sage: a + b # indirect doctest
                a + b
                sage: a.__class__._add_ == a.__class__._add_parent
                True
            """
            # This should instead register the summation to the coercion model
            # But this is not yet implemented in the coercion model
            if (self.summation != self.summation_from_element_class_add) and hasattr(self, "element_class") and hasattr(self.element_class, "_add_parent"):
                self.element_class._add_ = self.element_class._add_parent


    class ElementMethods:

        # This could eventually be moved to SageObject
        def __add__(self, right):
            r"""
            Sum of two elements

            This calls the `_add_` method of ``self``, if it is
            available and the two elements have the same parent.

            Otherwise, the job is delegated to the coercion model.

            Do not override; instead implement an ``_add_`` method in the
            element class or a ``summation`` method in the parent class.

            EXAMPLES::

                sage: F = CommutativeAdditiveSemigroups().example()
                sage: (a,b,c,d) = F.additive_semigroup_generators()
                sage: a + b
                a + b
            """
            if have_same_parent(self, right) and hasattr(self, "_add_"):
                return self._add_(right)
            from sage.structure.element import get_coercion_model
            import operator
            return get_coercion_model().bin_op(self, right, operator.add)

        def __radd__(self, left):
            r"""
            Handles the sum of two elements, when the left hand side
            needs to be coerced first.

            EXAMPLES::

                sage: F = CommutativeAdditiveSemigroups().example()
                sage: (a,b,c,d) = F.additive_semigroup_generators()
                sage: a.__radd__(b)
                a + b
            """
            if have_same_parent(left, self) and hasattr(left, "_add_"):
                return left._add_(self)
            from sage.structure.element import get_coercion_model
            import operator
            return get_coercion_model().bin_op(left, self, operator.add)

        @abstract_method(optional = True)
        def _add_(self, right):
            """
            Sum of two elements

            INPUT:

             - ``self``, ``right`` -- two elements with the same parent

            OUTPUT:

             - an element of the same parent

            EXAMPLES::

                sage: F = CommutativeAdditiveSemigroups().example()
                sage: (a,b,c,d) = F.additive_semigroup_generators()
                sage: a._add_(b)
                a + b
            """

        def _add_parent(self, other):
            r"""
            Returns the sum of the two elements, calculated using
            the ``summation`` method of the parent.

            This is the default implementation of _add_ if
            ``summation`` is implemented in the parent.

            INPUT:

             - ``other`` -- an element of the parent of ``self``

            OUTPUT:

            an element of the parent of ``self``

            EXAMPLES::

                sage: S = CommutativeAdditiveSemigroups().example()
                sage: (a,b,c,d) = S.additive_semigroup_generators()
                sage: a._add_parent(b)
                a + b
            """
            return self.parent().summation(self, other)
