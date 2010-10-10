"""
Testing signal handling.

AUTHORS:

 - Jeroen Demeyer (2010-09-29): initial version (#10030)

"""
#*****************************************************************************
#       Copyright (C) 2010 Jeroen Demeyer <jdemeyer@cage.ugent.be>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************


import signal

cdef extern from 'stdlib.h':
    void abort()

cdef extern from 'signal.h':
    int SIGHUP, SIGINT, SIGQUIT, SIGILL, SIGABRT, SIGFPE, SIGKILL, \
        SIGSEGV, SIGPIPE, SIGALRM, SIGTERM, SIGBUS

cdef extern from '../tests/c_lib.h':
    void ms_sleep(long ms)
    void signal_after_delay(int signum, long ms)
    void signals_after_delay(int signum, long ms, long interval, int n)

cdef extern from *:
    ctypedef int volatile_int "volatile int"


include '../ext/interrupt.pxi'
include '../ext/stdsage.pxi'


# Default delay in milliseconds before raising signals
cdef long DEFAULT_DELAY = 200


########################################################################
# C helper functions                                                   #
########################################################################
cdef void infinite_loop():
    while True:
        pass

cdef void infinite_malloc_loop():
    cdef size_t s = 1
    while True:
        sage_free(sage_malloc(s))
        s *= 2
        if (s > 1000000): s = 1

# Dereference a NULL pointer on purpose. This signals a SIGSEGV on most
# systems, but on older Mac OS X and possibly other systems, this
# signals a SIGBUS instead. In any case, this should give some signal.
cdef void dereference_null_pointer():
    cdef long* ptr = <long*>(0)
    ptr[0] += 1


########################################################################
# Python helper functions                                              #
########################################################################
def raise_KeyboardInterrupt():
    """
    Raise a KeyboardInterrupt.
    """
    raise KeyboardInterrupt, "raise test"

def try_sigint(f):
    """
    Calls the Python function ``f`` and catch any KeyboardInterrupts.
    This function is needed because the doctest program stops whenever
    it sees a KeyboardInterrupt.

    EXAMPLES::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(raise_KeyboardInterrupt)
        KeyboardInterrupt: raise test
    """
    try:
        f()
    except KeyboardInterrupt, err:
        print "KeyboardInterrupt:", err

def interrupt_after_delay(ms_delay = 500):
    """
    Send an interrupt signal (``SIGINT``) to the Sage process
    after a delay of ``ms_delay`` milliseconds.

    INPUT:

    - ``ms_delay`` -- (default: 500) a nonnegative integer indicating
      how many milliseconds to wait before raising the interrupt signal.

    EXAMPLES:

    This function is meant to test interrupt functionality.  We
    demonstrate here how to test that the ``factor`` function can be
    interrupted::

        sage: import sage.tests.interrupt
        sage: try:
        ...     sage.tests.interrupt.interrupt_after_delay()
        ...     factor(10^1000 + 3)
        ... except KeyboardInterrupt:
        ...     print "Caught KeyboardInterrupt"
        Caught KeyboardInterrupt
    """
    signal_after_delay(SIGINT, ms_delay)


########################################################################
# Test basic macros from c_lib/headers/interrupt.h                     #
########################################################################
def test_sig_off():
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_off()
    """
    sig_on()
    sig_off()

def test_sig_on(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_on)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    sig_on()
    infinite_loop()

def test_sig_str(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_str()
        Traceback (most recent call last):
        ...
        RuntimeError: Everything ok!
    """
    sig_str("Everything ok!")
    signal_after_delay(SIGABRT, delay)
    infinite_loop()

cdef c_test_sig_on_cython():
    sig_on()
    infinite_loop()

def test_sig_on_cython(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_on_cython)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    c_test_sig_on_cython()

cdef int c_test_sig_on_cython_except() except 42:
    sig_on()
    infinite_loop()

def test_sig_on_cython_except(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_on_cython_except)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    c_test_sig_on_cython_except()

cdef void c_test_sig_on_cython_except_all() except *:
    sig_on()
    infinite_loop()

def test_sig_on_cython_except_all(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_on_cython_except_all)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    c_test_sig_on_cython_except_all()

def test_sig_check(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_check)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    while True:
        sig_check()

def test_sig_check_inside_sig_on(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_check_inside_sig_on)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    sig_on()
    while True:
        sig_check()

def test_sig_retry():
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_retry()
        10
    """
    cdef volatile_int v = 0

    sig_on()
    if v < 10:
        v = v + 1
        sig_retry()
    sig_off()
    return v

def test_sig_retry_and_signal(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_retry_and_signal)
        KeyboardInterrupt:
    """
    cdef volatile_int v = 0

    sig_on()
    if v < 10:
        v = v + 1
        sig_retry()
    signal_after_delay(SIGINT, delay)
    infinite_loop()

########################################################################
# Test no_except macros                                                #
########################################################################
def test_sig_on_no_except(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_on_no_except()
        42
    """
    if not sig_on_no_except():
        # We should never get here, because this sig_on_no_except()
        # will not catch a signal.
        print "Unexpected zero returned from sig_on_no_except()"
    sig_off()

    signal_after_delay(SIGINT, delay)
    if not sig_on_no_except():
        # We get here when we caught a signal.  An exception
        # has been raised, but Cython doesn't realize it yet.
        try:
            # Make Cython realize that there is an exception.
            # To Cython, it will look like the exception was raised on
            # the following line, so the try/except should work.
            cython_check_exception()
        except KeyboardInterrupt:
            return 42
        return 0 # fail
    infinite_loop()

def test_sig_str_no_except(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_str_no_except()
        Traceback (most recent call last):
        ...
        RuntimeError: Everything ok!
    """
    if not sig_on_no_except():
        # We should never get here, because this sig_on_no_except()
        # will not catch a signal.
        print "Unexpected zero returned from sig_on_no_except()"
    sig_off()

    if not sig_str_no_except("Everything ok!"):
        cython_check_exception()
        return 0 # fail
    signal_after_delay(SIGABRT, delay)
    infinite_loop()


def test_sig_check_no_except(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_check_no_except)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    while True:
        if not sig_check_no_except():
            cython_check_exception()
            return 0 # fail


########################################################################
# Test deprecated macros for backwards compatibility                   #
########################################################################
def test_old_sig_off():
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_old_sig_off()
    """
    _sig_on
    _sig_off

def test_old_sig_on(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_old_sig_on)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    _sig_on
    infinite_loop()

def test_old_sig_str(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_old_sig_str()
        Traceback (most recent call last):
        ...
        RuntimeError: Everything ok!
    """
    _sig_str("Everything ok!")
    signal_after_delay(SIGABRT, delay)
    infinite_loop()


########################################################################
# Test different signals                                               #
########################################################################
def test_signal_segv(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_signal_segv()
        Traceback (most recent call last):
        ...
        RuntimeError: Segmentation fault
    """
    sig_on()
    signal_after_delay(SIGSEGV, delay)
    infinite_loop()

def test_signal_fpe(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_signal_fpe()
        Traceback (most recent call last):
        ...
        RuntimeError: Floating point exception
    """
    sig_on()
    signal_after_delay(SIGFPE, delay)
    infinite_loop()

def test_signal_ill(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_signal_ill()
        Traceback (most recent call last):
        ...
        RuntimeError: Illegal instruction
    """
    sig_on()
    signal_after_delay(SIGILL, delay)
    infinite_loop()

def test_signal_abrt(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_signal_abrt()
        Traceback (most recent call last):
        ...
        RuntimeError: Aborted
    """
    sig_on()
    signal_after_delay(SIGABRT, delay)
    infinite_loop()

def test_signal_bus(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_signal_bus()
        Traceback (most recent call last):
        ...
        RuntimeError: Bus error
    """
    sig_on()
    signal_after_delay(SIGBUS, delay)
    infinite_loop()


########################################################################
# Test with "true" errors (not signals raised by hand)                 #
########################################################################
def test_dereference_null_pointer():
    """
    TESTS:

    This test should result in either a Segmentation Fault or a Bus
    Error. ::

        sage: from sage.tests.interrupt import *
        sage: test_dereference_null_pointer()
        Traceback (most recent call last):
        ...
        RuntimeError: ...
    """
    sig_on()
    dereference_null_pointer()

def unguarded_dereference_null_pointer():
    """
    TESTS:

    We run Sage in a subprocess and dereference a NULL pointer without
    using ``sig_on()``. This will crash Sage::

        sage: from subprocess import *
        sage: cmd = 'from sage.tests.interrupt import *; unguarded_dereference_null_pointer()'
        sage: print '---'; print Popen(['sage', '-c', cmd], stdout=PIPE, stderr=PIPE).communicate()[1]  # long time
        -...
        ------------------------------------------------------------------------
        Unhandled SIG...
        This probably occurred because a *compiled* component of Sage has a bug
        in it and is not properly wrapped with sig_on(), sig_off(). You might
        want to run Sage under gdb with 'sage -gdb' to debug this.
        Sage will now terminate.
        ------------------------------------------------------------------------
        ...
    """
    dereference_null_pointer()

def test_abort():
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_abort()
        Traceback (most recent call last):
        ...
        RuntimeError: Aborted
    """
    sig_on()
    abort()

def unguarded_abort():
    """
    TESTS:

    We run Sage in a subprocess and make it call abort()::

        sage: from subprocess import *
        sage: cmd = 'from sage.tests.interrupt import *; unguarded_abort()'
        sage: print '---'; print Popen(['sage', '-c', cmd], stdout=PIPE, stderr=PIPE).communicate()[1]  # long time
        -...
        ------------------------------------------------------------------------
        Unhandled SIGABRT: An abort() occurred in Sage.
        This probably occurred because a *compiled* component of Sage has a bug
        in it and is not properly wrapped with sig_on(), sig_off(). You might
        want to run Sage under gdb with 'sage -gdb' to debug this.
        Sage will now terminate.
        ------------------------------------------------------------------------
        ...
    """
    abort()

def test_bad_str(long delay = DEFAULT_DELAY):
    """
    TESTS:

    We run Sage in a subprocess and induce an error during the signal handler::

        sage: from subprocess import *
        sage: cmd = 'from sage.tests.interrupt import *; test_bad_str()'
        sage: print '---'; print Popen(['sage', '-c', cmd], stdout=PIPE, stderr=PIPE).communicate()[1]  # long time
        -...
        ------------------------------------------------------------------------
        An error occured during signal handling.
        This probably occurred because a *compiled* component of Sage has a bug
        in it and is not properly wrapped with sig_on(), sig_off(). You might
        want to run Sage under gdb with 'sage -gdb' to debug this.
        Sage will now terminate.
        ------------------------------------------------------------------------
        ...
    """
    cdef char* s = <char*>(16)
    sig_str(s)
    signal_after_delay(SIGILL, delay)
    infinite_loop()


########################################################################
# Test various usage scenarios for sig_on()/sig_off()                  #
########################################################################
def test_sig_on_cython_after_delay(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: try_sigint(test_sig_on_cython_after_delay)
        KeyboardInterrupt:
    """
    signal_after_delay(SIGINT, delay)
    ms_sleep(delay * 2)  # We get signaled during this sleep
    sig_on()             # The signal should be detected here
    abort()              # This should not be reached

def test_sig_on_inside_try(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_on_inside_try()
    """
    try:
        sig_on()
        signal_after_delay(SIGABRT, delay)
        infinite_loop()
    except RuntimeError:
        pass

def test_interrupt_bomb(int n = 100, int p = 10):
    """
    Have `p` processes each sending `n` interrupts in very quick
    succession and see what happens :-)

    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_interrupt_bomb()  # long time (1200 + 5*p + 10*n milliseconds)
        Received ... interrupts
    """
    cdef int i

    # Spawn p processes, each sending n signals with an interval of 1 millisecond
    cdef long base_delay = DEFAULT_DELAY + 5*p
    for i in range(p):
        signals_after_delay(SIGINT, base_delay, 1, n)

    # Some time later (after the smoke clears up) send a SIGABRT,
    # which will raise RuntimeError.
    signal_after_delay(SIGABRT, base_delay + 10*n + 1000)
    i = 0
    while True:
        try:
            sig_on()
            infinite_loop()
        except KeyboardInterrupt:
            i = i + 1
        except RuntimeError:
            break
    print "Received %i/%i interrupts"%(i,n*p)

def test_sig_on_loop():
    """
    Test sig_on() and sig_off() in a loop, this is also useful for
    benchmarking.

    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_on_loop()
    """
    cdef int i
    for i in range(10000000):
        sig_on()
        sig_off()

# Special thanks to Robert Bradshaw for suggesting the try/finally
# construction. -- Jeroen Demeyer
def test_try_finally_signal(long delay = DEFAULT_DELAY):
    """
    Test a try/finally construct for sig_on() and sig_off(), raising
    a signal inside the ``try``.

    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_try_finally_signal()
        Traceback (most recent call last):
        ...
        RuntimeError: Aborted
    """
    sig_on()
    try:
        signal_after_delay(SIGABRT, delay)
        infinite_loop()
    finally:
        sig_off()

def test_try_finally_raise():
    """
    Test a try/finally construct for sig_on() and sig_off(), raising
    a Python exception inside the ``try``.

    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_try_finally_raise()
        Traceback (most recent call last):
        ...
        RuntimeError: Everything ok!
    """
    sig_on()
    try:
        raise RuntimeError, "Everything ok!"
    finally:
        sig_off()

def test_try_finally_return():
    """
    Test a try/finally construct for sig_on() and sig_off(), doing a
    normal ``return`` inside the ``try``.

    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_try_finally_return()
        'Everything ok!'
    """
    sig_on()
    try:
        return "Everything ok!"
    finally:
        sig_off()


########################################################################
# Test sig_block()/sig_unblock()                                       #
########################################################################
def test_sig_block(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_block()
        42
    """
    cdef volatile_int v = 0

    try:
        sig_on()
    except KeyboardInterrupt:
        return v

    sig_block()
    signal_after_delay(SIGINT, delay)
    ms_sleep(delay * 2)  # We get signaled during this sleep
    v = 42
    sig_unblock()        # Here, the interrupt will be handled
    return 1             # Never reached

def test_sig_block_outside_sig_on(long delay = DEFAULT_DELAY):
    """
    TESTS::

        sage: from sage.tests.interrupt import *
        sage: test_sig_block_outside_sig_on()
        'Success'
    """
    signal_after_delay(SIGINT, delay)
    cdef int v = 0
    cdef int* p = &v

    # sig_block()/sig_unblock() shouldn't do anything
    # since we're outside of sig_on()
    sig_block()
    ms_sleep(delay * 2)  # We get signaled during this sleep
    sig_unblock()

    try:
        sig_on()  # Interrupt caught here
    except KeyboardInterrupt:
        return "Success"
    abort()   # This should not be reached

def test_signal_during_malloc(long delay = DEFAULT_DELAY):
    """
    Test a signal arriving during a sage_malloc() or sage_free() call.
    Since these are wrapped with sig_block()/sig_unblock(), we should
    safely be able to interrupt them.

    TESTS::

        sage: from sage.tests.interrupt import *
        sage: for i in range(4):  # Several times to reduce chances of false positive
        ...       test_signal_during_malloc()
    """
    signal_after_delay(SIGINT, delay)
    try:
        sig_on()
        infinite_malloc_loop()
    except KeyboardInterrupt:
        pass
