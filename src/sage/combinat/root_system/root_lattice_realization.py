"""
Root lattice realization
"""
#*****************************************************************************
#       Copyright (C) 2007 Nicolas M. Thiery <nthiery at users.sf.net>
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

from sage.misc.all import cached_method, attrcall
from sage.misc.lazy_attribute import lazy_attribute
from sage.sets.family import Family
from sage.rings.all import ZZ
from sage.structure.sage_object import SageObject
from sage.combinat.backtrack import TransitiveIdeal

class RootLatticeRealization(SageObject):
    def cartan_type(self):
        """
        EXAMPLES::

           sage: r = RootSystem(['A',4]).root_space()
           sage: r.cartan_type()
           ['A', 4]
        """
        return self.root_system.cartan_type()

    def index_set(self):
        """
        EXAMPLES:
           sage: r = RootSystem(['A',4]).root_space()
           sage: r.index_set()
           [1, 2, 3, 4]
        """
        return self.root_system.index_set()

    def dynkin_diagram(self):
        """
        EXAMPLES::

            sage: r = RootSystem(['A',4]).root_space()
            sage: r.dynkin_diagram()
            O---O---O---O
            1   2   3   4
            A4
        """
        return self.root_system.dynkin_diagram()

    def _name_string_helper(self, name, capitalize=True, base_ring=True, type=True):
        """
        EXAMPLES::

            sage: r = RootSystem(['A',4]).root_space()
            sage: r._name_string_helper("root")
            "Root space over the Rational Field of the Root system of type ['A', 4]"
            sage: r._name_string_helper("root", base_ring=False)
            "Root space of the Root system of type ['A', 4]"
            sage: r._name_string_helper("root", base_ring=False, type=False)
            'Root space'
            sage: r._name_string_helper("root", capitalize=False, base_ring=False, type=False)
            'root space'
        """
        s = ""
        if self.root_system.dual_side:
            s += "co"

        s += name + " "

        if self.base_ring() == ZZ:
            s += "lattice "
        else:
            s += "space "
            if base_ring:
                s += "over the %s "%self.base_ring()

        if type:
            s += "of the "
            if self.root_system.dual_side:
                s += repr(self.root_system.dual)
            else:
                s += repr(self.root_system)

        if capitalize:
            s = s[:1].upper() + s[1:]


        return s.strip()

    ##########################################################################
    # checks
    ##########################################################################

    def _test_root_lattice_realization(self, **options):
        """
        Runs sanity checks on this root lattice realization:
         - scalar products between simple roots and simple coroots
         - ...

        See also: :class:`Test`

        Examples::
            sage: RootSystem(['A',3]).root_lattice()._test_root_lattice_realization()
        """
        tester = self._tester(**options)
        alpha = self.simple_roots()
        alphacheck = self.simple_coroots()
        tester.assertEqual(alpha     .keys(), self.index_set())
        tester.assertEqual(alphacheck.keys(), self.index_set())

        dynkin_diagram = self.dynkin_diagram()
        for i in self.index_set():
            for j in self.index_set():
                tester.assertEqual(alpha[j].scalar(alphacheck[i]), dynkin_diagram[i,j])

        if self.cartan_type().is_affine():
            nullroot = self.null_root()
            nullcoroot = self.null_coroot()
            for k in alpha.keys():
                assert (nullroot.scalar(alphacheck[k])).is_zero()
                assert (alpha[k].scalar(nullcoroot)).is_zero()

        # Todo: add tests of highest root, roots, has_descent, ...


    ##########################################################################
    # highest root
    ##########################################################################

    @cached_method
    def highest_root(self):
        """
        Returns the highest root (for an irreducible finite root system)

        EXAMPLES::

            sage: RootSystem(['A',4]).ambient_space().highest_root()
            (1, 0, 0, 0, -1)

            sage: RootSystem(['E',6]).weight_space().highest_root()
            Lambda[2]

        """
        assert(self.root_system.is_finite())
        assert(self.root_system.is_irreducible())
        return self.a_long_simple_root().to_positive_chamber()

    @cached_method
    def a_long_simple_root(self):
        """
        Returns a long simple root, corresponding to the highest outgoing edge
        in the Dynkin diagram.

        Caveat: this may be break in affine type `A_{2n}^{(2)}`

        Caveat: meaningful/broken for non irreducible?

        TODO: implement CartanType.nodes_by_length as in
        MuPAD-Combinat (using CartanType.symmetrizer), and use it
        here.

        TESTS::

            sage: X=RootSystem(['A',1]).weight_space()
            sage: X.a_long_simple_root()
            2*Lambda[1]
            sage: X=RootSystem(['A',5]).weight_space()
            sage: X.a_long_simple_root()
            2*Lambda[1] - Lambda[2]
        """
        if self.dynkin_diagram().rank() == 1:
            return self.simple_roots()[self.index_set()[0]]
        longest=self.dynkin_diagram().outgoing_edges()[0]
        for j in self.dynkin_diagram().outgoing_edges():
            if j[2]>longest[2]:
                longest=j
        return self.simple_roots()[longest[0]]


    ##########################################################################
    # simple roots
    ##########################################################################

    @cached_method
    def simple_root(self, i):
        """
        Returns the `i^{th}` simple root.  This should be overridden by any
        subclass.

        EXAMPLES::

            sage: r = RootSystem(["A",3]).root_lattice()
            sage: r.simple_root(1)
            alpha[1]

        TESTS::

            sage: from sage.combinat.root_system.root_lattice_realization import RootLatticeRealization
            sage: RootLatticeRealization().simple_root(1)
            Traceback (most recent call last):
            ...
            NotImplementedError

        """
        raise NotImplementedError

    @cached_method
    def simple_roots(self):
        """
        Returns the family `(\alpha_i)_{i\in I}` of the simple roots.

        EXAMPLES::

            sage: alpha = RootSystem(["A",3]).root_lattice().simple_roots()
            sage: [alpha[i] for i in [1,2,3]]
            [alpha[1], alpha[2], alpha[3]]
        """
        if not hasattr(self,"_simple_roots"):
            self._simple_roots = Family(self.index_set(), self.simple_root)
            # Should we use rename to set a nice name for this family?
            # self._simple_roots.rename("alpha")
            # This break some doctests
        return self._simple_roots

    @cached_method
    def alpha(self):
        r"""
        Returns the family `(\alpha_i)_{i\in I}` of the simple roots,
        with the extra feature that, for simple irreducible root
        systems, `\alpha_0` yields the opposite of the highest root.

        EXAMPLES::

            sage: alpha = RootSystem(["A",2]).root_lattice().alpha()
            sage: alpha[1]
            alpha[1]
            sage: alpha[0]
            -alpha[1] - alpha[2]

        """
        if self.root_system.is_finite() and self.root_system.is_irreducible():
            return Family(self.index_set(), self.simple_root, \
                          hidden_keys = [0], hidden_function = lambda i: - self.highest_root())
        else:
            return self.simple_roots()

    ##########################################################################
    # roots
    ##########################################################################

    def roots(self):
        """
        Returns the roots of self.

        EXAMPLES::

            sage: RootSystem(['A',2]).ambient_lattice().roots()
            [(1, -1, 0), (1, 0, -1), (0, 1, -1), (-1, 1, 0), (-1, 0, 1), (0, -1, 1)]


        This matches with http://en.wikipedia.org/wiki/Root_systems::

            sage: for T in CartanType.samples(finite = True, crystalographic = True):
            ...       print "%s %3s %3s"%(T, len(RootSystem(T).root_lattice().roots()), len(RootSystem(T).weight_lattice().roots()))
            ['A', 1]   2   2
            ['A', 5]  30  30
            ['B', 1]   2   2
            ['B', 5]  50  50
            ['C', 1]   2   2
            ['C', 5]  50  50
            ['D', 2]   4   4
            ['D', 3]  12  12
            ['D', 5]  40  40
            ['E', 6]  72  72
            ['E', 7] 126 126
            ['E', 8] 240 240
            ['F', 4]  48  48
            ['G', 2]  12  12

        Todo: the result should be an enumerated set, and handle infinite root systems

        """
        return list(self.positive_roots()) + list(self.negative_roots())

    def positive_roots(self):
        r"""
        Returns the positive roots of self.

        EXAMPLES::

            sage: L = RootSystem(['A',3]).root_lattice()
            sage: sorted(L.positive_roots())
            [alpha[1], alpha[1] + alpha[2], alpha[1] + alpha[2] + alpha[3], alpha[2], alpha[2] + alpha[3], alpha[3]]

        Algorithm: generate them from the simple roots by applying
        successive reflections toward the positive chamber.
        """
        assert self.cartan_type().is_finite()
        return TransitiveIdeal(attrcall('pred'), self.simple_roots())

    def negative_roots(self):
        r"""
        Returns the negative roots of self.

        EXAMPLES::

            sage: L = RootSystem(['A', 2]).weight_lattice()
            sage: sorted(L.negative_roots())
            [-2*Lambda[1] + Lambda[2], -Lambda[1] - Lambda[2], Lambda[1] - 2*Lambda[2]]

        Algorithm: negate the positive roots

        """
        assert self.cartan_type().is_finite()
        from sage.combinat.combinat import MapCombinatorialClass
        return MapCombinatorialClass(self.positive_roots(), attrcall('__neg__'), "The negative roots of %s"%self)
        # Todo: use this instead once TransitiveIdeal will be a proper enumerated set
        #return self.positive_roots().map(attrcall('__negate__'))

    ##########################################################################
    # coroots
    ##########################################################################

    def coroot_lattice(self):
        """
        Returns the coroot lattice.

        EXAMPLES::

            sage: RootSystem(['A',2]).root_lattice().coroot_lattice()
            Coroot lattice of the Root system of type ['A', 2]

        """
        return self.root_system.coroot_lattice()

    def coroot_space(self):
        """
        Returns the coroot lattice.

        EXAMPLES::

            sage: RootSystem(['A',2]).root_lattice().coroot_space()
            Coroot space over the Rational Field of the Root system of type ['A', 2]

        """
        return self.root_system.coroot_space()


    def simple_coroot(self, i):
        """
        Returns the `i^{th}` simple coroot.

        EXAMPLES::

            sage: RootSystem(['A',2]).root_lattice().simple_coroot(1)
            alphacheck[1]
        """
        return self.coroot_lattice().simple_root(i)

    @cached_method
    def simple_coroots(self):
        """
        Returns the family `(\alpha^\vee_i)_{i\in I}` of the simple coroots.

        EXAMPLES::

            sage: alphacheck = RootSystem(['A',3]).root_lattice().simple_coroots()
            sage: [alphacheck[i] for i in [1, 2, 3]]
            [alphacheck[1], alphacheck[2], alphacheck[3]]

        """
        if not hasattr(self,"cache_simple_coroots"):
            self.cache_simple_coroots = Family(self.index_set(), self.simple_coroot)
            # Should we use rename to set a nice name for this family?
            # self.cache_simple_coroots.rename("alphacheck")
            # break some doctests
        return self.cache_simple_coroots

    def alphacheck(self):
        r"""
        Returns the family `(\alpha^\vee_i)_{i\in I}` of the simple
        coroots, with the extra feature that,  for simple irreducible
        root systems, `\alpha^\vee_0` yields the coroot associated to
        the opposite of the highest root (caveat: for non simply laced
        root systems, this is not the opposite of the highest coroot!)

        EXAMPLES::

            sage: alphacheck = RootSystem(["A",2]).ambient_space().alphacheck()
            sage: alphacheck
            Finite family {1: (1, -1, 0), 2: (0, 1, -1)}

        Here is now `\alpha^\vee_0`:

            (-1, 0, 1)

        TODO: add a non simply laced example

        Finaly, here is an affine example::

            sage: RootSystem(["A",2,1]).weight_space().alphacheck()
            Finite family {0: alphacheck[0], 1: alphacheck[1], 2: alphacheck[2]}

            sage: RootSystem(["A",3]).ambient_space().alphacheck()
            Finite family {1: (1, -1, 0, 0), 2: (0, 1, -1, 0), 3: (0, 0, 1, -1)}

        """
        if self.root_system.is_finite() and self.root_system.is_irreducible():
            return Family(self.index_set(), self.simple_coroot, \
                          hidden_keys = [0], hidden_function = lambda i: - self.cohighest_root())
        else:
            return self.simple_coroots()

    @cached_method
    def cohighest_root(self):
        """
        Returns the associated coroot of the highest root.  Note that this is
        usually not the highest coroot.

        EXAMPLES::

            sage: RootSystem(['A', 3]).ambient_space().cohighest_root()
            (1, 0, 0, -1)
        """
        return self.highest_root().associated_coroot()

    ##########################################################################
    # null_root
    ##########################################################################

    @cached_method
    def null_root(self):
        """
        Returns the null root of self. The null root is the smallest
        non trivial positive root which is orthogonal to all simple
        coroots. It exists for any affine root system.

        EXAMPLES::

            sage: RootSystem(['C',2,1]).root_lattice().null_root()
            alpha[0] + 2*alpha[1] + alpha[2]
            sage: RootSystem(['D',4,1]).root_lattice().null_root()
            alpha[0] + alpha[1] + 2*alpha[2] + alpha[3] + alpha[4]
            sage: RootSystem(['F',4,1]).root_lattice().null_root()
            alpha[0] + 2*alpha[1] + 3*alpha[2] + 4*alpha[3] + 2*alpha[4]
        """
        if self.cartan_type().is_affine():
            coef = self.cartan_type().a()
            return sum(coef[k]*self.simple_roots()[k] for k in coef.keys())

    ##########################################################################
    # null_coroot (Also called CanonicalCentralElement)
    ##########################################################################

    @cached_method
    def null_coroot(self):
        """
        Returns the null coroot of self. The null coroot is the smallest
        non trivial positive coroot which is orthogonal to all simple
        roots. It exists for any affine root system.

        EXAMPLES::

            sage: RootSystem(['C',2,1]).root_lattice().null_coroot()
            alphacheck[0] + alphacheck[1] + alphacheck[2]
            sage: RootSystem(['D',4,1]).root_lattice().null_coroot()
            alphacheck[0] + alphacheck[1] + 2*alphacheck[2] + alphacheck[3] + alphacheck[4]
            sage: RootSystem(['F',4,1]).root_lattice().null_coroot()
            alphacheck[0] + 2*alphacheck[1] + 3*alphacheck[2] + 2*alphacheck[3] + alphacheck[4]
        """
        assert(self.cartan_type().is_affine())
        coef = self.cartan_type().acheck()
        return sum(coef[k]*self.simple_coroots()[k] for k in coef.keys())

    ##########################################################################
    # reflections
    ##########################################################################

    def reflection(self, root, coroot=None):
        """
        Returns the reflection along the root, and across the
        hyperplane define by coroot, as a function from
        self to self.

        EXAMPLES::

            sage: space = RootSystem(['A',2]).weight_lattice()
            sage: x=space.simple_roots()[1]
            sage: y=space.simple_coroots()[1]
            sage: s = space.reflection(x,y)
            sage: x
            2*Lambda[1] - Lambda[2]
            sage: s(x)
            -2*Lambda[1] + Lambda[2]
            sage: s(-x)
            2*Lambda[1] - Lambda[2]
        """
        if coroot is None:
            coroot = root.associated_coroot()
        return lambda v: v - v.scalar(coroot) * root

    @cached_method
    def simple_reflection(self, i):
        """
        Returns the `i^{th}` simple reflection, as a function from
        self to self.

        INPUT:

        - ``i`` - i is in self's index set

        EXAMPLES::

            sage: space = RootSystem(['A',2]).ambient_lattice()
            sage: s = space.simple_reflection(1)
            sage: x = space.simple_roots()[1]
            sage: x
            (1, -1, 0)
            sage: s(x)
            (-1, 1, 0)
        """
        return self.reflection(self.simple_root(i), self.simple_coroot(i))

    @cached_method
    def simple_reflections(self):
        """
        Returns the family `(s_i)_{i\in I}` of the simple reflections
        of this root system.

        EXAMPLES::

            sage: r = RootSystem(["A", 2]).root_lattice()
            sage: s = r.simple_reflections()
            sage: s[1]( r.simple_root(1) )
            -alpha[1]

        TEST::

            sage: s
            simple reflections
        """
        res =  self.alpha().zip(self.reflection, self.alphacheck())
        # Should we use rename to set a nice name for this family?
        res.rename("simple reflections")
        return res

    s = simple_reflections

    ##########################################################################
    # projections
    ##########################################################################

    def projection(self, root, coroot=None, to_negative=True):
        r"""
        Returns the projection along the root, and across the
        hyperplane define by coroot, as a function `\pi` from self to
        self. `\pi` is a half-linear map which stabilizes the negative
        half space, and acts by reflection on the positive half space.

        If to_negative is False, then this project onto the positive
        half space instead.

        EXAMPLES::

            sage: space = RootSystem(['A',2]).weight_lattice()
            sage: x=space.simple_roots()[1]
            sage: y=space.simple_coroots()[1]
            sage: pi = space.projection(x,y)
            sage: x
            2*Lambda[1] - Lambda[2]
            sage: pi(x)
            -2*Lambda[1] + Lambda[2]
            sage: pi(-x)
            -2*Lambda[1] + Lambda[2]
            sage: pi = space.projection(x,y,False)
            sage: pi(-x)
            2*Lambda[1] - Lambda[2]
        """
        if coroot is None:
            coroot = root.associated_coroot()

        return lambda v: v - v.scalar(coroot) * root if ((v.scalar(coroot) > 0) == to_negative) else v

    @cached_method
    def simple_projection(self, i, to_negative=True):
        """
        Returns the projection along the `i^{th}` simple root, and across the
        hyperplane define by the `i^{th}` simple coroot, as a function from
        self to self.

        INPUT:

        - ``i`` - i is in self's index set

        EXAMPLES::

            sage: space = RootSystem(['A',2]).weight_lattice()
            sage: x = space.simple_roots()[1]
            sage: pi = space.simple_projection(1)
            sage: x
            2*Lambda[1] - Lambda[2]
            sage: pi(x)
            -2*Lambda[1] + Lambda[2]
            sage: pi(-x)
            -2*Lambda[1] + Lambda[2]
            sage: pi = space.simple_projection(1,False)
            sage: pi(-x)
            2*Lambda[1] - Lambda[2]
        """
        return self.projection(self.simple_root(i), self.simple_coroot(i), to_negative)

    @cached_method
    def simple_projections(self, to_negative=True):
        r"""
        Returns the family `(s_i)_{i\in I}` of the simple projections
        of this root system

        EXAMPLES::

            sage: space = RootSystem(['A',2]).weight_lattice()
            sage: pi = space.simple_projections()
            sage: x = space.simple_roots()
            sage: pi[1](x[2])
            -Lambda[1] + 2*Lambda[2]

        TESTS:
            sage: pi
            pi
        """
        res = self.alpha().zip(self.projection, self.alphacheck())
        # Should this use rename to set a nice name for this family?
        res.rename("pi")
        return res

    @lazy_attribute
    def pi(self):
        return self.simple_projections()

    @lazy_attribute
    def opi(self):
        return self.simple_projections(to_negative=False)

    def to_coroot_lattice_morphism(self):
        """
        Returns a morphism to the coroot lattice using the symmetrizer of the Cartan matrix.

        EXAMPLES::

            sage: R = RootSystem(['A',3]).root_space()
            sage: alpha = R.simple_roots()
            sage: f = R.to_coroot_lattice_morphism()
            sage: f(alpha[1])
            alphacheck[1]
            sage: f(alpha[1]+alpha[2])
            alphacheck[1] + alphacheck[2]
            sage: S = RootSystem(['G',2]).root_space()
            sage: alpha = S.simple_roots()
            sage: f = S.to_coroot_lattice_morphism()
            sage: f(alpha[1])
            alphacheck[1]
            sage: f(alpha[1]+alpha[2])
            alphacheck[1] + 3*alphacheck[2]
        """
        return self.module_morphism(diagonal=(lambda i : self.cartan_type().symmetrizer()[i]), codomain=self.coroot_space())


    ##########################################################################
    # Weyl group
    ##########################################################################

    def weyl_group(self, prefix=None):
        """
        Returns the Weyl group associated to self.

        EXAMPLES::

            sage: RootSystem(['F',4]).ambient_space().weyl_group()
            Weyl Group of type ['F', 4] (as a matrix group acting on the ambient space)
            sage: RootSystem(['F',4]).root_space().weyl_group()
            Weyl Group of type ['F', 4] (as a matrix group acting on the root space)

        """
        from sage.combinat.root_system.weyl_group import WeylGroup
        return WeylGroup(self, prefix=prefix)

class RootLatticeRealizationElement(object):
    def scalar(self, lambdacheck):
        """
        The natural pairing between this and the coroot lattice.  This should be overridden
        in subclasses.

        EXAMPLES::

            sage: r = RootSystem(['A',4]).root_lattice()
            sage: cr = RootSystem(['A',4]).coroot_lattice()
            sage: a1 = r.simple_root(1)
            sage: ac1 = cr.simple_root(1)
            sage: a1.scalar(ac1)
            2

        TESTS::

            sage: from sage.combinat.root_system.root_lattice_realization import RootLatticeRealizationElement
            sage: RootLatticeRealizationElement.scalar(a1, ac1)
            Traceback (most recent call last):
            ...
            NotImplementedError

        """
        raise NotImplementedError


    ##########################################################################
    # Action and orbits w.r.t. the Weyl group
    ##########################################################################

    def simple_reflection(self, i):
        """
        The image of self by the `i^{th}` simple reflection.

        EXAMPLES::

            sage: alpha = RootSystem(["A", 3]).root_lattice().alpha()
            sage: alpha[1].simple_reflection(2)
            alpha[1] + alpha[2]

        """
        # Subclasses should optimize whenever possible!
        return self.parent().simple_reflections()[i](self)

    def simple_reflections(self):
        """
        The images of self by all the simple reflections
        """
        return [s(self) for s in self.parent().simple_reflections()]

    def orbit(self):
        r"""
        The orbit of self under the action of the Weyl group

        EXAMPLES::

        `\rho` is a regular element whose orbit is in bijection with the Weyl group.
        In particular, it as 6 elements for the symmetric group `S_3`::

            sage: L = RootSystem(["A", 2]).ambient_lattice()
            sage: sorted(L.rho().orbit())		# the output order is not specified
            [(1, 2, 0), (1, 0, 2), (2, 1, 0), (2, 0, 1), (0, 1, 2), (0, 2, 1)]

            sage: L = RootSystem(["A", 3]).weight_lattice()
            sage: len(L.rho().orbit())
            24
            sage: len(L.fundamental_weights()[1].orbit())
            4
            sage: len(L.fundamental_weights()[2].orbit())
            6
        """
        return [x for x in TransitiveIdeal(attrcall('simple_reflections'), [self])]

    ##########################################################################
    #
    ##########################################################################

    def associated_coroot(self):
        """
        Returns the coroot associated to this root.

        EXAMPLES::

            sage: alpha = RootSystem(["A", 3]).root_space().simple_roots()
            sage: alpha[1].associated_coroot()
            alphacheck[1]
        """
        #assert(self in self.parent().roots() is not False)
        f = self.parent().to_coroot_lattice_morphism()
        return (2/self.scalar(f(self)))*f(self);

    ##########################################################################
    # Descents
    ##########################################################################

    def has_descent(self, i, positive=False):
        """
        Test if self has a descent at position `i`, that is if self is
        on the strict negative side of the `i^{th}` simple reflection
        hyperplane.

        If positive if True, tests if it is on the strict positive
        side instead.

        EXAMPLES::

            sage: space=RootSystem(['A',5]).weight_space()
            sage: alpha=RootSystem(['A',5]).weight_space().simple_roots()
            sage: [alpha[i].has_descent(1) for i in space.index_set()]
            [False, True, False, False, False]
            sage: [(-alpha[i]).has_descent(1) for i in space.index_set()]
            [True, False, False, False, False]
            sage: [alpha[i].has_descent(1, True) for i in space.index_set()]
            [True, False, False, False, False]
            sage: [(-alpha[i]).has_descent(1, True) for i in space.index_set()]
            [False, True, False, False, False]
            sage: (alpha[1]+alpha[2]+alpha[4]).has_descent(3)
            True
            sage: (alpha[1]+alpha[2]+alpha[4]).has_descent(1)
            False
            sage: (alpha[1]+alpha[2]+alpha[4]).has_descent(1, True)
            True
        """
        s = self.scalar(self.parent().simple_coroots()[i])
        if positive:
            return s > 0
        else:
            return s < 0

    def first_descent(self, index_set=None, positive=False):
        """
        Returns the first descent of pt

        One can use the index_set option to restrict to the parabolic
        subgroup indexed by index_set.

        EXAMPLES::

            sage: space=RootSystem(['A',5]).weight_space()
            sage: alpha=space.simple_roots()
            sage: (alpha[1]+alpha[2]+alpha[4]).first_descent()
            3
            sage: (alpha[1]+alpha[2]+alpha[4]).first_descent([1,2,5])
            5
            sage: (alpha[1]+alpha[2]+alpha[4]).first_descent([1,2,5,3,4])
            5
        """
        if index_set == None:
            index_set = self.parent().index_set()
        for i in index_set:
            if self.has_descent(i, positive):
                return i
        return None

    def descents(self, index_set=None, positive=False):
        """
        Returns the descents of pt

        EXAMPLES::

            sage: space=RootSystem(['A',5]).weight_space()
            sage: alpha=space.simple_roots()
            sage: (alpha[1]+alpha[2]+alpha[4]).descents()
            [3, 5]
        """
        if index_set==None:
            index_set=self.parent().index_set()
        return [ i for i in index_set if self.has_descent(i, positive) ]

    def to_positive_chamber(self, index_set = None, positive = True):
        """
        Returns the unique element of the orbit of pt in the positive
        chamber.

        With the index_set optional parameter, this is done with
        respect to the corresponding parbolic subgroup

        With positive = False, returns the unique element in the
        negative chamber instead


        EXAMPLES::

            sage: space=RootSystem(['A',5]).weight_space()
            sage: alpha=RootSystem(['A',5]).weight_space().simple_roots()
            sage: alpha[1].to_positive_chamber()
            Lambda[1] + Lambda[5]
            sage: alpha[1].to_positive_chamber([1,2])
            Lambda[1] + Lambda[2] - Lambda[3]
        """
        if index_set is None:
            index_set=self.parent().index_set()
        while True:
            # The first index where it is *not* yet on the positive side
            i = self.first_descent(index_set, positive=(not positive))
            if i is None:
                return self
            else:
                self = self.simple_reflection(i)

    def reduced_word(self, index_set = None, positive = True):
        """
        Returns a shortest sequence of simple reflections mapping self
        to the unique element `o` of its orbit in the positive
        chamber. Alternatively this is a reduced word for the smallest
        element of the group mapping `o` to self (recall that, by
        convention, Weyl groups act on the left).

        With the index_set optional parameter, this is done with
        respect to the corresponding parabolic subgroup

        With positive = False, returns the shortest sequence to the
        negative chamber instead

        FIXME: better name?

        EXAMPLES::

            sage: space=RootSystem(['A',5]).weight_space()
            sage: alpha=RootSystem(['A',5]).weight_space().simple_roots()
            sage: alpha[1].reduced_word()
            [2, 3, 4, 5]
            sage: alpha[1].reduced_word([1,2])
            [2]
        """
        result = []
        if index_set is None:
            index_set=self.parent().index_set()
        while True:
            # The first index where it is *not* yet on the positive side
            i = self.first_descent(index_set, positive=(not positive))
            if i is None:
                return result
            else:
                self = self.simple_reflection(i)
                result.append(i)

    def is_dominant(self, index_set = None, positive = True):
        """
        Returns whether self is dominant.

        INPUT:

        - ``v`` - an element of the lattice

        EXAMPLES::

            sage: L = RootSystem(['A',2]).ambient_lattice()
            sage: Lambda = L.fundamental_weights()
            sage: [x.is_dominant() for x in Lambda]
            [True, True]
            sage: [x.is_dominant(positive=False) for x in Lambda]
            [False, False]
            sage: (Lambda[1]-Lambda[2]).is_dominant()
            False
            sage: (-Lambda[1]+Lambda[2]).is_dominant()
            False
            sage: (Lambda[1]-Lambda[2]).is_dominant([1])
            True
            sage: (Lambda[1]-Lambda[2]).is_dominant([2])
            False
            sage: [x.is_dominant() for x in L.roots()]
            [False, True, False, False, False, False]
            sage: [x.is_dominant(positive=False) for x in L.roots()]
            [False, False, False, False, True, False]
        """
        return self.first_descent(index_set, not positive) is None

    ##########################################################################
    # weak order
    ##########################################################################

    def succ(self):
        r"""
        Returns the immediate successors of self for the weak order

        EXAMPLES::

            sage: L = RootSystem(['A',3]).weight_lattice()
            sage: Lambda = L.fundamental_weights()
            sage: Lambda[1].succ()
            [-Lambda[1] + Lambda[2]]
            sage: L.rho().succ()
            [-Lambda[1] + 2*Lambda[2] + Lambda[3], 2*Lambda[1] - Lambda[2] + 2*Lambda[3], Lambda[1] + 2*Lambda[2] - Lambda[3]]
            sage: (-L.rho()).succ()
            []
       """
        return [ self.simple_reflection(i) for i in self.descents(positive=True) ]

    def pred(self):
        r"""
        Returns the immediate predecessors of self for the weak order

        EXAMPLES::

            sage: L = RootSystem(['A',3]).weight_lattice()
            sage: Lambda = L.fundamental_weights()
            sage: Lambda[1].pred()
            []
            sage: L.rho().pred()
            []
            sage: (-L.rho()).pred()
            [Lambda[1] - 2*Lambda[2] - Lambda[3], -2*Lambda[1] + Lambda[2] - 2*Lambda[3], -Lambda[1] - 2*Lambda[2] + Lambda[3]]
        """
        return [ self.simple_reflection(i) for i in self.descents() ]

    def greater(self):
        r"""
        Returns the elements in the orbit of self which are
        greater than self in the weak order.

        EXAMPLES::

            sage: L = RootSystem(['A',3]).ambient_lattice()
            sage: e = L.basis()
            sage: e[2].greater()
            [(0, 0, 1, 0), (0, 0, 0, 1)]
            sage: len(L.rho().greater())
            24
            sage: len((-L.rho()).greater())
            1
            sage: sorted([len(x.greater()) for x in L.rho().orbit()])
            [1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6, 8, 8, 8, 8, 12, 12, 12, 24]
        """
        return [x for x in TransitiveIdeal(attrcall('succ'), [self])]

    def smaller(self):
        r"""
        Returns the elements in the orbit of self which are
        smaller than self in the weak order.

        EXAMPLES::

            sage: L = RootSystem(['A',3]).ambient_lattice()
            sage: e = L.basis()
            sage: e[2].smaller()
            [(0, 0, 1, 0), (0, 1, 0, 0), (1, 0, 0, 0)]
            sage: len(L.rho().smaller())
            1
            sage: len((-L.rho()).smaller())
            24
            sage: sorted([len(x.smaller()) for x in L.rho().orbit()])
            [1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6, 8, 8, 8, 8, 12, 12, 12, 24]
        """
        return [x for x in TransitiveIdeal(attrcall('pred'), [self])]

    ##########################################################################
    # Level
    ##########################################################################

    def level(self):
        """
        EXAMPLES::

            sage: L = RootSystem(['A',2,1]).weight_lattice()
            sage: L.rho().level()
            3
        """
        assert(self.parent().cartan_type().is_affine())
        return self.scalar(self.parent().null_coroot())


    def translation(self, x):
        """
        INPUT:
         - ``self`` - an element `t` at level `0`
         - ``x`` - an element of the same space

        Returns `x` translated by `t`, that is `x+level(x) t`

        EXAMPLES::

            sage: L = RootSystem(['A',2,1]).weight_lattice()
            sage: alpha = L.simple_roots()
            sage: Lambda = L.fundamental_weights()
            sage: t = alpha[2]

        Let us look at the translation of an element of level `1`::

            sage: Lambda[1].level()
            1
            sage: t.translation(Lambda[1])
            -Lambda[0] + 2*Lambda[2]
            sage: Lambda[1] + t
            -Lambda[0] + 2*Lambda[2]

        and of an element of level `0`::

            sage: alpha [1].level()
            0
            sage: t.translation(alpha [1])
            -Lambda[0] + 2*Lambda[1] - Lambda[2]
            sage: alpha[1] + 0*t
            -Lambda[0] + 2*Lambda[1] - Lambda[2]

        The arguments are given in this seemingly unnatural order to
        make it easy to construct the translation function::

            sage: f = t.translation
            sage: f(Lambda[1])
            -Lambda[0] + 2*Lambda[2]
        """
        assert self.level().is_zero()
        return x + x.level() * self
