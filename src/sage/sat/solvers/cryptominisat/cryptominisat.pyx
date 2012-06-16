"""
CryptoMiniSat.

"CryptoMiniSat is an LGPL-licenced SAT solver that aims to become a
premier SAT solver with all the features and speed of successful SAT
solvers, such as MiniSat and PrecoSat. The long-term goals of
CryptoMiniSat are to be an efficient sequential, parallel and
distributed solver. There are solvers that are good at one or the
other, e.g. ManySat (parallel) or PSolver (distributed), but we wish
to excel at all." -- http://www.msoos.org/cryptominisat2/

.. note::

    Our SAT solver interfaces are 1-based, i.e., literals start at
    1. This is consistent with the popular DIMACS format for SAT
    solving but not with Pythion's 0-based convention. However, this
    also allows to construct clauses using simple integers.

AUTHORS:

- Martin Albrecht (2012): first version
"""
##############################################################################
#  Copyright (C) 2012 Martin Albrecht <martinralbrecht@googlemail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
##############################################################################

include "../../../ext/stdsage.pxi"
include "../../../ext/interrupt.pxi"

from libc.stdint cimport uint32_t
from decl cimport lbool, Var, Lit, Clause, l_Undef, l_False
from decl cimport vec, vector
from decl cimport GaussConf
from solverconf cimport SolverConf

from sage.misc.misc import get_verbose

cdef extern from "cryptominisat_helper.h":
     cdef uint32_t** get_sorted_learnts_helper(Solver* solver, uint32_t* num)

cdef class CryptoMiniSat(SatSolver):
    """
    The CryptoMiniSat solver.

    EXAMPLE::

        sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
        sage: cms = CryptoMiniSat()                      # optional - cryptominisat
        sage: cms.add_clause((1,2,-3))                   # optional - cryptominisat
        sage: cms()                                      # optional - cryptominisat
        (None, True, True, False)

    .. note::

        Do not import 'sage.sat.solvers.cryptominisat.cryptominisat'
        directly, but use 'sage.sat.solvers.cryptominisat' which
        throws a friendlier error message if the CryptoMiniSat SPKG is
        not installed. Also, 'CryptoMiniSat' will be available in
        'sage.sat.solvers' if the CryptoMiniSat SPKG is installed.
    """
    def __cinit__(self, SolverConf sc=None, **kwds):
        """
        Construct a new CryptoMiniSat instance.

        INPUT:

        - ``SolverConf`` - a :cls:`sage.sat.solvers.cryptominisat.SolverConf` instance
        - ``**kwds`` - passed to :cls:`sage.sat.solvers.cryptominisat.SolverConf`

        EXAMPLE::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat

        CryptoMiniSat accepts a :cls:`sage.sat.solvers.cryptominisat.SolverConf` instance as parameter::

            sage: from sage.sat.solvers.cryptominisat import SolverConf # optional - cryptominisat
            sage: sc = SolverConf(verbosity=2)                          # optional - cryptominisat
            sage: cms = CryptoMiniSat(sc=sc)                            # optional - cryptominisat

        However, parameters passed directly tot he solver overwrite
        any options passed to the :cls:`sage.sat.solvers.cryptominisat.SolverConf` instance::

            sage: from sage.sat.solvers.cryptominisat import SolverConf # optional - cryptominisat
            sage: sc = SolverConf(verbosity=2)                          # optional - cryptominisat
            sage: cms = CryptoMiniSat(sc=sc, verbosity=3)               # optional - cryptominisat
        """
        cdef SolverConf _sc
        if sc is not None:
             _sc = sc.__copy__()
        else:
             _sc = SolverConf()
        cdef GaussConf gc

        for k,v in kwds.iteritems():
            _sc[k] = v

        self._solver = new Solver(_sc._conf[0], gc)

    def __dealloc__(self):
        """
        TESTS::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: del cms                                    # optional - cryptominisat
        """
        del self._solver

    def __repr__(self):
         """
         TESTS::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: cms.add_clause((1,2,-3))                   # optional - cryptominisat
            sage: cms                                        # optional - cryptominisat
            CryptoMiniSat
            #vars:       3, #lits:       3, #clauses:       1, #learnt:       0, #assigns:       0
         """
         s = """CryptoMiniSat
#vars: %7d, #lits: %7d, #clauses: %7d, #learnt: %7d, #assigns: %7d
"""%(self._solver.nVars(), self._solver.nLiterals(), self._solver.nClauses(), self._solver.nLearnts(), self._solver.nAssigns())
         return s

    def var(self, decision=None):
        """
        Return a *new* generator.

        INPUT:

        - ``decision`` - if ``True`` this variable will be used for
          decisions (default: ``None``, let the solver decide.)

        EXAMPLE::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: cms.var()                                  # optional - cryptominisat
            1
            sage: cms.var(decision=True)                     # optional - cryptominisat
            2

        """
        cdef Var var
        if decision is None:
            var = self._solver.newVar()
        else:
            var = self._solver.newVar(bool(decision))
        return int(var+1)

    def nvars(self):
        """
        Return the number of variables.

        EXAMPLE::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: cms.var()                                  # optional - cryptominisat
            1
            sage: cms.var(decision=True)                     # optional - cryptominisat
            2
            sage: cms.nvars()                                # optional - cryptominisat
            2
        """
        return int(self._solver.nVars())

    def add_clause(self, lits):
        """
        Add a new clause to set of clauses.

        INPUT:

        - ``lits`` - a tuple of integers != 0

        .. note::

            If any element ``e`` in ``lits`` has ``abs(e)`` greater
            than the number of variables generated so far, then new
            variables are created automatically.

        EXAMPLE::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: cms.var()                                  # optional - cryptominisat
            1
            sage: cms.var(decision=True)                     # optional - cryptominisat
            2
            sage: cms.add_clause( (1, -2 , 3) )              # optional - cryptominisat
            sage: cms                                        # optional - cryptominisat
            CryptoMiniSat
            #vars:       3, #lits:       3, #clauses:       1, #learnt:       0, #assigns:       0
        """
        cdef vec[Lit] l
        for lit in lits:
            lit = int(lit)
            while abs(lit) > self._solver.nVars():
                self._solver.newVar()
            l.push(Lit(abs(lit)-1,lit<0))
        self._solver.addClause(l)

    def add_xor_clause(self, lits, isfalse):
        """
        Add a new XOR clause to set of clauses.

        INPUT:

        - ``lits`` - a tuple of integers != 0
        - ``isfalse`` - set to ``True`` if the XOR chain should evaluate to ``False``

        .. note::

            If any element ``e`` in ``lits`` has ``abs(e)`` greater
            than the number of variables generated so far, then new
            variables are created automatically.

        EXAMPLE::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: cms.var()                                  # optional - cryptominisat
            1
            sage: cms.var(decision=True)                     # optional - cryptominisat
            2
            sage: cms.add_xor_clause( (1, -2 , 3), True )    # optional - cryptominisat
            sage: cms                                        # optional - cryptominisat
            CryptoMiniSat
            #vars:       3, #lits:       3, #clauses:       1, #learnt:       0, #assigns:       0
        """
        cdef vec[Lit] l
        for lit in lits:
            while abs(lit) > self._solver.nVars():
                self._solver.newVar()
            l.push(Lit(abs(lit)-1,lit<0))
        self._solver.addXorClause(l, bool(isfalse))

    def __call__(self, assumptions=None):
        """
        Solve this instance.

        INPUT:

        - ``assumptions`` - assumed variable assignments (default: ``None``)

        OUTPUT:

        - If this instance is SAT: A tuple of length ``nvars()+1``
          where the ``i``-th entry holds an assignment for the
          ``i``-th variables (the ``0``-th entry is always ``None``).

        - If this instance is UNSAT: ``False``

        - If the solver was interrupted before deciding satisfiability
          ``None``.

        EXAMPLE:

        We construct a simple example::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: cms.add_clause( (1, 2) )                   # optional - cryptominisat


        First, we do not assume anything, note that the first entry is
        ``None`` because there is not ``0``-th variable::

            sage: cms()                                      # optional - cryptominisat
            (None, True, False)

        Now, we make assumptions which make this instance UNSAT::

            sage: cms( (-1, -2) )                            # optional - cryptominisat
            False
            sage: cms.conflict_clause()                      # optional - cryptominisat
            (2, 1)

        Finally, we use assumptions to decide on a solution::

            sage: cms( (-1,) )                               # optional - cryptominisat
            (None, False, True)
        """
        cdef vec[Lit] l
        cdef lbool r
        if assumptions is None:
             _sig_on
             r = self._solver.solve()
             _sig_off
        else:
             for lit in assumptions:
                  while abs(lit) > self._solver.nVars():
                       self._solver.newVar()
                  l.push(Lit(abs(lit)-1,lit<0))
             _sig_on
             r = self._solver.solve(l)
             _sig_off

        if r == l_False:
            return False
        if r == l_Undef:
            return None

        return (None, ) + tuple([self._solver.model[i].getBool() for i in range(self._solver.model.size())])

    def conflict_clause(self):
        """
        Return conflict clause if this instance is UNSAT and the last
        call used assumptions.

        EXAMPLE::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: cms.add_clause( (1,2) )                    # optional - cryptominisat
            sage: cms.add_clause( (1,-2) )                   # optional - cryptominisat
            sage: cms.add_clause( (-1,) )                    # optional - cryptominisat
            sage: cms.conflict_clause()                      # optional - cryptominisat
            ()

        We solve again, but this time with an explicit assumption::

            sage: from sage.sat.solvers import CryptoMiniSat # optional - cryptominisat
            sage: cms = CryptoMiniSat()                      # optional - cryptominisat
            sage: cms.add_clause( (1,2) )                    # optional - cryptominisat
            sage: cms.add_clause( (1,-2) )                   # optional - cryptominisat
            sage: cms( (-1,) )                               # optional - cryptominisat
            False
            sage: cms.conflict_clause()                      # optional - cryptominisat
            (1,)

        A more elaborate example using small-scale AES where we set 80 variables to ``1``::

            sage: from sage.sat.solvers import CryptoMiniSat          # optional - cryptominisat
            sage: from sage.sat.converters.polybori import CNFEncoder # optional - cryptominisat
            sage: set_random_seed( 22 )                               # optional - cryptominisat
            sage: sr = mq.SR(1,4,4,4,gf2=True,polybori=True)          # optional - cryptominisat
            sage: F,s = sr.polynomial_system()                        # optional - cryptominisat
            sage: cms = CryptoMiniSat()                               # optional - cryptominisat
            sage: phi = CNFEncoder(cms, F.ring())(F)                  # optional - cryptominisat
            sage: cms( range(1,80) )                                  # optional - cryptominisat
            False

        This guess was wrong and we need to flip one of the following variables::

            sage: cms.conflict_clause()                                    # optional - cryptominisat
            (-72, -71, -70, -69)
        """
        cdef Lit l
        r = []
        for i in range(self._solver.conflict.size()):
             l = self._solver.conflict[i]
             r.append( (-1)**l.sign() * (l.var()+1) )
        return tuple(r)

    def learnt_clauses(self, unitary_only=False):
        """
        Return learnt clauses.

        INPUT:

        - ``unitary_only`` - return only unitary learnt clauses (default: ``False``)

        EXAMPLE::

            sage: from sage.sat.solvers import CryptoMiniSat          # optional - cryptominisat
            sage: from sage.sat.converters.polybori import CNFEncoder # optional - cryptominisat
            sage: set_random_seed( 22 )                               # optional - cryptominisat
            sage: sr = mq.SR(1,4,4,4,gf2=True,polybori=True)          # optional - cryptominisat
            sage: F,s = sr.polynomial_system()                        # optional - cryptominisat
            sage: cms = CryptoMiniSat(maxrestarts=10,verbosity=0)     # optional - cryptominisat
            sage: phi = CNFEncoder(cms, F.ring())(F)                  # optional - cryptominisat
            sage: cms()                                               # optional - cryptominisat
            sage: sorted(cms.learnt_clauses())[0]                     # optional - cryptominisat
            (-592, -578, -68, 588, 94, 579, 584, 583)


        An example for unitary clauses::

            sage: from sage.sat.solvers import CryptoMiniSat          # optional - cryptominisat
            sage: from sage.sat.converters.polybori import CNFEncoder # optional - cryptominisat
            sage: set_random_seed( 22 )                               # optional - cryptominisat
            sage: sr = mq.SR(1,4,4,4,gf2=True,polybori=True)          # optional - cryptominisat
            sage: F,s = sr.polynomial_system()                        # optional - cryptominisat
            sage: cms = CryptoMiniSat(maxrestarts=10,verbosity=0)     # optional - cryptominisat
            sage: phi = CNFEncoder(cms, F.ring())(F)                  # optional - cryptominisat
            sage: cms()                                               # optional - cryptominisat
            sage: cms.learnt_clauses(unitary_only=True)               # optional - cryptominisat
            ()

        .. todo::

            Find a more useful example for unitary learnt clauses.
        """
        cdef vector[Lit] learnt1 = self._solver.get_unitary_learnts()

        r = []
        for i in range(learnt1.size()):
            r.append( (-1)**learnt1[i].sign() * (learnt1[i].var()+1) )

        if unitary_only:
             return tuple(r)

        cdef uint32_t num = 0
        cdef uint32_t **learnt = get_sorted_learnts_helper(self._solver,&num)
        cdef uint32_t *clause = NULL

        r = []
        for i in range(num):
            clause = learnt[i]
            C = [(-1)**int(clause[j]&1) * (int(clause[j]>>1)+1) for j in range(1,clause[0]+1)]
            sage_free(clause)
            r.append(tuple(C))
        sage_free(learnt)
        return tuple(r)
