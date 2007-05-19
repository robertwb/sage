r"""
Frobenius on Monsky-Washnitzer cohomology, for largish p

This is a wrapper for the frobenius() function in frobenius_cpp.cpp.

AUTHOR:
    -- David Harvey (2007-05)
"""

#################################################################################
#       Copyright (C) 2007 David Harvey <dmharvey@math.harvard.edu>
#                          William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************


from sage.libs.ntl.ntl cimport ntl_ZZ, ntl_ZZX, ntl_mat_ZZ
from sage.libs.ntl.all import ZZ, ZZX
from sage.matrix.all import Matrix
from sage.rings.all import Qp, O as big_oh

include "sage/libs/ntl/decl.pxi"
include "sage/ext/interrupt.pxi"


cdef extern from "frobenius_cpp.h":
     int frobenius_cpp "frobenius" (mat_ZZ output, ntl_c_ZZ p, int N, ntl_c_ZZX Q)


def frobenius(p, N, Q):
   r"""
   Computes the matrix of Frobenius acting on the Monsky-Washnitzer cohomology
   of a hyperelliptic curve $y^2 = Q(x)$, with respect to the basis $x^i dx/y$,
   $0 \leq i < 2g$.

   INPUT:
      p -- a prime
      Q -- a monic polynomial in $\Z[x]$ of odd degree. Must have no multiple
           roots mod p.
      N -- precision parameter; the output matrix will be correct modulo $p^N$.

   PRECONDITIONS:
      Must have $p > (2g+1)(2N-1)$, where $g = (\deg(Q)-1)/2$ is the genus
      of the curve.

   ALGORITHM:
      Described in ``Kedlaya's algorithm in larger characteristic'' by David
      Harvey. Running time is theoretically soft-$O(p^{1/2} N^{5/2} g^{7/2})$.

   TODO:
      Remove the restriction on $p$. Probably by merging in Robert's code,
      which eventually needs a fast C++/NTL implementation.

   EXAMPLES:
      sage: from sage.schemes.hyperelliptic_curves.frobenius import frobenius
      sage: R.<x> = PolynomialRing(ZZ)
      sage: f = x^5 + 2*x^2 + x + 1; p = 101
      sage: M = frobenius(p, 4, f); M
       [     51*101 + 14*101^2 + 89*101^3 + O(101^4)      11*101 + 17*101^2 + 37*101^3 + O(101^4) 93 + 14*101 + 19*101^2 + 43*101^3 + O(101^4)  62 + 4*101 + 51*101^2 + 11*101^3 + O(101^4)]
       [     22*101 + 77*101^2 + 90*101^3 + O(101^4)      22*101 + 55*101^2 + 47*101^3 + O(101^4) 55 + 79*101 + 72*101^2 + 51*101^3 + O(101^4)  19 + 7*101 + 63*101^2 + 59*101^3 + O(101^4)]
       [      8*101 + 63*101^2 + 75*101^3 + O(101^4)      13*101 + 88*101^2 + 58*101^3 + O(101^4) 65 + 97*101 + 26*101^2 + 98*101^3 + O(101^4) 42 + 94*101 + 58*101^2 + 54*101^3 + O(101^4)]
       [     84*101 + 92*101^2 + 56*101^3 + O(101^4)      77*101 + 32*101^2 + 79*101^3 + O(101^4) 89 + 39*101 + 79*101^2 + 82*101^3 + O(101^4)  29 + 31*101 + 4*101^2 + 68*101^3 + O(101^4)]
      sage: -M.trace()
       7 + O(101^4)
      sage: sum([legendre_symbol(f(i), p) for i in range(p)])
       7
      sage: ZZ(M.det())
       10201

   AUTHORS:
      -- David Harvey (2007-05)

   """

   # SAGE objects that wrap the NTL objects
   cdef ntl_ZZ pp
   cdef ntl_ZZX QQ
   cdef ntl_mat_ZZ mm   # the result will go in mm
   cdef int i, j

   if N < 1:
      raise ValueError, "N must be an integer >= 1"

   Q = Q.list()
   if len(Q) < 4 or len(Q) % 2 or Q[-1] != 1:
      raise ValueError, "Q must be a monic polynomial of odd degree >= 3"
   QQ = ZZX(Q)

   bound = (len(Q) - 1) * (2*N - 1)
   if p <= bound:
      raise ValueError, "In the current implementation, p must be greater than (2g+1)(2N-1) = %s" % bound

   pp = ZZ(p)

   cdef int g    # the genus
   g = (len(Q) / 2) - 1

   # Note: the C++ code actually resets the size of the matrix, but this seems
   # to confuse the SAGE NTL wrapper. So to be safe I'm setting it ahead of
   # time.
   mm = ntl_mat_ZZ(2*g, 2*g)

   # actual NTL objects
   cdef ntl_c_ZZ ppp
   cdef ntl_c_ZZX QQQ
   cdef mat_ZZ* mmm
   ppp = pp.x[0]
   QQQ = QQ.x[0]
   mmm = mm.x

   cdef int result
   _sig_on
   result = frobenius_cpp(mmm[0], ppp, N, QQQ)
   _sig_off

   if not result:
      raise ValueError, "Could not compute frobenius matrix. Perhaps the curve was singular at p."

   R = Qp(p, N)
   prec = big_oh(p**N)
   data = [[mm[j, i].get_as_sage_int() + prec for i from 0 <= i < 2*g] for j from 0 <= j < 2*g]
   return Matrix(R, data)


################ end of file
