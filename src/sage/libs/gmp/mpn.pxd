from types cimport *

cdef extern from "gmp.h":

    ### Low-level Functions ###

    mp_limb_t mpn_add_n (mp_limb_t *rp, mp_limb_t *s1p, mp_limb_t *s2p, mp_size_t n)
    mp_limb_t mpn_add_1 (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t n, mp_limb_t s2limb)
    mp_limb_t mpn_add (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t s1n, mp_limb_t *s2p, mp_size_t s2n)
    mp_limb_t mpn_sub_n (mp_limb_t *rp, mp_limb_t *s1p, mp_limb_t *s2p, mp_size_t n)
    mp_limb_t mpn_sub_1 (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t n, mp_limb_t s2limb)
    mp_limb_t mpn_sub (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t s1n, mp_limb_t *s2p, mp_size_t s2n)
    void mpn_mul_n (mp_limb_t *rp, mp_limb_t *s1p, mp_limb_t *s2p, mp_size_t n)
    mp_limb_t mpn_mul_1 (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t n, mp_limb_t s2limb)
    mp_limb_t mpn_addmul_1 (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t n, mp_limb_t s2limb)
    mp_limb_t mpn_submul_1 (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t n, mp_limb_t s2limb)
    mp_limb_t mpn_mul (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t s1n, mp_limb_t *s2p, mp_size_t s2n)
    void mpn_tdiv_qr (mp_limb_t *qp, mp_limb_t *rp, mp_size_t qxn, mp_limb_t *np, mp_size_t nn, mp_limb_t *dp, mp_size_t dn)
    mp_limb_t mpn_divrem (mp_limb_t *r1p, mp_size_t qxn, mp_limb_t *rs2p, mp_size_t rs2n, mp_limb_t *s3p, mp_size_t s3n)
    mp_limb_t mpn_divrem_1 (mp_limb_t *r1p, mp_size_t qxn, mp_limb_t *s2p, mp_size_t s2n, mp_limb_t s3limb)
    mp_limb_t mpn_divmod_1 (mp_limb_t *r1p, mp_limb_t *s2p, mp_size_t s2n, mp_limb_t s3limb)
    mp_limb_t mpn_divmod (mp_limb_t *r1p, mp_limb_t *rs2p, mp_size_t rs2n, mp_limb_t *s3p, mp_size_t s3n)
    mp_limb_t mpn_divexact_by3 (mp_limb_t *rp, mp_limb_t *sp, mp_size_t n)
    mp_limb_t mpn_divexact_by3c (mp_limb_t *rp, mp_limb_t *sp, mp_size_t n, mp_limb_t carry)
    mp_limb_t mpn_mod_1 (mp_limb_t *s1p, mp_size_t s1n, mp_limb_t s2limb)
    mp_limb_t mpn_bdivmod (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t s1n, mp_limb_t *s2p, mp_size_t s2n, unsigned long int d)
    mp_limb_t mpn_lshift (mp_limb_t *rp, mp_limb_t *sp, mp_size_t n, unsigned int count)
    mp_limb_t mpn_rshift (mp_limb_t *rp, mp_limb_t *sp, mp_size_t n, unsigned int count)
    int mpn_cmp (mp_limb_t *s1p, mp_limb_t *s2p, mp_size_t n)
    mp_size_t mpn_gcd (mp_limb_t *rp, mp_limb_t *s1p, mp_size_t s1n, mp_limb_t *s2p, mp_size_t s2n)
    mp_limb_t mpn_gcd_1 (mp_limb_t *s1p, mp_size_t s1n, mp_limb_t s2limb)
    mp_size_t mpn_gcdext (mp_limb_t *r1p, mp_limb_t *r2p, mp_size_t *r2n, mp_limb_t *s1p, mp_size_t s1n, mp_limb_t *s2p, mp_size_t s2n)
    mp_size_t mpn_sqrtrem (mp_limb_t *r1p, mp_limb_t *r2p, mp_limb_t *sp, mp_size_t n)
    mp_size_t mpn_get_str (unsigned char *str, int base, mp_limb_t *s1p, mp_size_t s1n)
    mp_size_t mpn_set_str (mp_limb_t *rp, unsigned char *str, size_t strsize, int base)
    unsigned long int mpn_scan0 (mp_limb_t *s1p, unsigned long int bit)
    unsigned long int mpn_scan1 (mp_limb_t *s1p, unsigned long int bit)
    void mpn_random (mp_limb_t *r1p, mp_size_t r1n)
    void mpn_random2 (mp_limb_t *r1p, mp_size_t r1n)
    unsigned long int mpn_popcount (mp_limb_t *s1p, mp_size_t n)
    unsigned long int mpn_hamdist (mp_limb_t *s1p, mp_limb_t *s2p, mp_size_t n)
    int mpn_perfect_square_p (mp_limb_t *s1p, mp_size_t n)
