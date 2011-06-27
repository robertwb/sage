"""
Vectors over the symbolic ring.

Implements vectors over the symbolic ring.


AUTHOR:

    -- Robert Bradshaw (2011-05-25): Added more element-wise simplification methods

    -- Joris Vankerschaver (2011-05-15): Initial version


EXAMPLES::

    sage: x, y = var('x, y')
    sage: u = vector([sin(x)^2 + cos(x)^2, log(2*y) + log(3*y)]); u
    (sin(x)^2 + cos(x)^2, log(2*y) + log(3*y))
    sage: type(u)
    <class 'sage.modules.vector_symbolic_dense.Vector_symbolic_dense'>
    sage: u.simplify_full()
    (1, log(6) + 2*log(y))

Check that the outcome of arithmetic with symbolic vectors is again
a symbolic vector (#11549):

    sage: v = vector(SR, [1, 2])
    sage: w = vector(SR, [sin(x), 0])
    sage: type(v)
    <class 'sage.modules.vector_symbolic_dense.Vector_symbolic_dense'>
    sage: type(w)
    <class 'sage.modules.vector_symbolic_dense.Vector_symbolic_dense'>
    sage: type(v + w)
    <class 'sage.modules.vector_symbolic_dense.Vector_symbolic_dense'>
    sage: type(-v)
    <class 'sage.modules.vector_symbolic_dense.Vector_symbolic_dense'>
    sage: type(5*w)
    <class 'sage.modules.vector_symbolic_dense.Vector_symbolic_dense'>

TESTS::

    sage: u = vector(SR, [sin(x^2)])
    sage: loads(dumps(u)) == u
    True

"""

#*****************************************************************************
#       Copyright (C) 2011 Joris Vankerschaver (jv@caltech.edu)
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

import free_module_element
from sage.symbolic.all import SR, Expression


def apply_map(phi):
    """
    Returns a function that applies phi to its argument.

    EXAMPLES::

        sage: from sage.modules.vector_symbolic_dense import apply_map
        sage: v = vector([1,2,3])
        sage: f = apply_map(lambda x: x+1)
        sage: f(v)
        (2, 3, 4)

    """
    def apply(self, *args, **kwds):
        """
        Generic function used to implement common symbolic operations
        elementwise as methods of a vector.

        EXAMPLES::

            sage: var('x,y')
            (x, y)
            sage: v = vector([sin(x)^2 + cos(x)^2, log(x*y), sin(x/(x^2 + x)), factorial(x+1)/factorial(x)])
            sage: v.simplify_trig()
            (1, log(x*y), sin(1/(x + 1)), factorial(x + 1)/factorial(x))
            sage: v.simplify_radical()
            (sin(x)^2 + cos(x)^2, log(x) + log(y), sin(1/(x + 1)), factorial(x + 1)/factorial(x))
            sage: v.simplify_rational()
            (sin(x)^2 + cos(x)^2, log(x*y), sin(1/(x + 1)), factorial(x + 1)/factorial(x))
            sage: v.simplify_factorial()
            (sin(x)^2 + cos(x)^2, log(x*y), sin(x/(x^2 + x)), x + 1)
            sage: v.simplify_full()
            (1, log(x*y), sin(1/(x + 1)), x + 1)

            sage: v = vector([sin(2*x), sin(3*x)])
            sage: v.simplify_trig()
            (2*sin(x)*cos(x), (4*cos(x)^2 - 1)*sin(x))
            sage: v.simplify_trig(False)
            (sin(2*x), sin(3*x))
            sage: v.simplify_trig(expand=False)
            (sin(2*x), sin(3*x))
        """
        return self.apply_map(lambda x: phi(x, *args, **kwds))
    apply.__doc__ += "\nSee Expression." + phi.__name__ + "() for optional arguments."
    return apply


class Vector_symbolic_dense(free_module_element.FreeModuleElement_generic_dense):
    pass

# Add elementwise methods.
for method in ['simplify', 'simplify_exp', 'simplify_factorial',
        'simplify_log', 'simplify_radical', 'simplify_rational',
        'simplify_trig', 'simplify_full', 'trig_expand', 'trig_reduce']:
    setattr(Vector_symbolic_dense, method, apply_map(getattr(Expression, method)))
