cdef extern from "stdlib.h":
    ctypedef int size_t
    void free(void *ptr)
    void *malloc(size_t size)
    void *realloc(void *ptr, size_t size)
    size_t strlen(char *s)
    char *strcpy(char *dest, char *src)

cdef extern from "stdio.h":
    ctypedef void* FILE
    int printf(char *format, ...)
    int fprintf(FILE *stream, char *format, ...)
    int sprintf(char *str, char *format, ...)


cdef extern from "math.h":
    double sqrt(double x)
    float roundf(float x)

cdef extern from "Python.h":
    void PyMem_Free(void *p)
    void* PyMem_Realloc(void *p, size_t n)
    void* PyMem_Malloc(size_t)
    object PyString_FromString(char *v)
    char* PyString_AsString(object string)
    object PyString_InternFromString(char *v)
    int PyErr_CheckSignals()

cdef extern from "gmp.h":
    ctypedef void* mpq_t
    ctypedef void* mpz_t
    ctypedef void* mpf_t
    ctypedef void* gmp_randstate_t

    void gmp_randinit_default(gmp_randstate_t state)
    size_t mpz_sizeinbase(mpz_t op, int base)

    # The mpz type
    void mpz_abs (mpz_t rop, mpz_t op)
    void mpz_add (mpz_t rop, mpz_t op1, mpz_t op2)
    void mpz_and (mpz_t rop, mpz_t op1, mpz_t op2)
    void mpz_ior (mpz_t rop, mpz_t op1, mpz_t op2)
    void mpz_clear(mpz_t integer)
    int  mpz_cmp(mpz_t op1, mpz_t op2)
    int  mpz_cmp_si(mpz_t op1, signed long int op2)
    int  mpz_cmp_ui(mpz_t op1, unsigned long int op2)
    void mpz_divexact (mpz_t q, mpz_t n, mpz_t d)
    int mpz_divisible_p (mpz_t n, mpz_t d)
    void mpz_fac_ui (mpz_t rop, unsigned long int op)
    void mpz_fdiv_q(mpz_t q, mpz_t n, mpz_t d)
    void mpz_fdiv_qr (mpz_t q, mpz_t r, mpz_t n, mpz_t d)
    void mpz_cdiv_q(mpz_t q, mpz_t n, mpz_t d)
    void mpz_cdiv_qr (mpz_t q, mpz_t r, mpz_t n, mpz_t d)
    void mpz_tdiv_qr (mpz_t q, mpz_t r, mpz_t n, mpz_t d)
    double mpz_get_d (mpz_t op)
    unsigned long int mpz_fdiv_ui (mpz_t n, unsigned long int d)
    unsigned long int mpz_fdiv_q_ui(mpz_t q, mpz_t n, unsigned long int d)
    void mpz_gcd(mpz_t rop, mpz_t op1, mpz_t op2)
    void mpz_gcdext(mpz_t g, mpz_t s, mpz_t t, mpz_t a, mpz_t b)
    signed long int mpz_get_si(mpz_t op)
    unsigned long int mpz_get_ui (mpz_t op)
    char *mpz_get_str(char *str, int base, mpz_t op)
    void mpz_init(mpz_t integer)
    void mpz_init_set(mpz_t rop, mpz_t op)
    void mpz_init_set_si(mpz_t integer, signed long int n)
    void mpz_init_set_ui(mpz_t integer, unsigned long int n)
    int mpz_invert (mpz_t rop, mpz_t op1, mpz_t op2)
    void mpz_lcm(mpz_t rop, mpz_t op1, mpz_t op2)
    void mpz_mod (mpz_t r, mpz_t n, mpz_t d)
    void mpz_mul (mpz_t rop, mpz_t op1, mpz_t op2)
    void mpz_mul_si (mpz_t rop, mpz_t op1, long int op2)
    void mpz_neg(mpz_t rop, mpz_t op)
    void mpz_nextprime(mpz_t next_prime, mpz_t prime)
    int mpz_probab_prime_p(mpz_t n, int reps)
    void mpz_powm (mpz_t rop, mpz_t base, mpz_t exp, mpz_t mod)
    void mpz_powm_ui (mpz_t rop, mpz_t base, unsigned long int exp, mpz_t mod)
    void mpz_pow_ui (mpz_t rop, mpz_t base, unsigned long int exp)
    void mpz_set (mpz_t rop, mpz_t op)
    void mpz_set_si(mpz_t integer, signed long int n)
    void mpz_set_ui(mpz_t integer, unsigned long int n)
    int  mpz_set_str(mpz_t rop, char *str, int base)
    int  mpz_sgn(mpz_t op)
    void mpz_sqrt (mpz_t rop, mpz_t op)
    void mpz_sub (mpz_t rop, mpz_t op1, mpz_t op2)
    void mpz_sub_ui(mpz_t rop, mpz_t op1, unsigned long int op2)
    unsigned long int mpz_mod_ui(mpz_t r, mpz_t n, unsigned long int d)
    void mpz_urandomm(mpz_t rop, gmp_randstate_t state, mpz_t n)
    int mpz_tstbit(mpz_t rop, unsigned long int bit_index)
    void mpz_mul_2exp (mpz_t rop, mpz_t op1, unsigned long int op2)
    void mpz_fdiv_q_2exp (mpz_t rop, mpz_t op1, unsigned long int op2)


    # The mpq type
    void mpq_abs (mpq_t rop, mpq_t op)
    void mpq_add(mpq_t sum, mpq_t addend1, mpq_t addend2)
    void mpq_canonicalize(mpq_t op)
    void mpq_clear(mpq_t rational_number)
    int mpq_cmp (mpq_t op1, mpq_t op2)
    int mpq_cmp_si (mpq_t op1, long int num2, unsigned long int den2)
    void mpq_div(mpq_t ans, mpq_t op1, mpq_t op2)
    int mpq_equal(mpq_t x, mpq_t y)
    void mpq_get_num(mpz_t numerator, mpq_t rational)
    void mpq_get_den(mpz_t denominator, mpq_t rational)
    void mpq_init(mpq_t rational_number)
    void mpq_inv(mpq_t inverted_number, mpq_t number)
    void mpq_mul(mpq_t product, mpq_t multiplier, mpq_t multiplicand)
    void mpq_neg(mpq_t negated_operand, mpq_t operand)
    mpz_t mpq_numref (mpq_t op)
    mpz_t mpq_denref (mpq_t op)
    double mpq_get_d (mpq_t op)
    char *mpq_get_str(char *str, int base, mpq_t op)
    void mpq_set(mpq_t rop, mpq_t op)
    void mpq_set_num (mpq_t rational, mpz_t numerator)
    void mpq_set_den (mpq_t rational, mpz_t denominator)
    void mpq_set_si(mpq_t rop, signed long int num, unsigned long int denom)
    void mpq_set_ui(mpq_t rop, unsigned long int num, unsigned long int denom)
    int  mpq_set_str(mpq_t rop, char *str, int base)
    void mpq_set_z(mpq_t rop, mpz_t op)
    int  mpq_sgn(mpq_t op)
    void mpq_sub (mpq_t difference, mpq_t minuend, mpq_t subtrahend)
    void mpq_div_2exp(mpq_t rop, mpq_t op1, unsigned long int exp)
    void mpq_mul_2exp(mpq_t rop, mpq_t op1, unsigned long int exp)

    # The mpf type
    void mpf_add (mpf_t rop, mpf_t op1, mpf_t op2)
    void mpf_sub (mpf_t rop, mpf_t op1, mpf_t op2)
    void mpf_mul (mpf_t rop, mpf_t op1, mpf_t op2)
    void mpf_div (mpf_t rop, mpf_t op1, mpf_t op2)
    void mpf_sqrt (mpf_t rop, mpf_t op)
    void mpf_neg (mpf_t rop, mpf_t op)
    void mpf_abs (mpf_t rop, mpf_t op)
