"""
Isolate Complex Roots of Polynomials

AUTHOR:
    -- Carl Witty (2007-11-18): initial version

This is an implementation of complex root isolation.  That is, given a
polynomial with exact complex coefficients, we compute isolating
intervals for the complex roots of the polynomial.  (Polynomials with
integer, rational, Gaussian rational, or algebraic coefficients are
supported.)

We use a simple algorithm.  First, we compute a squarefree decomposition
of the input polynomial; the resulting polynomials have no multiple roots.
Then, we find the roots numerically, using numpy (at low precision) or
Pari (at high precision).  Then, we verify the roots using interval
arithmetic.

EXAMPLES:
    sage: x = polygen(ZZ)
    sage: (x^5 - x - 1).roots(ring=CIF)
    [([1.1673039782614185 .. 1.1673039782614188], 1), ([0.18123244446987518 .. 0.18123244446987558] + [1.0839541013177103 .. 1.0839541013177110]*I, 1), ([0.181232444469875... .. 0.1812324444698755...] - [1.083954101317710... .. 1.0839541013177110]*I, 1), ([-0.76488443360058489 .. -0.76488443360058455] + [0.35247154603172609 .. 0.35247154603172643]*I, 1), ([-0.76488443360058489 .. -0.76488443360058455] - [0.35247154603172609 .. 0.35247154603172643]*I, 1)]
"""

from copy import copy

from sage.rings.complex_field import ComplexField
from sage.rings.complex_interval_field import ComplexIntervalField

def refine_root(ip, ipd, irt, fld):
    """
    We are given a polynomial and its derivative (with complex
    interval coefficients), an estimated root, and a complex interval
    field to use in computations.  We use interval arithmetic to
    refine the root and prove that we have in fact isolated a unique
    root.

    If we succeed, we return the isolated root; if we fail, we return
    None.

    EXAMPLES:
        sage: from sage.rings.polynomial.complex_roots import *
        sage: x = polygen(ZZ)
        sage: p = x^9 - 1
        sage: ip = CIF['x'](p); ip
        [1.0000000000000000 .. 1.0000000000000000]*x^9 + [-1.0000000000000000 .. -1.0000000000000000]
        sage: ipd = CIF['x'](p.derivative()); ipd
        [9.0000000000000000 .. 9.0000000000000000]*x^8
        sage: irt = CIF(CC(cos(2*pi/9), sin(2*pi/9))); irt
        [0.76604444311897801 .. 0.76604444311897802] + [0.64278760968653925 .. 0.64278760968653926]*I
        sage: ip(irt)
        [-0.0000000000000013322676295501879 .. 0.00000000000000066613381477509393] + [-0.0000000000000012212453270876722 .. 0.00000000000000066613381477509393]*I
        sage: ipd(irt)
        [6.8943999880707931 .. 6.8943999880708056] - [5.7850884871788474 .. 5.7850884871788600]*I
        sage: refine_root(ip, ipd, irt, CIF)
        [0.76604444311897779 .. 0.76604444311897824] + [0.64278760968653914 .. 0.64278760968653948]*I
    """

    # There has got to be a better way to do this, but I don't know
    # what it is...

    # We start with a basic fact: if we do an interval Newton-Raphson
    # step, and the refined interval is contained in the original interval,
    # then the refined interval contains exactly one root.

    # Unfortunately, our initial estimated root almost certainly does not
    # contain the actual root (our initial interval is a point, which
    # is exactly equal to whatever floating-point estimate we got from
    # the external solver).  So we need to do multiple Newton-Raphson
    # steps, and check this inclusion property on each step.

    # After a few steps of refinement, if the initial root estimate was
    # close to a root, we should have an essentially perfect interval
    # bound on the root (since Newton-Raphson has quadratic convergence),
    # unless either the real or imaginary component of the root is zero.
    # If the real or imaginary component is zero, then we could spend
    # a long time computing closer and closer approximations to that
    # component.  (This doesn't happen for non-zero components, because
    # of the imprecision of floating-point numbers combined with the
    # outward interval rounding; but close to zero, MPFI provides
    # extremely precise numbers.)

    # If the root is actually a real root, but we start with an imaginary
    # component, we can bounce back and forth between having a positive
    # and negative imaginary component, without ever hitting zero.
    # To deal with this, on every other Newton-Raphson step, instead of
    # replacing the old interval with the new one, we take the union.

    # If the containment check continues to fail many times in a row,
    # we give up and return None; we also return None if we detect
    # that the slope in our current interval is not bounded away
    # from zero at any step.

    # After every refinement step, we check to see if the real or
    # imaginary component of our interval includes zero.  If so, we
    # try setting it to exactly zero.  This gives us a good chance of
    # detecting real roots.  However, we do this replacement at most
    # once per component.

    refinement_steps = 10

    smashed_real = False
    smashed_imag = False

    for i in range(refinement_steps):
        slope = ipd(irt)
        if slope.contains_zero():
            return None
        center = fld(irt.center())
        val = ip(center)

        nirt = center - val / slope
        if nirt in irt and nirt.diameter() >= irt.diameter() >> 1:
            # If the new diameter is much less than the original diameter,
            # then we have not yet converged.  (Perhaps we were asked
            # for a particularly high-precision result.)  So we don't
            # return yet.
            return nirt

        if i & 1:
            irt = nirt
        else:
            irt = irt.union(nirt)

        if not smashed_real and irt.real().contains_zero():
            irt = irt.parent()(0, irt.imag())
        if not smashed_imag and irt.imag().contains_zero():
            irt = irt.parent()(irt.real(), 0)

    return None

def interval_roots(p, rts, prec):
    """
    We are given a squarefree polynomial p, a list of estimated roots,
    and a precision.

    We attempt to verify that the estimated roots are in fact distinct
    roots of the polynomial, using interval arithmetic of precision prec.
    If we succeed, we return a list of intervals bounding the roots; if we
    fail, we return None.

    EXAMPLES:
        sage: x = polygen(ZZ)
        sage: p = x^3 - 1
        sage: rts = [CC.zeta(3)^i for i in range(0, 3)]
        sage: from sage.rings.polynomial.complex_roots import interval_roots
        sage: interval_roots(p, rts, 53)
        [[1.0000000000000000 .. 1.0000000000000000], [-0.50000000000000012 .. -0.49999999999999983] + [0.86602540378443848 .. 0.86602540378443882]*I, [-0.50000000000000012 .. -0.49999999999999988] - [0.86602540378443848 .. 0.86602540378443882]*I]
        sage: interval_roots(p, rts, 200)
        [[1.0000000000000000000000000000000000000000000000000000000000000 .. 1.0000000000000000000000000000000000000000000000000000000000000], [-0.50000000000000000000000000000000000000000000000000000000000063 .. -0.49999999999999999999999999999999999999999999999999999999999968] + [0.86602540378443864676372317075293618347140262690519031402790313 .. 0.86602540378443864676372317075293618347140262690519031402790377]*I, [-0.50000000000000000000000000000000000000000000000000000000000063 .. -0.49999999999999999999999999999999999999999999999999999999999968] - [0.86602540378443864676372317075293618347140262690519031402790313 .. 0.86602540378443864676372317075293618347140262690519031402790377]*I]
    """

    CIF = ComplexIntervalField(prec)
    CIFX = CIF['x']

    ip = CIFX(p)
    ipd = CIFX(p.derivative())

    irts = []

    for rt in rts:
        irt = refine_root(ip, ipd, CIF(rt), CIF)
        if irt is None:
            return None
        irts.append(irt)

    return irts

def intervals_disjoint(intvs):
    """
    Given a list of complex intervals, check whether they are pairwise
    disjoint.

    EXAMPLES:
        sage: from sage.rings.polynomial.complex_roots import intervals_disjoint
        sage: a = CIF(RIF(0, 3), 0)
        sage: b = CIF(0, RIF(1, 3))
        sage: c = CIF(RIF(1, 2), RIF(1, 2))
        sage: d = CIF(RIF(2, 3), RIF(2, 3))
        sage: intervals_disjoint([a,b,c,d])
        False
        sage: d2 = CIF(RIF(2, 3), RIF(2.001, 3))
        sage: intervals_disjoint([a,b,c,d2])
        True
    """

    # This may be quadratic in perverse cases, but will take only
    # n log(n) time in typical cases.

    intvs = copy(intvs)
    intvs.sort()

    column = []
    prev_real = None

    def column_disjoint():
        column.sort()

        row = []
        prev_imag = None

        def row_disjoint():
            for a in range(len(row)):
                for b in range(a+1, len(row)):
                    if row[a].overlaps(row[b]):
                        return False
            return True

        for (y_imag, y) in column:
            if prev_imag is not None and y_imag > prev_imag:
                if not row_disjoint(): return False
                row = []
            prev_imag = y_imag
            row.append(y)
        if not row_disjoint(): return False
        return True

    for x in intvs:
        x_real = x.real()
        if prev_real is not None and x_real > prev_real:
            if not column_disjoint(): return False
            column = []
        prev_real = x_real
        column.append((x.imag(), x))

    if not column_disjoint(): return False
    return True



def complex_roots(p, skip_squarefree=False, retval='interval', min_prec=0):
    """
    Compute the complex roots of a given polynomial with exact
    coefficients (integer, rational, Gaussian rational, and algebraic
    coefficients are supported).  Returns a list of pairs of a root
    and its multiplicity.

    Roots are returned as a ComplexIntervalFieldElement; each interval
    includes exactly one root, and the intervals are disjoint.

    By default, the algorithm will do a squarefree decomposition
    to get squarefree polynomials.  The skip_squarefree parameter
    lets you skip this step.  (If this step is skipped, and the polynomial
    has a repeated root, then the algorithm will loop forever!)

    EXAMPLES:
        sage: from sage.rings.polynomial.complex_roots import complex_roots
        sage: x = polygen(ZZ)
        sage: complex_roots(x^5 - x - 1)
        [([1.1673039782614185 .. 1.1673039782614188], 1), ([0.18123244446987518 .. 0.18123244446987558] + [1.0839541013177103 .. 1.0839541013177110]*I, 1), ([0.181232444469875... .. 0.1812324444698755...] - [1.083954101317710... .. 1.0839541013177110]*I, 1), ([-0.76488443360058489 .. -0.76488443360058455] + [0.35247154603172609 .. 0.35247154603172643]*I, 1), ([-0.76488443360058489 .. -0.76488443360058455] - [0.35247154603172609 .. 0.35247154603172643]*I, 1)]

        sage: K.<im> = NumberField(x^2 + 1)
        sage: eps = 1/2^100
        sage: x = polygen(K)
        sage: p = (x-1)*(x-1-eps)*(x-1+eps)*(x-1-eps*im)*(x-1+eps*im)

    This polynomial actually has all-real coefficients, and is very, very
    close to (x-1)^5:
        sage: [RR(QQ(x)) for x in list(p - (x-1)^5)]
        [3.87259191484932e-121, -3.87259191484932e-121]
        sage: rts = complex_roots(p)
        sage: [ComplexIntervalField(10)(rt[0] - 1) for rt in rts]
        [0, [7.8886e-31 .. 7.8887e-31]*I, [7.8886e-31 .. 7.8887e-31], [-7.8887e-31 .. -7.8886e-31]*I, [-7.8887e-31 .. -7.8886e-31]]
    """

    if skip_squarefree:
        factors = [(p, 1)]
    else:
        factors = p.squarefree_decomposition()

    prec = 53
    while True:
        CC = ComplexField(prec)
        CCX = CC['x']

        all_rts = []
        ok = True

        for (factor, exp) in factors:
            cfac = CCX(factor)
            rts = cfac.roots(multiplicities=False)
            irts = interval_roots(factor, rts, max(prec, min_prec))
            if irts is None:
                ok = False
                break
            for irt in irts:
                all_rts.append((irt, exp))

        if ok and intervals_disjoint([rt for (rt, mult) in all_rts]):
            return all_rts

        prec = prec * 2
