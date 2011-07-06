r"""
Arithmetic subgroups defined by permutation action of generators on cosets.

A subgroup of finite index `H` of a finitely generated group `G` is completely
described by the action of the generators on the right cosets `H\\G = \{Hg\}`.
After some arbitrary choice of numbering one can identify the action of
generators as elements of a symmetric group acting transitively (and satisfying
the relations of the relators in G). As `{\rm SL}_2(\ZZ)` is a central extension of a
free product of cyclic group one can easily design algorithms from this point of
view.

The generators of `{\rm SL}_2(\ZZ)` used in this module are named as follows `s_2`,
`s_3`, `l`, `r` which are defined by

.. MATH::

    s_2 = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix},\quad
    s_3 = \begin{pmatrix} 0 & 1 \\ -1 & 1 \end{pmatrix},\quad
    l = \begin{pmatrix} 1 & 1 \\ 0 & 1 \end{pmatrix},\quad
    r = \begin{pmatrix} 1 & 0 \\ 1 & 1 \end{pmatrix}.

Those generators satisfy the following relations

.. MATH::

    s_2^2 = s_3^3 = -1 \quad r = s_2^{-1}\ l^{-1}\ s_2.

In particular not all four are needed to generate the whole `{\rm SL}_2(\ZZ)`. Three
couples which which generate `{\rm SL}_2(\ZZ)` are of particular interest:

- `(l,r)` as the pair is involved in the continued fraction algorithm,
- `(l,s_2)` similar as the one above because of the relations,
- `(s_2,s_3)` as the pair generates freely `{\rm PSL}_2(\ZZ)`.

Part of these functions are based on Chris Kurth's *KFarey* package [Kur08]. For
tests see the file sage.modular.arithgroup.tests

REFERENCES:

.. [AtSD71] A. O. L. Atkin and H. P. F. Swinnerton-Dyer, "Modular forms on
   noncongruence subgroups", Proc. Symp. Pure Math., Combinatorics (T. S. Motzkin,
   ed.), vol. 19, AMS, Providence 1971

.. [Hsu96] Tim Hsu, "Identifying congruence subgroups of the modular group",
   Proc. AMS 124, no. 5, 1351-1359 (1996)

.. [Hsu97] Tim Hsu, "Permutation techniques for coset representations of modular
   subgroups", in L. Schneps (ed.), Geometric Galois Actions II: Dessins
   d'Enfants, Mapping Class Groups and Moduli, volume 243 of LMS Lect. Notes,
   67-77, Cambridge Univ. Press (1997)

.. [Go09] Alexey G. Gorinov, "Combinatorics of double cosets and fundamental
   domains for the subgroups of the modular group", preprint
   http://fr.arxiv.org/abs/0901.1340

.. [Kul91] Ravi Kulkarni "An arithmetic geometric method in the study of the
   subgroups of the modular group", American Journal of Mathematics 113 (1991),
   no 6, 1053-1133

.. [Kur08] Chris Kurth, "K Farey package for Sage",
   http://www.public.iastate.edu/~kurthc/research/index.html

.. [KuLo] Chris Kurth and Ling Long, "Computations with finite index subgroups
   of `{\rm PSL}_2(ZZ)` using Farey symbols"

.. [Ve] Helena Verrill, "Fundamental domain drawer", java program,
   http://www.math.lsu.edu/~verrill/

TODO:

- modular Farey symbols

- computation of generators of a modular subgroup with a standard surface
  group presentation. In other words, compute a presentation of the form

  .. MATH::

      \langle x_i,y_i,c_j |\ \prod_i [x_i,y_i] \prod_j c_j^{\nu_j} = 1\rangle

  where the elements `x_i` and `y_i` are hyperbolic and `c_j` are parabolic
  (`\nu_j=\infty`) or elliptic elements (`\nu_j < \infty`).

- computation of centralizer.

- generation of modular (even) subgroups of fixed index.

AUTHORS:

- Chris Kurth (2008): created KFarey package

- David Loeffler (2009): adapted functions from KFarey for inclusion into Sage

- Vincent Delecroix (2010): implementation for odd groups, new design,
  improvements, documentation
"""

################################################################################
#
#       Copyright (C) 2009, The Sage Group -- http://www.sagemath.org/
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#
################################################################################

from all import SL2Z
from arithgroup_generic import ArithmeticSubgroup
from arithgroup_element import ArithmeticSubgroupElement
from sage.rings.all import Zmod, ZZ
from sage.rings.infinity import Infinity
from sage.misc.cachefunc import cached_method
import sage.rings.arith as arith

from sage.groups.perm_gps.permgroup_element import PermutationGroupElement


Idm = SL2Z([1,0,0,1])    # identity

Lm = SL2Z([1,1,0,1])     # parabolic that fixes infinity
Rm = SL2Z([1,0,1,1])     # parabolic that fixes 0
S2m = SL2Z([0,-1,1,0])   # elliptic of order 2 (fix i)
S3m = SL2Z([0,1,-1,1])   # elliptic of order 3 (fix j)

S2mi = SL2Z([0,1,-1,0])  # the inverse of S2m in SL(2,Z)
S3mi = SL2Z([1,-1,1,0])  # the inverse of S3m in SL(2,Z)
Lmi = SL2Z([1,-1,0,1])   # the inverse of Lm in SL(2,Z)
Rmi = SL2Z([1,0,-1,1])   # the inverse of Rm in SL(2,Z)

def sl2z_word_problem(A):
    r"""
    Given an element of `{\rm SL}_2(\ZZ)`, express it as a word in the generators L =
    [1,1,0,1] and R = [1,0,1,1].

    The return format is a list of pairs ``(a,b)``, where ``a = 0`` or ``1``
    denoting ``L`` or ``R`` respectively, and ``b`` is an integer exponent.

    See also the method eval_sl2z_word.

    EXAMPLES::

        sage: from sage.modular.arithgroup.arithgroup_perm import eval_sl2z_word, sl2z_word_problem
        sage: m = SL2Z([1,0,0,1])
        sage: eval_sl2z_word(sl2z_word_problem(m)) == m
        True
        sage: m = SL2Z([0,-1,1,0])
        sage: eval_sl2z_word(sl2z_word_problem(m)) == m
        True
        sage: m = SL2Z([7,8,-50,-57])
        sage: eval_sl2z_word(sl2z_word_problem(m)) == m
        True
    """
    A = SL2Z(A)
    output=[]

    ## If A00 is zero
    if A[0,0]==0:
        c=A[1,1]
        if c != 1:
            A=A*Lm**(c-1)*Rm*Lmi
            output.extend([(0,1-c),(1,-1),(0,1)])
        else:
            A=A*Rm*Lmi
            output.extend([(1,-1),(0,1)])

    if A[0,0]<0:   # Make sure A00 is positive
        A=SL2Z(-1)*A
        output.extend([(1,-1), (0,1), (1,-1), (0,1), (1,-1), (0,1)])

    if A[0,1]<0:   # if A01 is negative make it positive
        n=(-A[0,1]/A[0,0]).ceil()  #n s.t. 0 <= A[0,1]+n*A[0,0] < A[0,0]
        A=A*Lm**n
        output.append((0, -n))
   ## At this point A00>0 and A01>=0
    while not (A[0,0]==0 or A[0,1]==0):
        if A[0,0]>A[0,1]:
            n=(A[0,0]/A[0,1]).floor()
            A=A*SL2Z([1,0,-n,1])
            output.append((1, n))

        else:      #A[0,0]<=A[0,1]
            n=(A[0,1]/A[0,0]).floor()
            A=A*SL2Z([1,-n,0,1])
            output.append((0, n))

    if A==SL2Z(1):
        pass       #done, so don't add R^0
    elif A[0,0]==0:
        c=A[1,1]
        if c != 1:
            A=A*Lm**(c-1)*Rm*Lmi
            output.extend([(0,1-c),(1,-1),(0, 1)])
        else:
            A=A*Rm*Lmi
            output.extend([(1,-1),(0,1)])
    else:
        c=A[1,0]
        if c:
            A=A*Rm**(-c)
            output.append((1,c))

    output.reverse()
    return output

def eval_sl2z_word(w):
    r"""
    Given a word in the format output by sl2z_word_problem, convert it back
    into an element of `{\rm SL}_2(\ZZ)`.

    EXAMPLES::

        sage: from sage.modular.arithgroup.arithgroup_perm import eval_sl2z_word
        sage: eval_sl2z_word([(0, 1), (1, -1), (0, 0), (1, 3), (0, 2), (1, 9), (0, -1)])
        [ 66 -59]
        [ 47 -42]
    """
    from sage.all import prod
    mat = [Lm,Rm]
    w0 = Idm
    w1 = w
    return w0 * prod((mat[a[0]]**a[1] for a in w1), Idm)

def word_of_perms(w, p1, p2):
    r"""
    Given a word `w` as a list of 2-tuples ``(index,power)`` and permutations
    ``p1`` and ``p2`` return the product of ``p1`` and ``p2`` that corresponds
    to ``w``.

    EXAMPLES::

        sage: import sage.modular.arithgroup.arithgroup_perm as ap
        sage: S2 = SymmetricGroup(4)
        sage: p1 = S2('(1,2)(3,4)')
        sage: p2 = S2('(1,2,3,4)')
        sage: ap.word_of_perms([(1,1),(0,1)], p1, p2) ==  p2 * p1
        True
        sage: ap.word_of_perms([(0,1),(1,1)], p1, p2) == p1 * p2
        True
    """
    if not isinstance(p1,PermutationGroupElement):
        p1 = PermutationGroupElement(p1)
    if not isinstance(p2,PermutationGroupElement):
        p2 = PermutationGroupElement(p2)

    G = p1.parent()
    if G != p2.parent(): # find a minimal parent
        G2 = p2.parent()
        if G.has_coerce_map_from(G2):
            p2 = G(p2)
        elif G2.has_coerce_map_from(G):
            G = G2
            p1 = G(p1)
        else:
            from sage.groups.perm_gps.all import PermutationGroup
            G = PermutationGroup([p1,p2])
            p1 = G(p1)
            p2 = G(p2)

    M = G.identity()
    p = [p1, p2]
    m = [p1.order(),p2.order()]

    for i,j in w:
        M *= p[i]**(j%m[i])

    return M

def equalize_perms(l):
    r"""
    Transform a list of lists into a list of lists with identical length. Each list
    ``p`` in the argument is completed with ``range(len(p),n)`` where ``n`` is
    the maximal length of the lists in ``l``.

    EXAMPLES::

        sage: from sage.modular.arithgroup.arithgroup_perm import equalize_perms
        sage: l = [[],[1,0],[3,0,1,2]]
        sage: equalize_perms(l)
        sage: l
        [[0, 1, 2, 3], [1, 0, 2, 3], [3, 0, 1, 2]]
    """
    n=max(map(len,l))
    if n ==0:
        n = 1
    for p in l:
        p.extend(xrange(len(p),n))


def ArithmeticSubgroup_Permutation(
        S2=None, S3=None, L=None, R=None,
        relabel=False,
        check=True):
    r"""
    Generate a subgroup of `{\rm SL}_2(\ZZ)` from the action of generators on its
    right cosets.

    Return an arithmetic subgroup knowing the action, given by permutations, of
    at least two standard generators on the its cosets. The generators
    considered are the following matrices

    .. math::

        s_2 = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix},\quad
        s_3 = \begin{pmatrix} 0 & 1 \\ -1 & 1 \end{pmatrix},\quad
        l = \begin{pmatrix} 1 & 1 \\ 0 & 1\end{pmatrix},\quad
        r = \begin{pmatrix} 1 & 0 \\ 1 & 1 \end{pmatrix}.

    INPUT:

    - ``S2``, ``S3``, ``L``, ``R`` - permutations - action of matrices on the
      right cosets (each coset is identified to an element of `\{1,\dots,n\}`
      where `1` is reserved for the identity coset).

    - ``relabel`` - boolean (default: False) - if True, renumber the cosets in a
      canonical way.

    - ``check`` - boolean (default: True) - check that the input is valid (it
      may be time efficient but less safer to set it to False)

    EXAMPLES::

        sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)(3,4)",S3="(1,2,3)")
        sage: G
        Arithmetic subgroup with permutations of right cosets
         S2=(1,2)(3,4)
         S3=(1,2,3)
         L=(1,4,3)
         R=(2,4,3)
        sage: G.index()
        4

        sage: ArithmeticSubgroup_Permutation()
        Arithmetic subgroup with permutations of right cosets
         S2=()
         S3=()
         L=()
         R=()
    """
    gens = filter(lambda x: x is not None, [S2,S3,L,R])
    if len(gens) == 0:
        S2 = S3 = L = R = ''
    elif len(gens) < 2:
        raise ValueError, "need at least two generators"

    if check:
        from sage.groups.perm_gps.all import PermutationGroup

        G = PermutationGroup(gens)
        if not G.is_transitive():
            raise ValueError, "the group is not transitive"

    if S2 is not None:
        S2 = PermutationGroupElement(S2,check=check)
    if S3 is not None:
        S3 = PermutationGroupElement(S3,check=check)
    if L is not None:
        L = PermutationGroupElement(L,check=check)
    if R is not None:
        R = PermutationGroupElement(R,check=check)

    if L is not None:
        if R is not None: # initialize from L,R
            if S2 is None:
                S2 = R * ~L * R
            if S3 is None:
                S3 = L * ~R
        elif S2 is not None: # initialize from L,S2
            if S3 is None:
                S3 =  ~S2 * ~L
            if R is None:
                R = ~S2 * ~L * S2
        elif S3 is not None: # initialize from L,S3
            if S2 is None:
                S2 = ~L * ~S3
            if R is None:
                R = S3 * ~L * ~S3
    elif R is not None:
        if S2 is not None: # initialize from R, S2
            if L is None:
                L = ~S2 * ~R * S2
            if S3 is None:
                S3 = R * ~S2
        elif S3 is not None: # initialize from R, S3
            if L is None:
                L = ~S3 * ~R * S3
            if S2 is None:
                S2 = ~S3 * R
    else: # intialize from S2, S3
        if L is None:
            L = ~S3 * ~S2
        if R is None:
            R = S3 * S2

    if check and (L != ~S3 * ~S2 or R != S3 * S2):
        raise ValueError, "wrong relations between generators"

    inv = S2*S2
    if check and (inv != S3*S3*S3):
        raise ValueError, "S2^2 does not equal to S3^3"

    s2 = [i-1 for i in S2.list()]
    s3 = [i-1 for i in S3.list()]
    l = [i-1 for i in L.list()]
    r = [i-1 for i in R.list()]
    equalize_perms((s2,s3,l,r))

    if inv.is_one(): # the group is even
        G = EvenArithmeticSubgroup_Permutation(s2,s3,l,r)
    else:
        if (not check) or (inv.order() == 2 and inv in G.center()): # the group is odd
            G = OddArithmeticSubgroup_Permutation(s2,s3,l,r)
        else:
             raise ValueError, "wrong relations between generators"

    if relabel:
        G.relabel()

    return G

class ArithmeticSubgroup_Permutation_class(ArithmeticSubgroup):
    r"""
    A subgroup of `{\rm SL}_2(\ZZ)` defined by the action of generators on its
    coset graph.

    The class stores the action of generators `s_2`,`s_3`,`l`,`r` on right cosets
    `Hg` of a finite index subgroup `H < {\rm SL}_2(\ZZ)`. In particular the action of
    `{\rm SL}_2(\ZZ)` on the cosets is on right.

    .. MATH::

        s_2 = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix},\quad
        s_3 = \begin{pmatrix} 0 & 1 \\ -1 & 1 \end{pmatrix},\quad
        l = \begin{pmatrix} 1 & 1 \\ 0 & 1\end{pmatrix},\quad
        r = \begin{pmatrix} 1 & 0 \\ 1 & 1 \end{pmatrix}.

    TEST::

        sage: s2 = PermutationGroupElement('(1,2)(3,4)(5,6)')
        sage: s3 = PermutationGroupElement('(1,3,5)(2,4,6)')
        sage: G = ArithmeticSubgroup_Permutation(S2=s2, S3=s3)
        sage: G.S2() == s2
        True
        sage: G.S3() == s3
        True
        sage: G == ArithmeticSubgroup_Permutation(L=G.L(), R=G.R())
        True
        sage: G == ArithmeticSubgroup_Permutation(L=G.L(), S2=G.S2())
        True
        sage: G == ArithmeticSubgroup_Permutation(L=G.L(), S3=G.S3())
        True
        sage: G == ArithmeticSubgroup_Permutation(R=G.R(), S2=G.S2())
        True
        sage: G == ArithmeticSubgroup_Permutation(R=G.R(), S3=G.S3())
        True
        sage: G == ArithmeticSubgroup_Permutation(S2=G.S2(), S3=G.S3())
        True

        sage: G = ArithmeticSubgroup_Permutation(S2='',S3='')
        sage: G == loads(dumps(G))
        True

        sage: S2 = '(1,2)(3,4)(5,6)'
        sage: S3 = '(1,2,3)(4,5,6)'
        sage: G = ArithmeticSubgroup_Permutation(S2=S2, S3=S3)
        sage: loads(dumps(G)) == G
        True
    """
    def __eq__(self, other):
        r"""
        Equality test.

        TESTS::

            sage: G2 = Gamma(2)
            sage: G3 = Gamma(3)
            sage: H = ArithmeticSubgroup_Permutation(S2="(1,4)(2,6)(3,5)",S3="(1,2,3)(4,5,6)")
            sage: (G2 == H) and (H == G2)
            True
            sage: (G3 == H) or (H == G3)
            False

            sage: G2 = Gamma1(2)
            sage: G3 = Gamma1(3)
            sage: H = ArithmeticSubgroup_Permutation(S2="(1,6,4,3)(2,7,5,8)",S3="(1,2,3,4,5,6)(7,8)")
            sage: (G2 == H) or (H == G2)
            False
            sage: (G3 == H) and (H == G3)
            True
        """
        if isinstance(other, ArithmeticSubgroup_Permutation_class):
            return (self.is_odd() == other.is_odd() and
                    self.index() == other.index() and
                    self.relabel(inplace=False)._S2 == other.relabel(inplace=False)._S2 and
                    self.relabel(inplace=False)._S3 == other.relabel(inplace=False)._S3)

        elif isinstance(other, ArithmeticSubgroup):
            return self == other.as_permutation_group()

        else:
            raise NotImplemented

    def _repr_(self):
        r"""
        String representation of self.

        EXAMPLES::

            sage: G = Gamma(2).as_permutation_group()
            sage: repr(G) #indirect doctest
            'Arithmetic subgroup with permutations of right cosets\n S2=(1,4)(2,6)(3,5)\n S3=(1,2,3)(4,5,6)\n L=(1,5)(2,4)(3,6)\n R=(1,6)(2,5)(3,4)'
            sage: G = Gamma(3).as_permutation_group()
            sage: repr(G) #indirect doctest
            'Arithmetic subgroup of index 24'
        """
        if self.index() < 20:
            return "Arithmetic subgroup with permutations of right cosets\n S2=%s\n S3=%s\n L=%s\n R=%s" %(
                self.S2(), self.S3(), self.L(), self.R())

        else:
            return "Arithmetic subgroup of index %d" %self.index()

    #
    # Attribute access
    #

    def S2(self):
        r"""
        Return the action of the matrix `s_2` as a permutation of cosets.

        .. MATH::

            s_2 = \begin{pmatrix}0&-1\\1&0\end{pmatrix}

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)",S3="(1,2,3)")
            sage: G.S2()
            (1,2)
        """
        return PermutationGroupElement([i+1 for i in self._S2], check=False)

    def S3(self):
        r"""
        Return the action of the matrix `s_3` as a permutation of cosets.

        .. MATH::

           s_3 = \begin{pmatrix} 0 & 1 \\ -1 & 1 \end{pmatrix},\quad

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)",S3="(1,2,3)")
            sage: G.S3()
            (1,2,3)
        """

        return PermutationGroupElement([i+1 for i in self._S3], check=False)

    def L(self):
        r"""
        Return the action of the matrix `l` as a permutation of cosets.

        .. MATH::

            l = \begin{pmatrix}1&1\\0&1\end{pmatrix}

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)",S3="(1,2,3)")
            sage: G.L()
            (1,3)
        """
        return PermutationGroupElement([i+1 for i in self._L], check=False)

    def R(self):
        r"""
        Return the action of the matrix `r` as a permutation of cosets.

        .. MATH::

            r = \begin{pmatrix}1&0\\1&1\end{pmatrix}

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)",S3="(1,2,3)")
            sage: G.R()
            (2,3)
        """
        return PermutationGroupElement([i+1 for i in self._R], check=False)

    def perm_group(self):
        r"""
        Return the underlying permutation group.

        The permutation group returned is isomorphic to the action of the
        generators `s_2` (element of order two), `s_3` (element of order 3), `l`
        (parabolic element) and `r` (parabolic element) on right cosets (the
        action is on the right).

        EXAMPLE::

            sage: import sage.modular.arithgroup.arithgroup_perm as ap
            sage: ap.HsuExample10().perm_group()
            Permutation Group with generators [(1,2)(3,4)(5,6)(7,8)(9,10), (1,4)(2,5,9,10,8)(3,7,6), (1,7,9,10,6)(2,3)(4,5,8), (1,8,3)(2,4,6)(5,7,10)]
        """
        from sage.groups.perm_gps.all import PermutationGroup
        return PermutationGroup([self.S2(), self.S3(), self.L(), self.R()])

    def index(self):
        r"""
        Returns the index of this modular subgroup in the full modular group.

        EXAMPLES::

            sage: G = Gamma(2)
            sage: P = G.as_permutation_group()
            sage: P.index()
            6
            sage: G.index() == P.index()
            True

            sage: G = Gamma0(8)
            sage: P = G.as_permutation_group()
            sage: P.index()
            12
            sage: G.index() == P.index()
            True

            sage: G = Gamma1(6)
            sage: P = G.as_permutation_group()
            sage: P.index()
            24
            sage: G.index() == P.index()
            True
        """
        return len(self._S2)

    #
    # Canonical renumbering
    #

    def relabel(self, inplace=True):
        r"""
        Relabel the cosets of this modular subgroup in a canonical way.

        The implementation of modular subgroup by action of generators on cosets
        depends on the choice of a numbering. This function provides
        canonical labels in the sense that two equal subgroups whith different
        labels are relabeled the same way. The default implementation relabels
        the group itself. If you want to get a relabeled copy of your modular
        subgroup, put to ``False`` the option ``inplace``.

        ALGORITHM:

        We give an overview of how the canonical labels for the modular subgroup
        are built. The procedure only uses the permutations `S3` and `S2` that
        define the modular subgroup and can be used to renumber any
        transitive action of the symmetric group. In other words, the algorithm
        construct a canonical representative of a transitive subgroup in its
        conjugacy class in the full symmetric group.

        1. The identity is still numbered `0` and set the curent vertex to be
        the identity.

        2. Number the cycle of `S3` the current vertex belongs to: if the
        current vertex is labeled `n` then the numbering in such way that the
        cycle becomes `(n, n+1, \ldots, n+k)`).

        3. Find a new current vertex using the permutation `S2`.
        If all vertices are relabeled then it's done, otherwise go to step 2.

        EXAMPLES::

            sage: S2 = "(1,2)(3,4)(5,6)"; S3 = "(1,2,3)(4,5,6)"
            sage: G1 = ArithmeticSubgroup_Permutation(S2=S2,S3=S3); G1
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,4)(5,6)
             S3=(1,2,3)(4,5,6)
             L=(1,4,5,3)
             R=(2,4,6,3)
            sage: G1.relabel(); G1
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,4)(5,6)
             S3=(1,2,3)(4,5,6)
             L=(1,4,5,3)
             R=(2,4,6,3)

            sage: S2 = "(1,2)(3,5)(4,6)"; S3 = "(1,2,3)(4,5,6)"
            sage: G2 = ArithmeticSubgroup_Permutation(S2=S2,S3=S3); G2
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,5)(4,6)
             S3=(1,2,3)(4,5,6)
             L=(1,5,6,3)
             R=(2,5,4,3)
            sage: G2.relabel(); G2
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,4)(5,6)
             S3=(1,2,3)(4,5,6)
             L=(1,4,5,3)
             R=(2,4,6,3)

            sage: S2 = "(1,2)(3,6)(4,5)"; S3 = "(1,2,3)(4,5,6)"
            sage: G3 = ArithmeticSubgroup_Permutation(S2=S2,S3=S3); G3
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,6)(4,5)
             S3=(1,2,3)(4,5,6)
             L=(1,6,4,3)
             R=(2,6,5,3)
            sage: G4 = G3.relabel(inplace=False)
            sage: G4
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,4)(5,6)
             S3=(1,2,3)(4,5,6)
             L=(1,4,5,3)
             R=(2,4,6,3)
            sage: G3 is G4
            False

        TESTS::

            sage: S2 = "(1,2)(3,6)(4,5)"
            sage: S3 = "(1,2,3)(4,5,6)"
            sage: G = ArithmeticSubgroup_Permutation(S2=S2,S3=S3)
            sage: H = G.relabel(inplace=False)
            sage: G is H
            False
            sage: G._S2 is H._S2 or G._S3 is H._S3 or G._L is H._L or G._R is H._R
            False
            sage: G.relabel(inplace=False) is H
            True
            sage: H.relabel(inplace=False) is H
            True
            sage: G.relabel(); G
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,4)(5,6)
             S3=(1,2,3)(4,5,6)
             L=(1,4,5,3)
             R=(2,4,6,3)
            sage: G.relabel(inplace=False) is G
            True
        """
        if hasattr(self,'_canonical_label_group'):
            if inplace:
                if not (self is self._canonical_label_group):
                    self.__dict__ = self._canonical_label_group.__dict__
                    self._canonical_label_group = self
            else:
                return self._canonical_label_group

        if inplace:
            G = self
        else:
            from copy import deepcopy
            G = deepcopy(self)

        n = G.index()
        mapping = G._canonical_rooted_labels()
        S2 = G._S2
        S3 = G._S3
        L = G._L
        R = G._R
        G._S2 = [None]*n
        G._S3 = [None]*n
        G._L = [None]*n
        G._R = [None]*n

        for i in xrange(n):
            G._S2[mapping[i]] = mapping[S2[i]]
            G._S3[mapping[i]] = mapping[S3[i]]
            G._L[mapping[i]] = mapping[L[i]]
            G._R[mapping[i]] = mapping[R[i]]

        self._canonical_label_group = G
        G._canonical_label_group = G

        if not inplace:
            return G

    def _canonical_unrooted_labels(self):
        r"""
        Returns the smallest label among rooted label

        OUTPUT:

        A 3-tuple of lists corresponding to permutations. The first list is the
        mapping that gives the canonical labels and the second and third one
        correspond to the permutations obtained by the conjugation of ``S2`` and
        ``S3``.

        EXAMPLES::

            sage: S2 = "(1,2)(4,5)"
            sage: S3 = "(1,3,4)(2,5,6)"
            sage: G = ArithmeticSubgroup_Permutation(S2=S2,S3=S3)
            sage: s2,s3 = G._S2,G._S3
            sage: m,ss2,ss3 = G._canonical_unrooted_labels()
            sage: all(ss2[m[i]] == m[s2[i]] for i in xrange(6))
            True
            sage: all(ss3[m[i]] == m[s3[i]] for i in xrange(6))
            True

            sage: S2 = "(1,2)(3,4)(5,6)"
            sage: S3 = "(1,3,4)(2,5,6)"
            sage: G = ArithmeticSubgroup_Permutation(S2=S2,S3=S3)
            sage: s2,s3 = G._S2,G._S3
            sage: m,ss2,ss3 = G._canonical_unrooted_labels()
            sage: all(ss2[m[i]] == m[s2[i]] for i in xrange(6))
            True
            sage: all(ss3[m[i]] == m[s3[i]] for i in xrange(6))
            True

            sage: S2 = "(1,2)(3,4)(5,6)"
            sage: S3 = "(1,3,5)(2,4,6)"
            sage: G = ArithmeticSubgroup_Permutation(S2=S2,S3=S3)
            sage: s2,s3 = G._S2,G._S3
            sage: m,ss2,ss3 = G._canonical_unrooted_labels()
            sage: all(ss2[m[i]] == m[s2[i]] for i in xrange(6))
            True
            sage: all(ss3[m[i]] == m[s3[i]] for i in xrange(6))
            True
        """
        n = self.index()
        S2_win = [None]*n;  S3_win = [None]*n
        S2_test = [None]*n; S3_test = [None]*n

        m_win = self._canonical_rooted_labels(0)
        for i in xrange(n): # conjugation
            S2_win[m_win[i]] = m_win[self._S2[i]]
            S3_win[m_win[i]] = m_win[self._S3[i]]

        for j0 in xrange(1,self.index()):
            m_test = self._canonical_rooted_labels(j0)
            for i in xrange(n):
                S2_test[m_test[i]] = m_test[self._S2[i]]
                S3_test[m_test[i]] = m_test[self._S3[i]]

            for i in xrange(n-1):
                if (S2_test[i] < S2_win[i] or
                    (S2_test[i] == S2_win[i] and S3_test[i] < S3_win[i])):
                    S2_win,S2_test = S2_test,S2_win
                    S3_win,S3_test = S3_test,S3_win
                    m_win = m_test
                    break

        return m_win, S2_win, S3_win

    def _canonical_rooted_labels(self, j0=0):
        r"""
        Return the permutation which correspond to the renumbering of self in
        order to get canonical labels.

        If ``j0`` is 0 then the renumbering corresponds to the same group. If
        not, the renumbering corresponds to the conjugated subgroup such that
        ``j0`` becomes the identity coset.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)",S3="(1,2,3)")
            sage: G._canonical_rooted_labels(0)
            [0, 1, 2]
            sage: G._canonical_rooted_labels(1)
            [2, 0, 1]
            sage: G._canonical_rooted_labels(2)
            [1, 2, 0]
        """
        x = self._S3
        y = self._S2
        n = len(x)

        k = 0
        seen = [True] * n
        mapping = [None] * n
        waiting = []

        while True:
            # intialize at j0
            mapping[j0] = k
            waiting.append(j0)
            k += 1
            # complete x cycle from j0
            j = x[j0]
            while j != j0:
                mapping[j] = k
                waiting.append(j)
                k += 1
                j = x[j]

            # if everybody is labelled do not go further
            if k == n: break

            # find another guy with y
            j0 = y[waiting.pop(0)]
            while mapping[j0] is not None:
                j0 = y[waiting.pop(0)]

        return mapping

    #
    # Contains and random element
    #

    @cached_method
    def _index_to_lr_cusp_width(self):
        r"""
        Precomputation of cusps data of self for this modular subgroup.

        This is a central precomputation for the ``.__contains__()`` method and
        consists in two lists  of positive integers ``lc`` and ``rc`` of length
        the index of the subgroup. They are defined as follows: the number
        ``lc[i]`` (resp ``rc[i]``) is the lenth of the cycle of ``L`` (resp.
        ``R``) which contains ``i``.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)",S3="(1,2,3)")
            sage: G.L()
            (1,3)
            sage: G.R()
            (2,3)
            sage: G._index_to_lr_cusp_width()
            ([2, 1, 2], [1, 2, 2])
        """
        G = self.relabel(inplace=False)

        l = G.L()
        l_cycle_length = [None]*self.index()
        for c in l.cycle_tuples(singletons=True):
            for i in c:
                l_cycle_length[i-1]=len(c)

        r = G.R()
        r_cycle_length = [None]*self.index()
        for c in r.cycle_tuples(singletons=True):
            for i in c:
                r_cycle_length[i-1]=len(c)

        return (l_cycle_length, r_cycle_length)

    def __contains__(self, x):
        r"""
        Test whether ``x`` is in the group or not.

        ALGORITHM:

        An element of `{\rm SL}_2(\ZZ)` is in a given modular subgroup if it does not
        permute the identity coset!

        TEST::

            sage: G = Gamma(4)
            sage: m1 = G([1,4,0,1])
            sage: m2 = G([17,4,4,1])
            sage: m3 = G([1,-4,-4,17])
            sage: m4 = SL2Z([1,2,0,1])
            sage: P = G.as_permutation_group()
            sage: m1 in P
            True
            sage: m2 in P
            True
            sage: m3 in P
            True
            sage: m4 in P
            False
        """
        if x.parent() is self or x.parent() == self: return True
        if x not in SL2Z: return False

        w = sl2z_word_problem(x)

        perms = [self.relabel(inplace=False)._L,self.relabel(inplace=False)._R]
        widths = self._index_to_lr_cusp_width()

        k = 0
        for (i,j) in w:
            for _ in xrange(j % widths[i][k]):
                k = perms[i][k]

        return not k

    def random_element(self, initial_steps=30):
        r"""
        Returns a random element in this subgroup.

        The algorithm uses a random walk on the Cayley graph of `{\rm SL}_2(\ZZ)` stopped
        at the first time it reaches the subgroup after at least
        ``initial_steps`` steps.

        INPUT:

        - ``initial_steps`` - positive integer (default: 30)

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2='(1,3)(4,5)',S3='(1,2,5)(3,4,6)')
            sage: all(G.random_element() in G for _ in xrange(10))
            True
        """
        from sage.misc.prandom import randint

        i = 0
        m = SL2Z(1)
        for _ in xrange(initial_steps):
            j = randint(0,1)
            if j == 0:
                i = self._S2[i]
                m = m*S2m
            else:
                i = self._S3[i]
                m = m*S3m

        while i != 0:
            j = randint(0,1)
            if j == 0:
                i = self._S2[i]
                m = m*S2m
            else:
                i = self._S3[i]
                m = m*S3m

        return m

    def permutation_action(self, x):
        r"""
        Given an element ``x`` of `{\rm SL}_2(\ZZ)`, compute the permutation of the
        cosets of self given by right multiplication by ``x``.

        EXAMPLE::

            sage: import sage.modular.arithgroup.arithgroup_perm as ap
            sage: ap.HsuExample10().permutation_action(SL2Z([32, -21, -67, 44]))
            (1,4,6,2,10,5,3,7,8,9)
        """
        return word_of_perms(sl2z_word_problem(x), self.L(), self.R())

    def __call__(self, g, check=True):
        r"""
        Create an element of this group from ``g``. If check=True (the default),
        perform the (possibly rather computationally-intensive) check to make
        sure ``g`` is in this group.

        EXAMPLE::

            sage: import sage.modular.arithgroup.arithgroup_perm as ap
            sage: m = SL2Z([1,1,0,1])
            sage: m in ap.HsuExample10()
            False
            sage: ap.HsuExample10()(m)
            Traceback (most recent call last):
            ...
            TypeError: The element is not in group
            sage: ap.HsuExample10()(m, check=False)
            [1 1]
            [0 1]
        """
        g = SL2Z(g)
        if not check or g in self:
            return ArithmeticSubgroupElement(parent=self,x=g,check=check)
        raise TypeError, "The element is not in group"

    #
    # Group stuff
    #

    def is_normal(self):
        r"""
        Test whether the group is normal

        EXAMPLES::

            sage: G = Gamma(2).as_permutation_group()
            sage: G.is_normal()
            True

            sage: G = Gamma1(2).as_permutation_group()
            sage: G.is_normal()
            False
        """
        N = self.index()
        G = self.relabel(inplace=False)
        s2 = G._S2
        s3 = G._S3
        ss2 = [None]*N
        ss3 = [None]*N
        for j in [s2[0],s3[0]]:
            m = G._canonical_rooted_labels(j)
            for i in xrange(N):
                ss2[m[i]] = m[s2[i]]
                ss3[m[i]] = m[s3[i]]
            if s2 != ss2 or s3 != ss3:
                return False
        return True

    def _conjugate(self,j0):
        r"""
        Return the conjugate of self rooted at j0.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2='(1,2)(3,4)',S3='(1,2,3)(4,5,6)')
            sage: G
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,4)
             S3=(1,2,3)(4,5,6)
             L=(1,4,6,5,3)
             R=(2,4,5,6,3)
            sage: G._conjugate(0) == G
            True
            sage: G._conjugate(4)
            Arithmetic subgroup with permutations of right cosets
             S2=(3,4)(5,6)
             S3=(1,2,3)(4,5,6)
             L=(1,4,5,3,2)
             R=(1,2,4,6,3)
        """
        N = self.index()
        s2 = self._S2
        s3 = self._S3
        l = self._L
        r = self._R
        ss2 = [None]*N
        ss3 = [None]*N
        ll = [None]*N
        rr = [None]*N

        m = self._canonical_rooted_labels(j0)
        for i in xrange(N):
            ss2[m[i]] = m[s2[i]]
            ss3[m[i]] = m[s3[i]]
            ll[m[i]] = m[l[i]]
            rr[m[i]] = m[r[i]]
        return self.__class__(ss2,ss3,ll,rr,True)

    def coset_graph(self,
            right_cosets=False,
            s2_edges=True, s3_edges=True, l_edges=False, r_edges=False,
            s2_label='s2', s3_label='s3', l_label='l', r_label='r'):
        r"""
        Return the right (or left) coset graph.

        INPUT:

        - ``right_cosets`` - bool (default: False) - right or left coset graph

        - ``s2_edges`` - bool (default: True) - put edges associated to s2

        - ``s3_edges`` - bool (default: True) - put edges associated to s3

        - ``l_edges`` - bool (default: False) - put edges associated to l

        - ``r_edges`` - bool (default: False) - put edges associated to r

        - ``s2_label``, ``s3_label``, ``l_label``, ``r_label`` - the labels to
          put on the edges corresponding to the generators action. Use ``None``
          for no label.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)",S3="()")
            sage: G
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)
             S3=()
             L=(1,2)
             R=(1,2)
            sage: G.index()
            2
            sage: G.coset_graph()
            Looped multi-digraph on 2 vertices
        """
        from sage.graphs.digraph import DiGraph
        res = DiGraph(multiedges=True,loops=True)
        res.add_vertices(range(self.index()))


        if right_cosets: # invert the permutations
            S2 = [None]*self.index()
            S3 = [None]*self.index()
            L = [None]*self.index()
            R = [None]*self.index()
            for i in xrange(self.index()):
                S2[self._S2[i]] = i
                S3[self._S3[i]] = i
                L[self._L[i]] = i
                R[self._R[i]] = i

        else:
            S2 = self._S2
            S3 = self._S3
            L = self._L
            R = self._R

        if s2_edges:
            if s2_label is not None:
               res.add_edges((i,S2[i],s2_label) for i in xrange(self.index()))
            else:
                res.add_edges((i,S2[i]) for i in xrange(self.index()))

        if s3_edges:
            if s3_label is not None:
                res.add_edges((i,S3[i],s3_label) for i in xrange(self.index()))
            else:
                res.add_edges((i,S3) for i in xrange(self.index()))

        if l_edges:
            if l_label is not None:
                res.add_edges((i,L[i],l_label) for i in xrange(self.index()))
            else:
                res.add_edges((i,L[i]) for i in xrange(self.index()))

        if r_edges:
            if r_label is not None:
                res.add_edges((i,R[i],r_label) for i in xrange(self.index()))
            else:
                res.add_edges((i,R[i]) for i in xrange(self.index()))

        res.plot.options['color_by_label'] = True

        if s2_label or s3_label or l_label or r_label:
            res.plot.options['edge_labels'] = True

        return res

    def generalised_level(self):
        r"""
        Return the generalised level of this subgroup.

        The *generalised level* of a subgroup of the modular group is the least
        common multiple of the widths of the cusps. It was proven by Wohlfart
        that if the subgroup is a congruence subgroup then the (conventional)
        level coincide with the generalised level.

        EXAMPLES::

            sage: G = Gamma(2).as_permutation_group()
            sage: G.generalised_level()
            2
            sage: G = Gamma0(3).as_permutation_group()
            sage: G.generalised_level()
            3
        """
        return arith.lcm(self.cusp_widths())

class OddArithmeticSubgroup_Permutation(ArithmeticSubgroup_Permutation_class):
    def __init__(self, S2, S3, L, R, canonical_labels=False):
        r"""
        TESTS::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2,3,4)",S3="(1,3)(2,4)")
            sage: G
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2,3,4)
             S3=(1,3)(2,4)
             L=(1,2,3,4)
             R=(1,4,3,2)
            sage: loads(dumps(G)) == G
            True
        """
        self._S2 = S2
        self._S3 = S3
        self._L = L
        self._R = R
        if canonical_labels:
            self._canonical_label_group = self

    def __reduce__(self):
        r"""
        Return the data used to construct self. Used in pickling.

        TESTS::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2,3,4)",S3="(1,3)(2,4)")
            sage: G == loads(dumps(G))  #indirect doctest
            True
            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2,3,4)",S3="(1,3)(2,4)",relabel=True)
            sage: GG = loads(dumps(G))
            sage: GG == G #indirect doctest
            True
            sage: GG.relabel(inplace=False) is GG
            True
        """
        if hasattr(self,'_canonical_label_group'):
            canonical_labels = (self is self._canonical_label_group)
        else:
            canonical_labels = False
        return (OddArithmeticSubgroup_Permutation,
                (self._S2,self._S3,self._L,self._R,canonical_labels))

    def is_odd(self):
        r"""
        Test whether the group is odd.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,6,4,3)(2,7,5,8)",S3="(1,2,3,4,5,6)(7,8)")
            sage: G.is_odd()
            True
        """
        return True

    def is_even(self):
        r"""
        Test whether the group is even.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,6,4,3)(2,7,5,8)",S3="(1,2,3,4,5,6)(7,8)")
            sage: G.is_even()
            False
        """
        return False

    def to_even_subgroup(self,relabel=True):
        r"""
        Returns the group with `-Id` added in it.

        EXAMPLES::

            sage: G = Gamma1(3).as_permutation_group()
            sage: G.to_even_subgroup()
            Arithmetic subgroup with permutations of right cosets
             S2=(1,3)(2,4)
             S3=(1,2,3)
             L=(2,3,4)
             R=(1,4,2)
        """
        N = self.index()

        # build equivalence classes in e
        s2 = self._S2
        e = set([])
        for i in xrange(N):
            j = s2[s2[i]]
            if i < j:
                e.add((i,j))

        # build index for equivalence classes
        e2i = [None]*N  # eq. class to index
        for i,(j0,j1) in enumerate(e):
            e2i[j0] = i
            e2i[j1] = i

        # build the quotient permutations
        ss2 = [None]*(N/2)
        ss3 = [None]*(N/2)
        ll = [None]*(N/2)
        rr = [None]*(N/2)

        s3 = self._S3
        l = self._L
        r = self._R
        for (j0,j1) in e:
            ss2[e2i[j0]] = e2i[s2[j0]]
            ss3[e2i[j0]] = e2i[s3[j0]]
            ll[e2i[j0]] = e2i[l[j0]]
            rr[e2i[j0]] = e2i[r[j0]]

        G = EvenArithmeticSubgroup_Permutation(ss2,ss3,ll,rr)
        if relabel:
            G.relabel()
        return G

    def nu2(self):
        r"""
        Return the number of elliptic points of order 2.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2,3,4)",S3="(1,3)(2,4)")
            sage: G.nu2()
            0

            sage: G = Gamma1(2).as_permutation_group()
            sage: G.nu2()
            1
        """
        return sum(1 for c in self.S2().cycle_tuples() if len(c) == 2)

    def nu3(self):
        r"""
        Return the number of elliptic points of order 3.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2,3,4)",S3="(1,3)(2,4)")
            sage: G.nu3()
            2

            sage: G = Gamma1(3).as_permutation_group()
            sage: G.nu3()
            1
        """
        return sum(1 for c in self.S3().cycle_tuples() if len(c) == 2)

    def nirregcusps(self):
        r"""
        Return the number of irregular cusps.

        The cusps are associated to cycles of the permutations `L` or `R`.
        The irregular cusps are the one which are stabilised by `-Id`.

        EXAMPLES::

            sage: S2 = "(1,3,2,4)(5,7,6,8)(9,11,10,12)"
            sage: S3 = "(1,3,5,2,4,6)(7,9,11,8,10,12)"
            sage: G = ArithmeticSubgroup_Permutation(S2=S2,S3=S3)
            sage: G.nirregcusps()
            3
        """
        inv = self.S2()**2
        n = 0
        for c in self.L().cycle_tuples(singletons=True):
            if inv(c[0]) in c:
                n += 1
        return n

    def nregcusps(self):
        r"""
        Return the number of regular cusps of the group.

        The cusps are associated to cycles of `L` or `R`. The irregular cusps
        correspond to the ones which are not stabilised by `-Id`.

        EXAMPLES::

            sage: G = Gamma1(3).as_permutation_group()
            sage: G.nregcusps()
            2
        """
        inv = self.S2()**2
        n = 0
        for c in self.L().cycle_tuples(singletons=True):
            if inv(c[0]) not in c:
                n += 1
        return n//2

    def cusp_widths(self,exp=False):
        r"""
        Return the list of cusp widths.

        INPUT:

        ``exp`` - boolean (default: False) - if True, return a dictionnary with
        keys the possible widths and with values the number of cusp with that
        width.

        EXAMPLES::

            sage: G = Gamma1(5).as_permutation_group()
            sage: G.cusp_widths()
            [1, 1, 5, 5]
            sage: G.cusp_widths(exp=True)
            {1: 2, 5: 2}
        """
        inv = self.S2()**2
        L = self.L()
        cusps = set(c[0] for c in L.cycle_tuples(singletons=True))
        if exp:
            widths = {}
        else:
            widths = []

        while cusps:
            c0 = cusps.pop()
            c = L.orbit(c0)
            if inv(c0) not in c:
                c1 = min(L.orbit(inv(c0)))
                cusps.remove(c1)
                if exp:
                    if not len(c) in widths:
                        widths[len(c)] = 0
                    widths[len(c)] += 1
                else:
                    widths.append(len(c))
            else:
                if exp:
                    if not len(c)/2 in widths:
                        widths[len(c)/2] = 0
                    widths[len(c)/2] += 1
                else:
                    widths.append(len(c)/2)

        if exp:
            return widths
        return sorted(widths)

    def ncusps(self):
        r"""
        Returns the number of cusps.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2,3,4)",S3="(1,3)(2,4)")
            sage: G.ncusps()
            1

            sage: G = Gamma1(3).as_permutation_group()
            sage: G.ncusps()
            2
        """
        inv = self.S2()**2
        n = 0
        m = 0
        for c in self.L().cycle_tuples(singletons=True):
            if inv(c[0]) in c:
                n += 1
            else:
                m += 1
        return n + m//2

    def is_congruence(self):
        r"""
        Test whether self is a congruence group.

        An odd group is *congruence* if, when we add to it the element `-Id` it
        contains a congruence subgroup `\Gamma(n)` for a certain `n`.

        EXAMPLES::

            sage: S2 = '(1,6,4,3)(2,7,5,10)(8,9,11,12)'
            sage: S3 = '(1,2,3,4,5,6)(7,8,9,10,11,12)'
            sage: G = ArithmeticSubgroup_Permutation(S2=S2,S3=S3); G
            Arithmetic subgroup with permutations of right cosets
             S2=(1,6,4,3)(2,7,5,10)(8,9,11,12)
             S3=(1,2,3,4,5,6)(7,8,9,10,11,12)
             L=(2,3,10,8)(5,6,7,11)(9,12)
             R=(1,7,9,2)(4,10,12,5)(8,11)
            sage: G.is_congruence()
            True
        """
        return self.to_even_subgroup().is_congruence()

class EvenArithmeticSubgroup_Permutation(ArithmeticSubgroup_Permutation_class):
    r"""
    An arithmetic subgroup `\Gamma` defined by two permutations, giving the
    action of four standard generators

    .. MATH::

        s_2 = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix},\quad
        s_3 = \begin{pmatrix} 0 & 1 \\ -1 & 1 \end{pmatrix},\quad
        l = \begin{pmatrix} 1 & 1 \\ 0 & 1\end{pmatrix},\quad
        r = \begin{pmatrix} 1 & 0 \\ 1 & 1 \end{pmatrix}.

    by right multiplication on the coset representatives `\Gamma \backslash {\rm SL}_2(\ZZ)`.


    EXAMPLES:

    Construct a noncongruence subgroup of index 7 (the smallest possible)::

        sage: a2 = SymmetricGroup(7)([(1,2),(3,4),(6,7)]); a3 = SymmetricGroup(7)([(1,2,3),(4,5,6)])
        sage: G = ArithmeticSubgroup_Permutation(S2=a2, S3=a3); G
        Arithmetic subgroup with permutations of right cosets
        S2=(1,2)(3,4)(6,7)
        S3=(1,2,3)(4,5,6)
        L=(1,4,7,6,5,3)
        R=(2,4,5,7,6,3)
        sage: G.index()
        7
        sage: G.dimension_cusp_forms(4)
        1
        sage: G.is_congruence()
        False

    Convert some standard congruence subgroups into permutation form::

        sage: G = Gamma0(8).as_permutation_group()
        sage: G.index()
        12
        sage: G.is_congruence()
        True

        sage: G = Gamma0(12).as_permutation_group()
        sage: print G
        Arithmetic subgroup of index 24
        sage: G.is_congruence()
        True

    The following is the unique index 2 even subgroup of `{\rm SL}_2(\ZZ)`::

        sage: w = SymmetricGroup(2)([2,1])
        sage: G = ArithmeticSubgroup_Permutation(L=w, R=w)
        sage: G.dimension_cusp_forms(6)
        1
        sage: G.genus()
        0
    """
    def __init__(self, S2, S3, L, R, canonical_labels=False):
        r"""
        TESTS::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)(3,4)(5,6)",S3="(1,2,3)(4,5,6)")
            sage: G == loads(dumps(G))
            True
            sage: G is loads(dumps(G))
            False
        """
        self._S2 = S2
        self._S3 = S3
        self._L = L
        self._R = R
        if canonical_labels:
            self._canonical_label_group = self

    def __reduce__(self):
        r"""
        Data for pickling.

        TESTS::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)(3,4)",S3="(1,2,4)")
            sage: G == loads(dumps(G)) #indirect doctest
            True
            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)(3,4)",S3="(1,2,4)",relabel=True)
            sage: GG = loads(dumps(G))
            sage: G == GG #indirect doctest
            True
            sage: GG.relabel(inplace=False) is GG
            True
        """
        if hasattr(self, '_canonical_label_group'):
            canonical_labels = (self is self._canonical_label_group)
        else:
            canonical_labels = False
        return (EvenArithmeticSubgroup_Permutation,
                (self._S2, self._S3, self._L, self._R, canonical_labels))

    def is_odd(self):
        r"""
        Returns True if this subgroup does not contain the matrix `-Id`.

        EXAMPLES::

            sage: G = Gamma(2).as_permutation_group()
            sage: G.is_odd()
            False
        """
        return False

    def is_even(self):
        r"""
        Returns True if this subgroup contains the matrix `-Id`.

        EXAMPLES::

            sage: G = Gamma(2).as_permutation_group()
            sage: G.is_even()
            True
        """
        return True

    def nu2(self):
        r"""
        Returns the number of orbits of elliptic points of order 2 for this
        arithmetic subgroup.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,4)(2)(3)",S3="(1,2,3)(4)")
            sage: G.nu2()
            2
        """
        return sum(1 for i in xrange(self.index()) if self._S2[i] == i)

    def nu3(self):
        r"""
        Returns the number of orbits of elliptic points of order 3 for this
        arithmetic subgroup.

        EXAMPLES::
            sage: G = ArithmeticSubgroup_Permutation(S2="(1,4)(2)(3)",S3="(1,2,3)(4)")
            sage: G.nu3()
            1
        """
        return sum(1 for i in xrange(self.index()) if self._S3[i] == i)

    def ncusps(self):
        r"""
        Return the number of cusps of this arithmetic subgroup.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)(3,4)(5,6)",S3="(1,2,3)(4,5,6)")
            sage: G.ncusps()
            3
        """
        return len(self.L().cycle_tuples(True))

    def _spanning_tree_kulkarni(self, root=0, on_right=True):
        r"""
        Returns a spanning tree for the coset graph of the group for the
        generators `S2` and `S3`.

        Warning: the output is randomized in order to be able to obtain any
        spanning tree of the coset graph. The algorithm mainly follows
        Kulkarni's paper.

        INPUT:

        - ``on_right`` - boolean (default: True) - if False, return spanning
          tree for the left cosets.

        OUTPUT:

        - ``tree`` - a spanning tree of the graph associated to the action of
          ``L`` and ``S2`` on the cosets

        - ``reps`` - list of matrices in `{\rm SL}_2(\ZZ)`` - representatives of the
          cosets with respect to the spanning tree

        - ``word_reps`` - list of lists with ``s2`` and ``s3`` - word
          representatives of the cosets with respect to the spanning tree.

        - ``gens`` - list of 3-tuples ``(in,out,label)`` - the list of edges in
          the graph which are not in the spanning tree.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2='(1,2)(3,4)',S3='(1,2,3)')
            sage: tree,reps,wreps,gens = G._spanning_tree_kulkarni()
            sage: tree
            Digraph on 4 vertices
            sage: for m in reps: print m,"\n****"
            [1 0]
            [0 1]
            ****
            [ 0  1]
            [-1  1]
            ****
            [-1  1]
            [-1  0]
            ****
            [1 1]
            [0 1]
            ****
            sage: for w in wreps: print ','.join(w)
            <BLANKLINE>
            s3
            s3,s3
            s3,s3,s2
            sage: gens
            [(0, 1, 's2'), (3, 3, 's3')]
        """
        from sage.graphs.digraph import DiGraph
        from sage.misc.prandom import randint

        N = len(self._S2)

        if on_right:
            s2 = self._S2
            s3 = self._S3

        else:
            s2 = [None] * N
            s3 = [None] * N
            for i in xrange(N):
                s2[self._S2[i]] = i
                s3[self._S3[i]] = i

        # the tree and the lift
        tree = DiGraph(multiedges=False,loops=False)
        gens = []

        reps = [None]*self.index()
        word_reps = [None]*self.index()
        reps[root] = SL2Z(1)
        word_reps[root] = []

        x0 = root
        tree.add_vertex(x0)
        l = [x0]

        while True:
            # complete the current 3-loop in the tree
            if s3[x0] != x0: # loop of length 3
                x1 = s3[x0]
                x2 = s3[x1]
                tree.add_edge(x0,x1,'s3')
                tree.add_edge(x1,x2,'s3')
                if on_right:
                    reps[x1] = reps[x0] * S3m
                    reps[x2] = reps[x1] * S3m
                    word_reps[x1] = word_reps[x0] + ['s3']
                    word_reps[x2] = word_reps[x1] + ['s3']
                else:
                    reps[x1] = S3m * reps[x0]
                    reps[x2] = S3m * reps[x1]
                    word_reps[x1] = ['s3'] + word_reps[x0]
                    word_reps[x2] = ['s3'] + word_reps[x1]
                l.append(x1)
                l.append(x2)
            else: # elliptic generator
                gens.append((x0,x0,'s3'))

            # now perform links with s while we find another guy
            while l:
                x1 = l.pop(randint(0,len(l)-1))
                x0 = s2[x1]

                if x1 != x0: # loop of length 2
                    if x0 in tree:
                        gens.append((x1,x0,'s2'))
                        del l[l.index(x0)] # x0 must be in l
                    else:
                        tree.add_edge(x1,x0,'s2')
                        if on_right:
                            reps[x0] = reps[x1] * S2m
                            word_reps[x0] = word_reps[x1] + ['s2']
                        else:
                            reps[x0] = S2m * reps[x1]
                            word_reps[x0] = ['s2'] + word_reps[x1]
                        break
                else: # elliptic generator
                    gens.append((x1,x1,'s2'))

            else:
                break

        return tree,reps,word_reps,gens

    def _spanning_tree_verrill(self, root=0, on_right=True):
        r"""
        Returns a spanning tree with generators `S2` and `L`.

        The algorithm follows the one of Helena Verrill.

        OUTPUT:

        - ``tree`` - a spanning tree of the graph associated to the action of
          ``L`` and ``S2`` on the cosets

        - ``reps`` - list of matrices in `{\rm SL}_2(\ZZ)` - representatives of the
          cosets with respect to the spanning tree

        - ``word_reps`` - list of string with ``s`` and ``l`` - word
          representatives of the cosets with respect to the spanning tree.

        - ``gens`` - list of 3-tuples ``(in,out,label)`` - the list of edges in
          the graph which are not in the spanning tree.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2='(1,2)(3,4)',S3='(1,2,3)')
            sage: tree,reps,wreps,gens=G._spanning_tree_verrill()
            sage: tree
            Digraph on 4 vertices
            sage: for m in reps: print m, "\n****"
            [1 0]
            [0 1]
            ****
            [ 0 -1]
            [ 1  0]
            ****
            [1 2]
            [0 1]
            ****
            [1 1]
            [0 1]
            ****
            sage: wreps
            ['', 's', 'll', 'l']
            sage: gens
            [(2, 0, 'l'), (1, 1, 'l'), (2, 3, 's')]

        TODO:

        Take care of the shape of the spanning tree as in Helena Verrill's program.
        """
        from sage.misc.prandom import randint
        from copy import copy

        if on_right:
            s = self._S2
            l = self._L
        else:
            s = [None]*self.index()
            l = [None]*self.index()
            for i in xrange(self.index()):
                s[self._S2[i]] = i
                l[self._L[i]] = i

        from sage.graphs.digraph import DiGraph
        tree = DiGraph(multiedges=False,loops=False)
        gens = []

        reps = [None]*self.index()
        word_reps = [None]*self.index()
        reps[root] = SL2Z(1)
        word_reps[root] = ''

        x0 = root
        tree.add_vertex(x0)
        waiting = [x0]

        while True:
            # complete the current l-loop in the tree from x0
            x = x0
            xx = l[x]
            while xx != x0:
                tree.add_edge(x,xx,'l')
                if on_right:
                    reps[xx] = reps[x] * Lm
                    word_reps[xx] = word_reps[x] + 'l'
                else:
                    reps[xx] = Lm * reps[x]
                    word_reps[xx] = 'l' + word_reps[x]
                waiting.append(xx)
                x = xx
                xx = l[x]

            gens.append((x,x0,'l'))

            # now perform links with s while we find another guy which will
            # become the new x0
            while waiting:
                x0 = None
                while waiting and x0 is None:
                    x1 = waiting.pop(randint(0,len(waiting)-1))
                    x0 = s[x1]

                if x0 is not None:
                    if x1 != x0: # loop of length 2
                        if x0 in tree:
                            gens.append((x1,x0,'s'))
                            if x0 in waiting:
                                del waiting[waiting.index(x0)] # x0 must be in l
                        else:
                            tree.add_edge(x1,x0,'s')
                            if on_right:
                                reps[x0] = reps[x1] * S2m
                                word_reps[x0] = word_reps[x1] + 's'
                            else:
                                reps[x0] = S2m * reps[x1]
                                word_reps[x0] = 's' + word_reps[x1]
                            break
                    else: # elliptic generator
                        gens.append((x1,x1,'s'))

            else:
                break

        return tree,reps,word_reps,gens

    def todd_coxeter_s2_s3(self):
        r"""
        Returns a 4-tuple ``(coset_reps, gens, s2, s3)`` where ``coset_reps``
        are coset representatives of the subgroup, ``gens`` is a list of
        generators, ``s2`` and ``s3`` are the action of the matrices `S2` and
        `S3` on the list of cosets.

        The so called *Todd-Coxeter algorithm* is a general method for coset
        enumeration for a subgroup of a group given by generators and relations.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2='(1,2)(3,4)',S3='(1,2,3)')
            sage: G.genus()
            0
            sage: reps,gens,s2,s3=G.todd_coxeter_s2_s3()
            sage: g1,g2 = gens
            sage: g1 in G and g2 in G
            True
            sage: g1
            [-1  0]
            [ 1 -1]
            sage: g2
            [-1  3]
            [-1  2]
            sage: S2 = SL2Z([0,-1,1,0])
            sage: S3 = SL2Z([0,1,-1,1])
            sage: reps[0] == SL2Z([1,0,0,1])
            True
            sage: all(reps[i]*S2*~reps[s2[i]] in G for i in xrange(4))
            True
            sage: all(reps[i]*S3*~reps[s3[i]] in G for i in xrange(4))
            True
        """
        tree,reps,wreps,edges = self._spanning_tree_kulkarni()

        gens = []
        for e in edges:
            if e[2] == 's2':
                gens.append(self(reps[e[0]] * S2m * ~reps[e[1]]))
            elif e[2] == 's3':
                gens.append(self(reps[e[0]] * S3m * ~reps[e[1]]))
            else:
                raise ValueError, "this should not happen"

        return reps, gens, self._S2[:], self._S3[:]

    def todd_coxeter_l_s2(self):
        r"""
        Returns a 4-tuple ``(coset_reps, gens, l, s2)`` where ``coset_reps`` is
        a list of coset representatives of the subgroup, ``gens`` a list of
        generators, ``l`` and ``s2`` are list that corresponds to the action of
        the matrix `S2` and `L` on the cosets.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2='(1,2)(3,4)',S3='(1,2,3)')
            sage: reps,gens,l,s=G.todd_coxeter_l_s2()
            sage: reps
            [[1 0]
            [0 1], [ 0 -1]
            [ 1  0], [1 2]
            [0 1], [1 1]
            [0 1]]
            sage: gens
            [[1 3]
            [0 1], [ 1 0]
            [-1  1], [ 2 -3]
            [ 1 -1]]
            sage: l
            [3, 1, 0, 2]
            sage: s
            [1, 0, 3, 2]
            sage: S2 = SL2Z([0,-1,1,0])
            sage: L = SL2Z([1,1,0,1])
            sage: reps[0] == SL2Z([1,0,0,1])
            True
            sage: all(reps[i]*S2*~reps[s[i]] in G for i in xrange(4))
            True
            sage: all(reps[i]*L*~reps[l[i]] in G for i in xrange(4))
            True
        """
        tree,reps,wreps,edges = self._spanning_tree_verrill()

        gens = []
        for e in edges:
            if e[2] == 'l':
                gens.append(self(reps[e[0]] * Lm * ~reps[e[1]]))
            elif e[2] == 's':
                gens.append(self(reps[e[0]] * S2m * ~reps[e[1]]))
            else:
                raise ValueError, "this should not happen"

        return reps, gens, self._L[:], self._S2[:]

    todd_coxeter = todd_coxeter_l_s2

    def coset_reps(self):
        r"""
        Return coset representatives.

        EXAMPLES::

            sage: G = ArithmeticSubgroup_Permutation(S2="(1,2)(3,4)",S3="(1,2,3)")
            sage: c = G.coset_reps()
            sage: len(c)
            4
            sage: [g in G for g in c]
            [True, False, False, False]
        """
        return self.todd_coxeter()[0]

    def cusp_widths(self,exp=False):
        r"""
        Return the list of cusp widths of the group.

        EXAMPLES::

            sage: G = Gamma(2).as_permutation_group()
            sage: G.cusp_widths()
            [2, 2, 2]
            sage: G.cusp_widths(exp=True)
            {2: 3}

            sage: S2 = "(1,2)(3,4)(5,6)"
            sage: S3 = "(1,2,3)(4,5,6)"
            sage: G = ArithmeticSubgroup_Permutation(S2=S2,S3=S3)
            sage: G.cusp_widths()
            [1, 1, 4]
            sage: G.cusp_widths(exp=True)
            {1: 2, 4: 1}

            sage: S2 = "(1,2)(3,4)(5,6)"
            sage: S3 = "(1,3,5)(2,4,6)"
            sage: G = ArithmeticSubgroup_Permutation(S2=S2,S3=S3)
            sage: G.cusp_widths()
            [6]
            sage: G.cusp_widths(exp=True)
            {6: 1}
        """
        seen = [True]*self.index()

        if exp:
            widths = {}
        else:
            widths = []
        for i in xrange(self.index()):
            if seen[i]:
                seen[i] = False
                j = self._L[i]
                n = 1
                while j != i:
                    seen[j] = False
                    n += 1
                    j = self._L[j]
                if exp:
                    if n not in widths:
                        widths[n] = 0
                    widths[n] += 1
                else:
                    widths.append(n)

        if exp:
            return widths
        return sorted(widths)

    def is_congruence(self):
        r"""
        Return True if this is a congruence subgroup.

        ALGORITHM:

        Uses Hsu's algorithm, as implemented by Chris Kurth in KFarey.

        EXAMPLES:

        Test if `{\rm SL}_2(\ZZ)` is congruence::

            sage: a = ArithmeticSubgroup_Permutation(L='',R='')
            sage: a.index()
            1
            sage: a.is_congruence()
            True

        This example is congruence -- it's Gamma0(3) in disguise: ::

            sage: S2 = SymmetricGroup(4)
            sage: l = S2((2,3,4))
            sage: r = S2((1,3,4))
            sage: G = ArithmeticSubgroup_Permutation(L=l,R=r)
            sage: print G
            Arithmetic subgroup with permutations of right cosets
             S2=(1,2)(3,4)
             S3=(1,4,2)
             L=(2,3,4)
             R=(1,3,4)
            sage: G.is_congruence()
            True

        This one is noncongruence: ::

            sage: import sage.modular.arithgroup.arithgroup_perm as ap
            sage: ap.HsuExample10().is_congruence()
            False
        """
        if self.index() == 1:  # the group is SL2Z (trivial case)
            return True

        L = self.L()              # action of L
        R = self.R()              # action of R

        N = L.order() # generalised level of the group

        # write N as N = em where e = 2^k and m odd
        e = 1
        m = N
        while m%2 == 0:
            m //= 2
            e *= 2

        if e==1:     # N is odd
            onehalf = int(~Zmod(N)(2))   #i.e. 2^(-1) mod N
            rel = (R*R*L**(-onehalf))**3
            return rel.is_one()

        elif m==1:     # N is a power of 2
            onefifth=int(~Zmod(N)(5))   #i.e. 5^(-1) mod N
            S=L**20*R**onefifth*L**(-4)*~R

            # congruence if the three below permutations are trivial
            rel=(~L*R*~L) * S * (L*~R*L) * S
            if not rel.is_one():
                return False

            rel=~S*R*S*R**(-25)
            if not rel.is_one():
                return False

            rel=(S*R**5*L*~R*L)**3
            if not rel.is_one():
                return False

            return True

        else:         # e>1, m>1
            onehalf=int(~Zmod(m)(2))    #i.e. 2^(-1)  mod m
            onefifth=int(~Zmod(e)(5))   #i.e. 5^(-1)  mod e
            c=int(~Zmod(m)(e))*e        #i.e. e^(-1)e mod m
            d=int(~Zmod(e)(m))*m        #i.e. m^(-1)m mod e
            a=L**c
            b=R**c
            l=L**d
            r=R**d
            s=l**20*r**onefifth*l**(-4)*~r

            #Congruence if the seven permutations below are trivial:
            rel=~a*~r*a*r
            if not rel.is_one():
                return False

            rel=(a*~b*a)**4
            if not rel.is_one():
                return False

            rel=(a*~b*a)**2*(~a*b)**3
            if not rel.is_one():
                return False

            rel=(a*~b*a)**2*(b*b*a**(-onehalf))**(-3)
            if not rel.is_one():
                return False

            rel=(~l*r*~l)*s*(l*~r*l)*s
            if not rel.is_one():
                return False

            rel=~s*r*s*r**(-25)
            if not rel.is_one():
                return False

            rel=(l*~r*l)**2*(s*r**5*l*~r*l)**(-3)
            if not rel.is_one():
                return False

            return True



def HsuExample10():
    r"""
    An example of an index 10 arithmetic subgroup studied by Tim Hsu.

    EXAMPLE::

        sage: import sage.modular.arithgroup.arithgroup_perm as ap
        sage: ap.HsuExample10()
        Arithmetic subgroup with permutations of right cosets
         S2=(1,2)(3,4)(5,6)(7,8)(9,10)
         S3=(1,8,3)(2,4,6)(5,7,10)
         L=(1,4)(2,5,9,10,8)(3,7,6)
         R=(1,7,9,10,6)(2,3)(4,5,8)
    """
    return ArithmeticSubgroup_Permutation(
            L="(1,4)(2,5,9,10,8)(3,7,6)",
            R="(1,7,9,10,6)(2,3)(4,5,8)",
            relabel=False)

def HsuExample18():
    r"""
    An example of an index 18 arithmetic subgroup studied by Tim Hsu.

    EXAMPLE::

        sage: import sage.modular.arithgroup.arithgroup_perm as ap
        sage: ap.HsuExample18()
        Arithmetic subgroup with permutations of right cosets
         S2=(1,5)(2,11)(3,10)(4,15)(6,18)(7,12)(8,14)(9,16)(13,17)
         S3=(1,7,11)(2,18,5)(3,9,15)(4,14,10)(6,17,12)(8,13,16)
         L=(1,2)(3,4)(5,6,7)(8,9,10)(11,12,13,14,15,16,17,18)
         R=(1,12,18)(2,6,13,9,4,8,17,7)(3,16,14)(5,11)(10,15)
    """
    return ArithmeticSubgroup_Permutation(
            L="(1,2)(3,4)(5,6,7)(8,9,10)(11,12,13,14,15,16,17,18)",
            R="(1,12,18)(2,6,13,9,4,8,17,7)(3,16,14)(5,11)(10,15)",
            relabel=False)
