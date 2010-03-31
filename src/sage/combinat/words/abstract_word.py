r"""
Abstract word (finite or infinite)

This module gathers functions that works for both finite and infinite
words.

AUTHORS:

- Sebastien Labbe
- Franco Saliola

EXAMPLES::

    sage: a = 0.618
    sage: g = words.CodingOfRotationWord(alpha=a, beta=1-a, x=a)
    sage: f = words.FibonacciWord()
    sage: p = f.longest_common_prefix(g, length='finite')
    sage: p
    word: 0100101001001010010100100101001001010010...
    sage: p.length()
    231
"""
#*****************************************************************************
#       Copyright (C) 2008-2010 Sebastien Labbe <slabqc@gmail.com>,
#                     2008-2010 Franco Saliola <saliola@gmail.com>
#
#  Distributed under the terms of the GNU General Public License version 2 (GPLv2)
#
#  The full text of the GPLv2 is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.structure.sage_object import SageObject
from sage.misc.lazy_attribute import lazy_attribute
from sage.combinat.words.word_options import word_options
from itertools import islice, izip, groupby
from sage.rings.all import Integers, ZZ, Infinity

class Word_class(SageObject):
    def parent(self):
        r"""
        Returns the parent of self.

        TESTS::

            sage: Word(iter([1,2,3]), length="unknown").parent()
            Words
            sage: Word(range(12)).parent()
            Words
            sage: Word(range(4), alphabet=range(6)).parent()
            Words over Ordered Alphabet [0, 1, 2, 3, 4, 5]
            sage: Word(iter('abac'), alphabet='abc').parent()
            Words over Ordered Alphabet ['a', 'b', 'c']
        """
        return self._parent

    def _repr_(self):
        r"""
        Returns a string representation of self.

        TESTS::

            sage: Word(iter([1,2,3]), length="unknown")._repr_()
            'word: 123'
            sage: Word(xrange(100), length="unknown")._repr_()
            'word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...'
            sage: Word(lambda x:x%3)._repr_()
            'word: 0120120120120120120120120120120120120120...'
        """
        global word_options
        if word_options['old_repr']:
            return "Word over %s" % (str(self.parent().alphabet())[17:])
        return word_options['identifier'] + self.string_rep()

    def string_rep(self):
        r"""
        Returns the raw sequence of letters as a string.

        EXAMPLES::

            sage: Word('abbabaab').string_rep()
            'abbabaab'
            sage: Word([0, 1, 0, 0, 1]).string_rep()
            '01001'
            sage: Word([0,1,10,101]).string_rep()
            '0,1,10,101'
            sage: WordOptions(letter_separator='-')
            sage: Word([0,1,10,101]).string_rep()
            '0-1-10-101'
            sage: WordOptions(letter_separator=',')
        """
        global word_options
        l = word_options['truncate_length']
        letters = list(islice(self, l+1))
        if len(letters) == l+1:
            letters.pop()
            suffix = "..."
        else:
            suffix = ""
        if word_options['display'] == 'string':
            ls = word_options['letter_separator']
            letters = map(str, letters)
            if all(len(a)==1 for a in letters):
                return ''.join(letters) + suffix
            elif suffix == "...":
                return ls.join(letters) + ls + suffix
            else:
                return ls.join(letters)
        elif word_options['display'] == 'list':
            if suffix == "...":
                return "[%s, %s]" % (str(list(letters))[1:-1], suffix)
            else:
                return str(list(letters))

    def __iter__(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.words.word import Word_class
            sage: w = Word_class()
            sage: w.__iter__()
            Traceback (most recent call last):
            ...
            NotImplementedError: you need to define an iterator in __iter__
        """
        raise NotImplementedError, "you need to define an iterator in __iter__"

    def length(self):
        r"""
        Returns the length of self.

        TESTS::

            sage: from sage.combinat.words.word import Word_class
            sage: w = Word(iter('abba'*100), length="unknown")
            sage: w.length() is None
            True
            sage: w = Word(iter('abba'), length="finite")
            sage: w.length()
            4
            sage: w = Word(iter([0,1,1,0,1,0,0,1]*100), length="unknown")
            sage: w.length() is None
            True
            sage: w = Word(iter([0,1,1,0,1,0,0,1]), length="finite")
            sage: w.length()
            8
        """
        return self._len

    def __len__(self):
        r"""
        Return the length of self (as a python integer).

        ..NOTE::

            For infinite words or words of unknown length, use length method
            instead.

        OUTPUT:

            positive integer

        EXAMPLES::

            sage: len(Word(lambda n:n, length=1000))
            1000
            sage: len(Word(iter('a'*200), length='finite'))
            200

        We make sure #8574 is fixed::

            sage: s = WordMorphism('0->000,1->%s'%('1'*100))
            sage: len(s('1'))
            100

        For infinite word::

            sage: len(Word(lambda n:n))
            Traceback (most recent call last):
            ...
            TypeError: Python len method can not return a non integer value (=+Infinity): use length method instead.
            sage: len(Word(iter('a'*200)))
            Traceback (most recent call last):
            ...
            TypeError: Python len method can not return a non integer value (=+Infinity): use length method instead.

        For word of unknown length::

            sage: len(Word(iter('a'*200), length='unknown'))
            Traceback (most recent call last):
            ...
            TypeError: Python len method can not return a non integer value (=None): use length method instead.
        """
        L = self.length()
        if L is None or L is Infinity:
            msg = "Python len method can not return a non integer value (=%s): "%L
            msg += "use length method instead."
            raise TypeError, msg
        return int(L)

    def __cmp__(self, other):
        r"""
        Compares two words lexicographically according to the ordering
        defined by the parent of self. This corresponds to Python's built-in
        ordering when no parent nor alphabet was used to defined the word.

        Provides for all normal comparison operators.

        .. NOTE::

            This function will not terminate if self and other are equal
            infinite words!

        EXAMPLES::

            sage: W = Word
            sage: from itertools import count
            sage: W(range(1,10)).__cmp__(W(range(10))) > 0
            True
            sage: W(range(10)).__cmp__(W(range(1,10))) < 0
            True
            sage: W(range(10)).__cmp__(W(range(10))) == 0
            True
            sage: W(range(10)).__cmp__(W(count())) < 0
            True
            sage: W(count()).__cmp__(W(range(10))) > 0
            True

        ::

            sage: W = Words(['a', 'b', 'c'])
            sage: W('a').__cmp__(W([]))
            1
            sage: W([]).__cmp__(W('a'))
            -1
        """
        if not isinstance(other, Word_class):
            return NotImplemented
        self_it, other_it = iter(self), iter(other)
        cmp_fcn = self._parent.cmp_letters
        while True:
            try:
                cs = self_it.next()
            except StopIteration:
                try:
                    co = other_it.next()
                except StopIteration:
                    # If both self_it and other_it are exhausted then
                    # self == other. Return 0.
                    return 0
                else:
                    # If self_it is exhausted, but not other_it, then
                    # self is a proper prefix of other: return -1
                    return -1
            else:
                try:
                    co = other_it.next()
                except StopIteration:
                    # If self_it is not exhausted but other_it is, then
                    # other is a proper prefix of self: return 1.
                    return 1
                else:
                    r = cmp_fcn(cs, co)
                    if r != 0:
                        return r

    def __eq__(self, other):
        r"""
        Returns True if self is equal to other and False otherwise.

        INPUT:

        - ``other`` - a word

        OUTPUT:

            boolean

        .. NOTE:

            This function will not terminate if self and other are equal
            infinite words!

        EXAMPLES::

            sage: Word('abc') == Word(['a','b','c'])
            True
            sage: Words([0,1])([0,1,0,1]) == Words([0,1])([0,1,0,1])
            True
            sage: Words([0,1])([0,1,0,1]) == Words([0,1])([0,1,0,0])
            False

        It works even when parents are not the same::

            sage: Words([0,1,2])([0,1,0,1]) ==  Words([0,1])([0,1,0,1])
            True
            sage: Words('abc')('abab') == Words([0,9])([0,0,9])
            False
            sage: Word('ababa') == Words('abcd')('ababa')
            True

        Or when one word is finite while the other is infinite::

            sage: Word(range(20)) == Word(lambda n:n)
            False
            sage: Word(lambda n:n) == Word(range(20))
            False

        Beware the following does not halt!::

            sage: from itertools import count
            sage: Word(lambda n:n) == Word(count()) #not tested

        TESTS::

            sage: Word(count())[:20] == Word(range(20))
            True
            sage: Word(range(20)) == Word(count())[:20]
            True
            sage: Word(range(20)) == Word(lambda n:n)[:20]
            True
            sage: Word(range(20)) == Word(lambda n:n,length=20)
            True
        """
        if not isinstance(other, Word_class):
            return NotImplemented
        self_it, other_it = iter(self), iter(other)
        while True:
            try:
                cs = self_it.next()
            except StopIteration:
                try:
                    co = other_it.next()
                except StopIteration:
                    # If both self_it and other_it are exhausted then
                    # self == other. Return 0.
                    return True
                else:
                    # If self_it is exhausted, but not other_it, then
                    # self is a proper prefix of other: return -1
                    return False
            else:
                try:
                    co = other_it.next()
                except StopIteration:
                    # If self_it is not exhausted but other_it is, then
                    # other is a proper prefix of self: return 1.
                    return False
                else:
                    if cs != co:
                        return False

    def __ne__(self, other):
        r"""
        Returns True if self is not equal to other and False otherwise.

        INPUT:

        - ``other`` - a word

        OUTPUT:

            boolean

        .. NOTE:

            This function will not terminate if self and other are equal
            infinite words!

        EXAMPLES::

            sage: w = Word(range(10))
            sage: z = Word(range(10))
            sage: w != z
            False
            sage: u = Word(range(12))
            sage: u != w
            True
        """
        #print '__ne__', self, other, type(self), type(other)
        return not self.__eq__(other)

    def _longest_common_prefix_iterator(self, other):
        r"""
        Return an iterator of the longest common prefix of self and other.

        INPUT:

        -  ``other`` - word

        OUTPUT:

            iterator

        EXAMPLES::

            sage: f = words.FibonacciWord()
            sage: it = f._longest_common_prefix_iterator(f)
            sage: w = Word(it, length="unknown"); w
            word: 0100101001001010010100100101001001010010...
            sage: w[:6]
            word: 010010
            sage: it = w._longest_common_prefix_iterator(w[:10])
            sage: w = Word(it, length="finite"); w
            word: 0100101001
        """
        for (b,c) in izip(self, other):
            if b == c:
                yield b
            else:
                raise StopIteration
        else:
            raise StopIteration

    def longest_common_prefix(self, other, length='unknown'):
        r"""
        Returns the longest common prefix of self and other.

        INPUT:

        -  ``other`` - word

        -  ``length`` - str or +Infinity (optional, default: ``'unknown'``)
           the length type of the resulting word if known. It may be one of
           the following:

           - ``'unknown'``
           - ``'finite'``
           - ``'infinite'`` or ``Infinity``

        OUTPUT:

        word

        EXAMPLES::

            sage: f = lambda n : add(Integer(n).digits(2)) % 2
            sage: t = Word(f)
            sage: u = t[:10]
            sage: t.longest_common_prefix(u)
            word: 0110100110

        The longest common prefix of two equal infinite words::

            sage: t1 = Word(f)
            sage: t2 = Word(f)
            sage: t1.longest_common_prefix(t2)
            word: 0110100110010110100101100110100110010110...

        Useful to study the approximation of an infinite word::

            sage: a = 0.618
            sage: g = words.CodingOfRotationWord(alpha=a, beta=1-a, x=a)
            sage: f = words.FibonacciWord()
            sage: p = f.longest_common_prefix(g, length='finite')
            sage: p.length()
            231

        TESTS::

            sage: w = Word('12345')
            sage: y = Word('1236777')
            sage: w.longest_common_prefix(y)
            word: 123
            sage: w.longest_common_prefix(w)
            word: 12345
            sage: y.longest_common_prefix(w)
            word: 123
            sage: y.longest_common_prefix(y)
            word: 1236777
            sage: Word().longest_common_prefix(w)
            word:
            sage: w.longest_common_prefix(Word())
            word:
            sage: w.longest_common_prefix(w[:3])
            word: 123
            sage: Word("11").longest_common_prefix(Word("1"))
            word: 1
            sage: Word("1").longest_common_prefix(Word("11"))
            word: 1

        With infinite words::

            sage: t = words.ThueMorseWord('ab')
            sage: u = t[:10]
            sage: u.longest_common_prefix(t)
            word: abbabaabba
            sage: u.longest_common_prefix(u)
            word: abbabaabba
        """
        from sage.combinat.words.word import FiniteWord_class
        if (isinstance(self, FiniteWord_class) or
            isinstance(other, FiniteWord_class)):
            length = "finite"
        it = self._longest_common_prefix_iterator(other)
        return self._parent(it, length=length)

    def _longest_periodic_prefix_iterator(self, period=1):
        r"""
        Returns an iterator of the longest prefix of self having the given
        period.

        INPUT:

        - ``period`` - positive integer (optional, default 1)

        OUTPUT:

        iterator

        EXAMPLES::

            sage: list(Word([])._longest_periodic_prefix_iterator())
            []
            sage: list(Word([1])._longest_periodic_prefix_iterator())
            [1]
            sage: list(Word([1,2])._longest_periodic_prefix_iterator())
            [1]
            sage: list(Word([1,1,2])._longest_periodic_prefix_iterator())
            [1, 1]
            sage: list(Word([1,1,1,2])._longest_periodic_prefix_iterator())
            [1, 1, 1]
            sage: Word(Word(lambda n:0)._longest_periodic_prefix_iterator())
            word: 0000000000000000000000000000000000000000...
            sage: list(Word([1,2,1,2,1,3])._longest_periodic_prefix_iterator(2))
            [1, 2, 1, 2, 1]
        """
        for i,l in enumerate(self):
            if self[i%period] == l:
                yield l
            else:
                raise StopIteration

    def longest_periodic_prefix(self, period=1):
        r"""
        Returns the longest prefix of self having the given period.

        INPUT:

        - ``period`` - positive integer (optional, default 1)

        OUTPUT:

        word

        EXAMPLES::

            sage: Word([]).longest_periodic_prefix()
            word:
            sage: Word([1]).longest_periodic_prefix()
            word: 1
            sage: Word([1,2]).longest_periodic_prefix()
            word: 1
            sage: Word([1,1,2]).longest_periodic_prefix()
            word: 11
            sage: Word([1,2,1,2,1,3]).longest_periodic_prefix(2)
            word: 12121
            sage: type(_)
            <class 'sage.combinat.words.word.FiniteWord_iter_with_caching'>
            sage: Word(lambda n:0).longest_periodic_prefix()
            word: 0000000000000000000000000000000000000000...
        """
        from sage.combinat.words.word import FiniteWord_class
        length = 'finite' if isinstance(self, FiniteWord_class) else 'unknown'
        return self._parent(self._longest_periodic_prefix_iterator(period), length=length)

    def is_empty(self):
        r"""
        Returns True if the length of self is zero, and False otherwise.

        EXAMPLES::

            sage: it = iter([])
            sage: Word(it).is_empty()
            True
            sage: it = iter([1,2,3])
            sage: Word(it).is_empty()
            False
            sage: from itertools import count
            sage: Word(count()).is_empty()
            False
        """
        try:
            iter(self).next()
            return False
        except StopIteration:
            return True

    def _to_integer_iterator(self, use_parent_alphabet=False):
        r"""
        Returns an iterator over the letters of an integer representation of
        self.

        INPUT:

        - ``use_parent_alphabet`` - Bool (default: False). When True and if
          the self parent's alphabet is finite, it uses the index of
          the letters in the alphabet. Otherwise, the first letter occurring in
          self is mapped to zero, and every letter that hasn't yet occurred in
          the word is mapped to the next available integer.

        EXAMPLES::

            sage: from itertools import count
            sage: w = Word(count())
            sage: ir = w._to_integer_iterator()
            sage: [ir.next() for _ in range(10)]
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            sage: w = Word(iter("abbacabba"))
            sage: ir = w._to_integer_iterator()
            sage: list(ir)
            [0, 1, 1, 0, 2, 0, 1, 1, 0]

        ::

            sage: w = Words('abc')('abbccc')
            sage: list(w._to_integer_iterator(True))
            [0, 1, 1, 2, 2, 2]
            sage: w = Words('acb')('abbccc')
            sage: list(w._to_integer_iterator(True))
            [0, 2, 2, 1, 1, 1]
            sage: w = Words('xabc')('abbccc')
            sage: list(w._to_integer_iterator(True))
            [1, 2, 2, 3, 3, 3]
        """
        from sage.combinat.words.words import Words_over_Alphabet
        if use_parent_alphabet and\
           isinstance(self.parent(), Words_over_Alphabet):
            A = self.parent().alphabet()
            for letter in self:
                yield A.rank(letter)

        else:
            mapping = {}
            next_value = 0
            for letter in self:
                if not(letter in mapping):
                    mapping[letter] = next_value
                    next_value += 1
                yield mapping[letter]

    def to_integer_word(self):
        r"""
        Returns a word over the integers whose letters are those output by
        self._to_integer_iterator()

        EXAMPLES::

            sage: from itertools import count
            sage: w = Word(count()); w
            word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...
            sage: w.to_integer_word()
            word: 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,...
            sage: w = Word(iter("abbacabba"), length="finite"); w
            word: abbacabba
            sage: w.to_integer_word()
            word: 011020110
            sage: w = Word(iter("abbacabba"), length="unknown"); w
            word: abbacabba
            sage: w.to_integer_word()
            word: 011020110
        """
        length = "unknown" if self._len is None else self._len
        from sage.combinat.words.word import Word
        return Word(self._to_integer_iterator(), length=length)

    def lex_less(self, other):
        r"""
        Returns True if self is lexicographically less than other.

        EXAMPLES::

            sage: w = Word([1,2,3])
            sage: u = Word([1,3,2])
            sage: v = Word([3,2,1])
            sage: w.lex_less(u)
            True
            sage: v.lex_less(w)
            False
            sage: a = Word("abba")
            sage: b = Word("abbb")
            sage: a.lex_less(b)
            True
            sage: b.lex_less(a)
            False

        For infinite words::

            sage: t = words.ThueMorseWord()
            sage: t.lex_less(t[:10])
            False
            sage: t[:10].lex_less(t)
            True
        """
        return self < other

    def lex_greater(self, other):
        r"""
        Returns True if self is lexicographically greater than other.

        EXAMPLES::

            sage: w = Word([1,2,3])
            sage: u = Word([1,3,2])
            sage: v = Word([3,2,1])
            sage: w.lex_greater(u)
            False
            sage: v.lex_greater(w)
            True
            sage: a = Word("abba")
            sage: b = Word("abbb")
            sage: a.lex_greater(b)
            False
            sage: b.lex_greater(a)
            True

        For infinite words::

            sage: t = words.ThueMorseWord()
            sage: t[:10].lex_greater(t)
            False
            sage: t.lex_greater(t[:10])
            True
        """
        return self > other

    def apply_morphism(self,morphism):
        r"""
        Returns the word obtained by applying the morphism to self.

        INPUT:

        -  ``morphism`` - Can be an instance of WordMorphism, or
           anything that can be used to construct one.

        EXAMPLES::

            sage: w = Word("ab")
            sage: d = {'a':'ab', 'b':'ba'}
            sage: w.apply_morphism(d)
            word: abba
            sage: w.apply_morphism(WordMorphism(d))
            word: abba

        ::

            sage: w = Word('ababa')
            sage: d = dict(a='ab', b='ba')
            sage: d
            {'a': 'ab', 'b': 'ba'}
            sage: w.apply_morphism(d)
            word: abbaabbaab

        For infinite words::

            sage: t = words.ThueMorseWord([0,1]); t
            word: 0110100110010110100101100110100110010110...
            sage: t.apply_morphism({0:8,1:9})
            word: 8998988998898998988989988998988998898998...
        """
        from sage.combinat.words.morphism import WordMorphism
        if not isinstance(morphism, WordMorphism):
            morphism = WordMorphism(morphism)
        return morphism(self)

    def _delta_iterator(self):
        r"""
        Returns an iterator of the image of self under the delta morphism.
        This is the word composed of the length of consecutive runs of the
        same letter in a given word.

        OUTPUT:

            generator object

        EXAMPLES::

            sage: W = Words('0123456789')
            sage: it=W('22112122')._delta_iterator()
            sage: Word(it)
            word: 22112
            sage: Word(W('555008')._delta_iterator())
            word: 321
            sage: Word(W()._delta_iterator())
            word:

        For infinite words::

            sage: t = words.ThueMorseWord()
            sage: it = t._delta_iterator()
            sage: Word(it)
            word: 1211222112112112221122211222112112112221...
        """
        for letter, run in groupby(self):
            yield len(list(run))

    def delta(self):
        r"""
        Returns the image of self under the delta morphism. This is the
        word composed of the length of consecutive runs of the same letter
        in a given word.

        OUTPUT:

            Word over integers

        EXAMPLES:

        For finite words::

            sage: W = Words('0123456789')
            sage: W('22112122').delta()
            word: 22112
            sage: W('555008').delta()
            word: 321
            sage: W().delta()
            word:
            sage: Word('aabbabaa').delta()
            word: 22112

        For infinite words::

            sage: t = words.ThueMorseWord()
            sage: t.delta()
            word: 1211222112112112221122211222112112112221...
        """
        from sage.combinat.words.word import Word
        return Word(self._delta_iterator())

    def _iterated_right_palindromic_closure_iterator(self, f=None):
        r"""
        Returns an iterator over the iterated (`f`-)palindromic closure of self.

        INPUT:

        -  ``f`` - involution (default: None) on the alphabet of self. It must
           be callable on letters as well as words (e.g. WordMorphism).

        OUTPUT:

            iterator -- the iterated (`f`-)palindromic closure of self

        EXAMPLES::

            sage: w = Word('abc')
            sage: it = w._iterated_right_palindromic_closure_iterator()
            sage: Word(it)
            word: abacaba

        ::

            sage: w = Word('aaa')
            sage: it = w._iterated_right_palindromic_closure_iterator()
            sage: Word(it)
            word: aaa

        ::

            sage: w = Word('abbab')
            sage: it = w._iterated_right_palindromic_closure_iterator()
            sage: Word(it)
            word: ababaabababaababa

        An infinite word::

            sage: t = words.ThueMorseWord('ab')
            sage: it = t._iterated_right_palindromic_closure_iterator()
            sage: Word(it)
            word: ababaabababaababaabababaababaabababaabab...

        TESTS:

        The empty word::

            sage: w = Word()
            sage: it = w._iterated_right_palindromic_closure_iterator()
            sage: it.next()
            Traceback (most recent call last):
            ...
            StopIteration

        REFERENCES:

        -   [1] A. de Luca, A. De Luca, Pseudopalindrome closure operators
            in free monoids, Theoret. Comput. Sci. 362 (2006) 282--300.
        """
        par = self.parent()
        w = self[:0]
        for letter in self:
            length_before = w.length()
            w = (w*par([letter])).palindromic_closure(f=f)
            length_after = w.length()
            d = length_after - length_before
            for a in w[-d:]:
                yield a

    def _iterated_right_palindromic_closure_recursive_iterator(self, f=None):
        r"""
        Returns an iterator over the iterated (`f`-)palindromic closure of self.

        INPUT:

        -  ``f`` - involution (default: None) on the alphabet of self. It must
           be callable on letters as well as words (e.g. WordMorphism).

        OUTPUT:

            iterator -- the iterated (`f`-)palindromic closure of self

        ALGORITHM:

            For the case of palindromes only, it has been shown in [2] that
            the iterated right palindromic closure of a given word `w`,
            denoted by `IRPC(w)`, may be obtained as follows.
            Let `w` be any word and `x` be a letter. Then

            #. If `x` does not occur in `w`,
               `IRPC(wx) = IRPC(w) \cdot x \cdot IRPC(w)`
            #. Otherwise, write `w = w_1xw_2` such that `x` does not
               occur in `w_2`. Then `IRPC(wx) = IRPC(w) \cdot IRPC(w_1)^{-1}
               \cdot IRPC(w)`

            This formula is directly generalized to the case of `f`-palindromes.
            See [1] for more details.

        EXAMPLES::

            sage: w = Word('abc')
            sage: it = w._iterated_right_palindromic_closure_recursive_iterator()
            sage: Word(it)
            word: abacaba

        ::

            sage: w = Word('aaa')
            sage: it = w._iterated_right_palindromic_closure_recursive_iterator()
            sage: Word(it)
            word: aaa

        ::

            sage: w = Word('abbab')
            sage: it = w._iterated_right_palindromic_closure_recursive_iterator()
            sage: Word(it)
            word: ababaabababaababa

        An infinite word::

            sage: t = words.ThueMorseWord('ab')
            sage: it = t._iterated_right_palindromic_closure_recursive_iterator()
            sage: Word(it)
            word: ababaabababaababaabababaababaabababaabab...

        TESTS:

        The empty word::

            sage: w = Word()
            sage: it = w._iterated_right_palindromic_closure_recursive_iterator()
            sage: it.next()
            Traceback (most recent call last):
            ...
            StopIteration

        REFERENCES:

        -   [1] A. de Luca, A. De Luca, Pseudopalindrome closure operators
            in free monoids, Theoret. Comput. Sci. 362 (2006) 282--300.
        -   [2] J. Justin, Episturmian morphisms and a Galois theorem on
            continued fractions, RAIRO Theoret. Informatics Appl. 39 (2005)
            207-215.
        """
        parent = self.parent()
        ipcw = self[:0]
        lengths = []
        for i, letter in enumerate(self):
            lengths.append(ipcw.length())
            w = self[:i]
            pos = w.rfind(parent([letter]))
            if pos == -1:
                to_append = parent([letter]).palindromic_closure(f=f) + ipcw
            else:
                to_append = ipcw[lengths[pos]:]
            ipcw += to_append
            for a in to_append:
                yield a

    def iterated_right_palindromic_closure(self, f=None, algorithm='recursive'):
        r"""
        Returns the iterated (`f`-)palindromic closure of self.

        INPUT:

        -  ``f`` - involution (default: None) on the alphabet of self. It must
           be callable on letters as well as words (e.g. WordMorphism).

        -  ``algorithm`` - string (default: ``'recursive'``) specifying which
           algorithm to be used when computing the iterated palindromic closure.
           It must be one of the two following values:

           - ``'definition'`` - computed using the definition
           - ``'recursive'`` - computation based on an efficient formula
             that recursively computes the iterated right palindromic closure
             without having to recompute the longest `f`-palindromic suffix
             at each iteration [2].

        OUTPUT:

            word -- the iterated (`f`-)palindromic closure of self

        EXAMPLES::

            sage: w = Word('abc')
            sage: w.iterated_right_palindromic_closure()
            word: abacaba

        ::

            sage: w = Word('aaa')
            sage: w.iterated_right_palindromic_closure()
            word: aaa

        ::

            sage: w = Word('abbab')
            sage: w.iterated_right_palindromic_closure()
            word: ababaabababaababa

        A right `f`-palindromic closure::

            sage: f = WordMorphism('a->b,b->a')
            sage: w = Word('abbab')
            sage: w.iterated_right_palindromic_closure(f=f)
            word: abbaabbaababbaabbaabbaababbaabbaab

        An infinite word::

            sage: t = words.ThueMorseWord('ab')
            sage: t.iterated_right_palindromic_closure()
            word: ababaabababaababaabababaababaabababaabab...

        There are two implementations computing the iterated right
        `f`-palindromic closure, the latter being much more efficient::

            sage: w = Word('abaab')
            sage: u = w.iterated_right_palindromic_closure(algorithm='definition')
            sage: v = w.iterated_right_palindromic_closure(algorithm='recursive')
            sage: u
            word: abaabaababaabaaba
            sage: u == v
            True
            sage: w = words.RandomWord(8)
            sage: u = w.iterated_right_palindromic_closure(algorithm='definition')
            sage: v = w.iterated_right_palindromic_closure(algorithm='recursive')
            sage: u == v
            True

        TESTS:

        The empty word::

            sage: w = Word()
            sage: w.iterated_right_palindromic_closure()
            word:

        If the word is finite, so is the result::

            sage: w = Word([0,1]*7)
            sage: c = w.iterated_right_palindromic_closure()
            sage: type(c)
            <class 'sage.combinat.words.word.FiniteWord_iter_with_caching'>

        REFERENCES:

        -   [1] A. de Luca, A. De Luca, Pseudopalindrome closure operators
            in free monoids, Theoret. Comput. Sci. 362 (2006) 282--300.
        -   [2] J. Justin, Episturmian morphisms and a Galois theorem on
            continued fractions, RAIRO Theoret. Informatics Appl. 39 (2005)
            207-215.
        """
        from sage.combinat.words.word import FiniteWord_class, InfiniteWord_class
        if isinstance(self, FiniteWord_class):
            length = "finite"
        elif isinstance(self, InfiniteWord_class):
            length = None
        else:
            length = "unknown"
        if algorithm == 'definition':
            it = self._iterated_right_palindromic_closure_iterator(f=f)
        elif algorithm == 'recursive':
            it = self._iterated_right_palindromic_closure_recursive_iterator(f=f)
        else:
            raise ValueError, "algorithm (=%s) must be either 'definition' or 'recursive'"
        return self._parent(it, length=length)

    def prefixes_iterator(self, max_length=None):
        r"""
        Returns an iterator over the prefixes of self.

        INPUT:

        - ``max_length`` - non negative integer or None (optional,
          default: None) the maximum length of the prefixes

        OUTPUT:

            iterator

        EXAMPLES::

            sage: w = Word('abaaba')
            sage: for p in w.prefixes_iterator(): print p
            word:
            word: a
            word: ab
            word: aba
            word: abaa
            word: abaab
            word: abaaba
            sage: for p in w.prefixes_iterator(max_length=3): print p
            word:
            word: a
            word: ab
            word: aba

        You can iterate over the prefixes of an infinite word::

            sage: f = words.FibonacciWord()
            sage: for p in f.prefixes_iterator(max_length=8): print p
            word:
            word: 0
            word: 01
            word: 010
            word: 0100
            word: 01001
            word: 010010
            word: 0100101
            word: 01001010

        TESTS::

            sage: list(f.prefixes_iterator(max_length=0))
            [word: ]
        """
        to_consider = self if max_length is None else self[:max_length]
        yield self[:0]
        for (i,a) in enumerate(to_consider):
            yield self[:i+1]

    def palindrome_prefixes_iterator(self, max_length=None):
        r"""
        Returns an iterator over the palindrome prefixes of self.

        INPUT:

        - ``max_length`` - non negative integer or None (optional,
          default: None) the maximum length of the prefixes

        OUTPUT:

            iterator

        EXAMPLES::

            sage: w = Word('abaaba')
            sage: for pp in w.palindrome_prefixes_iterator(): print pp
            word:
            word: a
            word: aba
            word: abaaba
            sage: for pp in w.palindrome_prefixes_iterator(max_length=4): print pp
            word:
            word: a
            word: aba

        You can iterate over the palindrome prefixes of an infinite word::

            sage: f = words.FibonacciWord()
            sage: for pp in f.palindrome_prefixes_iterator(max_length=20): print pp
            word:
            word: 0
            word: 010
            word: 010010
            word: 01001010010
            word: 0100101001001010010
        """
        for p in self.prefixes_iterator(max_length):
            if p.is_palindrome():
                yield p

    @lazy_attribute
    def _word_content(self):
        r"""
        EXAMPLES::

            sage: w = Word('abaccefa')
            sage: w._word_content
            doctest:...: DeprecationWarning: _word_content is deprecated! try to_integer_word instead! See the documentation for more information
            word: 01022340
        """
        from sage.misc.misc import deprecation
        deprecation("_word_content is deprecated! try to_integer_word instead! See the documentation for more information")
        return self.to_integer_word()

    def alphabet(self):
        r"""
        EXAMPLES::

            sage: w = Word('abaccefa')
            sage: w. alphabet()
            doctest:1: DeprecationWarning: alphabet() is deprecated, use parent().alphabet() instead
            Python objects
            sage: y = Words('456')('64654564')
            sage: y.alphabet()
            Ordered Alphabet ['4', '5', '6']

        """
        from sage.misc.misc import deprecation
        deprecation("alphabet() is deprecated, use parent().alphabet() instead")
        return self.parent().alphabet()

    def _partial_sums_iterator(self, start, mod=None):
        r"""
        Iterator over the partial sums of the prefixes of self.

        INPUT:

        - ``self`` - A word over the integers.
        - ``start`` - integer, the first letter of the resulting word.
        - ``mod`` - (default: None) It can be one of the following:
            - None or 0 : result is over the integers
            - integer : result is over the integers modulo ``mod``.

        EXAMPLES::

            sage: w = Word(range(8))
            sage: list(w._partial_sums_iterator(0, mod=10))
            [0, 0, 1, 3, 6, 0, 5, 1, 8]

        ::

            sage: w = Word([1,1,1,1,1,1,1,1,1,1,1,1])
            sage: list(w._partial_sums_iterator(0, mod=10))
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2]

        ::

            sage: w = Word([1,1,1,1,1,1,1,1,1,1,1,1])
            sage: list(w._partial_sums_iterator(0))
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        """
        if mod in (None, 0):
            sum = start

        elif mod in ZZ:
            Zn = Integers(mod)
            sum = Zn(start)

        else:
            raise TypeError, 'mod(=%s) must be None or an integer'%mod

        yield sum
        for letter in self:
            sum += letter
            yield sum

    def partial_sums(self, start, mod=None):
        r"""
        Returns the word defined by the partial sums of its prefixes.

        INPUT:

        - ``self`` - A word over the integers.
        - ``start`` - integer, the first letter of the resulting word.
        - ``mod`` - (default: None) It can be one of the following:
            - None or 0 : result is over the integers
            - integer : result is over the integers modulo ``mod``.

        EXAMPLES::

            sage: w = Word(range(10))
            sage: w.partial_sums(0)
            word: 0,0,1,3,6,10,15,21,28,36,45
            sage: w.partial_sums(1)
            word: 1,1,2,4,7,11,16,22,29,37,46

        ::

            sage: w = Word([1,2,3,1,2,3,2,2,2,2])
            sage: w.partial_sums(0, mod=None)
            word: 0,1,3,6,7,9,12,14,16,18,20
            sage: w.partial_sums(0, mod=0)
            word: 0,1,3,6,7,9,12,14,16,18,20
            sage: w.partial_sums(0, mod=8)
            word: 01367146024
            sage: w.partial_sums(0, mod=4)
            word: 01323102020
            sage: w.partial_sums(0, mod=2)
            word: 01101100000
            sage: w.partial_sums(0, mod=1)
            word: 00000000000

        TESTS:

        If the word is infinite, so is the result::

            sage: w = Word(lambda n:1)
            sage: u = w.partial_sums(0)
            sage: type(u)
            <class 'sage.combinat.words.word.InfiniteWord_iter_with_caching'>
        """
        it = self._partial_sums_iterator(start=start, mod=mod)

        if mod in (None, 0):
            alphabet = None
        elif mod in ZZ:
            alphabet = Integers(mod)

        from sage.combinat.words.word import FiniteWord_class, InfiniteWord_class
        if isinstance(self, FiniteWord_class):
            length = "finite"
        elif isinstance(self, InfiniteWord_class):
            length = None
        else:
            length = "unknown"
        from sage.combinat.words.word import Word
        return Word(it, alphabet=alphabet, length=length)

    def _finite_differences_iterator(self, mod=None):
        r"""
        Iterator over the diffences of consecutive letters of self.

        INPUT:

        - ``self`` - A word over the integers.
        - ``mod`` - (default: None) It can be one of the following:
            - None or 0 : result is over the integers
            - integer : result is over the integers modulo ``mod``.

        EXAMPLES::

            sage: w = Word(x^2 for x in range(10))
            sage: list(w._finite_differences_iterator())
            [1, 3, 5, 7, 9, 11, 13, 15, 17]

        ::

            sage: w = Word([1,6,8,4,2,6,8,2,3])
            sage: list(w._finite_differences_iterator())
            [5, 2, -4, -2, 4, 2, -6, 1]
            sage: list(w._finite_differences_iterator(4))
            [1, 2, 0, 2, 0, 2, 2, 1]
            sage: list(w._finite_differences_iterator(5))
            [0, 2, 1, 3, 4, 2, 4, 1]

        TESTS::

            sage: w = Word([2,3,6])
            sage: list(w._finite_differences_iterator())
            [1, 3]
            sage: w = Word([2,6])
            sage: list(w._finite_differences_iterator())
            [4]
            sage: w = Word([2])
            sage: list(w._finite_differences_iterator())
            []
            sage: w = Word()
            sage: list(w._finite_differences_iterator())
            []

        ::

            sage: list(w._finite_differences_iterator('a'))
            Traceback (most recent call last):
            ...
            TypeError: mod(=a) must be None or an integer
        """
        if mod in (None, 0):
            i = iter(self)
            j = iter(self)
            j.next()
            while True:
                yield j.next() - i.next()

        elif mod in ZZ:
            Zn = Integers(mod)
            i = iter(self)
            j = iter(self)
            j.next()
            while True:
                yield Zn(j.next() - i.next())

        else:
            raise TypeError, 'mod(=%s) must be None or an integer'%mod

    def finite_differences(self, mod=None):
        r"""
        Returns the word obtained by the diffences of consecutive letters
        of self.

        INPUT:

        - ``self`` - A word over the integers.
        - ``mod`` - (default: None) It can be one of the following:
            - None or 0 : result is over the integers
            - integer : result is over the integers modulo ``mod``.

        EXAMPLES::

            sage: w = Word([x^2 for x in range(10)])
            sage: w.finite_differences()
            word: 1,3,5,7,9,11,13,15,17
            sage: w.finite_differences(mod=4)
            word: 131313131
            sage: w.finite_differences(mod=0)
            word: 1,3,5,7,9,11,13,15,17

        TESTS::

            sage: w = Word([2,3,6])
            sage: w.finite_differences()
            word: 13
            sage: w = Word([2,6])
            sage: w.finite_differences()
            word: 4
            sage: w = Word([2])
            sage: w.finite_differences()
            word:
            sage: w = Word()
            sage: w.finite_differences()
            word:

        If the word is infinite, so is the result::

            sage: w = Word(lambda n:n)
            sage: u = w.finite_differences()
            sage: u
            word: 1111111111111111111111111111111111111111...
            sage: type(u)
            <class 'sage.combinat.words.word.InfiniteWord_iter_with_caching'>
        """
        it = self._finite_differences_iterator(mod=mod)

        if mod in (None, 0):
            alphabet = None
        elif mod in ZZ:
            alphabet = Integers(mod)

        from sage.combinat.words.word import FiniteWord_class, InfiniteWord_class
        if isinstance(self, FiniteWord_class):
            length = "finite"
        elif isinstance(self, InfiniteWord_class):
            length = None
        else:
            length = "unknown"
        from sage.combinat.words.word import Word
        return Word(it, alphabet=alphabet, length=length)
