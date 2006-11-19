include '../ext/cdefs.pxi'
include '../ext/interrupt.pxi'
include '../gsl/gsl.pxi'

cimport free_module_element
import  free_module_element

cdef class ComplexDoubleVectorSpace_element(free_module_element.FreeModuleElement):
	cdef gsl_vector_complex * v
	cdef _new_c(self, gsl_vector_complex* v)
	cdef gsl_vector_complex* gsl_vector_complex_copy(self)
