cimport free_module_element
import  free_module_element

include '../ext/cdefs.pxi'

cdef class Vector_integer_dense(free_module_element.FreeModuleElement):
        cdef mpz_t* _entries
        cdef _new_c(self)
        cdef _init(self, Py_ssize_t degree, parent)
