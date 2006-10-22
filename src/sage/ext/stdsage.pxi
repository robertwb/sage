"""
Standard SAGE Pyrex Helper Code
"""

################################################################################
# stdsage.pxi
#   Standard useful stuff for SAGE modules to include:
#   See stdsage.h for macros and stdsage.c for C functions.
#
#   Each module currently gets its own copy of this, which is why
#   we call the initialization code below.
#
################################################################################

###############################################################################
#   SAGE: System for Algebra and Geometry Experimentation
#       Copyright (C) 2005, 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

cdef extern from "stdsage.h":
    # Global tuple -- useful optimization
    void init_global_empty_tuple()

# Initialize the global tuple.
init_global_empty_tuple()

# Memory management
cdef extern from "stdlib.h":
    ctypedef unsigned long size_t
cdef extern from "stdsage.h":
    void  sage_free(void *p)
    void* sage_realloc(void *p, size_t n)
    void* sage_malloc(size_t)
