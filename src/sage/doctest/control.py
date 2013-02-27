"""
This module controls the various classes involved in doctesting.

AUTHORS:

- David Roe (2012-03-27) -- initial version, based on Robert Bradshaw's code.
"""

#*****************************************************************************
#       Copyright (C) 2012 David Roe <roed.math@gmail.com>
#                          Robert Bradshaw <robertwb@gmail.com>
#                          William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import random, os, sys, time, json, re, types
import sage.misc.flatten
from sage.structure.sage_object import SageObject
from sage.misc.misc import DOT_SAGE

from sources import FileDocTestSource, DictAsObject
from forker import DocTestDispatcher
from reporting import DocTestReporter
from util import NestedName, Timer, count_noun, dict_difference


class DocTestDefaults(SageObject):
    """
    This class is used for doctesting the Sage doctest module.

    It fills in attributes to be the same as the defaults defined in
    ``SAGE_ROOT/local/bin/sage-runtests``, expect for a few places,
    which is mostly to make doctesting more predictable.

    EXAMPLES::

        sage: from sage.doctest.control import DocTestDefaults
        sage: D = DocTestDefaults()
        sage: D
        DocTestDefaults()
        sage: D.timeout
        -1

    Keyword arguments become attributes::

        sage: D = DocTestDefaults(timeout=100)
        sage: D
        DocTestDefaults(timeout=100)
        sage: D.timeout
        100
    """
    def __init__(self, **kwds):
        """
        Edit these parameters after creating an instance.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults
            sage: D = DocTestDefaults(); D.optional
            'sage'
        """
        self.nthreads = 1
        self.serial = False
        self.timeout = -1
        self.all = False
        self.logfile = None
        self.sagenb = False
        self.long = False
        self.warn_long = None
        self.optional = "sage"
        self.randorder = None
        self.global_iterations = 1  # sage-runtests default is 0
        self.file_iterations = 1    # sage-runtests default is 0
        self.initial = False
        self.force_lib = False
        self.abspath = True         # sage-runtests default is False
        self.verbose = False
        self.debug = False
        self.gdb = False
        self.valgrind = False
        self.massif = False
        self.cachegrind = False
        self.omega = False
        self.failed = False
        self.new = False
        # We don't want to use the real stats file by default so that
        # we don't overwrite timings for the actual running doctests.
        self.stats_path = os.path.join(DOT_SAGE, "timings_dt_test.json")
        if not os.path.exists(self.stats_path):
            with open(self.stats_path, "w") as stats_file:
                json.dump({},stats_file)
        self.__dict__.update(kwds)

    def _repr_(self):
        """
        Return the print representation.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults
            sage: DocTestDefaults(timeout=100, foobar="hello")
            DocTestDefaults(foobar='hello', timeout=100)
        """
        s = "DocTestDefaults("
        for k in sorted(dict_difference(self.__dict__, DocTestDefaults().__dict__).keys()):
            if s[-1] != "(":
                s += ", "
            s += str(k) + "=" + repr(getattr(self,k))
        s += ")"
        return s


class DocTestController(SageObject):
    """
    This class controls doctesting of files.

    After creating it with appropriate options, call the :meth:run() method to run the doctests.
    """
    def __init__(self, options, args):
        """
        Initialization.

        INPUT:

        - options -- either options generated from the command line by SAGE_ROOT/local/bin/sage-runtests
                     or a DocTestDefaults object (possibly with some entries modified)
        - args -- a list of filenames to doctest

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DC = DocTestController(DocTestDefaults(), [])
            sage: DC
            DocTest Controller
        """
        # First we modify options to take environment variables into
        # account and check compatibility of the user's specified
        # options.
        if options.timeout < 0:
            if options.gdb or options.debug:
                # Interactive debuggers: "infinite" timeout
                options.timeout = 0
            elif options.valgrind or options.massif or options.cachegrind or options.omega:
                # Non-interactive debuggers: 48 hours
                options.timeout = os.getenv('SAGE_TIMEOUT_VALGRIND', 48 * 60 * 60)
            elif options.long:
                options.timeout = os.getenv('SAGE_TIMEOUT_LONG', 30 * 60)
            else:
                options.timeout = os.getenv('SAGE_TIMEOUT', 5 * 60)
        if options.nthreads == 0:
            options.nthreads = int(os.getenv('SAGE_NUM_THREADS_PARALLEL',1))
        if options.failed and not (args or options.new or options.sagenb):
            # If the user doesn't specify any files then we rerun all failed files.
            options.all = True
        if options.global_iterations == 0:
            options.global_iterations = int(os.environ.get('SAGE_TEST_GLOBAL_ITER', 1))
        if options.file_iterations == 0:
            options.file_iterations = int(os.environ.get('SAGE_TEST_ITER', 1))
        if options.debug and options.nthreads > 1:
            print("Debugging requires single-threaded operation, setting number of threads to 1.")
            options.nthreads = 1
        if options.serial:
            options.nthreads = 1

        self.options = options
        self.files = args
        if options.all and options.logfile is None:
            options.logfile = os.path.join(os.environ['SAGE_TESTDIR'], 'test.log')
        if options.logfile:
            try:
                self.logfile = open(options.logfile, 'a')
            except IOError:
                print "Unable to open logfile at %s\nProceeding without logging."%(options.logfile)
                self.logfile = None
        else:
            self.logfile = None
        self.stats = {}
        self.load_stats(options.stats_path)

    def _repr_(self):
        """
        String representation.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DC = DocTestController(DocTestDefaults(), [])
            sage: repr(DC) # indirect doctest
            'DocTest Controller'
        """
        return "DocTest Controller"

    def load_stats(self, filename):
        """
        Load stats from the most recent run(s).

        Stats are stored as a JSON file, and include information on
        which files failed tests and the walltime used for execution
        of the doctests.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DC = DocTestController(DocTestDefaults(), [])
            sage: import json
            sage: filename = tmp_filename()
            sage: with open(filename, 'w') as stats_file:
            ...       json.dump({'sage.doctest.control':{u'walltime':1.0r}}, stats_file)
            sage: DC.load_stats(filename)
            sage: DC.stats['sage.doctest.control']
            {u'walltime': 1.0}
        """
        try:
            with open(filename) as stats_file:
                self.stats.update(json.load(stats_file))
        except StandardError:
            self.log("Error loading stats from %s"%filename)

    def save_stats(self, filename):
        """
        Save stats from the most recent run as a JSON file.

        WARNING: This function overwrites the file.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DC = DocTestController(DocTestDefaults(), [])
            sage: DC.stats['sage.doctest.control'] = {u'walltime':1.0r}
            sage: filename = tmp_filename()
            sage: DC.save_stats(filename)
            sage: import json
            sage: D = json.load(open(filename))
            sage: D['sage.doctest.control']
            {u'walltime': 1.0}
        """
        with open(filename, 'w') as stats_file:
            json.dump(self.stats, stats_file)

    def log(self, s, end="\n"):
        """
        Logs the string ``s + end`` (where ``end`` is a newline by default)
        to the logfile and prints it to the standard output.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DD = DocTestDefaults(logfile=tmp_filename())
            sage: DC = DocTestController(DD, [])
            sage: DC.log("hello world")
            hello world
            sage: DC.logfile.close()
            sage: with open(DD.logfile) as logger: print logger.read()
            hello world

        """
        s += end
        if self.logfile is not None:
            self.logfile.write(s)
        sys.stdout.write(s)

    def test_safe_directory(self, dir=None):
        """
        Test that the given directory is safe to run Python code from.

        We use the check added to Python for this, which gives a
        warning when the current directory is considered unsafe.  We promote
        this warning to an error with ``-Werror``.  See
        ``sage/tests/cmdline.py`` for a doctest that this works, see
        also :trac:`13579`.

        TESTS::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DD = DocTestDefaults()
            sage: DC = DocTestController(DD, [])
            sage: DC.test_safe_directory()
            sage: d = os.path.join(tmp_dir(), "test")
            sage: os.mkdir(d)
            sage: os.chmod(d, 0o777)
            sage: DC.test_safe_directory(d)
            Traceback (most recent call last):
            ...
            RuntimeError: refusing to run doctests...
        """
        import subprocess
        with open(os.devnull, 'w') as dev_null:
            if subprocess.call(['python', '-Werror', '-c', ''],
                    stdout=dev_null, stderr=dev_null, cwd=dir) != 0:
                raise RuntimeError(
                      "refusing to run doctests from the current "
                      "directory '{}' since untrusted users could put files in "
                      "this directory, making it unsafe to run Sage code from"
                      .format(os.getcwd()))

    def create_run_id(self):
        """
        Creates the run id.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DC = DocTestController(DocTestDefaults(), [])
            sage: DC.create_run_id()
            Running doctests with ID ...
        """
        self.run_id = time.strftime('%Y-%m-%d-%H-%M-%S-') + "%08x" % random.getrandbits(32)
        from sage.version import version
        self.log("Running doctests with ID %s."%self.run_id)

    def add_files(self):
        """
        Checks for the flags '--all', '--new' and '--sagenb'.

        For each one present, this function adds the appropriate directories and files to the todo list.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: import os
            sage: log_location = os.path.join(SAGE_TMP, 'control_dt_log.log')
            sage: DD = DocTestDefaults(all=True, logfile=log_location)
            sage: DC = DocTestController(DD, [])
            sage: DC.add_files()
            Doctesting entire Sage library.
            sage: os.path.join(os.environ['SAGE_ROOT'], 'devel', 'sage', 'sage') in DC.files
            True

        ::

            sage: DD = DocTestDefaults(new = True)
            sage: DC = DocTestController(DD, [])
            sage: DC.add_files()
            Doctesting files changed since last HG commit.
            sage: len(DC.files) == len([L for L in hg_sage('status', interactive=False, debug=False)[0].split('\n') if len(L.split()) ==2 and L.split()[0] in ['M','A']])
            True

        ::

            sage: DD = DocTestDefaults(sagenb = True)
            sage: DC = DocTestController(DD, [])
            sage: DC.add_files()
            Doctesting the Sage notebook.
            sage: DC.files[0][-6:]
            'sagenb'
        """
        opj = os.path.join
        SAGE_ROOT = os.environ['SAGE_ROOT']
        base = opj(SAGE_ROOT, 'devel', 'sage')
        if self.options.all:
            self.log("Doctesting entire Sage library.")
            from glob import glob
            self.files.append(opj(base, 'sage'))
            self.files.append(opj(base, 'doc', 'common'))
            self.files.extend(glob(opj(base, 'doc', '[a-z][a-z]')))
            self.options.sagenb = True
        elif self.options.new:
            self.log("Doctesting files changed since last HG commit.")
            import sage.all_cmdline
            from sage.misc.hg import hg_sage
            for X in hg_sage('status', interactive=False, debug=False)[0].split('\n'):
                tup = X.split()
                if len(tup) != 2: continue
                c, filename = tup
                if c in ['M','A']:
                    filename = opj(os.environ['SAGE_ROOT'], 'devel', 'sage', filename)
                    self.files.append(filename)
        if self.options.sagenb:
            if not self.options.all:
                self.log("Doctesting the Sage notebook.")
            from pkg_resources import Requirement, working_set
            sagenb_loc = working_set.find(Requirement.parse('sagenb')).location
            self.files.append(opj(sagenb_loc, 'sagenb'))

    def expand_files_into_sources(self):
        """
        Expands ``self.files``, which may include directories, into a
        list of :class:`sage.doctest.FileDocTestSource`

        This function also handles the optional command line option.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: import os
            sage: dirname = os.path.join(os.environ['SAGE_ROOT'], 'devel', 'sage', 'sage', 'doctest')
            sage: DD = DocTestDefaults(optional='all')
            sage: DC = DocTestController(DD, [dirname])
            sage: DC.expand_files_into_sources()
            sage: len(DC.sources)
            9
            sage: DC.sources[0].optional
            True

        ::

            sage: DD = DocTestDefaults(optional='magma,guava')
            sage: DC = DocTestController(DD, [dirname])
            sage: DC.expand_files_into_sources()
            sage: sorted(list(DC.sources[0].optional))
            ['guava', 'magma']
        """
        def skipdir(dirname):
            if os.path.exists(os.path.join(dirname, "nodoctest.py")):
                return True
            # Workaround for https://github.com/sagemath/sagenb/pull/84
            if dirname.endswith(os.path.join(os.sep, 'sagenb', 'data')):
                return True
            return False
        def skipfile(filename):
            base, ext = os.path.splitext(filename)
            if ext not in ('.py', '.pyx', '.pxi', '.sage', '.spyx', '.rst', '.tex'):
                return True
            with open(filename) as F:
                return 'nodoctest' in F.read(50)
        def expand():
            for path in self.files:
                if os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for dir in list(dirs):
                            if dir[0] == "." or skipdir(os.path.join(root,dir)):
                                dirs.remove(dir)
                        for file in files:
                            if not skipfile(os.path.join(root,file)):
                                yield os.path.join(root, file)
                else:
                    # the user input this file explicitly, so we don't skip it
                    yield path
        if self.options.optional == 'all':
            optionals = True
        else:
            optionals = set(self.options.optional.lower().split(','))
        self.sources = [FileDocTestSource(path, self.options.force_lib, long=self.options.long, optional=optionals, randorder=self.options.randorder, useabspath=self.options.abspath) for path in expand()]

    def filter_sources(self):
        """

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: import os
            sage: dirname = os.path.join(os.environ['SAGE_ROOT'], 'devel', 'sage', 'sage', 'doctest')
            sage: DD = DocTestDefaults(failed=True)
            sage: DC = DocTestController(DD, [dirname])
            sage: DC.expand_files_into_sources()
            sage: for i, source in enumerate(DC.sources):
            ...       DC.stats[source.basename] = {'walltime': 0.1*(i+1)}
            sage: DC.stats['sage.doctest.control'] = {'failed':True,'walltime':1.0}
            sage: DC.filter_sources()
            Only doctesting files that failed last test.
            sage: len(DC.sources)
            1
        """
        # Filter the sources to only include those with failing doctests if the --failed option is passed
        if self.options.failed:
            self.log("Only doctesting files that failed last test.")
            def is_failure(source):
                basename = source.basename
                return basename not in self.stats or self.stats[basename].get('failed')
            self.sources = filter(is_failure, self.sources)

    def sort_sources(self):
        """
        This function sorts the sources so that slower doctests are run first.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: import os
            sage: dirname = os.path.join(os.environ['SAGE_ROOT'], 'devel', 'sage', 'sage', 'doctest')
            sage: DD = DocTestDefaults(nthreads=2)
            sage: DC = DocTestController(DD, [dirname])
            sage: DC.expand_files_into_sources()
            sage: DC.sources.sort(key=lambda s:s.basename)
            sage: for i, source in enumerate(DC.sources):
            ...       DC.stats[source.basename] = {'walltime': 0.1*(i+1)}
            sage: DC.sort_sources()
            Sorting sources by runtime so that slower doctests are run first....
            sage: print "\n".join([source.basename for source in DC.sources])
            sage.doctest.util
            sage.doctest.test
            sage.doctest.sources
            sage.doctest.reporting
            sage.doctest.parsing
            sage.doctest.forker
            sage.doctest.control
            sage.doctest.all
            sage.doctest
        """
        if self.options.nthreads > 1 and len(self.sources) > self.options.nthreads:
            self.log("Sorting sources by runtime so that slower doctests are run first....")
            default = dict(walltime=0)
            def sort_key(source):
                basename = source.basename
                return -self.stats.get(basename, default).get('walltime'), basename
            self.sources = [x[1] for x in sorted((sort_key(source), source) for source in self.sources)]

    def run_doctests(self):
        """
        Actually runs the doctests.

        This function is called by :meth:run().

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: import os
            sage: dirname = os.path.join(os.environ['SAGE_ROOT'], 'devel', 'sage', 'sage', 'rings', 'homset.py')
            sage: DD = DocTestDefaults()
            sage: DC = DocTestController(DD, [dirname])
            sage: DC.expand_files_into_sources()
            sage: DC.run_doctests()
            Doctesting 1 file.
            sage -t .../sage/rings/homset.py
                [... tests, ... s]
            ------------------------------------------------------------------------
            All tests passed!
            ------------------------------------------------------------------------
            Total time for all tests: ... seconds
                cpu time: ... seconds
                cumulative wall time: ... seconds

        """
        nfiles = 0
        nother = 0
        for F in self.sources:
            if isinstance(F, FileDocTestSource):
                nfiles += 1
            else:
                nother += 1
        if self.sources:
            filestr = ", ".join(([count_noun(nfiles, "file")] if nfiles else []) +
                                ([count_noun(nother, "other source")] if nother else []))
            if self.options.nthreads > len(self.sources):
                self.options.nthreads = len(self.sources)
            threads = " using %s threads"%(self.options.nthreads) if self.options.nthreads > 1 else ""
            iterations = []
            if self.options.global_iterations > 1:
                iterations.append("%s global iterations"%(self.options.global_iterations))
            if self.options.file_iterations > 1:
                iterations.append("%s file iterations"%(self.options.file_iterations))
            iterations = ", ".join(iterations)
            if iterations:
                iterations = " (%s)"%(iterations)
            self.log("Doctesting %s%s%s."%(filestr, threads, iterations))
            self.reporter = DocTestReporter(self)
            self.dispatcher = DocTestDispatcher(self)
            N = self.options.global_iterations
            for it in range(N):
                try:
                    self.timer = Timer().start()
                    self.dispatcher.dispatch()
                except KeyboardInterrupt:
                    it = N - 1
                    break
                finally:
                    self.timer.stop()
                    self.reporter.finalize()
                    self.cleanup(it == N - 1)
        else:
            self.log("No files to doctest")
            self.reporter = DictAsObject(dict(error_status=0))

    def cleanup(self, final=True):
        """
        Runs cleanup activities after actually running doctests.

        In particular, saves the stats to disk and closes the logfile.

        INPUT:

        - ``final`` -- whether to close the logfile

        EXAMPLES::

             sage: from sage.doctest.control import DocTestDefaults, DocTestController
             sage: import os
             sage: dirname = os.path.join(os.environ['SAGE_ROOT'], 'devel', 'sage', 'sage', 'rings', 'infinity.py')
             sage: DD = DocTestDefaults()

             sage: DC = DocTestController(DD, [dirname])
             sage: DC.expand_files_into_sources()
             sage: DC.sources.sort(key=lambda s:s.basename)

             sage: for i, source in enumerate(DC.sources):
             ....:     DC.stats[source.basename] = {'walltime': 0.1*(i+1)}
             ....:

             sage: DC.run()
             Running doctests with ID ...
             Doctesting 1 file.
             sage -t .../rings/infinity.py
                 [... tests, ... s]
             ------------------------------------------------------------------------
             All tests passed!
             ------------------------------------------------------------------------
             Total time for all tests: ... seconds
                 cpu time: ... seconds
                 cumulative wall time: ... seconds
             0
             sage: DC.cleanup()
        """
        self.stats.update(self.reporter.stats)
        self.save_stats(self.options.stats_path)
        # Close the logfile
        if final and self.logfile is not None:
            self.logfile.close()
            self.logfile = None

    def _assemble_cmd(self):
        """
        Assembles a shell command used in running tests under gdb or valgrind.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DC = DocTestController(DocTestDefaults(), ["hello_world.py"])
            sage: print DC._assemble_cmd()
            python "$SAGE_LOCAL/bin/sage-runtests" --serial --timeout=300 hello_world.py
        """
        cmd = '''python "%s" --serial '''%(os.path.join("$SAGE_LOCAL","bin","sage-runtests"))
        opt = dict_difference(self.options.__dict__, DocTestDefaults().__dict__)
        for o in ("all", "sagenb"):
            if o in opt:
                raise ValueError("You cannot run gdb/valgrind on the whole sage%s library"%("" if o == "all" else "nb"))
        for o in ("all", "sagenb", "long", "force_lib", "verbose", "failed", "new"):
            if o in opt:
                cmd += "--%s "%o
        for o in ("timeout", "optional", "randorder", "stats_path"):
            if o in opt:
                cmd += "--%s=%s "%(o, opt[o])
        return cmd + " ".join(self.files)

    def run_val_gdb(self, testing=False):
        """
        Spawns a subprocess to run tests under the control of gdb or valgrind.

        INPUT:

        - ``testing`` -- boolean; if True then the command to be run
          will be printed rather than a subprocess started.

        EXAMPLES:

        Note that the command lines include unexpanded environment
        variables. It is safer to let the shell expand them than to
        expand them here and risk insufficient quoting. ::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: DD = DocTestDefaults(gdb=True)
            sage: DC = DocTestController(DD, ["hello_world.py"])
            sage: DC.run_val_gdb(testing=True)
            exec gdb -x "$SAGE_LOCAL/bin/sage-gdb-commands" --args python "$SAGE_LOCAL/bin/sage-runtests" --serial --timeout=0 hello_world.py

        ::

            sage: DD = DocTestDefaults(valgrind=True, optional="all")
            sage: DC = DocTestController(DD, ["hello_world.py"])
            sage: DC.run_val_gdb(testing=True)
            exec valgrind --tool=memcheck --leak-resolution=high --leak-check=full --num-callers=25 --suppressions="$SAGE_LOCAL/lib/valgrind/sage.supp"  --log-file=".../valgrind/sage-memcheck.%p" python "$SAGE_LOCAL/bin/sage-runtests" --serial --timeout=172800 --optional=all hello_world.py
        """
        try:
            sage_cmd = self._assemble_cmd()
        except ValueError:
            self.log(sys.exc_info()[1])
            return 2
        opt = self.options
        if opt.gdb:
            cmd = '''exec gdb -x "$SAGE_LOCAL/bin/sage-gdb-commands" --args '''
            flags = ""
            if opt.logfile:
                sage_cmd += " --logfile %s"%(opt.logfile)
        else:
            if opt.logfile is None:
                default_log = os.path.join(DOT_SAGE, "valgrind")
                if os.path.exists(default_log):
                    if not os.path.isdir(default_log):
                        self.log("%s must be a directory"%default_log)
                        return 2
                else:
                    os.makedirs(default_log)
                logfile = os.path.join(default_log, "sage-%s")
            else:
                logfile = opt.logfile
            if opt.valgrind:
                toolname = "memcheck"
                flags = os.getenv("SAGE_MEMCHECK_FLAGS")
                if flags is None:
                    flags = "--leak-resolution=high --leak-check=full --num-callers=25 "
                    flags += '''--suppressions="%s" '''%(os.path.join("$SAGE_LOCAL","lib","valgrind","sage.supp"))
            elif opt.massif:
                toolname = "massif"
                flags = os.getenv("SAGE_MASSIF_FLAGS", "--depth=6 ")
            elif opt.cachegrind:
                toolname = "cachegrind"
                flags = os.getenv("SAGE_CACHEGRIND_FLAGS", "")
            elif opt.omega:
                toolname = "exp-omega"
                flags = os.getenv("SAGE_OMEGA_FLAGS", "")
            cmd = "exec valgrind --tool=%s "%(toolname)
            flags += ''' --log-file="%s" ''' % logfile
            if opt.omega:
                toolname = "omega"
            if "%s" in flags:
                flags %= toolname + ".%p" # replace %s with toolname
        cmd += flags + sage_cmd

        self.log(cmd)
        sys.stdout.flush()
        sys.stderr.flush()
        if self.logfile is not None:
            self.logfile.flush()

        if testing:
            return

        import signal, subprocess
        def handle_alrm(sig, frame):
            raise RuntimeError
        signal.signal(signal.SIGALRM, handle_alrm)
        p = subprocess.Popen(cmd, shell=True)
        if opt.timeout > 0:
            signal.alarm(opt.timeout)
        try:
            return p.wait()
        except RuntimeError:
            self.log("    Time out")
            return 4
        except KeyboardInterrupt:
            self.log("    Interrupted")
            return 128
        finally:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            if p.returncode is None:
                p.terminate()

    def run(self):
        """
        This function is called after initialization to set up and run all doctests.

        EXAMPLES::

            sage: from sage.doctest.control import DocTestDefaults, DocTestController
            sage: import os
            sage: DD = DocTestDefaults()
            sage: filename = os.path.join(os.environ["SAGE_ROOT"], "devel", "sage", "sage", "sets", "non_negative_integers.py")
            sage: DC = DocTestController(DD, [filename])
            sage: DC.run()
            Running doctests with ID ...
            Doctesting 1 file.
            sage -t .../sage/sets/non_negative_integers.py
                [... tests, ... s]
            ------------------------------------------------------------------------
            All tests passed!
            ------------------------------------------------------------------------
            Total time for all tests: ... seconds
                cpu time: ... seconds
                cumulative wall time: ... seconds
            0
        """
        opt = self.options
        L = (opt.gdb, opt.valgrind, opt.massif, opt.cachegrind, opt.omega)
        if any(L):
            if L.count(True) > 1:
                self.log("You may only specify one of gdb, valgrind/memcheck, massif, cachegrind, omega")
                return 2
            return self.run_val_gdb()
        else:
            self.test_safe_directory()
            self.create_run_id()
            self.add_files()
            self.expand_files_into_sources()
            self.filter_sources()
            self.sort_sources()
            self.run_doctests()
            return self.reporter.error_status

def run_doctests(module, options=None):
    """
    Runs the doctests in a given file.

    INPUTS:

    - ``module`` -- a Sage module, a string, or a list of such.

    - ``options`` -- a DocTestDefaults object or None.

    EXAMPLES::

        sage: run_doctests(sage.rings.infinity)
        Doctesting .../sage/rings/infinity.py
        Running doctests with ID ...
        Doctesting 1 file.
        sage -t .../sage/rings/infinity.py
            [... tests, ... s]
        ------------------------------------------------------------------------
        All tests passed!
        ------------------------------------------------------------------------
        Total time for all tests: ... seconds
            cpu time: ... seconds
            cumulative wall time: ... seconds
    """
    import sys
    sys.stdout.flush()
    def stringify(x):
        if isinstance(x, (list, tuple)):
            F = [stringify(a) for a in x]
            return sage.misc.flatten.flatten(F)
        elif isinstance(x, types.ModuleType):
            F = re.sub(os.path.join("local","lib", r"python[0-9\.]*","site-packages"),os.path.join("devel","sage"),x.__file__)
            base, pyfile = os.path.split(F)
            file, ext = os.path.splitext(pyfile)
            if ext == ".pyc":
                ext = ".py"
            elif ext == ".so":
                ext = ".pyx"
            if file == "__init__":
                return [base]
            else:
                return [os.path.join(base, file) + ext]
        elif isinstance(x, basestring):
            return [os.path.abspath(x)]
    F = stringify(module)
    print "Doctesting %s"%(", ".join(F))
    if options is None:
        options = DocTestDefaults()
    DC = DocTestController(options, F)
    import sage.plot.plot
    save_dtmode = sage.plot.plot.DOCTEST_MODE
    try:
        DC.run()
    finally:
        sage.plot.plot.DOCTEST_MODE = save_dtmode
