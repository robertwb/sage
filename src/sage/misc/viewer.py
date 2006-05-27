r"""
Determination of Programs for Viewing web pages, etc.
"""

import os

def cmd_exists(cmd):
    return os.system('which %s 2>/dev/null >/dev/null'%cmd) == 0


if os.uname()[0] == 'Darwin':

    # Simple on OS X, since there is an open command that opens
    # anything, using the user's preferences.
    # sage-open -- a wrapper around OS X open that
    # turns off any of SAGE's special library stuff.

    BROWSER = 'sage-open'
    DVI_VIEWER = BROWSER
    PDF_VIEWER = BROWSER
    PNG_VIEWER = BROWSER

elif os.uname()[0][:6] == 'CYGWIN':
    # Windows is also easy, since it has a system for
    # determining what opens things.
    # Bobby Moreti provided the following.

    BROWSER= 'rundll32.exe url.dll,FileProtocolHandler'
    DVI_VIEWER = BROWSER
    PDF_VIEWER = BROWSER
    PNG_VIEWER = BROWSER

else:

    # Try to get something from the environment on other OS's (namely Linux?)

    try:
	BROWSER = os.environ['BROWSER']
    except KeyError:
        BROWSER = 'less'  # silly default; lets hope it doesn't come to this!
        for cmd in ['firefox', 'konqueror', 'mozilla', 'mozilla-firefox']:
            if cmd_exists(cmd):
                BROWSER = cmd

    DVI_VIEWER = BROWSER
    PDF_VIEWER = BROWSER
    PNG_VIEWER = BROWSER

    # Alternatives, if they are set in the environment or available.
    try:
        DVI_VIEWER = os.environ['DVI_VIEWER']
    except KeyError:
        for cmd in ['xdvi', 'kdvi']:
            if cmd_exists(cmd):
                DVI_VIEWER = cmd

    try:
        PDF_VIEWER = os.environ['PDF_VIEWER']
    except KeyError:
        for cmd in ['acroread', 'xpdf']:
            if cmd_exists(cmd):
                PDF_VIEWER = cmd
                break

def browser():
    global BROWSER
    return BROWSER
