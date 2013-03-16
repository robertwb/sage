"""
Multidimensional enumeration

AUTHORS:

- Joel B. Mohler (2006-10-12)

- William Stein (2006-07-19)

- Jon Hanke
"""

########################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
########################################################################

import misc

def _len(L):
    """
    Determines the length of L.

    Uses either ``cardinality`` or ``__len__`` as appropriate.

    EXAMPLES::

        sage: from sage.misc.mrange import _len
        sage: _len(ZZ)
        +Infinity
        sage: _len(range(4))
        4
        sage: _len(4)
        Traceback (most recent call last):
        ...
        TypeError: object of type 'sage.rings.integer.Integer' has no len()
    """
    try:
        return L.cardinality()
    except AttributeError:
        return len(L)

def _is_finite(L):
    """
    Determines whether ``L`` is finite.

    If ``L`` implements none of ``is_finite``, ``cardinality`` or
    ``__len__``, we assume it is finite for speed reasons.

    EXAMPLES::

        sage: from sage.misc.mrange import _is_finite
        sage: _is_finite(ZZ)
        False
        sage: _is_finite(range(4))
        True
        sage: _is_finite([])
        True
        sage: _is_finite(xrange(10^8))
        True
    """
    try:
        return L.is_finite()
    except AttributeError:
        try:
            n = _len(L)
        except (TypeError, AttributeError):
            # We assume L is finite for speed reasons
            return True
        from sage.rings.infinity import infinity
        if n is infinity:
            return False
        return True

def _xmrange_iter( iter_list, typ=list ):
    """
    This implements the logic for mrange_iter and xmrange_iter.

    Note that with typ==list, we will be returning a new copy each
    iteration. This makes it OK to modified the returned list. This
    functionality is relied on in the polynomial iterators. Here's a
    doc-test to prove this::

        sage: iter = sage.misc.mrange._xmrange_iter( [[1,2],[1,3]] )
        sage: l1 = iter.next()
        sage: l2 = iter.next()
        sage: l1 is l2
        False

    However, if you would like to re-use the list object::

        sage: iter = sage.misc.mrange._xmrange_iter( [[1,2],[1,3]], lambda x: x )
        sage: l1 = iter.next()
        sage: l2 = iter.next()
        sage: l1 is l2  # eeek, this is freaky!
        True

    We check that #14285 has been resolved::

        sage: iter = sage.misc.mrange._xmrange_iter([ZZ,[]])
        sage: iter.next()
        Traceback (most recent call last):
        ...
        StopIteration
    """
    if len(iter_list) == 0:
        yield ()
        return
    # If any iterator in the list is infinite we need to be more careful
    if any(not _is_finite(L) for L in iter_list):
        for L in iter_list:
            try:
                n = _len(L)
            except TypeError:
                continue
        if n == 0:
            return
    curr_iters = [iter(i) for i in iter_list]
    curr_elt = [i.next() for i in curr_iters[:-1]] + [None]
    place = len(iter_list) - 1
    while True:
        try:
            while True:
                curr_elt[place] = curr_iters[place].next()
                if place < len(iter_list) - 1:
                    place += 1
                    curr_iters[place] = iter(iter_list[place])
                    continue
                else:
                    yield typ(curr_elt)
        except StopIteration:
            place -= 1
            if place == -1:
                return

def mrange_iter(iter_list, typ=list):
    """
    Return the multirange list derived from the given list of
    iterators.

    This is the list version of xmrange_iter. Use xmrange_iter for
    the iterator.

    More precisely, return the iterator over all objects of type typ of
    n-tuples of Python ints with entries between 0 and the integers in
    the sizes list. The iterator is empty if sizes is empty or contains
    any non-positive integer.

    INPUT:


    -  ``iter_list`` - a finite iterable of finite iterables

    -  ``typ`` - (default: list) a type or class; more
       generally, something that can be called with a list as input.


    OUTPUT: a list

    EXAMPLES::

        sage: mrange_iter([range(3),[0,2]])
        [[0, 0], [0, 2], [1, 0], [1, 2], [2, 0], [2, 2]]
        sage: mrange_iter([['Monty','Flying'],['Python','Circus']], tuple)
        [('Monty', 'Python'), ('Monty', 'Circus'), ('Flying', 'Python'), ('Flying', 'Circus')]
        sage: mrange_iter([[2,3,5,7],[1,2]], sum)
        [3, 4, 4, 5, 6, 7, 8, 9]

    Examples that illustrate empty multi-ranges::

        sage: mrange_iter([range(5),xrange(3),xrange(-2)])
        []
        sage: mrange_iter([range(5),range(3),range(0)])
        []

    This example isn't empty, and shouldn't be. See trac #6561.

    ::

        sage: mrange_iter([])
        [()]

    AUTHORS:

    - Joel B. Mohler
    """
    return list(_xmrange_iter(iter_list, typ))

class xmrange_iter:
    """
    Return the multirange iterate derived from the given iterators and
    type.

    .. note::

       This basically gives you the Cartesian product of sets.

    More precisely, return the iterator over all objects of type typ of
    n-tuples of Python ints with entries between 0 and the integers in
    the sizes list. The iterator is empty if sizes is empty or contains
    any non-positive integer.

    Use mrange_iter for the non-iterator form.

    INPUT:


    - ``iter_list`` - a list of objects usable as iterators (possibly
       lists)

    - ``typ`` - (default: list) a type or class; more generally,
       something that can be called with a list as input.


    OUTPUT: a generator

    EXAMPLES: We create multi-range iterators, print them and also
    iterate through a tuple version.

    ::

        sage: z = xmrange_iter([xrange(3),xrange(2)]);z
        xmrange_iter([xrange(3), xrange(2)])
        sage: z = xmrange_iter([range(3),range(2)], tuple);z
        xmrange_iter([[0, 1, 2], [0, 1]], <type 'tuple'>)
        sage: for a in z:
        ...    print a
        (0, 0)
        (0, 1)
        (1, 0)
        (1, 1)
        (2, 0)
        (2, 1)

    We illustrate a few more iterations.

    ::

        sage: list(xmrange_iter([range(3),range(2)]))
        [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]]
        sage: list(xmrange_iter([range(3),range(2)], tuple))
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

    Here we compute the sum of each element of the multi-range
    iterator::

        sage: list(xmrange_iter([range(3),range(2)], sum))
        [0, 1, 1, 2, 2, 3]

    Next we compute the product::

        sage: list(xmrange_iter([range(3),range(2)], prod))
        [0, 0, 0, 1, 0, 2]

    Examples that illustrate empty multi-ranges.

    ::

        sage: list(xmrange_iter([xrange(5),xrange(3),xrange(-2)]))
        []
        sage: list(xmrange_iter([xrange(5),xrange(3),xrange(0)]))
        []

    This example isn't empty, and shouldn't be. See trac #6561.

    ::

        sage: list(xmrange_iter([]))
        [()]

    We use a multi-range iterator to iterate through the Cartesian
    product of sets.

    ::

        sage: X = ['red', 'apple', 389]
        sage: Y = ['orange', 'horse']
        sage: for i,j in xmrange_iter([X, Y], tuple):
        ...    print (i, j)
        ('red', 'orange')
        ('red', 'horse')
        ('apple', 'orange')
        ('apple', 'horse')
        (389, 'orange')
        (389, 'horse')

    AUTHORS:

    - Joel B. Mohler
    """
    def __init__(self, iter_list, typ=list):
        self.iter_list = iter_list
        self.typ = typ

    def __repr__(self):
        if self.typ == list:
            return 'xmrange_iter(%s)'%self.iter_list
        else:
            return 'xmrange_iter(%s, %s)'%(self.iter_list, self.typ)

    def __iter__(self):
        return _xmrange_iter(self.iter_list, self.typ)

    def __len__(self):
        """
        EXAMPLES::

            sage: C = cartesian_product_iterator([xrange(3), xrange(4)])
            sage: len(C)
            12
            sage: len(cartesian_product_iterator([]))
            1
            sage: len(cartesian_product_iterator([ZZ,[]]))
            0
        """
        n = self.cardinality()
        try:
            n = int(n)
            if not isinstance(n, int): # could be a long
                raise TypeError
        except TypeError:
            raise TypeError("This object's length is too large for Python")
        return n

    def cardinality(self):
        """
        EXAMPLES::

            sage: C = cartesian_product_iterator([xrange(3), xrange(4)])
            sage: C.cardinality()
            12
            sage: C = cartesian_product_iterator([ZZ,QQ])
            sage: C.cardinality()
            +Infinity
            sage: C = cartesian_product_iterator([ZZ,[]])
            sage: C.cardinality()
            0
        """
        from sage.rings.integer import Integer
        from sage.rings.infinity import infinity
        ans = Integer(1)
        found_infinity = False
        for L in self.iter_list:
            try:
                n = L.cardinality()
            except AttributeError:
                n = Integer(len(L))
            if n == 0:
                return Integer(0)
            elif n is infinity:
                found_infinity = True
            elif not found_infinity:
                ans *= n
        if found_infinity:
            return infinity
        else:
            return ans

def _xmrange(sizes, typ=list):
    n = len(sizes)
    if n == 0:
        yield typ([])
        return
    for i in sizes:
        if i <= 0:
            return
    v = [0] * n    # make a list of n 0's.
    v[-1] = -1
    ptr_max = n - 1
    ptr = ptr_max
    while True:
        while True:
            if ptr != -1 and v[ptr] + 1 < sizes[ptr]:
                v[ptr] += 1
                ptr = ptr_max
                break
            elif ptr != -1:
                v[ptr] = 0
                ptr -= 1
            else:
                return
        yield typ(v)   # make a copy of v!


def mrange(sizes, typ=list):
    """
    Return the multirange list with given sizes and type.

    This is the list version of xmrange. Use xmrange for the iterator.

    More precisely, return the iterator over all objects of type typ of
    n-tuples of Python ints with entries between 0 and the integers in
    the sizes list. The iterator is empty if sizes is empty or contains
    any non-positive integer.

    INPUT:


    -  ``sizes`` - a list of nonnegative integers

    -  ``typ`` - (default: list) a type or class; more
       generally, something that can be called with a list as input.


    OUTPUT: a list

    EXAMPLES::

        sage: mrange([3,2])
        [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]]
        sage: mrange([3,2], tuple)
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
        sage: mrange([3,2], sum)
        [0, 1, 1, 2, 2, 3]

    Examples that illustrate empty multi-ranges::

        sage: mrange([5,3,-2])
        []
        sage: mrange([5,3,0])
        []

    This example isn't empty, and shouldn't be. See trac #6561.

    ::

        sage: mrange([])
        [[]]


    AUTHORS:

    - Jon Hanke

    - William Stein
    """
    return list(_xmrange(sizes, typ))


class xmrange:
    """
    Return the multirange iterate with given sizes and type.

    More precisely, return the iterator over all objects of type typ of
    n-tuples of Python ints with entries between 0 and the integers in
    the sizes list. The iterator is empty if sizes is empty or contains
    any non-positive integer.

    Use mrange for the non-iterator form.

    INPUT:


    -  ``sizes`` - a list of nonnegative integers

    -  ``typ`` - (default: list) a type or class; more
       generally, something that can be called with a list as input.


    OUTPUT: a generator

    EXAMPLES: We create multi-range iterators, print them and also
    iterate through a tuple version.

    ::

        sage: z = xmrange([3,2]);z
        xmrange([3, 2])
        sage: z = xmrange([3,2], tuple);z
        xmrange([3, 2], <type 'tuple'>)
        sage: for a in z:
        ...    print a
        (0, 0)
        (0, 1)
        (1, 0)
        (1, 1)
        (2, 0)
        (2, 1)

    We illustrate a few more iterations.

    ::

        sage: list(xmrange([3,2]))
        [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]]
        sage: list(xmrange([3,2], tuple))
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

    Here we compute the sum of each element of the multi-range
    iterator::

        sage: list(xmrange([3,2], sum))
        [0, 1, 1, 2, 2, 3]

    Next we compute the product::

        sage: list(xmrange([3,2], prod))
        [0, 0, 0, 1, 0, 2]

    Examples that illustrate empty multi-ranges.

    ::

        sage: list(xmrange([5,3,-2]))
        []
        sage: list(xmrange([5,3,0]))
        []

    This example isn't empty, and shouldn't be. See trac #6561.

    ::

        sage: list(xmrange([]))
        [[]]

    We use a multi-range iterator to iterate through the Cartesian
    product of sets.

    ::

        sage: X = ['red', 'apple', 389]
        sage: Y = ['orange', 'horse']
        sage: for i,j in xmrange([len(X), len(Y)]):
        ...    print (X[i], Y[j])
        ('red', 'orange')
        ('red', 'horse')
        ('apple', 'orange')
        ('apple', 'horse')
        (389, 'orange')
        (389, 'horse')

    AUTHORS:

    - Jon Hanke

    - William Stein
    """
    def __init__(self, sizes, typ=list):
        self.sizes = [int(x) for x in sizes]
        self.typ = typ

    def __repr__(self):
        if self.typ == list:
            return 'xmrange(%s)'%self.sizes
        else:
            return 'xmrange(%s, %s)'%(self.sizes, self.typ)

    def __len__(self):
        sizes = self.sizes
        n = len(sizes)
        if n == 0:
            return 0
        for i in sizes:
            if i <= 0:
                return 0
        return misc.prod(sizes, 1)

    def __iter__(self):
        return _xmrange(self.sizes, self.typ)

def cartesian_product_iterator(X):
    """
    Iterate over the Cartesian product.

    INPUT:


    -  ``X`` - list or tuple of lists


    OUTPUT: iterator over the cartesian product of the elements of X

    EXAMPLES::

        sage: list(cartesian_product_iterator([[1,2], ['a','b']]))
        [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
        sage: list(cartesian_product_iterator([]))
        [()]
    """
    return xmrange_iter(X, tuple)
