include '../ext/cdefs.pxi'
include '../ext/interrupt.pxi'
include 'gsl.pxi'
import gsl_array
cimport gsl_array


cdef class DiscreteWaveletTransform(gsl_array.GSLDoubleArray):
  cdef gsl_wavelet* wavelet
  cdef gsl_wavelet_workspace* workspace
