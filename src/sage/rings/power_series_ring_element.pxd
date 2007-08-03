from sage.structure.element cimport AlgebraElement, RingElement

cdef class PowerSeries(AlgebraElement):
    cdef char __is_gen
    cdef _prec
    cdef common_prec_c(self, PowerSeries other)
    #_prec(self, RingElement right_r)
