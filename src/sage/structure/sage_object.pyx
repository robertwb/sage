r"""
Abstract base class for Sage objects
"""

import cPickle
import os
import sys
from cStringIO import StringIO
from sage.misc.sage_unittest import TestSuite

sys_modules = sys.modules

# change to import zlib to use zlib instead; but this
# slows down loading any data stored in the other format
import zlib; comp = zlib
import bz2; comp_other = bz2

base=None

cdef process(s):
    if not base is None and (len(s) == 0 or s[0] != '/'):
        s = base + '/' + s
    if s[-5:] != '.sobj':
        return s + '.sobj'
    else:
        return s


cdef class SageObject:

    #######################################################################
    # Textual representation code
    #######################################################################

    def rename(self, x=None):
        r"""
        Change self so it prints as x, where x is a string.

        .. note::

           This is *only* supported for Python classes that derive
           from SageObject.

        EXAMPLES::

            sage: x = PolynomialRing(QQ, 'x', sparse=True).gen()
            sage: g = x^3 + x - 5
            sage: g
            x^3 + x - 5
            sage: g.rename('a polynomial')
            sage: g
            a polynomial
            sage: g + x
            x^3 + 2*x - 5
            sage: h = g^100
            sage: str(h)[:20]
            'x^300 + 100*x^298 - '
            sage: h.rename('x^300 + ...')
            sage: h
            x^300 + ...

        Real numbers are not Python classes, so rename is not supported::

            sage: a = 3.14
            sage: type(a)
            <type 'sage.rings.real_mpfr.RealLiteral'>
            sage: a.rename('pi')
            Traceback (most recent call last):
            ...
            NotImplementedError: object does not support renaming: 3.14000000000000

        .. note::

           The reason C-extension types are not supported by default
           is if they were then every single one would have to carry
           around an extra attribute, which would be slower and waste
           a lot of memory.

           To support them for a specific class, add a
           ``cdef public __custom_name`` attribute.
        """
        if x is None:
            #if hasattr(self, '__custom_name'):
            # that's tested in reset_name anyway...
            self.reset_name()
        else:
            try:
                self.__custom_name = str(x)
            except AttributeError:
                raise NotImplementedError, "object does not support renaming: %s"%self

    def reset_name(self):
        """
        Remove the custrom name of an object.

        EXAMPLES::

            sage: P.<x> = QQ[]
            sage: P
            Univariate Polynomial Ring in x over Rational Field
            sage: P.rename('A polynomial ring')
            sage: P
            A polynomial ring
            sage: P.reset_name()
            sage: P
            Univariate Polynomial Ring in x over Rational Field
        """
        if hasattr(self, '__custom_name'):
            del self.__custom_name


    def __repr__(self):
        """
        Default method for string representation.

        NOTE:

        Do not overwrite this method. Instead, implement
        a ``_repr_`` (single underscore) method.

        EXAMPLES:

        By default, the string representation coincides with
        the output of the single underscore ``_repr_``::

            sage: P.<x> = QQ[]
            sage: repr(P) == P._repr_()  #indirect doctest
            True

        Using :meth:`rename`, the string representation can
        be customized::

            sage: P.rename('A polynomial ring')
            sage: repr(P) == P._repr_()
            False

        The original behaviour is restored with :meth:`reset_name`.

            sage: P.reset_name()
            sage: repr(P) == P._repr_()
            True
        """
        try:
            name = self.__custom_name
            if name is not None:
                return name
        except AttributeError:
            pass
        try:
            repr_func = self._repr_
        except AttributeError:
            return str(type(self))
        else:
            return repr_func()

    def __hash__(self):
        return hash(self.__repr__())


    #############################################################################
    # DATABASE Related code
    #############################################################################

    def version(self):
        r"""
        The version of Sage.

        Call this to save the version of Sage in this object.
        If you then save and load this object it will know in what
        version of Sage it was created.

        This only works on Python classes that derive from SageObject.
        """
        try:
            return self.__version
        except AttributeError:
            import sage.version
            self.__version = sage.version.version
            return self.__version

    def save(self, filename=None, compress=True):
        """
        Save self to the given filename.

        EXAMPLES::

            sage: f = x^3 + 5
            sage: f.save(SAGE_TMP + '/file')
            sage: load(SAGE_TMP + '/file.sobj')
            x^3 + 5
        """
        if filename is None:
            try:
                filename = self._default_filename
            except AttributeError:
                raise RuntimeError, "no default filename, so it must be specified"
        filename = process(filename)
        try:
            self._default_filename = filename
        except AttributeError:
            pass
        open(filename, 'wb').write(self.dumps(compress))

    def dump(self, filename, compress=True):
        """
        Same as self.save(filename, compress)
        """
        return self.save(filename, compress=compress)

    def dumps(self, compress=True):
        """
        Dump self to a string s, which can later be reconstituted
        as self using loads(s).
        """
        # the protocol=2 is very important -- this enables
        # saving extensions classes (with no attributes).
        s = cPickle.dumps(self, protocol=2)
        if compress:
            return comp.compress(s)
        else:
            return s

    def db(self, name, compress=True):
        r"""
        Dumps self into the Sage database.  Use db(name) by itself to
        reload.

        The database directory is ``$HOME/.sage/db``
        """
        #if name is None:
        #    name = self._db_name()
        from sage.misc.all import SAGE_DB
        return self.dump('%s/%s'%(SAGE_DB,name), compress=compress)

##     def _db_name(self):
##         t = str(type(self)).split()[-1][1:-2]
##         try:
##             d = str(self._defining_params_())
##         except AttributeError:
##             d = str(self)
##         d = '_'.join(d.split())
##         from sage.misc.all import SAGE_DB
##         if not os.path.exists('%s/%s'%(SAGE_DB, t)):
##             os.makedirs(t)
##         return '%s/%s'%(t, d)


    #############################################################################
    # Category theory / structure
    #############################################################################

    def category(self):
        from sage.categories.all import Objects
        return Objects()

    def _test_category(self, **options):
        """
        Run generic tests on the method :meth:`.category`.

        See also: :class:`TestSuite`.

        EXAMPLES::

            sage: O = SageObject()
            sage: O._test_category()

        Let us now write a broken :meth:`.category` method::

            sage: class CCls(SageObject):
            ...       def category(self):
            ...           return 3
            sage: CC = CCls()
            sage: CC._test_category()
            Traceback (most recent call last):
            ...
            AssertionError: False is not true
        """
        from sage.categories.category import Category
        from sage.categories.objects import Objects
        tester = self._tester(**options)
        category = self.category()
        tester.assert_(isinstance(category, Category))
        tester.assert_(category.is_subcategory(Objects()))
        tester.assert_(self in category)

##     def category(self):
##         try:
##             return self.__category
##         except AttributeError:
##             from sage.categories.all import Objects
##             return Objects()

##     def _set_category(self, C):
##         self.__category = C

    #############################################################################
    # Test framework
    #############################################################################

    def _tester(self, **options):
        """
        Returns a gadget attached to ``self`` providing testing utilities.

        This is used by :class:`sage.misc.sage_unittest.TestSuite` and the
        ``_test_*`` methods.

        EXAMPLES::

            sage: tester = ZZ._tester()

            sage: tester.assert_(1 == 1)
            sage: tester.assert_(1 == 0)
            Traceback (most recent call last):
            ...
            AssertionError: False is not true
            sage: tester.assert_(1 == 0, "this is expected to fail")
            Traceback (most recent call last):
            ...
            AssertionError: this is expected to fail

            sage: tester.assertEquals(1, 1)
            sage: tester.assertEquals(1, 0)
            Traceback (most recent call last):
            ...
            AssertionError: 1 != 0

        The available assertion testing facilities are the same as in
        :class:`unittest.TestCase`, which see (actually, by a slight
        abuse, tester is currently an instance of this class).

        TESTS::

            sage: ZZ._tester(tester = tester) is tester
            True
        """
        from sage.misc.sage_unittest import instance_tester
        return instance_tester(self, **options)

    def _test_not_implemented_methods(self, **options):
        """
        Checks that all required methods for this object are implemented

        TESTS::

            sage: class Abstract(SageObject):
            ...       @abstract_method
            ...       def bla(self):
            ...           "returns bla"
            ...
            sage: class Concrete(Abstract):
            ...       def bla(self):
            ...           return 1
            ...
            sage: class IncompleteConcrete(Abstract):
            ...       pass
            sage: Concrete()._test_not_implemented_methods()
            sage: IncompleteConcrete()._test_not_implemented_methods()
            Traceback (most recent call last):
            ...
            AssertionError: Not implemented method: bla

        """
        tester = self._tester(**options)
        for name in dir(self):
            try:
                getattr(self, name)
            except NotImplementedError:
                # It would be best to make sure that this NotImplementedError was triggered by AbstractMethod
                tester.fail("Not implemented method: %s"%name)
            except:
                pass

    def _test_pickling(self, **options):
        """
        Checks that this object can be pickled and unpickled properly.

        EXAMPLES::

            sage: ZZ._test_pickling()

        SEE ALSO: :func:`dumps` :func:`loads`

        TESTS::

            sage: class Bla(SageObject): pass
            sage: Bla()._test_pickling()
            Traceback (most recent call last):
            ...
            PicklingError: Can't pickle <class '__main__.Bla'>: attribute lookup __main__.Bla failed

        TODO: for a stronger test, this could send the object to a
        remote Sage session, and get it back.
        """
        tester = self._tester(**options)
        from sage.misc.all import loads, dumps
        tester.assertEqual(loads(dumps(self)), self)

    #############################################################################
    # Coercions to interface objects
    #############################################################################

    # Sage
    def _sage_(self):
        return self

    def _interface_(self, I):
        """
        Return coercion of self to an object of the interface I.

        The result of coercion is cached, unless self is not a C
        extension class or ``self._interface_is_cached_()`` returns
        False.
        """
        c = self._interface_is_cached_()
        if c:
            try:
                X = self.__interface[I]
                X._check_valid()
                return X
            except (AttributeError, TypeError):
                try:
                    self.__interface = {}
                except AttributeError:
                    # do this because C-extension classes won't have
                    # an __interface attribute.
                    pass
            except (KeyError, ValueError):
                pass
        nm = I.name()
        init_func = getattr(self, '_%s_init_' % nm, None)
        if init_func is not None:
            s = init_func()
        else:
            try:
                s = self._interface_init_(I)
            except:
                raise NotImplementedError, "coercion of object %s to %s not implemented:\n%s\n%s"%\
                  (repr(self), I)
        X = I(s)
        if c:
            try:
                self.__interface[I] = X
            except AttributeError:
                pass
        return X

    def _interface_init_(self, I=None):
        return repr(self)

    def _interface_is_cached_(self):
        """
        Return True if the interface objects are cached.

        If you have an object x and do gp(x), the result is cached if
        this function returns True.
        """
        return True

    def _gap_(self, G=None):
        if G is None:
            import sage.interfaces.gap
            G = sage.interfaces.gap.gap
        return self._interface_(G)

    def _gap_init_(self):
        import sage.interfaces.gap
        I = sage.interfaces.gap.gap
        return self._interface_init_(I)

    def _gp_(self, G=None):
        if G is None:
            import sage.interfaces.gp
            G = sage.interfaces.gp.gp
        return self._interface_(G)

    def _gp_init_(self):
        return self._pari_init_()

    def _kash_(self, G=None):
        if G is None:
            import sage.interfaces.kash
            G = sage.interfaces.kash.kash
        return self._interface_(G)

    def _kash_init_(self):
        import sage.interfaces.kash
        I = sage.interfaces.kash.kash
        return self._interface_init_(I)

    def _axiom_(self, G=None):
        if G is None:
            import sage.interfaces.axiom
            G = sage.interfaces.axiom.axiom
        return self._interface_(G)

    def _axiom_init_(self):
        import sage.interfaces.axiom
        I = sage.interfaces.axiom.axiom
        return self._interface_init_(I)

    def _fricas_(self, G=None):
        if G is None:
            import sage.interfaces.fricas
            G = sage.interfaces.fricas.fricas
        return self._interface_(G)

    def _fricas_init_(self):
        import sage.interfaces.fricas
        I = sage.interfaces.fricas.fricas
        return self._interface_init_(I)

    def _giac_(self, G=None):
        if G is None:
            import sage.interfaces.giac
            G = sage.interfaces.giac.giac
        return self._interface_(G)

    def _giac_init_(self):
        import sage.interfaces.giac
        I = sage.interfaces.giac.giac
        return self._interface_init_(I)

    def _maxima_(self, G=None):
        if G is None:
            import sage.interfaces.maxima
            G = sage.interfaces.maxima.maxima
        return self._interface_(G)

    def _maxima_init_(self):
        import sage.interfaces.maxima
        I = sage.interfaces.maxima.maxima
        return self._interface_init_(I)

    def _maxima_lib_(self, G=None):
        from sage.interfaces.maxima_lib import maxima_lib
        return self._interface_(maxima_lib)

    def _maxima_lib_init_(self):
        return self._maxima_init_()

    def _magma_init_(self, magma):
        """
        Given a Magma interpreter M, return a string that evaluates in
        that interpreter to the Magma object corresponding to self.
        This function may call the magma interpreter when it runs.

        INPUT:

        - ``magma`` -- a Magma interface

        OUTPUT:

        - string

        EXAMPLES::

            sage: n = -3/7
            sage: n._magma_init_(magma)
            '-3/7'

        Some other examples that illustrate conversion to Magma.
        ::

            sage: n = -3/7
            sage: m2 = Magma()
            sage: magma(n)                        # optional - magma
            -3/7
            sage: magma(n).parent()               # optional - magma
            Magma
            sage: magma(n).parent() is m2         # optional - magma
            False
            sage: magma(n).parent() is magma      # optional - magma
            True

        This example illustrates caching, which happens automatically
        since K is a Python object::

            sage: K.<a> = NumberField(x^3 + 2)
            sage: magma(K) is magma(K)        # optional - magma
            True
            sage: magma2 = Magma()
            sage: magma(K) is magma2(K)       # optional - magma
            False
        """
        return repr(self)  # default

    def _macaulay2_(self, G=None):
        if G is None:
            import sage.interfaces.macaulay2
            G = sage.interfaces.macaulay2.macaulay2
        return self._interface_(G)

    def _macaulay2_init_(self):
        import sage.interfaces.macaulay2
        I = sage.interfaces.macaulay2.macaulay2
        return self._interface_init_(I)

    def _maple_(self, G=None):
        if G is None:
            import sage.interfaces.maple
            G = sage.interfaces.maple.maple
        return self._interface_(G)

    def _maple_init_(self):
        import sage.interfaces.maple
        I = sage.interfaces.maple.maple
        return self._interface_init_(I)

    def _mathematica_(self, G=None):
        if G is None:
            import sage.interfaces.mathematica
            G = sage.interfaces.mathematica.mathematica
        return self._interface_(G)

    def _mathematica_init_(self):
        import sage.interfaces.mathematica
        I = sage.interfaces.mathematica.mathematica
        return self._interface_init_(I)

    def _octave_(self, G=None):
        if G is None:
            import sage.interfaces.octave
            G = sage.interfaces.octave.octave
        return self._interface_(G)

    def _octave_init_(self):
        import sage.interfaces.octave
        I = sage.interfaces.octave.octave
        return self._interface_init_(I)

    def _r_init_(self):
        """
        Return default string expression that evaluates in R to this
        object.

        OUTPUT:

        - string

        EXAMPLES::

            sage: a = 2/3
            sage: a._r_init_()
            '2/3'
        """
        import sage.interfaces.r
        I = sage.interfaces.r.r
        return self._interface_init_(I)

    def _singular_(self, G=None, have_ring=False):
        if G is None:
            import sage.interfaces.singular
            G = sage.interfaces.singular.singular
        return self._interface_(G)

    def _singular_init_(self, have_ring=False):
        import sage.interfaces.singular
        I = sage.interfaces.singular.singular
        return self._interface_init_(I)

    # PARI (slightly different, since is via C library, hence instance is unique)
    def _pari_(self):
        if self._interface_is_cached_():
            try:
                return self.__pari
            except AttributeError:
                pass
        from sage.libs.pari.all import pari
        x = pari(self._pari_init_())
        if self._interface_is_cached_():
            try:
                self.__pari = x
            except AttributeError:
                # do this because C-extension class won't have a __pari attribute.
                pass
        return x

    def _pari_init_(self):
        from sage.interfaces.gp import gp
        return self._interface_init_(gp)


######################################################
# A python-accessible version of the one in coerce.pxi
# Where should it be?

def have_same_parent(self, other):
    """
    EXAMPLES::

        sage: from sage.structure.sage_object import have_same_parent
        sage: have_same_parent(1, 3)
        True
        sage: have_same_parent(1, 1/2)
        False
        sage: have_same_parent(gap(1), gap(1/2))
        True
    """
    from sage.structure.coerce import parent
    return parent(self) == parent(other)

##################################################################

def load(*filename, compress=True, verbose=True):
    """
    Load Sage object from the file with name filename, which will have
    an .sobj extension added if it doesn't have one.  Or, if the input
    is a filename ending in .py, .pyx, or .sage, load that file into
    the current running session.  Loaded files are not loaded into
    their own namespace, i.e., this is much more like Python's
    ``execfile`` than Python's ``import``.

    .. note::

       There is also a special Sage command (that is not
       available in Python) called load that you use by typing

       ::

          sage: load filename.sage           # not tested

       The documentation below is not for that command.  The
       documentation for load is almost identical to that for attach.
       Type attach? for help on attach.

    This function also loads a ``.sobj`` file over a network by
    specifying the full URL.  (Setting ``verbose = False`` suppresses
    the loading progress indicator.)

    Finally, if you give multiple positional input arguments, then all
    of those files are loaded, or all of the objects are loaded and a
    list of the corresponding loaded objects is returned.

    EXAMPLE::

        sage: u = 'http://sage.math.washington.edu/home/was/db/test.sobj'
        sage: s = load(u)                                                  # optional - internet
        Attempting to load remote file: http://sage.math.washington.edu/home/was/db/test.sobj
        Loading: [.]
        sage: s                                                            # optional - internet
        'hello SAGE'

    We test loading a file or multiple files or even mixing loading files and objects::

        sage: t=tmp_filename()+'.py'; open(t,'w').write("print 'hello world'")
        sage: load(t)
        hello world
        sage: load(t,t)
        hello world
        hello world
        sage: t2=tmp_filename(); save(2/3,t2)
        sage: load(t,t,t2)
        hello world
        hello world
        [None, None, 2/3]
    """
    import sage.misc.preparser
    if len(filename) != 1:
        v = [load(file, compress=True, verbose=True) for file in filename]
        ret = False
        for file in filename:
            if not sage.misc.preparser.is_loadable_filename(file):
                ret = True
        return v if ret else None
    else:
        filename = filename[0]

    if sage.misc.preparser.is_loadable_filename(filename):
        sage.misc.preparser.load(filename, globals())
        return

    ## Check if filename starts with "http://" or "https://"
    lower = filename.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        from sage.misc.remote_file import get_remote_file
        filename = get_remote_file(filename, verbose=verbose)
        tmpfile_flag = True
    elif lower.endswith('.f') or lower.endswith('.f90'):
        globals()['fortran'](filename)
        return
    else:
        tmpfile_flag = False
        filename = process(filename)

    ## Load file by absolute filename
    X = loads(open(filename).read(), compress=compress)
    try:
        X._default_filename = os.path.abspath(filename)
    except AttributeError:
        pass

    ## Delete the tempfile, if it exists
    if tmpfile_flag == True:
        os.unlink(filename)

    return X


def save(obj, filename=None, compress=True, **kwds):
    """
    Save ``obj`` to the file with name ``filename``, which will have an
    ``.sobj`` extension added if it doesn't have one, or if ``obj``
    doesn't have its own ``save()`` method, like e.g. Python tuples.

    For image objects and the like (which have their own ``save()`` method),
    you may have to specify a specific extension, e.g. ``.png``, if you
    don't want the object to be saved as a Sage object (or likewise, if
    ``filename`` could be interpreted as already having some extension).

    .. warning::

       This will *replace* the contents of the file if it already exists.

    EXAMPLES::

        sage: a = matrix(2, [1,2,3,-5/2])
        sage: objfile = SAGE_TMP + 'test.sobj'
        sage: objfile_short = SAGE_TMP + 'test'
        sage: save(a, objfile)
        sage: load(objfile_short)
        [   1    2]
        [   3 -5/2]
        sage: E = EllipticCurve([-1,0])
        sage: P = plot(E)
        sage: save(P, objfile_short)   # saves the plot to "test.sobj"
        sage: save(P, filename=SAGE_TMP + "sage.png", xmin=-2)
        sage: save(P, SAGE_TMP + "filename.with.some.wrong.ext")
        Traceback (most recent call last):
        ...
        ValueError: allowed file extensions for images are '.eps', '.pdf', '.png', '.ps', '.sobj', '.svg'!
        sage: print load(objfile)
        Graphics object consisting of 2 graphics primitives
        sage: save("A python string", SAGE_TMP + 'test')
        sage: load(objfile)
        'A python string'
        sage: load(objfile_short)
        'A python string'

    TESTS:

    Check that #11577 is fixed::

        sage: filename = SAGE_TMP + "foo.bar" # filename containing a dot
        sage: save((1,1),filename)            # saves tuple to "foo.bar.sobj"
        sage: load(filename)
        (1, 1)
    """
    # Add '.sobj' if the filename currently has no extension
    # and also if the object doesn't have its own save() method (#11577)
    # since we otherwise assume below it is an image object:
    if (os.path.splitext(filename)[1] == ''
        or (os.path.splitext(filename)[1] != '.sobj'
             and not hasattr(obj,"save"))):
        filename += '.sobj'

    if filename.endswith('.sobj'):
        try:
            obj.save(filename=filename, compress=compress, **kwds)
        except (AttributeError, RuntimeError, TypeError):
            s = cPickle.dumps(obj, protocol=2)
            if compress:
                s = comp.compress(s)
            open(process(filename), 'wb').write(s)
    else:
        # Saving an object to an image file.
        obj.save(filename, **kwds)

def dumps(obj, compress=True):
    """
    Dump obj to a string s.  To recover obj, use ``loads(s)``.

    .. seealso:: :func:`dumps`

    EXAMPLES::

        sage: a = 2/3
        sage: s = dumps(a)
        sage: print len(s)
        49
        sage: loads(s)
        2/3
    """
    if make_pickle_jar:
        picklejar(obj)
    try:
        return obj.dumps(compress)
    except (AttributeError, RuntimeError, TypeError):
        if compress:
            return comp.compress(cPickle.dumps(obj, protocol=2))
        else:
            return cPickle.dumps(obj, protocol=2)

# This is used below, and also by explain_pickle.py
unpickle_override = {}

def register_unpickle_override(module, name, callable, call_name=None):
    r"""
    Python pickles include the module and class name of classes.
    This means that rearranging the Sage source can invalidate old
    pickles.  To keep the old pickles working, you can call
    register_unpickle_override with an old module name and class name,
    and the Python callable (function, class with __call__ method, etc.)
    to use for unpickling.  (If this callable is a value in some module,
    you can specify the module name and class name, for the benefit of
    explain_pickle(..., in_current_sage=True).)

    EXAMPLES::

        sage: from sage.structure.sage_object import unpickle_override, register_unpickle_override
        sage: unpickle_global('sage.rings.integer', 'Integer')
        <type 'sage.rings.integer.Integer'>

    Now we horribly break the pickling system::

        sage: register_unpickle_override('sage.rings.integer', 'Integer', Rational, call_name=('sage.rings.rational', 'Rational'))
        sage: unpickle_global('sage.rings.integer', 'Integer')
        <type 'sage.rings.rational.Rational'>

    And we reach into the internals and put it back::

        sage: del unpickle_override[('sage.rings.integer', 'Integer')]
        sage: unpickle_global('sage.rings.integer', 'Integer')
        <type 'sage.rings.integer.Integer'>
    """
    unpickle_override[(module,name)] = (callable, call_name)

def unpickle_global(module, name):
    r"""
    Given a module name and a name within that module (typically a class
    name), retrieve the corresponding object.  This normally just looks
    up the name in the module, but it can be overridden by
    register_unpickle_override.  This is used in the Sage unpickling
    mechanism, so if the Sage source code organization changes,
    register_unpickle_override can allow old pickles to continue to work.

    EXAMPLES::

        sage: from sage.structure.sage_object import unpickle_override, register_unpickle_override
        sage: unpickle_global('sage.rings.integer', 'Integer')
        <type 'sage.rings.integer.Integer'>

    Now we horribly break the pickling system::

        sage: register_unpickle_override('sage.rings.integer', 'Integer', Rational, call_name=('sage.rings.rational', 'Rational'))
        sage: unpickle_global('sage.rings.integer', 'Integer')
        <type 'sage.rings.rational.Rational'>

    And we reach into the internals and put it back::

        sage: del unpickle_override[('sage.rings.integer', 'Integer')]
        sage: unpickle_global('sage.rings.integer', 'Integer')
        <type 'sage.rings.integer.Integer'>
    """
    unpickler = unpickle_override.get((module, name))
    if unpickler is not None:
        return unpickler[0]

    mod = sys_modules.get(module)
    if mod is not None:
        return getattr(mod, name)
    __import__(module)
    mod = sys_modules[module]
    return getattr(mod, name)

def loads(s, compress=True):
    """
    Recover an object x that has been dumped to a string s
    using ``s = dumps(x)``.

    .. seealso:: :func:`dumps`

    EXAMPLES::

        sage: a = matrix(2, [1,2,3,-4/3])
        sage: s = dumps(a)
        sage: loads(s)
        [   1    2]
        [   3 -4/3]

    If compress is True (the default), it will try to decompress
    the data with zlib and with bz2 (in turn); if neither succeeds,
    it will assume the data is actually uncompressed.  If compress=False
    is explicitly specified, then no decompression is attempted.

    ::

        sage: v = [1..10]
        sage: loads(dumps(v, compress=False)) == v
        True
        sage: loads(dumps(v, compress=False), compress=True) == v
        True
        sage: loads(dumps(v, compress=True), compress=False)
        Traceback (most recent call last):
        ...
        UnpicklingError: invalid load key, 'x'.
    """
    if not isinstance(s, str):
        raise TypeError, "s must be a string"
    if compress:
        try:
            s = comp.decompress(s)
        except Exception, msg1:
            try:
                s = comp_other.decompress(s)
            except Exception, msg2:
                # Maybe data is uncompressed?
                pass

    unpickler = cPickle.Unpickler(StringIO(s))
    unpickler.find_global = unpickle_global

    return unpickler.load()


cdef bint make_pickle_jar = os.environ.has_key('SAGE_PICKLE_JAR')

def picklejar(obj, dir=None):
    """
    Create pickled sobj of obj in dir, with name the absolute value of
    the hash of the pickle of obj.  This is used in conjunction with
    sage.structure.sage_object.unpickle_all.

    To use this to test the whole Sage library right now, set the
    environment variable SAGE_PICKLE_JAR, which will make it so dumps
    will by default call picklejar with the default dir.  Once you do
    that and doctest Sage, you'll find that the SAGE_ROOT/tmp/
    contains a bunch of pickled objects along with corresponding txt
    descriptions of them.  Use the
    sage.structure.sage_object.unpickle_all to see if they unpickle
    later.

    INPUTS:

    - ``obj`` -- a pickleable object

    - ``dir`` -- a string or None; if None defaults to
      ``SAGE_ROOT/tmp/pickle_jar``

    EXAMPLES::

        sage: dir = tmp_dir()
        sage: sage.structure.sage_object.picklejar(1, dir)
        sage: sage.structure.sage_object.picklejar('test', dir)
        sage: len(os.listdir(dir))   # Two entries (sobj and txt) for each object
        4

    TESTS:

    Test an unaccessible directory::

        sage: import os
        sage: os.chmod(dir, 0000)
        sage: sage.structure.sage_object.picklejar(1, dir + '/noaccess')
        Traceback (most recent call last):
        ...
        OSError: ...
        sage: os.chmod(dir, 0755)
    """
    if dir is None:
        dir = os.environ['SAGE_ROOT'] + '/tmp/pickle_jar/'
    try:
        os.makedirs(dir)
    except OSError as err:
        # It is not an error if the directory exists
        import errno
        if not err.errno == errno.EEXIST:
            raise

    s = comp.compress(cPickle.dumps(obj,protocol=2))

    typ = str(type(obj))
    name = ''.join([x if (x.isalnum() or x == '_') else '_' for x in typ])
    base = '%s/%s'%(dir, name)
    if os.path.exists(base):
        i = 0
        while os.path.exists(base + '-%s'%i):
            i += 1
        base += '-%s'%i

    open(base + '.sobj', 'wb').write(s)
    txt = "type(obj) = %s\n"%typ
    import sage.version
    txt += "version = %s\n"%sage.version.version
    txt += "obj =\n'%s'\n"%str(obj)

    open(base + '.txt', 'w').write(txt)

def unpickle_all(dir = None, debug=False, run_test_suite=False):
    """
    Unpickle all sobj's in the given directory, reporting failures as
    they occur.  Also printed the number of successes and failure.

    INPUT:

     - ``dir`` -- a string; the name of a directory (or of a .tar.bz2
       file that decompresses to a directory) full of pickles.
       (default: the standard pickle jar)
     - ``debug`` -- a boolean (default: False)
       whether to report a stacktrace in case of failure
     - ``run_test_suite`` -- a boolean (default: False)
       whether to run ``TestSuite(x).run()`` on the unpickled objects

    EXAMPLES::

        sage: dir = tmp_dir()
        sage: sage.structure.sage_object.picklejar('hello', dir)
        sage: sage.structure.sage_object.unpickle_all(dir)
        Successfully unpickled 1 objects.
        Failed to unpickle 0 objects.

    We unpickle the standard pickle jar. This doctest tests that
    all "standard pickles" unpickle::

        sage: sage.structure.sage_object.unpickle_all()  # (4s on sage.math, 2011)
        doctest:... DeprecationWarning: This class is replaced by Matrix_modn_dense_float/Matrix_modn_dense_double.
        See http://trac.sagemath.org/4260 for details.
        Successfully unpickled ... objects.
        Failed to unpickle 0 objects.

    Every so often the standard pickle jar should be updated by
    running the doctest suite with the environment variable
    SAGE_PICKLE_JAR set, then copying the files from
    SAGE_ROOT/tmp/pickle_jar* into the standard pickle jar.

    Do you want to find *lots* of little issues in Sage? Run the following:

        sage: print "x"; sage.structure.sage_object.unpickle_all(run_test_suite = True) # todo: not tested

    This runs :class:`TestSuite` tests on all objects in the Sage pickle
    jar. Some of those objects seem to unpickle properly, but do not
    pass the tests because their internal data structure is messed
    up. In most cases though it is just that their source file misses
    a TestSuite call, and therefore some misfeatures went unnoticed
    (typically Parents not implementing the ``an_element`` method).
    """
    if dir is None:
        dir = os.environ['SAGE_DATA'] + '/extcode/pickle_jar/pickle_jar.tar.bz2'
    i = 0
    j = 0
    failed = []
    tracebacks = []
    # This could use instead Python's tarfile module
    if dir.endswith('.tar.bz2'):
        # create a temporary directory
        from sage.misc.all import tmp_dir
        T = tmp_dir()
        # extract tarball to it
        os.system('cd "%s"; bunzip2 -c "%s" | tar fx - '%(T, os.path.abspath(dir)))
        # Now use the directory in the tarball instead of dir
        dir = T + "/" + os.listdir(T)[0]

    for A in sorted(os.listdir(dir)):
        if A.endswith('.sobj'):
            try:
                object = load(dir + '/' + A)
                if run_test_suite:
                    TestSuite(object).run(catch = False)
                i += 1
            except Exception, msg:
                j += 1
                if run_test_suite:
                    print " * unpickle failure: TestSuite(load('%s')).run()"%(dir+'/'+A)
                else:
                    print " * unpickle failure: load('%s')"%(dir+'/'+A)
                failed.append(A)
                if debug:
                    tracebacks.append(sys.exc_info())

    if len(failed) > 0:
        print "Failed:\n%s"%('\n'.join(failed))
    print "Successfully unpickled %s objects."%i
    print "Failed to unpickle %s objects."%j
    if debug:
        return tracebacks
