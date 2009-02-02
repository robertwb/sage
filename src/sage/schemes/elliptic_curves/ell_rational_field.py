"""
Elliptic curves over the rational numbers

AUTHORS:

- William Stein (2005): first version

- William Stein (2006-02-26): fixed Lseries_extended which didn't work
  because of changes elsewhere in Sage.

- David Harvey (2006-09): Added padic_E2, padic_sigma, padic_height,
  padic_regulator methods.

- David Harvey (2007-02): reworked padic-height related code

- Christian Wuthrich (2007): added padic sha computation

- David Roe (2007-09): moved sha, l-series and p-adic functionality to
  separate files.

- John Cremona (2008-01)

- Tobias Nagel and Michael Mardaus (2008-07): added integral_points

- John Cremona (2008-07): further work on integral_points
"""

#*****************************************************************************
#       Copyright (C) 2005,2006,2007 William Stein <wstein@gmail.com>
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

import ell_point
import formal_group
import ell_torsion
from ell_generic import EllipticCurve_generic
from ell_number_field import EllipticCurve_number_field

import sage.groups.all
import sage.rings.arith as arith
import sage.rings.all as rings
import sage.rings.number_field.number_field as number_field
import sage.misc.misc as misc
from sage.misc.all import verbose
import sage.functions.constants as constants
import sage.modular.modform.constructor
import sage.modular.modform.element
from sage.misc.functional import log
from sage.rings.padics.factory import Zp, Qp

# Use some interval arithmetic to guarantee correctness.  We assume
# that alpha is computed to the precision of a float.
# IR = rings.RIF
#from sage.rings.interval import IntervalRing; IR = IntervalRing()

import sage.matrix.all as matrix
import sage.databases.cremona
from   sage.libs.pari.all import pari, PariError
import sage.functions.transcendental as transcendental
from math import sqrt
import sage.libs.mwrank.all as mwrank
import constructor
from sage.interfaces.all import gp

import ell_modular_symbols
import padic_lseries
import padics
from sage.rings.padics.precision_error import PrecisionError

from lseries_ell import Lseries_ell

import mod5family

from sage.rings.all import (
    PowerSeriesRing, LaurentSeriesRing, O,
    infinity as oo,
    Integer,
    Integers,
    IntegerRing, RealField,
    ComplexField, RationalField)

import gp_cremona
import sea

from gp_simon import simon_two_descent

import ell_tate_curve

factor = arith.factor
mul = misc.mul
next_prime = arith.next_prime
kronecker_symbol = arith.kronecker_symbol

Q = RationalField()
C = ComplexField()
R = RealField()
Z = IntegerRing()
IR = rings.RealIntervalField(20)

_MAX_HEIGHT=21

# complex multiplication dictionary:
# CMJ is a dict of pairs (j,D) where j is a rational CM j-invariant
# and D is the corresponding quadratic discriminant

CMJ={ 0: -3, 54000: -12, -12288000: -27, 1728: -4, 287496: -16,
      -3375: -7, 16581375: -28, 8000: -8, -32768: -11, -884736: -19,
      -884736000: -43, -147197952000: -67, -262537412640768000: -163}



class EllipticCurve_rational_field(EllipticCurve_number_field):
    """
    Elliptic curve over the Rational Field.
    """
    def __init__(self, ainvs, extra=None):
        if extra != None:   # possibility of two arguments (the first would be the field)
            ainvs = extra
        if isinstance(ainvs, str):
            label = ainvs
            X = sage.databases.cremona.CremonaDatabase()[label]
            EllipticCurve_number_field.__init__(self, Q, X.a_invariants())
            for attr in ['rank', 'torsion_order', 'cremona_label', 'conductor',
                         'modular_degree', 'gens', 'regulator']:
                s = "_EllipticCurve_rational_field__"+attr
                if hasattr(X,s):
                    setattr(self, s, getattr(X, s))
            return
        EllipticCurve_number_field.__init__(self, Q, ainvs)
        self.__np = {}
        self.__gens = {}
        self.__rank = {}
        self.__regulator = {}
        if self.base_ring() != Q:
            raise TypeError, "Base field (=%s) must be the Rational Field."%self.base_ring()

    def _set_rank(self, r):
        """
        Internal function to set the cached rank of this elliptic curve to
        r.

        .. warning::

           No checking is done! Not intended for use by users.

        EXAMPLES::

            sage: E = EllipticCurve('37a1')
            sage: E._set_rank(99)  # bogus value -- not checked
            sage: E.rank()         # returns bogus cached value
            99
            sage: E._EllipticCurve_rational_field__rank={} # undo the damage
            sage: E.rank()         # the correct rank
            1
        """
        self.__rank = {}
        self.__rank[True] = Integer(r)

    def _set_torsion_order(self, t):
        """
        Internal function to set the cached torsion order of this elliptic
        curve to t.

        .. warning::

           No checking is done! Not intended for use by users.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E._set_torsion_order(99)  # bogus value -- not checked
            sage: E.torsion_order()         # returns bogus cached value
            99
            sage: T = E.torsion_subgroup()  # causes actual torsion to be computed
            sage: E.torsion_order()         # the correct value
            1
        """
        self.__torsion_order = Integer(t)

    def _set_cremona_label(self, L):
        """
        Internal function to set the cached label of this elliptic curve to
        L.

        .. warning::

           No checking is done! Not intended for use by users.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E._set_cremona_label('bogus')
            sage: E.label()
            'bogus'
            sage: E.database_curve().label()
            '37a1'
            sage: E.label() # no change
            'bogus'
            sage: E._set_cremona_label(E.database_curve().label())
            sage: E.label() # now it is correct
            '37a1'
        """
        self.__cremona_label = L

    def _set_conductor(self, N):
        """
        Internal function to set the cached conductor of this elliptic
        curve to N.

        .. warning::

           No checking is done! Not intended for use by users.
           Setting to the wrong value will cause strange problems (see
           examples).

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E._set_conductor(99)      # bogus value -- not checked
            sage: E.conductor()             # returns bogus cached value
            99

        This will not work since the conductor is used when searching the
        database::

            sage: E._set_conductor(E.database_curve().conductor())
            Traceback (most recent call last):
            ...
            RuntimeError: Elliptic curve ... not in the database.
            sage: E._set_conductor(EllipticCurve(E.a_invariants()).database_curve().conductor())
            sage: E.conductor()             # returns correct value
            37
        """
        self.__conductor_pari = Integer(N)

    def _set_modular_degree(self, deg):
        """
        Internal function to set the cached modular degree of this elliptic
        curve to deg.

        .. warning::

           No checking is done!

        EXAMPLES::

            sage: E=EllipticCurve('5077a1')
            sage: E.modular_degree()
            1984
            sage: E._set_modular_degree(123456789)
            sage: E.modular_degree()
            123456789
            sage: E._set_modular_degree(E.database_curve().modular_degree())
            sage: E.modular_degree()
            1984
        """
        self.__modular_degree = Integer(deg)

    def _set_gens(self, gens):
        """
        Internal function to set the cached generators of this elliptic
        curve to gens.

        .. warning::

           No checking is done!

        EXAMPLES::

            sage: E=EllipticCurve('5077a1')
            sage: E.rank()
            3
            sage: E.gens() # random
            [(-2 : 3 : 1), (-7/4 : 25/8 : 1), (1 : -1 : 1)]
            sage: E._set_gens([]) # bogus list
            sage: E.rank()        # unchanged
            3
            sage: E._set_gens([E(-2,3), E(-1,3), E(0,2)])
            sage: E.gens()
            [(-2 : 3 : 1), (-1 : 3 : 1), (0 : 2 : 1)]
        """
        self.__gens = {}
        self.__gens[True] = [self.point(x, check=True) for x in gens]
        self.__gens[True].sort()

    def is_p_integral(self, p):
        r"""
         Returns True if this elliptic curve has `p`-integral
         coefficients.

         INPUT:


         -  ``p`` - a prime integer


         EXAMPLES::

             sage: E=EllipticCurve(QQ,[1,1]); E
             Elliptic Curve defined by y^2 = x^3 + x + 1 over Rational Field
             sage: E.is_p_integral(2)
             True
             sage: E2=E.change_weierstrass_model(2,0,0,0); E2
             Elliptic Curve defined by y^2 = x^3 + 1/16*x + 1/64 over Rational Field
             sage: E2.is_p_integral(2)
             False
             sage: E2.is_p_integral(3)
             True
         """
        if not arith.is_prime(p):
            raise ArithmeticError, "p must be prime"
        if self.is_integral():
            return True
        return bool(misc.mul([x.valuation(p) >= 0 for x in self.ainvs()]))

    def is_integral(self):
        """
         Returns True if this elliptic curve has integral coefficients (in
         Z)

         EXAMPLES::

             sage: E=EllipticCurve(QQ,[1,1]); E
             Elliptic Curve defined by y^2 = x^3 + x + 1 over Rational Field
             sage: E.is_integral()
             True
             sage: E2=E.change_weierstrass_model(2,0,0,0); E2
             Elliptic Curve defined by y^2 = x^3 + 1/16*x + 1/64 over Rational Field
             sage: E2.is_integral()
             False
         """
        try:
            return self.__is_integral
        except AttributeError:
            one = Integer(1)
            self.__is_integral = bool(misc.mul([x.denominator() == 1 for x in self.ainvs()]))
            return self.__is_integral


    def mwrank(self, options=''):
        """
        Run Cremona's mwrank program on this elliptic curve and return the
        result as a string.

        INPUT:


        -  ``options`` - string; passed when starting mwrank.
           The format is q pprecision vverbosity bhlim_q xnaux chlim_c l t o
           s d]


        OUTPUT:


        -  ``string`` - output of mwrank on this curve


        .. note::

           The output is a raw string and completely illegible using
           automatic display, so it is recommended to use print for
           legible output.

        EXAMPLES::

            sage: E = EllipticCurve('37a1')
            sage: E.mwrank() #random
            ...
            sage: print E.mwrank()
            Curve [0,0,1,-1,0] :        Basic pair: I=48, J=-432
            disc=255744
            ...
            Generator 1 is [0:-1:1]; height 0.05111...

            Regulator = 0.05111...

            The rank and full Mordell-Weil basis have been determined unconditionally.
            ...

        Options to mwrank can be passed::

            sage: E = EllipticCurve([0,0,0,877,0])

        Run mwrank with 'verbose' flag set to 0 but list generators if
        found

        ::

            sage: print E.mwrank('-v0 -l')
            Curve [0,0,0,877,0] :   0 <= rank <= 1
            Regulator = 1

        Run mwrank again, this time with a higher bound for point searching
        on homogeneous spaces::

            sage: print E.mwrank('-v0 -l -b11')
            Curve [0,0,0,877,0] :   Rank = 1
            Generator 1 is [29604565304828237474403861024284371796799791624792913256602210:-256256267988926809388776834045513089648669153204356603464786949:490078023219787588959802933995928925096061616470779979261000]; height 95.980371987964
            Regulator = 95.980371987964
        """
        if options == "":
            from sage.interfaces.all import mwrank
        else:
            from sage.interfaces.all import Mwrank
            mwrank = Mwrank(options=options)
        return mwrank(self.a_invariants())

    def conductor(self, algorithm="pari"):
        """
        Returns the conductor of the elliptic curve.

        INPUT:


        -  ``algorithm`` - str, (default: "pari")

           -  ``"pari"`` - use the PARI C-library ellglobalred
              implementation of Tate's algorithm

           -  ``"mwrank"`` - use Cremona's mwrank implementation
              of Tate's algorithm; can be faster if the curve has integer
              coefficients (TODO: limited to small conductor until mwrank gets
              integer factorization)

           -  ``"gp"`` - use the GP interpreter.

           -  ``"generic"`` - use the general number field
              implementation

           -  ``"all"`` - use all four implementations, verify
              that the results are the same (or raise an error), and output the
              common value.


        EXAMPLE::

            sage: E = EllipticCurve([1, -1, 1, -29372, -1932937])
            sage: E.conductor(algorithm="pari")
            3006
            sage: E.conductor(algorithm="mwrank")
            3006
            sage: E.conductor(algorithm="gp")
            3006
            sage: E.conductor(algorithm="generic")
            3006
            sage: E.conductor(algorithm="all")
            3006

        .. note::

           The conductor computed using each algorithm is cached
           separately. Thus calling ``E.conductor('pari')``, then
           ``E.conductor('mwrank')`` and getting the same result
           checks that both systems compute the same answer.
        """

        if algorithm == "pari":
            try:
                return self.__conductor_pari
            except AttributeError:
                self.__conductor_pari = Integer(self.pari_mincurve().ellglobalred()[0])
            return self.__conductor_pari

        elif algorithm == "gp":
            try:
                return self.__conductor_gp
            except AttributeError:
                self.__conductor_gp = Integer(gp.eval('ellglobalred(ellinit(%s,0))[1]'%self.a_invariants()))
                return self.__conductor_gp

        elif algorithm == "mwrank":
            try:
                return self.__conductor_mwrank
            except AttributeError:
                if self.is_integral():
                    self.__conductor_mwrank = Integer(self.mwrank_curve().conductor())
                else:
                    self.__conductor_mwrank = Integer(self.minimal_model().mwrank_curve().conductor())
            return self.__conductor_mwrank

        elif algorithm == "generic":
            try:
                return self.__conductor_generic
            except AttributeError:
                self.__conductor_generic = sage.schemes.elliptic_curves.ell_number_field.EllipticCurve_number_field.conductor(self).gen()
                return self.__conductor_generic

        elif algorithm == "all":
            N1 = self.conductor("pari")
            N2 = self.conductor("mwrank")
            N3 = self.conductor("gp")
            N4 = self.conductor("generic")
            if N1 != N2 or N2 != N3 or N2 != N4:
                raise ArithmeticError, "Pari, mwrank, gp and Sage compute different conductors (%s,%s,%s,%3) for %s"%(
                    N1, N2, N3, N4, self)
            return N1
        else:
            raise RuntimeError, "algorithm '%s' is not known."%algorithm

    ####################################################################
    #  Access to PARI curves related to this curve.
    ####################################################################

    def pari_curve(self, prec = None, factor = 1):
        """
        Return the PARI curve corresponding to this elliptic curve.

        INPUT:


        -  ``prec`` - The precision of quantities calculated for the
           returned curve, in bits. If None, defaults to factor
           multiplied by the precision of the largest cached curve (or
           the default real precision if none yet computed).

        -  ``factor`` - The factor by which to increase the
           precision over the maximum previously computed precision. Only used
           if prec (which gives an explicit precision) is None.


        EXAMPLES::

            sage: E = EllipticCurve([0, 0, 1, -1, 0])
            sage: e = E.pari_curve()
            sage: type(e)
            <type 'sage.libs.pari.gen.gen'>
            sage: e.type()
            't_VEC'
            sage: e.ellan(10)
            [1, -2, -3, 2, -2, 6, -1, 0, 6, 4]

        ::

            sage: E = EllipticCurve(RationalField(), ['1/3', '2/3'])
            sage: e = E.pari_curve(prec = 100)
            sage: E._pari_curve.has_key(100)
            True
            sage: e.type()
            't_VEC'
            sage: e[:5]
            [0, 0, 0, 1/3, 2/3]

        This shows that the bug uncovered by trac #3954 is fixed::

            sage: E._pari_curve.has_key(100)
            True

        ::

            sage: E = EllipticCurve('37a1').pari_curve()
            sage: E[14].python().prec()
            64
            sage: [a.precision() for a in E]
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4] # 32-bit
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3] # 64-bit

        This shows that the bug uncovered by trac #4715 is fixed::

            sage: Ep = EllipticCurve('903b3').pari_curve()
        """
        try:
            # if the PARI curve has already been computed to this
            # precision, returned the cached copy
            return self._pari_curve[prec]
        except AttributeError:
            # no PARI curves have been computed for this elliptic curve
            self._pari_curve = {}
            if prec is None:
                prec = rings.RealField().precision()
        except KeyError:
            # PARI curves are cached for this elliptic curve, but they
            # are not of the requested precision (or prec = None)
            if prec is None:
                L = self._pari_curve.keys()
                L.sort()
                if factor == 1:
                    return self._pari_curve[L[-1]]
                else:
                    prec = int(factor * L[-1])
        # EllipticCurve('903b3').pari_curve() fails without this loop:
        while True:
            try:
                self._pari_curve[prec] = pari(self.a_invariants()).ellinit(precision=prec)
                return self._pari_curve[prec]
            except PariError:
                prec *= 2

    # This alias is defined so that pari(E) returns exactly the same
    # as E.pari_curve().  Without it, pari(E) would call the default
    # _pari_() as defined in sage.structure.sage_object.pyx, which
    # in turn calls pari(s) where s=E._pari_init_(), as defined in
    # ell_generic.py, which is just an ellinit() string of the form
    # 'ellinit([a1,a2,a3,a4,a6])'.  This way gives better control over
    # the precision of the returned pari curve: pari(E) will return a
    # pari elliptic curve with the highest precision computed by any
    # previous call to E.pari_curve(), or 53 bits by default if that
    # function has not previously been called.

    _pari_ = pari_curve

    def pari_mincurve(self, prec = None, factor = 1):
        """
        Return the PARI curve corresponding to a minimal model for this
        elliptic curve.

        INPUT:


        -  ``prec`` - The precision of quantities calculated for the
           returned curve, in bits. If None, defaults to factor
           multiplied by the precision of the largest cached curve (or
           the default real precision if none yet computed).

        -  ``factor`` - The factor by which to increase the
           precision over the maximum previously computed precision. Only used
           if prec (which gives an explicit precision) is None.


        EXAMPLES::

            sage: E = EllipticCurve(RationalField(), ['1/3', '2/3'])
            sage: e = E.pari_mincurve()
            sage: e[:5]
            [0, 0, 0, 27, 486]
            sage: E.conductor()
            47232
            sage: e.ellglobalred()
            [47232, [1, 0, 0, 0], 2]
        """
        try:
            # if the PARI curve has already been computed to this
            # precision, returned the cached copy
            return self._pari_mincurve[prec]
        except AttributeError:
            # no PARI curves have been computed for this elliptic curve
            self._pari_mincurve = {}
        except KeyError:
            # PARI curves are cached for this elliptic curve, but they
            # are not of the requested precision (or prec = None)
            if prec is None:
                L = self._pari_mincurve.keys()
                L.sort()
                if factor == 1:
                    return self._pari_mincurve[L[-1]]
                else:
                    prec = int(factor * L[-1])
        e = self.pari_curve(prec)
        mc, change = e.ellminimalmodel()
        self._pari_mincurve[prec] = mc
        # self.__min_transform = change
        return mc

    def database_curve(self):
        """
        Return the curve in the elliptic curve database isomorphic to this
        curve, if possible. Otherwise raise a RuntimeError exception.

        EXAMPLES::

            sage: E = EllipticCurve([0,1,2,3,4])
            sage: E.database_curve()
            Elliptic Curve defined by y^2  = x^3 + x^2 + 3*x + 5 over Rational Field

        .. note::

           The model of the curve in the database can be different
           from the Weierstrass model for this curve, e.g., database
           models are always minimal.
        """
        try:
            return self.__database_curve
        except AttributeError:
            misc.verbose("Looking up %s in the database."%self)
            D = sage.databases.cremona.CremonaDatabase()
            ainvs = self.minimal_model().ainvs()
            try:
                self.__database_curve = D.elliptic_curve_from_ainvs(self.conductor(), ainvs)
            except RuntimeError:
                raise RuntimeError, "Elliptic curve %s not in the database."%self
            return self.__database_curve


    def Np(self, p):
        """
        The number of points on E modulo p, where p is a prime, not
        necessarily of good reduction. (When p is a bad prime, also counts
        the singular point.)

        EXAMPLES::

            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.Np(2)
            5
            sage: E.Np(3)
            5
            sage: E.conductor()
            11
            sage: E.Np(11)
            11
        """
        if self.conductor() % p == 0:
            return p + 1 - self.ap(p)
        #raise ArithmeticError, "p (=%s) must be a prime of good reduction"%p
        if p < 1125899906842624:   # TODO: choose more wisely?
            return p+1 - self.ap(p)
        else:
            return self.sea(p)

    def sea(self, p, early_abort=False):
        r"""
        Return the number of points on `E` over
        `\mathbb{F}_p` computed using the SEA algorithm, as
        implemented in PARI by Christophe Doche and Sylvain Duquesne.

        INPUT:


        -  ``p`` - a prime number

        -  ``early_abort`` - bool (default: False); if True an
           early abort technique is used and the computation is interrupted as
           soon as a small divisor of the order is detected.


        .. note::

           As of 2006-02-02 this function does not work on Microsoft
           Windows under Cygwin (though it works under VMWare of
           course).

        EXAMPLES::

            sage: E = EllipticCurve('37a')
            sage: E.sea(next_prime(10^30))
            1000000000000001426441464441649
        """
        p = rings.Integer(p)
        return sea.ellsea(self.minimal_model().a_invariants(), p, early_abort=early_abort)

    #def __pari_double_prec(self):
    #    EllipticCurve_number_field._EllipticCurve__pari_double_prec(self)
    #    try:
    #        del self._pari_mincurve
    #    except AttributeError:
    #        pass

    ####################################################################
    #  Access to mwrank
    ####################################################################
    def mwrank_curve(self, verbose=False):
        """
        Construct an mwrank_EllipticCurve from this elliptic curve

        The resulting mwrank_EllipticCurve has available methods from John
        Cremona's eclib library.

        EXAMPLES::

            sage: E=EllipticCurve('11a1')
            sage: EE=E.mwrank_curve()
            sage: EE
            y^2+ y = x^3 - x^2 - 10*x - 20
            sage: type(EE)
            <class 'sage.libs.mwrank.interface.mwrank_EllipticCurve'>
            sage: EE.isogeny_class()
            ([[0, -1, 1, -10, -20], [0, -1, 1, -7820, -263580], [0, -1, 1, 0, 0]],
            [[0, 5, 5], [5, 0, 0], [5, 0, 0]])
        """
        try:
            return self.__mwrank_curve
        except AttributeError:
            pass
        self.__mwrank_curve = mwrank.mwrank_EllipticCurve(
            self.ainvs(), verbose=verbose)
        return self.__mwrank_curve

    def two_descent(self, verbose=True,
                    selmer_only = False,
                    first_limit = 20,
                    second_limit = 8,
                    n_aux = -1,
                    second_descent = 1):
        """
        Compute 2-descent data for this curve.

        INPUT:


        -  ``verbose`` - (default: True) print what mwrank is
           doing. If False, **no output** is printed.

        -  ``selmer_only`` - (default: False) selmer_only
           switch

        -  ``first_limit`` - (default: 20) firstlim is bound
           on x+z second_limit- (default: 8) secondlim is bound on log max
           x,z , i.e. logarithmic

        -  ``n_aux`` - (default: -1) n_aux only relevant for
           general 2-descent when 2-torsion trivial; n_aux=-1 causes default
           to be used (depends on method)

        -  ``second_descent`` - (default: True)
           second_descent only relevant for descent via 2-isogeny


        OUTPUT:

        Nothing - nothing is returned (though much is printed unless
        verbose=False)

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.two_descent(verbose=False) # no output
        """
        self.mwrank_curve().two_descent(verbose, selmer_only,
                                        first_limit, second_limit,
                                        n_aux, second_descent)


    ####################################################################
    #  Etc.
    ####################################################################

    def aplist(self, n, python_ints=False):
        r"""
        The Fourier coefficients `a_p` of the modular form
        attached to this elliptic curve, for all primes `p\leq n`.

        INPUT:


        -  ``n`` - integer

        -  ``python_ints`` - bool (default: False); if True
           return a list of Python ints instead of Sage integers.


        OUTPUT: list of integers

        EXAMPLES::

            sage: e = EllipticCurve('37a')
            sage: e.aplist(1)
            []
            sage: e.aplist(2)
            [-2]
            sage: e.aplist(10)
            [-2, -3, -2, -1]
            sage: v = e.aplist(13); v
            [-2, -3, -2, -1, -5, -2]
            sage: type(v[0])
            <type 'sage.rings.integer.Integer'>
            sage: type(e.aplist(13, python_ints=True)[0])
            <type 'int'>
        """
        e = self.pari_mincurve()
        v = e.ellaplist(n, python_ints=True)
        if python_ints:
            return v
        else:
            return [Integer(a) for a in v]



    def anlist(self, n, python_ints=False):
        """
        The Fourier coefficients up to and including `a_n` of the
        modular form attached to this elliptic curve. The i-th element of
        the return list is a[i].

        INPUT:


        -  ``n`` - integer

        -  ``python_ints`` - bool (default: False); if True
           return a list of Python ints instead of Sage integers.


        OUTPUT: list of integers

        EXAMPLES::

            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E.anlist(3)
            [0, 1, -2, -1]

        ::

            sage: E = EllipticCurve([0,1])
            sage: E.anlist(20)
            [0, 1, 0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 8, 0]
        """
        n = int(n)
        e = self.pari_mincurve()
        if n >= 2147483648:
            raise RuntimeError, "anlist: n (=%s) must be < 2147483648."%n

        v = [0] + e.ellan(n, python_ints=True)
        if not python_ints:
            v = [Integer(x) for x in v]
        return v


        # There is some overheard associated with coercing the PARI
        # list back to Python, but it's not bad.  It's better to do it
        # this way instead of trying to eval the whole list, since the
        # int conversion is done very sensibly.  NOTE: This would fail
        # if a_n won't fit in a C int, i.e., is bigger than
        # 2147483648; however, we wouldn't realistically compute
        # anlist for n that large anyway.
        #
        # Some relevant timings:
        #
        # E <--> [0, 1, 1, -2, 0]   389A
        #  E = EllipticCurve([0, 1, 1, -2, 0]);   // SAGE or MAGMA
        #  e = E.pari_mincurve()
        #  f = ellinit([0,1,1,-2,0]);
        #
        #  Computation                                              Time (1.6Ghz Pentium-4m laptop)
        #  time v:=TracesOfFrobenius(E,10000);  // MAGMA            0.120
        #  gettime;v=ellan(f,10000);gettime/1000                    0.046
        #  time v=e.ellan (10000)                                   0.04
        #  time v=E.anlist(10000)                                   0.07

        #  time v:=TracesOfFrobenius(E,100000);  // MAGMA           1.620
        #  gettime;v=ellan(f,100000);gettime/1000                   0.676
        #  time v=e.ellan (100000)                                  0.7
        #  time v=E.anlist(100000)                                  0.83

        #  time v:=TracesOfFrobenius(E,1000000);  // MAGMA          20.850
        #  gettime;v=ellan(f,1000000);gettime/1000                  9.238
        #  time v=e.ellan (1000000)                                 9.61
        #  time v=E.anlist(1000000)                                 10.95  (13.171 in cygwin vmware)

        #  time v:=TracesOfFrobenius(E,10000000);  //MAGMA          257.850
        #  gettime;v=ellan(f,10000000);gettime/1000      FAILS no matter how many allocatemem()'s!!
        #  time v=e.ellan (10000000)                                139.37
        #  time v=E.anlist(10000000)                                136.32
        #
        #  The last Sage comp retries with stack size 40MB,
        #  80MB, 160MB, and succeeds last time.  It's very interesting that this
        #  last computation is *not* possible in GP, but works in py_pari!
        #

    def q_expansion(self, prec):
        r"""
        Return the `q`-expansion to precision prec of the newform
        attached to this elliptic curve.

        INPUT:


        -  ``prec`` - an integer


        OUTPUT:

        a power series (in th evariable 'q')

        .. note::

           If you want the output to be a modular form and not just a
           `q`-expansion, use :meth:`.modular_form`.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.q_expansion(20)
            q - 2*q^2 - 3*q^3 + 2*q^4 - 2*q^5 + 6*q^6 - q^7 + 6*q^9 + 4*q^10 - 5*q^11 - 6*q^12 - 2*q^13 + 2*q^14 + 6*q^15 - 4*q^16 - 12*q^18 + O(q^20)
        """
        return PowerSeriesRing(Q, 'q')(self.anlist(prec), prec, check=True)

    def modular_form(self):
        r"""
        Return the cuspidal modular form associated to this elliptic
        curve.

        EXAMPLES::

            sage: E = EllipticCurve('37a')
            sage: f = E.modular_form()
            sage: f
            q - 2*q^2 - 3*q^3 + 2*q^4 - 2*q^5 + O(q^6)

        If you need to see more terms in the `q`-expansion::

            sage: f.q_expansion(20)
            q - 2*q^2 - 3*q^3 + 2*q^4 - 2*q^5 + 6*q^6 - q^7 + 6*q^9 + 4*q^10 - 5*q^11 - 6*q^12 - 2*q^13 + 2*q^14 + 6*q^15 - 4*q^16 - 12*q^18 + O(q^20)

        .. note::

           If you just want the `q`-expansion, use
           :meth:`.q_expansion`.
        """
        try:
            return self.__modular_form
        except AttributeError:
            M = sage.modular.modform.constructor.ModularForms(self.conductor(),weight=2)
            f = sage.modular.modform.element.ModularFormElement_elliptic_curve(M, self)
            self.__modular_form = f
            return f

    def modular_symbol_space(self, sign=1, base_ring=Q, bound=None):
        r"""
        Return the space of cuspidal modular symbols associated to this
        elliptic curve, with given sign and base ring.

        INPUT:


        -  ``sign`` - 0, -1, or 1

        -  ``base_ring`` - a ring


        EXAMPLES::

            sage: f = EllipticCurve('37b')
            sage: f.modular_symbol_space()
            Modular Symbols subspace of dimension 1 of Modular Symbols space of dimension 3 for Gamma_0(37) of weight 2 with sign 1 over Rational Field
            sage: f.modular_symbol_space(-1)
            Modular Symbols subspace of dimension 1 of Modular Symbols space of dimension 2 for Gamma_0(37) of weight 2 with sign -1 over Rational Field
            sage: f.modular_symbol_space(0, bound=3)
            Modular Symbols subspace of dimension 2 of Modular Symbols space of dimension 5 for Gamma_0(37) of weight 2 with sign 0 over Rational Field

        .. note::

           If you just want the `q`-expansion, use
           :meth:`.q_expansion`.
        """
        typ = (sign, base_ring)
        try:
            return self.__modular_symbol_space[typ]
        except AttributeError:
            self.__modular_symbol_space = {}
        except KeyError:
            pass
        M = ell_modular_symbols.modular_symbol_space(self, sign, base_ring, bound=bound)
        self.__modular_symbol_space[typ] = M
        return M

    def modular_symbol(self, sign=1, use_eclib = False, normalize = "L_ratio"):
        r"""
        Return the modular symbol associated to this elliptic curve,
        with given sign and base ring.  This is the map that sends `r/s`
        to a fixed multiple of the integral of `2 \pi I f(z) dz`
        from `\infty` to `r/s`, normalized so that all values of this map take
        values in `\QQ`.

        The normalization is such that for sign +1,
        the value at the cusp 0 is equal to the quotient of L(E,1)
        by the least positive period of E (unlike in ``L_ratio``
        of ``lseries()``, where the value is also divided by the
        number of connected components of E(R)). In particular the
        modular symbol depends on E and not only the isogeny class of E.

        INPUT:

        -  ``sign`` - -1, or 1

        -  ``base_ring`` - a ring

        -  ``normalize`` - (default: True); if True, the
           modular symbol is correctly normalized (up to possibly a factor of
           -1 or 2). If False, the modular symbol is almost certainly not
           correctly normalized, i.e., all values will be a fixed scalar
           multiple of what they should be. But the initial computation of the
           modular symbol is much faster, though evaluation of it after
           computing it won't be any faster.

         - ``use_eclib`` - (default: False); if True the computation is
           done with John Cremona's implementation of modular
           symbols in eclib. But this is only possible for
           sign = +1.

        -  ``normalize`` - (default: 'L_ratio'); either 'L_ratio', 'period', or 'none';
           For 'L_ratio', the modular symbol is correctly normalized
           as explained above by comparing it to L_ratio for the
           curve and some small twists.
           The normalization 'period' is only available if
           use_eclib=False. It uses the integral_period_map for modular
           symbols and is known to be equal to the above normalization
           up to the sign and a possible power of 2.
           For 'none', the modular symbol is almost certainly
           not correctly normalized, i.e. all values will be a
           fixed scalar multiple of what they should be.  But
           the initial computation of the modular symbol is
           much faster if use_eclib=False, though evaluation of
           it after computing it won't be any faster.


        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: M=E.modular_symbol(); M
            Modular symbol with sign 1 over Rational Field attached to Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
            sage: M(1/2)
            0
            sage: M(1/5)
            1

            sage: E=EllipticCurve('121b1')
            sage: M=E.modular_symbol()
            sage: M(1/7)
            2

            sage: E=EllipticCurve('11a1')
            sage: E.modular_symbol()(0)
            1/5
            sage: E=EllipticCurve('11a2')
            sage: E.modular_symbol()(0)
            1
            sage: E=EllipticCurve('11a3')
            sage: E.modular_symbol()(0)
            1/25

            sage: E=EllipticCurve('11a2')
            sage: E.modular_symbol(use_eclib=True, normalize='L_ratio')(0)
            1
            sage: E.modular_symbol(use_eclib=True, normalize='none')(0)
            1/5
            sage: E.modular_symbol(use_eclib=True, normalize='period')(0)
            Traceback (most recent call last):
            ...
            ValueError: no normalization 'period' known for modular symbols using John Cremona's eclib
            sage: E.modular_symbol(use_eclib=False, normalize='L_ratio')(0)
            1
            sage: E.modular_symbol(use_eclib=False, normalize='none')(0)
            1
            sage: E.modular_symbol(use_eclib=False, normalize='period')(0)
            1

            sage: E=EllipticCurve('11a3')
            sage: E.modular_symbol(use_eclib=True, normalize='L_ratio')(0)
            1/25
            sage: E.modular_symbol(use_eclib=True, normalize='none')(0)
            1/5
            sage: E.modular_symbol(use_eclib=True, normalize='period')(0)
            Traceback (most recent call last):
            ...
            ValueError: no normalization 'period' known for modular symbols using John Cremona's eclib
            sage: E.modular_symbol(use_eclib=False, normalize='L_ratio')(0)
            1/25
            sage: E.modular_symbol(use_eclib=False, normalize='none')(0)
            1
            sage: E.modular_symbol(use_eclib=False, normalize='period')(0)
            1/25

        """
        typ = (sign, normalize, use_eclib)
        try:
            return self.__modular_symbol[typ]
        except AttributeError:
            self.__modular_symbol = {}
        except KeyError:
            pass
        if use_eclib :
            M = ell_modular_symbols.ModularSymbolECLIB(self, sign, normalize=normalize)
        else :
            M = ell_modular_symbols.ModularSymbolSage(self, sign, normalize=normalize)
        self.__modular_symbol[typ] = M
        return M

    padic_lseries = padics.padic_lseries

    def newform(self):
        r"""
        Same as ``self.modular_form()``.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.newform()
            q - 2*q^2 - 3*q^3 + 2*q^4 - 2*q^5 + O(q^6)
            sage: E.newform() == E.modular_form()
            True
        """
        return self.modular_form()

    def q_eigenform(self, prec):
        r"""
        Synonym for ``self.q_expansion(prec)``.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.q_eigenform(10)
            q - 2*q^2 - 3*q^3 + 2*q^4 - 2*q^5 + 6*q^6 - q^7 + 6*q^9 + O(q^10)
            sage: E.q_eigenform(10) == E.q_expansion(10)
            True
        """
        return self.q_expansion(prec)

    def analytic_rank(self, algorithm="cremona"):
        r"""
        Return an integer that is *probably* the analytic rank of this
        elliptic curve.

        INPUT:

        - algorithm -

          - 'cremona' (default) - Use the Buhler-Gross algorithm as
            implemented in GP by Tom Womack and John Cremona, who note
            that their implementation is practical for any rank and
            conductor `\leq 10^{10}` in 10 minutes.

          - 'sympow' -use Watkins's program sympow

          - 'rubinstein' - use Rubinstein's L-function C++ program lcalc.

          - 'magma' - use MAGMA

          - 'all' - compute with all other free algorithms, check that
            the answers agree, and return the common answer.

        .. note::

           If the curve is loaded from the large Cremona database,
           then the modular degree is taken from the database.

        Of the three above, probably Rubinstein's is the most
        efficient (in some limited testing I've done).

        .. note::

           It is an open problem to *prove* that *any* particular
           elliptic curve has analytic rank `\geq 4`.

        EXAMPLES::

            sage: E = EllipticCurve('389a')
            sage: E.analytic_rank(algorithm='cremona')
            2
            sage: E.analytic_rank(algorithm='rubinstein')
            2
            sage: E.analytic_rank(algorithm='sympow')
            2
            sage: E.analytic_rank(algorithm='magma')    # optional - magma
            2
            sage: E.analytic_rank(algorithm='all')
            2

        TESTS:

        When the input is horrendous, some of the algorithms just bomb out with a RuntimeError::

            sage: EllipticCurve([1234567,89101112]).analytic_rank(algorithm='rubinstein')
            Traceback (most recent call last):
            ...
            RuntimeError: unable to compute analytic rank using rubinstein algorithm ('unable to convert x (= 6.19283e+19 and is too large) to an integer')
            sage: EllipticCurve([1234567,89101112]).analytic_rank(algorithm='sympow')
            Traceback (most recent call last):
            ...
            RuntimeError: failed to compute analytic rank
        """
        if algorithm == 'cremona':
            return rings.Integer(gp_cremona.ellanalyticrank(self.minimal_model().a_invariants()))
        elif algorithm == 'rubinstein':
            try:
                from sage.lfunctions.lcalc import lcalc
                return lcalc.analytic_rank(L=self)
            except TypeError,msg:
                raise RuntimeError, "unable to compute analytic rank using rubinstein algorithm ('%s')"%msg
        elif algorithm == 'sympow':
            from sage.lfunctions.sympow import sympow
            return sympow.analytic_rank(self)[0]
        elif algorithm == 'magma':
            from sage.interfaces.all import magma
            return rings.Integer(magma(self).AnalyticRank())
        elif algorithm == 'all':
            S = list(set([self.analytic_rank('cremona'),
                     self.analytic_rank('rubinstein'), self.analytic_rank('sympow')]))
            if len(S) != 1:
                raise RuntimeError, "Bug in analytic rank; algorithms don't agree! (E=%s)"%E
            return S[0]
        else:
            raise ValueError, "algorithm %s not defined"%algorithm

    def p_isogenous_curves(self, p=None):
        r"""
        Return a list of pairs `(p, L)` where `p` is a
        prime and `L` is a list of the elliptic curves over
        `\mathbb{Q}` that are `p`-isogenous to this
        elliptic curve.

        INPUT:


        -  ``p`` - prime or None (default: None); if a prime,
           returns a list of the p-isogenous curves. Otherwise, returns a list
           of all prime-degree isogenous curves sorted by isogeny degree.


        This is implemented using Cremona's GP script
        ``allisog.gp``.

        EXAMPLES::

            sage: E = EllipticCurve([0,-1,0,-24649,1355209])
            sage: E.p_isogenous_curves()
            [(2, [Elliptic Curve defined by y^2  = x^3 - x^2 - 91809*x - 9215775 over Rational Field, Elliptic Curve defined by y^2  = x^3 - x^2 - 383809*x + 91648033 over Rational Field, Elliptic Curve defined by y^2  = x^3 - x^2 + 1996*x + 102894 over Rational Field])]

        The isogeny class of the curve 11a2 has three curves in it. But
        ``p_isogenous_curves`` only returns one curves, since
        there is only one curve `5`-isogenous to 11a2.

        ::

            sage: E = EllipticCurve('11a2')
            sage: E.p_isogenous_curves()
            [(5, [Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field])]
            sage: E.p_isogenous_curves(5)
            [Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field]
            sage: E.p_isogenous_curves(3)
            []

        In contrast, the curve 11a1 admits two `5`-isogenies::

            sage: E = EllipticCurve('11a1')
            sage: E.p_isogenous_curves(5)
            [Elliptic Curve defined by y^2 + y = x^3 - x^2 - 7820*x - 263580 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 - x^2 over Rational Field]
        """
        if p is None:
            X = eval(gp_cremona.allisog(self.minimal_model().a_invariants()))
            Y = [(p, [constructor.EllipticCurve(ainvs) for ainvs in L]) for p, L in X]
            Y.sort()
            return Y
        else:
            X = eval(gp_cremona.p_isog(self.minimal_model().a_invariants(), p))
            Y = [constructor.EllipticCurve(ainvs) for ainvs in X]
            Y.sort()
            return Y

    def simon_two_descent(self, verbose=0, lim1=5, lim3=50, limtriv=10, maxprob=20, limbigprime=30):
        r"""
        Given a curve with no 2-torsion, computes (probably) the rank of
        the Mordell-Weil group, with certainty the rank of the 2-Selmer
        group, and a list of independent points on the curve.

        INPUT:


        -  ``verbose`` - integer, 0,1,2,3; (default: 0), the
           verbosity level

        -  ``lim1`` - (default: 5) limite des points triviaux
           sur les quartiques

        -  ``lim3`` - (default: 50) limite des points sur les
           quartiques ELS

        -  ``limtriv`` - (default: 10) limite des points
           triviaux sur la courbe elliptique

        -  ``maxprob`` - (default: 20)

        -  ``limbigprime`` - (default: 30) to distinguish
           between small and large prime numbers. Use probabilistic tests for
           large primes. If 0, don't any probabilistic tests.


        OUTPUT:


        -  ``integer`` - "probably" the rank of self

        -  ``integer`` - the 2-rank of the Selmer group

        -  ``list`` - list of independent points on the
           curve.


        IMPLEMENTATION: Uses Denis Simon's GP/PARI scripts from
        http://www.math.unicaen.fr/~simon/

        EXAMPLES: These computations use pseudo-random numbers, so we set
        the seed for reproducible testing.

        We compute the ranks of the curves of lowest known conductor up to
        rank `8`. Amazingly, each of these computations finishes
        almost instantly!

        ::

            sage: E = EllipticCurve('11a1')
            sage: set_random_seed(0)
            sage: E.simon_two_descent()
            (0, 0, [])
            sage: E = EllipticCurve('37a1')
            sage: set_random_seed(0)
            sage: E.simon_two_descent()
            (1, 1, [(0 : 0 : 1)])
            sage: E = EllipticCurve('389a1')
            sage: set_random_seed(0)
            sage: E.simon_two_descent()
            (2, 2, [(1 : 0 : 1), (-11/9 : -55/27 : 1)])
            sage: E = EllipticCurve('5077a1')
            sage: set_random_seed(0)
            sage: E.simon_two_descent()
            (3, 3, [(1 : 0 : 1), (2 : -1 : 1), (0 : 2 : 1)])

        In this example Simon's program does not find any points, though it
        does correctly compute the rank of the 2-Selmer group.

        ::

            sage: E = EllipticCurve([1, -1, 0, -751055859, -7922219731979])     # long (0.6 seconds)
            sage: set_random_seed(0)
            sage: E.simon_two_descent ()
            (1, 1, [])

        The rest of these entries were taken from Tom Womack's page
        http://tom.womack.net/maths/conductors.htm

        ::

            sage: E = EllipticCurve([1, -1, 0, -79, 289])
            sage: set_random_seed(0)
            sage: E.simon_two_descent()
            (4, 4, [(6 : -5 : 1), (4 : 3 : 1), (5 : -3 : 1), (8 : -15 : 1)])
            sage: E = EllipticCurve([0, 0, 1, -79, 342])
            sage: set_random_seed(0)
            sage: E.simon_two_descent()
            (5, 5, [(5 : 8 : 1), (10 : 23 : 1), (3 : 11 : 1), (4 : -10 : 1), (0 : 18 : 1)])
            sage: E = EllipticCurve([1, 1, 0, -2582, 48720])
            sage: set_random_seed(0)
            sage: r, s, G = E.simon_two_descent(); r,s
            (6, 6)
            sage: E = EllipticCurve([0, 0, 0, -10012, 346900])
            sage: set_random_seed(0)
            sage: r, s, G = E.simon_two_descent(); r,s
            (7, 7)
            sage: E = EllipticCurve([0, 0, 1, -23737, 960366])
            sage: set_random_seed(0)
            sage: r, s, G = E.simon_two_descent(); r,s
            (8, 8)
        """
        t = simon_two_descent(self, verbose=verbose, lim1=lim1, lim3=lim3, limtriv=limtriv,
                              maxprob=maxprob, limbigprime=limbigprime)
        prob_rank = rings.Integer(t[0])
        two_selmer_rank = rings.Integer(t[1])
        prob_gens = [self(P) for P in t[2]]
        return prob_rank, two_selmer_rank, prob_gens

    two_descent_simon = simon_two_descent

    def three_selmer_rank(self, algorithm='UseSUnits'):
        r"""
        Return the 3-selmer rank of this elliptic curve, computed using
        Magma.

        INPUT:


        -  ``algorithm`` - 'Heuristic' (which is usually much
           faster in large examples), 'FindCubeRoots', or 'UseSUnits'
           (default)


        OUTPUT: nonnegative integer

        EXAMPLES: A rank 0 curve::

            sage: EllipticCurve('11a').three_selmer_rank()       # optional - magma
            0

        A rank 0 curve with rational 3-isogeny but no 3-torsion

        ::

            sage: EllipticCurve('14a3').three_selmer_rank()      # optional - magma
            0

        A rank 0 curve with rational 3-torsion::

            sage: EllipticCurve('14a1').three_selmer_rank()      # optional - magma
            1

        A rank 1 curve with rational 3-isogeny::

            sage: EllipticCurve('91b').three_selmer_rank()       # optional - magma
            2

        A rank 0 curve with nontrivial 3-Sha. The Heuristic option makes
        this about twice as fast as without it.

        ::

            sage: EllipticCurve('681b').three_selmer_rank(algorithm='Heuristic')   # long (10 seconds); optional - magma
            2
        """
        from sage.interfaces.all import magma
        E = magma(self)
        return Integer(E.ThreeSelmerGroup(MethodForFinalStep = magma('"%s"'%algorithm)).Ngens())

    def rank(self, use_database=False, verbose=False,
                   only_use_mwrank=True,
                   algorithm='mwrank_shell',
                   proof=None):
        """
        Return the rank of this elliptic curve, assuming no conjectures.

        If we fail to provably compute the rank, raises a RuntimeError
        exception.

        INPUT:


        -  ``use_database (bool)`` - (default: False), if
           True, try to look up the regulator in the Cremona database.

        -  ``verbose`` - (default: None), if specified changes
           the verbosity of mwrank computations. algorithm -

        -  ``- 'mwrank_shell'`` - call mwrank shell command

        -  ``- 'mwrank_lib'`` - call mwrank c library

        -  ``only_use_mwrank`` - (default: True) if False try
           using analytic rank methods first.

        -  ``proof`` - bool or None (default: None, see
           proof.elliptic_curve or sage.structure.proof). Note that results
           obtained from databases are considered proof = True


        OUTPUT:


        -  ``rank (int)`` - the rank of the elliptic curve.


        IMPLEMENTATION: Uses L-functions, mwrank, and databases.

        EXAMPLES::

            sage: EllipticCurve('11a').rank()
            0
            sage: EllipticCurve('37a').rank()
            1
            sage: EllipticCurve('389a').rank()
            2
            sage: EllipticCurve('5077a').rank()
            3
            sage: EllipticCurve([1, -1, 0, -79, 289]).rank()   # long time.  This will use the default proof behavior of True.
            4
            sage: EllipticCurve([0, 0, 1, -79, 342]).rank(proof=False)  # long time -- but under a minute
            5
            sage: EllipticCurve([0, 0, 1, -79, 342]).simon_two_descent()[0]  # much faster -- almost instant.
            5

        Examples with denominators in defining equations::

            sage: E = EllipticCurve( [0, 0, 0, 0, -675/4])
            sage: E.rank()
            0
            sage: E = EllipticCurve( [0, 0, 1/2, 0, -1/5])
            sage: E.rank()
            1
            sage: E.minimal_model().rank()
            1

        A large example where mwrank doesn't determine the result with certainty:
            sage: EllipticCurve([1,0,0,0,37455]).rank(proof=False)
            0
            sage: EllipticCurve([1,0,0,0,37455]).rank(proof=True)
            Traceback (most recent call last):
            ...
            RuntimeError: Rank not provably correct.
        """
        if proof is None:
            from sage.structure.proof.proof import get_flag
            proof = get_flag(proof, "elliptic_curve")
        else:
            proof = bool(proof)
        try:
            return self.__rank[proof]
        except KeyError:
            if proof is False and self.__rank.has_key(True):
                return self.__rank[True]
        if use_database:
            try:
                self.__rank[True] = self.database_curve().rank()
                return self.__rank[True]
            except (AttributeError, RuntimeError):
                pass
        if not only_use_mwrank:
            N = self.conductor()
            prec = int(4*float(sqrt(N))) + 10
            if self.root_number() == 1:
                L, err = self.lseries().at1(prec)
                if abs(L) > err + R(0.0001):  # definitely doesn't vanish
                    misc.verbose("rank 0 because L(E,1)=%s"%L)
                    self.__rank[proof] = 0
                    return self.__rank[proof]
            else:
                Lprime, err = self.lseries().deriv_at1(prec)
                if abs(Lprime) > err + R(0.0001):  # definitely doesn't vanish
                    misc.verbose("rank 1 because L'(E,1)=%s"%Lprime)
                    self.__rank[proof] = 1
                    return self.__rank[proof]

        if algorithm == 'mwrank_lib':
            misc.verbose("using mwrank lib")
            C = self.mwrank_curve()
            C.set_verbose(verbose)
            r = C.rank()
            if not C.certain():
                del self.__mwrank_curve
                raise RuntimeError, "Unable to compute the rank with certainty (lower bound=%s).  This could be because Sha(E/Q)[2] is nontrivial."%C.rank() + "\nTrying calling something like two_descent(second_limit=13) on the curve then trying this command again.  You could also try rank with only_use_mwrank=False."
            self.__rank[proof] = r
        elif algorithm == 'mwrank_shell':
            misc.verbose("using mwrank shell")
            X = self.mwrank()
            if 'determined unconditionally' not in X or 'only a lower bound of' in X:
                if proof:
                    X= "".join(X.split("\n")[-4:-2])
                    print X
                    raise RuntimeError, 'Rank not provably correct.'
                else:
                    misc.verbose("Warning -- rank not proven correct", level=1)

                s = "lower bound of"
                X = X[X.rfind(s)+len(s)+1:]
                r = Integer(X.split()[0])
            else:
                if proof is False:
                    proof = True #since we actually provably found the rank
                match = 'Rank ='
                i = X.find(match)
                if i == -1:
                    match = 'found points of rank'
                    i = X.find(match)
                    if i == -1:
                        raise RuntimeError, "%s\nbug -- tried to find 'Rank =' or 'found points of rank' in mwrank output but couldn't."%X
                j = i + X[i:].find('\n')
                r = Integer(X[i+len(match)+1:j])
            self.__rank[proof] = r

        return self.__rank[proof]

    def gens(self, verbose=False, rank1_search=10,
             algorithm='mwrank_shell',
             only_use_mwrank=True,
             proof = None,
             use_database = True):
        """
        Compute and return generators for the Mordell-Weil group E(Q)
        *modulo* torsion.

        HINT: If you would like to control the height bounds used in the
        2-descent, first call the two_descent function with those height
        bounds. However that function, while it displays a lot of output,
        returns no values.

        TODO: Allow passing of command-line parameters to mwrank.

        .. warning::

           If the program fails to give a provably correct result, it
           prints a warning message, but does not raise an
           exception. Use the gens_certain command to find out if this
           warning message was printed.

        INPUT:


        -  ``verbose`` - (default: None), if specified changes
           the verbosity of mwrank computations.

        -  ``rank1_search`` - (default: 16), if the curve has
           analytic rank 1, try to find a generator by a direct search up to
           this logarithmic height. If this fails the usual mwrank procedure
           is called. algorithm -

        -  ``- 'mwrank_shell' (default)`` - call mwrank shell
           command

        -  ``- 'mwrank_lib'`` - call mwrank c library

        -  ``only_use_mwrank`` - bool (default True) if
           False, attempts to first use more naive, natively implemented
           methods.

        -  ``proof`` - bool or None (default None, see
           proof.elliptic_curve or sage.structure.proof).

        -  ``use_database`` - bool (default True) if True,
           attempts to find curve and gens in the (optional) database


        OUTPUT:


        -  ``generators`` - List of generators for the
           Mordell-Weil group modulo torsion.


        IMPLEMENTATION: Uses Cremona's mwrank C library.

        EXAMPLES::

            sage: E = EllipticCurve('389a')
            sage: E.gens()                 # random output
            [(-1 : 1 : 1), (0 : 0 : 1)]

        A non-integral example::

            sage: E = EllipticCurve([-3/8,-2/3])
            sage: E.gens() # random (up to sign)
            [(10/9 : 29/54 : 1)]

        A non-minimal example::

            sage: E = EllipticCurve('389a1')
            sage: E1 = E.change_weierstrass_model([1/20,0,0,0]); E1
            Elliptic Curve defined by y^2 + 8000*y = x^3 + 400*x^2 - 320000*x over Rational Field
            sage: E1.gens() # random (if database not used)
            [(-400 : 8000 : 1), (0 : -8000 : 1)]
        """
        if proof is None:
            from sage.structure.proof.proof import get_flag
            proof = get_flag(proof, "elliptic_curve")
        else:
            proof = bool(proof)

        # If the gens are already cached, return them:
        try:
            return list(self.__gens[proof])  # return copy so not changed
        except KeyError:
            if proof is False and self.__gens.has_key(True):
                return self.__gens[True]

        # If the optional extended database is installed and an
        # isomorphic curve is in the database then its gens will be
        # known; if only the default database is installed, the rank
        # will be known but not the gens.

        if use_database:
            try:
                E = self.database_curve()
                iso = E.isomorphism_to(self)
                try:
                    self.__gens[True] = [iso(P) for P in E.__gens[True]]
                    return self.__gens[True]
                except KeyError: # database curve does not have the gens
                    pass
            except (RuntimeError, KeyError):  # curve or gens not in database
                pass

        if self.conductor() > 10**7:
            only_use_mwrank = True

        if not only_use_mwrank:
            try:
                misc.verbose("Trying to compute rank.")
                r = self.rank(only_use_mwrank = False)
                misc.verbose("Got r = %s."%r)
                if r == 0:
                    misc.verbose("Rank = 0, so done.")
                    self.__gens[True] = []
                    return self.__gens[True]
                if r == 1 and rank1_search:
                    misc.verbose("Rank = 1, so using direct search.")
                    h = 6
                    while h <= rank1_search:
                        misc.verbose("Trying direct search up to height %s"%h)
                        G = self.point_search(h, verbose)
                        G = [P for P in G if P.order() == oo]
                        if len(G) > 0:
                            misc.verbose("Direct search succeeded.")
                            G, _, _ = self.saturation(G, verbose=verbose)
                            misc.verbose("Computed saturation.")
                            self.__gens[True] = G
                            return self.__gens[True]
                        h += 2
                    misc.verbose("Direct search FAILED.")
            except RuntimeError:
                pass
        # end if (not_use_mwrank)
        if algorithm == "mwrank_lib":
            misc.verbose("Calling mwrank C++ library.")
            C = self.mwrank_curve(verbose)
            if not (verbose is None):
                C.set_verbose(verbose)
            G = C.gens()
            if proof is True and C.certain() is False:
                del self.__mwrank_curve
                raise RuntimeError, "Unable to compute the rank, hence generators, with certainty (lower bound=%s, generators found=%s).  This could be because Sha(E/Q)[2] is nontrivial."%(C.rank(),G) + \
                      "\nTrying calling something like two_descent(second_limit=13) on the curve then trying this command again."
            else:
                proof = C.certain()
        else:
            # when gens() calls mwrank it passes the command-line
            # parameter "-p 100" which helps curves with large
            # coefficients and 2-torsion and is otherwise harmless.
            # This is pending a more intelligent handling of mwrank
            # options in gens() (which is nontrivial since gens() needs
            # to parse the output from mwrank and this is seriously
            # affected by what parameters the user passes!).
            # In fact it would be much better to avoid the mwrank console at
            # all for gens() and just use the library. This is in
            # progress (see trac #1949).
            X = self.mwrank('-p 100')
            misc.verbose("Calling mwrank shell.")
            if not 'The rank and full Mordell-Weil basis have been determined unconditionally' in X:
                msg = 'Generators not provably computed.'
                if proof:
                    raise RuntimeError, '%s\n%s'%(X,msg)
                else:
                    misc.verbose("Warning -- %s"%msg, level=1)
            elif proof is False:
                proof = True
            G = []
            i = X.find('Generator ')
            while i != -1:
                j = i + X[i:].find(';')
                k = i + X[i:].find('[')
                G.append(eval(X[k:j].replace(':',',')))
                X = X[j:]
                i = X.find('Generator ')
        ####
        self.__gens[proof] = [self.point(x, check=True) for x in G]
        self.__gens[proof].sort()
        self.__rank[proof] = len(self.__gens[proof])
        return self.__gens[proof]

    def gens_certain(self):
        """
       Return True if the generators have been proven correct.

       EXAMPLES::

           sage: E=EllipticCurve('37a1')
           sage: E.gens()                   # random (up to sign)
           [(0 : -1 : 1)]
           sage: E.gens_certain()
           True
       """
        return self.__gens.has_key(True)

    def ngens(self, proof = None):
        """
        Return the number of generators of this elliptic curve.

        .. note::

           See :meth:'.gens' for further documentation. The function
           :meth:`.ngens` calls :meth:`.gens` if not already done, but
           only with default parameters.  Better results may be
           obtained by calling ``mwrank()`` with carefully chosen
           parameters.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.ngens()
            1

        TO DO: This example should not cause a run-time error.

        ::

            sage: E=EllipticCurve([0,0,0,877,0])
            sage: # E.ngens()  ######## causes run-time error

        ::

            sage: print E.mwrank('-v0 -b12 -l')
            Curve [0,0,0,877,0] :   Rank = 1
            Generator 1 is [29604565304828237474403861024284371796799791624792913256602210:-256256267988926809388776834045513089648669153204356603464786949:490078023219787588959802933995928925096061616470779979261000]; height 95.980371987964
            Regulator = 95.980...
        """
        return len(self.gens(proof = proof))

    def regulator(self, use_database=True, proof=None, precision=None):
        """
        Returns the regulator of this curve, which must be defined over Q.

        INPUT:


        -  ``use_database`` - bool (default: False), if True,
           try to look up the generators in the Cremona database.

        -  ``proof`` - bool or None (default: None, see
           proof.[tab] or sage.structure.proof). Note that results from
           databases are considered proof = True

        -  ``precision`` - int or None (default: None): the
           precision in bits of the result (default real precision if None)


        EXAMPLES::

            sage: E = EllipticCurve([0, 0, 1, -1, 0])
            sage: E.regulator()              # long time (1 second)
            0.0511114082399688
            sage: EllipticCurve('11a').regulator()
            1.00000000000000
            sage: EllipticCurve('37a').regulator()
            0.0511114082399688
            sage: EllipticCurve('389a').regulator()
            0.152460177943144
            sage: EllipticCurve('5077a').regulator()
            0.41714355875838...
            sage: EllipticCurve([1, -1, 0, -79, 289]).regulator()  # long time (seconds)
            1.50434488827528
            sage: EllipticCurve([0, 0, 1, -79, 342]).regulator(proof=False)  # long time (seconds)
            14.790527570131...
        """
        if precision is None:
            RR = rings.RealField()
            precision = RR.precision()
        else:
            RR = rings.RealField(precision)

        if proof is None:
            from sage.structure.proof.proof import get_flag
            proof = get_flag(proof, "elliptic_curve")
        else:
            proof = bool(proof)

        # We return a cached value if it exists and has sufficient precision:
        try:
            reg = self.__regulator[proof]
            if reg.parent().precision() >= precision:
                return RR(reg)
            else: # Found regulator value but precision is too low
                pass
        except KeyError:
            if proof is False and self.__regulator.has_key(True):
                reg = self.__regulator[True]
                if reg.parent().precision() >= precision:
                    return RR(reg)
                else: # Found regulator value but precision is too low
                    pass

        # Next we find the gens, taking them from the database if they
        # are there and use_database is True, else computing them:

        G = self.gens(proof=proof, use_database=use_database)

        # Finally compute the regulator of the generators found:

        self.__regulator[proof] = self.regulator_of_points(G,precision=precision)
        return self.__regulator[proof]

    def height_pairing_matrix(self, points=None, precision=None):
        """
        Returns the height pairing matrix of the given points on this
        curve, which must be defined over Q.

        INPUT:

        points - either a list of points, which must be on this curve, or
        (default) None, in which case self.gens() will be used. precision -
        number of bits of precision of result (default: None, for default
        RealField precision)

        EXAMPLES::

            sage: E = EllipticCurve([0, 0, 1, -1, 0])
            sage: E.height_pairing_matrix()
            [0.0511114082399688]

        For rank 0 curves, the result is a valid 0x0 matrix::

            sage: EllipticCurve('11a').height_pairing_matrix()
            []
            sage: E=EllipticCurve('5077a1')
            sage: E.height_pairing_matrix([E.lift_x(x) for x in [-2,-7/4,1]], precision=100)
            [  1.3685725053539301120518194471  -1.3095767070865761992624519454 -0.63486715783715592064475542573]
            [ -1.3095767070865761992624519454   2.7173593928122930896610589220   1.0998184305667292139777571432]
            [-0.63486715783715592064475542573   1.0998184305667292139777571432  0.66820516565192793503314205089]
        """
        if points is None:
            points = self.gens()
        else:
            for P in points:
                assert P.curve() == self

        r = len(points)
        if precision is None:
            RR = rings.RealField()
        else:
            RR = rings.RealField(precision)
        M = matrix.MatrixSpace(RR, r)
        mat = M()
        for j in range(r):
            mat[j,j] = points[j].height(precision=precision)
        for j in range(r):
            for k in range(j+1,r):
                mat[j,k]=((points[j]+points[k]).height(precision=precision) - mat[j,j] - mat[k,k])/2
                mat[k,j]=mat[j,k]
        return mat

    def regulator_of_points(self, points=[], precision=None):
        """
        Returns the regulator of the given points on this curve.

        INPUT:

        - ``points`` -(default: empty list)  a list of points on this curve

        - ``precision`` - int or None (default: None): the precision
          in bits of the result (default real precision if None)

        EXAMPLES::

            sage: E = EllipticCurve('37a1')
            sage: P = E(0,0)
            sage: Q = E(1,0)
            sage: E.regulator_of_points([P,Q])
            0.000000000000000
            sage: 2*P==Q
            True

        ::

            sage: E = EllipticCurve('5077a1')
            sage: points = [E.lift_x(x) for x in [-2,-7/4,1]]
            sage: E.regulator_of_points(points)
            0.417143558758384
            sage: E.regulator_of_points(points,precision=100)
            0.41714355875838396981711954462

        ::

            sage: E = EllipticCurve('389a')
            sage: E.regulator_of_points()
            1.00000000000000
            sage: points = [P,Q] = [E(-1,1),E(0,-1)]
            sage: E.regulator_of_points(points)
            0.152460177943144
            sage: E.regulator_of_points(points, precision=100)
            0.15246017794314375162432475705
            sage: E.regulator_of_points(points, precision=200)
            0.15246017794314375162432475704945582324372707748663081784028
            sage: E.regulator_of_points(points, precision=300)
            0.152460177943143751624324757049455823243727077486630817840280980046053225683562463604114816
        """
        if points is None:
            points = []
        mat = self.height_pairing_matrix(points=points, precision=precision)
        return mat.det()


    def saturation(self, points, verbose=False, max_prime=0, odd_primes_only=False):
        """
        Given a list of rational points on E, compute the saturation in
        E(Q) of the subgroup they generate.

        INPUT:


        -  ``points (list)`` - list of points on E

        -  ``verbose (bool)`` - (default: False), if True, give
           verbose output

        -  ``max_prime (int)`` - (default: 0), saturation is
           performed for all primes up to max_prime. If max_prime==0,
           perform saturation at *all* primes, i.e., compute the true
           saturation.

        -  ``odd_primes_only (bool)`` - only do saturation at
           odd primes


        OUTPUT:


        -  ``saturation (list)`` - points that form a basis for
           the saturation

        -  ``index (int)`` - the index of the group generated
           by points in their saturation

        -  ``regulator (real with default precision)`` -
           regulator of saturated points.


        IMPLEMENTATION: Uses Cremona's mwrank package. With max_prime=0,
        we call mwrank with successively larger prime bounds until the full
        saturation is provably found. The results of saturation at the
        previous primes is stored in each case, so this should be
        reasonably fast.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: P=E(0,0)
            sage: Q=5*P; Q
            (1/4 : -5/8 : 1)
            sage: E.saturation([Q])
            ([(0 : 0 : 1)], '5', 0.0511114075779915)
        """
        if not isinstance(points, list):
            raise TypeError, "points (=%s) must be a list."%points

        v = []
        for P in points:
            if not isinstance(P, ell_point.EllipticCurvePoint_field):
                P = self(P)
            elif P.curve() != self:
                raise ArithmeticError, "point (=%s) must be %s."%(P,self)
            x, y = P.xy()
            d = x.denominator().lcm(y.denominator())
            v.append((x*d, y*d, d))
        c = self.mwrank_curve()
        mw = mwrank.mwrank_MordellWeil(c, verbose)
        mw.process(v)
        if max_prime == 0:
            repeat_until_saturated = True
            max_prime = 97
        while True:
            ok, index, unsat = mw.saturate(max_prime=max_prime, odd_primes_only = odd_primes_only)
            reg = mw.regulator()
            if not ok and repeat_until_saturated:
                max_prime = arith.next_prime(max_prime + 100)
                ok, index, unsat = mw.saturate(max_prime=max_prime, odd_primes_only = odd_primes_only)
                reg = mw.regulator()
            else:
                break
        sat = mw.points()
        sat = [self(P) for P in sat]
        return sat, index, R(reg)

    def CPS_height_bound(self):
        """
        Return the Cremona-Prickett-Siksek height bound. This is a floating
        point number B such that if P is a point on the curve, then the
        naive logarithmic height of P differs from the canonical height by
        at most B.

        EXAMPLES::

            sage: E = EllipticCurve("11a")
            sage: E.CPS_height_bound()
            2.8774743273580445
            sage: E = EllipticCurve("5077a")
            sage: E.CPS_height_bound()
            0.0
            sage: E = EllipticCurve([1,2,3,4,1])
            sage: E.CPS_height_bound()
            Traceback (most recent call last):
            ...
            RuntimeError: curve must be minimal.
            sage: F = E.quadratic_twist(-19)
            sage: F
            Elliptic Curve defined by y^2 + x*y + y = x^3 - x^2 + 1376*x - 130 over Rational Field
            sage: F.CPS_height_bound()
            0.65551583769728516

        IMPLEMENTATION:

        Call the corresponding mwrank C++ library function.
        """
        if not self.is_minimal():
            raise RuntimeError, "curve must be minimal."
        return self.mwrank_curve().CPS_height_bound()


    def silverman_height_bound(self):
        r""" Return the Silverman height bound.  This is a positive real
        (floating point) number B such that for all rational points
        `P` on the curve,

        .. math::

                          h(P) \le \hat{h}(P) + B


        where h(P) is the logarithmic height of `P` and
        `\hat{h}(P)` is the canonical height.

        Note that the CPS_height_bound is often better (i.e. smaller)
        than the Silverman bound.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.silverman_height_bound()
            4.8254007581809182
            sage: E.CPS_height_bound()
            0.16397076103046915
        """
        return self.mwrank_curve().silverman_bound()


    def point_search(self, height_limit, verbose=True):
        """
        Search for points on a curve up to an input bound on the naive
        logarithmic height.

        INPUT:


        -  ``height_limit (float)`` - bound on naive height
           (at most 21,

        -  ``or mwrank overflows`` - see below)

        -  ``verbose (bool)`` - (default: True)

           If True, report on each point as found together with linear
           relations between the points found and the saturation process.

           If False, just return the result.


        OUTPUT: points (list) - list of independent points which generate
        the subgroup of the Mordell-Weil group generated by the points
        found and then p-saturated for p20.

        .. warning::

           height_limit is logarithmic, so increasing by 1 will cause
           the running time to increase by a factor of approximately
           4.5 (=exp(1.5)). The limit of 21 is to prevent overflow,
           but in any case using height_limit=20 takes rather a long
           time!

        IMPLEMENTATION: Uses Cremona's mwrank package. At the heart of this
        function is Cremona's port of Stoll's ratpoints program (version
        1.4).

        EXAMPLES::

            sage: E=EllipticCurve('389a1')
            sage: E.point_search(5, verbose=False)
            [(0 : -1 : 1), (-1 : 1 : 1)]

        Increasing the height_limit takes longer, but finds no more
        points::

            sage: E.point_search(10, verbose=False)
            [(0 : -1 : 1), (-1 : 1 : 1)]

        In fact this curve has rank 2 so no more than 2 points will ever be
        output, but we are not using this fact.

        ::

            sage: E.saturation(_)
            ([(0 : -1 : 1), (-1 : 1 : 1)], '1', 0.152460172772408)

        What this shows is that if the rank is 2 then the points listed do
        generate the Mordell-Weil group (mod torsion). Finally,

        ::

            sage: E.rank()
            2
        """
        height_limit = float(height_limit)
        if height_limit > _MAX_HEIGHT:
            raise OverflowError, "height_limit (=%s) must be at most %s."%(height_limit,_MAX_HEIGHT)
        c = self.mwrank_curve()
        mw = mwrank.mwrank_MordellWeil(c, verbose)
        mw.search(height_limit, verbose=verbose)
        v = mw.points()
        return [self(P) for P in v]

    def two_torsion_rank(self):
        r"""
        Return the dimension of the 2-torsion subgroup of
        `E(\mathbb{Q})`.

        This will be 0, 1 or 2.

        .. note::

           As a side-effect of calling this function, the full torsion
           subgroup of the curve is computed (if not already
           cached). A simpler implementation of this function would be
           possible (by counting the roots of the 2-division
           polynomial), but the full torsion subgroup computation is
           not expensive.

        EXAMPLES::

            sage: EllipticCurve('11a1').two_torsion_rank()
            0
            sage: EllipticCurve('14a1').two_torsion_rank()
            1
            sage: EllipticCurve('15a1').two_torsion_rank()
            2
        """
        A = self.torsion_subgroup().invariants()
        if len(A) == 2:
            return rings.Integer(2)
        elif len(A) == 1 and A[0] % 2 == 0:
            return rings.Integer(1)
        else:
            return rings.Integer(0)

    def selmer_rank_bound(self):
        """
        Bound on the rank of the curve, computed using the 2-selmer group.
        This is the rank of the curve minus the rank of the 2-torsion,
        minus a number determined by whatever mwrank was able to determine
        related to Sha[2]. Thus in many cases, this is the actual rank of
        the curve.

        EXAMPLE: The following is the curve 960D1, which has rank 0, but
        Sha of order 4.

        ::

            sage: E = EllipticCurve([0, -1, 0, -900, -10098])
            sage: E.selmer_rank_bound()
            0

        It gives 0 instead of 2, because it knows Sha is nontrivial. In
        contrast, for the curve 571A, also with rank 0 and Sha of order 4,
        we get a worse bound::

            sage: E = EllipticCurve([0, -1, 1, -929, -10595])
            sage: E.selmer_rank_bound()
            2
            sage: E.rank(only_use_mwrank=False)   # uses L-function
            0
        """
        try:
            return self.__selmer_rank_bound
        except AttributeError:
            C = self.mwrank_curve()
            self.__selmer_rank_bound = C.selmer_rank_bound()
            return self.__selmer_rank_bound


    def an(self, n):
        """
        The n-th Fourier coefficient of the modular form corresponding to
        this elliptic curve, where n is a positive integer.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: [E.an(n) for n in range(20) if n>0]
            [1, -2, -3, 2, -2, 6, -1, 0, 6, 4, -5, -6, -2, 2, 6, -4, 0, -12, 0]
        """
        return Integer(self.pari_mincurve().ellak(n))

    def ap(self, p):
        """
        The p-th Fourier coefficient of the modular form corresponding to
        this elliptic curve, where p is prime.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: [E.ap(p) for p in prime_range(50)]
            [-2, -3, -2, -1, -5, -2, 0, 0, 2, 6, -4, -1, -9, 2, -9]
        """
        if not arith.is_prime(p):
            raise ArithmeticError, "p must be prime"
        return Integer(self.pari_mincurve().ellap(p))

    def quadratic_twist(self, D):
        """
       Return the quadratic twist of this elliptic curve by D.

       D must be a nonzero rational number.

       .. note::

          This function overrides the generic ``quadratic_twist()``
          function for elliptic curves, returning a minimal model.

       EXAMPLES::

           sage: E=EllipticCurve('37a1')
           sage: E2=E.quadratic_twist(2); E2
           Elliptic Curve defined by y^2  = x^3 - 4*x + 2 over Rational Field
           sage: E2.conductor()
           2368
           sage: E2.quadratic_twist(2) == E
           True
       """
        return EllipticCurve_number_field.quadratic_twist(self, D).minimal_model()

    def minimal_model(self):
        r"""
        Return the unique minimal Weierstrass equation for this elliptic
        curve. This is the model with minimal discriminant and
        `a_1,a_2,a_3 \in \{0,\pm 1\}`.

        EXAMPLES::

            sage: E=EllipticCurve([10,100,1000,10000,1000000])
            sage: E.minimal_model()
            Elliptic Curve defined by y^2 + x*y + y = x^3 + x^2 + x + 1 over Rational Field
        """
        try:
            return self.__minimal_model
        except AttributeError:
            F = self.pari_mincurve()
            self.__minimal_model = EllipticCurve_rational_field([Q(F[i]) for i in range(5)])
            return self.__minimal_model

    def is_minimal(self):
        r"""
        Return True iff this elliptic curve is a reduced minimal model.

        The unique minimal Weierstrass equation for this elliptic curve.
        This is the model with minimal discriminant and
        `a_1,a_2,a_3 \in \{0,\pm 1\}`.

        TO DO: This is not very efficient since it just computes the
        minimal model and compares. A better implementation using the Kraus
        conditions would be preferable.

        EXAMPLES::

            sage: E=EllipticCurve([10,100,1000,10000,1000000])
            sage: E.is_minimal()
            False
            sage: E=E.minimal_model()
            sage: E.is_minimal()
            True
        """
        return self.ainvs() == self.minimal_model().ainvs()

    def is_p_minimal(self, p):
        """
        Tests if curve is p-minimal at a given prime p.

        INPUT: p - a primeOUTPUT: True - if curve is p-minimal


        -  ``False`` - if curve isn't p-minimal


        EXAMPLES::

            sage: E = EllipticCurve('441a2')
            sage: E.is_p_minimal(7)
            True

        ::

            sage: E = EllipticCurve([0,0,0,0,(2*5*11)**10])
            sage: [E.is_p_minimal(p) for p in prime_range(2,24)]
            [False, True, False, True, False, True, True, True, True]
        """
        if not p.is_prime():
            raise ValueError,"p must be prime"
        if not self.is_p_integral(p):
            return False
        if p > 3:
            return ((self.discriminant().valuation(p) < 12) or (self.c4().valuation(p) < 4))
        # else p = 2,3
        Emin = self.minimal_model()
        return self.discriminant().valuation(p) == Emin.discriminant().valuation(p)

#    Duplicate!
#
#    def is_integral(self):
#        for n in self.ainvs():
#            if n.denominator() != 1:
#                return False
#        return True

    def kodaira_type(self, p):
        """
        Local Kodaira type of the elliptic curve at `p`.

        INPUT:

        -   p, an integral prime


        OUTPUT:


        - the Kodaira type of this elliptic curve at p,
          as a KodairaSymbol.


        EXAMPLES::

            sage: E = EllipticCurve('124a')
            sage: E.kodaira_type(2)
            IV
        """
        return self.local_data(p).kodaira_symbol()

    kodaira_symbol = kodaira_type

    def kodaira_type_old(self, p):
        """
        Local Kodaira type of the elliptic curve at `p`.

        INPUT:


        -   p, an integral prime


        OUTPUT:

        - the kodaira type of this elliptic curve at p,
          as a KodairaSymbol.

        EXAMPLES::

            sage: E = EllipticCurve('124a')
            sage: E.kodaira_type_old(2)
            IV
        """
        if not arith.is_prime(p):
            raise ArithmeticError, "p must be prime"
        try:
            self.__kodaira_type
        except AttributeError:
            self.__kodaira_type = {}
            self.__tamagawa_number = {}
        if not self.__kodaira_type.has_key(p):
            v = self.pari_mincurve().elllocalred(p)
            from kodaira_symbol import KodairaSymbol
            self.__kodaira_type[p] = KodairaSymbol(v[1])
            self.__tamagawa_number[p] = Integer(v[3])
        return self.__kodaira_type[p]

    def tamagawa_number(self, p):
        r"""
        The Tamagawa number of the elliptic curve at `p`.

        This is the order of the component group
        `E(\mathbb{Q}_p)/E^0(\mathbb{Q}_p)`.

        EXAMPLES::

            sage: E = EllipticCurve('11a')
            sage: E.tamagawa_number(11)
            5
            sage: E = EllipticCurve('37b')
            sage: E.tamagawa_number(37)
            3
        """
        return self.local_data(p).tamagawa_number()

    def tamagawa_number_old(self, p):
        r"""
        The Tamagawa number of the elliptic curve at `p`.

        This is the order of the component group
        `E(\mathbb{Q}_p)/E^0(\mathbb{Q}_p)`.

        EXAMPLES::

            sage: E = EllipticCurve('11a')
            sage: E.tamagawa_number_old(11)
            5
            sage: E = EllipticCurve('37b')
            sage: E.tamagawa_number_old(37)
            3
        """
        if not arith.is_prime(p):
            raise ArithmeticError, "p must be prime"
        try:
            return self.__tamagawa_number[p]
        except (AttributeError, KeyError):
            self.kodaira_type_old(p)
            return self.__tamagawa_number[p]

    def tamagawa_exponent(self, p):
        """
        The Tamagawa index of the elliptic curve at `p`.

        This is the index of the component group
        `E(\mathbb{Q}_p)/E^0(\mathbb{Q}_p)`. It equals the
        Tamagawa number (as the component group is cyclic) except for types
        `I_m^*` (`m` even) when the group can be
        `C_2 \times C_2`.

        EXAMPLES::

            sage: E = EllipticCurve('816a1')
            sage: E.tamagawa_number(2)
            4
            sage: E.tamagawa_exponent(2)
            2
            sage: E.kodaira_symbol(2)
            I2*

        ::

            sage: E = EllipticCurve('200c4')
            sage: E.kodaira_symbol(5)
            I4*
            sage: E.tamagawa_number(5)
            4
            sage: E.tamagawa_exponent(5)
            2

        See #4715::

            sage: E=EllipticCurve('117a3')
            sage: E.tamagawa_exponent(13)
            4
        """
        if not arith.is_prime(p):
            raise ArithmeticError, "p must be prime"
        cp = self.tamagawa_number(p)
        if not cp==4:
            return cp
        ks = self.kodaira_type(p)
        if ks._roman==1 and ks._n%2==0 and ks._starred:
            return 2
        return 4

    def tamagawa_numbers(self):
        """
        Return a list of all Tamagawa numbers for all prime divisors of the
        conductor (in order).

        EXAMPLES::

            sage: e = EllipticCurve('30a1')
            sage: e.tamagawa_numbers()
            [2, 3, 1]
            sage: vector(e.tamagawa_numbers())
            (2, 3, 1)
        """
        return [self.tamagawa_number(p) for p in arith.prime_divisors(self.conductor())]

    def tamagawa_product(self):
        """
        Returns the product of the Tamagawa numbers.

        EXAMPLES::

            sage: E = EllipticCurve('54a')
            sage: E.tamagawa_product ()
            3
        """
        try:
            return self.__tamagawa_product
        except AttributeError:
            self.__tamagawa_product = Integer(self.pari_mincurve().ellglobalred()[2].python())
            return self.__tamagawa_product

    def real_components(self):
        """
        Returns 1 if there is 1 real component and 2 if there are 2.

        EXAMPLES::

            sage: E = EllipticCurve('37a')
            sage: E.real_components ()
            2
            sage: E = EllipticCurve('37b')
            sage: E.real_components ()
            2
            sage: E = EllipticCurve('11a')
            sage: E.real_components ()
            1
        """
        invs = self.short_weierstrass_model().ainvs()
        x = rings.polygen(self.base_ring())
        f = x**3 + invs[3]*x + invs[4]
        if f.discriminant() > 0:
            return 2
        else:
            return 1

    def period_lattice(self, embedding=None):
        r"""
        Returns the period lattice of the elliptic curve.

        INPUT:


        -  ``embedding`` - ignored (for compatibility with the
           period_lattice function for elliptic_curve_number_field)


        EXAMPLES::

            sage: E = EllipticCurve('37a')
            sage: E.period_lattice()
            Period lattice associated to Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
        """
        from sage.schemes.elliptic_curves.period_lattice import PeriodLattice_ell
        return PeriodLattice_ell(self)

    def lseries(self):
        """
        Returns the L-series of this elliptic curve.

        Further documentation is available for the functions which apply to
        the L-series.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.lseries()
            Complex L-series of the Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
        """
        try:
            return self.__lseries
        except AttributeError:
            from lseries_ell import Lseries_ell
            self.__lseries = Lseries_ell(self)
            return self.__lseries

    def Lambda(self, s, prec):
        r"""
        Returns the value of the Lambda-series of the elliptic curve E at
        s, where s can be any complex number.

        IMPLEMENTATION: Fairly *slow* computation using the definitions
        and implemented in Python.

        Uses prec terms of the power series.

        EXAMPLES::

            sage: E = EllipticCurve('389a')
            sage: E.Lambda(1.4+0.5*I, 50)
            -0.354172680517... + 0.874518681720...*I
        """
        s = C(s)
        N = self.conductor()
        pi = R(constants.pi)
        from sage.calculus.calculus import gamma as Gamma
        Gamma_inc = transcendental.gamma_inc
        a = self.anlist(prec)
        eps = self.root_number()
        sqrtN = float(N.sqrt())
        def _F(n, t):
            return Gamma_inc(t+1, 2*pi*n/sqrtN) * C(sqrtN/(2*pi*n))**(t+1)
        return sum([a[n]*(_F(n,s-1) + eps*_F(n,1-s)) for n in xrange(1,prec+1)])

    def is_local_integral_model(self,*p):
        r"""
        Tests if self is integral at the prime `p`, or at all the
        primes if `p` is a list or tuple of primes

        EXAMPLES::

            sage: E=EllipticCurve([1/2,1/5,1/5,1/5,1/5])
            sage: [E.is_local_integral_model(p) for p in (2,3,5)]
            [False, True, False]
            sage: E.is_local_integral_model(2,3,5)
            False
            sage: Eint2=E.local_integral_model(2)
            sage: Eint2.is_local_integral_model(2)
            True
        """
        if len(p)==1: p=p[0]
        if isinstance(p,(tuple,list)):
            return misc.forall(p, lambda x : self.is_local_integral_model(x))[0]
        assert p.is_prime(), "p must be prime in is_local_integral_model()"
        return misc.forall(self.ainvs(), lambda x : x.valuation(p) >= 0)[0]

    def local_integral_model(self,p):
        r"""
        Return a model of self which is integral at the prime `p`.

        EXAMPLES::

            sage: E=EllipticCurve([0, 0, 1/216, -7/1296, 1/7776])
            sage: E.local_integral_model(2)
            Elliptic Curve defined by y^2 + 1/27*y = x^3 - 7/81*x + 2/243 over Rational Field
            sage: E.local_integral_model(3)
            Elliptic Curve defined by y^2 + 1/8*y = x^3 - 7/16*x + 3/32 over Rational Field
            sage: E.local_integral_model(2).local_integral_model(3) == EllipticCurve('5077a1')
            True
        """
        assert p.is_prime(), "p must be prime in local_integral_model()"
        ai = self.a_invariants()
        e  = min([(ai[i].valuation(p)/[1,2,3,4,6][i]) for i in range(5)]).floor()
        return constructor.EllipticCurve([ai[i]/p**(e*[1,2,3,4,6][i]) for i in range(5)])

    def is_global_integral_model(self):
        r"""
        Return true iff self is integral at all primes.

        EXAMPLES::

            sage: E=EllipticCurve([1/2,1/5,1/5,1/5,1/5])
            sage: E.is_global_integral_model()
            False
            sage: Emin=E.global_integral_model()
            sage: Emin.is_global_integral_model()
            True
        """
        return self.is_integral()

    def global_integral_model(self):
        r"""
        Return a model of self which is integral at all primes.

        EXAMPLES::

            sage: E = EllipticCurve([0, 0, 1/216, -7/1296, 1/7776])
            sage: F = E.global_integral_model(); F
            Elliptic Curve defined by y^2 + y = x^3 - 7*x + 6 over Rational Field
            sage: F == EllipticCurve('5077a1')
            True
        """
        ai = self.a_invariants()
        for a in ai:
            if not a.is_integral():
               for p, _ in a.denom().factor():
                  e  = min([(ai[i].valuation(p)/[1,2,3,4,6][i]) for i in range(5)]).floor()
                  ai = [ai[i]/p**(e*[1,2,3,4,6][i]) for i in range(5)]
        for z in ai:
            assert z.denominator() == 1, "bug in global_integral_model: %s" % ai
        return constructor.EllipticCurve(ai)

    integral_model = global_integral_model

    def integral_short_weierstrass_model(self):
        r"""
        Return a model of the form `y^2 = x^3 + a*x + b` for this
        curve with `a,b\in\mathbb{Z}`.

        EXAMPLES::

            sage: E = EllipticCurve('17a1')
            sage: E.integral_short_weierstrass_model()
            Elliptic Curve defined by y^2  = x^3 - 11*x - 890 over Rational Field
        """
        F = self.minimal_model().short_weierstrass_model()
        _,_,_,A,B = F.ainvs()
        for p in [2,3]:
            e=min(A.valuation(p)/4,B.valuation(p)/6).floor()
            A /= Integer(p**(4*e))
            B /= Integer(p**(6*e))
        return constructor.EllipticCurve([A,B])

    # deprecated function replaced by integral_short_weierstrass_model, see trac 3974.
    def integral_weierstrass_model(self):
        r"""
        Return a model of the form `y^2 = x^3 + a*x + b` for this
        curve with `a,b\in\mathbb{Z}`.

        Note that this function is deprecated, and that you should use
        integral_short_weierstrass_model instead as this will be
        disappearing in the near future.

        EXAMPLES::

            sage: E = EllipticCurve('17a1')
            sage: E.integral_weierstrass_model() #random
            doctest:1: DeprecationWarning: integral_weierstrass_model is deprecated, use integral_short_weierstrass_model instead!
            Elliptic Curve defined by y^2  = x^3 - 11*x - 890 over Rational Field
        """
        from sage.misc.misc import deprecation
        deprecation("integral_weierstrass_model is deprecated, use integral_short_weierstrass_model instead!")
        return self.integral_short_weierstrass_model()


    def modular_degree(self, algorithm='sympow'):
        r"""
        Return the modular degree of this elliptic curve.

        The result is cached. Subsequent calls, even with a different
        algorithm, just returned the cached result.

        INPUT:


        -  ``algorithm`` - string:

        -  ``'sympow'`` - (default) use Mark Watkin's (newer) C
           program sympow

        -  ``'magma'`` - requires that MAGMA be installed (also
           implemented by Mark Watkins)


        .. note::

           On 64-bit computers ec does not work, so Sage uses sympow
           even if ec is selected on a 64-bit computer.

        The correctness of this function when called with algorithm "sympow"
        is subject to the following three hypothesis:


        -  Manin's conjecture: the Manin constant is 1

        -  Steven's conjecture: the `X_1(N)`-optimal quotient is
           the curve with minimal Faltings height. (This is proved in most
           cases.)

        -  The modular degree fits in a machine double, so it better be
           less than about 50-some bits. (If you use sympow this constraint
           does not apply.)


        Moreover for all algorithms, computing a certain value of an
        `L`-function "uses a heuristic method that discerns when
        the real-number approximation to the modular degree is within
        epsilon [=0.01 for algorithm="sympow"] of the same integer for 3
        consecutive trials (which occur maybe every 25000 coefficients or
        so). Probably it could just round at some point. For rigour, you
        would need to bound the tail by assuming (essentially) that all the
        `a_n` are as large as possible, but in practise they
        exhibit significant (square root) cancellation. One difficulty is
        that it doesn't do the sum in 1-2-3-4 order; it uses
        1-2-4-8--3-6-12-24-9-18- (Euler product style) instead, and so you
        have to guess ahead of time at what point to curtail this
        expansion." (Quote from an email of Mark Watkins.)

        .. note::

           If the curve is loaded from the large Cremona database,
           then the modular degree is taken from the database.

        EXAMPLES::

            sage: E = EllipticCurve([0, -1, 1, -10, -20])
            sage: E
            Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field
            sage: E.modular_degree()
            1
            sage: E = EllipticCurve('5077a')
            sage: E.modular_degree()
            1984
            sage: factor(1984)
            2^6 * 31

        ::

            sage: EllipticCurve([0, 0, 1, -7, 6]).modular_degree()
            1984
            sage: EllipticCurve([0, 0, 1, -7, 6]).modular_degree(algorithm='sympow')
            1984
            sage: EllipticCurve([0, 0, 1, -7, 6]).modular_degree(algorithm='magma')  # optional - magma
            1984

        We compute the modular degree of the curve with rank 4 having
        smallest (known) conductor::

            sage: E = EllipticCurve([1, -1, 0, -79, 289])
            sage: factor(E.conductor())  # conductor is 234446
            2 * 117223
            sage: factor(E.modular_degree())
            2^7 * 2617
        """
        try:
            return self.__modular_degree

        except AttributeError:
            if algorithm == 'sympow':
                from sage.lfunctions.all import sympow
                m = sympow.modular_degree(self)
            elif algorithm == 'magma':
                from sage.interfaces.all import magma
                m = rings.Integer(magma(self).ModularDegree())
            else:
                raise ValueError, "unknown algorithm %s"%algorithm
            self.__modular_degree = m
            return m

    def modular_parametrization(self):
        r"""
        Computes and returns the modular parametrization of this elliptic
        curve.

        The curve is converted to a minimal model.

        OUTPUT: A list of two Laurent series [X(x),Y(x)] of degrees -2, -3
        respectively, which satisfy the equation of the (minimal model of
        the) elliptic curve. There are modular functions on
        `\Gamma_0(N)` where `N` is the conductor.

        X.deriv()/(2\*Y+a1\*X+a3) should equal f(q)dq/q where f is
        self.q_expansion().

        EXAMPLES::

            sage: E=EllipticCurve('389a1')
            sage: X,Y=E.modular_parametrization()
            sage: X
            q^-2 + 2*q^-1 + 4 + 7*q + 13*q^2 + 18*q^3 + 31*q^4 + 49*q^5 + 74*q^6 + 111*q^7 + 173*q^8 + 251*q^9 + 379*q^10 + 560*q^11 + 824*q^12 + 1199*q^13 + 1773*q^14 + 2365*q^15 + 3463*q^16 + 4508*q^17 + O(q^18)
            sage: Y
            -q^-3 - 3*q^-2 - 8*q^-1 - 17 - 33*q - 61*q^2 - 110*q^3 - 186*q^4 - 320*q^5 - 528*q^6 - 861*q^7 - 1383*q^8 - 2218*q^9 - 3472*q^10 - 5451*q^11 - 8447*q^12 - 13020*q^13 - 20083*q^14 - 29512*q^15 - 39682*q^16 + O(q^17)

        The following should give 0, but only approximately::

            sage: q = X.parent().gen()
            sage: E.defining_polynomial()(X,Y,1) + O(q^11) == 0
            True

        Note that below we have to change variable from x to q

        ::

            sage: a1,_,a3,_,_=E.a_invariants()
            sage: f=E.q_expansion(17)
            sage: q=f.parent().gen()
            sage: f/q == (X.derivative()/(2*Y+a1*X+a3))
            True
        """
        R = LaurentSeriesRing(RationalField(),'q')
        XY = self.pari_mincurve().elltaniyama()
        return [1/R(1/XY[0]),1/R(1/XY[1])]

    def congruence_number(self):
        r"""
        Let `X` be the subspace of `S_2(\Gamma_0(N))` spanned by the newform
        associated with this elliptic curve, and `Y` be orthogonal compliment
        of `X` under the Petersson inner product. Let `S_X` and `S_Y` be the
        intersections of `X` and `Y` with `S_2(\Gamma_0(N)m \mathbb{Z})`. The congruence
        number is defined to be `[S_X \oplus S_Y : S_2(\Gamma_0(N),\mathbb{Z})]`.
        It measures congruences between `f` and elements of `S_2(\Gamma_0(N),\mathbb{Z})`
        orthogonal to `f`.

        EXAMPLES::

            sage: E = EllipticCurve('37a')
            sage: E.congruence_number()
            2
            sage: E.congruence_number()
            2
            sage: E = EllipticCurve('54b')
            sage: E.congruence_number()
            6
            sage: E.modular_degree()
            2
            sage: E = EllipticCurve('242a1')
            sage: E.modular_degree()
            16
            sage: E.congruence_number()  # long time
            176


            It is a theorem of Ribet that the congruence number is equal to the
            modular degree in the case of square free conductor. It is a conjecture
            of Agashe, Ribet, and Stein that `ord_p(c_f/m_f) \le ord_p(N)/2`.

        TESTS::

            sage: E = EllipticCurve('11a')
            sage: E.congruence_number()
            1
        """
        try:
            return self.__congruence_number
        except AttributeError:
            pass
        # Currently this is *much* faster to compute
        m = self.modular_degree()
        if self.conductor().is_squarefree():
            self.__congruence_number = m
        else:
            W = self.modular_symbol_space(sign=1)
            V = W.complement().cuspidal_subspace()
            self.__congruence_number = W.congruence_number(V)
            if not m.divides(self.__congruence_number):
                # We should never get here
                raise ValueError, "BUG in modular degree or congruence number computation of: %s" % self
        return self.__congruence_number

    def cremona_label(self, space=False):
        """
        Return the Cremona label associated to (the minimal model) of this
        curve, if it is known. If not, raise a RuntimeError exception.

        EXAMPLES::

            sage: E=EllipticCurve('389a1')
            sage: E.cremona_label()
            '389a1'

        The default database only contains conductors up to 10000, so any
        curve with conductor greater than that will cause an error to be
        raised. The optional package 'database_cremona_ellcurve-20071019'
        contains more curves, with conductors up to 130000.

        ::

            sage: E=EllipticCurve([1,2,3,4,5]);
            sage: E.conductor()
            10351
            sage: E.cremona_label()
            Traceback (most recent call last):
            ...
            RuntimeError: Cremona label not known for Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 4*x + 5 over Rational Field.
        """
        try:
            if not space:
                return self.__cremona_label.replace(' ','')
            return self.__cremona_label
        except AttributeError:
            try:
                X = self.database_curve()
            except RuntimeError:
                raise RuntimeError, "Cremona label not known for %s."%self
            self.__cremona_label = X.__cremona_label
            return self.cremona_label(space)

    label = cremona_label

    def reduction(self,p):
       """
       Return the reduction of the elliptic curve at a prime of good
       reduction.

       .. note::

          All is done in ``self.change_ring(GF(p))``; all we do is
          check that p is prime and does not divide the discriminant.

       INPUT:

       -  ``p`` - a (positive) prime number


       OUTPUT: an elliptic curve over the finite field GF(p)

       EXAMPLES::

           sage: E = EllipticCurve('389a1')
           sage: E.reduction(2)
           Elliptic Curve defined by y^2 + y = x^3 + x^2 over Finite Field of size 2
           sage: E.reduction(3)
           Elliptic Curve defined by y^2 + y = x^3 + x^2 + x over Finite Field of size 3
           sage: E.reduction(5)
           Elliptic Curve defined by y^2 + y = x^3 + x^2 + 3*x over Finite Field of size 5
           sage: E.reduction(38)
           Traceback (most recent call last):
           ...
           AttributeError: p must be prime.
           sage: E.reduction(389)
           Traceback (most recent call last):
           ...
           AttributeError: The curve must have good reduction at p.
       """
       p = rings.Integer(p)
       if not p.is_prime():
           raise AttributeError, "p must be prime."
       disc = self.discriminant()
       if not disc.valuation(p) == 0:
           raise AttributeError, "The curve must have good reduction at p."
       return self.change_ring(rings.GF(p))

    def torsion_order(self):
        """
        Return the order of the torsion subgroup.

        EXAMPLES::

            sage: e = EllipticCurve('11a')
            sage: e.torsion_order()
            5
            sage: type(e.torsion_order())
            <type 'sage.rings.integer.Integer'>
            sage: e = EllipticCurve([1,2,3,4,5])
            sage: e.torsion_order()
            1
            sage: type(e.torsion_order())
            <type 'sage.rings.integer.Integer'>
        """
        try:
            return self.__torsion_order
        except AttributeError:
            self.__torsion_order = self.torsion_subgroup().order()
            return self.__torsion_order

    def _torsion_bound(self,number_of_places = 20):
        r"""
        Computes an upper bound on the order of the torsion group of the
        elliptic curve by counting points modulo several primes of good
        reduction. Note that the upper bound returned by this function is a
        multiple of the order of the torsion group.

        INPUT:


        -  ``number_of_places (default = 20)`` - the number
           of places that will be used to find the bound


        OUTPUT:


        -  ``integer`` - the upper bound


        EXAMPLES:
        """
        E = self
        bound = Integer(0)
        k = 0
        p = Integer(2)   # will run through odd primes
        while k < number_of_places :
            p = p.next_prime()
            # check if the formal group at the place is torsion-free
            # if so the torsion injects into the reduction
            while not E.is_local_integral_model(p) or not E.is_good(p): p = p.next_prime()
            bound = arith.gcd(bound,E.reduction(p).cardinality())
            if bound == 1:
                return bound
            k += 1
        return bound


    def torsion_subgroup(self, algorithm="pari"):
        """
        Returns the torsion subgroup of this elliptic curve.

        INPUT:


        -  ``algorithm`` - string:

        -  ``"pari"`` - (default) use the pari library

        -  ``"doud"`` - use Doud's algorithm

        -  ``"lutz_nagell"`` - use the Lutz-Nagell theorem


        OUTPUT: The EllipticCurveTorsionSubgroup instance associated to
        this elliptic curve.

        .. note::

           To see the torsion points as a list, use :meth:`.torsion_points`.

        EXAMPLES::

            sage: EllipticCurve('11a').torsion_subgroup()
            Torsion Subgroup isomorphic to Multiplicative Abelian Group isomorphic to C5 associated to the Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field
            sage: EllipticCurve('37b').torsion_subgroup()
            Torsion Subgroup isomorphic to Multiplicative Abelian Group isomorphic to C3 associated to the Elliptic Curve defined by y^2 + y = x^3 + x^2 - 23*x - 50 over Rational Field

        ::

            sage: e = EllipticCurve([-1386747,368636886]);e
            Elliptic Curve defined by y^2  = x^3 - 1386747*x + 368636886 over Rational Field
            sage: G = e.torsion_subgroup(); G
            Torsion Subgroup isomorphic to Multiplicative Abelian
            Group isomorphic to C8 x C2 associated to the Elliptic
            Curve defined by y^2 = x^3 - 1386747*x + 368636886 over
            Rational Field
            sage: G.0
            (1227 : 22680 : 1)
            sage: G.1
            (282 : 0 : 1)
            sage: list(G)
            [1, P1, P0, P0*P1, P0^2, P0^2*P1, P0^3, P0^3*P1, P0^4, P0^4*P1, P0^5, P0^5*P1, P0^6, P0^6*P1, P0^7, P0^7*P1]
        """
        try:
            return self.__torsion_subgroup
        except AttributeError:
            self.__torsion_subgroup = ell_torsion.EllipticCurveTorsionSubgroup(self, algorithm)
            self.__torsion_order = self.__torsion_subgroup.order()
            return self.__torsion_subgroup

    def torsion_points(self, algorithm="pari"):
        """
        Returns the torsion points of this elliptic curve as a sorted
        list.

        INPUT:


        -  ``algorithm`` - string:

        -  ``"pari"`` - (default) use the pari library

        -  ``"doud"`` - use Doud's algorithm

        -  ``"lutz_nagell"`` - use the Lutz-Nagell theorem


        OUTPUT: A list of all the torsion points on this elliptic curve.

        EXAMPLES::

            sage: EllipticCurve('11a').torsion_points()
            [(0 : 1 : 0), (5 : -6 : 1), (5 : 5 : 1), (16 : -61 : 1), (16 : 60 : 1)]
            sage: EllipticCurve('37b').torsion_points()
            [(0 : 1 : 0), (8 : -19 : 1), (8 : 18 : 1)]

        ::

            sage: E=EllipticCurve([-1386747,368636886])
            sage: T=E.torsion_subgroup(); T
            Torsion Subgroup isomorphic to Multiplicative Abelian Group isomorphic to C8 x C2 associated to the Elliptic Curve defined by y^2  = x^3 - 1386747*x + 368636886 over Rational Field
            sage: T == E.torsion_subgroup(algorithm="doud")
            True
            sage: T == E.torsion_subgroup(algorithm="lutz_nagell")
            True
            sage: E.torsion_points()
            [(-1293 : 0 : 1),
            (-933 : -29160 : 1),
            (-933 : 29160 : 1),
            (-285 : -27216 : 1),
            (-285 : 27216 : 1),
            (0 : 1 : 0),
            (147 : -12960 : 1),
            (147 : 12960 : 1),
            (282 : 0 : 1),
            (1011 : 0 : 1),
            (1227 : -22680 : 1),
            (1227 : 22680 : 1),
            (2307 : -97200 : 1),
            (2307 : 97200 : 1),
            (8787 : -816480 : 1),
            (8787 : 816480 : 1)]
        """
        multiples = sage.groups.generic.multiples
        gens = self.torsion_subgroup(algorithm).gens()
        ngens = len(gens)
        if ngens == 0:
            return [self(0)]
        pts = list(multiples(gens[0],gens[0].order()))
        if ngens == 1:
            pts.sort()
            return pts
        pts = [P+Q for P in pts for Q in multiples(gens[1],gens[1].order())]
        pts.sort()
        return pts

    ## def newform_eval(self, z, prec):
##         """
##         The value of the newform attached to this elliptic curve at
##         the point z in the complex upper half plane, computed using
##         prec terms of the power series expansion.  Note that the power
##         series need not converge well near the real axis.
##         """
##         raise NotImplementedError

    def root_number(self):
        """
        Returns the root number of this elliptic curve.

        This is 1 if the order of vanishing of the L-function L(E,s) at 1
        is even, and -1 if it is odd.

        EXAMPLES::

            sage: EllipticCurve('11a1').root_number()
            1
            sage: EllipticCurve('37a1').root_number()
            -1
            sage: EllipticCurve('389a1').root_number()
            1
        """
        try:
            return self.__root_number
        except AttributeError:
            self.__root_number = int(self.pari_mincurve().ellrootno())
        return self.__root_number

    def has_cm(self):
        """
        Returns True iff this elliptic curve has Complex Multiplication.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.has_cm()
            False
            sage: E=EllipticCurve('32a1')
            sage: E.has_cm()
            True
            sage: E.j_invariant()
            1728
        """

        return CMJ.has_key(self.j_invariant())

    def cm_discriminant(self):
        """
        Returns the associated quadratic discriminant if this elliptic
        curve has Complex Multiplication.

        A ValueError is raised if the curve does not have CM (see the
        function has_cm()).

        EXAMPLES::

            sage: E=EllipticCurve('32a1')
            sage: E.cm_discriminant()
            -4
            sage: E=EllipticCurve('121b1')
            sage: E.cm_discriminant()
            -11
            sage: E=EllipticCurve('37a1')
            sage: E.cm_discriminant()
            Traceback (most recent call last):
            ...
            ValueError: Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field does not have CM
        """

        try:
            return CMJ[self.j_invariant()]
        except KeyError:
            raise ValueError, "%s does not have CM"%self


    def quadratic_twist(self, D):
        """
        Return the global minimal model of the quadratic twist of this
        curve by D.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E7=E.quadratic_twist(7); E7
            Elliptic Curve defined by y^2  = x^3 - 784*x + 5488 over Rational Field
            sage: E7.conductor()
            29008
            sage: E7.quadratic_twist(7) == E
            True
        """
        return EllipticCurve_number_field.quadratic_twist(self, D).minimal_model()

    def minimal_quadratic_twist(self):
        r"""
        Determines a quadratic twist with minimal conductor. Returns a global
        minimal model of the twist and the fundamental discriminant of the
        quadratic field over which they are isomorphic.

        The implementation is not optimal at all. It factors the conductor `N` and tries to twist
        by `(-1)^((p-1)/2) p` if `p^2` divides `N`. For 2 and 3 we try and check if it smaller.

        EXAMPLES::

            sage: E = EllipticCurve('121d1')
            sage: E.minimal_quadratic_twist()
            (Elliptic Curve defined by y^2 + y = x^3 - x^2 over Rational Field, -11)
            sage: Et, D = EllipticCurve('32a1').minimal_quadratic_twist()
            sage: D
            1

            sage: E = EllipticCurve('11a1')
            sage: Et, D = E.quadratic_twist(-24).minimal_quadratic_twist()
            sage: E == Et
            True
            sage: D
            -24

        """
        N = self.conductor()
        D = 1
        Nt = N
        for (p,f) in factor(N):
            if f > 1 and p > 3:
                if p % 4 == 1:
                    DD = p
                else:
                    DD = (-p)
                Et = self.quadratic_twist(DD)
                if Et.conductor() < Nt:
                    Nt = Et.conductor()
                    D *= DD
        Et = self.quadratic_twist(D)
        Nt = Et.conductor()
        # try with -3
        Ett = Et.quadratic_twist(-3)
        if Ett.conductor() < Nt:
            D *= (-3)
            Et = Ett
            Nt = Ett.conductor()
        # try with -4, 8 or -8
        DD = 1
        for D2 in [-4,8,-8]:
            Ett = Et.quadratic_twist(D2)
            if Ett.conductor() < Nt :
                Nt = Ett.conductor()
                DD = D2
        D *= DD
        Et = self.quadratic_twist(D)
        return Et, D



    ##########################################################
    # Isogeny class
    ##########################################################
    def isogeny_class(self, algorithm="mwrank", verbose=False):
        r"""
        Return all curves over `\mathbb{Q}` in the isogeny class of
        this elliptic curve.

        WARNING: The result is \emph{not} provably correct, in the
            sense that when the numbers are huge isogenies could be
            missed because of precision issues.

        INPUT:
            verbose -- bool (default: False)


        -  ``algorithm`` - string:

        -  ``"mwrank"`` - (default) use the mwrank C++
           library

        -  ``"database"`` - use the Cremona database (only
           works if curve is isomorphic to a curve in the database)


        OUTPUT: Returns the sorted list of the curves isogenous to self. If
        algorithm is "mwrank", also returns the isogeny matrix (otherwise
        returns None as second return value).


        .. note::

           The ordering depends on which algorithm is used.

        EXAMPLES::

            sage: I, A = EllipticCurve('37b').isogeny_class('mwrank')
            sage: I   # randomly ordered
            [Elliptic Curve defined by y^2 + y = x^3 + x^2 - 23*x - 50 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 + x^2 - 1873*x - 31833 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 + x^2 - 3*x +1 over Rational Field]
            sage: A
            [0 3 3]
            [3 0 0]
            [3 0 0]

        ::

            sage: I, _ = EllipticCurve('37b').isogeny_class('database'); I
            [Elliptic Curve defined by y^2 + y = x^3 + x^2 - 1873*x - 31833 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 + x^2 - 23*x - 50 over Rational Field,
             Elliptic Curve defined by y^2 + y = x^3 + x^2 - 3*x + 1 over Rational Field]

        This is an example of a curve with a `37`-isogeny::

            sage: E = EllipticCurve([1,1,1,-8,6])
            sage: E.isogeny_class ()
            ([Elliptic Curve defined by y^2 + x*y + y = x^3 + x^2 - 8*x + 6 over Rational Field,
              Elliptic Curve defined by y^2 + x*y + y = x^3 + x^2 - 208083*x - 36621194 over Rational Field],
             [ 0 37]
             [37  0])

        This curve had numerous `2`-isogenies::

            sage: e=EllipticCurve([1,0,0,-39,90])
            sage: e.isogeny_class ()
            ([Elliptic Curve defined by y^2 + x*y = x^3 - 39*x + 90 over Rational Field,
              Elliptic Curve defined by y^2 + x*y = x^3 - 4*x - 1 over Rational Field,
              Elliptic Curve defined by y^2 + x*y = x^3 + x over Rational Field,
              Elliptic Curve defined by y^2 + x*y = x^3 - 49*x - 136 over Rational Field,
              Elliptic Curve defined by y^2 + x*y = x^3 - 34*x - 217 over Rational Field,
              Elliptic Curve defined by y^2 + x*y = x^3 - 784*x - 8515 over Rational Field],
             [0 2 0 0 0 0]
             [2 0 2 2 0 0]
             [0 2 0 0 0 0]
             [0 2 0 0 2 2]
             [0 0 0 2 0 0]
             [0 0 0 2 0 0])

        See http://math.harvard.edu/~elkies/nature.html for more interesting
        examples of isogeny structures.
        """
        if algorithm == "mwrank":
            try:
                E = self.mwrank_curve()
            except ValueError:
                E = self.minimal_model().mwrank_curve()
            I, A = E.isogeny_class(verbose=verbose)
            mat = matrix.MatrixSpace(rings.IntegerRing(), len(A))(A)
            I = [constructor.EllipticCurve(ainvs) for ainvs in I]
            return I, mat

        elif algorithm == "database":

            try:
                label = self.cremona_label(space=False)
            except RuntimeError:
                raise RuntimeError, "unable to to find %s in the database"%self
            db = sage.databases.cremona.CremonaDatabase()
            I = db.isogeny_class(label)
            if len(I) == 0:
                raise RuntimeError, "unable to to find %s in the database"%self
            I.sort()
            return I, None

        else:

            raise ValueError, "unknown algorithm '%s'"%algorithm

    def optimal_curve(self):
        """
        Given an elliptic curve that is in the installed Cremona
        database, return the optimal curve isogenous to it.

        EXAMPLES:

        The following curve is not optimal::

            sage: E = EllipticCurve('11a2'); E
            Elliptic Curve defined by y^2 + y = x^3 - x^2 - 7820*x - 263580 over Rational Field
            sage: E.optimal_curve()
            Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field
            sage: E.optimal_curve().cremona_label()
            '11a1'

        Note that 990h is the special case where the optimal curve
        isn't the first in the Cremona labeling::

            sage: E = EllipticCurve('990h4'); E
            Elliptic Curve defined by y^2 + x*y + y = x^3 - x^2 + 6112*x - 41533 over Rational Field
            sage: F = E.optimal_curve(); F
            Elliptic Curve defined by y^2 + x*y + y = x^3 - x^2 - 1568*x - 4669 over Rational Field
            sage: F.cremona_label()
            '990h3'
            sage: EllipticCurve('990a1').optimal_curve().cremona_label()   # a isn't h.
            '990a1'

        If the input curve is optimal, this function returns that
        curve (not just a copy of it or a curve isomorphic to it!)::

            sage: E = EllipticCurve('37a1')
            sage: E.optimal_curve() is E
            True

        Also, if this curve is optimal but not given by a minimal
        model, this curve will still be returned, so this function
        need not return a minimal model in general.

        ::
            sage: F = E.short_weierstrass_model(); F
            Elliptic Curve defined by y^2  = x^3 - 16*x + 16 over Rational Field
            sage: F.optimal_curve()
            Elliptic Curve defined by y^2  = x^3 - 16*x + 16 over Rational Field
        """
        label = self.cremona_label()
        N, isogeny, number = sage.databases.cremona.parse_cremona_label(label)
        if N == 990 and isogeny == 'h':
            optimal_label = '990h3'
        else:
            optimal_label = '%s%s1'%(N,isogeny)
        if optimal_label == label: return self
        return constructor.EllipticCurve(optimal_label)

    def isogeny_graph(self):
        r"""
        Returns a graph representing the isogeny class of this elliptic
        curve, where the vertices are isogenous curves over
        `\mathbb{Q}` and the edges are prime degree isogenies

        .. warning::

           The result is *not* provably correct, in the
           sense that when the numbers are huge isogenies could be
           missed because of precision issues.

        EXAMPLES::

            sage: LL = []
            sage: for e in cremona_optimal_curves(range(1, 38)):
            ...    G = e.isogeny_graph()
            ...    already = False
            ...    for H in LL:
            ...        if G.is_isomorphic(H):
            ...            already = True
            ...            break
            ...    if not already:
            ...        LL.append(G)
            ...
            sage: graphs_list.show_graphs(LL)

        ::

            sage: E = EllipticCurve('195a')
            sage: G = E.isogeny_graph()
            sage: for v in G: print v, G.get_vertex(v)
            ...
            0 Elliptic Curve defined by y^2 + x*y  = x^3 - 110*x + 435 over Rational Field
            1 Elliptic Curve defined by y^2 + x*y  = x^3 - 115*x + 392 over Rational Field
            2 Elliptic Curve defined by y^2 + x*y  = x^3 + 210*x + 2277 over Rational Field
            3 Elliptic Curve defined by y^2 + x*y  = x^3 - 520*x - 4225 over Rational Field
            4 Elliptic Curve defined by y^2 + x*y  = x^3 + 605*x - 19750 over Rational Field
            5 Elliptic Curve defined by y^2 + x*y  = x^3 - 8125*x - 282568 over Rational Field
            6 Elliptic Curve defined by y^2 + x*y  = x^3 - 7930*x - 296725 over Rational Field
            7 Elliptic Curve defined by y^2 + x*y  = x^3 - 130000*x - 18051943 over Rational Field
            sage: G.plot(edge_labels=True)
        """
        from sage.graphs.graph import Graph
        L, M = self.isogeny_class(algorithm='mwrank')
        G = Graph(M, format='weighted_adjacency_matrix')
        G.set_vertices(dict([(v,L[v]) for v in G.vertices()]))
        return G

    def manin_constant(self):
        r"""
        Return the Manin constant of this elliptic curve.

        OUTPUT:

        an integer

        This function only works if the curve is in the installed
        Cremona database.  Sage includes by default a small databases;
        for the full database you have to install an optional package.

        .. warning::

           The result is *not* provably correct, in the
           sense that when the numbers are huge isogenies could be
           missed because of precision issues.

        EXAMPLES::

            sage: EllipticCurve('11a1').manin_constant()
            1
            sage: EllipticCurve('11a2').manin_constant()
            5
            sage: EllipticCurve('11a3').manin_constant()
            5

        Check that it works even if the curve is non-minimal::

            sage: EllipticCurve('11a1').short_weierstrass_model().manin_constant()
            1

        An example where the isogeny class is large, so it's not completely
        trivial to find the minimal degree of an isogeny to the optimal curve::

            sage: [EllipticCurve('210b%s'%i).manin_constant() for i in [1..8]]
            [1, 2, 3, 4, 4, 6, 12, 12]

        Make sure the special case 990h is treated correctly, i.e., that 990h3 has
        Manin constant 1::

            sage: [EllipticCurve('990h%s'%i).manin_constant() for i in [1..4]]
            [3, 6, 1, 2]

        This plots helps you see that the above Manin constants are
        right.  Note that the vertex labels are 0-based unlinke the
        Cremona isogeny labels::

            sage: EllipticCurve('210b1').isogeny_graph().plot(edge_labels=True)
        """
        label = self.cremona_label()
        optimal = self.optimal_curve()
        if optimal == self:
            return Integer(1)
        L, v = self._shortest_paths()
        i = L.index(optimal)
        return v[i]

    def _shortest_paths(self):
        r"""
        Technical internal function that returns the list of isogenies
        curves and corresponding dictionary of shortest isogeny paths
        from self to each other curve in the isogeny class.

        .. warning::

           The result is *not* provably correct, in the
           sense that when the numbers are huge isogenies could be
           missed because of precision issues.

        OUTPUT:

        list, dict

        EXAMPLES::

            sage: EllipticCurve('11a1')._shortest_paths()
            ([Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field,
              Elliptic Curve defined by y^2 + y = x^3 - x^2 - 7820*x - 263580 over Rational Field,
              Elliptic Curve defined by y^2 + y = x^3 - x^2 over Rational Field],
             {0: 0, 1: 5, 2: 5})
            sage: EllipticCurve('11a2')._shortest_paths()
            ([Elliptic Curve defined by y^2 + y = x^3 - x^2 - 7820*x - 263580 over Rational Field,
              Elliptic Curve defined by y^2 + y = x^3 - x^2 - 10*x - 20 over Rational Field,
              Elliptic Curve defined by y^2 + y = x^3 - x^2 over Rational Field],
             {0: 0, 1: 5, 2: 25})
        """
        from sage.graphs.graph import Graph
        L, M = self.isogeny_class(algorithm='mwrank')
        M = M.change_ring(rings.RR)
        # see trac #4889 for nebulous M.list() --> M.entries() change...
        # Take logs here since shortest path minimizes the *sum* of the weights -- not the product.
        M = M.parent()([a.log() if a else 0 for a in M.list()])
        G = Graph(M, format='weighted_adjacency_matrix')
        G.set_vertices(dict([(v,L[v]) for v in G.vertices()]))
        v = G.shortest_path_lengths(0, by_weight=True, weight_sums=True)
        # Now exponentiate and round to get degrees of isogenies
        v = dict([(i, j.exp().round() if j else 0) for i,j in v.iteritems()])
        return L, v

    def _multiple_of_degree_of_isogeny_to_optimal_curve(self):
        r"""
        Internal function returning an integer m such that the degree of
        the isogeny between this curve and the optimal curve in its
        isogeny class is a divisor of m.

        .. warning::

           The result is *not* provably correct, in the
           sense that when the numbers are huge isogenies could be
           missed because of precision issues.

        EXAMPLES::

            sage: E = EllipticCurve('11a1')
            sage: E._multiple_of_degree_of_isogeny_to_optimal_curve()
            5
            sage: E = EllipticCurve('11a2')
            sage: E._multiple_of_degree_of_isogeny_to_optimal_curve()
            25
            sage: E = EllipticCurve('11a3')
            sage: E._multiple_of_degree_of_isogeny_to_optimal_curve()
            25
        """
        _, v = self._shortest_paths()
        # Compute the degree of an isogeny from self to anything else
        # in the isogeny class of self.  Assuming the isogeny
        # enumeration is complete (which need not be the case a priori!), the LCM
        # of these numbers is a multiple of the degree of the isogeny
        # to the optimal curve.
        v = [deg for num, deg in v.iteritems() if deg]  # get just the degrees
        return arith.LCM(v)



    ##########################################################
    # Galois Representations
    ##########################################################

    def is_reducible(self, p):
        """
        Return True if the mod-p representation attached to E is
        reducible.

        INPUT:


        -  ``p`` - a prime number


        .. note::

           The answer is cached.

        EXAMPLES::

            sage: E = EllipticCurve('121a'); E
            Elliptic Curve defined by y^2 + x*y + y = x^3 + x^2 - 30*x - 76 over Rational Field
            sage: E.is_reducible(7)
            False
            sage: E.is_reducible(11)
            True
            sage: EllipticCurve('11a').is_reducible(5)
            True
            sage: e = EllipticCurve('11a2')
            sage: e.is_reducible(5)
            True
            sage: e.torsion_order()
            1
        """
        try:
            return self.__is_reducible[p]
        except AttributeError:
            self.__is_reducible = {}
        except KeyError:
            pass

        if not arith.is_prime(p):
            raise ValueError, 'p (=%s) must be prime'%p
        # we do is_surjective first, since this is
        # much easier than computing isogeny_class
        t, why = self.is_surjective(p)
        if t == True:
            self.__is_reducible[p] = False
            return False  # definitely not reducible
        isogeny_matrix = self.isogeny_class()[ 1 ]
        v = isogeny_matrix.row(0) # first row
        for a in v:
            if a != 0 and a % p == 0:
                self.__is_reducible[p] = True
                return True
        self.__is_reducible[p] = False
        return False

    def is_irreducible(self, p):
        """
        Return True if the mod p representation is irreducible.

        EXAMPLES::

            sage: e = EllipticCurve('37b')
            sage: e.is_irreducible(2)
            True
            sage: e.is_irreducible(3)
            False
            sage: e.is_reducible(2)
            False
            sage: e.is_reducible(3)
            True
        """
        return not self.is_reducible(p)

    def is_surjective(self, p, A=1000):
        """
        Return True if the mod-p representation attached to E is
        surjective, False if it is not, or None if we were unable to
        determine whether it is or not.

        .. note::

           The answer is cached.

        INPUT:


        -  ``p`` - int (a prime number)

        -  ``A`` - int (a bound on the number of a_p to use)


        OUTPUT:

        A 2-tuple:

        - surjective or (probably) not

        - information about what it is if not surjective


        EXAMPLES::

            sage: e = EllipticCurve('37b')
            sage: e.is_surjective(2)
            (True, None)
            sage: e.is_surjective(3)
            (False, '3-torsion')

        REMARKS:

        1. If `p = 5` then the mod-p representation is
           surjective if and only if the p-adic representation is
           surjective. When `p = 2, 3` there are
           counterexamples. See a very recent paper of Elkies for more
           details when `p=3`.

        2. When p = 3 this function always gives the correct result
           irregardless of A, since it explicitly determines the
           p-division polynomial.
        """
        if not arith.is_prime(p):
            raise TypeError, "p (=%s) must be prime."%p
        A = int(A)
        key = (p, A)
        try:
            return self.__is_surjective[key]
        except KeyError:
            pass
        except AttributeError:
            self.__is_surjective = {}

        ans = self._is_surjective(p, A)
        self.__is_surjective[key] = ans
        return ans

    def _is_surjective(self, p, A):
        T = self.torsion_subgroup().order()
        if T % p == 0:
            return False, "%s-torsion"%p

        if p == 2:
            # E is isomorphic to  [0,b2,0,8*b4,16*b6]
            b2,b4,b6,b8=self.b_invariants()
            R = rings.PolynomialRing(self.base_ring(), 'x')
            x = R.gen()
            f = x**3 + b2*x**2 + 8*b4*x + 16*b6
            if not f.is_irreducible():
                return False, '2-torsion'
            if arith.is_square(f.discriminant()):
                return False, "A3"
            return True, None

        if p == 3:
            # Algorithm: Let f be the 3-division polynomial, which is
            # a polynomial of degree 4.  Then I claim that this
            # polynomial has Galois group S_4 if and only if the
            # representation rhobar_{E,3} is surjective.  If the group
            # is S_4, then S_4 is a quotient of the image of
            # rhobar_{E,3}.  Since S_4 has order 24 and GL_2(F_3)
            # has order 48, the only possibility we have to consider
            # is that the image of rhobar is isomorphic to S_4.
            # But this is not the case because S_4 is not a subgroup
            # of GL_2(F_3).    If it were, it would be normal, since
            # it would have index 2.  But there is a *unique* normal
            # subgroup of GL_2(F_3) of index 2, namely SL_2(F_3),
            # and SL_2(F_3) is not isomorphic to S_4 (S_4 has a normal
            # subgroup of index 2 and SL_2(F_3) does not.)
            # (What's a simple way to see that SL_2(F_3) is the
            # unique index-2 normal subgroup?  I didn't see an obvious
            # reason, so just used the NormalSubgroups command in MAGMA
            # and it output exactly one of index 2.)

            # Here's Noam Elkies proof for the other direction:

            #> Let E be an elliptic curve over Q.  Is the mod-3
            #> representation E[3]  surjective if and only if the
            #> (degree 4) division polynomial has Galois group S_4?  I
            #> can see why the group being S_4 implies the
            #> representation is surjective, but the converse is not
            #> clear to me.
            # I would have thought that this is the easier part: to
            # say that E[3] is surjective is to say the 3-torsion
            # field Q(E[3]) has Galois group GL_2(Z/3) over Q.  Let
            # E[3]+ be the subfield fixed by the element -1 of
            # GL_2(Z/3).  Then E[3] has Galois group PGL_2(Z/3), which
            # is identified with S_4 by its action on the four
            # 3-element subgroups of E[3].  Each such subgroup is in
            # turn determined by the x-coordinate shared by its two
            # nonzero points.  So, if E[3] is surjective then any
            # permutation of those x-coordinates is realized by some
            # element of Gal(E[3]+/Q).  Thus the Galois group of the
            # division polynomial (whose roots are those
            # x-coordinates) maps surjectively to S_4, which means it
            # equals S_4.


            f = self.division_polynomial(3)
            if not f.is_irreducible():
                return False, "reducible_3-divpoly"
            n = pari(f).polgalois()[0]
            if n == 24:
                return True, None
            else:
                return False, "3-divpoly_galgroup_order_%s"%n

        if self.has_cm():
            return False, "CM"
        an = self.anlist(A)
        ell = 0
        Np = self.conductor() * p
        signs = []
        while True:
            ell = arith.next_prime(ell)
            if ell >= A: break
            if Np % ell != 0:
                a_ell = an[int(ell)]
                if a_ell % p != 0:
                    s = arith.kronecker(a_ell**2 - 4*ell, p)
                    #print ell, s
                    if s == 0: continue
                    if not (s in signs):
                        signs.append(s)
                        if len(signs) == 2:
                            return True, None

        # could do something further here...
        return False, signs

    def is_semistable(self):
        """
        Return True iff this elliptic curve is semi-stable at all primes.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.is_semistable()
            True
            sage: E=EllipticCurve('90a1')
            sage: E.is_semistable()
            False
        """
        if self.base_ring() != Q:
            raise NotImplementedError, "is_semistable only implemented for curves over the rational numbers."
        return self.conductor().is_squarefree()

    def reducible_primes(self):
        r"""
        Returns a list of the primes `p` such that the mod
        `p` representation `\rho_{E,p}` is reducible. For
        all other primes the representation is irreducible.

        .. note::

           This is *not* provably correct in general. See the
           documentation for :meth:`.isogeny_class`.

        EXAMPLES::

            sage: E = EllipticCurve('225a')
            sage: E.reducible_primes()
            [3]
        """
        try:
            return self.__reducible_primes
        except AttributeError:
            pass
        C, I = self.isogeny_class(algorithm='mwrank')
        X = set(I.list())
        R = [p for p in X if arith.is_prime(p)]
        self.__reducible_primes = R
        return R

    def non_surjective(self, A=1000):
        r"""
        Returns a list of primes p such that the mod-p representation
        `\rho_{E,p}` *might* not be surjective (this list
        usually contains 2, because of shortcomings of the algorithm). If p
        is not in the returned list, then rho_E,p is provably surjective
        (see A. Cojocaru's paper). If the curve has CM then infinitely many
        representations are not surjective, so we simply return the
        sequence [(0,"cm")] and do no further computation.

        INPUT:


        -  ``A`` - an integer


        OUTPUT:


        -  ``list`` - if curve has CM, returns [(0,"cm")].
           Otherwise, returns a list of primes where mod-p representation is
           very likely not surjective. At any prime not in this list, the
           representation is definitely surjective.


        EXAMPLES::

            sage: E = EllipticCurve([0, 0, 1, -38, 90])  # 361A
            sage: E.non_surjective()   # CM curve
            [(0, 'cm')]

        ::

            sage: E = EllipticCurve([0, -1, 1, 0, 0]) # X_1(11)
            sage: E.non_surjective()
            [(5, '5-torsion')]

        ::

            sage: E = EllipticCurve([0, 0, 1, -1, 0]) # 37A
            sage: E.non_surjective()
            []

        ::

            sage: E = EllipticCurve([0,-1,1,-2,-1])   # 141C
            sage: E.non_surjective()
            [(13, [1])]

        ALGORITHM: When p=3 use division polynomials. For 5 = p = B, where
        B is Cojocaru's bound, use the results in Section 2 of Serre's
        inventiones paper"Sur Les Representations Modulaires Deg Degre 2 de
        Galqbar Over Q."
        """
        if self.has_cm():
            misc.verbose("cm curve")
            return [(0,"cm")]
        N = self.conductor()
        if self.is_semistable():
            C = 11
            misc.verbose("semistable -- so bound is 11")
        else:
            C = 1 + 4*sqrt(6)*int(N)/3 * sqrt(mul([1+1.0/int(p) for p,_ in factor(N)]))
            misc.verbose("conductor = %s, and bound is %s"%(N,C))
        C = 1 + 4*sqrt(6)*int(N)/3 * sqrt(mul([1+1.0/int(p) for p,_ in factor(N)]))
        misc.verbose("conductor = %s, and bound is %s"%(N,C))
        B = []
        p = 2
        while p <= C:
            t, v = self.is_surjective(p, A=A)
            misc.verbose("(%s,%s,%s)"%(p,t,v))
            if not t:
                B.append((p,v))
            p = next_prime(p)
        return B

    def is_ordinary(self, p, ell=None):
        """
        Return True precisely when the mod-p representation attached to
        this elliptic curve is ordinary at ell.

        INPUT:


        -  ``p`` - a prime ell - a prime (default: p)


        OUTPUT: bool

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.is_ordinary(37)
            True
            sage: E=EllipticCurve('32a1')
            sage: E.is_ordinary(2)
            False
            sage: [p for p in prime_range(50) if E.is_ordinary(p)]
            [5, 13, 17, 29, 37, 41]
        """
        if ell is None:
            ell = p
        return self.ap(ell) % p != 0

    def is_good(self, p, check=True):
        """
        Return True if `p` is a prime of good reduction for
        `E`.

        INPUT:


        -  ``p`` - a prime


        OUTPUT: bool

        EXAMPLES::

            sage: e = EllipticCurve('11a')
            sage: e.is_good(-8)
            Traceback (most recent call last):
            ...
            ValueError: p must be prime
            sage: e.is_good(-8, check=False)
            True
        """
        if check:
            if not arith.is_prime(p):
                raise ValueError, "p must be prime"
        return self.conductor() % p != 0


    def is_supersingular(self, p, ell=None):
        """
        Return True precisely when p is a prime of good reduction and the
        mod-p representation attached to this elliptic curve is
        supersingular at ell.

        INPUT:


        -  ``p`` - a prime ell - a prime (default: p)


        OUTPUT: bool

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.is_supersingular(37)
            False
            sage: E=EllipticCurve('32a1')
            sage: E.is_supersingular(2)
            False
            sage: E.is_supersingular(7)
            True
            sage: [p for p in prime_range(50) if E.is_supersingular(p)]
            [3, 7, 11, 19, 23, 31, 43, 47]
        """
        if ell is None:
            ell = p
        return self.is_good(p) and not self.is_ordinary(p, ell)

    def supersingular_primes(self, B):
        """
        Return a list of all supersingular primes for this elliptic curve
        up to and possibly including B.

        EXAMPLES::

            sage: e = EllipticCurve('11a')
            sage: e.aplist(20)
            [-2, -1, 1, -2, 1, 4, -2, 0]
            sage: e.supersingular_primes(1000)
            [2, 19, 29, 199, 569, 809]

        ::

            sage: e = EllipticCurve('27a')
            sage: e.aplist(20)
            [0, 0, 0, -1, 0, 5, 0, -7]
            sage: e.supersingular_primes(97)
            [2, 5, 11, 17, 23, 29, 41, 47, 53, 59, 71, 83, 89]
            sage: e.ordinary_primes(97)
            [7, 13, 19, 31, 37, 43, 61, 67, 73, 79, 97]
            sage: e.supersingular_primes(3)
            [2]
            sage: e.supersingular_primes(2)
            [2]
            sage: e.supersingular_primes(1)
            []
        """
        v = self.aplist(max(B, 3))
        P = rings.prime_range(max(B,3)+1)
        N = self.conductor()
        return [P[i] for i in [0,1] if P[i] <= B and v[i]%P[i]==0 and N%P[i] != 0] + \
                      [P[i] for i in range(2,len(v)) if v[i] == 0 and N%P[i] != 0]

    def ordinary_primes(self, B):
        """
        Return a list of all ordinary primes for this elliptic curve up to
        and possibly including B.

        EXAMPLES::

            sage: e = EllipticCurve('11a')
            sage: e.aplist(20)
            [-2, -1, 1, -2, 1, 4, -2, 0]
            sage: e.ordinary_primes(97)
            [3, 5, 7, 11, 13, 17, 23, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
            sage: e = EllipticCurve('49a')
            sage: e.aplist(20)
            [1, 0, 0, 0, 4, 0, 0, 0]
            sage: e.supersingular_primes(97)
            [3, 5, 13, 17, 19, 31, 41, 47, 59, 61, 73, 83, 89, 97]
            sage: e.ordinary_primes(97)
            [2, 11, 23, 29, 37, 43, 53, 67, 71, 79]
            sage: e.ordinary_primes(3)
            [2]
            sage: e.ordinary_primes(2)
            [2]
            sage: e.ordinary_primes(1)
            []
        """
        v = self.aplist(max(B, 3) )
        P = rings.prime_range(max(B,3) +1)
        return [P[i] for i in [0,1] if P[i] <= B and v[i]%P[i]!=0] +\
               [P[i] for i in range(2,len(v)) if v[i] != 0]

    def eval_modular_form(self, points, prec):
        """
        Evaluate the L-series of this elliptic curve at points in CC

        INPUT:


        -  ``points`` - a list of points in the half-plane of
           convergence

        -  ``prec`` - precision


        OUTPUT: A list of values L(E,s) for s in points

        .. note::

           Better examples are welcome.

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: E.eval_modular_form([1.5+I,2.0+I,2.5+I],0.000001)
            [0, 0, 0]
        """
        if not isinstance(points, (list,xrange)):
            try:
                points = list(points)
            except TypeError:
                return self.eval_modular_form([points],prec)
        an = self.pari_mincurve().ellan(prec)
        s = 0
        I = pari("I")
        pi = pari("Pi")
        c = pari(2)*pi*I
        ans = []
        for z in points:
            s = pari(0)
            r0 = (c*z).exp()
            r = r0
            for n in xrange(1,prec):
                s += an[n-1]*r
                r *= r0
            ans.append(s.python())
        return ans


    ########################################################################
    # Functions related to bounding the order of Sha (provably correctly!)
    # Heegner points and Kolyvagin's theorem
    ########################################################################

    def sha(self):
        """
        Return an object of class
        'sage.schemes.elliptic_curves.sha_tate.Sha' attached to this
        elliptic curve.

        This can be used in functions related to bounding the order of Sha
        (The Tate-Shafarevich group of the curve).

        EXAMPLES::

            sage: E=EllipticCurve('37a1')
            sage: S=E.sha()
            sage: S
            Shafarevich-Tate group for the Elliptic Curve defined by y^2 + y = x^3 - x over Rational Field
            sage: S.bound_kolyvagin()
            ([2], 1)
        """
        try:
            return self.__sha
        except AttributeError:
            from sha_tate import Sha
            self.__sha = Sha(self)
            return self.__sha

    def satisfies_heegner_hypothesis(self, D):
        """
        Returns True precisely when D is a fundamental discriminant that
        satisfies the Heegner hypothesis for this elliptic curve.

        EXAMPLES::

            sage: E = EllipticCurve('11a1')
            sage: E.satisfies_heegner_hypothesis(-7)
            True
            sage: E.satisfies_heegner_hypothesis(-11)
            False
        """
        if not number_field.is_fundamental_discriminant(D):
            return False
        if arith.GCD(D, self.conductor()) != 1:
            return False
        for p, _ in factor(self.conductor()):
            if kronecker_symbol(D,p) != 1:
                return False
        return True

    def heegner_discriminants(self, bound):
        """
        Return the list of self's Heegner discriminants between -1 and
        -bound.

        INPUT:


        -  ``bound (int)`` - upper bound for -discriminant


        OUTPUT: The list of Heegner discriminants between -1 and -bound for
        the given elliptic curve.

        EXAMPLE::

            sage: E=EllipticCurve('11a')
            sage: E.heegner_discriminants(30)
            [-7, -8, -19, -24]
        """
        return [-D for D in xrange(1,bound) if self.satisfies_heegner_hypothesis(-D)]

    def heegner_discriminants_list(self, n):
        """
        Return the list of self's first n Heegner discriminants smaller
        than -5.

        INPUT:


        -  ``n (int)`` - the number of discriminants to
           compute


        OUTPUT: The list of the first n Heegner discriminants smaller than
        -5 for the given elliptic curve.

        EXAMPLE::

            sage: E=EllipticCurve('11a')
            sage: E.heegner_discriminants_list(4)
            [-7, -8, -19, -24]
        """
        v = []
        D = -5
        while len(v) < n:
            while not self.satisfies_heegner_hypothesis(D):
                D -= 1
            v.append(D)
            D -= 1
        return v

    def heegner_point_height(self, D, prec=2):
        """
        Use the Gross-Zagier formula to compute the Neron-Tate canonical
        height over K of the Heegner point corresponding to D, as an
        Interval (since it's computed to some precision using
        L-functions).

        INPUT:


        -  ``D (int)`` - fundamental discriminant (=/= -3, -4)

        -  ``prec (int)`` - (default: 2), use prec\*sqrt(N) +
           20 terms of L-series in computations, where N is the conductor.


        OUTPUT: Interval that contains the height of the Heegner point.

        EXAMPLE::

            sage: E = EllipticCurve('11a')
            sage: E.heegner_point_height(-7)
            0.22227?
        """

        if not self.satisfies_heegner_hypothesis(D):
            raise ArithmeticError, "Discriminant (=%s) must be a fundamental discriminant that satisfies the Heegner hypothesis."%D
        if D == -3 or D == -4:
            raise ArithmeticError, "Discriminant (=%s) must not be -3 or -4."%D
        eps = self.root_number()
        L1_vanishes = self.lseries().L1_vanishes()
        if eps == 1 and L1_vanishes:
            return IR(0) # rank even hence >= 2, so Heegner point is torsion.
        alpha = R(sqrt(abs(D)))/(2*self.period_lattice().complex_area())
        F = self.quadratic_twist(D)
        E = self
        k_E = prec*sqrt(E.conductor()) + 20
        k_F = prec*sqrt(F.conductor()) + 20

        MIN_ERR = R('1e-6')  # we assume that regulator and
                             # discriminant, etc., computed to this accuracy (which is easily the case).
                             # this should be made more intelligent / rigorous relative
                             # to the rest of the system.
        if eps == 1:   # E has even rank
            LF1, err_F = F.lseries().deriv_at1(k_F)
            LE1, err_E = E.lseries().at1(k_E)
            err_F = max(err_F, MIN_ERR)
            err_E = max(err_E, MIN_ERR)
            return IR(alpha-MIN_ERR,alpha+MIN_ERR) * IR(LE1-err_E,LE1+err_E) * IR(LF1-err_F,LF1+err_F)

        else:          # E has odd rank
            LE1, err_E = E.lseries().deriv_at1(k_E)
            LF1, err_F = F.lseries().at1(k_F)
            err_F = max(err_F, MIN_ERR)
            err_E = max(err_E, MIN_ERR)
            return IR(alpha-MIN_ERR,alpha+MIN_ERR) * IR(LE1-err_E,LE1+err_E) * IR(LF1-err_F,LF1+err_F)


    def heegner_index(self, D,  min_p=2, prec=5, verbose=False):
        r"""
        Return an interval that contains the index of the Heegner
        point `y_K` in the group of K-rational points modulo torsion
        on this elliptic curve, computed using the Gross-Zagier
        formula and/or a point search, or the index divided by `2`.

        .. note::

           If ``min_p`` is bigger than 2 then the index can be off by
           any prime less than ``min_p``. This function returns the
           index divided by `2` exactly when
           `E(\mathbb{Q})_{/tor}` has index `2` in
           `E(K)_{/tor}`.

        INPUT:


        -  ``D (int)`` - Heegner discriminant

        -  ``min_p (int)`` - (default: 2) only rule out primes
           = min_p dividing the index.

        -  ``verbose (bool)`` - (default: False); print lots of
           mwrank search status information when computing regulator

        -  ``prec (int)`` - (default: 5), use prec\*sqrt(N) +
           20 terms of L-series in computations, where N is the conductor.


        OUTPUT: an interval that contains the index

        EXAMPLES::

            sage: E = EllipticCurve('11a')
            sage: E.heegner_discriminants(50)
            [-7, -8, -19, -24, -35, -39, -40, -43]
            sage: E.heegner_index(-7)
            1.00000?

        ::

            sage: E = EllipticCurve('37b')
            sage: E.heegner_discriminants(100)
            [-3, -4, -7, -11, -40, -47, -67, -71, -83, -84, -95]
            sage: E.heegner_index(-95)          # long time (1 second)
            2.00000?

        This tests doing direct computation of the Mordell-Weil group.

        ::

            sage: EllipticCurve('675b').heegner_index(-11)
            3.0000?

        Currently discriminants -3 and -4 are not supported::

            sage: E.heegner_index(-3)
            Traceback (most recent call last):
            ...
            ArithmeticError: Discriminant (=-3) must not be -3 or -4.

        The curve 681b returns an interval that contains `3/2`.
        This is because `E(\mathbb{Q})` is not saturated in
        `E(K)`. The true index is `3`::

            sage: E = EllipticCurve('681b')
            sage: I = E.heegner_index(-8); I
            1.50000?
            sage: 2*I
            3.0000?

        In fact, whenever the returned index has a denominator of
        `2`, the true index is got by multiplying the returned
        index by `2`. Unfortunately, this is not an if and only if
        condition, i.e., sometimes the index must be multiplied by
        `2` even though the denominator is not `2`.
        """
        # First compute upper bound on height of Heegner point.
        tm = misc.verbose("computing heegner point height...")
        h0 = self.heegner_point_height(D, prec=prec)

        # We divide by 2 to get the height **over Q** of the
        # Heegner point on the twist.

        ht = h0/2
        misc.verbose('Height of heegner point = %s'%ht, tm)

        if self.root_number() == 1:
            F = self.quadratic_twist(D)
        else:
            F = self
        h  = ht.upper()
        misc.verbose("Heegner height bound = %s"%h)
        B = F.CPS_height_bound()
        misc.verbose("CPS bound = %s"%B)
        c = h/(min_p**2) + B
        misc.verbose("Search would have to be up to height = %s"%c)

        if c > _MAX_HEIGHT or F is self:
            misc.verbose("Doing direct computation of MW group.")
            reg = F.regulator()
            return self.__adjust_heegner_index(ht/IR(reg))

        # Do naive search to eliminate possibility that Heegner point
        # is divisible by p<min_p, without finding Heegner point.
        misc.verbose("doing point search")
        P = F.point_search(c, verbose=verbose)
        misc.verbose("done with point search")
        P = [x for x in P if x.order() == oo]
        if len(P) == 0:
            return IR(1)

        misc.verbose("saturating")
        S, I, reg = F.saturation(P, verbose=verbose)
        misc.verbose("done saturating")
        return self.__adjust_heegner_index(ht/IR(reg))

    def __adjust_heegner_index(self, a):
        r"""
        Take the square root of the interval that contains the Heegner
        index.

        EXAMPLES::

            sage: E = EllipticCurve('11a1')
            sage: a = RIF(sqrt(2))-1.4142135623730951
            sage: E._EllipticCurve_rational_field__adjust_heegner_index(a)
            1.?e-8
        """
        if a.lower() < 0:
            a = IR((0, a.upper()))
        return a.sqrt()


    def heegner_index_bound(self, D=0,  prec=5, verbose=True, max_height=_MAX_HEIGHT):
        """
        Assume self has rank 0.

        Return a list v of primes such that if an odd prime p divides
        the index of the Heegner point in the group of rational points
        *modulo torsion*, then p is in v.

        If 0 is in the interval of the height of the Heegner point
        computed to the given prec, then this function returns v =
        0. This does not mean that the Heegner point is torsion, just
        that it is very likely torsion.

        If we obtain no information from a search up to max_height,
        e.g., if the Siksek et al. bound is bigger than max_height,
        then we return v = -1.

        INPUT:


        -  ``D (int)`` - (default: 0) Heegner discriminant; if
           0, use the first discriminant -4 that satisfies the Heegner
           hypothesis

        -  ``verbose (bool)`` - (default: True)

        -  ``prec (int)`` - (default: 5), use prec\*sqrt(N) +
           20 terms of L-series in computations, where N is the conductor.

        -  ``max_height (float)`` - should be = 21; bound on
           logarithmic naive height used in point searches. Make smaller to
           make this function faster, at the expense of possibly obtaining a
           worse answer. A good range is between 13 and 21.


        OUTPUT:


        -  ``v`` - list or int (bad primes or 0 or -1)

        -  ``D`` - the discriminant that was used (this is
           useful if D was automatically selected).


        EXAMPLES::

            sage: E = EllipticCurve('11a1')
            sage: E.heegner_index_bound(verbose=False)
            ([2], -7)
        """
        max_height = min(float(max_height), _MAX_HEIGHT)
        if self.root_number() != 1:
            raise RuntimeError, "The rank must be 0."

        if D == 0:
            D = -5
            while not self.satisfies_heegner_hypothesis(D):
                D -= 1

        # First compute upper bound on Height of Heegner point.
        ht = self.heegner_point_height(D, prec=prec)
        if 0 in ht:
            return 0, D
        F = self.quadratic_twist(D)
        h  = ht.upper()
        misc.verbose("Heegner height bound = %s"%h)
        B = F.CPS_height_bound()
        misc.verbose("CPS bound = %s"%B)
        H = h
        p = 3
        while True:
            c = h/(2*p**2) + B
            if c < max_height:
                break
            if p > 100:
                break
            p = next_prime(p)
        misc.verbose("Using p = %s"%p)

        if c > max_height:
            misc.verbose("No information by searching only up to max_height (=%s)."%c)
            return -1, D

        misc.verbose("Searching up to height = %s"%c)
        eps = 10e-5

        def _bound(P):
            """
            We will use this function below in two places. It bounds the index
            using a nontrivial point.
            """
            assert len(P) == 1

            S, I, reg = F.saturation(P, verbose=verbose)
            h = IR(reg-eps,reg+eps)
            ind2 = ht/(h/2)
            misc.verbose("index squared = %s"%ind2)
            ind = ind2.sqrt()
            misc.verbose("index = %s"%ind)
            # Compute upper bound on square root of index.
            if ind.absolute_diameter() < 1:
                t, i = ind.is_int()
                if t:   # unique integer in interval, so we've found exact index squared.
                    return arith.prime_divisors(i), D
            raise RuntimeError, "Unable to compute bound for e=%s, D=%s (try increasing precision)"%(self,D)

        # First try a quick search, in case we get lucky and find
        # a generator.
        P = F.point_search(13, verbose=verbose)
        P = [x for x in P if x.order() == oo]
        if len(P) > 0:
            return _bound(P)

        # Do search to eliminate possibility that Heegner point is
        # divisible by primes up to p, without finding Heegner point.
        P = F.point_search(c, verbose=verbose)
        P = [x for x in P if x.order() == oo]
        if len(P) == 0:
            # We've eliminated the possibility of a divisor up to p.
            return rings.prime_range(3,p), D
        else:
            return _bound(P)


    #################################################################################
    def _heegner_index_in_EK(self, D):
        """
        Return the index of the sum of E(QQ)/tor + E^D(QQ)/tor in E(K)/tor.

        INPUT:
            D -- negative integer; the Heegner discriminant

        OUTPUT:
            a power of 2 -- the given index

        EXAMPLES:
        We compute the index for a rank 2 curve and found that it is 2.
            sage: E = EllipticCurve('389a')
            sage: E._heegner_index_in_EK(-7)
            2

        We explicitly verify in the above example that indeed that
        index is divisibly by 2 by writing down a generator of
        E(QQ)/tor + E^D(QQ)/tor that is divisible by 2 in E(K).
            sage: F = E.quadratic_twist(-7)
            sage: K = QuadraticField(-7,'a')
            sage: G = E.change_ring(K)
            sage: phi = F.change_ring(K).isomorphism_to(G)
            sage: P = G(E.0) + G(E.1) + G(phi(F.0)); P
            (-867/3872*a - 3615/3872 : -18003/170368*a - 374575/170368 : 1)
            sage: P.division_points(2)
            [(1/8*a + 5/8 : -5/16*a - 9/16 : 1)]

        """
        # check conditions, then use cache if possible.
        if not self.satisfies_heegner_hypothesis(D):
            raise ValueError, "D (=%s) must satisfy the Heegner hypothesis"%D
        try:
            return self.__heegner_index_in_EK[D]
        except AttributeError:
            self.__heegner_index_in_EK = {}
        except KeyError:
            pass

        #####################################################################
        # THE ALGORITHM:
        #
        # For an element P of an abelian group A, let [P] denote the
        # equivalence class of P in the quotient A/A_tor of A by
        # its torsion subgroup.   Then for P in E(Q) + E^D(QQ), we
        # have that [P] is divisible by 2 in E(K)/tor if and only
        # there is R in E(K) such that 2*[R] = [P], and this is
        # only if there is R in E(K) and t in E(K)_tor such that
        #          2*R = P + t.
        #
        # Using complex conjugation, one sees that the quotient
        # group E(K)/tor / ( E(Q)/tor + E^D(Q)/tor ) is killed by 2.
        # So to compute the order of this group we run through
        # representatives P for A/(2A) where A = E(Q)/tor + E^D(Q)/tor,
        # and for each we see whether there is a torsion point t in E(K)
        # such that P + t is divisible by 2.   Also, we have
        #    2 | P+t  <==> 2 | P+n*t for any odd integer n,
        # so we may assume t is of 2-power order.
        #####################################################################

        E     = self  # nice shortcut
        F     = E.quadratic_twist(D).minimal_model()
        K     = rings.QuadraticField(D,'a')

        # Define a map phi that we'll use to put the points of E^D(QQ)
        # into E(K):
        G     = E.change_ring(K)
        G2    = F.change_ring(K)
        phi   = G2.isomorphism_to(G)

        # Basis for E(Q)/tor oplus E^D(QQ)/tor in E(K):
        basis = [G(z) for z in E.gens()] + [G(phi(z)) for z in F.gens()]
        # Make a list of the 2-power order torsion points in E(K), including 0.
        T     = [G(z) for z in G.torsion_subgroup().list() if z.order() == 1 or
                ((z.order() % 2 == 0 and len(z.order().factor()) == 1))]

        r     = len(basis)   # rank
        V     = rings.QQ**r
        B     = []

        # Iterate through reps for A/(2*A) creating vectors in (1/2)*ZZ^r
        for v in rings.GF(2)**r:
            if not v: continue
            P = sum([basis[i] for i in range(r) if v[i]])
            for t in T:
                if (P+t).is_divisible_by(2):
                    B.append(V(v)/2)

        A = rings.ZZ**r
        # Take span of our vectors in (1/2)*ZZ^r, along with ZZ^r.  This is E(K)/tor.
        W     = V.span(B,rings.ZZ) + A

        # Compute the index in E(K)/tor of A = E(Q)/tor + E^D(Q)/tor, cache, and return.
        index = A.index_in(W)
        self.__heegner_index_in_EK[D] = index
        return index

    def heegner_sha_an(self, D, prec=53):
        """
        Return the conjectural (analytic) order of Sha

        INPUT:
            D -- negative integer; the Heegner discriminant
            prec -- integer (default: 53); bits of precision to
                    compute analytic order of Sha

        OUTPUT:
            sha -- conjectural order of sha, as a floating point number

        NOTE: Often you'll want to do proof.elliptic_curve(False) when
        using this function, since often the twisted elliptic curves
        that come up have enormous conductor, and Sha is nontrivial,
        which makes provably finding the Mordell-Weil group using
        2-descent difficult.

        EXAMPLES:
        An example where E has rank 11.
            sage: E = EllipticCurve('11a')
            sage: E.heegner_sha_an(-7)                                  # long
            1.00000000000000

        The cache works:
            sage: E.heegner_sha_an(-7) is E.heegner_sha_an(-7)          # long
            True

        Lower precision.
            sage: E.heegner_sha_an(-7,10)                               # long
            1.0

        Checking that the cache works for any precision.
            sage: E.heegner_sha_an(-7,10) is E.heegner_sha_an(-7,10)    # long
            True

        A rank 1 curve with nontrivial Sha over the quadratic
        imaginary field K; however, there is no Sha for E over QQ or
        for the quadratic twist of E.
            sage: E = EllipticCurve('37a')
            sage: E.heegner_sha_an(-40)                                 # long
            4.00000000000000
            sage: E.quadratic_twist(-40).sha().an()                     # long
            1
            sage: E.sha().an()                                          # long
            1

        A rank 2 curve.
            sage: E = EllipticCurve('389a')                             # long
            sage: E.heegner_sha_an(-7)                                  # long
            1.00000000000000

        If we remove the hypothesis that E(K) has rank 1 in Conjecture
        2.3 in [Gross-Zagier, 1986, page 311], then that conjecture is
        falase, as the following example shows:
            sage: E = EllipticCurve('65a')                              # long
            sage: E.heegner_sha_an(-56)                                 # long
            1.00000000000000
            sage: E.torsion_order()                                     # long
            2
            sage: E.tamagawa_product()                                  # long
            1
            sage: E.quadratic_twist(-56).rank()                         # long
            2
        """
        # check conditions, then return from cache if possible.
        if not self.satisfies_heegner_hypothesis(D):
            raise ValueError, "D (=%s) must satisfy the Heegner hypothesis"%D
        try:
            return self.__heegner_sha_an[(D,prec)]
        except AttributeError:
            self.__heegner_sha_an = {}
        except KeyError:
            pass

        # Use the BSD conjecture over the quadratic imaginary K --
        # see page 311 of [Gross-Zagier, 1986] for the formula.
        E   = self  # notational convenience
        F   = E.quadratic_twist(D).minimal_model()
        K   = rings.QuadraticField(D,'a')

        # Compute each of the quantities in BSD
        #  - The torsion subgroup over K.
        T   = E.change_ring(K).torsion_order()

        #  - The product of the Tamagawa numbers, which because D is
        #    coprime to N is just the square of the product of the
        #    Tamagawa numbers over QQ for E.  (we square below in the
        #    BSD formula)
        cqprod = E.tamagawa_product()

        #  - The leading term of the L-series, as a product of two
        #  other L-series.
        rE  = E.rank()
        rF = F.rank()
        L_E = E.lseries().dokchitser(prec).derivative(1, rE)
        L_F = F.lseries().dokchitser(prec).derivative(1, rF)
        #    NOTE: The binomial coefficient in the following formula
        #    for the leading term in terms of the other two leading
        #    terms comes from the product rule for the derivative.
        #    You can think this through or just type something like
        #      f = function('f',x); g = function('g',x); diff(f*g,6)
        #    into Sage to be convinced.
        L = rings.binomial(rE + rF, rE) * (L_E * L_F / (rings.factorial(rE+rF)) )

        #  - ||omega||^2 -- the period.  It's twice the volume of the
        #    period lattice.  See the following paper for a derivation:
        #    "Verification of the Birch and Swinnerton-Dyer Conjecture
        #     for Specific Elliptic Curves", G. Grigorov, A. Jorza, S. Patrikis,
        #     C. Patrascu, W. Stein
        omega = 2 * abs(E.period_lattice().basis_matrix().det())

        #  - The regulator.
        #    First we compute the regualtor of the subgroup E(QQ) + E^D(QQ)
        #    of E(K).   The factor of 2 in the regulator
        #    accounts for the fact that the height over K is twice the
        #    height over QQ, i.e., for P in E(QQ) we have h_K(P,P) =
        #    2*h_Q(P,P).  See, e.g., equation (6.4) on page 230 of
        #    [Gross-Zagier, 1986].
        Reg_prod = 2**(rE + rF) * E.regulator(precision=prec) * F.regulator(precision=prec)
        #    Next we call off to the _heegner_index_in_EK function, which
        #    saturates the group E(QQ) + E^D(QQ) in E(K), given us the index,
        #    which must be a power of 2, since E(QQ) is the +1 eigenspace for
        #    complex conjugation, and E^D(QQ) is the -1 eigenspace.
        ind = self._heegner_index_in_EK(D)
        #    Finally, we know the regulator of E(K).
        Reg = Reg_prod / ind**2

        #  - Square root of the absolute value of the discriminant.  This is
        #    easy; we just make sure the D passed in is an integer, so we
        #    can call sqrt with the chosen precision.
        sqrtD = Integer(abs(D)).sqrt(prec=prec)

        #  - Done: Finally, we plug everything into the BSD formula to get the
        #    analytic order of Sha.
        sha_an = (L * T**2 * sqrtD) / (omega * Reg * cqprod**2)

        #  - We cache and return the answer.
        self.__heegner_sha_an[(D,prec)] = sha_an
        return sha_an


    #################################################################################

    padic_regulator = padics.padic_regulator

    padic_height_pairing_matrix = padics.padic_height_pairing_matrix

    padic_height = padics.padic_height
    padic_height_via_multiply = padics.padic_height_via_multiply

    padic_sigma = padics.padic_sigma
    padic_sigma_truncated = padics.padic_sigma_truncated

    padic_E2 = padics.padic_E2

    matrix_of_frobenius = padics.matrix_of_frobenius

    # def weierstrass_p(self):
    #         # TODO: add allowing negative valuations for power series
    #         return 1/t**2 + a1/t + rings.frac(1,12)*(a1-8*a2) -a3*t \
    #                - (a4+a1*a3)*t**2  + O(t**3)


    def mod5family(self):
        """
        Return the family of all elliptic curves with the same mod-5
        representation as self.

        EXAMPLES::

            sage: E=EllipticCurve('32a1')
            sage: E.mod5family()
            Elliptic Curve defined by y^2  = x^3 + 4*x over Fraction Field of Univariate Polynomial Ring in t over Rational Field
        """
        E = self.short_weierstrass_model()
        a = E.a4()
        b = E.a6()
        return mod5family.mod5family(a,b)

    def tate_curve(self, p):
        r"""
        Creates the Tate Curve over the `p`-adics associated to
        this elliptic curves.

        This Tate curve a `p`-adic curve with split multiplicative
        reduction of the form `y^2+xy=x^3+s_4 x+s_6` which is
        isomorphic to the given curve over the algebraic closure of
        `\mathbb{Q}_p`. Its points over `\mathbb{Q}_p`
        are isomorphic to `\mathbb{Q}_p^{\times}/q^{\mathbb{Z}}`
        for a certain parameter `q\in\mathbb{Z}_p`.

        INPUT:

        p - a prime where the curve has multiplicative reduction.

        EXAMPLES::

            sage: e = EllipticCurve('130a1')
            sage: e.tate_curve(2)
            2-adic Tate curve associated to the Elliptic Curve defined by y^2 + x*y + y = x^3 - 33*x + 68 over Rational Field

        The input curve must have multiplicative reduction at the prime.

        ::

            sage: e.tate_curve(3)
            Traceback (most recent call last):
            ...
            ValueError: The elliptic curve must have multiplicative reduction at 3

        We compute with `p=5`::

            sage: T = e.tate_curve(5); T
            5-adic Tate curve associated to the Elliptic Curve defined by y^2 + x*y + y = x^3 - 33*x + 68 over Rational Field

        We find the Tate parameter `q`::

            sage: T.parameter(prec=5)
            3*5^3 + 3*5^4 + 2*5^5 + 2*5^6 + 3*5^7 + O(5^8)

        We compute the `L`-invariant of the curve::

            sage: T.L_invariant(prec=10)
            5^3 + 4*5^4 + 2*5^5 + 2*5^6 + 2*5^7 + 3*5^8 + 5^9 + O(5^10)
        """
        try:
            return self._tate_curve[p]
        except AttributeError:
            self._tate_curve = {}
        except KeyError:
            pass

        Eq = ell_tate_curve.TateCurve(self,p)
        self._tate_curve[p] = Eq
        return Eq

    def height(self, precision=None):
        """
        Returns the real height of this elliptic curve. This is used in
        integral_points()

        INPUT:


        -  ``precision`` - desired real precision of the result
           (default real precision if None)


        EXAMPLES::

            sage: E=EllipticCurve('5077a1')
            sage: E.height()
            17.4513334798896
            sage: E.height(100)
            17.451333479889612702508579399
            sage: E=EllipticCurve([0,0,0,0,1])
            sage: E.height()
            1.38629436111989
            sage: E=EllipticCurve([0,0,0,1,0])
            sage: E.height()
            7.45471994936400
        """
        if precision is None:
            precision = RealField().precision()
        R = RealField(precision)
        c4 = self.c4()
        c6 = self.c6()
        j = self.j_invariant()
        log_g2 = R((c4/12)).abs().log()
        log_g3 = R((c6/216)).abs().log()

        if j == 0:
            h_j = R(1)
        else:
            h_j = max(log(R(abs(j.numerator()))), log(R(abs(j.denominator()))))
        if (self.c4() != 0) and (self.c6() != 0):
            h_gs = max(1, log_g2, log_g3)
        elif c4 == 0:
            if c6 == 0:
                return max(1,h_j)
            h_gs = max(1, log_g3)
        else:
            h_gs = max(1, log_g2)
        return max(R(1),h_j, h_gs)

    def lll_reduce(self, points, height_matrix=None):
        """
        Returns an LLL-reduced basis from a given basis, with transform
        matrix.

        INPUT:


        -  ``points`` - a list of points on this elliptic
           curve, which should be independent.

        -  ``height_matrix`` - the height-pairing matrix of
           the points, or None. If None, it will be computed.


        OUTPUT: A tuple (newpoints,U) where U is a unimodular integer
        matrix, new_points is the transform of points by U, such that
        new_points has LLL-reduced height pairing matrix

        .. note::

           If the input points are not independent, the output depends
           on the undocumented behaviour of pari's ``qflllgram()``
           function when applied to a gram matrix which is not
           positive definite.

        EXAMPLE::

            sage: E = EllipticCurve([0, 1, 1, -2, 42])
            sage: Pi = E.gens(); Pi
            [(-4 : 1 : 1), (-3 : 5 : 1), (-11/4 : 43/8 : 1), (-2 : 6 : 1)]
            sage: Qi, U = E.lll_reduce(Pi)
            sage: Qi
            [(0 : 6 : 1), (1 : -7 : 1), (-4 : 1 : 1), (-3 : 5 : 1)]
            sage: U.det()
            1
            sage: E.regulator_of_points(Pi)
            4.59088036960574
            sage: E.regulator_of_points(Qi)
            4.59088036960574

        ::

            sage: E = EllipticCurve([1,0,1,-120039822036992245303534619191166796374,504224992484910670010801799168082726759443756222911415116])
            sage: xi = [2005024558054813068,\
            -4690836759490453344,\
            4700156326649806635,\
            6785546256295273860,\
            6823803569166584943,\
            7788809602110240789,\
            27385442304350994620556,\
            54284682060285253719/4,\
            -94200235260395075139/25,\
            -3463661055331841724647/576,\
            -6684065934033506970637/676,\
            -956077386192640344198/2209,\
            -27067471797013364392578/2809,\
            -25538866857137199063309/3721,\
            -1026325011760259051894331/108241,\
            9351361230729481250627334/1366561,\
            10100878635879432897339615/1423249,\
            11499655868211022625340735/17522596,\
            110352253665081002517811734/21353641,\
            414280096426033094143668538257/285204544,\
            36101712290699828042930087436/4098432361,\
            45442463408503524215460183165/5424617104,\
            983886013344700707678587482584/141566320009,\
            1124614335716851053281176544216033/152487126016]
            sage: points = [E.lift_x(x) for x in xi]
            sage: newpoints, U = E.lll_reduce(points) # long time (2m)
            sage: [P[0] for P in newpoints]           # long time
            [6823803569166584943, 5949539878899294213, 2005024558054813068, 5864879778877955778, 23955263915878682727/4, 5922188321411938518, 5286988283823825378, 11465667352242779838, -11451575907286171572, 3502708072571012181, 1500143935183238709184/225, 27180522378120223419/4, -5811874164190604461581/625, 26807786527159569093, 7041412654828066743, 475656155255883588, 265757454726766017891/49, 7272142121019825303, 50628679173833693415/4, 6951643522366348968, 6842515151518070703, 111593750389650846885/16, 2607467890531740394315/9, -1829928525835506297]
        """
        r = len(points)
        if height_matrix is None:
            height_matrix = self.height_pairing_matrix(points)
        U = pari(height_matrix).lllgram().python()
        new_points = [sum([U[j,i]*points[j] for j in range(r)]) for i in range(r)]
        return new_points, U

    def antilogarithm(self, z, prec=None):
        """
        Returns the rational point (if any) associated to this complex
        number; the inverse of the elliptic logarithm function.

        INPUT:


        -  ``z`` - a complex number representing an element of
           CC/L where L is the period lattice of the elliptic curve

        -  ``precision`` - an integer specifying the precision
           (in bits) which will be used for the computation (default real
           precision if None)


        OUTPUT: The rational point which is the image of z under the
        Weierstrass parametrization, if it exists and can be determined
        from z with default precision.

        .. note::

           This uses the function ellztopoint from the pari library

        TODO: Extend the wrapping of ellztopoint() to allow passing of the
        precision parameter.
        """

        E_pari = self.pari_curve(prec)
        try:
            coords = E_pari.ellztopoint(z)
            if len(coords) == 1:
                return self(0)
            return self([CC(xy).real().simplest_rational() for xy in coords])
        except TypeError:
            raise ValueError, "No rational point computable from z"

    def integral_points(self, mw_base='auto', both_signs=False, verbose=False):
        """
        Computes all integral points (up to sign) on this elliptic curve.

        INPUT:


        -  ``mw_base`` - list of EllipticCurvePoint generating
           the Mordell-Weil group of E (default: 'auto' - calls self.gens())

        -  ``both_signs`` - True/False (default False): if
           True the output contains both P and -P, otherwise only one of each
           pair.

        -  ``verbose`` - True/False (default False): if True,
           some details of the computation are output


        OUTPUT: A sorted list of all the integral points on E (up to sign
        unless both_signs is True)

        .. note::

           The complexity increases exponentially in the rank of curve
           E. The computation time (but not the output!) depends on
           the Mordell-Weil basis. If mw_base is given but is not a
           basis for the Mordell-Weil group (modulo torsion), integral
           points which are not in the subgroup generated by the given
           points will almost certainly not be listed.

        EXAMPLES: A curve of rank 3 with no torsion points

        ::

            sage: E=EllipticCurve([0,0,1,-7,6])
            sage: P1=E.point((2,0)); P2=E.point((-1,3)); P3=E.point((4,6))
            sage: a=E.integral_points([P1,P2,P3]); a
            [(-3 : 0 : 1), (-2 : 3 : 1), (-1 : 3 : 1), (0 : 2 : 1), (1 : 0 : 1), (2 : 0 : 1), (3 : 3 : 1), (4 : 6 : 1), (8 : 21 : 1), (11 : 35 : 1), (14 : 51 : 1), (21 : 95 : 1), (37 : 224 : 1), (52 : 374 : 1), (93 : 896 : 1), (342 : 6324 : 1), (406 : 8180 : 1), (816 : 23309 : 1)]

        ::

            sage: a = E.integral_points([P1,P2,P3], verbose=True)
            Using mw_basis  [(2 : 0 : 1), (3 : -4 : 1), (8 : -22 : 1)]
            e1,e2,e3:  -3.0124303725933... 1.0658205476962... 1.94660982489710
            Minimal eigenvalue of height pairing matrix:  0.63792081458500...
            x-coords of points on compact component with  -3 <=x<= 1
            [-3, -2, -1, 0, 1]
            x-coords of points on non-compact component with  2 <=x<= 6
            [2, 3, 4]
            starting search of remaining points using coefficient bound  5
            x-coords of extra integral points:
            [2, 3, 4, 8, 11, 14, 21, 37, 52, 93, 342, 406, 816]
            Total number of integral points: 18

        It is not necessary to specify mw_base; if it is not provided,
        then the Mordell-Weil basis must be computed, which may take
        much longer.

        ::

            sage: E=EllipticCurve([0,0,1,-7,6])
            sage: a=E.integral_points(both_signs=True); a
            [(-3 : -1 : 1), (-3 : 0 : 1), (-2 : -4 : 1), (-2 : 3 : 1), (-1 : -4 : 1), (-1 : 3 : 1), (0 : -3 : 1), (0 : 2 : 1), (1 : -1 : 1), (1 : 0 : 1), (2 : -1 : 1), (2 : 0 : 1), (3 : -4 : 1), (3 : 3 : 1), (4 : -7 : 1), (4 : 6 : 1), (8 : -22 : 1), (8 : 21 : 1), (11 : -36 : 1), (11 : 35 : 1), (14 : -52 : 1), (14 : 51 : 1), (21 : -96 : 1), (21 : 95 : 1), (37 : -225 : 1), (37 : 224 : 1), (52 : -375 : 1), (52 : 374 : 1), (93 : -897 : 1), (93 : 896 : 1), (342 : -6325 : 1), (342 : 6324 : 1), (406 : -8181 : 1), (406 : 8180 : 1), (816 : -23310 : 1), (816 : 23309 : 1)]

        An example with negative discriminant::

            sage: EllipticCurve('900d1').integral_points()
            [(-11 : 27 : 1), (-4 : 34 : 1), (4 : 18 : 1), (16 : 54 : 1)]

        Another example with rank 5 and no torsion points

        ::

            sage: E=EllipticCurve([-879984,319138704])
            sage: P1=E.point((540,1188)); P2=E.point((576,1836))
            sage: P3=E.point((468,3132)); P4=E.point((612,3132))
            sage: P5=E.point((432,4428))
            sage: a=E.integral_points([P1,P2,P3,P4,P5]); len(a)  # long time (400s!)
            54

        The bug reported on trac #4525 is now fixed::

            sage: EllipticCurve('91b1').integral_points()
            [(-1 : 3 : 1), (1 : 0 : 1), (3 : 4 : 1)]

        ::

            sage: [len(e.integral_points(both_signs=False)) for e in cremona_curves([11..100])] # long time
            [2, 0, 2, 3, 2, 1, 3, 0, 2, 4, 2, 4, 3, 0, 0, 1, 2, 1, 2, 0, 2, 1, 0, 1, 3, 3, 1, 1, 4, 2, 3, 2, 0, 0, 5, 3, 2, 2, 1, 1, 1, 0, 1, 3, 0, 1, 0, 1, 1, 3, 6, 1, 2, 2, 2, 0, 0, 2, 3, 1, 2, 2, 1, 1, 0, 3, 2, 1, 0, 1, 0, 1, 3, 3, 1, 1, 5, 1, 0, 1, 1, 0, 1, 2, 0, 2, 0, 1, 1, 3, 1, 2, 2, 4, 4, 2, 1, 0, 0, 5, 1, 0, 1, 2, 0, 2, 2, 0, 0, 0, 1, 0, 3, 1, 5, 1, 2, 4, 1, 0, 1, 0, 1, 0, 1, 0, 2, 2, 0, 0, 1, 0, 1, 1, 4, 1, 0, 1, 1, 0, 4, 2, 0, 1, 1, 2, 3, 1, 1, 1, 1, 6, 2, 1, 1, 0, 2, 0, 6, 2, 0, 4, 2, 2, 0, 0, 1, 2, 0, 2, 1, 0, 3, 1, 2, 1, 4, 6, 3, 2, 1, 0, 2, 2, 0, 0, 5, 4, 1, 0, 0, 1, 0, 2, 2, 0, 0, 2, 3, 1, 3, 1, 1, 0, 1, 0, 0, 1, 2, 2, 0, 2, 0, 0, 1, 2, 0, 0, 4, 1, 0, 1, 1, 0, 1, 2, 0, 1, 4, 3, 1, 2, 2, 1, 1, 1, 1, 6, 3, 3, 3, 3, 1, 1, 1, 1, 1, 0, 7, 3, 0, 1, 3, 2, 1, 0, 3, 2, 1, 0, 2, 2, 6, 0, 0, 6, 2, 2, 3, 3, 5, 5, 1, 0, 6, 1, 0, 3, 1, 1, 2, 3, 1, 2, 1, 1, 0, 1, 0, 1, 0, 5, 5, 2, 2, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1]

        The bug reported at #4897 is now fixed::

            sage: [P[0] for P in EllipticCurve([0,0,0,-468,2592]).integral_points()]
            [-24, -18, -14, -6, -3, 4, 6, 18, 21, 24, 36, 46, 102, 168, 186, 381, 1476, 2034, 67246]

        .. note::

           This function uses the algorithm given in [Co1].

        REFERENCES:

        - [Co1] Cohen H., Number Theory Vol I: Tools and Diophantine
          Equations GTM 239, Springer 2007

        AUTHORS:

        - Michael Mardaus (2008-07)

        - Tobias Nagel (2008-07)

        - John Cremona (2008-07)
        """
        #####################################################################
        # INPUT CHECK #######################################################
        if not self.is_integral():
            raise ValueError, "integral_points() can only be called on an integral model"

        if mw_base=='auto':
            mw_base = self.gens()
            r = len(mw_base)
        else:
            try:
                r = len(mw_base)
            except TypeError:
                raise TypeError, 'mw_base must be a list'
            if not all([P.curve() is self for P in mw_base]):
                raise ValueError, "points are not on the correct curve"

        tors_points = self.torsion_points()

        # END INPUT-CHECK####################################################
        #####################################################################

        #####################################################################
        # INTERNAL FUNCTIONS ################################################

        ############################## begin ################################
        def point_preprocessing(free,tor):
            # Transforms an mw_base "free" into a Z-basis for E(Q)\cap
            # E^0(R). If there is a torsion point on the "egg" we add
            # it to any of the gens on the egg; otherwise we replace
            # the free generators with generators of a subgroup of
            # index 2.
            r = len(free)
            newfree = [Q for Q in free] # copy
            tor_egg = [T for T in tor if not T.is_on_identity_component()]
            free_id = [P.is_on_identity_component() for P in free]
            if any(tor_egg):
                T = tor_egg[0]
                for i in range(r):
                    if not free_id[i]:
                        newfree[i] += T
            else:
                if not all(free_id):
                    i0 = free_id.index(False)
                    P = free[i0]
                    for i in range(r):
                        if not free_id[i]:
                            if i==i0:
                                newfree[i] = 2*newfree[i]
                            else:
                                newfree[i] += P
            return newfree
        ##############################  end  ################################
        ############################## begin ################################
        def modified_height(i):#computes modified height if base point i
            return max(mw_base[i].height(),h_E,c7*mw_base_log[i]**2)
        ##############################  end  ################################
        ############################## begin ################################
        def integral_x_coords_in_interval(xmin,xmax):
            """
            Returns the set of integers x with xmin=x=xmax which are
            x-coordinates of points on this curve.
            """
            return set([x for x  in range(xmin,xmax) if self.is_x_coord(x)])
        ##############################  end  ################################

        # END Internal functions #############################################
        ######################################################################

        if (r == 0):
            int_points = [P for P in tors_points if not P.is_zero()]
            int_points = [P for P in int_points if P[0].is_integral()]
            if not both_signs:
                xlist = set([P[0] for P in int_points])
                int_points = [self.lift_x(x) for x in xlist]
            int_points.sort()
            if verbose:
                print 'Total number of integral points:',len(int_points)
            return int_points

        if verbose:
            import sys  # so we can flush stdout for debugging

        g2 = self.c4()/12
        g3 = self.c6()/216
        disc = self.discriminant()
        j = self.j_invariant()
        b2 = self.b2()

        Qx = rings.PolynomialRing(RationalField(),'x')
        pol = Qx([-self.c6()/216,-self.c4()/12,0,4])
        if disc > 0: # two real component -> 3 roots in RR
            #on curve 897e4, only one root is found with default precision!
            RR = R
            prec = RR.precision()
            ei = pol.roots(RR,multiplicities=False)
            while len(ei)<3:
                prec*=2
                RR=RealField(prec)
                ei = pol.roots(RR,multiplicities=False)
            e1,e2,e3 = ei
            if r >= 1: #preprocessing of mw_base only necessary if rank > 0
                mw_base = point_preprocessing(mw_base, tors_points)
                  #at most one point in E^{egg}

        elif disc < 0: # one real component => 1 root in RR (=: e3),
                       # 2 roots in C (e1,e2)
            roots = pol.roots(C,multiplicities=False)
            e3 = pol.roots(R,multiplicities=False)[0]
            roots.remove(e3)
            e1,e2 = roots

        e = R(1).exp()
        pi = R(constants.pi)

        M = self.height_pairing_matrix(mw_base)
        mw_base, U = self.lll_reduce(mw_base,M)
        M = U.transpose()*M*U

        if verbose:
            print "Using mw_basis ",mw_base
            print "e1,e2,e3: ",e1,e2,e3
            sys.stdout.flush()

        # Algorithm presented in [Co1]
        h_E = self.height()
        w1, w2 = self.period_lattice().basis()
        mu = R(disc).abs().log() / 6
        if j!=0:
            mu += max(R(1),R(j).abs().log()) / 6
        if b2!=0:
            mu += max(R(1),R(b2).abs().log())
            mu += log(R(2))
        else:
            mu += 1

        c1 = (mu + 2.14).exp()
        c2 = min(M.charpoly ().roots(multiplicities=False))
        if verbose:
            print "Minimal eigenvalue of height pairing matrix: ", c2
            sys.stdout.flush()

        c3 = (w1**2)*R(b2).abs()/48 + 8
        c5 = (c1*c3).sqrt()
        c7 = abs((3*pi)/((w1**2) * (w1/w2).imag()))

        mw_base_log = [] #contains \Phi(Q_i)
        mod_h_list = []  #contains h_m(Q_i)
        c9_help_list = []
        for i in range(0,r):
            mw_base_log.append(mw_base[i].elliptic_logarithm().abs())
            mod_h_list.append(modified_height(i))
            c9_help_list.append((mod_h_list[i]).sqrt()/mw_base_log[i])
        c8 = max(e*h_E,max(mod_h_list))
        c9 = e/c7.sqrt() * min(c9_help_list)
        n=r+1
        c10 = R(2 * 10**(8+7*n) * R((2/e)**(2 * n**2)) * (n+1)**(4 * n**2 + 10 * n) * log(c9)**(-2*n - 1) * misc.prod(mod_h_list))

        top = Z(128) #arbitrary first upper bound
        bottom = Z(0)
        log_c9=log(c9); log_c5=log(c5)
        log_r_top = log(R(r*(10**top)))
#        if verbose:
#            print "[bottom,top] = ",[bottom,top]

        while R(c10*(log_r_top+log_c9)*(log(log_r_top)+h_E+log_c9)**(n+1)) > R(c2/2 * (10**top)**2 - log_c5):
            #initial bound 'top' too small, upshift of search interval
            bottom = top
            top = 2*top
        while top >= bottom: #binary-search like search for fitting exponent (bound)
#            if verbose:
#                print "[bottom,top] = ",[bottom,top]
            bound = (bottom + (top - bottom)/2).floor()
            log_r_bound = log(R(r*(10**bound)))
            if R(c10*(log_r_bound+log_c9)*(log(log_r_bound)+h_E+log_c9)**(n+1)) > R(c2/2 * (10**bound)**2 - log_c5):
                bottom = bound + 1
            else:
                top = bound - 1

        H_q = R(10)**bound
        break_cond = 0 #at least one reduction step
        #reduction via LLL
        while break_cond < 0.9: #as long as the improvement of the new bound in comparison to the old is greater than 10%
            c = R((H_q**n)*10)  #c has to be greater than H_q^n
            M = matrix.MatrixSpace(Z,n)
            m = M.identity_matrix()
            for i in range(r):
                m[i, r] = R(c*mw_base_log[i]).round()
            m[r,r] = max(Z(1),R(c*w1).round()) #ensures that m isn't singular

            #LLL - implemented in sage - operates on rows not on columns
            m_LLL = m.LLL()
            m_gram = m_LLL.gram_schmidt()[0]
            b1_norm = R(m_LLL.row(0).norm())

            #compute constant c1 ~ c1_LLL of Corollary 2.3.17 and hence d(L,0)^2 ~ d_L_0
            c1_LLL = -1
            for i in range(n):
                tmp = R(b1_norm/(m_gram.row(i).norm()))
                if tmp > c1_LLL:
                    c1_LLL = tmp

            if c1_LLL < 0:
                raise RuntimeError, 'Unexpected intermediate result. Please try another Mordell-Weil base'

            d_L_0 = R(b1_norm**2 / c1_LLL)

            #Reducing of upper bound
            Q = r * H_q**2
            T = (1 + (3/2*r*H_q))/2
            if d_L_0 < R(T**2+Q):
                d_L_0 = 10*(T**2*Q)
            low_bound = R(((d_L_0 - Q).sqrt() - T)/c)

            #new bound according to low_bound and upper bound
            #[c_5 exp((-c_2*H_q^2)/2)] provided by Corollary 8.7.3
            if low_bound != 0:
                H_q_new = R((log(low_bound/c5)/(-c2/2))).sqrt()
                H_q_new = H_q_new.ceil()
                if H_q_new == 1:
                    break_cond = 1 # stops reduction
                else:
                    break_cond = R(H_q_new/H_q)
                H_q = H_q_new
            else:
                break_cond = 1 # stops reduction, so using last H_q > 0
            #END LLL-Reduction loop

        b2_12 = b2/12
        if disc > 0:
            ##Points in egg have X(P) between e1 and e2 [X(P)=x(P)+b2/12]:
            x_int_points = integral_x_coords_in_interval((e1-b2_12).ceil(), (e2-b2_12).floor()+1)
            if verbose:
                print 'x-coords of points on compact component with ',(e1-b2_12).ceil(),'<=x<=',(e2-b2_12).floor()
                L = list(x_int_points) # to have the order
                L.sort()               # deterministic for doctests!
                print L
                sys.stdout.flush()
        else:
            x_int_points = set()

        ##Points in noncompact component with X(P)< 2*max(|e1|,|e2|,|e3|) , espec. X(P)>=e3
        x0 = (e3-b2_12).ceil()
        x1 = (2*max(abs(e1),abs(e2),abs(e3)) - b2_12).ceil()
        x_int_points2 = integral_x_coords_in_interval(x0, x1)
        x_int_points = x_int_points.union(x_int_points2)
        if verbose:
            print 'x-coords of points on non-compact component with ',x0,'<=x<=',x1-1
            L = list(x_int_points2)
            L.sort()
            print L
            sys.stdout.flush()

        if verbose:
            print 'starting search of remaining points using coefficient bound ',H_q
            sys.stdout.flush()
        x_int_points3 = integral_points_with_bounded_mw_coeffs(self,mw_base,H_q)
        x_int_points = x_int_points.union(x_int_points3)
        if verbose:
            print 'x-coords of extra integral points:'
            L = list(x_int_points3)
            L.sort()
            print L
            sys.stdout.flush()

        if len(tors_points)>1:
            x_int_points_t = set()
            for x in x_int_points:
                P = self.lift_x(x)
                for T in tors_points:
                    Q = P+T
                    if not Q.is_zero() and Q[0].is_integral():
                        x_int_points_t = x_int_points_t.union([Q[0]])
            x_int_points = x_int_points.union(x_int_points_t)

        # Now we have all the x-coordinates of integral points, and we
        # construct the points, depending on the parameter both_signs:
        if both_signs:
            int_points = sum([self.lift_x(x,all=True) for x in x_int_points],[])
        else:
            int_points = [self.lift_x(x) for x in x_int_points]
        int_points.sort()
        if verbose:
            print 'Total number of integral points:',len(int_points)
        return int_points

    def S_integral_points(self, S, mw_base='auto', both_signs=False, verbose=False, proof=None):
        """
        Computes all S-integral points (up to sign) on this elliptic curve.

        INPUT:

        - ``S`` -  list of primes

        - ``mw_base`` - list of EllipticCurvePoint generating the
          Mordell-Weil group of E (default: 'auto' - calls
          :meth:`.gens`)

        - ``both_signs`` - True/False (default False): if True the
          output contains both P and -P, otherwise only one of each
          pair.

        - ``verbose`` - True/False (default False): if True, some
          details of the computation are output.

        - ``proof`` - True/False (default True): if True ALL
          S-integral points will be returned.  If False, the MW basis
          will be computed with the proof=False flag, and also the
          time-consuming final call to
          S_integral_x_coords_with_abs_bounded_by(abs_bound) is
          omitted.  Use this only if the computation takes too long,
          but be warned that then it cannot be guaranteed that all
          S-integral points will be found.

        OUTPUT:

        A sorted list of all the S-integral points on E (up to sign
        unless both_signs is True)

        .. note::

           The complexity increases exponentially in the rank of curve
           E and in the length of S.  The computation time (but not
           the output!) depends on the Mordell-Weil basis.  If mw_base
           is given but is not a basis for the Mordell-Weil group
           (modulo torsion), S-integral points which are not in the
           subgroup generated by the given points will almost
           certainly not be listed.

        EXAMPLES:

        A curve of rank 3 with no torsion points::

            sage: E=EllipticCurve([0,0,1,-7,6])
            sage: P1=E.point((2,0)); P2=E.point((-1,3)); P3=E.point((4,6))
            sage: a=E.S_integral_points(S=[2,3], mw_base=[P1,P2,P3], verbose=True);a
            max_S: 3 len_S: 3 len_tors: 1
            lambda 0.485997517468...
            k1,k2,k3,k4 6.68597129142710e234 1.31952866480763 3.31908110593519e9 2.42767548272846e17
            p= 2 : trying with p_prec =  30
            mw_base_p_log_val =  [2, 2, 1]
            min_psi =  2 + 2^3 + 2^6 + 2^7 + 2^8 + 2^9 + 2^11 + 2^12 + 2^13 + 2^16 + 2^17 + 2^19 + 2^20 + 2^21 + 2^23 + 2^24 + 2^28 + O(2^30)
            p= 3 : trying with p_prec =  30
            mw_base_p_log_val =  [1, 2, 1]
            min_psi =  3 + 3^2 + 2*3^3 + 3^6 + 2*3^7 + 2*3^8 + 3^9 + 2*3^11 + 2*3^12 + 2*3^13 + 3^15 + 2*3^16 + 3^18 + 2*3^19 + 2*3^22 + 2*3^23 + 2*3^24 + 2*3^27 + 3^28 + 3^29 + O(3^30)
            mw_base [(1 : -1 : 1), (2 : 0 : 1), (0 : -3 : 1)]
            mw_base_log [0.667789378224099, 0.552642660712417, 0.818477222895703]
            mp [5, 7]
            mw_base_p_log [[2^2 + 2^3 + 2^6 + 2^7 + 2^8 + 2^9 + 2^14 + 2^15 + 2^18 + 2^19 + 2^24 + 2^29 + O(2^30), 2^2 + 2^3 + 2^5 + 2^6 + 2^9 + 2^11 + 2^12 + 2^14 + 2^15 + 2^16 + 2^18 + 2^20 + 2^22 + 2^23 + 2^26 + 2^27 + 2^29 + O(2^30), 2 + 2^3 + 2^6 + 2^7 + 2^8 + 2^9 + 2^11 + 2^12 + 2^13 + 2^16 + 2^17 + 2^19 + 2^20 + 2^21 + 2^23 + 2^24 + 2^28 + O(2^30)], [2*3^2 + 2*3^5 + 2*3^6 + 2*3^7 + 3^8 + 3^9 + 2*3^10 + 3^12 + 2*3^14 + 3^15 + 3^17 + 2*3^19 + 2*3^23 + 3^25 + 3^28 + O(3^30), 2*3 + 2*3^2 + 2*3^3 + 2*3^4 + 2*3^6 + 2*3^7 + 2*3^8 + 3^10 + 2*3^12 + 3^13 + 2*3^14 + 3^15 + 3^18 + 3^22 + 3^25 + 2*3^26 + 3^27 + 3^28 + O(3^30), 3 + 3^2 + 2*3^3 + 3^6 + 2*3^7 + 2*3^8 + 3^9 + 2*3^11 + 2*3^12 + 2*3^13 + 3^15 + 2*3^16 + 3^18 + 2*3^19 + 2*3^22 + 2*3^23 + 2*3^24 + 2*3^27 + 3^28 + 3^29 + O(3^30)]]
            k5,k6,k7 0.321154513240... 1.55246328915... 0.161999172489...
            initial bound 2.6227097483365...e117
            bound_list [58, 58, 58]
            bound_list [8, 9, 9]
            bound_list [8, 7, 7]
            bound_list [8, 7, 7]
            starting search of points using coefficient bound  8
            x-coords of S-integral points via linear combination of mw_base and torsion:
            [-3, -26/9, -8159/2916, -2759/1024, -151/64, -1343/576, -2, -7/4, -1, -47/256, 0, 1/4, 4/9, 9/16, 58/81, 7/9, 6169/6561, 1, 17/16, 2, 33/16, 172/81, 9/4, 25/9, 3, 31/9, 4, 25/4, 1793/256, 8, 625/64, 11, 14, 21, 37, 52, 6142/81, 93, 4537/36, 342, 406, 816, 207331217/4096]
            starting search of extra S-integer points with absolute value bounded by 3.89321964979420
            x-coords of points with bounded absolute value
            [-3, -2, -1, 0, 1, 2]
            Total number of S-integral points: 43
            [(-3 : 0 : 1), (-26/9 : 28/27 : 1), (-8159/2916 : 233461/157464 : 1), (-2759/1024 : 60819/32768 : 1), (-151/64 : 1333/512 : 1), (-1343/576 : 36575/13824 : 1), (-2 : 3 : 1), (-7/4 : 25/8 : 1), (-1 : 3 : 1), (-47/256 : 9191/4096 : 1), (0 : 2 : 1), (1/4 : 13/8 : 1), (4/9 : 35/27 : 1), (9/16 : 69/64 : 1), (58/81 : 559/729 : 1), (7/9 : 17/27 : 1), (6169/6561 : 109871/531441 : 1), (1 : 0 : 1), (17/16 : -25/64 : 1), (2 : 0 : 1), (33/16 : 17/64 : 1), (172/81 : 350/729 : 1), (9/4 : 7/8 : 1), (25/9 : 64/27 : 1), (3 : 3 : 1), (31/9 : 116/27 : 1), (4 : 6 : 1), (25/4 : 111/8 : 1), (1793/256 : 68991/4096 : 1), (8 : 21 : 1), (625/64 : 14839/512 : 1), (11 : 35 : 1), (14 : 51 : 1), (21 : 95 : 1), (37 : 224 : 1), (52 : 374 : 1), (6142/81 : 480700/729 : 1), (93 : 896 : 1), (4537/36 : 305425/216 : 1), (342 : 6324 : 1), (406 : 8180 : 1), (816 : 23309 : 1), (207331217/4096 : 2985362173625/262144 : 1)]

       It is not necessary to specify mw_base; if it is not provided,
       then the Mordell-Weil basis must be computed, which may take
       much longer.

       ::

            sage: a = E.S_integral_points([2,3])
            sage: len(a)
            43

        An example with negative discriminant::

            sage: EllipticCurve('900d1').S_integral_points([17], both_signs=True)
            [(-11 : -27 : 1), (-11 : 27 : 1), (-4 : -34 : 1), (-4 : 34 : 1), (4 : -18 : 1), (4 : 18 : 1), (2636/289 : -98786/4913 : 1), (2636/289 : 98786/4913 : 1), (16 : -54 : 1), (16 : 54 : 1)]

        Output checked with Magma (corrected in 3 cases)::

            sage: [len(e.S_integral_points([2], both_signs=False)) for e in cremona_curves([11..100])] # long time
            [2, 0, 2, 3, 3, 1, 3, 1, 3, 5, 3, 5, 4, 1, 1, 2, 2, 2, 3, 1, 2, 1, 0, 1, 3, 3, 1, 1, 5, 3, 4, 2, 1, 1, 5, 3, 2, 2, 1, 1, 1, 0, 1, 3, 0, 1, 0, 1, 1, 3, 7, 1, 3, 3, 3, 1, 1, 2, 3, 1, 2, 3, 1, 2, 1, 3, 3, 1, 1, 1, 0, 1, 3, 3, 1, 1, 7, 1, 0, 1, 1, 0, 1, 2, 0, 3, 1, 2, 1, 3, 1, 2, 2, 4, 5, 3, 2, 1, 1, 6, 1, 0, 1, 3, 1, 3, 3, 1, 1, 1, 1, 1, 3, 1, 5, 1, 2, 4, 1, 1, 1, 1, 1, 0, 1, 0, 2, 2, 0, 0, 1, 0, 1, 1, 6, 1, 0, 1, 1, 0, 4, 3, 1, 2, 1, 2, 3, 1, 1, 1, 1, 8, 3, 1, 2, 1, 2, 0, 8, 2, 0, 6, 2, 3, 1, 1, 1, 3, 1, 3, 2, 1, 3, 1, 2, 1, 6, 9, 3, 3, 1, 1, 2, 3, 1, 1, 5, 5, 1, 1, 0, 1, 1, 2, 3, 1, 1, 2, 3, 1, 3, 1, 1, 1, 1, 0, 0, 1, 3, 3, 1, 3, 1, 1, 2, 2, 0, 0, 6, 1, 0, 1, 1, 1, 1, 3, 1, 2, 6, 3, 1, 2, 2, 1, 1, 1, 1, 7, 5, 4, 3, 3, 1, 1, 1, 1, 1, 1, 8, 5, 1, 1, 3, 3, 1, 1, 3, 3, 1, 1, 2, 3, 6, 1, 1, 7, 3, 3, 4, 5, 9, 6, 1, 0, 7, 1, 1, 3, 1, 1, 2, 3, 1, 2, 1, 1, 1, 1, 1, 1, 1, 7, 8, 2, 3, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1]


        An example from [PZGH]::

            sage: E = EllipticCurve([0,0,0,-172,505])
            sage: E.rank(), len(E.S_integral_points([3,5,7]))  # long time (~7s)
            (4, 72)

        This is curve "7690e1" which failed until \#4805 was fixed::

            sage: EllipticCurve([1,1,1,-301,-1821]).S_integral_points([13,2])
            [(-13 : 16 : 1),
            (-9 : 20 : 1),
            (-7 : 4 : 1),
            (21 : 30 : 1),
            (23 : 52 : 1),
            (63 : 452 : 1),
            (71 : 548 : 1),
            (87 : 756 : 1),
            (2711 : 139828 : 1),
            (7323 : 623052 : 1),
            (17687 : 2343476 : 1)]

        REFERENCES:

        - [PZGH] Petho A., Zimmer H.G., Gebel J. and Herrmann E.,
          Computing all S-integral points on elliptic curves
          Math. Proc. Camb. Phil. Soc. (1999), 127, 383-402

        - Some parts of this implementation are partially based on the
          function integral_points()

        AUTHORS:

        - Tobias Nagel (2008-12)

        - Michael Mardaus (2008-12)

        - John Cremona (2008-12)
        """
        # INPUT CHECK #######################################################

        if proof is None:
            from sage.structure.proof.proof import get_flag
            proof = get_flag(proof, "elliptic_curve")
        else:
            proof = bool(proof)


        if not self.is_integral():
            raise ValueError, "S_integral_points() can only be called on an integral model"
        if not all([self.is_p_minimal(s) for s in S]):
            raise ValueError, "%s must be p-minimal for all primes in S"%self

        try:
            len_S = len(S)
            if len_S == 0:
                return self.integral_points(mw_base, both_signs, verbose)
            if not all([s.is_prime() for s in S]):
                raise ValueError, "All elements of S must be prime"
            S.sort()
        except TypeError:
            raise TypeError, 'S must be a list of primes'
        except AttributeError:#catches: <tuple>.sort(), <!ZZ>.is_prime()
            raise AttributeError,'S must be a list of primes'

        if mw_base=='auto':
            if verbose:
                print "Starting computation of MW basis"
            mw_base = self.gens(proof=proof)
            r = len(mw_base)
            if verbose:
                print "Finished computation of MW basis; rank is ",r
        else:
            try:
                r = len(mw_base)
            except TypeError:
                raise TypeError, 'mw_base must be a list'
            if not all([P.curve() is self for P in mw_base]):
                raise ValueError, "mw_base-points are not on the correct curve"

        #End Input-Check ######################################################

        #Internal functions ###################################################
        def is_S_int(x):
            """
            Tests if the rational number x is S-integral.
            """
            fac_list_S=[]
            xde = x.denominator()
            fac_list_S = [p**(xde.valuation(p)) for p in S]
            res_S = misc.prod(fac_list_S)
            if res_S == xde:
                return True
            else:
                return False
            #other possibility using division
            #tmp = xde
            #for p in S:
                #tmp = tmp / p**(tmp.valuation(p))
            #if tmp = xde:
                #return True
            #else:
                #return False
    #<-------------------------------------------------------------------------
    #>-------------------------------------------------------------------------
        def reduction_at(p):
            r"""
            Reducing the bound `H_q` at the finite place p in S via LLL
            """
            indexp = S.index(p)
            pc = Z(p**(R(c.log()/log(p,e)).ceil()))
            m = M.identity_matrix()
            for i in range(r):
                try:
                    m[i, r] = Z((beta[indexp][i])%pc)
                except ZeroDivisionError:  #If Inverse doesn't exist, change denominator (which is only approx)
                    val_nu = (beta[indexp][i]).numerator()
                    val_de = (beta[indexp][i]).denominator()
                    m[i, r] = Z((val_nu/(val_de+1))%pc)
            m[r,r] = max(Z(1), pc)

            #LLL - implemented in sage - operates on rows not on columns
            m_LLL = m.LLL()
            m_gram = m_LLL.gram_schmidt()[0]
            b1_norm = R(m_LLL.row(0).norm())

            c1_LLL = -1
            for i in range(n):
                tmp = R(b1_norm/(m_gram.row(i).norm()))
                if tmp > c1_LLL:
                    c1_LLL = tmp
            if c1_LLL < 0:
                raise RuntimeError, 'Unexpected intermediate result. Please try another Mordell-Weil base'
            d_L_0 = R(b1_norm**2 / c1_LLL)

            #Reducing of upper bound
            Q = r * H_q**2
            T = (1 + (3/2*r*H_q))/2
            if d_L_0 < R(T**2+Q):
                d_L_0 = 10*(T**2*Q)
            low_bound = R(((d_L_0 - Q).sqrt() - T)/c)

            ##new bound according to low_bound and upper bound
            ##[k5*k6 exp(-k7**H_q^2)]
            if low_bound != 0:
                H_q_infinity = R(((low_bound/(k6)).log()/(-k7)).sqrt())
                return (H_q_infinity.ceil())
            else:
                return (H_q)
    #<-------------------------------------------------------------------------
    #>-------------------------------------------------------------------------
        def S_integral_points_with_bounded_mw_coeffs():
            r"""
            Returns the set of S-integers x which are x-coordinates of
            points on the curve which are linear combinations of the
            generators (basis and torsion points) with coefficients
            bounded by `H_q`.  The bound `H_q` will be computed at
            runtime.
            (Modified version of integral_points_with_bounded_mw_coeffs() in
             integral_points() )

            TODO: Make this more efficient.  In the case ``S=[]`` we
            worked over the reals and only computed a combination
            exactly if the real coordinates were approximately
            integral.  We need a version of this which works for
            S-integral points, probably by finding a bound on the
            denominator.
            """
            from sage.groups.generic import multiples
            xs=set()
            N=H_q

            def test(P):
                """
                Record x-coord of a point if S-integral.
                """
                if not P.is_zero():
                    xP = P[0]
                    if is_S_int(xP):
                        xs.add(xP)

            def test_with_T(R):
                """
                Record x-coords of a 'point+torsion' if S-integral.
                """
                for T in tors_points:
                    test(R+T)

         # For small rank and small H_q perform simple search
            if r==1 and N<=10:
                for P in multiples(mw_base[0],N+1):
                    test_with_T(P)
                return xs

         # explicit computation and testing linear combinations
         # ni loops through all tuples (n_1,...,n_r) with |n_i| <= N
         # stops when (0,0,...,0) is reached because after that, only inverse points of
         # previously tested points would be tested

            E0=E(0)
            ni = [-N for i in range(r)]
            mw_baseN = [-N*P for P in mw_base]
            Pi = [0 for j in range(r)]
            Pi[0] = mw_baseN[0]
            for i in range(1,r):
                Pi[i] = Pi[i-1] + mw_baseN[i]

            while True:
                if all([n==0 for n in ni]):
                    test_with_T(E0)
                    break

                # test the ni-combination which is Pi[r-1]
                test_with_T(Pi[r-1])

                # increment indices and stored points
                i0 = r-1
                while ni[i0]==N:
                    ni[i0] = -N
                    i0 -= 1
                ni[i0] += 1
                if all([n==0 for n in ni[0:i0+1]]):
                    Pi[i0] = E0
                else:
                    Pi[i0] += mw_base[i0]
                for i in range(i0+1,r):
                    Pi[i] = Pi[i-1] + mw_baseN[i]

            return xs
    #<-------------------------------------------------------------------------
    #>-------------------------------------------------------------------------
        def S_integral_x_coords_with_abs_bounded_by(abs_bound):
            r"""
            Extra search of points with `|x|< ` abs_bound, assuming
            that `x` is `S`-integral and `|x|\ge|x|_q` for all primes
            `q` in `S`. (Such points are not covered by the main part
            of the code).  We know

            .. math::

               x=\frac{\xi}{\p_1^{\alpha_1} \cdot \dots \cdot \p_s^{\alpha_s}},\ (gcd(\xi,\p_i)=1),\ p_i \in S

            so a bound of `\alpha_i` can be found in terms of
            abs_bound. Additionally each `\alpha` must be even, giving
            another restriction.  This gives a finite list of
            denominators to test, and for each, a range of numerators.
            All candidates for `x` resulting from this theory are then
            tested, and a list of the ones which are `x`-coordinates
            of (`S`-integral) points is returned.

            TODO: Make this more efficient.  If we had an efficient
            function for searching for integral points (for example,
            by wrapping Stoll's ratpoint program) then it should be
            better to scale the equation by the maximum denominator
            and search for integral points on the scaled model.

            """
            x_min = min(self.two_division_polynomial().roots(R,multiplicities=False))
            x_min_neg = bool(x_min<0)
            x_min_pos = not x_min_neg
            log_ab = R(abs_bound.log())
            alpha = [(log_ab/R(log(p,e))).floor() for p in S]
            if all([alpha_i <= 1 for alpha_i in alpha]): # so alpha_i must be 0 to satisfy that denominator is a square
                return set([x for x  in range(-abs_bound,abs_bound) if E.is_x_coord(x)])
            else:
                xs = []
                alpha_max_even = [y-y%2 for y in alpha]
                p_pow_alpha = []
                list_alpha = []
                for i in range(len_S-1):
                    list_alpha.append(range(0,alpha_max_even[i]+2,2))
                    p_pow_alpha.append([S[i]**list_alpha[i][j] for j in range(len(list_alpha[i]))])
                if verbose:
                    print list_alpha, p_pow_alpha
                # denom_maxpa is a list of pairs (d,q) where d runs
                # through possible denominators, and q=p^a is the
                # maximum prime power divisor of d:
                denom_maxpa = [(misc.prod(tmp),max(tmp)) for tmp in cartesian_product_iterator(p_pow_alpha)]
#               The maximum denominator is this (not used):
#                denom = [misc.prod([pp[-1] for pp in p_pow_alpha],1)]
                for de,maxpa in denom_maxpa:
                    n_max = (abs_bound*de).ceil()
                    n_min = maxpa*de
                    if x_min_pos:
                        pos_n_only = True
                        if x_min > maxpa:
                            n_min = (x_min*de).floor()
                    else:
                        pos_n_only = False
                        neg_n_max = (x_min.abs()*de).ceil()

#                   if verbose:
#                       print "testing denominator ",de
#                       print "numerator bounds = ",(n_min,n_max)

                    for n in misc.xsrange(n_min,n_max+1):
                        tmp = n/de  # to save time, do not check de is the exact denominator
                        if E.is_x_coord(tmp):
                            xs+=[tmp]
                        if not pos_n_only:
                            if n <= neg_n_max:
                                if E.is_x_coord(-tmp):
                                    xs+=[-tmp]

                return set(xs)
    #<-------------------------------------------------------------------------
        #End internal functions ###############################################
        from sage.misc.all import cartesian_product_iterator

        E = self
        tors_points = E.torsion_points()

        if (r==0):#only Torsionpoints to consider
            int_points = [P for P in tors_points if not P.is_zero()]
            int_points = [P for P in int_points if is_S_int(P[0])]
            if not both_signs:
                xlist = set([P[0] for P in int_points])
                int_points = [E.lift_x(x) for x in xlist]
            int_points.sort()
            if verbose:
                print 'Total number of S-integral points:',len(int_points)
            return int_points

        if verbose:
            import sys  # so we can flush stdout for debugging

        e = R(1).exp()
        a1, a2, a3, a4, a6 = E.a_invariants()
        b2, b4, b6, b8 = E.b_invariants()
        c4, c6 = E.c_invariants()
        disc = E.discriminant()
        #internal function is doing only a comparision of E and E.short_weierstass_model() so the following is easier
        if a1 == a2 == a3 == 0:
            is_short = True
        else:
            is_short = False

        w1, w2 = E.period_lattice().basis()

        Qx = rings.PolynomialRing(RationalField(),'x')
        pol = Qx([-54*c6,-27*c4,0,1])
        if disc > 0: # two real component -> 3 roots in RR
            # it is possible that only one root is found with default precision! (see integral_points())
            RR = R
            prec = RR.precision()
            ei = pol.roots(RR,multiplicities=False)
            while len(ei)<3:
                prec*=2
                RR=RealField(prec)
                ei = pol.roots(RR,multiplicities=False)
            e1,e2,e3 = ei
        elif disc < 0: # one real component => 1 root in RR (=: e3),
                       # 2 roots in C (e1,e2)
            roots = pol.roots(C,multiplicities=False)
            e3 = pol.roots(R,multiplicities=False)[0]
            roots.remove(e3)
            e1,e2 = roots

        len_tors = len(tors_points)
        n = r + 1

        M = E.height_pairing_matrix(mw_base)
        mw_base, U = E.lll_reduce(mw_base,M)
        M = U.transpose()*M*U

        # NB "lambda" is a reserved word in Python!
        lamda = min(M.charpoly().roots(multiplicities = False))
        max_S = max(S)
        len_S += 1 #Counting infinity (always "included" in S)
        if verbose:
            print 'max_S:',max_S,'len_S:',len_S,'len_tors:',len_tors
            print 'lambda',lamda
            sys.stdout.flush()

        if is_short:
            disc_0_abs = R((4*a4**3 + 27*a6**2).abs())
            k4 = R(10**4 * max(16*a4**2, 256*disc_0_abs.sqrt()**3))
            k3 = R(32/3 * disc_0_abs.sqrt() * (8 + 0.5*disc_0_abs.log())**4)
        else:
            disc_sh = R(E.short_weierstrass_model().discriminant()) #computes y^2=x^3 -27c4x -54c6
            k4 = R(20**4 * max(3**6 * c4**2, 16*(disc_sh.abs().sqrt())**3))
            k3 = R(32/3 * disc_sh.abs().sqrt() * (8 + 0.5*disc_sh.abs().log())**4)


        k2 = max(R(b2.abs()), R(b4.abs().sqrt()), R(b6.abs()**(1/3)), R(b8.abs()**(1/4))).log()
        k1 = R(7 * 10**(38*len_S+49)) * R(len_S**(20*len_S+15)) * max_S**24 * R(max(1,log(max_S, e))**(4*len_S - 2)) * k3 * k3.log()**2 * ((20*len_S - 19)*k3 + (e*k4).log()) + 2*R(2*b2.abs()+6).log()

        if verbose:
            print 'k1,k2,k3,k4',k1,k2,k3,k4
            sys.stdout.flush()
        #H_q -> [PZGH]:N_0 (due to consistency to integral_points())
        H_q = R(((k1/2+k2)/lamda).sqrt())

        #computation of logs
        mw_base_log = [(pts.elliptic_logarithm().abs())*(len_tors/w1) for pts in mw_base]
        mw_base_p_log = []
        beta = []
        mp=[]
        tmp = 0
        for p in S:
            Np = E.Np(p)
            cp = E.tamagawa_exponent(p)
            mp_temp = Z(len_tors).lcm(cp*Np)
            mp.append(mp_temp) #only necessary because of verbose below
            p_prec=30+E.discriminant().valuation(p)
            p_prec_ok=False
            while not p_prec_ok:
                if verbose:
                    print "p=",p,": trying with p_prec = ",p_prec
                try:
                    mw_base_p_log.append([mp_temp*(pts.padic_elliptic_logarithm(p,absprec=p_prec)) for pts in mw_base])
                    p_prec_ok=True
                except ValueError:
                    p_prec *= 2
            #reorder mw_base_p: last value has minimal valuation at p
            mw_base_p_log_val = [mw_base_p_log[tmp][i].valuation() for i in range(r)]
            if verbose:
                print "mw_base_p_log_val = ",mw_base_p_log_val
            min_index = mw_base_p_log_val.index(min(mw_base_p_log_val))
            min_psi = mw_base_p_log[tmp][min_index]
            if verbose:
                print "min_psi = ",min_psi
            mw_base_p_log[tmp].remove(min_psi)
            mw_base_p_log[tmp].append(min_psi)
            #beta needed for reduction at p later on
            try:
                beta.append([-mw_base_p_log[tmp][j]/min_psi for j in range(r)])
            except ValueError:
                # e.g. mw_base_p_log[tmp]==[0]:  can occur e.g. [?]'172c6, S=[2]
                beta.append([0] for j in range(r))
            tmp +=1

        if verbose:
            print 'mw_base',mw_base
            print 'mw_base_log', mw_base_log
            print 'mp', mp
            print 'mw_base_p_log',mw_base_p_log
            #print 'beta', beta
            sys.stdout.flush()

        #constants in reduction (not needed to be computed every reduction step)
        k5 = R((2*len_tors)/(3*w1))
        k6 = R((k2/len_S).exp())
        k7 = R(lamda/len_S)

        if verbose:
            print 'k5,k6,k7',k5,k6,k7
            sys.stdout.flush()

        break_cond = 0
        M = matrix.MatrixSpace(Z,n)
   #Reduction of initial bound
        if verbose:
            print 'initial bound',H_q
            sys.stdout.flush()

        while break_cond < 0.9:
         #reduction at infinity
            bound_list=[]
            c = R((H_q**n)*100)
            m = M.identity_matrix()
            for i in range(r):
                m[i, r] = R(c*mw_base_log[i]).round()
            m[r,r] = max(Z(1), R(c*w1).round())
            #LLL - implemented in sage - operates on rows not on columns
            m_LLL = m.LLL()
            m_gram = m_LLL.gram_schmidt()[0]
            b1_norm = R(m_LLL.row(0).norm())

            #compute constant c1_LLL (cf. integral_points())
            c1_LLL = -1
            for i in range(n):
                tmp = R(b1_norm/(m_gram.row(i).norm()))
                if tmp > c1_LLL:
                    c1_LLL = tmp
            if c1_LLL < 0:
                raise RuntimeError, 'Unexpected intermediate result. Please try another Mordell-Weil base'
            d_L_0 = R(b1_norm**2 / c1_LLL)

            #Reducing of upper bound
            Q = r * H_q**2
            T = (1 + (3/2*r*H_q))/2
            if d_L_0 < R(T**2+Q):
                d_L_0 = 10*(T**2*Q)
            low_bound = R(((d_L_0 - Q).sqrt() - T)/c)

            ##new bound according to low_bound and upper bound
            ##[k5*k6 exp(-k7**H_q^2)]
            if low_bound != 0:
                H_q_infinity = R(((low_bound/(k5*k6)).log()/(-k7)).abs().sqrt())
                bound_list.append(H_q_infinity.ceil())
            else:
                bound_list.append(H_q)

         ##reduction for finite places in S
            for p in S:
                bound_list.append(reduction_at(p))

            if verbose:
                print 'bound_list',bound_list
                sys.stdout.flush()

            H_q_new = max(bound_list)
            if (H_q_new > H_q): #no improvement
                break_cond = 1 #stop reduction
            elif (H_q_new == 1): #best possible H_q
                H_q = H_q_new
                break_cond = 1 #stop
            else:
                break_cond = R(H_q_new/H_q)
                H_q = H_q_new
    #end of reductions

    #search of S-integral points
        #step1: via linear combination and H_q
        x_S_int_points = set()
        if verbose:
            print 'starting search of points using coefficient bound ',H_q
            sys.stdout.flush()
        x_S_int_points1 = S_integral_points_with_bounded_mw_coeffs()
        x_S_int_points = x_S_int_points.union(x_S_int_points1)
        if verbose:
            print 'x-coords of S-integral points via linear combination of mw_base and torsion:'
            L = list(x_S_int_points1)
            L.sort()
            print L
            sys.stdout.flush()

        #step 2: Extra search
        if e3 < 0:
            M = R( max((27*c4).abs().sqrt(), R((54*c6).abs()**(1/3)) / R(2**(1/3))-1) )
        else:
            M = R(0)
        e0 = max(e1+e2, 2*e3) + M
        abs_bound = R((max(0,e0)+6*b2.abs())/36)

        if proof:
            if verbose:
                print 'starting search of extra S-integer points with absolute value bounded by',abs_bound
                sys.stdout.flush()
            if abs_bound != 0:
                x_S_int_points2 = S_integral_x_coords_with_abs_bounded_by(abs_bound)
                x_S_int_points = x_S_int_points.union(x_S_int_points2)
                if verbose:
                    print 'x-coords of points with bounded absolute value'
                    L = list(x_S_int_points2)
                    L.sort()
                    print L
                    sys.stdout.flush()

        if len(tors_points)>1:
            x_S_int_points_t = set()
            for x in x_S_int_points:
                P = E.lift_x(x)
                for T in tors_points:
                    Q = P+T
                    if not Q.is_zero() and is_S_int(Q[0]):
                        x_S_int_points_t = x_S_int_points_t.union([Q[0]])
            x_S_int_points = x_S_int_points.union(x_S_int_points_t)

        # All x values collected, now considering "both_signs"
        if both_signs:
            S_int_points = sum([self.lift_x(x,all=True) for x in x_S_int_points],[])
        else:
            S_int_points = [self.lift_x(x) for x in x_S_int_points]
        S_int_points.sort()
        if verbose:
            print 'Total number of S-integral points:',len(S_int_points)
        return S_int_points


def cremona_curves(conductors):
    """
    Return iterator over all known curves (in database) with conductor
    in the list of conductors.

    EXAMPLES::

        sage: [(E.label(), E.rank()) for E in cremona_curves(srange(35,40))]
        [('35a1', 0),
        ('35a2', 0),
        ('35a3', 0),
        ('36a1', 0),
        ('36a2', 0),
        ('36a3', 0),
        ('36a4', 0),
        ('37a1', 1),
        ('37b1', 0),
        ('37b2', 0),
        ('37b3', 0),
        ('38a1', 0),
        ('38a2', 0),
        ('38a3', 0),
        ('38b1', 0),
        ('38b2', 0),
        ('39a1', 0),
        ('39a2', 0),
        ('39a3', 0),
        ('39a4', 0)]
    """
    if isinstance(conductors, (int,long, rings.RingElement)):
        conductors = [conductors]
    return sage.databases.cremona.CremonaDatabase().iter(conductors)

def cremona_optimal_curves(conductors):
    """
    Return iterator over all known optimal curves (in database) with
    conductor in the list of conductors.

    EXAMPLES::

        sage: [(E.label(), E.rank()) for E in cremona_optimal_curves(srange(35,40))]
        [('35a1', 0),
        ('36a1', 0),
        ('37a1', 1),
        ('37b1', 0),
        ('38a1', 0),
        ('38b1', 0),
        ('39a1', 0)]

    There is one case -- 990h3 -- when the optimal curve isn't labeled with a 1::

        sage: [e.cremona_label() for e in cremona_optimal_curves([990])]
        ['990a1', '990b1', '990c1', '990d1', '990e1', '990f1', '990g1', '990h3', '990i1', '990j1', '990k1', '990l1']

    """
    if isinstance(conductors, (int,long,rings.RingElement)):
        conductors = [conductors]
    return sage.databases.cremona.CremonaDatabase().iter_optimal(conductors)

def integral_points_with_bounded_mw_coeffs(E, mw_base, N):
    r"""
    Returns the set of integers `x` which are
    `x`-coordinates of points on the curve `E` which
    are linear combinations of the generators (basis and torsion
    points) with coefficients bounded by `N`.
    """
    from sage.groups.generic import multiples
    xs=set()
    tors_points = E.torsion_points()
    r = len(mw_base)

    def use(P):
        """
        Helper function to record x-coord of a point if integral.
        """
        if not P.is_zero():
            xP = P[0]
            if xP.is_integral():
                xs.add(xP)

    def use_t(R):
        """
        Helper function to record x-coords of a point +torsion if
        integral.
        """
        for T in tors_points:
            use(R+T)

    # We use a naive method when the number of possibilities is small:

    if r==1 and N<=10:
        for P in multiples(mw_base[0],N+1):
            use_t(P)
        return xs

    # Otherwise it is very very much faster to first compute
    # the linear combinations over RR, and only compute them as
    # rational points if they are approximately integral.

    # Note: making eps larger here will dramatically increase
    # the running time.  If evidence arises that integral
    # points are being missed, it would be better to increase
    # the real precision than to increase eps.

    def is_approx_integral(P):
        eps = 0.0001
        return (abs(P[0]-P[0].round()))<eps and (abs(P[1]-P[1].round()))<eps

    RR = RealField(100) #(100)
    ER = E.change_ring(RR)
    ER0 = ER(0)

    # Note: doing [ER(P) for P in mw_base] sometimes fails.  The
    # following way is harder, since we have to make sure we don't use
    # -P instead of P, but is safer.

    Rgens = [ER.lift_x(P[0]) for P in mw_base]
    for i in range(r):
        if abs(Rgens[i][1]-mw_base[i][1])>abs((-Rgens[i])[1]-mw_base[i][1]):
            Rgens[i] = -Rgens[i]

    # the ni loop through all tuples (a1,a2,...,ar) with
    # |ai|<=N, but we stop immediately after using the tuple
    # (0,0,...,0).

    # Initialization:
    ni = [-N for i in range(r)]
    RgensN = [-N*P for P in Rgens]
    # RPi[i] = -N*(Rgens[0]+...+Rgens[i])
    RPi = [0 for j in range(r)]
    RPi[0] = RgensN[0]
    for i in range(1,r):
        RPi[i] = RPi[i-1] + RgensN[i]

    while True:
        if all([n==0 for n in ni]):
             use_t(E(0))
             break

        # test the ni-combination which is RPi[r-1]
        RP = RPi[r-1]

        for T in tors_points:
            if is_approx_integral(RP+ER(T)):
                 P = sum([ni[i]*mw_base[i] for i in range(r)],T)
                 use(P)

        # increment indices and stored points
        i0 = r-1
        while ni[i0]==N:
            ni[i0] = -N
            i0 -= 1
        ni[i0] += 1
        # The next lines are to prevent rounding error: (-P)+P behaves
        # badly for real points!
	if all([n==0 for n in ni[0:i0+1]]):
            RPi[i0] = ER0
        else:
            RPi[i0] += Rgens[i0]
	for i in range(i0+1,r):
            RPi[i] = RPi[i-1] + RgensN[i]

    return xs
