"""
Common combinatorial tools


REFERENCES:

.. [NCSF] Gelfand, Krob, Lascoux, Leclerc, Retakh, Thibon,
   *Noncommutative Symmetric Functions*, Adv. Math. 112 (1995), no. 2, 218-348.

"""

from sage.misc.misc_c import prod
from sage.functions.other import factorial
from sage.misc.cachefunc import cached_method, cached_function
from sage.combinat.composition import Composition, Compositions

# The following might call for defining a morphism from ``structure
# coefficients'' / matrix using something like:
# Complete.module_morphism( coeff = coeff_pi, codomain=Psi, triangularity="finer" )
# the difficulty is how to best describe the support of the output.

def coeff_pi(J,I):
    r"""
    Returns the coefficient `\pi_{J,I}` as defined in [NCSF]_.

    INPUT:

    - ``J`` -- a composition
    - ``I`` -- a composition refining ``J``

    OUTPUT:

    - integer

    EXAMPLES::

        sage: from sage.combinat.ncsf_qsym.combinatorics import coeff_pi
        sage: coeff_pi(Composition([1,1,1]), Composition([2,1]))
        2
        sage: coeff_pi(Composition([2,1]), Composition([3]))
        6
    """
    return prod(prod(K.partial_sums()) for K in J.refinement_splitting(I))

def coeff_lp(J,I):
    r"""
    Returns the coefficient `lp_{J,I}` as defined in [NCSF]_.

    INPUT:

    - ``J`` -- a composition
    - ``I`` -- a composition refining ``J``

    OUTPUT:

    - integer

    EXAMPLES::

        sage: from sage.combinat.ncsf_qsym.combinatorics import coeff_lp
        sage: coeff_lp(Composition([1,1,1]), Composition([2,1]))
        1
        sage: coeff_lp(Composition([2,1]), Composition([3]))
        1
    """
    return prod(K[-1] for K in J.refinement_splitting(I))

def coeff_ell(J,I):
    r"""
    Returns the coefficient `\ell_{J,I}` as defined in [NCSF]_.

    INPUT:

    - ``J`` -- a composition
    - ``I`` -- a composition refining ``J``

    OUTPUT:

    - integer

    EXAMPLES::

        sage: from sage.combinat.ncsf_qsym.combinatorics import coeff_ell
        sage: coeff_ell(Composition([1,1,1]), Composition([2,1]))
        2
        sage: coeff_ell(Composition([2,1]), Composition([3]))
        2
    """
    return prod(map(len, J.refinement_splitting(I)))

def coeff_sp(J,I):
    r"""
    Returns the coefficient `sp_{J,I}` as defined in [NCSF]_.

    INPUT:

    - ``J`` -- a composition
    - ``I`` -- a composition refining ``J``

    OUTPUT:

    - integer

    EXAMPLES::

        sage: from sage.combinat.ncsf_qsym.combinatorics import coeff_sp
        sage: coeff_sp(Composition([1,1,1]), Composition([2,1]))
        2
        sage: coeff_sp(Composition([2,1]), Composition([3]))
        4
    """
    return prod(factorial(len(K))*prod(K) for K in J.refinement_splitting(I))

def m_to_s_stat(R, I, K):
    r"""
    Returns the statistic for the expansion of the Monomial basis element indexed by two
    compositions, as in formula (36) of Tevlin's "Noncommutative Analogs of Monomial Symmetric
    Functions, Cauchy Identity, and Hall Scalar Product".

    INPUT:

    - ``R`` -- A ring
    - ``I``, ``K`` -- compositions

    OUTPUT:

    - An integer

    EXAMPLES::

        sage: from sage.combinat.ncsf_qsym.combinatorics import m_to_s_stat
        sage: m_to_s_stat(QQ,Composition([2,1]), Composition([1,1,1]))
        -1
        sage: m_to_s_stat(QQ,Composition([3]), Composition([1,2]))
        -2
    """
    stat = 0
    for J in Compositions(I.size()):
        if (I.is_finer(J) and  K.is_finer(J)):
            pvec = [0] + Composition(I).refinement_splitting_lengths(J).partial_sums()
            pp = prod( R( len(I) - pvec[i] ) for i in range( len(pvec)-1 ) )
            stat += R((-1)**(len(I)-len(K)) / pp * coeff_lp(K,J))
    return stat

@cached_function
def number_of_fCT(content_comp, shape_comp):
    r"""
    Returns the number of Immaculate tableau of shape ``shape_comp`` and content ``content_comp``.

    INPUT:

    - ``content_comp``, ``shape_comp`` -- compositions

    OUTPUT:

    - An integer

    EXAMPLES::

        sage: from sage.combinat.ncsf_qsym.combinatorics import number_of_fCT
        sage: number_of_fCT(Composition([3,1]), Composition([1,3]))
        0
        sage: number_of_fCT(Composition([1,2,1]), Composition([1,3]))
        1
        sage: number_of_fCT(Composition([1,1,3,1]), Composition([2,1,3]))
        2

    """
    if content_comp.to_partition().length() == 1:
        if shape_comp.to_partition().length() == 1:
            return 1
        else:
            return 0
    C = Compositions(content_comp.size()-content_comp[-1], outer = list(shape_comp))
    s = 0
    for x in C:
        if len(x) >= len(shape_comp)-1:
            s += number_of_fCT(Composition(content_comp[:-1]),x)
    return s
