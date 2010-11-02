"""
Decorators

Python decorators for use in Sage.

AUTHORS:

- Tim Dumol (5 Dec 2009) -- initial version.
"""
from functools import partial, update_wrapper, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES
from copy import copy
from sage.misc.sageinspect import sage_getsource
from sage.misc.misc import verbose, deprecation

def sage_wraps(wrapped, assigned = WRAPPER_ASSIGNMENTS, updated = WRAPPER_UPDATES):
    """
    Decorator factory to apply update_wrapper() to a wrapper function,
    and additionally add a _sage_src_ attribute for Sage introspection.

    Use this exactly like @wraps from the functools module.

    EXAMPLES::

        sage: def square(f):
        ...     @sage_wraps(f)
        ...     def new_f(x):
        ...         return f(x)*f(x)
        ...     return new_f
        sage: @square
        ... def g(x):
        ...     "My little function"
        ...     return x
        sage: g(2)
        4
        sage: g(x)
        x^2
        sage: g._sage_src_()
        '@square...def g(x)...'
        sage: g.__doc__
        'My little function'

        # Demonstrate that sage_wraps works for non-function callables
        # (Trac 9919)
        sage: def square_for_met(f):
        ...     @sage_wraps(f)
        ...     def new_f(self, x):
        ...         return f(self,x)*f(self,x)
        ...     return new_f
        sage: class T:
        ...     @square_for_met
        ...     def g(self, x):
        ...         "My little method"
        ...         return x
        sage: t = T()
        sage: t.g(2)
        4
        sage: t.g._sage_src_()
        '   @square_for_met...def g(self, x)...'
        sage: t.g.__doc__
        'My little method'
    """
    #TRAC 9919: Workaround for bug in @update_wrapper when used with
    #non-function callables.
    assigned= set(assigned).intersection(set(dir(wrapped)))
    #end workaround
    def f(wrapper):
        update_wrapper(wrapper, wrapped, assigned=assigned, updated=updated)
        wrapper._sage_src_=lambda: sage_getsource(wrapped)
        return wrapper
    return f



# Infix operator decorator
class infix_operator(object):
    """
    A decorator for functions which allows for a hack that makes
    the function behave like an infix operator.

    This decorator exists as a convenience for interactive use.

    EXAMPLES:

    An infix dot product operator::

        sage: def dot(a,b): return a.dot_product(b)
        sage: dot=infix_operator('multiply')(dot)
        sage: u=vector([1,2,3])
        sage: v=vector([5,4,3])
        sage: u *dot* v
        22

    An infix element-wise addition operator::

        sage: def eadd(a,b):
        ...     return a.parent([i+j for i,j in zip(a,b)])
        sage: eadd=infix_operator('add')(eadd)
        sage: u=vector([1,2,3])
        sage: v=vector([5,4,3])
        sage: u +eadd+ v
        (6, 6, 6)
        sage: 2*u +eadd+ v
        (7, 8, 9)

    A hack to simulate a postfix operator::

        sage: def thendo(a,b): return b(a)
        sage: thendo=infix_operator('or')(thendo)
        sage: x |thendo| cos |thendo| (lambda x: x^2)
        cos(x)^2
    """

    def __init__(self, precedence):
        """
        A decorator for functions which allows for a hack that makes
        the function behave like an infix operator.

        This decorator exists as a convenience for interactive use.

        EXAMPLES::

            sage: def dot(a,b): return a.dot_product(b)
            sage: dot=infix_operator('multiply')(dot)
            sage: u=vector([1,2,3])
            sage: v=vector([5,4,3])
            sage: u *dot* v
            22

            sage: from sage.misc.decorators import infix_operator
            sage: def eadd(a,b):
            ...     return a.parent([i+j for i,j in zip(a,b)])
            sage: eadd=infix_operator('add')(eadd)
            sage: u=vector([1,2,3])
            sage: v=vector([5,4,3])
            sage: u +eadd+ v
            (6, 6, 6)
            sage: 2*u +eadd+ v
            (7, 8, 9)

            sage: from sage.misc.decorators import infix_operator
            sage: def thendo(a,b): return b(a)
            sage: thendo=infix_operator('or')(thendo)
            sage: x |thendo| cos |thendo| (lambda x: x^2)
            cos(x)^2
        """
        self.precedence=precedence

    operators={'add': {'left': '__add__', 'right': '__radd__'},
               'multiply': {'left': '__mul__', 'right': '__rmul__'},
               'or': {'left': '__or__', 'right': '__ror__'},
               }

    def __call__(self, func):
        """
        Returns a function which acts as an inline operator.

        EXAMPLES::

            sage: from sage.misc.decorators import infix_operator
            sage: def dot(a,b): return a.dot_product(b)
            sage: dot=infix_operator('multiply')(dot)
            sage: u=vector([1,2,3])
            sage: v=vector([5,4,3])
            sage: u *dot* v
            22

            sage: def eadd(a,b):
            ...     return a.parent([i+j for i,j in zip(a,b)])
            sage: eadd=infix_operator('add')(eadd)
            sage: u=vector([1,2,3])
            sage: v=vector([5,4,3])
            sage: u +eadd+ v
            (6, 6, 6)
            sage: 2*u +eadd+ v
            (7, 8, 9)

            sage: def thendo(a,b): return b(a)
            sage: thendo=infix_operator('or')(thendo)
            sage: x |thendo| cos |thendo| (lambda x: x^2)
            cos(x)^2
        """
        def left_func(self, right):
            """
            The function for the operation on the left (e.g., __add__).

            EXAMPLES::

                sage: def dot(a,b): return a.dot_product(b)
                sage: dot=infix_operator('multiply')(dot)
                sage: u=vector([1,2,3])
                sage: v=vector([5,4,3])
                sage: u *dot* v
                22
            """

            if self.left is None:
                if self.right is None:
                    new = copy(self)
                    new.right=right
                    return new
                else:
                    raise SyntaxError, "Infix operator already has its right argument"
            else:
                return self.function(self.left, right)

        def right_func(self, left):
            """
            The function for the operation on the right (e.g., __radd__).

            EXAMPLES::

                sage: def dot(a,b): return a.dot_product(b)
                sage: dot=infix_operator('multiply')(dot)
                sage: u=vector([1,2,3])
                sage: v=vector([5,4,3])
                sage: u *dot* v
                22
            """
            if self.right is None:
                if self.left is None:
                    new = copy(self)
                    new.left=left
                    return new
                else:
                    raise SyntaxError, "Infix operator already has its left argument"
            else:
                return self.function(left, self.right)


        @sage_wraps(func)
        class wrapper:
            def __init__(self, left=None, right=None):
                """
                Initialize the actual infix object, with possibly a
                specified left and/or right operand.

                EXAMPLES::

                    sage: def dot(a,b): return a.dot_product(b)
                    sage: dot=infix_operator('multiply')(dot)
                    sage: u=vector([1,2,3])
                    sage: v=vector([5,4,3])
                    sage: u *dot* v
                    22
                """

                self.function = func
                self.left = left
                self.right = right
            def __call__(self, *args, **kwds):
                """
                Call the passed function.

                EXAMPLES::

                    sage: def dot(a,b): return a.dot_product(b)
                    sage: dot=infix_operator('multiply')(dot)
                    sage: u=vector([1,2,3])
                    sage: v=vector([5,4,3])
                    sage: dot(u,v)
                    22
                """
                return self.function(*args, **kwds)

        setattr(wrapper, self.operators[self.precedence]['left'], left_func)
        setattr(wrapper, self.operators[self.precedence]['right'], right_func)

        from sage.misc.sageinspect import sage_getsource
        wrapper._sage_src_ = lambda: sage_getsource(func)

        return wrapper()




def decorator_defaults(func):
    """
    This function allows a decorator to have default arguments.

    Normally, a decorator can be called with or without arguments.
    However, the two cases call for different types of return values.
    If a decorator is called with no parentheses, it should be run
    directly on the function.  However, if a decorator is called with
    parentheses (i.e., arguments), then it should return a function
    that is then in turn called with the defined function as an
    argument.

    This decorator allows us to have these default arguments without
    worrying about the return type.

    EXAMPLES::

        sage: from sage.misc.decorators import decorator_defaults
        sage: @decorator_defaults
        ... def my_decorator(f,*args,**kwds):
        ...     print kwds
        ...     print args
        ...     print f.__name__
        ...
        sage: @my_decorator
        ... def my_fun(a,b):
        ...     return a,b
        ...
        {}
        ()
        my_fun
        sage: @my_decorator(3,4,c=1,d=2)
        ... def my_fun(a,b):
        ...     return a,b
        ...
        {'c': 1, 'd': 2}
        (3, 4)
        my_fun
    """
    @sage_wraps(func)
    def my_wrap(*args,**kwds):
        if len(kwds)==0 and len(args)==1:
            # call without parentheses
            return func(*args)
        else:
            return lambda f: func(f, *args, **kwds)
    return my_wrap


class suboptions(object):
    def __init__(self, name, **options):
        """
        A decorator for functions which collects all keywords
        starting with name_ and collects them into a dictionary
        which will be passed on to the wrapped function as a
        dictionary called name_options.

        The keyword arguments passed into the constructor are taken
        to be default for the name_options dictionary.

        EXAMPLES::

            sage: from sage.misc.decorators import suboptions
            sage: s = suboptions('arrow', size=2)
            sage: s.name
            'arrow_'
            sage: s.options
            {'size': 2}
        """
        self.name = name + "_"
        self.options = options

    def __call__(self, func):
        """
        Returns a wrapper around func

        EXAMPLES::

            sage: from sage.misc.decorators import suboptions
            sage: def f(*args, **kwds): print list(sorted(kwds.items()))
            sage: f = suboptions('arrow', size=2)(f)
            sage: f(size=2)
            [('arrow_options', {'size': 2}), ('size', 2)]
            sage: f(arrow_size=3)
            [('arrow_options', {'size': 3})]
            sage: f(arrow_options={'size':4})
            [('arrow_options', {'size': 4})]
            sage: f(arrow_options={'size':4}, arrow_size=5)
            [('arrow_options', {'size': 5})]

        """
        @sage_wraps(func)
        def wrapper(*args, **kwds):
            suboptions = copy(self.options)
            suboptions.update(kwds.pop(self.name+"options", {}))

            #Collect all the relevant keywords in kwds
            #and put them in suboptions
            for key, value in kwds.items():
                if key.startswith(self.name):
                    suboptions[key[len(self.name):]] = value
                    del kwds[key]

            kwds[self.name + "options"] = suboptions

            return func(*args, **kwds)

        return wrapper

class options(object):
    def __init__(self, **options):
        """
        A decorator for functions which allows for default options to be
        set and reset by the end user.  Additionally, if one needs to, one
        can get at the original keyword arguments passed into the
        decorator.

        TESTS::

            sage: from sage.misc.decorators import options
            sage: o = options(rgbcolor=(0,0,1))
            sage: o.options
            {'rgbcolor': (0, 0, 1)}
            sage: o = options(rgbcolor=(0,0,1), __original_opts=True)
            sage: o.original_opts
            True
            sage: loads(dumps(o)).options
            {'rgbcolor': (0, 0, 1)}
        """
        self.options = options
        self.original_opts = options.pop('__original_opts', False)

    def __call__(self, func):
        """
        EXAMPLES::

            sage: from sage.misc.decorators import options
            sage: o = options(rgbcolor=(0,0,1))
            sage: def f(*args, **kwds): print args, list(sorted(kwds.items()))
            sage: f1 = o(f)
            sage: f1()
            () [('rgbcolor', (0, 0, 1))]
            sage: f1(rgbcolor=1)
            () [('rgbcolor', 1)]
            sage: o = options(rgbcolor=(0,0,1), __original_opts=True)
            sage: f2 = o(f)
            sage: f2(alpha=1)
            () [('__original_opts', {'alpha': 1}), ('alpha', 1), ('rgbcolor', (0, 0, 1))]

        """
        @sage_wraps(func)
        def wrapper(*args, **kwds):
            options = copy(wrapper.options)
            if self.original_opts:
                options['__original_opts'] = kwds
            options.update(kwds)
            return func(*args, **options)


        def defaults():
            """
            Return the default options.

            EXAMPLES::

                sage: from sage.misc.decorators import options
                sage: o = options(rgbcolor=(0,0,1))
                sage: def f(*args, **kwds): print args, list(sorted(kwds.items()))
                sage: f = o(f)
                sage: f.options['rgbcolor']=(1,1,1)
                sage: f.defaults()
                {'rgbcolor': (0, 0, 1)}
            """
            return copy(self.options)

        def reset():
            """
            Reset the options to the defaults.

            EXAMPLES::

                sage: from sage.misc.decorators import options
                sage: o = options(rgbcolor=(0,0,1))
                sage: def f(*args, **kwds): print args, list(sorted(kwds.items()))
                sage: f = o(f)
                sage: f.options
                {'rgbcolor': (0, 0, 1)}
                sage: f.options['rgbcolor']=(1,1,1)
                sage: f.options
                {'rgbcolor': (1, 1, 1)}
                sage: f()
                () [('rgbcolor', (1, 1, 1))]
                sage: f.reset()
                sage: f.options
                {'rgbcolor': (0, 0, 1)}
                sage: f()
                () [('rgbcolor', (0, 0, 1))]
            """
            wrapper.options = copy(self.options)

        wrapper.options = copy(self.options)
        wrapper.reset = reset
        wrapper.reset.__doc__ = """
        Reset the options to the defaults.

        Defaults:
        %s
        """%self.options

        wrapper.defaults = defaults
        wrapper.defaults.__doc__ = """
        Return the default options.

        Defaults:
        %s
        """%self.options

        return wrapper


class rename_keyword(object):
    def __init__(self, deprecated=None, **renames):
        """
        A decorator which renames keyword arguments and optionally
        deprecates the new keyword.

        INPUT:

        - ``deprecated`` - If the option being renamed is deprecated, this
          is the Sage version where the deprecation initially occurs.

        - the rest of the arguments is a list of keyword arguments in the
          form ``renamed_option='existing_option'``.  This will have the
          effect of renaming ``renamed_option`` so that the function only
          sees ``existing_option``.  If both ``renamed_option`` and
          ``existing_option`` are passed to the function, ``existing_option``
          will override the ``renamed_option`` value.

        EXAMPLES::

            sage: from sage.misc.decorators import rename_keyword
            sage: r = rename_keyword(color='rgbcolor')
            sage: r.renames
            {'color': 'rgbcolor'}
            sage: loads(dumps(r)).renames
            {'color': 'rgbcolor'}

        To deprecate an old keyword::

            sage: r = rename_keyword(deprecated='Sage version 4.2', color='rgbcolor')
        """
        self.renames = renames
        self.deprecated=deprecated

    def __call__(self, func):
        """
        Rename keywords.

        EXAMPLES::

            sage: from sage.misc.decorators import rename_keyword
            sage: r = rename_keyword(color='rgbcolor')
            sage: def f(*args, **kwds): print args, kwds
            sage: f = r(f)
            sage: f()
            () {}
            sage: f(alpha=1)
            () {'alpha': 1}
            sage: f(rgbcolor=1)
            () {'rgbcolor': 1}
            sage: f(color=1)
            () {'rgbcolor': 1}

        We can also deprecate the renamed keyword::

            sage: r = rename_keyword(deprecated='Sage version 4.2', deprecated_option='new_option')
            sage: def f(*args, **kwds): print args, kwds
            sage: f = r(f)
            sage: f()
            () {}
            sage: f(alpha=1)
            () {'alpha': 1}
            sage: f(new_option=1)
            () {'new_option': 1}
            sage: f(deprecated_option=1)
            doctest:...: DeprecationWarning: (Since Sage version 4.2) use the option 'new_option' instead of 'deprecated_option'
            () {'new_option': 1}
        """
        @sage_wraps(func)
        def wrapper(*args, **kwds):
            for old_name, new_name in self.renames.items():
                if old_name in kwds and new_name not in kwds:
                    if self.deprecated is not None:
                        deprecation("use the option %r instead of %r"%(new_name,old_name),
                            version=self.deprecated)
                    kwds[new_name] = kwds[old_name]
                    del kwds[old_name]
            return func(*args, **kwds)

        return wrapper


class specialize:
    r"""
    A decorator generator that returns a decorator that in turn
    returns a specialized function for function ``f``. In other words,
    it returns a function that acts like ``f`` with arguments
    ``*args`` and ``**kwargs`` supplied.

    INPUT:

    - ``*args``, ``**kwargs`` -- arguments to specialize the function for.

    OUTPUT:

    - a decorator that accepts a function ``f`` and specializes it
      with ``*args`` and ``**kwargs``

    EXAMPLES::

        sage: f = specialize(5)(lambda x, y: x+y)
        sage: f(10)
        15
        sage: f(5)
        10
        sage: @specialize("Bon Voyage")
        ... def greet(greeting, name):
        ...    print "{0}, {1}!".format(greeting, name)
        sage: greet("Monsieur Jean Valjean")
        Bon Voyage, Monsieur Jean Valjean!
        sage: greet(name = 'Javert')
        Bon Voyage, Javert!
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, f):
        return sage_wraps(f)(partial(f, *self.args, **self.kwargs))
