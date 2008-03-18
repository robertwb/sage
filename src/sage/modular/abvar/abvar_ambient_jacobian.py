"""
Ambient Jacobian Abelian Variety

TESTS:
    sage: loads(dumps(J0(37))) == J0(37)
    True
    sage: loads(dumps(J1(13))) == J1(13)
    True
"""

import weakref

from abvar             import ModularAbelianVariety_modsym_abstract, ModularAbelianVariety
from sage.rings.all    import QQ
from sage.modular.dims import dimension_cusp_forms

from sage.modular.modsym.modsym import ModularSymbols
import morphism

_cache = {}

def ModAbVar_ambient_jacobian(group):
    """
    Return the ambient Jacobian attached to a given congruence
    subgroup.

    The result is cached using a weakref.  This function is called
    internally by modular abelian variety constructors.

    INPUT:
        group -- a congruence subgroup.

    OUTPUT:
        a modular abelian variety attached

    EXAMPLES:
        sage: import sage.modular.abvar.abvar_ambient_jacobian as abvar_ambient_jacobian
        sage: A = abvar_ambient_jacobian.ModAbVar_ambient_jacobian(Gamma0(11))
        sage: A
        Jacobian of the modular curve associated to the congruence subgroup Gamma0(11)
        sage: B = abvar_ambient_jacobian.ModAbVar_ambient_jacobian(Gamma0(11))
        sage: A is B
        True

    You can get access to and/or clear the cache as follows:
        sage: abvar_ambient_jacobian._cache = {}
        sage: B = abvar_ambient_jacobian.ModAbVar_ambient_jacobian(Gamma0(11))
        sage: A is B
        False
    """
    try:
        X = _cache[group]()
        if not X is None:
            return X
    except KeyError:
        pass
    X = ModAbVar_ambient_jacobian_class(group)
    _cache[group] = weakref.ref(X)
    return X

class ModAbVar_ambient_jacobian_class(ModularAbelianVariety_modsym_abstract):
    """
    An ambient Jacobian modular abelian variety attached to a
    congruence subgroup.
    """
    def __init__(self, group):
        """
        Create an ambient Jacobian modular abelian variety.

        EXAMPLES:
            sage: A = J0(37); A
            Jacobian of the modular curve associated to the congruence subgroup Gamma0(37)
            sage: type(A)
            <class 'sage.modular.abvar.abvar_ambient_jacobian.ModAbVar_ambient_jacobian_class'>
            sage: A.group()
            Congruence Subgroup Gamma0(37)
        """
        ModularAbelianVariety_modsym_abstract.__init__(self, QQ)
        self.__group = group
        self._is_hecke_stable = True

    def _modular_symbols(self):
        try:
            return self.__modsym
        except AttributeError:
            self.__modsym = ModularSymbols(self.__group, weight=2).cuspidal_submodule()
            return self.__modsym

    def _repr_(self):
        """
        Return string representation of this Jacobian modular abelian
        variety.

        EXAMPLES:
            sage: A = J0(11); A
            Jacobian of the modular curve associated to the congruence subgroup Gamma0(11)
            sage: A._repr_()
            'Jacobian of the modular curve associated to the congruence subgroup Gamma0(11)'
            sage: A.rename("J_0(11)")
            sage: A
            J_0(11)

        We now clear the cache to get rid of our renamed $J_0(11)$.
            sage: import sage.modular.abvar.abvar_ambient_jacobian as abvar_ambient_jacobian
            sage: abvar_ambient_jacobian._cache = {}
        """
        g = str(self.__group)
        g = g.replace('Congruence','congruence').replace('Subgroup','subgroup')
        return "Jacobian of the modular curve associated to the %s"%g

    def ambient_variety(self):
        """
        Return the ambient modular abelian variety that contains self.
        Since self is a Jacobian modular abelian variety, this is just
        self.

        EXAMPLES:
            sage: A = J0(11)
            sage: A.ambient_variety()
            Jacobian of the modular curve associated to the congruence subgroup Gamma0(11)
            sage: A is A.ambient_variety()
            True
        """
        return self

    def group(self):
        """
        Return the group that this Jacobian modular abelian variety
        is attached to.

        EXAMPLES:
            sage: J1(37).group()
            Congruence Subgroup Gamma1(37)
            sage: J0(5077).group()
            Congruence Subgroup Gamma0(5077)
            sage: J = GammaH(11,[3]).modular_abelian_variety(); J
            Jacobian of the modular curve associated to the congruence subgroup Gamma_H(11) with H generated by [3]
            sage: J.group()
            Congruence Subgroup Gamma_H(11) with H generated by [3]
        """
        return self.__group

    def groups(self):
        return (self.__group,)

    def degeneracy_map(self, level, t=1):
        """
        Return the t-th degeneracy map from self to J0(level).
        Here t must be a divisor of level/self.level().
        """
        if not self.level().divides(level):
            raise ValueError, "level must be divisible by level of self"
        if not t.divides(self.level().div(level)):
            raise ValueError, "t must divide the quotient of the two levels"

        Jdest = J0(level)
        Mself = self.modular_symbols()
        Mdest = Jdest.modular_symbols()

        symbol_map = Mself.degeneracy_map(level, t).restrict_codomain(Mdest)
        H = self.Hom(Jdest)

        return H(morphism.Morphism(H,symbol_map.matrix()))

    def dimension(self):
        """
        Return the dimension of this modular abelian variety.

        EXAMPLES:
            sage: J0(2007).dimension()
            221
            sage: J1(13).dimension()
            2
            sage: J1(997).dimension()
            40920
            sage: J0(389).dimension()
            32
            sage: JH(389,[4]).dimension()
            64
            sage: J1(389).dimension()
            6112
        """
        try:
            return self._dimension
        except AttributeError:
            d = dimension_cusp_forms(self.group(), k=2)
            self._dimension = d
            return d
