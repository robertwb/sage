##########################################################
# Setup the c-library and GMP random number generators.
# seed it when module is loaded.
from random import randrange
cdef extern from "stdlib.h":
    long RAND_MAX
    long random()
    void srandom(unsigned int seed)
k = randrange(0, int(2)**32)
srandom(k)

cdef gmp_randstate_t state
gmp_randinit_mt(state)
gmp_randseed_ui(state,k)


###########################

cdef void mpq_randomize_entry(mpq_t x, mpz_t num_bound, mpz_t den_bound):
    mpz_urandomm(mpq_numref(x), state, num_bound)
    mpz_urandomm(mpq_denref(x), state, den_bound)
    if mpz_sgn(mpq_denref(x)) == 0:
        mpz_set_si(mpq_denref(x),1)
    if random() % 2:
        mpz_mul_si(mpq_numref(x), mpq_numref(x), -1)
    mpq_canonicalize(x)

cdef void mpq_randomize_entry_as_int(mpq_t x, mpz_t bound):
    mpz_urandomm(mpq_numref(x), state, bound)
    mpz_set_si(mpq_denref(x), 1)
    if random() % 2:
        mpz_mul_si(mpq_numref(x), mpq_numref(x), -1)

cdef inline void mpq_randomize_entry_recip_uniform(mpq_t x):
    # Distributes top and bottom according to mpz_randomize_entry_recip_uniform.
    cdef int den = random() - RAND_MAX/2
    if den == 0: den = 1
    mpz_set_si(mpq_numref(x), (RAND_MAX/2) / den)
    den = random()
    if den == 0: den = 1
    mpz_set_si(mpq_denref(x), RAND_MAX / den)
    mpq_canonicalize(x)
