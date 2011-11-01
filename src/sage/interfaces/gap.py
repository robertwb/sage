r"""
Interface to GAP

Sage provides an interface to the GAP system. This system provides
extensive group theory, combinatorics, etc.

The GAP interface will only work if GAP is installed on your
computer; this should be the case, since GAP is included with Sage.
The interface offers three pieces of functionality:


#. ``gap_console()`` - A function that dumps you into
   an interactive command-line GAP session.

#. ``gap(expr)`` - Evaluation of arbitrary GAP
   expressions, with the result returned as a string.

#. ``gap.new(expr)`` - Creation of a Sage object that
   wraps a AP object. This provides a Pythonic interface to GAP. For
   example, if ``f=gap.new(10)``, then
   ``f.Factors()`` returns the prime factorization of
   `10` computed using GAP.


First Examples
--------------

We factor an integer using GAP::

    sage: n = gap(20062006); n
    20062006
    sage: n.parent()
    Gap
    sage: fac = n.Factors(); fac
    [ 2, 17, 59, 73, 137 ]
    sage: fac.parent()
    Gap
    sage: fac[1]
    2

GAP and Singular
----------------

This example illustrates conversion between Singular and GAP via
Sage as an intermediate step. First we create and factor a Singular
polynomial.

::

    sage: singular(389)
    389
    sage: R1 = singular.ring(0, '(x,y)', 'dp')
    sage: f = singular('9*x^16-18*x^13*y^2-9*x^12*y^3+9*x^10*y^4-18*x^11*y^2+36*x^8*y^4+18*x^7*y^5-18*x^5*y^6+9*x^6*y^4-18*x^3*y^6-9*x^2*y^7+9*y^8')
    sage: F = f.factorize()
    sage: print F
    [1]:
       _[1]=9
       _[2]=x^6-2*x^3*y^2-x^2*y^3+y^4
       _[3]=-x^5+y^2
    [2]:
       1,1,2

Next we convert the factor `-x^5+y^2` to a Sage
multivariate polynomial. Note that it is important to let
`x` and `y` be the generators of a polynomial ring,
so the eval command works.

::

    sage: R.<x,y> = PolynomialRing(QQ,2)
    sage: s = F[1][3].sage_polystring(); s
    '-x**5+y**2'
    sage: g = eval(s); g
    -x^5 + y^2

Next we create a polynomial ring in GAP and obtain its
indeterminates::

    sage: R = gap.PolynomialRing('Rationals', 2); R
    PolynomialRing( Rationals, ["x_1", "x_2"] )
    sage: I = R.IndeterminatesOfPolynomialRing(); I
    [ x_1, x_2 ]

In order to eval `g` in GAP, we need to tell GAP to view
the variables ``x0`` and ``x1`` as the two
generators of `R`. This is the one tricky part. In the GAP
interpreter the object ``I`` has its own name (which
isn't ``I``). We can access its name using
``I.name()``.

::

    sage: _ = gap.eval("x := %s[1];; y := %s[2];;"%(I.name(), I.name()))

Now `x_0` and `x_1` are defined, so we can
construct the GAP polynomial `f` corresponding to
`g`::

    sage: R.<x,y> = PolynomialRing(QQ,2)
    sage: f = gap(str(g)); f
    -x_1^5+x_2^2

We can call GAP functions on `f`. For example, we evaluate
the GAP ``Value`` function, which evaluates `f`
at the point `(1,2)`.

::

    sage: f.Value(I, [1,2])
    3
    sage: g(1,2)        # agrees
    3

Saving and loading objects
--------------------------

Saving and loading GAP objects (using the dumps method, etc.) is
*not* supported, since the output string representation of Gap
objects is sometimes not valid input to GAP. Creating classes that
wrap GAP objects *is* supported, via simply defining the a
_gap_init_ member function that returns a string that when
evaluated in GAP constructs the object. See
``groups/permutation_group.py`` for a nontrivial
example of this.

Long Input
----------

The GAP interface reads in even very long input (using files) in a
robust manner, as long as you are creating a new object.

.. note::

   Using ``gap.eval`` for long input is much less robust, and is not
   recommended.

::

    sage: t = '"%s"'%10^10000   # ten thousand character string.
    sage: a = gap(t)

Changing which GAP is used
--------------------------

Use this code to change which GAP interpreter is run. E.g.,

::

       import sage.interfaces.gap
       sage.interfaces.gap.gap_cmd = "/usr/local/bin/gap"

AUTHORS:

- David Joyner and William Stein: initial version(s)

- William Stein (2006-02-01): modified gap_console command so it uses
  exactly the same startup command as Gap.__init__.

- William Stein (2006-03-02): added tab completions: gap.[tab], x =
  gap(...), x.[tab], and docs, e.g., gap.function? and x.function?
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

import expect
from expect import Expect, ExpectElement, FunctionElement, ExpectFunction
from sage.misc.misc import SAGE_ROOT, SAGE_DATA, DOT_SAGE, is_64_bit, is_in_string
from IPython.genutils import page
import re
import os
import pexpect
import time

WORKSPACE = "%s/gap/workspace-%s"%(DOT_SAGE, abs(hash(SAGE_ROOT)))

GAP_STAMP = '%s/local/bin/gap_stamp'%SAGE_ROOT
if not os.path.exists(GAP_STAMP):
    open(GAP_STAMP,'w').close()

GAP_DIR = '%s/gap/'%DOT_SAGE

first_try = True

try:
    os.makedirs(GAP_DIR)
    open('%s/gap/README.txt'%DOT_SAGE, 'w').write("It is OK to delete all these cache files.  They will be recreated as needed.")
except OSError as err:
    import errno
    if not err.errno == errno.EEXIST:
        raise

gap_cmd = "gap -r"

def gap_command(use_workspace_cache=True, local=True):
    if use_workspace_cache:
        if local:
            return "%s -L %s"%(gap_cmd, WORKSPACE), False
        else:
            # TO DO: Use remote workspace
            return gap_cmd, False
    else:
        return gap_cmd, True

############ Classes with methods for both the GAP3 and GAP4 interface

class Gap_generic(Expect):
    r"""
    Generic interface to the GAP3/GAP4 interpreters.

    AUTHORS:

    - William Stein and David Joyner (interface for GAP4)

    - Franco Saliola (Feb 2010): refactored to separate out the generic
      code

    """
    def _assign_symbol(self):
        r"""
        Return the assign symbol in GAP.

        TESTS::

            sage: gap = Gap()
            sage: print gap._assign_symbol()
            :=

        """
        return ":="

    def _quit_string(self):
        """
        Returns the string used to quit GAP.

        EXAMPLES::

            sage: gap._quit_string()
            'quit'

        ::

            sage: g = Gap()
            sage: a = g(2); g.is_running()
            True
            sage: g.quit()
            sage: g.is_running()
            False
        """
        return 'quit'

    def _read_in_file_command(self, filename):
        r"""
        Returns the command use to read in a file in GAP.

        EXAMPLES::

            sage: gap._read_in_file_command('test')
            'Read("test");'

        ::

            sage: filename = tmp_filename()
            sage: f = open(filename, 'w')
            sage: f.write('xx := 22;\n')
            sage: f.close()
            sage: gap.read(filename)
            sage: gap.get('xx').strip()
            '22'
        """
        return 'Read("%s");'%filename

    def _continuation_prompt(self):
        """
        Returns the continuation prompt in GAP.

        EXAMPLES::

            sage: gap._continuation_prompt()
            '> '
        """
        return '> '

    def load_package(self, pkg, verbose=False):
        """
        Load the Gap package with the given name.

        If loading fails, raise a RuntimeError exception.

        TESTS::

            sage: gap.load_package("chevie")
            Traceback (most recent call last):
            ...
            RuntimeError: Error loading Gap package chevie

        """
        if verbose:
            print "Loading GAP package %s"%pkg
        x = self.eval('LoadPackage("%s")'%pkg)
        if x == 'fail':
            raise RuntimeError, 'Error loading Gap package %s'%pkg

    def eval(self, x, newlines=False, strip=True, split_lines=True, **kwds):
        r"""
        Send the code in the string s to the GAP interpreter and return the
        output as a string.

        INPUT:


        -  ``s`` - string containing GAP code.

        -  ``newlines`` - bool (default: True); if False,
           remove all backslash-newlines inserted by the GAP output
           formatter.

        -  ``strip`` - ignored

        -  ``split_lines`` -- bool (default: True); if True then each
           line is evaluated separately.  If False, then the whole
           block of code is evaluated all at once.

        EXAMPLES::

            sage: gap.eval('2+2')
            '4'
            sage: gap.eval('Print(4); #test\n Print(6);')
            '46'
            sage: gap.eval('Print("#"); Print(6);')
            '#6'
            sage: gap.eval('4; \n 6;')
            '4\n6'
            sage: gap.eval('if 3>2 then\nPrint("hi");\nfi;')
            'hi'
            sage: gap.eval('## this is a test\nPrint("OK")')
            'OK'
            sage: gap.eval('Print("This is a test. Oh no, a #");# but this is a comment\nPrint("OK")')
            'This is a test. Oh no, a #OK'
            sage: gap.eval('if 4>3 then')
            ''
            sage: gap.eval('Print("Hi how are you?")')
            'Hi how are you?'
            sage: gap.eval('fi')
            ''
        """
        # '"
        #We remove all of the comments:  On each line, we try
        #to find a pound sign.  If we find it, we check to see if
        #it is occurring in a string.  If it is not in a string, we
        #strip off the comment.
        if not split_lines:
            input_line=str(x)
        else:
            input_line = ""
            for line in str(x).rstrip().split('\n'):
                pound_position = line.find('#')
                while pound_position != -1:
                    if not is_in_string(line, pound_position):
                        line = line[:pound_position]
                    pound_position = line.find('#',pound_position+1)
                input_line += " "+line
            if not input_line.endswith(';'):
                input_line += ';'
        result = Expect.eval(self, input_line, **kwds)
        if not newlines:
            result = result.replace("\\\n","")
        return result.strip()


    def _execute_line(self, line, wait_for_prompt=True, expect_eof=False):
        E = self._expect
        try:
            if len(line) > 4095:
                raise RuntimeError("Passing commands this long to gap would hang")
            E.sendline(line)
        except OSError:
            raise RuntimeError("Error evaluating %s in %s"%(line, self))
        if wait_for_prompt == False:
            return ('','')
        if len(line)==0:
            return ('','')
        try:
            E.expect("\r\n") # seems to be necessary to skip TWO echoes
            E.expect("\r\n") # one from the pty and one from GAP, I guess
            normal_outputs = []
            error_outputs = []
            current_outputs = normal_outputs
            while True:
                x = E.expect_list(self._compiled_full_pattern)
                current_outputs.append(E.before)
                if x == 0:   # @p
                    if E.after != '@p1.':
                        print "Warning: possibly wrong version of GAP package interface\n"
                        print "Crossing fingers and continuing\n"
                elif x == 1: #@@
                    current_outputs.append('@')
                elif x == 2: #special char
                    current_outputs.append(chr(ord(E.after[1:2])-ord('A')+1))
                elif x == 3: # garbage collection info, ignore
                    pass
                elif x == 4: # @e -- break loop
                    E.sendline("quit;")
                elif x == 5: # @c completion, doesn't seem to happen when -p is in use
                    print "I didn't think GAP could do this\n"
                elif x == 6: # @f GAP error message
                    current_outputs = error_outputs;
                elif x == 7: # @h help text, but this stopped happening with new help
                    print "I didn't think GAP could do this"
                elif x == 8: # @i awaiting normal input
                    break;
                elif x == 9: # @m finished running a child
                    pass   # there is no need to do anything
                elif x==10: #@n normal output line
                    current_outputs = normal_outputs;
                elif x==11: #@r echoing input
                    E.expect_list(self._compiled_small_pattern)
                elif x==12: #@sN shouldn't happen
                    print "Warning: this should never happen"
                elif x==13: #@w GAP is trying to send a Window command
                    print "Warning: this should never happen"
                elif x ==14: #@x seems to be safely ignorable
                    pass
                elif x == 15:#@z GAP starting a subprocess
                    pass  # there is no need to do anything
        except pexpect.EOF:
            if not expect_eof:
                raise RuntimeError("Unexpected EOF from %s executing %s"%(self,line))
        except IOError:
            raise RuntimeError("IO Error from %s executing %s"%(self,line))
        return ("".join(normal_outputs),"".join(error_outputs))

    def _keyboard_interrupt(self):
        """
        TESTS:

        We check that the gap interface behaves correctly after an
        interrupt::

            sage: gap(2)
            2
            sage: import sage.tests.interrupt
            sage: try:
            ...     sage.tests.interrupt.interrupt_after_delay()
            ...     while True: SymmetricGroup(8).conjugacy_classes_subgroups()
            ... except KeyboardInterrupt:
            ...     pass
            Interrupting Gap...
            sage: gap(2)
            2
        """
        print "Interrupting %s..."%self
        self.quit()
        raise KeyboardInterrupt, "Ctrl-c pressed while running %s"%self

    def _eval_line(self, line, allow_use_file=True, wait_for_prompt=True):
        """
        EXAMPLES::

            sage: gap._eval_line('2+2;')
            '4'
        """
        #if line.find('\n') != -1:
        #    raise ValueError, "line must not contain any newlines"
        try:
            if self._expect is None:
                self._start()
            E = self._expect
            #import pdb; pdb.set_trace()
            if allow_use_file and len(line) > self._eval_using_file_cutoff:
                return self._eval_line_using_file(line)
            try:
                (normal, error) = self._execute_line(line, wait_for_prompt=wait_for_prompt,
                                                 expect_eof= (self._quit_string() in line))

                if len(error)> 0:
                    if 'Error, Rebuild completion files!' in error:
                        error += "\nRunning gap_reset_workspace()..."
                        self.quit()
                        gap_reset_workspace()
                    error = error.replace('\r','')
                    raise RuntimeError, "%s produced error output\n%s\n   executing %s"%(self, error,line)
                if len(normal) == 0:
                    return ''

                if isinstance(wait_for_prompt, str) and normal.ends_with(wait_for_prompt):
                    n = len(wait_for_prompt)
                elif normal.endswith(self._prompt):
                    n = len(self._prompt)
                elif normal.endswith(self._continuation_prompt()):
                    n = len(self._continuation_prompt())
                else:
                    n = 0
                out = normal[:-n]
                if len(out) > 0 and out[-1] == "\n":
                    out = out[:-1]
                return out

            except (RuntimeError,),message:
                if 'EOF' in message:
                    print "** %s crashed or quit executing '%s' **"%(self, line)
                    print "Restarting %s and trying again"%self
                    self._start()
                    if line != '':
                        return self._eval_line(line, allow_use_file=allow_use_file)
                    else:
                        return ''
                else:
                    raise RuntimeError, message

        except KeyboardInterrupt:
            self._keyboard_interrupt()
            raise KeyboardInterrupt, "Ctrl-c pressed while running %s"%self

    def unbind(self, var):
        """
        Clear the variable named var.

        EXAMPLES::

            sage: gap.set('x', '2')
            sage: gap.get('x')
            '2'
            sage: gap.unbind('x')
            sage: gap.get('x')
            Traceback (most recent call last):
            ...
            RuntimeError: Gap produced error output
            Variable: 'x' must have a value
            ...
        """
        self.eval('Unbind(%s)'%var)
        self.clear(var)

    def _contains(self, v1, v2):
        """
        EXAMPLES::

            sage: Integers = gap('Integers')
            sage: two = gap(2)
            sage: gap._contains(two.name(), Integers.name())
            True

        ::

            sage: 2 in gap('Integers')
            True
        """
        return self.eval('%s in %s'%(v1,v2)) == "true"

    def _true_symbol(self):
        """
        Returns the symbol for truth in GAP.

        EXAMPLES::

            sage: gap._true_symbol()
            'true'
            sage: gap(2) == gap(2)
            True
        """
        return "true"

    def _false_symbol(self):
        """
        Returns the symbol for falsity in GAP.

        EXAMPLES::

            sage: gap._false_symbol()
            'false'
            sage: gap(2) == gap(3)
            False
        """
        return "false"

    def _equality_symbol(self):
        """
        Returns the symbol for equality in GAP.

        EXAMPLES::

            sage: gap._equality_symbol()
            '='
            sage: gap(2) == gap(3)
            False
            sage: gap(2) == gap(2)
            True
        """
        return "="

    def version(self):
        """
        Returns the version of GAP being used.

        EXAMPLES::

            sage: gap.version()
            '4.4.12'
        """
        return self.eval('VERSION')[1:-1]

    def function_call(self, function, args=None, kwds=None):
        """
        Calls the GAP function with args and kwds.

        EXAMPLES::

            sage: gap.function_call('SymmetricGroup', [5])
            SymmetricGroup( [ 1 .. 5 ] )

        If the GAP function does not return a value, but prints something
        to the screen, then a string of the printed output is returned.

        ::

            sage: s = gap.function_call('Display', [gap.SymmetricGroup(5).CharacterTable()])
            sage: type(s)
            <class 'sage.interfaces.interface.AsciiArtString'>
            sage: s.startswith('CT')
            True
        """
        args, kwds = self._convert_args_kwds(args, kwds)
        self._check_valid_function_name(function)

        #Here we have to do some magic because not all GAP
        #functions return a value.  If you try to store their
        #results to a variable, then GAP will complain.  Thus, before
        #we evaluate the function, we make it so that the marker string
        #is in the 'last' variable in GAP.  If the function returns a
        #value, then that value will be in 'last', otherwise it will
        #be the marker.
        marker = '"__SAGE_LAST__"'
        self.eval('__SAGE_LAST__ := %s;;'%marker)
        res = self.eval("%s(%s)"%(function, ",".join([s.name() for s in args]+
                  ['%s=%s'%(key,value.name()) for key, value in kwds.items()])))
        if self.eval('last') != marker:
            return self.new('last')
        else:
            if res.strip():
                from sage.interfaces.expect import AsciiArtString
                return AsciiArtString(res)

    def trait_names(self):
        """
        EXAMPLES::

            sage: c = gap.trait_names()
            sage: len(c) > 100
            True
            sage: 'Order' in c
            True
        """
        return []

    def get_record_element(self, record, name):
        r"""
        Return the element of a GAP record identified by ``name``.

        INPUT:

        - ``record`` -- a GAP record
        - ``name`` -- str

        OUTPUT:

        - :class:`GapElement`

        EXAMPLES::

            sage: rec = gap('rec( a := 1, b := "2" )')
            sage: gap.get_record_element(rec, 'a')
            1
            sage: gap.get_record_element(rec, 'b')
            2

        TESTS::

            sage: rec = gap('rec( a := 1, b := "2" )')
            sage: type(gap.get_record_element(rec, 'a'))
            <class 'sage.interfaces.gap.GapElement'>
        """
        return self('%s.%s' % (record.name(), name))


class GapElement_generic(ExpectElement):
    r"""
    Generic interface to the GAP3/GAP4 interpreters.

    AUTHORS:

    - William Stein and David Joyner (interface for GAP4)

    - Franco Saliola (Feb 2010): refactored to separate out the generic
      code

    """
    def __repr__(self):
        """
        EXAMPLES::

            sage: gap(2)
            2
        """
        s = ExpectElement.__repr__(self)
        if s.find('must have a value') != -1:
            raise RuntimeError, "An error occurred creating an object in %s from:\n'%s'\n%s"%(self.parent().name(), self._create, s)
        return s

    def bool(self):
        """
        EXAMPLES::

            sage: bool(gap(2))
            True
            sage: gap(0).bool()
            False
            sage: gap('false').bool()
            False
        """
        P = self._check_valid()
        return self != P(0) and repr(self) != 'false'


    def __len__(self):
        """
        EXAMPLES::

            sage: v = gap('[1,2,3]'); v
            [ 1, 2, 3 ]
            sage: len(v)
            3

        len is also called implicitly by if::

            sage: if gap('1+1 = 2'):
            ...    print "1 plus 1 does equal 2"
            1 plus 1 does equal 2

        ::

            sage: if gap('1+1 = 3'):
            ...    print "it is true"
            ... else:
            ...    print "it is false"
            it is false
        """
        P = self.parent()
        if P.eval('%s = true'%self.name()) == 'true':
            return 1
        elif P.eval('%s = false'%self.name()) == 'true':
            return 0
        else:
            return int(self.Length())

    def _matrix_(self, R):
        r"""
        Return matrix over the (Sage) ring R determined by self, where self
        should be a Gap matrix.

        EXAMPLES::

            sage: s = gap("(Z(7)^0)*[[1,2,3],[4,5,6]]"); s
            [ [ Z(7)^0, Z(7)^2, Z(7) ], [ Z(7)^4, Z(7)^5, Z(7)^3 ] ]
            sage: s._matrix_(GF(7))
            [1 2 3]
            [4 5 6]

        ::

            sage: s = gap("[[1,2], [3/4, 5/6]]"); s
            [ [ 1, 2 ], [ 3/4, 5/6 ] ]
            sage: m = s._matrix_(QQ); m
            [  1   2]
            [3/4 5/6]
            sage: parent(m)
            Full MatrixSpace of 2 by 2 dense matrices over Rational Field

        ::

            sage: s = gap('[[Z(16),Z(16)^2],[Z(16)^3,Z(16)]]')
            sage: s._matrix_(GF(16,'a'))
            [  a a^2]
            [a^3   a]
        """
        P = self.parent()
        v = self.DimensionsMat()
        n = int(v[1])
        m = int(v[2])

        from sage.matrix.matrix_space import MatrixSpace
        M = MatrixSpace(R, n, m)
        entries = [[R(self[r,c]) for c in range(1,m+1)] for r in range(1,n+1)]
        return M(entries)

############

class Gap(Gap_generic):
    r"""
    Interface to the GAP interpreter.

    AUTHORS:

    - William Stein and David Joyner
    """
    def __init__(self, max_workspace_size=None,
                 maxread=100000, script_subdirectory=None,
                 use_workspace_cache = True,
                 server=None,
                 server_tmpdir=None,
                 logfile = None):
        """
        EXAMPLES::

            sage: gap == loads(dumps(gap))
            True
        """
        self.__use_workspace_cache = use_workspace_cache
        cmd, self.__make_workspace = gap_command(use_workspace_cache, server is None)
        cmd += " -b -p -T"
        if max_workspace_size != None:
            cmd += " -o %s"%int(max_workspace_size)
        else: # unlimited
            if is_64_bit:
                cmd += " -o 9999G"
            else:
                cmd += " -o 3900m"
        cmd += " %s/extcode/gap/sage.g"%SAGE_DATA
        Expect.__init__(self,
                        name = 'gap',
                        prompt = 'gap> ',
                        command = cmd,
                        maxread = maxread,
                        server = server,
                        server_tmpdir = server_tmpdir,
                        script_subdirectory = script_subdirectory,
                        restart_on_ctrlc = True,
                        verbose_start = False,
                        logfile = logfile,
                        eval_using_file_cutoff=100)
        self.__seq = 0

    def __reduce__(self):
        """
        EXAMPLES::

            sage: gap.__reduce__()
            (<function reduce_load_GAP at 0x...>, ())
            sage: f, args = _
            sage: f(*args)
            Gap
        """
        return reduce_load_GAP, tuple([])

    def _next_var_name(self):
        """
        Returns the next unused variable name.

        EXAMPLES::

            sage: g = Gap()
            sage: g._next_var_name()
            '$sage1'
            sage: g(2)^2
            4
            sage: g._next_var_name()
            '$sage...'
        """
        if len(self._available_vars) != 0:
            v = self._available_vars[0]
            del self._available_vars[0]
            return v
        self.__seq += 1
        return '$sage%s'%self.__seq

    def _start(self):
        """
        EXAMPLES::

            sage: g = Gap()
            sage: g.is_running()
            False
            sage: g._start()
            sage: g.is_running()
            True
            sage: g.quit()
        """
        if self.__use_workspace_cache and not os.path.exists(WORKSPACE):
            gap_reset_workspace()
        global first_try
        n = self._session_number
        try:
            Expect._start(self, "Failed to start GAP.")
        except Exception, msg:
            if self.__use_workspace_cache and first_try:
                print "A workspace appears to have been corrupted... automatically rebuilding (this is harmless)."
                first_try = False
                self._expect = None
                expect.failed_to_start.remove(self.name())
                gap_reset_workspace(verbose=False)
                Expect._start(self, "Failed to start GAP.")
                self._session_number = n
                return
            raise RuntimeError, msg

        if self.__use_workspace_cache and self.__make_workspace:
            self.save_workspace()
        # Now, as self._expect exists, we can compile some useful pattern:
        self._compiled_full_pattern = self._expect.compile_pattern_list(['@p\d+\.','@@','@[A-Z]','@[123456!"#$%&][^+]*\+',
                              '@e','@c','@f','@h','@i','@m','@n','@r','@s\d','@w.*\+','@x','@z'])
        self._compiled_small_pattern = self._expect.compile_pattern_list('@J')

    def _function_class(self):
        """
        Returns the GapFunction class.

        EXAMPLES::

            sage: gap._function_class()
            <class 'sage.interfaces.gap.GapFunction'>

        ::

            sage: type(gap.Order)
            <class 'sage.interfaces.gap.GapFunction'>
        """
        return GapFunction


    def cputime(self, t=None):
        r"""
        Returns the amount of CPU time that the GAP session has used. If
        ``t`` is not None, then it returns the difference
        between the current CPU time and ``t``.

        EXAMPLES::

            sage: t = gap.cputime()
            sage: t  #random
            0.13600000000000001
            sage: gap.Order(gap.SymmetricGroup(5))
            120
            sage: gap.cputime(t)  #random
            0.059999999999999998
        """
        if t is not None:
            return self.cputime() - t
        else:
            self.eval('_r_ := Runtimes();')
            r = sum(eval(self.eval('[_r_.user_time, _r_.system_time, _r_.user_time_children, _r_.system_time_children]')))
            return r/1000.0

    def save_workspace(self):
        r"""
        Save the GAP workspace.

        TESTS:

        We make sure that #9938 (GAP does not start if the path to the GAP
        workspace file contains more than 82 characters) is fixed::

            sage: ORIGINAL_WORKSPACE = sage.interfaces.gap.WORKSPACE
            sage: sage.interfaces.gap.WORKSPACE = SAGE_TMP + "gap" + "0"*(80-len(SAGE_TMP))
            sage: gap = Gap()
            sage: gap('3+2')
            5
            sage: sage.interfaces.gap.WORKSPACE = ORIGINAL_WORKSPACE
        """
        # According to the GAP Reference Manual,
        # [http://www.gap-system.org/Manuals/doc/htm/ref/CHAP003.htm#SSEC011.1]
        # SaveWorkspace can only be used at the main gap> prompt. It cannot
        # be included in the body of a loop or function, or called from a
        # break loop.
        self.eval('SaveWorkspace("%s");'%WORKSPACE, allow_use_file=False)

    # Todo -- this -- but there is a tricky "when does it end" issue!
    # Maybe do via a file somehow?
    def help(self, s, pager=True):
        """
        Print help on a given topic.

        EXAMPLES::

            sage: print gap.help('SymmetricGroup', pager=False)
            Basic Groups _____________________________________________ Group Libraries
            ...
        """
        tmp_to_use = self._local_tmpfile()
        if self.is_remote():
            tmp_to_use = self._remote_tmpfile()
        else:
            tmp_to_use = self._local_tmpfile()
        self.eval('$SAGE.tempfile := "%s";'%tmp_to_use)
        line = Expect.eval(self, "? %s"%s)
        match = re.search("Page from (\d+)", line)
        if match == None:
            print line
        else:
            (sline,) = match.groups()
            if self.is_remote():
                self._get_tmpfile()
            F = open(self._local_tmpfile(),"r")
            if pager:
                page(F.read(), start = int(sline)-1)
            else:
                return F.read()

    def set(self, var, value):
        """
        Set the variable var to the given value.

        EXAMPLES::

            sage: gap.set('x', '2')
            sage: gap.get('x')
            '2'
        """
        cmd = ('%s:=%s;;'%(var,value)).replace('\n','')
        out = self._eval_line(cmd, allow_use_file=True)

    def get(self, var, use_file=False):
        """
        Get the string representation of the variable var.

        EXAMPLES::

            sage: gap.set('x', '2')
            sage: gap.get('x')
            '2'
        """
        if use_file:
            tmp = self._local_tmpfile()
            if os.path.exists(tmp):
                os.unlink(tmp)
            self.eval('PrintTo("%s", %s);'%(tmp,var), strip=False)
            r = open(tmp).read()
            r = r.strip().replace("\\\n","")
            os.unlink(tmp)
            return r
        else:
            return self.eval('Print(%s);'%var, newlines=False)

    def _pre_interact(self):
        """
        EXAMPLES::

            sage: gap._pre_interact()
            sage: gap._post_interact()
        """
        self._eval_line("$SAGE.StartInteract();")

    def _post_interact(self):
        """
        EXAMPLES::

            sage: gap._pre_interact()
            sage: gap._post_interact()
        """
        self._eval_line("$SAGE.StopInteract();")

    def _eval_line_using_file(self, line):
        i = line.find(':=')
        if i != -1:
            j = line.find('"')
            if j >= 0 and j < i:
                i = -1
        if i == -1:
            line0 = 'Print( %s );'%line.rstrip().rstrip(';')
            try:  # this is necessary, since Print requires something as input, and some functions (e.g., Read) return nothing.
                return Expect._eval_line_using_file(self, line0)
            except RuntimeError, msg:
                #if not ("Function call: <func> must return a value" in msg):
                #    raise RuntimeError, msg
                return ''
        return Expect._eval_line_using_file(self, line)

    def console(self):
        """
        Spawn a new GAP command-line session.

        EXAMPLES::

            sage: gap.console() #not tested
            GAP4, Version: 4.4.12 of 17-Dec-2008, powerpc-apple-darwin9.8.0-gcc
            gap>
        """
        gap_console()

    def _object_class(self):
        """
        Returns the GapElement class.

        EXAMPLES::

            sage: gap._object_class()
            <class 'sage.interfaces.gap.GapElement'>
            sage: type(gap(2))
            <class 'sage.interfaces.gap.GapElement'>
        """
        return GapElement

    def _function_element_class(self):
        """
        Returns the GapFunctionElement class.

        EXAMPLES::

            sage: gap._function_element_class()
            <class 'sage.interfaces.gap.GapFunctionElement'>
            sage: type(gap.SymmetricGroup(4).Order)
            <class 'sage.interfaces.gap.GapFunctionElement'>
        """
        return GapFunctionElement
    def trait_names(self):
        """
        EXAMPLES::

            sage: c = gap.trait_names()
            sage: len(c) > 100
            True
            sage: 'Order' in c
            True
        """
        try:
            return self.__trait_names
        except AttributeError:
            self.__trait_names = eval(self.eval('NamesSystemGVars()')) + \
                                 eval(self.eval('NamesUserGVars()'))
        return self.__trait_names


############

def gap_reset_workspace(max_workspace_size=None, verbose=False):
    r"""
    Call this to completely reset the GAP workspace, which is used by
    default when Sage first starts GAP.

    The first time you start GAP from Sage, it saves the startup state
    of GAP in the file

    ::

                $HOME/.sage/gap-workspace


    This is useful, since then subsequent startup of GAP is at least 10
    times as fast. Unfortunately, if you install any new code for GAP,
    it won't be noticed unless you explicitly load it, e.g., with
    gap.load_package("my_package")

    The packages sonata, guava, factint, gapdoc, grape, design, toric,
    and laguna are loaded in all cases before the workspace is saved,
    if they are available.
    """
    if os.path.exists(WORKSPACE):
        os.unlink(WORKSPACE)

    g = Gap(use_workspace_cache=False, max_workspace_size=None)
    for pkg in ['ctbllib', 'sonata', 'guava', 'factint', \
                'gapdoc', 'grape', 'design', \
                'toric', 'laguna', 'braid']:   # NOTE: Do *not* autoload hap - it screws up PolynomialRing(Rationals,2)
        try:
            g.load_package(pkg, verbose=verbose)
        except RuntimeError, msg:
            if verbose:
                print '*** %s'%msg
            pass
    # end for
    g.save_workspace()


# Check to see if we need to auto-regenerate the gap workspace, i.e.,
# if the modification time of the gap link has changed (which signals
# that gap has been somehow upgraded).
if not os.path.exists(WORKSPACE) or os.path.getmtime(WORKSPACE) < os.path.getmtime(GAP_STAMP):
    #print "Automatically updating the cached Gap workspace:"
    #print WORKSPACE
    gap_reset_workspace(verbose=False)

    # Delete all gap workspaces that haven't been used in at least 1
    # week, to avoid needless cruft.  I had an install on sage.math
    # with 90 of these, since I run a lot of different versions of
    # Sage, and it totalled 1.3GB of wasted space!  See trac #4936.
    # We only do this after creating a new workspace, since this cruft
    # issue is only a problem if workspaces get created every so
    # often.  We don't want to have to do this on every startup.
    now = time.time()
    for F in os.listdir(GAP_DIR):
        if F.startswith('workspace'):
            age = now - os.path.getatime(GAP_DIR + '/' + F)
            if age  >= 604800:    # = 168*3600 = 2 weeks in seconds
                os.unlink(GAP_DIR + '/' + F)


class GapElement(GapElement_generic):
    def __getitem__(self, n):
        """
        EXAMPLES::

            sage: a = gap([1,2,3])
            sage: a[1]
            1
        """
        self._check_valid()
        if not isinstance(n, tuple):
            return self.parent().new('%s[%s]'%(self._name, n))
        else:
            return self.parent().new('%s%s'%(self._name, ''.join(['[%s]'%x for x in n])))

    def __reduce__(self):
        """
        Note that GAP elements cannot be pickled.

        EXAMPLES::

            sage: gap(2).__reduce__()
            (<function reduce_load at 0x...>, ())
            sage: f, args = _
            sage: f(*args)
            Traceback (most recent call last):
            ...
            ValueError: The session in which this object was defined is no longer running.
        """
        return reduce_load, ()  # default is an invalid object

    def str(self, use_file=False):
        """
        EXAMPLES::

            sage: print gap(2)
            2
        """
        if use_file:
            P = self._check_valid()
            return P.get(self.name(), use_file=True)
        else:
            return self.__repr__()

    def _latex_(self):
        r"""
        EXAMPLES::

            sage: s = gap("[[1,2], [3/4, 5/6]]")
            sage: latex(s)
            \left(\begin{array}{rr} 1&2\\ 3/4&\frac{5}{6}\\ \end{array}\right)
        """
        P = self._check_valid()
        try:
            s = P.eval('LaTeXObj(%s)'%self.name())
            s = s.replace('\\\\','\\').replace('"','')
            s = s.replace('%\\n',' ')
            return s
        except RuntimeError:
            return str(self)

    def trait_names(self):
        """
        EXAMPLES::

            sage: s5 = gap.SymmetricGroup(5)
            sage: 'Centralizer' in s5.trait_names()
            True
        """
        if '__trait_names' in self.__dict__:
            return self.__trait_names
        P = self.parent()
        v = P.eval('$SAGE.OperationsAdmittingFirstArgument(%s)'%self.name())
        v = v.replace('Tester(','').replace('Setter(','').replace('<Operation ','').replace('>','').replace(')','')
        v = eval(v)
        v = list(set(v))
        v.sort()
        self.__trait_names = v
        return v



class GapFunctionElement(FunctionElement):
    def _sage_doc_(self):
        """
        EXAMPLES::

            sage: print gap(4).SymmetricGroup._sage_doc_()
            Basic Groups _____________________________________________ Group Libraries
            ...
        """
        M = self._obj.parent()
        return M.help(self._name, pager=False)


class GapFunction(ExpectFunction):
    def _sage_doc_(self):
        """
        EXAMPLES::

            sage: print gap.SymmetricGroup._sage_doc_()
            Basic Groups _____________________________________________ Group Libraries
            ...
        """
        M = self._parent
        return M.help(self._name, pager=False)


def is_GapElement(x):
    """
    Returns True if x is a GapElement.

    EXAMPLES::

        sage: from sage.interfaces.gap import is_GapElement
        sage: is_GapElement(gap(2))
        True
        sage: is_GapElement(2)
        False
    """
    return isinstance(x, GapElement)

def gfq_gap_to_sage(x, F):
    """
    INPUT:


    -  ``x`` - gap finite field element

    -  ``F`` - Sage finite field


    OUTPUT: element of F

    EXAMPLES::

        sage: x = gap('Z(13)')
        sage: F = GF(13, 'a')
        sage: F(x)
        2
        sage: F(gap('0*Z(13)'))
        0
        sage: F = GF(13^2, 'a')
        sage: x = gap('Z(13)')
        sage: F(x)
        2
        sage: x = gap('Z(13^2)^3')
        sage: F(x)
        12*a + 11
        sage: F.multiplicative_generator()^3
        12*a + 11

    AUTHOR:

    - David Joyner and William Stein
    """
    from sage.rings.finite_rings.constructor import FiniteField

    s = str(x)
    if s[:2] == '0*':
        return F(0)
    i1 = s.index("(")
    i2 = s.index(")")
    q  = eval(s[i1+1:i2].replace('^','**'))
    if q == F.order():
        K = F
    else:
        K = FiniteField(q, F.variable_name())
    if s.find(')^') == -1:
        e = 1
    else:
        e = int(s[i2+2:])
    if F.degree() == 1:
        g = int(gap.eval('Int(Z(%s))'%q))
    else:
        g = K.multiplicative_generator()
    return F(K(g**e))

def intmod_gap_to_sage(x):
    r"""
    INPUT:

    - x -- Gap integer mod ring element

    EXAMPLES::

        sage: a = gap(Mod(3, 18)); a
        ZmodnZObj( 3, 18 )
        sage: b = sage.interfaces.gap.intmod_gap_to_sage(a); b
        3
        sage: b.parent()
        Ring of integers modulo 18

        sage: a = gap(Mod(3, 17)); a
        Z(17)
        sage: b = sage.interfaces.gap.intmod_gap_to_sage(a); b
        3
        sage: b.parent()
        Ring of integers modulo 17

        sage: a = gap(Mod(0, 17)); a
        0*Z(17)
        sage: b = sage.interfaces.gap.intmod_gap_to_sage(a); b
        0
        sage: b.parent()
        Ring of integers modulo 17

        sage: a = gap(Mod(3, 65537)); a
        ZmodpZObj( 3, 65537 )
        sage: b = sage.interfaces.gap.intmod_gap_to_sage(a); b
        3
        sage: b.parent()
        Ring of integers modulo 65537
    """
    from sage.rings.finite_rings.integer_mod import Mod
    from sage.rings.finite_rings.integer_mod_ring import Zmod
    s = str(x)
    m = re.search(r'Z\(([0-9]*)\)', s)
    if m:
        return gfq_gap_to_sage(x, Zmod(m.group(1)))
    m = re.match(r'Zmod[np]ZObj\( ([0-9]*), ([0-9]*) \)', s)
    if m:
        return Mod(m.group(1), m.group(2))
    raise ValueError, "Unable to convert Gap element '%s'" % s

#############

gap = Gap()

def reduce_load_GAP():
    """
    Returns the GAP interface object defined in sage.interfaces.gap.

    EXAMPLES::

        sage: from sage.interfaces.gap import reduce_load_GAP
        sage: reduce_load_GAP()
        Gap
    """
    return gap

def reduce_load():
    """
    Returns an invalid GAP element. Note that this is the object
    returned when a GAP element is unpickled.

    EXAMPLES::

        sage: from sage.interfaces.gap import reduce_load
        sage: reduce_load()
        Traceback (most recent call last):
        ...
        ValueError: The session in which this object was defined is no longer running.
        sage: loads(dumps(gap(2)))
        Traceback (most recent call last):
        ...
        ValueError: The session in which this object was defined is no longer running.
    """
    return GapElement(None, None)

import os
def gap_console(use_workspace_cache=True):
    """
    Spawn a new GAP command-line session.

    EXAMPLES::

        sage: gap.console() #not tested
        GAP4, Version: 4.4.12 of 17-Dec-2008, powerpc-apple-darwin9.8.0-gcc
        gap>
    """
    cmd, _ = gap_command(use_workspace_cache=use_workspace_cache)
    os.system(cmd)

def gap_version():
    """
    Returns the version of GAP being used.

    EXAMPLES::

        sage: gap_version()
        '4.4.12'
    """
    return gap.eval('VERSION')[1:-1]
