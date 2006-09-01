"""
The set of prime numbers
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

from sage.rings.all import Integer, ZZ, infinity

from set import Set_generic

cache = {}
class uniq(object):
    def __new__(cls):
        if cache.has_key(cls):
            return cache[cls]
        O = object.__new__(cls)
        cache[cls] = O
        return O

class Primes(uniq, Set_generic):
    """
    The set of prime numbers.

    EXAMPLES:
        sage: P = Primes(); P
        Set of all prime numbers: 2, 3, 5, 7, ...
        sage: loads(P.dumps()) == P
        True
    """
    def __init__(self):
        pass

    def order(self):
        return infinity

    def __cmp__(self, right):
        if isinstance(right, Primes):
            return 0
        return -1

    def __repr__(self):
        return "Set of all prime numbers: 2, 3, 5, 7, ..."

    def __iter__(self):
        p = Integer(2)
        while True:
            yield p
            p = p.next_prime()

    def __contains__(self, x):
        try:
            y = ZZ._coerce_(x)
            return y.is_prime()
        except TypeError:
            return False
