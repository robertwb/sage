r"""
General Linear Groups

EXAMPLES::

    sage: GL(4,QQ)
    General Linear Group of degree 4 over Rational Field
    sage: GL(1,ZZ)
    General Linear Group of degree 1 over Integer Ring
    sage: GL(100,RR)
    General Linear Group of degree 100 over Real Field with 53 bits of precision
    sage: GL(3,GF(49,'a'))
    General Linear Group of degree 3 over Finite Field in a of size 7^2

AUTHORS:

- David Joyner (2006-01)

- William Stein (2006-01)

- David Joyner (2006-05): added _latex_, __str__, examples

- William Stein (2006-12-09): rewrite
"""

##TODO: Rework this and \code{special_linear} into MatrixGroup class for any
##field, wrapping all of GAP's matrix group commands in chapter 41
##Matrix Groups of the GAP reference manual.


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

from sage.structure.unique_representation import UniqueRepresentation
from sage.rings.all import is_FiniteField, Integer, FiniteField
from matrix_group import MatrixGroup_gap, MatrixGroup_gap_finite_field

def GL(n, R, var='a'):
    """
    Return the general linear group of degree `n` over the ring
    `R`.

    .. note::
        This group is also available via ``groups.matrix.GL()``.

    EXAMPLES::

        sage: G = GL(6,GF(5))
        sage: G.order()
        11064475422000000000000000
        sage: G.base_ring()
        Finite Field of size 5
        sage: G.category()
        Category of finite groups
        sage: TestSuite(G).run()

        sage: G = GL(6, QQ)
        sage: G.category()
        Category of groups
        sage: TestSuite(G).run()

    Here is the Cayley graph of (relatively small) finite General Linear Group::

        sage: g = GL(2,3)
        sage: d = g.cayley_graph(); d
        Digraph on 48 vertices
        sage: d.show(color_by_label=True, vertex_size=0.03, vertex_labels=False)
        sage: d.show3d(color_by_label=True)

    ::

        sage: F = GF(3); MS = MatrixSpace(F,2,2)
        sage: gens = [MS([[0,1],[1,0]]),MS([[1,1],[0,1]])]
        sage: G = MatrixGroup(gens)
        sage: G.order()
        48
        sage: G.cardinality()
        48
        sage: H = GL(2,F)
        sage: H.order()
        48
        sage: H == G           # Do we really want this equality?
        False
        sage: H.as_matrix_group() == G
        True
        sage: H.gens()
        [
        [2 0]
        [0 1],
        [2 1]
        [2 0]
        ]

    TESTS::

        sage: groups.matrix.GL(2, 3)
        General Linear Group of degree 2 over Finite Field of size 3
    """
    if isinstance(R, (int, long, Integer)):
        R = FiniteField(R, var)
    if is_FiniteField(R):
        return GeneralLinearGroup_finite_field(n, R)
    return GeneralLinearGroup_generic(n, R)

class GeneralLinearGroup_generic(UniqueRepresentation, MatrixGroup_gap):
    """
    TESTS::

        sage: G6 = GL(6, QQ)
        sage: G6 == G6
        True
        sage: G6 != G6  # check that #8695 is fixed.
        False
    """
    def _gap_init_(self):
        """
        EXAMPLES::

            sage: G = GL(6,GF(5))
            sage: G._gap_init_()
            'GL(6, GF(5))'
        """
        return "GL(%s, %s)"%(self.degree(), self.base_ring()._gap_init_())

    def _latex_(self):
        """
        EXAMPLES::

            sage: G = GL(6,GF(5))
            sage: latex(G)
            \text{GL}_{6}(\Bold{F}_{5})
        """
        return "\\text{GL}_{%s}(%s)"%(self.degree(), self.base_ring()._latex_())

    def _repr_(self):
        """
        String representation of this linear group.

        EXAMPLES::

            sage: GL(6,GF(5))
            General Linear Group of degree 6 over Finite Field of size 5
        """
        return "General Linear Group of degree %s over %s"%(self.degree(), self.base_ring())

    def __call__(self, x):
        """
        Construct a new element in this group, i.e. try to coerce x into
        self if at all possible.

        EXAMPLES: This indicates that the issue from trac #1834 is
        resolved::

            sage: G = GL(3, ZZ)
            sage: x = [[1,0,1], [0,1,0], [0,0,1]]
            sage: G(x)
            [1 0 1]
            [0 1 0]
            [0 0 1]
        """
        if isinstance(x, self.element_class) and x.parent() is self:
            return x
        try:
            m = self.matrix_space()(x)
        except TypeError:
            raise TypeError, "Cannot coerce %s to a %s-by-%s matrix over %s"%(x,self.degree(),self.degree(),self.base_ring())
        if m.is_invertible():
            return self.element_class(m, self)
        else:
            raise TypeError, "%s is not an invertible matrix"%(x)

    def __contains__(self, x):
        """
        Return True if x is an element of self, False otherwise.

        EXAMPLES::

            sage: G = GL(2, GF(101))
            sage: x = [[0,1], [1,0]]
            sage: x in G
            True

        ::

            sage: G = GL(3, ZZ)
            sage: x = [[1,0,1], [0,2,0], [0,0,1]]
            sage: x in G
            False
        """
        try:
            x = self(x)
        except TypeError:
            return False
        return True

class GeneralLinearGroup_finite_field(GeneralLinearGroup_generic, MatrixGroup_gap_finite_field):

    def random_element(self):
        """
        Return a random element of this group.

        EXAMPLES::

            sage: G = GL(4, GF(3))
            sage: G.random_element()  # random
            [2 1 1 1]
            [1 0 2 1]
            [0 1 1 0]
            [1 0 0 1]
            sage: G.random_element() in G
            True

        ALGORITHM:

        The random matrix is generated by rejection sampling:
        1. Generate a random matrix
        2. Check if is is invertible, if so return it
        3. Go back to step 1

        The expected number of iterations of this procedure is of
        order `1 + 1/q` where `q` is the size of the field. In all
        cases, the expected number of iterations is less than 4.
        """
        M = self.matrix_space().random_element()
        while not M.is_invertible():
            M.randomize()
        return self(M)
