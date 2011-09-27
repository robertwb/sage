"""
Dense matrices over `\ZZ/n\ZZ` for `n < 2^{23}` using LinBox's ``Modular<float>``

AUTHORS:
- Burcin Erocal
- Martin Albrecht
"""
###############################################################################
#   SAGE: Open Source Mathematical Software
#       Copyright (C) 2011 Burcin Erocal <burcin@erocal.org>
#       Copyright (C) 2011 Martin Albrecht <martinralbrecht@googlemail.com>
#  Distributed under the terms of the GNU General Public License (GPL),
#  version 2 or any later version.  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

include "../ext/stdsage.pxi"
include "../ext/interrupt.pxi"

# randstate in template needs this
include '../ext/random.pxi'

from sage.libs.linbox.echelonform cimport  BlasMatrix

from sage.libs.linbox.modular cimport ModDoubleField as ModField, ModDoubleFieldElement as ModFieldElement
from sage.libs.linbox.echelonform cimport EchelonFormDomainDouble as EchelonFormDomain

from sage.libs.linbox.fflas cimport ModDouble_fgemm as Mod_fgemm, ModDouble_fgemv as Mod_fgemv, \
    ModDoubleDet as ModDet, \
    ModDoubleRank as ModRank, ModDouble_echelon as Mod_echelon, \
    ModDouble_applyp as Mod_applyp, \
    ModDouble_MinPoly as Mod_MinPoly, \
    ModDouble_CharPoly as Mod_CharPoly

MAX_MODULUS = 2**23

cdef extern from "../rings/finite_rings/stdint.h":
    ctypedef int int_fast32_t
    ctypedef int int_fast64_t
    int_fast32_t INTEGER_MOD_INT32_LIMIT
    int_fast64_t INTEGER_MOD_INT64_LIMIT

from sage.rings.finite_rings.integer_mod cimport IntegerMod_int64

include "matrix_modn_dense_template.pxi"


cdef class Matrix_modn_dense_double(Matrix_modn_dense_template):
    r"""
    Dense matrices over `\ZZ/n\ZZ` for `n < 2^{23}` using LinBox's ``Modular<float>``

    These are matrices with integer entries mod ``n`` represented as
    floating-point numbers in a 64-bit word for use with LinBox routines.
    This allows for ``n`` up to `2^{23}`.  The
    ``Matrix_modn_dense_float`` class specializes to smaller moduli.

    Routines here are for the most basic access, see the
    `matrix_modn_dense_template.pxi` file for higher-level routines.
    """
    cdef set_unsafe_int(self, Py_ssize_t i, Py_ssize_t j, int value):
        r"""
        Set the (i,j) entry of self to the int value.

        EXAMPLE::

            sage: A = random_matrix(GF(3016963), 4, 4); A
            [ 220081 2824836  765701 2282256]
            [1795330  767112 2967421 1373921]
            [2757699 1142917 2720973 2877160]
            [1674049 1341486 2641133 2173280]
            sage: A[0,0] = 220082r; A
            [ 220082 2824836  765701 2282256]
            [1795330  767112 2967421 1373921]
            [2757699 1142917 2720973 2877160]
            [1674049 1341486 2641133 2173280]
            sage: a = A[0,0]; a
            220082
            sage: ~a
            2859358

            sage: A = random_matrix(Integers(5099106), 4, 4); A
            [2629491 1237101 2033003 3788106]
            [4649912 1157595 4928315 4382585]
            [4252686  978867 2601478 1759921]
            [1303120 1860486 3405811 2203284]
            sage: A[0,0] = 220082r; A
            [ 220082 1237101 2033003 3788106]
            [4649912 1157595 4928315 4382585]
            [4252686  978867 2601478 1759921]
            [1303120 1860486 3405811 2203284]
            sage: a = A[0,0]; a
            220082
            sage: a*a
            4777936
        """
        self._matrix[i][j] = <double>value

    cdef set_unsafe(self, Py_ssize_t i, Py_ssize_t j, x):
        r"""
        Set the (i,j) entry with no bounds-checking, or any other checks.

        Assumes that `x` is in the base ring.

        EXAMPLE::

            sage: A = random_matrix(GF(3016963), 4, 4); A
            [ 220081 2824836  765701 2282256]
            [1795330  767112 2967421 1373921]
            [2757699 1142917 2720973 2877160]
            [1674049 1341486 2641133 2173280]
            sage: K = A.base_ring()
            sage: A[0,0] = K(220082); A
            [ 220082 2824836  765701 2282256]
            [1795330  767112 2967421 1373921]
            [2757699 1142917 2720973 2877160]
            [1674049 1341486 2641133 2173280]
            sage: a = A[0,0]; a
            220082
            sage: ~a
            2859358

            sage: A = random_matrix(Integers(5099106), 4, 4); A
            [2629491 1237101 2033003 3788106]
            [4649912 1157595 4928315 4382585]
            [4252686  978867 2601478 1759921]
            [1303120 1860486 3405811 2203284]
            sage: K = A.base_ring()
            sage: A[0,0] = K(220081)
            sage: a = A[0,0]; a
            220081
            sage: a*a
            4337773
        """
        self._matrix[i][j] = <double>(<IntegerMod_int>x).ivalue

    cdef IntegerMod_abstract get_unsafe(self, Py_ssize_t i, Py_ssize_t j):
        r"""
        Return the (i,j) entry with no bounds-checking.

        EXAMPLE::

            sage: A = random_matrix(GF(3016963), 4, 4); A
            [ 220081 2824836  765701 2282256]
            [1795330  767112 2967421 1373921]
            [2757699 1142917 2720973 2877160]
            [1674049 1341486 2641133 2173280]
            sage: a = A[0,0]; a
            220081
            sage: ~a
            697224
            sage: K = A.base_ring()
            sage: ~K(220081)
            697224

            sage: A = random_matrix(Integers(5099106), 4, 4); A
            [2629491 1237101 2033003 3788106]
            [4649912 1157595 4928315 4382585]
            [4252686  978867 2601478 1759921]
            [1303120 1860486 3405811 2203284]
            sage: a = A[0,1]; a
            1237101
            sage: a*a
            3803997
            sage: K = A.base_ring()
            sage: K(1237101)^2
            3803997
        """
        if (<Matrix_modn_dense_template>self).p <= INTEGER_MOD_INT32_LIMIT:
            return IntegerMod_int(self._base_ring, <mod_int>(<Matrix_modn_dense_template>self)._matrix[i][j])
        else:
            return IntegerMod_int64(self._base_ring, <mod_int>(<Matrix_modn_dense_template>self)._matrix[i][j])
