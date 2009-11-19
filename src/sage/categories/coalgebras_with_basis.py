r"""
CoalgebrasWithBasis
"""
#*****************************************************************************
#  Copyright (C) 2008 Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#  Copyright (C) 2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.misc.lazy_attribute import lazy_attribute
from category_types import Category_over_base_ring
from sage.categories.all import Coalgebras, ModulesWithBasis, tensor, Hom
#from sage.categories.homset import Hom

class CoalgebrasWithBasis(Category_over_base_ring):
    """
    The category of coalgebras with a distinguished basis

    EXAMPLES::

        sage: CoalgebrasWithBasis(ZZ)
        Category of coalgebras with basis over Integer Ring
        sage: CoalgebrasWithBasis(ZZ).super_categories()
        [Category of modules with basis over Integer Ring, Category of coalgebras over Integer Ring]

    TESTS::

        sage: TestSuite(CoalgebrasWithBasis(ZZ)).run()
    """

    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: CoalgebrasWithBasis(QQ).super_categories()
            [Category of modules with basis over Rational Field, Category of coalgebras over Rational Field]
        """
        R = self.base_ring()
        return [ModulesWithBasis(R), Coalgebras(R)]

    class ParentMethods:

        @abstract_method(optional = True)
        def coproduct_on_basis(self, i):
            """
            The product of the algebra on the basis (optional)

            INPUT:
             - ``i``: the indices of an element of the basis of self

            Returns the coproduct of the corresponding basis elements
            If implemented, the coproduct of the algebra is defined
            from it by linearity.

            EXAMPLES::

                sage: A = HopfAlgebrasWithBasis(QQ).example(); A
                An example of Hopf algebra with basis: the group algebra of the Dihedral group of order 6 as a permutation group over Rational Field
                sage: (a, b) = A._group.gens()
                sage: A.coproduct_on_basis(a)
                B[(1,2,3)] # B[(1,2,3)]
            """

    class ParentMethods:
        @lazy_attribute
        def coproduct(self):
            """
            If :meth:`.coproduct_basis` is available, construct the
            coproduct morphism from ``self`` to ``self`` `\otimes`
            ``self`` by extending it by linearity

            EXAMPLES::

                sage: A = HopfAlgebrasWithBasis(QQ).example(); A
                An example of Hopf algebra with basis: the group algebra of the Dihedral group of order 6 as a permutation group over Rational Field
                sage: [a,b] = A.algebra_generators()
                sage: a, A.coproduct(a)
                (B[(1,2,3)], B[(1,2,3)] # B[(1,2,3)])
                sage: b, A.coproduct(b)
                (B[(1,3)], B[(1,3)] # B[(1,3)])

            """
            if self.coproduct_on_basis is not NotImplemented:
                # TODO: if self is a coalgebra, then one would want
                # to create a morphism of algebras with basis instead
                # should there be a method self.coproduct_hom_category?
                return Hom(self, tensor([self, self]), ModulesWithBasis(self.base_ring()))(on_basis = self.coproduct_on_basis)

    class ElementMethods:
        pass
