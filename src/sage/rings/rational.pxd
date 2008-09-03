include "../ext/cdefs.pxi"
cimport sage.structure.element
import  sage.structure.element

cimport integer

cdef class Rational(sage.structure.element.FieldElement):
    cdef mpq_t value

    cdef void set_from_mpq(Rational self, mpq_t value)
    cdef _lshift(self, long int exp)
    cdef _rshift(self, long int exp)

    cdef _val_unit(self, integer.Integer p)