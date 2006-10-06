import  sage.structure.element
cimport sage.structure.element

cdef class Matrix(sage.structure.element.ModuleElement):
    cdef object _mutability
    cdef object __nrows
    cdef object __ncols
    cdef object __dict
    cdef object __determinant
    cdef object __sparse_columns
    cdef object __sparse_rows
    cdef object __eigenvectors
    cdef object __rank
