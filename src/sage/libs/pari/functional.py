from sage.libs._pari.gen import pari

def allocatemem(silent=False):
    pari.allocatemem(silent)

def factorial(n): return P.factorial(n)

def Col(x): return pari(x).Col()
def List(x): return pari(x).List()
def Mat(x): return pari(x).Mat()
def Mod(x, y): return pari(x).Mod(y)
def Pol(self, v=-1): return pari(x).Pol(v)
def Polrev(self, v=-1): return pari(self).Polrev(v)
def Qfb(a, b, c, D=0): return pari(a).Qfb(b,c,D)
def Ser(x, v=-1): return pari(x).Ser(v)
def Set(x): return pari(x).Set()
def Str(self): return pari(self).Str()
def Strchr(x): return pari(x).Strchr()
def Strexpand(x): return pari(x).Strexpand()
def Strtex(x): return pari(x).Strtex()
def Vec(x): return pari(x).Vec()
def Vecsmall(x): return pari(x).Vecsmall()
def abs(self): return pari(self).abs()
def algdep(self, n, flag=0): return pari(self).algdep(n,flag)

def bezout(x, y): return pari(x).bezout(y)
def binary(x): return  pari(x).binary()
def bitand(x, y): return pari(x).bitand(y)
def bitneg(x,  n=-1): return pari(x).bitneg(n)
def bitnegimply(x, y): return pari(x).bitnegimply(y)
def bitor(x, y): return pari(x).bitor(y)
def bittest(x,  n): return pari(x).bitset(n)
def bitxor(x, y): return pari(x).bitxor(y)
def bnfinit(self,  flag=0): return pari(self).bnfinit(flag)
def bnfunit(self): return pari(self).bnfunit()
def ceil(x): return pari(x).ceil()
def centerlift(x, v=-1): return pari(x).centerlift(v)
def changevar(x, y): return pari(x).changevar(y)
def charpoly(self, var=-1, flag=0): return pari(self).charpoly(var,flag)
def component(x,  n): return pari(x).component(n)
def concat(self, y): return pari(self).concat(y)
def conj(x): return pari(x).conj()
def conjvec(x): return pari(x).conjvec()
def copy(self): return pari(self).copy()
def denominator(x): return pari(x).denominator()
def deriv(self, v=-1): return pari(self).deriv()
def disc(self): return pari(self).disc()
def divrem(x, y, var=-1): return pari(self).divrem()
def eint1(self,  n=0): return pari(self).eint1(n)
def elladd(self, z0, z1): return pari(self).ellad(z0,z1)
def ellak(self, n): return pari(self).ellak(n)
def ellan(self,  n): return pari(self).ellan(n)
def ellap(self, p): return pari(self).ellap(p)
def ellbil(self, z0, z1): return pari(self).ellbil(z0,z1)
def ellchangecurve(self, ch): return pari(self).ellchangecurve(ch)
def ellchangepoint(self, y): return pari(self).ellchangepoint(y)
def elleisnum(self,  k, flag=0): return pari(self).elleisnum(k,flag)
def elleta(self): return pari(self).elleta()
def ellglobalred(self): return pari(self).ellglobalred()
def ellheight(self, a, flag=0): return pari(self).ellheight(a,flag)
def ellheightmatrix(self, x): return pari(self).ellheightmatrix(x)
def ellinit(self, flag=0, precision=0): return pari(self).ellinit(flag,precision)
def ellisoncurve(self, x): return pari(self).ellisoncurve(x)
def ellj(self): return pari(self).ellj()
def elllocalred(self, p): return pari(self).elllocalred(p)
def elllseries(self, s, A=1,  prec=0): return pari(self).elllseries(a,A,prec)
def ellminimalmodel(self): return pari(self).ellminimalmodel()
def ellorder(self, x): return pari(self).ellorder(x)
def ellordinate(self, x): return pari(self).ellordinate(x)
def ellpointtoz(self, P): return pari(self).ellpointtoz(P)
def ellpow(self, z, n): return pari(self).ellpow(z,n)
def ellrootno(self, p=1): return pari(self).ellrootno(p)
def ellsigma(self, z, flag=0): return pari(self).ellsigma(z,flag)
def ellsub(self, z1, z2): return pari(self).ellsub(z1,z2)
def elltaniyama(self): return pari(self).elltaniyama()
def elltors(self, flag=0): return pari(self).elltors(flag)
def ellwp(self, z='z',  n=20,  flag=0): return pari(self).ellwp(z,n,flag)
def ellzeta(self, z): return pari(self).ellzeta(z)
def ellztopoint(self, z): return pari(self).ellztopoint(z)
def euler(): return pari.euler()
Euler = euler
def eval(self, x): return pari(self).eval(x)
def exp(self): return pari(self).exp()
def factor(self, limit=-1): return pari(self).factor(limit)
def factorpadic(self, p,  r=20,  flag=0): return pari(self).factorpadic(p,r,flag)
def finitefield_init(p,  n, var=-1): return P.finitefield_init(p,n,var)
def floor(x): return pari(x).floor()
def frac(x): return pari(x).frac()
def gamma(s, precision=0): return pari(s).gamma(precision)
def gcd(x, y): return pari(x).gcd(y)
def get_real_precision(self): return P.get_real_precision()
def get_series_precision(self): return P.get_series_precision()
def idealfactor(self, x): return pari(self).idealfactor(x)
def imag(x): return pari(x).imag()
def init_primes(M, silent=False): pari.init_primes(M,silent)
def intformal(self, y=-1): return pari(self).intformal(y)
def isprime(self, flag=0): return pari(self).isprime(flag)
def issquare(x, find_root=False): return pari(x).issquare(find_root)
def issquarefree(self): return pari(self).issquarefree()
def j(self): return pari(self).j()
def kronecker(self, y): return pari(self).kronecker(y)
def lcm(x, y): return pari(x).lcm(y)
def length(x): return pari(x).length()
def lex(x, y): return pari(x).lex(y)
def lift(x, v=-1): return pari(x).lift(v)
def lindep(self, flag=0): return pari(self).lindep(flag)
def list(self): return pari(self).list()
def list_str(self): return pari(self).list_str()
def listcreate(n): return pari.listcreate(n)
def listinsert(self, obj,  n): self.listinsert(obj, n)
def listput(self, obj,  n): return pari(self).listput(obj, n)
def log(self): return pari(self).log()
def mathnf(self, flag=0): return pari(self).mathnf(flag)
def matker(self,  flag=0): return pari(self).matker(flag)
def matkerint(self,  flag=0): return pari(self).matkerint(flag)
def matrix(m,  n, entries=None): return pari(pari).matrix(m,n,entries)
def mattranspose(self): return pari(self).mattranspose()
def ncols(self): return pari(self).ncols()
def nextprime(self): return pari(self).nextprime()
def nfbasis(self,  flag=0, p=0): return pari(self).nfbasis(flag, p)
def nfgenerator(self): return pari(self).nfgenerator()
def nfinit(self,  flag=0): return pari(self).nfinit(flag)
def norm(self): return pari(self).norm()
def nrows(self): return pari(self).nrows()
def prime(n): return pari.nth_prime(n)
def numerator(x): return pari(x).numerator()
def numtoperm(k,  n): return pari.numtoperm(k,n)
def omega(self): return pari(self).omega()
def order(self): return pari(self).order()
def padicappr(self, a): return pari(self).padicappr(a)
def padicprec(x, p): return pari(x).padicprec(p)
def pari_version(): return pari.pari_version()
def permtonum(x): return pari.permtonum(pari(x))
def pi(precision=0): return pari.pi(precision)
def polcoeff(self,  n, var=-1): return pari(self).polcoeff(n,var)
def polcompositum(self, pol2,  flag=0): return pari(self).polcompositum(pol2, flag)
def polcyclo(self,  n, v=-1): return pari.polcyclo(n, v)
def poldegree(self, var=-1): return pari(self).poldegree(var)
def poldisc(self, var=-1): return pari(self).poldisc(var)
def poldiscreduced(self): return pari(self).poldiscreduced()
def polgalois(self): return pari(self).polgalois()
def polhensellift(self, factors, p,  e): return pari(self).polhensellift(factors,p,e)
def polinterpolate(self, ya, x): return pari(self).polinterpolate(ya,x)
def polisirreducible(self): return pari(self).polisirreducible()
def pollead(self, v=-1): return pari(self).pollead(v)
def pollegendre(n, v=-1): return pari.pollegendre(n, v)
def polrecip(self): return pari(self).polrecip()
def polresultant(self, y, var=-1, flag=0): return pari(self).polresultant(y, var, flag)
def polroots(self, flag=0): return par(self).polroots(flag)
def polrootsmod(self, p, flag=0): return pari(self).polrootsmod(p,flag)
def polrootspadic(self, p, r=20): return pari(self).polrootspadic(p,r)
def polrootspadicfast(self, p, r=20): return pari(self).polrootspadicfast(p,r)
def polsturm(self, a, b): return pari(self).polsturm(a,b)
def polsubcyclo(n,  d, v=-1): return pari.polsubcyclo(n,d,v)
def polsylvestermatrix(self, g): return pari(self).polsylverstermatrix(g)
def polsym(self,  n): return pari(self).polsym(n)
def poltchebi(n, v=-1): return pari.poltchebi(n,v)
def polzagier(n,  m): return pari.polzagier(n,m)
def prime_list(n): return pari.prime_list(n)
def printtex(x): return pari(x).printtex()
def python(self, precision=0): return pari(self).python(precision)
def python_list(self): return pari(self).python_list()
def random(N): return pari.random(N)
def read(filename): pari.read(filename)
def real(x): return pari(x).real()
def reverse(self): return pari(self).reverse()
def rnfinit(self, poly): return pari(self).rnfinit(poly)
def round(x, estimate=False): return pari(x).round(estimate)
def serconvol(self, g): return pari(self).serconvol(g)
def serlaplace(self): return pari(self).serlaplace()
def serreverse(self): return pari(self).serreverse()
def set_real_precision(n): pari.set_real_precision(n)
def set_series_precision(n): pari.set_series_precision(n)
def shift(x,  n): return pari(x).shift(n)
def shiftmul(x,  n): return pari(x).shiftmul(n)
def sign(x): return pari(x).sign()
def simplify(x): return pari(x).simplify()
def sizebyte(x): return pari(x).sizebyte()
def sizedigit(x): return pari(x).sizedigit()
def sqrt(x, precision=0): return pari(x).sqrt(precision)
def subst(self, var, y): return pari(self).subst(var, y)
def substpol(self, y, z): return pari(self).substpol(y,z)
def taylor(self, v=-1): return pari(self).taylor(v)
def thue(self, rhs, ne): return pari(self).thue(rhs, ne)
def thueinit(self, flag=0): return pari(self).thueinit(flag)
def trace(self): return pari(self).trace()
def transpose(self): return pari(self).transpose()
def truncate(x, estimate=False): return pari(x).truncate(estimate)
def typ(self): return pari(self).type()
def valuation(x, p): return pari(x).valuation(p)
def variable(x): return pari(x).variable()
def vecmax(x): return pari(x).vecmax()
def vecmin(x): return pari(x).vecmin()
def vector(n, entries=None): return pari.vector(n, entries)
def xgcd(x, y): return pari(x).xgcd(y)
def zeta(s, precision=0): return pari(s).zeta(precision)
def znprimroot(self): return pari(self).znprimroot()

def variable(s): return pari(str(s))
