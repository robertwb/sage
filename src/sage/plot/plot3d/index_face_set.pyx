"""
Graphics3D object that consists of a list of polygons, also used for
triangulations of other objects.

AUTHORS:
    -- Robert Bradshaw (2007-08-26): inital version
    -- Robert Bradshaw (2007-08-28): significant optimizations

TODO:
    -- Smooth triangles
"""


#*****************************************************************************
#      Copyright (C) 2007 Robert Bradshaw <robertwb@math.washington.edu>
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
#*****************************************************************************



include "../../ext/stdsage.pxi"
include "../../ext/interrupt.pxi"

cdef extern from *:
     void memset(void *, int, Py_ssize_t)
     void memcpy(void * dest, void * src, Py_ssize_t n)
     int sprintf_3d "sprintf" (char*, char*, double, double, double)
     int sprintf_3i "sprintf" (char*, char*, int, int, int)
     int sprintf_4i "sprintf" (char*, char*, int, int, int, int)
     int sprintf_5i "sprintf" (char*, char*, int, int, int, int, int)
     int sprintf_6i "sprintf" (char*, char*, int, int, int, int, int, int)
     int sprintf_9d "sprintf" (char*, char*, double, double, double, double, double, double, double, double, double)

include "../../ext/python_list.pxi"
include "../../ext/python_string.pxi"

include "point_c.pxi"


from math import sin, cos, sqrt
from random import randint

from sage.rings.real_double import RDF

from sage.matrix.constructor import matrix
from sage.modules.free_module_element import vector

from sage.plot.plot3d.base import Graphics3dGroup

from transform cimport Transformation



# --------------------------------------------------------------------
# Fast routines for generating string representations of the polygons.
# --------------------------------------------------------------------

cdef inline format_tachyon_triangle(point_c P, point_c Q, point_c R):
    cdef char ss[250]
    # PyString_FromFormat doesn't do floats?
    cdef Py_ssize_t r = sprintf_9d(ss,
                                   "TRI V0 %g %g %g V1 %g %g %g V2 %g %g %g",
                                   P.x, P.y, P.z,
                                   Q.x, Q.y, Q.z,
                                   R.x, R.y, R.z )
    return PyString_FromStringAndSize(ss, r)

cdef inline format_obj_vertex(point_c P):
    cdef char ss[100]
    # PyString_FromFormat doesn't do floats?
    cdef Py_ssize_t r = sprintf_3d(ss, "v %g %g %g", P.x, P.y, P.z)
    return PyString_FromStringAndSize(ss, r)

cdef inline format_obj_face(face_c face, int off):
    cdef char ss[100]
    cdef Py_ssize_t r, i
    if face.n == 3:
        r = sprintf_3i(ss, "f %d %d %d", face.vertices[0] + off, face.vertices[1] + off, face.vertices[2] + off)
    elif face.n == 4:
        r = sprintf_4i(ss, "f %d %d %d %d", face.vertices[0] + off, face.vertices[1] + off, face.vertices[2] + off, face.vertices[3] + off)
    else:
        return "f " + " ".join([str(face.vertices[i] + off) for i from 0 <= i < face.n])
    # PyString_FromFormat is almost twice as slow
    return PyString_FromStringAndSize(ss, r)

cdef inline format_obj_face_back(face_c face, int off):
    cdef char ss[100]
    cdef Py_ssize_t r, i
    if face.n == 3:
        r = sprintf_3i(ss, "f %d %d %d", face.vertices[2] + off, face.vertices[1] + off, face.vertices[0] + off)
    elif face.n == 4:
        r = sprintf_4i(ss, "f %d %d %d %d", face.vertices[3] + off, face.vertices[2] + off, face.vertices[1] + off, face.vertices[0] + off)
    else:
        return "f " + " ".join([str(face.vertices[i] + off) for i from face.n > i >= 0])
    return PyString_FromStringAndSize(ss, r)


cdef inline format_pmesh_vertex(point_c P):
    cdef char ss[100]
    # PyString_FromFormat doesn't do floats?
    cdef Py_ssize_t r = sprintf_3d(ss, "%g %g %g", P.x, P.y, P.z)
    return PyString_FromStringAndSize(ss, r)

cdef inline format_pmesh_face(face_c face):
    cdef char ss[100]
    cdef Py_ssize_t r, i
    if face.n == 3:
        r = sprintf_5i(ss, "%d\n%d\n%d\n%d\n%d", face.n+1,
                                                 face.vertices[0],
                                                 face.vertices[1],
                                                 face.vertices[2],
                                                 face.vertices[0])
    elif face.n == 4:
        r = sprintf_6i(ss, "%d\n%d\n%d\n%d\n%d\n%d", face.n+1,
                                                     face.vertices[0],
                                                     face.vertices[1],
                                                     face.vertices[2],
                                                     face.vertices[3],
                                                     face.vertices[0])
    else:
        # Naive triangulation
        all = []
        for i from 1 <= i < face.n-1:
            r = sprintf_4i(ss, "4\n%d\n%d\n%d\n%d", face.vertices[0],
                                                    face.vertices[i],
                                                    face.vertices[i+1],
                                                    face.vertices[0])
            PyList_Append(all, PyString_FromStringAndSize(ss, r))
        return "\n".join(all)
    # PyString_FromFormat is almost twice as slow
    return PyString_FromStringAndSize(ss, r)




cdef class IndexFaceSet(PrimitiveObject):

    """
    Graphics3D object that consists of a list of polygons, also used for
    triangulations of other objects.

    Polygons (mostly triangles and quadrilaterals) are stored in the
    c struct \code{face_c} (see transform.pyx). Rather than storing
    the points directly for each polygon, each face consists a list
    of pointers into a common list of points which are basically triples
    of doubles in a \code{point_c}.

    Usually these objects are not created directly by users.

    EXAMPLES:
        sage: from sage.plot.plot3d.index_face_set import IndexFaceSet
        sage: S = IndexFaceSet([[(1,0,0),(0,1,0),(0,0,1)],[(1,0,0),(0,1,0),(0,0,0)]])
        sage: S.face_list()
        [[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)], [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0)]]
        sage: S.vertex_list()
        [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0)]

        sage: def make_face(n): return [(0,0,n),(0,1,n),(1,1,n),(1,0,n)]
        sage: S = IndexFaceSet([make_face(n) for n in range(10)])
        sage: S.show()

        sage: point_list = [(1,0,0),(0,1,0)] + [(0,0,n) for n in range(10)]
        sage: face_list = [[0,1,n] for n in range(2,10)]
        sage: S = IndexFaceSet(face_list, point_list, color='red')
        sage: S.face_list()
        [[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0)], [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)], [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 2.0)], [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 3.0)], [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 4.0)], [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 5.0)], [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 6.0)], [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 7.0)]]
        sage: S.show()
    """

    def __new__(self, faces, point_list=None, enclosed=False, **kwds):
        self.vs = <point_c *>NULL
        self.face_indices = <int *>NULL
        self._faces = <face_c *>NULL


    def __init__(self, faces, point_list=None, enclosed=False, **kwds):
        PrimitiveObject.__init__(self, **kwds)

        self.enclosed = enclosed

        if point_list is None:
            face_list = faces
            faces = []
            point_list = []
            point_index = {}
            for face in face_list:
                iface = []
                for p in face:
                    try:
                        ix = point_index[p]
                    except KeyError:
                        ix = len(point_list)
                        point_index[p] = ix
                        point_list.append(p)
                    iface.append(ix)
                faces.append(iface)

        cdef Py_ssize_t i
        cdef Py_ssize_t index_len = 0
        for i from 0 <= i < len(faces):
            index_len += len(faces[i])

        self.vcount = len(point_list)
        self.fcount = len(faces)
        self.icount = index_len

        self.realloc(self.vcount, self.fcount, index_len)

        for i from 0 <= i < self.vcount:
            self.vs[i].x, self.vs[i].y, self.vs[i].z = point_list[i]

        cdef int cur_pt = 0
        for i from 0 <= i < self.fcount:
            self._faces[i].n = len(faces[i])
            self._faces[i].vertices = &self.face_indices[cur_pt]
            for ix in faces[i]:
                self.face_indices[cur_pt] = ix
                cur_pt += 1

    cdef realloc(self, vcount, fcount, icount):
        if self.vs == NULL:
            self.vs = <point_c *> sage_malloc(sizeof(point_c) * vcount)
        else:
            self.vs = <point_c *> sage_realloc(self.vs, sizeof(point_c) * vcount)
        if self._faces == NULL:
            self._faces = <face_c *> sage_malloc(sizeof(face_c) * fcount)
        else:
            self._faces = <face_c *> sage_realloc(self._faces, sizeof(face_c) * fcount)
        if self.face_indices == NULL:
            self.face_indices = <int *> sage_malloc(sizeof(int) * icount)
        else:
            self.face_indices = <int *> sage_realloc(self.face_indices, sizeof(int) * icount)
        if self.vs == NULL or self.face_indices == NULL or self._faces == NULL:
            raise MemoryError, "Out of memory allocating triangulation for %s" % type(self)

    def _clean_point_list(self):
        # TODO: There is still wasted space where quadrilaterals were converted to triangles...
        #       but it's so little it's probably not worth bothering with
        cdef int* point_map = <int *>sage_malloc(sizeof(int) * self.vcount)
        if point_map == NULL:
            raise MemoryError, "Out of memory cleaning up for %s" % type(self)
        memset(point_map, 0, sizeof(int) * self.vcount)  # TODO: sage_calloc
        cdef Py_ssize_t i, j
        cdef face_c *face
        for i from 0 <= i < self.fcount:
            face = &self._faces[i]
            for j from 0 <= j < face.n:
                point_map[face.vertices[j]] += 1
        ix = 0
        for i from 0 <= i < self.vcount:
            if point_map[i] > 0:
                point_map[i] = ix
                self.vs[ix] = self.vs[i]
                ix += 1
        if ix != self.vcount:
            for i from 0 <= i < self.fcount:
                face = &self._faces[i]
                for j from 0 <= j < face.n:
                    face.vertices[j] = point_map[face.vertices[j]]
            self.realloc(ix, self.fcount, self.icount)
            self.vcount = ix
        sage_free(point_map)

    def _seperate_creases(self, threshold):
        """
        Some rendering engines Gouraud shading, which is great for smooth
        surfaces but looks bad if one actually has a polyhedron.

        INPUT:
            threshold -- the minimum cosine of the angle between adjacent faces
                         a higher threshold seperates more, all faces if >= 1,
                         no faces if <= -1
        """
        cdef Py_ssize_t i, j, k
        cdef face_c *face
        cdef int v, count, total = 0
        cdef int* point_counts = <int *>sage_malloc(sizeof(int) * (self.vcount * 2 + 1))
        # For each vertex, get number of faces
        if point_counts == NULL:
            raise MemoryError, "Out of memory in _seperate_creases for %s" % type(self)
        cdef int* running_point_counts = &point_counts[self.vcount]
        memset(point_counts, 0, sizeof(int) * self.vcount)
        for i from 0 <= i < self.fcount:
            face = &self._faces[i]
            total += face.n
            for j from 0 <= j < face.n:
                point_counts[face.vertices[j]] += 1
        # Running used as index into face list
        cdef int running = 0
        cdef int max = 0
        for i from 0 <= i < self.vcount:
            running_point_counts[i] = running
            running += point_counts[i]
            if point_counts[i] > max:
               max = point_counts[i]
        running_point_counts[self.vcount] = running
        # Create an array, indexed by running_point_counts[v], to the list of faces containing that vertex.
        cdef face_c** point_faces = <face_c **>sage_malloc(sizeof(face_c*) * total)
        if point_faces == NULL:
            sage_free(point_counts)
            raise MemoryError, "Out of memory in _seperate_creases for %s" % type(self)
        _sig_on
        memset(point_counts, 0, sizeof(int) * self.vcount)
        for i from 0 <= i < self.fcount:
            face = &self._faces[i]
            for j from 0 <= j < face.n:
                v = face.vertices[j]
                point_faces[running_point_counts[v]+point_counts[v]] = face
                point_counts[v] += 1
        # Now, for each vertex, see if all faces are close enough,
        # or if it is a crease.
        cdef face_c** faces
        cdef int start = 0
        cdef bint any
        # We compare against face 0, and if it's not flat enough we push it to the end.
        # Then we come around again to compare everything that was put at the end, possibly
        # pushing stuff to the end again (until no further changes are needed).
        while start < self.vcount:
            ix = self.vcount
            # Find creases
            for i from 0 <= i < self.vcount - start:
                faces = &point_faces[running_point_counts[i]]
                any = 0
                for j from point_counts[i] > j >= 1:
                    if cos_face_angle(faces[0][0], faces[j][0], self.vs) < threshold:
                        any = 1
                        face = faces[j]
                        point_counts[i] -= 1
                        if j != point_counts[i]:
                            faces[j] = faces[point_counts[i]] # swap
                            faces[point_counts[i]] = face
                if any:
                    ix += 1
            # Reallocate room for vertices at end
            if ix > self.vcount:
                self.vs = <point_c *>sage_realloc(self.vs, sizeof(point_c) * ix)
                if self.vs == NULL:
                    sage_free(point_counts)
                    sage_free(point_faces)
                    self.vcount = self.fcount = self.icount = 0 # so we don't get segfaults on bad points
                    _sig_off
                    raise MemoryError, "Out of memory in _seperate_creases for %s, CORRUPTED" % type(self)
                ix = self.vcount
                running = 0
                for i from 0 <= i < self.vcount - start:
                    if point_counts[i] != running_point_counts[i+1] - running_point_counts[i]:
                        # We have a new vertex
                        self.vs[ix] = self.vs[i+start]
                        # Update the point_counts and point_faces arrays for the next time around.
                        count = running_point_counts[i+1] - running_point_counts[i] - point_counts[i]
                        faces = &point_faces[running]
                        for j from 0 <= j < count:
                            faces[j] = point_faces[running_point_counts[i] + point_counts[i] + j]
                            face = faces[j]
                            for k from 0 <= k < face.n:
                                if face.vertices[k] == i + start:
                                    face.vertices[k] = ix
                        point_counts[ix-self.vcount] = count
                        running_point_counts[ix-self.vcount] = running
                        running += count
                        ix += 1
                running_point_counts[ix-self.vcount] = running
            start = self.vcount
            self.vcount = ix

        sage_free(point_counts)
        sage_free(point_faces)
        _sig_off



    def _mem_stats(self):
        return self.vcount, self.fcount, self.icount

    def __dealloc__(self):
        if self.vs != NULL:
            sage_free(self.vs)
        if self._faces != NULL:
            sage_free(self._faces)
        if self.face_indices != NULL:
            sage_free(self.face_indices)

    def is_enclosed(self):
        """
        Whether or not it is necessary to render the back sides of the polygons
        (assuming, of course, that they have the correct orientation).

        This is may be passed in on construction. It is also calculated
        in ParametricSurface by verifying the opposite edges of the rendered
        domain either line up or are pinched together.

        EXAMPLES:
            sage: from sage.plot.plot3d.index_face_set import IndexFaceSet
            sage: IndexFaceSet([[(0,0,1),(0,1,0),(1,0,0)]]).is_enclosed()
            False
        """
        return self.enclosed

    def index_faces(self):
        cdef Py_ssize_t i, j
        return [[self._faces[i].vertices[j] for j from 0 <= j < self._faces[i].n] for i from 0 <= i < self.fcount]

    def faces(self):
        """
        An iterator over the faces.

        EXAMPLES:
            sage: from sage.plot.plot3d.shapes import *
            sage: S = Box(1,2,3)
            sage: list(S.faces()) == S.face_list()
            True
        """
        return FaceIter(self)

    def face_list(self):
        points = self.vertex_list()
        cdef Py_ssize_t i, j
        return [[points[self._faces[i].vertices[j]] for j from 0 <= j < self._faces[i].n] for i from 0 <= i < self.fcount]

    def edges(self):
        return EdgeIter(self)

    def edge_list(self):
        # For consistancy
        return list(self.edges())

    def vertices(self):
        """
        An iterator over the vertices.

        EXAMPLES:
            sage: from sage.plot.plot3d.shapes import *
            sage: S = Cone(1,1)
            sage: list(S.vertices()) == S.vertex_list()
            True
        """
        return VertexIter(self)

    def vertex_list(self):
        cdef Py_ssize_t i
        return [(self.vs[i].x, self.vs[i].y, self.vs[i].z) for i from 0 <= i < self.vcount]

    def x3d_geometry(self):
        cdef Py_ssize_t i
        points = ",".join(["%s %s %s"%(self.vs[i].x, self.vs[i].y, self.vs[i].z) for i from 0 <= i < self.vcount])
        coordIndex = ",-1,".join([",".join([str(self._faces[i].vertices[j])
                                            for j from 0 <= j < self._faces[i].n])
                                  for i from 0 <= i < self.fcount])
        return """
<IndexedFaceSet coordIndex='%s,-1'>
  <Coordinate point='%s'/>
</IndexedFaceSet>
"""%(coordIndex, points)

    def bounding_box(self):
        if self.vcount == 0:
            return ((0,0,0),(0,0,0))

        cdef Py_ssize_t i
        cdef point_c low = self.vs[0], high = self.vs[0]
        for i from 1 <= i < self.vcount:
            point_c_lower_bound(&low, low, self.vs[i])
            point_c_upper_bound(&high, high, self.vs[i])
        return ((low.x, low.y, low.z), (high.x, high.y, high.z))

    def partition(self, f):
        """
        Partition the faces of self based on a map $f: \mathbb{R}^3 \leftarrow \mathbb{Z}$
        applied to the center of each face.
        """
        cdef Py_ssize_t i, j, ix, face_ix
        cdef int part
        cdef point_c P
        cdef face_c *face, *new_face
        cdef IndexFaceSet face_set

        cdef int *partition = <int *>sage_malloc(sizeof(int) * self.fcount)

        if partition == NULL:
            raise MemoryError
        part_counts = {}
        for i from 0 <= i < self.fcount:
            face = &self._faces[i]
            P = self.vs[face.vertices[0]]
            for j from 1 <= j < face.n:
                point_c_add(&P, P, self.vs[face.vertices[j]])
            point_c_mul(&P, P, 1.0/face.n)
            partition[i] = part = f(P.x, P.y, P.z)
            try:
                count = part_counts[part]
            except KeyError:
                part_counts[part] = count = [0,0]
            count[0] += 1
            count[1] += face.n
        all = {}
        for part, count in part_counts.iteritems():
            face_set = IndexFaceSet([])
            face_set.realloc(self.vcount, count[0], count[1])
            face_set.vcount = self.vcount
            face_set.fcount = count[0]
            face_set.icount = count[1]
            memcpy(face_set.vs, self.vs, sizeof(point_c) * self.vcount)
            face_ix = 0
            ix = 0
            for i from 0 <= i < self.fcount:
                if partition[i] == part:
                    face = &self._faces[i]
                    new_face = &face_set._faces[face_ix]
                    new_face.n = face.n
                    new_face.vertices = &face_set.face_indices[ix]
                    for j from 0 <= j < face.n:
                        new_face.vertices[j] = face.vertices[j]
                    face_ix += 1
                    ix += face.n
            face_set._clean_point_list()
            all[part] = face_set
        sage_free(partition)
        return all

    def tachyon_repr(self, render_params):
        """
        TESTS:
            sage: from sage.plot.plot3d.shapes import *
            sage: S = Cone(1,1)
            sage: s = S.tachyon_repr(S.default_render_params())
        """
        cdef Transformation transform = render_params.transform
        lines = []
        cdef point_c P, Q, R
        cdef face_c face
        cdef Py_ssize_t i, k
        _sig_on
        for i from 0 <= i < self.fcount:
            face = self._faces[i]
            if transform is not None:
                transform.transform_point_c(&P, self.vs[face.vertices[0]])
                transform.transform_point_c(&Q, self.vs[face.vertices[1]])
                transform.transform_point_c(&R, self.vs[face.vertices[2]])
            else:
                P = self.vs[face.vertices[0]]
                Q = self.vs[face.vertices[1]]
                R = self.vs[face.vertices[2]]
            PyList_Append(lines, format_tachyon_triangle(P, Q, R))
            PyList_Append(lines, self.texture.id)
            if face.n > 3:
                for k from 3 <= k < face.n:
                    Q = R
                    if transform is not None:
                        transform.transform_point_c(&R, self.vs[face.vertices[k]])
                    else:
                        R = self.vs[face.vertices[k]]
                    PyList_Append(lines, format_tachyon_triangle(P, Q, R))
                    PyList_Append(lines, self.texture.id)
        _sig_off

        return lines


    def obj_repr(self, render_params):
        """
        TESTS:
            sage: from sage.plot.plot3d.shapes import *
            sage: S = Cylinder(1,1)
            sage: s = S.obj_repr(S.default_render_params())
        """
        cdef Transformation transform = render_params.transform
        cdef int off = render_params.obj_vertex_offset
        cdef Py_ssize_t i
        cdef point_c res

        _sig_on
        if transform is None:
            points = [format_obj_vertex(self.vs[i]) for i from 0 <= i < self.vcount]
        else:
            points = []
            for i from 0 <= i < self.vcount:
                transform.transform_point_c(&res, self.vs[i])
                PyList_Append(points, format_obj_vertex(res))

        faces = [format_obj_face(self._faces[i], off) for i from 0 <= i < self.fcount]
        if not self.enclosed:
            back_faces = [format_obj_face_back(self._faces[i], off) for i from 0 <= i < self.fcount]
        else:
            back_faces = []

        render_params.obj_vertex_offset += self.vcount
        _sig_off

        return ["g " + render_params.unique_name('obj'),
                "usemtl " + self.texture.id,
                points,
                faces,
                back_faces]

    def jmol_repr(self, render_params):
        """
        TESTS:
          sage: from sage.plot.plot3d.shapes import *
          sage: S = Cylinder(1,1)
          sage: S.show()
        """
        cdef Transformation transform = render_params.transform
        cdef Py_ssize_t i
        cdef point_c res

        self._seperate_creases(render_params.crease_threshold)

        _sig_on
        if transform is None:
            points = [format_pmesh_vertex(self.vs[i]) for i from 0 <= i < self.vcount]
        else:
            points = []
            for i from 0 <= i < self.vcount:
                transform.transform_point_c(&res, self.vs[i])
                PyList_Append(points, format_pmesh_vertex(res))

        faces = [format_pmesh_face(self._faces[i]) for i from 0 <= i < self.fcount]

        # If a face has more than 4 vertices, it gets chopped up in format_pmesh_face
        cdef Py_ssize_t extra_faces = 0
        for i from 0 <= i < self.fcount:
            if self._faces[i].n >= 5:
                extra_faces += self._faces[i].n-3

        _sig_off

        all = [str(self.vcount),
               points,
               str(self.fcount + extra_faces),
               faces]

        from base import flatten_list
        name = render_params.unique_name('obj')
        all = flatten_list(all)
        if render_params.output_archive:
            filename = "%s.pmesh" % (name)
            render_params.output_archive.writestr(filename, '\n'.join(all))
        else:
            filename = "%s-%s.pmesh" % (render_params.output_file, name)
            f = open(filename, 'w')
            for line in all:
                f.write(line)
                f.write('\n')
            f.close()

        s = 'pmesh %s "%s"\n%s' % (name, filename, self.texture.jmol_str("pmesh"))

        # Turn on display of the mesh lines or dots?
        if render_params.mesh:
             s += '\npmesh %s mesh\n'%name
        if render_params.dots:
             s += '\npmesh %s dots\n'%name
        return [s]

    def dual(self, **kwds):

        cdef point_c P
        cdef face_c *face
        cdef Py_ssize_t i, j, ix, ff
        cdef IndexFaceSet dual = IndexFaceSet([], **kwds)
        cdef int incoming, outgoing

        dual.realloc(self.fcount, self.vcount, self.icount)

        _sig_on
        # is using dicts overly-heavy?
        dual_faces = [{} for i from 0 <= i < self.vcount]

        for i from 0 <= i < self.fcount:
            # Let the vertex be centered on the face according to a simple average
            face = &self._faces[i]
            dual.vs[i] = self.vs[face.vertices[0]]
            for j from 1 <= j < face.n:
                point_c_add(&dual.vs[i], dual.vs[i], self.vs[face.vertices[j]])
            point_c_mul(&dual.vs[i], dual.vs[i], 1.0/face.n)

            # Now compute the new face
            for j from 0 <= j < face.n:
                if j == 0:
                    incoming = face.vertices[face.n-1]
                else:
                    incoming = face.vertices[j-1]
                if j == face.n-1:
                    outgoing = face.vertices[0]
                else:
                    outgoing = face.vertices[j+1]
                dd = dual_faces[face.vertices[j]]
                dd[incoming] = i, outgoing

        i = 0
        ix = 0
        for dd in dual_faces:
            face = &dual._faces[i]
            face.n = len(dd)
            if face.n == 0: # skip unused vertices
                continue
            face.vertices = &dual.face_indices[ix]
            ff, next = dd.itervalues().next()
            face.vertices[0] = ff
            for j from 1 <= j < face.n:
                ff, next = dd[next]
                face.vertices[j] = ff
            i += 1
            ix += face.n

        dual.vcount = self.fcount
        dual.fcount = i
        dual.icount = ix
        _sig_off

        return dual


    def stickers(self, colors, width, hover):
        """
        Returns a group of IndexFaceSets

        INPUT:
            colors  - list of colors/textures to use (in cyclic order)
            width   - offset perpendicular into the edge (to creat a border)
                      may also be negative
            hover   - offset normal to the face (usually have to float above
                      the original surface so it shows, typically this value
                      is very small compared to the actual object

        OUTPUT:
            Graphics3dGroup of stickers

        EXAMPLE:
            sage: from sage.plot.plot3d.shapes import Box
            sage: B = Box(.5,.4,.3, color='black')
            sage: S = B.stickers(['red','yellow','blue'], 0.1, 0.05)
            sage: S.show()
            sage: (S+B).show()
        """
        all = []
        n = self.fcount; ct = len(colors)
        for k in range(len(colors)):
            if colors[k]:
                all.append(self.sticker(range(k,n,ct), width, hover, texture=colors[k]))
        return Graphics3dGroup(all)

    def sticker(self, face_list, width, hover, **kwds):
        if not isinstance(face_list, (list, tuple)):
            face_list = (face_list,)
        faces = self.face_list()
        all = []
        for k in face_list:
            all.append(sticker(faces[k], width, hover))
        return IndexFaceSet(all, **kwds)


cdef class FaceIter:
    def __init__(self, face_set):
        self.set = face_set
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        cdef point_c P
        if self.i >= self.set.fcount:
            raise StopIteration
        else:
            face = []
            for j from 0 <= j < self.set._faces[self.i].n:
                P = self.set.vs[self.set._faces[self.i].vertices[j]]
                PyList_Append(face, (P.x, P.y, P.z))
            self.i += 1
            return face

cdef class EdgeIter:
    def __init__(self, face_set):
        self.set = face_set
        if not self.set.enclosed:
            raise TypeError, "Must be closed to use the simple iterator."
        self.i = 0
        self.j = 0
        self.seen = {}
    def __iter__(self):
        return self
    def __next__(self):
        cdef point_c P, Q
        cdef face_c face = self.set._faces[self.i]
        while self.i < self.set.fcount:
            if self.j == face.n:
                self.i += 1
                self.j = 0
                if self.i < self.set.fcount:
                    face = self.set._faces[self.i]
            else:
                if self.j == 0:
                    P = self.set.vs[face.vertices[face.n-1]]
                else:
                    P = self.set.vs[face.vertices[self.j-1]]
                Q = self.set.vs[face.vertices[self.j]]
                self.j += 1
                if self.set.enclosed: # Every edge appears exactly twice, once in each orientation.
                    if point_c_cmp(P, Q) < 0:
                        return ((P.x, P.y, P.z), (Q.x, Q.y, Q.z))
                else:
                    if point_c_cmp(P, Q) > 0:
                        P,Q = Q,P
                    edge = ((P.x, P.y, P.z), (Q.x, Q.y, Q.z))
                    if not edge in self.seen:
                        self.seen[edge] = edge
                        return edge
        raise StopIteration


cdef class VertexIter:
    def __init__(self, face_set):
        self.set = face_set
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= self.set.vcount:
            raise StopIteration
        else:
            self.i += 1
            return (self.set.vs[self.i-1].x, self.set.vs[self.i-1].y, self.set.vs[self.i-1].z)

def len3d(v):
    return sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def sticker(face, width, hover):
    n = len(face)
    edges = []
    for i from 0 <= i < n:
        edges.append(vector(RDF, [face[i-1][0] - face[i][0],
                                  face[i-1][1] - face[i][1],
                                  face[i-1][2] - face[i][2]]))
    sticker = []
    for i in range(n):
        v = -edges[i]
        w = edges[i-1]
        N = v.cross_product(w)
        lenN = len3d(N)
        dv = v*(width*len3d(w)/lenN)
        dw = w*(width*len3d(v)/lenN)
        sticker.append(tuple(vector(RDF, face[i-1]) + dv + dw + N*(hover/lenN)))
    return sticker
