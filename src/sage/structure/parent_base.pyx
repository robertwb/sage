r"""
Base class for old-style parent objects with a base ring
"""
###############################################################################
#   Sage: System for Algebra and Geometry Experimentation
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

include "../ext/stdsage.pxi"

cimport parent

from coerce_exceptions import CoercionException

cdef inline check_old_coerce(parent.Parent p):
    if p._element_constructor is not None:
        raise RuntimeError, "%s still using old coercion framework" % p


# TODO: Unpickled parents with base sometimes have their base set to None.
# This causes a segfault in the module arithmetic architecture.
#
# sage: H = HomsetWithBase(QQ, RR, base=ZZ); H
# sage: H0 = loads(dumps(H))
# sage: H.base_ring(), H0.base_ring()
# (Integer Ring, None)
#
# Perhaps the code below would help (why was it commented out?).

## def make_parent_with_base_v0(_class, _dict, base, has_coerce_map_from):
##     """
##     This should work for any Python class deriving from this, as long
##     as it doesn't implement some screwy __new__() method.
##     """
##     new_object = _class.__new__(_class)
##     if base is None:
##         (<ParentWithBase>new_object)._base = new_object
##     else:
##         (<ParentWithBase>new_object)._base = base
##     (<ParentWithBase>new_object)._has_coerce_map_from = has_coerce_map_from
##     if not _dict is None:
##         new_object.__dict__ = _dict
##     return new_object

def is_ParentWithBase(x):
    """
    Return True if x is a parent object with base.
    """
    return bool(PY_TYPE_CHECK(x, ParentWithBase))

cdef class ParentWithBase(parent_old.Parent):
    """
    This class is being deprecated, see parent.Parent for the new model.
    """
    def __init__(self, base, coerce_from=[], actions=[], embeddings=[], category=None):
        # TODO: SymbolicExpressionRing has base RR, which makes this bad
#        print type(self), "base", base, coerce_from
#        if base != self and not base in coerce_from:
#            coerce_from.append(base)
        parent_old.Parent.__init__(self, coerce_from=coerce_from, actions=actions, embeddings=embeddings, category=category)
        self._base = base

    def _richcmp(left, right, int op):
        check_old_coerce(left)
        return (<parent_old.Parent>left)._richcmp(right, op) # the cdef method


    cdef _coerce_c_impl(self,x):
       check_old_coerce(self)
       if not self._base is self:
           return self._coerce_try(x,(self._base))
       else:
           raise TypeError, "No canonical coercion found."

##     def x__reduce__(self):
##         if HAS_DICTIONARY(self):
##             _dict = self.__dict__
##         else:
##             _dict = None
##         if self._base is self:
##             return (make_parent_with_base_v0, (self.__class__, _dict, None, self._has_coerce_map_from))
##         else:
##             return (make_parent_with_base_v0, (self.__class__, _dict, self._base, self._has_coerce_map_from))

    # Derived class *must* define base_extend.
    def base_extend(self, X):
        check_old_coerce(self)
        raise CoercionException, "BUG: the base_extend method must be defined for '%s' (class '%s')"%(
            self, type(self))

    ############################################################################
    # Homomorphism --
    ############################################################################
    def Hom(self, codomain, category = None):
        r"""
        self.Hom(codomain, category = None):

        Returns the homspace \code{Hom(self, codomain, category)} of all
        homomorphisms from self to codomain in the category cat.  The
        default category is \code{self.category()}.

        EXAMPLES:
            sage: R.<x,y> = PolynomialRing(QQ, 2)
            sage: R.Hom(QQ)
            Set of Homomorphisms from Multivariate Polynomial Ring in x, y over Rational Field to Rational Field

        Homspaces are defined for very general \sage objects, even elements of familiar rings.
            sage: n = 5; Hom(n,7)
            Set of Morphisms from 5 to 7 in Category of elements of Integer Ring
            sage: z=(2/3); Hom(z,8/1)
            Set of Morphisms from 2/3 to 8 in Category of elements of Rational Field

        This example illustrates the optional third argument:
            sage: QQ.Hom(ZZ, Sets())
            Set of Morphisms from Rational Field to Integer Ring in Category of sets
        """
        # NT 01-2009: what's the difference with parent.Parent.Hom???
        if self._element_constructor is None:
            return parent.Parent.Hom(self, codomain, category)
        try:
            return self._Hom_(codomain, category)
        except (AttributeError, TypeError):
            pass
        from sage.categories.all import Hom
        return Hom(self, codomain, category)
