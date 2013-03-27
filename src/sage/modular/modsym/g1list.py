r"""
List of coset representatives for `\Gamma_1(N)` in `{\rm SL}_2(\ZZ)`
"""

#*****************************************************************************
#       Sage: System for Algebra and Geometry Experimentation
#
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

import sage.rings.arith as arith

class G1list:
    r"""
    A class representing a list of coset representatives for `\Gamma_1(N)` in
    `{\rm SL}_2(\ZZ)`. What we actually calculate is a list of elements of
    `(\ZZ/N\ZZ)^2` of exact order `N`.

    TESTS::

        sage: L = sage.modular.modsym.g1list.G1list(18)
        sage: loads(dumps(L)) == L
        True
    """
    def __init__(self, N):
        """
        EXAMPLE::

            sage: L = sage.modular.modsym.g1list.G1list(6); L # indirect doctest
            List of coset representatives for Gamma_1(6) in SL_2(Z)
        """
        self.__N = N
        self.__list = [(u,v) for u in xrange(N) for v in xrange(N) \
                             if arith.GCD(arith.GCD(u,v),N) == 1]

    def __cmp__(self, other):
        r"""
        Compare self to other.

        EXAMPLE::

            sage: L1 = sage.modular.modsym.g1list.G1list(6)
            sage: L2 = sage.modular.modsym.g1list.G1list(7)
            sage: L1 < L2
            True
            sage: L1 == QQ
            False
        """

        if not isinstance(other, G1list):
            return cmp(type(self), type(other))
        else:
            return cmp(self.__N, other.__N)

    def __getitem__(self, i):
        """
        EXAMPLE::

            sage: L = sage.modular.modsym.g1list.G1list(19); L[100] # indirect doctest
            (5, 6)
        """
        return self.__list[i]

    def __len__(self):
        """
        Return the length of the underlying list.

        EXAMPLE::

            sage: L = sage.modular.modsym.g1list.G1list(24); len(L) # indirect doctest
            384
        """
        return len(self.__list)

    def __repr__(self):
        """
        String representation of self.

        EXAMPLE::

            sage: L = sage.modular.modsym.g1list.G1list(3); L.__repr__()
            'List of coset representatives for Gamma_1(3) in SL_2(Z)'
        """
        return "List of coset representatives for Gamma_1(%s) in SL_2(Z)"%self.__N

    def list(self):
        r"""
        Return a list of vectors representing the cosets. Do not change the
        returned list!

        EXAMPLE::

            sage: L = sage.modular.modsym.g1list.G1list(4); L.list()
            [(0, 1), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
        """
        return self.__list

    def normalize(self, u, v):
        r"""
        Given a pair `(u,v)` of integers, return the unique pair `(u', v')`
        such that the pair `(u', v')` appears in ``self.list()`` and `(u, v)`
        is equivalent to `(u', v')`. This is rather trivial, but is here for
        consistency with the ``P1List`` class which is the equivalent for
        `\Gamma_0` (where the problem is rather harder).

        This will only make sense if `{\rm gcd}(u, v, N) = 1`; otherwise the
        output will not be an element of self.

        EXAMPLE::

            sage: L = sage.modular.modsym.g1list.G1list(4); L.normalize(6, 1)
            (2, 1)
            sage: L = sage.modular.modsym.g1list.G1list(4); L.normalize(6, 2) # nonsense!
            (2, 2)
        """
        return u % self.__N,   v % self.__N
