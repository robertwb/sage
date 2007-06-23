"""
Morphisms

AUTHORS:
    -- William Stein: initial version
    -- David Joyner (12-17-2005): added examples
    -- Robert Bradshaw (2007-06-25) Pyrexification
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

import operator

import homset

include "../ext/stdsage.pxi"
from sage.structure.element cimport Element

def is_Morphism(x):
    return isinstance(x, Morphism)

cdef class Morphism(Element):
    def __init__(Morphism self, parent):
        if not isinstance(parent, homset.Homset):
            raise TypeError, "parent (=%s) must be a Homspace"%parent
        Element.__init__(self, parent)
        self._domain = parent.domain()
        self._codomain = parent.codomain()

    def _repr_type(self):
        return "Generic"

    def _repr_defn(self):
        return ""

    def _repr_(self):
        if self.is_endomorphism():
            s = "%s endomorphism of %s"%(self._repr_type(), self.domain())
        else:
            s = "%s morphism:"%self._repr_type()
            s += "\n  From: %s"%self.domain()
            s += "\n  To:   %s"%self.codomain()
        d = self._repr_defn()
        if d != '':
            s += "\n  Defn: %s"%('\n        '.join(self._repr_defn().split('\n')))
        return s

    def domain(self):
        return self._domain

    def codomain(self):
        return self.parent().codomain()

    def category(self):
        return self.parent().category()

    def is_endomorphism(self):
        return self.parent().is_endomorphism_set()

    def __invert__(self):  # notation in python is (~f) for the inverse of f.
        raise NotImplementedError

    def __call__(self, x):
        if not PY_TYPE_CHECK(x, Element) or (<Element>x)._parent is not self._domain:
            try:
                x = self._domain(x)
            except TypeError:
                raise TypeError, "%s must be coercible into %s"%(x,self._domain)
        return self._call_(x)

    def _call_(self, x):
        return self._call_c(x)

    cdef Element _call_c(self, Element x):
        raise NotImplementedError

    def __mul__(self, right):
        r"""
        The multiplication * operator is operator composition.

        INPUT:
            self -- Morphism
            right -- Morphism

        OUTPUT:
            The morphism $x \mapsto self(right(x))$.
        """
        if not isinstance(right, Morphism):
            raise TypeError, "right (=%s) must be a morphism to multiply it by %s"%(right, self)
        if right.codomain() != self.domain():
            raise TypeError, "self (=%s) domain must equal right (=%s) codomain"%(self, right)
        H = homset.Hom(right.domain(), self.codomain(), self.parent().category())
        return self._composition_(right, H)

    def _composition_(self, right, homset):
        return FormalCompositeMorphism(homset, right, self)

    def __pow__(self, n, dummy):
        if not self.is_endomorphism():
            raise TypeError, "self must be an endomorphism."
        # todo -- what about the case n=0 -- need to specify the identity map somehow.
        import sage.rings.arith as arith
        return arith.generic_power(self, n)

cdef class FormalCoercionMorphism(Morphism):
    def __init__(self, parent):
        Morphism.__init__(self, parent)
        if not self.codomain().has_coerce_map_from(self.domain()):
            raise TypeError, "Natural coercion morphism from %s to %s not defined."%(self.domain(), self.codomain())

    def _repr_type(self):
        return "Coercion"

    cdef Element _call_c(self, Element x):
        if x._parent is not self._domain:
            x = x._domain._coerce_c(x)
        return self._codomain._coerce_c(x)

cdef class FormalCompositeMorphism(Morphism):
    def __init__(self, parent, first, second):
        Morphism.__init__(self, parent)
        self.__first = first
        self.__second = second

    cdef Element _call_c(self, Element x):
        return self.__second(self.__first(x))

    def _repr_type(self):
        return "Composite"

    def _repr_defn(self):
        return "  %s\nthen\n  %s"%(self.__first, self.__second)

    def first(self):
        """
        The first morphism in the formal composition, where the
        composition is x|--> second(first(x)).

        """
        return self.__first

    def second(self):
        """
        The second morphism in the formal composition, where the
        composition is x|--> second(first(x)).
        """
        return self.__second
