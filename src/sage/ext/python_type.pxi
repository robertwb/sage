cdef extern from "Python.h":
    ctypedef void PyObject
    ctypedef void PyTypeObject
    # The C structure of the objects used to describe built-in types.

    ############################################################################
    # 7.1.1 Type Objects
    ############################################################################

    # PyObject* PyType_Type
    # This is the type object for type objects; it is the same object
    # as type and types.TypeType in the Python layer.

    int PyType_Check(object o)
    # Return true if the object o is a type object, including
    # instances of types derived from the standard type object. Return
    # false in all other cases.

    int PyType_CheckExact(object o)
    # Return true if the object o is a type object, but not a subtype
    # of the standard type object. Return false in all other
    # cases.

    int PyType_HasFeature(object o, int feature)
    # Return true if the type object o sets the feature feature. Type
    # features are denoted by single bit flags.

    int PyType_IS_GC(object o)
    # Return true if the type object includes support for the cycle
    # detector; this tests the type flag Py_TPFLAGS_HAVE_GC.

    int PyType_IsSubtype(object a, object b)
    # Return true if a is a subtype of b.

    object PyType_GenericAlloc(object type, Py_ssize_t nitems)
    # Return value: New reference.

    object PyType_GenericNew(object type, object args, object kwds)
    # Return value: New reference.

    int PyType_Ready(object type)
    # Finalize a type object. This should be called on all type
    # objects to finish their initialization. This function is
    # responsible for adding inherited slots from a type's base
    # class. Return 0 on success, or return -1 and sets an exception
    # on error.
