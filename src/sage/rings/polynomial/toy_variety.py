"""
Educational Versions of Groebner Basis Algorithms: Triangular Factorization.

In this file is the implementation of two algorithms in [Laz92]_.

The main algorithm is ``Triangular``; a secondary algorithm, necessary for the
first, is ``ElimPolMin``. As per Lazard's formulation, the implementation works
with any term ordering, not only lexicographic.

Lazard does not specify a few of the subalgorithms implemented as the
functions

* ``is_triangular``,
* ``is_linearly_dependent``, and
* ``linear_representation``.

The implementations are not hard, and the choice of algorithm is described
with the relevant function.

No attempt was made to optimize these algorithms as the emphasis of this
implementation is a clean and easy presentation.

Examples appear with the appropriate function.

AUTHORS:

- John Perry (2009-02-24): initial version, but some words of
  documentation were stolen shamelessly from Martin Albrecht's
  ``toy_buchberger.py``.

REFERENCES:

.. [Laz92] Daniel Lazard, *Solving Zero-dimensional Algebraic Systems*,
  in Journal of Symbolic Computation (1992) vol\. 13, pp\. 117-131

"""

def is_triangular(B):
  """
  Check whether the basis ``B`` of an ideal is triangular.  That is:
  check whether the largest variable in ``B[i]`` with respect to the
  ordering of the base ring ``R`` is ``R.gens()[i]``.

  The algorithm is based on the definition of a triangular basis,
  given by Lazard in 1992 in [Laz92]_.

  INPUT:

  - ``B`` - a list/tuple of polynomials or a multivariate polynomial ideal

  OUTPUT:

      ``True`` if the basis is triangular; ``False`` otherwise.

  EXAMPLE::

      sage: from sage.rings.polynomial.toy_variety import is_triangular
      sage: R.<x,y,z> = PolynomialRing(QQ)
      sage: p1 = x^2*y + z^2
      sage: p2 = y*z + z^3
      sage: p3 = y+z
      sage: is_triangular(R.ideal(p1,p2,p3))
      False
      sage: p3 = z^2 - 3
      sage: is_triangular(R.ideal(p1,p2,p3))
      True
  """
  # type checking in a probably vain attempt to avoid stupid errors
  if isinstance(B, (list, tuple)):
    G = B
  else:
    try:
      G = B.gens()
    except StandardError:
      raise TypeError, "is_triangular wants as input an ideal, or a list of polynomials\n"
  vars = G[0].parent().gens()
  n = len(G)
  # We expect the polynomials of G to be ordered G[i].lm() > G[i+1].lm();
  # by definition, the largest variable that appears in G[i] must be vars[i].
  for i in xrange(n):
    for t in G[i].monomials():
      for x in vars[0:i]:
        if t.degree(x) != 0:
          return False
  return True


def coefficient_matrix(polys):
  """
  Generates the matrix ``M`` whose entries are the coefficients of
  ``polys``.  The entries of row ``i`` of ``M`` consist of the
  coefficients of ``polys[i]``.

  INPUT:

  - ``polys`` - a list/tuple of polynomials

  OUTPUT:

      A matrix ``M`` of the coefficients of ``polys``.

  EXAMPLE::

      sage: from sage.rings.polynomial.toy_variety import coefficient_matrix
      sage: R.<x,y> = PolynomialRing(QQ)
      sage: coefficient_matrix([x^2 + 1, y^2 + 1, x*y + 1])
      [1 0 0 1]
      [0 0 1 1]
      [0 1 0 1]

  .. note::

    This function may be merged with :meth:`sage.crypto.mq.MPolynomialSystem_generic.coefficient_matrix()` in
    the future.
  """
  from sage.matrix.constructor import matrix
  R = polys[0].base_ring()
  mons = set()
  for each in polys:
    mons = mons.union(each.monomials())
  mons = list(mons)
  mons.sort(reverse=True)
  M = matrix(R, len(polys), len(mons))
  for i in xrange(len(polys)):
    imons = polys[i].monomials()
    icoeffs = polys[i].coefficients()
    for j in xrange(len(imons)):
      M[i,mons.index(imons[j])] = icoeffs[j]
  return M

def is_linearly_dependent(polys):
  """
  Decides whether the polynomials of ``polys`` are linearly dependent.
  Here ``polys`` is a collection of polynomials.

  The algorithm creates a matrix of coefficients of the monomials of
  ``polys``. It computes the echelon form of the matrix, then checks whether
  any of the rows is the zero vector.

  Essentially this relies on the fact that the monomials are linearly
  independent, and therefore is building a linear map from the vector space of
  the monomials to the canonical basis of ``R^n``, where ``n`` is the number of
  distinct monomials in ``polys``. There is a zero vector iff there is a
  linear dependence among ``polys``.

  The case where ``polys=[]`` is considered to be not linearly dependent.

  INPUT:

  - ``polys`` - a list/tuple of polynomials

  OUTPUT:

      ``True`` if the elements of ``polys`` are linearly dependent;
      ``False`` otherwise.

  EXAMPLE::

      sage: from sage.rings.polynomial.toy_variety import is_linearly_dependent
      sage: R.<x,y> = PolynomialRing(QQ)
      sage: B = [x^2 + 1, y^2 + 1, x*y + 1]
      sage: p = 3*B[0] - 2*B[1] + B[2]
      sage: is_linearly_dependent(B + [p])
      True
      sage: p = x*B[0]
      sage: is_linearly_dependent(B + [p])
      False
      sage: is_linearly_dependent([])
      False

  """
  if len(polys) == 0:
    return False
  R = polys[0].base_ring()
  M = coefficient_matrix(polys).echelon_form()
  return any(M.row(each).is_zero() for each in xrange(M.nrows()))

def linear_representation(p, polys):
  """
  Assuming that ``p`` is a linear combination of ``polys``,
  determines coefficients that describe the linear combination.
  This probably doesn't work for any inputs except ``p``, a polynomial,
  and ``polys``, a sequence of polynomials.
  If ``p`` is not in fact a linear combination of ``polys``,
  the function raises an exception.

  The algorithm creates a matrix of coefficients of the monomials of
  ``polys`` and ``p``, with the coefficients of ``p`` in the last
  row. It augments this matrix with the appropriate identity matrix, then
  computes the echelon form of the augmented matrix. The last row should
  contain zeroes in the first columns, and the last
  columns contain a linear dependence relation. Solving for
  the desired linear relation is straightforward.

  INPUT:

  - ``p`` - a polynomial
  - ``polys`` - a list/tuple of polynomials

  OUTPUT:

      If ``n == len(polys)``, returns ``[a[0],a[1],...,a[n-1]]``
      such that ``p == a[0]*poly[0] + ... + a[n-1]*poly[n-1]``.

  EXAMPLE::

      sage: from sage.rings.polynomial.toy_variety import linear_representation
      sage: R.<x,y> = PolynomialRing(GF(32003))
      sage: B = [x^2 + 1, y^2 + 1, x*y + 1]
      sage: p = 3*B[0] - 2*B[1] + B[2]
      sage: linear_representation(p, B)
      [3, 32001, 1]

  """
  from sage.matrix.constructor import diagonal_matrix
  R = p.base_ring()
  M = coefficient_matrix(polys + [p]).augment(diagonal_matrix(R, [1 for each in xrange(len(polys) + 1)]))
  M.echelonize()
  j = M.ncols() - 1
  n = M.nrows() - 1
  offset = M.ncols() - M.nrows()
  return [M[n,offset+each] / (-M[n,j]) for each in xrange(len(polys))]

def triangular_factorization(B, n=-1):
  """
  Compute the triangular factorization of the Groebner basis ``B`` of an ideal.

  This will not work properly if ``B`` is not a Groebner basis!

  The algorithm used is that described in a 1992 paper by Daniel Lazard [Laz92]_.
  It is not necessary for the term ordering to be lexicographic.

  INPUT:

  - ``B`` - a list/tuple of polynomials or a multivariate polynomial ideal
  - ``n`` - the recursion parameter (default: ``-1``)

  OUTPUT:

      A list ``T`` of triangular sets ``T_0``, ``T_1``, etc.

  EXAMPLE::

      sage: set_verbose(0)
      sage: from sage.rings.polynomial.toy_variety import triangular_factorization
      sage: R.<x,y,z> = PolynomialRing(GF(32003))
      sage: p1 = x^2*(x-1)^3*y^2*(z-3)^3
      sage: p2 = z^2 - z
      sage: p3 = (x-2)^2*(y-1)^3
      sage: I = R.ideal(p1,p2,p3)
      sage: triangular_factorization(I.groebner_basis())
      [[x^2 - 4*x + 4, y, z],
       [x^5 - 3*x^4 + 3*x^3 - x^2, y - 1, z],
       [x^2 - 4*x + 4, y, z - 1],
       [x^5 - 3*x^4 + 3*x^3 - x^2, y - 1, z - 1]]
  """
  import sage.rings.polynomial.polynomial_ring_constructor as prc
  import copy
  # type checking in a probably vain attempt to avoid stupid errors
  if isinstance(B, (tuple,list)):
    G = B
  else:
    try:
      G = B.gens()
    except StandardError:
      raise TypeError, "triangular_factorization wants as input an ideal, or a list of polynomials\n"
  # easy cases
  if len(G)==0:
    return list()
  if is_triangular(G):
    return [G]
  # this is what we get paid for...
  # first, find the univariate polynomial in the ideal
  # corresponding to the smallest variable under consideration
  p = elim_pol(G,n)
  R = p.parent()
  family = []
  # recursively build the family,
  # looping through the factors of p
  for (q,a) in p.factor():
    # Construct an analog to I in (R.quotient(R.ideal(q)))[x_0,x_1,...x_{n-1}]
    I = R.ideal([each.reduce([q]) for each in G])
    if len(I.gens()) == 1:
      # save some effort
      H = [I.gens()[0]]
    else:
      H = I.groebner_basis()
    T = triangular_factorization(list(H),n-1)
    # now add the current factor q of p to the factorization
    for each in T:
      each.append(q)
    for each in T:
      family.append(each)
  return family

def elim_pol(B, n=-1):
  """
  Finds the unique monic polynomial of lowest degree and lowest variable
  in the ideal described by ``B``.

  For the purposes of the triangularization algorithm, it is necessary to
  preserve the ring, so ``n`` specifies which variable to check.
  By default, we check the last one, which should also be the smallest.

  The algorithm may not work if you are trying to cheat:
  ``B`` should describe the Groebner basis of a zero-dimensional ideal.
  However, it is not necessary for the Groebner basis to be lexicographic.

  The algorithm is taken from a 1993 paper by Lazard [Laz92]_.

  INPUT:

  - ``B`` - a list/tuple of polynomials or a multivariate polynomial ideal
  - ``n`` - the variable to check (see above) (default: ``-1``)

  EXAMPLE::

      sage: set_verbose(0)
      sage: from sage.rings.polynomial.toy_variety import elim_pol
      sage: R.<x,y,z> = PolynomialRing(GF(32003))
      sage: p1 = x^2*(x-1)^3*y^2*(z-3)^3
      sage: p2 = z^2 - z
      sage: p3 = (x-2)^2*(y-1)^3
      sage: I = R.ideal(p1,p2,p3)
      sage: elim_pol(I.groebner_basis())
      z^2 - z
  """
  # type checking in a probably vain attempt to avoid stupid errors
  if isinstance(B, (list,tuple)):
    G = B
  else:
    try:
      G = B.gens()
    except StandardError:
      raise TypeError, "elim_pol wants as input an ideal or a list of polynomials"

  # setup -- main algorithm
  x = G[0].parent().gens()[n]
  monom = x**0
  nfm = monom.reduce(G)
  lnf = []
  listmonom = []
  # ratchet up the degree of monom, adding each time a normal form,
  # until finally the normal form is a linear combination
  # of the previous normal forms
  while not is_linearly_dependent(lnf + [nfm]):
    lnf.insert(0,nfm)
    listmonom.append(monom)
    monom = x * monom
    nfm = monom.reduce(G)
  result = monom
  coeffs = linear_representation(nfm, lnf)
  for each in xrange(len(coeffs)):
    result = result - coeffs[each] * lnf[each]
  return result
