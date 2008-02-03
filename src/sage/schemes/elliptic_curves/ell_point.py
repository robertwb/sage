"""
Points on elliptic curves

EXAMPLES:
    sage: K = Qp(5)
    sage: E = EllipticCurve([K(1), K(1)])

    #sage: P = E([K(0), K(1), K(1)])
    #sage: P
    #(0 : 1 : 1)
    #sage: P + P
    #(4 + 3*5 + 3*5^2 + 3*5^3 + 3*5^4 + 3*5^5 + 3*5^6 + 3*5^7 + 3*5^8 + 3*5^9 + 3*5^10 + 3*5^11 + 3*5^12 + 3*5^13 + 3*5^14 + 3*5^15 + 3*5^16 + 3*5^17 + 3*5^18 + 3*5^19 + O(5^20) : 2 + 3*5^2 + 3*5^4 + 3*5^6 + 3*5^8 + 3*5^10 + 3*5^12 + 3*5^14 + 3*5^16 + 3*5^18 + O(5^20) : 1)

Arithmetic with a point over an extension of a finite field:
    sage: k.<a> = GF(5^2)
    sage: E = EllipticCurve(k,[1,0]); E
    Elliptic Curve defined by y^2  = x^3 + x over Finite Field in a of size 5^2
    sage: P = E([a,2*a+4])
    sage: 5*P
    (2*a + 3 : 2*a : 1)
    sage: P*5
    (2*a + 3 : 2*a : 1)
    sage: P + P + P + P + P
    (2*a + 3 : 2*a : 1)


    sage: F = Zmod(3)
    sage: E = EllipticCurve(F,[1,0]);
    sage: P = E([2,1])
    sage: import sys
    sage: n = sys.maxint
    sage: P*(n+1)-P*n == P
    True
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.structure.element import AdditiveGroupElement, RingElement

import sage.plot.all as plot

from sage.rings.padics.factory import Qp

import ell_generic
import sage.rings.all as rings
import sage.rings.arith as arith
import sage.misc.misc as misc

from sage.structure.sequence  import Sequence
from sage.schemes.generic.morphism import (SchemeMorphism_projective_coordinates_ring,
                                           SchemeMorphism_abelian_variety_coordinates_field,
                                           is_SchemeMorphism, SchemeMorphism_coordinates)

import sage.schemes.generic.scheme as scheme

oo = rings.infinity       # infinity

class EllipticCurvePoint(SchemeMorphism_projective_coordinates_ring):
    """
    A point on an elliptic curve.
    """
    def __cmp__(self, other):
        if isinstance(other, (int, long, rings.Integer)) and other == 0:
            if self.is_zero():
                return 0
            else:
                return -1
        return SchemePoint_projective_abelian_scheme.__cmp__(self, other)

class EllipticCurvePoint_field(AdditiveGroupElement): # SchemeMorphism_abelian_variety_coordinates_field):
    """
    A point on an elliptic curve over a field.  The point has coordinates
    in the base field.

    EXAMPLES:
        sage: E = EllipticCurve('37a')
        sage: E([0,0])
        (0 : 0 : 1)
        sage: E(0,0)               # brackets are optional
        (0 : 0 : 1)
        sage: E([GF(5)(0), 0])     # entries are coerced
        (0 : 0 : 1)

        sage: E(0.000, 0)
        (0 : 0 : 1)

        sage: E(1,0,0)
        Traceback (most recent call last):
        ...
        TypeError: coordinates [1, 0, 0] do not define a point on
        Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field

        sage: E = EllipticCurve([0,0,1,-1,0])
        sage: S = E(QQ); S
        Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field

    TESTS:
        sage: loads(S.dumps()) == S
        True
        sage: P = E(0,0); P
        (0 : 0 : 1)
        sage: loads(P.dumps()) == P
        True
        sage: T = 100*P
        sage: loads(T.dumps()) == T
        True

    Test pickling an elliptic curve that has known points on it.
        sage: e = EllipticCurve([0, 0, 1, -1, 0]); g = e.gens(); loads(dumps(e)) == e
        True
    """
    def __init__(self, curve, v, check=True):
        point_homset = curve.point_homset()
        AdditiveGroupElement.__init__(self, point_homset)
        if check:
            # mostly from  SchemeMorphism_projective_coordinates_field
            d = point_homset.codomain().ambient_space().ngens()
            if is_SchemeMorphism(v) or isinstance(v, EllipticCurvePoint_field):
                v = list(v)
            if v == 0:
                v = (0,1,0)
            if not isinstance(v,(list,tuple)):
                raise TypeError, \
                      "Argument v (= %s) must be a scheme point, list, or tuple."%str(v)
            if len(v) != d and len(v) != d-1:
                raise TypeError, "v (=%s) must have %s components"%(v, d)
            v = Sequence(v, point_homset.value_ring())
            if len(v) == d-1:     # very common special case
                v.append(1)

            n = len(v)
            all_zero = True
            for i in range(n):
                if v[n-1-i]:
                    all_zero = False
                    c = v[n-1-i]
                    if c == 1:
                        break
                    for j in range(n-i):
                        v[j] /= c
                    break
            if all_zero:
                raise ValueError, "%s does not define a valid point since all entries are 0"%repr(v)

            point_homset.codomain()._check_satisfies_equations(v)

        self._coords = v


    def _repr_(self):
        return self.codomain().ambient_space()._repr_generic_point(self._coords)

    def _latex_(self):
        return self.codomain().ambient_space()._latex_generic_point(self._coords)

    def __getitem__(self, n):
        return self._coords[n]

    def __list__(self):
        return list(self._coords)

    def __tuple__(self):
        return self._coords

    def __cmp__(self, other):
        if not isinstance(other, EllipticCurvePoint_field):
            try:
                other = self.codomain().ambient_space()(other)
            except TypeError:
                return -1
        return cmp(self._coords, other._coords)

    def scheme(self):
        return self.codomain()

    def domain(self):
        return self.parent().domain()

    def codomain(self):
        return self.parent().codomain()

    def order(self):
        """
        Return the order of this point on the elliptic curve.
        If the point has infinite order, returns 0.

        EXAMPLE:
            sage: E = EllipticCurve([0,0,1,-1,0])
            sage: P = E([0,0]); P
            (0 : 0 : 1)
            sage: P.order()
            +Infinity

            sage: E = EllipticCurve([0,1])
            sage: P = E([-1,0])
            sage: P.order()
            2
        """
        if self.is_zero():
            return rings.Integer(1)
        E = self.curve()
        try:
            n = int(E.pari_curve().ellorder([self[0], self[1]]))
            if n == 0:
                return oo
            return n
        except AttributeError, msg:
            raise NotImplementedError, "%s\nComputation of order of point."%msg

    def curve(self):
        """
        Return the curve that this point is a point on.

        EXAMPLES:
            sage: E = EllipticCurve('389a')
            sage: P = E([-1,1])
            sage: P.curve()
            Elliptic Curve defined by y^2 + y = x^3 + x^2 - 2*x over Rational Field
        """
        return self.scheme()

    def __nonzero__(self):
        """
        Return True if this is the zero point on the curve.

        EXAMPLES:
            sage: E = EllipticCurve('37a')
            sage: P = E(0); P
            (0 : 1 : 0)
            sage: P.is_zero()
            True
            sage: P = E.gens()[0]
            sage: P.is_zero()
            False
        """
        return bool(self[2])

    def is_finite_order(self):
        """
        Return True if this point has finite additive order as an element
        of the group of points on this curve.

        EXAMPLES:
            sage: E = EllipticCurve('11a')
            sage: P = E([5,5])
            sage: P.is_finite_order()
            True
            sage: Q = 5*P; Q
            (0 : 1 : 0)
            sage: Q.is_finite_order()
            True
            sage: E = EllipticCurve('37a')
            sage: P = E([0,0])
            sage: P.is_finite_order()
            False
        """
        return self[2] == 0 or self.order() != oo

    def plot(self, **args):
        """
        Plot this point on an elliptic curve.

        INPUT:
            **args -- all arguments get passed directly onto the point
              plotting function.

        EXAMPLES:
            sage: E = EllipticCurve('389a')
            sage: P = E([-1,1])
            sage: P.plot(pointsize=30, rgbcolor=(1,0,0))
        """
        if self.is_zero():
            return plot.text("$\\infty$", (-3,3), **args)

        else:
            return plot.point((self[0], self[1]), **args)

    def _add_(self, right):
        """
        Add self to right.

        EXAMPLES:
            sage: E = EllipticCurve('389a')
            sage: P = E([-1,1]); Q = E([0,0])
            sage: P + Q
            (1 : 0 : 1)
        """
        # Use Prop 7.1.7 of Cohen "A Course in Computational Algebraic Number Theory"
        if self.is_zero():
            return right
        if right.is_zero():
            return self
        E = self.curve()
        a1, a2, a3, a4, a6 = E.ainvs()
        x1, y1 = self[0], self[1]
        x2, y2 = right[0], right[1]
        if x1 == x2 and y1 == -y2 - a1*x2 - a3:
            return E(0) # point at infinity

        if x1 == x2 and y1 == y2:
            try:
                m = (3*x1*x1 + 2*a2*x1 + a4 - a1*y1) / (2*y1 + a1*x1 + a3)
            except ZeroDivisionError:
                raise ZeroDivisionError, "Inverse of %s does not exist"%(2*y1 + a1*x1 + a3)
        else:
            try:
                m = (y1-y2)/(x1-x2)
            except ZeroDivisionError:
                raise ZeroDivisionError, "Inverse of %s does not exist"%(x1-x2)

        x3 = -x1 - x2 - a2 + m*(m+a1)
        y3 = -y1 - a3 - a1*x3 + m*(x1-x3)
        return E.point([x3, y3, 1], check=False)

    def _sub_(self, right):
        """
        EXAMPLES:
            sage: E = EllipticCurve('389a')
            sage: P = E([-1,1]); Q = E([0,0])
            sage: P - Q
            (4 : 8 : 1)
            sage: (P - Q) + Q
            (-1 : 1 : 1)
            sage: P
            (-1 : 1 : 1)
        """
        return self + (-right)

    def __neg__(self):
        """
        Return the additive inverse of this point.

        EXAMPLES:
            sage: E = EllipticCurve('389a')
            sage: P = E([-1,1])
            sage: Q = -P; Q
            (-1 : -2 : 1)
            sage: Q + P
            (0 : 1 : 0)
        """
        if self.is_zero():
            return self
        E, x, y = self.curve(), self[0], self[1]
        return E.point([x, -y - E.a1()*x - E.a3(), 1], check=False)

    def height(self):
        """
        The Neron-Tate canonical height of the point.

        INPUT:
            self -- a point on a curve over QQ

        OUTPUT:
            the rational number 0 or a nonzero real field element

        EXAMPLES:
            sage: E = EllipticCurve('11a'); E
            Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field
            sage: P = E([5,5]); P
            (5 : 5 : 1)
            sage: P.height()
            0
            sage: Q = 5*P
            sage: Q.height()
            0

            sage: E = EllipticCurve('37a'); E
            Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
            sage: P = E([0,0])
            sage: P.height()
            0.0511114082399688
            sage: P.order()
            +Infinity
            sage: E.regulator()      # slightly random output
            0.051111408239968840

            sage: E = EllipticCurve('4602a1'); E
            Elliptic Curve defined by y^2 + x*y  = x^3 + x^2 - 37746035*x - 89296920339 over Rational Field
            sage: x = 77985922458974949246858229195945103471590
            sage: y = 19575260230015313702261379022151675961965157108920263594545223
            sage: d = 2254020761884782243
            sage: E([ x / d^2,  y / d^3 ]).height()
            86.7406561381275

            sage: E = EllipticCurve([17, -60, -120, 0, 0]); E
            Elliptic Curve defined by y^2 + 17*x*y - 120*y = x^3 - 60*x^2 over Rational Field
            sage: E([30, -90]).height()
            0
        """
        if self.is_finite_order():
            return rings.QQ(0)
        h = self.curve().pari_curve().ellheight([self[0], self[1]])
        return rings.RR(h)

    def xy(self):
        """
        Return the x and y coordinates of this point, as a 2-tuple.
        If this is point at infinity a ZeroDivisionError is raised.

        EXAMPLES:
            sage: E = EllipticCurve('389a')
            sage: P = E([-1,1])
            sage: P.xy()
            (-1, 1)
            sage: Q = E(0); Q
            (0 : 1 : 0)
            sage: Q.xy()
            Traceback (most recent call last):
            ...
            ZeroDivisionError: Rational division by zero
        """
        if self[2] == 1:
            return self[0], self[1]
        else:
            return self[0]/self[2], self[1]/self[2]



class EllipticCurvePoint_finite_field(EllipticCurvePoint_field):
    def order(self, disable_warning=False):
        """
        Return the order of this point on the elliptic curve.
        If the point has infinite order, returns 0.

        EXAMPLE:
            sage: E = EllipticCurve([0,0,1,-1,0])
            sage: P = E([0,0]); P
            (0 : 0 : 1)
            sage: P.order()
            +Infinity

            sage: E = EllipticCurve([0,1])
            sage: P = E([-1,0])
            sage: P.order()
            2
            sage: k.<a> = GF(5^5)
            sage: E = EllipticCurve(k,[2,4]); E
            Elliptic Curve defined by y^2  = x^3 + 2*x + 4 over Finite Field in a of size 5^5
            sage: P = E(3*a^4 + 3*a , 2*a + 1 )
            sage: P.order()
            3227

        ALGORITHM: uses PARI's \code{ellzppointorder} if base ring is prime
        or baby-step-giant-step algorithm as presented in

          Washington, Lawrence C.; 'Elliptic Curves: Number Theory and
          Cryptography', Boca Raton 2003
        """
        try:
            return self.__order
        except AttributeError:
            pass
        if self.is_zero():
            return rings.Integer(1)
        E = self.curve()
        K = E.base_ring()
        if K.is_prime_field():
            e = E._gp()
            self.__order = rings.Integer(e.ellzppointorder(list(self.xy())))
            return self.__order
        else:
            P = self
            E = P.curve()
            k = E.base_ring()
            q = k.order()

            if q < 256: # TODO: check this heuristc
                n = 1
                while not P.is_zero():
                    n += 1
                    P += self
                self.__order = rings.Integer(n)
                return self.__order

            # 1. Compute Q = (q+1)P
            Q = (q+1) * P

            # 2. Choos an integer m with m > q^{1/4}. Compute and store the
            # points jP for j = 0,1,2,...,m

            m = rings.Integer((q**rings.RR(0.25)).floor() + 1) #

            l = dict()
            X = E(0)
            for j in range(0,m+1):
                l[X] = j
                X = P + X

            # 3. Compute the points Q + k(2mP) for k = -m, -(m+1), ..., m
            # until there is a match Q + k(2mP) = +- jP with a point or its
            # negative on the list

            twomP = (2*m*P)
            for k in range(-m,m+1):
                W =  Q + k*twomP
                if W in l:
                    # 4a. Conclude that (q + 1 + 2mk - j)P = oo. Let M = q + 1 + 2mk - j
                    M = q + 1 + 2*m*k - l[W]
                    break
                elif -W in l:
                    # 4b. Conclude that (q + 1 + 2mk + j)P = oo. Let M = q + 1 + 2mk + j
                    M = q + 1 + 2*m*k + l[-W]
                    break

            # 5. Factor M. let p1,...,pr be the distinct prime factors of M.
            while True:
                N = M
                plist = [ p for p,n in M.factor()]
                for p in plist:
                    # 6. Compute (M/pi)P for i = 1...r. If (M/pi)P =
                    # oo for some i, replace M with M/pi and go back
                    # to step (4). If (M/pi)P != oo for all i then M
                    # is the order of the point P.
                    if (int(M/p) * P).is_zero():
                        M = M/p
                        break
                if N == M:
                    self.__order = rings.Integer(M)
                    return self.__order

    def _magma_init_(self):
        """
        Return a string representation of self that MAGMA can
        understand.
        """
        E = self.curve()._magma_().name()
        x,y = map(lambda x: x._magma_().name(), self.xy())
        return "%s![%s,%s]"%(E,x,y)
