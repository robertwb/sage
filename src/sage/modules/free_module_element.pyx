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
    TypeError: x=(1, 0, 0, 0, 0), y=(1, 0, 0, 0, 0)
    unable to find a common canonical parent for x and y
    No canonical coercion defined.

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

from sage.structure.element cimport Element, ModuleElement, RingElement
from sage.matrix.matrix cimport Matrix

def is_FreeModuleElement(x):
    return isinstance(x, FreeModuleElement)

def Vector(R, elts):
    """
    Return a vector over R with given entries.

    INPUT:
        R -- ring
        elts -- entries of a vector
    OUTPUT:
        An element of the free module over R of rank len(elts).

    EXAMPLES:
        sage: v = Vector(Rationals(), [1,1]); v
        (1, 1)
    """
    return (R**len(elts))(elts)

cdef class FreeModuleElement(ModuleElement):
    """
    An element of a generic free module.
    """
    def __init__(self, parent):
        ModuleElement.__init__(self, parent)

    def _vector_(self, R):
        return self.change_ring(R)

    def change_ring(self, R):
        P = self.parent()
        if P.base_ring() is R:
            return self
        return P.change_ring(R)(self)

    def __abs__(self):
        return self.norm()

    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        EXAMPLES:
            sage: v = (QQ['x']^4)(0)
            sage: v == 0
            True
            sage: v == 1
            False
            sage: v == v
            True
            sage: w = v.parent()([-1,0,0,0])
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
            sage: V = Vector(ZZ, [0, 0, 0, 0])
            sage: bool(V)
            False
            sage: V = Vector(ZZ, [1, 2, 3, 5])
            sage: bool(V)
            True
        """
        return self == 0

    def __getitem__(self, i):
        raise NotImplementedError

    def __invert__(self):
        raise NotImplementedError

    def __len__(self):
        return self.parent().degree()

    def __mod__(self, p):
        """
        EXAMPLES:
            sage: V = Vector(ZZ, [5, 9, 13, 15])
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
            sage: V = Vector(ZZ, [5, 9, 13, 15])
            sage: V.Mod(7)
            (5, 2, 6, 1)
            sage: parent(V.Mod(7))
            Vector space of dimension 4 over Finite Field of size 7
        """
        return self.change_ring(self.base_ring().quotient_ring(p))

    def lift(self):
        """
        EXAMPLES:
            sage: V = Vector(ZZ/7, [5, 9, 13, 15]) ; V
            (5, 2, 6, 1)
            sage: V.lift()
            (5, 2, 6, 1)
            sage: parent(V.lift())
            Ambient free module of rank 4 over the principal ideal domain Integer Ring
        """
        return self.change_ring(self.base_ring().cover_ring())

    def test(left, right):
        """
        EXAMPLES:
            sage: v = (ZZ^5)(range(5)); v
            (0, 1, 2, 3, 4)
            sage: v * v
            30
            sage: (4/3) * v
        """
        if PY_TYPE_CHECK(right, Matrix):
            # vector x matrix multiply
            return (<FreeModuleElement>left)._matrix_multiply(<Matrix>right)
        raise TypeError


    #def __div__(left, right):
    #   return left * ~(left.parent().base_ring()(right))

    cdef ModuleElement _neg_c_impl(self):
        """
        EXAMPLES:
            sage: V = QQ^3
            sage: v = V([1,2,3])
            sage: v.__neg__()
            (-1, -2, -3)
        """
        return self._scalar_multiply(-1)

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
        # todo: speed up -- should be calling a cdef'd method of A.
        return A.vector_matrix_multiply(self)

    cdef ModuleElement _rmul_nonscalar_c_impl(left, right):
        if PY_TYPE_CHECK(right, Matrix):
            return right.vector_matrix_multiply(left)
        raise TypeError

    def degree(self):
        return self.parent().degree()

    def denominator(self):
        R = self.base_ring()
        if self.degree() == 0: return 1
        x = self.list()
        d = x[0].denominator()
        for y in x:
            d = d.lcm(y.denominator())
        return d

    def dict(self):
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

    def additive_order(self):
        import sage.rings.arith as arith
        return eval('arith.lcm([self[i].order() for i in range(self.degree())])',
                    {'self':self})

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

    def nonzero_positions(self):
        """
        Return the sorted list of integers i such that self[i] != 0.
        """
        z = self.base_ring()(0)
        v = self.list()
        return eval('[i for i in xrange(self.degree()) if v[i] != z]',
                    {'self':self, 'z':z, 'v':v})

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
def make_FreeModuleElement_generic_dense(parent, entries):
    cdef FreeModuleElement_generic_dense v
    v = FreeModuleElement_generic_dense.__new__(FreeModuleElement_generic_dense)
    v._entries = entries
    v._parent = parent
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
        return x

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
        cdef object e, v, a
        cdef Py_ssize_t i, n
        cdef PyObject **w_left, **w_right
        n = PyList_Size(left._entries)
        v = PyList_New(n)
        w_left = FAST_SEQ_UNSAFE(left._entries)
        w_right = FAST_SEQ_UNSAFE((<FreeModuleElement_generic_dense>right)._entries)
        for i from 0 <= i < n:
            a = (<RingElement>w_left[i])._add_c(<RingElement> w_right[i])
            Py_INCREF(a)
            PyList_SET_ITEM(v, i, a)
        return left._new_c(v)

    cdef ModuleElement _sub_c_impl(left, ModuleElement right):
        """
        Subtract right from left.

        EXAMPLES:
            sage: V = QQ^5
            sage: W = V.span([V.1, V.2])
            sage: W.0 - V.0
            ?
            sage: V.0 - W.0
            ?
        """
        cdef object e, v, a
        cdef Py_ssize_t i, n
        cdef PyObject **w_left, **w_right
        n = PyList_Size(left._entries)
        v = PyList_New(n)
        w_left = FAST_SEQ_UNSAFE(left._entries)
        w_right = FAST_SEQ_UNSAFE((<FreeModuleElement_generic_dense>right)._entries)
        for i from 0 <= i < n:
            a = (<RingElement>(w_left[i]))._sub_c(<RingElement> (w_right[i]))
            Py_INCREF(a)
            PyList_SET_ITEM(v, i, a)
        return left._new_c(v)

    cdef ModuleElement _rmul_c_impl(self, RingElement left):
        # This is basically a fast Python/C version of
        #    [left*x for x in self.list()]
        cdef object e, v, a
        cdef Py_ssize_t i, n
        cdef PyObject** w
        n = PyList_Size(self._entries)
        v = PyList_New(n)
        w = FAST_SEQ_UNSAFE(self._entries)
        for i from 0 <= i < n:
            a = left._mul_c(<RingElement> w[i])
            Py_INCREF(a)
            PyList_SET_ITEM(v, i, a)
        return self._new_c(v)

    cdef ModuleElement _lmul_c_impl(self, RingElement right):
        # This is basically a very fast Python/C version of
        #    [x*right for x in self.list()]
        cdef object e, v, a
        cdef Py_ssize_t i, n
        cdef PyObject** w
        n = PyList_Size(self._entries)
        v = PyList_New(n)
        w = FAST_SEQ_UNSAFE(self._entries)
        for i from 0 <= i < n:
            a = (<RingElement> w[i])._mul_c(right)
            Py_INCREF(a)
            PyList_SET_ITEM(v, i, a)
        return self._new_c(v)

    def __reduce__(self):
        return (make_FreeModuleElement_generic_dense, (self._parent, self._entries))

    def __getitem__(self, i):
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

    def __setitem__(self, i, value):
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

    def list(self, copy=True):
        if copy:
            return list(self._entries)
        else:
            return self._entries

    def __richcmp__(left, right, int op):
        a = (<Element>left)._richcmp(right, op)
        return a


    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        Compare two free module elements.

        Free module elements are compared in lexicographic order on
        the underlying list of coefficients.  A dense a sparse free
        module element are equal if their coefficients are the same.

        EXAMPLES:
        sage: ??
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

def make_FreeModuleElement_generic_sparse(parent, entries):
    cdef FreeModuleElement_generic_sparse v
    v = FreeModuleElement_generic_sparse.__new__(FreeModuleElement_generic_sparse)
    v._entries = entries
    v._parent = parent
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
        sage: loads(dumps(v)) == v
        True
    """
    cdef _new_c(self, object v):
        # Create a new sparse free module element with minimal overhead and
        # no type checking.
        cdef FreeModuleElement_generic_sparse x
        x = PY_NEW(FreeModuleElement_generic_sparse)
        x._parent = self._parent
        x._entries = v
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
        e = dict((<FreeModuleElement_generic_sparse>right)._entries)
        for i, a in left._entries.iteritems():
            if e.has_key(i):
                e[i] = (<RingElement>a)._sub_c(<RingElement> e[i])
            else:
                e[i] = a
        return left._new_c(e)


    cdef ModuleElement _lmul_c_impl(self, RingElement right):
        cdef object v
        v = PyDict_New()
        for i, a in self._entries.iteritems():
            v[i] = (<RingElement>a)._mul_c(right)
        return self._new_c(v)

    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        Compare two sparse free module elements.

        Free module elements are compared in lexicographic order on
        the underlying list of coefficients.  A dense a sparse free
        module element are equal if their coefficients are the same.

        EXAMPLES:
        sage: ??
        """
        a = left._entries.items()
        a.sort()
        b = (<FreeModuleElement_generic_dense>right)._entries.items()
        b.sort()
        return cmp(a,b)

    def iteritems(self):
        return self._entries.iteritems()

    def __reduce__(self):
        return (make_FreeModuleElement_generic_sparse, (self._parent, self._entries))

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

    def support(self):
        return self.nonzero_positions()
