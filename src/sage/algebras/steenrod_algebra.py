r"""
The Steenrod algebra

AUTHORS:

- John H. Palmieri (2008-07-30): version 0.9

This module defines the mod `p` Steenrod algebra
`\mathcal{A}_p`, some of its properties, and ways to
define elements of it.

From a topological point of view, `\mathcal{A}_p` is the
algebra of stable cohomology operations on mod `p`
cohomology; thus for any topological space `X`, its mod
`p` cohomology algebra `H^*(X,\mathbf{F}_p)` is a
module over `\mathcal{A}_p`.

From an algebraic point of view, `\mathcal{A}_p` is an
`\mathbf{F}_p`-algebra; when `p=2`, it is
generated by elements `\text{Sq}^i` for `i\geq 0`
(the *Steenrod squares*), and when `p` is odd, it is
generated by elements `\mathcal{P}^i` for
`i \geq 0` (the *Steenrod reduced `p`th powers*)
along with an element `\beta` (the
*mod `p` Bockstein*). The Steenrod algebra is graded:
`\text{Sq}^i` is in degree `i` for each
`i`, `\beta` is in degree 1, and
`\mathcal{P}^i` is in degree `2(p-1)i`.

The unit element is `\text{Sq}^0` when `p=2` and
`\mathcal{P}^0` when `p` is odd. The generating
elements also satisfy the *Adem relations*. At the prime 2, these
have the form

.. math::

     \text{Sq}^a \text{Sq}^b   = \sum_{c=0}^{[a/2]} \binom{b-c-1}{a-2c} \text{Sq}^{a+b-c} \text{Sq}^c.


At odd primes, they are a bit more complicated. See Steenrod and
Epstein [SE] for full details. These relations lead to the
existence of the *Serre-Cartan* basis for
`\mathcal{A}_p`.

The mod `p` Steenrod algebra has the structure of a Hopf
algebra, and Milnor [Mil] has a beautiful description of the dual,
leading to a construction of the *Milnor basis* for
`\mathcal{A}_p`. In this module, elements in the Steenrod
algebra are represented, by default, using the Milnor basis.

See the documentation for ``SteenrodAlgebra`` for many
more details and examples.

REFERENCES:

- [Mil] J. W. Milnor, "The Steenrod algebra and its dual," Ann. of
  Math. (2) 67 (1958), 150-171.

- [SE] N. E. Steenrod and D. B. A. Epstein, Cohomology operations,
  Ann. of Math. Stud. 50 (Princeton University Press, 1962).
"""

#*****************************************************************************
#       Copyright (C) 2008 John H. Palmieri <palmieri@math.washington.edu>
#  Distributed under the terms of the GNU General Public License (GPL)
#*****************************************************************************

from sage.rings.ring import Algebra
from sage.algebras.algebra_element import AlgebraElement
from sage.structure.parent_gens import ParentWithGens
from sage.structure.element import RingElement
from sage.rings.all import GF
from sage.misc.functional import parent
from sage.rings.integer import Integer
from sage.structure.factory import UniqueFactory

class SteenrodAlgebra_generic(Algebra):
    r"""
    The mod `p` Steenrod algebra.

    Users should not call this, but use the function 'SteenrodAlgebra'
    instead. See that function for extensive documentation.

    EXAMPLES::

        sage: sage.algebras.steenrod_algebra.SteenrodAlgebra_generic()
        mod 2 Steenrod algebra
        sage: sage.algebras.steenrod_algebra.SteenrodAlgebra_generic(5)
        mod 5 Steenrod algebra
        sage: sage.algebras.steenrod_algebra.SteenrodAlgebra_generic(5, 'adem')
        mod 5 Steenrod algebra
    """

    def __init__(self, p=2, basis='milnor'):
        """
        INPUT:


        -  ``p`` - positive prime integer (optional, default =
           2)

        -  ``basis`` - string (optional, default = 'milnor')


        OUTPUT: mod p Steenrod algebra with basis

        EXAMPLES::

            sage: SteenrodAlgebra()   # 2 is the default prime
            mod 2 Steenrod algebra
            sage: SteenrodAlgebra(5)
            mod 5 Steenrod algebra
            sage: SteenrodAlgebra(2, 'milnor').Sq(0,1)
            Sq(0,1)
            sage: SteenrodAlgebra(2, 'adem').Sq(0,1)
            Sq^{2} Sq^{1} + Sq^{3}
        """
        from sage.rings.arith import is_prime
        if is_prime(p):
            self.prime = p
            ParentWithGens.__init__(self, GF(p))
            self._basis_name = basis
        else:
            raise ValueError, "%s is not prime." % p


    def _repr_(self):
        """
        Printed representation of the Steenrod algebra.

        EXAMPLES::

            sage: SteenrodAlgebra(3)
            mod 3 Steenrod algebra
            sage: B = SteenrodAlgebra(2003)
            sage: B
            mod 2003 Steenrod algebra
            sage: B._repr_()
            'mod 2003 Steenrod algebra'
        """
        return "mod %d Steenrod algebra" % self.prime


    def _latex_(self):
        """
        LaTeX representation of the Steenrod algebra.

        EXAMPLES::

            sage: C = SteenrodAlgebra(3)
            sage: C
            mod 3 Steenrod algebra
            sage: C._latex_()
            '\\mathcal{A}_{3}'
        """
        return "\\mathcal{A}_{%s}" % self.prime


    def ngens(self):
        """
        Number of generators of the Steenrod algebra.

        This returns infinity, since the Steenrod algebra is infinitely
        generated.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.ngens()
            +Infinity
        """
        from sage.rings.infinity import Infinity
        return Infinity


    def gens(self):
        """
        List of generators for the Steenrod algebra. Not implemented
        (mainly because the list of generators is infinite).

        EXAMPLES::

            sage: A3 = SteenrodAlgebra(3, 'adem')
            sage: A3.gens()
            Traceback (most recent call last):
            ...
            NotImplementedError: 'gens' is not implemented for the Steenrod algebra.
        """
        raise NotImplementedError, "'gens' is not implemented " + \
            "for the Steenrod algebra."


    def gen(self, i=0):
        r"""
        The ith generator of the Steenrod algebra.

        INPUT:


        -  ``i`` - non-negative integer


        OUTPUT: the ith generator of the Steenrod algebra

        The `i^{th}` generator is `Sq(2^i)` at the prime 2;
        when `p` is odd, the 0th generator is
        `\beta = Q(0)`, and for `i>0`, the `i^{th}`
        generator is `P(p^{i-1})`.

        EXAMPLES::

            sage: A = SteenrodAlgebra(2)
            sage: A.gen(4)
            Sq(16)
            sage: A.gen(200)
            Sq(1606938044258990275541962092341162602522202993782792835301376)
            sage: B = SteenrodAlgebra(5)
            sage: B.gen(0)
            Q_0
            sage: B.gen(2)
            P(5)
        """
        if not isinstance(i, (Integer, int)) and i >= 0:
            raise ValueError, "%s is not a non-negative integer" % i
        if self.prime == 2:
            return self.Sq(self.prime**i)
        else:
            if i == 0:
                return self.Q(0)
            else:
                return self.P(self.prime**(i-1))

    def __cmp__(self,right):
        """
        Two Steenrod algebras are equal iff their associated primes are
        equal.

        EXAMPLES::

            sage: A = SteenrodAlgebra(2)
            sage: B = SteenrodAlgebra(2, 'adem')
            sage: cmp(A, B)
            0
            sage: A.__cmp__(B)
            0
            sage: A is B
            False
            sage: C = SteenrodAlgebra(17)
            sage: cmp(A,C)
            -1
        """
        if type(self) == type(right) and self.prime == right.prime:
            return 0
        else:
            return -1


    def __call__(self, x):
        """
        Try to turn x into an element of self.

        INPUT:


        -  ``x`` - a SteenrodAlgebra element or an element of
           F_p


        OUTPUT: x as a member of self

        Note that this provides a way of converting elements from one basis
        to another.

        EXAMPLES::

            sage: x = Sq(2,1)
            sage: x
            Sq(2,1)
            sage: B = SteenrodAlgebra(2, 'adem')
            sage: B(x)
            Sq^{4} Sq^{1} + Sq^{5}
        """
        from sage.algebras.steenrod_algebra_element import SteenrodAlgebraElement
        if isinstance(x, SteenrodAlgebraElement) and x.parent() == self:
            dict = x._raw
            a = SteenrodAlgebraElement(dict['milnor'],
                                       p=x._prime,
                                       basis=self._basis_name)
            a._raw = dict
            return a
        else:
            return SteenrodAlgebraElement(x, p=self.prime,
                                          basis=self._basis_name)


    def _coerce_impl(self, x):
        """
        Return the coercion of x into this Steenrod algebra.

        INPUT:


        -  ``x`` - a SteenrodAlgebraElement or an element of
           F_p


        OUTPUT: coercion of x into the Steenrod algebra

        EXAMPLES::

            sage: A = SteenrodAlgebra(); A
            mod 2 Steenrod algebra
            sage: A(1)     # convert 1 to an element of A
            Sq(0)
            sage: A(Sq(3))
            Sq(3)

        The algebras that coerce into the mod p Steenrod algebra are:

        - the mod p Steenrod algebra

        - its base field GF(p)
        """
        return self._coerce_try(x, [self.base_ring()])


    def __contains__(self, x):
        """
        Instances of the class SteenrodAlgebraElement with the same prime
        are contained in the Steenrod algebra.

        EXAMPLES::

            sage: A = SteenrodAlgebra()
            sage: x = Sq(2) * Sq(1); x
            Sq(0,1) + Sq(3)
            sage: x in A
            True
            sage: x in SteenrodAlgebra(5)
            False
        """
        from sage.algebras.steenrod_algebra_element import SteenrodAlgebraElement
        return (isinstance(x, SteenrodAlgebraElement) and x.parent() == self) \
            or (GF(self.prime).__contains__(x))


    def is_commutative(self):
        """
        The Steenrod algebra is not commutative.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.is_commutative()
            False
        """
        return False


    def is_finite(self):
        """
        The Steenrod algebra is not finite.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.is_finite()
            False
        """
        return False


    def order(self):
        """
        The Steenrod algebra has infinite order.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.order()
            +Infinity
        """
        from sage.rings.infinity import Infinity
        return Infinity


    def is_division_algebra(self):
        """
        The Steenrod algebra is not a division algebra.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.is_division_algebra()
            False
        """
        return False


    def is_field(self, proof = True):
        """
        The Steenrod algebra is not a field.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.is_field()
            False
        """
        return False


    def is_integral_domain(self, proof = True):
        """
        The Steenrod algebra is not an integral domain.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.is_integral_domain()
            False
        """
        return False


    def is_noetherian(self):
        """
        The Steenrod algebra is not noetherian.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.is_noetherian()
            False
        """
        return False


    def category(self):
        """
        The Steenrod algebra is an algebra over `F_p`.

        EXAMPLES::

            sage: A = SteenrodAlgebra(3)
            sage: A.category()
            Category of algebras over Finite Field of size 3
        """
        from sage.categories.category_types import Algebras
        return Algebras(GF(self.prime))


    def basis(self, n):
        """
        Basis for self in dimension n

        INPUT:


        -  ``n`` - non-negative integer


        OUTPUT:


        -  ``basis`` - tuple of Steenrod algebra elements


        EXAMPLES::

            sage: A3 = SteenrodAlgebra(3)
            sage: A3.basis(13)
            (Q_1 P(2), Q_0 P(3))
            sage: SteenrodAlgebra(2, 'adem').basis(12)
            (Sq^{12},
            Sq^{11} Sq^{1},
            Sq^{9} Sq^{2} Sq^{1},
            Sq^{8} Sq^{3} Sq^{1},
            Sq^{10} Sq^{2},
            Sq^{9} Sq^{3},
            Sq^{8} Sq^{4})
        """
        from steenrod_algebra_bases import steenrod_algebra_basis
        return steenrod_algebra_basis(n, basis=self._basis_name, p=self.prime)


    def P(self, *nums):
        r"""
        The element `P(a, b, c, ...)`

        INPUT:


        -  ``a, b, c, ...`` - non-negative integers


        OUTPUT: element of the Steenrod algebra given by the single basis
        element P(a, b, c, ...)

        Note that at the prime 2, this is the same element as
        `\text{Sq}(a, b, c, ...)`.

        EXAMPLES::

            sage: A = SteenrodAlgebra(2)
            sage: A.P(5)
            Sq(5)
            sage: B = SteenrodAlgebra(3)
            sage: B.P(5,1,1)
            P(5,1,1)
        """
        from sage.algebras.steenrod_algebra_element import SteenrodAlgebraElement
        if self.prime == 2:
            dict = {nums: 1}
        else:
            dict = {((), nums): 1}
        return SteenrodAlgebraElement(dict, p=self.prime,
                                      basis=self._basis_name)


    def Q_exp(self, *nums):
        r"""
        The element `Q_0^{e_0} Q_1^{e_1} ...` , given by
        specifying the exponents.

        INPUT:


        -  ``e0, e1, ...`` - 0s and 1s


        OUTPUT: The element `Q_0^{e_0} Q_1^{e_1} ...`

        Note that at the prime 2, `Q_n` is the element
        `\text{Sq}(0,0,...,1)` , where the 1 is in the
        `(n+1)^{st}` position.

        Compare this to the method 'Q', which defines a similar element,
        but by specifying the tuple of subscripts of terms with exponent
        1.

        EXAMPLES::

            sage: A2 = SteenrodAlgebra(2)
            sage: A5 = SteenrodAlgebra(5)
            sage: A2.Q_exp(0,0,1,1,0)
            Sq(0,0,1,1)
            sage: A5.Q_exp(0,0,1,1,0)
            Q_2 Q_3
            sage: A5.Q(2,3)
            Q_2 Q_3
            sage: A5.Q_exp(0,0,1,1,0) == A5.Q(2,3)
            True
        """
        from sage.algebras.steenrod_algebra_element import SteenrodAlgebraElement
        if not set(nums).issubset(set((0,1))):
            raise ValueError, "The tuple %s should consist " % (nums,) + \
                "only of 0's and 1's"
        else:
            if self.prime == 2:
                answer = self.Sq(0)
                index = 0
                for n in nums:
                    if n == 1:
                        answer = answer * self.pst(0,index+1)
                    index += 1
                return answer
            else:
                mono = ()
                index = 0
                for e in nums:
                    if e == 1:
                        mono = mono + (index,)
                    index += 1
                dict = {((mono), ()): 1}
                return SteenrodAlgebraElement(dict, p=self.prime,
                                              basis=self._basis_name)


    def Q(self, *nums):
        r"""
        The element `Q_{n0} Q_{n1} ...` , given by specifying the
        subscripts.

        INPUT:

        -  ``n0, n1, ...`` - non-negative integers


        OUTPUT: The element `Q_{n0} Q_{n1} ...`

        Note that at the prime 2, `Q_n` is the element
        `\text{Sq}(0,0,...,1)` , where the 1 is in the
        `(n+1)^{st}` position.

        Compare this to the method 'Q_exp', which defines a similar
        element, but by specifying the tuple of exponents.

        EXAMPLES::

            sage: A2 = SteenrodAlgebra(2)
            sage: A5 = SteenrodAlgebra(5)
            sage: A2.Q(2,3)
            Sq(0,0,1,1)
            sage: A5.Q(1,4)
            Q_1 Q_4
            sage: A5.Q(1,4) == A5.Q_exp(0,1,0,0,1)
            True
        """
        from sage.algebras.steenrod_algebra_element import SteenrodAlgebraElement
        if len(nums) != len(set(nums)):
            return self(0)
        else:
            if self.prime == 2:
                if len(nums) == 0:
                    return Sq(0)
                else:
                    list = (1+max(nums)) * [0]
                    for i in nums:
                        list[i] = 1
                    return SteenrodAlgebraElement({tuple(list): 1}, p=2,
                                                  basis=self._basis_name)
            else:
                return SteenrodAlgebraElement({(nums, ()): 1}, p=self.prime,
                                              basis=self._basis_name)


    def pst(self,s,t):
        r"""
        The Margolis element `P^s_t`.

        INPUT:


        -  ``s`` - non-negative integer

        -  ``t`` - positive integer

        -  ``p`` - positive prime number


        OUTPUT: element of the Steenrod algebra

        This returns the Margolis element `P^s_t` of the mod
        `p` Steenrod algebra: the element equal to
        `P(0,0,...,0,p^s)`, where the `p^s` is in position
        `t`.

        EXAMPLES::

            sage: A2 = SteenrodAlgebra(2)
            sage: A2.pst(3,5)
            Sq(0,0,0,0,8)
            sage: A2.pst(1,2) == Sq(4)*Sq(2) + Sq(2)*Sq(4)
            True
            sage: SteenrodAlgebra(5).pst(3,5)
            P(0,0,0,0,125)
        """
        from sage.algebras.steenrod_algebra_element import SteenrodAlgebraElement
        if not isinstance(s, (Integer, int)) and s >= 0:
            raise ValueError, "%s is not a non-negative integer" % s
        if not isinstance(t, (Integer, int)) and t > 0:
            raise ValueError, "%s is not a positive integer" % t
        nums = (0,)*(t-1) + (self.prime**s,)
        if self.prime == 2:
            return SteenrodAlgebraElement({nums: 1}, p=2, basis=self._basis_name)
        else:
            return SteenrodAlgebraElement({((), nums): 1}, p=self.prime,
                                          basis=self._basis_name)


class SteenrodAlgebra_mod_two(SteenrodAlgebra_generic):
    """
    The mod 2 Steenrod algebra.

    Users should not call this, but use the function 'SteenrodAlgebra'
    instead. See that function for extensive documentation. (This
    differs from SteenrodAlgebra_generic only in that it has a method
    'Sq' for defining elements.)
    """
    def Sq(self, *nums):
        r"""
        Milnor element `\text{Sq}(a,b,c,...)`.

        INPUT:


        -  ``a, b, c, ...`` - non-negative integers


        OUTPUT: element of the Steenrod algebra

        This returns the Milnor basis element
        `\text{Sq}(a, b, c, ...)`.

        EXAMPLES::

            sage: A = SteenrodAlgebra(2)
            sage: A.Sq(5)
            Sq(5)
            sage: A.Sq(5,0,2)
            Sq(5,0,2)

        Entries must be non-negative integers; otherwise, an error
        results.
        """
        from sage.algebras.steenrod_algebra_element import SteenrodAlgebraElement
        if self.prime == 2:
            dict = {nums: 1}
            return SteenrodAlgebraElement(dict, p=2, basis=self._basis_name)
        else:
            raise ValueError, "Sq is only defined at the prime 2"


# Now we specify the names of the implemented bases.  For the Milnor
# and Serre-Cartan bases, give a list of synonyms:

_steenrod_milnor_basis_names = ['milnor']
_steenrod_serre_cartan_basis_names = ['serre_cartan', 'serre-cartan', 'sc',
                                         'adem', 'admissible']

# For the other bases, use pattern-matching rather than a list of
# synonyms:
#   * Search for 'wood' and 'y' or 'wood' and 'z' to get the Wood bases.
#   * Search for 'arnon' and 'c' for the Arnon C basis.
#   * Search for 'arnon' (and no 'c') for the Arnon A basis.  Also see if
#     'long' is present, for the long form of the basis.
#   * Search for 'wall' for the Wall basis. Also see if 'long' is present.
#   * Search for 'pst' for P^s_t bases, then search for the order type:
#     'rlex', 'llex', 'deg', 'revz'.
#   * For commutator types, search for 'comm', an order type, and also
#     check to see if 'long' is present.

def get_basis_name(basis, p):
    """
    Return canonical basis named by string basis at the prime p.

    INPUT:

    - ``basis`` - string

    - ``p`` - positive prime number

    OUTPUT:

    - ``basis_name`` - string

    EXAMPLES::

        sage: sage.algebras.steenrod_algebra.get_basis_name('adem', 2)
        'serre-cartan'
        sage: sage.algebras.steenrod_algebra.get_basis_name('milnor', 2)
        'milnor'
        sage: sage.algebras.steenrod_algebra.get_basis_name('MiLNoR', 5)
        'milnor'
        sage: sage.algebras.steenrod_algebra.get_basis_name('pst-llex', 2)
        'pst_llex'
    """
    basis = basis.lower()
    if basis in _steenrod_milnor_basis_names:
        result = 'milnor'
    elif basis in _steenrod_serre_cartan_basis_names:
        result = 'serre-cartan'
    elif p == 2 and basis.find('pst') >= 0:
        if basis.find('rlex') >= 0:
            result = 'pst_rlex'
        elif basis.find('llex') >= 0:
            result = 'pst_llex'
        elif basis.find('deg') >= 0:
            result = 'pst_deg'
        elif basis.find('revz') >= 0:
            result = 'pst_revz'
        else:
            result = 'pst_revz'
    elif p == 2 and basis.find('comm') >= 0:
        if basis.find('rlex') >= 0:
            result = 'comm_rlex'
        elif basis.find('llex') >= 0:
            result = 'comm_llex'
        elif basis.find('deg') >= 0:
            result = 'comm_deg'
        elif basis.find('revz') >= 0:
            result = 'comm_revz'
        else:
            result = 'comm_revz'
        if basis.find('long') >= 0:
            result = result + '_long'
    elif p == 2 and basis.find('wood') >= 0:
        if basis.find('y') >= 0:
            result = 'woody'
        else:
            result = 'woodz'
    elif p == 2 and basis.find('arnon') >= 0:
        if basis.find('c') >= 0:
            result = 'arnonc'
        else:
            result = 'arnona'
            if basis.find('long') >= 0:
                result = result + '_long'
    elif p == 2 and basis.find('wall') >= 0:
        result = 'wall'
        if basis.find('long') >= 0:
            result = result + '_long'
    else:
        raise ValueError, "%s is not a recognized basis at the prime %s." % (basis, p)
    return result


class SteenrodAlgebraFactory(UniqueFactory):
    r"""
    The mod `p` Steenrod algebra

    INPUT:

    - ``p`` - positive prime integer (optional, default = 2)

    - ``basis`` - string (optional, default = 'milnor')

    OUTPUT:

    - mod `p` Steenrod algebra with given basis

    This returns the mod `p` Steenrod algebra, elements of which are
    printed using basis.

    EXAMPLES:

    Some properties of the Steenrod algebra are available::

        sage: A = SteenrodAlgebra(2)
        sage: A.ngens()  # number of generators
        +Infinity
        sage: A.gen(5)   # 5th generator
        Sq(32)
        sage: A.order()
        +Infinity
        sage: A.is_finite()
        False
        sage: A.is_commutative()
        False
        sage: A.is_noetherian()
        False
        sage: A.is_integral_domain()
        False
        sage: A.is_field()
        False
        sage: A.is_division_algebra()
        False
        sage: A.category()
        Category of algebras over Finite Field of size 2

    There are methods for constructing elements of the Steenrod
    algebra::

        sage: A2 = SteenrodAlgebra(2); A2
        mod 2 Steenrod algebra
        sage: A2.Sq(1,2,6)
        Sq(1,2,6)
        sage: A2.Q(3,4)  # product of Milnor primitives Q_3 and Q_4
        Sq(0,0,0,1,1)
        sage: A2.pst(2,3)  # Margolis pst element
        Sq(0,0,4)
        sage: A5 = SteenrodAlgebra(5); A5
        mod 5 Steenrod algebra
        sage: A5.P(1,2,6)
        P(1,2,6)
        sage: A5.Q(3,4)
        Q_3 Q_4
        sage: A5.Q(3,4) * A5.P(1,2,6)
        Q_3 Q_4 P(1,2,6)
        sage: A5.pst(2,3)
        P(0,0,25)

    You can test whether elements are contained in the Steenrod
    algebra::

        sage: w = Sq(2) * Sq(4)
        sage: w in SteenrodAlgebra(2)
        True
        sage: w in SteenrodAlgebra(17)
        False

    Different bases for the Steenrod algebra:

    There are two standard vector space bases for the mod `p`
    Steenrod algebra: the Milnor basis and the Serre-Cartan basis. When
    `p=2`, there are also several other, less well-known,
    bases. See the documentation for the function
    'steenrod_algebra_basis' for full descriptions of each of the
    implemented bases.

    This module implements the following bases at all primes:

    - 'milnor': Milnor basis.

    - 'serre-cartan' or 'adem' or 'admissible': Serre-Cartan basis.

    It implements the following bases when `p=2`:

    - 'wood_y': Wood's Y basis.

    - 'wood_z': Wood's Z basis.

    - 'wall', 'wall_long': Wall's basis.

    - 'arnon_a', 'arnon_a_long': Arnon's A basis.

    - 'arnon_c': Arnon's C basis.

    - 'pst', 'pst_rlex', 'pst_llex', 'pst_deg', 'pst_revz': various
      `P^s_t`-bases.

    - 'comm', 'comm_rlex', 'comm_llex', 'comm_deg', 'comm_revz', or
      these with '_long' appended: various commutator bases.

    When defining a Steenrod algebra, you can specify a basis. Then
    elements of that Steenrod algebra are printed in that basis

    ::

        sage: adem = SteenrodAlgebra(2, 'adem')
        sage: x = adem.Sq(2,1)  # Sq(-) always means a Milnor basis element
        sage: x
        Sq^{4} Sq^{1} + Sq^{5}
        sage: y = Sq(0,1)    # unadorned Sq defines elements w.r.t. Milnor basis
        sage: y
        Sq(0,1)
        sage: adem(y)
        Sq^{2} Sq^{1} + Sq^{3}
        sage: adem5 = SteenrodAlgebra(5, 'serre-cartan')
        sage: adem5.P(0,2)
        P^{10} P^{2} + 4 P^{11} P^{1} + P^{12}

    You can get a list of basis elements in a given dimension::

        sage: A3 = SteenrodAlgebra(3, 'milnor')
        sage: A3.basis(13)
        (Q_1 P(2), Q_0 P(3))

    As noted above, several of the bases ('arnon_a', 'wall', 'comm')
    have alternate, longer, representations. These provide ways of
    expressing elements of the Steenrod algebra in terms of the
    `\text{Sq}^{2^n}`.

    ::

        sage: A_long = SteenrodAlgebra(2, 'arnon_a_long')
        sage: A_long(Sq(6))
        Sq^{1} Sq^{2} Sq^{1} Sq^{2} + Sq^{2} Sq^{4}
        sage: SteenrodAlgebra(2, 'wall_long')(Sq(6))
        Sq^{2} Sq^{1} Sq^{2} Sq^{1} + Sq^{2} Sq^{4}
        sage: SteenrodAlgebra(2, 'comm_deg_long')(Sq(6))
        s_{1} s_{2} s_{12} + s_{2} s_{4}

    Testing unique parents::

        sage: S0 = SteenrodAlgebra(2)
        sage: S1 = SteenrodAlgebra(2)
        sage: S0 is S1
        True
    """
    def create_key(self, p = 2, basis = 'milnor'):
        """
        This is an internal function that is used to ensure unique
        parents.  Not for public consumption.

        EXAMPLES::

            sage: SteenrodAlgebra.create_key()
            (2, 'milnor')
        """
        return (p,basis)

    def create_object(self, version, key, **extra_args):
        """
        This is an internal function that is used to ensure unique
        parents.  Not for public consumption.

        EXAMPLES::

            sage: SteenrodAlgebra.create_object(1,(11,'milnor'))
            mod 11 Steenrod algebra
        """

        p = key[0]
        basis = key[1]
        basis_name = get_basis_name(basis, p)
        if p == 2:
            return SteenrodAlgebra_mod_two(p=2, basis=basis_name)
        else:
            return SteenrodAlgebra_generic(p=p, basis=basis_name)

SteenrodAlgebra = SteenrodAlgebraFactory("SteenrodAlgebra")
