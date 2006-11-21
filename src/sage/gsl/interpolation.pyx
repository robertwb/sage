"""
Interpolation
"""

include '../ext/stdsage.pxi'

cdef class Spline:
    """
    Create a spline interpolation object.

    Given a list v of pairs, s = spline(v) is an object s such that
    s(x) is the value of the spline interpolation through the points
    in v at the point x.

    The values in v do not have to be sorted.  Moreover, one can append
    values to v, delete values from v, or change values in v, and the
    spline is recomputed.

    EXAMPLES:
    This is the example in the GSL documentation.
        sage: v = [(i + sin(i)/2, i+cos(i^2)) for i in range(10)]
        sage: s = spline(v)
        sage.: show(point(v) + plot(s,0,11, hue=.8))
    """
    def __init__(self, v=[]):
        self.v = list(v)
        self.started = 0

    def __dealloc__(self):
        self.stop_interp()

    def __setitem__(self, int i, xy):
        cdef int j
        if i < len(self.v):
            self.v[i] = xy
        else:
            for j from len(self.v) <= j <= i:
                self.v.append((0,0))
            self.v[i] = xy
        self.stop_interp()

    def __getitem__(self, int i):
        return self.v[i]

    def __delitem__(self, int i):
        del self.v[i]

    def append(self, xy):
        self.v.append(xy)

    def list(self):
        return self.v

    def __len__(self):
        return len(self.v)

    def __repr__(self):
        return str(self.v)

    cdef start_interp(self):
        if self.started:
            sage_free(self.x)
            sage_free(self.y)
            return
        v = list(self.v)
        v.sort()
        n = len(v)
        if n < 3:
            raise RuntimeError, "must have at least 3 points in order to interpolate."
        self.x = <double*> sage_malloc(n*sizeof(double))
        if self.x == <double*>0:
            raise MemoryError
        self.y = <double*> sage_malloc(n*sizeof(double))
        if self.y == <double*>0:
            sage_free(self.x)
            raise MemoryError

        cdef int i
        for i from 0 <= i < n:
            self.x[i] = v[i][0]
            self.y[i] = v[i][1]

        self.acc = gsl_interp_accel_alloc ()
        self.spline = gsl_spline_alloc (gsl_interp_cspline, n)
        gsl_spline_init (self.spline, self.x, self.y, n)
        self.started = 1

    cdef stop_interp(self):
        if not self.started:
            return
        sage_free(self.x)
        sage_free(self.y)
        gsl_spline_free (self.spline)
        gsl_interp_accel_free (self.acc)
        self.started = 0

    def __call__(self, double x):
        if not self.started:
            self.start_interp()
        _sig_on
        y = gsl_spline_eval(self.spline, x, self.acc)
        _sig_off
        return y

spline = Spline
