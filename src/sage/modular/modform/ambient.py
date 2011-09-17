# -*- coding: utf-8 -*-
r"""
Ambient Spaces of Modular Forms.

EXAMPLES:

We compute a basis for the ambient space
`M_2(\Gamma_1(25),\chi)`, where `\chi` is
quadratic.

::

    sage: chi = DirichletGroup(25,QQ).0; chi
    Dirichlet character modulo 25 of conductor 5 mapping 2 |--> -1
    sage: n = ModularForms(chi,2); n
    Modular Forms space of dimension 6, character [-1] and weight 2 over Rational Field
    sage: type(n)
    <class 'sage.modular.modform.ambient_eps.ModularFormsAmbient_eps_with_category'>

Compute a basis::

    sage: n.basis()
    [
    1 + O(q^6),
    q + O(q^6),
    q^2 + O(q^6),
    q^3 + O(q^6),
    q^4 + O(q^6),
    q^5 + O(q^6)
    ]

Compute the same basis but to higher precision::

    sage: n.set_precision(20)
    sage: n.basis()
    [
    1 + 10*q^10 + 20*q^15 + O(q^20),
    q + 5*q^6 + q^9 + 12*q^11 - 3*q^14 + 17*q^16 + 8*q^19 + O(q^20),
    q^2 + 4*q^7 - q^8 + 8*q^12 + 2*q^13 + 10*q^17 - 5*q^18 + O(q^20),
    q^3 + q^7 + 3*q^8 - q^12 + 5*q^13 + 3*q^17 + 6*q^18 + O(q^20),
    q^4 - q^6 + 2*q^9 + 3*q^14 - 2*q^16 + 4*q^19 + O(q^20),
    q^5 + q^10 + 2*q^15 + O(q^20)
    ]

TESTS::

    sage: m = ModularForms(Gamma1(20),2,GF(7))
    sage: loads(dumps(m)) == m
    True

::

    sage: m = ModularForms(GammaH(11,[2]), 2); m
    Modular Forms space of dimension 2 for Congruence Subgroup Gamma_H(11) with H generated by [2] of weight 2 over Rational Field
    sage: type(m)
    <class 'sage.modular.modform.ambient_g1.ModularFormsAmbient_gH_Q_with_category'>
    sage: m == loads(dumps(m))
    True
"""

#########################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#########################################################################

# system packages

# Sage packages
import sage.rings.all as rings
import sage.modular.arithgroup.all as arithgroup
import sage.modular.dirichlet as dirichlet
import sage.modular.hecke.all as hecke
import sage.modular.modsym.all as modsym
import sage.modules.free_module as free_module
import sage.rings.all as rings

from sage.structure.sequence import Sequence


import cuspidal_submodule
import defaults
import eisenstein_submodule
import eis_series
import space
import submodule


class ModularFormsAmbient(space.ModularFormsSpace,
                          hecke.AmbientHeckeModule):
    """
    An ambient space of modular forms.
    """
    def __init__(self, group, weight, base_ring, character=None):
        """
        Create an ambient space of modular forms.

        EXAMPLES::

            sage: m = ModularForms(Gamma1(20),20); m
            Modular Forms space of dimension 238 for Congruence Subgroup Gamma1(20) of weight 20 over Rational Field
            sage: m.is_ambient()
            True
        """
        if not arithgroup.is_CongruenceSubgroup(group):
            raise TypeError, 'group (=%s) must be a congruence subgroup'%group
        weight = rings.Integer(weight)

        if character is None and arithgroup.is_Gamma0(group):
            character = dirichlet.TrivialCharacter(group.level(), base_ring)

        space.ModularFormsSpace.__init__(self, group, weight, character, base_ring)
        try:
            d = self.dimension()
        except NotImplementedError:
            d = None
        hecke.AmbientHeckeModule.__init__(self, base_ring, d, group.level(), weight)

    def _repr_(self):
        """
        Return string representation of self.

        EXAMPLES::

            sage: m = ModularForms(Gamma1(20),100); m._repr_()
            'Modular Forms space of dimension 1198 for Congruence Subgroup Gamma1(20) of weight 100 over Rational Field'

        The output of _repr_ is not affected by renaming the space::

            sage: m.rename('A big modform space')
            sage: m
            A big modform space
            sage: m._repr_()
            'Modular Forms space of dimension 1198 for Congruence Subgroup Gamma1(20) of weight 100 over Rational Field'
        """
        try:
            d = self.dimension()
        except NotImplementedError:
            d = "(unknown)"
        return "Modular Forms space of dimension %s for %s of weight %s over %s"%(
                d, self.group(), self.weight(), self.base_ring())

    def _submodule_class(self):
        """
        Return the Python class of submodules of this modular forms space.

        EXAMPLES::

            sage: m = ModularForms(Gamma0(20),2)
            sage: m._submodule_class()
            <class 'sage.modular.modform.submodule.ModularFormsSubmodule'>
        """
        return submodule.ModularFormsSubmodule

    def change_ring(self, base_ring):
        """
        Change the base ring of this space of modular forms.

        INPUT:


        -  ``R`` - ring


        EXAMPLES::

            sage: M = ModularForms(Gamma0(37),2)
            sage: M.basis()
            [
            q + q^3 - 2*q^4 + O(q^6),
            q^2 + 2*q^3 - 2*q^4 + q^5 + O(q^6),
            1 + 2/3*q + 2*q^2 + 8/3*q^3 + 14/3*q^4 + 4*q^5 + O(q^6)
            ]

        The basis after changing the base ring is the reduction modulo
        `3` of an integral basis.

        ::

            sage: M3 = M.change_ring(GF(3))
            sage: M3.basis()
            [
            1 + q^3 + q^4 + 2*q^5 + O(q^6),
            q + q^3 + q^4 + O(q^6),
            q^2 + 2*q^3 + q^4 + q^5 + O(q^6)
            ]
        """
        import constructor
        M = constructor.ModularForms(self.group(), self.weight(), base_ring, prec=self.prec())
        return M

    def dimension(self):
        """
        Return the dimension of this ambient space of modular forms,
        computed using a dimension formula (so it should be reasonably
        fast).

        EXAMPLES::

            sage: m = ModularForms(Gamma1(20),20)
            sage: m.dimension()
            238
        """
        try:
            return self.__dimension
        except AttributeError:
            self.__dimension = self._dim_eisenstein() + self._dim_cuspidal()
            return self.__dimension

    def hecke_module_of_level(self, N):
        r"""
        Return the Hecke module of level N corresponding to self, which is the
        domain or codomain of a degeneracy map from self. Here N must be either
        a divisor or a multiple of the level of self.

        EXAMPLES::

            sage: ModularForms(25, 6).hecke_module_of_level(5)
            Modular Forms space of dimension 3 for Congruence Subgroup Gamma0(5) of weight 6 over Rational Field
            sage: ModularForms(Gamma1(4), 3).hecke_module_of_level(8)
            Modular Forms space of dimension 7 for Congruence Subgroup Gamma1(8) of weight 3 over Rational Field
            sage: ModularForms(Gamma1(4), 3).hecke_module_of_level(9)
            Traceback (most recent call last):
            ...
            ValueError: N (=9) must be a divisor or a multiple of the level of self (=4)
        """
        if not (N % self.level() == 0 or self.level() % N == 0):
            raise ValueError, "N (=%s) must be a divisor or a multiple of the level of self (=%s)" % (N, self.level())
        import constructor
        return constructor.ModularForms(self.group()._new_group_from_level(N), self.weight(), self.base_ring(), prec=self.prec())

    def _degeneracy_raising_matrix(self, M, t):
        r"""
        Calculate the matrix of the degeneracy map from self to M corresponding
        to `f(q) \mapsto f(q^t)`. Here the level of M should be a multiple of
        the level of self, and t should divide the quotient.

        EXAMPLE::

            sage: ModularForms(22, 2)._degeneracy_raising_matrix(ModularForms(44, 2), 1)
            [  1   0  -1  -2   0   0   0   0   0]
            [  0   1   0  -2   0   0   0   0   0]
            [  0   0   0   0   1   0   0   0  24]
            [  0   0   0   0   0   1   0  -2  21]
            [  0   0   0   0   0   0   1   3 -10]
            sage: ModularForms(22, 2)._degeneracy_raising_matrix(ModularForms(44, 2), 2)
            [0 1 0 0 0 0 0 0 0]
            [0 0 0 1 0 0 0 0 0]
            [0 0 0 0 1 0 0 0 0]
            [0 0 0 0 0 0 1 0 0]
            [0 0 0 0 0 0 0 1 0]
        """
        from sage.matrix.matrix_space import MatrixSpace
        A = MatrixSpace(self.base_ring(), self.dimension(), M.dimension())
        d = M.sturm_bound() + 1
        q = self.an_element().qexp(d).parent().gen()
        im_gens = []
        for x in self.basis():
            fq = x.qexp(d)
            fqt = fq(q**t).add_bigoh(d) # silly workaround for #5367
            im_gens.append(M(fqt))
        return A([M.coordinate_vector(u) for u in im_gens])

    def rank(self):
        r"""
        This is a synonym for ``self.dimension()``.

        EXAMPLES::

            sage: m = ModularForms(Gamma0(20),4)
            sage: m.rank()
            12
            sage: m.dimension()
            12
        """
        return self.dimension()

    def ambient_space(self):
        """
        Return the ambient space that contains this ambient space. This is,
        of course, just this space again.

        EXAMPLES::

            sage: m = ModularForms(Gamma0(3),30)
            sage: m.ambient_space() is m
            True
        """
        return self

    def is_ambient(self):
        """
        Return True if this an ambient space of modular forms.

        This is an ambient space, so this function always returns True.

        EXAMPLES::

            sage: ModularForms(11).is_ambient()
            True
            sage: CuspForms(11).is_ambient()
            False
        """
        return True

    def modular_symbols(self, sign=0):
        """
        Return the corresponding space of modular symbols with the given
        sign.

        EXAMPLES::

            sage: S = ModularForms(11,2)
            sage: S.modular_symbols()
            Modular Symbols space of dimension 3 for Gamma_0(11) of weight 2 with sign 0 over Rational Field
            sage: S.modular_symbols(sign=1)
            Modular Symbols space of dimension 2 for Gamma_0(11) of weight 2 with sign 1 over Rational Field
            sage: S.modular_symbols(sign=-1)
            Modular Symbols space of dimension 1 for Gamma_0(11) of weight 2 with sign -1 over Rational Field

        ::

            sage: ModularForms(1,12).modular_symbols()
            Modular Symbols space of dimension 3 for Gamma_0(1) of weight 12 with sign 0 over Rational Field
        """
        sign = rings.Integer(sign)
        try:
            return self.__modular_symbols[sign]
        except AttributeError:
            self.__modular_symbols = {}
        except KeyError:
            pass
        M = modsym.ModularSymbols(group = self.group(),
                                  weight = self.weight(),
                                  sign = sign,
                                  base_ring = self.base_ring())
        self.__modular_symbols[sign] = M
        return M

    def module(self):
        """
        Return the underlying free module corresponding to this space
        of modular forms.

        If the dimension of self can be computed reasonably quickly,
        then this function returns a free module (viewed as a tuple
        space) of the same dimension as self over the same base ring.
        Otherwise, the dimension of self.module() may be smaller.  For
        example, in the case of weight 1 forms, in some cases the
        dimension can't easily be computed so self.module() is of
        smaller dimension.

        EXAMPLES::

            sage: m = ModularForms(Gamma1(13),10)
            sage: m.free_module()
            Vector space of dimension 69 over Rational Field
            sage: ModularForms(Gamma1(13),4, GF(49,'b')).free_module()
            Vector space of dimension 27 over Finite Field in b of size 7^2

        Note that in the following example the dimension can't be
        (quickly) computed, so M.module() returns a space of different
        dimension than M::

            sage: M = ModularForms(Gamma1(57), 1); M
            Modular Forms space of dimension (unknown) for Congruence ...
            sage: M.module()
            Vector space of dimension 36 over Rational Field
            sage: M.basis()
            Traceback (most recent call last):
            ...
            NotImplementedError: Computation of dimensions of weight 1 cusp forms spaces not implemented in general
        """
        if hasattr(self, "__module"): return self.__module
        try:
            d = self.dimension()
        except NotImplementedError:

            # This only comes up for weight 1 forms, where we want to be able
            # to embed Eisenstein forms (which we know how to calculate) into
            # some suitable ambient space. Because we can't even calculate the
            # dimension of the weight 1 cusp forms in general, we just map
            # Eisenstein series onto basis vectors, and then make it clear by
            # raising errors in appropriate places that some cusp forms might
            # exist but we don't know how to compute them.

            d = self._dim_eisenstein()
        self.__module = free_module.VectorSpace(self.base_ring(), d)
        return self.__module

    # free_module -- stupid thing: there are functions in classes
    # ModularFormsSpace and HeckeModule that both do much the same
    # thing, and one has to override both of them!
    def free_module(self):
        """
        Return the free module underlying this space of modular forms.

        EXAMPLES::

            sage: ModularForms(37).free_module()
            Vector space of dimension 3 over Rational Field
        """
        return self.module()

    def prec(self, new_prec=None):
        """
        Set or get default initial precision for printing modular forms.

        INPUT:


        -  ``new_prec`` - positive integer (default: None)


        OUTPUT: if new_prec is None, returns the current precision.

        EXAMPLES::

            sage: M = ModularForms(1,12, prec=3)
            sage: M.prec()
            3

        ::

            sage: M.basis()
            [
            q - 24*q^2 + O(q^3),
            1 + 65520/691*q + 134250480/691*q^2 + O(q^3)
            ]

        ::

            sage: M.prec(5)
            5
            sage: M.basis()
            [
            q - 24*q^2 + 252*q^3 - 1472*q^4 + O(q^5),
            1 + 65520/691*q + 134250480/691*q^2 + 11606736960/691*q^3 + 274945048560/691*q^4 + O(q^5)
            ]
        """
        if new_prec:
            self.__prec = new_prec
        try:
            return self.__prec
        except AttributeError:
            self.__prec = defaults.DEFAULT_PRECISION
        return self.__prec

    def set_precision(self, n):
        """
        Set the default precision for displaying elements of this space.

        EXAMPLES::

            sage: m = ModularForms(Gamma1(5),2)
            sage: m.set_precision(10)
            sage: m.basis()
            [
            1 + 60*q^3 - 120*q^4 + 240*q^5 - 300*q^6 + 300*q^7 - 180*q^9 + O(q^10),
            q + 6*q^3 - 9*q^4 + 27*q^5 - 28*q^6 + 30*q^7 - 11*q^9 + O(q^10),
            q^2 - 4*q^3 + 12*q^4 - 22*q^5 + 30*q^6 - 24*q^7 + 5*q^8 + 18*q^9 + O(q^10)
            ]
            sage: m.set_precision(5)
            sage: m.basis()
            [
            1 + 60*q^3 - 120*q^4 + O(q^5),
            q + 6*q^3 - 9*q^4 + O(q^5),
            q^2 - 4*q^3 + 12*q^4 + O(q^5)
            ]
        """
        if n < 0:
            raise ValueError, "n (=%s) must be >= 0"%n
        self.__prec = rings.Integer(n)

    ####################################################################
    # Computation of Special Submodules
    ####################################################################
    def cuspidal_submodule(self):
        """
        Return the cuspidal submodule of this ambient module.

        EXAMPLES::

            sage: ModularForms(Gamma1(13)).cuspidal_submodule()
            Cuspidal subspace of dimension 2 of Modular Forms space of dimension 13 for
            Congruence Subgroup Gamma1(13) of weight 2 over Rational Field
        """
        try:
            return self.__cuspidal_submodule
        except AttributeError:
            self.__cuspidal_submodule = cuspidal_submodule.CuspidalSubmodule(self)
        return self.__cuspidal_submodule

    def eisenstein_submodule(self):
        """
        Return the Eisenstein submodule of this ambient module.

        EXAMPLES::

            sage: m = ModularForms(Gamma1(13),2); m
            Modular Forms space of dimension 13 for Congruence Subgroup Gamma1(13) of weight 2 over Rational Field
            sage: m.eisenstein_submodule()
            Eisenstein subspace of dimension 11 of Modular Forms space of dimension 13 for Congruence Subgroup Gamma1(13) of weight 2 over Rational Field
        """
        try:
            return self.__eisenstein_submodule
        except AttributeError:
            self.__eisenstein_submodule = eisenstein_submodule.EisensteinSubmodule(self)
        return self.__eisenstein_submodule

    def new_submodule(self, p=None):
        """
        Return the new or `p`-new submodule of this ambient
        module.

        INPUT:


        -  ``p`` - (default: None), if specified return only
           the `p`-new submodule.


        EXAMPLES::

            sage: m = ModularForms(Gamma0(33),2); m
            Modular Forms space of dimension 6 for Congruence Subgroup Gamma0(33) of weight 2 over Rational Field
            sage: m.new_submodule()
            Modular Forms subspace of dimension 1 of Modular Forms space of dimension 6 for Congruence Subgroup Gamma0(33) of weight 2 over Rational Field

        Another example::

            sage: M = ModularForms(17,4)
            sage: N = M.new_subspace(); N
            Modular Forms subspace of dimension 4 of Modular Forms space of dimension 6 for Congruence Subgroup Gamma0(17) of weight 4 over Rational Field
            sage: N.basis()
            [
            q + 2*q^5 + O(q^6),
            q^2 - 3/2*q^5 + O(q^6),
            q^3 + O(q^6),
            q^4 - 1/2*q^5 + O(q^6)
            ]

        ::

            sage: ModularForms(12,4).new_submodule()
            Modular Forms subspace of dimension 1 of Modular Forms space of dimension 9 for Congruence Subgroup Gamma0(12) of weight 4 over Rational Field

        Unfortunately (TODO) - `p`-new submodules aren't yet
        implemented::

            sage: m.new_submodule(3)            # not implemented
            Traceback (most recent call last):
            ...
            NotImplementedError
            sage: m.new_submodule(11)           # not implemented
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        try:
            return self.__new_submodule[p]
        except AttributeError:
           self.__new_submodule = {}
        except KeyError:
           pass
        if not p is None:
            p = rings.Integer(p)
            if not p.is_prime():
               raise ValueError, "p (=%s) must be a prime or None."%p
        M = self.cuspidal_submodule().new_submodule(p) + self.eisenstein_submodule().new_submodule(p)
        self.__new_submodule[p] = M
        return M

    def _q_expansion(self, element, prec):
        r"""
        Return the q-expansion of a particular element of this space of
        modular forms, where the element should be a vector, list, or tuple
        (not a ModularFormElement). Here element should have length =
        self.dimension(). If element = [ a_i ] and self.basis() = [ v_i
        ], then we return `\sum a_i v_i`.

        INPUT:


        -  ``element`` - vector, list or tuple

        -  ``prec`` - desired precision of q-expansion


        EXAMPLES::

            sage: m = ModularForms(Gamma0(23),2); m
            Modular Forms space of dimension 3 for Congruence Subgroup Gamma0(23) of weight 2 over Rational Field
            sage: m.basis()
            [
            q - q^3 - q^4 + O(q^6),
            q^2 - 2*q^3 - q^4 + 2*q^5 + O(q^6),
            1 + 12/11*q + 36/11*q^2 + 48/11*q^3 + 84/11*q^4 + 72/11*q^5 + O(q^6)
            ]
            sage: m._q_expansion([1,2,0], 5)
            q + 2*q^2 - 5*q^3 - 3*q^4 + O(q^5)
        """
        B = self.q_expansion_basis(prec)
        f = self._q_expansion_zero()
        for i in range(len(element)):
            if element[i]:
                f += element[i] * B[i]
        return f


    ####################################################################
    # Computations of Dimensions
    ####################################################################
    def _dim_cuspidal(self):
        """
        Return the dimension of the cuspidal subspace of this ambient
        modular forms space, computed using a dimension formula.

        EXAMPLES::

            sage: m = ModularForms(GammaH(11,[2]), 2); m
            Modular Forms space of dimension 2 for Congruence Subgroup Gamma_H(11) with H generated by [2] of weight 2 over Rational Field
            sage: m._dim_cuspidal()
            1
        """
        try:
            return self.__the_dim_cuspidal
        except AttributeError:
            if arithgroup.is_Gamma1(self.group()) and self.character() is not None:
               self.__the_dim_cuspidal = self.group().dimension_cusp_forms(self.weight(), self.character())
            else:
               self.__the_dim_cuspidal = self.group().dimension_cusp_forms(self.weight())
        return self.__the_dim_cuspidal

    def _dim_eisenstein(self):
        """
        Return the dimension of the Eisenstein subspace of this modular
        symbols space, computed using a dimension formula.

        EXAMPLES::

            sage: m = ModularForms(GammaH(13,[2]), 2); m
            Modular Forms space of dimension 1 for Congruence Subgroup Gamma_H(13) with H generated by [2] of weight 2 over Rational Field
            sage: m._dim_eisenstein()
            1
        """
        try:
            return self.__the_dim_eisenstein
        except AttributeError:
            if self.weight() == 1:
                self.__the_dim_eisenstein = len(self.eisenstein_params())
            else:
                if arithgroup.is_Gamma1(self.group()) and self.character() is not None:
                    self.__the_dim_eisenstein = self.group().dimension_eis(self.weight(), self.character())
                else:
                    self.__the_dim_eisenstein = self.group().dimension_eis(self.weight())
        return self.__the_dim_eisenstein

    def _dim_new_cuspidal(self):
        """
        Return the dimension of the new cuspidal subspace, computed using
        dimension formulas.

        EXAMPLES::

            sage: m = ModularForms(GammaH(11,[2]), 2); m._dim_new_cuspidal()
            1
        """
        try:
            return self.__the_dim_new_cuspidal
        except AttributeError:
            if arithgroup.is_Gamma1(self.group()) and self.character() is not None:
                self.__the_dim_new_cuspidal = self.group().dimension_new_cusp_forms(self.weight(), self.character())
            else:
                self.__the_dim_new_cuspidal = self.group().dimension_new_cusp_forms(self.weight())
        return self.__the_dim_new_cuspidal

    def _dim_new_eisenstein(self):
        """
        Compute the dimension of the Eisenstein submodule.

        EXAMPLES::

            sage: m = ModularForms(Gamma0(11), 4)
            sage: m._dim_new_eisenstein()
            0
            sage: m = ModularForms(Gamma0(11), 2)
            sage: m._dim_new_eisenstein()
            1
        """
        try:
            return self.__the_dim_new_eisenstein
        except AttributeError:
            if arithgroup.is_Gamma0(self.group()) and self.weight() == 2:
                if rings.is_prime(self.level()):
                    d = 1
                else:
                    d = 0
            else:
                E = self.eisenstein_series()
                d = len([g for g in E if g.new_level() == self.level()])
            self.__the_dim_new_eisenstein = d
        return self.__the_dim_new_eisenstein


    ####################################################################
    # Computations of all Eisenstein series in self
    ####################################################################

    def eisenstein_params(self):
        """
        Return parameters that define all Eisenstein series in self.

        OUTPUT: an immutable Sequence

        EXAMPLES::

            sage: m = ModularForms(Gamma0(22), 2)
            sage: v = m.eisenstein_params(); v
            [(Dirichlet character modulo 22 of conductor 1 mapping 13 |--> 1, Dirichlet character modulo 22 of conductor 1 mapping 13 |--> 1, 2), (Dirichlet character modulo 22 of conductor 1 mapping 13 |--> 1, Dirichlet character modulo 22 of conductor 1 mapping 13 |--> 1, 11), (Dirichlet character modulo 22 of conductor 1 mapping 13 |--> 1, Dirichlet character modulo 22 of conductor 1 mapping 13 |--> 1, 22)]
            sage: type(v)
            <class 'sage.structure.sequence.Sequence_generic'>
        """
        try:
            return self.__eisenstein_params
        except AttributeError:
            eps = self.character()
            if eps == None:
                if arithgroup.is_Gamma1(self.group()):
                    eps = self.level()
                else:
                    raise NotImplementedError
            params = eis_series.compute_eisenstein_params(eps, self.weight())
            self.__eisenstein_params = Sequence(params, immutable=True)
        return self.__eisenstein_params

    def eisenstein_series(self):
        """
        Return all Eisenstein series associated to this space.

        ::

            sage: ModularForms(27,2).eisenstein_series()
            [
            q^3 + O(q^6),
            q - 3*q^2 + 7*q^4 - 6*q^5 + O(q^6),
            1/12 + q + 3*q^2 + q^3 + 7*q^4 + 6*q^5 + O(q^6),
            1/3 + q + 3*q^2 + 4*q^3 + 7*q^4 + 6*q^5 + O(q^6),
            13/12 + q + 3*q^2 + 4*q^3 + 7*q^4 + 6*q^5 + O(q^6)
            ]

        ::

            sage: ModularForms(Gamma1(5),3).eisenstein_series()
            [
            -1/5*zeta4 - 2/5 + q + (4*zeta4 + 1)*q^2 + (-9*zeta4 + 1)*q^3 + (4*zeta4 - 15)*q^4 + q^5 + O(q^6),
            q + (zeta4 + 4)*q^2 + (-zeta4 + 9)*q^3 + (4*zeta4 + 15)*q^4 + 25*q^5 + O(q^6),
            1/5*zeta4 - 2/5 + q + (-4*zeta4 + 1)*q^2 + (9*zeta4 + 1)*q^3 + (-4*zeta4 - 15)*q^4 + q^5 + O(q^6),
            q + (-zeta4 + 4)*q^2 + (zeta4 + 9)*q^3 + (-4*zeta4 + 15)*q^4 + 25*q^5 + O(q^6)
            ]

        ::

            sage: eps = DirichletGroup(13).0^2
            sage: ModularForms(eps,2).eisenstein_series()
            [
            -7/13*zeta6 - 11/13 + q + (2*zeta6 + 1)*q^2 + (-3*zeta6 + 1)*q^3 + (6*zeta6 - 3)*q^4 - 4*q^5 + O(q^6),
            q + (zeta6 + 2)*q^2 + (-zeta6 + 3)*q^3 + (3*zeta6 + 3)*q^4 + 4*q^5 + O(q^6)
            ]
        """
        return self.eisenstein_submodule().eisenstein_series()

    def _compute_q_expansion_basis(self, prec):
        """
        EXAMPLES::

            sage: m = ModularForms(11,4)
            sage: m._compute_q_expansion_basis(5)
            [q + 3*q^3 - 6*q^4 + O(q^5), q^2 - 4*q^3 + 2*q^4 + O(q^5), 1 + O(q^5), q + 9*q^2 + 28*q^3 + 73*q^4 + O(q^5)]
        """
        S = self.cuspidal_submodule()
        E = self.eisenstein_submodule()
        B_S = S._compute_q_expansion_basis(prec)
        B_E = E._compute_q_expansion_basis(prec)
        return B_S + B_E

    def _compute_hecke_matrix(self, n):
        """
        Compute the matrix of the Hecke operator T_n acting on self.

        NOTE:

        If self is a level 1 space, the much faster Victor Miller basis
        is used for this computation.

        EXAMPLES::

            sage: M = ModularForms(11, 2)
            sage: M._compute_hecke_matrix(6)
            [ 2  0]
            [ 0 12]

        TESTS:

        The following Hecke matrix is 43x43 with very large integer entries.
        We test it indirectly by computing the product and the sum of its
        eigenvalues, and reducing these two integers modulo all the primes
        less than 100::

            sage: M = ModularForms(1, 512)
            sage: t = M._compute_hecke_matrix(5)     # long time (2s)
            sage: f = t.charpoly()                   # long time (4s)
            sage: [f[0]%p for p in prime_range(100)] # long time (0s, depends on above)
            [0, 0, 0, 0, 1, 9, 2, 7, 0, 0, 0, 0, 1, 12, 9, 16, 37, 0, 21, 11, 70, 22, 0, 58, 76]
            sage: [f[42]%p for p in prime_range(100)] # long time (0s, depends on above)
            [0, 0, 4, 0, 10, 4, 4, 8, 12, 1, 23, 13, 10, 27, 20, 13, 16, 59, 53, 41, 11, 13, 12, 6, 82]
        """
        if self.level() == 1:
            k = self.weight()
            d = self.dimension()
            from sage.modular.all import victor_miller_basis, hecke_operator_on_basis
            vmb = victor_miller_basis(k, prec=d*n+1)
            return hecke_operator_on_basis(vmb, n, k)
        else:
            return space.ModularFormsSpace._compute_hecke_matrix(self, n)

    def _compute_hecke_matrix_prime_power(self, p, r):
        r"""
        Compute the Hecke matrix `T_{p^r}`, where `p` is prime and `r \ge 2`.

        This is an internal method.  End users are encouraged to use the
        method hecke_matrix() instead.

        TESTS:

            sage: M = ModularForms(1, 12)
            sage: M._compute_hecke_matrix_prime_power(5, 3)
            [  116415324211120654296876 11038396588040733750558720]
            [                         0              -359001100500]
            sage: delta_qexp(126)[125]
            -359001100500
            sage: eisenstein_series_qexp(12, 126)[125]
            116415324211120654296876
        """
        if self.level() == 1:
            return self._compute_hecke_matrix(p**r)
        else:
            return space.ModularFormsSpace._compute_hecke_matrix_prime_power(self, p, r)
