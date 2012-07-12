"""
Multiplicative symmetric functions

A realization `h` of the ring of symmetric functions is multiplicative if for
a partition `\lambda = (\lambda_1,\lambda_2,\ldots)` we have
`h_\lambda = h_{\lambda_1} h_{\lambda_2} \cdots`.
"""
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
import classical
import sage.combinat.partition

class SymmetricFunctionAlgebra_multiplicative(classical.SymmetricFunctionAlgebra_classical):
    """
    The class of multiplicative symmetric functions.

    A realization `h` of the ring of symmetric functions is multiplicative if for
    a partition `\lambda = (\lambda_1,\lambda_2,\ldots)` we have
    `h_\lambda = h_{\lambda_1} h_{\lambda_2} \cdots`.
    """

    def _multiply_basis(self, left, right):
        """
        Returns the product of ``left`` and ``right``.

        INPUT:

        - ``self`` -- a multiplicative basis of the symmetric functions
        - ``left``, ``right`` -- instances of the multiplicative basis ``self`` of the ring of symmetric functions.

        OUTPUT:

        - an element of ``self``

        TESTS::

            sage: e = SymmetricFunctions(QQ).e()
            sage: e([2,1])^2  # indirect doctest
            e[2, 2, 1, 1]

        ::

            sage: h = SymmetricFunctions(QQ).h()
            sage: h([2,1])^2
            h[2, 2, 1, 1]

        ::

            sage: p = SymmetricFunctions(QQ).p()
            sage: p([2,1])^2
            p[2, 2, 1, 1]

        ::

            sage: QQx.<x> = QQ[]
            sage: p = SymmetricFunctions(QQx).p()
            sage: (x*p([2]))^2
            x^2*p[2, 2]

            sage: TestSuite(p).run() # to silence sage -coverage
        """
        m = list(left)+list(right)
        m.sort(reverse=True)
        return sage.combinat.partition.Partition_class(m)

    def coproduct_on_basis(self, mu):
        r"""
        Returns coproduct on basis for multiplicative bases.

        INPUT:

        - ``self`` -- a multiplicative basis of the symmetric functions
        - ``mu`` -- a partition

        OUTPUT:

        - an element of the tensor square of ``self``

        EXAMPLES::

            sage: Sym = SymmetricFunctions(QQ)
            sage: p = Sym.powersum()
            sage: p.coproduct_on_basis([2,1])
            p[] # p[2, 1] + p[1] # p[2] + p[2] # p[1] + p[2, 1] # p[]

            sage: e = Sym.elementary()
            sage: e.coproduct_on_basis([3,1])
            e[] # e[3, 1] + e[1] # e[2, 1] + e[1] # e[3] + e[1, 1] # e[2] + e[2] # e[1, 1] + e[2, 1] # e[1] + e[3] # e[1] + e[3, 1] # e[]

            sage: h = Sym.homogeneous()
            sage: h.coproduct_on_basis([3,1])
            h[] # h[3, 1] + h[1] # h[2, 1] + h[1] # h[3] + h[1, 1] # h[2] + h[2] # h[1, 1] + h[2, 1] # h[1] + h[3] # h[1] + h[3, 1] # h[]
        """
        T = self.tensor_square()
        return T.prod(self.coproduct_on_generators(p) for p in mu)
