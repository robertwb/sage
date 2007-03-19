"""
TESTS:

    sage: R = Zp(5, prec=5, type='fixed-mod')
    sage: a = random_matrix(R,5)
    sage: a.determinant()                # random output
    5 + 3*5^2 + 5^3 + 4*5^4 + O(5^5)

Computation of logs:

    sage: Qp(5)(1).log()
    O(5^20)
    sage: Qp(5)(-1).log()
    O(5^20)
    sage: Qp(5,prec=5)(7).log()
    4*5^2 + 4*5^3 + 3*5^4 + O(5^5)
    sage: Qp(5,prec=10)(25*8).log()
    5 + 3*5^3 + 3*5^4 + 2*5^5 + 5^6 + 2*5^7 + 3*5^8 + 3*5^9 + O(5^10)
    sage: Zp(5,prec=10)(8).log()
    5 + 3*5^3 + 3*5^4 + 2*5^5 + 5^6 + 2*5^7 + 3*5^8 + 3*5^9 + O(5^10)

Loading and saving elements of various types:

    sage: a = ZpCA(5)(-3); loads(dumps(a)) == a
    True
    sage: a = ZpCR(5)(-3); loads(dumps(a)) == a
    True
    sage: a = Zp(5)(-3); loads(dumps(a)) == a
    True
    sage: a = ZpFM(5)(-3); loads(dumps(a)) == a
    True
    sage: a = ZpL(5)(-3); loads(dumps(a)) == a
    True
"""
