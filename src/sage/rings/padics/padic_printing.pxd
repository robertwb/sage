include "../../ext/cdefs.pxi"

from sage.structure.sage_object cimport SageObject
from sage.rings.padics.pow_computer cimport PowComputer_class
from sage.rings.padics.padic_generic_element cimport pAdicGenericElement

cdef class pAdicPrinter_class(SageObject):
    cdef object ring
    cdef int mode
    cdef int terse
    cdef int series
    cdef int val_unit
    cdef int digits
    cdef int bars
    cdef bint pos
    cdef object pname
    cdef object unram_name
    cdef object var_name
    cdef object sep
    cdef object alphabet
    cdef PowComputer_class prime_pow
    cdef bint base
    cdef pAdicPrinter_class old
    cdef long max_ram_terms
    cdef long max_unram_terms
    cdef long max_terse_terms

    cdef base_p_list(self, mpz_t value, bint pos)
    cdef _repr_gen(self, pAdicGenericElement elt, bint do_latex, bint pos, int mode, pname)
    cdef _repr_spec(self, pAdicGenericElement elt, bint do_latex, bint pos, int _mode, bint paren, pname)
    cdef _print_list_as_poly(self, L, bint do_latex, polyname, long expshift, bint increasing)
    cdef _truncate_list(self, L, max_terms, zero)
    cdef _var(self, x, exp, do_latex)
    cdef _dot_var(self, x, exp, do_latex)
    cdef _co_dot_var(self, co, x, exp, do_latex)
    cdef _plus_ellipsis(self, do_latex)
    cdef _print_term_of_poly(self, s, coeff, bint do_latex, polyname, long exp)
