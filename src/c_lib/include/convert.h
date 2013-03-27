/*

  convert.h
  2007 Aug 19
  Author: Craig Citro

  C header for conversions to and from pari types.

*/

#include <gmp.h>
#include <pari/pari.h>
#include <stdio.h>

void t_INT_to_ZZ ( mpz_t value, GEN g );
void t_FRAC_to_QQ ( mpq_t value, GEN g );
