#ifdef __cplusplus
#include <NTL/ZZ.h>
#include <NTL/ZZX.h>
#include <NTL/ZZ_pXFactoring.h>
#include <NTL/ZZXFactoring.h>
#include <NTL/mat_ZZ.h>
#include <NTL/mat_poly_ZZ.h>
#include <NTL/GF2E.h>
#include <NTL/GF2X.h>
#include <NTL/GF2EX.h>
#include <NTL/mat_GF2E.h>
#include <NTL/HNF.h>
#include <gmp.h>
using namespace NTL;
#endif

#ifdef __cplusplus
#define EXTERN extern "C"
#else
#define EXTERN
#endif

#include "ccobject.h"

EXTERN void del_charstar(char*);


////////  ZZ //////////

#ifndef __cplusplus
struct ZZ;
#endif

EXTERN struct ZZ* new_ZZ(void);
EXTERN void del_ZZ(struct ZZ* x);
EXTERN struct ZZ* str_to_ZZ(const char* s);
EXTERN char* ZZ_to_str(const struct ZZ* x);
EXTERN int ZZ_to_int(const struct ZZ* x);
EXTERN struct ZZ* int_to_ZZ(int value);
EXTERN void ZZ_to_mpz(mpz_t* output, const struct ZZ* x);
EXTERN void mpz_to_ZZ(struct ZZ *output, const mpz_t* x);
EXTERN void ZZ_set_from_int(struct ZZ* x, int value);
EXTERN struct ZZ* ZZ_add(const struct ZZ* x, const struct ZZ* y);
EXTERN struct ZZ* ZZ_sub(const struct ZZ* x, const struct ZZ* y);
EXTERN struct ZZ* ZZ_mul(const struct ZZ* x, const struct ZZ* y);
EXTERN struct ZZ* ZZ_pow(const struct ZZ* x, long e);
EXTERN int ZZ_equal(struct ZZ* x, struct ZZ* y);
EXTERN int ZZ_is_zero(struct ZZ*x );
EXTERN int ZZ_is_one(struct ZZ*x );
EXTERN struct ZZ* ZZ_neg(struct ZZ* x);
EXTERN struct ZZ* ZZ_copy(struct ZZ* x);
/*Random-number generation */
EXTERN void setSeed(const struct ZZ* n);
EXTERN struct ZZ* ZZ_randomBnd(const struct ZZ* x);
EXTERN struct ZZ* ZZ_randomBits(long n);


////////  ZZ_p //////////

#ifndef __cplusplus
struct ZZ_p;
#endif

EXTERN struct ZZ_p* new_ZZ_p(void);
EXTERN void del_ZZ_p(struct ZZ_p* x);
EXTERN struct ZZ_p* str_to_ZZ_p(const char* s);
EXTERN char* ZZ_p_to_str(const struct ZZ_p* x);
EXTERN int ZZ_p_to_int(const struct ZZ_p* x);
EXTERN struct ZZ_p* int_to_ZZ_p(int value);
EXTERN void ZZ_p_set_from_int(struct ZZ_p* x, int value);
EXTERN struct ZZ_p* ZZ_p_add(const struct ZZ_p* x, const struct ZZ_p* y);
EXTERN struct ZZ_p* ZZ_p_sub(const struct ZZ_p* x, const struct ZZ_p* y);
EXTERN struct ZZ_p* ZZ_p_mul(const struct ZZ_p* x, const struct ZZ_p* y);
EXTERN struct ZZ_p* ZZ_p_pow(const struct ZZ_p* x, long e);
EXTERN int ZZ_p_is_zero(struct ZZ_p*x );
EXTERN int ZZ_p_is_one(struct ZZ_p*x );
EXTERN void ntl_ZZ_set_modulus(struct ZZ* x);
EXTERN int ZZ_p_eq(struct ZZ_p* x, struct ZZ_p* y);
EXTERN struct ZZ_p* ZZ_p_inv(struct ZZ_p* x);
EXTERN struct ZZ_p* ZZ_p_neg(struct ZZ_p* x);
EXTERN struct ZZ_p* ZZ_p_random(void);
EXTERN void ZZ_p_modulus(struct ZZ* mod, const struct ZZ_p* x);


EXTERN struct ZZ_pContext* ZZ_pContext_new(struct ZZ* p);
EXTERN struct ZZ_pContext* ZZ_pContext_construct(void* mem, struct ZZ* p);
EXTERN void ZZ_pContext_restore(struct ZZ_pContext* ctx);

//////// ZZX //////////
#ifndef __cplusplus
struct ZZX;
#endif

EXTERN struct ZZX* ZZX_init();
EXTERN struct ZZX* str_to_ZZX(const char* s);
EXTERN char* ZZX_repr(struct ZZX* x);
EXTERN void ZZX_dealloc(struct ZZX* x);
EXTERN struct ZZX* ZZX_copy(struct ZZX* x);
EXTERN void ZZX_setitem(struct ZZX* x, long i, const char* a);
EXTERN void ZZX_setitem_from_int(struct ZZX* x, long i, int value);
EXTERN char* ZZX_getitem(struct ZZX* x, long i);
EXTERN int ZZX_getitem_as_int(struct ZZX* x, long i);
EXTERN void ZZX_getitem_as_mpz(mpz_t* output, struct ZZX* x, long i);
EXTERN struct ZZX* ZZX_add(struct ZZX* x, struct ZZX* y);
EXTERN struct ZZX* ZZX_sub(struct ZZX* x, struct ZZX* y);
EXTERN struct ZZX* ZZX_mul(struct ZZX* x, struct ZZX* y);
EXTERN struct ZZX* ZZX_div(struct ZZX* x, struct ZZX* y, int* divisible);
EXTERN struct ZZX* ZZX_mod(struct ZZX* x, struct ZZX* y);
EXTERN void ZZX_quo_rem(struct ZZX* x, struct ZZX* other, struct ZZX** r, struct ZZX** q);
EXTERN struct ZZX* ZZX_square(struct ZZX* x);
EXTERN int ZZX_equal(struct ZZX* x, struct ZZX* y);
EXTERN int ZZX_is_zero(struct ZZX* x);
EXTERN int ZZX_is_one(struct ZZX* x);
EXTERN int ZZX_is_monic(struct ZZX* x);
EXTERN struct ZZX* ZZX_neg(struct ZZX* x);
EXTERN struct ZZX* ZZX_left_shift(struct ZZX* x, long n);
EXTERN struct ZZX* ZZX_right_shift(struct ZZX* x, long n);
EXTERN char* ZZX_content(struct ZZX* x);
EXTERN struct ZZX* ZZX_primitive_part(struct ZZX* x);
EXTERN void ZZX_pseudo_quo_rem(struct ZZX* x, struct ZZX* y, struct ZZX** r, struct ZZX** q);
EXTERN struct ZZX* ZZX_gcd(struct ZZX* x, struct ZZX* y);
EXTERN void ZZX_xgcd(struct ZZX* x, struct ZZX* y, struct ZZ** r, struct ZZX** s, struct ZZX** t, int proof);
EXTERN long ZZX_degree(struct ZZX* x);
EXTERN struct ZZ* ZZX_leading_coefficient(struct ZZX* x);
EXTERN char* ZZX_constant_term(struct ZZX* x);
EXTERN void ZZX_set_x(struct ZZX* x);
EXTERN int ZZX_is_x(struct ZZX* x);
EXTERN struct ZZX* ZZX_derivative(struct ZZX* x);
EXTERN struct ZZX* ZZX_reverse(struct ZZX* x);
EXTERN struct ZZX* ZZX_reverse_hi(struct ZZX* x, int hi);
EXTERN struct ZZX* ZZX_truncate(struct ZZX* x, long m);
EXTERN struct ZZX* ZZX_multiply_and_truncate(struct ZZX* x, struct ZZX* y, long m);
EXTERN struct ZZX* ZZX_square_and_truncate(struct ZZX* x, long m);
EXTERN struct ZZX* ZZX_invert_and_truncate(struct ZZX* x, long m);
EXTERN struct ZZX* ZZX_multiply_mod(struct ZZX* x, struct ZZX* y,  struct ZZX* modulus);
EXTERN struct ZZ* ZZX_trace_mod(struct ZZX* x, struct ZZX* y);
/* EXTERN struct ZZ* ZZX_polyeval(struct ZZX* f, struct ZZ* a); */
EXTERN char* ZZX_trace_list(struct ZZX* x);
EXTERN struct ZZ* ZZX_resultant(struct ZZX* x, struct ZZX* y, int proof);
EXTERN struct ZZ* ZZX_norm_mod(struct ZZX* x, struct ZZX* y, int proof);
EXTERN struct ZZ* ZZX_discriminant(struct ZZX* x, int proof);
EXTERN struct ZZX* ZZX_charpoly_mod(struct ZZX* x, struct ZZX* y, int proof);
EXTERN struct ZZX* ZZX_minpoly_mod(struct ZZX* x, struct ZZX* y);
EXTERN void ZZX_clear(struct ZZX* x);
EXTERN void ZZX_preallocate_space(struct ZZX* x, long n);

//////// ZZXFactoring //////////

// OUTPUT: v -- pointer to list of n ZZX elements (the squarefree factors)
//         e -- point to list of e longs (the exponents)
//         n -- length of above two lists
//  The lists v and e are mallocd, and must be freed by the calling code.
EXTERN void ZZX_square_free_decomposition(struct ZZX*** v, long** e, long* n, struct ZZX* x);


//////// ZZ_pX //////////
#ifndef __cplusplus
struct ZZ_pX;
#endif

EXTERN struct ZZ_pX* ZZ_pX_init();
EXTERN struct ZZ_pX* str_to_ZZ_pX(const char* s);
EXTERN char* ZZ_pX_repr(struct ZZ_pX* x);
EXTERN void ZZ_pX_dealloc(struct ZZ_pX* x);
EXTERN struct ZZ_pX* ZZ_pX_copy(struct ZZ_pX* x);
EXTERN void ZZ_pX_setitem(struct ZZ_pX* x, long i, const char* a);
EXTERN void ZZ_pX_setitem_from_int(struct ZZ_pX* x, long i, int value);
EXTERN char* ZZ_pX_getitem(struct ZZ_pX* x, long i);
EXTERN int ZZ_pX_getitem_as_int(struct ZZ_pX* x, long i);
EXTERN struct ZZ_pX* ZZ_pX_add(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN struct ZZ_pX* ZZ_pX_sub(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN struct ZZ_pX* ZZ_pX_mul(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN struct ZZ_pX* ZZ_pX_div(struct ZZ_pX* x, struct ZZ_pX* y, int* divisible);
EXTERN struct ZZ_pX* ZZ_pX_mod(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN void ZZ_pX_quo_rem(struct ZZ_pX* x, struct ZZ_pX* other, struct ZZ_pX** r, struct ZZ_pX** q);
EXTERN struct ZZ_pX* ZZ_pX_square(struct ZZ_pX* x);
EXTERN int ZZ_pX_equal(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN int ZZ_pX_is_zero(struct ZZ_pX* x);
EXTERN int ZZ_pX_is_one(struct ZZ_pX* x);
EXTERN int ZZ_pX_is_monic(struct ZZ_pX* x);
EXTERN struct ZZ_pX* ZZ_pX_neg(struct ZZ_pX* x);
EXTERN struct ZZ_pX* ZZ_pX_left_shift(struct ZZ_pX* x, long n);
EXTERN struct ZZ_pX* ZZ_pX_right_shift(struct ZZ_pX* x, long n);
EXTERN void ZZ_pX_quo_rem(struct ZZ_pX* x, struct ZZ_pX* y, struct ZZ_pX** r, struct ZZ_pX** q);
EXTERN struct ZZ_pX* ZZ_pX_gcd(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN void ZZ_pX_xgcd(struct ZZ_pX** d, struct ZZ_pX** s, struct ZZ_pX** t, struct ZZ_pX* a, struct ZZ_pX* b);
EXTERN void ZZ_pX_plain_xgcd(struct ZZ_pX** d, struct ZZ_pX** s, struct ZZ_pX** t, struct ZZ_pX* a, struct ZZ_pX* b);
EXTERN long ZZ_pX_degree(struct ZZ_pX* x);
EXTERN struct ZZ_p* ZZ_pX_leading_coefficient(struct ZZ_pX* x);
EXTERN char* ZZ_pX_constant_term(struct ZZ_pX* x);
EXTERN void ZZ_pX_set_x(struct ZZ_pX* x);
EXTERN int ZZ_pX_is_x(struct ZZ_pX* x);
EXTERN struct ZZ_pX* ZZ_pX_derivative(struct ZZ_pX* x);
EXTERN struct ZZ_pX* ZZ_pX_reverse(struct ZZ_pX* x);
EXTERN struct ZZ_pX* ZZ_pX_reverse_hi(struct ZZ_pX* x, int hi);
EXTERN struct ZZ_pX* ZZ_pX_truncate(struct ZZ_pX* x, long m);
EXTERN struct ZZ_pX* ZZ_pX_multiply_and_truncate(struct ZZ_pX* x, struct ZZ_pX* y, long m);
EXTERN struct ZZ_pX* ZZ_pX_square_and_truncate(struct ZZ_pX* x, long m);
EXTERN struct ZZ_pX* ZZ_pX_invert_and_truncate(struct ZZ_pX* x, long m);
EXTERN struct ZZ_pX* ZZ_pX_multiply_mod(struct ZZ_pX* x, struct ZZ_pX* y,  struct ZZ_pX* modulus);
EXTERN struct ZZ_p* ZZ_pX_trace_mod(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN char* ZZ_pX_trace_list(struct ZZ_pX* x);
EXTERN struct ZZ_p* ZZ_pX_resultant(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN struct ZZ_p* ZZ_pX_norm_mod(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN struct ZZ_pX* ZZ_pX_charpoly_mod(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN struct ZZ_pX* ZZ_pX_minpoly_mod(struct ZZ_pX* x, struct ZZ_pX* y);
EXTERN void ZZ_pX_clear(struct ZZ_pX* x);
EXTERN void ZZ_pX_preallocate_space(struct ZZ_pX* x, long n);

// Factoring elements of ZZ_pX:
// OUTPUT: v -- pointer to list of n ZZ_pX elements (the irred factors)
//         e -- point to list of e longs (the exponents)
//         n -- length of above two lists
//  The lists v and e are mallocd, and must be freed by the calling code.
EXTERN void ZZ_pX_factor(struct ZZ_pX*** v, long** e, long* n, struct ZZ_pX* x, long verbose);
EXTERN void ZZ_pX_linear_roots(struct ZZ_p*** v, long* n, struct ZZ_pX* f);



//////// mat_ZZ //////////

#ifndef __cplusplus
struct mat_ZZ;
#endif

EXTERN void mat_ZZ_SetDims(struct mat_ZZ* mZZ, long nrows, long ncols);
EXTERN struct mat_ZZ* new_mat_ZZ(long nrows, long ncols);
EXTERN void del_mat_ZZ(struct mat_ZZ* x);
EXTERN char* mat_ZZ_to_str(struct mat_ZZ* x);
EXTERN struct mat_ZZ* mat_ZZ_add(const struct mat_ZZ* x, const struct mat_ZZ* y);
EXTERN struct mat_ZZ* mat_ZZ_sub(const struct mat_ZZ* x, const struct mat_ZZ* y);
EXTERN struct mat_ZZ* mat_ZZ_mul(const struct mat_ZZ* x, const struct mat_ZZ* y);
EXTERN struct mat_ZZ* mat_ZZ_pow(const struct mat_ZZ* x, long e);
EXTERN long mat_ZZ_nrows(const struct mat_ZZ* x);
EXTERN long mat_ZZ_ncols(const struct mat_ZZ* x);
EXTERN void mat_ZZ_setitem(struct mat_ZZ* x, int i, int j, const struct ZZ* z);
EXTERN struct ZZ* mat_ZZ_getitem(const struct mat_ZZ* x, int i, int j);
EXTERN struct ZZ* mat_ZZ_determinant(const struct mat_ZZ* x, long deterministic);
EXTERN struct mat_ZZ* mat_ZZ_HNF(const struct mat_ZZ* A, const struct ZZ* D);
EXTERN struct ZZX* mat_ZZ_charpoly(const struct mat_ZZ* A);
EXTERN long mat_ZZ_LLL(struct ZZ **det, struct mat_ZZ *x, long a, long b, long verbose);
EXTERN long mat_ZZ_LLL_U(struct ZZ **det, struct mat_ZZ *x, struct mat_ZZ *U, long a, long b, long verbose);

/* //////// ZZ_p ////////// */
/* #ifndef __cplusplus */
/* struct ZZ_p; */
/* #endif */

/* EXTERN void ZZ_p_set_modulus(const struct ZZ* p); */
/* EXTERN struct ZZ_p* new_ZZ_p(void); */
/* EXTERN struct ZZ_p* str_to_ZZ_p(const char* s); */
/* EXTERN void del_ZZ_p(struct ZZ_p* x); */
/* EXTERN char* ZZ_p_to_str(const struct ZZ_p* x); */
/* EXTERN struct ZZ_p* ZZ_p_add(const struct ZZ_p* x, const struct ZZ_p* y); */
/* EXTERN struct ZZ_p* ZZ_p_sub(const struct ZZ_p* x, const struct ZZ_p* y); */
/* EXTERN struct ZZ_p* ZZ_p_mul(const struct ZZ_p* x, const struct ZZ_p* y); */
/* EXTERN struct ZZ_p* ZZ_p_pow(const struct ZZ_p* x, long e); */
/* EXTERN int ZZ_p_is_zero(struct ZZ_p*x ); */
/* EXTERN int ZZ_p_is_one(struct ZZ_p*x ); */


//////// ZZ_pE //////////
#ifndef __cplusplus
struct ZZ_pE;
#endif

// EXTERN struct ZZ_pE* new_ZZ_pE



//////// ZZ_pEX //////////

//#ifndef __cplusplus
//struct ZZ_pEX;
//#endif

//EXTERN struct ZZ_pEX* new_ZZ_pEX

/////// GF2X ////////////////
#ifndef __cplusplus
struct GF2X;
#endif

EXTERN struct GF2X* new_GF2X(void);
EXTERN void del_GF2X(struct GF2X* x);
EXTERN struct GF2X* str_to_GF2X(const char* s);
EXTERN char* GF2X_to_str(const struct GF2X* x);
EXTERN struct GF2X* GF2X_add(const struct GF2X* x, const struct GF2X* y);
EXTERN struct GF2X* GF2X_sub(const struct GF2X* x, const struct GF2X* y);
EXTERN struct GF2X* GF2X_mul(const struct GF2X* x, const struct GF2X* y);
EXTERN struct GF2X* GF2X_pow(const struct GF2X* x, long e);
EXTERN int GF2X_eq(const struct GF2X* x, const struct GF2X* y);
EXTERN int GF2X_is_zero(struct GF2X*x );
EXTERN int GF2X_is_one(struct GF2X*x );
EXTERN struct GF2X* GF2X_neg(struct GF2X* x);
EXTERN struct GF2X* GF2X_copy(struct GF2X* x);
EXTERN long GF2X_deg(struct GF2X* x);
EXTERN void GF2X_hex(long h);
EXTERN char *GF2X_to_bin(const struct GF2X* x);
EXTERN char *GF2X_to_hex(const struct GF2X* x);


/////// GF2E ////////////////

#ifndef __cplusplus
struct GF2E;
#endif

EXTERN struct GF2E* new_GF2E(void);
EXTERN void del_GF2E(struct GF2E* x);
EXTERN struct GF2E* str_to_GF2E(const char* s);
EXTERN char *GF2E_to_str(const struct GF2E* x);
EXTERN struct GF2E* GF2E_add(const struct GF2E* x, const struct GF2E* y);
EXTERN struct GF2E* GF2E_sub(const struct GF2E* x, const struct GF2E* y);
EXTERN struct GF2E* GF2E_mul(const struct GF2E* x, const struct GF2E* y);
EXTERN struct GF2E* GF2E_pow(const struct GF2E* x, long e);
EXTERN int GF2E_eq(const struct GF2E* x, const struct GF2E* y);
EXTERN int GF2E_is_zero(struct GF2E*x );
EXTERN int GF2E_is_one(struct GF2E*x );
EXTERN struct GF2E* GF2E_neg(struct GF2E* x);
EXTERN struct GF2E* GF2E_copy(struct GF2E* x);
EXTERN void ntl_GF2E_set_modulus(struct GF2X* x);
EXTERN long GF2E_degree();
EXTERN const struct GF2X *GF2E_modulus();
EXTERN struct GF2E *GF2E_random(void);
EXTERN long GF2E_trace(struct GF2E *x);
EXTERN const struct GF2X *GF2E_ntl_GF2X(struct GF2E *x);

#ifndef __cplusplus
struct GF2EX;
#endif

EXTERN struct GF2EX* new_GF2EX(void);
EXTERN void del_GF2EX(struct GF2EX* x);
EXTERN struct GF2EX* str_to_GF2EX(const char* s);
EXTERN char* GF2EX_to_str(const struct GF2EX* x);
EXTERN struct GF2EX* GF2EX_add(const struct GF2EX* x, const struct GF2EX* y);
EXTERN struct GF2EX* GF2EX_sub(const struct GF2EX* x, const struct GF2EX* y);
EXTERN struct GF2EX* GF2EX_mul(const struct GF2EX* x, const struct GF2EX* y);
EXTERN struct GF2EX* GF2EX_pow(const struct GF2EX* x, long e);
EXTERN int GF2EX_is_zero(struct GF2EX*x );
EXTERN int GF2EX_is_one(struct GF2EX*x );
EXTERN struct GF2EX* GF2EX_neg(struct GF2EX* x);
EXTERN struct GF2EX* GF2EX_copy(struct GF2EX* x);


//////// mat_GF2E //////////

#ifndef __cplusplus
struct mat_GF2E;
#endif

void mat_GF2E_SetDims(struct mat_GF2E* mGF2E, long nrows, long ncols);
EXTERN struct mat_GF2E* new_mat_GF2E(long nrows, long ncols);
EXTERN void del_mat_GF2E(struct mat_GF2E* x);
EXTERN char* mat_GF2E_to_str(struct mat_GF2E* x);
EXTERN struct mat_GF2E* mat_GF2E_add(const struct mat_GF2E* x, const struct mat_GF2E* y);
EXTERN struct mat_GF2E* mat_GF2E_sub(const struct mat_GF2E* x, const struct mat_GF2E* y);
EXTERN struct mat_GF2E* mat_GF2E_mul(const struct mat_GF2E* x, const struct mat_GF2E* y);
EXTERN struct mat_GF2E* mat_GF2E_pow(const struct mat_GF2E* x, long e);
EXTERN long mat_GF2E_nrows(const struct mat_GF2E* x);
EXTERN long mat_GF2E_ncols(const struct mat_GF2E* x);
EXTERN void mat_GF2E_setitem(struct mat_GF2E* x, int i, int j, const struct GF2E* z);
EXTERN struct GF2E* mat_GF2E_getitem(const struct mat_GF2E* x, int i, int j);
EXTERN struct GF2E* mat_GF2E_determinant(const struct mat_GF2E* x);
EXTERN long mat_GF2E_gauss(struct mat_GF2E *x, long w);
EXTERN long mat_GF2E_is_zero(struct mat_GF2E *x);
EXTERN struct mat_GF2E* mat_GF2E_transpose(const struct mat_GF2E* x);



//EXTERN struct mat_GF2E* mat_GF2E_HNF(const struct mat_GF2E* A, const struct GF2E* D);
//EXTERN struct GF2EX* mat_GF2E_charpoly(const struct mat_GF2E* A);
