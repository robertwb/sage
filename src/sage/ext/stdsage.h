/*
General C (.h) code this is useful to include in any pyrex module.

Put

include 'relative/path/to/stdsage.pxi'

at the top of your Pyrex file.

These are mostly things that can't be done in Pyrex.
*/

/******************************************************************************
       Copyright (C) 2006 William Stein <wstein@gmail.com>

  Distributed under the terms of the GNU General Public License (GPL), Version 2.

  The full text of the GPL is available at:
                  http://www.gnu.org/licenses/

******************************************************************************/

#ifndef STDSAGE_H
#define STDSAGE_H


/*****************************************
          For PARI
          Memory management

 *****************************************/

#define set_gel(x, n, z)  gel(x,n)=z;


/******************************************
 Some macros exported for Pyrex in cdefs.pxi
 ****************************************/

/* Tests whether zzz_obj is of type zzz_type. The zzz_type must be a built-in
   or extension type. This is just a C++-compatible wrapper for
   PyObject_TypeCheck. */
#define PY_TYPE_CHECK(zzz_obj, zzz_type) \
    (PyObject_TypeCheck((PyObject*)(zzz_obj), (PyTypeObject*)(zzz_type)))

/* Returns the type field of a python object, cast to void*. The returned
   value should only be used as an opaque object e.g. for type comparisons. */
#define PY_TYPE(zzz_obj) ((void*)((zzz_obj)->ob_type))

/* Constructs a new object of type zzz_type by calling tp_new directly,
   with no arguments. */
/* #define PY_NEW(zzz_type) \
    (((PyTypeObject*)(zzz_type))->tp_new((zzz_type), global_empty_tuple, NULL)) */

#define PY_NEW(zzz_type) \
    (((PyTypeObject*)(zzz_type))->tp_new((zzz_type), global_empty_tuple, NULL))

/* Resets the tp_new slot of zzz_type1 to point to the tp_new slot of
   zzz_type2. This is used in SAGE to speed up Pyrex's boilerplate object
   construction code by skipping irrelevant base class tp_new methods. */
#define PY_SET_TP_NEW(zzz_type1, zzz_type2) \
    (((PyTypeObject*)zzz_type1)->tp_new = ((PyTypeObject*)zzz_type2)->tp_new)


/* Tests whether the given object has a python dictionary. */
#define HAS_DICTIONARY(zzz_obj) \
    (((PyObject*)(zzz_obj))->ob_type->tp_dictoffset != NULL)

/* Very very unsafe access to the list of pointers to PyObject*'s underlying a list / sequence.
   This does error checking of any kind -- make damn sure you hand it a list or sequence! */
#define FAST_SEQ_UNSAFE(zzz_obj) \
    PySequence_Fast_ITEMS(PySequence_Fast(zzz_obj, "expected sequence type"))

/* Returns the type field of a python object, cast to void*. The returned
   value should only be used as an opaque object e.g. for type comparisons. */
#define PY_IS_NUMERIC(zzz_obj) \
     (PyInt_Check(zzz_obj) ||  PyBool_Check(zzz_obj) || PyLong_Check(zzz_obj) || \
       PyFloat_Check(zzz_obj) || PyComplex_Check(zzz_obj))


/* This is exactly the same as isinstance (and does return a Python
   bool), but the second argument must be a C-extension type -- so it
   can't be a Python class or a list.  If you just want an int return
   value, i.e., aren't going to pass this back to Python, just use
   PY_TYPE_CHECK. */
#define IS_INSTANCE(zzz_obj, zzz_type) \
    PyBool_FromLong(PY_TYPE_CHECK(zzz_obj, zzz_type))

PyObject* global_empty_tuple;

/*****************************************
          Memory management

NOTE -- before changing these away from Python's keep the following in
mind (from the Python C/API guide):

"In most situations, however, it is recommended to allocate memory from
the Python heap specifically because the latter is under control of
the Python memory manager. For example, this is required when the
interpreter is extended with new object types written in C. Another
reason for using the Python heap is the desire to inform the Python
memory manager about the memory needs of the extension module. Even
when the requested memory is used exclusively for internal,
highly-specific purposes, delegating all memory requests to the Python
memory manager causes the interpreter to have a more accurate image of
its memory footprint as a whole. Consequently, under certain
circumstances, the Python memory manager may or may not trigger
appropriate actions, like garbage collection, memory compaction or
other preventive procedures. Note that by using the C library
allocator as shown in the previous example, the allocated memory for
the I/O buffer escapes completely the Python memory manager."

 *****************************************/

#define sage_malloc  malloc
#define sage_free    free
#define sage_realloc realloc



#endif
