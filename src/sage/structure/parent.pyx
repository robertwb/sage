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
import operator

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


## def make_parent_v0(_class, _dict, has_coerce_map_from):
##     """
##     This should work for any Python class deriving from this, as long
##     as it doesn't implement some screwy __new__() method.
##     """
##     cdef Parent new_object
##     new_object = _class.__new__(_class)
##     if not _dict is None:
##         new_object.__dict__ = _dict
##     new_object._has_coerce_map_from = has_coerce_map_from
##     return new_object

cdef class Parent(sage_object.SageObject):
    """
    Parents are the SAGE/mathematical analogues of container objects in computer science.
    """

    def __init__(self, coerce_from=[], actions=[], embeddings=[]):
        # TODO: many classes don't call this at all, but __new__ crashes SAGE
#        if len(coerce_from) > 0:
#            print type(self), coerce_from
        self._coerce_from_list = list(coerce_from)
        self._coerce_from_hash = {}
        self._action_list = list(actions)
        self._action_hash = {}

        cdef Parent other
        for mor in embeddings:
            other = mor.domain()
            print "embedding", self, " --> ", other
            print mor
            other.init_coerce() # TODO remove when we can
            other._coerce_from_list.append(mor)

        # old
        self._has_coerce_map_from = {}

    def init_coerce(self):
        if self._coerce_from_hash is None:
#            print "init_coerce() for ", type(self)
            self._coerce_from_list = []
            self._coerce_from_hash = {}
            self._action_list = []
            self._action_hash = {}


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


    #################################################################################
    # New Coercion support functionality
    #################################################################################

    def coerce_map_from(self, S):
        return self.coerce_map_from_c(S)

    cdef coerce_map_from_c(self, S):
        if S is self:
            from sage.categories.homset import Hom
            return Hom(self, self).identity()
        elif S == self:
            # non-unique parents
            from sage.categories.homset import Hom
            from sage.categories.morphism import CallMorphism
            return CallMorphism(Hom(S, self))
        try:
            if self._coerce_from_hash is None: # this is because parent.__init__() does not always get called
                self.init_coerce()
            return self._coerce_from_hash[S]
        except KeyError:
            pass
        if HAS_DICTIONARY(self):
            mor = self.coerce_map_from_impl(S)
        else:
            mor = self.coerce_map_from_c_impl(S)
        import sage.categories.morphism
        if mor is True:
            mor = sage.categories.morphism.CallMorphism(S, self)
        elif mor is False:
            mor = None
        elif mor is not None and not isinstance(mor, sage.categories.morphism.Morphism):
            raise TypeError, "coerce_map_from_impl must return a boolean, None, or an explicit Morphism"
        if mor is not None:
            self._coerce_from_hash[S] = mor # TODO: if this is None, could it be non-None in the future?
        return mor

    def coerce_map_from_impl(self, S):
        return self.coerce_map_from_c_impl(S)

    cdef coerce_map_from_c_impl(self, S):
        import sage.categories.morphism
        from sage.categories.morphism import Morphism
        from sage.categories.homset import Hom
        cdef Parent R
        for mor in self._coerce_from_list:
            if PY_TYPE_CHECK(mor, Morphism):
                R = mor.domain()
            else:
                R = mor
                mor = sage.categories.morphism.CallMorphism(Hom(R, self))
                i = self._coerce_from_list.index(R)
                self._coerce_from_list[i] = mor # cache in case we need it again
            if R is S:
                return mor
            else:
                connecting = R.coerce_map_from_c(S)
                if connecting is not None:
                    return mor * connecting

        # Piggyback off the old code for now
        # WARNING: when working on this, make sure circular dependancies aren't introduced!
        if self.has_coerce_map_from_c(S):
            if isinstance(S, type):
                S = Set_PythonType(S)
            return sage.categories.morphism.FormalCoercionMorphism(Hom(S, self))
        else:
            return None

    def get_action(self, S, op=operator.mul, self_on_left=True):
        return self.get_action_c(S, op, self_on_left)

    cdef get_action_c(self, S, op, bint self_on_left):
        try:
            if self._action_hash is None: # this is because parent.__init__() does not always get called
                self.init_coerce()
            return self._action_hash[S, op, self_on_left]
        except KeyError:
            pass
        if HAS_DICTIONARY(self):
            action = self.get_action_impl(S, op, self_on_left)
        else:
            action = self.get_action_c_impl(S, op, self_on_left)
        if action is not None:
            from sage.categories.action import Action
            if not isinstance(action, Action):
                raise TypeError, "get_action_impl must return None or an Action"
            self._action_hash[S, op, self_on_left] = action
        return action

    def get_action_impl(self, S, op, self_on_left):
        return self.get_action_c_impl(S, op, self_on_left)

    cdef get_action_c_impl(self, S, op, bint self_on_left):
        # G acts on S, G -> G', R -> S => G' acts on R (?)
        import sage.categories.morphism
        from sage.categories.action import Action, PrecomposedAction
        from sage.categories.morphism import Morphism
        from sage.categories.homset import Hom
        from coerce import LeftModuleAction, RightModuleAction
        cdef Parent R
        for action in self._action_list:
            if PY_TYPE_CHECK(action, Action):
                if self_on_left:
                    if action.left() is not self: continue
                    R = action.right()
                else:
                    if action.right() is not self: continue
                    R = action.left()
            elif op is operator.mul:
                try:
                    R = action
                    _register_pair(x,y) # to kill circular recursion
                    if self_on_left:
                        action = LeftModuleAction(S, self) # self is acted on from right
                    else:
                        action = RightModuleAction(S, self) # self is acted on from left
                    _unregister_pair(x,y)
                    i = self._action_list.index(R)
                    self._action_list[i] = action
                except TypeError:
                    continue
            else:
                continue # only try mul if not specified
            if R is S:
                return action
            else:
                connecting = R.coerce_map_from_c(S) # S -> R
                if connecting is not None:
                    if self_on_left:
                        return PrecomposedAction(action, None, connecting)
                    else:
                        return PrecomposedAction(action, connecting, None)


        if op is operator.mul and PY_TYPE_CHECK(S, Parent):
            from coerce import LeftModuleAction, RightModuleAction, LAction, RAction
            # Actors define _l_action_ and _r_action_
            # Acted-on elements define _lmul_ and _rmul_

            # TODO: if _xmul_/_x_action_ code does stuff like
            # if self == 0:
            #    return self
            # then _an_element_c() == 0 could be very bad.
            #
            #
            x = self._an_element_c()
            y = (<Parent>S)._an_element_c()
#            print "looking action ", x, y

            _register_pair(x,y) # this is to avoid possible infinite loops
            if self_on_left:
                try:
#                    print "RightModuleAction"
                    action = RightModuleAction(S, self) # this will test _lmul_
                    _unregister_pair(x,y)
#                    print "got", action
                    return action
                except (NotImplementedError, TypeError, AttributeError, ValueError):
                    pass

                try:
#                    print "LAction"
                    z = x._l_action_(y)
                    _unregister_pair(x,y)
                    return LAction(self, S)
                except (NotImplementedError, TypeError, AttributeError, ValueError):
                    pass

            else:
                try:
#                    print "LeftModuleAction"
                    action = LeftModuleAction(S, self) # this will test _rmul_
                    _unregister_pair(x,y)
#                    print "got", action
                    return action
                except (NotImplementedError, TypeError, AttributeError, ValueError):
                    pass

                try:
#                    print "RAction"
                    z = x._r_action_(y)
                    _unregister_pair(x,y)
                    return RAction(self, S)
                except (NotImplementedError, TypeError, AttributeError, ValueError):
                    pass

            _unregister_pair(x,y)
#            print "found nothing"

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
            elif P == self:      # canonically isomorphic parents in same category.
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
        if HAS_DICTIONARY(self):
            x = self.has_coerce_map_from_impl(S)
        else:
            x = self.has_coerce_map_from_c_impl(S)
        self._has_coerce_map_from[S] = x
        return x

    def has_coerce_map_from_impl(self, S):
        return self.has_coerce_map_from_c_impl(S)

    cdef has_coerce_map_from_c_impl(self, S):
        if not PY_TYPE_CHECK(S, Parent):
            return False
        try:
            self._coerce_c((<Parent>S)._an_element_c())
        except TypeError:
            return False
        except NotImplementedError, msg:
            raise NotImplementedError, "%s\nAlso, please make sure you have implemented has_coerce_map_from_impl or has_coerce_map_from_c_impl (or better _an_element_c_impl or _an_element_impl if possible) for %s"%(msg,self)
        return True

    def _an_element_impl(self):     # override this in Python
        r"""
        Implementation of a function that returns an element (often non-trivial)
        of a parent object.  Every parent object should implement it,
        unless the default implementation works.

        NOTE: Parent structures that are implemented in SageX should
        implement \code{_an_element_c_impl} instead.
        """
        return self._an_element_c_impl()

    cdef _an_element_c_impl(self):  # override this in SageX
        """
        Returns an element of self. Want it in sufficent generality
        that poorly-written functions won't work when they're not
        supposed to. This is cached so doesn't have to be super fast.
        """
        try:
            return self.gen(0)
        except:
            pass

        try:
            return self.gen()
        except:
            pass

        for x in ['_an_element_', 'pi', 1.2, 2, 1, 0]:
            try:
                return self(x)
            except (TypeError, NameError, NotImplementedError):
                pass

        raise NotImplementedError, "please implement _an_element_c_impl or _an_element_impl for %s"%self

    def _an_element(self):        # do not override this (call from Python)
        return self._an_element_c()

    cdef _an_element_c(self):     # do not override this (call from SageX)
        if not self.__an_element is None:
            return self.__an_element
        if HAS_DICTIONARY(self):
            self.__an_element = self._an_element_impl()
        else:
            self.__an_element = self._an_element_c_impl()
        return self.__an_element


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

##         # NOT NEEDED, since all attributes are public!
##     def __reduce__(self):
##         if HAS_DICTIONARY(self):
##             _dict = self.__dict__
##         else:
##             _dict = None
##         return (make_parent_v0, (self.__class__, _dict, self._has_coerce_map_from))

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


    ############################################################################
    # Set baseclass --
    ############################################################################


class Set_generic(Parent): # Cannot use Parent because Element._parent is ParentWithBase
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
        import sage.categories.all
        return sage.categories.all.Sets()

    def object(self):
        return self


class Set_PythonType(Set_generic):

    def __init__(self, theType):
        self._type = theType

    def __call__(self, x):
        return self._type(x)

    def __hash__(self):
        return hash(self._type)

    def __cmp__(self, other):
        if isinstance(other, Set_PythonType):
            return cmp(self._type, other._type)
        else:
            return cmp(self._type, other)

    def __contains__(self, x):
        return isinstance(x, self._type)

    def _latex_(self):
        return self._repr_()

    def _repr_(self):
        return "Set of Python objects of %s"%(str(self._type)[1:-1])

    def object(self):
        return self._type

    def cardinality(self):
        if self._type is bool:
            return 2
        else:
            import sage.rings.infinity
            return sage.rings.infinity.infinity


# These functions are to guerentee that user defined _lmul_, _rmul_, _l_action_, _r_action_ do
# not in turn call __mul__ on their arguments, leading to an infinite loop.

cdef object _coerce_test_list = []

class EltPair:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return type(self.x) is type(other.x) and self.x == other.x and type(self.y) is type(other.y) and self.y == other.y
    def __repr__(self):
        return "%r (%r), %r (%r)" % (self.x, type(self.x), self.y, type(self.y))

cdef bint _register_pair(x, y) except -1:
    both = EltPair(x,y)
#    print _coerce_test_list, " + ", both
    if both in _coerce_test_list:
#        print "Uh oh..."
#        print _coerce_test_list
#        print both
        raise NotImplementedError, "Infinite loop in multiplication of %s (parent %s) and %s (parent %s)!" % (x, x.parent(), y, y.parent())
    _coerce_test_list.append(both)
    return 0

cdef void _unregister_pair(x, y):
    try:
        _coerce_test_list.remove(EltPair(x,y))
    except ValueError:
        pass