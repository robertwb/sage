"""
Wrapper for Singular's Polynomial Arithmetic

AUTHOR:

- Martin Albrecht (2009-07): refactoring
"""
#*****************************************************************************
#       Copyright (C) 2009 Martin Albrecht <malb@informatik.uni-bremen.de>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************
include "../../ext/interrupt.pxi"

cdef extern from "":
    int unlikely(int)

import re
plusminus_pattern = re.compile("([^\(^])([\+\-])")

from sage.libs.singular.decl cimport number, ideal
from sage.libs.singular.decl cimport currRing, rChangeCurrRing
from sage.libs.singular.decl cimport p_Copy, p_Add_q, p_Neg, pp_Mult_nn, p_GetCoeff, p_IsConstant, p_Cmp, pNext
from sage.libs.singular.decl cimport p_GetMaxExp, pp_Mult_qq, pPower, p_String, p_GetExp, pLDeg
from sage.libs.singular.decl cimport n_Delete, idInit, fast_map, id_Delete, n_GreaterZero, n_Sub, nInvers
from sage.libs.singular.decl cimport omAlloc0, omStrDup, omFree
from sage.libs.singular.decl cimport p_GetComp, p_SetComp


from sage.libs.singular.singular cimport sa2si, si2sa, overflow_check

from sage.misc.latex import latex


cdef int singular_polynomial_add(poly **ret, poly *p, poly *q, ring *r):
    """
    ``ret[0] = p+q`` where ``p`` and ``p`` in ``r``.

    INPUT:

    - ``ret`` - a pointer to a Singular polynomial to store the result in
    - ``p`` - a Singular polynomial
    - ``q`` - a Singular polynomial
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: x + y # indirect doctest
        x + y

        sage: x + P(0)
        x
    """
    if(r != currRing): rChangeCurrRing(r)
    p = p_Copy(p, r)
    q = p_Copy(q, r)
    ret[0] = p_Add_q(p, q, r)
    return 0;

cdef int singular_polynomial_sub(poly **ret, poly *p, poly *q, ring *r):
    """
    ``ret[0] = p-q`` where ``p`` and ``p`` in ``r``.

    INPUT:

    - ``ret`` - a pointer to a Singular polynomial to store the result in
    - ``p`` - a Singular polynomial
    - ``q`` - a Singular polynomial
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: x - y # indirect doctest
        x - y

        sage: x + P(0)
        x
    """
    if(r != currRing): rChangeCurrRing(r)
    p = p_Copy(p, r)
    q = p_Copy(q, r)
    ret[0] = p_Add_q(p, p_Neg(q, r), r)
    return 0;

cdef int singular_polynomial_rmul(poly **ret, poly *p, RingElement n, ring *r):
    """
    ``ret[0] = n*p`` where ``n`` is a coefficient and ``p`` in ``r``.

    INPUT:

    - ``ret`` - a pointer to a Singular polynomial to store the result in
    - ``p`` - a Singular polynomial
    - ``n`` - a Sage coefficient
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: 2*x # indirect doctest
        2*x

        sage: P(0)*x
        0
    """
    if(r != currRing): rChangeCurrRing(r)
    cdef number *_n = sa2si(n,r)
    ret[0] = pp_Mult_nn(p, _n, r)
    n_Delete(&_n, r)
    return 0

cdef int singular_polynomial_call(poly **ret, poly *p, ring *r, list args, poly *(*get_element)(object)):
    """
    ``ret[0] = p(*args)`` where each entry in arg  is a polynomial and ``p`` in ``r``.

    INPUT:

    - ``ret`` - a pointer to a Singular polynomial to store the result in
    - ``p`` - a Singular polynomial
    - ``r`` - a Singular ring
    - ``args`` - a list/tuple of elements which can be converted to
      Singular polynomials using the ``(get_element)`` function
      provided.
    - ``(*get_element)`` - a function to turn a Sage element into a
      Singular element.

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: x(0,0,0) # indirect doctest
        0

        sage: (3*x*z)(x,x,x)
        3*x^2
    """
    cdef long l = len(args)
    cdef ideal *to_id = idInit(l,1)
    for i from 0 <= i < l:
        to_id.m[i]= p_Copy( get_element(args[i]), r)

    cdef ideal *from_id=idInit(1,1)
    from_id.m[0] = p

    cdef ideal *res_id = fast_map(from_id, r, to_id, r)
    ret[0] = res_id.m[0]

    from_id.m[0] = NULL
    res_id.m[0] = NULL

    id_Delete(&to_id, r)
    id_Delete(&from_id, r)
    id_Delete(&res_id, r)

    return 0

cdef int singular_polynomial_cmp(poly *p, poly *q, ring *r):
    """
    Compare two Singular elements ``p`` and ``q`` in ``r``.

    INPUT:

    - ``p`` - a Singular polynomial
    - ``q`` - a Singular polynomial
    - ``r`` - a Singular ring

    EXAMPLES::

        sage: P.<x,y,z> = PolynomialRing(QQ,order='degrevlex')
        sage: x == x
        True

        sage: x > y
        True
        sage: y^2 > x
        True

        sage: (2/3*x^2 + 1/2*y + 3) > (2/3*x^2 + 1/4*y + 10)
        True
    """
    cdef number *h
    cdef int ret = 0

    if(r != currRing): rChangeCurrRing(r)

    # handle special cases first (slight slowdown, as special cases
    # are - well - special
    if p == NULL:
        if q == NULL:
            # compare 0, 0
            return 0
        elif p_IsConstant(q,r):
            # compare 0, const
            return 1-2*n_GreaterZero(p_GetCoeff(q,r), r) # -1: <, 1: > #
    elif q == NULL:
        if p_IsConstant(p,r):
            # compare const, 0
            return -1+2*n_GreaterZero(p_GetCoeff(p,r), r) # -1: <, 1: >
    #else

    while ret==0 and p!=NULL and q!=NULL:
        ret = p_Cmp( p, q, r)

        if ret==0:
            h = n_Sub(p_GetCoeff(p, r),p_GetCoeff(q, r), r)
            # compare coeffs
            ret = -1+r.cf.nIsZero(h)+2*r.cf.nGreaterZero(h) # -1: <, 0:==, 1: >
            n_Delete(&h, r)
        p = pNext(p)
        q = pNext(q)

    if ret==0:
        if p==NULL and q != NULL:
            ret = -1
        elif p!=NULL and q==NULL:
            ret = 1

    return ret

cdef int singular_polynomial_mul(poly** ret, poly *p, poly *q, ring *r) except -1:
    """
    ``ret[0] = p*q`` where ``p`` and ``p`` in ``r``.

    INPUT:

    - ``ret`` - a pointer to a Singular polynomial to store the result in
    - ``p`` - a Singular polynomial
    - ``q`` - a Singular polynomial
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: x*y # indirect doctest
        x*y

        sage: x * P(0)
        0
    """
    if(r != currRing): rChangeCurrRing(r)
    cdef unsigned long le = p_GetMaxExp(p, r)
    cdef unsigned long lr = p_GetMaxExp(q, r)
    cdef unsigned long esum = le + lr
    overflow_check(esum)
    ret[0] = pp_Mult_qq(p, q, r)
    return 0;

cdef int singular_polynomial_div_coeff(poly** ret, poly *p, poly *q, ring *r) except -1:
    """
    ``ret[0] = p/n`` where ``p`` and ``q`` in ``r`` and ``q`` constant.

    The last condition is not checked.

    INPUT:

    - ``ret`` - a pointer to a Singular polynomial to store the result in
    - ``p`` - a Singular polynomial
    - ``q`` - a constant Singular polynomial
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: x/2 # indirect doctest
        1/2*x

        sage: x/0
        Traceback (most recent call last):
        ...
        ZeroDivisionError: rational division by zero
    """
    if q == NULL:
        raise ZeroDivisionError
    cdef number *n = p_GetCoeff(q, r)
    n = nInvers(n)
    ret[0] = pp_Mult_nn(p, n, r)
    n_Delete(&n, r)
    return 0

cdef int singular_polynomial_pow(poly **ret, poly *p, long exp, ring *r) except -1:
    """
    ``ret[0] = p**exp`` where ``p`` in ``r`` and ``exp`` > 0.

    The last condition is not checked.

    INPUT:

    - ``ret`` - a pointer to a Singular polynomial to store the result in
    - ``p`` - a Singular polynomial
    - ``exp`` - integer
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: f = 3*x*y + 5/2*z
        sage: f*f == f^2 # indirect doctest
        True
        sage: f^2
        9*x^2*y^2 + 15*x*y*z + 25/4*z^2
        sage: f^0
        1
        sage: f^(2^60)
        Traceback (most recent call last):
        ...
        OverflowError: ...
    """
    cdef unsigned long v = p_GetMaxExp(p, r)
    v = v * exp

    overflow_check(v)

    if(r != currRing): rChangeCurrRing(r)
    cdef int count = singular_polynomial_length_bounded(p,15)
    if count >= 15 or exp > 15:
        _sig_on
    ret[0] = pPower( p_Copy(p,r), exp)
    if count >= 15 or exp > 15:
        _sig_off
    return 0

cdef int singular_polynomial_neg(poly **ret, poly *p, ring *r):
    """
    ``ret[0] = -p where ``p`` in ``r``.

    The last condition is not checked.

    INPUT:

    - ``ret`` - a pointer to a Singular polynomial to store the result in
    - ``p`` - a Singular polynomial
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: f = 3*x*y + 5/2*z
        sage: -f # indirect doctest
        -3*x*y - 5/2*z
        sage: -P(0)
        0
    """
    if(r != currRing): rChangeCurrRing(r)
    ret[0] = p_Neg(p_Copy(p,r),r)
    return 0

cdef object singular_polynomial_str(poly *p, ring *r):
    """
    Return the string representation of ``p``.

    INPUT:

    - ``p`` - a Singular polynomial
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = ZZ[]
        sage: str(x) # indirect doctest
        'x'
        sage: str(10*x)
        '10*x'
    """
    if(r!=currRing): rChangeCurrRing(r)

    s = p_String(p, r, r)
    s = re.sub(plusminus_pattern, "\\1 \\2 ", s)
    return s


cdef object singular_polynomial_latex(poly *p, ring *r, object base, object latex_gens):
    """
    Return the LaTeX string representation of ``p``.

    INPUT:

    - ``p`` - a Singular polynomial
    - ``r`` - a Singular ring

    EXAMPLE::

        sage: P.<x,y,z> = QQ[]
        sage: latex(x) # indirect doctest
        x
        sage: latex(10*x^2 + 1/2*y)
        10 x^{2} + \frac{1}{2} y
    """
    poly = ""
    cdef long e,j
    cdef int n = r.N
    while p:
        sign_switch = False

        # First determine the multinomial:
        multi = ""
        for j in range(1,n+1):
            e = p_GetExp(p, j, r)
            if e > 0:
                multi += " "+latex_gens[j-1]
            if e > 1:
                multi += "^{%d}"%e
        multi = multi.lstrip().rstrip()

        # Next determine coefficient of multinomial
        c =  si2sa( p_GetCoeff(p, r), r, base)
        if len(multi) == 0:
            multi = latex(c)
        elif c != 1:
            if  c == -1:
                if len(poly) > 0:
                    sign_switch = True
                else:
                    multi = "- %s"%(multi)
            else:
                multi = "%s %s"%(latex(c),multi)

        # Now add on coefficiented multinomials
        if len(poly) > 0:
            if sign_switch:
                poly = poly + " - "
            else:
                poly = poly + " + "
        poly = poly + multi

        p = pNext(p)

    poly = poly.lstrip().rstrip()
    poly = poly.replace("+ -","- ")

    if len(poly) == 0:
        return "0"
    return poly

cdef object singular_polynomial_str_with_changed_varnames(poly *p, ring *r, object varnames):
    cdef char **_names
    cdef char **_orig_names
    cdef char *_name
    cdef int i

    if len(varnames) != r.N:
        raise TypeError("len(varnames) doesn't equal self.parent().ngens()")

    _names = <char**>omAlloc0(sizeof(char*)*r.N)
    for i from 0 <= i < r.N:
        _name = varnames[i]
        _names[i] = omStrDup(_name)

    _orig_names = r.names
    r.names = _names
    s = singular_polynomial_str(p, r)
    r.names = _orig_names

    for i from 0 <= i < r.N:
        omFree(_names[i])
    omFree(_names)
    return s

cdef long singular_polynomial_deg(poly *p, poly *x, ring *r):
    cdef int deg, _deg, i

    deg = 0
    if p == NULL:
        return -1
    if(r != currRing): rChangeCurrRing(r)
    if x == NULL:
        return pLDeg(p,&deg,r)

    for i in range(1,r.N+1):
        if p_GetExp(x, i, r):
            break
    while p:
        _deg =  p_GetExp(p,i,r)
        if _deg > deg:
            deg = _deg
        p = pNext(p)
    return deg

cdef inline int singular_polynomial_length_bounded(poly *p, int bound):
    """
    Return the number of monomials in ``p`` but stop counting at
    ``bound``.

    This is useful to estimate whether a certain calculation will take
    long or not.

    INPUT:

    - ``p`` - a Singular polynomial
    - ``bound`` - an integer > 0
    """
    cdef int count = 0
    while p != NULL and count < bound:
        p = pNext(p)
        count += 1
    return count

cdef int singular_vector_maximal_component(poly *v, ring *r) except -1:
    """
    returns the maximal module component of the vector ``v``.
    INPUT:

       - ``v`` - a polynomial/vector
       - ``r`` - a ring
    """
    cdef int res=0
    while v!=NULL:
        res=max(p_GetComp(v, r), res)
        v = pNext(v)
    return res
