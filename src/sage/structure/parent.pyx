r"""
Base class for parent objects

CLASS HIEARCHY:

SageObject
    Parent
        ParentWithBase
            ParentWithGens
"""

###############################################################################
#   SAGE: System for Algebra and Geometry Experimentation
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

cimport sage_object

include '../ext/python_object.pxi'
include '../ext/python_bool.pxi'
include '../ext/stdsage.pxi'

def is_Parent(x):
    """
    Return True if x is a parent object, i.e., derives from
    sage.structure.parent.Parent and False otherwise.

    EXAMPLES:
        sage: is_Parent(2/3)
        False
        sage: is_Parent(ZZ)
        True
        sage: is_Parent(Primes())
        True
    """
    return PyBool_FromLong(PyObject_TypeCheck(x, Parent))

cdef class Parent(sage_object.SageObject):
    """
    Parents are the SAGE/mathematical analogues of container objects in computer science.
    """
    def __init__(self):
        self._has_coerce_map_from = {}

    #############################################################################
    # Containment testing
    #############################################################################
    def __contains__(self, x):
        r"""
        True if there is an element of self that is equal to x under ==.

        For many structures we test this by using \code{__call__} and
        then testing equality between x and the result.

        EXAMPLES:
            sage: 2 in Integers(7)
            True
            sage: 2 in ZZ
            True
            sage: Integers(7)(3) in ZZ
            True
            sage: 3/1 in ZZ
            True
            sage: 5 in QQ
            True
            sage: I in RR
            False
        """
        try:
            x2 = self(x)
            return x2 == x
        except TypeError:
            return False
        return True


    #################################################################################
    # Coercion support functionality
    #################################################################################

    def _coerce_(self, x):            # Call this from Python (do not override!)
        return self._coerce_c(x)

    cdef _coerce_c(self, x):          # DO NOT OVERRIDE THIS (call it)
        try:
            P = x.parent()   # todo -- optimize
            if P is self:
                return x
            elif P == self:
                return self(x)
        except AttributeError, msg:
            pass
        if HAS_DICTIONARY(self):
            return self._coerce_impl(x)
        else:
            return self._coerce_c_impl(x)

    cdef _coerce_c_impl(self, x):     # OVERRIDE THIS FOR SAGEX CLASES
        """
        Canonically coerce x in assuming that the parent of x is not
        equal to self.
        """
        raise TypeError

    def _coerce_impl(self, x):        # OVERRIDE THIS FOR PYTHON CLASSES
        """
        Canonically coerce x in assuming that the parent of x is not
        equal to self.
        """
        return self._coerce_c_impl(x)

    def _coerce_try(self, x, v):
        """
        Given a list v of rings, try to coerce x canonically into each
        one in turn.  Return the __call__ coercion of the result into
        self of the first canonical coercion that succeeds.  Raise a
        TypeError if none of them succeed.

        INPUT:
             x -- Python object
             v -- parent object or list (iterator) of parent objects
        """
        if not isinstance(v, list):
            v = [v]
        for R in v:
            try:
                y = R._coerce_(x)
                return self(y)
            except TypeError, msg:
                pass
        raise TypeError, "no canonical coercion of element into self"

    def _coerce_self(self, x):
        return self._coerce_self_c(x)

    cdef _coerce_self_c(self, x):
        """
        Try to canonically coerce x into self.
        Return result on success or raise TypeError on failure.
        """
        # todo -- optimize?
        try:
            P = x.parent()
            if P is self:
                return x
            elif P == self:
                return self(x)
        except AttributeError:
            pass
        raise TypeError, "no canonical coercion to self defined"

    def has_coerce_map_from(self, S):
        return self.has_coerce_map_from_c(S)

    cdef has_coerce_map_from_c(self, S):
        """
        Return True if there is a natural map from S to self.
        Otherwise, return False.
        """
        try:
            return self._has_coerce_map_from[S]
        except KeyError:
            pass
        except TypeError:
            self._has_coerce_map_from = {}
        if not PY_TYPE_CHECK(S, Parent):
            return False
        try:
            self._coerce_c(S(0))
        except TypeError:
            self._has_coerce_map_from[S] = False
            return False
        self._has_coerce_map_from[S] = True
        return True

    ################################################
    # Comparison of parent objects
    ################################################
    cdef _richcmp(left, right, int op):
        """
        Compare left and right.
        """
        cdef int r

        if not PY_TYPE_CHECK(right, Parent) or not PY_TYPE_CHECK(left, Parent):
            # One is not a parent -- use arbitrary ordering
            if (<PyObject*>left) < (<PyObject*>right):
                r = -1
            elif (<PyObject*>left) > (<PyObject*>right):
                r = 1
            else:
                r = 0

        else:
            # Both are parents -- but need *not* have the same type.
            if HAS_DICTIONARY(left):
                r = left.__cmp__(right)
            else:
                r = left._cmp_c_impl(right)

        if op == 0:  #<
            return PyBool_FromLong(r  < 0)
        elif op == 2: #==
            return PyBool_FromLong(r == 0)
        elif op == 4: #>
            return PyBool_FromLong(r  > 0)
        elif op == 1: #<=
            return PyBool_FromLong(r <= 0)
        elif op == 3: #!=
            return PyBool_FromLong(r != 0)
        elif op == 5: #>=
            return PyBool_FromLong(r >= 0)

##     ####################################################################
##     # For a derived SageX class, you **must** put the following in
##     # your subclasses, in order for it to take advantage of the
##     # above generic comparison code.  You must also define
##     # _cmp_c_impl for a SageX class.
##     #
##     # For a derived Python class, simply define __cmp__.
##     ####################################################################
##     def __richcmp__(left, right, int op):
##         return (<Parent>left)._richcmp(right, op)

    cdef int _cmp_c_impl(left, Parent right) except -2:
        pass
        # this would be nice to do, but we can't since
        # it leads to infinite recurssions -- and is slow -- and this
        # stuff must be fast!
        #if right.has_coerce_map_from(left):
        #    if left.has_coerce_map_from(right):
        #        return 0
        #    else:
        #        return -1
        if (<PyObject*>left) < (<PyObject*>right):
            return -1
        elif (<PyObject*>left) > (<PyObject*>right):
            return 1
        return 0

##     def __cmp__(left, right):
##         return left._cmp_c_impl(right)   # default


    ############################################################################
    # Homomorphism --
    ############################################################################
    def Hom(self, codomain, cat=None):
        r"""
        self.Hom(codomain, cat=None):

        Return the homspace \code{Hom(self, codomain, cat)} of all
        homomorphisms from self to codomain in the category cat.  The
        default category is \code{self.category()}.

        EXAMPLES:
            sage: R.<x,y> = PolynomialRing(QQ, 2)
            sage: R.Hom(QQ)
            Set of Homomorphisms from Polynomial Ring in x, y over Rational Field to Rational Field

        Homspaces are defined for very general \sage objects, even elements of familiar rings.
            sage: n = 5; Hom(n,7)
            Set of Morphisms from 5 to 7 in Category of elements of Integer Ring
            sage: z=(2/3); Hom(z,8/1)
            Set of Morphisms from 2/3 to 8 in Category of elements of Rational Field

        This example illustrates the optional third argument:
            sage: QQ.Hom(ZZ, Sets())
            Set of Morphisms from Rational Field to Integer Ring in Category of sets
        """
        try:
            return self._Hom_(codomain, cat)
        except (TypeError, AttributeError):
            pass
        from sage.categories.all import Hom
        return Hom(self, codomain, cat)
