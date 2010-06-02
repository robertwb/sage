"""
Weyl Groups

AUTHORS:

- Daniel Bump (2008): initial version
- Mike Hansen (2008): initial version
- Anne Schilling (2008): initial version
- Nicolas Thiery (2008): initial version

EXAMPLES:

More examples on Weyl Groups should be added here...

The Cayley graph of the Weyl Group of type ['A', 3]::

    sage: w = WeylGroup(['A',3])
    sage: d = w.cayley_graph(); d
    Digraph on 24 vertices
    sage: d.show3d(color_by_label=True, edge_size=0.01, vertex_size=0.03)

The Cayley graph of the Weyl Group of type ['D', 4]::

    sage: w = WeylGroup(['D',4])
    sage: d = w.cayley_graph(); d
    Digraph on 192 vertices
    sage: d.show3d(color_by_label=True, edge_size=0.01, vertex_size=0.03) #long time (less than one minute)
"""
#*****************************************************************************
#       Copyright (C) 2008 Daniel Bump <bump at match.stanford.edu>,
#                          Mike Hansen <mhansen@gmail.com>
#                          Anne Schilling <anne at math.ucdavis.edu>
#                          Nicolas Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.groups.matrix_gps.matrix_group import MatrixGroup_gens
from sage.groups.matrix_gps.matrix_group_element import MatrixGroupElement
from sage.rings.all import ZZ, QQ
from sage.interfaces.gap import gap
#from sage.misc.cache import Cache
from sage.misc.cachefunc import cached_method, ClearCacheOnPickle
from sage.misc.lazy_attribute import lazy_attribute
from sage.misc.misc import deprecated_function_alias
from sage.combinat.root_system.cartan_type import CartanType
from sage.matrix.constructor import matrix, diagonal_matrix
from sage.combinat.root_system.root_lattice_realization import RootLatticeRealization
from sage.structure.unique_representation import UniqueRepresentation
from sage.categories.all import WeylGroups, FiniteWeylGroups, AffineWeylGroups
from sage.sets.family import Family
from sage.matrix.constructor import Matrix
from sage.graphs.graph import DiGraph

def WeylGroup(x, prefix=None):
    """
    Returns the Weyl group of type ct.

    INPUT:

    - ``ct`` - a Cartan Type.

    OPTIONAL:

    - ``prefix`` - changes the representation of elements from matrices
      to products of simple reflections

    EXAMPLES: The following constructions yield the same result, namely
    a weight lattice and its corresponding Weyl group::

        sage: G = WeylGroup(['F',4])
        sage: L = G.domain()

    or alternatively and equivalently::

        sage: L = RootSystem(['F',4]).ambient_space()
        sage: G = L.weyl_group()

    Either produces a weight lattice, with access to its roots and
    weights.

    ::

        sage: G = WeylGroup(['F',4])
        sage: G.order()
        1152
        sage: [s1,s2,s3,s4] = G.simple_reflections()
        sage: w = s1*s2*s3*s4; w
        [ 1/2  1/2  1/2  1/2]
        [-1/2  1/2  1/2 -1/2]
        [ 1/2  1/2 -1/2 -1/2]
        [ 1/2 -1/2  1/2 -1/2]
        sage: type(w) == G.element_class
        True
        sage: w.order()
        12
        sage: w.length() # length function on Weyl group
        4

    The default representation of Weyl group elements is as matrices.
    If you prefer, you may specify a prefix, in which case the
    elements are represented as products of simple reflections.

    ::

        sage: W=WeylGroup("C3",prefix="s")
        sage: [s1,s2,s3]=W.simple_reflections() # lets Sage parse its own output
        sage: s2*s1*s2*s3
        s1*s2*s3*s1
        sage: s2*s1*s2*s3 == s1*s2*s3*s1
        True
        sage: (s2*s3)^2==(s3*s2)^2
        True
        sage: (s1*s2*s3*s1).matrix()
        [ 0  0 -1]
        [ 0  1  0]
        [ 1  0  0]

    ::

        sage: L = G.domain()
        sage: fw = L.fundamental_weights(); fw
        Finite family {1: (1, 1, 0, 0), 2: (2, 1, 1, 0), 3: (3/2, 1/2, 1/2, 1/2), 4: (1, 0, 0, 0)}
        sage: rho = sum(fw); rho
        (11/2, 5/2, 3/2, 1/2)
        sage: w.action(rho) # action of G on weight lattice
        (5, -1, 3, 2)

    TESTS:
        sage: TestSuite(WeylGroup(["A",3])).run()
        sage: TestSuite(WeylGroup(["A",3, 1])).run()

        sage: W=WeylGroup(['A',3,1])
        sage: s=W.simple_reflections()
        sage: w=s[0]*s[1]*s[2]
        sage: w.reduced_word()
        [0, 1, 2]
        sage: w=s[0]*s[2]
        sage: w.reduced_word()
        [2, 0]
    """
    if isinstance(x, RootLatticeRealization):
        return WeylGroup_gens(x, prefix=prefix)

    ct = CartanType(x)
    if ct.is_affine():
        return WeylGroup_gens(ct.root_system().root_space(), prefix=prefix)
    else:
        return WeylGroup_gens(ct.root_system().ambient_space(), prefix=prefix)

class WeylGroup_gens(ClearCacheOnPickle, UniqueRepresentation, MatrixGroup_gens):
    @staticmethod
    def __classcall__(cls, domain, prefix=None):
        return super(WeylGroup_gens, cls).__classcall__(cls, domain, prefix)

    def __init__(self, domain, prefix):
        """
        EXAMPLES::

            sage: G = WeylGroup(['B',3])
            sage: TestSuite(G).run()
        """
        self._domain = domain
        if self.cartan_type().is_affine():
            category = AffineWeylGroups()
        elif self.cartan_type().is_finite():
            category = FiniteWeylGroups()
        else:
            category = WeylGroups()
        self.n = domain.dimension() # Really needed?
        # MatrixGroup_gens takes plain matrices as input. So we can't do:
        #MatrixGroup_gens.__init__(self, list(self.simple_reflections()))
        self._prefix = prefix
        MatrixGroup_gens.__init__(self, [self.morphism_matrix(self.domain().simple_reflection(i)) for i in self.index_set()], category = category)

    @cached_method
    def cartan_type(self):
        """
        Returns the CartanType associated to self.

        EXAMPLES::

            sage: G = WeylGroup(['F',4])
            sage: G.cartan_type()
            ['F', 4]
        """
        return self.domain().cartan_type()

    @cached_method
    def index_set(self):
        """
        Returns the index set of self.

        EXAMPLES::

            sage: G = WeylGroup(['F',4])
            sage: G.index_set()
            [1, 2, 3, 4]
            sage: G = WeylGroup(['A',3,1])
            sage: G.index_set()
            [0, 1, 2, 3]
        """
        return self.cartan_type().index_set()

    # Should be implemented in (morphisms of) modules with basis
    def morphism_matrix(self, f):
        return matrix(self.domain().base_ring(), [f(b).to_vector()
                           for b in self.domain().basis()]).transpose()

    def from_morphism(self, f):
        return self._element_constructor_(self.morphism_matrix(f))

    @cached_method
    def simple_reflections(self):
        """
        Returns the simple reflections of self, as a family.

        EXAMPLES:

        There are the simple reflections for the symmetric group::

            sage: W=WeylGroup(['A',2])
            sage: s = W.simple_reflections(); s
            Finite family {1: [0 1 0]
            [1 0 0]
            [0 0 1], 2: [1 0 0]
            [0 0 1]
            [0 1 0]}

        As a special feature, for finite irreducible root systems,
        s[0] gives the reflection along the highest root::

            sage: s[0]
            [0 0 1]
            [0 1 0]
            [1 0 0]

        We now look at some further examples::

            sage: W=WeylGroup(['A',2,1])
            sage: W.simple_reflections()
            Finite family {0: [-1  1  1]
            [ 0  1  0]
            [ 0  0  1], 1: [ 1  0  0]
            [ 1 -1  1]
            [ 0  0  1], 2: [ 1  0  0]
            [ 0  1  0]
            [ 1  1 -1]}
            sage: W = WeylGroup(['F',4])
            sage: [s1,s2,s3,s4] = W.simple_reflections()
            sage: w = s1*s2*s3*s4; w
            [ 1/2  1/2  1/2  1/2]
            [-1/2  1/2  1/2 -1/2]
            [ 1/2  1/2 -1/2 -1/2]
            [ 1/2 -1/2  1/2 -1/2]
            sage: s4^2 == W.unit()
            True
            sage: type(w) == W.element_class
            True

        """
        return self.domain().simple_reflections().map(self.from_morphism)

    def reflections(self):
        """
        The reflections of W are the conjugates of the simple reflections.
        They are in bijection with the positive roots, for given a positive
        root, we may have the reflection in the hyperplane orthogonal to it.
        This method returns a dictionary indexed by the reflections taking
        values in the positive roots. This requires self to be a finite
        Weyl group.

        EXAMPLES::

            sage: W = WeylGroup("B2",prefix="s")
            sage: refdict = W.reflections(); refdict
            Finite family {s1: (1, -1), s2*s1*s2: (1, 1), s1*s2*s1: (1, 0), s2: (0, 1)}
            sage: [refdict[r]+r.action(refdict[r]) for r in refdict.keys()]
            [(0, 0), (0, 0), (0, 0), (0, 0)]

        """
        ret = {}
        try:
            for alp in self.domain().positive_roots():
                r = self.__call__(Matrix([self.domain().reflection(alp)(x).to_vector() for x in self.domain().basis()]))
                ret[r] = alp
            return Family(ret)
        except:
            raise NotImplementedError, "reflections are only implemented for finite Weyl groups"

    def gens(self):
        """
        Returns the generators of self, i.e. the simple reflections.

        EXAMPLES::

            sage: G = WeylGroup(['A',3])
            sage: G.gens()
            [[0 1 0 0]
             [1 0 0 0]
             [0 0 1 0]
             [0 0 0 1],
             [1 0 0 0]
             [0 0 1 0]
             [0 1 0 0]
             [0 0 0 1],
             [1 0 0 0]
             [0 1 0 0]
             [0 0 0 1]
             [0 0 1 0]]
        """
        return list(self.simple_reflections())

    def __repr__(self):
        """
        EXAMPLES::

            sage: WeylGroup(['A', 1])
            Weyl Group of type ['A', 1] (as a matrix group acting on the ambient space)
            sage: WeylGroup(['A', 3, 1])
            Weyl Group of type ['A', 3, 1] (as a matrix group acting on the root space)
        """
        return "Weyl Group of type %s (as a matrix group acting on the %s)"%(self.cartan_type(),
                                                                           self._domain._name_string(capitalize=False,
                                                                                                      base_ring=False,
                                                                                                      type=False))


    def __call__(self, x):
        """
        EXAMPLES::

            sage: W = WeylGroup(['A',2])
            sage: W(1)
            [1 0 0]
            [0 1 0]
            [0 0 1]

        ::

            sage: W(2)
            Traceback (most recent call last):
            ...
            TypeError: no way to coerce element into self.

            sage: W2 = WeylGroup(['A',3])
            sage: W(1) in W2  # indirect doctest
            False

        """
        if isinstance(x, self.element_class) and x.parent() is self:
            return x
        from sage.matrix.matrix import is_Matrix
        if not (x in ZZ or is_Matrix(x)): # this should be handled by self.matrix_space()(x)
            raise TypeError, "no way to coerce element into self"
        M = self.matrix_space()(x)
        # This is really bad, especially for infinite groups!
        # TODO: compute the image of rho, compose by s_i until back in
        # the fundamental chamber. Return True iff the matrix is the identity
        g = self._element_constructor_(M)
        if not gap(g) in gap(self):
            raise TypeError, "no way to coerce element into self."
        return g

        # Here is a first attempt, which is not guaranteed to terminate
        # because g might map the simple roots all over the place.
        # we really need to do that with a single element of the fundamental chamber
        #while True:
        #    s = self.simple_reflections()
        #    i = g.first_descent()
        #    if i is None:
        #        if g == self.unit():
        #            return g
        #        else:
        #            raise TypeError, "no way to coerce element into self."
        #    g = g * s[i]


    #def list(self):
    #    """
    #    Returns a list of the elements of self.
    #
    #    EXAMPLES::
    #
    #        sage: G = WeylGroup(['A',1])
    #        sage: G.list()
    #        [[0 1]
    #         [1 0], [1 0]
    #         [0 1]]
    #    """
    #    return [self._element_constructor_(a._matrix_(QQ)) for a in self._gap_().Elements()]
    def list(self):
        """
        Returns a list of the elements of self.

        EXAMPLES::

            sage: G = WeylGroup(['A',1])
            sage: G.list()
            [[1 0]
             [0 1], [0 1]
             [1 0]]

        This overrides the implementation of MatrixGroup_gap.
        Those seem typical timings (without the overriding):

        #   sage: W = WeylGroup(["C",4])

        #   sage: %time  len(W.list())
            CPU times: user 7.63 s, sys: 0.60 s, total: 8.22 s
            Wall time: 8.63 s

        #    sage: %time  len([ x for x in W])
            CPU times: user 3.23 s, sys: 0.09 s, total: 3.32 s
            Wall time: 3.34 s

        #    sage: %time  len(list(W))
            CPU times: user 3.26 s, sys: 0.02 s, total: 3.28 s
            Wall time: 3.29 s

        """
        return self._list_from_iterator()

    def character_table(self):
        """
        Returns the GAP character table as a string. For larger tables you
        may preface this with a command such as
        gap.eval("SizeScreen([120,40])") in order to widen the screen.

        EXAMPLES::

            sage: print WeylGroup(['A',3]).character_table()
            CT1
            <BLANKLINE>
                 2  3  2  2  .  3
                 3  1  .  .  1  .
            <BLANKLINE>
                   1a 4a 2a 3a 2b
            <BLANKLINE>
            X.1     1 -1 -1  1  1
            X.2     3  1 -1  . -1
            X.3     2  .  . -1  2
            X.4     3 -1  1  . -1
            X.5     1  1  1  1  1
        """
        return gap.eval("Display(CharacterTable(%s))"%gap(self).name())

    @cached_method
    def one(self):
        """
        Returns the unit element of the Weyl group

        EXAMPLES::
            sage: W = WeylGroup(['A',3])
            sage: e = W.unit(); e
            [1 0 0 0]
            [0 1 0 0]
            [0 0 1 0]
            [0 0 0 1]
            sage: type(e) == W.element_class
            True
        """
        return self._element_constructor_(matrix(QQ,self.n,self.n,1))

    unit = one # For backward compatibility

    def domain(self):
        """
        Returns the domain of the element of ``self``, that is the
        root lattice realization on which they act.

        EXAMPLES::

            sage: G = WeylGroup(['F',4])
            sage: G.domain()
            Ambient space of the Root system of type ['F', 4]
	    sage: G = WeylGroup(['A',3,1])
	    sage: G.domain()
	    Root space over the Rational Field of the Root system of type ['A', 3, 1]

        This method used to be called ``lattice``:

            sage: G.lattice()
            doctest:...: DeprecationWarning: (Since Sage Version 4.3.4) lattice is deprecated. Please use domain instead.
            Root space over the Rational Field of the Root system of type ['A', 3, 1]
        """
        return self._domain

    lattice = deprecated_function_alias(domain, 'Sage Version 4.3.4')

    def simple_reflection(self, i):
        """
        Returns the `i^{th}` simple reflection.

        EXAMPLES::

            sage: G = WeylGroup(['F',4])
            sage: G.simple_reflection(1)
            [1 0 0 0]
            [0 0 1 0]
            [0 1 0 0]
            [0 0 0 1]
            sage: W=WeylGroup(['A',2,1])
            sage: W.simple_reflection(1)
            [ 1  0  0]
            [ 1 -1  1]
            [ 0  0  1]
        """
        if i not in self.index_set():
            raise ValueError, "i must be in the index set"
	return self.simple_reflections()[i]

    def long_element_hardcoded(self):
        """
        Returns the long Weyl group element (hardcoded data)

        Do we really want to keep it? There is a generic
        implementation which works in all cases. The hardcoded should
        have a better complexity (for large classical types), but
        there is a cache, so does this really matter?

        EXAMPLES::

            sage: types = [ ['A',5],['B',3],['C',3],['D',4],['G',2],['F',4],['E',6] ]
            sage: [WeylGroup(t).long_element().length() for t in types]
            [15, 9, 9, 12, 6, 24, 36]
            sage: all( WeylGroup(t).long_element() == WeylGroup(t).long_element_hardcoded() for t in types )
            True
        """
        type = self.cartan_type()
        if type[0] == 'D' and type[1]%2 == 1:
            l = [-1 for i in range(self.n-1)]
            l.append(1)
            m = diagonal_matrix(QQ,l)
        elif type[0] == 'A':
            l = [0 for k in range((self.n)**2)]
            for k in range(self.n-1, (self.n)**2-1, self.n-1):
                l[k] = 1
            m = matrix(QQ, self.n, l)
        elif type[0] == 'E':
            if type[1] == 6:
                half = ZZ(1)/ZZ(2)
                l = [[-half, -half, -half, half, 0, 0, 0, 0],
                     [-half, -half, half, -half, 0, 0, 0, 0],
                     [-half, half, -half, -half, 0, 0, 0, 0],
                     [half, -half, -half, -half, 0, 0, 0, 0],
                     [0, 0, 0, 0, half, half, half, -half],
                     [0, 0, 0, 0, half, half, -half, half],
                     [0, 0, 0, 0, half, -half, half, half],
                     [0, 0, 0, 0, -half, half, half, half]]
                m = matrix(QQ, 8, l)
            else:
                raise NotImplementedError, "Not implemented yet for this type"
        elif type[0] == 'G':
            third = ZZ(1)/ZZ(3)
            twothirds = ZZ(2)/ZZ(3)
            l = [[-third, twothirds, twothirds],
                 [twothirds, -third, twothirds],
                 [twothirds, twothirds, -third]]
            m = matrix(QQ, 3, l)
        else:
            m = diagonal_matrix([-1 for i in range(self.n)])
        return self.__call__(m)

    def __cmp__(self, other):
        """
        TESTS::

            sage: G1 = WeylGroup(CartanType(['A',2]))
            sage: G2 = WeylGroup(CartanType(['A',2]))
            sage: G1 == G2
            True
        """
        if self.__class__ != other.__class__:
            return cmp(self.__class__, other.__class__)
        if self.cartan_type() != other.cartan_type():
            return cmp(self.cartan_type(), other.cartan_type())
        return 0

    def classical(self):
        """
        If self is a Weyl group from an affine Cartan Type, this give
        the classical parabolic subgroup of self.

        Caveat: we assume that 0 is a special node of the Dynkin diagram

        TODO: extract parabolic subgroup method
        """
        assert(self.cartan_type().is_affine())
        return ClassicalWeylSubgroup(self._domain, prefix=self._prefix)

    def bruhat_graph(self, x, y):
        """
        The Bruhat graph Gamma(x,y), defined if x <= y in the Bruhat order, has
        as its vertices the Bruhat interval, {t | x <= t <= y}, and as its
        edges the pairs u, v such that u = r.v where r is a reflection, that
        is, a conjugate of a simple reflection.

        Returns the Bruhat graph as a directed graph, with an edge u --> v
        if and only if u < v in the Bruhat order, and u = r.v.

        See:

        Carrell, The Bruhat graph of a Coxeter group, a conjecture of Deodhar, and
        rational smoothness of Schubert varieties. Algebraic groups and their
        generalizations: classical methods (University Park, PA, 1991), 53--61,
        Proc. Sympos. Pure Math., 56, Part 1, Amer. Math. Soc., Providence, RI, 1994.

        EXAMPLES:

            sage: W = WeylGroup("A3", prefix = "s")
            sage: [s1,s2,s3] = W.simple_reflections()
            sage: W.bruhat_graph(s1*s3,s1*s2*s3*s2*s1)
            Digraph on 10 vertices
        """
        g = self.bruhat_interval(x, y)
        ref = self.reflections()
        d = {}
        for x in g:
            d[x] = [y for y in g if x.length() < y.length() and ref.has_key(x*y.inverse())]
        return DiGraph(d)


class ClassicalWeylSubgroup(WeylGroup_gens):
    """
    A class for Classical Weyl Subgroup of a Weyl Group

    EXAMPLES::

        sage: G = WeylGroup(["A",3,1]).classical()
        sage: G
        Parabolic Subgroup of the Weyl Group of type ['A', 3, 1] (as a matrix group acting on the root space)
        sage: G.category()
        Category of finite weyl groups
        sage: G.cardinality()
        24
        sage: TestSuite(G).run()

    TESTS::

        sage: from sage.combinat.root_system.weyl_group import ClassicalWeylSubgroup
        sage: H = ClassicalWeylSubgroup(RootSystem(["A", 3, 1]).root_space(), prefix=None)
        sage: H is G
        True

    Caveat: the interface is likely to change. The current main
    application is for plots.

    TODO: implement:
     - Parabolic subrootsystems
     - Parabolic subgroups with a set of nodes as argument
    """

    @cached_method
    def cartan_type(self):
        """
        EXAMPLES::

            sage: WeylGroup(['A',3,1]).classical().cartan_type()
            ['A', 3]
            sage: WeylGroup(['A',3,1]).classical().index_set()
            [1, 2, 3]

        Note: won't be needed, once the lattice will be a parabolic sub root system
        """
        return self.domain().cartan_type().classical()

    def simple_reflections(self):
        """
        EXAMPLES::

            sage: WeylGroup(['A',2,1]).classical().simple_reflections()
            Finite family {1: [ 1  0  0]
                              [ 1 -1  1]
                              [ 0  0  1],
                           2: [ 1  0  0]
                              [ 0  1  0]
                              [ 1  1 -1]}

        Note: won't be needed, once the lattice will be a parabolic sub root system
        """
        return Family(dict((i, self.from_morphism(self.domain().simple_reflection(i))) for i in self.index_set()))

    def __repr__(self):
        """
        EXAMPLES::

            sage: WeylGroup(['A',2,1]).classical()
            Parabolic Subgroup of the Weyl Group of type ['A', 2, 1] (as a matrix group acting on the root space)
            sage: WeylGroup(['C',4,1]).classical()
            Parabolic Subgroup of the Weyl Group of type ['C', 4, 1] (as a matrix group acting on the root space)
            sage: RootSystem(['C',3,1]).coweight_lattice().weyl_group().classical()
            Parabolic Subgroup of the Weyl Group of type ['C', 3, 1]^* (as a matrix group acting on the coweight lattice)
            sage: RootSystem(['C',4,1]).coweight_lattice().weyl_group().classical()
            Parabolic Subgroup of the Weyl Group of type ['C', 4, 1]^* (as a matrix group acting on the coweight lattice)
        """
        return "Parabolic Subgroup of the Weyl Group of type %s (as a matrix group acting on the %s)"%(self.domain().cartan_type(),
                                                                           self._domain._name_string(capitalize=False,
                                                                                                      base_ring=False,
                                                                                                      type=False))
    def weyl_group(self, prefix="hereditary"):
        """
        Return the Weyl group associated to the parabolic subgroup.

        EXAMPLES::

            sage: WeylGroup(['A',4,1]).classical().weyl_group()
            Weyl Group of type ['A', 4, 1] (as a matrix group acting on the root space)
            sage: WeylGroup(['C',4,1]).classical().weyl_group()
            Weyl Group of type ['C', 4, 1] (as a matrix group acting on the root space)
            sage: WeylGroup(['E',8,1]).classical().weyl_group()
            Weyl Group of type ['E', 8, 1] (as a matrix group acting on the root space)
        """
        if prefix == "hereditary":
            prefix = self._prefix
        return self.domain().weyl_group(prefix)

    def _test_is_finite(self, **options):
        """
        Tests some internal invariants

        EXAMPLES::

            sage: WeylGroup(['A', 2, 1]).classical()._test_is_finite()
            sage: WeylGroup(['B', 3, 1]).classical()._test_is_finite()
        """
        tester = self._tester(**options)
        assert(not self.weyl_group(self._prefix).is_finite())
        assert(self.is_finite())

class WeylGroupElement(MatrixGroupElement):
    """
    Class for a Weyl Group elements
    """
    def __init__(self, g, parent):
        """
        EXAMPLES::

            sage: G = WeylGroup(['A',2])
            sage: s1 = G.simple_reflection(1)
            sage: TestSuite(s1).run()
        """
        MatrixGroupElement.__init__(self, g, parent)
        self.__matrix = self._MatrixGroupElement__mat
        self.__matrix.set_immutable()
        self._parent = parent

    def __hash__(self):
        return hash(self.__matrix)

    def domain(self):
        """
        Returns the ambient lattice associated with self.

        EXAMPLES::

            sage: W = WeylGroup(['A',2])
            sage: s1 = W.simple_reflection(1)
            sage: s1.domain()
            Ambient space of the Root system of type ['A', 2]
        """
        return self._parent.domain()

    def __repr__(self):
        """
        EXAMPLES::

            sage: W = WeylGroup(['A',2,1], prefix="s")
            sage: [s0,s1,s2]=W.simple_reflections()
            sage: s0*s1
            s0*s1
            sage: W = WeylGroup(['A',2,1])
            sage: [s0,s1,s2]=W.simple_reflections()
            sage: s0*s1
            [ 0 -1  2]
            [ 1 -1  1]
            [ 0  0  1]
        """
        if self._parent._prefix is None:
            return MatrixGroupElement.__repr__(self)
        else:
            redword = self.reduced_word()
            if len(redword) == 0:
                return "1"
            else:
                ret = ""
                for i in redword[:-1]:
                    ret += "%s%d*"%(self._parent._prefix, i)
            return ret + "%s%d"%(self._parent._prefix, redword[-1])

    def matrix(self):
        """
        Returns self as a matrix.

        EXAMPLES::

            sage: W = WeylGroup(['A',2])
            sage: s1 = W.simple_reflection(1)
            sage: m = s1.matrix(); m
            [0 1 0]
            [1 0 0]
            [0 0 1]
            sage: m.parent()
            Full MatrixSpace of 3 by 3 dense matrices over Rational Field
        """
        return self.__matrix

    def __eq__(self, other):
        """
        EXAMPLES::

            sage: W = WeylGroup(['A',3])
            sage: s = W.simple_reflections()
            sage: s[1] == s[1]
            True
            sage: s[1] == s[2]
            False

        Note: this implementation of :meth:`__eq__` is not much faster
        than :meth:`__cmp__`. But it turned out to be useful for
        subclasses overriding __cmp__ with something slow for specific
        purposes.
        """
        return self.__class__ == other.__class__ and \
               self._parent   == other._parent   and \
               self.__matrix  == other.__matrix

    def __cmp__(self, other):
        """
        EXAMPLES::

            sage: W = WeylGroup(['A',3])
            sage: s = W.simple_reflections()
            sage: s[1] == s[1]
            True
            sage: s[1] == s[2]
            False
        """
        if self.__class__ != other.__class__:
            return cmp(self.__class__, other.__class__)
        if self._parent.cartan_type() != other._parent.cartan_type():
            return cmp(self._parent.cartan_type(), other._parent.cartan_type())
        return cmp(self.matrix(), other.matrix())

    def parent(self):
        """
        Returns self's parent.

        EXAMPLES::

            sage: W = WeylGroup(['A',2])
            sage: s = W.simple_reflections()
            sage: s[1].parent()
            Weyl Group of type ['A', 2] (as a matrix group acting on the ambient space)
        """
        return self._parent

    def _mul_(self, other):
        """
        EXAMPLES::

            sage: W = WeylGroup(['A',2])
            sage: s = W.simple_reflections()
            sage: s[1]*s[1]
            [1 0 0]
            [0 1 0]
            [0 0 1]
        """
        return self.parent()._element_constructor_(self.__matrix * other.__matrix)

    def inverse(self):
        """
        Returns the inverse of self.

        EXAMPLES::

            sage: W = WeylGroup(['A',2])
            sage: w = W.unit()
            sage: w = w.inverse()
            sage: type(w.inverse()) == W.element_class
            True
            sage: W=WeylGroup(['A',2])
            sage: w=W.from_reduced_word([2,1])
            sage: w.inverse().reduced_word()
            [1, 2]
            sage: ~w == w.inverse()
            True
        """
        return self.parent()._element_constructor_(self.matrix().inverse())

    __invert__ = inverse

    def action(self, v):
        """
        Returns the action of self on the vector v.

        EXAMPLES::
            sage: W = WeylGroup(['A',2])
            sage: s = W.simple_reflections()
            sage: v = W.domain()([1,0,0])
            sage: s[1].action(v)
            (0, 1, 0)

            sage: W = WeylGroup(RootSystem(['A',2]).root_lattice())
            sage: s = W.simple_reflections()
            sage: alpha = W.domain().simple_roots()
            sage: s[1].action(alpha[1])
            -alpha[1]

            sage: W=WeylGroup(['A',2,1])
            sage: alpha = W.domain().simple_roots()
            sage: s = W.simple_reflections()
            sage: s[1].action(alpha[1])
            -alpha[1]
            sage: s[1].action(alpha[0])
            alpha[0] + alpha[1]
        """
        assert(v in self.domain())
        return self.domain().from_vector(self.__matrix*v.to_vector())


    ##########################################################################
    # Descents
    ##########################################################################

    def has_descent(self, i, positive=False, side = "right"):
        """
        Tests if self has a descent at position `i`, that is if self is
        on the strict negative side of the `i^{th}` simple reflection
        hyperplane.

        If positive is True, tests if it is on the strict positive
        side instead.

        EXAMPLES::

            sage: W = WeylGroup(['A',3])
            sage: s = W.simple_reflections()
            sage: [W.unit().has_descent(i) for i in W.domain().index_set()]
            [False, False, False]
            sage: [s[1].has_descent(i) for i in W.domain().index_set()]
            [True, False, False]
            sage: [s[2].has_descent(i) for i in W.domain().index_set()]
            [False, True, False]
            sage: [s[3].has_descent(i) for i in W.domain().index_set()]
            [False, False, True]
            sage: [s[3].has_descent(i, True) for i in W.domain().index_set()]
            [True, True, False]
            sage: W = WeylGroup(['A',3,1])
            sage: s = W.simple_reflections()
            sage: [W.one().has_descent(i) for i in W.domain().index_set()]
            [False, False, False, False]
            sage: [s[0].has_descent(i) for i in W.domain().index_set()]
            [True, False, False, False]
            sage: w = s[0] * s[1]
            sage: [w.has_descent(i) for i in W.domain().index_set()]
            [False, True, False, False]
            sage: [w.has_descent(i, side = "left") for i in W.domain().index_set()]
            [True, False, False, False]
            sage: w = s[0] * s[2]
            sage: [w.has_descent(i) for i in W.domain().index_set()]
            [True, False, True, False]
            sage: [w.has_descent(i, side = "left") for i in W.domain().index_set()]
            [True, False, True, False]

            sage: W = WeylGroup(['A',3])
            sage: W.one().has_descent(0)
            True
            sage: W.w0.has_descent(0)
            False
        """
#        s=self.parent().lattice().rho().scalar(self.action(self.parent().lattice().simple_root(i)))
#        if positive:
#            return s > 0
#        else:
#            return s < 0
        L = self.domain()
        # Choose the method depending on the side and the availability of rho and is_positive_root
        if not hasattr(L.element_class, "is_positive_root"):
            use_rho = True
        elif not hasattr(L, "rho"):
            use_rho = False
        else:
            use_rho = side == "left"

        if use_rho is not (side == "left"):
            self = ~self

        if use_rho:
            s = self.action(L.rho()   ).scalar(L.alphacheck()[i]) >= 0
        else:
            s = self.action(L.alpha()[i]).is_positive_root()

        return s is positive

    def apply_simple_reflection(self, i, side = "right"):
        s = self.parent().simple_reflections()
        if side == "right":
            return self * s[i]
        else:
            return s[i] * self

# The methods first_descent, descents, reduced_word appear almost verbatim in
# root_lattice_realization and need to be factored out!

    def to_permutation(self):
        """
        A first approximation of to_permutation ...

        This assumes types A,B,C,D on the ambient lattice

        This further assume that the basis is indexed by 0,1,...
        and returns a permutation of (5,4,2,3,1) (beuargl), as a tuple
        """
        W = self.parent()
        e = W.domain().basis()
        return tuple( c*(j+1)
                      for i in e.keys()
                      for (j,c) in self.action(e[i]) )

    def to_permutation_string(self):
        """
        EXAMPLES::
            sage: W = WeylGroup(["A",3])
            sage: s = W.simple_reflections()
            sage: (s[1]*s[2]*s[3]).to_permutation_string()
            '2341'

        """
        return "".join(str(i) for i in self.to_permutation())

WeylGroup_gens.Element = WeylGroupElement
