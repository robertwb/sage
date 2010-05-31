r"""
Convex rational polyhedral cones

This module was designed as a part of framework for toric varieties
(:mod:`~sage.schemes.generic.toric_variety`,
:mod:`~sage.schemes.generic.fano_toric_variety`). While the emphasis is on
strictly convex cones, non-strictly convex cones are supported as well. Work
with distinct lattices (in the sense of discrete subgroups spanning vector
spaces) is supported. The default lattice is :class:`ToricLattice
<sage.geometry.toric_lattice.ToricLatticeFactory>` `N` of the appropriate
dimension. The only case when you must specify lattice explicitly is creation
of a 0-dimensional cone, where dimension of the ambient space cannot be
guessed.

In addition to cones (:class:`ConvexRationalPolyhedralCone`), this module
provides the base class for cones and fans (:class:`IntegralRayCollection`)
and the function for computing Hasse diagrams of finite atomic and coatomic
lattices (in the sense of partially ordered sets where any two elements have
meet and joint) (:func:`hasse_diagram_from_incidences`).

AUTHORS:

- Andrey Novoseltsev (2010-05-13): initial version.

EXAMPLES:

Use :func:`Cone` to construct cones::

    sage: octant = Cone([(1,0,0), (0,1,0), (0,0,1)])
    sage: halfspace = Cone([(1,0,0), (0,1,0), (-1,-1,0), (0,0,1)])
    sage: positive_xy = Cone([(1,0,0), (0,1,0)])
    sage: four_rays = Cone([(1,1,1), (1,-1,1), (-1,-1,1), (-1,1,1)])

For all of the cones above we have provided primitive generating rays, but in
fact this is not necessary - a cone can be constructed from any collection of
rays (from the same space, of course). If there are non-primitive (or even
non-integral) rays, they will be replaced with primitive ones. If there are
extra rays, they will be discarded. Of course, this means that :func:`Cone`
has to do some work before actually constructing the cone and sometimes it is
not desirable, if you know for sure that your input is already "good". In this
case you can use options ``check=False`` to force :func:`Cone` to use
exactly the directions that you have specified and ``normalize=False`` to
force it to use exactly the rays that you have specified. However, it is
better not to use these possibilities without necessity, since cones are
assumed to be represented by a minimal set of primitive generating rays.
See :func:`Cone` for further documentation on construction.

Once you have a cone, you can perfrom numerous operations on it. The most
important ones are, probably, ray accessing methods::

    sage: halfspace.rays()
    (N(0, 0, 1), N(1, 0, 0), N(-1, 0, 0), N(0, 1, 0), N(0, -1, 0))
    sage: halfspace.ray(2)
    N(-1, 0, 0)
    sage: halfspace.ray_matrix()
    [ 0  1 -1  0  0]
    [ 0  0  0  1 -1]
    [ 1  0  0  0  0]
    sage: halfspace.ray_set()
    frozenset([N(1, 0, 0), N(-1, 0, 0), N(0, 1, 0), N(0, 0, 1), N(0, -1, 0)])

If you want to do something with each ray of a cone, you can write ::

    sage: for ray in positive_xy: print ray
    N(1, 0, 0)
    N(0, 1, 0)

You can also get an iterator over only some selected rays::

    sage: for ray in halfspace.ray_iterator([1,2,1]): print ray
    N(1, 0, 0)
    N(-1, 0, 0)
    N(1, 0, 0)

There are two dimensions associated to each cone - the dimension of the
subspace spanned by the cone and the dimension of the ambient space where it
lives::

    sage: positive_xy.dim()
    2
    sage: positive_xy.ambient_dim()
    3

You also may be interested in this dimension::

    sage: dim(positive_xy.linear_subspace())
    0
    sage: dim(halfspace.linear_subspace())
    2

Or, perhaps, all you care about is whether it is zero or not::

    sage: positive_xy.is_strictly_convex()
    True
    sage: halfspace.is_strictly_convex()
    False

You can also perform these checks::

    sage: positive_xy.is_simplicial()
    True
    sage: four_rays.is_simplicial()
    False
    sage: positive_xy.is_smooth()
    True

You can work with subcones that form faces of other cones::

    sage: face = four_rays.faces(dim=2)[0]
    sage: face
    2-dimensional face of 3-dimensional cone
    sage: face.rays()
    (N(1, 1, 1), N(1, -1, 1))
    sage: face.cone_rays()
    (0, 1)
    sage: four_rays.rays(face.cone_rays())
    (N(1, 1, 1), N(1, -1, 1))

If you need to know inclusion relations between faces, use ::

    sage: L = four_rays.face_lattice()
    sage: map(len, L.level_sets())
    [1, 4, 4, 1]
    sage: face = L.level_sets()[2][0]
    sage: face.element.rays()
    (N(1, 1, 1), N(1, -1, 1))
    sage: L.hasse_diagram().neighbors_in(face)
    [1-dimensional face of 3-dimensional cone,
     1-dimensional face of 3-dimensional cone]

When all the functionality provided by cones is not enough, you may want to
check if you can do necessary things using lattice polytopes and polyhedra
corresponding to cones::

    sage: four_rays.lattice_polytope()
    A lattice polytope: 3-dimensional, 5 vertices.
    sage: four_rays.polyhedron()
    A 3-dimensional polyhedron in QQ^3 defined as
    the convex hull of 1 vertex and 4 rays.

And of course you are always welcome to suggest new features that should be
added to cones!
"""

#*****************************************************************************
#       Copyright (C) 2010 Andrey Novoseltsev <novoselt@gmail.com>
#       Copyright (C) 2010 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************


import collections
import copy
import warnings

from sage.combinat.posets.posets import FinitePoset
from sage.geometry.lattice_polytope import LatticePolytope
from sage.geometry.polyhedra import Polyhedron
from sage.geometry.toric_lattice import ToricLattice, is_ToricLattice
from sage.graphs.all import DiGraph
from sage.matrix.all import matrix, identity_matrix
from sage.misc.all import flatten
from sage.modules.all import span, vector
from sage.rings.all import QQ, RR, ZZ, gcd
from sage.structure.all import SageObject
from sage.structure.coerce import parent


def is_Cone(x):
    r"""
    Check if ``x`` is a cone.

    INPUT:

    - ``x`` -- anything.

    OUTPUT:

    - ``True`` if ``x`` is a cone and ``False`` otherwise.

    EXAMPLES::

        sage: from sage.geometry.cone import is_Cone
        sage: is_Cone(1)
        False
        sage: quadrant = Cone([(1,0), (0,1)])
        sage: quadrant
        2-dimensional cone
        sage: is_Cone(quadrant)
        True
    """
    return isinstance(x, ConvexRationalPolyhedralCone)


def Cone(data, lattice=None, check=True, normalize=True):
    r"""
    Construct a (not necessarily strictly) convex rational polyhedral cone.

    INPUT:

    - ``data`` -- one of the following:
        * :class:`~sage.geometry.polyhedra.Polyhedron` object representing
          a valid cone;
        * list of rays. Each ray should be given as a list or a vector
          convertible to the rational extension of the given ``lattice``;

    - ``lattice`` -- :class:`ToricLattice
      <sage.geometry.toric_lattice.ToricLatticeFactory>`, `\ZZ^n`, or any
      other object that behaves like these. If not specified, an attempt will
      be made to determine an appropriate toric lattice automatically;

    - ``check`` -- by default the input data will be checked for correctness
      (e.g. that all rays have the same number of components) and generating
      rays will be constructed from ``data``. If you know that the input is
      a minimal set of generators of a valid cone, you may significantly
      (up to 100 times on simple input) decrease construction time using
      ``check=False`` option;

    - ``normalize`` -- you can further speed up construction using
      ``normalize=False`` option. In this case ``data`` must be a list of
      immutable primitive rays in ``lattice``. In general, you should not use
      this option, it is designed for code optimization and does not give as
      drastic improvement in speed as the previous one.

    OUTPUT:

    - convex rational polyhedral cone determined by ``data``.

    EXAMPLES:

    Let's define a cone corresponding to the first quadrant of the plane
    (note, you can even mix objects of different types to represent rays, as
    long as you let this function to perform all the checks and necessary
    conversions!)::

        sage: quadrant = Cone([(1,0), [0,1]])
        sage: quadrant
        2-dimensional cone
        sage: quadrant.rays()
        (N(1, 0), N(0, 1))

    You may prefer to use :meth:`~IntegralRayCollection.ray_matrix` when you
    want to take a look at rays, they will be given as columns::

        sage: quadrant.ray_matrix()
        [1 0]
        [0 1]

    If you give more rays than necessary, the extra ones will be discarded::

        sage: Cone([(1,0), (0,1), (1,1), (0,1)]).rays()
        (N(1, 0), N(0, 1))

    However, this work is not done with ``check=False`` option, so use it
    carefully! ::

        sage: Cone([(1,0), (0,1), (1,1), (0,1)], check=False).rays()
        (N(1, 0), N(0, 1), N(1, 1), N(0, 1))

    Even worse things can happen with ``normalize=False`` option::

        sage: Cone([(1,0), (0,1)], check=False, normalize=False)
        Traceback (most recent call last):
        ...
        AttributeError: 'tuple' object has no attribute 'parent'

    You can construct different "not" cones: not full-dimensional, not
    strictly convex, not containing any rays::

        sage: one_dimensional_cone = Cone([(1,0)])
        sage: one_dimensional_cone.dim()
        1
        sage: half_plane = Cone([(1,0), (0,1), (-1,0)])
        sage: half_plane.rays()
        (N(0, 1), N(1, 0), N(-1, 0))
        sage: half_plane.is_strictly_convex()
        False
        sage: origin = Cone([(0,0)])
        sage: origin.rays()
        ()
        sage: origin.dim()
        0
        sage: origin.ambient_dim()
        2

    You may construct the cone above without giving any rays, but in this case
    you must provide lattice explicitly::

        sage: origin = Cone([])
        Traceback (most recent call last):
        ...
        ValueError: lattice must be given explicitly if there are no rays!
        sage: origin = Cone([], lattice=ToricLattice(2))
        sage: origin.dim()
        0
        sage: origin.ambient_dim()
        2
        sage: origin.lattice()
        2-dimensional lattice N

    Of course, you can also provide lattice in other cases::

        sage: L = ToricLattice(3, "L")
        sage: c1 = Cone([(1,0,0),(1,1,1)], lattice=L)
        sage: c1.rays()
        (L(1, 0, 0), L(1, 1, 1))

    Or you can construct cones from rays of a particular lattice::

        sage: ray1 = L(1,0,0)
        sage: ray2 = L(1,1,1)
        sage: c2 = Cone([ray1, ray2])
        sage: c2.rays()
        (L(1, 0, 0), L(1, 1, 1))
        sage: c1 == c2
        True

    When the cone in question is not strictly convex, the standard form for
    the "generating rays" of the linear subspace is "basis vectors and their
    negatives", as in the following example::

        sage: plane = Cone([(1,0), (0,1), (-1,-1)])
        sage: plane.ray_matrix()
        [ 1 -1  0  0]
        [ 0  0  1 -1]
    """
    # Cone from Polyhedron
    if isinstance(data, Polyhedron):
        polyhedron = data
        if lattice is None:
            lattice = ToricLattice(polyhedron.ambient_dim())
        if polyhedron.n_vertices() > 1:
            raise ValueError("%s is not a cone!" % polyhedron)
        apex = polyhedron.vertices()[0]
        if apex.count(0) != len(apex):
            raise ValueError("the apex of %s is not at the origin!"
                             % polyhedron)
        rays = normalize_rays(polyhedron.rays(), lattice)
        strict_rays = tuple(rays)
        lines = tuple(normalize_rays(polyhedron.lines(), lattice))
        for line in lines:
            rays.append(line)
            rays.append(-line)
            rays[-1].set_immutable()
        cone = ConvexRationalPolyhedralCone(rays, lattice)
        # Save constructed stuff for later use
        cone._polyhedron = polyhedron
        cone._strict_rays = strict_rays
        cone._lines = lines
        return cone
    # Cone from rays
    rays = data
    if check or normalize:
        # In principle, if check is True, this normalization is redundant,
        # since we will need to renormalize the output from Polyhedra, but
        # doing it now gives more consistent error messages (and it seems to
        # be fast anyway, compared to Polyhedron creation).
        rays = normalize_rays(rays, lattice)
    if lattice is None:
        if rays:
            lattice = rays[0].parent()
        else:
            raise ValueError(
                "lattice must be given explicitly if there are no rays!")
    if check and rays:
        # Any set of rays forms a cone, but we want to keep only generators
        return Cone(Polyhedron(rays=rays), lattice)
    return ConvexRationalPolyhedralCone(rays, lattice)


def normalize_rays(rays, lattice):
    r"""
    Normalize a list of rational rays, i.e. make them integral.

    INPUT:

    - ``rays`` -- list of rays which can be converted to the rational
      extension of ``lattice``;

    - ``lattice`` -- :class:`ToricLattice
      <sage.geometry.toric_lattice.ToricLatticeFactory>`, `\ZZ^n`, or any
      other object that behaves like these. If ``None``, an attempt will
      be made to determine an appropriate toric lattice automatically.

    OUTPUT:

    - list of immutable primitive vectors of the ``lattice`` in the same
      directions as original ``rays``.

    EXAMPLES::

        sage: from sage.geometry.cone import normalize_rays
        sage: normalize_rays([(0, 1), (0, 2), (3, 2), (5/7, 10/3)], None)
        [N(0, 1), N(0, 1), N(3, 2), N(3, 14)]
        sage: L = ToricLattice(2, "L")
        sage: normalize_rays([(0, 1), (0, 2), (3, 2), (5/7, 10/3)], L.dual())
        [L*(0, 1), L*(0, 1), L*(3, 2), L*(3, 14)]
        sage: ray_in_L = L(0,1)
        sage: normalize_rays([ray_in_L, (0, 2), (3, 2), (5/7, 10/3)], None)
        [L(0, 1), L(0, 1), L(3, 2), L(3, 14)]
        sage: normalize_rays([(0, 1), (0, 2), (3, 2), (5/7, 10/3)], ZZ^2)
        [(0, 1), (0, 1), (3, 2), (3, 14)]
        sage: normalize_rays([(0, 1), (0, 2), (3, 2), (5/7, 10/3)], ZZ^3)
        Traceback (most recent call last):
        ...
        TypeError: cannot convert (0, 1) to
        Vector space of dimension 3 over Rational Field!
        sage: normalize_rays([], ZZ^3)
        []
    """
    if rays is None:
        rays = []
    try:
        rays = list(rays)
    except TypeError:
        raise TypeError(
                    "rays must be given as a list or a compatible structure!"
                    "\nGot: %s" % rays)
    if rays:
        if lattice is None:
            ray_parent = parent(rays[0])
            lattice = (ray_parent if is_ToricLattice(ray_parent)
                                  else ToricLattice(len(rays[0])))
        V = lattice.base_extend(QQ)
        for n, ray in enumerate(rays):
            try:
                ray = V(ray)
            except TypeError:
                raise TypeError("cannot convert %s to %s!" % (ray, V))
            if ray.is_zero():
                ray = lattice(0)
            else:
                ray = ray.denominator() * ray
                ray = lattice(ray / gcd(lattice(ray)))
            ray.set_immutable()
            rays[n] = ray
    return rays


class IntegralRayCollection(SageObject,
                            collections.Container,
                            collections.Hashable,
                            collections.Iterable):
    r"""
    Create a collection of integral rays.

    This is a base class for rational polyhedral cones and fans.

    Ray collections are immutable, but they cache most of the returned values.

    INPUT:

    - ``rays`` -- list of immutable vectors in ``lattice``;

    - ``lattice`` -- :class:`ToricLattice
      <sage.geometry.toric_lattice.ToricLatticeFactory>`, `\ZZ^n`, or any
      other object that behaves like these. If ``None``, it will be determined
      as :func:`parent` of the first ray. Of course, this cannot be done if
      there are no rays, so in this case you must give an appropriate
      ``lattice`` directly.

    OUTPUT:

    - collection of given integral rays.

    .. WARNING::

        No correctness check or normalization is performed on the input data.
        This class is designed for internal operations and you probably should
        not use it directly.

    TESTS::

        sage: v = vector([0,1])
        sage: v.set_immutable()
        sage: c = sage.geometry.cone.IntegralRayCollection([v], None)
        sage: c.rays()
        ((0, 1),)
        sage: TestSuite(c).run()
    """

    def __init__(self, rays, lattice):
        r"""
        See :class:`IntegralRayCollection` for documentation.

        TESTS::

            sage: v = vector([0,1])
            sage: v.set_immutable()
            sage: sage.geometry.cone.IntegralRayCollection([v], None).rays()
            ((0, 1),)
        """
        self._rays = tuple(rays)
        self._lattice = self._rays[0].parent() if lattice is None else lattice

    def __cmp__(self, right):
        r"""
        Compare ``self`` and ``right``.

        INPUT:

        - ``right`` -- anything.

        OUTPUT:

        - 0 if ``right`` is of the same type as ``self`` and their rays are
          the same and listed in the same order. 1 or -1 otherwise.

        TESTS::

            sage: c1 = Cone([(1,0), (0,1)])
            sage: c2 = Cone([(0,1), (1,0)])
            sage: c3 = Cone([(0,1), (1,0)])
            sage: cmp(c1, c2)
            1
            sage: cmp(c2, c1)
            -1
            sage: cmp(c2, c3)
            0
            sage: c2 is c3
            False
            sage: cmp(c1, 1) * cmp(1, c1)
            -1
        """
        c = cmp(type(self), type(right))
        if c:
            return c
        return cmp((self.lattice(), self.rays()),
                   (right.lattice(), right.rays()))

    def __hash__(self):
        r"""
        Return the hash of ``self`` computed from rays.

        OUTPUT:

        - integer.

        TESTS::

            sage: c = Cone([(1,0), (0,1)])
            sage: hash(c)  # 64-bit
            4372618627376133801
        """
        if "_hash" not in self.__dict__:
            self._hash = hash(self._rays)
        return self._hash

    def __iter__(self):
        r"""
        Return an iterator over rays of ``self``.

        OUTPUT:

        -  iterator.

        TESTS::

            sage: c = Cone([(1,0), (0,1)])
            sage: for ray in c: print ray
            N(1, 0)
            N(0, 1)
        """
        return self.ray_iterator()

    def ambient_dim(self):
        r"""
        Return the dimension of the ambient lattice of ``self``.

        OUTPUT:

        - integer.

        EXAMPLES::

            sage: c = Cone([(1,0)])
            sage: c.ambient_dim()
            2
            sage: c.dim()
            1
        """
        return self.lattice().dimension()

    def dim(self):
        r"""
        Return the dimension of the subspace spanned by rays of ``self``.

        OUTPUT:

        - integer.

        EXAMPLES::

            sage: c = Cone([(1,0)])
            sage: c.ambient_dim()
            2
            sage: c.dim()
            1
        """
        if "_dim" not in self.__dict__:
            self._dim = self.ray_matrix().rank()
        return self._dim

    def lattice(self):
        r"""
        Return the ambient lattice of ``self``.

        OUTPUT:

        - lattice.

        EXAMPLES::

            sage: c = Cone([(1,0)])
            sage: c.lattice()
            2-dimensional lattice N
            sage: Cone([], ZZ^3).lattice()
            Ambient free module of rank 3
            over the principal ideal domain Integer Ring
        """
        return self._lattice

    def nrays(self):
        r"""
        Return the number of rays of ``self``.

        OUTPUT:

        - integer.

        EXAMPLES::

            sage: c = Cone([(1,0), (0,1)])
            sage: c.nrays()
            2
        """
        return len(self._rays)

    def ray(self, n):
        r"""
        Return the ``n``-th ray of ``self``.

        INPUT:

        - ``n`` -- integer, an index of a ray of ``self``. Enumeration of rays
          starts with zero.

        OUTPUT:

        - ray, an element of the lattice of ``self``.

        EXAMPLES::

            sage: c = Cone([(1,0), (0,1)])
            sage: c.ray(0)
            N(1, 0)
        """
        return self._rays[n]

    def ray_iterator(self, ray_list=None):
        r"""
        Return an iterator over (some of) the rays of ``self``.

        INPUT:

        - ``ray_list`` -- list of integers, the indices of the requested rays.
          If not specified, an iterator over all rays of ``self`` will be
          returned.

        OUTPUT:

        - iterator.

        EXAMPLES::

            sage: c = Cone([(1,0), (0,1), (-1, 0)])
            sage: for ray in c.ray_iterator(): print ray
            N(0, 1)
            N(1, 0)
            N(-1, 0)
            sage: for ray in c.ray_iterator([2,1]): print ray
            N(-1, 0)
            N(1, 0)
        """
        if ray_list is None:
            for ray in self._rays:
                yield ray
        else:
            rays = self._rays
            for n in ray_list:
                yield rays[n]

    def ray_matrix(self):
        r"""
        Return a matrix whose columns are rays of ``self``.

        It can be convenient for linear algebra operations on rays, as well as
        for easy-to-read output.

        OUTPUT:

        - matrix.

        EXAMPLES::

            sage: c = Cone([(1,0), (0,1), (-1, 0)])
            sage: c.ray_matrix()
            [ 0  1 -1]
            [ 1  0  0]
        """
        if "_ray_matrix" not in self.__dict__:
            self._ray_matrix = matrix(self.nrays(), self.ambient_dim(),
                                      self._rays).transpose()
            self._ray_matrix.set_immutable()
        return self._ray_matrix

    def ray_set(self):
        r"""
        Return rays of ``self`` as a :class:`frozenset`.

        Use :meth:`rays` if you want to get rays in the fixed order.

        OUTPUT:

        - :class:`frozenset` of rays.

        EXAMPLES::

            sage: c = Cone([(1,0), (0,1), (-1, 0)])
            sage: c.ray_set()
            frozenset([N(0, 1), N(1, 0), N(-1, 0)])
        """
        if "_ray_set" not in self.__dict__:
            self._ray_set = frozenset(self._rays)
        return self._ray_set

    def rays(self, ray_list=None):
        r"""
        Return rays of ``self`` as a :class:`tuple`.

        INPUT:

        - ``ray_list`` -- list of integers, the indices of the requested rays.
          If not specified, all rays of ``self`` will be returned. You may
          want to use :meth:`ray_set` if you do not care about the order of
          rays. See also :meth:`ray_iterator`.

        OUTPUT:

        - :class:`tuple` of rays.

        EXAMPLES::

            sage: c = Cone([(1,0), (0,1), (-1, 0)])
            sage: c.rays()
            (N(0, 1), N(1, 0), N(-1, 0))
            sage: c.rays([0, 2])
            (N(0, 1), N(-1, 0))
        """
        if ray_list is None:
            return self._rays
        else:
            return tuple(self.ray_iterator(ray_list))


class ConvexRationalPolyhedralCone(IntegralRayCollection):
    r"""
    Create a convex rational polyhedral cone.

    .. WARNING::

        This class does not perform any checks of correctness of input nor
        does it convert input into the standard representation. Use
        :func:`Cone` to construct cones.

    Cones are immutable, but they cache most of the returned values.

    INPUT:

    - same as for :class:`IntegralRayCollection`.

    OUTPUT:

    - convex rational polyhedral cone.

    TESTS::

        sage: v = vector([0,1])
        sage: v.set_immutable()
        sage: c = sage.geometry.cone.ConvexRationalPolyhedralCone([v], None)
        sage: c.rays()
        ((0, 1),)
        sage: TestSuite(c).run()

        sage: c = Cone([(0,1)])
        sage: TestSuite(c).run()
    """

    # No __init__ method, just use the base class.

    def __contains__(self, point):
        r"""
        Check if ``point`` is contained in ``self``.

        See :meth:`_contains` (which is called by this function) for
        documentation.

        TESTS::

            sage: c = Cone([(1,0), (0,1)])
            sage: (1,1) in c
            True
            sage: [1,1] in c
            True
            sage: (-1,0) in c
            False
        """
        return self._contains(point)

    def __getstate__(self):
        r"""
        Return the dictionary that should be pickled.

        OUTPUT:

        - :class:`dict`.

        TESTS::

            sage: loads(dumps(Cone([(1,0)])))
            1-dimensional cone
        """
        state = copy.copy(self.__dict__)
        state.pop("_polyhedron", None) # Polyhedron is not picklable.
        state.pop("_lattice_polytope", None) # Just to save time and space.
        return state

    def _contains(self, point):
        r"""
        Check if ``point`` is contained in ``self``.

        This function is called by :meth:`__contains__` and :meth:`contains`
        to ensure the same call depth for warning messages.

        INPUT:

        - ``point`` -- anything. An attempt will be made to convert it into a
          single element of the ambient space of ``self``. If it fails,
          ``False`` will be returned.

        OUTPUT:

        - ``True`` if ``point`` is contained in ``self``, ``False`` otherwise.

        TESTS::

            sage: c = Cone([(1,0), (0,1)])
            sage: c._contains((1,1))
            True
        """
        if is_ToricLattice(parent(point)):
            # Special treatment for elements of OTHER toric lattices
            if point not in self.lattice():
                # This is due to the discussion in Trac #8986
                warnings.warn("you have checked if a cone contains a point "
                              "from another lattice, this is always False!",
                              stacklevel=3)
                return False
        else:
            try: # to cook up a point being exact ...
                point = self.lattice().base_extend(QQ)(point)
            except TypeError:
                try: # ... or at least numeric
                    point = self.lattice().base_extend(RR)(point)
                except TypeError:
                    # Give up, input is really strange
                    return False
        return all(n * point >= 0 for n in self.facet_normals())

    def __cmp__(self, right):
        r"""
        Compare ``self`` and ``right``.

        INPUT:

        - ``right`` -- anything.

        OUTPUT:

        - 0 if ``self`` and ``right`` are cones of any kind in the same
          lattice with the same rays listed in the same order. 1 or -1
          otherwise.

        TESTS::

            sage: c1 = Cone([(1,0), (0,1)])
            sage: c2 = Cone([(0,1), (1,0)])
            sage: c3 = Cone([(0,1), (1,0)])
            sage: cmp(c1, c2)
            1
            sage: cmp(c2, c1)
            -1
            sage: cmp(c2, c3)
            0
            sage: c2 is c3
            False
            sage: cmp(c1, 1)
            -1
        """
        if is_Cone(right):
            # We don't care about particular type of right in this case
            return cmp((self.lattice(), self.rays()),
                       (right.lattice(), right.rays()))
        else:
            return cmp(type(self), type(right))

    def _latex_(self):
        r"""
        Return a LaTeX representation of ``self``.

        OUTPUT:

        - string.

        TESTS::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: quadrant._latex_()
            '\\sigma^{2}'
        """
        return r"\sigma^{%d}" % self.dim()

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        OUTPUT:

        - string.

        TESTS::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: quadrant._repr_()
            '2-dimensional cone'
            sage: quadrant
            2-dimensional cone
        """
        return "%d-dimensional cone" % self.dim()

    def contains(self, *args):
        r"""
        Check if a given point is contained in ``self``.

        INPUT:

        - anything. An attempt will be made to convert all arguments into a
          single element of the ambient space of ``self``. If it fails,
          ``False`` will be returned.

        OUTPUT:

        - ``True`` if the given point is contained in ``self``, ``False``
          otherwise.

        EXAMPLES::

            sage: c = Cone([(1,0), (0,1)])
            sage: c.contains(c.lattice()(1,0))
            True
            sage: c.contains((1,0))
            True
            sage: c.contains((1,1))
            True
            sage: c.contains(1,1)
            True
            sage: c.contains((-1,0))
            False
            sage: c.contains(c.lattice().dual()(1,0)) #random output (warning)
            False
            sage: c.contains(c.lattice().dual()(1,0))
            False
            sage: c.contains(1)
            False
            sage: c.contains(1/2, sqrt(3))
            True
            sage: c.contains(-1/2, sqrt(3))
            False
        """
        point = flatten(args)
        if len(point) == 1:
           point = point[0]
        return self._contains(point)

    def face_lattice(self):
        r"""
        Return the face lattice of ``self``.

        This lattice will have the origin as the bottom (we do not include the
        empty set as a face) and this cone itself as the top.

        OUTPUT:

        - :class:`~sage.combinat.posets.posets.FinitePoset` of
          :class:`ConeFace` objects, behaving like other cones, but also
          containing the information about their relation to this one, namely,
          the generating rays and containing facets.

        EXAMPLES:

        Let's take a look at the face lattice of the first quadrant::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: L = quadrant.face_lattice()
            sage: L
            Finite poset containing 4 elements

        To see all faces arranged by dimension, you can do this::

            sage: for level in L.level_sets(): print level
            [0-dimensional face of 2-dimensional cone]
            [1-dimensional face of 2-dimensional cone,
             1-dimensional face of 2-dimensional cone]
            [2-dimensional face of 2-dimensional cone]

        To work with a particular face of a particular dimension it is not
        enough to do just ::

            sage: face = L.level_sets()[1][0]
            sage: face
            1-dimensional face of 2-dimensional cone
            sage: face.rays()
            Traceback (most recent call last):
            ...
            AttributeError: 'PosetElement' object has no attribute 'rays'

        To get the actual face you need one more step::

            sage: face = face.element

        Now you can look at the actual rays of this face... ::

            sage: face.rays()
            (N(1, 0),)

        ... or you can see indices of the rays of the orginal cone that
        correspond to the above ray::

            sage: face.cone_rays()
            (0,)
            sage: quadrant.ray(0)
            N(1, 0)

        You can also get the list of facets of the original cone containing
        this face::

            sage: face.cone_facets()
            (1,)

        An alternative to extracting faces from the face lattice is to use
        :meth:`faces` method::

            sage: face is quadrant.faces(dim=1)[0]
            True

        The advantage of working with the face lattice directly is that you
        can (relatively easily) get faces that are related to the given one::

            sage: face = L.level_sets()[1][0]
            sage: D = L.hasse_diagram()
            sage: D.neighbors(face)
            [0-dimensional face of 2-dimensional cone,
             2-dimensional face of 2-dimensional cone]
        """
        if "_face_lattice" not in self.__dict__:
            if not self.is_strictly_convex():
                raise NotImplementedError("face lattice is currently "
                                "implemented only for strictly convex cones!")
            # Should we build it from PALP complete incidences? May be faster.
            # On the other hand this version is also quite nice ;-)
            ray_to_facets = []
            facet_to_rays = []
            for ray in self:
                ray_to_facets.append([])
            for normal in self.facet_normals():
                facet_to_rays.append([])
            for i, ray in enumerate(self):
                for j, normal in enumerate(self.facet_normals()):
                    if ray * normal == 0:
                        ray_to_facets[i].append(j)
                        facet_to_rays[j].append(i)
            self._face_lattice = hasse_diagram_from_incidences(
                        ray_to_facets, facet_to_rays, ConeFace, cone=self)
        return self._face_lattice

    def faces(self, dim=None, codim=None):
        r"""
        Return faces of ``self`` of specified (co)dimension.

        INPUT:

        - ``dim`` -- integer, dimension of the requested faces;

        - ``codim`` -- integer, codimension of the requested faces.

        .. NOTE::

            You can specify at most one parameter. If you don't give any, then
            all faces will be returned.

        OUTPUT:

        - if either ``dim`` or ``codim`` is given, the output will be a
          :class:`tuple` of :class:`ConeFace` objects, behaving like other
          cones, but also containing the information about their relation to
          this one, namely, the generating rays and containing facets;

        - if neither ``dim`` nor ``codim`` is given, the output will be the
          :class:`tuple` of tuples as above, giving faces of all dimension. If
          you care about inclusion relations between faces, consider using
          :meth:`face_lattice`.

        EXAMPLES:

        Let's take a look at the faces of the first quadrant::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: quadrant.faces()
            ((0-dimensional face of 2-dimensional cone,),
             (1-dimensional face of 2-dimensional cone,
              1-dimensional face of 2-dimensional cone),
             (2-dimensional face of 2-dimensional cone,))
            sage: quadrant.faces(dim=1)
            (1-dimensional face of 2-dimensional cone,
             1-dimensional face of 2-dimensional cone)
            sage: face = quadrant.faces(dim=1)[0]

        Now you can look at the actual rays of this face... ::

            sage: face.rays()
            (N(1, 0),)

        ... or you can see indices of the rays of the orginal cone that
        correspond to the above ray::

            sage: face.cone_rays()
            (0,)
            sage: quadrant.ray(0)
            N(1, 0)

        You can also get the list of facets of the original cone containing
        this face::

            sage: face.cone_facets()
            (1,)
        """
        if "_faces" not in self.__dict__:
            self._faces = tuple(tuple(e.element
                                      for e in level)
                                for level in self.face_lattice().level_sets())
        if dim is None and codim is None:
            return self._faces
        elif dim is None:
            return self._faces[self.dim() - codim]
        elif codim is None:
            return self._faces[dim]
        raise ValueError(
                    "dimension and codimension cannot be specified together!")

    def facet_normals(self):
        r"""
        Return normals to facets of ``self``.

        .. NOTE::

            For a not full-dimensional cone facet normals will be parallel to
            the subspace spanned by the cone.

        OUTPUT:

        - :class:`tuple` of vectors.

        EXAMPLES::

            sage: cone = Cone([(1,0), (-1,3)])
            sage: cone.facet_normals()
            ((3, 1), (0, 1))
        """
        if "_facet_normals" not in self.__dict__:
            if not self.is_strictly_convex():
                raise NotImplementedError("facet normals are currently "
                                "implemented only for strictly convex cones!")
            lp = self.lattice_polytope()
            self._facet_normals = tuple(lp.facet_normal(i)
                                        for i in range(lp.nfacets())
                                        if lp.facet_constant(i) == 0)
        return self._facet_normals

    def facets(self):
        r"""
        Return facets (faces of codimension 1) of ``self``.

        This function is a synonym for ``self.faces(codim=1)``.

        OUTPUT:

        - :class:`tuple` of :class:`ConeFace` objects.

        EXAMPLES::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: quadrant.facets()
            (1-dimensional face of 2-dimensional cone,
             1-dimensional face of 2-dimensional cone)
            sage: quadrant.facets() is quadrant.faces(codim=1)
            True
        """
        return self.faces(codim=1)

    def intersection(self, other):
        r"""
        Compute the intersection of two cones.

        INPUT:

        - ``other`` - cone.

        OUTPUT:

        - cone.

        EXAMPLES::

            sage: cone1 = Cone([(1,0), (-1, 3)])
            sage: cone2 = Cone([(-1,0), (2, 5)])
            sage: cone1.intersection(cone2).rays()
            (N(2, 5), N(-1, 3))
        """
        return Cone(self.polyhedron().intersection(other.polyhedron()),
                    self.lattice())

    def is_equivalent(self, other):
        r"""
        Check if ``self`` is "mathematically" the same as ``other``.

        INPUT:

        - ``other`` - cone.

        OUTPUT:

        - ``True`` if ``self`` and ``other`` define the same cones as sets of
          points in the same lattice, ``False`` otherwise.

        There are three different equivalences between cones `C_1` and `C_2`
        in the same lattice:

        #. They have the same generating rays in the same order.
           This is tested by ``C1 == C2``.
        #. They describe the same sets of points.
           This is tested by ``C1.is_equivalent(C2)``.
        #. They are in the same orbit of `GL(n,\ZZ)` (and, therefore,
           correspond to isomorphic affine toric varieties).
           This is tested by ``C1.is_isomorphic(C2)``.

        EXAMPLES::

            sage: cone1 = Cone([(1,0), (-1, 3)])
            sage: cone2 = Cone([(-1,3), (1, 0)])
            sage: cone1.rays()
            (N(1, 0), N(-1, 3))
            sage: cone2.rays()
            (N(-1, 3), N(1, 0))
            sage: cone1 == cone2
            False
            sage: cone1.is_equivalent(cone2)
            True
        """
        if self.lattice() != other.lattice():
            return False
        if self.ray_set() == other.ray_set():
            return True
        if self.is_strictly_convex() or other.is_strictly_convex():
            return False # For strictly convex cones ray sets must coincide
        if self.linear_subspace() != other.linear_subspace():
            return False
        return self.strict_quotient().is_equivalent(other.strict_quotient())

    def is_face_of(self, cone):
        r"""
        Check if ``self`` forms a face of another ``cone``.

        INPUT:

        - ``cone`` -- cone.

        OUTPUT:

        - ``True`` if ``self`` is a face of ``cone``, ``False`` otherwise.

        EXAMPLES::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: cone1 = Cone([(1,0)])
            sage: cone2 = Cone([(1,2)])
            sage: quadrant.is_face_of(quadrant)
            True
            sage: cone1.is_face_of(quadrant)
            True
            sage: cone2.is_face_of(quadrant)
            False
        """
        if self.lattice() != cone.lattice():
            return False
        # Cases of the origin and the whole cone (we don't have empty cones)
        if self.nrays() == 0 or self.is_equivalent(cone):
            return True
        # Obviously False cases
        if (self.dim() >= cone.dim() # if == and face, we return True above
            or self.is_strictly_convex() != cone.is_strictly_convex()
            or self.linear_subspace() != cone.linear_subspace()):
            return False
        # Now we need to worry only about strict quotients
        if not self.strict_quotient().ray_set().issubset(
                                            cone.strict_quotient().ray_set()):
            return False
        # Maybe this part can be written in a more efficient way
        ph_self = self.strict_quotient().polyhedron()
        ph_cone = cone.strict_quotient().polyhedron()
        containing = []
        for n, H in enumerate(ph_cone.Hrepresentation()):
            containing.append(n)
            for V in ph_self.Vrepresentation():
                if H.eval(V) != 0:
                    containing.pop()
                    break
        m = ph_cone.incidence_matrix().matrix_from_columns(containing)
        # The intersection of all containing hyperplanes should contain only
        # rays of the potential face and the origin
        return map(sum, m.rows()).count(m.ncols()) == ph_self.n_rays() + 1

    def is_isomorphic(self, other):
        r"""
        Check if ``self`` is in the same `GL(n, \ZZ)`-orbit as ``other``.

        INPUT:

        - ``other`` - cone.

        OUTPUT:

        - ``True`` if ``self`` and ``other`` are in the same
          `GL(n, \ZZ)`-orbit, ``False`` otherwise.

        There are three different equivalences between cones `C_1` and `C_2`
        in the same lattice:

        #. They have the same generating rays in the same order.
           This is tested by ``C1 == C2``.
        #. They describe the same sets of points.
           This is tested by ``C1.is_equivalent(C2)``.
        #. They are in the same orbit of `GL(n,\ZZ)` (and, therefore,
           correspond to isomorphic affine toric varieties).
           This is tested by ``C1.is_isomorphic(C2)``.

        EXAMPLES::

            sage: cone1 = Cone([(1,0), (0, 3)])
            sage: cone2 = Cone([(-1,3), (1, 0)])
            sage: cone1.is_isomorphic(cone2)
            Traceback (most recent call last):
            ...
            NotImplementedError: cone isomorphism is not implemented yet!
        """
        if self.lattice() != other.lattice():
            return False
        raise NotImplementedError("cone isomorphism is not implemented yet!")

    def is_simplicial(self):
        r"""
        Check if ``self`` is simplicial.

        A cone is called *simplicial* if primitive vectors along its
        generating rays form a part of a rational basis of the ambient space.

        OUTPUT:

        - ``True`` if ``self`` is simplicial, ``False`` otherwise.

        EXAMPLES::

            sage: cone1 = Cone([(1,0), (0, 3)])
            sage: cone2 = Cone([(1,0), (0, 3), (-1,-1)])
            sage: cone1.is_simplicial()
            True
            sage: cone2.is_simplicial()
            False
        """
        return self.nrays() == self.dim()

    def is_smooth(self):
        r"""
        Check if ``self`` is smooth.

        A cone is called *smooth* if primitive vectors along its generating
        rays form a part of an *integral* basis of the ambient space.

        OUTPUT:

        - ``True`` if ``self`` is smooth, ``False`` otherwise.

        EXAMPLES::

            sage: cone1 = Cone([(1,0), (0, 1)])
            sage: cone2 = Cone([(1,0), (-1, 3)])
            sage: cone1.is_smooth()
            True
            sage: cone2.is_smooth()
            False
        """
        if "_is_smooth" not in self.__dict__:
            if not self.is_simplicial():
                self._is_smooth = False
            else:
                m = self.ray_matrix()
                if self.dim() != self.ambient_dim():
                    m = m.augment(identity_matrix(self.ambient_dim()))
                    m = m.matrix_from_columns(m.pivots())
                self._is_smooth = abs(m.det()) == 1
        return self._is_smooth

    def is_strictly_convex(self):
        r"""
        Check if ``self`` is strictly convex.

        A cone is called *strictly convex* if it does not contain any lines.

        OUTPUT:

        - ``True`` if ``self`` is strictly convex, ``False`` otherwise.

        EXAMPLES::

            sage: cone1 = Cone([(1,0), (0, 1)])
            sage: cone2 = Cone([(1,0), (-1, 0)])
            sage: cone1.is_strictly_convex()
            True
            sage: cone2.is_strictly_convex()
            False
        """
        if "_is_strictly_convex" not in self.__dict__:
            self._is_strictly_convex = self.polyhedron().n_lines() == 0
        return self._is_strictly_convex

    def lattice_polytope(self):
        r"""
        Return the lattice polytope associated to ``self``.

        The vertices of this polytope are primitive vectors along the
        generating rays of ``self`` and the origin, if ``self`` is strictly
        convex. In this case the origin is the last vertex, so the `i`-th ray
        of the cone always corresponds to the `i`-th vertex of the polytope.

        See also :meth:`polyhedron`.

        OUTPUT:

        - :class:`LatticePolytope
          <sage.geometry.lattice_polytope.LatticePolytopeClass>`.

        EXAMPLES::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: lp = quadrant.lattice_polytope()
            sage: lp
            A lattice polytope: 2-dimensional, 3 vertices.
            sage: lp.vertices()
            [1 0 0]
            [0 1 0]

            sage: line = Cone([(1,0), (-1,0)])
            sage: lp = line.lattice_polytope()
            sage: lp
            A lattice polytope: 1-dimensional, 2 vertices.
            sage: lp.vertices()
            [ 1 -1]
            [ 0  0]
        """
        if "_lattice_polytope" not in self.__dict__:
            m = self.ray_matrix()
            if self.is_strictly_convex():
                m = m.augment(matrix(ZZ, self.ambient_dim(), 1)) # the origin
            self._lattice_polytope = LatticePolytope(m,
                                compute_vertices=False, copy_vertices=False)
        return self._lattice_polytope

    def line_set(self):
        r"""
        Return a set of lines generating the linear subspace of ``self``.

        OUTPUT:

        - :class:`frozenset` of primitive vectors in the lattice of ``self``
          giving directions of lines that span the linear subspace of
          ``self``. These lines are arbitrary, but fixed. See also
          :meth:`lines`.

        EXAMPLES::

            sage: halfplane = Cone([(1,0), (0,1), (-1,0)])
            sage: halfplane.line_set()
            frozenset([N(1, 0)])
            sage: fullplane = Cone([(1,0), (0,1), (-1,-1)])
            sage: fullplane.line_set()
            frozenset([N(0, 1), N(1, 0)])
        """
        if "_line_set" not in self.__dict__:
            self._line_set = frozenset(self.lines())
        return self._line_set

    def linear_subspace(self):
        r"""
        Return the largest linear subspace contained inside of ``self``.

        OUTPUT:

        - subspace of the ambient space of ``self``.

        EXAMPLES::

            sage: halfplane = Cone([(1,0), (0,1), (-1,0)])
            sage: halfplane.linear_subspace()
            Vector space of degree 2 and dimension 1 over Rational Field
            Basis matrix:
            [1 0]
        """
        if "_linear_subspace" not in self.__dict__:
            if self.is_strictly_convex():
                self._linear_subspace = span([vector(QQ, self.ambient_dim())],
                                             QQ)
            else:
                self._linear_subspace = span(self.lines(), QQ)
        return self._linear_subspace

    def lines(self):
        r"""
        Return lines generating the linear subspace of ``self``.

        OUTPUT:

        - :class:`tuple` of primitive vectors in the lattice of ``self``
          giving directions of lines that span the linear subspace of
          ``self``. These lines are arbitrary, but fixed. If you do not care
          about the order, see also :meth:`line_set`.

        EXAMPLES::

            sage: halfplane = Cone([(1,0), (0,1), (-1,0)])
            sage: halfplane.lines()
            (N(1, 0),)
            sage: fullplane = Cone([(1,0), (0,1), (-1,-1)])
            sage: fullplane.lines()
            (N(1, 0), N(0, 1))
        """
        if "_lines" not in self.__dict__:
            if self.is_strictly_convex():
                self._lines = ()
            else:
                self._lines = tuple(normalize_rays(self.polyhedron().lines(),
                                                   self.lattice()))
        return self._lines

    def polyhedron(self):
        r"""
        Return the polyhedron associated to ``self``.

        Mathematically this polyhedron is the same as ``self``.

        See also :meth:`lattice_polytope`.

        OUTPUT:

        - :class:`~sage.geometry.polyhedra.Polyhedron`.

        EXAMPLES::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: ph = quadrant.polyhedron()
            sage: ph
            A 2-dimensional polyhedron in QQ^2 defined as the convex hull
            of 1 vertex and 2 rays.
            sage: line = Cone([(1,0), (-1,0)])
            sage: ph = line.polyhedron()
            sage: ph
            A 1-dimensional polyhedron in QQ^2 defined as the convex hull
            of 1 vertex and 1 line.
        """
        if "_polyhedron" not in self.__dict__:
            self._polyhedron = Polyhedron(rays=self.rays())
        return self._polyhedron

    def strict_quotient(self):
        r"""
        Return the quotient of ``self`` by the linear subspace.

        We define the **strict quotient** of a cone to be the image of this
        cone in the quotient of the ambient space by the linear subspace of
        the cone, i.e. it is the "complementary part" to the linear subspace.

        OUTPUT:

        - cone.

        EXAMPLES::

            sage: halfplane = Cone([(1,0), (0,1), (-1,0)])
            sage: ssc = halfplane.strict_quotient()
            sage: ssc
            1-dimensional cone
            sage: ssc.rays()
            (N(1),)
            sage: line = Cone([(1,0), (-1,0)])
            sage: ssc = line.strict_quotient()
            sage: ssc
            0-dimensional cone
            sage: ssc.rays()
            ()
        """
        if "_strict_quotient" not in self.__dict__:
            if self.is_strictly_convex():
                self._strict_quotient = self
            else:
                L = self.lattice()
                Q = L.base_extend(QQ) / self.linear_subspace()
                # Maybe we can improve this one if we create something special
                # for sublattices. But it seems to be the most natural choice
                # for names. If many subcones land in the same lattice -
                # that's just how it goes.
                if is_ToricLattice(L):
                    S = ToricLattice(Q.dimension(), L._name, L._dual_name,
                                     L._latex_name, L._latex_dual_name)
                else:
                    S = ZZ**Q.dimension()
                rays = [Q(ray) for ray in self.rays() if not Q(ray).is_zero()]
                quotient = Cone(rays, S, check=False)
                quotient._is_strictly_convex = True
                self._strict_quotient = quotient
        return self._strict_quotient


class ConeFace(ConvexRationalPolyhedralCone):
    r"""
    Constuct a face of a cone (which is again a cone).

    This class provides access to the containing cone and face incidence
    information.

    .. WARNING::

        This class will sort the incidence information, but it does not check
        that the input defines a valid face. You should not construct objects
        of this class directly.

    INPUT:

    - ``cone_rays`` -- indices of rays of ``cone`` contained in this face;

    - ``cone_facets`` -- indices of facets of ``cone`` containing this face;

    - ``cone`` -- cone whose face is constructed.

    OUTPUT:

    - face of ``cone``.

    TESTS:

    The following code is likely to construct an invalid face, we just test
    that face creation is working::

        sage: quadrant = Cone([(1,0), (0,1)])
        sage: face = sage.geometry.cone.ConeFace([0], [0], quadrant)
        sage: face
        1-dimensional face of 2-dimensional cone
        sage: TestSuite(face).run()

    The intended way to get objects of this class is the following::

        sage: face = quadrant.facets()[0]
        sage: face
        1-dimensional face of 2-dimensional cone
        sage: face.cone_rays()
        (0,)
        sage: face.cone_facets()
        (1,)
    """

    def __init__(self, cone_rays, cone_facets, cone):
        r"""
        See :class:`ConeFace` for documentation.

        TESTS::

        The following code is likely to construct an invalid face, we just
        test that face creation is working::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: face = sage.geometry.cone.ConeFace([0], [0], quadrant)
            sage: face
            1-dimensional face of 2-dimensional cone
        """
        self._cone_rays = tuple(sorted(cone_rays))
        self._cone_facets = tuple(sorted(cone_facets))
        self._cone = cone
        super(ConeFace, self).__init__(cone.rays(self._cone_rays),
                                       cone.lattice())

    def _latex_(self):
        r"""
        Return a LaTeX representation of ``self``.

        OUTPUT:

        - string.

        TESTS::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: face = quadrant.facets()[0]
            sage: face._latex_()
            '\\sigma^{1} \\subset \\sigma^{2}'
        """
        return r"%s \subset %s" % (super(ConeFace, self)._latex_(),
                                   self.cone()._latex_())

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        OUTPUT:

        - string.

        TESTS::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: face = quadrant.facets()[0]
            sage: face
            1-dimensional face of 2-dimensional cone
            sage: face._repr_()
            '1-dimensional face of 2-dimensional cone'
        """
        return "%d-dimensional face of %s" % (self.dim(), self.cone())

    def cone(self):
        r"""
        Return the "ambient cone", i.e. the cone whose face ``self`` is.

        OUTPUT:

        - cone.

        EXAMPLES::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: face = quadrant.facets()[0]
            sage: face.cone() is quadrant
            True
        """
        return self._cone

    def cone_facets(self):
        r"""
        Return indices of facets of the "ambient cone" containing ``self``.

        OUTPUT:

        - increasing :class:`tuple` of integers.

        EXAMPLES::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: face = quadrant.faces(dim=0)[0]
            sage: face.cone_facets()
            (0, 1)
        """
        return self._cone_facets

    def cone_rays(self):
        r"""
        Return indices of rays of the "ambient cone" contained in ``self``.

        OUTPUT:

        - increasing :class:`tuple` of integers.

        EXAMPLES::

            sage: quadrant = Cone([(1,0), (0,1)])
            sage: face = quadrant.faces(dim=2)[0]
            sage: face.cone_rays()
            (0, 1)
        """
        return self._cone_rays


def hasse_diagram_from_incidences(atom_to_coatoms, coatom_to_atoms,
                                  face_constructor=None, **kwds):
    r"""
    Compute the Hasse diagram of an atomic and coatomic lattice.

    INPUT:

    - ``atom_to_coatoms`` - list, ``atom_to_coatom[i]`` should list all
      coatoms over the ``i``-th atom;

    - ``coatom_to_atoms`` - list, ``coatom_to_atom[i]`` should list all
      atoms under the ``i``-th coatom;

    - ``face_constructor`` - function or class taking as the first two
      arguments :class:`frozenset` and any number of keyword arguments. It
      will be called to construct a face over atoms passed as the first
      argument and under coatoms passed as the second argument;

    - all other keyword arguments will be passed to ``face_constructor`` on
      each call.

    OUTPUT:

    - :class:`~sage.combinat.posets.posets.FinitePoset` with elements
      constructed by ``face_constructor``.

    ALGORITHM:

    The detailed description of the used algorithm is given in [KP2002]_.

    The code of this function follows the pseudocode description in the
    section 2.5 of the paper, although it is mostly based on frozen sets
    instead of sorted lists - this makes the implementation easier and should
    not cost a big performance penalty. (If one wants to make this function
    faster, it should be probably written in Cython.)

    While the title of the paper mentions only polytopes, the algorithm (and
    the implementation provided here) is applicable to any atomic and coatomic
    lattice if both incidences are given, see Section 3.4.

    In particular, this function can be used for cones and complete fans.

    REFERENCES:

    ..  [KP2002]
        Volker Kaibel and Marc E. Pfetsch,
        "Computing the Face Lattice of a Polytope from its Vertex-Facet
        Incidences", Computational Geometry: Theory and Applications,
        Volume 23, Issue 3 (November 2002), 281-290.
        Available at http://portal.acm.org/citation.cfm?id=763203

    AUTHORS:

    - Andrey Novoseltsev (2010-05-13) with thanks to Marshall Hampton for the
      reference.

    EXAMPLES:

    Let's construct the Hasse diagram of a lattice of subsets of {0, 1, 2}.
    Our atoms are {0}, {1}, and {2}, while our coatoms are {0,1}, {0,2}, and
    {1,2}. Then incidences are ::

        sage: atom_to_coatoms = [(0,1), (0,2), (1,2)]
        sage: coatom_to_atoms = [(0,1), (0,2), (1,2)]

    Let's store elements of the lattice as pairs of sorted tuples::

        sage: face_constructor = \
        ...      lambda a, b: (tuple(sorted(a)), tuple(sorted(b)))

    Then we can compute the Hasse diagram as ::

        sage: L = sage.geometry.cone.hasse_diagram_from_incidences(
        ...       atom_to_coatoms, coatom_to_atoms, face_constructor)
        sage: L
        Finite poset containing 8 elements
        sage: for level in L.level_sets(): print level
        [((), (0, 1, 2))]
        [((0,), (0, 1)), ((1,), (0, 2)), ((2,), (1, 2))]
        [((0, 1), (0,)), ((0, 2), (1,)), ((1, 2), (2,))]
        [((0, 1, 2), ())]

    For more involved examples see the source code of
    :meth:`~ConvexRationalPolyhedralCone.face_lattice` and
    :meth:`~RationalPolyhedralFan.cone_lattice`.
    """
    def default_face_constructor(atoms, coatoms, **kwds):
        return (atoms, coatoms)
    if face_constructor is None:
        face_constructor = default_face_constructor

    atom_to_coatoms = [frozenset(atc) for atc in atom_to_coatoms]
    A = frozenset(range(len(atom_to_coatoms)))  # All atoms
    coatom_to_atoms = [frozenset(cta) for cta in coatom_to_atoms]
    C = frozenset(range(len(coatom_to_atoms)))  # All coatoms
    # Comments with numbers correspond to steps in Section 2.5 of the article
    L = DiGraph()       # 3: initialize L
    faces = dict()
    atoms = frozenset()
    coatoms = C
    faces[atoms, coatoms] = 0
    next_index = 1
    Q = [(atoms, coatoms)]              # 4: initialize Q with the empty face
    while Q:                            # 5
        q_atoms, q_coatoms = Q.pop()    # 6: remove some q from Q
        q = faces[q_atoms, q_coatoms]
        # 7: compute H = {closure(q+atom) : atom not in atoms of q}
        H = dict()
        candidates = set(A.difference(q_atoms))
        for atom in candidates:
            coatoms = q_coatoms.intersection(atom_to_coatoms[atom])
            atoms = A
            for coatom in coatoms:
                atoms = atoms.intersection(coatom_to_atoms[coatom])
            H[atom] = (atoms, coatoms)
        # 8: compute the set G of minimal sets in H
        minimals = set([])
        while candidates:
            candidate = candidates.pop()
            atoms = H[candidate][0]
            if atoms.isdisjoint(candidates) and atoms.isdisjoint(minimals):
                minimals.add(candidate)
        # Now G == {H[atom] : atom in minimals}
        for atom in minimals:   # 9: for g in G:
            g_atoms, g_coatoms = H[atom]
            if (g_atoms, g_coatoms) in faces:
                g = faces[g_atoms, g_coatoms]
            else:               # 11: if g was newly created
                g = next_index
                faces[g_atoms, g_coatoms] = g
                next_index += 1
                Q.append((g_atoms, g_coatoms))  # 12
            L.add_edge(q, g)                    # 14
    # End of algorithm, now construct a FinitePoset
    # In principle, it is recommended to use Poset or in this case perhaps
    # even LatticePoset, but it seems to take several times more time
    # than the above computation, makes unnecessary copies, and crashes.
    # So for now we will mimick the relevant code from Poset.
    # Relabel vertices so {0,...,n} becomes a linear extension of the poset.
    labels = dict()
    for new, old in enumerate(L.topological_sort()):
        labels[old] = new
    L.relabel(labels)
    # Set element labels.
    elements = [None] * next_index
    for face, index in faces.items():
        elements[labels[index]] = face_constructor(*face, **kwds)
    return FinitePoset(L, elements)
