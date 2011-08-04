from sage import all
from sage.rings.polynomial.pbori import *
import weakref
class OrderCode:
    pass

OrderCode.__dict__ = order_dict

def Ring(n, order='lp', names=[], blocks=[]):


    allnames = names + ['x' + str(i) for i in xrange(len(names), n)]
    order = TermOrder_from_pb_order(n, order, blocks)
    return BooleanPolynomialRing(n, names=allnames, order=order)

BoolePolynomialVector = BooleanPolynomialVector

_gauss_on_polys=gauss_on_polys
def gauss_on_polys(l):
    vec=BoolePolynomialVector(l)
    return list(_gauss_on_polys(vec))

_add_up_polynomials=add_up_polynomials
def add_up_polynomials(polys, init):
    """
    Adds up the polynomials in polys (which should be a BoolePolynomialVector or a sequence of ???
    """
    if not isinstance(polys, BoolePolynomialVector):
        vec = BoolePolynomialVector
        for p in polys:
            vec.append(p)
        polys=vec

    return _add_up_polynomials(polys, init)

#todo: PolyBoRi's original interface uses its WeakRingPtr here
def WeakRingRef(ring):
    return weakref.weakref(ring)

Monomial = MonomialFactory()
Polynomial = PolynomialFactory()
Variable = VariableFactory()
