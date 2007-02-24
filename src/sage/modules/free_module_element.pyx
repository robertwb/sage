r"""
Elements of free modules

AUTHOR:
    -- William Stein
    -- Josh Kantor

TODO:
    Change to use a get_unsafe / set_unsafe, etc., structure exactly
    like with matrices, since we'll have to define a bunch of special
    purpose implementations of vectors easily and systematically.

EXAMPLES:
We create a vector space over $\QQ$ and a subspace of this space.
    sage: V = QQ^5
    sage: W = V.span([V.1, V.2])

Arithmetic operations always return something in the ambient space,
since there is a canonical map from $W$ to $V$ but not from $V$ to $W$.

    sage: parent(W.0 + V.1)
    Vector space of dimension 5 over Rational Field
    sage: parent(V.1 + W.0)
    Vector space of dimension 5 over Rational Field
    sage: W.0 + V.1
    (0, 2, 0, 0, 0)
    sage: W.0 - V.0
    (-1, 1, 0, 0, 0)

Next we define modules over $\ZZ$ and a finite field.
    sage: K = ZZ^5
    sage: M = GF(7)^5

Arithmetic between the $\QQ$  and $\ZZ$ modules is defined, and
the result is always over $\QQ$, since there is a canonical coercion
map to $\QQ$.
    sage: K.0 + V.1
    (1, 1, 0, 0, 0)
    sage: parent(K.0 + V.1)
    Vector space of dimension 5 over Rational Field

Since there is no canonical coercion map to the finite field from $\QQ$
the following arithmetic is not defined:
    sage: V.0 + M.0
    Traceback (most recent call last):
    ...
    TypeError: unsupported operand parent(s) for '+': 'Vector space of dimension 5 over Rational Field' and 'Vector space of dimension 5 over Finite Field of size 7'

However, there is a map from $\ZZ$ to the finite field, so the
following is defined, and the result is in the finite field.
    sage: w = K.0 + M.0; w
    (2, 0, 0, 0, 0)
    sage: parent(w)
    Vector space of dimension 5 over Finite Field of size 7
    sage: parent(M.0 + K.0)
    Vector space of dimension 5 over Finite Field of size 7
"""

import operator

include '../ext/cdefs.pxi'
include '../ext/stdsage.pxi'

import sage.misc.misc as misc
import sage.misc.latex as latex

cimport sage.structure.coerce
cdef sage.structure.coerce.Coerce coerce
coerce = sage.structure.coerce.Coerce()

from sage.structure.sequence import Sequence

from sage.structure.element cimport Element, ModuleElement, RingElement, Vector as element_Vector
from sage.matrix.matrix cimport Matrix

import sage.rings.arith

from sage.rings.ring import is_Ring
import sage.rings.integer_ring

def is_FreeModuleElement(x):
    return isinstance(x, FreeModuleElement)

def vector(arg0, arg1=None, sparse=None):
    r"""
    Return a vector over R with given entries.

    CALL FORMATS:
        1. vector(object)
        2. vector(ring, object)
        3. vector(object, ring)

    INPUT:
        elts -- entries of a vector (either a list or dict).
        R -- ring
        sparse -- optional

    OUTPUT:
        An element of the free module over R of rank len(elts).

    EXAMPLES:
        sage: v = vector([1,2,3]); v
        (1, 2, 3)
        sage: v.parent()
        Ambient free module of rank 3 over the principal ideal domain Integer Ring
        sage: v = vector([1,2,3/5]); v
        (1, 2, 3/5)
        sage: v.parent()
        Vector space of dimension 3 over Rational Field

    All entries must \emph{canonically} coerce to some common ring:
        sage: v = vector([17, GF(11)(5), 19/3]); v
        Traceback (most recent call last):
        ...
        TypeError: unable to find a common ring for all elements

        sage: v = vector([17, GF(11)(5), 19]); v
        (6, 5, 8)
        sage: v.parent()
        Vector space of dimension 3 over Finite Field of size 11
        sage: v = vector([17, GF(11)(5), 19], QQ); v
        (17, 5, 19)
        sage: v.parent()
        Vector space of dimension 3 over Rational Field
        sage: v = vector((1,2,3), QQ); v
        (1, 2, 3)
        sage: v.parent()
        Vector space of dimension 3 over Rational Field
        sage: v = vector(QQ, (1,2,3)); v
        (1, 2, 3)
        sage: v.parent()
        Vector space of dimension 3 over Rational Field
        sage: v = vector(vector([1,2,3])); v
        (1, 2, 3)
        sage: v.parent()
        Ambient free module of rank 3 over the principal ideal domain Integer Ring

    You can also use \code{free_module_element}, which is the same as \code{vector}.
        sage: free_module_element([1/3, -4/5])
        (1/3, -4/5)

    Make a vector mod 3 out of a vector over ZZ:
        sage: vector(vector([1,2,3]), GF(3))
        (1, 2, 0)
    """
    if hasattr(arg0, '_vector_'):
        if arg1 is None:
            arg1 = sage.rings.integer_ring.ZZ
        return arg0._vector_(arg1)

    if hasattr(arg1, '_vector_'):
        return arg1._vector_(arg0)

    if is_Ring(arg0):
        R = arg0
        v = arg1
    elif is_Ring(arg1):
        R = arg1
        v = arg0
    else:
        v = arg0
        R = None
    if isinstance(v, dict):
        if sparse is None:
            sparse = True
        v, R = prepare_dict(v, R)
    else:
        if sparse is None:
            sparse = False
        v, R = prepare(v, R)
    if sparse:
        import free_module  # slow -- can we improve
        return free_module.FreeModule(R, len(v), sparse=True)(v)
    else:
        return (R**len(v))(v)

free_module_element = vector

def prepare(v, R):
    v = Sequence(v, universe=R)
    ring = v.universe()
    if not is_Ring(ring):
        raise TypeError, "unable to find a common ring for all elements"
    return v, ring

def prepare_dict(w, R):
    Z = w.items()
    cdef Py_ssize_t n
    n = len(Z)
    X = [None]*n
    cdef Py_ssize_t i
    i = 0
    for _, x in Z:
        X[i] = x
        i = i + 1
    return prepare(X, R)

cdef class FreeModuleElement(element_Vector):   # abstract base class
    """
    An element of a generic free module.
    """
    def __init__(self, parent):
        self._parent = parent
        self._degree = parent.degree()

    def _vector_(self, R):
        return self.change_ring(R)

    def _hash(self):
        return hash(tuple(list(self)))

    def change_ring(self, R):
        P = self.parent()
        if P.base_ring() is R:
            return self
        return P.change_ring(R)(self)

    def additive_order(self):
        """
        Return the additive order of self.

        EXAMPLES:
            sage: v = vector(Integers(4), [1,2])
            sage: v.additive_order()
            4

            sage: v = vector([1,2,3])
            sage: v.additive_order()
            +Infinity

            sage: v = vector(Integers(30), [6, 15]); v
            (6, 15)
            sage: v.additive_order()
            10
            sage: 10*v
            (0, 0)
        """
        v = [None]*self.degree()
        cdef int i
        for i from 0 <= i < self.degree():
            v[i] = self[i].additive_order()
        return sage.rings.arith.LCM(v)

    def iteritems(self):
        return self.dict(copy=False).iteritems()

    def __abs__(self):
        return self.norm()

    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        EXAMPLES:
            sage: v = vector(QQ, [0,0,0,0])
            sage: v == 0
            True
            sage: v == 1
            False
            sage: v == v
            True
            sage: w = vector(QQ, [-1,0,0,0])
            sage: w < v
            True
            sage: w > v
            False
        """
        cdef Py_ssize_t i
        cdef int c
        for i from 0 <= i < left.degree():
            c = cmp(left[i], right[i])
            if c: return c
        return 0

    def __nonzero__(self):
        """
        EXAMPLES:
            sage: V = vector(ZZ, [0, 0, 0, 0])
            sage: bool(V)
            False
            sage: V = vector(ZZ, [1, 2, 3, 5])
            sage: bool(V)
            True
        """
        return self != 0

    def __getitem__(self, i):
        raise NotImplementedError

    def __invert__(self):
        raise NotImplementedError

    def __len__(self):
        return self.parent().degree()

    def __mod__(self, p):
        """
        EXAMPLES:
            sage: V = vector(ZZ, [5, 9, 13, 15])
            sage: V % 7
            (5, 2, 6, 1)
            sage: parent(V % 7)
            Ambient free module of rank 4 over the principal ideal domain Integer Ring
        """
        return eval('self.parent()([x % p for x in self.list()], \
                     copy=False, coerce=False, check=False)',
                    {'self':self, 'p':p})

    def Mod(self, p):
        """
        EXAMPLES:
            sage: V = vector(ZZ, [5, 9, 13, 15])
            sage: V.Mod(7)
            (5, 2, 6, 1)
            sage: parent(V.Mod(7))
            Vector space of dimension 4 over Ring of integers modulo 7
        """
        return self.change_ring(self.base_ring().quotient_ring(p))

    def list(self, copy=True):
        d = self.degree()
        v = [0]*d
        for i in range(d):
            v[i] = self[i]
        return v

    def list_from_positions(self, positions):
        cdef Py_ssize_t j
        v = [0]*len(positions)
        j = 0
        for i in positions:
            v[j] = self[i]
            j = j + 1
        return v

    def lift(self):
        """
        EXAMPLES:
            sage: V = vector(Integers(7), [5, 9, 13, 15]) ; V
            (5, 2, 6, 1)
            sage: V.lift()
            (5, 2, 6, 1)
            sage: parent(V.lift())
            Ambient free module of rank 4 over the principal ideal domain Integer Ring
        """
        return self.change_ring(self.base_ring().cover_ring())

    def __pos__(self):
        return self

    def __pow__(self, n, dummy):
        raise NotImplementedError

    def _repr_(self):
        d = self.degree()
        if d == 0: return "()"
        # compute column widths
        S = eval('[str(x) for x in self.list(copy=False)]', {'self':self})
        #width = max([len(x) for x in S])
        s = "("
        for i in xrange(d):
            if i == d-1:
                sep = ""
            else:
                sep=", "
            entry = S[i]
            #if i > 0:
            #    entry = " "*(width-len(entry)) + entry
            s = s + entry + sep
        s = s + ")"
        return s

    def __setitem__(self, i, x):
        raise NotImplementedError

    def __getslice__(self, Py_ssize_t i, Py_ssize_t j):
        """
        EXAMPLES:
            sage: v = vector(QQ['x,y'], [1,2, 'x*y', 'x^2-y^2']); v
            (1, 2, x*y, -1*y^2 + x^2)
            sage: v[1:]
            (2, x*y, -1*y^2 + x^2)
            sage: v[:2]
            (1, 2)
            sage: type(v[1:])
            <type 'sage.modules.free_module_element.FreeModuleElement_generic_dense'>
            sage: v = vector(CDF,[1,2,(3,4)]); v
            (1.0, 2.0, 3.0 + 4.0*I)
            sage: w = v[1:]; w
            (2.0, 3.0 + 4.0*I)
            sage: parent(w)
            Vector space of dimension 2 over Complex Double Field
        """
        return vector(self.base_ring(), self.list()[i:j])

    def __setslice__(self, i, j, value):
        """
        EXAMPLES:
            sage: v = vector(CDF,[1,2,(3,4)]); v
            (1.0, 2.0, 3.0 + 4.0*I)
            sage: v[1:] = (1,3); v
            (1.0, 1.0, 3.0)
        """
        cdef Py_ssize_t k, d, n
        d = self.degree()
        R = self.base_ring()
        n = 0
        for k from i <= k < j:
            if k >= d:
                return
            if k >= 0:
                self[k] = R(value[n])
                n = n + 1



    def __richcmp__(left, right, int op):
        cdef int ld, rd
        if not isinstance(left, FreeModuleElement) or not isinstance(right, FreeModuleElement):
            # use the generic compare
            return (<Element>left)._richcmp(right, op)
        ld = (<FreeModuleElement>left)._degree
        rd = (<FreeModuleElement>right)._degree
        if ld < rd:
            return (<Element>left)._rich_to_bool(op, -1)
        elif ld > rd:
            return (<Element>left)._rich_to_bool(op, 1)
        if (<FreeModuleElement>left)._parent.base_ring() is (<FreeModuleElement>right)._parent.base_ring():
            return (<Element>left)._rich_to_bool(op, (
                    <FreeModuleElement>left)._cmp_same_ambient_c(right))
        return (<Element>left)._richcmp(right, op)


    cdef int _cmp_same_ambient_c(left, FreeModuleElement right):
        return cmp(left.list(copy=False), right.list(copy=False))

    def _matrix_multiply(self, Matrix A):
        """
        Return the product self*A.

        EXAMPLES:
            sage: MS = MatrixSpace(QQ,3)
            sage: A = MS([0,1,0,1,0,0,0,0,1])
            sage: V = QQ^3
            sage: v = V([1,2,3])
            sage: v._matrix_multiply(A)
            (2, 1, 3)

        The multiplication operator also just calls \code{_matrix_multiply}:
            sage: v*A
            (2, 1, 3)
        """
        return self*A

    cdef ModuleElement _rmul_nonscalar_c_impl(left, right):
        if PY_TYPE_CHECK(right, Matrix):
            return right.vector_matrix_multiply(left)
        raise TypeError

    def degree(self):
        return self._degree

    def denominator(self):
        R = self.base_ring()
        if self.degree() == 0: return 1
        x = self.list()
        d = x[0].denominator()
        for y in x:
            d = d.lcm(y.denominator())
        return d

    def dict(self, copy=True):
        e = {}
        for i in xrange(self.degree()):
            c = self[i]
            if c != 0:
                e[i] = c
        return e

    def dot_product(self, right):
        """
        Return the dot product of self and right, which is the sum
        of the product of the corresponding entries.

        INPUT:
            right -- vector of the same degree as self.  it need not
                     be in the same vector space as self, as long as
                     the coefficients can be multiplied.

        EXAMPLES:
            sage: V = FreeModule(ZZ, 3)
            sage: v = V([1,2,3])
            sage: w = V([4,5,6])
            sage: v.dot_product(w)
            32

            sage: W = VectorSpace(GF(3),3)
            sage: w = W([0,1,2])
            sage: w.dot_product(v)
            2
            sage: w.dot_product(v).parent()
            Finite Field of size 3

        Implicit coercion is well defined (irregardless of order), so
        we get 2 even if we do the dot product in the other order.

            sage: v.dot_product(w)
            2
        """
        if not isinstance(right, FreeModuleElement):
            raise TypeError, "right must be a free module element"
        r = right.list()
        l = self.list()
        if len(r) != len(l):
            raise ArithmeticError, "degrees must be the same"%(len(l),len(r))
        zero = self.parent().base_ring()(0)
        return sum(eval('[l[i]*r[i] for i in xrange(len(l))]', {'l':l,'r':r}), zero)

    def element(self):
        return self

    def get(self, i):
        """
        get is meant to be more efficient
        than getitem, because it does not do
        any error checking.
        """
        return self[i]

    def set(self, i, x):
        """
        set is meant to be more efficient
        than setitem, because it does not do
        any error checking or coercion.  Use with care.
        """
        self[i] = x


    def inner_product(self, right):
        """
        Returns the inner product of self and other, with respect to
        the inner product defined on the parent of self.

        EXAMPLES: todo
        """
        if self.parent().is_ambient() and self.parent()._inner_product_is_dot_product():
            return self.dot_product(right)
        if not isinstance(right, FreeModuleElement):
            raise TypeError, "right must be a free module element"
        M = self.parent()
        if M.is_ambient() or M.uses_ambient_inner_product():
            A = M.ambient_module().inner_product_matrix()
            return M(A.linear_combination_of_rows(self)).dot_product(right)
        else:
            A = M.inner_product_matrix()
            v = M.coordinate_vector(self)
            w = M.coordinate_vector(right)
            return A.linear_combination_of_rows(v).dot_product(w)

    def is_dense(self):
        return self.parent().is_dense()

    def is_sparse(self):
        return self.parent().is_sparse()

    def is_vector(self):
        return True

##     def zero_out_positions(self, P):
##         """
##         Set the positions of self in the list P equal to 0.
##         """
##         z = self.base_ring()(0)
##         d = self.degree()
##         for n in P:
##             self[n] = z

    def nonzero_positions(self):
        """
        Return the sorted list of integers i such that self[i] != 0.
        """
        z = self.base_ring()(0)
        v = self.list()
        return eval('[i for i in xrange(self.degree()) if v[i] != z]',
                    {'self':self, 'z':z, 'v':v})

    def support(self):   # do not override.
        """
        Return the integers i such that self[i] != 0.
        This is the same as the \code{nonzero_positions} function.
        """
        return self.nonzero_positions()

    def _latex_(self):
        """
        Return a latex representation of self.  For example, if self is
        the free module element (1,2,3,4), then following latex is
        generated: "(1,2,3,4)"  (without the quotes).
        """
        s = '\\left('
        for a in self.list():
            s = s + latex.latex(a) + ','
        if len(self.list()) > 0:
            s = s[:-1]  # get rid of last comma
        return s + '\\right)'



#############################################
# Generic dense element
#############################################
def make_FreeModuleElement_generic_dense(parent, entries, degree):
    cdef FreeModuleElement_generic_dense v
    v = FreeModuleElement_generic_dense.__new__(FreeModuleElement_generic_dense)
    v._entries = entries
    v._parent = parent
    v._degree = degree
    return v

cdef class FreeModuleElement_generic_dense(FreeModuleElement):
    """
        EXAMPLES:
            sage: v = (ZZ^3).0
            sage: loads(dumps(v)) == v
            True
            sage: v = (QQ['x']^3).0
            sage: loads(dumps(v)) == v
            True
    """
    cdef _new_c(self, object v):
        # Create a new dense free module element with minimal overhead and
        # no type checking.
        cdef FreeModuleElement_generic_dense x
        x = PY_NEW(FreeModuleElement_generic_dense)
        x._parent = self._parent
        x._entries = v
        x._degree = self._degree
        return x

    def _hash(self):
        return hash(tuple(list(self)))

    def __copy__(self):
        return self._new_c(list(self._entries))

    def __init__(self, parent, entries, coerce=True, copy=True):
        FreeModuleElement.__init__(self, parent)
        R = self.parent().base_ring()
        if entries == 0:
            entries = [R(0)]*self.degree()
        else:
            if not isinstance(entries, (list, tuple)):

                raise TypeError, "entries (=%s) must be a list"%(entries, )

            if len(entries) != self.degree():
                raise ArithmeticError, "entries must be a list of length %s"%\
                            self.degree()
            if coerce:
                try:
                    entries = eval('[R(x) for x in entries]',{'R':R, 'entries':entries})
                except TypeError:
                    raise TypeError, "Unable to coerce entries (=%s) to %s"%(entries, R)
            elif copy:
                # Make a copy
                entries = list(entries)
        self._entries = entries

    cdef ModuleElement _add_c_impl(left, ModuleElement right):
        """
        Add left and right.
        """
        cdef Py_ssize_t i, n
        n = PyList_Size(left._entries)
        v = [None]*n
        for i from 0 <= i < n:
            v[i] = (<RingElement>left._entries[i])._add_c(<RingElement>
                                            ((<FreeModuleElement_generic_dense>right)._entries[i]))
        return left._new_c(v)

    cdef ModuleElement _sub_c_impl(left, ModuleElement right):
        """
        Subtract right from left.

        EXAMPLES:
            sage: V = QQ^5
            sage: W = V.span([V.1, V.2])
            sage: W.0 - V.0
            (-1, 1, 0, 0, 0)
            sage: V.0 - W.0
            (1, -1, 0, 0, 0)
        """
        cdef Py_ssize_t i, n
        n = PyList_Size(left._entries)
        v = [None]*n
        for i from 0 <= i < n:
            v[i] = (<RingElement>left._entries[i])._sub_c(<RingElement>
                                            ((<FreeModuleElement_generic_dense>right)._entries[i]))
        return left._new_c(v)

    cdef ModuleElement _rmul_c_impl(self, RingElement left):
        # This is basically a fast Python/C version of
        #    [left*x for x in self.list()]
        cdef Py_ssize_t i, n
        n = PyList_Size(self._entries)
        v = [None]*n
        for i from 0 <= i < n:
            v[i] = left._mul_c(<RingElement>(self._entries[i]))
        return self._new_c(v)

    cdef ModuleElement _lmul_c_impl(self, RingElement right):
        # This is basically a very fast Python/C version of
        #    [x*right for x in self.list()]
        cdef Py_ssize_t i, n
        n = PyList_Size(self._entries)
        v = [None]*n
        for i from 0 <= i < n:
            v[i] = (<RingElement>(self._entries[i]))._mul_c(right)
        return self._new_c(v)

    cdef element_Vector _vector_times_vector_c_impl(left, element_Vector right):
        # Component wise vector * vector multiplication.
        cdef Py_ssize_t i, n
        n = PyList_Size(left._entries)
        v = [None]*n
        for i from 0 <= i < n:
            v[i] = (<RingElement>left._entries[i])._mul_c((<FreeModuleElement_generic_dense>right)._entries[i])
        return self._new_c(v)

    def __reduce__(self):
        return (make_FreeModuleElement_generic_dense, (self._parent, self._entries, self._degree))

    def __getitem__(self, Py_ssize_t i):
        """
        """
        if isinstance(i, slice):
            return list(self)[i]
        i = int(i)
        #if not isinstance(i, int):
        #    raise TypeError, "index must an integer"
        if i < 0 or i >= self.degree():
            raise IndexError, "index (i=%s) must be between 0 and %s"%(i,
                            self.degree()-1)
        return self._entries[i]

    def __setitem__(self, Py_ssize_t i, value):
        """
        Set entry i of self to value.
        """
        i = int(i)
        #if not isinstance(i, int):
        #    raise TypeError, "index must an integer"
        if i < 0 or i >= self.degree():
            raise IndexError, "index (i=%s) must be between 0 and %s"%(i,
                            self.degree()-1)
        self._entries[i] = self.base_ring()(value)

    def __setslice__(self, Py_ssize_t i, Py_ssize_t j, value):
        """
        EXAMPLES:
            sage: v = vector(QQ['x,y'], [1,2, 'x*y'])
            sage: v
            (1, 2, x*y)
            sage: v[1:]
            (2, x*y)
            sage: v[1:] = [4,5]; v
            (1, 4, 5)
            sage: v[:2] = [5,(6,2)]; v
            (5, 3, 5)
            sage: v[:2]
            (5, 3)
        """
        cdef Py_ssize_t k, n, d
        d = self.degree()
        R = self.base_ring()
        n = 0
        for k from i <= k < j:
            if k >= d:
                return
            if k >= 0:
                self._entries[k] = R(value[n])
                n = n + 1

    def list(self, copy=True):
        if copy:
            return list(self._entries)
        else:
            return self._entries

    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        Compare two free module elements with identical parents.

        Free module elements are compared in lexicographic order on
        the underlying list of coefficients.  A dense a sparse free
        module element are equal if their coefficients are the same.
        """
        return cmp(left._entries, (<FreeModuleElement_generic_dense>right)._entries)


#############################################
# Generic sparse element
#############################################
def _sparse_dot_product(v, w):
    """
    v and w are dictionaries with integer keys.
    """
    x = set(v.keys()).intersection(set(w.keys()))
    return eval('sum([v[k]*w[k] for k in x])', {'v':v, 'w':w, 'x':x})

def make_FreeModuleElement_generic_sparse(parent, entries, degree):
    cdef FreeModuleElement_generic_sparse v
    v = FreeModuleElement_generic_sparse.__new__(FreeModuleElement_generic_sparse)
    v._entries = entries
    v._parent = parent
    v._degree = degree
    return v

cdef class FreeModuleElement_generic_sparse(FreeModuleElement):
    """
    A generic sparse free module element is a dictionary with keys
    ints i and entries in the base ring.

    EXAMPLES:

    Pickling works:
        sage: v = FreeModule(ZZ, 3, sparse=True).0
        sage: loads(dumps(v)) == v
        True
        sage: v = FreeModule(Integers(8)['x,y'], 5, sparse=True).1
        sage: loads(dumps(v)) - v
        (0, 0, 0, 0, 0)

        sage: a = vector([-1,0,1/1],sparse=True); b = vector([-1/1,0,0],sparse=True)
        sage: a.parent()
        Sparse vector space of dimension 3 over Rational Field
        sage: b - a
        (0, 0, -1)
    """
    cdef _new_c(self, object v):
        # Create a new sparse free module element with minimal overhead and
        # no type checking.
        cdef FreeModuleElement_generic_sparse x
        x = PY_NEW(FreeModuleElement_generic_sparse)
        x._parent = self._parent
        x._entries = v
        x._degree = self._degree
        return x

    def __copy__(self):
        return self._new_c(dict(self._entries))

    def __init__(self, parent,
                 entries=0,
                 coerce=True,
                 copy=True):
        #WARNING: In creation, we do not check that the i pairs satisfy
        #     0 <= i < degree.
        FreeModuleElement.__init__(self, parent)
        R = self.base_ring()
        if entries == 0:
            entries = {}
        else:
            if isinstance(entries, list):
                if len(entries) != self.degree():
                    raise TypeError, "entries has the wrong length"
                x = entries
                entries = {}
                for i in xrange(self.degree()):
                    if x[i] != 0:
                        entries[i] = x[i]
                copy = False
            if not isinstance(entries, dict):
                raise TypeError, "entries must be a dict"
            if coerce:
                try:
                    for k, x in entries.iteritems():
                        entries[k] = R(x)
                except TypeError:
                    raise TypeError, "Unable to coerce values of entries dict (=%s) to %s"%(entries, R)
            elif copy:
                # Make a copy
                entries = dict(entries)
        self._entries = entries

    cdef ModuleElement _add_c_impl(left, ModuleElement right):
        """
        Add left and right.
        """
        cdef object v, e
        e = dict((<FreeModuleElement_generic_sparse>right)._entries)
        for i, a in left._entries.iteritems():
            if e.has_key(i):
                e[i] = (<RingElement>a)._add_c(<RingElement> e[i])
            else:
                e[i] = a
        return left._new_c(e)

    cdef ModuleElement _sub_c_impl(left, ModuleElement right):
        cdef object v, e
        e = dict(left._entries)   # dict to make a copy
        for i, a in (<FreeModuleElement_generic_sparse>right)._entries.iteritems():
            if e.has_key(i):
                e[i] = (<RingElement> e[i])._sub_c(<RingElement>a)
            else:
                e[i] = -a
        return left._new_c(e)


    cdef ModuleElement _lmul_c_impl(self, RingElement right):
        cdef object v
        v = PyDict_New()
        for i, a in self._entries.iteritems():
            v[i] = (<RingElement>a)._mul_c(right)
        return self._new_c(v)

    cdef ModuleElement _rmul_c_impl(self, RingElement left):
        cdef object v
        v = PyDict_New()
        for i, a in self._entries.iteritems():
            v[i] = left._mul_c(a)
        return self._new_c(v)

    cdef element_Vector _vector_times_vector_c_impl(left, element_Vector right):
        # Component wise vector * vector multiplication.
        cdef object v, e
        e = dict((<FreeModuleElement_generic_sparse>right)._entries)
        for i, a in left._entries.iteritems():
            if e.has_key(i):
                e[i] = (<RingElement>a)._mul_c(<RingElement> e[i])
            else:
                e[i] = a
        return left._new_c(e)

    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        Compare two sparse free module elements.

        Free module elements are compared in lexicographic order on
        the underlying list of coefficients.  A dense a sparse free
        module element are equal if their coefficients are the same.
        """
        a = left._entries.items()
        a.sort()
        b = (<FreeModuleElement_generic_dense>right)._entries.items()
        b.sort()
        return cmp(a,b)

    def iteritems(self):
        return self._entries.iteritems()

    def __reduce__(self):
        return (make_FreeModuleElement_generic_sparse, (self._parent, self._entries, self._degree))

    def __getitem__(self, i):
        #if not isinstance(i, int):
        i = int(i)
            #raise TypeError, "index must an integer"
        if i < 0 or i >= self.degree():
            raise IndexError, "index (i=%s) must be between 0 and %s"%(i,
                            self.degree()-1)
        if self._entries.has_key(i):
            return self._entries[i]
        return self.base_ring()(0)  # optimize this somehow

    def get(self, i):
        """
        Like __getitem__ but with no type or bounds checking.
        Returns 0 if access is out of bounds.
        """
        i = int(i)
        if self._entries.has_key(i):
            return self._entries[i]
        return self.base_ring()(0)  # optimize this somehow


    def set(self, i, x):
        """
        Like __setitem__ but with no type or bounds checking.
        """
        i = int(i)
        if x == 0:
            if self._entries.has_key(i):
                del self._entries[i]
            return
        self._entries[i] = x

    def __setitem__(self, i, value):
        """
        """
        i = int(i)
        #if not isinstance(i, int):
        #    raise TypeError, "index must an integer"
        if i < 0 or i >= self.degree():
            raise IndexError, "index (i=%s) must be between 0 and %s"%(i,
                            self.degree()-1)
        self.set(i, value)

    def denominator(self):
        R = self.base_ring()
        x = self.entries()
        if len(x) == 0:
            return 1
        Z = x.iteritems()
        d = Z.next()[1].denominator()
        for _, y in Z:
            d = d.lcm(y.denominator())
        return d

    def dict(self, copy=True):
        if copy:
            return dict(self._entries)
        else:
            return self._entries

    def list(self, copy=True):
        cdef Py_ssize_t n
        n = self._parent.degree()
        z = self._parent.base_ring()(0)
        v = [z]*n
        for i, a in self._entries.iteritems():
            v[i] = a
        return v

    def nonzero_positions(self):
        """
        Returns the set of pairs (i,j) such that self[i,j] != 0.
        """
        K = self._entries.keys()
        K.sort()
        return K
