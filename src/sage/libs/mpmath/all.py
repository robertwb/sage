import mpmath

# Patch mpmath to use Cythonized functions
import utils as _utils
mpmath.libmpf.normalize = mpmath.libmpf.normalize1 = normalize = _utils.normalize
mpmath.libmpf.from_man_exp = from_man_exp = _utils.from_man_exp

# Also import internal functions
from mpmath.libmpf import *
from mpmath.libelefun import *
from mpmath.libhyper import *
from mpmath.libmpc import *
from mpmath.mptypes import *
from mpmath.gammazeta import *

# Main namespace
from mpmath import *

# Utilities
from utils import call, mpmath_to_sage, sage_to_mpmath

# Use mpmath internal functions for constants, to avoid unnecessary overhead
_constants_funcs = {
  'glaisher' : glaisher_fixed,
  'khinchin' : khinchin_fixed,
  'twinprime' : twinprime_fixed,
  'mertens' : mertens_fixed
}

def eval_constant(name, ring):
    prec = ring.precision() + 20
    return ring(_constants_funcs[name](prec)) >> prec
