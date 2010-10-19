##############################################################################
#       Copyright (C) 2010 Nathann Cohen <nathann.cohen@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
##############################################################################

cdef class GenericBackend:
    cpdef int add_variable(self)
    cpdef int add_variables(self, int)
    cpdef set_variable_type(self, int variable, int vtype)
    cpdef set_sense(self, int sense)
    cpdef set_objective_coefficient(self, int variable, double coeff)
    cpdef set_objective(self, list coeff)
    cpdef set_verbosity(self, int level)
    cpdef add_constraint(self, list indices, list coeffs, int direction, double bound)
    cpdef add_col(self, list indices, list coeffs)
    cpdef add_constraints(self, int number, int direction, double bound)
    cpdef int solve(self) except -1
    cpdef double get_objective_value(self)
    cpdef double get_variable_value(self, int variable)
    cpdef name(self)
    cpdef bint is_maximization(self)
    cpdef write_lp(self, char * name)
    cpdef write_mps(self, char * name, int modern)
    cpdef row(self, int i)
    cpdef double get_objective_coefficient(self, int i)
    cpdef int ncols(self)
    cpdef int nrows(self)
    cpdef bint is_variable_binary(self, int)
    cpdef bint is_variable_integer(self, int)
    cpdef bint is_variable_continuous(self, int)

    cpdef problem_name(self, char * name = *)
    cpdef row_bounds(self, int index)
    cpdef col_bounds(self, int index)
    cpdef row_name(self, int index, char * name = *)
    cpdef col_name(self, int index, char * name = *)
    cpdef variable_max(self, int index, value = *)
    cpdef variable_min(self, int index, value = *)
