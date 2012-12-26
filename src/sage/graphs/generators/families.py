r"""
Families of graphs
==================

This file gathers generators for some families of graphs.
- :meth:`RingedTree <GraphGenerators.RingedTree>`

AUTHORS:

- David Coudert (2012) Ringed Trees

"""

###########################################################################
#
#           Copyright (C) 2006 Robert L. Miller <rlmillster@gmail.com>
#                              and Emily A. Kirkman
#           Copyright (C) 2009 Michael C. Yurko <myurko@gmail.com>
#
# Distributed  under  the  terms  of  the  GNU  General  Public  License (GPL)
#                         http://www.gnu.org/licenses/
###########################################################################

# import from Sage library
from sage.graphs.graph import Graph
from sage.graphs import graph
from math import sin, cos, pi

def HararyGraph( self, k, n ):
    r"""
    Returns the Harary graph on `n` vertices and connectivity `k`, where
    `2 \leq k < n`.

    A `k`-connected graph `G` on `n` vertices requires the minimum degree
    `\delta(G)\geq k`, so the minimum number of edges `G` should have is
    `\lceil kn/2\rceil`. Harary graphs achieve this lower bound, that is,
    Harary graphs are minimal `k`-connected graphs on `n` vertices.

    The construction provided uses the method CirculantGraph.  For more
    details, see the book D. B. West, Introduction to Graph Theory, 2nd
    Edition, Prentice Hall, 2001, p. 150--151; or the `MathWorld article on
    Harary graphs <http://mathworld.wolfram.com/HararyGraph.html>`_.

    EXAMPLES:

    Harary graphs `H_{k,n}`::

        sage: h = graphs.HararyGraph(5,9); h
        Harary graph 5, 9: Graph on 9 vertices
        sage: h.order()
        9
        sage: h.size()
        23
        sage: h.vertex_connectivity()
        5

    TESTS:

    Connectivity of some Harary graphs::

        sage: n=10
        sage: for k in range(2,n):
        ...       g = graphs.HararyGraph(k,n)
        ...       if k != g.vertex_connectivity():
        ...          print "Connectivity of Harary graphs not satisfied."
    """
    if k < 2:
        raise ValueError("Connectivity parameter k should be at least 2.")
    if k >= n:
        raise ValueError("Number of vertices n should be greater than k.")

    if k%2 == 0:
        G = self.CirculantGraph( n, range(1,k/2+1) )
    else:
        if n%2 == 0:
            G = self.CirculantGraph( n, range(1,(k-1)/2+1) )
            for i in range(n):
                G.add_edge( i, (i+n/2)%n )
        else:
            G = self.HararyGraph( k-1, n )
            for i in range((n-1)/2+1):
                G.add_edge( i, (i+(n-1)/2)%n )
    G.name('Harary graph {0}, {1}'.format(k,n))
    return G

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

def MycielskiGraph(self, k=1, relabel=True):
    r"""
    Returns the `k`-th Mycielski Graph.

    The graph `M_k` is triangle-free and has chromatic number
    equal to `k`. These graphs show, constructively, that there
    are triangle-free graphs with arbitrarily high chromatic
    number.

    The Mycielski graphs are built recursively starting with
    `M_0`, an empty graph; `M_1`, a single vertex graph; and `M_2`
    is the graph `K_2`.  `M_{k+1}` is then built from `M_k`
    as follows:

    If the vertices of `M_k` are `v_1,\ldots,v_n`, then the
    vertices of `M_{k+1}` are
    `v_1,\ldots,v_n,w_1,\ldots,w_n,z`. Vertices `v_1,\ldots,v_n`
    induce a copy of `M_k`. Vertices `w_1,\ldots,w_n` are an
    independent set. Vertex `z` is adjacent to all the
    `w_i`-vertices. Finally, vertex `w_i` is adjacent to vertex
    `v_j` iff `v_i` is adjacent to `v_j`.

    INPUT:

    - ``k`` Number of steps in the construction process.

    - ``relabel`` Relabel the vertices so their names are the integers
      ``range(n)`` where ``n`` is the number of vertices in the graph.

    EXAMPLE:

    The Mycielski graph `M_k` is triangle-free and has chromatic
    number equal to `k`. ::

        sage: g = graphs.MycielskiGraph(5)
        sage: g.is_triangle_free()
        True
        sage: g.chromatic_number()
        5

    The graphs `M_4` is (isomorphic to) the Grotzsch graph. ::

        sage: g = graphs.MycielskiGraph(4)
        sage: g.is_isomorphic(graphs.GrotzschGraph())
        True

    REFERENCES:

    -  [1] Weisstein, Eric W. "Mycielski Graph."
       From MathWorld--A Wolfram Web Resource.
       http://mathworld.wolfram.com/MycielskiGraph.html

    """
    g = graph.Graph()
    g.name("Mycielski Graph " + str(k))

    if k<0:
        raise ValueError, "parameter k must be a nonnegative integer"

    if k == 0:
        return g

    if k == 1:
        g.add_vertex(0)
        return g

    if k == 2:
        g.add_edge(0,1)
        return g

    g0 = MycielskiGraph(self,k-1)
    g = MycielskiStep(self,g0)
    g.name("Mycielski Graph " + str(k))
    if relabel: g.relabel()

    return g

def MycielskiStep(self, g):
    r"""
    Perform one iteration of the Mycielski construction.

    See the documentation for ``MycielskiGraph`` which uses this
    method. We expose it to all users in case they may find it
    useful.

    EXAMPLE. One iteration of the Mycielski step applied to the
    5-cycle yields a graph isomorphic to the Grotzsch graph ::

        sage: g = graphs.CycleGraph(5)
        sage: h = graphs.MycielskiStep(g)
        sage: h.is_isomorphic(graphs.GrotzschGraph())
        True
    """

    # Make a copy of the input graph g
    gg = g.copy()

    # rename a vertex v of gg as (1,v)
    renamer = dict( [ (v, (1,v)) for v in g.vertices() ] )
    gg.relabel(renamer)

    # add the w vertices to gg as (2,v)
    wlist = [ (2,v) for v in g.vertices() ]
    gg.add_vertices(wlist)

    # add the z vertex as (0,0)
    gg.add_vertex((0,0))

    # add the edges from z to w_i
    gg.add_edges( [ ( (0,0) , (2,v) ) for v in g.vertices() ] )

    # make the v_i w_j edges
    for v in g.vertices():
        gg.add_edges( [ ((1,v),(2,vv)) for vv in g.neighbors(v) ] )

    return gg


def KneserGraph(self,n,k):
    r"""
    Returns the Kneser Graph with parameters `n, k`.

    The Kneser Graph with parameters `n,k` is the graph
    whose vertices are the `k`-subsets of `[0,1,\dots,n-1]`, and such
    that two vertices are adjacent if their corresponding sets
    are disjoint.

    For example, the Petersen Graph can be defined
    as the Kneser Graph with parameters `5,2`.

    EXAMPLE::

        sage: KG=graphs.KneserGraph(5,2)
        sage: print KG.vertices()
        [{4, 5}, {1, 3}, {2, 5}, {2, 3}, {3, 4}, {3, 5}, {1, 4}, {1, 5}, {1, 2}, {2, 4}]
        sage: P=graphs.PetersenGraph()
        sage: P.is_isomorphic(KG)
        True

    TESTS::

        sage: KG=graphs.KneserGraph(0,0)
        Traceback (most recent call last):
        ...
        ValueError: Parameter n should be a strictly positive integer
        sage: KG=graphs.KneserGraph(5,6)
        Traceback (most recent call last):
        ...
        ValueError: Parameter k should be a strictly positive integer inferior to n
    """

    if not n>0:
        raise ValueError, "Parameter n should be a strictly positive integer"
    if not (k>0 and k<=n):
        raise ValueError, "Parameter k should be a strictly positive integer inferior to n"

    g=graph.Graph(name="Kneser graph with parameters "+str(n)+","+str(k))
    from sage.combinat.subset import Subsets

    if k>n/2:
        g.add_vertices(Subsets(n,k).list())

    S = Subsets(n,k)
    for s in S:
        for t in Subsets(S.s.difference(s),k):
            g.add_edge(s,t)

    return g


###########################################################################
#   Families of Graphs
###########################################################################

def BalancedTree(self, r, h):
    r"""
    Returns the perfectly balanced tree of height `h \geq 1`,
    whose root has degree `r \geq 2`.

    The number of vertices of this graph is
    `1 + r + r^2 + \cdots + r^h`, that is,
    `\frac{r^{h+1} - 1}{r - 1}`. The number of edges is one
    less than the number of vertices.

    INPUT:

    - ``r`` -- positive integer `\geq 2`. The degree of the root node.

    - ``h`` -- positive integer `\geq 1`. The height of the balanced tree.

    OUTPUT:

    The perfectly balanced tree of height `h \geq 1` and whose root has
    degree `r \geq 2`. A ``NetworkXError`` is returned if `r < 2` or
    `h < 1`.

    ALGORITHM:

    Uses `NetworkX <http://networkx.lanl.gov>`_.

    EXAMPLES:

    A balanced tree whose root node has degree `r = 2`, and of height
    `h = 1`, has order 3 and size 2::

        sage: G = graphs.BalancedTree(2, 1); G
        Balanced tree: Graph on 3 vertices
        sage: G.order(); G.size()
        3
        2
        sage: r = 2; h = 1
        sage: v = 1 + r
        sage: v; v - 1
        3
        2

    Plot a balanced tree of height 5, whose root node has degree `r = 3`::

        sage: G = graphs.BalancedTree(3, 5)
        sage: G.show()   # long time

    A tree is bipartite. If its vertex set is finite, then it is planar. ::

        sage: r = randint(2, 5); h = randint(1, 7)
        sage: T = graphs.BalancedTree(r, h)
        sage: T.is_bipartite()
        True
        sage: T.is_planar()
        True
        sage: v = (r^(h + 1) - 1) / (r - 1)
        sage: T.order() == v
        True
        sage: T.size() == v - 1
        True

    TESTS:

     Normally we would only consider balanced trees whose root node
     has degree `r \geq 2`, but the construction degenerates
     gracefully::

        sage: graphs.BalancedTree(1, 10)
        Balanced tree: Graph on 2 vertices

        sage: graphs.BalancedTree(-1, 10)
        Balanced tree: Graph on 1 vertex

    Similarly, we usually want the tree must have height `h \geq 1`
    but the algorithm also degenerates gracefully here::

        sage: graphs.BalancedTree(3, 0)
        Balanced tree: Graph on 1 vertex

        sage: graphs.BalancedTree(5, -2)
        Balanced tree: Graph on 0 vertices

        sage: graphs.BalancedTree(-2,-2)
        Balanced tree: Graph on 0 vertices
    """
    import networkx
    return graph.Graph(networkx.balanced_tree(r, h), name="Balanced tree")

def BubbleSortGraph(self, n):
    r"""
    Returns the bubble sort graph `B(n)`.

    The vertices of the bubble sort graph are the set of permutations on
    `n` symbols. Two vertices are adjacent if one can be obtained from the
    other by swapping the labels in the `i`-th and `(i+1)`-th positions for
    `1 \leq i \leq n-1`. In total, `B(n)` has order `n!`. Thus, the order
    of `B(n)` increases according to `f(n) = n!`.

    INPUT:

    - ``n`` -- positive integer. The number of symbols to permute.

    OUTPUT:

    The bubble sort graph `B(n)` on `n` symbols. If `n < 1`, a
    ``ValueError`` is returned.

    EXAMPLES::

        sage: g = graphs.BubbleSortGraph(4); g
        Bubble sort: Graph on 24 vertices
        sage: g.plot() # long time

    The bubble sort graph on `n = 1` symbol is the trivial graph `K_1`::

        sage: graphs.BubbleSortGraph(1)
        Bubble sort: Graph on 1 vertex

    If `n \geq 1`, then the order of `B(n)` is `n!`::

        sage: n = randint(1, 8)
        sage: g = graphs.BubbleSortGraph(n)
        sage: g.order() == factorial(n)
        True

    TESTS:

    Input ``n`` must be positive::

        sage: graphs.BubbleSortGraph(0)
        Traceback (most recent call last):
        ...
        ValueError: Invalid number of symbols to permute, n should be >= 1
        sage: graphs.BubbleSortGraph(randint(-10^6, 0))
        Traceback (most recent call last):
        ...
        ValueError: Invalid number of symbols to permute, n should be >= 1

    AUTHORS:

    - Michael Yurko (2009-09-01)
    """
    # sanity checks
    if n < 1:
        raise ValueError(
            "Invalid number of symbols to permute, n should be >= 1")
    if n == 1:
        return graph.Graph(self.CompleteGraph(n), name="Bubble sort")
    from sage.combinat.permutation import Permutations
    #create set from which to permute
    label_set = [str(i) for i in xrange(1, n + 1)]
    d = {}
    #iterate through all vertices
    for v in Permutations(label_set):
        tmp_dict = {}
        #add all adjacencies
        for i in xrange(n - 1):
            #swap entries
            v[i], v[i + 1] = v[i + 1], v[i]
            #add new vertex
            new_vert = ''.join(v)
            tmp_dict[new_vert] = None
            #swap back
            v[i], v[i + 1] = v[i + 1], v[i]
        #add adjacency dict
        d[''.join(v)] = tmp_dict
    return graph.Graph(d, name="Bubble sort")

def CirculantGraph(self, n, adjacency):
    r"""
    Returns a circulant graph with n nodes.

    A circulant graph has the property that the vertex i is connected
    with the vertices i+j and i-j for each j in adj.

    INPUT:


    -  ``n`` - number of vertices in the graph

    -  ``adjacency`` - the list of j values


    PLOTTING: Upon construction, the position dictionary is filled to
    override the spring-layout algorithm. By convention, each circulant
    graph will be displayed with the first (0) node at the top, with
    the rest following in a counterclockwise manner.

    Filling the position dictionary in advance adds O(n) to the
    constructor.

    EXAMPLES: Compare plotting using the predefined layout and
    networkx::

        sage: import networkx
        sage: n = networkx.cycle_graph(23)
        sage: spring23 = Graph(n)
        sage: posdict23 = graphs.CirculantGraph(23,2)
        sage: spring23.show() # long time
        sage: posdict23.show() # long time

    We next view many cycle graphs as a Sage graphics array. First we
    use the ``CirculantGraph`` constructor, which fills in
    the position dictionary::

        sage: g = []
        sage: j = []
        sage: for i in range(9):
        ...    k = graphs.CirculantGraph(i+3,i)
        ...    g.append(k)
        ...
        sage: for i in range(3):
        ...    n = []
        ...    for m in range(3):
        ...        n.append(g[3*i + m].plot(vertex_size=50, vertex_labels=False))
        ...    j.append(n)
        ...
        sage: G = sage.plot.graphics.GraphicsArray(j)
        sage: G.show() # long time

    Compare to plotting with the spring-layout algorithm::

        sage: g = []
        sage: j = []
        sage: for i in range(9):
        ...    spr = networkx.cycle_graph(i+3)
        ...    k = Graph(spr)
        ...    g.append(k)
        ...
        sage: for i in range(3):
        ...    n = []
        ...    for m in range(3):
        ...        n.append(g[3*i + m].plot(vertex_size=50, vertex_labels=False))
        ...    j.append(n)
        ...
        sage: G = sage.plot.graphics.GraphicsArray(j)
        sage: G.show() # long time

    Passing a 1 into adjacency should give the cycle.

    ::

        sage: graphs.CirculantGraph(6,1)==graphs.CycleGraph(6)
        True
        sage: graphs.CirculantGraph(7,[1,3]).edges(labels=false)
        [(0, 1),
        (0, 3),
        (0, 4),
        (0, 6),
        (1, 2),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 5),
        (2, 6),
        (3, 4),
        (3, 6),
        (4, 5),
        (5, 6)]
    """
    if not isinstance(adjacency,list):
        adjacency=[adjacency]
    pos_dict = {}
    for i in range(n):
        x = float(cos((pi/2) + ((2*pi)/n)*i))
        y = float(sin((pi/2) + ((2*pi)/n)*i))
        pos_dict[i] = (x,y)
    G=graph.Graph(n, name="Circulant graph ("+str(adjacency)+")")
    G._pos=pos_dict
    for v in G:
        G.add_edges([(v,(v+j)%n) for j in adjacency])
        G.add_edges([(v,(v-j)%n) for j in adjacency])
    return G

def CompleteGraph(self, n):
    """
    Returns a complete graph on n nodes.

    A Complete Graph is a graph in which all nodes are connected to all
    other nodes.

    This constructor is dependent on vertices numbered 0 through n-1 in
    NetworkX complete_graph()

    PLOTTING: Upon construction, the position dictionary is filled to
    override the spring-layout algorithm. By convention, each complete
    graph will be displayed with the first (0) node at the top, with
    the rest following in a counterclockwise manner.

    In the complete graph, there is a big difference visually in using
    the spring-layout algorithm vs. the position dictionary used in
    this constructor. The position dictionary flattens the graph,
    making it clear which nodes an edge is connected to. But the
    complete graph offers a good example of how the spring-layout
    works. The edges push outward (everything is connected), causing
    the graph to appear as a 3-dimensional pointy ball. (See examples
    below).

    EXAMPLES: We view many Complete graphs with a Sage Graphics Array,
    first with this constructor (i.e., the position dictionary
    filled)::

        sage: g = []
        sage: j = []
        sage: for i in range(9):
        ...    k = graphs.CompleteGraph(i+3)
        ...    g.append(k)
        ...
        sage: for i in range(3):
        ...    n = []
        ...    for m in range(3):
        ...        n.append(g[3*i + m].plot(vertex_size=50, vertex_labels=False))
        ...    j.append(n)
        ...
        sage: G = sage.plot.graphics.GraphicsArray(j)
        sage: G.show() # long time

    We compare to plotting with the spring-layout algorithm::

        sage: import networkx
        sage: g = []
        sage: j = []
        sage: for i in range(9):
        ...    spr = networkx.complete_graph(i+3)
        ...    k = Graph(spr)
        ...    g.append(k)
        ...
        sage: for i in range(3):
        ...    n = []
        ...    for m in range(3):
        ...        n.append(g[3*i + m].plot(vertex_size=50, vertex_labels=False))
        ...    j.append(n)
        ...
        sage: G = sage.plot.graphics.GraphicsArray(j)
        sage: G.show() # long time

    Compare the constructors (results will vary)

    ::

        sage: import networkx
        sage: t = cputime()
        sage: n = networkx.complete_graph(389); spring389 = Graph(n)
        sage: cputime(t)           # random
        0.59203700000000126
        sage: t = cputime()
        sage: posdict389 = graphs.CompleteGraph(389)
        sage: cputime(t)           # random
        0.6680419999999998

    We compare plotting::

        sage: import networkx
        sage: n = networkx.complete_graph(23)
        sage: spring23 = Graph(n)
        sage: posdict23 = graphs.CompleteGraph(23)
        sage: spring23.show() # long time
        sage: posdict23.show() # long time
    """
    pos_dict = {}
    for i in range(n):
        x = float(cos((pi/2) + ((2*pi)/n)*i))
        y = float(sin((pi/2) + ((2*pi)/n)*i))
        pos_dict[i] = (x,y)
    import networkx
    G = networkx.complete_graph(n)
    return graph.Graph(G, pos=pos_dict, name="Complete graph")

def CompleteBipartiteGraph(self, n1, n2):
    """
    Returns a Complete Bipartite Graph sized n1+n2, with each of the
    nodes [0,(n1-1)] connected to each of the nodes [n1,(n2-1)] and
    vice versa.

    A Complete Bipartite Graph is a graph with its vertices partitioned
    into two groups, V1 and V2. Each v in V1 is connected to every v in
    V2, and vice versa.

    PLOTTING: Upon construction, the position dictionary is filled to
    override the spring-layout algorithm. By convention, each complete
    bipartite graph will be displayed with the first n1 nodes on the
    top row (at y=1) from left to right. The remaining n2 nodes appear
    at y=0, also from left to right. The shorter row (partition with
    fewer nodes) is stretched to the same length as the longer row,
    unless the shorter row has 1 node; in which case it is centered.
    The x values in the plot are in domain [0,maxn1,n2].

    In the Complete Bipartite graph, there is a visual difference in
    using the spring-layout algorithm vs. the position dictionary used
    in this constructor. The position dictionary flattens the graph and
    separates the partitioned nodes, making it clear which nodes an
    edge is connected to. The Complete Bipartite graph plotted with the
    spring-layout algorithm tends to center the nodes in n1 (see
    spring_med in examples below), thus overlapping its nodes and
    edges, making it typically hard to decipher.

    Filling the position dictionary in advance adds O(n) to the
    constructor. Feel free to race the constructors below in the
    examples section. The much larger difference is the time added by
    the spring-layout algorithm when plotting. (Also shown in the
    example below). The spring model is typically described as
    `O(n^3)`, as appears to be the case in the NetworkX source
    code.

    EXAMPLES: Two ways of constructing the complete bipartite graph,
    using different layout algorithms::

        sage: import networkx
        sage: n = networkx.complete_bipartite_graph(389,157); spring_big = Graph(n)   # long time
        sage: posdict_big = graphs.CompleteBipartiteGraph(389,157)                    # long time

    Compare the plotting::

        sage: n = networkx.complete_bipartite_graph(11,17)
        sage: spring_med = Graph(n)
        sage: posdict_med = graphs.CompleteBipartiteGraph(11,17)

    Notice here how the spring-layout tends to center the nodes of n1

    ::

        sage: spring_med.show() # long time
        sage: posdict_med.show() # long time

    View many complete bipartite graphs with a Sage Graphics Array,
    with this constructor (i.e., the position dictionary filled)::

        sage: g = []
        sage: j = []
        sage: for i in range(9):
        ...    k = graphs.CompleteBipartiteGraph(i+1,4)
        ...    g.append(k)
        ...
        sage: for i in range(3):
        ...    n = []
        ...    for m in range(3):
        ...        n.append(g[3*i + m].plot(vertex_size=50, vertex_labels=False))
        ...    j.append(n)
        ...
        sage: G = sage.plot.graphics.GraphicsArray(j)
        sage: G.show() # long time

    We compare to plotting with the spring-layout algorithm::

        sage: g = []
        sage: j = []
        sage: for i in range(9):
        ...    spr = networkx.complete_bipartite_graph(i+1,4)
        ...    k = Graph(spr)
        ...    g.append(k)
        ...
        sage: for i in range(3):
        ...    n = []
        ...    for m in range(3):
        ...        n.append(g[3*i + m].plot(vertex_size=50, vertex_labels=False))
        ...    j.append(n)
        ...
        sage: G = sage.plot.graphics.GraphicsArray(j)
        sage: G.show() # long time

    Trac ticket #12155::

        sage: graphs.CompleteBipartiteGraph(5,6).complement()
        complement(Complete bipartite graph): Graph on 11 vertices
    """
    pos_dict = {}
    c1 = 1 # scaling factor for top row
    c2 = 1 # scaling factor for bottom row
    c3 = 0 # pad to center if top row has 1 node
    c4 = 0 # pad to center if bottom row has 1 node
    if n1 > n2:
        if n2 == 1:
            c4 = (n1-1)/2
        else:
            c2 = ((n1-1)/(n2-1))
    elif n2 > n1:
        if n1 == 1:
            c3 = (n2-1)/2
        else:
            c1 = ((n2-1)/(n1-1))
    for i in range(n1):
        x = c1*i + c3
        y = 1
        pos_dict[i] = (x,y)
    for i in range(n1+n2)[n1:]:
        x = c2*(i-n1) + c4
        y = 0
        pos_dict[i] = (x,y)
    import networkx
    from sage.graphs.graph import Graph
    G = networkx.complete_bipartite_graph(n1,n2)
    return Graph(G, pos=pos_dict, name="Complete bipartite graph")

def CompleteMultipartiteGraph(self, l):
    r"""
    Returns a complete multipartite graph.

    INPUT:

    - ``l`` -- a list of integers : the respective sizes
      of the components.

    EXAMPLE:

    A complete tripartite graph with sets of sizes
    `5, 6, 8`::

        sage: g = graphs.CompleteMultipartiteGraph([5, 6, 8]); g
        Multipartite Graph with set sizes [5, 6, 8]: Graph on 19 vertices

    It clearly has a chromatic number of 3::

        sage: g.chromatic_number()
        3
    """

    from sage.graphs.graph import Graph
    g = Graph()
    for i in l:
        g = g + self.CompleteGraph(i)

    g = g.complement()
    g.name("Multipartite Graph with set sizes "+str(l))

    return g

def CubeGraph(self, n):
    r"""
    Returns the hypercube in `n` dimensions.

    The hypercube in `n` dimension is build upon the binary
    strings on `n` bits, two of them being adjacent if
    they differ in exactly one bit. Hence, the distance
    between two vertices in the hypercube is the Hamming
    distance.

    EXAMPLES:

    The distance between `0100110` and `1011010` is
    `5`, as expected ::

        sage: g = graphs.CubeGraph(7)
        sage: g.distance('0100110','1011010')
        5

    Plot several `n`-cubes in a Sage Graphics Array ::

        sage: g = []
        sage: j = []
        sage: for i in range(6):
        ...    k = graphs.CubeGraph(i+1)
        ...    g.append(k)
        ...
        sage: for i in range(2):
        ...    n = []
        ...    for m in range(3):
        ...        n.append(g[3*i + m].plot(vertex_size=50, vertex_labels=False))
        ...    j.append(n)
        ...
        sage: G = sage.plot.graphics.GraphicsArray(j)
        sage: G.show(figsize=[6,4]) # long time

    Use the plot options to display larger `n`-cubes

    ::

        sage: g = graphs.CubeGraph(9)
        sage: g.show(figsize=[12,12],vertex_labels=False, vertex_size=20) # long time

    AUTHORS:

    - Robert Miller
    """
    theta = float(pi/n)

    d = {'':[]}
    dn={}
    p = {'':(float(0),float(0))}
    pn={}

    # construct recursively the adjacency dict and the positions
    for i in xrange(n):
        ci = float(cos(i*theta))
        si = float(sin(i*theta))
        for v,e in d.iteritems():
            v0 = v+'0'
            v1 = v+'1'
            l0 = [v1]
            l1 = [v0]
            for m in e:
                l0.append(m+'0')
                l1.append(m+'1')
            dn[v0] = l0
            dn[v1] = l1
            x,y = p[v]
            pn[v0] = (x, y)
            pn[v1] = (x+ci, y+si)
        d,dn = dn,{}
        p,pn = pn,{}

    # construct the graph
    r = graph.Graph(name="%d-Cube"%n)
    r.add_vertices(d.keys())
    for u,L in d.iteritems():
        for v in L:
            r.add_edge(u,v)
    r.set_pos(p)

    return r

def FriendshipGraph(self, n):
    r"""
    Returns the friendship graph `F_n`.

    The friendship graph is also known as the Dutch windmill graph. Let
    `C_3` be the cycle graph on 3 vertices. Then `F_n` is constructed by
    joining `n \geq 1` copies of `C_3` at a common vertex. If `n = 1`,
    then `F_1` is isomorphic to `C_3` (the triangle graph). If `n = 2`,
    then `F_2` is the butterfly graph, otherwise known as the bowtie
    graph. For more information, see this
    `Wikipedia article on the friendship graph <http://en.wikipedia.org/wiki/Friendship_graph>`_.

    INPUT:

    - ``n`` -- positive integer; the number of copies of `C_3` to use in
      constructing `F_n`.

    OUTPUT:

    - The friendship graph `F_n` obtained from `n` copies of the cycle
      graph `C_3`.

    .. seealso::

        - :meth:`GraphGenerators.ButterflyGraph`

    EXAMPLES:

    The first few friendship graphs. ::

        sage: A = []; B = []
        sage: for i in range(9):
        ...       g = graphs.FriendshipGraph(i + 1)
        ...       A.append(g)
        sage: for i in range(3):
        ...       n = []
        ...       for j in range(3):
        ...           n.append(A[3*i + j].plot(vertex_size=20, vertex_labels=False))
        ...       B.append(n)
        sage: G = sage.plot.graphics.GraphicsArray(B)
        sage: G.show()  # long time

    For `n = 1`, the friendship graph `F_1` is isomorphic to the cycle
    graph `C_3`, whose visual representation is a triangle. ::

        sage: G = graphs.FriendshipGraph(1); G
        Friendship graph: Graph on 3 vertices
        sage: G.show()  # long time
        sage: G.is_isomorphic(graphs.CycleGraph(3))
        True

    For `n = 2`, the friendship graph `F_2` is isomorphic to the
    butterfly graph, otherwise known as the bowtie graph. ::

        sage: G = graphs.FriendshipGraph(2); G
        Friendship graph: Graph on 5 vertices
        sage: G.is_isomorphic(graphs.ButterflyGraph())
        True

    If `n \geq 1`, then the friendship graph `F_n` has `2n + 1` vertices
    and `3n` edges. It has radius 1, diameter 2, girth 3, and
    chromatic number 3. Furthermore, `F_n` is planar and Eulerian. ::

        sage: n = randint(1, 10^3)
        sage: G = graphs.FriendshipGraph(n)
        sage: G.order() == 2*n + 1
        True
        sage: G.size() == 3*n
        True
        sage: G.radius()
        1
        sage: G.diameter()
        2
        sage: G.girth()
        3
        sage: G.chromatic_number()
        3
        sage: G.is_planar()
        True
        sage: G.is_eulerian()
        True

    TESTS:

    The input ``n`` must be a positive integer. ::

        sage: graphs.FriendshipGraph(randint(-10^5, 0))
        Traceback (most recent call last):
        ...
        ValueError: n must be a positive integer
    """
    # sanity checks
    if n < 1:
        raise ValueError("n must be a positive integer")
    # construct the friendship graph
    if n == 1:
        G = self.CycleGraph(3)
        G.name("Friendship graph")
        return G
    # build the edge and position dictionaries
    from sage.functions.trig import cos, sin
    from sage.rings.real_mpfr import RR
    from sage.symbolic.constants import pi
    N = 2*n + 1           # order of F_n
    d = (2*pi) / (N - 1)  # angle between external nodes
    edge_dict = {}
    pos_dict = {}
    for i in range(N - 2):
        if i & 1:  # odd numbered node
            edge_dict.setdefault(i, [i + 1, N - 1])
        else:      # even numbered node
            edge_dict.setdefault(i, [N - 1])
        pos_dict.setdefault(i, [RR(cos(i*d)), RR(sin(i*d))])
    edge_dict.setdefault(N - 2, [0, N - 1])
    pos_dict.setdefault(N - 2, [RR(cos(d * (N-2))), RR(sin(d * (N-2)))])
    pos_dict.setdefault(N - 1, [0, 0])
    return graph.Graph(edge_dict, pos=pos_dict, name="Friendship graph")

def FuzzyBallGraph(self, partition, q):
    r"""
    Construct a Fuzzy Ball graph with the integer partition
    ``partition`` and ``q`` extra vertices.

    Let `q` be an integer and let `m_1,m_2,...,m_k` be a set of positive
    integers.  Let `n=q+m_1+...+m_k`.  The Fuzzy Ball graph with partition
    `m_1,m_2,...,m_k` and `q` extra vertices is the graph constructed from the
    graph `G=K_n` by attaching, for each `i=1,2,...,k`, a new vertex `a_i` to
    `m_i` distinct vertices of `G`.

    For given positive integers `k` and `m` and nonnegative
    integer `q`, the set of graphs ``FuzzyBallGraph(p, q)`` for
    all partitions `p` of `m` with `k` parts are cospectral with
    respect to the normalized Laplacian.

    EXAMPLES::

        sage: graphs.FuzzyBallGraph([3,1],2).adjacency_matrix()
        [0 1 1 1 1 1 1 0]
        [1 0 1 1 1 1 1 0]
        [1 1 0 1 1 1 1 0]
        [1 1 1 0 1 1 0 1]
        [1 1 1 1 0 1 0 0]
        [1 1 1 1 1 0 0 0]
        [1 1 1 0 0 0 0 0]
        [0 0 0 1 0 0 0 0]


    Pick positive integers `m` and `k` and a nonnegative integer `q`.
    All the FuzzyBallGraphs constructed from partitions of `m` with
    `k` parts should be cospectral with respect to the normalized
    Laplacian::

        sage: m=4; q=2; k=2
        sage: g_list=[graphs.FuzzyBallGraph(p,q) for p in Partitions(m, length=k)]
        sage: set([g.laplacian_matrix(normalized=True).charpoly() for g in g_list])  # long time (7s on sage.math, 2011)
        set([x^8 - 8*x^7 + 4079/150*x^6 - 68689/1350*x^5 + 610783/10800*x^4 - 120877/3240*x^3 + 1351/100*x^2 - 931/450*x])
    """
    if len(partition)<1:
        raise ValueError, "partition must be a nonempty list of positive integers"
    n=q+sum(partition)
    g=CompleteGraph(self,n)
    curr_vertex=0
    for e,p in enumerate(partition):
        g.add_edges([(curr_vertex+i, 'a{0}'.format(e+1)) for i in range(p)])
        curr_vertex+=p
    return g

def FibonacciTree(self, n):
    r"""
    Returns the graph of the Fibonacci Tree `F_{i}` of order `n`.
    `F_{i}` is recursively defined as the a tree with a root vertex
    and two attached child trees `F_{i-1}` and `F_{i-2}`, where
    `F_{1}` is just one vertex and `F_{0}` is empty.

    INPUT:

    - ``n`` - the recursion depth of the Fibonacci Tree

    EXAMPLES::

        sage: g = graphs.FibonacciTree(3)
        sage: g.is_tree()
        True

    ::

        sage: l1 = [ len(graphs.FibonacciTree(_)) + 1 for _ in range(6) ]
        sage: l2 = list(fibonacci_sequence(2,8))
        sage: l1 == l2
        True

    AUTHORS:

    - Harald Schilly and Yann Laigle-Chapuy (2010-03-25)
    """
    T = graph.Graph(name="Fibonacci-Tree-%d"%n)
    if n == 1: T.add_vertex(0)
    if n < 2: return T

    from sage.combinat.combinat import fibonacci_sequence
    F = list(fibonacci_sequence(n + 2))
    s = 1.618 ** (n / 1.618 - 1.618)
    pos = {}

    def fib(level, node, y):
        pos[node] = (node, y)
        if level < 2: return
        level -= 1
        y -= s
        diff = F[level]
        T.add_edge(node, node - diff)
        if level == 1: # only one child
            pos[node - diff] = (node, y)
            return
        T.add_edge(node, node + diff)
        fib(level, node - diff, y)
        fib(level - 1, node + diff, y)

    T.add_vertices(xrange(sum(F[:-1])))
    fib(n, F[n + 1] - 1, 0)
    T.set_pos(pos)

    return T

def GeneralizedPetersenGraph(self, n,k):
    r"""
    Returns a generalized Petersen graph with `2n` nodes. The variables
    `n`, `k` are integers such that `n>2` and `0<k\leq\lfloor(n-1)`/`2\rfloor`

    For `k=1` the result is a graph isomorphic to the circular ladder graph
    with the same `n`. The regular Petersen Graph has `n=5` and `k=2`.
    Other named graphs that can be described using this notation include
    the Desargues graph and the Moebius-Kantor graph.

    INPUT:

    - ``n`` - the number of nodes is `2*n`.

    - ``k`` - integer `0<k\leq\lfloor(n-1)`/`2\rfloor`. Decides
      how inner vertices are connected.

    PLOTTING: Upon construction, the position dictionary is filled to
    override the spring-layout algorithm. By convention, the generalized
    Petersen graphs are displayed as an inner and outer cycle pair, with
    the first n nodes drawn on the outer circle. The first (0) node is
    drawn at the top of the outer-circle, moving counterclockwise after that.
    The inner circle is drawn with the (n)th node at the top, then
    counterclockwise as well.

    EXAMPLES: For `k=1` the resulting graph will be isomorphic to a circular
    ladder graph. ::

        sage: g = graphs.GeneralizedPetersenGraph(13,1)
        sage: g2 = graphs.CircularLadderGraph(13)
        sage: g.is_isomorphic(g2)
        True

    The Desargues graph::

        sage: g = graphs.GeneralizedPetersenGraph(10,3)
        sage: g.girth()
        6
        sage: g.is_bipartite()
        True

    AUTHORS:

    - Anders Jonsson (2009-10-15)
    """
    if (n < 3):
            raise ValueError("n must be larger than 2")
    if (k < 1 or k>((n-1)/2)):
            raise ValueError("k must be in 1<= k <=floor((n-1)/2)")
    pos_dict = {}
    G=Graph()
    for i in range(n):
        x = float(cos((pi/2) + ((2*pi)/n)*i))
        y = float(sin((pi/2) + ((2*pi)/n)*i))
        pos_dict[i] = (x,y)
    for i in range(n, 2*n):
        x = float(0.5*cos((pi/2) + ((2*pi)/n)*i))
        y = float(0.5*sin((pi/2) + ((2*pi)/n)*i))
        pos_dict[i] = (x,y)
    for i in range(n):
        G.add_edge(i, (i+1) % n)
        G.add_edge(i, i+n)
        G.add_edge(i+n, n + (i+k) % n)
    return graph.Graph(G, pos=pos_dict, name="Generalized Petersen graph (n="+str(n)+",k="+str(k)+")")

def HyperStarGraph(self,n,k):
    r"""
    Returns the hyper-star graph HS(n,k).

    The vertices of the hyper-star graph are the set of binary strings
    of length n which contain k 1s. Two vertices, u and v, are adjacent
    only if u can be obtained from v by swapping the first bit with a
    different symbol in another position.

    INPUT:

    -  ``n``

    -  ``k``

    EXAMPLES::

        sage: g = graphs.HyperStarGraph(6,3)
        sage: g.plot() # long time

    REFERENCES:

    - Lee, Hyeong-Ok, Jong-Seok Kim, Eunseuk Oh, and Hyeong-Seok Lim.
      "Hyper-Star Graph: A New Interconnection Network Improving the
      Network Cost of the Hypercube." In Proceedings of the First EurAsian
      Conference on Information and Communication Technology, 858-865.
      Springer-Verlag, 2002.

    AUTHORS:

    - Michael Yurko (2009-09-01)
    """
    from sage.combinat.combination import Combinations
    # dictionary associating the positions of the 1s to the corresponding
    # string: e.g. if n=6 and k=3, comb_to_str([0,1,4])=='110010'
    comb_to_str={}
    for c in Combinations(n,k):
        L = ['0']*n
        for i in c:
            L[i]='1'
        comb_to_str[tuple(c)] = ''.join(L)

    g=graph.Graph(name="HS(%d,%d)"%(n,k))
    g.add_vertices(comb_to_str.values())

    for c in Combinations(range(1,n),k): # 0 is not in c
        L = []
        u = comb_to_str[tuple(c)]
        # switch 0 with the 1s
        for i in xrange(len(c)):
            v = tuple([0]+c[:i]+c[i+1:])
            g.add_edge( u , comb_to_str[v] )

    return g

def LCFGraph(self, n, shift_list, repeats):
    """
    Returns the cubic graph specified in LCF notation.

    LCF (Lederberg-Coxeter-Fruchte) notation is a concise way of
    describing cubic Hamiltonian graphs. The way a graph is constructed
    is as follows. Since there is a Hamiltonian cycle, we first create
    a cycle on n nodes. The variable shift_list = [s_0, s_1, ...,
    s_k-1] describes edges to be created by the following scheme: for
    each i, connect vertex i to vertex (i + s_i). Then, repeats
    specifies the number of times to repeat this process, where on the
    jth repeat we connect vertex (i + j\*len(shift_list)) to vertex (
    i + j\*len(shift_list) + s_i).

    INPUT:


    -  ``n`` - the number of nodes.

    -  ``shift_list`` - a list of integer shifts mod n.

    -  ``repeats`` - the number of times to repeat the
       process.


    EXAMPLES::

        sage: G = graphs.LCFGraph(4, [2,-2], 2)
        sage: G.is_isomorphic(graphs.TetrahedralGraph())
        True

    ::

        sage: G = graphs.LCFGraph(20, [10,7,4,-4,-7,10,-4,7,-7,4], 2)
        sage: G.is_isomorphic(graphs.DodecahedralGraph())
        True

    ::

        sage: G = graphs.LCFGraph(14, [5,-5], 7)
        sage: G.is_isomorphic(graphs.HeawoodGraph())
        True

    The largest cubic nonplanar graph of diameter three::

        sage: G = graphs.LCFGraph(20, [-10,-7,-5,4,7,-10,-7,-4,5,7,-10,-7,6,-5,7,-10,-7,5,-6,7], 1)
        sage: G.degree()
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
        sage: G.diameter()
        3
        sage: G.show()  # long time

    PLOTTING: LCF Graphs are plotted as an n-cycle with edges in the
    middle, as described above.

    REFERENCES:

    - [1] Frucht, R. "A Canonical Representation of Trivalent
      Hamiltonian Graphs." J. Graph Th. 1, 45-60, 1976.

    - [2] Grunbaum, B.  Convex Polytope es. New York: Wiley,
      pp. 362-364, 1967.

    - [3] Lederberg, J. 'DENDRAL-64: A System for Computer
      Construction, Enumeration and Notation of Organic Molecules
      as Tree Structures and Cyclic Graphs. Part II. Topology of
      Cyclic Graphs.' Interim Report to the National Aeronautics
      and Space Administration. Grant NsG 81-60. December 15,
      1965.  http://profiles.nlm.nih.gov/BB/A/B/I/U/_/bbabiu.pdf.
    """
    import networkx
    pos_dict = {}
    for i in range(n):
        x = float(cos(pi/2 + ((2*pi)/n)*i))
        y = float(sin(pi/2 + ((2*pi)/n)*i))
        pos_dict[i] = [x,y]
    return graph.Graph(networkx.LCF_graph(n, shift_list, repeats),\
                       pos=pos_dict, name="LCF Graph")

def NKStarGraph(self,n,k):
    r"""
    Returns the (n,k)-star graph.

    The vertices of the (n,k)-star graph are the set of all arrangements of
    n symbols into labels of length k. There are two adjacency rules for
    the (n,k)-star graph. First, two vertices are adjacent if one can be
    obtained from the other by swapping the first symbol with another
    symbol. Second, two vertices are adjacent if one can be obtained from
    the other by swapping the first symbol with an external symbol (a
    symbol not used in the original label).

    INPUT:

    -  ``n``

    -  ``k``

    EXAMPLES::

        sage: g = graphs.NKStarGraph(4,2)
        sage: g.plot() # long time

    REFERENCES:

    - Wei-Kuo, Chiang, and Chen Rong-Jaye. "The (n, k)-star graph: A
      generalized star graph." Information Processing Letters 56,
      no. 5 (December 8, 1995): 259-264.

    AUTHORS:

    - Michael Yurko (2009-09-01)
    """
    from sage.combinat.permutation import Arrangements
    #set from which to permute
    set = [str(i) for i in xrange(1,n+1)]
    #create dict
    d = {}
    for v in Arrangements(set,k):
        tmp_dict = {}
        #add edges of dimension i
        for i in xrange(1,k):
            #swap 0th and ith element
            v[0], v[i] = v[i], v[0]
            #convert to str and add to list
            vert = "".join(v)
            tmp_dict[vert] = None
            #swap back
            v[0], v[i] = v[i], v[0]
        #add other edges
        tmp_bit = v[0]
        for i in set:
            #check if external
            if not (i in v):
                v[0] = i
                #add edge
                vert = "".join(v)
                tmp_dict[vert] = None
            v[0] = tmp_bit
        d["".join(v)] = tmp_dict
    return graph.Graph(d, name="(%d,%d)-star"%(n,k))

def NStarGraph(self,n):
    r"""
    Returns the n-star graph.

    The vertices of the n-star graph are the set of permutations on n
    symbols. There is an edge between two vertices if their labels differ
    only in the first and one other position.

    INPUT:

    -  ``n``

    EXAMPLES::

        sage: g = graphs.NStarGraph(4)
        sage: g.plot() # long time

    REFERENCES:

    - S.B. Akers, D. Horel and B. Krishnamurthy, The star graph: An
      attractive alternative to the previous n-cube. In: Proc. Internat.
      Conf. on Parallel Processing (1987), pp. 393--400.

    AUTHORS:

    - Michael Yurko (2009-09-01)
    """
    from sage.combinat.permutation import Permutations
    #set from which to permute
    set = [str(i) for i in xrange(1,n+1)]
    #create dictionary of lists
    #vertices are adjacent if the first element
    #is swapped with the ith element
    d = {}
    for v in Permutations(set):
        tmp_dict = {}
        for i in xrange(1,n):
            if v[0] != v[i]:
                #swap 0th and ith element
                v[0], v[i] = v[i], v[0]
                #convert to str and add to list
                vert = "".join(v)
                tmp_dict[vert] = None
                #swap back
                v[0], v[i] = v[i], v[0]
        d["".join(v)] = tmp_dict
    return graph.Graph(d, name = "%d-star"%n)

def OddGraph(self,n):
    r"""
    Returns the Odd Graph with parameter `n`.

    The Odd Graph with parameter `n` is defined as the
    Kneser Graph with parameters `2n-1,n-1`.
    Equivalently, the Odd Graph is the graph whose vertices
    are the `n-1`-subsets of `[0,1,\dots,2(n-1)]`, and such
    that two vertices are adjacent if their corresponding sets
    are disjoint.

    For example, the Petersen Graph can be defined
    as the Odd Graph with parameter `3`.

    EXAMPLE::

        sage: OG=graphs.OddGraph(3)
        sage: print OG.vertices()
        [{4, 5}, {1, 3}, {2, 5}, {2, 3}, {3, 4}, {3, 5}, {1, 4}, {1, 5}, {1, 2}, {2, 4}]
        sage: P=graphs.PetersenGraph()
        sage: P.is_isomorphic(OG)
        True

    TESTS::

        sage: KG=graphs.OddGraph(1)
        Traceback (most recent call last):
        ...
        ValueError: Parameter n should be an integer strictly greater than 1
    """

    if not n>1:
        raise ValueError, "Parameter n should be an integer strictly greater than 1"
    g = self.KneserGraph(2*n-1,n-1)
    g.name("Odd Graph with parameter %s" % n)
    return g

def PaleyGraph(self,q):
    r"""
    Paley graph with `q` vertices

    Parameter `q` must be the power of a prime number and congruent
    to 1 mod 4.

    EXAMPLES::

        sage: G=graphs.PaleyGraph(9);G
        Paley graph with parameter 9: Graph on 9 vertices
        sage: G.is_regular()
        True

    A Paley graph is always self-complementary::

        sage: G.complement().is_isomorphic(G)
        True
    """
    from sage.rings.finite_rings.integer_mod import mod
    from sage.rings.finite_rings.constructor import FiniteField
    assert q.is_prime_power(), "Parameter q must be a prime power"
    assert mod(q,4)==1, "Parameter q must be congruent to 1 mod 4"
    g = graph.Graph([FiniteField(q,'a'), lambda i,j: (i-j).is_square()],
    loops=False, name = "Paley graph with parameter %d"%q)
    return g

def PermutationGraph(self, second_permutation, first_permutation = None):
    r"""
    Builds a permutation graph from one (or two) permutations.

    General definition

    A Permutation Graph can be encoded by a permutation `\sigma`
    of `0, ..., n`. It is then built in the following way :

      Take two horizontal lines in the euclidean plane, and mark points `0,
      ..., n` from left to right on the first of them. On the second one,
      still from left to right, mark point in the order in which they appear
      in `\sigma`. Now, link by a segment the two points marked with 1, then
      link together the points marked with 2, and so on. The permutation
      graph defined by the permutation is the intersection graph of those
      segments : there exists a point in this graph for each element from
      `1` to `n`, two vertices `i, j` being adjacent if the segments `i` and
      `j` cross each other.

    The set of edges of the resulting graph is equal to the set of
    inversions of the inverse of the given permutation.

    INPUT:

    - ``second_permutation`` -- the permutation from which the graph should
      be built. It corresponds to the ordering of the elements on the second
      line (see previous definition)

    - ``first_permutation`` (optional) -- the ordering of the elements on
      the *first* line. This is useful when the elements have no natural
      ordering, for instance when they are strings, or tuples, or anything
      else.

      When ``first_permutation == None`` (default), it is set to be equal to
      ``sorted(second_permutation)``, which just yields the expected
      ordering when the elements of the graph are integers.

    .. SEEALSO:

      - Recognition of Permutation graphs in the :mod:`comparability module
        <sage.graphs.comparability>`.

      - Drawings of permutation graphs as intersection graphs of segments is
        possible through the
        :meth:`~sage.combinat.permutation.Permutation_class.show` method of
        :class:`~sage.combinat.permutation.Permutation` objects.

        The correct argument to use in this case is ``show(representation =
        "braid")``.

      - :meth:`~sage.combinat.permutation.Permutation_class.inversions`

    EXAMPLE::

        sage: p = Permutations(5).random_element()
        sage: edges = graphs.PermutationGraph(p).edges(labels =False)
        sage: set(edges) == set(map(lambda (x,y) : (x+1,y+1),p.inverse().inversions()))
        True

    TESTS::

        sage: graphs.PermutationGraph([1, 2, 3], [4, 5, 6])
        Traceback (most recent call last):
        ...
        ValueError: The two permutations do not contain the same set of elements ...
    """
    if first_permutation == None:
        first_permutation = sorted(second_permutation)
    else:
        if set(second_permutation) != set(first_permutation):
            raise ValueError("The two permutations do not contain the same "+
                             "set of elements ! It is going to be pretty "+
                             "hard to define a permutation graph from that !")

    vertex_to_index = {}
    for i, v in enumerate(first_permutation):
        vertex_to_index[v] = i+1

    from sage.combinat.permutation import Permutation
    p2 = Permutation(map(lambda x:vertex_to_index[x], second_permutation))
    p1 = Permutation(map(lambda x:vertex_to_index[x], first_permutation))
    p2 = p2 * p1.inverse()
    p2 = p2.inverse()

    g = graph.Graph(name="Permutation graph for "+str(second_permutation))
    g.add_vertices(second_permutation)

    for u,v in p2.inversions():
        g.add_edge(first_permutation[u], first_permutation[v])

    return g

def HanoiTowerGraph(self, pegs, disks, labels=True, positions=True):
    r"""
    Returns the graph whose vertices are the states of the
    Tower of Hanoi puzzle, with edges representing legal moves between states.

    INPUT:

    - ``pegs`` - the number of pegs in the puzzle, 2 or greater
    - ``disks`` - the number of disks in the puzzle, 1 or greater
    - ``labels`` - default: ``True``, if ``True`` the graph contains
      more meaningful labels, see explanation below.  For large instances,
      turn off labels for much faster creation of the graph.
    - ``positions`` - default: ``True``, if ``True`` the graph contains
      layout information.  This creates a planar layout for the case
      of three pegs.  For large instances, turn off layout information
      for much faster creation of the graph.

    OUTPUT:

    The Tower of Hanoi puzzle has a certain number of identical pegs
    and a certain number of disks, each of a different radius.
    Initially the disks are all on a single peg, arranged
    in order of their radii, with the largest on the bottom.

    The goal of the puzzle is to move the disks to any other peg,
    arranged in the same order.  The one constraint is that the
    disks resident on any one peg must always be arranged with larger
    radii lower down.

    The vertices of this graph represent all the possible states
    of this puzzle.  Each state of the puzzle is a tuple with length
    equal to the number of disks, ordered by largest disk first.
    The entry of the tuple is the peg where that disk resides.
    Since disks on a given peg must go down in size as we go
    up the peg, this totally describes the state of the puzzle.

    For example ``(2,0,0)`` means the large disk is on peg 2, the
    medium disk is on peg 0, and the small disk is on peg 0
    (and we know the small disk must be above the medium disk).
    We encode these tuples as integers with a base equal to
    the number of pegs, and low-order digits to the right.

    Two vertices are adjacent if we can change the puzzle from
    one state to the other by moving a single disk.  For example,
    ``(2,0,0)`` is adjacent to ``(2,0,1)`` since we can move
    the small disk off peg 0 and onto (the empty) peg 1.
    So the solution to a 3-disk puzzle (with at least
    two pegs) can be expressed by the shortest path between
    ``(0,0,0)`` and ``(1,1,1)``.  For more on this representation
    of the graph, or its properties, see [ARETT-DOREE]_.

    For greatest speed we create graphs with integer vertices,
    where we encode the tuples as integers with a base equal
    to the number of pegs, and low-order digits to the right.
    So for example, in a 3-peg puzzle with 5 disks, the
    state ``(1,2,0,1,1)`` is encoded as
    `1\ast 3^4 + 2\ast 3^3 + 0\ast 3^2 + 1\ast 3^1 + 1\ast 3^0 = 139`.

    For smaller graphs, the labels that are the tuples are informative,
    but slow down creation of the graph.  Likewise computing layout
    information also incurs a significant speed penalty. For maximum
    speed, turn off labels and layout and decode the
    vertices explicitly as needed.  The
    :meth:`sage.rings.integer.Integer.digits`
    with the ``padsto`` option is a quick way to do this, though you
    may want to reverse the list that is output.

    PLOTTING:

    The layout computed when ``positions = True`` will
    look especially good for the three-peg case, when the graph is known
    to be planar.  Except for two small cases on 4 pegs, the graph is
    otherwise not planar, and likely there is a better way to layout
    the vertices.

    EXAMPLES:

    A classic puzzle uses 3 pegs.  We solve the 5 disk puzzle using
    integer labels and report the minimum number of moves required.
    Note that `3^5-1` is the state where all 5 disks
    are on peg 2. ::

        sage: H = graphs.HanoiTowerGraph(3, 5, labels=False, positions=False)
        sage: H.distance(0, 3^5-1)
        31

    A slightly larger instance. ::

        sage: H = graphs.HanoiTowerGraph(4, 6, labels=False, positions=False)
        sage: H.num_verts()
        4096
        sage: H.distance(0, 4^6-1)
        17

    For a small graph, labels and layout information can be useful.
    Here we explicitly list a solution as a list of states. ::

        sage: H = graphs.HanoiTowerGraph(3, 3, labels=True, positions=True)
        sage: H.shortest_path((0,0,0), (1,1,1))
        [(0, 0, 0), (0, 0, 1), (0, 2, 1), (0, 2, 2), (1, 2, 2), (1, 2, 0), (1, 1, 0), (1, 1, 1)]

    Some facts about this graph with `p` pegs and `d` disks:

    - only automorphisms are the "obvious" ones - renumber the pegs.
    - chromatic number is less than or equal to `p`
    - independence number is `p^{d-1}`

    ::

        sage: H = graphs.HanoiTowerGraph(3,4,labels=False,positions=False)
        sage: H.automorphism_group().is_isomorphic(SymmetricGroup(3))
        True
        sage: H.chromatic_number()
        3
        sage: len(H.independent_set()) == 3^(4-1)
        True

    TESTS:

    It is an error to have just one peg (or less). ::

        sage: graphs.HanoiTowerGraph(1, 5)
        Traceback (most recent call last):
        ...
        ValueError: Pegs for Tower of Hanoi graph should be two or greater (not 1)

    It is an error to have zero disks (or less). ::

        sage: graphs.HanoiTowerGraph(2, 0)
        Traceback (most recent call last):
        ...
        ValueError: Disks for Tower of Hanoi graph should be one or greater (not 0)

    .. rubric:: Citations

    .. [ARETT-DOREE] Arett, Danielle and Doree, Suzanne
       "Coloring and counting on the Hanoi graphs"
       Mathematics Magazine, Volume 83, Number 3, June 2010, pages 200-9


    AUTHOR:

    - Rob Beezer, (2009-12-26), with assistance from Su Doree

    """

    # sanitize input
    from sage.rings.all import Integer
    pegs = Integer(pegs)
    if pegs < 2:
        raise ValueError("Pegs for Tower of Hanoi graph should be two or greater (not %d)" % pegs)
    disks = Integer(disks)
    if disks < 1:
        raise ValueError("Disks for Tower of Hanoi graph should be one or greater (not %d)" % disks)

    # Each state of the puzzle is a tuple with length
    # equal to the number of disks, ordered by largest disk first
    # The entry of the tuple is the peg where that disk resides
    # Since disks on a given peg must go down in size as we go
    # up the peg, this totally describes the puzzle
    # We encode these tuples as integers with a base equal to
    # the number of pegs, and low-order digits to the right

    # complete graph on number of pegs when just a single disk
    edges = [[i,j] for i in range(pegs) for j in range(i+1,pegs)]

    nverts = 1
    for d in range(2, disks+1):
        prevedges = edges      # remember subgraph to build from
        nverts = pegs*nverts   # pegs^(d-1)
        edges = []

        # Take an edge, change its two states in the same way by adding
        # a large disk to the bottom of the same peg in each state
        # This is accomplished by adding a multiple of pegs^(d-1)
        for p in range(pegs):
            largedisk = p*nverts
            for anedge in prevedges:
                edges.append([anedge[0]+largedisk, anedge[1]+largedisk])

        # Two new states may only differ in the large disk
        # being the only disk on two different pegs, thus
        # otherwise being a common state with one less disk
        # We construct all such pairs of new states and add as edges
        from sage.combinat.subset import Subsets
        for state in range(nverts):
            emptypegs = range(pegs)
            reduced_state = state
            for i in range(d-1):
                apeg = reduced_state % pegs
                if apeg in emptypegs:
                    emptypegs.remove(apeg)
                reduced_state = reduced_state//pegs
            for freea, freeb in Subsets(emptypegs, 2):
                edges.append([freea*nverts+state,freeb*nverts+state])

    H = graph.Graph({}, loops=False, multiedges=False)
    H.add_edges(edges)


    # Making labels and/or computing positions can take a long time,
    # relative to just constructing the edges on integer vertices.
    # We try to minimize coercion overhead, but need Sage
    # Integers in order to use digits() for labels.
    # Getting the digits with custom code was no faster.
    # Layouts are circular (symmetric on the number of pegs)
    # radiating outward to the number of disks (radius)
    # Algorithm uses some combination of alternate
    # clockwise/counterclockwise placements, which
    # works well for three pegs (planar layout)
    #
    from sage.functions.trig import sin, cos, csc
    if labels or positions:
        mapping = {}
        pos = {}
        a = Integer(-1)
        one = Integer(1)
        if positions:
            radius_multiplier = 1 + csc(pi/pegs)
            sine = []; cosine = []
            for i in range(pegs):
                angle = 2*i*pi/float(pegs)
                sine.append(sin(angle))
                cosine.append(cos(angle))
        for i in range(pegs**disks):
            a += one
            state = a.digits(base=pegs, padto=disks)
            if labels:
                state.reverse()
                mapping[i] = tuple(state)
                state.reverse()
            if positions:
                locx = 0.0; locy = 0.0
                radius = 1.0
                parity = -1.0
                for index in range(disks):
                    p = state[index]
                    radius *= radius_multiplier
                    parity *= -1.0
                    locx_temp = cosine[p]*locx - parity*sine[p]*locy + radius*cosine[p]
                    locy_temp = parity*sine[p]*locx + cosine[p]*locy - radius*parity*sine[p]
                    locx = locx_temp
                    locy = locy_temp
                pos[i] = (locx,locy)
        # set positions, then relabel (not vice versa)
        if positions:
            H.set_pos(pos)
        if labels:
            H.relabel(mapping)

    return H

def line_graph_forbidden_subgraphs(self):
    r"""
    Returns the 9 forbidden subgraphs of a line graph.

    `Wikipedia article on the line graphs
    <http://en.wikipedia.org/wiki/Line_graph>`_

    The graphs are returned in the ordering given by the Wikipedia
    drawing, read from left to right and from top to bottom.

    EXAMPLE::

        sage: graphs.line_graph_forbidden_subgraphs()
        [Claw graph: Graph on 4 vertices,
        Graph on 6 vertices,
        Graph on 6 vertices,
        Graph on 5 vertices,
        Graph on 6 vertices,
        Graph on 6 vertices,
        Graph on 6 vertices,
        Graph on 6 vertices,
        Graph on 5 vertices]

    """
    from sage.graphs.all import Graph
    graphs = [self.ClawGraph()]

    graphs.append(Graph({
                0: [1, 2, 3],
                1: [2, 3],
                4: [2],
                5: [3]
                }))

    graphs.append(Graph({
                0: [1, 2, 3, 4],
                1: [2, 3, 4],
                3: [4],
                2: [5]
                }))

    graphs.append(Graph({
                0: [1, 2, 3],
                1: [2, 3],
                4: [2, 3]
                }))

    graphs.append(Graph({
                0: [1, 2, 3],
                1: [2, 3],
                4: [2],
                5: [3, 4]
                }))

    graphs.append(Graph({
                0: [1, 2, 3, 4],
                1: [2, 3, 4],
                3: [4],
                5: [2, 0, 1]
                }))

    graphs.append(Graph({
                5: [0, 1, 2, 3, 4],
                0: [1, 4],
                2: [1, 3],
                3: [4]
                }))

    graphs.append(Graph({
                1: [0, 2, 3, 4],
                3: [0, 4],
                2: [4, 5],
                4: [5]
                }))

    graphs.append(Graph({
                0: [1, 2, 3],
                1: [2, 3, 4],
                2: [3, 4],
                3: [4]
                }))

    return graphs

def trees(self, vertices):
    r"""
    Returns a generator of the distinct trees on a fixed number of vertices.

    INPUT:

    -  ``vertices`` - the size of the trees created.

    OUTPUT:

    A generator which creates an exhaustive, duplicate-free listing
    of the connected free (unlabeled) trees with ``vertices`` number
    of vertices.  A tree is a graph with no cycles.

    ALGORITHM:

    Uses an algorithm that generates each new tree
    in constant time.  See the documentation for, and implementation
    of, the :mod:`sage.graphs.trees` module, including a citation.

    EXAMPLES:

    We create an iterator, then loop over its elements. ::

        sage: tree_iterator = graphs.trees(7)
        sage: for T in tree_iterator:
        ...     print T.degree_sequence()
        [2, 2, 2, 2, 2, 1, 1]
        [3, 2, 2, 2, 1, 1, 1]
        [3, 2, 2, 2, 1, 1, 1]
        [4, 2, 2, 1, 1, 1, 1]
        [3, 3, 2, 1, 1, 1, 1]
        [3, 3, 2, 1, 1, 1, 1]
        [4, 3, 1, 1, 1, 1, 1]
        [3, 2, 2, 2, 1, 1, 1]
        [4, 2, 2, 1, 1, 1, 1]
        [5, 2, 1, 1, 1, 1, 1]
        [6, 1, 1, 1, 1, 1, 1]

    The number of trees on the first few vertex counts.
    This is sequence A000055 in Sloane's OEIS. ::

        sage: [len(list(graphs.trees(i))) for i in range(0, 15)]
        [1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235, 551, 1301, 3159]
    """
    from sage.graphs.trees import TreeIterator
    return iter(TreeIterator(vertices))

def RingedTree(self, k, vertex_labels = True):
    r"""
    Return the ringed tree on k-levels.

    A ringed tree of level `k` is a binary tree with `k` levels (counting
    the root as a level), in which all vertices at the same level are connected
    by a ring.

    More precisely, in each layer of the binary tree (i.e. a layer is the set of
    vertices `[2^i...2^{i+1}-1]`) two vertices `u,v` are adjacent if `u=v+1` or
    if `u=2^i` and `v=`2^{i+1}-1`.

    Ringed trees are defined in [CFHM12]_.

    INPUT:

    - ``k`` -- the number of levels of the ringed tree.

    - ``vertex_labels`` (boolean) -- whether to label vertices as binary words
      (default) or as integers.

    EXAMPLE::

        sage: G = graphs.RingedTree(5)
        sage: P = G.plot(vertex_labels=False, vertex_size=10)
        sage: P.show() # long time
        sage: G.vertices()
        ['', '0', '00', '000', '0000', '0001', '001', '0010', '0011', '01',
         '010', '0100', '0101', '011', '0110', '0111', '1', '10', '100',
         '1000', '1001', '101', '1010', '1011', '11', '110', '1100', '1101',
         '111', '1110', '1111']

    TEST::

        sage: G = graphs.RingedTree(-1)
        Traceback (most recent call last):
        ...
        ValueError: The number of levels must be >= 1.
        sage: G = graphs.RingedTree(5, vertex_labels = False)
        sage: G.vertices()
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
        18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

    REFERENCES:

    .. [CFHM12] On the Hyperbolicity of Small-World and Tree-Like Random Graphs
      Wei Chen, Wenjie Fang, Guangda Hu, Michael W. Mahoney
      http://arxiv.org/abs/1201.1717
    """
    if k<1:
        raise ValueError('The number of levels must be >= 1.')

    from sage.graphs.graph_plot import _circle_embedding
    from sage.graphs.graph_plot import GraphGenerators

    # Creating the Balanced tree, which contains most edges already
    g = GraphGenerators().BalancedTree(2,k-1)
    g.name('Ringed Tree on '+str(k)+' levels')

    # We consider edges layer by layer
    for i in range(1,k):
        vertices = range(2**(i)-1,2**(i+1)-1)

        # Add the missing edges
        g.add_cycle(vertices)

        # And set the vertices' positions
        radius = i if i <= 1 else 1.5**i
        shift = -2**(i-2)+.5 if i > 1 else 0
        _circle_embedding(g, vertices, radius = radius, shift = shift)

    # Specific position for the central vertex
    g.get_pos()[0] = (0,0.2)

    # Relabel vertices as binary words
    if not vertex_labels:
        return g

    vertices = ['']
    for i in range(k-1):
        for j in range(2**(i)-1,2**(i+1)-1):
            v = vertices[j]
            vertices.append(v+'0')
            vertices.append(v+'1')

    g.relabel(vertices)

    return g
