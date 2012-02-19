r"""
Set of homomorphisms between two toric varieties.

For schemes `X` and `Y`, this module implements the set of morphisms
`Hom(X,Y)`. This is done by :class:`SchemeHomset_generic`.

As a special case, the Hom-sets can also represent the points of a
scheme. Recall that the `K`-rational points of a scheme `X` over `k`
can be identified with the set of morphisms `Spec(K) \to X`. In Sage,
the rational points are implemented by such scheme morphisms. This is
done by :class:`SchemeHomset_points` and its subclasses.

.. note::

    You should not create the Hom-sets manually. Instead, use the
    :meth:`~sage.structure.parent.Hom` method that is inherited by all
    schemes.
"""

from sage.rings.all import ZZ, is_RingHomomorphism
from sage.matrix.matrix import is_Matrix
from sage.matrix.matrix_space import MatrixSpace
from sage.geometry.fan_morphism import FanMorphism

from sage.schemes.generic.homset import SchemeHomset_generic


class SchemeHomset_toric_variety(SchemeHomset_generic):
    """
    Set of homomorphisms between two toric varieties.

    EXAMPLES::

        sage: P1xP1 = toric_varieties.P1xP1()
        sage: P1 = toric_varieties.P1()
        sage: hom_set = P1xP1.Hom(P1);  hom_set
        Set of morphisms
         From: 2-d CPR-Fano toric variety covered by 4 affine patches
         To:   1-d CPR-Fano toric variety covered by 2 affine patches
        sage: type(hom_set)
        <class 'sage.schemes.generic.toric_homset.SchemeHomset_toric_variety_with_category'>

        sage: hom_set(matrix([[1],[0]]))
        Scheme morphism:
          From: 2-d CPR-Fano toric variety covered by 4 affine patches
          To:   1-d CPR-Fano toric variety covered by 2 affine patches
          Defn: Defined by sending the Rational polyhedral fan in 2-d lattice N
                to Rational polyhedral fan in 1-d lattice N.
    """

    def __init__(self, X, Y, category=None, check=True, base=ZZ):
        SchemeHomset_generic.__init__(self, X, Y, category=category, check=check, base=base)
        self.register_conversion(MatrixSpace(ZZ, X.fan().dim(), Y.fan().dim()))

    def _element_constructor_(self, x, check=True):
        """
        Construct a scheme morphism.

        INPUT:

        - `x` -- anything that defines a morphism of toric
          varieties. A matrix, fan morphism, or a list or tuple of
          homogeneous polynomials that define a morphism.

        - ``check`` -- boolean (default: ``True``) passed onto
          functions called by this to be more careful about input
          argument type checking

        OUTPUT:

        The morphism of toric varieties determined by ``x``.

        EXAMPLES:

        First, construct from fan morphism::

            sage: dP8.<t,x0,x1,x2> = toric_varieties.dP8()
            sage: P2.<y0,y1,y2> = toric_varieties.P2()
            sage: Hom = dP8.Hom(P2)

            sage: fm = FanMorphism(identity_matrix(2), dP8.fan(), P2.fan())
            sage: Hom(fm)
            Scheme morphism:
              From: 2-d CPR-Fano toric variety covered by 4 affine patches
              To:   2-d CPR-Fano toric variety covered by 3 affine patches
              Defn: Defined by sending the Rational polyhedral fan in 2-d lattice N
                    to Rational polyhedral fan in 2-d lattice N.

        A matrix will automatically be converted to a fan morphism::

            sage: Hom(identity_matrix(2))
            Scheme morphism:
              From: 2-d CPR-Fano toric variety covered by 4 affine patches
              To:   2-d CPR-Fano toric variety covered by 3 affine patches
              Defn: Defined by sending the Rational polyhedral fan in 2-d lattice N
                    to Rational polyhedral fan in 2-d lattice N.

        Alternatively, one can use homogeneous polynomials to define morphisms::

            sage: P2.inject_variables()
            Defining y0, y1, y2
            sage: dP8.inject_variables()
            Defining t, x0, x1, x2
            sage: Hom([x0,x1,x2])
            Scheme morphism:
              From: 2-d CPR-Fano toric variety covered by 4 affine patches
              To:   2-d CPR-Fano toric variety covered by 3 affine patches
              Defn: Defined on coordinates by sending [t : x0 : x1 : x2] to
                    [x0 : x1 : x2]

        A morphism of the coordinate ring will also work::

            sage: ring_hom = P2.coordinate_ring().hom([x0,x1,x2], dP8.coordinate_ring())
            sage: ring_hom
            Ring morphism:
              From: Multivariate Polynomial Ring in y0, y1, y2 over Rational Field
              To:   Multivariate Polynomial Ring in t, x0, x1, x2 over Rational Field
              Defn: y0 |--> x0
                    y1 |--> x1
                    y2 |--> x2
            sage: Hom(ring_hom)
            Scheme morphism:
              From: 2-d CPR-Fano toric variety covered by 4 affine patches
              To:   2-d CPR-Fano toric variety covered by 3 affine patches
              Defn: Defined on coordinates by sending [t : x0 : x1 : x2] to
                    [x0 : x1 : x2]
        """
        from sage.schemes.generic.toric_morphism import SchemeMorphism_polynomial_toric_variety
        if isinstance(x, (list, tuple)):
            return SchemeMorphism_polynomial_toric_variety(self, x, check=check)

        if is_RingHomomorphism(x):
            assert x.domain() is self.codomain().coordinate_ring()
            assert x.codomain() is self.domain().coordinate_ring()
            return SchemeMorphism_polynomial_toric_variety(self, x.im_gens(), check=check)

        from sage.schemes.generic.toric_morphism import SchemeMorphism_fan_toric_variety
        if isinstance(x, FanMorphism):
            return SchemeMorphism_fan_toric_variety(self, x, check=check)

        if is_Matrix(x):
            fm = FanMorphism(x, self.domain().fan(), self.codomain().fan())
            return SchemeMorphism_fan_toric_variety(self, fm, check=check)

        raise TypeError, "x must be a fan morphism or a list/tuple of polynomials"
