"""
Projective plane curves over a general ring

AUTHORS:

- William Stein (2005-11-13)

- David Joyner (2005-11-13)

- David Kohel (2006-01)
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.interfaces.all import singular
from sage.misc.all import add, sage_eval
from sage.rings.all import degree_lowest_rational_function, is_PrimeField

from sage.schemes.generic.projective_space import is_ProjectiveSpace

from curve import Curve_generic_projective

class ProjectiveSpaceCurve_generic(Curve_generic_projective):
    def _repr_type(self):
        return "Projective Space"

    def __init__(self, A, X):
        if not is_ProjectiveSpace(A):
            raise TypeError, "A (=%s) must be a projective space"%A
        Curve_generic_projective.__init__(self, A, X)
        d = self.dimension()
        if d != 1:
            raise ValueError, "defining equations (=%s) define a scheme of dimension %s != 1"%(X,d)

class ProjectiveCurve_generic(Curve_generic_projective):
    def __init__(self, A, f):
        if not (is_ProjectiveSpace(A) and A.dimension != 2):
            raise TypeError, "Argument A (= %s) must be a projective plane."%A
        Curve_generic_projective.__init__(self, A, [f])

    def _repr_type(self):
        return "Projective"

    def arithmetic_genus(self):
        r"""
        Return the arithmetic genus of this curve.

        This is the arithmetic genus `g_a(C)` as defined in
        Hartshorne. If the curve has degree `d` then this is simply
        `(d-1)(d-2)/2`. It need *not* equal the geometric genus
        (the genus of the normalization of the curve).

        EXAMPLE::

            sage: x,y,z = PolynomialRing(GF(5), 3, 'xyz').gens()
            sage: C = Curve(y^2*z^7 - x^9 - x*z^8); C
            Projective Curve over Finite Field of size 5 defined by -x^9 + y^2*z^7 - x*z^8
            sage: C.arithmetic_genus()
            28
            sage: C.genus()
            4
        """
        d = self.defining_polynomial().total_degree()
        return int((d-1)*(d-2)/2)

    def divisor_of_function(self, r):
        """
        Return the divisor of a function on a curve.

        INPUT: r is a rational function on X

        OUTPUT:


        -  ``list`` - The divisor of r represented as a list of
           coefficients and points. (TODO: This will change to a more
           structural output in the future.)


        EXAMPLES::

            sage: FF = FiniteField(5)
            sage: P2 = ProjectiveSpace(2, FF, names = ['x','y','z'])
            sage: R = P2.coordinate_ring()
            sage: x, y, z = R.gens()
            sage: f = y^2*z^7 - x^9 - x*z^8
            sage: C = Curve(f)
            sage: K = FractionField(R)
            sage: r = 1/x
            sage: C.divisor_of_function(r)     # todo: not implemented  !!!!
            [[-1, (0, 0, 1)]]
            sage: r = 1/x^3
            sage: C.divisor_of_function(r)     # todo: not implemented  !!!!
            [[-3, (0, 0, 1)]]
        """
        F = self.base_ring()
        f = self.defining_polynomial()
        x, y, z = f.parent().gens()
        pnts = self.rational_points()
        divf = []
        for P in pnts:
            if P[2] != F(0):
                # What is the '5' in this line and the 'r()' in the next???
                lcs = self.local_coordinates(P,5)
                ldg = degree_lowest_rational_function(r(lcs[0],lcs[1]),z)
                if ldg[0] != 0:
                    divf.append([ldg[0],P])
        return divf


    def local_coordinates(self, pt, n):
        r"""
        Return local coordinates to precision n at the given point.

            Behaviour is flaky - some choices of `n` are worst that
            others.


        INPUT:


        -  ``pt`` - an F-rational point on X which is not a
           point of ramification for the projection (x,y) - x.

        -  ``n`` - the number of terms desired


        OUTPUT: x = x0 + t y = y0 + power series in t

        EXAMPLES::

            sage: FF = FiniteField(5)
            sage: P2 = ProjectiveSpace(2, FF, names = ['x','y','z'])
            sage: x, y, z = P2.coordinate_ring().gens()
            sage: C = Curve(y^2*z^7-x^9-x*z^8)
            sage: pt = C([2,3,1])
            sage: C.local_coordinates(pt,9)     # todo: not implemented  !!!!
                  [2 + t, 3 + 3*t^2 + t^3 + 3*t^4 + 3*t^6 + 3*t^7 + t^8 + 2*t^9 + 3*t^11 + 3*t^12]
        """

        f = self.defining_polynomial()
        R = f.parent()
        F = self.base_ring()
        p = F.characteristic()
        x0 = F(pt[0])
        y0 = F(pt[1])
        astr = ["a"+str(i) for i in range(1,2*n)]
        x,y = R.gens()
        R0 = PolynomialRing(F,2*n+2,names = [str(x),str(y),"t"]+astr)
        vars0 = R0.gens()
        t = vars0[2]
        yt = y0*t**0 + add([vars0[i]*t**(i-2) for i in range(3,2*n+2)])
        xt = x0+t
        ft = f(xt,yt)
        S = singular
        S.eval('ring s = '+str(p)+','+str(R0.gens())+',lp;')
        S.eval('poly f = '+str(ft))
        cmd = 'matrix c = coeffs ('+str(ft)+',t)'
        S.eval(cmd)
        N = int(S.eval('size(c)'))
        b = ["c["+str(i)+",1]," for i in range(2,N/2-4)]
        b = ''.join(b)
        b = b[:len(b)-1] #to cut off the trailing comma
        cmd = 'ideal I = '+b
        S.eval(cmd)
        c = S.eval('slimgb(I)')
        d = c.split("=")
        d = d[1:]
        d[len(d)-1] += "\n"
        e = [x[:x.index("\n")] for x in d]
        vals = []
        for x in e:
            for y in vars0:
                if str(y) in x:
                    if len(x.replace(str(y),"")) != 0:
                        i = x.find("-")
                        if i>0:
                            vals.append([eval(x[1:i]),x[:i],F(eval(x[i+1:]))])
                        i = x.find("+")
                        if i>0:
                            vals.append([eval(x[1:i]),x[:i],-F(eval(x[i+1:]))])
                    else:
                        vals.append([eval(str(y)[1:]),str(y),F(0)])
        vals.sort()
        k = len(vals)
        v = [x0+t,y0+add([vals[i][2]*t**(i+1) for i in range(k)])]
        return v

    def plot(self, *args, **kwds):
        """
        Plot the real points of an affine patch of this projective
        plane curve.


        INPUT:


        -  ``self`` - an affine plane curve

        -  ``patch`` - (optional) the affine patch to be plotted; if not
           specified, the patch corresponding to the last projective
           coordinate being nonzero

        -  ``*args`` - optional tuples (variable, minimum, maximum) for
           plotting dimensions

        -  ``**kwds`` - optional keyword arguments passed on to
           ``implicit_plot``


        EXAMPLES:

        A cuspidal curve::

            sage: R.<x, y, z> = QQ[]
            sage: C = Curve(x^3 - y^2*z)
            sage: C.plot()

        The other affine patches of the same curve::

            sage: C.plot(patch=0)
            sage: C.plot(patch=1)

        An elliptic curve::

            sage: E = EllipticCurve('101a')
            sage: C = Curve(E)
            sage: C.plot()
            sage: C.plot(patch=0)
            sage: C.plot(patch=1)

        A hyperelliptic curve::

            sage: P.<x> = QQ[]
            sage: f = 4*x^5 - 30*x^3 + 45*x - 22
            sage: C = HyperellipticCurve(f)
            sage: C.plot()
            sage: C.plot(patch=0)
            sage: C.plot(patch=1)
        """
        # if user hasn't specified a favourite affine patch, take the
        # one avoiding "infinity", i.e. the one corresponding to the
        # last projective coordinate being nonzero
        patch = kwds.pop('patch', self.ngens() - 1)
        from constructor import Curve
        C = Curve(self.affine_patch(patch))
        return C.plot(*args, **kwds)


class ProjectiveCurve_finite_field(ProjectiveCurve_generic):
    def rational_points(self, algorithm="enum", sort=True):
        r"""
        Return the rational points on this curve computed via enumeration.


        INPUT:

        - ``algorithm`` (string, default: 'enum') -- the algorithm to
          use.  Currently this is ignored.

        - ``sort`` (boolean, default ``True``) -- whether the output
          points should be sorted.  If False, the order of the output
          is non-deterministic.

        OUTPUT:

        A list of all the rational points on the curve defined over
        its base field, possibly sorted.

        .. note::

           This is a slow Python-level implementation.


        EXAMPLES::

            sage: F = GF(5)
            sage: P2.<X,Y,Z> = ProjectiveSpace(F,2)
            sage: C = Curve(X^3+Y^3-Z^3)
            sage: C.rational_points()
            [(0 : 1 : 1), (1 : 0 : 1), (2 : 2 : 1), (3 : 4 : 1), (4 : 1 : 0), (4 : 3 : 1)]
            sage: C.rational_points(sort=False)
            [(4 : 1 : 0), (1 : 0 : 1), (0 : 1 : 1), (2 : 2 : 1), (4 : 3 : 1), (3 : 4 : 1)]

        ::

            sage: F = GF(1009)
            sage: P2.<X,Y,Z> = ProjectiveSpace(F,2)
            sage: C = Curve(X^5+12*X*Y*Z^3 + X^2*Y^3 - 13*Y^2*Z^3)
            sage: len(C.rational_points())
            1043

        ::

            sage: F = GF(2^6,'a')
            sage: P2.<X,Y,Z> = ProjectiveSpace(F,2)
            sage: C = Curve(X^5+11*X*Y*Z^3 + X^2*Y^3 - 13*Y^2*Z^3)
            sage: len(C.rational_points())
            104

        ::

            sage: R.<x,y,z> = GF(2)[]
            sage: f = x^3*y + y^3*z + x*z^3
            sage: C = Curve(f); pts = C.rational_points()
            sage: pts
            [(0 : 0 : 1), (0 : 1 : 0), (1 : 0 : 0)]

        """
        g = self.defining_polynomial()
        K = g.parent().base_ring()
        from sage.rings.polynomial.all import PolynomialRing
        R = PolynomialRing(K,'X')
        X = R.gen()
        one = K.one_element()
        zero = K.zero_element()

        points = []
        # Point with y = z = 0:
        try:
            points.append(self.point([one,zero,zero]))
        except TypeError:
            pass

        # Points with z = 0 and y = 1:
        for x in R(g((X,one,zero))).roots(multiplicities=False):
            points.append(self.point([x,one,zero]))

        # Points with z = 1:
        for y in K:
            for x in R(g((X,y,one))).roots(multiplicities=False):
                points.append(self.point([x,y,one]))

        if sort:
            points.sort()
        return points


class ProjectiveCurve_prime_finite_field(ProjectiveCurve_finite_field):
    def _points_via_singular(self, sort=True):
        r"""
        Return all rational points on this curve, computed using Singular's
        Brill-Noether implementation.

        INPUT:


        -  ``sort`` - bool (default: True), if True return the
           point list sorted. If False, returns the points in the order
           computed by Singular.


        EXAMPLE::

            sage: x, y, z = PolynomialRing(GF(5), 3, 'xyz').gens()
            sage: f = y^2*z^7 - x^9 - x*z^8
            sage: C = Curve(f); C
            Projective Curve over Finite Field of size 5 defined by -x^9 + y^2*z^7 - x*z^8
            sage: C._points_via_singular()
            [(0 : 0 : 1), (0 : 1 : 0), (2 : 2 : 1), (2 : 3 : 1), (3 : 1 : 1), (3 : 4 : 1)]
            sage: C._points_via_singular(sort=False)     #random
            [(0 : 1 : 0), (3 : 1 : 1), (3 : 4 : 1), (2 : 2 : 1), (0 : 0 : 1), (2 : 3 : 1)]


        .. note::

           The Brill-Noether package does not always work (i.e., the
           'bn' algorithm. When it fails a RuntimeError exception is
           raised.
        """
        f = self.defining_polynomial()._singular_()
        singular = f.parent()
        singular.lib('brnoeth')
        try:
            X1 = f.Adj_div()
        except (TypeError, RuntimeError), s:
            raise RuntimeError, str(s) + "\n\n ** Unable to use the Brill-Noether Singular package to compute all points (see above)."

        X2 = singular.NSplaces(1, X1)
        X3 = singular.extcurve(1, X2)
        R = X3[1][5]
        singular.set_ring(R)

        # We use sage_flattened_str_list since iterating through
        # the entire list through the sage/singular interface directly
        # would involve hundreds of calls to singular, and timing issues with
        # the expect interface could crop up.  Also, this is vastly
        # faster (and more robust).
        v = singular('POINTS').sage_flattened_str_list()
        pnts = [self(int(v[3*i]), int(v[3*i+1]), int(v[3*i+2])) for i in range(len(v)/3)]


        if sort:
            pnts.sort()
        return pnts

    def riemann_roch_basis(self, D):
        r"""
        Return a basis for the Riemann-Roch space corresponding to
        `D`.

        .. warning::

          This function calls a Singular function that
          appears to be very buggy and should not be trusted.

        This uses Singular's Brill-Noether implementation.

        INPUT:


        -  ``sort`` - bool (default: True), if True return the
           point list sorted. If False, returns the points in the order
           computed by Singular.


        EXAMPLE::

            sage: R.<x,y,z> = GF(2)[]
            sage: f = x^3*y + y^3*z + x*z^3
            sage: C = Curve(f); pts = C.rational_points()
            sage: D = C.divisor([ (4, pts[0]), (0,pts[1]), (4, pts[2]) ])
            sage: C.riemann_roch_basis(D)
            [x/y, 1, z/y, z^2/y^2, z/x, z^2/(x*y)]

        The following example illustrates that the Riemann-Roch space
        function in Singular doesn't *not* work correctly.

        ::

            sage: R.<x,y,z> = GF(5)[]
            sage: f = x^7 + y^7 + z^7
            sage: C = Curve(f); pts = C.rational_points()
            sage: D = C.divisor([ (3, pts[0]), (-1,pts[1]), (10, pts[5]) ])
            sage: C.riemann_roch_basis(D)    # output is random (!!!!)
            [x/(y + x), (z + y)/(y + x)]

        The answer has dimension 2 (confirmed via Magma). But it varies
        between 1 and quite large with Singular.
        """
        f = self.defining_polynomial()._singular_()
        singular = f.parent()
        singular.lib('brnoeth')
        try:
            X1 = f.Adj_div()
        except (TypeError, RuntimeError), s:
            raise RuntimeError, str(s) + "\n\n ** Unable to use the Brill-Noether Singular package to compute all points (see above)."

        X2 = singular.NSplaces(1, X1)
        X3 = singular.extcurve(1, X2)
        R = X3[1][5]
        singular.set_ring(R)

        # We use sage_flattened_str_list since iterating through
        # the entire list through the sage/singular interface directly
        # would involve hundreds of calls to singular, and timing issues with
        # the expect interface could crop up.  Also, this is vastly
        # faster (and more robust).
        v = singular('POINTS').sage_flattened_str_list()
        pnts = [self(int(v[3*i]), int(v[3*i+1]), int(v[3*i+2])) for i in range(len(v)/3)]
        Dsupport = D.support()
        Dcoeffs = []
        for x in pnts:
            Dcoeffs.append(D.coeff(x))
        Dstr = str(tuple(Dcoeffs))
        G = singular(','.join([str(x) for x in Dcoeffs]), type='intvec')
        T = X2[1][2]
        T.set_ring()
        LG = G.BrillNoether(X2)
        LG = [X.split(',\n') for X in LG.sage_structured_str_list()]
        x,y,z = self.ambient_space().coordinate_ring().gens()
        vars = {'x':x, 'y':y, 'z':z}
        V = [(sage_eval(a, vars)/sage_eval(b, vars)) for a, b in LG]
        return V

    def rational_points(self, algorithm="enum", sort=True):
        r"""
        INPUT:


        -  ``algorithm`` - string:

        -  ``'enum'`` - straightforward enumeration

        -  ``'bn'`` - via Singular's brnoeth package.


        EXAMPLE::

            sage: x, y, z = PolynomialRing(GF(5), 3, 'xyz').gens()
            sage: f = y^2*z^7 - x^9 - x*z^8
            sage: C = Curve(f); C
            Projective Curve over Finite Field of size 5 defined by -x^9 + y^2*z^7 - x*z^8
            sage: C.rational_points()
            [(0 : 0 : 1), (0 : 1 : 0), (2 : 2 : 1), (2 : 3 : 1), (3 : 1 : 1), (3 : 4 : 1)]
            sage: C = Curve(x - y + z)
            sage: C.rational_points()
            [(0 : 1 : 1), (1 : 1 : 0), (1 : 2 : 1), (2 : 3 : 1), (3 : 4 : 1), (4 : 0 : 1)]

        .. note::

           The Brill-Noether package does not always work (i.e., the
           'bn' algorithm. When it fails a RuntimeError exception is
           raised.
        """
        if algorithm == "enum":

            return ProjectiveCurve_finite_field.rational_points(self, algorithm="enum", sort=sort)

        elif algorithm == "bn":

            return self._points_via_singular(sort=sort)

        elif algorithm == "all":

            S_enum = self.rational_points(algorithm = "enum")
            S_bn = self.rational_points(algorithm = "bn")
            if S_enum != S_bn:
                raise RuntimeError, "Bug in rational_points -- different algorithms give different answers for curve %s!"%self
            return S_enum

        else:

            raise ValueError, "No algorithm '%s' known"%algorithm

def Hasse_bounds(q, genus=1):
    r"""
    Return the Hasse-Weil bounds for the cardinality of a nonsingular
    curve defined over `\GF{q}` of given ``genus``.

    INPUT:

    - ``q`` (int) -- a prime power

    - ``genus`` (int, default 1) -- a non-negative integer,

    OUTPUT:

    (tuple)  The Hasse bounds (lb,ub) for the cardinality of a curve of
    genus ``genus`` defined over `\GF{q}`.

    EXAMPLES::

        sage: Hasse_bounds(2)
        (1, 5)
        sage: Hasse_bounds(next_prime(10^30))
        (999999999999998000000000000058, 1000000000000002000000000000058)
    """
    if genus==1:
        rq = (4*q).isqrt()
    else:
        rq = (4*(genus**2)*q).isqrt()
    return (q+1-rq,q+1+rq)
