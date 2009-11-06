# coding=utf-8
r"""
A collection of constructors of common words

AUTHORS:

    - Franco Saliola (2008-12-17): merged into sage
    - Sebastien Labbe (2008-12-17): merged into sage
    - Arnaud Bergeron (2008-12-17): merged into sage
    - Amy Glen (2008-12-17): merged into sage

USE:

To see a list of all word constructors, type “words.” and then press the tab
key. The documentation for each constructor includes information about each
word, which provides a useful reference.

EXAMPLES::

    sage: t = words.ThueMorseWord(); t
    word: 0110100110010110100101100110100110010110...
"""
#*****************************************************************************
#       Copyright (C) 2008 Franco Saliola <saliola@gmail.com>,
#                          Sebastien Labbe <slabqc@gmail.com>,
#                          Arnaud Bergeron <abergeron@gmail.com>,
#                          Amy Glen <amy.glen@gmail.com>
#
#  Distributed under the terms of the GNU General Public License version 2 (GPLv2)
#
#  The full text of the GPLv2 is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from itertools import cycle, count
from random import randint
from sage.misc.cachefunc import cached_method
from sage.structure.sage_object import SageObject
from sage.rings.all import ZZ
from sage.rings.infinity import Infinity
from sage.combinat.words.word import (FiniteWord_class, Word_class,
        FiniteWord_list, Factorization)
from sage.combinat.words.words import Words
from sage.combinat.words.morphism import WordMorphism
from sage.rings.arith import gcd

def _build_tab(sym, tab, W):
    r"""
    Internal function building a coding table for the ``phi_inv_tab`` function.

    TESTS::

        sage: from sage.combinat.words.word_generators import _build_tab
        sage: _build_tab(1, [], Words([1, 2]))
        [1]
        sage: _build_tab(1, [1], Words([1, 2]))
        [1, 2]
        sage: _build_tab(2, [1], Words([1, 2]))
        [2, 2]
        sage: _build_tab(2, [1, 2], Words([1, 2]))
        [2, 2, 1]
        sage: _build_tab(1, [2, 2], Words([1, 2]))
        [1, 1, 2]
    """
    res = [sym]
    if len(tab) == 0:
        return res
    if sym == 1:
        res += tab
        res[1] = (res[1] % W.size_of_alphabet()) + 1
        return res
    w = W([sym]).delta_inv(W, tab[0])
    w = w[1:]
    res.append((w[-1] % W.size_of_alphabet()) + 1)
    for i in xrange(1, len(tab)):
        w = w.delta_inv(W, tab[i])
        res.append((w[-1] % W.size_of_alphabet()) + 1)
    return res

class LowerChristoffelWord(FiniteWord_list):
    r"""
    Returns the lower Christoffel word of slope `p/q`, where `p` and
    `q` are relatively prime non-negative integers, over the given
    two-letter alphabet.

    The *Christoffel word of slope `p/q`* is obtained from the
    Cayley graph of `\ZZ/(p+q)\ZZ` with generator `q` as
    follows. If `u \rightarrow v` is an edge in the Cayley graph, then
    `v = u + p \mod{p+q}`. Label the edge `u \rightarrow v` by
    ``alphabet[1]`` if `u < v` and ``alphabet[0]`` otherwise. The Christoffel
    word is the word obtained by reading the edge labels along the
    cycle beginning from 0.

    EXAMPLES::

        sage: words.LowerChristoffelWord(4,7)
        word: 00100100101

    ::

        sage: words.LowerChristoffelWord(4,7,alphabet='ab')
        word: aabaabaabab

    TESTS::

        sage: words.LowerChristoffelWord(1,0)
        word: 1
        sage: words.LowerChristoffelWord(0,1,'xy')
        word: x
        sage: words.LowerChristoffelWord(1,1)
        word: 01
    """

    def __init__(self, p, q, alphabet=(0,1)):
        r"""
        TESTS::

            sage: words.LowerChristoffelWord(4,8)
            Traceback (most recent call last):
            ...
            ValueError: 4 and 8 are not relatively prime
            sage: words.LowerChristoffelWord(17, 39, 'xyz')
            Traceback (most recent call last):
            ...
            ValueError: alphabet must contain exactly two distinct elements
            sage: w = words.LowerChristoffelWord(4,7)
            sage: w2 = loads(dumps(w))
            sage: w == w2
            True
            sage: type(w2)
            <class 'sage.combinat.words.word_generators.LowerChristoffelWord'>
            sage: _ = w2.standard_factorization() # hackish test for self.__p and self.__q
        """
        if len(set(alphabet)) != 2:
            raise ValueError, "alphabet must contain exactly two distinct elements"
        # Compute gcd of p, q; raise TypeError if not 1.
        if gcd(p,q) != 1:
            raise ValueError, "%s and %s are not relatively prime" % (p, q)
        # Compute the Christoffel word
        w = []
        u = 0
        if (p, q) == (0, 1):
            w = [alphabet[0]]
        else:
            for i in range(p + q):
                v = (u+p) % (p+q)
                new_letter = alphabet[0] if u < v else alphabet[1]
                w.append(new_letter)
                u = v
        super(LowerChristoffelWord, self).__init__(Words(alphabet), w)
        self.__p = p
        self.__q = q

    def markoff_number(self):
        r"""
        Returns the Markoff number associated to the Christoffel word self.

        The *Markoff number* of a Christoffel word `w` is `trace(M(w))/3`,
        where `M(w)` is the `2\times 2` matrix obtained by applying the
        morphism:
        0 -> matrix(2,[2,1,1,1])
        1 -> matrix(2,[5,2,2,1])

        EXAMPLES::

            sage: w0 = words.LowerChristoffelWord(4,7)
            sage: w1, w2 = w0.standard_factorization()
            sage: (m0,m1,m2) = (w.markoff_number() for w in (w0,w1,w2))
            sage: (m0,m1,m2)
            (294685, 13, 7561)
            sage: m0**2 + m1**2 + m2**2 == 3*m0*m1*m2
            True
        """
        from sage.matrix.constructor import matrix
        eta = {0:matrix(2,[2,1,1,1]), 1:matrix(2,[5,2,2,1])}
        M = matrix(2,[1,0,0,1])
        for a in self:
            M *= eta[a]
        return M.trace()/3

    def standard_factorization(self):
        r"""
        Returns the standard factorization of the Christoffel word ``self``.

        The *standard factorization* of a Christoffel word `w` is the
        unique factorization of `w` into two Christoffel words.

        EXAMPLES::

            sage: w = words.LowerChristoffelWord(5,9)
            sage: print w
            word: 00100100100101
            sage: w1, w2 = w.standard_factorization()
            sage: print w1
            word: 001
            sage: print w2
            word: 00100100101

        ::

            sage: w = words.LowerChristoffelWord(51,37)
            sage: w1, w2 = w.standard_factorization()
            sage: w1
            word: 0101011010101101011
            sage: w2
            word: 0101011010101101011010101101010110101101...
            sage: w1 * w2 == w
            True
        """
        p, q = self.__p, self.__q
        index = 0
        u = 0
        for i in range(p + q):
            v = (u+p) % (p+q)
            if v == 1:
                index = i
                break
            u = v
        w1, w2 = self[:index+1], self[index+1:]
        return Factorization([LowerChristoffelWord(w1.count(1),w1.count(0)),
                LowerChristoffelWord(w2.count(1),w2.count(0))])

    def __reduce__(self):
        r"""
        EXAMPLES::

            sage: from sage.combinat.words.word_generators import LowerChristoffelWord
            sage: w = LowerChristoffelWord(5,7)
            sage: w.__reduce__()
            (<class 'sage.combinat.words.word_generators.LowerChristoffelWord'>, (5, 7, Ordered Alphabet [0, 1]))
        """
        return self.__class__, (self.__p, self.__q, self.parent().alphabet())

class ChristoffelWord_Lower(LowerChristoffelWord):
    def __new__(cls, *args, **kwds):
        r"""
        TEST:
            sage: from sage.combinat.words.word_generators import ChristoffelWord_Lower
            sage: w = ChristoffelWord_Lower(1,0); w
            doctest:1: DeprecationWarning: ChristoffelWord_Lower is deprecated, use LowerChristoffelWord instead
            word: 1
        """
        from sage.misc.misc import deprecation
        deprecation("ChristoffelWord_Lower is deprecated, use LowerChristoffelWord instead")
        return LowerChristoffelWord.__new__(cls, *args, **kwds)

class WordGenerator(object):
    r"""
    A class consisting of constructors for several famous words.

    TESTS::

        sage: from sage.combinat.words.word_generators import WordGenerator
        sage: MyWordBank = WordGenerator()
        sage: type(loads(dumps(MyWordBank)))
        <class 'sage.combinat.words.word_generators.WordGenerator'>

    """

    def ThueMorseWord(self, alphabet=(0, 1), base=2):
        r"""
        Returns the (Generalized) Thue-Morse word over the given alphabet.

        There are several ways to define the Thue-Morse word `t`.
        We use the following definition: `t[n]` is the sum modulo `m` of
        the digits in the given base expansion of `n`.

        INPUT:

        -  ``alphabet`` - (default: (0, 1) ) any container that is suitable to
           build an instance of OrderedAlphabet (list, tuple, str, ...)

        -  ``base`` - an integer (default : 2) greater or equal to 2

        EXAMPLES:

        Thue-Morse word::

            sage: t = words.ThueMorseWord(); t
            word: 0110100110010110100101100110100110010110...

        Thue-Morse word on other alphabets::

            sage: t = words.ThueMorseWord('ab'); t
            word: abbabaabbaababbabaababbaabbabaabbaababba...

        ::

            sage: t = words.ThueMorseWord(['L1', 'L2'])
            sage: t[:8]
            word: L1,L2,L2,L1,L2,L1,L1,L2

        Generalized Thue Morse word::

            sage: words.ThueMorseWord(alphabet=(0,1,2), base=2)
            word: 0112122012202001122020012001011212202001...
            sage: t = words.ThueMorseWord(alphabet=(0,1,2), base=5); t
            word: 0120112012201200120112012120122012001201...
            sage: t[100:130].critical_exponent()
            10/3

        TESTS::

            sage: words.ThueMorseWord(alphabet='ab', base=1)
            Traceback (most recent call last):
            ...
            ValueError: base (=1) and len(alphabet) (=2) must be at least 2

        REFERENCES:

        -  [1] A. Blondin-Masse, S. Brlek, A. Glen, and S. Labbe. On the
           critical exponent of generalized Thue-Morse words. *Discrete Math.
           Theor. Comput.  Sci.* 9 (1):293--304, 2007.
        -  [2] Brlek, S. 1989. «Enumeration of the factors in the Thue-Morse
           word», *Discrete Appl. Math.*, vol. 24, p. 83--96.
        -  [3] Morse, M., et G. A. Hedlund. 1938. «Symbolic dynamics»,
           *American Journal of Mathematics*, vol. 60, p. 815--866.
        """
        from functools import partial
        f = partial(self._ThueMorseWord_nth_digit, alphabet=alphabet, base=base)
        w = Words(alphabet)(f, datatype='callable', length=Infinity)

        alphabet = w.parent().alphabet()
        m = w.parent().size_of_alphabet()
        if base < 2 or m < 2 :
            raise ValueError, "base (=%s) and size of alphabet (=%s) must be at least 2"%(base, m)
        return w

    def _ThueMorseWord_nth_digit(self, n, alphabet=(0,1), base=2):
        r"""
        Returns the `n`-th letter of the (Generalized) Thue-Morse word.

        The `n`-th digit of the Thue-Morse word can be defined as the number
        of bits in the 2-complement representation of the position
        modulo 2 which is what this function uses.  The running time
        is `O(\log n)` where `n` is the position desired.

        The `n`-th digit of the Generalized Thue Morse word can be defined as
        the sum of the digits of `n` written in the given base mod `m`,
        where `m` is the length of the given alphabet.

        INPUT:

        - ``n`` - integer, the position
        - ``alphabet`` - an alphabet (default : (0, 1) ) of size at least 2
        - ``base`` - an integer (default : 2) greater or equal to 2

        OUTPUT:

            0 or 1 -- the digit at the position
            letter -- the letter of alphabet at the position

        TESTS::

            sage: from sage.combinat.words.word_generators import WordGenerator
            sage: WordGenerator()._ThueMorseWord_nth_digit(0)
            0
            sage: WordGenerator()._ThueMorseWord_nth_digit(3)
            0
            sage: WordGenerator()._ThueMorseWord_nth_digit(32)
            1
            sage: WordGenerator()._ThueMorseWord_nth_digit(6, 'abc', base = 7)
            'a'

        """
        m = len(alphabet)
        if base == 2 and m == 2:
            for tn in count():
                if n == 0:
                    return alphabet[tn & 1]
                n &= n - 1
        elif base < 2 or m < 2 :
            raise ValueError, "base (=%s) and len(alphabet) (=%s) must be at least 2"%(base, m)
        else:
            return alphabet[ZZ(sum(ZZ(n).digits(base = base))).mod(m)]

    def FibonacciWord(self, alphabet=(0, 1), construction_method="recursive"):
        r"""
        Returns the Fibonacci word on the given two-letter alphabet.

        INPUT:

        -  ``alphabet`` - any container of length two that is suitable to
           build an instance of OrderedAlphabet (list, tuple, str, ...)
        -  ``construction_method`` - can be any of the following:
           "recursive", "fixed point", "function" (see below for definitions).

        Recursive construction: the Fibonacci word is the limit of the
        following sequence of words: `S_0 = 0`, `S_1 = 01`,
        `S_n = S_{n-1} S_{n-2}` for `n \geq 2`.

        Fixed point construction: the Fibonacci word is the fixed point of the
        morphism: `0 \mapsto 01` and `1 \mapsto 0`. Hence, it can be constructed
        by the following read-write process:

        |    beginning at the first letter of `01`,
        |    if the next letter is `0`, append `01` to the word;
        |    if the next letter is `1`, append `1` to the word;
        |    move to the next letter of the word.
        |

        Function: Over the alphabet `\{1, 2\}`, the n-th letter of the
        Fibonacci word is
        `\lfloor (n+2) \varphi \rfloor - \lfloor (n+1) \varphi \rfloor`
        where `\varphi=(1+\sqrt{5})/2` is the golden ratio.

        EXAMPLES::

            sage: w = words.FibonacciWord(construction_method="recursive"); w
            word: 0100101001001010010100100101001001010010...

        ::

            sage: v = words.FibonacciWord(construction_method="recursive", alphabet='ab'); v
            word: abaababaabaababaababaabaababaabaababaaba...

        ::

            sage: u = words.FibonacciWord(construction_method="fixed point"); u
            word: 0100101001001010010100100101001001010010...

        ::

            sage: words.FibonacciWord(construction_method="fixed point", alphabet=[4, 1])
            word: 4144141441441414414144144141441441414414...

        ::

            sage: words.FibonacciWord([0,1], 'function')
            word: 0100101001001010010100100101001001010010...
            sage: words.FibonacciWord('ab', 'function')
            word: abaababaabaababaababaabaababaabaababaaba...

        TESTS::

            sage: from math import floor, sqrt
            sage: golden_ratio = (1 + sqrt(5))/2.0
            sage: a = golden_ratio / (1  + 2*golden_ratio)
            sage: wn = lambda n : int(floor(a*(n+2)) - floor(a*(n+1)))
            sage: f = Words([0,1])(wn); f
            word: 0100101001001010010100100101001001010010...
            sage: f[:10000] == w[:10000]
            True
            sage: f[:10000] == u[:10000] #long time
            True
            sage: words.FibonacciWord("abc")
            Traceback (most recent call last):
            ...
            TypeError: alphabet does not contain two distinct elements
        """
        from sage.combinat.words.alphabet import Alphabet
        alphabet = Alphabet(alphabet)
        if alphabet.cardinality() != 2:
            raise TypeError, "alphabet does not contain two distinct elements"

        a,b = alphabet
        W = Words(alphabet)

        if construction_method == "recursive":
            w = W(self._FibonacciWord_RecursiveConstructionIterator(alphabet), \
                    datatype='iter')
            return w

        elif construction_method in ("fixed point", "fixed_point"):
            d = {b:[a],a:[a,b]}
            w = self.FixedPointOfMorphism(d, a)
            return w

        elif construction_method == "function":
            from sage.functions.other import sqrt, floor
            phi = (1 + sqrt(5))/2 # the golden ratio
            f = lambda n:a if floor((n+2)*phi) - floor((n+1)*phi) == 2 else b
            return W(f)

        else:
            raise NotImplementedError

    def _FibonacciWord_RecursiveConstructionIterator(self,alphabet=(0,1)):
        r"""
        Iterates over the symbols of the Fibonacci word, as defined by
        the following recursive construction: the Fibonacci word is the
        limit of the sequence `S_0 = 0`, `S_1 = 01`, `S_n = S_{n-1}
        S_{n-2}` for `n \geq 2`.

        TESTS::

            sage: from sage.combinat.words.word_generators import WordGenerator
            sage: from itertools import islice
            sage: it = WordGenerator()._FibonacciWord_RecursiveConstructionIterator()
            sage: list(islice(it,13))
            [0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1]
        """
        Fib0 = [0]
        Fib1 = [0,1]
        n = 0
        while True:
            it = iter(Fib1[n:])
            for i in it:
                n += 1
                yield alphabet[i]
            else:
                Fib1, Fib0 = Fib1 + Fib0, Fib1

    def FixedPointOfMorphism(self, morphism, first_letter):
        r"""
        Returns the fixed point of the morphism beginning with
        ``first_letter``.

        A *fixed point* of a morphism `\varphi` is a word `w` such that
        `\varphi(w) = w`.

        INPUT:

        -  ``morphism`` - endomorphism prolongable on first_letter. It must be
           something that WordMorphism's constructor understands
           (dict, str, ...).
        -  ``first_letter`` - the first letter of the fixed point

        OUTPUT:
            word -- the fixed point of the morphism beginning with first_letter

        EXAMPLES::

            sage: mu = {0:[0,1], 1:[1,0]}
            sage: tm = words.FixedPointOfMorphism(mu,0); tm
            word: 0110100110010110100101100110100110010110...
            sage: TM = words.ThueMorseWord()
            sage: tm[:1000] == TM[:1000]
            True

        ::

            sage: mu = {0:[0,1], 1:[0]}
            sage: f = words.FixedPointOfMorphism(mu,0); f
            word: 0100101001001010010100100101001001010010...
            sage: F = words.FibonacciWord(); F
            word: 0100101001001010010100100101001001010010...
            sage: f[:1000] == F[:1000]
            True

        ::

            sage: fp = words.FixedPointOfMorphism('a->abc,b->,c->','a'); fp
            word: abc
        """
        return WordMorphism(morphism).fixed_point(letter=first_letter)

    def CodingOfRotationWord(self, alpha, beta, x=0, alphabet=(0,1)):
        r"""
        Returns the infinite word obtained from the coding of rotation of
        parameters `(\alpha,\beta, x)` over the given two-letter alphabet.

        The *coding of rotation* corresponding to the parameters
        `(\alpha,\beta, x)` is the symbolic sequence `u = (u_n)_{n\geq 0}`
        defined over the binary alphabet `\{0, 1\}` by `u_n = 1` if
        `x+n\alpha\in[0, \beta[` and `u_n = 0` otherwise. See [1].

        EXAMPLES::

            sage: alpha = 0.45
            sage: beta = 0.48
            sage: words.CodingOfRotationWord(0.45, 0.48)
            word: 1101010101001010101011010101010010101010...

        ::

            sage: words.CodingOfRotationWord(0.45, 0.48, alphabet='xy')
            word: yyxyxyxyxyxxyxyxyxyxyyxyxyxyxyxxyxyxyxyx...

        TESTS::

            sage: words.CodingOfRotationWord(0.51,0.43,alphabet=[1,0,2])
            Traceback (most recent call last):
            ...
            TypeError: alphabet does not contain two distinct elements

        REFERENCES:

        -   [1] B. Adamczewski, J. Cassaigne, On the transcendence of real
            numbers with a regular expansion, J. Number Theory 103 (2003)
            27--37.
        """
        if len(set(alphabet)) != 2:
            raise TypeError, "alphabet does not contain two distinct elements"
        from functools import partial
        f = partial(self._CodingOfRotationWord_function,alpha=alpha,beta=beta,x=x,alphabet=alphabet)
        w = Words(alphabet)(f, datatype='callable')
        return w

    def _CodingOfRotationWord_function(self, n, alpha, beta, x=0, alphabet=(0,1)):
        r"""
        Internal function that returns the symbol in position `n` of the
        coding of rotation word corresponding to the parameters `\alpha`,
        `\beta`, and `x`.

        TESTS::

            sage: alpha, beta = 0.45, 0.48
            sage: words._CodingOfRotationWord_function(3, alpha, beta)
            1
            sage: words._CodingOfRotationWord_function(10, alpha, beta)
            0
            sage: words._CodingOfRotationWord_function(17, alpha, beta)
            0
        """
        hauteur = x + n * alpha
        fracH = hauteur.frac()
        if fracH < 0:
            fracH += 1
        if 0 <= fracH < beta:
            return alphabet[1]
        else:
            return alphabet[0]

    def CharacteristicSturmianWord(self, cf, alphabet=(0, 1), repeat=True):
        r"""
        Returns the characteristic Sturmian word over the given two-letter
        alphabet with slope given by the continued fraction
        [0, cf[1], cf[2], ...].
        Here cf should be an iterator.

        The *characteristic Sturmian word of slope*
        `\alpha = [0, d[1] + 1, d[2], d[3], \ldots]` is the limit of the
        sequence: `s_0 = 1, s_1 = 0, \ldots, s_{n+1} = s_n^{d_n} s_{n-1}`
        for `n > 0`.

        Equivalently, the `n`-th term of the characteristic Sturmian word
        of slope `\alpha` is `\lfloor\alpha(n+1)\rfloor -
        \lfloor\alpha n\rfloor + \lfloor\alpha\rfloor`.

        INPUT:

        -  ``alphabet`` - any container of length two that is suitable to
           build an instance of OrderedAlphabet (list, tuple, str, ...)
        -  ``cf`` - an iterator outputting integers (thought of as a
           continued fraction)

        EXAMPLES::

            sage: def cf():
            ...     yield 0
            ...     while True: yield 1
            ...
            sage: F = words.CharacteristicSturmianWord(cf()); F
            word: 0100101001001010010100100101001001010010...
            sage: Fib = words.FibonacciWord(); Fib
            word: 0100101001001010010100100101001001010010...
            sage: F[:10000] == Fib[:10000]
            True

        ::

            sage: def cf():
            ...     yield 0
            ...     while True: yield 1
            ...
            sage: G = words.CharacteristicSturmianWord(cf(),'rs'); G
            word: rsrrsrsrrsrrsrsrrsrsrrsrrsrsrrsrrsrsrrsr...
            sage: print G[:50]
            word: rsrrsrsrrsrrsrsrrsrsrrsrrsrsrrsrrsrsrrsrsrrsrrsrsr

        TESTS::

            sage: words.CharacteristicSturmianWord([1,1,1],'xyz')
            Traceback (most recent call last):
            ...
            TypeError: alphabet does not contain two distinct elements
        """
        if len(set(alphabet)) != 2:
            raise TypeError, "alphabet does not contain two distinct elements"
        if not repeat:
            d = iter(cf)
        else:
            d = cycle(cf)
        w = Words(alphabet)( \
                self._CharacteristicSturmianWord_LetterIterator(d,alphabet), \
                datatype='iter')
        return w

    def _CharacteristicSturmianWord_LetterIterator(self, d, alphabet=(0,1)):
        r"""
        Internal function iterating over the symbols of the characteristic
        Sturmian word of slope `[0, d[1] + 1, d[2], d[3], \ldots]`. This
        word is the limit of the sequence:
            `s_0 = 1, s_1 = 0, \ldots, s_{n+1} = s_n^{d_n} s_{n-1}` for `n > 0`.

        TESTS::

            sage: d = iter([1,1,1,1,1,1])
            sage: list(words._CharacteristicSturmianWord_LetterIterator(d))
            [0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1]
        """
        s0 = [0]
        s1 = [1]
        s1, s0 = s1*(d.next()-1) + s0, s1
        n = 0
        while True:
            for i in s1[n:]:
                n += 1
                yield alphabet[i]
            else:
                s1, s0 = s1*d.next() + s0, s1

    def StandardEpisturmianWord(self, directive_word):
        r"""
        Returns the standard episturmian word (or epistandard word) directed by
        directive_word. Over a 2-letter alphabet, this function
        gives characteristic Sturmian words.

        An infinite word `w` over a finite alphabet `A` is said to be
        *standard episturmian* (or *epistandard*) iff there exists an
        infinite word `x_1x_2x_3\cdots` over `A` (called the *directive
        word* of `w`) such that `w` is the limit as `n` goes to infinity of
        `Pal(x_1\cdots x_n)`, where `Pal` is the iterated palindromic closure
        function.

        Note that an infinite word is *episturmian* if it has the same set
        of factors as some epistandard word.

        See for instance [1], [2], and [3].

        INPUT:

        -  ``directive_word`` - an infinite word or a period of a periodic
           infinite word

        EXAMPLES::

            sage: Fibonacci = words.StandardEpisturmianWord(Words('ab')('ab')); Fibonacci
            word: abaababaabaababaababaabaababaabaababaaba...
            sage: Tribonacci = words.StandardEpisturmianWord(Words('abc')('abc')); Tribonacci
            word: abacabaabacababacabaabacabacabaabacababa...
            sage: S = words.StandardEpisturmianWord(Words('abcd')('aabcabada')); S
            word: aabaacaabaaabaacaabaabaacaabaaabaacaabaa...
            sage: S = words.StandardEpisturmianWord(Fibonacci); S
            word: abaabaababaabaabaababaabaababaabaabaabab...
            sage: S[:25]
            word: abaabaababaabaabaababaaba
            sage: S = words.StandardEpisturmianWord(Tribonacci); S
            word: abaabacabaabaabacabaababaabacabaabaabaca...
            sage: words.StandardEpisturmianWord(123)
            Traceback (most recent call last):
            ...
            TypeError: directive_word is not a word, so it cannot be used to build an episturmian word
            sage: words.StandardEpisturmianWord(Words('ab'))
            Traceback (most recent call last):
            ...
            TypeError: directive_word is not a word, so it cannot be used to build an episturmian word

        REFERENCES:

        -   [1] X. Droubay, J. Justin, G. Pirillo, Episturmian words and some
            constructions of de Luca and Rauzy, Theoret. Comput. Sci. 255
            (2001) 539--553.
        -   [2] J. Justin, G. Pirillo, Episturmian words and episturmian
            morphisms, Theoret. Comput. Sci. 276 (2002) 281--313.
        -   [3] A. Glen, J. Justin, Episturmian words: a survey, Preprint,
            2007, arXiv:0801.1655.
        """
        if not isinstance(directive_word, Word_class):
           raise TypeError, "directive_word is not a word, so it cannot be used to build an episturmian word"
        epistandard = directive_word.parent()(\
                self._StandardEpisturmianWord_LetterIterator(directive_word), \
                datatype='iter')
        return epistandard

    def _StandardEpisturmianWord_LetterIterator(self, directive_word):
        r"""
        Internal iterating over the symbols of the standard episturmian
        word defined by the (directive) word directive_word.

        An infinite word `w` over a finite alphabet `A` is standard episturmian
        (or epistandard) iff there exists an infinite word `x_1x_2x_3\ldots`
        over `A` (called the directive word of `w`) such that `w` is the limit
        as `n` goes to infinity of `Pal(x_1x_2\cdots x_n)`, where `Pal` is the
        iterated palindromic closure function.

        INPUT:

        -  ``directive_word`` - an infinite word or a finite word. If
           directive_word is finite, then it is repeated to give
           an infinite word.

        TESTS::

            sage: import itertools
            sage: it = words._StandardEpisturmianWord_LetterIterator(Word('ab'))
            sage: list(itertools.islice(it, 13))
            ['a', 'b', 'a', 'a', 'b', 'a', 'b', 'a', 'a', 'b', 'a', 'a', 'b']
        """
        if isinstance(directive_word, FiniteWord_class):
           d = cycle(directive_word)
        else:
           d = iter(directive_word)
        W = directive_word.parent()
        w = W(d.next())
        n = 0
        while True:
              for x in w[n:]:
                  n += 1
                  yield x
              else:
                  w = W(w*W(d.next())).palindromic_closure()

    def MinimalSmoothPrefix(self, n):
        r"""
        This function finds and returns the minimal smooth prefix of length
        ``n``.

        See [1] for a definition.

        INPUT:

        - ``n`` - the desired length of the prefix

        OUTPUT:

            word -- the prefix

        NOTE:

        Be patient, this function can take a really long time if asked
        for a large prefix.

        EXAMPLES::

            sage: words.MinimalSmoothPrefix(10)
            word: 1212212112

        REFERENCES:

        -   [1] S. Brlek, G. Melançon, G. Paquin, Properties of the extremal
            infinite smooth words, Discrete Math. Theor. Comput. Sci. 9 (2007)
            33--49.
        """
        tab = []
        W = Words([1, 2])
        suff1 = W([1, 2, 2]).phi_inv()
        suff2 = W([2, 2]).phi_inv()
        w = [1]
        tab = _build_tab(1, tab, W)
        for k in xrange(1, n):
            if suff1._phi_inv_tab(tab) < suff2._phi_inv_tab(tab):
                w.append(1)
                tab = _build_tab(1, tab, W)
            else:
                w.append(2)
                tab = _build_tab(2, tab, W)
        return W(w)

    def RandomWord(self, n, m=2, alphabet=None):
        """
        Returns a random word of length `n` over the given `m`-letter
        alphabet.

        INPUT:

        - ``n`` - integer, the length of the word
        - ``m`` - integer (default 2), the size of the output alphabet
        -  ``alphabet`` - (default is `\{0,1,...,m-1\}`) any container of
           length m that is suitable to build an instance of
           OrderedAlphabet (list, tuple, str, ...)

        EXAMPLES::

            sage: words.RandomWord(10)         # random results
            word: 0110100101
            sage: words.RandomWord(10, 4)      # random results
            word: 0322313320
            sage: words.RandomWord(100, 7)     # random results
            word: 2630644023642516442650025611300034413310...
            sage: words.RandomWord(100, 7, range(-3,4))  # random results
            word: 1,3,-1,-1,3,2,2,0,1,-2,1,-1,-3,-2,2,0,3,0,-3,0,3,0,-2,-2,2,0,1,-3,2,-2,-2,2,0,2,1,-2,-3,-2,-1,0,...
            sage: words.RandomWord(100, 5, "abcde") # random results
            word: acebeaaccdbedbbbdeadeebbdeeebeaaacbadaac...
            sage: words.RandomWord(17, 5, "abcde")     # random results
            word: dcacbbecbddebaadd

        TESTS::

            sage: words.RandomWord(2,3,"abcd")
            Traceback (most recent call last):
            ...
            TypeError: alphabet does not contain 3 distinct elements
        """
        if alphabet is None:
            alphabet = range(m)
        if len(set(alphabet)) != m:
            raise TypeError, "alphabet does not contain %s distinct elements" % m
        return Words(alphabet)([alphabet[randint(0,m-1)] for i in xrange(n)])

    LowerChristoffelWord = LowerChristoffelWord

    ChristoffelWord = LowerChristoffelWord

    def UpperChristoffelWord(self, p, q, alphabet=(0,1)):
        r"""
        Returns the upper Christoffel word of slope `p/q`, where
        `p` and `q` are relatively prime non-negative
        integers, over the given alphabet.

        The *upper Christoffel word of slope `p/q`* is equal to the
        reversal of the lower Christoffel word of slope `p/q`.
        Equivalently, if `xuy` is the lower Christoffel word of
        slope `p/q`, where `x` and `y` are letters,
        then `yux` is the upper Christoffel word of slope
        `p/q` (because `u` is a palindrome).

        INPUT:

        -  ``alphabet`` - any container of length two that is
           suitable to build an instance of OrderedAlphabet (list, tuple, str,
           ...)

        EXAMPLES::

            sage: words.UpperChristoffelWord(1,0)
            word: 1

        ::

            sage: words.UpperChristoffelWord(0,1)
            word: 0

        ::

            sage: words.UpperChristoffelWord(1,1)
            word: 10

        ::

            sage: words.UpperChristoffelWord(4,7)
            word: 10100100100

        TESTS:::

            sage: words.UpperChristoffelWord(51,43,"abc")
            Traceback (most recent call last):
            ...
            ValueError: alphabet must contain exactly two distinct elements
        """
        w = words.LowerChristoffelWord(p, q, alphabet=alphabet).reversal()
        return w

    @cached_method
    def _fibonacci_tile(self, n, q_0=None, q_1=3):
        r"""
        Returns the word `q_n` defined by the recurrence below.

        The sequence `(q_n)_{n\in\NN}` is defined by `q_0=\varepsilon`,
        `q_1=3` and `q_n = \begin{cases}
            q_{n-1}q_{n-2}       & \mbox{if $n\equiv 2 \mod 3$,} \\
            q_{n-1}\bar{q_{n-2}} & \mbox{if $n\equiv 0,1 \mod 3$.}
        \end{cases}` where the operator `\bar{\,}` exchanges the `1` and `3`.

        INPUT:

        - ``n`` - non negative integer
        - ``q_0`` - first initial value (default: None) It can be None, 0, 1,
          2 or 3.
        - ``q_1`` - second initial value (default: 3) It can be None, 0, 1, 2
          or 3.

        EXAMPLES::

            sage: for i in range(10): words._fibonacci_tile(i)
            word:
            word: 3
            word: 3
            word: 31
            word: 311
            word: 31131
            word: 31131133
            word: 3113113313313
            word: 311311331331331131133
            word: 3113113313313311311331331331131131

        REFERENCES:

        -  [1] A. Blondin-Masse, S. Brlek, A. Garon, and S. Labbe. Christoffel
           and Fibonacci Tiles, DGCI 2009, Montreal, to appear in LNCS.

        """
        from sage.combinat.words.all import Words, WordMorphism
        W = Words([0,1,2,3])
        bar = WordMorphism({0:0,1:3,3:1,2:2},codomain=W)
        if n==0:
            a = [] if q_0 is None else [q_0]
            return W(a)
        elif n==1:
            b = [] if q_1 is None else [q_1]
            return W(b)
        elif n%3 == 2:
            u = self._fibonacci_tile(n-1,q_0,q_1)
            v = self._fibonacci_tile(n-2,q_0,q_1)
            return u * v
        else:
            u = self._fibonacci_tile(n-1,q_0,q_1)
            v = bar(self._fibonacci_tile(n-2,q_0,q_1))
            return u * v

    def fibonacci_tile(self, n):
        r"""
        Returns the n-th Fibonacci Tile [1].

        EXAMPLES::

            sage: for i in range(3): words.fibonacci_tile(i)
            Path: 3210
            Path: 323030101212
            Path: 3230301030323212323032321210121232121010...

        REFERENCES:

        -  [1] A. Blondin-Masse, S. Brlek, A. Garon, and S. Labbe. Christoffel
           and Fibonacci Tiles, DGCI 2009, Montreal, to appear in LNCS.
        """
        w = self._fibonacci_tile(3*n+1)
        w = w**4
        from sage.combinat.words.paths import WordPaths
        P = WordPaths([0,1,2,3])
        l = list(w.partial_sums(start=3,mod=4))
        return P(l)[:-1]

    def dual_fibonacci_tile(self, n):
        r"""
        Returns the n-th dual Fibonacci Tile [1].

        EXAMPLES::

            sage: for i in range(4): words.dual_fibonacci_tile(i)
            Path: 3210
            Path: 32123032301030121012
            Path: 3212303230103230321232101232123032123210...
            Path: 3212303230103230321232101232123032123210...

        REFERENCES:

        -  [1] A. Blondin-Masse, S. Brlek, A. Garon, and S. Labbe. Christoffel
           and Fibonacci Tiles, DGCI 2009, Montreal, to appear in LNCS.
        """
        w = self._fibonacci_tile(3*n+1,3,3)
        w = w**4
        from sage.combinat.words.paths import WordPaths
        P = WordPaths([0,1,2,3])
        l = list(w.partial_sums(start=3,mod=4))
        return P(l)[:-1]


words = WordGenerator()
