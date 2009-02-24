r"""
Interface to Maple

AUTHORS:

- William Stein (2005): maple interface

- Gregg Musiker (2006-02-02): tutorial

- William Stein (2006-03-05): added tab completion, e.g., maple.[tab],
  and help, e.g, maple.sin?.

You must have the optional commercial Maple interpreter installed
and available as the command ``maple`` in your PATH in
order to use this interface. You do not have to install any
optional Sage packages.

Type ``maple.[tab]`` for a list of all the functions
available from your Maple install. Type
``maple.[tab]?`` for Maple's help about a given
function. Type ``maple(...)`` to create a new Maple
object, and ``maple.eval(...)`` to run a string using
Maple (and get the result back as a string).

EXAMPLES::

    sage: maple('3 * 5')                                 # optional - maple
    15
    sage: maple.eval('ifactor(2005)')                    # optional - maple
    '"(5)*"(401)'
    sage: maple.ifactor(2005)                            # optional - maple
    "(5)*"(401)
    sage: maple.fsolve('x^2=cos(x)+4', 'x=0..5')         # optional - maple
    1.914020619
    sage: maple.factor('x^5 - y^5')                      # optional - maple
    (x-y)*(x^4+x^3*y+x^2*y^2+x*y^3+y^4)

If the string "error" (case insensitive) occurs in the output of
anything from Maple, a RuntimeError exception is raised.

Tutorial
--------

AUTHORS:

- Gregg Musiker (2006-02-02): initial version.

This tutorial is based on the Maple Tutorial for number theory from
http://www.math.mun.ca/~drideout/m3370/numtheory.html.

There are several ways to use the Maple Interface in Sage. We will
discuss two of those ways in this tutorial.


#. If you have a maple expression such as

   ::

       factor( (x^5-1));

   We can write that in sage as

   ::

       sage: maple('factor(x^5-1)')                 # optional - maple
       (x-1)*(x^4+x^3+x^2+x+1)

   Notice, there is no need to use a semicolon.

#. Since Sage is written in Python, we can also import maple
   commands and write our scripts in a pythonic way. For example,
   ``factor()`` is a maple command, so we can also factor
   in Sage using

   ::

       sage: maple('(x^5-1)').factor()              # optional - maple
       (x-1)*(x^4+x^3+x^2+x+1)

   where ``expression.command()`` means the same thing as
   ``command(expression)`` in Maple. We will use this
   second type of syntax whenever possible, resorting to the first
   when needed.

   ::

       sage: maple('(x^12-1)/(x-1)').simplify()     # optional - maple
       x^11+x^10+x^9+x^8+x^7+x^6+x^5+x^4+x^3+x^2+x+1


The normal command will always reduce a rational function to the
lowest terms. The factor command will factor a polynomial with
rational coefficients into irreducible factors over the ring of
integers. So for example,

::

    sage: maple('(x^12-1)').factor( )           # optional - maple
    (x-1)*(x+1)*(x^2+x+1)*(x^2-x+1)*(x^2+1)*(x^4-x^2+1)

::

    sage: maple('(x^28-1)').factor( )           # optional - maple
    (x-1)*(x^6+x^5+x^4+x^3+x^2+x+1)*(x+1)*(1-x+x^2-x^3+x^4-x^5+x^6)*(x^2+1)*(x^12-x^10+x^8-x^6+x^4-x^2+1)

Another important feature of maple is its online help. We can
access this through sage as well. After reading the description of
the command, you can press q to immediately get back to your
original prompt.

Incidentally you can always get into a maple console by the
command

::

    sage: maple.console()          # not tested
    sage: !maple                   # not tested

Note that the above two commands are slightly different, and the
first is preferred.

For example, for help on the maple command fibonacci, we type

::

    sage: maple.help('fibonacci')  # not tested, since it uses a pager

We see there are two choices. Type

::

    sage: maple.help('combinat, fibonacci')   # not tested, since it uses a pager

We now see how the Maple command fibonacci works under the
combinatorics package. Try typing in

::

    sage: maple.fibonacci(10)                # optional - maple
    fibonacci(10)

You will get fibonacci(10) as output since Maple has not loaded the
combinatorics package yet. To rectify this type

::

    sage: maple('combinat[fibonacci]')(10)     # optional - maple
    55

instead.

If you want to load the combinatorics package for future
calculations, in Sage this can be done as

::

    sage: maple.with_package('combinat')       # optional - maple

or

::

    sage: maple.load('combinat')               # optional - maple

Now if we type ``maple.fibonacci(10)``, we get the
correct output::

    sage: maple.fibonacci(10)                  # optional - maple
    55

Some common maple packages include ``combinat``,
``linalg``, and ``numtheory``. To produce
the first 19 Fibonacci numbers, use the sequence command.

::

    sage: maple('seq(fibonacci(i),i=1..19)')     # optional - maple
    1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584,
    4181

Two other useful Maple commands are ifactor and isprime. For
example

::

    sage: maple.isprime(maple.fibonacci(27))     # optional - maple
    false
    sage: maple.ifactor(maple.fibonacci(27))     # optional - maple
    "(2)*"(17)*"(53)*"(109)

Note that the isprime function that is included with Sage (which
uses PARI) is better than the Maple one (it is faster and gives a
provably correct answer, whereas Maple is sometimes wrong).

::

    sage: alpha = maple('(1+sqrt(5))/2')         # optional - maple
    sage: beta = maple('(1-sqrt(5))/2')          # optional - maple
    sage: f19  = alpha^19 - beta^19/maple('sqrt(5)')      # optional - maple
    sage: f19                                             # optional - maple
    (1/2+1/2*5^(1/2))^19-1/5*(1/2-1/2*5^(1/2))^19*5^(1/2)
    sage: f19.simplify()                # somewhat randomly ordered output; optional - maple
    6765+5778/5*5^(1/2)

Let's say we want to write a maple program now that squares a
number if it is positive and cubes it if it is negative. In maple,
that would look like

::

    mysqcu := proc(x)
    if x > 0 then x^2;
    else x^3; fi;
    end;

In Sage, we write

::

    sage: mysqcu = maple('proc(x) if x > 0 then x^2 else x^3 fi end')    # optional - maple
    sage: mysqcu(5)                                                      # optional - maple
    25
    sage: mysqcu(-5)                                                     # optional - maple
    -125

More complicated programs should be put in a separate file and
loaded.
"""

#############################################################################
#       Copyright (C) 2005 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#############################################################################

from __future__ import with_statement

import os

from expect import Expect, ExpectElement, ExpectFunction, FunctionElement, gc_disabled

import pexpect

from sage.misc.misc import verbose, DOT_SAGE
from sage.misc.pager import pager

COMMANDS_CACHE = '%s/maple_commandlist_cache.sobj'%DOT_SAGE

class Maple(Expect):
    """
    Interface to the Maple interpreter.

    Type ``maple.[tab]`` for a list of all the functions
    available from your Maple install. Type
    ``maple.[tab]?`` for Maple's help about a given
    function. Type ``maple(...)`` to create a new Maple
    object, and ``maple.eval(...)`` to run a string using
    Maple (and get the result back as a string).
    """
    def __init__(self, maxread=100, script_subdirectory="", server=None, server_tmpdir=None, logfile=None):
        """
        Create an instance of the Maple interpreter.

        EXAMPLES::

            sage: maple == loads(dumps(maple))
            True
        """
        Expect.__init__(self,
                        name = 'maple',
                        prompt = '#-->',
                        command = "maple -t",
                        maxread = maxread,
                        script_subdirectory = script_subdirectory,
                        restart_on_ctrlc = False,
                        server = server,
                        server_tmpdir = server_tmpdir,
                        verbose_start = False,
                        logfile = logfile,
                        eval_using_file_cutoff=1)  # very important that this is 1
        # It's very important to use file i/o for everything,
        # since maple stupid command line interface always
        # dumps you into the editor when an error occurs,
        # and I can find no way to turn it off!!

    def _function_class(self):
        """
        EXAMPLES::

            sage: maple._function_class()
            <class 'sage.interfaces.maple.MapleFunction'>

        ::

            sage: type(maple.diff)
            <class 'sage.interfaces.maple.MapleFunction'>
        """
        return MapleFunction

    def _keyboard_interrupt(self):
        print "Interrupting %s..."%self
        self._expect.sendline(chr(3))  # send ctrl-c
        self._expect.expect(self._prompt)
        self._expect.expect(self._prompt)
        raise RuntimeError, "Ctrl-c pressed while running %s"%self

    def __reduce__(self):
        """
        EXAMPLES::

            sage: maple.__reduce__()
            (<function reduce_load_Maple at 0x...>, ())
            sage: f, args = _
            sage: f(*args)
            Maple
        """
        return reduce_load_Maple, tuple([])

    def _read_in_file_command(self, filename):
        r"""
        Returns the string used to read filename into Maple.

        EXAMPLES::

            sage: maple._read_in_file_command('test')
            'read "test"'

        ::

            sage: filename = tmp_filename()
            sage: f = open(filename, 'w')
            sage: f.write('xx := 22;\n')
            sage: f.close()
            sage: maple.read(filename)    # optional - maple
            sage: maple.get('xx').strip() # optional - maple
            '22'
        """
        return 'read "%s"'%filename

    def _quit_string(self):
        """
        EXAMPLES::

            sage: maple._quit_string()
            'quit'

        ::

            sage: m = Maple()
            sage: a = m(2)           # optional - maple
            sage: m.is_running()     # optional - maple
            True
            sage: m.quit()           # optional - maple
            sage: m.is_running()     # optional - maple
            False
        """
        return 'quit'

    def _install_hints(self):
        """
        Hints for installing Maple on your computer.

        AUTHORS:

        - William Stein and Justin Walker (2006-02-12).

        EXAMPLES::

            sage: print maple._install_hints()
            In order...
        """
        return """

In order to use the Maple interface you need to have Maple installed
and have a script in your PATH called "maple" that runs the
command-line version of Maple.  Alternatively, you could use a remote
connection to a server running Maple; for hints, type
    print maple._install_hints_ssh()

  (1) You might have to buy Maple (http://webstore.maplesoft.com/).

  (2) * LINUX: The maple script comes standard with your Maple install.

      * APPLE OS X:
          (a) create a file called maple (in your PATH), with the following contents:
             #!/bin/sh
             /Library/Frameworks/Maple.framework/Versions/Current/bin/maple $@
          (b) Save the file.
          (c) Make the file executable.
                chmod +x maple

      * WINDOWS:
        You must install Maple-for-Linux into the VMware machine (sorry, that's
        the only way at present).
"""

    def expect(self):
        """
        Returns the pexpect object for this Maple session.

        EXAMPLES::

            sage: m = Maple()
            sage: m.expect() is None
            True
            sage: m._start()           # optional - maple
            sage: m.expect()           # optional - maple
            <pexpect.spawn instance at 0x...>
            sage: m.quit()             # optional - maple
        """
        return self._expect

    def console(self):
        """
        Spawn a new Maple command-line session.

        EXAMPLES::

            sage: maple.console() # not tested
                |^/|     Maple 11 (IBM INTEL LINUX)
            ._|\|   |/|_. Copyright (c) Maplesoft, a division of Waterloo Maple Inc. 2007
             \  MAPLE  /  All rights reserved. Maple is a trademark of
             <____ ____>  Waterloo Maple Inc.
                  |       Type ? for help.
            >
        """
        maple_console()

##     def killall(self):
##         """
##         Kill all running instances of the maple interpreter
##         on this system.

##         TODO: When SAGE exists it doesn't correctly by default kill
##         all running Maple interpreters, for some strange reason.
##         Calling this function uses the kill and pidof operating system
##         programs to find all instances of cmaple and kill them.
##         """
##         import os
##         self._expect = None
##         while True:
##             pid = os.popen("pidof cmaple").read()[:-1]
##             if len(pid) > 0:
##                 os.system('kill -9 %s'%pid)
##             else:
##                 break

    def completions(self, s):
        """
        Return all commands that complete the command starting with the
        string s. This is like typing s[Ctrl-T] in the maple interpreter.

        EXAMPLES::

            sage: c = maple.completions('di')  # optional - maple
            sage: 'divide' in c                # optional - maple
            True
        """
        bs = chr(8)*len(s)
        if self._expect is None:
            self._start()
        E = self._expect
        E.sendline('%s%s%s'%(s,chr(20),bs))
        t = E.timeout
        E.timeout=0.3  # since some things have no completion
        try:
            E.expect('----')
        except pexpect.TIMEOUT:
            E.timeout = t
            return []
        E.timeout = t
        v = E.before
        E.expect(self._prompt)
        E.expect(self._prompt)
        return v.split()[2:]

    def _commands(self):
        """
        Return list of all commands defined in Maple.

        EXAMPLES::

            sage: c = maple._commands() # optional - maple
            sage: len(c) > 100          # optional - maple
            True
            sage: 'dilog' in c          # optional - maple
            True
        """
        try:
            v = sum([self.completions(chr(65+n)) for n in range(26)], []) + \
                sum([self.completions(chr(97+n)) for n in range(26)], [])
        except RuntimeError:
            print "\n"*3
            print "*"*70
            print "WARNING: You do not have a working version of Maple installed!"
            print "*"*70
            v = []
        v.sort()
        return v

    def trait_names(self, verbose=True, use_disk_cache=True):
        """
        Returns a list of all the commands defined in Maple and optionally
        (per default) store them to disk.

        EXAMPLES::

            sage: c = maple.trait_names(use_disk_cache=False, verbose=False) # optional - maple
            sage: len(c) > 100  # optional - maple
            True
            sage: 'dilog' in c  # optional - maple
            True
        """
        try:
            return self.__trait_names
        except AttributeError:
            import sage.misc.persist
            if use_disk_cache:
                try:
                    self.__trait_names = sage.misc.persist.load(COMMANDS_CACHE)
                    return self.__trait_names
                except IOError:
                    pass
            if verbose:
                print "\nBuilding Maple command completion list (this takes"
                print "a few seconds only the first time you do it)."
                print "To force rebuild later, delete %s."%COMMANDS_CACHE
            v = self._commands()
            self.__trait_names = v
            if len(v) > 200:
                # Maple is actually installed.
                sage.misc.persist.save(v, COMMANDS_CACHE)
            return v

    def _eval_line(self, line, allow_use_file=True, wait_for_prompt=True):
        """
        EXAMPLES::

            sage: maple._eval_line('2+2')  # optional - maple
            '4'
        """
        line += ';'
        with gc_disabled():
            z = Expect._eval_line(self, line, allow_use_file=allow_use_file,
                    wait_for_prompt=wait_for_prompt).replace('\\\n','').strip()
            if z.lower().find("error") != -1:
                # The following was very tricky to figure out.
                # When an error occurs using Maple, unfortunately,
                # Maple also dumps one into the line where the
                # error occured with that line copied in.  This
                # totally messes up the pexpect interface.  However,
                # I think the following few lines successfully
                # "clear things out", i.e., delete the text from
                # the edit buffer and get a clean prompt.
                e = self.expect()
                e.sendline('%s__sage__;'%(chr(8)*len(line)))
                e.expect('__sage__;')
                e.expect(self._prompt)
                raise RuntimeError, "An error occured running a Maple command:\nINPUT:\n%s\nOUTPUT:\n%s"%(line, z)
        return z

    def cputime(self, t=None):
        r"""
        Returns the amount of CPU time that the Maple session has used. If
        ``t`` is not None, then it returns the difference
        between the current CPU time and ``t``.

        EXAMPLES::

            sage: t = maple.cputime() # optional - maple
            sage: t                   # random; optional - maple
            0.02
            sage: x = maple('x')      # optional - maple
            sage: maple.diff(x^2, x)  # optional - maple
            2*x
            sage: maple.cputime(t)    # random; optional - maple
            0.0
        """
        if t is None:
            return float(self('time()'))
        else:
            return float(self('time() - %s'%float(t)))

    def set(self, var, value):
        """
        Set the variable var to the given value.

        EXAMPLES::

            sage: maple.set('xx', '2') # optional - maple
            sage: maple.get('xx')      # optional - maple
            '2'
        """
        cmd = '%s:=%s:'%(var,value)
        out = self.eval(cmd)
        if out.find("error") != -1:
            raise TypeError, "Error executing code in Maple\nCODE:\n\t%s\nMaple ERROR:\n\t%s"%(cmd, out)

    def get(self, var):
        """
        Get the value of the variable var.

        EXAMPLES::

            sage: maple.set('xx', '2') # optional - maple
            sage: maple.get('xx')      # optional - maple
            '2'
        """
        s = self.eval('printf("%%q",%s)'%var)
        return s

    def _object_class(self):
        """
        Returns the class of MapleElements.

        EXAMPLES::

            sage: maple._object_class()
            <class 'sage.interfaces.maple.MapleElement'>

        ::

            sage: m = maple(2)  # optional - maple
            sage: type(m)       # optional - maple
            <class 'sage.interfaces.maple.MapleElement'>
        """
        return MapleElement

    def _function_element_class(self):
        """
        Returns the MapleFunctionElement class.

        EXAMPLES::

            sage: maple._function_element_class()
            <class 'sage.interfaces.maple.MapleFunctionElement'>

        ::

            sage: two = maple(2)  # optional - maple
            sage: type(two.gcd)   # optional - maple
            <class 'sage.interfaces.maple.MapleFunctionElement'>
        """
        return MapleFunctionElement

    def _equality_symbol(self):
        """
        Returns the symbol used for equality testing in Maple.

        EXAMPLES::

            sage: maple._equality_symbol()
            '='

            sage: maple(2) == maple(2) # optional -- requires maple
            True
        """
        return '='

    def _true_symbol(self):
        """
        Returns the symbol used for truth in Maple.

        EXAMPLES::

            sage: maple._true_symbol()
            'true'

        ::

            sage: maple(2) == maple(2) # optional - maple
            True
        """
        return 'true'

    def _assign_symbol(self):
        """
        Returns the symbol used for assignment in Maple.

        EXAMPLES::

            sage: maple._assign_symbol()
            ':='
        """
        return ":="

    def _source(self, s):
        """
        Tries to return the source code of a Maple function str as a
        string.

        EXAMPLES::

            sage: print maple._source('curry').strip()  # optional - maple
            p -> subs('_X' = args[2 .. nargs], () -> p(_X, args))
            sage: maple._source('ZZZ')                  # optional - maple
            Traceback (most recent call last):
            ...
            Exception: no source code could be found
        """
        cmd = 'echo "interface(verboseproc=2): print(%s);" | maple -q'%s
        src = os.popen(cmd).read()
        if src.strip() == s:
            raise Exception, "no source code could be found"
        else:
            return src

    def source(self, s):
        """
        Display the Maple source (if possible) about s. This is the same as
        returning the output produced by the following Maple commands:

        interface(verboseproc=2): print(s)

        INPUT:


        -  ``s`` - a string representing the function whose
           source code you want


        EXAMPLES::

            sage: maple.source('curry')  #not tested
            p -> subs('_X' = args[2 .. nargs], () -> p(_X, args))
        """
        try:
            pager()(self._source(s))
        except Exception:
            pager()('No source code could be found.')

    def _help(self, str):
        r"""
        Returns the Maple help on ``str``.

        EXAMPLES::

            sage: maple._help('gcd')  # optional - maple
            "gcd - greatest common divisor of polynomials...
        """
        return os.popen('echo "?%s" | maple -q'%str).read()

    def help(self, str):
        """
        Display Maple help about str. This is the same as typing "?str" in
        the Maple console.

        INPUT:


        -  ``str`` - a string to search for in the maple help
           system


        EXAMPLES::

            sage: maple.help('digamma') #not tested
            Psi - the Digamma and Polygamma functions
            ...
        """
        pager()(self._help(str))

    def with_package(self, package):
        """
        Make a package of Maple procedures available in the interpreter.

        INPUT:


        -  ``package`` - string


        EXAMPLES: Some functions are unknown to Maple until you use with to
        include the appropriate package.

        ::

            sage: maple.quit()   # optional -- to reset maple.
            sage: maple('partition(10)')              # optional -- requires maple
            partition(10)
            sage: maple('bell(10)')                   # optional -- requires maple
            bell(10)
            sage: maple.with_package('combinat')      # optional -- requires maple
            sage: maple('partition(10)')              # optional -- requires maple
            [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 2], [1, 1, 1, 1, 1, 1, 2, 2], [1, 1, 1, 1, 2, 2, 2], [1, 1, 2, 2, 2, 2], [2, 2, 2, 2, 2], [1, 1, 1, 1, 1, 1, 1, 3], [1, 1, 1, 1, 1, 2, 3], [1, 1, 1, 2, 2, 3], [1, 2, 2, 2, 3], [1, 1, 1, 1, 3, 3], [1, 1, 2, 3, 3], [2, 2, 3, 3], [1, 3, 3, 3], [1, 1, 1, 1, 1, 1, 4], [1, 1, 1, 1, 2, 4], [1, 1, 2, 2, 4], [2, 2, 2, 4], [1, 1, 1, 3, 4], [1, 2, 3, 4], [3, 3, 4], [1, 1, 4, 4], [2, 4, 4], [1, 1, 1, 1, 1, 5], [1, 1, 1, 2, 5], [1, 2, 2, 5], [1, 1, 3, 5], [2, 3, 5], [1, 4, 5], [5, 5], [1, 1, 1, 1, 6], [1, 1, 2, 6], [2, 2, 6], [1, 3, 6], [4, 6], [1, 1, 1, 7], [1, 2, 7], [3, 7], [1, 1, 8], [2, 8], [1, 9], [10]]
            sage: maple('bell(10)')                   # optional -- requires maple
            115975
            sage: maple('fibonacci(10)')              # optional -- requires maple
            55
        """
        self.eval('with(%s)'%package)

    load = with_package

    def clear(self, var):
        """
        Clear the variable named var.

        Unfortunately, Maple does not have a clear command. The next best
        thing is to set equal to the constant 0, so that memory will be
        freed.

        EXAMPLES::

            sage: maple.set('xx', '2')  # optional - maple
            sage: maple.get('xx')       # optional - maple
            '2'
            sage: maple.clear('xx')     # optional - maple
            sage: maple.get('xx')       # optional - maple
            '0'
        """
        self.set(var, '0')

class MapleFunction(ExpectFunction):
    def _sage_doc_(self):
        """
        Returns the Maple help for this function. This gets called when
        doing "?" on self.

        EXAMPLES::

            sage: maple.gcd._sage_doc_()  # optional - maple
            "gcd - greatest common divisor of polynomials...
        """
        M = self._parent
        return M._help(self._name)

    def _sage_src_(self):
        """
        Returns the source code of self. This is the function that
        eventually gets called when doing maple.gcd?? for example.

        EXAMPLES::

            sage: print maple.curry._sage_src_().strip() # optional - maple
            p -> subs('_X' = args[2 .. nargs], () -> p(_X, args))
            sage: maple.ZZZ._sage_src_()                 # optional - maple
            Traceback (most recent call last):
            ...
            Exception: no source code could be found
        """
        M = self._parent
        return M._source(self._name)

class MapleFunctionElement(FunctionElement):
    def _sage_doc_(self):
        """
        Returns the Maple help for this function. This gets called when
        doing "?" on self.

        EXAMPLES::

            sage: two = maple(2)  # optional - maple
            sage: two.gcd._sage_doc_() # optional - maple
            "gcd - greatest common divisor of polynomials...
        """
        return self._obj.parent()._help(self._name)

    def _sage_src_(self):
        """
        Returns the source code of self.

        EXAMPLES::

            sage: g = maple('gcd')                   # optional - maple
            sage: print g.curry._sage_src_().strip() # optional - maple
            p -> subs('_X' = args[2 .. nargs], () -> p(_X, args))
            sage: m = maple('2')                     # optional - maple
            sage: m.ZZZ._sage_src_()                 # optional - maple
            Traceback (most recent call last):
            ...
            Exception: no source code could be found
        """
        return self._obj.parent()._source(self._name)

class MapleElement(ExpectElement):
    def __float__(self):
        """
        Returns a floating point version of self.

        EXAMPLES::

            sage: float(maple(1/2))  # optional - maple
            0.5
            sage: type(_)            # optional - maple
            <type 'float'>
        """
        M = self.parent()
        return float(maple.eval('evalf(%s)'%self.name()))

    def __hash__(self):
        """
        Returns a 64-bit integer representing the hash of self. Since
        Python uses 32-bit hashes, it will automatically convert the result
        of this to a 32-bit hash.

        These examples are optional, and require Maple to be installed. You
        don't need to install any Sage packages for this.

        EXAMPLES::

            sage: m = maple('x^2+y^2')                      # optional - maple
            sage: m.__hash__()                              # optional - maple
            188724254834261060184983038723355865733L
            sage: hash(m)                                   # optional - maple
            5035731711831192733
            sage: m = maple('x^2+y^3')                      # optional - maple
            sage: m.__hash__()                              # optional - maple
            264835029579301191531663246434344770556L
            sage: hash(m)                                   # optional - maple
            -2187277978252104690
        """
        return int(maple.eval('StringTools:-Hash(convert(%s, string));'%self.name())[1:-1],16)

    def __cmp__(self, other):
        """
        Compare equality between self and other, using maple.

        These examples are optional, and require Maple to be installed. You
        don't need to install any Sage packages for this.

        EXAMPLES::

            sage: a = maple(5)                             # optional - maple
            sage: b = maple(5)                             # optional - maple
            sage: a == b                                   # optional - maple
            True
            sage: a == 5                                   # optional - maple
            True

        ::

            sage: c = maple(3)                             # optional - maple
            sage: a == c                                   # optional - maple
            False
            sage: a < c                                    # optional - maple
            False
            sage: a < 6                                    # optional - maple
            True
            sage: c <= a                                   # optional - maple
            True

        ::

            sage: M = matrix(ZZ, 2, range(1,5))            # optional - maple
            sage: Mm = maple(M)                            # optional - maple
            sage: Mm == Mm                                 # optional - maple
            True
            sage: Mm < 5                                   # optional - maple
            True
            sage: (Mm < 5) == (M < 5)                      # optional - maple
            True
            sage: 5 < Mm                                   # optional - maple
            False

        TESTS::

            sage: x = var('x')
            sage: t = maple((x+1)^2)                       # optional -- requires maple
            sage: u = maple(x^2+2*x+1)                     # optional -- requires maple
            sage: u == t # todo: not implemented
            True         # returns False, should use 'testeq' in maple
            sage: maple.eval('testeq(%s = %s)'%(t.name(),u.name()))    # optional - maple
            'true'
        """
        P = self.parent()
        if P.eval("evalb(%s %s %s)"%(self.name(), P._equality_symbol(),
                                 other.name())) == P._true_symbol():
            return 0
        # Maple does not allow comparing objects of different types and
        # it raises an error in this case.
        # We catch the error, and return True for <
        try:
            if P.eval("evalb(%s %s %s)"%(self.name(), P._lessthan_symbol(), other.name())) == P._true_symbol():
                return -1
        except RuntimeError, e:
            msg = str(e)
            if 'is not valid' in msg and 'to < or <=' in msg:
                if (hash(str(self)) < hash(str(other))):
                    return -1
                else:
                    return 1
            else:
                raise RuntimeError, e
        if P.eval("evalb(%s %s %s)"%(self.name(), P._greaterthan_symbol(), other.name())) == P._true_symbol():
            return 1
        # everything is supposed to be comparable in Python, so we define
        # the comparison thus when no comparable in interfaced system.
        if (hash(self) < hash(other)):
            return -1
        else:
            return 1

    def _mul_(self, right):
        """
        These examples are optional, and require Maple to be installed. You
        don't need to install any Sage packages for this.

        EXAMPLES::

            sage: t = maple(5); u = maple(3)                # optional - maple
            sage: t*u                                       # optional - maple
            15
            sage: M = matrix(ZZ,2,range(4))                 # optional - maple
            sage: Mm = maple(M)                             # optional - maple
            sage: Mm*Mm                                     # optional - maple
            Matrix(2, 2, [[2,3],[6,11]])

        ::

            sage: v = vector(ZZ,2,[2,3])
            sage: vm = maple(v)                             # optional - maple
            sage: vm*Mm                                     # optional - maple
            Vector[row](2, [6,11])

        ::

            sage: t*Mm                                      # optional - maple
            Matrix(2, 2, [[0,5],[10,15]])
        """
        P = self._check_valid()
        try:
            return P.new('%s . %s'%(self._name, right._name))
        except Exception, msg:
            raise TypeError,msg

    def trait_names(self):
        """
        EXAMPLES::

            sage: a = maple(2) # optional - maple
            sage: 'sin' in a.trait_names() # optional - maple
            True
        """
        return self.parent().trait_names()

    def __repr__(self):
        """
        Return a string representation of self.

        These examples are optional, and require Maple to be installed. You
        don't need to install any Sage packages for this.

        EXAMPLES::

            sage: x = var('x')
            sage: maple(x)                      # optional - maple
            x
            sage: maple(5)                      # optional - maple
            5
            sage: M = matrix(QQ,2,range(4))
            sage: maple(M)                      # optional - maple
            Matrix(2, 2, [[0,1],[2,3]])
        """
        self._check_valid()
        return self.parent().get(self._name)

    def _latex_(self):
        r"""
        You can output Maple expressions in latex.

        EXAMPLES::

            sage: print latex(maple('(x^4 - y)/(y^2-3*x)'))      # optional -- requires maple
            {\frac {{x}^{4}-y}{{y}^{2}-3\,x}}
            sage: print latex(maple(pi - e^3))                   # optional -- requires maple
            \pi - \left( {e^{1}} \right) ^{3}

        .. note::

           Some expressions might require the Maple style file
           ``maple2e.sty`` in order to latex correctly.
        """
        return self.parent().eval('latex(%s)'%self.name())

# An instance
maple = Maple(script_subdirectory='user')

def reduce_load_Maple():
    """
    Returns the maple object created in sage.interfaces.maple.

    EXAMPLES::

        sage: from sage.interfaces.maple import reduce_load_Maple
        sage: reduce_load_Maple()
        Maple
    """
    return maple


import os
def maple_console():
    """
    Spawn a new Maple command-line session.

    EXAMPLES::

        sage: maple_console() #not tested
            |^/|     Maple 11 (IBM INTEL LINUX)
        ._|\|   |/|_. Copyright (c) Maplesoft, a division of Waterloo Maple Inc. 2007
         \  MAPLE  /  All rights reserved. Maple is a trademark of
         <____ ____>  Waterloo Maple Inc.
              |       Type ? for help.
        >
    """
    os.system('maple')


def __doctest_cleanup():
    """
    EXAMPLES::

        sage: from sage.interfaces.maple import __doctest_cleanup
        sage: m = maple(2)         # optional - maple
        sage: maple.is_running()   # optional - maple
        True
        sage: __doctest_cleanup()
        sage: maple.is_running()
        False
    """
    import sage.interfaces.quit
    sage.interfaces.quit.expect_quitall()



"""
The following only works in Maple >= 9, I guess, but could
be useful.

From Jaap Spies:  In addition Maple has a nice feature the function

 > FunctionAdvisor();

 > FunctionAdvisor(topics, quiet);
      [DE, analytic_extension, asymptotic_expansion, branch_cuts,
      branch_points, calling_sequence, class_members,
      classify_function, definition, describe, differentiation_rule,
      function_classes, identities, integral_form,
      known_functions, relate, series, singularities, special_values,
      specialize, sum_form, synonyms]

 > FunctionAdvisor(syntax, hypergeom);
                                            hypergeom([a, b], [c], z)

Eventually this could be used to do an intelligent command
completion.
"""
