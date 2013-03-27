r"""
Division rings
"""
#*****************************************************************************
#  Copyright (C) 2008 Teresa Gomez-Diaz (CNRS) <Teresa.Gomez-Diaz@univ-mlv.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.category import Category
from sage.categories.category_singleton import Category_singleton
from sage.misc.cachefunc import cached_method

class DivisionRings(Category_singleton):
    """
    The category of division rings

    a division ring (or skew field) is a not necessarily commutative
    ring where all non-zero elements have multiplicative inverses

    EXAMPLES::

      sage: DivisionRings()
      Category of division rings
      sage: DivisionRings().super_categories()
      [Category of domains]

    TESTS::

        sage: TestSuite(DivisionRings()).run()
    """

    def super_categories(self):
        """
        EXAMPLES::

            sage: DivisionRings().super_categories()
            [Category of domains]
        """
        from sage.categories.domains import Domains
        return [Domains()]

    class ParentMethods:
        pass

    class ElementMethods:
        pass
