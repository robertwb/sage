r"""
Elliptic curves over a general ring.

Elliptic curves are always represented by 'Weierstrass Models' with
five coefficients `[a_1,a_2,a_3,a_4,a_6]` in standard
notation. In Magma, 'Weierstrass Model' means a model with
a1=a2=a3=0, which is called 'Short Weierstrass Model' in Sage;
these only exist in characteristics other than 2 and 3.

EXAMPLES:

We construct an elliptic curve over an elaborate base ring::

    sage: p = 97; a=1; b=3
    sage: R, u = PolynomialRing(GF(p), 'u').objgen()
    sage: S, v = PolynomialRing(R, 'v').objgen()
    sage: T = S.fraction_field()
    sage: E = EllipticCurve(T, [a, b]); E
    Elliptic Curve defined by y^2  = x^3 + x + 3 over Fraction Field of Univariate Polynomial Ring in v over Univariate Polynomial Ring in u over Finite Field of size 97
    sage: latex(E)
    y^2  = x^3 + x + 3

AUTHORS:

- William Stein (2005): Initial version

- Robert Bradshaw et al....

- John Cremona (2008-01): isomorphisms, automorphisms and twists in all characteristics
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

import math

from sage.rings.all import PolynomialRing, polygen
import sage.groups.abelian_gps as groups
import sage.groups.generic as generic
import sage.plot.all as plot

import sage.rings.arith as arith
import sage.rings.all as rings
import sage.rings.number_field as number_field
from sage.rings.number_field.all import is_NumberField
from sage.rings.all import is_Infinite
import sage.misc.misc as misc
import sage.misc.latex as latex
import sage.modular.modform as modform
import sage.functions.transcendental as transcendental

from sage.categories.morphism import IdentityMorphism
from sage.categories.homset import Hom
from sage.rings.arith import lcm

# Schemes
import sage.schemes.generic.projective_space as projective_space
import sage.schemes.generic.homset as homset

import ell_point
import ell_torsion
import constructor
import formal_group
import weierstrass_morphism as wm
from constructor import EllipticCurve


factor = arith.factor
sqrt = math.sqrt
exp = math.exp
mul = misc.mul
next_prime = arith.next_prime

oo = rings.infinity       # infinity
O = rings.O         # big oh

import sage.schemes.plane_curves.projective_curve as plane_curve

def is_EllipticCurve(x):
    r"""
    Utility function to test if ``x`` is an instance of an Elliptic Curve class.

    EXAMPLES::

        sage: from sage.schemes.elliptic_curves.ell_generic import is_EllipticCurve
        sage: E = EllipticCurve([1,2,3/4,7,19])
        sage: is_EllipticCurve(E)
        True
        sage: is_EllipticCurve(0)
        False
    """
    return isinstance(x, EllipticCurve_generic)

class EllipticCurve_generic(plane_curve.ProjectiveCurve_generic):
    r"""
    Elliptic curve over a generic base ring.

    EXAMPLES::

        sage: E = EllipticCurve([1,2,3/4,7,19]); E
        Elliptic Curve defined by y^2 + x*y + 3/4*y = x^3 + 2*x^2 + 7*x + 19 over Rational Field
        sage: loads(E.dumps()) == E
        True
        sage: E = EllipticCurve([1,3])
        sage: P = E([-1,1,1])
        sage: -5*P
        (179051/80089 : -91814227/22665187 : 1)
    """
    def __init__(self, ainvs, extra=None):
        r"""
        Constructor from `a`-invariants (long or short Weierstrass coefficients).

        INPUT:

        - ``ainvs`` (list) -- either `[a_1,a_2,a_3,a_4,a_6]` or
          `[a_4,a_6]` (with `a_1=a_2=a_3=0` in the second case).

        .. note::

           See constructor.py for more variants.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,5]); E
            Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 4*x + 5 over Rational Field
            sage: E = EllipticCurve(GF(7),[1,2,3,4,5]); E
            Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 4*x + 5 over Finite Field of size 7

        Constructor from `[a_4,a_6]` sets `a_1=a_2=a_3=0`::

            sage: EllipticCurve([4,5]).ainvs()
            [0, 0, 0, 4, 5]

        The base ring need not be a field::

            sage: EllipticCurve(IntegerModRing(91),[1,2,3,4,5])
            Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 4*x + 5 over Ring of integers modulo 91
        """
        if extra != None:   # possibility of two arguments
            K, ainvs = ainvs, extra
        else:
            K = ainvs[0].parent()
        assert len(ainvs) == 2 or len(ainvs) == 5
        self.__base_ring = K
        ainvs = [K(x) for x in ainvs]
        if len(ainvs) == 2:
            ainvs = [K(0),K(0),K(0)] + ainvs
        self.__ainvs = ainvs
        if self.discriminant() == 0:
            raise ArithmeticError, \
                  "Invariants %s define a singular curve."%ainvs
        PP = projective_space.ProjectiveSpace(2, K, names='xyz');
        x, y, z = PP.coordinate_ring().gens()
        a1, a2, a3, a4, a6 = ainvs
        f = y**2*z + (a1*x + a3*z)*y*z \
            - (x**3 + a2*x**2*z + a4*x*z**2 + a6*z**3)
        plane_curve.ProjectiveCurve_generic.__init__(self, PP, f)
        # TODO: cleanup, are these two point classes redundant?
        if K.is_field():
            if is_NumberField(K):
                self._point_morphism_class = self._point_class = ell_point.EllipticCurvePoint_number_field
            else:
                self._point_morphism_class = self._point_class = ell_point.EllipticCurvePoint_field
        else:
            self._point_morphism_class = self._point_class = ell_point.EllipticCurvePoint

    def _defining_params_(self):
        r"""
        Internal function. Returns a tuple of the base ring of this
        elliptic curve and its `a`-invariants, from which it can be
        reconstructed.

        EXAMPLES::

            sage: E=EllipticCurve(QQ,[1,1])
            sage: E._defining_params_()
            (Rational Field, [0, 0, 0, 1, 1])
            sage: EllipticCurve(*E._defining_params_()) == E
            True
        """
        return (self.__base_ring, self.__ainvs)

    def _repr_(self):
        """
        String representation of elliptic curve.

        EXAMPLES::

            sage: E=EllipticCurve([1,2,3,4,5]); E._repr_()
            'Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 4*x + 5 over Rational Field'

        ::

            sage: R.<x> = QQ['x']
            sage: K.<a> = NumberField(x^3-17)
            sage: EllipticCurve([a^2-3, -2/3*a + 3])
            Elliptic Curve defined by y^2  = x^3 + (a^2-3)*x + (-2/3*a+3) over Number Field in a
            with defining polynomial x^3 - 17
        """
        #return "Elliptic Curve with a-invariants %s over %s"%(self.ainvs(), self.base_ring())
        b = self.ainvs()
        #return "y^2 + %s*x*y + %s*y = x^3 + %s*x^2 + %s*x + %s"%\
        #       (a[0], a[2], a[1], a[3], a[4])
        a = [z._coeff_repr() for z in b]
        s = "Elliptic Curve defined by "
        s += "y^2 "
        if a[0] == "-1":
            s += "- x*y "
        elif a[0] == '1':
            s += "+ x*y "
        elif b[0]:
            s += "+ %s*x*y "%a[0]
        if a[2] == "-1":
            s += "- y "
        elif a[2] == '1':
            s += "+ y "
        elif b[2]:
            s += "+ %s*y "%a[2]
        s += "= x^3 "
        if a[1] == "-1":
            s += "- x^2 "
        elif a[1] == '1':
            s += "+ x^2 "
        elif b[1]:
            s += "+ %s*x^2 "%a[1]
        if a[3] == "-1":
            s += "- x "
        elif a[3] == '1':
            s += "+ x "
        elif b[3]:
            s += "+ %s*x "%a[3]
        if a[4] == '-1':
            s += "- 1 "
        elif a[4] == '1':
            s += "+ 1 "
        elif b[4]:
            s += "+ %s "%a[4]
        s = s.replace("+ -","- ")
        s += "over %s"%self.base_ring()
        return s

    def _latex_(self):
        """
        Internal function. Returns a latex string for this elliptic curve.
        Users will normally use latex() instead.

        EXAMPLES::

            sage: E=EllipticCurve(QQ,[1,1])
            sage: E._latex_()
            'y^2 = x^3 + x + 1 '
            sage: latex(E)
            y^2 = x^3 + x + 1
        """
        b = self.ainvs()
        a = [z._latex_coeff_repr() for z in b]
        s = "y^2 "
        if a[0] == '-1':
            s += "- xy "
        elif a[0] == '1':
            s += "+ xy "
        elif b[0]:
            s += "+ %sxy "%a[0]
        if a[2] == '-1':
            s += "- y "
        elif a[2] == '1':
            s += "+ y "
        elif b[2]:
            s += "+ %sy "%a[2]
        s += "= x^3 "
        if a[1] == '-1':
            s += "- x^2 "
        elif a[1] == '1':
            s += "+ x^2 "
        elif b[1]:
            s += "+ %sx^2 "%a[1]
        if a[3] == '-1':
            s += "- x "
        elif a[3] == '1':
            s += "+ x "
        elif b[3]:
            s += "+ %sx "%a[3]
        if a[4] == '-1':
            s += "- 1 "
        elif a[4] == '1':
            s += "+ 1 "
        elif b[4]:
            s += "+ %s "%a[4]
        s = s.replace("+ -","- ")
        return s

    def _pari_init_(self):
        """
        Internal function. Returns a string to initialize this elliptic
        curve in the pari system.

        EXAMPLES::

            sage: E=EllipticCurve(QQ,[1,1])
            sage: E._pari_init_()
            'ellinit([0/1,0/1,0/1,1/1,1/1])'
        """
        return 'ellinit([%s])'%(','.join([x._pari_init_() for x in self.ainvs()]))

    def _magma_init_(self, magma):
        """
        Internal function. Returns a string to initialize this elliptic
        curve in the Magma subsystem.

        EXAMPLES::

            sage: E = EllipticCurve(QQ,[1,1])
            sage: E._magma_init_(magma)                          # optional - magma
            'EllipticCurve([_sage_ref...|0,0,0,1,1])'
            sage: E =  EllipticCurve(GF(41),[2,5])               # optional - magma
            sage: E._magma_init_(magma)                          # optional - magma
            'EllipticCurve([_sage_ref...|GF(41)!0,GF(41)!0,GF(41)!0,GF(41)!2,GF(41)!5])'
            sage: E = EllipticCurve(GF(25,'a'), [0,0,1,4,0])
            sage: magma(E)                                       # optional - magma
            Elliptic Curve defined by y^2 + y = x^3 + 4*x over GF(5^2)
            sage: magma(EllipticCurve([1/2,2/3,-4/5,6/7,8/9]))   # optional - magma
            Elliptic Curve defined by y^2 + 1/2*x*y - 4/5*y = x^3 + 2/3*x^2 + 6/7*x + 8/9 over Rational Field
            sage: R.<x> = Frac(QQ['x'])
            sage: magma(EllipticCurve([x,1+x]))                  # optional - magma
            Elliptic Curve defined by y^2 = x^3 + x*x + (x + 1) over Univariate rational function field over Rational Field
        """
        kmn = magma(self.base_ring())._ref()
        return 'EllipticCurve([%s|%s])'%(kmn,','.join([x._magma_init_(magma) for x in self.ainvs()]))


    def _symbolic_(self, SR):
        r"""
        Many elliptic curves can be converted into a symbolic expression
        using the ``symbolic_expression`` command.

        EXAMPLES: We find a torsion point on 11a.

        ::

            sage: E = EllipticCurve('11a')
            sage: E._symbolic_(SR)
            y^2 + y == x^3 - x^2 - 10*x - 20
            sage: E.torsion_subgroup().gens()
            ((5 : 5 : 1),)

        We find the corresponding symbolic equality::

            sage: eqn = symbolic_expression(E); eqn
            y^2 + y == x^3 - x^2 - 10*x - 20
            sage: print eqn
                                      2        3    2
                                     y  + y == x  - x  - 10 x - 20

        We verify that the given point is on the curve::

            sage: eqn(x=5,y=5)
            30 == 30
            sage: bool(eqn(x=5,y=5))
            True

        We create a single expression::

            sage: F = eqn.lhs() - eqn.rhs(); print F
                                      2        3    2
                                     y  + y - x  + x  + 10 x + 20
            sage: y = var('y')
            sage: print F.solve(y)
            [
                                  3      2
                        - sqrt(4 x  - 4 x  - 40 x - 79) - 1
                    y == -----------------------------------
                                         2,
                                 3      2
                         sqrt(4 x  - 4 x  - 40 x - 79) - 1
                     y == ---------------------------------
                                         2
            ]

        You can also solve for x in terms of y, but the result is
        horrendous. Continuing with the above example, we can explicitly
        find points over random fields by substituting in values for x::

            sage: v = F.solve(y)[0].rhs()
            sage: print v
                                            3      2
                                  - sqrt(4 x  - 4 x  - 40 x - 79) - 1
                                  -----------------------------------
                                                   2
            sage: v = v.function(x)
            sage: v(3)
            (-sqrt(127)*I - 1)/2
            sage: v(7)
            (-sqrt(817) - 1)/2
            sage: v(-7)
            (-sqrt(1367)*I - 1)/2
            sage: v(sqrt(2))
            (-sqrt(-32*sqrt(2) - 87) - 1)/2

        We can even do arithmetic with them, as follows::

            sage: E2 = E.change_ring(SR); E2
            Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Symbolic Ring
            sage: P = E2.point((3, v(3), 1), check=False)
            sage: P
            (3 : (-sqrt(127)*I - 1)/2 : 1)
            sage: P + P
            (-756/127 : (sqrt(127)*I + 1)/2 + 12507*I/(127*sqrt(127)) - 1 : 1)

        We can even throw in a transcendental::

            sage: w = E2.point((pi,v(pi),1), check=False); w
            (pi : (-sqrt(4*pi^3 - 4*pi^2 - 40*pi - 79) - 1)/2 : 1)
            sage: 2*w
            ((3*pi^2 - 2*pi - 10)^2/(4*pi^3 - 4*pi^2 - 40*pi - 79) - 2*pi + 1 : (sqrt(4*pi^3 - 4*pi^2 - 40*pi - 79) + 1)/2 - (3*pi^2 - 2*pi - 10)*(-(3*pi^2 - 2*pi - 10)^2/(4*pi^3 - 4*pi^2 - 40*pi - 79) + 3*pi - 1)/sqrt(4*pi^3 - 4*pi^2 - 40*pi - 79) - 1 : 1)
        """
        a = [SR(x) for x in self.a_invariants()]
        x, y = SR.var('x, y')
        return y**2 + a[0]*x*y + a[2]*y == x**3 + a[1]*x**2 + a[3]*x + a[4]

    def __cmp__(self, other):
        """
        Standard comparison function for elliptic curves, to allow sorting
        and equality testing.

        EXAMPLES::

            sage: E=EllipticCurve(QQ,[1,1])
            sage: F=EllipticCurve(QQ,[0,0,0,1,1])
            sage: E==F
            True
        """
        if not isinstance(other, EllipticCurve_generic):
            return -1
        t = cmp(self.base_ring(), other.base_ring())
        if t:
            return t
        return cmp(self.ainvs(), other.ainvs())

    def __contains__(self, P):
        """
        Returns True if and only if P is a point on the elliptic curve. P
        just has to be something that can be coerced to a point.

        EXAMPLES::

            sage: E = EllipticCurve([0, 0, 1, -1, 0])
            sage: (0,0) in E
            True
            sage: (1,3) in E
            False
            sage: E = EllipticCurve([GF(7)(0), 1])
            sage: [0,0] in E
            False
            sage: [0,8] in E
            True
            sage: P = E(0,8)
            sage: P
            (0 : 1 : 1)
            sage: P in E
            True
        """
        if not isinstance(P, ell_point.EllipticCurvePoint):
            try:
                P = self(P)
            except TypeError:
                return False
        if P.curve() == self:
            return True
        x, y, a = P[0], P[1], self.ainvs()
        return y**2 + a[0]*x*y + a[2]*y == x**3 + a[1]*x**2 + a[3]*x + a[4]

    def __call__(self, *args, **kwds):
        """
        EXAMPLES::

            sage: E = EllipticCurve([0, 0, 1, -1, 0])

        The point at infinity, which is the 0 element of the group::

            sage: E(0)
            (0 : 1 : 0)

        The origin is a point on our curve::

            sage: P = E([0,0])
            sage: P
            (0 : 0 : 1)

        The curve associated to a point::

            sage: P.curve()
            Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field

        Points can be specified by given a 2-tuple or 3-tuple

        ::

            sage: E([0,0])
            (0 : 0 : 1)
            sage: E([0,1,0])
            (0 : 1 : 0)

        Over a field, points are normalized so the 3rd entry (if non-zero)
        is 1::

            sage: E(105, -69, 125)
            (21/25 : -69/125 : 1)

        We create points on an elliptic curve over a prime finite field.

        ::

            sage: E = EllipticCurve([GF(7)(0), 1])
            sage: E([2,3])
            (2 : 3 : 1)
            sage: E([0,0])
            Traceback (most recent call last):
            ...
            TypeError: coordinates [0, 0, 1] do not define a point on Elliptic Curve defined by y^2 = x^3 + 1 over Finite Field of size 7

        We create a point on an elliptic curve over a number field.

        ::

            sage: x = polygen(RationalField())
            sage: K = NumberField(x**3 + x + 1, 'a'); a = K.gen()
            sage: E = EllipticCurve([a,a])
            sage: E
            Elliptic Curve defined by y^2  = x^3 + a*x + a over Number Field in a with defining polynomial x^3 + x + 1
            sage: E = EllipticCurve([K(1),1])
            sage: E
            Elliptic Curve defined by y^2 = x^3 + x + 1 over Number Field in a with defining polynomial x^3 + x + 1
            sage: P = E([a,0,1])
            sage: P
            (a : 0 : 1)
            sage: P+P
            (0 : 1 : 0)

        Another example involving p-adics::

            sage: E = EllipticCurve('37a1')
            sage: P = E([0,0]); P
            (0 : 0 : 1)
            sage: R = pAdicField(3,20)
            sage: Ep = E.base_extend(R); Ep
            Elliptic Curve defined by y^2 + (1+O(3^20))*y = x^3 + (2+2*3+2*3^2+2*3^3+2*3^4+2*3^5+2*3^6+2*3^7+2*3^8+2*3^9+2*3^10+2*3^11+2*3^12+2*3^13+2*3^14+2*3^15+2*3^16+2*3^17+2*3^18+2*3^19+O(3^20))*x over 3-adic Field with capped relative precision 20
            sage: Ep(P)
            (0 : 0 : 1 + O(3^20))

        Constructing points from the torsion subgroup (which is an abstract
        abelian group)::

            sage: E = EllipticCurve('14a1')
            sage: T = E.torsion_subgroup()
            sage: [E(t) for t in T]
            [(0 : 1 : 0),
            (9 : 23 : 1),
            (2 : 2 : 1),
            (1 : -1 : 1),
            (2 : -5 : 1),
            (9 : -33 : 1)]

        ::

            sage: E = EllipticCurve([0,0,0,-49,0])
            sage: T = E.torsion_subgroup()
            sage: [E(t) for t in T]
            [(0 : 1 : 0), (0 : 0 : 1), (7 : 0 : 1), (-7 : 0 : 1)]

        ::

            sage: E = EllipticCurve('37a1')
            sage: T = E.torsion_subgroup()
            sage: [E(t) for t in T]
            [(0 : 1 : 0)]
        """
        if len(args) == 1 and args[0] == 0:
            R = self.base_ring()
            return self.point([R(0),R(1),R(0)], check=False)
        P = args[0]
        if isinstance(P,groups.abelian_group_element.AbelianGroupElement) and isinstance(P.parent(),ell_torsion.EllipticCurveTorsionSubgroup):
            T = P.parent()
            return sum([zi*Ti for zi,Ti in zip(P.list(),T.gens())],T.curve()(0))
        if isinstance(args[0],
              (ell_point.EllipticCurvePoint_field, \
               ell_point.EllipticCurvePoint_number_field, \
               ell_point.EllipticCurvePoint)):
            # check if denominator of the point contains a factor of the
            # characteristic of the base ring. if so, coerce the point to
            # infinity.
            characteristic = self.base_ring().characteristic()
            if characteristic != 0 and isinstance(args[0][0], rings.Rational) and isinstance(args[0][1], rings.Rational):
                if rings.mod(args[0][0].denominator(),characteristic) == 0 or rings.mod(args[0][1].denominator(),characteristic) == 0:
                    args = self._reduce_point(args[0], characteristic)
                    args = tuple(args)
            else:
                args = tuple(args[0])

        return plane_curve.ProjectiveCurve_generic.__call__(self, *args, **kwds)

    def _reduce_point(self, R, p):
        r"""
        Reduces a point R on an ellipitc curve to the corresponding point on
        the elliptic curve reduced modulo p. Used to coerce points between
        curves when p is a factor of the denominator of one of the
        coordinates.

        This functionality is used internally in the \code{call} method for
        elliptic curves.

        INPUT:
            R -- a point on an elliptic curve
            p -- a prime

        OUTPUT:
            S -- the corresponding point of the elliptic curve containing R, but
                 reduced modulo p

        EXAMPLES:
        Suppose we have a point with large height on a rational elliptic curve
        whose denominator contains a factor of 11:
            sage: E = EllipticCurve([1,-1,0,94,9])
            sage: R = E([0,3]) + 5*E([8,31])
            sage: factor(R.xy()[0].denominator())
            2^2 * 11^2 * 1457253032371^2

        Since 11 is a factor of the denominator, this point corresponds to the
        point at infinity on the same curve but reduced modulo 11. The reduce
        function tells us this:
            sage: E11 = E.change_ring(GF(11))
            sage: S = E11._reduce_point(R, 11)
            sage: E11(S)
            (0 : 1 : 0)

        The 0 point reduces as expected:
            sage: E11._reduce_point(E(0), 11)
            (0 : 1 : 0)

        Note that one need not explicitly call
        \code{EllipticCurve._reduce_point}
        """
        if R.is_zero():
            return R.curve().change_ring(rings.GF(p))(0)
        x, y = R.xy()
        d = arith.LCM(x.denominator(), y.denominator())
        return R.curve().change_ring(rings.GF(p))([x*d, y*d, d])

    def is_x_coord(self, x):
        """
        Returns True if ``x`` is the `x`-coordinate of a point on this curve.

        .. note::

           See also ``lift_x()`` to find the point(s) with a given
           `x`-coordinate.  This function may be useful in cases where
           testing an element of the base field for being a square is
           faster than finding its square root.

        EXAMPLES::

            sage: E = EllipticCurve('37a'); E
            Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
            sage: E.is_x_coord(1)
            True
            sage: E.is_x_coord(2)
            True

        There are no rational points with x-coordinate 3::

            sage: E.is_x_coord(3)
            False

        However, there are such points in `E(\RR)`::

            sage: E.change_ring(RR).is_x_coord(3)
            True

        And of course it always works in `E(\CC)`::

            sage: E.change_ring(RR).is_x_coord(-3)
            False
            sage: E.change_ring(CC).is_x_coord(-3)
            True

        AUTHORS:

        - John Cremona (2008-08-07): adapted from lift_x()

        TEST::

            sage: E=EllipticCurve('5077a1')
            sage: [x for x in srange(-10,10) if E.is_x_coord (x)]
            [-3, -2, -1, 0, 1, 2, 3, 4, 8]

        ::

            sage: F=GF(32,'a')
            sage: E=EllipticCurve(F,[1,0,0,0,1])
            sage: set([P[0] for P in E.points() if P!=E(0)]) == set([x for x in F if E.is_x_coord(x)])
            True
        """
        K = self.base_ring()
        try:
            x = K(x)
        except TypeError:
            raise TypeError, 'x must be coercible into the base ring of the curve'
        a1, a2, a3, a4, a6 = self.ainvs()
        fx = ((x + a2) * x + a4) * x + a6
        if a1.is_zero() and a3.is_zero():
            return fx.is_square()
        b = (a1*x + a3)
        if K.characteristic() == 2:
            R = PolynomialRing(K, 'y')
            F = R([-fx,b,1])
            return len(F.roots())>0
        D = b*b + 4*fx
        return D.is_square()

    def lift_x(self, x, all=False):
        r"""
        Returns one or all points with given `x`-coordinate.

        INPUT:

        - ``x`` -- an element of the base ring of the curve.

        - ``all`` (bool, default False) -- if True, return a (possibly
          empty) list of all points; if False, return just one point,
          or raise a ValueError if there are none.

        .. note::

           See also ``is_x_coord()``.

        EXAMPLES::

            sage: E = EllipticCurve('37a'); E
            Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
            sage: E.lift_x(1)
            (1 : 0 : 1)
            sage: E.lift_x(2)
            (2 : 2 : 1)
            sage: E.lift_x(1/4, all=True)
            [(1/4 : -3/8 : 1), (1/4 : -5/8 : 1)]

        There are no rational points with `x`-coordinate 3::

            sage: E.lift_x(3)
            Traceback (most recent call last):
            ...
            ValueError: No point with x-coordinate 3 on Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field

        However, there are two such points in `E(\RR)`::

            sage: E.change_ring(RR).lift_x(3, all=True)
            [(3.00000000000000 : 4.42442890089805 : 1.00000000000000), (3.00000000000000 : -5.42442890089805 : 1.00000000000000)]

        And of course it always works in `E(\CC)`::

            sage: E.change_ring(RR).lift_x(.5, all=True)
            []
            sage: E.change_ring(CC).lift_x(.5)
            (0.500000000000000 : -0.500000000000000 + 0.353553390593274*I : 1.00000000000000)

        We can perform these operations over finite fields too::

            sage: E = E.change_ring(GF(17)); E
            Elliptic Curve defined by y^2 + y = x^3 + 16*x over Finite Field of size 17
            sage: E.lift_x(7)
            (7 : 11 : 1)
            sage: E.lift_x(3)
            Traceback (most recent call last):
            ...
            ValueError: No point with x-coordinate 3 on Elliptic Curve defined by y^2 + y = x^3 + 16*x over Finite Field of size 17

        Note that there is only one lift with `x`-coordinate 10 in
        `E(\GF{17})`::

            sage: E.lift_x(10, all=True)
            [(10 : 8 : 1)]

        We can lift over more exotic rings too::

            sage: E = EllipticCurve('37a');
            sage: E.lift_x(pAdicField(17, 5)(6))
            (6 + O(17^5) : 2 + 16*17 + 16*17^2 + 16*17^3 + 16*17^4 + O(17^5) : 1 + O(17^5))
            sage: K.<t> = PowerSeriesRing(QQ, 't', 5)
            sage: E.lift_x(1+t)
            (1 + t : 2*t - t^2 + 5*t^3 - 21*t^4 + O(t^5) : 1)
            sage: K.<a> = GF(16)
            sage: E = E.change_ring(K)
            sage: E.lift_x(a^3)
            (a^3 : a^3 + a : 1)

        AUTHOR:

        - Robert Bradshaw (2007-04-24)

        TEST::

            sage: E = EllipticCurve('37a').short_weierstrass_model().change_ring(GF(17))
            sage: E.lift_x(3, all=True)
            []
            sage: E.lift_x(7, all=True)
            [(7 : 3 : 1), (7 : 14 : 1)]
        """
        a1, a2, a3, a4, a6 = self.ainvs()
        f = ((x + a2) * x + a4) * x + a6
        K = self.base_ring()
        x += K(0)
        one = x.parent()(1)
        if a1.is_zero() and a3.is_zero():
            if f.is_square():
                if all:
                    ys = f.sqrt(all=True)
                    return [self.point([x, y, one], check=False) for y in ys]
                else:
                    return self.point([x, f.sqrt(), one], check=False)
        else:
            b = (a1*x + a3)
            D = b*b + 4*f
            if K.characteristic() == 2:
                R = PolynomialRing(K, 'y')
                F = R([-f,b,1])
                ys = F.roots(multiplicities=False)
                if all:
                    return [self.point([x, y, one], check=False) for y in ys]
                elif len(ys) > 0:
                    return self.point([x, ys[0], one], check=False)
            elif D.is_square():
                if all:
                    return [self.point([x, (-b+d)/2, one], check=False) for d in D.sqrt(all=True)]
                else:
                    return self.point([x, (-b+D.sqrt())/2, one], check=False)
        if all:
            return []
        else:
            raise ValueError, "No point with x-coordinate %s on %s"%(x, self)

    def _homset_class(self, *args, **kwds):
        """
        Internal function. Returns the (abstract) group of points on this
        elliptic curve over a ring.

        EXAMPLES::

            sage: E=EllipticCurve(GF(5),[1,1])
            sage: E._homset_class(GF(5^10,'a'),GF(5))
            Abelian group of points on Finite Field in a of size 5^10
        """
        return homset.SchemeHomsetModule_abelian_variety_coordinates_field(*args, **kwds)

    def __getitem__(self, n):
        """
        Placeholder for standard indexing function.

        EXAMPLES::

            sage: E=EllipticCurve(QQ,[1,1])
            sage: E[2]
            Traceback (most recent call last):
            ...
            NotImplementedError: not implemented.
        """
        raise NotImplementedError, "not implemented."

    def __is_over_RationalField(self):
        """
        Internal function. Returns true iff the base ring of this elliptic
        curve is the field of rational numbers.

        EXAMPLES::

            sage: E=EllipticCurve(QQ,[1,1])
            sage: E._EllipticCurve_generic__is_over_RationalField()
            True
            sage: E=EllipticCurve(GF(5),[1,1])
            sage: E._EllipticCurve_generic__is_over_RationalField()
            False
        """
        return isinstance(self.base_ring(), rings.RationalField)

    def change_ring(self, R):
        r"""
        Return the new elliptic curve defined by coercing the
        `a`-invariants of this elliptic curve into the ring `R`.

        INPUT:

        -  ``R`` - ring


        OUTPUT:

        An elliptic curve defined over ``R`` with the same `a`-invariants.

        EXAMPLES::

            sage: E = EllipticCurve([0, 0, 1, -1, 0])
            sage: E.change_ring(GF(3))
            Elliptic Curve defined by y^2 + y = x^3 + 2*x over Finite Field of size 3
        """
        return constructor.EllipticCurve(R, [R(a) for a in self.ainvs()])

    def is_on_curve(self, x, y):
        """
        Returns True if `(x,y)` is an affine point on this curve.

        INPUT:

        - ``x``, ``y`` - elements of the base ring of the curve.

        EXAMPLES::

            sage: E=EllipticCurve(QQ,[1,1])
            sage: E.is_on_curve(0,1)
            True
            sage: E.is_on_curve(1,1)
            False
        """
        a = self.ainvs()
        return y**2 +a[0]*x*y + a[2]*y == x**3 + a[1]*x**2 + a[3]*x + a[4]

    def a_invariants(self):
        """
        The `a`-invariants of this elliptic curve, as a list.

        OUTPUT:

        (list) - a (new) list of the 5 `a`-invariants.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,5])
            sage: E.a_invariants()
            [1, 2, 3, 4, 5]
            sage: E = EllipticCurve([0,1])
            sage: E
            Elliptic Curve defined by y^2 = x^3 + 1 over Rational Field
            sage: E.a_invariants()
            [0, 0, 0, 0, 1]
            sage: E = EllipticCurve([GF(7)(3),5])
            sage: E.a_invariants()
            [0, 0, 0, 3, 5]

        We check that a new list is returned::

            sage: E = EllipticCurve([1,0,0,0,1])
            sage: E.a_invariants()[0] = 100000000
            sage: E
            Elliptic Curve defined by y^2 + x*y = x^3 + 1 over Rational Field
        """
        return list(self.__ainvs)

    ainvs = a_invariants

    def a1(self):
        r"""
        Returns the `a_1` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,6])
            sage: E.a1()
            1
        """
        return self.__ainvs[0]

    def a2(self):
        r"""
        Returns the `a_2` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,6])
            sage: E.a2()
            2
        """
        return self.__ainvs[1]

    def a3(self):
        r"""
        Returns the `a_3` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,6])
            sage: E.a3()
            3
        """
        return self.__ainvs[2]

    def a4(self):
        r"""
        Returns the `a_4` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,6])
            sage: E.a4()
            4
        """
        return self.__ainvs[3]

    def a6(self):
        r"""
        Returns the `a_6` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,6])
            sage: E.a6()
            6
        """
        return self.__ainvs[4]

    def b_invariants(self):
        """
        Returns the `b`-invariants of this elliptic curve, as a tuple.

        OUTPUT:

        (tuple) - a 4-tuple of the `b`-invariants of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.b_invariants()
            (-4, -20, -79, -21)
            sage: E = EllipticCurve([-4,0])
            sage: E.b_invariants()
            (0, -8, 0, -16)

        ::

            sage: E = EllipticCurve([1,2,3,4,5])
            sage: E.b_invariants()
            (9, 11, 29, 35)
            sage: E.b2()
            9
            sage: E.b4()
            11
            sage: E.b6()
            29
            sage: E.b8()
            35

        ALGORITHM:

        These are simple functions of the `a`-invariants.

        AUTHORS:

        - William Stein (2005-04-25)
        """
        try:
            return self.__b_invariants
        except AttributeError:
            a1,a2,a3,a4,a6 = tuple(self.ainvs())
            self.__b_invariants = a1*a1 + 4*a2, \
                                  a1*a3 + 2*a4, \
                                  a3**2 + 4*a6, \
                                  a1**2 * a6 + 4*a2*a6 - a1*a3*a4 + a2*a3**2 - a4**2
            return self.__b_invariants

    def b2(self):
        r"""
        Returns the `b_2` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,5])
            sage: E.b2()
            9
        """
        try:
            return self.__b_invariants[0]
        except AttributeError:
            return self.b_invariants()[0]

    def b4(self):
        r"""
        Returns the `b_4` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,5])
            sage: E.b4()
            11
        """
        try:
            return self.__b_invariants[1]
        except AttributeError:
            return self.b_invariants()[1]

    def b6(self):
        r"""
        Returns the `b_6` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,5])
            sage: E.b6()
            29
        """
        try:
            return self.__b_invariants[2]
        except AttributeError:
            return self.b_invariants()[2]

    def b8(self):
        r"""
        Returns the `b_8` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,5])
            sage: E.b8()
            35
        """
        try:
            return self.__b_invariants[3]
        except AttributeError:
            return self.b_invariants()[3]

    def c_invariants(self):
        r"""
        Returns the `c`-invariants of this elliptic curve, as a tuple.

        OUTPUT:

        (tuple) - a 2-tuple of the `c`-invariants of the elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.c_invariants()
            (496, 20008)
            sage: E = EllipticCurve([-4,0])
            sage: E.c_invariants()
            (192, 0)

        ALGORITHM:

        These are simple functions of the `a`-invariants.

        AUTHORS:

        - William Stein (2005-04-25)
        """
        try:
            return self.__c_invariants
        except AttributeError:
            b2,b4,b6,b8 = self.b_invariants()
            self.__c_invariants = b2**2 - 24*b4,\
                                  -b2**3 + 36*b2*b4 - 216*b6    # note: c6 is wrong in Silverman, but right in Cremona
            return self.__c_invariants

    def c4(self):
        r"""
        Returns the `c_4` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.c4()
            496
        """
        try:
            return self.__c_invariants[0]
        except AttributeError:
            pass
        return self.c_invariants()[0]

    def c6(self):
        r"""
        Returns the `c_6` invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.c6()
            20008
        """
        try:
            return self.__c_invariants[1]
        except AttributeError:
            pass
        return self.c_invariants()[1]

    def discriminant(self):
        """
        Returns the discriminant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([0,0,1,-1,0])
            sage: E.discriminant()
            37
            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.discriminant()
            -161051

        ::

            sage: E = EllipticCurve([GF(7)(2),1])
            sage: E.discriminant()
            1
        """
        try:
            return self.__discriminant
        except AttributeError:
            b2, b4, b6, b8 = self.b_invariants()
            self.__discriminant = -b2**2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6
            return self.__discriminant

    def j_invariant(self):
        r"""
        Returns the `j`-invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([0,0,1,-1,0])
            sage: E.j_invariant()
            110592/37
            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.j_invariant()
            -122023936/161051
            sage: E = EllipticCurve([-4,0])
            sage: E.j_invariant()
            1728

        ::

            sage: E = EllipticCurve([GF(7)(2),1])
            sage: E.j_invariant()
            1
        """
        try:
            return self.__j_invariant
        except AttributeError:
            c4, _ = self.c_invariants()
            self.__j_invariant = c4**3 / self.discriminant()
            return self.__j_invariant


    def base_extend(self, R):
        r"""
        Returns a new curve with the same `a`-invariants but defined over a new ring.

        INPUT:

        - ``R`` -- either a ring into which the curve's `a`-invariants
          may be coerced, or a morphism which may be applied to them.

        OUTPUT:

        A new elliptic curve with the saem `a`-invariants, defined over the new ring.

        EXAMPLES::

            sage: E=EllipticCurve(GF(5),[1,1]); E
            Elliptic Curve defined by y^2 = x^3 + x + 1 over Finite Field of size 5
            sage: E1=E.base_extend(GF(125,'a')); E1
            Elliptic Curve defined by y^2 = x^3 + x + 1 over Finite Field in a of size 5^3
            sage: F2=GF(5^2,'a'); a=F2.gen()
            sage: F4=GF(5^4,'b'); b=F4.gen()
            sage: h=F2.hom([a.charpoly().roots(ring=F4,multiplicities=False)[0]],F4)
            sage: E=EllipticCurve(F2,[1,a]); E
            Elliptic Curve defined by y^2 = x^3 + x + a over Finite Field in a of size 5^2
            sage: E.base_extend(h)
            Elliptic Curve defined by y^2 = x^3 + x + (4*b^3+4*b^2+4*b+3) over Finite Field in b of size 5^4
        """
        return constructor.EllipticCurve([R(a) for a in self.a_invariants()])

    def base_ring(self):
        """
        Returns the base ring of the elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve(GF(49, 'a'), [3,5])
            sage: E.base_ring()
            Finite Field in a of size 7^2

        ::

            sage: E = EllipticCurve([1,1])
            sage: E.base_ring()
            Rational Field

        ::

            sage: E = EllipticCurve(ZZ, [3,5])
            sage: E.base_ring()
            Integer Ring
        """
        return self.__base_ring

    base_field = base_ring

    def gens(self):
        """
        Placeholder function to return generators of an elliptic curve.

        .. note::

           This functionality is implemented in certain derived
           classes, such as EllipticCurve_rational_field.

        EXAMPLES::

            sage: R.<a1,a2,a3,a4,a6>=QQ[]
            sage: E=EllipticCurve([a1,a2,a3,a4,a6])
            sage: E.gens()
            Traceback (most recent call last):
            ...
            NotImplementedError: not implemented.
            sage: E=EllipticCurve(QQ,[1,1])
            sage: E.gens()
            [(0 : 1 : 1)]
        """
        raise NotImplementedError, "not implemented."

    def gen(self, i):
        """
        Function returning the i'th generator of this elliptic curve.

        .. note::

           Relies on gens() being implemented.

        EXAMPLES::

            sage: R.<a1,a2,a3,a4,a6>=QQ[]
            sage: E=EllipticCurve([a1,a2,a3,a4,a6])
            sage: E.gen(0)
            Traceback (most recent call last):
            ...
            NotImplementedError: not implemented.
        """
        return self.gens()[i]


    # Twists: rewritten by John Cremona as follows:
    #
    # Quadratic twist allowed except when char=2, j=0
    # Quartic twist allowed only if j=1728!=0 (so char!=2,3)
    # Sextic  twist allowed only if j=0!=1728 (so char!=2,3)
    #
    # More complicated twists exist in theory for char=2,3 and
    # j=0=1728, but I have never worked them out or seen them used!
    #

    r"""
    Twists: rewritten by John Cremona as follows:

    The following twists are implemented:

    - Quadratic twist:  except when char=2 and `j=0`.
    - Quartic twist: only if `j=1728\not=0` (so not if char=2,3).
    - Sextic  twist: only if `j=0\not=1728` (so not if char=2,3).

    More complicated twists exist in theory for char=2,3 and
    j=0=1728, but are not implemented.
    """

    def quadratic_twist(self, D=None):
        """
        Return the quadratic twist of this curve by ``D``.

        INPUT:

        - ``D`` (default None) the twisting parameter (see below).

        In characteristics other than 2, `D` must be nonzero, and the twist is
        isomorphic to self after adjoining `\sqrt(D)` to the base.

        In characteristic 2, `D` is arbitrary, and the twist is isomorphic
        to self after adjoining a root of `x^2+x+D` to the base.

        In characteristic 2 when `j=0`, this is not implemented.

        If the base field `F` is finite, `D` need not be specified, and
        the curve returned is the unique curve (up to isomorphism)
        defined over `F` isomorphic to the original curve over the
        quadratic extension of `F` but not over `F` itself.  Over infinte
        fields, an error is raised if `D` is not given.

        EXAMPLES::

            sage: E = EllipticCurve([GF(1103)(1), 0, 0, 107, 340]); E
            Elliptic Curve defined by y^2 + x*y  = x^3 + 107*x + 340 over Finite Field of size 1103
            sage: F=E.quadratic_twist(-1); F
            Elliptic Curve defined by y^2  = x^3 + 1102*x^2 + 609*x + 300 over Finite Field of size 1103
            sage: E.is_isomorphic(F)
            False
            sage: E.is_isomorphic(F,GF(1103^2,'a'))
            True

        A characteristic 2 example::

            sage: E=EllipticCurve(GF(2),[1,0,1,1,1])
            sage: E1=E.quadratic_twist(1)
            sage: E.is_isomorphic(E1)
            False
            sage: E.is_isomorphic(E1,GF(4,'a'))
            True

        Over finite fields, the twisting parameter may be omitted::

            sage: k.<a> = GF(2^10)
            sage: E = EllipticCurve(k,[a^2,a,1,a+1,1])
            sage: Et = E.quadratic_twist()
            sage: Et # random (only determined up to isomorphism)
            Elliptic Curve defined by y^2 + x*y  = x^3 + (a^7+a^4+a^3+a^2+a+1)*x^2 + (a^8+a^6+a^4+1) over Finite Field in a of size 2^10
            sage: E.is_isomorphic(Et)
            False
            sage: E.j_invariant()==Et.j_invariant()
            True

            sage: p=next_prime(10^10)
            sage: k = GF(p)
            sage: E = EllipticCurve(k,[1,2,3,4,5])
            sage: Et = E.quadratic_twist()
            sage: Et # random (only determined up to isomorphism)
            Elliptic Curve defined by y^2  = x^3 + 7860088097*x^2 + 9495240877*x + 3048660957 over Finite Field of size 10000000019
            sage: E.is_isomorphic(Et)
            False
            sage: k2 = GF(p^2,'a')
            sage: E.change_ring(k2).is_isomorphic(Et.change_ring(k2))
            True
        """
        K=self.base_ring()
        char=K.characteristic()

        if D is None:
            if K.is_finite():
                x = polygen(K)
                if char==2:
                    # We find D such that x^2+x+D is irreducible. If the
                    # degree is odd we can take D=1; otherwise it suffices to
                    # consider odd powers of a generator.
                    D = K(1)
                    if K.degree()%2==0:
                        D = K.gen()
                        a = D**2
                        while len((x**2+x+D).roots())>0:
                            D *= a
                else:
                    # We could take a multiplicative generator but
                    # that might be expensive to compute; otherwise
                    # half the elements will do
                    D = K.random_element()
                    while len((x**2-D).roots())>0:
                        D = K.random_element()
            else:
                raise ValueError, "twisting parameter D must be specified over infinite fields."
        else:
            try:
                D=K(D)
            except ValueError:
                raise ValueError, "twisting parameter D must be in the base field."

            if char!=2 and D.is_zero():
                raise ValueError, "twisting parameter D must be nonzero when characteristic is not 2"

        if char!=2:
            b2,b4,b6,b8=self.b_invariants()
            # E is isomorphic to  [0,b2,0,8*b4,16*b6]
            return EllipticCurve(K,[0,b2*D,0,8*b4*D**2,16*b6*D**3])

        # now char==2
        if self.j_invariant() !=0: # iff a1!=0
            a1,a2,a3,a4,a6=self.ainvs()
            E0=self.change_weierstrass_model(a1,a3/a1,0,(a1**2*a4+a3**2)/a1**3)
            # which has the form = [1,A2,0,0,A6]
            assert E0.a1()==K(1)
            assert E0.a3()==K(0)
            assert E0.a4()==K(0)
            return EllipticCurve(K,[1,E0.a2()+D,0,0,E0.a6()])
        else:
            raise ValueError, "Quadratic twist not implemented in char 2 when j=0"

    def quartic_twist(self, D):
        r"""
        Return the quartic twist of this curve by `D`.

        INPUT:

        - ``D`` (must be nonzero) -- the twisting parameter..

        .. note::

           The characteristic must not be 2 or 3, and the `j`-invariant must be 1728.

        EXAMPLES::

            sage: E=EllipticCurve_from_j(GF(13)(1728)); E
            Elliptic Curve defined by y^2  = x^3 + x over Finite Field of size 13
            sage: E1=E.quartic_twist(2); E1
            Elliptic Curve defined by y^2  = x^3 + 5*x over Finite Field of size 13
            sage: E.is_isomorphic(E1)
            False
            sage: E.is_isomorphic(E1,GF(13^2,'a'))
            False
            sage: E.is_isomorphic(E1,GF(13^4,'a'))
            True
        """
        K=self.base_ring()
        char=K.characteristic()
        D=K(D)

        if char==2 or char==3:
            raise ValueError, "Quartic twist not defined in chars 2,3"

        if self.j_invariant() !=K(1728):
            raise ValueError, "Quartic twist not defined when j!=1728"

        if D.is_zero():
            raise ValueError, "quartic twist requires a nonzero argument"

        c4,c6=self.c_invariants()
        # E is isomorphic to  [0,0,0,-27*c4,0]
        assert c6==0
        return EllipticCurve(K,[0,0,0,-27*c4*D,0])

    def sextic_twist(self, D):
        r"""
        Return the quartic twist of this curve by `D`.

        INPUT:

        - ``D`` (must be nonzero) -- the twisting parameter..

        .. note::

           The characteristic must not be 2 or 3, and the `j`-invariant must be 0.

        EXAMPLES::

            sage: E=EllipticCurve_from_j(GF(13)(0)); E
            Elliptic Curve defined by y^2 = x^3 + 1 over Finite Field of size 13
            sage: E1=E.sextic_twist(2); E1
            Elliptic Curve defined by y^2 = x^3 + 11 over Finite Field of size 13
            sage: E.is_isomorphic(E1)
            False
            sage: E.is_isomorphic(E1,GF(13^2,'a'))
            False
            sage: E.is_isomorphic(E1,GF(13^4,'a'))
            False
            sage: E.is_isomorphic(E1,GF(13^6,'a'))
            True
        """
        K=self.base_ring()
        char=K.characteristic()
        D=K(D)

        if char==2 or char==3:
            raise ValueError, "Sextic twist not defined in chars 2,3"

        if self.j_invariant() !=K(0):
            raise ValueError, "Sextic twist not defined when j!=0"

        if D.is_zero():
            raise ValueError, "Sextic twist requires a nonzero argument"

        c4,c6=self.c_invariants()
        # E is isomorphic to  [0,0,0,0,-54*c6]
        assert c4==0
        return EllipticCurve(K,[0,0,0,0,-54*c6*D])

    def is_quadratic_twist(self, other):
        r"""
        Determine whether this curve is a quadratic twist of another.

        INPUT:

        - ``other`` -- an elliptic curves with the same base field as self.

        OUTPUT:

        Either 0, if the curves are not quadratic twists, or `D` if
        ``other`` is ``self.quadratic_twist(D)`` (up to isomorphism).
        If ``self`` and ``other`` are isomorphic, returns 1.

        .. note::

           Not fully implemented in characteristic 2, or in
           characteristic 3 when both `j`-invariants are 0.

        EXAMPLES::

            sage: E = EllipticCurve('11a1')
            sage: Et = E.quadratic_twist(-24)
            sage: E.is_quadratic_twist(Et)
            -6

            sage: E1=EllipticCurve([0,0,1,0,0])
            sage: E1.j_invariant()
            0
            sage: E2=EllipticCurve([0,0,0,0,2])
            sage: E1.is_quadratic_twist(E2)
            2

        ::

            sage: E1=EllipticCurve([0,0,0,1,0])
            sage: E1.j_invariant()
            1728
            sage: E2=EllipticCurve([0,0,0,2,0])
            sage: E1.is_quadratic_twist(E2)
            0
            sage: E2=EllipticCurve([0,0,0,25,0])
            sage: E1.is_quadratic_twist(E2)
            5

        ::

            sage: F = GF(101)
            sage: E1 = EllipticCurve(F,[4,7])
            sage: E2 = E1.quadratic_twist()
            sage: D = E1.is_quadratic_twist(E2); D!=0
            True
            sage: F = GF(101)
            sage: E1 = EllipticCurve(F,[4,7])
            sage: E2 = E1.quadratic_twist()
            sage: D = E1.is_quadratic_twist(E2)
            sage: E1.quadratic_twist(D).is_isomorphic(E2)
            True
            sage: E1.is_isomorphic(E2)
            False
            sage: F2 = GF(101^2,'a')
            sage: E1.change_ring(F2).is_isomorphic(E2.change_ring(F2))
            True

        A characteristic 3 example::

            sage: F = GF(3^5,'a')
            sage: E1 = EllipticCurve_from_j(F(1))
            sage: E2 = E1.quadratic_twist(-1)
            sage: D = E1.is_quadratic_twist(E2); D!=0
            True
            sage: E1.quadratic_twist(D).is_isomorphic(E2)
            True

        ::

            sage: E1 = EllipticCurve_from_j(F(0))
            sage: E2 = E1.quadratic_twist()
            sage: D = E1.is_quadratic_twist(E2); D
            1
            sage: E1.is_isomorphic(E2)
            True

        """
        from sage.schemes.elliptic_curves.ell_generic import is_EllipticCurve
        E = self
        F = other
        if not is_EllipticCurve(E) or not is_EllipticCurve(F):
            raise ValueError, "arguments are not elliptic curves"
        K = E.base_ring()
        zero = K.zero_element()
        if not K == F.base_ring():
            return zero
        j=E.j_invariant()
        if  j != F.j_invariant():
            return zero

        if E.is_isomorphic(F):
            return K.one_element()

        char=K.characteristic()

        if char==2:
            raise NotImplementedError, "not implemented in characteristic 2"
        elif char==3:
            if j==0:
                raise NotImplementedError, "not implemented in characteristic 3 for curves of j-invariant 0"
            D = E.b2()/F.b2()

        else:
            # now char!=2,3:
            c4E,c6E = E.c_invariants()
            c4F,c6F = F.c_invariants()

            if j==0:
                um = c6E/c6F
                x=polygen(K)
                ulist=(x**3-um).roots(multiplicities=False)
                if len(ulist)==0:
                    D = zero
                else:
                    D = ulist[0]
            elif j==1728:
                um=c4E/c4F
                x=polygen(K)
                ulist=(x**2-um).roots(multiplicities=False)
                if len(ulist)==0:
                    D = zero
                else:
                    D = ulist[0]
            else:
                D = (c6E*c4F)/(c6F*c4E)

        # Normalization of output:

        if D.is_zero():
            return D

        if K is rings.QQ:
            D = D.squarefree_part()

        assert E.quadratic_twist(D).is_isomorphic(F)

        return D

    def is_quartic_twist(self, other):
        r"""
        Determine whether this curve is a quartic twist of another.

        INPUT:

        - ``other`` -- an elliptic curves with the same base field as self.

        OUTPUT:

        Either 0, if the curves are not quartic twists, or `D` if
        ``other`` is ``self.quartic_twist(D)`` (up to isomorphism).
        If ``self`` and ``other`` are isomorphic, returns 1.

        .. note::

           Not fully implemented in characteristics 2 or 3.

        EXAMPLES::

            sage: E = EllipticCurve_from_j(GF(13)(1728))
            sage: E1 = E.quartic_twist(2)
            sage: D = E.is_quartic_twist(E1); D!=0
            True
            sage: E.quartic_twist(D).is_isomorphic(E1)
            True

        ::

            sage: E = EllipticCurve_from_j(1728)
            sage: E1 = E.quartic_twist(12345)
            sage: D = E.is_quartic_twist(E1); D
            15999120
            sage: (D/12345).is_perfect_power(4)
            True
        """
        from sage.schemes.elliptic_curves.ell_generic import is_EllipticCurve
        E = self
        F = other
        if not is_EllipticCurve(E) or not is_EllipticCurve(F):
            raise ValueError, "arguments are not elliptic curves"
        K = E.base_ring()
        zero = K.zero_element()
        if not K == F.base_ring():
            return zero
        j=E.j_invariant()
        if  j != F.j_invariant() or j!=K(1728):
            return zero

        if E.is_isomorphic(F):
            return K.one_element()

        char=K.characteristic()

        if char==2:
            raise NotImplementedError, "not implemented in characteristic 2"
        elif char==3:
            raise NotImplementedError, "not implemented in characteristic 3"
        else:
            # now char!=2,3:
            D = F.c4()/E.c4()

        if D.is_zero():
            return D

        assert E.quartic_twist(D).is_isomorphic(F)

        return D

    def is_sextic_twist(self, other):
        r"""
        Determine whether this curve is a sextic twist of another.

        INPUT:

        - ``other`` -- an elliptic curves with the same base field as self.

        OUTPUT:

        Either 0, if the curves are not sextic twists, or `D` if
        ``other`` is ``self.sextic_twist(D)`` (up to isomorphism).
        If ``self`` and ``other`` are isomorphic, returns 1.

        .. note::

           Not fully implemented in characteristics 2 or 3.

        EXAMPLES::

            sage: E = EllipticCurve_from_j(GF(13)(0))
            sage: E1 = E.sextic_twist(2)
            sage: D = E.is_sextic_twist(E1); D!=0
            True
            sage: E.sextic_twist(D).is_isomorphic(E1)
            True

        ::

            sage: E = EllipticCurve_from_j(0)
            sage: E1 = E.sextic_twist(12345)
            sage: D = E.is_sextic_twist(E1); D
            575968320
            sage: (D/12345).is_perfect_power(6)
            True
        """
        from sage.schemes.elliptic_curves.ell_generic import is_EllipticCurve
        E = self
        F = other
        if not is_EllipticCurve(E) or not is_EllipticCurve(F):
            raise ValueError, "arguments are not elliptic curves"
        K = E.base_ring()
        zero = K.zero_element()
        if not K == F.base_ring():
            return zero
        j=E.j_invariant()
        if  j != F.j_invariant() or not j.is_zero():
            return zero

        if E.is_isomorphic(F):
            return K.one_element()

        char=K.characteristic()

        if char==2:
            raise NotImplementedError, "not implemented in characteristic 2"
        elif char==3:
            raise NotImplementedError, "not implemented in characteristic 3"
        else:
            # now char!=2,3:
            D = F.c6()/E.c6()

        if D.is_zero():
            return D

        assert E.sextic_twist(D).is_isomorphic(F)

        return D

    def rst_transform(self, r, s, t):
        r"""
        Returns the transform of the curve by `(r,s,t)` (with `u=1`).

        INPUT:

        - ``r``, ``s``, ``t`` -- three elements of the base ring.

        OUTPUT:

        The elliptic curve obtained from self by the standard
        Weierstrass transformation `(u,r,s,t)` with `u=1`.

        .. note::

           This is just a special case of ``change_weierstrass_model()``, with `u=1`.

        EXAMPLES::

            sage: R.<r,s,t>=QQ[]
            sage: E=EllipticCurve([1,2,3,4,5])
            sage: E.rst_transform(r,s,t)
            Elliptic Curve defined by y^2 + (2*s+1)*x*y + (r+2*t+3)*y = x^3 + (-s^2+3*r-s+2)*x^2 + (3*r^2-r*s-2*s*t+4*r-3*s-t+4)*x + (r^3+2*r^2-r*t-t^2+4*r-3*t+5) over Multivariate Polynomial Ring in r, s, t over Rational Field
        """
        return self.change_weierstrass_model(1,r,s,t)

    def scale_curve(self, u):
        r"""
        Returns the transform of the curve by scale factor `u`.

        INPUT:

        - ``u`` -- an invertible element of the base ring.

        OUTPUT:

        The elliptic curve obtained from self by the standard
        Weierstrass transformation `(u,r,s,t)` with `r=s=t=0`.

        .. note::

           This is just a special case of ``change_weierstrass_model()``, with `r=s=t=0`.

       EXAMPLES::

            sage: K=Frac(PolynomialRing(QQ,'u'))
            sage: u=K.gen()
            sage: E=EllipticCurve([1,2,3,4,5])
            sage: E.scale_curve(u)
            Elliptic Curve defined by y^2 + u*x*y + 3*u^3*y = x^3 + 2*u^2*x^2 + 4*u^4*x + 5*u^6 over Fraction Field of Univariate Polynomial Ring in u over Rational Field
        """
        if isinstance(u, (int,long)):
            u=self.base_ring()(u)       # because otherwise 1/u would round!
        return self.change_weierstrass_model(1/u,0,0,0)

    def discriminant(self):
        """
        Returns the discriminant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([0,0,1,-1,0])
            sage: E.discriminant()
            37
            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.discriminant()
            -161051

        ::

            sage: E = EllipticCurve([GF(7)(2),1])
            sage: E.discriminant()
            1
        """
        try:
            return self.__discriminant
        except AttributeError:
            b2, b4, b6, b8 = self.b_invariants()
            self.__discriminant = -b2**2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6
            return self.__discriminant

    def j_invariant(self):
        """
        Returns the j-invariant of this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve([0,0,1,-1,0])
            sage: E.j_invariant()
            110592/37
            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.j_invariant()
            -122023936/161051
            sage: E = EllipticCurve([-4,0])
            sage: E.j_invariant()
            1728

        ::

            sage: E = EllipticCurve([GF(7)(2),1])
            sage: E.j_invariant()
            1
        """
        try:
            return self.__j_invariant
        except AttributeError:
            c4, _ = self.c_invariants()
            self.__j_invariant = c4**3 / self.discriminant()
            return self.__j_invariant

#############################################################
#
# Explanation of the division (also known as torsion) polynomial
# functions in Sage.
#
# The main user function division_polynomial() (also aliased as
# torsion_polynomial()) is used to compute polynomials whose roots
# determine the $m$-torsion points on the curve.  Three options are
# available, which effect the result when $m$ is even and also the
# parent ring of the returned value.  The function can return either a
# polynomial or the evaluation of that polynomial at a point,
# depending on the input.  Values are cached.
#
# The options are controlled by the value of the parameter
# two_torsion_multiplicity, which may be 0, 1 or 2.  If it is 0 or 2,
# then a univariate polynomial will be returned (or evaluated at the
# parameter x if x is not None).  This is the polynomial whose roots
# are the values of $x(P)$ at the nonzero points $P$ where $m*P=0$
# (when two_torsion_multiplicity==2), or the points where $m*P=0$ but
# $2*P\not=0$ (when two_torsion_multiplicity==0).
#
# If two_torsion_multiplicity==1, then a bivariate polynomial is
# returned, which (as a function on the curve) has a simple zero at
# each nonzero point $P$ such that $m*P=0$.  When $m$ is odd this is a
# polynomial in $x$ alone, but is still returned as an element of a
# polynomial ring in two variables; when $m$ is even it has a factor
# $2y+a_1x+a_3$.  In this case if the parameter x is not None then it
# should be a tuple of length 2, or a point P on the curve, and the
# returned value is the value of the bivariate polynomial at this
# point.
#
# Comparison with Magma: Magma's function DivisionPolynomial(E,m)
# returns a triple of univariate polynomials $f,g,h$ where $f$ is
# \code{E.division_polynomial(m,two_torsion_multiplicity=2)}, $g$ is
# \code{E.division_polynomial(m,two_torsion_multiplicity=0)} and $h$
# is the quotient, so that $h=1$ when $m$ is odd.

#############################################################

    def division_polynomial_0(self, n, x=None, cache=None):
         r"""
         Returns the `n^{th}` torsion (division) polynomial, without
         the 2-torsion factor if `n` is even, as a polynomial in `x`.

         These are the polynomials `g_n` defined in Mazur/Tate
         ("The p-adic sigma function"), but with the sign flipped for even
         `n`, so that the leading coefficient is always positive.

         .. note::

            This function is intended for internal use; users should use
            :meth:`.division_polynomial`.

         .. seealso::

            :meth:`multiple_x_numerator`
            :meth:`multiple_x_denominator`
            :meth:`division_polynomial`

         INPUT:


         -  ``n`` - positive integer, or the special values `-1`
            and `-2` which mean `B_6 = (2y + a_1 x + a_3)^2` and
            `B_6^2` respectively (in the notation of Mazur/Tate).

         -  ``x`` - optional ring element to use as the "x"
            variable. If x is None, then a new polynomial ring will be
            constructed over the base ring of the elliptic curve, and its
            generator will be used as x. Note that x does not need to be a
            generator of a polynomial ring; any ring element is ok. This
            permits fast calculation of the torsion polynomial *evaluated* on
            any element of a ring.

         -  ``cache`` - optional dictionary, with integer keys.
            If the key m is in cache, then cache[m] is assumed to be the value
            of division_polynomial_0(m) for the supplied x. New entries will
            be added to the cache as they are computed.


         ALGORITHM:

         Recursion described in Mazur/Tate. The recursive
         formulae are evaluated `O((log n)^2)` times.

         AUTHORS:

         - David Harvey (2006-09-24): initial version

         - John Cremona (2008-08-26): unified division polynomial code

         EXAMPLES::

             sage: E = EllipticCurve("37a")
             sage: E.division_polynomial_0(1)
             1
             sage: E.division_polynomial_0(2)
             1
             sage: E.division_polynomial_0(3)
             3*x^4 - 6*x^2 + 3*x - 1
             sage: E.division_polynomial_0(4)
             2*x^6 - 10*x^4 + 10*x^3 - 10*x^2 + 2*x + 1
             sage: E.division_polynomial_0(5)
             5*x^12 - 62*x^10 + 95*x^9 - 105*x^8 - 60*x^7 + 285*x^6 - 174*x^5 - 5*x^4 - 5*x^3 + 35*x^2 - 15*x + 2
             sage: E.division_polynomial_0(6)
             3*x^16 - 72*x^14 + 168*x^13 - 364*x^12 + 1120*x^10 - 1144*x^9 + 300*x^8 - 540*x^7 + 1120*x^6 - 588*x^5 - 133*x^4 + 252*x^3 - 114*x^2 + 22*x - 1
             sage: E.division_polynomial_0(7)
             7*x^24 - 308*x^22 + 986*x^21 - 2954*x^20 + 28*x^19 + 17171*x^18 - 23142*x^17 + 511*x^16 - 5012*x^15 + 43804*x^14 - 7140*x^13 - 96950*x^12 + 111356*x^11 - 19516*x^10 - 49707*x^9 + 40054*x^8 - 124*x^7 - 18382*x^6 + 13342*x^5 - 4816*x^4 + 1099*x^3 - 210*x^2 + 35*x - 3
             sage: E.division_polynomial_0(8)
             4*x^30 - 292*x^28 + 1252*x^27 - 5436*x^26 + 2340*x^25 + 39834*x^24 - 79560*x^23 + 51432*x^22 - 142896*x^21 + 451596*x^20 - 212040*x^19 - 1005316*x^18 + 1726416*x^17 - 671160*x^16 - 954924*x^15 + 1119552*x^14 + 313308*x^13 - 1502818*x^12 + 1189908*x^11 - 160152*x^10 - 399176*x^9 + 386142*x^8 - 220128*x^7 + 99558*x^6 - 33528*x^5 + 6042*x^4 + 310*x^3 - 406*x^2 + 78*x - 5

         ::

             sage: E.division_polynomial_0(18) % E.division_polynomial_0(6) == 0
             True

         An example to illustrate the relationship with torsion points::

             sage: F = GF(11)
             sage: E = EllipticCurve(F, [0, 2]); E
             Elliptic Curve defined by y^2  = x^3 + 2 over Finite Field of size 11
             sage: f = E.division_polynomial_0(5); f
             5*x^12 + x^9 + 8*x^6 + 4*x^3 + 7
             sage: f.factor()
             (5) * (x^2 + 5) * (x^2 + 2*x + 5) * (x^2 + 5*x + 7) * (x^2 + 7*x + 7) * (x^2 + 9*x + 5) * (x^2 + 10*x + 7)

         This indicates that the x-coordinates of all the 5-torsion points
         of `E` are in `GF(11^2)`, and therefore the
         `y`-coordinates are in `\GF(11^4)`::

             sage: K = GF(11^4, 'a')
             sage: X = E.change_ring(K)
             sage: f = X.division_polynomial_0(5)
             sage: x_coords = f.roots(multiplicities=False); x_coords
             [10*a^3 + 4*a^2 + 5*a + 6,
              9*a^3 + 8*a^2 + 10*a + 8,
              8*a^3 + a^2 + 4*a + 10,
              8*a^3 + a^2 + 4*a + 8,
              8*a^3 + a^2 + 4*a + 4,
              6*a^3 + 9*a^2 + 3*a + 4,
              5*a^3 + 2*a^2 + 8*a + 7,
              3*a^3 + 10*a^2 + 7*a + 8,
              3*a^3 + 10*a^2 + 7*a + 3,
              3*a^3 + 10*a^2 + 7*a + 1,
              2*a^3 + 3*a^2 + a + 7,
              a^3 + 7*a^2 + 6*a]

         Now we check that these are exactly the `x`-coordinates of the
         5-torsion points of `E`::

             sage: for x in x_coords:
             ...       assert X.lift_x(x).order() == 5

         The roots of the polynomial are the `x`-coordinates of the points `P`
         such that `mP=0` but `2P\not=0`::

             sage: E=EllipticCurve('14a1')
             sage: T=E.torsion_subgroup()
             sage: [n*T.0 for n in range(6)]
             [(0 : 1 : 0),
             (9 : 23 : 1),
             (2 : 2 : 1),
             (1 : -1 : 1),
             (2 : -5 : 1),
             (9 : -33 : 1)]
             sage: pol=E.division_polynomial_0(6)
             sage: xlist=pol.roots(multiplicities=False); xlist
             [9, 2, -1/3, -5]
             sage: [E.lift_x(x, all=True) for x in xlist]
             [[(9 : 23 : 1), (9 : -33 : 1)], [(2 : 2 : 1), (2 : -5 : 1)], [], []]

         .. note::

            The point of order 2 and the identity do not appear.
            The points with `x=-1/3` and `x=-5` are not rational.
         """
         if cache is None:
             cache = {}
         else:
             try:
                 return cache[n]
             except KeyError:
                 pass

         if x is None:
             x = rings.PolynomialRing(self.base_ring(), 'x').gen()

         b2, b4, b6, b8 = self.b_invariants()

         n = int(n)
         if n <= 4:
             if n == -1:
                 answer = 4*x**3 + b2*x**2 + 2*b4*x + b6
             elif n == -2:
                 answer = self.division_polynomial_0(-1, x, cache) ** 2
             elif n == 1 or n == 2:
                 answer = x.parent()(1)
             elif n == 3:
                 answer = 3*x**4 + b2*x**3 + 3*b4*x**2 + 3*b6*x + b8
             elif n == 4:
                 answer = -self.division_polynomial_0(-2, x, cache) + \
                          (6*x**2 + b2*x + b4) * \
                          self.division_polynomial_0(3, x, cache)
             else:
                 raise ValueError, "n must be a positive integer (or -1 or -2)"
         else:
             if n % 2 == 0:
                 m = (n-2) // 2
                 g_mplus3 = self.division_polynomial_0(m+3, x, cache)
                 g_mplus2 = self.division_polynomial_0(m+2, x, cache)
                 g_mplus1 = self.division_polynomial_0(m+1, x, cache)
                 g_m      = self.division_polynomial_0(m,   x, cache)
                 g_mless1 = self.division_polynomial_0(m-1, x, cache)
                 answer = g_mplus1 * \
                          (g_mplus3 * g_m**2 - g_mless1 * g_mplus2**2)
             else:
                 m = (n-1) // 2
                 g_mplus2 = self.division_polynomial_0(m+2, x, cache)
                 g_mplus1 = self.division_polynomial_0(m+1, x, cache)
                 g_m      = self.division_polynomial_0(m,   x, cache)
                 g_mless1 = self.division_polynomial_0(m-1, x, cache)
                 B6_sqr   = self.division_polynomial_0(-2, x, cache)
                 if m % 2 == 0:
                     answer = B6_sqr * g_mplus2 * g_m**3 - \
                              g_mless1 * g_mplus1**3
                 else:
                     answer = g_mplus2 * g_m**3 - \
                              B6_sqr * g_mless1 * g_mplus1**3

         cache[n] = answer
         return answer

    def two_division_polynomial(self, x = None):
        r"""
        Returns the 2-division polynomial of this elliptic curve evaluated
        at ``x``.

        INPUT:

        - ``x`` - optional ring element to use as the `x` variable. If
          ``x`` is ``None``, then a new polynomial ring will be
          constructed over the base ring of the elliptic curve, and
          its generator will be used as ``x``. Note that ``x`` does
          not need to be a generator of a polynomial ring; any ring
          element is ok. This permits fast calculation of the torsion
          polynomial *evaluated* on any element of a ring.


        EXAMPLES::

            sage: E=EllipticCurve('5077a1')
            sage: E.two_division_polynomial()
            4*x^3 - 28*x + 25
            sage: E=EllipticCurve(GF(3^2,'a'),[1,1,1,1,1])
            sage: E.two_division_polynomial()
            x^3 + 2*x^2 + 2
            sage: E.two_division_polynomial().roots()
            [(2, 1), (2*a, 1), (a + 2, 1)]
        """
        return self.division_polynomial_0(-1,x)

    def division_polynomial(self, m, x=None, two_torsion_multiplicity=2):
        r"""
        Returns the `m^{th}` division polynomial of this elliptic
        curve evaluated at ``x``.

        INPUT:


        -  ``m`` - positive integer.

        -  ``x`` - optional ring element to use as the "x"
           variable. If x is None, then a new polynomial ring will be
           constructed over the base ring of the elliptic curve, and its
           generator will be used as x. Note that x does not need to be a
           generator of a polynomial ring; any ring element is ok. This
           permits fast calculation of the torsion polynomial *evaluated* on
           any element of a ring.

        -  ``two_torsion_multiplicity`` - 0,1 or 2

            If 0: for even `m` when x is None, a univariate polynomial
            over the base ring of the curve is returned, which omits
            factors whose roots are the `x`-coordinates of the
            `2`-torsion points. Similarly when `x` is not none, the
            evaluation of such a polynomial at `x` is returned.

            If 2: for even `m` when x is None, a univariate polynomial
            over the base ring of the curve is returned, which includes a
            factor of degree 3 whose roots are the `x`-coordinates of
            the `2`-torsion points. Similarly when `x` is not
            none, the evaluation of such a polynomial at `x` is
            returned.

            If 1: when x is None, a bivariate polynomial over the base
            ring of the curve is returned, which includes a factor
            `2*y+a1*x+a3` which has simple zeros at the `2`-torsion
            points. When `x` is not none, it should be a tuple of
            length 2, and the evaluation of such a polynomial at `x`
            is returned.

        EXAMPLES::

            sage: E = EllipticCurve([0,0,1,-1,0])
            sage: E.division_polynomial(1)
            1
            sage: E.division_polynomial(2, two_torsion_multiplicity=0)
            1
            sage: E.division_polynomial(2, two_torsion_multiplicity=1)
            2*y + 1
            sage: E.division_polynomial(2, two_torsion_multiplicity=2)
            4*x^3 - 4*x + 1
            sage: E.division_polynomial(2)
            4*x^3 - 4*x + 1
            sage: [E.division_polynomial(3, two_torsion_multiplicity=i) for i in range(3)]
            [3*x^4 - 6*x^2 + 3*x - 1, 3*x^4 - 6*x^2 + 3*x - 1, 3*x^4 - 6*x^2 + 3*x - 1]
            sage: [type(E.division_polynomial(3, two_torsion_multiplicity=i)) for i in range(3)]
            [<class 'sage.rings.polynomial.polynomial_element_generic.Polynomial_rational_dense'>,
            <type 'sage.rings.polynomial.multi_polynomial_libsingular.MPolynomial_libsingular'>,
            <class 'sage.rings.polynomial.polynomial_element_generic.Polynomial_rational_dense'>]

        ::

            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: R.<z>=PolynomialRing(QQ)
            sage: E.division_polynomial(4,z,0)
            2*z^6 - 4*z^5 - 100*z^4 - 790*z^3 - 210*z^2 - 1496*z - 5821
            sage: E.division_polynomial(4,z)
            8*z^9 - 24*z^8 - 464*z^7 - 2758*z^6 + 6636*z^5 + 34356*z^4 + 53510*z^3 + 99714*z^2 + 351024*z + 459859

        This does not work, since when two_torsion_multiplicity is 1, we
        compute a bivariate polynomial, and must evaluate at a tuple of
        length 2::

            sage: E.division_polynomial(4,z,1)
            Traceback (most recent call last):
            ...
            ValueError: x should be a tuple of length 2 (or None) when two_torsion_multiplicity is 1
            sage: R.<z,w>=PolynomialRing(QQ,2)
            sage: E.division_polynomial(4,(z,w),1).factor()
            (2*w + 1) * (2*z^6 - 4*z^5 - 100*z^4 - 790*z^3 - 210*z^2 - 1496*z - 5821)

        We can also evaluate this bivariate polynomial at a point::

            sage: P = E(5,5)
            sage: E.division_polynomial(4,P,two_torsion_multiplicity=1)
            -1771561
        """

        if not two_torsion_multiplicity in [0,1,2]:
            raise ValueError, "two_torsion_multiplicity must be 0,1 or 2"

        # Coerce the input m to be an integer
        m = rings.Integer(m)

        if two_torsion_multiplicity == 0:
            try:
                return self.__divpoly0[(m,x)]
            except AttributeError:
                self.__divpoly0 = {}
            except KeyError:
                pass
            f = self.division_polynomial_0(m,x)
            self.__divpoly0[(m,x)] = f
            return f

        if two_torsion_multiplicity == 1:
            try:
                return self.__divpoly1[(m,x)]
            except AttributeError:
                self.__divpoly1 = {}
            except KeyError:
                pass
            xy = x
            R, (x,y) = PolynomialRing(self.base_ring(), 2, 'x,y').objgens()
            a1,a2,a3,a4,a6 = self.a_invariants()
            f = self.division_polynomial_0(m,x)
            if m % 2 == 0:
                f *= (2*y+a1*x+a3)
            if xy is None:
                self.__divpoly1[(m,(x,y))] = f
                return f
            else:
                if isinstance(xy,tuple) and len(xy)==2 or isinstance(xy, ell_point.EllipticCurvePoint_field):
                    fxy = f(xy[0],xy[1])
                    self.__divpoly1[(m,xy)] = fxy
                    return fxy
                else:
                    raise ValueError, "x should be a tuple of length 2 (or None) when two_torsion_multiplicity is 1"

        if two_torsion_multiplicity == 2:
            try:
                return self.__divpoly2[(m,x)]
            except AttributeError:
                self.__divpoly2 = {}
            except KeyError:
                pass
            f = self.division_polynomial_0(m,x)
            if m%2 == 0:
                f *= self.division_polynomial_0(-1,x)
            self.__divpoly2[(m,x)] = f
            return f

    torsion_polynomial = division_polynomial

#     def torsion_polynomial_old(self, n, var='x', i=0):
#         r"""
#         Returns the n-th torsion polynomial (a.k.a., division polynomial).

#         INPUT:
#             n -- non-negative integer
#             var -- string; the indeterminate of the polynomial (default: x)
#             i -- integer, either 0 (default) or 1.

#         OUTPUT:
#             Polynomial -- n-th torsion polynomial, which is a polynomial over
#                           the base field of the elliptic curve.

#         SEE ALSO: _division_polynomial, full_division_polynomial

#         EXAMPLES:
#             sage: E = EllipticCurve([0,0,1,-1,0])
#             sage: E.torsion_polynomial_old(1)
#             1
#             sage: E.torsion_polynomial_old(2)
#             4*x^3 - 4*x + 1
#             sage: E.torsion_polynomial_old(3, 'z')
#             3*z^4 - 6*z^2 + 3*z - 1

#             sage: E = EllipticCurve([0, -1, 1, -10, -20])
#             sage: E.torsion_polynomial(0)
#             0
#             sage: E.torsion_polynomial(1)
#             1
#             sage: E.torsion_polynomial(2)
#             4*x^3 - 4*x^2 - 40*x - 79
#             sage: E.torsion_polynomial(3)
#             3*x^4 - 4*x^3 - 60*x^2 - 237*x - 21
#             sage: E.torsion_polynomial(4)
#             8*x^9 - 24*x^8 - 464*x^7 - 2758*x^6 + 6636*x^5 + 34356*x^4 + 53510*x^3 + 99714*x^2 + 351024*x + 459859

#             sage: E = EllipticCurve([-4,0])
#             sage: E.torsion_polynomial(2)
#             4*x^3 - 16*x
#             sage: E.torsion_polynomial(5)
#             5*x^12 - 248*x^10 - 1680*x^8 + 19200*x^6 - 32000*x^4 + 51200*x^2 + 4096
#             sage: E.torsion_polynomial(6)
#             12*x^19 - 1200*x^17 - 18688*x^15 + 422912*x^13 - 2283520*x^11 + 9134080*x^9 - 27066368*x^7 + 19136512*x^5 + 19660800*x^3 - 3145728*x

#             Check for consistency with division_polynomial_0:
#             sage: assert all([E.torsion_polynomial(2*m-1)==E.division_polynomial_0(2*m-1) for m in range(1,20)])
#             sage: assert all([E.torsion_polynomial(2*m)==E.division_polynomial_0(2*m)*E.division_polynomial_0(-1) for m in range(1,20)])

#         AUTHOR: David Kohel (kohel@maths.usyd.edu.au), 2005-04-25
#         """
#         n = int(n)
#         try:
#             return self.__torsion_polynomial[n]
#         except AttributeError:
#             self.__torsion_polynomial = {}
#         except KeyError:
#             pass
#         E = self; i=int(i)
#         if n < 0:
#             raise ValueError, "n must be a non-negative integer."
#         if i > 1 :
#             raise ValueError, "i must be 0 or 1."

#         R = rings.PolynomialRing(E.base_ring(), var)

# # This is just an abbreviation to make the following code clearer:
#         tp = lambda m: E.torsion_polynomial(m)

#         if i == 1:
#             if n == 0:
#                 f = tp(1)
#                 E.__torsion_polynomial[n] = f
#                 return f
#             else:
#                 x = R.gen()
#                 psi2 = tp(2)
#                 if n%2 == 0:
#                     f = x * psi2 * (tp(n)//psi2)**2 - tp(n+1) * tp(n-1)
#                     E.__torsion_polynomial[n] = f
#                     return f
#                 else:
#                     f = x * tp(n)**2 - (tp(n+1)//psi2) * tp(n-1)
#                     E.__torsion_polynomial[n] = f
#                     return f

#         else:

#             if n == 0: return R(0)
#             if n == 1: return R(1)
#             x = R.gen()
#             b2, b4, b6, b8 = E.b_invariants()
#             psi2 = 4*x**3 + b2*x**2 + 2*b4*x + b6
#             if n == 2:
#                 f = psi2
#                 E.__torsion_polynomial[n] = f; return f
#             if n == 3:
#                 f = 3*x**4 + b2*x**3 + 3*b4*x**2 + 3*b6*x + b8
#                 E.__torsion_polynomial[n] = f; return f
#             if n == 4:
#                 f = psi2 * (2*x**6 + b2*x**5 + 5*b4*x**4 + 10*b6*x**3 \
#                     + 10*b8*x**2  + (b2*b8 - b4*b6)*x + b4*b8 - b6**2)
#                 E.__torsion_polynomial[n] = f; return f
#             if n%2 == 0:
#                 m = n//2
#                 if m%2 == 0:
#                     f = tp(m) * \
#                         ((tp(m+2)//psi2) * tp(m-1)**2 - \
#                          (tp(m-2)//psi2) * tp(m+1)**2)
#                     E.__torsion_polynomial[n] = f; return f
#                 else:
#                     f = psi2 * tp(m)*( \
#                         tp(m+2) * (tp(m-1)//psi2)**2 - \
#                         tp(m-2) * (tp(m+1)//psi2)**2)
#                     E.__torsion_polynomial[n] = f; return f
#             else:
#                 m = n//2
#                 if m%2 == 0:
#                     f = psi2 * \
#                         tp(m+2) * (tp(m)//psi2)**3 - \
#                         tp(m-1) * tp(m+1)**3
#                     E.__torsion_polynomial[n] = f; return f
#                 else:
#                     f = tp(m+2) * tp(m)**3 - psi2 * \
#                         tp(m-1)*(tp(m+1)//psi2)**3
#                     E.__torsion_polynomial[n] = f; return f

#     def full_division_polynomial(self, m):
#         """
#         Return the $m$-th bivariate division polynomial in $x$ and
#         $y$.  When $m$ is odd this is exactly the same as the usual
#         $m$th division polynomial.

#         For the usual division polynomial only in $x$, see the
#         functions division_polynomial() and
#         division_polynomial_0().

#         INPUT:
#             self -- elliptic curve
#             m    -- a positive integer
#         OUTPUT:
#             a polynomial in two variables $x$, $y$.

#         NOTE: The result is cached.

#         EXAMPLES:
#         We create a curve and compute the first two full division
#         polynomials.
#             sage: E = EllipticCurve([2,3])
#             sage: E.full_division_polynomial(1)
#             1
#             sage: E.full_division_polynomial(2)
#             2*y

#         Note that for odd input the full division polynomial is
#         just the usual division polynomial, but not for even input:
#             sage: E.division_polynomial(2)
#             4*x^3 + 8*x + 12
#             sage: E.full_division_polynomial(3)
#             3*x^4 + 12*x^2 + 36*x - 4
#             sage: E.division_polynomial(3)
#             3*x^4 + 12*x^2 + 36*x - 4
#             sage: E.full_division_polynomial(4)
#             4*x^6*y + 40*x^4*y + 240*x^3*y - 80*x^2*y - 96*x*y - 320*y
#             sage: E.full_division_polynomial(5)
#             5*x^12 + 124*x^10 + 1140*x^9 - 420*x^8 + 1440*x^7 - 4560*x^6 - 8352*x^5 - 36560*x^4 - 45120*x^3 - 10240*x^2 - 39360*x - 22976

#         TESTS:
#         We test that the full division polynomial as computed using
#         the recurrence agrees with the normal division polynomial for
#         a certain curve and all odd $n$ up to $23$:

#             sage: E = EllipticCurve([23,-105])
#             sage: for n in [1,3,..,23]:
#             ...       assert E.full_division_polynomial(n) == E.division_polynomial(n)
#         """
#         # Coerce the input m to be an integer
#         m = rings.Integer(m)

#         # Check whether the corresponding poly is cached already
#         try:
#             return self.__divpoly2[m]
#         except AttributeError:
#             self.__divpoly2 = {}
#         except KeyError:
#             pass

#         # Get the invariants of the curve
#         a1,a2,a3,a4,a6 = self.a_invariants()

#         # Define the polynomial ring that will contain the full
#         # division polynomial.

#         R, (x,y) = PolynomialRing(self.base_ring(), 2, 'x,y').objgens()

#         # The function division_polynomial_0() gives the correct
#         # result when m is odd, and all we do in this case is evaluate
#         # this at the variable x in our bivariate polynomial ring.

#         # For even m, we must multiply the result of
#         # division_polynomial_0() by the full 2-torsion polynomial
#         # which is 2*y+a1*x+a3

#         f = self.division_polynomial_0(m,x)
#         if m % 2 == 0:
#             f *= (2*y+a1*x+a3)

#         # Cache the result and return it.
#         self.__divpoly2[m] = f
#         return f

    def _multiple_x_numerator(self, n, x=None, cache=None):
         r"""
         Returns the numerator of the `x`-coordinate of the `n\th` multiple of a
         point, using torsion polynomials (division polynomials).

         INPUT:

         -  ``n``, ``x``, ``cache`` --  as described in ``division_polynomial_0()``.

         The result is cached.  This is so that on calling
         ``P.division_points(n)`` for the same `n` and different
         points `P` (on the same curve), we do not have to recompute
         the polynomials.

         .. warning::

            There may of course be cancellation between the numerator
            and the denominator (_multiple_x_denominator()). Be
            careful. E.g. if a point on an elliptic curve with
            coefficients in ZZ reduces to a singular point modulo a
            prime, then there will be cancellation, otherwise not, see
            Chris Wuthrich' p-adic heights in families of elliptic
            curves'.

         .. seealso::

            :meth:`_multiple_x_denominator`

         AUTHORS:

         - David Harvey (2006-09-24)

         EXAMPLES::

             sage: E = EllipticCurve("37a")
             sage: P = E.gens()[0]
             sage: x = P[0]

         ::

             sage: (35*P)[0]
             -804287518035141565236193151/1063198259901027900600665796
             sage: E._multiple_x_numerator(35, x)
             -804287518035141565236193151
             sage: E._multiple_x_denominator(35, x)
             1063198259901027900600665796

         ::

             sage: (36*P)[0]
             54202648602164057575419038802/15402543997324146892198790401
             sage: E._multiple_x_numerator(36, x)
             54202648602164057575419038802
             sage: E._multiple_x_denominator(36, x)
             15402543997324146892198790401

         An example where cancellation occurs::

             sage: E = EllipticCurve("88a1")
             sage: P = E([2,2])   # fixed choice of generator
             sage: n = E._multiple_x_numerator(11, P[0]); n
             442446784738847563128068650529343492278651453440
             sage: d = E._multiple_x_denominator(11, P[0]); d
             1427247692705959881058285969449495136382746624
             sage: n/d
             310
             sage: 11*P
             (310 : -5458 : 1)
         """
         try:
             return self._mul_x_num_cache[n]
         except AttributeError:
             self._mul_x_num_cache = {}
         except KeyError:
             pass

         if cache is None:
             cache = {}

         if x is None:
             x = rings.PolynomialRing(self.base_ring(), 'x').gen()

         n = int(n)
         if n < 2:
             print "n must be at least 2"

         self.division_polynomial_0( -2, x, cache)
         self.division_polynomial_0(n-1, x, cache)
         self.division_polynomial_0(n  , x, cache)
         self.division_polynomial_0(n+1, x, cache)

         if n % 2 == 0:
             self._mul_x_num_cache[n] = x * cache[-1] * cache[n]**2 - cache[n-1] * cache[n+1]
         else:
             self._mul_x_num_cache[n] = x * cache[n]**2 - cache[-1] * cache[n-1] * cache[n+1]
         return self._mul_x_num_cache[n]


    def _multiple_x_denominator(self, n, x=None, cache=None):
         r"""
         Returns the denominator of the x-coordinate of the nth multiple of
         a point, using torsion polynomials (division polynomials).

         INPUT:

         -  ``n``, ``x``, ``cache`` --  as described in ``division_polynomial_0()``.

         The result is cached.  This is so that calling
         P.division_points(n) for the same n and different points P
         (on the same curve) does not have to recompute the
         polynomials.

         .. seealso::

            :meth:`multiple_x_numerator`

         TODO: the numerator and denominator versions share a calculation,
         namely squaring `\psi_n`. Maybe would be good to offer a
         combined version to make this more efficient.

         EXAMPLES::

             sage: E = EllipticCurve("43a")
             sage: P = E.gens()[0]
             sage: x = P[0]
             sage: (31*P)[0]
             -33058398375463796474831580/154693637754223970056975321
             sage: E._multiple_x_numerator(31, x)
             -33058398375463796474831580
             sage: E._multiple_x_denominator(31, x)
             154693637754223970056975321

         AUTHORS:

         - David Harvey (2006-09-24)
         """
         try:
             return self._mul_x_den_cache[n]
         except AttributeError:
             self._mul_x_den_cache = {}
         except KeyError:
             pass

         if cache is None:
             cache = {}

         if x is None:
             x = rings.PolynomialRing(self.base_ring(), 'x').gen()

         n = int(n)
         if n < 2:
             print "n must be at least 2"

         self.division_polynomial_0(-2, x, cache)
         self.division_polynomial_0(n , x, cache)

         if n % 2 == 0:
             self._mul_x_den_cache[n] = cache[-1] * cache[n]**2
         else:
             self._mul_x_den_cache[n] = cache[n]**2
         return self._mul_x_den_cache[n]


    def multiplication_by_m(self, m, x_only=False):
        r"""
        Return the multiplication-by-`m` map from self to self as a pair of
        rational functions in two variables `x`,`y`.

        INPUT:

        -  ``m`` - a nonzero integer

        -  ``x_only`` - bool (default: False) if True, return
           only the `x`-coordinate of the map.


        OUTPUT:

        (2-tuple) `(f(x), g(x,y))`, where `f` and `g` are rational
        functions with the degree of `y` in `g(x,y)` exactly 1.


        .. note:

           The result is not cached.

           ``m`` is allowed to be negative (but not 0).

        EXAMPLES::

            sage: E = EllipticCurve([-1,3])

        We verify that multiplication by 1 is just the identity::

            sage: E.multiplication_by_m(1)
            (x, y)

        Multiplication by 2 is more complicated::

            sage: f = E.multiplication_by_m(2)
            sage: f
            ((x^4 + 2*x^2 - 24*x + 1)/(4*x^3 - 4*x + 12), (8*x^6*y - 40*x^4*y + 480*x^3*y - 40*x^2*y + 96*x*y - 568*y)/(64*x^6 - 128*x^4 + 384*x^3 + 64*x^2 - 384*x + 576))

        Grab only the x-coordinate (less work)::

            sage: E.multiplication_by_m(2, x_only=True)
            (x^4 + 2*x^2 - 24*x + 1)/(4*x^3 - 4*x + 12)

        We check that it works on a point::

            sage: P = E([2,3])
            sage: eval = lambda f,P: [fi(P[0],P[1]) for fi in f]
            sage: assert E(eval(f,P)) == 2*P

        We do the same but with multiplication by 3::

            sage: f = E.multiplication_by_m(3)
            sage: assert E(eval(f,P)) == 3*P

        And the same with multiplication by 4::

            sage: f = E.multiplication_by_m(4)
            sage: assert E(eval(f,P)) == 4*P

        And the same with multiplication by -1,-2,-3,-4::

            sage: for m in [-1,-2,-3,-4]:
            ...       f = E.multiplication_by_m(m)
            ...       assert E(eval(f,P)) == m*P

        TESTS:

        Verify for this fairly random looking curve and point that
        multiplication by m returns the right result for the first 10
        integers::

            sage: E = EllipticCurve([23,-105])
            sage: P = E([129/4, 1479/8])
            sage: for n in [1..10]:
            ...       f = E.multiplication_by_m(n)
            ...       Q = n*P
            ...       assert Q == E(eval(f,P))
            ...       f = E.multiplication_by_m(-n)
            ...       Q = -n*P
            ...       assert Q == E(eval(f,P))

        The following test shows that \#4364 is indeed fixed::

            sage: p = next_prime(2^30-41)
            sage: a = GF(p)(1)
            sage: b = GF(p)(1)
            sage: E = EllipticCurve([a, b])
            sage: P = E.random_point()
            sage: my_eval = lambda f,P: [fi(P[0],P[1]) for fi in f]
            sage: f = E.multiplication_by_m(2)
            sage: assert(E(eval(f,P)) == 2*P)
        """
        # Coerce the input m to be an integer
        m = rings.Integer(m)

        if m==0:
            raise ValueError, "m must be a non-zero integer"

        R = PolynomialRing(self.base_ring(), 2, 'x,y')

        # Kxy is the function field, containing the full division polynomial.
        Kxy = R.fraction_field()
        x,y = Kxy.gens()

        # Special case of multiplication by 1 is easy.
        if m == 1:
            return (x, y)

        # Grab curve invariants
        a1,a2,a3,a4,a6 = self.a_invariants()

        if m == -1:
            return (x, -y-a1*x-a3)

        # the x-coordonate does not depend on the sign of m.  The work
        # here is done by functions defined earlier:

        mx = self._multiple_x_numerator(m.abs(),x) / self._multiple_x_denominator(m.abs(),x)

        if x_only:
            # Return it if the optional parameter x_only is set.
            return mx

        #  Consideration of the invariant differential
        #  w=dx/(2*y+a1*x+a3) shows that m*w = d(mx)/(2*my+a1*mx+a3)
        #  and hence 2*my+a1*mx+a3 = (1/m)*(2*y+a1*x+a3)*d(mx)/dx

        my = ((2*y+a1*x+a3)*mx.derivative(x)/m - a1*mx-a3)/2

        return mx, my

    def isomorphism_to(self, other):
        """
        Given another weierstrass model ``other`` of self, return an
        isomorphism from self to ``other``.

        INPUT:

        - ``other`` -- an elliptic curve isomorphic to ``self``.

        OUTPUT:

        (Weierstrassmorphism) An isomorphism from self to other.

        .. note::

           If the curves in question are not isomorphic, a ValueError is raised.

        EXAMPLES::

            sage: E = EllipticCurve('37a')
            sage: F = E.short_weierstrass_model()
            sage: w = E.isomorphism_to(F); w
            Generic morphism:
            From: Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
            To:   Abelian group of points on Elliptic Curve defined by y^2  = x^3 - 16*x + 16 over Rational Field
            Via:  (u,r,s,t) = (1/2, 0, 0, -1/2)
            sage: P = E(0,-1,1)
            sage: w(P)
            (0 : -4 : 1)
            sage: w(5*P)
            (1 : 1 : 1)
            sage: 5*w(P)
            (1 : 1 : 1)
            sage: 120*w(P) == w(120*P)
            True

        We can also handle injections to different base rings::

            sage: K.<a> = NumberField(x^3-7)
            sage: E.isomorphism_to(E.change_ring(K))
            Generic morphism:
              From: Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
              To:   Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 + (-1)*x over Number Field in a with defining polynomial x^3 - 7
              Via:  (u,r,s,t) = (1, 0, 0, 0)
        """
        return wm.WeierstrassIsomorphism(self, None, other)

    def automorphisms(self, field=None):
        """
        Return the set of isomorphisms from self to itself (as a list).

        INPUT:

        - ``field`` (default None) -- a field into which the
          coefficients of the curve may be coerced (by default, uses
          the base field of the curve).

        OUTPUT:

        (list) A list of ``WeierstrassIsomorphism``s consisting of all
        the isomorphisms from the curve ``self`` to itself defined
        over ``field``.

        EXAMPLES::

            sage: E = EllipticCurve_from_j(QQ(0)) # a curve with j=0 over QQ
            sage: E.automorphisms();
            [Generic endomorphism of Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 over Rational Field
            Via:  (u,r,s,t) = (-1, 0, 0, -1), Generic endomorphism of Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 over Rational Field
            Via:  (u,r,s,t) = (1, 0, 0, 0)]

        We can also find automorphisms defined over extension fields::

            sage: K.<a> = NumberField(x^2+3) # adjoin roots of unity
            sage: E.automorphisms(K)
            [Generic endomorphism of Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 over Number Field in a with defining polynomial x^2 + 3
            Via:  (u,r,s,t) = (1, 0, 0, 0),
            ...
            Generic endomorphism of Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 over Number Field in a with defining polynomial x^2 + 3
            Via:  (u,r,s,t) = (-1/2*a - 1/2, 0, 0, 0)]

        ::

            sage: [ len(EllipticCurve_from_j(GF(q,'a')(0)).automorphisms()) for q in [2,4,3,9,5,25,7,49]]
            [2, 24, 2, 12, 2, 6, 6, 6]
        """
        if field==None:
            return [wm.WeierstrassIsomorphism(self, urst, self)
                    for urst in wm.isomorphisms(self,self)]
        E=self.change_ring(field)
        return [wm.WeierstrassIsomorphism(E, urst, E)
                for urst in wm.isomorphisms(E,E)]

    def isomorphisms(self, other, field=None):
        """
        Return the set of isomorphisms from self to other (as a list).

        INPUT:

        - ``other`` -- another elliptic curve.

        - ``field`` (default None) -- a field into which the
          coefficients of the curves may be coerced (by default, uses
          the base field of the curves).

        OUTPUT:

        (list) A list of ``WeierstrassIsomorphism``s consisting of all
        the isomorphisms from the curve ``self`` to the curve
        ``other`` defined over ``field``.

        EXAMPLES::

            sage: E = EllipticCurve_from_j(QQ(0)) # a curve with j=0 over QQ
            sage: F = EllipticCurve('27a3') # should be the same one
            sage: E.isomorphisms(F);
            [Generic morphism:
            From: Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 over Rational Field
            To:   Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 over Rational Field
            Via:  (u,r,s,t) = (-1, 0, 0, -1), Generic morphism:
            From: Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 over Rational Field
            To:   Abelian group of points on Elliptic Curve defined by y^2 + y = x^3 over Rational Field
            Via:  (u,r,s,t) = (1, 0, 0, 0)]

        We can also find istomorphisms defined over extension fields::

            sage: E=EllipticCurve(GF(7),[0,0,0,1,1])
            sage: F=EllipticCurve(GF(7),[0,0,0,1,-1])
            sage: E.isomorphisms(F)
            []
            sage: E.isomorphisms(F,GF(49,'a'))
            [Generic morphism:
            From: Abelian group of points on Elliptic Curve defined by y^2 = x^3 + x + 1 over Finite Field in a of size 7^2
            To:   Abelian group of points on Elliptic Curve defined by y^2 = x^3 + x + 6 over Finite Field in a of size 7^2
            Via:  (u,r,s,t) = (a + 3, 0, 0, 0), Generic morphism:
            From: Abelian group of points on Elliptic Curve defined by y^2 = x^3 + x + 1 over Finite Field in a of size 7^2
            To:   Abelian group of points on Elliptic Curve defined by y^2 = x^3 + x + 6 over Finite Field in a of size 7^2
            Via:  (u,r,s,t) = (6*a + 4, 0, 0, 0)]
        """
        if field==None:
            return [wm.WeierstrassIsomorphism(self, urst, other)
                    for urst in wm.isomorphisms(self,other)]
        E=self.change_ring(field)
        F=other.change_ring(field)
        return [wm.WeierstrassIsomorphism(E, urst, F)
                for urst in wm.isomorphisms(E,F)]

    def is_isomorphic(self, other, field=None):
        """
        Returns whether or not self is isomorphic to other.

        INPUT:

        - ``other`` -- another elliptic curve.

        - ``field`` (default None) -- a field into which the
          coefficients of the curves may be coerced (by default, uses
          the base field of the curves).

        OUTPUT:

        (bool) True if there is an isomorphism from curve ``self`` to
        curve ``other`` defined over ``field``.

        EXAMPLES::

            sage: E = EllipticCurve('389a')
            sage: F = E.change_weierstrass_model([2,3,4,5]); F
            Elliptic Curve defined by y^2 + 4*x*y + 11/8*y = x^3 - 3/2*x^2 - 13/16*x over Rational Field
            sage: E.is_isomorphic(F)
            True
            sage: E.is_isomorphic(F.change_ring(CC))
            False
        """
        if not is_EllipticCurve(other):
            return False
        if field==None:
            if self.base_ring() != other.base_ring():
                return False
            elif self.j_invariant() != other.j_invariant():  # easy check
                return False
            else:
                return wm.isomorphisms(self,other,True) != None
        else:
            E=self.base_extend(field)
            F=other.base_extend(field)
            if E.j_invariant() != F.j_invariant():  # easy check
                return False
            else:
                return wm.isomorphisms(E,other,F) != None

    def change_weierstrass_model(self, *urst):
        r"""
        Return a new Weierstrass model of self under the standard transformation `(u,r,s,,t)`

        .. math::

             (x,y) \mapsto (x',y') = (u^2xr , u^3y + su^2x' + t).


        EXAMPLES::

            sage: E = EllipticCurve('15a')
            sage: F1 = E.change_weierstrass_model([1/2,0,0,0]); F1
            Elliptic Curve defined by y^2 + 2*x*y + 8*y = x^3 + 4*x^2 - 160*x - 640 over Rational Field
            sage: F2 = E.change_weierstrass_model([7,2,1/3,5]); F2
            Elliptic Curve defined by y^2 + 5/21*x*y + 13/343*y = x^3 + 59/441*x^2 - 10/7203*x - 58/117649 over Rational Field
            sage: F1.is_isomorphic(F2)
            True
        """
        if isinstance(urst[0], (tuple, list)):
            urst = urst[0]
        return constructor.EllipticCurve((wm.baseWI(*urst))(self.ainvs()))

    def short_weierstrass_model(self, complete_cube=True):
        """
        Returns a short Weierstrass model for self.

        INPUT:

        -  ``complete_cube`` - bool (default: True); for
           meaning, see below.

        OUTPUT:

        An elliptic curve.

        If ``complete_cube=True``: Return a model of the form
        `y^2 = x^3 + a*x + b` for this curve. The characteristic
        must not be 2; in characteristic 3, it is only possible if `b_2=0`.

        If ``complete_cube=False``: Return a model of the form
        `y^2 = x^3 + ax^2 + bx + c` for this curve. The
        characteristic must not be 2.

        EXAMPLES::

            sage: E = EllipticCurve([1,2,3,4,5])
            sage: print E
            Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 4*x + 5 over Rational Field
            sage: F = E.short_weierstrass_model()
            sage: print F
            Elliptic Curve defined by y^2  = x^3 + 4941*x + 185166 over Rational Field
            sage: E.is_isomorphic(F)
            True
            sage: F = E.short_weierstrass_model(complete_cube=False)
            sage: print F
            Elliptic Curve defined by y^2  = x^3 + 9*x^2 + 88*x + 464 over Rational Field
            sage: print E.is_isomorphic(F)
            True

        ::

            sage: E = EllipticCurve(GF(3),[1,2,3,4,5])
            sage: E.short_weierstrass_model(complete_cube=False)
            Elliptic Curve defined by y^2 = x^3 + x + 2 over Finite Field of size 3

        This used to be different see trac #3973::

            sage: E.short_weierstrass_model()
            Elliptic Curve defined by y^2 = x^3 + x + 2 over Finite Field of size 3

        More tests in characteristic 3::

            sage: E = EllipticCurve(GF(3),[0,2,1,2,1])
            sage: E.short_weierstrass_model()
            Traceback (most recent call last):
            ...
            ValueError: short_weierstrass_model(): no short model for Elliptic Curve defined by y^2 + y = x^3 + 2*x^2 + 2*x + 1 over Finite Field of size 3 (characteristic is 3)
            sage: E.short_weierstrass_model(complete_cube=False)
            Elliptic Curve defined by y^2 = x^3 + 2*x^2 + 2*x + 2 over Finite Field of size 3
            sage: E.short_weierstrass_model(complete_cube=False).is_isomorphic(E)
            True
        """
        import constructor
        K = self.base_ring()

        # any curve of the form y^2 = x^3 +.. is singular in characteristic 2
        if K.characteristic() == 2:
            raise ValueError, "short_weierstrass_model(): no short model for %s (characteristic is %s)"%(self,K.characteristic())

        # in characteristic 3 we can complete the square but we can only complete the cube if b2 is 0
        if K.characteristic() == 3:
            b2,b4,b6,_ = self.b_invariants()
            if complete_cube and b2 != 0:
                raise ValueError, "short_weierstrass_model(): no short model for %s (characteristic is %s)"%(self,K.characteristic())
            else:
                return constructor.EllipticCurve([0,b2,0,8*b4,16*b6])

        a1,a2,a3,_,_ = self.a_invariants()
        if complete_cube:
            if a1==0 and a2==0 and a3==0:
                return self
            else:
                b2,b4,b6,_ = self.b_invariants()
                if b2==0:
                    return constructor.EllipticCurve([0,0,0,8*b4,16*b6])
                else:
                    c4, c6 = self.c_invariants()
                    return constructor.EllipticCurve([0,0,0,-27*c4, -54*c6])
        else:
            if a1==0 and a3==0:
                return self
            else:
                b2,b4,b6,_ = self.b_invariants()
                return constructor.EllipticCurve([0,b2,0,8*b4,16*b6])



    # Plotting


    def plot(self, xmin=None, xmax=None, **args):
        """
        Draw a graph of this elliptic curve.

        INPUT:

        -  ``xmin, xmax`` - (optional) points will be computed at
           least within this range, but possibly farther.

        -  ``**args`` - all other options are passed to the
           line graphing primitive.


        EXAMPLES::

            sage: E = EllipticCurve([0,-1])
            sage: plot(E, rgbcolor=hue(0.7))
            sage: E = EllipticCurve('37a')
            sage: plot(E)
            sage: plot(E, xmin=25,xmax=25)
        """
        RR = rings.RealField()
        K = self.base_ring()
        try:
            RR._coerce_(K(1))
        except TypeError:
            raise NotImplementedError, "Plotting of curves over %s not implemented yet"%K
        a1, a2, a3, a4, a6 = self.ainvs()
        R = rings.PolynomialRing(rings.RealField(), 'x')
        x = R.gen()
        d = 4*x**3 + (a1**2 + 4*a2)*x**2 + (2*a3*a1 + 4*a4)*x + (a3**2 + 4*a6)
        # Internal function for plotting first branch of the curve
        f1 = lambda z: (-(a1*z + a3) + sqrt(abs(d(z))))/2
        # Internal function for plotting second branch of the curve
        f2 = lambda z: (-(a1*z + a3) - sqrt(abs(d(z))))/2
        r = d.roots(multiplicities=False)
        r.sort()
        if xmax is None:
            xmax = r[-1] + 2
        xmax = max(xmax, r[-1]+2)
        if xmin is None:
            xmin = r[0]  - 2
        xmin = min(xmin, r[0]-2)
        if len(r) == 1:
            # one real root; 1 component
            I = [(r[0],xmax)]
        else:
            # three real roots; 2 components
            I = [(r[0],r[1]), (r[2],xmax)]
        I = [(max(a,xmin),min(b,xmax)) for a,b in I]

        g = plot.Graphics()
        try:
            plot_points = int(args['plot_points'])
            del args['plot_points']
        except KeyError:
            plot_points = 100

        for j in range(len(I)):
            a,b = I[j]
            delta = (b-a)/float(plot_points)
            v = []
            w = []
            for i in range(plot_points):
                x = a + delta*i
                v.append((x, f1(x)))
                w.append((x, f2(x)))
            v.append((b,f1(b)))
            w.append((b,f2(b)))
            if len(I) == 2 and j == 0:  # two components -- the oh.
                g += plot.line(v + list(reversed(w)) + [v[0]], **args)
            else:
                g += plot.line(list(reversed(v)) + w, **args)
        return g

    def formal_group(self):
        r"""
        The formal group associated to this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve("37a")
            sage: E.formal_group()
            Formal Group associated to the Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
        """
        try:
            return self.__formal_group
        except AttributeError:
            self.__formal_group = formal_group.EllipticCurveFormalGroup(self)
            return self.__formal_group

    formal = formal_group

    def _p_primary_torsion_basis(self,p):
        r"""
        Find a basis for the `p`-primary part of the torsion
        subgroup of this elliptic curve.

        INPUT:

        - ``p`` (integer) -- a prime number.

        OUTPUT:

        A list of 0, 1 or 2 pairs `[T,k]` where `T` is a generator of
        order `p^k`. That is, either `[]` or `[[T_1,k_1]]` or
        `[[T_1,k_1],[T_2,k_2]]` with `[]`, `[T_1]`, or `[T_1,T_2]` a
        basis and `p^{k_1} \ge p^{k_2} \ge 1` their orders.

        .. warning::

           1. Do not call this on a curve whose group is
              `p`-divisible (i.e., whose `p`-primary part
              is infinite)!

           2. The code uses division polynomials and will be slow for
              large `p`.

        EXAMPLES::

            sage: E=EllipticCurve('11a1')
            sage: E._p_primary_torsion_basis(5)
            [[(5 : -6 : 1), 1]]
            sage: K.<t>=NumberField(x^4 + x^3 + 11*x^2 + 41*x + 101)
            sage: EK=E.base_extend(K)
            sage: EK._p_primary_torsion_basis(5)
            [[(16 : 60 : 1), 1], [(t : 1/11*t^3 + 6/11*t^2 + 19/11*t + 48/11 : 1), 1]]
            sage: EF=E.change_ring(GF(101))
            sage: EF._p_primary_torsion_basis(5)
            [[(0 : 13 : 1), 1], [(5 : 5 : 1), 1]]

            This shows that the bug at trac \#4937 is fixed::

            sage: a=804515977734860566494239770982282063895480484302363715494873
            sage: b=584772221603632866665682322899297141793188252000674256662071
            sage: [t[1] for t in EllipticCurve(GF(10^60+3201),[0,a,0,b,0])._p_primary_torsion_basis(2)]
            [16, 1]
        """
        p = rings.Integer(p)
        if not p.is_prime():
            raise ValueError, "p (=%s) should be prime"%p

        # First find the p-torsion:
        Ep = self(0).division_points(p)
        p_rank = rings.Integer(len(Ep)).exact_log(p)
        assert p_rank in [0,1,2]

        if p_rank == 0:
            return []

        assert p_rank in [1,2]

        if p_rank == 1:
            P = Ep[0]
            if P.is_zero(): P=Ep[1]
            k = 1
            pts = P.division_points(p) # length 0 or p
            while len(pts)>0:
                k += 1
                P = pts[0]
                pts = P.division_points(p)
            # now P generates the p-power-torsion and has order p^k
            return [[P,k]]

        assert p_rank == 2

        Epi = iter(Ep) # used to iterate through Ep
        # Find P1,P2 which generate the p-torsion:
        P1 = Epi.next()
        while P1.is_zero(): P1 = Epi.next()
        P2 = Epi.next()
        while generic.linear_relation(P1,P2,'+')[0] != 0: P2 = Epi.next()

        k = 1
        pts1 = P1.division_points(p)
        pts2 = P2.division_points(p)
        while len(pts1)>0 and len(pts2)>0:
            k += 1
            P1 = pts1[0]
            P2 = pts2[0]
            pts1 = P1.division_points(p)
            pts2 = P2.division_points(p)

        # Now P1,P2 are a basis for the p^k torsion, which is
        # isomorphic to (Z/p^k)^2, and k is the maximal integer for
        # which this is the case.

        # We now determine whether a combination (P2 or P1+a*P2 for
        # some a) can be further divided for some a mod p; if so,
        # replace P1 by that combination, set pts to be the list of
        # solutions Q to p*Q=P1.  If no combination can be divided,
        # then the structure is (p^k,p^k) and we can stop.

        if len(pts1) > 0:
            pts = pts1
        elif len(pts2) > 0:
            P1, P2 = P2, P1
            pts = pts2

        for Q in generic.multiples(P2,p-1,P1+P2,operation='+'):
            # Q runs through P1+a*P2 for a=1,2,...,p-1
            pts = Q.division_points(p)
            if len(pts) > 0:
                P1 = Q
                break
        if len(pts)==0:
            return [[P1,k],[P2,k]]

        # Now the structure is (p^n,p^k) for some n>k.  We need to
        # replace P1 by an element of maximal order p^n.  So far we
        # have pts = list of Q satisfying p*Q=P1, and all such Q have
        # order p^{k+1}.

        # We keep trying to divide P1 by p.  At each step, if we
        # succeed, replace P1 by any of the results and increment n.
        # If we fails try again with P1+a*P2 for a in [1..p-1]. If any
        # succeed, replace P1 by one of the resulting divided points.
        # If all fail, the structure is (p^n,p^k) and P1,P2 are
        # generators.

        n=k
        while True:
            P1=pts[0]
            n += 1
            pts = P1.division_points(p)
            if len(pts)==0:
                for Q in generic.multiples(P2,p-1,P1+P2,operation='+'):
                    # Q runs through P1+a*P2 for a=1,2,...,p-1
                    pts = Q.division_points(p)
                    if len(pts)>0:
                        break
                if len(pts)==0:
                    return [[P1,n],[P2,k]]


    def hyperelliptic_polynomials(self):
        r"""
        Returns a pair of polynomials `g(x)`, `h(x)` such that this elliptic
        curve can be defined by the standard hyperelliptic equation

        .. math::

            y^2 + h(x)y = g(x).

        EXAMPLES::

            sage: R.<a1,a2,a3,a4,a6>=QQ[]
            sage: E=EllipticCurve([a1,a2,a3,a4,a6])
            sage: E.hyperelliptic_polynomials()
            (x^3 + a2*x^2 + a4*x + a6, a1*x + a3)
        """
        K = self.base_ring()
        R = PolynomialRing(K, 'x')
        x = R.gen(0)
        a1, a2, a3, a4, a6 = self.ainvs()
        return R([a6, a4, a2, 1]), R([a3, a1])

    def pari_curve(self, prec=53):
        """
        Return the PARI curve corresponding to this elliptic curve.

        .. note::

           The result is cached; on subsequent calls teh cached value
           is returned prvided that it has sufficient precision,
           otherwise pari is called again with the new precision.

        EXAMPLES::

            sage: E = EllipticCurve([RR(0), RR(0), RR(1), RR(-1), RR(0)])
            sage: e = E.pari_curve()
            sage: type(e)
            <type 'sage.libs.pari.gen.gen'>
            sage: e.type()
            't_VEC'
            sage: e.disc()
            37.0000000000000
        """
        try:
            return self._pari_curve
        except AttributeError:
            pass

        from sage.libs.pari.all import pari
        self._pari_curve = pari(self.a_invariants()).ellinit(precision=prec)
        return self._pari_curve



def Hasse_bounds(q, genus=1):
    r"""
    Return the Hasse bounds for the cardinality of a curve defined
    over `\GF{q}` of given ``genus``.

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
