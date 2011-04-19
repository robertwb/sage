r"""
Base class for objects of a category

CLASS HIERARCHY:

- :class:`~sage.structure.sage_object.SageObject`

  - **CategoryObject**

    - :class:`~sage.structure.parent.Parent`

Many category objects in Sage are equipped with generators, which are
usually special elements of the object.  For example, the polynomial ring
`\ZZ[x,y,z]` is generated by `x`, `y`, and `z`.  In Sage the ``i`` th
generator of an object ``X`` is obtained using the notation
``X.gen(i)``.  From the Sage interactive prompt, the shorthand
notation ``X.i`` is also allowed.

The following examples illustrate these functions in the context of
multivariate polynomial rings and free modules.

EXAMPLES::

    sage: R = PolynomialRing(ZZ, 3, 'x')
    sage: R.ngens()
    3
    sage: R.gen(0)
    x0
    sage: R.gens()
    (x0, x1, x2)
    sage: R.variable_names()
    ('x0', 'x1', 'x2')

This example illustrates generators for a free module over `\ZZ`.

::

    sage: M = FreeModule(ZZ, 4)
    sage: M
    Ambient free module of rank 4 over the principal ideal domain Integer Ring
    sage: M.ngens()
    4
    sage: M.gen(0)
    (1, 0, 0, 0)
    sage: M.gens()
    ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
"""

cdef int bad_parent_warnings = 0

import generators
import sage_object
from sage.categories.category import Category, JoinCategory

def guess_category(obj):
    # this should be obsolete if things declare their categories
    try:
        if obj.is_field():
            from sage.categories.all import Fields
            return Fields()
    except:
        pass
    try:
        if obj.is_ring():
            from sage.categories.all import CommutativeAlgebras, Algebras, CommutativeRings, Rings
            if obj.is_commutative():
                if obj._base is not obj:
                    return CommutativeAlgebras(obj._base)
                else:
                    return CommutativeRings()
            else:
                if obj._base is not obj:
                    return Algebras(obj._base)
                else:
                    return Rings()
    except:
        pass
    from sage.structure.parent import Parent
    #if isinstance(obj, Parent):
    #    import sys
    #    sys.stderr.write("bla: %s"%obj)
    #    from sage.categories.all import Sets
    #    return Sets()
    return None # don't want to risk importing stuff...

def check_default_category(default_category, category):
    if category is None:
        return default_category
    else:
        #assert category.is_subcategory(default_category), "%s is not a subcategory of %s"%(category, default_category)
        #return category
        return default_category.join([default_category,category])

cdef class CategoryObject(sage_object.SageObject):
    """
    An object in some category.
    """
    def __init__(self, category = None, base = None):
        """
        Initializes an object in a category

        INPUT:

        - ``category`` - The category this object belongs to. If this object
          belongs to multiple categories, those can be passed as a tuple
        - ``base`` - If this object has another object that should be
          considered a base in its primary category, you can include that base
          here.

        EXAMPLES::

            sage: from sage.structure.category_object import CategoryObject
            sage: A = CategoryObject()
            sage: A.category()
            Category of objects
            sage: A.base()

            sage: A = CategoryObject(category = Rings(), base = QQ)
            sage: A.category()
            Category of rings
            sage: A.base()
            Rational Field

            sage: A = CategoryObject(category = (Semigroups(), CommutativeAdditiveSemigroups()))
            sage: A.category()
            Join of Category of semigroups and Category of commutative additive semigroups

        FIXME: the base and generators attributes have nothing to do with categories, do they?
        """
        if base is not None:
            self._base = base
        self._generators = {}
        if category is not None:
            self._init_category_(category)

    def _init_category_(self, category):
        """
        Sets the category or categories of this object.

        EXAMPLES::

            sage: A = sage.structure.category_object.CategoryObject()
            sage: A._init_category_(Rings())
            sage: A.category()
            Category of rings
            sage: A._init_category_((Semigroups(), CommutativeAdditiveSemigroups()))
            sage: A.category()
            Join of Category of semigroups and Category of commutative additive semigroups
        """
        if category is None:
            if bad_parent_warnings:
                print "No category for %s" % type(self)
            category = guess_category(self) # so generators don't crash
        elif (type(category) == tuple or type(category) == list):
            assert(len(category)>0) # or we should decide of the semantic for an empty category
            if len(category) == 1:
                category = category[0]
            else:
                category = JoinCategory(category)
        self._category = category

    def _is_category_initialized(self):
        return self._category is not None

    def category(self):
        if self._category is None:
            # COERCE TODO: we shouldn't need this
            from sage.categories.objects import Objects
            self._category = Objects()
        return self._category

    def categories(self):
        """
        EXAMPLES::

            sage: ZZ.categories()
            [Category of euclidean domains,
             Category of principal ideal domains,
             Category of unique factorization domains,
             Category of gcd domains,
             Category of integral domains,
             Category of commutative rings,
             Category of domains,
             Category of rings,
             Category of rngs,
             Category of commutative additive groups,
             Category of semirings,
             Category of commutative additive monoids,
             Category of commutative additive semigroups,
             Category of additive magmas,
             Category of monoids,
             Category of semigroups,
             Category of magmas,
             Category of sets,
             Category of sets with partial maps,
             Category of objects]
        """
        return self.category().all_super_categories()

    ##############################################################################
    # Generators
    ##############################################################################

    def _populate_generators_(self, gens=None, names=None, normalize = True, category=None):
        if self._generators.has_key(category):
            raise ValueError, "Generators cannot be changed after object creation."
        if category is None:
            category = self._category
        from sage.structure.sequence import Sequence
        if gens is None:
            n = self._ngens_()
            from sage.rings.infinity import infinity
            if n is infinity:
                gens = generators.Generators_naturals(self, category)
            else:
                gens = generators.Generators_finite(self, self._ngens_(), None, category)
        elif isinstance(gens, Generators):
            pass
        elif isinstance(gens, (list, tuple, Sequence)):
            if names is None:
                names = tuple([str(x) for x in gens])
            gens = generators.Generators_list(self, list(gens), category)
        else:
            gens = generators.Generators_list(self, [gens], category)
        self._generators[category] = gens
        if category == self._category:
            if names is not None and self._names is None:
                self._assign_names(names, ngens=gens.count(), normalize=normalize)
            self._generators[category] = gens

#    cpdef Generators gens(self, category=None):
#        if category is None:
#            category = self._categories[0]
#        try:
#            return self._generators[category]
#        except KeyError:
#            if category == self._categories[0]:
#                n = self._ngens_()
#                from sage.rings.infinity import infinity
#                if n is infinity:
#                    gens = generators.Generators_naturals(self, category)
#                else:
#                    gens = generators.Generators_finite(self, self._ngens_(), None, category)
#            else:
#                gens = self._compute_generators_(category)
#            self._generators[category] = gens
#            return gens
#
#    cpdef gen(self, index=0, category=None):
#        return self.gens(category)[index]
#
#    cpdef ngens(self, category=None):
#        return self.gens(category).count()

    def _ngens_(self):
        return 0

    def gens_dict(self):
         r"""
         Return a dictionary whose entries are ``{var_name:variable,...}``.
         """
         if HAS_DICTIONARY(self):
            try:
                if self._gens_dict is not None:
                    return self._gens_dict
            except AttributeError:
                pass
         v = {}
         for x in self.gens():
             v[str(x)] = x
         if HAS_DICTIONARY(self):
            self._gens_dict = v
         return v

    def objgens(self):
        """
        Return the tuple ``(self, self.gens())``.

        EXAMPLES::

            sage: R = PolynomialRing(QQ, 3, 'x'); R
            Multivariate Polynomial Ring in x0, x1, x2 over Rational Field
            sage: R.objgens()
            (Multivariate Polynomial Ring in x0, x1, x2 over Rational Field, (x0, x1, x2))
        """
        return self, self.gens()

    def objgen(self):
        """
        Return the tuple ``(self, self.gen())``.

        EXAMPLES::

            sage: R, x = PolynomialRing(QQ,'x').objgen()
            sage: R
            Univariate Polynomial Ring in x over Rational Field
            sage: x
            x
        """
        return self, self.gen()

    def _first_ngens(self, n):
        """
        Used by the preparser for R.<x> = ...
        """
        return self.gens()[:n]

    #################################################################################################
    # Names and Printers
    #################################################################################################

    def _assign_names(self, names=None, normalize=True, ngens=None):
        """
        Set the names of the generator of this object.

        This can only be done once because objects with generators
        are immutable, and is typically done during creation of the object.


        EXAMPLES:
        When we create this polynomial ring, self._assign_names is called by the constructor::

            sage: R = QQ['x,y,abc']; R
            Multivariate Polynomial Ring in x, y, abc over Rational Field
            sage: R.2
            abc

        We can't rename the variables::

            sage: R._assign_names(['a','b','c'])
            Traceback (most recent call last):
            ...
            ValueError: variable names cannot be changed after object creation.
        """
        # this will eventually all be handled by the printer
        if names is None: return
        if normalize:
            if ngens is None:
                if self._generators is None or len(self._generators) == 0:
                    # not defined yet
                    if isinstance(names, (tuple, list)) and names is not None:
                        ngens = len(names)
                    else:
                        ngens = 1
                else:
                    ngens = self.ngens()
            names = self.normalize_names(ngens, names)
        if self._names is not None and names != self._names:
            raise ValueError, 'variable names cannot be changed after object creation.'
        if PY_TYPE_CHECK(names, str):
            names = (names, )  # make it a tuple
        elif PY_TYPE_CHECK(names, list):
            names = tuple(names)
        elif not PY_TYPE_CHECK(names, tuple):
            raise TypeError, "names must be a tuple of strings"
        self._names = names

    def normalize_names(self, int ngens, names=None):
        if names is None:
            return None
        if ngens == 0:
            return ()
        if isinstance(names, str) and names.find(',') != -1:
            names = names.split(',')
        if isinstance(names, str) and ngens > 1 and len(names) == ngens:
            names = tuple(names)
        if isinstance(names, str):
            name = names
            import sage.misc.defaults
            names = sage.misc.defaults.variable_names(ngens, name)
            names = self._certify_names(names)
        else:
            names = self._certify_names(names)
            if not isinstance(names, (list, tuple)):
                raise TypeError, "names must be a list or tuple of strings"
            for x in names:
                if not isinstance(x,str):
                    raise TypeError, "names must consist of strings"
            if len(names) != ngens:
                raise IndexError, "the number of names must equal the number of generators"
        return names

    def _certify_names(self, names):
        v = []
        try:
            names = tuple(names)
        except TypeError:
            names = [str(names)]
        for N in names:
            if not isinstance(N, str):
                N = str(N)
            N = N.strip().strip("'")
            if len(N) == 0:
                raise ValueError, "variable name must be nonempty"
            if not N.isalnum() and not N.replace("_","").isalnum():
                # We must be alphanumeric, but we make an exception for non-leading '_' characters.
                raise ValueError, "variable names must be alphanumeric, but one is '%s' which is not."%N
            if not N[0].isalpha():
                raise ValueError, "first letter of variable name must be a letter: %s" % N
            v.append(N)
        return tuple(v)

    def variable_names(self):
        if self._names != None:
            return self._names
        raise ValueError, "variable names have not yet been set using self._assign_names(...)"

    def variable_name(self):
        return self.variable_names()[0]

    def __temporarily_change_names(self, names, latex_names):
        """
        This is used by the variable names context manager.
        """
        #old = self._names, self._latex_names
        # We can not assume that self *has* _latex_variable_names.
        # But there is a method that returns them and sets
        # the attribute at the same time, if needed.
        old = self.variable_names(), self.latex_variable_names()
        self._names, self._latex_names = names, latex_names
        return old

    def inject_variables(self, scope=None, verbose=True):
        """
        Inject the generators of self with their names into the
        namespace of the Python code from which this function is
        called.  Thus, e.g., if the generators of self are labeled
        'a', 'b', and 'c', then after calling this method the
        variables a, b, and c in the current scope will be set
        equal to the generators of self.

        NOTE: If Foo is a constructor for a Sage object with generators, and
        Foo is defined in Cython, then it would typically call
        ``inject_variables()`` on the object it creates.  E.g.,
        ``PolynomialRing(QQ, 'y')`` does this so that the variable y is the
        generator of the polynomial ring.
        """
        vs = self.variable_names()
        gs = self.gens()
        if scope is None:
           scope = globals()
        if verbose:
           print "Defining %s"%(', '.join(vs))
        for v, g in zip(vs, gs):
           scope[v] = g

    def injvar(self, scope=None, verbose=True):
        """
        This is a deprecated synonym for :meth:`.inject_variables`.
        """
        from sage.misc.misc import deprecation
        deprecation('injvar is deprecated; use inject_variables instead.')
        return self.inject_variables(scope=scope, verbose=verbose)

    #################################################################################################
    # Bases
    #################################################################################################

#    cpdef base(self, category=None):
#        if category is None:
#            return self._base
#        else:
#            return category._obj_base(self)

    def has_base(self, category=None):
        if category is None:
            return self._base is not None
        else:
            return category._obj_base(self) is not None

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
#        try:
#            if category is None:
#                method = self._category.get_object_method("base_extend") # , self._categories[1:])
#            else:
#                method = category.get_object_method("base_extend")
#            return method(self)
#        except AttributeError:
#            raise TypeError, "base extension not defined for %s" % self

    # COERCE TODO: When everything has a category, move let it be an optional arg.
    def base_ring(self): # This should be in a category or elsewhere, but not here
        return self._base

    def base(self):
        return self._base

    #################################################################################################
    # Automatic lookup of methods on the category.
    #################################################################################################

#    def __getattr__(self, name):
#        """
#        Overriding the __getattr__ method allows one to define methods for objects in a particular
#        category by writing a corresponding method on the category.
#
#        In order to write a method called FOO that's automatically attached to a category object,
#        write a method object_FOO on one of that object's categories.
#
#        EXAMPLES:
#        sage: G = DirichletGroup(18); G
#        Group of Dirichlet characters of modulus 18 over Cyclotomic Field of order 6 and degree 2
#        sage: G.generator_orders()
#        [1, 6]
#        sage: G.category().object_generator_orders(G)
#        [1, 6]
#        """
#        if self._category is not None:
#            attr = self._category.get_object_method(name)
#            if attr is not None:
#                if callable(attr):
#                    return FillFirstArg(attr, self)
#                else:
#                    return attr
#        return object.__getattribute__(self, name)

    ############################################################################
    # Homomorphism --
    ############################################################################
    def Hom(self, codomain, cat=None):
        r"""
        Return the homspace ``Hom(self, codomain, cat)`` of all
        homomorphisms from self to codomain in the category cat.  The
        default category is determined by ``self.category()`` and
        ``codomain.category()``.

        EXAMPLES::

            sage: R.<x,y> = PolynomialRing(QQ, 2)
            sage: R.Hom(QQ)
            Set of Homomorphisms from Multivariate Polynomial Ring in x, y over Rational Field to Rational Field

        Homspaces are defined for very general Sage objects, even elements of familiar rings.

        ::

            sage: n = 5; Hom(n,7)
            Set of Morphisms from 5 to 7 in Category of elements of Integer Ring
            sage: z=(2/3); Hom(z,8/1)
            Set of Morphisms from 2/3 to 8 in Category of elements of Rational Field

        This example illustrates the optional third argument::

            sage: QQ.Hom(ZZ, Sets())
            Set of Morphisms from Rational Field to Integer Ring in Category of sets
        """
        try:
            return self._Hom_(codomain, cat)
        except (AttributeError, TypeError):
            pass
        from sage.categories.all import Hom
        return Hom(self, codomain, cat)

    def latex_variable_names(self):
        """
        Returns the list of variable names suitable for latex output.

        All ``_SOMETHING`` substrings are replaced by ``_{SOMETHING}``
        recursively so that subscripts of subscripts work.

        EXAMPLES::

         sage: R, x = PolynomialRing(QQ,'x',12).objgens()
         sage: x
         (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11)
         sage: print R.latex_variable_names ()
         ['x_{0}', 'x_{1}', 'x_{2}', 'x_{3}', 'x_{4}', 'x_{5}', 'x_{6}', 'x_{7}', 'x_{8}', 'x_{9}', 'x_{10}', 'x_{11}']
         sage: f = x[0]^3 + 15/3 * x[1]^10
         sage: print latex(f)
         5 x_{1}^{10} + x_{0}^{3}
        """
        from sage.misc.latex import latex, latex_variable_name
        try:
            names = self._latex_names
            if names is not None:
                return names
        except AttributeError:
            pass
        # Compute the latex versions of the variable names.
        self._latex_names = [latex_variable_name(x) for x in self.variable_names()]
        return self._latex_names

    def latex_name(self):
        return self.latex_variable_names()[0]

    def _temporarily_change_names(self, names):
        self._names = names

    #################################################################################
    # Give all objects with generators a dictionary, so that attribute setting
    # works.   It would be nice if this functionality were standard in Cython,
    # i.e., just define __dict__ as an attribute and all this code gets generated.
    #################################################################################
    def __getstate__(self):
        d = []
        try:
            d = list(self.__dict__.copy().iteritems()) # so we can add elements
        except AttributeError:
            pass
        d = dict(d)
        d['_generators'] = self._generators
        d['_category'] = self._category
        d['_base'] = self._base
        d['_cdata'] = self._cdata
        d['_names'] = self._names
        ###########
        # The _pickle_version ensures that the unpickling for objects created
        # in different versions of sage works across versions.
        # Update this integer if you change any of these attributes
        ###########
        d['_pickle_version'] = 1
        try:
            d['_generator_orders'] = self._generator_orders
        except AttributeError:
            pass

        return d

    def __setstate__(self,d):
        try:
            version = d['_pickle_version']
        except KeyError:
            version = 0
        try:
            if version == 1:
                self._generators = d['_generators']
                if d['_category'] is not None:
                    # We must not erase the category information of
                    # self.  Otherwise, pickles break (e.g., QQ should
                    # be a commutative ring, but when QQ._category is
                    # None then it only knows that it is a ring!
                    if self._category is None:
                        self._category = d['_category']
                    else:
                        self._category = self._category.join([self._category,d['_category']])
                self._base = d['_base']
                self._cdata = d['_cdata']
                self._names = d['_names']
                try:
                    self._generator_orders = d['_generator_orders']
                except (AttributeError, KeyError):
                    pass
            elif version == 0:
                # In the old code, this functionality was in parent_gens,
                # but there were parents that didn't inherit from parent_gens.
                # If we have such, then we only need to deal with the dictionary.
                try:
                    self._base = d['_base']
                    self._names = d['_names']
                    from sage.categories.all import Objects
                    if d['_gens'] is None:
                        from sage.structure.generators import Generators
                        self._generators = Generators(self, None, Objects())
                    else:
                        from sage.structure.generators import Generator_list
                        self._generators = Generator_list(self, d['_gens'], Objects())
                    self._generator_orders = d['_generator_orders'] # this may raise a KeyError, but that's okay.
                    # We throw away d['_latex_names'] and d['_list'] and d['_gens_dict']
                except (AttributeError, KeyError):
                    pass
            try:
                self.__dict__ = d
            except AttributeError:
                pass
        except (AttributeError, KeyError):
            raise
            #raise RuntimeError, "If you change the pickling code in parent or category_object, you need to update the _pickle_version field"


#     #################################################################################
#     # Morphisms of objects with generators
#     #################################################################################


## COERCE TODO: see categories.MultiplicativeAbelianGroups

# cdef class ParentWithMultiplicativeAbelianGens(Parent):
#     def generator_orders(self):
#         if self._generator_orders != None:
#             return self._generator_orders
#         else:
#             g = []
#             for x in self.gens():
#                 g.append(x.multiplicative_order())
#             self._generator_orders = g
#             return g

#     def __iter__(self):
#         """
#         Return an iterator over the elements in this object.
#         """
#         return gens_py.multiplicative_iterator(self)



# cdef class ParentWithAdditiveAbelianGens(Parent):
#     def generator_orders(self):
#         if self._generator_orders != None:
#             return self._generator_orders
#         else:
#             g = []
#             for x in self.gens():
#                 g.append(x.additive_order())
#             self._generator_orders = g
#             return g

#     def __iter__(self):
#         """
#         Return an iterator over the elements in this object.
#         """
#         return gens_py.abelian_iterator(self)




class localvars:
    r"""
    Context manager for safely temporarily changing the variables
    names of an object with generators.

    Objects with named generators are globally unique in Sage.
    Sometimes, though, it is very useful to be able to temporarily
    display the generators differently.   The new Python ``with``
    statement and the localvars context manager make this easy and
    safe (and fun!)

    Suppose X is any object with generators.  Write

    ::

        with localvars(X, names[, latex_names] [,normalize=False]):
            some code
            ...

    and the indented code will be run as if the names in ``X`` are changed to
    the new names. If you give ``normalize=True``, then the names are assumed
    to be a tuple of the correct number of strings.

    If you're writing Python library code, you currently have to put ``from
    __future__ import with_statement`` in your file in order to use the
    ``with`` statement. This restriction will disappear in Python 2.6.

    EXAMPLES::

       sage: R.<x,y> = PolynomialRing(QQ,2)
       sage: with localvars(R, 'z,w'):
       ...       print x^3 + y^3 - x*y
       ...
       z^3 + w^3 - z*w

    NOTES: I wrote this because it was needed to print elements of the quotient
    of a ring `R` by an ideal `I` using the print function for elements of `R`.
    See the code in :mod:`sage.rings.quotient_ring_element`.

    AUTHOR: William Stein (2006-10-31)
    """
    # fix this so that it handles latex names with the printer framework.
    def __init__(self, obj, names, latex_names=None, normalize=True):
        self._obj = obj
        if normalize:
            self._names = obj.normalize_names(obj.ngens(), names)
        else:
            self._names = names

    def __enter__(self):
        self._orig_names = (<CategoryObject?>self._obj)._names
        self._obj._temporarily_change_names(self._names)

    def __exit__(self, type, value, traceback):
        self._obj._temporarily_change_names(self._orig_names)


# This Cython class confuses the hell out of the Sphinx documentation parser
# (because __doc__ is defined but not set). And the only code that refers to it
# is commented out. So I'm commenting it out too. -- David Loeffler 2009-07-06
#cdef class FillFirstArg:
#    cdef object arg, f
#    cdef public __doc__
#    def __init__(self, f, arg):
#        self.arg = arg
#        self.f = f
#        self.__doc__ = f.__doc__
#    def __call__(self, *args, **kwds):
#        return self.f(self.arg, *args, **kwds)
