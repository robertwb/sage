"""
libSingular: Functions.

Sage implements a C wrapper around the Singular interpreter which
allows to call any function directly from Sage without string parsing
or interprocess communication overhead. Users who do not want to call
Singular functions directly, usually do not have to worry about this
interface, since it is handled by higher level functions in Sage.

AUTHORS:

- Michael Brickenstein (2009-07): initial implementation, overall design
- Martin Albrecht (2009-07): clean up, enhancements, etc.
- Michael Brickenstein (2009-10): extension to more Singular types
- Martin Albrecht (2010-01): clean up, support for attributes

EXAMPLES:

The direct approach for loading a Singular function is to call the
function :func:`singular_function` with the function name as
parameter::

    sage: from sage.libs.singular.function import singular_function
    sage: P.<a,b,c,d> = PolynomialRing(GF(7))
    sage: std = singular_function('std')
    sage: I = sage.rings.ideal.Cyclic(P)
    sage: std(I)
    [a + b + c + d,
     b^2 + 2*b*d + d^2,
     b*c^2 + c^2*d - b*d^2 - d^3,
     b*c*d^2 + c^2*d^2 - b*d^3 + c*d^3 - d^4 - 1,
     b*d^4 + d^5 - b - d,
     c^3*d^2 + c^2*d^3 - c - d,
     c^2*d^4 + b*c - b*d + c*d - 2*d^2]

If a Singular library needs to be loaded before a certain function is
available, use the :func:`lib` function as shown below::

    sage: from sage.libs.singular.function import singular_function, lib as singular_lib
    sage: primdecSY = singular_function('primdecSY')
    Traceback (most recent call last):
    ...
    NameError: Function 'primdecSY' is not defined.

    sage: singular_lib('primdec.lib')
    sage: primdecSY = singular_function('primdecSY')

There is also a short-hand notation for the above::

    sage: primdecSY = sage.libs.singular.ff.primdec__lib.primdecSY

The above line will load "primdec.lib" first and then load the
function ``primdecSY``.

TESTS::

    sage: from sage.libs.singular.function import singular_function
    sage: std = singular_function('std')
    sage: loads(dumps(std)) == std
    True
"""
#*****************************************************************************
#       Copyright (C) 2009 Michael Brickenstein <brickenstein@mfo.de>
#       Copyright (C) 2009,2010 Martin Albrecht <M.R.Albrecht@rhul.ac.uk>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from __future__ import with_statement

include "../../ext/stdsage.pxi"
include "../../ext/interrupt.pxi"

from sage.structure.sage_object cimport SageObject

from sage.rings.integer cimport Integer

from sage.modules.free_module_element cimport FreeModuleElement_generic_dense

from sage.rings.polynomial.multi_polynomial_libsingular cimport MPolynomial_libsingular, new_MP
from sage.rings.polynomial.multi_polynomial_libsingular cimport MPolynomialRing_libsingular

from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal

from sage.rings.polynomial.multi_polynomial_ideal_libsingular cimport sage_ideal_to_singular_ideal, singular_ideal_to_sage_sequence

from sage.libs.singular.decl cimport leftv, idhdl, poly, ideal, ring, number, intvec, lists
from sage.libs.singular.decl cimport sleftv_bin, omAllocBin, omFreeBin, omStrDup, slists_bin, omAlloc0Bin
from sage.libs.singular.decl cimport iiMake_proc, iiExprArith1, iiExprArith2, iiExprArith3, iiExprArithM, iiLibCmd
from sage.libs.singular.decl cimport ggetid, IDEAL_CMD, CMD_M, POLY_CMD, PROC_CMD, RING_CMD, QRING_CMD, NUMBER_CMD, INT_CMD, INTVEC_CMD, RESOLUTION_CMD
from sage.libs.singular.decl cimport MODUL_CMD, LIST_CMD, MATRIX_CMD, VECTOR_CMD, STRING_CMD, V_LOAD_LIB, V_REDEFINE, INTMAT_CMD, NONE, PACKAGE_CMD
from sage.libs.singular.decl cimport IsCmd, rChangeCurrRing, currRing, p_Copy
from sage.libs.singular.decl cimport IDROOT, enterid, currRingHdl, memcpy, IDNEXT, IDTYP, IDPACKAGE
from sage.libs.singular.decl cimport errorreported, verbose, Sy_bit, currentVoice, myynest
from sage.libs.singular.decl cimport intvec_new_int3, intvec_new, matrix, mpNew
from sage.libs.singular.decl cimport p_Add_q, p_SetComp, p_GetComp, pNext, p_Setm, IDELEMS
from sage.libs.singular.decl cimport idInit, syStrategy, atSet, atGet, setFlag, FLAG_STD

from sage.libs.singular.option import opt_ctx
from sage.libs.singular.polynomial cimport singular_vector_maximal_component
from sage.libs.singular.singular cimport sa2si, si2sa, si2sa_intvec

from sage.libs.singular.singular import error_messages

from sage.interfaces.singular import get_docstring

from sage.misc.misc import get_verbose

from sage.structure.sequence import Sequence, Sequence_generic
from sage.rings.polynomial.multi_polynomial_sequence import PolynomialSequence


cdef poly* sage_vector_to_poly(v, ring *r) except <poly*> -1:
    """
    Convert a vector or list of multivariate polynomials to a
    polynomial by adding them all up.
    """
    cdef poly *res = NULL
    cdef poly *poly_component
    cdef poly *p_iter
    cdef int component

    for (i, p) in enumerate(v):
        component = <int>i+1
        poly_component = p_Copy(
            (<MPolynomial_libsingular>p)._poly, r)
        p_iter = poly_component
        while p_iter!=NULL:
            p_SetComp(p_iter, component, r)
            p_Setm(p_iter, r)
            p_iter=pNext(p_iter)
        res=p_Add_q(res, poly_component, r)
    return res

cdef class RingWrap:
    """
    A simple wrapper around Singular's rings.
    """
    def __repr__(self):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import singular_function
            sage: P.<x,y,z> = PolynomialRing(QQ)
            sage: ringlist = singular_function("ringlist")
            sage: l = ringlist(P)
            sage: ring = singular_function("ring")
            sage: ring(l, ring=P)
            <RingWrap>
        """
        return "<RingWrap>"

    def __dealloc__(self):
        if self._ring!=NULL:
            self._ring.ref -= 1

cdef class Resolution:
    """
    A simple wrapper around Singular's resolutions.
    """
    def __init__(self, base_ring):
        """
        EXAMPLE::

           sage: from sage.libs.singular.function import singular_function
           sage: mres = singular_function("mres")
           sage: syz = singular_function("syz")
           sage: P.<x,y,z> = PolynomialRing(QQ)
           sage: I = P.ideal([x+y,x*y-y, y*2,x**2+1])
           sage: M = syz(I)
           sage: resolution = mres(M, 0)
        """
        assert PY_TYPE_CHECK(base_ring, MPolynomialRing_libsingular)
        self.base_ring = <MPolynomialRing_libsingular> base_ring
    def __repr__(self):
        """
        EXAMPLE::

           sage: from sage.libs.singular.function import singular_function
           sage: mres = singular_function("mres")
           sage: syz = singular_function("syz")
           sage: P.<x,y,z> = PolynomialRing(QQ)
           sage: I = P.ideal([x+y,x*y-y, y*2,x**2+1])
           sage: M = syz(I)
           sage: resolution = mres(M, 0)
           sage: resolution
           <Resolution>
        """
        return "<Resolution>"
    def __dealloc__(self):
        """
        EXAMPLE::

           sage: from sage.libs.singular.function import singular_function
           sage: mres = singular_function("mres")
           sage: syz = singular_function("syz")
           sage: P.<x,y,z> = PolynomialRing(QQ)
           sage: I = P.ideal([x+y,x*y-y, y*2,x**2+1])
           sage: M = syz(I)
           sage: resolution = mres(M, 0)
           sage: del resolution
        """
        if self._resolution != NULL:
            self._resolution.references -= 1

cdef leftv* new_leftv(void *data, res_type):
    """
    INPUT:

    - ``data`` - some Singular data this interpreter object points to

    - ``res_type`` - the type of that data
    """
    cdef leftv* res
    res = <leftv*>omAllocBin(sleftv_bin)
    res.Init()
    res.data = data
    res.rtyp = res_type
    return res

cdef free_leftv(leftv * args):
    """
    Kills this ``leftv`` and all ``leftv``s in the tail.

    INPUT:

    - ``args`` - a list of Singular arguments
    """
    args.CleanUp()
    omFreeBin(args, sleftv_bin)


def all_polynomials(s):
    """
    Tests for a sequence ``s``, whether it consists of
    singular polynomials.

    EXAMPLE::

        sage: from sage.libs.singular.function import all_polynomials
        sage: P.<x,y,z> = QQ[]
        sage: all_polynomials([x+1, y])
        True
        sage: all_polynomials([x+1, y, 1])
        False
    """
    for p in s:
        if not isinstance(p, MPolynomial_libsingular):
            return False
    return True

def all_vectors(s):
    """
    Checks if a sequence ``s`` consists of free module
    elements over a singular ring.

    EXAMPLE::

        sage: from sage.libs.singular.function import all_vectors
        sage: P.<x,y,z> = QQ[]
        sage: M = P**2
        sage: all_vectors([x])
        False
        sage: all_vectors([(x,y)])
        False
        sage: all_vectors([M(0), M((x,y))])
        True
        sage: all_vectors([M(0), M((x,y)),(0,0)])
        False
    """
    for p in s:
        if not (isinstance(p, FreeModuleElement_generic_dense)\
            and isinstance(p.parent().base_ring(), MPolynomialRing_libsingular)):
            return False
    return True



cdef class Converter(SageObject):
    """
    A :class:`Converter` interfaces between Sage objects and Singular
    interpreter objects.
    """

    def __init__(self, args, ring, attributes=None):
        """
        Create a new argument list.

        INPUT:

        - ``args`` - a list of Python objects

        - ``ring`` - a multivariate polynomial ring

        - ``attributes`` - an optional dictionary of Singular
                           attributes (default: ``None``)

        EXAMPLE::

            sage: from sage.libs.singular.function import Converter
            sage: P.<a,b,c> = PolynomialRing(GF(127))
            sage: Converter([a,b,c],ring=P)
            Singular Converter in Multivariate Polynomial Ring in a, b, c over Finite Field of size 127
        """
        cdef leftv *v
        self.args = NULL
        self._ring = ring
        from  sage.matrix.matrix_mpolynomial_dense import Matrix_mpolynomial_dense
        from sage.matrix.matrix_integer_dense import Matrix_integer_dense
        for a in args:
            if PY_TYPE_CHECK(a, MPolynomial_libsingular):
                v = self.append_polynomial(<MPolynomial_libsingular> a)

            elif PY_TYPE_CHECK(a, MPolynomialRing_libsingular):
                v = self.append_ring(<MPolynomialRing_libsingular> a)

            elif PY_TYPE_CHECK(a, MPolynomialIdeal):
                v = self.append_ideal(a)

            elif PY_TYPE_CHECK(a, int) or PY_TYPE_CHECK(a, long):
                v = self.append_int(a)

            elif PY_TYPE_CHECK(a, basestring):
                v = self.append_str(a)

            elif PY_TYPE_CHECK(a, Matrix_mpolynomial_dense):
                v = self.append_matrix(a)

            elif PY_TYPE_CHECK(a, Matrix_integer_dense):
                v = self.append_intmat(a)

            elif PY_TYPE_CHECK(a, Resolution):
                v = self.append_resolution(a)

            elif PY_TYPE_CHECK(a, FreeModuleElement_generic_dense)\
                and isinstance(
                    a.parent().base_ring(),
                    MPolynomialRing_libsingular):
                v = self.append_vector(a)

            # as output ideals get converted to sequences
            # sequences of polynomials should get converted to ideals
            # this means, that Singular lists should not be converted to Sequences,
            # as we do not want ambiguities
            elif PY_TYPE_CHECK(a, Sequence_generic)\
                and all_polynomials(a):
                v = self.append_ideal(ring.ideal(a))
            elif PY_TYPE_CHECK(a, PolynomialSequence):
                v = self.append_ideal(ring.ideal(a))
            elif PY_TYPE_CHECK(a, Sequence_generic)\
                and all_vectors(a):
                v = self.append_module(a)
            elif PY_TYPE_CHECK(a, list):
                v = self.append_list(a)

            elif PY_TYPE_CHECK(a, tuple):
                is_intvec = True
                for i in a:
                    if not (PY_TYPE_CHECK(i, int)
                        or PY_TYPE_CHECK(i, Integer)):
                        is_intvec = False
                        break
                if is_intvec:
                    v = self.append_intvec(a)
                else:
                    v = self.append_list(a)
            elif a.parent() is self._ring.base_ring():
                v = self.append_number(a)

            elif PY_TYPE_CHECK(a, Integer):
                v = self.append_int(a)

            else:
                raise TypeError("unknown argument type '%s'"%(type(a),))

            if attributes and a in attributes:
                for attrib in attributes[a]:
                    if attrib == "isSB" :
                        val = int(attributes[a][attrib])
                        atSet(v, omStrDup("isSB"), <void*><int>val, INT_CMD)
                        setFlag(v, FLAG_STD)
                    else:
                        raise NotImplementedError("Support for attribute '%s' not implemented yet."%attrib)

    def ring(self):
        """
        Return the ring in which the arguments of this list live.

        EXAMPLE::

            sage: from sage.libs.singular.function import Converter
            sage: P.<a,b,c> = PolynomialRing(GF(127))
            sage: Converter([a,b,c],ring=P).ring()
            Multivariate Polynomial Ring in a, b, c over Finite Field of size 127
        """
        return self._ring

    def _repr_(self):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import Converter
            sage: P.<a,b,c> = PolynomialRing(GF(127))
            sage: Converter([a,b,c],ring=P) # indirect doctest
            Singular Converter in Multivariate Polynomial Ring in a, b, c over Finite Field of size 127
        """
        return "Singular Converter in %s"%(self._ring)

    def __dealloc__(self):
        if self.args:
            free_leftv(self.args)

    def __len__(self):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import Converter
            sage: P.<a,b,c> = PolynomialRing(GF(127))
            sage: len(Converter([a,b,c],ring=P))
            3
        """
        cdef leftv * v
        v=self.args
        cdef int l
        l=0
        while v != NULL:
            l=l+1
            v=v.next
        return l

    cdef leftv* pop_front(self) except NULL:
        """
        Pop a Singular element from the front of the list.
        """
        assert(self.args != NULL)
        cdef leftv *res = self.args
        self.args = self.args.next
        res.next = NULL
        return res

    cdef leftv *_append_leftv(self, leftv *v):
        """
        Append a new Singular element to the list.
        """
        cdef leftv* last
        if not self.args == NULL:
            last = self.args
            while not last.next == NULL:
                last=last.next
            last.next=v
        else:
            self.args = v
        return v

    cdef leftv *_append(self, void* data, int res_type):
        """
        Create a new ``leftv`` and append it to the list.

        INPUT:

        - ``data`` - the raw data

        - ``res_type`` - the type of the data
        """
        return self._append_leftv( new_leftv(data, res_type) )

    cdef to_sage_matrix(self, matrix* mat):
        """
        Convert singular matrix to matrix over the polynomial ring.
        """
        from sage.matrix.constructor import Matrix
        sage_ring = self._ring
        cdef ring *singular_ring = (<MPolynomialRing_libsingular>\
            sage_ring)._ring
        ncols = mat.ncols
        nrows = mat.nrows
        result = Matrix(sage_ring, nrows, ncols)
        cdef MPolynomial_libsingular p
        for i in xrange(nrows):
            for j in xrange(ncols):
                p = MPolynomial_libsingular(sage_ring)
                p._poly = mat.m[i*ncols+j]
                mat.m[i*ncols+j]=NULL
                result[i,j] = p
        return result

    cdef to_sage_vector_destructive(self, poly *p, free_module = None):
        cdef ring *r=self._ring._ring
        cdef int rank
        if free_module:
            rank = free_module.rank()
        else:
            rank = singular_vector_maximal_component(p, r)
            free_module = self._ring**rank
        cdef poly *acc
        cdef poly *p_iter
        cdef poly *first
        cdef poly *previous
        cdef int i
        result = []
        for i from 1 <= i <= rank:
            previous = NULL
            acc = NULL
            first = NULL
            p_iter=p
            while p_iter != NULL:
                if p_GetComp(p_iter, r) == i:
                    p_SetComp(p_iter,0, r)
                    p_Setm(p_iter, r)
                    if acc == NULL:
                        first = p_iter
                    else:
                        acc.next = p_iter
                    acc = p_iter
                    if p_iter==p:
                        p=pNext(p_iter)
                    if previous != NULL:
                        previous.next=pNext(p_iter)
                    p_iter = pNext(p_iter)
                    acc.next = NULL
                else:
                    previous = p_iter
                    p_iter = pNext(p_iter)
            result.append(new_MP(self._ring, first))
        return free_module(result)

    cdef object to_sage_module_element_sequence_destructive( self, ideal *i):
        """
        Convert a SINGULAR module to a Sage Sequence (the format Sage
        stores a Groebner basis in).

        INPUT:

        - ``i`` -- a SINGULAR ideal
        - ``r`` -- a SINGULAR ring
        - ``sage_ring`` -- a Sage ring matching r
        """
        cdef MPolynomialRing_libsingular sage_ring = self._ring
        cdef int j
        cdef int rank=i.rank
        free_module = sage_ring**rank
        l = []

        for j from 0 <= j < IDELEMS(i):
            p = self.to_sage_vector_destructive(
                i.m[j], free_module)
            i.m[j]=NULL#save it from getting freed
            l.append( p )

        return Sequence(l, check=False, immutable=True)


    cdef to_sage_integer_matrix(self, intvec* mat):
        """
        Convert Singular matrix to matrix over the polynomial ring.
        """
        from sage.matrix.constructor import Matrix
        from sage.rings.integer_ring import ZZ

        ncols = mat.cols()
        nrows = mat.rows()

        result = Matrix(ZZ, nrows, ncols)
        for i in xrange(nrows):
            for j in xrange(ncols):
                result[i,j] = mat.get(i*ncols+j)
        return result


    cdef leftv *append_polynomial(self, MPolynomial_libsingular p) except NULL:
        """
        Append the polynomial ``p`` to the list.
        """
        cdef poly* _p = p_Copy(p._poly, <ring*>(<MPolynomialRing_libsingular>p._parent)._ring)
        return self._append(_p, POLY_CMD)

    cdef leftv *append_ideal(self,  i) except NULL:
        """
        Append the ideal ``i`` to the list.
        """
        cdef ideal* singular_ideal = sage_ideal_to_singular_ideal(i)
        return self._append(singular_ideal, IDEAL_CMD)

    cdef leftv *append_module(self, m) except NULL:
        """
        Append sequence ``m`` of vectors over the polynomial ring to
        the list
        """
        rank = max([v.parent().rank() for v in m])
        cdef ideal *result
        cdef ring *r = self._ring._ring
        cdef ideal *i
        cdef int j = 0



        i = idInit(len(m),rank)
        for f in m:
            i.m[j] = sage_vector_to_poly(f, r)
            j+=1
        return self._append(<void*> i, MODUL_CMD)

    cdef leftv *append_number(self, n) except NULL:
        """
        Append the number ``n`` to the list.
        """
        cdef number *_n =  sa2si(n, self._ring._ring)
        return self._append(<void *>_n, NUMBER_CMD)

    cdef leftv *append_ring(self, MPolynomialRing_libsingular r) except NULL:
        """
        Append the ring ``r`` to the list.
        """
        cdef ring *_r =  <ring*> r._ring
        _r.ref+=1
        return self._append(<void *>_r, RING_CMD)

    cdef leftv *append_matrix(self, mat) except NULL:

        sage_ring = mat.base_ring()
        cdef ring *r=<ring*> (<MPolynomialRing_libsingular> sage_ring)._ring

        cdef poly *p
        ncols = mat.ncols()
        nrows = mat.nrows()
        cdef matrix* _m=mpNew(nrows,ncols)
        for i in xrange(nrows):
            for j in xrange(ncols):
                p = p_Copy(
                    (<MPolynomial_libsingular> mat[i,j])._poly, r)
                _m.m[ncols*i+j]=p
        return self._append(_m, MATRIX_CMD)

    cdef leftv *append_int(self, n) except NULL:
        """
        Append the integer ``n`` to the list.
        """
        cdef long _n =  n
        return self._append(<void*>_n, INT_CMD)



    cdef leftv *append_list(self, l) except NULL:
        """
        Append the list ``l`` to the list.
        """

        cdef Converter c = Converter(l, self._ring)
        n = len(c)

        cdef lists *singular_list=<lists*>omAlloc0Bin(slists_bin)
        singular_list.Init(n)
        cdef leftv* iv
        for i in xrange(n):
          iv=c.pop_front()
          memcpy(&singular_list.m[i],iv,sizeof(leftv))
          omFreeBin(iv, sleftv_bin)

        return self._append(<void*>singular_list, LIST_CMD)

    cdef leftv *append_intvec(self, a) except NULL:
        """
        Append ``a`` to the list as intvec.
        """
        s = len(a)
        cdef intvec *iv=intvec_new()
        iv.resize(s)
        #new intvec(s);

        for i in xrange(s):
            iv.ivGetVec()[i]=<int>a[i]
        return self._append(<void*>iv, INTVEC_CMD)

    cdef leftv *append_vector(self, v) except NULL:
        """
        Append vector ``v`` from free
        module over polynomial ring.
        """
        cdef ring *r = self._ring._ring
        cdef poly *p = sage_vector_to_poly(v, r)
        return self._append(<void*> p, VECTOR_CMD)

    cdef leftv *append_resolution(self, Resolution resolution) except NULL:
        """
        Append free resolution ``r`` to the list.
        """
        resolution._resolution.references += 1
        return self._append(<void*> resolution._resolution, RESOLUTION_CMD)

    cdef leftv *append_intmat(self, a) except NULL:
        """
        Append ``a`` to the list as intvec.
        """
        cdef int nrows = <int> a.nrows()
        cdef int ncols = <int> a.ncols()
        cdef intvec *iv=intvec_new_int3(nrows, ncols, 0)
        #new intvec(s);

        for i in xrange(nrows):
            for j in xrange(ncols):
                iv.ivGetVec()[i*ncols+j]=<int>a[i,j]
        return self._append(<void*>iv, INTMAT_CMD)

    cdef leftv *append_str(self, n) except NULL:
        """
        Append the string ``n`` to the list.
        """
        cdef char *_n = <char *>n
        return self._append(omStrDup(_n), STRING_CMD)

    cdef to_python(self, leftv* to_convert):
        """
        Convert the ``leftv`` to a Python object.

        INPUT:

        - ``to_convert`` - a Singular ``leftv``
        """
        cdef MPolynomial_libsingular res_poly
        cdef int rtyp = to_convert.rtyp
        cdef lists *singular_list
        cdef Resolution res_resolution
        if rtyp == IDEAL_CMD:
            return singular_ideal_to_sage_sequence(<ideal*>to_convert.data, self._ring._ring, self._ring)

        elif rtyp == POLY_CMD:
            res_poly = MPolynomial_libsingular(self._ring)
            res_poly._poly = <poly*>to_convert.data
            to_convert.data = NULL
            #prevent it getting free, when cleaning the leftv
            return res_poly

        elif rtyp == INT_CMD:
            return <long>to_convert.data

        elif rtyp == NUMBER_CMD:
            return si2sa(<number *>to_convert.data, self._ring._ring, self._ring.base_ring())

        elif rtyp == INTVEC_CMD:
            return si2sa_intvec(<intvec *>to_convert.data)

        elif rtyp == STRING_CMD:
            ret = <char *>to_convert.data
            return ret
        elif rtyp == VECTOR_CMD:
            result = self.to_sage_vector_destructive(
                <poly *> to_convert.data)
            to_convert.data = NULL
            return result


        elif rtyp == RING_CMD or rtyp==QRING_CMD:
            ring_wrap_result=RingWrap()
            (<RingWrap> ring_wrap_result)._ring=<ring*> to_convert.data
            (<RingWrap> ring_wrap_result)._ring.ref+=1
            return ring_wrap_result

        elif rtyp == MATRIX_CMD:
            return self.to_sage_matrix(<matrix*>  to_convert.data )

        elif rtyp == LIST_CMD:
            singular_list = <lists*> to_convert.data
            ret = []
            for i in xrange(singular_list.nr+1):
                ret.append(
                    self.to_python(
                        &(singular_list.m[i])))
            return ret


        elif rtyp == MODUL_CMD:
            return self.to_sage_module_element_sequence_destructive(
                <ideal*> to_convert.data
            )
        elif rtyp == INTMAT_CMD:
            return self.to_sage_integer_matrix(
                <intvec*> to_convert.data)
        elif rtyp == RESOLUTION_CMD:
            res_resolution = Resolution(self._ring)
            res_resolution._resolution = <syStrategy*> to_convert.data
            res_resolution._resolution.references += 1
            return res_resolution
        elif rtyp == NONE:
            return None
        else:
            raise NotImplementedError("rtyp %d not implemented."%(rtyp))

cdef class BaseCallHandler:
    """
    A call handler is an abstraction which hides the details of the
    implementation differences between kernel and library functions.
    """
    cdef leftv* handle_call(self, Converter argument_list):
        """
        Actual function call.
        """
        return NULL

    cdef bint free_res(self):
        """
        Do we need to free the result object.
        """
        return False

cdef class LibraryCallHandler(BaseCallHandler):
    """
    A call handler is an abstraction which hides the details of the
    implementation differences between kernel and library functions.

    This class implements calling a library function.

    .. note::

        Do not construct this class directly, use
        :func:`singular_function` instead.
    """
    def __init__(self):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import LibraryCallHandler
            sage: LibraryCallHandler()
            <sage.libs.singular.function.LibraryCallHandler object at 0x...>
        """
        super(LibraryCallHandler, self).__init__()

    cdef leftv* handle_call(self, Converter argument_list):
        return iiMake_proc(self.proc_idhdl, NULL, argument_list.args)

    cdef bint free_res(self):
        """
        We do not need to free the result object for library
        functions.
        """
        return False

cdef class KernelCallHandler(BaseCallHandler):
    """
    A call handler is an abstraction which hides the details of the
    implementation differences between kernel and library functions.

    This class implements calling a kernel function.

    .. note::

        Do not construct this class directly, use
        :func:`singular_function` instead.
    """
    def __init__(self, cmd_n, arity):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import KernelCallHandler
            sage: KernelCallHandler(0,0)
            <sage.libs.singular.function.KernelCallHandler object at 0x...>
        """
        super(KernelCallHandler, self).__init__()
        self.cmd_n = cmd_n
        self.arity = arity

    cdef leftv* handle_call(self, Converter argument_list):
        cdef leftv * res
        res = <leftv*> omAllocBin(sleftv_bin)
        res.Init()
        cdef leftv *arg1
        cdef leftv *arg2
        cdef leftv *arg3
        if self.arity != CMD_M:
            number_of_arguments=len(argument_list)

            if number_of_arguments == 1:
                arg1 = argument_list.pop_front()
                iiExprArith1(res, arg1, self.cmd_n)
                free_leftv(arg1)

            elif number_of_arguments == 2:
                arg1 = argument_list.pop_front()
                arg2 = argument_list.pop_front()
                iiExprArith2(res, arg1, self.cmd_n, arg2, self.cmd_n>255)
                free_leftv(arg1)
                free_leftv(arg2)

            elif number_of_arguments == 3:
                arg1 = argument_list.pop_front()
                arg2 = argument_list.pop_front()
                arg3 = argument_list.pop_front()
                iiExprArith3(res, self.cmd_n, arg1, arg2, arg3)
                free_leftv(arg1)
                free_leftv(arg2)
                free_leftv(arg3)
        else:
          iiExprArithM(res, argument_list.args, self.cmd_n)

        return res

    cdef bint free_res(self):
        """
        We need to free the result object for kernel functions.
        """
        return True

cdef class SingularFunction(SageObject):
    """
    The base class for Singular functions either from the kernel or
    from the library.
    """
    def __init__(self, name):
        """
        INPUT:

        - ``name`` - the name of the function

        EXAMPLE::

            sage: from sage.libs.singular.function import SingularFunction
            sage: SingularFunction('foobar')
            foobar (singular function)
        """
        self._name = name

        global currRingHdl
        if currRingHdl == NULL:
            currRingHdl = enterid("my_awesome_sage_ring", 0, RING_CMD, &IDROOT, 1)
            currRingHdl.data.uring.ref += 1

    cdef BaseCallHandler get_call_handler(self):
        """
        Return a call handler which does the actual work.
        """
        raise NotImplementedError

    cdef bint function_exists(self):
        """
        Return ``True`` if the function exists in this interface.
        """
        raise NotImplementedError

    def _repr_(self):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import SingularFunction
            sage: SingularFunction('foobar') # indirect doctest
            foobar (singular function)
        """
        return "%s (singular function)" %(self._name)

    def __call__(self, *args, MPolynomialRing_libsingular ring=None, bint interruptible=True, attributes=None):
        """
        Call this function with the provided arguments ``args`` in the
        ring ``R``.

        INPUT:

        - ``args`` - a list of arguments

        - ``ring`` - a multivariate polynomial ring

        - ``interruptible`` - if ``True`` pressing Ctrl-C during the
                              execution of this function will
                              interrupt the computation (default: ``True``)

        - ``attributes`` - a dictionary of optional Singular
                           attributes assigned to Singular objects (default: ``None``)

        EXAMPLE::

            sage: from sage.libs.singular.function import singular_function
            sage: size = singular_function('size')
            sage: P.<a,b,c> = PolynomialRing(QQ)
            sage: size(a, ring=P)
            1
            sage: size(2r,ring=P)
            1
            sage: size(2, ring=P)
            1
            sage: size(2)
            Traceback (most recent call last):
            ...
            ValueError: Could not detect ring.
            sage: size(Ideal([a*b + c, a + 1]), ring=P)
            2
            sage: size(Ideal([a*b + c, a + 1]))
            2
            sage: size(1,2, ring=P)
            Traceback (most recent call last):
            ...
            RuntimeError: Error in Singular function call 'size':
             size(`int`,`int`) failed

            sage: size('foobar', ring=P)
            6

        Show the usage of the optional ``attributes`` parameter::

            sage: P.<x,y,z> = PolynomialRing(QQ)
            sage: I = Ideal([x^3*y^2 + 3*x^2*y^2*z + y^3*z^2 + z^5])
            sage: I = Ideal(I.groebner_basis())
            sage: hilb = sage.libs.singular.ff.hilb
            sage: hilb(I) # Singular will print // ** _ is no standard basis

        So we tell Singular that ``I`` is indeed a Groebner basis::

            sage: hilb(I,attributes={I:{'isSB':1}}) # no complaint from Singular


        TESTS:

        We show that the interface recovers gracefully from errors::

            sage: P.<e,d,c,b,a> = PolynomialRing(QQ,5,order='lex')
            sage: I = sage.rings.ideal.Cyclic(P)

            sage: triangL = sage.libs.singular.ff.triang__lib.triangL
            sage: _ = triangL(I)
            Traceback (most recent call last):
            ...
            RuntimeError: Error in Singular function call 'triangL':
             The input is no groebner basis.
             leaving triang.lib::triangL

            sage: G= Ideal(I.groebner_basis())
            sage: triangL(G,attributes={G:{'isSB':1}})
            [[e + d + c + b + a, ...]]
        """
        if ring is None:
            ring = self.common_ring(args, ring)
        if not PY_TYPE_CHECK(ring, MPolynomialRing_libsingular):
            raise TypeError("Cannot call Singular function '%s' with ring parameter of type '%s'"%(self._name,type(ring)))
        return call_function(self, args, ring, interruptible, attributes)

    def _sage_doc_(self):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import singular_function
            sage: groebner = singular_function('groebner')
            sage: 'groebner' in groebner._sage_doc_()
            True
        """

        prefix = \
"""
This function is an automatically generated C wrapper around the Singular
function '%s'.

This wrapper takes care of converting Sage datatypes to Singular
datatypes and vice versa. In addition to whatever parameters the
underlying Singular function accepts when called this function also
accepts the following keyword parameters:

INPUT:

- ``args`` - a list of arguments
- ``ring`` - a multivariate polynomial ring
- ``interruptible`` - if ``True`` pressing Ctrl-C during the
                      execution of this function will
                      interrupt the computation (default: ``True``)
- ``attributes`` - a dictionary of optional Singular
                   attributes assigned to Singular objects (default: ``None``)

EXAMPLE::

    sage: groebner = sage.libs.singular.ff.groebner
    sage: P.<x, y> = PolynomialRing(QQ)
    sage: I = P.ideal(x^2-y, y+x)
    sage: groebner(I)
    [x + y, y^2 - y]

    sage: triangL = sage.libs.singular.ff.triang__lib.triangL
    sage: P.<x1, x2> = PolynomialRing(QQ, order='lex')
    sage: f1 = 1/2*((x1^2 + 2*x1 - 4)*x2^2 + 2*(x1^2 + x1)*x2 + x1^2)
    sage: f2 = 1/2*((x1^2 + 2*x1 + 1)*x2^2 + 2*(x1^2 + x1)*x2 - 4*x1^2)
    sage: I = Ideal(Ideal(f1,f2).groebner_basis()[::-1])
    sage: triangL(I, attributes={I:{'isSB':1}})
    [[x2^4 + 4*x2^3 - 6*x2^2 - 20*x2 + 5, 8*x1 - x2^3 + x2^2 + 13*x2 - 5],
     [x2, x1^2],
     [x2, x1^2],
     [x2, x1^2]]

The Singular documentation for '%s' is given below.
"""%(self._name,self._name)

        return prefix + get_docstring(self._name)

    cdef MPolynomialRing_libsingular common_ring(self, tuple args, ring=None):
        """
        Return the common ring for the argument list ``args``.

        If ``ring`` is not ``None`` this routine checks whether it is
        the parent/ring of all members of ``args`` instead.

        If no common ring was found a ``ValueError`` is raised.

        INPUT:

        - ``args`` - a list of Python objects

        - ``ring`` - an optional ring to check
        """
        from  sage.matrix.matrix_mpolynomial_dense import Matrix_mpolynomial_dense
        from sage.matrix.matrix_integer_dense import Matrix_integer_dense
        for a in args:
            if PY_TYPE_CHECK(a, MPolynomialIdeal):
                ring2 = a.ring()
            elif PY_TYPE_CHECK(a, MPolynomial_libsingular):
                ring2 = a.parent()
            elif PY_TYPE_CHECK(a, MPolynomialRing_libsingular):
                ring2 = a
            elif PY_TYPE_CHECK(a, int) or PY_TYPE_CHECK(a, long) or PY_TYPE_CHECK(a, basestring):
                continue
            elif PY_TYPE_CHECK(a, Matrix_integer_dense):
                continue
            elif PY_TYPE_CHECK(a, Matrix_mpolynomial_dense):
                ring2 = a.base_ring()
            elif PY_TYPE_CHECK(a, list) or PY_TYPE_CHECK(a, tuple)\
                or PY_TYPE_CHECK(a, Sequence_generic):
                #TODO: catch exception, if recursion finds no ring
                ring2 = self.common_ring(tuple(a), ring)
            elif PY_TYPE_CHECK(a, Resolution):
                ring2 = (<Resolution> a).base_ring
            elif PY_TYPE_CHECK(a, FreeModuleElement_generic_dense)\
                and PY_TYPE_CHECK(
                    a.parent().base_ring(),
                     MPolynomialRing_libsingular):
                ring2 = a.parent().base_ring()
            elif ring is not None:
                a.parent() is ring
                continue

            if ring is None:
                ring = ring2
            elif ring is not ring2:
                raise ValueError("Rings do not match up.")
        if ring is None:
            raise ValueError("Could not detect ring.")
        return <MPolynomialRing_libsingular>ring

    def __reduce__(self):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import singular_function
            sage: groebner = singular_function('groebner')
            sage: groebner == loads(dumps(groebner))
            True
        """
        return singular_function, (self._name,)

    def __cmp__(self, other):
        """
        EXAMPLE::

            sage: from sage.libs.singular.function import singular_function
            sage: groebner = singular_function('groebner')
            sage: groebner == singular_function('groebner')
            True
            sage: groebner == singular_function('std')
            False
            sage: groebner == 1
            False
        """
        if not PY_TYPE_CHECK(other, SingularFunction):
            return cmp(type(self),type(other))
        else:
            return cmp(self._name, (<SingularFunction>other)._name)

cdef inline call_function(SingularFunction self, tuple args, MPolynomialRing_libsingular R, bint signal_handler=True, attributes=None):
    global currRingHdl
    global errorreported
    global currentVoice
    global myynest
    global error_messages


    cdef ring *si_ring = R._ring

    if si_ring != currRing:
        rChangeCurrRing(si_ring)

    if currRingHdl.data.uring!= currRing:
        currRingHdl.data.uring.ref -= 1
        currRingHdl.data.uring = currRing # ref counting?
        currRingHdl.data.uring.ref += 1

    cdef Converter argument_list = Converter(args, R, attributes)

    cdef leftv * _res

    currentVoice = NULL
    myynest = 0
    errorreported = 0

    while error_messages:
        error_messages.pop()

    with opt_ctx: # we are preserving the global options state here
        if signal_handler:
            sig_on()
            _res = self.call_handler.handle_call(argument_list)
            sig_off()
        else:
            _res = self.call_handler.handle_call(argument_list)

    if myynest:
        myynest = 0

    if currentVoice:
        currentVoice = NULL

    if errorreported:
        errorreported = 0
        error_msg = " " + "\n ".join(error_messages)
        raise RuntimeError("Error in Singular function call '%s':\n%s"%(self._name,
                                                                           error_msg))

    res = argument_list.to_python(_res)

    if self.call_handler.free_res():
        free_leftv(_res)
    else:
        _res.CleanUp()

    return res

cdef class SingularLibraryFunction(SingularFunction):
    """
    EXAMPLES::

        sage: from sage.libs.singular.function import SingularLibraryFunction
        sage: R.<x,y> = PolynomialRing(QQ, order='lex')
        sage: I = R.ideal(x, x+1)
        sage: f = SingularLibraryFunction("groebner")
        sage: f(I)
        [1]
    """
    def __init__(self, name):
        """
        Construct a new Singular kernel function.

        EXAMPLES::

            sage: from sage.libs.singular.function import SingularLibraryFunction
            sage: R.<x,y> = PolynomialRing(QQ, order='lex')
            sage: I = R.ideal(x + 1, x*y + 1)
            sage: f = SingularLibraryFunction("groebner")
            sage: f(I)
            [y - 1, x + 1]
        """
        super(SingularLibraryFunction,self).__init__(name)
        self.call_handler = self.get_call_handler()

    cdef BaseCallHandler get_call_handler(self):
        cdef idhdl* singular_idhdl = ggetid(self._name)
        if singular_idhdl==NULL:
            raise NameError("Function '%s' is not defined."%self._name)
        if singular_idhdl.typ!=PROC_CMD:
            raise ValueError("Not a procedure")

        cdef LibraryCallHandler res = LibraryCallHandler()
        res.proc_idhdl = singular_idhdl
        return res

    cdef bint function_exists(self):
        cdef idhdl* singular_idhdl = ggetid(self._name)
        return singular_idhdl!=NULL

cdef class SingularKernelFunction(SingularFunction):
    """
    EXAMPLES::

        sage: from sage.libs.singular.function import SingularKernelFunction
        sage: R.<x,y> = PolynomialRing(QQ, order='lex')
        sage: I = R.ideal(x, x+1)
        sage: f = SingularKernelFunction("std")
        sage: f(I)
        [1]
    """
    def __init__(self, name):
        """
        Construct a new Singular kernel function.

        EXAMPLES::

            sage: from sage.libs.singular.function import SingularKernelFunction
            sage: R.<x,y> = PolynomialRing(QQ, order='lex')
            sage: I = R.ideal(x + 1, x*y + 1)
            sage: f = SingularKernelFunction("std")
            sage: f(I)
            [y - 1, x + 1]
        """
        super(SingularKernelFunction,self).__init__(name)
        self.call_handler = self.get_call_handler()

    cdef BaseCallHandler get_call_handler(self):
        cdef int cmd_n = -1
        arity = IsCmd(self._name, cmd_n) # call by reverence for CMD_n
        if cmd_n == -1:
            raise NameError("Function '%s' is not defined."%self._name)

        return KernelCallHandler(cmd_n, arity)

    cdef bint function_exists(self):
        cdef int cmd_n = -1
        arity = IsCmd(self._name, cmd_n) # call by reverence for CMD_n
        return cmd_n != -1


def singular_function(name):
    """
    Construct a new libSingular function object for the given
    ``name``.

    This function works both for interpreter and built-in functions.

    INPUT:

    - ``name`` - the name of the function

    EXAMPLE::

        sage: from sage.libs.singular.function import singular_function
        sage: P.<x,y,z> = PolynomialRing(QQ)
        sage: f = 3*x*y + 2*z + 1
        sage: g = 2*x + 1/2
        sage: I = Ideal([f,g])

        sage: number_foobar = singular_function('number_foobar');
        Traceback (most recent call last):
        ...
        NameError: Function 'number_foobar' is not defined.

        sage: from sage.libs.singular.function import lib as singular_lib
        sage: singular_lib('general.lib')
        sage: number_e = singular_function('number_e')
        sage: number_e(10r,ring=P)
        67957045707/25000000000
        sage: RR(number_e(10r,ring=P))
        2.71828182828000

        sage: std = singular_function("std")
        sage: std(I)
        [3*y - 8*z - 4, 4*x + 1]
        sage: singular_list = singular_function("list")
        sage: singular_list(2, 3, 6, ring=P)
        [2, 3, 6]
        sage: size = singular_function("size")
        sage: size([2, 3, 3], ring=P)
        3
        sage: size("sage", ring=P)
        4
        sage: size(["hello", "sage"], ring=P)
        2
        sage: factorize = singular_function("factorize")
        sage: factorize(f)
        [[1, 3*x*y + 2*z + 1], (1, 1)]
        sage: singular_lib('primdec.lib')
        sage: primdecGTZ = singular_function("primdecGTZ")
        sage: primdecGTZ(I)
        [[[3*y - 8*z - 4, 4*x + 1], [3*y - 8*z - 4, 4*x + 1]]]
        sage: singular_list((1,2,3),3,[1,2,3], ring=P)
        [(1, 2, 3), 3, [1, 2, 3]]
        sage: ringlist=singular_function("ringlist")
        sage: l = ringlist(P)
        sage: l[3].__class__
        <class 'sage.rings.polynomial.multi_polynomial_sequence.PolynomialSequence_generic'>
        sage: l
        [0, ['x', 'y', 'z'], [['dp', (1, 1, 1)], ['C', (0,)]], [0]]
        sage: ring=singular_function("ring")
        sage: ring(l, ring=P)
        <RingWrap>
        sage: matrix = Matrix(P,2,2)
        sage: matrix.randomize(terms=1)
        sage: det = singular_function("det")
        sage: det(matrix)
        -3/5*x*y*z
        sage: coeffs = singular_function("coeffs")
        sage: coeffs(x*y+y+1,y)
        [    1]
        [x + 1]
        sage: F.<x,y,z> = GF(3)[]
        sage: intmat = Matrix(ZZ, 2,2, [100,2,3,4])
        sage: det(intmat, ring=F)
        394
        sage: random = singular_function("random")
        sage: random(10,2,3, ring =F)
        [-3 -3 -8]
        [10  3 10]
        sage: P.<x,y,z> = PolynomialRing(QQ)
        sage: M=P**3
        sage: leadcoef = singular_function("leadcoef")
        sage: v=M((100*x,5*y,10*z*x*y))
        sage: leadcoef(v)
        10
        sage: v = M([x+y,x*y+y**3,z])
        sage: lead = singular_function("lead")
        sage: lead(v)
        (0, y^3)
        sage: jet = singular_function("jet")
        sage: jet(v, 2)
        (x + y, x*y, z)
        sage: syz = singular_function("syz")
        sage: I = P.ideal([x+y,x*y-y, y*2,x**2+1])
        sage: M = syz(I)
        sage: M
        [(-2*y, 2, y + 1, 0), (0, -2, x - 1, 0), (x*y - y, -y + 1, 1, -y), (x^2 + 1, -x - 1, -1, -x)]
        sage: singular_lib("mprimdec.lib")
        sage: syz(M)
        [(-x - 1, y - 1, 2*x, -2*y)]
        sage: GTZmod = singular_function("GTZmod")
        sage: GTZmod(M)
        [[[(-2*y, 2, y + 1, 0), (0, x + 1, 1, -y), (0, -2, x - 1, 0), (x*y - y, -y + 1, 1, -y), (x^2 + 1, 0, 0, -x - y)], [0]]]
        sage: mres = singular_function("mres")
        sage: resolution = mres(M, 0)
        sage: resolution
        <Resolution>
        sage: singular_list(resolution)
        [[(-2*y, 2, y + 1, 0), (0, -2, x - 1, 0), (x*y - y, -y + 1, 1, -y), (x^2 + 1, -x - 1, -1, -x)], [(-x - 1, y - 1, 2*x, -2*y)], [(0)]]


    """

    cdef SingularFunction fnc
    try:
        return SingularKernelFunction(name)
    except NameError:
        return SingularLibraryFunction(name)

def lib(name):
    """
    Load the Singular library ``name``.

    INPUT:

    - ``name`` - a Singular library name

    EXAMPLE::

        sage: from sage.libs.singular.function import singular_function
        sage: from sage.libs.singular.function import lib as singular_lib
        sage: singular_lib('general.lib')
        sage: primes = singular_function('primes')
        sage: primes(2,10, ring=GF(127)['x,y,z'])
        (2, 3, 5, 7)
    """
    global verbose
    cdef int vv = verbose

    if get_verbose() <= 0:
        verbose &= ~Sy_bit(V_LOAD_LIB)

    if get_verbose() <= 0:
        verbose &= ~Sy_bit(V_REDEFINE)

    cdef bint failure = iiLibCmd(omStrDup(name), 1, 1, 1)
    verbose = vv

    if failure:
        raise NameError("Library '%s' not found."%(name,))



def list_of_functions(packages=False):
    """
    Return a list of all function names currently available.

    INPUT:

    - ``packages`` - include local functions in packages.

    EXAMPLE::

        sage: 'groebner' in sage.libs.singular.function.list_of_functions()
        True
    """
    cdef list l = []
    cdef idhdl *h=IDROOT
    cdef idhdl *ph = NULL
    while h!=NULL:
        if PROC_CMD == IDTYP(h):
            l.append(h.id)
        if  PACKAGE_CMD == IDTYP(h):
            if packages:
                ph = IDPACKAGE(h).idroot
                while ph != NULL:
                    if PROC_CMD == IDTYP(ph):
                        l.append(ph.id)
                    ph = IDNEXT(ph)
        h = IDNEXT(h)
    return l
