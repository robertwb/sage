r"""
Crystals

Let $T$ be a CartanType with index set $I$, and $W$ be a realization of the
type $T$ weight lattice.

A type $T$ crystal $C$ is an oriented graph equiped with a weight
function the nodes to some realization of the type $T$ weight lattice
such that:
\begin{itemize}
\item each edge has a label in $I$
\item for each $i$ in $I$, each node $x$ has:
    - at most one $i$-successor $f_i(x)$
    - at most one $i$-predecessor $e_i(x)$
   Furthermore, when the exists,
    - $f_i(x)$.weight() = x.weight() - $\alpha_i$
    - $e_i(x)$.weight() = x.weight() + $\alpha_i$

This crystal actually models a representation of a Lie algebra if it
satisfies some further local conditions due to Stembridge.

EXAMPLES:

We construct the type $A_5$ crystal on letters

    sage: C = CrystalOfLetters(['A',5]); C
    The crystal of letters for type ['A', 5]

It has a single highest weight element:
    sage: C.module_generators
    [1]

A crystal is a CombinatorialClass; and we can count and list its elements
in the usual way:
    sage: C.count()    # todo: not implemented
    5
    sage: C.list()
    [1, 2, 3, 4, 5]
"""

#*****************************************************************************
#       Copyright (C) 2007 Anne Schilling <anne at math.ucdavis.edu>
#                          Nicolas Thiery <nthiery at users.sf.net>
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

from sage.structure.parent     import Parent
from sage.structure.element    import Element
from sage.combinat.combinat    import CombinatorialClass
from sage.combinat.cartan_type import CartanType

## MuPAD-Combinat's Cat::Crystal
class Crystal(CombinatorialClass, Parent):
    r"""
    The abstract class of crystals

    instances of this class should have the following attributes:
    \begin{itemize}
    \item cartan_type
    \item index_set
        the index set of the cartan type
    \item module_generators
        a list (or container) of distinct elements which generate the crystal
    \item weight_lattice_realization
    \end{itemize}
    """

    def __iter__(self):
        r"""
        Returns an iterator over the elements of the crystal.

        Memory complexity: O(depth of the crystal)

        Caveats: this assume that the crystal is highest weight, and
        that the module generators are all highest weights.
        This second restriction would be easy to remove.

        EXAMPLES:
            sage: C = CrystalOfLetters(['A',5])
            sage: [x for x in C]
            [1, 2, 3, 4, 5, 6]
        """
        def rec(x):
            for i in x.index_set():
                child = x.f(i);
                if child is None:
                    continue
                hasParent = False;
                for j in x.index_set():
                    if j == i:
                        break
                    if not child.e(j) == None:
                        hasParent = True
                        break
                if hasParent:
                    break;
                yield child
                for y in rec(child):
                    yield y;
        for generator in self.module_generators:
            # This is just in case the module_generators
            if not generator.is_highest_weight():
                continue
            yield generator;
            for x in rec(generator):
                yield x;


class CrystalElement(Element):
    r"""
    The abstract class of crystal elements

    Sub classes should implement:
    \begin{itemize}
    \item x.e(i)        (returning $e_i(x)$)
    \item x.f(i)        (returning $f_i(x)$)
    \item x.weight()
    \end{itemize}
    """

    def index_set(self):
        return self._parent.index_set

    def e(self, i):
        r"""
        Returns $e_i(x)$ if it exists or None otherwise
        """
        raise NotImplementedError

    def f(self, i):
        r"""
        Returns $f_i(x)$ if it exists or None otherwise
        """
        raise NotImplementedError

    def epsilon(self, i):
        r"""
        TESTS:
            # rather minimal tests
            sage: C = CrystalOfLetters(['A',5])
            sage: C(1).epsilon(1)
            0
            sage: C(2).epsilon(1)
            1
        """
        assert i in self.index_set()
        x = self
        eps = 0
        while True:
            x = x.e(i)
            if x is None:
                break
            eps = eps+1
        return eps

    def phi(self, i):
        r"""
        TESTS:
            # rather minimal tests
            sage: C = CrystalOfLetters(['A',5])
            sage: C(1).phi(1)
            1
            sage: C(2).phi(1)
            0
        """
        assert i in self.index_set()
        x = self
        phi = 0
        while True:
            x = x.f(i)
            if x is None:
                break
            phi = phi+1
        return phi

    def is_highest_weight(self):
	r"""
        TEST:
	    sage: C = CrystalOfLetters(['A',5])
	    sage: C(1).is_highest_weight()
	    True
	    sage: C(2).is_highest_weight()
	    False
	"""
	return all(self.e(i) == None for i in self.index_set())
