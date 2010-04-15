"""
The Victor Miller Basis
"""

#########################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#########################################################################

import math

from sage.matrix.all import MatrixSpace, Matrix
from sage.rings.all import QQ, ZZ, Integer, binomial, PowerSeriesRing, O as bigO
from sage.structure.all import Sequence
from sage.libs.flint.fmpz_poly import Fmpz_poly
from sage.misc.all import verbose
from sage.rings.power_series_ring import PowerSeriesRing

from eis_series_cython import eisenstein_series_poly

def victor_miller_basis(k, prec=10, cusp_only=False, var='q'):
    r"""
    Compute and return the Victor-Miller basis for modular forms of
    weight k and level 1 to precision `O(q^{prec})`.  If
    ``cusp_only`` is True, return only a basis for the cuspidal
    subspace.

    INPUT:

    - ``k`` -- an integer

    - ``prec`` -- (default: 10) a positive integer

    - ``cusp_only`` -- bool (default: False)

    - ``var`` -- string (default: 'q'

    OUTPUT:
        A sequence whose entries are power series in ZZ[[var]].

    EXAMPLES::

        sage: victor_miller_basis(1, 6)
        []
        sage: victor_miller_basis(0, 6)
        [
        1 + O(q^6)
        ]
        sage: victor_miller_basis(2, 6)
        []
        sage: victor_miller_basis(4, 6)
        [1 + 240*q + 2160*q^2 + 6720*q^3 + 17520*q^4 + 30240*q^5 + O(q^6)]

        sage: victor_miller_basis(6, 6, var='w')
        [1 - 504*w - 16632*w^2 - 122976*w^3 - 532728*w^4 - 1575504*w^5 + O(w^6)]

        sage: victor_miller_basis(6, 6)
        [1 - 504*q - 16632*q^2 - 122976*q^3 - 532728*q^4 - 1575504*q^5 + O(q^6)]
        sage: victor_miller_basis(12, 6)
        [1 + 196560*q^2 + 16773120*q^3 + 398034000*q^4 + 4629381120*q^5 + O(q^6), q - 24*q^2 + 252*q^3 - 1472*q^4 + 4830*q^5 + O(q^6)]

        sage: victor_miller_basis(12, 6, cusp_only=True)
        [q - 24*q^2 + 252*q^3 - 1472*q^4 + 4830*q^5 + O(q^6)]
        sage: victor_miller_basis(24, 6, cusp_only=True)
        [q + 195660*q^3 + 12080128*q^4 + 44656110*q^5 + O(q^6), q^2 - 48*q^3 + 1080*q^4 - 15040*q^5 + O(q^6)]
        sage: victor_miller_basis(24, 6)
        [1 + 52416000*q^3 + 39007332000*q^4 + 6609020221440*q^5 + O(q^6), q + 195660*q^3 + 12080128*q^4 + 44656110*q^5 + O(q^6), q^2 - 48*q^3 + 1080*q^4 - 15040*q^5 + O(q^6)]
        sage: victor_miller_basis(32, 6)
        [1 + 2611200*q^3 + 19524758400*q^4 + 19715347537920*q^5 + O(q^6), q + 50220*q^3 + 87866368*q^4 + 18647219790*q^5 + O(q^6), q^2 + 432*q^3 + 39960*q^4 - 1418560*q^5 + O(q^6)]

        sage: victor_miller_basis(40,200)[1:] == victor_miller_basis(40,200,cusp_only=True)
        True
        sage: victor_miller_basis(200,40)[1:] == victor_miller_basis(200,40,cusp_only=True)
        True

    AUTHORS :
    - ??? : Original code

    - Martin Raum (2009-08-02) : Use FLINT, eisenstein_series_list and delta_list
    """
    k = Integer(k)
    if k%2 == 1 or k==2:
        return Sequence([])
    elif k < 0:
        raise ValueError, "k must be non-negative"
    elif k == 0:
        return Sequence([PowerSeriesRing(ZZ,var)(1).add_bigoh(prec)], cr=True)
    e = k.mod(12)
    if e == 2: e += 12
    n = (k-e) // 12

    if n == 0 and cusp_only:
        return Sequence([])

    # If prec is less than or equal to the dimension of the space of
    # cusp forms, which is just n, then we know the answer, and we
    # simply return it.
    if prec <= n:
        q = PowerSeriesRing(ZZ,var).gen(0)
        err = bigO(q**prec)
        ls = [0] * (n+1)
        if not cusp_only:
            ls[0] = 1 + err
        for i in range(1,prec):
            ls[i] = q**i + err
        for i in range(prec,n+1):
            ls[i] = err
        return Sequence(ls, cr=True)

    F6 = eisenstein_series_poly(6,prec)

    if e == 0:
        A = Fmpz_poly(1)
    elif e == 4:
        A = eisenstein_series_poly(4,prec)
    elif e == 6:
        A = F6
    elif e == 8:
        A = eisenstein_series_poly(8,prec)
    elif e == 10:
        A = eisenstein_series_poly(10,prec)
    else: # e == 14
        A = eisenstein_series_poly(14,prec)

    if A[0] == -1 :
        A = -A

    if n == 0:
        return [PowerSeriesRing(ZZ,var)(A.list()).add_bigoh(prec)]

    F6_squared = F6**2
    F6_squared._unsafe_mutate_truncate(prec)
    D = delta_poly(prec)
    Fprod = F6_squared
    Dprod = D

    if cusp_only:
        ls = [Fmpz_poly(0)] + [A] * n
    else:
        ls = [A] * (n+1)

    for i in xrange(1,n+1):
        ls[n-i] *= Fprod
        ls[i] *= Dprod
        ls[n-i]._unsafe_mutate_truncate(prec)
        ls[i]._unsafe_mutate_truncate(prec)

        Fprod *= F6_squared
        Dprod *= D
        Fprod._unsafe_mutate_truncate(prec)
        Dprod._unsafe_mutate_truncate(prec)


    P = PowerSeriesRing(ZZ,var)
    if cusp_only :
        for i in xrange(1,n+1) :
            for j in xrange(1, i) :
                ls[j] = ls[j] - ls[j][i]*ls[i]

        return map(lambda l: P(l.list()).add_bigoh(prec), ls[1:])
    else :
        for i in xrange(1,n+1) :
            for j in xrange(i) :
                ls[j] = ls[j] - ls[j][i]*ls[i]

        return map(lambda l: P(l.list()).add_bigoh(prec), ls)

def delta_poly(prec=10):
    """
    Return the q-expansion of Delta as a FLINT polynomial.

    INPUT:

    - ``prec`` -- integer; the absolute precision of the output

    OUTPUT:
        a power series over K


    ALGORITHM:
        Compute a simple very explicit modular form whose 8th power
        is Delta.

    EXAMPLES::

        sage: from sage.modular.modform.vm_basis import delta_poly
        sage: delta_poly(7)
        7  0 1 -24 252 -1472 4830 -6048

    AUTHORS:

    - William Stein: original code

    - David Harvey (2007-05): sped up first squaring step
    """
    if prec <= 0:
        raise ValueError, "prec must be positive"
    v = [0] * prec

    # Let F = \sum_{n >= 0} (-1)^n (2n+1) q^(floor(n(n+1)/2)).
    # Then delta is F^8.

    # First compute F^2 directly by naive polynomial multiplication,
    # since F is very sparse.

    stop = int((-1+math.sqrt(1+8*prec))/2.0)
    # make list of index/value pairs for the sparse poly
    values = [(n*(n+1)//2, ((-2*n-1) if (n & 1) else (2*n+1))) \
              for n in xrange(stop+1)]

    for (i1, v1) in values:
        for (i2, v2) in values:
            try:
                v[i1 + i2] += v1 * v2
            except IndexError:
                break

    f = Fmpz_poly(v)
    t = verbose('made series')
    f = f*f
    f._unsafe_mutate_truncate(prec)
    t = verbose('squared (2 of 3)', t)
    f = f*f
    f._unsafe_mutate_truncate(prec - 1)
    t = verbose('squared (3 of 3)', t)
    f = f.left_shift(1)
    t = verbose('shifted', t)

    return f

def delta_qexp(prec=10, var='q', K=ZZ) :
    """
    Return the q-expansion of Delta as a power series with
    coefficients in K (=ZZ by default).

    INPUT:

    - ``prec`` -- integer; the absolute precision of the output

    - ``var`` -- (default: 'q') variable name

    - ``K`` -- (default: ZZ) base ring of answer

    OUTPUT:
        a power series over K


    ALGORITHM:
        Compute a simple very explicit modular form whose 8th power
        is Delta.   Then compute the 8th power using FLINT polynomial
        arithmetic, which is VERY fast.   This function
        computes a *million* terms of Delta in under a minute.

    EXAMPLES::

        sage: delta_qexp(7)
        q - 24*q^2 + 252*q^3 - 1472*q^4 + 4830*q^5 - 6048*q^6 + O(q^7)
        sage: delta_qexp(7,'z')
        z - 24*z^2 + 252*z^3 - 1472*z^4 + 4830*z^5 - 6048*z^6 + O(z^7)
        sage: delta_qexp(-3)
        Traceback (most recent call last):
        ...
        ValueError: prec must be positive

    AUTHORS:

    - William Stein: original code, which is now in delta_poly

    - David Harvey (2007-05): sped up first squaring step
    """
    R = PowerSeriesRing(K, var)
    return R(delta_poly(prec).list(), prec, check=False)
