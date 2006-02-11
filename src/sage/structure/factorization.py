r"""
Factorizations

AUTHORS:
    -- William Stein (2006-01-22): added unit part as suggested by D Kohel.

EXAMPLES:

This example illustrates that the unit part is not discarded from
factorizations.
    sage: x = QQ['x'].0
    sage: f = -5*(x-2)*(x-3)
    sage: f
    -5*x^2 + 25*x - 30
    sage: F = f.factor(); F
    (-5) * (x - 3) * (x - 2)
    sage: F.unit()
    -5
    sage: list(F)
    [(x - 3, 1), (x - 2, 1)]
    sage: mul(F)            # or F.mul() or F.prod()
    -5*x^2 + 25*x - 30
    sage: len(F)
    2

In the ring $\Z[x]$, the integer $-5$ is not a unit, so the
factorization has three factors:

    sage: x = ZZ['x'].0
    sage: f = -5*(x-2)*(x-3)
    sage: f
    -5*x^2 + 25*x - 30
    sage: F = f.factor(); F
    (-5) * (x - 3) * (x - 2)
    sage: F.unit()
    1
    sage: list(F)
    [(-5, 1), (x - 3, 1), (x - 2, 1)]
    sage: mul(F)            # or F.mul() or F.prod()
    -5*x^2 + 25*x - 30
    sage: len(F)
    3

On the other hand, -1 is a unit in $\Z$, so it is included in the unit.
    sage: x = ZZ['x'].0
    sage: f = -1*(x-2)*(x-3)
    sage: F = f.factor(); F
    (-1) * (x - 3) * (x - 2)
    sage: F.unit()
    -1
    sage: list(F)
    [(x - 3, 1), (x - 2, 1)]
"""

#*****************************************************************************
#
#   SAGE: System for Algebra and Geometry Experimentation
#
#       Copyright (C) 2005 William Stein <wstein@ucsd.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import sage.misc.latex as latex
from sage.ext.sage_object import SageObject

class Factorization(SageObject, list):
    """
    EXAMPLES:
        sage: N = 2006
        sage: F = N.factor(); F
        2 * 17 * 59
        sage: F.unit()
        1
        sage: F = factor(-2006); F
        -1 * 2 * 17 * 59
        sage: F.unit()
        -1
        sage: loads(F.dumps()) == F
        True


    """
    def __init__(self, x, unit=None):
        if not isinstance(x, list):
            raise TypeError, "x must be a list"
        if isinstance(x, Factorization):
            if unit is None:
                unit = x.__unit
            else:
                unit = x.__unit * unit
        from sage.rings.integer import Integer
        for t in x:
            if not (isinstance(t, tuple) and len(t) == 2 and isinstance(t[1],(int, long, Integer))):
                raise TypeError, "x must be a list of tuples of length 2"
        if unit is None:
            if len(x) > 0:
                try:
                    unit = x[0][0].parent()(1)
                except AttributeError:
                    unit = Integer(1)
            else:
                unit = Integer(1)
        list.__init__(self, x)
        self.__unit = unit
        self.sort()

    def __reduce__(self):
        x = list(self)
        return Factorization, (x,)

    def unit(self):
        """
        Return the unit part of this factorization.

        EXAMPLES:
            sage: F = factor(-2006); F
            -1 * 2 * 17 * 59
            sage: F.unit()
            -1
        """
        return self.__unit

    def unit_part(self):
        r"""
        Same as \code{self.unit()}.
        """
        return self.__unit

    def _repr_(self):
        if len(self) == 0:
            return str(self.__unit)
        try:
            atomic = ((isinstance(self[0][0], (int, long)) or \
                       self[0][0].parent().is_atomic_repr()))
        except AttributeError:
            atomic = False
        s = ''
        for i in range(len(self)):
            t = str(self[i][0])
            if not atomic  and (t.find('+') != -1 or t.find('-') != -1):
                t = '(%s)'%t
            n = self[i][1]
            if n != 1:
                t += '^%s'%n
            s += t
            if i < len(self)-1:
                s += ' * '
        if self.__unit != 1:
            if atomic:
                u = str(self.__unit)
            else:
                u = '(%s)'%self.__unit
            s =  u + ' * ' + s
        return s

    def _latex_(self):
        if len(self) == 0:
            return latex.latex(self.__unit)
        try:
            atomic = ((isinstance(self[0][0], (int, long)) or \
                       self[0][0].parent().is_atomic_repr()))
        except AttributeError:
            atomic = False
        s = ''
        for i in range(len(self)):
            t = latex.latex(self[i][0])
            if not atomic and (t.find('+') != -1 or t.find('-') != -1):
                t = '(%s)'%t
            n = self[i][1]
            if n != 1:
                t += '^{%s}'%latex.latex(n)
            s += t
            if i < len(self)-1:
                s += ' \\cdot '
        if self.__unit != 1:
            if atomic:
                u = latex.latex(self.__unit)
            else:
                u = '(%s)'%latex.latex(self.__unit)
            s =  u + ' * ' + s
        return s

    def __add__(self, other):
        raise NotImplementedError

    def __mul__(self, other):
        """
        Return the product of two factorizations.
        """
        if not isinstance(other, Factorization):
            return self.mul() * other
        d1 = dict(self)
        d2 = dict(other)
        s = {}
        for a in set(d1.keys()).union(set(d2.keys())):
            s[a] = 0
            if d1.has_key(a):
                s[a] += d1[a]
            if d2.has_key(a):
                s[a] += d2[a]
        return Factorization(list(s.iteritems()))

    def mul(self):
        """
        Return the product of the factors in the factorization, multiplied out.

        EXAMPLES:
            sage: F = factor(2006); F
            2 * 17 * 59
            sage: F.mul()
            2006
        """
        x = self.__unit
        for f, e in self:
            x *= (f**e)
        return x

    def prod(self):
        r"""
        Same as \code{self.mul()}.
        """
        return self.mul()


def Factorization_deduce_unit(x, mul):
    F = Factorization(x)
    z = F.mul()
    u = mul/z
    F._Factorization__unit = u
    return F
