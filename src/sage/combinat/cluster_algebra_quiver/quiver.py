r"""
Quiver

A *quiver* is an oriented graphs without loops, two-cycles, or multiple edges. The edges are labelled by pairs `(i,-j)`
such that the matrix `M = (m_{ab})` with `m_{ab} = i, m_{ba} = -j` for an edge `(i,-j)` between vertices `a` and `b` is skew-symmetrizable.

For the compendium on the cluster algebra and quiver package see

        http://arxiv.org/abs/1102.4844.

AUTHORS:

- Gregg Musiker
- Christian Stump

.. seealso:: For mutation types of combinatorial quivers, see :meth:`~sage.combinat.cluster_algebra_quiver.quiver_mutation_type.QuiverMutationType`.
"""

#*****************************************************************************
#       Copyright (C) 2011 Gregg Musiker <musiker@math.mit.edu>
#                          Christian Stump <christian.stump@univie.ac.at>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.structure.sage_object import SageObject
from copy import copy
from sage.structure.unique_representation import UniqueRepresentation
from sage.misc.all import cached_method
from sage.rings.all import ZZ, CC, infinity
from sage.graphs.all import Graph, DiGraph
from sage.combinat.cluster_algebra_quiver.quiver_mutation_type import QuiverMutationType, QuiverMutationType_Irreducible, QuiverMutationType_Reducible, _edge_list_to_matrix
from sage.combinat.cluster_algebra_quiver.mutation_class import _principal_part, _digraph_mutate, _matrix_to_digraph, _dg_canonical_form
from sage.groups.perm_gps.permgroup import PermutationGroup

class ClusterQuiver(SageObject):
    """
    The *quiver* associated to an *exchange matrix*.

    INPUT:

    - ``data`` -- can be any of the following::

        * QuiverMutationType
        * str - a string representing a QuiverMutationType or a common quiver type (see Examples)
        * ClusterQuiver
        * Matrix - a skew-symmetrizable matrix
        * DiGraph - must be the input data for a quiver
        * List of edges - must be the edge list of a digraph for a quiver

    - ``frozen`` -- (default:``None``) sets the number of frozen variables if the input type is a DiGraph, it is ignored otherwise.

    EXAMPLES:

        from a QuiverMutationType::

            sage: Q = ClusterQuiver(['A',5]); Q
            Quiver on 5 vertices of type ['A', 5]

            sage: Q = ClusterQuiver(['B',2]); Q
            Quiver on 2 vertices of type ['B', 2]
            sage: Q2 = ClusterQuiver(['C',2]); Q2
            Quiver on 2 vertices of type ['B', 2]
            sage: MT = Q.mutation_type(); MT.standard_quiver() == Q
            True
            sage: MT = Q2.mutation_type(); MT.standard_quiver() == Q2
            False

            sage: Q = ClusterQuiver(['A',[2,5],1]); Q
            Quiver on 7 vertices of type ['A', [2, 5], 1]

            sage: Q = ClusterQuiver(['A', [5,0],1]); Q
            Quiver on 5 vertices of type ['D', 5]
            sage: Q.is_acyclic()
            False

            sage: Q = ClusterQuiver(['F', 4, [2,1]]); Q
            Quiver on 6 vertices of type ['F', 4, [1, 2]]
            sage: MT = Q.mutation_type(); MT.standard_quiver() == Q
            False
            sage: dg = Q.digraph(); Q.mutate([2,1,4,0,5,3])
            sage: dg2 = Q.digraph(); dg2.is_isomorphic(dg,edge_labels=True)
            False
            sage: dg2.is_isomorphic(MT.standard_quiver().digraph(),edge_labels=True)
            True

            sage: Q = ClusterQuiver(['G',2, (3,1)]); Q
            Quiver on 4 vertices of type ['G', 2, [1, 3]]
            sage: MT = Q.mutation_type(); MT.standard_quiver() == Q
            False

            sage: Q = ClusterQuiver(['GR',[3,6]]); Q
            Quiver on 4 vertices of type ['D', 4]
            sage: MT = Q.mutation_type(); MT.standard_quiver() == Q
            False

            sage: Q = ClusterQuiver(['GR',[3,7]]); Q
            Quiver on 6 vertices of type ['E', 6]

            sage: Q = ClusterQuiver(['TR',2]); Q
            Quiver on 3 vertices of type ['A', 3]
            sage: MT = Q.mutation_type(); MT.standard_quiver() == Q
            False
            sage: Q.mutate([1,0]); MT.standard_quiver() == Q
            True

            sage: Q = ClusterQuiver(['TR',3]); Q
            Quiver on 6 vertices of type ['D', 6]
            sage: MT = Q.mutation_type(); MT.standard_quiver() == Q
            False

        from a ClusterQuiver::

            sage: Q = ClusterQuiver(['A',[2,5],1]); Q
            Quiver on 7 vertices of type ['A', [2, 5], 1]
            sage: T = ClusterQuiver( Q ); T
            Quiver on 7 vertices of type ['A', [2, 5], 1]

        from a Matrix::

            sage: Q = ClusterQuiver(['A',[2,5],1]); Q
            Quiver on 7 vertices of type ['A', [2, 5], 1]
            sage: T = ClusterQuiver( Q._M ); T
            Quiver on 7 vertices

            sage: Q = ClusterQuiver( matrix([[0,1,-1],[-1,0,1],[1,-1,0],[1,2,3]]) ); Q
            Quiver on 4 vertices with 1 frozen vertex

            sage: Q = ClusterQuiver( matrix([]) ); Q
            Quiver without vertices

        from a DiGraph::

            sage: Q = ClusterQuiver(['A',[2,5],1]); Q
            Quiver on 7 vertices of type ['A', [2, 5], 1]
            sage: T = ClusterQuiver( Q._digraph ); T
            Quiver on 7 vertices

            sage: Q = ClusterQuiver( DiGraph([[1,2],[2,3],[3,4],[4,1]]) ); Q
            Quiver on 4 vertices

        from a List of edges::

            sage: Q = ClusterQuiver(['A',[2,5],1]); Q
            Quiver on 7 vertices of type ['A', [2, 5], 1]
            sage: T = ClusterQuiver( Q._digraph.edges() ); T
            Quiver on 7 vertices

            sage: Q = ClusterQuiver( [[1,2],[2,3],[3,4],[4,1]] ); Q
            Quiver on 4 vertices

    TESTS::

        sage: Q = ClusterQuiver(DiGraph([[1,1]]))
        Traceback (most recent call last):
        ...
        ValueError: The input DiGraph contains a loop

        sage: Q = ClusterQuiver([[1,1]])
        Traceback (most recent call last):
        ...
        ValueError: The input DiGraph contains a loop

        sage: Q = ClusterQuiver(DiGraph([[1, 0],[0,1]]))
        Traceback (most recent call last):
        ...
        ValueError: The input DiGraph contains two-cycles

        sage: Q = ClusterQuiver('whatever')
        Traceback (most recent call last):
        ...
        ValueError: The input data was not recognized.

    """
    def __init__( self, data, frozen=None ):
        """
        TESTS::

            sage: Q = ClusterQuiver(['A',4])
            sage: TestSuite(Q).run()
        """
        from sage.matrix.matrix import Matrix

        # constructs a quiver from a mutation type
        if type( data ) in [QuiverMutationType_Irreducible,QuiverMutationType_Reducible]:
            if frozen is not None:
                print 'The input data is a quiver, therefore the additional parameter frozen is ignored.'

            mutation_type = data
            self.__init__( mutation_type.standard_quiver() )

        # constructs a quiver from string representing a mutation type or a common quiver type (see Examples)
        # NOTE: for now, any string representing a *reducible type* is coerced into the standard quiver, but there is now more flexibility in how to input a connected (irreducible) quiver.
        elif type( data ) in [list,tuple] and ( type( data[0] ) is str or all(type( comp ) in [list,tuple] and type( comp[0] ) is str for comp in data) ):
            if frozen is not None:
                print 'The input data is a quiver, therefore the additional parameter frozen is ignored.'
            mutation_type = QuiverMutationType( data )

            # The command QuiverMutationType_Irreducible (which is not imported globally) already creates the desired digraph as long as we bypass the mutation type checking of QuiverMutationType and format the input appropriately.  Thus we handle several special cases this way.
            if len(data) == 2 and type( data[0] ) is str:
                if data[0] == 'TR' or data[0] == 'GR' or (data[0] == 'C' and data[1] == 2):
                    if data[1] in ZZ:
                        quiv = ClusterQuiver( QuiverMutationType_Irreducible( data[0], data[1] )._digraph )
                        quiv._mutation_type = mutation_type
                        self.__init__( quiv )
                    elif type( data[1]) is list:
                        quiv = ClusterQuiver( QuiverMutationType_Irreducible( data[0], tuple(data[1]) )._digraph )
                        quiv._mutation_type = mutation_type
                        self.__init__( quiv )
                else:
                    self.__init__( mutation_type.standard_quiver() )
            elif len(data) == 3 and type( data[0] ) is str:
                if (data[0] == 'F' and data[1] == 4 and data[2] == [2,1])   or (data[0] == 'G' and data[1] == 2 and data[2] == [3,1]):
                    quiv = ClusterQuiver( QuiverMutationType_Irreducible( data[0], data[1], tuple(data[2]) )._digraph )
                    quiv._mutation_type = mutation_type
                    self.__init__( quiv )
                elif (data[0] == 'F' and data[1] == 4 and data[2] == (2,1) )   or (data[0] == 'G' and data[1] == 2 and data[2] == (3,1) ):
                    quiv = ClusterQuiver( QuiverMutationType_Irreducible( data[0], data[1], data[2] )._digraph )
                    quiv._mutation_type = mutation_type
                    self.__init__( quiv )
                elif data[0] == 'A' and type(data[1]) is list and data[2] == 1:
                    if len(data[1]) == 2 and min(data[1]) == 0:
                        quiv = ClusterQuiver( QuiverMutationType_Irreducible( data[0], tuple(data[1]), data[2] )._digraph )
                        quiv._mutation_type = mutation_type
                        self.__init__( quiv )
                    else:
                        self.__init__( mutation_type.standard_quiver() )

                elif data[0] == 'A' and type(data[1]) is tuple and data[2] == 1:
                    if len(data[1]) == 2 and min(data[1]) == 0:
                        quiv = ClusterQuiver( QuiverMutationType_Irreducible( data[0], data[1], data[2] )._digraph )
                        quiv._mutation_type = mutation_type
                        self.__init__( quiv )
                    else:
                        self.__init__( mutation_type.standard_quiver() )

                else:
                    self.__init__( mutation_type.standard_quiver() )
            else:
                self.__init__( mutation_type.standard_quiver() )

        # constructs a quiver from a quiver
        elif type(data) is ClusterQuiver:
            if frozen is not None:
                print 'The input data is a quiver, therefore the additional parameter frozen is ignored.'

            self._M = copy(data._M)
            self._n = data._n
            self._m = data._m
            self._digraph = copy( data._digraph )
            self._mutation_type = data._mutation_type
            self._description = data._description

        # constructs a quiver from a matrix
        elif isinstance(data, Matrix):
            if not _principal_part(data).is_skew_symmetrizable( positive=True ):
                raise ValueError, 'The principal part of the matrix data must be skew-symmetrizable.'
            if frozen is not None:
                print 'The input data is a matrix, therefore the additional parameter frozen is ignored.'

            self._M = copy(data).sparse_matrix()
            self._n = n = self._M.ncols()
            self._m = m = self._M.nrows() - self._n
            self._digraph = _matrix_to_digraph( self._M )
            self._mutation_type = None
            if n+m == 0:
                self._description = 'Quiver without vertices'
            elif n+m == 1:
                self._description = 'Quiver on %d vertex' %(n+m)
            else:
                self._description = 'Quiver on %d vertices' %(n+m)

        # constructs a quiver from a digraph
        elif type(data) is DiGraph:
            if frozen is None:
                frozen = 0
            elif not ZZ(frozen) == frozen:
                raise ValueError("The optional argument frozen (=%s) must be an integer."%frozen)
            m = self._m = frozen
            n = self._n = data.order() - m
            dg = copy( data )
            edges = data.edges(labels=False)
            if any( (a,a) in edges for a in data.vertices() ):
                raise ValueError, "The input DiGraph contains a loop"
            if any( (b,a) in edges for (a,b) in edges ):
                raise ValueError, "The input DiGraph contains two-cycles"
            if not set(dg.vertices()) == set(range(n+m)):
                dg.relabel()
            if dg.has_multiple_edges():
                multi_edges = {}
                for v1,v2,label in dg.multiple_edges():
                    if label not in ZZ:
                        raise ValueError, "The input DiGraph contains multiple edges labeled by non-integers"
                    elif (v1,v2) in multi_edges:
                        multi_edges[(v1,v2)] += label
                    else:
                        multi_edges[(v1,v2)] = label
                    dg.delete_edge(v1,v2)
                dg.add_edges( [ (v1,v2,multi_edges[(v1,v2)]) for v1,v2 in multi_edges ] )
            for edge in dg.edge_iterator():
                if edge[0] >= n and edge[1] >= n:
                    raise ValueError, "The input digraph contains edges within the frozen vertices"
                if edge[2] is None:
                    dg.set_edge_label( edge[0], edge[1], (1,-1) )
                    edge = (edge[0],edge[1],(1,-1))
                elif edge[2] in ZZ:
                    dg.set_edge_label( edge[0], edge[1], (edge[2],-edge[2]) )
                    edge = (edge[0],edge[1],(edge[2],-edge[2]))
                elif type(edge[2]) == list and len(edge[2]) <> 2:
                    raise ValueError, "The input digraph contains an edge with the wrong type of list as a label."
                elif type(edge[2]) == list and len(edge[2]) == 2:
                    dg.set_edge_label( edge[0], edge[1], (edge[2][0], edge[2][1]))
                    edge = (edge[0],edge[1],(edge[2][0],edge[2][1]))
                elif ( edge[0] >= n or edge[1] >= n ) and not edge[2][0] == - edge[2][1]:
                    raise ValueError, "The input digraph contains an edge to or from a frozen vertex which is not skew-symmetric."
                if edge[2][0] < 0:
                    raise ValueError, "The input digraph contains an edge of the form (a,-b) with negative a."

            M = _edge_list_to_matrix( dg.edge_iterator(), n, m )
            if not _principal_part(M).is_skew_symmetrizable( positive=True ):
                raise ValueError, "The input digraph must be skew-symmetrizable"
            self._digraph = dg
            self._M = M
            if n+m == 0:
                self._description = 'Quiver without vertices'
            elif n+m == 1:
                self._description = 'Quiver on %d vertex' %(n+m)
            else:
                self._description = 'Quiver on %d vertices' %(n+m)
            self._mutation_type = None

        # if data is a list of edges, the appropriate digraph is constructed.

        elif isinstance(data,list) and all(isinstance(x,(list,tuple)) for x in data ):
            dg = DiGraph( data )
            self.__init__(data=dg, frozen=frozen )

        # otherwise, an error is raised
        else:
            raise ValueError, "The input data was not recognized."

    def __eq__(self, other):
        """
        Returns ``True`` if ``self`` and ``other`` represent the same quiver.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',5])
            sage: T = Q.mutate( 2, inplace=False )
            sage: Q.__eq__( T )
            False
            sage: T.mutate( 2 )
            sage: Q.__eq__( T )
            True
        """
        return type( other ) is ClusterQuiver and self._M == other._M

    def _repr_(self):
        """
        Returns the description of ``self``.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',5])
            sage: Q._repr_()
            "Quiver on 5 vertices of type ['A', 5]"
        """
        name = self._description
        if self._mutation_type:
            if type( self._mutation_type ) in [QuiverMutationType_Irreducible,QuiverMutationType_Reducible]:
                name += ' of type ' + str(self._mutation_type)
            else:
                name += ' of ' + self._mutation_type
        if self._m == 1:
            name += ' with %s frozen vertex'%self._m
        elif self._m > 1:
            name += ' with %s frozen vertices'%self._m
        return name

    def plot(self, circular=True, center=(0,0), directed=True, mark=None, save_pos=False):
        """
        Returns the plot of the underlying digraph of ``self``.

        INPUT:

        - ``circular`` -- (default:True) if True, the circular plot is chosen, otherwise >>spring<< is used.
        - ``center`` -- (default:(0,0)) sets the center of the circular plot, otherwise it is ignored.
        - ``directed`` -- (default: True) if True, the directed version is shown, otherwise the undirected.
        - ``mark`` -- (default: None) if set to i, the vertex i is highlighted.
        - ``save_pos`` -- (default:False) if True, the positions of the vertices are saved.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',5])
            sage: pl = Q.plot()
            sage: pl = Q.plot(circular=True)
        """
        from sage.plot.colors import rainbow
        from sage.graphs.graph_generators import GraphGenerators
        from sage.all import e,pi,I
        graphs = GraphGenerators()
        # returns positions for graph vertices on two concentric cycles with radius 1 and 2
        def _graphs_concentric_circles(n,m):
            g1 = graphs.CycleGraph(n).get_pos()
            g2 = graphs.CycleGraph(m).get_pos()
            for i in g2:
                z = CC(g2[i])*e**(-pi*I/(2*m))
                g2[i] = (z.real_part(),z.imag_part())
            for i in range(m):
                g1[n+i] = [2*g2[i][0], 2*g2[i][1]]
            return g1

        n, m = self._n, self._m
        colors = rainbow(11)
        color_dict = { colors[0]:[], colors[1]:[], colors[6]:[], colors[5]:[] }
        if directed:
            dg = DiGraph( self._digraph )
        else:
            dg = Graph( self._digraph )
        for edge in dg.edges():
            v1,v2,(a,b) = edge
            if v1 < n and v2 < n:
                if (a,b) == (1,-1):
                    color_dict[ colors[0] ].append((v1,v2))
                else:
                    color_dict[ colors[6] ].append((v1,v2))
            else:
                if (a,b) == (1,-1):
                    color_dict[ colors[1] ].append((v1,v2))
                else:
                    color_dict[ colors[5] ].append((v1,v2))
            if a == -b:
                if a == 1:
                    dg.set_edge_label( v1,v2,'' )
                else:
                    dg.set_edge_label( v1,v2,a )
        if mark is not None:
            if mark < n:
                partition = (range(mark)+range(mark+1,n),range(n,n+m),[mark])
            elif mark > n:
                partition = (range(n),range(n,mark)+range(mark+1,n+m),[mark])
            else:
                raise ValueError, "The given mark is not a vertex of self."
        else:
            partition = (range(n),range(n,n+m),[])
        vertex_color_dict = {}
        vertex_color_dict[ colors[0] ] = partition[0]
        vertex_color_dict[ colors[6] ] = partition[1]
        vertex_color_dict[ colors[4] ] = partition[2]

        options = {
            'graph_border' : True,
            'edge_colors': color_dict,
            'vertex_colors': vertex_color_dict,
            'edge_labels' : True,
        }
        if circular:
            pp = _graphs_concentric_circles( n, m )
            for v in pp:
                pp[v] = (pp[v][0]+center[0],pp[v][1]+center[1])
            options[ 'pos' ] = pp
        return dg.plot( **options )

    def show(self, fig_size=1, circular=False, directed=True, mark=None, save_pos=False):
        """
        Shows the plot of the underlying digraph of ``self``.

        INPUT:

        - ``fig_size`` -- (default: 1) factor by which the size of the plot is multiplied.
        - ``circular`` -- (default: False) if True, the circular plot is chosen, otherwise >>spring<< is used.
        - ``directed`` -- (default: True) if True, the directed version is shown, otherwise the undirected.
        - ``mark`` -- (default: None) if set to i, the vertex i is highlighted.
        - ``save_pos`` -- (default:False) if True, the positions of the vertices are saved.

        TESTS::

            sage: Q = ClusterQuiver(['A',5])
            sage: Q.show() # long time
        """
        n, m = self._n, self._m
        plot = self.plot( circular=circular, directed=directed, mark=mark, save_pos=save_pos )
        if circular:
            plot.show( figsize=[fig_size*3*(n+m)/4+1,fig_size*3*(n+m)/4+1] )
        else:
            plot.show( figsize=[fig_size*n+1,fig_size*n+1] )

    def interact(self, fig_size=1, circular=True):
        """
        Only in notebook mode. Starts an interactive window for cluster seed mutations.

        INPUT:

        - ``fig_size`` -- (default: 1) factor by which the size of the plot is multiplied.
        - ``circular`` -- (default: False) if True, the circular plot is chosen, otherwise >>spring<< is used.

        TESTS::

            sage: Q = ClusterQuiver(['A',4])
            sage: Q.interact() # long time
            'The interactive mode only runs in the Sage notebook.'
        """
        from sage.plot.plot import EMBEDDED_MODE
        from sagenb.notebook.interact import interact, selector
        from sage.misc.all import html,latex

        if not EMBEDDED_MODE:
            return "The interactive mode only runs in the Sage notebook."
        else:
            seq = []
            sft = [True]
            sss = [True]
            ssm = [True]
            ssl = [True]
            @interact
            def player(k=selector(values=range(self._n),nrows = 1,label='Mutate at: '), show_seq=("Mutation sequence:", True), show_matrix=("B-Matrix:", True), show_lastmutation=("Show last mutation:", True) ):
                ft,ss,sm,sl = sft.pop(), sss.pop(), ssm.pop(), ssl.pop()
                if ft:
                    self.show(fig_size=fig_size, circular=circular)
                elif show_seq is not ss or show_matrix is not sm or show_lastmutation is not sl:
                    if seq and show_lastmutation:
                        self.show(fig_size=fig_size, circular=circular, mark=seq[len(seq)-1])
                    else:
                        self.show(fig_size=fig_size, circular=circular )
                else:
                    self.mutate(k)
                    seq.append(k)
                    if not show_lastmutation:
                        self.show(fig_size=fig_size, circular=circular)
                    else:
                        self.show(fig_size=fig_size, circular=circular,mark=k)
                sft.append(False)
                sss.append(show_seq)
                ssm.append(show_matrix)
                ssl.append(show_lastmutation)
                if show_seq: html( "Mutation sequence: $" + str( [ seq[i] for i in xrange(len(seq)) ] ).strip('[]') + "$" )
                if show_matrix:
                    html( "B-Matrix:" )
                    m = self._M
                    #m = matrix(range(1,self._n+1),sparse=True).stack(m)
                    m = latex(m)
                    m = m.split('(')[1].split('\\right')[0]
                    html( "$ $" )
                    html( "$\\begin{align*} " + m + "\\end{align*}$" )
                    #html( "$" + m + "$" )
                    html( "$ $" )

    def save_image(self,filename,circular=False):
        """
        Saves the plot of the underlying digraph of ``self``.

        INPUT:

        - ``filename`` -- the filename the image is saved to.
        - ``circular`` -- (default: False) if True, the circular plot is chosen, otherwise >>spring<< is used.

        EXAMPLES::

            sage: Q = ClusterQuiver(['F',4,[1,2]])
            sage: Q.save_image(os.path.join(SAGE_TMP, 'sage.png'))
        """
        graph_plot = self.plot( circular=circular )
        graph_plot.save( filename=filename )

    def qmu_save(self,filename=None):
        """
        Saves a .qmu file of ``self`` that can then be opened in Bernhard Keller's Quiver Applet.

        INPUT:

        - ``filename`` -- the filename the image is saved to.

        If a filename is not specified, the default name is from_sage.qmu in the current sage directory.

        EXAMPLES::

            sage: Q = ClusterQuiver(['F',4,[1,2]])
            sage: Q.qmu_save(os.path.join(SAGE_TMP, 'sage.qmu'))
        """
        M = self.b_matrix()
        if self.m() > 0:
            from sage.matrix.constructor import Matrix
            from sage.matrix.constructor import block_matrix
            M1 = M.matrix_from_rows(range(self.n()))
            M2 = M.matrix_from_rows(range(self.n(),self.n()+self.m()))
            M3 = Matrix(self.m(),self.n())
            M = block_matrix([[M1,-M2.transpose()],[M2,M3]])
        dg = self.digraph()
        dg.plot(save_pos=True)
        PP = dg.get_pos()
        m = M.ncols()
        if filename is None:
            filename = 'from_sage.qmu'
        try:
            self._default_filename = filename
        except AttributeError:
            pass
        if filename[-4:] <> '.qmu':
            filename = filename + '.qmu'
        myfile = open(filename, 'w')
        myfile.write('//Number of points'); myfile.write('\n')
        myfile.write(str(m)); myfile.write('\n')
        myfile.write('//Vertex radius'); myfile.write('\n')
        myfile.write(str(9)); myfile.write('\n')
        myfile.write('//Labels shown'); myfile.write('\n')
        myfile.write(str(1)); myfile.write('\n')
        myfile.write('//Matrix'); myfile.write('\n')
        myfile.write(str(m)); myfile.write(' '); myfile.write(str(m)); myfile.write('\n')
        for i in range(m):
            for j in range(m):
                myfile.write(str(M[i,j])); myfile.write(' ')
            myfile.write('\n')
        myfile.write('//Points'); myfile.write('\n')
        for i in range(m):
            myfile.write(str(9)); myfile.write(' '); myfile.write(str(100*PP[i][0])); myfile.write(' ');
            myfile.write(str(100*PP[i][1]));
            if i > self.n()-1:
                myfile.write(' '); myfile.write(str(1))
            myfile.write('\n')
        myfile.write('//Historycounter'); myfile.write('\n')
        myfile.write(str(-1)); myfile.write('\n')
        myfile.write('//History'); myfile.write('\n'); myfile.write('\n')
        myfile.write('//Cluster is null');
        myfile.close()

    def b_matrix(self):
        """
        Returns the b-matrix of ``self``.

        EXAMPLES::

            sage: ClusterQuiver(['A',4]).b_matrix()
            [ 0  1  0  0]
            [-1  0 -1  0]
            [ 0  1  0  1]
            [ 0  0 -1  0]

            sage: ClusterQuiver(['B',4]).b_matrix()
            [ 0  1  0  0]
            [-1  0 -1  0]
            [ 0  1  0  1]
            [ 0  0 -2  0]

            sage: ClusterQuiver(['D',4]).b_matrix()
            [ 0  1  0  0]
            [-1  0 -1 -1]
            [ 0  1  0  0]
            [ 0  1  0  0]

            sage: ClusterQuiver(QuiverMutationType([['A',2],['B',2]])).b_matrix()
            [ 0  1  0  0]
            [-1  0  0  0]
            [ 0  0  0  1]
            [ 0  0 -2  0]
        """
        return copy( self._M )

    def digraph(self):
        """
        Returns the underlying digraph of ``self``.

        EXAMPLES::

            sage: ClusterQuiver(['A',1]).digraph()
            Digraph on 1 vertex
            sage: ClusterQuiver(['A',1]).digraph().vertices()
            [0]
            sage: ClusterQuiver(['A',1]).digraph().edges()
            []

            sage: ClusterQuiver(['A',4]).digraph()
            Digraph on 4 vertices
            sage: ClusterQuiver(['A',4]).digraph().edges()
            [(0, 1, (1, -1)), (2, 1, (1, -1)), (2, 3, (1, -1))]

            sage: ClusterQuiver(['B',4]).digraph()
            Digraph on 4 vertices
            sage: ClusterQuiver(['A',4]).digraph().edges()
            [(0, 1, (1, -1)), (2, 1, (1, -1)), (2, 3, (1, -1))]

            sage: ClusterQuiver(QuiverMutationType([['A',2],['B',2]])).digraph()
            Digraph on 4 vertices

            sage: ClusterQuiver(QuiverMutationType([['A',2],['B',2]])).digraph().edges()
            [(0, 1, (1, -1)), (2, 3, (1, -2))]
        """
        return copy( self._digraph )

    def mutation_type(self):
        """
        Returns the mutation type of ``self``.

        EXAMPLES::

            sage: ClusterQuiver(['A',4]).mutation_type()
            ['A', 4]
            sage: ClusterQuiver(['A',(3,1),1]).mutation_type()
            ['A', [1, 3], 1]
            sage: ClusterQuiver(['C',2]).mutation_type()
            ['B', 2]
            sage: ClusterQuiver(['B',4,1]).mutation_type()
            ['BD', 4, 1]
        """
        return self._mutation_type

    def n(self):
        """
        Returns the number of free vertices of ``self``.

        EXAMPLES::

            sage: ClusterQuiver(['A',4]).n()
            4
            sage: ClusterQuiver(['A',(3,1),1]).n()
            4
            sage: ClusterQuiver(['B',4]).n()
            4
            sage: ClusterQuiver(['B',4,1]).n()
            5
        """
        return self._n

    def m(self):
        """
        Returns the number of frozen vertices of ``self``.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',4])
            sage: Q.m()
            0

            sage: T = ClusterQuiver( Q.digraph().edges(), frozen=1 )
            sage: T.n()
            3
            sage: T.m()
            1
        """
        return self._m

    def canonical_label( self, certify=False ):
        """
        Returns the canonical labelling of ``self``, see sage.graphs.graph.GenericGraph.canonical_label.

        INPUT:

        - ``certify`` -- (default: False) if True, the dictionary from ``self.vertices()`` to the vertices of the returned quiver is returned as well.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',4]); Q.digraph().edges()
            [(0, 1, (1, -1)), (2, 1, (1, -1)), (2, 3, (1, -1))]

            sage: T = Q.canonical_label(); T.digraph().edges()
            [(0, 3, (1, -1)), (1, 2, (1, -1)), (1, 3, (1, -1))]

            sage: T,iso = Q.canonical_label(certify=True); T.digraph().edges(); iso
            [(0, 3, (1, -1)), (1, 2, (1, -1)), (1, 3, (1, -1))]
            {0: 0, 1: 3, 2: 1, 3: 2}

            sage: Q = ClusterQuiver(QuiverMutationType([['B',2],['A',1]])); Q
            Quiver on 3 vertices of type [ ['B', 2], ['A', 1] ]

            sage: Q.canonical_label()
            Quiver on 3 vertices of type [ ['A', 1], ['B', 2] ]

            sage: Q.canonical_label(certify=True)
            (Quiver on 3 vertices of type [ ['A', 1], ['B', 2] ], {0: 1, 1: 2, 2: 0})
        """
        n = self._n
        m = self._m

        # computing the canonical form respecting the frozen variables
        dg = copy( self._digraph )
        iso, orbits = _dg_canonical_form( dg, n, m )
        Q = ClusterQuiver( dg )
        # getting the new ordering for the mutation type if necessary
        if self._mutation_type:
            if dg.is_connected():
                Q._mutation_type = self._mutation_type
            else:
                CC = sorted( self._digraph.connected_components() )
                CC_new = sorted( zip( [ sorted( [ iso[i] for i in L ] ) for L in CC ], range( len( CC ) ) ) )
                comp_iso = [ L[1] for L in CC_new ]
                Q._mutation_type = []
                for i in range( len( CC_new ) ):
                    Q._mutation_type.append( copy( self._mutation_type.irreducible_components()[ comp_iso[i] ] ) )
                Q._mutation_type = QuiverMutationType( Q._mutation_type )
        if certify:
            return Q, iso
        else:
            return Q

    def is_acyclic(self):
        """
        Returns true if ``self`` is acyclic.

        EXAMPLES::

            sage: ClusterQuiver(['A',4]).is_acyclic()
            True

            sage: ClusterQuiver(['A',[2,1],1]).is_acyclic()
            True

            sage: ClusterQuiver([[0,1],[1,2],[2,0]]).is_acyclic()
            False
        """
        return self._digraph.is_directed_acyclic()

    def is_bipartite(self,return_bipartition=False):
        """
        Returns true if ``self`` is bipartite.

        EXAMPLES::

            sage: ClusterQuiver(['A',[3,3],1]).is_bipartite()
            True

            sage: ClusterQuiver(['A',[4,3],1]).is_bipartite()
            False
        """
        dg = copy( self._digraph )
        dg.delete_vertices( range(self._n,self._n+self._m) )
        innie = dg.in_degree()
        outie = dg.out_degree()
        is_bip = sum( [ innie[i]*outie[i] for i in range(len(innie)) ] ) == 0
        if not is_bip:
            return False
        else:
            if not return_bipartition:
                return True
            else:
                g = dg.to_undirected()
                return g.bipartite_sets()

    def exchangeable_part(self):
        """
        Returns the restriction to the principal part (i.e. exchangeable part) of ``self``, the subquiver obtained by deleting the frozen vertices of ``self``.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',4])
            sage: T = ClusterQuiver( Q.digraph().edges(), frozen=1 )
            sage: T.digraph().edges()
            [(0, 1, (1, -1)), (2, 1, (1, -1)), (2, 3, (1, -1))]

            sage: T.exchangeable_part().digraph().edges()
            [(0, 1, (1, -1)), (2, 1, (1, -1))]

            sage: Q2 = Q.principal_extension()
            sage: Q3 = Q2.principal_extension()
            sage: Q2.exchangeable_part() == Q3.exchangeable_part()
            True
        """
        dg = DiGraph( self._digraph )
        dg.delete_vertices( range(self._n,self._n+self._m) )
        Q = ClusterQuiver( dg )
        Q._mutation_type = self._mutation_type
        return Q

    def principal_extension(self, inplace=False):
        """
        Returns the principal extension of ``self``, adding n frozen vertices to any previously frozen vertices. I.e., the quiver obtained by adding an outgoing edge to every mutable vertex of ``self``.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',2]); Q
            Quiver on 2 vertices of type ['A', 2]
            sage: T = Q.principal_extension(); T
            Quiver on 4 vertices of type ['A', 2] with 2 frozen vertices
            sage: T2 = T.principal_extension(); T2
            Quiver on 6 vertices of type ['A', 2] with 4 frozen vertices
            sage: Q.digraph().edges()
            [(0, 1, (1, -1))]
            sage: T.digraph().edges()
            [(0, 1, (1, -1)), (2, 0, (1, -1)), (3, 1, (1, -1))]
            sage: T2.digraph().edges()
            [(0, 1, (1, -1)), (2, 0, (1, -1)), (3, 1, (1, -1)), (4, 0, (1, -1)), (5, 1, (1, -1))]
        """
        dg = DiGraph( self._digraph )
        dg.add_edges( [(self._n+self._m+i,i) for i in range(self._n)] )
        Q = ClusterQuiver( dg, frozen=self._m+self._n )
        Q._mutation_type = self._mutation_type
        if inplace:
            self.__init__(Q)
        else:
            return Q

    def mutate(self, data, inplace=True):
        """
        Mutates ``self`` at a sequence of vertices.

        INPUT:

        - ``sequence`` -- a vertex of ``self`` or an iterator of vertices of ``self``.
        - ``inplace`` -- (default: True) if False, the result is returned, otherwise ``self`` is modified.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',4]); Q.b_matrix()
            [ 0  1  0  0]
            [-1  0 -1  0]
            [ 0  1  0  1]
            [ 0  0 -1  0]

            sage: Q.mutate(0); Q.b_matrix()
            [ 0 -1  0  0]
            [ 1  0 -1  0]
            [ 0  1  0  1]
            [ 0  0 -1  0]

            sage: T = Q.mutate(0, inplace=False); T
            Quiver on 4 vertices of type ['A', 4]

            sage: Q.mutate(0)
            sage: Q == T
            True

            sage: Q.mutate([0,1,0])
            sage: Q.b_matrix()
            [ 0 -1  1  0]
            [ 1  0  0  0]
            [-1  0  0  1]
            [ 0  0 -1  0]

            sage: Q = ClusterQuiver(QuiverMutationType([['A',1],['A',3]]))
            sage: Q.b_matrix()
            [ 0  0  0  0]
            [ 0  0  1  0]
            [ 0 -1  0 -1]
            [ 0  0  1  0]

            sage: T = Q.mutate(0,inplace=False)
            sage: Q == T
            True

        TESTS::

            sage: Q = ClusterQuiver(['A',4]); Q.mutate(0,1)
            Traceback (most recent call last):
            ...
            ValueError: The second parameter must be boolean.  To mutate at a sequence of length 2, input it as a list.

            sage: Q = ClusterQuiver(['A',4]); Q.mutate(0,0)
            Traceback (most recent call last):
            ...
            ValueError: The second parameter must be boolean.  To mutate at a sequence of length 2, input it as a list.
        """
        n = self._n
        m = self._m
        dg = self._digraph
        V = range(n)

        if data in V:
            seq = [data]
        else:
            seq = data
        if type( seq ) is tuple:
            seq = list( seq )
        if not type( seq ) is list:
            raise ValueError, 'The quiver can only be mutated at a vertex or at a sequence of vertices'
        if not type(inplace) is bool:
            raise ValueError, 'The second parameter must be boolean.  To mutate at a sequence of length 2, input it as a list.'
        if any( v not in V for v in seq ):
            v = filter( lambda v: v not in V, seq )[0]
            raise ValueError, 'The quiver cannot be mutated at the vertex ' + str( v )

        for v in seq:
            dg = _digraph_mutate( dg, v, n, m )
        M = _edge_list_to_matrix( dg.edge_iterator(), n, m )
        if inplace:
            self._M = M
            self._digraph = dg
        else:
            Q = ClusterQuiver( M )
            Q._mutation_type = self._mutation_type
            return Q

    def mutation_sequence(self, sequence, show_sequence=False, fig_size=1.2 ):
        """
        Returns a list containing the sequence of quivers obtained from ``self`` by a sequence of mutations on vertices.

        INPUT:

        - ``sequence`` -- a list or tuple of vertices of ``self``.
        - ``show_sequence`` -- (default: False) if True, a png containing the mutation sequence is shown.
        - ``fig_size`` -- (default: 1.2) factor by which the size of the sequence is expanded.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',4])
            sage: seq = Q.mutation_sequence([0,1]); seq
            [Quiver on 4 vertices of type ['A', 4], Quiver on 4 vertices of type ['A', 4], Quiver on 4 vertices of type ['A', 4]]
            sage: [T.b_matrix() for T in seq]
            [
            [ 0  1  0  0]  [ 0 -1  0  0]  [ 0  1 -1  0]
            [-1  0 -1  0]  [ 1  0 -1  0]  [-1  0  1  0]
            [ 0  1  0  1]  [ 0  1  0  1]  [ 1 -1  0  1]
            [ 0  0 -1  0], [ 0  0 -1  0], [ 0  0 -1  0]
            ]
        """
        from sage.plot.plot import Graphics
        from sage.plot.text import text
        n = self._n
        m = self._m
        if m == 0:
            width_factor = 3
            fig_size = fig_size*2*n/3
        else:
            width_factor = 6
            fig_size = fig_size*4*n/3
        V = range(n)

        if type( sequence ) is tuple:
            sequence = list( sequence )
        if not type( sequence ) is list:
            raise ValueError, 'The quiver can only be mutated at a vertex or at a sequence of vertices'
        if any( v not in V for v in sequence ):
            v = filter( lambda v: v not in V, sequence )[0]
            raise ValueError, 'The quiver can only be mutated at the vertex ' + str( v )

        quiver = copy( self )
        quiver_sequence = []
        quiver_sequence.append( copy( quiver ) )

        for v in sequence:
            quiver.mutate( v )
            quiver_sequence.append( copy( quiver ) )

        if show_sequence:
            def _plot_arrow( v, k, center=(0,0) ):
                return text("$\longleftrightarrow$",(center[0],center[1]), fontsize=25) + text("$\mu_"+str(v)+"$",(center[0],center[1]+0.15), fontsize=15) \
                    + text("$"+str(k)+"$",(center[0],center[1]-0.2), fontsize=15)
            plot_sequence = [ quiver_sequence[i].plot( circular=True, center=(i*width_factor,0) ) for i in range(len(quiver_sequence)) ]
            arrow_sequence = [ _plot_arrow( sequence[i],i+1,center=((i+0.5)*width_factor,0) ) for i in range(len(sequence)) ]
            sequence = []
            for i in xrange( len( plot_sequence ) ):
                if i < len( arrow_sequence ):
                    sequence.append( plot_sequence[i] + arrow_sequence[i] )
                else:
                    sequence.append( plot_sequence[i] )
            plot_obj = Graphics()
            for elem in sequence:
                plot_obj += elem
            plot_obj.show(axes=False, figsize=[fig_size*len(quiver_sequence),fig_size])
        return quiver_sequence

    def reorient( self, data ):
        """
        Reorients ``self`` with respect to the given total order, or with respect to an iterator of edges in ``self`` to be reverted.

        WARNING::

            This operation might change the mutation type of ``self``.

        INPUT:

        - ``data`` -- an iterator defining a total order on ``self.vertices()``, or an iterator of edges in ``self`` to be reoriented.

        EXAMPLES::

            sage: Q = ClusterQuiver(['A',(2,3),1])

            sage: Q.reorient([(0,1),(1,2),(2,3),(3,4)])

            sage: Q.reorient([0,1,2,3,4])
        """
        if all( 0 <= i and i < self._n + self._m for i in data ) and len( set( data ) ) == self._n+self._m :
            dg_new = DiGraph()
            for edge in self._digraph.edges():
                if data.index( edge[0] ) < data.index( edge[1] ):
                    dg_new.add_edge( edge[0],edge[1],edge[2] )
                else:
                    dg_new.add_edge( edge[1],edge[0],edge[2] )
            self._digraph = dg_new
            self._M = _edge_list_to_matrix( dg_new.edges(), self._n, self._m )
            self._mutation_type = None
        elif all( type(edge) in [list,tuple] and len(edge)==2 for edge in data ):
            edges = self._digraph.edges(labels=False)
            for edge in data:
                if (edge[1],edge[0]) in edges:
                    label = self._digraph.edge_label(edge[1],edge[0])
                    self._digraph.delete_edge(edge[1],edge[0])
                    self._digraph.add_edge(edge[0],edge[1],label)
            self._M = _edge_list_to_matrix( self._digraph.edges(), self._n, self._m )
            self._mutation_type = None
        else:
            raise ValueError, 'The order is no total order on the vertices of the quiver or a list of edges to be oriented.'
