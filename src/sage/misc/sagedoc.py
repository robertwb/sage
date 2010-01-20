r"""
Format Sage documentation for viewing with IPython and the notebook

AUTHORS:

- William Stein (2005): initial version.
- Nick Alexander (2007): nodetex functions
- Nick Alexander (2008): search_src, search_def improvements
- Martin Albrecht (2008-03-21): parse LaTeX description environments in sagedoc
- John Palmieri (2009-04-11): fix for #5754 plus doctests
- Dan Drake (2009-05-21): refactor search_* functions, use system 'find' instead of sage -grep
- John Palmieri (2009-06-28): don't use 'find' -- use Python (os.walk, re.search) instead.
"""

#*****************************************************************************
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
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

import os, re, sys
import pydoc
from subprocess import Popen, PIPE
from sage.misc.viewer import browser
from sage.misc.misc import SAGE_DOC, tmp_dir
from sagenb.misc.sphinxify import sphinxify
import sage.version

# two kinds of substitutions: math, which should only be done on the
# command line -- in the notebook, these should instead by taken care
# of by jsMath -- and nonmath, which should be done always.
math_substitutes = [('\\to', '-->'),
                    ('\\leq', '<='),
                    ('\\geq', '>='),
                    ('\\le', '<='),
                    ('\\ge', '>='),
                    ('cdots', '...'),
                    ('\\cdot', ' *'),
                    (' \\times', ' x'),
                    ('\\times', ' x'),
                    ('backslash','\\'),
                    ('mapsto', ' |--> '),
                    ('ldots', '...')]
nonmath_substitutes = [('\\_','_'),
                       ('\\item', '* '),
                       ('<BLANKLINE>',''),
                       ('\\bf', ''),
                       ('\\sage', 'SAGE'),
                       ('\\SAGE', 'SAGE'),
                       ('\\rm', ''),
                       ('backslash','\\'),
                       ('begin{enumerate}',''),
                       ('end{enumerate}',''),
                       ('begin{description}',''),
                       ('end{description}',''),
                       ('begin{itemize}',''),
                       ('end{itemize}',''),
                       ('begin{verbatim}',''),
                       ('end{verbatim}',''),
                       ('note{','NOTE: ')]

def _rmcmd(s, cmd, left='', right=''):
    """
    Remove the LaTeX command ``cmd`` from the string ``s``.  This
    function is used by ``detex``.

    INPUT:

    - ``s`` - (string) string from which to remove the command

    - ``cmd`` - (string) command to be removed.  This should be a
      command which takes a single argument, like 'emph' or 'url'; the
      command is removed, but its argument is not.

    - ``left``, ``right`` - (string, optional, default '') add these
      strings at the left and right ends of the command. See the
      examples.

    EXAMPLES::

        sage: from sage.misc.sagedoc import _rmcmd
        sage: _rmcmd('Check out \\url{http://www.sagemath.org}.', 'url')
        'Check out http://www.sagemath.org.'
        sage: _rmcmd('Text in \\emph{italics} looks like this.', 'emph', '*', '*')
        'Text in *italics* looks like this.'
        sage: _rmcmd('This is a \\very{silly} example.', 'very', right='!?')
        'This is a silly!? example.'
    """
    c = '\\%s{'%cmd
    while True:
        i = s.find(c)
        if i == -1:
            return s
        nesting = 1
        j = i+len(c)+1
        while j < len(s) and nesting > 0:
            if s[j] == '{':
                nesting += 1
            elif s[j] == '}':
                nesting -= 1
            j += 1
        j -= 1  # j is position of closing '}'
        if j < len(s):
            s = s[:i] + left + s[i+len(c):j] + right + s[j+1:]
        else:
            return s

# I wanted to be cool and use regexp's, but they aren't really
# useful, since really this is a parsing problem, because of
# nesting of commands, etc.   Since it doesn't have to be
# super super fast (it's a page of text scrolled to the user),
# the above works fine.

#
## import re
## def _rmcmd(s, cmd, left='', right=''):
##     c = '\\%s{.*}'%cmd
##     r = re.compile(c, re.DOTALL)
##     while True:
##         m = r.search(s)
##         if m is None: break
##         s = s[:m.start()] + left + s[m.start()+len(cmd)+1:m.end()-1] \
##             + right + s[m.end():]
##     return s

import re
itempattern = re.compile(r"\\item\[?([^]]*)\]? *(.*)")
itemreplace = r"* \1 \2"

def detex(s, embedded=False):
    r"""nodetex
    This strips LaTeX commands from a string; it is used by the
    ``format`` function to process docstrings for display from the
    command line interface.

    INPUT:

    - ``s`` - string
    - ``embedded`` - boolean (optional, default False)

    If ``embedded`` is False, then do the replacements in both
    ``math_substitutes`` and ``nonmath_substitutes``.  If True, then
    only do ``nonmath_substitutes``.

    OUTPUT: string

    EXAMPLES::

        sage: from sage.misc.sagedoc import detex
        sage: detex(r'Some math: `n \geq k`.  A website: \url{sagemath.org}.')
        'Some math: `n >= k`.  A website: sagemath.org.'
        sage: detex(r'More math: `x \mapsto y`.  {\bf Bold face}.')
        'More math: `x  |-->  y`.  { Bold face}.'
        sage: detex(r'`a, b, c, \ldots, z`')
        '`a, b, c, ..., z`'
        sage: detex(r'`a, b, c, \ldots, z`', embedded=True)
        '`a, b, c, \\\\ldots, z`'
    """
    s = _rmcmd(s, 'url')
    s = _rmcmd(s, 'code')
    s = _rmcmd(s, 'class')
    s = _rmcmd(s, 'mbox')
    s = _rmcmd(s, 'text')
    s = _rmcmd(s, 'section')
    s = _rmcmd(s, 'subsection')
    s = _rmcmd(s, 'subsubsection')
    s = _rmcmd(s, 'note', 'NOTE: ', '')
    s = _rmcmd(s, 'emph', '*', '*')
    s = _rmcmd(s, 'textbf', '*', '*')

    s = re.sub(itempattern, itemreplace, s)

    for a,b in nonmath_substitutes:
        s = s.replace(a,b)
    if not embedded: # not in the notebook
        for a,b in math_substitutes:  # do math substitutions
            s = s.replace(a,b)
        s = s.replace('\\','')        # nuke backslashes
        s = s.replace('.. math::\n', '')  # get rid of .. math:: directives
    else:
        s = s.replace('\\','\\\\')    # double up backslashes for jsMath
    return s

def format(s, embedded=False):
    r"""
    Format Sage documentation ``s`` for viewing with IPython.

    This calls ``detex`` on ``s`` to convert LaTeX commands to plain
    text, and if ``s`` contains a string of the form "<<<obj>>>",
    then it replaces it with the docstring for "obj".

    INPUT:

    - ``s`` - string
    - ``embedded`` - boolean (optional, default False)

    OUTPUT: string

    Set ``embedded`` equal to True if formatting for use in the
    notebook; this just gets passed as an argument to ``detex``.

    EXAMPLES::

        sage: from sage.misc.sagedoc import format
        sage: identity_matrix(2).rook_vector.__doc__[115:184]
        'Let `A` be a general `m` by `n`\n        (0,1)-matrix with `m \\le n`. '
        sage: format(identity_matrix(2).rook_vector.__doc__[115:184])
        'Let `A` be a general `m` by `n`\n        (0,1)-matrix with `m <= n`. '

    If the first line of the string is 'nodetex', remove 'nodetex' but
    don't modify any TeX commands::

        sage: format("nodetex\n`x \\geq y`")
        '\n`x \\geq y`'

    Testing a string enclosed in triple angle brackets::

        sage: format('<<<identity_matrix')
        '<<<identity_matrix'
        sage: format('identity_matrix>>>')
        'identity_matrix>>>'
        sage: format('<<<identity_matrix>>>')[:28]
        '\nDefinition: identity_matrix'
    """
    if not isinstance(s, str):
        raise TypeError, "s must be a string"

    # parse directives at beginning of docstring
    # currently, only 'nodetex' is supported.
    # 'no' + 'doctest' may be supported eventually (don't type that as
    # one word, or the whole file will not be doctested).
    first_newline = s.find('\n')
    if first_newline > -1:
        first_line = s[:first_newline]
    else:
        first_line = s
    directives = [ d.lower() for d in first_line.split(',') ]

    import sage.all
    import sage.server.support
    docs = set([])
    while True:
        i = s.find("<<<")
        if i == -1: break
        j = s[i+3:].find('>>>')
        if j == -1: break
        obj = s[i+3:i+3+j]
        if obj in docs:
            t = ''
        else:
            x = eval('sage.all.%s'%obj, locals())
            t0 = sage.misc.sageinspect.sage_getdef(x, obj)
            t1 = my_getdoc(x)
            t = 'Definition: ' + t0 + '\n\n' + t1
            docs.add(obj)
        s = s[:i] + '\n' + t + s[i+6+j:]

    if 'nodetex' not in directives:
        s = detex(s, embedded=embedded)
    else:
        # strip the 'nodetex' directive from s
        s = s.replace('nodetex', '', 1)
    return s

def format_src(s):
    """
    Format Sage source code ``s`` for viewing with IPython.

    If ``s`` contains a string of the form "<<<obj>>>", then it
    replaces it with the source code for "obj".

    INPUT: ``s`` - string

    OUTPUT: string

    EXAMPLES::

        sage: from sage.misc.sagedoc import format_src
        sage: format_src('unladen swallow')
        'unladen swallow'
        sage: format_src('<<<Sq>>>')[5:15]
        'Sq(*nums):'
    """
    if not isinstance(s, str):
        raise TypeError, "s must be a string"
    docs = set([])
    import sage.all
    while True:
        i = s.find("<<<")
        if i == -1: break
        j = s[i+3:].find('>>>')
        if j == -1: break
        obj = s[i+3:i+3+j]
        if obj in docs:
            t = ''
        else:
            x = eval('sage.all.%s'%obj, locals())
            t = my_getsource(x, False)
            docs.add(obj)
        if t is None:
            print x
            t = ''
        s = s[:i] + '\n' + t + s[i+6+j:]

    return s

###############################

def _search_src_or_doc(what, string, extra1='', extra2='', extra3='',
                       extra4='', extra5='', **kwds):
    r"""
    Search the Sage library or documentation for lines containing
    ``string`` and possibly some other terms. This function is used by
    :func:`search_src`, :func:`search_doc`, and :func:`search_def`.

    INPUT:

    - ``what``: either ``'src'`` or ``'doc'``, according to whether you
      are searching the documentation or source code.
    - the rest of the input is the same as :func:`search_src`,
      :func:`search_doc`, and :func:`search_def`.

    OUTPUT:

    If ``interact`` is ``False``, a string containing the results;
    otherwise, there is no output and the results are presented
    according to whether you are using the notebook or command-line
    interface. In the command-line interface, each line of the results
    has the form ``filename:num:line of code``, where ``num`` is the
    line number in ``filename`` and ``line of code`` is the line that
    matched your search terms.

    EXAMPLES::

        sage: from sage.misc.sagedoc import _search_src_or_doc
        sage: print _search_src_or_doc('src', 'matrix\(', 'incidence_structures', 'self', '^combinat', interact=False) # random # long time
        misc/sagedoc.py:        sage: _search_src_or_doc('src', 'matrix(', 'incidence_structures', 'self', '^combinat', interact=False)
        combinat/designs/incidence_structures.py:        M1 = self.incidence_matrix()
        combinat/designs/incidence_structures.py:        A = self.incidence_matrix()
        combinat/designs/incidence_structures.py:        M = transpose(self.incidence_matrix())
        combinat/designs/incidence_structures.py:    def incidence_matrix(self):
        combinat/designs/incidence_structures.py:        A = self.incidence_matrix()
        combinat/designs/incidence_structures.py:        A = self.incidence_matrix()
        combinat/designs/incidence_structures.py:        #A = self.incidence_matrix()

    TESTS:

    The examples are nice, but marking them "random" means we're not
    really testing if the function works, just that it completes. These
    tests aren't perfect, but are reasonable.

    ::

        sage: len(_search_src_or_doc('src', 'matrix\(', 'incidence_structures', 'self', 'combinat', interact=False).splitlines()) > 1
        True

        sage: 'abvar/homology' in _search_src_or_doc('doc', 'homology', 'variety', interact=False)
        True

        sage: 'divisors' in _search_src_or_doc('src', '^ *def prime', interact=False)
        True
    """
    # process keywords
    if 'interact' in kwds:
        interact = kwds['interact']
    else:
        interact = True
    if 'path_re' in kwds:
        path_re = kwds['path_re']
    else:
        path_re = ''
    if 'module' in kwds:
        module = kwds['module']
    else:
        module = 'sage'
    if 'whole_word' in kwds:
        whole_word = kwds['whole_word']
    else:
        whole_word = False
    if 'ignore_case' in kwds:
        ignore_case = kwds['ignore_case']
    else:
        ignore_case = False
    # done processing keywords
    # define module, exts (file extension), title (title of search),
    # base_path (top directory in which to search)
    ROOT = os.environ['SAGE_ROOT']
    if what == 'src':
        if module.find('sage') == 0:
            module = module[4:].lstrip(".")  # remove 'sage' or 'sage.' from module
            base_path = os.path.join('devel', 'sage', 'sage')
        else:
            base_path = os.path.join('devel', 'sage')
        module = module.replace(".", os.sep)
        exts = ['py', 'pyx', 'pxd']
        title = 'Source Code'
    else:
        module = ''
        exts = ['html']
        title = 'Documentation'
        base_path = os.path.join('devel', 'sage', 'doc', 'output')

        # check if any documentation is missing.  first read the start
        # of SAGE_ROOT/devel/sage/doc/common/builder.py to find list
        # of languages, documents, and documents to omit
        doc_path = os.path.join(ROOT, 'devel', 'sage', 'doc')
        builder = open(os.path.join(doc_path, 'common', 'builder.py'))
        s = builder.read()[:1000]
        builder.close()
        # list of languages
        lang = []
        idx = s.find("LANGUAGES")
        if idx != -1:
            start = s[idx:].find('[')
            end =  s[idx:].find(']')
            if start != -1 and end != -1:
                lang = s[idx+start+1:idx+end].translate(None, "'\" ").split(",")
        # documents in SAGE_ROOT/devel/sage/doc/LANG/ to omit
        omit = []
        idx = s.find("OMIT")
        if idx != -1:
            start = s[idx:].find('[')
            end =  s[idx:].find(']')
            if start != -1 and end != -1:
                omit = s[idx+start+1:idx+end].translate(None, "'\" ").split(",")
        # list of documents, minus the omitted ones
        documents = []
        for L in lang:
            documents += [os.path.join(L, dir) for dir
                          in os.listdir(os.path.join(doc_path, L))
                          if dir not in omit]
        # now check to see if any documents are missing.  this just
        # checks to see if the appropriate output directory exists,
        # not that it contains a complete build of the docs.
        missing = [os.path.join(ROOT, base_path, 'html', doc)
                   for doc in documents if not
                   os.path.exists(os.path.join(ROOT, base_path, 'html', doc))]
        num_missing = len(missing)
        if num_missing > 0:
            print """Warning, the following Sage documentation hasn't been built,
so documentation search results may be incomplete:
"""
            for s in missing:
                print s
            if num_missing > 1:
                print """
You can build these with 'sage -docbuild DOCUMENT html',
where DOCUMENT is one of""",
                for s in missing:
                    if s.find('en') != -1:
                        print "'%s'," % os.path.split(s)[-1],
                    else:
                        print "'%s'," % os.path.join(
                            os.path.split(os.path.split(s)[0])[-1],
                            os.path.split(s)[-1]),
                print """
or you can use 'sage -docbuild all html' to build all of the missing documentation."""
            else:
                s = missing[0]
                if s.find('en') != -1:
                    s = os.path.split(s)[-1]
                else:
                    s = os.path.join(
                        os.path.split(os.path.split(s)[0])[-1],
                        os.path.split(s)[-1])
                print """
You can build this with 'sage -docbuild %s html'.""" % s

    base_path = os.path.join(ROOT, base_path)
    strip = len(base_path)
    results = ''
    # in regular expressions, '\bWORD\b' matches 'WORD' but not
    # 'SWORD' or 'WORDS'.  so if the user requests a whole_word
    # search, append and prepend '\b' to each string.
    if whole_word:
        string = r'\b' + string + r'\b'
        if extra1:
            extra1 = r'\b' + extra1 + r'\b'
        if extra2:
            extra2 = r'\b' + extra2 + r'\b'
        if extra3:
            extra3 = r'\b' + extra3 + r'\b'
        if extra4:
            extra4 = r'\b' + extra4 + r'\b'
        if extra5:
            extra5 = r'\b' + extra5 + r'\b'
    if ignore_case:
        # 'flags' is a list of arguments passed to re.search
        flags = [re.IGNORECASE]
    else:
        flags = []
    # done with preparation; ready to start search
    for dirpath, dirs, files in os.walk(os.path.join(base_path, module)):
        for f in files:
            if re.search("\.(" + "|".join(exts) + ")$", f):
                filename = os.path.join(dirpath, f)
                if re.search(path_re, filename):
                    match_list = [(lineno, line) for lineno, line in
                                  enumerate(open(filename).read().splitlines(True))
                                  if re.search(string, line, *flags)]
                    for extra in [extra1, extra2, extra3, extra4, extra5]:
                        if extra:
                            match_list = filter(lambda s:
                                                    re.search(extra, s[1],
                                                              re.MULTILINE,
                                                              *flags),
                                                match_list)
                    for num, line in match_list:
                        results += ':'.join([filename[strip:].lstrip("/"),
                                             str(num+1),
                                             line])

    if not interact:
        return results

    from sage.server.support import EMBEDDED_MODE
    if EMBEDDED_MODE:   # I.e., running from the notebook
        # format the search terms nicely
        terms = ', '.join(['"%s"' % s for s in [string] + [extra1,
                          extra2, extra3, extra4, extra5] if s])
        print format_search_as_html(title, results, terms)
    else:
        # hard-code a 25-line screen into the pager; this works around a
        # problem with doctests: see
        # http://trac.sagemath.org/sage_trac/ticket/5806#comment:11
        from IPython.genutils import page
        page(results, screen_lines = 25)


def search_src(string, extra1='', extra2='', extra3='', extra4='',
               extra5='', **kwds):
    r"""
    Search Sage library source code for lines containing ``string``.
    The search is case-sensitive.

    INPUT:

    - ``string`` - a string to find in the Sage source code.

    - ``extra1``, ..., ``extra5`` - additional strings to require when
      searching.  Lines must match all of these, as well as ``string``.

    - ``whole_word`` (optional, default False) - if True, search for
      ``string`` and ``extra1`` (etc.) as whole words only.  This
      assumes that each of these arguments is a single word, not a
      regular expression, and it might have unexpected results if used
      with regular expressions.

    - ``ignore_case`` (optional, default False) - if True, perform a
      case-insensitive search

    - ``interact`` (optional, default ``True``) - if ``False``, return
      a string with all the matches. Otherwise, this function returns
      ``None``, and the results are displayed appropriately, according
      to whether you are using the notebook or the command-line
      interface. You should not ordinarily need to use this.

    - ``path_re`` (optional, default '') - regular expression which
      the filename (including the path) must match.

    - ``module`` (optional, default 'sage') - the module in which to
      search.  The default is 'sage', the entire Sage library.  If
      ``module`` doesn't start with "sage", then the links in the
      notebook output may not function.

    The file paths in the output are relative to
    ``$SAGE_ROOT/devel/sage/``. In the command-line interface, each line
    of the results has the form ``filename:num:line of code``, where
    ``num`` is the line number in ``filename`` and ``line of code`` is
    the line that matched your search terms.

    The ``string`` and ``extraN`` arguments are treated as regular
    expressions, as is ``path_re``, and errors will be raised if they
    are invalid. The matches will be case-sensitive unless
    ``ignore_case`` is True.

    .. note::

        The ``extraN`` parameters are present only because
        ``search_src(string, *extras, interact=False)``
        is not parsed correctly by Python 2.6; see http://bugs.python.org/issue1909.

    EXAMPLES:

    First note that without using ``interact=False``, this function
    produces no output, while with ``interact=False``, the output is a
    string.  These examples almost all use this option.

    You can search for "matrix" by typing ``search_src("matrix")``.
    This particular search will produce many results::

        sage: len(search_src("matrix", interact=False).splitlines()) # random # long time
        9522

    You can restrict to the Sage calculus code with
    ``search_src("matrix", module="sage.calculus")``, and this
    produces many fewer results::

        sage: len(search_src("matrix", module="sage.calculus", interact=False).splitlines()) # random
        26

    Note that you can do tab completion on the ``module`` string.
    Another way to accomplish a similar search::

        sage: len(search_src("matrix", path_re="calc", interact=False).splitlines()) > 15
        True

    The following produces an error because the string 'fetch(' is a
    malformed regular expression::

        sage: print search_src(" fetch(", "def", interact=False)
        Traceback (most recent call last):
        ...
        error: unbalanced parenthesis

    To fix this, *escape* the parenthesis with a backslash::

        sage: print search_src(" fetch\(", "def", interact=False) # random # long time
        matrix/matrix0.pyx:    cdef fetch(self, key):
        matrix/matrix0.pxd:    cdef fetch(self, key)

        sage: print search_src(" fetch\(", "def", "pyx", interact=False) # random # long time
        matrix/matrix0.pyx:    cdef fetch(self, key):

    As noted above, the search is case-sensitive, but you can make it
    case-insensitive with the 'ignore_case' key word::

        sage: s = search_src('Matrix', path_re='matrix', interact=False); s.find('x') > 0
        True

        sage: s = search_src('MatRiX', path_re='matrix', interact=False); s.find('x') > 0
        False

        sage: s = search_src('MatRiX', path_re='matrix', interact=False, ignore_case=True); s.find('x') > 0
        True

    A little recursive narcissism: let's do a doctest that searches for
    this function's doctests. Note that you can't put "sage:" in the
    doctest string because it will get replaced by the Python ">>>"
    prompt.

    ::

        sage: print search_src('^ *sage[:] .*search_src\(', interact=False) # long time
        misc/sagedoc.py:... len(search_src("matrix", interact=False).splitlines()) # random # long time
        misc/sagedoc.py:... len(search_src("matrix", module="sage.calculus", interact=False).splitlines()) # random
        misc/sagedoc.py:... len(search_src("matrix", path_re="calc", interact=False).splitlines()) > 15
        misc/sagedoc.py:... print search_src(" fetch(", "def", interact=False)
        misc/sagedoc.py:... print search_src(" fetch\(", "def", interact=False) # random # long time
        misc/sagedoc.py:... print search_src(" fetch\(", "def", "pyx", interact=False) # random # long time
        misc/sagedoc.py:... s = search_src('Matrix', path_re='matrix', interact=False); s.find('x') > 0
        misc/sagedoc.py:... s = search_src('MatRiX', path_re='matrix', interact=False); s.find('x') > 0
        misc/sagedoc.py:... s = search_src('MatRiX', path_re='matrix', interact=False, ignore_case=True); s.find('x') > 0
        misc/sagedoc.py:... print search_src('^ *sage[:] .*search_src\(', interact=False) # long time
        misc/sagedoc.py:... len(search_src("matrix", interact=False).splitlines()) > 9000 # long time
        misc/sagedoc.py:... print search_src('matrix', 'column', 'row', 'sub', 'start', 'index', interact=False) # random # long time

    TESTS:

    As of this writing, there are about 9500 lines in the Sage library that
    contain "matrix"; it seems safe to assume we'll continue to have
    over 9000 such lines::

        sage: len(search_src("matrix", interact=False).splitlines()) > 9000 # long time
        True

    Check that you can pass 5 parameters::

        sage: print search_src('matrix', 'column', 'row', 'sub', 'start', 'index', interact=False) # random # long time
        matrix/matrix0.pyx:598:        Get The 2 x 2 submatrix of M, starting at row index and column
        matrix/matrix0.pyx:607:        Get the 2 x 3 submatrix of M starting at row index and column index
        matrix/matrix0.pyx:924:        Set the 2 x 2 submatrix of M, starting at row index and column
        matrix/matrix0.pyx:933:        Set the 2 x 3 submatrix of M starting at row index and column

    """
    return _search_src_or_doc('src', string, extra1=extra1, extra2=extra2,
                              extra3=extra3, extra4=extra4, extra5=extra5,
                              **kwds)

def search_doc(string, extra1='', extra2='', extra3='', extra4='',
               extra5='', **kwds):
    """
    Search Sage HTML documentation for lines containing ``string``. The
    search is case-sensitive.

    The file paths in the output are relative to
    ``$SAGE_ROOT/devel/sage/doc/output``.

    INPUT:

    - ``string`` - a string to find in the Sage documentation.

    - ``extra1``, ..., ``extra5`` - additional strings to require when
      searching.  Lines must match all of these, as well as ``string``.

    - ``whole_word`` (optional, default False) - if True, search for
      ``string`` and ``extra1`` (etc.) as whole words only.  This
      assumes that each of these arguments is a single word, not a
      regular expression, and it might have unexpected results if used
      with regular expressions.

    - ``ignore_case`` (optional, default False) - if True, perform a
      case-insensitive search

    - ``interact`` (optional, default ``True``) - if ``False``, return
      a string with all the matches. Otherwise, this function returns
      ``None``, and the results are displayed appropriately, according
      to whether you are using the notebook or the command-line
      interface. You should not ordinarily need to use this.

    - ``path_re`` (optional, default '') - regular expression which
      the filename (including the path) must match.

    The ``string`` and ``extraN`` arguments are treated as regular
    expressions, as is ``path_re``, and errors will be raised if they
    are invalid. The matches will be case-sensitive unless
    ``ignore_case`` is True.

    In the command-line interface, each line of the results
    has the form ``filename:num:line of code``, where ``num`` is the
    line number in ``filename`` and ``line of code`` is the line that
    matched your search terms. This may not be very helpful for this
    function, but we include it anyway.

    .. note::

        The ``extraN`` parameters are present only because
        ``search_src(string, *extras, interact=False)``
        is not parsed correctly by Python 2.6; see http://bugs.python.org/issue1909.

    EXAMPLES::

        sage: search_doc('creates a polynomial', path_re='tutorial', interact=False) # random
        html/en/tutorial/tour_polynomial.html:<p>This creates a polynomial ring and tells Sage to use (the string)

    If you search the documentation for 'tree', then you will get too
    many results, because many lines in the documentation contain the
    word 'toctree'.  If you use the ``whole_word`` option, though, you
    can search for 'tree' without returning all of the instances of
    'toctree'.  In the following, since ``search_doc('tree',
    interact=False)`` returns a string with one line for each match,
    counting the length of ``search_doc('tree',
    interact=False).splitlines()`` gives the number of matches. ::

        sage: len(search_doc('tree', interact=False).splitlines()) > 2000
        True
        sage: len(search_doc('tree', whole_word=True, interact=False).splitlines()) < 100
        True
    """
    return _search_src_or_doc('doc', string, extra1=extra1, extra2=extra2,
                              extra3=extra3, extra4=extra4, extra5=extra5,
                              **kwds)

def search_def(name, extra1='', extra2='', extra3='', extra4='',
               extra5='', **kwds):
    r"""
    Search Sage library source code for function definitions containing
    ``name``. The search is case sensitive.

    INPUT:

    - ``name`` - a string to find in the names of functions in the Sage
      source code.

    - ``extra1``, ..., ``extra4`` - additional strings to require, as
      in :func:`search_src`.

    - ``whole_word`` (optional, default False) - if True, search for
      ``string`` and ``extra1`` (etc.) as whole words only.  This
      assumes that each of these arguments is a single word, not a
      regular expression, and it might have unexpected results if used
      with regular expressions.

    - ``ignore_case`` (optional, default False) - if True, perform a
      case-insensitive search

    - ``interact`` (optional, default ``True``) - if ``False``, return
      a string with all the matches. Otherwise, this function returns
      ``None``, and the results are displayed appropriately, according
      to whether you are using the notebook or the command-line
      interface. You should not ordinarily need to use this.

    - ``path_re`` (optional, default '') - regular expression which
      the filename (including the path) must match.

    - ``module`` (optional, default 'sage') - the module in which to
      search.  The default is 'sage', the entire Sage library.  If
      ``module`` doesn't start with "sage", then the links in the
      notebook output may not function.

    The ``string`` and ``extraN`` arguments are treated as regular
    expressions, as is ``path_re``, and errors will be raised if they
    are invalid. The matches will be case-sensitive unless
    ``ignore_case`` is True.

    In the command-line interface, each line of the results has the form
    ``filename:num:line of code``, where ``num`` is the line number in
    ``filename`` and ``line of code`` is the line that matched your
    search terms.

    .. note::

        The regular expression used by this function only finds function
        definitions that are preceded by spaces, so if you use tabs on a
        "def" line, this function will not find it. As tabs are not
        allowed in Sage library code, this should not be a problem.

    .. note::

        The ``extraN`` parameters are present only because
        ``search_src(string, *extras, interact=False)``
        is not parsed correctly by Python 2.6; see http://bugs.python.org/issue1909.

    EXAMPLES::

        sage: print search_def("fetch", interact=False) # random # long time
        matrix/matrix0.pyx:    cdef fetch(self, key):
        matrix/matrix0.pxd:    cdef fetch(self, key)

        sage: print search_def("fetch", path_re="pyx", interact=False) # random # long time
        matrix/matrix0.pyx:    cdef fetch(self, key):
    """
    # since we convert name to a regular expression, we need to do the
    # 'whole_word' conversion here, rather than pass it on to
    # _search_src_or_doc.
    if 'whole_word' in kwds and kwds['whole_word']:
        name = r'\b' + name + r'\b'
        if extra1:
            extra1 = r'\b' + extra1 + r'\b'
        if extra2:
            extra2 = r'\b' + extra2 + r'\b'
        if extra3:
            extra3 = r'\b' + extra3 + r'\b'
        if extra4:
            extra4 = r'\b' + extra4 + r'\b'
        if extra5:
            extra5 = r'\b' + extra5 + r'\b'
        kwds['whole_word'] = False

    return _search_src_or_doc('src', '^ *[c]?def.*%s' % name, extra1=extra1,
                              extra2=extra2, extra3=extra3, extra4=extra4,
                              extra5=extra5, **kwds)

def format_search_as_html(what, r, search):
    r"""
    Format the output from ``search_src``, ``search_def``, or
    ``search_doc`` as html, for use in the notebook.

    INPUT:

    - ``what`` - (string) what was searched (source code or
      documentation)
    - ``r`` - (string) the results of the search
    - ``search`` - (string) what was being searched for

    This function parses ``r``: it should have the form ``FILENAME:
    string`` where FILENAME is the file in which the string that matched
    the search was found. Everything following the first colon is
    ignored; we just use the filename. If FILENAME ends in '.html', then
    this is part of the documentation; otherwise, it is in the source
    code.  In either case, an appropriate link is created.

    EXAMPLES::

        sage: from sage.misc.sagedoc import format_search_as_html
        sage: format_search_as_html('Source', 'algebras/steenrod_algebra_element.py:        an antihomomorphism: if we call the antipode `c`, then', 'antipode antihomomorphism')
        '<html><font color="black"><h2>Search Source: antipode antihomomorphism</h2></font><font color="darkpurple"><ol><li><a href="/src/algebras/steenrod_algebra_element.py"><tt>algebras/steenrod_algebra_element.py</tt></a>\n</ol></font></html>'
        sage: format_search_as_html('Other', 'html/en/reference/sage/algebras/steenrod_algebra_element.html:an antihomomorphism: if we call the antipode <span class="math">c</span>, then', 'antipode antihomomorphism')
        '<html><font color="black"><h2>Search Other: antipode antihomomorphism</h2></font><font color="darkpurple"><ol><li><a href="/doc/live/reference/sage/algebras/steenrod_algebra_element.html"><tt>reference/sage/algebras/steenrod_algebra_element.html</tt></a>\n</ol></font></html>'
    """
    s = '<html>'
    s += '<font color="black">'
    s += '<h2>Search %s: %s</h2>'%(what, search)
    s += '</font>'
    s += '<font color="darkpurple">'
    s += '<ol>'

    files = set([])
    for L in r.splitlines():
        i = L.find(':')
        if i != -1:
            files.add(L[:i])
    files = list(files)
    files.sort()
    for F in files:
        if F.endswith('.html'):
            F = F.split('/', 2)[2]
            url = '/doc/live/' + F
        else:
            # source code
            url = '/src/' + F
        s += '<li><a href="%s"><tt>%s</tt></a>\n'%(url, F)
    s += '</ol>'
    s += '</font>'
    s += '</html>'
    return s



#######################################
## Add detex'ing of documentation
#######################################
import inspect
import sageinspect

def my_getdoc(obj):
    """
    Retrieve the documentation for ``obj``.

    INPUT: ``obj`` - a Sage object, function, etc.

    OUTPUT: its documentation (string)

    EXAMPLES::

        sage: from sage.misc.sagedoc import my_getdoc
        sage: s = my_getdoc(identity_matrix)
        sage: type(s)
        <type 'str'>
    """
    try:
        ds = obj._sage_doc_()
    except (AttributeError, TypeError):  # TypeError for interfaces
        try:
            ds = sageinspect.sage_getdoc(obj)
        except:
            return None
    if ds is None:
        return None
    return ds

def my_getsource(obj, is_binary):
    """
    Retrieve the source code for ``obj``.

    INPUT:

    - ``obj`` - a Sage object, function, etc.
    - ``is_binary`` - (boolean) ignored argument.

    OUTPUT: its documentation (string)

    EXAMPLES::

        sage: from sage.misc.sagedoc import my_getsource
        sage: s = my_getsource(identity_matrix, True)
        sage: s[:19]
        'def identity_matrix'
    """
    try:
        s = sageinspect.sage_getsource(obj, is_binary)
        return format_src(s)
    except Exception, msg:
        print 'Error getting source:', msg
        return None

class _sage_doc:
    """
    Open Sage documentation in a web browser, from either the
    command-line or the notebook.

    - Type "browse_sage_doc.DOCUMENT()" to open the named document --
      for example, "browse_sage_doc.tutorial()" opens the tutorial.
      Available documents are

      - tutorial: the Sage tutorial
      - reference: the Sage reference manual
      - constructions: "how do I construct ... in Sage?"
      - developer: the Sage developer's guide.

    - Type "browse_sage_doc(OBJECT, output=FORMAT, view=BOOL)" to view
      the documentation for OBJECT, as in
      "browse_sage_doc(identity_matrix, 'html').  ``output`` can be
      either 'html' or 'rst': the form of the output.  ``view`` is
      only relevant if ``output`` is ``html``; in this case, if
      ``view`` is True (its default value), then open up the
      documentation in a web browser.  Otherwise, just output the
      documentation as a string.

    EXAMPLES::

        sage: browse_sage_doc._open("reference", testing=True)[0]  # indirect doctest
        'http://localhost:8000/doc/live/reference/index.html'
        sage: browse_sage_doc(identity_matrix, 'rst')[-60:-5]
        'MatrixSpace of 3 by 3 sparse matrices over Integer Ring'
    """
    def __init__(self):
        self._base_url = "http://localhost:8000/doc/live/"
        self._base_path = os.path.join(SAGE_DOC, "output/html/en/")

    def __call__(self, obj, output='html', view=True):
        r"""
        Return the documentation for ``obj``.

        INPUT:

        - ``obj`` - a Sage object
        - ``output`` - either 'html' or 'rst': return documentation in this form
        - ``view`` - only has an effect if output is 'html': in this
          case, if ``view`` is ``True``, display the documentation in
          a web browser.  Otherwise, return the documentation as a
          string.

        EXAMPLES::

            sage: browse_sage_doc(identity_matrix, 'rst')
            "...**File:**...**Type:**...**Definition:** identity_matrix..."
            sage: identity_matrix.__doc__.replace('\\','\\\\') in browse_sage_doc(identity_matrix, 'rst')
            True
            sage: browse_sage_doc(identity_matrix, 'html', False)
            '...div...File:...Type:...Definition:...identity_matrix...'
        """
        if output != 'html' and view:
            view = False
        # much of the following is taken from 'docstring' in server/support.py
        s  = ''
        newline = "\n\n"  # blank line to start new paragraph

        try:
            filename = sageinspect.sage_getfile(obj)
            s += '**File:** %s' % filename
            s += newline
        except TypeError:
            pass

        obj_name = ''
        locs = sys._getframe(1).f_locals
        for var in locs:
            if id(locs[var]) == id(obj):
                obj_name = var

        s += '**Type:** %s' % type(obj)
        s += newline
        s += '**Definition:** %s' % sageinspect.sage_getdef(obj, obj_name)
        s += newline
        s += '**Docstring:**'
        s += newline
        s += sageinspect.sage_getdoc(obj, obj_name, embedded_override=True)

        # now s should be the reST version of the docstring
        if output == 'html':
            html = sphinxify(s)
            if view:
                path = os.path.join(tmp_dir(), "temp.html")
                filed = open(path, 'w')

                static_path = os.path.join(SAGE_DOC, 'output/html/en/_static')
                if os.path.exists(static_path):
                    title = obj_name + ' - Sage ' + sage.version.version + ' Documentation'
                    template = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>%(title)s</title>
    <link rel="stylesheet" href="%(static_path)s/default.css" type="text/css" />
    <link rel="stylesheet" href="%(static_path)s/pygments.css" type="text/css" />
    <style type="text/css">
      <!--
        div.body {
          margin: 1.0em;
          padding: 1.0em;
        }
        div.bodywrapper {
          margin: 0;
        }
      -->
    </style>
    <script type="text/javascript">
      var DOCUMENTATION_OPTIONS = {
        URL_ROOT:    '',
        VERSION:     '%(version)s',
        COLLAPSE_MODINDEX: false,
        FILE_SUFFIX: '.html',
        HAS_SOURCE:  false
      };
    </script>
    <script type="text/javascript" src="%(static_path)s/jquery.js"></script>
    <script type="text/javascript" src="%(static_path)s/doctools.js"></script>
    <script type="text/javascript" src="%(static_path)s/jsmath_sage.js"></script>
    <link rel="shortcut icon" href="%(static_path)s/favicon.ico" />
    <link rel="icon" href="%(static_path)s/sageicon.png" type="image/x-icon" />
  </head>
  <body>
    <div class="document">
      <div class="documentwrapper">
        <div class="bodywrapper">
          <div class="body">
            %(html)s
          </div>
        </div>
      </div>
    </div>
  </body>
</html>"""
                    html = template % { 'html': html,
                                        'static_path': static_path,
                                        'title': title,
                                        'version': sage.version.version }

                filed.write(html)
                filed.close()
                os.system(browser() + " " + path)
            else:
                return html
        elif output == 'rst':
            return s
        else:
            raise ValueError, "output type %s not recognized" % output

    def _open(self, name, testing=False):
        """
        Open the document ``name`` in a web browser.  This constructs
        the appropriate URL and/or path name and passes it to the web
        browser.

        INPUT:

        - ``name`` - string, name of the documentation

        - ``testing`` - boolean (optional, default False): if True,
          then just return the URL and path-name for this document;
          don't open the web browser.

        EXAMPLES::

            sage: browse_sage_doc._open("reference", testing=True)[0]
            'http://localhost:8000/doc/live/reference/index.html'
            sage: browse_sage_doc._open("tutorial", testing=True)[1]
            '...doc/output/html/en/tutorial/index.html'
        """
        url = self._base_url + os.path.join(name, "index.html")
        path = os.path.join(self._base_path, name, "index.html")
        if testing:
            return (url, path)

        if not os.path.exists(path):
            raise OSError, """The document '%s' does not exist.  Please build it
with 'sage -docbuild %s html --jsmath' and try again.""" %(name, name)

        from sage.server.support import EMBEDDED_MODE
        if EMBEDDED_MODE:
            os.system(browser() + " " + url)
        else:
            os.system(browser() + " " + path)

    def tutorial(self):
        """
        The Sage tutorial.  To get started with Sage, start here.
        """
        self._open("tutorial")

    def reference(self):
        """
        The Sage reference manual.
        """
        self._open("reference")

    manual = reference

    def developer(self):
        """
        The Sage developer's guide.  Learn to develop programs for Sage.
        """
        self._open("developer")

    def constructions(self):
        """
        Sage constructions.  Attempts to answer the question "How do I
        construct ... in Sage?"
        """
        self._open("constructions")

browse_sage_doc = _sage_doc()
tutorial = browse_sage_doc.tutorial
reference = browse_sage_doc.reference
manual = browse_sage_doc.reference
developer = browse_sage_doc.developer
constructions = browse_sage_doc.constructions

python_help = pydoc.help

def help(module=None):
    """
    If there is an argument ``module``, print the Python help message
    for ``module``.  With no argument, print a help message about
    getting help in Sage.

    EXAMPLES::

        sage: help()
        Welcome to Sage ...
    """
    if module:
        python_help(module)
    else:
        print """Welcome to Sage %s!  To view the Sage tutorial in your web browser,
type 'tutorial()', and to view the (very detailed) Sage reference
manual, type 'manual()'.  For help on any Sage function, for example
'matrix_plot', type 'matrix_plot?' to see a help message, type
'help(matrix_plot)' to see a very similar message, type
'browse_sage_doc(matrix_plot)' to view a message in a web browser, and
type 'matrix_plot??' to look at the function's source code.

To enter Python's interactive online help utility, type 'python_help()'.
To get help on a Python function, module or package, type 'help(MODULE)' or
'python_help(MODULE)'.""" % sage.version.version
