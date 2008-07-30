r"""
Hidden Markov Models

AUTHOR: William Stein

EXAMPLES:

TODO:
   * make models pickleable (i.e., all parameters should be obtainable
     using functions to make this easy).
   * continuous hmm's
"""

import math

from sage.matrix.all import is_Matrix, matrix
from sage.rings.all  import RDF
from sage.misc.randstate import random

include "../../ext/stdsage.pxi"

include "misc.pxi"

cdef class HiddenMarkovModel:
    def __init__(self, A, B, pi):
        if not is_Matrix(A):
            A = matrix(RDF, len(A), len(A[0]), A)
        if not is_Matrix(B):
            B = matrix(RDF, len(B), len(B[0]), B)
        if not A.is_square():
            raise ValueError, "A must be square"
        if A.nrows() != B.nrows():
            raise ValueError, "number of rows of A and B must be the same"
        if A.base_ring() != RDF:
            A = A.change_ring(RDF)
        if B.base_ring() != RDF:
            B = B.change_ring(RDF)

        self.pi = [float(x) for x in pi]
        if len(self.pi) != A.nrows():
            raise ValueError, "length of pi must equal number of rows of A"

        self.A = A
        self.B = B


cdef class DiscreteHiddenMarkovModel(HiddenMarkovModel):

    def __init__(self, A, B, pi, emission_symbols=None, name=None):
        """
        INPUTS:
            A  -- square matrix of doubles; the state change probabilities
            B  -- matrix of doubles; emission probabilities
            pi -- list of floats; probabilities for each initial state
            emission_state -- list of B.ncols() symbols (just used for printing)
            name -- (optional) name of the model

        EXAMPLES:
        We create a discrete HMM with 2 internal states on an alphabet of
        size 2.

            sage: a = hmm.DiscreteHiddenMarkovModel([[0.2,0.8],[0.5,0.5]], [[1,0],[0,1]], [0,1])

        """
        self.initialized = False
        HiddenMarkovModel.__init__(self, A, B, pi)

        cdef Py_ssize_t i, j, k
        self.set_emission_symbols(emission_symbols)

        self.m = <ghmm_dmodel*> safe_malloc(sizeof(ghmm_dmodel))

        self.m.label = to_int_array(range(len(self._emission_symbols)))

        # Set all pointers to NULL
        self.m.s = NULL; self.m.name = NULL; self.m.silent = NULL
        self.m.tied_to = NULL; self.m.order = NULL; self.m.background_id = NULL
        self.m.bp = NULL; self.m.topo_order = NULL; self.m.pow_lookup = NULL;
        self.m.label_alphabet = NULL; self.m.alphabet = NULL

        # Set number of states and number of outputs
        self.m.N = self.A.nrows()
        self.m.M = len(self._emission_symbols)
        # Set the model type to discrete
        self.m.model_type = GHMM_kDiscreteHMM

        # Set that no a prior model probabilities are set.
        self.m.prior = -1

        # Assign model identifier if specified
        if name is not None:
            name = str(name)
            self.m.name = name
        else:
            self.m.name = NULL

        # Allocate and initialize states
        cdef ghmm_dstate* states = <ghmm_dstate*> safe_malloc(sizeof(ghmm_dstate) * self.m.N)
        cdef ghmm_dstate* state

        silent_states = []
        tmp_order     = []

        for i in range(self.m.N):
            v = self.B[i]

            # Get a reference to the i-th state for convenience of the notation below.
            state = &(states[i])
            state.desc = NULL

            # Compute state order
            if self.m.M > 1:
                order = math.log( len(v), self.m.M ) - 1
            else:
                order = len(v) - 1

            # Check for valid number of emission parameters
            order = int(order)
            if self.m.M**(order+1) == len(v):
                tmp_order.append(order)
            else:
                raise ValueError, "number of columns (= %s) of B must be a power of the number of emission symbols (= %s)"%(
                    self.B.ncols(), len(emission_symbols))

            state.b = to_double_array(v)
            state.pi = self.pi[i]

            silent_states.append( 1 if sum(v) == 0 else 0)

            # Set out probabilities, i.e., the probabilities that each
            # symbol will be emitted from this state.
            v = self.A[i]
            nz = v.nonzero_positions()
            k = len(nz)
            state.out_states = k
            state.out_id = <int*> safe_malloc(sizeof(int)*k)
            state.out_a  = <double*> safe_malloc(sizeof(double)*k)
            for j in range(k):
                state.out_id[j] = nz[j]
                state.out_a[j]  = v[nz[j]]

            # Set "in" probabilities
            v = self.A.column(i)
            nz = v.nonzero_positions()
            k = len(nz)
            state.in_states = k
            state.in_id = <int*> safe_malloc(sizeof(int)*k)
            state.in_a  = <double*> safe_malloc(sizeof(double)*k)
            for j in range(k):
                state.in_id[j] = nz[j]
                state.in_a[j]  = v[nz[j]]

            state.fix = 0

        self.m.s = states
        self.initialized = True

##         if sum(silent_states) > 0:
##             self.m.model_type |= GHMM_kSilentStates
##             self.m.silent = to_int_array(silent_states)
##         self.m.maxorder = max(tmp_order)
##         if self.m.maxorder > 0:
##             self.m.model_type |= GHMM_kHigherOrderEmissions
##             self.m.order = to_int_array(tmp_order)
##         # Initialize lookup table for powers of the alphabet size,
##         # which speeds up models with higher order states.
##         powLookUp = [1] * (self.m.maxorder+2)
##         for i in range(1,len(powLookUp)):
##             powLookUp[i] = powLookUp[i-1] * self.m.M
##         self.m.pow_lookup = to_int_array(powLookUp)
##         self.initialized = True

    def __dealloc__(self):
        if self.initialized:
            ghmm_dmodel_free(&self.m)

    def __repr__(self):
        """
        Return string representation of this HMM.

        OUTPUT:
            string

        EXAMPLES:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.1,0.9],[0.1,0.9]], [[0.9,0.1],[0.1,0.9]], [0.5,0.5], [3/4, 'abc'])
            sage: a.__repr__()
            "Discrete Hidden Markov Model (2 states, 2 outputs)\nInitial probabilities: [0.5, 0.5]\nTransition matrix:\n[0.1 0.9]\n[0.1 0.9]\nEmission matrix:\n[0.9 0.1]\n[0.1 0.9]\nEmission symbols: [3/4, 'abc']"
        """
        s = "Discrete Hidden Markov Model%s (%s states, %s outputs)"%(
            ' ' + self.m.name if self.m.name else '',
            self.m.N, self.m.M)
        s += '\nInitial probabilities: %s'%self.initial_probabilities()
        s += '\nTransition matrix:\n%s'%self.transition_matrix()
        s += '\nEmission matrix:\n%s'%self.emission_matrix()
        if self._emission_symbols_dict:
            s += '\nEmission symbols: %s'%self._emission_symbols
        return s

    def initial_probabilities(self):
        """
        Return the list of initial state probabilities.

        EXAMPLES:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.9,0.1],[0.9,0.1]], [[0.5,0.5,0,0],[0,0,.5,.5]], [0.5,0.5], [1,-1,3,-3])
            sage: a.initial_probabilities()
            [0.5, 0.5]
        """
        cdef Py_ssize_t i
        return [self.m.s[i].pi for i in range(self.m.N)]

    def transition_matrix(self, list_only=True):
        """
        Return the hidden state transition matrix.

        EXAMPLES:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.9,0.1],[0.9,0.1]], [[0.5,0.5,0,0],[0,0,.5,.5]], [0.5,0.5], [1,-1,3,-3])
            sage: a.transition_matrix()
            [0.9 0.1]
            [0.9 0.1]
        """
        cdef Py_ssize_t i, j
        for i from 0 <= i < self.m.N:
            for j from 0 <= j < self.m.s[i].out_states:
                self.A.set_unsafe_double(i,j,self.m.s[i].out_a[j])
        return self.A

    def emission_matrix(self, list_only=True):
        """
        Return the emission probability matrix.

        EXAMPLES:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.9,0.1],[0.9,0.1]], [[0.5,0.5,0,0],[0,0,.5,.5]], [0.5,0.5], [1,-1,3,-3])
            sage: a.emission_matrix()
            [0.5 0.5 0.0 0.0]
            [0.0 0.0 0.5 0.5]
        """
        cdef Py_ssize_t i, j
        for i from 0 <= i < self.m.N:
            for j from 0 <= j < self.B._ncols:
                self.B.set_unsafe_double(i,j,self.m.s[i].b[j])
        return self.B

    def normalize(self):
        """
        Normalize the transition and emission probabilities, if applicable.

        EXAMPLES:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.5,1],[1.2,0.9]], [[1,0.5],[0.5,1]], [0.1,1.2])
            sage: a.normalize()
            sage: a
            Discrete Hidden Markov Model (2 states, 2 outputs)
            Initial probabilities: [0.076923076923076927, 0.92307692307692302]
            Transition matrix:
            [0.333333333333 0.666666666667]
            [0.571428571429 0.428571428571]
            Emission matrix:
            [0.666666666667 0.333333333333]
            [0.333333333333 0.666666666667]
        """
        ghmm_dmodel_normalize(self.m)

    def sample_single(self, long length):
        """
        Return a single sample computed using this Hidden Markov Model.

        EXAMPLE:
            sage: set_random_seed(0)
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.1,0.9],[0.1,0.9]], [[1,0],[0,1]], [0,1])
            sage: a.sample_single(20)
            [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            sage: a.sample_single(1000).count(0)
            113

        If the emission symbols are set
            sage: set_random_seed(0)
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.5,0.5],[0.1,0.9]], [[1,0],[0,1]], [0,1], ['up', 'down'])
            sage: print a.sample_single(10)
            ['down', 'up', 'down', 'down', 'up', 'down', 'down', 'up', 'down', 'up']

        """
        seed = random()
        cdef ghmm_dseq *d = ghmm_dmodel_generate_sequences(self.m, seed, length, 1, length)
        cdef Py_ssize_t i
        v = [d.seq[0][i] for i in range(length)]
        ghmm_dseq_free(&d)
        if self._emission_symbols_dict:
            w = self._emission_symbols
            return [w[i] for i in v]
        else:
            return v

    def sample(self, long length, long number):
        """
        Return number samples from this HMM of given length.

        EXAMPLES:
            sage: set_random_seed(0)
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.1,0.9],[0.1,0.9]], [[1,0],[0,1]], [0,1])
            sage: print a.sample(10, 3)
            [[1, 0, 1, 1, 0, 1, 1, 0, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        """
        seed = random()
        cdef ghmm_dseq *d = ghmm_dmodel_generate_sequences(self.m, seed, length, number, length)
        cdef Py_ssize_t i, j
        v = [[d.seq[j][i] for i in range(length)] for j in range(number)]
        if self._emission_symbols_dict:
            w = self._emission_symbols
            return [[w[i] for i in z] for z in v]
        else:
            return v

    def emission_symbols(self):
        """
        Return a copy of the list of emission symbols of self.

        Use set_emission_symbols to set the list of emission symbols.

        EXAMPLES:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.5,0.5],[0.1,0.9]], [[1,0],[0,1]], [0,1], ['up', -3/179])
            sage: a.emission_symbols()
            ['up', -3/179]
        """
        return list(self._emission_symbols)

    def set_emission_symbols(self, emission_symbols):
        """
        Set the list of emission symbols.

        EXAMPLES:
            sage: set_random_seed(0)
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.5,0.5],[0.1,0.9]], [[1,0],[0,1]], [0,1], ['up', 'down'])
            sage: a.set_emission_symbols([3,5])
            sage: a.emission_symbols()
            [3, 5]
            sage: a.sample_single(10)
            [5, 3, 5, 5, 3, 5, 5, 3, 5, 3]
            sage: a.set_emission_symbols([pi,5/9+e])
            sage: a.sample_single(10)
            [e + 5/9, e + 5/9, e + 5/9, e + 5/9, e + 5/9, e + 5/9, pi, pi, e + 5/9, pi]
        """
        if emission_symbols is None:
            self._emission_symbols = range(self.B.ncols())
            self._emission_symbols_dict = None
        else:
            self._emission_symbols = list(emission_symbols)
            if self._emission_symbols != range(self.B.ncols()):
                self._emission_symbols_dict = dict([(x,i) for i, x in enumerate(emission_symbols)])


    ####################################################################
    # HMM Problem 1 -- Computing likelihood: Given the parameter set
    # lambda of an HMM model and an observation sequence O, determine
    # the likelihood P(O | lambda).
    ####################################################################
    def log_likelihood(self, seq):
        r"""
        HMM Problem 1: Likelihood. Return $\log ( P[seq | model] )$,
        the log of the probability of seeing the given sequence given
        this model, using the forward algorithm and assuming
        independance of the sequence seq.

        INPUT:
            seq -- a list; sequence of observed emissions of the HMM

        OUTPUT:
            float -- the log of the probability of seeing this sequence
                     given the model

        WARNING: By convention we return -inf for 0 probability events.

        EXAMPLES:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.1,0.9],[0.1,0.9]], [[1,0],[0,1]], [0,1])
            sage: a.log_likelihood([1,1])
            -0.10536051565782635
            sage: a.log_likelihood([1,0])
            -2.3025850929940459

        Notice that any sequence starting with 0 can't occur, since
        the above model always starts in a state that produces 1 with
        probability 1.  By convention log(probability 0) is -inf.
            sage: a.log_likelihood([0,0])
            -inf

        Here's a special case where each sequence is equally probable.
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.5,0.5],[0.5,0.5]], [[1,0],[0,1]], [0.5,0.5])
            sage: a.log_likelihood([0,0])
            -1.3862943611198906
            sage: log(0.25)
            -1.38629436111989
            sage: a.log_likelihood([0,1])
            -1.3862943611198906
            sage: a.log_likelihood([1,0])
            -1.3862943611198906
            sage: a.log_likelihood([1,1])
            -1.3862943611198906
        """
        cdef double log_p
        cdef int* O = to_int_array(seq)
        cdef int ret = ghmm_dmodel_logp(self.m, O, len(seq), &log_p)
        sage_free(O)
        if ret == -1:
            # forward returned -1: sequence can't be built
            return -float('Inf')
        return log_p

    ####################################################################
    # HMM Problem 2 -- Decoding: Given the complete parameter set that
    # defines the model and an observation sequence seq, determine the
    # best hidden sequence Q.  Use the Viterbi algorithm.
    ####################################################################
    def viterbi(self, seq):
        """
        HMM Problem 2: Decoding.  Determine a hidden sequence of
        states that is most likely to produce the given sequence seq
        of obserations.

        INPUT:
            seq -- sequence of emitted symbols

        OUTPUT:
            list -- a most probable sequence of hidden states, i.e., the
                    Viterbi path.
            float -- log of the probability that the sequence of hidden
                     states actually produced the given sequence seq.
                     [[TODO: I do not understand precisely what this means.]]

        EXAMPLES:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.1,0.9],[0.1,0.9]], [[0.9,0.1],[0.1,0.9]], [0.5,0.5])
            sage: a.viterbi([1,0,0,1,0,0,1,1])
            ([1, 0, 0, 1, 1, 0, 1, 1], -11.062453224772216)

        We predict the state sequence when the emissions are 3/4 and 'abc'.
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.1,0.9],[0.1,0.9]], [[0.9,0.1],[0.1,0.9]], [0.5,0.5], [3/4, 'abc'])

        Note that state 0 is common below, despite the model trying hard to
        switch to state 1:
            sage: a.viterbi([3/4, 'abc', 'abc'] + [3/4]*10)
            ([0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], -25.299405845367794)
        """
        if self._emission_symbols_dict:
            seq = [self._emission_symbols_dict[z] for z in seq]
        cdef int* path
        cdef int* O = to_int_array(seq)
        cdef int pathlen
        cdef double log_p

        path = ghmm_dmodel_viterbi(self.m, O, len(seq), &pathlen, &log_p)
        sage_free(O)
        p = [path[i] for i in range(pathlen)]
        sage_free(path)

        return p, log_p

    ####################################################################
    # HMM Problem 3 -- Learning: Given an observation sequence O and
    # the set of states in the HMM, improve the HMM to increase the
    # probability of observing O.
    ####################################################################
    def baum_welch(self, training_seqs, nsteps=None, log_likelihood_cutoff=None):
        """
        HMM Problem 3: Learning.  Given an observation sequence O and
        the set of states in the HMM, improve the HMM using the
        Baum-Welch algorithm to increase the probability of observing O.

        INPUT:
            training_seqs -- a list of lists of emission symbols
            nsteps -- integer or None (default: None) maximum number
                      of Baum-Welch steps to take
            log_likehood_cutoff -- positive float or None (default:
                      None); the minimal improvement in likelihood
                      with respect to the last iteration required to
                      continue. Relative value to log likelihood

        OUTPUT:
            changes the model in places, or raises a RuntimError
            exception on error

        EXAMPLES:
        We make a model that has two states and is equally likely to output
        0 or 1 in either state and transitions back and forth with equal
        probability.
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.5,0.5],[0.5,0.5]], [[0.5,0.5],[0.5,0.5]], [0.5,0.5])

        We give the model some training data this much more likely to
        be 1 than 0.
            sage: a.baum_welch([[1,1,1,1,0,1], [1,0,1,1,1,1]])

        Now the model's emission matrix changes since it is much
        more likely to emit 1 than 0.
            sage: a
            Discrete Hidden Markov Model (2 states, 2 outputs)
            Initial probabilities: [0.5, 0.5]
            Transition matrix:
            [0.5 0.5]
            [0.5 0.5]
            Emission matrix:
            [0.166666666667 0.833333333333]
            [0.166666666667 0.833333333333]

        Note that 1/6 = 1.666...:
            sage: 1.0/6
            0.166666666666667

        TESTS:
        We test training with non-default string symbols:
            sage: a = hmm.DiscreteHiddenMarkovModel([[0.5,0.5],[0.5,0.5]], [[0.5,0.5],[0.5,0.5]], [0.5,0.5], ['up','down'])
            sage: a.baum_welch([['up','up'], ['down','up']])
            sage: a
            Discrete Hidden Markov Model (2 states, 2 outputs)
            Initial probabilities: [0.5, 0.5]
            Transition matrix:
            [0.5 0.5]
            [0.5 0.5]
            Emission matrix:
            [0.75 0.25]
            [0.75 0.25]
            Emission symbols: ['up', 'down']

        NOTE: Training for models including silent states is not yet supported.

        REFERENCES:
            Rabiner, L.R.: "`A Tutorial on Hidden Markov Models and Selected
            Applications in Speech Recognition"', Proceedings of the IEEE,
            77, no 2, 1989, pp 257--285.
        """
        if self._emission_symbols_dict:
            seqs = [[self._emission_symbols_dict[z] for z in x] for x in training_seqs]
        else:
            seqs = training_seqs

        cdef ghmm_dseq* d = malloc_ghmm_dseq(seqs)

        if ghmm_dmodel_baum_welch(self.m, d):
            raise RuntimeError, "error running Baum-Welch algorithm"

        ghmm_dseq_free(&d)


##################################################################################
# Helper Functions
##################################################################################

cdef ghmm_dseq* malloc_ghmm_dseq(seqs) except NULL:
    cdef ghmm_dseq* d = ghmm_dseq_calloc(len(seqs))
    if d == NULL:
        raise MemoryError
    cdef int i, j, m, n
    m = len(seqs)
    d.seq_number = m
    d.capacity = m
    d.total_w = m
    for i from 0 <= i < m:
        v = seqs[i]
        n = len(v)
        d.seq[i] = <int*> safe_malloc(sizeof(int) * n)
        for j from 0 <= j < n:
            d.seq[i][j] = v[j]
        d.seq_len[i] = n
        d.seq_id[i] = i
        d.seq_w[i] = 1
    d.flags = 0
    return d
