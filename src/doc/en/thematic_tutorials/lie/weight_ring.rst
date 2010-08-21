------------
Weight Rings
------------

You may wish to work directly with the weights of a representation.

``WeylCharacterRingElements`` are represented internally by a
dictionary of their weights with multiplicities. However these are
subject to a constraint: the coefficients must be invariant under the
action of the Weyl group.

The ``WeightRing`` is also a ring whose elements are represented
internally by a dictionary of their weights with multiplicities, but
it is not subject to this constraint of Weyl group invariance. The
weights are allowed to be fractional, that is, elements of the ambient
space. In other words, the weight ring is the group algebra over the
ambient space of the weight lattice.

To create a ``WeightRing`` first construct the Weyl Character Ring,
then create the ``WeightRing`` as follows::

    sage: A2 = WeylCharacterRing(['A',2])
    sage: a2 = WeightRing(A2)

You may coerce elements of the ``WeylCharacterRing`` into the weight
ring. For example, if you want to see the weights of the adjoint
representation of `GL(3)`, you may use the method ``mlist``, but
another way is to coerce it into the weight ring::

    sage: A2 = WeylCharacterRing(['A',2])
    sage: a2 = WeightRing(A2)
    sage: ad = A2(1,0,-1)
    sage: ad.mlist()
    [[(-1, 1, 0), 1], [(0, 1, -1), 1], [(1, 0, -1), 1], [(0, 0, 0), 2], [(-1, 0, 1), 1],
    [(0, -1, 1), 1], [(1, -1, 0), 1]]
    sage: a2(ad)
    a2(-1,0,1) + a2(-1,1,0) + a2(0,-1,1) + 2*a2(0,0,0) + a2(0,1,-1) + a2(1,-1,0) + a2(1,0,-1)

For example, the Weyl denominator formula is usually written this way:

.. MATH::

    \prod_{\alpha\in\Phi^+}\left(e^{\alpha/2}-e^{-\alpha/2}\right)
    =
    \sum_{w\in W} (-1)^{l(w)}e^{w(\rho)}.

The notation is as follows. Here if `\lambda` is a weight, or more
generally, an element of the ambient space, then `e^\lambda` means the
image of `\lambda` in the group algebra of the ambient space of the
weight lattice `\lambda`. Since this group algebra is just the weight
ring, we can interpret `e^\lambda` as its image in the weight ring.

Let us confirm the Weyl denominator formula for ``A2``::

    sage: A2 = WeylCharacterRing("A2")
    sage: a2 = WeightRing(A2)
    sage: L = A2.space()
    sage: W = L.weyl_group()
    sage: rho = A2.coerce_to_sl(L.rho())
    sage: lhs = prod(a2(alpha/2)-a2(-alpha/2) for alpha in L.positive_roots()); lhs
    -a2(-1,0,1) + a2(-1,1,0) + a2(0,-1,1) - a2(0,1,-1) - a2(1,-1,0) + a2(1,0,-1)
    sage: rhs = sum((-1)^(w.length())*a2(w.action(rho)) for w in W); rhs
    -a2(-1,0,1) + a2(-1,1,0) + a2(0,-1,1) - a2(0,1,-1) - a2(1,-1,0) + a2(1,0,-1)
    sage: lhs == rhs
    True

Note that we have to be careful to use the right value of `\rho`. The
reason for this is explained in :ref:`SLvsGL`.

We have seen that elements of the ``WeylCharacterRing`` can be coerced
into the ``WeightRing``. Elements of the ``WeightRing`` can be coerced
into the ``WeylCharacterRing`` *provided* they are invariant under the
Weyl group.
