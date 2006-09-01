"""
Abstract base class for modules
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
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

import random

cdef class Module(gens.AdditiveAbelianGenerators):
    """
    Generic module class.
    """
    def __init__(self):
        pass

    def __call__(self, x):
        """
        Coerce x into the ring.
        """
        raise NotImplementedError

    def _coerce_(self, x):
        return self(x)

    def base_ring(self):
        """
        Return the base ring of this module.
        """
        raise NotImplementedError

    def category(self):
        """
        Return the category to which this module belongs.
        """
        import sage.categories.all
        return sage.categories.all.Modules(self.base_ring())

    def endomorphism_ring(self):
        """
        Return the endomorphism ring of this module in its category.
        """
        try:
            return self.__endomorphism_ring
        except AttributeError:
            import sage.categories.all
            E = sage.categories.all.End(self)
            self.__endomorphism_ring = E
            return E


    def is_atomic_repr(self):
        """
        True if the elements have atomic string representations, in the sense
        that they print if they print at s, then -s means the negative of s.
        For example, integers are atomic but polynomials are not.
        """
        return False

    def __hash__(self):
        return hash(self.__repr__())
