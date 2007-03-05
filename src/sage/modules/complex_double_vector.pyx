r"""
Complex double vectors

The SAGE \code{ComplexDoubleVector} class supports optimized
computation with vectors whose entries are complex double precision
numbers. The underlying arithmetic is implemented by the GSL library.

EXAMPLES:
    sage: v = vector(CDF,[(1,-1), (2,pi), (3,5)])
    sage: v
    (1.0 - 1.0*I, 2.0 + 3.14159265359*I, 3.0 + 5.0*I)
    sage: type(v)
    <type 'sage.modules.complex_double_vector.ComplexDoubleVectorSpaceElement'>
    sage: parent(v)
    Vector space of dimension 3 over Complex Double Field
    sage: v[0] = 5
    sage: v
    (5.0, 2.0 + 3.14159265359*I, 3.0 + 5.0*I)


AUTHORS:
    -- Josh Kantor
    -- William Stein
"""

###############################################################################
#   SAGE: System for Algebra and Geometry Experimentation
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
###############################################################################

cimport free_module_element
import  free_module_element

from sage.structure.element cimport Element, ModuleElement, RingElement

from sage.rings.complex_double import CDF, new_ComplexDoubleElement
from sage.rings.complex_double cimport ComplexDoubleElement

include '../ext/stdsage.pxi'

cdef extern from "arrayobject.h":
#The following exposes the internal C structure of the numpy python object
# extern class [object PyArrayObject]  tells pyrex that this is
# a compiled python class defined by the C struct PyArrayObject
    cdef enum:
        NPY_OWNDATA = 0x0004 #bit mask so numpy does not free array contents when its destroyed

    ctypedef int intp

    ctypedef extern class numpy.ndarray [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef intp *dimensions
        cdef intp *strides
        cdef int flags

    object PyArray_FromDims(int,int *,int)
    object PyArray_FromDimsAndData(int,int*,int,double *)
    void import_array()



cdef class ComplexDoubleVectorSpaceElement(free_module_element.FreeModuleElement):
    cdef _new_c(self, gsl_vector_complex* v):
        cdef ComplexDoubleVectorSpaceElement y
        y = PY_NEW(ComplexDoubleVectorSpaceElement)
        y._parent = self._parent
        y._degree = self._degree
        y.v = v
        return y

    cdef gsl_vector_complex* gsl_vector_complex_copy(self) except NULL:
        """
        Return a copy of the underlying GSL vector of self.
        """
        cdef gsl_vector_complex* v
        v = <gsl_vector_complex*> gsl_vector_complex_calloc(self.v.size)
        if v is NULL:
            raise MemoryError, "error allocating real double vector"
        if gsl_vector_complex_memcpy(v, self.v):
            raise RuntimeError, "error copying real double vector"
        return v

    def __copy__(self, copy=True):
        return self._new_c(self.gsl_vector_complex_copy())

    def __init__(self,parent,x, coerce = True, copy = True):
        """
            parent -- free module element
            x -- defining data
            coerce, copy -- ignored
        """
        self._parent = parent
        self._degree = parent.degree()
        cdef int i
        cdef int n
        cdef gsl_complex z_temp
        cdef ComplexDoubleElement z
        n = parent.rank()
        cdef int length

        self.v = gsl_vector_complex_calloc(n)
        try:
            length=len(x)
        except TypeError:
            if x == 0:
                if self.v is not NULL:
                    return
                else:
                    raise MemoryError, "error allocating memory"
            else:
                self.v = NULL
                raise TypeError, "must be a list, tuple, vector or 0"

        _sig_on
        self.v = <gsl_vector_complex *> gsl_vector_complex_calloc(n)
        _sig_off

        if self.v is not NULL and length == n:
            _sig_on
            for i from 0 <=i <n:
                z = CDF(x[i])
                gsl_vector_complex_set(self.v, i, <gsl_complex>z._complex)
            _sig_off

        elif self.v is NULL:
            raise MemoryError,"Error allocating memory"

        elif length != n:
            raise TypeError, "User supplied vector not same length as rank of vector space"


    def __dealloc__(self):
        gsl_vector_complex_free(self.v)


    def __len__(self):
        return self.v.size

    def __setitem__(self,size_t i,x):
        cdef gsl_complex z_temp

        if i < 0 or i >= self.v.size:
            raise IndexError
        else:
            z_temp =<gsl_complex> (<ComplexDoubleElement> CDF(x))._complex
            gsl_vector_complex_set(self.v,i,z_temp)

    def __getitem__(self,size_t i):
        """
        Return the ith entry of self.

        EXAMPLES:
            sage: v = vector(CDF, [1,CDF(3,2), -1]); v
            (1.0, 3.0 + 2.0*I, -1.0)
            sage: v[1]
            3.0 + 2.0*I
            sage: v[5]
            Traceback (most recent call last):
            ...
            IndexError: index out of range
        """
        cdef gsl_complex z_temp
        cdef ComplexDoubleElement x
        if i < 0 or i >= self.v.size:
            raise IndexError, 'index out of range'
        else:
            x = new_ComplexDoubleElement()
            x._complex = gsl_vector_complex_get(self.v, i)
            return x

    cdef ModuleElement _add_c_impl(self, ModuleElement right):
        cdef gsl_vector_complex *v, *w
        cdef gsl_vector_view v_real, v_imag, w_real, w_imag
        v = self.gsl_vector_complex_copy()
        w = (<ComplexDoubleVectorSpaceElement> right).v
        v_real = gsl_vector_complex_real(v)
        v_imag = gsl_vector_complex_imag(v)
        w_real = gsl_vector_complex_real(w)
        w_imag = gsl_vector_complex_imag(w)
        gsl_vector_add(&(v_real.vector), &(w_real.vector))
        gsl_vector_add(&(v_imag.vector), &(w_imag.vector))
        return self._new_c(v)

    cdef ModuleElement _sub_c_impl(self, ModuleElement right):
        cdef gsl_vector_complex *v, *w
        cdef gsl_vector_view v_real, v_imag, w_real, w_imag
        v = self.gsl_vector_complex_copy()
        w = (<ComplexDoubleVectorSpaceElement> right).v
        v_real = gsl_vector_complex_real(v)
        v_imag = gsl_vector_complex_imag(v)
        w_real = gsl_vector_complex_real(w)
        w_imag = gsl_vector_complex_imag(w)
        gsl_vector_sub(&(v_real.vector), &(w_real.vector))
        gsl_vector_sub(&(v_imag.vector), &(w_imag.vector))
        return self._new_c(v)

    cdef ModuleElement _rmul_c_impl(self, RingElement left):
        cdef gsl_vector_complex* v
        v = self.gsl_vector_complex_copy()
        gsl_blas_zscal(<gsl_complex> (<ComplexDoubleElement>left)._complex, v)
        return self._new_c(v)

    cdef ModuleElement _lmul_c_impl(self, RingElement right):
        cdef gsl_vector_complex* v
        v = self.gsl_vector_complex_copy()
        gsl_blas_zscal(<gsl_complex> (<ComplexDoubleElement>right)._complex, v)
        return self._new_c(v)

    def inv_fft(self,algorithm="radix2", inplace=False):
        """
        This performs the inverse fast fourier transform on the vector.
        sage: v = vector(CDF,[1,2,3,4])
        sage: w = v.fft()
        sage: v - w.inv_fft()    # random -- should be very close to 0.
        (0, 0, 0, 0)

        The fourier transform can be done in place using the keyword
        inplace=True

        This will be fastest if the vector's length is a power of 2.

        """
        return self.fft(direction="backward",algorithm=algorithm,inplace=inplace)

    def fft(self,direction = "forward",algorithm = "radix2",inplace=False):
        """
        This performs a fast fourier transform on the vector.
        By default a forward transform is performed.
        To perform the inverse fourier transform use the the keyword
        direction='backward', or use the method inv_fft.

        sage: v = vector(CDF,[1,2,3,4])
        sage: w = v.fft()
        sage: v2 = w.fft(direction='backward')

        To perform the transform in place use the keyword
        inplace=True

        This will be fastest if the vector's length is a power of 2.
        """
        gsl_set_error_handler_off()
        cdef gsl_fft_complex_wavetable* wavetable
        cdef gsl_fft_complex_workspace* workspace
        cdef int err,err_1
        cdef ComplexDoubleVectorSpaceElement result
        cdef double* data
        cdef gsl_vector_complex* v

        if inplace:
            data = self.v.data
        else:
            # not in place.
            v = self.gsl_vector_complex_copy()
            data = v.data
            result = self._new_c(v)

        if direction == "forward":
            if ispow(self.v.size):
                err = gsl_fft_complex_radix2_forward(data,self.v.stride,self.v.size)
            else:
                wavetable = gsl_fft_complex_wavetable_alloc(self.v.size)
                workspace = gsl_fft_complex_workspace_alloc(self.v.size)
                if wavetable !=NULL and workspace!= NULL:
                    err = gsl_fft_complex_forward(data,1,self.v.size,wavetable,workspace)

                gsl_fft_complex_wavetable_free(wavetable)
                gsl_fft_complex_workspace_free(workspace)
            if not err:
                pass
            else:
                raise ValueError, "error with transform"


        elif direction == "backward":
            if ispow(self.v.size):
                err  = gsl_fft_complex_radix2_inverse(data,self.v.stride,self.v.size)
            else:
                wavetable = gsl_fft_complex_wavetable_alloc(self.v.size)
                workspace = gsl_fft_complex_workspace_alloc(self.v.size)
                if wavetable !=NULL and workspace!= NULL:
                    err = gsl_fft_complex_inverse(data,1,self.v.size,wavetable,workspace)

                gsl_fft_complex_wavetable_free(wavetable)
                gsl_fft_complex_workspace_free(workspace)
            if not err:
                pass
            else:
                raise ValueError, "error with transform"

        if inplace == True:
            return
        else:
            return result


    def numpy(self):
        import_array() #This must be called before using the numpy C/api or you will get segfault
        cdef ComplexDoubleVectorSpaceElement _V,_result_vector
        _V=self
        cdef int dims[1]
        cdef double * data
        cdef int i
        cdef object temp
        cdef double *p
        cdef ndarray _n,_m
        dims[0] = _V.v.size
        data = <double*> malloc(sizeof(double)*dims[0]*2)
        memcpy(data,_V.v.data,sizeof(double)*dims[0]*2)
        temp = PyArray_FromDimsAndData(1, dims, 15,data)
        _n = temp
        _n.flags = _n.flags|(NPY_OWNDATA) # this sets the ownership flag
        return _n

    def _replace_self_with_numpy(self,numpy_array):
        cdef double* p
        cdef ndarray n
        n=numpy_array
        p=<double *>n.data
        memcpy(self.v.data,p,self.v.size*sizeof(double)*2)


cdef int ispow(int n):
    while n and n%2==0:
        n = n>>1
    return n == 1
