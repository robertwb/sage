"""
C level declarations of symbols in the SINGULAR libary.

AUTHOR: Martin Albrecht <malb@informatik.uni-bremen.de>

NOTE: our ring, poly etc. types are not the SINGULAR ring, poly,
etc. types. They are deferences. So a SINGULAR ring is a ring pointer
here.

"""
include "sage/ext/stdsage.pxi"
include "sage/ext/cdefs.pxi"

cdef extern from "stdlib.h":
    void delete "delete" (void *ptr)


cdef extern from "factory.h":

    #
    # CF OPTIONS
    #

    void On( int )
    void Off( int )
    int isOn( int )

    cdef int SW_USE_CHINREM_GCD
    cdef int SW_USE_EZGCD

cdef extern from "libsingular.h":

    #
    # OPTIONS
    #

    # We are working around a bug in Cython here. If you want to write
    # to an external int Cython creates a local Python it to write
    # to. We can however happyly work with pointers.

    cdef int *singular_options "(&test)"

    # actual options
    cdef int OPT_PROT
    cdef int OPT_REDSB
    cdef int OPT_NOT_BUCKETS
    cdef int OPT_NOT_SUGAR
    cdef int OPT_INTERRUPT
    cdef int OPT_SUGARCRIT
    cdef int OPT_DEBUG
    cdef int OPT_REDTHROUGH
    cdef int OPT_RETURN_SB
    cdef int OPT_FASTHC
    cdef int OPT_OLDSTD
    cdef int OPT_KEEPVARS
    cdef int OPT_STAIRCASEBOUND
    cdef int OPT_MULTBOUND
    cdef int OPT_DEGBOUND
    cdef int OPT_REDTAIL
    cdef int OPT_INTSTRATEGY
    cdef int OPT_INFREDTAIL
    cdef int OPT_SB_1
    cdef int OPT_NOTREGULARITY
    cdef int OPT_WEIGHTM

    # getter/setter functions
    int Sy_bit(int)
    int Sy_inset(int x,int s)
    int BTEST1(int)
    int BVERBOSE(int)

    #
    # STRUCTS
    #

    # rational numbers

    ctypedef struct number "snumber":
        mpz_t z
        mpz_t n
        int s

    # finite extension field elements

    ctypedef struct napoly "polyrec"

    # algebraic numbers

    ctypedef struct lnumber "slnumber":
        napoly *z
        napoly *n
        int s

    # rings

    ctypedef struct ring "ip_sring":
        int  *order  # array of orderings
        int  *block0 # starting pos
        int  *block1 # ending pos
        int  **wvhdl # weight vectors
        int  OrdSgn  # 1 for polynomial rings
        int  ShortOut # control printing
        int  CanShortOut # control printing capabilities
        number *minpoly # minpoly for base extension field
        char **names # variable names
        char **parameter # parameter names
        ring *algring # base extension field
        short N # number of variables
        short P # number of parameters
        int ch # charactersitic (0:QQ, p:GF(p),-p:GF(q), 1:NF)

    # available ring orders

    cdef enum rRingOrder_t:
        ringorder_no
        ringorder_a
        ringorder_a64 # for int64 weights
        ringorder_c
        ringorder_C
        ringorder_M
        ringorder_S
        ringorder_s
        ringorder_lp
        ringorder_dp
        ringorder_rp
        ringorder_Dp
        ringorder_wp
        ringorder_Wp
        ringorder_ls
        ringorder_ds
        ringorder_Ds
        ringorder_ws
        ringorder_Ws
        ringorder_L

    # polynomials

    ctypedef struct poly "polyrec":
        poly *next


    # groebner basis options

    cdef enum tHomog:
        isNotHomog
        isHomog
        testHomog

    # ideals

    ctypedef struct ideal "ip_sideal":
        poly **m # gens array
        long rank # rank of module, 1 for ideals
        int nrows # always 1
        int ncols # number of gens

    # dense matrices

    ctypedef struct matrix "ip_smatrix":
        poly **m # gens array
        long rank # rank of module, 1 for normal matrices
        int nrows # number of rows
        int ncols # number of columns

    # integer vectors

    ctypedef struct intvec:
        int *(*ivGetVec)() # this is internal actually
        int (*rows)()
        int (*cols)()

    # omalloc bins

    ctypedef struct omBin "omBin_s"

    #
    # GLOBAL VARIABLES
    #

    # current ring

    cdef ring *currRing

    # omalloc bin for numbers

    cdef omBin *rnumber_bin

    # omalloc bin for rings

    cdef omBin *sip_sring_bin

    # integer conversion constant

    cdef long SR_INT


    #
    # FUNCTIONS
    #

    # singular init

    int siInit(char *)

    # external resource init

    void feInitResources(char *name)




    # calloc

    void *omAlloc0(size_t size)

    # typed malloc from bin

    void *omAllocBin(omBin *bin)

    # typed calloc from bin

    void *omAlloc0Bin(omBin *bin)

    # strdup

    char *omStrDup(char *)

    # free

    void omFree(void *)




    # construct ring with characteristic, number of vars and names

    ring *rDefault(int char, int nvars, char **names)

    # ring destructor

    void rDelete(ring *r)

    # return characteristic of r

    int rChar(ring *r)

    # return name of the i-th variable of ring r

    char* rRingVar(short i, ring *r)

    # before changing a ring struct, call this

    void rUnComplete(ring *r)

    # after changing a ring struct, call thi

    void rComplete(ring *r, int force)

    # deep copy of ring

    ring *rCopy0(ring *)

    # change current ring to r

    void rChangeCurrRing(ring *r)




    # return new empty monomial

    poly *p_Init(ring *r)

    # return constant polynomial from int

    poly *p_ISet(int i, ring *r)

    # return constant polynomial from number

    poly *p_NSet(number *n,ring *r)

    # destructor for polynomials

    void p_Delete(poly **p, ring *r)

    # set the coefficient n for the current list element p in r

    int p_SetCoeff(poly *p, number *n, ring *r)

    # get the coefficient of the current list element p in r

    number *p_GetCoeff(poly *p, ring *r)

    # set the exponent e at index v for the monomial p, v starts at 1

    int p_SetExp(poly *p, int v, int e, ring *r)

    # get the exponent at index v of the monomial p in r, v starts at 1

    int p_GetExp(poly *p, int v, ring *r)

    # if SetExp is called on p, p_Setm needs to be called afterwards to finalize the change.

    void p_Setm(poly *p, ring *r)

    # gets a component out of a polynomial vector

    poly *pTakeOutComp1(poly **, int)

    # deep copy p

    poly *p_Copy(poly *p, ring *r)

    # homogenizes p by multiplying certain powers of the varnum-th variable

    poly *pHomogen (poly *p, int varnum)

    # return whether a polynomial is homogenous

    int pIsHomogeneous(poly *p)

    # return string representation of p

    char *p_String(poly *p, ring *r, ring *r)

    # normalize p, needed e.g. for polynomials over the rationals

    void p_Normalize(poly *p, ring *r)

    # return -p, p is destroyed

    poly *p_Neg(poly *p, ring *r)

    # return p*n, p is const (i.e. copied)

    poly *pp_Mult_nn(poly *p, number *n, ring *r)

    # return p*m, does neither destroy p nor m

    poly *pp_Mult_mm(poly *p, poly *m, ring *r)

    # return p+q, destroys p and q

    poly *p_Add_q(poly *p, poly *q, ring *r)

    # return p - m*q, destroys p; const: q,m

    poly *p_Minus_mm_Mult_qq(poly *p, poly *m, poly *q, ring *r)

    # return p + m*q destroys p, const: q, m

    poly *p_Plus_mm_Mult_qq(poly *p, poly *m, poly *q, ring *r)

    # return p*q, does neither destroy p nor q
    poly *pp_Mult_qq(poly *p, poly *q, ring *r)

    # return p*q, destroys p and q
    poly *p_Mult_q(poly *p, poly *q, ring *r)

    # divide monomial p by monomial q, p,q const

    poly *pDivide(poly *p,poly *q)

    # return the i-th power of p; p destroyed, requires global ring

    poly *pPower(poly *p, int exp)

    # return new copy of lm(p), coefficient copied, next=NULL, p may be NULL

    poly *p_Head(poly *p, ring *r)

    # return TRUE, if leading monom of a divides leading monom of b
    # i.e., if there exists a expvector c > 0, s.t. b = a + c

    int p_DivisibleBy(poly *a, poly *b, ring *r)

    # like pDivisibleBy, except that it is assumed that a!=NULL, b!=NULL

    int p_LmDivisibleBy(poly *a, poly *b, ring *r)

    # least common multiplies for monomials only, result is written to m
    # p_Setm must be called on m afterwards.

    void pLcm(poly *a, poly *b, poly *m)

    # total degree of p

    long pTotaldegree(poly *p, ring *r)

    # iterate through the monomials of p

    poly *pNext(poly *p)

    # compare l and r

    int p_Cmp(poly *l, poly *r, ring *r)

    # compare exponent vectors only

    int p_ExpVectorEqual(poly *p, poly *m, ring *r)

    # TRUE if poly is constant

    int p_IsConstant(poly *, ring *)

    # like p_IsConstant but p must be !=NULL

    int p_LmIsConstant(poly *p, ring *)

    # TRUE if poly is unit

    int p_IsUnit(poly *p, ring *r)

    # substitute monomial for variable given by varidx in poly

    poly *pSubst(poly *p, int varidx, poly *value)

    # inverse of poly, if possible

    poly *pInvers(int n, poly *, intvec *)

    # gcd of f and g

    poly *singclap_gcd ( poly *f, poly *g )

    # resultant of f and g in x

    poly *singclap_resultant ( poly *f, poly *g , poly *x)

    # extended gcd of f and g

    int singclap_extgcd( poly *f, poly *g, poly *res, poly *pa, poly *pb )

    # full polynomial division (as opposed to monomial division)

    poly *singclap_pdivide ( poly *f, poly *g )

    # factorization

    ideal *singclap_factorize ( poly *f, intvec ** v , int with_exps)

    # TRUE if p is square free
    int singclap_isSqrFree(poly *p)

    # normal form calculation of p with respect to i, q is quotient
    # ring.

    poly *kNF(ideal *i, ideal *q, poly *p)

    # derive p with respect to i-th variable

    poly *pDiff(poly *p, int i)

    # return total degree of p

    int (*pLDeg)(poly *p, int *l, ring *r)

    # TRUE if p is a vector

    int pIsVector(poly *p)

    # return current component level

    int pGetComp(poly *p)




    # general number constructor

    number *n_Init(int n, ring *r)

    # general number destructor

    void n_Delete(number **n, ring *r)

    # return int representation of number n

    int nInt(number *n)

    # general number division

    number *n_Div(number *a, number *b, ring *r)

    # compare general number with zero

    int n_GreaterZero(number *a, ring *r)

    # TRUE if a == 0

    int n_IsZero(number *a, ring *r)

    # general number subtraction

    number *n_Sub(number *a, number *b, ring *r)

    # general number inversion

    number *nInvers(number *n)

    # rational number from int

    number *nlInit(int)

    # rational number from int

    number *nlRInit(int)

    # rational number from numerator and denominator

    number *nlInit2gmp(mpz_t n, mpz_t d)

    # rational number from numerator and denominator

    number *nlInit2(int i, int j)

    # copy a number

    number *nlCopy(number *)

    # get numerator

    number *nlGetNom(number *n, ring *r)

    # get denominator

    number *nlGetDenom(number *n, ring *r)




    # i-th algebraic number paraemeter

    number *naPar(int i)

    # algebraic number power

    void naPower(number *, int, number **)

    # algebraic number multiplication

    number *naMult(number *, number *)

    # algebraic number addition

    number *naAdd(number *, number *)

    # deep copy of algebraic number

    number *naCopy(number *)

    # algebraic number from int

    number *naInit(int)

    # algebraic number destructor

    void naDelete(number **, ring*)

    # algebraic number comparison with zero

    int naIsZero(number *)

    # algebraic number comparison with one

    int naIsOne(number *)

    # get current coefficent

    number *napGetCoeff(napoly *z)

    # get exponent of i-th variable

    int napGetExp(napoly *, int i)

    # loop through algebraic number

    napoly *napIter(napoly *)




    # number to integer handle

    long SR_TO_INT(number *)

    # mpz_t to integer handle

    long SR_HDL(mpz_t )




    # ideal constructor

    ideal *idInit(int size, int rank)

    # ideal destructor

    void id_Delete(ideal **, ring *)

    # mappinf from ideal i1 in r1 by i2 to r2

    ideal *fast_map(ideal *i1, ring *r1, ideal *i2, ring *r2)

    # lifting

    ideal *idLift(ideal *mod, ideal *submod, ideal **rest, int goodShape, int isSB, int divide)

    # number of generators of ideal

    int IDELEMS(ideal *i)

    # remove zero entries

    void idSkipZeroes (ideal *ide)

    # rank of free module for m

    long idRankFreeModule(ideal *m, ring *r)

    # buchberger's algorithm

    ideal *kStd(ideal *i, ideal *q, tHomog h, intvec *w)

    # slimgb algorithm

    ideal *t_rep_gb(ring *r,ideal *arg_I, int syz_comp, int F4_mode)

    # interreduction

    ideal *kInterRed(ideal *i, ideal *q)

    # TRUE if ideal is module

    int idIsModule(ideal *m, ring *r)

    # convert module to matrix

    matrix *idModule2Matrix(ideal *i)

    # convert matrix to module

    ideal * idMatrix2Module(matrix *m)

    # dense matrix constructor

    matrix *mpNew(int i, int j)

    # gauss-bareiss algorithm

    void smCallNewBareiss(ideal *, int, int, ideal *, intvec**)

    # get element at row i and column j

    poly *MATELEM(matrix *, int i, int j)

    # number columns of matrix

    int MATCOLS(matrix *)

    # number for rows of matrix

    int MATROWS(matrix *)
