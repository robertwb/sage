"""
Elements of p-Adic Rings

AUTHOR:
    -- David Roe
    -- Genya Zaytman: documentation
    -- David Harvey: doctests
"""

#*****************************************************************************
#       Copyright (C) 2007 David Roe <roed@math.harvard.edu>
#                          William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

#import sage.rings.padics.precision_error
import sage.rings.padics.padic_generic_element
#import sage.rings.padics.padic_ring_generic

Integer = sage.rings.integer.Integer
PrecisionError = sage.rings.padics.precision_error.PrecisionError
pAdicGenericElement = sage.rings.padics.padic_generic_element.pAdicGenericElement
infinity = sage.rings.infinity.infinity
#Zp = sage.rings.padics.padic_ring_generic.Zp

class pAdicRingGenericElement(pAdicGenericElement):
    def __getitem__(self, n):
        r"""
        Returns the coefficient of $p^n$ in the series expansion of self, as an integer in the range $0$ to $p-1$.

        EXAMPLE:
            sage: R = Zp(7,4,'capped-rel','series'); a = R(1/3); a
            5 + 4*7 + 4*7^2 + 4*7^3 + O(7^4)
            sage: a[0]
            5
            sage: a[1]
            4
        """
        if n >= self.precision_absolute():
            raise PrecisionError, "element not known to enough precision."
        elif n < self.valuation():
            return 0
        else:
            return self.list()[n]

    def __invert__(self, prec=infinity):
        r"""
        Returns the multiplicative inverse of self.

        EXAMPLE:
            sage: R = Zp(7,4,'capped-rel','series'); a = R(3); a
            3 + O(7^4)
            sage: ~a
            5 + 4*7 + 4*7^2 + 4*7^3 + O(7^4)

        NOTES:
        The element returned is an element of the fraction field.
        """
        return self.parent().fraction_field()(self).__invert__()

    def __floordiv__(self, right):
        if isinstance(right, Integer):
            right = self.parent()(right)
        return self.parent()(self / right.unit_part()).__rshift__(right.valuation())

    def __mod__(self, right):
        return self - right * self.__floordiv__(right)

    def _integer_(self):
        return self.lift()


    def padded_list(self, absprec = infinity, relprec = infinity):
        """
        Returns a list of coeficiants of p starting with $p^0$ up to $p^n$ exclusive (padded with zeros if needed), where n is the minimum of absprec and relprec + self.valuation()

        INPUT:
            self -- a p-adic element
            absprec -- an integer
            relprec -- an integer
        OUTPUT:
            list -- the list of coeficients of self
        EXAMPLES:
            sage: R = Zp(7,4,'fixed-mod'); a = R(2*7+7**2); a.padded_list(5)
            [0, 2, 1, 0, 0]

        NOTE:
            this differs from the padded_list method of padic_field_element
        """
        if absprec is infinity and relprec is infinity:
            raise ValueError, "must specify at least one of absprec and relprec"
        if self.valuation() is infinity:
            if absprec < infinity:
                return [self.parent().residue_class_field()(0)]*absprec
            else:
                raise ValueError, "would return infinite list"
        absprec = min(absprec, relprec + self.valuation())
        retlist = self.list()
        return retlist[:absprec] + [self.parent().residue_class_field()(0)]*(absprec - len(retlist))


    def residue(self, prec):
        raise NotImplementedError
