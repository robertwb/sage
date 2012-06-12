r"""
"Named" Permutation groups (such as the symmetric group, S_n)

You can construct the following permutation groups:

-- SymmetricGroup, $S_n$ of order $n!$ (n can also be a list $X$ of distinct
                   positive integers, in which case it returns $S_X$)

-- AlternatingGroup, $A_n$ or order $n!/2$ (n can also be a list $X$
                   of distinct positive integers, in which case it returns
                   $A_X$)

-- DihedralGroup, $D_n$ of order $2n$

-- CyclicPermutationGroup, $C_n$ of order $n$

-- DiCyclicGroup, nonabelian groups of order `4m` with a unique element of order 2

-- TransitiveGroup, $n^{th}$ transitive group of degree $d$
                      from the GAP tables of transitive groups (requires
                      the "optional" package database_gap)

-- TransitiveGroups(d), TransitiveGroups(), set of all of the above

-- MathieuGroup(degree), Mathieu group of degree 9, 10, 11, 12, 21, 22, 23, or 24.

-- KleinFourGroup, subgroup of $S_4$ of order $4$ which is not $C_2 \times C_2$

-- QuaternionGroup, non-abelian group of order `8`, `\{\pm 1, \pm I, \pm J, \pm K\}`

-- PGL(n,q), projective general linear group of $n\times n$ matrices over
             the finite field GF(q)

-- PSL(n,q), projective special linear group of $n\times n$ matrices over
             the finite field GF(q)

-- PSp(2n,q), projective symplectic linear group of $2n\times 2n$ matrices
              over the finite field GF(q)

-- PSU(n,q), projective special unitary group of $n \times n$ matrices having
             coefficients in the finite field $GF(q^2)$ that respect a
             fixed nondegenerate sesquilinear form, of determinant 1.

-- PGU(n,q), projective general unitary group of $n\times n$ matrices having
             coefficients in the finite field $GF(q^2)$ that respect a
             fixed nondegenerate sesquilinear form, modulo the centre.

-- SuzukiGroup(q), Suzuki group over GF(q), $^2 B_2(2^{2k+1}) = Sz(2^{2k+1})$.


AUTHOR:
    - David Joyner (2007-06): split from permgp.py (suggested by Nick Alexander)

REFERENCES:
    Cameron, P., Permutation Groups. New York: Cambridge University Press, 1999.
    Wielandt, H., Finite Permutation Groups. New York: Academic Press, 1964.
    Dixon, J. and Mortimer, B., Permutation Groups, Springer-Verlag, Berlin/New York, 1996.

NOTE:
    Though Suzuki groups are okay, Ree groups should *not* be wrapped as
    permutation groups - the construction is too slow - unless (for
    small values or the parameter) they are made using explicit generators.
"""

#*****************************************************************************
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#                          David Joyner <wdjoyner@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.rings.all      import Integer
from sage.interfaces.all import gap
from sage.rings.finite_rings.constructor import FiniteField as GF
from sage.rings.arith import factor
from sage.rings.integer_ring import ZZ
from sage.groups.abelian_gps.abelian_group import AbelianGroup
from sage.misc.functional import is_even
from sage.misc.cachefunc import cached_method
from sage.misc.misc import deprecated_function_alias
from sage.groups.perm_gps.permgroup import PermutationGroup_generic
from sage.groups.perm_gps.permgroup_element import PermutationGroupElement
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from sage.sets.finite_enumerated_set import FiniteEnumeratedSet
from sage.sets.disjoint_union_enumerated_sets import DisjointUnionEnumeratedSets
from sage.categories.enumerated_sets import EnumeratedSets
from sage.sets.non_negative_integers import NonNegativeIntegers
from sage.sets.family import Family

class PermutationGroup_unique(UniqueRepresentation, PermutationGroup_generic):
    @staticmethod
    def __classcall__(cls, *args, **kwds):
        """
        This makes sure that domain is a FiniteEnumeratedSet before it gets passed
        on to the __init__ method.

        EXAMPLES::

            sage: SymmetricGroup(['a','b']).domain() #indirect doctest
            {'a', 'b'}
        """
        domain = kwds.pop('domain', None)
        if domain is not None:
            if domain not in FiniteEnumeratedSets():
                domain = FiniteEnumeratedSet(domain)
            kwds['domain'] = domain
        return super(PermutationGroup_unique, cls).__classcall__(cls, *args, **kwds)

    def __eq__(self, other):
        """
        Overrides the default equality testing provided by
        UniqueRepresentation by forcing a call to :meth:.`__cmp__`.

        EXAMPLES::

            sage: G = SymmetricGroup(6)
            sage: G3 = G.subgroup([G((1,2,3,4,5,6)),G((1,2))])
            sage: G == G3
            True
        """
        return self.__cmp__(other) == 0


class PermutationGroup_symalt(PermutationGroup_unique):
    """
    This is a class used to factor out some of the commonality
    in the SymmetricGroup and AlternatingGroup classes.
    """

    @staticmethod
    def __classcall__(cls, domain):
        """
        Normalizes the input of the constructor into a set

        INPUT:

         - ``n`` - an integer or list or tuple thereof

        Calls the constructor with a tuple representing the set.

        EXAMPLES::

            sage: S1 = SymmetricGroup(4)
            sage: S2 = SymmetricGroup([1,2,3,4])
            sage: S3 = SymmetricGroup((1,2,3,4))
            sage: S1 is S2
            True
            sage: S1 is S3
            True

        TESTS::

            sage: SymmetricGroup(0)
            Symmetric group of order 0! as a permutation group
            sage: SymmetricGroup(1)
            Symmetric group of order 1! as a permutation group
            sage: SymmetricGroup(-1)
            Traceback (most recent call last):
            ...
            ValueError: domain (=-1) must be an integer >= 0 or a list
        """
        if domain not in FiniteEnumeratedSets():
            if not isinstance(domain, (tuple, list)):
                try:
                    domain = Integer(domain)
                except TypeError:
                    raise ValueError, "domain (=%s) must be an integer >= 0 or a finite set (but domain has type %s)"%(domain,type(domain))

                if domain < 0:
                    raise ValueError, "domain (=%s) must be an integer >= 0 or a list"%domain
                else:
                    domain = range(1, domain+1)
            v = FiniteEnumeratedSet(domain)
        else:
            v = domain

        return super(PermutationGroup_symalt, cls).__classcall__(cls, domain=v)

    set = deprecated_function_alias(PermutationGroup_generic.domain, 'Sage Version 4.7.1')

class SymmetricGroup(PermutationGroup_symalt):
    def __init__(self, domain=None):
        """
        The full symmetric group of order $n!$, as a permutation group.
        If n is a list or tuple of positive integers then it returns the
        symmetric group of the associated set.

        INPUT:

         - ``n`` - a positive integer, or list or tuple thereof

        EXAMPLES::

            sage: G = SymmetricGroup(8)
            sage: G.order()
            40320
            sage: G
            Symmetric group of order 8! as a permutation group
            sage: G.degree()
            8
            sage: S8 = SymmetricGroup(8)
            sage: G = SymmetricGroup([1,2,4,5])
            sage: G
            Symmetric group of order 4! as a permutation group
            sage: G.domain()
            {1, 2, 4, 5}
            sage: G = SymmetricGroup(4)
            sage: G
            Symmetric group of order 4! as a permutation group
            sage: G.domain()
            {1, 2, 3, 4}
            sage: G.category()
            Join of Category of finite permutation groups and Category of finite weyl groups
            sage: TestSuite(G).run()

        TESTS::

            sage: TestSuite(SymmetricGroup(0)).run()
        """
        from sage.categories.finite_weyl_groups import FiniteWeylGroups
        from sage.categories.finite_permutation_groups import FinitePermutationGroups
        from sage.categories.category import Category

        #Note that we skip the call to the superclass initializer in order to
        #avoid infinite recursion since SymmetricGroup is called by
        #PermutationGroupElement
        super(PermutationGroup_generic, self).__init__(category = Category.join([FinitePermutationGroups(), FiniteWeylGroups()]))

        self._domain = domain
        self._deg = len(self._domain)
        self._domain_to_gap = dict((key, i+1) for i, key in enumerate(self._domain))
        self._domain_from_gap = dict((i+1, key) for i, key in enumerate(self._domain))

        #Create the generators for the symmetric group
        gens = [ tuple(self._domain) ]
        if len(self._domain) > 2:
            gens.append( tuple(self._domain[:2]) )
        self._gens = [PermutationGroupElement(g, self, check=False) for g in gens]


    def _gap_init_(self, gap=None):
        """
        Returns the string used to create this group in GAP.

        EXAMPLES::

            sage: S = SymmetricGroup(3)
            sage: S._gap_init_()
            'SymmetricGroup(3)'
            sage: S = SymmetricGroup(['a', 'b', 'c'])
            sage: S._gap_init_()
            'SymmetricGroup(3)'
        """
        return 'SymmetricGroup(%s)'%self.degree()

    @cached_method
    def index_set(self):
        """
        Indexing sets of descent of the symmetric group.

        EXAMPLES::

            sage: S8 = SymmetricGroup(8)
            sage: S8.index_set()
            [1, 2, 3, 4, 5, 6, 7]

            sage: S = SymmetricGroup([3,1,4,5])
            sage: S.index_set()
            [3, 1, 4]
        """
        return self.domain()[:-1]

    def __cmp__(self, x):
        """
        Fast comparison for SymmetricGroups.

        EXAMPLES:
            sage: S8 = SymmetricGroup(8)
            sage: S3 = SymmetricGroup(3)
            sage: S8 > S3
            True
        """
        if isinstance(x, SymmetricGroup):
            return cmp((self._deg, self._domain), (x._deg, x._domain))
        else:
            return PermutationGroup_generic.__cmp__(self, x)

    def _repr_(self):
        """
        EXAMPLES:
            sage: A = SymmetricGroup([2,3,7]); A
            Symmetric group of order 3! as a permutation group
        """
        return "Symmetric group of order %s! as a permutation group"%self.degree()

    def simple_reflection(self, i):
        """
        For `i` in the index set of ``self``, this returns the
        elementary transposition `s_i=(i,i+1)`.

        EXAMPLES::

            sage: A = SymmetricGroup(5)
            sage: A.simple_reflection(3)
            (3,4)

            sage: A = SymmetricGroup([2,3,7])
            sage: A.simple_reflections()
            Finite family {2: (2,3), 3: (3,7)}
        """
        return self([(i, self._domain[self._domain.index(i)+1])], check=False)

    def major_index(self, parameter=None):
        r"""
        Returns the *major index generating polynomial* of ``self``,
        which is a gadget counting the elements of ``self`` by major
        index.

        INPUT:

        - ``parameter`` - an element of a ring. The result is
          more explicit with a formal variable.  (default:
          element q of Univariate Polynomial Ring in q over
          Integer Ring)

        .. math::

            P(q) = \sum_{g\in S_n} q^{ \operatorname{major\ index}(g) }

        EXAMPLES::

            sage: S4 = SymmetricGroup(4)
            sage: S4.major_index()
            q^6 + 3*q^5 + 5*q^4 + 6*q^3 + 5*q^2 + 3*q + 1
            sage: K.<t> = QQ[]
            sage: S4.major_index(t)
            t^6 + 3*t^5 + 5*t^4 + 6*t^3 + 5*t^2 + 3*t + 1
        """
        from sage.combinat.q_analogues import q_factorial
        return q_factorial(self.degree(), parameter)

class AlternatingGroup(PermutationGroup_symalt):
    def __init__(self, domain=None):
        """
        The alternating group of order $n!/2$, as a permutation group.

        INPUT:

            ``n`` -- a positive integer, or list or tuple thereof

        EXAMPLES::

            sage: G = AlternatingGroup(6)
            sage: G.order()
            360
            sage: G
            Alternating group of order 6!/2 as a permutation group
            sage: G.category()
            Category of finite permutation groups
            sage: TestSuite(G).run()

            sage: G = AlternatingGroup([1,2,4,5])
            sage: G
            Alternating group of order 4!/2 as a permutation group
            sage: G.domain()
            {1, 2, 4, 5}
            sage: G.category()
            Category of finite permutation groups
            sage: TestSuite(G).run()
        """
        PermutationGroup_symalt.__init__(self, gap_group='AlternatingGroup(%s)'%len(domain), domain=domain)

    def _repr_(self):
        """
        EXAMPLES:
            sage: A = AlternatingGroup([2,3,7]); A
            Alternating group of order 3!/2 as a permutation group
        """
        return "Alternating group of order %s!/2 as a permutation group"%self.degree()

    def _gap_init_(self, gap=None):
        """
        Returns the string used to create this group in GAP.

        EXAMPLES::

            sage: A = AlternatingGroup(3)
            sage: A._gap_init_()
            'AlternatingGroup(3)'
            sage: A = AlternatingGroup(['a', 'b', 'c'])
            sage: A._gap_init_()
            'AlternatingGroup(3)'
        """
        return 'AlternatingGroup(%s)'%(self.degree())

class CyclicPermutationGroup(PermutationGroup_unique):
    def __init__(self, n):
        """
        A cyclic group of order n, as a permutation group.

        INPUT:
            n -- a positive integer

        EXAMPLES::

            sage: G = CyclicPermutationGroup(8)
            sage: G.order()
            8
            sage: G
            Cyclic group of order 8 as a permutation group
            sage: G.category()
            Category of finite permutation groups
            sage: TestSuite(G).run()
            sage: C = CyclicPermutationGroup(10)
            sage: C.is_abelian()
            True
            sage: C = CyclicPermutationGroup(10)
            sage: C.as_AbelianGroup()
            Multiplicative Abelian Group isomorphic to C2 x C5
        """
        n = Integer(n)
        if n < 1:
            raise ValueError, "n (=%s) must be >= 1"%n
        gens = tuple(range(1, n+1))
        PermutationGroup_generic.__init__(self, [gens], n)

    def _repr_(self):
        """
        EXAMPLES:
            sage: CyclicPermutationGroup(8)
            Cyclic group of order 8 as a permutation group
        """
        return "Cyclic group of order %s as a permutation group"%self.order()

    def is_commutative(self):
        """
        Return True if this group is commutative.

        EXAMPLES:
            sage: C = CyclicPermutationGroup(8)
            sage: C.is_commutative()
            True
        """
        return True

    def is_abelian(self):
        """
        Return True if this group is abelian.

        EXAMPLES:
            sage: C = CyclicPermutationGroup(8)
            sage: C.is_abelian()
            True
        """
        return True

    def as_AbelianGroup(self):
        """
        Returns the corresponding Abelian Group instance.

        EXAMPLES:
            sage: C = CyclicPermutationGroup(8)
            sage: C.as_AbelianGroup()
            Multiplicative Abelian Group isomorphic to C8

        """
        n = self.order()
        a = list(factor(n))
        invs = [x[0]**x[1] for x in a]
        G = AbelianGroup(len(a), invs)
        return G

class DiCyclicGroup(PermutationGroup_unique):
    r"""
    The dicyclic group of order `4n`, for `n\geq 2`.

    INPUT:
        - n -- a positive integer, two or greater

    OUTPUT:

    This is a nonabelian group similar in some respects to the
    dihedral group of the same order, but with far fewer
    elements of order 2 (it has just one).  The permutation
    representation constructed here is based on the presentation

    .. MATH::

        \langle a, x\mid a^{2n}=1, x^{2}=a^{n}, x^{-1}ax=a^{-1}\rangle

    For `n=2` this is the group of quaternions
    (`{\pm 1, \pm I,\pm J, \pm K}`), which is the nonabelian
    group of order 8 that is not the dihedral group `D_4`,
    the symmetries of a square.  For `n=3` this is the nonabelian
    group of order 12 that is not the dihedral group `D_6`
    nor the alternating group `A_4`.  This group of order 12 is
    also the semi-direct product of of `C_2` by `C_4`,
    `C_3\rtimes C_4`.  [CONRAD2009]_


    When the order of the group is a
    power of 2 it is known as a "generalized quaternion group."

    IMPLEMENTATION:

    The presentation above means every element can be written as
    `a^{i}x^{j}` with `0\leq i<2n`, `j=0,1`.  We code `a^i` as the symbol
    `i+1` and code `a^{i}x` as the symbol `2n+i+1`.  The two generators
    are then represented using a left regular representation.

    EXAMPLES:

    A dicyclic group of order 384, with a large power of 2 as a divisor::

        sage: n = 3*2^5
        sage: G = DiCyclicGroup(n)
        sage: G.order()
        384
        sage: a = G.gen(0)
        sage: x = G.gen(1)
        sage: a^(2*n)
        ()
        sage: a^n==x^2
        True
        sage: x^-1*a*x==a^-1
        True

    A large generalized quaternion group (order is a power of 2)::

        sage: n = 2^10
        sage: G=DiCyclicGroup(n)
        sage: G.order()
        4096
        sage: a = G.gen(0)
        sage: x = G.gen(1)
        sage: a^(2*n)
        ()
        sage: a^n==x^2
        True
        sage: x^-1*a*x==a^-1
        True

    Just like the dihedral group, the dicyclic group has
    an element whose order is half the order of the group.
    Unlike the dihedral group, the dicyclic group has only
    one element of order 2.  Like the dihedral groups of
    even order, the center of the dicyclic group is a
    subgroup of order 2 (thus has the unique element of
    order 2 as its non-identity element). ::

        sage: G=DiCyclicGroup(3*5*4)
        sage: G.order()
        240
        sage: two = [g for g in G if g.order()==2]; two
        [(1,5)(2,6)(3,7)(4,8)(9,13)(10,14)(11,15)(12,16)]
        sage: G.center().order()
        2

    For small orders, we check this is really a group
    we do not have in Sage otherwise. ::

        sage: G = DiCyclicGroup(2)
        sage: H = DihedralGroup(4)
        sage: G.is_isomorphic(H)
        False
        sage: G = DiCyclicGroup(3)
        sage: H = DihedralGroup(6)
        sage: K = AlternatingGroup(6)
        sage: G.is_isomorphic(H) or G.is_isomorphic(K)
        False

    REFERENCES:

        .. [CONRAD2009] `Groups of order 12
          <http://www.math.uconn.edu/~kconrad/blurbs/grouptheory/group12.pdf>`_.
          Keith Conrad, accessed 21 October 2009.

    AUTHOR:
        - Rob Beezer (2009-10-18)
    """
    def __init__(self, n):
        r"""
        The dicyclic group of order `4*n`, as a permutation group.

        INPUT:
            n -- a positive integer, two or greater

        EXAMPLES:
            sage: G = DiCyclicGroup(3*8)
            sage: G.order()
            96
            sage: TestSuite(G).run()
        """
        n = Integer(n)
        if n < 2:
            raise ValueError, "n (=%s) must be 2 or greater"%n

        # Certainly 2^2 is part of the first factor of the order
        #   r is maximum power of 2 in the order
        #   m is the rest, the odd part
        order = 4*n
        factored = order.factor()
        r = factored[0][0]**factored[0][1]
        m = order//r
        halfr, fourthr = r//2, r//4

        # Representation of  a
        # Two cycles of length halfr
        a = [tuple(range(1, halfr+1)), tuple(range(halfr+1, r+1))]
        # With an odd part, a cycle of length m will give the right order for a
        if m > 1:
            a.append( tuple(range(r+1, r+m+1)) )

        # Representation of  x
        # Four-cycles that will conjugate the generator  a  properly
        x = [(i+1, (-i)%halfr + halfr + 1, (fourthr+i)%halfr + 1, (-fourthr-i)%halfr + halfr + 1)
                for i in range(0, fourthr)]
        # With an odd part, transpositions will conjugate the m-cycle to create inverse
        if m > 1:
            x += [(r+i+1, r+m-i) for i in range(0, (m-1)//2)]

        PermutationGroup_generic.__init__(self, gens=[a, x])

    def _repr_(self):
        r"""
        EXAMPLES:
            sage: DiCyclicGroup(12)
            Diyclic group of order 48 as a permutation group
        """
        return "Diyclic group of order %s as a permutation group"%self.order()

    def is_commutative(self):
        r"""
        Return True if this group is commutative.

        EXAMPLES::

            sage: D = DiCyclicGroup(12)
            sage: D.is_commutative()
            False
        """
        return False

    def is_abelian(self):
        r"""
        Return True if this group is abelian.

        EXAMPLES::

            sage: D = DiCyclicGroup(12)
            sage: D.is_abelian()
            False
        """
        return False

class KleinFourGroup(PermutationGroup_unique):
    def __init__(self):
        r"""
        The Klein 4 Group, which has order $4$ and exponent $2$, viewed
        as a subgroup of $S_4$.

        OUTPUT:
            -- the Klein 4 group of order 4, as a permutation group of degree 4.

        EXAMPLES:
            sage: G = KleinFourGroup(); G
            The Klein 4 group of order 4, as a permutation group
            sage: list(G)
            [(), (3,4), (1,2), (1,2)(3,4)]

        TESTS::

            sage: G.category()
            Category of finite permutation groups
            sage: TestSuite(G).run()

        AUTHOR:
            -- Bobby Moretti (2006-10)
        """
        gens = [(1,2),(3,4)]
        PermutationGroup_generic.__init__(self, gens)

    def _repr_(self):
        """
        EXAMPLES:
            sage: G = KleinFourGroup(); G
            The Klein 4 group of order 4, as a permutation group
        """
        return 'The Klein 4 group of order 4, as a permutation group'

class QuaternionGroup(DiCyclicGroup):
    r"""
    The quaternion group of order 8.

    OUTPUT:
        The quaternion group of order 8, as a permutation group.
        See the ``DiCyclicGroup`` class for a generalization of this
        construction.

    EXAMPLES:

    The quaternion group is one of two non-abelian groups of order 8,
    the other being the dihedral group `D_4`.  One way to describe this
    group is with three generators, `I, J, K`, so the whole group is
    then given as the set `\{\pm 1, \pm I, \pm J, \pm K\}` with relations
    such as `I^2=J^2=K^2=-1`, `IJ=K` and `JI=-K`.

    The examples below illustrate how to use this group in a similar
    manner, by testing some of these relations.  The representation used
    here is the left-regular representation. ::

        sage: Q = QuaternionGroup()
        sage: I = Q.gen(0)
        sage: J = Q.gen(1)
        sage: K = I*J
        sage: [I,J,K]
        [(1,2,3,4)(5,6,7,8), (1,5,3,7)(2,8,4,6), (1,8,3,6)(2,7,4,5)]
        sage: neg_one = I^2; neg_one
        (1,3)(2,4)(5,7)(6,8)
        sage: J^2 == neg_one and K^2 == neg_one
        True
        sage: J*I == neg_one*K
        True
        sage: Q.center().order() == 2
        True
        sage: neg_one in Q.center()
        True

    AUTHOR:
        -- Rob Beezer (2009-10-09)
    """
    def __init__(self):
        r"""
        TESTS::

            sage: Q = QuaternionGroup()
            sage: TestSuite(Q).run()
        """
        DiCyclicGroup.__init__(self, 2)

    def _repr_(self):
        r"""
        EXAMPLES:
            sage: Q=QuaternionGroup(); Q
            Quaternion group of order 8 as a permutation group
        """
        return "Quaternion group of order 8 as a permutation group"

class DihedralGroup(PermutationGroup_unique):
    def __init__(self, n):
        """
        The Dihedral group of order $2n$ for any integer $n\geq 1$.

        INPUT:
            n -- a positive integer

        OUTPUT:
            -- the dihedral group of order 2*n, as a permutation group

        EXAMPLES:
            sage: DihedralGroup(1)
            Dihedral group of order 2 as a permutation group

            sage: DihedralGroup(2)
            Dihedral group of order 4 as a permutation group
            sage: DihedralGroup(2).gens()
            [(3,4), (1,2)]

            sage: DihedralGroup(5).gens()
            [(1,2,3,4,5), (1,5)(2,4)]
            sage: list(DihedralGroup(5))
            [(), (2,5)(3,4), (1,2)(3,5), (1,2,3,4,5), (1,3)(4,5), (1,3,5,2,4), (1,4)(2,3), (1,4,2,5,3), (1,5,4,3,2), (1,5)(2,4)]

            sage: G = DihedralGroup(6)
            sage: G.order()
            12
            sage: G = DihedralGroup(5)
            sage: G.order()
            10
            sage: G
            Dihedral group of order 10 as a permutation group
            sage: G.gens()
            [(1,2,3,4,5), (1,5)(2,4)]

            sage: DihedralGroup(0)
            Traceback (most recent call last):
            ...
            ValueError: n must be positive

        TESTS::

            sage: TestSuite(G).run()
            sage: G.category()
            Category of finite permutation groups
            sage: TestSuite(G).run()
        """
        n = Integer(n)
        if n <= 0:
            raise ValueError, "n must be positive"

        # the first generator generates the cyclic subgroup of D_n, <(1...n)> in
        # cycle notation
        gen0 = range(1,n+1)

        if n < 1:
            raise ValueError, "n (=%s) must be >= 1"%n

        # D_1 is a subgroup of S_2, we need the cyclic group of order 2
        if n == 1:
            gens = CyclicPermutationGroup(2).gens()
        elif n == 2:
            gens = ((1,2),(3,4))
        else:
            gen1 = [(i, n-i+1) for i in range(1, n//2 +1)]
            gens = tuple([tuple(gen0),tuple(gen1)])

        PermutationGroup_generic.__init__(self, gens)

    def _repr_(self):
        """
        EXAMPLES:
            sage: G = DihedralGroup(5); G
            Dihedral group of order 10 as a permutation group
        """
        return "Dihedral group of order %s as a permutation group"%self.order()

class MathieuGroup(PermutationGroup_unique):
    def __init__(self, n):
        """
        The Mathieu group of degree $n$.

        INPUT:
            n -- a positive integer in  {9, 10, 11, 12, 21, 22, 23, 24}.

        OUTPUT:
            -- the Mathieu group of degree n, as a permutation group

        EXAMPLES::

            sage: G = MathieuGroup(12)
            sage: G
            Mathieu group of degree 12 and order 95040 as a permutation group

        TESTS::

            sage: G.category()
            Category of finite permutation groups
            sage: TestSuite(G).run(skip=["_test_enumerated_set_contains", "_test_enumerated_set_iter_list"])

        Note: this is a fairly big group, so we skip some tests that
        currently require to list all the elements of the group,
        because there is no proper iterator yet.
        """
        n = Integer(n)
        self._n = n
        if not(n in [9, 10, 11, 12, 21, 22, 23, 24]):
            raise ValueError,"argument must belong to {9, 10, 11, 12, 21, 22, 23, 24}."
        id = 'MathieuGroup(%s)'%n
        PermutationGroup_generic.__init__(self, gap_group=id)

    def _repr_(self):
        """
        EXAMPLES:
            sage: G = MathieuGroup(12); G
            Mathieu group of degree 12 and order 95040 as a permutation group
        """
        return "Mathieu group of degree %s and order %s as a permutation group"%(self._n,self.order())

class TransitiveGroup(PermutationGroup_unique):
    def __init__(self, d, n):
        """
        The transitive group from the GAP tables of transitive groups.

        INPUT:
            d -- positive integer; the degree
            n -- positive integer; the number

        OUTPUT:
            the n-th transitive group of degree d

        EXAMPLES::

            sage: TransitiveGroup(0,1)
            Transitive group number 1 of degree 0
            sage: TransitiveGroup(1,1)
            Transitive group number 1 of degree 1
            sage: G = TransitiveGroup(5, 2); G         # requires optional database_gap
            Transitive group number 2 of degree 5
            sage: G.gens()                             # requires optional database_gap
            [(1,2,3,4,5), (1,4)(2,3)]

            sage: G.category()                         # requires optional database_gap
            Category of finite permutation groups

        .. warning:: this follows GAP's naming convention of indexing
          the transitive groups starting from ``1``::

            sage: TransitiveGroup(5,0)
            Traceback (most recent call last):
            ...
              assert n > 0
            AssertionError

        .. warning:: only transitive groups of "small" degree are
          available in GAP's database::

            sage: TransitiveGroup(31,1)                # requires optional database_gap
            Traceback (most recent call last):
            ...
            NotImplementedError: Only the transitive groups of order less than 30 are available in GAP's database

        TESTS::

            sage: TestSuite(TransitiveGroup(0,1)).run()
            sage: TestSuite(TransitiveGroup(1,1)).run()
            sage: TestSuite(TransitiveGroup(5,2)).run()# requires optional database_gap

            sage: TransitiveGroup(1,5)
            Traceback (most recent call last):
            ...
            AssertionError: n should be in {1,..,1}
        """
        d = ZZ(d)
        n = ZZ(n)
        assert d >= 0
        assert n > 0
        max_n = TransitiveGroups(d).cardinality()
        assert n <= max_n, "n should be in {1,..,%s}"%max_n
        gap_group = 'Group([()])' if d in [0,1] else 'TransitiveGroup(%s,%s)'%(d,n)
        try:
            PermutationGroup_generic.__init__(self, gap_group=gap_group)
        except RuntimeError:
            from sage.misc.misc import verbose
            verbose("Warning: Computing with TransitiveGroups requires the optional database_gap package. Please install it.", level=0)

        self._d = d
        self._n = n
        self._domain = range(1, d+1)

    def _repr_(self):
        """
        EXAMPLES:
            sage: G = TransitiveGroup(1,1); G
            Transitive group number 1 of degree 1
        """
        return "Transitive group number %s of degree %s"%(self._n, self._d)

def TransitiveGroups(d=None):
    """
    INPUT:

     - ``d`` -- an integer (optional)

    Returns the set of all transitive groups of a given degree
    ``d``. If ``d`` is not specified, it returns the set of all
    transitive groups.

    Warning: TransitiveGroups requires the optional GAP database
    package. Please install it with ``sage -i database_gap``.

    EXAMPLES::

        sage: TransitiveGroups(3)
        Transitive Groups of degree 3
        sage: TransitiveGroups(7)
        Transitive Groups of degree 7
        sage: TransitiveGroups(8)
        Transitive Groups of degree 8

        sage: TransitiveGroups()
        Transitive Groups

    .. warning:: in practice, the database currently only contains
      transitive groups up to degree 30::

        sage: TransitiveGroups(31).cardinality() # requires optional database_gap
        Traceback (most recent call last):
        ...
        NotImplementedError: Only the transitive groups of order less than 30 are available in GAP's database

    """
    if d == None:
        return TransitiveGroupsAll()
    else:
        d == Integer(d)
        assert d >= 0, "A transitive group acts on a non negative integer number of positions"
        return TransitiveGroupsOfDegree(d)

class TransitiveGroupsAll(DisjointUnionEnumeratedSets):
    """
    The infinite set of all transitive groups.

    EXAMPLES::

        sage: L = TransitiveGroups(); L
        Transitive Groups
        sage: L.category()
        Category of infinite enumerated sets
        sage: L.cardinality()
        +Infinity

        sage: p = L.__iter__()            # requires optional database_gap
        sage: (p.next(), p.next(), p.next(), p.next(), p.next(), p.next(), p.next(), p.next()) # requires optional database_gap
        (Transitive group number 1 of degree 0, Transitive group number 1 of degree 1, Transitive group number 1 of degree 2, Transitive group number 1 of degree 3, Transitive group number 2 of degree 3, Transitive group number 1 of degree 4, Transitive group number 2 of degree 4, Transitive group number 3 of degree 4)

    TESTS::

        sage: TestSuite(TransitiveGroups()).run() # requires optional database_gap # long time
    """
    def __init__(self):
        """
        TESTS::

            sage: S = TransitiveGroups() # requires optional database_gap
            sage: S.category() # requires optional database_gap
            Category of infinite enumerated sets
        """
        DisjointUnionEnumeratedSets.__init__(self, Family(NonNegativeIntegers(), lambda i: TransitiveGroups(i)) )

    def _repr_(self):
        """
        TESTS::

            sage: TransitiveGroups() # requires optional database_gap # indirect doctest
            Transitive Groups
        """
        return "Transitive Groups"

    def __contains__(self, G):
        r"""
        EXAMPLES::

            sage: TransitiveGroup(5,2) in TransitiveGroups() # requires optional database_gap
            True
            sage: TransitiveGroup(6,5) in TransitiveGroups() # requires optional database_gap
            True
            sage: 1 in TransitiveGroups() # requires optional database_gap
            False
        """
        return isinstance(G,TransitiveGroup)

    def _an_element_(self):
        """
        Returns an element of ``self``.

        EXAMPLES::

            sage: TransitiveGroups(5).an_element() # requires optional database_gap # indirect doctest
            Transitive group number 1 of degree 5
        """
        return TransitiveGroup(7,3)

class TransitiveGroupsOfDegree(UniqueRepresentation, Parent):
    """
    The set of all transitive groups of a given (small) degree.

    EXAMPLES::

        sage: S = TransitiveGroups(4); S       # requires optional database_gap
        Transitive Groups of degree 4
        sage: list(S)                          # requires optional database_gap
        [Transitive group number 1 of degree 4, Transitive group number 2 of degree 4, Transitive group number 3 of degree 4, Transitive group number 4 of degree 4, Transitive group number 5 of degree 4]

        sage: TransitiveGroups(5).an_element() # requires optional database_gap
        Transitive group number 1 of degree 5

    We write the cardinality of all transitive groups of degree 5::

        sage: for G in TransitiveGroups(5):    # requires optional database_gap
        ...       print G.cardinality()
        5
        10
        20
        60
        120

    TESTS::

        sage: TestSuite(TransitiveGroups(3)).run() # requires optional database_gap


    """
    def __init__(self, n):
        """
        TESTS::

            sage: S = TransitiveGroups(4) # requires optional database_gap
            sage: S.category() # requires optional database_gap
            Category of finite enumerated sets
        """
        self._degree = n
        Parent.__init__(self, category = FiniteEnumeratedSets())

    def _repr_(self):
        """
        TESTS::

            sage: TransitiveGroups(6) # requires optional database_gap
            Transitive Groups of degree 6
        """
        return "Transitive Groups of degree %s"%(self._degree)

    def __contains__(self, G):
        r"""
        EXAMPLES::

            sage: TransitiveGroup(6,5) in TransitiveGroups(4) # requires optional database_gap
            False
            sage: TransitiveGroup(4,3) in TransitiveGroups(4) # requires optional database_gap
            True
            sage: 1 in TransitiveGroups(4) # requires optional database_gap
            False
        """
        if isinstance(G,TransitiveGroup):
            return G._d == self._degree
        else:
            False

    def __getitem__(self, n):
        r"""
        INPUT:

         - ``n`` -- a positive integer

        Returns the `n`-th transitive group of a given degree.

        EXAMPLES::

            sage: TransitiveGroups(5)[3]          # requires optional database_gap#
            Transitive group number 3 of degree 5

        .. warning:: this follows GAP's naming convention of indexing
        the transitive groups starting from ``1``::

            sage: TransitiveGroups(5)[0]
            Traceback (most recent call last):
            ...
                assert n > 0
            AssertionError
        """
        return TransitiveGroup(self._degree, n)

    def __iter__(self):
        """
        EXAMPLES::

            sage: list(TransitiveGroups(5)) # indirect doctest # requires optional database_gap
            [Transitive group number 1 of degree 5, Transitive group number 2 of degree 5, Transitive group number 3 of degree 5, Transitive group number 4 of degree 5, Transitive group number 5 of degree 5]
        """
        for n in xrange(1, self.cardinality() + 1):
            yield self[n]

    _an_element_ = EnumeratedSets.ParentMethods._an_element_

    @cached_method
    def cardinality(self):
        r"""
        Returns the cardinality of ``self``, that is the number of
        transitive groups of a given degree.

        EXAMPLES::

            sage: TransitiveGroups(0).cardinality()                      # requires optional database_gap
            1
            sage: TransitiveGroups(2).cardinality()                      # requires optional database_gap
            1
            sage: TransitiveGroups(7).cardinality()                      # requires optional database_gap
            7
            sage: TransitiveGroups(12).cardinality()                     # requires optional database_gap
            301
            sage: [TransitiveGroups(i).cardinality() for i in range(11)] # requires optional database_gap
            [1, 1, 1, 2, 5, 5, 16, 7, 50, 34, 45]

        .. warning::

            The database_gap contains all transitive groups
            up to degree 30::

                sage: TransitiveGroups(31).cardinality()                     # requires optional database_gap
                Traceback (most recent call last):
                ...
                NotImplementedError: Only the transitive groups of order less than 30 are available in GAP's database

        TESTS::

            sage: type(TransitiveGroups(12).cardinality())               # requires optional database_gap
            <type 'sage.rings.integer.Integer'>
            sage: type(TransitiveGroups(0).cardinality())
            <type 'sage.rings.integer.Integer'>
        """
        # gap.NrTransitiveGroups(0) fails, so Sage needs to handle this

        # While we are at it, and since Sage also handles the
        # transitive group of degree 1, we may as well handle 1
        if self._degree <= 1:
            return ZZ(1)
        else:
            try:
                return Integer(gap.NrTransitiveGroups(gap(self._degree)))
            except RuntimeError:
                from sage.misc.misc import verbose
                verbose("Warning: TransitiveGroups requires the GAP database package. Please install it with ``sage -i database_gap``.", level=0)
            except TypeError:
                raise NotImplementedError, "Only the transitive groups of order less than 30 are available in GAP's database"

class PermutationGroup_plg(PermutationGroup_unique):
    def base_ring(self):
        """
        EXAMPLES:
            sage: G = PGL(2,3)
            sage: G.base_ring()
            Finite Field of size 3

            sage: G = PSL(2,3)
            sage: G.base_ring()
            Finite Field of size 3
        """
        return self._base_ring

    def matrix_degree(self):
        """
        EXAMPLES:
            sage: G = PSL(2,3)
            sage: G.matrix_degree()
            2
        """
        return self._n

class PGL(PermutationGroup_plg):
    def __init__(self, n, q, name='a'):
        """
        The projective general linear groups over GF(q).

        INPUT:
            n -- positive integer; the degree
            q -- prime power; the size of the ground field
            name -- (default: 'a') variable name of indeterminate of finite field GF(q)

        OUTPUT:
            PGL(n,q)

        EXAMPLES:
            sage: G = PGL(2,3); G
            Permutation Group with generators [(3,4), (1,2,4)]
            sage: print G
            The projective general linear group of degree 2 over Finite Field of size 3
            sage: G.base_ring()
            Finite Field of size 3
            sage: G.order()
            24

            sage: G = PGL(2, 9, 'b'); G
            Permutation Group with generators [(3,10,9,8,4,7,6,5), (1,2,4)(5,6,8)(7,9,10)]
            sage: G.base_ring()
            Finite Field in b of size 3^2

            sage: G.category()
            Category of finite permutation groups
            sage: TestSuite(G).run()
        """
        id = 'Group([()])' if n == 1 else 'PGL(%s,%s)'%(n,q)
        PermutationGroup_generic.__init__(self, gap_group=id)
        self._q = q
        self._base_ring = GF(q, name=name)
        self._n = n

    def __str__(self):
        """
        EXAMPLES:
            sage: G = PGL(2,3); G
            Permutation Group with generators [(3,4), (1,2,4)]
            sage: print G
            The projective general linear group of degree 2 over Finite Field of size 3
        """
        return "The projective general linear group of degree %s over %s"%(self._n, self.base_ring())

class PSL(PermutationGroup_plg):
    def __init__(self, n, q, name='a'):
        """
        The projective special linear groups over GF(q).

        INPUT:
            n -- positive integer; the degree
            q -- prime power; the size of the ground field
            name -- (default: 'a') variable name of indeterminate of finite field GF(q)

        OUTPUT:
            PSL(n,q)

        EXAMPLES:
            sage: G = PSL(2,3); G
            Permutation Group with generators [(2,3,4), (1,2)(3,4)]
            sage: G.order()
            12
            sage: G.base_ring()
            Finite Field of size 3
            sage: print G
            The projective special linear group of degree 2 over Finite Field of size 3

        We create two groups over nontrivial finite fields:
            sage: G = PSL(2, 4, 'b'); G
            Permutation Group with generators [(3,4,5), (1,2,3)]
            sage: G.base_ring()
            Finite Field in b of size 2^2
            sage: G = PSL(2, 8); G
            Permutation Group with generators [(3,8,6,4,9,7,5), (1,2,3)(4,7,5)(6,9,8)]
            sage: G.base_ring()
            Finite Field in a of size 2^3

            sage: G.category()
            Category of finite permutation groups
            sage: TestSuite(G).run()
        """
        if n == 1:
            id = 'Group([()])'
        else:
            id = 'PSL(%s,%s)'%(n,q)
        PermutationGroup_generic.__init__(self, gap_group=id)
        self._q = q
        self._base_ring = GF(q, name=name)
        self._n = n


    def __str__(self):
        """
        EXAMPLES:
            sage: G = PSL(2,3)
            sage: print G
            The projective special linear group of degree 2 over Finite Field of size 3
        """
        return "The projective special linear group of degree %s over %s"%(self._n, self.base_ring())

    def ramification_module_decomposition_hurwitz_curve(self):
        """
        Helps compute the decomposition of the ramification module
        for the Hurwitz curves X (over CC say) with automorphism group
        G = PSL(2,q), q a "Hurwitz prime" (ie, p is $\pm 1 \pmod 7$).
        Using this computation and Borne's formula helps determine the
        G-module structure of the RR spaces of equivariant
        divisors can be determined explicitly.

        The output is a list of integer multiplicities: [m1,...,mn],
        where n is the number of conj classes of G=PSL(2,p) and mi is the
        multiplicity of pi_i in the ramification module of a
        Hurwitz curve with automorphism group G.
        Here IrrRepns(G) = [pi_1,...,pi_n] (in the order listed in the
        output of self.character_table()).

        REFERENCE: David Joyner, Amy Ksir, Roger Vogeler,
                   "Group representations on Riemann-Roch spaces of some
                   Hurwitz curves," preprint, 2006.

        EXAMPLES:
            sage: G = PSL(2,13)
            sage: G.ramification_module_decomposition_hurwitz_curve() #random
            [0, 7, 7, 12, 12, 12, 13, 15, 14]

        This means, for example, that the trivial representation does not
        occur in the ramification module of a Hurwitz curve with automorphism
        group PSL(2,13), since the trivial representation is listed first
        and that entry has multiplicity 0. The "randomness" is due to the
        fact that GAP randomly orders the conjugacy classes of the same order
        in the list of all conjugacy classes. Similarly, there is some
        randomness to the ordering of the characters.

        If you try to use this function on a group PSL(2,q) where q is
        not a (smallish) "Hurwitz prime", an error message will be printed.
        """
        if self.matrix_degree()!=2:
            raise ValueError("Degree must be 2.")
        F = self.base_ring()
        q = F.order()
        from sage.misc.misc import SAGE_EXTCODE
        gapcode = SAGE_EXTCODE + '/gap/joyner/hurwitz_crv_rr_sp.gap'
        gap.eval('Read("'+gapcode+'")')
        mults = gap.eval("ram_module_hurwitz("+str(q)+")")
        return eval(mults)

    def ramification_module_decomposition_modular_curve(self):
        """
        Helps compute the decomposition of the ramification module
        for the modular curve X(p) (over CC say) with automorphism group G = PSL(2,q),
        q a prime > 5. Using this computation and Borne's formula helps determine the
        G-module structure of the RR spaces of equivariant
        divisors can be determined explicitly.

        The output is a list of integer multiplicities: [m1,...,mn],
        where n is the number of conj classes of G=PSL(2,p) and mi is the
        multiplicity of pi_i in the ramification module of a
        modular curve with automorphism group G.
        Here IrrRepns(G) = [pi_1,...,pi_n] (in the order listed in the
        output of self.character_table()).

        REFERENCE: D. Joyner and A. Ksir, 'Modular representations
                   on some Riemann-Roch spaces of modular curves
                   $X(N)$', Computational Aspects of Algebraic Curves,
                   (Editor: T. Shaska) Lecture Notes in Computing, WorldScientific,
                   2005.)

        EXAMPLES:
            sage: G = PSL(2,7)
            sage: G.ramification_module_decomposition_modular_curve() ## random
            [0, 4, 3, 6, 7, 8]

        This means, for example, that the trivial representation does not
        occur in the ramification module of X(7), since the trivial representation
        is listed first and that entry has multiplicity 0. The "randomness" is due to the
        fact that GAP randomly orders the conjugacy classes of the same order
        in the list of all conjugacy classes. Similarly, there is some
        randomness to the ordering of the characters.
        """
        if self.matrix_degree()!=2:
            raise ValueError("Degree must be 2.")
        F = self.base_ring()
        q = F.order()
        from sage.misc.misc import SAGE_EXTCODE
        gapcode = SAGE_EXTCODE + '/gap/joyner/modular_crv_rr_sp.gap'
        gap.eval('Read("'+gapcode+'")')
        mults = gap.eval("ram_module_X("+str(q)+")")
        return eval(mults)

class PSp(PermutationGroup_plg):
    def __init__(self, n, q, name='a'):
        """
        The projective symplectic linear groups over GF(q).

        INPUT:
            n -- positive integer; the degree
            q -- prime power; the size of the ground field
            name -- (default: 'a') variable name of indeterminate of finite field GF(q)

        OUTPUT:
            PSp(n,q)

        EXAMPLES:
            sage: G = PSp(2,3); G
            Permutation Group with generators [(2,3,4), (1,2)(3,4)]
            sage: G.order()
            12
            sage: G = PSp(4,3); G
            Permutation Group with generators [(3,4)(6,7)(9,10)(12,13)(17,20)(18,21)(19,22)(23,32)(24,33)(25,34)(26,38)(27,39)(28,40)(29,35)(30,36)(31,37), (1,5,14,17,27,22,19,36,3)(2,6,32)(4,7,23,20,37,13,16,26,40)(8,24,29,30,39,10,33,11,34)(9,15,35)(12,25,38)(21,28,31)]
            sage: G.order()
            25920
            sage: print G
            The projective symplectic linear group of degree 4 over Finite Field of size 3
            sage: G.base_ring()
            Finite Field of size 3

            sage: G = PSp(2, 8, name='alpha'); G
            Permutation Group with generators [(3,8,6,4,9,7,5), (1,2,3)(4,7,5)(6,9,8)]
            sage: G.base_ring()
            Finite Field in alpha of size 2^3
        """
        if n%2 == 1:
            raise TypeError, "The degree n must be even"
        else:
            id = 'PSp(%s,%s)'%(n,q)
        PermutationGroup_generic.__init__(self, gap_group=id)
        self._q = q
        self._base_ring = GF(q, name=name)
        self._n = n

    def __str__(self):
        """
        EXAMPLES:
            sage: G = PSp(4,3)
            sage: print G
            The projective symplectic linear group of degree 4 over Finite Field of size 3
        """
        return "The projective symplectic linear group of degree %s over %s"%(self._n, self.base_ring())

PSP = PSp

class PermutationGroup_pug(PermutationGroup_plg):
    def field_of_definition(self):
        """
        EXAMPLES:
            sage: PSU(2,3).field_of_definition()
            Finite Field in a of size 3^2
        """
        return self._field_of_definition

class PSU(PermutationGroup_pug):
    def __init__(self, n, q, name='a'):
        """
        The projective special unitary groups over GF(q).

        INPUT:
            n -- positive integer; the degree
            q -- prime power; the size of the ground field
            name -- (default: 'a') variable name of indeterminate of finite field GF(q)
        OUTPUT:
            PSU(n,q)

        EXAMPLES:
            sage: PSU(2,3)
            The projective special unitary group of degree 2 over Finite Field of size 3

            sage: G = PSU(2, 8, name='alpha'); G
            The projective special unitary group of degree 2 over Finite Field in alpha of size 2^3
            sage: G.base_ring()
            Finite Field in alpha of size 2^3
        """
        id = 'PSU(%s,%s)'%(n,q)
        PermutationGroup_generic.__init__(self, gap_group=id)
        self._q = q
        self._base_ring = GF(q, name=name)
        self._field_of_definition = GF(q**2, name)
        self._n = n

    def _repr_(self):
        """
        EXAMPLES:
            sage: PSU(2,3)
            The projective special unitary group of degree 2 over Finite Field of size 3

        """
        return "The projective special unitary group of degree %s over %s"%(self._n, self.base_ring())

class PGU(PermutationGroup_pug):
    def __init__(self, n, q, name='a'):
        """
        The projective general unitary groups over GF(q).

        INPUT:
            n -- positive integer; the degree
            q -- prime power; the size of the ground field
            name -- (default: 'a') variable name of indeterminate of finite field GF(q)

        OUTPUT:
            PGU(n,q)

        EXAMPLES:
            sage: PGU(2,3)
            The projective general unitary group of degree 2 over Finite Field of size 3

            sage: G = PGU(2, 8, name='alpha'); G
            The projective general unitary group of degree 2 over Finite Field in alpha of size 2^3
            sage: G.base_ring()
            Finite Field in alpha of size 2^3
        """
        id = 'PGU(%s,%s)'%(n,q)
        PermutationGroup_generic.__init__(self, gap_group=id)
        self._q = q
        self._base_ring = GF(q, name=name)
        self._field_of_definition = GF(q**2, name)
        self._n = n

    def _repr_(self):
        """
        EXAMPLES:
            sage: PGU(2,3)
            The projective general unitary group of degree 2 over Finite Field of size 3

        """
        return "The projective general unitary group of degree %s over %s"%(self._n, self.base_ring())


class SuzukiGroup(PermutationGroup_unique):
    def __init__(self, q, name='a'):
        r"""
        The Suzuki group over GF(q),
        $^2 B_2(2^{2k+1}) = Sz(2^{2k+1})$.

        A wrapper for the GAP function SuzukiGroup.

        INPUT:
            q -- 2^n, an odd power of 2; the size of the ground
                 field. (Strictly speaking, n should be greater than 1, or
                 else this group os not simple.)
            name -- (default: 'a') variable name of indeterminate of
                    finite field GF(q)

        OUTPUT:

        - A Suzuki group.

        EXAMPLES::

            sage: SuzukiGroup(8)
            Permutation Group with generators [(1,2)(3,10)(4,42)(5,18)(6,50)(7,26)(8,58)(9,34)(12,28)(13,45)(14,44)(15,23)(16,31)(17,21)(19,39)(20,38)(22,25)(24,61)(27,60)(29,65)(30,55)(32,33)(35,52)(36,49)(37,59)(40,54)(41,62)(43,53)(46,48)(47,56)(51,63)(57,64), (1,28,10,44)(3,50,11,42)(4,43,53,64)(5,9,39,52)(6,36,63,13)(7,51,60,57)(8,33,37,16)(12,24,55,29)(14,30,48,47)(15,19,61,54)(17,59,22,62)(18,23,34,31)(20,38,49,25)(21,26,45,58)(27,32,41,65)(35,46,40,56)]
            sage: print SuzukiGroup(8)
            The Suzuki group over Finite Field in a of size 2^3

            sage: G = SuzukiGroup(32, name='alpha')
            sage: G.order()
            32537600
            sage: G.order().factor()
            2^10 * 5^2 * 31 * 41
            sage: G.base_ring()
            Finite Field in alpha of size 2^5

        REFERENCES:

        -  http://en.wikipedia.org/wiki/Group_of_Lie_type\#Suzuki-Ree_groups
        """
        q = Integer(q)
        from sage.rings.arith import valuation
        t = valuation(q, 2)
        if 2**t != q or is_even(t):
            raise ValueError,"The ground field size %s must be an odd power of 2."%q
        id = 'SuzukiGroup(IsPermGroup,%s)'%q
        PermutationGroup_generic.__init__(self, gap_group=id)
        self._q = q
        self._base_ring = GF(q, name=name)

    def base_ring(self):
        """
        EXAMPLES:
            sage: G = SuzukiGroup(32, name='alpha')
            sage: G.base_ring()
            Finite Field in alpha of size 2^5

        """
        return self._base_ring

    def __str__(self):
        """
        EXAMPLES:
            sage: G = SuzukiGroup(32, name='alpha')
            sage: print G
            The Suzuki group over Finite Field in alpha of size 2^5

        """
        return "The Suzuki group over %s"%self.base_ring()
