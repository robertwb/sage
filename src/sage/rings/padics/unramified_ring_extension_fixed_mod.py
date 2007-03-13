from sage.rings.padics.padic_ring_generic import pAdicRingGeneric
from sage.rings.padics.padic_ring_generic import pAdicRingBaseGeneric
from sage.rings.polynomial_quotient_ring import *
from sage.rings.integer import Integer
from sage.rings.finite_field import GF
from sage.rings.polynomial_ring import PolynomialRing
from sage.rings.padics.unramified_ring_extension_element import UnramifiedRingExtensionElement
import sage.rings.polynomial_quotient_ring_element
import sage.rings.padics.padic_ring_generic
import sage.rings.polynomial_element
import sage.rings.padics.unramified_extension_generic
import sage.rings.padics.padic_ring_extension_generic
import sage.rings.padics.padic_ring_fixed_mod
import sage.rings.padics.unramified_ring_extension_element
import sage.rings.infinity

infinity = sage.rings.infinity.infinity
Polynomial = sage.rings.polynomial_element.Polynomial
pAdicRingFixedMod = sage.rings.padics.padic_ring_fixed_mod.pAdicRingFixedMod
pAdicRingBaseGeneric = sage.rings.padics.padic_ring_generic.pAdicRingBaseGeneric
PQRElement = sage.rings.polynomial_quotient_ring_element.PolynomialQuotientRingElement
UnramifiedExtensionGeneric = sage.rings.padics.unramified_extension_generic.UnramifiedExtensionGeneric
pAdicRingExtensionGeneric = sage.rings.padics.padic_ring_extension_generic.pAdicRingExtensionGeneric
UnramifiedExtensionElement = sage.rings.padics.unramified_extension_element.UnramifiedExtensionElement

class UnramifiedRingExtensionFixedMod(UnramifiedExtensionGeneric, pAdicRingExtensionGeneric):
    r"""
    Unramified Extension of a p-adic ring with fixed modulus

    You should not create this class directly unless you know what you're doing.  Use ExtensionFactory.
    """

    def __init__(self, base, poly, names, prec, halt, print_mode):
        UnramifiedExtensionGeneric.__init__(self, poly, names, prec, print_mode)

    def __call__(self, x, absprec = infinity, relprec = infinity):
        return UnramifiedExtensionElement(self, x, absprec, relprec)

    def gen(self, n = 0):
        if n == 0:
            try:
                return self._gen
            except AttributeError:
                self._gen = UnramifiedExtensionElement(self, self.polynomial_ring().gen(), check = False, construct = True)
                return self._gen

    def fraction_field(self):
        r"""
        Would return the fraction field, but this operation is not allowed for fixed-mod rings.
        """
        raise TypeError, "cannot take fraction field of a fixed-mod ring"
