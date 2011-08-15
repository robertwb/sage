import os
import sys

# FIXME: Do we really want to *overwrite* the flags (e.g. if set by the user)?
CCFLAGS=["-O3 -Wno-long-long -Wreturn-type -g -fPIC"]
#CXXFLAGS=CCFLAGS+["-ftemplate-depth-100 -g -fPIC"]
CXXFLAGS=CCFLAGS+["-ftemplate-depth-100"]

GD_LIBS+=["png12","z"]

# FIXME: Should we include LDFLAGS here? (see above)
if not globals().has_key("LINKFLAGS"): LINKFLAGS=[] # s.t. we can *append* below

print "Platform: ", sys.platform

if 'sunos' in sys.platform:
  try:
    SHLINKFLAGS = os.environ['SAGESOFLAGS']
  except:
    SHLINKFLAGS = ["$LINKFLAGS", "-shared", "${_sonamecmd(SONAMEPREFIX, TARGET, SONAMESUFFIX, __env__)}"]


if sys.platform=='darwin':
    FORCE_HASH_MAP=True


if os.environ.get('SAGE_DEBUG', "no") == "yes":
    CPPDEFINES=[]
    CCFLAGS=["-pg"] + CCFLAGS
    CXXFLAGS=["-pg"] + CXXFLAGS
    # LINKFLAGS=["-pg"]
    LINKFLAGS=["-pg"] + LINKFLAGS

if os.environ.get('SAGE64', "no") == "yes":
    print "Building a 64-bit version of PolyBoRi"
    CCFLAGS=["-m64"] + CCFLAGS
    CXXFLAGS=["-m64"] + CXXFLAGS
    # LINKFLAGS=["-m64"]
    LINKFLAGS=["-m64"] + LINKFLAGS

CPPPATH=[os.environ['SAGE_LOCAL']+"/include"]
LIBPATH=[os.environ['SAGE_LOCAL']+"/lib"]

PYPREFIX=os.environ['PYTHONHOME']
PBP=os.environ['PYTHONHOME']+'/bin/python'

HAVE_DOXYGEN=False
HAVE_PYDOC=False
HAVE_L2H=False
HAVE_HEVEA=False
HAVE_TEX4HT=False
HAVE_PYTHON_EXTENSION=False
EXTERNAL_PYTHON_EXTENSION=True

# (CC and CXX should have been set by sage-env, but never mind...:)
try:
  CC = os.environ['CC']
except:
  pass

try:
  CXX = os.environ['CXX']
except:
  pass
