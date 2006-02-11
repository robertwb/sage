"""
Grab signal handlers back from PARI or other C libraries
"""

import signal

def my_sigint(x, n):
    raise KeyboardInterrupt

def my_sigfpe(x, n):
    raise RuntimeError, "A floating point exception occured."

#def my_sigterm(x, n):
#    from sage.all import quit_sage
#    quit_sage(verbose=True)

def get_sigs():
    signal.signal(signal.SIGINT, my_sigint)
    signal.signal(signal.SIGABRT, my_sigint)
    signal.signal(signal.SIGFPE, my_sigfpe)
    signal.signal(signal.SIGALRM, my_sigint)
    #signal.signal(signal.SIGTERM, my_sigterm)
