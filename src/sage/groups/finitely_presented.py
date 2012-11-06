"""
Finitely Presented Groups

Finitely presented groups are constructed as quotients of
:mod:`~sage.groups.free_group` ::

    sage: F.<a,b,c> = FreeGroup()
    sage: G = F / [a^2, b^2, c^2, a*b*c*a*b*c]
    sage: G
    Finitely presented group < a, b, c | a^2, b^2, c^2, a*b*c*a*b*c >

One can create their elements by mutiplying the generators or by
specifying a Tietze list (see
:meth:`~sage.groups.finitely_presented.FinitelyPresentedGroupElement.Tietze`)
as in the case of free groups::

    sage: G.gen(0) * G.gen(1)
    a*b
    sage: G([1,2,-1])
    a*b*a^-1
    sage: a.parent()
    Free Group on generators {a, b, c}
    sage: G.inject_variables()
    Defining a, b, c
    sage: a.parent()
    Finitely presented group < a, b, c | a^2, b^2, c^2, a*b*c*a*b*c >

Notice that, even if they are represented in the same way, the
elements of a finitely presented group and the elements of the
corresponding free group are not the same thing.  However, they can be
converted from one parent to the other::

    sage: F.<a,b,c> = FreeGroup()
    sage: G = F / [a^2,b^2,c^2,a*b*c*a*b*c]
    sage: F([1])
    a
    sage: G([1])
    a
    sage: F([1]) is G([1])
    False
    sage: F([1]) == G([1])
    False
    sage: G(a*b/c)
    a*b*c^-1
    sage: F(G(a*b/c))
    a*b*c^-1

Finitely presented groups are implemented via GAP. You can use the
:meth:`~sage.groups.libgap_wrapper.ParentLibGAP.gap` method to access
the underlying LibGAP object::

    sage: G = FreeGroup(2)
    sage: G.inject_variables()
    Defining x0, x1
    sage: H = G / (x0^2, (x0*x1)^2, x1^2)
    sage: H.gap()
    <fp group on the generators [ x0, x1 ]>

This can be useful, for example, to use GAP functions that are not yet
wrapped in Sage::

    sage: H.gap().LowerCentralSeries()
    [ Group(<fp, no generators known>), Group(<fp, no generators known>) ]

The same holds for the group elements::

    sage: G = FreeGroup(2)
    sage: H = G / (G([1, 1]), G([2, 2, 2]), G([1, 2, -1, -2]));  H
    Finitely presented group < x0, x1 | x0^2, x1^3, x0*x1*x0^-1*x1^-1 >
    sage: a = H([1])
    sage: a
    x0
    sage: a.gap()
    x0
    sage: a.gap().Order()
    2
    sage: type(_)    # note that the above output is not a Sage integer
    <type 'sage.libs.gap.element.GapElement_Integer'>

Caution: some methods are not granted to finish, since they try to give an
answer to problems that are, in general, undecideable. In those cases, the
process is finished when the available memory is exhausted.

AUTHOR:

- Miguel Angel Marco Buzunariz
"""

##############################################################################
#       Copyright (C) 2012 Miguel Angel Marco Buzunariz <mmarco@unizar.es>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
##############################################################################


from sage.groups.group import Group
from sage.groups.libgap_wrapper import ParentLibGAP, ElementLibGAP
from sage.structure.unique_representation import UniqueRepresentation
from sage.libs.gap.libgap import libgap
from sage.libs.gap.element import GapElement
from sage.rings.integer import Integer
from sage.rings.integer_ring import IntegerRing
from sage.misc.cachefunc import cached_method
from sage.groups.free_group import FreeGroupElement

from sage.structure.element import Element, MultiplicativeGroupElement
from sage.interfaces.gap import gap
from sage.rings.integer import Integer
from sage.rings.integer_ring import IntegerRing
from sage.functions.generalized import sign
from sage.matrix.constructor import matrix

class FinitelyPresentedGroupElement(FreeGroupElement):
    """
    A wrapper of GAP's Finitely Presented Group elements.

    The elements are created by passing the Tietze list that determines them.

    EXAMPLES::

        sage: G = FreeGroup('a, b')
        sage: H = G / [G([1]), G([2, 2, 2])]
        sage: H([1, 2, 1, -1])
        a*b
        sage: H([1, 2, 1, -2])
        a*b*a*b^-1
        sage: x = H([1, 2, -1, -2])
        sage: x
        a*b*a^-1*b^-1
        sage: y = H([2, 2, 2, 1, -2, -2, -2])
        sage: y
        b^3*a*b^-3
        sage: x*y
        a*b*a^-1*b^2*a*b^-3
        sage: x^(-1)
        b*a*b^-1*a^-1
    """

    def __init__(self, x, parent):
        """
        The Python constructor.

        See :class:`FinitelyPresentedGroupElement` for details.

        TESTS::

            sage: G = FreeGroup('a, b')
            sage: H = G / [G([1]), G([2, 2, 2])]
            sage: H([1, 2, 1, -1])
            a*b

            sage: TestSuite(G).run()
            sage: TestSuite(x).run()

            sage: G.<a,b> = FreeGroup()
            sage: H = G / (G([1]), G([2, 2, 2]))
            sage: x = H([1, 2, -1, -2])
            sage: TestSuite(x).run()
            sage: TestSuite(G.one()).run()
        """
        if not isinstance(x, GapElement):
            F = parent.free_group()
            free_element = F(x)
            fp_family = parent.one().gap().FamilyObj()
            x = libgap.ElementOfFpGroup(fp_family, free_element.gap())
        ElementLibGAP.__init__(self, x, parent)

    def __reduce__(self):
        """
        TESTS::

            sage: F.<a,b> = FreeGroup()
            sage: G = F / [a*b, a^2]
            sage: G.inject_variables()
            Defining a, b
            sage: a.__reduce__()
            (Finitely presented group < a, b | a*b, a^2 >, ((1,),))
            sage: (a*b*a^-1).__reduce__()
            (Finitely presented group < a, b | a*b, a^2 >, ((1, 2, -1),))

            sage: F.<a,b,c> = FreeGroup('a, b, c')
            sage: G = F.quotient([a*b*c/(b*c*a), a*b*c/(c*a*b)])
            sage: G.__reduce__()
            (<class 'sage.groups.finitely_presented.FinitelyPresentedGroup'>,
             (Free Group on generators {a, b, c},
             (a*b*c*a^-1*c^-1*b^-1, a*b*c*b^-1*a^-1*c^-1)))
            sage: G.inject_variables()
            Defining a, b, c
            sage: x = a*b*c
            sage: x.__reduce__()
            (Finitely presented group < a, b, c | a*b*c*a^-1*c^-1*b^-1, a*b*c*b^-1*a^-1*c^-1 >,
             ((1, 2, 3),))
        """
        return (self.parent(), tuple([self.Tietze()]))

    def _repr_(self):
        """
        Return a string representation.

        OUTPUT:

        String.

        EXAMPLES::

            sage: G.<a,b> = FreeGroup()
            sage: H = G / [a^2, b^3]
            sage: H.gen(0)
            a
            sage: H.gen(0)._repr_()
            'a'
            sage: H.one()
            1
        """
        # computing that an element is actually one can be very expensive
        if self.Tietze() == ():
            return '1'
        else:
            return self.gap()._repr_()

    @cached_method
    def Tietze(self):
        """
        Return the Tietze list of the element.

        The Tietze list of a word is a list of integers that represent
        the letters in the word.  A positive integer `i` represents
        the letter corresponding to the `i`-th generator of the group.
        Negative integers represent the inverses of generators.

        OUTPUT:

        A tuple of integers.

        EXAMPLES::

            sage: G = FreeGroup('a, b')
            sage: H = G / (G([1]), G([2, 2, 2]))
            sage: H.inject_variables()
            Defining a, b
            sage: a.Tietze()
            (1,)
            sage: x = a^2*b^(-3)*a^(-2)
            sage: x.Tietze()
            (1, 1, -2, -2, -2, -1, -1)
        """
        tl = self.gap().UnderlyingElement().TietzeWordAbstractWord()
        return tuple(tl.sage())


def wrap_FpGroup(libgap_fpgroup):
    """
    Wrap a GAP finitely presented group.

    This function changes the comparison method of
    ``libgap_free_group`` to comparison by Python ``id``. If you want
    to put the LibGAP free group into a container (set, dict) then you
    should understand the implications of
    :meth:`~sage.libs.gap.element.GapElement._set_compare_by_id`. To
    be safe, it is recommended that you just work with the resulting
    Sage :class:`FinitelyPresentedGroup`.

    INPUT:

    - ``libgap_fpgroup`` -- a LibGAP finitely presented group

    OUTPUT:

    A Sage :class:`FinitelyPresentedGroup`.

    EXAMPLES:

    First construct a LibGAP finitely presented group::

        sage: F = libgap.FreeGroup(['a', 'b'])
        sage: a_cubed = F.GeneratorsOfGroup()[0] ^ 3
        sage: P = F / libgap([ a_cubed ]);   P
        <fp group of size infinity on the generators [ a, b ]>
        sage: type(P)
        <type 'sage.libs.gap.element.GapElement'>

    Now wrap it::

        sage: from sage.groups.finitely_presented import wrap_FpGroup
        sage: wrap_FpGroup(P)
        Finitely presented group < a, b | a^3 >
    """
    assert libgap_fpgroup.IsFpGroup()
    libgap_fpgroup._set_compare_by_id()
    from sage.groups.free_group import wrap_FreeGroup
    free_group = wrap_FreeGroup(libgap_fpgroup.FreeGroupOfFpGroup())
    relations = tuple( free_group(rel.UnderlyingElement())
                       for rel in libgap_fpgroup.RelatorsOfFpGroup() )
    return FinitelyPresentedGroup(free_group, relations)


class FinitelyPresentedGroup(UniqueRepresentation, Group, ParentLibGAP):
    """
    A class that wraps GAP's Finitely Presented Groups

    .. warning::

        You should use
        :meth:`~sage.groups.free_group.FreeGroup_class.quotient` to
        construct finitely presented groups as quotients of free
        groups.

    EXAMPLES::

        sage: G.<a,b> = FreeGroup()
        sage: H = G / [a, b^3]
        sage: H
        Finitely presented group < a, b | a, b^3 >
        sage: H.gens()
        (a, b)

        sage: F.<a,b> = FreeGroup('a, b')
        sage: J = F / (F([1]), F([2, 2, 2]))
        sage: J is H
        True

        sage: G = FreeGroup(2)
        sage: H = G / (G([1, 1]), G([2, 2, 2]))
        sage: H.gens()
        (x0, x1)
        sage: H.gen(0)
        x0
        sage: H.ngens()
        2
        sage: H.gap()
        <fp group on the generators [ x0, x1 ]>
        sage: type(_)
        <type 'sage.libs.gap.element.GapElement'>
    """
    Element = FinitelyPresentedGroupElement

    def __init__(self, free_group, relations):
        """
        The Python constructor

        TESTS::

            sage: G = FreeGroup('a, b')
            sage: H = G / (G([1]), G([2])^3)
            sage: H
            Finitely presented group < a, b | a, b^3 >

            sage: F = FreeGroup('a, b')
            sage: J = F / (F([1]), F([2, 2, 2]))
            sage: J is H
            True

            sage: TestSuite(H).run()
            sage: TestSuite(J).run()
        """
        from sage.groups.free_group import is_FreeGroup
        assert is_FreeGroup(free_group)
        assert isinstance(relations, tuple)
        self._free_group = free_group
        self._relations = relations
        self._assign_names(free_group.variable_names())
        parent_gap = free_group.gap() / libgap([ rel.gap() for rel in relations])
        ParentLibGAP.__init__(self, parent_gap)
        Group.__init__(self)

    def __reduce__(self):
        """
        TESTS::

            sage: F = FreeGroup(4)
            sage: F.inject_variables()
            Defining x0, x1, x2, x3
            sage: G = F.quotient([x0*x2, x3*x1*x3, x2*x1*x2])
            sage: G.__reduce__()
            (<class 'sage.groups.finitely_presented.FinitelyPresentedGroup'>,
             (Free Group on generators {x0, x1, x2, x3},
              (x0*x2, x3*x1*x3, x2*x1*x2)))

            sage: F.<a,b,c> = FreeGroup()
            sage: F.inject_variables()
            Defining a, b, c
            sage: G = F / [a*b*c/(b*c*a), a*b*c/(c*a*b)]
            sage: G.__reduce__()
            (<class 'sage.groups.finitely_presented.FinitelyPresentedGroup'>,
             (Free Group on generators {a, b, c},
              (a*b*c*a^-1*c^-1*b^-1, a*b*c*b^-1*a^-1*c^-1)))
        """
        return (FinitelyPresentedGroup, (self._free_group, self._relations))

    def _repr_(self):
        """
        Return a string representation.

        OUTPUT:

        String.

        TESTS::

            sage: G.<a,b> = FreeGroup()
            sage: H = G / (G([1]), G([2])^3)
            sage: H  # indirect doctest
            Finitely presented group < a, b | a, b^3 >
            sage: H._repr_()
            'Finitely presented group < a, b | a, b^3 >'
        """
        gens = ', '.join(self.variable_names())
        rels = ', '.join([ str(r) for r in self.relations() ])
        return 'Finitely presented group ' + '< '+ gens + ' | ' + rels + ' >'

    def _latex_(self):
        """
        Return a LaTeX representation

        OUTPUT:

        String. A valid LaTeX math command sequence.

        TESTS::

            sage: F=FreeGroup(4)
            sage: F.inject_variables()
            Defining x0, x1, x2, x3
            sage: G=F.quotient([x0*x2, x3*x1*x3, x2*x1*x2])
            sage: G._latex_()
            '\\langle x_{0}, x_{1}, x_{2}, x_{3} \\mid x_{0}\\cdot x_{2} , x_{3}\\cdot x_{1}\\cdot x_{3} , x_{2}\\cdot x_{1}\\cdot x_{2}\\rangle'
        """
        r = '\\langle '
        for i in range(self.ngens()):
            r = r+self.gen(i)._latex_()
            if i < self.ngens()-1:
                r = r+', '
        r = r+' \\mid '
        for i in range(len(self._relations)):
            r = r+(self._relations)[i]._latex_()
            if i < len(self.relations())-1:
                r = r+' , '
        r = r+'\\rangle'
        return r

    def free_group(self):
        """
        Return the free group (without relations).

        OUTPUT:

        A :func:`~sage.groups.free_group.FreeGroup`.

        EXAMPLES::

            sage: G.<a,b,c> = FreeGroup()
            sage: H = G / (a^2, b^3, a*b*~a*~b)
            sage: H.free_group()
            Free Group on generators {a, b, c}
            sage: H.free_group() is G
            True
        """
        return self._free_group

    def relations(self):
        """
        Return the relations of the group.

        OUTPUT:

        The relations as a touple of elements of :meth:`free_group`.

        EXAMPLES::

            sage: F = FreeGroup(5, 'x')
            sage: F.inject_variables()
            Defining x0, x1, x2, x3, x4
            sage: G = F.quotient([x0*x2, x3*x1*x3, x2*x1*x2])
            sage: G.relations()
            (x0*x2, x3*x1*x3, x2*x1*x2)
            sage: all(rel in F for rel in G.relations())
            True
        """
        return self._relations

    @cached_method
    def cardinality(self):
        """
        Compute the size of self.

        OUTPUT:

        Integer or ``Infinity``. The number of elements in the group.

        EXAMPLES::

            sage: G.<a,b> = FreeGroup('a, b')
            sage: H = G / (a^2, b^3, a*b*~a*~b)
            sage: H.cardinality()
            6

            sage: F.<a,b,c> = FreeGroup()
            sage: J = F / (F([1]), F([2, 2, 2]))
            sage: J.cardinality()
            +Infinity

        ALGORITHM:

            Uses GAP.

        .. WARNING::

            This is in general not a decidable problem, so it is not guaranteed to give an answer. If all
            the memory available for the Gap session is used before reaching a satisfactory answer, a
            MemoryError is raised. In this case, there could be future issues with orphaned objects.

            It is in general a good idea to be cautious when using this method. If the group is infinite,
            or too big, you should be prepared for a long computation that consumes all the memory without
            finishing.
        """
        if not libgap.IsFinite(self.gap()):
            from sage.rings.infinity import Infinity
            return Infinity
        try:
            size = self.gap().Size()
        except StandardError:
            raise MemoryError('Coset Enumeration ran out of memory of the GAP session')
        return size.sage()

    order = cardinality

    def as_permutation_group(self):
        """
        Return an isomorphic permutation group.

        The generators of the resulting group correspond to the images
        by the isomorphism of the generators of the given group.

        EXAMPLES::

            sage: G.<a,b> = FreeGroup()
            sage: H = G / (a^2, b^3, a*b*~a*~b)
            sage: H.as_permutation_group()
            Permutation Group with generators [(1,2)(3,5)(4,6), (1,3,4)(2,5,6)]

        ALGORITHM:

            Uses GAP's coset enumeration on the trivial subgroup.

        .. WARNING::

            This is in general not a decidable problem (in fact, it is not even posible to check if the
            group is finite or not). If all the memory available in the gap session is used, it returns a
            Memory Error. In this case, there could be future issues with orphaned objects.

            It is in general a good idea to be cautious when using this method. If the group is infinite,
            or too big, you should be prepared for a long computation that consumes all the memory without
            finishing.
        """
        try:
            l=list(map(lambda i: i.sage(), self.gap().CosetTable(self.gap().TrivialSubgroup())))
        except StandardError:
            MemoryError('Coset Enumeration ran out of memory of the GAP session')
        from sage.combinat.permutation import Permutation
        from sage.groups.perm_gps.permgroup import PermutationGroup
        return PermutationGroup(map(Permutation, [l[2*i] for i in range(len(l)/2)]))

    def _element_constructor_(self, *args, **kwds):
        """
        TESTS::

            sage: G.<a,b> = FreeGroup()
            sage: H = G / (G([1]), G([2, 2, 2]))
            sage: H([1, 2, 1, -1]) # indirect doctest
            a*b
            sage: H([1, 2, 1, -2]) # indirect doctest
            a*b*a*b^-1
        """
        if len(args)!=1:
            return self.element_class(*args, parent=self, **kwds)
        x = args[0]
        if x==1:
            return self.one()
        try:
            P = x.parent()
        except AttributeError:
            return self.element_class(x, parent=self, **kwds)
        if P is self._free_group:
            return self.element_class(x.Tietze(), parent=self, **kwds)
        return self.element_class(x, parent=self, **kwds)

    @cached_method
    def abelian_invariants(self):
        """
        Return the abelian invariants of self.

        The abelian invariants are given by a list of integers $i_1 \dots i_j$, such that the
        abelianization of the group is isomorphic to $\mathbb{Z}/(i_1) \\times \dots \\times
        \mathbb{Z}/(i_j)$.

        EXAMPLES::

            sage: G = FreeGroup(4, 'g')
            sage: G.inject_variables()
            Defining g0, g1, g2, g3
            sage: H = G.quotient([g1^2, g2*g1*g2^(-1)*g1^(-1), g1*g3^(-2), g0^4])
            sage: H.abelian_invariants()
            (0, 4, 4)

        ALGORITHM:

            Uses GAP.
        """
        invariants = self.gap().AbelianInvariants()
        return tuple( i.sage() for i in invariants )

    def simplification_isomorphism(self):
        """
        Return an isomorphism from self to a finitely presented group with a (hopefully) simpler
        presentation.

        EXAMPLES::

            sage: G.<a,b,c> = FreeGroup()
            sage: H = G / [a*b*c, a*b^2, c*b/c^2]
            sage: I = H.simplification_isomorphism()
            sage: I
            Generic morphism:
              From: Finitely presented group < a, b, c | a*b*c, a*b^2, c*b*c^-2 >
              To:   Finitely presented group < b |  >
            sage: I(a)
            b^-2
            sage: I(b)
            b
            sage: I(c)
            b

        TESTS::

            sage: F = FreeGroup(1)
            sage: G = F.quotient([F.0])
            sage: G.simplification_isomorphism()
            Generic morphism:
              From: Finitely presented group < x | x >
              To:   Finitely presented group <  |  >

        ALGORITM:

            Uses GAP.
        """
        I = self.gap().IsomorphismSimplifiedFpGroup()
        domain = self
        codomain = wrap_FpGroup(I.Range())
        phi = lambda x: codomain(I.ImageElm(x.gap()))
        return self.hom(phi, codomain)

    def simplified(self):
        """
        Return an isomorphic group with a (hopefully) simpler presentation.

        OUTPUT:

        A new finitely presented group. Use
        :meth:simplification_isomorphism` if you want to know the
        isomorphism.

        EXAMPLES::

            sage: G.<x,y> = FreeGroup()
            sage: H = G /  [x ^5, y ^4, y*x*y^3*x ^3]
            sage: H
            Finitely presented group < x, y | x^5, y^4, y*x*y^3*x^3 >
            sage: H.simplified()
            Finitely presented group < x, y | y^4, y*x*y^-1*x^-2, x^5 >

        A more complicate example::

            sage: G.<e0, e1, e2, e3, e4, e5, e6, e7, e8, e9> = FreeGroup()
            sage: rels = [e6, e5, e3, e9, e4*e7^-1*e6, e9*e7^-1*e0,
            ...           e0*e1^-1*e2, e5*e1^-1*e8, e4*e3^-1*e8, e2]
            sage: H = G.quotient(rels);  H
            Finitely presented group < e0, e1, e2, e3, e4, e5, e6, e7, e8, e9 |
            e6, e5, e3, e9, e4*e7^-1*e6, e9*e7^-1*e0, e0*e1^-1*e2, e5*e1^-1*e8, e4*e3^-1*e8, e2 >
            sage: H.simplified()
            Finitely presented group < e0 | e0^2 >
        """
        return self.simplification_isomorphism().codomain()

    def alexander_matrix(self):
        """
        Return the Alexander matrix of the group.

        This matrix is given by the fox derivatives of the relations
        with respect to the generators.

        OUTPUT:

        A group algebra-valued matrix. It depends on the (fixed)
        choice of presentation.

        EXAMPLES::

            sage: G.<a,b,c> = FreeGroup()
            sage: H = G.quotient([a*b/a/b, a*c/a/c, c*b/c/b])
            sage: H.alexander_matrix()
            [     B[1] - B[a*b*a^-1] B[a] - B[a*b*a^-1*b^-1]                       0]
            [     B[1] - B[a*c*a^-1]                       0 B[a] - B[a*c*a^-1*c^-1]]
            [                      0 B[c] - B[c*b*c^-1*b^-1]      B[1] - B[c*b*c^-1]]

            sage: G.<a,b,c,d,e> = FreeGroup()
            sage: H = G.quotient([a*b/a/b, a*c/a/c, a*d/a/d, b*c*d/(c*d*b), b*c*d/(d*b*c)])
            sage: H.alexander_matrix()
            [              B[1] - B[a*b*a^-1]          B[a] - B[a*b*a^-1*b^-1]                                0                                0                                0]
            [              B[1] - B[a*c*a^-1]                                0          B[a] - B[a*c*a^-1*c^-1]                                0                                0]
            [              B[1] - B[a*d*a^-1]                                0                                0          B[a] - B[a*d*a^-1*d^-1]                                0]
            [                               0             B[1] - B[b*c*d*b^-1]   B[b] - B[b*c*d*b^-1*d^-1*c^-1]      B[b*c] - B[b*c*d*b^-1*d^-1]                                0]
            [                               0        B[1] - B[b*c*d*c^-1*b^-1]             B[b] - B[b*c*d*c^-1] B[b*c] - B[b*c*d*c^-1*b^-1*d^-1]                                0]
        """
        rel = self.relations()
        gen = self._free_group.gens()
        return matrix(len(rel), len(gen),
                      lambda i,j: rel[i].fox_derivative(gen[j]))
