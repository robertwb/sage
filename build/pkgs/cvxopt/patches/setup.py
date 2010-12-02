from distutils.core import setup, Extension
from glob import glob

import os
SAGE_LIB = os.environ['SAGE_LOCAL']+'/lib'
SAGE_INCLUDE = os.environ['SAGE_LOCAL']+'/include'

# directory containing libblas and liblapack
ATLAS_LIB_DIR = SAGE_LIB
libdirs = [ATLAS_LIB_DIR]

if os.popen('sage_fortran --version').read()[:3]=='G95':
    libraries = ['m','lapack','gsl','gslcblas','blas','f95']
    GCC_LIB_DIR=SAGE_LIB
    if os.path.exists(GCC_LIB_DIR + "/gcc-lib"):
       GCC_LIB_DIR += "/gcc-lib/"
       GCC_LIB_DIR += os.listdir(GCC_LIB_DIR)[0] + "/"
       GCC_LIB_DIR += os.listdir(GCC_LIB_DIR)[0] + "/"
    libdirs = [ATLAS_LIB_DIR,GCC_LIB_DIR]
elif os.environ['UNAME'] == 'CYGWIN':
    libraries = ['lapack','gsl','gslcblas','blas', 'gfortran']
else:
    libraries = ['m','lapack','gsl','blas','gslcblas','cblas','gfortran','atlas']


# Set to 1 if you are using the random number generators in the GNU
# Scientific Library.
BUILD_GSL = 1

# Directory containing libgsl (used only when BUILD_GSL = 1).
GSL_LIB_DIR = SAGE_LIB

# Directory containing the GSL header files (used only when BUILD_GSL = 1).
GSL_INC_DIR = SAGE_INCLUDE

# Set to 1 if you are installing the fftw module.
BUILD_FFTW = 0

# Directory containing libfftw3 (used only when BUILD_FFTW = 1).
FFTW_LIB_DIR = '/usr/lib'

# Directory containing fftw.h (used only when BUILD_FFTW = 1).
FFTW_INC_DIR = '/usr/include'

# Set to 1 if you are installing the GLPK module.
BUILD_GLPK = 1

# Directory containing libglpk (used only when BUILD_GLPK = 1).
GLPK_LIB_DIR = SAGE_LIB

# Directory containing glpk.h (used only when BUILD_GLPK = 1).
GLPK_INC_DIR = SAGE_INCLUDE

# Set to 1 if you are installing the DSDP module.
BUILD_DSDP = 0

# Directory containing libdsdp (used only when BUILD_DSDP = 1).
DSDP_LIB_DIR = '/usr/local/src/sage/dsdp/DSDP5.8/lib'

# Directory containing dsdp5.h (used only when BUILD_DSDP = 1).
DSDP_INC_DIR = '/usr/local/src/sage/dsdp/DSDP5.8/include'

extmods = []

# optional modules

if BUILD_GSL:
    gsl = Extension('gsl', libraries = libraries+['gsl'],
        include_dirs = [ GSL_INC_DIR ],
        library_dirs = libdirs + [ GSL_LIB_DIR ],
        sources = ['C/gsl.c'] )
    extmods += [gsl];

if BUILD_FFTW:
    fftw = Extension('fftw', libraries = ['fftw3', 'blas'],
        include_dirs = [ FFTW_INC_DIR ],
        library_dirs = [ FFTW_LIB_DIR] + libdirs,
        sources = ['C/fftw.c'] )
    extmods += [fftw];

if BUILD_GLPK:
    glpk = Extension('glpk', libraries = libraries+['glpk', 'gmp', 'z'],
        include_dirs = [ GLPK_INC_DIR ],
        library_dirs = libdirs + [ GLPK_LIB_DIR ],
        sources = ['C/glpk.c'] )
    extmods += [glpk];

if BUILD_DSDP:
    dsdp = Extension('dsdp', libraries = libraries+['dsdp'],
        include_dirs = [ DSDP_INC_DIR ],
        library_dirs = [ DSDP_LIB_DIR] + libdirs,
        sources = ['C/dsdp.c'] )
    extmods += [dsdp];


# required modules

# Modify this for compilation on Windows.
# Set to True if your BLAS/LAPACK do not use trailing underscores
# (eg, on Windows).
BLAS_NOUNDERSCORES = False
if BLAS_NOUNDERSCORES:
    MACROS = [('BLAS_NO_UNDERSCORE','')]
else:
    MACROS = []

base = Extension('base', libraries = libraries,
    library_dirs = libdirs,
    define_macros = MACROS,
    sources = ['C/base.c','C/dense.c','C/sparse.c'])

blas = Extension('blas', libraries = libraries,
    library_dirs = libdirs,
    define_macros = MACROS,
    sources = ['C/blas.c'] )

lapack = Extension('lapack', libraries = libraries,
    library_dirs = libdirs,
    define_macros = MACROS,
    sources = ['C/lapack.c'] )

umfpack = Extension('umfpack',
    include_dirs = [ 'C/SuiteSparse/UMFPACK/Include',
        'C/SuiteSparse/AMD/Include', 'C/SuiteSparse/AMD/Source',
        'C/SuiteSparse/UFconfig', ],
    library_dirs = libdirs,
    define_macros = MACROS,
    libraries = libraries,
    sources = [ 'C/umfpack.c',
        'C/SuiteSparse/UMFPACK/Source/umfpack_global.c',
        'C/SuiteSparse/UMFPACK/Source/umfpack_tictoc.c' ] +
        glob('C/SuiteSparse_cvxopt_extra/umfpack/*'))

# Build for int or long?
import sys
if sys.maxint > 2**31: MACROS += [('DLONG','')]

cholmod = Extension('cholmod',
    library_dirs = libdirs,
    libraries = libraries,
    include_dirs = [ 'C/SuiteSparse/CHOLMOD/Include',
        'C/SuiteSparse/COLAMD', 'C/SuiteSparse/AMD/Include',
        'C/SuiteSparse/UFconfig', 'C/SuiteSparse/COLAMD/Include',],
    define_macros = MACROS + [('NPARTITION', '1')],
    sources = [ 'C/cholmod.c' ] +
        ['C/SuiteSparse/AMD/Source/' + s for s in ['amd_global.c',
            'amd_postorder.c', 'amd_post_tree.c', 'amd_2.c']] +
        ['C/SuiteSparse/COLAMD/Source/' + s for s in ['colamd.c',
            'colamd_global.c']] +
        glob('C/SuiteSparse/CHOLMOD/Core/c*.c') +
        glob('C/SuiteSparse/CHOLMOD/Cholesky/c*.c') +
        ['C/SuiteSparse/CHOLMOD/Check/cholmod_check.c'] +
        glob('C/SuiteSparse/CHOLMOD/Supernodal/c*.c') )

amd = Extension('amd',
    include_dirs = [ 'C/SuiteSparse/AMD/Include',
        'C/SuiteSparse/UFconfig', ],
    define_macros = MACROS,
    library_dirs = libdirs,
    sources = [ 'C/amd.c' ] + glob('C/SuiteSparse/AMD/Source/*.c') )

misc_solvers = Extension('misc_solvers',
    libraries = libraries,
    library_dirs = libdirs,
    define_macros = MACROS,
    sources = ['C/misc_solvers.c'] )

extmods += [base, blas, lapack, umfpack, cholmod, amd, misc_solvers]

for mod in extmods:
    mod.include_dirs += [ SAGE_INCLUDE ]

setup (name = 'cvxopt',
    description = 'Convex optimization package',
    version = '1.1.3',
    long_description = '''
CVXOPT is a free software package for convex optimization based on the
Python programming language. It can be used with the interactive Python
interpreter, on the command line by executing Python scripts, or
integrated in other software via Python extension modules. Its main
purpose is to make the development of software for convex optimization
applications straightforward by building on Python's extensive standard
library and on the strengths of Python as a high-level programming
language.''',
    author = 'J. Dahl and L. Vandenberghe',
    author_email = 'dahl.joachim@gmail.com, vandenbe@ee.ucla.edu',
    url = 'http://abel.ee.ucla.edu/cvxopt',
    license = 'GNU GPL version 3',
    ext_package = "cvxopt",
    ext_modules = extmods,
    package_dir = {"cvxopt": "python"},
    packages = ["cvxopt"])
