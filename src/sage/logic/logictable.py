r"""
Module designed for the creation and printing of truth tables that are
associated with a logical statement.

A logic table is essentially a 2-D array that is created by the statement class
and stored in the private global variable table, along with a list containing
the variable names to be used, in order.

The order in which the table is listed essentially amounts to counting in binary.
For instance, with the variables A, B, and C the truth table looks like:

A      B      C      value
False  False  False    ?
False  False  True     ?
False  True   False    ?
False  True   True     ?
True   False  False    ?
True   False  True     ?
True   True   False    ?
True   True   True     ?

This is equivalent to counting in binary, where a table would appear thus;

2^2 2^1 2^0 value
0   0   0     0
0   0   1     1
0   1   0     2
0   1   1     3
1   0   0     4
1   0   1     5
1   1   0     6
1   1   1     7

Given that a table can be created corresponding to any range of acceptable
values for a given statement, it is easy to find the value of a statement
for arbitrary values of its variables.

EXAMPLES:
    sage: import sage.logic.propcalc as propcalc
    sage: s = propcalc.formula("a&b|~(c|a)")
    sage: s.truthtable()
    a      b      c      value
    False  False  False  True
    False  False  True   False
    False  True   False  True
    False  True   True   False
    True   False  False  False
    True   False  True   False
    True   True   False  True
    True   True   True   True

    sage: latex(s.truthtable(5,11))
    \\\begin{tabular}{llll}c & b & a & value \\\hline True & False & True & False \\True & True & False & True \\True & True & True & True\end{tabular}

It is not an error to use nonsensical numeric inputs.
    sage: s = propcalc.formula("a&b|~(c|a)")
    sage: s.truthtable(5, 9)
    a      b      c      value
    True   False  True   False
    True   True   False  True
    True   True   True   True

    sage: s.truthtable(9, 5)
    a      b      c      value

If one argument is provided, truthtable defaults to the end.
    sage: s.truthtable(-1)
    a      b      c      value
    False  False  False  True
    False  False  True   False
    False  True   False  True
    False  True   True   False
    True   False  False  False
    True   False  True   False
    True   True   False  True
    True   True   True   True

If the second argument is negative, truthtable defaults to the end.
    sage: s.truthtable(4, -2)
    a      b      c      value
    True   False  False  False
    True   False  True   False
    True   True   False  True
    True   True   True   True

NOTES:
    For statements that contain a variable list that when printed is longer than
    the \latex page, the columns of the table will run off the screen.
"""
#*************************************************************************************
# Copyright (C) 2006 William Stein <wstein@gmail.com>
# Copyright (C) 2006 Chris Gorecki <chris.k.gorecki@gmail.com>
#
# Distributed under the terms of the GNU General Public License (GPL)
# http://www.gnu.org/licenses/
#*************************************************************************************

#Global variables
__table = []
__vars_order = []

class Truthtable:

    def __init__(self, t, vo):
        r"""
        This function initializes the data fields and is called when a
        new table is created.

        INPUT:
            self -- the calling object.
            t -- a 2-D array containing the table values
            vo -- a list of the variables in the expression in order,
                  with each variable occurring only once.

        OUTPUT:
            Effectively returns an instance of this class.

        EXAMPLES:
        This example illustrates the creation of a table.
            sage: import sage.logic.propcalc as propcalc
            sage: s = propcalc.formula("a&b|~(c|a)")
            sage: s.truthtable()
            a      b      c      value
            False  False  False  True
            False  False  True   False
            False  True   False  True
            False  True   True   False
            True   False  False  False
            True   False  True   False
            True   True   False  True
            True   True   True   True

        There should be no errors.
        """
        self.__table = t
        self.__vars_order = vo

    def _latex_(self):
        r"""
        Returns a string representation of the calling table object.

        INPUT:
            self -- the calling object.

        OUTPUT:
            Returns the \latex representation of this table.

        EXAMPLES:
            sage: import sage.logic.propcalc as propcalc
            sage: s = propcalc.formula("man->monkey&human")
            sage: latex(s.truthtable())
            \\\begin{tabular}{llll}human & monkey & man & value \\\hline False & False & False & True \\False & False & True & True \\False & True & False & True \\False & True & True & True \\True & False & False & False \\True & False & True & False \\True & True & False & False \\True & True & True & True\end{tabular}

        Strange parameters can lead to a table header with no body.
            sage: latex(s.truthtable(2, 1))
            \\\begin{tabular}{llll}human & monkey & man & value \\\hli\end{tabular}
        """
        vars_len = []
        rt = s = ""
        self.__vars_order.reverse()
        s = r'\\\begin{tabular}{'
        s += 'l' * (len(self.__vars_order) + 1) + '}'
        for var in self.__vars_order:
            s += var + ' & '
        rt += s + r'value \\' + r'\hline '
        for row in self.__table:
            s = ""
            for i in row:
                s += str(i) + ' & '
            rt += s[:-3] + r' \\'
        rt = rt[:-3] + r'\end{tabular}'
        self.__vars_order.reverse()
        return rt

    def __repr__(self):
        r"""
        This function returns a string representation of the calling table object.

        INPUT:
            self -- the calling object: not used.

        OUTPUT:
            Returns a string representation of this table.

        EXAMPLES:
            sage: import sage.logic.propcalc as propcalc
            sage: s = propcalc.formula("man->monkey&human")
            sage: s.truthtable()
            man    monkey  human  value
            False  False   False  True
            False  False   True   True
            False  True    False  True
            False  True    True   True
            True   False   False  False
            True   False   True   False
            True   True    False  False
            True   True    True   True

        Strange parameters can lead to the table header with no body.
            sage: s.truthtable(2, 1)
            man    monkey  human  value

        There should be no errors.
        """
        vars_len = []
        line = rt = s = ""
        for var in self.__vars_order:
            vars_len.append(len(var))
            s = var + ' '
            while(len(s) < len('False ')):
                s += ' '
            s += ' '
            line += s
        rt += line + 'value\n'
        for row in self.__table:
            line = s = ""
            i = 0
            for e in row:
                if e == True:
                    j = 2
                else:
                    j = 1
                s = str(e) + ' ' * j
                if(i < len(vars_len)):
                    while(len(s) <= vars_len[i]):
                        s += ' '
                s += ' '
                line += s
                i += 1
            rt += line + '\n'
        return rt

    def get_table_list(self):
        r"""
        This function returns a string representation of the calling table object.

        INPUT:
            self -- the calling object: not used.

        OUTPUT:
            Returns the list representation of this table.

        EXAMPLES:
            sage: import sage.logic.propcalc as propcalc
            sage: s = propcalc.formula("man->monkey&human")
            sage: s.truthtable().get_table_list()
             [['man', 'monkey', 'human'], [False, False, False, True], [False, False, True, True], [False, True, False, True], [False, True, True, True], [True, False, False, False], [True, False, True, False], [True, True, False, False], [True, True, True, True]]

        """
	t = self.__table[:]
	t.insert(0, self.__vars_order)
	return t
