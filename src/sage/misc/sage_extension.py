"""
A Sage extension which adds sage-specific features:

* magics
  - %loadfile
  - %attach
  - %mode (like %maxima, etc.)
* preparsing of input
  - also make runfile and attach magics so that the '%' is optional, but encouraged
* loading Sage library
* running init.sage
* changing prompt to Sage prompt
* Display hook

TESTS:

We test that preparsing is off for ``%runfile``, on for ``%time``::

    sage: import os, re
    sage: from sage.misc.interpreter import get_test_shell
    sage: from sage.misc.misc import tmp_dir
    sage: shell = get_test_shell()
    sage: TMP = tmp_dir()

The temporary directory should have a name of the form
``.../12345/...``, to demonstrate that file names are not
preparsed when calling ``%runfile``. ::

    sage: bool(re.search('/[0-9]+/', TMP))
    True
    sage: tmp = os.path.join(TMP, 'run_cell.py')
    sage: f = open(tmp, 'w'); f.write('a = 2\n'); f.close()
    sage: shell.run_cell('%runfile '+tmp)
    sage: shell.run_cell('a')
    2

In contrast, input to the ``%time`` magic command is preparsed::

    sage: shell.run_cell('%time 594.factor()')
    CPU times: user ...
    Wall time: ...
    2 * 3^3 * 11
"""

from IPython.core.hooks import TryNext
from IPython.core.magic import Magics, magics_class, line_magic
import os
import sys
import sage
import sage.all
from sage.misc.interpreter import preparser
from sage.misc.preparser import preparse

@magics_class
class SageMagics(Magics):

    @line_magic
    def runfile(self, s):
        r"""
        Loads the code contained in the file ``s``. This is designed
        to be used from the command line as ``%runfile /path/to/file``.

        :param s: file to be loaded
        :type s: string

        EXAMPLES::

            sage: import os
            sage: from sage.misc.interpreter import get_test_shell
            sage: from sage.misc.misc import tmp_dir
            sage: shell = get_test_shell()
            sage: tmp = os.path.join(tmp_dir(), 'run_cell.py')
            sage: f = open(tmp, 'w'); f.write('a = 2\n'); f.close()
            sage: shell.run_cell('%runfile '+tmp)
            sage: shell.run_cell('a')
            2
        """
        from sage.misc.preparser import load_wrap
        return self.shell.ex(load_wrap(s, attach=False))

    @line_magic
    def attach(self, s):
        r"""
        Attaches the code contained in the file ``s``. This is
        designed to be used from the command line as
        ``%attach /path/to/file``.

        :param s: file to be attached
        :type s: string

        EXAMPLES::

            sage: import os
            sage: from sage.misc.interpreter import get_test_shell
            sage: shell = get_test_shell()
            sage: tmp = os.path.normpath(os.path.join(SAGE_TMP, 'run_cell.py'))
            sage: f = open(tmp, 'w'); f.write('a = 2\n'); f.close()
            sage: shell.run_cell('%attach ' + tmp)
            sage: shell.run_cell('a')
            2
            sage: import time; time.sleep(1)
            sage: f = open(tmp, 'w'); f.write('a = 3\n'); f.close()
            sage: shell.run_cell('a')
            3
            sage: shell.run_cell('detach(%r)'%tmp)
            sage: shell.run_cell('attached_files()')
            []
            sage: os.remove(tmp)
        """
        from sage.misc.preparser import load_wrap
        return self.shell.ex(load_wrap(s, attach=True))

    def pre_run_code_hook(self, ip):
        """
        Load the attached files (if needed) before running some code.

        The examples are from the %attach magic.

        EXAMPLES::

            sage: import os
            sage: from sage.misc.interpreter import get_test_shell
            sage: shell = get_test_shell()
            sage: tmp = os.path.normpath(os.path.join(SAGE_TMP, 'run_cell.py'))
            sage: f = open(tmp, 'w'); f.write('a = 2\n'); f.close()
            sage: shell.run_cell('%attach ' + tmp)
            sage: shell.run_cell('a')
            2
            sage: import time; time.sleep(1)
            sage: f = open(tmp, 'w'); f.write('a = 3\n'); f.close()
            sage: shell.run_cell('a')
            3
            sage: shell.run_cell('detach(%r)'%tmp)
            sage: shell.run_cell('attached_files()')
            []
            sage: os.remove(tmp)
        """
        from sage.misc.preparser import load_attached
        s=load_attached()
        if s:
            self.shell.ex(s)
        raise TryNext

    @line_magic
    def iload(self, s):
        """
        A magic command to interactively load a file as in MAGMA.

        :param s: the file to be interactively loaded
        :type s: string

        .. note::

            Currently, this cannot be completely doctested as it
            relies on :func:`raw_input`.

        EXAMPLES::

            sage: ip = get_ipython()           # not tested: works only in interactive shell
            sage: ip.magic_iload('/dev/null')  # not tested: works only in interactive shell
            Interactively loading "/dev/null"  # not tested: works only in interactive shell
        """
        try:
            name = str(eval(s))
        except Exception:
            name = s.strip()

        try:
            F = open(name)
        except IOError:
            raise ImportError, 'could not open file "%s"'%name


        shell = self.shell

        #We need to update the execution count so that the history for the
        #iload command and the history for the first line of the loaded
        #file are not written to the history database with the same line
        #number (execution count).  This happens since the execution count
        #is updated only after the magic command is run.
        shell.execution_count += 1

        print 'Interactively loading "%s"'%name

        # The following code is base on IPython's
        # InteractiveShell.interact,
        more = False
        for line in F.readlines():
            prompt = shell.prompt_manager.render('in' if not more else 'in2', color=True)
            raw_input(prompt.encode('utf-8') + line.rstrip())

            shell.input_splitter.push(line)
            more = shell.input_splitter.push_accepts_more()
            if not more:
                source, source_raw = shell.input_splitter.source_raw_reset()
                shell.run_cell(source_raw, store_history=True)

from IPython.core.formatters import PlainTextFormatter
class SagePlainTextFormatter(PlainTextFormatter):
    """
    A replacement for the plain text formatter which correctly print lists
    of matrices.

    EXAMPLES::

        sage: from sage.misc.interpreter import get_test_shell
        sage: shell = get_test_shell()
        sage: shell.display_formatter.formatters['text/plain']
        <...sage_extension.SagePlainTextFormatter object at 0x...>
        sage: shell.run_cell('a = identity_matrix(ZZ, 2); [a,a]')
        [
        [1 0]  [1 0]
        [0 1], [0 1]
        ]
    """
    def __call__(self, obj):
        r"""
        Computes the format data of ``result``.  If the
        :func:`sage.misc.displayhook.format_obj` writes a string, then
        we override IPython's :class:`DisplayHook` formatting.

        EXAMPLES::

            sage: from sage.misc.interpreter import get_test_shell
            sage: shell = get_test_shell()
            sage: shell.display_formatter.formatters['text/plain']
            <...sage_extension.SagePlainTextFormatter object at 0x...>
            sage: shell.displayhook.compute_format_data(2)
            {u'text/plain': '2'}
            sage: a = identity_matrix(ZZ, 2)
            sage: shell.displayhook.compute_format_data([a,a])
            {u'text/plain': '[\n[1 0]  [1 0]\n[0 1], [0 1]\n]'}
        """
        import sage
        from sage.misc.displayhook import format_obj
        s = format_obj(obj)
        if s is None:
            s = super(SagePlainTextFormatter, self).__call__(obj)
        return s


# SageInputSplitter:
#  Hopefully most or all of this code can go away when
#  https://github.com/ipython/ipython/issues/2293 is resolved
#  apparently we will have stateful transformations then.
#  see also https://github.com/ipython/ipython/pull/2402
from IPython.core.inputsplitter import (transform_ipy_prompt, transform_classic_prompt,
                                        transform_help_end, transform_escaped,
                                        transform_assign_system, transform_assign_magic,
                                        cast_unicode,
                                        IPythonInputSplitter)

def first_arg(f):
    def tm(arg1, arg2):
        return f(arg1)
    return tm

class SageInputSplitter(IPythonInputSplitter):
    """
    We override the input splitter for two reasons:

    1. to make the list of transforms a class attribute that can be modified

    2. to pass the line number to transforms (we strip the line number off for IPython transforms)
    """

    # List of input transforms to apply
    transforms = map(first_arg, [transform_ipy_prompt, transform_classic_prompt,
                                 transform_help_end, transform_escaped,
                                 transform_assign_system, transform_assign_magic])

    # a direct copy of the IPython splitter, except that the
    # transforms are called with the line numbers, and the transforms come from the class attribute
    # and except that we add a .startswith('@') in the test to see if we should transform a line
    # (see http://mail.scipy.org/pipermail/ipython-dev/2012-September/010329.html; the current behavior
    # doesn't run the preparser on a 'def' line following an decorator.
    def push(self, lines):
        """Push one or more lines of IPython input.

        This stores the given lines and returns a status code indicating
        whether the code forms a complete Python block or not, after processing
        all input lines for special IPython syntax.

        Any exceptions generated in compilation are swallowed, but if an
        exception was produced, the method returns True.

        Parameters
        ----------
        lines : string
          One or more lines of Python input.

        Returns
        -------
        is_complete : boolean
          True if the current input source (the result of the current input
        plus prior inputs) forms a complete Python execution block.  Note that
        this value is also stored as a private attribute (_is_complete), so it
        can be queried at any time.
        """
        if not lines:
            return super(IPythonInputSplitter, self).push(lines)

        # We must ensure all input is pure unicode
        lines = cast_unicode(lines, self.encoding)

        # If the entire input block is a cell magic, return after handling it
        # as the rest of the transformation logic should be skipped.
        if lines.startswith('%%') and not \
          (len(lines.splitlines()) == 1 and lines.strip().endswith('?')):
            return self._handle_cell_magic(lines)

        # In line mode, a cell magic can arrive in separate pieces
        if self.input_mode == 'line' and self.processing_cell_magic:
            return self._line_mode_cell_append(lines)

        # The rest of the processing is for 'normal' content, i.e. IPython
        # source that we process through our transformations pipeline.
        lines_list = lines.splitlines()

        # Transform logic
        #
        # We only apply the line transformers to the input if we have either no
        # input yet, or complete input, or if the last line of the buffer ends
        # with ':' (opening an indented block).  This prevents the accidental
        # transformation of escapes inside multiline expressions like
        # triple-quoted strings or parenthesized expressions.
        #
        # The last heuristic, while ugly, ensures that the first line of an
        # indented block is correctly transformed.
        #
        # FIXME: try to find a cleaner approach for this last bit.

        # If we were in 'block' mode, since we're going to pump the parent
        # class by hand line by line, we need to temporarily switch out to
        # 'line' mode, do a single manual reset and then feed the lines one
        # by one.  Note that this only matters if the input has more than one
        # line.
        changed_input_mode = False

        if self.input_mode == 'cell':
            self.reset()
            changed_input_mode = True
            saved_input_mode = 'cell'
            self.input_mode = 'line'

        # Store raw source before applying any transformations to it.  Note
        # that this must be done *after* the reset() call that would otherwise
        # flush the buffer.
        self._store(lines, self._buffer_raw, 'source_raw')

        try:
            push = super(IPythonInputSplitter, self).push
            buf = self._buffer
            for line in lines_list:
                line_number = len(buf)
                if (self._is_complete or not buf or
                    buf[-1].rstrip().endswith((':', ',')) or buf[-1].lstrip().startswith('@')):
                    for f in self.transforms:
                        line = f(line, line_number)
                out = push(line)
        finally:
            if changed_input_mode:
                self.input_mode = saved_input_mode
        return out

# END SageIPythonInputSplitter
#
#


class SageCustomizations(object):
    startup_code = """from sage.all_cmdline import *
from sage.misc.interpreter import sage_prompt
"""

    def __init__(self, shell=None):
        """
        Initialize the Sage plugin.
        """
        self.shell = shell
        self.auto_magics = SageMagics(shell)
        shell.register_magics(self.auto_magics)
        shell.set_hook('pre_run_code_hook', self.auto_magics.pre_run_code_hook)
        shell.display_formatter.formatters['text/plain'] = SagePlainTextFormatter(config=shell.config)
        from sage.misc.edit_module import edit_devel
        self.shell.set_hook('editor', edit_devel)
        self.init_inspector()
        self.init_line_transforms()
        self.register_interface_magics()

        # right now, the shutdown hook calling quit_sage() doesn't
        # work when we run doctests that involve creating test shells.
        # The test run segfaults right when it exits, complaining
        # about a bad memory access in the pari_close() function.
        #self.set_quit_hook()

        self.print_branch()

        # These are things I'm not sure that we need to do anymore
        #self.deprecated()


        if os.environ.get('SAGE_IMPORTALL', 'yes') != 'yes':
            return

        self.init_environment()

    def register_interface_magics(self):
        """Register magics for each of the Sage interfaces"""
        interfaces = sorted([ obj.name()
                              for obj in sage.interfaces.all.__dict__.values()
                              if isinstance(obj, sage.interfaces.interface.Interface) ])
        for name in interfaces:
            def tmp(line,name=name):
                self.shell.run_cell('%s.interact()'%name)
            tmp.__doc__="Interact with %s"%name
            self.shell.register_magic_function(tmp, magic_name=name)


    def set_quit_hook(self):
        """
        Set the exit hook to cleanly exit Sage.  This does not work in all cases right now.
        """
        def quit(shell):
            import sage
            sage.all.quit_sage()
        self.shell.set_hook('shutdown_hook', quit)

    def print_branch(self):
        """
        Print the branch we are on currently
        """
        from sage.misc.misc import branch_current_hg_notice, branch_current_hg
        branch = branch_current_hg_notice(branch_current_hg())
        if branch and not self.shell.test_shell:
            print branch

    def init_environment(self):
        """
        Set up Sage command-line environment
        """
        try:
            self.shell.run_cell('from sage.all import Integer, RealNumber')
        except Exception:
            import traceback
            print "Error importing the Sage library"
            traceback.print_exc()
            print
            print "To debug this, you can run:"
            print 'sage -ipython -i -c "import sage.all"'
            print 'and then type "%debug" to enter the interactive debugger'
            sys.exit(1)
        self.shell.run_cell(self.startup_code)
        self.run_init()


    def run_init(self):
        """
        Run Sage's initial startup file.
        """
        startup_file = os.environ.get('SAGE_STARTUP_FILE', '')
        if os.path.exists(startup_file):
            self.shell.run_cell('%%run %r'%startup_file)

    def init_inspector(self):
        # Ideally, these would just be methods of the Inspector class
        # that we could override; however, IPython looks them up in
        # the global :class:`IPython.core.oinspect` module namespace.
        # Thus, we have to monkey-patch.
        from sage.misc import sagedoc, sageinspect
        import IPython.core.oinspect
        IPython.core.oinspect.getdoc = sageinspect.sage_getdoc #sagedoc.my_getdoc
        IPython.core.oinspect.getsource = sagedoc.my_getsource
        IPython.core.oinspect.getargspec = sageinspect.sage_getargspec

    def init_line_transforms(self):
        """
        Set up transforms (like the preparser).
        """
        self.shell.input_splitter = SageInputSplitter()
        import sage
        import sage.all
        from sage.misc.interpreter import (SagePromptDedenter, SagePromptTransformer,
                                           MagicTransformer, SagePreparseTransformer)

        self.shell.input_splitter.transforms = [SagePromptDedenter(),
                                                SagePromptTransformer(),
                                                MagicTransformer(),
                                                SagePreparseTransformer()] + self.shell.input_splitter.transforms

        preparser(True)

    def deprecated(self):
        """
        These are things I don't think we need to do anymore; are they used?
        """
        # I'm not sure this is ever needed; when would this not be ''?
        if sys.path[0]!='':
            sys.path.insert(0, '')

# from http://stackoverflow.com/questions/4103773/efficient-way-of-having-a-function-only-execute-once-in-a-loop
from functools import wraps
def run_once(f):
    """Runs a function (successfully) only once.

    The running can be reset by setting the `has_run` attribute to False
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            result = f(*args, **kwargs)
            wrapper.has_run = True
            return result
    wrapper.has_run = False
    return wrapper

@run_once
def load_ipython_extension(ip):
    """Load the extension in IPython."""
    # this modifies ip
    SageCustomizations(shell=ip)
