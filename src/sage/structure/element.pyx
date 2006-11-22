r"""
Elements

AUTHORS:
   -- David Harvey (2006-10-16): changed CommutativeAlgebraElement to derive
   from CommutativeRingElement instead of AlgebraElement
   -- David Harvey (2006-10-29): implementation and documentation of new
   arithmetic architecture
   -- William Stein (2006-11): arithmetic architecture -- pushing it through to completion.


\subsection{The Abstract Element Class Heierarchy}
This is the abstract class heierchary, i.e., these are all
abstract base classes.
\begin{verbatim}
SageObject
    Element
        ModuleElement
            AdditiveGroupElement

        MonoidElement
            MultiplicativeGroupElement

        RingElement
            CommutativeRingElement
                IntegralDomainElement
                    DedekindDomainElement
                        PrincipalIdealDomainElement
                            EuclideanDomainElement
            FieldElement
                FiniteFieldElement
            AlgebraElement   (note -- can't derive from module, since no multiple inheritence)
                CommutativeAlgebraElement
            InfinityElement
\end{verbatim}

\subsection{How to Define a New Element Class}
Elements typically define a method \code{_new_c}, e.g.,
\begin{verbatim}
    cdef _new_c(self, defining data):
        cdef FreeModuleElement_generic_dense x
        x = PY_NEW(FreeModuleElement_generic_dense)
        x._parent = self._parent
        x._entries = v
\end{verbatim}
that creates a new sibling very quickly from defining data
with assumed properties.

SAGE has a special system in place for handling arithmetic operations
for all Element subclasses. There are various rules that must be
followed by both arithmetic implementors and callers.

A quick summary for the impatient:
\begin{itemize}
 \item DO NOT OVERRIDE _add_c. EVER. THANKS.
 \item DO NOT CALL _add_c_impl DIRECTLY.
 \item To implement addition for a python class, override def _add_().
 \item To implement addition for a pyrex class, override cdef _add_c_impl().
 \item If you want to add x and y, whose parents you know are IDENTICAL,
   you may call _add_(x, y) (from python or pyrex) or _add_c(x, y) (from
   pyrex -- this will be faster). This will be the fastest way to guarantee
   that the correct implementation gets called. Of course you can still
   always use "x + y".
\end{itemize}

Now in more detail. The aims of this system are to provide (1) an efficient
calling protocol from both python and pyrex, (2) uniform coercion semantics
across SAGE, (3) ease of use, (4) readability of code.

We will take addition of RingElements as an example; all other operators
and classes are similar. There are four relevant functions.

{\bf def RingElement.__add__}

   This function is called by python or pyrex when the binary "+" operator
   is encountered. It ASSUMES that at least one of its arguments is a
   RingElement; only a really twisted programmer would violate this
   condition. It has a fast pathway to deal with the most common case
   where the arguments have the same parent. Otherwise, it uses the coercion
   module to work out how to make them have the same parent. After any
   necessary coercions have been performed, it calls _add_c to dispatch to
   the correct underlying addition implementation.

   Note that although this function is declared as def, it doesn't have the
   usual overheads associated with python functions (either for the caller
   or for __add__ itself). This is because python has optimised calling
   protocols for such special functions.

{\bf cdef RingElement._add_c}

   DO ***NOT*** OVERRIDE THIS FUNCTION.

   The two arguments to this function MUST have the SAME PARENT.
   Its return value MUST have the SAME PARENT as its arguments.

   If you want to add two objects from pyrex, and you know that their
   parents are the same object, you are encouraged to call this function
   directly, instead of using "x + y".

   This function dispatches to either _add_ or _add_c_impl as appropriate.
   It takes necessary steps to decide whether a pyrex implementation of
   _add_c_impl has been overridden by some python implementation of _add_.
   The code is optimised in favour of reaching _add_c_impl as soon as
   possible.

{\bf def RingElement._add_}

   This is the function you should override to implement addition in a
   python subclass of RingElement.

   WARNING: if you override this in a *pyrex* class, it won't get called.
   You should override _add_c_impl instead. It is especially important to
   keep this in mind whenever you move a class down from python to pyrex.

   The two arguments to this function are guaranteed to have the
   SAME PARENT. Its return value MUST have the SAME PARENT as its
   arguments.

   If you want to add two objects from python, and you know that their
   parents are the same object, you are encouraged to call this function
   directly, instead of using "x + y".

   The default implementation of this function is to call _add_c_impl,
   so if no-one has defined a python implementation, the correct pyrex
   implementation will get called.

{\bf cdef RingElement._add_c_impl}

   This is the function you should override to implement addition in a
   pyrex subclass of RingElement.

   The two arguments to this function are guaranteed to have the
   SAME PARENT. Its return value MUST have the SAME PARENT as its
   arguments.

   DO ***NOT*** CALL THIS FUNCTION DIRECTLY.

   (Exception: you know EXACTLY what you are doing, and you know exactly
   which implementation you are trying to call; i.e. you're not trying to
   write generic code. In particular, if you call this directly, your code
   will not work correctly if you run it on a python class derived from
   a pyrex class where someone has redefined _add_ in python.)

   The default implementation of this function is to raise a
   NotImplementedError, which will happen if no-one has supplied
   implementations of either _add_ or _add_c_impl.

"""


##################################################################
# Generic element, so all this functionality must be defined
# by any element.  Derived class must call __init__
##################################################################

include "../ext/cdefs.pxi"
include "../ext/stdsage.pxi"
include "../ext/python.pxi"

import operator

from sage.structure.parent      cimport Parent
from sage.structure.parent_base cimport ParentWithBase

# This classes uses element.pxd.  To add data members, you
# must change that file.

def make_element(_class, _dict, parent):
    """
    Used for unpickling Element objects (and subclasses).

    This should work for any Python class deriving from Element, as long
    as it doesn't implement some screwy __new__() method.

    See also Element.__reduce__().
    """
    new_object = _class.__new__(_class)
    new_object._set_parent(parent)
    new_object.__dict__ = _dict
    return new_object



def is_Element(x):
    """
    Return True if x is of type Element.

    EXAMPLES:
        sage: is_Element(2/3)
        True
        sage: is_Element(QQ^3)
        False
    """
    return IS_INSTANCE(x, Element)

cdef class Element(sage_object.SageObject):
    """
    Generic element of a structure. All other types of elements
    (RingElement, ModuleElement, etc) derive from this type.

    Subtypes must either call __init__() to set _parent, or may
    set _parent themselves if that would be more efficient.
    """

    def __init__(self, parent):
        r"""
        INPUT:
            parent -- a SageObject
        """
        self._parent = parent

    def _set_parent(self, parent):
        r"""
        INPUT:
            parent -- a SageObject
        """
        self._parent = parent

    cdef _set_parent_c(self, ParentWithBase parent):
        self._parent = parent

    def _repr_(self):
        return "Generic element of a structure"

    def __reduce__(self):
        return (make_element, (self.__class__, self.__dict__, self._parent))

    def __hash__(self):
        return hash(str(self))

    def _im_gens_(self, codomain, im_gens):
        """
        Return the image of self in codomain under the map that sends
        the images of the generators of the parent of self to the
        tuple of elements of im_gens.
        """
        raise NotImplementedError

    cdef base_extend_c(self, ParentWithBase R):
        if HAS_DICTIONARY(self):
            return self.base_extend(R)
        else:
            return self.base_extend_c_impl(R)

    cdef base_extend_c_impl(self, ParentWithBase R):
        cdef ParentWithBase V
        V = self._parent.base_extend(R)
        return (<Parent>V)._coerce_c(self)

    def base_extend(self, R):
        return self.base_extend_c_impl(R)

    def base_ring(self):
        """
        Returns the base ring of this element's parent (if that makes sense).
        """
        return self._parent.base_ring()

    def category(self):
        from sage.categories.category import Elements
        return Elements(self._parent)

    def parent(self, x=None):
        """
        Returns parent of this element; or, if the optional argument x is
        supplied, the result of coercing x into the parent of this element.
        """
        if x is None:
            return self._parent
        else:
            return self._parent(x)

    def __xor__(self, right):
        raise RuntimeError, "Use ** for exponentiation, not '^', which means xor\n"+\
              "in Python, and has the wrong precedence."

    def _coeff_repr(self, no_space=True):
        if self._is_atomic():
            s = str(self)
        else:
            s = "(%s)"%self
        if no_space:
            return s.replace(' ','')
        return s

    def _latex_coeff_repr(self):
        try:
            s = self._latex_()
        except AttributeError:
            s = str(self)
        if self._is_atomic():
            return s
        else:
            return "\\left(%s\\right)"%s

    def _is_atomic(self):
        if self._parent.is_atomic_repr():
            return True
        s = str(self)
        return PyBool_FromLong(s.find("+") == -1 and s.find("-") == -1 and s.find(" ") == -1)

    def is_zero(self):
        return PyBool_FromLong(self == self._parent(0))

    def _richcmp_(left, right, op):
        return left._richcmp(right, op)

    cdef _richcmp(left, right, int op):
        """
        Compare left and right.
        """
        cdef int r
        if not have_same_parent(left, right):
            try:
                _left, _right = canonical_coercion_c(left, right)
                r = cmp(_left, _right)
            except TypeError:
                r = cmp(type(left), type(right))
                if r == 0:
                    r = -1
        else:
            if HAS_DICTIONARY(left):   # fast check
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

    ####################################################################
    # For a derived Pyrex class, you **must** put the following in
    # your subclasses, in order for it to take advantage of the
    # above generic comparison code.  You must also define
    # _cmp_c_impl.
    # This is simply how Python works.
    #
    # For a *Python* class just define __cmp__ as always.
    # But note that when this get called you can assume that
    # both inputs have identical parents.
    ####################################################################
    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    cdef int _cmp_c_impl(left, Element right) except -2:
        ### For derived SAGEX code, you *MUST* ALSO COPY the __richcmp__ above
        ### into your class!!!  For Python code just use __cmp__.
        raise NotImplementedError, "BUG: sort algorithm for elements of type %s not implemented"%(type(left))

    def __cmp__(left, right):
        return left._cmp_c_impl(right)   # default

def is_ModuleElement(x):
    """
    Return True if x is of type ModuleElement.

    This is even faster than using isinstance inline.

    EXAMPLES:
        sage: is_ModuleElement(2/3)
        True
        sage: is_ModuleElement((QQ^3).0)
        True
        sage: is_ModuleElement('a')
        False
    """
    return IS_INSTANCE(x, ModuleElement)


cdef class ModuleElement(Element):
    """
    Generic element of a module.
    """
    ##################################################
    def is_zero(self):
        return PyBool_FromLong(self == self._parent(0))

    ##################################################
    # Addition
    ##################################################
    def __add__(left, right):
        """
        Top-level addition operator for ModuleElements.

        See extensive documentation at the top of element.pyx.
        """

        # Try fast pathway if they are both ModuleElements and the parents
        # match.

        # (We know at least one of the arguments is a ModuleElement. So if
        # their types are *equal* (fast to check) then they are both
        # ModuleElements. Otherwise use the slower test via PY_TYPE_CHECK.)
        if have_same_parent(left, right):
            return (<ModuleElement>left)._add_c(<ModuleElement>right)
        return bin_op_c(left, right, operator.add)

    cdef ModuleElement _add_c(left, ModuleElement right):
        """
        Addition dispatcher for ModuleElements.

        DO NOT OVERRIDE THIS FUNCTION.

        See extensive documentation at the top of element.pyx.
        """
        if HAS_DICTIONARY(left):   # fast check
            # TODO: this bit will be unnecessarily slow if someone derives
            # from the pyrex class *without* overriding _add_, since then
            # we'll be making an unnecessary python call to _add_, which will
            # end up in _add_c_impl anyway. There must be a simple way to
            # distinguish this situation. It's complicated because someone
            # can even override it at the instance level (without overriding
            # it in the class.)
            return left._add_(right)
        else:
            # Must be a pure Pyrex class.
            return left._add_c_impl(right)


    cdef ModuleElement _add_c_impl(left, ModuleElement right):
        """
        Pyrex classes should override this function to implement addition.
        DO NOT CALL THIS FUNCTION DIRECTLY.
        See extensive documentation at the top of element.pyx.
        """
        raise TypeError, arith_error_message(left, right, operator.add)


    def _add_(ModuleElement left, ModuleElement right):
        """
        Python classes should override this function to implement addition.

        See extensive documentation at the top of element.pyx.
        """
        return left._add_c_impl(right)

    ##################################################
    # Subtraction
    ##################################################

    def __sub__(left, right):
        """
        Top-level subtraction operator for ModuleElements.
        See extensive documentation at the top of element.pyx.
        """
        if have_same_parent(left, right):
            return (<ModuleElement>left)._sub_c(<ModuleElement>right)
        return bin_op_c(left, right, operator.sub)

    cdef ModuleElement _sub_c(left, ModuleElement right):
        """
        Subtraction dispatcher for ModuleElements.

        DO NOT OVERRIDE THIS FUNCTION.

        See extensive documentation at the top of element.pyx.
        """

        if HAS_DICTIONARY(left):   # fast check
            return left._sub_(right)
        else:
            # Must be a pure Pyrex class.
            return left._sub_c_impl(right)


    cdef ModuleElement _sub_c_impl(left, ModuleElement right):
        """
        Pyrex classes should override this function to implement subtraction.

        DO NOT CALL THIS FUNCTION DIRECTLY.

        See extensive documentation at the top of element.pyx.
        """
        # default implementation is to use the negation and addition
        # dispatchers:
        return left._add_c(right._neg_c())


    def _sub_(ModuleElement left, ModuleElement right):
        """
        Python classes should override this function to implement subtraction.

        See extensive documentation at the top of element.pyx.
        """
        return left._sub_c_impl(right)

    ##################################################
    # Negation
    ##################################################

    def __neg__(self):
        """
        Top-level negation operator for ModuleElements.
        See extensive documentation at the top of element.pyx.
        """
        # We ASSUME that self is a ModuleElement. No type checks.
        return (<ModuleElement>self)._neg_c()


    cdef ModuleElement _neg_c(self):
        """
        Negation dispatcher for ModuleElements.
        DO NOT OVERRIDE THIS FUNCTION.
        See extensive documentation at the top of element.pyx.
        """

        if HAS_DICTIONARY(self):   # fast check
            return self._neg_()
        else:
            # Must be a pure Pyrex class.
            return self._neg_c_impl()


    cdef ModuleElement _neg_c_impl(self):
        """
        Pyrex classes should override this function to implement negation.
        DO NOT CALL THIS FUNCTION DIRECTLY.
        See extensive documentation at the top of element.pyx.
        """
        # default implementation is to try multiplying by -1.
        return bin_op_c(-1, self, operator.mul)


    def _neg_(ModuleElement self):
        """
        Python classes should override this function to implement negation.

        See extensive documentation at the top of element.pyx.
        """
        return self._neg_c_impl()

    ##################################################
    # Module element multiplication (scalars, etc.)
    ##################################################
    def __mul__(left, right):
        return module_element_generic_multiply_c(left, right)

    cdef ModuleElement _multiply_by_scalar(self, right):
        # self * right,  where right need not be a ring element in the base ring
        # This does type checking and canonical coercion then calls _lmul_c_impl.
        if PY_TYPE_CHECK(right, Element) and (<Element>right)._parent is self._parent._base:
            # No coercion needed
            return self._lmul_c(right)
        else:
            # Otherwise we do an explicit canonical coercion.
            try:
                return self._lmul_c( self._parent._base._coerce_c(right) )
            except TypeError:
                # that failed -- try to base extend right then do the multiply:
                self = self.base_extend((<RingElement>right)._parent)
                return (<ModuleElement>self)._lmul_c(right)

    cdef ModuleElement _rmultiply_by_scalar(self, left):
        # left * self, where left need not be a ring element in the base ring
        # This does type checking and canonical coercion then calls _rmul_c_impl.
        if PY_TYPE_CHECK(left, Element) and (<Element>self)._parent is self._parent._base:
            # No coercion needed
            return self._rmul_c(right)
        else:
            # Otherwise we do an explicit canonical coercion.
            try:
                return self._rmul_c(self._parent._base._coerce_c(left))
            except TypeError:
                # that failed -- try to base extend self then do the multiply:
                self = self.base_extend((<RingElement>left)._parent)
                return (<ModuleElement>self)._rmul_c(left)

    cdef ModuleElement _lmul_nonscalar_c(left, right):
        # Compute the product left * right, where right is assumed to be a nonscalar (so no coercion)
        # This is a last resort.
        if HAS_DICTIONARY(left):
            return left._lmul_nonscalar(right)
        else:
            return left._lmul_nonscalar_c_impl(right)

    cdef ModuleElement _lmul_nonscalar_c_impl(left, right):
        raise TypeError

    def _lmul_nonscalar(left, right):
        return left._lmul_nonscalar_c_impl(right)

    cdef ModuleElement _rmul_nonscalar_c(right, left):
        if HAS_DICTIONARY(right):
            return right._rmul_nonscalar(left)
        else:
            return right._rmul_nonscalar_c_impl(left)

    cdef ModuleElement _rmul_nonscalar_c_impl(right, left):
        raise TypeError

    def _rmul_nonscalar(right, left):
        return right._rmul_nonscalar_c_impl(left)


    # rmul -- left * self
    cdef ModuleElement _rmul_c(self, RingElement left):
        """
        DO NOT OVERRIDE THIS FUNCTION.  OK to call.
        """
        if HAS_DICTIONARY(self):
            return self._rmul_(left)
        else:
            return self._rmul_c_impl(left)

    cdef ModuleElement _rmul_c_impl(self, RingElement left):
        """
        Default module left scalar multiplication, which is to try to
        canonically coerce the scalar to the integers and do that
        multiplication, which is always defined.
        """
        from sage.rings.all import ZZ
        n = (<Parent>ZZ)._coerce_c(left)
        a = self
        if n < 0:
            a = -a
            n = -n
        prod = self._parent(0)
        aprod = a
        while True:
            if n&1 > 0: prod = prod + aprod
            n = n >> 1
            if n != 0:
                aprod = aprod + aprod
            else:
                break
        return prod

    def _rmul_(self, left):
        return self._rmul_c_impl(left)


    # lmul -- self * right

    cdef ModuleElement _lmul_c(self, RingElement right):
        """
        DO NOT OVERRIDE THIS FUNCTION.
        """
        if HAS_DICTIONARY(self):
            return self._lmul_(right)
        else:
            return self._lmul_c_impl(right)

    cdef ModuleElement _lmul_c_impl(self, RingElement right):
        """
        Default module right scalar multiplication, which is to try to
        canonically coerce the scalar to the integers and do that
        multiplication, which is always defined.
        """
        return self._rmul_c(right)

    def _lmul_(self, right):
        return self._lmul_c_impl(right)


    cdef RingElement coerce_to_base_ring(self, x):
        if PY_TYPE_CHECK(x, Element) and (<Element>x)._parent is self._parent._base:
            return x
        try:
            return self._parent._base._coerce_c(x)
        except AttributeError:
            return self._parent._base(x)

    ##################################################
    # Other properties
    ##################################################
    def order(self):
        """
        Return the additive order of self.
        """
        return self.additive_order()

    def additive_order(self):
        """
        Return the additive order of self.
        """
        raise NotImplementedError

def module_element_generic_multiply(left, right):
    return module_element_generic_multiply_c(left, right)

cdef module_element_generic_multiply_c(left, right):
    cdef int is_element
    if PY_TYPE_CHECK(right, ModuleElement) and not PY_TYPE_CHECK(right, RingElement):
        # do left * (a module element right)
        is_element = PY_TYPE_CHECK(left, Element)
        if is_element  and  (<Element>left)._parent is (<ModuleElement>right)._parent._base:
            # No coercion needed
            return (<ModuleElement>right)._rmul_c(left)
        else:
            try:
                return (<ModuleElement>right)._rmul_nonscalar_c(left)
            except TypeError:
                pass
            # Otherwise we have to do an explicit canonical coercion.
            try:
                return (<ModuleElement>right)._rmul_c(
                    (<Parent>(<ModuleElement>right)._parent._base)._coerce_c(left))
            except TypeError:
                if is_element:
                    # that failed -- try to base extend right then do the multiply:
                    right = right.base_extend((<RingElement>left)._parent)
                    return (<ModuleElement>right)._rmul_c(left)
    else:
        # do (module element left) * right
        # This is the symmetric case of above.
        is_element = PY_TYPE_CHECK(right, Element)
        if is_element  and  (<Element>right)._parent is (<ModuleElement>left)._parent._base:
            # No coercion needed
            return (<ModuleElement>left)._lmul_c(right)
        else:
            try:
                return (<ModuleElement>left)._lmul_nonscalar_c(right)
            except TypeError:
                pass
            # Otherwise we have to do an explicit canonical coercion.
            try:
                return (<ModuleElement>left)._lmul_c(
                    (<Parent>(<ModuleElement>left)._parent._base)._coerce_c(right))
            except TypeError:
                if is_element:
                    # that failed -- try to base extend right then do the multiply:
                    left = left.base_extend((<RingElement>right)._parent)
                    return (<ModuleElement>left)._rmul_c(right)
    raise TypeError

########################################################################
# Monoid
########################################################################

def is_MonoidElement(x):
    """
    Return True if x is of type MonoidElement.
    """
    return IS_INSTANCE(x, MonoidElement)

cdef class MonoidElement(Element):
    """
    Generic element of a monoid.
    """

    #############################################################
    # Multiplication
    #############################################################
    def __mul__(left, right):
        """
        Top-level multiplication operator for ring elements.
        See extensive documentation at the top of element.pyx.
        """
        if have_same_parent(left, right):
            return (<MonoidElement>left)._mul_c(<MonoidElement>right)
        return bin_op_c(left, right, operator.mul)


    cdef MonoidElement _mul_c(left, MonoidElement right):
        """
        Multiplication dispatcher for RingElements.
        DO NOT OVERRIDE THIS FUNCTION.
        See extensive documentation at the top of element.pyx.
        """
        if HAS_DICTIONARY(left):   # fast check
            return left._mul_(right)
        else:
            return left._mul_c_impl(right)


    cdef MonoidElement _mul_c_impl(left, MonoidElement right):
        """
        Pyrex classes should override this function to implement multiplication.
        DO NOT CALL THIS FUNCTION DIRECTLY.
        See extensive documentation at the top of element.pyx.
        """
        raise TypeError

    def _mul_(left, right):
        return left._mul_c_impl(right)

    #############################################################
    # Other generic functions that should be available to
    # any monoid element.
    #############################################################
    def order(self):
        """
        Return the multiplicative order of self.
        """
        return self.multiplicative_order()

    def multiplicative_order(self):
        """
        Return the multiplicative order of self.
        """
        raise NotImplementedError

    def __pow__(self, n, dummy):
        cdef int i

        if PyFloat_Check(n):
            raise TypeError, "raising %s to the power of the float %s not defined"%(self, n)

        n = int(n)

        a = self
        power = self.parent()(1)
        if n < 0:
            n = -n
            a = ~self
        elif n == 0:
            return power

        power = (<Element>self)._parent(1)
        apow = a
        while True:
            if n&1 > 0: power = power*apow
            n = n >> 1
            if n != 0:
                apow = apow*apow
            else:
                break

        return power


def is_AdditiveGroupElement(x):
    """
    Return True if x is of type AdditiveGroupElement.
    """
    return IS_INSTANCE(x, AdditiveGroupElement)

cdef class AdditiveGroupElement(ModuleElement):
    """
    Generic element of an additive group.
    """
    def order(self):
        """
        Return additive order of element
        """
        return self.additive_order()

    def __invert__(self):
        raise NotImplementedError, "multiplicative inverse not defined for additive group elements"

    cdef ModuleElement _rmul_c_impl(self, RingElement left):
        return self._lmul_c_impl(left)

    cdef ModuleElement _lmul_c_impl(self, RingElement right):
        cdef int m
        m = int(right)  # a little worrisome.
        if m<0:
            return (-self)*(-m)
        if m==1:
            return self
        P = self.scheme()(0)
        if m==0:
            return P
        power = P
        i = 0
        apow2 = self
        while ((m>>i) > 0):
            if((m>>i) & 1):
                power = power + apow2
            apow2 = apow2 + apow2
            i = i + 1
        return power


def is_MultiplicativeGroupElement(x):
    """
    Return True if x is of type MultiplicativeGroupElement.
    """
    return IS_INSTANCE(x, MultiplicativeGroupElement)

cdef class MultiplicativeGroupElement(MonoidElement):
    """
    Generic element of a multiplicative group.
    """
    def order(self):
        """
        Return the multiplicative order of self.
        """
        return self.multiplicative_order()

    def _add_(self, x):
        raise ArithmeticError, "addition not defined in a multiplicative group"

    def __div__(left, right):
        if have_same_parents(left, right):
            return left._div_(right)
        return bin_op_c(left, right, operator.div)

    cdef MultiplicativeGroupElement _div_c(self, MultiplicativeGroupElement right):
        """
        Multiplication dispatcher for MultiplicativeGroupElements.
        DO NOT OVERRIDE THIS FUNCTION.
        See extensive documentation at the top of element.pyx.
        """
        if HAS_DICTIONARY(self):   # fast check
            return self._div_(right)
        else:
            return self._div_c_impl(right)

    cdef MultiplicativeGroupElement _div_c_impl(self, MultiplicativeGroupElement right):
        """
        Pyrex classes should override this function to implement division.
        DO NOT CALL THIS FUNCTION DIRECTLY.
        See extensive documentation at the top of element.pyx.
        """
        return self._parent.fraction_field()(self, right)

    def _div_(MultiplicativeGroupElement self, MultiplicativeGroupElement right):
        """
        Python classes should override this function to implement division.
        """
        return self._div_c_impl(right)


    def __invert__(self):
        return 1/self


def is_RingElement(x):
    """
    Return True if x is of type RingElement.
    """
    return IS_INSTANCE(x, RingElement)

cdef class RingElement(ModuleElement):
    ##################################################
    def is_zero(self):
        return PyBool_FromLong(self == self.parent()(0))

    def is_one(self):
        return PyBool_FromLong(self == self.parent()(1))

    ##################################
    # Multiplication
    ##################################

    def __mul__(self, right):
        """
        Top-level multiplication operator for ring elements.
        See extensive documentation at the top of element.pyx.
        """
        # Try fast pathway if they are both RingElements and the parents match.
        # (We know at least one of the arguments is a RingElement. So if their
        # types are *equal* (fast to check) then they are both RingElements.
        # Otherwise use the slower test via PY_TYPE_CHECK.)
        if have_same_parent(self, right):
            return (<RingElement>self)._mul_c(<RingElement>right)

        # VERY important special case:
        # (ring element) * (module element that is not a ring element)
        # We don't have to do the other direction, since it is
        # done in module element __mul__.
        if PY_TYPE_CHECK(right, ModuleElement) and not PY_TYPE_CHECK(right, RingElement):
            # Now self must be a ring element:
            # If the parent is the same as the base ring, good
            if (<RingElement>self)._parent is (<ModuleElement>right)._parent._base:
                return (<ModuleElement>right)._rmul_c(self)
            else:
                # Otherwise we have to do an explicit canonical coercion.
                try:
                    return (<ModuleElement>right)._rmul_c(
                        (<Parent>(<ModuleElement>right)._parent._base)._coerce_c(self))
                except TypeError:
                    # that failed -- try to base extend right then do the multiply:
                    right = right.base_extend((<RingElement>self)._parent)
                    return (<ModuleElement>right)._rmul_c(self)

        # General case.
        return bin_op_c(self, right, operator.mul)

    cdef RingElement _mul_c(self, RingElement right):
        """
        Multiplication dispatcher for RingElements.
        DO NOT OVERRIDE THIS FUNCTION.
        See extensive documentation at the top of element.pyx.
        """
        if HAS_DICTIONARY(self):   # fast check
            return self._mul_(right)
        else:
            return self._mul_c_impl(right)

    cdef RingElement _mul_c_impl(self, RingElement right):
        """
        Pyrex classes should override this function to implement multiplication.
        DO NOT CALL THIS FUNCTION DIRECTLY.
        See extensive documentation at the top of element.pyx.
        """
        raise TypeError, arith_error_message(self, right, operator.mul)

    def _mul_(RingElement self, RingElement right):
        """
        Python classes should override this function to implement multiplication.
        See extensive documentation at the top of element.pyx.
        """
        return self._mul_c_impl(right)


    ##################################
    # Division
    ##################################

    def __truediv__(self, right):
        # in sage all divs are true
        if not PY_TYPE_CHECK(self, Element):
            return bin_op_c(self, right, operator.div)
        return self.__div__(right)

    def __div__(self, right):
        """
        Top-level multiplication operator for ring elements.
        See extensive documentation at the top of element.pyx.
        """
        if have_same_parent(self, right):
            return (<RingElement>self)._div_c(<RingElement>right)
        return bin_op_c(self, right, operator.div)



    cdef RingElement _div_c(self, RingElement right):
        """
        Multiplication dispatcher for RingElements.
        DO NOT OVERRIDE THIS FUNCTION.
        See extensive documentation at the top of element.pyx.
        """
        if HAS_DICTIONARY(self):   # fast check
            return self._div_(right)
        else:
            return self._div_c_impl(right)

    cdef RingElement _div_c_impl(self, RingElement right):
        """
        Pyrex classes should override this function to implement division.
        DO NOT CALL THIS FUNCTION DIRECTLY.
        See extensive documentation at the top of element.pyx.
        """
        try:
            return self._parent.fraction_field()(self, right)
        except AttributeError:
            raise TypeError, arith_error_message(self, right, operator.div)

    def _div_(RingElement self, RingElement right):
        """
        Python classes should override this function to implement division.
        """
        return self._div_c_impl(right)

    def __pos__(self):
        return self

    def __invert__(self):
        return 1/self

    ##################################################

    def order(self):
        """
        Return the additive order of self.
        """
        return self.additive_order()

    def additive_order(self):
        """
        Return the additive order of self.
        """
        raise NotImplementedError

    def multiplicative_order(self):
        r"""
        Return the multiplicative order of self, if self is a unit, or raise
        \code{ArithmeticError} otherwise.
        """
        if not self.is_unit():
            raise ArithmeticError, "self (=%s) must be a unit to have a multiplicative order."
        raise NotImplementedError

    def is_unit(self):
        if self == 1 or self == -1:
            return True
        raise NotImplementedError

    def __pow__(self, n, dummy):
        cdef int i
        if PyFloat_Check(n):
            raise TypeError, "raising %s to the power of the float %s not defined"%(self, n)

        n = int(n)
        try:
            return self._pow(n)
        except AttributeError:
            pass

        a = self
        power = self.parent()(1)
        if n < 0:
            n = -n
            a = ~self
        elif n == 0:
            return power
        i = 0
        apow2 = a
        while (n>>i) > 0:
            if (n>>i) & 1:
                power = power * apow2
            if n == 0: break   # to not waste time doing an extra multiplication/increment
            apow2 = apow2 * apow2
            i = i+1
        return power




def is_CommutativeRingElement(x):
    """
    Return True if x is of type CommutativeRingElement.
    """
    return IS_INSTANCE(x, CommutativeRingElement)

cdef class CommutativeRingElement(RingElement):
    def _im_gens_(self, codomain, im_gens):
        if len(im_gens) == 1 and self.parent().gen(0) == 1:
            return codomain(self)
        raise NotImplementedError

    def inverse_mod(self, I):
        r"""
        Return an inverse of self modulo the ideal $I$, if defined,
        i.e., if $I$ and self together generate the unit ideal.
        """
        raise NotImplementedError

    def mod(self, I):
        r"""
        Return a representative for self modulo the ideal I (or the ideal
        generated by the elements of I if I is not an ideal.)

        EXAMPLE:  Integers
        Reduction of 5 modulo an ideal:
            sage: n = 5
            sage: n.mod(3*ZZ)
            2

        Reduction of 5 modulo the ideal generated by 3.
            sage: n.mod(3)
            2

        Reduction of 5 modulo the ideal generated by 15 and 6, which is $(3)$.
            sage: n.mod([15,6])
            2


        EXAMPLE: Univiate polynomials
            sage: R.<x> = PolynomialRing(QQ)
            sage: f = x^3 + x + 1
            sage: f.mod(x + 1)
            -1

        When little is implemented about a given ring, then mod may
        return simply return $f$.  For example, reduction is not
        implemented for $\Z[x]$ yet. (TODO!)

            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = x^3 + x + 1
            sage: f.mod(x + 1)
            x^3 + x + 1



        EXAMPLE: Multivariate polynomials
        We reduce a polynomial in two variables modulo a polynomial
        and an ideal:
            sage: R.<x,y,z> = PolynomialRing(QQ, 3)
            sage: (x^2 + y^2 + z^2).mod(x+y+z)
            2*z^2 + 2*y*z + 2*y^2

        Notice above that $x$ is eliminated.  In the next example,
        both $y$ and $z$ are eliminated.

            sage: (x^2 + y^2 + z^2).mod( (x - y, y - z) )
            3*z^2
            sage: f = (x^2 + y^2 + z^2)^2; f
            z^4 + 2*y^2*z^2 + y^4 + 2*x^2*z^2 + 2*x^2*y^2 + x^4
            sage: f.mod( (x - y, y - z) )
            9*z^4

        In this example $y$ is eliminated.
            sage: (x^2 + y^2 + z^2).mod( (x^3, y - z) )
            2*z^2 + x^2
        """
        from sage.rings.all import is_Ideal
        if not is_Ideal(I) or not I.ring() is self.parent():
            I = self.parent().ideal(I)
            #raise TypeError, "I = %s must be an ideal in %s"%(I, self.parent())
        return I.reduce(self)

cdef class Vector(ModuleElement):
    def __mul__(left, right):
        if PY_TYPE_CHECK(left, Vector):
            # left is the vector
            # Possibilities:
            #     left * matrix
            if PY_TYPE_CHECK(right, Matrix):
                return (<Matrix>right)._vector_times_matrix_c(<Vector>left)
            #     left * vector
            if PY_TYPE_CHECK(right, Vector):
                return (<Vector>left)._vector_times_vector_c(<Vector>right)
            #     left * scalar
            return (<ModuleElement>left)._multiply_by_scalar(right)

        else:
            # right is the vector
            # Possibilities:
            #     matrix * right
            if PY_TYPE_CHECK(left, Matrix):
                return (<Matrix>left)._matrix_times_vector_c(<Vector>right)
            #     vector * right
            if PY_TYPE_CHECK(left, Vector):
                return (<Vector>left)._vector_times_vector_c(<Vector>right)
            #     scalar * right
            return (<ModuleElement>right)._rmultiply_by_scalar_c(left)

    cdef Vector _vector_times_vector_c(Vector left, Vector right):
        if left._degree != right._degree:
            raise TypeError, "incompatible degrees"
        left, right = canonical_base_coercion_c(left, right)
        if HAS_DICTIONARY(left):
            return left._vector_times_vector(right)
        else:
            return left._vector_times_vector_c_impl(right)
    cdef Vector _vector_times_vector_c_impl(Vector left, Vector right):
        raise TypeError
    def  _vector_times_vector(left, right):
        return self.vector_time_vector_c_impl(right)


cdef have_same_base(Element x, Element y):
    return x._parent._base is y._parent._base


def is_Vector(x):
    return IS_INSTANCE(x, Vector)

cdef class Matrix(ModuleElement):
    cdef int is_sparse_c(self):
        raise NotImplementedError

    cdef int is_dense_c(self):
        raise NotImplementedError

    def __mul__(left, right):
        if PY_TYPE_CHECK(left, Matrix):
            # left is the matrix
            # Possibilities:
            #     left * matrix
            if PY_TYPE_CHECK(right, Matrix):
                return (<Matrix>left)._matrix_times_matrix_c(<Vector>right)
            #     left * vector
            if PY_TYPE_CHECK(right, Vector):
                return (<Matrix>left)._matrix_times_vector_c(<Vector>right)
            #     left * scalar
            return (<Matrix>left)._multiply_by_scalar(right)

        else:
            # right is the matrix
            # Possibilities:
            #     matrix * right
            if PY_TYPE_CHECK(left, Matrix):
                return (<Matrix>left)._matrix_times_matrix_c(<Matrix>right)
            #     vector * right
            if PY_TYPE_CHECK(left, Vector):
                return (<Matrix>right)._vector_times_matrix_c(<Vector>left)
            #     scalar * right
            return (<Matrix>right)._rmultiply_by_scalar(left)

    cdef Vector _vector_times_matrix_c(matrix_right, Vector vector_left):
        if vector_left._degree != matrix_right._nrows:
            raise TypeError, "incompatible dimensions"
        matrix_right, vector_left = canonical_base_coercion_c(matrix_right, vector_left)
        if HAS_DICTIONARY(matrix_right):
            return matrix_right._vector_times_matrix(vector_left)
        else:
            return matrix_right._vector_times_matrix_c_impl(vector_left)

    cdef Vector _vector_times_matrix_c_impl(matrix_right, Vector vector_left):
        raise TypeError

    def _vector_times_matrix(matrix_right, vector_left):
        return matrix_right._vector_times_matrix_c_impl(vector_left)


    cdef Vector _matrix_times_vector_c(matrix_left, Vector vector_right):
        if matrix_left._ncols != vector_right._degree:
            raise TypeError, "incompatible dimensions"
        matrix_left, vector_right = canonical_base_coercion_c(matrix_left, vector_right)
        if HAS_DICTIONARY(matrix_left):
            return matrix_left._matrix_times_vector(vector_right)
        else:
            return matrix_left._matrix_times_vector_c_impl(vector_right)

    cdef Vector _matrix_times_vector_c_impl(matrix_left, Vector vector_right):
        raise TypeError
    def _matrix_times_vector(matrix_left, vector_right):
        return matrix_left._matrix_times_vector_c_impl(vector_right)


    cdef Matrix _matrix_times_matrix_c(left, Matrix right):
        cdef int sl, sr
        if left._ncols != right._nrows:
            raise TypeError, "incompatible dimensions"
        left, right = canonical_base_coercion_c(left, right)
        sl = left.is_sparse_c(); sr = right.is_sparse_c()
        if sl != sr:  # is dense and one is sparse
            if sr:  # left is dense
                right = right.dense_matrix()
            else:
                left = left.dense_matrix()
        if HAS_DICTIONARY(left):
            return left._matrix_times_matrix(right)
        else:
            return left._matrix_times_matrix_c_impl(right)

    cdef Matrix _matrix_times_matrix_c_impl(left, Matrix right):
        raise TypeError
    def _matrix_time_matrix(left, right):
        return left._matrix_times_matrix_c_impl(right)


def is_Matrix(x):
    return IS_INSTANCE(x, Matrix)

def is_IntegralDomainElement(x):
    """
    Return True if x is of type IntegralDomainElement.
    """
    return IS_INSTANCE(x, IntegralDomainElement)

cdef class IntegralDomainElement(CommutativeRingElement):
    pass


def is_DedekindDomainElement(x):
    """
    Return True if x is of type DedekindDomainElement.
    """
    return IS_INSTANCE(x, DedekindDomainElement)

cdef class DedekindDomainElement(IntegralDomainElement):
    pass

def is_PrincipalIdealDomainElement(x):
    """
    Return True if x is of type PrincipalIdealDomainElement.
    """
    return IS_INSTANCE(x, PrincipalIdealDomainElement)

cdef class PrincipalIdealDomainElement(DedekindDomainElement):
    def lcm(self, right):
        """
        Returns the least common multiple of self and right.
        """
        if not PY_TYPE_CHECK(right, Element) or not ((<Element>right)._parent is self._parent):
            return bin_op_c(self, right, lcm)
        return self._lcm(right)

    def gcd(self, right):
        """
        Returns the gcd of self and right, or 0 if both are 0.
        """
        if not PY_TYPE_CHECK(right, Element) or not ((<Element>right)._parent is self._parent):
            return bin_op_c(self, right, gcd)
        return self._gcd(right)

    def xgcd(self, right):
        r"""
        Return the extended gcd of self and other, i.e., elements $r, s, t$ such that
        $$
           r = s \cdot self + t \cdot other.
        $$
        """
        if not PY_TYPE_CHECK(right, Element) or not ((<Element>right)._parent is self._parent):
            return bin_op_c(self, right, xgcd)
        return self._xgcd(right)


# This is pretty nasty low level stuff. The idea is to speed up construction
# of EuclideanDomainElements (in particular Integers) by skipping some tp_new
# calls up the inheritance tree.
PY_SET_TP_NEW(EuclideanDomainElement, Element)

def is_EuclideanDomainElement(x):
    """
    Return True if x is of type EuclideanDomainElement.
    """
    return IS_INSTANCE(x, EuclideanDomainElement)

cdef class EuclideanDomainElement(PrincipalIdealDomainElement):

    def degree(self):
        raise NotImplementedError

    def _gcd(self, other):
        """
        Return the greatest common divisor of self and other.

        Algorithm 3.2.1 in Cohen, GTM 138.
        """
        A = self
        B = other
        while not B.is_zero():
            Q, R = A.quo_rem(B)
            A = B
            B = R
        return A

    def leading_coefficient(self):
        raise NotImplementedError

    def quo_rem(self, other):
        raise NotImplementedError

    def __floordiv__(self,right):
        """
        Quotient of division of self by other.  This is denoted //.
        """
        Q, _ = self.quo_rem(right)
        return Q

    def __mod__(self, other):
        """
        Remainder of division of self by other.

        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: x % (x+1)
            -1
            sage: (x**3 + x - 1) % (x**2 - 1)
            2*x - 1
        """
        _, R = self.quo_rem(other)
        return R

def is_FieldElement(x):
    """
    Return True if x is of type FieldElement.
    """
    return IS_INSTANCE(x, FieldElement)

cdef class FieldElement(CommutativeRingElement):

    def is_unit(self):
        """
        Return True if self is a unit in its parent ring.

        EXAMPLES:
            sage: a = 2/3; a.is_unit()
            True

        On the other hand, 2 is not a unit, since its parent is ZZ.
            sage: a = 2; a.is_unit()
            False
            sage: parent(a)
            Integer Ring

        However, a is a unit when viewed as an element of QQ:
            sage: a = QQ(2); a.is_unit()
            True
        """
        return PyBool_FromLong(not self.is_zero())

    def _gcd(self, FieldElement other):
        """
        Return the greatest common divisor of self and other.
        """
        if self.is_zero() and other.is_zero():
            return self
        else:
            return self.parent()(1)

    def _lcm(self, FieldElement other):
        """
        Return the least common multiple of self and other.
        """
        if self.is_zero() and other.is_zero():
            return self
        else:
            return self.parent()(1)

    def _xgcd(self, FieldElement other):
        R = self.parent()
        if not self.is_zero():
            return R(1), ~self, R(0)
        elif not other.is_zero():
            return R(1), R(0), ~self
        else: # both are 0
            return self, self, self


    def quo_rem(self, right):
        if not isinstance(right, FieldElement) or not (right.parent() is self.parent()):
            right = self.parent()(right)
        return self/right, 0

def is_FiniteFieldElement(x):
    """
    Return True if x is of type FiniteFieldElement.
    """
    return IS_INSTANCE(x, FiniteFieldElement)

cdef class FiniteFieldElement(FieldElement):
    pass

def is_AlgebraElement(x):
    """
    Return True if x is of type AlgebraElement.
    """
    return IS_INSTANCE(x, AlgebraElement)

cdef class AlgebraElement(RingElement):
    pass

def is_CommutativeAlgebraElement(x):
    """
    Return True if x is of type CommutativeAlgebraElement.
    """
    return IS_INSTANCE(x, CommutativeAlgebraElement)

cdef class CommutativeAlgebraElement(CommutativeRingElement):
    pass

def is_InfinityElement(x):
    """
    Return True if x is of type InfinityElement.
    """
    return IS_INSTANCE(x, InfinityElement)

cdef class InfinityElement(RingElement):
    pass


cdef int have_same_parent(left, right):
    """
    Return nonzero true value if and only if left and right are
    elements and have the same parent.
    """
    # (We know at least one of the arguments is an Element. So if
    # their types are *equal* (fast to check) then they are both
    # Elements.  Otherwise use the slower test via PY_TYPE_CHECK.)
    if PY_TYPE(left) is PY_TYPE(right):
        return (<Element>left)._parent is (<Element>right)._parent

    if PY_TYPE_CHECK(right, Element) and PY_TYPE_CHECK(left, Element):
        return (<Element>left)._parent is (<Element>right)._parent

    return 0






#################################################################################
#
#  Coercion of elements
#
#################################################################################
import __builtin__
import operator

cimport sage.modules.module
import  sage.modules.module

#################################################################################
# parent
#################################################################################
cdef parent_c(x):
    if PY_TYPE_CHECK(x,Element):
        return (<Element>x)._parent
    return <object>PY_TYPE(x)

def parent(x):
    return parent_c(x)

#################################################################################
# coerce
#################################################################################
def coerce(Parent p, x):
    try:
        return p._coerce_c(x)
    except AttributeError:
        return p(x)


#################################################################################
# canonical coercion of two ring elements into one of their parents.
#################################################################################
cdef _verify_canonical_coercion_c(x, y):
    if not have_same_parent(x,y):
        raise RuntimeError, """There is a bug in the ring coercion code in SAGE.
Both x (=%s) and y (=%s) are supposed to have identical parents but they don't.
In fact, x has parent '%s'
whereas y has parent '%s'"""%(x,y,parent_c(x),parent_c(y))
    return x, y

def canonical_coercion(x, y):
    return canonical_coercion_c(x,y)

cdef canonical_coercion_c(x, y):
    cdef int i
    xp = parent_c(x)
    yp = parent_c(y)
    if xp is yp:
        return x, y

    if PY_IS_NUMERIC(x):
        try:
            x = yp(x)
        except TypeError:
            y = x.__class__(y)
            return x, y
        # Calling this every time incurs overhead -- however, if a mistake
        # gets through then one can get infinite loops in C code hence core
        # dumps.  And users define _coerce_ and __call__ for rings, which
        # can easily have bugs in it, i.e., not really make the element
        # have the correct parent.  Thus this check is *crucial*.
        return _verify_canonical_coercion_c(x,y)

    elif PY_IS_NUMERIC(y):
        try:
            y = xp(y)
        except TypeError:
            x = y.__class__(x)
            return x, y
        return _verify_canonical_coercion_c(x,y)

    try:
        if xp.has_coerce_map_from(yp):
            y = (<Parent>xp)._coerce_c(y)
            return _verify_canonical_coercion_c(x,y)
    except AttributeError:
        pass
    try:
        if yp.has_coerce_map_from(xp):
            x = (<Parent>yp)._coerce_c(x)
            return _verify_canonical_coercion_c(x,y)
    except AttributeError:
        pass
    raise TypeError, "unable to find a common canonical parent for x and y"

cdef canonical_base_coercion_c(Element x, Element y):
    if not have_same_base(x, y):
        if (<Parent> x._parent._base).has_coerce_map_from_c(y._parent._base):
            # coerce all elements of y to the base ring of x
            y = y.base_extend_c(x._parent._base)
        elif (<Parent> y._parent._base).has_coerce_map_from_c(x._parent._base):
            # coerce x to have elements in the base ring of y
            x = x.base_extend_c(y._parent._base)
    return x,y

def canonical_base_coercion(x, y):
    try:
        xb = x.base_ring()
    except AttributeError:
        #raise TypeError, "unable to find base ring for %s (parent: %s)"%(x,x.parent())
        raise TypeError, "unable to find base ring"
    try:
        yb = y.base_ring()
    except AttributeError:
        raise TypeError, "unable to find base ring"
        #raise TypeError, "unable to find base ring for %s (parent: %s)"%(y,y.parent())
    try:
        b = canonical_coercion_c(xb(0),yb(0))[0].parent()
    except TypeError:
        raise TypeError, "unable to find base ring"
        #raise TypeError, "unable to find a common base ring for %s (base ring: %s) and %s (base ring %s)"%(x,xb,y,yb)
    return x.change_ring(b), y.change_ring(b)


D = {'mul':'*', 'add':'+', 'sub':'-', 'div':'/'}
cdef arith_error_message(x, y, op):
    try:
        n = D[op.__name__]
    except KeyError:
        n = op.__name__
    return "unsupported operand parent(s) for '%s': '%s' and '%s'"%(n, parent_c(x), parent_c(y))

def bin_op(x, y, op):
    return bin_op_c(x,y,op)

cdef bin_op_c(x, y, op):
    """
    Compute x op y, where coercion of x and y works according to
    SAGE's coercion rules.
    """
    # Try canonical element coercion.
    try:
        x1, y1 = canonical_coercion_c(x, y)
        return op(x1,y1)
    except TypeError, msg:
        if not op is operator.mul:
            raise TypeError, arith_error_message(x,y,op)

    # If the op is multiplication, then some other algebra multiplications
    # may be defined

    # 2. Try scalar multiplication.
    # No way to multiply x and y using the ``coerce into a canonical
    # parent'' rule.
    # The next rule to try is scalar multiplication by coercing
    # into the base ring.
    cdef int x_is_modelt, y_is_modelt

    y_is_modelt = PY_TYPE_CHECK(y, ModuleElement)
    if y_is_modelt:
        # First try to coerce x into the base ring of y if y is an element.
        try:
            R = (<ModuleElement> y)._parent._base
            if R is None:
                raise RuntimeError, "base of '%s' must be set to a ring (but it is None)!"%((<ModuleElement> y)._parent)
            x = (<Parent>R)._coerce_c(x)
            return (<ModuleElement> y)._rmul_c(x)     # the product x * y
        except TypeError, msg:
            pass

    x_is_modelt = PY_TYPE_CHECK(x, ModuleElement)
    if x_is_modelt:
        # That did not work.  Try to coerce y into the base ring of x.
        try:
            R = (<ModuleElement> x)._parent._base
            if R is None:
                raise RuntimeError, "base of '%s' must be set to a ring (but it is None)!"%((<ModuleElement> x)._parent)
            y = (<Parent> R)._coerce_c(y)
            return (<ModuleElement> x)._lmul_c(y)    # the product x * y
        except TypeError:
            pass

    if y_is_modelt and x_is_modelt:
        # 3. Both canonical coercion failed, but both are module elements.
        # Try base extending the right object by the parent of the left

        ## TODO -- WORRY -- only unambiguous if one succeeds!
        if  PY_TYPE_CHECK(x, RingElement):
            try:
                return x * y.base_extend((<RingElement>x)._parent)
            except (TypeError, AttributeError), msg:
                pass
        # Also try to base extending the left object by the parent of the right
        if  PY_TYPE_CHECK(y, RingElement):
            try:
                return y * x.base_extend((<Element>y)._parent)
            except (TypeError, AttributeError), msg:
                pass

    # 4. Try _l_action or _r_action.
    # Test to see if an _r_action or _l_action is
    # defined on either side.
    try:
        return x._l_action(y)
    except (AttributeError, TypeError):
        pass
    try:
        return y._r_action(x)
    except (AttributeError, TypeError):
        pass

    raise TypeError, arith_error_message(x,y,op)

def coerce_cmp(x,y):
    cdef int c
    try:
        x, y = canonical_coercion_c(x, y)
        return cmp(x,y)
    except TypeError:
        c = cmp(type(x), type(y))
        if c == 0: c = -1
        return c



###############################################################################

def lcm(x,y):
    from sage.rings.arith import lcm
    return lcm(x,y)

def gcd(x,y):
    from sage.rings.arith import gcd
    return gcd(x,y)

def xgcd(x,y):
    from sage.rings.arith import xgcd
    return xgcd(x,y)
