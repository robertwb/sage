﻿r"""
Toric varieties

This module provides support for (normal) toric varieties, corresponding to
:class:`rational polyhedral fans <sage.geometry.fan.RationalPolyhedralFan>`.
See also :mod:`~sage.schemes.generic.fano_toric_variety` for a more
restrictive class of (weak) Fano toric varieties.

An **excellent reference on toric varieties** is the book "Toric Varieties" by
David A. Cox, John B. Little, and Hal Schenck [CLS]_. Its draft **is freely
available** at
http://www.cs.amherst.edu/~dac/toric.html
**but will be removed** from this site once it is published, so hurry up!

The interface to this module is provided through functions
:func:`AffineToricVariety` and :func:`ToricVariety`, although you may also be
interested in :func:`normalize_names`.

.. NOTE::

    We do NOT build "general toric varieties" from affine toric varieties.
    Instead, we are using the quotient representation of toric varieties with
    the homogeneous coordinate ring (a.k.a. Cox's ring or the total coordinate
    ring). This description works best for simplicial fans of the full
    dimension.

REFERENCES:

..  [CLS]
    David A. Cox, John B. Little,  Hal Schenck,
    "Toric Varieties", Graduate Studies in Mathematics,
    Amer. Math. Soc., Providence, RI, to appear.

AUTHORS:

- Andrey Novoseltsev (2010-05-17): initial version.

- Volker Braun (2010-07-24): Cohomology and characteristic classes added.

EXAMPLES:

We start with constructing the affine plane as an affine toric variety. First,
we need to have a corresponding cone::

    sage: quadrant = Cone([(1,0), (0,1)])

If you don't care about variable names and the base field, that's all we need
for now::

    sage: A2 = AffineToricVariety(quadrant)
    sage: A2
    2-d affine toric variety
    sage: origin = A2(0,0)
    sage: origin
    [0 : 0]

Only affine toric varieties have points whose (homogeneous) coordinates
are all zero. ::

    sage: parent(origin)
    Set of Rational Points of 2-d affine toric variety

As you can see, by default toric varieties live over the field of rational
numbers::

    sage: A2.base_ring()
    Rational Field

While usually toric varieties are considered over the field of complex
numbers, for computational purposes it is more convenient to work with fields
that have exact representation on computers. You can also always do ::

    sage: C2 = AffineToricVariety(quadrant, base_field=CC)
    sage: C2.base_ring()
    Complex Field with 53 bits of precision
    sage: C2(1,2+i)
    [1.00000000000000 : 2.00000000000000 + 1.00000000000000*I]

or even ::

    sage: F = CC["a, b"].fraction_field()
    sage: F.inject_variables()
    Defining a, b
    sage: A2 = AffineToricVariety(quadrant, base_field=F)
    sage: A2(a,b)
    [a : b]

OK, if you need to work only with affine spaces,
:func:`~sage.schemes.generic.affine_space.AffineSpace` may be a better way to
construct them. Our next example is the product of two projective lines
realized as the toric variety associated to the
:func:`face fan <sage.geometry.fan.FaceFan>` of the "diamond"::

    sage: diamond = lattice_polytope.octahedron(2)
    sage: diamond.vertices()
    [ 1  0 -1  0]
    [ 0  1  0 -1]
    sage: fan = FaceFan(diamond)
    sage: P1xP1 = ToricVariety(fan)
    sage: P1xP1
    2-d toric variety covered by 4 affine patches
    sage: P1xP1.fan().ray_matrix()
    [ 1  0 -1  0]
    [ 0  1  0 -1]
    sage: P1xP1.gens()
    (z0, z1, z2, z3)

We got four coordinates - two for each of the projective lines, but their
names are perhaps not very well chosen. Let's make `(x,y)` to be coordinates
on the first line and `(s,t)` on the second one::

    sage: P1xP1 = ToricVariety(fan, coordinate_names="x s y t")
    sage: P1xP1.gens()
    (x, s, y, t)

Now, if we want to define subschemes of this variety, the defining polynomials
must be homogeneous in each of these pairs::

    sage: P1xP1.inject_variables()
    Defining x, s, y, t
    sage: P1xP1.subscheme(x)
    Closed subscheme of 2-d toric variety
    covered by 4 affine patches defined by:
      x
    sage: P1xP1.subscheme(x^2 + y^2)
    Closed subscheme of 2-d toric variety
    covered by 4 affine patches defined by:
      x^2 + y^2
    sage: P1xP1.subscheme(x^2 + s^2)
    Traceback (most recent call last):
    ...
    ValueError: x^2 + s^2 is not homogeneous
    on 2-d toric variety covered by 4 affine patches!
    sage: P1xP1.subscheme([x^2*s^2 + x*y*t^2 +y^2*t^2, s^3 + t^3])
    Closed subscheme of 2-d toric variety
    covered by 4 affine patches defined by:
      x^2*s^2 + x*y*t^2 + y^2*t^2,
      s^3 + t^3

While we don't build toric varieties from affine toric varieties, we still can
access the "building pieces"::

    sage: patch = P1xP1.affine_patch(2)
    sage: patch
    2-d affine toric variety
    sage: patch.fan().ray_matrix()
    [1 0]
    [0 1]
    sage: patch.embedding_morphism()
    Scheme morphism:
      From: 2-d affine toric variety
      To:   2-d toric variety covered by 4 affine patches
      Defn: Defined on coordinates by sending [x : s] to
            [x : s : 1 : 1]

The patch above was specifically chosen to coincide with our representation of
the affine plane before, but you can get the other three patches as well.
(While any cone of a fan will correspond to an affine toric variety, the main
interest is usually in the generating fans as "the biggest" affine
subvarieties, and these are precisely the patches that you can get from
:meth:`~ToricVariety_field.affine_patch`.)

All two-dimensional toric varieties are "quite nice" because any
two-dimensional cone is generated by exactly two rays. From the point of view
of the corresponding toric varieties, this means that they have at worst
quotient singularities::

    sage: P1xP1.is_orbifold()
    True
    sage: P1xP1.is_smooth()
    True
    sage: TV = ToricVariety(NormalFan(diamond))
    sage: TV.fan().ray_matrix()
    [-1  1 -1  1]
    [ 1  1 -1 -1]
    sage: TV.is_orbifold()
    True
    sage: TV.is_smooth()
    False

In higher dimensions worse things can happen::

    sage: TV3 = ToricVariety(NormalFan(lattice_polytope.octahedron(3)))
    sage: TV3.fan().ray_matrix()
    [-1  1 -1  1 -1  1 -1  1]
    [-1 -1  1  1 -1 -1  1  1]
    [ 1  1  1  1 -1 -1 -1 -1]
    sage: TV3.is_orbifold()
    False

Fortunately, we can perform a (partial) resolution::

    sage: TV3_res = TV3.resolve_to_orbifold()
    sage: TV3_res.is_orbifold()
    True
    sage: TV3_res.fan().ngenerating_cones()
    12
    sage: TV3.fan().ngenerating_cones()
    6

In this example we had to double the number of affine patches. The result is
still singular::

    sage: TV3_res.is_smooth()
    False

You can resolve it further using :meth:`~ToricVariety_field.resolve` method,
but (at least for now) you will have to specify which rays should be inserted
into the fan. See also
:func:`~sage.schemes.generic.fano_toric_variety.CPRFanoToricVariety`,
which can construct some other "nice partial resolutions."

Below you will find detailed descriptions of available functions. If you are
familiar with toric geometry, you will likely see that many important objects
and operations are unavailable. However, this module is under active
development and hopefully will improve in future releases of Sage. If there
are some particular features that you would like to see implemented ASAP,
please consider reporting them to the Sage Development Team or even
implementing them on your own as a patch for inclusion!
"""


#*****************************************************************************
#       Copyright (C) 2010 Volker Braun <vbraun.name@gmail.com>
#       Copyright (C) 2010 Andrey Novoseltsev <novoselt@gmail.com>
#       Copyright (C) 2010 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.geometry.cone import Cone, is_Cone
from sage.geometry.fan import Fan
from sage.matrix.all import matrix
from sage.misc.all import latex, prod
from sage.structure.unique_representation import UniqueRepresentation
from sage.modules.free_module_element import vector
from sage.rings.all import PolynomialRing, ZZ, QQ, is_Field, is_FractionField
from sage.rings.quotient_ring_element import QuotientRingElement
from sage.rings.quotient_ring import QuotientRing_generic
from sage.schemes.generic.ambient_space import AmbientSpace
from sage.schemes.generic.homset import (SchemeHomset_coordinates,
                                         SchemeHomset_toric_coordinates_field)
from sage.schemes.generic.morphism import (SchemeMorphism_on_points_toric_variety,
                                           SchemeMorphism_toric_coordinates_field,
                                           SchemeMorphism_coordinates,
                                           SchemeMorphism_on_points,
                                           is_SchemeMorphism)
from sage.structure.sequence import Sequence
from sage.functions.all import factorial


# Default prefix for indexed coordinates
DEFAULT_PREFIX = "z"


def is_ToricVariety(x):
    r"""
    Check if ``x`` is a toric variety.

    INPUT:

    - ``x`` -- anything.

    OUTPUT:

    - ``True`` if ``x`` is a :class:`toric variety <ToricVariety_field>` and
      ``False`` otherwise.

    .. NOTE::

        While projective spaces are toric varieties mathematically, they are
        not toric varieties in Sage due to efficiency considerations, so this
        function will return ``False``.

    EXAMPLES::

        sage: from sage.schemes.generic.toric_variety import is_ToricVariety
        sage: is_ToricVariety(1)
        False
        sage: fan = FaceFan(lattice_polytope.octahedron(2))
        sage: P = ToricVariety(fan)
        sage: P
        2-d toric variety covered by 4 affine patches
        sage: is_ToricVariety(P)
        True
        sage: is_ToricVariety(ProjectiveSpace(2))
        False
    """
    return isinstance(x, ToricVariety_field)


def ToricVariety(fan,
                 coordinate_names=None,
                 coordinate_indices=None,
                 base_field=QQ):
    r"""
    Construct a toric variety.

    INPUT:

    - ``fan`` -- :class:`rational polyhedral fan
      <sage.geometry.fan.RationalPolyhedralFan>`;

    - ``coordinate_names`` -- names of variables for the coordinate ring, see
      :func:`normalize_names` for acceptable formats. If not given, indexed
      variable names will be created automatically;

    - ``coordinate_indices`` -- list of integers, indices for indexed
      variables. If not given, the index of each variable will coincide with
      the index of the corresponding ray of the fan;

    - ``base_field`` -- base field of the toric variety (default: `\QQ`).

    OUTPUT:

    - :class:`toric variety <ToricVariety_field>`.

    EXAMPLES:

    We will create the product of two projective lines::

        sage: fan = FaceFan(lattice_polytope.octahedron(2))
        sage: fan.ray_matrix()
        [ 1  0 -1  0]
        [ 0  1  0 -1]
        sage: P1xP1 = ToricVariety(fan)
        sage: P1xP1.gens()
        (z0, z1, z2, z3)

    Let's create some points::

        sage: P1xP1(1,1,1,1)
        [1 : 1 : 1 : 1]
        sage: P1xP1(0,1,1,1)
        [0 : 1 : 1 : 1]
        sage: P1xP1(0,1,0,1)
        Traceback (most recent call last):
        ...
        TypeError: coordinates (0, 1, 0, 1)
        are in the exceptional set!

    We cannot set to zero both coordinates of the same projective line!

    Let's change the names of the variables. We have to re-create our toric
    variety::

        sage: P1xP1 = ToricVariety(fan, "x s y t")
        sage: P1xP1.gens()
        (x, s, y, t)

    Now `(x, y)` correspond to one line and `(s, t)` to the other one. ::

        sage: P1xP1.inject_variables()
        Defining x, s, y, t
        sage: P1xP1.subscheme(x*s-y*t)
        Closed subscheme of 2-d toric variety
        covered by 4 affine patches defined by:
          x*s - y*t
    """
    if not is_Field(base_field):
        raise TypeError("need a field to construct a toric variety!\n Got %s"
                        % base_field)
    return ToricVariety_field(fan, coordinate_names, coordinate_indices,
                             base_field)


def AffineToricVariety(cone, *args, **kwds):
    r"""
    Construct an affine toric variety.

    INPUT:

    - ``cone`` -- :class:`strictly convex rational polyhedral cone
      <sage.geometry.cone.ConvexRationalPolyhedralCone>`.

    This cone will be used to construct a :class:`rational polyhedral fan
    <sage.geometry.fan.RationalPolyhedralFan>`, which will be passed to
    :func:`ToricVariety` with the rest of positional and keyword arguments.

    OUTPUT:

    - :class:`toric variety <ToricVariety_field>`.

    .. NOTE::

        The generating rays of the fan of this variety are guaranteed to be
        listed in the same order as the rays of the original cone.

    EXAMPLES:

    We will create the affine plane as an affine toric variety::

        sage: quadrant = Cone([(1,0), (0,1)])
        sage: A2 = AffineToricVariety(quadrant)
        sage: origin = A2(0,0)
        sage: origin
        [0 : 0]
        sage: parent(origin)
        Set of Rational Points of 2-d affine toric variety

    Only affine toric varieties have points whose (homogeneous) coordinates
    are all zero.
    """
    if not cone.is_strictly_convex():
        raise ValueError("affine toric varieties are defined for strictly "
                         "convex cones only!")
    # We make sure that Fan constructor does not meddle with the order of
    # rays, this is very important for affine patches construction
    fan = Fan([tuple(range(cone.nrays()))], cone.rays(),
              check=False, normalize=False)
    return ToricVariety(fan, *args, **kwds)


class ToricVariety_field(AmbientSpace):
    r"""
    Construct a toric variety associated to a rational polyhedral fan.

    .. WARNING::

        This class does not perform any checks of correctness of input. Use
        :func:`ToricVariety` and :func:`AffineToricVariety` to construct toric
        varieties.

    INPUT:

    - ``fan`` -- :class:`rational polyhedral fan
      <sage.geometry.fan.RationalPolyhedralFan>`;

    - ``coordinate_names`` -- names of variables, see :func:`normalize_names`
      for acceptable formats. If ``None``, indexed variable names will be
      created automatically;

    - ``coordinate_indices`` -- list of integers, indices for indexed
      variables. If ``None``, the index of each variable will coincide with
      the index of the corresponding ray of the fan;

    - ``base_field`` -- base field of the toric variety.

    OUTPUT:

    - :class:`toric variety <ToricVariety_field>`.

    TESTS::

        sage: fan = FaceFan(lattice_polytope.octahedron(2))
        sage: P1xP1 = ToricVariety(fan)
    """

    def __init__(self, fan, coordinate_names, coordinate_indices, base_field):
        r"""
        See :class:`ToricVariety_field` for documentation.

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
        """
        self._fan = fan
        super(ToricVariety_field, self).__init__(fan.lattice_dim(),
                                                 base_field)
        self._torus_factor_dim = fan.lattice_dim() - fan.dim()
        coordinate_names = normalize_names(coordinate_names,
                        fan.nrays() + self._torus_factor_dim, DEFAULT_PREFIX,
                        coordinate_indices, return_prefix=True)
        # Save the prefix for use in resolutions
        self._coordinate_prefix = coordinate_names.pop()
        self._assign_names(names=coordinate_names, normalize=False)

    def __cmp__(self, right):
        r"""
        Compare ``self`` and ``right``.

        INPUT:

        - ``right`` -- anything.

        OUTPUT:

        - 0 if ``right`` is of the same type as ``self``, their fans are the
          same, names of variables are the same and stored in the same order,
          and base fields are the same. 1 or -1 otherwise.

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1a = ToricVariety(fan, "x s y t")
            sage: P1xP1b = ToricVariety(fan)
            sage: cmp(P1xP1, P1xP1a)
            1
            sage: cmp(P1xP1a, P1xP1)
            -1
            sage: cmp(P1xP1, P1xP1b)
            0
            sage: P1xP1 is P1xP1b
            False
            sage: cmp(P1xP1, 1) * cmp(1, P1xP1)
            -1
        """
        c = cmp(type(self), type(right))
        if c:
            return c
        return cmp([self.fan(),
                    self.variable_names(),
                    self.base_ring()],
                   [right.fan(),
                    right.variable_names(),
                    right.base_ring()])

    def _an_element_(self):
        r"""
        Construct an element of ``self``.

        This function is needed (in particular) for the test framework.

        OUTPUT:

        - a point of ``self`` with coordinates [1 : 2: ... : n].

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1._an_element_()
            [1 : 2 : 3 : 4]
        """
        return self(range(1, self.ngens() + 1))

    def _check_satisfies_equations(self, coordinates):
        r"""
        Check if ``coordinates`` define a valid point of ``self``.

        INPUT:

        - ``coordinates`` -- list of elements of the base field of ``self``.

        OUTPUT:

        - ``True`` if ``coordinates`` do define a valid point of ``self``,
          otherwise a ``TypeError`` or ``ValueError`` exception is raised.

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1._check_satisfies_equations([1,1,1,1])
            True
            sage: P1xP1._check_satisfies_equations([0,0,1,1])
            True
            sage: P1xP1._check_satisfies_equations([0,1,0,1])
            Traceback (most recent call last):
            ...
            TypeError: coordinates (0, 1, 0, 1)
            are in the exceptional set!
            sage: P1xP1._check_satisfies_equations([1,1,1])
            Traceback (most recent call last):
            ...
            TypeError: coordinates (1, 1, 1) must have 4 components!
            sage: P1xP1._check_satisfies_equations(1)
            Traceback (most recent call last):
            ...
            TypeError: 1 can not be used as coordinates!
            Use a list or a tuple.
            sage: P1xP1._check_satisfies_equations([1,1,1,fan])
            Traceback (most recent call last):
            ...
            TypeError: coordinate Rational polyhedral fan
            in 2-d lattice N is not an element of Rational Field!
        """
        try:
            coordinates = tuple(coordinates)
        except TypeError:
            raise TypeError("%s can not be used as coordinates! "
                            "Use a list or a tuple." % coordinates)
        n = self.ngens()
        if len(coordinates) != n:
            raise TypeError("coordinates %s must have %d components!"
                            % (coordinates, n))
        base_field = self.base_ring()
        for coordinate in coordinates:
            if coordinate not in base_field:
                raise TypeError("coordinate %s is not an element of %s!"
                                % (coordinate, base_field))
        zero_positions = set(position
                            for position, coordinate in enumerate(coordinates)
                            if coordinate == 0)
        if not zero_positions:
            return True
        for i in range(n - self._torus_factor_dim, n):
            if i in zero_positions:
                raise ValueError("coordinates on the torus factor cannot be "
                                 "zero! Got %s" % str(coordinates))
        if len(zero_positions) == 1:
            return True
        fan = self.fan()
        possible_charts = set(fan._ray_to_cones(zero_positions.pop()))
        for i in zero_positions:
            possible_charts.intersection_update(fan._ray_to_cones(i))
        if possible_charts:
            return True     # All zeros are inside one generating cone
        raise TypeError("coordinates %s are in the exceptional set!"
                        % str(coordinates)) # Need str, coordinates is a tuple

    def _homset_class(self, *args, **kwds):
        r"""
        Construct a `Hom`-space for ``self``.

        INPUT:

        - same as for
          :class:`~sage.schemes.generic.homset.SchemeHomset_toric_coordinates_field`.

        OUPUT:

        -
          :class:`~sage.schemes.generic.homset.SchemeHomset_toric_coordinates_field`.

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1._homset_class(P1xP1, P1xP1.base_ring())
            Set of Rational Points of 2-d toric variety
            covered by 4 affine patches
        """
        return SchemeHomset_toric_coordinates_field(*args, **kwds)

    def _latex_(self):
        r"""
        Return a LaTeX representation of ``self``.

        OUTPUT:

        - string.

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1._latex_()
            '\\mathbb{X}_{\\Sigma^{2}}'
        """
        return r"\mathbb{X}_{%s}" % latex(self.fan())

    def _latex_generic_point(self, coordinates=None):
        """
        Return a LaTeX representation of a point of ``self``.

        INPUT:

        - ``coordinates`` -- list of coordinates of a point of ``self``.
          If not given, names of coordinates of ``self`` will be used.

        OUTPUT:

        - string.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1._latex_generic_point()
            '\\left[z_{0} : z_{1} : z_{2} : z_{3}\\right]'
            sage: P1xP1._latex_generic_point([1,2,3,4])
            '\\left[1 : 2 : 3 : 4\\right]'
        """
        if coordinates is None:
            coordinates = self.gens()
        return r"\left[%s\right]" % (" : ".join(str(latex(coord))
                                                for coord in coordinates))

    def _point_class(self, *args, **kwds):
        r"""
        Construct a point of ``self``.

        INPUT:

        - same as for
          :class:`~sage.schemes.generic.morphism.SchemeMorphism_toric_coordinates_field`.

        OUPUT:

        :class:`~sage.schemes.generic.morphism.SchemeMorphism_toric_coordinates_field`.

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1._point_class(P1xP1, [1,2,3,4])
            [1 : 2 : 3 : 4]
        """
        return SchemeMorphism_toric_coordinates_field(*args, **kwds)

    def _point_morphism_class(self, *args, **kwds):
        r"""
        Construct a morphism determined by action on points of ``self``.

        INPUT:

        - same as for
          :class:`~sage.schemes.generic.morphism.SchemeMorphism_on_points_toric_variety`.

        OUPUT:

        :class:`~sage.schemes.generic.morphism.SchemeMorphism_on_points_toric_variety`.

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1.inject_variables()
            Defining z0, z1, z2, z3
            sage: P1 = P1xP1.subscheme(z0-z2)
            sage: H = P1xP1.Hom(P1)
            sage: P1xP1._point_morphism_class(H, [z0,z1,z0,z3])
            Scheme morphism:
              From: 2-d toric variety covered by 4 affine patches
              To:   Closed subscheme of 2-d toric variety
              covered by 4 affine patches defined by:
              z0 - z2
              Defn: Defined on coordinates by sending
                    [z0 : z1 : z2 : z3] to [z0 : z1 : z0 : z3]
        """
        return SchemeMorphism_on_points_toric_variety(*args, **kwds)

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        OUTPUT:

        - string.

        TESTS::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1._repr_()
            '2-d toric variety covered by 4 affine patches'
        """
        result = "%d-d" % self.dimension_relative()
        if self.fan().ngenerating_cones() == 1:
            result += " affine toric variety"
        else:
            result += (" toric variety covered by %d affine patches"
                       % self.fan().ngenerating_cones())
        return result

    def _repr_generic_point(self, coordinates=None):
        r"""
        Return a string representation of a point of ``self``.

        INPUT:

        - ``coordinates`` -- list of coordinates of a point of ``self``.
          If not given, names of coordinates of ``self`` will be used.

        OUTPUT:

        - string.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1._repr_generic_point()
            '[z0 : z1 : z2 : z3]'
            sage: P1xP1._repr_generic_point([1,2,3,4])
            '[1 : 2 : 3 : 4]'
        """
        if coordinates is None:
            coordinates = self.gens()
        return "[%s]" % (" : ".join(str(coord) for coord in coordinates))

    def _validate(self, polynomials):
        """
        Check if ``polynomials`` define valid functions on ``self``.

        Since this is a toric variety, polynomials must be homogeneous in the
        total coordinate ring of ``self``.

        INPUT:

        - ``polynomials`` -- list of polynomials in the coordinate ring of
          ``self`` (this function does not perform any conversions).

        OUTPUT:

        - ``polynomials`` (the input parameter without any modifications) if
          ``polynomials`` do define valid polynomial functions on ``self``,
          otherwise a ``ValueError`` exception is raised.

        TESTS:

        We will use the product of two projective lines with coordinates
        `(x, y)` for one and `(s, t)` for the other::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: fan.ray_matrix()
            [ 1  0 -1  0]
            [ 0  1  0 -1]
            sage: P1xP1 = ToricVariety(fan, "x s y t")
            sage: P1xP1.inject_variables()
            Defining x, s, y, t
            sage: P1xP1._validate([x - y, x*s + y*t])
            [x - y, x*s + y*t]
            sage: P1xP1._validate([x + s])
            Traceback (most recent call last):
            ...
            ValueError: x + s is not homogeneous on
            2-d toric variety covered by 4 affine patches!
        """
        for p in polynomials:
            if not self.is_homogeneous(p):
                raise ValueError("%s is not homogeneous on %s!" % (p, self))
        return polynomials

    def affine_patch(self, i):
        r"""
        Return the ``i``-th affine patch of ``self``.

        INPUT:

        - ``i`` -- integer, index of a generating cone of the fan of ``self``.

        OUTPUT:

        - affine :class:`toric variety <ToricVariety_field>` corresponding to
          the ``i``-th generating cone of the fan of ``self``.

        The result is cached, so the ``i``-th patch is always the same object
        in memory.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan, "x s y t")
            sage: patch0 = P1xP1.affine_patch(0)
            sage: patch0
            2-d affine toric variety
            sage: patch0.embedding_morphism()
            Scheme morphism:
              From: 2-d affine toric variety
              To:   2-d toric variety covered by 4 affine patches
              Defn: Defined on coordinates by sending [x : t] to
                    [x : 1 : 1 : t]
            sage: patch1 = P1xP1.affine_patch(1)
            sage: patch1.embedding_morphism()
            Scheme morphism:
              From: 2-d affine toric variety
              To:   2-d toric variety covered by 4 affine patches
              Defn: Defined on coordinates by sending [y : t] to
                    [1 : 1 : y : t]
            sage: patch1 is P1xP1.affine_patch(1)
            True
        """
        i = int(i)   # implicit type checking
        try:
            return self._affine_patches[i]
        except AttributeError:
            self._affine_patches = dict()
        except KeyError:
            pass
        cone = self.fan().generating_cone(i)
        names = self.variable_names()
        # Number of "honest fan coordinates"
        n = self.fan().nrays()
        # Number of "torus factor coordinates"
        t = self._torus_factor_dim
        names = ([names[ray] for ray in cone.ambient_ray_indices()]
                 + list(names[n:]))
        patch = AffineToricVariety(cone, names, base_field=self.base_ring())
        embedding_coordinates = [1] * n
        for k, ray in enumerate(cone.ambient_ray_indices()):
            embedding_coordinates[ray] = patch.gen(k)
        if t > 0: # Passing "-0" gives unintended result
            embedding_coordinates.extend(patch.gens()[-t:])
        patch._embedding_morphism = patch.hom(embedding_coordinates, self)
        self._affine_patches[i] = patch
        return patch

    def change_ring(self, F):
        r"""
        Return a toric variety over ``F`` and otherwise the same as ``self``.

        INPUT:

        - ``F`` -- field.

        OUTPUT:

        - :class:`toric variety <ToricVariety_field>` over ``F``.

        .. NOTE::

            There is no need to have any relation between ``F`` and the base
            field of ``self``. If you do want to have such a relation, use
            :meth:`base_extend` instead.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1.base_ring()
            Rational Field
            sage: P1xP1_RR = P1xP1.change_ring(RR)
            sage: P1xP1_RR.base_ring()
            Real Field with 53 bits of precision
            sage: P1xP1_QQ = P1xP1_RR.change_ring(QQ)
            sage: P1xP1_QQ.base_ring()
            Rational Field
            sage: P1xP1_RR.base_extend(QQ)
            Traceback (most recent call last):
            ...
            ValueError: no natural map from the base ring
            (=Real Field with 53 bits of precision)
            to R (=Rational Field)!
        """
        if self.base_ring() == F:
            return self
        else:
            return ToricVariety(self.fan(), self.variable_names(),
                                base_field=F)

    def coordinate_ring(self):
        r"""
        Return the coordinate ring of ``self``.

        For toric varieties this is the homogeneous coordinate ring (a.k.a.
        Cox's ring and total ring).

        OUTPUT:

        - polynomial ring.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1.coordinate_ring()
            Multivariate Polynomial Ring in z0, z1, z2, z3
            over Rational Field
        """
        if "_coordinate_ring" not in self.__dict__:
            self._coordinate_ring = PolynomialRing(self.base_ring(),
                                                   self.variable_names())
        return self._coordinate_ring

    def embedding_morphism(self):
        r"""
        Return the default embedding morphism of ``self``.

        Such a morphism is always defined for an affine patch of a toric
        variety (which is also a toric varieties itself).

        OUTPUT:

        - :class:`scheme morphism
          <sage.schemes.generic.morphism.SchemeMorphism_on_points_toric_variety>`
          if the default embedding morphism was defined for ``self``,
          otherwise a ``ValueError`` exception is raised.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan, "x s y t")
            sage: P1xP1.embedding_morphism()
            Traceback (most recent call last):
            ...
            ValueError: no default embedding was
            defined for this toric variety!
            sage: patch = P1xP1.affine_patch(0)
            sage: patch
            2-d affine toric variety
            sage: patch.embedding_morphism()
            Scheme morphism:
              From: 2-d affine toric variety
              To:   2-d toric variety covered by 4 affine patches
              Defn: Defined on coordinates by sending [x : t] to
                    [x : 1 : 1 : t]
        """
        try:
            return self._embedding_morphism
        except AttributeError:
            raise ValueError("no default embedding was defined for this "
                             "toric variety!")

    def fan(self, dim=None, codim=None):
        r"""
        Return the underlying fan of ``self`` or its cones.

        INPUT:

        - ``dim`` -- dimension of the requested cones;

        - ``codim`` -- codimension of the requested cones.

        OUTPUT:

        - :class:`rational polyhedral fan
          <sage.geometry.fan.RationalPolyhedralFan>` if no parameters were
          given, :class:`tuple` of :class:`cones
          <sage.geometry.cone.ConvexRationalPolyhedralCone>` otherwise.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1.fan()
            Rational polyhedral fan in 2-d lattice N
            sage: P1xP1.fan() is fan
            True
            sage: P1xP1.fan(1)[0]
            1-d cone of Rational polyhedral fan in 2-d lattice N
        """
        return self._fan(dim, codim)

    def inject_coefficients(self, scope=None, verbose=True):
        r"""
        Inject generators of the base field of ``self`` into ``scope``.

        This function is useful if the base field is the field of rational
        functions.

        INPUT:

        - ``scope`` -- namespace (default: global);

        - ``verbose`` -- if ``True`` (default), names of injected generators
          will be printed.

        OUTPUT:

        - none.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1.inject_coefficients()

        The last command does nothing, since ``P1xP1`` is defined over `\QQ`.
        Let's construct a toric variety over a more complicated field::

            sage: F = QQ["a, b"].fraction_field()
            sage: P1xP1 = ToricVariety(fan, base_field=F)
            sage: P1xP1.inject_coefficients()
            Defining a, b
        """
        if is_FractionField(self.base_ring()):
            self.base_ring().inject_variables(scope, verbose)

    def is_homogeneous(self, polynomial):
        r"""
        Check if ``polynomial`` is homogeneous.

        The coordinate ring of a toric variety is multigraded by relations
        between generating rays of the underlying fan.

        INPUT:

        - ``polynomial`` -- polynomial in the coordinate ring of ``self`` or
          its quotient.

        OUTPUT:

        - ``True`` if ``polynomial`` is homogeneous and ``False`` otherwise.

        EXAMPLES:

        We will use the product of two projective lines with coordinates
        `(x, y)` for one and `(s, t)` for the other::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: fan.ray_matrix()
            [ 1  0 -1  0]
            [ 0  1  0 -1]
            sage: P1xP1 = ToricVariety(fan, "x s y t")
            sage: P1xP1.inject_variables()
            Defining x, s, y, t
            sage: P1xP1.is_homogeneous(x - y)
            True
            sage: P1xP1.is_homogeneous(x*s + y*t)
            True
            sage: P1xP1.is_homogeneous(x - t)
            False
        """
        if "_relation_matrix" not in self.__dict__:
            m = self.fan().ray_matrix().transpose().kernel().matrix()
            # We ignore degrees of torus factor coordinates
            m = m.augment(matrix(m.nrows(), self._torus_factor_dim))
            self._relation_matrix = m
        relation_matrix = self._relation_matrix
        if polynomial not in self.coordinate_ring():
            # Then it should be in the quotient corresponding to a subscheme
            polynomial = polynomial.lift()
        monomials = polynomial.monomials()
        if not monomials:
            return True
        degree = relation_matrix * vector(monomials[0].degrees())
        for monomial in monomials:
            if relation_matrix * vector(monomial.degrees()) != degree:
                return False
        return True

    def is_isomorphic(self, another):
        r"""
        Check if ``self`` is isomorphic to ``another``.

        INPUT:

        - ``another`` - :class:`toric variety <ToricVariety_field>`.

        OUTPUT:

        - ``True`` if ``self`` and ``another`` are isomorphic,
          ``False`` otherwise.

        EXAMPLES::

            sage: fan1 = FaceFan(lattice_polytope.octahedron(2))
            sage: TV1 = ToricVariety(fan1)
            sage: fan2 = NormalFan(lattice_polytope.octahedron(2))
            sage: TV2 = ToricVariety(fan2)

        Only the most trivial case is implemented so far::

            sage: TV1.is_isomorphic(TV1)
            True
            sage: TV1.is_isomorphic(TV2)
            Traceback (most recent call last):
            ...
            NotImplementedError:
            isomorphism check is not yet implemented!
        """
        if self is another:
            return True
        if not is_ToricVariety(another):
            raise TypeError(
                "only another toric variety can be checked for isomorphism! "
                "Got %s" % another)
        raise NotImplementedError("isomorphism check is not yet implemented!")

    def is_complete(self):
        r"""
        Check if ``self`` is complete.

        OUTPUT:

        - ``True`` if ``self`` is complete and ``False`` otherwise.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1.is_complete()
            True
            sage: P1xP1.affine_patch(0).is_complete()
            False
        """
        return self.fan().is_complete()

    def is_orbifold(self):
        r"""
        Check if ``self`` has only quotient singularities.

        OUTPUT:

        - ``True`` if ``self`` has at most quotient singularities by
          finite groups, ``False`` otherwise.

        EXAMPLES::

            sage: fan1 = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan1)
            sage: P1xP1.is_orbifold()
            True
            sage: fan2 = NormalFan(lattice_polytope.octahedron(3))
            sage: TV = ToricVariety(fan2)
            sage: TV.is_orbifold()
            False
        """
        return self.fan().is_simplicial()

    def is_smooth(self):
        r"""
        Check if ``self`` is smooth.

        OUTPUT:

        - ``True`` if ``self`` is smooth and ``False`` otherwise.

        EXAMPLES::

            sage: diamond = lattice_polytope.octahedron(2)
            sage: fan1 = FaceFan(diamond)
            sage: P1xP1 = ToricVariety(fan1)
            sage: P1xP1.is_smooth()
            True
            sage: fan2 = NormalFan(lattice_polytope.octahedron(2))
            sage: TV = ToricVariety(fan2)
            sage: TV.is_smooth()
            False
        """
        return self.fan().is_smooth()

    def Kaehler_cone(self):
        r"""
        Return the closure of the Kähler cone of ``self``.

        OUTPUT:

        - :class:`cone <sage.geometry.cone.ConvexRationalPolyhedralCone>`.

        .. NOTE::

            This cone sits in the rational divisor class group of ``self`` and
            the choice of coordinates agrees with
            :meth:`rational_class_group`.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: Kc = P1xP1.Kaehler_cone()
            sage: Kc
            2-d cone in 2-d lattice
            sage: Kc.rays()
            (Divisor class [0, 1], Divisor class [1, 0])
            sage: [ divisor_class.lift() for divisor_class in Kc.rays() ]
            [V(z1), V(z0)]
            sage: Kc.lattice()
            The toric rational divisor class group
            of a 2-d toric variety covered by 4 affine patches
        """
        if "_Kaehler_cone" not in self.__dict__:
            fan = self.fan()
            GT = fan.Gale_transform().columns()
            n = fan.nrays()
            K = None
            for cone in fan:
                sigma = Cone([GT[i] for i in range(n)
                                    if i not in cone.ambient_ray_indices()],
                             lattice = self.rational_class_group())
                K = K.intersection(sigma) if K is not None else sigma
            self._Kaehler_cone = K
        return self._Kaehler_cone

    def Mori_cone(self):
        """
        Returns the Mori cone of ``self``.

        OUTPUT:

        - :class:`cone <sage.geometry.cone.ConvexRationalPolyhedralCone>`.

        .. NOTE::

            * The Mori cone is dual to the Kähler cone.

            * We think of the Mori cone as living inside the row span of the
              Gale transform matrix (computed by
              ``self.fan().Gale_transform()``).

            * The points in the Mori cone are the effective curves in the
              variety.

            * The ``i``-th entry in each Mori vector is the intersection
              number of the curve corresponding to the generator of the
              ``i``-th ray of the fan with the corresponding divisor class.
              The very last entry is associated to the orgin of the fan
              lattice.

            * The Mori vectors are also known as the gauged linear sigma model
              charge vectors.

        EXAMPLES::

            sage: P4_11169 = toric_varieties.P4_11169_resolved()
            sage: P4_11169.Mori_cone()
            2-d cone in 7-d lattice
            sage: P4_11169.Mori_cone().rays()
            ((3, 2, 0, 0, 0, 1, -6), (0, 0, 1, 1, 1, -3, 0))
        """
        if "_Mori_cone" not in self.__dict__:
            # Ideally, self.Kaehler_cone().dual() should be it, but
            # so far this is not the case.
            rays = (ray * self._fan.Gale_transform()
                    for ray in self.Kaehler_cone().dual().rays())
            self._Mori_cone = Cone(rays, lattice=ZZ**(self._fan.nrays()+1))
        return self._Mori_cone

    def plot(self, **options):
        r"""
        Plot ``self``, i.e. the corresponding fan.

        INPUT:

        - any options for toric plots (see :func:`toric_plotter.options
          <sage.geometry.toric_plotter.options>`), none are mandatory.

        OUTPUT:

        - a plot.

        .. NOTE::

            The difference between ``X.plot()`` and ``X.fan().plot()`` is that
            in the first case default ray labels correspond to variables of
            ``X``.

        EXAMPLES::

            sage: X = toric_varieties.Cube_deformation(4)
            sage: X.plot()
        """
        if "ray_label" not in options:
            gens = self.coordinate_ring().gens()
            if self.fan().lattice().degree() <= 2:
                options["ray_label"] = ["$%s$" % latex(z) for z in gens]
            else:
                options["ray_label"] = [str(z) for z in gens]
        return self.fan().plot(**options)

    def rational_class_group(self):
        r"""
        Return the rational divisor class group of ``self``.

        Let `X` be a toric variety.

        The **Weil divisor class group** `\mathop{Cl}(X)` is a finitely
        generated abelian group and can contain torsion. Its rank equals the
        number of rays in the fan of `X` minus the dimension of `X`.

        The **rational divisor class group** is
        `\mathop{Cl}(X) \otimes_\ZZ \QQ` and never includes torsion. If `X` is
        *smooth*, this equals the **Picard group** of `X`, whose elements are
        the isomorphism classes of line bundles on `X`. The group law (which
        we write as addition) is the tensor product of the line bundles. The
        Picard group of a toric variety is always torsion-free.

        OUTPUT:

        - :class:`rational divisor class group
          <sage.schemes.generic.toric_divisor.ToricRationalDivisorClassGroup>`.

        .. NOTE::

            * Coordinates correspond to the rows of
              ``self.fan().gale_transform()``.

            * :meth:`Kaehler_cone` yields a cone in this group.

        EXAMPLES::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: P1xP1 = ToricVariety(fan)
            sage: P1xP1.rational_class_group()
            The toric rational divisor class group
            of a 2-d toric variety covered by 4 affine patches
        """
        from sage.schemes.generic.toric_divisor import ToricRationalDivisorClassGroup
        return ToricRationalDivisorClassGroup(self)

    def resolve(self, **kwds):
        r"""
        Construct a toric variety whose fan subdivides the fan of ``self``.

        The name of this function reflects the fact that usually such
        subdivisions are done for resolving singularities of the original
        variety.

        INPUT:

        This function accepts only keyword arguments, none of which are
        mandatory.

        - ``coordinate_names`` -- names for coordinates of the new variety. If
          not given, will be constructed from the coordinate names of ``self``
          and necessary indexed ones. See :func:`normalize_names` for the
          description of acceptable formats;

        - ``coordinate_indices`` -- coordinate indices which should be used
          for indexed variables of the new variety;

        - all other arguments will be passed to
          :meth:`~sage.geometry.fan.RationalPolyhedralFan.subdivide` method of
          the underlying :class:`rational polyhedral fan
          <sage.geometry.fan.RationalPolyhedralFan>`, see its documentation
          for the available options.

        OUTPUT:

        - :class:`toric variety <ToricVariety_field>`.

        EXAMPLES:

        First we will "manually" resolve a simple orbifold singularity::

            sage: cone = Cone([(1,1), (-1,1)])
            sage: fan = Fan([cone])
            sage: TV = ToricVariety(fan)
            sage: TV.is_smooth()
            False
            sage: TV_res = TV.resolve(new_rays=[(0,1)])
            sage: TV_res.is_smooth()
            True
            sage: TV_res.fan().ray_matrix()
            [ 1 -1  0]
            [ 1  1  1]
            sage: [cone.ambient_ray_indices() for cone in TV_res.fan()]
            [(0, 2), (1, 2)]

        Now let's "automatically" partially resolve a more complicated fan::

            sage: fan = NormalFan(lattice_polytope.octahedron(3))
            sage: TV = ToricVariety(fan)
            sage: TV.is_smooth()
            False
            sage: TV.is_orbifold()
            False
            sage: TV.fan().nrays()
            8
            sage: TV.fan().ngenerating_cones()
            6
            sage: TV_res = TV.resolve(make_simplicial=True)
            sage: TV_res.is_smooth()
            False
            sage: TV_res.is_orbifold()
            True
            sage: TV_res.fan().nrays()
            8
            sage: TV_res.fan().ngenerating_cones()
            12
            sage: TV.gens()
            (z0, z1, z2, z3, z4, z5, z6, z7)
            sage: TV_res.gens()
            (z0, z1, z2, z3, z4, z5, z6, z7)
            sage: TV_res = TV.resolve(coordinate_names="x+",
            ...                       make_simplicial=True)
            sage: TV_res.gens()
            (x0, x1, x2, x3, x4, x5, x6, x7)
        """
        # If you are changing this function, check out resolve in Fano toric
        # varieties to see if it should be changed too
        #
        # Currently the resolution of fans works for full-dimensional ones
        # only, so there is no point to deal with the general case here, since
        # we will not be able to check that it works.
        coordinate_names = kwds.pop("coordinate_names", None)
        coordinate_indices = kwds.pop("coordinate_indices", None)
        fan = self.fan()
        if fan.dim() != fan.lattice_dim():
            raise NotImplementedError("resolution of toric varieties with "
                                      "torus factors is not yet implemented!")
            # When it is implemented, should be careful with the torus factor
        rfan = fan.subdivide(**kwds)
        if coordinate_names is None:
            coordinate_names = list(self.variable_names())
            if coordinate_indices is None:
                coordinate_indices = range(fan.nrays(), rfan.nrays())
            else:
                coordinate_indices = coordinate_indices[fan.nrays():]
            coordinate_names.extend(normalize_names(
                                    ngens=rfan.nrays() - fan.nrays(),
                                    indices=coordinate_indices,
                                    prefix=self._coordinate_prefix))
            coordinate_names.append(self._coordinate_prefix + "+")
        resolution = ToricVariety(rfan, coordinate_names=coordinate_names,
                                  coordinate_indices=coordinate_indices,
                                  base_field=self.base_ring())
        R = self.coordinate_ring()
        R_res = resolution.coordinate_ring()
        resolution_map = resolution.hom(R.hom(R_res.gens()[:R.ngens()]), self)
        resolution._resolution_map = resolution_map
        # The above map does not have (yet) public methods to access it.
        # While this map is defined correctly, base classes of schemes and
        # morphisms do not treat it as they should. The plan is to fix this
        # situation soon and to be able to use this map!
        return resolution

    def resolve_to_orbifold(self, **kwds):
        r"""
        Construct an orbifold whose fan subdivides the fan of ``self``.

        It is a synonym for :meth:`resolve` with ``make_simplicial=True``
        option.

        INPUT:

        - this function accepts only keyword arguments. See :meth:`resolve`
          for documentation.

        OUTPUT:

        - :class:`toric variety <ToricVariety_field>`.

        EXAMPLES::

            sage: fan = NormalFan(lattice_polytope.octahedron(3))
            sage: TV = ToricVariety(fan)
            sage: TV.is_orbifold()
            False
            sage: TV.fan().nrays()
            8
            sage: TV.fan().ngenerating_cones()
            6
            sage: TV_res = TV.resolve_to_orbifold()
            sage: TV_res.is_orbifold()
            True
            sage: TV_res.fan().nrays()
            8
            sage: TV_res.fan().ngenerating_cones()
            12
        """
        return self.resolve(make_simplicial=True, **kwds)

    def subscheme(self, polynomials):
        r"""
        Return the subscheme of ``self`` defined by ``polynomials``.

        INPUT:

        - ``polynomials`` -- list of polynomials in the coordinate ring of
          ``self``.

        OUTPUT:

        - :class:`subscheme of a toric variety
          <sage.schemes.genreric.algebraic_scheme.AlgebraicScheme_subscheme_toric>`.

        EXAMPLES:

        We will construct a subscheme of the product of two projective lines
        with coordinates `(x, y)` for one and `(s, t)` for the other::

            sage: fan = FaceFan(lattice_polytope.octahedron(2))
            sage: fan.ray_matrix()
            [ 1  0 -1  0]
            [ 0  1  0 -1]
            sage: P1xP1 = ToricVariety(fan, "x s y t")
            sage: P1xP1.inject_variables()
            Defining x, s, y, t
            sage: X = P1xP1.subscheme([x*s + y*t, x^3+y^3])
            sage: X
            Closed subscheme of 2-d toric variety
            covered by 4 affine patches defined by:
              x*s + y*t,
              x^3 + y^3
            sage: X.defining_polynomials()
            (x*s + y*t, x^3 + y^3)
            sage: X.defining_ideal()
            Ideal (x*s + y*t, x^3 + y^3)
            of Multivariate Polynomial Ring in x, s, y, t
            over Rational Field
            sage: X.base_ring()
            Rational Field
            sage: X.base_scheme()
            Spectrum of Rational Field
            sage: X.structure_morphism()
            Scheme morphism:
              From: Closed subscheme of
              2-d toric variety covered by 4 affine patches defined by:
              x*s + y*t,
              x^3 + y^3
              To:   Spectrum of Rational Field
              Defn: Structure map
        """
        from sage.schemes.generic.algebraic_scheme import AlgebraicScheme_subscheme_toric
        return AlgebraicScheme_subscheme_toric(self, polynomials)

    def Stanley_Reisner_ideal(self):
        """
        Return the Stanley-Reisner ideal.

        OUTPUT:

        - The Stanley-Reisner ideal in the polynomial ring over
          `\QQ` generated by the homogeneous coordinates.

        EXAMPLES::

            sage: fan = Fan([[0,1,3],[3,4],[2,0],[1,2,4]], [(-3, -2, 1), (0, 0, 1), (3, -2, 1), (-1, -1, 1), (1, -1, 1)])
            sage: X = ToricVariety(fan, coordinate_names='A B C D E', base_field=GF(5))
            sage: SR = X.Stanley_Reisner_ideal(); SR
            Ideal (A*E, C*D, A*B*C, B*D*E) of Multivariate Polynomial Ring in A, B, C, D, E over Rational Field
        """
        if "_SR" not in self.__dict__:
            R = PolynomialRing(QQ, self.variable_names())
            self._SR = self._fan.Stanley_Reisner_ideal(R)
        return self._SR

    def linear_equivalence_ideal(self):
        """
        Return the ideal generated by linear relations

        OUTPUT:

        - The ideal generated by the linear relations of the rays in
          the polynomial ring over `\QQ` generated by the homogeneous
          coordinates.

        EXAMPLES::

            sage: fan = Fan([[0,1,3],[3,4],[2,0],[1,2,4]], [(-3, -2, 1), (0, 0, 1), (3, -2, 1), (-1, -1, 1), (1, -1, 1)])
            sage: X = ToricVariety(fan, coordinate_names='A B C D E', base_field=GF(5))
            sage: lin = X.linear_equivalence_ideal(); lin
            Ideal (-3*A + 3*C - D + E, -2*A - 2*C - D - E, A + B + C + D + E) of Multivariate Polynomial Ring in A, B, C, D, E over Rational Field
        """
        if "_linear_equivalence_ideal" not in self.__dict__:
            R = PolynomialRing(QQ, self.variable_names())
            self._linear_equivalence_ideal = self._fan.linear_equivalence_ideal(R)
        return self._linear_equivalence_ideal

    def cohomology_ring(self):
        r"""
        Return the cohomology ring of the toric variety.

        OUTPUT:

        - If the toric variety is is over `\CC` and has at most finite
          orbifold singularities: `H^\bullet(X,\QQ)` as a polynomial
          quotient ring.

        - Other cases are not handled yet.

        .. NOTE::

            - Toric varieties over any field of characteristic 0 are
              treated as if they were varieties over `\CC`.

            - The integral cohomology of smooth toric varieties is
              torsion-free, so in this case there is no loss of
              information when going to rational coefficients.

            - ``self.cohomology_ring().gen(i)`` is the divisor class generated by
              the ``i``-th ray of the fan.

        EXAMPLES::

            sage: X = toric_varieties.dP6()
            sage: X.cohomology_ring()
            Rational cohomology ring of a 2-d CPR-Fano toric variety covered by 6 affine patches
            sage: X.cohomology_ring().defining_ideal()
            Ideal (-u - y + z + w, x - y - v + w, x*y, x*v, x*z, u*v, u*z, u*w, y*z, y*w, v*w) of Multivariate Polynomial Ring in x, u, y, v, z, w over Rational Field
            sage: X.cohomology_ring().defining_ideal().ring()
            Multivariate Polynomial Ring in x, u, y, v, z, w over Rational Field
            sage: X.variable_names()
            ('x', 'u', 'y', 'v', 'z', 'w')
            sage: X.cohomology_ring().gens()
            ([y + v - w], [-y + z + w], [y], [v], [z], [w])
        """
        if "_cohomology_ring" not in self.__dict__:
            if self.base_ring().characteristic()>0:
                raise NotImplementedError('Only characteristic 0 base fields '
                                          'are implemented.')
            self._cohomology_ring = CohomologyRing(self)
        return self._cohomology_ring

    def cohomology_basis(self, d=None):
        r"""
        Return a basis for the cohomology of the toric variety.

        INPUT:

        - ``d`` (optional) -- integer.

        OUTPUT:

        - Without the optional argument, a list whose d-th entry is a
          basis for `H^{2d}(X,\QQ)`

        - If the argument is an integer ``d``, returns basis for
          `H^{2d}(X,\QQ)`

        EXAMPLES::

            sage: X = toric_varieties.dP8()
            sage: X.cohomology_basis()
            (([1],), ([z], [y]), ([y*z],))
            sage: X.cohomology_basis(1)
            ([z], [y])
            sage: X.cohomology_basis(dimension(X))[0] == X.volume_class()
            True
        """
        if d!=None:
            return self.cohomology_basis()[d]

        try:
            return self._cohomology_basis
        except AttributeError:
            pass
        H = self.cohomology_ring()
        # Make an empty list for each d-piece
        basis = [[] for d in range(self.dimension() + 1)]
        # Distribute basis elements into d-pieces
        for x in H.defining_ideal().normal_basis():
            basis[x.total_degree()].append(x)
        # Convert list of lists of polynomials to
        # tuple of tuples of cohomology classes
        basis = tuple(tuple(H(x) for x in dbasis)
                      for dbasis in basis)
        self._cohomology_basis = basis
        return self._cohomology_basis

    def volume_class(self):
        """
        Return the cohomology class of the volume form on the toric
        variety.

        If the variety is non-compact: Note that we are using
        cohomology with compact supports. This is dual to homology
        without any support condition. In particular, for non-compact
        varieties the volume form `\mathrm{dVol}=\wedge_i(dx_i \wedge
        dy_i)` does not define a cohomology class.

        OUTPUT:

        A :class:`CohomologyClass`. If it exists, it is the class of
        the (properly normalized) volume form, that is, it is the
        Poincare dual of a single point. If it does not exist, a
        ``ValueError`` is raised.

        EXAMPLES::

            sage: P2 = toric_varieties.P2()
            sage: P2.volume_class()
            [z^2]
            sage: A2_Z2 = toric_varieties.A2_Z2()
            sage: A2_Z2.volume_class()
            Traceback (most recent call last):
            ...
            ValueError: Volume class does not exist.
        """
        if "_volume_class" not in self.__dict__:
            if not self.is_orbifold():
                raise NotImplementedError('Cohomology computations are only '
                                          'implemented for orbifolds.')
            def V(cone): return abs(cone.ray_matrix().determinant())
            min_cone = min( self._fan.generating_cones(), key=V)
            self._volume_class = self.cohomology_ring()(min_cone) / V(min_cone)
        if self._volume_class.is_zero():
            raise ValueError, 'Volume class does not exist.'
        return self._volume_class

    def integrate(self, cohomology_class):
        """
        Integrate a cohomology class over the toric variety.

        INPUT:

        - ``cohomology_class`` -- A cohomology class given as a
          polynomial in ``self.cohomology_ring()``

        OUTPUT:

        The integral of the cohomology class over the variety. The
        volume normalization is given by :meth:`volume_class`, that
        is, ``self.integrate(self.volume_class())`` is always one (if
        the volume class exists).

        EXAMPLES::

            sage: dP6 = toric_varieties.dP6()
            sage: HH = dP6.cohomology_ring()
            sage: D = [ HH(c) for c in dP6.fan(dim=1) ]
            sage: matrix([ [ D[i]*D[j] for i in range(0,6) ] for j in range(0,6) ])
            [ [w^2] [-w^2]    [0]    [0]    [0] [-w^2]]
            [[-w^2]  [w^2] [-w^2]    [0]    [0]    [0]]
            [   [0] [-w^2]  [w^2] [-w^2]    [0]    [0]]
            [   [0]    [0] [-w^2]  [w^2] [-w^2]    [0]]
            [   [0]    [0]    [0] [-w^2]  [w^2] [-w^2]]
            [[-w^2]    [0]    [0]    [0] [-w^2]  [w^2]]
            sage: matrix([ [ dP6.integrate(D[i]*D[j]) for i in range(0,6) ] for j in range(0,6) ])
            [-1  1  0  0  0  1]
            [ 1 -1  1  0  0  0]
            [ 0  1 -1  1  0  0]
            [ 0  0  1 -1  1  0]
            [ 0  0  0  1 -1  1]
            [ 1  0  0  0  1 -1]
        """
        assert self.is_complete(), "Can only integrate over compact varieties."
        top_form = cohomology_class.part_of_degree(self.dimension())
        if top_form.is_zero(): return 0
        return top_form.lc() / self.volume_class().lc()

    def Chern_class(self, deg=None):
        """
        Return Chern classes of the (tangent bundle of the) toric variety.

        INPUT:

        - ``deg`` -- integer (optional). The degree of the Chern class.

        OUTPUT:

        - If the degree is specified, the ``deg``-th Chern class.

        - If no degree is specified, the total Chern class.

        REFERENCES:

        ..

            http://en.wikipedia.org/wiki/Chern_class

        EXAMPLES::

            sage: X = toric_varieties.dP6()
            sage: X.Chern_class()
            [-6*w^2 + y + 2*v + 2*z + w + 1]
            sage: X.c()
            [-6*w^2 + y + 2*v + 2*z + w + 1]
            sage: X.c(1)
            [y + 2*v + 2*z + w]
            sage: X.c(2)
            [-6*w^2]
            sage: X.integrate( X.c(2) )
            6
            sage: X.integrate( X.c(2) ) == X.Euler_number()
            True
        """
        assert self.is_orbifold(), "Requires the toric variety to be an orbifold."
        try:
            c = self._chern_class
        except AttributeError:
            c = prod([ 1+self.cohomology_ring().gen(i) for i in range(0,self._fan.nrays()) ])
            self._chern_class = c

        if deg==None:
            return c
        else:
            return c.part_of_degree(deg)

    def Chern_character(self, deg=None):
        """
        Return the Chern character (of the tangent bundle) of the toric
        variety.

        INPUT:

        - ``deg`` -- integer (optional). The degree of the Chern
          character.

        OUTPUT:

        - If the degree is specified, the degree-``deg`` part of the
          Chern character.

        - If no degree is specified, the total Chern character.

        REFERENCES:

        ..

            http://en.wikipedia.org/wiki/Chern_character#The_Chern_character

        EXAMPLES::

            sage: dP6 = toric_varieties.dP6()
            sage: dP6.Chern_character()
            [3*w^2 + y + 2*v + 2*z + w + 2]
            sage: dP6.ch()
            [3*w^2 + y + 2*v + 2*z + w + 2]
            sage: dP6.ch(1) == dP6.c(1)
            True
        """
        assert self.is_orbifold(), "Requires the toric variety to be an orbifold."
        try:
            ch = self._chern_character
        except AttributeError:
            n_rels = self._fan.nrays() - self.dimension()
            ch = sum([ self.cohomology_ring().gen(i).exp()
                       for i in range(0,self._fan.nrays()) ]) - n_rels
            self._chern_character = ch

        if deg==None:
            return ch
        else:
            return ch.part_of_degree(deg)

    def Todd_class(self, deg=None):
        """
        Return the Todd class (of the tangent bundle) of the toric variety.

        INPUT:

        - ``deg`` -- integer (optional). The desired degree part.

        OUTPUT:

        - If the degree is specified, the degree-``deg`` part of the
          Todd class.

        - If no degree is specified, the total Todd class.

        REFERENCES:

        ..

            http://en.wikipedia.org/wiki/Todd_class

        EXAMPLES::

            sage: dP6 = toric_varieties.dP6()
            sage: dP6.Todd_class()
            [-w^2 + 1/2*y + v + z + 1/2*w + 1]
            sage: dP6.Td()
            [-w^2 + 1/2*y + v + z + 1/2*w + 1]
            sage: dP6.integrate( dP6.Td() )
            1
        """
        try:
            Td = self._Todd
        except AttributeError:
            Td = QQ(1)
            if self.dimension() >= 1:
                c1 = self.Chern_class(1)
                Td += QQ(1)/2 * c1
            if self.dimension() >= 2:
                c2 = self.Chern_class(2)
                Td += QQ(1)/12 * (c1**2 + c2)
            if self.dimension() >= 3:
                Td += QQ(1)/24 * c1*c2
            if self.dimension() >= 4:
                c3 = self.Chern_class(3)
                c4 = self.Chern_class(4)
                Td += -QQ(1)/720 * (c1**4 -4*c1**2*c2 -3*c2**2 -c1*c3 +c4)
            if self.dimension() >= 5:
                raise NotImplemented, 'Todd class is currently only implemented up to degree 4'
            self._Todd = Td

        if deg==None:
            return Td
        else:
            return Td.part_of_degree(deg)

    c = Chern_class
    ch = Chern_character
    Td = Todd_class

    def Euler_number(self):
        """
        Return the topological Euler number of the toric variety.

        Sometimes, this is also called the Euler
        characteristic. :meth:`chi` is a synonym for
        :meth:`Euler_number`.

        REFERENCES:

        ..

            http://en.wikipedia.org/wiki/Euler_characteristic

        EXAMPLES::

            sage: P1xP1 = toric_varieties.P1xP1()
            sage: P1xP1.Euler_number()
            4
            sage: P1xP1.chi()
            4
        """
        if "_chi" not in self.__dict__:
            if self.is_complete():
                chi = self.integrate(self.Chern_class())
            else:
                chi=0
                H = self.cohomology_basis()
                for d in range(0, self.dimension()+1):
                    chi += (-1)**d * len(H[d])
            self._chi = chi
        return self._chi

    chi = Euler_number

    def K(self):
        r"""
        Returns the canonical divisor of the toric variety.

        EXAMPLES:

        Lets test that the del Pezzo surface `dP_6` has degree 6, as its name implies::

            sage: dP6 = toric_varieties.dP6()
            sage: HH = dP6.cohomology_ring()
            sage: dP6.K()
            -V(x) - V(u) - V(y) - V(v) - V(z) - V(w)
            sage: dP6.integrate( HH(dP6.K())^2 )
            6
        """
        from sage.schemes.generic.toric_divisor import ToricDivisor
        return ToricDivisor(self, [-1]*self._fan.nrays())

    def divisor(self, arg, base_ring=None, check=True, reduce=True):
        r"""
        Return a divisor.

        INPUT:

        The arguments are the same as in
        :func:`sage.schemes.generic.toric_divisor.ToricDivisor`.

        OUTPUT:

        - A :class:`sage.schemes.generic.toric_divisor.ToricDivisor_generic`

        EXAMPLES::

            sage: dP6 = toric_varieties.dP6()
            sage: dP6.coordinate_ring()
            Multivariate Polynomial Ring in x, u, y, v, z, w over Rational Field
            sage: dP6.divisor(0)
            V(x)
            sage: for i in range(0,dP6.fan().nrays()): print dP6.divisor(i), ': generated by ray', dP6.fan().ray(i)
            ...
            V(x) : generated by ray N(0, 1)
            V(u) : generated by ray N(-1, 0)
            V(y) : generated by ray N(-1, -1)
            V(v) : generated by ray N(0, -1)
            V(z) : generated by ray N(1, 0)
            V(w) : generated by ray N(1, 1)
        """
        from sage.schemes.generic.toric_divisor import ToricDivisor
        return ToricDivisor(self, ring=base_ring, arg=arg, check=check, reduce=reduce)

    def divisor_group(self, base_ring=ZZ):
        r"""
        Return the group of Weil divisors.

        INPUT:

        - ``base_ring`` -- the coefficient ring, usually ``ZZ``
          (default) or ``QQ``.

        OUTPUT:

        The (free abelian) group of Cartier divisors, that is, formal
        linear combinations of polynomial equations over the
        coefficient ring ``base_ring``.

        These need not be toric (=defined by monomials), but allow
        general polynomials. The output will be an instance of
        :class:`sage.schemes.generic.divisor_group.DivisorGroup_generic`.

        .. WARNING::

            You almost certainly want the group of toric divisors, see
            :meth:`toric_divisor_group`. The toric divisor group is
            generated by the rays of the fan. The general divisor
            group has no toric functionality implemented.

        EXAMPLES:

            sage: dP6 = toric_varieties.dP6()
            sage: Div = dP6.divisor_group(); Div
            Group of ZZ-Divisors on 2-d CPR-Fano toric variety
            covered by 6 affine patches
            sage: Div(x)
            V(x)
        """
        from sage.schemes.generic.divisor_group import DivisorGroup
        return DivisorGroup(self, base_ring)

    def toric_divisor_group(self, base_ring=ZZ):
        r"""
        Return the group of toric (T-Weil) divisors.

        INPUT:

        - ``base_ring`` -- the coefficient ring, usually ``ZZ``
          (default) or ``QQ``.

        OUTPUT:

        The free Abelian agroup of toric Weil divisors, that is,
        formal ``base_ring``-linear combinations of codimension-one
        toric subvarieties. The output will be an instance of
        :class:`sage.schemes.generic.toric_divisor.ToricDivisorGroup`.

        The `i`-th generator of the divisor group is the divisor where
        the `i`-th homogeneous coordinate vanishes, `\{z_i=0\}`.

        EXAMPLES::

            sage: dP6 = toric_varieties.dP6()
            sage: TDiv = dP6.toric_divisor_group(); TDiv
            Group of toric ZZ-Weil divisors on 2-d CPR-Fano toric variety
            covered by 6 affine patches
            sage: TDiv == dP6.toric_divisor_group()
            True
            sage: TDiv.gens()
            (V(x), V(u), V(y), V(v), V(z), V(w))
            sage: dP6.coordinate_ring()
            Multivariate Polynomial Ring in x, u, y, v, z, w over Rational Field
        """
        from sage.schemes.generic.toric_divisor import ToricDivisorGroup
        return ToricDivisorGroup(self, base_ring);



def normalize_names(names=None, ngens=None, prefix=None, indices=None,
                    return_prefix=False):
    r"""
    Return a list of names in the standard form.

    INPUT:

    All input parameters are optional.

    - ``names`` -- names given either as a single string (with individual
      names separated by commas or spaces) or a list of strings with each
      string specifying a name. If the last name ends with the plus sign,
      "+", this name will be used as ``prefix`` (even if ``prefix`` was
      given explicitly);

    - ``ngens`` -- number of names to be returned;

    - ``prefix`` -- prefix for the indexed names given as a string;

    - ``indices`` -- list of integers (default: ``range(ngens)``) used as
      indices for names with ``prefix``. If given, must be of length
      ``ngens``;

    - ``return_prefix`` -- if ``True``, the last element of the returned list
      will contain the prefix determined from ``names`` or given as the
      parameter ``prefix``. This is useful if you may need more names in the
      future.

    OUTPUT:

    - list of names given as strings.

    These names are constructed in the following way:

    #. If necessary, split ``names`` into separate names.
    #. If the last name ends with "+", put it into ``prefix``.
    #. If ``ngens`` was given, add to the names obtained so far as many
       indexed names as necessary to get this number. If the ``k``-th name of
       the *total* list of names is indexed, it is
       ``prefix + str(indices[k])``. If there were already more names than
       ``ngens``, discard "extra" ones.
    #. Check if constructed names are valid. See :func:`certify_names` for
       details.
    #. If the option ``return_prefix=True`` was given, add ``prefix`` to the
       end of the list.

    EXAMPLES:

    As promised, all parameters are optional::

        sage: from sage.schemes.generic.toric_variety import normalize_names
        sage: normalize_names()
        []

    One of the most common uses is probably this one::

        sage: normalize_names("x+", 4)
        ['x0', 'x1', 'x2', 'x3']

    Now suppose that you want to enumerate your variables starting with one
    instead of zero::

        sage: normalize_names("x+", 4, indices=range(1,5))
        ['x1', 'x2', 'x3', 'x4']

    You may actually have an arbitrary enumeration scheme::

        sage: normalize_names("x+", 4, indices=[1, 10, 100, 1000])
        ['x1', 'x10', 'x100', 'x1000']

    Now let's add some "explicit" names::

        sage: normalize_names("x y z t+", 4)
        ['x', 'y', 'z', 't3']

    Note that the "automatic" name is ``t3`` instead of ``t0``. This may seem
    weird, but the reason for this behaviour is that the fourth name in this
    list will be the same no matter how many explicit names were given::

        sage: normalize_names("x y t+", 4)
        ['x', 'y', 't2', 't3']

    This is especially useful if you get ``names`` from a user but want to
    specify all default names::

        sage: normalize_names("x, y", 4, prefix="t")
        ['x', 'y', 't2', 't3']

    In this format, the user can easily override your choice for automatic
    names::

        sage: normalize_names("x y s+", 4, prefix="t")
        ['x', 'y', 's2', 's3']

    Let's now use all parameters at once::

        sage: normalize_names("x, y, s+", 4, prefix="t",
        ...       indices=range(1,5), return_prefix=True)
        ['x', 'y', 's3', 's4', 's']

    Note that you still need to give indices for all names, even if some of
    the first ones will be "wasted" because of the explicit names. The reason
    is the same as before - this ensures consistency of automatically
    generated names, no matter how many explicit names were given.

    The prefix is discarded if ``ngens`` was not given::

        sage: normalize_names("alpha, beta, gamma, zeta+")
        ['alpha', 'beta', 'gamma']

    Finally, let's take a look at some possible mistakes::

        sage: normalize_names("123")
        Traceback (most recent call last):
        ...
        ValueError: name must start with a letter! Got 123

    A more subtle one::

        sage: normalize_names("x1", 4, prefix="x")
        Traceback (most recent call last):
        ...
        ValueError: names must be distinct! Got: ['x1', 'x1', 'x2', 'x3']
    """
    if names is None:
        names = []
    elif isinstance(names, str):
        names = names.replace(",", " ").split()
    else:
        try:
            names = list(names)
        except TypeError:
            raise TypeError(
                    "names must be a string or a list or tuple of them!")
        for name in names:
            if not isinstance(name, str):
                raise TypeError(
                    "names must be a string or a list or tuple of them!")
    if names and names[-1].endswith("+"):
        prefix = names.pop()[:-1]
    if ngens is None:
        ngens = len(names)
    if len(names) < ngens:
        if prefix is None:
            raise IndexError("need %d names but only %d are given!"
                             % (ngens, len(names)))
        if indices is None:
            indices = range(ngens)
        elif len(indices) != ngens:
            raise ValueError("need exactly %d indices, but got %d!"
                             % (ngens, len(indices)))
        names += [prefix + str(i) for i in indices[len(names):]]
    if len(names) > ngens:
        names = names[:ngens]
    # Check that all given and constructed names are valid
    certify_names(names)
    if return_prefix:
        names.append(prefix)
    return names


def certify_names(names):
    r"""
    Make sure that ``names`` are valid in Python.

    INPUT:

    - ``names`` -- list of strings.

    OUTPUT:

    - none, but a ``ValueError`` exception is raised if ``names`` are invalid.

    Each name must satisfy the following requirements:

    * Be non-empty.
    * Contain only (Latin) letters, digits, and underscores ("_").
    * Start with a letter.

    In addition, all names must be distinct.

    EXAMPLES::

        sage: from sage.schemes.generic.toric_variety import certify_names
        sage: certify_names([])
        sage: certify_names(["a", "x0", "x_45"])
        sage: certify_names(["", "x0", "x_45"])
        Traceback (most recent call last):
        ...
        ValueError: name must be nonempty!
        sage: certify_names(["a", "0", "x_45"])
        Traceback (most recent call last):
        ...
        ValueError: name must start with a letter! Got 0
        sage: certify_names(["a", "x0", "@_45"])
        Traceback (most recent call last):
        ...
        ValueError: name must be alphanumeric! Got @_45
        sage: certify_names(["a", "x0", "x0"])
        Traceback (most recent call last):
        ...
        ValueError: names must be distinct! Got: ['a', 'x0', 'x0']
    """
    for name in names:
        if not name:
            raise ValueError("name must be nonempty!")
        if not name.isalnum() and not name.replace("_","").isalnum():
            # Must be alphanumeric except for non-leading '_'
            raise ValueError("name must be alphanumeric! Got %s" % name)
        if not name[0].isalpha():
            raise ValueError("name must start with a letter! Got %s" % name)
    if len(set(names)) != len(names):
        raise ValueError("names must be distinct! Got: %s" % names)


#*****************************************************************
class CohomologyRing(QuotientRing_generic, UniqueRepresentation):
    r"""
    The (even) cohomology ring of a toric variety.

    Irregardles of the variety's base ring, we always work with the
    variety over `\CC` and its topology.

    The cohomology is always the singular cohomology with
    `\QQ`-coefficients. Note, however, that the cohomology of smooth
    toric varieties is torsion-free, so there is no loss of
    information in that case.

    Currently, the toric variety must not be "too singular".  See
    :meth:`ToricVariety_field.cohomology_ring` for a detailed
    description of which toric varieties are admissible. For such
    varieties the odd-dimensional cohomology groups vanish.

    .. WARNING::

        You should not create instances of this class manually. Use
        :meth:`ToricVariety_field.cohomology_ring` to generate the
        cohomology ring.

    INPUT:

    - ``variety`` -- a toric variety. Currently, the toric variety
      must be at least an orbifold. See
      :meth:`ToricVariety_field.cohomology_ring` for a detailed
      description of which toric varieties are admissible.

    EXAMPLES::

        sage: P2 = toric_varieties.P2()
        sage: P2.cohomology_ring()
        Rational cohomology ring of a 2-d CPR-Fano toric variety covered by 3 affine patches

    This is equivalent to::

        sage: from sage.schemes.generic.toric_variety import CohomologyRing
        sage: CohomologyRing(P2)
        Rational cohomology ring of a 2-d CPR-Fano toric variety covered by 3 affine patches
    """

    def __init__(self, variety):
        r"""
        See :class:`CohomologyRing` for documentation.

        TESTS::

            sage: P2 = toric_varieties.P2()
            sage: P2.cohomology_ring()
            Rational cohomology ring of a 2-d CPR-Fano toric variety covered by 3 affine patches

        TESTS::

            sage: cone1 = Cone([(1,0)]);  cone2 = Cone([(1,0)])
            sage: cone1 is cone2
            False
            sage: fan1 = Fan([cone1]);  fan2 = Fan([cone2])
            sage: fan1 is fan2
            False
            sage: X1 = ToricVariety(fan1);  X2 = ToricVariety(fan2)
            sage: X1 is X2
            False
            sage: X1.cohomology_ring() is X2.cohomology_ring()   # see http://trac.sagemath.org/sage_trac/ticket/10325
            True
            sage: TDiv = X1.toric_divisor_group()
            sage: X1.toric_divisor_group() is TDiv
            True
            sage: X2.toric_divisor_group() is TDiv
            True
            sage: TDiv.scheme() is X1   # as you expect
            True
            sage: TDiv.scheme() is X2   # perhaps less obvious, but toric_divisor_group is unique!
            False
            sage: TDiv.scheme() == X2   # isomorphic, but not necessarily identical
            True
            sage: TDiv.scheme().cohomology_ring() is X2.cohomology_ring()  # this is where it gets tricky
            True
            sage: TDiv.gen(0).Chern_character() * X2.cohomology_ring().one()
            [1]
        """
        self._variety = variety

        if not variety.is_orbifold():
            raise NotImplementedError, 'Requires an orbifold toric variety.'

        R = PolynomialRing(QQ, variety.variable_names())
        self._polynomial_ring = R

        I = variety._fan.linear_equivalence_ideal(R) + variety._fan.Stanley_Reisner_ideal(R)
        super(CohomologyRing, self).__init__(R, I, names=variety.variable_names())

    def _repr_(self):
        r"""
        Return a string representation of the cohomology ring.

        OUTPUT:

        A string.

        EXAMPLES::

            sage: toric_varieties.P2().cohomology_ring()._repr_()
            'Rational cohomology ring of a 2-d CPR-Fano toric variety covered by 3 affine patches'
        """
        return 'Rational cohomology ring of a '+self._variety._repr_()

    def _latex_(self):
        r"""
        Return a latex representation of the cohomology ring.

        OUTPUT:

        A string.

        EXAMPLES::

            sage: cohomology_ring = toric_varieties.P2().cohomology_ring()
            sage: cohomology_ring._latex_()
            'H^\\ast\\left(\\mathbb{P}_{\\Delta^{2}},\\QQ\\right)'
        """
        return 'H^\\ast\\left('+self._variety._latex_()+',\QQ\\right)'

    def _element_constructor_(self,x):
        r"""
        Construct a :class:`CohomologyClass`.

        INPUT::

        - ``x`` -- something that defines a cohomology class. Either a
          cohomology class, a cone of the fan, or something that can
          be converted into a polynomial in the homogeneous
          coordinates.

        EXAMPLES::

            sage: dP6 = toric_varieties.dP6()
            sage: H = dP6.cohomology_ring()
            sage: cone = dP6.fan().cone_containing(2,3); cone
            2-d cone of Rational polyhedral fan in 2-d lattice N
            sage: H(cone)   # indirect doctest
            [-w^2]
            sage: H( Cone(cone) )
            [-w^2]
            sage: H( dP6.fan(0)[0] )   # trivial cone
            [1]


        Numbers will be converted into the ring::

            sage: P2 = toric_varieties.P2()
            sage: H = P2.cohomology_ring()
            sage: H._element_constructor_(1)
            [1]
            sage: H(1)
            [1]
            sage: type( H(1) )
            <class 'sage.schemes.generic.toric_variety.CohomologyClass'>
            sage: P2.inject_variables()
            Defining x, y, z
            sage: H(1+x*y+z)
            [z^2 + z + 1]
        """
        fan = self._variety.fan()
        if isinstance(x, CohomologyClass) and x.parent()==self:
            return x
        if isinstance(x, QuotientRingElement):
            x = x.lift()
        elif is_Cone(x):
            cone = fan.embed(x)
            assert cone.ambient() is fan
            x = prod((self.cover_ring().gen(i) for i in cone.ambient_ray_indices()),
                     z=self.cover_ring().one())
        else:
            try:
                # divisor, for example, know how to compute their own cohomology class
                return x.cohomology_class()
            except AttributeError:
                # this ensures that rationals are converted to cohomology ring elements
                x = self.cover_ring()(x)
        return CohomologyClass(self, x)

    # We definitely should not override __call__, but since our
    # superclass QuotientRing_generic does not adhere to the coercion
    # model we cannot either. See
    # http://trac.sagemath.org/sage_trac/ticket/9429
    def __call__(self, x, coerce=True):
        r"""
        Turn ``x`` into a ``CohomologyClass``.

        EXAMPLES::

            sage: P2 = toric_varieties.P2()
            sage: H = P2.cohomology_ring()
            sage: H(1)
            [1]
            sage: type( H(1) )
            <class 'sage.schemes.generic.toric_variety.CohomologyClass'>
        """
        return self._element_constructor_(x)

    def gens(self):
        r"""
        Return the generators of the cohomology ring.

        OUTPUT:

        A tuple of generators, one for each toric divisor of the toric
        variety ``X``. The order is the same as the ordering of the
        rays of the fan ``X.fan().rays()``, which is also the same as
        the ordering of the one-cones in ``X.fan(1)``

        EXAMPLES::

            sage: P2 = toric_varieties.P2()
            sage: P2.cohomology_ring().gens()
            ([z], [z], [z])
        """
        if "_gens" not in self.__dict__:
            self._gens = tuple( self.gen(i) for i in range(0,self._variety.fan().nrays()) )
        return self._gens

    def gen(self, i):
        r"""
        Return the generators of the cohomology ring.

        INPUT:

        - ``i`` -- integer.

        OUTPUT:

        The ``i``-th generator of the cohomology ring. If we denote
        the toric variety by ``X``, then this generator is
        associated to the ray ``X.fan().ray(i)``, which spans the
        one-cone ``X.fan(1)[i]``

        EXAMPLES::

            sage: P2 = toric_varieties.P2()
            sage: P2.cohomology_ring().gen(2)
            [z]
        """
        return CohomologyClass(self, self._polynomial_ring.gen(i))


#*****************************************************************
def is_CohomologyClass(x):
    r"""
    Check whether ``x`` is a cohomology class of a toric variety.

    INPUT:

    - ``x`` -- anything.

    OUTPUT:

    ``True`` or ``False`` depending on whether ``x`` is an instance of
    :class:`CohomologyClass`

    EXAMPLES::

        sage: P2 = toric_varieties.P2()
        sage: HH = P2.cohomology_ring()
        sage: from sage.schemes.generic.toric_variety import is_CohomologyClass
        sage: is_CohomologyClass( HH.one() )
        True
        sage: is_CohomologyClass( HH(P2.fan(1)[0]) )
        True
        sage: is_CohomologyClass('z')
        False
    """
    return isinstance(x,CohomologyClass)


#*****************************************************************
class CohomologyClass(QuotientRingElement):
    r"""
    An element of the :class:`CohomologyRing`.

    .. WARNING::

        You should not create instances of this class manually. The
        generators of the cohomology ring as well as the cohomology
        classes associated to cones of the fan can be obtained from
        :meth:`ToricVariety_field.cohomology_ring`.

    EXAMPLES::

        sage: P2 = toric_varieties.P2()
        sage: P2.cohomology_ring().gen(0)
        [z]
        sage: HH = P2.cohomology_ring()
        sage: HH.gen(0)
        [z]
        sage: cone = P2.fan(1)[0];  HH(cone)
        [z]
    """

    def __init__(self, cohomology_ring, representative):
        r"""
        Construct the cohomology class.

        INPUT:

        - ``cohomology_ring`` -- :class:`CohomologyRing`.

        - ``representative`` -- a polynomial in the generators of the cohomology ring.

        OUTPUT:

        An instance of :class:`CohomologyClass`.

        EXAMPLES::

            sage: P2 = toric_varieties.P2()
            sage: H = P2.cohomology_ring()
            sage: from sage.schemes.generic.toric_variety import CohomologyClass
            sage: CohomologyClass(H, H.defining_ideal().ring().zero() )
            [0]
        """
        assert representative in cohomology_ring.defining_ideal().ring(), \
            'The given representative is not in the parent polynomial ring.'
        super(CohomologyClass, self).__init__(cohomology_ring, representative)

    def _repr_(self):
        r"""
        Return a string representation of the cohomology class.

        OUTPUT:

        A string.

        EXAMPLES::

            sage: toric_varieties.P2().cohomology_ring().gen(0)._repr_()
            '[z]'
        """
        return '['+super(CohomologyClass,self)._repr_()+']'

    def _latex_(self):
        r"""
        Return a latex representation of the cohomology class.

        OUTPUT:

        A string.

        EXAMPLES::

            sage: cohomology_class = toric_varieties.P2().cohomology_ring().gen(0)^2/2
            sage: cohomology_class._latex_()
            '\\left[ \\frac{1}{2} z^{2} \\right]'
        """
        return r'\left[ %s \right]' % latex(self.lift())

    def deg(self):
        r"""
        The degree of the cohomology class.

        OUTPUT:

        An integer `d` such that the cohomology class is in degree
        `2d`. If the cohomology class is of mixed degree, the highest
        degree is returned.

        EXAMPLES::

            sage: P2 = toric_varieties.P2()
            sage: P2.cohomology_ring().gen(0).deg()
            1
            sage: P2.cohomology_ring().zero().deg()
            -1
        """
        return self.lift().degree()

    def part_of_degree(self, d):
        r"""
        Project the (mixed-degree) cohomology class to the given degree.

        .. MATH::

            \mathop{pr}\nolimits_d:~ H^\bullet(X_\Delta,\QQ) \to H^{2d}(X_\Delta,\QQ)

        INPUT:

        - An integer ``d``

        OUTPUT:

        - The degree-``2d`` part of the cohomology class.

        EXAMPLES::

            sage: P1xP1 = toric_varieties.P1xP1()
            sage: t = P1xP1.cohomology_ring().gen(0)
            sage: y = P1xP1.cohomology_ring().gen(2)
            sage: 3*t+4*t^2*y+y+t*y+t+1
            [t*y + 4*t + y + 1]
            sage: (3*t+4*t^2*y+y+t*y+t+1).part_of_degree(1)
            [4*t + y]
        """
        Q = self.parent()
        # We iterate over monomials of self.lift()
        p = filter( lambda x: x[1].total_degree() == d, self.lift() )
        if len(p)==0:
            return Q.zero()
        else:
            return Q(sum(x[0]*x[1] for x in p))

    def exp(self):
        """
        Exponentiate ``self``.

        .. NOTE::

            The exponential `\exp(x)` of a rational number `x` is
            usually not rational. Therefore, the cohomology class must
            not have a constant (degree zero) part. The coefficients
            in the Taylor series of `\exp` are rational, so any
            cohomology class without constant term can be
            exponentiated.

        OUTPUT

        The cohomology class `\exp(` ``self`` `)` if the constant part
        vanishes, otherwise a ``ValueError`` is raised.

        EXAMPLES::

            sage: P2 = toric_varieties.P2()
            sage: H_class = P2.cohomology_ring().gen(0)
            sage: H_class
            [z]
            sage: H_class.exp()
            [1/2*z^2 + z + 1]
        """
        if not self.part_of_degree(0).is_zero():
            raise ValueError, 'Must not have a constant part.'
        exp_x = self.parent().one()
        for d in range(1,self.parent()._variety.dimension()+1):
            exp_x += self**d / factorial(d)
        return exp_x
