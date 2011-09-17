"""
Symmetric Ideals of Infinite Polynomial Rings

This module provides an implementation of ideals of polynomial rings
in a countably infinite number of variables that are invariant under
variable permutation. Such ideals are called 'Symmetric Ideals' in the
rest of this document.  Our implementation is based on the theory of
M. Aschenbrenner and C. Hillar.

AUTHORS:

- Simon King <simon.king@nuigalway.ie>

EXAMPLES:

Here, we demonstrate that working in quotient rings of Infinite
Polynomial Rings works, provided that one uses symmetric Groebner
bases.
::

    sage: R.<x> = InfinitePolynomialRing(QQ)
    sage: I = R.ideal([x[1]*x[2] + x[3]])

Note that ``I`` is not a symmetric Groebner basis::

    sage: G = R*I.groebner_basis()
    sage: G
    Symmetric Ideal (x_1^2 + x_1, x_2 - x_1) of Infinite polynomial ring in x over Rational Field
    sage: Q = R.quotient(G)
    sage: p = x[3]*x[1]+x[2]^2+3
    sage: Q(p)
    -2*x_1 + 3

By the second generator of ``G``, variable `x_n` is equal to `x_1` for
any positive integer `n`.  By the first generator of ``G``, `x_1^3` is
equal to `x_1` in ``Q``. Indeed, we have
::

    sage: Q(p)*x[2] == Q(p)*x[1]*x[3]*x[5]
    True

"""
#*****************************************************************************
#       Copyright (C) 2009 Simon King <king@mathematik.nuigalway.ie>
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
from sage.rings.ideal import Ideal_generic
from sage.rings.integer import Integer
from sage.structure.sequence import Sequence
from sage.misc.cachefunc import cached_method
import sys

class SymmetricIdeal( Ideal_generic ):
    r"""
    Ideal in an Infinite Polynomial Ring, invariant under permutation of variable indices

    THEORY:

    An Infinite Polynomial Ring with finitely many generators `x_\ast,
    y_\ast, ...` over a field `F` is a free commutative `F`-algebra
    generated by infinitely many 'variables' `x_0, x_1, x_2,..., y_0,
    y_1, y_2,...`. We refer to the natural number `n` as the *index*
    of the variable `x_n`. See more detailed description at
    :mod:`~sage.rings.polynomial.infinite_polynomial_ring`


    Infinite Polynomial Rings are equipped with a permutation action
    by permuting positive variable indices, i.e., `x_n^P = x_{P(n)},
    y_n^P=y_{P(n)}, ...` for any permutation `P`.  Note that the
    variables `x_0, y_0, ...` of index zero are invariant under that
    action.

    A *Symmetric Ideal* is an ideal in an infinite polynomial ring `X`
    that is invariant under the permutation action. In other words, if
    `\mathfrak S_\infty` denotes the symmetric group of `1,2,...`,
    then a Symmetric Ideal is a right `X[\mathfrak
    S_\infty]`-submodule of `X`.

    It is known by work of Aschenbrenner and Hillar [AB2007]_ that an
    Infinite Polynomial Ring `X` with a single generator `x_\ast` is
    Noetherian, in the sense that any Symmetric Ideal `I\subset X` is
    finitely generated modulo addition, multiplication by elements of
    `X`, and permutation of variable indices (hence, it is a finitely
    generated right `X[\mathfrak S_\infty]`-module).

    Moreover, if `X` is equipped with a lexicographic monomial
    ordering with `x_1 < x_2 < x_3 ...` then there is an algorithm of
    Buchberger type that computes a Groebner basis `G` for `I` that
    allows for computation of a unique normal form, that is zero
    precisely for the elements of `I` -- see [AB2008]_. See
    :meth:`.groebner_basis` for more details.

    Our implementation allows more than one generator and also
    provides degree lexicographic and degree reverse lexicographic
    monomial orderings -- we do, however, not guarantee termination of
    the Buchberger algorithm in these cases.

    .. [AB2007] M. Aschenbrenner, C. Hillar,
       Finite generation of symmetric ideals.
       Trans. Amer. Math. Soc. 359 (2007), no. 11, 5171--5192.

    .. [AB2008] M. Aschenbrenner, C. Hillar,
       `An Algorithm for Finding Symmetric Groebner Bases in Infinite Dimensional Rings.
       <http://de.arxiv.org/abs/0801.4439>`_

    EXAMPLES::

        sage: X.<x,y> = InfinitePolynomialRing(QQ)
        sage: I = [x[1]*y[2]*y[1] + 2*x[1]*y[2]]*X
        sage: I == loads(dumps(I))
        True
        sage: latex(I)
        \left(x_{1} y_{2} y_{1} + 2 x_{1} y_{2}\right)\Bold{Q}[x_{\ast}, y_{\ast}][\mathfrak{S}_{\infty}]

    The default ordering is lexicographic. We now compute a Groebner basis::

        sage: J = I.groebner_basis() ; J   # about 3 seconds
        [x_1*y_2*y_1 + 2*x_1*y_2, x_2*y_2*y_1 + 2*x_2*y_1, x_2*x_1*y_1^2 + 2*x_2*x_1*y_1, x_2*x_1*y_2 - x_2*x_1*y_1]

    Note that even though the symmetric ideal can be generated by a
    single polynomial, its reduced symmetric Groebner basis comprises
    four elements.  Ideal membership in ``I`` can now be tested by
    commuting symmetric reduction modulo ``J``::

        sage: I.reduce(J)
        Symmetric Ideal (0) of Infinite polynomial ring in x, y over Rational Field

    The Groebner basis is not point-wise invariant under permutation::

        sage: P=Permutation([2, 1])
        sage: J[2]
        x_2*x_1*y_1^2 + 2*x_2*x_1*y_1
        sage: J[2]^P
        x_2*x_1*y_2^2 + 2*x_2*x_1*y_2
        sage: J[2]^P in J
        False

    However, any element of ``J`` has symmetric reduction zero even
    after applying a permutation. This even holds when the
    permutations involve higher variable indices than the ones
    occuring in ``J``::

        sage: [[(p^P).reduce(J) for p in J] for P in Permutations(3)]
        [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    Since ``I`` is not a Groebner basis, it is no surprise that it can not detect
    ideal membership::

        sage: [p.reduce(I) for p in J]
        [0, x_2*y_2*y_1 + 2*x_2*y_1, x_2*x_1*y_1^2 + 2*x_2*x_1*y_1, x_2*x_1*y_2 - x_2*x_1*y_1]

    Note that we give no guarantee that the computation of a symmetric
    Groebner basis will terminate in any order different from
    lexicographic.

    When multiplying Symmetric Ideals or raising them to some integer
    power, the permutation action is taken into account, so that the
    product is indeed the product of ideals in the mathematical sense.
    ::

        sage: I=X*(x[1])
        sage: I*I
        Symmetric Ideal (x_1^2, x_2*x_1) of Infinite polynomial ring in x, y over Rational Field
        sage: I^3
        Symmetric Ideal (x_1^3, x_2*x_1^2, x_2^2*x_1, x_3*x_2*x_1) of Infinite polynomial ring in x, y over Rational Field
        sage: I*I == X*(x[1]^2)
        False

    """

    def __init__(self, ring, gens, coerce=True):
        """
        INPUT:

        ``ring`` -- an infinite polynomial ring
        ``gens`` -- generators of this ideal
        ``coerce`` -- (bool, default ``True``) coerce the given generators into ``ring``

        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]^2+y[2]^2,x[1]*x[2]*y[3]+x[1]*y[4]) # indirect doctest
            sage: I
            Symmetric Ideal (x_1^2 + y_2^2, x_2*x_1*y_3 + x_1*y_4) of Infinite polynomial ring in x, y over Rational Field
            sage: from sage.rings.polynomial.symmetric_ideal import SymmetricIdeal
            sage: J=SymmetricIdeal(X,[x[1]^2+y[2]^2,x[1]*x[2]*y[3]+x[1]*y[4]])
            sage: I==J
            True

        """
        Ideal_generic.__init__(self, ring, gens, coerce=coerce)

    def __repr__(self):
        """
        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]^2+y[2]^2,x[1]*x[2]*y[3]+x[1]*y[4])
            sage: I # indirect doctest
            Symmetric Ideal (x_1^2 + y_2^2, x_2*x_1*y_3 + x_1*y_4) of Infinite polynomial ring in x, y over Rational Field

        """
        return "Symmetric Ideal %s of %s"%(self._repr_short(), self.ring())

    def _latex_(self):
        r"""
        EXAMPLES::

            sage: from sage.misc.latex import latex
            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]*y[2])
            sage: latex(I) # indirect doctest
            \left(x_{1} y_{2}\right)\Bold{Q}[x_{\ast}, y_{\ast}][\mathfrak{S}_{\infty}]

        """
        from sage.misc.latex import latex
        return '\\left(%s\\right)%s[\\mathfrak{S}_{\\infty}]'%(", ".join([latex(g) for g in self.gens()]), latex(self.ring()))

    def _contains_(self, p):
        """
        Determine whether the argument belongs to ``self``.

        ASSUMPTION:

        ``self`` is given by a symmetric Groebner basis.

        EXAMPLES::

            sage: R.<x> = InfinitePolynomialRing(QQ)
            sage: I = R.ideal([x[1]*x[2] + x[3]])
            sage: I = R*I.groebner_basis()
            sage: I
            Symmetric Ideal (x_1^2 + x_1, x_2 - x_1) of Infinite polynomial ring in x over Rational Field
            sage: x[2]^2 + x[3] in I # indirect doctest
            True

        """
        try:
            return self.reduce(p) == 0
        except:
            return False

    def __mul__ (self, other):
        """
        Product of two symmetric ideals.

        Since the generators of a symmetric ideal are subject to a
        permutation action, they in fact stand for a set of
        polynomials. Hence, when multiplying two symmetric ideals, it
        does not suffice to simply multiply the respective generators.

        EXAMPLE::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1])
            sage: I*I         # indirect doctest
            Symmetric Ideal (x_1^2, x_2*x_1) of Infinite polynomial ring in x over Rational Field

        """
        # determine maximal generator index
        PARENT = self.ring()
        if (not isinstance(other, self.__class__)) or self.ring()!=other.ring():
            if hasattr(other,'gens'):
                other = SymmetricIdeal(PARENT, other.gens(), coerce=True)
        other = other.symmetrisation()
        sN = max([X.max_index() for X in self.gens()]+[1])
        oN = max([X.max_index() for X in other.gens()]+[1])

        from sage.combinat.permutation import Permutation
        P = Permutation(range(2,sN+oN+1)+[1])
        oGen = list(other.gens())
        SymL = oGen
        for i in range(sN):
            oGen = [X.__pow__(P) for X in oGen]
            SymL = SymL + oGen
        # Now, SymL contains all necessary permutations of the second factor
        OUT = []
        for X in self.gens():
            OUT.extend([X*Y for Y in SymL])
        return SymmetricIdeal(PARENT, OUT, coerce=False).interreduction()

    def __pow__(self, n):
        """
        Raise self to some power.

        Since the generators of a symmetric ideal are subject to a
        permutation action, they in fact stand for a set of
        polynomials. Hence, when raising a symmetric ideals to some
        power, it does not suffice to simply raise the generators to
        the respective power.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1])
            sage: I^2     # indirect doctest
            Symmetric Ideal (x_1^2, x_2*x_1) of Infinite polynomial ring in x over Rational Field

        """
        OUT = SymmetricIdeal(self.ring(),[1])
        for i in range(n):
            OUT = self*OUT
        return OUT

    def is_maximal(self):
        """
        Answers whether self is a maximal ideal.

        ASSUMPTION:

        ``self`` is defined by a symmetric Groebner basis.

        NOTE:

        It is not checked whether self is in fact a symmetric Groebner
        basis. A wrong answer can result if this assumption does not
        hold.  A ``NotImplementedError`` is raised if the base ring is not
        a field, since symmetric Groebner bases are not implemented in
        this setting.

        EXAMPLES::

            sage: R.<x,y> = InfinitePolynomialRing(QQ)
            sage: I = R.ideal([x[1]+y[2], x[2]-y[1]])
            sage: I = R*I.groebner_basis()
            sage: I
            Symmetric Ideal (y_1, x_1) of Infinite polynomial ring in x, y over Rational Field
            sage: I = R.ideal([x[1]+y[2], x[2]-y[1]])
            sage: I.is_maximal()
            False

        The preceding answer is wrong, since it is not the case that
        ``I`` is given by a symmetric Groebner basis::

            sage: I = R*I.groebner_basis()
            sage: I
            Symmetric Ideal (y_1, x_1) of Infinite polynomial ring in x, y over Rational Field
            sage: I.is_maximal()
            True

        """
        if not self.base_ring().is_field():
            raise NotImplementedError
        if len(self.gens()) == 1:
            if self.is_trivial() and not self.is_zero():
                return True
        V = [p.variables() for p in self.gens()]
        V = [x for x in V if len(x)==1]
        V = [str(x[0]).split('_')[0] for x in V]
        return set(V) == set(self.ring().variable_names())

    def reduce(self, I, tailreduce=False):
        """
        Symmetric reduction of self by another Symmetric Ideal or list of Infinite Polynomials,
        or symmetric reduction of a given Infinite Polynomial by self.

        INPUT:

        - ``I`` -- an Infinite Polynomial, or a Symmetric Ideal or a
          list of Infinite Polynomials.
        - ``tailreduce`` -- (bool, default ``False``) If ``True``, the
          non-leading terms will be reduced as well.

        OUTPUT:

        Symmetric reduction of ``self`` with respect to ``I``.

        THEORY:

        Reduction of an element `p` of an Infinite Polynomial Ring `X`
        by some other element `q` means the following:

        1. Let `M` and `N` be the leading terms of `p` and `q`.
        2. Test whether there is a permutation `P` that does not does
           not diminish the variable indices occurring in `N` and
           preserves their order, so that there is some term `T\in X`
           with `T N^P = M`. If there is no such permutation, return `p`
        3. Replace `p` by `p-T q^P` and continue with step 1.

        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I = X*(y[1]^2*y[3]+y[1]*x[3]^2)
            sage: I.reduce([x[1]^2*y[2]])
            Symmetric Ideal (x_3^2*y_1 + y_3*y_1^2) of Infinite polynomial ring in x, y over Rational Field

        The preceding is correct, since any permutation that turns
        ``x[1]^2*y[2]`` into a factor of ``x[3]^2*y[2]`` interchanges
        the variable indices 1 and 2 -- which is not allowed. However,
        reduction by ``x[2]^2*y[1]`` works, since one can change
        variable index 1 into 2 and 2 into 3::

            sage: I.reduce([x[2]^2*y[1]])
            Symmetric Ideal (y_3*y_1^2) of Infinite polynomial ring in x, y over Rational Field

        The next example shows that tail reduction is not done, unless
        it is explicitly advised.  The input can also be a symmetric
        ideal::

            sage: J = (y[2])*X
            sage: I.reduce(J)
            Symmetric Ideal (x_3^2*y_1 + y_3*y_1^2) of Infinite polynomial ring in x, y over Rational Field
            sage: I.reduce(J, tailreduce=True)
            Symmetric Ideal (x_3^2*y_1) of Infinite polynomial ring in x, y over Rational Field

        """
        if I in self.ring(): # we want to reduce a polynomial by self
            return self.ring()(I).reduce(self)
        from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
        if hasattr(I,'gens'):
            I = I.gens()
        if (not I):
            return self
        I = list(I)
        S = SymmetricReductionStrategy(self.ring(),I, tailreduce)
        return SymmetricIdeal(self.ring(),[S.reduce(X) for X in self.gens()], coerce=False)

    def interreduction(self, tailreduce=True, sorted=False, report=None, RStrat=None):
        """
        Return symmetrically interreduced form of self

        INPUT:

        - ``tailreduce`` -- (bool, default ``True``) If True, the
          interreduction is also performed on the non-leading monomials.
        - ``sorted`` -- (bool, default ``False``) If True, it is assumed that the
          generators of self are already increasingly sorted.
        - ``report`` -- (object, default ``None``) If not None, some information on the
          progress of computation is printed
        - ``RStrat`` -- (:class:`~sage.rings.polynomial.symmetric_reduction.SymmetricReductionStrategy`,
          default ``None``) A reduction strategy to which the polynomials resulting
          from the interreduction will be added. If ``RStrat`` already contains some
          polynomials, they will be used in the interreduction. The effect is to
          compute in a quotient ring.

        OUTPUT:

        A Symmetric Ideal J (sorted list of generators) coinciding
        with self as an ideal, so that any generator is symmetrically
        reduced w.r.t. the other generators. Note that the leading
        coefficients of the result are not necessarily 1.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]+x[2],x[1]*x[2])
            sage: I.interreduction()
            Symmetric Ideal (-x_1^2, x_2 + x_1) of Infinite polynomial ring in x over Rational Field

        Here, we show the ``report`` option::

            sage: I.interreduction(report=True)
            Symmetric interreduction
            [1/2]  >
            [2/2] : >
            [1/2]  >
            [2/2] T[1] >
            >
            Symmetric Ideal (-x_1^2, x_2 + x_1) of Infinite polynomial ring in x over Rational Field

        ``[m/n]`` indicates that polynomial number ``m`` is considered
        and the total number of polynomials under consideration is
        ``n``. '-> 0' is printed if a zero reduction occurred. The
        rest of the report is as described in
        :meth:`sage.rings.polynomial.symmetric_reduction.SymmetricReductionStrategy.reduce`.

        Last, we demonstrate the use of the optional parameter ``RStrat``::

            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: R = SymmetricReductionStrategy(X)
            sage: R
            Symmetric Reduction Strategy in Infinite polynomial ring in x over Rational Field
            sage: I.interreduction(RStrat=R)
            Symmetric Ideal (-x_1^2, x_2 + x_1) of Infinite polynomial ring in x over Rational Field
            sage: R
            Symmetric Reduction Strategy in Infinite polynomial ring in x over Rational Field, modulo
                x_1^2,
                x_2 + x_1
            sage: R = SymmetricReductionStrategy(X,[x[1]^2])
            sage: I.interreduction(RStrat=R)
            Symmetric Ideal (x_2 + x_1) of Infinite polynomial ring in x over Rational Field

        """
        DONE = []
        j = 0
        TODO = []
        PARENT = self.ring()
        for P in self.gens():
            if P._p!=0:
                if P.is_unit(): # self generates all of self.ring()
                    if RStrat is not None:
                        RStrat.add_generator(PARENT(1))
                    return SymmetricIdeal(self.ring(),[self.ring()(1)], coerce=False)
                TODO.append(P)
        if not sorted:
            TODO = list(set(TODO))
            TODO.sort()
        if hasattr(PARENT,'_P'):
            CommonR = PARENT._P
        else:
            VarList = set([])
            for P in TODO:
                if P._p!=0:
                    if P.is_unit(): # self generates all of PARENT
                        if RStrat is not None:
                            RStrat.add_generator(PARENT(1))
                        return SymmetricIdeal(PARENT,[PARENT(1)], coerce=False)
                    VarList = VarList.union(P._p.parent().variable_names())
            VarList = list(VarList)
            if not VarList:
                return SymmetricIdeal(PARENT,[0])
            VarList.sort(cmp=PARENT.varname_cmp, reverse=True)
            from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
            CommonR = PolynomialRing(self.base_ring(), VarList, order=self.ring()._order)

        ## Now, the symmetric interreduction starts
        if not (report is None):
            print 'Symmetric interreduction'
        from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
        if RStrat is None:
            RStrat = SymmetricReductionStrategy(self.ring(),tailreduce=tailreduce)
        GroundState = RStrat.gens()
        while (1):
            RStrat.setgens(GroundState)
            DONE = []
            for i in range(len(TODO)):
                if (not (report is None)):
                    print '[%d/%d] '%(i+1,len(TODO)),
                    sys.stdout.flush()
                p = RStrat.reduce(TODO[i], report=report)
                if p._p != 0:
                    if p.is_unit(): # self generates all of self.ring()
                        return SymmetricIdeal(self.ring(),[self.ring()(1)], coerce=False)
                    RStrat.add_generator(p, good_input=True)
                    DONE.append(p)
                else:
                    if not (report is None):
                        print "-> 0"
            DONE.sort()
            if DONE == TODO:
                break
            else:
                if len(TODO)==len(DONE):
                    import copy
                    bla = copy.copy(TODO)
                    bla.sort()
                    if bla==DONE:
                        break
                TODO = DONE
        return SymmetricIdeal(self.ring(),DONE, coerce=False)

    def interreduced_basis(self):
        """
        A fully symmetrically reduced generating set (type :class:`~sage.structure.sequence.Sequence`) of self.

        This does essentially the same as :meth:`interreduction` with
        the option 'tailreduce', but it returns a
        :class:`~sage.structure.sequence.Sequence` rather than a
        :class:`~sage.rings.polynomial.symmetric_ideal.SymmetricIdeal`.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I=X*(x[1]+x[2],x[1]*x[2])
            sage: I.interreduced_basis()
            [-x_1^2, x_2 + x_1]

        """
        return Sequence(self.interreduction(tailreduce=True).gens(), self.ring(), check=False)

    def symmetrisation(self, N=None, tailreduce=False, report=None, use_full_group=False):
        """
        Apply permutations to the generators of self and interreduce

        INPUT:

        - ``N`` -- (integer, default ``None``) Apply permutations in
          `Sym(N)`. If it is not given then it will be replaced by the
          maximal variable index occurring in the generators of
          ``self.interreduction().squeezed()``.
        - ``tailreduce`` -- (bool, default ``False``) If ``True``, perform
          tail reductions.
        - ``report`` -- (object, default ``None``) If not ``None``, report
          on the progress of computations.
        - ``use_full_group`` (optional) -- If True, apply *all* elements of
          `Sym(N)` to the generators of self (this is what [AB2008]_
          originally suggests). The default is to apply all elementary
          transpositions to the generators of ``self.squeezed()``,
          interreduce, and repeat until the result stabilises, which is
          often much faster than applying all of `Sym(N)`, and we are
          convinced that both methods yield the same result.

        OUTPUT:

        A symmetrically interreduced symmetric ideal with respect to
        which any `Sym(N)`-translate of a generator of self is
        symmetrically reducible, where by default ``N`` is the maximal
        variable index that occurs in the generators of
        ``self.interreduction().squeezed()``.

        NOTE:

        If ``I`` is a symmetric ideal whose generators are monomials,
        then ``I.symmetrisation()`` is its reduced Groebner basis.  It
        should be noted that without symmetrisation, monomial
        generators, in general, do not form a Groebner basis.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I = X*(x[1]+x[2], x[1]*x[2])
            sage: I.symmetrisation()
            Symmetric Ideal (-x_1^2, x_2 + x_1) of Infinite polynomial ring in x over Rational Field
            sage: I.symmetrisation(N=3)
            Symmetric Ideal (-2*x_1) of Infinite polynomial ring in x over Rational Field
            sage: I.symmetrisation(N=3, use_full_group=True)
            Symmetric Ideal (-2*x_1) of Infinite polynomial ring in x over Rational Field

        """
        newOUT = self.interreduction(tailreduce=tailreduce, report=report).squeezed()
        R = self.ring()
        OUT = R*()
        if N is None:
            N = max([Y.max_index() for Y in newOUT.gens()]+[1])
        else:
            N = Integer(N)
        if hasattr(R,'_max') and R._max<N:
            R.gen()[N]
        if report!=None:
            print "Symmetrise %d polynomials at level %d"%(len(newOUT.gens()),N)
        if use_full_group:
            from sage.combinat.permutation import Permutations
            NewGens = []
            Gens = self.gens()
            for P in Permutations(N):
                NewGens.extend([p**P for p in Gens])
            return (NewGens * R).interreduction(tailreduce=tailreduce,report=report)
        from sage.combinat.permutation import Permutation
        from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
        RStrat = SymmetricReductionStrategy(self.ring(),OUT.gens(),tailreduce=tailreduce)
        while (OUT!=newOUT):
            OUT = newOUT
            PermutedGens = list(OUT.gens())
            if not (report is None):
                print "Apply permutations"
            for i in range(1,N):
                for j in range(i+1,N+1):
                    P = Permutation(((i,j)))
                    for X in OUT.gens():
                        p = RStrat.reduce(X**P,report=report)
                        if p._p !=0:
                            PermutedGens.append(p)
                            RStrat.add_generator(p,good_input=True)
            newOUT = (PermutedGens * R).interreduction(tailreduce=tailreduce,report=report)
        return OUT

    def symmetric_basis(self):
        """
        A symmetrised generating set (type :class:`~sage.structure.sequence.Sequence`) of self.

        This does essentially the same as :meth:`symmetrisation` with
        the option 'tailreduce', and it returns a
        :class:`~sage.structure.sequence.Sequence` rather than a
        :class:`~sage.rings.polynomial.symmetric_ideal.SymmetricIdeal`.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I = X*(x[1]+x[2], x[1]*x[2])
            sage: I.symmetric_basis()
            [x_1^2, x_2 + x_1]

        """
        return Sequence(self.symmetrisation(tailreduce=True).normalisation().gens(), self.ring(), check=False)

    def normalisation(self):
        """
        Return an ideal that coincides with self, so that all generators have leading coefficient 1.

        Possibly occurring zeroes are removed from the generator list.

        EXAMPLES::

            sage: X.<x> = InfinitePolynomialRing(QQ)
            sage: I = X*(1/2*x[1]+2/3*x[2], 0, 4/5*x[1]*x[2])
            sage: I.normalisation()
            Symmetric Ideal (x_2 + 3/4*x_1, x_2*x_1) of Infinite polynomial ring in x over Rational Field

        """
        return SymmetricIdeal(self.ring(), [X/X.lc() for X in self.gens() if X._p!=0])

    def squeezed(self):
        """
        Reduce the variable indices occurring in ``self``.

        OUTPUT:

        A Symmetric Ideal whose generators are the result of applying
        :meth:`~sage.rings.polynomial.infinite_polynomial_element.InfinitePolynomial_sparse.squeezed`
        to the generators of ``self``.

        NOTE:

        The output describes the same Symmetric Ideal as ``self``.

        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ,implementation='sparse')
            sage: I = X*(x[1000]*y[100],x[50]*y[1000])
            sage: I.squeezed()
            Symmetric Ideal (x_2*y_1, x_1*y_2) of Infinite polynomial ring in x, y over Rational Field

        """
        return SymmetricIdeal(self.ring(), [X.squeezed() for X in self.gens()])

    @cached_method
    def groebner_basis(self, tailreduce=False, reduced=True, algorithm=None, report=None, use_full_group=False):
        """
        Return a symmetric Groebner basis (type :class:`~sage.structure.sequence.Sequence`) of ``self``.

        INPUT:

        - ``tailreduce`` -- (bool, default ``False``) If True, use tail reduction
          in intermediate computations
        - ``reduced`` -- (bool, default ``True``) If ``True``, return the reduced normalised
          symmetric Groebner basis.
        - ``algorithm`` -- (string, default ``None``) Determine the algorithm (see below for
          available algorithms).
        - ``report`` -- (object, default ``None``) If not ``None``, print information on the
          progress of computation.
        - ``use_full_group`` -- (bool, default ``False``) If ``True`` then proceed as
          originally suggested by [AB2008]_. Our default method should be faster; see
          :meth:`.symmetrisation` for more details.

        The computation of symmetric Groebner bases also involves the
        computation of *classical* Groebner bases, i.e., of Groebner
        bases for ideals in polynomial rings with finitely many
        variables. For these computations, Sage provides the following
        ALGORITHMS:

        ''
            autoselect (default)

        'singular:groebner'
            Singular's ``groebner`` command

        'singular:std'
            Singular's ``std`` command

        'singular:stdhilb'
            Singular's ``stdhib`` command

        'singular:stdfglm'
            Singular's ``stdfglm`` command

        'singular:slimgb'
            Singular's ``slimgb`` command

        'libsingular:std'
            libSingular's ``std`` command

        'libsingular:slimgb'
            libSingular's ``slimgb`` command

        'toy:buchberger'
            Sage's toy/educational buchberger without strategy

        'toy:buchberger2'
            Sage's toy/educational buchberger with strategy

        'toy:d_basis'
            Sage's toy/educational d_basis algorithm

        'macaulay2:gb'
            Macaulay2's ``gb`` command (if available)

        'magma:GroebnerBasis'
            Magma's ``Groebnerbasis`` command (if available)


        If only a system is given - e.g. 'magma' - the default algorithm is
        chosen for that system.

        .. note::

           The Singular and libSingular versions of the respective
           algorithms are identical, but the former calls an external
           Singular process while the later calls a C function, i.e. the
           calling overhead is smaller.

        EXAMPLES::

            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: I1 = X*(x[1]+x[2],x[1]*x[2])
            sage: I1.groebner_basis()
            [x_1]
            sage: I2 = X*(y[1]^2*y[3]+y[1]*x[3])
            sage: I2.groebner_basis()
            [x_1*y_2 + y_2^2*y_1, x_2*y_1 + y_2*y_1^2]

        Note that a symmetric Groebner basis of a principal ideal is
        not necessarily formed by a single polynomial.

        When using the algorithm originally suggested by Aschenbrenner
        and Hillar, the result is the same, but the computation takes
        much longer::

            sage: I2.groebner_basis(use_full_group=True)
            [x_1*y_2 + y_2^2*y_1, x_2*y_1 + y_2*y_1^2]

        Last, we demonstrate how the report on the progress of
        computations looks like::

            sage: I1.groebner_basis(report=True, reduced=True)
            Symmetric interreduction
            [1/2]  >
            [2/2] : >
            [1/2]  >
            [2/2]  >
            Symmetrise 2 polynomials at level 2
            Apply permutations
            >
            >
            Symmetric interreduction
            [1/3]  >
            [2/3]  >
            [3/3] : >
            -> 0
            [1/2]  >
            [2/2]  >
            Symmetrisation done
            Classical Groebner basis
            -> 2 generators
            Symmetric interreduction
            [1/2]  >
            [2/2]  >
            Symmetrise 2 polynomials at level 3
            Apply permutations
            >
            >
            :>
            ::>
            :>
            ::>
            Symmetric interreduction
            [1/4]  >
            [2/4] : >
            -> 0
            [3/4] :: >
            -> 0
            [4/4] : >
            -> 0
            [1/1]  >
            Apply permutations
            :>
            :>
            :>
            Symmetric interreduction
            [1/1]  >
            Classical Groebner basis
            -> 1 generators
            Symmetric interreduction
            [1/1]  >
            Symmetrise 1 polynomials at level 4
            Apply permutations
            >
            :>
            :>
            >
            :>
            :>
            Symmetric interreduction
            [1/2]  >
            [2/2] : >
            -> 0
            [1/1]  >
            Symmetric interreduction
            [1/1]  >
            [x_1]

        The Aschenbrenner-Hillar algorithm is only guaranteed to work
        if the base ring is a field. So, we raise a TypeError if this
        is not the case::

            sage: R.<x,y> = InfinitePolynomialRing(ZZ)
            sage: I = R*[x[1]+x[2],y[1]]
            sage: I.groebner_basis()
            Traceback (most recent call last):
            ...
            TypeError: The base ring (= Integer Ring) must be a field

        TESTS:

        In an earlier version, the following examples failed::

            sage: X.<y,z> = InfinitePolynomialRing(GF(5),order='degrevlex')
            sage: I = ['-2*y_0^2 + 2*z_0^2 + 1', '-y_0^2 + 2*y_0*z_0 - 2*z_0^2 - 2*z_0 - 1', 'y_0*z_0 + 2*z_0^2 - 2*z_0 - 1', 'y_0^2 + 2*y_0*z_0 - 2*z_0^2 + 2*z_0 - 2', '-y_0^2 - 2*y_0*z_0 - z_0^2 + y_0 - 1']*X
            sage: I.groebner_basis()
            [1]

            sage: Y.<x,y> = InfinitePolynomialRing(GF(3), order='degrevlex', implementation='sparse')
            sage: I = ['-y_3']*Y
            sage: I.groebner_basis()
            [y_1]

        """
        # determine maximal generator index
        # and construct a common parent for the generators of self
        if algorithm is None:
            algorithm=''
        PARENT = self.ring()
        if not (hasattr(PARENT.base_ring(),'is_field') and PARENT.base_ring().is_field()):
            raise TypeError, "The base ring (= %s) must be a field"%PARENT.base_ring()
        OUT = self.symmetrisation(tailreduce=tailreduce,report=report,use_full_group=use_full_group)
        if not (report is None):
            print "Symmetrisation done"
        VarList = set([])
        for P in OUT.gens():
            if P._p!=0:
                if P.is_unit():
                    return Sequence([PARENT(1)], PARENT, check=False)
                VarList = VarList.union([str(X) for X in P.variables()])
        VarList = list(VarList)
        if not VarList:
            return Sequence([PARENT(0)], PARENT, check=False)
        from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
        N = max([int(X.split('_')[1]) for X in VarList]+[1])

        #from sage.combinat.permutation import Permutations
        while (1):
            if hasattr(PARENT,'_P'):
                CommonR = PARENT._P
            else:
                VarList = set([])
                for P in OUT.gens():
                    if P._p!=0:
                        if P.is_unit():
                            return Sequence([PARENT(1)], PARENT, check=False)
                        VarList = VarList.union([str(X) for X in P.variables()])
                VarList = list(VarList)
                VarList.sort(cmp=PARENT.varname_cmp, reverse=True)
                CommonR = PolynomialRing(PARENT._base, VarList, order=PARENT._order)

            try: # working around one libsingular bug and one libsingular oddity
                DenseIdeal = [CommonR(P._p) if ((CommonR is P._p.parent()) or CommonR.ngens()!=P._p.parent().ngens()) else CommonR(repr(P._p))  for P in OUT.gens()]*CommonR
            except:
                if report != None:
                    print "working around a libsingular bug"
                DenseIdeal = [repr(P._p) for P in OUT.gens()]*CommonR
            if hasattr(DenseIdeal,'groebner_basis'):
                if report != None:
                    print "Classical Groebner basis"
                    if algorithm!='':
                        print "(using %s)"%algorithm
                newOUT = (DenseIdeal.groebner_basis(algorithm)*PARENT)
                if report != None:
                    print "->",len(newOUT.gens()),'generators'
            else:
                if report != None:
                    print "Univariate polynomial ideal"
                newOUT = DenseIdeal.gens()*PARENT
            # Symmetrise out to the next index:
            N += 1
            newOUT = newOUT.symmetrisation(N=N,tailreduce=tailreduce,report=report,use_full_group=use_full_group)
            if [X.lm() for X in OUT.gens()] == [X.lm() for X in newOUT.gens()]:
                if reduced:
                    if tailreduce:
                        return Sequence(newOUT.normalisation().gens(), PARENT, check=False)
                    return Sequence(newOUT.interreduction(tailreduce=True, report=report).normalisation().gens(), PARENT, check=False)
                return Sequence(newOUT.gens(), PARENT, check=False)
            OUT = newOUT
