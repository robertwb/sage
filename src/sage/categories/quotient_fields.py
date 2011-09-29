r"""
Quotient fields
"""
#*****************************************************************************
#  Copyright (C) 2008 Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.category import Category
from sage.categories.category_singleton import Category_singleton
from sage.misc.cachefunc import cached_method
from sage.misc.abstract_method import abstract_method
from sage.categories.fields import Fields

class QuotientFields(Category_singleton):
    """
    The category of quotient fields over an integral domain

    EXAMPLES::

        sage: QuotientFields()
        Category of quotient fields
        sage: QuotientFields().super_categories()
        [Category of fields]

    TESTS::

        sage: TestSuite(QuotientFields()).run()
    """

    def super_categories(self):
        """
        EXAMPLES::

            sage: QuotientFields().super_categories()
            [Category of fields]
        """
        return [Fields()]

    class ParentMethods:
        pass

    class ElementMethods:

        @abstract_method
        def numerator(self):
            pass

        @abstract_method
        def denominator(self):
            pass

        def gcd(self,other):
            """
            Greatest common divisor

            NOTE:

            In a field, the greatest common divisor is not very
            informative, as it is only determined up to a unit. But in
            the fraction field of an integral domain that provides
            both gcd and lcm, it is possible to be a bit more specific
            and define the gcd uniquely up to a unit of the base ring
            (rather than in the fraction field).

            AUTHOR:

            - Simon King (2011-02): See trac ticket #10771

            EXAMPLES::

                sage: R.<x>=QQ[]
                sage: p = (1+x)^3*(1+2*x^2)/(1-x^5)
                sage: q = (1+x)^2*(1+3*x^2)/(1-x^4)
                sage: factor(p)
                (-2) * (x - 1)^-1 * (x + 1)^3 * (x^2 + 1/2) * (x^4 + x^3 + x^2 + x + 1)^-1
                sage: factor(q)
                (-3) * (x - 1)^-1 * (x + 1) * (x^2 + 1)^-1 * (x^2 + 1/3)
                sage: gcd(p,q)
                (x + 1)/(x^7 + x^5 - x^2 - 1)
                sage: factor(gcd(p,q))
                (x - 1)^-1 * (x + 1) * (x^2 + 1)^-1 * (x^4 + x^3 + x^2 + x + 1)^-1
                sage: factor(gcd(p,1+x))
                (x - 1)^-1 * (x + 1) * (x^4 + x^3 + x^2 + x + 1)^-1
                sage: factor(gcd(1+x,q))
                (x - 1)^-1 * (x + 1) * (x^2 + 1)^-1

            TESTS:

            The following tests that the fraction field returns a correct gcd
            even if the base ring does not provide lcm and gcd::

                sage: R = ZZ.extension(x^2+5,names='q'); R
                Order in Number Field in q with defining polynomial x^2 + 5
                sage: R.1
                q
                sage: gcd(R.1,R.1)
                Traceback (most recent call last):
                ...
                TypeError: unable to find gcd of q and q
                sage: (R.1/1).parent()
                Number Field in q with defining polynomial x^2 + 5
                sage: gcd(R.1/1,R.1)
                1
                sage: gcd(R.1/1,0)
                1
                sage: gcd(R.zero(),0)
                0

            """
            try:
                other = self.parent()(other)
            except (TypeError, ValueError):
                raise ArithmeticError, "The second argument can not be interpreted in the parent of the first argument. Can't compute the gcd"
            try:
                selfN = self.numerator()
                selfD = self.denominator()
                selfGCD = selfN.gcd(selfD)
                otherN = other.numerator()
                otherD = other.denominator()
                otherGCD = otherN.gcd(otherD)
                selfN = selfN // selfGCD
                selfD = selfD // selfGCD
                otherN = otherN // otherGCD
                otherD = otherD // otherGCD
                return selfN.gcd(otherN)/selfD.lcm(otherD)
            except (AttributeError, NotImplementedError, TypeError, ValueError):
                if self==0 and other==0:
                    return self.parent().zero()
                return self.parent().one()

        def lcm(self,other):
            """
            Least common multiple

            NOTE:

            In a field, the least common multiple is not very
            informative, as it is only determined up to a unit. But in
            the fraction field of an integral domain that provides
            both gcd and lcm, it is reasonable to be a bit more
            specific and to define the least common multiple so that
            it restricts to the usual least common multiple in the
            base ring and is unique up to a unit of the base ring
            (rather than up to a unit of the fraction field).

            AUTHOR:

            - Simon King (2011-02): See trac ticket #10771

            EXAMPLES::

                sage: R.<x>=QQ[]
                sage: p = (1+x)^3*(1+2*x^2)/(1-x^5)
                sage: q = (1+x)^2*(1+3*x^2)/(1-x^4)
                sage: factor(p)
                (-2) * (x - 1)^-1 * (x + 1)^3 * (x^2 + 1/2) * (x^4 + x^3 + x^2 + x + 1)^-1
                sage: factor(q)
                (-3) * (x - 1)^-1 * (x + 1) * (x^2 + 1)^-1 * (x^2 + 1/3)
                sage: factor(lcm(p,q))
                (x - 1)^-1 * (x + 1)^3 * (x^2 + 1/3) * (x^2 + 1/2)
                sage: factor(lcm(p,1+x))
                (x + 1)^3 * (x^2 + 1/2)
                sage: factor(lcm(1+x,q))
                (x + 1) * (x^2 + 1/3)

            TESTS:

            The following tests that the fraction field returns a correct lcm
            even if the base ring does not provide lcm and gcd::

                sage: R = ZZ.extension(x^2+5,names='q'); R
                Order in Number Field in q with defining polynomial x^2 + 5
                sage: R.1
                q
                sage: lcm(R.1,R.1)
                Traceback (most recent call last):
                ...
                TypeError: unable to find lcm of q and q
                sage: (R.1/1).parent()
                Number Field in q with defining polynomial x^2 + 5
                sage: lcm(R.1/1,R.1)
                1
                sage: lcm(R.1/1,0)
                0
                sage: lcm(R.zero(),0)
                0

            """
            try:
                other = self.parent()(other)
            except (TypeError, ValueError):
                raise ArithmeticError, "The second argument can not be interpreted in the parent of the first argument. Can't compute the lcm"
            try:
                selfN = self.numerator()
                selfD = self.denominator()
                selfGCD = selfN.gcd(selfD)
                otherN = other.numerator()
                otherD = other.denominator()
                otherGCD = otherN.gcd(otherD)
                selfN = selfN // selfGCD
                selfD = selfD // selfGCD
                otherN = otherN // otherGCD
                otherD = otherD // otherGCD
                return selfN.lcm(otherN)/selfD.gcd(otherD)
            except (AttributeError, NotImplementedError, TypeError, ValueError):
                if self==0 or other==0:
                    return self.parent().zero()
                return self.parent().one()

        def factor(self, *args, **kwds):
            """
            Return the factorization of ``self`` over the base ring.

            INPUT:

            - ``*args`` - Arbitrary arguments suitable over the base ring
            - ``**kwds`` - Arbitrary keyword arguments suitable over the base ring

            OUTPUT:

            - Factorization of ``self`` over the base ring

            EXAMPLES::

                sage: K.<x> = QQ[]
                sage: f = (x^3+x)/(x-3)
                sage: f.factor()
                (x - 3)^-1 * x * (x^2 + 1)

            Here is an example to show that ticket #7868 has been resolved::

                sage: R.<x,y> = GF(2)[]
                sage: f = x*y/(x+y)
                sage: f.factor()
                (x + y)^-1 * y * x
            """
            return (self.numerator().factor(*args, **kwds) /
                    self.denominator().factor(*args, **kwds))

        def partial_fraction_decomposition(self):
            """
            Decomposes fraction field element into a whole part and a list of
            fraction field elements over prime power denominators.

            The sum will be equal to the original fraction.

            AUTHORS:

            - Robert Bradshaw (2007-05-31)

            EXAMPLES::

                sage: S.<t> = QQ[]
                sage: q = 1/(t+1) + 2/(t+2) + 3/(t-3); q
                (6*t^2 + 4*t - 6)/(t^3 - 7*t - 6)
                sage: whole, parts = q.partial_fraction_decomposition(); parts
                [3/(t - 3), 1/(t + 1), 2/(t + 2)]
                sage: sum(parts) == q
                True
                sage: q = 1/(t^3+1) + 2/(t^2+2) + 3/(t-3)^5
                sage: whole, parts = q.partial_fraction_decomposition(); parts
                [1/3/(t + 1), 3/(t^5 - 15*t^4 + 90*t^3 - 270*t^2 + 405*t - 243), (-1/3*t + 2/3)/(t^2 - t + 1), 2/(t^2 + 2)]
                sage: sum(parts) == q
                True

            We do the best we can over inexact fields::

                sage: R.<x> = RealField(20)[]
                sage: q = 1/(x^2 + x + 2)^2 + 1/(x-1); q
                (x^4 + 2.0000*x^3 + 5.0000*x^2 + 5.0000*x + 3.0000)/(x^5 + x^4 + 3.0000*x^3 - x^2 - 4.0000)
                sage: whole, parts = q.partial_fraction_decomposition(); parts
                [1.0000/(x - 1.0000), 1.0000/(x^4 + 2.0000*x^3 + 5.0000*x^2 + 4.0000*x + 4.0000)]
                sage: sum(parts)
                (x^4 + 2.0000*x^3 + 5.0000*x^2 + 5.0000*x + 3.0000)/(x^5 + x^4 + 3.0000*x^3 - x^2 - 4.0000)

            TESTS:

            We test partial fraction for irreducible denominators::

                sage: R.<x> = ZZ[]
                sage: q = x^2/(x-1)
                sage: q.partial_fraction_decomposition()
                (x + 1, [1/(x - 1)])
                sage: q = x^10/(x-1)^5
                sage: whole, parts = q.partial_fraction_decomposition()
                sage: whole + sum(parts) == q
                True

            And also over finite fields (see trac #6052, #9945)::

                sage: R.<x> = GF(2)[]
                sage: q = (x+1)/(x^3+x+1)
                sage: q.partial_fraction_decomposition()
                (0, [(x + 1)/(x^3 + x + 1)])

                sage: R.<x> = GF(11)[]
                sage: q = x + 1 + 1/(x+1) + x^2/(x^3 + 2*x + 9)
                sage: q.partial_fraction_decomposition()
                (x + 1, [1/(x + 1), x^2/(x^3 + 2*x + 9)])

            And even the rationals::

                sage: (26/15).partial_fraction_decomposition()
                (1, [1/3, 2/5])
            """
            from sage.misc.misc import prod
            denom = self.denominator()
            whole, numer = self.numerator().quo_rem(denom)
            factors = denom.factor()
            if factors.unit() != 1:
                numer *= ~factors.unit()
            if len(factors) == 1:
                return whole, [numer/r**e for r,e in factors]
            if not self.parent().is_exact():
                # factors not grouped in this case
                all = {}
                for r in factors: all[r[0]] = 0
                for r in factors: all[r[0]] += r[1]
                factors = all.items()
                factors.sort() # for doctest consistency
            factors = [r**e for r,e in factors]
            parts = []
            for d in factors:
                # note that the product below is non-empty, since the case
                # of only one factor has been dealt with above
                n = numer * prod([r for r in factors if r != d]).inverse_mod(d) % d # we know the inverse exists as the two are relatively prime
                parts.append(n/d)
            return whole, parts

        def derivative(self, *args):
            r"""
            The derivative of this rational function, with respect to variables
            supplied in args.

            Multiple variables and iteration counts may be supplied; see
            documentation for the global derivative() function for more
            details.

            .. seealso::

               :meth:`_derivative`

            EXAMPLES::

                sage: F.<x> = Frac(QQ['x'])
                sage: (1/x).derivative()
                -1/x^2

            ::

                sage: (x+1/x).derivative(x, 2)
                2/x^3

            ::

                sage: F.<x,y> = Frac(QQ['x,y'])
                sage: (1/(x+y)).derivative(x,y)
                2/(x^3 + 3*x^2*y + 3*x*y^2 + y^3)
            """
            from sage.misc.derivative import multi_derivative
            return multi_derivative(self, args)

        def _derivative(self, var=None):
            r"""
            Returns the derivative of this rational function with respect to the
            variable ``var``.

            Over an ring with a working gcd implementation, the derivative of a
            fraction `f/g`, supposed to be given in lowest terms, is computed as
            `(f'(g/d) - f(g'/d))/(g(g'/d))`, where `d` is a greatest common
            divisor of `f` and `g`.

            INPUT:

            - ``var`` - Variable with respect to which the derivative is computed

            OUTPUT:

            - Derivative of ``self`` with respect to ``var``

            .. seealso::

               :meth:`derivative`

            EXAMPLES::

                sage: F.<x> = Frac(QQ['x'])
                sage: t = 1/x^2
                sage: t._derivative(x)
                -2/x^3
                sage: t.derivative()
                -2/x^3

            ::

                sage: F.<x,y> = Frac(QQ['x,y'])
                sage: t = (x*y/(x+y))
                sage: t._derivative(x)
                y^2/(x^2 + 2*x*y + y^2)
                sage: t._derivative(y)
                x^2/(x^2 + 2*x*y + y^2)

            TESTS::

                sage: F.<t> = Frac(ZZ['t'])
                sage: F(0).derivative()
                0
                sage: F(2).derivative()
                0
                sage: t.derivative()
                1
                sage: (1+t^2).derivative()
                2*t
                sage: (1/t).derivative()
                -1/t^2
                sage: ((t+2)/(t-1)).derivative()
                -3/(t^2 - 2*t + 1)
                sage: (t/(1+2*t+t^2)).derivative()
                (-t + 1)/(t^3 + 3*t^2 + 3*t + 1)
            """
            R = self.parent()
            if var in R.gens():
                var = R.ring()(var)

            num = self.numerator()
            den = self.denominator()

            if (num.is_zero()):
                return R.zero_element()

            if R.is_exact():
                try:
                    numder = num._derivative(var)
                    dender = den._derivative(var)
                    d      = den.gcd(dender)
                    den    = den // d
                    dender = dender // d
                    tnum   = numder * den - num * dender
                    tden   = self.denominator() * den
                    if not tden.is_one() and tden.is_unit():
                        try:
                            tnum = tnum * tden.inverse_of_unit()
                            tden = R.ring().one_element()
                        except AttributeError:
                            pass
                        except NotImplementedError:
                            pass
                    return self.__class__(R, tnum, tden,
                        coerce=False, reduce=False)
                except AttributeError:
                    pass
                except NotImplementedError:
                    pass
                except TypeError:
                    pass
                num = self.numerator()
                den = self.denominator()

            num = num._derivative(var) * den - num * den._derivative(var)
            den = den**2

            return self.__class__(R, num, den,
                coerce=False, reduce=False)
