cdef class GenericBackend:
    cpdef int add_variable(self)
    cpdef int add_variables(self, int)
    cpdef  set_variable_type(self, int variable, int vtype)
    cpdef  set_direction(self, int sense)
    cpdef  set_objective_coeff(self, int variable, double coeff)
    cpdef  set_objective(self, list coeff)
    cpdef set_log_level(self, int level)
    cpdef add_constraint(self, list indices, list coeffs, int direction, double bound)
    cpdef add_col(self, list indices, list coeffs)
    cpdef add_constraints(self, int number, int direction, double bound)
    cpdef int solve(self) except -1
    cpdef double get_objective_value(self)
    cpdef double get_variable_value(self, int variable)
    cpdef int n_rows(self)
    cpdef int n_cols(self)
    cpdef name(self)
    cpdef bint is_maximization(self)
    cpdef  set_problem_name(self, char * name)
    cpdef get_problem_name(self)
    cpdef  set_objective_name(self, name)
    cpdef  write_lp(self, char * name)
    cpdef  write_mps(self, char * name, int modern)
    cpdef get_row(self, int i)
    cpdef double get_objective_coeff(self, int i)
    cpdef int n_cols(self)
    cpdef int n_rows(self)
    cpdef get_row_name(self, int)
    cpdef bint is_variable_binary(self, int)
    cpdef bint is_variable_integer(self, int)
    cpdef bint is_variable_continuous(self, int)
    cpdef get_row_bounds(self, int index)
    cpdef get_col_bounds(self, int index)
    cpdef  set_row_name(self, int index, char * name)
    cpdef  set_col_name(self, int index, char * name)
    cpdef get_col_name(self, int index)

    cpdef get_variable_max(self, int index)
    cpdef get_variable_min(self, int index)
    cpdef  set_variable_max(self, int index, value)
    cpdef  set_variable_min(self, int index, value)
