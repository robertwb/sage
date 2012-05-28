"""
all_cmdline.py

This is all.py (load all sage functions) plus set-up for the Sage commandline.
"""

#############################################################################
#       Copyright (C) 2007 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
#############################################################################

"""nodoctest"""

sage_mode = 'cmdline'

try:

    from sage.all import *
    from sage.calculus.predefined import x
    preparser(on=True)

except ValueError as msg:
    import traceback
    t = traceback.format_exc()
    print t
    if 'type object' in str(msg):
        msg = str(msg) + '\n\n** In Sage, the easiest fix for this problem is to type "sage -ba"\n   to rebuild all the Cython code (this takes several minutes).\n   Alternatively, touch the last .pyx file in the traceback above. **\n'
    raise ValueError(msg)

sage.misc.session.init()

import sage.misc.displayhook
sage.misc.displayhook.install()
