#include <iostream>
#include <sstream>
using namespace std;

#include "ntl_wrap.h"
#include <NTL/mat_poly_ZZ.h>
#include <NTL/LLL.h>

void del_charstar(char* a) {
  delete[] a;
}

//////// ZZ //////////

/* Return value is only valid if the result should fit into an int.
   AUTHOR: David Harvey (2008-06-08) */
int ZZ_to_int(const ZZ* x)
{
  return to_int(*x);
}

/* Returns a *new* ZZ object.
   AUTHOR: David Harvey (2008-06-08) */
struct ZZ* int_to_ZZ(int value)
{
  ZZ* output = new ZZ();
  conv(*output, value);
  return output;
}

/* Copies the ZZ into the mpz_t
   Assumes output has been mpz_init'd.
   AUTHOR: David Harvey
           Joel B. Mohler moved the ZZX_getitem_as_mpz code out to this function (2007-03-13) */
void ZZ_to_mpz(mpz_t* output, const struct ZZ* x)
{
    unsigned char stack_bytes[4096];
    int use_heap;
    unsigned long size = NumBytes(*x);
    use_heap = (size > sizeof(stack_bytes));
    unsigned char* bytes = use_heap ? (unsigned char*) malloc(size) : stack_bytes;
    BytesFromZZ(bytes, *x, size);
    mpz_import(*output, size, -1, 1, 0, 0, bytes);
    if (sign(*x) < 0)
        mpz_neg(*output, *output);
    if (use_heap)
        free(bytes);
}

// Ok, I know that this is obvious
// I just wanted to document the appearance of the magic number 8 in the code below
#define bits_in_byte        8

/* Copies the mpz_t into the ZZ
   AUTHOR: Joel B. Mohler (2007-03-15) */
void mpz_to_ZZ(struct ZZ* output, const mpz_t* x)
{
    unsigned char stack_bytes[4096];
    int use_heap;
    size_t size = (mpz_sizeinbase(*x, 2) + bits_in_byte-1) / bits_in_byte;
    use_heap = (size > sizeof(stack_bytes));
    void* bytes = use_heap ? malloc(size) : stack_bytes;
    size_t words_written;
    mpz_export(bytes, &words_written, -1, 1, 0, 0, *x);
    clear(*output);
    ZZFromBytes(*output, (unsigned char *)bytes, words_written);
    if (mpz_sgn(*x) < 0)
        NTL::negate(*output, *output);
    if (use_heap)
        free(bytes);
}

/* Sets given ZZ to value
   AUTHOR: David Harvey (2008-06-08) */
void ZZ_set_from_int(ZZ* x, int value)
{
  conv(*x, value);
}

/*Random-number generation */

/*
void setSeed(const struct ZZ* n)
{
  SetSeed(*n);
}

struct ZZ* ZZ_randomBnd(const struct ZZ* n)
{
  ZZ *z = new ZZ();
  RandomBnd(*z,*n);
  return z;
}

struct ZZ* ZZ_randomBits(long n)
{
  ZZ *z = new ZZ();
  RandomBits(*z,n);
  return z;
}
*/

long ZZ_remove(struct ZZ &dest, const struct ZZ &src, const struct ZZ &f)
{
    // Based on the code for mpz_remove
    ZZ fpow[40];            // inexaustible...until year 2020 or so
    ZZ x, rem;
    long pwr;
    int p;

    if (compare(f, 1) <= 0)
        Error("Division by zero");

    if (compare(src, 0) == 0)
    {
        if (src != dest)
           dest = src;
        return 0;
    }

    if (compare(f, 2) == 0)
    {
        dest = src;
        return MakeOdd(dest);
    }

    /* We could perhaps compute mpz_scan1(src,0)/mpz_scan1(f,0).  It is an
     upper bound of the result we're seeking.  We could also shift down the
     operands so that they become odd, to make intermediate values smaller.  */

    pwr = 0;
    fpow[0] = ZZ(f);
    dest = src;
    rem = ZZ();
    x = ZZ();

    /* Divide by f, f^2, ..., f^(2^k) until we get a remainder for f^(2^k).  */
    for (p = 0;;p++)
    {
        DivRem(x, rem, dest, fpow[p]);
        if (compare(rem, 0) != 0)
            break;
        fpow[p+1] = ZZ();
        mul(fpow[p+1], fpow[p], fpow[p]);
        dest = x;
    }

    pwr = (1 << p) - 1;

    /* Divide by f^(2^(k-1)), f^(2^(k-2)), ..., f for all divisors that give a
       zero remainder.  */
    while (--p >= 0)
    {
        DivRem(x, rem, dest, fpow[p]);
        if (compare(rem, 0) == 0)
        {
            pwr += 1 << p;
            dest = x;
        }
    }
    return pwr;
}

//////// ZZ_p //////////

/* Return value is only valid if the result should fit into an int.
   AUTHOR: David Harvey (2008-06-08) */
int ZZ_p_to_int(const ZZ_p& x )
{
  return ZZ_to_int(&rep(x));
}

/* Returns a *new* ZZ_p object.
   AUTHOR: David Harvey (2008-06-08) */
ZZ_p int_to_ZZ_p(int value)
{
  ZZ_p r;
  r = value;
  return r;
}

/* Sets given ZZ_p to value
   AUTHOR: David Harvey (2008-06-08) */
void ZZ_p_set_from_int(ZZ_p* x, int value)
{
  conv(*x, value);
}

void ZZ_p_modulus(struct ZZ* mod, const struct ZZ_p* x)
{
	(*mod) = x->modulus();
}

struct ZZ_p* ZZ_p_pow(const struct ZZ_p* x, long e)
{
  ZZ_p *z = new ZZ_p();
  power(*z, *x, e);
  return z;
}

void ntl_ZZ_set_modulus(ZZ* x)
{
  ZZ_p::init(*x);
}

ZZ_p* ZZ_p_inv(ZZ_p* x)
{
  ZZ_p *z = new ZZ_p();
  inv(*z, *x);
  return z;
}

ZZ_p* ZZ_p_random(void)
{
  ZZ_p *z = new ZZ_p();
  random(*z);
  return z;
}

struct ZZ_p* ZZ_p_neg(struct ZZ_p* x)
{
  return new ZZ_p(-(*x));
}



///////////////////////////////////////////////
//////// ZZX //////////
///////////////////////////////////////////////

char* ZZX_repr(struct ZZX* x)
{
  ostringstream instore;
  instore << (*x);
  int n = strlen(instore.str().data());
  char* buf = new char[n+1];
  strcpy(buf, instore.str().data());
  return buf;
}

struct ZZX* ZZX_copy(struct ZZX* x) {
  return new ZZX(*x);
}

/* Sets ith coefficient of x to value.
   AUTHOR: David Harvey (2006-06-08) */
void ZZX_setitem_from_int(struct ZZX* x, long i, int value)
{
  SetCoeff(*x, i, value);
}

/* Returns ith coefficient of x.
   Return value is only valid if the result should fit into an int.
   AUTHOR: David Harvey (2006-06-08) */
int ZZX_getitem_as_int(struct ZZX* x, long i)
{
  return ZZ_to_int(&coeff(*x, i));
}

/* Copies ith coefficient of x to output.
   Assumes output has been mpz_init'd.
   AUTHOR: David Harvey (2007-02) */
void ZZX_getitem_as_mpz(mpz_t* output, struct ZZX* x, long i)
{
    const ZZ& z = coeff(*x, i);
    ZZ_to_mpz(output, &z);
}

struct ZZX* ZZX_div(struct ZZX* x, struct ZZX* y, int* divisible)
{
  struct ZZX* z = new ZZX();
  *divisible = divide(*z, *x, *y);
  return z;
}



void ZZX_quo_rem(struct ZZX* x, struct ZZX* other, struct ZZX** r, struct ZZX** q)
{
  struct ZZX *qq = new ZZX(), *rr = new ZZX();
  DivRem(*qq, *rr, *x, *other);
  *r = rr; *q = qq;
}


struct ZZX* ZZX_square(struct ZZX* x)
{
  struct ZZX* s = new ZZX();
  sqr(*s, *x);
  return s;
}


int ZZX_is_monic(struct ZZX* x)
{
  IsOne(LeadCoeff(*x));
}


struct ZZX* ZZX_neg(struct ZZX* x)
{
  struct ZZX* y = new ZZX();
  *y = -*x;
  return y;
}


struct ZZX* ZZX_left_shift(struct ZZX* x, long n)
{
  struct ZZX* y = new ZZX();
  LeftShift(*y, *x, n);
  return y;
}


struct ZZX* ZZX_right_shift(struct ZZX* x, long n)
{
  struct ZZX* y = new ZZX();
  RightShift(*y, *x, n);
  return y;
}

struct ZZX* ZZX_primitive_part(struct ZZX* x)
{
  struct ZZX* p = new ZZX();
  PrimitivePart(*p, *x);
  return p;
}


void ZZX_pseudo_quo_rem(struct ZZX* x, struct ZZX* y, struct ZZX** r, struct ZZX** q)
{
  *r = new ZZX();
  *q = new ZZX();
  PseudoDivRem(**q, **r, *x, *y);
}


struct ZZX* ZZX_gcd(struct ZZX* x, struct ZZX* y)
{
  struct ZZX* g = new ZZX();
  GCD(*g, *x, *y);
  return g;
}


void ZZX_xgcd(struct ZZX* x, struct ZZX* y, struct ZZ** r, struct ZZX** s, \
	      struct ZZX** t, int proof)
{
  *r = new ZZ();
  *s = new ZZX();
  *t = new ZZX();
  XGCD(**r, **s, **t, *x, *y, proof);
}


long ZZX_degree(struct ZZX* x)
{
  return deg(*x);
}

void ZZX_set_x(struct ZZX* x)
{
  SetX(*x);
}


int ZZX_is_x(struct ZZX* x)
{
  return IsX(*x);
}


struct ZZX* ZZX_derivative(struct ZZX* x)
{
  ZZX* d = new ZZX();
  diff(*d, *x);
  return d;
}


struct ZZX* ZZX_reverse(struct ZZX* x)
{
  ZZX* r = new ZZX();
  reverse(*r, *x);
  return r;
}

struct ZZX* ZZX_reverse_hi(struct ZZX* x, int hi)
{
  ZZX* r = new ZZX();
  reverse(*r, *x, hi);
  return r;
}


struct ZZX* ZZX_truncate(struct ZZX* x, long m)
{
  ZZX* t = new ZZX();
  trunc(*t, *x, m);
  return t;
}


struct ZZX* ZZX_multiply_and_truncate(struct ZZX* x, struct ZZX* y, long m)
{
  ZZX* t = new ZZX();
  MulTrunc(*t, *x, *y, m);
  return t;
}


struct ZZX* ZZX_square_and_truncate(struct ZZX* x, long m)
{
  ZZX* t = new ZZX();
  SqrTrunc(*t, *x, m);
  return t;
}


struct ZZX* ZZX_invert_and_truncate(struct ZZX* x, long m)
{
  ZZX* t = new ZZX();
  InvTrunc(*t, *x, m);
  return t;
}


struct ZZX* ZZX_multiply_mod(struct ZZX* x, struct ZZX* y,  struct ZZX* modulus)
{
  ZZX* p = new ZZX();
  MulMod(*p, *x, *y, *modulus);
  return p;
}


struct ZZ* ZZX_trace_mod(struct ZZX* x, struct ZZX* y)
{
  ZZ* p = new ZZ();
  TraceMod(*p, *x, *y);
  return p;
}


char* ZZX_trace_list(struct ZZX* x)
{
  vec_ZZ v;
  TraceVec(v, *x);
  ostringstream instore;
  instore << v;
  int n = strlen(instore.str().data());
  char* buf = new char[n+1];
  strcpy(buf, instore.str().data());
  return buf;
}


struct ZZ* ZZX_resultant(struct ZZX* x, struct ZZX* y, int proof)
{
  ZZ* res = new ZZ();
  resultant(*res, *x, *y, proof);
  return res;
}


struct ZZ* ZZX_norm_mod(struct ZZX* x, struct ZZX* y, int proof)
{
  ZZ* res = new ZZ();
  NormMod(*res, *x, *y, proof);
  return res;
}


struct ZZ* ZZX_discriminant(struct ZZX* x, int proof)
{
  ZZ* d = new ZZ();
  discriminant(*d, *x, proof);
  return d;
}


struct ZZX* ZZX_charpoly_mod(struct ZZX* x, struct ZZX* y, int proof)
{
  ZZX* f = new ZZX();
  CharPolyMod(*f, *x, *y, proof);
  return f;
}


struct ZZX* ZZX_minpoly_mod(struct ZZX* x, struct ZZX* y)
{
  ZZX* f = new ZZX();
  MinPolyMod(*f, *x, *y);
  return f;
}


void ZZX_clear(struct ZZX* x)
{
  clear(*x);
}


void ZZX_preallocate_space(struct ZZX* x, long n)
{
  x->SetMaxLength(n);
}

/*
EXTERN struct ZZ* ZZX_polyeval(struct ZZX* f, struct ZZ* a)
{
  ZZ* b = new ZZ();
  *b = PolyEval(*f, *a);
  return b;
}
*/

void ZZX_squarefree_decomposition(struct ZZX*** v, long** e, long* n, struct ZZX* x)
{
  vec_pair_ZZX_long factors;
  SquareFreeDecomp(factors, *x);
  *n = factors.length();
  *v = (ZZX**) malloc(sizeof(ZZX*) * (*n));
  *e = (long*) malloc(sizeof(long) * (*n));
  for (long i = 0; i < (*n); i++) {
    (*v)[i] = new ZZX(factors[i].a);
    (*e)[i] = factors[i].b;
  }
}

///////////////////////////////////////////////
//////// ZZ_pX //////////
///////////////////////////////////////////////

char* ZZ_pX_repr(struct ZZ_pX* x)
{
  ostringstream instore;
  instore << (*x);
  int n = strlen(instore.str().data());
  char* buf = new char[n+1];
  strcpy(buf, instore.str().data());
  return buf;
}

void ZZ_pX_dealloc(struct ZZ_pX* x) {
  delete x;
}

struct ZZ_pX* ZZ_pX_copy(struct ZZ_pX* x) {
  return new ZZ_pX(*x);
}

/* Sets ith coefficient of x to value.
   AUTHOR: David Harvey (2008-06-08) */
void ZZ_pX_setitem_from_int(struct ZZ_pX* x, long i, int value)
{
  SetCoeff(*x, i, value);
}

/* Returns ith coefficient of x.
   Return value is only valid if the result should fit into an int.
   AUTHOR: David Harvey (2008-06-08) */
int ZZ_pX_getitem_as_int(struct ZZ_pX* x, long i)
{
    return ZZ_to_int(&rep(coeff(*x, i)));
}

struct ZZ_pX* ZZ_pX_add(struct ZZ_pX* x, struct ZZ_pX* y)
{
  ZZ_pX *z = new ZZ_pX();
  add(*z, *x, *y);
  return z;
}

struct ZZ_pX* ZZ_pX_sub(struct ZZ_pX* x, struct ZZ_pX* y)
{
  ZZ_pX *z = new ZZ_pX();
  sub(*z, *x, *y);
  return z;
}

struct ZZ_pX* ZZ_pX_mul(struct ZZ_pX* x, struct ZZ_pX* y)
{
  ZZ_pX *z = new ZZ_pX();
  mul(*z, *x, *y);
  return z;
}


struct ZZ_pX* ZZ_pX_div(struct ZZ_pX* x, struct ZZ_pX* y, int* divisible)
{
  struct ZZ_pX* z = new ZZ_pX();
  *divisible = divide(*z, *x, *y);
  return z;
}


struct ZZ_pX* ZZ_pX_mod(struct ZZ_pX* x, struct ZZ_pX* y)
{
  struct ZZ_pX* z = new ZZ_pX();
  rem(*z, *x, *y);
  return z;
}



void ZZ_pX_quo_rem(struct ZZ_pX* x, struct ZZ_pX* y, struct ZZ_pX** r, struct ZZ_pX** q)
{
  *r = new ZZ_pX();
  *q = new ZZ_pX();
  DivRem(**q, **r, *x, *y);
}


struct ZZ_pX* ZZ_pX_square(struct ZZ_pX* x)
{
  struct ZZ_pX* s = new ZZ_pX();
  sqr(*s, *x);
  return s;
}



int ZZ_pX_is_monic(struct ZZ_pX* x)
{
  IsOne(LeadCoeff(*x));
}


struct ZZ_pX* ZZ_pX_neg(struct ZZ_pX* x)
{
  struct ZZ_pX* y = new ZZ_pX();
  *y = -*x;
  return y;
}


struct ZZ_pX* ZZ_pX_left_shift(struct ZZ_pX* x, long n)
{
  struct ZZ_pX* y = new ZZ_pX();
  LeftShift(*y, *x, n);
  return y;
}


struct ZZ_pX* ZZ_pX_right_shift(struct ZZ_pX* x, long n)
{
  struct ZZ_pX* y = new ZZ_pX();
  RightShift(*y, *x, n);
  return y;
}



struct ZZ_pX* ZZ_pX_gcd(struct ZZ_pX* x, struct ZZ_pX* y)
{
  struct ZZ_pX* g = new ZZ_pX();
  GCD(*g, *x, *y);
  return g;
}


void ZZ_pX_xgcd(struct ZZ_pX** d, struct ZZ_pX** s, struct ZZ_pX** t, struct ZZ_pX* a, struct ZZ_pX* b)
{
  *d = new ZZ_pX();
  *s = new ZZ_pX();
  *t = new ZZ_pX();
  XGCD(**d, **s, **t, *a, *b);
}

void ZZ_pX_plain_xgcd(struct ZZ_pX** d, struct ZZ_pX** s, struct ZZ_pX** t, struct ZZ_pX* a, struct ZZ_pX* b)
{
  *d = new ZZ_pX();
  *s = new ZZ_pX();
  *t = new ZZ_pX();
  PlainXGCD(**d, **s, **t, *a, *b);
}

ZZ_p* ZZ_pX_leading_coefficient(struct ZZ_pX* x)
{
  return new ZZ_p(LeadCoeff(*x));
}


void ZZ_pX_set_x(struct ZZ_pX* x)
{
  SetX(*x);
}


int ZZ_pX_is_x(struct ZZ_pX* x)
{
  return IsX(*x);
}


struct ZZ_pX* ZZ_pX_derivative(struct ZZ_pX* x)
{
  ZZ_pX* d = new ZZ_pX();
  diff(*d, *x);
  return d;
}


struct ZZ_pX* ZZ_pX_reverse(struct ZZ_pX* x)
{
  ZZ_pX* r = new ZZ_pX();
  reverse(*r, *x);
  return r;
}

struct ZZ_pX* ZZ_pX_reverse_hi(struct ZZ_pX* x, int hi)
{
  ZZ_pX* r = new ZZ_pX();
  reverse(*r, *x, hi);
  return r;
}


struct ZZ_pX* ZZ_pX_truncate(struct ZZ_pX* x, long m)
{
  ZZ_pX* t = new ZZ_pX();
  trunc(*t, *x, m);
  return t;
}


struct ZZ_pX* ZZ_pX_multiply_and_truncate(struct ZZ_pX* x, struct ZZ_pX* y, long m)
{
  ZZ_pX* t = new ZZ_pX();
  MulTrunc(*t, *x, *y, m);
  return t;
}


struct ZZ_pX* ZZ_pX_square_and_truncate(struct ZZ_pX* x, long m)
{
  ZZ_pX* t = new ZZ_pX();
  SqrTrunc(*t, *x, m);
  return t;
}


struct ZZ_pX* ZZ_pX_invert_and_truncate(struct ZZ_pX* x, long m)
{
  ZZ_pX* t = new ZZ_pX();
  InvTrunc(*t, *x, m);
  return t;
}


struct ZZ_pX* ZZ_pX_multiply_mod(struct ZZ_pX* x, struct ZZ_pX* y,  struct ZZ_pX* modulus)
{
  ZZ_pX* p = new ZZ_pX();
  MulMod(*p, *x, *y, *modulus);
  return p;
}


struct ZZ_p* ZZ_pX_trace_mod(struct ZZ_pX* x, struct ZZ_pX* y)
{
  ZZ_p* p = new ZZ_p();
  TraceMod(*p, *x, *y);
  return p;
}


char* ZZ_pX_trace_list(struct ZZ_pX* x)
{
  vec_ZZ_p v;
  TraceVec(v, *x);
  ostringstream instore;
  instore << v;
  int n = strlen(instore.str().data());
  char* buf = new char[n+1];
  strcpy(buf, instore.str().data());
  return buf;
}


struct ZZ_p* ZZ_pX_resultant(struct ZZ_pX* x, struct ZZ_pX* y)
{
  ZZ_p* res = new ZZ_p();
  resultant(*res, *x, *y);
  return res;
}


struct ZZ_p* ZZ_pX_norm_mod(struct ZZ_pX* x, struct ZZ_pX* y)
{
  ZZ_p* res = new ZZ_p();
  NormMod(*res, *x, *y);
  return res;
}



struct ZZ_pX* ZZ_pX_charpoly_mod(struct ZZ_pX* x, struct ZZ_pX* y)
{
  ZZ_pX* f = new ZZ_pX();
  CharPolyMod(*f, *x, *y);
  return f;
}


struct ZZ_pX* ZZ_pX_minpoly_mod(struct ZZ_pX* x, struct ZZ_pX* y)
{
  ZZ_pX* f = new ZZ_pX();
  MinPolyMod(*f, *x, *y);
  return f;
}


void ZZ_pX_clear(struct ZZ_pX* x)
{
  clear(*x);
}


void ZZ_pX_preallocate_space(struct ZZ_pX* x, long n)
{
  x->SetMaxLength(n);
}


void ZZ_pX_factor(struct ZZ_pX*** v, long** e, long* n, struct ZZ_pX* x, long verbose)
{
  long i;
  vec_pair_ZZ_pX_long factors;
  berlekamp(factors, *x, verbose);
  *n = factors.length();
  *v = (ZZ_pX**) malloc(sizeof(ZZ_pX*) * (*n));
  *e = (long*) malloc(sizeof(long)*(*n));
  for (i=0; i<(*n); i++) {
    (*v)[i] = new ZZ_pX(factors[i].a);
    (*e)[i] = factors[i].b;
  }
}

void ZZ_pX_linear_roots(struct ZZ_p*** v, long* n, struct ZZ_pX* f)
{
  long i;
  // printf("1\n");
  vec_ZZ_p w;
  FindRoots(w, *f);
  // printf("2\n");
  *n = w.length();
  //   printf("3 %d\n",*n);
  (*v) = (ZZ_p**) malloc(sizeof(ZZ_p*)*(*n));
  for (i=0; i<(*n); i++) {
    (*v)[i] = new ZZ_p(w[i]);
  }
}

/////////// ZZ_pE //////////////

struct ZZ_pX ZZ_pE_to_ZZ_pX(struct ZZ_pE x)
{
  ZZ_pX *ans = new ZZ_pX(rep(x));
  return *ans;
}



//////// mat_ZZ //////////

void mat_ZZ_SetDims(struct mat_ZZ* mZZ, long nrows, long ncols){
  mZZ->SetDims(nrows, ncols);
}

struct mat_ZZ* mat_ZZ_pow(const struct mat_ZZ* x, long e)
{
  mat_ZZ *z = new mat_ZZ();
  power(*z, *x, e);
  return z;
}

long mat_ZZ_nrows(const struct mat_ZZ* x)
{
  return x->NumRows();
}


long mat_ZZ_ncols(const struct mat_ZZ* x)
{
  return x->NumCols();
}

void mat_ZZ_setitem(struct mat_ZZ* x, int i, int j, const struct ZZ* z)
{
  (*x)[i][j] = *z;

}

struct ZZ* mat_ZZ_getitem(const struct mat_ZZ* x, int i, int j)
{
  return new ZZ((*x)(i,j));
}

struct ZZ* mat_ZZ_determinant(const struct mat_ZZ* x, long deterministic)
{
  ZZ* d = new ZZ();
  determinant(*d, *x, deterministic);
  return d;
}

struct mat_ZZ* mat_ZZ_HNF(const struct mat_ZZ* A, const struct ZZ* D)
{
  struct mat_ZZ* W = new mat_ZZ();
  HNF(*W, *A, *D);
  return W;
}

long mat_ZZ_LLL(struct ZZ **det, struct mat_ZZ *x, long a, long b, long verbose)
{
  *det = new ZZ();
  return LLL(**det,*x,a,b,verbose);
}

long mat_ZZ_LLL_U(struct ZZ **det, struct mat_ZZ *x, struct mat_ZZ *U, long a, long b, long verbose)
{
  *det = new ZZ();
  return LLL(**det,*x,*U,a,b,verbose);
}


struct ZZX* mat_ZZ_charpoly(const struct mat_ZZ* A)
{
  ZZX* f = new ZZX();
  CharPoly(*f, *A);
  return f;
}



/**
 * GF2X
 *
 * @author Martin Albrecht <malb@informatik.uni-bremen.de>
 *
 * @versions 2006-01 malb
 *           initial version (based on code by William Stein)
 */

struct GF2X* GF2X_pow(const struct GF2X* x, long e)
{
  GF2X *z = new GF2X();
  power(*z, *x, e);
  return z;
}

struct GF2X* GF2X_neg(struct GF2X* x)
{
  return new GF2X(-(*x));
}

struct GF2X* GF2X_copy(struct GF2X* x)
{
  GF2X *z = new GF2X(*x);
  return z;
}

long GF2X_deg(struct GF2X* x)
{
  return deg(*x);
}

void GF2X_hex(long h)
{
  GF2X::HexOutput=h;
}



PyObject* GF2X_to_bin(const struct GF2X* x)
{
  long hex;
  hex = GF2X::HexOutput;
  GF2X::HexOutput=0;
  std::ostringstream instore;
  instore << (*x);
  GF2X::HexOutput=hex;
  return PyString_FromString(instore.str().data());
}

PyObject* GF2X_to_hex(const struct GF2X* x)
{
  long hex;
  hex = GF2X::HexOutput;
  GF2X::HexOutput=1;
  std::ostringstream instore;
  instore << (*x);
  GF2X::HexOutput=hex;
  return PyString_FromString(instore.str().data());
}



/**
 * GF2E
 *
 * @author Martin Albrecht <malb@informatik.uni-bremen.de>
 *
 * @versions 2006-01 malb
 *           initial version (based on code by William Stein)
 */


void ntl_GF2E_set_modulus(GF2X* x)
{
  GF2E::init(*x);
}


struct GF2E* GF2E_pow(const struct GF2E* x, long e)
{
  GF2E *z = new GF2E();
  power(*z, *x, e);
  return z;
}


struct GF2E* GF2E_neg(struct GF2E* x)
{
  return new GF2E(-(*x));
}

struct GF2E* GF2E_copy(struct GF2E* x)
{
  GF2E *z = new GF2E(*x);
  return z;
}

long GF2E_trace(struct GF2E* x)
{
  return rep(trace(*x));
}


long GF2E_degree()
{
  return GF2E::degree();
}

const struct GF2X* GF2E_modulus()
{
  GF2XModulus mod = GF2E::modulus();
  GF2X *z = new GF2X(mod.val());
  return z;
}

struct GF2E *GF2E_random(void)
{
  GF2E *z = new GF2E();
  random(*z);
  return z;
}

const struct GF2X *GF2E_ntl_GF2X(struct GF2E *x) {
  GF2X *r = new GF2X(rep(*x));
  return r;
}


/**
 * mat_GF2E
 *
 * @author Martin Albrecht <malb@informatik.uni-bremen.de>
 *
 * @versions 2006-01 malb
 *           initial version (based on code by William Stein)
 */

void mat_GF2E_SetDims(struct mat_GF2E* m, long nrows, long ncols){
  m->SetDims(nrows, ncols);
}

struct mat_GF2E* mat_GF2E_pow(const struct mat_GF2E* x, long e)
{
  mat_GF2E *z = new mat_GF2E();
  power(*z, *x, e);
  return z;
}

long mat_GF2E_nrows(const struct mat_GF2E* x)
{
  return x->NumRows();
}


long mat_GF2E_ncols(const struct mat_GF2E* x)
{
  return x->NumCols();
}

void mat_GF2E_setitem(struct mat_GF2E* x, int i, int j, const struct GF2E* z)
{
  (*x)[i][j] = *z;
}

struct GF2E* mat_GF2E_getitem(const struct mat_GF2E* x, int i, int j)
{
  return new GF2E((*x)(i,j));
}

struct GF2E* mat_GF2E_determinant(const struct mat_GF2E* x)
{
  GF2E* d = new GF2E();
  determinant(*d, *x);
  return d;
}

long mat_GF2E_gauss(struct mat_GF2E *x, long w)
{
  if(w==0) {
    return gauss(*x);
  } else {
    return gauss(*x, w);
  }
}

struct mat_GF2E* mat_GF2E_transpose(const struct mat_GF2E* x) {
  mat_GF2E *y = new mat_GF2E();
  transpose(*y,*x);
  return y;
}



ZZ_pContext* ZZ_pContext_new(ZZ *p)
{
	return new ZZ_pContext(*p);
}

ZZ_pContext* ZZ_pContext_construct(void *mem, ZZ *p)
{
	return new(mem) ZZ_pContext(*p);
}

void ZZ_pContext_restore(ZZ_pContext *ctx)
{
	ctx->restore();
}

ZZ_pEContext* ZZ_pEContext_new(ZZ_pX *f)
{
	return new ZZ_pEContext(*f);
}

ZZ_pEContext* ZZ_pEContext_construct(void *mem, ZZ_pX *f)
{
	return new(mem) ZZ_pEContext(*f);
}

void ZZ_pEContext_restore(ZZ_pEContext *ctx)
{
	ctx->restore();
}

zz_pContext* zz_pContext_new(long p)
{
	return new zz_pContext(p);
}

zz_pContext* zz_pContext_construct(void *mem, long p)
{
	return new(mem) zz_pContext(p);
}

void zz_pContext_restore(zz_pContext *ctx)
{
	ctx->restore();
}
