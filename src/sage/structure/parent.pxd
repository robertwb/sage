###############################################################################
#   SAGE: System for Algebra and Geometry Experimentation
#       Copyright (C) 2006 William Stein <wstein@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

#cimport sage.categories.object
cimport sage.structure.category_object


cdef class Parent(category_object.CategoryObject):

    cdef public _element_class
    cdef public _convert_method_name
    cdef public bint _element_init_pass_parent
    cdef public _initial_coerce_list
    cdef public _initial_action_list
    cdef public _initial_convert_list

    # New New Coercion support functionality

    # returns whether or not there is a Morphism from S to self
    cpdef bint has_coerce_map_from(self, S) except -2
    cpdef bint _has_coerce_map_from_(self, S) except -2

    # returns a Morphism from S to self, or None
    cpdef coerce_map_from(self, S)
    cpdef _coerce_map_from_(self, S)

    # returns a Map from S to self, or None
    cpdef convert_map_from(self, S)
    cpdef _convert_map_from_(self, S)

    # returns the Action by/on self on/by S
    # corresponding to op and self_on_left
    cpdef get_action(self, other, op=*, bint self_on_left=*)
    cpdef _get_action_(self, other, op, bint self_on_left)

    # coerce x into self
    cpdef coerce(self, x)
    cpdef an_element(self)
    cpdef _an_element_(self)


    # For internal use
    cpdef _generic_convert_map(self, S)
    cdef discover_coerce_map_from(self, S)
    cdef discover_convert_map_from(self, S)
    cdef discover_action(self, G, op, bint self_on_left)

    # List consisting of Morphisms (from anything to self)
    # and Parents for which the __call__ method of self
    # results in natural coercion.
    # Initalized at ring creation.
    cdef _coerce_from_list
    # Hashtable of everything we've (possibliy recursively) discovered so far.
    cdef _coerce_from_hash

    # List consisting of Actions (either by or on self)
    # and Parents for which self._rmul_ and/or self._lmul_
    # do the correct thing.
    # Initalized at ring creation.
    cdef _action_list
    # Hashtable of everything we've (possibliy recursively) discovered so far.
    cdef _action_hash

    # List consisting of Morphisms (from anything to self)
    # and Parents for which the __call__ method of self
    # does not result in type errors
    # Initalized at ring creation.
    cdef _convert_from_list
    # Hashtable of everything we've (possibliy recursively) discovered so far.
    cdef _convert_from_hash
    # An optional single Morphism that describes a cannonical coercion out of self
    cdef _embedding


    #########################################

    cdef public object __an_element
    cpdef _an_element_impl(self)
