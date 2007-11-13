"""
Fast binary code routines.

Some computations with linear binary codes. Fix a basis for $GF(2)^n$.
A linear binary code is a linear subspace of $GF(2)^n$, together with
this choice of basis. A permutation $g \in S_n$ of the fixed basis
gives rise to a permutation of the vectors, or words, in $GF(2)^n$,
sending $(w_i)$ to $(w_{g(i)})$. The permutation automorphism group of
the code $C$ is the set of permutations of the basis that bijectively
map $C$ to itself. Note that if $g$ is such a permutation, then
$$g(a_i) + g(b_i) = (a_{g(i)} + b_{g(i)}) = g((a_i) + (b_i)).$$
Over other fields, it is also required that the map be linear, which
as per above boils down to scalar multiplication. However, over
$GF(2),$ the only scalars are 0 and 1, so the linearity condition has
trivial effect.

AUTHOR:
    Robert L Miller (Oct-Nov 2007)
        * compiled code datastructure
        * union-find based orbit partition
        * optimized partition stack class

        * NICE-based partition refinement algorithm
        * canonical generation function

"""

#*******************************************************************************
#         Copyright (C) 2007 Robert L. Miller <rlmillster@gmail.com>
#
# Distributed  under  the  terms  of  the  GNU  General  Public  License (GPL)
#                         http://www.gnu.org/licenses/
#*******************************************************************************

include '../ext/cdefs.pxi'
include '../ext/python_mem.pxi'
include '../ext/stdsage.pxi'
from sage.structure.element import is_Matrix
from sage.misc.misc import cputime
from math import log, floor
from sage.rings.integer import Integer

## NOTE - Since most of the functions are used from within the module, cdef'd
## functions come without an underscore, and the def'd equivalents, which are
## essentially only for doctesting and debugging, have underscores.

cdef int *hamming_weights():
    cdef int *ham_wts
    ham_wts = <int *> sage_malloc( 65536 * sizeof(int) )
    if not ham_wts:
        sage_free(ham_wts)
        raise MemoryError("Memory.")
    ham_wts[0] = 0
    ham_wts[1] = 1
    ham_wts[2] = 1
    ham_wts[3] = 2
    for i from 4 <= i < 16:
        ham_wts[i] = ham_wts[i & 3] + ham_wts[(i>>2) & 3]
    for i from 16 <= i < 256:
        ham_wts[i] = ham_wts[i & 15] + ham_wts[(i>>4) & 15]
    for i from 256 <= i < 65536:
        ham_wts[i] = ham_wts[i & 255] + ham_wts[(i>>8) & 255]
    return ham_wts
    # This may seem like overkill, but the worst case for storing the words
    # themselves is 65536- in this case, we are increasing memory usage by a
    # factor of 2. Also, this function will only be called once ever.

cdef class BinaryCode:
    """
    Minimal, but optimized, binary code object.

    EXAMPLE:
        sage: import sage.coding.binary_code
        sage: from sage.coding.binary_code import *
        sage: M = Matrix(GF(2), [[1,1,1,1]])
        sage: B = BinaryCode(M)     # create from matrix
        sage: C = BinaryCode(B, 60) # create using glue
        sage: D = BinaryCode(C, 240)
        sage: E = BinaryCode(D, 85)
        sage: B
        Binary [4,1] linear code, generator matrix
        [1111]
        sage: C
        Binary [6,2] linear code, generator matrix
        [111100]
        [001111]
        sage: D
        Binary [8,3] linear code, generator matrix
        [11110000]
        [00111100]
        [00001111]
        sage: E
        Binary [8,4] linear code, generator matrix
        [11110000]
        [00111100]
        [00001111]
        [10101010]

    """
    def __new__(self, arg1, arg2=None):
        cdef int nrows, i, j
        cdef int nwords, other_nwords, parity, word, combination, glue_word
        cdef BinaryCode other
        cdef int *self_words, *self_basis, *other_basis

        self.radix = sizeof(int) << 3

        if is_Matrix(arg1):
            self.ncols = arg1.ncols()
            self.nrows = arg1.nrows()
            nrows = self.nrows
            self.nwords = 1 << nrows
            nwords = self.nwords
        elif isinstance(arg1, BinaryCode):
            other = arg1
            self.nrows = other.nrows + 1
            glue_word = arg2
            self.ncols = max( other.ncols , floor(log(glue_word,2))+1 )
            other_nwords = other.nwords
            self.nwords = 2 * other_nwords
            nrows = self.nrows
            nwords = self.nwords
        else: raise NotImplementedError("!")

        if self.nrows >= self.radix or self.ncols > self.radix:
            raise NotImplementedError("Columns and rows are stored as ints. This code is too big.")

        self.words = <int *> sage_malloc( nwords * sizeof(int) )
        self.basis = <int *> sage_malloc( nrows * sizeof(int) )
        if not self.words or not self.basis:
            if self.words: sage_free(self.words)
            if self.basis: sage_free(self.basis)
            raise MemoryError("Memory.")
        self_words = self.words
        self_basis = self.basis

        if is_Matrix(arg1):
            rows = arg1.rows()
            for i from 0 <= i < nrows:
                word = 0
                for j in rows[i].nonzero_positions():
                    word += (1<<j)
                self_basis[i] = word

            word = 0
            parity = 0
            combination = 0
            while True:
                self_words[combination] = word
                parity ^= 1
                j = 0
                if not parity:
                    while not combination & (1 << j): j += 1
                    j += 1
                if j == nrows: break
                else:
                    combination ^= (1 << j)
                    word ^= self_basis[j]

        else: # isinstance(arg1, BinaryCode)
            other_basis = other.basis
            for i from 0 <= i < nrows-1:
                self_basis[i] = other_basis[i]
            i = nrows - 1
            self_basis[i] = glue_word

            memcpy(self_words, other.words, other_nwords*(self.radix>>3))

            for combination from 0 <= combination < other_nwords:
                self_words[combination+other_nwords] = self_words[combination] ^ glue_word

    def __dealloc__(self):
        sage_free(self.words)
        sage_free(self.basis)

    def print_data(self):
        """
        Print all data for self.

        EXAMPLES:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: M = Matrix(GF(2), [[1,1,1,1]])
            sage: B = BinaryCode(M)
            sage: C = BinaryCode(B, 60)
            sage: D = BinaryCode(C, 240)
            sage: E = BinaryCode(D, 85)
            sage: B.print_data() # random - actually "print P.print_data()"
            ncols: 4
            nrows: 1
            nwords: 2
            radix: 32
            basis:
            1111
            words:
            0000
            1111
            sage: C.print_data() # random - actually "print P.print_data()"
            ncols: 6
            nrows: 2
            nwords: 4
            radix: 32
            basis:
            111100
            001111
            words:
            000000
            111100
            001111
            110011
            sage: D.print_data() # random - actually "print P.print_data()"
            ncols: 8
            nrows: 3
            nwords: 8
            radix: 32
            basis:
            11110000
            00111100
            00001111
            words:
            00000000
            11110000
            00111100
            11001100
            00001111
            11111111
            00110011
            11000011
            sage: E.print_data() # random - actually "print P.print_data()"
            ncols: 8
            nrows: 4
            nwords: 16
            radix: 32
            basis:
            11110000
            00111100
            00001111
            10101010
            words:
            00000000
            11110000
            00111100
            11001100
            00001111
            11111111
            00110011
            11000011
            10101010
            01011010
            10010110
            01100110
            10100101
            01010101
            10011001
            01101001
        """
        from sage.graphs.graph_fast import binary
        cdef int ui
        cdef int i
        s = ''
        s += "ncols:" + str(self.ncols)
        s += "\nnrows:" + str(self.nrows)
        s += "\nnwords:" + str(self.nwords)
        s += "\nradix:" + str(self.radix)
        s += "\nbasis:\n"
        for i from 0 <= i < self.nrows:
            b = list(binary(self.basis[i]).zfill(self.ncols))
            b.reverse()
            b.append('\n')
            s += ''.join(b)
        s += "\nwords:\n"
        for ui from 0 <= ui < self.nwords:
            b = list(binary(self.words[ui]).zfill(self.ncols))
            b.reverse()
            b.append('\n')
            s += ''.join(b)

    def __repr__(self):
        """
        String representation of self.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: M = Matrix(GF(2), [[1,1,1,1,0,0,0,0],[0,0,1,1,1,1,0,0],[0,0,0,0,1,1,1,1],[1,0,1,0,1,0,1,0]])
            sage: B = BinaryCode(M)
            sage: B
            Binary [8,4] linear code, generator matrix
            [11110000]
            [00111100]
            [00001111]
            [10101010]

        """
        cdef int i, j
        s = 'Binary [%d,%d] linear code, generator matrix\n'%(self.ncols, self.nrows)
        for i from 0 <= i < self.nrows:
            s += '['
            for j from 0 <= j < self.ncols:
                s += '%d'%self.is_one(1<<i,j)
            s += ']\n'
        return s

    def _is_one(self, word, col):
        """
        Returns the col-th letter of word, i.e. 0 or 1. Words are expressed
        as integers, which represent linear combinations of the rows of the
        generator matrix of the code.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: M = Matrix(GF(2), [[1,1,1,1,0,0,0,0],[0,0,1,1,1,1,0,0],[0,0,0,0,1,1,1,1],[1,0,1,0,1,0,1,0]])
            sage: B = BinaryCode(M)
            sage: B
            Binary [8,4] linear code, generator matrix
            [11110000]
            [00111100]
            [00001111]
            [10101010]
            sage: B._is_one(7, 4)
            0
            sage: B._is_one(8, 4)
            1
            sage: B._is_automorphism([1,0,3,2,4,5,6,7], [1, 2, 4, 9])
            1

        """
        return self.is_one(word, col)

    cdef int is_one(self, int word, int column):
        if self.words[word] & (1 << column):
            return 1
        else:
            return 0

    def _is_automorphism(self, col_gamma, basis_gamma):
        """
        Check whether a given permutation is an automorphism of the code.

        INPUT:
            col_gamma -- permutation sending i |--> col_gamma[i] acting
                on the columns.
            basis_gamma -- describes where the basis elements are mapped
                under gamma. basis_gamma[i] is where the i-th row is sent,
                as an integer expressing a linear combination of the rows
                of the generator matrix.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: M = Matrix(GF(2), [[1,1,1,1,0,0,0,0],[0,0,1,1,1,1,0,0],[0,0,0,0,1,1,1,1],[1,0,1,0,1,0,1,0]])
            sage: B = BinaryCode(M)
            sage: B
            Binary [8,4] linear code, generator matrix
            [11110000]
            [00111100]
            [00001111]
            [10101010]
            sage: B._is_automorphism([1,0,3,2,4,5,6,7], [1, 2, 4, 9])
            1

        """
        cdef int i
        cdef int *_col_gamma
        cdef int *_basis_gamma
        _basis_gamma = <int *> sage_malloc(self.nrows * sizeof(int))
        _col_gamma = <int *> sage_malloc(self.ncols * sizeof(int))
        if not (_col_gamma and _basis_gamma):
            if _basis_gamma: sage_free(_basis_gamma)
            if _col_gamma: sage_free(_col_gamma)
            raise MemoryError("Memory.")
        for i from 0 <= i < self.nrows:
            _basis_gamma[i] = basis_gamma[i]
        for i from 0 <= i < self.ncols:
            _col_gamma[i] = col_gamma[i]
        result = self.is_automorphism(_col_gamma, _basis_gamma)
        sage_free(_col_gamma)
        sage_free(_basis_gamma)
        return result

    cdef int is_automorphism(self, int *col_gamma, int *basis_gamma):
        cdef int i, j, self_nrows = self.nrows, self_ncols = self.ncols
        for i from 0 <= i < self_nrows:
            for j from 0 <= j < self_ncols:
                if self.is_one(1 << i, j) != self.is_one(basis_gamma[i], col_gamma[j]):
                    return 0
        return 1

cdef class OrbitPartition:
    """
    Structure which keeps track of which vertices are equivalent
    under the part of the automorphism group that has already been
    seen, during search. Essentially a disjoint-set data structure*,
    which also keeps track of the minimum element and size of each
    cell of the partition, and the size of the partition.

    * http://en.wikipedia.org/wiki/Disjoint-set_data_structure

    """
    def __new__(self, nrows, ncols):
        cdef int nwords, word
        cdef int col
        nwords = (1 << nrows)
        self.nwords = nwords
        self.ncols = ncols
        self.wd_parent =       <int *> sage_malloc( nwords * sizeof(int) )
        self.wd_rank =         <int *> sage_malloc( nwords * sizeof(int) )
        self.wd_min_cell_rep = <int *> sage_malloc( nwords * sizeof(int) )
        self.wd_size =         <int *> sage_malloc( nwords * sizeof(int) )
        self.col_parent =       <int *> sage_malloc( ncols * sizeof(int) )
        self.col_rank =         <int *> sage_malloc( ncols * sizeof(int) )
        self.col_min_cell_rep = <int *> sage_malloc( ncols * sizeof(int) )
        self.col_size =         <int *> sage_malloc( ncols * sizeof(int) )
        if not (self.wd_parent and self.wd_rank and self.wd_min_cell_rep and self.wd_size and self.col_parent and self.col_rank and self.col_min_cell_rep and self.col_size):
            if self.wd_parent: sage_free(self.wd_parent)
            if self.wd_rank: sage_free(self.wd_rank)
            if self.wd_min_cell_rep: sage_free(self.wd_min_cell_rep)
            if self.wd_size: sage_free(self.wd_size)
            if self.col_parent: sage_free(self.col_parent)
            if self.col_rank: sage_free(self.col_rank)
            if self.col_min_cell_rep: sage_free(self.col_min_cell_rep)
            if self.col_size: sage_free(self.col_size)
            raise MemoryError("Memory.")
        for word from 0 <= word < nwords:
            self.wd_parent[word] = word
            self.wd_rank[word] = 0
            self.wd_min_cell_rep[word] = word
            self.wd_size[word] = 1
        for col from 0 <= col < ncols:
            self.col_parent[col] = col
            self.col_rank[col] = 0
            self.col_min_cell_rep[col] = col
            self.col_size[col] = 1

    def __dealloc__(self):
        sage_free(self.wd_parent)
        sage_free(self.wd_rank)
        sage_free(self.wd_min_cell_rep)
        sage_free(self.wd_size)
        sage_free(self.col_parent)
        sage_free(self.col_rank)
        sage_free(self.col_min_cell_rep)
        sage_free(self.col_size)

    def __repr__(self):
        """
        Return a string representation of the orbit partition.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: O = OrbitPartition(4, 8)
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
            Columns:
            0,1,2,3,4,5,6,7

        """
        cdef int i
        cdef int j
        s = 'OrbitPartition on %d words and %d columns. Data:\nWords:\n'%(self.nwords, self.ncols)
        for i from 0 <= i < self.nwords:
            s += '%d,'%self.wd_parent[i]
        s = s[:-1] + '\nColumns:\n'
        for j from 0 <= j < self.ncols:
            s += '%d,'%self.col_parent[j]
        return s[:-1]

    def _wd_find(self, word):
        """
        Returns the root of word.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: O = OrbitPartition(4, 8)
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
            Columns:
            0,1,2,3,4,5,6,7
            sage: O._wd_find(12)
            12

        """
        return self.wd_find(word)

    cdef int wd_find(self, int word):
        if self.wd_parent[word] == word:
            return word
        else:
            self.wd_parent[word] = self.wd_find(self.wd_parent[word])
            return self.wd_parent[word]

    def _wd_union(self, x, y):
        """
        Join the cells containing x and y.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: O = OrbitPartition(4, 8)
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
            Columns:
            0,1,2,3,4,5,6,7
            sage: O._wd_union(1,10)
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,9,1,11,12,13,14,15
            Columns:
            0,1,2,3,4,5,6,7
            sage: O._wd_find(10)
            1

        """
        self.wd_union(x, y)

    cdef void wd_union(self, int x, int y):
        cdef int x_root, y_root
        x_root = self.wd_find(x)
        y_root = self.wd_find(y)
        if self.wd_rank[x_root] > self.wd_rank[y_root]:
            self.wd_parent[y_root] = x_root
            self.wd_min_cell_rep[y_root] = min(self.wd_min_cell_rep[x_root],self.wd_min_cell_rep[y_root])
            self.wd_size[y_root] += self.wd_size[x_root]
        elif self.wd_rank[x_root] < self.wd_rank[y_root]:
            self.wd_parent[x_root] = y_root
            self.wd_min_cell_rep[x_root] = min(self.wd_min_cell_rep[x_root],self.wd_min_cell_rep[y_root])
            self.wd_size[x_root] += self.wd_size[y_root]
        elif x_root != y_root:
            self.wd_parent[y_root] = x_root
            self.wd_min_cell_rep[y_root] = min(self.wd_min_cell_rep[x_root],self.wd_min_cell_rep[y_root])
            self.wd_size[y_root] += self.wd_size[x_root]
            self.wd_rank[x_root] += 1

    def _col_find(self, col):
        """
        Returns the root of col.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: O = OrbitPartition(4, 8)
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
            Columns:
            0,1,2,3,4,5,6,7
            sage: O._col_find(6)
            6

        """
        return self.col_find(col)

    cdef int col_find(self, int col):
        if self.col_parent[col] == col:
            return col
        else:
            self.col_parent[col] = self.col_find(self.col_parent[col])
            return self.col_parent[col]

    def _col_union(self, x, y):
        """
        Join the cells containing x and y.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: O = OrbitPartition(4, 8)
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
            Columns:
            0,1,2,3,4,5,6,7
            sage: O._col_union(1,4)
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
            Columns:
            0,1,2,3,1,5,6,7
            sage: O._col_find(4)
            1

        """
        self.col_union(x, y)

    cdef void col_union(self, int x, int y):
        cdef int x_root, y_root
        x_root = self.col_find(x)
        y_root = self.col_find(y)
        if self.col_rank[x_root] > self.col_rank[y_root]:
            self.col_parent[y_root] = x_root
            self.col_min_cell_rep[y_root] = min(self.col_min_cell_rep[x_root],self.col_min_cell_rep[y_root])
            self.col_size[y_root] += self.col_size[x_root]
        elif self.col_rank[x_root] < self.col_rank[y_root]:
            self.col_parent[x_root] = y_root
            self.col_min_cell_rep[x_root] = min(self.col_min_cell_rep[x_root],self.col_min_cell_rep[y_root])
            self.col_size[x_root] += self.col_size[y_root]
        elif x_root != y_root:
            self.col_parent[y_root] = x_root
            self.col_min_cell_rep[y_root] = min(self.col_min_cell_rep[x_root],self.col_min_cell_rep[y_root])
            self.col_size[y_root] += self.col_size[x_root]
            self.col_rank[x_root] += 1

    def _merge_perm(self, col_gamma, wd_gamma):
        """
        Merges the cells of self under the given permutation. If gamma[a] = b,
        then after merge_perm, a and b will be in the same cell. Returns 0 if
        nothing was done, otherwise returns 1.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: O = OrbitPartition(4, 8)
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
            Columns:
            0,1,2,3,4,5,6,7
            sage: O._merge_perm([1,0,3,2,4,5,6,7], [0,1,2,3,4,5,6,7,9,8,11,10,13,12,15,14])
            1
            sage: O
            OrbitPartition on 16 words and 8 columns. Data:
            Words:
            0,1,2,3,4,5,6,7,8,8,10,10,12,12,14,14
            Columns:
            0,0,2,2,4,5,6,7

        """
        cdef int i
        cdef int *_col_gamma
        cdef int *_wd_gamma
        _wd_gamma = <int *> sage_malloc(self.nwords * sizeof(int))
        _col_gamma = <int *> sage_malloc(self.ncols * sizeof(int))
        if not (_col_gamma and _wd_gamma):
            if _wd_gamma: sage_free(_wd_gamma)
            if _col_gamma: sage_free(_col_gamma)
            raise MemoryError("Memory.")
        for i from 0 <= i < self.nwords:
            _wd_gamma[i] = wd_gamma[i]
        for i from 0 <= i < self.ncols:
            _col_gamma[i] = col_gamma[i]
        result = self.merge_perm(_col_gamma, _wd_gamma)
        sage_free(_col_gamma)
        sage_free(_wd_gamma)
        return result

    cdef int merge_perm(self, int *col_gamma, int *wd_gamma):
        cdef int i, gamma_i_root
        cdef int j, gamma_j_root, return_value = 0
        cdef int *self_wd_parent = self.wd_parent
        cdef int *self_col_parent = self.col_parent
        for i from 0 <= i < self.nwords:
            if self_wd_parent[i] == i:
                gamma_i_root = self.wd_find(wd_gamma[i])
                if gamma_i_root != i:
                    return_value = 1
                    self.wd_union(i, gamma_i_root)
        for j from 0 <= j < self.ncols:
            if self_col_parent[j] == j:
                gamma_j_root = self.col_find(col_gamma[j])
                if gamma_j_root != j:
                    return_value = 1
                    self.col_union(j, gamma_j_root)
        return return_value

cdef class PartitionStack:
    """
    Partition stack structure for traversing the search tree during automorphism
    group computation.

    """
    def __new__(self, arg1, arg2=None):
        cdef int k, nwords, ncols
        cdef PartitionStack other
        cdef int *wd_ents, *wd_lvls, *col_ents, *col_lvls

        try:
            self.nrows = int(arg1)
            self.nwords = 1 << self.nrows
            self.ncols = int(arg2)
        except:
            other = arg1
            self.nrows = other.nrows
            self.nwords = other.nwords
            self.ncols = other.ncols
        self.radix = 8*sizeof(int)
        self.flag = (1 << (self.radix-1))

        # data
        self.wd_ents =    <int *> sage_malloc( self.nwords * sizeof(int) )
        self.wd_lvls =    <int *> sage_malloc( self.nwords * sizeof(int) )
        self.col_ents =   <int *> sage_malloc( self.ncols  * sizeof(int) )
        self.col_lvls =   <int *> sage_malloc( self.ncols  * sizeof(int) )

        # scratch space
        self.col_degs =   <int *> sage_malloc( self.ncols  * sizeof(int) )
        self.col_counts = <int *> sage_malloc( self.nwords * sizeof(int) )
        self.col_output = <int *> sage_malloc( self.ncols  * sizeof(int) )
        self.wd_degs =    <int *> sage_malloc( self.nwords * sizeof(int) )
        self.wd_counts =  <int *> sage_malloc( (self.ncols+1)  * sizeof(int) )
        self.wd_output =  <int *> sage_malloc( self.nwords * sizeof(int) )

        if not (self.wd_ents  and self.wd_lvls    and self.col_ents   and self.col_lvls  \
            and self.col_degs and self.col_counts and self.col_output \
            and self.wd_degs  and self.wd_counts  and self.wd_output):
            if self.wd_ents:    sage_free(self.wd_ents)
            if self.wd_lvls:    sage_free(self.wd_lvls)
            if self.col_ents:   sage_free(self.col_ents)
            if self.col_lvls:   sage_free(self.col_lvls)
            if self.col_degs:   sage_free(self.col_degs)
            if self.col_counts: sage_free(self.col_counts)
            if self.col_output: sage_free(self.col_output)
            if self.wd_degs:    sage_free(self.wd_degs)
            if self.wd_counts:  sage_free(self.wd_counts)
            if self.wd_output:  sage_free(self.wd_output)
            raise MemoryError("Memory.")

        if other:
            memcpy(self.wd_ents,  other.wd_ents, self.nwords*(self.radix>>3))
            memcpy(self.wd_lvls,  other.wd_lvls, self.nwords*(self.radix>>3))
            memcpy(self.col_ents, other.col_ents, self.ncols*(self.radix>>3))
            memcpy(self.col_lvls, other.col_lvls, self.ncols*(self.radix>>3))
        else:
            wd_ents = self.wd_ents
            wd_lvls = self.wd_lvls
            col_ents = self.col_ents
            col_lvls = self.col_lvls
            nwords = self.nwords
            ncols = self.ncols
            for k from 0 <= k < nwords-1:
                wd_ents[k] = k
                wd_lvls[k] = nwords
            for k from 0 <= k < ncols-1:
                col_ents[k] = k
                col_lvls[k] = ncols
            wd_ents[nwords-1] = nwords-1
            wd_lvls[nwords-1] = -1
            col_ents[ncols-1] = ncols-1
            col_lvls[ncols-1] = -1

    def __dealloc__(self):
        if self.basis_locations: sage_free(self.basis_locations)
        sage_free(self.wd_ents)
        sage_free(self.wd_lvls)
        sage_free(self.col_ents)
        sage_free(self.col_lvls)
        sage_free(self.col_degs)
        sage_free(self.col_counts)
        sage_free(self.col_output)
        sage_free(self.wd_degs)
        sage_free(self.wd_counts)
        sage_free(self.wd_output)

    def print_data(self):
        """
        Prints all data for self.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: P.print_data() # random - actually "print P.print_data()"
            nwords: 4
            nrows: 2
            ncols: 6
            radix: 32
            wd_ents:
            0
            1
            2
            3
            wd_lvls:
            4
            4
            4
            -1
            col_ents:
            0
            1
            2
            3
            4
            5
            col_lvls:
            6
            6
            6
            6
            6
            -1
            col_degs:
            -1209339024
            145606688
            135493408
            3
            -1210787264
            -1210787232
            col_counts:
            -1209339024
            145666744
            40129536
            21248
            col_output:
            -1209339024
            145654064
            0
            0
            0
            0
            wd_degs:
            -1209339024
            145166112
            16
            3
            wd_counts:
            -1209339024
            146261160
            0
            0
            0
            0
            wd_output:
            -1209339024
            146424680
            135508928
            3

        """
        cdef int i, j
        s = ''
        s += "nwords:" + str(self.nwords) + '\n'
        s += "nrows:" + str(self.nrows) + '\n'
        s += "ncols:" + str(self.ncols) + '\n'
        s += "radix:" + str(self.radix) + '\n'
        s += "wd_ents:" + '\n'
        for i from 0 <= i < self.nwords:
            s += str(self.wd_ents[i]) + '\n'
        s += "wd_lvls:" + '\n'
        for i from 0 <= i < self.nwords:
            s += str(self.wd_lvls[i]) + '\n'
        s += "col_ents:" + '\n'
        for i from 0 <= i < self.ncols:
            s += str(self.col_ents[i]) + '\n'
        s += "col_lvls:" + '\n'
        for i from 0 <= i < self.ncols:
            s += str(self.col_lvls[i]) + '\n'
        s += "col_degs:" + '\n'
        for i from 0 <= i < self.ncols:
            s += str(self.col_degs[i]) + '\n'
        s += "col_counts:" + '\n'
        for i from 0 <= i < self.nwords:
            s += str(self.col_counts[i]) + '\n'
        s += "col_output:" + '\n'
        for i from 0 <= i < self.ncols:
            s += str(self.col_output[i]) + '\n'
        s += "wd_degs:" + '\n'
        for i from 0 <= i < self.nwords:
            s += str(self.wd_degs[i]) + '\n'
        s += "wd_counts:" + '\n'
        for i from 0 <= i < self.ncols:
            s += str(self.wd_counts[i]) + '\n'
        s += "wd_output:" + '\n'
        for i from 0 <= i < self.nwords:
            s += str(self.wd_output[i]) + '\n'
        if self.basis_locations:
            s += "basis_locations:" + '\n'
            j = 1
            while (1 << j) < self.nwords:
                j += 1
            for i from 0 <= i < j:
                s += str(self.basis_locations[i]) + '\n'
        return s

    def __repr__(self):
        """
        Return a string representation of self.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})

        """
        cdef int i, j, k
        s = ''
        for i from 0 <= i < self.nwords:
            s += '({'
            for j from 0 <= j < self.nwords:
                s += str(self.wd_ents[j])
                if self.wd_lvls[j] <= i:
                    s += '},{'
                else:
                    s += ','
            s = s[:-2] + ')\n'
        for i from 0 <= i < self.ncols:
            s += '({'
            for j from 0 <= j < self.ncols:
                s += str(self.col_ents[j])
                if self.col_lvls[j] <= i:
                    s += '},{'
                else:
                    s += ','
            s = s[:-2] + ')\n'
        return s

    def _is_discrete(self, k):
        """
        Returns whether the partition at level k is discrete.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})
            sage: P._is_discrete(4)
            0
            sage: P._is_discrete(5)
            1

        """
        return self.is_discrete(k)

    cdef int is_discrete(self, int k):
        cdef int i
        cdef int *self_col_lvls = self.col_lvls
        for i from 0 <= i < self.ncols:
            if self_col_lvls[i] > k:
                return 0
        return 1

    def _num_cells(self, k):
        """
        Returns the number of cells in the partition at level k.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})
            sage: P._num_cells(3)
            5

        """
        return self.num_cells(k)

    cdef int num_cells(self, int k):
        cdef int i, j = 0
        cdef int *self_wd_lvls = self.wd_lvls
        cdef int *self_col_lvls = self.col_lvls
        for i from 0 <= i < self.nwords:
            if self_wd_lvls[i] <= k:
                j += 1
        for i from 0 <= i < self.ncols:
            if self_col_lvls[i] <= k:
                j += 1
        return j

    def _sat_225(self, k):
        """
        Returns whether the partition at level k satisfies the hypotheses of
        Lemma 2.25 in Brendan McKay's Practical Graph Isomorphism paper (see
        sage/graphs/graph_isom.pyx.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: P._sat_225(3)
            0
            sage: P._sat_225(4)
            1
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})

        """
        return self.sat_225(k)

    cdef int sat_225(self, int k):
        cdef int i, n = self.nwords + self.ncols, in_cell = 0
        cdef int nontrivial_cells = 0, total_cells = self.num_cells(k)
        cdef int *self_wd_lvls = self.wd_lvls
        cdef int *self_col_lvls = self.col_lvls
        if n <= total_cells + 4:
            return 1
        for i from 0 <= i < self.nwords:
            if self_wd_lvls[i] <= k:
                if in_cell:
                    nontrivial_cells += 1
                in_cell = 0
            else:
                in_cell = 1
        in_cell = 0
        for i from 0 <= i < self.ncols:
            if self_col_lvls[i] <= k:
                if in_cell:
                    nontrivial_cells += 1
                in_cell = 0
            else:
                in_cell = 1
        if n == total_cells + nontrivial_cells:
            return 1
        if n == total_cells + nontrivial_cells + 1:
            return 1
        return 0

    def _min_cell_reps(self, k):
        """
        Returns an integer whose bits represent which columns are minimal cell
        representatives.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: a = P._min_cell_reps(2)
            sage: Integer(a).binary()
            '111'
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})

        """
        return self.min_cell_reps(k)

    cdef int min_cell_reps(self, int k):
        cdef int i
        cdef int reps = 1
        cdef int *self_col_lvls = self.col_lvls
        for i from 0 < i < self.ncols:
            if self_col_lvls[i-1] <= k:
                reps += (1 << i)
        return reps

    def _fixed_cols(self, mcrs, k):
        """
        Returns an integer whose bits represent which columns are fixed. For
        efficiency, mcrs is the output of min_cell_reps.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: a = P._fixed_cols(7, 2)
            sage: Integer(a).binary()
            '11'
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})

        """
        return self.fixed_cols(mcrs, k)

    cdef int fixed_cols(self, int mcrs, int k):
        cdef int i
        cdef int fixed = 0
        cdef int *self_col_lvls = self.col_lvls
        for i from 0 <= i < self.ncols:
            if self_col_lvls[i] <= k:
                fixed += (1 << i)
        return fixed & mcrs

    def _first_smallest_nontrivial(self, k):
        """
        Returns an integer representing the first, smallest nontrivial cell of columns.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: a = P._first_smallest_nontrivial(2)
            sage: Integer(a).binary().zfill(32)
            '00000000000000000000000000111100'
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})

        """
        return self.first_smallest_nontrivial(k)

    cdef int first_smallest_nontrivial(self, int k):
        cdef int cell
        cdef int i = 0, j = 0, location = 0, ncols = self.ncols
        cdef int *self_col_lvls = self.col_lvls
        while True:
            if self_col_lvls[i] <= k:
                if i != j and ncols > i - j + 1:
                    ncols = i - j + 1
                    location = j
                j = i + 1
            if self_col_lvls[i] == -1: break
            i += 1
        # location now points to the beginning of the first, smallest,
        # nontrivial cell
        j = location
        while True:
            if self_col_lvls[j] <= k: break
            j += 1
        # j now points to the last element of the cell
        i = self.radix - j - 1                 # the cell is represented in binary, reading from the right:
        cell = (~0 << location) ^ (~0 << j+1)  # <-------            self.radix               ----->
        return cell                            # [0]*(radix-j-1) + [1]*(j-location+1) + [0]*location

    def _dangerous_dont_use_set_ents_lvls(self, col_ents, col_lvls, wd_ents, wd_lvls):
        """
        For debugging only.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            sage: P._dangerous_dont_use_set_ents_lvls([99]*6, [0,3,2,3,5,-1], [4,3,5,6], [3,2,1,-1])
            sage: P
            ({4,3,5,6})
            ({4,3,5},{6})
            ({4,3},{5},{6})
            ({4},{3},{5},{6})
            ({99},{99,99,99,99,99})
            ({99},{99,99,99,99,99})
            ({99},{99,99},{99,99,99})
            ({99},{99},{99},{99},{99,99})
            ({99},{99},{99},{99},{99,99})
            ({99},{99},{99},{99},{99},{99})

        """
        cdef int i
        for i from 0 <= i < len(col_ents):
            self.col_ents[i] = col_ents[i]
        for i from 0 <= i < len(col_lvls):
            self.col_lvls[i] = col_lvls[i]
        for i from 0 <= i < len(wd_ents):
            self.wd_ents[i] = wd_ents[i]
        for i from 0 <= i < len(wd_lvls):
            self.wd_lvls[i] = wd_lvls[i]

    def _col_percolate(self, start, end):
        """
        Do one round of bubble sort on ents.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: P._dangerous_dont_use_set_ents_lvls(range(5,-1,-1), [1,2,2,3,3,-1], range(3,-1,-1), [1,1,2,-1])
            sage: P
            ({3,2,1,0})
            ({3},{2},{1,0})
            ({3},{2},{1},{0})
            ({3},{2},{1},{0})
            ({5,4,3,2,1,0})
            ({5},{4,3,2,1,0})
            ({5},{4},{3},{2,1,0})
            ({5},{4},{3},{2},{1},{0})
            ({5},{4},{3},{2},{1},{0})
            ({5},{4},{3},{2},{1},{0})
            sage: P._wd_percolate(0,3)
            sage: P._col_percolate(0,5)
            sage: P
            ({0,3,2,1})
            ({0},{3},{2,1})
            ({0},{3},{2},{1})
            ({0},{3},{2},{1})
            ({0,5,4,3,2,1})
            ({0},{5,4,3,2,1})
            ({0},{5},{4},{3,2,1})
            ({0},{5},{4},{3},{2},{1})
            ({0},{5},{4},{3},{2},{1})
            ({0},{5},{4},{3},{2},{1})

        """
        self.col_percolate(start, end)

    cdef void col_percolate(self, int start, int end):
        cdef int i, temp
        cdef int *self_col_ents = self.col_ents
        for i from end >= i > start:
            if self_col_ents[i] < self_col_ents[i-1]:
                temp = self.col_ents[i]
                self_col_ents[i] = self_col_ents[i-1]
                self_col_ents[i-1] = temp

    def _wd_percolate(self, start, end):
        """
        Do one round of bubble sort on ents.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: P._dangerous_dont_use_set_ents_lvls(range(5,-1,-1), [1,2,2,3,3,-1], range(3,-1,-1), [1,1,2,-1])
            sage: P
            ({3,2,1,0})
            ({3},{2},{1,0})
            ({3},{2},{1},{0})
            ({3},{2},{1},{0})
            ({5,4,3,2,1,0})
            ({5},{4,3,2,1,0})
            ({5},{4},{3},{2,1,0})
            ({5},{4},{3},{2},{1},{0})
            ({5},{4},{3},{2},{1},{0})
            ({5},{4},{3},{2},{1},{0})
            sage: P._wd_percolate(0,3)
            sage: P._col_percolate(0,5)
            sage: P
            ({0,3,2,1})
            ({0},{3},{2,1})
            ({0},{3},{2},{1})
            ({0},{3},{2},{1})
            ({0,5,4,3,2,1})
            ({0},{5,4,3,2,1})
            ({0},{5},{4},{3,2,1})
            ({0},{5},{4},{3},{2},{1})
            ({0},{5},{4},{3},{2},{1})
            ({0},{5},{4},{3},{2},{1})

        """
        self.wd_percolate(start, end)

    cdef void wd_percolate(self, int start, int end):
        cdef int i, temp
        cdef int *self_wd_ents = self.wd_ents
        for i from end >= i > start:
            if self_wd_ents[i] < self_wd_ents[i-1]:
                temp = self.wd_ents[i]
                self_wd_ents[i] = self_wd_ents[i-1]
                self_wd_ents[i-1] = temp

    def _split_column(self, int v, int k):
        """
        Split column v out, placing it before the rest of the cell it was in.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})
            sage: P = PartitionStack(2, 6)
            sage: P._split_column(0,1)
            0
            sage: P._split_column(2,2)
            1
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,2,1,3,4,5})
            ({0},{2,1,3,4,5})
            ({0},{2},{1,3,4,5})
            ({0},{2},{1,3,4,5})
            ({0},{2},{1,3,4,5})
            ({0},{2},{1,3,4,5})

        """
        return self.split_column(v, k)

    cdef int split_column(self, int v, int k):
        cdef int i = 0, j
        cdef int *self_col_ents = self.col_ents
        cdef int *self_col_lvls = self.col_lvls
        while self_col_ents[i] != v: i += 1
        j = i
        while self_col_lvls[i] > k: i += 1
        if j == 0 or self_col_lvls[j-1] <= k:
            self.col_percolate(j+1, i)
        else:
            while j != 0 and self_col_lvls[j-1] > k:
                self_col_ents[j] = self_col_ents[j-1]
                j -= 1
            self_col_ents[j] = v
        self_col_lvls[j] = k
        return j

    def _col_degree(self, C, col, wd_ptr, k):
        """
        Returns the number of words in the cell specified by wd_ptr that have a
        1 in the col-th column.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: M = Matrix(GF(2), [[1,1,1,1,0,0],[0,0,1,1,1,1]])
            sage: B = BinaryCode(M)
            sage: B
            Binary [6,2] linear code, generator matrix
            [111100]
            [001111]
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})
            sage: P._col_degree(B, 2, 0, 2)
            2

        """
        return self.col_degree(C, col, wd_ptr, k)

    cdef int col_degree(self, BinaryCode CG, int col, int wd_ptr, int k):
        cdef int i = 0
        cdef int *self_wd_lvls = self.wd_lvls, *self_wd_ents = self.wd_ents
        col = self.col_ents[col]
        while True:
            if CG.is_one(self_wd_ents[wd_ptr], col): i += 1
            if self_wd_lvls[wd_ptr] > k: wd_ptr += 1
            else: break
        return i

    def _wd_degree(self, C, wd, col_ptr, k):
        """
        Returns the number of columns in the cell specified by col_ptr that are
        1 in wd.

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: M = Matrix(GF(2), [[1,1,1,1,0,0],[0,0,1,1,1,1]])
            sage: B = BinaryCode(M)
            sage: B
            Binary [6,2] linear code, generator matrix
            [111100]
            [001111]
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})
            sage: P._wd_degree(B, 1, 1, 1)
            3

        """
        cdef int *ham_wts = hamming_weights()
        result = self.wd_degree(C, wd, col_ptr, k, ham_wts)
        sage_free(ham_wts)
        return result

    cdef int wd_degree(self, BinaryCode CG, int wd, int col_ptr, int k, int *ham_wts):

        cdef int mask = (1 << col_ptr)
        cdef int *self_col_lvls = self.col_lvls
        while self_col_lvls[col_ptr] > k:
            col_ptr += 1
            mask += (1 << col_ptr)
        mask &= CG.words[self.wd_ents[wd]]
        return ham_wts[mask & 65535] + ham_wts[(mask >> 16) & 65535]

    def _sort_cols(self, start, degrees, k):
        """
        Essentially a counting sort, but on only one cell of the partition.

        INPUT:
            start -- location of the beginning of the cell
            k -- at what level of refinement the partition of interest lies
            degrees -- the counts to sort by

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: P._sort_cols(1, [0,2,2,1,1], 1)
            2
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,4,5,2,3})
            ({0},{1},{4,5},{2,3})
            ({0},{1},{4,5},{2,3})
            ({0},{1},{4},{5},{2,3})
            ({0},{1},{4},{5},{2,3})
            ({0},{1},{4},{5},{2},{3})

        """
        cdef int i
        for i from 0 <= i < len(degrees):
            self.col_degs[i] = degrees[i]
        return self.sort_cols(start, k)

    cdef int sort_cols(self, int start, int k):
        cdef int i, j, max, max_location, self_ncols = self.ncols
        cdef int self_nwords = self.nwords, ii
        cdef int *self_col_counts = self.col_counts
        cdef int *self_col_lvls = self.col_lvls
        cdef int *self_col_degs = self.col_degs
        cdef int *self_col_ents = self.col_ents
        cdef int *self_col_output = self.col_output
        for ii from 0 <= ii < self_nwords:
            self_col_counts[ii] = 0
        i = 0
        while self_col_lvls[i+start] > k:
            self_col_counts[self_col_degs[i]] += 1
            i += 1
        self_col_counts[self_col_degs[i]] += 1

        # i+start is the right endpoint of the cell now
        max = self_col_counts[0]
        max_location = 0
        for ii from 0 < ii < self_nwords:
            if self_col_counts[ii] > max:
                max = self_col_counts[ii]
                max_location = ii
            self_col_counts[ii] += self_col_counts[ii-1]

        for j from i >= j >= 0:
            self_col_counts[self_col_degs[j]] -= 1
            self_col_output[self_col_counts[self_col_degs[j]]] = self_col_ents[start+j]

        max_location = self_col_counts[max_location] + start

        for j from 0 <= j <= i:
            self_col_ents[start+j] = self_col_output[j]

        ii = 1
        while ii < self_nwords and self_col_counts[ii] <= i:
            if self_col_counts[ii] > 0:
                self_col_lvls[start + self_col_counts[ii] - 1] = k
            self.col_percolate(start + self_col_counts[ii-1], start + self_col_counts[ii] - 1)
            ii += 1

        return max_location

    def _sort_wds(self, start, degrees, k):
        """
        Essentially a counting sort, but on only one cell of the partition.

        INPUT:
            start -- location of the beginning of the cell
            k -- at what level of refinement the partition of interest lies
            degrees -- the counts to sort by

        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(3, 6)
            sage: P._sort_wds(0, [0,0,3,3,3,3,2,2], 1)
            4
            sage: P
            ({0,1,6,7,2,3,4,5})
            ({0,1},{6,7},{2,3,4,5})
            ({0,1},{6,7},{2,3,4,5})
            ({0,1},{6,7},{2,3,4,5})
            ({0,1},{6,7},{2,3,4,5})
            ({0,1},{6,7},{2,3,4,5})
            ({0,1},{6,7},{2,3,4,5})
            ({0,1},{6,7},{2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})
            ({0,1,2,3,4,5})

        """
        cdef int i
        for i from 0 <= i < len(degrees):
            self.wd_degs[i] = degrees[i]
        return self.sort_wds(start, k)

    cdef int sort_wds(self, int start, int k):
        cdef int i, j, max, max_location, self_nwords = self.nwords
        cdef int ii, self_ncols = self.ncols
        cdef int *self_wd_counts = self.wd_counts
        cdef int *self_wd_lvls = self.wd_lvls
        cdef int *self_wd_degs = self.wd_degs
        cdef int *self_wd_ents = self.wd_ents
        cdef int *self_wd_output = self.wd_output

        for ii from 0 <= ii < self_ncols+1:
            self_wd_counts[ii] = 0
        i = 0
        while self_wd_lvls[i+start] > k:
            self_wd_counts[self_wd_degs[i]] += 1
            i += 1
        self_wd_counts[self_wd_degs[i]] += 1

        # i+start is the right endpoint of the cell now
        max = self_wd_counts[0]
        max_location = 0
        for ii from 0 < ii < self_ncols+1:
            if self_wd_counts[ii] > max:
                max = self_wd_counts[ii]
                max_location = ii
            self_wd_counts[ii] += self_wd_counts[ii-1]

        for j from i >= j >= 0:
            if j > i: break # cython bug with ints...
            self_wd_counts[self_wd_degs[j]] -= 1
            self_wd_output[self_wd_counts[self_wd_degs[j]]] = self_wd_ents[start+j]

        max_location = self_wd_counts[max_location] + start

        for j from 0 <= j <= i:
            self_wd_ents[start+j] = self_wd_output[j]

        ii = 1
        while ii < self_ncols+1 and self_wd_counts[ii] <= i:
            if self_wd_counts[ii] > 0:
                self_wd_lvls[start + self_wd_counts[ii] - 1] = k
            self.wd_percolate(start + self_wd_counts[ii-1], start + self_wd_counts[ii] - 1)
            ii += 1

        return max_location

    def _refine(self, k, alpha, CG):
        """
        EXAMPLE:

            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: M = Matrix(GF(2), [[1,1,1,1,0,0,0,0],[0,0,1,1,1,1,0,0],[0,0,0,0,1,1,1,1],[1,0,1,0,1,0,1,0]])
            sage: B = BinaryCode(M)
            sage: P = PartitionStack(4, 8)
            sage: P._refine(1, [[0,0],[1,0]], B)
            304
            sage: P._split_column(0, 2)
            0
            sage: P._refine(2, [[0,0]], B)
            346
            sage: P._split_column(1, 3)
            1
            sage: P._refine(3, [[0,1]], B)
            558
            sage: P._split_column(2, 4)
            2
            sage: P._refine(4, [[0,2]], B)
            1713
            sage: P._split_column(3, 5)
            3
            sage: P._refine(5, [[0,3]], B)
            641
            sage: P._split_column(4, 6)
            4
            sage: P._refine(6, [[0,4]], B)
            1609
            sage: P._is_discrete(5)
            0
            sage: P._is_discrete(6)
            1
            sage: P
            ({0,4,6,2,13,9,11,15,10,14,12,8,7,3,1,5})
            ({0},{4,6,2,13,9,11,15,10,14,12,8,7,3,1},{5})
            ({0},{4,6,2,13,9,11,15},{10,14,12,8,7,3,1},{5})
            ({0},{4,6,2},{13,9,11,15},{10,14,12,8},{7,3,1},{5})
            ({0},{4},{6,2},{13,9},{11,15},{10,14},{12,8},{7,3},{1},{5})
            ({0},{4},{6,2},{13,9},{11,15},{10,14},{12,8},{7,3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0},{4},{6},{2},{13},{9},{11},{15},{10},{14},{12},{8},{7},{3},{1},{5})
            ({0,1,2,3,4,7,6,5})
            ({0,1,2,3,4,7,6,5})
            ({0},{1,2,3,4,7,6,5})
            ({0},{1},{2,3,4,7,6,5})
            ({0},{1},{2},{3,4,7,6,5})
            ({0},{1},{2},{3},{4,7,6,5})
            ({0},{1},{2},{3},{4},{7},{6},{5})
            ({0},{1},{2},{3},{4},{7},{6},{5})

        """
        cdef int i, alpha_length = len(alpha)
        cdef int *_alpha = <int *> sage_malloc( (self.nwords + self.ncols) * sizeof(int) )
        cdef int *ham_wts = hamming_weights()
        if not _alpha:
            sage_free(_alpha)
            raise MemoryError("Memory.")
        for i from 0 <= i < alpha_length:
            if alpha[i][0]:
                _alpha[i] = alpha[i][1] ^ self.flag
            else:
                _alpha[i] = alpha[i][1]
        result = self.refine(k, _alpha, alpha_length, CG, ham_wts)
        sage_free(_alpha)
        sage_free(ham_wts)
        return result

    cdef int refine(self, int k, int *alpha, int alpha_length, BinaryCode CG, int *ham_wts):
        cdef int q, r, s, t, flag = self.flag, self_ncols = self.ncols
        cdef int t_w, self_nwords = self.nwords, invariant = 0, i, j, m = 0
        cdef int *self_wd_degs = self.wd_degs, *self_wd_lvls = self.wd_lvls, *self_col_lvls = self.col_lvls
        cdef int *self_col_degs = self.col_degs
        while not self.is_discrete(k) and m < alpha_length:
#            print "m:", m
#            print "alpha:", ','.join(['w'+str(alpha[i]^flag) if alpha[i]&flag else 'c'+str(alpha[i]) for i from 0 <= i < alpha_length])
            invariant += 1
            j = 0
            if alpha[m] & flag:
                while j < self_ncols:
                    i = j; s = 0
                    invariant += 8
                    while True:
                        self_col_degs[i-j] = self.col_degree(CG, i, alpha[m]^flag, k)
                        if s == 0 and self_col_degs[i-j] != self_col_degs[0]: s = 1
                        i += 1
                        if self_col_lvls[i-1] <= k: break
                    if s:
                        invariant += 8
                        t = self.sort_cols(j, k)
                        invariant += t + self_col_degs[i-j-1]
                        q = m
                        while q < alpha_length:
                            if alpha[q] == j:
                                alpha[q] = t
                                break
                            q += 1
                        r = j
                        while True:
                            if r == 0 or self.col_lvls[r-1] == k:
                                if r != t:
                                    alpha[alpha_length] = r
                                    alpha_length += 1
                            r += 1
                            if r >= i: break
                        while self_col_lvls[j] > k:
                            j += 1
                        j += 1
                        invariant += (i-j)
                    else: j = i
            else:
                while j < self.nwords:
                    i = j; s = 0
                    invariant += 64
                    while True:
                        self_wd_degs[i-j] = self.wd_degree(CG, i, alpha[m], k, ham_wts)
                        if s == 0 and self_wd_degs[i-j] != self_wd_degs[0]: s = 1
                        i += 1
                        if self_wd_lvls[i-1] <= k: break
                    if s:
                        invariant += 64
                        t_w = self.sort_wds(j, k)
                        invariant += t_w + self_wd_degs[i-j-1]
                        q = m
                        j ^= flag
                        while q < alpha_length:
                            if alpha[q] == j:
                                alpha[q] = t_w ^ flag
                                break
                            q += 1
                        j ^= flag
                        r = j
                        while True:
                            if r == 0 or self.wd_lvls[r-1] == k:
                                if r != t_w:
                                    alpha[alpha_length] = r^flag
                                    alpha_length += 1
                            r += 1
                            if r >= i: break
                        while self_wd_lvls[j] > k:
                            j += 1
                        j += 1
                        invariant += (i-j)
                    else: j = i
            m += 1
        return invariant

    def _clear(self, k):
        """
        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(2, 6)
            sage: [P._split_column(i,i+1) for i in range(5)]
            [0, 1, 2, 3, 4]
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})
            ({0},{1},{2},{3},{4},{5})
            sage: P._clear(2)
            sage: P
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3})
            ({0,1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1,2,3,4,5})
            ({0},{1},{2,3,4,5})
            ({0},{1},{2},{3,4,5})
            ({0},{1},{2},{3},{4,5})

        """
        self.clear(k)

    cdef void clear(self, int k):
        cdef int i = 0, j = 0
        cdef int *wd_lvls = self.wd_lvls, *col_lvls = self.col_lvls
        while wd_lvls[i] != -1:
            if wd_lvls[i] >= k:
                wd_lvls[i] += 1
            if wd_lvls[i] < k:
                self.wd_percolate(j, i)
                j = i + 1
            i+=1
        i = 0
        j = 0
        while col_lvls[i] != -1:
            if col_lvls[i] >= k:
                col_lvls[i] += 1
            if col_lvls[i] < k:
                self.col_percolate(j, i)
                j = i + 1
            i+=1

    def _cmp(self, other, C):
        """
        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: M = Matrix(GF(2), [[1,1,1,1,0,0,0,0],[0,0,1,1,1,1,0,0],[0,0,0,0,1,1,1,1],[1,0,1,0,1,0,1,0]])
            sage: B = BinaryCode(M)
            sage: P = PartitionStack(4, 8)
            sage: P._refine(0, [[0,0],[1,0]], B)
            304
            sage: P._split_column(0, 1)
            0
            sage: P._refine(1, [[0,0]], B)
            346
            sage: P._split_column(1, 2)
            1
            sage: P._refine(2, [[0,1]], B)
            558
            sage: P._split_column(2, 3)
            2
            sage: P._refine(3, [[0,2]], B)
            1713
            sage: P._split_column(4, 4)
            4
            sage: P._refine(4, [[0,4]], B)
            1609
            sage: P._is_discrete(4)
            1
            sage: Q = PartitionStack(P)
            sage: Q._clear(4)
            sage: Q._split_column(5, 4)
            4
            sage: Q._refine(4, [[0,4]], B)
            1609
            sage: Q._is_discrete(4)
            1
            sage: Q._cmp(P, B)
            1

        """
        return self.cmp(other, C)

    cdef int cmp(self, PartitionStack other, BinaryCode CG):
        cdef int *cur_span = self.col_counts # grab spare scratch space, size self.nwords.
        cdef int *self_wd_ents = self.wd_ents
        cdef int i, j, k, l, m, word, span = 1, ncols = self.ncols, nwords = self.nwords
        cur_span[0] = 0
        for i from 0 <= i < CG.nwords/2 + 1:
            word = self_wd_ents[i]
            k = 0
            while k < span and word != cur_span[k]:
                k += 1
            if k == span:
                if (span << 1) != nwords:
                    for j from 0 <= j < span:
                        cur_span[span+j] = cur_span[j] ^ word
                span << 1
                for j from 0 <= j < ncols:
                    l = CG.is_one(self.wd_ents[i], self.col_ents[j])
                    m = CG.is_one(other.wd_ents[i], other.col_ents[j])
                    if l != m:
                        return l - m
                if span == nwords: break
        return 0

    def print_basis(self):
        """
        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(4, 8)
            sage: P._dangerous_dont_use_set_ents_lvls(range(8), range(7)+[-1], [4,7,12,11,1,9,3,0,2,5,6,8,10,13,14,15], [0]*16)
            sage: P
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({0},{1,2,3,4,5,6,7})
            ({0},{1},{2,3,4,5,6,7})
            ({0},{1},{2},{3,4,5,6,7})
            ({0},{1},{2},{3},{4,5,6,7})
            ({0},{1},{2},{3},{4},{5,6,7})
            ({0},{1},{2},{3},{4},{5},{6,7})
            ({0},{1},{2},{3},{4},{5},{6},{7})
            ({0},{1},{2},{3},{4},{5},{6},{7})
            sage: P._find_basis()
            sage: P.print_basis()
            basis_locations:
            4
            8
            0
            11

        """
        cdef int i, j
        if self.basis_locations:
            print "basis_locations:"
            j = 1
            while (1 << j) < self.nwords:
                j += 1
            for i from 0 <= i < j:
                print self.basis_locations[i]

    def _find_basis(self):
        """
        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: P = PartitionStack(4, 8)
            sage: P._dangerous_dont_use_set_ents_lvls(range(8), range(7)+[-1], [4,7,12,11,1,9,3,0,2,5,6,8,10,13,14,15], [0]*16)
            sage: P
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({4},{7},{12},{11},{1},{9},{3},{0},{2},{5},{6},{8},{10},{13},{14},{15})
            ({0},{1,2,3,4,5,6,7})
            ({0},{1},{2,3,4,5,6,7})
            ({0},{1},{2},{3,4,5,6,7})
            ({0},{1},{2},{3},{4,5,6,7})
            ({0},{1},{2},{3},{4},{5,6,7})
            ({0},{1},{2},{3},{4},{5},{6,7})
            ({0},{1},{2},{3},{4},{5},{6},{7})
            ({0},{1},{2},{3},{4},{5},{6},{7})
            sage: P._find_basis()
            sage: P.print_basis()
            basis_locations:
            4
            8
            0
            11

        """
        cdef int i
        cdef int *ham_wts = hamming_weights()
        self.find_basis(ham_wts)
        sage_free(ham_wts)

    cdef void find_basis(self, int *ham_wts):
        cdef int i = 0, j, k, nwords = self.nwords, weight, basis_elts = 0, nrows = self.nrows
        cdef int *self_wd_ents = self.wd_ents
        if not self.basis_locations:
            self.basis_locations = <int *> sage_malloc( nrows * sizeof(int) )
        if not self.basis_locations:
            raise MemoryError("Memory.")
        while i < nwords:
            j = self_wd_ents[i]
            weight = ham_wts[j & 65535] + ham_wts[(j>>16) & 65535]
            if weight == 1:
                basis_elts += 1
                k = 0
                while not (1<<k) & j:
                    k += 1
                self.basis_locations[k] = i
                if basis_elts == nrows: break
            i += 1

    def _get_permutation(self, other):
        """
        EXAMPLE:
            sage: import sage.coding.binary_code
            sage: from sage.coding.binary_code import *
            sage: M = Matrix(GF(2), [[1,1,1,1,0,0,0,0],[0,0,1,1,1,1,0,0],[0,0,0,0,1,1,1,1],[1,0,1,0,1,0,1,0]])
            sage: B = BinaryCode(M)
            sage: P = PartitionStack(4, 8)
            sage: P._refine(0, [[0,0],[1,0]], B)
            304
            sage: P._split_column(0, 1)
            0
            sage: P._refine(1, [[0,0]], B)
            346
            sage: P._split_column(1, 2)
            1
            sage: P._refine(2, [[0,1]], B)
            558
            sage: P._split_column(2, 3)
            2
            sage: P._refine(3, [[0,2]], B)
            1713
            sage: P._split_column(4, 4)
            4
            sage: P._refine(4, [[0,4]], B)
            1609
            sage: P._is_discrete(4)
            1
            sage: Q = PartitionStack(P)
            sage: Q._clear(4)
            sage: Q._split_column(5, 4)
            4
            sage: Q._refine(4, [[0,4]], B)
            1609
            sage: Q._is_discrete(4)
            1
            sage: P._get_permutation(Q)
            ([1, 2, 4, 8], [0, 1, 2, 3, 5, 4, 6, 7])

        """
        cdef int i
        cdef int *ham_wts = hamming_weights()
        cdef int *basis_g = <int *> sage_malloc( self.nrows * sizeof(int) )
        cdef int *col_g = <int *> sage_malloc( self.ncols * sizeof(int) )
        if not (basis_g and col_g):
            if basis_g: sage_free(basis_g)
            if col_g: sage_free(col_g)
            raise MemoryError("Memory.")
        self.get_permutation(other, basis_g, col_g, ham_wts)
        sage_free(ham_wts)
        basis_l = [basis_g[i] for i from 0 <= i < self.nrows]
        col_l = [col_g[i] for i from 0 <= i < self.ncols]
        sage_free(basis_g)
        sage_free(col_g)
        return basis_l, col_l

    cdef void get_permutation(self, PartitionStack other, int *basis_gamma, int *col_gamma, int *ham_wts):
        cdef int i
        cdef int *bas_loc, *self_wd_ents = self.wd_ents, *self_col_ents = self.col_ents, *other_col_ents = other.col_ents
        if not other.basis_locations:
            other.find_basis(ham_wts)
        bas_loc = other.basis_locations
        # basis_gamma[i] := image of the ith row as linear comb of rows
        for i from 0 <= i < self.nrows:
            basis_gamma[i] = self_wd_ents[bas_loc[i]]
        for i from 0 <= i < self.ncols:
            col_gamma[other_col_ents[i]] = self_col_ents[i]

################################################################################
################################################################################
################################################################################

cdef class BinaryCodeClassifier:

    def __new__(self):
        self.ham_wts = hamming_weights()

    def __dealloc__(self):
        sage_free(self.ham_wts)



















#def classify(BinaryCode C, lab=True, verbosity=0):
#    """
#    """
#    cdef int i, j # local variables
#    cdef OrbitPartition Theta # keeps track of which vertices have been
#                              # discovered to be equivalent
#    cdef int index = 0, size = 1
#    cdef int L = 100
#    cdef int **Phi, **Omega
#    cdef int l = -1
#    cdef PartitionStack nu, zeta, rho
#    cdef int k_rho
#    cdef int k = 0
#    cdef int h = -1
#    cdef int hb
#    cdef int hh = 1
#    cdef int ht
#    cdef mpz_t *Lambda_mpz, *zf_mpz, *zb_mpz
#    cdef int hzf
#    cdef int hzb = -1
#    cdef int *basis_gamma
#    cdef int *col_gamma
#    cdef int *alpha
#    cdef int *v
#    cdef int *e
#    cdef int state
#    cdef int tvc, tvh, nwords = C.nwords, ncols = C.ncols, n = nwords + ncols, nrows = C.nrows

#    # trivial case
#    if ncols == 0:
#        return [], {}
#    elif nwords == 0 and ncols == 1:
#        return [], {0:0}
#    elif nwords == 0:
#        output1 = []
#        dd = {}
#        for i from 0 <= i < ncols-1:
#            dd[i] = i
#            perm = range(ncols)
#            perm[i] = i+1
#            perm[i+1] = i
#            output1.append(perm)
#        dd[ncols-1] = ncols-1
#        return output1, dd

#    # allocate int pointers
#    Phi = <int **> sage_malloc(L * sizeof(int *))
#    Omega = <int **> sage_malloc(L * sizeof(int *))

#    # allocate GMP int pointers
#    Lambda_mpz = <mpz_t *> sage_malloc((ncols+2)*sizeof(mpz_t))
#    zf_mpz     = <mpz_t *> sage_malloc((ncols+2)*sizeof(mpz_t))
#    zb_mpz     = <mpz_t *> sage_malloc((ncols+2)*sizeof(mpz_t))

#    # check for memory errors
#    if not (Phi and Omega and Lambda_mpz and zf_mpz and zb_mpz):
#        if Lambda_mpz: sage_free(Lambda_mpz)
#        if zf_mpz: sage_free(zf_mpz)
#        if zb_mpz: sage_free(zb_mpz)
#        if Phi: sage_free(Phi)
#        if Omega: sage_free(Omega)
#        raise MemoryError("Error allocating memory.")

#    # allocate int arrays
#    basis_gamma = <int *> sage_malloc(nrows*sizeof(int))
#    col_gamma = <int *> sage_malloc(ncols*sizeof(int))
#    Phi[0] = <int *> sage_malloc(L*ncols*sizeof(int))
#    Omega[0] = <int *> sage_malloc(L*ncols*sizeof(int))
#    alpha = <int *> sage_malloc(4*ncols*sizeof(int))
#    v = <int *> sage_malloc(ncols*sizeof(int))
#    e = <int *> sage_malloc(ncols*sizeof(int))

#    # check for memory errors
#    if not (basis_gamma and col_gamma and Phi[0] and Omega[0] and alpha and v and e):
#        if basis_gamma: sage_free(basis_gamma)
#        if col_gamma: sage_free(col_gamma)
#        if Phi[0]: sage_free(Phi[0])
#        if Omega[0]: sage_free(Omega[0])
#        if alpha: sage_free(alpha)
#        if v: sage_free(v)
#        if e: sage_free(e)
#        sage_free(Lambda_mpz)
#        sage_free(zf_mpz)
#        sage_free(zb_mpz)
#        sage_free(Phi)
#        sage_free(Omega)
#        raise MemoryError("Error allocating memory.")

#    # setup double index arrays
