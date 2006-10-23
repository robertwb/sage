cimport sage.structure.element
cimport sage.matrix.matrix_generic

cdef class FreeModuleElement(sage.structure.element.ModuleElement):
    cdef FreeModuleElement _matrix_multiply(self, sage.matrix.matrix_generic.Matrix A)
    cdef FreeModuleElement _scalar_multiply(self, s)

cdef class FreeModuleElement_generic_dense(FreeModuleElement):
    cdef object _entries

cdef class FreeModuleElement_generic_sparse(FreeModuleElement):
    cdef object _entries
