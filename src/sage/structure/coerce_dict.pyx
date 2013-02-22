#*****************************************************************************
#       Copyright (C) 2007 Robert Bradshaw <robertwb@math.washington.edu>
#                     2012 Simon King <simon.king@uni-jena.de>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
"""
Containers for storing coercion data

This module provides :class:`TripleDict` and :class:`MonoDict`. These are
structures similar to ``WeakKeyDictionary`` in Python's weakref module,
and are optimized for lookup speed. The keys for :class:`TripleDict` consist
of triples (k1,k2,k3) and are looked up by identity rather than equality. The
keys are stored by weakrefs if possible. If any one of the components k1, k2,
k3 gets garbage collected, then the entry is removed from the :class:`TripleDict`.

Key components that do not allow for weakrefs are stored via a normal
refcounted reference. That means that any entry stored using a triple
(k1,k2,k3) so that none of the k1,k2,k3 allows a weak reference behaves
as an entry in a normal dictionary: Its existence in :class:`TripleDict`
prevents it from being garbage collected.

That container currently is used to store coercion and conversion maps
between two parents (:trac:`715`) and to store homsets of pairs of objects
of a category (:trac:`11521`). In both cases, it is essential that the parent
structures remain garbage collectable, it is essential that the data access
is faster than with a usual ``WeakKeyDictionary``, and we enforce the "unique
parent condition" in Sage (parent structures should be identical if they are
equal).

:class:`MonoDict` behaves similarly, but it takes a single item as a key. It
is used for caching the parents which allow a coercion map into a fixed other
parent (:trac:`12313`).

"""
include "../ext/python_list.pxi"

from weakref import KeyedRef, ref

cdef extern from "Python.h":
    Py_ssize_t PyInt_AsSsize_t(PyObject* io)
    PyObject* PyWeakref_GetObject(object ref)
    PyObject* Py_None

import gc

############################################
# A note about how to store "id" keys in python structures:
#
# In python a "pointer length integer" (size_t) normally, is encoded
# as a *signed* integer, of type Py_ssize_t. This has an advantage in that
# if the value gets encoded as a *python integer* it can do so in a sign-preserving
# way and still make use of all the bits that python offers to store (small) integers.
#
# There is one place where we have to be careful about signs:
# Our hash values most naturally live in Py_ssize_t. We convert those into
# an index into our bucket list by taking the hash modulo the number of buckets.
# However, the modulo operator in C preserves the sign of the number we take the
# modulus of, which is not what we want.
# The solution is to always do
# (<size_t) h)% modulus
# to ensure we're doing an unsigned modulus.

############################################
# The following code is responsible for
# removing dead references from the cache
############################################

cdef class MonoDictEraser:
    """
    Erase items from a :class:`MonoDict` when a weak reference becomes
    invalid.

    This is of internal use only. Instances of this class will be passed as a
    callback function when creating a weak reference.

    EXAMPLES::

        sage: from sage.structure.coerce_dict import MonoDict
        sage: class A: pass
        sage: a = A()
        sage: M = MonoDict(11)
        sage: M[a] = 1
        sage: len(M)
        1
        sage: del a
        sage: import gc
        sage: n = gc.collect()
        sage: len(M)    # indirect doctest
        0

    AUTHOR:

    - Simon King (2012-01)
    """
    def __init__(self, D):
        """
        INPUT:

        A :class:`MonoDict`.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict, MonoDictEraser
            sage: D = MonoDict(11)
            sage: MonoDictEraser(D)
            <sage.structure.coerce_dict.MonoDictEraser object at ...>
        """
        self.D = ref(D)

    def __call__(self, r):
        """
        INPUT:

        A weak reference with key.

        When this is called with a weak reference ``r``, then each item
        containing ``r`` is removed from the associated :class:`MonoDict`.
        Normally, this only happens when a weak reference becomes invalid.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: class A: pass
            sage: a = A()
            sage: M = MonoDict(11)
            sage: M[a] = 1
            sage: len(M)
            1
            sage: del a
            sage: import gc
            sage: n = gc.collect()
            sage: len(M)    # indirect doctest
            0
        """
        # r is a (weak) reference (typically to a parent),
        # and it knows the stored key of the unique singleton r() had been part
        # of.
        # We remove that unique tuple from self.D -- if self.D is still there!

        #WARNING! These callbacks can happen during the addition of items to the same
        #dictionary. The addition code may then be in the process of adding a new entry
        #(one PyList_Append call at a time) to the relevant bucket.
        #The "PyList_GET_SIZE(bucket) by 3" call should mean that we round down and hence not look
        #at incomplete entries. Furthermore, deleting a slice out of a buck should still be OK.
        #this callback code should absolutely not resize the dictionary, because that would wreak
        #complete havoc.

        cdef MonoDict D = <object> PyWeakref_GetObject(self.D)
        if D is None:
            return
        cdef list buckets = D.buckets
        if buckets is None:
            return
        cdef Py_ssize_t h = r.key
        cdef list bucket = <object>PyList_GET_ITEM(buckets, (<size_t>h) % PyList_GET_SIZE(buckets))
        cdef Py_ssize_t i
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 3:
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket,i))==h:
                del bucket[i:i+3]
                D._size -= 1
                break

cdef class TripleDictEraser:
    """
    Erases items from a :class:`TripleDict` when a weak reference becomes
    invalid.

    This is of internal use only. Instances of this class will be passed as a
    callback function when creating a weak reference.

    EXAMPLES::

        sage: from sage.structure.coerce_dict import TripleDict
        sage: class A: pass
        sage: a = A()
        sage: T = TripleDict(11)
        sage: T[a,ZZ,None] = 1
        sage: T[ZZ,a,1] = 2
        sage: T[a,a,ZZ] = 3
        sage: len(T)
        3
        sage: del a
        sage: import gc
        sage: n = gc.collect()
        sage: len(T)
        0

    AUTHOR:

    - Simon King (2012-01)
    """
    def __init__(self, D):
        """
        INPUT:

        A :class:`TripleDict`.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict, TripleDictEraser
            sage: D = TripleDict(11)
            sage: TripleDictEraser(D)
            <sage.structure.coerce_dict.TripleDictEraser object at ...>

        """
        self.D = ref(D)

    def __call__(self, r):
        """
        INPUT:

        A weak reference with key.

        When this is called with a weak reference ``r``, then each item
        containing ``r`` is removed from the associated :class:`TripleDict`.
        Normally, this only happens when a weak reference becomes invalid.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: class A: pass
            sage: a = A()
            sage: T = TripleDict(11)
            sage: T[a,ZZ,None] = 1
            sage: T[ZZ,a,1] = 2
            sage: T[a,a,ZZ] = 3
            sage: len(T)
            3
            sage: del a
            sage: import gc
            sage: n = gc.collect()
            sage: len(T)    # indirect doctest
            0
        """

        #WARNING! These callbacks can happen during the addition of items to the same
        #dictionary. The addition code may then be in the process of adding a new entry
        #(one PyList_Append call at a time) to the relevant bucket.
        #The "PyList_GET_SIZE(bucket) by 3" call should mean that we round down and hence not look
        #at incomplete entries. Furthermore, deleting a slice out of a buck should still be OK.
        #this callback code should absolutely not resize the dictionary, because that would wreak
        #complete havoc.

        cdef TripleDict D = <object>PyWeakref_GetObject(self.D)
        if D is None:
            return
        cdef list buckets = D.buckets
        if buckets is None:
            return
        # r is a (weak) reference (typically to a parent), and it knows the
        # stored key of the unique triple r() had been part of.
        # We remove that unique triple from self.D
        cdef Py_ssize_t k1,k2,k3
        k1,k2,k3 = r.key
        cdef Py_ssize_t h = (k1 + 13*k2 ^ 503*k3)
        cdef list bucket = <object>PyList_GET_ITEM(buckets, (<size_t>h) % PyList_GET_SIZE(buckets))
        cdef Py_ssize_t i
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 7:
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i))==k1 and \
               PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+1))==k2 and \
               PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+2))==k3:
                del bucket[i:i+7]
                D._size -= 1
                break

cdef class MonoDict:
    """
    This is a hashtable specifically designed for (read) speed in
    the coercion model.

    It differs from a python WeakKeyDictionary in the following important way:

       - Comparison is done using the 'is' rather than '==' operator.
       - Only weak references to the keys are stored if at all possible.
         Keys that do not allow for weak references are stored with a normal
         refcounted reference.

    There are special cdef set/get methods for faster access.
    It is bare-bones in the sense that not all dictionary methods are
    implemented.

    It is implemented as a list of lists (hereafter called buckets). The bucket
    is chosen according to a very simple hash based on the object pointer,
    and each bucket is of the form [id(k1), r1, value1, id(k2), r2, value2, ...],
    on which a linear search is performed.

    If ki supports weak references then ri is a weak reference to ki with a
    callback to remove the entry from the dictionary if ki gets garbage
    collected. If ki is does not support weak references then ri is identical to ki.
    In the latter case the presence of the key in the dictionary prevents it from
    being garbage collected.

    To spread objects evenly, the size should ideally be a prime, and certainly
    not divisible by 2.

    EXAMPLES::

        sage: from sage.structure.coerce_dict import MonoDict
        sage: L = MonoDict(31)
        sage: a = 'a'; b = 'ab'; c = -15
        sage: L[a] = 1
        sage: L[b] = 2
        sage: L[c] = 3

    The key is expected to be a unique object. Hence, the item stored for ``c``
    can not be obtained by providing another equal number::

        sage: L[a]
        1
        sage: L[b]
        2
        sage: L[c]
        3
        sage: L[-15]
        Traceback (most recent call last):
        ...
        KeyError: -15

    Not all features of Python dictionaries are available, but iteration over
    the dictionary items is possible::

        sage: # for some reason the following fails in "make ptest"
        sage: # on some installations, see #12313 for details
        sage: sorted(L.iteritems()) # random layout
        [(-15, 3), ('a', 1), ('ab', 2)]
        sage: # the following seems to be more consistent
        sage: set(L.iteritems())
        set([('a', 1), ('ab', 2), (-15, 3)])
        sage: del L[c]
        sage: sorted(L.iteritems())
        [('a', 1), ('ab', 2)]
        sage: len(L)
        2
        sage: L.stats()             # random
        (0, 0.06451..., 1)
        sage: L.bucket_lens()       # random layout
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]
        sage: for i in range(1000):
        ...       L[i] = i
        sage: len(L)
        1002
        sage: L.stats()             # random
        (26, 32.32258064516129, 37)
        sage: L.bucket_lens()       # random layout
        [32, 34, 31, 32, 33, 32, 32, 33, 34, 31, 32, 32, 31, 31, 32, 34, 31, 33, 34, 32, 32, 33, 33, 31, 33, 35, 32, 32, 32, 32, 31]
        sage: L = MonoDict(101, L)
        sage: L.stats()             # random
        (8, 9.92079207920792, 12)
        sage: L = MonoDict(3, L)
        sage: L.stats()             # random
        (0, 334.0, 985)
        sage: L['a']
        1
        sage: L['c']
        Traceback (most recent call last):
        ...
        KeyError: 'c'

    The following illustrates why even sizes are bad::

        sage: L = MonoDict(4, L, threshold=0)
        sage: L.stats()
        (0, 250.5, 1002)
        sage: L.bucket_lens()
        [1002, 0, 0, 0]

    Note that this kind of dictionary is also used for caching actions
    and coerce maps. In previous versions of Sage, the cache was by
    strong references and resulted in a memory leak in the following
    example. However, this leak was fixed by :trac:`715`, using
    weak references::

        sage: K = GF(1<<55,'t')
        sage: for i in range(50):
        ...     a = K.random_element()
        ...     E = EllipticCurve(j=a)
        ...     P = E.random_point()
        ...     Q = 2*P
        sage: import gc
        sage: n = gc.collect()
        sage: from sage.schemes.elliptic_curves.ell_finite_field import EllipticCurve_finite_field
        sage: LE = [x for x in gc.get_objects() if isinstance(x, EllipticCurve_finite_field)]
        sage: len(LE)    # indirect doctest
        1

    AUTHOR:

    - Simon King (2012-01)
    - Nils Bruin (2012-08)
    """
    def __init__(self, size, data=None, threshold=0.7):
        """
        Create a special dict using singletons for keys.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(31)
            sage: a = 'a'
            sage: L[a] = 1
            sage: L[a]
            1
        """
        cdef Py_ssize_t i
        self.threshold = threshold
        self.buckets = [[] for i from 0 <= i < size]
        self._size = 0
        self.eraser = MonoDictEraser(self)
        if data is not None:
            for k, v in data.iteritems():
                self.set(k,v)

    def __len__(self):
        """
        The number of items in self.
        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(37)
            sage: a = 'a'; b = 'b'; c = 'c'
            sage: L[a] = 1
            sage: L[a] = -1 # re-assign
            sage: L[b] = 1
            sage: L[c] = None
            sage: len(L)
            3
        """
        return self._size

    def stats(self):
        """
        The distribution of items in buckets.

        OUTPUT:

        - (min, avg, max)

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(37)
            sage: for i in range(100): L[i] = None
            sage: L.stats() # random
            (2, 2.7027027027027026, 4)

            sage: L = MonoDict(3007)
            sage: for i in range(100): L[i] = None
            sage: L.stats() # random
            (0, 0.03325573661456601, 1)

            sage: L = MonoDict(1,threshold=0)
            sage: for i in range(100): L[i] = None
            sage: L.stats()
            (100, 100.0, 100)
        """
        cdef Py_ssize_t size = self._size
        cdef Py_ssize_t cur, min = size, max = 0
        for bucket in self.buckets:
            if bucket:
                cur = len(bucket)/3
                if cur < min: min = cur
                if cur > max: max = cur
            else:
                min = 0
        return min, 1.0*size/len(self.buckets), max

    def bucket_lens(self):
        """
        The distribution of items in buckets.

        OUTPUT:

        A list of how many items are in each bucket.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(37)
            sage: for i in range(100): L[i] = None
            sage: L.bucket_lens() # random
            [3, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 3, 3, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 3, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4]
            sage: sum(L.bucket_lens())
            100

            sage: L = MonoDict(1,threshold=0)
            sage: for i in range(100): L[i] = None
            sage: L.bucket_lens()
            [100]
        """
        return [len(self.buckets[i])/3 for i from 0 <= i < len(self.buckets)]

    def _get_buckets(self):
        """
        The actual buckets of self, for debugging.

        EXAMPLE::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(3)
            sage: L[0] = None
            sage: L._get_buckets() # random
            [[0, None], [], []]
        """
        return self.buckets

    def __contains__(self, k):
        """
        Test if the dictionary contains a given key.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(31)
            sage: a = 'a'; b = 'ab'; c = 15
            sage: L[a] = 1
            sage: L[b] = 2
            sage: L[c] = 3
            sage: c in L         # indirect doctest
            True

        The keys are compared by identity, not by equality. Hence, we have::

            sage: c == 15
            True
            sage: 15 in L
            False
        """
        cdef Py_ssize_t h = <Py_ssize_t><void *>k
        cdef Py_ssize_t i
        cdef list all_buckets = self.buckets
        cdef list bucket = <object>PyList_GET_ITEM(all_buckets, (<size_t>h)% PyList_GET_SIZE(all_buckets))
        cdef object r
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 3:
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i)) == h:
                r = <object>PyList_GET_ITEM(bucket, i+1)
                if isinstance(r, KeyedRef) and PyWeakref_GetObject(r) == Py_None:
                    return False
                else:
                    return True
        return False

    def __getitem__(self, k):
        """
        Get the value corresponding to a key.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(31)
            sage: a = 'a'; b = 'b'; c = 15
            sage: L[a] = 1
            sage: L[b] = 2
            sage: L[c] = 3
            sage: L[c]                  # indirect doctest
            3

        Note that the keys are supposed to be unique::

            sage: c==15
            True
            sage: c is 15
            False
            sage: L[15]
            Traceback (most recent call last):
            ...
            KeyError: 15
        """
        return self.get(k)

    cdef get(self, object k):
        cdef Py_ssize_t h =<Py_ssize_t><void *>k
        cdef Py_ssize_t i
        cdef list all_buckets = self.buckets
        cdef list bucket = <object>PyList_GET_ITEM(all_buckets, (<size_t>h) % PyList_GET_SIZE(all_buckets))
        cdef object r
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 3:
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i)) == h:
                r = <object>PyList_GET_ITEM(bucket, i+1)
                if isinstance(r, KeyedRef) and PyWeakref_GetObject(r) == Py_None:
                    raise KeyError, k
                else:
                    return <object>PyList_GET_ITEM(bucket, i+2)
        raise KeyError, k

    def __setitem__(self, k, value):
        """
        Set the value corresponding to a key.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(31)
            sage: a = 'a'
            sage: L[a] = -1   # indirect doctest
            sage: L[a]
            -1
            sage: L[a] = 1
            sage: L[a]
            1
            sage: len(L)
            1
        """
        self.set(k,value)

    cdef set(self,object k, value):
        if self.threshold and self._size > len(self.buckets) * self.threshold:
            self.resize()
        cdef Py_ssize_t h = <Py_ssize_t><void *>k
        cdef Py_ssize_t i
        cdef list bucket = <object>PyList_GET_ITEM(self.buckets,(<size_t> h) % PyList_GET_SIZE(self.buckets))
        cdef object r
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 3:
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i)) == h:
                r = <object>PyList_GET_ITEM(bucket, i+1)
                if isinstance(r, KeyedRef) and PyWeakref_GetObject(r) == Py_None:
                    #uh oh, an entry has died and has not received a callback yet.
                    #that callback might still be out there! safest thing is to simply remove the entry and
                    #append a new one below.

                    #We checked that slice deletion is safe: Python will save references the the removed items,
                    #rearrange the list (so no references exist there anymore!) and only THEN delete the
                    #items. Therefore, any code that executes upon deallocation will see the bucket in its
                    #new, consistent form already.
                    del bucket[i:i+3]
                    self._size -=1
                    #by now we believe dangling weakref is well and truly gone. If python still has its callback
                    #scheduled somewhere, we think it's in breach of contract.
                    break
                else:
                    #key is present and still alive. We can just store the value.
                    bucket[i+2] = value
                    return
        #key id was not present, or was storing a dead reference, which has now been removed.

        #the following code fragment may allocate new memory and hence may trigger garbage collections.
        #that means it can also trigger callbacks that removes entries from the bucket
        #we are adding to. However, as long as such callbacks never ADD anything to buckets,
        #we're still OK building up our entry by adding entries at the end of it.
        #Note that the bucket list will only have increased by a multiple of 3 in length
        #after `value` has successfully been added, i.e, once the entry is complete. That means any
        #search in the bucket list by a callback will round len(bucket)/3 DOWN and hence not
        #investigate our partial entry.
        PyList_Append(bucket, h)
        try:
            PyList_Append(bucket, KeyedRef(k,self.eraser,h))
        except TypeError:
            PyList_Append(bucket, k)
        PyList_Append(bucket, value)
        self._size += 1

    def __delitem__(self, k):
        """
        Delete the value corresponding to a key.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(31)
            sage: a = 15
            sage: L[a] = -1
            sage: len(L)
            1

        Note that the keys are unique, hence using a key that is equal but not
        identical to a results in an error::

            sage: del L[15]
            Traceback (most recent call last):
            ...
            KeyError: 15
            sage: a in L
            True
            sage: del L[a]
            sage: len(L)
            0
            sage: a in L
            False
        """
        cdef Py_ssize_t h = <Py_ssize_t><void *>k
        cdef object r
        cdef Py_ssize_t i
        cdef object tmp
        cdef list all_buckets = self.buckets
        cdef list bucket = <object>PyList_GET_ITEM(all_buckets, (<size_t>h) % PyList_GET_SIZE(all_buckets))
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 3:
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i)) == h:
                r = <object>PyList_GET_ITEM(bucket, i+1)
                del bucket[i:i+3]
                self._size -= 1
                if isinstance(r, KeyedRef) and PyWeakref_GetObject(r) == Py_None:
                    break
                else:
                    return
        raise KeyError, k

    def resize(self, int buckets=0):
        """
        Change the number of buckets of self, while preserving the contents.

        If the number of buckets is 0 or not given, it resizes self to the
        smallest prime that is at least twice as large as self.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(8)
            sage: for i in range(100): L[i] = None
            sage: L.bucket_lens() # random
            [50, 0, 0, 0, 50, 0, 0, 0]
            sage: L.resize(7)
            sage: L.bucket_lens() # random
            [15, 14, 14, 14, 14, 15, 14]
            sage: L.resize()
            sage: len(L.bucket_lens())
            17
        """
        if buckets == 0:
            buckets = next_odd_prime(2*len(self.buckets))
        cdef list old_buckets = self.buckets
        cdef list bucket
        cdef Py_ssize_t i
        cdef Py_ssize_t h
        cdef list new_buckets = [[] for i from 0 <= i <  buckets]
        cdef object r
        cdef object v

        #this would be a very bad place for a garbage collection to happen
        #so we disable them.
        cdef bint gc_originally_enabled = gc.isenabled()
        if gc_originally_enabled:
            gc.disable()

        #BEGIN of critical block. NO GC HERE!
        for bucket in old_buckets:
            for i from 0 <= i < PyList_GET_SIZE(bucket) by 3:
                h = PyInt_AsSsize_t(PyList_GET_ITEM(bucket,i))
                r  = <object>PyList_GET_ITEM(bucket,i+1)
                v  = <object>PyList_GET_ITEM(bucket,i+2)
                #this line can trigger allocation, so GC must be turned off!
                new_buckets[(<size_t>h) % buckets] += [h,r,v]
        self.buckets = new_buckets
        #END of critical block. The dict is consistent again.

        if gc_originally_enabled:
            gc.enable()

    def iteritems(self):
        """
        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(31)
            sage: L[1] = None
            sage: L[2] = True
            sage: list(sorted(L.iteritems()))
            [(1, None), (2, True)]
        """
        cdef list bucket
        cdef Py_ssize_t i
        # We test whether the references are still valid.
        # However, we must not delete them, since we are
        # iterating.
        for bucket in self.buckets:
            for i from 0<=i<len(bucket) by 3:
                r = <object>PyList_GET_ITEM(bucket,i+1)
                if isinstance(r, KeyedRef):
                    r = <object>PyWeakref_GetObject(r)
                    if r is None:
                        continue
                yield r, <object>PyList_GET_ITEM(bucket,i+2)


    def __reduce__(self):
        """
        Note that we don't expect equality as this class concerns itself with
        object identity rather than object equality.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import MonoDict
            sage: L = MonoDict(31)
            sage: L[1] = True
            sage: loads(dumps(L)) == L
            False
            sage: list(loads(dumps(L)).iteritems())
            [(1, True)]
        """
        return MonoDict, (len(self.buckets), dict(self.iteritems()), self.threshold)

cdef class TripleDict:
    """
    This is a hashtable specifically designed for (read) speed in
    the coercion model.

    It differs from a python dict in the following important ways:

       - All keys must be sequence of exactly three elements. All sequence
         types (tuple, list, etc.) map to the same item.
       - Comparison is done using the 'is' rather than '==' operator.

    There are special cdef set/get methods for faster access.
    It is bare-bones in the sense that not all dictionary methods are
    implemented.

    It is implemented as a list of lists (hereafter called buckets). The bucket is
    chosen according to a very simple hash based on the object pointer, and each
    bucket is of the form [id(k1), id(k2), id(k3), r1, r2, r3, value, id(k1),
    id(k2), id(k3), r1, r2, r3, value, ...], on which a linear search is performed.
    If a key component ki supports weak references then ri is a weak reference to
    ki; otherwise ri is identical to ki.

    If any of the key components k1,k2,k3 (this can happen for a key component that
    supports weak references) gets garbage collected then the entire entry
    disappears. In that sense this structure behaves like a nested WeakKeyDictionary.

    To spread objects evenly, the size should ideally be a prime, and certainly
    not divisible by 2.

    EXAMPLES::

        sage: from sage.structure.coerce_dict import TripleDict
        sage: L = TripleDict(31)
        sage: a = 'a'; b = 'b'; c = 'c'
        sage: L[a,b,c] = 1
        sage: L[a,b,c]
        1
        sage: L[c,b,a] = -1
        sage: list(L.iteritems())     # random order of output.
        [(('c', 'b', 'a'), -1), (('a', 'b', 'c'), 1)]
        sage: del L[a,b,c]
        sage: list(L.iteritems())
        [(('c', 'b', 'a'), -1)]
        sage: len(L)
        1
        sage: L.stats()             # min, avg, max (bucket length)
        (0, 0.03225806451612903, 1)
        sage: L.bucket_lens()       # random layout
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        sage: for i in range(1000):
        ...       L[i,i,i] = i
        sage: len(L)
        1001
        sage: L.stats()             # random
        (31, 32.29032258064516, 35)
        sage: L.bucket_lens()       # random layout
        [33, 34, 32, 32, 35, 32, 31, 33, 34, 31, 32, 34, 32, 31, 31, 32, 32, 31, 31, 33, 32, 32, 32, 33, 33, 33, 31, 33, 33, 32, 31]
        sage: L = TripleDict(101, L)
        sage: L.stats()             # random
        (8, 9.9108910891089117, 11)
        sage: L = TripleDict(3, L)
        sage: L.stats()             # random
        (291, 333.66666666666669, 410)
        sage: L[c,b,a]
        -1
        sage: L[a,b,c]
        Traceback (most recent call last):
        ...
        KeyError: ('a', 'b', 'c')
        sage: L[a]
        Traceback (most recent call last):
        ...
        KeyError: 'a'
        sage: L[a] = 1
        Traceback (most recent call last):
        ...
        KeyError: 'a'

    The following illustrates why even sizes are bad (setting the threshold
    zero, so that no beneficial resizing happens)::

        sage: L = TripleDict(4, L, threshold=0)
        sage: L.stats()
        (0, 250.25, 1001)
        sage: L.bucket_lens()
        [1001, 0, 0, 0]

    Note that this kind of dictionary is also used for caching actions
    and coerce maps. In previous versions of Sage, the cache was by
    strong references and resulted in a memory leak in the following
    example. However, this leak was fixed by :trac:`715`, using weak
    references::

        sage: K = GF(1<<55,'t')
        sage: for i in range(50):
        ...     a = K.random_element()
        ...     E = EllipticCurve(j=a)
        ...     P = E.random_point()
        ...     Q = 2*P
        sage: import gc
        sage: n = gc.collect()
        sage: from sage.schemes.elliptic_curves.ell_finite_field import EllipticCurve_finite_field
        sage: LE = [x for x in gc.get_objects() if isinstance(x, EllipticCurve_finite_field)]
        sage: len(LE)    # indirect doctest
        1

    .. NOTE::

        The index `h` corresponding to the key [k1, k2, k3] is computed as a
        value of unsigned type size_t as follows:

        .. MATH::

            h = id(k1) + 13*id(k2) xor 503 id(k3)

        The natural type for this quantity is Py_ssize_t, which is a signed
        quantity with the same length as size_t. Storing it in a signed way gives the most
        efficient storage into PyInt, while preserving sign information.

        As usual for a hashtable, we take h modulo some integer to obtain the bucket
        number into which to store the key/value pair. A problem here is that C mandates
        sign-preservation for the modulo operator "%". We cast to an unsigned type, i.e.,
        (<size_t> h)% N
        If we don't do this we may end up indexing lists with negative indices, which may lead to
        segfaults if using the non-error-checking python macros, as happens here.

        This has been observed on 32 bits systems, see :trac:`715` for details.

    AUTHORS:

    - Robert Bradshaw, 2007-08

    - Simon King, 2012-01

    - Nils Bruin, 2012-08
    """

    def __init__(self, size, data=None, threshold=0.7):
        """
        Create a special dict using triples for keys.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(31)
            sage: a = 'a'; b = 'b'; c = 'c'
            sage: L[a,b,c] = 1
            sage: L[a,b,c]
            1
        """
        cdef int i
        self.threshold = threshold
        self.buckets = [[] for i from 0 <= i <  size]
        self._size = 0
        self.eraser = TripleDictEraser(self)
        if data is not None:
            for (k1,k2,k3), v in data.iteritems():
                self.set(k1,k2,k3, v)

    def __len__(self):
        """
        The number of items in self.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(37)
            sage: a = 'a'; b = 'b'; c = 'c'
            sage: L[a,b,c] = 1
            sage: L[a,b,c] = -1 # re-assign
            sage: L[a,c,b] = 1
            sage: L[a,a,None] = None
            sage: len(L)
            3
        """
        return self._size

    def stats(self):
        """
        The distribution of items in buckets.

        OUTPUT:

        - (min, avg, max)

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(37)
            sage: for i in range(100): L[i,i,i] = None
            sage: L.stats() # random
            (2, 2.7027027027027026, 4)

            sage: L = TripleDict(3007)
            sage: for i in range(100): L[i,i,i] = None
            sage: L.stats() # random
            (0, 0.03325573661456601, 1)

        In order to have a test that isn't random, we use parameters
        that should not be used in real applications::

            sage: L = TripleDict(1, threshold=0)
            sage: for i in range(100): L[i,i,i] = None
            sage: L.stats()
            (100, 100.0, 100)
        """
        cdef Py_ssize_t size = self._size
        cdef Py_ssize_t cur, min = size, max = 0
        for bucket in self.buckets:
            if bucket:
                cur = len(bucket)/7
                if cur < min: min = cur
                if cur > max: max = cur
            else:
                min = 0
        return min, 1.0*size/len(self.buckets), max

    def bucket_lens(self):
        """
        The distribution of items in buckets.

        OUTPUT:

        A list of how many items are in each bucket.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(37, threshold=0)
            sage: for i in range(100): L[i,i,i] = None
            sage: L.bucket_lens() # random
            [3, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 3, 3, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 3, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4]
            sage: sum(L.bucket_lens())
            100

        In order to have a test that isn't random, we use parameters
        that should not be used in real applications::

            sage: L = TripleDict(1, threshold=0)
            sage: for i in range(100): L[i,i,i] = None
            sage: L.bucket_lens()
            [100]
        """
        return [len(self.buckets[i])/7 for i from 0 <= i < len(self.buckets)]

    def _get_buckets(self):
        """
        The actual buckets of self, for debugging.

        EXAMPLE::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(3)
            sage: L[0,0,0] = None
            sage: L._get_buckets() # random
            [[0, 0, 0, None], [], []]
        """
        return self.buckets

    def __contains__(self, k):
        """
        Test if the dictionary contains a given key.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(31)
            sage: a = 'a'; b = 'ab'; c = 15
            sage: L[a,b,c] = 123
            sage: (a,b,c) in L         # indirect doctest
            True

        The keys are compared by identity, not by equality. Hence, we have::

            sage: c == 15
            True
            sage: (a,b,15) in L
            False
        """
        cdef object k1,k2,k3
        try:
            k1, k2, k3 = k
        except (TypeError,ValueError):
            return False
        try:
            self.get(k1,k2,k3)
        except KeyError:
            return False
        return True

    def __getitem__(self, k):
        """
        Get the value corresponding to a key.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(31)
            sage: a = 'a'; b = 'b'; c = 'c'
            sage: L[a,b,c] = 1
            sage: L[a,b,c]
            1
        """
        cdef object k1,k2,k3
        try:
            k1, k2, k3 = k
        except (TypeError,ValueError):
            raise KeyError, k
        return self.get(k1, k2, k3)

    cdef get(self, object k1, object k2, object k3):
        cdef Py_ssize_t h1 = <Py_ssize_t><void *>k1
        cdef Py_ssize_t h2 = <Py_ssize_t><void *>k2
        cdef Py_ssize_t h3 = <Py_ssize_t><void *>k3
        cdef Py_ssize_t h = (h1 + 13*h2 ^ 503*h3)

        cdef object r1,r2,r3
        cdef Py_ssize_t i
        cdef list all_buckets = self.buckets
        cdef list bucket = <object>PyList_GET_ITEM(all_buckets, (<size_t>h )% PyList_GET_SIZE(all_buckets))
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 7:
            tmp = <object>PyList_GET_ITEM(bucket, i)
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i)) == h1 and \
                   PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+1)) == h2 and \
                   PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+2)) == h3:
                r1 = <object>PyList_GET_ITEM(bucket, i+3)
                r2 = <object>PyList_GET_ITEM(bucket, i+4)
                r3 = <object>PyList_GET_ITEM(bucket, i+5)
                if (isinstance(r1,KeyedRef) and PyWeakref_GetObject(r1) == Py_None) or \
                        (isinstance(r2,KeyedRef) and PyWeakref_GetObject(r2) == Py_None) or \
                        (isinstance(r3,KeyedRef) and PyWeakref_GetObject(r3) == Py_None):
                    raise KeyError, (k1,k2,k3)
                else:
                    return <object>PyList_GET_ITEM(bucket, i+6)
        raise KeyError, (k1, k2, k3)

    def __setitem__(self, k, value):
        """
        Set the value corresponding to a key.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(31)
            sage: a = 'a'; b = 'b'; c = 'c'
            sage: L[a,b,c] = -1
            sage: L[a,b,c]
            -1
        """
        cdef object k1,k2,k3
        try:
            k1, k2, k3 = k
        except (TypeError,ValueError):
            raise KeyError, k
        self.set(k1, k2, k3, value)

    cdef set(self, object k1, object k2, object k3, value):
        if self.threshold and self._size > len(self.buckets) * self.threshold:
            self.resize()
        cdef Py_ssize_t h1 = <Py_ssize_t><void *>k1
        cdef Py_ssize_t h2 = <Py_ssize_t><void *>k2
        cdef Py_ssize_t h3 = <Py_ssize_t><void *>k3
        cdef Py_ssize_t h = (h1 + 13*h2 ^ 503*h3)

        cdef object r1,r2,r3
        cdef Py_ssize_t i
        cdef list all_buckets = self.buckets
        cdef list bucket = <object>PyList_GET_ITEM(all_buckets, (<size_t>h) % PyList_GET_SIZE(all_buckets))
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 7:
            tmp = <object>PyList_GET_ITEM(bucket, i)
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i)) == h1 and \
                   PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+1)) == h2 and \
                   PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+2)) == h3:
                r1 = <object>PyList_GET_ITEM(bucket, i+3)
                r2 = <object>PyList_GET_ITEM(bucket, i+4)
                r3 = <object>PyList_GET_ITEM(bucket, i+5)
                if (isinstance(r1,KeyedRef) and PyWeakref_GetObject(r1) == Py_None) or \
                        (isinstance(r2,KeyedRef) and PyWeakref_GetObject(r2) == Py_None) or \
                        (isinstance(r3,KeyedRef) and PyWeakref_GetObject(r3) == Py_None):
                    #apparently one of the keys has died but the callback hasn't executed yet.
                    #we delete the whole entry (including the weakrefs) and hope that this
                    #purges the callbacks too (it should, because the weakref doesn't
                    #exist anymore. In particular it cannot be passed as a parameter to
                    #the callback anymore)
                    del bucket[i:i+7]
                    self._size -= 1
                else:
                    #keys are present and alive, so we can just store the new value
                    bucket[i+6]=value
                    return

        #at this point the key triple isn't present so we append a new entry.
        #we first form the appropriate weakrefs to receive callbacks on.
        try:
            r1 = KeyedRef(k1,self.eraser,(h1, h2, h3))
        except TypeError:
            r1 = k1
        if k2 is not k1:
            try:
                r2 = KeyedRef(k2,self.eraser,(h1, h2, h3))
            except TypeError:
                r2 = k2
        else:
            r2 = None
        if k3 is not k2 or k3 is not k1:
            try:
                r3 = KeyedRef(k3,self.eraser,(h1, h2, h3))
            except TypeError:
                r3 = k3
        else:
            r3 = None
        PyList_Append(bucket, h1)
        PyList_Append(bucket, h2)
        PyList_Append(bucket, h3)
        PyList_Append(bucket, r1)
        PyList_Append(bucket, r2)
        PyList_Append(bucket, r3)
        PyList_Append(bucket, value)
        self._size += 1

    def __delitem__(self, k):
        """
        Delete the value corresponding to a key.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(31)
            sage: a = 'a'; b = 'b'; c = 'c'
            sage: L[a,b,c] = -1
            sage: (a,b,c) in L
            True
            sage: del L[a,b,c]
            sage: len(L)
            0
            sage: (a,b,c) in L
            False
        """
        cdef object k1,k2,k3
        cdef object r1,r2,r3
        try:
            k1, k2, k3 = k
        except (TypeError,ValueError):
            raise KeyError, k
        cdef Py_ssize_t h1 = <Py_ssize_t><void *>k1
        cdef Py_ssize_t h2 = <Py_ssize_t><void *>k2
        cdef Py_ssize_t h3 = <Py_ssize_t><void *>k3
        cdef Py_ssize_t h = (h1 + 13*h2 ^ 503*h3)

        cdef Py_ssize_t i
        cdef list all_buckets = self.buckets
        cdef list bucket = <object>PyList_GET_ITEM(all_buckets, (<size_t>h) % PyList_GET_SIZE(all_buckets))
        for i from 0 <= i < PyList_GET_SIZE(bucket) by 7:
            if PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i)) == h1 and \
                   PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+1)) == h2 and \
                   PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+2)) == h3:
                r1 = <object>PyList_GET_ITEM(bucket, i+3)
                r2 = <object>PyList_GET_ITEM(bucket, i+4)
                r3 = <object>PyList_GET_ITEM(bucket, i+5)
                del bucket[i:i+7]
                self._size -= 1
                if (isinstance(r1,KeyedRef) and PyWeakref_GetObject(r1) == Py_None) or \
                        (isinstance(r2,KeyedRef) and PyWeakref_GetObject(r2) == Py_None) or \
                        (isinstance(r3,KeyedRef) and PyWeakref_GetObject(r3) == Py_None):
                    #the entry was already dead
                    break
                else:
                    return
        raise KeyError, k

    def resize(self, int buckets=0):
        """
        Change the number of buckets of self, while preserving the contents.

        If the number of buckets is 0 or not given, it resizes self to the
        smallest prime that is at least twice as large as self.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(8)
            sage: for i in range(100): L[i,i,i] = None
            sage: L.bucket_lens() # random
            [50, 0, 0, 0, 50, 0, 0, 0]
            sage: L.resize(7) # random
            [15, 14, 14, 14, 14, 15, 14]
            sage: L.resize()
            sage: len(L.bucket_lens())
            17
        """
        if buckets == 0:
            buckets = next_odd_prime(2*len(self.buckets))
        cdef list old_buckets = self.buckets
        cdef list bucket
        cdef Py_ssize_t i
        cdef Py_ssize_t h
        cdef list new_buckets = [[] for i from 0 <= i <  buckets]
        cdef Py_ssize_t k1,k2,k3

        #this would be a very bad place for a garbage collection to happen
        #so we disable them.
        cdef bint gc_originally_enabled = gc.isenabled()
        if gc_originally_enabled:
            gc.disable()

        #BEGIN of critical block. NO GC HERE!
        for bucket in old_buckets:
            for i from 0 <= i < PyList_GET_SIZE(bucket) by 7:
                k1 = PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i))
                k2 = PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+1))
                k3 = PyInt_AsSsize_t(PyList_GET_ITEM(bucket, i+2))
                h = (k1 + 13*k2 ^ 503*k3)
                #this line can trigger allocation, so GC must be turned off!
                new_buckets[(<size_t> h) % buckets] += bucket[i:i+7]
        self.buckets = new_buckets
        #END of critical block. The dict is consistent again.

        if gc_originally_enabled:
            gc.enable()

    def iteritems(self):
        """
        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(31)
            sage: L[1,2,3] = None
            sage: list(L.iteritems())
            [((1, 2, 3), None)]
        """
        cdef list bucket
        cdef Py_ssize_t i
        cdef object r1,r2,r3
        # We test whether the references are still valid.
        # However, we must not delete them, since we are
        # iterating.
        for bucket in self.buckets:
            for i from 0<=i<len(bucket) by 7:
                r1,r2,r3 = bucket[i+3:i+6]
                if isinstance(r1, KeyedRef):
                    r1 = <object>PyWeakref_GetObject(r1)
                    if r1 is None:
                        continue
                if isinstance(r2, KeyedRef):
                    r2 = <object>PyWeakref_GetObject(r2)
                    if r2 is None:
                        continue
                if isinstance(r3, KeyedRef):
                    r3 = <object>PyWeakref_GetObject(r3)
                    if r3 is None:
                        continue
                yield (r1,r2,r3), <object>PyList_GET_ITEM(bucket,i+6)

    def __reduce__(self):
        """
        Note that we don't expect equality as this class concerns itself with
        object identity rather than object equality.

        EXAMPLES::

            sage: from sage.structure.coerce_dict import TripleDict
            sage: L = TripleDict(31)
            sage: L[1,2,3] = True
            sage: loads(dumps(L)) == L
            False
            sage: list(loads(dumps(L)).iteritems())
            [((1, 2, 3), True)]
        """
        return TripleDict, (len(self.buckets), dict(self.iteritems()), self.threshold)

cdef long next_odd_prime(long n):
    if n % 2 == 0:
        n -= 1
    cdef long k
    while n > 0:
        n += 2
        k = 3
        while k*k <= n:
            if n % k == 0:
                break
            k += 2
        if k*k > n:
            return n
