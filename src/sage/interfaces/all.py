# interfaces to other interpreters

from expect import is_ExpectElement
from gap import gap, gap_reset_workspace, gap_console, gap_version, is_GapElement, Gap
from genus2reduction import genus2reduction, Genus2reduction
from gp import gp, gp_console, gp_version, is_GpElement, Gp
from gnuplot import gnuplot, gnuplot_console
from kash import  kash, kash_console, kash_version, is_KashElement, Kash
from lcalc import lcalc
from magma import magma, magma_console, magma_version, Magma
from macaulay2 import macaulay2, macaulay2_console, Macaulay2
from maple import maple, maple_console, Maple
from maxima import maxima, maxima_console, is_MaximaElement, Maxima
from mathematica import mathematica, mathematica_console, Mathematica
from mwrank import mwrank, Mwrank, mwrank_console
from octave import octave, octave_console, octave_version, Octave
from singular import singular, singular_console, singular_version, is_SingularElement, Singular
from sage0 import sage0 as sage0, sage0_console, sage0_version, Sage
from sympow import sympow
from psage import PSage

# signal handling
from get_sigs import *

interfaces = ['gap', 'gp', 'mathematica', 'gnuplot', \
              'kash', 'magma', 'macaulay2', 'maple', 'maxima', \
              'mathematica', 'mwrank', 'octave', \
              'singular', 'sage0', 'sage']
