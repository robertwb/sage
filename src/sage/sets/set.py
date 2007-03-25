"""
Sets

AUTHORS:
    -- Mike Hansen (2007-3-25) -- added differences and symmetric differences; fixed operators
    -- William Stein (2005) -- first version
    -- William Stein (2006-02-16) -- large number of documentation and examples; improved code
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
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

from sage.structure.element import Element
from sage.structure.parent import Parent
import sage.categories.all
from sage.misc.latex import latex
import sage.rings.infinity

def Set(X):
    r"""
    Create the underlying set of $X$.

    If $X$ is a list, tuple, Python set, or \code{X.is_finite()} is
    true, this returns a wrapper around Python's enumerated set type
    with extra functionality.  Otherwise it returns a more formal
    wrapper.

    EXAMPLES:
        sage: X = Set(GF(9,'a'))
        sage: X
        {0, 1, 2, a, a + 1, a + 2, 2*a, 2*a + 1, 2*a + 2}
        sage: type(X)
        <class 'sage.sets.set.Set_object_enumerated'>
        sage: Y = X.union(Set(QQ))
        sage: Y
        Set-theoretic union of Finite Field in a of size 3^2 and Rational Field
        sage: type(Y)
        <class 'sage.sets.set.Set_object_union'>
    """
    if is_Set(X):
        return X

    if isinstance(X, Element):
        raise TypeError, "Element has no defined underlying set"
    try:
        if isinstance(X, (list, tuple, set)) or X.is_finite():
            return Set_object_enumerated(X)
    except AttributeError:
        pass
    return Set_object(X)

def EnumeratedSet(X):
    """
    Return the enumerated set associated to $X$.

    The input object $X$ must be finite.

    EXAMPLES:
        sage: EnumeratedSet([1,1,2,3])
        {1, 2, 3}
        sage: EnumeratedSet(ZZ)
        Traceback (most recent call last):
        ...
        ValueError: X (=Integer Ring) must be finite
    """
    try:
        if not X.is_finite():
            raise ValueError, "X (=%s) must be finite"%X
    except AttributeError:
        pass
    return Set_object_enumerated(X)

def is_Set(x):
    """
    Returns true if $x$ is a SAGE Set (not to be confused with
    a Python 2.4 set).

    EXAMPLES:
        sage: is_Set([1,2,3])
        False
        sage: is_Set(set([1,2,3]))
        False
        sage: is_Set(Set([1,2,3]))
        True
        sage: is_Set(Set(QQ))
        True
        sage: is_Set(Primes())
        True
    """
    return isinstance(x, Set_generic)

class Set_generic(Parent):
    """
    Abstract base class for sets.
    """
    def category(self):
        """
        The category that this set belongs to, which is the category
        of all sets.

        EXAMPLES:
            sage: Set(QQ).category()
            Category of sets
        """
        return sage.categories.all.Sets()

    def object(self):
        return self

class Set_object(Set_generic):
    r"""
    A set attached to an almost arbitrary object.

    EXAMPLES:
        sage: K = GF(19)
        sage: Set(K)
        {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}
        sage: S = Set(K)

        sage: latex(S)
        \left\{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18\right\}
        sage: loads(S.dumps()) == S
        True

        sage: latex(Set(ZZ))
        \mathbf{Z}
    """
    def __init__(self, X):
        """
        Create a Set_object

        This function is called by the Set function; users
        shouldn't call this directly.

        EXAMPLES:
            sage: type(Set(QQ))
            <class 'sage.sets.set.Set_object'>
        """
        self.__object = X

    def _latex_(self):
        r"""
        Return latex representation of this set.

        This is often the same as the latex representation of this
        object when the object is infinite.

        EXAMPLES:
            sage: latex(Set(QQ))
            \mathbf{Q}

        When the object is finite or a special set then the latex
        representation can be more interesting.

            sage: print latex(Primes())
            \text{Set of all prime numbers: 2, 3, 5, 7, ...}
            sage: print latex(Set([1,1,1,5,6]))
            \left\{1, 5, 6\right\}
        """
        return latex(self.__object)

    def _repr_(self):
        """
        Print representation of this set.

        EXAMPLES:
            sage: X = Set(ZZ)
            sage: X
            Set of elements of Integer Ring
            sage: X.rename('{ integers }')
            sage: X
            { integers }
        """
        return "Set of elements of %s"%self.__object

    def __iter__(self):
        """
        Iterate over the elements of this set.

        EXAMPLES:
            sage: X = Set(ZZ)
            sage: I = X.__iter__()
            sage: I.next()
            0
            sage: I.next()
            1
            sage: I.next()
            -1
            sage: I.next()
            2
        """
        return self.__object.__iter__()

    def __contains__(self, x):
        """
        Return True if $x$ is in self.

        EXAMPLES:
            sage: X = Set(ZZ)
            sage: 5 in X
            True
            sage: GF(7)(3) in X
            True
            sage: 2/1 in X
            True
            sage: 2/1 in ZZ
            True
            sage: 2/3 in X
            False

        Finite fields better illustrate the difference between
        __contains__ for objects and their underlying sets.

            sage: X = Set(GF(7))
            sage: X
            {0, 1, 2, 3, 4, 5, 6}
            sage: 5/3 in X
            False
            sage: 5/3 in GF(7)
            False
            sage: Set(GF(7)).union(Set(GF(5)))
            {0, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 0}
            sage: Set(GF(7)).intersection(Set(GF(5)))
            {}
        """
        return x in self.__object

    def __cmp__(self, right):
        r"""
        Compare self and right.

        If right is not a Set compare types.  If right is also a Set,
        returns comparison on the underlying objects.

        \note{If $X < Y$ is true this does {\em not} necessarily mean
        that $X$ is a subset of $Y$.  Also, any two sets can be
        compared, which is a general Python philosophy.}

        EXAMPLES:
            sage: Set(ZZ) == Set(QQ)
            False
            sage: Set(ZZ) < Set(QQ)
            True
            sage: Primes() == Set(QQ)
            False
            sage: Primes() < Set(QQ)
            True

            sage: Set(QQ) == Primes()
            False
        """
        if not isinstance(right, Set_object):
            return cmp(type(right), type(Set_object))
        return cmp(self.__object, right.__object)

    def union(self, X):
        """
        Return the union of self and X.

        EXAMPLES:
            sage: Set(QQ).union(Set(ZZ))
            Set-theoretic union of Rational Field and Integer Ring
            sage: Set(QQ) + Set(ZZ)
            Set-theoretic union of Rational Field and Integer Ring
            sage: X = Set(QQ).union(Set(GF(3))); X
            Set-theoretic union of Rational Field and Finite Field of size 3
            sage: 2/3 in X
            True
            sage: GF(3)(2) in X
            True
            sage: GF(5)(2) in X
            False
            sage: Set(GF(7)) + Set(GF(3))
            {0, 1, 2, 3, 4, 5, 6, 1, 2, 0}
        """
        if is_Set(X):
            if self == X:
                return self
            return Set_object_union(self, X)
        raise TypeError, "X (=%s) must be a Set"%X

    def __add__(self, X):
        """
        Return the union of self and X.

        EXAMPLES:
            sage: Set(RealField()) + Set(QQ^5)
            Set-theoretic union of Real Field with 53 bits of precision and Vector space of dimension 5 over Rational Field
            sage: Set(GF(3)) + Set(GF(2))
            {0, 1, 2, 0, 1}
            sage: Set(GF(2)) + Set(GF(4,'a'))
            {0, 1, a, a + 1}
            sage: Set(GF(8,'b')) + Set(GF(4,'a'))
            {0, 1, b, b + 1, b^2, b^2 + 1, b^2 + b, b^2 + b + 1, a, a + 1, 1, 0}
        """
        return self.union(X)

    def __or__(self, X):
        """
        Return the union of self and X.

        EXAMPLES:
            sage: Set([2,3]) | Set([3,4])
            {2, 3, 4}
            sage: Set(ZZ) | Set(QQ)
            Set-theoretic union of Integer Ring and Rational Field
        """

        return self.union(X)

    def intersection(self, X):
        r"""
        Return the intersection of self and X.

        EXAMPLES:
            sage: X = Set(ZZ).intersection(Primes())
            sage: 4 in X
            False
            sage: 3 in X
            True

            sage: 2/1 in X
            True

            sage: X = Set(GF(9,'b')).intersection(Set(GF(27,'c')))
            sage: X
            {}

            sage: X = Set(GF(9,'b')).intersection(Set(GF(27,'b')))
            sage: X
            {}
        """
        if is_Set(X):
            if self == X:
                return self
            return Set_object_intersection(self, X)
        raise TypeError, "X (=%s) must be a Set"%X


    def difference(self, X):
        r"""
        Return the intersection of self and X.

        EXAMPLES:
            sage: X = Set(ZZ).difference(Primes())
            sage: 4 in X
            True
            sage: 3 in X
            False

            sage: 4/1 in X
            True

            sage: X = Set(GF(9,'b')).difference(Set(GF(27,'c')))
            sage: X
            {0, 1, 2, b, b + 1, b + 2, 2*b, 2*b + 1, 2*b + 2}

            sage: X = Set(GF(9,'b')).difference(Set(GF(27,'b')))
            sage: X
            {0, 1, 2, b, b + 1, b + 2, 2*b, 2*b + 1, 2*b + 2}
        """
        if is_Set(X):
            if self == X:
                return Set([])
            return Set_object_difference(self, X)
        raise TypeError, "X (=%s) must be a Set"%X

    def symmetric_difference(self, X):
        r"""
        Returns the symmetric difference of self and X.

        EXAMPLES:
            sage: X = Set([1,2,3]).symmetric_difference(Set([3,4]))
            sage: X
            {1, 2, 4}
        """

        if is_Set(X):
            if self == X:
                return Set([])
            return Set_object_symmetric_difference(self, X)
        raise TypeError, "X (=%s) must be a Set"%X


    def __sub__(self, X):
        """
        Return the difference of self and X.

        EXAMPLES:
            sage: X = Set(ZZ).difference(Primes())
            sage: Y = Set(ZZ) - Primes()
            sage: X == Y
            True
        """
        return self.difference(X)

    def __and__(self, X):
        """
        Returns the intersection of self and X.

        EXAMPLES:
            sage: Set([2,3]) & Set([3,4])
            {3}
            sage: Set(ZZ) & Set(QQ)
            Set-theoretic intersection of Integer Ring and Rational Field
        """

        return self.intersection(X)

    def __xor__(self, X):
        """
        Returns the symmetric difference of self and X.
        """
        return self.symmetric_difference(X)

    def cardinality(self):
        """
        Return the cardinality of this set, which is either an integer or Infinity.

        EXAMPLES:
            sage: Set(ZZ).cardinality()
            Infinity
            sage: Primes().cardinality()
            Infinity
            sage: Set(GF(5)).cardinality()
            5
            sage: Set(GF(5^2,'a')).cardinality()
            25
        """
        try:
            if not self.__object.is_finite():
                return sage.rings.infinity.infinity
        except AttributeError:
            pass
        try:
            return len(self.__object)
        except TypeError:
            raise NotImplementedError, "computation of cardinality of %s not yet implemented"%self.__object

    def object(self):
        """
        Return underlying object.

        EXAMPLES:
            sage: X = Set(QQ)
            sage: X.object()
            Rational Field
            sage: X = Primes()
            sage: X.object()
            Set of all prime numbers: 2, 3, 5, 7, ...
        """
        return self.__object

class Set_object_enumerated(Set_object):
    """
    A finite enumerated set.
    """
    def __init__(self, X):
        """
        EXAMPLES:
            sage: S = EnumeratedSet(GF(19)); S
            {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}
            sage: print latex(S)
            \left\{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18\right\}
            sage: loads(S.dumps()) == S
            True
        """
        Set_object.__init__(self, X)

    def cardinality(self):
        """
        EXAMPLES:
            sage: Set([1,1]).cardinality()
            1
        """
        return len(self.set())

    def __len__(self):
        """
        EXAMPLES:
            sage: len(Set([1,1]))
            1
        """
        return self.cardinality()


    def __iter__(self):
        for x in self.set():
            yield x

    def _latex_(self):
        return '\\left\\{' + ', '.join([latex(x) for x in self.set()])  + '\\right\\}'

    def _repr_(self):
        s = str(self.set())
        return "{" + s[5:-2] + "}"
        #    return "Finite set of elements of %s"%self.__object

    def set(self):
        """
        Return the Python set object associated to this set.

        Python has a notion of finite set, and often SAGE sets
        have an associated Python set.  This function returns
        that set.

        EXAMPLES:
            sage: X = Set(GF(8,'c'))
            sage: X
            {0, 1, c, c + 1, c^2, c^2 + 1, c^2 + c, c^2 + c + 1}
            sage: X.set()
            set([0, 1, c, c + 1, c^2, c^2 + 1, c^2 + c, c^2 + c + 1])
            sage: type(X.set())
            <type 'set'>
            sage: type(X)
            <class 'sage.sets.set.Set_object_enumerated'>
        """
        try:
            return self.__set
        except AttributeError:
            self.__set = set(self.object())
            return self.__set

    def __cmp__(self, other):
        """
        Compare the sets self and other.

        EXAMPLES:
            sage: X = Set(GF(8,'c'))
            sage: X == Set(GF(8,'c'))
            True
            sage: X == Set(GF(4,'a'))
            False
            sage: Set(QQ) == Set(ZZ)
            False
        """
        if isinstance(other, Set_object_enumerated):
            if self.set() == other.set():
                return 0
            return -1
        else:
            return Set_object.__cmp__(self, other)

    def union(self, other):
        """
        Return the union of self and other.

        EXAMPLES:
            sage: X = Set(GF(8,'c'))
            sage: Y = Set([GF(8,'c').0, 1, 2, 3])
            sage: X
            {0, 1, c, c + 1, c^2, c^2 + 1, c^2 + c, c^2 + c + 1}
            sage: Y
            {1, c, 3, 2}
            sage: X.union(Y)
            {0, 1, c, c + 1, c^2, c^2 + 1, c^2 + c, c^2 + c + 1, 2, 3}
        """
        if not isinstance(other, Set_object_enumerated):
            return Set_object.union(self, other)
        return Set_object_enumerated(self.set().union(other.set()))

    def intersection(self, other):
        """
        Return the intersection of self and other.

        EXAMPLES:
            sage: X = Set(GF(8,'c'))
            sage: Y = Set([GF(8,'c').0, 1, 2, 3])
            sage: X.intersection(Y)
            {1, c}
        """
        if not isinstance(other, Set_object_enumerated):
            return Set_object.intersection(self, other)
        return Set_object_enumerated(self.set().intersection(other.set()))

    def difference(self, other):
        """
        Returns the set difference self-other.

        EXAMPLES:
            sage: X = Set([1,2,3,4])
            sage: Y = Set([1,2])
            sage: X.difference(Y)
            {3, 4}
            sage: Z = Set(ZZ)
            sage: W = Set([2.5, 4, 5, 6])
            sage: W.difference(Z)
            {2.50000000000000}
        """
        if not isinstance(other, Set_object_enumerated):
            return Set([x for x in self if x not in other])
        return Set_object_enumerated(self.set().difference(other.set()))

    def symmetric_difference(self, other):
        """
        Returns the set difference self-other.

        EXAMPLES:
            sage: X = Set([1,2,3,4])
            sage: Y = Set([1,2])
            sage: X.symmetric_difference(Y)
            {3, 4}
            sage: Z = Set(ZZ)
            sage: W = Set([2.5, 4, 5, 6])
            sage: U = W.symmetric_difference(Z)
            sage: 2.5 in U
            True
            sage: 4 in U
            False
            sage: V = Z.symmetric_difference(W)
            sage: V == U
            True
            sage: 2.5 in V
            True
            sage: 6 in V
            False
        """
        if not isinstance(other, Set_object_enumerated):
            return Set_object.symmetric_difference(self, other)
        return Set_object_enumerated(self.set().symmetric_difference(other.set()))

class Set_object_union(Set_object):
    """
    A formal union of two sets.
    """
    def __init__(self, X, Y):
        r"""
        EXAMPLES:
            sage: S = Set(QQ^2)
            sage: T = Set(ZZ)
            sage: X = S.union(T); X
            Set-theoretic union of Vector space of dimension 2 over Rational Field and Integer Ring

            sage: latex(X)
            \mathbf{Q}^{2} \cup \mathbf{Z}

            sage: loads(X.dumps()) == X
            True
        """
        self.__X = X
        self.__Y = Y
        Set_object.__init__(self, self)

    def __cmp__(self, right):
        r"""
        Try to compare self and right.

        \note{Comparison is basically not implemented, or rather it
        could say sets are not equal even though they are.  I don't
        know how one could implement this for a generic union of sets
        in a meaningful manner.  So be careful when using this.}

        EXAMPLES:
            sage: Y = Set(ZZ^2).union(Set(ZZ^3))
            sage: X = Set(ZZ^3).union(Set(ZZ^2))
            sage: X == Y
            True
            sage: Y == X
            True

        This illustrates that equality testing for formal unions
        can be misleading in general.
            sage: Set(ZZ).union(Set(QQ)) == Set(QQ)
            False
        """
        if not is_Set(right):
            return -1
        if not isinstance(right, Set_object_union):
            return -1
        if self.__X == right.__X and self.__Y == right.__Y or \
           self.__X == right.__Y and self.__Y == right.__X:
            return 0
        return -1

    def _repr_(self):
        r"""
        Return string representation of self.

        EXAMPLES:
            sage: Set(ZZ).union(Set(GF(5)))
            Set-theoretic union of Integer Ring and Finite Field of size 5
        """
        return "Set-theoretic union of %s and %s"%(self.__X.object(),
                                                   self.__Y.object())

    def _latex_(self):
        r"""
        Return latex representation of self.

        EXAMPLES:
            sage: latex(Set(ZZ).union(Set(GF(5))))
            \mathbf{Z} \cup \left\{0, 1, 2, 3, 4\right\}
        """
        return '%s \\cup %s'%(latex(self.__X), latex(self.__Y))

    def __iter__(self):
        """
        Return iterator over the elements of self.

        EXAMPLES:
            sage: [x for x in Set(GF(3)).union(Set(GF(2)))]
            [0, 1, 2, 0, 1]
        """
        for x in self.__X:
            yield x
        for y in self.__Y:
            yield y

    def __contains__(self, x):
        """
        Returns True if x is an element of self.

        EXAMPLES:
            sage: X = Set(GF(3)).union(Set(GF(2)))
            sage: GF(5)(1) in X
            False
            sage: GF(3)(2) in X
            True
            sage: GF(2)(0) in X
            True
            sage: GF(5)(0) in X
            False
        """
        return x in self.__X or x in self.__Y

    def cardinality(self):
        """
        Return the cardinality of this set.

        EXAMPLES:
            sage: X = Set(GF(3)).union(Set(GF(2)))
            sage: X
            {0, 1, 2, 0, 1}
            sage: X.cardinality()
            5

            sage: X = Set(GF(3)).union(Set(ZZ))
            sage: X.cardinality()
            Infinity
        """
        return self.__X.cardinality() + self.__Y.cardinality()

class Set_object_intersection(Set_object):
    """
    Formal intersection of two sets.
    """
    def __init__(self, X, Y):
        r"""
        EXAMPLES:
            sage: S = Set(QQ^2)
            sage: T = Set(ZZ)
            sage: X = S.intersection(T); X
            Set-theoretic intersection of Vector space of dimension 2 over Rational Field and Integer Ring
            sage: latex(X)
            \mathbf{Q}^{2} \cap \mathbf{Z}

            sage: loads(X.dumps()) == X
            True
        """
        self.__X = X
        self.__Y = Y
        Set_object.__init__(self, self)


    def __cmp__(self, right):
        r"""
        Try to compare self and right.

        \note{Comparison is basically not implemented, or rather it
        could say sets are not equal even though they are.  I don't
        know how one could implement this for a generic intersection
        of sets in a meaningful manner.  So be careful when using
        this.}

        EXAMPLES:
            sage: Y = Set(ZZ).intersection(Set(QQ))
            sage: X = Set(QQ).intersection(Set(ZZ))
            sage: X == Y
            True
            sage: Y == X
            True

        This illustrates that equality testing for formal unions
        can be misleading in general.
            sage: Set(ZZ).intersection(Set(QQ)) == Set(QQ)
            False
        """
        if not is_Set(right):
            return -1
        if not isinstance(right, Set_object_intersection):
            return -1
        if self.__X == right.__X and self.__Y == right.__Y or \
           self.__X == right.__Y and self.__Y == right.__X:
            return 0
        return -1

    def _repr_(self):
        """
        Return string representation of self.

        EXAMPLES:
            sage: X = Set(ZZ).intersection(Set(QQ)); X
            Set-theoretic intersection of Integer Ring and Rational Field
            sage: X.rename('Z /\ Q')
            sage: X
            Z /\ Q
        """
        return "Set-theoretic intersection of %s and %s"%(self.__X.object(),
                                                          self.__Y.object())

    def _latex_(self):
        r"""
        Return latex representation of self.

        EXAMPLES:
            sage: X = Set(ZZ).intersection(Set(QQ))
            sage: latex(X)
            \mathbf{Z} \cap \mathbf{Q}
        """
        return '%s \\cap %s'%(latex(self.__X), latex(self.__Y))

    def __iter__(self):
        """
        Return iterator through elements of self.

        Self is a formal intersection of X and Y and this function is
        implemented by iterating through the elements of X and for
        each checking if it is in Y, and if yielding it.

        EXAMPLES:
            sage: X = Set(ZZ).intersection(Primes())
            sage: I = X.__iter__()
            sage: I.next()
            2
        """
        for x in self.__X:
            if x in self.__Y:
                yield x

    def __contains__(self, x):
        """
        Return true if self contains x.

        Since self is a formal intersection of X and Y this function
        returns true if both X and Y contains x.

        EXAMPLES:
            sage: X = Set(QQ).intersection(Set(RealField()))
            sage: 5 in X
            True
            sage: ComplexField().0 in X
            False
            sage: sqrt(2) in X
            False
            sage: pi in X
            False
            sage: pi in RR
            True
        """
        return x in self.__X and x in self.__Y

    def cardinality(self):
        """
        This tries to return the cardinality of this formal intersection.

        Note that this is not likely to work in very much generality,
        and may just hang if either set involved is infinite.

        EXAMPLES:
            sage: X = Set(GF(13)).intersection(Set(ZZ))
            sage: X.cardinality()
            13
        """
        return len(list(self))



class Set_object_difference(Set_object):
    """
    Formal difference of two sets.
    """
    def __init__(self, X, Y):
        r"""
        EXAMPLES:
            sage: S = Set(QQ)
            sage: T = Set(ZZ)
            sage: X = S.difference(T); X
            Set-theoretic difference between Rational Field and Integer Ring
            sage: latex(X)
            \mathbf{Q} - \mathbf{Z}

            sage: loads(X.dumps()) == X
            True
        """
        self.__X = X
        self.__Y = Y
        Set_object.__init__(self, self)


    def __cmp__(self, right):
        r"""
        Try to compare self and right.

        \note{Comparison is basically not implemented, or rather it
        could say sets are not equal even though they are.  I don't
        know how one could implement this for a generic intersection
        of sets in a meaningful manner.  So be careful when using
        this.}

        EXAMPLES:
            sage: Y = Set(ZZ).difference(Set(QQ))
            sage: Y == Set([])
            False
            sage: X = Set(QQ).difference(Set(ZZ))
            sage: Y == X
            False
            sage: Z = X.difference(Set(ZZ))
            sage: Z == X
            False

        This illustrates that equality testing for formal unions
        can be misleading in general.
            sage: X == Set(QQ).difference(Set(ZZ))
            True
        """
        if not is_Set(right):
            return -1
        if not isinstance(right, Set_object_difference):
            return -1
        if self.__X == right.__X and self.__Y == right.__Y:
            return 0
        return -1

    def _repr_(self):
        """
        Return string representation of self.

        EXAMPLES:
            sage: X = Set(QQ).difference(Set(ZZ)); X
            Set-theoretic difference between Rational Field and Integer Ring
            sage: X.rename('Q - Z')
            sage: X
            Q - Z
        """
        return "Set-theoretic difference between %s and %s"%(self.__X.object(),
                                                          self.__Y.object())

    def _latex_(self):
        r"""
        Return latex representation of self.

        EXAMPLES:
            sage: X = Set(QQ).difference(Set(ZZ))
            sage: latex(X)
            \mathbf{Q} - \mathbf{Z}
        """
        return '%s - %s'%(latex(self.__X), latex(self.__Y))

    def __iter__(self):
        """
        Return iterator through elements of self.

        Self is a formal difference of X and Y and this function is
        implemented by iterating through the elements of X and for
        each checking if it is not in Y, and if yielding it.

        EXAMPLES:
            sage: X = Set(ZZ).difference(Primes())
            sage: I = X.__iter__()
            sage: I.next()
            0
            sage: I.next()
            1
            sage: I.next()
            -1
            sage: I.next()
            -2
            sage: I.next()
            -3
        """
        for x in self.__X:
            if x not in self.__Y:
                yield x

    def __contains__(self, x):
        """
        Return true if self contains x.

        Since self is a formal intersection of X and Y this function
        returns true if both X and Y contains x.

        EXAMPLES:
            sage: X = Set(QQ).difference(Set(ZZ))
            sage: 5 in X
            False
            sage: ComplexField().0 in X
            False
            sage: sqrt(2) in X
            False
            sage: 5/2 in X
            True
        """
        return x in self.__X and x not in self.__Y

    def cardinality(self):
        """
        This tries to return the cardinality of this formal intersection.

        Note that this is not likely to work in very much generality,
        and may just hang if either set involved is infinite.

        EXAMPLES:
            sage: X = Set(GF(13)).difference(Set(Primes()))
            sage: X.cardinality()
            8
        """
        return len(list(self))

class Set_object_symmetric_difference(Set_object):
    """
    Formal symmetric difference of two sets.
    """
    def __init__(self, X, Y):
        r"""
        EXAMPLES:
            sage: S = Set(QQ)
            sage: T = Set(ZZ)
            sage: X = S.symmetric_difference(T); X
            Set-theoretic symmetric difference of Rational Field and Integer Ring
            sage: latex(X)
            \mathbf{Q} \bigtriangleup \mathbf{Z}

            sage: loads(X.dumps()) == X
            True
        """
        self.__X = X
        self.__Y = Y
        Set_object.__init__(self, self)


    def __cmp__(self, right):
        r"""
        Try to compare self and right.

        \note{Comparison is basically not implemented, or rather it
        could say sets are not equal even though they are.  I don't
        know how one could implement this for a generic symmetric difference
        of sets in a meaningful manner.  So be careful when using
        this.}

        EXAMPLES:
            sage: Y = Set(ZZ).symmetric_difference(Set(QQ))
            sage: X = Set(QQ).symmetric_difference(Set(ZZ))
            sage: X == Y
            True
            sage: Y == X
            True

        """
        if not is_Set(right):
            return -1
        if not isinstance(right, Set_object_symmetric_difference):
            return -1
        if self.__X == right.__X and self.__Y == right.__Y or \
           self.__X == right.__Y and self.__Y == right.__X:
            return 0
        return -1

    def _repr_(self):
        """
        Return string representation of self.

        EXAMPLES:
            sage: X = Set(ZZ).symmetric_difference(Set(QQ)); X
            Set-theoretic symmetric difference of Integer Ring and Rational Field
            sage: X.rename('Z symdif Q')
            sage: X
            Z symdif Q
        """
        return "Set-theoretic symmetric difference of %s and %s"%(self.__X.object(),
                                                          self.__Y.object())

    def _latex_(self):
        r"""
        Return latex representation of self.

        EXAMPLES:
            sage: X = Set(ZZ).symmetric_difference(Set(QQ))
            sage: latex(X)
            \mathbf{Z} \bigtriangleup \mathbf{Q}
        """
        return '%s \\bigtriangleup %s'%(latex(self.__X), latex(self.__Y))

    def __iter__(self):
        """
        Return iterator through elements of self.

        Self is the formal symmetric difference of X and Y. This function is
        implemented by first iterating through the elements of X and
        yielding it if it is not in Y.  Then it will iterate throw all
        the elements of Y and yielding it if it is not in X.

        EXAMPLES:
            sage: X = Set(ZZ).symmetric_difference(Primes())
            sage: I = X.__iter__()
            sage: I.next()
            0
            sage: I.next()
            1
            sage: I.next()
            -1
            sage: I.next()
            -2
            sage: I.next()
            -3
        """
        for x in self.__X:
            if x not in self.__Y:
                yield x

        for y in self.__Y:
            if y not in self.__X:
                yield y


    def __contains__(self, x):
        """
        Return true if self contains x.

        Since self is the formal symmetric difference of X and Y this function
        returns true if either X or Y (but now both) contains x.

        EXAMPLES:
            sage: X = Set(QQ).symmetric_difference(Primes())
            sage: 4 in X
            True
            sage: ComplexField().0 in X
            False
            sage: sqrt(2) in X
            False
            sage: pi in X
            False
            sage: 5/2 in X
            True
            sage: 3 in X
            False
        """
        return (x in self.__X and x not in self.__Y) \
               or (x in self.__Y and x not in self.__X)

    def cardinality(self):
        """
        This tries to return the cardinality of this formal symmetric difference.

        Note that this is not likely to work in very much generality,
        and may just hang if either set involved is infinite.

        EXAMPLES:
            sage: X = Set(GF(13)).symmetric_difference(Set(range(5)))
            sage: X.cardinality()
            8
        """
        return len(list(self))
