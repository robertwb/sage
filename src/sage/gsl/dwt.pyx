"""
 Wavelet transform wrapper. Wraps GSL's gsl_wavelet_transform_forward,
 and gsl_wavelet_transform_inverse and creates plot methods.

AUTHOR:
   Josh Kantor (2006-10-07)  - initial version
   David Joyner (2006-10-09) - minor changes to docstrings and examples.

"""

#*****************************************************************************
#       Copyright (C) 2006 Joshua Kantor <jkantor@math.washington.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

#include 'gsl.pxi'

import sage.plot.all

#import gsl_array
#cimport gsl_array

def WaveletTransform(size_t n, wavelet_type,size_t wavelet_k):
    """
    This function initializes an GSLDoubleArray of length n which
    can perform a discrete wavelet transform.

    INPUT:
        n --  a power of 2.
        T -- the data in the GSLDoubleArray must be real.
        wavelet_type -- the name of the type of wavelet,
                        valid choices are:
                         'daubechies','daubechies_centered',
                         'haar','haar_centered','bspline', and
                         'bspline_centered'.

    For daubechies wavelets, wavelet_k specifies a daubechie wavelet
    with k/2 vanishing moments. k = 4,6,...,20 for k even are the
    only ones implemented.
    For Haar wavelets, wavelet_k must be 2.
    For bspline wavelets, wavelet_k = 103,105,202,204,206,208,301,305,
    307,309 will give biorthogonal B-spline wavelets of order (i,j) where
    wavelet_k=100*i+j.
    The wavelet transfrom uses J=log_2(n) levels.

    OUTPUT:
        An array of the form
         (s_{-1,0},d_{0,0},d_{1,0},d_{1,1}, d_{2,0}...,d_{J-1,2^{J-1}-1})
        for d_{j,k} the detail coefficients of level j.
        The centered forms align the coefficients of the sub-bands on edges.

    EXAMPLES:
        sage: a = WaveletTransform(128,'daubechies',4)
        sage: for i in range(1, 11):
        ...    a[i] = 1
        ...    a[128-i] = 1
        sage: show(a.plot(), ymin=0)
        sage: a.forward_transform()
        sage: show(a.plot())
        sage: a = WaveletTransform(128,'haar',2)
        sage: for i in range(1, 11): a[i] = 1; a[128-i] = 1
        sage: a.forward_transform()
        sage: show(a.plot(), ymin=0)
        sage: a = WaveletTransform(128,'bspline_centered',103)
        sage: for i in range(1, 11): a[i] = 1; a[100+i] = 1
        sage: a.forward_transform()
        sage: show(a.plot(), ymin=0)

    This example gives a simple example of wavelet compression.
        sage: a = DWT(2048,'daubechies',6)
        sage: for i in range(2048): a[i]=float(sin((i*5/2048)**2))
        sage: show(a.plot())
        sage: a.forward_transform()
        sage: for i in range(1800): a[2048-i-1] = 0
        sage: a.backward_transform()
        sage: show(a.plot())
    """
    return DiscreteWaveletTransform(n,1,wavelet_type,wavelet_k)

DWT = WaveletTransform

cdef class DiscreteWaveletTransform(gsl_array.GSLDoubleArray):
    def __init__(self,size_t n,size_t stride, wavelet_type, size_t wavelet_k):
        gsl_array.GSLDoubleArray.__init__(self,n,stride)
        if wavelet_type=="daubechies":
            self.wavelet = <gsl_wavelet*> gsl_wavelet_alloc(gsl_wavelet_daubechies, wavelet_k)
        elif wavelet_type == "daubechies_centered":
            self.wavelet = <gsl_wavelet*> gsl_wavelet_alloc(gsl_wavelet_daubechies_centered,wavelet_k)
        elif wavelet_type == "haar":
            self.wavelet = <gsl_wavelet *> gsl_wavelet_alloc(gsl_wavelet_haar,wavelet_k)
        elif wavelet_type == "haar_centered":
            self.wavelet = <gsl_wavelet*> gsl_wavelet_alloc(gsl_wavelet_haar_centered,wavelet_k)
        elif wavelet_type == "bspline":
            self.wavelet = <gsl_wavelet*> gsl_wavelet_alloc(gsl_wavelet_bspline,wavelet_k)
        elif wavelet_type == "bspline_centered":
            self.wavelet = <gsl_wavelet*> gsl_wavelet_alloc(gsl_wavelet_bspline_centered,wavelet_k)
        self.workspace = <gsl_wavelet_workspace*> gsl_wavelet_workspace_alloc(n)

    def __dealloc__(self):
        #    GSLDoubleArray.__dealloc__(self)
        #    sage_free(self.data)
        gsl_wavelet_free(self.wavelet)
        gsl_wavelet_workspace_free(self.workspace)

    def forward_transform(self):
        gsl_wavelet_transform_forward(self.wavelet,self.data,self.stride,self.n,self.workspace)

    def backward_transform(self):
        gsl_wavelet_transform_inverse(self.wavelet,self.data,self.stride,self.n,self.workspace)

    def plot(self,xmin=None,xmax=None,**args):
        cdef int i
        cdef double x
        v = []
        point = sage.plot.all.point
        if xmin == None:
            x_min = 0
        if xmax == None:
            x_max=self.n
        for i from x_min <=i < x_max:
            x = self.data[i]
            if i >0:
                v.append(point([(i,x)],hue=(1,1,1),**args))
        return sum(v)
