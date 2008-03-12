#*****************************************************************************
#       Copyright (C) 2007 Mike Hansen <mhansen@gmail.com>,
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

import cartan_type
from sage.combinat.combinatorial_algebra import CombinatorialAlgebra
from sage.modules.free_module import FreeModule
from sage.rings.all import ZZ
from sage.misc.misc import prod


def RootSystem(t):
    """
    EXAMPLES:
        sage: RootSystem(['A',3])
        Root system of type ['A', 3]
    """
    ct = cartan_type.CartanType(t)
    if not ct.affine:
        type = ct.type()
        if type == "A":
            return RootSystem_a(ct)
        elif type == "B":
            return RootSystem_b(ct)
        elif type == "C":
            return RootSystem_c(ct)
        elif type == "D":
            return RootSystem_d(ct)
        elif type == "G":
            return RootSystem_g(ct)
    else:
        return RootSystem_generic(ct)

class RootSystem_generic:
    def __init__(self, ct):
        """
        TESTS:
            sage: R = RootSystem(['A',3])
            sage: loads(dumps(R))
            Root system of type ['A', 3]
        """
        self.ct = ct

    def __repr__(self):
        """
        EXAMPLES:
            sage: RootSystem(['A',3])
            Root system of type ['A', 3]
        """
        return "Root system of type %s"%self.ct

    def cartan_type(self):
        """
        Returns the Cartan type of the root system.

        EXAMPLES:
            sage: R = RootSystem(['A',3])
            sage: R.cartan_type()
            ['A', 3]
        """
        return self.ct

    def cartan_matrix(self):
        """
        EXAMPLES:
            sage: RootSystem(['A',3]).cartan_matrix()
            [ 2 -1  0]
            [-1  2 -1]
            [ 0 -1  2]
        """
        return self.cartan_type().cartan_matrix()

    def index_set(self):
        """
        EXAMPLES:
            sage: RootSystem(['A',3]).index_set()
            [1, 2, 3]
        """
        return self.cartan_type().index_set()

    def ambient_lattice(self):
        raise NotImplementedError

    def coroot_lattice(self):
        raise NotImplementedError

    def root_lattice(self):
        raise NotImplementedError

    def weight_lattice(self):
        raise NotImplementedError

    def dual_weight_lattice(self):
        return self.coroot_lattice()

    def ambient_lattice(self):
        raise NotImplementedError

class RootSystem_a(RootSystem_generic):
    def ambient_lattice(self):
        return AmbientLattice_a(self.ct)

class RootSystem_b(RootSystem_generic):
    def ambient_lattice(self):
        return AmbientLattice_b(self.ct)

class RootSystem_c(RootSystem_generic):
    def ambient_lattice(self):
        return AmbientLattice_c(self.ct)

class RootSystem_d(RootSystem_generic):
    def ambient_lattice(self):
        return AmbientLattice_d(self.ct)

class RootSystem_g(RootSystem_generic):
    def ambient_lattice(self):
        return AmbientLattice_g(self.ct)




class RootSystem_affine(RootSystem_generic):
    def weight_lattice(self):
        return affine_weight_lattice(self)

    def dual_weight_lattice(self):
        raise NotImplementedError



class CorootLattice_generic(CombinatorialAlgebra):
    def __init__(self, ct):
        self.ct = ct
        self._prefix = "alphacheck"
        self._combinatorial_class = None


    def cartan_type(self):
        return self.ct




class RootSystemRealization_generic:
    """

    """
    ## Realization of a root system (that is of the
    ## (positive/negative/simple) roots inside some space, not necessarily
    ## with any particular structure


class WeightLatticeRealization_class:

    # Should this be a method or an attribute?
    # same question for the roots, ...
    def rho(self):
        return sum(self.fundamental_weights())

    # Should it be a method of highest_weight?
    def weyl_dimension(self, highest_weight):
        # Should assert(highest_weight.is_dominant())
        rho = self.rho()
        n = prod([(rho+highest_weight).dot_product(x) for x in self.positive_roots()])
        d = prod([ rho                .dot_product(x) for x in self.positive_roots()])
        return n/d

class AmbientLattice_generic(WeightLatticeRealization_class):
    def __init__(self, ct):
        if not hasattr(self, 'n'):
            self.n  = ct.rank()
        self.ct = ct
        self._free_module = FreeModule(ZZ, self.n)

    #def __call__(self, i):
    #    return self._term(i+1)

    def __repr__(self):
        """
        EXAMPLES:
            sage: RootSystem(['B',4]).ambient_lattice()
            Ambient lattice of the root system of type ['B', 4]

        """
        return "Ambient lattice of the root system of type %s"%self.ct

    def __getitem__(self,i):
        return self._term(i-1)

    def roots(self):
        return self.positive_roots() + self.negative_roots()

    def _term(self, i):
        return self._free_module.gen(i)

    def fundamental_weights(self):
        return self._fundamental_weights_from_simple_roots()

    def _fundamental_weights_from_simple_roots(self):
        raise NotImplementedError

    def positive_roots(self):
        raise NotImplementedError

    def negative_roots(self):
        raise NotImplementedError

class AmbientLattice_a(AmbientLattice_generic):
    def __init__(self, ct):
        self.n  = ct.rank()+1
        AmbientLattice_generic.__init__(self, ct)

    def root(self, i, j):
        return self._term(i) - self._term(j)

    def simple_roots(self):
        """
        EXAMPLES:
            sage: e = CartanType(['A',3]).root_system().ambient_lattice()
            sage: e.simple_roots()
            [(1, -1, 0, 0), (0, 1, -1, 0), (0, 0, 1, -1)]
        """
        return [ self.root(i, i+1) for i in range(self.n-1) ]

    def negative_roots(self):
        """
        EXAMPLES:
            sage: e = CartanType(['A',3]).root_system().ambient_lattice()
            sage: e.negative_roots()
            [(-1, 1, 0, 0),
             (-1, 0, 1, 0),
             (-1, 0, 0, 1),
             (0, -1, 1, 0),
             (0, -1, 0, 1),
             (0, 0, -1, 1)]
        """
        res = []
        for j in range(self.n-1):
            for i in range(j+1,self.n):
                res.append(  self.root(i,j) )
        return res

    def positive_roots(self):
        """
        EXAMPLES:
            sage: e = CartanType(['A',3]).root_system().ambient_lattice()
            sage: e.positive_roots()
            [(1, -1, 0, 0),
             (1, 0, -1, 0),
             (0, 1, -1, 0),
             (1, 0, 0, -1),
             (0, 1, 0, -1),
             (0, 0, 1, -1)]

        """
        res = []
        for j in range(self.n):
            for i in range(j):
                res.append(  self.root(i,j) )
        return res

    def fundamental_weights(self):
        """
        EXAMPLES:
            sage: e = CartanType(['A',3]).root_system().ambient_lattice()
            sage: e.fundamental_weights()
            [(1, 0, 0, 0), (1, 1, 0, 0), (1, 1, 1, 0)]

        """
        return [ sum([self._term(j) for j in range(i+1)]) for i in range(self.n-1)]

class AmbientLattice_b(AmbientLattice_generic):
    def root(self, i, j):
        return self._term(i) - self._term(j)
    def simple_roots(self):
        """
        EXAMPLES:
            sage: e =  RootSystem(['B',4]).ambient_lattice()
            sage: e.simple_roots()
            [(1, -1, 0, 0), (0, 1, -1, 0), (0, 0, 1, -1), (0, 0, 0, 1)]
            sage: e.positive_roots()
            [(1, -1, 0, 0),
            (1, 1, 0, 0),
            (1, 0, -1, 0),
            (1, 0, 1, 0),
            (1, 0, 0, -1),
            (1, 0, 0, 1),
            (0, 1, -1, 0),
            (0, 1, 1, 0),
            (0, 1, 0, -1),
            (0, 1, 0, 1),
            (0, 0, 1, -1),
            (0, 0, 1, 1),
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1)]
            sage: e.fundamental_weights()
            [(1, 0, 0, 0), (1, 1, 0, 0), (1, 1, 1, 0), (1/2, 1/2, 1/2, 1/2)]
        """
        return [ self.root(i,i+1) for i in range(self.n-1) ] + [ self._term(self.n-1) ]
    def negative_roots(self):
        return [ -a for a in self.positive_roots()]
    def positive_roots(self):
        res = []
        for i in range(self.n-1):
            for j in range(i+1,self.n):
                res.append(self._term(i) - self._term(j))
                res.append(self._term(i) + self._term(j))
        for i in range(self.n):
            res.append(self._term(i))
        return res

    def fundamental_weights(self):
        return [ sum(self._term(j) for j in range(i+1)) for i in range(self.n-1)]\
               + [ sum( self._term(j) for j in range(self.n) ) / 2 ]


class AmbientLattice_c(AmbientLattice_generic):
    def root(self, i, j, p1, p2):
        return (-1)**p1 * self._term(i) + (-1)**p2 * self._term(j)

    def simple_roots(self):
        """
        EXAMPLES:
            sage: RootSystem(['C',3]).ambient_lattice().simple_roots()
            [(1, -1, 0), (0, 1, -1), (0, 0, 2)]

        """
        return [ self.root(i, i+1,0,1) for i in range(self.n-1) ] + [self.root(self.n-1, self.n-1, 0, 0)]

    def positive_roots(self):
        """
        EXAMPLES:
            sage: RootSystem(['C',3]).ambient_lattice().positive_roots()
            [(1, 1, 0),
             (1, 0, 1),
             (0, 1, 1),
             (1, -1, 0),
             (1, 0, -1),
             (0, 1, -1),
             (2, 0, 0),
             (0, 2, 0),
             (0, 0, 2)]
        """
        res = []
        for p in [0,1]:
            for j in range(self.n):
                res.extend([self.root(i,j,0,p) for i in range(j)])
        res.extend([self.root(i,i,0,0) for i in range(self.n)])
        return res
    def negative_roots(self):
        """
        EXAMPLES:
            sage: RootSystem(['C',3]).ambient_lattice().negative_roots()
            [(-1, 1, 0),
             (-1, 0, 1),
             (0, -1, 1),
             (-1, -1, 0),
             (-1, 0, -1),
             (0, -1, -1),
             (-2, 0, 0),
             (0, -2, 0),
             (0, 0, -2)]
        """
        res = []
        for p in [0,1]:
            for j in range(self.n):
                res.extend( [self.root(i,j,1,p) for i in range(j) ] )
        res.extend( [ self.root(i,i,1,1) for i in range(self.n) ] )
        return res


    def fundamental_weights(self):
        """
        EXAMPLES:
            sage: RootSystem(['C',3]).ambient_lattice().fundamental_weights()
            [(1, 0, 0), (1, 1, 0), (1, 1, 1)]
        """
        return [ sum(self._term(j) for j in range(i+1)) for i in range(self.n)]


class AmbientLattice_d(AmbientLattice_generic):
    def root(self, i, j, p1, p2):
        if i != j:
            return (-1)**p1 * self._term(i) + (-1)**p2 * self._term(j)
        else:
            return (-1)**p1 * self._term(i)

    def simple_roots(self):
        """
        EXAMPLES:
            sage: RootSystem(['D',4]).ambient_lattice().simple_roots()
            [(1, -1, 0, 0), (0, 1, -1, 0), (0, 0, 1, -1), (0, 0, 1, 1)]
        """
        return [ self.root(i, i+1, 0, 1) for i in range(self.n-1) ] + [self.root(self.n-2, self.n-1, 0, 0)]

    def positive_roots(self):
        """
        EXAMPLES:
            sage: RootSystem(['D',4]).ambient_lattice().positive_roots()
            [(1, 1, 0, 0),
             (1, 0, 1, 0),
             (0, 1, 1, 0),
             (1, 0, 0, 1),
             (0, 1, 0, 1),
             (0, 0, 1, 1),
             (1, -1, 0, 0),
             (1, 0, -1, 0),
             (0, 1, -1, 0),
             (1, 0, 0, -1),
             (0, 1, 0, -1),
             (0, 0, 1, -1)]

        """
        res = []
        for p in [0,1]:
            for j in range(self.n):
                res.extend([self.root(i,j,0,p) for i in range(j)])
        return res

    def negative_roots(self):
        """
        EXAMPLES:
            sage: RootSystem(['D',4]).ambient_lattice().negative_roots()
            [(-1, 1, 0, 0),
             (-1, 0, 1, 0),
             (0, -1, 1, 0),
             (-1, 0, 0, 1),
             (0, -1, 0, 1),
             (0, 0, -1, 1),
             (-1, -1, 0, 0),
             (-1, 0, -1, 0),
             (0, -1, -1, 0),
             (-1, 0, 0, -1),
             (0, -1, 0, -1),
             (0, 0, -1, -1)]
        """
        res = []
        for p in [0,1]:
            for j in range(self.n):
                res.extend([self.root(i,j,1,p) for i in range(j)])
        return res


    def fundamental_weights(self):
        """
        EXAMPLES:
            sage: RootSystem(['D',4]).ambient_lattice().fundamental_weights()
            [(1, 0, 0, 0), (1, 1, 0, 0), (1/2, 1/2, 1/2, -1/2), (1/2, 1/2, 1/2, 1/2)]
        """
        return [ sum(self._term(j) for j in range(i+1)) for i in range(self.n-2)]+\
               [ sum(self._term(j) for j in range(self.n-1))/2-self._term(self.n-1)/2]+\
               [ sum(self._term(j) for j in range(self.n))/2 ]


class AmbientLattice_g(AmbientLattice_generic):
    """
    TESTS:
        sage: [WeylDim(['G',2],[a,b]) for [a,b] in [0,0], [1,0], [0,1], [1,1]]
        [1, 7, 14, 64]
    """
    def __init__(self, ct):
        self.n = 3
        AmbientLattice_generic.__init__(self, ct)

    def simple_roots(self):
        """
        EXAMPLES:
            sage: CartanType(['G',2]).root_system().ambient_lattice().simple_roots()
            [(0, 1, -1), (1, -2, 1)]
         """
        return [ self._term(1)-self._term(2),\
                 self._term(0)-2*self._term(1)+self._term(2)]

    def positive_roots(self):
        """
        EXAMPLES:
            sage: CartanType(['G',2]).root_system().ambient_lattice().positive_roots()
            [(0, 1, -1), (1, -2, 1), (1, -1, 0), (1, 0, -1), (1, 1, -2), (2, -1, -1)]
        """
        return [ c0*self._term(0)+c1*self._term(1)+c2*self._term(2) \
                 for [c0,c1,c2] in
                 [[0,1,-1],[1,-2,1],[1,-1,0],[1,0,-1],[1,1,-2],[2,-1,-1]]]

    def negative_roots(self):
        """
        EXAMPLES:
            sage: CartanType(['G',2]).root_system().ambient_lattice().negative_roots()
            [(0, -1, 1), (-1, 2, -1), (-1, 1, 0), (-1, 0, 1), (-1, -1, 2), (-2, 1, 1)]
        """
        return [ c0*self._term(0)+c1*self._term(1)+c2*self._term(2) \
                 for [c0,c1,c2] in
                 [[0,-1,1],[-1,2,-1],[-1,1,0],[-1,0,1],[-1,-1,2],[-2,1,1]]]

    def fundamental_weights(self):
        """
        EXAMPLES:
            sage: CartanType(['G',2]).root_system().ambient_lattice().fundamental_weights()
            [(-1, 0, 1), (-2, 1, 1)]
        """
        return [ c0*self._term(0)+c1*self._term(1)+c2*self._term(2) \
                 for [c0,c1,c2] in
                 [[-1,0,1],[-2,1,1]]]

def WeylDim(type, coeffs):
    """
    The Weyl Dimension Formula. Here type is a Cartan type and coeffs
    are a list of nonnegative integers of length equal to the rank
    type[1]. A dominant weight hwv is constructed by summing the
    fundamental weights with coefficients from this list. The
    dimension of the irreducible representation of the semisimple
    complex Lie algebra with highest weight vector hwv is returned.
    EXAMPLE: For SO(7), the Cartan type is B3, so:
        sage: WeylDim(['B',3],[1,0,0]) # standard representation of SO(7)
        7
        sage: WeylDim(['B',3],[0,1,0]) # exterior square
        21
        sage: WeylDim(['B',3],[0,0,1]) # spin representation of spin(7)
        8
        sage: WeylDim(['B',3],[1,0,1]) # sum of the first and third fundamental weights
        48
    """
    lattice = RootSystem(type).ambient_lattice()
    rank = type[1]
    fw = lattice.fundamental_weights()
    hwv = sum(coeffs[i]*fw[i] for i in range(min(rank, len(coeffs))))
    return lattice.weyl_dimension(hwv)
