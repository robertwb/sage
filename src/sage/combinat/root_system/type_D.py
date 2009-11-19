"""
Root system data for type D
"""
#*****************************************************************************
#       Copyright (C) 2008-2009 Daniel Bump
#       Copyright (C) 2008-2009 Justin Walker
#       Copyright (C) 2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>,
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************
import ambient_space

class AmbientSpace(ambient_space.AmbientSpace):
    def dimension(self):
        """
        EXAMPLES::

            sage: e = RootSystem(['D',3]).ambient_space()
            sage: e.dimension()
            3
        """
        return self.root_system.cartan_type().rank()

    def root(self, i, j, p1, p2):
        """
        Note that indexing starts at 0.

        EXAMPLES::

            sage: e = RootSystem(['D',3]).ambient_space()
            sage: e.root(0, 1, 1, 1)
            (-1, -1, 0)
            sage: e.root(0, 0, 1, 1)
            (-1, 0, 0)

        """
        if i != j:
            return (-1)**p1 * self.term(i) + (-1)**p2 * self.term(j)
        else:
            return (-1)**p1 * self.term(i)

    def simple_root(self, i):
        """
        EXAMPLES::

            sage: RootSystem(['D',4]).ambient_space().simple_roots()
            Finite family {1: (1, -1, 0, 0), 2: (0, 1, -1, 0), 3: (0, 0, 1, -1), 4: (0, 0, 1, 1)}

        """
        assert(i in self.index_set())
        return self.root(i-1, i, 0, 1) if i < self.n else self.root(self.n-2, self.n-1, 0, 0)

    def positive_roots(self):
        """
        EXAMPLES::

            sage: RootSystem(['D',4]).ambient_space().positive_roots()
            [(1, 1, 0, 0),
             (1, 0, 1, 0),
             (0, 1, 1, 0),
             (1, 0, 0, 1),
             (0, 1, 0, 1),
             (0, 0, 1, 1),
             (1, -1, 0, 0),
             (1, 0, -1, 0),
             (0, 1, -1, 0),
             (1, 0, 0, -1),
             (0, 1, 0, -1),
             (0, 0, 1, -1)]

        """
        res = []
        for p in [0,1]:
            for j in range(self.n):
                res.extend([self.root(i,j,0,p) for i in range(j)])
        return res

    def negative_roots(self):
        """
        EXAMPLES::

            sage: RootSystem(['D',4]).ambient_space().negative_roots()
            [(-1, 1, 0, 0),
             (-1, 0, 1, 0),
             (0, -1, 1, 0),
             (-1, 0, 0, 1),
             (0, -1, 0, 1),
             (0, 0, -1, 1),
             (-1, -1, 0, 0),
             (-1, 0, -1, 0),
             (0, -1, -1, 0),
             (-1, 0, 0, -1),
             (0, -1, 0, -1),
             (0, 0, -1, -1)]

        """
        res = []
        for p in [0,1]:
            for j in range(self.n):
                res.extend([self.root(i,j,1,p) for i in range(j)])
        return res


    def fundamental_weight(self, i):
        """
        EXAMPLES::

            sage: RootSystem(['D',4]).ambient_space().fundamental_weights()
            Finite family {1: (1, 0, 0, 0), 2: (1, 1, 0, 0), 3: (1/2, 1/2, 1/2, -1/2), 4: (1/2, 1/2, 1/2, 1/2)}
        """
        assert(i in self.index_set())
        n = self.dimension()
        if i == n:
            return  self.sum(self.term(j) for j in range(n)) / 2
        elif i == n-1:
            return (self.sum(self.term(j) for j in range(n-1)) - self.term(n-1)) / 2
        else:
            return  self.sum(self.term(j) for j in range(i))

from sage.structure.sage_object import register_unpickle_override
register_unpickle_override('sage.combinat.root_system.type_A', 'ambient_space',  AmbientSpace)

from sage.misc.cachefunc import cached_method
from cartan_type import CartanType_standard_finite, CartanType_simply_laced, CartanType_simple
class CartanType(CartanType_standard_finite, CartanType_simply_laced):
    def __init__(self, n):
        """
        EXAMPLES::

            sage: ct = CartanType(['D',4])
            sage: ct
            ['D', 4]
            sage: ct._repr_(compact = True)
            'D4'

            sage: ct.is_irreducible()
            True
            sage: ct.is_finite()
            True
            sage: ct.is_crystalographic()
            True
            sage: ct.is_simply_laced()
            True
            sage: ct.dual()
            ['D', 4]
            sage: ct.affine()
            ['D', 4, 1]

            sage: ct = CartanType(['D',2])
            sage: ct.is_irreducible()
            False
            sage: ct.dual()
            ['D', 2]
            sage: ct.affine()
            Traceback (most recent call last):
            ...
            ValueError: ['D', 2, 1] is not a valid cartan type


        TESTS:
            sage: ct == loads(dumps(ct))
            True
        """
        assert n >= 2
        CartanType_standard_finite.__init__(self, "D", n)
        if n >= 3:
            self._add_abstract_superclass(CartanType_simple)

    AmbientSpace = AmbientSpace

    def is_atomic(self):
        """
        Implements :meth:`CartanType_abstract.is_atomic`

        `D_2` is atomic, like all `D_n`, despite being non irreducible.

        EXAMPLES::

            sage: CartanType(["D",2]).is_atomic()
            True
            sage: CartanType(["D",2]).is_irreducible()
            False
        """
        return True

    @cached_method
    def dynkin_diagram(self):
        """
        Returns a Dynkin diagram for type D.

        EXAMPLES::

            sage: d = CartanType(['D',5]).dynkin_diagram(); d
                    O 5
                    |
                    |
            O---O---O---O
            1   2   3   4
            D5
            sage: sorted(d.edges())
            [(1, 2, 1), (2, 1, 1), (2, 3, 1), (3, 2, 1), (3, 4, 1), (3, 5, 1), (4, 3, 1), (5, 3, 1)]

            sage: d = CartanType(['D',4]).dynkin_diagram(); d
                O 4
                |
                |
            O---O---O
            1   2   3
            D4
            sage: sorted(d.edges())
            [(1, 2, 1), (2, 1, 1), (2, 3, 1), (2, 4, 1), (3, 2, 1), (4, 2, 1)]

            sage: d = CartanType(['D',3]).dynkin_diagram(); d
            O 3
            |
            |
            O---O
            1   2
            D3
            sage: sorted(d.edges())
            [(1, 2, 1), (1, 3, 1), (2, 1, 1), (3, 1, 1)]


            sage: d = CartanType(['D',2]).dynkin_diagram(); d
            O   O
            1   2
            D2
            sage: sorted(d.edges())
            []
        """
        from dynkin_diagram import DynkinDiagram_class
        g = DynkinDiagram_class(self)
        n = self.n
        if n >= 3:
            for i in range(1, n-1):
                g.add_edge(i, i+1)
            g.add_edge(n-2, n)
        return g

    def ascii_art(self, label = lambda x: x):
        """
        Returns a ascii art representation of the extended Dynkin diagram

        EXAMPLES::

            sage: print CartanType(['D',3]).ascii_art()
            O 3
            |
            |
            O---O
            1   2
            sage: print CartanType(['D',4]).ascii_art()
                O 4
                |
                |
            O---O---O
            1   2   3
            sage: print CartanType(['D',4]).ascii_art(label = lambda x: x+2)
                O 6
                |
                |
            O---O---O
            3   4   5
            sage: print CartanType(['D',6]).ascii_art(label = lambda x: x+2)
                        O 8
                        |
                        |
            O---O---O---O---O
            3   4   5   6   7
        """
        n = self.n
        if n == 2:
            return "O   O\n" + "   ".join("%s"%label(i) for i in range(1,n+1))
        ret  =  (4*(n-3))*" "+"O %s"%label(n) + "\n"
        ret += ((4*(n-3))*" "                 +"|\n")*2
        ret += (n-2)*"O---"+"O\n"
        ret += "   ".join("%s"%label(i) for i in range(1,n))
        return ret

# For unpickling backward compatibility (Sage <= 4.1)
from sage.structure.sage_object import register_unpickle_override
register_unpickle_override('sage.combinat.root_system.type_D', 'ambient_space',  AmbientSpace)
