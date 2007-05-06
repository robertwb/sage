"""
Multivariate polynomials over QQ and GF(p) implemented using SINGULAR as backend.

AUTHORS:
    Martin Albrecht <malb@informatik.uni-bremen.de>



TODO:
   * implement every method from multi_polynomial_ring and multi_polynomial_element
   * check SINGULAR code base for 'interesting' methods to add
   * add required methods for F4, Buchberger etc.
   * implement GF(p^n)
   * implement block orderings
   * implement Real, Complex
   * test under CYGWIN (link error)

"""
# We do this as we get a link error for init_csage(). However, on
# obscure plattforms (Windows) we might need to link to csage anyway.

cdef extern from "stdsage.h":
    ctypedef void PyObject
    object PY_NEW(object t)
    int PY_TYPE_CHECK(object o, object t)
    PyObject** FAST_SEQ_UNSAFE(object o)
    void init_csage()

    void  sage_free(void *p)
    void* sage_realloc(void *p, size_t n)
    void* sage_malloc(size_t)

import os
import sage.rings.memory

from sage.libs.singular.singular import Conversion
from sage.libs.singular.singular cimport Conversion

cdef Conversion co
co = Conversion()

from sage.rings.polynomial.multi_polynomial_ring import singular_name_mapping, TermOrder
from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal
from sage.rings.polynomial.polydict import ETuple

from sage.rings.rational_field import RationalField
from sage.rings.finite_field import FiniteField_prime_modn

from  sage.rings.rational cimport Rational

from sage.interfaces.singular import singular as singular_default, is_SingularElement, SingularElement
from sage.interfaces.macaulay2 import macaulay2 as macaulay2_default, is_Macaulay2Element
from sage.structure.factorization import Factorization

from sage.rings.complex_field import is_ComplexField
from sage.rings.real_mpfr import is_RealField


from sage.rings.integer_ring import IntegerRing
from sage.structure.element cimport EuclideanDomainElement, \
     RingElement, \
     ModuleElement, \
     Element, \
     CommutativeRingElement

from sage.rings.integer cimport Integer

from sage.structure.parent cimport Parent
from sage.structure.parent_base cimport ParentWithBase
from sage.structure.parent_gens cimport ParentWithGens

from sage.misc.sage_eval import sage_eval

# shared library loading
cdef extern from "dlfcn.h":
    void *dlopen(char *, long)
    char *dlerror()

cdef extern from "string.h":
    char *strdup(char *s)


cdef init_singular():
    """
    This initializes the Singular library. Right now, this is a hack.

    SINGULAR has a concept of compiled extension modules similar to
    SAGE. For this, the compiled modules need to see the symbols from
    the main programm. However, SINGULAR is a shared library in this
    context these symbols are not known globally. The work around so
    far is to load the library again and to specifiy RTLD_GLOBAL.
    """

    cdef void *handle


    lib = os.environ['SAGE_LOCAL']+"/lib/libsingular.so"
    if os.path.exists(lib):
       handle = dlopen(lib, 256+1)
    else:
        lib = os.environ['SAGE_LOCAL']+"/lib/libsingular.dylib"
        if os.path.exists(lib):
            handle = dlopen(lib, 256+1)
        else:
            raise ImportError, "cannot load libSINGULAR library"

    if handle == NULL:
        print dlerror()

    # Load Singular
    siInit(lib)

    # Steal Memory Manager back or weird things may happen
    sage.rings.memory.pmem_malloc()

# call it
init_singular()

cdef class MPolynomialRing_libsingular(MPolynomialRing_generic):
    """
    A multivariate polynomial ring over QQ or GF(p) implemented using SINGULAR.

    """
    def __init__(self, base_ring, n, names, order='degrevlex'):
        """

        Construct a multivariate polynomial ring subject to the following conditions:

        INPUT:
            base_ring -- base ring (must be either GF(p) (p prime) or QQ)
            n -- number of variables (must be at least 1)
            names -- names of ring variables, may be string of list/tuple
            order -- term order (default: degrevlex)

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P
            Polynomial Ring in x, y, z over Rational Field

            sage: f = 27/113 * x^2 + y*z + 1/2; f
            27/113*x^2 + y*z + 1/2

            sage: P.term_order()
            Degree reverse lexicographic term order

            sage: P = MPolynomialRing_libsingular(GF(127),3,names='abc', order='lex')
            sage: P
            Polynomial Ring in a, b, c over Finite Field of size 127

            sage: a,b,c = P.gens()
            sage: f = 57 * a^2*b + 43 * c + 1; f
            57*a^2*b + 43*c + 1

            sage: P.term_order()
            Lexicographic term order

        """
        cdef char **_names
        cdef char *_name
        cdef int i
        cdef int characteristic

        n = int(n)
        if n<1:
            raise ArithmeticError, "number of variables must be at least 1"

        self.__ngens = n

        MPolynomialRing_generic.__init__(self, base_ring, n, names, TermOrder(order))

        self._has_singular = True

        _names = <char**>sage_malloc(sizeof(char*)*len(self._names))

        for i from 0 <= i < n:
            _name = self._names[i]
            _names[i] = strdup(_name)

        if PY_TYPE_CHECK(base_ring, FiniteField_prime_modn):
            characteristic = base_ring.characteristic()

        elif PY_TYPE_CHECK(base_ring, RationalField):
            characteristic = 0

        else:
            raise NotImplementedError, "Only GF(p) and QQ are supported right now, sorry"

        try:
            order = singular_name_mapping[order]
        except KeyError:
            pass

        self._ring = rDefault(characteristic, n, _names)
        if(self._ring != currRing): rChangeCurrRing(self._ring)

        rUnComplete(self._ring)

        omFree(self._ring.wvhdl)
        omFree(self._ring.order)
        omFree(self._ring.block0)
        omFree(self._ring.block1)

        self._ring.wvhdl  = <int **>omAlloc0(3 * sizeof(int*))
        self._ring.order  = <int *>omAlloc0(3* sizeof(int *))
        self._ring.block0 = <int *>omAlloc0(3 * sizeof(int *))
        self._ring.block1 = <int *>omAlloc0(3 * sizeof(int *))

        if order == "dp":
            self._ring.order[0] = ringorder_dp
        elif order == "Dp":
            self._ring.order[0] = ringorder_Dp
        elif order == "lp":
            self._ring.order[0] = ringorder_lp
        elif order == "rp":
            self._ring.order[0] = ringorder_rp
        else:
            self._ring.order[0] = ringorder_lp

        self._ring.order[1] = ringorder_C

        self._ring.block0[0] = 1
        self._ring.block1[0] = n

        rComplete(self._ring, 1)
        self._ring.ShortOut = 0

        self._zero = <MPolynomial_libsingular>new_MP(self,NULL)

        sage_free(_names)

    def __dealloc__(self):
        """
        """
        rDelete(self._ring)

    cdef _coerce_c_impl(self, element):
        """

        Coerces elements to self.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)

            We can coerce elements of self to self

            sage: P._coerce_(x*y + 1/2)
            x*y + 1/2

            We can coerce elements for a ring with the same algebraic properties

            sage: R.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P == R
            True

            sage: P is R
            False

            sage: P._coerce_(x*y + 1)
            x*y + 1

            We can coerce base ring elements

            sage: P._coerce_(3/2)
            3/2

            sage: P._coerce_(ZZ(1))
            1

            sage: P._coerce_(int(1))
            1

        """
        cdef poly *_p
        cdef ring *_ring
        cdef number *_n
        cdef poly *rm
        cdef int ok
        cdef int i
        cdef ideal *from_id, *to_id, *res_id

        _ring = self._ring

        if(_ring != currRing): rChangeCurrRing(_ring)

        if PY_TYPE_CHECK(element, MPolynomial_libsingular):
            if element.parent() is <object>self:
                return element
            elif element.parent() == self:
                # is this safe?
                _p = p_Copy((<MPolynomial_libsingular>element)._poly, _ring)
            else:
                raise TypeError, "parents do not match"

        elif PY_TYPE_CHECK(element, CommutativeRingElement):
            # Accepting ZZ
            if element.parent() is IntegerRing():
                _p = p_ISet(int(element), _ring)

            elif  <Parent>element.parent() is self._base:
                # Accepting GF(p)
                if PY_TYPE_CHECK(self._base, FiniteField_prime_modn):
                    _p = p_ISet(int(element), _ring)

                # Accepting QQ
                elif PY_TYPE_CHECK(self._base, RationalField):
                    _n = co.sa2si_QQ(element,_ring)
                    _p = p_NSet(_n, _ring)
                else:
                    raise NotImplementedError
            else:
                raise TypeError, "base rings must be identical"

        # Accepting int
        elif PY_TYPE_CHECK(element, int):
            _p = p_ISet(int(element), _ring)
        else:
            raise TypeError, "Cannot coerce element"

        return new_MP(self,_p)

    def __call__(self, element):
        """
        Construct a new element in self.

        INPUT:
            element -- several types are supported, see below

        EXAMPLE:
            Call supports all conversions _coerce_ supports, plus:

            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P('x+y + 1/4')
            x + y + 1/4

            sage: P._singular_()
            //   characteristic : 0
            //   number of vars : 3
            //        block   1 : ordering dp
            //                  : names    x y z
            //        block   2 : ordering C

            sage: P(singular('x + 3/4'))
            x + 3/4
        """
        cdef poly *_m, *_p, *_tmp
        cdef ring *_r

        if PY_TYPE_CHECK(element, SingularElement):
            element = str(element)

        if PY_TYPE_CHECK(element,str):
            # let python do the the parsing
            return sage_eval(element,self.gens_dict())

               # this almost does what I want, besides variables with 0-9 in their names
##             _r = self._ring
##             if(_r != currRing): rChangeCurrRing(_r)
##             # improve this
##             element = element.replace('^','').replace('**','').replace(' ','').strip()
##             monomials = element.split('+')
##             _p = p_ISet(0, _r)
##             # wrong for e.g. x0,..,x7
##             for m in monomials:
##                 _m = p_ISet(1,_r)
##                 for var in m.split('*'):
##                     p_Read(var, _tmp, _r)
##                     _m = p_Mult_q(_m,_tmp, _r)

##                 _p = p_Add_q(_p,_m,_r)

##             return new_MP(self,_p)

        return self._coerce_c_impl(element)

    def _repr_(self):
        """
        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y> = MPolynomialRing_libsingular(QQ, 2)
            sage: P
            Polynomial Ring in x, y over Rational Field

        """
        varstr = ", ".join([ rRingVar(i,self._ring)  for i in range(self.__ngens) ])
        return "Polynomial Ring in %s over %s"%(varstr,self._base)

    def ngens(self):
        """
        Returns the number of variables in self.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y> = MPolynomialRing_libsingular(QQ, 2)
            sage: P.ngens()
            2

            sage: P = MPolynomialRing_libsingular(GF(127),1000,'x')
            sage: P.ngens()
            1000

        """
        return int(self.__ngens)

    def gens(self):
        """
        Return the tuple of variables in self.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P.gens()
            (x, y, z)

            sage: P = MPolynomialRing_libsingular(QQ,10,'x')
            sage: P.gens()
            (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9)

            sage: P.<SAGE,SINGULAR> = MPolynomialRing_libsingular(QQ,2) # weird names
            sage: P.gens()
            (SAGE, SINGULAR)

        """
        return tuple([self.gen(i) for i in range(self.__ngens)  ])

    def gen(self, int n=0):
        """
        Returns the n-th generator of self.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P.gen(),P.gen(1)
            (x, y)

            sage: P = MPolynomialRing_libsingular(GF(127),1000,'x')
            sage: P.gen(500)
            x500

            sage: P.<SAGE,SINGULAR> = MPolynomialRing_libsingular(QQ,2) # weird names
            sage: P.gen(1)
            SINGULAR

        """
        cdef poly *_p
        cdef ring *_ring

        if n < 0 or n >= self.__ngens:
            raise ValueError, "Generator not defined."

        _ring = self._ring
        _p = p_ISet(1,_ring)

        # oddly enough, Singular starts counting a 1!!!
        p_SetExp(_p, n+1, 1, _ring)
        p_Setm(_p, _ring);

        return new_MP(self,_p)

    def ideal(self, gens, coerce=True):
        """
        Create an ideal in this polynomial ring.

        INPUT:
            gens -- generators of the ideal
            coerce -- shall the generators be coerced first (default:True)

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: sage.rings.ideal.Katsura(P)
            Ideal (x + 2*y + 2*z - 1, x^2 + 2*y^2 + 2*z^2 - x, 2*x*y + 2*y*z - y) of Polynomial Ring in x, y, z over Rational Field

            sage: P.ideal([x + 2*y + 2*z-1, 2*x*y + 2*y*z-y, x^2 + 2*y^2 + 2*z^2-x])
            Ideal (x + 2*y + 2*z - 1, 2*x*y + 2*y*z - y, x^2 + 2*y^2 + 2*z^2 - x) of Polynomial Ring in x, y, z over Rational Field

        """
        if is_SingularElement(gens):
            gens = list(gens)
            coerce = True
        if is_Macaulay2Element(gens):
            gens = list(gens)
            coerce = True
        elif not isinstance(gens, (list, tuple)):
            gens = [gens]
        if coerce:
            gens = [self(x) for x in gens]  # this will even coerce from singular ideals correctly!
        return MPolynomialIdeal(self, gens, coerce=False)

    def _macaulay2_(self, macaulay2=macaulay2_default):
        """
        Create a M2 representation of self if Macaulay2 is installed.

        INPUT:
            macaulay2 -- M2 interpreter (default: macaulay2_default)
        """
        try:
            R = self.__macaulay2
            if R is None or not (R.parent() is macaulay2):
                raise ValueError
            R._check_valid()
            return R
        except (AttributeError, ValueError):
            if self.base_ring().is_prime_field():
                if self.characteristic() == 0:
                    base_str = "QQ"
                else:
                    base_str = "ZZ/" + str(self.characteristic())
            elif is_IntegerRing(self.base_ring()):
                base_str = "ZZ"
            else:
                raise TypeError, "no conversion of to a Macaulay2 ring defined"
            self.__macaulay2 = macaulay2.ring(base_str, str(self.gens()), \
                                              self.term_order().macaulay2_str())
        return self.__macaulay2

    def _singular_(self, singular=singular_default):
        """
        Create a SINGULAR (as in the CAS) representation of self. The
        result is cached.

        INPUT:
            singular -- SINGULAR interpreter (default: singular_default)

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P._singular_()
            //   characteristic : 0
            //   number of vars : 3
            //        block   1 : ordering dp
            //                  : names    x y z
            //        block   2 : ordering C

            sage: P._singular_() is P._singular_()
            True

            sage: P._singular_().name() == P._singular_().name()
            True

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x> = MPolynomialRing_libsingular(QQ,1)
            sage: P._singular_()
            //   characteristic : 0
            //   number of vars : 1
            //        block   1 : ordering lp
            //                  : names    x
            //        block   2 : ordering C

        """
        try:
            R = self.__singular
            if R is None or not (R.parent() is singular):
                raise ValueError
            R._check_valid()
            if self.base_ring().is_prime_field():
                return R
            if self.base_ring().is_finite():
                R.set_ring() #sorry for that, but needed for minpoly
                if  singular.eval('minpoly') != self.__minpoly:
                    singular.eval("minpoly=%s"%(self.__minpoly))
            return R
        except (AttributeError, ValueError):
            return self._singular_init_(singular)

    def _singular_init_(self, singular=singular_default):
        """
        Create a SINGULAR (as in the CAS) representation of self. The
        result is NOT cached.

        INPUT:
            singular -- SINGULAR interpreter (default: singular_default)

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P._singular_init_()
            //   characteristic : 0
            //   number of vars : 3
            //        block   1 : ordering dp
            //                  : names    x y z
            //        block   2 : ordering C
            sage: P._singular_init_() is P._singular_init_()
            False

            sage: P._singular_init_().name() == P._singular_init_().name()
            False

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x> = MPolynomialRing_libsingular(QQ,1)
            sage: P._singular_init_()
            //   characteristic : 0
            //   number of vars : 1
            //        block   1 : ordering lp
            //                  : names    x
            //        block   2 : ordering C

        """
        if self.ngens()==1:
            _vars = str(self.gen())
            if "*" in _vars: # 1.000...000*x
                _vars = _vars.split("*")[1]
            order = 'lp'
        else:
            _vars = str(self.gens())
            order = self.term_order().singular_str()

        if is_RealField(self.base_ring()):
            # singular converts to bits from base_10 in mpr_complex.cc by:
            #  size_t bits = 1 + (size_t) ((float)digits * 3.5);
            precision = self.base_ring().precision()
            digits = sage.rings.arith.ceil((2*precision - 2)/7.0)
            self.__singular = singular.ring("(real,%d,0)"%digits, _vars, order=order)

        elif is_ComplexField(self.base_ring()):
            # singular converts to bits from base_10 in mpr_complex.cc by:
            #  size_t bits = 1 + (size_t) ((float)digits * 3.5);
            precision = self.base_ring().precision()
            digits = sage.rings.arith.ceil((2*precision - 2)/7.0)
            self.__singular = singular.ring("(complex,%d,0,I)"%digits, _vars,  order=order)

        elif self.base_ring().is_prime_field():
            self.__singular = singular.ring(self.characteristic(), _vars, order=order)

        elif self.base_ring().is_finite(): #must be extension field
            gen = str(self.base_ring().gen())
            r = singular.ring( "(%s,%s)"%(self.characteristic(),gen), _vars, order=order)
            self.__minpoly = "("+(str(self.base_ring().modulus()).replace("x",gen)).replace(" ","")+")"
            singular.eval("minpoly=%s"%(self.__minpoly) )

            self.__singular = r
        else:
            raise TypeError, "no conversion to a Singular ring defined"

        return self.__singular

    def __hash__(self):
        """
        Return a hash for self, that is, a hash of the string representation of self

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: hash(P)
            -6257278808099690586 # 64-bit
            -1767675994 # 32-bit
        """
        return hash(self.__repr__())

    def __richcmp__(left, right, int op):
        return (<Parent>left)._richcmp(right, op)

    cdef int _cmp_c_impl(left, Parent right) except -2:
        """
        Multivariate polynomial rings are said to be equal if:
         * their base rings match
         * their generator names match
         * their term orderings match

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: R.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P == R
            True

            sage: R.<x,y,z> = MPolynomialRing_libsingular(GF(127),3)
            sage: P == R
            False

            sage: R.<x,y> = MPolynomialRing_libsingular(QQ,2)
            sage: P == R
            False

            sage: R.<x,y,z> = MPolynomialRing_libsingular(QQ,3,order='revlex')
            sage: P == R
            False


        """
        if PY_TYPE_CHECK(right, MPolynomialRing_libsingular):
            return cmp( (left.base_ring(), map(str, left.gens()), left.term_order()),
                        (right.base_ring(), map(str, right.gens()), right.term_order())
                        )
        else:
            return cmp(type(left),type(right))

    def __reduce__(self):
        """
        Serializes self.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3, order='degrevlex')
            sage: P == loads(dumps(P))
            True

            sage: P = MPolynomialRing_libsingular(GF(127),3,names='abc')
            sage: P == loads(dumps(P))
            True

        """
        return sage.rings.polynomial.multi_polynomial_libsingular.unpickle_MPolynomialRing_libsingular, ( self.base_ring(),
                                                                                               map(str, self.gens()),
                                                                                               self.term_order() )

    ### The following methods are handy for implementing e.g. F4. They
    ### do only superficial type/sanity checks and should be called
    ### carefully.

    def monomial_m_div_n(self, MPolynomial_libsingular f, MPolynomial_libsingular g, coeff=False):
        """
        Return f/g, where both f and g are treated as
        monomials. Coefficients are ignored by default.

        INPUT:
            f -- monomial
            g -- monomial
            coeff -- divide coefficents as well (default: False)

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.monomial_m_div_n(3/2*x*y,x)
            y

            sage: P.monomial_m_div_n(3/2*x*y,x,coeff=True)
            3/2*y

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.monomial_m_div_n(x*y,x)
            y

            sage: P.monomial_m_div_n(x*y,R.gen())
            y

            sage: P.monomial_m_div_n(P(0),P(1))
            0

            sage: P.monomial_m_div_n(P(1),P(0))
            Traceback (most recent call last):
            ...
            ZeroDivisionError

            sage: P.monomial_m_div_n(P(3/2),P(2/3), coeff=True)
            9/4

            sage: P.monomial_m_div_n(x,y) # Note the wrong result
            x*y^1048575*z^1048575 # 64-bit
            x*y^65535*z^65535 # 32-bit

            sage: P.monomial_m_div_n(x,P(1))
            x

        NOTE: Assumes that the head term of f is a multiple of the
        head term of g and return the multiplicant m. If this rule is
        violated, funny things may happen.



        """
        cdef poly *res
        cdef ring *r = self._ring

        if not <ParentWithBase>self is f._parent:
            f = self._coerce_c(f)
        if not <ParentWithBase>self is g._parent:
            g = self._coerce_c(g)

        if(r != currRing): rChangeCurrRing(r)

        if not f._poly:
            return self._zero
        if not g._poly:
            raise ZeroDivisionError

        res = pDivide(f._poly,g._poly)
        if coeff:
            p_SetCoeff(res, n_Div( p_GetCoeff(f._poly, r) , p_GetCoeff(g._poly, r), r), r)
        else:
            p_SetCoeff(res, n_Init(1, r), r)
        return new_MP(self, res)

    def monomial_lcm(self, MPolynomial_libsingular f, MPolynomial_libsingular g):
        """
        LCM for monomials. Coefficients are ignored.

        INPUT:
            f -- monomial
            g -- monomial

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.monomial_lcm(3/2*x*y,x)
            x*y

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.monomial_lcm(x*y,R.gen())
            x*y

            sage: P.monomial_lcm(P(3/2),P(2/3))
            1

            sage: P.monomial_lcm(x,P(1))
            x

        """
        cdef poly *m = p_ISet(1,self._ring)

        if not <ParentWithBase>self is f._parent:
            f = self._coerce_c(f)
        if not <ParentWithBase>self is g._parent:
            g = self._coerce_c(g)

        if f._poly == NULL:
            if g._poly == NULL:
                return self._zero
            else:
                raise ArithmeticError, "cannot compute lcm of zero and nonzero element"
        if g._poly == NULL:
            raise ArithmeticError, "cannot compute lcm of zero and nonzero element"

        if(self._ring != currRing): rChangeCurrRing(self._ring)

        pLcm(f._poly, g._poly, m)
        return new_MP(self,m)

    def monomial_reduce(self, MPolynomial_libsingular f, G):
        """
        Try to find a g in G where g.lm() divides f. If found (g,flt)
        is returned, (0,0) otherwise, where flt is f/g.lm().

        It is assumed that G is iterable and contains ONLY elements in
        self.

        INPUT:
            f -- monomial
            G -- list/set of mpolynomials

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: f = x*y^2
            sage: G = [ 3/2*x^3 + y^2 + 1/2, 1/4*x*y + 2/7, 1/2  ]
            sage: P.monomial_reduce(f,G)
            (1/4*x*y + 2/7, y)

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: f = x*y^2
            sage: G = [ 3/2*x^3 + y^2 + 1/2, 1/4*x*y + 2/7, 1/2  ]

            sage: P.monomial_reduce(P(0),G)
            (0, 0)

            sage: P.monomial_reduce(f,[P(0)])
            (0, 0)

        """
        cdef poly *m = f._poly
        cdef ring *r = self._ring
        cdef poly *flt

        if not m:
            return f,f

        for g in G:
            if PY_TYPE_CHECK(g, MPolynomial_libsingular) \
                   and (<MPolynomial_libsingular>g) \
                   and p_LmDivisibleBy((<MPolynomial_libsingular>g)._poly, m, r):
                flt = pDivide(f._poly, (<MPolynomial_libsingular>g)._poly)
                #p_SetCoeff(flt, n_Div( p_GetCoeff(f._poly, r) , p_GetCoeff((<MPolynomial_libsingular>g)._poly, r), r), r)
                p_SetCoeff(flt, n_Init(1, r), r)
                return g, new_MP(self,flt)
        return self._zero,self._zero

    def monomial_pairwise_prime(self, MPolynomial_libsingular g, MPolynomial_libsingular h):
        """
        Return True if h and g are pairwise prime. Both are treated as monomials.

        INPUT:
            h -- monomial
            g -- monomial

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P.monomial_pairwise_prime(x^2*z^3, y^4)
            True

            sage: P.monomial_pairwise_prime(1/2*x^3*y^2, 3/4*y^3)
            False

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: Q.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P.monomial_pairwise_prime(x^2*z^3, Q('y^4'))
            True

            sage: P.monomial_pairwise_prime(1/2*x^3*y^2, Q(0))
            True

            sage: P.monomial_pairwise_prime(P(1/2),x)
            False


        """
        cdef int i
        cdef ring *r
        cdef poly *p, *q

        if h._parent is not g._parent:
            g = (<MPolynomialRing_libsingular>h._parent)._coerce_c(g)

        r = (<MPolynomialRing_libsingular>h._parent)._ring
        p = g._poly
        q = h._poly

        if p == NULL:
            if q == NULL:
                return False #GCD(0,0) = 0
            else:
                return True #GCD(x,0) = 1

        elif q == NULL:
            return True # GCD(0,x) = 1

        elif p_IsConstant(p,r) or p_IsConstant(q,r): # assuming a base field
            return False

        for i from 1 <= i <= r.N:
            if p_GetExp(p,i,r) and p_GetExp(q,i,r):
                return False
        return True

    def monomial_is_divisible_by(self, MPolynomial_libsingular a, MPolynomial_libsingular b):
        """
        Return 0 if b does not divide a and the factor
        otherwise. Coefficients are ignored.

        INPUT:
            a -- monomial
            b -- monomial

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.monomial_is_divisible_by(x^3*y^2*z^4, x*y*z)
            x^2*y*z^3
            sage: P.monomial_is_divisible_by(x*y*z, x^3*y^2*z^4)
            0

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.monomial_is_divisible_by(P(0),P(1))
            0
            sage: P.monomial_is_divisible_by(x,P(1))
            x

        """
        cdef poly *_a
        cdef poly *_b
        cdef ring *_r
        cdef poly *ret
        if a._parent is not b._parent:
            b = (<MPolynomialRing_libsingular>a._parent)._coerce_c(b)

        _a = a._poly
        _b = b._poly
        _r = (<MPolynomialRing_libsingular>a._parent)._ring
        if(_r != currRing): rChangeCurrRing(_r)

        if _b == NULL:
            raise ZeroDivisionError
        if _a == NULL:
            return self._zero

        if not p_DivisibleBy(_b, _a, _r):
           return self._zero
        else:
            ret = pDivide(_a,_b)
            p_SetCoeff(ret, n_Init(1, _r), _r)
            return new_MP(self,ret)

def unpickle_MPolynomialRing_libsingular(base_ring, names, term_order):
    """
    inverse function for MPolynomialRing_libsingular.__reduce__

    """
    return MPolynomialRing_libsingular(base_ring, len(names), names, term_order)

cdef MPolynomial_libsingular new_MP(MPolynomialRing_libsingular parent, poly *juice):
    """
    Construct a new MPolynomial_libsingular element
    """
    cdef MPolynomial_libsingular p
    p = PY_NEW(MPolynomial_libsingular)
    p._parent = <ParentWithBase>parent
    p._poly = juice
    return p

cdef class MPolynomial_libsingular(sage.rings.polynomial.multi_polynomial.MPolynomial):
    """
    A multivariate polynomial implemented using libSINGULAR.
    """
    def __init__(self, MPolynomialRing_libsingular parent):
        """
        Construct a zero element in parent.
        """
        self._parent = <ParentWithBase>parent

    def __dealloc__(self):
        if self._poly:
            p_Delete(&self._poly, (<MPolynomialRing_libsingular>self._parent)._ring)

    def __call__(self, *x):
        """
        Evaluate a polynomial at the given point x

        INPUT:
            x -- a list of elements in self.parent()

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: f = 3/2*x^2*y + 1/7 * y^2 + 13/27
            sage: f(0,0,0)
            13/27

            sage: f(1,1,1)
            803/378
            sage: 3/2 + 1/7 + 13/27
            803/378

            sage: f(45/2,19/3,1)
            7281167/1512

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P(0)(1,2,3)
            0
            sage: P(3/2)(1,2,3)
            3/2
        """
        cdef int l = len(x)
        cdef MPolynomialRing_libsingular parent = (<MPolynomialRing_libsingular>self._parent)
        cdef ring *_ring = parent._ring

        cdef poly *_p

        if l != parent._ring.N:
            raise TypeError, "number of arguments does not match number of variables in parent"

        cdef ideal *to_id = idInit(l,1)

        try:
            for i from 0 <= i < l:
                e = x[i] # TODO: optimize this line
                to_id.m[i]= p_Copy( (<MPolynomial_libsingular>(<MPolynomialRing_libsingular>parent._coerce_c(x[i])))._poly, _ring)

        except TypeError:
            id_Delete(&to_id, _ring)
            raise TypeError, "cannot coerce in arguments"

        cdef ideal *from_id=idInit(1,1)
        from_id.m[0] = p_Copy(self._poly, _ring)

        cdef ideal *res_id = fast_map(from_id, _ring, to_id, _ring)
        cdef poly *res = p_Copy(res_id.m[0], _ring)

        id_Delete(&to_id, _ring)
        id_Delete(&from_id, _ring)
        id_Delete(&res_id, _ring)
        return new_MP(parent, res)

    def __richcmp__(left, right, int op):
        return (<Element>left)._richcmp(right, op)

    cdef int _cmp_c_impl(left, Element right) except -2:
        """
        Compare left and right and return -1, 0, and 1 for <,==, and > respectively.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3, order='degrevlex')
            sage: x == x
            True

            sage: x > y
            True
            sage: y^2 > x
            True

            sage: (2/3*x^2 + 1/2*y + 3) > (2/3*x^2 + 1/4*y + 10)
            True

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3, order='degrevlex')
            sage: x > P(0)
            True

            sage: P(0) == P(0)
            True

            sage: P(0) < P(1)
            True

            sage: x > P(1)
            True

            sage: 1/2*x < 3/4*x
            True

            sage: (x+1) > x
            True

            sage: f = 3/4*x^2*y + 1/2*x + 2/7
            sage: f > f
            False
            sage: f < f
            False
            sage: f == f
            True

            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(GF(127),3, order='degrevlex')
            sage: (66*x^2 + 23) > (66*x^2 + 2)
            True


        """
        cdef ring *r
        cdef poly *p, *q
        cdef number *h
        cdef int ret = 0

        r = (<MPolynomialRing_libsingular>left._parent)._ring
        if(r != currRing): rChangeCurrRing(r)
        p = (<MPolynomial_libsingular>left)._poly
        q = (<MPolynomial_libsingular>right)._poly

        # handle special cases first (slight slowdown, as special
        # cases are - well - special
        if p==NULL:
            if q==NULL:
                # compare 0, 0
                return 0
            elif p_IsConstant(q,r):
                # compare 0, const
                return 1-2*n_GreaterZero(p_GetCoeff(q,r), r) # -1: <, 1: > #
        elif q==NULL:
            if p_IsConstant(p,r):
                # compare const, 0
                return -1+2*n_GreaterZero(p_GetCoeff(p,r), r) # -1: <, 1: >
        #else

        while ret==0 and p!=NULL and q!=NULL:
            ret = p_Cmp( p, q, r)

            if ret==0:
                h = n_Sub(p_GetCoeff(p, r),p_GetCoeff(q, r), r)
                # compare coeffs
                ret = -1+n_IsZero(h, r)+2*n_GreaterZero(h, r) # -1: <, 0:==, 1: >
                n_Delete(&h, r)
            p = pNext(p)
            q = pNext(q)

        if ret==0:
            if p==NULL and q != NULL:
                ret = -1
            elif p!=NULL and q==NULL:
                ret = 1

        return ret

    cdef ModuleElement _add_c_impl( left, ModuleElement right):
        """
        Add left and right.

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: 3/2*x + 1/2*y + 1
            3/2*x + 1/2*y + 1

        """
        cdef MPolynomial_libsingular res

        cdef poly *_l, *_r, *_p
        cdef ring *_ring

        _ring = (<MPolynomialRing_libsingular>left._parent)._ring

        _l = p_Copy(left._poly, _ring)
        _r = p_Copy((<MPolynomial_libsingular>right)._poly, _ring)

        if(_ring != currRing): rChangeCurrRing(_ring)
        _p= p_Add_q(_l, _r, _ring)

        return new_MP((<MPolynomialRing_libsingular>left._parent),_p)

    cdef ModuleElement _sub_c_impl( left, ModuleElement right):
        """
        Subtract left and right.

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: 3/2*x - 1/2*y - 1
            3/2*x - 1/2*y - 1

        """
        cdef MPolynomial_libsingular res

        cdef poly *_l, *_r, *_p
        cdef ring *_ring

        _ring = (<MPolynomialRing_libsingular>left._parent)._ring

        _l = p_Copy(left._poly, _ring)
        _r = p_Copy((<MPolynomial_libsingular>right)._poly, _ring)

        if(_ring != currRing): rChangeCurrRing(_ring)
        _p= p_Add_q(_l, p_Neg(_r, _ring), _ring)

        return new_MP((<MPolynomialRing_libsingular>left._parent),_p)


    cdef ModuleElement _rmul_c_impl(self, RingElement left):
        """
        Multiply self with a base ring element.

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: 3/2*x
            3/2*x
        """

        cdef number *_n
        cdef ring *_ring
        cdef poly *_p

        _ring = (<MPolynomialRing_libsingular>self._parent)._ring

        if(_ring != currRing): rChangeCurrRing(_ring)

        if PY_TYPE_CHECK((<MPolynomialRing_libsingular>self._parent)._base, FiniteField_prime_modn):
            _n = n_Init(int(left),_ring)

        elif PY_TYPE_CHECK((<MPolynomialRing_libsingular>self._parent)._base, RationalField):
            _n = co.sa2si_QQ(left,_ring)

        _p = pp_Mult_nn(self._poly,_n,_ring)
        n_Delete(&_n, _ring)
        return new_MP((<MPolynomialRing_libsingular>self._parent),_p)

    cdef RingElement  _mul_c_impl(left, RingElement right):
        """
        Multiply left and right.

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: (3/2*x - 1/2*y - 1) * (3/2*x + 1/2*y + 1)
            9/4*x^2 - 1/4*y^2 - y - 1
        """
        cdef poly *_l, *_r, *_p
        cdef ring *_ring

        _ring = (<MPolynomialRing_libsingular>left._parent)._ring

        if(_ring != currRing): rChangeCurrRing(_ring)
        _p = pp_Mult_qq(left._poly, (<MPolynomial_libsingular>right)._poly, _ring)

        return new_MP(left._parent,_p)

    cdef RingElement  _div_c_impl(left, RingElement right):
        """
        Divide left by right

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y>=MPolynomialRing_libsingular(QQ,2)
            sage: f = (x + y)/3
            sage: f.parent()
            Polynomial Ring in x, y over Rational Field

        Note that / is still a constructor for elements of the
        fraction field in all cases as long as both arguments have the
        same parent.

            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y>=MPolynomialRing_libsingular(QQ,2)
            sage: f = x^3 + y
            sage: g = x
            sage: h = f/g; h
            (x^3 + y)/x
            sage: h.parent()
            Fraction Field of Polynomial Ring in x, y over Rational Field

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y>=MPolynomialRing_libsingular(QQ,2)
            sage: x/0
            Traceback (most recent call last):
            ...
            ZeroDivisionError

        """
        cdef poly *p
        cdef ring *r
        cdef number *n
        if (<MPolynomial_libsingular>right).is_constant_c():

            p = (<MPolynomial_libsingular>right)._poly
            if p == NULL:
                raise ZeroDivisionError
            r = (<MPolynomialRing_libsingular>(<MPolynomial_libsingular>left)._parent)._ring
            n = p_GetCoeff(p, r)
            n = nInvers(n)
            p = pp_Mult_nn(left._poly, n,  r)
            n_Delete(&n,r)
            return new_MP(left._parent, p)
        else:
            return (<MPolynomialRing_libsingular>left._parent).fraction_field()(left,right)

    def __pow__(MPolynomial_libsingular self,int exp,ignored):
        """
        """
        cdef ring *_ring
        _ring = (<MPolynomialRing_libsingular>self._parent)._ring

        cdef poly *_p


        if exp < 0:
            raise ArithmeticError, "Cannot comput negative powers of polynomials"

        if(_ring != currRing): rChangeCurrRing(_ring)
        _p = pPower( p_Copy(self._poly,(<MPolynomialRing_libsingular>self._parent)._ring),exp)
        return new_MP((<MPolynomialRing_libsingular>self._parent),_p)


    def __neg__(self):
        cdef ring *_ring
        _ring = (<MPolynomialRing_libsingular>self._parent)._ring
        if(_ring != currRing): rChangeCurrRing(_ring)

        return new_MP((<MPolynomialRing_libsingular>self._parent),\
                                           p_Neg(p_Copy(self._poly,_ring),_ring))

    def _repr_(self):
        s =  self._repr_short_c()
        s = s.replace("+"," + ").replace("-"," - ")
        if s.startswith(" - "):
            return "-" + s[3:]
        else:
            return s

    def _repr_short(self):
        """
        This is a faster but less pretty way to print polynomials. If available
        it uses the short SINGULAR notation.
        """
        cdef ring *_ring = (<MPolynomialRing_libsingular>self._parent)._ring
        if _ring.CanShortOut:
            _ring.ShortOut = 1
            s = self._repr_short_c()
            _ring.ShortOut = 0
        else:
            s = self._repr_short_c()
        return s

    cdef _repr_short_c(self):
        """
        Raw SINGULAR printing.
        """
        s = p_String(self._poly, (<MPolynomialRing_libsingular>self._parent)._ring, (<MPolynomialRing_libsingular>self._parent)._ring)
        return s

    def _latex(self):
        #do it for real, may be slow
        raise NotImplementedError

    def _repr_with_changed_varnames(self, varnames):
        #plan: replace self._ring.names for the moment with varnames
        raise NotImplementedError

    def degree(self, MPolynomial_libsingular x=None):
        """
        Return the maximal degree of self in x, where x must be one of the
        generators for the parent of self.

        INPUT:
            x -- multivariate polynmial (a generator of the parent of self)
                 If x is not specified (or is None), return the total degree,
                 which is the maximum degree of any monomial.

        OUTPUT:
            integer

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x, y> = MPolynomialRing_libsingular(QQ, 2)
            sage: f = y^2 - x^9 - x
            sage: f.degree(x)
            9
            sage: f.degree(y)
            2
            sage: (y^10*x - 7*x^2*y^5 + 5*x^3).degree(x)
            3
            sage: (y^10*x - 7*x^2*y^5 + 5*x^3).degree(y)
            10

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x, y> = MPolynomialRing_libsingular(QQ, 2)
            sage: P(0).degree(x)
            0
            sage: P(1).degree(x)
            0

        """
        cdef ring *r = (<MPolynomialRing_libsingular>self._parent)._ring
        cdef poly *p = self._poly
        cdef int deg, _deg

        deg = 0

        if not x:
            return self.total_degree()

        # TODO: we can do this faster
        if not x in self._parent.gens():
            raise TypeError, "x must be one of the generators of the parent."
        for i from 1 <= i <= r.N:
            if p_GetExp(x._poly, i, r):
                break
        while p:
            _deg =  p_GetExp(p,i,r)
            if _deg > deg:
                deg = _deg
            p = pNext(p)

        return deg

    def newton_polytope(self):
        """
        Return the Newton polytope of this polynomial.

        You should have the optional polymake package installed.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y> = MPolynomialRing_libsingular(QQ,2)
            sage: f = 1 + x*y + x^3 + y^3
            sage: P = f.newton_polytope()
            sage: P
            Convex hull of points [[1, 0, 0], [1, 0, 3], [1, 1, 1], [1, 3, 0]]
            sage: P.facets()
            [(0, 1, 0), (3, -1, -1), (0, 0, 1)]
            sage: P.is_simple()
            True

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y> = MPolynomialRing_libsingular(QQ,2)
            sage: R(0).newton_polytope()
            Convex hull of points []
            sage: R(1).newton_polytope()
            Convex hull of points [[1, 0, 0]]

        """
        from sage.geometry.all import polymake
        e = self.exponents()
        a = [[1] + list(v) for v in e]
        P = polymake.convex_hull(a)
        return P

    def total_degree(self):
        """
        Return the total degree of self, which is the maximum degree
        of all monomials in self.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y,z> = MPolynomialRing_libsingular(QQ, 3)
            sage: f=2*x*y^3*z^2
            sage: f.total_degree()
            6
            sage: f=4*x^2*y^2*z^3
            sage: f.total_degree()
            7
            sage: f=99*x^6*y^3*z^9
            sage: f.total_degree()
            18
            sage: f=x*y^3*z^6+3*x^2
            sage: f.total_degree()
            10
            sage: f=z^3+8*x^4*y^5*z
            sage: f.total_degree()
            10
            sage: f=z^9+10*x^4+y^8*x^2
            sage: f.total_degree()
            10

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y,z> = MPolynomialRing_libsingular(QQ, 3)
            sage: R(0).total_degree()
            0
            sage: R(1).total_degree()
            0
        """
        cdef poly *p = self._poly
        cdef ring *r = (<MPolynomialRing_libsingular>self._parent)._ring
        cdef int l
        if self._poly == NULL:
            return 0
        if(r != currRing): rChangeCurrRing(r)
        return pLDeg(p,&l,r)

    def monomial_coefficient(self, MPolynomial_libsingular mon):
        """
        Return the coefficient of the monomial mon in self, where mon
        must have the same parent as self.

        INPUT:
            mon -- a monomial

        OUTPUT:
            ring element

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y> = MPolynomialRing_libsingular(QQ, 2)

        The coefficient returned is an element of the base ring of self; in
        this case, QQ.

            sage: f = 2 * x * y
            sage: c = f.monomial_coefficient(x*y); c
            2
            sage: c in QQ
            True

            sage: f = y^2 - x^9 - 7*x + 5*x*y
            sage: f.monomial_coefficient(y^2)
            1
            sage: f.monomial_coefficient(x*y)
            5
            sage: f.monomial_coefficient(x^9)
            -1
            sage: f.monomial_coefficient(x^10)
            0
        """
        cdef poly *p = self._poly
        cdef poly *m = mon._poly
        cdef ring *r = (<MPolynomialRing_libsingular>self._parent)._ring

        if not mon._parent is self._parent:
            raise TypeError, "mon must have same parent as self"

        while(p):
            if p_ExpVectorEqual(p, m, r) == 1:
                return co.si2sa(p_GetCoeff(p, r), r, (<MPolynomialRing_libsingular>self._parent)._base)
            p = pNext(p)

        return (<MPolynomialRing_libsingular>self._parent)._base(0)

    def dict(self):
        cdef poly *p
        cdef ring *r
        cdef int n
        cdef int v
        r = (<MPolynomialRing_libsingular>self._parent)._ring
        base = (<MPolynomialRing_libsingular>self._parent)._base
        p = self._poly
        pd = dict()
        while p:
            d = dict()
            # assuming that SINGULAR stores monomial dense
            for v from 1 <= v <= r.N:
                n = p_GetExp(p,v,r)
                if n!=0:
                    d[v-1] = n

            pd[ETuple(d,r.N)] = co.si2sa(p_GetCoeff(p, r), r, base)

            p = pNext(p)
        return pd

    def __getitem__(self,x):
        """
        same as self.monomial_coefficent but for exponent vectors.

        INPUT:
            x -- a tuple or, in case of a single-variable MPolynomial
                 ring x can also be an integer.

        EXAMPLES:
            sage: R.<x, y> = PolynomialRing(QQ, 2)
            sage: f = -10*x^3*y + 17*x*y
            sage: f[3,1]
            -10
            sage: f[1,1]
            17
            sage: f[0,1]
            0

            sage: R.<x> = PolynomialRing(GF(7),1); R
            Polynomial Ring in x over Finite Field of size 7
            sage: f = 5*x^2 + 3; f
            3 + 5*x^2
            sage: f[2]
            5
        """

        cdef poly *m
        cdef poly *p = self._poly
        cdef ring *r = (<MPolynomialRing_libsingular>self._parent)._ring
        cdef int i

        if PY_TYPE_CHECK(x, MPolynomial_libsingular):
            return self.monomial_coefficient(x)
        if not PY_TYPE_CHECK(x, tuple):
            try:
                x = tuple(x)
            except TypeError:
                x = (x,)

        if len(x) != (<MPolynomialRing_libsingular>self._parent).__ngens:
            raise TypeError, "x must have length self.ngens()"

        m = p_ISet(1,r)
        i = 1
        for e in x:
            p_SetExp(m, i, int(e), r)
            i += 1
        p_Setm(m, r)

        while(p):
            if p_ExpVectorEqual(p, m, r) == 1:
                p_Delete(&m,r)
                return co.si2sa(p_GetCoeff(p, r), r, (<MPolynomialRing_libsingular>self._parent)._base)
            p = pNext(p)

        p_Delete(&m,r)
        return (<MPolynomialRing_libsingular>self._parent)._base(0)

    def coefficient(self, mon):
        raise NotImplementedError

    def exponents(self):
        """
        Return the exponents of the monomials appearing in self.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<a,b,c> = MPolynomialRing_libsingular(QQ, 3)
            sage: f = a^3 + b + 2*b^2
            sage: f.exponents()
            [(3, 0, 0), (0, 2, 0), (0, 1, 0)]
        """
        cdef poly *p
        cdef ring *r
        cdef int v
        r = (<MPolynomialRing_libsingular>self._parent)._ring

        p = self._poly

        pl = list()
        while p:
            ml = list()
            for v from 1 <= v <= r.N:
                ml.append(p_GetExp(p,v,r))
            pl.append(tuple(ml))

            p = pNext(p)
        return pl

    def is_unit(self):
        """
        Return True if self is a unit.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y> = MPolynomialRing_libsingular(QQ, 2)
            sage: (x+y).is_unit()
            False
            sage: R(0).is_unit()
            False
            sage: R(-1).is_unit()
            True
            sage: R(-1 + x).is_unit()
            False
            sage: R(2).is_unit()
            True
        """
        return bool(p_IsUnit(self._poly, (<MPolynomialRing_libsingular>self._parent)._ring))

    def inverse_of_unit(self):
        """
        Return the inverse of self if self is a unit.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y> = MPolynomialRing_libsingular(QQ, 2)
        """
        cdef ring *_ring = (<MPolynomialRing_libsingular>self._parent)._ring
        if(_ring != currRing): rChangeCurrRing(_ring)

        if not p_IsUnit(self._poly, _ring):
            raise ArithmeticError, "is not a unit"
        else:
            return new_MP(self._parent,pInvers(0,self._poly,NULL))

    def is_homogeneous(self):
        """
        Return True if self is a homogeneous polynomial.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y> = MPolynomialRing_libsingular(RationalField(), 2)
            sage: (x+y).is_homogeneous()
            True
            sage: (x.parent()(0)).is_homogeneous()
            True
            sage: (x+y^2).is_homogeneous()
            False
            sage: (x^2 + y^2).is_homogeneous()
            True
            sage: (x^2 + y^2*x).is_homogeneous()
            False
            sage: (x^2*y + y^2*x).is_homogeneous()
            True

        """
        cdef ring *_ring = (<MPolynomialRing_libsingular>self._parent)._ring
        if(_ring != currRing): rChangeCurrRing(_ring)
        return bool(pIsHomogeneous(self._poly))

    def homogenize(self, var='h'):
        raise NotImplementedError

    def is_monomial(self):
        return not self._poly.next

    def fix(self, fixed):
        """
        Fixes some given variables in a given multivariate polynomial and
        returns the changed multivariate polynomials. The polynomial
        itself is not affected.  The variable,value pairs for fixing are
        to be provided as dictionary of the form {variable:value}.

        This is a special case of evaluating the polynomial with some of
        the variables constants and the others the original variables, but
        should be much faster if only few variables are to be fixed.

        INPUT:
            fixed -- dict with variable:value pairs

        OUTPUT:
            new MPolynomial

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: x, y = MPolynomialRing_libsingular(QQ,2,'xy').gens()
            sage: f = x^2 + y + x^2*y^2 + 5
            sage: f(5,y)
            25*y^2 + y + 30
            sage: f.fix({x:5})
            25*y^2 + y + 30

        """
        cdef int mi, i

        cdef MPolynomialRing_libsingular parent = <MPolynomialRing_libsingular>self._parent
        cdef ring *_ring = parent._ring

        if(_ring != currRing): rChangeCurrRing(_ring)

        cdef poly *_p = p_Copy(self._poly, _ring)

        for m,v in fixed.iteritems():
            if PY_TYPE_CHECK(m,int) or PY_TYPE_CHECK(m,Integer):
                mi = m+1
            elif PY_TYPE_CHECK(m,MPolynomial_libsingular) and <MPolynomialRing_libsingular>m.parent() is parent:
                for i from 0 < i <= _ring.N:
                    mi = p_GetExp((<MPolynomial_libsingular>m)._poly,i, _ring)
                    if mi!=0:
                        break
            else:
                raise TypeError, "keys do not match self's parent"

            _p = pSubst(p_Copy(_p, _ring), mi, (<MPolynomial_libsingular>parent._coerce_c(v))._poly)

        return new_MP(parent,_p)

    def monomials(self):
        raise NotImplementedError

    def constant_coefficent(self):
        raise NotImplementedError

    def is_univariate(self):
        return bool(len(self._variable_indices_(sort=False))<2)

    def univariate_polynomial(self, R=None):
        raise NotImplementedError

    def _variable_indices_(self, sort=True):
        cdef poly *p
        cdef ring *r = (<MPolynomialRing_libsingular>self._parent)._ring
        cdef int i
        s = set()
        p = self._poly
        while p:
            for i from 1 <= i <= r.N:
                if p_GetExp(p,i,r):
                    s.add(i)
            p = pNext(p)
        if sort:
            return sorted(s)
        else:
            return list(s)

    def variables(self, sort=True):
        cdef poly *p, *v
        cdef ring *r = (<MPolynomialRing_libsingular>self._parent)._ring
        cdef int i
        l = list()
        si = set()
        p = self._poly
        while p:
            for i from 1 <= i <= r.N:
                if i not in si and p_GetExp(p,i,r):
                    v = p_ISet(1,r)
                    p_SetExp(v, i, 1, r)
                    p_Setm(v, r)
                    l.append(new_MP(self._parent, v))
                    si.add(i)
            p = pNext(p)
        if sort:
            return sorted(l)
        else:
            return l

    def variable(self, i=0):
        return self.variables()[i]

    def nvariables(self):
        return self._variable_indices_(sort=False)

    def is_constant(self):
        return bool(p_IsConstant(self._poly, (<MPolynomialRing_libsingular>self._parent)._ring))

    cdef int is_constant_c(self):
        return p_IsConstant(self._poly, (<MPolynomialRing_libsingular>self._parent)._ring)

    def __hash__(self):
        s = p_String(self._poly, (<MPolynomialRing_libsingular>self._parent)._ring, (<MPolynomialRing_libsingular>self._parent)._ring)
        return hash(s)


    def lm(MPolynomial_libsingular self):
        """
        Returns the lead monomial of self with respect to the term
        order of self.parent(). In SAGE a monomial is a product of
        variables in some power without a coefficient.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular

            sage: R.<x,y,z>=MPolynomialRing_libsingular(GF(7),3,order='lex')
            sage: f = x^1*y^2 + y^3*z^4
            sage: f.lm()
            x*y^2
            sage: f = x^3*y^2*z^4 + x^3*y^2*z^1
            sage: f.lm()
            x^3*y^2*z^4

            sage: R.<x,y,z>=MPolynomialRing_libsingular(QQ,3,order='deglex')
            sage: f = x^1*y^2*z^3 + x^3*y^2*z^0
            sage: f.lm()
            x*y^2*z^3
            sage: f = x^1*y^2*z^4 + x^1*y^1*z^5
            sage: f.lm()
            x*y^2*z^4

            sage: R.<x,y,z>=PolynomialRing(GF(127),3,order='degrevlex')
            sage: f = x^1*y^5*z^2 + x^4*y^1*z^3
            sage: f.lm()
            x*y^5*z^2
            sage: f = x^4*y^7*z^1 + x^4*y^2*z^3
            sage: f.lm()
            x^4*y^7*z

        """
        cdef poly *_p
        cdef ring *_ring
        _ring = (<MPolynomialRing_libsingular>self._parent)._ring
        _p = p_Head(self._poly, _ring)
        p_SetCoeff(_p, n_Init(int(1),_ring), _ring)
        p_Setm(_p,_ring)
        return new_MP((<MPolynomialRing_libsingular>self._parent), _p)


    def lc(MPolynomial_libsingular self):
        """
        Leading coefficient of self. See self.lm() for details.
        """

        cdef poly *_p
        cdef ring *_ring
        cdef number *_n
        _ring = (<MPolynomialRing_libsingular>self._parent)._ring

        if(_ring != currRing): rChangeCurrRing(_ring)

        _p = p_Head(self._poly, _ring)
        _n = p_GetCoeff(_p, _ring)

        return co.si2sa(_n, _ring, (<MPolynomialRing_libsingular>self._parent)._base)

    def lt(MPolynomial_libsingular self):
        """
        Leading term of self. In SAGE a term is a product of variables
        in some power AND a coefficient.

        See self.lm() for details
        """
        return new_MP((<MPolynomialRing_libsingular>self._parent),
                                           p_Head(self._poly,(<MPolynomialRing_libsingular>self._parent)._ring))

    def is_zero(self):
        if self._poly is NULL:
            return True
        else:
            return False

    def __nonzero__(self):
        if self._poly:
            return True
        else:
            return False

    def __floordiv__(self,right):
        raise NotImplementedError

    def factor(self, param=0):
        """
        """
        cdef ring *_ring
        cdef intvec *iv
        cdef int *ivv
        cdef ideal *I
        cdef MPolynomialRing_libsingular parent
        cdef int i

        parent = self._parent
        _ring = parent._ring

        if(_ring != currRing): rChangeCurrRing(_ring)

        iv = NULL
        I = singclap_factorize ( self._poly, &iv , int(param)) #delete iv at some point

        if param!=1:
            ivv = iv.ivGetVec()
            v = [(new_MP(parent, p_Copy(I.m[i],_ring)) , ivv[i])   for i in range(I.ncols)]
        else:
            v = [(new_MP(parent, p_Copy(I.m[i],_ring)) , 1)   for i in range(I.ncols)]

        # TODO: peel of 1

        F = Factorization(v)
        F.sort()

        # delete intvec
        # delete ideal

        return F

    def lift(self, I):
        #m = idLift(Ideal(self), I, NULL, FALSE, TRUE );
        #matrix_to_list(m)
        raise NotImplementedError

    def gcd(self, right):
        """
        Return the greates common divisor of self and right.

        INPUT:
            right -- polynomial

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: f = (x*y*z)^6 - 1
            sage: g = (x*y*z)^4 - 1
            sage: f.gcd(g)
            x^2*y^2*z^2 - 1
            sage: GCD([x^3 - 3*x + 2, x^4 - 1, x^6 -1])
            x - 1

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: Q.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3)
            sage: P(0).gcd(Q(0))
            0
            sage: x.gcd(1)
            1

        """
        cdef MPolynomial_libsingular _right
        cdef poly *_res
        cdef ring *_ring

        _ring = (<MPolynomialRing_libsingular>self._parent)._ring

        if(_ring != currRing): rChangeCurrRing(_ring)

        if not PY_TYPE_CHECK(right, MPolynomial_libsingular):
            _right = (<MPolynomialRing_libsingular>self._parent)._coerce_c(right)
        else:
            _right = (<MPolynomial_libsingular>right)

        _res = singclap_gcd(p_Copy(self._poly, _ring), p_Copy(_right._poly, _ring))

        return new_MP((<MPolynomialRing_libsingular>self._parent), _res)

    def lcm(self, g):
        #poly *singclap_alglcm ( poly *f, poly *g );
        raise NotImplementedError

    def is_square_free(self):
        #BOOLEAN singclap_isSqrFree(poly f);
        raise NotImplementedError

    def quo_rem(self, MPolynomial_libsingular right):
        if self._parent is not right._parent:
            right = self._parent._coerce_c(right)
        raise NotImplementedError

    def _magma_(self):
        raise NotImplementedError

    def _singular_(self, singular=singular_default, have_ring=False):
        """
        Return a SINGULAR (as in the CAS) element for this
        element. The result is cached.

        INPUT:
            singular -- interpreter (default: singular_default)
            have_ring -- should the correct ring not be set in SINGULAR first (default:False)

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(GF(127),3)
            sage: x._singular_()
            x
            sage: f =(x^2 + 35*y + 128); f
            x^2 + 35*y + 1
            sage: x._singular_().name() == x._singular_().name()
            True


        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(GF(127),3)
            sage: P(0)._singular_()
            0

        """
        if not have_ring:
            self.parent()._singular_(singular).set_ring() #this is expensive

        try:
            if self.__singular is None:
                return self._singular_init_c(singular, True)

            self.__singular._check_valid()

            if self.__singular.parent() is singular:
                return self.__singular

        except (AttributeError, ValueError):
            pass

        return self._singular_init_c(singular, True)

    def _singular_init_(self,singular=singular_default, have_ring=False):
        """
        Return a new SINGULAR (as in the CAS) element for this element.

        INPUT:
            singular -- interpreter (default: singular_default)
            have_ring -- should the correct ring not be set in SINGULAR first (default:False)

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(GF(127),3)
            sage: x._singular_init_()
            x
            sage: (x^2+37*y+128)._singular_init_()
            x^2+37*y+1
            sage: x._singular_init_().name() == x._singular_init_().name()
            False

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P(0)._singular_init_()
            0
        """
        return self._singular_init_c(singular, have_ring)

    cdef _singular_init_c(self,singular, have_ring):
        """
        See MPolynomial_libsingular._singular_init_

        """
        if not have_ring:
            self.parent()._singular_(singular).set_ring() #this is expensive

        self.__singular = singular(str(self))
        return self.__singular

    def sub_m_mul_q(self, MPolynomial_libsingular m, MPolynomial_libsingular q):
        """
        Return self - m*q, where m must be a monomial and q a
        polynomial.

        INPUT:
            m -- a monomial
            q -- a polynomial

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: x.sub_m_mul_q(y,z)
            -y*z + x

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: Q.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P(0).sub_m_mul_q(P(0),P(1))
            0
            sage: x.sub_m_mul_q(Q.gen(1),Q.gen(2))
            -y*z + x

         """
        cdef ring *r = (<MPolynomialRing_libsingular>self._parent)._ring

        if not self._parent is m._parent:
            m = self._parent._coerce_c(m)
        if not self._parent is q._parent:
            q = self._parent._coerce_c(q)

        if m._poly and m._poly.next:
            raise ArithmeticError, "m must be a monomial"
        elif not m._poly:
            return self

        return new_MP(self._parent, p_Minus_mm_Mult_qq(p_Copy(self._poly, r), m._poly, q._poly, r))

    def add_m_mul_q(self, MPolynomial_libsingular m, MPolynomial_libsingular q):
        """
        Return self + m*q, where m must be a monomial and q a
        polynomial.

       INPUT:
            m -- a monomial
            q -- a polynomial

        EXAMPLE:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: x.add_m_mul_q(y,z)
            y*z + x

        TESTS:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: R.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P.<x,y,z>=MPolynomialRing_libsingular(QQ,3)
            sage: P(0).add_m_mul_q(P(0),P(1))
            0
            sage: x.add_m_mul_q(R.gen(),R.gen(1))
            x*y + x
         """

        cdef ring *r = (<MPolynomialRing_libsingular>self._parent)._ring

        if not self._parent is m._parent:
            m = self._parent._coerce_c(m)
        if not self._parent is q._parent:
            q = self._parent._coerce_c(q)

        if m._poly and m._poly.next:
            raise ArithmeticError, "m must be a monomial"
        elif not m._poly:
            return self

        return new_MP(self._parent, p_Plus_mm_Mult_qq(p_Copy(self._poly, r), m._poly, q._poly, r))


    def __reduce__(self):
        """

        Serialize self.

        EXAMPLES:
            sage: from sage.rings.polynomial.multi_polynomial_libsingular import MPolynomialRing_libsingular
            sage: P.<x,y,z> = MPolynomialRing_libsingular(QQ,3, order='degrevlex')
            sage: f = 27/113 * x^2 + y*z + 1/2
            sage: f == loads(dumps(f))
            True

            sage: P = MPolynomialRing_libsingular(GF(127),3,names='abc')
            sage: a,b,c = P.gens()
            sage: f = 57 * a^2*b + 43 * c + 1
            sage: f == loads(dumps(f))
            True

        """
        return sage.rings.polynomial.multi_polynomial_libsingular.unpickle_MPolynomial_libsingular, ( self._parent, self.dict() )

def unpickle_MPolynomial_libsingular(MPolynomialRing_libsingular R, d):
    """
    Deserialize a MPolynomial_libsingular object

    INPUT:
        R -- the base ring
        d -- a Python dictionary as returned by MPolynomial_libsingular.dict

    """
    cdef ring *r = R._ring
    cdef poly *m, *p
    cdef int _i, _e
    p = p_ISet(0,r)
    for mon,c in d.iteritems():
        m = p_Init(r)
        for i,e in mon.sparse_iter():
            _i = i
            if _i >= r.N:
                p_Delete(&p,r)
                p_Delete(&m,r)
                raise TypeError, "variable index too big"
            _e = e
            if _e <= 0:
                p_Delete(&p,r)
                p_Delete(&m,r)
                raise TypeError, "exponent too small"
            p_SetExp(m, _i+1,_e, r)
        p_SetCoeff(m, co.sa2si(c, r), r)
        p_Setm(m,r)
        p = p_Add_q(p,m,r)
    return new_MP(R,p)
