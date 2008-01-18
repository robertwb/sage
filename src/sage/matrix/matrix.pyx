"""
Abstract base class for matrices.

For design documentation see matrix/docs.py.
"""

################################################################################
#       Copyright (C) 2005, 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL).
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
################################################################################

include '../ext/stdsage.pxi'

def is_Matrix(x):
    """
    EXAMPLES:
        sage: is_Matrix(0)
        False
        sage: is_Matrix(matrix([[1,2],[3,4]]))
        True
    """
    return IS_INSTANCE(x, Matrix)

cdef class Matrix(matrix2.Matrix):
    pass
