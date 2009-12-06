###############################################################################
#   Sage: Open Source Mathematical Software
#       Copyright (C) 2008 - 2009 Burcin Erocal <burcin@erocal.org>
#       Copyright (C) 2008 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL),
#  version 2 or any later version.  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

r"""

Support for symbolic functions.

"""
include "../ext/interrupt.pxi"
include "../ext/stdsage.pxi"
include "../ext/cdefs.pxi"
include "../libs/ginac/decl.pxi"


from sage.structure.sage_object cimport SageObject
from expression cimport new_Expression_from_GEx, Expression
from ring import SR

from sage.structure.parent cimport Parent
from sage.structure.element cimport Element
from sage.structure.element import parent

# we keep a database of symbolic functions initialized in a session
# this also makes the .operator() method of symbolic expressions work
cdef dict sfunction_serial_dict = {}

from sage.misc.fpickle import pickle_function, unpickle_function

cdef class Function(SageObject):
    """
    Base class for symbolic functions defined through Pynac in Sage.

    This is only an abstract base class, with generic code for the interfaces
    and a :method:`__call__` method. Subclasses should implement the
    :method:`_is_registered` and :method:`_register_function` methods.
    """
    def __init__(self, name, nargs, latex_name=None, conversions=None):
        """
        This is an abstract base class. It's not possible to test it directly.

        EXAMPLES::

            sage: f = function('f', nargs=1, conjugate_func=lambda self,x: 2r*x) # indirect doctest
            sage: f(2)
            f(2)
            sage: f(2).conjugate()
            4
        """
        self._name = name
        self._nargs = nargs
        self._latex_name = latex_name
        self._conversions = {} if conversions is None else conversions

        if not self._is_registered():
            self._register_function()

            global sfunction_serial_dict
            sfunction_serial_dict[self._serial] = self

            from sage.symbolic.pynac import symbol_table, register_symbol
            symbol_table['functions'][self._name] = self

            register_symbol(self, self._conversions)

    cdef _is_registered(self):
        """
        Check if this function is already registered. If it is, set
        `self._serial` to the right value.
        """
        raise NotImplementedError, "this is an abstract base class, it shouldn't be initialized directly"

    cdef _register_function(self):
        """
        Add this function to the GiNaC function registry, and set
        `self._serial` to the right value.
        """
        raise NotImplementedError, "this is an abstract base class, it shouldn't be initialized directly"

    def __hash__(self):
        """
        EXAMPLES::

            sage: f = function('f', nargs=1, conjugate_func=lambda self,x: 2r*x)
            sage: f.__hash__() #random
            -2224334885124003860
            sage: hash(f(2)) #random
            4168614485
        """
        return hash(self._name)*(self._nargs+1)*self._serial

    def __repr__(self):
        """
        EXAMPLES::

            sage: foo = function("foo", nargs=2); foo
            foo
        """
        return self._name

    def _latex_(self):
        r"""
        EXAMPLES::

            sage: from sage.symbolic.function import SymbolicFunction
            sage: s = SymbolicFunction('foo'); s
            foo
            sage: latex(s)
            foo
            sage: s = SymbolicFunction('foo', latex_name=r'{\rm foo}')
            sage: latex(s)
            {\rm foo}
            sage: s._latex_()
            '{\\rm foo}'
        """
        if self._latex_name is not None:
            return self._latex_name
        else:
            return self._name

    def __cmp__(self, other):
        """
        TESTS:
            sage: foo = function("foo", nargs=2)
            sage: foo == foo
            True
            sage: foo == 2
            False
            sage: foo(1,2).operator() == foo
            True

        """
        if PY_TYPE_CHECK(other, Function):
            return cmp(self._serial, (<Function>other)._serial)
        return False

    def __call__(self, *args, coerce=True, hold=False):
        """
        Evaluates this function at the given arguments.

        We coerce the arguments into symbolic expressions if coerce=True, then
        call the Pynac evaluation method, which in turn passes the arguments to
        a custom automatic evaluation method if ``_eval_()`` is defined.

        EXAMPLES::

            sage: foo = function("foo", nargs=2)
            sage: x,y,z = var("x y z")
            sage: foo(x,y)
            foo(x, y)

            sage: foo(y)
            Traceback (most recent call last):
            ...
            TypeError: Symbolic function foo takes exactly 2 arguments (1 given)

            sage: bar = function("bar")
            sage: bar(x)
            bar(x)
            sage: bar(x,y)
            bar(x, y)

        The `hold` argument prevents automatic evaluation of the function::

            sage: exp(log(x))
            x
            sage: exp(log(x), hold=True)
            e^log(x)

        We can also handle numpy types::

            sage: import numpy
            sage: sin(numpy.arange(5))
            array([ 0.        ,  0.84147098,  0.90929743,  0.14112001, -0.7568025 ])

        Symbolic functions evaluate non-exact input numerically, and return
        symbolic expressions on exact input::

            sage: arctan(1)
            1/4*pi
            sage: arctan(float(1))
            0.78539816339744828

        Precision of the result depends on the precision of the input::

            sage: arctan(RR(1))
            0.785398163397448
            sage: arctan(RealField(100)(1))
            0.78539816339744830961566084582

        Return types for non-exact input depends on the input type::

            sage: type(exp(float(0)))
            <type 'float'>
            sage: exp(RR(0)).parent()
            Real Field with 53 bits of precision


        TESTS:

        Test coercion::

            sage: bar(ZZ)
            Traceback (most recent call last):
            ...
            TypeError: cannot coerce arguments: ...
            sage: exp(QQbar(I))
            0.540302305868140 + 0.841470984807897*I

        For functions with single argument, if coercion fails we try to call
        a method with the name of the function on the object::

            sage: M = matrix(SR, 2, 2, [x, 0, 0, I*pi])
            sage: exp(M)
            [e^x   0]
            [  0  -1]
        """
        if self._nargs > 0 and len(args) != self._nargs:
            raise TypeError, "Symbolic function %s takes exactly %s arguments (%s given)"%(self._name, self._nargs, len(args))

        # support fast_float
        if self._nargs == 1:
            import sage.ext.fast_eval
            if isinstance(args[0], sage.ext.fast_eval.FastDoubleFunc):
                try:
                    return getattr(args[0], self._name)()
                except AttributeError, err:
                    raise TypeError, "cannot handle fast float arguments"
            elif type(args[0]).__module__ == 'numpy': # avoid importing
                import numpy
                try:
                    return getattr(numpy, self.name())(args[0])
                except AttributeError:
                    pass

        # if the given input is a symbolic expression, we don't convert it back
        # to a numeric type at the end
        if len(args) == 1 and parent(args[0]) is SR:
            symbolic_input = True
        else:
            symbolic_input = False


        cdef Py_ssize_t i
        if coerce:
            try:
                args = map(SR.coerce, args)
            except TypeError, err:
                # If the function takes only one argument, we try to call
                # a method with the name of this function on the object.
                # This makes the following work:
                #     sage: M = matrix(SR, 2, 2, [x, 0, 0, I*pi])
                #     [e^x   0]
                #     [  0  -1]
                if len(args) == 1:
                    try:
                        return getattr(args[0], self._name)()
                    except AttributeError:
                        pass

                # There is no natural coercion from QQbar to the symbolic ring
                # in order to support
                #     sage: QQbar(sqrt(2)) + sqrt(3)
                #     3.146264369941973?
                # to work around this limitation, we manually convert
                # elements of QQbar to symbolic expressions here
                from sage.rings.qqbar import QQbar, AA
                nargs = [None]*len(args)
                for i in range(len(args)):
                    carg = args[i]
                    if PY_TYPE_CHECK(carg, Element) and \
                            (<Element>carg)._parent is QQbar or \
                            (<Element>carg)._parent is AA:
                        nargs[i] = SR(carg)
                    else:
                        try:
                            nargs[i] = SR.coerce(carg)
                        except:
                            raise TypeError, "cannot coerce arguments: %s"%(err)
                args = nargs
        else: # coerce == False
            for a in args:
                if PY_TYPE_CHECK(a, Expression):
                    raise TypeError, "arguments must be symbolic expressions"

        cdef GEx res
        cdef GExVector vec
        if self._nargs == 0 or self._nargs > 3:
            for i from 0 <= i < len(args):
                vec.push_back((<Expression>args[i])._gobj)
            res = g_function_evalv(self._serial, vec, hold)
        elif self._nargs == 1:
            res = g_function_eval1(self._serial,
                    (<Expression>args[0])._gobj, hold)
        elif self._nargs == 2:
            res = g_function_eval2(self._serial, (<Expression>args[0])._gobj,
                    (<Expression>args[1])._gobj, hold)
        elif self._nargs == 3:
            res = g_function_eval3(self._serial,
                    (<Expression>args[0])._gobj, (<Expression>args[1])._gobj,
                    (<Expression>args[2])._gobj, hold)


        if not symbolic_input and is_a_numeric(res):
            return py_object_from_numeric(res)

        return new_Expression_from_GEx(SR, res)

    def name(self):
        """
        Returns the name of this function.

        EXAMPLES::

            sage: foo = function("foo", nargs=2)
            sage: foo.name()
            'foo'
        """
        return self._name

    def number_of_arguments(self):
        """
        Returns the number of arguments that this function takes.

        EXAMPLES::

            sage: foo = function("foo", nargs=2)
            sage: foo.number_of_arguments()
            2
            sage: foo(x,x)
            foo(x, x)

            sage: foo(x)
            Traceback (most recent call last):
            ...
            TypeError: Symbolic function foo takes exactly 2 arguments (1 given)
        """
        return self._nargs

    def variables(self):
        """
        Returns the variables (of which there are none) present in
        this SFunction.

        EXAMPLES::

            sage: sin.variables()
            ()
        """
        return ()

    def default_variable(self):
        """
        Returns a default variable.

        EXAMPLES::

            sage: sin.default_variable()
            x
        """
        return SR.var('x')

    def _interface_init_(self, I=None):
        """
        EXAMPLES::

             sage: sin._interface_init_(maxima)
             'sin'
        """
        if I is None:
            return self._name
        return self._conversions.get(I.name(), self._name)

    def _mathematica_init_(self):
        """
        EXAMPLES::

             sage: sin._mathematica_init_()
             'Sin'
             sage: exp._mathematica_init_()
             'Exp'
             sage: (exp(x) + sin(x) + tan(x))._mathematica_init_()
             '(Exp[x])+(Sin[x])+(Tan[x])'
        """
        s = self._conversions.get('mathematica', None)
        return s if s is not None else repr(self).capitalize()

    def _maxima_init_(self, I=None):
        """
        EXAMPLES::

            sage: exp._maxima_init_()
            'exp'
            sage: from sage.symbolic.function import SymbolicFunction
            sage: f = SymbolicFunction('f', latex_name='f', conversions=dict(maxima='ff'))
            sage: f._maxima_init_()
            'ff'
        """
        s = self._conversions.get('maxima', None)
        if s is None:
            return repr(self)
        else:
            return s

    def _fast_float_(self, *vars):
        """
        Returns an object which provides fast floating point evaluation of
        self.

        See sage.ext.fast_eval? for more information.

        EXAMPLES::

            sage: sin._fast_float_()
            <sage.ext.fast_eval.FastDoubleFunc object at 0x...>
            sage: sin._fast_float_()(0)
            0.0

        ::

            sage: ff = cos._fast_float_(); ff
            <sage.ext.fast_eval.FastDoubleFunc object at 0x...>
            sage: ff.is_pure_c()
            True
            sage: ff(0)
            1.0

        ::

            sage: ff = erf._fast_float_()
            sage: ff.is_pure_c()
            False
            sage: ff(1.5)
            0.96610514647531076
            sage: erf(1.5)
            0.966105146475311
        """
        import sage.ext.fast_eval as fast_float

        args = [fast_float.fast_float_arg(n) for n in range(self.number_of_arguments())]
        try:
            return self(*args)
        except TypeError, err:
            return fast_float.fast_float_func(self, *args)

    def _fast_callable_(self, etb):
        r"""
        Given an ExpressionTreeBuilder, return an Expression representing
        this value.

        EXAMPLES::

            sage: from sage.ext.fast_callable import ExpressionTreeBuilder
            sage: etb = ExpressionTreeBuilder(vars=['x','y'])
            sage: sin._fast_callable_(etb)
            sin(v_0)
            sage: erf._fast_callable_(etb)
            {erf}(v_0)
        """
        args = [etb._var_number(n) for n in range(self.number_of_arguments())]
        return etb.call(self, *args)

cdef class GinacFunction(Function):
    """
    This class provides a wrapper around symbolic functions already defined in
    Pynac/GiNaC. Custom methods for these functions are defined at the C++ level
    and we can't change them from Python. There is also no need to register
    these functions.
    """
    def __init__(self, name, nargs=1, latex_name=None, conversions=None,
            ginac_name=None):
        """
        TESTS::

            sage: from sage.functions.trig import Function_sin
            sage: s = Function_sin() # indirect doctest
            sage: s(0)
            0
            sage: s(pi)
            0
            sage: s(pi/2)
            1
        """
        self._ginac_name = ginac_name
        Function.__init__(self, name, nargs, latex_name, conversions)

    cdef _is_registered(self):
        # Since this is function is defined in C++, it is already in
        # ginac's function registry
        fname = self._ginac_name if self._ginac_name is not None else self._name
        # get serial
        try:
            self._serial = find_function(fname, self._nargs)
        except ValueError, err:
            raise ValueError, "cannot find GiNaC function with name %s and %s arguments"%(fname, self._nargs)

        global sfunction_serial_dict
        return sfunction_serial_dict.has_key(self._serial)

    cdef _register_function(self):
        # Nothing to be done for registering
        # Function.__init__ has the necessary code to register in the
        # Sage function table
        pass

    def __reduce__(self):
        """
        TESTS::

            sage: t = loads(dumps(sin)); t
            sin
            sage: t(pi)
            0
        """
        return self.__class__, tuple()

    # this is required to read old pickles of ginac functions
    # like sin, cos, etc.
    def __setstate__(self, state):
        """
        TESTS::

            sage: sin.__setstate__([1,0])
            Traceback (most recent call last):
            ...
            ValueError: cannot read pickle
            sage: sin.__setstate__([0]) #don't try this at home
        """

        if state[0] == 0:
            # old pickle data
            self.__init__()
        else:
            # we should never end up here
            raise ValueError, "cannot read pickle"

    def __call__(self, *args, coerce=True, hold=False):
        # we want to convert the result to the original parent if the input
        # is not exact, so we store the parent here
        org_parent = parent(args[0])

        res = super(GinacFunction, self).__call__(*args, coerce=coerce,
                hold=hold)

        # convert the result back to the original parent previously stored
        # otherwise we end up with
        #     sage: arctan(RR(1))
        #     1/4*pi
        # which is surprising, to say the least...
        if org_parent is not SR and \
                (org_parent is float or org_parent is complex or \
                (PY_TYPE_CHECK(org_parent, Parent) and \
                    not org_parent.is_exact())):
            try:
                return org_parent(res)
            except (TypeError, ValueError):
                pass

            # conversion to the original parent failed
            # we try if it works with the corresponding complex domain
            if org_parent is float:
                try:
                    return complex(res)
                except (TypeError, ValueError):
                    pass
            elif hasattr(org_parent, 'complex_field'):
                try:
                    return org_parent.complex_field()(res)
                except (TypeError, ValueError):
                    pass

        return res

# list of functions which ginac allows us to define custom behavior for
# changing the order of this list could cause problems unpickling old pickles
sfunctions_funcs = ['eval', 'evalf', 'conjugate', 'real_part', 'imag_part',
        'derivative', 'power', 'series', 'print', 'print_latex']

cdef class CustomizableFunction(Function):
    """
    This is the basis for symbolic functions with custom evaluation, derivative,
    etc. methods defined in Sage from Python/Cython.

    This class is not intended for direct use, instead use one of the
    subclasses :class:`BuiltinFunction` or :class:`SymbolicFunction`.
    """
    def __init__(self, name, nargs=0, latex_name=None, conversions=None):
        """
        TESTS::

            # eval_func raises exception
            sage: def ef(self, x): raise RuntimeError, "foo"
            sage: bar = function("bar", nargs=1, eval_func=ef)
            sage: bar(x)
            Traceback (most recent call last):
            ...
            RuntimeError: foo

            # eval_func returns non coercible
            sage: def ef(self, x): return ZZ
            sage: bar = function("bar", nargs=1, eval_func=ef)
            sage: bar(x)
            Traceback (most recent call last):
            ...
            TypeError: eval function did not return a symbolic expression or an element that can be coerced into a symbolic expression

            # eval_func is not callable
            sage: bar = function("bar", nargs=1, eval_func=5)
            Traceback (most recent call last):
            ...
            ValueError: eval_func parameter must be callable

        """
        # handle custom printing
        # if print_func is defined, it is used instead of name
        # latex printing can be customised either by setting a string latex_name
        # or giving a custom function argument print_latex_func
        if latex_name and hasattr(self, '_print_latex_'):
            raise ValueError, "only one of latex_name or _print_latex_ should be specified."

        for fname in sfunctions_funcs:
            real_fname = '_%s_'%fname
            if hasattr(self, real_fname) and not \
                    callable(getattr(self, real_fname)):
                raise ValueError,  real_fname + " parameter must be callable"

        Function.__init__(self, name, nargs, latex_name, conversions)

    cdef _register_function(self):
        cdef GFunctionOpt opt
        opt = g_function_options_args(self._name, self._nargs)
        opt.set_python_func()

        if hasattr(self, '_eval_'):
            opt.eval_func(self)

        if hasattr(self, '_evalf_'):
            opt.evalf_func(self)

        if hasattr(self, '_conjugate_'):
            opt.conjugate_func(self)

        if hasattr(self, '_real_part_'):
            opt.real_part_func(self)

        if hasattr(self, '_imag_part_'):
            opt.imag_part_func(self)

        if hasattr(self, '_derivative_'):
            opt.derivative_func(self)

        if hasattr(self, '_power_'):
            opt.power_func(self)

        if hasattr(self, '_series_'):
            opt.series_func(self)

        # custom print functions are called from python
        #if hasattr(self, '_print_latex_'):
        #    opt.set_print_latex_func(self._print_latex_)
        #if hasattr(self, '_print_'):
        #    opt.set_print_dflt_func(self._print_)

        if self._latex_name:
            opt.latex_name(self._latex_name)

        self._serial = g_register_new(opt)
        g_foptions_assign(g_registered_functions().index(self._serial), opt)

    def _eval_default(self, x):
        """
        Default automatic evaluation function.

        Calls numeric evaluation if the argument is not exact.

        TESTS::

            sage: cot(0.5) #indirect doctest
            1.83048772171245
            sage: cot(complex(1,2))
            (0.032797755533752602-0.98432922645819...j)
        """
        if isinstance(x, (int, long)):
            return None

        if isinstance(x, float):
            return self._evalf_(x, float)
        if isinstance(x, complex):
            return self._evalf_(x, complex)
        if isinstance(x, Element):
            if x.parent().is_exact():
                return None
        try:
            return getattr(x, self.name())()
        except AttributeError:
            pass


cdef class BuiltinFunction(CustomizableFunction):
    """
    This is the base class for symbolic functions defined in Sage.

    If a function is provided by the Sage library, we don't need to pickle
    the custom methods, since we can just initialize the same library function
    again. This allows us to use Cython for custom methods.

    We assume that each subclass of this class will define one symbolic
    function. Make sure you use subclasses and not just call the initializer
    of this class.
    """
    def __init__(self, name, nargs=1, latex_name=None, conversions=None):
        """
        TESTS::

            sage: from sage.functions.trig import Function_cot
            sage: c = Function_cot() # indirect doctest
            sage: c(pi/2)
            0
        """
        CustomizableFunction.__init__(self, name, nargs, latex_name,
                conversions)

    _eval_ = CustomizableFunction._eval_default

    cdef _is_registered(self):
        # check if already defined
        cdef int serial = -1

        # search ginac registry for name and nargs
        try:
            serial = find_function(self._name, self._nargs)
        except ValueError, err:
            pass

        # if match, get operator from function table
        global sfunction_serial_dict
        if serial != -1 and sfunction_serial_dict.has_key(self._name) and \
                sfunction_serial_dict[self._name].__class__ == self.__class__:
                    # if the returned function is of the same type
                    self._serial = serial
                    return True

        # search the function table to check if any of this type
        for key, val in sfunction_serial_dict.iteritems():
            if val.__class__ == self.__class__:
                self._serial = key
                return True

        return False

    def __reduce__(self):
        """
        EXAMPLES::

            sage: cot.__reduce__()
            (<class 'sage.functions.trig.Function_cot'>, ())

            sage: f = loads(dumps(cot)) #indirect doctest
            sage: f(pi/2)
            0
        """
        return self.__class__, tuple()

    # this is required to read old pickles of erf, elliptic_ec, etc.
    def __setstate__(self, state):
        """
        EXAMPLES::

            sage: cot.__setstate__([1,0])
            Traceback (most recent call last):
            ...
            ValueError: cannot read pickle
            sage: cot.__setstate__([0]) #don't try this at home
        """
        if state[0] == 0:
            # old pickle data
            # we call __init__ since Python only allocates the class and does
            # not call __init__ before passing the pickled state to __setstate__
            self.__init__()
        else:
            # we should never end up here
            raise ValueError, "cannot read pickle"


cdef class SymbolicFunction(CustomizableFunction):
    """
    This is the basis for user defined symbolic functions. We try to pickle or
    hash the custom methods, so subclasses must be defined in Python not Cython.
    """
    def __init__(self, name, nargs=0, latex_name=None, conversions=None):
        """
        EXAMPLES::

            sage: from sage.symbolic.function import SymbolicFunction
            sage: class my_function(SymbolicFunction):
            ...  def __init__(self):
            ...     SymbolicFunction.__init__(self, 'foo', nargs=2)
            ...  def _evalf_(self, x, y, parent=None):
            ...     return x*y*2r
            ...  def _conjugate_(self, x, y):
            ...     return x
            sage: foo = my_function()
            sage: foo
            foo
            sage: foo(2,3)
            foo(2, 3)
            sage: foo(2,3).n()
            12.0000000000000
            sage: foo(2,3).conjugate()
            2
        """
        self.__hinit = False
        CustomizableFunction.__init__(self, name, nargs, latex_name,
                conversions)

    cdef _is_registered(SymbolicFunction self):
        # see if there is already an SFunction with the same state
        cdef Function sfunc
        cdef long myhash = self._hash_()
        for sfunc in sfunction_serial_dict.itervalues():
            if PY_TYPE_CHECK(sfunc, SymbolicFunction) and \
                    myhash == (<SymbolicFunction>sfunc)._hash_():
                # found one, set self._serial to be a copy
                self._serial = sfunc._serial
                return True

        return False

    # cache the hash value of this function
    # this is used very often while unpickling to see if there is already
    # a function with the same properties
    cdef long _hash_(self) except -1:
        if not self.__hinit:
            # create a string representation of this SFunction
            slist = [self._nargs, self._name, str(self._latex_name)]
            for fname in sfunctions_funcs:
                real_fname = '_%s_'%fname
                if hasattr(self, '%s'%real_fname):
                    slist.append(hash(getattr(self, real_fname).func_code))
                else:
                    slist.append(' ')
            self.__hcache = hash(tuple(slist))
            self.__hinit = True
        return self.__hcache

    def __hash__(self):
        """
        TESTS::

            sage: foo = function("foo", nargs=2)
            sage: hash(foo)      # random output
            -6859868030555295348

            sage: def ev(self, x): return 2*x
            sage: foo = function("foo", nargs=2, eval_func = ev)
            sage: hash(foo)      # random output
            -6859868030555295348
        """
        return self._serial*self._hash_()

    def __getstate__(self):
        """
        Returns a tuple describing the state of this object for pickling.

        Pickling SFunction objects is limited by the ability to pickle
        functions in python. We use sage.misc.fpickle.pickle_function for
        this purpose, which only works if there are no nested functions.


        This should return all information that will be required to unpickle
        the object. The functionality for unpickling is implemented in
        __setstate__().

        In order to pickle SFunction objects, we return a tuple containing

         * 0  - as pickle version number
                in case we decide to change the pickle format in the feature
         * name of this function
         * number of arguments
         * latex_name
         * a tuple containing attempts to pickle the following optional
           functions, in the order below
           * eval_f
           * evalf_f
           * conjugate_f
           * real_part_f
           * imag_part_f
           * derivative_f
           * power_f
           * series_f
           * print_f
           * print_latex_f

        EXAMPLES::

            sage: foo = function("foo", nargs=2)
            sage: foo.__getstate__()
            (1, 'foo', 2, None, {}, [None, None, None, None, None, None, None, None, None, None])
            sage: t = loads(dumps(foo))
            sage: t == foo
            True
            sage: var('x,y')
            (x, y)
            sage: t(x,y)
            foo(x, y)

            sage: def ev(self, x,y): return 2*x
            sage: foo = function("foo", nargs=2, eval_func = ev)
            sage: foo.__getstate__()
            (1, 'foo', 2, None, {}, ["...", None, None, None, None, None, None, None, None, None])

            sage: u = loads(dumps(foo))
            sage: u == foo
            True
            sage: t == u
            False
            sage: u(y,x)
            2*y

            sage: def evalf_f(self, x, parent=None): return int(6)
            sage: foo = function("foo", nargs=1, evalf_func=evalf_f)
            sage: foo.__getstate__()
            (1, 'foo', 1, None, {}, [None, "...", None, None, None, None, None, None, None, None])

            sage: v = loads(dumps(foo))
            sage: v == foo
            True
            sage: v == u
            False
            sage: foo(y).n()
            6
            sage: v(y).n()
            6

        Test pickling expressions with symbolic functions::

            sage: u = loads(dumps(foo(x)^2 + foo(y) + x^y)); u
            x^y + foo(x)^2 + foo(y)
            sage: u.subs(y=0)
            foo(x)^2 + foo(0) + 1
            sage: u.subs(y=0).n()
            43.0000000000000
        """
        return (1, self._name, self._nargs, self._latex_name, self._conversions,
                map(pickle_wrapper, [getattr(self, '_%s_'%fname) \
                        if hasattr(self, '_%s_'%fname) else None \
                        for fname in sfunctions_funcs]))

    def __setstate__(self, state):
        """
        Initializes the state of the object from data saved in a pickle.

        During unpickling __init__ methods of classes are not called, the saved
        data is passed to the class via this function instead.

        TESTS::

            sage: var('x,y')
            (x, y)
            sage: foo = function("foo", nargs=2)
            sage: bar = function("bar", nargs=1)
            sage: bar.__setstate__(foo.__getstate__())

        ::

            sage: g = function('g', nargs=1, conjugate_func=lambda y,x: 2*x)
            sage: st = g.__getstate__()
            sage: f = function('f')
            sage: f(x)
            f(x)
            sage: f(x).conjugate() # no special conjugate method
            conjugate(f(x))
            sage: f.__setstate__(st)
            sage: f(x+1).conjugate() # now there is a special method
            2*x + 2

        Note that the other direction doesn't work here, since foo._hash_()
        hash already been initialized.::

            sage: bar
            foo
            sage: bar(x,y)
            foo(x, y)
        """
        # check input
        if state[0] == 1 and len(state) == 6:
            name = state[1]
            nargs = state[2]
            latex_name = state[3]
            conversions = state[4]
            for pickle, fname in zip(state[5], sfunctions_funcs):
                if pickle:
                    real_fname = '_%s_'%fname
                    setattr(self, real_fname, unpickle_function(pickle))
            SymbolicFunction.__init__(self, name, nargs, latex_name,
                    conversions)
        else:
            raise ValueError, "unknown state information"


cdef class DeprecatedSFunction(SymbolicFunction):
    cdef dict __dict__
    def __init__(self, name, nargs=0, latex_name=None):
        """
        EXAMPLES::

            sage: from sage.symbolic.function import DeprecatedSFunction
            sage: foo = DeprecatedSFunction("foo", 2)
            sage: foo
            foo
            sage: foo(x,2)
            foo(x, 2)
            sage: foo(2)
            Traceback (most recent call last):
            ...
            TypeError: Symbolic function foo takes exactly 2 arguments (1 given)
        """
        self.__dict__ = {}
        SymbolicFunction.__init__(self, name, nargs, latex_name)

    def __getattr__(self, attr):
        """
        This method allows us to access attributes set by
        :meth:`__setattr__`.

        EXAMPLES::

            sage: from sage.symbolic.function import DeprecatedSFunction
            sage: foo = DeprecatedSFunction("foo", 2)
            sage: foo.bar = 4
            sage: foo.bar
            4
        """
        try:
            return self.__dict__[attr]
        except KeyError:
            raise AttributeError, attr

    def __setattr__(self, attr, value):
        """
        This method allows us to store arbitrary Python attributes
        on symbolic functions which is normally not possible with
        Cython extension types.

        EXAMPLES::

            sage: from sage.symbolic.function import DeprecatedSFunction
            sage: foo = DeprecatedSFunction("foo", 2)
            sage: foo.bar = 4
            sage: foo.bar
            4
        """
        self.__dict__[attr] = value

    def __reduce__(self):
        """
        EXAMPLES::

            sage: from sage.symbolic.function import DeprecatedSFunction
            sage: foo = DeprecatedSFunction("foo", 2)
            sage: foo.__reduce__()
            (<function unpickle_function at ...>, ('foo', 2, None, {}, [None, None, None, None, None, None, None, None, None, None]))
        """
        from sage.symbolic.function_factory import unpickle_function
        state = self.__getstate__()
        name = state[1]
        nargs = state[2]
        latex_name = state[3]
        conversions = state[4]
        pickled_functions = state[5]
        return (unpickle_function, (name, nargs, latex_name, conversions,
            pickled_functions))

    def __setstate__(self, state):
        """
        EXAMPLES::

            sage: from sage.symbolic.function import DeprecatedSFunction
            sage: foo = DeprecatedSFunction("foo", 2)
            sage: foo.__setstate__([0, 'bar', 1, '\\bar', [None]*10])
            sage: foo
            bar
            sage: foo(x)
            bar(x)
            sage: latex(foo(x))
            \bar\left(x\right)
        """
        name = state[1]
        nargs = state[2]
        latex_name = state[3]
        self.__dict__ = {}
        for pickle, fname in zip(state[4], sfunctions_funcs):
            if pickle:
                if fname == 'evalf':
                    from sage.symbolic.function_factory import \
                            deprecated_custom_evalf_wrapper
                    setattr(self, '_evalf_',
                            deprecated_custom_evalf_wrapper(
                                unpickle_function(pickle)))
                    continue
                real_fname = '_%s_'%fname
                setattr(self, real_fname, unpickle_function(pickle))

        SymbolicFunction.__init__(self, name, nargs, latex_name, None)

SFunction = DeprecatedSFunction
PrimitiveFunction = DeprecatedSFunction


def get_sfunction_from_serial(serial):
    """
    Returns an already created SFunction given the serial.  These are
    stored in the dictionary
    :obj:`sage.symbolic.function.sfunction_serial_dict`.

    EXAMPLES::

        sage: from sage.symbolic.function import get_sfunction_from_serial
        sage: get_sfunction_from_serial(65) #random
        f
    """
    global sfunction_serial_dict
    return sfunction_serial_dict.get(serial)

def pickle_wrapper(f):
    """
    Returns a pickled version of the function f if f is not None;
    otherwise, it returns None.  This is a wrapper around
    :func:`pickle_function`.

    EXAMPLES::

        sage: from sage.symbolic.function import pickle_wrapper
        sage: def f(x): return x*x
        sage: pickle_wrapper(f)
        "csage...."
        sage: pickle_wrapper(None) is None
        True
    """
    if f is None:
        return None
    return pickle_function(f)

def unpickle_wrapper(p):
    """
    Returns a unpickled version of the function defined by *p* if *p*
    is not None; otherwise, it returns None.  This is a wrapper around
    :func:`unpickle_function`.

    EXAMPLES::

        sage: from sage.symbolic.function import pickle_wrapper, unpickle_wrapper
        sage: def f(x): return x*x
        sage: s = pickle_wrapper(f)
        sage: g = unpickle_wrapper(s)
        sage: g(2)
        4
        sage: unpickle_wrapper(None) is None
        True
    """
    if p is None:
        return None
    return unpickle_function(p)
