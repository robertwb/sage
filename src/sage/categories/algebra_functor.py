"""
Algebra Functorial Construction

AUTHORS:

 - Nicolas M. Thiery (2010): initial revision
"""
#*****************************************************************************
#  Copyright (C) 2010 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.categories.category import Category
from sage.categories.covariant_functorial_construction import CovariantFunctorialConstruction, CovariantConstructionCategory
from sage.categories.category_types import Category_over_base_ring
import sage.structure.parent
import sage.structure.element

# This is Category.Algebras
def Algebras(self, base_ring):
    """
    INPUT:

     - ``self`` -- a subcategory of ``Sets()``
     - ``base_ring`` -- a ring

    Returns the category of objects constructed as
    algebras of objects of ``self`` over ``base_ring``.

    EXAMPLES::

        sage: Monoids().Algebras(QQ)
        Category of monoid algebras over Rational Field

        sage: Groups().Algebras(QQ)
        Category of group algebras over Rational Field

        sage: M = Monoids().example(); M
        An example of a monoid: the free monoid generated by ('a', 'b', 'c', 'd')
        sage: A = M.algebra(QQ); A
        Free module generated by An example of a monoid: the free monoid generated by ('a', 'b', 'c', 'd') over Rational Field
        sage: A.category()
        Category of monoid algebras over Rational Field
    """
    from sage.categories.rings import Rings
    assert base_ring in Rings()
    return AlgebrasCategory.category_of(self, base_ring)

Category.Algebras = Algebras

class AlgebraFunctor(CovariantFunctorialConstruction):
    """
    A singleton class for the algebra functor
    """
    _functor_name = "algebra"
    _functor_category = "Algebras"

    def __init__(self, base_ring):
        """
        EXAMPLES::

            sage: from sage.categories.algebra_functor import AlgebraFunctor
            sage: F = AlgebraFunctor(QQ); F
            The algebra functorial construction
            sage: TestSuite(F).run()
        """
        from sage.categories.rings import Rings
        assert base_ring in Rings()
        self._base_ring = base_ring

    def base_ring(self):
        """
        Returns the base ring for this functor

        EXAMPLES::

            sage: from sage.categories.algebra_functor import AlgebraFunctor
            sage: AlgebraFunctor(QQ).base_ring()
            Rational Field
        """
        return self._base_ring

class AlgebrasCategory(CovariantConstructionCategory, Category_over_base_ring):
    """
    Returns the category of ``base_ring``-algebras over ``self``

    A category with algebra functor is a category endowed with an
    algebra functor from itself to the category of modules, mapping a
    set `S` and a field `C` to a `C`-free module with basis indexed by
    `S`, more often than not endowed with an algebra
    structure. Typical examples are the functor from monoids to monoid
    algebras, groups to group algebras, etc.

    See also
    :class:`~sage.categories.covariant_functorial_construction.CovariantFunctorialConstruction`.

    INPUT:

     - ``base_ring`` -- a ring

    EXAMPLES::

        sage: Monoids().Algebras(QQ)
        Category of monoid algebras over Rational Field
    """

    _functor_category = "Algebras"

    def __init__(self, base_category, base_ring):
        """
        EXAMPLES::

            sage: C = Semigroups().Algebras(QQ)
            sage: C
            Category of semigroup algebras over Rational Field
            sage: C.base_category()
            Category of semigroups
            sage: C.super_categories()
            [Category of algebras with basis over Rational Field, Category of set algebras over Rational Field]

        TESTS::

            sage: C._short_name()
            'Algebras'
            sage: latex(C) # todo: improve that
            \mathbf{Algebras}(\mathbf{Semigroups})
        """
        CovariantConstructionCategory.__init__(self, base_category, base_ring)
        Category_over_base_ring.__init__(self, base_ring)

    def _repr_object_names(self):
        """
        EXAMPLES::

            sage: Semigroups().Algebras(QQ) # indirect doctest
            Category of semigroup algebras over Rational Field
        """
        return "%s algebras over %s"%(self.base_category()._repr_object_names()[:-1], self.base_ring())
