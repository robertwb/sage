"""
Base class for groups
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
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

doc="""
Base class for all groups
"""

import random

from   sage.rings.infinity import infinity
import sage.rings.integer_ring

cdef class Group(sage.structure.parent_gens.ParentWithGens):
    """
    Generic group class
    """
    def __init__(self, category = None):
        """

        TESTS::
            sage: from sage.groups.group import Group
            sage: G = Group()
            sage: G.category()
            Category of groups
            sage: G = Group(category = Groups()) # todo: do the same test with some subcategory of Groups when there will exist one
            sage: G.category()
            Category of groups
            sage: G = Group(category = CommutativeAdditiveGroups())
            Traceback (most recent call last):
            ...
            AssertionError: Category of commutative additive groups is not a subcategory of Category of groups
        """
        from sage.categories.basic import Groups
        if category is None:
            category = Groups()
        else:
            assert category.is_subcategory(Groups()), "%s is not a subcategory of %s"%(category, Groups())

        sage.structure.parent_gens.ParentWithGens.__init__(self,
                sage.rings.integer_ring.ZZ, category = category)

    def __call__(self, x):
        """
        Coerce x into this group.
        """
        raise NotImplementedError

    def __contains__(self, x):
        r"""
        True if coercion of `x` into self is defined.
        """
        try:
            self(x)
        except TypeError:
            return False
        return True

#    def category(self):
#        """
#        The category of all groups
#        """
#        import sage.categories.all
#        return sage.categories.all.Groups()

    def is_atomic_repr(self):
        """
        True if the elements of this group have atomic string
        representations. For example, integers are atomic but polynomials
        are not.
        """
        return False

    def is_abelian(self):
        """
        Return True if this group is abelian.
        """
        raise NotImplementedError

    def order(self):
        """
        Returns the number of elements of this group, which is either a
        positive integer or infinity.
        """
        raise NotImplementedError

    def is_finite(self):
        """
        Returns True if this group is finite.
        """
        return self.order() != infinity

    def is_multiplicative(self):
        """
        Returns True if the group operation is given by \* (rather than
        +).

        Override for additive groups.
        """
        return True

    def __hash__(self):
        return hash(self.__repr__())

    def random_element(self, bound=None):
        """
        Return a random element of this group.
        """
        raise NotImplementedError

    def quotient(self, H):
        """
        Return the quotient of this group by the normal subgroup
        `H`.
        """
        raise NotImplementedError

cdef class AbelianGroup(Group):
    """
    Generic abelian group.
    """
    def is_abelian(self):
        """
        Return True.
        """
        return True

cdef class FiniteGroup(Group):
    """
    Generic finite group.
    """
    def is_finite(self):
        """
        Return True.
        """
        return True

    def cayley_graph(self, connecting_set=None):
        """
        Returns the cayley graph for this finite group, as a Sage DiGraph
        object. To plot the graph with with different colors

        INPUT::

            `connecting_set` - (optional) list of elements to use for edges,
                               default is the stored generators

        EXAMPLES::

            sage: D4 = DihedralGroup(4); D4
            Dihedral group of order 8 as a permutation group
            sage: G = D4.cayley_graph()
            sage: show(G, color_by_label=True, edge_labels=True)
            sage: A5 = AlternatingGroup(5); A5
            Alternating group of order 5!/2 as a permutation group
            sage: G = A5.cayley_graph()
            sage: G.show3d(color_by_label=True, edge_size=0.01, edge_size2=0.02, vertex_size=0.03)
            sage: G.show3d(vertex_size=0.03, edge_size=0.01, edge_size2=0.02, vertex_colors={(1,1,1):G.vertices()}, bgcolor=(0,0,0), color_by_label=True, xres=700, yres=700, iterations=200) # long time (less than a minute)
            sage: G.num_edges()
            120
            sage: G = A5.cayley_graph(connecting_set=A5.gens()[0])
            sage: G.num_edges()
            60
            sage: g=PermutationGroup([(i+1,j+1) for i in range(5) for j in range(5) if j!=i])
            sage: g.cayley_graph(connecting_set=[(1,2),(2,3)])
            Digraph on 120 vertices

        ::

            sage: s1 = SymmetricGroup(1); s = s1.cayley_graph(); s.vertices()
            [()]

        AUTHORS:

        - Bobby Moretti (2007-08-10)

        - Robert Miller (2008-05-01): editing
        """
        if connecting_set is None:
            connecting_set = self.gens()
        else:
            try:
                for g in connecting_set:
                    assert g in self
            except AssertionError:
                raise RuntimeError("Each element of the connecting set must be in the group!")
            connecting_set = [self(g) for g in connecting_set]
        from sage.graphs.all import DiGraph
        arrows = {}
        for x in self:
            arrows[x] = {}
            for g in connecting_set:
                xg = x*g # cache the multiplication
                if not xg == x:
                    arrows[x][xg] = g

        return DiGraph(arrows, implementation='networkx')

cdef class AlgebraicGroup(Group):
    """
    Generic algebraic group.
    """
