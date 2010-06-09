r"""
A subset of sage.categories.all with just the basic categories needed
for sage startup (i.e. to define ZZ, QQ, ...).
"""
#*****************************************************************************
#  Copyright (C) 2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from objects import Objects
from sets_cat import Sets, EmptySetError
from partially_ordered_sets import PartiallyOrderedSets
Posets = PartiallyOrderedSets
# For backward compatibility; will be deprecated at some point
OrderedSets = PartiallyOrderedSets

from additive_magmas import AdditiveMagmas
from commutative_additive_semigroups import CommutativeAdditiveSemigroups
from commutative_additive_monoids import CommutativeAdditiveMonoids
from commutative_additive_groups import CommutativeAdditiveGroups

from magmas import Magmas
from semigroups import Semigroups
from monoids import Monoids
from groups import Groups
from partially_ordered_monoids import PartiallyOrderedMonoids
# For backward compatibility; might be deprecated at some point
OrderedMonoids = PartiallyOrderedMonoids

# TODO: commutative and finite variants once the variants infrastructure will be implemented

from rngs import Rngs
from semirings import Semirings
from rings import Rings
from domains import Domains
from division_rings import DivisionRings

from commutative_rings import CommutativeRings
from integral_domains import IntegralDomains
from gcd_domains import GcdDomains
from principal_ideal_domains import PrincipalIdealDomains
from euclidean_domains import EuclideanDomains
from unique_factorization_domains import UniqueFactorizationDomains

from fields import Fields
