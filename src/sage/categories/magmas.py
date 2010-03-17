r"""
Magmas
"""
#*****************************************************************************
#  Copyright (C) 2010 Nicolas M. Thiery <nthiery at users.sf.net>
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

class Magmas(Category):
    """
    The category of (multiplicative) magmas, i.e. sets with a binary
    operation ``*``.

    EXAMPLES::

        sage: Magmas()
        Category of magmas
        sage: Magmas().super_categories()
        [Category of sets]
        sage: Magmas().all_super_categories()
        [Category of magmas, Category of sets, Category of sets with partial maps, Category of objects]

    TESTS::

        sage: C = Magmas()
        sage: TestSuite(C).run(verbose=True)
        running ._test_category() . . . pass
        running ._test_not_implemented_methods() . . . pass
        running ._test_pickling() . . . pass

    """
    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: Magmas().super_categories()
            [Category of sets]
        """
        return [Sets()]

    class ParentMethods:

        def product(self, x, y):
            """
            The binary multiplication of the magma

            INPUT:

             - ``x``, ``y``: elements of this magma

            OUTPUT:

             - an element of the magma (the product of ``x`` and ``y``)

            EXAMPLES::

                sage: S = Semigroups().example("free")
                sage: x = S('a'); y = S('b')
                sage: S.product(x, y)
                'ab'

            A parent in ``Magmas()`` must either implement
            :meth:`.product` in the parent class or ``_mul_`` in the
            element class. By default, the addition method on elements
            ``x._mul_(y)`` calls ``S.product(x,y)``, and reciprocally.


            As a bonus, ``S.product`` models the binary function from
            ``S`` to ``S``::

                sage: bin = S.product
                sage: bin(x,y)
                'ab'

            Currently, ``S.product`` is just a bound method:

                sage: bin
                <bound method FreeSemigroup_with_category.product of An example of a semigroup: the free semigroup generated by ('a', 'b', 'c', 'd')>

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

        def multiplication_table(self, names='letters', elements=None):
            r"""
            Returns a table describing the multiplication operation.

            .. note:: The order of the elements in the row and column
              headings is equal to the order given by the table's
              :meth:`~sage.matrix.operation_table.OperationTable.list`
              method.  The association can also be retrieved with the
              :meth:`~sage.matrix.operation_table.OperationTable.dict`
              method.

            INPUTS:

            - ``names`` - the type of names used

              * ``letters`` - lowercase ASCII letters are used
                for a base 26 representation of the elements'
                positions in the list given by
                :meth:`~sage.matrix.operation_table.OperationTable.column_keys`,
                padded to a common width with leading 'a's.
              * ``digits`` - base 10 representation of the
                elements' positions in the list given by
                :meth:`~sage.matrix.operation_table.OperationTable.column_keys`,
                padded to a common width with leading zeros.
              * ``elements`` - the string representations
                of the elements themselves.
              * a list - a list of strings, where the length
                of the list equals the number of elements.
            - ``elements`` - default = ``None``.  A list of
              elements of the set.  This may be used to impose an
              alternate ordering on the elements, perhaps
              when this is used in the context of a particular structure.
              The default is to use whatever ordering the
              ``S.list``
              method returns.  Or the ``elements`` can be a subset
              which is closed under the operation. In particular,
              this can be used when the base set is infinite.

            OUTPUT:
            The multiplication table as an object of the class
            :class:`~sage.matrix.operation_table.OperationTable`
            which defines several methods for manipulating and
            displaying the table.  See the documentation there
            for full details to supplement the documentation
            here.

            EXAMPLES:

            The default is to represent elements as lowercase
            ASCII letters.  ::

                sage: G=CyclicPermutationGroup(5)
                sage: G.multiplication_table()
                *  a b c d e
                 +----------
                a| a b c d e
                b| b c d e a
                c| c d e a b
                d| d e a b c
                e| e a b c d

            All that is required is that an algebraic structure
            has a multiplication defined.  A
            :class:`~sage.categories.examples.finite_semigroups.LeftRegularBand`
            is an example of a finite semigroup.  The ``names`` argument allows
            displaying the elements in different ways.  ::

                sage: from sage.categories.examples.finite_semigroups import LeftRegularBand
                sage: L=LeftRegularBand(('a','b'))
                sage: T=L.multiplication_table(names='digits')
                sage: T.column_keys()
                ('a', 'b', 'ab', 'ba')
                sage: T
                *  0 1 2 3
                 +--------
                0| 0 2 2 2
                1| 3 1 3 3
                2| 2 2 2 2
                3| 3 3 3 3

            Specifying the elements in an alternative order can provide
            more insight into how the operation behaves.  ::

                sage: L=LeftRegularBand(('a','b','c'))
                sage: elts = sorted(L.list())
                sage: L.multiplication_table(elements=elts)
                *  a b c d e f g h i j k l m n o
                 +------------------------------
                a| a b c d e b b c c c d d e e e
                b| b b c c c b b c c c c c c c c
                c| c c c c c c c c c c c c c c c
                d| d e e d e e e e e e d d e e e
                e| e e e e e e e e e e e e e e e
                f| g g h h h f g h i j i j j i j
                g| g g h h h g g h h h h h h h h
                h| h h h h h h h h h h h h h h h
                i| j j j j j i j j i j i j j i j
                j| j j j j j j j j j j j j j j j
                k| l m m l m n o o n o k l m n o
                l| l m m l m m m m m m l l m m m
                m| m m m m m m m m m m m m m m m
                n| o o o o o n o o n o n o o n o
                o| o o o o o o o o o o o o o o o

            The ``elements`` argument can be used to provide
            a subset of the elements of the structure.  The subset
            must be closed under the operation.  Elements need only
            be in a form that can be coerced into the set.  The
            ``names`` argument can also be used to request that
            the elements be represented with their usual string
            representation.  ::

                sage: L=LeftRegularBand(('a','b','c'))
                sage: elts=['a', 'c', 'ac', 'ca']
                sage: L.multiplication_table(names='elements', elements=elts)
                   *   'a'  'c' 'ac' 'ca'
                    +--------------------
                 'a'|  'a' 'ac' 'ac' 'ac'
                 'c'| 'ca'  'c' 'ca' 'ca'
                'ac'| 'ac' 'ac' 'ac' 'ac'
                'ca'| 'ca' 'ca' 'ca' 'ca'

            The table returned can be manipulated in various ways.  See
            the documentation for
            :class:`~sage.matrix.operation_table.OperationTable` for more
            comprehensive documentation. ::

                sage: G=AlternatingGroup(3)
                sage: T=G.multiplication_table()
                sage: T.column_keys()
                ((), (1,2,3), (1,3,2))
                sage: sorted(T.translation().items())
                [('a', ()), ('b', (1,2,3)), ('c', (1,3,2))]
                sage: T.change_names(['x', 'y', 'z'])
                sage: sorted(T.translation().items())
                [('x', ()), ('y', (1,2,3)), ('z', (1,3,2))]
                sage: T
                *  x y z
                 +------
                x| x y z
                y| y z x
                z| z x y
            """
            from sage.matrix.operation_table import OperationTable
            import operator
            return OperationTable(self, operation=operator.mul, names=names, elements=elements)

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
