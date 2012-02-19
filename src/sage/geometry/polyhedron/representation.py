"""
H(yperplane) and V(ertex) representation objects for polyhedra
"""

########################################################################
#       Copyright (C) 2008 Marshall Hampton <hamptonio@gmail.com>
#       Copyright (C) 2011 Volker Braun <vbraun.name@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
########################################################################


from sage.structure.sage_object import SageObject
from sage.structure.element import is_Vector
from sage.rings.all import QQ, ZZ, RDF
from sage.modules.free_module_element import vector
from sage.misc.all import cached_method



#########################################################################
#                      PolyhedronRepresentation
#                       /                     \
#                      /                       \
#              Hrepresentation            Vrepresentation
#                   /     \                 /     |   \
#                  /       \               /      |    \
#           Inequality  Equation        Vertex   Ray   Line

class PolyhedronRepresentation(SageObject):
    """
    The internal base class for all representation objects of
    ``Polyhedron`` (vertices/rays/lines and inequalites/equations)

    .. note::

        You should not (and cannot) instantiate it yourself. You can
        only obtain them from a Polyhedron() class.

    """

    # Numeric values for the output of the type() method
    INEQUALITY = 0
    EQUATION = 1
    VERTEX = 2
    RAY = 3
    LINE = 4

    def __init__(self, polyhedron, data):
        """
        Initializes the PolyhedronRepresentation object.

        TESTS::

            sage: import sage.geometry.polyhedron.representation as P
            sage: pr = P.PolyhedronRepresentation(Polyhedron(vertices = [[1,2,3]]), [1,2,3])
            sage: tuple(pr)
            (1, 2, 3)
            sage: TestSuite(pr).run(skip='_test_pickling')
        """
        self._representation_data = tuple(data)
        self._polyhedron = polyhedron

    def __len__(self):
        """
        Returns the length of the representation data.

        TESTS::

            sage: import sage.geometry.polyhedron.representation as P
            sage: pr = P.PolyhedronRepresentation(Polyhedron(vertices = [[1,2,3]]), [1,2,3])
            sage: pr.__len__()
            3
        """
        return len(self._representation_data)

    def __getitem__(self, i):
        """
        Supports indexing.

        TESTS::

            sage: import sage.geometry.polyhedron.representation as P
            sage: pr = P.PolyhedronRepresentation(Polyhedron(vertices = [[1,2,3]]), [1,2,3])
            sage: pr.__getitem__(1)
            2
        """
        return self._representation_data[i]

    def polyhedron(self):
        """
        Returns the underlying polyhedron.

        TESTS::

            sage: import sage.geometry.polyhedron.representation as P
            sage: pr = P.PolyhedronRepresentation(Polyhedron(vertices = [[1,2,3]]), [1,2,3])
            sage: pr.polyhedron()
            A 0-dimensional polyhedron in QQ^3 defined as the convex hull of 1 vertex
        """
        return self._polyhedron

    def __call__(self):
        """
        Returns the vector representation of the representation
        object. Shorthand for the vector() method.

        Note that the vector() method is only implemented in derived
        classes.

        TESTS::

            sage: import sage.geometry.polyhedron.representation as P
            sage: pr = Polyhedron(vertices = [[1,2,3]]).Vrepresentation(0)
            sage: pr.__call__()
            (1, 2, 3)

            sage: pr = P.PolyhedronRepresentation(Polyhedron(vertices = [[1,2,3]]), [1,2,3])
            sage: pr.__call__()
            Traceback (most recent call last):
            ...
            AttributeError: 'PolyhedronRepresentation' object has no attribute 'vector'
        """
        return self.vector()

    def index(self):
        """
        Returns an arbitrary but fixed number according to the internal
        storage order.

        NOTES:

        H-representation and V-representation objects are enumerated
        independently. That is, amongst all vertices/rays/lines there
        will be one with ``index()==0``, and amongs all
        inequalities/equations there will be one with ``index()==0``,
        unless the polyhedron is empty or spans the whole space.

        EXAMPLES::

            sage: s = Polyhedron(vertices=[[1],[-1]])
            sage: first_vertex = s.vertex_generator().next()
            sage: first_vertex.index()
            0
            sage: first_vertex == s.Vrepresentation(0)
            True
        """
        return self._index



class Hrepresentation(PolyhedronRepresentation):
    """
    The internal base class for H-representation objects of
    a polyhedron. Inherits from ``PolyhedronRepresentation``.
    """
    def __init__(self, polyhedron, data):
        """
        Initialization function.

        TESTS::

            sage: p = Polyhedron(ieqs = [[0,1,0],[0,0,1],[1,-1,0,],[1,0,-1]])
            sage: pH = p.Hrepresentation(0)
            sage: TestSuite(pH).run(skip='_test_pickling')
        """
        if len(data) != 1+polyhedron.ambient_dim():
            raise ValueError, \
                'H-representation data requires a list of length ambient_dim+1'
        super(Hrepresentation, self).__init__(polyhedron, data)
        self._index = len(polyhedron._Hrepresentation)
        polyhedron._Hrepresentation.append(self)

    @cached_method
    def vector(self):
        """
        Returns the vector representation of the H-representation object.

        OUTPUT:

        A vector of length
        :meth:`~sage.geometry.polyhedron.base.Polyhedron_base.ambient_dim` + 1.

        EXAMPLES::

            sage: s = polytopes.cuboctahedron()
            sage: v = s.vertex_generator().next()
            sage: v
            A vertex at (-1/2, -1/2, 0)
            sage: v.vector()
            (-1/2, -1/2, 0)
            sage: v()
            (-1/2, -1/2, 0)
            sage: type(v())
            <type 'sage.modules.vector_rational_dense.Vector_rational_dense'>
        """
        return self.polyhedron().Hrepresentation_space()(self._representation_data)

    def is_H(self):
        """
        Returns True if the object is part of a H-representation
        (inequality or equation).

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,1,0],[0,0,1],[1,-1,0,],[1,0,-1]])
            sage: pH = p.Hrepresentation(0)
            sage: pH.is_H()
            True
        """
        return True

    def is_inequality(self):
        """
        Returns True if the object is an inequality of the H-representation.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,1,0],[0,0,1],[1,-1,0,],[1,0,-1]])
            sage: pH = p.Hrepresentation(0)
            sage: pH.is_inequality()
            True
        """
        return False

    def is_equation(self):
        """
        Returns True if the object is an equation of the H-representation.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,1,0],[0,0,1],[1,-1,0,],[1,0,-1]], eqns = [[1,1,-1]])
            sage: pH = p.Hrepresentation(0)
            sage: pH.is_equation()
            True
        """
        return False

    @cached_method
    def A(self):
        r"""
        Returns the coefficient vector `A` in `A\vec{x}+b`.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,1,0],[0,0,1],[1,-1,0,],[1,0,-1]])
            sage: pH = p.Hrepresentation(2)
            sage: pH.A()
            (1, 0)
        """
        return self.polyhedron().ambient_space()(self._representation_data[1:])

    @cached_method
    def b(self):
        r"""
        Returns the constant `b` in `A\vec{x}+b`.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,1,0],[0,0,1],[1,-1,0,],[1,0,-1]])
            sage: pH = p.Hrepresentation(2)
            sage: pH.b()
            0
        """
        return self._representation_data[0]

    def neighbors(self):
        """
        Iterate over the adjacent facets (i.e. inequalities/equations)

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,0,0,1],[0,0,1,0,],[0,1,0,0],
            ...                          [1,-1,0,0],[1,0,-1,0,],[1,0,0,-1]])
            sage: pH = p.Hrepresentation(0)
            sage: a = list(pH.neighbors())
            sage: a[0]
            An inequality (0, -1, 0) x + 1 >= 0
            sage: list(a[0])
            [1, 0, -1, 0]
        """
        adjacency_matrix = self.polyhedron().facet_adjacency_matrix()
        for x in self.polyhedron().Hrep_generator():
            if adjacency_matrix[self.index(), x.index()] == 1:
                yield x

    def adjacent(self):
        """
        Alias for neighbors().

        TESTS::

            sage: p = Polyhedron(ieqs = [[0,0,0,2],[0,0,1,0,],[0,10,0,0],
            ...       [1,-1,0,0],[1,0,-1,0,],[1,0,0,-1]])
            sage: pH = p.Hrepresentation(0)
            sage: a = list(pH.neighbors())
            sage: b = list(pH.adjacent())
            sage: a==b
            True
        """
        return self.neighbors()

    def is_incident(self, Vobj):
        """
        Returns whether the incidence matrix element (Vobj,self) == 1

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,0,0,1],[0,0,1,0,],[0,1,0,0],
            ...       [1,-1,0,0],[1,0,-1,0,],[1,0,0,-1]])
            sage: pH = p.Hrepresentation(0)
            sage: pH.is_incident(p.Vrepresentation(1))
            True
            sage: pH.is_incident(p.Vrepresentation(5))
            False
        """
        return self.polyhedron().incidence_matrix()[Vobj.index(), self.index()] == 1

    def __mul__(self, Vobj):
        """
        Shorthand for ``self.eval(x)``

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,0,0,1],[0,0,1,0,],[0,1,0,0],
            ...        [1,-1,0,0],[1,0,-1,0,],[1,0,0,-1]])
            sage: pH = p.Hrepresentation(0)
            sage: pH*p.Vrepresentation(5)
            1
        """
        return self.eval(Vobj)

    def eval(self, Vobj):
        r"""
        Evaluates the left hand side `A\vec{x}+b` on the given
        vertex/ray/line.

        NOTES:

          * Evaluating on a vertex returns `A\vec{x}+b`
          * Evaluating on a ray returns `A\vec{r}`. Only the sign or
            whether it is zero is meaningful.
          * Evaluating on a line returns `A\vec{l}`. Only whether it
            is zero or not is meaningful.

        EXAMPLES::

            sage: triangle = Polyhedron(vertices=[[1,0],[0,1],[-1,-1]])
            sage: ineq = triangle.inequality_generator().next()
            sage: ineq
            An inequality (2, -1) x + 1 >= 0
            sage: [ ineq.eval(v) for v in triangle.vertex_generator() ]
            [0, 0, 3]
            sage: [ ineq * v for v in triangle.vertex_generator() ]
            [0, 0, 3]

        If you pass a vector, it is assumed to be the coordinate vector of a point::

            sage: ineq.eval( vector(ZZ, [3,2]) )
            5
        """
        if is_Vector(Vobj):
            return self.A() * Vobj + self.b()
        return Vobj.evaluated_on(self)
        #return self.A() * Vobj.vector() + self.b()

    def incident(self):
        """
        Returns a generator for the incident H-representation objects,
        that is, the vertices/rays/lines satisfying the (in)equality.

        EXAMPLES::

            sage: triangle = Polyhedron(vertices=[[1,0],[0,1],[-1,-1]])
            sage: ineq = triangle.inequality_generator().next()
            sage: ineq
            An inequality (2, -1) x + 1 >= 0
            sage: [ v for v in ineq.incident()]
            [A vertex at (-1, -1), A vertex at (0, 1)]
            sage: p = Polyhedron(vertices=[[0,0,0],[0,1,0],[0,0,1]], rays=[[1,-1,-1]])
            sage: ineq = p.Hrepresentation(2)
            sage: ineq
            An inequality (1, 0, 1) x + 0 >= 0
            sage: [ x for x in ineq.incident() ]
            [A vertex at (0, 0, 0),
             A vertex at (0, 1, 0),
             A ray in the direction (1, -1, -1)]
        """
        incidence_matrix = self.polyhedron().incidence_matrix()
        for V in self.polyhedron().Vrep_generator():
            if incidence_matrix[V.index(), self.index()] == 1:
                yield V


class Inequality(Hrepresentation):
    """
    A linear inequality (supporting hyperplane) of the
    polyhedron. Inherits from ``Hrepresentation``.
    """
    def __init__(self, polyhedron, data):
        """
        A linear inequality (supporting hyperplane) of the
        polyhedron. Inherits from ``Hrepresentation``.

        TESTS::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: a = p.inequality_generator().next()
            sage: a
            An inequality (-1, 1, 0) x + 0 >= 0
            sage: TestSuite(a).run(skip='_test_pickling')
        """
        super(Inequality, self).__init__(polyhedron, data)


    def type(self):
        r"""
        Returns the type (equation/inequality/vertex/ray/line) as an
        integer.

        OUTPUT:

        Integer. One of ``PolyhedronRepresentation.INEQUALITY``,
        ``.EQUATION``, ``.VERTEX``, ``.RAY``, or ``.LINE``.

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: repr_obj = p.inequality_generator().next()
            sage: repr_obj.type()
            0
            sage: repr_obj.type() == repr_obj.INEQUALITY
            True
            sage: repr_obj.type() == repr_obj.EQUATION
            False
            sage: repr_obj.type() == repr_obj.VERTEX
            False
            sage: repr_obj.type() == repr_obj.RAY
            False
            sage: repr_obj.type() == repr_obj.LINE
            False
        """
        return self.INEQUALITY


    def is_inequality(self):
        """
        Returns True since this is, by construction, an inequality.

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: a = p.inequality_generator().next()
            sage: a.is_inequality()
            True
        """
        return True

    def _repr_(self):
        """
        The string representation of the inequality.

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: a = p.inequality_generator().next()
            sage: a._repr_()
            'An inequality (-1, 1, 0) x + 0 >= 0'
            sage: Polyhedron(ieqs=[(1,-1),(-1,2)]).Hrepresentation()
            (An inequality (-1) x + 1 >= 0, An inequality (2) x - 1 >= 0)
            sage: Polyhedron(eqns=[(1,0)]).Hrepresentation()
            (An equation -1 == 0,)
            sage: Polyhedron(eqns=[(-1,0)]).Hrepresentation()
            (An equation -1 == 0,)
        """
        s = 'An inequality '
        have_A = not self.A().is_zero()
        if have_A:
            s += repr(self.A()) + ' x '
        if self.b()>=0:
            if have_A:
                s += '+'
        else:
            s += '-'
        if have_A:
            s += ' '
        s += repr(abs(self.b())) + ' >= 0'
        return s

    def contains(self, Vobj):
        """
        Tests whether the halfspace (including its boundary) defined
        by the inequality contains the given vertex/ray/line.

        EXAMPLES::

            sage: p = polytopes.cross_polytope(3)
            sage: i1 = p.inequality_generator().next()
            sage: [i1.contains(q) for q in p.vertex_generator()]
            [True, True, True, True, True, True]
            sage: p2 = 3*polytopes.n_cube(3)
            sage: [i1.contains(q) for q in p2.vertex_generator()]
            [True, False, False, False, True, True, True, False]
        """
        try:
            if Vobj.is_vector(): # assume we were passed a point
                return self.polyhedron()._is_nonneg( self.eval(Vobj) )
        except AttributeError:
            pass

        if Vobj.is_line():
            return self.polyhedron()._is_zero( self.eval(Vobj) )
        else:
            return self.polyhedron()._is_nonneg( self.eval(Vobj) )

    def interior_contains(self, Vobj):
        """
        Tests whether the interior of the halfspace (excluding its
        boundary) defined by the inequality contains the given
        vertex/ray/line.

        EXAMPLES::

            sage: p = polytopes.cross_polytope(3)
            sage: i1 = p.inequality_generator().next()
            sage: [i1.interior_contains(q) for q in p.vertex_generator()]
            [False, True, True, False, False, True]
            sage: p2 = 3*polytopes.n_cube(3)
            sage: [i1.interior_contains(q) for q in p2.vertex_generator()]
            [True, False, False, False, True, True, True, False]

        If you pass a vector, it is assumed to be the coordinate vector of a point::

            sage: P = Polyhedron(vertices=[[1,1],[1,-1],[-1,1],[-1,-1]])
            sage: p = vector(ZZ, [1,0] )
            sage: [ ieq.interior_contains(p) for ieq in P.inequality_generator() ]
            [True, True, False, True]
        """
        try:
            if Vobj.is_vector(): # assume we were passed a point
                return self.polyhedron()._is_positive( self.eval(Vobj) )
        except AttributeError:
            pass

        if Vobj.is_line():
            return self.polyhedron()._is_zero( self.eval(Vobj) )
        elif Vobj.is_vertex():
            return self.polyhedron()._is_positive( self.eval(Vobj) )
        else: # Vobj.is_ray()
            return self.polyhedron()._is_nonneg( self.eval(Vobj) )


class Equation(Hrepresentation):
    """
    A linear equation of the polyhedron. That is, the polyhedron is
    strictly smaller-dimensional than the ambient space, and contained
    in this hyperplane. Inherits from ``Hrepresentation``.
    """
    def __init__(self, polyhedron, data):
        """
        Initializes an equation object.

        TESTS::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: a = p.equation_generator().next()
            sage: a
            An equation (0, 0, 1) x + 0 == 0
            sage: TestSuite(a).run(skip='_test_pickling')
        """
        super(Equation, self).__init__(polyhedron, data)


    def type(self):
        r"""
        Returns the type (equation/inequality/vertex/ray/line) as an
        integer.

        OUTPUT:

        Integer. One of ``PolyhedronRepresentation.INEQUALITY``,
        ``.EQUATION``, ``.VERTEX``, ``.RAY``, or ``.LINE``.

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: repr_obj = p.equation_generator().next()
            sage: repr_obj.type()
            1
            sage: repr_obj.type() == repr_obj.INEQUALITY
            False
            sage: repr_obj.type() == repr_obj.EQUATION
            True
            sage: repr_obj.type() == repr_obj.VERTEX
            False
            sage: repr_obj.type() == repr_obj.RAY
            False
            sage: repr_obj.type() == repr_obj.LINE
            False
        """
        return self.EQUATION


    def is_equation(self):
        """
        Tests if this object is an equation.  By construction, it must be.

        TESTS::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: a = p.equation_generator().next()
            sage: a.is_equation()
            True
        """
        return True

    def _repr_(self):
        """
        A string representation of this object.

        TESTS::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: a = p.equation_generator().next()
            sage: a._repr_()
            'An equation (0, 0, 1) x + 0 == 0'
            sage: Polyhedron().Hrepresentation(0)
            An equation -1 == 0
        """
        s = 'An equation '
        have_A = not self.A().is_zero()
        if have_A:
            s += repr(self.A()) + ' x '
        if self.b()>=0:
            if have_A:
                s += '+'
        else:
            s += '-'
        if have_A:
            s += ' '
        s += repr(abs(self.b())) + ' == 0'
        return s

    def contains(self, Vobj):
        """
        Tests whether the hyperplane defined by the equation contains
        the given vertex/ray/line.

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: v = p.vertex_generator().next()
            sage: v
            A vertex at (0, 0, 0)
            sage: a = p.equation_generator().next()
            sage: a
            An equation (0, 0, 1) x + 0 == 0
            sage: a.contains(v)
            True
        """
        return self.polyhedron()._is_zero( self.eval(Vobj) )

    def interior_contains(self, Vobj):
        """
        Tests whether the interior of the halfspace (excluding its
        boundary) defined by the inequality contains the given
        vertex/ray/line.

        NOTE:

        Returns False for any equation.

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: v = p.vertex_generator().next()
            sage: v
            A vertex at (0, 0, 0)
            sage: a = p.equation_generator().next()
            sage: a
            An equation (0, 0, 1) x + 0 == 0
            sage: a.interior_contains(v)
            False
        """
        return False


class Vrepresentation(PolyhedronRepresentation):
    """
    The base class for V-representation objects of a
    polyhedron. Inherits from ``PolyhedronRepresentation``.
    """
    def __init__(self, polyhedron, data):
        """
        Initialization function for the vertex representation.

        TESTS::

            sage: p = Polyhedron(ieqs = [[1, 0, 0, 0, 1], [1, 1, 0, 0, 0], [1, 0, 1, 0, 0]])
            sage: from sage.geometry.polyhedron.representation import Vrepresentation
            sage: p._Vrepresentation = Sequence([])
            sage: vr = Vrepresentation(p,[1,2,3,4])
            sage: vr.__init__(p,[1,2,3,5])
            sage: vr.vector()
            (1, 2, 3, 5)
            sage: TestSuite(vr).run(skip='_test_pickling')
        """
        if len(data) != polyhedron.ambient_dim():
            raise ValueError, \
                'V-representation data requires a list of length ambient_dim'
        super(Vrepresentation, self).__init__(polyhedron, data)
        self._index = len(polyhedron._Vrepresentation)
        polyhedron._Vrepresentation.append(self)

    @cached_method
    def vector(self):
        """
        Returns the vector representation of the V-representation object.

        OUTPUT:

        A vector of length
        :meth:`~sage.geometry.polyhedron.base.Polyhedron_base.ambient_dim`.

        EXAMPLES::

            sage: s = polytopes.cuboctahedron()
            sage: v = s.vertex_generator().next()
            sage: v
            A vertex at (-1/2, -1/2, 0)
            sage: v.vector()
            (-1/2, -1/2, 0)
            sage: v()
            (-1/2, -1/2, 0)
            sage: type(v())
            <type 'sage.modules.vector_rational_dense.Vector_rational_dense'>
        """
        return self.polyhedron().Vrepresentation_space()(self._representation_data)

    def is_V(self):
        """
        Returns True if the object is part of a V-representation
        (a vertex, ray, or line).

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0],[1,0],[0,3],[1,3]])
            sage: v = p.vertex_generator().next()
            sage: v.is_V()
            True
        """
        return True

    def is_vertex(self):
        """
        Returns True if the object is a vertex of the V-representation.
        This method is over-ridden by the corresponding method in the
        derived class Vertex.

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0],[1,0],[0,3],[1,3]])
            sage: v = p.vertex_generator().next()
            sage: v.is_vertex()
            True
            sage: p = Polyhedron(ieqs = [[1, 0, 0, 0, 1], [1, 1, 0, 0, 0], [1, 0, 1, 0, 0]])
            sage: r1 = p.ray_generator().next()
            sage: r1.is_vertex()
            False
        """
        return False

    def is_ray(self):
        """
        Returns True if the object is a ray of the V-representation.
        This method is over-ridden by the corresponding method in the
        derived class Ray.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[1, 0, 0, 0, 1], [1, 1, 0, 0, 0], [1, 0, 1, 0, 0]])
            sage: r1 = p.ray_generator().next()
            sage: r1.is_ray()
            True
            sage: v1 = p.vertex_generator().next()
            sage: v1
            A vertex at (-1, -1, 0, -1)
            sage: v1.is_ray()
            False
        """
        return False

    def is_line(self):
        """
        Returns True if the object is a line of the V-representation.
        This method is over-ridden by the corresponding method in the
        derived class Line.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[1, 0, 0, 0, 1], [1, 1, 0, 0, 0], [1, 0, 1, 0, 0]])
            sage: line1 = p.line_generator().next()
            sage: line1.is_line()
            True
            sage: v1 = p.vertex_generator().next()
            sage: v1.is_line()
            False
        """
        return False

    def neighbors(self):
        """
        Returns a generator for the adjacent vertices/rays/lines.

        EXAMPLES::

             sage: p = Polyhedron(vertices = [[0,0],[1,0],[0,3],[1,4]])
             sage: v = p.vertex_generator().next()
             sage: v.neighbors().next()
             A vertex at (0, 3)
        """
        adjacency_matrix = self.polyhedron().vertex_adjacency_matrix()
        for x in self.polyhedron().Vrep_generator():
            if adjacency_matrix[self.index(), x.index()] == 1:
                yield x

    def adjacent(self):
        """
        Alias for neighbors().

        TESTS::

            sage: p = Polyhedron(vertices = [[0,0],[1,0],[0,3],[1,4]])
            sage: v = p.vertex_generator().next()
            sage: a = v.neighbors().next()
            sage: b = v.adjacent().next()
            sage: a==b
            True
        """
        return self.neighbors()

    def is_incident(self, Hobj):
        """
        Returns whether the incidence matrix element (self,Hobj) == 1

        EXAMPLES::

            sage: p = polytopes.n_cube(3)
            sage: h1 = p.inequality_generator().next()
            sage: h1
            An inequality (0, 0, -1) x + 1 >= 0
            sage: v1 = p.vertex_generator().next()
            sage: v1
            A vertex at (-1, -1, -1)
            sage: v1.is_incident(h1)
            False
        """
        return self.polyhedron().incidence_matrix()[self.index(), Hobj.index()] == 1

    def __mul__(self, Hobj):
        """
        Shorthand for self.evaluated_on(Hobj)

        TESTS::

            sage: p = polytopes.n_cube(3)
            sage: h1 = p.inequality_generator().next()
            sage: v1 = p.vertex_generator().next()
            sage: v1.__mul__(h1)
            2
        """
        return self.evaluated_on(Hobj)

    def incident(self):
        """
        Returns a generator for the equations/inequalities that are satisfied on the given
        vertex/ray/line.

        EXAMPLES::

            sage: triangle = Polyhedron(vertices=[[1,0],[0,1],[-1,-1]])
            sage: ineq = triangle.inequality_generator().next()
            sage: ineq
            An inequality (2, -1) x + 1 >= 0
            sage: [ v for v in ineq.incident()]
            [A vertex at (-1, -1), A vertex at (0, 1)]
            sage: p = Polyhedron(vertices=[[0,0,0],[0,1,0],[0,0,1]], rays=[[1,-1,-1]])
            sage: ineq = p.Hrepresentation(2)
            sage: ineq
            An inequality (1, 0, 1) x + 0 >= 0
            sage: [ x for x in ineq.incident() ]
            [A vertex at (0, 0, 0),
             A vertex at (0, 1, 0),
             A ray in the direction (1, -1, -1)]
        """
        incidence_matrix = self.polyhedron().incidence_matrix()
        for H in self.polyhedron().Hrep_generator():
            if incidence_matrix[self.index(), H.index()] == 1:
                yield H


class Vertex(Vrepresentation):
    """
    A vertex of the polyhedron. Inherits from ``Vrepresentation``.
    """
    def __init__(self, polyhedron, data):
        """
        Initializes the vertex object.

        TESTS::

            sage: p = Polyhedron(ieqs = [[0,0,1],[0,1,0],[1,-1,0]])
            sage: v1 = p.vertex_generator().next()
            sage: v1
            A vertex at (1, 0)
            sage: TestSuite(v1).run(skip='_test_pickling')
        """
        super(Vertex, self).__init__(polyhedron, data)


    def type(self):
        r"""
        Returns the type (equation/inequality/vertex/ray/line) as an
        integer.

        OUTPUT:

        Integer. One of ``PolyhedronRepresentation.INEQUALITY``,
        ``.EQUATION``, ``.VERTEX``, ``.RAY``, or ``.LINE``.

        EXAMPLES::

            sage: p = Polyhedron(vertices = [[0,0,0],[1,1,0],[1,2,0]])
            sage: repr_obj = p.vertex_generator().next()
            sage: repr_obj.type()
            2
            sage: repr_obj.type() == repr_obj.INEQUALITY
            False
            sage: repr_obj.type() == repr_obj.EQUATION
            False
            sage: repr_obj.type() == repr_obj.VERTEX
            True
            sage: repr_obj.type() == repr_obj.RAY
            False
            sage: repr_obj.type() == repr_obj.LINE
            False
        """
        return self.VERTEX


    def is_vertex(self):
        """
        Tests if this object is a vertex.  By construction it always is.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,0,1],[0,1,0],[1,-1,0]])
            sage: a = p.vertex_generator().next()
            sage: a.is_vertex()
            True
        """
        return True

    def _repr_(self):
        """
        Returns a string representation of the vertex.

        OUTPUT:

        String.

        TESTS::

            sage: p = Polyhedron(ieqs = [[0,0,1],[0,1,0],[1,-1,0]])
            sage: v = p.vertex_generator().next()
            sage: v.__repr__()
            'A vertex at (1, 0)'
        """
        return 'A vertex at ' + repr(self.vector());

    def evaluated_on(self, Hobj):
        r"""
        Returns `A\vec{x}+b`

        EXAMPLES::

            sage: p = polytopes.n_cube(3)
            sage: v = p.vertex_generator().next()
            sage: h = p.inequality_generator().next()
            sage: v
            A vertex at (-1, -1, -1)
            sage: h
            An inequality (0, 0, -1) x + 1 >= 0
            sage: v.evaluated_on(h)
            2
        """
        return Hobj.A() * self.vector() + Hobj.b()

    @cached_method
    def is_integral(self):
        r"""
        Return whether the coordinates of the vertex are all integral.

        OUTPUT:

        Boolean.

        EXAMPLES::

            sage: p = Polyhedron([(1/2,3,5), (0,0,0), (2,3,7)])
            sage: [ v.is_integral() for v in p.vertex_generator() ]
            [True, False, True]
        """
        return all(x in ZZ for x in self._representation_data)


class Ray(Vrepresentation):
    """
    A ray of the polyhedron. Inherits from ``Vrepresentation``.
    """
    def __init__(self, polyhedron, data):
        """
        Initializes a ray object.

        TESTS::

            sage: p = Polyhedron(ieqs = [[0,0,1],[0,1,0],[1,-1,0]])
            sage: r1 = p.ray_generator().next()
            sage: r1
            A ray in the direction (0, 1)
            sage: TestSuite(r1).run(skip='_test_pickling')
        """
        super(Ray, self).__init__(polyhedron, data)


    def type(self):
        r"""
        Returns the type (equation/inequality/vertex/ray/line) as an
        integer.

        OUTPUT:

        Integer. One of ``PolyhedronRepresentation.INEQUALITY``,
        ``.EQUATION``, ``.VERTEX``, ``.RAY``, or ``.LINE``.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,0,1],[0,1,0],[1,-1,0]])
            sage: repr_obj = p.ray_generator().next()
            sage: repr_obj.type()
            3
            sage: repr_obj.type() == repr_obj.INEQUALITY
            False
            sage: repr_obj.type() == repr_obj.EQUATION
            False
            sage: repr_obj.type() == repr_obj.VERTEX
            False
            sage: repr_obj.type() == repr_obj.RAY
            True
            sage: repr_obj.type() == repr_obj.LINE
            False
        """
        return self.RAY


    def is_ray(self):
        """
        Tests if this object is a ray.  Always True by construction.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,0,1],[0,1,0],[1,-1,0]])
            sage: a = p.ray_generator().next()
            sage: a.is_ray()
            True
        """
        return True

    def _repr_(self):
        """
        A string representation of the ray.

        TESTS::

            sage: p = Polyhedron(ieqs = [[0,0,1],[0,1,0],[1,-1,0]])
            sage: a = p.ray_generator().next()
            sage: a._repr_()
            'A ray in the direction (0, 1)'
        """
        return 'A ray in the direction ' + repr(self.vector());

    def evaluated_on(self, Hobj):
        r"""
        Returns `A\vec{r}`

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[0,0,1],[0,1,0],[1,-1,0]])
            sage: a = p.ray_generator().next()
            sage: h = p.inequality_generator().next()
            sage: a.evaluated_on(h)
            0
        """
        return Hobj.A() * self.vector()


class Line(Vrepresentation):
    r"""
    A line (Minkowski summand `\simeq\RR`) of the
    polyhedron. Inherits from ``Vrepresentation``.
    """
    def __init__(self, polyhedron, data):
        """
        Initializes the line object.

        TESTS::

            sage: p = Polyhedron(ieqs = [[1, 0, 0, 1],[1,1,0,0]])
            sage: a = p.line_generator().next()
            sage: p._Vrepresentation = Sequence([])
            sage: a.__init__(p,[1,2,3])
            sage: a
            A line in the direction (1, 2, 3)
            sage: TestSuite(a).run(skip='_test_pickling')
        """
        super(Line, self).__init__(polyhedron, data)


    def type(self):
        r"""
        Returns the type (equation/inequality/vertex/ray/line) as an
        integer.

        OUTPUT:

        Integer. One of ``PolyhedronRepresentation.INEQUALITY``,
        ``.EQUATION``, ``.VERTEX``, ``.RAY``, or ``.LINE``.

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[1, 0, 0, 1],[1,1,0,0]])
            sage: repr_obj = p.line_generator().next()
            sage: repr_obj.type()
            4
            sage: repr_obj.type() == repr_obj.INEQUALITY
            False
            sage: repr_obj.type() == repr_obj.EQUATION
            False
            sage: repr_obj.type() == repr_obj.VERTEX
            False
            sage: repr_obj.type() == repr_obj.RAY
            False
            sage: repr_obj.type() == repr_obj.LINE
            True
        """
        return self.LINE


    def is_line(self):
        """
        Tests if the object is a line.  By construction it must be.

        TESTS::

            sage: p = Polyhedron(ieqs = [[1, 0, 0, 1],[1,1,0,0]])
            sage: a = p.line_generator().next()
            sage: a.is_line()
            True
        """
        return True

    def _repr_(self):
        """
        A string representation of the line.

        TESTS::

            sage: p = Polyhedron(ieqs = [[1, 0, 0, 1],[1,1,0,0]])
            sage: a = p.line_generator().next()
            sage: a.__repr__()
            'A line in the direction (0, 1, 0)'
        """
        return 'A line in the direction ' + repr(self.vector());

    def evaluated_on(self, Hobj):
        r"""
        Returns `A\vec{\ell}`

        EXAMPLES::

            sage: p = Polyhedron(ieqs = [[1, 0, 0, 1],[1,1,0,0]])
            sage: a = p.line_generator().next()
            sage: h = p.inequality_generator().next()
            sage: a.evaluated_on(h)
            0
        """
        return Hobj.A() * self.vector()
