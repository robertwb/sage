include '../ext/cdefs.pxi'
include '../ext/interrupt.pxi'
include 'gsl.pxi'

cdef class Spline:
    cdef double *x, *y
    cdef gsl_interp_accel *acc
    cdef gsl_spline *spline
    cdef int started
    cdef object v

    cdef start_interp(self)
    cdef stop_interp(self)
