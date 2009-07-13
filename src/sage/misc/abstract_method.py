"""
Abstract methods
"""

#*****************************************************************************
#       Copyright (C) 2008 Nicolas M. Thiery <nthiery at users.sf.net>
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

import types

def abstract_method(f = None, optional = False):
    r"""
    Abstract methods

    INPUT:

     - ``f``: a function
     - ``optional``: a boolean; defaults to False

    The decorator :obj:`abstract_method` can be used to declare
    methods that should be implemented by all concrete derived
    classes. This declaration should typically include documentation
    for the specification for this method.

    The purpose is to enforce a consistent and visual syntax for such
    declarations. It is used by the Sage categories for automated
    tests (see ``Sets.Parent.test_not_implemented``).

    EXAMPLES:

    We create a class with an abstract method::

        sage: class A(object):
        ...
        ...       @abstract_method
        ...       def my_method(self):
        ...           '''
        ...           The method :meth:`my_method` computes my_method
        ...
        ...           EXAMPLES::
        ...
        ...           '''
        ...           pass
        ...
        sage: A.my_method
        <abstract method my_method at ...>

    The current policy is that a ``NotImplementedError`` is raised
    when accessing the method through an instance, even before the
    method is called::

        sage: x = A()
        sage: x.my_method
        Traceback (most recent call last):
        ...
        NotImplementedError: <abstract method my_method at ...>

    It is also possible to mark abstract methods as optional::

        sage: class A(object):
        ...
        ...       @abstract_method(optional = True)
        ...       def my_method(self):
        ...           '''
        ...           The method :meth:`my_method` computes my_method
        ...
        ...           EXAMPLES::
        ...
        ...           '''
        ...           pass
        ...

        sage: A.my_method
        <optional abstract method my_method at ...>

        sage: x = A()
        sage: x.my_method
        NotImplemented

    The official mantra for testing whether an optional abstract
    method is implemented is::

    # Fixme: sage -t complains about indentation below
    #    sage: if x.my_method is not NotImplemented:
    #    ...       x.my_method()
    #    ...   else:
    #    ...       print "x.my_method not available. Let's use some other trick."
    #    ...
    #    x.my_method not available. Let's use some other trick.

    ..topic: Discussion

    The policy details are not yet fixed. The purpose of this fist
    implementation is to let developpers experiment with it and give
    feedback on what's most practical.

    The advantage of the current policy is that attempts at using a
    non implemented methods are caught as early as possible. On the
    other hand, one cannot use introspection directly to fetch the
    documentation::

        sage: x.my_method?      # todo: not implemented

    Instead one needs to do::

        sage: A._my_method?     # todo: not implemented

    This could probably be fixed in :mod:`sage.misc.sageinspect`.

    TODO: what should be the recommended mantra for existence testing from the class?

    TODO: should extra information appear in the output? The name of
    the class? That of the super class where the abstract method is defined?

    TODO: look for similar decorators on the web, and merge

    ..topic: Implementation details

    Technically, an abstract_method is a non-data descriptor (see
    Invoking Descriptors in the Python reference manual).

    The syntax ``@abstract_method`` w.r.t. @abstract_method(optional = True)
    is achieved by a little trick which we test here::

        sage: abstract_method(optional = True)
        <function <lambda> at ...>
        sage: abstract_method(optional = True)(banner)
        <optional abstract method banner at ...>
        sage: abstract_method(banner, optional = True)
        <optional abstract method banner at ...>

    """
    if f is None:
        return lambda f: AbstractMethod(f, optional = optional)
    else:
        return AbstractMethod(f, optional)

class AbstractMethod(object):
    def __init__(self, f, optional = False):
        """
        Constructor for abstract methods

        EXAMPLES::

            sage: def f(x):
            ...       "doc of f"
            ...       return 1
            ...
            sage: x = abstract_method(f); x
            <abstract method f at ...>
            sage: x.__doc__
            'doc of f'
            sage: x.__name__
            'f'
            sage: x.__module__
            '__main__'
        """
        assert isinstance(f, types.FunctionType) # only plain functions are supported yet
        assert isinstance(optional, bool)
        self._f = f
        self._optional = optional
        if hasattr(f, "func_doc"):
            self.__doc__ = f.func_doc
        if hasattr(f, "func_name"):
            self.__name__ = f.func_name
        else:
            self.__name__ = "..."
        if hasattr(f, "__module__"):
            self.__module__ = f.__module__

    def __repr__(self):
        """
        EXAMPLES::

            sage: abstract_method(banner)
            <abstract method banner at ...>

            sage: abstract_method(banner, optional = True)
            <optional abstract method banner at ...>
        """
        return "<" + ("optional " if self._optional else "") + "abstract method %s"%repr(self._f)[10:]

    def _sage_src_lines_(self):
        """
        Returns the source code location for the wrapped function.

        EXAMPLES::

            sage: from sage.misc.sageinspect import sage_getsourcelines
            sage: g = abstract_method(banner)
            sage: (src, lines) = sage_getsourcelines(g)
            sage: src[0]
            'def banner():\n'
            sage: lines
            72

        """
        from sage.misc.sageinspect import sage_getsourcelines
        return sage_getsourcelines(self._f)


    def __get__(self, instance, cls):
        """
        Implements the attribute access protocol.

        EXAMPLES::

            sage: class A: pass
            sage: def f(x): return 1
            ...
            sage: f = abstract_method(f)
            sage: f.__get__(A(), A)
            Traceback (most recent call last):
            ...
            NotImplementedError: <abstract method f at ...>
        """
        if instance is None:
            return self
        elif self._optional:
            return NotImplemented
        else:
            raise NotImplementedError(repr(self))
