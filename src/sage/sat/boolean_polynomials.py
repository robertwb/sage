"""
SAT Functions for Boolean Polynomials

AUTHOR:

- Martin Albrecht (2012): initial version

"""
from sage.structure.sequence import Sequence
from sage.rings.infinity import PlusInfinity

def solve(F, Converter=None, Solver=None, n=1, **kwds):
    """
    Solve system of Boolean polynomials ``F`` by solving the
    SAT-problem -- produced by an instance of ``Converter`` -- using
    an instance of ``Solver``.

    INPUT:

    - ``F`` - a sequence of Boolean polynomials

    - ``n`` - number of solutions to return. If ``n`` is +infinity
      then all solutions are returned. If ``n <infinity`` then ``n``
      solutions are returned if ``F`` has at least ``n``
      solutions. Otherwise, all solutions of ``F`` are
      returned. (default: ``1``)

    - ``Converter`` - an ANF to CNF converter class.  If ``Converter``
      is ``None`` then :cls:`sage.sat.converters.polybori.CNFEncoder`
      is used. (default: ``None``)

    - ``Solver`` - a SAT-solver class If ``Solver`` is ``None`` then
      cls:`sage.sat.solvers.cryptominisat.CryptoMiniSat` is used.
      (default: ``None``)

    - ``**kwds`` - parameters can be passed to the converter and the
       solver by prefixing them with 'c_' and 's_' respectively. For
       example, to increase CryptoMiniSat's verbosity level, pass
       ``s_verbosity=1``.

    OUTPUT:

        A list of dictionaries, each of which contains a variable
        assignment solving ``F``.

    EXAMPLE:

    We construct a very small-scale AES system of equations::

        sage: sr = mq.SR(1,1,1,4,gf2=True,polybori=True)
        sage: F,s = sr.polynomial_system()

    and pass it to a SAT solver::

        sage: from sage.sat.boolean_polynomials import solve as solve_sat # optional - cryptominisat
        sage: s = solve_sat(F)                                            # optional - cryptominisat
        sage: F.subs(s[0])                                                 # optional - cryptominisat
        Polynomial Sequence with 36 Polynomials in 0 Variables

    This time we pass a few options through to the converter and the solver::

        sage: s = solve_sat(F, s_verbosity=1, c_max_variables=4, c_cutting_number=8) # optional - cryptominisat
        sage: F.subs(s[0])                                                           # optional - cryptominisat
        Polynomial Sequence with 36 Polynomials in 0 Variables

    We construct a very simple system with three solutions and ask for a specific number of solutions::

        sage: B.<a,b> = BooleanPolynomialRing() # optional - cryptominisat
        sage: f = a*b                           # optional - cryptominisat
        sage: l = solve_sat([f],n=1)            # optional - cryptominisat
        sage: len(l) == 1, f.subs(l[0])         # optional - cryptominisat
        (True, 0)

        sage: l = sorted(solve_sat([a*b],n=2))        # optional - cryptominisat
        sage: len(l) == 2, f.subs(l[0]), f.subs(l[1]) # optional - cryptominisat
        (True, 0, 0)

        sage: sorted(solve_sat([a*b],n=3))         # optional - cryptominisat
        [{b: 0, a: 0}, {b: 0, a: 1}, {b: 1, a: 0}]
        sage: sorted(solve_sat([a*b],n=4))         # optional - cryptominisat
        [{b: 0, a: 0}, {b: 0, a: 1}, {b: 1, a: 0}]
        sage: sorted(solve_sat([a*b],n=infinity))  # optional - cryptominisat
        [{b: 0, a: 0}, {b: 0, a: 1}, {b: 1, a: 0}]
    """
    assert(n>0)

    try:
        m = len(F)
    except AttributeError:
        F = F.gens()
        m = len(F)

    P = iter(F).next().parent()
    K = P.base_ring()

    # instantiate the SAT solver

    if Solver is None:
        from sage.sat.solvers.cryptominisat import CryptoMiniSat as Solver

    solver_kwds = {}
    for k,v in kwds.iteritems():
        if k.startswith("s_"):
            solver_kwds[k[2:]] = v

    solver = Solver(**solver_kwds)

    # instantiate the ANF to CNF converter

    if Converter is None:
        from sage.sat.converters.polybori import CNFEncoder as Converter

    converter_kwds = {}
    for k,v in kwds.iteritems():
        if k.startswith("c_"):
            converter_kwds[k[2:]] = v

    converter = Converter(solver, P, **converter_kwds)

    phi = converter(F, **converter_kwds)
    rho = dict( (phi[i],i) for i in range(len(phi)) )

    S = []

    while True:
        s = solver(**solver_kwds)

        if s:
            S.append( dict( (x, K(s[rho[x]])) for x in P.gens() ) )

            if n is not None and len(S) == n:
                break

            exclude_solution = tuple(-rho[x]  if s[rho[x]] else rho[x] for x in P.gens())
            solver.add_clause(exclude_solution)

        else:
            try:
                learnt = solver.unitary_learnt_clauses()
                if learnt:
                    S.append( dict((phi[abs(i)-1],K(i<0)) for i in learnt) )
                else:
                    S.append( s )
                    break
            except AttributeError:
                # solver does not support recovering learnt clauses
                S.append( s )
                break

    if len(S) == 1:
        if S[0] is False:
            return False
        if S[0] is None:
            return None
    elif S[-1] is False:
            return S[0:-1]
    return S

def learn(F, Converter=None, Solver=None, max_learnt_length=3, interreduction=False, **kwds):
    """
    Learn new polynomials by running SAT-solver ``Solver`` on
    SAT-instance produced by ``Converter`` from ``F``.

    INPUT:

    - ``F`` - a sequence of Boolean polynomials

    - ``Converter`` - an ANF to CNF converter class.  If ``Converter``
      is ``None`` then :cls:`sage.sat.converters.polybori.CNFEncoder`
      is used. (default: ``None``)

    - ``Solver`` - a SAT-solver class If ``Solver`` is ``None`` then
      cls:`sage.sat.solvers.cryptominisat.CryptoMiniSat` is used.
      (default: ``None``)

    - ``max_learnt_length`` - only clauses of length <=
      ``max_length_learnt`` are considered and converted to
      polynomials. (default: ``3``)

    - ``interreduction`` - inter-reduce the resulting polynomials
      (default: ``False``)

    - ``**kwds`` - parameters can be passed to the converter and the
       solver by prefixing them with 'c_' and 's_' respectively. For
       example, to increase CryptoMiniSat's verbosity level, pass
       ``s_verbosity=1``.

    OUTPUT:

        A sequence of Boolean polynomials.

    EXAMPLE::

       sage: from sage.sat.boolean_polynomials import learn as learn_sat # optional - cryptominisat

    We construct a simple system and solve it::

       sage: set_random_seed(2300)                      # optional - cryptominisat
       sage: sr = mq.SR(1,2,2,4,gf2=True,polybori=True) # optional - cryptominisat
       sage: F,s = sr.polynomial_system()               # optional - cryptominisat
       sage: H = learn_sat(F)                           # optional - cryptominisat
       sage: H[-1]                                      # optional - cryptominisat
       k033 + 1

    We construct a slightly larger equation system and recover some
    equations after 20 restarts::

       sage: set_random_seed(2300)                        # optional - cryptominisat
       sage: sr = mq.SR(1,4,4,4,gf2=True,polybori=True)   # optional - cryptominisat
       sage: F,s = sr.polynomial_system()                 # optional - cryptominisat
       sage: from sage.sat.boolean_polynomials import learn as learn_sat # optional - cryptominisat
       sage: H = learn_sat(F, s_maxrestarts=20, interreduction=True)     # optional - cryptominisat
       sage: H[-1]                                        # optional - cryptominisat
       s031*s030*x011201 + s031*x011201 + s031*s030 + s031

    .. note::

       This function is meant to be called with some parameter such
       that the SAT-solver is interrupted. For CryptoMiniSat this is
       max_restarts, so pass 'c_max_restarts' to limit the number of
       restarts CryptoMiniSat will attempt. If no such parameter is
       passed, then this function behaves essentially like
       :func:`solve` except that this function does not support
       ``n>1``.
    """
    try:
        m = len(F)
    except AttributeError:
        F = F.gens()
        m = len(F)

    P = iter(F).next().parent()
    K = P.base_ring()

    # instantiate the SAT solver

    if Solver is None:
        from sage.sat.solvers.cryptominisat import CryptoMiniSat as Solver

    solver_kwds = {}
    for k,v in kwds.iteritems():
        if k.startswith("s_"):
            solver_kwds[k[2:]] = v

    solver = Solver(**solver_kwds)

    # instantiate the ANF to CNF converter

    if Converter is None:
        from sage.sat.converters.polybori import CNFEncoder as Converter

    converter_kwds = {}
    for k,v in kwds.iteritems():
        if k.startswith("c_"):
            converter_kwds[k[2:]] = v

    converter = Converter(solver, P, **converter_kwds)


    phi = converter(F, **converter_kwds)
    rho = dict( (phi[i],i) for i in range(len(phi)) )

    s = solver(**solver_kwds)

    if s:
        learnt = [x + K(s[rho[x]]) for x in P.gens()]
    else:
        learnt = []
        for c in solver.unitary_learnt_clauses():
            try:
                f = phi[abs(i)] + K(i<0)
            except KeyError:
                # the solver might have learnt clauses that contain CNF
                # variables which have no correspondence to variables in our
                # polynomial ring (XOR chaining variables for example)
                pass
            learnt.append( f )

        for c in solver.learnt_clauses():
            if len(c) <= max_learnt_length:
                try:
                    learnt.append( converter.to_polynomial(c) )
                except ValueError:
                    # the solver might have learnt clauses that contain CNF
                    # variables which have no correspondence to variables in our
                    # polynomial ring (XOR chaining variables for example)
                    pass
    learnt = Sequence(learnt)

    if interreduction:
        learnt = learnt.ideal().interreduced_basis()
    return learnt
