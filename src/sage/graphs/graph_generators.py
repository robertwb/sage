# -*- coding: utf-8 -*-

r"""
Common graphs

Usage
=====

To see a list of all graph constructors, type "graphs." and then
press the tab key. The documentation for each constructor includes
information about each graph, which provides a useful reference.


Plotting
========

All graphs (i.e., networks) have an associated Sage
graphics object, which you can display::

    sage: G = graphs.WheelGraph(15)
    sage: P = G.plot()
    sage: P.show() # long time

If you create a graph in Sage using the ``Graph``
command, then plot that graph, the positioning of nodes is
determined using the spring-layout algorithm. For the special graph
constructors, which you get using ``graphs.[tab]``, the
positions are preset. For example, consider the Petersen graph with
default node positioning vs. the Petersen graph constructed by this
database::

    sage: petersen_spring = Graph({0:[1,4,5], 1:[0,2,6], 2:[1,3,7], 3:[2,4,8], 4:[0,3,9], 5:[0,7,8], 6:[1,8,9], 7:[2,5,9], 8:[3,5,6], 9:[4,6,7]})
    sage: petersen_spring.show() # long time
    sage: petersen_database = graphs.PetersenGraph()
    sage: petersen_database.show() # long time

For all the constructors in this database (except the octahedral,
dodecahedral, random and empty graphs), the position dictionary is
filled in, instead of using the spring-layout algorithm.

For further visual examples and explanation, see the docstrings
below, particularly for
:meth:`CycleGraph <GraphGenerators.CycleGraph>`,
:meth:`StarGraph <GraphGenerators.StarGraph>`,
:meth:`WheelGraph <GraphGenerators.WheelGraph>`,
:meth:`CompleteGraph <GraphGenerators.CompleteGraph>`, and
:meth:`CompleteBipartiteGraph <GraphGenerators.CompleteBipartiteGraph>`.

.. _organization:

Organization
============

The constructors available in this database are
organized as follows.

Basic structures
----------------

- :meth:`BarbellGraph <GraphGenerators.BarbellGraph>`
- :meth:`BuckyBall <GraphGenerators.BuckyBall>`
- :meth:`BullGraph <GraphGenerators.BullGraph>`
- :meth:`ButterflyGraph <GraphGenerators.ButterflyGraph>`
- :meth:`CircularLadderGraph <GraphGenerators.CircularLadderGraph>`
- :meth:`ClawGraph <GraphGenerators.ClawGraph>`
- :meth:`CycleGraph <GraphGenerators.CycleGraph>`
- :meth:`DiamondGraph <GraphGenerators.DiamondGraph>`
- :meth:`EmptyGraph <GraphGenerators.EmptyGraph>`
- :meth:`Grid2dGraph <GraphGenerators.Grid2dGraph>`
- :meth:`GridGraph <GraphGenerators.GridGraph>`
- :meth:`HouseGraph <GraphGenerators.HouseGraph>`
- :meth:`HouseXGraph <GraphGenerators.HouseXGraph>`
- :meth:`KrackhardtKiteGraph <GraphGenerators.KrackhardtKiteGraph>`
- :meth:`LadderGraph <GraphGenerators.LadderGraph>`
- :meth:`LCFGraph <GraphGenerators.LCFGraph>`
- :meth:`LollipopGraph <GraphGenerators.LollipopGraph>`
- :meth:`PathGraph <GraphGenerators.PathGraph>`
- :meth:`StarGraph <GraphGenerators.StarGraph>`
- :meth:`ToroidalGrid2dGraph <GraphGenerators.ToroidalGrid2dGraph>`
- :meth:`Toroidal6RegularGrid2dGraph <GraphGenerators.Toroidal6RegularGrid2dGraph>`
- :meth:`WheelGraph <GraphGenerators.WheelGraph>`

Platonic solids
---------------

- :meth:`DodecahedralGraph <GraphGenerators.DodecahedralGraph>`
- :meth:`HexahedralGraph <GraphGenerators.HexahedralGraph>`
- :meth:`IcosahedralGraph <GraphGenerators.IcosahedralGraph>`
- :meth:`OctahedralGraph <GraphGenerators.OctahedralGraph>`
- :meth:`TetrahedralGraph <GraphGenerators.TetrahedralGraph>`

Named Graphs
------------

- :meth:`Balaban10Cage <GraphGenerators.Balaban10Cage>`
- :meth:`Balaban11Cage <GraphGenerators.Balaban11Cage>`
- :meth:`BidiakisCube <GraphGenerators.BidiakisCube>`
- :meth:`BiggsSmithGraph <GraphGenerators.BiggsSmithGraph>`
- :meth:`BrinkmannGraph <GraphGenerators.BrinkmannGraph>`
- :meth:`ChvatalGraph <GraphGenerators.ChvatalGraph>`
- :meth:`ClebschGraph <GraphGenerators.ClebschGraph>`
- :meth:`CoxeterGraph <GraphGenerators.CoxeterGraph>`
- :meth:`DoubleStarSnark <GraphGenerators.DoubleStarSnark>`
- :meth:`DesarguesGraph <GraphGenerators.DesarguesGraph>`
- :meth:`DurerGraph <GraphGenerators.DurerGraph>`
- :meth:`DyckGraph <GraphGenerators.DyckGraph>`
- :meth:`EllinghamHorton54Graph <GraphGenerators.EllinghamHorton54Graph>`
- :meth:`EllinghamHorton78Graph <GraphGenerators.EllinghamHorton78Graph>`
- :meth:`ErreraGraph <GraphGenerators.ErreraGraph>`
- :meth:`FlowerSnark <GraphGenerators.FlowerSnark>`
- :meth:`FosterGraph <GraphGenerators.FosterGraph>`
- :meth:`FranklinGraph <GraphGenerators.FranklinGraph>`
- :meth:`FruchtGraph <GraphGenerators.FruchtGraph>`
- :meth:`GoldnerHararyGraph <GraphGenerators.GoldnerHararyGraph>`
- :meth:`GrayGraph <GraphGenerators.GrayGraph>`
- :meth:`GrotzschGraph <GraphGenerators.GrotzschGraph>`
- :meth:`HallJankoGraph <GraphGenerators.HallJankoGraph>`
- :meth:`HararyGraph <GraphGenerators.HararyGraph>`
- :meth:`HarriesGraph <GraphGenerators.HarriesGraph>`
- :meth:`HarriesWongGraph <GraphGenerators.HarriesWongGraph>`
- :meth:`HeawoodGraph <GraphGenerators.HeawoodGraph>`
- :meth:`HerschelGraph <GraphGenerators.HerschelGraph>`
- :meth:`HigmanSimsGraph <GraphGenerators.HigmanSimsGraph>`
- :meth:`HoffmanSingletonGraph <GraphGenerators.HoffmanSingletonGraph>`
- :meth:`HoffmanGraph <GraphGenerators.HoffmanGraph>`
- :meth:`HoltGraph <GraphGenerators.HoltGraph>`
- :meth:`LjubljanaGraph <GraphGenerators.LjubljanaGraph>`
- :meth:`McGeeGraph <GraphGenerators.McGeeGraph>`
- :meth:`MoebiusKantorGraph <GraphGenerators.MoebiusKantorGraph>`
- :meth:`MoserSpindle <GraphGenerators.MoserSpindle>`
- :meth:`PappusGraph <GraphGenerators.PappusGraph>`
- :meth:`PetersenGraph <GraphGenerators.PetersenGraph>`
- :meth:`ShrikhandeGraph <GraphGenerators.ShrikhandeGraph>`
- :meth:`ThomsenGraph <GraphGenerators.ThomsenGraph>`
- :meth:`Tutte12Cage <GraphGenerators.Tutte12Cage>`
- :meth:`TutteCoxeterGraph <GraphGenerators.TutteCoxeterGraph>`
- :meth:`WagnerGraph <GraphGenerators.WagnerGraph>`


Families of graphs
------------------

- :meth:`BalancedTree <GraphGenerators.BalancedTree>`
- :meth:`BubbleSortGraph <GraphGenerators.BubbleSortGraph>`
- :meth:`CirculantGraph <GraphGenerators.CirculantGraph>`
- :meth:`CompleteBipartiteGraph <GraphGenerators.CompleteBipartiteGraph>`
- :meth:`CompleteGraph <GraphGenerators.CompleteGraph>`
- :meth:`CubeGraph <GraphGenerators.CubeGraph>`
- :meth:`FibonacciTree <GraphGenerators.FibonacciTree>`
- :meth:`FriendshipGraph <GraphGenerators.FriendshipGraph>`
- :meth:`FuzzyBallGraph <GraphGenerators.FuzzyBallGraph>`
- :meth:`GeneralizedPetersenGraph <GraphGenerators.GeneralizedPetersenGraph>`
- :meth:`HanoiTowerGraph <GraphGenerators.HanoiTowerGraph>`
- :meth:`HyperStarGraph <GraphGenerators.HyperStarGraph>`
- :meth:`KneserGraph <GraphGenerators.KneserGraph>`
- :meth:`LCFGraph <GraphGenerators.LCFGraph>`
- :meth:`MycielskiGraph <GraphGenerators.MycielskiGraph>`
- :meth:`MycielskiStep <GraphGenerators.MycielskiStep>`
- :meth:`NKStarGraph <GraphGenerators.NKStarGraph>`
- :meth:`NStarGraph <GraphGenerators.NStarGraph>`
- :meth:`OddGraph <GraphGenerators.OddGraph>`
- :meth:`PaleyGraph <GraphGenerators.PaleyGraph>`
- :meth:`RingedTree <GraphGenerators.RingedTree>`
- :meth:`line_graph_forbidden_subgraphs <GraphGenerators.line_graph_forbidden_subgraphs>`
- :meth:`PermutationGraph <GraphGenerators.PermutationGraph>`
- :meth:`trees <GraphGenerators.trees>`

Chessboard graphs :

- :meth:`BishopGraph <GraphGenerators.BishopGraph>`
- :meth:`KingGraph <GraphGenerators.KingGraph>`
- :meth:`KnightGraph <GraphGenerators.KnightGraph>`
- :meth:`QueenGraph <GraphGenerators.QueenGraph>`
- :meth:`RookGraph <GraphGenerators.RookGraph>`

Pseudofractal graphs
--------------------

- :meth:`DorogovtsevGoltsevMendesGraph <GraphGenerators.DorogovtsevGoltsevMendesGraph>`

Random graphs
-------------

- :meth:`RandomBarabasiAlbert <GraphGenerators.RandomBarabasiAlbert>`
- :meth:`RandomBipartite <GraphGenerators.RandomBipartite>`
- :meth:`RandomGNM <GraphGenerators.RandomGNM>`
- :meth:`RandomGNP <GraphGenerators.RandomGNP>`
- :meth:`RandomHolmeKim <GraphGenerators.RandomHolmeKim>`
- :meth:`RandomInterval <GraphGenerators.RandomInterval>`
- :meth:`RandomLobster <GraphGenerators.RandomLobster>`
- :meth:`RandomNewmanWattsStrogatz <GraphGenerators.RandomNewmanWattsStrogatz>`
- :meth:`RandomRegular <GraphGenerators.RandomRegular>`
- :meth:`RandomShell <GraphGenerators.RandomShell>`
- :meth:`RandomTree <GraphGenerators.RandomTree>`
- :meth:`RandomTreePowerlaw <GraphGenerators.RandomTreePowerlaw>`


Graphs with a given degree sequence
-----------------------------------

- :meth:`DegreeSequence <GraphGenerators.DegreeSequence>`
- :meth:`DegreeSequenceBipartite <GraphGenerators.DegreeSequenceBipartite>`
- :meth:`DegreeSequenceConfigurationModel <GraphGenerators.DegreeSequenceConfigurationModel>`
- :meth:`DegreeSequenceExpected <GraphGenerators.DegreeSequenceExpected>`
- :meth:`DegreeSequenceTree <GraphGenerators.DegreeSequenceTree>`


Miscellaneous
-------------

- :meth:`WorldMap <GraphGenerators.WorldMap>`


AUTHORS:

- Robert Miller (2006-11-05): initial version, empty, random, petersen

- Emily Kirkman (2006-11-12): basic structures, node positioning for
  all constructors

- Emily Kirkman (2006-11-19): docstrings, examples

- William Stein (2006-12-05): Editing.

- Robert Miller (2007-01-16): Cube generation and plotting

- Emily Kirkman (2007-01-16): more basic structures, docstrings

- Emily Kirkman (2007-02-14): added more named graphs

- Robert Miller (2007-06-08-11): Platonic solids, random graphs,
  graphs with a given degree sequence, random directed graphs

- Robert Miller (2007-10-24): Isomorph free exhaustive generation

- Nathann Cohen (2009-08-12): WorldMap

- Michael Yurko (2009-9-01): added hyperstar, (n,k)-star, n-star, and
  bubblesort graphs

- Anders Jonsson (2009-10-15): added generalized Petersen graphs

- Harald Schilly and Yann Laigle-Chapuy (2010-03-24): added Fibonacci Tree

- Jason Grout (2010-06-04): cospectral_graphs

- Edward Scheinerman (2010-08-11): RandomTree

- Ed Scheinerman (2010-08-21): added Grotzsch graph and Mycielski graphs

- Minh Van Nguyen (2010-11-26): added more named graphs

- Keshav Kini (2011-02-16): added Shrikhande and Dyck graphs

- David Coudert (2012-02-10): new RandomGNP generator

- David Coudert (2012-08-02): added chessboard graphs: Queen, King,
  Knight, Bishop, and Rook graphs
"""

###########################################################################

#           Copyright (C) 2006 Robert L. Miller <rlmillster@gmail.com>
#                              and Emily A. Kirkman
#           Copyright (C) 2009 Michael C. Yurko <myurko@gmail.com>
#
# Distributed  under  the  terms  of  the  GNU  General  Public  License (GPL)
#                         http://www.gnu.org/licenses/
###########################################################################

# import from Python standard library
from math import sin, cos, pi

# import from Sage library
import graph
from sage.misc.randstate import current_randstate

class GraphGenerators():
    r"""
    A class consisting of constructors for several common graphs, as
    well as orderly generation of isomorphism class representatives. See the
    section :ref:`organization` for a list of supported constructors.

    A list of all graphs and graph structures (other than isomorphism class
    representatives) in this database is available via tab completion. Type
    "graphs." and then hit the tab key to see which graphs are available.

    The docstrings include educational information about each named
    graph with the hopes that this class can be used as a reference.

    For all the constructors in this class (except the octahedral,
    dodecahedral, random and empty graphs), the position dictionary is
    filled to override the spring-layout algorithm.


    ORDERLY GENERATION::

        graphs(vertices, property=lambda x: True, augment='edges', size=None)

    This syntax accesses the generator of isomorphism class
    representatives. Iterates over distinct, exhaustive
    representatives.

    Also: see the use of the optional nauty package for generating graphs
    at the :meth:`nauty_geng` method.

    INPUT:

    - ``vertices`` -- natural number.

    - ``property`` -- (default: ``lambda x: True``) any property to be
      tested on graphs before generation, but note that in general the
      graphs produced are not the same as those produced by using the
      property function to filter a list of graphs produced by using
      the ``lambda x: True`` default. The generation process assumes
      the property has certain characteristics set by the ``augment``
      argument, and only in the case of inherited properties such that
      all subgraphs of the relevant kind (for ``augment='edges'`` or
      ``augment='vertices'``) of a graph with the property also
      possess the property will there be no missing graphs.  (The
      ``property`` argument is ignored if ``degree_sequence`` is
      specified.)

    - ``augment`` -- (default: ``'edges'``) possible values:

      - ``'edges'`` -- augments a fixed number of vertices by
        adding one edge. In this case, all graphs on exactly ``n=vertices`` are
        generated. If for any graph G satisfying the property, every
        subgraph, obtained from G by deleting one edge but not the vertices
        incident to that edge, satisfies the property, then this will
        generate all graphs with that property. If this does not hold, then
        all the graphs generated will satisfy the property, but there will
        be some missing.

      - ``'vertices'`` -- augments by adding a vertex and
        edges incident to that vertex. In this case, all graphs up to
        ``n=vertices`` are generated. If for any graph G satisfying the
        property, every subgraph, obtained from G by deleting one vertex
        and only edges incident to that vertex, satisfies the property,
        then this will generate all graphs with that property. If this does
        not hold, then all the graphs generated will satisfy the property,
        but there will be some missing.

    - ``size`` -- (default: ``None``) the size of the graph to be generated.

    - ``degree_sequence`` -- (default: ``None``) a sequence of non-negative integers,
      or ``None``. If specified, the generated graphs will have these
      integers for degrees. In this case, property and size are both
      ignored.

    - ``loops`` -- (default: ``False``) whether to allow loops in the graph
      or not.

    - ``implementation`` -- (default: ``'c_graph'``) which underlying
      implementation to use (see ``Graph?``).

    - ``sparse`` -- (default: ``True``) ignored if implementation is not
      ``'c_graph'``.

    - ``copy`` (boolean) -- If set to ``True`` (default)
      this method makes copies of the graphs before returning
      them. If set to ``False`` the method returns the graph it
      is working on. The second alternative is faster, but modifying
      any of the graph instances returned by the method may break
      the function's behaviour, as it is using these graphs to
      compute the next ones : only use ``copy_graph = False`` when
      you stick to *reading* the graphs returned.

    EXAMPLES:

    Print graphs on 3 or less vertices::

        sage: for G in graphs(3, augment='vertices'):
        ...    print G
        Graph on 0 vertices
        Graph on 1 vertex
        Graph on 2 vertices
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 2 vertices
        Graph on 3 vertices

    Note that we can also get graphs with underlying Cython implementation::

        sage: for G in graphs(3, augment='vertices', implementation='c_graph'):
        ...    print G
        Graph on 0 vertices
        Graph on 1 vertex
        Graph on 2 vertices
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 2 vertices
        Graph on 3 vertices

    Print graphs on 3 vertices.

    ::

        sage: for G in graphs(3):
        ...    print G
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 3 vertices

    Generate all graphs with 5 vertices and 4 edges.

    ::

        sage: L = graphs(5, size=4)
        sage: len(list(L))
        6

    Generate all graphs with 5 vertices and up to 4 edges.

    ::

        sage: L = list(graphs(5, lambda G: G.size() <= 4))
        sage: len(L)
        14
        sage: graphs_list.show_graphs(L) # long time

    Generate all graphs with up to 5 vertices and up to 4 edges.

    ::

        sage: L = list(graphs(5, lambda G: G.size() <= 4, augment='vertices'))
        sage: len(L)
        31
        sage: graphs_list.show_graphs(L)              # long time

    Generate all graphs with degree at most 2, up to 6 vertices.

    ::

        sage: property = lambda G: ( max([G.degree(v) for v in G] + [0]) <= 2 )
        sage: L = list(graphs(6, property, augment='vertices'))
        sage: len(L)
        45

    Generate all bipartite graphs on up to 7 vertices: (see
    http://oeis.org/classic/A033995)

    ::

        sage: L = list( graphs(7, lambda G: G.is_bipartite(), augment='vertices') )
        sage: [len([g for g in L if g.order() == i]) for i in [1..7]]
        [1, 2, 3, 7, 13, 35, 88]

    Generate all bipartite graphs on exactly 7 vertices::

        sage: L = list( graphs(7, lambda G: G.is_bipartite()) )
        sage: len(L)
        88

    Generate all bipartite graphs on exactly 8 vertices::

        sage: L = list( graphs(8, lambda G: G.is_bipartite()) ) # long time
        sage: len(L)                                            # long time
        303

    Remember that the property argument does not behave as a filter,
    except for appropriately inheritable properties::

        sage: property = lambda G: G.is_vertex_transitive()
        sage: len(list(graphs(4, property)))
        1
        sage: len(filter(property, graphs(4)))
        4
        sage: property = lambda G: G.is_bipartite()
        sage: len(list(graphs(4, property)))
        7
        sage: len(filter(property, graphs(4)))
        7

    Generate graphs on the fly: (see http://oeis.org/classic/A000088)

    ::

        sage: for i in range(0, 7):
        ...    print len(list(graphs(i)))
        1
        1
        2
        4
        11
        34
        156

    Generate all simple graphs, allowing loops: (see
    http://oeis.org/classic/A000666)

    ::

        sage: L = list(graphs(5,augment='vertices',loops=True))               # long time
        sage: for i in [0..5]: print i, len([g for g in L if g.order() == i]) # long time
        0 1
        1 2
        2 6
        3 20
        4 90
        5 544

    Generate all graphs with a specified degree sequence (see
    http://oeis.org/classic/A002851)::

        sage: for i in [4,6,8]:  # long time (4s on sage.math, 2012)
        ...       print i, len([g for g in graphs(i, degree_sequence=[3]*i) if g.is_connected()])
        4 1
        6 2
        8 5
        sage: for i in [4,6,8]:  # long time (7s on sage.math, 2012)
        ...       print i, len([g for g in graphs(i, augment='vertices', degree_sequence=[3]*i) if g.is_connected()])
        4 1
        6 2
        8 5

    ::

        sage: print 10, len([g for g in graphs(10,degree_sequence=[3]*10) if g.is_connected()]) # not tested
        10 19

    Make sure that the graphs are really independent and the generator
    survives repeated vertex removal (trac 8458)::

        sage: for G in graphs(3):
        ...       G.delete_vertex(0)
        ...       print(G.order())
        2
        2
        2
        2

    REFERENCE:

    - Brendan D. McKay, Isomorph-Free Exhaustive generation.  *Journal
      of Algorithms*, Volume 26, Issue 2, February 1998, pages 306-324.
    """

################################################################################
#   Pseudofractal Graphs
################################################################################

    def DorogovtsevGoltsevMendesGraph(self, n):
        """
        Construct the n-th generation of the Dorogovtsev-Goltsev-Mendes
        graph.

        EXAMPLE::

            sage: G = graphs.DorogovtsevGoltsevMendesGraph(8)
            sage: G.size()
            6561

        REFERENCE:

        - [1] Dorogovtsev, S. N., Goltsev, A. V., and Mendes, J.
          F. F., Pseudofractal scale-free web, Phys. Rev. E 066122
          (2002).
        """
        import networkx
        return graph.Graph(networkx.dorogovtsev_goltsev_mendes_graph(n),\
               name="Dorogovtsev-Goltsev-Mendes Graph, %d-th generation"%n)

    def IntervalGraph(self,intervals):
        r"""
        Returns the graph corresponding to the given intervals.

        An interval graph is built from a list `(a_i,b_i)_{1\leq i \leq n}`
        of intervals : to each interval of the list is associated one
        vertex, two vertices being adjacent if the two corresponding
        (closed) intervals intersect.

        INPUT:

        - ``intervals`` -- the list of pairs `(a_i,b_i)`
          defining the graph.

        .. NOTE::

            * The vertices are named 0, 1, 2, and so on. The
              intervals used to create the graph are saved with the
              graph and can be recovered using ``get_vertex()`` or
              ``get_vertices()``.

            * The intervals `(a_i,b_i)` need not verify `a_i<b_i`.

        EXAMPLE:

        The following line creates the sequence of intervals
        `(i, i+2)` for i in `[0, ..., 8]`::

            sage: intervals = [(i,i+2) for i in range(9)]

        In the corresponding graph... ::

            sage: g = graphs.IntervalGraph(intervals)
            sage: g.get_vertex(3)
            (3, 5)
            sage: neigh = g.neighbors(3)
            sage: for v in neigh: print g.get_vertex(v)
            (1, 3)
            (2, 4)
            (4, 6)
            (5, 7)

        The is_interval() method verifies that this graph is an interval
        graph. ::

            sage: g.is_interval()
            True

        The intervals in the list need not be distinct. ::

            sage: intervals = [ (1,2), (1,2), (1,2), (2,3), (3,4) ]
            sage: g = graphs.IntervalGraph(intervals)
            sage: g.clique_maximum()
            [0, 1, 2, 3]
            sage: g.get_vertices()
            {0: (1, 2), 1: (1, 2), 2: (1, 2), 3: (2, 3), 4: (3, 4)}

        """

        n = len(intervals)
        g = graph.Graph(n)

        edges = []

        for i in range(n-1):
            I = intervals[i]
            for j in range(i+1,n):
                J = intervals[j]
                if max(I) < min(J) or max(J) < min(I): continue
                edges.append((i,j))

        g.add_edges(edges)

        rep = dict( zip(range(n),intervals) )
        g.set_vertices(rep)

        return g



###########################################################################
#   Graph Iterators
###########################################################################

    def __call__(self, vertices=None, property=lambda x: True, augment='edges',
        size=None, deg_seq=None, degree_sequence=None, loops=False, implementation='c_graph',
        sparse=True, copy = True):
        """
        Accesses the generator of isomorphism class representatives.
        Iterates over distinct, exhaustive representatives. See the docstring
        of this class for full documentation.

        EXAMPLES:

        Print graphs on 3 or less vertices::

            sage: for G in graphs(3, augment='vertices'):
            ...    print G
            Graph on 0 vertices
            Graph on 1 vertex
            Graph on 2 vertices
            Graph on 3 vertices
            Graph on 3 vertices
            Graph on 3 vertices
            Graph on 2 vertices
            Graph on 3 vertices

        ::

            sage: for g in graphs():
            ...    if g.num_verts() > 3: break
            ...    print g
            Graph on 0 vertices
            Graph on 1 vertex
            Graph on 2 vertices
            Graph on 2 vertices
            Graph on 3 vertices
            Graph on 3 vertices
            Graph on 3 vertices
            Graph on 3 vertices

        For more examples, see the class level documentation, or type::

            sage: graphs? # not tested

        REFERENCE:

        - Brendan D. McKay, Isomorph-Free Exhaustive generation.
          Journal of Algorithms Volume 26, Issue 2, February 1998,
          pages 306-324.
        """
        from sage.graphs.all import Graph
        from sage.misc.superseded import deprecation
        from copy import copy as copyfun

        if deg_seq is not None:
            deprecation(11927, "The argument name deg_seq is deprecated. It will be "
                        "removed in a future release of Sage. So, please use "
                        "degree_sequence instead.")
        if degree_sequence is None:
            degree_sequence=deg_seq
        if degree_sequence is not None:
            if vertices is None:
                raise NotImplementedError
            if len(degree_sequence) != vertices or sum(degree_sequence)%2 or sum(degree_sequence) > vertices*(vertices-1):
                raise ValueError("Invalid degree sequence.")
            degree_sequence = sorted(degree_sequence)
            if augment == 'edges':
                property = lambda x: all([degree_sequence[i] >= d for i,d in enumerate(sorted(x.degree()))])
                extra_property = lambda x: degree_sequence == sorted(x.degree())
            else:
                property = lambda x: all([degree_sequence[i] >= d for i,d in enumerate(sorted(x.degree() + [0]*(vertices-x.num_verts()) ))])
                extra_property = lambda x: x.num_verts() == vertices and degree_sequence == sorted(x.degree())
        elif size is not None:
            extra_property = lambda x: x.size() == size
        else:
            extra_property = lambda x: True
        if augment == 'vertices':
            if vertices is None:
                raise NotImplementedError
            g = Graph(loops=loops, implementation=implementation, sparse=sparse)
            for gg in canaug_traverse_vert(g, [], vertices, property, loops=loops, implementation=implementation, sparse=sparse):
                if extra_property(gg):
                    yield copyfun(gg) if copy else gg
        elif augment == 'edges':
            if vertices is None:
                from sage.rings.all import Integer
                vertices = Integer(0)
                while True:
                    for g in self(vertices, loops=loops, implementation=implementation, sparse=sparse):
                        yield copyfun(g) if copy else g
                    vertices += 1
            g = Graph(vertices, loops=loops, implementation=implementation, sparse=sparse)
            gens = []
            for i in range(vertices-1):
                gen = range(i)
                gen.append(i+1); gen.append(i)
                gen += range(i+2, vertices)
                gens.append(gen)
            for gg in canaug_traverse_edge(g, gens, property, loops=loops, implementation=implementation, sparse=sparse):
                if extra_property(gg):
                    yield copyfun(gg) if copy else gg
        else:
            raise NotImplementedError


    def nauty_geng(self, options="", debug=False):
        r"""
        Returns a generator which creates graphs from nauty's geng program.

        .. note::

            Due to license restrictions, the nauty package is distributed
            as a Sage optional package.  At a system command line, execute
            ``sage -i nauty`` to see the nauty license and install the
            package.

        INPUT:

        - ``options`` - a string passed to  geng  as if it was run at
          a system command line. At a minimum, you *must* pass the
          number of vertices you desire.  Sage expects the graphs to be
          in nauty's "graph6" format, do not set an option to change
          this default or results will be unpredictable.

        - ``debug`` - default: ``False`` - if ``True`` the first line of
          geng's output to standard error is captured and the first call
          to the generator's ``next()`` function will return this line
          as a string.  A line leading with ">A" indicates a successful
          initiation of the program with some information on the arguments,
          while a line beginning with ">E" indicates an error with the input.

        The possible options, obtained as output of ``geng --help``::

                 n    : the number of vertices
            mine:maxe : a range for the number of edges
                        #:0 means '# or more' except in the case 0:0
              res/mod : only generate subset res out of subsets 0..mod-1

                -c    : only write connected graphs
                -C    : only write biconnected graphs
                -t    : only generate triangle-free graphs
                -f    : only generate 4-cycle-free graphs
                -b    : only generate bipartite graphs
                            (-t, -f and -b can be used in any combination)
                -m    : save memory at the expense of time (only makes a
                            difference in the absence of -b, -t, -f and n <= 28).
                -d#   : a lower bound for the minimum degree
                -D#   : a upper bound for the maximum degree
                -v    : display counts by number of edges
                -l    : canonically label output graphs

                -q    : suppress auxiliary output (except from -v)

        Options which cause geng to use an output format different
        than the graph6 format are not listed above (-u, -g, -s, -y, -h)
        as they will confuse the creation of a Sage graph.  The res/mod
        option can be useful when using the output in a routine run
        several times in parallel.

        OUTPUT:

        A generator which will produce the graphs as Sage graphs.
        These will be simple graphs: no loops, no multiple edges, no
        directed edges.

        EXAMPLES:

        The generator can be used to construct graphs for testing,
        one at a time (usually inside a loop).  Or it can be used to
        create an entire list all at once if there is sufficient memory
        to contain it.  ::

            sage: gen = graphs.nauty_geng("2") # optional nauty
            sage: gen.next() # optional nauty
            Graph on 2 vertices
            sage: gen.next() # optional nauty
            Graph on 2 vertices
            sage: gen.next() # optional nauty
            Traceback (most recent call last):
            ...
            StopIteration: Exhausted list of graphs from nauty geng

        A list of all graphs on 7 vertices.  This agrees with
        Sloane's OEIS sequence A000088.  ::

            sage: gen = graphs.nauty_geng("7") # optional nauty
            sage: len(list(gen))  # optional nauty
            1044

        A list of just the connected graphs on 7 vertices.  This agrees with
        Sloane's OEIS sequence A001349.  ::

            sage: gen = graphs.nauty_geng("7 -c") # optional nauty
            sage: len(list(gen))  # optional nauty
            853

        The ``debug`` switch can be used to examine geng's reaction
        to the input in the ``options`` string.  We illustrate success.
        (A failure will be a string beginning with ">E".)  Passing the
        "-q" switch to geng will supress the indicator of a
        successful initiation.  ::

            sage: gen = graphs.nauty_geng("4", debug=True) # optional nauty
            sage: print gen.next() # optional nauty
            >A nauty-geng -d0D3 n=4 e=0-6
        """
        import subprocess
        from sage.misc.package import is_package_installed
        if not is_package_installed("nauty"):
            raise TypeError, "the optional nauty package is not installed"
        sp = subprocess.Popen("nauty-geng {0}".format(options), shell=True,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, close_fds=True)
        if debug:
            yield sp.stderr.readline()
        gen = sp.stdout
        while True:
            try:
                s = gen.next()
            except StopIteration:
                raise StopIteration("Exhausted list of graphs from nauty geng")
            G = graph.Graph(s[:-1], format='graph6')
            yield G


    def cospectral_graphs(self, vertices, matrix_function=lambda g: g.adjacency_matrix(), graphs=None):
        r"""
        Find all sets of graphs on ``vertices`` vertices (with
        possible restrictions) which are cospectral with respect to a
        constructed matrix.

        INPUT:

        - ``vertices`` - The number of vertices in the graphs to be tested

        - ``matrix_function`` - A function taking a graph and giving back
          a matrix.  This defaults to the adjacency matrix.  The spectra
          examined are the spectra of these matrices.

        - ``graphs`` - One of three things:

           - ``None`` (default) - test all graphs having ``vertices``
             vertices

           - a function taking a graph and returning ``True`` or ``False``
             - test only the graphs on ``vertices`` vertices for which
             the function returns ``True``

           - a list of graphs (or other iterable object) - these graphs
             are tested for cospectral sets.  In this case,
             ``vertices`` is ignored.

        OUTPUT:

           A list of lists of graphs.  Each sublist will be a list of
           cospectral graphs (lists of cadinality 1 being omitted).


        EXAMPLES::

            sage: g=graphs.cospectral_graphs(5)
            sage: sorted(sorted(g.graph6_string() for g in glist) for glist in g)
            [['Dr?', 'Ds_']]
            sage: g[0][1].am().charpoly()==g[0][1].am().charpoly()
            True

        There are two sets of cospectral graphs on six vertices with no isolated vertices::

            sage: g=graphs.cospectral_graphs(6, graphs=lambda x: min(x.degree())>0)
            sage: sorted(sorted(g.graph6_string() for g in glist) for glist in g)
            [['Ep__', 'Er?G'], ['ExGg', 'ExoG']]
            sage: g[0][1].am().charpoly()==g[0][1].am().charpoly()
            True
            sage: g[1][1].am().charpoly()==g[1][1].am().charpoly()
            True

        There is one pair of cospectral trees on eight vertices::

            sage: g=graphs.cospectral_graphs(6, graphs=graphs.trees(8))
            sage: sorted(sorted(g.graph6_string() for g in glist) for glist in g)
            [['GiPC?C', 'GiQCC?']]
            sage: g[0][1].am().charpoly()==g[0][1].am().charpoly()
            True

        There are two sets of cospectral graphs (with respect to the
        Laplacian matrix) on six vertices::

            sage: g=graphs.cospectral_graphs(6, matrix_function=lambda g: g.laplacian_matrix())
            sage: sorted(sorted(g.graph6_string() for g in glist) for glist in g)
            [['Edq_', 'ErcG'], ['Exoo', 'EzcG']]
            sage: g[0][1].laplacian_matrix().charpoly()==g[0][1].laplacian_matrix().charpoly()
            True
            sage: g[1][1].laplacian_matrix().charpoly()==g[1][1].laplacian_matrix().charpoly()
            True

        To find cospectral graphs with respect to the normalized
        Laplacian, assuming the graphs do not have an isolated vertex, it
        is enough to check the spectrum of the matrix `D^{-1}A`, where `D`
        is the diagonal matrix of vertex degrees, and A is the adjacency
        matrix.  We find two such cospectral graphs (for the normalized
        Laplacian) on five vertices::

            sage: def DinverseA(g):
            ...     A=g.adjacency_matrix().change_ring(QQ)
            ...     for i in range(g.order()):
            ...         A.rescale_row(i, 1/len(A.nonzero_positions_in_row(i)))
            ...     return A
            sage: g=graphs.cospectral_graphs(5, matrix_function=DinverseA, graphs=lambda g: min(g.degree())>0)
            sage: sorted(sorted(g.graph6_string() for g in glist) for glist in g)
            [['Dlg', 'Ds_']]
            sage: g[0][1].laplacian_matrix(normalized=True).charpoly()==g[0][1].laplacian_matrix(normalized=True).charpoly()
            True
        """
        from sage.graphs.all import graphs as graph_gen
        if graphs is None:
            graph_list=graph_gen(vertices)
        elif callable(graphs):
            graph_list=iter(g for g in graph_gen(vertices) if graphs(g))
        else:
            graph_list=iter(graphs)

        from collections import defaultdict
        charpolys=defaultdict(list)
        for g in graph_list:
            cp=matrix_function(g).charpoly()
            charpolys[cp].append(g)

        cospectral_graphs=[]
        for cp,g_list in charpolys.items():
            if len(g_list)>1:
                cospectral_graphs.append(g_list)

        return cospectral_graphs

###########################################################################
# Chessboard graphs
###########################################################################

    import sage.graphs.generators.chessboard
    ChessboardGraphGenerator = sage.graphs.generators.chessboard.ChessboardGraphGenerator
    BishopGraph = sage.graphs.generators.chessboard.BishopGraph
    KingGraph = sage.graphs.generators.chessboard.KingGraph
    KnightGraph = sage.graphs.generators.chessboard.KnightGraph
    QueenGraph = sage.graphs.generators.chessboard.QueenGraph
    RookGraph = sage.graphs.generators.chessboard.RookGraph

###########################################################################
# Families
###########################################################################

    import sage.graphs.generators.families
    MycielskiGraph = sage.graphs.generators.families.MycielskiGraph
    MycielskiStep = sage.graphs.generators.families.MycielskiStep
    KneserGraph = sage.graphs.generators.families.KneserGraph
    BalancedTree = sage.graphs.generators.families.BalancedTree
    BubbleSortGraph = sage.graphs.generators.families.BubbleSortGraph
    CirculantGraph = sage.graphs.generators.families.CirculantGraph
    CompleteGraph = sage.graphs.generators.families.CompleteGraph
    CompleteBipartiteGraph = sage.graphs.generators.families.CompleteBipartiteGraph
    CompleteMultipartiteGraph = sage.graphs.generators.families.CompleteMultipartiteGraph
    CubeGraph = sage.graphs.generators.families.CubeGraph
    FriendshipGraph = sage.graphs.generators.families.FriendshipGraph
    FuzzyBallGraph = sage.graphs.generators.families.FuzzyBallGraph
    FibonacciTree = sage.graphs.generators.families.FibonacciTree
    GeneralizedPetersenGraph = sage.graphs.generators.families.GeneralizedPetersenGraph
    HyperStarGraph = sage.graphs.generators.families.HyperStarGraph
    LCFGraph = sage.graphs.generators.families.LCFGraph
    NKStarGraph = sage.graphs.generators.families.NKStarGraph
    NStarGraph = sage.graphs.generators.families.NStarGraph
    OddGraph = sage.graphs.generators.families.OddGraph
    PaleyGraph = sage.graphs.generators.families.PaleyGraph
    PermutationGraph = sage.graphs.generators.families.PermutationGraph
    HanoiTowerGraph = sage.graphs.generators.families.HanoiTowerGraph
    line_graph_forbidden_subgraphs = sage.graphs.generators.families.line_graph_forbidden_subgraphs
    trees = sage.graphs.generators.families.trees
    RingedTree = sage.graphs.generators.families.RingedTree

###########################################################################
# Small Graphs
###########################################################################
    import sage.graphs.generators.smallgraphs
    Balaban10Cage = sage.graphs.generators.smallgraphs.Balaban10Cage
    Balaban11Cage = sage.graphs.generators.smallgraphs.Balaban11Cage
    BidiakisCube = sage.graphs.generators.smallgraphs.BidiakisCube
    BiggsSmithGraph = sage.graphs.generators.smallgraphs.BiggsSmithGraph
    BrinkmannGraph = sage.graphs.generators.smallgraphs.BrinkmannGraph
    ChvatalGraph = sage.graphs.generators.smallgraphs.ChvatalGraph
    ClebschGraph = sage.graphs.generators.smallgraphs.ClebschGraph
    CoxeterGraph = sage.graphs.generators.smallgraphs.CoxeterGraph
    DesarguesGraph = sage.graphs.generators.smallgraphs.DesarguesGraph
    DoubleStarSnark = sage.graphs.generators.smallgraphs.DoubleStarSnark
    DurerGraph = sage.graphs.generators.smallgraphs.DurerGraph
    DyckGraph = sage.graphs.generators.smallgraphs.DyckGraph
    EllinghamHorton54Graph = sage.graphs.generators.smallgraphs.EllinghamHorton54Graph
    EllinghamHorton78Graph = sage.graphs.generators.smallgraphs.EllinghamHorton78Graph
    ErreraGraph = sage.graphs.generators.smallgraphs.ErreraGraph
    FlowerSnark = sage.graphs.generators.smallgraphs.FlowerSnark
    FosterGraph = sage.graphs.generators.smallgraphs.FosterGraph
    FranklinGraph = sage.graphs.generators.smallgraphs.FranklinGraph
    FruchtGraph = sage.graphs.generators.smallgraphs.FruchtGraph
    GoldnerHararyGraph = sage.graphs.generators.smallgraphs.GoldnerHararyGraph
    GrayGraph = sage.graphs.generators.smallgraphs.GrayGraph
    GrotzschGraph = sage.graphs.generators.smallgraphs.GrotzschGraph
    HallJankoGraph = sage.graphs.generators.smallgraphs.HallJankoGraph
    HarriesGraph = sage.graphs.generators.smallgraphs.HarriesGraph
    HararyGraph = sage.graphs.generators.smallgraphs.HararyGraph
    HarriesWongGraph = sage.graphs.generators.smallgraphs.HarriesWongGraph
    HeawoodGraph = sage.graphs.generators.smallgraphs.HeawoodGraph
    HerschelGraph = sage.graphs.generators.smallgraphs.HerschelGraph
    HigmanSimsGraph = sage.graphs.generators.smallgraphs.HigmanSimsGraph
    HoffmanGraph = sage.graphs.generators.smallgraphs.HoffmanGraph
    HoffmanSingletonGraph = sage.graphs.generators.smallgraphs.HoffmanSingletonGraph
    HoltGraph = sage.graphs.generators.smallgraphs.HoltGraph
    LjubljanaGraph = sage.graphs.generators.smallgraphs.LjubljanaGraph
    McGeeGraph = sage.graphs.generators.smallgraphs.McGeeGraph
    MoebiusKantorGraph = sage.graphs.generators.smallgraphs.MoebiusKantorGraph
    MoserSpindle = sage.graphs.generators.smallgraphs.MoserSpindle
    NauruGraph = sage.graphs.generators.smallgraphs.NauruGraph
    PappusGraph = sage.graphs.generators.smallgraphs.PappusGraph
    PetersenGraph = sage.graphs.generators.smallgraphs.PetersenGraph
    ShrikhandeGraph = sage.graphs.generators.smallgraphs.ShrikhandeGraph
    ThomsenGraph = sage.graphs.generators.smallgraphs.ThomsenGraph
    Tutte12Cage = sage.graphs.generators.smallgraphs.Tutte12Cage
    TutteCoxeterGraph = sage.graphs.generators.smallgraphs.TutteCoxeterGraph
    WagnerGraph = sage.graphs.generators.smallgraphs.WagnerGraph


###########################################################################
# Basic Graphs
###########################################################################
    import sage.graphs.generators.basic
    BarbellGraph = sage.graphs.generators.basic.BarbellGraph
    BuckyBall = sage.graphs.generators.basic.BuckyBall
    BullGraph = sage.graphs.generators.basic.BullGraph
    ButterflyGraph = sage.graphs.generators.basic.ButterflyGraph
    CircularLadderGraph = sage.graphs.generators.basic.CircularLadderGraph
    ClawGraph = sage.graphs.generators.basic.ClawGraph
    CycleGraph = sage.graphs.generators.basic.CycleGraph
    DiamondGraph = sage.graphs.generators.basic.DiamondGraph
    EmptyGraph = sage.graphs.generators.basic.EmptyGraph
    Grid2dGraph = sage.graphs.generators.basic.Grid2dGraph
    GridGraph = sage.graphs.generators.basic.GridGraph
    HouseGraph = sage.graphs.generators.basic.HouseGraph
    HouseXGraph = sage.graphs.generators.basic.HouseXGraph
    KrackhardtKiteGraph = sage.graphs.generators.basic.KrackhardtKiteGraph
    LadderGraph = sage.graphs.generators.basic.LadderGraph
    LollipopGraph = sage.graphs.generators.basic.LollipopGraph
    PathGraph = sage.graphs.generators.basic.PathGraph
    StarGraph = sage.graphs.generators.basic.StarGraph
    Toroidal6RegularGrid2dGraph = sage.graphs.generators.basic.Toroidal6RegularGrid2dGraph
    ToroidalGrid2dGraph = sage.graphs.generators.basic.ToroidalGrid2dGraph
    WheelGraph = sage.graphs.generators.basic.WheelGraph

###########################################################################
# Random Graphs
###########################################################################
    import sage.graphs.generators.random
    RandomBarabasiAlbert = sage.graphs.generators.random.RandomBarabasiAlbert
    RandomBipartite = sage.graphs.generators.random.RandomBipartite
    RandomGNM = sage.graphs.generators.random.RandomGNM
    RandomGNP = sage.graphs.generators.random.RandomGNP
    RandomHolmeKim = sage.graphs.generators.random.RandomHolmeKim
    RandomInterval = sage.graphs.generators.random.RandomInterval
    RandomLobster = sage.graphs.generators.random.RandomLobster
    RandomNewmanWattsStrogatz = sage.graphs.generators.random.RandomNewmanWattsStrogatz
    RandomRegular = sage.graphs.generators.random.RandomRegular
    RandomShell = sage.graphs.generators.random.RandomShell
    RandomTreePowerlaw = sage.graphs.generators.random.RandomTreePowerlaw
    RandomTree = sage.graphs.generators.random.RandomTree

###########################################################################
# Platonic Solids
###########################################################################
    import sage.graphs.generators.platonic_solids
    DodecahedralGraph = sage.graphs.generators.platonic_solids.DodecahedralGraph
    HexahedralGraph = sage.graphs.generators.platonic_solids.HexahedralGraph
    IcosahedralGraph = sage.graphs.generators.platonic_solids.IcosahedralGraph
    OctahedralGraph = sage.graphs.generators.platonic_solids.OctahedralGraph
    TetrahedralGraph = sage.graphs.generators.platonic_solids.TetrahedralGraph

###########################################################################
# World Map
###########################################################################
    import sage.graphs.generators.world_map
    WorldMap = sage.graphs.generators.world_map.WorldMap

###########################################################################
# Degree Sequence
###########################################################################
    import sage.graphs.generators.degree_sequence
    DegreeSequence = sage.graphs.generators.degree_sequence.DegreeSequence
    DegreeSequenceBipartite = sage.graphs.generators.degree_sequence.DegreeSequenceBipartite
    DegreeSequenceConfigurationModel = sage.graphs.generators.degree_sequence.DegreeSequenceConfigurationModel
    DegreeSequenceTree = sage.graphs.generators.degree_sequence.DegreeSequenceTree
    DegreeSequenceExpected = sage.graphs.generators.degree_sequence.DegreeSequenceExpected

def canaug_traverse_vert(g, aut_gens, max_verts, property, dig=False, loops=False, implementation='c_graph', sparse=True):
    """
    Main function for exhaustive generation. Recursive traversal of a
    canonically generated tree of isomorph free (di)graphs satisfying a
    given property.

    INPUT:


    -  ``g`` - current position on the tree.

    -  ``aut_gens`` - list of generators of Aut(g), in
       list notation.

    -  ``max_verts`` - when to retreat.

    -  ``property`` - check before traversing below g.

    -  ``degree_sequence`` - specify a degree sequence to try to
       obtain.


    EXAMPLES::

        sage: from sage.graphs.graph_generators import canaug_traverse_vert
        sage: list(canaug_traverse_vert(Graph(), [], 3, lambda x: True))
        [Graph on 0 vertices, ... Graph on 3 vertices]

    The best way to access this function is through the graphs()
    iterator:

    Print graphs on 3 or less vertices.

    ::

        sage: for G in graphs(3, augment='vertices'):
        ...    print G
        ...
        Graph on 0 vertices
        Graph on 1 vertex
        Graph on 2 vertices
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 2 vertices
        Graph on 3 vertices

    Print digraphs on 2 or less vertices.

    ::

        sage: for D in digraphs(2, augment='vertices'):
        ...    print D
        ...
        Digraph on 0 vertices
        Digraph on 1 vertex
        Digraph on 2 vertices
        Digraph on 2 vertices
        Digraph on 2 vertices
    """
    from sage.graphs.generic_graph_pyx import binary
    from sage.groups.perm_gps.partn_ref.refinement_graphs import search_tree


    if not property(g):
        return
    yield g

    n = g.order()
    if n < max_verts:

        # build a list representing C(g) - the vertex to be added
        # is at the end, so only specify which edges...
        # in the case of graphs, there are n possibilities,
        # and in the case of digraphs, there are 2*n.
        if dig:
            possibilities = 2*n
        else:
            possibilities = n
        num_roots = 2**possibilities
        children = [-1]*num_roots

        # union-find C(g) under Aut(g)
        for gen in aut_gens:
            for i in xrange(len(children)):
                k = 0
                for j in xrange(possibilities):
                    if (1 << j)&i:
                        if dig and j >= n:
                            k += (1 << (gen[j-n]+n))
                        else:
                            k += (1 << gen[j])
                while children[k] != -1:
                    k = children[k]
                while children[i] != -1:
                    i = children[i]
                if i != k:
                    # union i & k
                    smaller, larger = sorted([i,k])
                    children[larger] = smaller
                    num_roots -= 1

        # find representatives of orbits of C(g)
        roots = []
        found_roots = 0
        i = 0
        while found_roots < num_roots:
            if children[i] == -1:
                found_roots += 1
                roots.append(i)
            i += 1
        for i in roots:
            # construct a z for each number in roots...
            z = g.copy(implementation=implementation, sparse=sparse)
            z.add_vertex(n)
            edges = []
            if dig:
                index = 0
                while index < possibilities/2:
                    if (1 << index)&i:
                        edges.append((index,n))
                    index += 1
                while index < possibilities:
                    if (1 << index)&i:
                        edges.append((n,index-n))
                    index += 1
            else:
                index = 0
                while (1 << index) <= i:
                    if (1 << index)&i:
                        edges.append((index,n))
                    index += 1
            z.add_edges(edges)
            z_s = []
            if property(z):
                z_s.append(z)
            if loops:
                z = z.copy(implementation=implementation, sparse=sparse)
                z.add_edge((n,n))
                if property(z):
                    z_s.append(z)
            for z in z_s:
                z_aut_gens, _, canonical_relabeling = search_tree(z, [z.vertices()], certify=True, dig=(dig or loops))
                cut_vert = 0
                while canonical_relabeling[cut_vert] != n:
                    cut_vert += 1
                sub_verts = [v for v in z if v != cut_vert]
                m_z = z.subgraph(sub_verts)

                if m_z == g:
                    for a in canaug_traverse_vert(z, z_aut_gens, max_verts, property, dig=dig, loops=loops, implementation=implementation, sparse=sparse):
                        yield a
                else:
                    for possibility in check_aut(z_aut_gens, cut_vert, n):
                        if m_z.relabel(possibility, inplace=False) == g:
                            for a in canaug_traverse_vert(z, z_aut_gens, max_verts, property, dig=dig, loops=loops, implementation=implementation, sparse=sparse):
                                yield a
                            break

def check_aut(aut_gens, cut_vert, n):
    """
    Helper function for exhaustive generation.

    At the start, check_aut is given a set of generators for the
    automorphism group, aut_gens. We already know we are looking for
    an element of the auto- morphism group that sends cut_vert to n,
    and check_aut generates these for the canaug_traverse function.

    EXAMPLE: Note that the last two entries indicate that none of the
    automorphism group has yet been searched - we are starting at the
    identity [0, 1, 2, 3] and so far that is all we have seen. We
    return automorphisms mapping 2 to 3.

    ::

        sage: from sage.graphs.graph_generators import check_aut
        sage: list( check_aut( [ [0, 3, 2, 1], [1, 0, 3, 2], [2, 1, 0, 3] ], 2, 3))
        [[1, 0, 3, 2], [1, 2, 3, 0]]
    """
    from copy import copy
    perm = range(n+1)
    seen_perms = [perm]
    unchecked_perms = [perm]
    while len(unchecked_perms) != 0:
        perm = unchecked_perms.pop(0)
        for gen in aut_gens:
            new_perm = copy(perm)
            for i in xrange(len(perm)):
                new_perm[i] = gen[perm[i]]
            if new_perm not in seen_perms:
                seen_perms.append(new_perm)
                unchecked_perms.append(new_perm)
                if new_perm[cut_vert] == n:
                    yield new_perm

def canaug_traverse_edge(g, aut_gens, property, dig=False, loops=False, implementation='c_graph', sparse=True):
    """
    Main function for exhaustive generation. Recursive traversal of a
    canonically generated tree of isomorph free graphs satisfying a
    given property.

    INPUT:


    -  ``g`` - current position on the tree.

    -  ``aut_gens`` - list of generators of Aut(g), in
       list notation.

    -  ``property`` - check before traversing below g.


    EXAMPLES::

        sage: from sage.graphs.graph_generators import canaug_traverse_edge
        sage: G = Graph(3)
        sage: list(canaug_traverse_edge(G, [], lambda x: True))
        [Graph on 3 vertices, ... Graph on 3 vertices]

    The best way to access this function is through the graphs()
    iterator:

    Print graphs on 3 or less vertices.

    ::

        sage: for G in graphs(3):
        ...    print G
        ...
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 3 vertices
        Graph on 3 vertices

    Print digraphs on 3 or less vertices.

    ::

        sage: for G in digraphs(3):
        ...    print G
        ...
        Digraph on 3 vertices
        Digraph on 3 vertices
        ...
        Digraph on 3 vertices
        Digraph on 3 vertices
    """
    from sage.graphs.generic_graph_pyx import binary
    from sage.groups.perm_gps.partn_ref.refinement_graphs import search_tree
    if not property(g):
        return
    yield g
    n = g.order()
    if dig:
        max_size = n*(n-1)
    else:
        max_size = (n*(n-1))>>1 # >> 1 is just / 2 (this is n choose 2)
    if loops: max_size += n
    if g.size() < max_size:
        # build a list representing C(g) - the edge to be added
        # is one of max_size choices
        if dig:
            children = [[(j,i) for i in xrange(n)] for j in xrange(n)]
        else:
            children = [[(j,i) for i in xrange(j)] for j in xrange(n)]
        # union-find C(g) under Aut(g)
        orbits = range(n)
        for gen in aut_gens:
            for iii in xrange(n):
                if orbits[gen[iii]] != orbits[iii]:
                    temp = orbits[gen[iii]]
                    for jjj in xrange(n):
                        if orbits[jjj] == temp:
                            orbits[jjj] = orbits[iii]
                if dig:
                    jjj_range = range(iii) + range(iii+1, n)
                else:
                    jjj_range = xrange(iii) # iii > jjj
                for jjj in jjj_range:
                    i, j = iii, jjj
                    if dig:
                        x, y = gen[i], gen[j]
                    else:
                        y, x = sorted([gen[i], gen[j]])
                    if children[i][j] != children[x][y]:
                        x_val, y_val = x, y
                        i_val, j_val = i, j
                        if dig:
                            while (x_val, y_val) != children[x_val][y_val]:
                                x_val, y_val = children[x_val][y_val]
                            while (i_val, j_val) != children[i_val][j_val]:
                                i_val, j_val = children[i_val][j_val]
                        else:
                            while (x_val, y_val) != children[x_val][y_val]:
                                y_val, x_val = sorted(children[x_val][y_val])
                            while (i_val, j_val) != children[i_val][j_val]:
                                j_val, i_val = sorted(children[i_val][j_val])
                        while (x, y) != (x_val, y_val):
                            xx, yy = x, y
                            x, y = children[x][y]
                            children[xx][yy] = (x_val, y_val)
                        while (i, j) != (i_val, j_val):
                            ii, jj = i, j
                            i, j = children[i][j]
                            children[ii][jj] = (i_val, j_val)
                        if x < i:
                            children[i][j] = (x, y)
                        elif x > i:
                            children[x][y] = (i, j)
                        elif y < j:
                            children[i][j] = (x, y)
                        elif y > j:
                            children[x][y] = (i, j)
                        else:
                            continue
        # find representatives of orbits of C(g)
        roots = []
        for i in range(n):
            if dig:
                j_range = range(i) + range(i+1, n)
            else:
                j_range = range(i)
            for j in j_range:
                if children[i][j] == (i, j):
                    roots.append((i,j))
        if loops:
            seen = []
            for i in xrange(n):
                if orbits[i] not in seen:
                    roots.append((i,i))
                    seen.append(orbits[i])
        for i, j in roots:
            if g.has_edge(i, j):
                continue
            # construct a z for each edge in roots...
            z = g.copy(implementation=implementation, sparse=sparse)
            z.add_edge(i, j)
            if not property(z):
                continue
            z_aut_gens, _, canonical_relabeling = search_tree(z, [z.vertices()], certify=True, dig=(dig or loops))
            relabel_inverse = [0]*n
            for ii in xrange(n):
                relabel_inverse[canonical_relabeling[ii]] = ii
            z_can = z.relabel(canonical_relabeling, inplace=False)
            cut_edge_can = z_can.edges(labels=False, sort=True)[-1]
            cut_edge = [relabel_inverse[cut_edge_can[0]], relabel_inverse[cut_edge_can[1]]]
            if dig:
                cut_edge = tuple(cut_edge)
            else:
                cut_edge = tuple(sorted(cut_edge))

            from copy import copy
            m_z = copy(z)
            m_z.delete_edge(cut_edge)
            if m_z == g:
                for a in canaug_traverse_edge(z, z_aut_gens, property, dig=dig, loops=loops, implementation=implementation, sparse=sparse):
                    yield a
            else:
                for possibility in check_aut_edge(z_aut_gens, cut_edge, i, j, n, dig=dig):
                    if m_z.relabel(possibility, inplace=False) == g:
                        for a in canaug_traverse_edge(z, z_aut_gens, property, dig=dig, loops=loops, implementation=implementation, sparse=sparse):
                            yield a
                        break

def check_aut_edge(aut_gens, cut_edge, i, j, n, dig=False):
    """
    Helper function for exhaustive generation.

    At the start, check_aut_edge is given a set of generators for the
    automorphism group, aut_gens. We already know we are looking for
    an element of the auto- morphism group that sends cut_edge to {i,
    j}, and check_aut generates these for the canaug_traverse
    function.

    EXAMPLE: Note that the last two entries indicate that none of the
    automorphism group has yet been searched - we are starting at the
    identity [0, 1, 2, 3] and so far that is all we have seen. We
    return automorphisms mapping 2 to 3.

    ::

        sage: from sage.graphs.graph_generators import check_aut
        sage: list( check_aut( [ [0, 3, 2, 1], [1, 0, 3, 2], [2, 1, 0, 3] ], 2, 3))
        [[1, 0, 3, 2], [1, 2, 3, 0]]
    """
    from copy import copy
    perm = range(n)
    seen_perms = [perm]
    unchecked_perms = [perm]
    while len(unchecked_perms) != 0:
        perm = unchecked_perms.pop(0)
        for gen in aut_gens:
            new_perm = copy(perm)
            for ii in xrange(n):
                new_perm[ii] = gen[perm[ii]]
            if new_perm not in seen_perms:
                seen_perms.append(new_perm)
                unchecked_perms.append(new_perm)
                if new_perm[cut_edge[0]] == i and new_perm[cut_edge[1]] == j:
                    yield new_perm
                if not dig and new_perm[cut_edge[0]] == j and new_perm[cut_edge[1]] == i:
                    yield new_perm


# Easy access to the graph generators from the command line:
graphs = GraphGenerators()


####################
# Helper functions #
####################

def _circle_embedding(g, vertices, center=(0, 0), radius=1, shift=0):
    r"""
    Set some vertices on a circle in the embedding of a graph G.

    This method modifies the graph's embedding so that the vertices
    listed in ``vertices`` appear in this ordering on a circle of given
    radius and center. The ``shift`` parameter is actually a rotation of
    the circle. A value of ``shift=1`` will replace in the drawing the
    `i`-th element of the list by the `(i-1)`-th. Non-integer values are
    admissible, and a value of `\alpha` corresponds to a rotation of the
    circle by an angle of `\alpha 2\pi/n` (where `n` is the number of
    vertices set on the circle).

    EXAMPLE::

        sage: from sage.graphs.graph_generators import _circle_embedding
        sage: g = graphs.CycleGraph(5)
        sage: _circle_embedding(g, [0, 2, 4, 1, 3], radius=2, shift=.5)
        sage: g.show()
    """
    c_x, c_y = center
    n = len(vertices)
    d = g.get_pos()
    if d is None:
        d = {}

    for i,v in enumerate(vertices):
        i += shift
        v_x = c_x + radius * cos(2*i*pi / n)
        v_y = c_y + radius * sin(2*i*pi / n)
        d[v] = (v_x, v_y)

    g.set_pos(d)

def _line_embedding(g, vertices, first=(0, 0), last=(0, 1)):
    r"""
    Sets some vertices on a line in the embedding of a graph G.

    This method modifies the graph's embedding so that the vertices of
    ``vertices`` appear on a line, where the position of ``vertices[0]``
    is the pair ``first`` and the position of ``vertices[-1]`` is
    ``last``. The vertices are evenly spaced.

    EXAMPLE::

        sage: from sage.graphs.graph_generators import _line_embedding
        sage: g = graphs.PathGraph(5)
        sage: _line_embedding(g, [0, 2, 4, 1, 3], first=(-1, -1), last=(1, 1))
        sage: g.show()
    """
    n = len(vertices) - 1.

    fx, fy = first
    dx = (last[0] - first[0])/n
    dy = (last[1] - first[1])/n

    d = g.get_pos()
    if d is None:
        d = {}

    for v in vertices:
        d[v] = (fx, fy)
        fx += dx
        fy += dy
