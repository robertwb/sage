include "../ext/cdefs.pxi"

cdef extern from "stdint.h":
    ctypedef int int_fast32_t
    ctypedef int int_fast64_t
    int_fast32_t INTEGER_MOD_INT32_LIMIT
    int_fast64_t INTEGER_MOD_INT64_LIMIT

import sage.ext.element
cimport sage.ext.element

import sage.ext.integer
cimport sage.ext.integer


cdef class NativeIntStruct:
    cdef sage.ext.integer.Integer sageInteger
    cdef int_fast32_t int32
    cdef int_fast64_t int64


cdef class IntegerMod_abstract(sage.ext.element.CommutativeRingElement):
    cdef public object _parent
    cdef NativeIntStruct __modulus

cdef class IntegerMod_gmp(IntegerMod_abstract):
    cdef mpz_t value
    cdef void set_from_mpz(IntegerMod_gmp self, mpz_t value)
    cdef mpz_t* get_value(IntegerMod_gmp self)

cdef class IntegerMod_int(IntegerMod_abstract):
    cdef int_fast32_t ivalue
    cdef void set_from_mpz(IntegerMod_int self, mpz_t value)
    cdef void set_from_int(IntegerMod_int self, int_fast32_t value)
    cdef int_fast32_t get_int_value(IntegerMod_int self)
