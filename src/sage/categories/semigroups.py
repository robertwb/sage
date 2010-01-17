r"""
Semigroups
"""
#*****************************************************************************
#  Copyright (C) 2005      David Kohel <kohel@maths.usyd.edu>
#                          William Stein <wstein@math.ucsd.edu>
#                2008      Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#                2008-2009 Florent Hivert <florent.hivert at univ-rouen.fr>
#                          Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.category import Category
from sage.misc.abstract_method import abstract_method, AbstractMethod
from sage.misc.cachefunc import cached_method
from sage.misc.lazy_attribute import lazy_attribute
from sage.misc.misc_c import prod
from sage.categories.sets_cat import Sets
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.structure.element import Element, generic_power
from sage.structure.sage_object import have_same_parent

class Semigroups(Category):
    """
    The category of (multiplicative) semigroups, i.e. sets with an associative
    operation ``*``.

    EXAMPLES::

        sage: Semigroups()
        Category of semigroups
        sage: Semigroups().super_categories()
        [Category of sets]
        sage: Semigroups().all_super_categories()
        [Category of semigroups, Category of sets, Category of objects]

    TESTS::

        sage: C = Semigroups()
        sage: TestSuite(C).run(verbose=True)
        running ._test_category() . . . pass
        running ._test_not_implemented_methods() . . . pass
        running ._test_pickling() . . . pass

    """
    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: Semigroups().super_categories()
            [Category of sets]
        """
        return [Sets()]

    def example(self, choice="leftzero", **kwds):
        r"""
        An example of a semigroup.

        INPUT::

         - ``choice`` -- str [default: 'leftzero']. Can be either 'leftzero'
           for the left zero semigroup, or 'free' for the free semigroup.
         - ``**kwds`` -- keyword arguments passed onto the constructor for the
           chosen semigroup.

        EXAMPLES::

            sage: Semigroups().example(choice='leftzero')
            An example of a semigroup: the left zero semigroup
            sage: Semigroups().example(choice='free')
            An example of a semigroup: the free semigroup generated by ('a', 'b', 'c', 'd')
            sage: Semigroups().example(choice='free', alphabet=('a','b'))
            An example of a semigroup: the free semigroup generated by ('a', 'b')

        """
        import sage.categories.examples.semigroups as examples
        if choice == "leftzero":
            return examples.LeftZeroSemigroup(**kwds)
        else:
            return examples.FreeSemigroup(**kwds)

    class ParentMethods:

        def _test_associativity(self, **options):
            r"""
            Test associativity for (not necessarily all) elements of this
            semigroup.

            INPUT::

             - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

            EXAMPLES:

            By default, this method tests only the elements returned by
            ``self.some_elements()``::

                sage: L = Semigroups().example(choice='leftzero')
                sage: L._test_associativity()

            However, the elements tested can be customized with the
            ``elements`` keyword argument::

                sage: L._test_associativity(elements = (L(1), L(2), L(3)))

            See the documentation for :class:`TestSuite` for more information.

            """
            tester = self._tester(**options)
            # Better than use all.
            for x in tester.some_elements():
                for y in tester.some_elements():
                    for z in tester.some_elements():
                        tester.assert_((x * y) * z == x * (y * z))

        def product(self, x, y):
            """
            The binary multiplication of the semigroup

            INPUT:

             - ``x``, ``y``: elements of this semigroup

            OUTPUT:

             - an element of the semigroup (the product of ``x`` and ``y``)

            EXAMPLES::

                sage: S = Semigroups().example("free")
                sage: x = S('a'); y = S('b')
                sage: S.product(x, y)
                'ab'

            A parent in ``Semigroups()`` must either implement
            :meth:`.product` in the parent class or ``_mul_`` in the
            element class. By default, the addition method on elements
            ``x._mul_(y)`` calls ``S.product(x,y)``, and reciprocally.


            As a bonus, ``S.product`` models the binary function from
            ``S`` to ``S``::

                sage: bin = S.product
                sage: bin(x,y)
                'ab'

            Currently, ``S.product`` is just a bound method:

                sage: S.rename("S")
                sage: bin
                <bound method FreeSemigroup_with_category.product of S>

            When Sage will support multivariate morphisms, it will be
            possible, and in fact recommended, to enrich ``S.product``
            with extra mathematical structure. This will typically be
            implemented using lazy attributes.

                sage: bin                 # todo: not implemented
                Generic binary morphism:
                From: (S x S)
                To:   S
            """
            return x._mul_(y)

        product_from_element_class_mul = product

        def prod(self, args):
            r"""
            Returns the product of the list of elements `args` inside `self`.

            EXAMPLES:

                sage: S = Semigroups().example("free")
                sage: S.prod([S('a'), S('b'), S('c')])
                'abc'
                sage: S.prod([])
                Traceback (most recent call last):
                ...
                AssertionError: Cannot compute an empty product in a semigroup
            """
            assert len(args) > 0, "Cannot compute an empty product in a semigroup"
            return prod(args[1:], args[0])

        def __init_extra__(self):
            """
                sage: S = Semigroups().example("free")
                sage: S('a') * S('b') # indirect doctest
                'ab'
                sage: S('a').__class__._mul_ == S('a').__class__._mul_parent
                True
            """
            # This should instead register the multiplication to the coercion model
            # But this is not yet implemented in the coercion model
            if (self.product != self.product_from_element_class_mul) and hasattr(self, "element_class") and hasattr(self.element_class, "_mul_parent"):
                self.element_class._mul_ = self.element_class._mul_parent

    class ElementMethods:

        def __mul__(self, right):
            r"""
            Product of two elements

            INPUT::

             - ``self``, ``right`` -- two elements

            This calls the `_mul_` method of ``self``, if it is
            available and the two elements have the same parent.

            Otherwise, the job is delegated to the coercion model.

            Do not override; instead implement a ``_mul_`` method in the
            element class or a ``product`` method in the parent class.

            EXAMPLES::

                sage: S = Semigroups().example("free")
                sage: x = S('a'); y = S('b')
                sage: x * y
                'ab'
            """
            if have_same_parent(self, right) and hasattr(self, "_mul_"):
                return self._mul_(right)
            from sage.structure.element import get_coercion_model
            import operator
            return get_coercion_model().bin_op(self, right, operator.mul)

        __imul__ = __mul__

        @abstract_method(optional = True)
        def _mul_(self, right):
            """
            Product of two elements

            INPUT::

             - ``self``, ``right`` -- two elements with the same parent

            OUTPUT::

             - an element of the same parent

            EXAMPLES::

                sage: S = Semigroups().example("free")
                sage: x = S('a'); y = S('b')
                sage: x._mul_(y)
                'ab'
            """

        def _mul_parent(self, other):
            r"""
            Returns the product of the two elements, calculated using
            the ``product`` method of the parent.

            This is the default implementation of _mul_ if
            ``product`` is implemented in the parent.

            INPUT::

             - ``other`` -- an element of the parent of ``self``

            OUTPUT::

             - an element of the parent of ``self``

            EXAMPLES::

                sage: S = Semigroups().example("free")
                sage: x = S('a'); y = S('b')
                sage: x._mul_parent(y)
                'ab'

            """
            return self.parent().product(self, other)

        def _pow_(self, n):
            """
            Returns self to the $n^{th}$ power.

            INPUT::

             - ``n`` -- a positive integer

            EXAMPLES::

                sage: S = Semigroups().example("leftzero")
                sage: x = S("x")
                sage: x^1, x^2, x^3, x^4, x^5
                ('x', 'x', 'x', 'x', 'x')
                sage: x^0
                Traceback (most recent call last):
                ...
                AssertionError

            TESTS::

                sage: x._pow_(17)
                'x'

            """
            assert n > 0
            return generic_power(self, n)

        __pow__ = _pow_

        def is_idempotent(self):
            r"""
            Test whether ``self`` is idempotent.

            EXAMPLES::

                sage: S = Semigroups().example("free"); S
                An example of a semigroup: the free semigroup generated by ('a', 'b', 'c', 'd')
                sage: a = S('a')
                sage: a^2
                'aa'
                sage: a.is_idempotent()
                False

            ::

                sage: L = Semigroups().example("leftzero"); L
                An example of a semigroup: the left zero semigroup
                sage: x = L('x')
                sage: x^2
                'x'
                sage: x.is_idempotent()
                True

            """
            return self * self == self


    #######################################
    class SubQuotients(Category): # (SubQuotientCategory):
        r"""
        The category of sub/quotient semi-groups.

        Let `G` and `S` be two semi-groups and `l: S \mapsto G` and
        `r: G \mapsto S` be two maps such that:

         - `r \circ l` is the identity of `G`.

         - for any two `a,b\in S` the identity `a \times_S b = r(l(a) \times_G l(b))` holds.

        The category SubQuotient implements the product `\times_S` from `l` and `r`
        and the product of `G`.

        `S` is supposed to belongs the category
        ``Semigroups().SubQuotients()`` and to specify `G` under the name
        ``S.ambient()`` and to implement `x\to l(x)` and `y \to r(y)`
        under the names ``S.lift(x)`` and ``S.retract(y)``.
        """

        @cached_method
        def super_categories(self):
            """
            EXAMPLES::

                sage: Semigroups().SubQuotients().super_categories()
                [Category of semigroups]
            """
            return [Semigroups()]

        def example(self):
            """
            Returns an example of sub quotient of a semigroup

            EXAMPLES::

                sage: Semigroups().SubQuotients().example()
                An example of a subquotient semigroup: a subquotient of the left zero semigroup
            """
            from sage.categories.examples.semigroups import SubQuotientOfLeftZeroSemigroup
            return SubQuotientOfLeftZeroSemigroup()

        class ParentMethods:
            # TODO: move _repr_ ambient, lift, retract to Sets.SubQuotients once
            # the subquotient functorial construction will be implemented

            def _repr_(self):
                """
                EXAMPLES::

                    sage: S = sage.categories.examples.semigroups.IncompleteSubQuotientSemigroup()
                    sage: S._repr_()
                    'A subquotient of An example of a semigroup: the left zero semigroup'
                """
                return "A subquotient of %s"%(self.ambient())

            @abstract_method
            def ambient(self):
                """
                Returns the ambient space for `self`.

                EXAMPLES::

                    sage: Semigroups().SubQuotients().example().ambient()
                    An example of a semigroup: the left zero semigroup

                See also :meth:`.lift` and :meth:`.retract`
                """

            @abstract_method
            def lift(self, x):
                """
                INPUT:
                 - ``x`` -- an element of ``self``

                Lifts `x` to the ambient space for ``self``.

                EXAMPLES::

                    sage: S = Semigroups().SubQuotients().example()
                    sage: s = S.an_element()
                    sage: s, s.parent()
                    (42, An example of a subquotient semigroup: a subquotient of the left zero semigroup)
                    sage: S.lift(s), S.lift(s).parent()
                    (42, An example of a semigroup: the left zero semigroup)
                    sage: s.lift(), s.lift().parent()
                    (42, An example of a semigroup: the left zero semigroup)

                See also :meth:`.ambient`, :meth:`.retract`, and :meth:`Semigroups.Subquotients.ElementMethods.lift`
                """

            @abstract_method
            def retract(self, x):
                """
                INPUT:
                 - ``x`` -- an element of the ambient space for ``self``

                Retracts `x` to `self`.

                See also :meth:`.ambient` and :meth:`.lift`.

                EXAMPLES::

                    sage: S = Semigroups().SubQuotients().example()
                    sage: s = S.ambient().an_element()
                    sage: s, s.parent()
                    (42, An example of a semigroup: the left zero semigroup)
                    sage: S.retract(s), S.retract(s).parent()
                    (42, An example of a subquotient semigroup: a subquotient of the left zero semigroup)
                """

            def product(self, x, y):
                """
                Returns the product of two elements of self.

                EXAMPLES::

                    sage: S = Semigroups().SubQuotients().example()
                    sage: S.product(S(19), S(3))
                    19
                """
                assert(x in self)
                assert(y in self)
                return self.retract(self.lift(x) * self.lift(y))

        # Should lift and retract be declared as conversions to the coercion mechanism ?

        class ElementMethods:

            def lift(self):
                """
                Lifts ``self`` to the ambient space for its parent

                EXAMPLES::

                    sage: S = Semigroups().SubQuotients().example()
                    sage: s = S.an_element()
                    sage: s, s.parent()
                    (42, An example of a subquotient semigroup: a subquotient of the left zero semigroup)
                    sage: S.lift(s), S.lift(s).parent()
                    (42, An example of a semigroup: the left zero semigroup)
                    sage: s.lift(), s.lift().parent()
                    (42, An example of a semigroup: the left zero semigroup)

                See also :meth:`Semigroups.Subquotients.ParentMethods.lift`
                """
                return self.parent().lift(self)
