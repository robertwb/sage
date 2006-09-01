"""
Minimal Polynomials of Linear Recurrence Sequences

AUTHOR:
    -- William Stein
"""


#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
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

import sage.rings.polynomial_ring as polynomial_ring
import sage.rings.rational_field

def berlekamp_massey(a):
    """
    Use the Berlekamp-Massey algorithm to find the minimal polynomial
    of a linearly recurrence sequence a.

    The minimal polynomial of a linear recurrence $\{a_r\}$ is by
    definition the unique monic polynomial~$g$, such that if $\{a_r\}$
    satisfies a linear recurrence $a_{j+k} + b_{j-1} a_{j-1+k} +
    \cdots + b_0 a_k=0$ (for all $k\geq 0$), then $g$ divides the
    polynomial $x^j + \sum_{i=0}^{j-1} b_i x^i$.

    INPUT:
        a -- a list of even length of elements of a field (or domain)

    OUTPUT:
        Polynomial -- the minimal polynomial of the sequence (as a
           polynomial over the field in which the entries of a live)

    EXAMPLES:
        sage: berlekamp_massey([1,2,1,2,1,2])
        x^2 - 1
        sage: berlekamp_massey([GF(7)(1),19,1,19])
        x^2 + 6
        sage: berlekamp_massey([2,2,1,2,1,191,393,132])
        x^4 - 36727/11711*x^3 + 34213/5019*x^2 + 7024942/35133*x - 335813/1673
        sage: berlekamp_massey(prime_range(2,38))
        x^6 - 14/9*x^5 - 7/9*x^4 + 157/54*x^3 - 25/27*x^2 - 73/18*x + 37/9
    """

    if not isinstance(a, list):
        raise TypeError, "Argument 1 must be a list."
    if len(a)%2 != 0:
        raise ValueError, "Argument 1 must have an even number of terms."

    M = len(a)//2

    try:
        K = a[0].parent().fraction_field()
    except AttributeError:
        K = sage.rings.rational_field.RationalField()
    R = polynomial_ring.PolynomialRing(K, name='x')
    x = R.gen()

    f = {}
    q = {}
    s = {}
    t = {}
    f[-1] = R(a)
    f[0] = x**(2*M)
    s[-1] = 1
    t[0] = 1
    s[0] = 0
    t[-1] = 0
    j = 0
    while f[j].degree() >= M:
        j += 1
        q[j], f[j] = f[j-2].quo_rem(f[j-1])
        # assert q[j]*f[j-1] + f[j] == f[j-2], "poly divide failed."
        s[j] = s[j-2] - q[j]*s[j-1]
        t[j] = t[j-2] - q[j]*t[j-1]
    t = s[j].reverse()
    f = ~(t[t.degree()]) * t  # make monic  (~ is inverse in python)
    return f
    return polynomial_ring.PolynomialRing(a[0].parent(),name='x')(f)
