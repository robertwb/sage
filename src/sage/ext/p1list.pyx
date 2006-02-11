r"""
List of Elements of $P^1(\Z/N\Z)$
"""

# TODO:
# Precompute table of xgcd's with N.  This would likely greatly speed
# things up, and probably be easy to compute!!!

from search import search

cimport arith
import arith
cdef arith.arith_int arith_int
cdef arith.arith_llong arith_llong
arith_int  = arith.arith_int()
arith_llong = arith.arith_llong()

ctypedef long long llong

include 'interrupt.pxi'

cdef int c_p1_normalize_int(int N, int u, int v,
                            int* uu, int* vv, int* ss,
                            int compute_s) except -1:
    """
    Do not compute s if compute_s == 0.
    """
    cdef int d, k, g, s, t, min_v, min_t, Ng, vNg
    if N == 1:
        uu[0] = 0
        vv[0] = 0
        ss[0] = 1
        return 0

    if N<=0 or N > 46340:
        raise OverflowError, "Modulus is too large (must be < 46340)"
        return -1

    u = u % N
    v = v % N
    if u<0: u = u + N
    if v<0: v = v + N
    if u == 0:
        uu[0] = 0
        if arith_int.c_gcd_int(v,N) == 1:
            vv[0] = 1
        else:
            vv[0] = 0
        ss[0] = v
        return 0

    g = arith_int.c_xgcd_int(u, N, &s, &t)
    s = s % N
    if s<0: s = s + N
    if arith_int.c_gcd_int(g, v) != 1:
        uu[0] = 0
        vv[0] = 0
        ss[0] = 0
        return 0

    # Now g = s*u + t*N, so s is a "pseudo-inverse" of u mod N
    # Adjust s modulo N/g so it is coprime to N.
    if g!=1:
        d = N/g
        while arith_int.c_gcd_int(s,N) != 1:
            s = (s+d) % N

    # Multiply [u,v] by s; then [s*u,s*v] = [g,s*v] (mod N)
    u = g
    v = (s*v) % N

    min_v = v; min_t = 1
    if g!=1:
        Ng = N/g
        vNg = (v*Ng) % N
        t = 1
        for k from 2 <= k <= g:
            v = (v + vNg) % N
            t = (t + Ng) % N
            if v<min_v and arith_int.c_gcd_int(t,N)==1:
                min_v = v; min_t = t
    v = min_v
    if u<0: u = u+N
    if v<0: v = v+N
    uu[0] = u
    vv[0] = v
    if compute_s:
        ss[0] = arith_int.c_inverse_mod_int(s*min_t, N);
    return 0

def p1_normalize_int(N, u, v):
    r"""
    p1_normalize_int(N, u, v):

    Computes the canonical representative of $\PP^1(\Z/N\Z)$ equivalent
    to $(u,v)$ along with a transforming scalar.

    INPUT:
        N -- an integer
        u -- an integer
        v -- an integer

    OUTPUT:
        If gcd(u,v,N) = 1, then returns
             uu -- an integer
             vv -- an integer
             ss -- an integer
             such that (ss*uu, ss*vv) is equivalent to (u,v) mod N
        and if gcd(u,v,N) != 1, returns
             0, 0, 0
    """
    cdef int uu, vv, ss
    c_p1_normalize_int(N, u%N, v%N, &uu, &vv, &ss, 1)
    return (uu,vv,ss)

def p1list_int(int N):
    r"""
    p1list_int(int N):

    Make a list of the normalized elements of $\PP^1(\Z/N\Z)$.
    """
    cdef int g, u, v, s, c, d
    cdef object lst

    if N==1: return [(0,0)]

    _sig_on
    lst = [(0,1), (1,0)]
    for c from 1 <= c < N:
        lst.append((1,c))
        g = arith_int.c_gcd_int(c,N)
        if g > 1:
            c_p1_normalize_int(N, c, 1, &u, &v, &s, 0)
            lst.append((u,v))
            if g==c:  # is a divisor
                for d from 2 <= d < N:
                    if arith_int.c_gcd_int(d,N)>1 and arith_int.c_gcd_int(d,c)==1:
                        c_p1_normalize_int(N, c, d, &u, &v, &s, 0)
                        lst.append((u,v))
    _sig_off
    # delete duplicate entries
    lst = list(set(lst))
    lst.sort()
    return lst


###############################################################
#
# The following is a version of the three functions
#
#      c_p1_normalize_int, p1_normalize_int, and p1list_int
#
# but the gcd's are done using GMP, so there are no overflow
# worries.   Also, the one multiplication is done using double
# precision.
#
################################################################

cdef int c_p1_normalize_llong(int N, int u, int v,
                              int* uu, int* vv, int* ss,
                              int compute_s) except -1:
    """
    Do not compute s if compute_s == 0.
    """
    cdef int d, k, g, s, t, min_v, min_t, Ng, vNg
    cdef llong ll_s, ll_t, ll_N
    if N == 1:
        uu[0] = 0
        vv[0] = 0
        ss[0] = 1
        return 0

    ll_N = <long> N

    #if N<=0 or N >= 2**31:
    #    raise OverflowError, "Modulus is too large (must be < 46340)"
    #    return -1

    u = u % N
    v = v % N
    if u<0: u = u + N
    if v<0: v = v + N
    if u == 0:
        uu[0] = 0
        if arith_int.c_gcd_int(v,N) == 1:
            vv[0] = 1
        else:
            vv[0] = 0
        ss[0] = v
        return 0

    #g = xgcd_int_llong(u, N, &s, &t)
    g = <int> arith_llong.c_xgcd_longlong(u, N, &ll_s, &ll_t)
    s = <int>(ll_s % ll_N)
    t = <int>(ll_t % ll_N)
    s = s % N
    if s<0: s = s + N
    if arith_int.c_gcd_int(g, v) != 1:
        uu[0] = 0
        vv[0] = 0
        ss[0] = 0
        return 0

    # Now g = s*u + t*N, so s is a "pseudo-inverse" of u mod N
    # Adjust s modulo N/g so it is coprime to N.
    if g!=1:
        d = N/g
        while arith_int.c_gcd_int(s,N) != 1:
            s = (s+d) % N

    # Multiply [u,v] by s; then [s*u,s*v] = [g,s*v] (mod N)
    u = g
    # v = (s*v) % N
    v = <int> ( ((<llong>s) * (<llong>v)) % ll_N )

    min_v = v; min_t = 1
    if g!=1:
        Ng = N/g
        vNg = <int> ((<llong>v * <llong> Ng) % ll_N)
        t = 1
        for k from 2 <= k <= g:
            v = (v + vNg) % N
            t = (t + Ng) % N
            if v<min_v and arith_int.c_gcd_int(t,N)==1:
                min_v = v; min_t = t
    v = min_v
    if u<0: u = u+N
    if v<0: v = v+N
    uu[0] = u
    vv[0] = v
    if compute_s:
        ss[0] = <int> (arith_llong.c_inverse_mod_longlong(s*min_t, N) % ll_N)
    return 0

def p1_normalize_llong(N, u, v):
    r"""
    p1_normalize_llong(N, u, v):

    Computes the canonical representative of $\PP^1(\Z/N\Z)$ equivalent
    to $(u,v)$ along with a transforming scalar.

    INPUT:
        N -- an integer
        u -- an integer
        v -- an integer
    OUTPUT:
        If gcd(u,v,N) = 1, then returns
             uu -- an integer
             vv -- an integer
             ss -- an integer
             such that (ss*uu, ss*vv) is equivalent to (u,v) mod N
        and if gcd(u,v,N) != 1, returns
             0, 0, 0
    """
    cdef int uu, vv, ss
    c_p1_normalize_llong(N, u%N, v%N, &uu, &vv, &ss, 1)
    return (uu,vv,ss)

def p1list_llong(int N):
    r"""
    p1list_llong(int N):

    Make a list of the normalized elements of $\PP^1(\Z/N\Z)$.
    """
    cdef int g, u, v, s, c, d
    if N==1: return [(0,0)]

    lst = [(0,1), (1,0)]
    _sig_on
    for c from 1 <= c < N:
        lst.append((1,c))
        g = arith_int.c_gcd_int(c,N)
        if g > 1:
            c_p1_normalize_llong(N, c, 1, &u, &v, &s, 0)
            lst.append((u,v))
            if g==c:  # is a divisor
                for d from 2 <= d < N:
                    if arith_int.c_gcd_int(d,N)>1 and arith_llong.c_gcd_longlong(d,c)==1:
                        c_p1_normalize_llong(N, c, d, &u, &v, &s, 0)
                        lst.append((u,v))
    _sig_off
    # delete duplicate entries
    lst = list(set(lst))
    lst.sort()
    return lst

def p1list(N):
    if N <= 46340:
        return p1list_int(N)
    if N <= 2147483647:
        return p1list_llong(N)
    else:
        raise OverflowError, "p1list not defined for such large N."

def p1_normalize(int N, int u, int v):
    if N <= 46340:
        return p1_normalize_int(N, u, v)
    if N <= 2147483647:
        return p1_normalize_llong(N, u, v)
    else:
        raise OverflowError

cdef class P1List:
    cdef int __N
    # Here we use a pointer to a function, so the if logic
    # for normalizing an element does not need to be used
    # every time the user calls the normalize function.
    cdef int (*__normalize)(int N, int u, int v,\
                            int* uu, int* vv, int* ss,
                            int compute_s) except -1
    cdef object __list

    def __init__(self, int N):
        self.__N = N
        if N <= 46340:
            self.__list = p1list_int(N)
            self.__normalize = c_p1_normalize_int
        elif N <= 2147483647:
            self.__list = p1list_llong(N)
            self.__normalize = c_p1_normalize_llong
        else:
            raise OverflowError, "p1list not defined for such large N."
        self.__list.sort()

    def __reduce__(self):
        import sage.modular.modsym.p1list
        return sage.modular.modsym.p1list._make_p1list, (self.__N, )

    def __getitem__(self, n):
        return self.__list[n]

    def __getslice__(self, n, m):
        return self.__list[n:m]

    def __len__(self):
        return len(self.__list)

    def __repr__(self):
        return "The projective line over the integers modulo %s"%self.__N

    def apply_I(self, i):
        cdef int u, v, uu, vv, ss
        u,v = self.__list[i]
        self.__normalize(self.__N, -u, v, &uu, &vv, &ss, 0)
        _, j = search(self.__list, (uu,vv))
        return j

    def apply_S(self, i):
        cdef int u, v, uu, vv, ss
        u,v = self.__list[i]
        self.__normalize(self.__N, -v, u, &uu, &vv, &ss, 0)
        _, j = search(self.__list, (uu,vv))
        return j

    def apply_T(self, i):
        cdef int u, v, uu, vv, ss
        u,v = self.__list[i]
        self.__normalize(self.__N, v, -u-v, &uu, &vv, &ss, 0)
        _, j = search(self.__list, (uu,vv))
        return j

    def index(self, int u, int v):
        r"""
        Returns the index of the class of $(u,v)$ in the fixed list of
        representatives of $\PP^1(\Z/N\Z)$.

        INPUT:
            u, v -- integers, with GCD(u,v,N)=1.

        OUTPUT:
            i -- the index of u, v, in the P^1 list.
        """
        cdef int uu, vv, ss
        self.__normalize(self.__N, u, v, &uu, &vv, &ss, 0)
        t, i = search(self.__list, (uu,vv))
        if t: return i
        return -1

    def index_of_normalized_pair(self, int u, int v):
        r"""
        Returns the index of the class of $(u,v)$ in the fixed list of
        representatives of $\PP^1(\Z/N\Z)$.

        INPUT:
            u, v -- integers, with GCD(u,v,N)=1 normalized so they lie in the list.
        OUTPUT:
            i -- the index of u, v, in the P^1 list.
        """
        t, i = search(self.__list, (u,v))
        if t: return i
        return -1

    def index_and_scalar(self, int u, int v):
        """
        Returns the index of the class of $(u,v)$ in the fixed list of
        representatives of $\PP^1(\Z/N\Z)$.

        INPUT:
            u, v -- integers, with GCD(u,v,N)=1.

        OUTPUT:
            i -- the index of u, v, in the P^1 list.
            s -- scalar that transforms normalized form to u,v
        """
        cdef int uu, vv, ss
        self.__normalize(self.__N, u, v, &uu, &vv, &ss, 1)
        t, i = search(self.__list, (uu,vv)), ss
        if t: return i
        return -1

    def list(self):
        return self.__list

    def normalize(self, int u, int v):
        cdef int uu, vv, ss
        self.__normalize(self.__N, u, v, &uu, &vv, &ss, 0)
        return (uu,vv)

    def normalize_with_scalar(self, int u, int v):
        """
        normalize_with_scalar(self, int u, int v)

        INPUT:
            u, v -- integers, with GCD(u,v,N)=1.

        OUTPUT:
            uu, vv -- integers of *normalized* rep
            ss -- scalar such that (ss*uu, ss*vv) = (u,v) mod N
        """
        cdef int uu, vv, ss
        self.__normalize(self.__N, u, v, &uu, &vv, &ss, 1)
        return (uu,vv,ss)

    def N(self):
        return self.__N


cdef class export:
    cdef int c_p1_normalize_int(self, int N, int u, int v,
                                int* uu, int* vv, int* ss,
                                int compute_s) except -1:
        return c_p1_normalize_int(N, u, v, uu, vv, ss, compute_s)

    cdef int c_p1_normalize_llong(self, int N, int u, int v,
                                  int* uu, int* vv, int* ss,
                                  int compute_s) except -1:
        return c_p1_normalize_llong(N, u, v, uu, vv, ss, compute_s)
