"""
Algebras
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

from quatalg.all import *

# Algebra base classes
from algebra import Algebra, is_Algebra

# Ring element base classes
from algebra_element import AlgebraElement, is_AlgebraElement


from free_algebra import FreeAlgebra, is_FreeAlgebra
from free_algebra_quotient import FreeAlgebraQuotient

from steenrod_algebra import SteenrodAlgebra
from steenrod_algebra_element import Sq
from steenrod_algebra_bases import steenrod_algebra_basis

from group_algebra import GroupAlgebra, GroupAlgebraElement

from iwahori_hecke_algebra import IwahoriHeckeAlgebraT
from affine_nil_temperley_lieb import AffineNilTemperleyLiebTypeA

def is_R_algebra(Q, R):
    # TODO: do something nontrivial when morphisms are defined.
    return True
