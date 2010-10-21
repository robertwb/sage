r"""
Mixed integer linear programming

A linear program (`LP <http://en.wikipedia.org/wiki/Linear_programming>`_)
is an `optimization problem <http://en.wikipedia.org/wiki/Optimization_%28mathematics%29>`_
in the following form

.. centered::
     `\max \{ c^T x \;|\; A x \leq b, x \geq 0 \}`

with given `A \in \mathbb{R}^{m,n}`, `b \in \mathbb{R}^m`,
`c \in \mathbb{R}^n` and unknown `x \in \mathbb{R}^{n}`.
If some or all variables in the vector `x` are restricted over
the integers `\mathbb{Z}`, the problem is called mixed integer
linear program (`MILP <http://en.wikipedia.org/wiki/Mixed_integer_linear_programming>`_).
A wide variety of problems in optimization
can be formulated in this standard form. Then, solvers are
able to calculate a solution.

Imagine you want to solve the following linear system of three equations:

 - `w_0 + w_1 + w_2 - 14 w_3 = 0`
 - `w_1 + 2 w_2 - 8 w_3 = 0`
 - `2 w_2 - 3 w_3 = 0`

and this additional inequality:

 - `w_0 - w_1 - w_2 \geq 0`

where all `w_i \in \mathbb{Z}`. You know that the trivial solution is
`w_i = 0 \; \forall i`, but what is the first non-trivial one with
`w_3 \geq 1`?

A mixed integer linear program can give you an answer:

  #. You have to create an instance of :class:`MixedIntegerLinearProgram` and
     -- in our case -- specify that it is a minimization.
  #. Create a variable vector ``w`` via ``w = p.new_variable(integer=True)`` and
     tell the system that it is over the integers.
  #. Add those three equations as equality constraints via
     :meth:`add_constraint <sage.numerical.mip.MixedIntegerLinearProgram.add_constraint>`.
  #. Also add the inequality constraint.
  #. Add an inequality constraint `w_3 \geq 1` to exclude the trivial solution.
  #. By default, all variables have a minimum of `0`. We remove that constraint
     via ``p.set_min(variable, None)``, see :meth:`set_min <sage.numerical.mip.MixedIntegerLinearProgram.set_min>`.
  #. Specify the objective function via :meth:`set_objective <sage.numerical.mip.MixedIntegerLinearProgram.set_objective>`.
     In our case that is just `w_3`. If it
     is a pure constraint satisfaction problem, specify it as ``None``.
  #. To check if everything is set up correctly, you can print the problem via
     :meth:`show <sage.numerical.mip.MixedIntegerLinearProgram.show>`.
  #. :meth:`Solve <sage.numerical.mip.MixedIntegerLinearProgram.solve>` it and print the solution.

The following example shows all these steps::

    sage: p = MixedIntegerLinearProgram(maximization=False)
    sage: w = p.new_variable(integer=True)
    sage: p.add_constraint(w[0] + w[1] + w[2] - 14*w[3] == 0)
    sage: p.add_constraint(w[1] + 2*w[2] - 8*w[3] == 0)
    sage: p.add_constraint(2*w[2] - 3*w[3] == 0)
    sage: p.add_constraint(w[0] - w[1] - w[2] >= 0)
    sage: p.add_constraint(w[3] >= 1)
    sage: _ = [ p.set_min(w[i], None) for i in range(1,4) ]
    sage: p.set_objective(w[3])
    sage: p.show()
    Minimization:
       x_3
    Constraints:
      0.0 <= x_0 +x_1 +x_2 -14.0 x_3 <= 0.0
      0.0 <= x_1 +2.0 x_2 -8.0 x_3 <= 0.0
      0.0 <= 2.0 x_2 -3.0 x_3 <= 0.0
      -1.0 x_0 +x_1 +x_2 <= 0.0
      -1.0 x_3 <= -1.0
    Variables:
      x_0 is an integer variable (min=0.0, max=+oo)
      x_1 is an integer variable (min=-oo, max=+oo)
      x_2 is an integer variable (min=-oo, max=+oo)
      x_3 is an integer variable (min=-oo, max=+oo)
    sage: print 'Objective Value:', p.solve()
    Objective Value: 2.0
    sage: for i, v in p.get_values(w).iteritems():\
              print 'w_%s = %s' % (i, int(round(v)))
    w_0 = 15
    w_1 = 10
    w_2 = 3
    w_3 = 2
"""

include "../ext/stdsage.pxi"
include "../ext/interrupt.pxi"
from copy import deepcopy

cdef class MixedIntegerLinearProgram:
    r"""
    The ``MixedIntegerLinearProgram`` class is the link between Sage, linear
    programming (LP) and  mixed integer programming (MIP) solvers. See the
    Wikipedia article on
    `linear programming <http://en.wikipedia.org/wiki/Linear_programming>`_
    for further information. A mixed integer program consists of variables,
    linear constraints on these variables, and an objective function which is
    to be maximised or minimised under these constraints. An instance of
    ``MixedIntegerLinearProgram`` also requires the information on the
    direction of the optimization.

    A ``MixedIntegerLinearProgram`` (or ``LP``) is defined as a maximization
    if ``maximization=True`` and is a minimization if ``maximization=False``.

    INPUT:

    - ``maximization``

      - When set to ``True`` (default), the ``MixedIntegerLinearProgram`` is
        defined as a maximization.
      - When set to ``False``, the ``MixedIntegerLinearProgram`` is defined as
        a minimization.

    EXAMPLES:

    Computation of a maximum stable set in Petersen's graph::

         sage: g = graphs.PetersenGraph()
         sage: p = MixedIntegerLinearProgram(maximization=True)
         sage: b = p.new_variable()
         sage: p.set_objective(sum([b[v] for v in g]))
         sage: for (u,v) in g.edges(labels=None):
         ...       p.add_constraint(b[u] + b[v], max=1)
         sage: p.set_binary(b)
         sage: p.solve(objective_only=True)
         4.0
    """

    def __init__(self, solver = None, maximization=True):
        r"""
        Constructor for the ``MixedIntegerLinearProgram`` class.

        INPUT:

        - ``solver`` -- 3 solvers should be available through this class:

          - GLPK (``solver="GLPK"``). See the
            `GLPK <http://www.gnu.org/software/glpk/>`_ web site.

          - COIN Branch and Cut  (``solver="Coin"``). See the
            `COIN-OR <http://www.coin-or.org>`_ web site.

          - CPLEX (``solver="CPLEX"``). See the
            `CPLEX <http://www.ilog.com/products/cplex/>`_ web site.
            An interface to CPLEX is not yet implemented.

            ``solver`` should then be equal to one of ``"GLPK"``,
            ``"Coin"``, ``"CPLEX"``, or ``None``. If ``solver=None``
            (default), the solvers are tried in this order :

                * CPLEX
                * Coin
                * GLPK

            A backend corresponding to the first solver available is
            then returned



        - ``maximization``

          - When set to ``True`` (default), the ``MixedIntegerLinearProgram``
            is defined as a maximization.
          - When set to ``False``, the ``MixedIntegerLinearProgram`` is
            defined as a minimization.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram(maximization=True)
        """

        from sage.numerical.backends.generic_backend import get_solver
        self._backend = get_solver(solver = solver)

        if not maximization:
            self._backend.set_sense(-1)

        self.__BINARY = 0
        self.__REAL = -1
        self.__INTEGER = 1


        # List of all the MIPVariables linked to this instance of
        # MixedIntegerLinearProgram
        self._mipvariables = []

        # Associates an index to the variables
        self._variables = {}

    def __repr__(self):
         r"""
         Returns a short description of the ``MixedIntegerLinearProgram``.

         EXAMPLE::

             sage: p = MixedIntegerLinearProgram()
             sage: v = p.new_variable()
             sage: p.add_constraint(v[1] + v[2], max=2)
             sage: print p
             Mixed Integer Program ( maximization, 2 variables, 1 constraints )
         """
         cdef GenericBackend b = self._backend

         return ("Mixed Integer Program "+

                 ( "\"" +self._backend.problem_name()+ "\""
                   if (str(self._backend.problem_name()) != "") else "")+

                 " ( " + ("maximization" if b.is_maximization() else "minimization" ) +

                 ", " + str(b.ncols()) + " variables, " +
                 str(b.nrows()) + " constraints )")

    def __getitem__(self, v):
        r"""
        Returns the symbolic variable corresponding to the key
        from a default dictionary.

        It returns the element asked, and otherwise creates it.
        If necessary, it also creates the default dictionary.

        This method lets the user define LinearProgram without having to
        define independent dictionaries when it is not necessary for him.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: p.set_objective(p['x'] + p['z'])
            sage: p['x']
            x_0
        """

        try:
            return self._default_mipvariable[v]
        except TypeError:
            self._default_mipvariable = self.new_variable()
            return self._default_mipvariable[v]

    def set_problem_name(self,name):
        r"""
        Sets the name of the ``MixedIntegerLinearProgram``.

        INPUT:

        - ``name`` -- A string representing the name of the
          ``MixedIntegerLinearProgram``.

        EXAMPLE::

            sage: p=MixedIntegerLinearProgram()
            sage: p.set_problem_name("Test program")
            sage: p
            Mixed Integer Program "Test program" ( maximization, 0 variables, 0 constraints )
        """

        self._backend.problem_name(name)

    def _update_variables_name(self):
        r"""
        Updates the names of the variables.

        Only called before writing the Problem to a MPS or LP file.

        EXAMPLE::

            sage: p=MixedIntegerLinearProgram()
            sage: v=p.new_variable(name="Test")
            sage: v[5]+v[99]
            x_0 +x_1
            sage: p._update_variables_name()
        """

        for v in self._mipvariables:
            v._update_variables_name()


    def new_variable(self, real=False, binary=False, integer=False, dim=1,name=None):
        r"""
        Returns an instance of ``MIPVariable`` associated
        to the current instance of ``MixedIntegerLinearProgram``.

        A new variable ``x`` is defined by::

            sage: p = MixedIntegerLinearProgram()
            sage: x = p.new_variable()

        It behaves exactly as a usual dictionary would. It can use any key
        argument you may like, as ``x[5]`` or ``x["b"]``, and has methods
        ``items()`` and ``keys()``.

        Any of its fields exists, and is uniquely defined.

        INPUT:

        - ``dim`` (integer) -- Defines the dimension of the dictionary.
          If ``x`` has dimension `2`, its fields will be of the form
          ``x[key1][key2]``.

        - ``binary, integer, real`` (boolean) -- Set one of these arguments
          to ``True`` to ensure that the variable gets the corresponding
          type. The default type is ``real``.

        - ``name`` (string) -- Associates a name to the variable. This is
          only useful when exporting the linear program to a file using
          ``write_mps`` or ``write_lp``, and has no other effect.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()

         To define two dictionaries of variables, the first being
         of real type, and the second of integer type ::

            sage: x = p.new_variable(real=True)
            sage: y = p.new_variable(dim=2, integer=True)
            sage: p.add_constraint(x[2] + y[3][5], max=2)
            sage: p.is_integer(x[2])
            False
            sage: p.is_integer(y[3][5])
            True

        An exception is raised when two types are supplied ::

            sage: z = p.new_variable(real = True, integer = True)
            Traceback (most recent call last):
            ...
            ValueError: Exactly one of the available types has to be True
        """
        if name==None:
            name="V"+str(len(self._mipvariables))

        if sum([real, binary, integer]) >= 2:
            raise ValueError("Exactly one of the available types has to be True")

        if binary:
            vtype = self.__BINARY
        elif integer:
            vtype = self.__INTEGER
        else:
            vtype = self.__REAL

        v=MIPVariable(self, vtype, dim=dim,name=name)
        self._mipvariables.append(v)
        return v

    def show(self):
        r"""
        Displays the ``MixedIntegerLinearProgram`` in a human-readable
        way.

        EXAMPLES::

            sage: p = MixedIntegerLinearProgram()
            sage: x = p.new_variable()
            sage: p.set_objective(x[1] + x[2])
            sage: p.add_constraint(-3*x[1] + 2*x[2], max=2, name="Constraint_1")
            sage: p.show()
            Maximization:
               x_0 +x_1
            Constraints:
              Constraint_1: -3.0 x_0 +2.0 x_1 <= 2.0
            Variables:
              x_0 is a real variable (min=0.0, max=+oo)
              x_1 is a real variable (min=0.0, max=+oo)
        """

        cdef int i, j
        cdef double c
        cdef GenericBackend b = self._backend
        self._update_variables_name()

        inv_variables = [0]*len(self._variables)
        for (v,id) in self._variables.iteritems():
            inv_variables[id]=v

        value = ( "Maximization:\n"
                  if b.is_maximization()
                  else "Minimization:\n" )
        value+="  "

        first = True
        for 0<= i< b.ncols():
            c = b.get_objective_coefficient(i)
            if c != 0:

                value+= ((" +" if (not first and c>0) else " ") +
                         str(inv_variables[i]*b.get_objective_coefficient(i))
                         )
                first = False

        value += "\nConstraints:"


        for 0<= i < b.nrows():

            indices, values = b.row(i)

            lb, ub = b.row_bounds(i)

            value += ("\n  "+
                      (b.row_name(i)+": " if b.row_name(i)!="" else "")+
                      (str(lb)+" <= " if lb!=None else "")
                      )

            first = True

            for j,v in sorted(zip(indices, values)):

                value += (("+" if (not first and v>=0) else "") +
                          str(inv_variables[j]*v) +" ")

                first = False

            value += ("<= "+str(ub) if ub!=None else "")

        value += "\nVariables:"

        for 0<= i < b.ncols():
            value += "\n  " + str(inv_variables[i]) + " is"

            if b.is_variable_integer(i):
                value += " an integer variable"
            elif b.is_variable_binary(i):
                value += " an boolean variable"
            else:
                value += " a real variable"

            lb, ub = b.col_bounds(i)

            value += " (min=" + \
                ( str(lb)
                  if lb != None
                  else "-oo" ) + \
                ", max=" + \
                ( str(ub)
                  if ub != None
                  else "+oo" ) + \
                ")"
        print value

    def write_mps(self,filename,modern=True):
        r"""
        Write the linear program as a MPS file.

        This function export the problem as a MPS file.

        INPUT:

        - ``filename`` -- The file in which you want the problem
          to be written.

        - ``modern`` -- Lets you choose between Fixed MPS and Free MPS

            - ``True`` -- Outputs the problem in Free MPS
            - ``False`` -- Outputs the problem in Fixed MPS

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: x = p.new_variable()
            sage: p.set_objective(x[1] + x[2])
            sage: p.add_constraint(-3*x[1] + 2*x[2], max=2,name="OneConstraint")
            sage: p.write_mps(SAGE_TMP+"/lp_problem.mps")

        For information about the MPS file format :
        http://en.wikipedia.org/wiki/MPS_%28format%29
        """

        self._backend.write_mps(filename, modern)

    def write_lp(self,filename):
        r"""
        Write the linear program as a LP file.

        This function export the problem as a LP file.

        INPUT:

        - ``filename`` -- The file in which you want the problem
          to be written.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: x = p.new_variable()
            sage: p.set_objective(x[1] + x[2])
            sage: p.add_constraint(-3*x[1] + 2*x[2], max=2)
            sage: p.write_lp(SAGE_TMP+"/lp_problem.lp")

        For more information about the LP file format :
        http://lpsolve.sourceforge.net/5.5/lp-format.htm
        """

        self._backend.write_lp(filename)

    def get_values(self, *lists):
        r"""
        Return values found by the previous call to ``solve()``.

        INPUT:

        - Any instance of ``MIPVariable`` (or one of its elements),
          or lists of them.

        OUTPUT:

        - Each instance of ``MIPVariable`` is replaced by a dictionary
          containing the numerical values found for each
          corresponding variable in the instance.
        - Each element of an instance of a ``MIPVariable`` is replaced
          by its corresponding numerical value.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: x = p.new_variable()
            sage: y = p.new_variable(dim=2)
            sage: p.set_objective(x[3] + 3*y[2][9] + x[5])
            sage: p.add_constraint(x[3] + y[2][9] + 2*x[5], max=2)
            sage: p.solve()
            6.0

        To return  the optimal value of ``y[2][9]``::

            sage: p.get_values(y[2][9])
            2.0

        To get a dictionary identical to ``x`` containing optimal
        values for the corresponding variables ::

            sage: x_sol = p.get_values(x)
            sage: x_sol.keys()
            [3, 5]

        Obviously, it also works with variables of higher dimension::

            sage: y_sol = p.get_values(y)

        We could also have tried ::

            sage: [x_sol, y_sol] = p.get_values(x, y)

        Or::

            sage: [x_sol, y_sol] = p.get_values([x, y])
        """
        val = []
        for l in lists:
            if isinstance(l, MIPVariable):
                if l.depth() == 1:
                    c = {}
                    for (k,v) in l.items():
                        #c[k] = self._values[v] if self._values.has_key(v) else None
                        c[k] = self._backend.get_variable_value(self._variables[v])
                    val.append(c)
                else:
                    c = {}
                    for (k,v) in l.items():
                        c[k] = self.get_values(v)
                    val.append(c)
            elif isinstance(l, list):
                if len(l) == 1:
                    val.append([self.get_values(l[0])])
                else:
                    c = []
                    [c.append(self.get_values(ll)) for ll in l]
                    val.append(c)
            elif self._variables.has_key(l):
                #val.append(self._values[l])
                val.append(self._backend.get_variable_value(self._variables[l]))
        if len(lists) == 1:
            return val[0]
        else:
            return val

    def set_objective(self,obj):
        r"""
        Sets the objective of the ``MixedIntegerLinearProgram``.

        INPUT:

        - ``obj`` -- A linear function to be optimized.
          ( can also be set to ``None`` or ``0`` when just
          looking for a feasible solution )

        EXAMPLE:

        Let's solve the following linear program::

            Maximize:
              x + 5 * y
            Constraints:
              x + 0.2 y       <= 4
              1.5 * x + 3 * y <= 4
            Variables:
              x is Real (min = 0, max = None)
              y is Real (min = 0, max = None)

        This linear program can be solved as follows::

            sage: p = MixedIntegerLinearProgram(maximization=True)
            sage: x = p.new_variable()
            sage: p.set_objective(x[1] + 5*x[2])
            sage: p.add_constraint(x[1] + 2/10*x[2], max=4)
            sage: p.add_constraint(1.5*x[1]+3*x[2], max=4)
            sage: round(p.solve(),5)
            6.66667
            sage: p.set_objective(None)
            sage: p.solve()
            0.0
        """

        cdef list values = []

        # If the objective is None, or a constant, we want to remember
        # that the objective function has been defined ( the user did not
        # forget it ). In some LP problems, you just want a feasible solution
        # and do not care about any function being optimal.

        cdef int i

        if obj != None:
            f = obj.dict()
        else:
            f = {-1 : 0}

        f.pop(-1,0)

        for i in range(self._backend.ncols()):
            values.append(f.get(i,0))

        self._backend.set_objective(values)

    def add_constraint(self, linear_function, max=None, min=None, name=None):
        r"""
        Adds a constraint to self.

        INPUT:

        - ``linear_function`` -- Two different types of arguments are possible:
            - A linear function. In this case, arguments ``min`` or ``max``
              have to be specified.
            - A linear constraint of the form ``A <= B``, ``A >= B``,
              ``A <= B <= C``, ``A >= B >= C`` or ``A == B``. In this
              case, arguments ``min`` and ``max`` will be ignored.
        - ``max`` -- An upper bound on the constraint (set to ``None``
          by default). This must be a numerical value.
        - ``min`` -- A lower bound on the constraint.  This must be a
          numerical value.
        - ``name`` -- A name for the constraint.

        EXAMPLE:

        Consider the following linear program::

            Maximize:
              x + 5 * y
            Constraints:
              x + 0.2 y       <= 4
              1.5 * x + 3 * y <= 4
            Variables:
              x is Real (min = 0, max = None)
              y is Real (min = 0, max = None)

        It can be solved as follows::

            sage: p = MixedIntegerLinearProgram(maximization=True)
            sage: x = p.new_variable()
            sage: p.set_objective(x[1] + 5*x[2])
            sage: p.add_constraint(x[1] + 0.2*x[2], max=4)
            sage: p.add_constraint(1.5*x[1] + 3*x[2], max=4)
            sage: round(p.solve(),6)
            6.666667

        There are two different ways to add the constraint
        ``x[5] + 3*x[7] <= x[6] + 3`` to self.

        The first one consists in giving ``add_constraint`` this
        very expression::

            sage: p.add_constraint( x[5] + 3*x[7] <= x[6] + 3 )

        The second (slightly more efficient) one is to use the
        arguments ``min`` or ``max``, which can only be numerical
        values::

            sage: p.add_constraint( x[5] + 3*x[7] - x[6], max = 3 )

        One can also define double-bounds or equality using symbols
        ``<=``, ``>=`` and ``==``::

            sage: p.add_constraint( x[5] + 3*x[7] == x[6] + 3 )
            sage: p.add_constraint( x[5] + 3*x[7] <= x[6] + 3 <= x[8] + 27 )

        The previous program can be rewritten::

            sage: p = MixedIntegerLinearProgram(maximization=True)
            sage: x = p.new_variable()
            sage: p.set_objective(x[1] + 5*x[2])
            sage: p.add_constraint(x[1] + 0.2*x[2] <= 4)
            sage: p.add_constraint(1.5*x[1] + 3*x[2] <= 4)
            sage: round(p.solve(), 5)
            6.66667

        TESTS::

            sage: p=MixedIntegerLinearProgram()
            sage: p.add_constraint(sum([]),min=2)

        Min/Max are numerical ::

            sage: v = p.new_variable()
            sage: p.add_constraint(v[3] + v[5], min = v[6])
            Traceback (most recent call last):
            ...
            ValueError: min and max arguments are required to be numerical
            sage: p.add_constraint(v[3] + v[5], max = v[6])
            Traceback (most recent call last):
            ...
            ValueError: min and max arguments are required to be numerical

        """
        if linear_function is None or linear_function is 0:
            return None

        # Raising an exception when min/max are not as expected
        from sage.rings.all import RR
        if ((min is not None and min not in RR)
            or (max is not None and max not in RR)):

            raise ValueError("min and max arguments are required to be numerical")

        if isinstance(linear_function, LinearFunction):

            f = linear_function.dict()

            constant_coefficient = f.get(-1,0)

            # We do not want to ignore the constant coefficient
            max = (max - constant_coefficient) if max != None else None
            min = (min - constant_coefficient) if min != None else None

            indices = []
            values = []

            for (v,coeff) in f.iteritems():
                if v != -1:
                    indices.append(v)
                    values.append(coeff)

            if min == None and max == None:
                raise ValueError("Both max and min are set to None ? Weird !")
            elif min == max:
                self._backend.add_linear_constraint(indices, values, 0, min)
            elif min != None:
                self._backend.add_linear_constraint(indices, values, -1, min)
            elif max != None:
                self._backend.add_linear_constraint(indices, values, +1, max)

            if name != None:
                self._backend.row_name(self._backend.nrows()-1,name)

        elif isinstance(linear_function,LinearConstraint):
            functions = linear_function.constraints

            if linear_function.equality:
                self.add_constraint(functions[0] - functions[1], min=0, max=0, name=name)

            elif len(functions) == 2:
                self.add_constraint(functions[0] - functions[1], max=0, name=name)

            else:
                self.add_constraint(functions[0] - functions[1], max=0, name=name)
                self.add_constraint(functions[1] - functions[2], max=0, name=name)

    def set_binary(self, ee):
        r"""
        Sets a variable or a ``MIPVariable`` as binary.

        INPUT:

        - ``ee`` -- An instance of ``MIPVariable`` or one of
          its elements.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: x = p.new_variable()

        With the following instruction, all the variables
        from x will be binary::

            sage: p.set_binary(x)
            sage: p.set_objective(x[0] + x[1])
            sage: p.add_constraint(-3*x[0] + 2*x[1], max=2)

        It is still possible, though, to set one of these
        variables as real while keeping the others as they are::

            sage: p.set_real(x[3])
        """
        cdef MIPVariable e
        e = <MIPVariable> ee

        if isinstance(e, MIPVariable):
            e._vtype = self.__BINARY
            if e.depth() == 1:
                for v in e.values():
                    self._backend.set_variable_type(self._variables[v],self.__BINARY)
            else:
                for v in e.keys():
                    self.set_binary(e[v])
        elif self._variables.has_key(e):
            self._backend.set_variable_type(self._variables[e],self.__BINARY)
        else:
            raise ValueError("e must be an instance of MIPVariable or one of its elements.")

    def is_binary(self, e):
        r"""
        Tests whether the variable ``e`` is binary. Variables are real by
        default.

        INPUT:

        - ``e`` -- A variable (not a ``MIPVariable``, but one of its elements.)

        OUTPUT:

        ``True`` if the variable ``e`` is binary; ``False`` otherwise.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[1])
            sage: p.is_binary(v[1])
            False
            sage: p.set_binary(v[1])
            sage: p.is_binary(v[1])
            True
        """

        return self._backend.is_variable_binary(self._variables[e])

    def set_integer(self, ee):
        r"""
        Sets a variable or a ``MIPVariable`` as integer.

        INPUT:

        - ``ee`` -- An instance of ``MIPVariable`` or one of
          its elements.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: x = p.new_variable()

        With the following instruction, all the variables
        from x will be integers::

            sage: p.set_integer(x)
            sage: p.set_objective(x[0] + x[1])
            sage: p.add_constraint(-3*x[0] + 2*x[1], max=2)

        It is still possible, though, to set one of these
        variables as real while keeping the others as they are::

            sage: p.set_real(x[3])
        """
        cdef MIPVariable e
        e = <MIPVariable> ee

        if isinstance(e, MIPVariable):
            e._vtype = self.__INTEGER
            if e.depth() == 1:
                for v in e.values():
                    self._backend.set_variable_type(self._variables[v],self.__INTEGER)
            else:
                for v in e.keys():
                    self.set_integer(e[v])
        elif self._variables.has_key(e):
            self._backend.set_variable_type(self._variables[e],self.__INTEGER)
        else:
            raise ValueError("e must be an instance of MIPVariable or one of its elements.")

    def is_integer(self, e):
        r"""
        Tests whether the variable is an integer. Variables are real by
        default.

        INPUT:

        - ``e`` -- A variable (not a ``MIPVariable``, but one of its elements.)

        OUTPUT:

        ``True`` if the variable ``e`` is an integer; ``False`` otherwise.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[1])
            sage: p.is_integer(v[1])
            False
            sage: p.set_integer(v[1])
            sage: p.is_integer(v[1])
            True
        """

        return self._backend.is_variable_integer(self._variables[e])

    def set_real(self,ee):
        r"""
        Sets a variable or a ``MIPVariable`` as real.

        INPUT:

        - ``ee`` -- An instance of ``MIPVariable`` or one of
          its elements.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: x = p.new_variable()

        With the following instruction, all the variables
        from x will be real (they are by default, though)::

            sage: p.set_real(x)
            sage: p.set_objective(x[0] + x[1])
            sage: p.add_constraint(-3*x[0] + 2*x[1], max=2)

         It is still possible, though, to set one of these
         variables as binary while keeping the others as they are::

            sage: p.set_binary(x[3])
        """

        cdef MIPVariable e
        e = <MIPVariable> ee

        if isinstance(e, MIPVariable):
            e._vtype = self.__REAL
            if e.depth() == 1:
                for v in e.values():
                    self._backend.set_variable_type(self._variables[v],self.__REAL)
            else:
                for v in e.keys():
                    self.set_real(e[v])
        elif self._variables.has_key(e):
            self._backend.set_variable_type(self._variables[e],self.__REAL)
        else:
            raise ValueError("e must be an instance of MIPVariable or one of its elements.")

    def is_real(self, e):
        r"""
        Tests whether the variable is real. Variables are real by default.

        INPUT:

        - ``e`` -- A variable (not a ``MIPVariable``, but one of its elements.)

        OUTPUT:

        ``True`` if the variable is real; ``False`` otherwise.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[1])
            sage: p.is_real(v[1])
            True
            sage: p.set_binary(v[1])
            sage: p.is_real(v[1])
            False
            sage: p.set_real(v[1])
            sage: p.is_real(v[1])
            True
        """

        return self._backend.is_variable_continuous(self._variables[e])

    def solve(self, solver=None, log=0, objective_only=False):
        r"""
        Solves the ``MixedIntegerLinearProgram``.

        INPUT:

        - ``solver`` -- DEPRECATED -- the solver now has to be set
          when calling the class' constructor

        - ``log`` -- integer (default: ``0``) The verbosity level. Indicates
          whether progress should be printed during computation.

        - ``objective_only`` -- Boolean variable.

          - When set to ``True``, only the objective function is returned.
          - When set to ``False`` (default), the optimal numerical values
            are stored (takes computational time).

        OUTPUT:

        The optimal value taken by the objective function.

        EXAMPLES:

        Consider the following linear program::

            Maximize:
              x + 5 * y
            Constraints:
              x + 0.2 y       <= 4
              1.5 * x + 3 * y <= 4
            Variables:
              x is Real (min = 0, max = None)
              y is Real (min = 0, max = None)

        This linear program can be solved as follows::

            sage: p = MixedIntegerLinearProgram(maximization=True)
            sage: x = p.new_variable()
            sage: p.set_objective(x[1] + 5*x[2])
            sage: p.add_constraint(x[1] + 0.2*x[2], max=4)
            sage: p.add_constraint(1.5*x[1] + 3*x[2], max=4)
            sage: round(p.solve(),6)
            6.666667
            sage: x = p.get_values(x)
            sage: round(x[1],6)
            0.0
            sage: round(x[2],6)
            1.333333

         Computation of a maximum stable set in Petersen's graph::

            sage: g = graphs.PetersenGraph()
            sage: p = MixedIntegerLinearProgram(maximization=True)
            sage: b = p.new_variable()
            sage: p.set_objective(sum([b[v] for v in g]))
            sage: for (u,v) in g.edges(labels=None):
            ...       p.add_constraint(b[u] + b[v], max=1)
            sage: p.set_binary(b)
            sage: p.solve(objective_only=True)
            4.0
        """

        if solver != None:
            raise ValueError("Solver argument deprecated. This parameter now has to be set when calling the class' constructor")

        self._backend.set_verbosity(log)

        self._backend.solve()

        return self._backend.get_objective_value()


    def _add_element_to_ring(self, vtype):
        r"""
        Creates a new variable in the (Mixed) Integer Linear Program.

        INPUT:

        - ``vtype`` (integer) -- Defines the type of the variables
          (default is ``REAL``).

        OUTPUT:

        - The newly created variable.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: print p
            Mixed Integer Program  ( maximization, 0 variables, 0 constraints )
            sage: p._add_element_to_ring(-1)
            x_0
            sage: print p
            Mixed Integer Program  ( maximization, 1 variables, 0 constraints )
        """

        v = LinearFunction({len(self._variables) : 1})

        self._variables[v] = len(self._variables)
        self._backend.add_variable()
        self._backend.set_variable_type(self._backend.ncols()-1,vtype)
        return v

    def set_min(self, v, min):
        r"""
        Sets the minimum value of a variable.

        INPUT:

        - ``v`` -- a variable (not a ``MIPVariable``, but one of its
          elements).
        - ``min`` -- the minimum value the variable can take.
          When ``min=None``, the variable has no lower bound.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[1])
            sage: p.get_min(v[1])
            0.0
            sage: p.set_min(v[1],6)
            sage: p.get_min(v[1])
            6.0
        """
        self._backend.variable_min(self._variables[v], min)

    def set_max(self, v, max):
        r"""
        Sets the maximum value of a variable.

        INPUT

        - ``v`` -- a variable (not a ``MIPVariable``, but one of its
          elements).
        - ``max`` -- the maximum value the variable can take.
          When ``max=None``, the variable has no upper bound.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[1])
            sage: p.get_max(v[1])
            sage: p.set_max(v[1],6)
            sage: p.get_max(v[1])
            6.0
        """

        self._backend.variable_max(self._variables[v], max)

    def get_min(self, v):
        r"""
        Returns the minimum value of a variable.

        INPUT:

        - ``v`` -- a variable (not a ``MIPVariable``, but one of its elements).

        OUTPUT:

        Minimum value of the variable, or ``None`` if
        the variable has no lower bound.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[1])
            sage: p.get_min(v[1])
            0.0
            sage: p.set_min(v[1],6)
            sage: p.get_min(v[1])
            6.0
        """

        return self._backend.variable_min(self._variables[v])

    def get_max(self, v):
        r"""
        Returns the maximum value of a variable.

        INPUT:

        - ``v`` -- a variable (not a ``MIPVariable``, but one of its elements).

        OUTPUT:

        Maximum value of the variable, or ``None`` if
        the variable has no upper bound.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[1])
            sage: p.get_max(v[1])
            sage: p.set_max(v[1],6)
            sage: p.get_max(v[1])
            6.0
        """

        return self._backend.variable_max(self._variables[v])

class MIPSolverException(Exception):
    r"""
    Exception raised when the solver fails.
    """

    def __init__(self, value):
        r"""
        Constructor for ``MIPSolverException``.

        ``MIPSolverException`` is the exception raised when the solver fails.

        EXAMPLE::

            sage: from sage.numerical.mip import MIPSolverException
            sage: MIPSolverException("Error")
            MIPSolverException()

        TESTS:

         No continuous solution::

            sage: p=MixedIntegerLinearProgram(solver="GLPK")
            sage: v=p.new_variable()
            sage: p.add_constraint(v[0],max=5.5)
            sage: p.add_constraint(v[0],min=7.6)
            sage: p.set_objective(v[0])

         Tests of GLPK's Exceptions::

            sage: p.solve()
            Traceback (most recent call last):
            ...
            MIPSolverException: 'GLPK : Solution is undefined'

         No integer solution::

            sage: p=MixedIntegerLinearProgram(solver="GLPK")
            sage: v=p.new_variable()
            sage: p.add_constraint(v[0],max=5.6)
            sage: p.add_constraint(v[0],min=5.2)
            sage: p.set_objective(v[0])
            sage: p.set_integer(v)

         Tests of GLPK's Exceptions::

            sage: p.solve()
            Traceback (most recent call last):
            ...
            MIPSolverException: 'GLPK : Solution is undefined'
        """
        self.value = value

    def __str__(self):
        r"""
        Returns the value of the instance of ``MIPSolverException``.

        EXAMPLE::

            sage: from sage.numerical.mip import MIPSolverException
            sage: e = MIPSolverException("Error")
            sage: print e
            'Error'
        """
        return repr(self.value)

cdef class MIPVariable:
    r"""
    ``MIPVariable`` is a variable used by the class
    ``MixedIntegerLinearProgram``.
    """

    def __init__(self, p, vtype, dim=1, name=""):
        r"""
        Constructor for ``MIPVariable``.

        INPUT:

        - ``p`` -- the instance of ``MixedIntegerLinearProgram`` to which the
          variable is to be linked.
        - ``vtype`` (integer) -- Defines the type of the variables
          (default is ``REAL``).
        - ``dim`` -- the integer defining the definition of the variable.
        - ``name`` -- A name for the ``MIPVariable``.

        For more informations, see the method
        ``MixedIntegerLinearProgram.new_variable``.

        EXAMPLE::

            sage: p=MixedIntegerLinearProgram()
            sage: v=p.new_variable()
        """
        self._dim = dim
        self._dict = {}
        self._p = p
        self._vtype = vtype

        #####################################################
        self._name="x"


    def __getitem__(self, i):
        r"""
        Returns the symbolic variable corresponding to the key.

        Returns the element asked, otherwise creates it.
        (When depth>1, recursively creates the variables).

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[0] + v[1])
            sage: v[0]
            x_0
        """
        if self._dict.has_key(i):
            return self._dict[i]
        elif self._dim == 1:
            self._dict[i] = self._p._add_element_to_ring(self._vtype)
            return self._dict[i]
        else:
            self._dict[i] = MIPVariable(self._p, self._vtype, dim=self._dim-1)
            return self._dict[i]

    def _update_variables_name(self, prefix=None):
        r"""
        Updates the names of the variables in the parent instant of ``MixedIntegerLinearProgram``.

        Only called before writing the Problem to a MPS or LP file.

        EXAMPLE::

            sage: p=MixedIntegerLinearProgram()
            sage: v=p.new_variable(name="Test")
            sage: v[5]+v[99]
            x_0 +x_1
            sage: v._update_variables_name()
        """

        if prefix == None:
            prefix = self._name

        if self._dim == 1:
            for (k,v) in self._dict.iteritems():
                name = prefix + "[" + str(k) + "]"
                self._p._backend.col_name(self._p._variables[v], name)
                #self._p._variables_name[self._p._variables[v]]=prefix + "[" + str(k) + "]"
        else:
            for v in self._dict.itervalues():
                v._update_variables_name(prefix=prefix + "(" + str(k) + ")")



    def __repr__(self):
        r"""
        Returns a representation of self.

        EXAMPLE::

            sage: p=MixedIntegerLinearProgram()
            sage: v=p.new_variable(dim=3)
            sage: v
            MIPVariable of dimension 3.
            sage: v[2][5][9]
            x_0
            sage: v
            MIPVariable of dimension 3.
        """
        return "MIPVariable of dimension " + str(self._dim) + "."

    def keys(self):
        r"""
        Returns the keys already defined in the dictionary.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[0] + v[1])
            sage: v.keys()
            [0, 1]
        """
        return self._dict.keys()

    def items(self):
        r"""
        Returns the pairs (keys,value) contained in the dictionary.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[0] + v[1])
            sage: v.items()
            [(0, x_0), (1, x_1)]
        """
        return self._dict.items()

    def depth(self):
        r"""
        Returns the current variable's depth.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[0] + v[1])
            sage: v.depth()
            1
        """
        return self._dim

    def values(self):
        r"""
        Returns the symbolic variables associated to the current dictionary.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: v = p.new_variable()
            sage: p.set_objective(v[0] + v[1])
            sage: v.values()
            [x_0, x_1]
        """
        return self._dict.values()


class LinearFunction:
    r"""
    An elementary algebra to represent symbolic linear functions.
    """

    def __init__(self,f):
        r"""
        Constructor taking a dictionary or a numerical value as its argument.

        A linear function is represented as a dictionary. The
        values are the coefficient of the variable represented
        by the keys ( which are integers ). The key ``-1``
        corresponds to the constant term.

        EXAMPLES:

        With a dictionary::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({0 : 1, 3 : -8})
            x_0 -8 x_3

        Using the constructor with a numerical value::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction(25)
            25
        """
        if isinstance(f, dict):
            self._f = f
        else:
            self._f = {-1:f}

    def dict(self):
        r"""
        Returns the dictionary corresponding to the Linear Function.

        A linear function is represented as a dictionary. The
        value are the coefficient of the variable represented
        by the keys ( which are integers ). The key ``-1``
        corresponds to the constant term.

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: lf = LinearFunction({0 : 1, 3 : -8})
            sage: lf.dict()
            {0: 1, 3: -8}
        """
        return self._f

    def __add__(self,b):
        r"""
        Defining the + operator

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({0 : 1, 3 : -8}) + LinearFunction({2 : 5, 3 : 2}) - 16
            -16 +x_0 +5 x_2 -6 x_3
        """
        if isinstance(b, LinearFunction):
            e = deepcopy(self._f)
            for (id,coeff) in b.dict().iteritems():
                e[id] = self._f.get(id,0) + coeff
            return LinearFunction(e)
        else:
            el = deepcopy(self)
            el.dict()[-1] = el.dict().get(-1,0) + b
            return el

    def __neg__(self):
        r"""
        Defining the - operator (opposite).

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: -LinearFunction({0 : 1, 3 : -8})
            -1 x_0 +8 x_3
        """
        return LinearFunction(dict([(id,-coeff) for (id, coeff) in self._f.iteritems()]))

    def __sub__(self,b):
        r"""
        Defining the - operator (substraction).

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({2 : 5, 3 : 2}) - 3
            -3 +5 x_2 +2 x_3
            sage: LinearFunction({0 : 1, 3 : -8}) - LinearFunction({2 : 5, 3 : 2}) - 16
            -16 +x_0 -5 x_2 -10 x_3
        """
        if isinstance(b, LinearFunction):
            e = deepcopy(self._f)
            for (id,coeff) in b.dict().iteritems():
                e[id] = self._f.get(id,0) - coeff
            return LinearFunction(e)
        else:
            el = deepcopy(self)
            el.dict()[-1] = self._f.get(-1,0) - b
            return el

    def __radd__(self,b):
        r"""
        Defining the + operator (right side).

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: 3 + LinearFunction({2 : 5, 3 : 2})
            3 +5 x_2 +2 x_3
        """
        if isinstance(self,LinearFunction):
            return self.__add__(b)
        else:
            return b.__add__(self)

    def __rsub__(self,b):
        r"""
        Defining the - operator (right side).

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: 3 - LinearFunction({2 : 5, 3 : 2})
            3 -5 x_2 -2 x_3
        """
        if isinstance(self,LinearFunction):
            return (-self).__add__(b)
        else:
            return b.__sub__(self)

    def __mul__(self,b):
        r"""
        Defining the * operator.

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({2 : 5, 3 : 2}) * 3
            15 x_2 +6 x_3
        """
        return LinearFunction(dict([(id,b*coeff) for (id, coeff) in self._f.iteritems()]))

    def __rmul__(self,b):
        r"""
        Defining the * operator (right side).

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: 3 * LinearFunction({2 : 5, 3 : 2})
            15 x_2 +6 x_3
        """
        return self.__mul__(b)

    def __repr__(self):
        r"""
        Returns a string version of the linear function.

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({2 : 5, 3 : 2})
            5 x_2 +2 x_3
        """
        cdef dict d = deepcopy(self._f)
        cdef bint first = True
        t = ""

        if d.has_key(-1):
            coeff = d.pop(-1)
            if coeff!=0:
                t = str(coeff)
                first = False

        cdef list l = sorted(d.items())
        for id,coeff in l:
            if coeff!=0:
                if not first:
                    t += " "
                t += ("+" if (not first and coeff >= 0) else "") + (str(coeff) + " " if coeff != 1 else "") + "x_" + str(id)
                first = False
        return t

    def __le__(self,other):
        r"""
        Defines the <= operator

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({2 : 5, 3 : 2}) <= LinearFunction({2 : 3, 9 : 2})
            5 x_2 +2 x_3 <= 3 x_2 +2 x_9
        """
        return LinearConstraint(self).__le__(other)

    def __lt__(self,other):
        r"""
        Defines the < operator

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({2 : 5, 3 : 2}) < LinearFunction({2 : 3, 9 : 2})
            Traceback (most recent call last):
            ...
            ValueError: The strict operators are not defined. Use <= and >= instead.
        """
        return LinearConstraint(self).__lt__(other)

    def __gt__(self,other):
        r"""
        Defines the > operator

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({2 : 5, 3 : 2}) > LinearFunction({2 : 3, 9 : 2})
            Traceback (most recent call last):
            ...
            ValueError: The strict operators are not defined. Use <= and >= instead.
        """
        return LinearConstraint(self).__gt__(other)


    def __ge__(self,other):
        r"""
        Defines the >= operator

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({2 : 5, 3 : 2}) >= LinearFunction({2 : 3, 9 : 2})
            3 x_2 +2 x_9 <= 5 x_2 +2 x_3
        """
        return LinearConstraint(self).__ge__(other)

    def __hash__(self):
        r"""
        Defines a ``__hash__`` function

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: d = {}
            sage: d[LinearFunction({2 : 5, 3 : 2})] = 3
        """
        return id(self)

    def __eq__(self,other):
        r"""
        Defines the == operator

        EXAMPLE::

            sage: from sage.numerical.mip import LinearFunction
            sage: LinearFunction({2 : 5, 3 : 2}) == LinearFunction({2 : 3, 9 : 2})
            5 x_2 +2 x_3 = 3 x_2 +2 x_9
        """
        return LinearConstraint(self).__eq__(other)

def Sum(L):
    r"""
    Efficiently computes the sum of a sequence of
    ``LinearFunction`` elements

    INPUT:

    - ``L`` a list of ``LinearFunction`` instances.

    .. NOTE::

        The use of the regular ``sum`` function is not recommended as it is much less efficient than this one.

    EXAMPLES::

        sage: p = MixedIntegerLinearProgram()
        sage: v = p.new_variable()

    The following command::

        sage: from sage.numerical.mip import Sum
        sage: s = Sum([v[i] for i in xrange(90)])

    is much more efficient than::

        sage: s = sum([v[i] for i in xrange(90)])

    """

    d = {}
    for v in L:
        for (id,coeff) in v._f.iteritems():
            d[id] = coeff + d.get(id,0)

    return LinearFunction(d)



class LinearConstraint:
    """
    A class to represent formal Linear Constraints.

    A Linear Constraint being an inequality between
    two linear functions, this class lets the user
    write ``LinearFunction1 <= LinearFunction2``
    to define the corresponding constraint, which
    can potentially involve several layers of such
    inequalities (``(A <= B <= C``), or even equalities
    like ``A == B``.

    This class has no reason to be instanciated by the
    user, and is meant to be used by instances of
    MixedIntegerLinearProgram.

    INPUT:

    - ``c`` -- A ``LinearFunction``

    EXAMPLE::

        sage: p = MixedIntegerLinearProgram()
        sage: b = p.new_variable()
        sage: b[2]+2*b[3] <= b[8]-5
        x_0 +2 x_1 <= -5 +x_2
    """

    def __init__(self, c):
        r"""
        Constructor for ``LinearConstraint``

        INPUT:

        - ``c`` -- A linear function (see ``LinearFunction``).

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: b = p.new_variable()
            sage: b[2]+2*b[3] <= b[8]-5
            x_0 +2 x_1 <= -5 +x_2
        """
        self.equality = False
        self.constraints = []
        if isinstance(c, LinearFunction):
            self.constraints.append(c)
        else:
            self.constraints.append(LinearFunction(c))

    def __repr__(self):
        r"""
        Returns a string representation of the constraint.

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: b = p.new_variable()
            sage: print b[3] <= b[8] + 9
            x_0 <= 9 +x_1
        """
        if self.equality:
            return str(self.constraints[0]) + " = " + str(self.constraints[1])
        else:
            first = True
            s = ""
            for c in self.constraints:
                s += (" <= " if not first else "") + c.__repr__()
                first = False
            return s

    def __eq__(self,other):
        r"""
        Defines the == operator

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: b = p.new_variable()
            sage: print b[3] == b[8] + 9
            x_0 = 9 +x_1
        """
        if not isinstance(other, LinearConstraint):
            other = LinearConstraint(other)

        if len(self.constraints) == 1 and len(other.constraints) == 1:
            self.constraints.extend(other.constraints)
            self.equality = True
            return self
        else:
            raise ValueError("Impossible to mix equality and inequality in the same equation")

    def __le__(self,other):
        r"""
        Defines the <= operator

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: b = p.new_variable()
            sage: print b[3] <= b[8] + 9
            x_0 <= 9 +x_1
        """

        if not isinstance(other, LinearConstraint):
            other = LinearConstraint(other)

        if self.equality or other.equality:
            raise ValueError("Impossible to mix equality and inequality in the same equation")

        self.constraints.extend(other.constraints)
        return self

    def __lt__(self, other):
        r"""
        Prevents the use of the stricts operators ``<`` and ``>``

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: b = p.new_variable()
            sage: print b[3] < b[8] + 9
            Traceback (most recent call last):
            ...
            ValueError: The strict operators are not defined. Use <= and >= instead.
            sage: print b[3] > b[8] + 9
            Traceback (most recent call last):
            ...
            ValueError: The strict operators are not defined. Use <= and >= instead.
        """
        raise ValueError("The strict operators are not defined. Use <= and >= instead.")

    __gt__ = __lt__

    def __ge__(self,other):
        r"""
        Defines the >= operator

        EXAMPLE::

            sage: p = MixedIntegerLinearProgram()
            sage: b = p.new_variable()
            sage: print b[3] >= b[8] + 9
            9 +x_1 <= x_0
        """
        if not isinstance(other, LinearConstraint):
            other = LinearConstraint(other)

        if self.equality or other.equality:
            raise ValueError("Impossible to mix equality and inequality in the same equation")

        self.constraints = other.constraints + self.constraints
        return self
