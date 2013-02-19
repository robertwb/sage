r"""
Spin Crystals

These are the crystals associated with the three spin
representations: the spin representations of odd orthogonal groups
(or rather their double covers); and the + and - spin
representations of the even orthogonal groups.

We follow Kashiwara and Nakashima (Journal of Algebra 165, 1994) in
representing the elements of the spin Crystal by sequences of signs
+/-. Two other representations are available as attributes
internal_repn and signature of the crystal element.

- A numerical internal representation, an integer N such that if N-1
  is written in binary and the 1's are replaced by ``-``, the 0's by
  ``+``

- The signature, which is a list in which ``+`` is replaced by +1 and
  ``-`` by -1.
"""

#*****************************************************************************
#       Copyright (C) 2007 Anne Schilling <anne at math.ucdavis.edu>
#                          Nicolas Thiery <nthiery at users.sf.net>
#                          Daniel Bump    <bump at match.stanford.edu>
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
#****************************************************************************

from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.categories.classical_crystals import ClassicalCrystals
from sage.combinat.crystals.letters import Letter
from sage.combinat.root_system.cartan_type import CartanType
from sage.combinat.tableau import Tableau


#########################
# Type B spin
#########################

def CrystalOfSpins(ct):
    r"""
    Return the spin crystal of the given type B.

    This is a combinatorial model for the crystal with highest weight
    `Lambda_n` (the n-th fundamental weight). It has
    `2^n` elements, here called Spins. See also
    CrystalOfLetters, CrystalOfSpinsPlus and CrystalOfSpinsMinus.

    INPUT:


    -  ``['B',n]`` - A CartanType of type B.


    EXAMPLES::

        sage: C = CrystalOfSpins(['B',3])
        sage: C.list()
        [+++, ++-, +-+, -++, +--, -+-, --+, ---]
        sage: C.cartan_type()
        ['B', 3]

    ::

        sage: [x.signature() for x in C]
        ['+++', '++-', '+-+', '-++', '+--', '-+-', '--+', '---']

    TESTS::

        sage: TensorProductOfCrystals(C,C,generators=[[C.list()[0],C.list()[0]]]).cardinality()
        35
    """
    ct = CartanType(ct)
    if ct[0] == 'B':
        return GenericCrystalOfSpins(ct, Spin_crystal_type_B_element, "spins")
    else:
        raise NotImplementedError

#########################
# Type D spins
#########################

def CrystalOfSpinsPlus(ct):
    r"""
    Return the plus spin crystal of the given type D.

    This is the crystal with highest weight `Lambda_n` (the
    n-th fundamental weight).

    INPUT:


    -  ``['D',n]`` - A CartanType of type D.


    EXAMPLES::

        sage: D = CrystalOfSpinsPlus(['D',4])
        sage: D.list()
        [++++, ++--, +-+-, -++-, +--+, -+-+, --++, ----]

    ::

        sage: [x.signature() for x in D]
        ['++++', '++--', '+-+-', '-++-', '+--+', '-+-+', '--++', '----']

    TESTS::

        sage: TestSuite(D).run()
    """
    ct = CartanType(ct)
    if ct[0] == 'D':
        return GenericCrystalOfSpins(ct, Spin_crystal_type_D_element, "plus")
    else:
        raise NotImplementedError

def CrystalOfSpinsMinus(ct):
    r"""
    Return the minus spin crystal of the given type D.

    This is the crystal with highest weight `Lambda_{n-1}`
    (the (n-1)-st fundamental weight).

    INPUT:


    -  ``['D',n]`` - A CartanType of type D.


    EXAMPLES::

        sage: E = CrystalOfSpinsMinus(['D',4])
        sage: E.list()
        [+++-, ++-+, +-++, -+++, +---, -+--, --+-, ---+]
        sage: [x.signature() for x in E]
        ['+++-', '++-+', '+-++', '-+++', '+---', '-+--', '--+-', '---+']

    TESTS::

        sage: len(TensorProductOfCrystals(E,E,generators=[[E[0],E[0]]]).list())
        35
        sage: D = CrystalOfSpinsPlus(['D',4])
        sage: len(TensorProductOfCrystals(D,E,generators=[[D.list()[0],E.list()[0]]]).list())
        56
    """
    ct = CartanType(ct)
    if ct[0] == 'D':
        return GenericCrystalOfSpins(ct, Spin_crystal_type_D_element, "minus")
    else:
        raise NotImplementedError

class GenericCrystalOfSpins(UniqueRepresentation, Parent):
    def __init__(self, ct, element_class, case):
        """
        EXAMPLES::

            sage: E = CrystalOfSpinsMinus(['D',4])
            sage: TestSuite(E).run()
        """
        self._cartan_type = CartanType(ct)
        if case == "spins":
            self.rename("The crystal of spins for type %s"%ct)
        elif case == "plus":
            self.rename("The plus crystal of spins for type %s"%ct)
        else:
            self.rename("The minus crystal of spins for type %s"%ct)

        self.Element = element_class
#        super(GenericCrystalOfSpins, self).__init__(category = FiniteEnumeratedSets())
        Parent.__init__(self, category = ClassicalCrystals())

        if case == "minus":
            generator = [1]*(ct[1]-1)
            generator.append(-1)
        else:
            generator = [1]*ct[1]
        self.module_generators = [self(generator)]
        self._list = list(self)
#        self._digraph = ClassicalCrystal.digraph(self)
        self._digraph = super(GenericCrystalOfSpins, self).digraph()
        self._digraph_closure = self.digraph().transitive_closure()

    def __call__(self, value):
        """
        EXAMPLES::

            sage: C = CrystalOfSpins(['B',3])
            sage: C([1,1,1])
            +++
        """
        if value.__class__ == self.element_class and value.parent() == self:
            return value
        else:
            return self.element_class(self, value)

    def list(self):
        """
        Returns a list of the elements of self.

        EXAMPLES::

            sage: CrystalOfSpins(['B',3]).list()
            [+++, ++-, +-+, -++, +--, -+-, --+, ---]
        """
        return self._list

    def digraph(self):
        """
        Returns the directed graph associated to self.

        EXAMPLES::

            sage: CrystalOfSpins(['B',3]).digraph()
            Digraph on 8 vertices
        """
        return self._digraph

    def lt_elements(self, x,y):
        r"""
        Returns True if and only if there is a path from x to y in the
        crystal graph.

        Because the crystal graph is classical, it is a directed acyclic
        graph which can be interpreted as a poset. This function implements
        the comparison function of this poset.

        EXAMPLES::

            sage: C = CrystalOfSpins(['B',3])
            sage: x = C([1,1,1])
            sage: y = C([-1,-1,-1])
            sage: C.lt_elements(x,y)
            True
            sage: C.lt_elements(y,x)
            False
            sage: C.lt_elements(x,x)
            False
        """
        assert x.parent() == self and y.parent() == self
        if self._digraph_closure.has_edge(x,y):
            return True
        return False

class Spin(Letter):
    """
    EXAMPLES::

        sage: C = CrystalOfSpins(['B',3])
        sage: c = C([1,1,1])
        sage: TestSuite(c).run()

        sage: C([1,1,1]).parent()
        The crystal of spins for type ['B', 3]

        sage: c = C([1,1,1])
        sage: c._repr_()
        '+++'

        sage: D = CrystalOfSpins(['B',4])
        sage: a = C([1,1,1])
        sage: b = C([-1,-1,-1])
        sage: c = D([1,1,1,1])
        sage: a == a
        True
        sage: a == b
        False
        sage: b == c
        False
    """

    def __hash__(self):
        """
        EXAMPLES::

            sage: C = CrystalOfSpins(['B',3])
            sage: c = C([1,1,1])
            sage: type(hash(c))
            <type 'int'>
        """

        return hash(tuple(self.value))

    def signature(self):
        """
        Returns the signature of self.

        EXAMPLES::

            sage: C = CrystalOfSpins(['B',3])
            sage: C([1,1,1]).signature()
            '+++'
            sage: C([1,1,-1]).signature()
            '++-'
        """
        sword = ""
        for x in range(self.parent().cartan_type().n):
            sword += "+" if self.value[x] == 1 else "-"
        return sword

    def _repr_(self):
        """
        Represents the spin elements in terms of its signature.

        EXAMPLES::

            sage: C = CrystalOfSpins(['B',3])
            sage: b = C([1,1,-1])
            sage: b
            ++-
            sage: b._repr_()
            '++-'
        """
        return self.signature()

    def _latex_(self):
        """
        Gives the latex output of a spin column.

        EXAMPLES::

            sage: C = CrystalOfSpins(['B',3])
            sage: b = C([1,1,-1])
            sage: print b._latex_()
            {\def\lr#1{\multicolumn{1}{|@{\hspace{.6ex}}c@{\hspace{.6ex}}|}{\raisebox{-.3ex}{$#1$}}}
            \raisebox{-.6ex}{$\begin{array}[b]{*{1}c}\cline{1-1}
            \lr{-}\\\cline{1-1}
            \lr{+}\\\cline{1-1}
            \lr{+}\\\cline{1-1}
            \end{array}$}
            }
        """
        return Tableau([[i] for i in reversed(self.signature())])._latex_()


class Spin_crystal_type_B_element(Spin):
    r"""
    Type B spin representation crystal element
    """
    def e(self, i):
        r"""
        Returns the action of `e_i` on self.

        EXAMPLES::

            sage: C = CrystalOfSpins(['B',3])
            sage: [[C[m].e(i) for i in range(1,4)] for m in range(8)]
            [[None, None, None], [None, None, +++], [None, ++-, None], [+-+, None, None],
            [None, None, +-+], [+--, None, -++], [None, -+-, None], [None, None, --+]]
        """
        assert i in self.index_set()
        rank = self.parent().cartan_type().n
        if i < rank:
            if self.value[i-1] == -1 and self.value[i] == 1:
                ret = [self.value[x] for x in range(rank)]
                ret[i-1] = 1
                ret[i] = -1
                return self.parent()(ret)
        elif i == rank:
            if self.value[i-1] == -1:
                ret = [self.value[x] for x in range(rank)]
                ret[i-1] = 1
                return self.parent()(ret)
        else:
            return None

    def f(self, i):
        r"""
        Returns the action of `f_i` on self.

        EXAMPLES::

            sage: C = CrystalOfSpins(['B',3])
            sage: [[C[m].f(i) for i in range(1,4)] for m in range(8)]
            [[None, None, ++-], [None, +-+, None], [-++, None, +--], [None, None, -+-],
            [-+-, None, None], [None, --+, None], [None, None, ---], [None, None, None]]
        """
        assert i in self.index_set()
        rank = self.parent().cartan_type().n
        if i < rank:
            if self.value[i-1] == 1 and self.value[i] == -1:
                ret = [self.value[x] for x in range(rank)]
                ret[i-1] = -1
                ret[i] = 1
                return self.parent()(ret)
        elif i == rank:
            if self.value[i-1] == 1:
                ret = [self.value[x] for x in range(rank)]
                ret[i-1] = -1
                return self.parent()(ret)
        else:
            return None

class Spin_crystal_type_D_element(Spin):
    r"""
    Type D spin representation crystal element
    """
    def e(self, i):
        r"""
        Returns the action of `e_i` on self.

        EXAMPLES::

            sage: D = CrystalOfSpinsPlus(['D',4])
            sage: [[D.list()[m].e(i) for i in range(1,4)] for m in range(8)]
            [[None, None, None], [None, None, None], [None, ++--, None], [+-+-, None, None],
            [None, None, +-+-], [+--+, None, -++-], [None, -+-+, None], [None, None, None]]

        ::

            sage: E = CrystalOfSpinsMinus(['D',4])
            sage: [[E[m].e(i) for i in range(1,4)] for m in range(8)]
            [[None, None, None], [None, None, +++-], [None, ++-+, None], [+-++, None, None],
            [None, None, None], [+---, None, None], [None, -+--, None], [None, None, --+-]]
        """
        assert i in self.index_set()
        rank = self.parent().cartan_type().n
        if i < rank:
            if self.value[i-1] == -1 and self.value[i] == 1:
                ret = [self.value[x] for x in range(rank)]
                ret[i-1] = 1
                ret[i] = -1
                return self.parent()(ret)
        elif i == rank:
            if self.value[i-2] == -1 and self.value[i-1] == -1:
                ret = [self.value[x] for x in range(rank)]
                ret[i-2] = 1
                ret[i-1] = 1
                return self.parent()(ret)
        else:
            return None

    def f(self, i):
        r"""
        Returns the action of `f_i` on self.

        EXAMPLES::

            sage: D = CrystalOfSpinsPlus(['D',4])
            sage: [[D.list()[m].f(i) for i in range(1,4)] for m in range(8)]
            [[None, None, None], [None, +-+-, None], [-++-, None, +--+], [None, None, -+-+],
            [-+-+, None, None], [None, --++, None], [None, None, None], [None, None, None]]

        ::

            sage: E = CrystalOfSpinsMinus(['D',4])
            sage: [[E[m].f(i) for i in range(1,4)] for m in range(8)]
            [[None, None, ++-+], [None, +-++, None], [-+++, None, None], [None, None, None],
            [-+--, None, None], [None, --+-, None], [None, None, ---+], [None, None, None]]
        """
        assert i in self.index_set()
        rank = self.parent().cartan_type().n
        if i < rank:
            if self.value[i-1] == 1 and self.value[i] == -1:
                ret = [self.value[x] for x in range(rank)]
                ret[i-1] = -1
                ret[i] = 1
                return self.parent()(ret)
        elif i == rank:
            if self.value[i-2] == 1 and self.value[i-1] == 1:
                ret = [self.value[x] for x in range(rank)]
                ret[i-2] = -1
                ret[i-1] = -1
                return self.parent()(ret)
        else:
            return None
