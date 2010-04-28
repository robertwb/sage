r"""
LaTeX Options for Graphs

This module provides a class to hold, manipulate and employ various
options for rendering a graph in `\mbox{\rm\LaTeX}`.

AUTHORS:

- Robert Beezer (2009-05-20): :class:`~sage.graphs.graph_latex.GraphLatex` class
- Fidel Barerra Cruz (2009-05-20): ``tkz-graph`` commands to render a graph
- Nicolas M. Thiery (2010-02): dot2tex/graphviz interface

LaTeX Versions of Graphs
-------------------------------------

Many mathematical objects in Sage have `\mbox{\rm\LaTeX}` representations, and graphs are no exception.  For a graph ``g``, the command ``view(g)`` or ``view(g, pdflatex=True)``, issued at the Sage command line or in the notebook, will create a graphic version of ``g``.  Similarly, ``latex(g)`` will return a (long) string that is a representation of the graph in `\mbox{\rm\LaTeX}`.  Other ways of employing `\mbox{\rm\LaTeX}` in Sage, such as ``%latex`` in a notebook cell, or the Typeset checkbox in the notebook, will handle ``g`` appropriately.

To use `\mbox{\rm\LaTeX}` in Sage you of course need a working `\mbox{\rm\TeX}` installation and it will work best if you have the ``dvipng`` and ``convert`` utilities.  For graphs you need the ``tkz-graph.sty`` and ``tkz-berge.sty`` style files of the  tkz-graph package.  You can find these at:

- `\mbox{\rm\TeX}`: http://ctan.org/
- dvipng: http://sourceforge.net/projects/dvipng/
- convert: http://www.imagemagick.org (the ImageMagick suite)
- tkz-graph: http://altermundus.com/pages/graph.html

Customizing the output is accomplished in several ways.  Suppose ``g`` is a graph, then ``g.set_latex_options()`` can be used to efficiently set or modify various options.  Setting individual options, or querying options, can be accomplished by first using a command like ``opts = g.latex_options()`` to obtain a :class:`sage.graphs.graph_latex.GraphLatex` object which has several methods to set and retrieve options.  The following session illustrates the use of these commands.  The full output of ``latex(g)`` is not included, but the two calls would produce different output due to the change of the style.

The range of possible options are carefully documented at :meth:`sage.graphs.graph_latex.GraphLatex.set_option`.

EXAMPLES:

An example using the tkz_graph format::

    sage: g = graphs.PetersenGraph()
    sage: g.set_latex_options(tkz_style = 'Classic')
    sage: from sage.graphs.graph_latex import check_tkz_graph
    sage: check_tkz_graph()  # random - depends on TeX installation
    sage: latex(g)
    \begin{tikzpicture}
    ...
    \end{tikzpicture}
    sage: opts = g.latex_options()
    sage: opts
    LaTeX options for Petersen graph: {'tkz_style': 'Classic'}
    sage: opts.set_option('tkz_style', 'Art')
    sage: opts.get_option('tkz_style')
    'Art'
    sage: opts
    LaTeX options for Petersen graph: {'tkz_style': 'Art'}
    sage: latex(g)
    \begin{tikzpicture}
    ...
    \end{tikzpicture}

An example using the optional dot2tex module::

    sage: g = graphs.PetersenGraph()
    sage: g.set_latex_options(format='dot2tex',prog='neato') # optional - requires dot2tex
    sage: latex(g) # optional - requires dot2tex
    \begin{tikzpicture}[>=latex,line join=bevel,]
    ...
    \end{tikzpicture}

GraphLatex class and functions
------------------------------
"""
#*****************************************************************************
#      Copyright (C) 2009   Robert Beezer <beezer@ups.edu>
#                    2009   Fidel Barrera Cruz <fidel.barrera@gmail.com>
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
#*****************************************************************************
from sage.structure.sage_object import SageObject
from sage.misc.cachefunc import cached_function
from sage.misc.latex import latex

def check_tkz_graph():
    r"""
    Checks if the proper `\mbox{\rm\LaTeX}`
    packages for the ``tikzpicture`` environment are
    installed in the user's environment, and issue
    a warning otherwise.

    The warning is only issued on the first call to this function. So
    any doctest that illustrates the use of the tkz-graph packages
    should call this once as having random output to exhaust the
    warnings before testing output.

    See also :meth:`sage.misc.latex.check_file`

    TESTS::

        sage: from sage.graphs.graph_latex import check_tkz_graph
        sage: check_tkz_graph()  # random - depends on TeX installation
        sage: check_tkz_graph()  # at least the second time, so no output
    """
    latex.check_file("tikz.sty", """This package is required to render graphs in LaTeX.
Visit '...'.
""")
    latex.check_file("tkz-graph.sty", """This package is required to render graphs in LaTeX.
Visit 'http://altermundus.com/pages/graph.html'.
""")
    latex.check_file("tkz-berge.sty", """This package is required to render graphs in LaTeX.
Visit 'http://altermundus.com/pages/graph.html'.
""")

def have_tkz_graph():
    r"""
    Returns ``True`` if the proper `\mbox{\rm\LaTeX}` packages
    for the ``tikzpicture`` environment are installed in the
    user's environment, namely tikz, tkz-graph and tkz-berge.

    The result is cached.

    See also :meth:`sage.misc.latex.has_file`

    TESTS::

        sage: from sage.graphs.graph_latex import have_tkz_graph
        sage: have_tkz_graph()  # random - depends on TeX installation
        sage: have_tkz_graph() in [True, False]
        True
    """
    return latex.has_file("tikz.sty") and latex.has_file("tkz-graph.sty") and latex.has_file("tkz-berge.sty")

@cached_function
def setup_latex_preamble():
    """
    Adds appropriate ``\usepackage{...}`` instructions to the latex
    preamble for the packages that are needed for processing graphs
    (``tikz``, ``tkz-graph``, ``tkz-berge``), if the later are
    available in the ``LaTeX`` installation.

    See also :meth:`sage.misc.latex.add_package_to_preamble_if_available`.

    EXAMPLES::

        sage: sage.graphs.graph_latex.setup_latex_preamble()

    TESTS::

        sage: ("\\usepackage{tikz}" in latex.extra_preamble()) == latex.has_file("tikz.sty")
        True
    """
    latex.add_package_to_preamble_if_available("tikz")
    latex.add_package_to_preamble_if_available("tkz-graph")
    latex.add_package_to_preamble_if_available("tkz-berge")

class GraphLatex(SageObject):
    r"""
    A class to hold, manipulate and employ options for converting
    a graph to `\mbox{\rm\LaTeX}`.

    This class serves two purposes.  First it holds the values of
    various options designed to work with the ``tkz-graph``
    `\mbox{\rm\LaTeX}` package for rendering graphs.  As such, a
    graph that uses this class will hold a reference to it. Second,
    this class contains the code to convert a graph into the
    corresponding `\mbox{\rm\LaTeX}` constructs, returning a string.

    EXAMPLES::

        sage: from sage.graphs.graph_latex import GraphLatex
        sage: opts = GraphLatex(graphs.PetersenGraph())
        sage: opts
        LaTeX options for Petersen graph: {}
        sage: g = graphs.PetersenGraph()
        sage: opts = g.latex_options()
        sage: g == loads(dumps(g))
        True
    """

    #  These are the "allowed" options for a graph, private to the class,
    #  along with their default value and description
    #  This allows intelligent errors when non-existent options are referenced
    #  Additionally, for each new option added here:
    #    1.  Document values in GraphLatex.set_option() docstring
    #    2.  Describe also in docstring for the sage.graphs.graph_latex module
    #
    # TODO: use some standard option handling mechanism
    # This dictionary could also contain type information (list of admissible values)
    # and a description
    # See e.g. @option
    __graphlatex_options = {
            'tkz_style': 'Normal',
            'format': 'tkz_graph',
            'layout': 'acyclic',
            'prog': 'dot',
            'edge_color': None,
            'edge_colors': None,
            'edge_labels': False,
            'color_by_label': False,
            }

    def __init__(self, graph, **options):
        r"""
        Returns a GraphLatex object, which holds all the parameters needed for
        creating a `\mbox{\rm\LaTeX}` string that will be rendered as a picture of the graph.

        See :mod:`sage.graphs.graph_latex` for more documentation.

        EXAMPLES::

            sage: from sage.graphs.graph_latex import GraphLatex
            sage: GraphLatex(graphs.PetersenGraph())
            LaTeX options for Petersen graph: {}
        """
        self._graph = graph
        self._options = {}
        self.set_options(**options)

    def __eq__(self, other):
        r"""
        Two :class:`sage.graphs.graph_latex.GraphLatex` objects
        are equal if their options are equal.

        The graphs they are associated with are ignored in the comparison.

        TESTS::

            sage: from sage.graphs.graph_latex import GraphLatex
            sage: opts1 = GraphLatex(graphs.PetersenGraph())
            sage: opts2 = GraphLatex(graphs.CompleteGraph(10))
            sage: opts1.set_option('tkz_style', 'Art')
            sage: opts2.set_option('tkz_style', 'Art')
            sage: opts1 == opts2
            True
            sage: opts2.set_option('tkz_style', 'Normal')
            sage: opts1 == opts2
            False
        """
        if not(isinstance(other, GraphLatex)):
            return False
        else:
            return self._options == other._options

    def _repr_(self):
        r"""
        Returns a string representation of a
        :class:`sage.graphs.graph_latex.GraphLatex` object
        which includes the name of the graph and the dictionary
        of current options.

        EXAMPLES::

            sage: g = graphs.PetersenGraph()
            sage: opts = g.latex_options()
            sage: opts.set_option('tkz_style', 'foo')
            sage: print opts._repr_()
            LaTeX options for Petersen graph: {'tkz_style': 'foo'}
        """
        return "LaTeX options for %s: %s"%(self._graph, self._options)

    def set_option(self, option_name, option_value = None):
        r"""
        Sets, modifies, clears a legitimate `\mbox{\rm\LaTeX}`
        option for rendering a graph.

        INPUTS:

        - ``option_name`` - a string for a latex option contained in
          the list :data:`__graphlatex_options`. A ``ValueError`` is
          raised if the option is not allowed.

        - ``option_value`` - a value for the option.  If omitted, or
          set to ``None``, the option is totally removed
          (i.e. cleared).  The value is not checked here for
          correctness, but rather it is checked where it is employed.

        The output can be either handled internaly by ``Sage``, or
        delegated to the external software ``dot2tex`` and
        ``graphviz``. This is controlled by the option 'format':

         - format -- 'dot2tex' or 'tkz_graph' (default: 'tkz_graph').
           (TODO: find a better name)

        Note: If format is 'dot2tex', then all the LaTeX generation
        will be delegated to `dot2tex` (which must be installed).

        For ``tkz_graph``, the possible option names, and associated
        values are given below. For precise details consult the
        documentation for the ``tkz-graph`` package:

        - ``tkz_style`` -- a pre-defined ``tkz-graph`` style such as "Art"
          or "Normal".  Currently, the recognized styles are "Shade",
          "Art", "Normal", "Dijkstra", "Welsh", "Classic", and
          "Simple".  Any other value will not give an error, but if
          you run ``latex`` on the graph, then an unrecognized style
          will be treated as "Normal" (only for tkz_graph format).

        - ``layout`` -- the layout used for coordinates of the vertices

        For the 'dot2tex' format, the possible option names and
        associated values are given below:

        - ``prog`` -- the program used for the layout. It must be a
          string corresponding to one of the software of the graphviz
          suite: 'dot', 'neato', 'twopi', 'circo' or 'fdp'.

        - ``edge_label`` -- a boolean (default: False). Whether to
          display the labels on edges.

        - ``edge_colors`` -- a color. Can be used to set a global
          color to the edge of the graph.

        - color_by_label - a boolean (default: False). Colors the
          edges according to their labels (only for dot2tex format)


        EXAMPLES:

        Set, then modify, then clear the ``tkz_style`` option, and
        finally show an error for an unrecognized option name::

            sage: g = graphs.PetersenGraph()
            sage: opts = g.latex_options()
            sage: opts
            LaTeX options for Petersen graph: {}
            sage: opts.set_option('tkz_style', 'foo')
            sage: opts
            LaTeX options for Petersen graph: {'tkz_style': 'foo'}
            sage: opts.set_option('tkz_style', 'bar')
            sage: opts
            LaTeX options for Petersen graph: {'tkz_style': 'bar'}
            sage: opts.set_option('tkz_style')
            sage: opts
            LaTeX options for Petersen graph: {}
            sage: opts.set_option('bad_name', 'nonsense')
            Traceback (most recent call last):
            ...
            ValueError: bad_name is not a LaTeX option for a graph.

        See :meth:`Graph.layout_graphviz` for installation
        instructions for ``graphviz`` and ``dot2tex``. Further more,
        pgf >= 2.00 should be available inside LaTeX's tree for LaTeX
        compilation (e.g. when using ``view``). In case your LaTeX
        distribution does not provide it, here are short instructions:

           - download pgf from http://sourceforge.net/projects/pgf/
           - unpack it in ``/usr/share/texmf/tex/generic`` (depends on your system)
           - clean out remaining pgf files from older version
           - run texhash
        """
        if not(option_name in GraphLatex.__graphlatex_options):
            raise ValueError( "%s is not a LaTeX option for a graph." % option_name )
        if option_value == None:    # clear the option, if set
            if option_name in self._options:
                del self._options[option_name]
        else:
            self._options[option_name] = option_value

    def set_options(self, **kwds):
        r"""
        Set several `\mbox{\rm\LaTeX}` options for a graph all at once.

        INPUTS:

         - kwds - any number of option/value pairs to se many graph latex
           options at once (a variable number, in any order). Existing
           values are overwritten, new values are added.  Existing
           values can be cleared by setting the value to ``None``.
           Errors are raised in the :func:`set_option` method.

        EXAMPLES::

            sage: g = graphs.PetersenGraph()
            sage: opts = g.latex_options()
            sage: opts.set_options(tkz_style = 'Welsh')
            sage: opts.get_option('tkz_style')
            'Welsh'
        """
        if kwds:
            for name, value in kwds.items():
                self.set_option(name, value)

    def get_option(self, option_name):
        r"""
        Returns the current value of the named option.

        INPUT:

        - option_name - the name of an option

        OUTPUT:

        If the name is not present in
        :data:`sage.graphs.graph_latex.__graphlatex_options` it is an
        error to ask for it.  If an option has not been set then the
        default value is returned. Otherwise, the value of the
        option is returned.

        EXAMPLES::

            sage: g = graphs.PetersenGraph()
            sage: opts = g.latex_options()
            sage: opts.set_option('tkz_style', 'Art')
            sage: opts.get_option('tkz_style')
            'Art'
            sage: opts.set_option('tkz_style')
            sage: opts.get_option('tkz_style') == "Normal"
            True
            sage: opts.get_option('bad_name')
            Traceback (most recent call last):
            ...
            ValueError: bad_name is not a Latex option for a graph.
        """
        if not(option_name in GraphLatex.__graphlatex_options):
            raise ValueError( "%s is not a Latex option for a graph." % option_name )
        else:
            if option_name in self._options:
                return self._options[option_name]
            else:
                return GraphLatex.__graphlatex_options[option_name]

    def latex(self):
        r"""
        Returns a string in `\mbox{\rm\LaTeX}` representing a graph.

        This is the command that is invoked by
        :meth:`~sage.graphs.graph.GenericGraph._latex_` for
        a graph, so it returns a string of
        `\mbox{\rm\LaTeX}` commands that can be incorporated
        into a `\mbox{\rm\LaTeX}` document unmodified.  The exact contents
        of this string are influenced by the options set via the methods
        :meth:`sage.graphs.graph.GenericGraph.set_latex_options`,
        :meth:`set_option`, and :meth:`set_options`.

        Right now it only calls one procedure for creating strings using the
        tkz-graph package, but by passing in an option and implementing a new
        procedure, other packages could be supported in the future.

        EXAMPLES::

            sage: from sage.graphs.graph_latex import check_tkz_graph
            sage: check_tkz_graph()  # random - depends on TeX installation
            sage: g = graphs.CompleteGraph(2)
            sage: opts = g.latex_options()
            sage: print opts.latex()
            \begin{tikzpicture}
            %
            \definecolor{col_a0}{rgb}{1.0,1.0,1.0}
            \definecolor{col_a1}{rgb}{1.0,1.0,1.0}
            %
            %
            \definecolor{col_lab_a0}{rgb}{0.0,0.0,0.0}
            \definecolor{col_lab_a1}{rgb}{0.0,0.0,0.0}
            %
            %
            \definecolor{col_a0-a1}{rgb}{0.0,0.0,0.0}
            %
            %
            \GraphInit[vstyle=Normal]
            %
            \SetVertexMath
            %
            \SetVertexNoLabel
            %
            \renewcommand*{\VertexLightFillColor}{col_a0}
            \Vertex[x=5.0cm,y=5.0cm]{a0}
            \renewcommand*{\VertexLightFillColor}{col_a1}
            \Vertex[x=0.0cm,y=0.0cm]{a1}
            %
            %
            \AssignVertexLabel{a}{2}{
            \color{col_lab_a0}{$0$},
            \color{col_lab_a1}{$1$}
            }
            %
            %
            \renewcommand*{\EdgeColor}{col_a0-a1}
            \Edge(a0)(a1)
            %
            %
            \end{tikzpicture}
        """
        # Possibly use options in the future to select
        # the use of different latex packages here
        format = self.get_option('format')
        if format  == "tkz_graph":
            return self.tkz_picture()
        elif format == "dot2tex":
            return self.dot2tex_picture()
        else:
            raise ValueError, "unknown format: %s"%format

    def dot2tex_picture(self):
        r"""
        Calls dot2tex to construct a string of `\mbox{\rm\LaTeX}` commands
        representing a graph as a ``tikzpicture``.

        EXAMPLES::

            sage: g = digraphs.ButterflyGraph(1)
            sage: print g.latex_options().dot2tex_picture()  # optional - requires dot2tex and graphviz
            \begin{tikzpicture}[>=latex,line join=bevel,]
            %%
              \node ('0'+1) at (60bp,9bp) [draw,draw=none] {$\left(\text{0}, 1\right)$};
              \node ('0'+0) at (14bp,63bp) [draw,draw=none] {$\left(\text{0}, 0\right)$};
              \node ('1'+0) at (60bp,63bp) [draw,draw=none] {$\left(\text{1}, 0\right)$};
              \node ('1'+1) at (14bp,9bp) [draw,draw=none] {$\left(\text{1}, 1\right)$};
              \draw [->] ('1'+0) ..controls (60bp,47bp) and (60bp,37bp)  .. ('0'+1);
              \draw [->] ('0'+0) ..controls (29bp,46bp) and (38bp,35bp)  .. ('0'+1);
              \draw [->] ('0'+0) ..controls (14bp,47bp) and (14bp,37bp)  .. ('1'+1);
              \draw [->] ('1'+0) ..controls (45bp,46bp) and (36bp,35bp)  .. ('1'+1);
            %
            \end{tikzpicture}


        Note: there is a lot of overlap between what tkz_picture and
        dot2tex do. It would be best to merge them! dot2tex probably
        can work without graphviz if layout information is provided.
        """
        from sage.graphs.dot2tex_utils import assert_have_dot2tex
        assert_have_dot2tex()

        options = self.__graphlatex_options.copy()
        options.update(self._options)
        dotdata = self._graph.graphviz_string(labels="latex", **options)
        import dot2tex
        return dot2tex.dot2tex(
                dotdata,
                format = 'tikz',
                autosize = True,
                crop = True,
                figonly = 'True',
                prog=self.get_option('prog'))
        # usepdflatex = True, debug = True)

    def tkz_picture(self):
        r"""
        Return a string of `\mbox{\rm\LaTeX}` commands representing a graph as a ``tikzpicture``.

        This routine interprets the graph's properties and the options in
        ``_options`` to render the graph with commands from the ``tkz-graph``
        `\mbox{\rm\LaTeX}` package.

        This requires that the `\mbox{\rm\LaTeX}` optional packages
        tkz-graph and tkz-berge be installed.  You may also need a
        current version of the pgf package.  If the tkz-graph and
        tkz-berge packages are present in the system's TeX
        installation, the appropriate ``\\usepackage{}`` commands
        will be added to the `\mbox{\rm\LaTeX}` preamble as part of
        the initialization of the graph. If these two packages
        are not present, then this command will return a warning
        on its first use, but will return a string that could be
        used elsewhere, such as a `\mbox{\rm\LaTeX}` document.

        For more information about tkz-graph you can visit
        http://altermundus.com/pages/graph.html

        EXAMPLES::

            sage: from sage.graphs.graph_latex import check_tkz_graph
            sage: check_tkz_graph()  # random - depends on TeX installation
            sage: g = graphs.CompleteGraph(3)
            sage: opts = g.latex_options()
            sage: print opts.tkz_picture()
            \begin{tikzpicture}
            %
            \definecolor{col_a0}{rgb}{1.0,1.0,1.0}
            \definecolor{col_a1}{rgb}{1.0,1.0,1.0}
            \definecolor{col_a2}{rgb}{1.0,1.0,1.0}
            %
            %
            \definecolor{col_lab_a0}{rgb}{0.0,0.0,0.0}
            \definecolor{col_lab_a1}{rgb}{0.0,0.0,0.0}
            \definecolor{col_lab_a2}{rgb}{0.0,0.0,0.0}
            %
            %
            \definecolor{col_a0-a1}{rgb}{0.0,0.0,0.0}
            \definecolor{col_a0-a2}{rgb}{0.0,0.0,0.0}
            \definecolor{col_a1-a2}{rgb}{0.0,0.0,0.0}
            %
            %
            \GraphInit[vstyle=Normal]
            %
            \SetVertexMath
            %
            \SetVertexNoLabel
            %
            \renewcommand*{\VertexLightFillColor}{col_a0}
            \Vertex[x=2.5cm,y=5.0cm]{a0}
            \renewcommand*{\VertexLightFillColor}{col_a1}
            \Vertex[x=0.0cm,y=0.0cm]{a1}
            \renewcommand*{\VertexLightFillColor}{col_a2}
            \Vertex[x=5.0cm,y=0.0cm]{a2}
            %
            %
            \AssignVertexLabel{a}{3}{
            \color{col_lab_a0}{$0$},
            \color{col_lab_a1}{$1$},
            \color{col_lab_a2}{$2$}
            }
            %
            %
            \renewcommand*{\EdgeColor}{col_a0-a1}
            \Edge(a0)(a1)
            \renewcommand*{\EdgeColor}{col_a0-a2}
            \Edge(a0)(a2)
            \renewcommand*{\EdgeColor}{col_a1-a2}
            \Edge(a1)(a2)
            %
            %
            \end{tikzpicture}

        TESTS:

        Graphs with preset layouts that are vertical or horizontal
        can cause problems. First test is a horizontal layout on a
        path with three vertices. ::

            sage: from sage.graphs.graph_latex import check_tkz_graph
            sage: check_tkz_graph()  # random - depends on TeX installation
            sage: g = graphs.PathGraph(3)
            sage: opts = g.latex_options()
            sage: print opts.tkz_picture()
            \begin{tikzpicture}
            %
            \definecolor{col_a0}{rgb}{1.0,1.0,1.0}
            \definecolor{col_a1}{rgb}{1.0,1.0,1.0}
            \definecolor{col_a2}{rgb}{1.0,1.0,1.0}
            %
            %
            \definecolor{col_lab_a0}{rgb}{0.0,0.0,0.0}
            \definecolor{col_lab_a1}{rgb}{0.0,0.0,0.0}
            \definecolor{col_lab_a2}{rgb}{0.0,0.0,0.0}
            %
            %
            \definecolor{col_a0-a1}{rgb}{0.0,0.0,0.0}
            \definecolor{col_a1-a2}{rgb}{0.0,0.0,0.0}
            %
            %
            \GraphInit[vstyle=Normal]
            %
            \SetVertexMath
            %
            \SetVertexNoLabel
            %
            \renewcommand*{\VertexLightFillColor}{col_a0}
            \Vertex[x=0.0cm,y=2.5cm]{a0}
            \renewcommand*{\VertexLightFillColor}{col_a1}
            \Vertex[x=2.5cm,y=2.5cm]{a1}
            \renewcommand*{\VertexLightFillColor}{col_a2}
            \Vertex[x=5.0cm,y=2.5cm]{a2}
            %
            %
            \AssignVertexLabel{a}{3}{
            \color{col_lab_a0}{$0$},
            \color{col_lab_a1}{$1$},
            \color{col_lab_a2}{$2$}
            }
            %
            %
            \renewcommand*{\EdgeColor}{col_a0-a1}
            \Edge(a0)(a1)
            \renewcommand*{\EdgeColor}{col_a1-a2}
            \Edge(a1)(a2)
            %
            %
            \end{tikzpicture}

        Scaling to a bounding box is problematic for graphs with
        just one vertex, or none. ::

            sage: from sage.graphs.graph_latex import check_tkz_graph
            sage: check_tkz_graph()  # random - depends on TeX installation
            sage: g = graphs.CompleteGraph(1)
            sage: opts = g.latex_options()
            sage: print opts.tkz_picture()
            \begin{tikzpicture}
            %
            \definecolor{col_a0}{rgb}{1.0,1.0,1.0}
            %
            %
            \definecolor{col_lab_a0}{rgb}{0.0,0.0,0.0}
            %
            %
            %
            %
            \GraphInit[vstyle=Normal]
            %
            \SetVertexMath
            %
            \SetVertexNoLabel
            %
            \renewcommand*{\VertexLightFillColor}{col_a0}
            \Vertex[x=2.5cm,y=2.5cm]{a0}
            %
            %
            \AssignVertexLabel{a}{1}{
            \color{col_lab_a0}{$0$}
            }
            %
            %
            %
            %
            \end{tikzpicture}
        """

        # We use cc=matplotlib.colors.ColorConverter() to convert from string to tuples
        # eg. cc.to_rgb('pink')
        import matplotlib
        from sage.misc.latex import latex
        import copy

        # On first use of this method, the next call may print warnings
        # as a side effect, but will be silent on any subsequent use.
        check_tkz_graph()

        # These defaults are hard-coded in the first version of this routine
        # They will migrate to the __init__ method once the infrastructure
        # here is stable
        #~~~~~~~~~~~
        layout = None
        bb=[ 5, 5 ]
        units='cm'
        prefix='a'
        vertex_math=True,
        vertex_color={}
        edge_color={}
        label_color={}
        labels=True
        #~~~~~~~~~~~

        if not units in ['in','mm','cm','pt', 'em', 'ex']:
            print 'Unknown units: %s.  Must be one of: in, mm, cm, pt, em, ex'% units
            return

        styles=['Shade', 'Art', 'Normal', 'Dijkstra', 'Welsh', 'Classic', 'Simple']
        style = self.get_option('tkz_style')
        if not style in styles:
            style = 'Normal'

        cc = matplotlib.colors.ColorConverter()
        color_dict={}

        # Default settings for the vertex and its labels
        default_vertex_color = cc.to_rgb( 'black' ) # default for Classic and Simple
        vertex_color_command = '\\renewcommand*{\\VertexDarkFillColor}'

        if labels:
            default_label_color = cc.to_rgb('black') # default label color for all styles
        # This means we will be using '\EdgeFillColor' in tkz-graph
        if style in styles[0:2]:#Shade or Art
            # This means we will be using '\VertexBallColor' in tkz-graph
            # to set the vertex color
            default_vertex_color = cc.to_rgb( 'orange' )
            vertex_color_command = '\\renewcommand*{\\VertexBallColor}'
        elif style in styles[2:5]:#Normal, Dijkstra or Welsh
            # This means we will be using '\VertexLightFillColor' in tkz-graph
            # to set the vertex color
            default_vertex_color = cc.to_rgb( 'white' )
            vertex_color_command = '\\renewcommand*{\\VertexLightFillColor}'


        # Defining vertex color and label dictionary so each vertex and its label
        # get a color. Argument 'vertex_color' and 'label_color' are dictionaries
        # specifying colors just for some of the vertices and labels, not necessarily all.
        v_color = {}
        if labels:
            l_color = {}
        for u in self._graph:
            c = default_vertex_color
            if vertex_color.has_key( u ):
                c = vertex_color[ u ]
                if type( c ) == str:
                    c = cc.to_rgb( c )
            v_color[ u ] = c
            if labels:
                lc = default_label_color
                if label_color.has_key( u ):
                    lc = label_color[ u ]
                    if type( lc ) == str:
                        lc = cc.to_rgb( lc )
                l_color[ u ] = lc

        # Default settings for the edges
        default_edge_color = cc.to_rgb( 'black' )
        edge_color_command = '\\renewcommand*{\\EdgeColor}'
        if style in styles[0:2]: # Shade, or Art
            # This means we will be using '\EdgeFillColor' in tkz-graph
            # to set the edge color
            default_edge_color = cc.to_rgb( 'orange' )
            edge_color_command = '\\renewcommand*{\\EdgeFillColor}'

        # Defining edge color dictionary so each edge
        # gets a color. Argument 'edge_color' could be a dictionary
        # specifying colors just for some edges.
        e_color = {}
        for f in self._graph.edges():
            f = f[0:2]
            c = default_edge_color
            if edge_color.has_key( f ):
                c = edge_color[ f ]
                if type( c ) == str:
                    c = cc.to_rgb( c )
            e_color[ f ] = c

        # A way of enumerating the vertices
        index_of_vertex={}
        i = 0;
        for u in self._graph:
            index_of_vertex[u]=i
            i = i+1

        pos = copy.deepcopy(self._graph.layout(layout = layout, labels = "latex"))

        # TODO: Could use self._graph._layout_bounding_box(pos)
        trans = lambda x,y: [x[0]-y[0],x[1]-y[1]]
        # Adjusting the image bounding box to have (0,0) as a corner
        # And identifying the spread in the x and y directions (i.e. xmax, ymax)
        # Needs care for perfectly horizontal and vertical layouts
        if len(pos.values()) > 0:
            xmin = min([ i[0] for i in pos.values()])
            ymin = min([ i[1] for i in pos.values()])
            for u in self._graph:
                pos[ u ] = trans( pos[ u ], [xmin,ymin])
            xmax = max([ i[0] for i in pos.values()])
            ymax = max([ i[1] for i in pos.values()])
        else:
            xmax, ymax = 0, 0
        # factors that will be used to scale the image to fit in the specified bounding box
        # horizontal and vertical layouts get put in the middle of the bounding box here
        # and get a scale factor of 1 so are unchanged later.
        if xmax == 0:
            for u in self._graph:
                pos[u][0] = 0.5*bb[0]
            x_factor = 1.0
        else:
            x_factor = float(bb[0])/xmax
        if ymax == 0:
            for u in self._graph:
                pos[u][1] = 0.5*bb[1]
            y_factor = 1.0
        else:
            y_factor = float(bb[1])/ymax

        # tkz string initialized
        s = ''
        s = s+'\\begin{tikzpicture}\n%\n'

        color_names = {}
        # add the definition of the colors for vertices
        for u in self._graph:
            color_names[ u ] = 'col_' + prefix + str(index_of_vertex[ u ])
            s = s+'\definecolor{'+color_names[ u ]+'}{rgb}'
            s = s+'{'+str(round( v_color[u][0],4))+','
            s = s+    str(round( v_color[u][1],4))+','
            s = s+    str(round( v_color[u][2],4))+'}\n'

        s = s+'%\n%\n'
        if labels:
            # add the definition of the colors for labels
            for u in self._graph:
                color_names[ color_names[u] ] = 'col_lab_' + prefix + str(index_of_vertex[ u ])
                s = s+'\definecolor{'+color_names[ color_names[ u ] ]+'}{rgb}'
                s = s+'{'+str(round( l_color[u][0],4))+','
                s = s+    str(round( l_color[u][1],4))+','
                s = s+    str(round( l_color[u][2],4))+'}\n'
            s = s+'%\n%\n'
        # add the definition of the colors for edges
        for f in self._graph.edges():
            f = f[0:2]
            color_names[ f ] = 'col_' + prefix + str(index_of_vertex[ f[0] ])+'-'+prefix + str(index_of_vertex[ f[1] ] )
            s = s+'\definecolor{'+color_names[ f ]+'}{rgb}'
            s = s+'{'+str(round( e_color[f][0],4))+','
            s = s+    str(round( e_color[f][1],4))+','
            s = s+    str(round( e_color[f][2],4))+'}\n'

        s = s+'%\n%\n'

        s = s+'\\GraphInit[vstyle='+style+']\n%\n'

        if vertex_math:
            s = s+'\\SetVertexMath\n%\n'

        s = s+'\\SetVertexNoLabel\n%\n'

        # Put vertices
        for u in self._graph:
            # First change the color of the vertex
            s = s + vertex_color_command + '{'+color_names[ u ]+'}\n'
            # Then add the vertex
            s = s+'\\Vertex'
            s = s+'[x='+str(round(x_factor*pos[u][0],4))+units
            s = s+',y='+str(round(y_factor*pos[u][1],4))+units+']'
            s = s+'{'+prefix+str(index_of_vertex[u])+'}\n'
        s = s+'%\n%\n'

        if labels:
            # Put labels for vertices
            s= s+'\\AssignVertexLabel{'+prefix+'}{'+str(self._graph.num_verts())+'}{\n'
            i=0
            for u in self._graph:
                s = s + '\color{' + color_names[ color_names[ u ] ] + '}{'
                if vertex_math:
                    s = s+'$'
                s = s+str(latex(u))
                if vertex_math:
                    s = s+'$'
                s = s+'},\n'

            s = s[:len(s)-2]
            s = s+'\n}\n'
            s = s+'%\n%\n'

        # Put edges
        for e in self._graph.edges():
            e = e[0:2]
            # First change the color
            s = s+ edge_color_command + '{'+color_names[ e ]+'}\n'
            # then put the edge
            s = s+'\\Edge'
            s = s+'('+prefix+str(index_of_vertex[e[0]])+')'
            s = s+'('+prefix+str(index_of_vertex[e[1]])+')'
            s = s+'\n'

        s = s+'%\n%\n'
        s = s+'\\end{tikzpicture}'
        return s
