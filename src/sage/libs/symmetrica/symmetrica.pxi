cdef extern from 'symmetrica/macro.h':
    pass

cdef extern from 'symmetrica/def.h':
    ctypedef int INT
    ctypedef INT OBJECTKIND

    ctypedef struct vector:
        pass
    ctypedef struct bruch:
        pass
    ctypedef struct graph:
        pass
    ctypedef struct list:
        pass
    ctypedef struct longint:
        pass
    ctypedef struct matrix:
        pass
    ctypedef struct monom:
        pass
    ctypedef struct number:
        pass
    ctypedef struct partition:
        pass
    ctypedef struct permutation:
        pass
    ctypedef struct reihe:
        pass
    ctypedef struct skewpartition:
        pass
    ctypedef struct symchar:
        pass
    ctypedef struct tableaux:
        pass

    ctypedef union OBJECTSELF:
        INT ob_INT
        INT *ob_INTpointer
        char *ob_charpointer
        bruch *ob_bruch
        graph *ob_graph
        list *ob_list
        longint *ob_longint
        matrix *ob_matrix
        monom *ob_monom
        number *ob_number
        partition *ob_partition
        permutation *ob_permutation
        reihe *ob_reihe
        skewpartition *ob_skewpartition
        symchar *ob_symchar
        tableaux *ob_tableaux
        vector *ob_vector


    cdef enum:
        INFREELIST = -1
        EMPTY = 0
        INTEGER = 1
        VECTOR = 2
        PARTITION = 3
        FRACTION = 4
        BRUCH = 4
        PERMUTATION = 6
        SKEWPARTITION = 7
        TABLEAUX = 8
        POLYNOM = 9
        SCHUR = 10
        MATRIX = 11
        AUG_PART = 12
        HOM_SYM = 13
        HOMSYM = 13
        SCHUBERT = 14
        INTEGERVECTOR = 15
        INEGER_VECTOR = 15
        INT_VECTOR = 15
        INTVECTOR = 15
        KOSTKA = 16
        INTINT = 17
        SYMCHAR = 18
        WORD =19
        LIST =20 # 210688 */
        MONOM =21 #230688*/
        LONGINT =22 # 170888 */
        GEN_CHAR =23 # 280888  nur fuer test-zwecke */
        BINTREE =24 # 291288 */
        GRAPH =25 # 210889 */
        COMP =26 # 300889 */
        COMPOSITION =26 # 300889 */
        KRANZTYPUS =27 # 280390 */
        POW_SYM =28
        POWSYM =28
        MONOMIAL =29  # 090992 */
        BTREE =30
        KRANZ =31
        GRAL =32 # 200691 */
        GROUPALGEBRA =32 # 170693 */
        ELM_SYM =33  # 090992 */
        ELMSYM =33  # 090992 */
        FINITEFIELD = 35 # 250193 */
        FF = 35 # 250193 */
        REIHE = 36 # 090393 */
        CHARPARTITION = 37 # 130593 */ # internal use */
        CHAR_AUG_PART = 38 # 170593 */ # internal use */
        INTEGERMATRIX =40 # AK 141293 */
        CYCLOTOMIC = 41 # MD */
        CYCLOTOMIC = 41 # MD */
        MONOPOLY = 42 # MD */
        SQ_RADICAL = 43 # MD */
        BITVECTOR = 44
        LAURENT =45
        SUBSET =47 # AK 220997 */
        FASTPOLYNOM =211093
        EXPONENTPARTITION =240298
        SKEWTABLEAUX =20398
        PARTTABLEAUX =10398
        BARPERM =230695
        PERMVECTOR =180998
        PERM_VECTOR =180998
        PERMUTATIONVECTOR =180998
        PERMUTATION_VECTOR =180998
        INTEGERBRUCH =220998
        INTEGER_BRUCH =220998
        INTEGERFRACTION =220998
        INTEGER_FRACTION =220998
        HASHTABLE  =120199



    ctypedef struct loc:
        INT w2, w1, w0
        loc *nloc

    ctypedef struct longint:
        loc *floc
        signed char signum #-1,0,+1
        INT laenge



    ctypedef struct ganzdaten:
        INT basis, basislaenge, auspos, auslaenge, auszz

    ctypedef struct zahldaten:
        char ziffer[13]
        INT mehr
        INT ziffernzhal
        loc *fdez


    ctypedef struct obj:
        OBJECTKIND ob_kind
        OBJECTSELF ob_self

    ctypedef obj *OP

    ctypedef struct vector:
        OP v_length
        OP v_self

    ctypedef struct REIHE_variablen:
        INT index
        INT potenz
        REIHE_variablen *weiter

    ctypedef struct REIHE_mon:
        OP coeff
        REIHE_variablen *zeiger
        REIHE_mon *ref

    ctypedef struct REIHE_poly:
        INT grad
        REIHE_mon *uten
        REIHE_poly *rechts

    ctypedef struct reihe:
        INT exist
        INT reihenart
        INT z
        reihe *x, *y
        reihe *p
        INT (*eingabefkt)()
        char ope
        REIHE_poly *infozeig

    ctypedef reihe* REIHE_ZEIGER

    ctypedef struct list:
        OP l_self
        OP l_next

    ctypedef struct partition:
        OBJECTKIND pa_kind
        OP pa_self

    ctypedef struct permutation:
        OBJECTKIND p_kind
        OP p_self

    ctypedef struct monom:
        OP mo_self
        OP mo_koeff

    ctypedef struct bruch:
        OP b_oben
        OP b_uten
        INT b_info

    ctypedef struct matrix:
        OP m_length
        OP m_height
        OP m_self

    ctypedef struct skewpartition:
        OP spa_gross
        OP spa_klein

    ctypedef struct tableaux:
        OP t_umriss
        OP t_self

    ctypedef struct symchar:
        OP sy_werte
        OP sy_parlist
        OP sy_dimension

    ctypedef struct graph:
        OBJECTKIND gr_kind
        OP gr_self

    ctypedef struct CYCLO_DATA:
        OP index, deg, poly, autos

    ctypedef struct FIELD_DATA:
        OP index, deg, poly

    ctypedef union data:
        CYCLO_DATA *c_data
        FIELD_DATA *f_data
        OP o_data

    ctypedef struct number:
        OP n_self
        data n_data


    #MACROS
    #S_PA_I(OP a, INT i)
    OBJECTKIND s_o_k(OP a)
    void* c_o_k(OP a, OBJECTKIND k)


    #Integers
    void* m_i_i(INT n, OP a)
    void* M_I_I(INT n, OP a)
    INT S_I_I(OP a)

    #Fractions
    OP S_B_O(OP a)
    OP S_B_U(OP a)
    OP m_ou_b(OP o, OP u, OP d)

    #Vectors
    void* M_IL_V(INT length, OP a)
    void* m_il_v(INT n, OP a )
    void* m_i_i(INT n, OP a)

    INT s_v_li(OP a)
    OP s_v_i(OP a, INT i)

    #Partitions
    OP s_pa_l(OP a)
    INT s_pa_li(OP a)
    INT s_pa_ii(OP a, INT i)
    OP s_pa_i(OP a, INT i)
    OP S_PA_S(OP a)
    OP S_PA_I(OP a, INT )
    void* b_ks_pa(INT kind, OP b, OP a)


    #Skew Partitions
    INT b_gk_spa(OP gross, OP klein, OP result)
    INT m_gk_spa(OP gross, OP klein, OP result)
    OP s_spa_g(OP spa)
    OP s_spa_k(OP spa)

    #Permutations
    OP s_p_i(OP a, INT i)
    INT s_p_li(OP a)
    INT s_p_ii(OP a, INT i)
    void* m_il_p(INT n, OP a)


    #Barred Permutations


    #Lists
    OP s_l_s(OP a)
    OP S_L_S(OP a)
    OP s_l_n(OP a)
    INT lastp_list(OP l)
    INT empty_listp(OP l)

    #Matrices
    INT S_M_HI(OP a)
    INT S_M_LI(OP a)
    OP S_M_IJ(OP a, INT i, INT j)
    void* m_ilih_m(INT l, INT h, OP a)

    #Schur polynomials
    OP s_s_s(OP a)
    OP s_s_k(OP a)
    OP s_s_n(OP a)
    void* m_skn_s(OP part, OP koeff, OP next, OP result)
    void* b_skn_s(OP part, OP koeff, OP next, OP result)

    #Schubert polynomials
    OP s_sch_s(OP a)
    OP s_sch_k(OP a)
    OP s_sch_n(OP a)
    void* m_skn_sch(OP perm, OP koeff, OP next, OP result)
    void* b_skn_sch(OP perm, OP koeff, OP next, OP result)

    #Polynomials
    OP s_po_n(OP a)
    OP s_po_sl(OP a)
    OP s_po_k(OP a)
    OP s_po_s(OP a)
    void* m_skn_po(OP s, OP k, OP next, OP polynom)

    #Tableaux
    OP S_T_S(OP t)

    #########

    INT insert(OP a, OP b, INT (*eq)(), INT (*comp)())


    INT nullp_sqrad(OP a)
    OP S_PO_K(OP a)
    OP S_PO_S(OP a)
    OP S_L_N(OP a)
    OP S_N_S(OP a)
    INT einsp(OP A)

    #Empty Object
    int EMPTYP(OP obj)

    #Functions
    INT anfang()
    INT ende()
    OP callocobject()
    INT sscan(INT, OP a)
    INT scan(INT, OP a)
    INT freeall(OP a)
    INT freeself(OP a)
    INT sprint(char* t, OP a)
    INT sprint_integer(char* t, OP A)
    INT println(OP a)

    #factorial
    INT fakul(OP a, OP b)

##########################################
cdef object matrix_constructor
cdef object Integer
cdef object Tableau
cdef object SkewPartition, SkewPartition_class
cdef object Partition, Partition_class
cdef object Permutation_class
cdef object builtinlist
cdef object sqrt
cdef object Rational
cdef object QQ
cdef object ZZ
cdef object SymmetricFunctionAlgebra
cdef object PolynomialRing
cdef object SchubertPolynomialRing

cdef void late_import():
    global matrix_constructor, \
           Integer, \
           Tableau, \
           SkewPartition, \
           SkewPartition_class, \
           Partition, \
           Partition_class, \
           Permutation_class, \
           prod, \
           PolynomialRing, \
           Rational, \
           QQ, \
           ZZ, \
           SymmetricFunctionAlgebra, \
           sqrt, \
           builtinlist, \
           MPolynomialRing_generic, \
           SchubertPolynomialRing

    if matrix_constructor is not None:
        return

    import sage.matrix.constructor
    matrix_constructor = sage.matrix.constructor.matrix

    import sage.rings.integer
    Integer = sage.rings.integer.Integer

    import sage.combinat.tableau
    Tableau = sage.combinat.tableau.Tableau

    import sage.combinat.skew_partition
    SkewPartition = sage.combinat.skew_partition.SkewPartition
    SkewPartition_class = sage.combinat.skew_partition.SkewPartition_class

    import sage.combinat.partition
    Partition = sage.combinat.partition.Partition
    Partition_class = sage.combinat.partition.Partition_class

    import sage.combinat.permutation
    Permutation_class = sage.combinat.permutation.Permutation_class

    import sage.calculus.calculus
    sqrt = sage.calculus.calculus.Function_sqrt()

    import sage.misc.misc
    prod = sage.misc.misc.prod

    import sage.rings.polynomial.polynomial_ring_constructor
    PolynomialRing =  sage.rings.polynomial.polynomial_ring_constructor.PolynomialRing

    import sage.rings.all
    QQ = sage.rings.all.QQ
    Rational = sage.rings.all.Rational
    ZZ = sage.rings.all.ZZ

    #Symmetric Function Algebra
    import sage.combinat.sf.sfa
    SymmetricFunctionAlgebra = sage.combinat.sf.sfa.SymmetricFunctionAlgebra

    import __builtin__
    builtinlist = __builtin__.list

    import sage.rings.polynomial.multi_polynomial_ring
    MPolynomialRing_generic = sage.rings.polynomial.multi_polynomial_ring.MPolynomialRing_generic

    import sage.combinat.schubert_polynomial
    SchubertPolynomialRing = sage.combinat.schubert_polynomial.SchubertPolynomialRing

##########################################
cdef object _py(OP a):
    cdef OBJECTKIND objk
    objk = s_o_k(a)
    #print objk
    if objk == INTEGER or objk == LONGINT:
        return _py_integer(a)
    elif objk == PARTITION:
        return _py_partition(a)
    elif objk == PERMUTATION:
        return _py_permutation(a)
    elif objk == SKEWPARTITION:
        return _py_skew_partition(a)
    elif objk == FRACTION:
        return _py_fraction(a)
    elif objk == SQ_RADICAL:
        return _py_sq_radical(a)
    elif objk == MATRIX or objk == KRANZTYPUS:
        return _py_matrix(a)
    elif objk == SCHUR:
        return _py_schur(a)
    elif objk == HOMSYM:
        return _py_homsym(a)
    elif objk == POWSYM:
        return _py_powsym(a)
    elif objk == ELMSYM:
        return _py_elmsym(a)
    elif objk == MONOMIAL:
        return _py_monomial(a)
    elif objk == LIST:
        return _py_list(a)
    elif objk == VECTOR:
        return _py_vector(a)
    elif objk == TABLEAUX:
        return _py_tableau(a)
    elif objk == EMPTY:
        return None
    elif objk == POLYNOM:
        return _py_polynom(a)
    elif objk == SCHUBERT:
        return _py_schubert(a)
    else:
        #println(a)
        raise NotImplementedError, str(objk)

cdef void* _op(object a, OP result):
    late_import()
    if PyObject_TypeCheck(a, Integer):
        _op_integer(a, result)
    elif PyObject_TypeCheck(a, Partition_class):
        _op_partition(a, result)
    elif PyObject_TypeCheck(a, Rational):
        _op_fraction(a, result)
    else:
        raise TypeError, "cannot convert a (= %s) to OP"%a

##########
#Integers#
##########
cdef void* _op_integer(object x, OP a):
    #a.ob_kind = INTEGER
    #a.ob_self = <OBJECTSELF>x
    M_I_I(x, a)

cdef object _py_integer(OP a):
    late_import()

    return Integer(S_I_I(a))


###########
#Fractions#
###########
cdef object _py_fraction(OP a):
    return _py_integer(S_B_O(a))/_py_integer(S_B_U(a))

cdef void* _op_fraction(object f, OP a):
    cdef OP o = callocobject(), u = callocobject()
    _op_integer(f.numerator(), o)
    _op_integer(f.denominator(), u)
    m_ou_b(o, u, a)

#########
#Vectors#
#########
cdef object _py_vector(OP a):
    cdef INT i
    res = []
    for i from 0 <= i < s_v_li(a):
        res.append( _py(s_v_i(a, i)))
    return res

cdef void* _op_il_vector(object l, OP a):
    cdef INT length, i
    length = len(l)

    m_il_v(length, a)
    for i from 0 <= i < length:
        m_i_i(l[i], s_v_i(a, i))

#########
#Numbers#
#########
cdef object _py_sq_radical(OP a):
    late_import()

    cdef OP ptr
    ptr = S_N_S(a)

    res = 0
    if nullp_sqrad(a):
        return res

    while ptr != NULL:

        if einsp(S_PO_S(ptr)):
            res += _py(S_PO_K(ptr))
        else:
            res += _py(S_PO_K(ptr))*sqrt(_py(S_PO_S(ptr)))


        ptr = S_L_N(ptr);

    return res.radical_simplify()

############
#Partitions#
############
cdef void* _op_partition(object p, OP a):
    cdef int n, i, j

    if not EMPTYP(a):
        freeself(a)

    n = len(p)
    b_ks_pa(VECTOR, callocobject(), a)
    m_il_v(n, S_PA_S(a))

    j = 0
    for i from n > i >= 0:
        _op_integer(p[i], S_PA_I(a,j))
        j = j + 1

cdef object _py_partition(OP a):
    cdef INT n, i
    late_import()
    res = []
    n = s_pa_li(a)
    for i from n > i >=0:
        res.append(s_pa_ii(a, i))
    return Partition(res)

################
#Skew Partition#
################
cdef void* _op_skew_partition(object p, OP a):
    cdef OP gross, klein
    gross = callocobject()
    klein = callocobject()

    #print p[0], p[1]
    _op_partition(p[0], gross)
    _op_partition(p[1], klein)

    b_gk_spa(gross, klein, a)

cdef object _py_skew_partition(OP a):
    late_import()
    return SkewPartition( [ _py_partition(s_spa_g(a)), _py_partition(s_spa_k(a)) ] )

##############
#Permutations#
##############
cdef void* _op_permutation(object p, OP a):
    cdef int n, i, j

    if not EMPTYP(a):
        freeself(a)

    n = len(p)
    m_il_p(n, a)
    for i from 0 <= i < n:
        _op_integer(p[i], s_p_i(a,i))

cdef object _py_permutation(OP a):
    late_import()
    cdef INT n, i
    res = []
    n = s_p_li(a)
    for i from 0 <= i < n:
        res.append(s_p_ii(a, i))
    return Permutation_class(res)

#####################
#Barred Permutations#
#####################

#######
#Lists#
#######
cdef object _py_list(OP a):
    cdef OP x
    x = a
    res = []
    if S_L_S(a) == NULL:
        return []
    elif empty_listp(a):
        return []
    while x  != NULL:
        res.append(_py(s_l_s(x)))
        x = s_l_n(x)

    return res


#############
#Polynomials#
#############
cdef object _py_polynom(OP a):
    late_import()
    cdef int maxneeded = 0, i = 0
    cdef OP pointer = a

    if pointer == NULL:
        return 0


    #Find the maximum number of variables needed
    while pointer != NULL:
        l = _py(s_po_sl(pointer))
        if l > maxneeded:
            maxneeded = l
        pointer = s_po_n(pointer)

    pointer = a
    parent_ring = _py(s_po_k(pointer)).parent()
    if maxneeded == 1:
        P = PolynomialRing(parent_ring, 'x')
    else:
        P = PolynomialRing(parent_ring, maxneeded, 'x')
    d = {}
    while pointer != NULL:
        exps = tuple(_py_vector(s_po_s(pointer)))
        d[ exps ] = _py(s_po_k(pointer))
        pointer = s_po_n(pointer)

    return P(d)


cdef object _py_polynom_alphabet(OP a, object alphabet):
    late_import()
    cdef OP pointer = a

    if pointer == NULL:
        return 0

    parent_ring = _py(s_po_k(pointer)).parent()
    if isinstance(alphabet, (builtinlist, tuple)):
        l = len(alphabet)
    else:
        l = _py(s_po_sl(a))

    P = PolynomialRing(parent_ring, l, alphabet)
    x = P.gens()
    res = P(0)
    while pointer != NULL:
        exps = _py_vector(s_po_s(pointer))
        res += _py(s_po_k(pointer)) *prod([ x[i]**exps[i] for i in range(min(len(exps),l))])
        pointer = s_po_n(pointer)
    return res

cdef object _op_polynom(object d, OP res):
    late_import()

    poly_ring = d.parent()

    if not PY_TYPE_CHECK(poly_ring, MPolynomialRing_generic):
        raise TypeError, "you must pass a multivariate polynomial"
    base_ring = poly_ring.base_ring()

    if not ( base_ring == ZZ or base_ring == QQ):
        raise TypeError, "the base ring must be either ZZ or QQ"

    cdef OP c = callocobject(), v = callocobject()
    cdef OP pointer = res
    m = d.monomials()
    exp = d.exponents()
    cdef int n, i
    n = len(exp)

    for i from 0 <= i < n:
        _op_il_vector(exp[i], v)
        _op(d.monomial_coefficient(poly_ring(m[i])), c)
        if i != n-1:
            m_skn_po(v,c, callocobject(), pointer)
        else:
            m_skn_po(v,c, NULL, pointer)
        pointer = s_po_n(pointer)

    freeall(c)
    freeall(v)
    return None



#######################################
#Schur symmetric functions and friends#
#######################################
cdef object _py_schur(OP a):
    late_import()
    z_elt = _py_schur_general(a)
    if len(z_elt) == 0:
        return SymmetricFunctionAlgebra(ZZ, basis='s')(0)

    #Figure out the parent ring of a coefficient
    R = z_elt[ z_elt.keys()[0] ].parent()

    s = SymmetricFunctionAlgebra(R, basis='s')
    z = s(0)
    z._monomial_coefficients = z_elt
    return z

cdef void* _op_schur(object d, OP res):
    _op_schur_general(d, res)

cdef object _py_monomial(OP a): #Monomial symmetric functions
    late_import()
    z_elt = _py_schur_general(a)
    if len(z_elt) == 0:
        return SymmetricFunctionAlgebra(ZZ, basis='m')(0)

    R = z_elt[ z_elt.keys()[0] ].parent()

    m = SymmetricFunctionAlgebra(R, basis='m')
    z = m(0)
    z._monomial_coefficients = z_elt
    return z

cdef void* _op_monomial(object d, OP res): #Monomial symmetric functions
    cdef OP pointer = res
    _op_schur_general(d, res)
    while pointer != NULL:
        c_o_k(pointer, MONOMIAL)
        pointer = s_s_n(pointer)

cdef object _py_powsym(OP a):  #Power-sum symmetric functions
    late_import()
    z_elt = _py_schur_general(a)
    if len(z_elt) == 0:
        return SymmetricFunctionAlgebra(ZZ, basis='p')(0)

    R = z_elt[ z_elt.keys()[0] ].parent()

    p = SymmetricFunctionAlgebra(R, basis='p')
    z = p(0)
    z._monomial_coefficients = z_elt
    return z

cdef void* _op_powsym(object d, OP res): #Power-sum symmetric functions
    cdef OP pointer = res
    _op_schur_general(d, res)
    while pointer != NULL:
        c_o_k(pointer, POWSYM)
        pointer = s_s_n(pointer)


cdef object _py_elmsym(OP a): #Elementary symmetric functions
    late_import()
    z_elt = _py_schur_general(a)
    if len(z_elt) == 0:
        return SymmetricFunctionAlgebra(ZZ, basis='e')(0)

    R = z_elt[ z_elt.keys()[0] ].parent()

    e = SymmetricFunctionAlgebra(R, basis='e')
    z = e(0)
    z._monomial_coefficients = z_elt
    return z

cdef void* _op_elmsym(object d, OP res): #Elementary symmetric functions
    cdef OP pointer = res
    _op_schur_general(d, res)
    while pointer != NULL:
        c_o_k(pointer, ELMSYM)
        pointer = s_s_n(pointer)


cdef object _py_homsym(OP a): #Homogenous symmetric functions
    late_import()
    z_elt = _py_schur_general(a)
    if len(z_elt) == 0:
        return SymmetricFunctionAlgebra(ZZ, basis='h')(0)

    R = z_elt[ z_elt.keys()[0] ].parent()

    h = SymmetricFunctionAlgebra(R, basis='h')
    z = h(0)
    z._monomial_coefficients = z_elt
    return z

cdef void* _op_homsym(object d, OP res): #Homogenous symmetric functions
    cdef OP pointer = res
    _op_schur_general(d, res)
    while pointer != NULL:
        c_o_k(pointer, HOMSYM)
        pointer = s_s_n(pointer)


cdef object _py_schur_general(OP a):
    cdef OP pointer = a
    d = {}
    if a == NULL:
        return d
    while pointer != NULL:
        d[ _py_partition(s_s_s(pointer)) ] = _py(s_s_k(pointer))
        pointer = s_s_n(pointer)
    return d

cdef void* _op_schur_general(object d, OP res):
    if PyObject_TypeCheck(d, dict):
        _op_schur_general_dict(d, res)
    else:
        _op_schur_general_sf(d, res)

cdef void* _op_schur_general_sf(object f, OP res):
    late_import()
    base_ring = f.parent().base_ring()
    if not ( base_ring is QQ or base_ring is ZZ ):
        raise ValueError, "the base ring must be either ZZ or QQ"

    _op_schur_general_dict( f.monomial_coefficients(), res)

cdef void* _op_schur_general_dict(object d, OP res):
    late_import()

    cdef OP next
    cdef OP pointer = res
    cdef INT n, i


    keys = d.keys()
    n = len(keys)

    if n == 0:
        raise ValueError, "the dictionary must be nonempty"

    b_skn_s( callocobject(), callocobject(), NULL, res)
    _op_partition( keys[0], s_s_s(res))
    _op( d[keys[0]], s_s_k(res))


    for i from 0 < i < n:
        next = callocobject()

        b_skn_s( callocobject(), callocobject(), NULL, next)
        _op_partition( keys[i], s_s_s(next))
        _op( d[keys[i]], s_s_k(next))

        insert(next, res, NULL, NULL)



######################
#Schubert Polynomials#
######################
cdef void* _op_schubert_general(object d, OP res):
    if PyObject_TypeCheck(d, dict):
        _op_schubert_dict(d, res)
    else:
        _op_schubert_sp(d, res)

cdef void* _op_schubert_perm(object a, OP res):
    cdef OP caperm = callocobject()
    _op_permutation(a, caperm)
    m_perm_sch(caperm, res)
    freeall(caperm)

cdef void* _op_schubert_sp(object f, OP res):
    late_import()
    base_ring = f.parent().base_ring()
    if not ( base_ring is QQ or base_ring is ZZ ):
        raise ValueError, "the base ring must be either ZZ or QQ"

    _op_schubert_dict( f.monomial_coefficients(), res)

cdef void* _op_schubert_dict(object d, OP res):
    late_import()

    cdef OP next
    cdef OP pointer = res
    cdef INT n, i

    keys = d.keys()
    n = len(keys)

    if n == 0:
        raise ValueError, "the dictionary must be nonempty"

    b_skn_sch( callocobject(), callocobject(), NULL, res)
    _op_permutation( keys[0], s_sch_s(res))
    _op( d[keys[0]], s_sch_k(res))


    for i from 0 < i < n:
        next = callocobject()

        b_skn_sch( callocobject(), callocobject(), NULL, next)
        _op_permutation( keys[i], s_sch_s(next))
        _op( d[keys[i]], s_sch_k(next))

        insert(next, res, NULL, NULL)

cdef object _py_schubert(OP a):
    late_import()
    cdef OP pointer = a
    z_elt = {}

    if a == NULL:
        return SchubertPolynomialRing(ZZ)(0)

    while pointer != NULL:
        z_elt[ _py(s_s_s(pointer)).remove_extra_fixed_points() ] = _py(s_sch_k(pointer))
        pointer = s_sch_n(pointer)

    if len(z_elt) == 0:
        return SchubertPolynomialRing(ZZ)(0)

    R = z_elt[ z_elt.keys()[0] ].parent()
    X = SchubertPolynomialRing(R)
    z = X(0)
    z._monomial_coefficients = z_elt
    return z


##########
#Matrices#
##########
cdef object _py_matrix(OP a):

    late_import()

    cdef INT i,j,rows, cols
    rows = S_M_HI(a)
    cols = S_M_LI(a)

    res = []
    for i from 0 <= i < rows:
        row = []
        for j from 0 <= j < cols:
            row.append( _py(S_M_IJ(a,i,j)) )

        res.append(row)

    #return res
    if res == [] or res is None:
        return res
    else:
        return matrix_constructor(res)


cdef void* _op_matrix(object a, OP res):
    #FIXME: only constructs integer matrices

    cdef INT i,j,rows, cols

    rows = a.nrows()
    cols = a.ncols()

    m_ilih_m(rows, cols, res)

    for i from 0 <= i < rows:
        for j from 0 <= j < cols:
            _op_integer( a[(i,j)], S_M_IJ(res,i,j) )

##########
#Tableaux#
##########
cdef object _py_tableau(OP t):

    late_import()

    cdef INT i,j,rows, cols
    cdef OP a
    a = S_T_S(t)
    rows = S_M_HI(a)
    cols = S_M_LI(a)

    res = []
    for i from 0 <= i < rows:
        row = []
        for j from 0 <= j < cols:
            if s_o_k(S_M_IJ(a,i,j)) == EMPTY:
                break
            else:
                row.append( _py(S_M_IJ(a,i,j)) )

        res.append(row)

    #return res

    return Tableau(res)




def start():
    anfang()

def end():
    ende()
