cdef struct point_c:
  double x
  double y
  double z

cdef struct face_c:
  int n
  int* vertices


cdef class Transformation:
    cdef matrix
    cdef double _matrix_data[12]
    cdef object _svd
    cpdef transform_point(self, x)
    cpdef transform_vector(self, x)
    cdef void transform_point_c(self, point_c* res, point_c P)
    cdef void transform_vector_c(self, point_c* res, point_c P)
