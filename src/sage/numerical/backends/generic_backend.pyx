r"""
Generic Backend for LP solvers

This class only lists the methods that should be defined by any
interface with a LP Solver. All these methods immediately raise
``NotImplementedError`` exceptions when called, and are obviously
meant to be replaced by the solver-specific method. This file can also
be used as a template to create a new interface : one would only need
to replace the occurences of ``"Nonexistent_LP_solver"`` by the
solver's name, and replace ``GenericBackend`` by
``SolverName(GenericBackend)`` so that the new solver extends this
class.

AUTHORS:

- Nathann Cohen (2010-10): initial implementation

"""

##############################################################################
#       Copyright (C) 2010 Nathann Cohen <nathann.cohen@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
##############################################################################


cdef class GenericBackend:
    cpdef int add_variable(self, lower_bound=0.0, upper_bound=None, binary=False, continuous=True, integer=False) except -1:
        """
        Add a variable.

        This amounts to adding a new column to the matrix. By default,
        the variable is both positive and real.

        INPUT:

        - ``lower_bound`` - the lower bound of the variable (default: 0)

        - ``upper_bound`` - the upper bound of the variable (default: ``None``)

        - ``binary`` - ``True`` if the variable is binary (default: ``False``).

        - ``continuous`` - ``True`` if the variable is binary (default: ``True``).

        - ``integer`` - ``True`` if the variable is binary (default: ``False``).

        OUTPUT: The index of the newly created variable

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")    # optional - Nonexistent_LP_solver
            sage: p.ncols()                                           # optional - Nonexistent_LP_solver
            0
            sage: p.add_variable()                                    # optional - Nonexistent_LP_solver
            0
            sage: p.ncols()                                           # optional - Nonexistent_LP_solver
            1
            sage: p.add_variable(binary=True)                         # optional - Nonexistent_LP_solver
            1
            sage: p.add_variable(lower_bound=-2.0, integer=True)      # optional - Nonexistent_LP_solver
            2
            sage: p.add_variable(continuous=True, integer=True)       # optional - Nonexistent_LP_solver
            Traceback (most recent call last):
            ...
            ValueError: ...
        """
        raise NotImplementedError()

    cpdef int add_variables(self, int n, lower_bound=0.0, upper_bound=None, binary=False, continuous=True, integer=False) except -1:
        """
        Add ``n`` variables.

        This amounts to adding new columns to the matrix. By default,
        the variables are both positive and real.

        INPUT:

        - ``n`` - the number of new variables (must be > 0)

        - ``lower_bound`` - the lower bound of the variable (default: 0)

        - ``upper_bound`` - the upper bound of the variable (default: ``None``)

        - ``binary`` - ``True`` if the variable is binary (default: ``False``).

        - ``continuous`` - ``True`` if the variable is binary (default: ``True``).

        - ``integer`` - ``True`` if the variable is binary (default: ``False``).

        OUTPUT: The index of the variable created last.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")    # optional - Nonexistent_LP_solver
            sage: p.ncols()                                           # optional - Nonexistent_LP_solver
            0
            sage: p.add_variables(5)                                  # optional - Nonexistent_LP_solver
            4
            sage: p.ncols()                                           # optional - Nonexistent_LP_solver
            5
            sage: p.add_variables(2, lower_bound=-2.0, integer=True)  # optional - Nonexistent_LP_solver
            6
        """
        raise NotImplementedError()

    cpdef  set_variable_type(self, int variable, int vtype):
        """
        Set the type of a variable

        INPUT:

        - ``variable`` (integer) -- the variable's id

        - ``vtype`` (integer) :

            *  1  Integer
            *  0  Binary
            * -1  Continuous

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")   # optional - Nonexistent_LP_solver
            sage: p.ncols()                                        # optional - Nonexistent_LP_solver
            0
            sage: p.add_variable()                                  # optional - Nonexistent_LP_solver
            1
            sage: p.set_variable_type(0,1)                          # optional - Nonexistent_LP_solver
            sage: p.is_variable_integer(0)                          # optional - Nonexistent_LP_solver
            True
        """
        raise NotImplementedError()

    cpdef set_sense(self, int sense):
        """
        Set the direction (maximization/minimization).

        INPUT:

        - ``sense`` (integer) :

            * +1 => Maximization
            * -1 => Minimization

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.is_maximization()                              # optional - Nonexistent_LP_solver
            True
            sage: p.set_sense(-1)                              # optional - Nonexistent_LP_solver
            sage: p.is_maximization()                              # optional - Nonexistent_LP_solver
            False
        """
        raise NotImplementedError()

    cpdef  set_objective_coefficient(self, int variable, double coeff):
        """
        Set the coefficient of a variable in the objective function

        INPUT:

        - ``variable`` (integer) -- the variable's id

        - ``coeff`` (double) -- its coefficient

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.get_objective_coefficient(0)                         # optional - Nonexistent_LP_solver
            0.0
            sage: p.set_objective_coefficient(0,2)                       # optional - Nonexistent_LP_solver
            sage: p.get_objective_coefficient(0)                         # optional - Nonexistent_LP_solver
            2.0
        """
        raise NotImplementedError()

    cpdef  set_objective(self, list coeff):
        """
        Set the objective function.

        INPUT:

        - ``coeff`` -- a list of real values, whose ith element is the
          coefficient of the ith variable in the objective function.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")    # optional - Nonexistent_LP_solver
            sage: p.add_variables(5)                                 # optional - Nonexistent_LP_solver
            5
            sage: p.set_objective([1, 1, 2, 1, 3])                   # optional - Nonexistent_LP_solver
            sage: map(lambda x :p.get_objective_coeffient(x), range(5))  # optional - Nonexistent_LP_solver
            [1.0, 1.0, 2.0, 1.0, 3.0]
        """
        raise NotImplementedError()

    cpdef set_verbosity(self, int level):
        """
        Set the log (verbosity) level

        INPUT:

        - ``level`` (integer) -- From 0 (no verbosity) to 3.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.set_verbosity(2)                                # optional - Nonexistent_LP_solver
        """
        raise NotImplementedError()

    cpdef add_linear_constraint(self, coefficients, lower_bound, upper_bound):
        """
        Add a linear constraint.

        INPUT:

        - ``coefficients`` an iterable with ``(c,v)`` pairs where ``c``
          is a variable index (integer) and ``v`` is a value (real
          value).

        - ``lower_bound`` - a lower bound, either a real value or ``None``

        - ``upper_bound`` - an upper bound, either a real value or ``None``

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver") # optional - Nonexistent_LP_solver
            sage: p.add_variables(5)                               # optional - Nonexistent_LP_solver
            4
            sage: p.add_linear_constraint(zip(range(5), range(5)), 2.0, 2.0) # optional - Nonexistent_LP_solver
            sage: p.row(0)                                         # optional - Nonexistent_LP_solver
            ([4, 3, 2, 1], [4.0, 3.0, 2.0, 1.0])                   # optional - Nonexistent_LP_solver
            sage: p.row_bounds(0)                                  # optional - Nonexistent_LP_solver
            (2.0, 2.0)
        """
        raise NotImplementedError()

    cpdef add_col(self, list indices, list coeffs):
        """
        Add a column.

        INPUT:

        - ``indices`` (list of integers) -- this list constains the
          indices of the constraints in which the variable's
          coefficient is nonzero

        - ``coeffs`` (list of real values) -- associates a coefficient
          to the variable in each of the constraints in which it
          appears. Namely, the ith entry of ``coeffs`` corresponds to
          the coefficient of the variable in the constraint
          represented by the ith entry in ``indices``.

        .. NOTE::

            ``indices`` and ``coeffs`` are expected to be of the same
            length.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.ncols()                                       # optional - Nonexistent_LP_solver
            0
            sage: p.nrows()                                       # optional - Nonexistent_LP_solver
            0
            sage: p.add_linear_constraints(5, 0, None)            # optional - Nonexistent_LP_solver
            sage: p.add_col(range(5), range(5))                   # optional - Nonexistent_LP_solver
            sage: p.nrows()                                       # optional - Nonexistent_LP_solver
            5
        """
        raise NotImplementedError()

    cpdef add_linear_constraints(self, int number, lower_bound, upper_bound):
        """
        Add constraints.

        INPUT:

        - ``number`` (integer) -- the number of constraints to add.

        - ``lower_bound`` - a lower bound, either a real value or ``None``

        - ``upper_bound`` - an upper bound, either a real value or ``None``

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")   # optional - Nonexistent_LP_solver
            sage: p.add_variables(5)                                # optional - Nonexistent_LP_solver
            5
            sage: p.add_linear_constraints(5, None, 2)          # optional - Nonexistent_LP_solver
            sage: p.row(4)                                      # optional - Nonexistent_LP_solver
            ([], [])
            sage: p.row_bounds(4)                               # optional - Nonexistent_LP_solver
            (None, 2.0)
        """
        raise NotImplementedError()

    cpdef int solve(self) except -1:
        """
        Solve the problem.

        .. NOTE::

            This method raises ``MIPSolverException`` exceptions when
            the solution can not be computed for any reason (none
            exists, or the LP solver was not able to find it, etc...)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver") # optional - Nonexistent_LP_solver
            sage: p.add_linear_constraints(5, 0, None)             # optional - Nonexistent_LP_solver
            sage: p.add_col(range(5), range(5))                    # optional - Nonexistent_LP_solver
            sage: p.solve()                                        # optional - Nonexistent_LP_solver
            0
            sage: p.set_objective_coefficient(0,1)                 # optional - Nonexistent_LP_solver
            sage: p.solve()                                        # optional - Nonexistent_LP_solver
            Traceback (most recent call last):
            ...
            MIPSolverException: ...
        """
        raise NotImplementedError()

    cpdef double get_objective_value(self):
        """
        Return the value of the objective function.

        .. NOTE::

           Behaviour is undefined unless ``solve`` has been called before.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver") # optional - Nonexistent_LP_solver
            sage: p.add_variables(2)                               # optional - Nonexistent_LP_solver
            2
            sage: p.add_linear_constraint([(0,1), (1,2)], None, 3) # optional - Nonexistent_LP_solver
            sage: p.set_objective([2, 5])                          # optional - Nonexistent_LP_solver
            sage: p.solve()                                        # optional - Nonexistent_LP_solver
            0
            sage: p.get_objective_value()                          # optional - Nonexistent_LP_solver
            7.5
            sage: p.get_variable_value(0)                          # optional - Nonexistent_LP_solver
            0.0
            sage: p.get_variable_value(1)                          # optional - Nonexistent_LP_solver
            1.5
        """

        raise NotImplementedError()

    cpdef double get_variable_value(self, int variable):
        """
        Return the value of a variable given by the solver.

        .. NOTE::

           Behaviour is undefined unless ``solve`` has been called before.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver") # optional - Nonexistent_LP_solver
            sage: p.add_variables(2)                              # optional - Nonexistent_LP_solver
            2
            sage: p.add_linear_constraint([(0,1), (1, 2)], None, 3) # optional - Nonexistent_LP_solver
            sage: p.set_objective([2, 5])                         # optional - Nonexistent_LP_solver
            sage: p.solve()                                       # optional - Nonexistent_LP_solver
            0
            sage: p.get_objective_value()                         # optional - Nonexistent_LP_solver
            7.5
            sage: p.get_variable_value(0)                         # optional - Nonexistent_LP_solver
            0.0
            sage: p.get_variable_value(1)                         # optional - Nonexistent_LP_solver
            1.5
        """

        raise NotImplementedError()

    cpdef int ncols(self):
        """
        Return the number of columns/variables.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.ncols()                                       # optional - Nonexistent_LP_solver
            0
            sage: p.add_variables(2)                               # optional - Nonexistent_LP_solver
            2
            sage: p.ncols()                                       # optional - Nonexistent_LP_solver
            2
        """

        raise NotImplementedError()

    cpdef int nrows(self):
        """
        Return the number of rows/constraints.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver") # optional - Nonexistent_LP_solver
            sage: p.nrows()                                        # optional - Nonexistent_LP_solver
            0
            sage: p.add_linear_constraints(2, 2.0, None)         # optional - Nonexistent_LP_solver
            sage: p.nrows()                                      # optional - Nonexistent_LP_solver
            2
        """

        raise NotImplementedError()

    cpdef bint is_maximization(self):
        """
        Test whether the problem is a maximization

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver") # optional - Nonexistent_LP_solver
            sage: p.is_maximization()                             # optional - Nonexistent_LP_solver
            True
            sage: p.set_sense(-1)                             # optional - Nonexistent_LP_solver
            sage: p.is_maximization()                             # optional - Nonexistent_LP_solver
            False
        """
        raise NotImplementedError()

    cpdef problem_name(self, char * name = NULL):
        """
        Return or define the problem's name

        INPUT:

        - ``name`` (``char *``) -- the problem's name. When set to
          ``NULL`` (default), the method returns the problem's name.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")   # optional - Nonexistent_LP_solver
            sage: p.problem_name("There once was a french fry") # optional - Nonexistent_LP_solver
            sage: print p.get_problem_name()                        # optional - Nonexistent_LP_solver
            There once was a french fry
        """

        raise NotImplementedError()

    cpdef write_lp(self, char * name):
        """
        Write the problem to a .lp file

        INPUT:

        - ``filename`` (string)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variables(2)                               # optional - Nonexistent_LP_solver
            2
            sage: p.add_linear_constraint([(0, 1], (1, 2)], None, 3) # optional - Nonexistent_LP_solver
            sage: p.set_objective([2, 5])                          # optional - Nonexistent_LP_solver
            sage: p.write_lp(SAGE_TMP+"/lp_problem.lp")            # optional - Nonexistent_LP_solver
        """
        raise NotImplementedError()

    cpdef write_mps(self, char * name, int modern):
        """
        Write the problem to a .mps file

        INPUT:

        - ``filename`` (string)

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variables(2)                               # optional - Nonexistent_LP_solver
            2
            sage: p.add_linear_constraint([(0, 1), (1, 2)], None, 3) # optional - Nonexistent_LP_solver
            sage: p.set_objective([2, 5])                          # optional - Nonexistent_LP_solver
            sage: p.write_lp(SAGE_TMP+"/lp_problem.lp")            # optional - Nonexistent_LP_solver
        """
        raise NotImplementedError()

    cpdef row(self, int i):
        """
        Return a row

        INPUT:

        - ``index`` (integer) -- the constraint's id.

        OUTPUT:

        A pair ``(indices, coeffs)`` where ``indices`` lists the
        entries whose coefficient is nonzero, and to which ``coeffs``
        associates their coefficient on the model of the
        ``add_linear_constraint`` method.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variables(5)                               # optional - Nonexistent_LP_solver
            5
            sage: p.add_linear_constraint(zip(range(5), range(5)), 2, 2) # optional - Nonexistent_LP_solver
            sage: p.row(0)                                     # optional - Nonexistent_LP_solver
            ([4, 3, 2, 1], [4.0, 3.0, 2.0, 1.0])
            sage: p.row_bounds(0)                              # optional - Nonexistent_LP_solver
            (2.0, 2.0)
        """
        raise NotImplementedError()

    cpdef double get_objective_coefficient(self, int i):
        """
        Set the coefficient of a variable in the objective function

        INPUT:

        - ``variable`` (integer) -- the variable's id

        - ``coeff`` (double) -- its coefficient

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.get_objective_coeffient(0)                         # optional - Nonexistent_LP_solver
            0.0
            sage: p.set_objective_coefficient(0,2)                       # optional - Nonexistent_LP_solver
            sage: p.get_objective_coeffient(0)                         # optional - Nonexistent_LP_solver
            2.0
        """
        raise NotImplementedError()

    cpdef row_bounds(self, int index):
        """
        Return the bounds of a specific constraint.

        INPUT:

        - ``index`` (integer) -- the constraint's id.

        OUTPUT:

        A pair ``(lower_bound, upper_bound)``. Each of them can be set
        to ``None`` if the constraint is not bounded in the
        corresponding direction, and is a real value otherwise.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variables(5)                               # optional - Nonexistent_LP_solver
            5
            sage: p.add_linear_constraint(range(5), range(5), 2, 2) # optional - Nonexistent_LP_solver
            sage: p.row(0)                                     # optional - Nonexistent_LP_solver
            ([4, 3, 2, 1], [4.0, 3.0, 2.0, 1.0])
            sage: p.row_bounds(0)                              # optional - Nonexistent_LP_solver
            (2.0, 2.0)
        """
        raise NotImplementedError()

    cpdef col_bounds(self, int index):
        """
        Return the bounds of a specific variable.

        INPUT:

        - ``index`` (integer) -- the variable's id.

        OUTPUT:

        A pair ``(lower_bound, upper_bound)``. Each of them can be set
        to ``None`` if the variable is not bounded in the
        corresponding direction, and is a real value otherwise.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.col_bounds(0)                              # optional - Nonexistent_LP_solver
            (0.0, None)
            sage: p.variable_upper_bound(0, 5)                 # optional - Nonexistent_LP_solver
            sage: p.col_bounds(0)                              # optional - Nonexistent_LP_solver
            (0.0, 5.0)
        """
        raise NotImplementedError()

    cpdef bint is_variable_binary(self, int index):
        """
        Test whether the given variable is of binary type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.ncols()                                       # optional - Nonexistent_LP_solver
            0
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.set_variable_type(0,0)                         # optional - Nonexistent_LP_solver
            sage: p.is_variable_binary(0)                          # optional - Nonexistent_LP_solver
            True

        """
        raise NotImplementedError()

    cpdef bint is_variable_integer(self, int index):
        """
        Test whether the given variable is of integer type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.ncols()                                       # optional - Nonexistent_LP_solver
            0
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.set_variable_type(0,1)                         # optional - Nonexistent_LP_solver
            sage: p.is_variable_integer(0)                         # optional - Nonexistent_LP_solver
            True
        """
        raise NotImplementedError()

    cpdef bint is_variable_continuous(self, int index):
        """
        Test whether the given variable is of continuous/real type.

        INPUT:

        - ``index`` (integer) -- the variable's id

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.ncols()                                       # optional - Nonexistent_LP_solver
            0
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.is_variable_continuous(0)                      # optional - Nonexistent_LP_solver
            True
            sage: p.set_variable_type(0,1)                         # optional - Nonexistent_LP_solver
            sage: p.is_variable_continuous(0)                      # optional - Nonexistent_LP_solver
            False

        """
        raise NotImplementedError()

    cpdef row_name(self, int index, char * name = NULL):
        """
        Return or define the ``index`` th row name

        INPUT:

        - ``index`` (integer) -- the row's id

        - ``name`` (``char *``) -- its name. When set to ``NULL``
          (default), the method returns the current name.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_linear_constraints(1, 2, None)         # optional - Nonexistent_LP_solver
            sage: p.row_name(0, "Empty constraint 1")          # optional - Nonexistent_LP_solver
            sage: p.row_name(0)                                # optional - Nonexistent_LP_solver
            'Empty constraint 1'

        """
        raise NotImplementedError()

    cpdef col_name(self, int index, char * name = NULL):
        """
        Return or define the ``index`` th col name

        INPUT:

        - ``index`` (integer) -- the col's id

        - ``name`` (``char *``) -- its name. When set to ``NULL``
          (default), the method returns the current name.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.col_name(0, "I am a variable")             # optional - Nonexistent_LP_solver
            sage: p.col_name(0)                                # optional - Nonexistent_LP_solver
            'I am a variable'
        """
        raise NotImplementedError()

    cpdef variable_upper_bound(self, int index, value = None):
        """
        Return or define the upper bound on a variable

        INPUT:

        - ``index`` (integer) -- the variable's id

        - ``value`` -- real value, or ``None`` to mean that the
          variable has not upper bound. When set to ``None``
          (default), the method returns the current value.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.col_bounds(0)                              # optional - Nonexistent_LP_solver
            (0.0, None)
            sage: p.variable_upper_bound(0, 5)                 # optional - Nonexistent_LP_solver
            sage: p.col_bounds(0)                              # optional - Nonexistent_LP_solver
            (0.0, 5.0)
        """
        raise NotImplementedError()

    cpdef variable_lower_bound(self, int index, value = None):
        """
        Return or define the lower bound on a variable

        INPUT:

        - ``index`` (integer) -- the variable's id

        - ``value`` -- real value, or ``None`` to mean that the
          variable has not lower bound. When set to ``None``
          (default), the method returns the current value.

        EXAMPLE::

            sage: from sage.numerical.backends.generic_backend import get_solver
            sage: p = get_solver(solver = "Nonexistent_LP_solver")  # optional - Nonexistent_LP_solver
            sage: p.add_variable()                                 # optional - Nonexistent_LP_solver
            1
            sage: p.col_bounds(0)                              # optional - Nonexistent_LP_solver
            (0.0, None)
            sage: p.variable_lower_bound(0, 5)                 # optional - Nonexistent_LP_solver
            sage: p.col_bounds(0)                              # optional - Nonexistent_LP_solver
            (5.0, None)
        """
        raise NotImplementedError()

default_solver = None

def default_mip_solver(solver = None):
    """
    Returns/Sets the default MILP Solver used by Sage

    INPUT:

    - ``solver`` -- defines the solver to use:

        - GLPK (``solver="GLPK"``). See the `GLPK
          <http://www.gnu.org/software/glpk/>`_ web site.

        - COIN Branch and Cut (``solver="Coin"``). See the `COIN-OR
          <http://www.coin-or.org>`_ web site.

        - CPLEX (``solver="CPLEX"``). See the
          `CPLEX <http://www.ilog.com/products/cplex/>`_ web site.
          An interface to CPLEX is not yet implemented.

        ``solver`` should then be equal to one of ``"GLPK"``,
        ``"Coin"``, ``"CPLEX"``.

        - If ``solver=None`` (default), the current default solver's name is
          returned.

    OUTPUT:

    This function returns the current default solver's name if ``solver = None``
    (default). Otherwise, it sets the default solver to the one given. If this
    solver does not exist, or is not available, a ``ValueError`` exception is
    raised.

    EXAMPLE::

        sage: former_solver = default_mip_solver()
        sage: default_mip_solver("GLPK")
        sage: default_mip_solver()
        'GLPK'
        sage: default_mip_solver("Yeahhhhhhhhhhh")
        Traceback (most recent call last):
        ...
        ValueError: 'solver' should be set to 'GLPK', 'Coin', 'CPLEX' or None.
        sage: default_mip_solver(former_solver)
    """
    global default_solver

    if solver is None:

        if default_solver is not None:
            return default_solver

        else:
            for s in ["CPLEX", "Coin", "GLPK"]:
                try:
                    default_mip_solver(s)
                    return s
                except ValueError:
                    pass

    elif solver == "CPLEX":
        try:
            from sage.numerical.backends.cplex_backend import CPLEXBackend
            default_solver = solver
        except ImportError:
            raise ValueError("CPLEX is not available. Please refer to the documentation to install it.")

    elif solver == "Coin":
        try:
            from sage.numerical.backends.coin_backend import CoinBackend
            default_solver = solver
        except ImportError:
            raise ValueError("COIN is not available. Please refer to the documentation to install it.")

    elif solver == "GLPK":
        default_solver = solver

    else:
        raise ValueError("'solver' should be set to 'GLPK', 'Coin', 'CPLEX' or None.")

cpdef GenericBackend get_solver(constraint_generation = False, solver = None):
    """
    Return a solver according to the given preferences

    INPUT:

    - ``solver`` -- 3 solvers should be available through this class:

        - GLPK (``solver="GLPK"``). See the `GLPK
          <http://www.gnu.org/software/glpk/>`_ web site.

        - COIN Branch and Cut (``solver="Coin"``). See the `COIN-OR
          <http://www.coin-or.org>`_ web site.

        - CPLEX (``solver="CPLEX"``). See the
          `CPLEX <http://www.ilog.com/products/cplex/>`_ web site.
          An interface to CPLEX is not yet implemented.

        ``solver`` should then be equal to one of ``"GLPK"``, ``"Coin"``,
        ``"CPLEX"``, or ``None``. If ``solver=None`` (default), the default
        solver is used (see ``default_mip_solver`` method.

    - ``constraint_generation`` (boolean) -- whether the solver
      returned is to be used for constraint/variable generation. As
      the interface with Coin does not support constraint/variable
      generation, setting ``constraint_generation`` to ``False``
      ensures that the backend to Coin is not returned when ``solver =
      None``. This is set to ``False`` by default.

    .. SEEALSO::

    - :func:`default_mip_solver` -- Returns/Sets the default MIP solver.

    EXAMPLE::

        sage: from sage.numerical.backends.generic_backend import get_solver
        sage: p = get_solver()
    """

    if solver is None:
        solver = default_mip_solver()

        # We do not want to use Coin for constraint_generation. It just does not
        # work with it.
        if solver == "Coin" and constraint_generation:
            solver = "GLPK"

    if solver == "Coin":
        from sage.numerical.backends.coin_backend import CoinBackend
        return CoinBackend()

    elif solver == "GLPK":
        from sage.numerical.backends.glpk_backend import GLPKBackend
        return GLPKBackend()

    elif solver == "CPLEX":
        from sage.numerical.backends.cplex_backend import CPLEXBackend
        return CPLEXBackend()

    else:
        raise ValueError("'solver' should be set to 'GLPK', 'Coin', 'CPLEX' or None (in which case the default one is used).")
