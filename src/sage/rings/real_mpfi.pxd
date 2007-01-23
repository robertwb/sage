cdef extern from "stdlib.h":
    ctypedef int size_t
    void free(void *ptr)

include 'mpfi.pxi'

cimport sage.rings.ring
import  sage.rings.ring

cimport sage.structure.element
from sage.structure.element cimport RingElement

cimport real_mpfr

cdef class RealIntervalFieldElement(sage.structure.element.RingElement)  # forward decl

cdef class RealIntervalField(sage.rings.ring.Field):
    cdef int __prec, sci_not
    # Cache RealField instances for the lower and upper bounds.
    # These have the same precision as the interval field;
    # __lower_field rounds down, __upper_field rounds up.
    # These fields with their roundings are not used for computation
    # in this module, but they do affect the printing and the return
    # values of lower() and upper().  Consider a 3-bit
    # interval containing exactly the floating-point number 1.25.
    # In round-to-nearest or round-down, this prints as 1.2; in round-up,
    # this prints as 1.3.  The straightforward options, then, are to
    # print this interval as [1.2 ... 1.2] (which does not even contain
    # the true value, 1.25), or to print it as [1.2 ... 1.3] (which
    # gives the impression that the upper and lower bounds are not
    # equal, even though they really are).  Neither of these is very
    # satisfying, but I have chosen the latter for now.
    cdef real_mpfr.RealField __lower_field
    cdef real_mpfr.RealField __upper_field
    cdef RealIntervalFieldElement _new(self)


cdef class RealIntervalFieldElement(sage.structure.element.RingElement):
    cdef mpfi_t value
    cdef char init
    cdef RealIntervalFieldElement _new(self)

    cdef RealIntervalFieldElement abs(RealIntervalFieldElement self)
