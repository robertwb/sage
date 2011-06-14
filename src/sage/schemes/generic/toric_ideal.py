r"""
Toric ideals

A toric ideal (associated to an integer matrix `A`) is an ideal of the
form

.. MATH::

    I_A = \left<
        x^u - x^v
        : u,v \in \ZZ_\geq^n
        , u-v \in \ker(A)
        \right>

In other words, it is an ideal generated by irreducible "binomials",
that is, differences of monomials without a common factor. Since the
Buchberger algorithm preserves this property, any Groebner basis is
then also generated by binomials.

EXAMPLES::

    sage: A = matrix([[1,1,1],[0,1,2]])
    sage: IA = ToricIdeal(A)
    sage: IA.ker()
    Free module of degree 3 and rank 1 over Integer Ring
    User basis matrix:
    [ 1 -2  1]
    sage: IA
    Ideal (-z1^2 + z0*z2) of Multivariate Polynomial
    Ring in z0, z1, z2 over Rational Field

Here, the "naive" ideal generated by `z_0 z_2 - z_1^2` does already
equal the toric ideal. But that is not true in general! For example,
this toric ideal ([ProcSympPureMath62], Example 1.2) is the twisted
cubic and cannot be generated by `2=\dim \ker(A)` polynomials::

    sage: A = matrix([[3,2,1,0],[0,1,2,3]])
    sage: IA = ToricIdeal(A)
    sage: IA.ker()
    Free module of degree 4 and rank 2 over Integer Ring
    User basis matrix:
    [ 1 -1 -1  1]
    [ 1 -2  1  0]
    sage: IA
    Ideal (-z1*z2 + z0*z3, -z1^2 + z0*z2, z2^2 - z1*z3) of
    Multivariate Polynomial Ring in z0, z1, z2, z3 over Rational Field

The following family of toric ideals is from Example 4.4 of
[ProcSympPureMath62]_. One can show that `I_d` is generated by one
quadric and `d` binomials of degree `d`::

    sage: I = lambda d: ToricIdeal(matrix([[1,1,1,1,1],[0,1,1,0,0],[0,0,1,1,d]]))
    sage: I(2)
    Ideal (-z3^2 + z0*z4,
           z0*z2 - z1*z3,
           z2*z3 - z1*z4) of
    Multivariate Polynomial Ring in z0, z1, z2, z3, z4 over Rational Field
    sage: I(3)
    Ideal (-z3^3 + z0^2*z4,
           z0*z2 - z1*z3,
           z2*z3^2 - z0*z1*z4,
           z2^2*z3 - z1^2*z4) of
    Multivariate Polynomial Ring in z0, z1, z2, z3, z4 over Rational Field
    sage: I(4)
    Ideal (-z3^4 + z0^3*z4,
           z0*z2 - z1*z3,
           z2*z3^3 - z0^2*z1*z4,
           z2^2*z3^2 - z0*z1^2*z4,
           z2^3*z3 - z1^3*z4) of
    Multivariate Polynomial Ring in z0, z1, z2, z3, z4 over Rational Field

Finally, the example in [GRIN]_ ::

    sage: A = matrix(ZZ, [ [15,  4, 14, 19,  2,  1, 10, 17],
    ...                    [18, 11, 13,  5, 16, 16,  8, 19],
    ...                    [11,  7,  8, 19, 15, 18, 14,  6],
    ...                    [17, 10, 13, 17, 16, 14, 15, 18] ])
    sage: IA = ToricIdeal(A)     # long time
    sage: IA.ngens()             # long time
    213

TESTS::

    sage: A = matrix(ZZ, [[1, 1, 0, 0, -1,  0,  0, -1],
    ...                   [0, 0, 1, 1,  0, -1, -1,  0],
    ...                   [1, 0, 0, 1,  1,  1,  0,  0],
    ...                   [1, 0, 0, 1,  0,  0, -1, -1]])
    sage: IA = ToricIdeal(A)
    sage: R = IA.ring()
    sage: R.inject_variables()
    Defining z0, z1, z2, z3, z4, z5, z6, z7
    sage: IA == R.ideal([z4*z6-z5*z7, z2*z5-z3*z6, -z3*z7+z2*z4,
    ...       -z2*z6+z1*z7, z1*z4-z3*z6, z0*z7-z3*z6, -z1*z5+z0*z6, -z3*z5+z0*z4,
    ...       z0*z2-z1*z3])  # Computed with Maple 12
    True

The next example first appeared in Example 12.7 in [GBCP]_. It is also
used by the Maple 12 help system as example::

    sage: A = matrix(ZZ, [[1, 2, 3, 4, 0, 1, 4, 5],
    ...                   [2, 3, 4, 1, 1, 4, 5, 0],
    ...                   [3, 4, 1, 2, 4, 5, 0, 1],
    ...                   [4, 1, 2, 3, 5, 0, 1, 4]])
    sage: IA = ToricIdeal(A, 'z1, z2, z3, z4, z5, z6, z7, z8')
    sage: R = IA.ring()
    sage: R.inject_variables()
    Defining z1, z2, z3, z4, z5, z6, z7, z8
    sage: IA == R.ideal([z4^4-z6*z8^3, z3^4-z5*z7^3, -z4^3+z2*z8^2,
    ...       z2*z4-z6*z8, -z4^2*z6+z2^2*z8, -z4*z6^2+z2^3, -z3^3+z1*z7^2,
    ...       z1*z3-z5*z7, -z3^2*z5+z1^2*z7, z1^3-z3*z5^2])
    True


REFERENCES:

..  [GRIN]
    Bernd Sturmfels, Serkan Hosten:
    GRIN: An implementation of Grobner bases for integer programming,
    in "Integer Programming and Combinatorial Optimization",
    [E. Balas and J. Clausen, eds.],
    Proceedings of the IV. IPCO Conference (Copenhagen, May 1995),
    Springer Lecture Notes in Computer Science 920 (1995) 267-276.

..  [ProcSympPureMath62]
    Bernd Sturmfels:
    Equations defining toric varieties,
    Algebraic Geometry - Santa Cruz 1995,
    Proc. Sympos. Pure Math., 62, Part 2,
    Amer. Math. Soc., Providence, RI, 1997,
    pp. 437-449.

..  [GBCP]
    Bernd Sturmfels:
    Grobner Bases and Convex Polytopes
    AMS University Lecture Series Vol. 8 (01 December 1995)

AUTHORS:

- Volker Braun (2011-01-03): Initial version
"""

#*****************************************************************************
#       Copyright (C) 2010 Volker Braun <vbraun.name@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

# TODO:
#   * Implement the Di Biase & Urbanke algorithm
#   * Implement the Conti & Traverso algorithm (for educational purposes)
#   * Cythonize the Buchberger algorithm for toric ideals
#   * Use the (multiple) weighted homegeneity during Groebner basis computations



from sage.structure.sage_object import SageObject
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.misc.misc_c import prod
from sage.matrix.constructor import matrix
from sage.rings.all import ZZ, QQ
from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal


class ToricIdeal(MPolynomialIdeal):
    r"""
    This class represents a toric ideal defined by an integral matrix.

    INPUT:

    - ``A`` -- integer matrix. The defining matrix of the toric ideal.

    - ``names`` -- string (optional). Names for the variables. By
      default, this is ``'z'`` and the variables will be named ``z0``,
      ``z1``, ...

    - ``base_ring`` -- a ring (optional). Default: `\QQ`. The base
      ring of the ideal. A toric ideal uses only coefficents `\pm 1`.

    - ``polynomial_ring`` -- a polynomial ring (optional). The
      polynomial ring to construct the ideal in.

      You may specify the ambient polynomial ring via the
      ``polynomial_ring`` parameter or via the ``names`` and
      ``base_ring`` parameter. A ``ValueError`` is raised if you
      specify both.

    - ``algorithm`` -- string (optional). The algorithm to use. For
      now, must be ``'HostenSturmfels'`` which is the algorithm
      proposed by Hosten and Sturmfels in [GRIN].

    EXAMPLES::

        sage: A = matrix([[1,1,1],[0,1,2]])
        sage: ToricIdeal(A)
        Ideal (-z1^2 + z0*z2) of Multivariate Polynomial Ring
        in z0, z1, z2 over Rational Field

    First way of specifying the polynomial ring::

        sage: ToricIdeal(A, names='x,y,z', base_ring=ZZ)
        Ideal (-y^2 + x*z) of Multivariate Polynomial Ring
        in x, y, z over Integer Ring

    Second way of specifying the polynomial ring::

        sage: R.<x,y,z> = ZZ[]
        sage: ToricIdeal(A, polynomial_ring=R)
        Ideal (-y^2 + x*z) of Multivariate Polynomial Ring
        in x, y, z over Integer Ring

    It is an error to specify both::

        sage: ToricIdeal(A, names='x,y,z', polynomial_ring=R)
        Traceback (most recent call last):
        ...
        ValueError: You must not specify both variable names and a polynomial ring.
    """

    def __init__(self, A,
                 names='z', base_ring=QQ,
                 polynomial_ring=None,
                 algorithm='HostenSturmfels'):
        r"""
        Create an ideal and a multivariate polynomial ring containing it.

        See the :mod:`module documentation
        <sage.schemes.generic.toric_ideal>` for an introduction to
        toric ideals.

        INPUT:

        See the :class:`class-level documentation <ToricIdeal>` for
        input values.

        EXAMPLES::

            sage: A = matrix([[1,1,1],[0,1,2]])
            sage: ToricIdeal(A)
            Ideal (-z1^2 + z0*z2) of Multivariate Polynomial Ring
            in z0, z1, z2 over Rational Field
            sage: ToricIdeal(A, names='x', base_ring=GF(101))
            Ideal (-x1^2 + x0*x2) of Multivariate Polynomial Ring
            in x0, x1, x2 over Finite Field of size 101
        """
        self._A = matrix(ZZ, A)
        if polynomial_ring:
            if (names!='z') or (base_ring is not QQ):
                raise ValueError('You must not specify both variable names and a polynomial ring.')
            self._names = map(str, polynomial_ring.gens())
            self._base_ring = polynomial_ring.base_ring()
            ring = polynomial_ring
        else:
            self._names = names
            self._base_ring = base_ring
            ring = self._init_ring('degrevlex')

        if algorithm=='HostenSturmfels':
            ideal = self._ideal_HostenSturmfels()
        else:
            raise ValueError, 'Algorithm = '+str(algorithm)+' is not known!'

        gens = [ ring(x) for x in ideal.gens() ]
        MPolynomialIdeal.__init__(self, ring, gens, coerce=False)

    def A(self):
        """
        Return the defining matrix.

        OUTPUT:

        An integer matrix.

        EXAMPLES::

            sage: A = matrix([[1,1,1],[0,1,2]])
            sage: IA = ToricIdeal(A)
            sage: IA.A()
            [1 1 1]
            [0 1 2]
        """
        return self._A

    def ker(self):
        """
        Return the kernel of the defining matrix.

        OUTPUT:

        The kernel of ``self.A()``.

        EXAMPLES::

            sage: A = matrix([[1,1,1],[0,1,2]])
            sage: IA = ToricIdeal(A)
            sage: IA.ker()
            Free module of degree 3 and rank 1 over Integer Ring
            User basis matrix:
            [ 1 -2  1]
        """

        if '_ker' in self.__dict__:
            return self._ker
        self._ker = self.A().right_kernel(basis='LLL')
        return self._ker

    def nvariables(self):
        r"""
        Return the number of variables of the ambient polynomial ring.

        OUTPUT:

        Integer. The number of columns of the defining matrix
        :meth:`A`.

        EXAMPLES::

            sage: A = matrix([[1,1,1],[0,1,2]])
            sage: IA = ToricIdeal(A)
            sage: IA.nvariables()
            3
        """
        return self.A().ncols()

    def _init_ring(self, term_order):
        r"""
        Construct the ambient polynomial ring.

        INPUT:

        - ``term_order`` -- string. The order of the variables, for
          example ``'neglex'`` and ``'degrevlex'``.

        OUTPUT:

        A polynomial ring with the given term order.

        .. NOTE::

            Reverse lexicographic ordering is equivalent to negative
            lexicographic order with the reversed list of
            variables. We are using the latter in the implementation
            of the Hosten/Sturmfels algorithm.

        EXAMPLES::

            sage: A = matrix([[1,1,1],[0,1,2]])
            sage: IA = ToricIdeal(A)
            sage: R = IA._init_ring('neglex');  R
            Multivariate Polynomial Ring in z0, z1, z2 over Rational Field
            sage: R.term_order()
            Negative lexicographic term order
            sage: R.inject_variables()
            Defining z0, z1, z2
            sage: z0 < z1 and z1 < z2
            True
        """
        return PolynomialRing(self._base_ring, self._names,
                              self.nvariables(), order=term_order)

    def _naive_ideal(self, ring):
        r"""
        Return the "naive" subideal.

        INPUT:

        - ``ring`` -- the ambient ring of the ideal.

        OUTPUT:

        A subideal of the toric ideal in the polynomial ring ``ring``.

        EXAMPLES::

            sage: A = matrix([[1,1,1],[0,1,2]])
            sage: IA = ToricIdeal(A)
            sage: IA.ker()
            Free module of degree 3 and rank 1 over Integer Ring
            User basis matrix:
            [ 1 -2  1]
            sage: IA._naive_ideal(IA.ring())
            Ideal (-z1^2 + z0*z2) of Multivariate Polynomial Ring in z0, z1, z2 over Rational Field
        """
        x = ring.gens()
        binomials = []
        for row in self.ker().matrix().rows():
            xpos = prod(x[i]**max( row[i],0) for i in range(0,len(x)))
            xneg = prod(x[i]**max(-row[i],0) for i in range(0,len(x)))
            binomials.append(xpos - xneg)
        return ring.ideal(binomials)

    def _ideal_quotient_by_variable(self, ring, ideal, n):
        r"""
        Return the ideal quotient `(J:x_n^\infty)`.

        INPUT:

        - ``ring`` -- the ambient polynomial ring in neglex order.

        - ``ideal`` -- the ideal `J`.

        - ``n`` -- Integer. The index of the next variable to divide by.

        OUTPUT:

        The ideal quotient `(J:x_n^\infty)`.

        ALGORITHM:

        Proposition 4 of [GRIN].

        EXAMPLES::

            sage: A = lambda d: matrix([[1,1,1,1,1],[0,1,1,0,0],[0,0,1,1,d]])
            sage: IA = ToricIdeal(A(3))
            sage: R = PolynomialRing(QQ, 5, 'z', order='neglex')
            sage: J0 = IA._naive_ideal(R)
            sage: IA._ideal_quotient_by_variable(R, J0, 0)
            Ideal (z2*z3^2 - z0*z1*z4, z1*z3 - z0*z2,
                   z2^2*z3 - z1^2*z4, z1^3*z4 - z0*z2^3)
            of Multivariate Polynomial Ring in z0, z1, z2, z3, z4 over Rational Field
        """
        N = self.nvariables()
        y = list(ring.gens())
        x = [ y[i-n] for i in range(0,N) ]
        y_to_x = dict(zip(x,y))
        x_to_y = dict(zip(y,x))

        # swap variables such that the n-th variable becomes the last one
        J = ideal.subs(y_to_x)

        # TODO: Can we use the weighted homogeneity with respect to
        # the rows of self.A() when computing the Groebner basis, see
        # [GRIN]?
        basis = J.groebner_basis()

        x_n = y[0]   # the cheapest variable in the revlex order
        def divide_by_x_n(p):
            power = min([ e[0] for e in p.exponents() ])
            return p/x_n**power

        basis = map(divide_by_x_n, basis)

        quotient = ring.ideal(basis)
        return quotient.subs(x_to_y)

    def _ideal_HostenSturmfels(self):
        r"""
        Compute the toric ideal by Hosten and Sturmfels' algorithm.

        OUTPUT:

        The toric ideal as an ideal in the polynomial ring
        ``self.ring()``.

        EXAMPLES::

            sage: A = matrix([[3,2,1,0],[0,1,2,3]])
            sage: IA = ToricIdeal(A);  IA
            Ideal (-z1*z2 + z0*z3, -z1^2 + z0*z2, z2^2 - z1*z3)
            of Multivariate Polynomial Ring in z0, z1, z2, z3 over Rational Field
            sage: R = IA.ring()
            sage: IA == IA._ideal_HostenSturmfels()
            True

        TESTS::

            sage: I_2x2 = identity_matrix(ZZ,2)
            sage: ToricIdeal(I_2x2)
            Ideal (0) of Multivariate Polynomial Ring in z0, z1 over Rational Field
        """
        ring = self._init_ring('neglex')
        J = self._naive_ideal(ring)
        if J.is_zero():
            return J
        for i in range(0,self.nvariables()):
            J = self._ideal_quotient_by_variable(ring, J, i)
        return J
