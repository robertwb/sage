#!/bin/sh
# Determine the type of C++ compiler, which can later
# be used to determine the flags the compiler
# will want. This is done by testing what the
# C++ compiler's pre-processor defines. For example,
# g++ will always define __GNUC__ (as does gcc).

# Copyright Dr. David Kirkby
# Released under the GPL version 2, or any later version
# the user wishes to use.
# Re-written in a simpler way by Peter Jeremy

# Some of the compilers have been tested, though some have
# not, due to a lack of hardware or software.

# Documentation on the compilers is taken from many source
# in particular, for the commercial Unix compilers.

# HP-UX C and C++ compiler.
# http://docs.hp.com/en/7730/newhelp0610/preprocess.htm

# IBM Compiler Reference - XL C/C++ for AIX, V10.1
# http://www-01.ibm.com/support/docview.wss?uid=swg27012860&aid=1

# Using HP C++ for Tru64 UNIX and Linux Alpha
# http://h30097.www3.hp.com/cplus/ugu_impl.html#implem_chap


# Define a function to display usage information.
usage()
{
cat <<EOF 1>&2
Usage: $0 name_or_path_to_the_C++_compiler

e.g.   $0 /usr/bin/CC
e.g.   $0 CC

  The script will print one of the following to indicate the C++ compiler

  GCC                 - For g++ or a g++ like C++ compiler on any platform
  Sun_Studio          - For Sun Studio or earlier Sun C++ compiler
  HP_on_Tru64         - For a C++ compiler produced by HP/Compaq for Tru64
  HP_on_HP-UX         - For a C++ compiler produced by HP/Compaq for HP-UX
  IBM_on_AIX          - For a C++ compiler produced by IBM for AIX
  HP_on_Alpha_Linux   - For a C++ compiler produced by HP for Alpha linux
                        (This script has not been tested on Alpha Linux,
                        but is based on HP's documentation)
  Unknown             - If the C++ compiler type is unknown

EOF
}

# Exit if the user does not supply one, command line argument.
if [ $# -ne 1 ] ; then
  usage
  exit 1
fi

CXX_LOCAL=$1 # Compiler name or path as argument to script.

# Create a test file. It does not need to be a complete
# C++ file, as it is only pre-processed. So there is no
# need for a 'main'

# Hopefully sufficiently random. $$ is the unique PID
TESTFILE=/tmp/uweew-Test-For-C_plus_Plus_Compiler89yrey4jdgi.$$.cpp
cat >$TESTFILE <<"E*O*F"

#ifdef __GNUC__
GCC
#define KNOWN_CXX
#endif

#ifdef __SUNPRO_CC
Sun_Studio
#define KNOWN_CXX
#endif

#ifdef __digital__
#ifdef __DECCXX
HP_on_Tru64
#define KNOWN_CXX
#endif
#endif

#ifdef __linux__
#ifdef __DECCXX
HP_on_Alpha_Linux
#define KNOWN_CXX
#endif
#endif

#ifdef __HP_aCC
HP_on_HP-UX
#define KNOWN_CXX
#endif

#ifdef __xlC__
IBM_on_AIX
#define KNOWN_CXX
#endif

#ifndef KNOWN_CXX
Unknown
#endif
E*O*F

${CXX_LOCAL} -E $TESTFILE | grep '^[A-Z]' | sed 's/ //g'
rm $TESTFILE
exit 0
