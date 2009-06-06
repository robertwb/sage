"""
A tool for inspecting Python pickles

AUTHORS:

- Carl Witty (2009-03)

The explain_pickle function takes a pickle and produces Sage code that
will evaluate to the contents of the pickle.  Ideally, the combination
of explain_pickle to produce Sage code and sage_eval to evaluate the code
would be a 100% compatible implementation of cPickle's unpickler; this
is almost the case now.

EXAMPLES::

    sage: explain_pickle(dumps(12345))
    pg_make_integer = unpickle_global('sage.rings.integer', 'make_integer')
    pg_make_integer('c1p')
    sage: explain_pickle(dumps(polygen(QQ)))
    pg_Polynomial_rational_dense = unpickle_global('sage.rings.polynomial.polynomial_element_generic', 'Polynomial_rational_dense')
    pg_PolynomialRing = unpickle_global('sage.rings.polynomial.polynomial_ring_constructor', 'PolynomialRing')
    pg_RationalField = unpickle_global('sage.rings.rational_field', 'RationalField')
    pg = unpickle_instantiate(pg_RationalField, ())
    pg_make_rational = unpickle_global('sage.rings.rational', 'make_rational')
    pg_Polynomial_rational_dense(pg_PolynomialRing(pg, 'x', None, False), [pg_make_rational('0'), pg_make_rational('1')], False, True)
    sage: sage_eval(explain_pickle(dumps(polygen(QQ)))) == polygen(QQ)
    True

By default (as above) the code produced contains calls to several
utility functions (unpickle_global, etc.); this is done so that the
code is truly equivalent to the pickle.  If the pickle can be loaded
into a future version of Sage, then the code that explain_pickle
produces today should work in that future Sage as well.

It is also possible to produce simpler code, that is tied to the current
version of Sage; here are the above two examples again::

    sage: explain_pickle(dumps(12345), in_current_sage=True)
    from sage.rings.integer import make_integer
    make_integer('c1p')
    sage: explain_pickle(dumps(polygen(QQ)), in_current_sage=True)
    from sage.rings.polynomial.polynomial_element_generic import Polynomial_rational_dense
    from sage.rings.rational import make_rational
    Polynomial_rational_dense(PolynomialRing(RationalField(), 'x', None, False), [make_rational('0'), make_rational('1')], False, True)

The explain_pickle function has several use cases.

  - Write pickling support for your classes

    You can use explain_pickle to see what will happen when a pickle
    is unpickled.  Consider: is this sequence of commands something
    that can be easily supported in all future Sage versions, or does
    it expose internal design decisions that are subject to change?

  - Debug old pickles

    If you have a pickle from an old version of Sage that no longer
    unpickles, you can use explain_pickle to see what it is trying to
    do, to figure out how to fix it.

  - Use explain_pickle in doctests to help maintenance

    If you have a ``loads(dumps(S))`` doctest, you could also add an
    ``explain_pickle(dumps(S))`` doctest.  Then if something changes
    in a way that would invalidate old pickles, the output of
    ``explain_pickle`` will also change.  At that point, you can add
    the previous output of :obj:`explain_pickle` as a new set of
    doctests (and then update the :obj`explain_pickle` doctest to use
    the new output), to ensure that old pickles will continue to work.
    (These problems will also be caught using the :obj:`picklejar`,
    but having the tests directly in the relevant module is clearer.)

As mentioned above, there are several output modes for :obj:`explain_pickle`,
that control fidelity versus simplicity of the output.  For example,
the GLOBAL instruction takes a module name and a class name and
produces the corresponding class.  So GLOBAL of ``sage.rings.integer``,
``Integer`` is approximately equivalent to ``sage.rings.integer.Integer``.

However, this class lookup process can be customized (using
sage.structure.sage_object.register_unpickle_override).  For instance,
if some future version of Sage renamed ``sage/rings/integer.pyx`` to
``sage/rings/knuth_was_here.pyx``, old pickles would no longer work unless
register_unpickle_override was used; in that case, GLOBAL of
'sage.rings.integer', 'integer' would mean
``sage.rings.knuth_was_here.integer``.

By default, ``explain_pickle`` will map this GLOBAL instruction to
``unpickle_global('sage.rings.integer', 'integer')``.  Then when this code
is evaluated, unpickle_global will look up the current mapping in the
register_unpickle_override table, so the generated code will continue
to work even in hypothetical future versions of Sage where integer.pyx
has been renamed.

If you pass the flag ``in_current_sage=True``, then
:obj:`explain_pickle` will generate code that may only work in the
current version of Sage, not in future versions.  In this case, it
would generate::

  from sage.rings.integer import integer

and if you ran explain_pickle in hypothetical future sage, it would generate:

  from sage.rings.knuth_was_here import integer

but the current code wouldn't work in the future sage.

If you pass the flag ``default_assumptions=True``, then
:obj:`explain_pickle` will generate code that would work in the
absence of any special unpickling information.  That is, in either
current Sage or hypothetical future Sage, it would generate::

  from sage.rings.integer import integer

The intention is that ``default_assumptions`` output is prettier (more
human-readable), but may not actually work; so it is only intended for
human reading.

There are several functions used in the output of :obj:`explain_pickle`.
Here I give a brief description of what they usually do, as well as
how to modify their operation (for instance, if you're trying to get
old pickles to work).

  - ``unpickle_global(module, classname)``:
    unpickle_global('sage.foo.bar', 'baz') is usually equivalent to
    sage.foo.bar.baz, but this can be customized with
    register_unpickle_override.

  - ``unpickle_newobj(klass, args)``:
    Usually equivalent to ``klass.__new__(klass, *args)``.  If
    ``klass`` is a Python class, then you can define :meth:`__new__`
    to control the result (this result actually need not be an
    instance of klass).  (This doesn't work for Cython classes.)

  - ``unpickle_build(obj, state)``:
    If ``obj`` has a :meth:`__setstate__` method, then this is equivalent to
    ``obj.__setstate__(state)``.  Otherwise uses state to set the attributes
    of ``obj``.  Customize by defining :meth:`__setstate__`.

  - ``unpickle_instantiate(klass, args)``:
    Usually equivalent to ``klass(*args)``.  Cannot be customized.

  - unpickle_appends(lst, vals):
    Appends the values in vals to lst.  If not ``isinstance(lst, list)``,
    can be customized by defining a :meth:`append` method.

"""

##########################################################################
#
#       Copyright (C) 2009 Carl Witty <Carl.Witty@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#
##########################################################################

from pickletools import genops

import zlib as comp
import bz2 as comp_other

from sage.misc.sage_input import SageInputBuilder, SageInputExpression
from sage.misc.sage_eval import sage_eval
from sage.structure.sage_object import unpickle_override, unpickle_global, dumps, register_unpickle_override
import pickletools
import types

import sys
import os
import sage.all
import new
import re

def explain_pickle(pickle=None, file=None, compress=True, **kwargs):
    r"""
    Explain a pickle. That is, produce source code such that evaluating
    the code is equivalent to loading the pickle.  Feeding the result
    of ``explain_pickle`` to ``sage_eval`` should be totally equivalent to loading
    the ``pickle`` with ``cPickle``.

    INPUTS:

     - ``pickle``   -- the pickle to explain, as a string (default: None)
     - ``file``     -- a filename of a pickle (default: None)
     - ``compress`` -- if False, don't attempt to decompress the pickle
                    (default: True)
     - ``in_current_sage`` -- if True, produce potentially simpler code that is
                           tied to the current version of Sage. (default: False)
     - ``default_assumptions`` -- if True, produce potentially simpler code that
                               assumes that generic unpickling code will be
                               used.  This code may not actually work.
                               (default: False)
     - ``eval`` -- if True, then evaluate the resulting code and return the
                evaluated result. (default: False)
     - ``preparse`` -- if True, then produce code to be evaluated with
                    Sage's preparser; if False, then produce standard
                    Python code; if None, then produce code that will work
                    either with or without the preparser.  (default: True)
     - ``pedantic`` -- if True, then carefully ensures that the result has
                    at least as much sharing as the result of cPickle
                    (it may have more, for immutable objects).  (default: False)

    Exactly one of ``pickle`` (a string containing a pickle) or
    ``file`` (the filename of a pickle) must be provided.

    EXAMPLES::

        sage: explain_pickle(dumps({('a', 'b'): [1r, 2r]}))
        {('a', 'b'):[1r, 2r]}
        sage: explain_pickle(dumps(RR(pi)), in_current_sage=True)
        from sage.rings.real_mpfr import __create__RealNumber_version0
        from sage.rings.real_mpfr import __create__RealField_version0
        __create__RealNumber_version0(__create__RealField_version0(53r, False, 'RNDN'), '3.4gvml245kc0@0', 32r)
        sage: s = 'hi'
        sage: explain_pickle(dumps((s, s)))
        ('hi', 'hi')
        sage: explain_pickle(dumps((s, s)), pedantic=True)
        si = 'hi'
        (si, si)
        sage: explain_pickle(dumps(5r))
        5r
        sage: explain_pickle(dumps(5r), preparse=False)
        5
        sage: explain_pickle(dumps(5r), preparse=None)
        int(5)
        sage: explain_pickle(dumps(22/7))
        pg_make_rational = unpickle_global('sage.rings.rational', 'make_rational')
        pg_make_rational('m/7')
        sage: explain_pickle(dumps(22/7), in_current_sage=True)
        from sage.rings.rational import make_rational
        make_rational('m/7')
        sage: explain_pickle(dumps(22/7), default_assumptions=True)
        from sage.rings.rational import make_rational
        make_rational('m/7')
    """
    if pickle is not None:
        p = pickle
    elif file is not None:
        p = open(file).read()
    else:
        raise ValueError, "Either pickle or file must be specified"

    if compress:
        try:
            p = comp.decompress(p)
        except Exception, msg1:
            try:
                p = comp_other.decompress(p)
            except Exception, msg2:
                # Maybe data is uncompressed?
                pass

    return explain_pickle_string(p, **kwargs)

def explain_pickle_string(pickle, in_current_sage=False,
                          default_assumptions=False, eval=False, preparse=True,
                          pedantic=False):
    r"""
    This is a helper function for explain_pickle.  It takes a decompressed
    pickle string as input; other than that, its options are all the same
    as explain_pickle.

    EXAMPLES::

        sage: sage.misc.explain_pickle.explain_pickle_string(dumps("Hello, world", compress=False))
        'Hello, world'

    (See the documentation for ``explain_pickle`` for many more examples.)
    """
    sib = SageInputBuilder(preparse=preparse)

    pe = PickleExplainer(sib, in_current_sage=in_current_sage,
                         default_assumptions=default_assumptions,
                         pedantic=pedantic)

    v = pe.run_pickle(pickle)

    ans = sib.result(sib(v))

    if eval:
        if default_assumptions:
            raise ValueError, "Not safe to evaluate code generated with default_assumptions"
        from sage.misc.sage_eval import sage_eval
        result = sage_eval(ans, preparse=preparse)
        print ans
        return result
    else:
        return ans

valid_name_re = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')
def name_is_valid(name):
    r"""
    Test whether a string is a valid Python identifier.  (We use a
    conservative test, that only allows ASCII identifiers.)

    EXAMPLES::

        sage: from sage.misc.explain_pickle import name_is_valid
        sage: name_is_valid('fred')
        True
        sage: name_is_valid('Yes!ValidName')
        False
        sage: name_is_valid('_happy_1234')
        True
    """
    # Technically, we also need to reject keywords...
    return bool(valid_name_re.match(name))

# The pickle interpreter can push and pop "marks" on the stack.
# This string is used as the representation of a mark.
the_mark = 'mark'

class PickleObject(object):
    r"""
    Pickles have a stack-based virtual machine.  The explain_pickle
    pickle interpreter mostly uses SageInputExpressions, from sage_input,
    as the stack values.  However, sometimes we want some more information
    about the value on the stack, so that we can generate better
    (prettier, less confusing) code.  In such cases, we push
    a PickleObject instead of a SageInputExpression.  A PickleObject
    contains a value (which may be a standard Python value, or a
    PickleDict or PickleInstance), an expression (a SageInputExpression),
    and an "immutable" flag (which checks whether this object
    has been converted to a SageInputExpression; if it has, then we
    must not mutate the object, since the SageInputExpression would not
    reflect the changes).
    """

    def __init__(self, value, expression):
        r"""
        Construct a PickleObject.

        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: v = PickleObject(1, 2)
            sage: v.value
            1
            sage: v.expression
            2
            sage: v.immutable
            False
        """
        self.value = value
        self.expression = expression
        self.immutable = False

    def _sage_input_(self, sib, coerced):
        r"""
        Extracts the expression from a PickleObject, and sets the immutable
        flag.

        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: v = PickleObject(1, 2)
            sage: v.immutable
            False
            sage: v._sage_input_('sib', False)
            2
            sage: v.immutable
            True
        """
        self.immutable = True
        return self.expression

class PickleDict(object):
    r"""
    An object which can be used as the value of a PickleObject.  The items
    is a list of key-value pairs, where the keys and values are
    SageInputExpressions.  We use this to help construct dictionary literals,
    instead of always starting with an empty dictionary and assigning to
    it.
    """
    def __init__(self, items):
        r"""
        Initialize a PickleDict.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: PickleDict([('a', 1)]).items
            [('a', 1)]
        """
        self.items = items

class PickleInstance(object):
    r"""
    An object which can be used as the value of a PickleObject.  Unlike
    other possible values of a PickleObject, a PickleInstance doesn't represent
    an exact value; instead, it gives the class (type) of the object.
    """
    def __init__(self, klass):
        r"""
        Initialize a PickleInstance.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: PickleInstance(Integer).klass
            <type 'sage.rings.integer.Integer'>
        """
        self.klass = klass

class PickleExplainer(object):
    r"""
    An interpreter for the pickle virtual machine, that executes
    symbolically and constructs SageInputExpressions instead of
    directly constructing values.
    """
    def __init__(self, sib, in_current_sage=False, default_assumptions=False,
                 pedantic=False):
        r"""
        Initialize a PickleExplainer interpreter for the pickle virtual machine.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: pe = PickleExplainer(SageInputBuilder(), in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: pe.in_current_sage
            True
            sage: pe.pedantic
            True
        """
        self.sib = sib
        self.in_current_sage = in_current_sage
        self.default_assumptions = default_assumptions
        self.pedantic = pedantic
        self.stopped = False
        self.stack = []
        self.memo = {}
        if in_current_sage and default_assumptions:
            raise ValueError, "in_current_sage and default_assumptions must not both be true"

        self.new_instance = self.sib.import_name('new', 'instance')

    def run_pickle(self, p):
        r"""
        Given an (uncompressed) pickle as a string, run the pickle
        in this virtual machine.  Once a STOP has been executed, return
        the result (a SageInputExpression representing code which, when
        evaluated, will give the value of the pickle).

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: sib(pe.run_pickle('T\5\0\0\0hello.'))
            {atomic:'hello'}
        """
        for (op, arg, pos) in genops(p):
            assert(not(self.stopped))
            try:
                handler = getattr(self, op.name)
            except AttributeError:
                raise NotImplementedError, 'PickleExplainer does not yet handle opcode %s' % op.name
            if arg is None:
                handler()
            else:
                handler(arg)

        assert(self.stopped)
        assert(len(self.stack) == 1)
        return self.stack[0]

    def check_value(self, v):
        r"""
        Check that the given value is either a SageInputExpression or a
        PickleObject. Used for internal sanity checking.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: pe.check_value(7)
            Traceback (most recent call last):
            ...
            AssertionError
            sage: pe.check_value(sib(7))
        """
        assert(isinstance(v, (SageInputExpression, PickleObject)))

    def push(self, v):
        r"""
        Push a value onto the virtual machine's stack.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: pe.push(sib(7))
            sage: pe.stack[-1]
            {atomic:7}
        """
        self.check_value(v)
        self.stack.append(v)

    def push_and_share(self, v):
        r"""
        Push a value onto the virtual machine's stack; also mark it as shared
        for sage_input if we are in pedantic mode.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: pe.push_and_share(sib(7))
            sage: pe.stack[-1]
            {atomic:7}
            sage: pe.stack[-1]._sie_share
            True
        """
        self.share(v)
        self.push(v)

    def pop(self):
        r"""
        Pop a value from the virtual machine's stack, and return it.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: pe.push(sib(7))
            sage: pe.pop()
            {atomic:7}
        """
        v = self.stack.pop()
        self.check_value(v)
        return v

    def push_mark(self):
        r"""
        Push a 'mark' onto the virtual machine's stack.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: pe.push_mark()
            sage: pe.stack[-1]
            'mark'
            sage: pe.stack[-1] is the_mark
            True
        """
        self.stack.append(the_mark)

    def pop_to_mark(self):
        r"""
        Pop all values down to the 'mark' from the virtual machine's stack,
        and return the values as a list.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: pe.push_mark()
            sage: pe.push(sib(7))
            sage: pe.push(sib('hello'))
            sage: pe.pop_to_mark()
            [{atomic:7}, {atomic:'hello'}]
        """
        slice = []
        while True:
            v = self.stack.pop()
            if v is the_mark:
                slice.reverse()
                return slice
            self.check_value(v)
            slice.append(v)

    def share(self, v):
        r"""
        Mark a sage_input value as shared, if we are in pedantic mode.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: v = sib(7)
            sage: v._sie_share
            False
            sage: pe.share(v)
            {atomic:7}
            sage: v._sie_share
            True
        """
        if self.pedantic:
            self.sib.share(v)
        return v

    def is_mutable_pickle_object(self, v):
        r"""
        Test whether a PickleObject is mutable (has never been converted
        to a SageInputExpression).

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: from sage.misc.sage_input import SageInputBuilder
            sage: sib = SageInputBuilder()
            sage: pe = PickleExplainer(sib, in_current_sage=True, default_assumptions=False, pedantic=True)
            sage: v = PickleObject(1, sib(1))
            sage: pe.is_mutable_pickle_object(v)
            True
            sage: sib(v)
            {atomic:1}
            sage: pe.is_mutable_pickle_object(v)
            False
        """
        return isinstance(v, PickleObject) and not v.immutable

    # Opcodes are in alphabetical order

    def APPEND(self):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(['a'])
                0: \x80 PROTO      2
                2: ]    EMPTY_LIST
                3: q    BINPUT     1
                5: U    SHORT_BINSTRING 'a'
                8: a    APPEND
                9: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            ['a']
            result: ['a']

        As shown above, we prefer to create a list literal.  This is not
        possible if the list is recursive::

            sage: v = []
            sage: v.append(v)
            sage: test_pickle(v)
                0: \x80 PROTO      2
                2: ]    EMPTY_LIST
                3: q    BINPUT     1
                5: h    BINGET     1
                7: a    APPEND
                8: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            si = []
            list.append(si, si)
            si
            result: [[...]]
        """

        obj = self.pop()
        lst = self.pop()
        self._APPENDS_helper(lst, [obj])

    def APPENDS(self):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(['a', 'b'])
                0: \x80 PROTO      2
                2: ]    EMPTY_LIST
                3: q    BINPUT     1
                5: (    MARK
                6: U        SHORT_BINSTRING 'a'
                9: U        SHORT_BINSTRING 'b'
               12: e        APPENDS    (MARK at 5)
               13: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            ['a', 'b']
            result: ['a', 'b']

        As shown above, we prefer to create a list literal.  This is not
        possible if the list is recursive::

            sage: v = []
            sage: v.append(v)
            sage: v.append(v)
            sage: test_pickle(v)
                0: \x80 PROTO      2
                2: ]    EMPTY_LIST
                3: q    BINPUT     1
                5: (    MARK
                6: h        BINGET     1
                8: h        BINGET     1
               10: e        APPENDS    (MARK at 5)
               11: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            si = []
            list.extend(si, [si, si])
            si
            result: [[...], [...]]
        """
        slice = self.pop_to_mark()
        lst = self.pop()
        self._APPENDS_helper(lst, slice)

    def _APPENDS_helper(self, lst, slice):
        r"""
        TESTS::

        See the doctests for APPEND and APPENDS for some simple indirect
        tests of this method.  Here we test some subtle behavior.

        For subtypes of list, we use list.append/list.extend instead of
        the append method of the object (TestAppendList.append raises
        an exception, so we can tell that cPickle doesn't call it either)::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(TestAppendList((True,))) # indirect doctest
                0: \x80 PROTO      2
                2: c    GLOBAL     'sage.misc.explain_pickle TestAppendList'
               43: q    BINPUT     1
               45: )    EMPTY_TUPLE
               46: \x81 NEWOBJ
               47: q    BINPUT     2
               49: \x88 NEWTRUE
               50: a    APPEND
               51: }    EMPTY_DICT
               52: q    BINPUT     3
               54: b    BUILD
               55: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from sage.misc.explain_pickle import TestAppendList
            si = unpickle_newobj(TestAppendList, ())
            list.append(si, True)
            si
            explain_pickle in_current_sage=False:
            pg_TestAppendList = unpickle_global('sage.misc.explain_pickle', 'TestAppendList')
            si = unpickle_newobj(pg_TestAppendList, ())
            unpickle_appends(si, [True])
            unpickle_build(si, {})
            si
            result: [True]

        For values which are not subtypes of list, we use their own append
        method::

            sage: v = TestAppendNonlist()
            sage: v.list = [False, None]
            sage: test_pickle(v, verbose_eval=True)
                0: \x80 PROTO      2
                2: c    GLOBAL     'sage.misc.explain_pickle TestAppendNonlist'
               46: q    BINPUT     1
               48: )    EMPTY_TUPLE
               49: R    REDUCE
               50: q    BINPUT     2
               52: (    MARK
               53: \x89     NEWFALSE
               54: N        NONE
               55: e        APPENDS    (MARK at 52)
               56: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from sage.misc.explain_pickle import TestAppendNonlist
            si = TestAppendNonlist()
            si.append(False)
            si.append(None)
            si
            explain_pickle in_current_sage=False:
            pg_TestAppendNonlist = unpickle_global('sage.misc.explain_pickle', 'TestAppendNonlist')
            pg = unpickle_instantiate(pg_TestAppendNonlist, ())
            unpickle_appends(pg, [False, None])
            pg
            evaluating explain_pickle in_current_sage=True:
            Fetching append attribute
            Fetching append attribute
            evaluating explain_pickle in_current_sage=False:
            Fetching append attribute
            loading pickle with cPickle:
            Fetching append attribute
            result: [False, None]

        We see above that the in_current_sage=True code doesn't quite match
        the other cases, because it fetches the append attribute twice
        instead of once.  If we set pedantic=True, then this is fixed.
        (We show only the changed parts of the output)::

            sage: test_pickle(v, verbose_eval=True, pedantic=True)
                0: \x80 PROTO      2
            ...
            explain_pickle in_current_sage=True:
            from sage.misc.explain_pickle import TestAppendNonlist
            si1 = TestAppendNonlist()
            si2 = si1.append
            si2(False)
            si2(None)
            si1
            ...
            evaluating explain_pickle in_current_sage=True:
            Fetching append attribute
            ...
        """
        # This has the side-effect of marking lst as immutable, if
        # slice happens to include lst.
        slice_exp = self.sib(slice)
        if self.is_mutable_pickle_object(lst) and isinstance(lst.value, list):
            lst.value.extend(slice)
            lst.expression = self.sib(lst.value)
        elif isinstance(lst, PickleObject) or self.default_assumptions:
            if isinstance(lst.value, list) or \
                    (isinstance(lst.value, PickleInstance) and
                     issubclass(lst.value.klass, list)) or \
                     self.default_assumptions:
                if len(slice) > 1:
                    self.sib.command(lst, self.sib.name('list').extend(lst, slice))
                else:
                    for s in slice:
                        self.sib.command(lst, self.sib.name('list').append(lst, self.sib(s)))
            else:
                if self.pedantic:
                    app = self.sib(lst).append
                    for s in slice:
                        self.sib.command(lst, app(self.sib(s)))
                else:
                    for s in slice:
                        self.sib.command(lst, self.sib(lst).append(self.sib(s)))
        else:
            self.sib.command(lst, self.sib.name('unpickle_appends')(self.sib(lst), slice_exp))
        self.push(lst)

    def BINFLOAT(self, f):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(float(pi))
                0: \x80 PROTO      2
                2: G    BINFLOAT   3.1415926535897931
               11: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            float(RR(3.1415926535897931))
            result: 3.1415926535897931
        """
        self.push(self.sib(f))

    def BINGET(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_LIST + BINPUT + 'x' + POP + BINGET + 'x' + '.')
                0: ]    EMPTY_LIST
                1: q    BINPUT     120
                3: 0    POP
                4: h    BINGET     120
                6: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            []
            result: []
        """
        self.push(self.memo[n])

    def BININT(self, n):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(dumps(100000r, compress=False))
                0: \x80 PROTO      2
                2: J    BININT     100000
                7: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            100000
            result: 100000
        """
        self.push_and_share(self.sib(n))

    def BININT1(self, n):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(dumps(100r, compress=False))
                0: \x80 PROTO      2
                2: K    BININT1    100
                4: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            100
            result: 100
        """
        self.push_and_share(self.sib(n))

    def BININT2(self, n):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(dumps(1000r, compress=False))
                0: \x80 PROTO      2
                2: M    BININT2    1000
                5: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            1000
            result: 1000
        """
        self.push_and_share(self.sib(n))

    def BINPUT(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_LIST + BINPUT + 'x' + POP + BINGET + 'x')
                0: ]    EMPTY_LIST
                1: q    BINPUT     120
                3: 0    POP
                4: h    BINGET     120
                6: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            []
            result: []
        """
        v = self.pop()
        self.memo[n] = v
        self.push(v)

    def BINSTRING(self, s):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle('T\5\0\0\0hello.')
                0: T    BINSTRING 'hello'
               10: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            'hello'
            result: 'hello'
        """
        self.push(PickleObject(s, self.share(self.sib(s))))

    def BINUNICODE(self, s):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(u'hi\u1234\U00012345')
                0: \x80 PROTO      2
                2: X    BINUNICODE u'hi\u1234\U00012345'
               16: q    BINPUT     1
               18: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            u'hi\u1234\U00012345'
            result: u'hi\u1234\U00012345'
        """
        self.push_and_share(self.sib(s))

    def BUILD(self):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(TestBuild())
                0: \x80 PROTO      2
                2: c    GLOBAL     'sage.misc.explain_pickle TestBuild'
               38: q    BINPUT     1
               40: )    EMPTY_TUPLE
               41: \x81 NEWOBJ
               42: q    BINPUT     2
               44: }    EMPTY_DICT
               45: q    BINPUT     3
               47: U    SHORT_BINSTRING 'x'
               50: K    BININT1    3
               52: s    SETITEM
               53: }    EMPTY_DICT
               54: q    BINPUT     4
               56: U    SHORT_BINSTRING 'y'
               59: K    BININT1    4
               61: s    SETITEM
               62: \x86 TUPLE2
               63: b    BUILD
               64: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from sage.misc.explain_pickle import TestBuild
            si = unpickle_newobj(TestBuild, ())
            si.__dict__['x'] = 3
            si.y = 4
            si
            explain_pickle in_current_sage=False:
            pg_TestBuild = unpickle_global('sage.misc.explain_pickle', 'TestBuild')
            si = unpickle_newobj(pg_TestBuild, ())
            unpickle_build(si, ({'x':3}, {'y':4}))
            si
            result: TestBuild: x=3; y=4

        ::

            sage: test_pickle(TestBuildSetstate(), verbose_eval=True)
                0: \x80 PROTO      2
                2: c    GLOBAL     'sage.misc.explain_pickle TestBuildSetstate'
               46: q    BINPUT     1
               48: )    EMPTY_TUPLE
               49: \x81 NEWOBJ
               50: q    BINPUT     2
               52: }    EMPTY_DICT
               53: q    BINPUT     3
               55: U    SHORT_BINSTRING 'x'
               58: K    BININT1    3
               60: s    SETITEM
               61: }    EMPTY_DICT
               62: q    BINPUT     4
               64: U    SHORT_BINSTRING 'y'
               67: K    BININT1    4
               69: s    SETITEM
               70: \x86 TUPLE2
               71: b    BUILD
               72: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from sage.misc.explain_pickle import TestBuildSetstate
            si = unpickle_newobj(TestBuildSetstate, ())
            si.__setstate__(({'x':3}, {'y':4}))
            si
            explain_pickle in_current_sage=False:
            pg_TestBuildSetstate = unpickle_global('sage.misc.explain_pickle', 'TestBuildSetstate')
            si = unpickle_newobj(pg_TestBuildSetstate, ())
            unpickle_build(si, ({'x':3}, {'y':4}))
            si
            evaluating explain_pickle in_current_sage=True:
            setting state from ({'x': 3}, {'y': 4})
            evaluating explain_pickle in_current_sage=False:
            setting state from ({'x': 3}, {'y': 4})
            loading pickle with cPickle:
            setting state from ({'x': 3}, {'y': 4})
            result: TestBuild: x=4; y=3
        """
        args = self.pop()
        obj = self.pop()
        use_setstate = False
        direct_set = False
        if self.default_assumptions:
            direct_set = True
        elif self.in_current_sage:
            if isinstance(obj, PickleObject) and isinstance(obj.value, PickleInstance):
                if hasattr(obj.value.klass, '__setstate__'):
                    use_setstate = True
                else:
                    direct_set = True

        can_handle_direct_set = False
        if direct_set:
            if isinstance(args, PickleObject):
                if isinstance(args.value, PickleDict):
                    can_handle_direct_set = True
                if isinstance(args.value, tuple) and isinstance(args.value[0], PickleObject) and isinstance(args.value[0].value, PickleDict) and isinstance(args.value[1], PickleObject) and isinstance(args.value[1].value, PickleDict):
                    can_handle_direct_set = True
            if not can_handle_direct_set:
                direct_set = False

        if use_setstate:
            self.sib.command(obj, self.sib.getattr(obj, '__setstate__')(args))
        elif direct_set:
            state = args.value
            slots = None
            if isinstance(state, tuple):
                slots = state[1].value
                state = state[0].value
            d = self.sib.getattr(obj, '__dict__')
            for k,v in state.items:
                self.sib.command(obj, self.sib.assign(d[k], v))
            if slots is not None:
                for k,v in slots.items:
                    if isinstance(k, PickleObject) and isinstance(k.value, str):
                        self.sib.command(obj, self.sib.assign(self.sib.getattr(obj, k.value), v))
                    else:
                        self.sib.command(obj, self.sib.name('setattr')(obj, k, v))
        else:
            self.sib.command(obj, self.sib.name('unpickle_build')(obj, args))

        self.push(obj)

    def DICT(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(DICT, args=('mark', 'a', 1, 2, 'b'))
                0: (    MARK
                1: P        PERSID     '1'
                4: P        PERSID     '2'
                7: P        PERSID     '3'
               10: P        PERSID     '4'
               13: d        DICT       (MARK at 0)
               14: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            {unpickle_persistent('1'):unpickle_persistent('2'), unpickle_persistent('3'):unpickle_persistent('4')}
            result: {'a': 1, 2: 'b'}
        """
        slice = self.pop_to_mark()
        self.EMPTY_DICT()
        self._SETITEMS_helper(slice)

    def DUP(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_LIST + DUP + TUPLE2 + STOP)
                0: ]    EMPTY_LIST
                1: 2    DUP
                2: \x86 TUPLE2
                3: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            si = []
            (si, si)
            result: ([], [])
        """
        v = self.pop()
        self.push(v)
        self.push(v)

    def EMPTY_DICT(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_DICT)
                0: }    EMPTY_DICT
                1: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            {}
            result: {}
        """
        self.push(PickleObject(PickleDict([]), self.sib({})))

    def EMPTY_LIST(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_LIST)
                0: ]    EMPTY_LIST
                1: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            []
            result: []
        """
        self.push(PickleObject([], self.sib([])))

    def EMPTY_TUPLE(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_TUPLE)
                0: )    EMPTY_TUPLE
                1: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            ()
            result: ()
        """
        self.push(PickleObject((), self.sib(())))

    def EXT1(self, n):
        r"""
        TESTS::

            sage: from copy_reg import *
            sage: from sage.misc.explain_pickle import *
            sage: add_extension('sage.misc.explain_pickle', 'EmptyNewstyleClass', 42)
            sage: test_pickle(EmptyNewstyleClass())
                0: \x80 PROTO      2
                2: \x82 EXT1       42
                4: )    EMPTY_TUPLE
                5: \x81 NEWOBJ
                6: q    BINPUT     1
                8: }    EMPTY_DICT
                9: q    BINPUT     2
               11: b    BUILD
               12: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            si = unpickle_newobj(unpickle_extension(42), ())
            unpickle_build(si, {})
            si
            result: EmptyNewstyleClass
            sage: remove_extension('sage.misc.explain_pickle', 'EmptyNewstyleClass', 42)
        """
        self.push(self.sib.name('unpickle_extension')(n))

    def EXT2(self, n):
        r"""
        TESTS::

            sage: from copy_reg import *
            sage: from sage.misc.explain_pickle import *
            sage: add_extension('sage.misc.explain_pickle', 'EmptyNewstyleClass', 31415)
            sage: test_pickle(EmptyNewstyleClass())
                0: \x80 PROTO      2
                2: \x83 EXT2       31415
                5: )    EMPTY_TUPLE
                6: \x81 NEWOBJ
                7: q    BINPUT     1
                9: }    EMPTY_DICT
               10: q    BINPUT     2
               12: b    BUILD
               13: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            si = unpickle_newobj(unpickle_extension(31415), ())
            unpickle_build(si, {})
            si
            result: EmptyNewstyleClass
            sage: remove_extension('sage.misc.explain_pickle', 'EmptyNewstyleClass', 31415)
        """
        self.push(self.sib.name('unpickle_extension')(n))

    def EXT4(self, n):
        r"""
        TESTS::

            sage: from copy_reg import *
            sage: from sage.misc.explain_pickle import *
            sage: add_extension('sage.misc.explain_pickle', 'EmptyNewstyleClass', 27182818)
            sage: test_pickle(EmptyNewstyleClass())
                0: \x80 PROTO      2
                2: \x84 EXT4       27182818
                7: )    EMPTY_TUPLE
                8: \x81 NEWOBJ
                9: q    BINPUT     1
               11: }    EMPTY_DICT
               12: q    BINPUT     2
               14: b    BUILD
               15: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            si = unpickle_newobj(unpickle_extension(27182818), ())
            unpickle_build(si, {})
            si
            result: EmptyNewstyleClass
            sage: remove_extension('sage.misc.explain_pickle', 'EmptyNewstyleClass', 27182818)
        """
        self.push(self.sib.name('unpickle_extension')(n))

    def FLOAT(self, f):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(FLOAT + '2.71828\n')
                0: F    FLOAT      2.71828
                9: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            2.71828
            result: 2.71828
        """
        self.push(self.sib(f))

    def GET(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_LIST + PUT + '1\n' + POP + GET + '1\n' + '.')
                0: ]    EMPTY_LIST
                1: p    PUT        1
                4: 0    POP
                5: g    GET        1
                8: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            []
            result: []
        """
        self.push(self.memo[n])

    def GLOBAL(self, name):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *

        We've used register_unpickle_override so that unpickle_global
        will map TestGlobalOldName to TestGlobalNewName.

        ::

            sage: test_pickle(TestGlobalOldName())
                0: \x80 PROTO      2
                2: c    GLOBAL     'sage.misc.explain_pickle TestGlobalOldName'
               46: q    BINPUT     1
               48: )    EMPTY_TUPLE
               49: \x81 NEWOBJ
               50: q    BINPUT     2
               52: }    EMPTY_DICT
               53: q    BINPUT     3
               55: b    BUILD
               56: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from sage.misc.explain_pickle import TestGlobalNewName
            unpickle_newobj(TestGlobalNewName, ())
            explain_pickle in_current_sage=False:
            pg_TestGlobalOldName = unpickle_global('sage.misc.explain_pickle', 'TestGlobalOldName')
            si = unpickle_newobj(pg_TestGlobalOldName, ())
            unpickle_build(si, {})
            si
            result: TestGlobalNewName

        Note that default_assumptions blithely assumes that it should
        use the old name, giving code that doesn't actually work as
        desired::

            sage: explain_pickle(dumps(TestGlobalOldName()), default_assumptions=True)
            from sage.misc.explain_pickle import TestGlobalOldName
            unpickle_newobj(TestGlobalOldName, ())

        A class name need not be a valid identifier::

            sage: sage.misc.explain_pickle.__dict__['funny$name'] = TestGlobalFunnyName # see comment at end of file
            sage: test_pickle((TestGlobalFunnyName(), TestGlobalFunnyName()))
                0: \x80 PROTO      2
                2: c    GLOBAL     'sage.misc.explain_pickle funny$name'
               39: q    BINPUT     1
               41: )    EMPTY_TUPLE
               42: \x81 NEWOBJ
               43: q    BINPUT     2
               45: }    EMPTY_DICT
               46: q    BINPUT     3
               48: b    BUILD
               49: h    BINGET     1
               51: )    EMPTY_TUPLE
               52: \x81 NEWOBJ
               53: q    BINPUT     4
               55: }    EMPTY_DICT
               56: q    BINPUT     5
               58: b    BUILD
               59: \x86 TUPLE2
               60: q    BINPUT     6
               62: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            si1 = unpickle_global('sage.misc.explain_pickle', 'funny$name')
            si2 = unpickle_newobj(si1, ())
            unpickle_build(si2, {})
            si3 = unpickle_newobj(si1, ())
            unpickle_build(si3, {})
            (si2, si3)
            result: (TestGlobalFunnyName, TestGlobalFunnyName)
        """
        module, func = name.split(' ')

        if self.default_assumptions:
            # Should the default assumption be that sage.all does, or
            # does not, have a conflicting variable name?
            # I'm going to go with "does not conflict".
            self.push(self.sib.import_name(module, func))
            return

        name_ok = name_is_valid(func)

        if self.in_current_sage and name_ok:
            override = unpickle_override.get((module, func))
            if override is None:
                __import__(module)
                f = getattr(sys.modules[module], func)
            else:
                f, new_mf = override
                if new_mf is not None:
                    module, func = new_mf
            if override is None or new_mf is not None:
                # OK, we know what module and function name will actually
                # be used, as well as the actual function.
                # Is this already available at the command line?
                cmdline_f = getattr(sage.all, func, None)
                if cmdline_f is f:
                    self.push(PickleObject(f, self.sib.name(func)))
                    return
                if cmdline_f is None:
                    # OK, we'll go ahead and import it under the original
                    # name.
                    self.push(PickleObject(f, self.sib.import_name(module, func)))
                    return
                # The original name is in use.
                self.push(PickleObject(f, self.sib.import_name(module, func, 'pg_' + func)))
                return

        # We don't know the full name of the function that will
        # actually be used (either we're being generic, or
        # unpickle_override only has the function, not its name).
        v = self.sib.name('unpickle_global')(module, func)
        if name_ok:
            self.sib.use_variable(v, 'pg_' + func)
        self.push(v)

    def INST(self, name):
        r"""
        TESTS::

            sage: import pickle
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(pickle.dumps(EmptyOldstyleClass(), protocol=0))
                0: (    MARK
                1: i        INST       'sage.misc.explain_pickle EmptyOldstyleClass' (MARK at 0)
               46: p    PUT        0
               49: (    MARK
               50: d        DICT       (MARK at 49)
               51: p    PUT        1
               54: b    BUILD
               55: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True:
            from new import instance
            from sage.misc.explain_pickle import EmptyOldstyleClass
            instance(EmptyOldstyleClass)
            explain_pickle in_current_sage=False:
            pg_EmptyOldstyleClass = unpickle_global('sage.misc.explain_pickle', 'EmptyOldstyleClass')
            pg = unpickle_instantiate(pg_EmptyOldstyleClass, ())
            unpickle_build(pg, {})
            pg
            result: EmptyOldstyleClass
        """
        self.TUPLE()
        v = self.pop()
        self.GLOBAL(name)
        self.push(v)
        self.REDUCE()

    def INT(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(INT + "-12345\n")
                0: I    INT        -12345
                8: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            -12345
            result: -12345

        INT can also be used to record True and False::

            sage: test_pickle(INT + "00\n")
                0: I    INT        False
                4: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            False
            result: False
            sage: test_pickle(INT + "01\n")
                0: I    INT        True
                4: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            True
            result: True
        """
        self.push_and_share(self.sib(n))

    def LIST(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(MARK + NONE + NEWFALSE + LIST)
                0: (    MARK
                1: N        NONE
                2: \x89     NEWFALSE
                3: l        LIST       (MARK at 0)
                4: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            [None, False]
            result: [None, False]
        """
        lst = self.pop_to_mark()
        self.push(PickleObject(lst, self.sib(lst)))

    def LONG(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(LONG + "12345678909876543210123456789L\n")
                0: L    LONG       12345678909876543210123456789L
               32: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            12345678909876543210123456789
            result: 12345678909876543210123456789L
        """
        self.push(self.sib(n))

    def LONG1(self, n):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(1L)
                0: \x80 PROTO      2
                2: \x8a LONG1      1L
                5: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            1L
            result: 1L
        """
        self.push(self.sib(n))

    def LONG4(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(LONG4 + '\014\0\0\0' + 'hello, world')
                0: \x8b LONG4      31079605376604435891501163880L
               17: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            31079605376604435891501163880
            result: 31079605376604435891501163880L
        """
        self.push(self.sib(n))

    def LONG_BINGET(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_LIST + LONG_BINPUT + 'Sage' + POP + LONG_BINGET + 'Sage')
                0: ]    EMPTY_LIST
                1: r    LONG_BINPUT 1701273939
                6: 0    POP
                7: j    LONG_BINGET 1701273939
               12: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            []
            result: []
        """
        self.push(self.memo[n])

    def LONG_BINPUT(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_LIST + LONG_BINPUT + 'Sage' + POP + LONG_BINGET + 'Sage')
                0: ]    EMPTY_LIST
                1: r    LONG_BINPUT 1701273939
                6: 0    POP
                7: j    LONG_BINGET 1701273939
               12: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            []
            result: []
        """
        v = self.pop()
        self.memo[n] = v
        self.push(v)

    def MARK(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(MARK + TUPLE)
                0: (    MARK
                1: t        TUPLE      (MARK at 0)
                2: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            ()
            result: ()
        """
        self.push_mark()

    def NEWFALSE(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(NEWFALSE)
                0: \x89 NEWFALSE
                1: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            False
            result: False
        """
        self.push(self.sib.name('False'))

    def NEWTRUE(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(NEWTRUE)
                0: \x88 NEWTRUE
                1: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            True
            result: True
        """
        self.push(self.sib.name('True'))

    def NEWOBJ(self):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EmptyNewstyleClass())
                0: \x80 PROTO      2
                2: c    GLOBAL     'sage.misc.explain_pickle EmptyNewstyleClass'
               47: q    BINPUT     1
               49: )    EMPTY_TUPLE
               50: \x81 NEWOBJ
               51: q    BINPUT     2
               53: }    EMPTY_DICT
               54: q    BINPUT     3
               56: b    BUILD
               57: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from sage.misc.explain_pickle import EmptyNewstyleClass
            unpickle_newobj(EmptyNewstyleClass, ())
            explain_pickle in_current_sage=False:
            pg_EmptyNewstyleClass = unpickle_global('sage.misc.explain_pickle', 'EmptyNewstyleClass')
            si = unpickle_newobj(pg_EmptyNewstyleClass, ())
            unpickle_build(si, {})
            si
            result: EmptyNewstyleClass
        """
        args = self.pop()
        klass = self.pop()
        obj = self.sib.name('unpickle_newobj')(klass, args)
        if isinstance(klass, PickleObject):
            self.push(PickleObject(PickleInstance(klass.value), obj))
        else:
            self.push(obj)

    def NONE(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(NONE)
                0: N    NONE
                1: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            None
            result: None
        """
        self.push(PickleObject(None, self.sib.name('None')))

    def OBJ(self):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EmptyOldstyleClass())
                0: \x80 PROTO      2
                2: (    MARK
                3: c        GLOBAL     'sage.misc.explain_pickle EmptyOldstyleClass'
               48: q        BINPUT     1
               50: o        OBJ        (MARK at 2)
               51: q    BINPUT     2
               53: }    EMPTY_DICT
               54: q    BINPUT     3
               56: b    BUILD
               57: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from new import instance
            from sage.misc.explain_pickle import EmptyOldstyleClass
            instance(EmptyOldstyleClass)
            explain_pickle in_current_sage=False:
            pg_EmptyOldstyleClass = unpickle_global('sage.misc.explain_pickle', 'EmptyOldstyleClass')
            pg = unpickle_instantiate(pg_EmptyOldstyleClass, ())
            unpickle_build(pg, {})
            pg
            result: EmptyOldstyleClass
        """
        klass_args = self.pop_to_mark()
        klass = klass_args[0]
        args = klass_args[1:]
        self.push(klass)
        self.push(PickleObject(tuple(args), self.sib(tuple(args))))
        self.REDUCE()

    def PERSID(self, id):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(PERSID + "0\n" + '.', args=('Yo!',))
                0: P    PERSID     '0'
                3: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            unpickle_persistent('0')
            result: 'Yo!'
        """
        self.push(self.sib.name('unpickle_persistent')(id))

    def BINPERSID(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(INT + "0\n" + BINPERSID + '.', args=('Yo!',))
                0: I    INT        0
                3: Q    BINPERSID
                4: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            unpickle_persistent(0)
            result: 'Yo!'
        """
        id = self.pop()
        self.push(self.sib.name('unpickle_persistent')(id))

    def POP(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(INT + "0\n" + POP + INT + "42\n")
                0: I    INT        0
                3: 0    POP
                4: I    INT        42
                8: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            42
            result: 42
        """
        v = self.stack.pop()
        if v is not the_mark:
            self.check_value(v)

    def POP_MARK(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(MARK + NONE + NEWFALSE + POP_MARK + NEWTRUE)
                0: (    MARK
                1: N        NONE
                2: \x89     NEWFALSE
                3: 1        POP_MARK   (MARK at 0)
                4: \x88 NEWTRUE
                5: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            True
            result: True
        """
        self.pop_to_mark()

    def PROTO(self, proto):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(0r)
                0: \x80 PROTO      2
                2: K    BININT1    0
                4: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            0
            result: 0
        """
        if not 0 <= proto <= 2:
            raise ValueError, "unsupported pickle protocol: %d" % proto

    def PUT(self, n):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_LIST + PUT + '1\n' + POP + GET + '1\n' + '.')
                0: ]    EMPTY_LIST
                1: p    PUT        1
                4: 0    POP
                5: g    GET        1
                8: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            []
            result: []
        """
        v = self.pop()
        self.memo[n] = v
        self.push(v)

    def REDUCE(self):
        r"""
        TESTS::

            sage: import pickle
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(pickle.dumps(EmptyNewstyleClass(), protocol=1))
                0: c    GLOBAL     'copy_reg _reconstructor'
               25: q    BINPUT     0
               27: (    MARK
               28: c        GLOBAL     'sage.misc.explain_pickle EmptyNewstyleClass'
               73: q        BINPUT     1
               75: c        GLOBAL     '__builtin__ object'
               95: q        BINPUT     2
               97: N        NONE
               98: t        TUPLE      (MARK at 27)
               99: q    BINPUT     3
              101: R    REDUCE
              102: q    BINPUT     4
              104: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True:
            from copy_reg import _reconstructor
            from sage.misc.explain_pickle import EmptyNewstyleClass
            from __builtin__ import object
            _reconstructor(EmptyNewstyleClass, object, None)
            explain_pickle in_current_sage=False:
            pg__reconstructor = unpickle_global('copy_reg', '_reconstructor')
            pg_EmptyNewstyleClass = unpickle_global('sage.misc.explain_pickle', 'EmptyNewstyleClass')
            pg_object = unpickle_global('__builtin__', 'object')
            pg__reconstructor(pg_EmptyNewstyleClass, pg_object, None)
            result: EmptyNewstyleClass

        ::

            sage: test_pickle(TestReduceGetinitargs(), verbose_eval=True)
            Running __init__ for TestReduceGetinitargs
                0: \x80 PROTO      2
                2: (    MARK
                3: c        GLOBAL     'sage.misc.explain_pickle TestReduceGetinitargs'
               51: q        BINPUT     1
               53: o        OBJ        (MARK at 2)
               54: q    BINPUT     2
               56: }    EMPTY_DICT
               57: q    BINPUT     3
               59: b    BUILD
               60: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from sage.misc.explain_pickle import TestReduceGetinitargs
            TestReduceGetinitargs()
            explain_pickle in_current_sage=False:
            pg_TestReduceGetinitargs = unpickle_global('sage.misc.explain_pickle', 'TestReduceGetinitargs')
            pg = unpickle_instantiate(pg_TestReduceGetinitargs, ())
            unpickle_build(pg, {})
            pg
            evaluating explain_pickle in_current_sage=True:
            Running __init__ for TestReduceGetinitargs
            evaluating explain_pickle in_current_sage=False:
            Running __init__ for TestReduceGetinitargs
            loading pickle with cPickle:
            Running __init__ for TestReduceGetinitargs
            result: TestReduceGetinitargs

        ::

            sage: test_pickle(TestReduceNoGetinitargs(), verbose_eval=True)
            Running __init__ for TestReduceNoGetinitargs
                0: \x80 PROTO      2
                2: (    MARK
                3: c        GLOBAL     'sage.misc.explain_pickle TestReduceNoGetinitargs'
               53: q        BINPUT     1
               55: o        OBJ        (MARK at 2)
               56: q    BINPUT     2
               58: }    EMPTY_DICT
               59: q    BINPUT     3
               61: b    BUILD
               62: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            from new import instance
            from sage.misc.explain_pickle import TestReduceNoGetinitargs
            instance(TestReduceNoGetinitargs)
            explain_pickle in_current_sage=False:
            pg_TestReduceNoGetinitargs = unpickle_global('sage.misc.explain_pickle', 'TestReduceNoGetinitargs')
            pg = unpickle_instantiate(pg_TestReduceNoGetinitargs, ())
            unpickle_build(pg, {})
            pg
            evaluating explain_pickle in_current_sage=True:
            evaluating explain_pickle in_current_sage=False:
            loading pickle with cPickle:
            result: TestReduceNoGetinitargs
        """

        # Reading cPickle.c (in the Instance_New function),
        # I think that REDUCE is equivalent to a function call unless
        # all three of the following conditions are met:
        #   obj is an old-style class
        #   obj defines __getinitargs__
        #   args is an empty tuple
        # in which case it is equivalent to PyInstance_NewRaw(obj)
        args = self.pop()
        obj = self.pop()
        simple_call = False
        new_inst = False
        if isinstance(args, PickleObject) and isinstance(args.value, tuple) \
                and len(args.value) > 0:
            simple_call = True
        if self.default_assumptions:
            simple_call = True
        if self.in_current_sage:
            if isinstance(obj, PickleObject):
                if isinstance(obj.value, type):
                    simple_call = True
                elif isinstance(obj.value, types.ClassType):
                    if hasattr(obj.value, '__getinitargs__'):
                        simple_call = True
                    else:
                        new_inst = True

        if simple_call:
            v = self.sib(obj)(*args.value)
        elif new_inst:
            v = self.new_instance(obj)
        else:
            v = self.sib.name('unpickle_instantiate')(obj, args)
            self.sib.use_variable(v, 'pg')
        if isinstance(obj, PickleObject):
            self.push(PickleObject(PickleInstance(obj.value), v))
        else:
            self.push(v)

    def SETITEM(self):
        r"""
        TESTS::

            sage: import pickle
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(pickle.dumps({'a': 'b'}))
                0: (    MARK
                1: d        DICT       (MARK at 0)
                2: p    PUT        0
                5: S    STRING     'a'
               10: p    PUT        1
               13: S    STRING     'b'
               18: p    PUT        2
               21: s    SETITEM
               22: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            {'a':'b'}
            result: {'a': 'b'}

        We see above that we output the result as a dictionary literal, when
        possible.  This is impossible when a key or value is recursive.  First
        we test recursive values::

            sage: value_rec = dict()
            sage: value_rec['circular'] = value_rec
            sage: test_pickle(pickle.dumps(value_rec))
                0: (    MARK
                1: d        DICT       (MARK at 0)
                2: p    PUT        0
                5: S    STRING     'circular'
               17: p    PUT        1
               20: g    GET        0
               23: s    SETITEM
               24: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            si = {}
            si['circular'] = si
            si
            result: {'circular': {...}}

        Then we test recursive keys::

            sage: key_rec = dict()
            sage: key = EmptyNewstyleClass()
            sage: key.circular = key_rec
            sage: key_rec[key] = 'circular'
            sage: test_pickle(pickle.dumps(key_rec))
                0: (    MARK
                1: d        DICT       (MARK at 0)
                2: p    PUT        0
                5: c    GLOBAL     'copy_reg _reconstructor'
               30: p    PUT        1
               33: (    MARK
               34: c        GLOBAL     'sage.misc.explain_pickle EmptyNewstyleClass'
               79: p        PUT        2
               82: c        GLOBAL     '__builtin__ object'
              102: p        PUT        3
              105: N        NONE
              106: t        TUPLE      (MARK at 33)
              107: p    PUT        4
              110: R    REDUCE
              111: p    PUT        5
              114: (    MARK
              115: d        DICT       (MARK at 114)
              116: p    PUT        6
              119: S    STRING     'circular'
              131: p    PUT        7
              134: g    GET        0
              137: s    SETITEM
              138: b    BUILD
              139: g    GET        7
              142: s    SETITEM
              143: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True:
            si1 = {}
            from copy_reg import _reconstructor
            from sage.misc.explain_pickle import EmptyNewstyleClass
            from __builtin__ import object
            si2 = _reconstructor(EmptyNewstyleClass, object, None)
            si2.__dict__['circular'] = si1
            si1[si2] = 'circular'
            si1
            explain_pickle in_current_sage=False:
            si1 = {}
            pg__reconstructor = unpickle_global('copy_reg', '_reconstructor')
            pg_EmptyNewstyleClass = unpickle_global('sage.misc.explain_pickle', 'EmptyNewstyleClass')
            pg_object = unpickle_global('__builtin__', 'object')
            si2 = pg__reconstructor(pg_EmptyNewstyleClass, pg_object, None)
            unpickle_build(si2, {'circular':si1})
            si1[si2] = 'circular'
            si1
            result: {EmptyNewstyleClass: 'circular'}
        """
        v = self.pop()
        k = self.pop()
        self._SETITEMS_helper([k, v])

    def SETITEMS(self):
        r"""
        TESTS::

            sage: import pickle
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(pickle.dumps({'a': 'b', 1r : 2r}, protocol=2))
                0: \x80 PROTO      2
                2: }    EMPTY_DICT
                3: q    BINPUT     0
                5: (    MARK
                6: U        SHORT_BINSTRING 'a'
                9: q        BINPUT     1
               11: U        SHORT_BINSTRING 'b'
               14: q        BINPUT     2
               16: K        BININT1    1
               18: K        BININT1    2
               20: u        SETITEMS   (MARK at 5)
               21: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            {'a':'b', 1:2}
            result: {'a': 'b', 1: 2}

        Similar to the tests for SETITEM, we test recursive keys and values::

            sage: recdict = {}
            sage: recdict['Circular value'] = recdict
            sage: key = EmptyOldstyleClass()
            sage: key.recdict = recdict
            sage: recdict[key] = 'circular_key'
            sage: test_pickle(pickle.dumps(recdict, protocol=2))
                0: \x80 PROTO      2
                2: }    EMPTY_DICT
                3: q    BINPUT     0
                5: (    MARK
                6: (        MARK
                7: c            GLOBAL     'sage.misc.explain_pickle EmptyOldstyleClass'
               52: q            BINPUT     1
               54: o            OBJ        (MARK at 6)
               55: q        BINPUT     2
               57: }        EMPTY_DICT
               58: q        BINPUT     3
               60: U        SHORT_BINSTRING 'recdict'
               69: q        BINPUT     4
               71: h        BINGET     0
               73: s        SETITEM
               74: b        BUILD
               75: U        SHORT_BINSTRING 'circular_key'
               89: q        BINPUT     5
               91: U        SHORT_BINSTRING 'Circular value'
              107: q        BINPUT     6
              109: h        BINGET     0
              111: u        SETITEMS   (MARK at 5)
              112: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True:
            si1 = {}
            from new import instance
            from sage.misc.explain_pickle import EmptyOldstyleClass
            si2 = instance(EmptyOldstyleClass)
            si2.__dict__['recdict'] = si1
            si1[si2] = 'circular_key'
            si1['Circular value'] = si1
            si1
            explain_pickle in_current_sage=False:
            si = {}
            pg_EmptyOldstyleClass = unpickle_global('sage.misc.explain_pickle', 'EmptyOldstyleClass')
            pg = unpickle_instantiate(pg_EmptyOldstyleClass, ())
            unpickle_build(pg, {'recdict':si})
            si[pg] = 'circular_key'
            si['Circular value'] = si
            si
            result: {EmptyOldstyleClass: 'circular_key', 'Circular value': {...}}
        """
        slice = self.pop_to_mark()
        self._SETITEMS_helper(slice)

    def _SETITEMS_helper(self, slice):
        r"""
        TESTS::

            sage: import pickle
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(pickle.dumps({'a': 'b'})) # indirect doctest
                0: (    MARK
                1: d        DICT       (MARK at 0)
                2: p    PUT        0
                5: S    STRING     'a'
               10: p    PUT        1
               13: S    STRING     'b'
               18: p    PUT        2
               21: s    SETITEM
               22: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            {'a':'b'}
            result: {'a': 'b'}
        """
        updates = []
        i = 0
        while i < len(slice):
            k = slice[i]
            v = slice[i+1]
            # This marks d as immutable, if k or v happens to include d.
            self.sib(k)
            self.sib(v)
            updates.append((k, v))
            i += 2
        d = self.pop()
        if self.is_mutable_pickle_object(d) and isinstance(d.value, PickleDict):
            d.value = PickleDict(d.value.items + updates)
            d.expression = self.sib.dict(d.value.items)
        else:
            d = self.sib(d)
            for k, v in updates:
                self.sib.command(d, self.sib.assign(d[k], v))
        self.push(d)

    def SHORT_BINSTRING(self, s):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(dumps('hello', compress=False))
                0: \x80 PROTO      2
                2: U    SHORT_BINSTRING 'hello'
                9: q    BINPUT     1
               11: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            'hello'
            result: 'hello'
        """
        self.push(PickleObject(s, self.share(self.sib(s))))

    def STOP(self):
        r"""
        TESTS::

            sage: from pickle import *
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(EMPTY_TUPLE)
                0: )    EMPTY_TUPLE
                1: .    STOP
            highest protocol among opcodes = 1
            explain_pickle in_current_sage=True/False:
            ()
            result: ()
        """
        self.stopped = True

    def STRING(self, s):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle("S'Testing...'\n.")
                0: S    STRING     'Testing...'
               14: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            'Testing...'
            result: 'Testing...'
        """
        self.push(PickleObject(s, self.share(self.sib(s))))

    def TUPLE(self):
        r"""
        TESTS::

            sage: import pickle
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(pickle.dumps(('a',)))
                0: (    MARK
                1: S        STRING     'a'
                6: p        PUT        0
                9: t        TUPLE      (MARK at 0)
               10: p    PUT        1
               13: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            ('a',)
            result: ('a',)

        We prefer to produce tuple literals, as above; but if the tuple
        is recursive, we need a more complicated construction.  Note
        that the cPickle unpickler can't handle this case, so we're
        not bug-for-bug identical to cPickle here (see
        http://bugs.python.org/issue5794)::

            sage: v = ([],)
            sage: v[0].append(v)
            sage: test_pickle(pickle.dumps(v))
                0: (    MARK
                1: (        MARK
                2: l            LIST       (MARK at 1)
                3: p        PUT        0
                6: (        MARK
                7: g            GET        0
               10: t            TUPLE      (MARK at 6)
               11: p        PUT        1
               14: a        APPEND
               15: 0        POP
               16: 0        POP        (MARK at 0)
               17: g    GET        1
               20: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            si1 = []
            si2 = (si1,)
            list.append(si1, si2)
            si2
            result: ([(...)],) (cPickle raised an exception!)
        """
        v = self.pop_to_mark()
        self.push(PickleObject(tuple(v), self.sib(tuple(v))))

    def TUPLE1(self):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(('a',))
                0: \x80 PROTO      2
                2: U    SHORT_BINSTRING 'a'
                5: \x85 TUPLE1
                6: q    BINPUT     1
                8: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            ('a',)
            result: ('a',)
        """
        v1 = self.pop()
        self.push(PickleObject((v1,), self.sib((v1,))))

    def TUPLE2(self):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(('a','b'))
                0: \x80 PROTO      2
                2: U    SHORT_BINSTRING 'a'
                5: U    SHORT_BINSTRING 'b'
                8: \x86 TUPLE2
                9: q    BINPUT     1
               11: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            ('a', 'b')
            result: ('a', 'b')
        """
        v2 = self.pop()
        v1 = self.pop()
        self.push(PickleObject((v1, v2), self.sib((v1, v2))))

    def TUPLE3(self):
        r"""
        TESTS::

            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(('a','b','c'))
                0: \x80 PROTO      2
                2: U    SHORT_BINSTRING 'a'
                5: U    SHORT_BINSTRING 'b'
                8: U    SHORT_BINSTRING 'c'
               11: \x87 TUPLE3
               12: q    BINPUT     1
               14: .    STOP
            highest protocol among opcodes = 2
            explain_pickle in_current_sage=True/False:
            ('a', 'b', 'c')
            result: ('a', 'b', 'c')
        """
        v3 = self.pop()
        v2 = self.pop()
        v1 = self.pop()
        self.push(PickleObject((v1, v2, v3), self.sib((v1, v2, v3))))

    def UNICODE(self, s):
        r"""
        TESTS::

            sage: import pickle
            sage: from sage.misc.explain_pickle import *
            sage: test_pickle(pickle.dumps(u'hi\u1234\U00012345'))
                0: V    UNICODE    u'hi\u1234\U00012345'
               20: p    PUT        0
               23: .    STOP
            highest protocol among opcodes = 0
            explain_pickle in_current_sage=True/False:
            u'hi\u1234\U00012345'
            result: u'hi\u1234\U00012345'
        """
        self.push_and_share(self.sib(s))

# def explain_picklejar(dir, catch_exceptions=True):
#     r"""
#     Given a directory or a .tar.bz2 of pickles, we unpickle each of
#     them three times: once with cPickle, once with explain_pickle
#     with in_current_sage=True, and once with explain_pickle
#     with in_current_sage=False.

#     We verify that each of these gives the same answer (where we check
#     using repr(a)==repr(b), in case equality is not defined on all
#     of these objects).

#     INPUT::

#         dir -- string; a directory or name of a .tar.bz2 file that
#                decompresses to give a directory full of pickles.
#         catch_exceptions -- boolean; default True: if True, then
#                unpickling exceptions will be caught (and if all three
#                unpicklers raise an exception, then that will be counted
#                as a match).  If False, then exceptions will not be caught,
#                and will terminate this function.

#     EXAMPLES:
#         sage: std = os.environ['SAGE_DATA'] + '/extcode/pickle_jar/pickle_jar.tar.bz2'
#         sage: from sage.misc.explain_pickle import *
#         sage: explain_picklejar(std) # long time (~45s on my computer)
#         doctest:...: DeprecationWarning: Your data is stored in an old format. Please use the save() function to store your data in a more recent format.
#         doctest:...: DeprecationWarning: Your data is stored in an old format. Please use the save() function to store your data in a more recent format.
#         doctest:...: DeprecationWarning: RQDF is deprecated; use RealField(212) instead.
#         doctest:...: DeprecationWarning: RQDF is deprecated; use RealField(212) instead.
#         doctest:...: DeprecationWarning: RQDF is deprecated; use RealField(212) instead.
#         4... matches; 0 mismatches
#     """
#     # Largely copied from unpickle_all in sage_object.pyx

#     from sage.structure.sage_object import load

#     obj_at = re.compile('object at 0x[0-9a-f]+')

#     n_success = 0
#     failed = []
#     if dir.endswith('.tar.bz2'):
#         # create a temporary directory
#         from sage.misc.all import tmp_dir
#         T = tmp_dir()
#         # extract tarball to it
#         os.system('cd "%s"; bunzip2 -c "%s" | tar fx - '%(T, os.path.abspath(dir)))
#         # Now use the directory in the tarball instead of dir
#         dir = T + "/" + os.listdir(T)[0]

#     for A in os.listdir(dir):
#         if A.endswith('.sobj'):
#             fn = dir + '/' + A
#             try:
#                 v1 = load(fn)
#                 v1r = repr(v1)
#             except Exception, msg:
#                 # if not catch_exceptions: raise
#                 v1r = 'error'

#             try:
#                 exp_current = explain_pickle(file=fn, in_current_sage=True)
#                 import sys
#                 sys.stderr.write(exp_current)
#                 v2 = sage_eval(exp_current)
#                 v2r = repr(v2)
#             except Exception, msg:
#                 if not catch_exceptions: raise
#                 v2r = 'error'

#             try:
#                 exp_generic = explain_pickle(file=fn)
#                 import sys
#                 sys.stderr.write(exp_generic)
#                 v3 = sage_eval(exp_generic)
#                 v3r = repr(v3)
#             except Exception, msg:
#                 if not catch_exceptions: raise
#                 v3r = 'error'

#             v1r = obj_at.sub('object at 0x...', v1r)
#             v2r = obj_at.sub('object at 0x...', v2r)
#             v3r = obj_at.sub('object at 0x...', v3r)

#             if v1r == v2r == v3r:
#                 n_success += 1
#             else:
#                 print "Mismatch on %s" % fn
#                 print v1r, v2r, v3r
#                 failed.append(A)

#     print "%d matches; %d mismatches" % (n_success, len(failed))
#     print '\n'.join(failed)

# Helper routines for explain_pickle

def unpickle_newobj(klass, args):
    r"""
    Create a new object; this corresponds to the C code
    klass->tp_new(klass, args, NULL).  Used by ``explain_pickle``.

    EXAMPLES:
        sage: unpickle_newobj(tuple, ([1, 2, 3],))
        (1, 2, 3)
    """
    # We need to call klass->tp_new(klass, args, NULL).
    # This is almost but not quite the same as klass.__new__(klass, *args).
    # (I don't know exactly what the difference is, but when you try
    # to unpickle a Sequence, cPickle -- which uses the former -- works,
    # and pickle.py -- which uses the latter -- fails, with
    # TypeError: sage.structure.sage_object.SageObject.__new__(Sequence) is not safe, use list.__new__()
    # )

    # It seems unlikely that you can implement this from pure-Python code --
    # somewhat disturbingly, it actually is possible.  This shows how.
    # (Using Cython would also work, of course; but this is cooler, and
    # probably simpler.)

    # This pickle is: load persistent object 0, load persistent object 1,
    # NEWOBJ, STOP.
    pickle = "P0\nP1\n\x81."

    pers = [klass, args]

    pers_load = lambda id: pers[int(id)]

    from cStringIO import StringIO
    import cPickle
    unp = cPickle.Unpickler(StringIO(pickle))
    unp.persistent_load = pers_load
    return unp.load()

def unpickle_build(obj, state):
    r"""
    Set the state of an object.  Used by ``explain_pickle``.

    EXAMPLES::

        sage: from sage.misc.explain_pickle import *
        sage: v = EmptyNewstyleClass()
        sage: unpickle_build(v, {'hello': 42})
        sage: v.hello
        42
    """
    setstate = getattr(obj, '__setstate__', None)
    if setstate is not None:
        setstate(state)
        return

    if isinstance(state, tuple) and len(state) == 2:
        state, slots = state
    else:
        slots = None

    if state is not None:
        assert(isinstance(state, dict))
        d = obj.__dict__
        for k,v in state.iteritems():
            d[k] = v

    if slots is not None:
        assert(isinstance(slots, dict))
        for k,v in slots.iteritems():
            setattr(obj, k, v)

def unpickle_instantiate(fn, args):
    r"""
    Instantiate a new object of class fn with arguments args.  Almost always
    equivalent to ``fn(*args)``.  Used by ``explain_pickle``.

    EXAMPLES::

        sage: unpickle_instantiate(Integer, ('42',))
        42
    """
    if isinstance(fn, types.ClassType) and len(args) == 0 and not hasattr(fn, '__getinitargs__'):
        return new.instance(fn)

    return fn(*args)

unpickle_persistent_loader = None

def unpickle_persistent(s):
    r"""
    Takes an integer index and returns the persistent object with that
    index; works by calling whatever callable is stored in
    unpickle_persistent_loader.  Used by ``explain_pickle``.

    EXAMPLES::

        sage: import sage.misc.explain_pickle
        sage: sage.misc.explain_pickle.unpickle_persistent_loader = lambda n: n+7
        sage: unpickle_persistent(35)
        42
    """
    return unpickle_persistent_loader(s)

def unpickle_extension(code):
    r"""
    Takes an integer index and returns the extension object with that
    index.  Used by ``explain_pickle``.

    EXAMPLES::

        sage: from copy_reg import *
        sage: add_extension('sage.misc.explain_pickle', 'EmptyNewstyleClass', 42)
        sage: unpickle_extension(42)
        <class 'sage.misc.explain_pickle.EmptyNewstyleClass'>
        sage: remove_extension('sage.misc.explain_pickle', 'EmptyNewstyleClass', 42)
    """
    from copy_reg import _inverted_registry, _extension_cache
    # copied from .get_extension() in pickle.py
    nil = []
    obj = _extension_cache.get(code, nil)
    if obj is not nil:
        return obj
    key = _inverted_registry.get(code)
    if not key:
        raise ValueError("unregistered extension code %d" % code)
    obj = unpickle_global(*key)
    _extension_cache[code] = obj
    return obj

def unpickle_appends(lst, vals):
    r"""
    Given a list (or list-like object) and a sequence of values, appends the
    values to the end of the list.  This is careful to do so using the
    exact same technique that cPickle would use.  Used by ``explain_pickle``.

    EXAMPLES::

        sage: v = []
        sage: unpickle_appends(v, (1, 2, 3))
        sage: v
        [1, 2, 3]
    """
    if isinstance(lst, list):
        # If lst is a list (or a subtype of list)
        list.extend(lst, vals)
    else:
        append = lst.append
        for v in vals:
            append(v)

def test_pickle(p, verbose_eval=False, pedantic=False, args=()):
    r"""
    Tests explain_pickle on a given pickle p.  p can be:

    - a string containing an uncompressed pickle (which will always end
      with a '.')

    - a string containing a pickle fragment (not ending with '.')
      test_pickle will synthesize a pickle that will push args onto
      the stack (using persistent IDs), run the pickle fragment, and then
      STOP (if the string 'mark' occurs in args, then a mark will be pushed)

    - an arbitrary object; test_pickle will pickle the object

    Once it has a pickle, test_pickle will print the pickle's
    disassembly, run explain_pickle with in_current_sage=True and
    False, print the results, evaluate the results, unpickle the
    object with cPickle, and compare all three results.

    If verbose_eval is True, then test_pickle will print messages
    before evaluating the pickles; this is to allow for tests where
    the unpickling prints messages (to verify that the same operations
    occur in all cases).

    EXAMPLES::

        sage: from sage.misc.explain_pickle import *
        sage: test_pickle(['a'])
            0: \x80 PROTO      2
            2: ]    EMPTY_LIST
            3: q    BINPUT     1
            5: U    SHORT_BINSTRING 'a'
            8: a    APPEND
            9: .    STOP
        highest protocol among opcodes = 2
        explain_pickle in_current_sage=True/False:
        ['a']
        result: ['a']
    """
    start = ''
    for n in range(len(args)):
        a = args[n]
        if a == 'mark':
            start += '('
        else:
            start += "P%d\n" % n

    if isinstance(p, str):
        if p[-1] != '.':
            p = start + p + '.'
    else:
        p = dumps(p, compress=False)

    pickletools.dis(p)

    current = explain_pickle(p, compress=False, in_current_sage=True, pedantic=pedantic, preparse=False)
    generic = explain_pickle(p, compress=False, pedantic=pedantic, preparse=False)

    if current == generic:
        print "explain_pickle in_current_sage=True/False:"
        print current
    else:
        print "explain_pickle in_current_sage=True:"
        print current
        print "explain_pickle in_current_sage=False:"
        print generic

    pers_load = lambda s: args[int(s)]

    global unpickle_persistent_loader
    unpickle_persistent_loader = pers_load

    if verbose_eval: print "evaluating explain_pickle in_current_sage=True:"
    current_res = sage_eval(current, preparse=False)
    if verbose_eval: print "evaluating explain_pickle in_current_sage=False:"
    generic_res = sage_eval(generic, preparse=False)
    if verbose_eval: print "loading pickle with cPickle:"
    from cStringIO import StringIO
    import cPickle
    unp = cPickle.Unpickler(StringIO(p))
    unp.persistent_load = pers_load
    unp.find_global = unpickle_global
    try:
        cpickle_res = unp.load()
        cpickle_ok = True
    except:
        cpickle_ok = False

    current_repr = repr(current_res)
    generic_repr = repr(generic_res)

    if cpickle_ok:
        cpickle_repr = repr(cpickle_res)

        assert(current_repr == generic_repr == cpickle_repr)

        print "result: " + current_repr
    else:
        assert(current_repr == generic_repr)
        print "result: " + current_repr + " (cPickle raised an exception!)"

class EmptyOldstyleClass:
    r"""
    A featureless old-style class (does not inherit from object); used for
    testing explain_pickle.
    """
    def __repr__(self):
        r"""
        Print an EmptyOldstyleClass.

        EXAMPLES:
            sage: from sage.misc.explain_pickle import *
            sage: v = EmptyOldstyleClass()
            sage: v
            EmptyOldstyleClass
            sage: repr(v)
            'EmptyOldstyleClass'
            sage: v.__repr__()
            'EmptyOldstyleClass'
        """
        return "EmptyOldstyleClass"

    def __hash__(self):
        r"""
        Produce a predictable hash value for EmptyOldstyleClass.

        EXAMPLES:
            sage: from sage.misc.explain_pickle import *
            sage: v = EmptyOldstyleClass()
            sage: hash(v)
            0
            sage: v.__hash__()
            0
        """
        return 0

class EmptyNewstyleClass(object):
    r"""
    A featureless new-style class (inherits from object); used for
    testing explain_pickle.
    """
    def __repr__(self):
        r"""
        Print an EmptyNewstyleClass.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = EmptyNewstyleClass()
            sage: v
            EmptyNewstyleClass
            sage: repr(v)
            'EmptyNewstyleClass'
            sage: v.__repr__()
            'EmptyNewstyleClass'
        """
        return "EmptyNewstyleClass"

class TestReduceGetinitargs:
    r"""
    An old-style class with a __getinitargs__ method.  Used for testing
    explain_pickle.
    """
    def __init__(self):
        r"""
        Initialize a TestReduceGetinitargs object.  Note that the
        constructor prints out a message.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: TestReduceGetinitargs()
            Running __init__ for TestReduceGetinitargs
            TestReduceGetinitargs
        """
        print "Running __init__ for TestReduceGetinitargs"

    def __getinitargs__(self):
        r"""
        A simple __getinitargs__ method, used for testing explain_pickle.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestReduceGetinitargs()
            Running __init__ for TestReduceGetinitargs
            sage: v.__getinitargs__()
            ()
        """
        return ()

    def __repr__(self):
        r"""
        Print a TestReduceGetinitargs.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestReduceGetinitargs()
            Running __init__ for TestReduceGetinitargs
            sage: v
            TestReduceGetinitargs
            sage: repr(v)
            'TestReduceGetinitargs'
            sage: v.__repr__()
            'TestReduceGetinitargs'
        """
        return "TestReduceGetinitargs"

class TestReduceNoGetinitargs:
    r"""
    An old-style class with no __getinitargs__ method.  Used for testing
    explain_pickle.
    """
    def __init__(self):
        r"""
        Initialize a TestReduceNoGetinitargs object.  Note that the
        constructor prints out a message.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: TestReduceNoGetinitargs()
            Running __init__ for TestReduceNoGetinitargs
            TestReduceNoGetinitargs
        """
        print "Running __init__ for TestReduceNoGetinitargs"

    def __repr__(self):
        r"""
        Print a TestReduceNoGetinitargs.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestReduceNoGetinitargs()
            Running __init__ for TestReduceNoGetinitargs
            sage: v
            TestReduceNoGetinitargs
            sage: repr(v)
            'TestReduceNoGetinitargs'
            sage: v.__repr__()
            'TestReduceNoGetinitargs'
        """
        return "TestReduceNoGetinitargs"

class TestAppendList(list):
    r"""
    A subclass of list, with deliberately-broken append and extend methods.
    Used for testing explain_pickle.
    """
    def append(self):
        r"""
        A deliberately broken append method.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestAppendList()
            sage: v.append(7)
            Traceback (most recent call last):
            ...
            TypeError: append() takes exactly 1 argument (2 given)

        We can still append by directly using the list method:
            sage: list.append(v, 7)
            sage: v
            [7]
        """
        raise NotImplementedError

    def extend(self):
        r"""
        A deliberately broken extend method.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestAppendList()
            sage: v.extend([3,1,4,1,5,9])
            Traceback (most recent call last):
            ...
            TypeError: extend() takes exactly 1 argument (2 given)

        We can still extend by directly using the list method:
            sage: list.extend(v, (3,1,4,1,5,9))
            sage: v
            [3, 1, 4, 1, 5, 9]
        """
        raise NotImplementedError

class TestAppendNonlist(object):
    r"""
    A list-like class, carefully designed to test exact unpickling
    behavior.  Used for testing explain_pickle.
    """
    def __init__(self):
        r"""
        Construct a TestAppendNonlist.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestAppendNonlist()
            sage: v
            []
        """
        self.list = []

    def __getattr__(self, a):
        r"""
        Get an 'append' method from a TestAppendNonlist.  We have this
        method so that we can distinguish how many times the append method
        is fetched.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestAppendNonlist()
            sage: v.append(1)
            Fetching append attribute
            sage: v.append(2)
            Fetching append attribute
            sage: app = v.append
            Fetching append attribute
            sage: app(3)
            sage: app(4)
            sage: v
            [1, 2, 3, 4]
        """
        if a == 'append':
            print "Fetching append attribute"
            return self.list.append

        raise AttributeError

    def __reduce__(self):
        r"""
        Implement __reduce__ for TestAppendNonlist.  Note that the
        loads(dumps(...)) test only fetches the append method once.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestAppendNonlist()
            sage: v.list = [1,2,3,4]
            sage: v.__reduce__()
            (<class 'sage.misc.explain_pickle.TestAppendNonlist'>, (), None, <listiterator object at 0x...>)
            sage: list(v.__reduce__()[3])
            [1, 2, 3, 4]
            sage: loads(dumps(v))
            Fetching append attribute
            [1, 2, 3, 4]
        """
        return (TestAppendNonlist, (), None, iter(self.list))

    def __repr__(self):
        r"""
        Print a TestAppendNonlist.  Just prints as its underlying list.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestAppendNonlist()
            sage: v.list = ['hello', 'world']
            sage: v
            ['hello', 'world']
            sage: repr(v)
            "['hello', 'world']"
            sage: v.__repr__()
            "['hello', 'world']"
        """
        return repr(self.list)

class TestBuild(object):
    r"""
    A simple class with a __getstate__ but no __setstate__.  Used for testing
    explain_pickle.
    """
    def __getstate__(self):
        r"""
        A __getstate__ method for testing pickling.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: TestBuild().__getstate__()
            ({'x': 3}, {'y': 4})
            sage: loads(dumps(TestBuild()))
            TestBuild: x=3; y=4
        """
        return ({'x': 3}, {'y': 4})

    def __repr__(self):
        r"""
        Print a TestBuild.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestBuild()
            sage: v
            TestBuild: x=None; y=None
            sage: repr(v)
            'TestBuild: x=None; y=None'
            sage: v.__repr__()
            'TestBuild: x=None; y=None'
        """
        return "TestBuild: x=%s; y=%s" % (getattr(self, 'x', None), getattr(self, 'y', None))

class TestBuildSetstate(TestBuild):
    r"""
    A simple class with a __getstate__ and a __setstate__.  Used for testing
    explain_pickle.
    """
    def __setstate__(self, state):
        r"""
        Set the state of a TestBuildSetstate.  Both prints a message, and
        swaps x and y, to verify that it is being called.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: loads(dumps(TestBuildSetstate())) # indirect doctest
            setting state from ({'x': 3}, {'y': 4})
            TestBuild: x=4; y=3
        """
        print "setting state from %r" % (state,)
        # Swap x and y, just for fun
        self.x = state[1]['y']
        self.y = state[0]['x']

class TestGlobalOldName(object):
    r"""
    A featureless new-style class.  When you try to unpickle an instance
    of this class, it is redirected to create a TestGlobalNewName instead.
    Used for testing explain_pickle.

    EXAMPLES::

        sage: from sage.misc.explain_pickle import *
        sage: loads(dumps(TestGlobalOldName()))
        TestGlobalNewName
    """
    pass

class TestGlobalNewName(object):
    r"""
    A featureless new-style class.  When you try to unpickle an instance
    of TestGlobalOldName, it is redirected to create an instance of this
    class instead.  Used for testing explain_pickle.

    EXAMPLES:
        sage: from sage.misc.explain_pickle import *
        sage: loads(dumps(TestGlobalOldName()))
        TestGlobalNewName
    """
    def __repr__(self):
        r"""
        Print a TestGlobalNewName.

        EXAMPLES::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestGlobalNewName()
            sage: v
            TestGlobalNewName
            sage: repr(v)
            'TestGlobalNewName'
            sage: v.__repr__()
            'TestGlobalNewName'
        """
        return "TestGlobalNewName"

register_unpickle_override('sage.misc.explain_pickle', 'TestGlobalOldName', TestGlobalNewName, call_name=('sage.misc.explain_pickle', 'TestGlobalNewName'))

class TestGlobalFunnyName(object):
    r"""
    A featureless new-style class which has a name that's not a legal
    Python identifier.

    EXAMPLES::

        sage: from sage.misc.explain_pickle import *
        sage: globals()['funny$name'] = TestGlobalFunnyName # see comment at end of file
        sage: TestGlobalFunnyName.__name__
        'funny$name'
        sage: globals()['funny$name'] is TestGlobalFunnyName
        True
    """
    def __repr__(self):
        r"""
        Print a TestGlobalFunnyName.

        EXAMPLE::

            sage: from sage.misc.explain_pickle import *
            sage: v = TestGlobalFunnyName()
            sage: v
            TestGlobalFunnyName
            sage: repr(v)
            'TestGlobalFunnyName'
            sage: v.__repr__()
            'TestGlobalFunnyName'
        """
        return "TestGlobalFunnyName"

TestGlobalFunnyName.__name__ = "funny$name"
#This crashed Sphinx. Instead, we manually execute this just before the test.
#globals()['funny$name'] = TestGlobalFunnyName
