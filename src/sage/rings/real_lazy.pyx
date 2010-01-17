"""
These classes are very lazy, in the sense that it doesn't really do anything
but simply sits between exact rings of characteristic 0 and the real numbers.
The values are actually computed when they are cast into a field of fixed
precision.

The main purpose of these classes is to provide a place for exact rings (e.g.
number fields) to embed for the coercion model (as only one embedding can be
specified in the forward direction.
"""

#*****************************************************************************
#     Copyright (C) 2008 Robert Bradshaw <robertwb@math.washington.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import math

cdef add, sub, mul, div, pow, neg, inv
from operator import add, sub, mul, div, pow, neg, inv

cdef canonical_coercion
from sage.structure.element import canonical_coercion

include "../ext/stdsage.pxi"

from sage.categories.morphism cimport Morphism
from sage.rings.ring cimport Field
import sage.rings.infinity
from sage.rings.integer import Integer

cdef QQ, RR, CC, RealField, ComplexField
from sage.rings.rational_field import QQ
from sage.rings.real_mpfr import RR, RealField
from sage.rings.complex_field import ComplexField
CC = ComplexField(53)

cdef _QQx = None

cdef QQx():
    global _QQx
    if _QQx is None:
        _QQx = QQ['x']
    return _QQx

cdef named_unops = [ 'sqrt', 'erf', 'gamma',
                     'floor', 'ciel', 'trunc',
                     'exp', 'log', 'log10', 'log2',
                     'sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan',
                     'csc', 'sec', 'cot',
                     'sinh', 'cosh', 'tanh', 'arcsinh', 'arccosh', 'arctanh' ]

cdef named_constants = [ 'pi', 'e',
                         'euler_constant', 'catalan_constant' ]

cdef class LazyField(Field):
    """
    The base class for lazy real fields.
    """
    def __getattr__(self, name):
        """
        Simulates a list of methods found on the real/complex rings.

        EXAMPLES:
            sage: a = CLF.pi() * CLF.I(); a
            3.141592653589794?*I
            sage: CDF(a)
            3.14159265359*I
        """
        if name in named_constants:
            return LazyConstant(self, name)
        elif name == 'I' and self == CLF:
            return LazyConstant(self, name)
        else:
            raise AttributeError, name

    cpdef _coerce_map_from_(self, R):
        r"""
        The only things that coerce into this ring are exact rings that
        embed into $\R$ or $\C$ (depending on whether or not this field
        is real or complex).

        EXAMPLES:
            sage: RLF.has_coerce_map_from(ZZ)
            True
            sage: RLF.has_coerce_map_from(QQ)
            True
            sage: RLF.has_coerce_map_from(AA)
            True
            sage: CLF.has_coerce_map_from(QQbar)
            True
            sage: RLF.has_coerce_map_from(RDF)
            False

            sage: CLF.has_coerce_map_from(QQ)
            True
            sage: CLF.has_coerce_map_from(QQbar)
            True
            sage: CLF.has_coerce_map_from(CC)
            False
            sage: CLF.has_coerce_map_from(RLF)
            True
        """
        if isinstance(R, type):
            if R in [int, long]:
                from sage.structure.parent import Set_PythonType
                return LazyWrapperMorphism(Set_PythonType(R), self)
        elif self.interval_field().has_coerce_map_from(R) and R.is_exact():
            return LazyWrapperMorphism(R, self)

    def algebraic_closure(self):
        """
        Returns the algebraic closure of self,
        ie, the complex lazy field.

        EXAMPLES:
            sage: RLF.algebraic_closure()
            Complex Lazy Field

            sage: CLF.algebraic_closure()
            Complex Lazy Field
        """
        return CLF

    cpdef interval_field(self, prec=None):
        raise NotImplementedError, "subclasses must override this method"


cdef class RealLazyField_class(LazyField):
    """
    This class represents the set of real numbers to unspecified precision.
    For the most part it simply wraps exact elements and defers evaluation
    until a specified precision is requested.

    It's primary use is to connect the exact rings (such as number fields) to
    fixed precision real numbers. For example, to specify an embedding of a
    number field $K$ into $\RR$ one can map into this field and the
    coercion will then be able to carry the mapping to real fields of any
    precision.

    EXAMPLES:
        sage: a = RLF(1/3)
        sage: a
        0.3333333333333334?
        sage: a + 1/5
        0.5333333333333334?
        sage: a = RLF(1/3)
        sage: a
        0.3333333333333334?
        sage: a + 5
        5.333333333333334?
        sage: RealField(100)(a+5)
        5.3333333333333333333333333333
    """

    def __init__(self):
        """
        EXAMPLES:
            sage: CC.0 + RLF(1/3)
            0.333333333333333 + 1.00000000000000*I
            sage: ComplexField(200).0 + RLF(1/3)
            0.33333333333333333333333333333333333333333333333333333333333 + 1.0000000000000000000000000000000000000000000000000000000000*I
        """
        self._populate_coercion_lists_(element_constructor=LazyWrapper)

    cpdef interval_field(self, prec=None):
        """
        Returns the interval field that represents the same mathematical
        field as self.

        EXAMPLES:
            sage: RLF.interval_field()
            Real Interval Field with 53 bits of precision
            sage: RLF.interval_field(200)
            Real Interval Field with 200 bits of precision
        """
        from sage.rings.real_mpfi import RIF, RealIntervalField
        if prec is None:
            return RIF
        else:
            return RealIntervalField(prec)

    def construction(self):
        """
        Returns the functorial construction of self, namely,
        the completion of the rationals at infinity to infinite
        precision.

        EXAMPLES:
            sage: c, S = RLF.construction(); S
            Rational Field
            sage: RLF == c(S)
            True
        """
        from sage.categories.pushout import CompletionFunctor
        return CompletionFunctor(sage.rings.infinity.Infinity,
                                 sage.rings.infinity.Infinity,
                                 {'type': 'RLF'}), QQ

    def _latex_(self):
        r"""
        EXAMPLES:
            sage: latex(RLF)
            \Bold{R}
        """
        return "\\Bold{R}"

    def gen(self, i=0):
        """
        EXAMPLES:
            sage: RLF.gen()
            1
        """
        if i == 0:
            return self(Integer(1))
        else:
            raise ValueError, "RLF has only one generator."

    def __repr__(self):
        """
        EXAMPLES:
            sage: RealLazyField()
            Real Lazy Field
        """
        return "Real Lazy Field"

    def __hash__(self):
        """
        EXAMPLES:
            sage: hash(RLF) % 2^32 == hash(str(RLF)) % 2^32
            True
        """
        return 1501555429

    def __reduce__(self):
        """
        TESTS:
            sage: RLF == loads(dumps(RLF))
            True
            sage: RLF is loads(dumps(RLF))
            True
        """
        return RealLazyField, ()


RLF = RealLazyField_class()

def RealLazyField():
    """
    Returns the lazy real field.

    EXAMPLES:
    There is only one lazy real field.
        sage: RealLazyField() is RealLazyField()
        True
    """
    return RLF


cdef class ComplexLazyField_class(LazyField):
    """
    This class represents the set of real numbers to unspecified precision.
    For the most part it simply wraps exact elements and defers evaluation
    until a specified precision is requested.

    For more information, see the documentation of the RLF.

    EXAMPLES:
        sage: a = CLF(-1).sqrt()
        sage: a
        1*I
        sage: CDF(a)
        1.0*I
        sage: ComplexField(200)(a)
        1.0000000000000000000000000000000000000000000000000000000000*I
    """

    def __init__(self):
        """
        This lazy field doesn't evaluate its elements until they are cast into
        a field of fixed precision.

        EXAMPLES:
            sage: a = RLF(1/3); a
            0.3333333333333334?
            sage: Reals(200)(a)
            0.33333333333333333333333333333333333333333333333333333333333
        """
        LazyField.__init__(self, base=RLF)
        self._populate_coercion_lists_(coerce_list=[LazyWrapperMorphism(RLF, self)], element_constructor=LazyWrapper)

    cpdef interval_field(self, prec=None):
        """
        Returns the interval field that represents the same mathematical
        field as self.

        EXAMPLES:
            sage: CLF.interval_field()
            Complex Interval Field with 53 bits of precision
            sage: CLF.interval_field(333)
            Complex Interval Field with 333 bits of precision
            sage: CLF.interval_field() is CIF
            True
        """
        from sage.rings.all import CIF, ComplexIntervalField
        if prec is None:
            return CIF
        else:
            return ComplexIntervalField(prec)

    def gen(self, i=0):
        """
        EXAMPLES:
            sage: CLF.gen()
            1*I
            sage: ComplexField(100)(CLF.gen())
            1.0000000000000000000000000000*I
        """
        if i == 0:
            from sage.rings.complex_double import CDF
            return LazyAlgebraic(self, [1, 0, 1], CDF.gen())
        else:
            raise ValueError, "CLF has only one generator."

    def construction(self):
        """
        Returns the functorial construction of self, namely,
        algebraic closure of the real lazy field.

        EXAMPLES:
            sage: c, S = CLF.construction(); S
            Real Lazy Field
            sage: CLF == c(S)
            True
        """
        from sage.categories.pushout import AlgebraicClosureFunctor
        return (AlgebraicClosureFunctor(), RLF)

    def _latex_(self):
        r"""
        EXAMPLES:
            sage: latex(CLF)
            \Bold{C}
        """
        return "\\Bold{C}"

    def __repr__(self):
        """
        EXAMPLES:
            sage: CLF
            Complex Lazy Field
        """
        return "Complex Lazy Field"

    def __hash__(self):
        """
        EXAMPLES:
            sage: hash(CLF) % 2^32 == hash(str(CLF)) % 2^32
            True
        """
        return -1382606040

    def __reduce__(self):
        """
        TESTS:
            sage: CLF == loads(dumps(CLF))
            True
            sage: CLF is loads(dumps(CLF))
            True
        """
        return ComplexLazyField, ()


CLF = ComplexLazyField_class()

def ComplexLazyField():
    """
    Returns the lazy complex field.

    EXAMPLES:
    There is only one lazy complex field.
        sage: ComplexLazyField() is ComplexLazyField()
        True
    """
    return CLF



cdef int get_new_prec(R, int depth) except -1:
    """
    There are depth operations, so we want at least that many more digits of
    precision.

    Field creation may be expensive, so we want to avoid incrementing by 1 so
    that it is more likely for cached fields to be used.
    """
    cdef int needed_prec = R.prec()
    needed_prec += depth
    if needed_prec % 10 != 0:
        needed_prec += 10 - needed_prec % 10
    return needed_prec


cdef class LazyFieldElement(FieldElement):

    cpdef ModuleElement _add_(left, ModuleElement right):
        """
        EXAMPLES:
            sage: RLF(5) + RLF(1/2)
            5.5000000000000000?
        """
        if PY_TYPE_CHECK(left, LazyWrapper) and PY_TYPE_CHECK(right, LazyWrapper):
            try:
                return left._new_wrapper((<LazyWrapper?>left)._value + (<LazyWrapper?>right)._value)
            except TypeError:
                pass
        return left._new_binop(left, right, add)

    cpdef ModuleElement _sub_(left, ModuleElement right):
        """
        EXAMPLES:
            sage: CLF(5)-2
            3
        """
        if PY_TYPE_CHECK(left, LazyWrapper) and PY_TYPE_CHECK(right, LazyWrapper):
            try:
                return left._new_wrapper((<LazyWrapper?>left)._value - (<LazyWrapper?>right)._value)
            except TypeError:
                pass
        return left._new_binop(left, right, sub)

    cpdef RingElement _mul_(left, RingElement right):
        """
        EXAMPLES:
            sage: CLF(10) * RLF(5)
            50
        """
        if PY_TYPE_CHECK(left, LazyWrapper) and PY_TYPE_CHECK(right, LazyWrapper):
            try:
                return left._new_wrapper((<LazyWrapper?>left)._value * (<LazyWrapper?>right)._value)
            except TypeError:
                pass
        return left._new_binop(left, right, mul)

    cpdef RingElement _div_(left, RingElement right):
        """
        EXAMPLES:
            sage: a = RLF(1) / RLF(6); a
            0.1666666666666667?
            sage: Reals(300)(a)
            0.166666666666666666666666666666666666666666666666666666666666666666666666666666666666666667
        """
        if PY_TYPE_CHECK(left, LazyWrapper) and PY_TYPE_CHECK(right, LazyWrapper):
            try:
                return left._new_wrapper((<LazyWrapper?>left)._value / (<LazyWrapper?>right)._value)
            except TypeError:
                pass
        return left._new_binop(left, right, div)

    def __pow__(left, right, dummy):
        """
        EXAMPLES:
            sage: a = RLF(2) ^ (1/2); a
            1.414213562373095?
            sage: Reals(300)(a)
            1.41421356237309504880168872420969807856967187537694807317667973799073247846210703885038753
        """
        if PY_TYPE_CHECK(left, LazyWrapper) and PY_TYPE_CHECK(right, LazyWrapper):
            try:
                return left._new_wrapper((<LazyWrapper>left)._value ** (<LazyWrapper>right)._value)
            except TypeError:
                pass
        if not PY_TYPE_CHECK(left, LazyFieldElement):
            left = (<LazyFieldElement>right)._new_wrapper(left)
        elif not PY_TYPE_CHECK(right, LazyFieldElement):
            right = (<LazyFieldElement>left)._new_wrapper(right)
        return (<LazyFieldElement>left)._new_binop(left, right, pow)

    def __neg__(self):
        """
        EXAMPLES:
            sage: -RLF(7)
            -7
        """
        return self._new_unop(self, neg)

    def __invert__(self):
        """
        EXAMPLES
          sage: a = ~RLF(6); a
          0.1666666666666667?
          sage: Reals(90)(a)
          0.16666666666666666666666667
        """
        return self._new_unop(self, inv)

    cdef int _cmp_c_impl(self, Element other) except -2:
        """
        If things are being wrapped, tries to compare values. That failing, it
        tries to compare intervals, which may return a false negative.

        EXAMPLES:
            sage: RLF(3) == RLF(9/3)
            True
            sage: RLF(3) == RLF(4)
            False
        """
        left = self
        try:
            if PY_TYPE_CHECK(self, LazyWrapper) and PY_TYPE_CHECK(other, LazyWrapper):
                left, right = canonical_coercion((<LazyWrapper>self)._value, (<LazyWrapper>other)._value)
                return cmp(left, right)
        except TypeError:
            pass
        left, right = self.approx(), other.approx()
        return cmp(left, right)


    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    def __hash__(self):
        """
        EXAMPLES:
            sage: a = RLF(3)
            sage: hash(a)
            3
        """
        return hash(complex(self))

    cdef LazyFieldElement _new_wrapper(self, value):
        cdef LazyWrapper e = <LazyWrapper>PY_NEW(LazyWrapper)
        e._parent = self._parent
        e._value = value
        return e

    cdef LazyFieldElement _new_binop(self, LazyFieldElement left, LazyFieldElement right, op):
        cdef LazyBinop e = <LazyBinop>PY_NEW(LazyBinop)
        e._parent = self._parent
        e._left = left
        e._right = right
        e._op = op
        return e

    cdef LazyFieldElement _new_unop(self, LazyFieldElement arg, op):
        cdef LazyUnop e = <LazyUnop>PY_NEW(LazyUnop)
        e._parent = self._parent
        e._op = op
        e._arg = arg
        return e

    def _repr_(self):
        """
        The string representation of self is an interval in which self is contained.

        EXAMPLES:
            sage: RLF(3)
            3
            sage: RLF(1/3)
            0.3333333333333334?
        """
        return str(self.approx())

    def approx(self):
        """
        Returns self as an element of an interval field.

        EXAMPLES:
            sage: CLF(1/6).approx()
            0.1666666666666667?
            sage: CLF(1/6).approx().parent()
            Complex Interval Field with 53 bits of precision
        """
        return self.eval(self._parent.interval_field())

    def _real_double_(self, R):
        """
        EXAMPLES:
            sage: a = RLF(3)
            sage: RDF(a)
            3.0
        """
        return self.eval(R)

    def _complex_double_(self, R):
        """
        EXAMPLES:
            sage: a = RLF(5)
            sage: CDF(a)
            5.0
            sage: a = CLF(-1)^(1/4)
            sage: CDF(a)
            0.707106781187 + 0.707106781187*I
        """
        return self.eval(R)

    def _generic_(self, R):
        """
        EXAMPLES:
            sage: a = RLF(2/3)
            sage: RR(a)
            0.666666666666667
            sage: RR(a^2)
            0.444444444444444
        """
        return self.eval(R)

    _mpfi_ = _mpfr_ = _complex_mpfr_field_ = _complex_mpfi_field_ = _generic_

    def __complex__(self):
        """
        EXAMPLES:
            sage: complex(CLF(-1)^(1/4))
            (0.707106781186547...+0.707106781186547...j)
        """
        try:
            return self.eval(complex)
        except:
            from complex_field import ComplexField
            return complex(self.eval(ComplexField(53)))

    cpdef eval(self, R):
        raise NotImplementedError, "Subclasses must override this method."

    cpdef int depth(self):
        raise NotImplementedError, "Subclasses must override this method."

    def __getattr__(self, name):
        """
        Simulates a list of methods found on the real/complex mpfr classes.

        EXAMPLES:
            sage: a = RLF(3)
            sage: a.sqrt()
            1.732050807568878?
            sage: sin(a)
            0.1411200080598673?
            sage: RealField(160)(tanh(RLF(3)))
            0.99505475368673045133188018525548847509781385470
        """
        if name in named_unops:
            return LazyNamedUnop(self._parent, self, name)
        else:
            raise AttributeError, name


def make_element(parent, *args):
    """
    EXAMPLES:
        sage: a = RLF(pi) + RLF(sqrt(1/2))
        sage: loads(dumps(a)) == a
        True
    """
    return parent(*args)

cdef class LazyWrapper(LazyFieldElement):

    cpdef int depth(self):
        """
        Returns the depth of self as an expression, which is always 0.

        EXAMPLES:
            sage: RLF(4).depth()
            0
        """
        return 0

    def __init__(self, LazyField parent, value, check=True):
        """
        A lazy element that simply wraps an element of another ring.

        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyWrapper
            sage: a = LazyWrapper(RLF, 3)
            sage: a._value
            3
        """
        FieldElement.__init__(self, parent)
        self._value = value
        if check:
            self._parent.interval_field()(value)

    def __neg__(self):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyWrapper
            sage: a = LazyWrapper(RLF, 3)
            sage: (-a)._value
            -3
        """
        return self._new_wrapper(-self._value)

    def __invert__(self):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyWrapper
            sage: a = LazyWrapper(RLF, 23)
            sage: ~a
            0.04347826086956522?
            sage: (~a)._value
            1/23
        """
        return self._new_wrapper(~self._value)

    def __float__(self):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyWrapper
            sage: a = LazyWrapper(CLF, 19)
            sage: float(a)
            19.0
        """
        return <double>self._value

    def __nonzero__(self):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyWrapper
            sage: not LazyWrapper(RLF, 1)
            False
            sage: not LazyWrapper(RLF, 0)
            True
        """
        return not not self._value

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    def __hash__(self):
        """
        EXAMPLES:
            sage: hash(CLF(-1))
            -2
            sage: hash(RLF(9/4)) == hash(9/4)
            True
        """
        return hash(self._value)

    cpdef eval(self, R):
        """
        Convert self into an element of R.

        EXAMPLES:
            sage: a = RLF(12)
            sage: a.eval(ZZ)
            12
            sage: a.eval(ZZ).parent()
            Integer Ring
        """
        return R(self._value)

    def __reduce__(self):
        """
        TESTS:
            sage: a = RLF(2)
            sage: loads(dumps(a)) == a
            True
        """
        return make_element, (self._parent, self._value)



cdef class LazyBinop(LazyFieldElement):

    def __init__(self, LazyField parent, left, right, op):
        """
        A lazy element representing a binary (usually arithmetic) operation
        between two other lazy elements.

        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyBinop
            sage: a = LazyBinop(RLF, 2, 1/3, operator.add)
            sage: a
            2.333333333333334?
            sage: Reals(200)(a)
            2.3333333333333333333333333333333333333333333333333333333333
        """
        FieldElement.__init__(self, parent)
        if not PY_TYPE_CHECK(left, LazyFieldElement):
            left = self._new_wrapper(left)
        if not PY_TYPE_CHECK(right, LazyFieldElement):
            right = self._new_wrapper(right)
        self._left = left
        self._right = right
        self._op = op

    cpdef int depth(self):
        """
        Return the depth of self as an arithmetic expression. This is the
        maximum number of dependent intermediate expressions when evaluating
        self, and is used to determine the precision needed to get the
        final result to the desired number of bits.

        It is equal to the maximum of the right and left depths, plus one.

        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyBinop
            sage: a = LazyBinop(RLF, 6, 8, operator.mul)
            sage: a.depth()
            1
            sage: b = LazyBinop(RLF, 2, a, operator.sub)
            sage: b.depth()
            2
        """
        cdef int left = self._left.depth()
        cdef int right = self._right.depth()
        return 1 + (left if left > right else right)

    cpdef eval(self, R):
        """
        Convert the operands to elements of R, then perform the operation on them.

        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyBinop
            sage: a = LazyBinop(RLF, 6, 8, operator.add)
            sage: a.eval(RR)
            14.0000000000000

        A bit absurd:
            sage: a.eval(str)
            '68'
        """
        left = self._left.eval(R)
        right = self._right.eval(R)
        if self._op is add:
            return left + right
        elif self._op is mul:
            return left * right
        elif self._op is sub:
            return left - right
        elif self._op is div:
            return left / right
        elif self._op is pow:
            return left ** right
        else:
            # We only do a call after testing the above because it is a python call.
            return self._op(left, right)

    def __float__(self):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyBinop
            sage: a = LazyBinop(RLF, 3, 1/2, operator.sub)
            sage: float(a)
            2.5
            sage: type(float(a))
            <type 'float'>
        """
        cdef double left = self._left
        cdef double right = self._right
        if self._op is add:
            return left + right
        elif self._op is mul:
            return left * right
        elif self._op is sub:
            return left - right
        elif self._op is div:
            return left / right
        elif self._op is pow:
            return left ** right
        else:
            # We only do a call here because it is a python call.
            return self._op(left, right)

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    def __hash__(self):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyBinop
            sage: a = LazyBinop(RLF, 5, 1/2, operator.sub)
            sage: hash(a)
            2
        """
        return hash(self._op(hash(self._left), hash(self._right)))

    def __reduce__(self):
        """
        TEST:
            sage: from sage.rings.real_lazy import LazyBinop
            sage: a = LazyBinop(CLF, 3, 2, operator.div)
            sage: loads(dumps(a)) == a
            True
        """
        return make_element, (LazyBinop, self._parent, self._left, self._right, self._op)


cdef class LazyUnop(LazyFieldElement):

    def __init__(self, LazyField parent, arg, op):
        """
        Represents a unevaluated single function of one variable.

        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyUnop
            sage: a = LazyUnop(RLF, 3, sqrt); a
            1.732050807568878?
            sage: a._arg
            3
            sage: a._op
            <function sqrt at ...>
            sage: Reals(100)(a)
            1.7320508075688772935274463415
            sage: Reals(100)(a)^2
            3.0000000000000000000000000000
        """
        FieldElement.__init__(self, parent)
        if not PY_TYPE_CHECK(arg, LazyFieldElement):
            arg = self._new_wrapper(arg)
        self._op = op
        self._arg = arg

    cpdef int depth(self):
        """
        Return the depth of self as an arithmetic expression. This is the
        maximum number of dependent intermediate expressions when evaluating
        self, and is used to determine the precision needed to get the
        final result to the desired number of bits.

        It is equal to one more than the depth of its operand.

        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyUnop
            sage: a = LazyUnop(RLF, 3, sqrt)
            sage: a.depth()
            1
            sage: b = LazyUnop(RLF, a, sin)
            sage: b.depth()
            2
        """
        return 1 + self._arg.depth()

    cpdef eval(self, R):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyUnop
            sage: a = LazyUnop(RLF, 3, sqrt)
            sage: a.eval(ZZ)
            sqrt(3)
        """
        arg = self._arg.eval(R)
        if self._op is neg:
            return -arg
        elif self._op is inv:
            return ~arg
        return self._op(self._arg.eval(R))

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    def __hash__(self):
        """
        EXAMPLES:
            sage: hash(RLF(sin(1))) #random
            -1524677126
        """
        return hash(self._op(hash(self._arg)))

    def __float__(self):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyUnop
            sage: a = LazyUnop(RLF, 3, sqrt)
            sage: float(a)
            1.7320508075688772
        """
        return self._op(<double>self._arg)

    def __reduce__(self):
        """
        TESTS:
            sage: from sage.rings.real_lazy import LazyUnop
            sage: a = LazyUnop(RLF, 7, sqrt)
            sage: float(loads(dumps(a))) == float(a)
            True
        """
        return make_element, (LazyUnop, self._parent, self._arg, self._op)


cdef class LazyNamedUnop(LazyUnop):

    def __init__(self, LazyField parent, arg, op, extra_args=None):
        """
        This class is used to represent the many named methods attached to real
        numbers, and is instantiated by the __getattr__ method of LazyElements.

        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyNamedUnop
            sage: a = LazyNamedUnop(RLF, 1, 'arcsin')
            sage: RR(a)
            1.57079632679490
            sage: a = LazyNamedUnop(RLF, 9, 'log', extra_args=(3,))
            sage: RR(a)
            2.00000000000000
        """
        LazyUnop.__init__(self, parent, arg, op)
        if extra_args is not None and not PY_TYPE_CHECK(extra_args, tuple):
            raise TypeError, "extra args must be a tuple"
        self._extra_args = extra_args

    cpdef eval(self, R):
        """
        TESTS:
            sage: from sage.rings.real_lazy import LazyNamedUnop
            sage: a = LazyNamedUnop(RLF, 4, 'sqrt')
            sage: RR(a)
            2.00000000000000
            sage: a.sqrt()
            1.414213562373095?
            sage: RealField(212)(a)
            2.00000000000000000000000000000000000000000000000000000000000000
            sage: float(a)
            2.0

        Now for some extra arguments:
            sage: a = RLF(100)
            sage: a.log(10)
            2
            sage: float(a.log(10))
            2.0
        """
        arg = self._arg.eval(R)
        cdef bint has_extra_args = self._extra_args is not None and len(self._extra_args) > 0
        if PY_TYPE_CHECK_EXACT(R, type):
            f = getattr(math, self._op)
            if has_extra_args:
                return f(arg, *self._extra_args)
            else:
                return f(arg)
        else:
            f = getattr(arg, self._op)
            if has_extra_args:
                return f(*self._extra_args)
            else:
                return f()

    def approx(self):
        """
        Does something reasonable with functions that are not defined on the interval fields.

        TESTS:
            sage: from sage.rings.real_lazy import LazyNamedUnop
            sage: LazyNamedUnop(RLF, 8, 'sqrt')
            2.828427124746190?
        """
        try:
            return LazyUnop.approx(self)
        except AttributeError:
            # not everything defined on interval fields
            # this is less info though, but mostly just want to print it
            interval_field = self._parent.interval_field()
            return self.eval(interval_field._middle_field())

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    def __hash__(self):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyNamedUnop
            sage: a = LazyNamedUnop(RLF, 1, 'sin')
            sage: hash(a)
            2110729788
        """
        return hash(complex(self))

    def __float__(self):
        """
        TESTS:
            sage: from sage.rings.real_lazy import LazyNamedUnop
            sage: a = LazyNamedUnop(RLF, 1, 'sin')
            sage: float(a)
            0.8414709848078965
        """
        return self.eval(float)

    def __call__(self, *args):
        """
        TESTS:
            sage: a = RLF(32)
            sage: a.log(2)
            5
            sage: float(a.log(2))
            5.0

        What is going on here in the background is
            sage: from sage.rings.real_lazy import LazyNamedUnop
            sage: b = LazyNamedUnop(RLF, a, 'log')
            sage: b(2)
            5
            sage: b(2)._extra_args
            (2,)
        """
        self._extra_args = args
        return self

    def __reduce__(self):
        """
        TESTS:
            sage: from sage.rings.real_lazy import LazyNamedUnop
            sage: a = LazyNamedUnop(RLF, 1, 'sin')
            sage: float(loads(dumps(a))) == float(a)
            True
        """
        return make_element, (LazyNamedUnop, self._parent, self._arg, self._op, self._extra_args)

cdef class LazyConstant(LazyFieldElement):

    cdef readonly _name
    cdef readonly _extra_args
    cdef readonly bint _is_special

    def __init__(self, LazyField parent, name, extra_args=None):
        """
        This class represents a real or complex constant (such as pi or I).

        TESTS:
            sage: a = RLF.pi(); a
            3.141592653589794?
            sage: RealField(300)(a)
            3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482

            sage: from sage.rings.real_lazy import LazyConstant
            sage: a = LazyConstant(RLF, 'euler_constant')
            sage: RealField(200)(a)
            0.57721566490153286060651209008240243104215933593992359880577
        """
        LazyFieldElement.__init__(self, parent)
        self._name = name
        self._extra_args = extra_args
        self._is_special = name in ['e', 'I']

    cpdef eval(self, R):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyConstant
            sage: a = LazyConstant(RLF, 'e')
            sage: RDF(a)
            2.71828182846
            sage: a = LazyConstant(CLF, 'I')
            sage: CC(a)
            1.00000000000000*I
        """
        if self._is_special:
            if self._name == 'e':
                return R(1).exp()
            elif self._name == 'I':
                I = R.gen()
                if I*I < 0:
                    return I
                else:
                    raise TypeError, "The complex constant I is not in this real field."
        f = getattr(R, self._name)
        if self._extra_args is None:
            return f()
        else:
            return f(*self._extra_args)

    def __call__(self, *args):
        """
        TESTS:
            sage: CLF.I()
            1*I
            sage: CDF(CLF.I())
            1.0*I
        """
        self._extra_args = args
        return self

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    def __hash__(self):
        """
        TESTS:
            sage: from sage.rings.real_lazy import LazyConstant
            sage: a = LazyConstant(RLF, 'e')
            sage: hash(a)
            2141977644
        """
        return hash(complex(self))

    def __float__(self):
        """
        TESTS:
            sage: from sage.rings.real_lazy import LazyConstant
            sage: a = LazyConstant(RLF, 'pi')
            sage: float(a)
            3.1415926535897931
        """
        interval_field = self._parent.interval_field()
        return <double>self.eval(interval_field._middle_field())

    def __reduce__(self):
        """
        TESTS:
            sage: from sage.rings.real_lazy import LazyConstant
            sage: a = LazyConstant(RLF, 'pi')
            sage: float(loads(dumps(a))) == float(a)
            True
        """
        return make_element, (LazyConstant, self._parent, self._name, self._extra_args)


cdef class LazyAlgebraic(LazyFieldElement):

    cdef readonly _poly
    cdef readonly _root_approx
    cdef readonly int _prec
    cdef readonly _quadratic_disc
    cdef readonly _root

    def __init__(self, parent, poly, approx, int prec=0):
        r"""
        This represents an algebraic number, specified by a polynomial over
        \Q and a real or complex approximation.

        EXAMPLES:
            sage: x = polygen(QQ)
            sage: from sage.rings.real_lazy import LazyAlgebraic
            sage: a = LazyAlgebraic(RLF, x^2-2, 1.5)
            sage: a
            1.414213562373095?
        """
        LazyFieldElement.__init__(self, parent)
        self._poly = QQx()(poly)
        self._root = None
        if prec is None:
            prec = approx.parent().prec()
        self._prec = prec
        if self._poly.degree() == 2:
            c, b, a = self._poly.list()
            self._quadratic_disc = b*b - 4*a*c
        if isinstance(parent, RealLazyField_class):
            from sage.rings.real_double import RDF
            if len(self._poly.roots(RDF)) == 0:
                raise ValueError, "%s has no real roots" % self._poly
            approx = (RR if prec == 0 else RealField(prec))(approx)
        else:
            approx = (CC if prec == 0 else ComplexField(prec))(approx)
        self._root_approx = approx

    cpdef eval(self, R):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyAlgebraic
            sage: a = LazyAlgebraic(CLF, QQ['x'].cyclotomic_polynomial(7), 0.6+0.8*CC.0)
            sage: a
            0.6234898018587335? + 0.7818314824680299?*I
            sage: ComplexField(150)(a)
            0.62348980185873353052500488400423981063227473 + 0.78183148246802980870844452667405775023233452*I

            sage: a = LazyAlgebraic(CLF, QQ['x'].0^2-7, -2.0)
            sage: RR(a)
            -2.64575131106459
            sage: RR(a)^2
            7.00000000000000
        """
        if PY_TYPE_CHECK(R, type):
            if self._prec < 53:
                self.eval(self.parent().interval_field(64)) # up the prec
        elif self._prec < R.prec():
            # Carl Witty said:
            # Quadratic equation faster and more accurate than roots(),
            # but the current code doesn't do the right thing with interval
            # arithmetic (it returns a point interval) so it's being disabled
            # for now
#             if self._quadratic_disc is not None:
#                 c, b, a = self._poly.list()
#                 if self._root_approx.real() < -b/2*a:
#                     z = (-b - R(self._quadratic_disc).sqrt()) / (2*a)
#                 else:
#                     z = (-b + R(self._quadratic_disc).sqrt()) / (2*a)
#                 if z.parent() is not R:
#                     z = R(z)
#                 self._root_approx = z
#                 from sage.rings.complex_interval_field import is_IntervalField
#                 if is_IntervalField(R):
#                     self._root_approx = (self._root_approx.upper() + self._root_approx.lower()) / 2
#                 self._prec = R.prec()
#                 return R(self._root_approx)
            if self._root is None:
                # This could be done much more efficiently with newton iteration,
                # but will require some care to make sure we get the right root, and
                # to the correct precision.
                from sage.rings.qqbar import AA, QQbar
                roots = self._poly.roots(ring = AA if isinstance(self._parent, RealLazyField_class) else QQbar)
                best_root = roots[0][0]
                min_dist = abs(self._root_approx - best_root)
                for r, e in roots[1:]:
                    dist = abs(self._root_approx - r)
                    if dist < min_dist:
                        best_root = r
                        min_dist = dist
                self._root = best_root
        if self._root is not None:
            return R(self._root)

    def __float__(self):
        """
        TESTS:
            sage: x = polygen(QQ)
            sage: from sage.rings.real_lazy import LazyAlgebraic
            sage: a = LazyAlgebraic(RLF, x^3-10, 1.5)
            sage: float(a)
            2.154434690031883...
        """
        return self.eval(float)

    def __reduce__(self):
        """
        TESTS:
            sage: from sage.rings.real_lazy import LazyAlgebraic
            sage: a = LazyAlgebraic(RLF, x^2-2, 1.5)
            sage: float(loads(dumps(a))) == float(a)
            True
        """
        return make_element, (LazyAlgebraic, self._parent, self._poly, self._root_approx, self._prec)


cdef class LazyWrapperMorphism(Morphism):

    def __init__(self, domain, LazyField codomain):
        """
        This morphism coerces elements from anywhere into lazy rings
        by creating a wrapper element (as fast as possible).

        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyWrapperMorphism
            sage: f = LazyWrapperMorphism(QQ, RLF)
            sage: a = f(3); a
            3
            sage: type(a)
            <type 'sage.rings.real_lazy.LazyWrapper'>
            sage: a._value
            3
            sage: a._value.parent()
            Rational Field
        """
        from sage.categories.homset import Hom
        Morphism.__init__(self, Hom(domain, codomain))

    cpdef Element _call_(self, x):
        """
        EXAMPLES:
            sage: from sage.rings.real_lazy import LazyWrapperMorphism
            sage: f = LazyWrapperMorphism(QQ, CLF)
            sage: a = f(1/3); a
            0.3333333333333334?
            sage: type(a)
            <type 'sage.rings.real_lazy.LazyWrapper'>
            sage: Reals(100)(a)
            0.33333333333333333333333333333

        Note that it doesn't double-wrap lazy elements:
            sage: f = LazyWrapperMorphism(RLF, CLF)
            sage: x = RLF(20)
            sage: f(x)
            20
            sage: f(x)._value
            20
        """
        cdef LazyWrapper e = <LazyWrapper>PY_NEW(LazyWrapper)
        e._parent = self._codomain
        if PY_TYPE_CHECK_EXACT(x, LazyWrapper):
            e._value = (<LazyWrapper>x)._value
        else:
            e._value = x
        return e
