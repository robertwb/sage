"""
Contour Plots
"""

#*****************************************************************************
#       Copyright (C) 2006 Alex Clemesha <clemesha@gmail.com>,
#                          William Stein <wstein@gmail.com>,
#                     2008 Mike Hansen <mhansen@gmail.com>,
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
from sage.plot.primitive import GraphicPrimitive
from sage.plot.misc import options, rename_keyword
from sage.plot.colors import rgbcolor, get_cmap
from sage.misc.misc import verbose, xsrange
import operator

class ContourPlot(GraphicPrimitive):
    """
    Primitive class for the contour plot graphics type.  See
    ``contour_plot?`` for help actually doing contour plots.

    INPUT:

    - ``xy_data_array`` - list of lists giving evaluated values of the function on the grid

    - ``xrange`` - tuple of 2 floats indicating range for horizontal direction

    - ``yrange`` - tuple of 2 floats indicating range for vertical direction

    - ``options`` - dict of valid plot options to pass to constructor

    EXAMPLES:

    Note this should normally be used indirectly via ``contour_plot``::

        sage: from sage.plot.contour_plot import ContourPlot
        sage: C = ContourPlot([[1,3],[2,4]],(1,2),(2,3),options={})
        sage: C
        ContourPlot defined by a 2 x 2 data grid
        sage: C.xrange
        (1, 2)

    TESTS:

    We test creating a contour plot::

        sage: x,y = var('x,y')
        sage: C = contour_plot(x^2-y^3+10*sin(x*y), (x, -4, 4), (y, -4, 4),plot_points=121,cmap='hsv')
    """
    def __init__(self, xy_data_array, xrange, yrange, options):
        """
        Initializes base class ContourPlot.

        EXAMPLES::

            sage: x,y = var('x,y')
            sage: C = contour_plot(x^2-y^3+10*sin(x*y), (x, -4, 4), (y, -4, 4),plot_points=121,cmap='hsv')
            sage: C[0].xrange
            (-4.0, 4.0)
            sage: C[0].options()['plot_points']
            121
        """
        self.xrange = xrange
        self.yrange = yrange
        self.xy_data_array = xy_data_array
        self.xy_array_row = len(xy_data_array)
        self.xy_array_col = len(xy_data_array[0])
        GraphicPrimitive.__init__(self, options)

    def get_minmax_data(self):
        """
        Returns a dictionary with the bounding box data.

        EXAMPLES::

            sage: x,y = var('x,y')
            sage: f(x,y) = x^2 + y^2
            sage: d = contour_plot(f, (3, 6), (3, 6))[0].get_minmax_data()
            sage: d['xmin']
            3.0
            sage: d['ymin']
            3.0
        """
        from sage.plot.plot import minmax_data
        return minmax_data(self.xrange, self.yrange, dict=True)

    def _allowed_options(self):
        """
        Return the allowed options for the ContourPlot class.

        EXAMPLES::

            sage: x,y = var('x,y')
            sage: C = contour_plot(x^2-y^2,(x,-2,2),(y,-2,2))
            sage: isinstance(C[0]._allowed_options(),dict)
            True
        """
        return {'plot_points':'How many points to use for plotting precision',
                'cmap':"""the name of a predefined colormap,
                        a list of colors, or an instance of a
                        matplotlib Colormap. Type: import matplotlib.cm; matplotlib.cm.datad.keys()
                        for available colormap names.""",
                       'fill':'Fill contours or not',
                'contours':"""Either an integer specifying the number of
                       contour levels, or a sequence of numbers giving
                       the actual contours to use.""",
                'zorder':'The layer level in which to draw'}

    def _repr_(self):
        """
        String representation of ContourPlot primitive.

        EXAMPLES::

            sage: x,y = var('x,y')
            sage: C = contour_plot(x^2-y^2,(x,-2,2),(y,-2,2))
            sage: c = C[0]; c
            ContourPlot defined by a 100 x 100 data grid
        """
        return "ContourPlot defined by a %s x %s data grid"%(self.xy_array_row, self.xy_array_col)

    def _render_on_subplot(self, subplot):
        """
        TESTS:

        A somewhat random plot, but fun to look at::

            sage: x,y = var('x,y')
            sage: contour_plot(x^2-y^3+10*sin(x*y), (x, -4, 4), (y, -4, 4),plot_points=121,cmap='hsv')
        """
        from sage.rings.integer import Integer
        options = self.options()
        fill = options['fill']
        contours = options['contours']
        if options.has_key('cmap'):
            cmap = get_cmap(options['cmap'])
        elif fill or contours is None:
            cmap = get_cmap('gray')
        else:
            if isinstance(contours, (int, Integer)):
                cmap = get_cmap([(i,i,i) for i in xsrange(0,1,1/contours)])
            else:
                l = Integer(len(contours))
                cmap = get_cmap([(i,i,i) for i in xsrange(0,1,1/l)])

        x0,x1 = float(self.xrange[0]), float(self.xrange[1])
        y0,y1 = float(self.yrange[0]), float(self.yrange[1])
        if fill:
            if contours is None:
                subplot.contourf(self.xy_data_array, cmap=cmap, extent=(x0,x1,y0,y1))
            elif isinstance(contours, (int, Integer)):
                subplot.contourf(self.xy_data_array, int(contours), cmap=cmap, extent=(x0,x1,y0,y1))
            else:
                subplot.contourf(self.xy_data_array, contours, cmap=cmap, extent=(x0,x1,y0,y1))
        else:
            if contours is None:
                subplot.contour(self.xy_data_array, cmap=cmap, extent=(x0,x1,y0,y1))
            elif isinstance(contours, (int, Integer)):
                subplot.contour(self.xy_data_array, int(contours), cmap=cmap, extent=(x0,x1,y0,y1))
            else:
                subplot.contour(self.xy_data_array, contours, cmap=cmap, extent=(x0,x1,y0,y1))

@options(plot_points=100, fill=True, contours=None,frame=True)
def contour_plot(f, xrange, yrange, **options):
    r"""
    ``contour_plot`` takes a function of two variables, `f(x,y)`
    and plots contour lines of the function over the specified
    ``xrange`` and ``yrange`` as demonstrated below.

    ``contour_plot(f, (xmin, xmax), (ymin, ymax), ...)``

    INPUT:

    - ``f`` -- a function of two variables

    - ``(xmin, xmax)`` -- 2-tuple, the range of ``x`` values OR 3-tuple
      ``(x,xmin,xmax)``

    - ``(ymin, ymax)`` -- 2-tuple, the range of ``y`` values OR 3-tuple
      ``(y,ymin,ymax)``

    The following inputs must all be passed in as named parameters:

    - ``plot_points``  -- integer (default: 100); number of points to plot
      in each direction of the grid.  For old computers, 25 is fine, but
      should not be used to verify specific intersection points.

    - ``fill`` -- bool (default: ``True``), whether to color in the area
      between contour lines

    - ``cmap`` -- a colormap (default: ``'gray'``), the name of
      a predefined colormap, a list of colors or an instance of a matplotlib
      Colormap. Type: ``import matplotlib.cm; matplotlib.cm.datad.keys()``
      for available colormap names.

    - ``contours`` -- integer or list of numbers (default: ``None``):
      If a list of numbers is given, then this specifies the contour levels
      to use.  If an integer is given, then this many contour lines are
      used, but the exact levels are determined automatically. If ``None``
      is passed (or the option is not given), then the number of contour
      lines is determined automatically, and is usually about 5.


    EXAMPLES:

    Here we plot a simple function of two variables.  Note that
    since the input function is an expression, we need to explicitly
    declare the variables in 3-tuples for the range::

        sage: x,y = var('x,y')
        sage: contour_plot(cos(x^2+y^2), (x, -4, 4), (y, -4, 4))

    Here we change the ranges and add some options::

        sage: x,y = var('x,y')
        sage: contour_plot((x^2)*cos(x*y), (x, -10, 5), (y, -5, 5), fill=False, plot_points=150)

    An even more complicated plot::

        sage: x,y = var('x,y')
        sage: contour_plot(sin(x^2 + y^2)*cos(x)*sin(y), (x, -4, 4), (y, -4, 4),plot_points=150)

    Some elliptic curves, but with symbolic endpoints.  In the first
    example, the plot is rotated 90 degrees because we switch the
    variables x,y::

        sage: x,y = var('x,y')
        sage: contour_plot(y^2 + 1 - x^3 - x, (y,-pi,pi), (x,-pi,pi))
        sage: contour_plot(y^2 + 1 - x^3 - x, (x,-pi,pi), (y,-pi,pi))

    We can play with the contour levels::

        sage: x,y = var('x,y')
        sage: f(x,y) = x^2 + y^2
        sage: contour_plot(f, (-2, 2), (-2, 2))
        sage: contour_plot(f, (-2, 2), (-2, 2), contours=2, cmap=[(1,0,0), (0,1,0), (0,0,1)])
        sage: contour_plot(f, (-2, 2), (-2, 2), contours=(0.1, 1.0, 1.2, 1.4), cmap='hsv')
        sage: contour_plot(f, (-2, 2), (-2, 2), contours=(1.0,), fill=False)

    This should plot concentric circles centered at the origin::

        sage: x,y = var('x,y')
        sage: contour_plot(x^2+y^2-2,(x,-1,1), (y,-1,1)).show(aspect_ratio=1)

    Extra options will get passed on to show(), as long as they are valid::

        sage: f(x, y) = cos(x) + sin(y)
        sage: contour_plot(f, (0, pi), (0, pi), axes=False)
        sage: contour_plot(f, (0, pi), (0, pi)).show(axes=False) # These are equivalent

    TESTS:

    To check that ticket 5221 is fixed, note that this has three curves, not two::

        sage: x,y = var('x,y')
        sage: contour_plot(x-y^2,(x,-5,5),(y,-3,3),contours=[-4,-2,0], fill=False)
    """
    from sage.plot.plot import Graphics, setup_for_eval_on_grid
    g, xstep, ystep, xrange, yrange = setup_for_eval_on_grid([f], xrange, yrange, options['plot_points'])
    g = g[0]
    xy_data_array = [[g(x, y) for x in xsrange(xrange[0], xrange[1], xstep, include_endpoint=True)]
                              for y in xsrange(yrange[0], yrange[1], ystep, include_endpoint=True)]

    g = Graphics()
    g._set_extra_kwds(Graphics._extract_kwds_for_show(options, ignore=['xmin', 'xmax']))
    g.add_primitive(ContourPlot(xy_data_array, xrange, yrange, options))
    return g

@options(plot_points=150, contours=(0,0), fill=False)
def implicit_plot(f, xrange, yrange, **options):
    r"""
    ``implicit_plot`` takes a function of two variables, `f(x,y)`
    and plots the curve `f(x,y) = 0` over the specified
    ``xrange`` and ``yrange`` as demonstrated below.

    ``implicit_plot(f, (xmin, xmax), (ymin, ymax), ...)``

    ``implicit_plot(f, (x, xmin, xmax), (y, ymin, ymax), ...)``

    INPUT:

    - ``f`` -- a function of two variables or equation in two variables

    - ``(xmin, xmax)`` -- 2-tuple, the range of ``x`` values or ``(x,xmin,xmax)``

    - ``(ymin, ymax)`` -- 2-tuple, the range of ``y`` values or ``(y,ymin,ymax)``

    The following inputs must all be passed in as named parameters:

    - ``plot_points`` -- integer (default: 150); number of points to plot
      in each direction of the grid

    - ``fill`` -- boolean (default: ``False``); if ``True``, fill the region
      `f(x,y) < 0`.


    EXAMPLES:

    A simple circle with a radius of 2. Note that
    since the input function is an expression, we need to explicitly
    declare the variables in 3-tuples for the range::

        sage: var("x y")
        (x, y)
        sage: implicit_plot(x^2+y^2-2, (x,-3,3), (y,-3,3)).show(aspect_ratio=1)

    I can do the same thing, but using a callable function so I don't need
    to explicitly define the variables in the ranges, and filling the inside::

        sage: x,y = var('x,y')
        sage: f(x,y) = x^2 + y^2 - 2
        sage: implicit_plot(f, (-3, 3), (-3, 3),fill=True).show(aspect_ratio=1)

    You can also plot an equation::

        sage: var("x y")
        (x, y)
        sage: implicit_plot(x^2+y^2 == 2, (x,-3,3), (y,-3,3)).show(aspect_ratio=1)

    We can define a level-`n` approximation of the boundary of the
    Mandelbrot set::

        sage: def mandel(n):
        ...       c = polygen(CDF, 'c')
        ...       z = 0
        ...       for i in range(n):
        ...           z = z*z + c
        ...       def f(x, y):
        ...           val = z(CDF(x, y))
        ...           return val.norm() - 4
        ...       return f

    The first-level approximation is just a circle::

        sage: implicit_plot(mandel(1), (-3, 3), (-3, 3)).show(aspect_ratio=1)

    A third-level approximation starts to get interesting::

        sage: implicit_plot(mandel(3), (-2, 1), (-1.5, 1.5)).show(aspect_ratio=1)

    The seventh-level approximation is a degree 64 polynomial, and
    ``implicit_plot`` does a pretty good job on this part of the curve.
    (``plot_points=200`` looks even better, but it takes over a second.)

    ::

        sage: implicit_plot(mandel(7), (-0.3, 0.05), (-1.15, -0.9),plot_points=50).show(aspect_ratio=1)
    """
    from sage.symbolic.expression import is_SymbolicEquation
    if is_SymbolicEquation(f):
        if f.operator() != operator.eq:
            raise ValueError, "input to implicit plot must be function or equation"
        f = f.lhs() - f.rhs()
    return contour_plot(f, xrange, yrange, **options)

@options(plot_points=100, incol='blue', outcol='white', bordercol=None)
def region_plot(f, xrange, yrange, plot_points, incol, outcol, bordercol):
    r"""
    ``region_plot`` takes a boolean function of two variables, `f(x,y)`
    and plots the region where f is True over the specified
    ``xrange`` and ``yrange`` as demonstrated below.

    ``region_plot(f, (xmin, xmax), (ymin, ymax), ...)``

    INPUT:

    - ``f`` -- a boolean function of two variables

    - ``(xmin, xmax)`` -- 2-tuple, the range of ``x`` values OR 3-tuple
      ``(x,xmin,xmax)``

    - ``(ymin, ymax)`` -- 2-tuple, the range of ``y`` values OR 3-tuple
      ``(y,ymin,ymax)``

    - ``plot_points``  -- integer (default: 100); number of points to plot
      in each direction of the grid

    - ``incol`` -- a color (default: ``'blue'``), the color inside the region

    - ``outcol`` -- a color (default: ``'white'``), the color of the outside
      of the region

    - ``bordercol`` -- a color (default: ``None``), the color of the border
      (``incol`` if not specified)

    EXAMPLES:

    Here we plot a simple function of two variables::

        sage: x,y = var('x,y')
        sage: region_plot(cos(x^2+y^2) <= 0, (x, -3, 3), (y, -3, 3))

    Here we play with the colors::

        sage: region_plot(x^2+y^3 < 2, (x, -2, 2), (y, -2, 2), incol='lightblue', bordercol='gray')

    An even more complicated plot::

        sage: region_plot(sin(x)*sin(y) >= 1/4, (x,-10,10), (y,-10,10), incol='yellow', bordercol='black', plot_points=250)

    A disk centered at the origin::

        sage: region_plot(x^2+y^2<1, (x,-1,1), (y,-1,1)).show(aspect_ratio=1)

    A plot with more than one condition::

        sage: region_plot([x^2+y^2<1, x<y], (x,-2,2), (y,-2,2))

    Since it doesn't look very good, let's increase plot_points::

        sage: region_plot([x^2+y^2<1, x<y], (x,-2,2), (y,-2,2), plot_points=400).show(aspect_ratio=1) #long time

    The first quadrant of the unit circle::

        sage: region_plot([y>0, x>0, x^2+y^2<1], (-1.1, 1.1), (-1.1, 1.1), plot_points = 400).show(aspect_ratio=1)

    Here is another plot::

        sage: region_plot(x*(x-1)*(x+1)+y^2<0, (x, -3, 2), (y, -3, 3), incol='lightblue', bordercol='gray', plot_points=50)

    If we want to keep only the region where x is positive::

        sage: region_plot([x*(x-1)*(x+1)+y^2<0, x>-1], (x, -3, 2), (y, -3, 3), incol='lightblue', bordercol='gray', plot_points=50)

    Here we have a cut circle::

        sage: region_plot([x^2+y^2<4, x>-1], (x, -2, 2), (y, -2, 2), incol='lightblue', bordercol='gray', plot_points=200).show(aspect_ratio=1) #long time
    """

    from sage.plot.plot import Graphics, setup_for_eval_on_grid
    if not isinstance(f, (list, tuple)):
        f = [f]

    variables = reduce(lambda g1, g2: g1.union(g2), [set(g.variables()) for g in f], set([]))

    f = [equify(g, variables) for g in f]

    g, xstep, ystep, xrange, yrange = setup_for_eval_on_grid(f, xrange, yrange, plot_points)

    xy_data_arrays = map(lambda g: [[g(x, y) for x in xsrange(xrange[0], xrange[1], xstep, include_endpoint=True)]
                                             for y in xsrange(yrange[0], yrange[1], ystep, include_endpoint=True)], g)

    xy_data_array = map(lambda *rows: map(lambda *vals: mangle_neg(vals), *rows), *xy_data_arrays)

    from matplotlib.colors import ListedColormap
    incol = rgbcolor(incol)
    outcol = rgbcolor(outcol)
    cmap = ListedColormap([incol, outcol])
    cmap.set_over(outcol)
    cmap.set_under(incol)

    g = Graphics()

    g.add_primitive(ContourPlot(xy_data_array, xrange, yrange, dict(plot_points=plot_points,
                                                                    contours=[-1e307, 0, 1e307], cmap=cmap, fill=True)))

    if bordercol is not None:
        bordercol = rgbcolor(bordercol)
        g.add_primitive(ContourPlot(xy_data_array, xrange, yrange, dict(plot_points=plot_points,
                                                                       contours=[0], cmap=[bordercol], fill=False)))

    return g

def equify(f, variables = None):
    """
    Returns the equation rewritten as a symbolic function to give
    negative values when True, positive when False.

    EXAMPLES::

        sage: from sage.plot.contour_plot import equify
        sage: var('x, y')
        (x, y)
        sage: equify(x^2 < 2)
        x |--> x^2 - 2
        sage: equify(x^2 > 2)
        x |--> -x^2 + 2
        sage: equify(x*y > 1)
        (x, y) |--> -x*y + 1
        sage: equify(y > 0, (x,y))
        (x, y) |--> -y
    """
    import operator
    from sage.calculus.all import symbolic_expression
    op = f.operator()
    if variables == None:
        variables = f.variables()

    if op is operator.gt or op is operator.ge:
        s = symbolic_expression(f.rhs() - f.lhs()).function(*variables)
        return s
    else:
        s = symbolic_expression(f.lhs() - f.rhs()).function(*variables)
        return s

def mangle_neg(vals):
    """
    Returns the product of all values in vals, with the result
    nonnegative if any of the values is nonnegative.

    EXAMPLES::

        sage: from sage.plot.contour_plot import mangle_neg
        sage: mangle_neg([-1.2, -0.74, -2.56, -1.01])
        -2.29601280000000
        sage: mangle_neg([-1.2, 0.0, -2.56])
        0.000000000000000
        sage: mangle_neg([-1.2, -0.74, -2.56, 1.01])
        2.29601280000000
    """
    from sage.misc.misc_c import prod
    res = abs(prod(vals))
    if any(map(lambda v: v>=0, vals)):
        return res
    else:
        return -res
