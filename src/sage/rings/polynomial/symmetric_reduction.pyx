"""
Symmetric Reduction of Infinite Polynomials

:class:`~sage.rings.polynomial.symmetric_reduction.SymmetricReductionStrategy`
provides a framework for efficient symmetric reduction of Infinite Polynomials, see
:mod:`~sage.rings.polynomial.infinite_polynomial_element`.

AUTHORS:

- Simon King <simon.king@uni-jena.de>

THEORY:
    According to M. Aschenbrenner and C. Hillar [AB2007]_, Symmetric Reduction
    of an element `p` of an Infinite Polynomial Ring `X` by some other element
    `q` means the following:

    1. Let `M` and `N` be the leading terms of `p` and `q`.
    2. Test whether there is a permutation `P` that does not does not diminish the variable
       indices occuring in `N` and preserves their order, so that there is some term `T\in X`
       with `T N^P = M`. If there is no such permutation, return `p`
    3. Replace `p` by `p-T q^P` and continue with step 1.

    .. [AB2007] M. Aschenbrenner, C. Hillar,
       Finite generation of symmetric ideals.
       Trans. Amer. Math. Soc. 359 (2007), no. 11, 5171--5192.


When reducing one polynomial `p` with respect to a list `L` of
other polynomials, there usually is a choice of order on which the
efficiency crucially depends. Also it helps to modify the polynomials
on the list in order to simplify the basic reduction steps.

The preparation of `L` may be expensive. Hence, if the same list is used
many times then it is reasonable to perform the preparation only once. This
is the background of :class:`~sage.rings.polynomial.symmetric_reduction.SymmetricReductionStrategy`.

Our current strategy is to keep the number of terms in the polynomials
as small as possible. For this, we sort `L` by increasing number of
terms. If several elements of `L` allow for a reduction of `p`, we
chose the one with the smallest number of terms. Later on, it should be possible
to implement further strategies for choice.

When adding a new polynomial `q` to `L`, we first reduce `q` with respect to `L`.
Then, we test heuristically whether it is possible to reduce the number of
terms of the elements of `L` by reduction modulo `q`.
That way, we see best chances to keep the number of terms in intermediate
reduction steps relatively small.

EXAMPLES:

First, we create an infinite polynomial ring and one of its elements::

    sage: X.<x,y> = InfinitePolynomialRing(QQ)
    sage: p = y[1]^2*y[3]+y[1]*x[3]

We want to symmetrically reduce it by another polynomial. So, we put this other
polynomial into a list and create a Symmetric Reduction Strategy object::

    sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
    sage: S = SymmetricReductionStrategy(X, [y[2]^2*y[1]])
    sage: S
    Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
        y2^2*y1
    sage: S.reduce(p)
    y3*y1^2 + y1*x3

The preceding is correct, since any permutation that turns ``y[2]^2*y[1]`` into
a factor of ``y[1]^2*y[3]`` interchanges the variable indices 1 and 2 -- which is not
allowed in a symmetric reduction. However, reduction by ``y[1]^2*y[2]`` works,
since one can change variable index 1 into 2 and 2 into 3. So, we add this to ``S``::

    sage: S.add_generator(y[1]^2*y[2])
    sage: S
    Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
        y2*y1^2,
        y2^2*y1
    sage: S.reduce(p)
    y1*x3

The next example shows that tail reduction is not done, unless it is explicitly adviced::

    sage: S.reduce(y[3] + 2*y[2]*y[1]^2 + 3*y[2]^2*y[1])
    y3 + 3*y2^2*y1 + 2*y2*y1^2
    sage: S.tailreduce(y[3] + 2*y[2]*y[1]^2 + 3*y[2]^2*y[1])
    y3

However, it is possible to ask for tailreduction already when the Symmetric Reduction
Strategy is created::

    sage: S2 = SymmetricReductionStrategy(X, [y[2]^2*y[1],y[1]^2*y[2]], tailreduce=True)
    sage: S2
    Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
        y2*y1^2,
        y2^2*y1
    with tailreduction
    sage: S2.reduce(y[3] + 2*y[2]*y[1]^2 + 3*y[2]^2*y[1])
    y3

"""

#*****************************************************************************
#       Copyright (C) 2009 Simon King <king@mathematik.uni-jena.de>
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

import copy, operator, sys

cdef class SymmetricReductionStrategy:
    """
    A framework for efficient symmetric reduction of InfinitePolynomial, see
    :mod:`~sage.rings.polynomial.infinite_polynomial_element`.

    INPUT:

    - ``Parent``, an Infinite Polynomial Ring, see :mod:`~sage.rings.polynomial.infinite_polynomial_element`.
    - ``L``, a list of elements of ``Parent`` (default: ``L=[]``) with respect to which reduction will be done
    - ``good_input``: If this optional parameter is true, it is assumed that each element of ``L`` is
      symmetrically reduced with respect to the previous elements of ``L``

    EXAMPLES::

        sage: X.<y> = InfinitePolynomialRing(QQ)
        sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
        sage: S = SymmetricReductionStrategy(X, [y[2]^2*y[1],y[1]^2*y[2]], good_input=True)
        sage: S.reduce(y[3] + 2*y[2]*y[1]^2 + 3*y[2]^2*y[1])
        y3 + 3*y2^2*y1 + 2*y2*y1^2
        sage: S.tailreduce(y[3] + 2*y[2]*y[1]^2 + 3*y[2]^2*y[1])
        y3

    """
    def __init__(self, Parent, L=None, tailreduce=False, good_input=None):
        """
        EXAMPLES::

            sage: X.<y> = InfinitePolynomialRing(QQ)
            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: S = SymmetricReductionStrategy(X, [y[2]^2*y[1],y[1]^2*y[2]], good_input=True)
            sage: S == loads(dumps(S))
            True

        """
        self._parent = Parent
        if hasattr(Parent, '_P'):
            self._R = Parent._P
        else:
            self._R = None
        self._lm   = []
        self._lengths = []
        self._min_lm = None
        self._tail = int(tailreduce)
        if not (L is None):
            for p in L:
                self.add_generator(p, good_input=good_input)

    def __getinitargs__(self):
        return (self._parent,[],self._tail,None)

    def __getstate__(self):
        return (self._lm, self._lengths, self._min_lm, self._tail, self._parent)

    def __setstate__(self, L): #(lm, lengths, min_lm, tail)
        self._lm = L[0]
        self._lengths  = L[1]
        self._min_lm = L[2]
        self._tail = L[3]
        self._parent = L[4]
        if hasattr(self._parent, '_P'):
            self._R = self._parent._P
        else:
            self._R = None

    def __cmp__(self, other):
        if not isinstance(other, SymmetricReductionStrategy):
            return -1
        cdef SymmetricReductionStrategy Other = other
        return cmp((self._parent,self._lm,self._tail),(Other._parent,Other._lm,Other._tail))

    def gens(self):
        """
        Return the list of Infinite Polynomials modulo which self reduces

        EXAMPLES::

            sage: X.<y> = InfinitePolynomialRing(QQ)
            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: S = SymmetricReductionStrategy(X, [y[2]^2*y[1],y[1]^2*y[2]])
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in y over Rational Field, modulo
                y2*y1^2,
                y2^2*y1
            sage: S.gens()
            [y2*y1^2, y2^2*y1]

        """
        return self._lm

    def setgens(self, L):
        """
        Define the list of Infinite Polynomials modulo which self reduces

        INPUT:

        ``L``, a list

        NOTE:

        It is not tested if ``L`` is a good input. That method simply assigns a *copy* of ``L``
        to the generators of self.

        EXAMPLES::

            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: X.<y> = InfinitePolynomialRing(QQ)
            sage: S = SymmetricReductionStrategy(X, [y[2]^2*y[1],y[1]^2*y[2]])
            sage: R = SymmetricReductionStrategy(X)
            sage: R.setgens(S.gens())
            sage: R
            Symmetric Reduction Strategy in Infinite polynomial ring in y over Rational Field, modulo
                y2*y1^2,
                y2^2*y1
            sage: R.gens() is S.gens()
            False
            sage: R.gens() == S.gens()
            True

        """
        self._lm = [X for X in L]


    def reset(self):
        """
        Remove all polynomials from self

        EXAMPLES::

            sage: X.<y> = InfinitePolynomialRing(QQ)
            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: S = SymmetricReductionStrategy(X, [y[2]^2*y[1],y[1]^2*y[2]])
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in y over Rational Field, modulo
                y2*y1^2,
                y2^2*y1
            sage: S.reset()
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in y over Rational Field

        """
        self._lm = []
        self._lengths = []
        self._min_lm = None

    def __repr__(self):
        """
        String representation of self

        EXAMPLES::

            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: S = SymmetricReductionStrategy(X, [y[2]^2*y[1],y[1]^2*y[2]], tailreduce=True)
            sage: S  # indirect doctest
            Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
                y2*y1^2,
                y2^2*y1
            with tailreduction

        """
        s = "Symmetric Reduction Strategy in %s"%self._parent
        if self._lm:
            s += ", modulo\n    %s"%(',\n    '.join([str(X) for X in self._lm]))
        if self._tail:
            s += '\nwith tailreduction'
        return s

    def __call__(self, p):
        """
        INPUT:
            A polynomial or an infinite polynomial

        OUTPUT:
            A polynomial whose parent ring allows for coercion of any generator of self

        EXAMPLES::

            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: X.<x,y> = InfinitePolynomialRing(QQ, implementation='sparse')
            sage: a, b = y[2]^2*y[1], y[1]^2*y[2]
            sage: p = y[3]*x[2]*x[1]
            sage: S = SymmetricReductionStrategy(X, [a,b])
            sage: p._p.parent().has_coerce_map_from(a._p.parent())
            False
            sage: q = S(p)
            sage: q.parent().has_coerce_map_from(a._p.parent())
            True
            sage: S(p) == S(p._p)
            True

        """
        if hasattr(p,'_p'):
            p = p._p
        if self._R is None:
            self._R = p.parent()
            if hasattr(self._parent,'_P'):
                self._parent._P = self._R
            return p
        if self._R.has_coerce_map_from(p.parent()):
            return self._R(p)
        if p.parent().has_coerce_map_from(self._R):
            self._R = p.parent()
            if hasattr(self._parent,'_P'):
                self._parent._P = self._R
            return p
        # now we really need to work...
        R = self._R
        VarList = list(set(R.variable_names() + p.parent().variable_names()))
        VarList.sort(cmp=self._parent.varname_cmp,reverse=True)
        from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
        self._R = PolynomialRing(self._parent.base_ring(), VarList, order = self._parent._order)
        if hasattr(self._parent,'_P'):
            self._parent._P = self._R
        return self._R(p)

    def add_generator(self, p, good_input=None):
        """
        Add another polynomial to self

        NOTE:
            Previously added polynomials may be modified. All input is prepared in view
            of an efficient symmetric reduction.

        EXAMPLES::

            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: S = SymmetricReductionStrategy(X)
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field
            sage: S.add_generator(y[3] + y[1]*(x[3]+x[1]))
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
                y3 + y1*x3 + y1*x1

        Note that the first added polynomial will be simplified when adding a suitable second polynomial::

            sage: S.add_generator(x[2]+x[1])
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
                y3,
                x2 + x1

        By default, reduction is applied to any newly added polynomial. This can be avoided by
        specifying the optional parameter 'good_input'::

            sage: S.add_generator(y[2]+y[1]*x[2])
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
                y3,
                y2 + y1*x2,
                x2 + x1
            sage: S.reduce(x[3]+x[2])
            -2*x1
            sage: S.add_generator(x[3]+x[2], good_input=True)
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
                y3,
                x3 + x2,
                y2 + y1*x2,
                x2 + x1

        In the previous example, ``x[3] + x[2]`` is added without being reduced to zero.

        """
        from sage.rings.polynomial.infinite_polynomial_element import InfinitePolynomial
        p = InfinitePolynomial(self._parent, self(p), is_good_poly=True)
        cdef SymmetricReductionStrategy tmpStrategy
        if good_input is None:
            p = self.reduce(p)
        if p._p == 0:
            return
        cdef int i = 0
        cdef int l = len(self._lm)
        cdef int newLength = len(p._p.coefficients())
        p = p/p.lc()
        if (self._min_lm is None) or (p.lm()<self._min_lm):
            self._min_lm = p.lm()
        while ((i<l) and (self._lengths[i]<newLength)):
            i+=1
        self._lm.insert(i, p)
        self._lengths.insert(i, newLength)
        #return
        i+=1
        l+=1
        if i<l:
            tmpStrategy = SymmetricReductionStrategy(self._parent, [p], tailreduce=False, good_input=True)
        else:
            return
        cdef int j
        while (i<l):
            q = tmpStrategy.reduce(self._lm[i].lm()) + tmpStrategy.reduce(self._lm[i].tail())
            if q._p==0:
                self._lm.pop(i)
                self._lengths.pop(i)
                l-=1
                i-=1
            else:
                q_len = len(q._p.coefficients())
                if q_len<self._lengths[i]:
                    self._lm.pop(i)
                    self._lengths.pop(i)
                    j = 0
                    while ((j<i) and (self._lengths[j]<q_len)):
                        j+=1
                    self._lm.insert(j, q)
                    self._lengths.insert(j, q_len)
            i+=1

    def reduce(self, p, notail=False, report=None):
        """
        Symmetric reduction of an infinite polynomial

        By default, tail reduction is done if and only if it was specified when
        creating self. If the optional parameter 'notail' is True, tail reduction
        is avoided. However, we do *not* guarantee that there will be no tail
        reduction at all in that case.

        If tail reduction shall be forced, use :meth:`.tailreduce`.

        Information on the progress of computation can be obtained by specifying the
        optional parameter ``report``.

        EXAMPLES::

            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: S = SymmetricReductionStrategy(X, [x[3]], tailreduce=True)
            sage: S.reduce(y[4]*x[1] + y[1]*x[4])
            y4*x1
            sage: S.reduce(y[4]*x[1] + y[1]*x[4], notail=True)
            y4*x1 + y1*x4

        Last, we demonstrate the 'report' option::

            sage: S = SymmetricReductionStrategy(X, [y[2]+x[1],y[2]*y[3]+y[1]*x[2]+x[4],x[3]+x[2]])
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
                x3 + x2,
                y2 + x1,
                y1*x2 + x4 + x1^2
            sage: S.reduce(y[3] + y[1]*x[3] + y[1]*x[1],report=True)
            :::>
            y1*x1 + x4 + x1^2 - x1

        Each ':' indicates that one reduction of the leading monomial was performed. Eventually, the '>'
        indicates that the computation is finished.

        """
        from sage.rings.polynomial.infinite_polynomial_element import InfinitePolynomial
        cdef list lml = self._lm
        if not lml:
            if report is not None:
                print '>'
            return p
        if p.lm()<self._min_lm:
            if report is not None:
                print '>'
            return p
        cdef list REDUCTOR
        while (1):
            REDUCTOR = []
            for q in lml:
                c, P, w = q.symmetric_cancellation_order(p)
                if (not (c is None)) and (c<=0):
                    REDUCTOR = [self(q**P)]
                    break
            if not REDUCTOR:
                new_p = p
                break
            p = self(p) # now this is a usual polynomial
            R = self._R
            if hasattr(p,'reduce'):
                new_p = InfinitePolynomial(self._parent, p.reduce([R(X) for X in REDUCTOR]), is_good_poly=True)
            else:
                new_p = InfinitePolynomial(self._parent, p % (REDUCTOR*R), is_good_poly=True)
            if report is not None:
                sys.stdout.write(':')
                sys.stdout.flush()
            if (new_p._p == p) or (new_p._p==0):
                break
            p = new_p # now this is an infinite polynomial
        p = new_p
        if (not self._tail) or notail or (p._p==0):
            if report is not None:
                print '>'
            return p
        # there remains to perform tail reduction
        REM = p.lt()
        p = p.tail()
        p = self.tailreduce(p, report=report)
        if report is not None:
            print '>'
        return p+REM

    def tailreduce(self, p, report=None):
        """
        Symmetric reduction of an infinite polynomial, with forced tail reduction

        Information on the progress of computation can be obtained by specifying the
        optional parameter 'report'.

        EXAMPLES::

            sage: from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
            sage: X.<x,y> = InfinitePolynomialRing(QQ)
            sage: S = SymmetricReductionStrategy(X, [x[3]])
            sage: S.reduce(y[4]*x[1] + y[1]*x[4])
            y4*x1 + y1*x4
            sage: S.tailreduce(y[4]*x[1] + y[1]*x[4])
            y4*x1


        Last, we demonstrate the 'report' option::

            sage: S = SymmetricReductionStrategy(X, [y[2]+x[1],y[2]*y[3]+y[1]*x[2]+x[4],x[3]+x[2]])
            sage: S
            Symmetric Reduction Strategy in Infinite polynomial ring in x, y over Rational Field, modulo
                x3 + x2,
                y2 + x1,
                y1*x2 + x4 + x1^2
            sage: S.tailreduce(y[3] + y[1]*x[3] + y[1]*x[1],report=True)
            T[3]:::>
            T[3]:>
            y1*x1 - x2 + x1^2 - x1

        The protocol means the following.
         * 'T[3]' means that we currently do tail reduction for a polynomial with three terms.
         * ':::>' means that there were three reductions of leading terms.
         * The tail of the result of the preceding reduction still has three terms. One reduction
           of leading terms was possible, and then the final result was obtained.
        """
        if not self._lm:
            return p
        OUT = p.parent()(0)
        while (p._p!=0):
            if report is not None:
                sys.stdout.write('T[%d]'%len(p._p.coefficients()))
                sys.stdout.flush()
            p = self.reduce(p, notail=True, report=report)
            OUT = OUT + p.lt()
            p = p.tail()
            if p.lm()<self._min_lm:
                return OUT+p
        return OUT
