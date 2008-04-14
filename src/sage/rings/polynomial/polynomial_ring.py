"""
Univariate Polynomial Rings

SAGE implements sparse and dense polynomials over commutative and
non-commutative rings.  In the non-commutative case, the polynomial
variable commutes with the elements of the base ring.

AUTHOR:
   -- William Stein
   -- Kiran Kedlaya (2006-02-13): added macaulay2 option
   -- Martin Albrecht (2006-08-25): removed it again as it isn't needed anymore

EXAMPLES:
Creating a polynomial ring injects the variable into the interpreter namespace:
    sage: z = QQ['z'].0
    sage: (z^3 + z - 1)^3
    z^9 + 3*z^7 - 3*z^6 + 3*z^5 - 6*z^4 + 4*z^3 - 3*z^2 + 3*z - 1

Saving and loading of polynomial rings works:
    sage: loads(dumps(QQ['x'])) == QQ['x']
    True
    sage: k = PolynomialRing(QQ['x'],'y'); loads(dumps(k))==k
    True
    sage: k = PolynomialRing(ZZ,'y'); loads(dumps(k)) == k
    True
    sage: k = PolynomialRing(ZZ,'y', sparse=True); loads(dumps(k))
    Sparse Univariate Polynomial Ring in y over Integer Ring

The rings of sparse and dense polynomials in the same variable are
canonically isomorphic:
    sage: PolynomialRing(ZZ,'y', sparse=True) == PolynomialRing(ZZ,'y')
    True

    sage: QQ['y'] < QQ['x']
    False
    sage: QQ['y'] < QQ['z']
    True

We create a polynomial ring over a quaternion algebra:
    sage: A.<i,j,k> = QuaternionAlgebra(QQ, -1,-1)
    sage: R.<w> = PolynomialRing(A,sparse=True)
    sage: f = w^3 + (i+j)*w + 1
    sage: f
    w^3 + (i + j)*w + 1
    sage: f^2
    w^6 + (2*i + 2*j)*w^4 + 2*w^3 + (-2)*w^2 + (2*i + 2*j)*w + 1
    sage: f = w + i ; g = w + j
    sage: f * g
    w^2 + (i + j)*w + k
    sage: g * f
    w^2 + (i + j)*w + -k

TESTS:
    sage: K.<x>=FractionField(QQ['x'])
    sage: V.<z> = K[]
    sage: x+z
    z + x
"""


#################################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.structure.element import is_Element
import sage.algebras.algebra
import sage.rings.commutative_ring as commutative_ring
import sage.rings.commutative_algebra as commutative_algebra
import sage.rings.ring as ring
import sage.rings.ring_element as ring_element
import sage.rings.field as field
import sage.rings.integral_domain as integral_domain
import sage.rings.principal_ideal_domain as principal_ideal_domain
import sage.rings.polynomial.polynomial_element_generic as polynomial_element_generic
import sage.rings.rational_field as rational_field
from sage.rings.integer_ring import is_IntegerRing, IntegerRing
from sage.rings.integer import Integer
from sage.libs.pari.all import pari_gen
import sage.misc.defaults
import sage.misc.latex as latex
import sage.rings.polynomial.padics.polynomial_padic_capped_relative_dense as polynomial_padic_capped_relative_dense
import sage.rings.polynomial.polynomial_integer_dense_ntl as polynomial_integer_dense_ntl
import sage.rings.polynomial.polynomial_modn_dense_ntl as polynomial_modn_dense_ntl
import sage.rings.polynomial.padics.polynomial_padic_flat
from sage.rings.polynomial.polynomial_singular_interface import PolynomialRing_singular_repr
from sage.rings.fraction_field_element import FractionFieldElement

import cyclotomic

ZZ_sage = IntegerRing()

from sage.interfaces.singular import is_SingularElement


def is_PolynomialRing(x):
    """
    Return True if x is a *univariate* polynomial ring (and not a sparse multivariate
    polynomial ring in one variable).

    EXAMPLES:
        sage: is_PolynomialRing(2)
        False

    This polynomial ring is not univariate.
        sage: is_PolynomialRing(ZZ['x,y,z'])
        False
        sage: is_MPolynomialRing(ZZ['x,y,z'])
        True

        sage: is_PolynomialRing(ZZ['w'])
        True

    Univariate means not only in one variable, but is a specific data
    type.  There is a multivariate (sparse) polynomial ring data type,
    which supports a single variable as a special case.

        sage: is_PolynomialRing(PolynomialRing(ZZ,1,'w'))
        False
        sage: R = PolynomialRing(ZZ,1,'w'); R
        Multivariate Polynomial Ring in w over Integer Ring
        sage: is_PolynomialRing(R)
        False
        sage: type(R)
        <class 'sage.rings.polynomial.multi_polynomial_ring.MPolynomialRing_polydict_domain'>
    """
    return isinstance(x, PolynomialRing_general)


#########################################################################################

class PolynomialRing_general(sage.algebras.algebra.Algebra):
    """
    Univariate polynomial ring over a ring.
    """
    def __init__(self, base_ring, name=None, sparse=False):
        """
        EXAMPLES:
            sage: R.<x> = QQ['x']
            sage: R(-1) + R(1)
            0
            sage: (x - 2/3)*(x^2 - 8*x + 16)
            x^3 - 26/3*x^2 + 64/3*x - 32/3
        """
        sage.algebras.algebra.Algebra.__init__(self, base_ring, names=name, normalize=True)
        self.__is_sparse = sparse
        self.__set_polynomial_class()
        self.__generator = self([0,1], is_gen=True)
        self.__cyclopoly_cache = {}
        self._has_singular = False

    def __reduce__(self):
        import sage.rings.polynomial.polynomial_ring_constructor
        return (sage.rings.polynomial.polynomial_ring_constructor.PolynomialRing,
                (self.base_ring(), self.variable_name(), None, self.is_sparse()))


    def __call__(self, x=None, check=True, is_gen = False, construct=False, absprec = None):
        r"""
        Coerce \code{x} into this univariate polynomial ring, possibly non-canonically.

        Stacked polynomial rings coerce into constants if possible.  First,
        the univariate case:
            sage: R.<x> = QQ[]
            sage: S.<u> = R[]
            sage: S(u + 2)
            u + 2
            sage: S(x + 3)
            x + 3
            sage: S(x + 3).degree()
            0

        Second, the multivariate case:
            sage: R.<x,y> = QQ[]
            sage: S.<u> = R[]
            sage: S(x + 2*y)
            x + 2*y
            sage: S(x + 2*y).degree()
            0
            sage: S(u + 2*x)
            u + 2*x
            sage: S(u + 2*x).degree()
            1

        Foreign polynomial rings coerce into the highest ring; the point here
        is that an element of T could coerce to an element of R or an element
        of S; it is anticipated that an element of T is more likely to be "the
        right thing" and is historically consistent.
            sage: R.<x> = QQ[]
            sage: S.<u> = R[]
            sage: T.<a> = QQ[]
            sage: S(a)
            u

        Coercing in pari elements:
            sage: QQ['x'](pari('[1,2,3/5]'))
            3/5*x^2 + 2*x + 1
            sage: QQ['x'](pari('(-1/3)*x^10 + (2/3)*x - 1/5'))
            -1/3*x^10 + 2/3*x - 1/5

        Coercing strings:
            sage: QQ['y']('-y')
            -y
        """
        if is_Element(x):
            P = x.parent()
            if P is self:
                return x
            elif P == self.base_ring():
                return self([x])
        if hasattr(x, '_polynomial_'):
            return x._polynomial_(self)
        if is_SingularElement(x) and self._has_singular:
            self._singular_().set_ring()
            try:
                return x.sage_poly(self)
            except:
                raise TypeError, "Unable to coerce singular object"
        elif isinstance(x , str):
            try:
                from sage.misc.parser import Parser, LookupNameMaker
                R = self.base_ring()
                p = Parser(Integer, R, LookupNameMaker({self.variable_name(): self.gen()}, R))
                return self(p.parse(x))
            except NameError:
                raise TypeError,"Unable to coerce string"
        elif isinstance(x, FractionFieldElement):
            if x.denominator().is_unit():
                x = x.numerator() * x.denominator().inverse_of_unit()
            else:
                raise TypeError, "denominator must be a unit"

        elif isinstance(x, pari_gen):
            if x.type() != 't_POL':
                x = x.Polrev()

        C = self.__polynomial_class
        if absprec is None:
            return C(self, x, check, is_gen, construct=construct)
        else:
            return C(self, x, check, is_gen, construct=construct, absprec = absprec)

    def is_integral_domain(self):
        """
        EXAMPLES:
            sage: ZZ['x'].is_integral_domain()
            True
            sage: Integers(8)['x'].is_integral_domain()
            False
        """
        return self.base_ring().is_integral_domain()

    def is_noetherian(self):
        return self.base_ring().is_noetherian()

    def construction(self):
        from sage.categories.pushout import PolynomialFunctor
        return PolynomialFunctor(self.variable_name()), self.base_ring()

    def completion(self, p, prec=20, extras=None):
        """
        Return the completion of self with respect to the irreducible
        polynomial p.  Currently only implemented for p=self.gen(),
        i.e. you can only cimplete R[x] with respect to x, the result
        being a rings of power series in x. The prec variable controls
        the precision used in the power series ring.

        EXAMPLES:
            sage: P.<x>=PolynomialRing(QQ)
            sage: P
            Univariate Polynomial Ring in x over Rational Field
            sage: PP=P.completion(x)
            sage: PP
            Power Series Ring in x over Rational Field
            sage: f=1-x
            sage: PP(f)
            1 - x
            sage: 1/f
            1/(-x + 1)
            sage: 1/PP(f)
            1 + x + x^2 + x^3 + x^4 + x^5 + x^6 + x^7 + x^8 + x^9 + x^10 + x^11 + x^12 + x^13 + x^14 + x^15 + x^16 + x^17 + x^18 + x^19 + O(x^20)
        """
        if str(p) == self._names[0]:
            from sage.rings.power_series_ring import PowerSeriesRing
            return PowerSeriesRing(self.base_ring(), self._names[0], prec)
        else:
            raise TypeError, "Cannot complete %s with respect to %s" % (self, p)

    def _coerce_impl(self, x):
        """
        Return the canonical coercion of x to this polynomial ring, if one is
        defined, or raise a TypeError.

        The rings that canonically coerce to this polynomial ring are:
            * this ring itself
            * any ring that canonically coerces to the base ring of this ring.
            * polynomial rings in the same variable over any base ring that
              canonically coerces to the base ring of this ring
        """
        # handle constants that canonically coerce into self.base_ring()
        # first, if possible
        try:
            y = self.base_ring()._coerce_(x)
            return self([y])
        except TypeError:
            pass

        # polynomial rings in the same variable over a base that canonically
        # coerces into self.base_ring()
        try:
            P = x.parent()
            if is_PolynomialRing(P):
                if P.variable_name() == self.variable_name():
                    if self.has_coerce_map_from(P.base_ring()):
                        return self(x)
                    else:
                        raise TypeError, "no natural map between bases of polynomial rings"
        except AttributeError:
            pass
        raise TypeError

    def _magma_(self, G=None):
        """
        Used in converting this ring to the corresponding ring in MAGMA.

        EXAMPLES:
            sage: R.<y> = PolynomialRing(QQ)
            sage: S = magma(R) #optional
            sage: print S #optional
            Univariate Polynomial Ring in y over Rational Field
            sage: S.1 #optional
            y

            sage: magma(PolynomialRing(GF(7), 'x')) #optional
            Univariate Polynomial Ring in x over GF(7)

            sage: magma(PolynomialRing(GF(49,'a'), 'x')) #optional
            Univariate Polynomial Ring in x over GF(7^2)

            sage: magma(PolynomialRing(PolynomialRing(ZZ,'w'), 'x')) #optional
            Univariate Polynomial Ring in x over Univariate Polynomial Ring over Integer Ring
        """
        if G is None:
            import sage.interfaces.magma
            G = sage.interfaces.magma.magma
        R = G(self._magma_init_())
        R.assign_names(self.variable_names())
        return R

    def _magma_init_(self):
        return 'PolynomialRing(%s)'%(self.base_ring()._magma_init_())

    def _gap_(self, G=None):
        """
        Used in converting this ring to the corresponding ring in GAP.

        EXAMPLES:
            sage: R.<z> = ZZ[]
            sage: gap(R)
            PolynomialRing( Integers, ["z"] )
            sage: gap(z^2 + z)
            z^2+z
        """
        if G is None:
            import sage.interfaces.gap
            G = sage.interfaces.gap.gap
        R = G(self._gap_init_())
        v = self.variable_name()
        G.eval('%s := IndeterminatesOfPolynomialRing(%s)[1]'%(v, R.name()))
        return R

    def _gap_init_(self):
        return 'PolynomialRing(%s, ["%s"])'%(self.base_ring()._gap_init_(), self.variable_name())

    def _is_valid_homomorphism_(self, codomain, im_gens):
        try:
            # all that is needed is that elements of the base ring
            # of the polynomial ring canonically coerce into codomain.
            # Since poly rings are free, any image of the gen
            # determines a homomorphism
            codomain._coerce_(self.base_ring()(1))
        except TypeError:
            return False
        return True

    def __cmp__(left, right):
        c = cmp(type(left),type(right))
        if c: return c
        return cmp((left.base_ring(), left.variable_name()), (right.base_ring(), right.variable_name()))

    def _repr_(self):
        s = "Univariate Polynomial Ring in %s over %s"%(
                self.variable_name(), self.base_ring())
        if self.is_sparse():
            s = "Sparse " + s
        return s

    def _latex_(self):
        r"""
        EXAMPLES:
            sage: S.<alpha12>=ZZ[]
            sage: latex(S)
            \mathbf{Z}[\alpha_{12}]
        """
        return "%s[%s]"%(latex.latex(self.base_ring()), self.latex_variable_names()[0])

    def __set_polynomial_class(self, cls=None):
        from sage.rings.padics.padic_ring_capped_relative import pAdicRingCappedRelative
        from sage.rings.padics.padic_field_capped_relative import pAdicFieldCappedRelative
        from sage.rings.padics.padic_ring_lazy import pAdicRingLazy
        from sage.rings.padics.padic_field_lazy import pAdicFieldLazy
        from sage.rings.padics.padic_ring_capped_absolute import pAdicRingCappedAbsolute
        from sage.rings.padics.padic_ring_fixed_mod import pAdicRingFixedMod
        import sage.rings.polynomial.polynomial_element as polynomial_element

        if not (cls is None):
            self.__polynomial_class = cls
            return
        R = self.base_ring()
        if isinstance(R, rational_field.RationalField) and not self.is_sparse():
            self.__polynomial_class = polynomial_element_generic.Polynomial_rational_dense
        elif is_IntegerRing(R) and not self.is_sparse():
            self.__polynomial_class = polynomial_integer_dense_ntl.Polynomial_integer_dense_ntl
        elif isinstance(R, pAdicRingLazy):
            self.__polynomial_class = polynomial_element_generic.Polynomial_generic_dense # Fix
        elif isinstance(R, pAdicFieldLazy):
            self.__polynomial_class = polynomial_element_generic.Polynomial_generic_dense # Fix
        elif isinstance(R, pAdicRingCappedRelative):
            self.__polynomial_class = polynomial_padic_capped_relative_dense.Polynomial_padic_capped_relative_dense
        elif isinstance(R, pAdicFieldCappedRelative):
            self.__polynomial_class = polynomial_padic_capped_relative_dense.Polynomial_padic_capped_relative_dense
        elif isinstance(R, pAdicRingCappedAbsolute):
            self.__polynomial_class = sage.rings.polynomial.padics.polynomial_padic_flat.Polynomial_padic_flat # Fix
        elif isinstance(R, pAdicRingFixedMod):
            self.__polynomial_class = sage.rings.polynomial.padics.polynomial_padic_flat.Polynomial_padic_flat # Fix
        elif isinstance(R, field.Field):
            if self.__is_sparse:
                self.__polynomial_class = polynomial_element_generic.Polynomial_generic_sparse_field
            else:
                self.__polynomial_class = polynomial_element_generic.Polynomial_generic_dense_field
        elif self.__is_sparse:
            self.__polynomial_class = polynomial_element_generic.Polynomial_generic_sparse
        else:
            self.__polynomial_class = polynomial_element.Polynomial_generic_dense

    def base_extend(self, R):
        """
        Return the base extension of this polynomial ring to R.

        EXAMPLES:
            sage: R.<x> = RR[]; R
            Univariate Polynomial Ring in x over Real Field with 53 bits of precision
            sage: R.base_extend(CC)
            Univariate Polynomial Ring in x over Complex Field with 53 bits of precision
            sage: R.base_extend(QQ)
            Traceback (most recent call last):
            ...
            TypeError: no such base extension
            sage: R.change_ring(QQ)
            Univariate Polynomial Ring in x over Rational Field
        """
        from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

        if R.has_coerce_map_from(self.base_ring()):
            return PolynomialRing(R, names=self.variable_name(), sparse=self.is_sparse())
        else:
            raise TypeError, "no such base extension"

    def change_ring(self, R):
        """
        Return the polynomial ring in the same variable as self over R.

        EXAMPLES:
            sage: R.<ZZZ> = RealIntervalField() []; R
            Univariate Polynomial Ring in ZZZ over Real Interval Field with 53 bits of precision
            sage: R.change_ring(GF(19^2,'b'))
            Univariate Polynomial Ring in ZZZ over Finite Field in b of size 19^2
        """
        from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

        return PolynomialRing(R, names=self.variable_name(), sparse=self.is_sparse())

    def change_var(self, var):
        r"""
        Return the polynomial ring in variable var over the same base ring.

        EXAMPLES:
            sage: R.<x> = ZZ[]; R
            Univariate Polynomial Ring in x over Integer Ring
            sage: R.change_var('y')
            Univariate Polynomial Ring in y over Integer Ring
        """
        from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

        return PolynomialRing(self.base_ring(), names = var, sparse=self.is_sparse())

    def extend_variables(self, added_names, order = 'degrevlex'):
        r"""
        Returns a multivariate polynomial ring with the same base ring but with added_names as additional variables.

        EXAMPLES:
            sage: R.<x> = ZZ[]; R
            Univariate Polynomial Ring in x over Integer Ring
            sage: R.extend_variables('y, z')
            Multivariate Polynomial Ring in x, y, z over Integer Ring
            sage: R.extend_variables(('y', 'z'))
            Multivariate Polynomial Ring in x, y, z over Integer Ring
        """
        from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

        if isinstance(added_names, str):
            added_names = added_names.split(',')
        return PolynomialRing(self.base_ring(), names = self.variable_names() + tuple(added_names), order = order)

    def variable_names_recursive(self, depth=sage.rings.infinity.infinity):
        r"""
        Returns the list of variable names of this and its baserings, as if
        it were a single multi-variate polynomial.

        EXAMPLES:
            sage: R = QQ['x']['y']['z']
            sage: R.variable_names_recursive()
            ('x', 'y', 'z')
            sage: R.variable_names_recursive(2)
            ('y', 'z')

        """
        if depth <= 0:
            return ()
        elif depth == 1:
            return self.variable_names()
        else:
            my_vars = self.variable_names()
            try:
               return self.base_ring().variable_names_recursive(depth - len(my_vars)) + my_vars
            except AttributeError:
                return my_vars

    def _mpoly_base_ring(self, variables=None):
        r"""
        Returns the basering if this is viewed as a polynomial ring over \var{variables}.
        See also Polynomial._mpoly_dict_recursive
        """
        if variables is None:
            variables = self.variable_names_recursive()
        variables = list(variables)
        var = self.variable_name()
        if not var in variables:
            return self
        else:
            try:
                return self.base_ring()._mpoly_base_ring(variables[:variables.index(var)])
            except AttributeError:
                return self.base_ring()


    def characteristic(self):
        """
        Return the characteristic of this polynomial ring, which is the same
        as that of its base ring.

        EXAMPLES:
            sage: R.<ZZZ> = RealIntervalField() []; R
            Univariate Polynomial Ring in ZZZ over Real Interval Field with 53 bits of precision
            sage: R.characteristic()
            0
            sage: S = R.change_ring(GF(19^2,'b')); S
            Univariate Polynomial Ring in ZZZ over Finite Field in b of size 19^2
            sage: S.characteristic()
            19
        """
        return self.base_ring().characteristic()

    def cyclotomic_polynomial(self, n):
        """
        Return the nth cyclotomic polynomial as a polynomial in this polynomial ring.

        EXAMPLES:
            sage: R = ZZ['x']
            sage: R.cyclotomic_polynomial(8)
            x^4 + 1
            sage: R.cyclotomic_polynomial(12)
            x^4 - x^2 + 1
            sage: S = PolynomialRing(FiniteField(7), 'x')
            sage: S.cyclotomic_polynomial(12)
            x^4 + 6*x^2 + 1
            sage: S.cyclotomic_polynomial(1)
            x + 6

        TESTS:

        Make sure it agrees with other systems for the trivial case:
            sage: ZZ['x'].cyclotomic_polynomial(1)
            x - 1
            sage: gp('polcyclo(1)')
            x - 1
        """
        if n <= 0:
            raise ArithmeticError, "n=%s must be positive"%n
        elif n == 1:
            return self.gen() - 1
        else:
            return self(cyclotomic.cyclotomic_coeffs(n), check=True)

    def gen(self, n=0):
        """
        Return the indeterminate generator of this polynomial ring.

        EXAMPLES:
            sage: R.<abc> = Integers(8)[]; R
            Univariate Polynomial Ring in abc over Ring of integers modulo 8
            sage: t = R.gen(); t
            abc
            sage: t.is_gen()
            True

        An identical generator is always returned.
            sage: t is R.gen()
            True
        """
        if n != 0:
            raise IndexError, "generator n not defined"
        return self.__generator

    def parameter(self):
        """
        Return the generator of this polynomial ring.

        This is the same as \code{self.gen()}.
        """
        return self.gen()

    def is_finite(self):
        """
        Return False since polynomial rings are not finite (unless
        the base ring is 0.)

        EXAMPLES:
            sage: R = Integers(1)['x']
            sage: R.is_finite()
            True
            sage: R = GF(7)['x']
            sage: R.is_finite()
            False
            sage: R['x']['y'].is_finite()
            False
        """
        R = self.base_ring()
        if R.is_finite() and R.order() == 1:
            return True
        return False

    def is_exact(self):
        return self.base_ring().is_exact()

    def is_field(self):
        """
        Return False, since polynomial rings are never fields.

        EXAMPLES:
            sage: R.<z> = Integers(2)[]; R
            Univariate Polynomial Ring in z over Ring of integers modulo 2
            sage: R.is_field()
            False
        """
        return False

    def is_sparse(self):
        """
        Return true if elements of this polynomial ring have a sparse representation.

        EXAMPLES:
            sage: R.<z> = Integers(8)[]; R
            Univariate Polynomial Ring in z over Ring of integers modulo 8
            sage: R.is_sparse()
            False
            sage: R.<W> = PolynomialRing(QQ, sparse=True); R
            Sparse Univariate Polynomial Ring in W over Rational Field
            sage: R.is_sparse()
            True
        """
        return self.__is_sparse

    def krull_dimension(self):
        """
        Return the Krull dimension of this polynomial ring, which is one more than
        the Krull dimension of the base ring.

        EXAMPLES:
            sage: R.<x> = QQ[]
            sage: R.krull_dimension()
            1
            sage: R.<z> = GF(9,'a')[]; R
            Univariate Polynomial Ring in z over Finite Field in a of size 3^2
            sage: R.krull_dimension()
            1
            sage: S.<t> = R[]
            sage: S.krull_dimension()
            2
            sage: for n in range(10):
            ...    S = PolynomialRing(S,'w')
            sage: S.krull_dimension()
            12
        """
        return self.base_ring().krull_dimension() + 1

    def ngens(self):
        """
        Return the number of generators of this polynomial ring, which is 1 since
        it is a univariate polynomial ring.

        EXAMPLES:
            sage: R.<z> = Integers(8)[]; R
            Univariate Polynomial Ring in z over Ring of integers modulo 8
            sage: R.ngens()
            1
        """
        return 1

    def random_element(self, degree=2, *args, **kwds):
        r"""
        Return a random polynomial.

        INPUT:
            degree -- an integer
            *args, **kwds -- passed onto the \code{random_element} method for the base ring.

        OUTPUT:
            Polynomial -- A polynomial such that the coefficient of $x^i$,
            for $i$ up to \var{degree}, are coercions to the base ring of
            random integers between -\var{bound} and \var{bound}.

        EXAMPLES:
            sage: R.<x> = ZZ[]
            sage: R.random_element(10, 5,10)
            9*x^10 + 8*x^9 + 6*x^8 + 8*x^7 + 8*x^6 + 9*x^5 + 8*x^4 + 8*x^3 + 6*x^2 + 8*x + 8
            sage: R.random_element(6)
            x^6 - 3*x^5 - x^4 + x^3 - x^2 + x + 1
            sage: R.random_element(6)
            -2*x^5 + 2*x^4 - 3*x^3 + 1
            sage: R.random_element(6)
            x^4 - x^3 + x - 2
        """
        R = self.base_ring()
        return self([R.random_element(*args, **kwds) for _ in xrange(degree+1)])

    def _monics_degree( self, of_degree ):
        """
        Refer to monics() for full documentation.
        """
        base = self.base_ring()
        for coeffs in sage.misc.mrange.xmrange_iter([[base(1)]]+[base]*of_degree):
            # Each iteration returns a *new* list!
            # safe to mutate the return
            coeffs.reverse()
            yield self(coeffs)

    def _monics_max( self, max_degree ):
        """
        Refer to monics() for full documentation.
        """
        for degree in xrange(max_degree + 1):
            for m in self._monics_degree( degree ):
                yield m

    def _polys_degree( self, of_degree ):
        """
        Refer to polynomials() for full documentation.
        """
        base = self.base_ring()
        for leading_coeff in base:
            if leading_coeff != base(0):
                for lt1 in sage.misc.mrange.xmrange_iter([base]*(of_degree)):
                    # Each iteration returns a *new* list!
                    # safe to mutate the return
                    coeffs = [leading_coeff] + lt1
                    coeffs.reverse()
                    yield self(coeffs)

    def _polys_max( self, max_degree ):
        """
        Refer to polynomials() for full documentation.
        """
        base = self.base_ring()
        for coeffs in sage.misc.mrange.xmrange_iter([base]*(max_degree+1)):
            # Each iteration returns a *new* list!
            # safe to mutate the return
            coeffs.reverse()
            yield self(coeffs)

    def polynomials( self, of_degree = None, max_degree = None ):
        """
        Return an iterator over the polynomials of specified degree.

        INPUT:
            Pass exactly one of:
            max_degree -- an int; the iterator will generate all polynomials which have degree less than or equal to max_degree
            of_degree -- an int; the iterator will generate all polynomials which have degree of_degree

        OUTPUT:
            an iterator

        EXAMPLES:
            sage: P = PolynomialRing(GF(3),'y')
            sage: for p in P.polynomials( of_degree = 2 ): print p
            y^2
            y^2 + 1
            y^2 + 2
            y^2 + y
            y^2 + y + 1
            y^2 + y + 2
            y^2 + 2*y
            y^2 + 2*y + 1
            y^2 + 2*y + 2
            2*y^2
            2*y^2 + 1
            2*y^2 + 2
            2*y^2 + y
            2*y^2 + y + 1
            2*y^2 + y + 2
            2*y^2 + 2*y
            2*y^2 + 2*y + 1
            2*y^2 + 2*y + 2
            sage: for p in P.polynomials( max_degree = 1 ): print p
            0
            1
            2
            y
            y + 1
            y + 2
            2*y
            2*y + 1
            2*y + 2
            sage: for p in P.polynomials( max_degree = 1, of_degree = 3 ): print p
            Traceback (most recent call last):
            ...
            ValueError: you should pass exactly one of of_degree and max_degree

        AUTHOR:
            Joel B. Mohler
        """

        if self.base_ring().order() is sage.rings.infinity.infinity:
            raise NotImplementedError
        if of_degree is not None and max_degree is None:
            return self._polys_degree( of_degree )
        if max_degree is not None and of_degree is None:
            return self._polys_max( max_degree )
        raise ValueError, "you should pass exactly one of of_degree and max_degree"

    def monics( self, of_degree = None, max_degree = None ):
        """
        Return an iterator over the monic polynomials of specified degree.

        INPUT:
            Pass exactly one of:
            max_degree -- an int; the iterator will generate all monic polynomials which have degree less than or equal to max_degree
            of_degree -- an int; the iterator will generate all monic polynomials which have degree of_degree

        OUTPUT:
            an iterator

        EXAMPLES:
            sage: P = PolynomialRing(GF(4,'a'),'y')
            sage: for p in P.monics( of_degree = 2 ): print p
            y^2
            y^2 + a
            y^2 + a + 1
            y^2 + 1
            y^2 + a*y
            y^2 + a*y + a
            y^2 + a*y + a + 1
            y^2 + a*y + 1
            y^2 + (a + 1)*y
            y^2 + (a + 1)*y + a
            y^2 + (a + 1)*y + a + 1
            y^2 + (a + 1)*y + 1
            y^2 + y
            y^2 + y + a
            y^2 + y + a + 1
            y^2 + y + 1
            sage: for p in P.monics( max_degree = 1 ): print p
            1
            y
            y + a
            y + a + 1
            y + 1
            sage: for p in P.monics( max_degree = 1, of_degree = 3 ): print p
            Traceback (most recent call last):
            ...
            ValueError: you should pass exactly one of of_degree and max_degree

        AUTHOR:
            Joel B. Mohler
        """

        if self.base_ring().order() is sage.rings.infinity.infinity:
            raise NotImplementedError
        if of_degree is not None and max_degree is None:
            return self._monics_degree( of_degree )
        if max_degree is not None and of_degree is None:
            return self._monics_max( max_degree )
        raise ValueError, "you should pass exactly one of of_degree and max_degree"

class PolynomialRing_commutative(PolynomialRing_general, commutative_algebra.CommutativeAlgebra):
    """
    Univariate polynomial ring over a commutative ring.
    """
    def __init__(self, base_ring, name=None, sparse=False):
        if not isinstance(base_ring, commutative_ring.CommutativeRing):
            raise TypeError, "Base ring must be a commutative ring."
        PolynomialRing_general.__init__(self, base_ring, name=name, sparse=sparse)

    def quotient_by_principal_ideal(self, f, names=None):
        """
        Return the quotient of this polynomial ring by the principal
        ideal generated by $f$.

        EXAMPLES:
        """
        import sage.rings.polynomial.polynomial_quotient_ring
        return sage.rings.polynomial.polynomial_quotient_ring.PolynomialQuotientRing(self, f, names)




class PolynomialRing_integral_domain(PolynomialRing_commutative, integral_domain.IntegralDomain):
    def __init__(self, base_ring, name="x", sparse=False):
        PolynomialRing_commutative.__init__(self, base_ring, name, sparse)

class PolynomialRing_field(PolynomialRing_integral_domain,
                           PolynomialRing_singular_repr,
                           principal_ideal_domain.PrincipalIdealDomain,
                           ):
    def __init__(self, base_ring, name="x", sparse=False):
        from sage.rings.polynomial.polynomial_singular_interface import can_convert_to_singular
        PolynomialRing_commutative.__init__(self, base_ring, name, sparse)
        self._has_singular = can_convert_to_singular(self)

    def lagrange_polynomial(self, points):
        """
        Return the Lagrange interpolation polynomial in self
        associated to the given list of points.

        Given a list of points, i.e. tuples of elements of self's base
        ring, this function returns the interpolation polynomial in
        the Lagrange form.

        INPUT:
            points -- a list of tuples representing points through which
                      the polynomial returned by this function must pass.

        EXAMPLE:
            sage: R = PolynomialRing(QQ, 'x')
            sage: f = R.lagrange_polynomial([(0,1),(2,2),(3,-2),(-4,9)]);f
            -23/84*x^3 - 11/84*x^2 + 13/7*x + 1
            sage: f(0)
            1
            sage: f(2)
            2
            sage: f(3)
            -2
            sage: f(-4)
            9
            sage: R = PolynomialRing(GF(2**3,'a'), 'x')
            sage: a = R.base_ring().gen()
            sage: f = R.lagrange_polynomial([(a^2+a,a),(a,1),(a^2,a^2+a+1)]); f
            a^2*x^2 + a^2*x + a^2
            sage: f(a^2+a)
            a
            sage: f(a)
            1
            sage: f(a^2)
            a^2 + a + 1

        NOTE:  This is a straight forward Lagrange construction and no
        measures were taken to optimize it.   (If you need something
        that is highly optimized, consider implementing it and including
        it with SAGE.)
        """
        var = self.gen()

        def Pj(j):
            denom = 1
            divis = 1
            for i in range(len(points)):
                if i!=j:
                    denom *= (var          - points[i][0])
                    divis *= (points[j][0] - points[i][0])
            return denom/divis

        P = 0
        for j in range(len(points)):
            P += Pj(j)*points[j][1]
        return P

class PolynomialRing_dense_padic_ring_generic(PolynomialRing_integral_domain):
    def __init__(self, base_ring, name=None):
        PolynomialRing_integral_domain.__init__(self, base_ring, name)

class PolynomialRing_dense_padic_field_generic(PolynomialRing_field):
    def __init__(self, base_ring, name=None):
        PolynomialRing_field.__init__(self, base_ring, name)

class PolynomialRing_dense_padic_ring_capped_relative(PolynomialRing_dense_padic_ring_generic):
    pass

class PolynomialRing_dense_padic_ring_capped_absolute(PolynomialRing_dense_padic_ring_generic):
    pass

class PolynomialRing_dense_padic_ring_fixed_mod(PolynomialRing_dense_padic_ring_generic):
    pass

class PolynomialRing_dense_padic_ring_lazy(PolynomialRing_dense_padic_ring_generic):
    pass

class PolynomialRing_dense_padic_field_capped_relative(PolynomialRing_dense_padic_field_generic):
    pass

class PolynomialRing_dense_padic_field_lazy(PolynomialRing_dense_padic_field_generic):
    pass

class PolynomialRing_dense_mod_n(PolynomialRing_commutative):
    def __init__(self, base_ring, name="x"):
        self.__modulus = base_ring.order()
        PolynomialRing_commutative.__init__(self, base_ring, name)

    def modulus(self):
        return self.__modulus

    def __call__(self, x=None, check=True, is_gen = False, construct=False):
        if self.__modulus < ZZ_sage(polynomial_modn_dense_ntl.zz_p_max):
            return polynomial_modn_dense_ntl.Polynomial_dense_modn_ntl_zz(self, x, check, is_gen, construct=construct)
        else:
            return polynomial_modn_dense_ntl.Polynomial_dense_modn_ntl_ZZ(self, x, check, is_gen, construct=construct)

class PolynomialRing_dense_mod_p(PolynomialRing_dense_mod_n,
                                 PolynomialRing_singular_repr,
                                 principal_ideal_domain.PrincipalIdealDomain):
    def __init__(self, base_ring, name="x"):
        from sage.rings.polynomial.polynomial_singular_interface import can_convert_to_singular
        self.__modulus = base_ring.order()
        PolynomialRing_dense_mod_n.__init__(self, base_ring, name)
        self._has_singular = can_convert_to_singular(self)

    def __call__(self, x=None, check=True, is_gen = False, construct=False):
        if is_SingularElement(x) and self._has_singular:
            self._singular_().set_ring()
            try:
                return x.sage_poly(self)
            except:
                raise TypeError, "Unable to coerce singular object"
        elif isinstance(x , str) and self._has_singular:
            self._singular_().set_ring()
            try:
                return self._singular_().parent(x).sage_poly(self)
            except:
                raise TypeError,"Unable to coerce string"
        elif hasattr(x, '_polynomial_'):
            return x._polynomial_(self)
        return polynomial_modn_dense_ntl.Polynomial_dense_mod_p(self, x, check, is_gen,construct=construct)


def polygen(ring_or_element, name="x"):
    """
    Return a polynomial indeterminate.

    INPUT:
       * polygen(base_ring, name="x")
       * polygen(ring_element, name="x")

    If the first input is a ring, return a polynomial generator
    over that ring.  If it is a ring element, return a polynomial
    generator over the parent of the element.

    EXAMPLES:
        sage: z = polygen(QQ,'z')
        sage: z^3 + z +1
        z^3 + z + 1
        sage: parent(z)
        Univariate Polynomial Ring in z over Rational Field

    NOTE: If you give a list or comma separated string to polygen, you'll
    get a tuple of indeterminates, exactly as if you called polygens.
    """
    if ring_element.is_RingElement(ring_or_element):
        base_ring = ring_or_element.parent()
    elif ring.is_Ring(ring_or_element):
        base_ring = ring_or_element
    else:
        raise TypeError, "input must be a ring or ring element"
    from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

    t = PolynomialRing(base_ring, name)
    if t.ngens() > 1:
        return t.gens()
    return t.gen()

def polygens(base_ring, names="x"):
    """
    Return indeterminates over the given base ring with the given names.

    EXAMPLES:
        sage: x,y,z = polygens(QQ,'x,y,z')
        sage: (x+y+z)^2
        x^2 + 2*x*y + y^2 + 2*x*z + 2*y*z + z^2
        sage: parent(x)
        Multivariate Polynomial Ring in x, y, z over Rational Field
        sage: t = polygens(QQ,['x','yz','abc'])
        sage: t
        (x, yz, abc)
    """
    from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
    return PolynomialRing(base_ring, names).gens()
