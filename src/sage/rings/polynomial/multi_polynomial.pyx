def is_MPolynomial(x):
    return isinstance(x, MPolynomial)

cdef class MPolynomial(CommutativeRingElement):

    ####################
    # Some standard conversions
    ####################
    def __int__(self):
        if self.degree() == 0:
            return int(self.constant_coefficient())
        else:
            raise TypeError

    def __long__(self):
        if self.degree() == 0:
            return long(self.constant_coefficient())
        else:
            raise TypeError

    def __float__(self):
        if self.degree() == 0:
            return float(self.constant_coefficient())
        else:
            raise TypeError

    def _mpfr_(self, R):
        if self.degree() == 0:
            return R(self.constant_coefficient())
        else:
            raise TypeError

    def _complex_mpfr_field_(self, R):
        if self.degree() == 0:
            return R(self.constant_coefficient())
        else:
            raise TypeError

    def _complex_double_(self, R):
        if self.degree() == 0:
            return R(self.constant_coefficient())
        else:
            raise TypeError

    def _real_double_(self, R):
        if self.degree() == 0:
            return R(self.constant_coefficient())
        else:
            raise TypeError

    def _rational_(self):
        if self.degree() == 0:
            from sage.rings.rational import Rational
            return Rational(repr(self))
        else:
            raise TypeError

    def _integer_(self):
        if self.degree() == 0:
            from sage.rings.integer import Integer
            return Integer(repr(self))
        else:
            raise TypeError

    def _polynomial_(self, R):
        var = R.variable_name()
        if var in self._parent.variable_names():
            return R(self.polynomial(self._parent(var)))
        else:
            return R([self])

    def coefficients(self):
        """
        Return the nonzero coefficients of this polynomial in a list.
        The order the coefficients appear in depends on the ordering
        used on self's parent.

        EXAMPLES:
            sage: R.<x,y,z> = MPolynomialRing(QQ,3,order='degrevlex')
            sage: f=23*x^6*y^7 + x^3*y+6*x^7*z
            sage: f.coefficients()
            [23, 6, 1]
            sage: R.<x,y,z> = MPolynomialRing(QQ,3,order='lex')
            sage: f=23*x^6*y^7 + x^3*y+6*x^7*z
            sage: f.coefficients()
            [6, 23, 1]

        AUTHOR:
            -- didier deshommes
        """
        degs = self.exponents()
        d = self.dict()
        return  [ d[i] for i in degs ]

    def truncate(self, var, n):
        """
        Returns a new multivariate polynomial obtained from self by
        deleting all terms that involve the given variable to a power
        at least n.
        """
        cdef int ind
        R = self.parent()
        G = R.gens()
        Z = list(G)
        try:
            ind = Z.index(var)
        except ValueError:
            raise ValueError, "var must be one of the generators of the parent polynomial ring."
        d = self.dict()
        return R(dict([(k, c) for k, c in d.iteritems() if k[ind] < n]))

    def polynomial(self, var):
        """
        Let var be one of the variables of the parent of self.  This
        returns self viewed as a unvariate polynomial in var over the
        polynomial ring generated by all the other variables of the parent.

        EXAMPLES:
            sage: R.<x,w,z> = QQ[]
            sage: f = x^3 + 3*w*x + w^5 + (17*w^3)*x + z^5
            sage: f.polynomial(x)
            x^3 + (17*w^3 + 3*w)*x + w^5 + z^5
            sage: parent(f.polynomial(x))
            Univariate Polynomial Ring in x over Polynomial Ring in w, z over Rational Field

            sage: f.polynomial(w)
            w^5 + 17*x*w^3 + 3*x*w + z^5 + x^3
            sage: f.polynomial(z)
            z^5 + w^5 + 17*x*w^3 + x^3 + 3*x*w
            sage: R.<x,w,z,k> = ZZ[]
            sage: f = x^3 + 3*w*x + w^5 + (17*w^3)*x + z^5 +x*w*z*k + 5
            sage: f.polynomial(x)
            x^3 + (17*w^3 + w*z*k + 3*w)*x + w^5 + z^5 + 5
            sage: f.polynomial(w)
            w^5 + 17*x*w^3 + (x*z*k + 3*x)*w + z^5 + x^3 + 5
            sage: f.polynomial(z)
            z^5 + x*w*k*z + w^5 + 17*x*w^3 + x^3 + 3*x*w + 5
            sage: f.polynomial(k)
            x*w*z*k + w^5 + z^5 + 17*x*w^3 + x^3 + 3*x*w + 5
        """
        cdef int ind
        R = self.parent()
        G = R.gens()
        Z = list(G)
        try:
            ind = Z.index(var)
        except ValueError:
            raise ValueError, "var must be one of the generators of the parent polynomial ring."

        if R.ngens() <= 1:
            return self.univariate_polynomial()

        other_vars = Z
        del other_vars[ind]

        # Make polynomial ring over all variables except var.
        S = R.base_ring()[tuple(other_vars)]
        ring = S[var]
        if not self:
            return ring(0)

        d = self.degree(var)
        B = ring.base_ring()
        w = dict([(remove_from_tuple(e, ind), val) for e, val in self.dict().iteritems() if not e[ind]])
        v = [B(w)]  # coefficients that don't involve var
        z = var
        for i in range(1,d+1):
            c = self.coefficient(z).dict()
            w = dict([(remove_from_tuple(e, ind), val) for e, val in c.iteritems()])
            v.append(B(w))
            z *= var
        return ring(v)

    def _mpoly_dict_recursive(self, vars=None, base_ring=None):
        """
        Return a dict of coefficent entries suitable for construction of a MPolynomial_polydict
        with the given variables.

        EXAMPLES:
            sage: R = Integers(10)['x,y,z']['t,s']
            sage: t,s = R.gens()
            sage: x,y,z = R.base_ring().gens()
            sage: (x+y+2*z*s+3*t)._mpoly_dict_recursive(['z','t','s'])
            {(1, 0, 1): 2, (0, 1, 0): 3, (0, 0, 0): x + y}

        TESTS:
            sage: R = Qp(7)['x,y,z,t,p']; S = ZZ['x,z,t']['p']
            sage: R(S.0)
            p
            sage: R = QQ['x,y,z,t,p']; S = ZZ['x']['y,z,t']['p']
            sage: z = S.base_ring().gen(1)
            sage: R(z)
            z
            sage: R = QQ['x,y,z,t,p']; S = ZZ['x']['y,z,t']['p']
            sage: z = S.base_ring().gen(1); p = S.0; x = S.base_ring().base_ring().gen()
            sage: R(z+p)
            z + p
            sage: R = Qp(7)['x,y,z,p']; S = ZZ['x']['y,z,t']['p'] # shouldn't work, but should throw a better error
            sage: R(S.0)
            Traceback (most recent call last):
            ...
            TypeError: len() of unsized object
        """
        from polydict import ETuple
        if not self:
            return {}

        if vars is None:
            vars = self.parent().variable_names_recursive()
        vars = list(vars)
        my_vars = self.parent().variable_names()
        if vars == list(my_vars):
            return self.dict()
        elif not my_vars[-1] in vars:
            x = base_ring(self) if base_ring else self
#            print "vars", vars, type(vars)
            const_ix = ETuple((0,)*len(vars))
            return { const_ix: x }
        elif not set(my_vars).issubset(set(vars)):
            # we need to split it up
            return self.polynomial(self.parent().gen(len(my_vars)-1))._mpoly_dict_recursive(vars, base_ring)
        else:
            D = {}
            prev_vars = vars[:vars.index(my_vars[0])]
            var_range = range(len(my_vars))
            if len(prev_vars) > 0:
                mapping = [vars.index(v) - len(prev_vars) for v in my_vars]
                tmp = [0] * (len(vars) - len(prev_vars))
                try:
                    for ix,a in self.dict().iteritems():
                        for k in var_range:
                            tmp[mapping[k]] = ix[k]
                        postfix = ETuple(tmp)
                        mpoly = a._mpoly_dict_recursive(prev_vars, base_ring)
                        for prefix,b in mpoly.iteritems():
                            D[prefix+postfix] = b
                    return D

                except AttributeError:
                    pass

            if base_ring is self.base_ring():
                base_ring = None

            mapping = [vars.index(v) for v in my_vars]
            tmp = [0] * len(vars)
            for ix,a in self.dict().iteritems():
                for k in var_range:
                    tmp[mapping[k]] = ix[k]
                if base_ring is not None:
                    a = base_ring(a)
                D[ETuple(tmp)] = a
            return D




cdef remove_from_tuple(e, int ind):
    w = list(e)
    del w[ind]
    return tuple(w)
