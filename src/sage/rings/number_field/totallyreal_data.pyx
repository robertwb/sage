"""
Enumeration of Totally Real Fields

AUTHORS:
    -- John Voight (2007-10-09):
        * Improvements: Symth bound, Lagrange multipliers for b.
    -- John Voight (2007-09-19):
        * Various optimization tweaks.
    -- John Voight (2007-09-01):
        * Initial version.
"""

#***********************************************************************************************
#       Copyright (C) 2007 William Stein and John Voight
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
#***********************************************************************************************

include "../../ext/cdefs.pxi"
include "../../ext/stdsage.pxi"

from sage.rings.arith import binomial, gcd
from sage.rings.integer_ring import IntegerRing
from sage.rings.polynomial.polynomial_ring import PolynomialRing

import math, numpy

#***********************************************************************************************
# Auxiliary routines:
# Hermite constant, naive Newton-Raphson, and a specialized Lagrange multiplier solver.
#***********************************************************************************************

def hermite_constant(n):
    r"""
    This function returns the nth Hermite constant (typically denoted
    $gamma_n$), defined to be
    $$ \max_L \min_{0 \neq x \in L} ||x||^2 $$
    where $L$ runs over all lattices of dimension $n$ and determinant $1$.
    For $n \leq 8$ it returns the exact value of $\gamma_n$, and for $n > 9$
    it returns an upper bound on $\gamma_n$.

    INPUT:
    n -- integer

    OUTPUT:
    (an upper bound for) the Hermite constant gamma_n

    EXAMPLES:
    sage: hermite_constant(1) # trivial one-dimensional lattice
    1.0
    sage: hermite_constant(2) # Eisenstein lattice
    1.1547005383792515
    sage: 2/sqrt(3.)
    1.15470053837925
    sage: hermite_constant(8) # E_8
    2.0

    NOTES:
    The upper bounds used can be found in [CS] and [CE].

        REFERENCES:
            [CE] Henry Cohn and Noam Elkies, New upper bounds on sphere
                 packings I, Ann. Math. 157 (2003), 689--714.
            [CS] J.H. Conway and N.J.A. Sloane, Sphere packings, lattices and
                 groups, 3rd. ed., Grundlehren der Mathematischen Wissenschaften,
                 vol. 290, Springer-Verlag, New York, 1999.

    AUTHORS:
    - John Voight (2007-09-03)
    """

    if n <= 8:
        # Exact values are known for gamma_n.
        gamman = [1, 1, 4./3, 2, 4, 8, 64./3, 64, 256][n]
        gamma = gamman**(1./n)
    elif n <= 36:
        gamma = [2.13263235569928, 2.26363016185702, 2.39334691240146,
                 2.52178702088414, 2.64929462619823, 2.77580405570023,
                 2.90147761892077, 3.02639364467182, 3.15067928476872,
                 3.27433066745617, 3.39744386110070, 3.52006195697466,
                 3.64224310140724, 3.76403701226104, 3.88547626036618,
                 4.00659977840648, 4.12744375027069, 4.24804458298177,
                 4.36843113799634, 4.48863097933934, 4.60866759008263,
                 4.72856660611662, 4.84834821242630, 4.96803435811402,
                 5.08764086822471, 5.20718687262715, 5.32668836123079,
                 5.44615801810606][n-9]
    else:
        raise ValueError, "Please update Hermite constants!"

    return gamma

cdef eval_seq_as_poly(int *f, int n, double x):
    r"""
    Evaluates the sequence a, thought of as a polynomial with
        $$ f[n]*x^n + f[n-1]*x^(n-1) + ... + f[0]. $$
    """
    cdef double s, xp

    # Horner's method: With polynomials of small degree, we shouldn't
    # expect asymptotic methods to be any faster.
    s = f[n]
    for i from n > i >= 0:
        s = s*x+f[i]
    return s

cdef newton(int *f, int *df, int n, double x0, double eps):
    r"""
    Find the real root x of f (with derivative df) near x0
    with provable precision eps, i.e. |x-z| < eps where z is the actual
    root.
    The sequence a corresponds to the polynomial f with
        $$ f(x) = x^n + a[n-1]*x^(n-1) + ... + a[0]. $$
    This function (for speed reasons) has no error checking and no
    guarantees are made as to the convergence; a naive Newton-Raphson
    method is used.
    """
    cdef double x, rdx

    x = x0
    dx = eval_seq_as_poly(f,n,x)/eval_seq_as_poly(df,n-1,x)
    x -= dx
    while abs(dx) > eps:
        # In truly optimized code, one could tune by automatically
        # iterating a certain number of times based on the size of dx to
        # save on a few comparisons.
        # This savings should be almost negligible...?
        dx = eval_seq_as_poly(f,n,x)/eval_seq_as_poly(df,n-1,x)
        x -= dx

    # Small hack for improved performance elsewhere: if it is close to an
    # integer, give it full precision as an integer.
    rdx = round(x)
    if abs(rdx-x) < eps:
        x = rdx

    # Now ensure that either f(x-eps) or f(x+eps) has opposite sign
    # as f(x), which implies that |x-z| < eps.
    fx = eval_seq_as_poly(f,n,x)
    while not (fx == 0 or fx*eval_seq_as_poly(f,n,x+eps) < 0 or
                          fx*eval_seq_as_poly(f,n,x-eps) < 0):
        dx = eval_seq_as_poly(f,n,x)/eval_seq_as_poly(df,n-1,x)
        x -= dx
        fx = eval_seq_as_poly(f,n,x)
    return x

cdef newton_in_intervals(int *f, int *df, int n, double *beta,
                         double eps, double *rts):
    r"""
    Find the real roots of f in the intervals specified by beta:
        (beta[0],beta[1]), (beta[1],beta[2]), ..., (beta[n-1], beta[n])
    Calls newton_kernel, so same provisos apply---in particular,
    each interval should contain a unique simple root.
    Note the derivative *df is passed but is recomputed--this is
    just a way to save a malloc and free for each call.
    """

    for i from 0 <= i < n:
        df[i] = f[i+1]*(i+1)
    for i from 0 <= i < n:
        rts[i] = newton(f, df, n, (beta[i]+beta[i+1])/2, eps)

def __lagrange_degree_3(n, an1, an2, an3):
    r"""
    Private function.  Solves the equations which arise in the Lagrange multiplier
    for degree 3: for each 1 <= r <= n-2, we solve
        r*x^i + (n-1-r)*y^i + z^i = s_i (i = 1,2,3)
    where the s_i are the power sums determined by the coefficients a.
    We output the largest value of z which occurs.
    We use a precomputed elimination ideal.
    """

    # Newton's relations.
    s1 = -an1
    s2 = -(an1*s1 + 2*an2)
    s3 = -(an1*s2 + an2*s1 + 3*an3)

    z4minmax = []

    for r from 1 <= r <= n-2:
        nr = n-1-r
        # Note: coefficients of elimination polynomial are in reverse order
        # for numpy, i.e. the coefficient of x^i is p[n-i].
        p = [
             r**3*nr + r**3 + 2*r**2*nr**2 + 5*r**2*nr + 3*r**2 + r*nr**3 + 5*r*nr**2 +
               7*r*nr + 3*r + nr**3 + 3*nr**2 + 3*nr + 1,
             -6*r**2*nr*s1 - 6*r**2*s1 - 6*r*nr**2*s1 - 18*r*nr*s1 - 12*r*s1 - 6*nr**2*s1 -
               12*nr*s1 - 6*s1,
             -3*r**3*s2 - 3*r**2*nr*s2 + 3*r**2*s1**2 - 6*r**2*s2 - 3*r*nr**2*s2 + 15*r*nr*s1**2 -
               6*r*nr*s2 + 18*r*s1**2 - 3*r*s2 - 3*nr**3*s2 + 3*nr**2*s1**2 - 6*nr**2*s2 +
               18*nr*s1**2 - 3*nr*s2 + 15*s1**2,
             -2*r**3*nr*s3 - 4*r**2*nr**2*s3 + 6*r**2*nr*s1*s2 - 6*r**2*nr*s3 + 12*r**2*s1*s2 -
               2*r*nr**3*s3 + 6*r*nr**2*s1*s2 - 6*r*nr**2*s3 - 4*r*nr*s1**3 + 12*r*nr*s1*s2 -
               4*r*nr*s3 - 12*r*s1**3 + 12*r*s1*s2 + 12*nr**2*s1*s2 - 12*nr*s1**3 +
               12*nr*s1*s2 - 20*s1**3,
             3*r**3*s2**2 + 6*r**2*nr*s1*s3 - 3*r**2*nr*s2**2 - 6*r**2*s1**2*s2 + 3*r**2*s2**2 +
               6*r*nr**2*s1*s3 - 3*r*nr**2*s2**2 - 6*r*nr*s1**2*s2 + 12*r*nr*s1*s3 +
               3*r*nr*s2**2 + 3*r*s1**4 - 18*r*s1**2*s2 + 3*nr**3*s2**2 - 6*nr**2*s1**2*s2 +
               3*nr**2*s2**2 + 3*nr*s1**4 - 18*nr*s1**2*s2 + 15*s1**4,
             6*r**2*nr*s2*s3 - 6*r**2*s1*s2**2 + 6*r*nr**2*s2*s3 - 12*r*nr*s1**2*s3 -
               6*r*nr*s1*s2**2 + 12*r*s1**3*s2 - 6*nr**2*s1*s2**2 + 12*nr*s1**3*s2 - 6*s1**5,
             r**3*nr*s3**2 - r**3*s2**3 + 2*r**2*nr**2*s3**2 - 6*r**2*nr*s1*s2*s3 +
               r**2*nr*s2**3 + 3*r**2*s1**2*s2**2 + r*nr**3*s3**2 - 6*r*nr**2*s1*s2*s3 +
               r*nr**2*s2**3 + 4*r*nr*s1**3*s3 + 3*r*nr*s1**2*s2**2 - 3*r*s1**4*s2 -
               nr**3*s2**3 + 3*nr**2*s1**2*s2**2 - 3*nr*s1**4*s2 + s1**6
            ]
        rts = numpy.roots(p)
        rts = numpy.real([rts[i] for i in range(6) if numpy.isreal(rts[i])]).tolist()
        if len(rts) > 0:
            z4minmax = [min(rts + z4minmax), max(rts + z4minmax)]

    return z4minmax

cimport sage.rings.integer

cdef int __len_primes = 46
cdef long primessq[46]
primessq_py = [4, 9, 25, 49, 121, 169, 289, 361, 529, 841, 961, 1369, 1681, 1849, 2209, 2809, 3481, 3721, 4489, 5041, 5329, 6241, 6889, 7921, 9409, 10201, 10609, 11449, 11881, 12769, 16129, 17161, 18769, 19321, 22201, 22801, 24649, 26569, 27889, 29929, 32041, 32761, 36481, 37249, 38809, 39601]
for i from 0 <= i < 46:
    primessq[i] = primessq_py[i]

def int_has_small_square_divisor(sage.rings.integer.Integer d):
    r"""
    Returns the largest a such that a^2 divides d and a has prime divisors < 200.
    """

    cdef int i
    cdef long asq = 1

    for i from 0 <= i < __len_primes:
        while mpz_divisible_ui_p(d.value, primessq[i]):
            asq *= primessq[i]
            mpz_divexact_ui(d.value, d.value, primessq[i])
    return asq

cdef easy_is_irreducible(int *a, int n):
    r"""
    Very often, polynomials have roots in {-2,-1,1,2}, so we rule
    these out quickly.  Returns 0 if reducible, 1 if inconclusive.
    """
    cdef s, sgn

    # Check if x-1 is a factor.
    s = 0
    for i from 0 <= i <= n:
        s += a[i]
    if s == 0:
        return 0

    # Check if x+1 is a factor.
    s = 0
    sgn = 1
    for i from 0 <= i <= n:
        s += sgn*a[i]
        sgn *= -1
    if s == 0:
        return 0

    # Check if x-2 is a factor.
    s = 0
    for i from 0 <= i <= n:
        s += (2**i)*a[i]
    if s == 0:
        return 0

    # Check if x+2 is a factor.
    s = 0
    sgn = 1
    for i from 0 <= i <= n:
        s += sgn*(2**i)*a[i]
        sgn *= -1
    if s == 0:
        return 0

    return 1


#***********************************************************************************************
# Main class and routine
#***********************************************************************************************

# Global precision to find roots; this should probably depend on the
# architecture in some way.  Algorithm gives provably correct results
# for any eps, but an optimal value of eps will be neither too large
# (which gives trivial bounds on coefficients) nor too small (which
# spends needless time computing higher precision on the roots).
eps_global = 10.**(-4)

# Other global variables
ZZx = PolynomialRing(IntegerRing(), 'x')

cdef class tr_data:
    r"""
    This class encodes the data used in the enumeration of totally real
    fields.

    We do not give a complete description here.  For more information,
    see the attached functions; all of these are used internally by the
    functions in totallyreal.py, so see that file for examples and
    further documentation.
    """

    cdef int n, k
    cdef double B
    cdef double b_lower, b_upper, gamma

    cdef int *a, *amax
    cdef double *beta
    cdef int *gnk

    cdef int *df

    def __init__(self, n, B, a=[]):
        r"""
        Initialization routine (constructor).

        INPUT:
        n -- integer, the degree
        B -- integer, the discriminant bound
        a -- list (default: []), the coefficient list to begin with, where
             a[len(a)]*x^n + ... + a[0]x^(n-len(a))

        OUTPUT:
        the data initialized to begin enumeration of totally real fields
        with degree n, discriminant bounded by B, and starting with
        coefficients a.
        """

        cdef int i

        # Initialize constants.
        self.n = n
        self.B = B
        self.gamma = hermite_constant(n-1)

        # Declare the coefficients of the polynomials (and max such).
        self.a = <int*>sage_malloc(sizeof(int)*(n+1))
        self.amax = <int*>sage_malloc(sizeof(int)*(n+1))

        # beta is an array of arrays (of length n) which list the
        # roots of the derivatives.
        self.beta = <double*>sage_malloc(sizeof(double)*n*(n+1))
        # gnk is the collection of (normalized) derivatives.
        self.gnk = <int*>sage_malloc(sizeof(int)*(n+1)*n)

        # df is memory set aside for the derivative, as
        # used in Newton iteration above.
        self.df = <int*>sage_malloc(sizeof(int)*(n+1))

        # Initialize variables.
        if a == []:
            # No starting input, all polynomials will be found; initalize to zero.
            a = [0]*n + [1]
            for i from 0 <= i < n+1:
                self.a[i] = a[i]
                self.amax[i] = a[i]
            self.a[n-1] = -(n/2)
            self.amax[n-1] = 0
            self.k = n-2
        elif len(a) <= n+1:
            # First few coefficients have been specified.
            # The value of k is the largest index of the coefficients of a which is
            # currently unknown; e.g., if k == -1, then we can iterate
            # over polynomials, and if k == n-1, then we have finished iterating.
            if a[len(a)-1] <> 1:
                raise ValueError, "a[len(a)-1](=%s) must be 1 so polynomial is monic"%a[len(a)-1]

            k = n-len(a)
            self.k = k
            a = [0]*(k+1) + a
            for i from 0 <= i < n+1:
                self.a[i] = a[i]
                self.amax[i] = a[i]

            # Bounds come from an application of Lagrange multipliers in degrees 2,3.
            if k == n-2:
                self.b_lower = 1./n*(-self.a[n-1] -
                                 (n-1)*sqrt((1.*self.a[n-1])**2 - 2.*(1-1./n)*self.a[n-2]))
                self.b_upper = -(2.*self.a[n-1]/n + self.b_lower)
            else:
                bminmax = __lagrange_degree_3(n,a[n-1],a[n-2],a[n-3])
                self.b_lower = bminmax[0]
                self.b_upper = bminmax[1]

            # Annoying, but must reverse coefficients for numpy.
            gnk = [binomial(j,k+2)*a[j] for j in range(k+2,n+1)]
            gnk.reverse()
            rts = numpy.roots(gnk).tolist()
            rts.sort()
            self.beta[(k+1)*(n+1)+0] = self.b_lower
            for i from 0 <= i < n-k-2:
                self.beta[(k+1)*(n+1)+(i+1)] = rts[i]
            self.beta[(k+1)*(n+1)+(n-k-1)] = self.b_upper

            # Now to really initialize gnk.
            gnk = [0] + [binomial(j,k+1)*a[j] for j in range (k+2,n+1)]
            for i from 0 <= i < n-k:
                self.gnk[(k+1)*n+i] = gnk[i]
        else:
            # Bad input!
            raise ValueError, "a has length %s > n+1"%len(a)

    def __dealloc__(self):
        r"""
        Destructor.
        """
        sage_free(self.df)
        sage_free(self.a)
        sage_free(self.amax)
        sage_free(self.beta)
        sage_free(self.gnk)

    def incr(self, f_out, verbose=False, haltk=0):
        r"""
        This function 'increments' the totally real data to the next value
        which satisfies the bounds essentially given by Rolle's theorem,
        and returns the next polynomial in the sequence f_out.

        The default or usual case just increments the constant coefficient; then
        inductively, if this is outside of the bounds we increment the next
        higher coefficient, and so on.

        If there are no more coefficients to be had, returns the zero polynomial.

        INPUT:
        f_out -- an integer sequence, to be written with the
            coefficients of the next polynomial
        verbose -- boolean to print verbosely computational details
        haltk -- integer, the level at which to halt the inductive
            coefficient bounds

        OUTPUT:
        the successor polynomial as a coefficient list.
        """

        cdef int n, np1, k, i, j
        cdef int *gnkm, *gnkm1
        cdef double *betak
        cdef int maxoutflag

        n = self.n
        np1 = n+1
        k = self.k

        # If k == -1, we have a full polynomial, so we add 1 to the constant coefficient.
        if k == -1:
            self.a[0] += 1
            # Can't have constant coefficient zero!
            if self.a[0] == 0:
                self.a[0] += 1
            if self.a[0] <= self.amax[0] and easy_is_irreducible(self.a, n):
                for i from 0 <= i < n:
                    f_out[i] = self.a[i]
                return
            else:
                if verbose:
                    print " ",
                    for i from 0 <= i < np1:
                        print self.a[i],
                    print ">",
                    for i from 0 <= i < np1:
                        print self.amax[i],
                    print ""

                # Already reached maximum, so "carry the 1" to find the next value of k.
                k += 1
                while k <= n-1 and self.a[k] >= self.amax[k]:
                    k += 1
                self.a[k] += 1
                self.gnk[n*k] = 0
                k -= 1
        # If we are working through an initialization routine, treat that.
        elif haltk and k == haltk-1:
            self.a[k] += 1
            if self.a[k] > self.amax[k]:
                k += 1
                while k <= n-1 and self.a[k] >= self.amax[k]:
                    k += 1
                self.a[k] += 1
                self.gnk[n*k] = 0
                k -= 1

        # If in the previous step we finished all possible values of
        # the lastmost coefficient, so we must compute bounds on the next coefficient.
        # Recall k == n-1 implies iteration is complete.
        while k < n-1:
            # maxoutflag flags a required abort along the way
            maxoutflag = 0;

            # Recall k == -1 means all coefficients are good to go.
            while k >= 0 and (not haltk or k >= haltk):
                if verbose:
                    print k, ":",
                    for i from 0 <= i < np1:
                        print self.a[i],
                    print ""

                if k == n-2:
                    # We only know the value of a[n-1], the trace.  Need to apply
                    # basic bounds from Hunter's theorem and Siegel's theorem, with
                    # improvements due to Smyth to get bounds on a[n-2].
                    bl = 1./2*(1-1./n)*(1.*self.a[n-1])**2 \
                         - 1./2*self.gamma*(1./n*self.B)**(1./(n-1))
                    self.a[k] = math.ceil(bl)
                    br = 1./2*(1.*self.a[n-1])**2 - 0.88595*n
                    self.amax[k] = math.floor(br)

                    # If maximum is already greater than the minimum, break!
                    if self.a[k] > self.amax[k]:
                        if verbose:
                            print " ",
                            for i from 0 <= i < np1:
                                print self.a[i],
                            print ">",
                            for i from 0 <= i < np1:
                                print self.amax[i],
                            print ""
                        maxoutflag = 1
                        break

                    # Initialize the second derivative.
                    self.b_lower = 1./n*(-self.a[n-1] -
                                     (n-1)*sqrt((1.*self.a[n-1])**2 - 2.*(1+1./(n-1))*self.a[n-2]))
                    self.b_upper = -(2.*self.a[n-1]/n + self.b_lower)
                    self.beta[k*np1+0] = self.b_lower
                    self.beta[k*np1+1] = -self.a[n-1]*1./n
                    self.beta[k*np1+2] = self.b_upper
                    self.gnk[k*n+0] = 0
                    self.gnk[k*n+1] = (n-1)*self.a[n-1]
                    self.gnk[k*n+2] = n*(n-1)/2

                    if verbose:
                        print " ", '%.2f'%self.beta[k*np1+1]
                else:
                    # Compute the roots of the derivative.
                    self.gnk[(k+1)*n+0] += self.a[k+1]
                    newton_in_intervals(&self.gnk[(k+1)*n], self.df, n-(k+1),
                                        &self.beta[(k+1)*np1],
                                        eps_global, &self.beta[k*np1+1])
                    if verbose:
                        print " ",
                        for i from 0 <= i < n-k-1:
                             print '%.2f'%self.beta[k*np1+1+i],
                        print ""

                    # Check for double roots
                    for i from 0 <= i < n-k-1:
                        if abs(self.beta[k*np1+i]
                                 - self.beta[k*np1+(i+1)]) < 2*eps_global:
                            # This happens reasonably infrequently, so calling
                            # the Python routine should be sufficiently fast...
                            f = ZZx([self.gnk[(k+1)*n+i] for i in range(n-(k+1)+1)])
                            df = ZZx([self.gnk[(k+2)*n+i] for i in range(n-(k+2)+1)])
                            if gcd(f,df) <> 1:
                                if verbose:
                                    print "  gnk has multiple factor!"
                                maxoutflag = 1
                                break
                    if maxoutflag:
                        break

                    if k == n-3:
                        # Knowing a[n-1] and a[n-2] means we can apply bounds from
                        # the Lagrange multiplier in degree 2, which can be solved
                        # immediately.
                        self.b_lower = 1./n*(-self.a[n-1] -
                                         (n-1)*sqrt((1.*self.a[n-1])**2 - 2.*(1-1./n)*self.a[n-2]))
                        self.b_upper = -(2.*self.a[n-1]/n + self.b_lower)
                    elif k == n-4:
                        # New bounds from Lagrange multiplier in degree 3.
                        bminmax = __lagrange_degree_3(n,self.a[n-1],self.a[n-2],self.a[n-3])
                        self.b_lower = bminmax[0]
                        self.b_upper = bminmax[1]

                    if verbose:
                        print "  [LM bounds:", '%.2f'%self.b_lower, '%.2f'%self.b_upper,
                        tb = sqrt((1.*self.a[n-1])**2 - 2.*self.a[n-2])
                        print "vs. +/-", '%.2f'%tb, ']'

                    self.beta[k*np1+0] = self.b_lower
                    self.beta[k*np1+n-k] = self.b_upper

                    # Compute next g_(n-(k+1)), k times the formal integral of g_(n-k).
                    gnkm = &self.gnk[k*n]
                    gnkm1 = &self.gnk[(k+1)*n]
                    gnkm[0] = 0
                    for i from 1 <= i < n-k+1:
                        gnkm[i] = gnkm[n+i-1]*(k+1)/i
                    nk = n-(k+1)

                    # Compute upper and lower bounds which guarantee one retains
                    # a polynomial with all real roots.
                    betak = &self.beta[k*np1]
                    akmin = -eval_seq_as_poly(gnkm, n-k, betak[nk+1]) \
                            -abs(eval_seq_as_poly(gnkm1, nk, betak[nk+1]))*eps_global
                    for i from 1 <= i < (nk+1)/2+1:
                        # Use the fact that f(z) <= f(x)+|f'(x)|eps if |x-z| < eps
                        # for sufficiently small eps, f(z) = 0, and f''(z) < 0.
                        akmin = max(akmin,
                                    -eval_seq_as_poly(gnkm, n-k, betak[nk+1-2*i]) \
                                    -abs(eval_seq_as_poly(gnkm1, nk, betak[nk+1-2*i]))*eps_global)

                    akmax = -eval_seq_as_poly(gnkm, n-k, betak[nk]) \
                            +abs(eval_seq_as_poly(gnkm1, n-(k+1), betak[nk]))*eps_global
                    for i from 1 <= i < nk/2+1:
                        # Similar calculus statement here.
                        akmax = min(akmax,
                                    -eval_seq_as_poly(gnkm, n-k, betak[nk-2*i]) \
                                    +abs(eval_seq_as_poly(gnkm1, nk, betak[nk-2*i]))*eps_global)

                    self.a[k] = math.ceil(akmin)
                    self.amax[k] = math.floor(akmax)

                    if self.a[n-1] == 0 and (n-k)%2 == 1:
                        # Can replace alpha by -alpha, so if all
                        # "odd" coefficients are zero, may assume next
                        # "odd" coefficient is positive.
                        kz = n-3
                        while kz > k and self.a[kz] == 0:
                            kz -= 2
                        if kz == k:
                            self.a[k] = max(self.a[k],0)
                    if self.a[k] == 0 and self.a[k+1] == 0:
                        self.a[k] += 1
                    # Can't have constant coefficient zero!
                    if k == 0 and self.a[k] == 0:
                        self.a[k] = 1

                    if self.a[k] > self.amax[k]:
                        if verbose:
                            print " ",
                            for i from 0 <= i < np1:
                                print self.a[i],
                            print ">",
                            for i from 0 <= i < np1:
                                print self.amax[i],
                            print ""
                        maxoutflag = 1
                        break

                self.k -= 1
                k -= 1

            if not maxoutflag and easy_is_irreducible(self.a, n):
                self.k = k
                for i from 0 <= i < n:
                    f_out[i] = self.a[i]
                return
            else:
                k += 1
                while k <= n-1 and self.a[k] >= self.amax[k]:
                    k += 1
                self.a[k] += 1
                self.gnk[n*k] = 0
                k -= 1

        # k == n-1, so iteration is complete; return the zero polynomial (of degree n+1).
        self.k = k
        f_out[n] = 0
        return

    def printa(self):
        print "k =", self.k
        print "a =", [self.a[i] for i in range(self.n+1)]
        print "amax =", [self.amax[i] for i in range(self.n+1)]
        print "beta = ", [self.beta[i] for i in range(self.n*(self.n+1))]
        print "gnk = ", [self.gnk[i] for i in range(self.n*(self.n+1))]
