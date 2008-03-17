"""
TODO
"""


###########################################################################
#       Copyright (C) 2008 William Stein <wstein@gmail.com>               #
#  Distributed under the terms of the GNU General Public License (GPL)    #
#                  http://www.gnu.org/licenses/                           #
###########################################################################

from sage.databases.cremona import cremona_letter_code

from sage.rings.all  import QQ, ZZ

from sage.modular.modform.element import Newform
from sage.modular.congroup import is_Gamma0, is_Gamma1, is_GammaH

from abvar import ModularAbelianVariety_modsym_abstract
import homspace

class ModularAbelianVariety_newform(ModularAbelianVariety_modsym_abstract):
    """
    A modular abelian variety attached to a specific newform.
    """
    def __init__(self, f):
        """
        Create the modular abelian variety $A_f$ attached to the
        newform $f$.

        INPUT:
            f -- a newform

        EXAMPLES:
            sage: f = CuspForms(37).newforms('a')[0]
            sage: f.abelian_variety()
            Modular abelian variety attached to the newform q - 2*q^2 - 3*q^3 + 2*q^4 - 2*q^5 + O(q^6)
        """
        if not isinstance(f, Newform):
            raise TypeError, "f must be a newform"
        self.__f = f
        ModularAbelianVariety_modsym_abstract.__init__(self, QQ)

    def _modular_symbols(self):
        return self.__f.modular_symbols()

    def newform(self):
        """
        Return the newform that this modular abelian variety is attached to.

        EXAMPLES:
            sage: f = CuspForms(37).newforms('a')[0]
            sage: A = f.abelian_variety()
            sage: A.newform()
            q - 2*q^2 - 3*q^3 + 2*q^4 - 2*q^5 + O(q^6)
            sage: A.newform() is f
            True
        """
        return self.__f

    def label(self):
        """
        Return canonical label that defines this newform modular
        abelian variety.

        OUTPUT:
            string

        EXAMPLES:

        """
        G = self.__f.group()
        if is_Gamma0(G):
            group = ''
        elif is_Gamma1(G):
            group = 'G1'
        elif is_GammaH(G):
            group = 'GH[' + ','.join([str(z) for z in G._generators_for_H()]) + ']'
        return '%s%s%s'(self.level(), cremona_letter_code(self.factor_number()), group)

    def factor_number(self):
        """
        Return factor number.

        OUTPUT:
            int
        """
        try:
            return self.__factor_number
        except AttributeError:
            self.__factor_number = self.__f.number()
            return self.__factor_number

    def _repr_(self):
        """
        String representation of this modular abelian variety.

        EXAMPLES:
        """
        return "Modular abelian variety attached to the newform %s"%self.newform()

    def endomorphism_ring(self):
        """
        """
        try:
            return self.__endomorphism_ring
        except AttributeError:
            pass

        A = self.ambient_variety()
        M = self.modular_symbols()
        bound = M.sturm_bound()

        d = self.dimension()
        EndVecZ = ZZ**(4*d**2)
        T1 = M.hecke_matrix(1)
        V = EndVecZ.submodule([T1.list()])
        n = 2

        while V.dimension() < d:
            W = EndVecZ.submodule([((M.hecke_matrix(n))**i).list()
                                   for i in range(1,d+1)])
            V = V+W
            n += 1

        R = T1.parent()
        E = homspace.EndomorphismSubring(self)
        E._set_generators(V.saturation().basis())
        self.__endomorphism_ring = E

        return self.__endomorphism_ring
