r"""
This file contains some tests that Sage command line options actually
do something.

We test the following command line options:

test.py
/path/to/test.py
test.sage
/path/to/test.sage
test.spyx
/path/to/test.spyx
--advanced
--branch
-c
--cython
--ecl
--experimental
--gap
--gp
-h
--help
--hg
--info
--ipython
--kash
--lisp
--maxima
--min
--mwrank
--optional
--preparse
--python
-q
--R
--root
--scons
--sh
--singular
--sqlite3
--standard
--startuptime
-t
-v
--zzfoobar (illegal option)


AUTHORS:

- Jeroen Demeyer (2010-11-20): initial version (#10300)

"""

from subprocess import *
import os, select


def test_executable(args, input="", timeout=50.0, cwd=None):
    """
    Run the program defined by ``args`` using the string ``input`` on
    the standard input.

    INPUT:

    - ``args`` -- a list of program arguments, the first being the
      executable.

    - ``input`` -- a string serving as standard input.  Usually, this
      should end with a newline.

    - ``timeout`` -- if the program produces no output for ``timeout``
      seconds, a RuntimeError is raised.

    - ``cwd`` -- (default: ``None``) if not None, run the program from
      the given directory.

    OUTPUT: a tuple ``(out, err, ret)`` with the standard output,
    standard error and exitcode of the program run.


    EXAMPLES::

        sage: from sage.tests.cmdline import test_executable
        sage: (out, err, ret) = test_executable(["cat"], "Hello World!")
        sage: out
        'Hello World!'
        sage: err
        ''
        sage: ret
        0

    We test the timeout option::

        sage: (out, err, ret) = test_executable(["sleep", "1"], timeout=0.1)
        Traceback (most recent call last):
        ...
        RuntimeError: timeout in test_executable()

    TESTS:

    Run Sage itself with various options::

        sage: (out, err, ret) = test_executable(["sage"])
        sage: out.find(version()) >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage"], "3^33\n")
        sage: out.find(version()) >= 0
        True
        sage: out.find("5559060566555523") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "-q"], "3^33\n")
        sage: out.find(version()) >= 0
        False
        sage: out.find("5559060566555523") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "-c", "print 3^33"])
        sage: print out
        5559060566555523
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--min", "-c", "print 3^33"])
        sage: print out
        5559060566555523
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--startuptime"])
        sage: out.find("Slowest module import") >= 0
        True
        sage: err
        ''
        sage: ret
        0

    Test help::

        sage: (out, err, ret) = test_executable(["sage", "-h"])
        sage: out.find("Optional arguments:") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--help"])
        sage: out.find("Optional arguments:") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--advanced"])
        sage: out.find("run with no output prompts") >= 0
        True
        sage: err
        ''
        sage: ret
        0

    Basic information about the Sage installation::

        sage: (out, err, ret) = test_executable(["sage", "-v"])
        sage: out.find(version()) >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--branch"])
        sage: len(out) >= 2   # at least one character + newline
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--root"])
        sage: len(out) >= 2   # at least one character + newline
        True
        sage: err
        ''
        sage: ret
        0

    Test ``sage --info [packages]``, unless this is a binary (bdist)
    distribution which doesn't ship spkgs::

        sage: if os.path.isfile(os.path.join(SAGE_ROOT, 'spkg', 'standard', '.from_bdist')):
        ...     out = "Found package sqlalchemy in spkg/standard/sqlalchemy-...spkg\n= SQLAlchemy =\n...\nSQLAlchemy is the Python SQL toolkit..."
        ...     err = ''
        ...     ret = 0
        ... else:
        ...     (out, err, ret) = test_executable(["sage", "--info", "sqlalchemy"])
        ...
        sage: print out
        Found package sqlalchemy in spkg/standard/sqlalchemy-...spkg
        = SQLAlchemy =
        ...
        SQLAlchemy is the Python SQL toolkit...
        sage: err
        ''
        sage: ret
        0

    Test ``sage-run`` on a Python file, both with an absolute and with a relative path::

        sage: dir = tmp_dir(); name = 'python_test_file.py'
        sage: fullname = os.path.join(dir, name)
        sage: F = open(fullname, 'w')
        sage: F.write("print 3^33\n")
        sage: F.close()
        sage: (out, err, ret) = test_executable(["sage", fullname])
        sage: print out
        34
        sage: err
        ''
        sage: ret
        0
        sage: (out, err, ret) = test_executable(["sage", name], cwd=dir)
        sage: print out
        34
        sage: err
        ''
        sage: ret
        0

    The same as above, but now with a ``.sage`` file.  This indirectly
    also tests the preparser::

        sage: dir = tmp_dir(); name = 'sage_test_file.sage'
        sage: fullname = os.path.join(dir, name)
        sage: F = open(fullname, 'w')
        sage: F.write("k.<a> = GF(5^3); print a^124\n")
        sage: F.close()
        sage: (out, err, ret) = test_executable(["sage", fullname])
        sage: print out
        1
        sage: err
        ''
        sage: ret
        0
        sage: (out, err, ret) = test_executable(["sage", name], cwd=dir)
        sage: print out
        1
        sage: err
        ''
        sage: ret
        0

    Test running a ``.spyx`` file::

        sage: dir = tmp_dir(); name = 'sage_test_file.spyx'
        sage: fullname = os.path.join(dir, name)
        sage: F = open(fullname, 'w')
        sage: F.write("cdef long i, s = 0\nfor i in range(1000): s += i\nprint s")
        sage: F.close()
        sage: (out, err, ret) = test_executable(["sage", fullname])
        sage: print out
        499500
        sage: err
        'Compiling ...spyx...'
        sage: ret
        0
        sage: (out, err, ret) = test_executable(["sage", name], cwd=dir)
        sage: print out
        499500
        sage: err
        'Compiling ...spyx...'
        sage: ret
        0

    Testing ``sage --preparse FILE`` and ``sage -t FILE``.  First create
    a file and preparse it::

        sage: s = '\"\"\"\nThis is a test file.\n\"\"\"\ndef my_add(a,b):\n    \"\"\"\n    Add a to b.\n\n        EXAMPLES::\n\n            sage: my_add(2,2)\n            4\n        \"\"\"\n    return a+b\n'
        sage: script = os.path.join(tmp_dir(), 'my_script.sage')
        sage: script_py = script[:-5] + '.py'
        sage: F = open(script, 'w')
        sage: F.write(s)
        sage: F.close()
        sage: (out, err, ret) = test_executable(["sage", "--preparse", script])
        sage: ret
        0
        sage: os.path.isfile(script_py)
        True

    Now test my_script.sage and the preparsed version my_script.py::

        sage: (out, err, ret) = test_executable(["sage", "-t", script])
        sage: ret
        0
        sage: out.find("All tests passed!") >= 0
        True
        sage: (out, err, ret) = test_executable(["sage", "-t", script_py])
        sage: ret
        0
        sage: out.find("All tests passed!") >= 0
        True

    Now for a file which should fail tests.  Run this test with
    SAGE_TESTDIR equal to a temporary directory, because failed doctests
    leave files lying around in SAGE_TESTDIR::

        sage: s = s.replace('4', '5') # (2+2 != 5)
        sage: F = open(script, 'w')
        sage: F.write(s)
        sage: F.close()
        sage: OLD_TESTDIR = os.environ['SAGE_TESTDIR']
        sage: os.environ['SAGE_TESTDIR'] = tmp_dir()
        sage: (out, err, ret) = test_executable(["sage", "-t", script])
        sage: ret
        128
        sage: out.find("1 items had failures:") >= 0
        True
        sage: os.environ['SAGE_TESTDIR'] = OLD_TESTDIR  # just in case

    Check that Sage refuses to run doctests from a directory whose
    permissions are too loose.  We create a world-writable directory
    inside a safe temporary directory to test this::

        sage: d = os.path.join(tmp_dir(), "test")
        sage: os.mkdir(d)
        sage: os.chmod(d, 0o777)
        sage: (out, err, ret) = test_executable(["sage", "-t", "nonexisting.py"], cwd=d)
        sage: print err
        Traceback (most recent call last):
        ...
        RuntimeError: refusing to run doctests...
        sage: (out, err, ret) = test_executable(["sage", "-tp", "1", "nonexisting.py"], cwd=d)
        sage: print err
        Traceback (most recent call last):
        ...
        RuntimeError: refusing to run doctests...

    Test external programs being called by Sage::

        sage: (out, err, ret) = test_executable(["sage", "--sh"], "echo Hello World\nexit 42\n")
        sage: out.find("Hello World\n") >= 0
        True
        sage: ret
        42

        sage: (out, err, ret) = test_executable(["sage", "--sh", "-c", "echo Hello World; exit 42"])
        sage: out.find("Hello World\n") >= 0
        True
        sage: ret
        42

        sage: (out, err, ret) = test_executable(["sage", "--ipython"], "\n3**33\n")
        sage: out.find("5559060566555523") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--python"], "print 3^33\n")
        sage: out
        '34\n'
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--cython"])
        sage: print err
        Cython (http://cython.org) is a compiler for code written in the
        Cython language.  Cython is based on Pyrex by Greg Ewing.
        ...

        sage: (out, err, ret) = test_executable(["sage", "--ecl"], "(* 12345 54321)\n")
        sage: out.find("Embeddable Common-Lisp") >= 0
        True
        sage: out.find("670592745") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--lisp"], "(* 12345 54321)\n")
        sage: out.find("Embeddable Common-Lisp") >= 0
        True
        sage: out.find("670592745") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--gap", "-q"], "Size(SymmetricGroup(5));\n")
        sage: out
        '120\n'
        sage: err.replace('gap: halving pool size.', '').strip()
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--kash", "-b", "3^33;\n"])  # optional - kash
        sage: out.find("5559060566555523") >= 0  # optional - kash
        True
        sage: err  # optional - kash
        ''
        sage: ret  # optional - kash
        0

        sage: (out, err, ret) = test_executable(["sage", "--mwrank", "-v0", "-q", "-o"], "0 0 1 -7 6 0 0 0 0 0\n")
        sage: out
        'Curve [0,0,1,-7,6] :\tRank = 3\n[[3],[[1,-1],[-2,3],[-7/4,25/8]]]\n\n\n'
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--singular"], "12345*54321;\n")
        sage: out.find("A Computer Algebra System for Polynomial Computations") >= 0
        True
        sage: out.find("670592745") >= 0
        True
        sage: err
        ''
        sage: ret
        0

    Check that ``sage-location`` did its job in making Python scripts
    relative.  We test it on the ``ipython`` script::

        sage: open(os.path.join(SAGE_ROOT, "local", "bin", "ipython")).readline()
        '#!/usr/bin/env python\n'

    Test GP using the ``-f`` option which prevents the reading of a ``.gprc``
    configuration file::

        sage: (out, err, ret) = test_executable(["sage", "--gp", "-f"], "3^33\nquit(42)\n")
        sage: out.find("PARI/GP") >= 0
        True
        sage: out.find("5559060566555523") >= 0
        True
        sage: err
        ''
        sage: ret
        42

    Some programs of which we check functionality using only ``--version``::

        sage: (out, err, ret) = test_executable(["sage", "--hg", "--version"])
        sage: out.find("Mercurial Distributed SCM") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--maxima", "--version"])
        sage: out.find("Maxima ") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--R", "--version"])
        sage: out.find("R version ") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--scons", "--version"])
        sage: out.find("SCons") >= 0
        True
        sage: err
        ''
        sage: ret
        0

        sage: (out, err, ret) = test_executable(["sage", "--sqlite3", "--version"])
        sage: out.startswith("3.")
        True
        sage: err
        ''
        sage: ret
        0

    Check some things requiring an internet connection::

        sage: (out, err, ret) = test_executable(["sage", "--standard"])  # optional - internet
        sage: out.find("atlas") >= 0  # optional - internet
        True
        sage: err  # optional - internet
        ''
        sage: ret  # optional - internet
        0

        sage: (out, err, ret) = test_executable(["sage", "--optional"])  # optional - internet
        sage: out.find("database_cremona_ellcurve") >= 0  # optional - internet
        True
        sage: err  # optional - internet
        ''
        sage: ret  # optional - internet
        0

        sage: (out, err, ret) = test_executable(["sage", "--experimental"])  # optional - internet
        sage: out.find("macaulay2") >= 0  # optional - internet
        True
        sage: err  # optional - internet
        ''
        sage: ret  # optional - internet
        0

    Check an illegal command line option.  This outputs an error to stdout,
    but we allow stderr in case this changes in the future::

        sage: (out, err, ret) = test_executable(["sage", "--zzfoobar"])
        sage: (out+err).find("unknown option: --zzfoobar") >= 0
        True
        sage: ret > 0
        True

    """
    pexpect_env = dict(os.environ)
    try:
        del pexpect_env["TERM"]
    except KeyError:
        pass
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd, env=pexpect_env)
    if input:
        p.stdin.write(input)
    p.stdin.close()
    fdout = p.stdout.fileno()
    fderr = p.stderr.fileno()
    out = ""; err = ""

    while True:
        # Try reading from fdout and fderr
        rfd = []
        if fdout: rfd.append(fdout)
        if fderr: rfd.append(fderr)
        if len(rfd) == 0: break
        rlist = select.select(rfd, [], [], timeout)[0]

        if len(rlist) == 0:
            # Timeout!
            p.terminate()
            raise RuntimeError("timeout in test_executable()")
        if fdout in rlist:
            s = os.read(fdout, 1024)
            if s == "": fdout = None   # EOF
            out += s
        if fderr in rlist:
            s = os.read(fderr, 1024)
            if s == "": fderr = None   # EOF
            err += s

    return (out, err, p.wait())
