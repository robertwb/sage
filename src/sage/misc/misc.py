"""
Miscellaneous functions

AUTHOR:
    -- William Stein
    -- William Stein (2006-04-26): added workaround for Windows where
            most users's home directory has a space in it.
"""

########################################################################
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
########################################################################

__doc_exclude=["cached_attribute", "cached_class_attribute", "lazy_prop",
               "generic_cmp", "is_64bit", "to_gmp_hex", "todo",
               "typecheck", "prop", "strunc",
               "assert_attribute", "LOGFILE"]

import operator, os, socket, sys, signal, time, weakref, random, resource

from banner import version, banner

SAGE_ROOT = os.environ["SAGE_ROOT"]
SAGE_LOCAL = SAGE_ROOT + '/local/'

HOSTNAME = socket.gethostname().replace('-','_')

LOCAL_IDENTIFIER = '%s.%s'%(HOSTNAME , os.getpid())

if not os.path.exists(SAGE_ROOT):
    os.makedirs(SAGE_ROOT)

try:
    SAGE_URL = os.environ["SAGE_URL"]
except KeyError:
    SAGE_URL = "http://sage.math.washington.edu/sage/"     # default server

LOGFILE = "%s/log/sage_log"%SAGE_ROOT


try:
    DOT_SAGE = os.environ['DOT_SAGE']
except KeyError:
    try:
        DOT_SAGE = '%s/.sage/'%os.environ['HOME']
    except KeyError:
        DOT_SAGE = '%s/.sage/'%SAGE_ROOT

UNAME=os.uname()[0]
if ' ' in DOT_SAGE:
    if UNAME[:6] == 'CYGWIN':
        # on windows/cygwin it is typical for the home directory
        # to have a space in it.  Fortunately, users also have
        # write privilegs to c:\cygwin\home, so we just put
        # .sage there.
        DOT_SAGE="/home/.sage"
    else:
        print "Your home directory has a space in it.  This"
        print "will probably break some functionality of SAGE.  E.g.,"
        print "the GAP interface will not work.  A workaround"
        print "is to set the environment variable HOME to a"
        print "directory with no spaces that you have write"
        print "permissions to before you start sage."

SAGE_TMP='%s/temp/%s/%s/'%(DOT_SAGE, HOSTNAME, os.getpid())
if not os.path.exists(SAGE_TMP):
    try:
        os.makedirs(SAGE_TMP)
    except OSError, msg:
        print msg
        raise OSError, " ** Error trying to create the SAGE tmp directory in your home directory.  A possible cause of this might be that you built or upgraded SAGE after typing 'su'.  You probably need to delete the directory $HOME/.sage."

SAGE_DATA = '%s/data/'%SAGE_ROOT
SAGE_EXTCODE = '%s/data/extcode/'%SAGE_ROOT
SPYX_TMP = '%s/spyx/'%SAGE_TMP


def delete_tmpfiles():
    # !!!If you change this, see also SAGE_ROOT/local/bin/sage-doctest!!!
    import shutil
    try:
        if os.path.exists(SAGE_TMP):
            shutil.rmtree(SAGE_TMP)
    except OSError, msg:
        print msg
        pass

SAGE_TMP_INTERFACE='%s/interface/'%SAGE_TMP
if not os.path.exists(SAGE_TMP_INTERFACE):
    os.makedirs(SAGE_TMP_INTERFACE)

SAGE_DB = '%s/db'%DOT_SAGE
if not os.path.exists(SAGE_DB):
    os.makedirs(SAGE_DB)


#################################################################
# Functions to help with interfacing with CXX code that
# uses the GMP library
#################################################################
def to_gmp_hex(n):
    return hex(n).replace("L","").replace("0x","")

#################################################################
# timing
#################################################################

def cputime(t=0):
    """
    Return the time in CPU second since SAGE started, or with optional
    argument t, return the time since time t.  This is how much
    time SAGE has spent using the CPU.  It does not count time
    spent by subprocesses spawned by SAGE (e.g., Gap, Singular, etc.).

    This is done via a call to resource.getrusage, so it avoids the
    wraparound problems in time.clock() on Cygwin.

    INPUT:
        t -- (optional) float, time in CPU seconds
    OUTPUT:
        float -- time in CPU seconds

    EXAMPLES:
        sage: t = cputime()
        sage: F = factor(2^199-1)
        sage: cputime(t)          # somewhat random
        0.29000000000000004

        sage: w = walltime()
        sage: F = factor(2^199-1)
        sage: walltime(w)         # somewhat random
        0.8823847770690918
    """
    try:
        t = float(t)
    except TypeError:
        t = 0.0
    u,s = resource.getrusage(resource.RUSAGE_SELF)[:2]
    return u+s - t

def walltime(t=0):
    """
    Return the wall time in second, or with optional argument t,
    return the wall time since time t.  "Wall time" means the time
    on a wall clock, i.e., the actual time.

    INPUT:
        t -- (optional) float, time in CPU seconds
    OUTPUT:
        float -- time in seconds

    EXAMPLES:
        sage: w = walltime()
        sage: F = factor(2^199-1)
        sage: walltime(w)   # somewhat random
        0.8823847770690918
    """
    return time.time() - t

#def clock(cmd):
#    t=cputime()
#    eval(compile(cmd,"clock",'single'))
#    return cputime(t)

#################################################################
# simple verbosity system
#################################################################
LEVEL=0  # default

verbose_files = []

def verbose(mesg="", t=0, level=1, caller_name=None):
    """
    Print a message if the current verbosity is at least level.

    INPUT:
        mesg -- str, a message to print
        t -- int, optional, if included, will also print cputime(t),
-            which is the time since time t.  Thus t should have been
             obtained with t=cputime()
        level -- int, (default: 1) the verbosity level of what we are printing
        caller_name -- string (default: None), the name of the calling function;
                       in most cases Python can deduce this, so it need not
                       be provided.
    OUTPUT:
        possibly prints a message to stdout;
        also returns cputime()

    EXAMPLE:
        sage.: set_verbose(1)
        sage.: t = cputime()
        sage.: t = verbose("This is SAGE.", t, level=1, caller_name="william")
        VERBOSE1 (william): This is SAGE. (time = 0.0)
    """
    if level>LEVEL:
        return cputime()

    frame = sys._getframe(1).f_code
    file_name = frame.co_filename
    lineno = frame.co_firstlineno
    if 'all' in verbose_files or level<=0:
        show = True
    else:
        show = False
        for X in verbose_files:
            if file_name.find(X) != -1:
                show = True
                break

    if not show:
        return cputime()

    if t != 0 and mesg=="":
        mesg = "Finished."

    # see recipe 14.7 in Python Cookbook
    if caller_name == None:
        caller_name = frame.co_name
        if caller_name == "?: ":
            caller_name = ""
    short_file_name = os.path.split(frame.co_filename)[1]
    if '<' in short_file_name and '>' in short_file_name:
        s = "verbose %s (%s) %s"%(level, caller_name, mesg)
    else:
        s = "verbose %s (%s: %s, %s) %s"%(level, lineno, short_file_name, caller_name, mesg)
    if t!=0:
        s = s + " (time = %s)"%cputime(t)
    print s
    #open(LOGFILE,"a").write(s+"\n")
    return cputime()

def todo(mesg=""):
    caller_name = sys._getframe(1).f_code.co_name
    raise NotImplementedError, "%s: todo -- %s"%(caller_name, mesg)

def set_verbose(level, files='all'):
    """
    Set the global SAGE verbosity level.

    INPUT:
        int level: an integer between 0 and 2, inclusive.
        files (default: 'all'): list of files to make verbose,
               or 'all' to make ALL files verbose (the default).
    OUTPUT:
        changes the state of the verbosity flag and
        possibly appends to the list of files that are verbose.

    EXAMPLES:
        sage.: set_verbose(2)
        sage.: _ = verbose("This is SAGE.", level=1)
        VERBOSE1 (?): This is SAGE.
        sage.: _ = verbose("This is SAGE.", level=2)
        VERBOSE2 (?): This is SAGE.
        sage.: _ = verbose("This is SAGE.", level=3)
        [no output]
    """
    if isinstance(level, str):
        set_verbose_files([level])
    global LEVEL
    LEVEL = level
    if isinstance(files, str):
        files = [files]
    set_verbose_files(files)

def set_verbose_files(file_name):
    """
    """
    if not isinstance(file_name, list):
        file_name = [file_name]
    global verbose_files
    verbose_files = file_name

def get_verbose_files():
    """
    """
    return verbose_files

def unset_verbose_files(file_name):
    """
    """
    if not isinstance(file_name, list):
        file_name = [file_name]
    for X in file_name:
        verbose_files.remove(X)


def get_verbose():
    """
    Return the global SAGE verbosity level.

    INPUT:
        int level: an integer between 0 and 2, inclusive.

    OUTPUT:
        changes the state of the verbosity flag.

    EXAMPLES:
        sage: get_verbose()
        0
        sage: set_verbose(2)
        sage: get_verbose()
        2
        sage: set_verbose(0)
    """
    global LEVEL
    return LEVEL



def generic_cmp(x,y):
    """
    Compare x and y and return -1, 0, or 1.

    This is similar to x.__cmp__(y), but works even in some cases
    when a .__cmp__ method isn't defined.
    """
    if x<y:
        return -1
    elif x==y:
        return 0
    return 1

def cmp_props(left, right, props):
    for a in props:
        c = cmp(left.__getattribute__(a)(), right.__getattribute__(a)())
        if c: return c
    return 0

def prod(x, z=None):
    """
    Return the product of the elements in the list x.  If optimal
    argument z is not given, start the product with the first element
    of the list, otherwise use z.  The empty product is the int 1 if z
    is not specified, and is z if given.

    EXAMPLES:
        sage: prod([1,2,34])
        68
        sage: prod([2,3], 5)
        30
        sage: F = factor(-2006); F
        -1 * 2 * 17 * 59
        sage: prod(F)
        -2006
    """
    try:
        return x.prod()
    except AttributeError:
        try:
            return x.mul()
        except AttributeError:
            pass

    if not isinstance(x, list):
        x = list(x)
    if z is None:
        if len(x) == 0:
            import sage.rings.integer
            return sage.rings.integer.Integer(1)
        z = x[0]
        i = 1
    else:
        i = 0

    # TODO: Change this to use a balanced tree in some cases, e.g.,
    # if input is a list?
    for m in x[i:]:
        z *= m
    return z

# alternative name for prod
mul = prod

add = sum

## def add(x, z=0):
##     """
##     Return the sum of the elements of x.  If x is empty,
##     return z.

##     INPUT:
##         x -- iterable
##         z -- the "0" that will be returned if x is empty.

##     OUTPUT:
##         object

##     EXAMPLES:

##     A very straightforward usage:
##         sage: add([1,2,3])
##         6

##     In the following example, xrange is an iterator:
##         sage: add(xrange(101))
##         5050

##     Append two sequences.
##         sage: add([[1,1], [-1,0]])
##         [1, 1, -1, 0]

##     The zero can be anything:
##         sage: add([], "zero")
##         'zero'
##     """
##     if len(x) == 0:
##         return z
##     if not isinstance(x, list):
##         m = x.__iter__()
##         y = m.next()
##         return reduce(operator.add, m, y)
##     else:
##         return reduce(operator.add, x[1:], x[0])


def union(x, y=None):
    """
    Return the union of x and y, as a list.  The resulting list need
    not be sorted and can change from call to call.

    INPUT:
        x -- iterable
        y -- iterable (may optionally omitted)
    OUTPUT:
        list

    EXAMPLES:
        sage.: union([1,2,3,4], [5,6])
        [1, 3, 2, 5, 4, 6]
        sage.: union([1,2,3,4,5,6], [5,6])
        [1, 3, 2, 5, 4, 6]
        sage.: union((1,2,3,4,5,6), [5,6])
        [1, 3, 2, 5, 4, 6]
        sage.: union((1,2,3,4,5,6), set([5,6]))
        [1, 3, 2, 5, 4, 6]
    """
    if y == None:
        return list(set(x))
    return list(set(x).union(y))

def uniq(x):
    """
    Return the sublist of all elements in the list x that is sorted
    and is such that the entries in the sublist are unique.

    EXAMPLES:
        sage: v = uniq([1,1,8,-5,3,-5,'a','x','a'])
        sage: v            # potentially random ordering of output
        ['a', 'x', -5, 1, 3, 8]
        sage: set(v) == set(['a', 'x', -5, 1, 3, 8])
        True
    """
    v = list(set(x))
    v.sort()
    return v


def coeff_repr(c, is_latex=False):
    if not is_latex:
        try:
            return c._coeff_repr()
        except AttributeError:
            pass
    if isinstance(c, (int, long, float)):
        return str(c)
    if is_latex and hasattr(c, '_latex_'):
        s = c._latex_()
    else:
        s = str(c).replace(' ','')
    if s.find("+") != -1 or s.find("-") != -1:
        if is_latex:
            return "\\left(%s\\right)"%s
        else:
            return "(%s)"%s
    return s

def repr_lincomb(symbols, coeffs, is_latex=False):
    """
    Compute a string representation of a linear combination of some
    formal symbols.

    INPUT:
        symbols -- list of symbols
        coeffs -- list of coefficients of the symbols

    OUTPUT:
        str -- a string

    EXAMPLES:
        sage: repr_lincomb(['a','b','c'], [1,2,3])
        'a + 2*b + 3*c'
        sage: repr_lincomb(['a','b','c'], [1,'2+3*x',3])
        'a + (2+3*x)*b + 3*c'
        sage: repr_lincomb(['a','b','c'], ['1+x^2','2+3*x',3])
        '(1+x^2)*a + (2+3*x)*b + 3*c'
        sage: repr_lincomb(['a','b','c'], ['1+x^2','-2+3*x',3])
        '(1+x^2)*a + (-2+3*x)*b + 3*c'
        sage: repr_lincomb(['a','b','c'], [1,-2,-3])
        'a - 2*b - 3*c'
        sage: t = PolynomialRing(RationalField(),'t').gen()
        sage: repr_lincomb(['a', 's', ''], [-t,t-2,t**2+2])
        '-t*a + (t-2)*s + (t^2+2)'
    """
    s = ""
    first = True
    i = 0

    all_atomic = True
    for c in coeffs:
        if is_latex and hasattr(symbols[i], '_latex_'):
            b = symbols[i]._latex_()
        else:
            b = str(symbols[i])
        if c != 0:
            coeff = coeff_repr(c, is_latex)
            if coeff == "1":
                coeff = ""
            elif coeff == "-1":
                coeff = "-"
            elif not is_latex and len(b) > 0:
                b = "*" + b
            elif len(coeff) > 0 and b == "1":
                b = ""
            if not first:
                coeff = " + %s"%coeff
            else:
                coeff = "%s"%coeff
            s += "%s%s"%(coeff, b)
            first = False
        i += 1
    if first:
        s = "0"
    s = s.replace("+ -","- ")
    if s[:2] == "1*":
        s = s[2:]
    elif s[:3] == "-1*":
        s = "-" + s[3:]
    s = s.replace(" 1*", " ")
    if s == "":
        return "1"
    return s

def strunc(s, n = 60):
    """
    Truncate at first space after position n, adding '...' if nontrivial truncation.
    """
    n = int(n)
    s = str(s)
    if len(s) > n:
        i = n
        while i < len(s) and s[i] != ' ':
            i += 1
        return s[:i] + " ..."
        #return s[:n-4] + " ..."
    return s



def newton_method_sizes(N):
    """
    Returns a sequence of integers $1 = a_1 \leq a_2 \leq \cdots \leq a_n = N$
    such that $a_j = \lceil a_{j+1} / 2 \rceil$ for all $j$.

    This is useful for Newton-style algorithms that double the precision at
    each stage. For example if you start at precision 1 and want an answer to
    precision 17, then it's better to use the intermediate stages 1, 2, 3, 5,
    9, 17 than to use 1, 2, 4, 8, 16, 17.

    INPUT:
        N -- positive integer

    EXAMPLES:
     sage: newton_method_sizes(17)
      [1, 2, 3, 5, 9, 17]
     sage: newton_method_sizes(16)
      [1, 2, 4, 8, 16]
     sage: newton_method_sizes(1)
      [1]

    AUTHOR:
        -- David Harvey (2006-09-09)
    """

    N = int(N)
    if N < 1:
        raise ValueError, "N (=%s) must be a positive integer" % N

    output = []
    while N > 1:
        output.append(N)
        N = (N + 1) >> 1

    output.append(1)
    output.reverse()
    return output


#################################################################
# Generally useful
#################################################################


def assert_attribute(x, attr, init=None):
    """
    If the object x has the attribute attr, do nothing.
    If not, set x.attr to init.
    """
    if x.__dict__.has_key(attr): return
    if attr[:2] == "__":
        z = str(x.__class__).split("'")
        if len(z) > 1:
            z = z[1]
        else:
            z = z[0]
        attr = "_" + z[len(x.__module__)+1:] + attr
    x.__dict__[attr] = init

#################################################################
# Useful but hard to classify
#################################################################

def srange(a,b=None,step=1, include_endpoint=False):
    """
    Return list of numbers \code{a, a+step, ..., a+k*step},
    where \code{a+k*step < b} and \code{a+(k+1)*step > b}.

    This is the best way to get an iterator over SAGE integers as
    opposed to Python int's.  It also allows you to specify step sizes
    to iterate.  It is potentially much slower than the Python range
    statement, depending on your application.

    INPUT:
        a -- number
        b -- number (default: None)
        step -- number (default: 1)
        include_endpoint -- whether or not to include the endpoint (default: False)

    OUTPUT:
        list

    If b is None, then b is set equal to a and a is
    set equal to the 0 in the parent of b.

    Unlike range, a and b can be any type of numbers, and the
    resulting list involves numbers of that type.

    NOTE: This function is called \code{srange} to distinguish
    it from the builtin Python \code{range} command.  The s
    at the beginning of the name stands for ``SAGE''.

    SEE ALSO: xsrange -- iterator version

    EXAMPLES:
        sage: v = srange(5); v
        [0, 1, 2, 3, 4]
        sage: type(v[2])
        <type 'sage.rings.integer.Integer'>

        sage: srange(1, 10)
        [1, 2, 3, 4, 5, 6, 7, 8, 9]

        sage: srange(10, 1, -1)
        [10, 9, 8, 7, 6, 5, 4, 3, 2]

        sage: srange(10,1,-1, include_endpoint=True)
        [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

        sage: Q = RationalField()
        sage: srange(1,10,Q('1/2'))
        [1, 3/2, 2, 5/2, 3, 7/2, 4, 9/2, 5, 11/2, 6, 13/2, 7, 15/2, 8, 17/2, 9, 19/2]

        sage: R = RealField()
        sage: srange(1,5,R('0.5'))
        [1, 1.50000000000000, 2.00000000000000, 2.50000000000000, 3.00000000000000, 3.50000000000000, 4.00000000000000, 4.50000000000000]
        sage: srange(0,1,R('0.4'))
        [0, 0.400000000000000, 0.800000000000000]
    """
    if b is None:
        b = a
        try:
            a = b.parent()(0)
        except AttributeError:
            a = type(b)(0)

    if step == 0:
        raise ValueError, "step size must be nonzero"
    num_steps = int(float((b-a)/step)) + 1
    if num_steps <= 0:
        return []
    v = [a] + [a + k*step for k in range(1,num_steps)]

    if step > 0:
        if v[num_steps-1] >= b:
            if include_endpoint:
                return v[:-1] + [b]
            else:
                return v[:-1]
        else:
            return v
    elif step < 0:
        if v[num_steps-1] <= b:
            if include_endpoint:
                return v[:-1] + [b]
            else:
                return v[:-1]
        else:
            return v

class xsrange:
    """
    Return an iterator over numbers \code{a, a+step, ..., a+k*step},
    where \code{a+k*step < b} and \code{a+(k+1)*step > b}.

    INPUT:
        a -- number
        b -- number
        step -- number (default: 1)
    OUTPUT:
        iterator

    Unlike range, a and b can be any type of numbers, and the
    resulting iterator involves numbers of that type.

    SEE ALSO: srange.

    NOTE: This function is called \code{xsrange} to distinguish
    it from the builtin Python \code{xrange} command.

    EXAMPLES:
        sage: list(xsrange(1,10))
        [1, 2, 3, 4, 5, 6, 7, 8, 9]

        sage: Q = RationalField()
        sage: list(xsrange(1, 10, Q('1/2')))
        [1, 3/2, 2, 5/2, 3, 7/2, 4, 9/2, 5, 11/2, 6, 13/2, 7, 15/2, 8, 17/2, 9, 19/2]

        sage: R = RealField()
        sage: list(xsrange(1, 5, R(0.5)))
        [1, 1.50000000000000, 2.00000000000000, 2.50000000000000, 3.00000000000000, 3.50000000000000, 4.00000000000000, 4.50000000000000]
        sage: list(xsrange(0, 1, R('0.4')))
        [0, 0.400000000000000, 0.800000000000000]

    Negative ranges are also allowed:
        sage: list(xrange(4,1,-1))
        [4, 3, 2]
        sage: list(sxrange(4,1,-1))
        [4, 3, 2]
        sage: list(sxrange(4,1,-1/2))
        [4, 7/2, 3, 5/2, 2, 3/2]
    """
    def __init__(self, a, b=None, step=1):
        self.__a = a
        self.__b = b
        if step == 0:
            raise ValueError, 'sxrange() arg 3 must not be zero'
        self.__step = step

    def __repr__(self):
        return 'xrange(%s, %s, %s)'%(self.__a, self.__b, self.__step)

    def __len__(self):
        if self.__b is None:
            return int(self.__a / self.__step)
        n = int((self.__b - self.__a) / self.__step)
        if n < 0:
            return 0
        return n

    def __iter__(self):
        return _xsrange(self.__a, self.__b, self.__step)

sxrange = xsrange


def _xsrange(a,b=None,step=1):
    if b is None:
        b = a
        try:
            a = b.parent()(0)
        except AttributeError:
            a = type(b)(0)
    cur = a
    if step > 0:
        while cur < b:
            yield cur
            cur += step
    elif step < 0:
        while cur > b:
            yield cur
            cur += step
    return

def random_sublist(X, s):
    """
    Return a pseudo-random sublist of the list X where the probability
    of including a particular element is s.

    INPUT:
        X -- list
        s -- floating point number between 0 and 1
    OUTPUT:
        list

    EXAMPLES:
        sage.: S = [1,7,3,4,18]
        sage.: random_sublist(S, 0.5)
        [7]
        sage.: random_sublist(S, 0.5)
        [1, 7, 3]
    """
    return [a for a in X if random.random() <= s]



def powerset(X):
    r"""
    Iterator over the \emph{list} of all subsets of the iterable X,
    in no particular order.  Each list appears exactly once,
    up to order.

    INPUT:
        X -- an iterable
    OUTPUT:
        iterator of lists

    EXAMPLES:
        sage: list(powerset([1,2,3]))
        [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
        sage: [z for z in powerset([0,[1,2]])]
        [[], [0], [[1, 2]], [0, [1, 2]]]

    Iterating over the power set of an infinite set is also allowed:
        sage: i = 0
        sage: for x in powerset(ZZ):
        ...    if i > 10:
        ...       break
        ...    else:
        ...       i += 1
        ...    print x,
        [] [0] [1] [0, 1] [-1] [0, -1] [1, -1] [0, 1, -1] [2] [0, 2] [1, 2]

    You may also use subsets as an alias for powerset:
        sage: subsets([1,2,3])   # random object location in output
        <generator object at 0xaeae418c>
        sage: list(subsets([1,2,3]))
        [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]

    \begin{notice} The reason we return lists instead of sets is that
    the elements of sets must be hashable and many structures on which
    one wants the powerset consist of non-hashable objects.
    \end{notice}

    AUTHORS:
        -- William Stein
        -- Nils Bruin (2006-12-19): rewrite to work for not-necessarily
                                    finite objects X.
    """
    yield []
    pairs = []
    for x in X:
        pairs.append((2**len(pairs),x))
        for w in xrange(2**(len(pairs)-1), 2**(len(pairs))):
            yield [x for m, x in pairs if m & w]

subsets = powerset

#################################################################
# Type checking
#################################################################
def typecheck(x, C, var="x"):
    """
    Check that x is of instance C.  If not raise a TypeError
    with an error message.
    """
    if not isinstance(x, C):
        raise TypeError, "%s (=%s) must be of type %s."%(var,x,C)

#################################################################
# System information
#################################################################
def is_64bit():
    """
    Determine whether this is a 64-bit computer.
    """
    import sys
    # TODO: There's probably a better way to do this..
    return sys.maxint == 9223372036854775807

#################################################################
# This will likely eventually be useful.
#################################################################

# From the Python Cookbook Ver 2, Recipe 20.4
class cached_attribute(object):
    """
    Computes attribute value and caches it in the instance.
    """
    def __init__(self, method, name=None):
        # record the unbound-method and the name
        self.method = method
        self.name = name or method.__name__
    def __get__(self, inst, cls):
        if inst is None:
            # instance attribute accessed on class, return self
            return self
        # compute, cache and return the instance's attribute value
        result = self.method(inst)
        setattr(inst, self.name, result)
        return result

class cached_class_attribute(cached_attribute):
    """
    Computes attribute value and caches it in the class.
    """
    def __get__(self, inst, cls):
        # just delegate to CachedAttribute, with 'cls' as ``instance''
        return super(CachedClassAttribute, self).__get__(cls, cls)

class lazy_prop(object):
    def __init__(self, calculate_function):
        self._calculate = calculate_function
        self.__doc__ = calculate_function.__doc__

    def __call__(self, obj, _=None):
        if obj is None:
            return self
        value = self._calculate(obj)
        setattr(obj, self._calculate.func_name, value)
        return value

def prop(f):
    return property(f, None, None, f.__doc__)


#################################################################
# Misc.
#################################################################

def exists(S, P):
    """
    If S contains an element x such that P(x) is True, this
    function returns True and the element x.  Otherwise it
    returns False and None.

    INPUT:
        S -- object (that supports enumeration)
        P -- function that returns True or False

    OUTPUT:
        bool -- whether or not P is True for some element x of S
        object -- x

    EXAMPLES:
    lambda functions are very useful when using the exists function:

        sage: exists([1,2,5], lambda x : x > 7)
        (False, None)
        sage: exists([1,2,5], lambda x : x > 3)
        (True, 5)

    The following example is similar to one in the MAGMA handbook.  We
    check whether certain integers are a some of two (small) cubes:

        sage: cubes = [t**3 for t in range(-10,11)]
        sage: exists([(x,y) for x in cubes for y in cubes], lambda v : v[0]+v[1] == 218)
        (True, (-125, 343))
        sage: exists([(x,y) for x in cubes for y in cubes], lambda v : v[0]+v[1] == 219)
        (False, None)
    """
    for x in S:
        if P(x): return True, x
    return False, None

def forall(S, P):
    """
    If P(x) is true every x in S, return True and None.
    If there is some element x in S such that P is not True,
    return False and x.

    INPUT:
        S -- object (that supports enumeration)
        P -- function that returns True or False

    OUTPUT:
        bool -- whether or not P is True for all elements of S
        object -- x

    EXAMPLES:
    lambda functions are very useful when using the forall function.
    As a toy example we test whether certain integers are >3.

        sage: forall([1,2,5], lambda x : x > 3)
        (False, 1)
        sage: forall([1,2,5], lambda x : x > 0)
        (True, None)

    Next we ask whether every positive integer <100 is a product of
    at most 2 prime factors:

        sage: forall(range(1,100),  lambda n : len(factor(n)) <= 2)
        (False, 30)

    The answer is no, and 30 is a counterexample.  However, every
    positive integer < 100 is a product of at most 3 primes.

        sage: forall(range(1,100),  lambda n : len(factor(n)) <= 3)
        (True, None)
    """
    for x in S:
        if not P(x): return False, x
    return True, None

#################################################################
# which source file?
#################################################################
import inspect
def sourcefile(object):
    """Work out which source or compiled file an object was defined in."""
    return inspect.getfile(object)


#################################################################
# alarm
#################################################################
__alarm_time=0
def __mysig(a,b):
    raise KeyboardInterrupt, "computation timed out because alarm was set for %s seconds"%__alarm_time

def alarm(seconds):
    """
    Raise a KeyboardInterrupt exception in a given number of seconds.
    This is useful for automatically interrupting long computations
    and can be trapped using exception handling (just catch
    KeyboardInterrupt).

    INPUT:
        seconds -- integer
    """
    seconds = int(seconds)
    # Set our alarm signal handler.
    signal.signal(signal.SIGALRM, __mysig)
    global __alarm_time
    __alarm_time = seconds
    signal.alarm(seconds)

def cancel_alarm():
    signal.signal(signal.SIGALRM, signal.SIG_IGN)


#################################################################
# debug tracing
#################################################################
import pdb
set_trace = pdb.set_trace


#################################################################
# temporary directory
#################################################################

def tmp_dir(name='dir'):
    r"""
    Create and return a temporary directory in \code{\$HOME/.sage/temp/hostname/pid/}
    """
    name = str(name)
    n = 0
    while True:
        tmp = "%s/%s_%s"%(SAGE_TMP, name, n)
        if not os.path.exists(tmp):
            break
        n += 1
    try:
        os.makedirs(tmp)
    except IOError:
        # Put in local directory instead, e.g., because user doesn't
        # have privileges to write in SAGE's tmp directory.  That's OK.
        n = 0
        while True:
            tmp = "/temp/tmp_%s_%s"%(name, n)
            if not os.path.exists(tmp):
                break
            n += 1
        os.makedirs(tmp)
    return os.path.abspath(tmp)


#################################################################
# temporary filename
#################################################################

__tmp_n = 0

def tmp_filename(name='tmp'):
    name = str(name)
    global __tmp_n
    while True:
        tmp = "%s/%s_%s"%(SAGE_TMP, name, __tmp_n)
        __tmp_n += 1
        if not os.path.exists(tmp):
            break
    return tmp

def graphics_filename(ext='png'):
    """
    Return the next available canonical filename for a plot/graphics
    file.
    """
    i = 0
    while os.path.exists('sage%d.%s'%(i,ext)):
        i += 1
    filename = 'sage%d.%s'%(i,ext)
    return filename

#################################################################
# 32/64-bit computer?
#################################################################
is_64_bit = sys.maxint >= 9223372036854775807
is_32_bit = not is_64_bit

#################################################################
# Word wrap lines
#################################################################
def word_wrap(s, ncols=85):
    t = []
    if ncols == 0:
        return s
    for x in s.split('\n'):
        if len(x) == 0 or x.lstrip()[:5] == 'sage:':
            t.append(x)
            continue
        while len(x) > ncols:
            k = ncols
            while k > 0 and x[k] != ' ':
                k -= 1
            if k == 0:
                k = ncols
                end = '\\'
            else:
                end = ''
            t.append(x[:k] + end)
            x = x[k:]
            k=0
            while k < len(x) and x[k] == ' ':
                k += 1
            x = x[k:]
        t.append(x)
    return '\n'.join(t)


def getitem(v, n):
    r"""
    Variant of getitem that coerces to an int if a TypeError is raised.

    (This is not needed anymore -- classes should define an __index__ method.)

    Thus, e.g., \code{getitem(v,n)} will work even if $v$ is a Python
    list and $n$ is a SAGE integer.

    EXAMPLES:
        sage: v = [1,2,3]

    The following use to fail in SAGE <= 1.3.7.  Now it works fine:
        sage: v[ZZ(1)]
        2

    This always worked.
        sage: getitem(v, ZZ(1))
        2
    """
    try:
        return v[n]
    except TypeError:
        return v[int(n)]


def branch_current_hg():
    """
    Return the current hg Mercurial branch name.  If the branch
    is 'main', which is the default branch, then just '' is returned.
    """
    s = os.popen('ls -l %s/devel/sage'%os.environ['SAGE_ROOT']).read()
    if 'No such file or directory' in s:
        raise RuntimeError, "unable to determine branch?!"
    # do ls -l and look for a symlink, which `ls` represents by a '->'
    i = s.rfind('->')
    if i == -1:
        raise RuntimeError, "unable to determine branch?!"
    s = s[i+2:]
    i = s.find('-')
    if i == -1:
        return ''
    br = s[i+1:].strip()
    return br

def branch_current_hg_notice(branch):
    r"""
    Return a string describing the current branch and that the library is
    being loaded.  This is called by the \code{<SAGE_ROOT>/local/bin/sage-sage}
    script.

    INPUT:
        string -- a representation of the name of the SAGE library branch.

    OUTPUT:
        string

    NOTE: If the branch is main, then return an empty string.
    """
    if branch[-1] == '/':
        branch = branch[:-1]
    if branch == 'main':
        return ''
    notice = 'Loading SAGE library. Current Mercurial branch is: '
    return notice + branch



def pad_zeros(s, size=3):
    """
    EXAMPLES:
        sage: pad_zeros(100)
        '100'
        sage: pad_zeros(10)
        '010'
        sage: pad_zeros(10, 5)
        '00010'
        sage: pad_zeros(389, 5)
        '00389'
        sage: pad_zeros(389, 10)
        '0000000389'
    """
    return "0"*(size-len(str(s))) + str(s)
