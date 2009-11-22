import sys

# Exclude these from the reset command.
EXCLUDE = set(['sage_mode', '__DIR__', 'DIR', 'DATA'])

def reset(vars=None):
    """
    Delete all user defined variables, reset all globals variables
    back to their default state, and reset all interfaces to other
    computer algebra systems.

    If vars is specified, just restore the value of vars and leave
    all other variables alone (i.e., call restore).

    Note that the variables in the set sage.misc.reset.EXCLUDE are
    excluded from being reset.

    INPUT:
        vars -- (default: None), a list, or space or comma separated
        string.

    EXAMPLES:
        sage: x = 5
        sage: reset()
        sage: x
        x
    """
    if not vars is None:
        restore(vars)
        return
    G = globals()  # this is the reason the code must be in Cython.
    T = type(sys)
    for k in G.keys():
        if k[0] != '_' and type(k) != T and k not in EXCLUDE:
            try:
                del G[k]
            except KeyError:
                pass
    restore()
    reset_interfaces()
    reset_attached()

def restore(vars=None):
    """
    Restore predefined global variables to their default values.

    INPUT:
       vars -- string or list (default: None) if not None, restores
               just the given variables to the default value.

    EXAMPLES:
        sage: x = 10; y = 15/3; QQ='red'
        sage: QQ
        'red'
        sage: restore('QQ')
        sage: QQ
        Rational Field
        sage: x
        10
        sage: y = var('y')
        sage: restore('x y')
        sage: x
        x
        sage: y
        Traceback (most recent call last):
        ...
        NameError: name 'y' is not defined
        sage: x = 10; y = 15/3; QQ='red'
        sage: ww = 15
        sage: restore()
        sage: x, QQ, ww
        (x, Rational Field, 15)
        sage: restore('ww')
        sage: ww
        Traceback (most recent call last):
        ...
        NameError: name 'ww' is not defined
    """
    G = globals()  # this is the reason the code must be in Cython.
    if not G.has_key('sage_mode'):
        import sage.all
        D = sage.all.__dict__
    else:
        mode = G['sage_mode']
        if mode == 'cmdline':
            import sage.all_cmdline
            D = sage.all_cmdline.__dict__
        elif mode == 'notebook':
            import sage.all_notebook
            D = sage.all_notebook.__dict__
        else:
            import sage.all
            D = sage.all.__dict__
    _restore(G, D, vars)
    import sage.calculus.calculus
    _restore(sage.calculus.calculus.syms_cur, sage.calculus.calculus.syms_default, vars)

def _restore(G, D, vars):
    if vars is None:
        for k, v in D.iteritems():
            G[k] = v
    else:
        if isinstance(vars, str):
            if ',' in vars:
                vars = vars.split(',')
            else:
                vars = vars.split()
        for k in vars:
            if D.has_key(k):
                G[k] = D[k]
            else:
                try:
                    del G[k]      # the default value was "unset"
                except KeyError:
                    pass


def reset_interfaces():
    from sage.interfaces.quit import expect_quitall
    expect_quitall()

def reset_attached():
    """
    Remove all the attached files from the list of attached files.

    EXAMPLES::

        sage: sage.misc.reset.reset_attached()
        sage: t = tmp_filename()+'.py'; open(t,'w').write("print 'hello world'")
        sage: attach t
        hello world
        sage: attached_files()
        ['/Users/wstein/.sage//temp/flat.local/12411//tmp_0.py']
        sage: sage.misc.reset.reset_attached()
        sage: attached_files()
        []
    """
    import preparser
    preparser.attached = {}
