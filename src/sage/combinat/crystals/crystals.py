r"""
Crystals

Let `T` be a CartanType with index set `I`, and
`W` be a realization of the type `T` weight
lattice.

A type `T` crystal `C` is a colored oriented graph
equipped with a weight function from the nodes to some realization
of the type `T` weight lattice such that:


-  Each edge is colored with a label in `i \in I`.

-  For each `i\in I`, each node `x` has:


   -  at most one `i`-successor `f_i(x)`;

   -  at most one `i`-predecessor `e_i(x)`.


   Furthermore, when they exist,


   -  `f_i(x)`.weight() = x.weight() - `\alpha_i`;

   -  `e_i(x)`.weight() = x.weight() + `\alpha_i`.



This crystal actually models a representation of a Lie algebra if
it satisfies some further local conditions due to Stembridge, see
J. Stembridge, *A local characterization of simply-laced crystals*,
Trans. Amer. Math. Soc. 355 (2003), no. 12, 4807-4823.

EXAMPLES:

We construct the type `A_5` crystal on letters (or in
representation theoretic terms, the highest weight crystal of type
`A_5` corresponding to the highest weight
`\Lambda_1`)

::

    sage: C = CrystalOfLetters(['A',5]); C
    The crystal of letters for type ['A', 5]

It has a single highest weight element::

    sage: C.highest_weight_vectors()
    [1]

A crystal is an enumerated set (see :class:`EnumeratedSets`); and we
can count and list its elements in the usual way::

    sage: C.cardinality()
    6
    sage: C.list()
    [1, 2, 3, 4, 5, 6]

as well as use it in for loops::

    sage: [x for x in C]
    [1, 2, 3, 4, 5, 6]

Here are some more elaborate crystals (see their respective
documentations)::

    sage: Tens = TensorProductOfCrystals(C, C)
    sage: Spin = CrystalOfSpins(['B', 3])
    sage: Tab  = CrystalOfTableaux(['A', 3], shape = [2,1,1])
    sage: Fast = FastCrystal(['B', 2], shape = [3/2, 1/2])
    sage: KR = KirillovReshetikhinCrystal(['A',2,1],1,1)

One can get (currently) crude plotting via::

    sage: Tab.plot()

For rank two crystals, there is an alternative method of getting
metapost pictures. For more information see C.metapost?

Caveat: this crystal library, although relatively featureful for
classical crystals, is still in an early development stage, and the
syntax details may be subject to changes.

TODO:


-  Vocabulary and conventions:


   -  elements or vectors of a crystal?

   -  For a classical crystal: connected / highest weight /
      irreducible

   -  ...


-  More introductory doc explaining the mathematical background

-  Layout instructions for plot() for rank 2 types

-  Streamlining the latex output

-  Littelmann paths and/or alcove paths (this would give us the
   exceptional types)

-  RestrictionOfCrystal / DirectSumOfCrystals


Most of the above features (except Littelmann/alcove paths) are in
MuPAD-Combinat (see lib/COMBINAT/crystals.mu), which could provide
inspiration.
"""

#*****************************************************************************
#       Copyright (C) 2007 Anne Schilling <anne at math.ucdavis.edu>
#                          Nicolas Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#****************************************************************************
# Acknowledgment: most of the design and implementation of this
# library is heavily inspired from MuPAD-Combinat.
#****************************************************************************

from sage.misc.misc_c import prod
from sage.misc.latex import latex
from sage.misc.cachefunc import CachedFunction
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.structure.element import Element
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from sage.graphs.all import DiGraph
from sage.combinat import ranker
from sage.combinat.root_system.weyl_characters import WeylCharacter
from sage.combinat.backtrack import GenericBacktracker
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.rational_field import QQ

## MuPAD-Combinat's Cat::Crystal
# FIXME: crystals, like most parent should have unique data representation
# TODO: make into a category
class Crystal(UniqueRepresentation, Parent):
    r"""
    The abstract class of crystals

    Derived subclasses should implement the following:

    -  either a method cartan_type or an attribute _cartan_type

    -  module_generators: a list (or container) of distinct elements
       which generate the crystal using `f_i`

    """

    def _an_element_(self):
        """
        Returns an element of self

            sage: C = CrystalOfLetters(['A', 5])
            sage: C.an_element()
            1
        """
        return self.first()

    def weight_lattice_realization(self):
        """
        Returns the weight lattice realization for the root system
        associated to self. This default implementation uses the
        ambient space of the root system.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A', 5])
            sage: C.weight_lattice_realization()
            Ambient space of the Root system of type ['A', 5]
            sage: K = KirillovReshetikhinCrystal(['A',2,1], 1, 1)
            sage: K.weight_lattice_realization()
            Weight lattice of the Root system of type ['A', 2, 1]
        """
        F = self.cartan_type().root_system()
        if F.ambient_space() is None:
            return F.weight_lattice()
        else:
            return F.ambient_space()

    def cartan_type(self):
        """
        Returns the Cartan type of the associated crystal

        EXAMPLES::
            sage: C = CrystalOfLetters(['A',2])
            sage: C.cartan_type()
            ['A', 2]
        """
        return self._cartan_type

    def index_set(self):
        """
        Returns the index set of the Dynkin diagram underlying the given crystal

        EXAMPLES:
            sage: C = CrystalOfLetters(['A', 5])
            sage: C.index_set()
            [1, 2, 3, 4, 5]
        """
        return self.cartan_type().index_set()

    def Lambda(self):
        """
        Returns the fundamentals weights in the weight lattice realization
        for the root system associated to self.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A', 5])
            sage: C.Lambda()
            Finite family {1: (1, 0, 0, 0, 0, 0), 2: (1, 1, 0, 0, 0, 0), 3: (1, 1, 1, 0, 0, 0), 4: (1, 1, 1, 1, 0, 0), 5: (1, 1, 1, 1, 1, 0)}
        """
        return self.weight_lattice_realization().fundamental_weights()

    def check(self):
        r"""
        Runs sanity checks on the crystal:


        -  Checks that count, list, and __iter__ are consistent. For a
           ClassicalCrystal, this in particular checks that the number of
           elements returned by the brute force listing and the iterator
           __iter__ are consistent with the Weyl dimension formula.

        -  Should check Stembridge's rules, etc.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A', 5])
            sage: C.check()
            True
        """
        # Those tests could be lifted up to CombinatorialClass
        list1 = self.list()
        set1 = set(list1)
        list2 = [c for c in self]
        set2 = set(list2)
        list3 = Crystal.list(self)
        set3 = set(list3)
        return len(set1) == len(list1) \
               and len(set2) == len(list2) \
               and len(set3) == len(list3) \
               and len(set1) == self.cardinality() \
               and set1 == set2 \
               and set2 == set3

    def list(self):
        """
        Returns a list of the elements of self obtained by continually
        apply the `f_i` operators to the module generators of
        self.

        EXAMPLES::

            sage: from sage.combinat.crystals.crystals import Crystal
            sage: C = CrystalOfLetters(['A', 5])
            sage: l = Crystal.list(C)
            sage: l.sort(); l
            [1, 2, 3, 4, 5, 6]
        """
        # Should use transitiveIdeal
        # should be transformed to __iter__ instead of list
        # To be moved in a super category CombinatorialModule
        result = set(self.module_generators)
        todo = result.copy()
        while len(todo) > 0:
            x = todo.pop()
            for i in self.index_set():
                y = x.f(i)
                if y == None or y in result:
                    continue
                todo.add(y)
                result.add(y)
        return list(result)

    def crystal_morphism(self, g, index_set = None, automorphism = lambda i : i, direction = 'down', direction_image = 'down',
                         similarity_factor = None, similarity_factor_domain = None, cached = False, acyclic = True):
        """
        Constructs a morphism from the crystal self to another crystal.
        The input `g` can either be a function of a (sub)set of elements of self to
        element in another crystal or a dictionary between certain elements.
        Usually one would map highest weight elements or crystal generators to each
        other using g.
        Specifying index_set gives the opportunity to define the morphism as `I`-crystals
        where `I =` index_set. If index_set is not specified, the index set of self is used.
        It is also possible to define twisted-morphisms by specifying an automorphism on the
        nodes in te Dynkin diagram (or the index_set).
        The option direction and direction_image indicate whether to use `f_i` or `e_i` in
        self or the image crystal to construct the morphism, depending on whether the direction
        is set to 'down' or 'up'.
        It is also possible to set a similarity_factor. This should be a dictionary between
        the elements in the index set and positive integers. The crystal operator `f_i` then gets
        mapped to `f_i^{m_i}` where `m_i =` similarity_factor[i].
        Setting similarity_factor_domain to a dictionary between the index set and positive integers
        has the effect that `f_i^{m_i}` gets mapped to `f_i` where `m_i =` similarity_factor_domain[i].
        Finally, it is possible to set the option `acyclic = False`. This calculates an isomorphism
        for cyclic crystals (for example finite affine crystals). In this case the input function `g`
        is supposed to be given as a dictionary.

        EXAMPLES::

            sage: C2 = CrystalOfLetters(['A',2])
            sage: C3 = CrystalOfLetters(['A',3])
            sage: g = {C2.module_generators[0] : C3.module_generators[0]}
            sage: g_full = C2.crystal_morphism(g)
            sage: g_full(C2(1))
            1
            sage: g_full(C2(2))
            2
            sage: g = {C2(1) : C2(3)}
            sage: g_full = C2.crystal_morphism(g, automorphism = lambda i : 3-i, direction_image = 'up')
            sage: [g_full(b) for b in C2]
            [3, 2, 1]
            sage: T = CrystalOfTableaux(['A',2], shape = [2])
            sage: g = {C2(1) : T(rows=[[1,1]])}
            sage: g_full = C2.crystal_morphism(g, similarity_factor = {1:2, 2:2})
            sage: [g_full(b) for b in C2]
            [[[1, 1]], [[2, 2]], [[3, 3]]]
            sage: g = {T(rows=[[1,1]]) : C2(1)}
            sage: g_full = T.crystal_morphism(g, similarity_factor_domain = {1:2, 2:2})
            sage: g_full(T(rows=[[2,2]]))
            2

            sage: B1=KirillovReshetikhinCrystal(['A',2,1],1,1)
            sage: B2=KirillovReshetikhinCrystal(['A',2,1],1,2)
            sage: T=TensorProductOfCrystals(B1,B2)
            sage: T1=TensorProductOfCrystals(B2,B1)
            sage: La = T.weight_lattice_realization().fundamental_weights()
            sage: t = [b for b in T if b.weight() == -3*La[0] + 3*La[1]][0]
            sage: t1 = [b for b in T1 if b.weight() == -3*La[0] + 3*La[1]][0]
            sage: g={t:t1}
            sage: f=T.crystal_morphism(g,acyclic = False)
            sage: [[b,f(b)] for b in T]
            [[[[[1]], [[1, 1]]], [[[1, 1]], [[1]]]],
            [[[[1]], [[1, 2]]], [[[1, 1]], [[2]]]],
            [[[[1]], [[2, 2]]], [[[1, 2]], [[2]]]],
            [[[[1]], [[1, 3]]], [[[1, 1]], [[3]]]],
            [[[[1]], [[2, 3]]], [[[1, 2]], [[3]]]],
            [[[[1]], [[3, 3]]], [[[1, 3]], [[3]]]],
            [[[[2]], [[1, 1]]], [[[1, 2]], [[1]]]],
            [[[[2]], [[1, 2]]], [[[2, 2]], [[1]]]],
            [[[[2]], [[2, 2]]], [[[2, 2]], [[2]]]],
            [[[[2]], [[1, 3]]], [[[2, 3]], [[1]]]],
            [[[[2]], [[2, 3]]], [[[2, 2]], [[3]]]],
            [[[[2]], [[3, 3]]], [[[2, 3]], [[3]]]],
            [[[[3]], [[1, 1]]], [[[1, 3]], [[1]]]],
            [[[[3]], [[1, 2]]], [[[1, 3]], [[2]]]],
            [[[[3]], [[2, 2]]], [[[2, 3]], [[2]]]],
            [[[[3]], [[1, 3]]], [[[3, 3]], [[1]]]],
            [[[[3]], [[2, 3]]], [[[3, 3]], [[2]]]],
            [[[[3]], [[3, 3]]], [[[3, 3]], [[3]]]]]
        """
        if index_set is None:
            index_set = self.index_set()
        if similarity_factor is None:
            similarity_factor = dict( (i,1) for i in index_set )
        if similarity_factor_domain is None:
            similarity_factor_domain = dict( (i,1) for i in index_set )
        if direction == 'down':
            e_string = 'e_string'
        else:
            e_string = 'f_string'
        if direction_image == 'down':
            f_string = 'f_string'
        else:
            f_string = 'e_string'

        if acyclic:
            if type(g) == dict:
                g = g.__getitem__

            def morphism(b):
                for i in index_set:
                    c = getattr(b, e_string)([i for k in range(similarity_factor_domain[i])])
                    if c is not None:
                        d = getattr(morphism(c), f_string)([automorphism(i) for k in range(similarity_factor[i])])
                        if d is not None:
                            return d
                        else:
                            raise ValueError, "This is not a morphism!"
                        #now we know that b is hw
                return g(b)

        else:
            import copy
            morphism = copy.copy(g)
            known = set( g.keys() )
            todo = copy.copy(known)
            images = set( [g[x] for x in known] )
            # Invariants:
            # - images contains all known morphism(x)
            # - known contains all elements x for which we know morphism(x)
            # - todo  contains all elements x for which we haven't propagated to each child
            while todo <> set( [] ):
                x = todo.pop()
                for i in index_set:
                    eix  = getattr(x, f_string)([i for k in range(similarity_factor_domain[i])])
                    eigx = getattr(morphism[x], f_string)([automorphism(i) for k in range(similarity_factor[i])])
                    if bool(eix is None) <> bool(eigx is None):
                        # This is not a crystal morphism!
                        raise ValueError, "This is not a morphism!" #, print("x="x,"g(x)="g(x),"i="i)
                    if (eix is not None) and (eix not in known):
                        todo.add(eix)
                        known.add(eix)
                        morphism[eix] = eigx
                        images.add(eigx)
            # Check that the module generators are indeed module generators
            assert(len(known) == self.cardinality())
            # We may not want to systematically run those tests,
            # to allow for non bijective crystal morphism
            # Add an option CheckBijective?
            if not ( len(known) == len(images) and len(images) == images.pop().parent().cardinality() ):
                return(None)
            return morphism.__getitem__

        if cached:
            return morphism
        else:
            return CachedFunction(morphism)

    def demazure_character(self, weight, reduced_word = False):
        r"""
        Calculates the Demazure character associated to the specified weight in the
        ambient weight lattice.

        INPUT:
            - weight in the weight lattice realization of the crystal (default input)
            - when the option reduced_word is set to True, a reduced word can be inputted

        This is currently only supported for crystals whose underlying weight space is
        the ambient space.

        References:

        M. Demazure, "Desingularisation des varietes de Schubert",
        Ann. E. N. S., Vol. 6, (1974), p. 163-172

        Sarah Mason, "An Explicit Construction of Type A Demazure Atoms",
        Journal of Algebraic Combinatorics, Vol. 29, (2009), No. 3, p.295-313
        (arXiv:0707.4267)

        EXAMPLES::

            sage: T = CrystalOfTableaux(['A',2], shape = [2,1])
            sage: e = T.weight_lattice_realization().basis()
            sage: weight = e[0] + 2*e[2]
            sage: weight.reduced_word()
            [2, 1]
            sage: T.demazure_character(weight)
            x1^2*x2 + x1^2*x3 + x1*x2^2 + x1*x2*x3 + x1*x3^2

            sage: T = CrystalOfTableaux(['A',3],shape=[2,1])
            sage: T.demazure_character([1,2,3], reduced_word = True)
            x1^2*x2 + x1^2*x3 + x1*x2^2 + x1*x2*x3 + x2^2*x3

            sage: T = CrystalOfTableaux(['B',2], shape = [2])
            sage: e = T.weight_lattice_realization().basis()
            sage: weight = -2*e[1]
            sage: T.demazure_character(weight)
            x1^2 + x1*x2 + x2^2 + x1 + x2 + x1/x2 + 1/x2 + 1/x2^2 + 1
        """
        if reduced_word:
            word = weight
        else:
            word = weight.reduced_word()
        n = self.weight_lattice_realization().n
        u = list( self.module_generators )
        for i in reversed(word):
            u = u + sum((x.demazure_operator(i, truncated = True) for x in u), [])
        x = ['x%s'%i for i in range(1,n+1)]
        P = PolynomialRing(QQ, x)
        u = [b.weight() for b in u]
        return sum((prod((x[i]**(la[i]) for i in range(n)), P.one()) for la in u), P.zero())

    def digraph(self):
        """
        Returns the DiGraph associated to self.

        EXAMPLES::

            sage: from sage.combinat.crystals.crystals import Crystal
            sage: C = CrystalOfLetters(['A', 5])
            sage: Crystal.digraph(C)
            Digraph on 6 vertices
        """
        d = {}
        for x in self:
            d[x] = {}
            for i in self.index_set():
                child = x.f(i)
                if child is None:
                    continue
                d[x][child]=i
        return DiGraph(d)

    def character(self, R):
        """
        INPUT: R, a WeylCharacterRing. Produces the character of the
        crystal.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',2])
            sage: T = TensorProductOfCrystals(C, C)
            sage: A2 = WeylCharacterRing(C.cartan_type()); A2
            The Weyl Character Ring of Type ['A', 2] with Integer Ring coefficients
            sage: chi = T.character(A2); chi
            A2(1,1,0) + A2(2,0,0)
            sage: chi.check(verbose = true)
            [9, 9]
        """
        if not R.cartan_type() == self.cartan_type():
            raise ValueError, "ring does not have the right Cartan type"
        hlist = {}
        mlist = {}

        for x in self.highest_weight_vectors():
            k = x.weight()
            if k in hlist:
                hlist[k] += 1
            else:
                hlist[k] = 1
        for x in self.list():
            k = x.weight()
            if k in mlist:
                mlist[k] += 1
            else:
                mlist[k] = 1
        return WeylCharacter(R, hlist, mlist)

    def latex_file(self, filename):
        r"""
        Exports a file, suitable for pdflatex, to 'filename'. This requires
        a proper installation of dot2tex in sage-python. For more
        information see the documentation for self.latex().

        EXAMPLES::

            sage: C = CrystalOfLetters(['A', 5])
            sage: C.latex_file('/tmp/test.tex') #optional requires dot2tex
        """
        header = r"""\documentclass{article}
        \usepackage[x11names, rgb]{xcolor}
        \usepackage[utf8]{inputenc}
        \usepackage{tikz}
        \usetikzlibrary{snakes,arrows,shapes}
        \usepackage{amsmath}
        \usepackage[active,tightpage]{preview}
        \newenvironment{bla}{}{}
        \PreviewEnvironment{bla}

        \begin{document}
        \begin{bla}"""

        footer = r"""\end{bla}
        \end{document}"""

        f = open(filename, 'w')
        f.write(header + self.latex() + footer)
        f.close()

    def latex(self):
        r"""
        Returns the crystal graph as a bit of latex. This can be exported
        to a file with self.latex_file('filename').

        This requires the dot2tex spkg. Here some tips for installation:

        -  Install graphviz = 2.14

        -  Download dot2tex-0.?.spkg from http://wiki.sagemath.org/combinat/FPSAC09/projects

        -  Install pgf-2.00 inside your latex tree. In short:

           -  untaring in /usr/share/texmf/tex/generic

           -  clean out remaining pgf files from older version

           -  run texhash


        In case LaTeX complains about tikzpicture not being defined,
        you may need to further run::

           sage: sage.misc.latex.LATEX_HEADER+=r"\\usepackage{tikz}"


        EXAMPLES::

            sage: C = CrystalOfLetters(['A', 5])
            sage: C.latex()         #optional requires dot2tex
            ...
            sage: view(C, pdflatex = True, tightpage = True) # optional
        """

        try:
            from dot2tex.dot2tex import Dot2TikZConv
        except ImportError:
            print "dot2tex not available.  Install after running \'sage -sh\'"
            return

        # In MuPAD, 'autosize' is an option, but this doesn't seem to work here.
        options = {'format':'tikz', 'crop':True, 'usepdflatex':True, 'figonly':True}

        content = (Dot2TikZConv(options)).convert(self.dot_tex())

        return content

    _latex_ = latex

    def metapost(self, filename, thicklines=False, labels=True, scaling_factor=1.0, tallness=1.0):
        """Use C.metapost("filename.mp",[options])
        where options can be:

        thicklines = True (for thicker edges) labels = False (to suppress
        labeling of the vertices) scaling_factor=value, where value is a
        floating point number, 1.0 by default. Increasing or decreasing the
        scaling factor changes the size of the image. tallness=1.0.
        Increasing makes the image taller without increasing the width.

        Root operators e(1) or f(1) move along red lines, e(2) or f(2)
        along green. The highest weight is in the lower left. Vertices with
        the same weight are kept close together. The concise labels on the
        nodes are strings introduced by Berenstein and Zelevinsky and
        Littelmann; see Littelmann's paper Cones, Crystals, Patterns,
        sections 5 and 6.

        For Cartan types B2 or C2, the pattern has the form

        a2 a3 a4 a1

        where c\*a2 = a3 = 2\*a4 =0 and a1=0, with c=2 for B2, c=1 for C2.
        Applying e(2) a1 times, e(1) a2 times, e(2) a3 times, e(1) a4 times
        returns to the highest weight. (Observe that Littelmann writes the
        roots in opposite of the usual order, so our e(1) is his e(2) for
        these Cartan types.) For type A2, the pattern has the form

        a3 a2 a1

        where applying e(1) a1 times, e(2) a2 times then e(3) a1 times
        returns to the highest weight. These data determine the vertex and
        may be translated into a Gelfand-Tsetlin pattern or tableau.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A', 2])
            sage: C.metapost('/tmp/test.mp') #optional

        ::

            sage: C = CrystalOfLetters(['A', 5])
            sage: C.metapost('/tmp/test.mp')
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        # FIXME: those tests are not robust
        # Should use instead self.cartan_type() == CartanType(['B',2])
        if self.cartan_type()[0] == 'B' and self.cartan_type()[1] == 2:
            word = [2,1,2,1]
        elif self.cartan_type()[0] == 'C' and self.cartan_type()[1] == 2:
            word = [2,1,2,1]
        elif self.cartan_type()[0] == 'A' and self.cartan_type()[1] == 2:
            word = [1,2,1]
        else:
            raise NotImplementedError
        size = self.cardinality()
        string_data = []
        for i in range(size):
            turtle = self.list()[i]
            string_datum = []
            for j in word:
                turtlewalk = 0
                while not turtle.e(j) == None:
                    turtle = turtle.e(j)
                    turtlewalk += 1
                string_datum.append(turtlewalk)
            string_data.append(string_datum)

        if self.cartan_type()[0] == 'A':
            if labels:
                c0 = int(55*scaling_factor)
                c1 = int(-25*scaling_factor)
                c2 = int(45*tallness*scaling_factor)
                c3 = int(-12*scaling_factor)
                c4 = int(-12*scaling_factor)
            else:
                c0 = int(45*scaling_factor)
                c1 = int(-20*scaling_factor)
                c2 = int(35*tallness*scaling_factor)
                c3 = int(12*scaling_factor)
                c4 = int(-12*scaling_factor)
            outstring = "verbatimtex\n\\magnification=600\netex\n\nbeginfig(-1);\nsx:=35; sy:=30;\n\nz1000=(%d,0);\nz1001=(%d,%d);\nz1002=(%d,%d);\nz2001=(-3,3);\nz2002=(3,3);\nz2003=(0,-3);\nz2004=(7,0);\nz2005=(0,7);\nz2006=(-7,0);\nz2007=(0,7);\n\n"%(c0,c1,c2,c3,c4)
        else:
            if labels:
                outstring = "verbatimtex\n\\magnification=600\netex\n\nbeginfig(-1);\n\nsx := %d;\nsy=%d;\n\nz1000=(2*sx,0);\nz1001=(-sx,sy);\nz1002=(-16,-10);\n\nz2001=(0,-3);\nz2002=(-5,3);\nz2003=(0,3);\nz2004=(5,3);\nz2005=(10,1);\nz2006=(0,10);\nz2007=(-10,1);\nz2008=(0,-8);\n\n"%(int(scaling_factor*40),int(tallness*scaling_factor*40))
            else:
                outstring = "beginfig(-1);\n\nsx := %d;\nsy := %d;\n\nz1000=(2*sx,0);\nz1001=(-sx,sy);\nz1002=(-5,-5);\n\nz1003=(10,10);\n\n"%(int(scaling_factor*35),int(tallness*scaling_factor*35))
        for i in range(size):
            if self.cartan_type()[0] == 'A':
                [a1,a2,a3] = string_data[i]
            else:
                [a1,a2,a3,a4] = string_data[i]
            shift = 0
            for j in range(i):
                if self.cartan_type()[0] == 'A':
                    [b1,b2,b3] = string_data[j]
                    if b1+b3 == a1+a3 and b2 == a2:
                        shift += 1
                else:
                    [b1,b2,b3,b4] = string_data[j]
                    if b1+b3 == a1+a3 and b2+b4 == a2+a4:
                        shift += 1
            if self.cartan_type()[0] == 'A':
                outstring = outstring +"z%d=%d*z1000+%d*z1001+%d*z1002;\n"%(i,a1+a3,a2,shift)
            else:
                outstring = outstring +"z%d=%d*z1000+%d*z1001+%d*z1002;\n"%(i,a1+a3,a2+a4,shift)
        outstring = outstring + "\n"
        if thicklines:
            outstring = outstring +"pickup pencircle scaled 2\n\n"
        for i in range(size):
            for j in range(1,3):
                dest = self.list()[i].f(j)
                if not dest == None:
                    dest = self.list().index(dest)
                    if j == 1:
                        col = "red;"
                    else:
                        col = "green;  "
                    if self.cartan_type()[0] == 'A':
                        [a1,a2,a3] = string_data[i] # included to facilitate hand editing of the .mp file
                        outstring = outstring+"draw z%d--z%d withcolor %s   %% %d %d %d\n"%(i,dest,col,a1,a2,a3)
                    else:
                        [a1,a2,a3,a4] = string_data[i]
                        outstring = outstring+"draw z%d--z%d withcolor %s   %% %d %d %d %d\n"%(i,dest,col,a1,a2,a3,a4)
        outstring += "\npickup pencircle scaled 3;\n\n"
        for i in range(self.cardinality()):
            if labels:
                if self.cartan_type()[0] == 'A':
                    outstring = outstring+"pickup pencircle scaled 15;\nfill z%d+z2004..z%d+z2006..z%d+z2006..z%d+z2007..cycle withcolor white;\nlabel(btex %d etex, z%d+z2001);\nlabel(btex %d etex, z%d+z2002);\nlabel(btex %d etex, z%d+z2003);\npickup pencircle scaled .5;\ndraw z%d+z2004..z%d+z2006..z%d+z2006..z%d+z2007..cycle;\n"%(i,i,i,i,string_data[i][2],i,string_data[i][1],i,string_data[i][0],i,i,i,i,i)
                else:
                    outstring = outstring+"%%%d %d %d %d\npickup pencircle scaled 1;\nfill z%d+z2005..z%d+z2006..z%d+z2007..z%d+z2008..cycle withcolor white;\nlabel(btex %d etex, z%d+z2001);\nlabel(btex %d etex, z%d+z2002);\nlabel(btex %d etex, z%d+z2003);\nlabel(btex %d etex, z%d+z2004);\npickup pencircle scaled .5;\ndraw z%d+z2005..z%d+z2006..z%d+z2007..z%d+z2008..cycle;\n\n"%(string_data[i][0],string_data[i][1],string_data[i][2],string_data[i][3],i,i,i,i,string_data[i][0],i,string_data[i][1],i,string_data[i][2],i,string_data[i][3],i,i,i,i,i)
            else:
                outstring += "drawdot z%d;\n"%i
        outstring += "\nendfig;\n\nend;\n\n"

        f = open(filename, 'w')
        f.write(outstring)
        f.close()

    def dot_tex(self):
        r"""
        Returns a dot_tex version of self.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',2])
            sage: C.dot_tex()
            'digraph G { \n  node [ shape=plaintext ];\n  N_0 [ label = " ", texlbl = "$1$" ];\n  N_1 [ label = " ", texlbl = "$2$" ];\n  N_2 [ label = " ", texlbl = "$3$" ];\n  N_0 -> N_1 [ label = " ", texlbl = "1" ];\n  N_1 -> N_2 [ label = " ", texlbl = "2" ];\n}'
        """
        import re
        rank = ranker.from_list(self.list())[0]
        vertex_key = lambda x: "N_"+str(rank(x))

        # To do: check the regular expression
        # Removing %-style comments, newlines, quotes
        # This should probably be moved to sage.misc.latex
        quoted_latex = lambda x: re.sub("\"|\r|(%[^\n]*)?\n","", latex(x))

        result = "digraph G { \n  node [ shape=plaintext ];\n"

        for x in self:
            result += "  " + vertex_key(x) + " [ label = \" \", texlbl = \"$"+quoted_latex(x)+"$\" ];\n"
        for x in self:
            for i in self.index_set():
                child = x.f(i)
                if child is None:
                    continue
#                result += "  " + vertex_key(x) + " -> "+vertex_key(child)+ " [ label = \" \", texlbl = \""+quoted_latex(i)+"\" ];\n"
                if i == 0:
                    option = "dir = back, "
                    (source, target) = (child, x)
                else:
                    option = ""
                    (source, target) = (x, child)
                result += "  " + vertex_key(source) + " -> "+vertex_key(target)+ " [ "+option+"label = \" \", texlbl = \""+quoted_latex(i)+"\" ];\n"
        result+="}"
        return result

    def plot(self, **options):
        """
        Returns the plot of self as a directed graph.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A', 5])
            sage: show_default(False) #do not show the plot by default
            sage: C.plot()
            Graphics object consisting of 17 graphics primitives
        """
        return self.digraph().plot(edge_labels=True,vertex_size=0,**options)

class CrystalElement(Element):
    r"""
    The abstract class of crystal elements

    Sub classes should implement at least:

    -  x.e(i) (returning `e_i(x)`)

    -  x.f(i) (returning `f_i(x)`)

    -  x.weight()
    """

    def index_set(self):
        """
        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C(1).index_set()
            [1, 2, 3, 4, 5]
        """
        return self.parent().index_set()

    def cartan_type(self):
        """
        Returns the cartan type associated to self

        EXAMPLES::
            sage: C = CrystalOfLetters(['A', 5])
            sage: C(1).cartan_type()
            ['A', 5]
        """
        return self.parent().cartan_type()

    def weight(self):
        """
        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C(1).weight()
            (1, 0, 0, 0, 0, 0)
        """
        return self.Phi() - self.Epsilon()

    def e(self, i):
        r"""
        Returns `e_i(x)` if it exists or None otherwise. This is
        to be implemented by subclasses of CrystalElement.

        TESTS::

            sage: from sage.combinat.crystals.crystals import CrystalElement
            sage: C = CrystalOfLetters(['A',5])
            sage: CrystalElement.e(C(1), 1)
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def f(self, i):
        r"""
        Returns `f_i(x)` if it exists or None otherwise. This is
        to be implemented by subclasses of CrystalElement.

        TESTS::

            sage: from sage.combinat.crystals.crystals import CrystalElement
            sage: C = CrystalOfLetters(['A',5])
            sage: CrystalElement.f(C(1), 1)
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def epsilon(self, i):
        r"""
        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C(1).epsilon(1)
            0
            sage: C(2).epsilon(1)
            1
        """
        assert i in self.index_set()
        x = self
        eps = 0
        while True:
            x = x.e(i)
            if x is None:
                break
            eps = eps+1
        return eps

    def phi(self, i):
        r"""
        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C(1).phi(1)
            1
            sage: C(2).phi(1)
            0
        """
        assert i in self.index_set()
        x = self
        phi = 0
        while True:
            x = x.f(i)
            if x is None:
                break
            phi = phi+1
        return phi

    def phi_minus_epsilon(self, i):
        """
        Returns `\phi_i - \epsilon_i` of self. There are sometimes
        better implementations using the weight for this. It is used
        for reflections along a string.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C(1).phi_minus_epsilon(1)
            1
        """
        return self.phi(i) - self.epsilon(i)

    def Epsilon(self):
        """
        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C(0).Epsilon()
            (0, 0, 0, 0, 0, 0)
            sage: C(1).Epsilon()
            (0, 0, 0, 0, 0, 0)
            sage: C(2).Epsilon()
            (1, 0, 0, 0, 0, 0)
        """
        Lambda = self.parent().Lambda()
        return sum(self.epsilon(i) * Lambda[i] for i in self.index_set())

    def Phi(self):
        """
        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C(0).Phi()
            (0, 0, 0, 0, 0, 0)
            sage: C(1).Phi()
            (1, 0, 0, 0, 0, 0)
            sage: C(2).Phi()
            (1, 1, 0, 0, 0, 0)
        """
        Lambda = self.parent().Lambda()
        return sum(self.phi(i) * Lambda[i] for i in self.index_set())

    def f_string(self, list):
        r"""
        Applies `f_{i_r} ... f_{i_1}` to self for `list = [i_1, ..., i_r]`

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',3])
            sage: b = C(1)
            sage: b.f_string([1,2])
            3
            sage: b.f_string([2,1])

        """
        b = self
        for i in list:
            b = b.f(i)
            if b is None:
                return None
        return b

    def e_string(self, list):
        r"""
        Applies `e_{i_r} ... e_{i_1}` to self for `list = [i_1, ..., i_r]`

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',3])
            sage: b = C(3)
            sage: b.e_string([2,1])
            1
            sage: b.e_string([1,2])

        """
        b = self
        for i in list:
            b = b.e(i)
            if b is None:
                return None
        return b

    def s(self, i):
        r"""
        Returns the reflection of self along its `i`-string

        EXAMPLES::

            sage: C = CrystalOfTableaux(['A',2], shape=[2,1])
            sage: b=C(rows=[[1,1],[3]])
            sage: b.s(1)
            [[2, 2], [3]]
            sage: b=C(rows=[[1,2],[3]])
            sage: b.s(2)
            [[1, 2], [3]]
            sage: T=CrystalOfTableaux(['A',2],shape=[4])
            sage: t=T(rows=[[1,2,2,2]])
            sage: t.s(1)
            [[1, 1, 1, 2]]
        """
        d = self.phi_minus_epsilon(i)
        b = self
        if d > 0:
            for j in range(d):
                b = b.f(i)
        else:
            for j in range(-d):
                b = b.e(i)
        return b

    def demazure_operator(self, i, truncated = False):
        r"""
        Yields all elements one can obtain from self by application of `f_i`.
        If the option "truncated" is set to True, then `self` is not included in the list.

        References:

        Peter Littelmann, "Crystal graphs and Young tableaux",
        J. Algebra 175 (1995), no. 1, 65--87.

        Masaki Kashiwara, "The crystal base and Littelmann's refined Demazure character formula",
        Duke Math. J. 71 (1993), no. 3, 839--858.

        EXAMPLES::

            sage: T = CrystalOfTableaux(['A',2], shape=[2,1])
            sage: t=T(rows=[[1,2],[2]])
            sage: t.demazure_operator(2)
            [[[1, 2], [2]], [[1, 3], [2]], [[1, 3], [3]]]
            sage: t.demazure_operator(2, truncated = True)
            [[[1, 3], [2]], [[1, 3], [3]]]
            sage: t.demazure_operator(1, truncated = True)
            []
            sage: t.demazure_operator(1)
            [[[1, 2], [2]]]

            sage: K = KirillovReshetikhinCrystal(['A',2,1],2,1)
            sage: t = K(rows=[[3],[2]])
            sage: t.demazure_operator(0)
            [[[2, 3]], [[1, 2]]]
        """
        if truncated:
            l = []
        else:
            l = [self]
        for k in range(self.phi(i)):
            l.append(self.f_string([i for j in range(k+1)]))
        return(l)

    def is_highest_weight(self, index_set = None):
        r"""
        Returns True if self is a highest weight.
        Specifying the option index_set to be a subset `I` of the index set
        of the underlying crystal, finds all highest weight vectors for arrows in `I`.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C(1).is_highest_weight()
            True
            sage: C(2).is_highest_weight()
            False
            sage: C(2).is_highest_weight(index_set = [2,3,4,5])
            True
        """
        if index_set is None:
            index_set = self.index_set()
        return all(self.e(i) is None for i in index_set)

    def to_highest_weight(self, list = [], index_set = None):
        r"""
        Yields the highest weight element `u` and list `[i_1,...,i_k]`
        such that `self = f_{i_1} ... f_{i_k} u`, where `i_1,...,i_k` are
        elements in `index_set`. By default the index set is assumed to be
        the full index set of self.

        EXAMPLES::

            sage: T = CrystalOfTableaux(['A',3], shape = [1])
            sage: t = T(rows = [[3]])
            sage: t.to_highest_weight()
            [[[1]], [2, 1]]
            sage: t.to_highest_weight()
            [[[1]], [2, 1]]
            sage: T = CrystalOfTableaux(['A',3], shape = [2,1])
            sage: t = T(rows = [[1,2],[4]])
            sage: t.to_highest_weight()
            [[[1, 1], [2]], [1, 3, 2]]
            sage: t.to_highest_weight(index_set = [3])
            [[[1, 2], [3]], [3]]
        """
        #should assert that self.parent() restricted to index_set is a highest weight crystal
        if index_set is None:
            index_set = self.index_set()
        for i in index_set:
            if self.epsilon(i) <> 0:
                self = self.e(i)
                return self.to_highest_weight(list = list + [i], index_set = index_set)
        return [self, list]


class CrystalBacktracker(GenericBacktracker):
    def __init__(self, crystal):
        """
        Time complexity: `O(nf)` amortized for each produced
        element, where `n` is the size of the index set, and f is
        the cost of computing `e` and `f` operators.

        Memory complexity: O(depth of the crystal)

        Principle of the algorithm:

        Let C be a classical crystal. It's an acyclic graph where all
        connected component has a unique element without predecessors (the
        highest weight element for this component). Let's assume for
        simplicity that C is irreducible (i.e. connected) with highest
        weight element u.

        One can define a natural spanning tree of `C` by taking
        `u` as rot of the tree, and for any other element
        `y` taking as ancestor the element `x` such that
        there is an `i`-arrow from `x` to `y` with
        `i` minimal. Then, a path from `u` to `y`
        describes the lexicographically smallest sequence
        `i_1,\dots,i_k` such that
        `(f_{i_k} \circ f_{i_1})(u)=y`.

        Morally, the iterator implemented below just does a depth first
        search walk through this spanning tree. In practice, this can be
        achieved recursively as follow: take an element `x`, and
        consider in turn each successor `y = f_i(x)`, ignoring
        those such that `y = f_j(x')` for some `x'` and
        `j<i` (this can be tested by computing `e_j(y)`
        for `j<i`).

        EXAMPLES::

            sage: from sage.combinat.crystals.crystals import CrystalBacktracker
            sage: C = CrystalOfTableaux(['B',3],shape=[3,2,1])
            sage: CB = CrystalBacktracker(C)
            sage: len(list(CB))
            1617
        """
        GenericBacktracker.__init__(self, None, None)
        self._crystal = crystal

    def _rec(self, x, state):
        """
        Returns an iterator for the (immediate) children of x in the search
        tree.

        EXAMPLES::

            sage: from sage.combinat.crystals.crystals import CrystalBacktracker
            sage: C = CrystalOfLetters(['A', 5])
            sage: CB = CrystalBacktracker(C)
            sage: list(CB._rec(C(1), 'n/a'))
            [(2, 'n/a', True)]
        """
        #We will signal the initial case by having a object and state
        #of None and consider it separately.
        if x is None and state is None:
            for gen in self._crystal.highest_weight_vectors():
                yield gen, "n/a", True
            return

        # Run through the children y of x
        for i in self._crystal.index_set():
            y = x.f(i)
            if y is None:
                continue
            # Ignore those which can be reached by an arrow with smaller label
            hasParent = False
            for j in x.index_set():
                if j == i:
                    break
                if not y.e(j) is None:
                    hasParent = True
                    break
            if hasParent:
                continue

            # yield y and all elements further below
            yield y, "n/a", True



class ClassicalCrystal(Crystal):
    r"""
    The abstract class of classical crystals
    """

    def list(self):
        r"""
        Returns the list of the elements of ``self``, as per
        :meth:`FiniteEnumeratedSets.ParentMethods.list`

        EXAMPLES::

            sage: C = CrystalOfLetters(['D',4])
            sage: C.list()
            [1, 2, 3, 4, -4, -3, -2, -1]

        FIXME: this is just there to reinstate the default
        implementation of list which is overriden in
        :class:`Crystals`.
        """
        return self._list_from_iterator()

    def __iter__(self):
        r"""
        Returns an iterator over the elements of the crystal.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: [x for x in C]
            [1, 2, 3, 4, 5, 6]

        TESTS::

            sage: C = CrystalOfLetters(['D',4])
            sage: D = CrystalOfSpinsPlus(['D',4])
            sage: E = CrystalOfSpinsMinus(['D',4])
            sage: T=TensorProductOfCrystals(D,E,generators=[[D.list()[0],E.list()[0]]])
            sage: U=TensorProductOfCrystals(C,E,generators=[[C(1),E.list()[0]]])
            sage: T.cardinality()
            56
            sage: T.check()
            True
            sage: U.check()
            True

        Bump's systematic tests::

            sage: fa3 = lambda a,b,c: CrystalOfTableaux(['A',3],shape=[a+b+c,b+c,c])
            sage: fb3 = lambda a,b,c: CrystalOfTableaux(['B',3],shape=[a+b+c,b+c,c])
            sage: fc3 = lambda a,b,c: CrystalOfTableaux(['C',3],shape=[a+b+c,b+c,c])
            sage: fb4 = lambda a,b,c,d: CrystalOfTableaux(['B',4],shape=[a+b+c+d,b+c+d,c+d,d])
            sage: fd4 = lambda a,b,c,d: CrystalOfTableaux(['D',4],shape=[a+b+c+d,b+c+d,c+d,d])
            sage: fd5 = lambda a,b,c,d,e: CrystalOfTableaux(['D',5],shape=[a+b+c+d+e,b+c+d+e,c+d+e,d+e,e])
            sage: def fd4spinplus(a,b,c,d):\
                 C = CrystalOfTableaux(['D',4],shape=[a+b+c+d,b+c+d,c+d,d]);\
                 D = CrystalOfSpinsPlus(['D',4]);\
                 return TensorProductOfCrystals(C,D,generators=[[C[0],D[0]]])
            sage: def fb3spin(a,b,c):\
                 C = CrystalOfTableaux(['B',3],shape=[a+b+c,b+c,c]);\
                 D = CrystalOfSpins(['B',3]);\
                 return TensorProductOfCrystals(C,D,generators=[[C[0],D[0]]])

        TODO: choose a good panel of values for a,b,c ... both for basic
        systematic tests and for conditionally run more computationally
        involved tests

        ::

            sage: fb4(1,0,1,0).check()
            True

        ::

            #sage: fb4(1,1,1,1).check() # expensive: the crystal is of size 297297
            #True
        """
        return iter(CrystalBacktracker(self))

    def _test_fast_iter(self, **options):
        r"""
        For classical crystals, tests whether the elements of list(self) and Crystal.list(self) are
        the same (the two algorithms are different).

        EXAMPLES::

            sage: C = CrystalOfLetters(['A', 5])
            sage: C._test_fast_iter()

        """
        tester = self._tester(**options)
        tester.assert_( list(self).sort() == Crystal.list(self).sort() )

    def highest_weight_vectors(self):
        r"""
        Returns a list of the highest weight vectors of self.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C.highest_weight_vectors()
            [1]

        ::

            sage: C = CrystalOfLetters(['A',2])
            sage: T = TensorProductOfCrystals(C,C,C,generators=[[C(2),C(1),C(1)],[C(1),C(2),C(1)]])
            sage: T.highest_weight_vectors()
            [[2, 1, 1], [1, 2, 1]]
        """
        # Implementation: selects among the module generators those that are
        # highest weight and cache the result
        try:
            return self._highest_weight_vectors
        except AttributeError:
            pass

        self._highest_weight_vectors = [g for g in self.module_generators if g.is_highest_weight()]
        return self._highest_weight_vectors

    def highest_weight_vector(self):
        r"""
        Returns the highest weight vector if there is a single one;
        otherwise, raises an error.

        EXAMPLES::

            sage: C = CrystalOfLetters(['A',5])
            sage: C.highest_weight_vector()
            1
        """
        hw = self.highest_weight_vectors();
        if len(hw) == 1:
            return hw[0]
        else:
            raise RuntimeError("The crystal does not have exactly one highest weight vector")

    def cardinality(self):
        r"""
        Returns the number of elements of the crystal, using Weyl's
        dimension formula on each connected component

        EXAMPLES::

            sage: from sage.combinat.crystals.crystals import ClassicalCrystal
            sage: C = CrystalOfLetters(['A', 5])
            sage: ClassicalCrystal.cardinality(C)
            6
        """
        return sum(self.weight_lattice_realization().weyl_dimension(x.weight())
                   for x in self.highest_weight_vectors())
