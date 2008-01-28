include "../../ext/cdefs.pxi"
include "../../libs/pari/decl.pxi"

cimport sage.rings.padics.padic_base_generic_element
from sage.rings.padics.padic_base_generic_element cimport pAdicBaseGenericElement

cimport sage.structure.element
from sage.structure.element cimport CommutativeRingElement, RingElement, ModuleElement, Element

cimport sage.rings.integer
from sage.rings.integer cimport Integer

cimport sage.rings.rational
from sage.rings.rational cimport Rational

cimport sage.rings.padics.pow_computer
from sage.rings.padics.pow_computer cimport PowComputer_class

import sage.libs.pari.gen
cimport sage.libs.pari.gen
from sage.libs.pari.gen cimport gen as pari_gen
from sage.libs.pari.gen cimport PariInstance

cdef class pAdicCappedRelativeElement(pAdicBaseGenericElement):
    cdef mpz_t unit    #An exact zero is indicated by unit < 0
    cdef long ordp
    cdef long relprec
    cdef bint _normalized
    cdef void _set_exact_zero(pAdicCappedRelativeElement self)
    cdef void _set_inexact_zero(pAdicCappedRelativeElement self, long absprec)
    cdef void _set_zero(pAdicCappedRelativeElement self, absprec)
    cdef void _set_prec(pAdicCappedRelativeElement self, long relprec)
    cdef void _set(pAdicCappedRelativeElement self, long ordp, mpz_t unit, long relprec)
    cdef int _set_from_mpz_rel(pAdicCappedRelativeElement self, mpz_t x, unsigned long relprec) except -1
    cdef int _set_from_mpz_both(pAdicCappedRelativeElement self, mpz_t x, long absprec, unsigned long relprec) except -1
    cdef int _set_from_mpq_rel(pAdicCappedRelativeElement self, mpq_t x, unsigned long relprec) except -1
    cdef int _set_from_mpq_both(pAdicCappedRelativeElement self, mpq_t x, long absprec, unsigned long relprec) except -1
    cdef int _set_from_CR(pAdicCappedRelativeElement self, pAdicCappedRelativeElement other) except -1
    cdef pAdicCappedRelativeElement _new_c(pAdicCappedRelativeElement self)
    cdef void _normalize(pAdicCappedRelativeElement self)
    cdef ModuleElement _neg_c_impl(self)
    cdef RingElement _floordiv_c_impl(self, RingElement right)
    cdef pAdicCappedRelativeElement _lshift_c(pAdicCappedRelativeElement self, long shift)
    cdef pAdicCappedRelativeElement _rshift_c(pAdicCappedRelativeElement self, long shift)
    cdef pAdicCappedRelativeElement lift_to_precision_c(pAdicCappedRelativeElement self, long absprec)
    cdef pari_gen _to_gen(pAdicCappedRelativeElement self)
    cdef teichmuller_list(pAdicCappedRelativeElement self)
    cdef val_unit_c(self)
    cdef pAdicCappedRelativeElement unit_part_c(self)
    cdef long valuation_c(self)
    cdef lift_c(self)
