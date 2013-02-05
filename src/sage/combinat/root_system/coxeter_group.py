"""
Coxeter Groups
"""
#*****************************************************************************
#       Copyright (C) 2010 Nicolas Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.cachefunc import cached_function, cached_method
from sage.categories.category import Category
from sage.categories.finite_coxeter_groups import FiniteCoxeterGroups
from sage.categories.finite_permutation_groups import FinitePermutationGroups
from sage.groups.perm_gps.permgroup_element import PermutationGroupElement
from sage.combinat.root_system.weyl_group import WeylGroup
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.combinat.root_system.cartan_type import CartanType
from sage.groups.perm_gps.permgroup import PermutationGroup_generic

def CoxeterGroup(cartan_type, implementation = None):
    """
    INPUT:

     - ``cartan_type`` -- a cartan type (or coercible into; see :class:`CartanType`)
     - ``implementation`` -- "permutation", "matrix", "coxeter3", or None (default: None)

    Returns an implementation of the Coxeter group of type
    ``cartan_type``.

    EXAMPLES:

    If ``implementation`` is not specified, a permutation
    representation is returned whenever possible (finite irreducible
    Cartan type, with the GAP3 Chevie package available)::

        sage: W = CoxeterGroup(["A",2])
        sage: W                                   # optional (requires chevie)
        Permutation Group with generators [(1,3)(2,5)(4,6), (1,4)(2,3)(5,6)]

    Otherwise, a Weyl group is returned::

        sage: W = CoxeterGroup(["A",3,1])
        sage: W
        Weyl Group of type ['A', 3, 1] (as a matrix group acting on the root space)

    We now use the ``implementation`` option::

        sage: W = CoxeterGroup(["A",2], implementation = "permutation") # optional (requires chevie)
        sage: W                                                         # optional (requires chevie)
        Permutation Group with generators [(1,3)(2,5)(4,6), (1,4)(2,3)(5,6)]
        sage: W.category()                       # optional (requires chevie)
        Join of Category of finite permutation groups and Category of finite coxeter groups

        sage: W = CoxeterGroup(["A",2], implementation = "matrix")
        sage: W
        Weyl Group of type ['A', 2] (as a matrix group acting on the ambient space)

        sage: W = CoxeterGroup(["H",3], implementation = "matrix")
        Traceback (most recent call last):
        ...
        NotImplementedError: Coxeter group of type ['H', 3] as matrix group not implemented

        sage: W = CoxeterGroup(["A",4,1], implementation = "permutation")
        Traceback (most recent call last):
        ...
        NotImplementedError: Coxeter group of type ['A', 4, 1] as permutation group not implemented

    """
    assert implementation in ["permutation", "matrix", "coxeter3", None]
    cartan_type = CartanType(cartan_type)

    if implementation is None:
        if cartan_type.is_finite() and cartan_type.is_irreducible() and is_chevie_available():
            implementation = "permutation"
        else:
            implementation = "matrix"

    if implementation == "coxeter3":
        try:
            from sage.libs.coxeter3.coxeter_group import CoxeterGroup
        except ImportError:
            raise RuntimeError, "coxeter3 must be installed"
        else:
            return CoxeterGroup(cartan_type)
    if implementation == "permutation" and is_chevie_available() and \
       cartan_type.is_finite() and cartan_type.is_irreducible():
        return CoxeterGroupAsPermutationGroup(cartan_type)
    elif implementation == "matrix" and cartan_type.is_crystalographic():
        return WeylGroup(cartan_type)
    else:
        raise NotImplementedError, "Coxeter group of type %s as %s group not implemented "%(cartan_type, implementation)

@cached_function
def is_chevie_available():
    r"""
    Tests whether the GAP3 Chevie package is available

    EXAMPLES::

        sage: from sage.combinat.root_system.coxeter_group import is_chevie_available
        sage: is_chevie_available() # random
        False
        sage: is_chevie_available() in [True, False]
        True
    """
    try:
        from sage.interfaces.gap3 import gap3
        gap3._start()
        gap3.load_package("chevie")
        return True
    except Exception:
        return False

class CoxeterGroupAsPermutationGroup(UniqueRepresentation, PermutationGroup_generic):

    @staticmethod
    def __classcall__(cls, cartan_type):
        """
        TESTS::

            sage: from sage.combinat.root_system.coxeter_group import CoxeterGroupAsPermutationGroup
            sage: W1 = CoxeterGroupAsPermutationGroup(CartanType(["H",3])) # optional (require chevie)
            sage: W2 = CoxeterGroupAsPermutationGroup(["H",3])             # optional (require chevie)
            sage: W1 is W2                                                 # optional (require chevie)
            True
        """
        cartan_type = CartanType(cartan_type)
        return super(CoxeterGroupAsPermutationGroup, cls).__classcall__(cls, cartan_type)

    def __init__(self, cartan_type):
        """
        Construct this Coxeter group as a Sage permutation group, by
        fetching the permutation representation of the generators from
        Chevie's database.

        TESTS::

            sage: from sage.combinat.root_system.coxeter_group import CoxeterGroupAsPermutationGroup
            sage: W = CoxeterGroupAsPermutationGroup(CartanType(["H",3])) # optional (require chevie)
            sage: TestSuite(W).run()             # optional (require chevie)
        """
        assert cartan_type.is_finite()
        assert cartan_type.is_irreducible()
        self._semi_simple_rank = cartan_type.n
        from sage.interfaces.gap3 import gap3
        gap3._start()
        gap3.load_package("chevie")
        self._gap_group = gap3('CoxeterGroup("%s",%s)'%(cartan_type.letter,cartan_type.n))
        # Following #9032, x.N is an alias for x.numerical_approx in every Sage object ...
        N = self._gap_group.__getattr__("N").sage()
        generators = [str(x) for x in self._gap_group.generators]
        self._is_positive_root = [None] + [ True ] * N + [False]*N
        PermutationGroup_generic.__init__(self, gens = generators,
                                          category = Category.join([FinitePermutationGroups(), FiniteCoxeterGroups()]))

    def _element_class(self):
        """
        A temporary workaround for compatibility with Sage's
        permutation groups

        TESTS::

            sage: W = CoxeterGroup(["H",3])                                  # optional (require chevie)
            sage: W._element_class() is W.element_class                      # optional (require chevie)
            True
        """
        return self.element_class

    def index_set(self):
        """
        Returns the index set of this Coxeter group

        EXAMPLES::

            sage: W = CoxeterGroup(["H",3], implementation = "permutation")  # optional (requires chevie)
            sage: W.index_set() # optional (requires chevie)
            [1, 2, 3]

        """
        return range(1, self._semi_simple_rank+1)

    @cached_method
    def reflection(self, i):
        """
        Returns the `i`-th reflection of ``self``.

        For `i` in `1,\dots,n`, this gives the `i`-th simple
        reflection of ``self``.

        EXAMPLES::

            sage: W = CoxeterGroup(["H",3], implementation = "permutation") # optional (requires chevie)
            sage: W.simple_reflection(1) # optional (requires chevie)
            (1,16)(2,5)(4,7)(6,9)(8,10)(11,13)(12,14)(17,20)(19,22)(21,24)(23,25)(26,28)(27,29)
            sage: W.simple_reflection(2) # optional (requires chevie)
            (1,4)(2,17)(3,6)(5,7)(9,11)(10,12)(14,15)(16,19)(18,21)(20,22)(24,26)(25,27)(29,30)
            sage: W.simple_reflection(3) # optional (requires chevie)
            (2,6)(3,18)(4,8)(5,9)(7,10)(11,12)(13,14)(17,21)(19,23)(20,24)(22,25)(26,27)(28,29)
            sage: W.reflection(4)        # optional (requires chevie)
            (1,5)(2,22)(3,11)(4,19)(7,17)(8,12)(9,13)(10,15)(16,20)(18,26)(23,27)(24,28)(25,30)
            sage: W.reflection(5)        # optional (requires chevie)
            (1,22)(2,4)(3,9)(5,20)(6,13)(7,16)(8,14)(12,15)(17,19)(18,24)(21,28)(23,29)(27,30)
            sage: W.reflection(6)        # optional (requires chevie)
            (1,8)(2,18)(3,17)(5,12)(6,21)(7,11)(9,10)(13,15)(16,23)(20,27)(22,26)(24,25)(28,30)
        """
        return self(str(self._gap_group.Reflection(i)))

    simple_reflection = reflection

    class Element(PermutationGroupElement):

        def has_descent(self, i, side = 'right', positive=False):
            """
            Returns whether `i` is a (left/right) descent of ``self``.

            See :meth:`sage.categories.coxeter_groups.CoxeterGroups.ElementMethods.descents` for a
            description of the options.

            EXAMPLES::

                sage: W = CoxeterGroup(["A",3])
                sage: s = W.simple_reflections()
                sage: w = s[1] * s[2] * s[3]
                sage: w.has_descent(3)
                True
                sage: [ w.has_descent(i)                  for i in [1,2,3] ]
                [False, False, True]
                sage: [ w.has_descent(i, side = 'left')   for i in [1,2,3] ]
                [True, False, False]
                sage: [ w.has_descent(i, positive = True) for i in [1,2,3] ]
                [True, True, False]

            This implementation is a plain copy of that of
            ``CoxeterGroups``. It is there as a workaround since
            `PermutationGroupElement` currently redefines abusively
            :meth:`has_descent` as if the group was the full symmetric
            group.
            """
            assert isinstance(positive, bool)
            if side == 'right':
                return self.has_right_descent(i) != positive
            else:
                assert side == 'left'
                return self.has_left_descent(i)  != positive

        def has_left_descent(self, i):
            r"""
            Returns whether ``i`` is a descent of ``self`` by testing
            whether ``i`` is mapped to a negative root.

            EXAMPLES::

                sage: W = CoxeterGroup(["A",3], implementation = "permutation") # optional (requires chevie)
                sage: s = W.simple_reflections() # optional (requires chevie)
                sage: (s[1]*s[2]).has_left_descent(1) # optional (requires chevie)
                True
                sage: (s[1]*s[2]).has_left_descent(2) # optional (requires chevie)
                False
            """
            return not self.parent()._is_positive_root[self(i)]

        def __cmp__(self, other):
            r"""
            Without this comparison method, the initialization of this
            permutation group fails ...

            EXAMPLES::

                sage: W = CoxeterGroup(["B",3], implementation = "permutation") # optional (requires chevie)
                sage: cmp(W.an_element(), W.one())        # optional (requires chevie)
                1
            """
            return super(CoxeterGroupAsPermutationGroup.Element, self).__cmp__(other)
