"""
Ambient Jacobian Abelian Variety

TESTS:
    sage: loads(dumps(J0(37))) == J0(37)
    True
    sage: loads(dumps(J1(13))) == J1(13)
    True
"""

import weakref

from abvar             import ModularAbelianVariety_modsym, ModularAbelianVariety
from sage.rings.all    import QQ
from sage.modular.dims import dimension_cusp_forms

_cache = {}

def ModAbVar_ambient_jacobian(group):
    """
    Return ambient Jacobian attached to a given congruence subgroup.

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

class ModAbVar_ambient_jacobian_class(ModularAbelianVariety_modsym):
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
            sage: A._group
            Congruence Subgroup Gamma0(37)
        """
        self._group = group
        ModularAbelianVariety_modsym.__init__(self, level = group.level(), base_field = QQ)

    def _repr_(self):
        """
        Return string representation of this Jacobian modular abelian variety.

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
        g = str(self._group)
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
        return self._group

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
            d = dimension_cusp_forms(self._group, k=2)
            self._dimension = d
            return d

    def modular_symbols(self, sign=0):
        """
        Return the space of modular symbols associated to this ambient
        modular symbols space.

        EXAMPLES:
            sage: J0(11).modular_symbols()
            Modular Symbols subspace of dimension 2 of Modular Symbols space of dimension 3 for Gamma_0(11) of weight 2 with sign 0 over Rational Field
            sage: J0(11).modular_symbols(sign=1)
            Modular Symbols subspace of dimension 1 of Modular Symbols space of dimension 2 for Gamma_0(11) of weight 2 with sign 1 over Rational Field
            sage: J0(11).modular_symbols(sign=0)
            Modular Symbols subspace of dimension 2 of Modular Symbols space of dimension 3 for Gamma_0(11) of weight 2 with sign 0 over Rational Field
            sage: J0(11).modular_symbols(sign=-1)
            Modular Symbols subspace of dimension 1 of Modular Symbols space of dimension 1 for Gamma_0(11) of weight 2 with sign -1 over Rational Field
        """
        try:
            return self._modular_symbols[sign]
        except AttributeError:
            self._modular_symbols = {}
        except KeyError:
            pass
        M = self._group.modular_symbols(sign=sign, weight=2, base_ring=QQ)
        S = M.cuspidal_submodule()
        self._modular_symbols[sign] = S
        return S

    def is_subvariety(self, other):
        """
        Return True if self is a subvariety of other, as they sit in an ambient
        modular abelian variety.

        EXAMPLES:
            sage: J = J0(37)
            sage: J.is_subvariety(J)
            True
            sage: J.is_subvariety(25)
            False
        """
        if not isinstance(other, ModularAbelianVariety):
            return False
        A = other.ambient_variety()
        if self == A:
            return True
        raise NotImplementedError, "general is_subvariety not yet implemented."
