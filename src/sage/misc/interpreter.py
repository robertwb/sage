"""
Preparses input from the interpreter

Modified input.

  -- All ^'s (not in strings) are replaced by **'s.

  -- If M is a variable and i an integer,
     then M.i is replaced by M.gen(i), so generators can be
     accessed as in MAGMA.

  -- quit alone on a line quits.

  -- load to load in scripts

  -- Most int literals n are replaced by ZZ(n) Thus 2/3 is a rational
     number.  If they are in []'s right after a valid identifier they
     aren't replaced.

  -- real literals get wrapped in "RR" (with a precision)

  -- the R.<x,y,z> = ... notation

TODO:
  I have no plans for anything further, except to improve the
  robustness of the above.  Preparsing may work incorrectly for
  multi-line input lines in some cases; this will be fixed.

All other input is processed normally.

It automatically converts *most* integer literals to Sage Integer's and
decimal literals to Sage Reals.  It does not convert indexes into
1-d arrays, since those have to be ints.

I also extended the load command so it *really* works exactly
like the Sage interpreter, so e.g., ^ for exponentiation is
allowed.  Also files being loaded can themselves load other files.
Finally, I added an "attach" command, e.g.,
    attach 'file'
that works kind of like attach in MAGMA.  Whenever you enter a blank
line in the Sage interpreter, *all* attached files that have changed
are automatically reloaded.  Moreover, the attached files work according
to the Sage interpreter rules, i.e., ^ --> **, etc.

I also fixed it so ^ is not replaced by ** inside strings.

Finally, I added back the M.n notation for the n-th generator
of object M, again like in MAGMA.

EXAMPLE:
    sage: 2/3
    2/3
    sage: type(2/3)
    <type 'sage.rings.rational.Rational'>
    sage: a = 49928420832092
    sage: type(a)
    <type 'sage.rings.integer.Integer'>
    sage: a.factor()
    2^2 * 11 * 1134736837093
    sage: v = [1,2,3]
    sage: type(v[0])
    <type 'sage.rings.integer.Integer'>

If we don't make potential list indices int's, then lots of stuff
breaks, or users have to type v[int(7)], which is insane.
A fix would be to only not make what's in the brackets an
Integer if what's before the bracket is a valid identifier,
so the w = [5] above would work right.

    sage: s = "x^3 + x + 1"
    sage: s
    'x^3 + x + 1'
    sage: pari(s)
    x^3 + x + 1
    sage: f = pari(s)
    sage: f^2
    x^6 + 2*x^4 + 2*x^3 + x^2 + 2*x + 1
    sage: V = VectorSpace(QQ,3)
    sage: V.0
    (1, 0, 0)
    sage: V.1
    (0, 1, 0)
    sage: s = "This. Is. It."
    sage: print s
    This. Is. It.
"""

#*****************************************************************************
#       Copyright (C) 2004 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
import IPython.ipapi
_ip = IPython.ipapi.get()

__author__ = 'William Stein <wstein@gmail.com> et al.'
__license__ = 'GPL'

import os
import log
import re

import remote_file

from IPython.iplib import InteractiveShell

import preparser_ipython
from preparser import preparse_file, load_wrap, modified_attached_files, attached_files

import cython

# IPython has a prefilter() function that analyzes each input line. We redefine
# it here to first pre-process certain forms of input

# The prototype of any alternate prefilter must be like this one (the name
# doesn't matter):
# - line is a string containing the user input line.
# - continuation is a parameter which tells us if we are processing a first line of
#   user input or the second or higher of a multi-line statement.



def load_startup_file(file):
    if os.path.exists(file):
        X = do_prefilter_paste('load "%s"'%file,False)
        _ip.runlines(X)
    if os.path.exists('attach.sage'):
        X = do_prefilter_paste('attach "attach.sage"',False)
        _ip.runlines(X)


def do_prefilter_paste(line, continuation):
    """
    Alternate prefilter for input.

    INPUT:

        - ``line`` -- a single line; must *not* have any newlines in it
        - ``continuation`` -- whether the input line is really part
          of the previous line, because of open parens or backslash.
    """
    if '\n' in line:
        raise RuntimeError, "bug in function that calls do_prefilter_paste -- there can be no newlines in the input"

    # This is so it's OK to have lots of blank space at the
    # beginning of any non-continuation line.

    if continuation:
        # strip ...'s that appear in examples
        L = line.lstrip()
        if L[:3] == '...':
            line = L[3:]
    else:
        line = line.lstrip()

    line = line.rstrip()

    # Process attached files.
    for F in modified_attached_files():
        # We attach the files again instead of loading them,
        # to preserve tracebacks or efficiency according
        # to the settings of load_attach_mode().
        _ip.runlines(load_wrap(F, attach=True))

    # Get rid of leading sage: prompts so that pasting of examples
    # from the documentation works.  This is like MAGMA's
    # SetLinePrompt(false).
    for prompt in ['sage:', '>>>']:
        if not continuation:
            while True:
                strip = False
                if line[:3] == prompt:
                    line = line[3:].lstrip()
                    strip = True
                elif line[:5] == prompt:
                    line = line[5:].lstrip()
                    strip = True
                if not strip:
                    break
                else:
                    line = line.lstrip()

    # 'quit' alone on a line to quit.
    if line.lower() in ['quit', 'exit', 'quit;', 'exit;']:
        line = '%quit'

    # An interactive load command, like iload in MAGMA.
    if line[:6] == 'iload ':
        try:
            name = str(eval(line[6:]))
        except:
            name = str(line[6:].strip())
        try:
            F = open(name)
        except IOError:
            raise ImportError, 'Could not open file "%s"'%name

        print 'Interactively loading "%s"'%name
        n = len(__IPYTHON__.input_hist)
        for L in F.readlines():
            L = L.rstrip()
            Llstrip = L.lstrip()
            raw_input('sage: %s'%L.rstrip())
            __IPYTHON__.input_hist_raw.append(L)
            if Llstrip[:5] == 'load ' or Llstrip[:7] == 'attach ' \
                   or Llstrip[:6] == 'iload ':
                log.offset -= 1
                L = do_prefilter_paste(L, False)
                if len(L.strip()) > 0:
                    _ip.runlines(L)
                L = ''
            else:
                L = preparser_ipython.preparse_ipython(L, not continuation)
            __IPYTHON__.input_hist.append(L)
            __IPYTHON__.push(L)
        log.offset += 1
        return ''


    #################################################################
    # load and attach commands
    #################################################################
    for cmd in ['load', 'attach']:
        if line.lstrip().startswith(cmd+' '):
            j = line.find(cmd+' ')
            s = line[j+len(cmd)+1:].strip()
            if not s.startswith('('):
                line = ' '*j + load_wrap(s, cmd=='attach')

    if len(line) > 0:
        line = preparser_ipython.preparse_ipython(line, not continuation)

    return line

def load_cython(name):
    cur = os.path.abspath(os.curdir)
    try:
        mod, dir  = cython.cython(name, compile_message=True, use_cache=True)
    except (IOError, OSError, RuntimeError), msg:
        print "Error compiling cython file:\n%s"%msg
        return ''
    import sys
    sys.path.append(dir)
    return 'from %s import *'%mod

def handle_encoding_declaration(contents, out):
    """Find a PEP 263-style Python encoding declaration in the first or
    second line of `contents`. If found, output it to `out` and return
    `contents` without the encoding line; otherwise output a default
    UTF-8 declaration and return `contents`.

    EXAMPLES::

        sage: from sage.misc.interpreter import handle_encoding_declaration
        sage: import sys
        sage: c1='# -*- coding: latin-1 -*-\nimport os, sys\n...'
        sage: c2='# -*- coding: iso-8859-15 -*-\nimport os, sys\n...'
        sage: c3='# -*- coding: ascii -*-\nimport os, sys\n...'
        sage: c4='import os, sys\n...'
        sage: handle_encoding_declaration(c1, sys.stdout)
        # -*- coding: latin-1 -*-
        'import os, sys\n...'
        sage: handle_encoding_declaration(c2, sys.stdout)
        # -*- coding: iso-8859-15 -*-
        'import os, sys\n...'
        sage: handle_encoding_declaration(c3, sys.stdout)
        # -*- coding: ascii -*-
        'import os, sys\n...'
        sage: handle_encoding_declaration(c4, sys.stdout)
        # -*- coding: utf-8 -*-
        'import os, sys\n...'

    TESTS::

    These are some of the tests listed in PEP 263.

        sage: contents = '#!/usr/bin/python\n# -*- coding: latin-1 -*-\nimport os, sys'
        sage: handle_encoding_declaration(contents, sys.stdout)
        # -*- coding: latin-1 -*-
        '#!/usr/bin/python\nimport os, sys'

        sage: contents = '# This Python file uses the following encoding: utf-8\nimport os, sys'
        sage: handle_encoding_declaration(contents, sys.stdout)
        # This Python file uses the following encoding: utf-8
        'import os, sys'

        sage: contents = '#!/usr/local/bin/python\n# coding: latin-1\nimport os, sys'
        sage: handle_encoding_declaration(contents, sys.stdout)
        # coding: latin-1
        '#!/usr/local/bin/python\nimport os, sys'

    Two hash marks are okay; this shows up in SageTeX-generated scripts::

        sage: contents = '## -*- coding: utf-8 -*-\nimport os, sys\nprint x'
        sage: handle_encoding_declaration(contents, sys.stdout)
        ## -*- coding: utf-8 -*-
        'import os, sys\nprint x'

    When the encoding declaration doesn't match the specification, we
    spit out a default UTF-8 encoding.

    Incorrect coding line::

        sage: contents = '#!/usr/local/bin/python\n# latin-1\nimport os, sys'
        sage: handle_encoding_declaration(contents, sys.stdout)
        # -*- coding: utf-8 -*-
        '#!/usr/local/bin/python\n# latin-1\nimport os, sys'

    Encoding declaration not on first or second line::

        sage: contents ='#!/usr/local/bin/python\n#\n# -*- coding: latin-1 -*-\nimport os, sys'
        sage: handle_encoding_declaration(contents, sys.stdout)
        # -*- coding: utf-8 -*-
        '#!/usr/local/bin/python\n#\n# -*- coding: latin-1 -*-\nimport os, sys'

    We don't check for legal encoding names; that's Python's job::

        sage: contents ='#!/usr/local/bin/python\n# -*- coding: utf-42 -*-\nimport os, sys'
        sage: handle_encoding_declaration(contents, sys.stdout)
        # -*- coding: utf-42 -*-
        '#!/usr/local/bin/python\nimport os, sys'


    NOTES::

        PEP 263: http://www.python.org/dev/peps/pep-0263/

        PEP 263 says that Python will interpret a UTF-8 byte order mark
        as a declaration of UTF-8 encoding, but I don't think we do
        that; this function only sees a Python string so it can't
        account for a BOM.

        We default to UTF-8 encoding even though PEP 263 says that
        Python files should default to ASCII.

        Also see http://docs.python.org/ref/encodings.html.

    AUTHORS::

        - Lars Fischer
        - Dan Drake (2010-12-08, rewrite for ticket #10440)
    """
    lines = contents.splitlines()
    for num, line in enumerate(lines[:2]):
        if re.search(r"coding[:=]\s*([-\w.]+)", line):
            out.write(line + '\n')
            return '\n'.join(lines[:num] + lines[(num+1):])

    # If we didn't find any encoding hints, use utf-8. This is not in
    # conformance with PEP 263, which says that Python files default to
    # ascii encoding.
    out.write("# -*- coding: utf-8 -*-\n")
    return contents

def preparse_file_named_to_stream(name, out):
    r"""
    Preparse file named \code{name} (presumably a .sage file), outputting to
    stream \code{out}.
    """
    name = os.path.abspath(name)
    dir, _ = os.path.split(name)
    cur = os.path.abspath(os.curdir)
    os.chdir(dir)
    contents = open(name).read()
    contents = handle_encoding_declaration(contents, out)
    parsed = preparse_file(contents)
    os.chdir(cur)
    out.write("# -*- encoding: utf-8 -*-\n")
    out.write('#'*70+'\n')
    out.write('# This file was *autogenerated* from the file %s.\n' % name)
    out.write('#'*70+'\n')
    out.write(parsed)

def preparse_file_named(name):
    r"""
    Preparse file named \code{name} (presumably a .sage file), outputting to a
    temporary file.  Returns name of temporary file.
    """
    import sage.misc.misc
    name = os.path.abspath(name)
    tmpfilename = os.path.abspath(sage.misc.misc.tmp_filename(name) + ".py")
    out = open(tmpfilename,'w')
    preparse_file_named_to_stream(name, out)
    out.close()
    return tmpfilename

def sage_prefilter(self, block, continuation):
    """
    Sage's prefilter for input.  Given a string block (usually a
    line), return the preparsed version of it.

    INPUT:
        block -- string (usually a single line, but not always)
        continuation -- whether or not this line is a continuation.
    """
    try:
        block2 = ''
        first = True
        B = block.split('\n')
        for i in range(len(B)):
            L = B[i]
            M = do_prefilter_paste(L, continuation or (not first))
            first = False
            # The L[:len(L)-len(L.lstrip())]  business here preserves
            # the whitespace at the beginning of L.
            if block2 != '':
                block2 += '\n'
            lstrip = L.lstrip()
            if lstrip[:5] == 'sage:' or lstrip[:3] == '>>>' or i==0:
                block2 += M
            else:
                block2 += L[:len(L)-len(lstrip)] + M

    except None:

        print "WARNING: An error occurred in the Sage parser while"
        print "parsing the following block:"
        print block
        print "Please report this as a bug (include the output of typing '%hist')."
        block2 = block

    return InteractiveShell._prefilter(self, block2, continuation)


import sage.server.support
def embedded():
    return sage.server.support.EMBEDDED_MODE

ipython_prefilter = InteractiveShell.prefilter
do_preparse=True
def preparser(on=True):
    """
    Turn on or off the Sage preparser.

    INPUT:
        - ``on`` -- bool (default: True) if True turn on preparsing; if False, turn it off.

    EXAMPLES:
        sage: 2/3
        2/3
        sage: preparser(False)
        sage: 2/3  # not tested since doctests are always preparsed
        0
        sage: preparser(True)
        sage: 2^3
        8
    """
    global do_preparse
    if on:
        do_preparse = True
        InteractiveShell.prefilter = sage_prefilter
    else:
        do_preparse = False
        InteractiveShell.prefilter = ipython_prefilter


import sagedoc
import sageinspect
import IPython.OInspect
IPython.OInspect.getdoc = sagedoc.my_getdoc
IPython.OInspect.getsource = sagedoc.my_getsource
IPython.OInspect.getargspec = sageinspect.sage_getargspec

#We monkey-patch IPython to disable the showing of plots
#when doing introspection on them. This fixes Trac #2163.
old_pinfo = IPython.OInspect.Inspector.pinfo
def sage_pinfo(self, *args, **kwds):
    """
    A wrapper around IPython.OInspect.Inspector.pinfo which turns
    off show_default before it is called and then sets it back
    to its previous value.

    Since this requires an IPython shell to test and the doctests aren't,
    run under IPython, we cannot add doctests for this function.
    """
    from sage.plot.all import show_default
    old_value = show_default()
    show_default(False)

    result = old_pinfo(self, *args, **kwds)

    show_default(old_value)
    return result
IPython.OInspect.Inspector.pinfo = sage_pinfo

import __builtin__
_prompt = 'sage'

def set_sage_prompt(s):
    global _prompt
    _prompt = str(s)

def sage_prompt():
    log.update()
    return '%s'%_prompt

__builtin__.sage_prompt = sage_prompt



#######################################
#
def load_a_file(argstr, globals):
    s = open(argstr).read()
    return preparse_file(s, globals=globals)
