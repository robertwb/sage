r"""
Base class for parent objects

CLASS HIEARCHY:

SageObject
    CategoryObject
        Parent


TESTS:
This came up in some subtle bug once.
    sage: gp(2) + gap(3)
    5
"""
cimport element
cimport sage.categories.morphism as morphism

cdef int bad_parent_warnings = 0
cdef int unique_parent_warnings = 0

# TODO: define this once?

cdef object elt_parent = None

cdef inline parent_c(x):
    if PY_TYPE_CHECK(x, element.Element):
        return (<element.Element>x)._parent
    elif hasattr(x, 'parent'):
        return x.parent()
    else:
        return <object>PY_TYPE(x)

cdef _record_exception():
    from element import get_coercion_model
    get_coercion_model()._record_exception()

cdef object _Integer
cdef bint is_Integer(x):
    global _Integer
    if _Integer is None:
        from sage.rings.integer import Integer as _Integer
    return PY_TYPE_CHECK_EXACT(x, _Integer) or PY_TYPE_CHECK_EXACT(x, int)

# for override testing
cdef extern from "descrobject.h":
    ctypedef struct PyMethodDef:
        void *ml_meth
    ctypedef struct PyMethodDescrObject:
        PyMethodDef *d_method
    void* PyCFunction_GET_FUNCTION(object)
    bint PyCFunction_Check(object)

cdef extern from *:
    Py_ssize_t PyDict_Size(object)
    Py_ssize_t PyTuple_GET_SIZE(object)


###############################################################################
#   SAGE: System for Algebra and Geometry Experimentation
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

import operator
import weakref

from category_object import CategoryObject
from generators import Generators

# TODO: Theses should probably go in the printer module (but lots of stuff imports them from parent)
from category_object import localvars

cdef object BuiltinMethodType = type(repr)

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
    return PY_TYPE_CHECK(x, Parent)


cdef object all_parents = [] #weakref.WeakKeyDictionary()


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

cdef class Parent(category_object.CategoryObject):
    """
    Parents are the SAGE/mathematical analogues of container objects
    in computer science.
    """

    def __init__(self, base=None, *, categories=[], element_constructor=None, gens=None, names=None, normalize=True, **kwds):
        CategoryObject.__init__(self, categories, base)
        if len(kwds) > 0:
            if bad_parent_warnings:
                print "Illegal keywords for %s: %s" % (type(self), kwds)
        # TODO: many classes don't call this at all, but __new__ crashes SAGE
        if bad_parent_warnings:
            if element_constructor is None:
                element_constructor = self._element_constructor_
            elif not callable(element_constructor):
                print "coerce BUG: Bad element_constructor provided", type(self), type(element_constructor), element_constructor
        if gens is not None:
            self._populate_generators_(gens, names, normalize)
        elif names is not None:
            self._assign_names(names, normalize)
        self._element_constructor = element_constructor
        if hasattr(element_constructor, 'init_no_parent'):
            self._element_init_pass_parent = not element_constructor.init_no_parent
        elif PY_TYPE_CHECK(element_constructor, types.MethodType):
            self._element_init_pass_parent = False
        elif PY_TYPE_CHECK(element_constructor, BuiltinMethodType):
            self._element_init_pass_parent = element_constructor.__self__ is not self
        else:
            self._element_init_pass_parent = True
        self._coerce_from_list = []
        self._coerce_from_hash = {}
        self._action_list = []
        self._action_hash = {}
        self._convert_from_list = []
        self._convert_from_hash = {}
        self._embedding = None
        self._initial_coerce_list = []
        self._initial_action_list = []
        self._initial_convert_list = []
        all_parents.append(self)
#        try:
#            all_parents[self] = True # this is a weak reference
#        except:
#            print "couldn't weakref", type(self)

    def init_coerce(self, bint verbose=True):
        if self._coerce_from_hash is None:
            if verbose:
                print "init_coerce() for ", type(self)
                raise ZeroDivisionError, "hello"
            self._initial_coerce_list = []
            self._initial_action_list = []
            self._initial_convert_list = []
            self._coerce_from_list = []
            self._coerce_from_hash = {}
            self._action_list = []
            self._action_hash = {}
            self._convert_from_list = []
            self._convert_from_hash = {}
            self._embedding = None

    def _introspect_coerce(self):
        return {
            '_coerce_from_list': self._coerce_from_list,
            '_coerce_from_hash': self._coerce_from_hash,
            '_action_list': self._action_list,
            '_action_hash': self._action_hash,
            '_convert_from_list': self._convert_from_list,
            '_convert_from_hash': self._convert_from_hash,
            '_embedding': self._embedding,
            '_initial_coerce_list': self._initial_coerce_list,
            '_initial_action_list': self._initial_action_list,
            '_initial_convert_list': self._initial_convert_list,
            '_element_init_pass_parent': self._element_init_pass_parent,

        }

    def __getstate__(self):
        #print self._introspect_coerce()
        d = CategoryObject.__getstate__(self)
        d['_embedding'] = self._embedding
        d['_element_constructor'] = self._element_constructor
        d['_convert_method_name'] = self._convert_method_name
        d['_element_init_pass_parent'] = self._element_init_pass_parent
        d['_initial_coerce_list'] = self._initial_coerce_list
        d['_initial_action_list'] = self._initial_action_list
        d['_initial_convert_list'] = self._initial_convert_list
        return d

    def __setstate__(self, d):
        CategoryObject.__setstate__(self, d)
        try:
            version = d['_pickle_version']
        except KeyError:
            version = 0
        if version == 1:
            self._element_constructor = d['_element_constructor']
            self.init_coerce(False) # Really, do we want to init this with the same initial data as before?
            self._populate_coercion_lists_(coerce_list=d['_initial_coerce_list'] or [],
                                           action_list=d['_initial_action_list'] or [],
                                           convert_list=d['_initial_convert_list'] or [],
                                           embedding=d['_embedding'],
                                           convert_method_name=d['_convert_method_name'],
                                           init_no_parent=not d['_element_init_pass_parent'])

    def __call__(self, x=0, *args, **kwds):
        cdef Py_ssize_t i
        R = parent_c(x)
        cdef bint no_extra_args = PyTuple_GET_SIZE(args) == 0 and PyDict_Size(kwds) == 0
        if R is self and no_extra_args:
            return x
        if self._coerce_from_hash is None: # this is because parent.__init__() does not always get called
            self.init_coerce()
        cdef morphism.Morphism mor = <morphism.Morphism>self.convert_map_from(R)
        if mor is not None:
            try:
                if no_extra_args:
                    return mor._call_(x)
                else:
                    return mor._call_with_args(x, args, kwds)
            except TypeError, msg:
                self._convert_from_hash.pop(mor.domain(), None)
                for i from 0 <= i < len(self._convert_from_list):
                    if self._convert_from_list[i] is mor:
                        self._convert_from_list = self._convert_from_list[:i] + self._convert_from_list[i+1:]
                        break
                raise

        raise TypeError, "No conversion defined from %s to %s"%(R, self)

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
            sage: SR(2) in ZZ
            True
        """
        try:
            x2 = self(x)
            return bool(x2 == x)
        except TypeError:
            return False

    cpdef coerce(self, x):
        """
        Return x as an element of self, if and only if there is a canonical
        coercion from the parent of x to self.

        EXAMPLES:
            sage: QQ.coerce(ZZ(2))
            2
            sage: ZZ.coerce(QQ(2))
            Traceback (most recent call last):
            ...
            TypeError: no cannonical coercion from Rational Field to Integer Ring

        We make an exception for zero:
            sage: V = GF(7)^7
            sage: V.coerce(0)
            (0, 0, 0, 0, 0, 0, 0)
        """
        mor = self.coerce_map_from(parent_c(x))
        if mor is None:
            if is_Integer(x) and not x:
                try:
                    return self(0)
                except:
                    _record_exception()
            raise TypeError, "no cannonical coercion from %s to %s" % (parent_c(x), self)
        else:
            return (<morphism.Morphism>mor)._call_(x)

    def list(self):
        """
        Return a list of all elements in this object, if possible (the
        object must define an iterator).
        """
        try:
            if self._list is not None:
                return self._list
        except AttributeError:
            try:
                self._list = list(self.__iter__())
                return self._list
            except AttributeError:
                return list(self.__iter__())

    def __nonzero__(self):
        return True

    def __len__(self):
        return len(self.list())

    def __getitem__(self, n):
        return self.list()[n]

    def __getslice__(self,  Py_ssize_t n,  Py_ssize_t m):
        return self.list()[int(n):int(m)]

    #################################################################################
    # Generators and Homomorphisms
    #################################################################################

    def _is_valid_homomorphism_(self, codomain, im_gens):
       r"""
       Return True if \code{im_gens} defines a valid homomorphism
       from self to codomain; otherwise return False.

       If determining whether or not a homomorphism is valid has not
       been implemented for this ring, then a NotImplementedError exception
       is raised.
       """
       raise NotImplementedError, "Verification of correctness of homomorphisms from %s not yet implmented."%self

    def hom(self, im_gens, codomain=None, check=None):
       r"""
       Return the unique homomorphism from self to codomain that
       sends \code{self.gens()} to the entries of \code{im_gens}.
       Raises a TypeError if there is no such homomorphism.

       INPUT:
           im_gens -- the images in the codomain of the generators of
                      this object under the homomorphism
           codomain -- the codomain of the homomorphism
           check -- whether to verify that the images of generators extend
                    to define a map (using only canonical coercisions).

       OUTPUT:
           a homomorphism self --> codomain

       \note{As a shortcut, one can also give an object X instead of
       \code{im_gens}, in which case return the (if it exists)
       natural map to X.}

       EXAMPLE: Polynomial Ring
       We first illustrate construction of a few homomorphisms
       involving a polynomial ring.

           sage: R.<x> = PolynomialRing(ZZ)
           sage: f = R.hom([5], QQ)
           sage: f(x^2 - 19)
           6

           sage: R.<x> = PolynomialRing(QQ)
           sage: f = R.hom([5], GF(7))
           Traceback (most recent call last):
           ...
           TypeError: images do not define a valid homomorphism

           sage: R.<x> = PolynomialRing(GF(7))
           sage: f = R.hom([3], GF(49,'a'))
           sage: f
           Ring morphism:
             From: Univariate Polynomial Ring in x over Finite Field of size 7
             To:   Finite Field in a of size 7^2
             Defn: x |--> 3
           sage: f(x+6)
           2
           sage: f(x^2+1)
           3

       EXAMPLE: Natural morphism
           sage: f = ZZ.hom(GF(5))
           sage: f(7)
           2
           sage: f
           Ring Coercion morphism:
             From: Integer Ring
             To:   Finite Field of size 5

       There might not be a natural morphism, in which case a TypeError exception is raised.
           sage: QQ.hom(ZZ)
           Traceback (most recent call last):
           ...
           TypeError: Natural coercion morphism from Rational Field to Integer Ring not defined.
       """
       if isinstance(im_gens, Parent):
           return self.Hom(im_gens).natural_map()
       from sage.structure.all import Sequence
       if codomain is None:
           im_gens = Sequence(im_gens)
           codomain = im_gens.universe()
       if isinstance(im_gens, (Sequence, Generators)):
            im_gens = list(im_gens)
       if check is None:
           return self.Hom(codomain)(im_gens)
       else:
           return self.Hom(codomain)(im_gens, check=check)

    #################################################################################
    # New New Coercion support functionality
    #################################################################################

    def _populate_coercion_lists_(self, coerce_list=[], action_list=[], convert_list=[], embedding=None, convert_method_name=None, init_no_parent=None):
        """
        This function allows one to specify coercions, actions, conversions
        and embeddings involving this parent.

        IT SHOULD ONLY BE CALLED DURING THE __INIT__ method, often at the end.

        INPUT:
            coerce_list  -- a list of coercion Morphisms to self and
                            parents with cannonical coercions to self
            action_list  -- a list of actions on and by self
            convert_list -- a list of conversion Morphisms to self and
                            parents with conversions to self
            embedding    -- a single Morphism from self
            convert_method_name -- a name to look for that other elements
                            can implement to create elements of self (e.g. _integer_)
            init_no_parent -- if True omit passing self in as the first
                              argument of element_constructor for conversion. This is
                              useful if parents are unique, or element_constructor is
                              a bound method.
        """
        if not PY_TYPE_CHECK(coerce_list, list):
            raise ValueError, "%s_populate_coercion_lists_: coerce_list is type %s, must be list" % (type(coerce_list), type(self))
        if not PY_TYPE_CHECK(action_list, list):
            raise ValueError, "%s_populate_coercion_lists_: action_list is type %s, must be list" % (type(action_list), type(self))
        if not PY_TYPE_CHECK(convert_list, list):
            raise ValueError, "%s_populate_coercion_lists_: convert_list is type %s, must be list" % (type(convert_list), type(self))

        self._initial_coerce_list = coerce_list
        self._initial_action_list = action_list
        self._initial_convert_list = convert_list

        from sage.categories.morphism import Morphism

        self._convert_method_name = convert_method_name
        if init_no_parent is not None:
            self._element_init_pass_parent = not init_no_parent

        for mor in coerce_list:
            if PY_TYPE_CHECK(mor, Morphism):
                if mor.codomain() is not self:
                    raise ValueError, "Morphism's codomain must be self (%s) is not (%s)" % (self, mor.codomain())
                self._coerce_from_list.append(mor)
                self._coerce_from_hash[mor.domain()] = mor
            elif PY_TYPE_CHECK(mor, Parent) or PY_TYPE_CHECK(mor, type):
                P = mor
                mor = self._generic_convert_map(mor)
                self._coerce_from_list.append(mor)
                self._coerce_from_hash[P] = mor
            else:
                raise TypeError, "entries in the coerce_list must be parents or morphisms (got %s)" % type(mor)

        from sage.categories.action import Action
        for action in action_list:
            if isinstance(action, Action):
                if action.actor() is self:
                    self._action_list.append(action)
                    self._action_list[action.domain(), action.operation(), action.is_left()] = action
                elif action.domain() is self:
                    self._action_list.append(action)
                    self._action_list[action.actor(), action.operation(), not action.is_left()] = action
                else:
                    raise ValueError, "Action must involve self"
            else:
                raise TypeError, "entries in the action_list must be actions"

        for mor in convert_list:
            if isinstance(mor, Morphism):
                if mor.codomain() is not self:
                    raise ValueError, "Morphism's codomain must be self"
                self._convert_from_list.append(mor)
                self._convert_from_hash[mor.domain()] = mor
            elif PY_TYPE_CHECK(mor, Parent) or PY_TYPE_CHECK(mor, type):
                mor = self._generic_convert_map(mor)
                self._convert_from_list.append(mor)
                self._convert_from_hash[mor.domain()] = mor
            else:
                raise TypeError, "entries in the convert_list must be parents or morphisms"

        if isinstance(embedding, Morphism):
            if embedding.domain() is not self:
                raise ValueError, "Morphism's domain must be self"
            self._embedding = embedding
        elif isinstance(embedding, Parent):
            self._embedding = embedding._generic_convert_map(self)
        elif embedding is not None:
            raise TypeError, "embedding must be a parent or morphism"

    def get_embedding(self):
        return self._embedding

    cpdef _generic_convert_map(self, S):
        import coerce_maps
        if self._convert_method_name is not None:
            # handle methods like _integer_
            if PY_TYPE_CHECK(S, type):
                element_constructor = S
            elif PY_TYPE_CHECK(S, Parent):
                element_constructor = (<Parent>S)._element_constructor
                if not PY_TYPE_CHECK(element_constructor, type):
                    # if element_constructor is not an actual class, get the element class
                    element_constructor = type(S.an_element())
            else:
                element_constructor = None
            if element_constructor is not None and hasattr(element_constructor, self._convert_method_name):
                return coerce_maps.NamedConvertMorphism(S, self, self._convert_method_name)

        if self._element_init_pass_parent:
            return coerce_maps.DefaultConvertMorphism(S, self)
        else:
            return coerce_maps.DefaultConvertMorphism_unique(S, self)

    cpdef bint has_coerce_map_from(self, S) except -2:
        """
        Return True if there is a natural map from S to self.
        Otherwise, return False.
        """
        if S is self:
            return True
        elif S == self:
            if unique_parent_warnings:
                print "Warning: non-unique parents %s"%(type(S))
            return True
        if self._coerce_from_hash is None:
            self.init_coerce()
        if self._coerce_from_hash.has_key(S):
            return self._coerce_from_hash[S] is not None
        if PY_TYPE_CHECK(S, Parent):
            if (<Parent>S)._embedding is not None and (<Parent>S)._embedding.codomain() is self:
                return True
        return self._has_coerce_map_from_(S)

    cpdef bint _has_coerce_map_from_(self, S) except -2:
        # We first check (using some cython trickery) to see if coerce_map_from_ has been overridden.
        # If it has, then we can just (by default) call it and see if it returns None or not.
        # Otherwise we return False by default (so that no canonical coercions exist)
        if HAS_DICTIONARY(self):
            method = (<object>self)._coerce_map_from_
            if PyCFunction_Check(method) and \
                (<PyMethodDescrObject *>(<object>Parent).coerce_map_from).d_method.ml_meth == PyCFunction_GET_FUNCTION(method):
                return False
        elif Parent._coerce_map_from_ == self._coerce_map_from_:
            return False
        # At this point we are guaranteed coerce_map_from is actually implemented
        return self.coerce_map_from(S) is not None

    cpdef coerce_map_from(self, S):
        if S is self:
            from sage.categories.homset import Hom
            return Hom(self, self).identity()

        elif isinstance(S, Set_PythonType_class):
            return self.coerce_map_from_c(S._type)
        if self._coerce_from_hash is None: # this is because parent.__init__() does not always get called
            self.init_coerce()
        cdef object ret
        try:
            return self._coerce_from_hash[S]
        except KeyError:
            pass

        if S == self:
            # non-unique parents
            if unique_parent_warnings:
                print "Warning: non-unique parents %s"%(type(S))
            return self._generic_convert_map(S)

        try:
            _register_pair(self, S)
            mor = self.discover_coerce_map_from(S)
            #if mor is not None:
            #    # Need to check that this morphism doesn't connect previously unconnected parts of the coercion diagram
            #    if self._embedding is not None and not self._embedding.codomain().has_coerce_map_from(S):
            #        # The following if statement may call this function with self and S.  If so, we want to return None,
            #        # so that it doesn't use this path for the existence of a coercion path.
            #        # We disable this for now because it is too strict
            #        pass
            #        # print "embed problem: the following morphisms connect unconnected portions of the coercion graph\n%s\n%s"%(self._embedding, mor)
            #        # mor = None
            if mor is not None:
                # NOTE: this line is what makes the coercion detection stateful
                self._coerce_from_list.append(mor)
            self._coerce_from_hash[S] = mor
            _unregister_pair(self, S)
            return mor
        except NotImplementedError:
            _record_exception()
            return None

    cdef discover_coerce_map_from(self, S):
        """
        Precedence for discovering a coercion S -> self goes as follows:

            1. If S has an embedding into T, look for T -> self and return composition
            2. If self._coerce_map_from_(S) is NOT exactly one of
                    - DefaultConvertMorphism
                    - DefaultConvertMorphism_unique
                    - NamedConvertMorphism
                return this morphism
            3. Traverse the coercion lists looking for the "best" morphism
               (including the one found at 2).
        """
        best_mor = None
        if PY_TYPE_CHECK(S, Parent) and (<Parent>S)._embedding is not None:
            if (<Parent>S)._embedding.codomain() is self:
                return (<Parent>S)._embedding
            connecting = self._coerce_map_from_((<Parent>S)._embedding.codomain())
            if connecting is not None:
                return (<Parent>S)._embedding.post_compose(connecting)

        cdef morphism.Morphism mor = self._coerce_map_from_(S)
        if mor is not None:
            from sage.categories.morphism import Morphism
            from coerce_maps import DefaultConvertMorphism, DefaultConvertMorphism_unique, NamedConvertMorphism
            if not PY_TYPE_CHECK(mor, Morphism):
                raise TypeError, "_coerce_map_from_ must return None or an explicit Morphism"
            elif (PY_TYPE_CHECK_EXACT(mor, DefaultConvertMorphism) or
                  PY_TYPE_CHECK_EXACT(mor, DefaultConvertMorphism_unique) or
                  PY_TYPE_CHECK_EXACT(mor, NamedConvertMorphism)) and not mor._force_use:
                # If there is something better in the list, try to return that instead
                # This is so, for example, has_coerce_map_from can return True but still
                # take advantage of the _populate_coercion_lists_ data.
                best_mor = mor
            else:
                return mor
        import sage.categories.morphism
        from sage.categories.morphism import Morphism
        from sage.categories.homset import Hom

        cdef int num_paths = 1 # this is the number of paths we find before settling on the best (the one with lowest coerce_cost).
                               # setting this to 1 will make it return the first path found.
        cdef int mor_found = 0
        cdef Parent R
        # Recurse.  Note that if S is the domain of one of the morphisms in self._coerce_from_list,
        # we will have stuck the morphism into _coerce_map_hash and thus returned it already.
        for mor in self._coerce_from_list:
            if mor._domain is S:
                if best_mor is None or mor._coerce_cost < best_mor._coerce_cost:
                    best_mor = mor
                mor_found += 1
                if mor_found  >= num_paths:
                    return best_mor
            connecting = mor._domain.coerce_map_from(S)
            if connecting is not None:
                mor = mor * connecting
                if best_mor is None or mor._coerce_cost < best_mor._coerce_cost:
                    best_mor = mor
                mor_found += 1
                if mor_found  >= num_paths:
                    return best_mor

        return best_mor


    cpdef _coerce_map_from_(self, S):
        if self.has_coerce_map_from(S):
            return self._generic_convert_map(S)
        return None

    cpdef convert_map_from(self, S):
        try:
            return self._convert_from_hash[S]
        except KeyError:
            mor = self.discover_convert_map_from(S)
            self._convert_from_list.append(mor)
            self._convert_from_hash[S] = mor
            return mor

    cdef discover_convert_map_from(self, S):
        cdef morphism.Morphism mor = self.coerce_map_from(S)
        if mor is not None:
            return mor

        try:
            if PY_TYPE_CHECK(S, Parent):
                mor = S.coerce_map_from(self)
                if mor is not None:
                    mor = mor.section()
                    if mor is not None:
                        return mor
        except NotImplementedError:
            pass

        mor = self._convert_map_from_(S)
        if mor is not None:
            return mor

        if not PY_TYPE_CHECK(S, type) and not PY_TYPE_CHECK(S, Parent):
            # Sequences is used as a category and a "Parent"
            from sage.categories.category_types import Sequences
            from sage.structure.coerce_maps import ListMorphism
            if isinstance(S, Sequences):
                return ListMorphism(S, self.convert_map_from(list))

        mor = self._generic_convert_map(S)
        return mor

    cpdef _convert_map_from_(self, S):
        return None

    cpdef get_action(self, S, op=operator.mul, bint self_on_left=True):
        """
        TESTS:
            sage: M = QQ['y']^3
            sage: M.get_action(ZZ['x']['y'])
            Right scalar multiplication by Univariate Polynomial Ring in y over Univariate Polynomial Ring in x over Integer Ring on Ambient free module of rank 3 over the principal ideal domain Univariate Polynomial Ring in y over Rational Field
            sage: M.get_action(ZZ['x']) # should be None
        """
        try:
            if self._action_hash is None: # this is because parent.__init__() does not always get called
                self.init_coerce()
            return self._action_hash[S, op, self_on_left]
        except KeyError:
            pass

        action = self._get_action_(S, op, self_on_left)
        if action is None:
            action = self.discover_action(S, op, self_on_left)

        if action is not None:
            from sage.categories.action import Action
            if not isinstance(action, Action):
                raise TypeError, "get_action_impl must return None or an Action"
            # We do NOT add to the list, as this would lead to errors as in
            # the example above.

        self._action_hash[S, op, self_on_left] = action
        return action


    cdef discover_action(self, S, op, bint self_on_left):
        # G acts on S, G -> G', R -> S => G' acts on R (?)
        # NO! ZZ[x,y] acts on Matrices(ZZ[x]) but ZZ[y] does not.
        # What may be true is that if the action's desination is S, then this can be allowed.
        import sage.categories.morphism
        from sage.categories.action import Action, PrecomposedAction
        from sage.categories.morphism import Morphism
        from sage.categories.homset import Hom
        from coerce_actions import LeftModuleAction, RightModuleAction
        cdef Parent R
        for action in self._action_list:
            if PY_TYPE_CHECK(action, Action) and action.operation() is op:
                if self_on_left:
                    if action.left_domain() is not self: continue
                    R = action.right_domain()
                else:
                    if action.right_domain() is not self: continue
                    R = action.left_domain()
            elif op is operator.mul:
                try:
                    R = action
                    _register_pair(x,y) # to kill circular recursion
                    if self_on_left:
                        action = LeftModuleAction(R, self) # self is acted on from right
                    else:
                        action = RightModuleAction(R, self) # self is acted on from left
                    _unregister_pair(x,y)
                    ## The following two lines are diabled to prevent the following from working:
                    ## sage: x, y = var('x,y')
                    ## sage: parent(ZZ[x][y](1)*vector(QQ[y],[1,2]))
                    ## sage: parent(ZZ[x](1)*vector(QQ[y],[1,2]))
                    ## We will hopefully come up with a way to reinsert them, because they increase the scope
                    ## of discovered actions.
                    #i = self._action_list.index(R)
                    #self._action_list[i] = action
                except TypeError:
                    _record_exception()
                    _unregister_pair(x,y)
                    continue
            else:
                continue # only try mul if not specified
            if R is S:
                return action
            else:
                connecting = R.coerce_map_from(S) # S -> R
                if connecting is not None:
                    if self_on_left:
                        return PrecomposedAction(action, None, connecting)
                    else:
                        return PrecomposedAction(action, connecting, None)

        if op is operator.mul and PY_TYPE_CHECK(S, Parent):
            from coerce_actions import LeftModuleAction, RightModuleAction, LAction, RAction
            # Actors define _l_action_ and _r_action_
            # Acted-on elements define _lmul_ and _rmul_

            # TODO: if _xmul_/_x_action_ code does stuff like
            # if self == 0:
            #    return self
            # then an_element() == 0 could be very bad.
            #

            x = self.an_element()
            y = (<Parent>S).an_element()
            #print "looking for action ", self, "<--->", S
            #print "looking for action ", x, "<--->", y

            _register_pair(x,y) # this is to avoid possible infinite loops
            if self_on_left:
                try:
                    #print "RightModuleAction", S, self
                    action = RightModuleAction(S, self) # this will test _lmul_
                    _unregister_pair(x,y)
                    #print "got", action
                    return action
                except (NotImplementedError, TypeError, AttributeError, ValueError), ex:
                    _record_exception()

                try:
                    #print "LAction"
                    z = x._l_action_(y)
                    _unregister_pair(x,y)
                    #print "got", z
                    return LAction(self, S)
                except (NotImplementedError, TypeError, AttributeError, ValueError):
                    _record_exception()

            else:
                try:
                    #print "LeftModuleAction"
                    action = LeftModuleAction(S, self) # this will test _rmul_
                    _unregister_pair(x,y)
                    #print "got", action
                    return action
                except (NotImplementedError, TypeError, AttributeError, ValueError), ex:
                    _record_exception()

                try:
                    #print "RAction"
                    z = x._r_action_(y)
                    _unregister_pair(x,y)
                    #print "got", z
                    return RAction(self, S)
                except (NotImplementedError, TypeError, AttributeError, ValueError):
                    _record_exception()


            try:
                # maybe there is a more clever way of detecting ZZ than importing here...
                from sage.rings.integer_ring import ZZ
                from sage.rings.ring import Ring
                if S is ZZ and not PY_TYPE_CHECK(self, Ring) and not self.has_coerce_map_from(ZZ):
                    #print "IntegerMulAction"
                    from sage.structure.coerce_actions import IntegerMulAction
                    action = IntegerMulAction(S, self, not self_on_left)
                    #print "got", action
                    _unregister_pair(x,y)
                    return action
            except (NotImplementedError, TypeError, AttributeError, ValueError):
                _record_exception()

            _unregister_pair(x,y)

            #print "found nothing"


    cpdef _get_action_(self, S, op, bint self_on_left):
        return None

    def construction(self):
        """
        Returns a pair (functor, parent) such that functor(parent) return self.
        If this ring does not have a functorial construction, return None.
        """
        return None

    cpdef an_element(self):
        if self.__an_element is None:
            self.__an_element = self._an_element_impl()
        return self.__an_element

    cpdef _an_element_impl(self):
        """
        COERCE TODO
        Here so that I didn't have to change parent.pxd.  Should be eliminated and _an_element_ made cpdef.  Also need to change:
        sage/rings/real_rqdf.pyx
        sage/libs/pari/gen.pyx
        """
        return self._an_element_()

    cpdef _an_element_(self):
        """
        Returns an element of self. Want it in sufficent generality
        that poorly-written functions won't work when they're not
        supposed to. This is cached so doesn't have to be super fast.
        """
        try:
            return self.gen(0)
        except:
            _record_exception()
            pass

        try:
            return self.gen()
        except:
            _record_exception()
            pass

        from sage.rings.infinity import infinity
        for x in ['_an_element_', 'pi', 1.2, 2, 1, 0, infinity]:
            # This weird looking list is to try to get an element
            # which doesn't coerce other places.
            try:
                return self(x)
            except (TypeError, NameError, NotImplementedError, AttributeError, ValueError):
                _record_exception()
                pass

        raise NotImplementedError, "please implement _an_element_ for %s" % self

    def is_exact(self):
        """
        Return True if elements of this ring are represented exactly, i.e.,
        there is no precision loss when doing arithmetic.

        NOTE: This defaults to true, so even if it does return True you have
        no guarantee (unless the ring has properly overloaded this).

        EXAMPLES:
            sage: QQ.is_exact()
            True
            sage: ZZ.is_exact()
            True
            sage: Qp(7).is_exact()
            False
            sage: Zp(7, type='capped-abs').is_exact()
            False
        """
        return True

#    cpdef base_extend(self, other, category=None):
#        """
#        EXAMPLES:
#            sage: QQ.base_extend(GF(7))
#            Traceback (most recent call last):
#            ...
#            TypeError: base extension not defined for Rational Field
#            sage: ZZ.base_extend(GF(7))
#            Finite Field of size 7
#        """
#        # Use the coerce map if a base extend is not defined in the category.
#        # this is the default implementation.
#        try:
#            if category is None:
#                method = self._categories[0].get_object_method("base_extend") # , self._categories[1:])
#            else:
#                method = category.get_object_method("base_extend")
#            if method is not None:
#                return method(self)
#            elif other.has_coerce_map_from(self):
#                return other
#            else:
#                raise TypeError, "base extension not defined for %s" % self
#        except AttributeError:
#            raise TypeError, "base extension not defined for %s" % self

############################################################################
# Set baseclass --
############################################################################


cdef class Set_generic(Parent): # Cannot use Parent because Element._parent is Parent
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

    def __nonzero__(self):
        return len(self) != 0



import types
cdef _type_set_cache = {}

def Set_PythonType(theType):
    """
    Return the (unique) Parent that represents the set of Python objects
    of a specified type.

    EXAMPLES:
        sage: from sage.structure.parent import Set_PythonType
        sage: Set_PythonType(list)
        Set of Python objects of type 'list'
        sage: Set_PythonType(list) is Set_PythonType(list)
        True
        sage: S = Set_PythonType(tuple)
        sage: S([1,2,3])
        (1, 2, 3)
    """
    try:
        return _type_set_cache[theType]
    except KeyError:
        _type_set_cache[theType] = theSet = Set_PythonType_class(theType)
        return theSet

cdef class Set_PythonType_class(Set_generic):

    cdef _type

    def __init__(self, theType):
        from sage.categories.category_types import Sets
        Set_generic.__init__(self, element_constructor=theType, categories=[Sets()])
        self._type = theType

    def __call__(self, x):
        return self._type(x)

    def __hash__(self):
        return -hash(self._type)

    cpdef int _cmp_(self, other) except -100:
        if self is other:
            return 0
        if isinstance(other, Set_PythonType_class):
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

# These functions are to guarantee that user defined _lmul_, _rmul_,
# _l_action_, _r_action_ do not in turn call __mul__ on their
# arguments, leading to an infinite loop.

cdef object _coerce_test_list = []

class EltPair:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return type(self.x) is type(other.x) and self.x is other.x and type(self.y) is type(other.y) and self.y is other.y
    def __repr__(self):
        return "%r (%r), %r (%r)" % (self.x, type(self.x), self.y, type(self.y))

cdef bint _register_pair(x, y) except -1:
    both = EltPair(x,y)
#    print _coerce_test_list, " + ", both
    if both in _coerce_test_list:
#        print "Uh oh..."
#        print _coerce_test_list
#        print both
        xp = type(x) if PY_TYPE_CHECK(x, Parent) else parent_c(x)
        yp = type(y) if PY_TYPE_CHECK(y, Parent) else parent_c(y)
        #print xp, yp
        raise NotImplementedError, "Infinite loop in action of %s (parent %s) and %s (parent %s)!" % (x, xp, y, yp)
    _coerce_test_list.append(both)
    return 0

cdef bint _unregister_pair(x, y) except -1:
    try:
        _coerce_test_list.remove(EltPair(x,y))
    except (ValueError, NotImplementedError):
        pass


def coerce_graph(parents=None):
    from sage.graphs.graph import DiGraph
    G = DiGraph()
    if parents is None:
        parents = all_parents #.keys()
    G.add_vertices(parents)
    cdef Parent P
    for P in parents:
        for S, mor in P._coerce_from_hash.iteritems():
            if S in parents:
                G.add_edge(P, S, mor)
    return G



empty_set = Set_generic()

def normalize_names(ngens, names):
    return empty_set.normalize_names(ngens, names)
