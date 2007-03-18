from abvar             import ModularAbelianVariety
from sage.rings.all    import QQ
from sage.modular.dims import dimension_cusp_forms


class ModAbVar_ambient_jacobian(ModularAbelianVariety):
    def __init__(self, group):
        self._group = group
        ModularAbelianVariety.__init__(self, level = group.level(), base_ring = QQ)

    def _repr_(self):
        g = str(self._group)
        g = g.replace('Congruence','congruence').replace('Subgroup','subgroup')
        return "Jacobian of the modular curve associated to the %s"%g

    def group(self):
        return self._group

    def dimension(self):
        """
        Return the dimension of this modular abelian variety.

        EXAMPLES:
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

    def _integral_hecke_matrix(self, n, sign=0):
        """
        EXAMPLES:
            sage: J1(13)._integral_hecke_matrix(2)
            [-2  0 -1  1]
            [ 1 -1  0 -1]
            [ 1  1 -2  0]
            [ 0  1 -1 -1]
            sage: J1(13)._integral_hecke_matrix(2,sign=1)
            [-1  1]
            [-1 -2]
            sage: J1(13)._integral_hecke_matrix(2,sign=-1)
            [-2 -1]
            [ 1 -1]
        """
        return self.modular_symbols(sign).integral_hecke_matrix(n)

    def _rational_hecke_matrix(self, n, sign=0):
        return self.modular_symbols(sign).hecke_matrix(n)

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
