include '../../../../devel/sage/sage/ext/stdsage.pxi'

cdef int BINARY = 1
cdef int REAL = -1
cdef int INTEGER = 0


def solve_coin(self,log=0,objective_only=False, threads = 0):
    r"""
    Solves the ``MixedIntegerLinearProgram`` using COIN-OR CBC/CLP
    *Use ``solve()`` instead*

    INPUT:

    - ``log`` (integer) -- level of verbosity during the
      solving process. Set ``log=3`` for maximal verbosity and
      ``log=0`` for no verbosity at all.

    - ``objective_only`` (boolean) -- Indicates whether the
      values corresponding to an optimal assignment of the
      variables should be computed. Setting ``objective_only``
      to ``True`` saves some time on the computation when
      this information is not needed.

    - ``threads`` -- Number of threads to use. Set ``threads``
      to 0 (its default value) to use one thread per core available.


    OUTPUT:

    This function returns the optimal value of the objective
    function given by Coin.

    EXAMPLE:

    Solving a simple Linear Program using Coin as a solver
    (Computation of a maximum stable set in Petersen's graph)::

        sage: from sage.numerical.mip_coin import solve_coin     # optional - CBC
        sage: g = graphs.PetersenGraph()
        sage: p = MixedIntegerLinearProgram(maximization=True)
        sage: b = p.new_variable()
        sage: p.set_objective(sum([b[v] for v in g]))
        sage: for (u,v) in g.edges(labels=None):
        ...       p.add_constraint(b[u] + b[v], max=1)
        sage: p.set_binary(b)
        sage: solve_coin(p,objective_only=True)     # optional - CBC
        4.0
    """
    # Creates the solver interfaces
    cdef c_OsiCbcSolverInterface* si
    si = new_c_OsiCbcSolverInterface();

    # stuff related to the loglevel
    cdef c_CoinMessageHandler * msg
    cdef c_CbcModel * model
    model = si.getModelPtr()
    if threads == 0:
        import multiprocessing
        model.setNumberThreads(multiprocessing.cpu_count())
    else:
        model.setNumberThreads(threads)


    msg = model.messageHandler()
    msg.setLogLevel(log)

    from sage.numerical.mip import MIPSolverException

    cdef Osi_interface OSI
    OSI = Osi_interface()


    return_value = OSI.osi_solve(self, <c_OsiSolverInterface *> si, objective_only, False)
    del_OsiCbcSolverInterface(si)

    return return_value
