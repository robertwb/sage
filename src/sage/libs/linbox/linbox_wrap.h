#ifndef LINBOX_WRAP_H
#define LINBOX_WRAP_H
#ifdef __cplusplus
#define EXTERN extern "C"
#else
#define EXTERN
#endif

/* Turn off lots of verbosity in the output of linbox functions */
#define DISABLE_COMMENTATOR

#include<stddef.h>
typedef size_t mod_int;

extern "C" {
#include "../m4ri/packedmatrix.h"
}


/*****************************************************************

  Dense modulo n.

*****************************************************************/

EXTERN int linbox_modn_dense_echelonize(mod_int modulus,
					mod_int** matrix, size_t nrows, size_t ncols);


EXTERN void linbox_modn_dense_minpoly(mod_int modulus, mod_int **mp, size_t* degree,
				      size_t n, mod_int **matrix, int do_minpoly);

EXTERN void linbox_modn_dense_delete_array(mod_int *f);

EXTERN int linbox_modn_dense_matrix_matrix_multiply(mod_int modulus, mod_int **ans, mod_int **A, mod_int **B,
						    size_t A_nr, size_t A_nc, size_t B_nr, size_t B_nc);

EXTERN int linbox_modn_dense_rank(mod_int modulus,
				  mod_int** matrix, size_t nrows, size_t ncols);


/*****************************************************************

  Dense modulo 2.

*****************************************************************/

EXTERN int linbox_mod2_dense_echelonize(packedmatrix *m);

EXTERN void linbox_mod2_dense_minpoly(mod_int **mp, size_t* degree, packedmatrix *matrix, int do_minpoly);

EXTERN int linbox_mod2_dense_matrix_matrix_multiply(packedmatrix *ans, packedmatrix *A, packedmatrix *B);

EXTERN int linbox_mod2_dense_rank(packedmatrix *m);

/*****************************************************************

  Dense over ZZ

*****************************************************************/

/* linbox_minpoly allocates space for minpoly, so you have to call linbox_delete_array
   to free it up afterwards. */
EXTERN void linbox_integer_dense_minpoly_hacked(mpz_t** minpoly, size_t* degree,
                  size_t n, mpz_t** matrix, int do_minpoly);
EXTERN void linbox_integer_dense_minpoly(mpz_t** minpoly, size_t* degree,
                  size_t n, mpz_t** matrix);
EXTERN void linbox_integer_dense_charpoly(mpz_t** charpoly, size_t* degree,
                  size_t n, mpz_t** matrix);
EXTERN void linbox_integer_dense_delete_array(mpz_t* f);

/* ans must be a pre-allocated and pre-initialized array of GMP ints. */
EXTERN int linbox_integer_dense_matrix_matrix_multiply(mpz_t** ans, mpz_t **A, mpz_t **B,
			      size_t A_nr, size_t A_nc, size_t B_nr, size_t B_nc);

EXTERN unsigned long linbox_integer_dense_rank(mpz_t** matrix, size_t nrows,
					       size_t ncols);

EXTERN  void linbox_integer_dense_det(mpz_t ans, mpz_t** matrix, size_t nrows,
				      size_t ncols);

EXTERN void linbox_integer_dense_smithform(mpz_t **v,
					   mpz_t **matrix,
					   size_t nrows, size_t ncols);

#endif // LINBOX_WRAP_H
