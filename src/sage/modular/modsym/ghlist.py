r"""
List of coset represenatives for $\Gamma_H(N)$ in $\SL_2(\ZZ)$.
"""

#####################################################################################
#       SAGE: System for Algebra and Geometry Experimentation
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
#####################################################################################


import sage.rings.arith as arith

class GHlist:
    def __init__(self, group):
        self.__group = group
        N = group.level()
        v = [group._reduce_coset(u,v) for u in xrange(N) for v in xrange(N) \
                if arith.GCD(arith.GCD(u,v),N) == 1]
        v = list(set(v))
        v.sort()
        self.__list = v

    def __getitem__(self, i):
        return self.__list[i]

    def __len__(self):
        return len(self.__list)

    def __repr__(self):
        return "List of coset representatives for %s"%self.__group

    def list(self):
        return self.__list

    def normalize(self, u, v):
        return self.__group._reduce_coset(u,v)
