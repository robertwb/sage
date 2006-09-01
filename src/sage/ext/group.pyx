"""
Base class for all groups
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

doc="""
Base class for all groups
"""

import random
import sage.rings.coerce
from sage.rings.infinity import infinity

cdef class Group(gens.Generators):
    """
    Generic group class
    """
    def __init__(self):
        pass

    def __call__(self, x):
        """
        Coerce x into this group.
        """
        raise NotImplementedError

    def _coerce_(self, x):
        return self(x)

    def __contains__(self, x):
        r"""
        True if coercion of $x$ into self is defined.
        """
        try:
            self(x)
        except TypeError:
            return False
        return True

    def category(self):
        """
        The category of all groups
        """
        import sage.categories.all
        return sage.categories.all.Groups()

    def is_atomic_repr(self):
        """
        True if the elements of this group have atomic string
        representations.  For example, integers are atomic but
        polynomials are not.
        """
        return False

    def is_abelian(self):
        """
        Return True if this group is abelian.
        """
        raise NotImplementedError

    def order(self):
        """
        Returns the number of elements of this group, which is either
        a positive integer or infinity.
        """
        raise NotImplementedError

    def is_finite(self):
        """
        Returns True if this group is finite.
        """
        return bool(self.order() != infinity)

    def __hash__(self):
        return hash(self.__repr__())

    def random_element(self, bound=None):
        """
        Return a random element of this group.
        """
        raise NotImplementedError

    def quotient(self, H):
        """
        Return the quotient of this group by the normal subgroup $H$.
        """
        raise NotImplementedError

cdef class AbelianGroup(Group):
    """
    Generic abelian group.
    """
    def is_abelian(self):
        """
        Return True.
        """
        return True


cdef class FiniteGroup(Group):
    """
    Generic finite group.
    """
    def is_finite(self):
        """
        Return True.
        """
        return True

cdef class AlgebraicGroup(Group):
    """
    Generic algebraic group.
    """
