/* Copyright (C) 2004, 2005 Patrick Pelissier, Paul Zimmermann,
   LORIA/INRIA Lorraine.

This file is part of the DPE Library.

The DPE Library is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2.1 of the License, or (at your
option) any later version.

The DPE Library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
License for more details.

You should have received a copy of the GNU Lesser General Public License
along with the DPE Library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
MA 02111-1307, USA. */


#include <stdlib.h> /* For abort */
#include <stdio.h>  /* For fprintf */
#include <math.h>   /* for round, floor, ceil */
#include <limits.h>


#ifndef __DPE
#define __DPE

#define DPE_VERSION_MAJOR 1
#define DPE_VERSION_MINOR 4

#if defined(__GNUC__) && (__GNUC__ >= 3)
# define DPE_LIKELY(x) (__builtin_expect(!!(x),1))
# define DPE_UNLIKELY(x) (__builtin_expect((x),0))
# define DPE_UNUSED_ATTR  /*__attribute__((unused))*/
#else
# define DPE_LIKELY(x) (x)
# define DPE_UNLIKELY(x) (x)
# define DPE_UNUSED_ATTR
#endif

#if !defined(DPE_USE_DOUBLE) && !defined(DPE_USE_LONGDOUBLE)
# define DPE_USE_DOUBLE
#endif

#if (defined(__i386) || defined (__x86_64)) && !defined(DPE_LITTLEENDIAN32) && defined(DPE_USE_DOUBLE)
# define DPE_LITTLEENDIAN32
#endif

#if defined(DPE_USE_DOUBLE)
# define DPE_DOUBLE double /* mantissa type */
# define DPE_BITSIZE 53 /* bitsize of DPE_DOUBLE */
# define DPE_2_POW_BITSIZE 0x1P53
/* DPE_LDEXP(DPE_DOUBLE m, DPEEXP e) return x = m * 2^e */
# define DPE_LDEXP ldexp
/* DPE_FREXP(DPE_DOUBLE x, DPEEXP *e) returns m, e such that x = m * 2^e with
   1/2 <= m < 1 */
# define DPE_FREXP frexp
/* DPE_ROUND(DPE_DOUBLE x) returns the nearest integer to x */
# define DPE_ROUND round
# define DPE_FLOOR floor
# define DPE_CEIL ceil
# define DPE_TRUNC trunc
/* some versions of math.h do not include a prototype for round() */
#ifndef round
#if defined (__sun)
#define round(a) ((fmod(a,1)<0.5)?floor(a):ceil(a))
#else
double round(double);
#endif
#endif
#ifndef trunc
double trunc(double);
#endif
#elif defined(DPE_USE_LONGDOUBLE)
# define DPE_DOUBLE long double
# define DPE_BITSIZE 64
# define DPE_2_POW_BITSIZE 0x1P64
# define DPE_LDEXP ldexpl
# define DPE_FREXP frexpl
# define DPE_ROUND roundl
# define DPE_FLOOR floorl
# define DPE_CEIL ceill
# define DPE_TRUNC truncl
/* some versions of math.h do not include a prototype for roundl() */
#ifndef roundl
long double roundl(long double);
#endif
#ifndef truncl
long double truncl(long double);
#endif
#else
# error "neither DPE_USE_DOUBLE nor DPE_USE_LONGDOUBLE is defined"
#endif

#if defined(DPE_USE_LONG)
# define DPE_EXP_T  long    /* exponent type */
# define DPE_EXPMIN LONG_MIN /* smallest possible exponent */
#elif defined(DPE_USE_LONGLONG)
# define DPE_EXP_T  long long
# define DPE_EXPMIN LONG_LONG_MIN
#else
# define DPE_EXP_T  int     /* exponent type */
# define DPE_EXPMIN INT_MIN /* smallest possible exponent */
#endif


typedef struct
{
  DPE_DOUBLE d; /* significand */
  DPE_EXP_T exp; /* exponent */
} dpe_struct;

typedef dpe_struct dpe_t[1];

#define DPE_MANT(x) ((x)->d)
#define DPE_EXP(x)  ((x)->exp)
#define DPE_SIGN(x) ((DPE_MANT(x) < 0.0) ? -1 : (DPE_MANT(x) > 0.0))

#define DPE_INLINE static inline

/* initialize */
DPE_INLINE void
dpe_init (dpe_t x/* DPE_UNUSED_ATTR*/)
{
}

/* clear */
DPE_INLINE void
dpe_clear (dpe_t x/* DPE_UNUSED_ATTR*/)
{
}

/* set x to y */
DPE_INLINE void
dpe_set (dpe_t x, dpe_t y)
{
  DPE_MANT(x) = DPE_MANT(y);
  DPE_EXP(x) = DPE_EXP(y);
}

/* set x to -y */
DPE_INLINE void
dpe_neg (dpe_t x, dpe_t y)
{
  DPE_MANT(x) = -DPE_MANT(y);
  DPE_EXP(x) = DPE_EXP(y);
}

/* set x to |y| */
DPE_INLINE void
dpe_abs (dpe_t x, dpe_t y)
{
  DPE_MANT(x) = (DPE_MANT(y) >= 0) ? DPE_MANT(y) : -DPE_MANT(y);
  DPE_EXP(x) = DPE_EXP(y);
}

/* set mantissa in [1/2, 1), except for 0 which has minimum exponent */
/* FIXME: don't inline this function yet ? */
static void
dpe_normalize (dpe_t x)
{
  if (DPE_UNLIKELY (DPE_MANT(x) == 0.0 || finite (DPE_MANT(x)) == 0))
    {
      if (DPE_MANT(x) == 0.0)
        DPE_EXP(x) = DPE_EXPMIN;
      /* otherwise let the exponent of NaN, Inf unchanged */
    }
  else
    {
      DPE_EXP_T e;
#ifdef DPE_LITTLEENDIAN32 /* 32-bit little endian */
      volatile unsigned int *i = (unsigned int *) &(DPE_MANT(x));
      e = (i[1] >> 20) & 0x7FF; /* unbiased exponent, 1022 for m=1/2 */
      DPE_EXP(x) += e - 1022;
      i[1] = (i[1] & 0x800FFFFF) | 0x3FE00000;
      DPE_MANT (x) = (double) DPE_MANT (x); /* Flush MANT */
#else /* portable code */
      double m = DPE_MANT(x);
      DPE_MANT(x) = DPE_FREXP (m, &e);
      DPE_EXP(x) += e;
#endif
    }
}

#if defined(DPE_USE_DOUBLE)
static const double dpe_scale_tab[54] = {
  0x1P0, 0x1P-1, 0x1P-2, 0x1P-3, 0x1P-4, 0x1P-5, 0x1P-6, 0x1P-7, 0x1P-8,
  0x1P-9, 0x1P-10, 0x1P-11, 0x1P-12, 0x1P-13, 0x1P-14, 0x1P-15, 0x1P-16,
  0x1P-17, 0x1P-18, 0x1P-19, 0x1P-20, 0x1P-21, 0x1P-22, 0x1P-23, 0x1P-24,
  0x1P-25, 0x1P-26, 0x1P-27, 0x1P-28, 0x1P-29, 0x1P-30, 0x1P-31, 0x1P-32,
  0x1P-33, 0x1P-34, 0x1P-35, 0x1P-36, 0x1P-37, 0x1P-38, 0x1P-39, 0x1P-40,
  0x1P-41, 0x1P-42, 0x1P-43, 0x1P-44, 0x1P-45, 0x1P-46, 0x1P-47, 0x1P-48,
  0x1P-49, 0x1P-50, 0x1P-51, 0x1P-52, 0x1P-53};
#endif

DPE_INLINE double
dpe_scale (double d, int s)
{
  /* -DPE_BITSIZE < s <= 0 and 1/2 <= d < 1 */
#if defined(DPE_USE_DOUBLE)
  return d * dpe_scale_tab [-s];
#else /* portable code */
  return DPE_LDEXP (d, s);
#endif
}

/* set x to y */
DPE_INLINE void
dpe_set_d (dpe_t x, double y)
{
  DPE_MANT(x) = (DPE_DOUBLE) y;
  DPE_EXP(x) = 0;
  dpe_normalize (x);
}

/* set x to y */
DPE_INLINE void
dpe_set_ld (dpe_t x, long double y)
{
  DPE_MANT(x) = (DPE_DOUBLE) y;
  DPE_EXP(x) = 0;
  dpe_normalize (x);
}


/* set x to y */
DPE_INLINE void
dpe_set_ui (dpe_t x, unsigned long y)
{
  DPE_MANT(x) = (DPE_DOUBLE) y;
  DPE_EXP(x) = 0;
  dpe_normalize (x);
}

/* set x to y */
DPE_INLINE void
dpe_set_si (dpe_t x, long y)
{
  DPE_MANT(x) = (DPE_DOUBLE) y;
  DPE_EXP(x) = 0;
  dpe_normalize (x);
}


DPE_INLINE long
dpe_get_si (dpe_t x)
{
  DPE_DOUBLE d = DPE_LDEXP (DPE_MANT (x), DPE_EXP (x));
  return (long) d;
}

DPE_INLINE unsigned long
dpe_get_ui (dpe_t x)
{
  DPE_DOUBLE d = DPE_LDEXP (DPE_MANT (x), DPE_EXP (x));
  return (d < 0.0) ? 0 : (unsigned long) d;
}

DPE_INLINE double
dpe_get_d (dpe_t x)
{
  return DPE_LDEXP (DPE_MANT (x), DPE_EXP (x));
}

DPE_INLINE long double
dpe_get_ld (dpe_t x)
{
  return DPE_LDEXP (DPE_MANT (x), DPE_EXP (x));
}


#ifdef __GMP_H__
/* set x to y */
DPE_INLINE void
dpe_set_z (dpe_t x, mpz_t y)
{
  long e;
  DPE_MANT(x) = mpz_get_d_2exp (&e, y);
  DPE_EXP(x) = (DPE_EXP_T) e;
}

/* set x to y, rounded to nearest */
DPE_INLINE void
dpe_get_z (mpz_t x, dpe_t y)
{
  DPE_EXP_T ey = DPE_EXP(y);
  if (ey >= DPE_BITSIZE) /* y is an integer */
    {
      DPE_DOUBLE d = DPE_MANT(y) * DPE_2_POW_BITSIZE; /* d is an integer */
      mpz_set_d (x, d); /* should be exact */
      mpz_mul_2exp (x, x, (unsigned long) ey - DPE_BITSIZE);
    }
  else /* DPE_EXP(y) < DPE_BITSIZE */
    {
      if (DPE_UNLIKELY (ey < 0)) /* |y| < 1/2 */
        mpz_set_ui (x, 0);
      else
        {
          DPE_DOUBLE d = DPE_LDEXP(DPE_MANT(y), ey);
          mpz_set_d (x, (double) DPE_ROUND(d));
        }
    }
}

/* return e and x such that y = x*2^e */
DPE_INLINE mp_exp_t
dpe_get_z_exp (mpz_t x, dpe_t y)
{
  mpz_set_d (x, DPE_MANT (y) * DPE_2_POW_BITSIZE);
  return DPE_EXP(y) - DPE_BITSIZE;
}
#endif

/* x <- y + z, assuming y and z are normalized, returns x normalized */
DPE_INLINE void
dpe_add (dpe_t x, dpe_t y, dpe_t z)
{
  if (DPE_UNLIKELY (DPE_EXP(y) > DPE_EXP(z) + DPE_BITSIZE))
    /* |z| < 1/2*ulp(y), thus o(y+z) = y */
    dpe_set (x, y);
  else if (DPE_UNLIKELY (DPE_EXP(z) > DPE_EXP(y) + DPE_BITSIZE))
    dpe_set (x, z);
  else
    {
      DPE_EXP_T d = DPE_EXP(y) - DPE_EXP(z); /* |d| <= DPE_BITSIZE */

      if (d >= 0)
        {
          DPE_MANT(x) = DPE_MANT(y) + dpe_scale (DPE_MANT(z), -d);
          DPE_EXP(x) = DPE_EXP(y);
        }
      else
        {
          DPE_MANT(x) = DPE_MANT(z) + dpe_scale (DPE_MANT(y), d);
          DPE_EXP(x) = DPE_EXP(z);
        }
      dpe_normalize (x);
    }
}

/* x <- y - z, assuming y and z are normalized, returns x normalized */
DPE_INLINE void
dpe_sub (dpe_t x, dpe_t y, dpe_t z)
{
  if (DPE_UNLIKELY (DPE_EXP(y) > DPE_EXP(z) + DPE_BITSIZE))
    /* |z| < 1/2*ulp(y), thus o(y-z) = y */
    dpe_set (x, y);
  else if (DPE_UNLIKELY (DPE_EXP(z) > DPE_EXP(y) + DPE_BITSIZE))
    dpe_neg (x, z);
  else
    {
      DPE_EXP_T d = DPE_EXP(y) - DPE_EXP(z); /* |d| <= DPE_BITSIZE */

      if (d >= 0)
        {
          DPE_MANT(x) = DPE_MANT(y) - dpe_scale (DPE_MANT(z), -d);
          DPE_EXP(x) = DPE_EXP(y);
        }
      else
        {
          DPE_MANT(x) = dpe_scale (DPE_MANT(y), d) - DPE_MANT(z);
          DPE_EXP(x) = DPE_EXP(z);
        }
      dpe_normalize (x);
    }
}

/* x <- y * z, assuming y and z are normalized, returns x normalized */
DPE_INLINE void
dpe_mul (dpe_t x, dpe_t y, dpe_t z)
{
  DPE_MANT(x) = DPE_MANT(y) * DPE_MANT(z);
  DPE_EXP(x) = DPE_EXP(y) + DPE_EXP(z);
  dpe_normalize (x);
}

/* x <- sqrt(y), assuming y is normalized, returns x normalized */
DPE_INLINE void
dpe_sqrt (dpe_t x, dpe_t y)
{
  DPE_EXP_T ey = DPE_EXP(y);
  if (ey % 2)
    {
      /* since 1/2 <= my < 1, 1/4 <= my/2 < 1 */
      DPE_MANT(x) = sqrt (0.5 * DPE_MANT(y));
      DPE_EXP(x) = (ey + 1) / 2;
    }
  else
    {
      DPE_MANT(x) = sqrt (DPE_MANT(y));
      DPE_EXP(x) = ey / 2;
    }
}

/* x <- y / z, assuming y and z are normalized, returns x normalized.
   Assumes z is not zero. */
DPE_INLINE void
dpe_div (dpe_t x, dpe_t y, dpe_t z)
{
  DPE_MANT(x) = DPE_MANT(y) / DPE_MANT(z);
  DPE_EXP(x) = DPE_EXP(y) - DPE_EXP(z);
  dpe_normalize (x);
}

/* x <- y * z, assuming y normalized, returns x normalized */
DPE_INLINE void
dpe_mul_ui (dpe_t x, dpe_t y, unsigned long z)
{
  DPE_MANT(x) = DPE_MANT(y) * (DPE_DOUBLE) z;
  DPE_EXP(x) = DPE_EXP(y);
  dpe_normalize (x);
}

/* x <- y / z, assuming y normalized, z non-zero, returns x normalized */
DPE_INLINE void
dpe_div_ui (dpe_t x, dpe_t y, unsigned long z)
{
  DPE_MANT(x) = DPE_MANT(y) / (DPE_DOUBLE) z;
  DPE_EXP(x) = DPE_EXP(y);
  dpe_normalize (x);
}

/* x <- y * 2^e */
DPE_INLINE void
dpe_mul_2exp (dpe_t x, dpe_t y, unsigned long e)
{
  DPE_MANT(x) = DPE_MANT(y);
  DPE_EXP(x) = DPE_EXP(y) + (DPE_EXP_T) e;
}

/* x <- y / 2^e */
DPE_INLINE void
dpe_div_2exp (dpe_t x, dpe_t y, unsigned long e)
{
  DPE_MANT(x) = DPE_MANT(y);
  DPE_EXP(x) = DPE_EXP(y) - (DPE_EXP_T) e;
}

static /*DPE_UNUSED_ATTR*/ int dpe_str_prec = 16;
static int dpe_out_str (FILE *s, int base, dpe_t x)/* DPE_UNUSED_ATTR*/;

/* return e and x such that y = x*2^e */
DPE_INLINE mp_exp_t
dpe_get_si_exp (long *x, dpe_t y)
{
  if (sizeof(long) == 4) /* 32-bit word: long has 31 bits */
    {
      *x = (long) (DPE_MANT (y) * 2147483648.0);
      if (DPE_EXP(y) - 31<0)
	{
	  *x = (long)ldexpl(*x, DPE_EXP(y) - 31);/*Avoid implicit typecasts*/
	  return 0;
	}
      else
	{
	  return DPE_EXP(y) - 31;
	}
    }
  else if (sizeof(long) == 8) /* 64-bit word: long has 63 bits */
    {
      *x = (long) (DPE_MANT (y) * 9223372036854775808.0);
      if (DPE_EXP(y) - 63<0)
	{
	  *x = (long)ldexpl(*x, DPE_EXP(y) - 63);
	  return 0;
	}
      else
	{
	  return DPE_EXP(y) - 63;
	}
    }
  else
    {
      fprintf (stderr, "Error, neither 32-bit nor 64-bit word\n");
      abort();
    }
}


static int
dpe_out_str (FILE *s, int base, dpe_t x)
{
  DPE_DOUBLE d = DPE_MANT(x);
  DPE_EXP_T e2 = DPE_EXP(x);
  int e10 = 0;
  char sign = ' ';
  if (DPE_UNLIKELY (base != 10))
    {
      fprintf (stderr, "Error in dpe_out_str, only base 10 allowed\n");
      abort ();
    }
  if (d == 0.0)
#ifdef DPE_USE_DOUBLE
    return fprintf (s, "%1.*f", dpe_str_prec, d);
#else
    return fprintf (s, "connard\n %1.*Lf", dpe_str_prec, d);
#endif
  if (d < 0)
    {
      d = -d;
      sign = '-';
    }
  if (e2 > 0)
    {
      while (e2 > 0)
        {
          e2 --;
          d *= 2.0;
          if (d >= 10.0)
            {
              d /= 10.0;
              e10 ++;
            }
        }
    }
  else /* e2 <= 0 */
    {
      while (e2 < 0)
        {
          e2 ++;
          d /= 2.0;
          if (d < 1.0)
            {
              d *= 10.0;
              e10 --;
            }
        }
    }
#ifdef DPE_USE_DOUBLE
  return fprintf (s, "%c%1.*f*10^%d", sign, dpe_str_prec, d, e10);
#else
  return fprintf (s, "%c%1.*Lf*10^%d", sign, dpe_str_prec, d, e10);
#endif
}

static size_t dpe_inp_str (dpe_t x, FILE *s, int base) DPE_UNUSED_ATTR;

static size_t
dpe_inp_str (dpe_t x, FILE *s, int base)
{
  size_t res;
  DPE_DOUBLE d;
  if (DPE_UNLIKELY (base != 10))
    {
      fprintf (stderr, "Error in dpe_out_str, only base 10 allowed\n");
      abort ();
    }
#ifdef DPE_USE_DOUBLE
  res = fscanf (s, "%lf", &d);
#else
  res = fscanf (s, "%Lf", &d);
#endif
  dpe_set_d (x, d);
  return res;
}

DPE_INLINE void
dpe_dump (dpe_t x)
{
  dpe_out_str (stdout, 10, x);
  putchar ('\n');
}

DPE_INLINE int
dpe_zero_p (dpe_t x)
{
  return DPE_MANT (x) == 0;
}

/* return a positive value if x > y
          a negative value if x < y
          and 0 otherwise (x=y). */
DPE_INLINE int
dpe_cmp (dpe_t x, dpe_t y)
{
  int sx = DPE_SIGN(x);
  int d = sx - DPE_SIGN(y);

  if (d != 0)
    return d;
  else if (DPE_EXP(x) > DPE_EXP(y))
    return (sx > 0) ? 1 : -1;
  else if (DPE_EXP(y) > DPE_EXP(x))
    return (sx > 0) ? -1 : 1;
  else /* DPE_EXP(x) = DPE_EXP(y) */
    return (DPE_MANT(x) < DPE_MANT(y)) ? -1 : (DPE_MANT(x) > DPE_MANT(y));
}

DPE_INLINE int
dpe_cmp_d (dpe_t x, double d)
{
  dpe_t y;
  dpe_set_d (y, d);
  return dpe_cmp (x, y);
}

DPE_INLINE int
dpe_cmp_ui (dpe_t x, unsigned long d)
{
  dpe_t y;
  dpe_set_ui (y, d);
  return dpe_cmp (x, y);
}

DPE_INLINE int
dpe_cmp_si (dpe_t x, long d)
{
  dpe_t y;
  dpe_set_si (y, d);
  return dpe_cmp (x, y);
}

/* set x to integer nearest to y */
DPE_INLINE void
dpe_round (dpe_t x, dpe_t y)
{
  if (DPE_EXP(y) < 0) /* |y| < 1/2 */
    dpe_set_ui (x, 0);
  else if (DPE_EXP(y) >= DPE_BITSIZE) /* y is an integer */
    dpe_set (x, y);
  else
    {
      DPE_DOUBLE d;
      d = DPE_LDEXP(DPE_MANT(y), DPE_EXP(y));
      dpe_set_d (x, DPE_ROUND(d));
    }
}

/* set x to the fractional part of y */
DPE_INLINE void
dpe_frac (dpe_t x, dpe_t y)
{
  /* If y is smaller than 1, keep it */
  if (DPE_EXP(y) <= 0) dpe_set (x, y);
  else if (DPE_EXP(y) >= DPE_BITSIZE) /* y is an integer */
    dpe_set_ui (x, 0);
  else
    {
      DPE_DOUBLE d;
      d=DPE_LDEXP(DPE_MANT(y), DPE_EXP(y));
      dpe_set_d (x, d-DPE_TRUNC(d));
    }
}


/* set x to largest integer <= y */
DPE_INLINE void
dpe_floor (dpe_t x, dpe_t y)
{
  if (DPE_EXP(y) <= 0) /* |y| < 1 */
    {
      if (DPE_SIGN(y) >= 0) /* 0 <= y < 1 */
        dpe_set_ui (x, 0);
      else /* -1 < y < 0 */
        dpe_set_si (x, -1);
    }
  else if (DPE_EXP(y) >= DPE_BITSIZE) /* y is an integer */
    dpe_set (x, y);
  else
    {
      DPE_DOUBLE d;
      d = DPE_LDEXP(DPE_MANT(y), DPE_EXP(y));
      dpe_set_d (x, DPE_FLOOR(d));
    }
}

/* set x to smallest integer >= y */
DPE_INLINE void
dpe_ceil (dpe_t x, dpe_t y)
{
  if (DPE_EXP(y) <= 0) /* |y| < 1 */
    {
      if (DPE_SIGN(y) > 0) /* 0 < y < 1 */
        dpe_set_ui (x, 1);
      else /* -1 < y <= 0 */
        dpe_set_si (x, 0);
    }
  else if (DPE_EXP(y) >= DPE_BITSIZE) /* y is an integer */
    dpe_set (x, y);
  else
    {
      DPE_DOUBLE d;
      d = DPE_LDEXP(DPE_MANT(y), DPE_EXP(y));
      dpe_set_d (x, DPE_CEIL(d));
    }
}

DPE_INLINE void
dpe_swap (dpe_t x, dpe_t y)
{
  DPE_EXP_T i = DPE_EXP (x);
  DPE_DOUBLE d = DPE_MANT (x);
  DPE_EXP (x) = DPE_EXP (y);
  DPE_MANT (x) = DPE_MANT (y);
  DPE_EXP (y) = i;
  DPE_MANT (y) = d;
}

#endif /* __DPE */
