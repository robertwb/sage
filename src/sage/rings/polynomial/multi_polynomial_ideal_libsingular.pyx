"""
Direct low-level access to SINGULAR's Groebner basis engine via libSINGULAR.

AUTHOR:

- Martin Albrecht (2007-08-08): initial version

EXAMPLES::

    sage: x,y,z = QQ['x,y,z'].gens()
    sage: I = ideal(x^5 + y^4 + z^3 - 1,  x^3 + y^3 + z^2 - 1)
    sage: I.groebner_basis('libsingular:std')
    [y^6 + x*y^4 + 2*y^3*z^2 + x*z^3 + z^4 - 2*y^3 - 2*z^2 - x + 1,
    x^2*y^3 - y^4 + x^2*z^2 - z^3 - x^2 + 1, x^3 + y^3 + z^2 - 1]

We compute a Groebner basis for cyclic 6, which is a standard
benchmark and test ideal::

    sage: R.<x,y,z,t,u,v> = QQ['x,y,z,t,u,v']
    sage: I = sage.rings.ideal.Cyclic(R,6)
    sage: B = I.groebner_basis('libsingular:std')
    sage: len(B)
    45

Two examples from the Mathematica documentation (done in Sage):

- We compute a Groebner basis::

        sage: R.<x,y> = PolynomialRing(QQ, order='lex')
        sage: ideal(x^2 - 2*y^2, x*y - 3).groebner_basis('libsingular:slimgb')
        [x - 2/3*y^3, y^4 - 9/2]

- We show that three polynomials have no common root::

        sage: R.<x,y> = QQ[]
        sage: ideal(x+y, x^2 - 1, y^2 - 2*x).groebner_basis('libsingular:slimgb')
        [1]
"""

#*****************************************************************************
#
#   Sage: System for Algebra and Geometry Experimentation
#
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
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


include "sage/ext/interrupt.pxi"
include "../../libs/singular/singular-cdefs.pxi"

from sage.structure.parent_base cimport ParentWithBase

from sage.rings.polynomial.multi_polynomial_libsingular cimport new_MP

from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal
from sage.rings.polynomial.multi_polynomial_libsingular cimport MPolynomial_libsingular
from sage.rings.polynomial.multi_polynomial_libsingular cimport MPolynomialRing_libsingular
from sage.structure.sequence import Sequence

cdef object singular_ideal_to_sage_sequence(ideal *i, ring *r, object parent):
    """
    convert a SINGULAR ideal to a Sage Sequence (the format Sage
    stores a Groebner basis in)

    INPUT:

    - ``i`` -- a SINGULAR ideal
    - ``r`` -- a SINGULAR ring
    - ``parent`` -- a Sage ring matching r
    """
    cdef int j
    cdef MPolynomial_libsingular p

    l = []

    for j from 0 <= j < IDELEMS(i):
        p = new_MP(parent, p_Copy(i.m[j], r))
        l.append( p )

    return Sequence(l, check=False, immutable=True)

cdef ideal *sage_ideal_to_singular_ideal(I):
    """
    convert a Sage ideal to a SINGULAR ideal

    INPUT:

    - ``I`` -- a Sage ideal in a ring of type
      :class:`~sage.rings.polynomial.multi_polynomial_libsingular.MPolynomialRing_libsingular`
    """
    R = I.ring()
    gens = I.gens()
    cdef ideal *result
    cdef ring *r
    cdef ideal *i
    cdef int j = 0

    if not PY_TYPE_CHECK(R,MPolynomialRing_libsingular):
        raise TypeError, "ring must be of type MPolynomialRing_libsingular"

    r = (<MPolynomialRing_libsingular>R)._ring
    rChangeCurrRing(r);

    i = idInit(len(gens),1)
    for f in gens:
        if not PY_TYPE_CHECK(f,MPolynomial_libsingular):
            id_Delete(&i, r)
            raise TypeError, "all generators must be of type MPolynomial_libsingular"
        i.m[j] = p_Copy((<MPolynomial_libsingular>f)._poly, r)
        j+=1
    return i

def kbase_libsingular(I):
    """
    SINGULAR's ``kbase()`` algorithm.

    INPUT:

    - ``I`` -- a groebner basis of an ideal

    OUTPUT:

    Computes a vector space basis (consisting of monomials) of the quotient
    ring by the ideal, resp. of a free module by the module, in case it is
    finite dimensional and if the input is a standard basis with respect to
    the ring ordering. If the input is not a standard basis, the leading terms
    of the input are used and the result may have no meaning.

    EXAMPLES::

        sage: R.<x,y> = PolynomialRing(QQ, order='lex')
        sage: I = R.ideal(x^2-2*y^2, x*y-3)
        sage: I.normal_basis()
        [y^3, y^2, y, 1]
    """

    global singular_options

    cdef ideal *i = sage_ideal_to_singular_ideal(I)
    cdef ring *r = currRing
    cdef ideal *q = currQuotient

    cdef ideal *result
    singular_options = singular_options | Sy_bit(OPT_REDSB)

    _sig_on
    result = scKBase(-1, i, q)
    _sig_off

    id_Delete(&i, r)
    res = singular_ideal_to_sage_sequence(result,r,I.ring())

    id_Delete(&result, r)

    return res

def std_libsingular(I):
    """
    SINGULAR's ``std()`` algorithm.

    INPUT:

    - ``I`` -- a Sage ideal
    """
    global singular_options

    cdef ideal *i = sage_ideal_to_singular_ideal(I)
    cdef ring *r = currRing
    cdef tHomog hom = testHomog
    cdef ideal *result

    singular_options = singular_options | Sy_bit(OPT_REDSB)

    _sig_on
    result =kStd(i,NULL,hom,NULL)
    _sig_off

    idSkipZeroes(result)


    id_Delete(&i,r)

    res = singular_ideal_to_sage_sequence(result,r,I.ring())

    id_Delete(&result,r)
    return res


def slimgb_libsingular(I):
    """
    SINGULAR's ``slimgb()`` algorithm.

    INPUT:

    - ``I`` -- a Sage ideal
    """
    global singular_options

    cdef tHomog hom=testHomog
    cdef ideal *i
    cdef ring *r
    cdef ideal *result

    i = sage_ideal_to_singular_ideal(I)
    r = currRing

    if r.OrdSgn!=1 :
        id_Delete(&i, r)
        raise TypeError, "ordering must be global for slimgb"

    if i.rank < idRankFreeModule(i, r):
        id_Delete(&i, r)
        raise TypeError

    singular_options = singular_options | Sy_bit(OPT_REDSB)

    _sig_on
    result = t_rep_gb(r, i, i.rank, 0)
    _sig_off

    id_Delete(&i,r)

    res = singular_ideal_to_sage_sequence(result,r,I.ring())

    id_Delete(&result,r)
    return res

def interred_libsingular(I):
    """
    SINGULAR's ``interred()`` command.

    INPUT:

    - ``I`` -- a Sage ideal

    EXAMPLES::

        sage: P.<x,y,z> = PolynomialRing(ZZ)
        sage: I = ideal( x^2 - 3*y, y^3 - x*y, z^3 - x, x^4 - y*z + 1 )
        sage: I.interreduced_basis()
        [9*y^2 - y*z + 1, x^2 - 3*y, z^3 - x, y^3 - x*y]

        sage: P.<x,y,z> = PolynomialRing(QQ)
        sage: I = ideal( x^2 - 3*y, y^3 - x*y, z^3 - x, x^4 - y*z + 1 )
        sage: I.interreduced_basis()
        [y^2 - 1/9*y*z + 1/9, x^2 - 3*y, z^3 - x, y*z^2 - 81*x*y - 9*y - z]
    """
    global singular_options

    cdef ideal *i
    cdef ideal *result
    cdef ring *r
    cdef number *n
    cdef poly *p
    cdef int j
    cdef int bck

    if len(I.gens()) == 0:
        return Sequence([], check=False, immutable=True)

    i = sage_ideal_to_singular_ideal(I)
    r = currRing

    bck = singular_options
    singular_options = singular_options | Sy_bit(OPT_REDTAIL)|Sy_bit(OPT_REDSB)
    _sig_on
    result = kInterRed(i,NULL)
    _sig_off
    singular_options = bck


    # divide head by coefficents
    if r.ringtype == 0:
        for j from 0 <= j < IDELEMS(result):
            p = result.m[j]
            n = p_GetCoeff(p,r)
            n = nInvers(n)
            result.m[j] = pp_Mult_nn(p, n, r)
            p_Delete(&p,r)
            n_Delete(&n,r)

    id_Delete(&i,r)

    res = singular_ideal_to_sage_sequence(result,r,I.ring())

    id_Delete(&result,r)
    return res
