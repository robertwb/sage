r"""
Datatypes for words defined by iterators and callables
"""
#*****************************************************************************
#       Copyright (C) 2009 Franco Saliola <saliola@gmail.com>
#                          Vincent Delecroix <20100.delecroix@gmail.com>
#
#  Distributed under the terms of the GNU General Public License version 2
#  (GPLv2)
#
#  The full text of the GPLv2 is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.combinat.words.word_datatypes import WordDatatype
from sage.rings.all import Infinity
from math import ceil
import itertools

class WordDatatype_callable(WordDatatype):
    r"""
    Datatype for a word defined by a callable.
    """
    def __init__(self, parent, callable, length=None):
        r"""
        INPUT:

        - ``parent`` - a parent
        -  ``callable`` - a callable defined on ``range(stop=length)``
        -  ``length`` - (default: ``None``) nonnegative integer or ``None``

        EXAMPLES::

            sage: f = lambda n : 'x' if n % 2 == 0 else 'y'
            sage: w = Word(f, length=9, caching=False); w
            word: xyxyxyxyx
            sage: type(w)
            <class 'sage.combinat.words.word.FiniteWord_callable'>
            sage: w.length()
            9

        ::

            sage: w = Word(f, caching=False); w
            word: xyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxy...
            sage: type(w)
            <class 'sage.combinat.words.word.InfiniteWord_callable'>
            sage: w.length() is None
            False
            sage: w.length()
            +Infinity

        TESTS::

            sage: from sage.combinat.words.word_infinite_datatypes import WordDatatype_callable
            sage: WordDatatype_callable(Words(),lambda n:n%3)
            <class 'sage.combinat.words.word_infinite_datatypes.WordDatatype_callable'>
            sage: WordDatatype_callable(Words([0,1,2]),lambda n:n%3)
            <class 'sage.combinat.words.word_infinite_datatypes.WordDatatype_callable'>
        """
        self._len = Infinity if length is None else length
        self._func = callable
        self._parent = parent
        # for hashing
        self._hash = None

    def __iter__(self):
        r"""
        EXAMPLES::

            sage: w = Word(lambda x : x % 2)
            sage: it = iter(w)
            sage: [it.next() for _ in range(10)]
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

        TESTS::

            sage: from sage.combinat.words.word_infinite_datatypes import WordDatatype_callable
            sage: s = WordDatatype_callable(Words(), lambda n:n%3+10, length=10); s
            <class 'sage.combinat.words.word_infinite_datatypes.WordDatatype_callable'>
            sage: it = iter(s)
            sage: [it.next() for _ in range(10)]
            [10, 11, 12, 10, 11, 12, 10, 11, 12, 10]
        """
        if self._len is Infinity:
            domain = itertools.count()
        else:
            domain = xrange(self._len)
        return itertools.imap(self._func, domain)

    def __getitem__(self, key):
        r"""
        EXAMPLES::

            sage: f = lambda n : "abbabaabbaab"[n]
            sage: w = Word(f, length=12, caching=False); w
            word: abbabaabbaab
            sage: w.length()
            12

        Test getitems with indexes::

            sage: w[0]
            'a'
            sage: w[4]
            'b'
            sage: w[-1]
            'b'
            sage: w[-2]
            'a'
            sage: [w[i] for i in range(12)]
            ['a', 'b', 'b', 'a', 'b', 'a', 'a', 'b', 'b', 'a', 'a', 'b']

        Slicing::

            sage: w[:]
            word: abbabaabbaab

        Prefixes::

            sage: w[0:]
            word: abbabaabbaab
            sage: w[1:]
            word: bbabaabbaab

        Suffixes::

            sage: w[:0]
            word:
            sage: w[:5]
            word: abbab

        With positive steps::

            sage: w[::2]
            word: abbaba

        With a negative start position::

            sage: w[-2:]
            word: ab
            sage: w[-20:]
            word: abbabaabbaab

        With a negative stop position::

            sage: w[:-1]
            word: abbabaabbaa
            sage: w[:-10]
            word: ab

        With a negative step::

            sage: w[::-2]
            word: babaab
            sage: w[10:1:-2]
            word: ababb
            sage: w[10:0:-2]
            word: ababb
            sage: w[:1:-3]
            word: bbab

        TESTS:

        For infinite words::

            sage: f = lambda n : add(Integer(n).digits(2)) % 2
            sage: tm = Word(f, caching=False); tm
            word: 0110100110010110100101100110100110010110...
            sage: tm.length()
            +Infinity

        Test getitems with indexes::

            sage: tm[0]
            0
            sage: tm[4]
            1
            sage: [tm[i] for i in range(12)]
            [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
            sage: tm[-1]
            Traceback (most recent call last):
            ...
            IndexError: cannot use a negative index with an infinite word

        Slicing::

            sage: tm[:]
            word: 0110100110010110100101100110100110010110...

        Prefixes::

            sage: tm[:0]
            word:
            sage: tm[:5]
            word: 01101

        Suffixes::

            sage: tm[0:]
            word: 0110100110010110100101100110100110010110...
            sage: tm[1:]
            word: 1101001100101101001011001101001100101100...

        With positive steps::

            sage: tm[::2]
            word: 0110100110010110100101100110100110010110...

        With a negative step::

            sage: tm[20:1:-3]
            word: 0011101
            sage: tm[10:1:-2]
            word: 01011
            sage: tm[10:0:-2]
            word: 01011
            sage: tm[::-2]
            Traceback (most recent call last):
            ...
            ValueError: start value must be nonnegative for negative step values
            sage: tm[-17::-2]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative
        """
        if isinstance(key, slice):
            # Infinite words
            if self._len is Infinity:
                if not(key.start is None) and key.start < 0 or \
                        not(key.stop is None) and key.stop < 0:
                    raise ValueError, "for infinite words, start and stop values cannot be negative"
                step = 1 if key.step is None else key.step
                if step > 0:
                    start = 0 if key.start is None else key.start
                    length = None if key.stop is None else \
                                int(max(0,ceil((key.stop-start)/float(step))))
                else:
                    if key.start is None or key.start < 0:
                        raise ValueError, "start value must be nonnegative for negative step values"
                    start = key.start
                    stop = 0 if key.stop is None else key.stop
                    length = int(max(0,ceil((key.stop-start)/float(step))))
                fcn = lambda x: self._func(start + x*step)
                return self._parent(fcn, length=length)
            # Finite words
            else:
                ## For testing: expand as a list and slice it
                #return self._parent(map(self._func, range(self._len))[key])
                step = 1 if key.step is None else key.step
                if step > 0:
                    start, stop, step = slice(key.start, key.stop,
                            step).indices(self._len)
                    length = int((stop-start)/float(step))
                else:
                    start, stop, step = slice(key.start, key.stop,
                            step).indices(self._len)
                    length = int(max(0,ceil((stop-start)/float(step))))
                fcn = lambda x: self._func(start + x*step)
                return self._parent(fcn, length=length)
        else:
            if key < 0:
                if self._len is Infinity:
                    raise IndexError, "cannot use a negative index with an infinite word"
                else:
                    key = self._len + key
            return self._func(key)

    def __reduce__(self):
        r"""
        EXAMPLES::

            sage: w = Word(lambda n : n%3+10, caching=False)
            sage: w.__reduce__()
            (Words, ("csage.misc.fpickle...<lambda>...", +Infinity, 'pickled_function', False))

        ::

            sage: w = Word(lambda n : n%3+10, caching=False, length=8)
            sage: w.__reduce__()
            (Words, ("csage.misc.fpickle...<lambda>...", 8, 'pickled_function', False))
        """
        from sage.misc.fpickle import pickle_function
        try:
            s = pickle_function(self._func)
        except Exception:
            from sage.combinat.words.word import FiniteWord_class
            if isinstance(self, FiniteWord_class):
                return self._parent, (list(self),)
            else:
                return self._parent, (self._func, self._len, 'callable', False)
        else:
            return self._parent, (s, self._len, 'pickled_function', False)

class WordDatatype_callable_with_caching(WordDatatype_callable):
    r"""
    Datatype for a word defined by a callable.
    """
    def __init__(self, parent, callable, length=None):
        r"""
        INPUT:

        - ``parent`` - a parent
        -  ``callable`` - a callable defined on ``range(stop=length)``
        -  ``length`` - (default: ``None``) nonnegative integer or ``None``

        EXAMPLES::

            sage: f = lambda n : 'x' if n % 2 == 0 else 'y'
            sage: w = Word(f, length=9, caching=True); w
            word: xyxyxyxyx
            sage: type(w)
            <class 'sage.combinat.words.word.FiniteWord_callable_with_caching'>
            sage: w.length()
            9

        ::

            sage: w = Word(f, caching=True); w
            word: xyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxyxy...
            sage: type(w)
            <class 'sage.combinat.words.word.InfiniteWord_callable_with_caching'>
            sage: w.length() is None
            False
            sage: w.length()
            +Infinity
        """
        super(WordDatatype_callable_with_caching,self).__init__(parent,callable,length)
        # for caching
        self._letter_cache = {}

    def __iter__(self):
        r"""
        Iterate through the letters of the word, in order.

        EXAMPLES::

            sage: w = Word(lambda x : x % 2)
            sage: it = iter(w)
            sage: [it.next() for _ in range(10)]
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        """
        if self._len is Infinity:
            domain = itertools.count()
        else:
            domain = xrange(self._len)
        letter_cache = self._letter_cache
        func = self._func
        for x in domain:
            if not letter_cache.has_key(x):
                letter_cache[x] = func(x)
            yield letter_cache[x]

    def __getitem__(self, key):
        r"""
        EXAMPLES::

            sage: f = lambda n : "abbabaabbaab"[n]
            sage: w = Word(f, length=12); w
            word: abbabaabbaab
            sage: w.length()
            12

        Test getitems with indexes.
            sage: w[0]
            'a'
            sage: w[4]
            'b'
            sage: w[-1]
            'b'
            sage: w[-2]
            'a'
            sage: [w[i] for i in range(12)]
            ['a', 'b', 'b', 'a', 'b', 'a', 'a', 'b', 'b', 'a', 'a', 'b']

        Slicing.
            sage: w[:]
            word: abbabaabbaab

        Prefixes.
            sage: w[0:]
            word: abbabaabbaab

            sage: w[1:]
            word: bbabaabbaab

        Suffixes.
            sage: w[:0]
            word:

            sage: w[:5]
            word: abbab

        With positive steps.
            sage: w[::2]
            word: abbaba

        With a negative start position.
            sage: w[-2:]
            word: ab
            sage: w[-20:]
            word: abbabaabbaab

        With a negative stop position.
            sage: w[:-1]
            word: abbabaabbaa
            sage: w[:-10]
            word: ab

        With a negative step.
            sage: w[::-2]
            word: babaab

            sage: w[10:1:-2]
            word: ababb
            sage: w[10:0:-2]
            word: ababb
            sage: w[:1:-3]
            word: bbab

        TESTS::

        For infinite words
            sage: f = lambda n : add(Integer(n).digits(2)) % 2
            sage: tm = Word(f); tm
            word: 0110100110010110100101100110100110010110...

            sage: tm.length()
            +Infinity

        Test getitems with indexes.
            sage: tm[0]
            0
            sage: tm[4]
            1
            sage: [tm[i] for i in range(12)]
            [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
            sage: tm[-1]
            Traceback (most recent call last):
            ...
            IndexError: cannot use a negative index with an infinite word

        Slicing.
            sage: tm[:]
            word: 0110100110010110100101100110100110010110...

        Prefixes.
            sage: tm[:0]
            word:

            sage: tm[:5]
            word: 01101

        Suffixes.
            sage: tm[0:]
            word: 0110100110010110100101100110100110010110...

            sage: tm[1:]
            word: 1101001100101101001011001101001100101100...

        With positive steps.
            sage: tm[::2]
            word: 0110100110010110100101100110100110010110...

        With a negative step.
            sage: tm[20:1:-3]
            word: 0011101
            sage: tm[10:1:-2]
            word: 01011
            sage: tm[10:0:-2]
            word: 01011
            sage: tm[::-2]
            Traceback (most recent call last):
            ...
            ValueError: start value must be nonnegative for negative step values
            sage: tm[-17::-2]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative
        """
        if isinstance(key, slice):
            return super(WordDatatype_callable_with_caching, self).__getitem__(key)
        else:
            if not self._letter_cache.has_key(key):
                self._letter_cache[key] = \
                    super(WordDatatype_callable_with_caching, self).__getitem__(key)
            return self._letter_cache[key]

    def __reduce__(self):
        r"""
        EXAMPLES::

            sage: w = Word(lambda n : n%3+10, caching=True)
            sage: w.__reduce__()
            (Words, ("csage.misc.fpickle...<lambda>...", +Infinity, 'pickled_function', True))

        ::

            sage: w = Word(lambda n : n%3+10, caching=True, length=8)
            sage: w.__reduce__()
            (Words, ("csage.misc.fpickle...<lambda>...", 8, 'pickled_function', True))

        Because ``pickle_function`` fails on CallableFromListOfWords,
        then concatenation of words are expanded as a list::

            sage: w = Word(range(5)) + Word('abcde')
            sage: w.__reduce__()
            (Words, ([0, 1, 2, 3, 4, 'a', 'b', 'c', 'd', 'e'],))

        """
        from sage.misc.fpickle import pickle_function
        try:
            s = pickle_function(self._func)
        except Exception:
            from sage.combinat.words.word import FiniteWord_class
            if isinstance(self, FiniteWord_class):
                return self._parent, (list(self),)
            else:
                return self._parent, (self._func, self._len, 'callable', True)
        else:
            return self._parent, (s, self._len, 'pickled_function', True)

    def flush(self):
        r"""
        Empty the associated cache of letters.

        EXAMPLES::

        The first 40 (by default) values are always cached.
            sage: w = words.ThueMorseWord()
            sage: w._letter_cache
            {0: 0, 1: 1, 2: 1, 3: 0, 4: 1, 5: 0, 6: 0, 7: 1, 8: 1, 9: 0, 10: 0, 11: 1, 12: 0, 13: 1, 14: 1, 15: 0, 16: 1, 17: 0, 18: 0, 19: 1, 20: 0, 21: 1, 22: 1, 23: 0, 24: 0, 25: 1, 26: 1, 27: 0, 28: 1, 29: 0, 30: 0, 31: 1, 32: 1, 33: 0, 34: 0, 35: 1, 36: 0, 37: 1, 38: 1, 39: 0}
            sage: w[100]
            1
            sage: w._letter_cache
            {0: 0, 1: 1, 2: 1, 3: 0, 4: 1, 5: 0, 6: 0, 7: 1, 8: 1, 9: 0, 10: 0, 11: 1, 12: 0, 13: 1, 14: 1, 15: 0, 16: 1, 17: 0, 18: 0, 19: 1, 20: 0, 21: 1, 22: 1, 23: 0, 24: 0, 25: 1, 26: 1, 27: 0, 28: 1, 29: 0, 30: 0, 31: 1, 32: 1, 33: 0, 34: 0, 35: 1, 36: 0, 37: 1, 38: 1, 39: 0, 100: 1}
            sage: w.flush()
            sage: w._letter_cache
            {}
        """
        self._letter_cache = {}

class WordDatatype_iter(WordDatatype):
    # NOTE: The constructor callable should do all the slicing (see islice)
    def __init__(self, parent, iter, length=None):
        r"""
        INPUT:

        - ``parent`` - a parent
        -  ``iter`` - an iterator
        -  ``length`` - (default: ``None``) the length of the word

        EXAMPLES::

            sage: w = Word(iter("abbabaab"), length="unknown", caching=False); w
            word: abbabaab
            sage: isinstance(w, sage.combinat.words.word_infinite_datatypes.WordDatatype_iter)
            True
            sage: w.length() is None
            False
            sage: w.length()
            8
            sage: s = "abbabaabbaababbabaababbaabbabaabbaababbaabbabaabab"
            sage: w = Word(iter(s), length="unknown", caching=False); w
            word: abbabaabbaababbabaababbaabbabaabbaababba...
            sage: w.length() is None
            True

        ::

            sage: w = Word(iter("abbabaab"), length="finite", caching=False); w
            word: abbabaab
            sage: isinstance(w, sage.combinat.words.word_infinite_datatypes.WordDatatype_iter)
            True
            sage: w.length()
            8
            sage: w = Word(iter("abbabaab"), length=8, caching=False); w
            word: abbabaab
            sage: isinstance(w, sage.combinat.words.word_infinite_datatypes.WordDatatype_iter)
            True
            sage: w.length()
            8
        """
        if length is None or length is Infinity:
            self._len = Infinity
            self._data = iter
        elif length is 'unknown' or length is 'finite':
            self._len = None
            self._data = iter
        else:
            self._len = length
            self._data = itertools.islice(iter, length)

        self._parent = parent
        self._hash = None

    def __iter__(self):
        r"""
        EXAMPLES::

            sage: it = iter(range(9))
            sage: w = Word(it, length='unknown', caching=False)
            sage: [a for a in iter(w)]
            [0, 1, 2, 3, 4, 5, 6, 7, 8]
        """
        self._data, it = itertools.tee(self._data)
        counter = 0
        for a in it:
            counter += 1
            yield a
        # If we reach this point, then we know the length of the word,
        # and that the word is finite.
        self._len = counter
        self.__class__ = self.parent()._element_classes['FiniteWord_iter']

    def __getitem__(self, key):
        r"""
        There is some support for negative stops and steps, but if the
        iterator does not terminate, then neither will this method.

        TESTS FOR FINITE WORDS.

        A word from an iterator without a length specified::

            sage: w = Word(iter("abbabaabbaab"), length="finite", caching=False); w
            word: abbabaabbaab

        Test getitems with indexes::

            sage: w[0]
            'a'
            sage: w[4]
            'b'
            sage: w[-1]
            'b'
            sage: w[-2]
            'a'
            sage: [w[i] for i in range(12)]
            ['a', 'b', 'b', 'a', 'b', 'a', 'a', 'b', 'b', 'a', 'a', 'b']

        The previous command exhausts the iterator, so we now know the
        length of the word::

            sage: w.length()
            12

        Slicing::

            sage: w[:]
            word: abbabaabbaab

        Suffixes::

            sage: w[0:]
            word: abbabaabbaab
            sage: w[1:]
            word: bbabaabbaab

        Prefixes::

            sage: w[:0]
            word:
            sage: w[:5]
            word: abbab

        With positive steps::

            sage: w[::2]
            word: abbaba

        With a negative start position, the word must be expanded! ::

            sage: w[-2:]
            word: ab
            sage: w[-20:]
            word: abbabaabbaab

        With a negative stop position, the word must be expanded! ::

            sage: w[:-1]
            word: abbabaabbaa
            sage: w[:-10]
            word: ab

        With a negative step, the word may or may not be expanded;
        it depends on the slice::

            sage: w[::-2]
            word: babaab
            sage: w[10:1:-2]
            word: ababb
            sage: list(w[10:1:-2])
            ['a', 'b', 'a', 'b', 'b']
            sage: list(w[20:1:-2])
            ['b', 'a', 'b', 'a', 'a']
            sage: list(w[10:1:-3])
            ['a', 'b', 'b']
            sage: w[::0]
            Traceback (most recent call last):
            ...
            ValueError: Step for islice() must be a positive integer or None.

        TESTS FOR INFINITE WORDS::

            sage: from itertools import count
            sage: c = Word(count()); c
            word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...

        Test getitems with indexes::

            sage: c[0]
            0
            sage: c[4]
            4
            sage: [c[i] for i in range(12)]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            sage: c[-1]
            Traceback (most recent call last):
            ...
            IndexError: cannot use negative indices with infinite words
            sage: c[-2]
            Traceback (most recent call last):
            ...
            IndexError: cannot use negative indices with infinite words

        Slicing::

            sage: c[:]
            word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...

        Prefixes::

            sage: c[:0]
            word:
            sage: c[:5]
            word: 01234

        Suffixes::

            sage: c[0:]
            word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...
            sage: c[1:]
            word: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,...

        With positive steps::

            sage: c[::2]
            word: 0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,...

        Cannot have negative start or stop positions::

            sage: c[-2:]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative
            sage: c[-20:]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative
            sage: c[:-1]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative
            sage: c[:-10]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative

        With a negative step, start must be nonnegative::

            sage: c[10:1:-2]
            word: 10,8,6,4,2
            sage: c[10:1:-3]
            word: 10,7,4
            sage: c[20:1:-3]
            word: 20,17,14,11,8,5,2
            sage: c[::-2]
            Traceback (most recent call last):
            ...
            ValueError: start value must be nonnegative for negative step values
            sage: c[::0]
            Traceback (most recent call last):
            ...
            ValueError: Step for islice() must be a positive integer or None.
        """
        if isinstance(key, slice):
            if self._len is Infinity:
                if not(key.start is None) and key.start < 0 or \
                        not(key.stop is None) and key.stop < 0:
                    raise ValueError, "for infinite words, start and stop values cannot be negative"
                step = 1 if key.step is None else key.step
                if step >= 0:
                    start = 0 if key.start is None else key.start
                    if key.stop is None:
                        length = Infinity
                    else: # key.stop > 0
                        length = int(max(0,ceil((key.stop-start)/float(step))))
                    data = itertools.islice(self, start, key.stop, step)
                    return self._parent(data, length=length)
                else:
                    if key.start is None or key.start < 0:
                        raise ValueError, "start value must be nonnegative for negative step values"
                    start = key.start
                    stop = 0 if key.stop is None else key.stop
                    length = int(max(0,ceil((key.stop-start)/float(step))))
                    data = list(itertools.islice(self, start+1))[key]
                    return self._parent(data, length=length)
            else:
                start = 0 if key.start is None else key.start
                stop = self._len if key.stop is None else key.stop
                step = 1 if key.step is None else key.step
                # If either key.start or key.stop is negative,
                # then we need to expand the word.
                if start < 0 or (not(stop is None) and stop < 0):
                    data = list(self)[key]
                    length = None
                # If key.step is negative, then we need to expand a prefix.
                elif step < 0:
                    if key.start is None:
                        data = list(self)[key]
                    else:
                        data = list(itertools.islice(self, start+1))[start:stop:step]
                    length = None
                else: # start >= 0, step >= 1, stop >= 0 or None
                    data = itertools.islice(self, key.start, key.stop, key.step)
                    length = "unknown" if stop is None else int(max(0,((stop-start)/float(step))))
                return self._parent(data, length=length)
        else:
            if key < 0:
                if self._len is Infinity:
                    raise IndexError, "cannot use negative indices with infinite words"
                elif self._len is None:
                    raise IndexError, "cannot use negative indices with words of unknown length"
                else:
                    key = self.length() + key
            it = iter(self)
            a = it.next()
            counter = 0
            while counter < key:
                try:
                    a = it.next()
                    counter += 1
                except StopIteration:
                    raise IndexError, "word index out of range"
            return a

    def __reduce__(self):
        r"""
        If finite, it expands the iterator in a list.

        EXAMPLES::

            sage: w = Word(iter('ab'), caching=False, length='unknown')
            sage: w.__reduce__()
            (Words, (['a', 'b'],))

        ::

            sage: w = Word(iter('ab'*10000), caching=False, length='unknown')
            sage: w.__reduce__()
            (Words, (<generator object __iter__ at ...>, None, 'iter', False))
        """
        from sage.combinat.words.word import FiniteWord_class
        if isinstance(self, FiniteWord_class):
            return self._parent, (list(self),)
        else:
            return self._parent, (iter(self), self._len, 'iter', False)

class WordDatatype_iter_with_caching(WordDatatype_iter):
    def __init__(self, parent, iter, length=None):
        r"""
        INPUT:

        - ``parent`` - a parent
        -  ``iter`` - an iterator
        -  ``length`` - (default: ``None``) the length of the word

        EXAMPLES::

            sage: import itertools
            sage: Word(itertools.cycle("abbabaab"))
            word: abbabaababbabaababbabaababbabaababbabaab...
            sage: w = Word(iter("abbabaab"), length="finite"); w
            word: abbabaab
            sage: w.length()
            8
            sage: w = Word(iter("abbabaab"), length="unknown"); w
            word: abbabaab
            sage: w.length()
            8
            sage: list(w)
            ['a', 'b', 'b', 'a', 'b', 'a', 'a', 'b']
            sage: w.length()
            8
            sage: w = Word(iter("abbabaab"), length=8)
            sage: w._len
            8
        """
        super(WordDatatype_iter_with_caching,self).__init__(parent,iter,length)
        # we use self._data for returning an iterator through __iter__;
        # we use self._gen for caching
        self._data, self._gen = itertools.tee(self._data)
        self._list = []
        self._last_index = -1

    def __iter__(self):
        r"""
        Iterate through the letters of the word, in order.

        EXAMPLES::

            sage: w = Word(iter([0,1,0,0,1,0,1,0,0,1,0,1,0]))
            sage: it = iter(w)
            sage: [it.next() for _ in range(10)]
            [0, 1, 0, 0, 1, 0, 1, 0, 0, 1]
        """
        # first iterator through the cached values
        # then continue through the self._gen
        for a in self._list:
            yield a
        for a in self._gen:
            self._list.append(a)
            self._last_index += 1
            yield a
        # If we reach this point, then we know the length of the word,
        # and that the word is finite.
        self._len = len(self._list)
        self.__class__ = self.parent()._element_classes['FiniteWord_iter_with_caching']

    def __getitem__(self, key):
        r"""
        There is some support for negative stops and steps, but if the
        iterator does not terminate, then neither will this method.

        TESTS FOR FINITE WORDS.

        A word from an iterator without a length specified::

            sage: w = Word(iter("abbabaabbaab"), length="unknown"); w
            word: abbabaabbaab

        Test getitems with indexes::

            sage: w[0]
            'a'
            sage: w[4]
            'b'
            sage: w[-1]
            'b'
            sage: w[-2]
            'a'
            sage: [w[i] for i in range(12)]
            ['a', 'b', 'b', 'a', 'b', 'a', 'a', 'b', 'b', 'a', 'a', 'b']

        Copying via slicing::

            sage: w = Word(iter("abbabaabbaab")); w
            word: abbabaabbaab
            sage: w[:]
            word: abbabaabbaab

        Suffixes::

            sage: w = Word(iter("abbabaabbaab"), length="finite")
            sage: w[0:]
            word: abbabaabbaab
            sage: w = Word(iter("abbabaabbaab"), length="finite")
            sage: w[1:]
            word: bbabaabbaab

        Prefixes::

            sage: w = Word(iter("abbabaabbaab"), length="finite")
            sage: w[:0]
            word:
            sage: w = Word(iter("abbabaabbaab"), length="finite")
            sage: w[:5]
            word: abbab

        With positive steps::

            sage: w = Word(iter("abbabaabbaab"), length="unknown")
            sage: w[::2]
            word: abbaba

        With a negative start position, the word must be expanded! ::

            sage: w = Word(iter("abbabaabbaab"), length="finite")
            sage: w[-2:]
            word: ab
            sage: w = Word(iter("abbabaabbaab"), length="finite")
            sage: w[-20:]
            word: abbabaabbaab

        With a negative stop position, the word must be expanded! ::

            sage: w = Word(iter("abbabaabbaab"), length="finite")
            sage: w[:-1]
            word: abbabaabbaa
            sage: w = Word(iter("abbabaabbaab"), length="unknown")
            sage: w[:-10]
            word: ab

        With a negative step, the word may or may not be expanded;
        it depends on the slice::

            sage: w = Word(iter("abbabaabbaab"), length="finite")
            sage: w[::-2]
            word: babaab
            sage: w = Word(iter("abbabaabbaab"))
            sage: w[10:1:-2]
            word: ababb
            sage: list(w[10:1:-2])
            ['a', 'b', 'a', 'b', 'b']
            sage: list(w[20:1:-2])
            ['b', 'a', 'b', 'a', 'a']
            sage: list(w[10:1:-3])
            ['a', 'b', 'b']
            sage: w = Word(iter("abbabaabbaab"))
            sage: w[::0]
            Traceback (most recent call last):
            ...
            ValueError: Step for islice() must be a positive integer or None.

        TESTS FOR INFINITE WORDS::

            sage: from itertools import count
            sage: c = Word(count()); c
            word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...

        Test getitems with indexes::

            sage: c[0]
            0
            sage: c[4]
            4
            sage: [c[i] for i in range(12)]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            sage: c[-1]
            Traceback (most recent call last):
            ...
            IndexError: cannot use negative indices with infinite words
            sage: c[-2]
            Traceback (most recent call last):
            ...
            IndexError: cannot use negative indices with infinite words

        Slicing::

            sage: c[:]
            word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...

        Prefixes::

            sage: c[:0]
            word:
            sage: c[:5]
            word: 01234

        Suffixes::

            sage: c[0:]
            word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...
            sage: c[1:]
            word: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...

        With positive steps::

            sage: c[::2]
            word: 0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,...

        Cannot have negative start or stop positions::

            sage: c[-2:]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative
            sage: c[-20:]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative
            sage: c[:-1]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative
            sage: c[:-10]
            Traceback (most recent call last):
            ...
            ValueError: for infinite words, start and stop values cannot be negative

        With a negative step, start must be nonnegative::

            sage: c[10:1:-2]
            word: 10,8,6,4,2
            sage: c[10:1:-3]
            word: 10,7,4
            sage: c[20:1:-3]
            word: 20,17,14,11,8,5,2
            sage: c[::-2]
            Traceback (most recent call last):
            ...
            ValueError: start value must be nonnegative for negative step values
            sage: c[::0]
            Traceback (most recent call last):
            ...
            ValueError: Step for islice() must be a positive integer or None.
        """
        if isinstance(key, slice):
            return super(WordDatatype_iter_with_caching,self).__getitem__(key)
        else:
            if key < 0:
                return super(WordDatatype_iter_with_caching,self).__getitem__(key)
            else:
                while self._last_index < key:
                    try:
                        self._list.append(self._gen.next())
                        self._last_index += 1
                    except StopIteration:
                        raise IndexError, "word index out of range"
                return self._list[key]

    def __reduce__(self):
        r"""
        If finite, it expands the iterator in a list.

        EXAMPLES::

            sage: w = Word(iter('ab'), caching=True, length='unknown')
            sage: w.__reduce__()
            (Words, (['a', 'b'],))

        ::

            sage: w = Word(iter('ab'*10000), caching=True, length='unknown')
            sage: w.__reduce__()
            (Words, (<generator object __iter__ at ...>, None, 'iter', True))

        """
        from sage.combinat.words.word import Word, FiniteWord_class
        if isinstance(self, FiniteWord_class):
            return self._parent, (list(self),)
        else:
            return self._parent, (iter(self), self._len, 'iter', True)

    def flush(self):
        r"""
        Delete the cached values.

        EXAMPLES::

            sage: from itertools import count
            sage: w = Word(count())
            sage: w._last_index, len(w._list)
            (39, 40)
            sage: w[43]
            43
            sage: w._last_index, len(w._list)
            (43, 44)
            sage: w.flush()
            sage: w._last_index, w._list
            (-1, [])
        """
        self._gen = iter(self)
        self._list = []
        self._last_index = -1
