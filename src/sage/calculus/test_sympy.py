r"""
A Sample Session using SymPy

In this first part, we do all of the examples in the SymPy tutorial
(http://code.google.com/p/sympy/wiki/Tutorial), but using Sage
instead of SymPy.

::

    sage: a = Rational((1,2))
    sage: a
    1/2
    sage: a*2
    1
    sage: Rational(2)^50 / Rational(10)^50
    1/88817841970012523233890533447265625
    sage: 1.0/2
    0.500000000000000
    sage: 1/2
    1/2
    sage: pi^2
    pi^2
    sage: float(pi)
    3.1415926535897931
    sage: RealField(200)(pi)
    3.1415926535897932384626433832795028841971693993751058209749
    sage: float(pi + exp(1))
    5.85987448204883...
    sage: oo != 2
    True

::

    sage: var('x y')
    (x, y)
    sage: x + y + x - y
    2*x
    sage: (x+y)^2
    (x + y)^2
    sage: ((x+y)^2).expand()
    x^2 + 2*x*y + y^2
    sage: ((x+y)^2).subs(x=1)
    (y + 1)^2
    sage: ((x+y)^2).subs(x=y)
    4*y^2

::

    sage: limit(sin(x)/x, x=0)
    1
    sage: limit(x, x=oo)
    +Infinity
    sage: limit((5^x + 3^x)^(1/x), x=oo)
    5

::

    sage: diff(sin(x), x)
    cos(x)
    sage: diff(sin(2*x), x)
    2*cos(2*x)
    sage: diff(tan(x), x)
    tan(x)^2 + 1
    sage: limit((tan(x+y) - tan(x))/y, y=0)
    cos(x)^(-2)
    sage: diff(sin(2*x), x, 1)
    2*cos(2*x)
    sage: diff(sin(2*x), x, 2)
    -4*sin(2*x)
    sage: diff(sin(2*x), x, 3)
    -8*cos(2*x)

::

    sage: cos(x).taylor(x,0,10)
    -1/3628800*x^10 + 1/40320*x^8 - 1/720*x^6 + 1/24*x^4 - 1/2*x^2 + 1
    sage: (1/cos(x)).taylor(x,0,10)
    50521/3628800*x^10 + 277/8064*x^8 + 61/720*x^6 + 5/24*x^4 + 1/2*x^2 + 1

::

    sage: matrix([[1,0], [0,1]])
    [1 0]
    [0 1]
    sage: var('x y')
    (x, y)
    sage: A = matrix([[1,x], [y,1]])
    sage: A
    [1 x]
    [y 1]
    sage: A^2
    [x*y + 1     2*x]
    [    2*y x*y + 1]
    sage: R.<x,y> = QQ[]
    sage: A = matrix([[1,x], [y,1]])
    sage: print A^10
    [x^5*y^5 + 45*x^4*y^4 + 210*x^3*y^3 + 210*x^2*y^2 + 45*x*y + 1     10*x^5*y^4 + 120*x^4*y^3 + 252*x^3*y^2 + 120*x^2*y + 10*x]
    [    10*x^4*y^5 + 120*x^3*y^4 + 252*x^2*y^3 + 120*x*y^2 + 10*y x^5*y^5 + 45*x^4*y^4 + 210*x^3*y^3 + 210*x^2*y^2 + 45*x*y + 1]
    sage: var('x y')
    (x, y)

And here are some actual tests of sympy::

    sage: from sympy import Symbol, cos, sympify, pprint
    sage: from sympy.abc import x

::

    sage: e = sympify(1)/cos(x)**3; e
    cos(x)**(-3)
    sage: f = e.series(x, 0, 10); f
    1 + 3*x**2/2 + 11*x**4/8 + 241*x**6/240 + 8651*x**8/13440 + O(x**10)

And the pretty-printer::

    sage: pprint(e)
           1
        -------
           3
        cos (x)
    sage: pprint(f)
               2       4        6         8
            3*x    11*x    241*x    8651*x
        1 + ---- + ----- + ------ + ------- + O(x**10)
             2       8      240      13440

And the functionality to convert from sympy format to Sage format::

    sage: e._sage_()
    cos(x)^(-3)
    sage: e._sage_().taylor(x._sage_(), 0, 8)
    8651/13440*x^8 + 241/240*x^6 + 11/8*x^4 + 3/2*x^2 + 1
    sage: f._sage_()
    8651/13440*x^8 + 241/240*x^6 + 11/8*x^4 + 3/2*x^2 + 1

Mixing SymPy with Sage::

    sage: import sympy
    sage: sympy.sympify(var("y"))+sympy.Symbol("x")
    x + y
    sage: o = var("omega")
    sage: s = sympy.Symbol("x")
    sage: t1 = s + o
    sage: t2 = o + s
    sage: type(t1)
    <class 'sympy.core.add.Add'>
    sage: type(t2)
    <type 'sage.symbolic.expression.Expression'>
    sage: t1, t2
    (omega + x, omega + x)
    sage: e=sympy.sin(var("y"))+sage.all.cos(sympy.Symbol("x"))
    sage: type(e)
    <class 'sympy.core.add.Add'>
    sage: e
    cos(x) + sin(y)
    sage: e=e._sage_()
    sage: type(e)
    <type 'sage.symbolic.expression.Expression'>
    sage: e
    sin(y) + cos(x)
    sage: e = sage.all.cos(var("y")**3)**4+var("x")**2
    sage: e = e._sympy_()
    sage: e
    x**2 + cos(y**3)**4

::

    sage: a = sympy.Matrix([1, 2, 3])
    sage: a[1]
    2

::

    sage: sympify(1.5)
    1.50000000000000
    sage: sympify(2)
    2
    sage: sympify(-2)
    -2
"""
